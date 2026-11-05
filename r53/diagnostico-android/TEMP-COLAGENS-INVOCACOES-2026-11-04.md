# Teto de TEMP em colagens e invocações

Base `cb04317` da PR61, pronta para revisão. Escopo A04 e A07.

O teto usa a interseção da edição com a âncora de cada TEMP. Lê o máximo
e o valor atual em lote e altera somente as caixas que precisam de limite.
Nas invocações, o atalho agora encaminha as 12 âncoras ao módulo. O teto
roda depois da restauração de fórmulas, para que uma colagem que inclua
a vida máxima não use o valor sobrescrito como teto. O diagnóstico
`testeTeto` distingue máximo em branco de máximo zero, conforme a PR61.

A descartável nova herdou Codigo.gs `5b81e86d…` da QA da PR61. O patch
incremental produziu e, depois de salvar, a releitura confirmou SHA-256
`3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7`.
Os outros nove arquivos GS mantiveram seus hashes. Os valores iniciais
foram preparados pela API e as edições abaixo ocorreram pela interface.

| Edição nativa | Resultado relido | Duração registrada do onEdit |
| --- | --- | ---: |
| FICHA!AF26:AQ26, TEMP 15 com máximo 20 e texto vizinho em AM26 | TEMP 10 e AM26 preservada | 17,436 s |
| INVOCAÇÕES!W13, TEMP 15 com máximo 20 | TEMP 10 | 20,372 s |
| INVOCAÇÕES!AP13:AQ13, TEMP 15 com máximo 0 e texto vizinho em AQ13 | TEMP 0 e AQ13 preservada | 16,554 s |
| INVOCAÇÕES!V13:W13, colar máximo 999 e TEMP 25 | Fórmula de máximo restaurada, máximo efetivo 32 e TEMP 16 | 31,097 s |

A tentativa inicial na coluna direita caiu no cabeçalho porque a seção
estava recolhida. O Sheets restaurou a fórmula do cabeçalho e AB11 foi
restaurada à mão a partir da base. A seção foi expandida para executar o
caso válido. Essa tentativa não conta nos quatro cenários aprovados.
Após os ensaios, restauramos as sete células divergentes. Os 47 valores
digitados, fórmulas e vazios dos recortes comparados ficaram iguais à base.
O Google não solicitou autorização.

Os tempos são do onEdit completo. A última operação concluiu no Google
com 31,097 s registrados, o que não permite garantir o tempo de colagens
maiores. Os dois lados da aba foram ensaiados no Google. A cobertura de
todas as 12 entidades é local.

Validação local: 667 verificações na cadeia de edição, diagnóstico onEdit
25/25, incremental 27 com snapshots, pacote leve 138 e smoke. O diagnóstico
histórico de A00/A08 segue na PR61. Restam A01, A02, A05 e A06.
