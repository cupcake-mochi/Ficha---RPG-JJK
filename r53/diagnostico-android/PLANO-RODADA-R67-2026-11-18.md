# Plano da rodada R67 nas oficiais · 18/11/2026

Base: `codex/corrige-colagem-atributos-20261108` em `95d46ee` (merge da #135), depois de `git fetch`. Nenhum agente
usado. Plano aprovado por ele ("Pode seguir"); a seção 0 diz o que foi feito e onde o feito mudou o plano.

## 0. Feito em 18/11 (offline, nada rodou no Google)

- `gerar_maxima_r67_plano.js` → `maxima_r67_plano.json` (~110 KB): 93 células, 54 notas, mesclas, 13 caixas, 39
  fundos, 5 formatos, 45 arestas de borda, 8 colunas da DADOS_R53 em trecho de linha, 13 contextos do editor.
- `preparar_maxima_r67.js`: o projeto (Codigo, EditorR53, módulo, AnaliseEstatica) e os pedidos da planilha.
- `r53/testes/maxima_r67_rodada.js`, no smoke (`nuvem-b47/conferir.py`): 52 verificações; 58 com
  `R67_PROJETO=<pasta com os .gs instalados>`.
- Sobre o projeto das oficiais reproduzido offline (o achatado do ensaio de 16/11 + os passos até `94f1a184`):

  | arquivo | antes | depois |
  |---|---|---|
  | Codigo | `94f1a184f2af` | `d7031a736b37` |
  | EditorR53 | `35065b22a3ea` | `f23329f99dc3` |
  | AnaliseEstatica | `450709a1a988` | `4543892d3cd9` |
  | Ficha (parte 0 do módulo) | `6c0391edac63` | `57d66d9cb7b5` |
  | Invocacoes (parte 1) | `e73584ddf3b1` | `650d9336aba9` |
  | Analise (parte 2) | `98f8f056cd4f` | `948bd0b51a61` |

  Fonte do módulo `35d00ae2…` → `ae0ed42b84da…` (3 partes); catálogo do editor `da1226e9…` → `eb35b245e9db…`; os
  outros arquivos sem mudança. Carregado em node: atalho ligado antes e depois; os 67 alvos dos cartões e as 54 notas
  iguais ao `0ac372f`; nada fora dos alvos mudou; editor com 251 contextos; reaplicar o ajuste não muda nada.

**Onde o feito mudou o plano:**
- **DADOS_R53 não está no pacote** (pacote leve: `VALORES_R53_DADOS_*_ = null`). O molde da R67 cobre só FA,
  INVOCAÇÕES e DADOS_AM. Quem guarda fórmula da DADOS_R53 é o restaurador da Prática (`R53_PRATICA_MONTAGEM_` e
  `R53_PRATICA_CACHE_`): o preparador troca nele a FX das 251 linhas e as 14 células das linhas 252–253 (fecha o risco
  da seção 7 sobre o `PraticaCotidiana.gs`).
- **Atalho:** o `--conferir` só aponta FA T355 (rótulo) e T356 (caixa); nenhuma é fórmula. A T357 (fórmula nova)
  entrou no mapa `R53_LIVRE_`. As caixas SEM DANO das INVOCAÇÕES já estavam fora dos livres.
- **Planilha por `findReplace` com regex, não `updateCells`:** a FX tem ~19 mil caracteres por fórmula; mandar a
  fórmula inteira dava 12 MB. Cada pedido troca só o trecho que muda, numa faixa contínua de até 40 linhas, e tem a
  contagem esperada (uma troca por célula); contagem diferente = parar. O número da linha é o grupo `(\d+)` (RE2, sem
  retrovisor). Há a variante `--ponto-e-virgula` se o idioma da cópia pedir. A volta é a regex inversa, mais a foto
  das 8 faixas dos cartões e da DADOS_AM tirada antes.
- **Forma B:** no editor vão os arquivos inteiros prontos, conferidos pelo hash, não trechos de console.
- Fundos, bordas, formatos, mesclas e caixas dos cartões vão só pela API; o molde leva fórmula, notas, mesclas e caixas.

**O que não rodou no Sheets:** nada desta rodada. Nem o preparador no Apps Script, nem os pedidos na API, nem o
`construir()` com o `criarGrupos_`, nem o custo do `r53AjustarMaximaR67_` na carga do módulo. Tudo isso é o ensaio
(seção 6), que ainda não aconteceu.

Leitura: `AGENTS.md` (12/11–17/11), `CORRECAO-MAXIMA-R67-2026-11-14.md`, `PLANO-RODADA-OFICIAIS-2026-11-16.md` (D1 e
#117), `ENSAIO-RODADA-OFICIAIS-2026-11-16.md`, `r53/OFICIAIS.md`. Conferências feitas em node, sem Google, sobre o
projeto achatado salvo no ensaio de 16/11 (pasta privada `rodada-oficiais-20261116/ensaio/era/projeto-achatado`).

## 1. De onde as oficiais partem hoje (pelo `OFICIAIS.md`, 18/11)

| Arquivo | Hash instalado | Observação |
|---|---|---|
| Codigo | `94f1a184f2af…` | achatado + atalho + salário + ganchos da ANALISE + cortes B e C |
| EditorR53 | `35065b22a3ea…` | `676337f1` + corte A corrigido |
| AnaliseEstatica | `450709a1a988…` | igual ao repo em `9553ff6^` (conferido) |
| módulo (texto do `new Function`) | `35d00ae28bfa…` | 3 partes, em Ficha / Invocacoes / Analise |
| `R53_LIVRE_HASHES_` | `[35d00ae2…, da1226e9…]` | [0] módulo, [1] o `r53ConfigEditor_` |

O módulo e o ABAS que o `construir()` e o restaurador usam moram **dentro** do pacote; o EditorR53 guarda os
contextos compactados dentro do `r53ConfigEditor_`.

## 2. O que a R67 muda (gerador `f474691` → `0ac372f`, contado agora)

| Onde | Guardado no molde | Na planilha | Além da fórmula |
|---|---|---|---|
| DADOS_R53 | 291 entradas | 2.034 células: J e O (13 cada, uma por Máxima) e 251 em CV, DA, DB, DG, DH, DI, FH, FX | — |
| FICHA AMALDIÇOADA | 6 | R356, N355/N357, T355:T357 (caixa SEM DANO) | 5 notas; mesclas R355:T355 e R356:T357 viram R:S; caixa em T356; fundos, bordas, formatos |
| INVOCAÇÕES | 60 | 12 domadas × (PV TEMP. + SEM DANO) | 49 notas; 36 mesclas desfeitas; 12 caixas (M e AF); fundos, bordas |
| DADOS_AM | 1 | HM38 | — |
| EditorR53 | contextos 44 e 204–248 | — | a conta da R356 que o editor reescreve |

Nada mais muda: nos outros `.gs` só o carimbo `geracao`, e o texto do R68 não aparece na planilha.

## 3. O preparador: `preparar_maxima_r67.js`

Um preparador, quatro partes, todas offline em node e cada uma com recusa se o "antes" não bater. No editor vai por
trecho de console (como o achatador), com `window.__r67Reverter()`.

**3.1 Molde da R67 no Codigo (`r53AjustarMaximaR67_`).** No modelo do `preparar_molde_api.js`: plano congelado
(`maxima_r67_plano.json`, gzip+base64) com antes/depois das 358 entradas guardadas, das 54 notas e das mesclas e
caixas das duas abas de cartão. Roda na carga do módulo, **depois** do `r53AjustarMoldeApi_`. Aceita, em cada alvo,
só o antes exato ou o depois; confere tudo antes de trocar o primeiro.
- Por que no Codigo e não no texto do pacote: o texto do pacote ainda tem os moldes de 27/10, e quem leva ao estado
  atual são os `r53Ajustar*` na carga. O "antes" da R67 só existe depois deles.
- **Fase 0 desta rodada:** carregar o módulo achatado em node com os `r53Ajustar*` e conferir que as quatro abas saem
  iguais ao gerador `f474691` nos alvos. Se não sair, paro e trago a diferença.
- Fundos, bordas e formatos ficam fora do molde: o restaurador só devolve fórmula. O `construir()` usa o molde, então
  num `construir()` futuro esses formatos viriam do pacote antigo (risco já conhecido, ver seção 7).

**3.2 Contextos do EditorR53.** Abre o gzip do `r53ConfigEditor_`, confere o hash, troca os contextos 44 e 204–248
pelos do `0ac372f` (cada antes conferido igual ao do `f474691`, e nenhum outro contexto muda), recompacta e grava o
hash novo. Parte do `35065b22` (com o corte A); recusa outro.

**3.3 Consertos do `construir()` da PR #135.**
- `criarGrupos_` e a guarda do estilo moram no `Ficha.gs`, que está **dentro do pacote**. As duas trocas de texto
  acham exatamente 1 ocorrência no módulo `35d00ae2` (conferido). Como o pacote está achatado e o achatador recusa
  pacote achatado, o preparador faz a troca no achatado: descompacta, confere `35d00ae2`, troca, recompacta, grava
  as partes, o tamanho e o "fonte <hash novo>" no `r53Modulo_`.
- O `criarGrupos_` usa o serviço avançado Sheets. O manifesto das oficiais tem esse serviço desde 24/10
  (`FICHA-DEFINITIVA-2026-10-24.md`); confiro na leitura antes. Sem ele, cai no caminho antigo, sem erro.
- `breakApart` no `AnaliseEstatica`: troca o arquivo inteiro, `450709a1a988` → `4543892d3cd9` (o do repo hoje).

**3.4 Atalho calado (os dois hashes).**
- [0]: o módulo muda (3.3), então `35d00ae2` → hash novo.
- [1]: o `r53ConfigEditor_` muda (3.2), então `da1226e9` → hash novo. O `preparar_religar_atalho.js` hoje só cuida do
  [0]; estendo para o [1].
- **Antes de religar, o `--conferir`.** A R67 cria células novas que o jogador clica: a caixa SEM DANO (FA T356 e as
  12 das INVOCAÇÕES) e a porta do PV TEMP. Se alguma estiver no mapa de livres, o atalho engole o clique e a caixa não
  chega ao editor. Se o `--conferir` apontar alguma, o caminho é regerar o mapa da aba com `r53/atalho_livre.js`, e
  isso vira um passo a mais (trago antes de fazer).
- Ordem: o atalho é o último passo de código, e cada passo confere que o anterior não o desligou.

## 4. O plano de planilha (pela API, sem onEdit)

Gerado pelo preparador como `batchUpdate` com guarda (antes exato, senão para), mais a inversa:
- DADOS_R53: 26 células soltas + as 8 colunas em faixas de **~40 linhas** (lote maior dá "service unavailable",
  visto no #117). *(Mudou: `findReplace` com regex e contagem esperada; ver seção 0.)*
- FA e INVOCAÇÕES: fórmulas, notas, mesclas, caixas, fundos/bordas/formatos dos alvos.
- DADOS_AM!HM38.
- Ordem: DADOS_R53 → DADOS_AM → cartões. Desfazer mesclas mexeu em borda e validação vizinha no ensaio de 16/11
  (P327/Q327 e D35:F36): a inversa relê também os vizinhos.

## 5. Testes com defeitos plantados (`r53/testes/maxima_r67_rodada.js`, no smoke)

- Plano: contagem por aba (291/6/60/1), alvos únicos, antes ≠ depois, igual ao gerador nos dois lados.
- Molde: aplica no ABAS do `f474691` e sai igual ao do `0ac372f`; aplicar duas vezes não muda; antes divergente
  recusa sem trocar nada.
- EditorR53: só 44 e 204–248 mudam; contexto alheio alterado recusa; hash do gzip confere.
- Pacote: as duas trocas do `Ficha.gs` e o `breakApart`; texto já trocado ou ausente recusa; o código novo compila.
- Atalho: [0] e [1] seguem o código novo; Codigo com atalho já desligado recusa.
- Planilha: cada pedido tem guarda; lote da FX com mais de 40 linhas recusa; a inversa volta ao antes.
- Defeitos plantados (cada um tem de acender): a conta antiga da R356; um contexto 44 antigo; uma célula da FX trocada;
  a caixa SEM DANO no mapa de livres; o [1] do atalho esquecido; o `criarGrupos_` duas vezes; o HM38 com a Forma.
- Com o projeto privado: a cadeia inteira sobre o achatado do ensaio (`a7f6f330` + os passos de 16/11–18/11
  reproduzidos até `94f1a184`) e os hashes de chegada. Se a reprodução não chegar ao `94f1a184`, paro e aviso.

## 6. Ensaio numa cópia descartável (nunca na oficial)

1. Cópia pelo Drive de uma oficial, na conta dona (leva o projeto). Preciso de você para isso, ou do seu ok para eu
   fazer pelo painel do navegador.
2. Ler os hashes da seção 1. Divergiu, para.
3. Arquivos prontos no editor (forma B): EditorR53, Codigo, Ficha/Invocacoes/Analise, AnaliseEstatica; Ctrl+S,
   recarregar, reler hashes (tabela da seção 0).
4. Planilha pela API, com guarda e releitura.
5. Testar no Sheets: Máxima pessoal com dano, cura, PV temp. e SEM DANO; uma domada; trocar de Classe e ver a R356
   reescrita com "− Melhorias"; digitar por cima da R356 e ver voltar a fórmula nova; um Buff (atalho ligado, medir
   o `R53_ONEDIT`); clicar SEM DANO e ver que o onEdit roda; varredura de erro em todas as abas.
6. `construir()` na cópia **só com o seu ok** (é o único jeito de provar o `criarGrupos_` e a guarda do estilo).
7. Inversa e reaplicação, como em 16/11. A cópia fica para você apagar.

### 6.1 O que rodou de verdade em 18/11 (cópia `19XMnZ…`, feita da oficial `19I1mr…` na conta dona)

Rodou:
- Os seis arquivos foram instalados no editor (forma B), buscados de um servidor local (`servir.js`, porta 8767), porque o
  `eval` é barrado pelos Trusted Types. Depois de salvar e recarregar, os hashes relidos batem com a seção 0.
- DADOS_R53: 26 células por `updateCells`, mais CV, DA, DB, DG, DH, DI, FH e FX por findReplace com regex. As contagens
  vieram todas como esperado (2.034 no total).
- Cartões da FA, das INVOCAÇÕES e da DADOS_AM!HM38: 263 pedidos em 3 chamadas, todos aceitos.
- Varredura das células lidas pela API: nenhum `#`.
- Marcar o SEM DANO da FA (T356) pela API faz a O46 virar "Sem dano". A caixa voltou para FALSE depois.

Achado: a planilha está em pt_BR. Fórmula com vírgula dá "Formula parse error", então o pedido sai com
`--ponto-e-virgula`. O `valorApi` agora converte também os `updateCells`, e o teste confere isso.

**Não rodou no Sheets (fica para você):**
- Os testes do passo 5 pela interface: dano, cura, PV temporário, domada, troca de Classe com a R356, digitar por cima,
  Buff com `R53_ONEDIT` medido e o clique no SEM DANO disparando o onEdit. Escrita pela API não dispara onEdit, e as
  linhas da seção estão num grupo fechado no painel estreito.
- O `construir()`, que não foi pedido.
- A inversa e a reaplicação. A volta da DADOS_R53 existe nos pedidos de volta. A dos cartões não tem pedido pronto: o
  caminho é o backup.
- A foto de antes dos 6 blocos das INVOCAÇÕES. Só a FA N355:U358 e o HM38 foram lidos.

### 6.2 Ensaio de 19/11 (cópia `1H6snr…`, feita da Ciclo oficial) e instalação nas oficiais

Rodou na cópia:
- Os onze hashes de partida batiam com o "antes"; os seis arquivos instalados e relidos no "depois".
- DADOS_R53: 26 células e 2.008 trocas (251 por coluna). Cartões, notas, validação, fundos, mesclas e bordas aceitos.
- Pela interface, cartão da FA: nome "Teste R67" e DANO marcado deram R356 "8 − Melhorias 0 = 8 pontos", P356 "5 PE",
  L357 "24d8"; a nota nova aparece na caixa. Depois DANO desmarcado e SEM DANO marcado.
- Execuções: as duas primeiras edições (nome e dano) estouraram os 30 s (30,6 s), as seguintes levaram 12,1 s e 6,6 s.
  Leitura: código frio logo depois de instalar.

Não rodou na cópia: o resultado do SEM DANO lido de volta, troca de Classe com a R356, domada, Buff com `R53_ONEDIT`,
a inversa e o `construir()`. Os valores de teste ficaram na cópia (D356 "Teste R67", T356 marcado).

Instalação nas oficiais em 19/11, com o "Pode instalar" do Mizuki: ver `r53/OFICIAIS.md`, seção "Técnica Máxima R67".

## 7. O que fica de fora e os riscos

- Oficiais: nada nesta sessão. Depois, só com você no PC e backup antes.
- `construir()` nas oficiais: não. Num `construir()` futuro com este Codigo, os formatos dos cartões vêm do pacote
  antigo (3.1); o molde de fórmula, notas, mesclas e caixas vem certo.
- `PraticaCotidiana.gs` repõe as linhas 252–253 com a fórmula de antes da R67 nas 14 células; não muda número.
- Fichas já copiadas por jogadores não recebem nada.
- Custo por execução: a carga do módulo ganha mais um `r53Ajustar*` (o do molde API custou ~10–20 ms em node).
  Meço no ensaio.
