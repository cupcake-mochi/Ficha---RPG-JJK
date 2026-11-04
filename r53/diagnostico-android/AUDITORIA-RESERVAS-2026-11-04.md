# Auditoria de vida e energia temporárias — 04/11/2026

Base: PR57 `8db0bae93a3fb04a4a165d632590a0b270aef51a`, sobre PR56.
Ramo de diagnóstico separado `codex/auditoria-reservas-20261104`.
Nenhum código de produção modificado, merge, escrita nas oficiais/jogador ou
alteração da PR31. A PR57 continua sendo a preparação do incremento anterior.

## Regra consultada

Livro atual R66, `cupcake-mochi/JJK---Project` no commit
`e3058ad29180fdec2efec75b512446c49bf87b3d`, seção Dano e recuperação →
Vida e energia temporárias (linhas 1654–1681 de LIVRO-COMPLETO.md).
Texto completo conferido: SHA-256
`315ba23a9044234b8eab9e94ff1412d553b45c46089548809741777b1e287893`.
A mesma regra já consta no livro R65 usado anteriormente, commit `a98d4af…`.

Vida/PE temporários têm teto de metade do máximo, arredondada para baixo,
com mínimo 1 apenas para máximo positivo. Máximo zero não cria temporários.
São consumidos antes da reserva comum. Vida temporária não cura nem encerra
Morrendo. As entradas manuais representam o saldo final: substituir uma fonte
ou encerrar a cena exige poder reduzir/zerar o campo; não tratar toda digitação
como uma concessão nova que deve conservar o maior valor.

## P2 confirmado — máximo zero permite temporários

`apps-script/Codigo.gs`, função `tetoTemp_`, usa `if (max <= 0) return v`.
Isso trata zero como ausência de teto, devolvendo integralmente o valor
digitado. A função no módulo recuperado do ensaio nativo é igual à fonte Git.
`aplicaPasso_` também foi comparada entre fonte e módulo e é idêntica.

Na cópia descartável, editando pelo navegador:

| Recurso | Máximo controlado | Digitado no campo TEMP | Esperado | Relido no Google |
|---|---:|---:|---:|---:|
| Vida | 0 | 9 | 0 | 9 |
| PE | 0 | 6 | 0 | 6 |

A preparação dos máximos foi feita por API na cópia, sem disparar onEdit.
A digitação dos temporários foi nativa, pelo campo da ficha. Releitura de
userEnteredValue/effectiveValue e captura do Google confirmaram ambos os valores.
Isso permite manter uma reserva temporária onde a regra não permite sua criação.
Não é falha introduzida pelas PRs 51–57: a rotina é anterior a elas.

Correção recomendada: distinguir máximo zero de máximo ausente/inválido em
`tetoTemp_`, e impedir temporários em zero. Preservar o mínimo 1 para máximo
positivo, a edição manual do saldo, os caminhos de dano e eventuais exceções
explícitas de campanha. O campo de Integridade temporária precisa de análise
separada; a regra citada cobre vida e PE. Não fazer troca global de `max <= 0`.
Uma correção posterior deverá alcançar a fonte e o módulo instalado por delta
estrito, com ensaio nativo. Nada foi corrigido nesta auditoria.

## Controles nativos aprovados

A cópia veio da QA Era com as PRs 51–56 já ensaiadas; as oficiais não foram
usadas como destino. As fórmulas máximas foram temporariamente substituídas por
literais somente para controlar os testes.

| Cenário | Resultado relido |
|---|---|
| Vida máxima 23, TEMP recebe 15 | TEMP limitado a 11 |
| Vida 10, TEMP 11, ajuste −12 | Vida 9, TEMP 0, caixa ± limpa |
| PE máximo 8, TEMP recebe 6 | TEMP limitado a 4 |
| PE 2, TEMP 4, ajuste −5 | PE 1, TEMP 0, caixa ± limpa |
| Vida 0, máximo 1, TEMP recebe 15 | TEMP 1 e vida continua 0 |

Total: sete cenários nativos válidos, cinco conformes e dois divergentes pela
mesma causa. Uma primeira tentativa do gasto de PE foi invalidada: a preparação
do cenário seguinte aconteceu enquanto o evento ainda estava pendente. A
repetição partiu de estado controlado e aguardou a limpeza do ± antes de ler o
resultado. Não contar a tentativa invalidada como falha da ficha ou aprovação.

Ao terminar, os 12 campos de recursos consultados foram restaurados exatamente
aos userEnteredValue iniciais, incluindo as fórmulas máximas. O código da cópia
não foi alterado. A cópia continua sendo QA herdada, não modelo para distribuir.

## Diagnóstico local reproduzível

```sh
node r53/testes/reservas_diagnostico.js
```

46 casos nas funções reais: 30 combinações de teto e 16 de ajuste (oito
cenários tanto no módulo quanto no atalho). Resultado: 43 conformes; três
combinações divergentes com máximo 0 e concessões 1, 6 e 15. O comando é um
**diagnóstico**, imprime as divergências e não equivale a uma suíte toda verde.

As contas de dano parcial, absorção integral, gasto de PE, limite inferior,
ganho sem repor TEMP, teto de ganho e proteção com vida zero passaram localmente.
Essas oito combinações não são todas ensaios nativos: a tabela acima delimita
exatamente os casos executados no Google.

## Evidências e fila

Snapshots, respostas Google e captura ficam somente em
`nuvem-b47/saidas/auditoria-reservas/`, ignorado. O JSON sanitizado do diagnóstico
local e este relatório não contêm snapshots ou dados de jogador.

Continuam fora desta rodada: onEdit das invocações, dano de Alma/Integridade,
concessão de temporários por capacidade específica, duração entre cenas,
colagens de múltiplas células e gatilhos de condições. Nenhuma garantia de
cobertura integral ou latência Android decorre destes resultados.

Próximo passo: revisão e correção focal do máximo zero; Sol/High para implementar,
Sol/Medium para revisar, sem mudar configurações automaticamente.
