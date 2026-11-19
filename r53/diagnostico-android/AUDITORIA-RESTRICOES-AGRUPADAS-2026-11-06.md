# Instalação da PR79 e auditoria das Restrições agrupadas · 06/11/2026

## PR79 nas descartáveis

A PR79 `4118bb9` estava sem conflito e com os dois checks aprovados.
O teste local do transporte, da reversão e dos moldes de recuperação
passou. Foram arquivados o Código anterior e as fórmulas dos 502
alvos de cada cópia antes de qualquer aplicação.

O Código.gs salvo e relido nas duas descartáveis corresponde ao
SHA-256 `30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658`.
O EditorR53 conservou o hash anterior.

Foram instaladas e relidas 502 fórmulas por cópia, em 15 lotes,
nas colunas CK e CP de DADOS_R53. Zero erros de fórmula e nenhuma
diferença de nota ou validação.

| Cópia | Cartão comum | Classe 0 | Controle da PR78 |
| --- | --- | --- | --- |
| Era | CK2 | CP252 | FX2 |
| Ciclo | CP2 | CK253 | FX2 |

As seis fórmulas foram apagadas pela interface. O acionador simples
concluiu as seis execuções e restaurou o texto exato da fórmula.
O painel do Apps Script registrou durações de 7,647 a 20,824
segundos. Essas durações se referem às execuções do teste e
deixam em aberto o desempenho geral no Android.

DADOS_R53 voltou a ficar oculta e o intervalo temporário da Era
voltou ao vazio. A releitura de 596 células por cópia, incluindo
532 posições de MONTAGENS, confirmou zero diferenças fora do lote.

## Pente-fino

Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Os cartões comuns de Classe 3 abaixo exibiram REVISAR, mas o crédito
aumentou o saldo. Nas linhas com duas Restrições mutuamente
exclusivas, o limite de comparação é a maior devolução entre as
opções isoladas. Essa comparação mede o excesso. A escolha de
qual Restrição fica exige revisar a montagem.

| Combinação de Classe 3 | Crédito aplicado | Limite de comparação |
| --- | ---: | ---: |
| Atrasar + Reação | 3 | 0 |
| Atrasar + Parado | 5 | 3 |
| Barulho + Assinatura | 4 | 2 |
| Barulho repetido | 4 | 2 |
| Recuo Lento + Fraqueza TR Físico | 5 | 3 |
| Fraqueza TR Físico + Peso Morto | 5 | 3 |
| Recuo Lento + Peso Morto | 4 | 2 |
| Uma Vez + Aquecer | 4 | 2 |
| Condicional Média + Aquecer | 5 | 3 |
| Uma Vez + Condicional Média | 5 | 3 |
| Remate + Aquecer | 2 | 0 |

Os controles em Classe 3 confirmaram 3 pontos para Atrasar sozinho,
2 para Parado sozinho e 5 para Sangra + Barulho, combinação de
dificuldades independentes. Os casos com Passo foram informativos
e conservaram o aviso de impedimento por Atrasar ou Parado.

Em Classe 0, Sangra, Atrasar, Carregar e Sem Volta estavam no
menu e foram rejeitadas pelo aviso de peso. Cada uma ainda
devolveu 1 ponto e exibiu 6d8 no cartão com Precisão. Barulho,
o controle válido de peso Leve, também deu 1 ponto. O menu
da Classe 0 usa o mesmo intervalo Q2:Q62 do catálogo dos cartões
comuns. A fórmula de devolução da Classe 0 fixa 1 para as
opções que passam pela guarda de crédito. O aviso de peso é
calculado separadamente. A PR79 cobre sete incompatibilidades
específicas e essas condições já existiam na base PR78.

Em cada descartável foram 21 cenários e 15 divergências
reproduzidas. As 21 entradas temporárias foram repostas.
A releitura de 622 células por cópia, incluindo 539 posições
de MONTAGENS, encontrou zero diferenças e zero erros. A PR79
permanece instalada nas duas descartáveis. Evidências privadas em
`nuvem-b47/saidas/instalacao-devolucoes-incompativeis/`.
