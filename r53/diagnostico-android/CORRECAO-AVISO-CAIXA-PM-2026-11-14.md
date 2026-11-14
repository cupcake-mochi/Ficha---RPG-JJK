# Caixa ± pendente fica âmbar · 14/11/2026

Ponta que o `PONTAS-DO-MAPA-2026-11-14.md` deixou aberta: numa rajada de edições, o Google às vezes descarta um
evento, e o número fica parado na caixa ± sem ser aplicado. Varrer as caixas pendentes não é seguro (um evento
atrasado seria aplicado em dobro), então o conserto é só visual. O Mizuki pediu em 14/11 ("Sim, faz o aviso").

## O que mudou

- **Regra de cor:** enquanto a caixa ± tem número, ela fica com fundo âmbar (`#D89B3A`) e letra branca. Quando o
  `onEdit` aplica e limpa, a cor some sozinha. A fórmula é `=AM30<>""`, sem separador de argumento.
  - FICHA: uma regra para cada caixa (AM26 vida, AM30 energia, AM34 integridade), montada no `corDeEstado_` do
    `Codigo.gs`, junto das outras regras dos recursos.
  - INVOCAÇÕES: uma regra para as 12 caixas (X13, X244, X475, X706, X937, X1168 e as mesmas linhas em AQ), com a
    referência relativa a X13.
- **Nota:** a das três caixas da FICHA (no título acima, AM25/AM29/AM33) e a de X12 das invocações ganharam:
  "Enquanto o número está aqui, a caixa fica âmbar: ainda não foi aplicado. Se continuar depois de um minuto, ele se
  perdeu (o Google às vezes descarta edições rápidas em sequência): confira o atual e digite de novo."
- **A conta não mudou.** O `r53DeltaExecutar_` continua igual.

Arquivos:
- `apps-script/Codigo.gs`: as notas `vida_delta`, `energia_delta`, `integridade_delta` e a regra no `corDeEstado_`;
- `ficha-v01/ficha_invocacoes.py`: a fonte da nota e da regra das invocações;
- `apps-script/Invocacoes.gs`: a regra na lista `condicional`;
- `apps-script/R53CartoesEntidade1.gs`: a nota de X12.

O mesmo ramo leva o conserto das faixas do B/D decimal (ver `CORRECAO-AVISO-DECIMAL-BD-2026-11-14.md`).

## QAs

Nas duas, pela API: as três regras da FICHA (índice 0), as notas de AM25/AM29/AM33, a regra das invocações (índice 4,
depois da do B/D decimal) e a nota de X12. Escrita pela API não dispara o `onEdit`, então a regra persiste até a
próxima montagem, que a recria pelo `Codigo.gs`.

Ensaio no Ciclo, visto no Chrome:

| caixa | como | resultado |
|---|---|---|
| FICHA!AM30 | −1 escrito pela API | âmbar |
| FICHA!AM34 | vazia | sem cor |
| INVOCAÇÕES!X13 | −2 escrito pela API | âmbar |
| FICHA!AM30 | −1 digitado na tela | âmbar logo depois do Enter; em ~20 s energia 10 → 9 e a caixa limpa, sem cor |

Valores repostos e relidos: AM30 e X13 vazias, energia atual `D30` = 10.

## Oficiais

Nada aplicado. Na rodada das oficiais entram as regras e as notas, pela API, como nas QAs.
