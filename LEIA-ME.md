# Ficha digital do Projeto M · leia isto primeiro

Este pacote continua o trabalho da conversa anterior. **Nada foi recomeçado do zero, e nenhum arquivo dos seus repositórios foi editado.**

O que mudou nesta rodada: a ficha **ganhou identidade**. Ela deixou de ser planilha organizada e virou o documento oficial do feiticeiro — carteira com foto e selo, régua no lugar de caixa, arte desenhada por código, e cinco fontes com papéis separados.

**Para subir isso e virar uma planilha de verdade: [`COMO-SUBIR.md`](COMO-SUBIR.md).**

---

## Por onde começar

1. **`DECISOES-bloco-A.md`** — as nove decisões (bloco A e bloco C), com o porquê e o que foi medido. É o dono delas.
2. **`COMO-SUBIR.md`** — do repositório até a ficha na mão do jogador, em seis passos.
3. **`ficha/ficha-projeto-m.xlsx`** — a ficha, seis abas. Gerada por `ficha/monta.py`; não edite o `.xlsx` na mão, edite o gerador.
4. **`apps-script/Codigo.gs`** — o que o `.xlsx` não carrega: caixa de seleção, cor de estado, proteção, e a entrada por delta.
5. **`manual-temporario.md`** — o texto pronto para colar no manual, decisão A2b. **Só você aplica isso**; eu não mexo no repositório.
6. **`PENDENCIAS.md`** — o bloco A saiu e virou ponteiro. Entraram cinco itens novos, do B5 ao B9.

O `DESIGN-ficha-digital.md` e o `ESPECIFICACAO-ficha-digital.md` continuam valendo. O desenho ganhou uma linha de "decidido" em cada seção que tinha pergunta aberta, e duas correções de fato na parte do script.

---

## Rodar os validadores

```bash
./rodar-tudo.sh
```

São dez, e os dez passam.

Para regerar a ficha:

```bash
python3 ficha/monta.py
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
| **`regressao-kaori-na-ficha.py`** | **novo.** Preenche a Kaori na ficha, manda o LibreOffice recalcular, e compara com a p.41 |

### Dois arquivos que os validadores leem de fora

O zip já traz os dois, então `./rodar-tudo.sh` funciona assim que você descompactar.

| arquivo | de onde veio |
|---|---|
| `manual.txt` | o seu próprio PDF, extraído com `pdftotext -layout` |
| `repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx` | cópia do seu repositório público, só esse arquivo |

Os dois são derivados de material seu. Se for subir isto para o GitHub e preferir não duplicar, pode apagar os dois — o `conferir-decisoes.py` **falha e diz como regerar**, em vez de pular em silêncio. Um verde que pulou checagem não prova nada.

---

## O que é dado e o que é prosa

O `decisoes-ficha.json` é o dono dos **valores** das cinco decisões: o script, o validador e a ficha leem de lá. O `DECISOES-bloco-A.md` é o dono do **porquê**.

Nenhum dos dois repete número do outro documento, e o `conferir-decisoes.py` confere que eles continuam de acordo. Isso é a lição nº 9 do seu projeto aplicada aqui: um número que mora em dois documentos vai divergir.

---

## O que ficou pendente na sua mão

- **Colar o texto do `manual-temporario.md`** no capítulo da p.15, e enxugar a entrada do `Braseiro` (a instrução está lá).
- **A checagem 7 das Famílias** (`repo-conserto/checagem-7-familias.py`), que conserta um erro que hoje está na ficha em branco que os seus jogadores usam. Independente de tudo isto, e vale sozinha.
- **Escolher o segundo caso de teste** (item B2): uma ficha de nível 15 ou mais, com Famílias Livres que a Kaori não usa.
