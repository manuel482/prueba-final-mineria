"""Genera una entrega completa validada; no cambia el manifiesto del repositorio."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def selected():
    excluded = {'.git', '.venv', 'venv', '__pycache__', '.ipynb_checkpoints', '.pbi', 'entrega'}
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(p in excluded for p in relative.parts):
            continue
        if path.name in {'MANIFEST_SHA256.json', 'online_retail.zip', 'ejecutar_programado.cmd', '.DS_Store', 'Thumbs.db'}:
            continue
        if path.suffix in {'.pyc', '.tmp', '.zip'} or path.name.startswith('.proyecto_kdd.sqlite'):
            continue
        if path.name.endswith(('-journal', '-wal', '-shm')):
            continue
        yield path


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=ROOT.parent / 'ProyectoKDD_Entrega.zip')
    args = parser.parse_args()
    output = args.salida.resolve()
    if output.is_relative_to(ROOT):
        parser.error('Guarda el ZIP fuera de la carpeta del proyecto.')
    subprocess.run([sys.executable, str(ROOT / 'src/verificar_entrega.py')], check=True)
    files = list(selected())
    manifest = {p.relative_to(ROOT).as_posix(): sha256(p) for p in files}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + '.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path in files:
                archive.write(path, arcname='ProyectoKDD/' + path.relative_to(ROOT).as_posix())
            archive.writestr('ProyectoKDD/MANIFEST_SHA256.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        with zipfile.ZipFile(temporary) as archive:
            invalid = archive.testzip()
            if invalid:
                raise ValueError(f'Archivo ZIP corrupto: {invalid}')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'{output}: {len(files) + 1} archivos, {output.stat().st_size} bytes, SHA-256 {sha256(output)}')


if __name__ == '__main__':
    main()
