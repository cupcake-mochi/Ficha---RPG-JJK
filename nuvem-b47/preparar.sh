#!/usr/bin/env bash
# Prepara Python localmente; não acessa Google, não envia código nem usa sudo.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 0 ]]; then
  echo 'Uso: bash nuvem-b47/preparar.sh (PYTHON=python3.11 para escolher Python)' >&2
  exit 2
fi
"${PYTHON:-python3}" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else "Use Python 3.12 (dependências fixadas para 3.10–3.12).")'
"${PYTHON:-python3}" -m venv .venv
venv_python=.venv/bin/python
# CPython nativo no Windows cria Scripts/, inclusive sob o Git Bash.
if [[ ! -x "$venv_python" && -f .venv/Scripts/python.exe ]]; then
  venv_python=.venv/Scripts/python.exe
fi
"$venv_python" -m pip install --disable-pip-version-check -r requirements.txt
mkdir -p nuvem-b47/saidas
"$venv_python" nuvem-b47/conferir.py
