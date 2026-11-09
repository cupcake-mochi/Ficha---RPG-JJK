# Treinos e limites das entidades · 09/11/2026

Recorte que o parecer da PR90 deixou como próximo: perícias e treinos
das entidades, seus limites e buffs. Referência: manual de invocações
no commit `e3058ad` do JJK---Project (`60-invocacoes.md`, igual ao da
`bbc4428`, última mudança do arquivo). Só parecer, nenhuma fórmula mudou.

## A regra

- **TR.** "A entidade tem um Teste de Resistência treinado; nos outros,
  a maestria não entra." Físico usa Força ou Destreza, escolhida na
  criação; Vigor, Constituição; Intelecto, Inteligência; Espírito,
  Essência. Treinado: d20 + atributo + sua maestria.
- **Perícias.** Treina `4 + metade da Inteligência da entidade`,
  arredondada para baixo. Treinada soma atributo e maestria; as demais,
  só o atributo. Ofício só com permissão expressa.
- **Nível e maestria.** O que depende de nível usa o da entidade; a
  maestria é a sua.

## O que bate

| ponto | fórmula | conclusão |
|---|---|---|
| bônus de perícia | `d_pb = total do atributo da perícia + maestria` | certo; toda perícia listada é treinada |
| TR | `tr = atributo + maestria se for o treinado + Buff/Debuff de TR` | certo |
| Físico | `vf = Destreza se escolhida, senão Força` | certo |
| perícia repetida, fora do catálogo, acima do limite | erro no resumo `d_per` | coberto, inclusive para valor colado |
| ofício | menu de perícias usa só o catálogo de perícias; ofício é campo à parte, só na entidade de criação | certo |

## Achados

**1. TR treinado em branco ou inválido não acusa nada.** O manual diz que
a entidade *tem* um TR treinado. Na ficha, `trT` só entra na conta dos
quatro TR e no menu (`ficha_invocacoes.py:529` e `:1184`); nenhum resumo
ou título olha para ele. Com o campo vazio, nenhum TR recebe a maestria,
em silêncio. O menu é estrito, mas a colagem passa por cima dele (ver
`REVISAO-PONTOS-FORCADOS-2026-11-09.md`), então um texto que não é nome de
teste também zera a maestria sem aviso. Conclusão tirada do código; não
ensaiei em entidade nomeada no Sheets.

*Correção possível:* aviso ou erro no rótulo dos TR quando a entidade tem
nome e `trT` não é um dos quatro testes. Mesmo padrão das PRs 92–94: não
reescreve a entrada.

**2. A quantidade de perícias usa os pontos de Inteligência, não o
total.** `nper = 4 + INT(p3 / 2)`, onde `p3` são os pontos distribuídos.
O total `t3` soma o Buff/Debuff de INT. O manual fala em "metade da
Inteligência da entidade", que pode ser lida como o total. Na prática:
um Buff de +2 em INT não abre uma perícia a mais, e um Debuff não fecha.
É uma escolha defensável (buff temporário não daria treino permanente),
mas é decisão de regra, não bug. Fica para o Mizuki.

## Fora do recorte

Pontos fora de 0–6 já corrigidos na PR94. Buff/Debuff decimal e a
divergência com a ficha do jogador estão no `PENDENCIAS.md`.
