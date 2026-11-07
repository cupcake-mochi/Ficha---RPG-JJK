# Revisão PR88 · isolamento de erros nos nomes · 07/11/2026

## Resultado

A PR88 foi revisada no head `4d22fb71f222da220712aec668b90ee1b52a94e4`,
sobre a PR87 `0554071`. Continua aberta, sem conflitos e com dois checks
smoke SUCCESS nesse commit. Os testes focais de preparação/recuperação e
comparação do modelo passaram novamente: 24 fórmulas, 280.056 posições,
26 abas e metadados preservados. Não foi repetido o smoke inteiro.

**Há um bloqueio de revisão confirmado: R88-01 [P2].** O novo cálculo
propaga erro de uma célula de nome fora do orçamento para todas as
entidades. Portanto a PR88 não deve ser considerada pronta apenas pelos
checks verdes. O código da PR88 não foi alterado nesta rodada.

## R88-01 · erro numa básica alcança as especiais das 12 entidades

`ficha-v01/expansao_domada.py:38–39` calcula `LEN` em todo o registro global
`DADOS_R53!B2:B253`, incluindo básicas, extras e cartões de outras entidades.
O resultado é multiplicado pelo teste de identidade das especiais normais.
Esse teste não impede a avaliação do erro no outro operando: zero vezes
um erro continua sendo erro.

Reprodução nativa nas duas descartáveis:

1. Colher snapshot de `INVOCAÇÕES!J71` e dos resultados envolvidos.
2. Colocar a fórmula `=1/0` no nome da **Básica 1**, em J71.
3. O registro leve B47 devolve erro; A47 continua `entidade.1.bas.1`.
4. Os **12 cabeçalhos** `DADOS_INVOC!IE2:IE13` devolvem `#DIV/0!`, mesmo
   que essa básica não ocupe espaço de especial normal.
5. Quando os 12 seletores de domínio contêm Completa, os **12 requisitos**
   `JJ2:JJ13` também devolvem erro, substituindo os avisos mecânicos.

O mesmo efeito foi reproduzido com `=NA()`: os 24 resultados mostram N_A.
Não foram inseridos erros nas fórmulas de orçamento, no registro leve ou
em células de outra entidade. A única origem é um campo de nome livre,
sem validação que o proíba de conter fórmula.

O erro digitado continua exigindo correção no próprio nome. O defeito da
PR88 é espalhá-lo para contas de categorias/entidades sem relação com ele.
Nomes comuns em texto ou número não provocaram essa falha.

## Comparação com a fórmula anterior

Foi feita uma comparação A/B em cada QA, com a mesma origem `J71 =1/0`:

- IE2 da PR88, com SUMPRODUCT e LEN global: `#DIV/0!`.
- IE2 com sua fórmula anterior da PR87, COUNTIFS por identidade: cabeçalho
  normal com consumo 0+0 e a capacidade original da cópia.

Somente IE2 foi trocada temporariamente para essa comparação; a fórmula
da PR88 e o valor original de J71 foram repostos em seguida. Isso confirma
que a propagação observada foi introduzida pela PR88. Não significa que
a fórmula anterior resolva o defeito de nomes numéricos: ela continua
ignorando esses nomes, conforme a auditoria anterior.

Não instalar a fórmula anterior como correção definitiva. A solução
precisa conservar números/zero/booleanos e o vazio por fórmula, isolando
a avaliação dos nomes à categoria e entidade pertinentes. Não envolver
a conta inteira em IFERROR retornando zero: isso pode ocultar uma montagem
com problema ou fazer um gasto desaparecer. O erro do campo de origem e
avisos mecânicos legítimos precisam permanecer visíveis.

## Matriz focal e restauração

Foram cinco configurações globais por cópia, dez no total. Cada uma
conferiu os 12 cabeçalhos e os 12 requisitos: **240 resultados observados**.
São quatro cenários de propagação e seis controles, variações de um
único defeito; não 240 defeitos ou 240 cenários independentes.

| Nome da básica | Cabeçalhos e requisitos observados |
| --- | --- |
| Texto `QA básica` | Contagem normal zero; sem erro de fórmula |
| Número 7 | Contagem normal zero; sem erro de fórmula |
| Fórmula `=""` | Contagem normal zero; sem erro de fórmula |
| Fórmula `=1/0` | DIVIDE_BY_ZERO nas 24 fórmulas |
| Fórmula `=NA()` | N_A nas 24 fórmulas |

Os domínios ficaram em Completa somente durante a matriz para executar
o ramo do requisito. As restrições originais de tipo, nível, refino e
capacidade foram mantidas: os controles não significam aprovação desses
domínios. Não houve ajuste para tornar avisos legítimos verdes.

As 13 entradas temporárias de cada cópia foram repostas. A comparação
focal de **1.038 posições por cópia**, incluindo **999 de MONTAGENS** de
três cartões, encontrou zero diferenças e zero erros remanescentes.
Há 435 posições com metadados explícitos; as caudas vazias omitidas pela
API foram tratadas como vazias nas duas leituras. Foram comparados
valores digitados/calculados, tipos, notas e validações. Os metadados
de arquivo/abas retornados pelo conector também ficaram idênticos.
Formatação não foi escrita nem incluída na comparação de células.

O estado restaurado foi conferido visualmente nas duas QAs. Auxiliares
permanecem ocultas. A amostra de montagens cobre a Básica 1, Especial 1
da primeira e Especial 1 da última entidade; não é varredura integral de
todas as versões da ficha. Os ensaios foram pela API nativa do Sheets,
que não dispara onEdit. Não houve instalação de código ou teste novo
de eventos nesta revisão.

## Entrega e próximo passo

Evidência sanitizada: `revisao_pr88_erros_nomes_2026-11-07.json`.
Snapshots, comparação A/B e capturas somente em
`nuvem-b47/saidas/revisao-pr88-contagens/`, ignorado pelo Git.
Ramo separado `codex/revisao-pr88-contagens-20261107`, sobre a PR88.

É necessário corrigir R88-01 na PR88 e ensaiar erro fora da categoria,
erro em outra entidade e manutenção da indicação no campo que falhou,
além dos controles numérico/vazio e da recuperação por edição real.
Nenhuma proposta de fórmula foi aplicada como solução nesta rodada.
O próximo grupo de mecânicas do pente-fino não foi iniciado: a condição
de concluir primeiro a revisão da PR88 ainda não foi atendida.

Sem merge, alterações nas oficiais, ficha do jogador, acionadores ou
acesso. PR31 permanece aberta em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
Sol/High para corrigir e ensaiar o isolamento; Sol/Medium para revisão
da evidência. Nenhuma configuração foi alterada.
