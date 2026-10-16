#!/usr/bin/env bash
# Bateria da revisão B47 (chat 2), em série. Uso: bash revisao-b47/rodar.sh [perfil]   (padrão base-v9)
# Não escreve no checkout fora de nuvem-b47/saidas/ nem no Google.
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
perfil=${1:-base-v9}
status=0
for t in test_contrato test_leitor test_enderecos test_carregador; do
  echo; echo "== $t --perfil $perfil"
  "$PY" "revisao-b47/$t.py" --perfil "$perfil" || status=1
done
echo; echo "== test_migracao"
"$PY" revisao-b47/test_migracao.py || status=1
exit $status
