# Caminhos, Trilhas e a ficha contra o R66 · 11/11/2026

Parte do pente fino de 11/11. O `MAPA-COBERTURA-2026-11-10.md` marcava Caminhos e Trilhas como "Parcial", sem
auditoria contra o livro.

## O livro de cada lado

- **Ficha:** o `manual.txt` do repositório é o **R53** (`b7eaa00`, 19/10). Dele saem o `catalogo-projeto-m.json`,
  o `ficha-v01/habilidades-do-livro.json` e o texto das cartas no `Habilidades.gs`.
- **Livro atual:** **R66**, `cupcake-mochi/JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, arquivo
  `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`.

**Como foi feito.** O `extrair-manual.py` gerou um manual do R66 numa cópia descartável, fora do repositório. Os
conferidores da ficha rodaram contra essa cópia: `conferir-catalogo.py` e `extrair_habilidades.py`. Em seguida,
os registros de alteração do livro (`revisao-de-regras/alteracoes/R53-para-R54.json` até `R65-para-R66.json`)
separaram o que é regra do que é redação.

## Mudança de regra entre o R53 e o R66

| versão | o que mudou | ficha |
|---|---|---|
| R60 | um feitiço de Classe 1+ por turno; a Reação fora do turno não entra no limite | texto já na ficha (`r53/textos_revisados.py`, Melhoria Reação) |
| R61 | os custos da Reação cancelada pelo Ataque sem Prenúncio não voltam | texto já na ficha (Origens e Custom) |
| **R66** | **cinco habilidades passam de "uma vez por combate" para "uma vez por cena"** | **a ficha ainda diz "por combate"** |

As cinco do R66 (registros R66-05 a R66-12):

| habilidade | Caminho ou Trilha | nível |
|---|---|---|
| Especial Combinada | Evocador | 30 |
| Resposta Técnica da Dupla | Parceria | 27 |
| Um Passo à Frente | Incursor | 30 |
| Sentença Final | Assassino | 27 |
| Trajetória Perfeita | Malabarista | 27 |

O livro R66 não tem mais nenhum "por combate". O `Habilidades.gs` tem seis, e o `habilidades-do-livro.json` tem
cinco.

O resto do R54 ao R66 é declarado **sem mudança de regra**:
- R54 a R57: `altera_regras: false` em todos os itens;
- R58 e R59: revisão didática;
- R62 a R65: linguagem simples;
- R66: clareza e diagramação, fora os cinco acima.

## O que bate com o R66

- **Características dos seis Caminhos:** vida inicial, vida por nível, PE por nível, perícias fixas, armas e troca
  de perícia por arma. São os números do catálogo.
- **As 18 Trilhas:** nome, Caminho e níveis (Caminho 2/7/15/23/30, Trilha 2/11/19/27).
- **As 111 habilidades:** os mesmos nomes e níveis.
  - Em 79 o texto mudou. Os números somem só onde o extrator do R53 se perde nos títulos novos. Exemplos:
    - Batedor · Arma de Fogo, nível 2: a carta corta no primeiro parágrafo;
    - Evocador: o exemplo dos 4 PE passou para a carta do nível 15.
  - Nos dois exemplos, as frases estão inteiras no R66 (Queima-Roupa, o exemplo dos 4 PE e Obras maiores).
- **Progressão:** marcos, Liberação Máxima, Integridade, maestria, espaços, níveis de Caminho e Trilha, e o feito
  do Limiar do nível 20. A regra é a mesma, com outra redação.
- **Especialização** e o marco de Corpo (PRs #101 a #103): o texto é idêntico no R53 e no R66.

## O que só mudou de redação

O `conferir-catalogo.py` contra o R66 dá 13 falhas. Fora os atributos naturais, todas são frase reescrita, com a
mesma regra:
- "saldo" virou "pontos que sobram";
- "ponto reservado" virou "ponto destinado";
- "conforme" virou "de acordo com";
- e os textos de marcantes, Melhorias e Restrições.

**Atributos naturais.** O R58 tirou a linha "Atributos naturais" das Características dos seis Caminhos, numa revisão
didática sem mudança de regra. No R53 ela não mexia em conta nenhuma, só sugeria. A ficha ainda mostra esses
atributos na tabela de Caminhos (`DADOS`, `custom_progressao.py`, `ANALISE`).

## Decisões do Mizuki

1. ~~Corrigir as cinco cartas para "uma vez por cena" (regra do R66).~~ Feito em 12/11
   (`CORRECAO-FREQUENCIA-CENA-2026-11-12.md`).
2. Atualizar todo o texto da ficha para a redação do R66. Isso pede:
   - manual.txt novo;
   - o extrator ajustado aos títulos do R66;
   - catálogo e cartas regerados.
   É só redação, mas mexe em muitos arquivos.
3. Manter ou tirar os atributos naturais da ficha.

Nada foi alterado na ficha, nas QAs nem nas oficiais por esta auditoria.
