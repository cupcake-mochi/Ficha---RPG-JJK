# Instalação incremental da PR82 nas descartáveis · 06/11/2026

A PR82 `b11c46a` estava aberta, sem conflitos e com os dois checks
aprovados. O teste local de transporte e reversão passou novamente.
A PR81 era a base confirmada nas duas descartáveis.

O preparador validou um retrato atual das 753 fórmulas de cada
cópia e gerou pedidos de aplicação e reversão. O Código anterior
foi arquivado. Código.gs foi salvo e relido nas duas cópias,
com SHA-256 `ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75`.
O hash do EditorR53 foi conferido antes e depois.

Foram instaladas e relidas 753 fórmulas em 22 lotes por cópia,
nas colunas CK, CP e FX de DADOS_R53. A releitura registrou zero
erros de fórmula e zero diferenças de nota ou validação.

| Cópia | Cartão comum | Classe 0 | Controle herdado da PR80 |
| --- | --- | --- | --- |
| Era | FX2 | CK252 | CZ2 |
| Ciclo | CP2 | FX253 | CZ2 |

As seis fórmulas apagadas pela interface voltaram idênticas à
proposta. O Apps Script registrou as seis execuções concluídas,
de 6,980 a 11,708 segundos.

DADOS_R53 voltou a ficar oculta e a faixa temporária de transporte
da Era voltou ao vazio. A releitura de 596 células por cópia,
incluindo 532 posições de MONTAGENS, encontrou zero diferenças
fora dos alvos da instalação.

## Controles com a PR82 instalada

Os seis cenários passaram na Era e no Ciclo. Salto instantâneo
e Maior num Cone instantâneo devolveram zero. Fica com Escolher
e Terreno com Maior conservaram 2 pontos de Frágil. Em Classe 0,
Sangra devolveu zero e Barulho devolveu 1 ponto.

As entradas temporárias foram repostas. A releitura de 624
células por cópia, incluindo 539 posições de MONTAGENS, encontrou
zero diferenças e zero erros. A PR82 está instalada nas duas
descartáveis. Evidências privadas em
`nuvem-b47/saidas/instalacao-fragil-catalogo/`.
