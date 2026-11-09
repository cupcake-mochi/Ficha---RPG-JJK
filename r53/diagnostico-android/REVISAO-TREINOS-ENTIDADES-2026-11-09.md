# Treinos e limites das entidades · 09/11/2026

Recorte que o parecer da PR90 deixou como próximo: perícias e treinos
das entidades, seus limites e buffs. Referência: manual de invocações
no commit `e3058ad` do JJK---Project (`60-invocacoes.md`, igual ao da
`bbc4428`, última mudança do arquivo). O achado 1 foi corrigido (ver
"Correção"); o 2 é decisão de regra.

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

## Correção do achado 1

`d_titulo` (DADOS_INVOC!HG2:HG13) ganhou, logo antes de " · nível ":

```
IF(OR($DVr="Físico";$DVr="Vigor";$DVr="Intelecto";$DVr="Espírito");"";" · REVISAR: escolha o TR treinado")
```

`$DV` é a mesma caixa que dá a maestria aos quatro TR. O "=" do Sheets
não diferencia maiúsculas, então "vigor" vale; acento e espaço contam,
então "Fisico" ou " Vigor" pedem revisão, como pedem na conta do TR. Vaga
sem nome continua "lugar vazio". A entrada não é reescrita.

O `NivelObtido` grava o título com o aviso de nível e o restaura quando
alguém edita a coluna. Os 12 pares `antes`/`depois` da coluna 215 em
`nivel_obtido_valores.json` receberam o mesmo trecho. Sem isso o pacote
R53 recusava o modelo ("Nível obtido: valor divergente") e a restauração
apagaria o aviso novo.

Arquivos: `ficha-v01/ficha_invocacoes.py`, plano
`preparar_tr_treinado.js` → `tr_treinado_delta.json` (12 fórmulas em
280.056 posições de 26 abas), teste `r53/testes/tr_treinado.js` no smoke.

**Ensaio nas duas QAs, 09/11.** HG2:HG13 conferidas iguais ao `antes`
(pt_BR) e trocadas pelo `depois`. Na vaga 1, com nome provisório:

| QA | TR treinado | título |
|---|---|---|
| Era | vazio | `… · REVISAR: escolha o TR treinado · nível 10 · vida 32 de 32` |
| Era | Vigor | `… · nível 10 · vida 32 de 32` |
| Era | Fisico (colado) | `… · REVISAR: escolha o TR treinado · nível 10 …` |
| Ciclo | vazio | `… · REVISAR: escolha o TR treinado · nível 2 · vida 8 de 8` |
| Ciclo | Espírito | `… · nível 2 · vida 8 de 8` |

Nome e TR voltaram a vazio; o título voltou a "INVOCAÇÃO 1 · lugar vazio".

## Fora do recorte

Pontos fora de 0–6 já corrigidos na PR94. Buff/Debuff decimal e a
divergência com a ficha do jogador estão no `PENDENCIAS.md`.
