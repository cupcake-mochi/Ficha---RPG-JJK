# Troca de paleta em lote único (24/10/2026)

Objetivo do Mizuki: uma lista de paletas só (CARTEIRA!C27) que troca as cores em qualquer cópia, sem ativar nada.
Isso exige o acionador simples `onEdit`, o único que vai junto numa cópia, com limite de 30 s.

## Resultado

Funciona na cópia de teste `1ESL-AageFm_eo9ybp1ITFAAKm1t6I2FKJyYp8-SFOYU` (projeto
`18AEaLKY0tG_B8zNZiaai2pm9S3-7tx-IWV7xkUJfSiN-XBrBH7LBkZZ9`): fundo e letra das 6 abas visíveis mudam em 13–21 s.
Bordas e arte ficam fixas no violeta acinzentado `#857F99`, escolhido pelo Mizuki entre `#8A7EC4`, `#857F99` e
`#808080` (contraste mínimo 2,70 contra fundo e painel nas 122 paletas).

Código: `lote_paleta.gs`, montado por `preparar_lote.js` (injeta PALETAS, ARTE e posições das imagens e desvia o
onEdit da C27), testado em `../testes/lote_paleta.js`.

## Medições (logs do Apps Script, fotos do Mizuki)

| Tentativa | O que fazia | Resultado |
|---|---|---|
| Tema da planilha (9 vagas) | `setConcreteColor` por vaga | ~4,8 s por vaga; 9 vagas + 7 s de partida não cabem em 30 s |
| Lote v1 | lia a grade de cada aba e gravava no fim | ~5 s por leitura, até na CARTEIRA (52×47); estourou lendo a 2ª aba |
| Lote v2 | lê só um mapa pronto, enfileira por papel, um flush | 13,1 s e 14,5 s (mapa 3 s, enfileirar 0,4 s, flush 10 s) |
| Lote + bordas pela régua | `RangeList.setBorder` por lado e estilo | só a CARTEIRA gastou 13 s; estourou. Descartado |
| Lote v2, mapa por aba | idem, com a FICHA PESSOAL no mapa | 21,6 s, dentro do limite |

O que aprendemos: nesta ficha toda leitura do SpreadsheetApp paga ~5 s, e `setBorder` não fica na fila como
`setBackground`/`setFontColor`. O custo é por chamada, não por célula.

## Passo a passo para aplicar numa base (uma vez, pelo editor)

1. `mapearLote()`: lê fundo e letra das 6 abas, detecta a paleta pintada aba por aba e grava o mapa de papéis na
   aba oculta `R53_LOTE` (vai junto na cópia).
2. `fixarBordasLote()`: pinta toda borda das 6 abas com `#857F99`, mantendo lado e estilo (usa o serviço avançado
   do Sheets; pede autorização na primeira vez).
3. `fixarArteLote()`: pinta as 10 imagens `PM-ARTE:` com `#857F99`; a foto do jogador não é tocada.

Se o layout de uma aba mudar, rode `mapearLote()` de novo.

## Pendências

- Aviso da paleta (CARTEIRA!C29): na cópia de teste já diz "A troca leva uns 20 segundos e muda a ficha inteira de uma
  vez. / Até as cores mudarem, não feche nem recarregue esta página." Na base, trocar também `TEXTO_AVISO_PALETA_`
  (Codigo.gs e módulo), senão a revisão de abertura volta o texto antigo.

- Ainda não aplicado na base nem na original. Antes: conferir que o `onOpen` não chama mais a paleta antiga
  (`paleta_pendente` / `r53PaletaLeve_().continuar`), que repintaria a arte e as bordas.
- Barras: o lote grava a cor em `DADOS!CZ51`, que as fórmulas de SPARKLINE leem.
- INVOCAÇÕES: o Mizuki pediu uma caixa explicando que as fichas 2–6 e 8–12 abrem pelo + da lateral (no Android, se
  a lateral estiver recolhida, o + vira um pontinho; tocar no « do canto). A caixa é nova: depois de criá-la, rodar
  `mapearLote()` de novo para ela entrar na troca de cores.
  Feita na cópia de teste em 24/10/2026: `INVOCAÇÕES!AB2:AR4` mesclada, fundo #FAD7E3 (papel "painel"; branco não entra no mapa e ficaria fixo nas paletas escuras), Roboto 9 na cor do texto do
  cabeçalho (#2F0414), texto "COMO ABRIR AS OUTRAS FICHAS · As invocações 2 a 6 e 8 a 12 ficam recolhidas. Toque no +
  da lateral esquerda, na altura de cada ficha, para abrir. No celular, se a lateral estiver estreita, o + aparece como
  um pontinho: toque no « do canto para abrir a lateral." Rodar `mapearLote()` de novo depois da troca do fundo; na base, repetir a caixa e o mapa.
- INVOCAÇÕES: os grupos de linha terminam antes do fim de cada bloco (ex.: grupo até 227, bloco até 238), então
  sobra o rodapé visível com o grupo fechado. Já vem da montagem; o Mizuki preferiu não mexer agora.
