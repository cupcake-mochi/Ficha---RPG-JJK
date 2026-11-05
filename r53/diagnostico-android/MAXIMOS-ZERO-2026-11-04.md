# Máximo zero em reservas e ajustes ±

A00 e A08 foram tratados em ramo separado sobre a PR60 `eaab143`, que
passou pela revisão final e está pronta para revisão no GitHub.

Antes, um máximo igual a zero passava pela mesma regra de um máximo em
branco. A edição de TEMP de vida ou PE agora limita a reserva a zero
quando o máximo é explicitamente zero. O mínimo de 1 ainda se aplica
quando o máximo é positivo. A regra de Integridade TEMP continua reservada
para análise própria, conforme a auditoria de reservas. Os ajustes ±
respeitam o zero explícito no módulo e no atalho, e preservam o tratamento
de um máximo ausente. A04 e A07 envolvem outros caminhos de edição de TEMP.

O preparador offline agora produz Codigo.gs de SHA-256
`5b81e86d0d5f06d648d9ae91af23dfee435aa6b3aec57c677b15309a3f750cb8`.
A descartável nova veio da QA da PR60. O código anterior conferido nela era
`6aec0d0a…`. Após salvar e recarregar, o Codigo tinha o hash esperado e os
outros nove arquivos GS mantinham os hashes da base. Os máximos de teste
foram preparados pela API. Cada entrada abaixo disparou um onEdit real.

| Cenário | Resultado relido | Duração de onEdit |
| --- | --- | ---: |
| Vida máxima 0, digitar 9 em TEMP | TEMP 0 | 13,799 s |
| PE máximo 0, digitar 6 em TEMP | TEMP 0 | 12,188 s |
| Vida máxima e atual 0, digitar 5 em ± | Vida 0 e caixa vazia | 11,191 s |
| PE máximo e atual 0, digitar 5 em ± | PE 0 e caixa vazia | 10,650 s |
| Vida máxima 1, digitar 9 em TEMP | TEMP 1 | 16,095 s |
| PE máximo em branco, atual 0, digitar 5 em ± | PE 5 e caixa vazia | 11,608 s |

Os oito campos foram restaurados e relidos iguais, inclusive fórmulas e
vazios. O Google não pediu autorização. O patch permanece na descartável
deste lote. O ensaio nativo cobre as barras de vida e PE do personagem.
As rotas das 12 entidades e da Integridade foram verificadas localmente.

Passaram 627 verificações em 18 rotas locais, 24 verificações incrementais
com snapshots, 137 do pacote leve, 46/46 do diagnóstico de reservas e o
smoke portátil. Outros achados pendentes no pente-fino são A01, A02, A04,
A05, A06 e A07. Sem merge, edição de oficiais/jogador/PR31 ou acionadores
novos.
