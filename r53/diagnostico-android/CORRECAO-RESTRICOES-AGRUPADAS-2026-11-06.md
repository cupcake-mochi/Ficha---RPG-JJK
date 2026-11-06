# Crédito de Restrições agrupadas e de Classe 0 · 06/11/2026

Base PR79 `4118bb9`. Reprodução dos 15 casos em
`AUDITORIA-RESTRICOES-AGRUPADAS-2026-11-06.md`.
Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Atrasar perde seu crédito com Reação, e Aquecer perde seu
crédito com Remate. A Classe 0 bloqueia devoluções de peso
diferente de Leve, com as guardas já aplicadas para Sobrecusto
e Queima-Roupa em Projétil.

Em caso de duplicação ou par incompatível, o saldo provisório
usa o maior crédito elegível das duas vagas. A ordem das vagas
é irrelevante. O cartão continua em REVISAR e conserva as duas
escolhas salvas para o jogador decidir qual retirar. Restrições
independentes continuam somando. O crédito próprio de Toque e
os tetos de devolução continuam aplicados.

A regra de frequência usa a marca do catálogo, inclusive nas
Restrições Próprias. As confirmações por vaga continuam
determinando se cada crédito é elegível antes de calcular o total.

## Entrega incremental

Geração `a4a5a3cc3698c18a`. A comparação de 280.001 posições
e dos metadados de 26 abas encontrou 753 fórmulas diferentes.
Elas ficam em CK, CP e CZ de DADOS_R53, nos 251 contextos.
EditorR53 e MONTAGENS são idênticos à PR79.

`preparar_restricoes_agrupadas.js` exige snapshot atual das
753 fórmulas e o Código ensaiado da PR79. Gera a aplicação e
a reversão limitadas a `userEnteredValue`, além do Código novo
e da cópia anterior. Apenas o bloco de recuperação de Prática
Cotidiana é substituído. A recuperação agora inclui CZ e
conserva os alvos anteriores. Os testes locais conferiram as
753 fórmulas reconstruídas, a reversão em pt_BR e en_US e a
edição simulada de CZ com escrita única.

## Ensaio no Google Sheets

Passaram 25 cenários em cada descartável, Era e Ciclo. Os 15
casos da auditoria conservaram os avisos e perderam o crédito
indevido. Sangra, Atrasar, Carregar e Sem Volta em Classe 0
voltaram a mostrar 5d8 com Precisão. Barulho e Queima-Roupa em
Explosão conservaram 6d8 no mesmo controle. A troca da ordem
de Atrasar e Parado conservou o crédito provisório de 3.
Sangra e Barulho continuaram somando 5 pontos na Classe 3.

A primeira tentativa do Ciclo parou durante as leituras
iniciais. A releitura da base confirmou a reversão das fórmulas
temporárias, e a repetição completou os 25 cenários. As seis
fórmulas focais em CK2, CP2, CZ2, CK41, CP41 e CZ41 e as 21
entradas de ensaio foram repostas em cada cópia. A releitura
de 624 células por descartável, incluindo 539 posições de
MONTAGENS, encontrou zero diferenças e zero erros. As cópias
voltaram à PR79. Evidências privadas em
`nuvem-b47/saidas/correcao-restricoes-agrupadas/`.

O smoke local passou. A aplicação integral dos 753 alvos e a
recuperação por edição real desta geração ficam para o ensaio
de instalação. O ensaio nativo desta etapa verificou o cálculo
nas fórmulas focais e a reversão das alterações de teste.
