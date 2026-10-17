#!/bin/bash
# Roda todos os validadores da ficha digital, na ordem, e devolve 1 se algum falhar.
# Nao esconde nada: cada um imprime a saida inteira.
cd "$(dirname "$0")"
if [ "${1:-}" = "--b47-focal" ]; then
  shift
  exec .venv/bin/python capacidade-b47/validar.py "$@"
fi
if [ "${1:-}" = "--b47-infra" ]; then
  shift
  exec .venv/bin/python infra-b47/executar.py "$@"
fi
FALHOU=0
for v in conferir-catalogo.py conferir-kaori.py conferir-progressao.py \
         regressao-exemplos.py arnes.py revisao-cetica.py conferir-decisoes.py arnes-decisoes.py conferir-ficha-xlsx.py regressao-kaori-na-ficha.py \
         regressao-delta.js arnes-delta.py \
         regressao-ficha-pessoal.py regressao-pessoal.js regressao-construir.js arnes-pessoal.py \
         regressao-amaldicoada.py regressao-invocacoes.py \
         comparar-ficha-01.py regressao-configuracao.py regressao-campanha.py regressao-custom.py regressao-progressao.py regressao-familias-invocacao.py conferir-copias.py; do
  echo "================================================================"
  echo "== $v"
  echo "================================================================"
  case "$v" in
    *.js)
      # o Apps Script nao roda fora do Google: o node testa a conta sozinha
      if command -v node > /dev/null; then node "$v" || FALHOU=1
      else echo "node nao existe nesta maquina: $v NAO RODOU."; FALHOU=1; fi ;;
    *) python3 "$v" || FALHOU=1 ;;
  esac
  echo
done
# Peças/textos requerem pacote atual: nunca validar um modelo de outra versão.
if python3 nuvem-b47/exportar-baseline.py; then
  python3 regressao-pecas.py --modelo nuvem-b47/saidas/pecas-modelo.json --anterior nuvem-b47/saidas/pecas-modelo-anterior.json || FALHOU=1
  node regressao-textos-custom.js nuvem-b47/saidas/pecas-modelo.json || FALHOU=1
  node conteudos-b47/comum/testar-carregamento.js nuvem-b47/saidas/pecas-modelo.json || FALHOU=1
else
  FALHOU=1
fi
# B47 (17/10/2026): testes novos que rodam sem dados privados nem Google. Os que pedem leituras/snapshots nativos
# (--base, --leituras, --metadata) e os de expectativa histórica ficam fora; ver acabamento-b47/BATERIA-D.json.
for v in regressao-paleta.js regressao-arte.js conteudos-b47/comum/testar-notas-contextuais.js \
         conteudos-b47/comum/testar-entidades-integradas.py conteudos-b47/comum/testar-limites-emissor.py \
         conteudos-b47/comum/testar-normalizacao-nativa-cd.py capacidade-b47/testar-coalescencia.py \
         capacidade-b47/testar-equivalencia-lotes.py capacidade-b47/testar-formulas-nativas.py \
         capacidade-b47/testar-snapshot.py acabamento-b47/testar-auditoria-estudos.py; do
  echo "================================================================"
  echo "== $v"
  echo "================================================================"
  case "$v" in
    *.js) node "$v" || FALHOU=1 ;;
    *) python3 "$v" || FALHOU=1 ;;
  esac
  echo
done
echo "================================================================"
if [ $FALHOU -eq 0 ]; then echo "TODOS OS VALIDADORES EXECUTADOS PASSARAM"; else echo "ALGUM VALIDADOR FALHOU"; fi
exit $FALHOU
