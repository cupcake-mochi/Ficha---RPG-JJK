# Ficha digital do Projeto M · leia isto primeiro

Este pacote continua o trabalho da conversa anterior. **Nada foi recomeçado do zero, e nenhum arquivo dos seus repositórios foi editado.**

O que mudou nesta rodada: a ficha **ganhou identidade**. Ela deixou de ser planilha organizada e virou o documento oficial do feiticeiro — carteira com foto e selo, régua no lugar de caixa, arte desenhada por código, e cinco fontes com papéis separados.

**Para subir isso e virar uma planilha de verdade: [`COMO-SUBIR.md`](COMO-SUBIR.md).**

---

## Por onde começar

1. **`DECISOES-bloco-A.md`** — as nove decisões (bloco A e bloco C), com o porquê e o que foi medido. É o dono delas.
2. **`COMO-SUBIR.md`** — do repositório até a ficha na mão do jogador, em seis passos.
3. **`ficha-v01/ficha-projeto-m-0.1.xlsx`** — a ficha, sete abas: `CARTEIRA`, `FICHA`, `FICHA AMALDIÇOADA`, `FICHA PESSOAL` e `GLOSSÁRIO`, e a `DADOS` e a `DADOS_AM`, escondidas. A `FICHA AMALDIÇOADA` entrou em 01/10/2026 (`ficha-v01/ficha_amaldicoada.py`, B29 do `PENDENCIAS.md`), e desde 02/10/2026 muda conforme a Origem da `FICHA`, nas quatro rotas de criação; a seção 8 da `FICHA` virou o menu rápido, que mostra o que está nela (`ficha-v01/menu_rapido.py`, B32), e a seção 7 virou as Habilidades, cartas de Caminho e de Trilha escritas pelo jogador (`ficha-v01/habilidades.py`, B34). A `INVOCAÇÃO`, o `CATÁLOGO` e a `DADOS_INV` saíram em 01/10/2026 (`ficha-v01/sem_invocacao.py`), até a invocação ser refeita. É a cópia da planilha viva: o `ficha-v01/extrair.py` tira o desenho da exportação, e o `ficha-v01/monta.py` remonta a ficha e escreve o `Ficha.gs`. *O `ficha/monta.py` foi aposentado no B18.*
4. **`apps-script/Codigo.gs`** — o que o `.xlsx` não carrega: caixa de seleção, cor de estado, proteção, e a entrada por delta.
5. **`manual-temporario.md`** — **superado.** *A regra entrou no capítulo 1 do manual, com texto próprio; o arquivo fica pelo exemplo que o `regressao-delta.js` confere.*
6. **`PENDENCIAS.md`** — o bloco A saiu e virou ponteiro. Entraram cinco itens novos, do B5 ao B9.

O `DESIGN-ficha-digital.md` e o `ESPECIFICACAO-ficha-digital.md` continuam valendo. O desenho ganhou uma linha de "decidido" em cada seção que tinha pergunta aberta, e duas correções de fato na parte do script.

---

## Rodar os validadores

```bash
./rodar-tudo.sh
```

São vinte e um. Dezoito passam em qualquer máquina; o
`regressao-kaori-na-ficha.py`, o `regressao-ficha-pessoal.py` e o `regressao-amaldicoada.py` precisam de um LibreOffice **com o filtro do
Calc** para recalcular a ficha, e onde ele não existe essa checagem falha alto
em vez de passar em branco — é de propósito. O `regressao-delta.js` roda no
node, porque o Apps Script não pode ser testado de fora; sem node ele é pulado
com aviso, também não em silêncio.

Para regerar a ficha da invocação:

```bash
python3 ficha-invocacao/monta.py
```

Para regerar a ficha, com a planilha exportada em `ficha-v01/original.xlsx`:

```bash
python3 ficha-v01/extrair.py
python3 ficha-v01/monta.py
``` O script devolve 1 se algum falhar, e não esconde saída de ninguém.

| validador | o que confere |
|---|---|
| `conferir-catalogo.py` | integridade referencial e as contagens que o manual declara |
| `conferir-kaori.py` | os onze números derivados, contra a ficha de exemplo |
| `conferir-progressao.py` | as cinco colunas de progressão, nos trinta níveis, com contra-teste |
| `regressao-exemplos.py` | os dois feitiços publicados na p.137 |
| `arnes.py` | prova que cada checagem de feitiço acende — **e as duas novas do A3** |
| `revisao-cetica.py` | a especificação contra o manual |
| **`conferir-decisoes.py`** | **novo.** As cinco decisões contra o manual, o catálogo e os outros documentos |
| `arnes-decisoes.py` | perturba as decisões numa cópia isolada e prova que o validador acende |
| **`conferir-ficha-xlsx.py`** | **novo.** Lê o `.xlsx` gerado: fonte, cor, largura, e se cada fórmula puxa o atributo certo |
| `regressao-ficha-pessoal.py` | **01/10/2026.** Preenche vinte casos na `FICHA PESSOAL`, recalcula no LibreOffice e compara com a regra do catálogo; a nota da arma em uso é comparada com o texto lido do livro |
| `regressao-pessoal.js` | **01/10/2026.** O que o `Codigo.gs` faz pela `FICHA PESSOAL`, num Sheets de mentira |
| `regressao-construir.js` | **01/10/2026.** Roda o `construir()` inteiro num Sheets de mentira rigoroso, e depois usa a planilha montada pelo `onEdit`. Desde o B32, o menu rápido da `FICHA`: as fileiras copiadas chegam mescladas, e escrever por cima devolve a conta |
| `arnes-pessoal.py` | **01/10/2026.** Planta cinquenta e um defeitos no script e no molde (os dois do B34 são o riscado das Habilidades e a etiqueta que volta; os três do B35, a caixa da paleta ancorada fora da foto), numa cópia, e confere que cada um acende. Os quatro do B31 são a conta que volta quando alguém digita por cima de uma caixa calculada da `FICHA AMALDIÇOADA` |
| `regressao-amaldicoada.py` | **01/10/2026.** Preenche dezesseis fichas na `FICHA AMALDIÇOADA` gerada, recalcula no LibreOffice e compara com a regra escrita de novo: os 33 feitiços prontos do livro, 429 cartas (as sorteadas e uma ficha de casos de borda) e o resto da aba. Desde o B31, também o desenho que ele pediu: o título de ponta a ponta, o respiro, o nome no acento, a inicial maiúscula em toda caixa e toda caixa calculada apontando para a `DADOS_AM`. Desde o B32, as quatro rotas (uma ficha para cada) e o menu rápido da `FICHA` em toda ficha: a lista sem buraco, o "Como é", o texto do jogador ou o do livro, os nomes da rota. Depois monta a planilha no Sheets de mentira e confere que a aba chega igual |
| `arnes-amaldicoada.py` | **01/10/2026.** Não mora no `rodar-tudo.sh`, e **roda à mão** (meia hora): planta sessenta defeitos na conta, no desenho e na montagem da `FICHA AMALDIÇOADA`, nas rotas (35 a 46), no menu rápido (48 a 57) e nas Habilidades (58 a 60), numa cópia, e confere que cada um acende. Aceita os números das perturbações (`python3 arnes-amaldicoada.py 16 17 18`) para rodar só as que mudaram |
| `arnes-ficha-pessoal.py` | **01/10/2026.** Não mora no `rodar-tudo.sh`, e **roda à mão** (perto de uma hora: cada rodada gera a ficha e recalcula 22 planilhas): planta treze defeitos no aviso embaixo da mão e na nota das propriedades da arma da `FICHA PESSOAL`, numa cópia, e confere que cada um acende no `regressao-ficha-pessoal.py` |
| `ficha-v01/extrair_tecnica.py` | **01/10/2026.** Não é validador: lê dos capítulos do livro o que a `FICHA AMALDIÇOADA` calcula e o catálogo ainda não tem, e grava o `ficha-v01/tecnica-do-livro.json`. Com `--confere`, só compara |
| `ficha-v01/extrair_equipamento.py` | **01/10/2026.** Não é validador: lê do capítulo de Equipamento do livro o que cada propriedade de arma faz, que o catálogo não traz, e grava o `ficha-v01/equipamento-do-livro.json`. A `FICHA PESSOAL` usa na nota da arma em uso. Com `--confere`, só compara |
| `medidas/sheets-de-mentira.js` | **01/10/2026.** Não é validador: é o Sheets de mentira que o `regressao-construir.js` usa. Guarda tudo o que o `construir()` grava, e acusa a fórmula gravada antes de a aba citada existir ou com a planilha fora do inglês |
| `medidas/comparar-construir.js` | **01/10/2026.** Não é validador, e **roda à mão**: monta a planilha com o script de um commit e com o da pasta, e compara célula a célula. É a prova de que mexer no `construir()` não mudou a planilha |
| `arnes-paleta.py` | **01/10/2026.** Planta onze defeitos na troca de paleta (a barra, a tinta de enfeite, a cor da arte, desde o B31 a cor de aviso acesa que a troca gravava na célula, desde o B32 a aba grande pintada em trechos, e desde o B35 o canto da moldura da foto fora da régua exata), numa cópia. **Roda à mão**, fora do `rodar-tudo.sh`: são uns dois minutos |
| `arnes-moldura.py` | **03/10/2026.** Não mora no `rodar-tudo.sh`, e **roda à mão** (uns quinze minutos, sem LibreOffice): planta nove defeitos na moldura da foto da `CARTEIRA` (B35: a moldura que fica dentro da caixa, a quina sem canto, a reta que falta ou que entra na quina, a caixa sem o convite ou sem a nota, a caixa não declarada, o canto fora da régua no nascimento ou na troca), numa cópia, gera a ficha e confere que o `conferir-ficha-xlsx.py` acusa cada um |
| `medidas/pintar-paletas.js` e `medidas/ver-paletas.py` | **01/10/2026.** Não são validadores: pintam a ficha com cada uma das 122 paletas, pelo `Codigo.gs` de verdade, e desenham o resultado para olhar tema por tema |
| **`regressao-kaori-na-ficha.py`** | **novo.** Preenche a Kaori na ficha, manda o LibreOffice recalcular, e compara com a p.41. Desde o B32 confere só o que ficou na `FICHA`; o refino, as aptidões e o Leque são da `regressao-amaldicoada.py` |
| **`conferir-invocacao.py`** | **novo.** O `invocacao.json` contra os capítulos 16 e 35 vendorizados, e a planilha contra o JSON |
| **`regressao-invocacao.py`** | **novo.** Recalcula a ficha da invocação e bate com os números que o capítulo 16 publica |
| **`arnes-invocacao.py`** | **novo.** Perturba o `invocacao.json` numa cópia isolada e prova que a checagem certa acende |

### Dois arquivos que os validadores leem de fora

O zip já traz os dois, então `./rodar-tudo.sh` funciona assim que você descompactar.

| arquivo | de onde veio |
|---|---|
| `manual.txt` | o seu próprio PDF, extraído com `pdftotext -layout` — o de hoje saiu do livro da **v0.263** do sistema |
| `repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx` | cópia do seu repositório público, só esse arquivo |

Os dois são derivados de material seu. Se for subir isto para o GitHub e preferir não duplicar, pode apagar os dois — o `conferir-decisoes.py` **falha e diz como regerar**, em vez de pular em silêncio. Um verde que pulou checagem não prova nada.

---

## O que é dado e o que é prosa

O `decisoes-ficha.json` é o dono dos **valores** das cinco decisões: o script, o validador e a ficha leem de lá. O `DECISOES-bloco-A.md` é o dono do **porquê**.

Nenhum dos dois repete número do outro documento, e o `conferir-decisoes.py` confere que eles continuam de acordo. Isso é a lição nº 9 do seu projeto aplicada aqui: um número que mora em dois documentos vai divergir.

---

## O que ficou pendente na sua mão

- ~~**Colar o texto do `manual-temporario.md`**~~ **feito no sistema, com texto próprio**, e o `Braseiro` foi enxugado.
- ~~**A checagem 7 das Famílias**~~ **feita na v0.239 do sistema**, como bloco 8 do `conferir-ficha.py`, e a ficha em branco foi regerada.
- **Reconstruir a planilha com o `Ficha.gs` novo e colar o `Codigo.gs` novo.** A FICHA de 17/09/2026 conta sozinha (B22) e traz o desenho que a mesa pediu (B23), e o índice da `DADOS` passou a andar quando a planilha muda de forma: o passo a passo está no `COMO-SUBIR.md`, na planilha central.
- **Escolher o segundo caso de teste** (item B2): uma ficha de nível 15 ou mais, com Famílias Livres que a Kaori não usa.
