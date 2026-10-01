"""Comprobación de lectura de la entrega. Solo usa la biblioteca estándar."""
import argparse
import hashlib
import json
import sqlite3
import sys
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="Comprueba fuentes, SQLite y evidencias")
    parser.add_argument("--archivos", action="store_true", help="Comprueba SHA-256 de la instantánea original")
    parser.add_argument("--solo-fuentes", action="store_true", help="Comprueba la descarga sin exigir CSV ni SQLite regenerados")
    parser.add_argument("--json", type=Path, help="Guarda un resumen JSON")
    args = parser.parse_args()
    checks = []

    def check(label, condition, detail=""):
        checks.append({"control": label, "resultado": "OK" if condition else "ERROR", "detalle": str(detail)})

    sources = ["Online Retail.xlsx", "productos_original.xlsx"]
    if not args.solo_fuentes:
        sources += ["retail_original.csv", "productos_original.csv"]
    for name in sources:
        p = ROOT / "data" / name
        check("fuente " + name, p.is_file() and p.stat().st_size > 0 if p.exists() else False)

    db = ROOT / "data/proyecto_kdd.sqlite"
    if not args.solo_fuentes:
        check("base SQLite", db.is_file() and db.stat().st_size > 0 if db.exists() else False,
              "Si falta, ejecuta src/pipeline.py --stage all")
    if not args.solo_fuentes and db.is_file():
        try:
            with sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True) as conn:
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
                check("integridad SQLite", integrity == "ok", integrity)
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                expected = [
                    "bronze_retail", "bronze_productos", "silver_retail",
                    "silver_retail_rechazos", "silver_productos", "silver_productos_rechazos",
                    "gold_retail", "gold_ventas_productos", "dim_productos",
                    "dim_retail_producto", "dim_pais", "dim_fecha",
                    "gold_predicciones", "gold_segmentos",
                ]
                missing = sorted(set(expected) - tables)
                check("tablas analíticas", not missing, ", ".join(missing))
                if not missing:
                    counts = {name: conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] for name in expected}
                    check("volumen Bronze", counts["bronze_retail"] > 100000 and counts["bronze_productos"] > 100000, counts)
                    check("conciliación Retail",
                          counts["bronze_retail"] == counts["silver_retail"] + counts["silver_retail_rechazos"])
                    check("conciliación Productos",
                          counts["bronze_productos"] == counts["silver_productos"] + counts["silver_productos_rechazos"])
                    check("hechos Gold", counts["gold_retail"] == counts["silver_retail"]
                          and counts["gold_ventas_productos"] == counts["silver_productos"])
                    for fact, key, dim in [
                        ("gold_ventas_productos", "producto_key", "dim_productos"),
                        ("gold_retail", "stock_key", "dim_retail_producto"),
                        ("gold_retail", "pais", "dim_pais"),
                    ]:
                        duplicates = conn.execute(
                            f'SELECT COUNT(*) FROM (SELECT "{key}" FROM "{dim}" GROUP BY "{key}" HAVING COUNT(*)>1)'
                        ).fetchone()[0]
                        orphans = conn.execute(
                            f'SELECT COUNT(*) FROM "{fact}" f LEFT JOIN "{dim}" d ON f."{key}"=d."{key}" '
                            f'WHERE d."{key}" IS NULL'
                        ).fetchone()[0]
                        check(f"relación {fact} → {dim}", duplicates == 0 and orphans == 0,
                              f"duplicados={duplicates}; huérfanos={orphans}")
                    kpis = json.loads((ROOT / "evidencias/kpis.json").read_text(encoding="utf-8"))
                    retail = conn.execute("SELECT SUM(importe), SUM(venta_bruta), SUM(devolucion) FROM gold_retail").fetchone()
                    productos = conn.execute("SELECT SUM(venta), SUM(costos), SUM(utilidad) FROM gold_ventas_productos").fetchone()
                    for group, keys, values in [
                        ("retail", ["venta_neta_gbp", "venta_bruta_gbp", "devoluciones_gbp"], retail),
                        ("productos", ["venta", "costos", "utilidad"], productos),
                    ]:
                        for key, actual in zip(keys, values):
                            check(f"KPI {group}.{key}", math.isclose(actual, kpis[group][key], rel_tol=1e-9, abs_tol=0.01))
        except (sqlite3.Error, OSError, ValueError, KeyError, TypeError) as exc:
            check("consulta SQLite", False, exc)

    evidence = ROOT / "evidencias"
    evidence_names = [] if args.solo_fuentes else ["metricas.json", "kpis.json", "verificacion.json", "estado_ejecucion.json"]
    for name in evidence_names:
        p = evidence / name
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            ok = data.get("estado") == "OK" if name == "estado_ejecucion.json" else bool(data)
            check("evidencia " + name, ok)
        except (OSError, ValueError) as exc:
            check("evidencia " + name, False, exc)

    p = evidence / "sha256_fuentes.json"
    try:
        source_hashes = json.loads(p.read_text(encoding="utf-8"))
        check("catálogo de fuentes", set(source_hashes) == {"Online Retail.xlsx", "productos_original.xlsx"})
        for name, expected_hash in source_hashes.items():
            source = ROOT / "data" / name
            actual = sha256_file(source) if source.is_file() else "archivo ausente"
            check("SHA-256 fuente " + name, actual == expected_hash, actual)
    except (OSError, ValueError) as exc:
        check("hashes de fuentes", False, exc)

    for relative in ["pentaho/proyecto_completo.kjb", "pentaho/bronze_retail.ktr", "pentaho/bronze_productos.ktr"]:
        try:
            ET.parse(ROOT / relative)
            check("XML " + relative, True)
        except (OSError, ET.ParseError) as exc:
            check("XML " + relative, False, exc)

    powerbi = ROOT / "powerbi"
    json_files = sorted(p for p in powerbi.rglob("*") if p.suffix in {".json", ".pbip", ".pbir", ".pbism", ".bim"})
    check("estructura Power BI", len(json_files) >= 32 and (powerbi / "ProyectoKDD.pbip").is_file(), len(json_files))
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
            check("JSON " + path.relative_to(ROOT).as_posix(), True)
        except (OSError, ValueError) as exc:
            check("JSON " + path.relative_to(ROOT).as_posix(), False, exc)

    if args.archivos:
        try:
            manifest = json.loads((ROOT / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
            for name, expected_hash in manifest.items():
                p = ROOT / name
                actual = sha256_file(p) if p.is_file() else "archivo ausente"
                check("instantánea " + name, actual == expected_hash, actual if actual != expected_hash else "")
        except (OSError, ValueError) as exc:
            check("manifiesto de entrega", False, exc)

    errors = sum(x["resultado"] != "OK" for x in checks)
    summary = {"resultado": "OK" if not errors else "ERROR", "controles": len(checks), "errores": errors,
               "alcance": "fuentes y estructura; validación de ejecución fuera de este modo" if args.solo_fuentes else "fuentes, base, KPI, evidencias y estructura",
               "detalle": checks,
               "validacion_nativa_requerida": ["ejecución real Pentaho", "PBIX y capturas Power BI Desktop"]}
    if args.json:
        path = args.json if args.json.is_absolute() else ROOT / args.json
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in checks:
        print(f"{row['resultado']:5} {row['control']}" + (f": {row['detalle']}" if row["resultado"] != "OK" else ""))
    print(f"RESULTADO: {summary['resultado']} ({len(checks)} controles, {errors} errores)")
    return 1 if errors else 0


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
