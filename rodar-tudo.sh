#!/bin/bash
# Roda todos os validadores da ficha digital, na ordem, e devolve 1 se algum falhar.
# Nao esconde nada: cada um imprime a saida inteira.
cd "$(dirname "$0")"
FALHOU=0
for v in conferir-catalogo.py conferir-kaori.py conferir-progressao.py \
         regressao-exemplos.py arnes.py revisao-cetica.py conferir-decisoes.py arnes-decisoes.py; do
  echo "================================================================"
  echo "== $v"
  echo "================================================================"
  python3 "$v" || FALHOU=1
  echo
done
echo "================================================================"
if [ $FALHOU -eq 0 ]; then echo "OS OITO PASSARAM"; else echo "ALGUM VALIDADOR FALHOU"; fi
exit $FALHOU
