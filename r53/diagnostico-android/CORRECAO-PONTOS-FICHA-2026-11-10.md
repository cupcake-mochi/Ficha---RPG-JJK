# Ponto fora de 0 a 6 na ficha do jogador · 10/11/2026

Continuação da PR94, que fez o mesmo nas entidades. O Mizuki aprovou o plano ("Pode seguir").

## O que estava errado

As caixas de pontos dos atributos (FICHA D21, L21, T21, AB21, AJ21) e as do Corpo (AK15, AM15, AO15, AQ15, AS15)
não têm menu. A ficha aceitava qualquer número sem aviso:

- negativo e fração entravam na conta e fechavam o orçamento;
- 7 passava, a não ser quando o teto da campanha já pegava;
- "1/2" virava a data 01/02 (o número 46054) e o resumo mostrava "46052 a mais", sem dizer o que estava errado.

## A regra agora

O resumo acusa e não reescreve a entrada. A ficha não arredonda nada. O aviso fica até o jogador corrigir.

| caixa | aviso | teto |
|---|---|---|
| pontos (Z15) | "Ponto fora de 0 a N" | N = teto de atributo da campanha (`DADOS_CONFIG!$S$5`, 6 por padrão) |
| Corpo (AK14) | "Pontos de Marco de Corpo Disponíveis - Ponto fora de 0 a 6" | 6 fixo |

Uma caixa acusa quando o valor é negativo, passa do teto ou não é inteiro. Texto que não é número (por exemplo
"abc") continua valendo 0, em silêncio, como nas entidades. O aviso vem antes dos outros, e o texto antigo
("N de M", "a mais", "Um atributo passou de", "Na criação, nenhum acima de") só aparece com as caixas em ordem.

## O que mudou no modelo

Antes a geração era `c8c2dae1ce50fa1b`, agora é `66aa9dde4fdec0b1`. Foram 280.056 posições em 26 abas, e só
**2 fórmulas** mudaram, as duas na FICHA: Z15 e AK14. `preparar_pontos_ficha.js` recusa qualquer outra diferença.

- Gerador: `ficha-v01/ficha_automatica.py` (função `fora`). A camada de campanha (`ficha-v01/campanha.py`) troca o
  "6" do aviso dos pontos pela caixa da CONFIGURAÇÃO, como já fazia com o "Um atributo passou de 6".
- `pontos_ficha_delta.json`: os 2 pares antes/depois.
- `preparar_pontos_ficha.reverterModelo` devolve Z15 e AK14 ao antes. É atômico: confere tudo antes de gravar.
  Nenhum comparador histórico do smoke precisou dessa camada.
- `r53/testes/pontos_ficha.js` está no smoke. Ele confere:
  - o plano e o modelo;
  - que a reversão parcial é recusada;
  - os pedidos em pt_BR e en_US;
  - que célula divergente é recusada;
  - a tabela da regra.
- Smoke completo: 152 OK, nenhuma falha.

## Instalação nas duas QAs (só as duas fórmulas, sem `construir()`)

Os pedidos saíram de `preparar_pontos_ficha.pedidos`, que confere se a célula atual é igual ao antes. Era e
Ciclo tinham o antes exato, e a aba FICHA tem o mesmo id (2091222604) nas duas. Cada QA recebeu 2 `updateCells`.

## Ensaio (entradas repostas depois)

| QA | entrada | Z15 / AK14 |
|---|---|---|
| Era | D21 −2 / 2,5 / "1/2" / 7 | Ponto fora de 0 a 6 |
| Era | D21 "abc" | 11 de 11 (silêncio) |
| Era | D21 3, L21 6 | 2 de 11 |
| Era | + AJ21 −1 | Ponto fora de 0 a 6 |
| Era | AQ15 −1 | …Disponíveis - Ponto fora de 0 a 6 |
| Era | AQ15 2 | …Disponíveis - 2 a mais (conta antiga) |
| Ciclo | T21 "1/2" | Ponto fora de 0 a 6 |
| Ciclo | AS15 2,5 | …Disponíveis - Ponto fora de 0 a 6 |
| Ciclo | T21 3 | 6 de 9 |

Ao final, todas as caixas de pontos e de Corpo estão em 0 nas duas. Z15 mostra "11 de 11" na Era e "9 de 9" no
Ciclo, e AK14 mostra "0 de 0".

**Achado do ensaio:** o "1/2" deixa a caixa com formato de data (`d/m`). Na reposição, o formato foi limpo, como
estava antes, quando a caixa não tinha formato de número.

## Fora deste trabalho

- **Bot (RPG---BOT):** não mudou. O texto do resumo chega como nota, e a ficha continua reprovada pela conferência
  do próprio bot.
- **`ler-analise.py`:** o leitor de teste da raiz está atrasado em relação ao formato atual. Fica para outra rodada.
- O Corpo fica com teto 6 fixo. Se a campanha ganhar teto próprio de Corpo, a fórmula muda junto.
- As oficiais e a ficha do jogador não foram tocadas. O pacote integral não foi reinstalado, e `construir()` e
  `continuar()` não rodaram.
