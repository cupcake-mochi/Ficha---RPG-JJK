# Módulo achatado e DADOS_CUSTOM sem INDIRECT · 15/11/2026

Pedido do Mizuki depois do pente fino de desempenho (usuários de telefone). Nada disso muda conta, regra ou texto da
ficha: só o caminho até a mesma conta.

## 1. Módulo achatado (`preparar_modulo_achatado.js`)

**O problema.** Cada preparador da cadeia injeta no `r53Modulo_` um remendo de texto que roda em toda execução. A cada
edição o Apps Script descompacta o pacote (8,7 milhões de caracteres), confere o SHA-256 e aplica 51.663 caracteres de
`split`/`replace` antes do `new Function`.

**O corte.** O achatador é o último preparador. Ele aplica os remendos uma vez só e grava o código já remendado nas
partes `R53_CODIGO_*`. O `r53Modulo_` que sobra só descompacta, confere o tamanho e roda os `r53Ajustar*` de sempre.

**O que fica igual.** O `new Function` recebe o mesmo texto, caractere por caractere. O trecho confere isso
descompactando as partes novas antes de gravar.

**Recusas.** O achatador não roda sobre Codigo já achatado. Um preparador que remende o módulo depois disso roda sobre o
backup não achatado, e o achatador roda de novo no fim.

**Editor do Apps Script.** O editor exige Trusted Types e não tem `unsafe-eval`, então `new Function` e `eval` falham lá
mesmo com TrustedScript. O trecho compila por um `<script>` que leva o nonce da própria página. Onde `new Function`
funciona, ele usa o `new Function` mesmo.

**Medição.** Cópia descartável do Ciclo, 4 edições do Buff da Defesa (FICHA!L59), cronômetro no `r53Modulo_`:

| | antes (6 edições) | achatado (4 edições) |
|---|---|---|
| descompactar | 0,9–1,9 s | 1,1–1,9 s |
| SHA-256 | 0,08–0,23 s | — |
| remendos | 0,4–1,0 s | — |
| `new Function` | 0,22–0,65 s | 0,53–0,92 s |
| `r53Ajustar*` | 0,13–0,33 s | 0,11–0,19 s |
| **módulo** | **1,7–4,1 s** | **1,8–3,0 s** |
| corpo do onEdit (`R53_ONEDIT ms`) | 2,1–4,8 s | 2,3–3,7 s |

O ganho esperado era de 0,5 a 1,2 s por edição, e a faixa caiu nessa medida. O `new Function` variou para cima, mas é
o mesmo texto e a mesma conta: com quatro amostras, isso é ruído do Apps Script.

**Resultado na cópia.** O pacote recomprimido ficou com 3 partes em vez de 5, e o Codigo ficou 52 mil caracteres menor.
As 4 edições terminaram sem erro e o Buff gravou e voltou.

**Testes.** `r53/testes/modulo_achatado.js`: o texto entregue ao `new Function` é idêntico antes e depois, no node e
num editor simulado com Trusted Types. Tem 9 defeitos plantados:
- âncora sumida;
- parte cortada;
- hash trocado;
- segunda passada;
- partes fora de ordem;
- parte duplicada;
- tamanho na execução;
- `<script>` sem nonce;
- erro de sintaxe num remendo.

## 2. DADOS_CUSTOM sem INDIRECT (`preparar_custom_sem_indirect.js`)

**O problema.** As listas dos cartões custom e as conferências JY/JZ tinham 525 `INDIRECT(SWITCH(...))`. INDIRECT é
volátil: recalcula a cada edição, em qualquer aba.

**A troca.** Agora a faixa vem de `CHOOSE(IFERROR(MATCH(tipo;{chaves};0);9);faixa1;…;padrão)`, que só recalcula quando
o tipo ou a faixa mudam. A mudança está no gerador (`ficha-v01/custom.py`, `escolha_faixa`), no `Custom.gs` e no
`Origens.gs`. `SWITCH` com a faixa direta não serve: no Sheets ele não devolve faixa, e o menu fica vazio. Isso foi visto
na cópia descartável.

**Planilha já montada.** Um único `spreadsheets.batchUpdate` com os dois `findReplace` que o preparador imprime. Ele é
atômico e fica limitado à DADOS_CUSTOM. A resposta tem de dizer 225 fórmulas com 4725 ocorrências, e depois 225 com
525. Outro número quer dizer planilha fora do molde: desfazer pelo histórico de versões.

**Conferido em duas cópias.**
- Na cópia descartável e na cópia fria da oficial, o resultado das 225 fórmulas foi fotografado antes e depois.
  - Estados: seletor "Arma" com o cartão 2 preenchido, e seletor "Origem" com o cartão 3 preenchido.
  - Resultado: 0 linhas diferentes nos dois estados.
- Na cópia fria, a resposta foi a esperada: 225/4725 e 225/525.

**Testes.**
- `r53/testes/custom_sem_indirect.js`: ida e volta do conversor e os pedidos emulados. Tem 5 defeitos plantados.
- `r53/testes/test_custom_sem_indirect.py`: a forma do gerador contra os `.gs`, as 525 trocas e as chaves na ordem do
  gerador. Tem 4 defeitos plantados.

## Fora desta rodada

- Nada nas oficiais.
- Nenhum `construir()`.
- A instalação nas oficiais é com o Mizuki no PC, nesta ordem:
  1. backup do projeto;
  2. preparadores pendentes;
  3. achatador;
  4. Ctrl+S;
  5. os dois `findReplace` da DADOS_CUSTOM.
