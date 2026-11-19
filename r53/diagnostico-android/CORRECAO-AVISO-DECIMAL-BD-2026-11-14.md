# Buff/Debuff decimal fica âmbar nas INVOCAÇÕES · 14/11/2026

Ponta que o `CORRECAO-BUFF-DECIMAL-2026-11-10.md` deixou como "só visual": a caixa B/D das invocações tem o formato
`"B/D "+0`, então um 1,5 aparecia como "B/D +2" e a conta usava 1 (arredonda contra o dono). O Mizuki aprovou o
conserto em 14/11 ("Pode seguir").

## O que mudou

- **Regra de cor:** a letra da caixa fica âmbar (`#D89B3A`, a mesma dos avisos) quando o número tem decimal. A
  fórmula é `=N(O21)<>INT(N(O21))`, sem separador de argumento, então não depende da região.
  - Vale para as 168 caixas B/D das 12 fichas (atributos, ataque/CD/defesa/vida/deslocamento e os quatro TR), em
    36 faixas.
  - A referência é relativa à primeira caixa, então cada célula das 36 faixas se lê a si mesma.
- **Nota da primeira caixa (O21):** ganhou "Decimal arredonda contra você (1,5 vale 1; −1,5 vale −2) e deixa o
  número âmbar."
- **A conta não mudou.** Texto decimal ("1.5") aparece como foi digitado, e por isso não ganha a cor.

Arquivos:
- `ficha-v01/ficha_invocacoes.py`: a fonte, com a regra montada das mesmas células do gerador;
- `apps-script/Invocacoes.gs`: a regra na lista `condicional` da aba;
- `apps-script/R53CartoesEntidade1.gs`: a nota.

## QAs

Nas duas, pela API: a regra (índice 3, depois das três que já existiam) e a nota de O21.

Ensaio no Ciclo, visto no Chrome:

| caixa | valor | cor |
|---|---|---|
| O21 | 1,5 | âmbar ("B/D +2") |
| P21 | 2 | branca |
| Q21 | −1,5 | âmbar ("B/D -2") |
| O26 (outra faixa) | 1,5 | âmbar |
| Q31 | 3 | branca |
| R31 (outra faixa) | 2,5 | âmbar |

Valores repostos e relidos (todos "B/D 0"; AJ224 vazio). As outras fichas estavam recolhidas e não foram vistas;
a seção abaixo conta o que isso escondeu.

## Conserto no mesmo dia: as faixas das fichas 2 a 6

A fonte (`ficha_invocacoes.py`) monta as faixas com a geometria real do gerador e estava certa. Mas os endereços
escritos à mão no `Invocacoes.gs` e nas QAs saíram de um script avulso que chamou o `linha_da_fileira` fora do
gerador. Ele deu fichas a cada 198 linhas (21, 219, 417…), e o certo é a cada 231 (21, 252, 483…), como os
`redutores`. Nas fichas 2 a 6 de cada coluna, a regra caía em outras células. Texto não pinta, então nada ficou
errado na tela, mas o aviso não aparecia nessas fichas.

Corrigido a partir dos `redutores` do próprio `Invocacoes.gs`: linha da caixa ± + 8, + 13 e + 18, com colunas O:S
(AH:AL na segunda coluna). Conferido na QA da Era que AH1176, AH1181 e AH1186 são caixas B/D. A regra foi trocada
(`updateConditionalFormatRule`, índice 3) nas duas QAs.

## Oficiais

Nada aplicado. Na rodada das oficiais entram a regra e a nota, pela API, como nas QAs.
