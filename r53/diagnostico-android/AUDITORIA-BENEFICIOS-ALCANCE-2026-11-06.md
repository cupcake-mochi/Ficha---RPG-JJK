# Revisão PR73 e auditoria de benefícios e alcance · 06/11/2026

A PR73 `868ebb8` está sem conflitos com a PR72 e com os dois checks
aprovados. O teste focal e o replay privado da preparação incremental
passaram, com os 36 alvos. Nenhum bloqueio identificado na correção de
cura e PV temporários.

O ensaio seguinte usou duas descartáveis com a PR73. Livro de referência
R66, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, seções
Formas, Alcance e área e entradas Longe e Maior.

## Achado de apresentação

Nos cartões comuns, Guarda, Impulso e Firmeza à distância continuam
exibindo o alcance ofensivo quando não há cura ou PV temporários.
Os três foram ensaiados separadamente na Classe 3, com Projétil e sem
dano. As montagens estavam válidas e o cartão mostrou 18 m em vez de
9 m. Em dano com Guarda e Longe de um degrau, o cartão mostrou apenas
36 m, embora Guarda tivesse alcance de 18 m.

O núcleo calcula os dois alcances corretamente em `DADOS_R53!EQ2:ER2`.
O resumo `FICHA AMALDIÇOADA!D81` só seleciona o alcance de benefício
quando a ficha tem cura ou PV temporários. O achado é separado do
delta ensaiado na PR73 e não exige alterar montagens ou alcance de área.

## Controles nativos

| Caso | Resultado nas duas cópias |
| --- | --- |
| Cura com Longe de um degrau, Classe 3 | 18 m no resumo, conforme |
| Dano e cura com as duas modalidades de Longe, Classe 5 | Ambos chegam a visão a olho nu e o resumo mostra a medida uma vez |
| Explosão Classe 2 com Longe e Maior de um degrau | Origem a 36 m e raio 4,5 m, conforme |
| Aura com Longe | Inválida, aviso de incompatibilidade |
| Projétil com Maior | Inválida, aviso de ausência de Forma de área |
| Longe com Queima-Roupa | Inválida, aviso de incompatibilidade |

Foram dez cenários por cópia. As escritas temporárias pelo conector
isolaram o cálculo com marcadores de preparação. O ensaio não executou
a conjuração nem disparou eventos de edição. Repostas 13 entradas
por cópia. A releitura de 324 células por cópia, incluindo 259 posições
de MONTAGENS, terminou sem diferenças e sem erros nos intervalos.
Evidências privadas em `nuvem-b47/saidas/auditoria-beneficios-alcance/`.
