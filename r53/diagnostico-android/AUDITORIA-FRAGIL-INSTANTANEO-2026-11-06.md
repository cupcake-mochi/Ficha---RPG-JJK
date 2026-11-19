# Instalação da PR80 e auditoria de Frágil · 06/11/2026

## PR80 nas descartáveis

A primeira execução dos dois checks falhou na conferência histórica
de `DADOS_R53!CZ252`. O teste de Prática Cotidiana ainda usava a
fórmula anterior. O commit `97d1b00` inclui CZ na comparação e
verifica a fórmula nas duas vagas restauradas em bloco. A mudança
ficou no teste. O smoke local e os dois checks do GitHub passaram
na nova execução. A PR80 ficou sem conflitos.

Foram arquivados o Código anterior e as 753 fórmulas de cada
descartável. O Código.gs foi salvo e relido nas duas cópias,
SHA-256 `9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05`.
O EditorR53 conservou o hash anterior.

Foram instaladas e relidas 753 fórmulas em 15 lotes por cópia,
nas colunas CK, CP e CZ de DADOS_R53. A releitura registrou zero
erros de fórmula e zero diferenças de nota ou validação.

| Cópia | Cartão comum | Classe 0 | Controle herdado da PR78 |
| --- | --- | --- | --- |
| Era | CZ2 | CK252 | FX2 |
| Ciclo | CP2 | CZ253 | FX2 |

As seis fórmulas apagadas na interface voltaram idênticas à
proposta. O Apps Script registrou as seis execuções concluídas,
com duração entre 7,030 e 10,861 segundos. Esses tempos cobrem as
execuções ensaiadas.

DADOS_R53 voltou a ficar oculta e o intervalo temporário de
transporte da Era voltou ao vazio. A releitura de 596 células
por cópia, incluindo 532 posições de MONTAGENS, confirmou zero
diferenças fora dos alvos da instalação.

## Pente-fino de Frágil

Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Frágil devolve até o valor Leve das Melhorias pagas cujos efeitos
podem ser interrompidos. Um feitiço que termina na própria resolução
carece de efeito interrompível.

Em Projétil de Classe 3, nos cartões comuns das duas descartáveis,
o ensaio usou dano e uma única Melhoria por vez, com 2 no campo
de gasto interrompível. Em cada caso o cartão ficou VÁLIDO,
sem aviso, e recebeu 2 pontos de devolução. Os seis casos foram
Passo, Empurrão, Longe de um degrau, Mais Um, Rajada e Remate.
As descrições especificaram aplicações que terminam na resolução.

Com Guarda e Passo, a declaração de 4 pontos também ficou VÁLIDA.
Guarda custava 3, e Passo era instantâneo. O crédito aplicado
continuou em 2 pelo teto Leve. Esse caso confirma uma falha de
validação do gasto declarado, mesmo sem excesso no crédito final.

A origem está em `r53/modelo.py`. O teto de gastos de Frágil
exclui Precisão e conta o preço das demais Melhorias. A validação
usa esse teto para aceitar ou rejeitar o valor digitado. Esses
casos já eram possíveis na PR79.

Os controles confirmaram Guarda com 2 pontos, Guarda + Passo
com declaração de 3, Precisão com zero e Passo sem declaração
com zero. Na PR80 instalada, Atrasar + Parado ficou em REVISAR
com 3 pontos, Sangra em Classe 0 devolveu zero e Barulho devolveu 1.

Foram 14 cenários por cópia. As 21 entradas temporárias foram
repostas. A releitura de 624 células por cópia, incluindo 539
posições de MONTAGENS, encontrou zero diferenças e zero erros.
As duas descartáveis estão com a PR80. Evidências privadas em
`nuvem-b47/saidas/instalacao-restricoes-agrupadas/`.
