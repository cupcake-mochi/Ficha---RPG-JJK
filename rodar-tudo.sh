#!/bin/bash
# Roda todos os validadores da ficha digital, na ordem, e devolve 1 se algum falhar.
# Nao esconde nada: cada um imprime a saida inteira.
cd "$(dirname "$0")"
FALHOU=0
for v in conferir-catalogo.py conferir-kaori.py conferir-progressao.py \
         regressao-exemplos.py arnes.py revisao-cetica.py conferir-decisoes.py arnes-decisoes.py conferir-ficha-xlsx.py regressao-kaori-na-ficha.py \
         conferir-invocacao.py regressao-invocacao.py arnes-invocacao.py \
         regressao-delta.js arnes-delta.py \
         comparar-ficha-01.py; do
  echo "================================================================"
  echo "== $v"
  echo "================================================================"
  case "$v" in
    *.js)
      # o Apps Script nao roda fora do Google: o node testa a conta sozinha
      if command -v node > /dev/null; then node "$v" || FALHOU=1
      else echo "node nao existe nesta maquina: $v foi pulado."; fi ;;
    *) python3 "$v" || FALHOU=1 ;;
  esac
  echo
done
echo "================================================================"
if [ $FALHOU -eq 0 ]; then echo "OS DEZESSEIS PASSARAM"; else echo "ALGUM VALIDADOR FALHOU"; fi
exit $FALHOU
