#!/bin/bash
# Roda todos os validadores da ficha digital, na ordem, e devolve 1 se algum falhar.
# Nao esconde nada: cada um imprime a saida inteira.
#
# ⚠ CODIGO 2 = PULADA, e nao falha. Ele e' para o validador que nao RODOU por
# falta de insumo — arquivo que e' entrada do Mizuki e nao mora no repositorio.
# Antes da v0.222 isso saia com 1 e o resumo dizia "ALGUM VALIDADOR FALHOU",
# que e' a mesma cor de um defeito de verdade. Cor igual para coisas diferentes
# e' como um vermelho vira paisagem, e aí o proximo desvio entra junto sem
# ninguem ver. Agora sao duas cores — e o que pulou continua gritando que NAO
# foi conferido, porque um verde que pulou checagem nao e' um verde.
cd "$(dirname "$0")"
FALHOU=0
PULADOS=()
TOTAL=0
for v in conferir-catalogo.py conferir-kaori.py conferir-progressao.py \
         regressao-exemplos.py arnes.py revisao-cetica.py conferir-decisoes.py arnes-decisoes.py conferir-ficha-xlsx.py regressao-kaori-na-ficha.py \
         conferir-invocacao.py regressao-invocacao.py arnes-invocacao.py \
         regressao-delta.js arnes-delta.py \
         comparar-ficha-01.py; do
  TOTAL=$((TOTAL+1))
  echo "================================================================"
  echo "== $v"
  echo "================================================================"
  case "$v" in
    *.js)
      # o Apps Script nao roda fora do Google: o node testa a conta sozinha
      if command -v node > /dev/null; then node "$v" || FALHOU=1
      else echo "node nao existe nesta maquina: $v foi pulado."; PULADOS+=("$v (sem node)"); fi ;;
    *)
      python3 "$v"; rc=$?
      if [ $rc -eq 2 ]; then PULADOS+=("$v"); elif [ $rc -ne 0 ]; then FALHOU=1; fi ;;
  esac
  echo
done
echo "================================================================"
if [ ${#PULADOS[@]} -gt 0 ]; then
  echo ">>> ${#PULADOS[@]} de $TOTAL PULARAM, e o que pulou NAO foi conferido:"
  for p in "${PULADOS[@]}"; do echo "    - $p"; done
  echo
fi
if [ $FALHOU -eq 0 ]; then
  if [ ${#PULADOS[@]} -eq 0 ]; then
    echo "OS DEZESSEIS PASSARAM"
  else
    echo "OS OUTROS $((TOTAL - ${#PULADOS[@]})) PASSARAM — mas veja a lista acima antes de subir."
  fi
else
  echo "ALGUM VALIDADOR FALHOU"
fi
exit $FALHOU
