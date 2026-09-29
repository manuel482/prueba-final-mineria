"""Prepara los archivos binarios de la entrega sin sobrescribir código ni guías."""
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA256 = 'd0895f9f1af4e76851e9edec5d1def33572105bbd2218b1d381521dd96a621e2'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def restore_missing():
    assets = json.loads((ROOT / 'docs/ARCHIVOS_BINARIOS.json').read_text(encoding='utf-8'))
    missing = {name: spec for name, spec in assets.items() if not (ROOT / name).is_file()}
    if not missing:
        print('Archivos binarios disponibles; se conservan los resultados existentes.')
        return
    parts = [ROOT / 'entrega' / f'ProyectoKDD_Entrega.zip.part{i:02}' for i in range(1, 24)]
    absent = [p.name for p in parts if not p.is_file()]
    if absent:
        raise FileNotFoundError('Descarga y extrae el repositorio completo con Code > Download ZIP. Faltan: ' + ', '.join(absent))
    with tempfile.TemporaryDirectory(prefix='kdd-fuentes-') as temporary:
        archive = Path(temporary) / 'fuentes.zip'
        with archive.open('wb') as output:
            for part in parts:
                with part.open('rb') as source:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
        if digest(archive) != ARCHIVE_SHA256:
            raise ValueError('Las partes no coinciden con el paquete de fuentes verificado. Descarga una copia completa.')
        with zipfile.ZipFile(archive) as bundle:
            for name, spec in missing.items():
                target = (ROOT / name).resolve()
                if not target.is_relative_to(ROOT.resolve()):
                    raise ValueError('Ruta fuera del proyecto: ' + name)
                pending = Path(temporary) / 'asset.tmp'
                with bundle.open(spec['member']) as source, pending.open('wb') as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                if digest(pending) != spec['sha256']:
                    raise ValueError('El archivo no coincide con la última entrega: ' + name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(pending, target)
                print('Preparado y verificado:', name)
    print('Preparación completada. Los scripts y las guías actuales permanecen intactos.')


if __name__ == '__main__':
    restore_missing()
