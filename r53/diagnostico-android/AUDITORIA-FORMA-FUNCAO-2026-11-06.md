# Auditoria de Forma e função das Melhorias · 06/11/2026

As duas descartáveis, Era e Ciclo, estavam na PR82 `b11c46a`.
O estado foi conferido por releitura de CK2, CP2 e FX2.
A referência usada foi a R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Os testes usaram um cartão comum de Classe 3 na aba FICHA
AMALDIÇOADA e leram a validade, os avisos, o resumo, o saldo e
o dano efetivo. A tabela descreve montagens com Formas publicadas.

## Divergências confirmadas

As dez combinações abaixo ficaram VÁLIDAS e sem aviso nas
duas descartáveis.

| Melhoria | Montagens testadas | Requisito da R66 |
| --- | --- | --- |
| Escolher | Projétil e Toque | A seleção acontece ao criar uma área. |
| Contorno | Projétil e Toque | A área precisa de um percurso aberto. |
| Perseguir | Cone e Explosão | A Melhoria acompanha um alvo individual. |
| Reserva | Só dano e só PV temporários | A reserva é formada rolando dados de cura. |
| Sugar | Só cura e dano final de 0d8 com Toca a Alma | A recuperação depende de dano inicial efetivo em criaturas. |

Escolher e Contorno em Cone, Perseguir em Projétil, Reserva com
2d8 de cura e Sugar com dano efetivo permaneceram válidos.
Maior em Projétil e Concentrada junto com Duradoura pediram
revisão. A repetição de Explosão com apenas Perseguir isolou o
requisito de alvo. A primeira tentativa incluía Guarda e pediu
revisão pelo saldo negativo. O controle de Toque com Guarda
confirmou os 2 pontos próprios de Toque. O comparativo de
Escolher e Contorno em Toque considera esse crédito legítimo.

Em `r53/modelo.py`, os avisos já distinguem Maior, Terreno, Fica
e Mais Um por Forma. A validação atual deixa Escolher, Contorno
e Perseguir sem a condição correspondente. Os cartões testados
também passam sem uma conferência de dados de cura para Reserva
ou de dano inicial efetivo para Sugar.

## Preservação

Foram 20 cenários por cópia em duas rodadas. As 15 entradas
temporárias foram repostas após cada rodada. A releitura de
624 células por cópia, incluindo 539 posições de MONTAGENS,
encontrou zero diferenças e zero erros nos intervalos conferidos.
A PR82 segue instalada nas descartáveis. Evidências privadas em
`nuvem-b47/saidas/auditoria-duracao-e-alvos/`.
