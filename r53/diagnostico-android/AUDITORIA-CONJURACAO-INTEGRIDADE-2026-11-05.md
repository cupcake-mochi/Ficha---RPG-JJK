# Conjuração e Integridade · 05/11/2026

Revisão da PR70 em `4324ad3`, sobre a PR69. O GitHub informou dois checks
`smoke` aprovados e estado sem conflito. Os testes focais locais passaram
com 992 verificações de estrutura, transporte e recuperação e 23.582 de
preflight e aparência. A revisão conferiu o acréscimo dos dois contextos,
a preservação dos 249 anteriores e o encaminhamento das novas áreas ao editor.

## Ensaio nativo

Reutilizadas as descartáveis de Era e Ciclo que receberam a PR70. Referência
mecânica R66 em `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
seção Estágios de Integridade. Os estágios são cumulativos. Ao perder pelo
menos metade da Integridade, soma-se 1 PE por Classe à conjuração. Ao perder
pelo menos três quartos, o teto de conjuração também cai à metade para baixo,
com mínimo 1 para quem já alcançou Classe 1.

Foram 12 leituras por cópia. Sete verificaram os limiares e a recuperação
com cartão sem preparação. Cinco repetiram a comparação com um feitiço
de Projétil preparado, um ponto de dano e a permissão de dano ativa. A Era
usou um cartão Classe 3 e Integridade máxima 65. O Ciclo usou Classe 1
e máximo 25, como controle do piso da regra.

| Caso com versão preparada | Integridade atual Era / Ciclo | PE no cartão Era / Ciclo | PE da conjuração segundo R66 |
| --- | --- | --- | --- |
| Alma inteira | 65 / 25 | 9 / 3 | 9 / 3 |
| Estágio 2 | 32 / 12 | 9 / 3 | 12 / 4 |
| Imediatamente acima do estágio 3 | 17 / 7 | 9 / 3 | 12 / 4 |
| Estágio 3 | 16 / 6 | 9 / 3 | Classe 3 acima do teto / 4 PE |
| Integridade recuperada | 65 / 25 | 9 / 3 | 9 / 3 |

## Achados

- O custo em `DADOS_R53!DX2` e o resumo de execução em
  `FICHA AMALDIÇOADA!D81` mantêm o preço base. `FICHA!D37` lembra o
  adicional no estágio 2. No estágio 3, o resumo de estágio mostra a
  redução de Classe sem repetir o adicional cumulativo.
- Na Era, `FICHA!Z73` e `DADOS_AM!HM4` representam o limite permanente
  de montagem. No estágio 3, o cartão Classe 3 continua `VÁLIDO` como
  montagem e o jogador precisa aplicar o teto de conjuração de Classe 1.
  A ficha não mostra o valor efetivo desse teto junto ao cartão ensaiado.
- Os limiares em `FICHA!D37` mudaram nas frações esperadas e a recuperação
  devolveu Alma Inteira. O orçamento, a distribuição de pontos e os
  marcadores de preparação permaneceram estáveis durante a variação de
  Integridade. A melhoria indicada é apresentar o preço e o teto de
  combate separadamente dos dados permanentes da montagem.

Escopo de diagnóstico de fórmulas e apresentação. As entradas foram
gravadas pelo conector e não dispararam `onEdit`. Este ensaio não mediu
desconto efetivo de PE, derrota, invocações, Liberação ou Técnica Máxima.

Ao encerrar, seis células de entrada por cópia foram repostas com seus
tipos originais. A releitura final conferiu 66 campos por cópia, incluindo
valores de entrada, notas, validações e controles vizinhos. Zero divergências.
Snapshots privados em `nuvem-b47/saidas/auditoria-conjuracao-integridade/`.
A PR31 foi conferida em `765e3b24`. Ensaios exclusivamente nas descartáveis.
