# Fichas oficiais atuais · 25/10/2026

Estes são os **dois modelos oficiais**, confirmados expressamente pelo usuário em 25/10/2026:

| Modelo | Google Sheets | Apps Script vinculado |
|---|---|---|
| Ficha - Era da Revolução (CM) | [Abrir ficha](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit) | [Abrir projeto](https://script.google.com/u/0/home/projects/1B6coyZOopuZb5encJpkAGalDcHUp5X4nwXc5hf9OkpNyTTEZWcVGrdtl/edit) |
| Ficha - Ciclo Maldito (CM) | [Abrir ficha](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit) | [Abrir projeto](https://script.google.com/u/0/home/projects/1xSJkCsmx7ygqdjMXv0NsQhs9XSwo9A_Ow-oJzqQNP-0iibueRi1v9s-M/edit) |

A antiga `1u0zWQ…`, a C, a candidata A `1427…` e as cópias de ensaio são referências históricas. Não substituir estes dois endereços pelos links de publicações antigas. A ficha do amigo usada para diagnóstico não integra este par e não foi alterada.

## Técnica Máxima R67 · 19/11/2026

Pedido do Mizuki no chat, depois do ensaio na cópia `1H6snr…`: "Pode instalar". Preparador e pedidos da PR #136
(ramo `claude/rodada-r67-0b8c4f`, commit `76bc667`); roteiro em `diagnostico-android/PLANO-RODADA-R67-2026-11-18.md`.
A Era foi feita primeiro; a Ciclo depois, em outra sessão do Claude que retomou do mesmo ponto, pelo Brave.

- **Backup antes**, pela página de cópia de cada oficial (leva o projeto junto), no Drive da conta dona:
  "BACKUP antes da R67 19-11-2026 · Era da Revolução" (`16fAW6…`) e "… · Ciclo Maldito" (`1sw4tc…`).
- **Projeto:** os onze arquivos relidos antes batiam com o "antes" do manifesto nas duas. Seis trocados, iguais nas duas
  e relidos depois de recarregar o editor: Analise `98f8f056cd4f` → `948bd0b51a61`, AnaliseEstatica `450709a1a988` →
  `4543892d3cd9`, Codigo `94f1a184f2af` → `d7031a736b37`, EditorR53 `35065b22a3ea` → `f23329f99dc3`, Ficha
  `6c0391edac63` → `57d66d9cb7b5`, Invocacoes `e73584ddf3b1` → `650d9336aba9`. Os outros cinco sem mudança. O Codigo
  novo já traz os dois `R53_LIVRE_HASHES_` novos, então o atalho segue ligado.
- **Planilha, pela API do Sheets:** 26 células da DADOS_R53; 2.008 trocas com regex (251 em cada coluna: CV, DA, DB,
  DG, DH, DI, FH e FX, como no ensaio); cartões da FA, das 12 domadas e a DADOS_AM!HM38 em 206 pedidos (80, 30, 25 e
  71), todos aceitos. O cartão da FA mostra "SEM DANO" com a caixa desmarcada; a HM38 dá 0.
- **Ciclo comparada com a Era** célula por célula, depois das duas prontas: FA J355:U357, INVOCAÇÕES I220:AF1383,
  DADOS_AM!HM38 e DADOS_R53 A2:GA253, 71.293 células. Fórmula, nota, validação, fundo e mesclas iguais. Nenhum `#`
  em DADOS_R53!CV2:GA253 nas duas.
- **Exportação:** menu Bot > Exportar para o bot nas duas, em dia às 11:23 (Ciclo 11:23:08, Era 11:23:36). A ANALISE
  de cada uma é igual à do próprio backup, fora `analise.exportada_em`: 18.502 linhas, formato 13, sem `#`. (Os
  modelos estão vazios; a Máxima só muda número quando alguém monta uma.)
- **Não rodou nas oficiais:** nenhum teste pela interface (o `onEdit` da R67 não foi medido nelas), o celular, um
  `construir()`, a inversa. No ensaio as duas primeiras edições depois da instalação estouraram os 30 s (código frio)
  e as seguintes levaram 12,1 s e 6,6 s; a primeira edição de cada ficha nova pode repetir isso.

Para voltar: restaurar dos backups `16fAW6…` e `1sw4tc…` (planilha e projeto). A volta da DADOS_R53 também existe nos
pedidos de volta do preparador; a dos cartões não.

### Ensaio numa cópia de jogador, depois da instalação · 19/11/2026

Pedido do Mizuki no chat: "va fazendo oq falta" e, para o script da cópia, "Autorizei, pode seguir". Nada foi feito
nas oficiais. Os testes rodaram em duas cópias descartáveis feitas pelo Drive, as duas já na lixeira:
- `1KCEtB…`, copiada da Ciclo instalada;
- uma cópia do backup `1sw4tc…`, que é a Ciclo de antes da R67 e serviu de base.

- **Tempo do `onEdit`** (cópia nova, primeira abertura):

  | Medida | Com a R67 | Antes da R67 |
  | --- | --- | --- |
  | `onOpen` | 30,8 s | 23,3 s |
  | Primeira edição de verdade | 30,9 s, estourou os 30 s | 24,6 s |
  | Edições seguintes no cartão | 14,7–16,7 s | 18,9–21,1 s |

  O código frio da R67 pesa uns 6 s a mais e passa do limite na primeira edição. Já aquecido, não ficou mais lento.
- **Máxima de ponta a ponta** no nível 17 (dropdown FICHA!AH11), no cartão da FICHA AMALDIÇOADA:
  - Explosão com dano dá 19d8, saldo 8 e 25 PE, sem aviso;
  - DADOS_R53 linha 46 dá base 0, forma 5 e orçamento 8;
  - é a mesma conta do modelo do bot.
- **Bot, rodado localmente** na ANALISE exportada pelo menu da cópia ("Bot: em dia · 19/11 12:40", formato 13):
  - O `conferir` local dá o mesmo resultado da produção: 12 erros, todos `invocacao.N.exp.acerto`. A ficha exporta essa
    chave como `resultado`, e o esquema B47 do bot ainda espera `entrada`. **Esses erros de formato fazem o bot
    parar antes dos cartões** ("Formato/entradas inválidos: contas dependentes não executadas"). Por isso nenhuma ficha
    formato 13 tem a Máxima, nem nenhum outro cartão R53, conferida no Discord hoje. Isso já acontecia antes da R67.
  - Quando a parte dessas 12 chaves é trocada para `entrada` no teste, o bot confere a Máxima: "Classe 5 · Dano 19d8 ·
    25 PE · saldo 8 · ficha VÁLIDO". Ele também acusa 22d8, 30 PE e saldo 2 como errados.
- **`construir()`:**
  - Não roda nas oficiais nem nas cópias delas. O pacote leve trava `construir`/`continuar`/`acabar`, e o seletor do
    editor não lista função. Ficha nova continua pelo pacote completo do repositório.
  - O `regressao-construir.js` no ramo da R67 roda 7 min e para na aba FICHA, porque o Sheets de mentira não imita
    `Sheet.hideRows()`. Com esse método acrescentado só no teste, ele passa e para na CONFIGURAÇÃO:
    `Range.getTextStyle()`, que o Apps Script tem mas a lista `REAIS` não tem.
  - As duas chamadas são das extensões custom de 18/10 (`a0b23e5`, `ccbd053`). Então o arnês está desatualizado desde
    então, e o `construir()` completo não foi certificado nesta rodada. O remendo do teste foi desfeito.
- **Não rodou:** o celular (não há como daqui) e o `construir()` num Sheets de verdade com o pacote completo.

## ANALISE estática · 17/11/2026

Pedido do Mizuki no chat, com ele no PC: "Sim, as duas coisas" (mesclar a PR #132 da ficha e a RPG---BOT#104 do bot,
e instalar nas oficiais). O bot já lia o formato 13 antes da primeira oficial mudar. Era primeiro, depois Ciclo.
Detalhes do mecanismo: `r53/diagnostico-android/ANALISE-ESTATICA-2026-11-17.md`.

- **Backup antes**, cópia pelo Drive de cada oficial (leva o projeto junto): "BACKUP antes da ANALISE estática
  17-11-2026 · Era da Revolução" e "… · Ciclo Maldito".
- **Projeto:** arquivo novo `AnaliseEstatica` (o `apps-script/AnaliseEstatica.gs`, `6ab0b843…`) e os dois ganchos do
  `preparar_analise_estatica.js` no Codigo (`onEdit` depois da guarda, `onOpen` depois do `r53CuraMenu_()`).
  Codigo `c7f388f70e0a` → `57a8398fa8c5` nas duas. O módulo comprimido não mudou, então o atalho calado continua valendo.
- Relido depois de recarregar o editor, iguais nas duas: Codigo `57a8398fa8c5`, AnaliseEstatica `6ab0b8432a9e`,
  Analise `98f8f056cd4f`, Configuracao/Origens `b5dfcd181c3c`, EditorR53 `676337f165f7`, Ficha `6c0391edac63`,
  Invocacoes `e73584ddf3b1`, LotePaleta `848e878b4a2a`, PaletaSegundoPlano `a5a0e83def3c`, SalarioLote `aaaa74f32b0c`.
- **Primeira exportação:** o item "Bot > Exportar para o bot" do menu deu o erro genérico ("Ocorreu um erro no script
  exportarParaOBot"), sem execução registrada. Rodado pelo editor (Executar `exportarParaOBot`), funcionou:
  - Era: 93 s, sem pedir autorização. CARTEIRA AH4 "Bot: em dia · 17/11 18:19".
  - Ciclo: pediu autorização (o Mizuki autorizou), 129 s. AH4 "Bot: em dia · 17/11 18:29".
  - Cada exportação criou a `ANALISE_MODELOS` oculta e a caixa AT4 da CARTEIRA.
- **CSV do bot** (link `gviz … sheet=ANALISE`), baixado depois de cada exportação: `formato.versao` 13,
  `analise.estado` `em_dia`, `analise.exportada_em` com a hora da exportação, nenhum `#` de erro, as mesmas 18.500 chaves
  nas duas. No Ciclo, comparado linha a linha com o CSV vivo de antes (formato 12): só mudaram `formato.versao` e as
  duas linhas novas.
- **Escorregão na Ciclo:** ao medir o ±, o Buff da vida (FICHA!P26) foi para 10 em vez de 1. O `onEdit` dessa edição
  (18:31) falhou depois de 150 s com "erro do servidor" da Google (a página de execuções também dava 500), então a
  ANALISE não foi marcada desatualizada. Digitar 0 na célula não pegou; o 0 foi escrito pela API do Sheets (sem
  `onEdit`). Relido: P26 0, vida máxima J26 0 (fórmula), vida atual D26 19, como antes. O CSV exportado às 18:29 já
  tinha `buff.vida` 0 e `vida_max` 0, então continua em dia.
- **Ciclo, 18/11 de manhã** (painel do navegador do app com login refeito):
  - **Menu Bot > Exportar para o bot funcionou:** execução do tipo "Menu", 67,4 s, em dia às 08:34. O erro de 17/11
    não voltou. O que mudou entre um e outro foi a autorização da Ciclo e o login refeito; não se sabe qual dos dois
    resolveu. A Era não foi testada pelo menu.
  - **Caixa AT4 funcionou com cliques de verdade, mas em três marcações:** `onEdit` de 24,1 s (6.488/18.480), 26,0 s
    (12.986/18.480) e **29,1 s** (em dia às 08:47), a última a menos de 1 s do limite de 30 s do gatilho simples. Na
    cópia da fase 1 eram duas marcações (26,6 s e 16,4 s).
  - CSV depois de cada exportação: igual, linha a linha, ao exportado em 17/11 (fora `analise.exportada_em`), sem `#`.
- **Caixa em blocos de 4.000 linhas, 18/11** (commit `bfdcf23`): backup antes, no Drive da conta dona,
  "BACKUP antes da caixa em blocos menores 18-11-2026 · Era da Revolução" e "… · Ciclo Maldito". Só o arquivo
  `AnaliseEstatica` mudou, `6ab0b8432a9e` → `7aea9ab87a17`, nas duas; os outros dez arquivos relidos iguais. Medido na
  Ciclo: 26,2 s, 16,3 s (sem avanço) e 26,5 s por marcação, sem ganho claro (ver
  `ANALISE-ESTATICA-2026-11-17.md`). Exportação terminada pelo menu (70,7 s), em dia às 09:17, CSV igual.
  Duas cópias feitas antes pelo conector do Drive ficaram na outra conta, sem acesso para conferir; não valem como
  backup.
- **Caixa lê só o bloco e exporta em qualquer toque, 18/11 à tarde** (commits `37506b2` e `065be2a`, PR #133).
  Pedido do Mizuki no chat: "Publica e instala". Backup antes, pela página de cópia de cada oficial (leva o projeto
  junto), no Drive da conta dona: "BACKUP antes da caixa em qualquer toque 18-11-2026 · Ciclo Maldito" (`1i2a9Z…`)
  e "… · Era da Revolução" (`1ioU9w…`). Só o arquivo `AnaliseEstatica` mudou, `7aea9ab87a17` → `450709a1a988`, nas
  duas; relido depois de recarregar o editor, e os outros dez arquivos iguais aos de antes. Medido antes só na cópia
  de teste (`1i7jy5b6…`, ver `ANALISE-ESTATICA-2026-11-17.md`); nas oficiais nenhuma marcação nem exportação rodou
  depois da instalação.
- **Testado logo depois, 18/11 10:31–10:38** (pedido do Mizuki: "faça os testes"), no painel do navegador do app:
  - **Ciclo, caixa AT4:** de em dia até em dia de novo em 5 toques, 20,1, 18,7, 18,3, 19,9 e 20,7 s, todos concluídos
    (na versão anterior eram 24 a 29 s). CSV igual à referência (`8d40252463892e70`, 18.502 linhas, sem `#`).
  - **Era, menu Bot > Exportar para o bot:** 73,7 s, concluído, em dia às 10:37. CSV igual ao de antes da exportação
    (`9bfc57db7091f8fd`, sem `#`). Primeira vez do menu na Era.
  - **Marca `desatualizada`** (na cópia de teste `1i7jy5b6…`, não nas oficiais): editar o portador da CARTEIRA trocou o
    texto para "Bot: desatualizada · marque ao lado" e a ANALISE para `desatualizada`. Essa edição levou **29,97 s** e
    a seguinte 29,55 s, as duas concluídas; o registro diz 19,9 s dentro do código da ficha (`R53_ONEDIT`). É o tempo da
    edição do portador, não da ANALISE (na segunda o estado já era desatualizada), e está colado no limite de 30 s.
- **Não rodou no Sheets (depois dos testes):** a caixa no celular; o ± medido nas próprias oficiais; a troca de paleta
  com a linha 4 da CARTEIRA; um `construir()`.
- **Antes dos testes não tinha rodado:** a caixa nova nas oficiais (nem no PC); o ± medido nas oficiais com o gancho; a marca `desatualizada` depois de uma edição (no
  painel, o teclado não chega à célula e a lista de opções não aceita o clique; a edição feita pelo Mizuki não gerou
  `onEdit`); a caixa AT4 no celular; o menu Bot na Era; a troca de paleta com a linha 4 da CARTEIRA; um `construir()`.
- **Cortes A e B do portador, 18/11 por volta das 11 h** (commits `6840223` e `0381484`, PR #133). Pedido do Mizuki
  no chat: "Sim, instala". Backup antes, pela página de cópia (leva o projeto junto), no Drive da conta dona:
  "BACKUP antes dos cortes do portador 18-11-2026 · Ciclo Maldito" (`17Y3R4…`) e "… · Era da Revolução" (`1s-jeX…`).
  Duas linhas trocadas, cada uma só se o hash de antes batesse:
  - **A** no EditorR53 (o `if(!gs.length)` do `r53Editar_`): o portador não relê o Amparo.
  - **B** no Codigo (o `var nome=` do `salarioEditar_`, o mesmo par do `preparar_portador_sem_trava.js`): no modo
    fórmula o portador não trava nem dá flush.
  - Codigo `57a8398fa8c5` → `261b452940ad` e EditorR53 `676337f165f7` → `abade0324d3f`, iguais nas duas; relido depois
    de recarregar o editor, os outros nove arquivos sem mudança.
  - **Ciclo, portador editado e voltado** (O9 "Teste portador", depois o texto original, conferido pelo CSV):
    `onEdit` de **13,0 s** e **9,8 s**, os dois concluídos (antes dos cortes, na cópia: 22,6 a 30,7 s, um estouro).
    A ANALISE ficou `desatualizada` (AH4 "Bot: desatualizada · marque ao lado"), como deve depois de uma edição.
    A exportação para voltar a em dia não foi rodada por mim (a permissão barrou o clique no menu): o Mizuki rodou
    Bot > Exportar para o bot, em dia às 11:23. CSV igual à referência (`8d40252463892e70` sem a linha
    `analise.exportada_em`, 18.502 linhas, formato 13, sem `#`).
  - **Não rodou:** o portador na Era; o celular; um `construir()`.
- **Corte C e o Amparo sujo, 18/11 por volta das 11:35** (commit `8f46597`, PR #133). Pedido do Mizuki no chat:
  "pode fazer a 1, 3, 4, 5 (todo ganho é bom, se afetar nada negativamente ta tudo bem)". Backup: os de manhã
  (`17Y3R4…` e `1s-jeX…`), anteriores a todos os cortes. Duas trocas, cada uma só se o hash de antes batesse:
  - **C** no Codigo (`preparar_portador_sem_modulo.js`): o portador sai do `r53OnEditOriginal_` depois do
    `r53LivreConferido_`, com o `r53ContinuarPaletaPendente_`, sem carregar o módulo.
  - **A corrigido** no EditorR53: com a marca `r53_amparo_sujo` (Trilha ou Caminho mudou na FICHA) o portador
    sincroniza as Famílias como antes. Sem isso, o `r53LivreConferido_` apagava a marca sem a sincronização rodar.
  - Codigo `261b452940ad` → `94f1a184f2af` e EditorR53 `abade0324d3f` → `35065b22a3ea`, iguais nas duas; relido depois
    de recarregar o editor, os outros nove arquivos sem mudança.
- **Testado nas oficiais, 18/11 11:39–13:40** (no painel do navegador do app):
  - **Portador, Ciclo:** 6,6 s e 10,5 s (com A e B eram 13,0 e 9,8). O registro diz 1,3 s dentro do código
    (`R53_ONEDIT`); o resto é o Google abrindo o projeto. **Era:** 12,8 s e 3,7 s. Nas duas o nome foi salvo, apareceu
    na FICHA PESSOAL, marcou a ANALISE `desatualizada` e voltou ao texto original (conferido pelo CSV).
  - **± na Ciclo** (FICHA!AM34, integridade 25/25): −1 deu 24 em 11,9 s, +1 voltou a 25 em 13,6 s. A vida não serviu
    de teste: com o máximo em 0 (J26), o ± zeraria a vida atual (19). Na Era a vida e a energia estão em 0/0.
  - **Paleta na Ciclo:** "Mizuki · Claro · rosa e magenta" em 19,3 s e de volta a "Mizuki · Escuro · ameixa e rosa"
    em 16,9 s, as duas concluídas. A linha 4 da CARTEIRA (texto "Bot: …" e caixa AT4) pintou com a paleta clara e
    ficou legível; a FICHA voltou igual à da Era.
  - **Depois dos testes:** a ANALISE das duas ficou `desatualizada` (AH4 "Bot: desatualizada · marque ao lado"). O
    Mizuki rodou Bot > Exportar para o bot nas duas: em dia às 14:07 (Ciclo 14:07:11, Era 14:07:54). CSV sem a linha
    `analise.exportada_em` igual à referência de 17/11 (Ciclo `8d40252463892e70`, Era `9bfc57db7091f8fd`), 18.502
    linhas, formato 13, sem `#`.
  - **Não rodou:** o celular.

Para voltar: restaurar o Codigo do backup, ou `node r53/diagnostico-android/preparar_analise_estatica.js --reverter`
no editor e apagar o arquivo `AnaliseEstatica`. A ANALISE fica com valores congelados até alguém refazer as fórmulas
(o `construir()` ou o backup).

## Atalho das edições livres religado · 16/11/2026

Pedido do Mizuki no chat, com ele no PC: "Sim, faz os backups" e "agora q o pc ta desbloqueado, vc consegeu efazer tudo, n?".
A rodada trocou o módulo (9dc3480a → bd42b535 → achatado `35d00ae2`) sem levar o `R53_LIVRE_HASHES_[0]`, então o
atalho das edições livres se desligou calado nas duas oficiais: toda edição simples rodava o onEdit inteiro (~3–5 s de
código a mais). Conserto da PR #127 (`preparar_religar_atalho.js`).
- Backup antes, no Drive da conta dona: "BACKUP antes do atalho 16-11-2026 · Era da Revolução" e "… · Ciclo Maldito".
  Ele pediu para mandar os dois para a lixeira em 17/11, depois da medida.
- Era primeiro, depois Ciclo: o trecho respondeu `9dc3480a -> 35d00ae2` e mudou só a linha do `R53_LIVRE_HASHES_`
  (2.106 linhas antes e depois). Salvo e relido depois de recarregar: `HASHES_[0]` = `35d00ae2`, os dez arquivos com o
  mesmo tamanho. Codigo `a7f6f33050c3` → `c81c26ffa5ee` (conta feita no Node sobre o achatado de referência; o
  `preparar_salario_datas.js` continua encaixando).
- Medido no Ciclo em 17/11, Buff da vida FICHA!P26 (0 → 1 → 0 → 1 → 0, termina como estava): `R53_ONEDIT.ms` 314, 822,
  373 e 328 ms. A Era não foi medida.

Para voltar: trocar o `R53_LIVRE_HASHES_[0]` de volta para `9dc3480af822…` (o atalho só se desliga; nada mais muda).

## Salário: início do período sem hora · 16/11/2026

Com autorização expressa ("Aplica"), as duas oficiais receberam pela API do Sheets a fórmula nova do
`DADOS_SALARIOS!Q2` (PR #128, `preparar_salario_datas.js`, `FORMULA_Q2`). **Só planilha, uma célula em cada:**
nenhum arquivo do Apps Script mudou, nenhum `construir()`, nenhum dado de personagem tocado.
- Antes: `…IF(ult>0;MAX(ult;em);em)…`. Depois: `…IF(ult>0;MAX(INT(ult);em);em)…`.
- Lido antes nas duas: o livro SALÁRIOS vazio e a fórmula antiga. Relido depois: a fórmula nova, o Q2 vazio (carteira
  não emitida, como antes) e Q3:Q8 sem mudança (0, 0, 0, 0, 1000 e 30).

**Trecho no Codigo: aplicado em 17/11/2026**, com o Mizuki no PC ("pode sim, resolver as 3").
- Backup antes, cópia pelo Drive de cada oficial (leva o projeto junto): "BACKUP antes do trecho do salário
  17-11-2026 · Era da Revolução" (`1pw47Xru…`) e "… · Ciclo Maldito" (`1ZtZZTnn…`).
- O trecho do `preparar_salario_datas.js` rodou no editor de cada projeto, os dois pares uma vez cada:
  Codigo `c81c26ffa5ee` → `c7f388f70e0a` nas duas (o `c81c…` é o Codigo já com o atalho religado).
- Salvo e relido depois de recarregar a página: `c7f388f70e0a`, com `MAX(INT(ult);em)` e
  `salarioData_(Math.floor(l[1]))` presentes. Agora o `salarioPrepararFormulas_` (ou um `construir()`) escreve a
  fórmula nova no Q2.
- Não rodou no Sheets: nenhum salário foi fechado depois da troca; a conta só foi conferida na simulação do
  `r53/testes/salario_datas.js` (intervalos de 1, 7 e 30 dias, sem erro).
- Para voltar o código: `node r53/diagnostico-android/preparar_salario_datas.js --reverter` gera o trecho inverso, ou
  restaurar o Codigo do backup.

Antes disso (16/11) o trecho não tinha sido aplicado: o backup nativo não saiu porque a janela do app estava
escondida.

Para voltar: escrever no Q2 a fórmula de antes,
`=IF(ISNUMBER(N2);LET(ult;MAX('SALÁRIOS'!C2:C);em;INT(N2);IF(ult>0;MAX(ult;em);em));"")`. Fichas já copiadas por
jogadores continuam com a fórmula antiga.

## Rodada de 16/11/2026 nas oficiais

Mizuki autorizou: “tô no pc, pode aplicar nas oficiais pelo método que vc testou. faz o backup e confere cada uma antes, começa pela Era e, se der tudo certo, segue pro Ciclo.” A Era foi aplicada e conferida antes do Ciclo.

| Oficial | Backup anterior no Drive | Backup nativo do projeto (Brasília) | Aplicação do plano com guardas e releitura |
|---|---|---|---|
| Era da Revolução | BACKUP antes da rodada 16-11-2026 · Era da Revolução | Versão 16, 18:04 | 7 min 27,067 s |
| Ciclo Maldito | BACKUP antes da rodada 16-11-2026 · Ciclo Maldito | Versão 16, 18:19 | 5 min 47,720 s |

As duas versões têm a descrição “Antes da rodada de 16/11”. A implantação de biblioteca de cada backup foi arquivada. Há cópia privada dos dez fontes de partida.

| Arquivo | SHA-256 antes, ambas | SHA-256 depois, ambas |
|---|---|---|
| Analise | 2ea7e9d453917956… | 98f8f056cd4f86cc… |
| Codigo | 52302778db247518… | a7f6f33050c3bdf9… |
| EditorR53 | 08badae12322539f… | 676337f165f7056d… |
| SalarioLote | aaaa74f32b0c7294… | aaaa74f32b0c7294… |
| Ficha | 6012dcb3dbcd1050… | 6c0391edac631146… |
| Invocacoes | ebf20bb167b57cc7… | e73584ddf3b14a66… |
| Configuracao | bb784c6d0e5fcd08… | b5dfcd181c3ccb43… |
| Origens | 9009522887026e3c… | b5dfcd181c3ccb43… |
| LotePaleta | 848e878b4a2aa4c4… | 848e878b4a2aa4c4… |
| PaletaSegundoPlano | a5a0e83def3c0363… | a5a0e83def3c0363… |

Em cada oficial, os dez arquivos de partida e o módulo 9dc3480af822… coincidiram com a própria cópia fria. Salvo e recarregado o pacote com o molde ensaiado (Codigo b3ed2f7e7b80…, EditorR53 676337f165f7…, módulo bd42b5351ec1… em cinco partes). Por último foram instalados os arquivos achatados ensaiados. O texto descompactado relido tem SHA-256 35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10 em três partes. A instalação usou os controles da guia do editor.

Na planilha, a forma B reuniu #57, #63–#65a, #67, #69–#96, #98, #100–#103, #108, #113, D4, #114 e #119 conforme a tabela por etapa do [ensaio](diagnostico-android/ENSAIO-RODADA-OFICIAIS-2026-11-16.md). As contagens históricas por PR são as do ensaio. Nas oficiais rodou o plano composto de cada uma, com 3.471 pedidos em 18 chamadas da API. Respostas efetivamente confirmadas em cada oficial, por lote na ordem: 37, 710, 468, 71, 71, 98, 90, 90, 85, 89, 86, 88, 89, 83, 82, 519, 658, 57. D2/D3 incluídos no molde, D4 nas duas notas, R67/#117 excluída, aviso âmbar #116/#120 preservado.

Em cada oficial, os 17.632 campos anteriores coincidiram com o ensaio. Na chegada, 25.424 controles de campos e 90 de estrutura passaram. Os dez arquivos foram relidos após recarregar o editor. A varredura das 30 abas encontrou zero erros de fórmula. A seção Prática Cotidiana foi aberta na ficha em modo de consulta. Os testes de personagem ficaram nas cópias.

Para voltar, a versão 16 guarda o projeto anterior e a inversa guardada de cada planilha tem 2.520 pedidos em 15 lotes, incluindo as duas bordas e cinco validações da desmesclagem. Conferir o estado antes de usar a inversa para preservar edições posteriores. As cópias completas e as evidências ficam na pasta privada rodada-oficiais-20261116/aplicacao e as inversas em ensaio/{era,ciclo}/composto/reversao.json.

## Aviso âmbar nas caixas ± · 16/11/2026

Com autorização expressa ("Pode aplicar"), as duas oficiais receberam pela API do Sheets o aviso de
`r53/diagnostico-android/CORRECAO-AVISO-CAIXA-PM-2026-11-14.md`. **Só planilha:** nenhum arquivo do Apps Script mudou,
nenhum `construir()`, nada digitado nas fichas, nenhum dado de personagem tocado.
- FICHA: 3 regras novas no topo da lista, uma para cada caixa ± (AM26, AM30, AM34). Fórmula `=AMxx<>""`, fundo
  `#D89B3A`, texto branco. Notas novas nos títulos AM25, AM29 e AM33.
- INVOCAÇÕES: 1 regra nova no topo, `=X13<>""`, nas 12 caixas ± (X e AQ das linhas 13, 244, 475, 706, 937 e 1168),
  mesma cor. A nota de X12 ganhou a frase do âmbar.

Antes, lido nas duas: FICHA com 22 regras e nenhuma nas caixas ±; AM25/AM29/AM33 sem nota; INVOCAÇÕES com 3 regras
(⚠, "! ", "Dê um nome") em D9:AS1394; X12 com a nota antiga e AQ12 sem nota. Depois, relido nas duas: as regras no topo
com a fórmula, a cor e as faixas certas, e as quatro notas com o texto novo.

Custo: medido na cópia de teste de 16/11, o ± isolado levou 10,5–10,7 s com a regra, o mesmo que sem ela. A cor é
calculada pelo navegador, não pelo script.

Para voltar: apagar a regra de índice 0 das INVOCAÇÕES e as de índice 0 a 2 da FICHA, limpar as notas de
AM25/AM29/AM33 e devolver a nota de X12: "Escreva −9 ou +5 e aperte Enter: a ficha aplica na vida atual e limpa a
caixa. A perda gasta a vida temporária primeiro, e a vida não passa da máxima."

O `Codigo.gs` das oficiais é anterior ao aviso. Um `construir()` com ele remonta as abas sem estas regras e notas. Fichas
já copiadas por jogadores continuam sem o aviso.

## Talentos grátis: o da Origem e o extra · 03/11/2026

Com autorização expressa ("Pode aplicar"), as duas oficiais receberam pela API do Sheets a mudança testada na cópia
"TESTE talento de origem (descartável)" (`1HOae6smqvODRSKqmpW7hi_p_GlUNYnEMBqm-AoT3fK0`). **Só planilha:** nenhum
arquivo do Apps Script mudou, então não houve versão de backup. Antes de mexer, as células que mudam foram lidas nas
duas e estavam com o valor antigo esperado; a R53_LOTE das duas era igual (182.070 caracteres).
- FICHA AMALDIÇOADA: cartas Talento · Origem (J426) e Talento · Extra (P426), com formato, menus e notas; título da
  seção 8 e "GRÁTIS" no orçamento (J54), notas novas em J54 e S54.
- DADOS_AM: linhas 14–15 das passivas, menu rápido de 12 para 14 cartas (KG4:KJ15, 4 trocas de faixa), contas
  HL51:HM55 e o GRÁTIS/LIVRES (KV19, HM21).
- DADOS_CONFIG: alvos "Talentos grátis" e "Feitiços fora dos espaços" nas linhas 52–53.
- ANALISE: 15 linhas novas no fim (18.395–18.409; a aba foi de 18.394 para 18.409 linhas), formato 12.
- R53_LOTE: mapa da paleta com as duas cartas (14 trocas no A1; 182.070 → 182.326 caracteres).

Conferência depois: o mapa das duas é igual ao calculado e o JSON abre; das 174 células do plano, 156 iguais e 18 só
sem as aspas que o Sheets tira de nome de aba sem espaço (o mesmo da cópia); nenhum erro de fórmula. Para voltar:
apagar as linhas 18.395–18.409 da ANALISE, limpar J426:T432 da FICHA AMALDIÇOADA, HO14:HW15 e HL51:HM55 da DADOS_AM
e A52:H53 da DADOS_CONFIG, e devolver o que era: KG4:KJ15 com as faixas até a linha 13 (`$HP$2:$HP$13`, `$HQ`, `$HV`, `$HW`), KV19 `="+"&DADOS_AM!$HM$8`, HM21 `=$HM$13+$HM$8-$HM$17-$HM$18-$HM$19`, J54 "DO LEQUE", D408 "TALENTOS DO LEQUE · um por escolha de Leque, sem ocupar espaço" e o mapa da R53_LOTE (o gerador da main anterior a esta PR reproduz tudo). Fichas já copiadas
por jogadores continuam sem as cartas novas.

## Amparo: dois cortes no recálculo · 03/11/2026

Com autorização expressa (PR48 mesclada), as duas oficiais trocaram **só o EditorR53 e o
SalarioLote**: EditorR53 `d8e99a70…` → `08badae1…` e SalarioLote `366f6dd3…` → `aaaa74f3…`,
relidos iguais depois de recarregar. Antes, cada projeto ganhou o backup nativo **versão 15**
(implantação Biblioteca "Antes dos cortes da reabertura do Amparo (03/11/2026)": Era da
Revolução 10:56, Ciclo Maldito 11:00); para voltar, restaurar esses dois arquivos dessa versão.
Sem mudança, iguais nas duas: Analise `2ea7e9d4`, Codigo `52302778`, Configuracao `bb784c6d`,
Ficha `6012dcb3`, Invocacoes `ebf20bb1`, LotePaleta `848e878b`, Origens `90095228`,
PaletaSegundoPlano `a5a0e83d`. Nenhum dado de personagem foi tocado.

Efeito medido na cópia de teste: reabrir o Amparo da entidade 29,4 s → 17,5 s; fechar
22–23 s → 18,6 s. A primeira reabertura depois da troca ainda lê a MONTAGENS (o fechamento
que está valendo foi feito pelo código antigo, sem guardar os valores); a partir do próximo
fechamento, não. Fichas já copiadas por jogadores continuam com o código antigo.

## Amparo: reabertura · 03/11/2026

Com autorização expressa (PR46 mesclada), as duas oficiais trocaram **só o EditorR53**:
`c3d31096…` → `d8e99a70…`, relido igual depois de recarregar. Antes, cada projeto ganhou o
backup nativo **versão 14** (implantação Biblioteca "Antes do conserto da reabertura do
Amparo (03/11/2026)"); para voltar, restaurar o EditorR53 dessa versão. Nenhum outro arquivo
do Apps Script nem dado de personagem foi tocado. No momento da troca as duas estavam com o
Amparo pessoal Neutra e o das entidades Fechada, sem reabertura pendente.

## Origens da ANALISE · 30/10/2026

Com autorização expressa e dois backups nativos completos anteriores, as duas
oficiais receberam somente as **2.627 correções de C** da PR44. A/B/D foram
relidos integralmente iguais, 18.393 chaves, zero erros retornados e repetição
sem pedidos. Tipos, notas, validações, formatos e as 30 abas foram preservados.
[Aplicação e recuperação](diagnostico-android/ORIGENS-OFICIAIS-2026-10-30.md).

Nenhum Apps Script foi alterado: vinte arquivos salvos relidos iguais. Codigo
`52302778…`, EditorR53 `c3d31096…`, módulo `9dc3480a…`; o molde da ANALISE já
está ausente no pacote otimizado. Não reinstalar o pacote integral por causa
deste conserto. Novas cópias herdam as origens corretas; cópias antigas exigem
atualização própria. A ficha do jogador e a PR31 ficaram fora da aplicação.
Backups e evidências têm registro privado na pasta ignorada, sem IDs no Git.

## Histórico do estado instalado

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

Depois, a pedido dele ("1 - sim"): na Era da Revolução oficial, DADOS!CZ54 (a base do XP) = 3700, para a ficha nascer no
nível 10 com o XP no começo dele (XP total 3700, falta 700 para o 11). O Ciclo Maldito está no nível 2, que já bate com 0.
Conferido pela API: CY47:CZ54 da Era = xp total 3700, nível 10, próximo 4400, deste nível 3700, base 3700.

## Fim da otimização Android · 27/10/2026

Os dois últimos candidatos de fórmula (os 225 INDIRECT da DADOS_CUSTOM e a coluna FD da DADOS_R53) foram medidos numa cópia e
não mudaram o tempo de edição (PENDENCIAS.md, PRs #33 e #34); nenhum foi às oficiais. O Mizuki fechou a otimização ("pode
fechar então"). Estado final das duas oficiais: a tabela da seção "XP com o nível escrito na mão", com a versão 10 de backup.

## XP digitado em cima da caixa de XP · 27/10/2026

Aval do Mizuki no chat ("Acha necessario otimizar mais antes de dar merge e install? se n, pode dar install e merge";
15,4 s na cópia, abaixo dos 20 s que ele pôs de limite). Pelo navegador do app, na conta dona (`/u/1/` lá). Antes, nas
duas, os dez arquivos iguais à seção das missões (Codigo `b8410018`), e a versão 13 de backup ("Antes do XP digitado na
caixa de XP (27/10/2026)": Era da Revolução 14:04, Ciclo Maldito 14:08), implantação de biblioteca arquivada em seguida.

- Projeto: só o Codigo, sete pares (`r53/diagnostico-android/preparar_xp_atualizar.js`): no salário o
  `salarioXpCongelado_`, no atalho a `r53LivreXp_` e o desvio da FICHA!AN11. O trecho conferiu o Codigo `b8410018`
  antes e `52302778` depois.
- Planilha, pela API do Sheets: as notas da FICHA!AH10 (NÍVEL) e AN10 (XP), iguais às do Codigo.gs. Conferido nas duas
  que a DADOS!CY54 tem "xp base" e a FICHA!AN11 é `=DADOS!$CZ$47`, a conta que o atalho devolve.

Depois de salvar e recarregar, iguais nas duas: Codigo `52302778…`; EditorR53 `c3d31096`, Analise `2ea7e9d4`, Ficha
`6012dcb3`, Invocacoes `ebf20bb1`, Configuracao `bb784c6d`, Origens `90095228`, LotePaleta `848e878b`,
PaletaSegundoPlano `a5a0e83d` e SalarioLote `366f6dd3` sem mudança. Módulo `9dc3480a` sem mudança. Para voltar: versão
13 (e as notas antigas estão na seção "XP com o nível escrito na mão").

## Missões sem a leitura dos registros · 27/10/2026

Aval do Mizuki no chat ("oq estavamos fazendo antes pode instalar e mesclar", sobre o PR #39). Pelo navegador do app, na
conta dona (`/u/1/` lá). Antes, nas duas, os dez arquivos iguais à seção da abertura (Codigo `f86423cf`), e a versão 12
de backup ("Antes das missões sem a leitura dos registros (27/10/2026)": Era da Revolução 13:32, Ciclo Maldito 13:35),
implantação de biblioteca arquivada em seguida.

- Projeto: só o Codigo, `salarioMissoesAtuais_`, `salarioSincronizar_` com a `salarioRegistrosIntactos_` nova e a chamada
  no `salarioEditar_` (`r53/diagnostico-android/preparar_missoes_sem_registros.js`). O trecho conferiu o Codigo
  `f86423cf` antes e `b8410018` depois.
- Planilha: nada.

Depois de salvar e recarregar, iguais nas duas: Codigo `b8410018…`; EditorR53 `c3d31096`, Analise `2ea7e9d4`, Ficha
`6012dcb3`, Invocacoes `ebf20bb1`, Configuracao `bb784c6d`, Origens `90095228`, LotePaleta `848e878b`,
PaletaSegundoPlano `a5a0e83d` e SalarioLote `366f6dd3` sem mudança. Módulo `9dc3480a` sem mudança. Para voltar: versão 12.
Efeito esperado: a edição no painel de missões que não forma nem desfaz missão (nome sem tipo, tipo sem nome,
modificadores) sai ~4 s mais rápida; as outras, iguais. Medição na cópia: MEDICAO-DESEMPENHO-2026-10-26-fim.md.

## Abertura sem a releitura diária do salário · 27/10/2026

Aval do Mizuki no chat ("Pode mesclar o PR #37 e instalar o corte da abertura nas duas oficiais, com versão 11 de backup
antes e conferindo os dez hashes"). Pelo navegador do app, na conta dona (`/u/1/` lá). Antes, nas duas, os dez arquivos
iguais à tabela da seção "XP com o nível escrito na mão" (Codigo `97c430f4`), e a versão 11 de backup ("Antes da
abertura sem a relida diária do salário (27/10/2026)": Era da Revolução 12:51, Ciclo Maldito 12:54), implantação de
biblioteca arquivada em seguida.

- Projeto: só o Codigo, uma linha do `salarioCongelar_` (`r53/diagnostico-android/preparar_abertura_salario.js`):
  sem carteira emitida, a próxima conferência vai para `hoje+3650` em vez de amanhã. O trecho conferiu o Codigo
  `97c430f4` antes e `f86423cf` depois.
- Planilha: nada.

Depois de salvar e recarregar, iguais nas duas: Codigo `f86423cf…`; EditorR53 `c3d31096`, Analise `2ea7e9d4`, Ficha
`6012dcb3`, Invocacoes `ebf20bb1`, Configuracao `bb784c6d`, Origens `90095228`, LotePaleta `848e878b`,
PaletaSegundoPlano `a5a0e83d` e SalarioLote `366f6dd3` sem mudança. Módulo `9dc3480a` sem mudança. Para voltar: versão 11.
Efeito esperado: nas fichas base (sem carteira), a conferência do salário roda uma vez e não volta a cada dia; numa
ficha com carteira emitida, nada muda. Medição na cópia: MEDICAO-DESEMPENHO-2026-10-26-fim.md.
