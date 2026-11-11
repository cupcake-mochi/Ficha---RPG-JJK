# Ofícios, TR e Talentos do jogador · 11/11/2026

Pente fino pedido pelo Mizuki em 11/11 ("passe um pente fino verificando e resolva"). Foram três áreas do
`MAPA-COBERTURA-2026-11-10.md` que ainda não tinham auditoria no jogador: Testes de Resistência, Ofícios, e
Talentos e Aptidões. A referência é o livro R66 (`manual.txt`).

## O que estava certo

- **TR do jogador (AG108:AG111).** A conta segue o livro: TR treinado = atributo + maestria. O Físico usa Força ou
  Destreza, escolhido na criação, e o jogador treina dois TRs. Na QA Era, nível 10, marcar AF108 e AF109 somou +2,
  a maestria do nível.
- **Contagem de ofícios.** As vagas de ofício, a maestria e a especialização (+metade) contam como o livro manda.
- **Talentos e Aptidões.** Os requisitos batem com o R66 e com a tabela das bênçãos: nível, Refino, pré-requisitos,
  atributos, Corpo Amaldiçoado fora da Extensão e Aptidão Própria uma vez só. Na QA Era, Energia Reversa sem os
  requisitos mostrou os avisos e "⚠ 1 de 0". A célula foi reposta.

## O que estava errado (consertado)

1. **Todos os ofícios nasciam em INTELIGÊNCIA.** O livro dá um atributo padrão para cada ofício (capítulo 7, tabela
   de Ofícios). Agora o menu nasce nesse atributo, lido da tabela do `manual.txt`. Mudaram só os oito que não são
   Inteligência:

   | ofício | célula | nasce em |
   |---|---|---|
   | Condução | K108 | DESTREZA |
   | Arrombamento | K109 | DESTREZA |
   | Forja | K111 | FORÇA |
   | Caligrafia | K112 | DESTREZA |
   | Entalhador | X108 | DESTREZA |
   | Alfaiate | X109 | DESTREZA |
   | Jogatina | X111 | ESSÊNCIA |
   | Instrumento | X112 | ESSÊNCIA |

   Herbalismo, Burocracia e Culinária continuam em INTELIGÊNCIA.

2. **Menu vazio ou fora das opções virava #N/A.** É o mesmo defeito da CD e dos ataques (PR100). Os menus dos onze
   ofícios e do TR Físico não são estritos, e o `IFS` não tem caso padrão. A caixa agora diz **Escolha o atributo**,
   na mesma regra da PR100:

   | menu | caixa |
   |---|---|
   | nome aceito, com qualquer caixa ("destreza" passa) | a conta normal |
   | vazio, "FORCA" sem cedilha, outro texto | Escolha o atributo |
   | qualquer valor, com a caixa fixada pela CONFIGURAÇÃO | o valor fixo, sem aviso |

   Os ofícios aceitam os cinco atributos. O TR Físico aceita só FORÇA e DESTREZA, como o menu dele.

## O que mudou no modelo

A geração era `10101178be8ab3cb` e passou a `d0096d09d68df7bb`. Em 280.056 posições, mudaram **20 células**, todas na
FICHA: 12 contas (os onze ofícios e o TR Físico) e 8 menus.

- **Geradores:**
  - `ficha-v01/ficha_automatica.py` lê a tabela de Ofícios do `manual.txt`, confere contra o catálogo e põe o padrão
    no menu de cada ofício.
  - `ficha-v01/configuracao.py` generaliza o `avisa_menu` da PR100. O aviso aceita qualquer lista de nomes, lida do
    `IFS` da própria conta. O `anterior` confere o aviso contra o `IFS` e recusa um aviso adulterado, de dois ou de
    cinco nomes. As quatro caixas da PR100 saíram iguais.
- **Camada:** `preparar_menu_oficios.js`, com o delta em `menu_oficios_delta.json`. A reversão é atômica. A
  instalação recusa um menu que o jogador já trocou: escolha do jogador não é sobrescrita.
- **Comparadores históricos:** a camada vem dentro da do aviso de atributo em `bencaos_imunidades`, `buff_decimal`,
  `buffs_entidades`, `integridade_movimento`, `reserva_bolsa`, `origens_recursos`, `pilha_5156` e
  `vida_bloquear_molde`.
- **Teste:** `r53/testes/menu_oficios.js`, no smoke. Ele confere:
  - o plano e a tabela do livro;
  - o modelo e a reversão;
  - o `anterior` do Python, inclusive com aviso adulterado;
  - os pedidos em pt_BR e en_US, inclusive a recusa do menu já trocado;
  - a tabela da regra.

## Testes quebrados que voltaram ao smoke

- **`vida_bloquear_molde.js`:** a busca do "depois" usava uma aba indefinida, porque as entradas do molde não têm
  aba. Agora usa FICHA quando falta e passa com 20 verificações.
- **`menu_origem.js`:** comparava o modelo inteiro com a base da PR54 (`93a109c`), que nem tem todos os arquivos do
  carregador. Agora confere só CP3 e CQ3 da DADOS_CUSTOM contra as fórmulas ensaiadas no Google. A instalação segue
  coberta pelo `menu_origem_molde.js`.

Os dois entraram no smoke junto com o `menu_oficios.js`. **Smoke completo: 156 OK, saída 0.**

## Instalação nas duas QAs

A instalação usou `findReplace` literal na célula inteira, uma célula por pedido, e o texto procurado é o "antes"
exato. Era e Ciclo deram **20 de 20**.

## Ensaio (entradas repostas depois)

| QA | entrada | resultado |
|---|---|---|
| Era | K108 vazio, X108 "FORCA", AK108 "ESSÊNCIA" | as três caixas: Escolha o atributo |
| Era | K109 "destreza" | 0, sem aviso |
| Era | menus repostos no padrão (K108, K109, X108 DESTREZA; AK108 FORÇA) | linhas 108 e 109 normais |
| Ciclo | K108 vazio | N108: Escolha o atributo; as outras caixas normais |
| Ciclo | K108 reposto em DESTREZA | normal |

## Fora deste conserto

- **Fichas já criadas.** O padrão novo vale para ficha nova. Ficha de jogador antiga guarda o que estava no menu.
- **Oficiais.** Nada foi aplicado nas oficiais. Isso fica para o Mizuki decidir, junto com a mescla da pilha na main.
- **Especialização sem treino (decisão do Mizuki).** Vale para perícias e ofícios. Na QA Era, E109 marcado com D109
  desmarcado deu 3 (maestria 2 + 1), sem gastar vaga de treino. Pelo livro, a especialização só vale em perícia ou
  ofício treinado. Mexer nisso toca umas 34 fórmulas.
- **Texto em caixa numérica (decisão do Mizuki).** Um "x" colado na caixa de Treino ou Especialização (D80), ou
  "dois" escrito no Extra (R81), dá #VALUE! no total da perícia. Os Extras dos ofícios e dos TRs devem fazer o mesmo.
- **Limite dos Talentos (só registro).** O cálculo de "aptidões a mais no teto" supõe a ordem de Refino mais
  favorável, porque a ficha não sabe em que ordem o jogador escolheu.
- **`cartas_custom.js` e `marcas_custom.js`.** Precisam da exportação privada da oficial (`oficial-era.json`), que
  não é versionada. Ficam como teste manual.
