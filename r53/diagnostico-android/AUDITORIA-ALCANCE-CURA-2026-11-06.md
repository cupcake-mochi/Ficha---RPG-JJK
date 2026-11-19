# Revisão da PR72 e auditoria de feitiços de cura · 06/11/2026

A PR72 em `b7c06b0` está sem conflitos com a PR71, com os dois
checks aprovados. Os testes locais de Classe 0 (incluindo replay
privado do transporte) e Prática Cotidiana (1.000 verificações)
passaram. Sem bloqueios identificados no escopo da PR72.

## Ensaio

Nove cenários em cada descartável, Era e Ciclo, ambas com PR72. A
referência foi a R66 em `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
seções Funções e pontos que sobram e Alcance e área.

| Montagem | Conta ou resultado observado | Alcance exibido |
| --- | --- | --- |
| Classe 3, cura em Projétil | 9 − base Média 3 = 6 pontos. Alocação de 6 gera 6d8, por 9 PE. Válido | **18 m**, benefício deveria mostrar **9 m** |
| Classe 3, cura em Projétil com Guarda | 9 − base 3 − Guarda 3 = 3 pontos. Gera 3d8 e +2 Defesa | **18 m**, benefício deveria mostrar **9 m** |
| Classe 3, dano e cura em Projétil | Base 3 uma vez. 2d8 de dano e 4d8 de cura | Só **18 m**. A parte de cura tem **9 m** |
| Classe 3, vida temporária em Projétil | Base Leve 2. Cinco pontos destinados geram 15 PV temporários | **18 m**, benefício deveria mostrar **9 m** |
| Classe 3, Aura de cura | Base 3, Forma 2. Quatro pontos destinados geram 4d8 | Centradas no conjurador, raio 3 m, conforme |
| Classe 3, Aura de cura e vida temporária | Base 3 compartilhada, Forma 2. 2d8 e 6 PV temporários | Centradas no conjurador, raio 3 m, conforme |
| Classe 3, cura com Toque | Base 3. 6d8 de cura | 1,5 m, conforme |
| Classe 3, cura com 7 pontos destinados | Saldo 6. Cartão em REVISAR, com aviso de distribuição excedida | Montagem inválida, fora da comparação de alcance válido |
| Classe 6, cura em Projétil | Base Média 6, 12 pontos destinados dão 12d8, por 18 PE | **36 m**, benefício deveria mostrar **18 m** |

O núcleo já calcula corretamente os dois alcances em
`DADOS_R53!EQ2:ER2`. O resumo em `FICHA AMALDIÇOADA!D81` usa só
`alcance_ofensivo`, como definido em `ficha-v01/cartoes_diretos.py`.
A correção de apresentação deve mostrar a medida de benefício quando
aplicável e distinguir as duas medidas no caso misto. Manter a origem
da área, Toque e o cálculo de PE e Integridade da PR71. Trunfos,
invocações, Formas próprias e Longe ficaram fora deste ensaio.

Foram feitas gravações temporárias pelo conector. Os marcadores de
preparação isolaram a conta nativa. A primeira entrada sintética usou
o texto do menu de Classe no lugar do número subjacente e foi
descartada. As 18 leituras válidas usaram os tipos reais do cartão,
sem erros de fórmula. Não houve ensaio do evento de edição ou de
aplicação de cura ao alvo. Ao encerrar, as dez entradas de cada cópia
foram repostas e 243 células por cópia foram relidas sem divergências.
Evidência privada em `nuvem-b47/saidas/auditoria-cura-feiticos/`.
