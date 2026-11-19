# PR90 revisada e auditoria de atributos de invocações · 08/11/2026

## Parecer da PR90

Sem novo bloqueio encontrado no delta revisado. PR aberta, não draft,
sem merge e sem conflitos reportados pelo GitHub. Base PR89
`e2b03307ebfaa3df67b494704508c10f3bd523b6`; head conferido
`4eeb276b3938105f9e33a647e9fa0657a700b4f8`.

Dois workflows concluídos com sucesso nesse head:

- [pull_request · 42534146894](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42534146894).
- [push · 42534090450](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42534090450).

Conferidos gerador, plano incremental, runtime de recuperação, bootstrap,
menus estritos e fontes regeneradas. A correção distingue ausência, nível
inteiro válido e entrada inválida; preserva o valor original, a prévia do
vazio e as aquisições que acompanham o invocador. Inválido em aquisição
fixa exige REVISAR, com cálculo provisório no nível 1. Não aprova a montagem.

Repetidos nesta revisão, com saída zero:

```text
node r53/testes/nivel_obtido.js <Codigo-era-antes.gs privado da PR90> <pacote antigo privado>
node r53/testes/nivel_obtido_modelo.js <base/apps-script privada da PR90>
git diff --check e2b0330..4eeb276
```

O primeiro conferiu 36 fórmulas, duas notas, 12 validações, 60 suportes,
pt_BR/en_US, recusa de snapshots divergentes, reversão, idempotência,
recuperação e carregamento real do pacote antigo. O segundo comparou
280.056 posições em 26 abas: delta exato e modelo incremental igual ao
integral, preservando ANALISE e demais estruturas.

As 240 observações nativas, seis controles de interface, 12 recuperações
reais, 16 onEdit concluídos e código salvo/reaberto/relido da instalação
anterior foram revisados nas evidências, **não executados novamente**.
Não se repete como resultado novo o smoke integral 124/124 da implementação.
O código Google não foi reinstalado nem relido integralmente nesta rodada.
Seu último hash comprovado permanece `b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e`.

PR90 continua empilhada sobre PR89. Não está aplicada nas oficiais.
`nivel_fixo = -1` em entrada inválida é mudança semântica documentada;
consumidor/bot não foi validado. Recuperação de retângulos arbitrários fora
dos moldes publicados e desempenho Android continuam fora desta aprovação.

## Pente-fino novo: atributos das invocações

Ensaios somente nas duas descartáveis já autorizadas, com snapshots
novos persistidos antes das escritas. Entidades 1 e 12 alternadas entre
Era/Ciclo; localidade nativa pt_BR. Nenhuma fórmula ou código instalado mudou.

Referência focal: [manual de invocações, commit e3058ad](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/manual/60-invocacoes.md).
São nove pontos iniciais, máximo três por atributo na criação, um ponto
por Marco e teto posterior seis. Marcos usados: 6, 10, 14, 18, 22, 26 e 30.
Não se atualizou o catálogo nem se declarou toda a extração histórica como R66.

**44 observações novas: 34 controles aprovados e dez sondagens de entradas
forçadas**, sem transformar sondagens em aprovações ou erros de uso comum.

Os controles verificaram pontos individuais, totais com buffs, gasto,
orçamento disponível, Marcos, excesso acima de três e sinalização. Cobrem
criação válida, excesso, saldo não gasto, transição 5→6, segundo Marco,
distribuição em vários atributos, teto seis no nível 14, nível 30, fórmula
que retorna número e buffs positivos/negativos. Não são uma nova certificação
de todas as fórmulas de PV; o PV foi confrontado focalmente no caso abaixo.

Os menus de pontos já são estritos: ONE_OF_RANGE, fonte
`DADOS_INVOC!CN2:CN8`, números 0–6. Não falta um menu de limite.

## Observação condicional: N(texto) nos pontos de atributo

Em `ficha-v01/ficha_invocacoes.py`, `p0` a `p4` ainda usam `N(entrada)`.
Se texto numérico chegar à entrada, ele vira zero nas contas. Isso já
existia antes da PR90; não é uma regressão do validador de nível obtido.

Caso sintético, entidade nível 1, pontos 3/3/3/0/0, sem buffs:

| Constituição na entrada Q20 | Constituição calculada | Pontos gastos | PV máximo |
| --- | ---: | ---: | ---: |
| número 3 | 3 | 9 | 8 |
| texto `3` | 0 | 6 | 5 |

O texto foi gravado e relido nas duas QAs usando a sequência automatizada
F2 → selecionar tudo → `typeText("'3")` → Enter. O Google conservou o menu
estrito e mostrou dica **Inválido**; o resumo informou apenas pontos não
gastos. A inserção também retirou o formato numérico customizado de Q20.
Isso limita a interpretação do ensaio e foi restaurado ao final.

**Controle necessário para evitar falso positivo:** digitação por teclas
F2 → selecionar tudo → apóstrofo → 3 → Enter foi recusada pelo Google nas
duas QAs, sem gravar o texto. Colagem textual explícita na Era e fórmula
`="3"` na Era também foram recusadas. Número 3 funcionou nas duas; número
7 por teclas foi recusado na Ciclo. Total de nove tentativas de interface.

Portanto, ficou confirmada uma **lacuna de robustez diante de valor textual
já gravado**, com reprodução pelo método automatizado específico e pela
API. Não ficou comprovado que a digitação ou colagem comum permita esse
estado. Não se contabiliza como novo erro mecânico do fluxo normal nem como
bloqueio da PR90. Antes de promover a prioridade, reproduzir manualmente em
uma descartável ou definir explicitamente o suporte a importações/colagens.

As sondagens via API de negativo, fração e sete pontos também não recebem
validação adicional no resumo de orçamento, mas contornam os menus. São
limites de defesa das fórmulas, não três novos bugs normais comprovados.
Nenhuma correção especulativa foi instalada.

## Preservação e retomada

29 entradas por cópia restauradas. Comparadas **86.000 posições por cópia**,
incluindo **MONTAGENS inteira A1:I9543, 85.887 posições**. API devolveu 37.065
células explícitas por cópia; omissões equivalem a vazio. Zero diferenças
nos valores, fórmulas, tipos, notas e validações lidos. Metadados, incluindo
formatação condicional, iguais. Essa comparação não é de toda a grade nem
de toda a formatação individual de células.

O formato numérico de Q20 foi reposto: na Era, padrão `0" pt"` conferido
nos outros quatro pontos do mesmo bloco e no gerador; na Ciclo, snapshot
individual anterior à interface. Demais campos do formato na Era coincidem
com os pares lidos; na Ciclo o objeto completo foi relido igual ao snapshot.
Visuais restaurados, auxiliares mantidas ocultas e duas abas de teste fechadas;
nenhuma aba da tarefa ficou aberta. Sem novo pedido de autorização Google.

Evidência sanitizada: `revisao_pr90_atributos_2026-11-08.json`.
Backups e capturas somente em
`nuvem-b47/saidas/revisao-pr90-atributos-20261108/`, ignorado pelo Git.
Primeiros snapshots grandes que falharam não foram usados: os dois arquivos
`antes-*.json` usados foram persistidos, parseados e conferidos antes da escrita.

Ramo separado `codex/revisao-pr90-auditoria-20261108`, apenas parecer e
diagnóstico. Nenhum merge, oficial, jogador, PR31, acesso ou acionador.
PR31 conservada em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
Preservar suportes da PR89/90, isolamento da PR88 e escape da ANALISE.

Próximo recorte plausível: perícias e treinos das entidades, seus limites e
buffs, com referência do manual e controles de entrada antes de atribuir
erro mecânico. Não há afirmação de que o pente-fino global terminou.
Sol/Medium para revisão; Sol/High para implementação ou novo ensaio nativo.
Não mudar configurações automaticamente nem abrir agentes.
