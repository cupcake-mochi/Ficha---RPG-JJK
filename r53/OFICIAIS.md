# Fichas oficiais atuais · 25/10/2026

Estes são os **dois modelos oficiais**, confirmados expressamente pelo usuário em 25/10/2026:

| Modelo | Google Sheets | Apps Script vinculado |
|---|---|---|
| Ficha - Era da Revolução (CM) | [Abrir ficha](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit) | [Abrir projeto](https://script.google.com/u/0/home/projects/1B6coyZOopuZb5encJpkAGalDcHUp5X4nwXc5hf9OkpNyTTEZWcVGrdtl/edit) |
| Ficha - Ciclo Maldito (CM) | [Abrir ficha](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit) | [Abrir projeto](https://script.google.com/u/0/home/projects/1xSJkCsmx7ygqdjMXv0NsQhs9XSwo9A_Ow-oJzqQNP-0iibueRi1v9s-M/edit) |

A antiga `1u0zWQ…`, a C, a candidata A `1427…` e as cópias de ensaio são referências históricas. Não substituir estes dois endereços pelos links de publicações antigas. A ficha do amigo usada para diagnóstico não integra este par e não foi alterada.

## Estado instalado

**26/10/2026, pacote otimizado (com o aval do Mizuki):** as duas oficiais receberam o pacote leve
(módulo `fef2a94b…`, que é o módulo instalado `2f153f65…` com as correções embutidas, os remendos
1–32 de `pacote_leve_remendos.json` e a montagem cortada), o bloco do Caminho de
`apps-script/Caminho.gs`, o atalho das células livres (`r53/atalho_livre.gs`, mapa `ce92ede0…`) e o
`EditorR53.gs` `d2e57223…`. Antes de subir: o script das duas era idêntico (fora a formatação do
manifesto, mantido o de cada uma); o mesmo módulo saiu do instalado com 22 remendos (`9d1cec81…`, o da
cópia de teste) e com 32 (`fef2a94b…`); a Ciclo Maldito exportada gera o mesmo mapa do atalho que a
Era; e no arnês a oficial de antes e o pacote montado gravaram o mesmo em 35.729 edições em cada uma.
`Codigo.gs` instalado: `1d8eb5b3…`. A **versão 1** de cada projeto do Apps Script guarda o script
anterior (`d92f846e…` / `bc300464…`) para voltar. Ainda não medido no Google.


Atualização de automações em cópias: veja a
[entrega e limites de validação](diagnostico-android/AUTOMACOES-COPIAS-2026-10-25.md).
Caminho, Trilha, habilidades e grupos de treino foram corrigidos e ensaiados em
cópia nova. As duas oficiais receberam a área oculta R53_EVENTOS (653 referências)
e o incremento de código; quatro releituras após reabrir ficaram iguais.

- `Codigo.gs` atual: `d92f846e42aa1ad42237ced54da53772d6aa796ae580c90b84fa718a980c5827`.
- `EditorR53.gs` atual, transporte comprimido do mesmo catálogo:
  `bc3004641a1a28c148885638955e6db66ffebaa01cd8acea30415cbbcd30e993`.

São 30 abas físicas, mantendo ANALISE12/esquema2 e seus endereços. Novas cópias
levam a correção; cópias antigas não recebem o código automaticamente.
O pacote integral não foi reinstalado. Os hashes abaixo documentam a aplicação
anterior de 25/10, antes deste incremento de automações.

As duas oficiais têm as correções incrementais de Ritual, carga das dez invocações,
Classes, validação de funções bloqueadas e edição de missões. Snapshots nativos
novos precederam a aplicação; os quatro códigos finais foram reabertos e relidos
integralmente iguais ao proposto. Nenhum dado de personagem foi preenchido nas
oficiais para testar: os ensaios ocorreram em cópias nativas.

- `Codigo.gs`: SHA-256 `f664e70a66063fba8fe966506d3e9446ba68e2ed0e0a4b45cc09e49ce7a2d66f`.
- `EditorR53.gs`: SHA-256 `6cb49d97c49fe93591967b86c79c0435f74c1bf0b34c4a62d004ebb3ec887f81`.

Fontes e pacote conferidos, geração de dados `7f85d740f71c4cb6`. O pacote integral
novo **não** substituiu os projetos instalados. O módulo-base nativo continua na
geração `e142593fdc5be157`, acompanhado dos incrementos de abertura, cores,
salários e correções desta revisão. Não reconstruir nem reaplicar os deltas.

Cobertura, tempos observados e limites: [pente-fino final](diagnostico-android/PENTE-FINO-FINAL-2026-10-25.md).
Histórico: [Ritual](diagnostico-android/REVISAO-2026-10-25.md) e
[carga e revisão ampliada](diagnostico-android/REVISAO-NATIVA-2026-10-25.md).

Os rótulos públicos do cabeçalho e do número da carteira usam **1.0**, sem
acompanhar as revisões do livro. Os metadados técnicos continuam preservados.
Veja [versão pública](diagnostico-android/VERSAO-PUBLICA-2026-10-25.md).

## Limpeza dos projetos · 26/10/2026

Aval do Mizuki pelo cartão de decisão. Nas duas oficiais saíram 31 arquivos sem uso: 29 só com o comentário
"Conteúdo incluído no pacote R53" e os diagnósticos AuditarAndroid e ConfigurarCopiaAndroid, presos a IDs de
planilhas antigas. Configuracao e Origens ficam, porque guardam R53_CODIGO_3_ e R53_CODIGO_4_, que o carregador lê.
Antes de limpar, cada projeto ganhou a versão 2 de backup ("Antes da limpeza de arquivos vazios"). O resto ficou
idêntico, conferido pela API. Se o empacotar_script.py rodar de novo, ele recria os 29 comentários: inofensivo.

## Missões enxutas · 26/10/2026

Aval do Mizuki pelo cartão de decisão ("Instalar e estudar mais depois"). Nas duas oficiais, só o Codigo mudou:
`preparar_missoes_enxutas.js` (os dois cortes, ver PENDENCIAS) aplicado sobre o Codigo instalado. O resultado
saiu byte a byte igual ao da cópia medida (`1HI96ICu…`, 21 edições de missão concluídas em 16–28 s). Antes, cada
projeto ganhou a versão 3 de backup ("Antes das missões enxutas"). Os outros arquivos ficaram idênticos,
conferido pela API.

## Missões enxutas, terceiro corte · 26/10/2026

Com o ok do Mizuki, as duas oficiais receberam o terceiro corte (painel antes dos registros, valores antes das
notas). O preparador foi aplicado sobre o Codigo da versão 3 e o resultado saiu byte a byte igual ao da cópia medida
(13 edições concluídas, pior caso 18,9 s). Antes, cada projeto ganhou a versão 4 de backup ("Antes do terceiro corte
das missões"). Os outros arquivos ficaram idênticos, conferido pela API.

## Remendos 33–38 da CONFIGURAÇÃO · 26/10/2026

Aval do Mizuki no chat ("Pode instalar 33–38 nas duas oficiais… exigindo o módulo 52fc6903 igual à cópia sem
DIAG"). Pelo Chrome, na conta dona, só o pacote do módulo mudou: os cinco arquivos `R53_CODIGO_` e o hash no
Codigo (as duas ocorrências: a conferência do `r53Modulo_` e a do atalho). Remendos 33–38 do
`pacote_leve_remendos.json` aplicados sobre o `fef2a94b`; o instalador exigia `fef2a94b` antes e `52fc6903` depois,
e recusou sem gravar quando tentei só 34–38 (o 33, cartas antes das caixas, está por baixo dos outros). O módulo
`52fc6903` é exatamente o da cópia medida `1HI96ICu…` sem as linhas `DIAG` (conferido pelo SHA-256). Antes, cada
projeto ganhou a versão 5 de backup ("Antes dos remendos 34-38 da CONFIGURAÇÃO" na Ciclo Maldito, 14:32; "Antes
dos remendos 33-38 da CONFIGURAÇÃO" na Era da Revolução, 14:42), feita como as anteriores: implantação de
biblioteca, arquivada em seguida. Depois de salvar e recarregar, nas duas: módulo `52fc6903`, nenhum
`fef2a94b` no Codigo, e Codigo, EditorR53, LotePaleta, PaletaSegundoPlano e SalarioLote idênticos aos da cópia.
Medição na cópia: habilidade custom da CONFIGURAÇÃO em 18–21 s, todas concluídas (MEDICAO-DESEMPENHO).

## Cartão em menos idas · 26/10/2026

Aval do Mizuki no chat ("Pode instalar o corte do cartão nas duas oficiais (versão 6 de backup antes), exigindo o
EditorR53 68f21a08 igual ao da cópia"). Pelo Chrome, na conta dona, só o EditorR53 mudou: três trechos do
`preparar_cartao_leve.js` trocados no EditorR53 instalado, que precisava ser o `d2e57223` e saiu `68f21a08`, o
mesmo gerado no node e medido na cópia `1HI96ICu…`. Antes, cada projeto ganhou a versão 6 de backup ("Antes do
corte do cartão (26/10/2026)": Ciclo Maldito 15:06, Era da Revolução 15:10), implantação de biblioteca arquivada
em seguida. Depois de salvar e recarregar, nas duas: EditorR53 `68f21a08`, módulo `52fc6903`, e Codigo,
LotePaleta, PaletaSegundoPlano e SalarioLote como estavam. Medição na cópia: pontos do cartão em 19,5–23,4 s,
todas concluídas (antes 23,2–26,0 s).

## SalarioLote sem esperar o recálculo · 26/10/2026

Aval do Mizuki no chat ("Pode instalar o SalarioLote novo nas duas oficiais (versão 7 de backup antes), exigindo o
arquivo 366f6dd3 igual ao da cópia"). Pelo Chrome, na conta dona, só o SalarioLote mudou: era o `d30b2972` (o do
repositório antes do corte) e passou a ser o `r53/diagnostico-android/salario_lote.gs` atual, `366f6dd3`, o mesmo
medido na cópia `1coYY2bg…`. Antes, cada projeto ganhou a versão 7 de backup ("Antes do SalarioLote novo
(26/10/2026)": Ciclo Maldito 15:59, Era da Revolução 16:03), implantação de biblioteca arquivada em seguida.
Depois de salvar e recarregar, nas duas: SalarioLote `366f6dd3`, EditorR53 `68f21a08`, módulo `52fc6903`, e
Codigo, LotePaleta e PaletaSegundoPlano como estavam. Na cópia, edição simples 8,9–11,7 s → 4,7–5,3 s.

## Cortes da noite · 26–27/10/2026

Aval do Mizuki no cartão ("Pode instalar nas duas"). Pelo navegador do app, na conta dona, um trecho único
(`r53/diagnostico-android/preparar_cortes_noite.js`, arquivo `2f5249c7…`) troca o módulo (remendos 39–41), o Codigo
(hash do módulo e atalho regerado) e o EditorR53; ele confere Codigo `452445ac`, EditorR53 `68f21a08`, módulo
`52fc6903` e o bloco do atalho antes e recusa sem gravar se algo não bater.

Nas duas, versão 8 de backup ("Antes dos cortes da noite (26/10/2026)": Era da Revolução 20:48, Ciclo Maldito
20:59), implantação de biblioteca arquivada em seguida. O trecho conferido na página (`2f5249c7…`) rodou sem erro.
Depois de salvar e recarregar, iguais nas duas:

| Arquivo | Antes | Depois |
|---|---|---|
| Codigo | `452445ac…` | `dc1aa740…04b1` |
| EditorR53 | `68f21a08…` | `c3d31096…153e` |
| Analise (pedaço 2) | `b367b063…` | `2ea7e9d4…` |
| Ficha, Invocacoes (pedaços 0 e 1) | `6012dcb3…`, `ebf20bb1…` | sem mudança |
| Configuracao, Origens (pedaços vazios) | `bb784c6d…`, `90095228…` | sem mudança |
| LotePaleta, PaletaSegundoPlano, SalarioLote | `848e878b…`, `a5a0e83d…`, `366f6dd3…` | sem mudança |

Módulo `9dc3480a…9ffc`: o hash no Codigo e os três pedaços `R53_CODIGO_` descomprimidos (850000, 850000 e 237688
caracteres; os dois últimos arquivos vazios). Ficha e Invocacoes iguais é esperado: o começo do gzip saiu idêntico.

## Caixas de ± sem abrir o módulo · 26–27/10/2026

Aval do Mizuki no chat ("Pode instalar o atalho das caixas de ± nas duas oficiais (versão 9 de backup antes), exigindo o
Codigo dc1aa740 → 07a66b0a igual ao da cópia"). Pelo Claude in Chrome, na conta dona (`/u/0/` naquele navegador), só o
Codigo mudou: o bloco gerado do atalho no fim dele trocado pelo `r53/atalho_livre.gs` de `36d08ad` (`be124889…`, baixado
pela página do editor e conferido lá), com as mesmas conferências do `preparar_caixas_delta.js` (Codigo `dc1aa740` e
atalho `fa5e793c` antes, Codigo `07a66b0a` depois). Medido antes na cópia `1aNuAcj2…` (MEDICAO-DESEMPENHO-2026-10-26-fim).

Antes, nas duas, os dez arquivos conferidos iguais aos da tabela dos cortes da noite, e a versão 9 de backup ("Antes do
atalho das caixas de ± (27/10/2026)": Era da Revolução 23:54, Ciclo Maldito 23:56 de 26/10), implantação de biblioteca
arquivada em seguida. O trecho devolveu `07a66b0a` nas duas. Depois de salvar e recarregar, iguais nas duas:

| Arquivo | Antes | Depois |
|---|---|---|
| Codigo | `dc1aa740…04b1` | `07a66b0a…bc8f` |
| EditorR53, Analise, Ficha, Invocacoes | `c3d31096…`, `2ea7e9d4…`, `6012dcb3…`, `ebf20bb1…` | sem mudança |
| Configuracao, Origens, LotePaleta, PaletaSegundoPlano, SalarioLote | `bb784c6d…`, `90095228…`, `848e878b…`, `a5a0e83d…`, `366f6dd3…` | sem mudança |

Módulo `9dc3480a` sem mudança (os pedaços não foram tocados). Para voltar: versão 9 de cada projeto.

## XP com o nível escrito na mão · 27/10/2026

Aval do Mizuki no chat ("okey", depois de testar a cópia `14l3Bywwm…` "TESTE xp nível (descartável)" no celular e
pedir os "meios de segurança"). Pelo Claude in Chrome, na conta dona (`/u/2/` no Chrome do Linux). Antes, nas duas, os dez
arquivos iguais à tabela das caixas de ± (Codigo `07a66b0a`), e a versão 10 de backup ("Antes do XP com nível escrito na
mão (27/10/2026)": Era da Revolução 11:05, Ciclo Maldito 11:09), implantação de biblioteca arquivada em seguida.

- Projeto: só o Codigo, o bloco gerado do atalho no fim trocado pelo `r53/atalho_livre.gs` de `ed4ff8c` (`8c42ec76…`,
  baixado pela página do editor e conferido lá), com as conferências do `preparar_xp_nivel.js` (Codigo `07a66b0a` e
  atalho `be124889` antes, Codigo `97c430f4` depois).
- Planilha, pela API do Sheets: DADOS!CY54 "xp base" e CZ54 0; DADOS!CZ47 com `+N(DADOS!$CZ$54)` no fim; as notas de
  FICHA!AH10 (NÍVEL), FICHA!AN10 (XP) e FICHA PESSOAL!AW10 (XP TOTAL); e o NÍVEL (FICHA!AH11) em menu estrito de 1 a 30.

Depois de salvar e recarregar, iguais nas duas:

| Arquivo | Antes | Depois |
|---|---|---|
| Codigo | `07a66b0a…bc8f` | `97c430f4…73f9` |
| EditorR53, Analise, Ficha, Invocacoes | `c3d31096…`, `2ea7e9d4…`, `6012dcb3…`, `ebf20bb1…` | sem mudança |
| Configuracao, Origens, LotePaleta, PaletaSegundoPlano, SalarioLote | `bb784c6d…`, `90095228…`, `848e878b…`, `a5a0e83d…`, `366f6dd3…` | sem mudança |

Módulo `9dc3480a` sem mudança. O Ficha do projeto continua `6012dcb3`: o Ficha.gs regerado no repositório (base do XP e
menu do NÍVEL) só entra num pacote inteiro; nas oficiais a planilha já foi acertada à mão. Para voltar: versão 10 de cada
projeto, e na planilha desfazer as cinco mudanças acima.
