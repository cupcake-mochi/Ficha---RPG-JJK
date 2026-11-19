# Frágil e Melhorias instantâneas · 06/11/2026

Base PR80 `97d1b00`. Reprodução dos sete casos em
`AUDITORIA-FRAGIL-INSTANTANEO-2026-11-06.md`.
Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Passo, Empurrão, Longe, Mais Um, Rajada e Remate passam a ficar
fora do teto de gasto interrompível de Frágil, junto com Precisão.
O cálculo usa o nome mecânico da Melhoria, incluindo as opções
publicadas de Longe. Nas duas vagas de Restrição, o crédito
continua limitado ao menor entre o preço Leve, o gasto declarado
e o gasto elegível após os descontos.

Um cartão só com uma dessas Melhorias perde a devolução e pede
revisão. Guarda com Passo conserva o crédito de Guarda, dentro
do teto Leve, e a ficha pede revisão se o gasto declarado incluir
Passo. As escolhas, os textos e a declaração ficam na montagem.
Os efeitos próprios sem base publicada continuam sujeitos à
declaração de gasto interrompível.

## Entrega incremental

Geração `52bef8f75b425d85`. Foram comparadas 280.001 posições e os
metadados de 26 abas. Mudaram 753 fórmulas de DADOS_R53, em CK, CP
e FX, nos 251 contextos. EditorR53 e MONTAGENS conservaram o
mesmo conteúdo da PR80.

A primeira forma da expressão ultrapassou a capacidade do pacote.
A expressão final compara os nomes mecânicos com REGEXMATCH,
dentro da mesma regra de cálculo. O pacote ocupa cinco partes e
4.225.808 bytes em Base64, dentro da capacidade de 4.250.000
bytes. A margem medida é de 24.192 bytes.

`preparar_fragil_instantaneo.js` valida o Código da PR80 e exige
um retrato atual das 753 fórmulas. O plano escreve apenas
`userEnteredValue` e inclui reversão. O Código proposto troca
somente o bloco de moldes de recuperação, com a cobertura anterior
preservada. Os testes locais conferiram o transporte e a reversão
nos dois idiomas e a recuperação simulada dos alvos.

## Ensaio no Google Sheets

A versão compacta passou 15 cenários por descartável, Era e
Ciclo. Os seis feitiços instantâneos e a variante de Longe de
três degraus ficaram em REVISAR com devolução zero. Guarda e
Passo com 4 pontos declarados passou a pedir revisão e conservou
os 2 pontos de crédito financiados por Guarda. A declaração de
3 pontos ficou válida. Passaram também os controles de Precisão,
Guarda, Atrasar + Parado, Sangra e Barulho na Classe 0.

As seis fórmulas focais em CK2, CP2, FX2, CK41, CP41 e FX41 e as
21 entradas de ensaio foram repostas por cópia. A releitura de
624 células por descartável, incluindo 539 posições de MONTAGENS,
encontrou zero diferenças e zero erros. As duas cópias voltaram
à PR80. Evidências privadas em
`nuvem-b47/saidas/correcao-fragil-instantaneo/`.

O smoke local passou. A instalação integral e a recuperação por
edição real ficam para o ensaio de instalação desta geração.
