#!/usr/bin/env python3
"""Gera o pacote 3c da versão em execução, sem importar Excel ou acessar Google."""
import argparse
import gzip
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--destino', type=Path, default=ROOT/'nuvem-b47/saidas')
args = parser.parse_args()
dest = args.destino.resolve()
dest.mkdir(parents=True, exist_ok=True)
model = dest/'pecas-modelo.json'
# Não reutilizar modelo antigo como resultado da execução atual.
subprocess.run([sys.executable, str(ROOT/'ficha-v01/monta.py'), '--exportar-pecas', str(model)], cwd=ROOT, check=True)
(dest/'pecas-modelo-anterior.json').write_bytes(gzip.decompress((ROOT/'nuvem-b47/fixtures/pecas-modelo-anterior.json.gz').read_bytes()))
print('Modelo atual:', model)
print('Referência histórica:', dest/'pecas-modelo-anterior.json')
