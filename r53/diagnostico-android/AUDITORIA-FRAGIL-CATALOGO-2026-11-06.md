# Instalação da PR81 e auditoria de Frágil · 06/11/2026

## PR81 nas descartáveis

A PR81 `bfe00a5` estava sem conflitos e com os dois checks aprovados.
O teste de transporte e reversão passou novamente. Foram arquivados
o Código da PR80 e as 753 fórmulas atuais por descartável antes da
instalação.

O Código.gs salvo e relido em cada cópia corresponde ao SHA-256
`e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f`.
O EditorR53 conservou o hash anterior.

Foram instaladas e relidas 753 fórmulas em 22 lotes por cópia,
nas colunas CK, CP e FX de DADOS_R53. A releitura registrou zero
erros de fórmula e zero diferenças de nota ou validação.

| Cópia | Cartão comum | Classe 0 | Controle herdado da PR80 |
| --- | --- | --- | --- |
| Era | FX2 | CK252 | CZ2 |
| Ciclo | CP2 | FX253 | CZ2 |

As seis fórmulas apagadas pela interface voltaram idênticas à
proposta. O Apps Script registrou as seis execuções concluídas,
de 6,373 a 18,481 segundos. Esses tempos cobrem apenas as
execuções ensaiadas.

DADOS_R53 voltou a ficar oculta e o intervalo temporário de
transporte da Era voltou ao vazio. A releitura de 596 células
por cópia, incluindo 532 posições de MONTAGENS, confirmou zero
diferenças fora dos alvos da instalação.

## Pente-fino de Frágil

Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Nos 14 casos abaixo, o feitiço foi montado para terminar na própria
resolução. Cada cartão tinha uma única Melhoria, 2 pontos declarados
no campo de gasto interrompível e Frágil em uma das duas vagas.
Em cada descartável, o cartão ficou VÁLIDO, sem aviso, e recebeu
2 pontos de crédito.

| Parte da montagem | Melhorias ensaiadas |
| --- | --- |
| Dano | Salto, Estilhaço, Quebra Coisa, Rasga Escudo |
| Tempo | Rápido, Reação, Silencioso |
| Mira e alcance | Sem Ver, Fura, Sem Cobertura, Perseguir |
| Cone de dano instantâneo | Maior de um degrau, Escolher, Contorno |

A regra vigente calcula o teto de Frágil pela soma do custo pago
das Melhorias que ficam fora da lista de exclusões em
`r53/modelo.py`. As 14 Melhorias testadas ficam fora dessa lista
desde a PR80. A reprodução de Maior, Escolher e Contorno se
refere a uma área que termina de imediato. Os ensaios deixam
em aberto o tratamento de combinações com uma área persistente.

Os controles em Classe 3 confirmaram zero crédito com Passo,
já coberto pela PR81, e 2 pontos com Guarda ou Fica em montagens
com efeito interrompível. Em Classe 0, Sangra devolveu zero e
Barulho devolveu 1.

Foram 19 cenários por cópia. As 21 entradas de teste foram
repostas. A releitura de 624 células por descartável, incluindo
539 posições de MONTAGENS, encontrou zero diferenças e zero erros.
A PR81 está instalada nas duas descartáveis. Evidências privadas em
`nuvem-b47/saidas/instalacao-fragil-instantaneo/`.
