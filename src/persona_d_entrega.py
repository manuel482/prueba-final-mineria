"""Automatiza las tareas reproducibles de Persona D (Manuel): pipeline, notebook y evidencias."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCIAS = ROOT / "evidencias"
DB = ROOT / "data" / "proyecto_kdd.sqlite"
NOTEBOOK = ROOT / "notebooks" / "Proyecto_KDD.ipynb"


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_table(frame: pd.DataFrame, title: str, output: Path, max_rows: int = 18) -> None:
    shown = frame.head(max_rows).copy()
    shown.columns = [str(c) for c in shown.columns]
    fig_height = max(3.2, min(12.0, 1.2 + 0.38 * (len(shown) + 1)))
    fig_width = max(9.0, min(18.0, 1.2 + 1.35 * max(1, len(shown.columns))))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")
    ax.set_title(title, pad=12)
    table = ax.table(
        cellText=shown.astype(str).values,
        colLabels=shown.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.2)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def capture_original_dataset() -> Path:
    source = ROOT / "data" / "Online Retail.xlsx"
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_excel(source, nrows=16)
    public_view = frame.drop(columns=["CustomerID"], errors="ignore")
    output = EVIDENCIAS / "persona_d_dataset_original.png"
    render_table(public_view, "Dataset original · Online Retail (muestra)", output)
    return output


def capture_sql_validation() -> tuple[Path, Path]:
    if not DB.is_file():
        raise FileNotFoundError(DB)

    queries = [
        ("Conteos principales", """
            SELECT
              (SELECT COUNT(*) FROM bronze_retail) AS bronze_retail,
              (SELECT COUNT(*) FROM silver_retail) AS silver_retail,
              (SELECT COUNT(*) FROM silver_retail_rechazos) AS rechazadas,
              (SELECT COUNT(*) FROM gold_retail) AS gold_retail
        """),
        ("KPI Retail", """
            SELECT
              ROUND(SUM(importe), 3) AS venta_neta_gbp,
              ROUND(SUM(venta_bruta), 3) AS venta_bruta_gbp,
              ROUND(SUM(devolucion), 3) AS devoluciones_gbp
            FROM gold_retail
        """),
        ("Segmentos", """
            SELECT cluster, COUNT(*) AS clientes,
                   ROUND(AVG(recencia), 2) AS recencia_media,
                   ROUND(AVG(monetario), 2) AS monetario_medio
            FROM gold_segmentos
            GROUP BY cluster
            ORDER BY cluster
        """),
    ]

    text_sections = []
    image_frames = []
    uri = DB.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        for title, query in queries:
            frame = pd.read_sql_query(query, conn)
            text_sections.append(f"## {title}\n{frame.to_string(index=False)}")
            display = frame.copy()
            display.insert(0, "consulta", title)
            image_frames.append(display)

    text_output = EVIDENCIAS / "persona_d_consultas_sql.txt"
    text_output.write_text("\n\n".join(text_sections) + "\n", encoding="utf-8")

    combined = pd.concat(image_frames, ignore_index=True, sort=False).fillna("")
    image_output = EVIDENCIAS / "persona_d_consultas_sql.png"
    render_table(combined, "Consultas SQL de validación", image_output, max_rows=30)
    return image_output, text_output


def execute_notebook() -> None:
    run(
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        str(NOTEBOOK.relative_to(ROOT)),
        "--ExecutePreprocessor.timeout=-1",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Tareas reproducibles de Persona D (Manuel)")
    parser.add_argument("--sin-pipeline", action="store_true", help="Reutiliza una base ya generada y verificada")
    parser.add_argument("--sin-notebook", action="store_true", help="Omite la ejecución de Jupyter")
    args = parser.parse_args()

    EVIDENCIAS.mkdir(parents=True, exist_ok=True)

    if not args.sin_pipeline:
        run(sys.executable, "src/pipeline.py", "--stage", "all")
    run(sys.executable, "src/verificar_entrega.py", "--json", "evidencias/comprobacion_local.json")

    if not DB.is_file():
        raise FileNotFoundError("No existe data/proyecto_kdd.sqlite después de la verificación.")

    dataset_capture = capture_original_dataset()
    sql_capture, sql_text = capture_sql_validation()

    if not args.sin_notebook:
        execute_notebook()

    summary = {
        "persona": "D",
        "responsable": "Manuel Mora",
        "matricula": "100065865",
        "integrantes": [
            {"nombre": "Manuel Mora", "matricula": "100065865"},
            {"nombre": "Stephany Ángeles", "matricula": "100063069"},
            {"nombre": "Erick Reynoso Torres", "matricula": "100068266"},
            {"nombre": "Enmanuel Jiménez", "matricula": "100066650"},
        ],
        "sqlite": {
            "ruta": str(DB.relative_to(ROOT)),
            "bytes": DB.stat().st_size,
            "sha256": sha256_file(DB),
            "compartir_por_drive": True,
        },
        "evidencias": [
            str(dataset_capture.relative_to(ROOT)),
            str(sql_capture.relative_to(ROOT)),
            str(sql_text.relative_to(ROOT)),
            str(NOTEBOOK.relative_to(ROOT)),
        ],
        "notebook_ejecutado": not args.sin_notebook,
    }
    output = EVIDENCIAS / "persona_d_resumen.json"
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nPersona D completada.")
    print(f"SQLite: {summary['sqlite']['bytes'] / (1024**2):.1f} MiB")
    print("SHA-256:", summary["sqlite"]["sha256"])
    print("Sube data/proyecto_kdd.sqlite a Drive y comparte el archivo con A, B y C.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
