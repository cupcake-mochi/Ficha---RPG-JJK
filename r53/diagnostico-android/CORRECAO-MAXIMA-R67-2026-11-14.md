# Técnica Máxima no livro R67 · 14/11/2026

Fonte: JJK---Project v0.378 (`ed52784`). Pedido do Mizuki em 12/11, com as escolhas dele:
- só a função paga base;
- ficha salva antes da R67 é recalculada, com nota;
- no catálogo, troca só os blocos da Máxima e registra em `ALTERACOES-R66-para-R67.json`;
- "no caso da máxima sem dano, so deixar uma caixa de marcar".

## A regra nova

- **A Forma e a base da função saem dos dados-base.** Os dados-base são 24/28/32 na pessoal e 19/22/26 na domada.
  O preço vem da maior Classe, e 1 ponto vale 1d8.
- **Os pontos de montagem (8/12/16) pagam só as Melhorias.**
- **As bases:**
  - dano: nenhuma;
  - cura: Média;
  - PV temporários individuais: Leve, e cada dado vale 3 PV;
  - PV temporários coletivos: Média mais a Forma.
- **Sem teto de cura.**
- **PV temporários viram uma função da Máxima.** Antes era bloqueado.
- **Sem dano** é o Efeito Próprio principal (até Pesada). Os dados são descartados. Com Melhoria de Controle, ganha o
  reforço: +1 rodada no prazo curto e +2 na CD.

## O que mudou no repositório

Commit `7b645e5`, mais esta rodada.

**Modelo e cartões**
- `r53/modelo.py`: as contas acima.
  - `controle = "Sem dano"` liga o modo sem dano.
  - Os avisos novos: "escolhe uma função", "marque a função" e "a Forma e a base passam dos dados-base".
- `ficha-v01/cartoes_diretos.py`:
  - **Caixa SEM DANO.** Na pessoal fica em T355:T357. Na domada fica na coluna depois de PV TEMP.
  - **PV TEMP.** abre pela porta do Amparo.
  - **Nota das funções** atualizada.
  - **Conta da MONTAGEM (R356)** desta rodada: mostra `pontos − Melhorias N = sobra`. Antes mostrava
    `− base − Forma − peças + devolução`, o que enganava, porque base e Forma não saem mais dos pontos.
- `DADOS_AM!HM38` (o gasto) sem a Forma.

**Catálogo**
- Quatro blocos da Máxima no `BLOCOS-R53.json`, registrados em `referencias-r53/ALTERACOES-R66-para-R67.json`:
  R67-F01 a F04.

**Gerado**
- `apps-script/*.gs`.
- O `EditorR53.gs` muda junto, porque o editor da Classe reescreve a R356.
- Nos outros arquivos só muda o carimbo `geracao`.
- O ruído do Windows foi descartado: PNGs da arte, CRLF e bloco ARTE do `Ficha.gs`.

## Testes

`r53/testes/test_maxima_r67.py` roda no smoke do CI. Tem três partes:

**Tabela do pedido de 14/11**
- Escrita à mão e conferida por uma conta independente do modelo.
- Cobre:
  - as seis faixas (pessoal e domada, níveis 17/21/26);
  - as cinco Formas;
  - dano, cura e PV temporários;
  - sem dano com reforço;
  - Guarda;
  - Fenda de Arrasto;
  - nove avisos.
- Onze defeitos plantados, um por número ou regra nova. Todos acendem.

**Conta da MONTAGEM** (nova nesta rodada)
- A R356 gerada no `R53Cartoes1.gs` precisa ter `− Melhorias` e não pode ter base, Forma ou devolução.
- O `EditorR53.gs` precisa reescrever a mesma fórmula.
- Defeito plantado: a conta antiga, que acende.

**`r53/testes/casos.json`**
- Sete casos R67.

**`r53/testes/pratica_cotidiana.js`** (estava quebrado desde o `7b645e5`)
- **Hash dos contextos do editor.** Foi atualizado. A diferença foi conferida campo a campo contra a base `f474691`.
  Só mudaram os contextos da Máxima: o 44 (pessoal) e os 12 das domadas (204 a 248, de 4 em 4). Mudaram a caixa
  SEM DANO, a porta do PV TEMP. e as fórmulas N/T (ou L/M, AE/AF) e R356.
- **Plano congelado da Prática Cotidiana.** O `pratica_cotidiana_plano.json` guarda as fórmulas das linhas 252 e
  253 de DADOS_R53 de antes da R67. Catorze células delas mudaram com a R67: CV, DA, DB, DG, DH, DI e FH.
  - Essas linhas são cartões de Classe 0, com o D fixo. Por isso BB (é Máxima) é sempre FALSE nelas.
  - O teste agora confere que, com BB falso, a fórmula nova é igual à congelada. Também confere que o D da linha é
    "Classe 0".
  - Defeito plantado: mudar a conta fora do ramo da Máxima acende.
  - As outras células do plano continuam com a comparação literal.
- Resultado: 1.021 verificações, OK.

## QAs (Ciclo e Era)

Aplicado pela API nas duas, validado e reposto. Nenhuma QA ficou com a R67.

**DADOS_R53**
- 40 localizar-e-substituir por regex nas colunas J, O, CV, DA, DB, DG, DH, DI, FH e FX.
- Entrada: o número da própria linha virou o grupo `$1`.
- Contagens:
  - 26 trocas em uma célula cada;
  - 14 trocas em 251 células cada.
- A coluna de avisos (FX) só passa em faixas de cerca de 40 linhas. Em lote maior, o Google responde "service
  unavailable".

**Cartões**
- Pessoal e as 12 domadas.
- O gasto (`DADOS_AM!HM38`).
- A conta R356.

**Conferido no Ciclo**, todos os casos da tabela batem:
- pessoal nas faixas 17/21/26;
- cura;
- PV temporários individuais e coletivos;
- sem dano com reforço;
- avisos;
- domada.

**Conferido na Era**, conferência rápida no nível 17, Classe 5, Projétil:

| caso | cartão | esperado |
|---|---|---|
| dano | 24d8; conta "8 − Melhorias 0 = 8 pontos" | 24 − 0 |
| cura | 19d8 | 24 − Média 5 |
| PV temp. individual | 63 PV | 3 × (24 − Leve 3) |
| sem dano | "Efeito", modo "Sem dano", dados descartados | — |
| domada, dano | 19d8 | dados-base da domada |

**Volta**
- As entradas de teste foram repostas antes.
- A volta usou os pedidos inversos, também conferidos pela contagem.
- Os cartões e o HM38 voltaram à foto tirada antes de mexer.
- Na Era, os cartões foram relidos e estão iguais à foto.
- No Ciclo, as caixas CURA das domadas estavam vazias, não FALSE. Foram postas em FALSE, como o gerador escreve.

## O que não foi feito ou testado

- **Oficiais:** nada.
- **`construir()`:** não rodou em lugar nenhum.
- **EditorR53 das QAs:** é o código antigo e não foi trocado. Por isso:
  - o clique à mão nas caixas (PV TEMP. e SEM DANO) não foi testado com o onEdit;
  - a escrita pela API não dispara o onEdit;
  - trocar de Classe numa QA reescreveria a R356 com a conta antiga.

  Entra com o pacote, na rodada das oficiais.
- **`PraticaCotidiana.gs` nas oficiais:** quando repõe as linhas 252 e 253, ele escreve as fórmulas de antes da R67
  nessas 14 células. O número não muda, porque ali BB é sempre FALSE. Fica registrado para não estranhar a
  diferença de texto.
- **Ponto do livro para o Mizuki decidir:** a linha 9975 do v0.378 diz que a Técnica Máxima não recebe reforço, e
  a R67-08 dá o reforço à Máxima sem dano. A ficha segue a R67-08.
