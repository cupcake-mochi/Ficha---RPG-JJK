# Handoff — sessão de invocações, ficha e escada

**Escrito em 06/09/2026, no fim de uma sessão longa.** Ela ficou longa porque
misturou três repositórios e cinco assuntos, e porque eu errei número várias
vezes e o Mizuki pegou todas. **Os erros estão listados no fim, e ler eles
primeiro economiza repetir.**

---

## 1. Onde cada coisa está

### `Ficha---RPG-JJK` — branch `claude/system-invocations-help-034pp2`

**Tudo commitado e empurrado.** Último commit: `fb410e4`.

| o que | estado |
|---|---|
| ficha da invocação, gerador em `ficha-invocacao/` | **fechada.** 202 conferências, 135 de regressão, 30 perturbações |
| coluna `DEGRAU` para Traço e Comando próprios | **no gerador**, e aplicada na planilha viva |
| caixinha de ± consumindo a vida temporária (`apps-script/Codigo.gs`) | **fechada e conferida na planilha** |
| `regressao-delta.js` + `arnes-delta.py` | 20 checagens e 12 perturbações, verdes |

**Quatro `.gs` para rodar na planilha do Sheets**, em `ficha-invocacao/`:

1. `migra-degrau.gs` — abre a coluna DEGRAU. **JÁ RODOU.**
2. `corrige-menus.gs` — religa os nove menus à `DADOS_INV`. Os dois grandes o
   Mizuki já consertou à mão; os outros sete seguem como lista literal, com
   `Z43` guardando `Intêligencia` escrito errado.
3. `tira-triangulo.gs` — tira o menu do nome (e o triângulo com ele), põe o
   aviso âmbar, e faz a vida agora nascer cheia. **JÁ RODOU, e o aviso saiu com
   `#ERROR!`.**
4. `conserta-aviso.gs` — **PENDENTE, é o próximo passo.** Conserta o `#ERROR!`.

### `JJK---Project` — 23 arquivos modificados, **NADA COMMITADO**

Base: `73bd969`, a v0.215. Eu escrevi a entrada da **v0.216** no topo do
`CHANGELOG` e subi a versão no README, no `ESTADO-ATUAL` e no `LEIA-ME`.

**O que está escrito e conferido:**

- **A escada de dificuldade virou `10 · 12 · 16 · 20 · 26`.** Fácil sai de 55%
  para 65% no nível 2. As pontas não andaram, porque a peça declara duas
  propriedades sobre elas.
- **A seção 8 do `conferir-pericias.py` virou checagem.** Ela tinha os cinco
  degraus escritos no código e só imprimia uma tabela. Agora lê da peça 4 §2 e
  confere as quinze porcentagens, as duas propriedades e as três cópias.
- **O ofício passou do Caminho para a Origem**, dois, livres, com gancho de
  lore nas sete Origens. A guarda do §12 do `conferir-legados.py` virou de lado
  e o extrator do `conferir-criacao.py` passou a ler o DONO separado da
  CONTAGEM.
- **Seis cópias que já estavam atrasadas antes disso** foram acertadas.
- **PDF, PDF de duas colunas, DOCX e TEXTO regerados** e conferidos por
  extração de texto.

**Estado dos validadores:** os 26 de mecânica passam com PULADAS 0. O
`conferir-repositorio.py` falha nos dois problemas do `finalizado/livro/`, que
**existem desde antes** — provado com `git stash`, a saída é idêntica com e sem
as minhas mudanças.

---

## 2. O que ficou no meio do caminho

### A régua da morte — decidida, medida, NÃO escrita

**A decisão do Mizuki, e ela está validada contra o bestiário:**

> **A régua da morte é a vida máxima daquele corpo.**
> **Morre de vez se um único golpe causar a régua inteira, ou se o excedente
> passar de metade da régua.**

*Motivo dele, e vale escrever junto:* a régua mede um golpe único, então um
golpe que apaga um corpo de vida cheia destruiu esse corpo. Régua maior que a
vida criava golpe que mata o corpo inteiro e ainda conta como "só caiu".

**O que ela faz na mesa**, com dano da peça 26 (`Ronda`/`Dupla`/`Alcateia`/
`Calamidade`, dano por rodada dividido pelas ações):

| CON | corpo cru | corpo forte |
|---|---|---|
| 0 | destruído por dano MÉDIO de `Dupla`, `Alcateia`, `Calamidade` | só no crítico |
| **3** | **só no crítico** | **só no crítico** |
| 6 | só no crítico de `Dupla` | nada destrói com golpe único |

**O corpo forte NÃO muda.** Ele vale `1,11×` a `1,27×` a vida do dono, que é o
"só um pouco a mais" que o Mizuki pediu.

**Uma coisa que a regra obriga a declarar:** com Constituição `0` o corpo cru
passa a ser destruído de vez por golpe comum. É inevitável se a régua é a vida,
e é coerente com o CON 0 já deixar o Evocador aguentando `1,1` golpe. **O
Mizuki não respondeu se quer uma trava para isso** — foi a última coisa que eu
perguntei e a conversa virou.

**Os seis passos, na ordem, e o primeiro destrava o resto:**

1. **Recalibrar a tabela de golpes do §3.5 da peça 15 contra o bestiário.** Ela
   é da v0.58, mede em unidades de `R = 5 × a vida crua`, e **superestima o dano
   real em 1,4× a 1,5×** em todo nível. O `conferir-invocacoes.py` §12 deriva
   uma JANELA dessa tabela e confere se a régua cai nela — então trocar a regra
   sem recalibrar faz a checagem medir contra uma escala que não existe.
2. A regra nova na **peça 15**, no §3.5 e no resumo da Q2 (linha 108).
3. O **capítulo 60 do livro**, cinco lugares: a ficha da `Carranca` (régua vira
   `55`, não `165`), a tabela das três Trilhas, o §"erros comuns" que hoje diz
   *"não ler a régua na linha da vida"* e passa a dizer o contrário, e o bloco
   da regra. *O exemplo do Kaito sobrevive sem reescrita — conferi: régua 32,
   metade 16, excedente 14, e ele continua "só caindo".*
4. **`conferir-invocacoes.py`** §12 — a janela muda de eixo, de múltiplo de `R`
   para múltiplo da vida do corpo.
5. **Re-vendorizar** o capítulo para `Ficha---RPG-JJK` (o de lá está atrás: o
   capítulo 60 ganhou a seção *"Montar uma invocação"* e mudou o texto do
   `Miúdo`/`Graúdo` depois da v0.205). Daí o `invocacao.json`
   (`morte.formula_regua`, `multiplicador_regua`, `exemplo_do_capitulo`), os
   três validadores e o `ficha-invocacao/constroi.py` (`D65`, `O65`, `Z65`).
6. **Regerar o PDF** — `sistema/05-material/livro/build/`, precisa de
   `markdown`, `beautifulsoup4` e `weasyprint`.

### Achados registrados, sem conserto

- **`PENDENCIAS.md` B17** — o campo `TEMP` da INTEGRIDADE não tem fonte no
  manual. Seis fontes de vida temporária, uma de energia, zero de integridade.
- **`PENDENCIAS.md` B18** — o `Ficha.gs` está atrás da planilha viva, e o
  `construir()` apaga todas as abas. **Arma carregada no editor.**
- **A cláusula do excedente era código morto no corpo forte** com a régua
  antiga: `vida + metade da régua` = `5 × crua` = a régua inteira. Ela só fazia
  efeito no Coro, e o efeito era matar o Coro mais fácil. Com a régua nova ela
  passa a valer abaixo de metade da vida, nos dois corpos.

---

## 3. Os erros que eu cometi, para não repetir

**Todos foram pegos pelo Mizuki, e a maioria por instinto de mesa contra a
minha aritmética.**

| eu disse | o certo | a lição |
|---|---|---|
| a barra de vida da invocação precisava de trilho em dois segmentos | o SPARKLINE não pinta o fundo, então o fundo da célula JÁ é o trilho | revertido; não invente conserto sem olhar o que o render faz |
| a barra ficava em branco com a vida agora vazia | ela desenhava **cheia** e mentia | o print do usuário vale mais que o meu modelo |
| "um acerto comum destrói qualquer invocação" | a tabela em `R` da peça 15 é da v0.58 e superestima 1,4× a 1,5× | **número de peça velha não é medida:** cruze com o bestiário |
| "a invocação tem 62 de vida no nv30" | era CON 0, o piso; com CON 3 são 152 | não chame o pior caso de típico |
| "o Servo tem 380 de vida com CON 3" | **245** — a Constituição fica FORA do multiplicador desde a v0.178 | leia a fórmula do json, não a que você lembra |
| `setFormula` converte o separador de vírgula para ponto e vírgula | **não converte.** O `Ficha.gs` já registra: *"Eu supus duas vezes que o setFormula resolvia isso sozinho, e duas vezes estava errado"* | eu supus a terceira. Use `separador_` e `paraLocal_` |
| a peça 9 dava um ofício livre à Origem | a v0.206 tirou; eu li o clone parado na v0.205 | **confira a versão do clone antes de ler regra** |

**E a de processo:** eu trabalhei dez versões atrasado sem perceber. O clone
estava na v0.205 e o repositório na v0.215. **Rode `git fetch` e compare o
`CHANGELOG` antes de ler qualquer peça.**

---

## 4. Restrições da sessão que continuam valendo

- **O commit é sempre do Mizuki.** Eu leio, edito e valido.
- O `subir.sh` vai recusar enquanto o `conferir-repositorio.py` estiver vermelho
  pelos dois problemas do `finalizado/livro/`.
- **Não rodar `construir()` do `Ficha.gs`** — ver B18.
