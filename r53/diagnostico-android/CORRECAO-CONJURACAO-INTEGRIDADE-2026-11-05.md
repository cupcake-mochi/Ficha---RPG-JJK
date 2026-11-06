# Conjuração nos estágios de Integridade · 05/11/2026

Correção sobre a PR70 em `4324ad3`. A regra segue a R66
(`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, seção
Estágios de Integridade). Os limiares incluem a perda exata de metade e
três quartos da Integridade.

- No estágio 2, o resumo de execução soma 1 PE por Classe.
- No estágio 3, o acréscimo continua e o teto permanente é dividido
  por dois e arredondado para baixo. O mínimo é Classe 1 para quem já
  alcançou Classe 1. Acima do teto, o cartão indica a restrição.
- No estágio 4, os resumos de execução que exibiam custo mostram
  “Sem conjuração”. O indicador central registra o estágio de derrota.

O cálculo aparece em 36 cartões comuns, três Liberações, na Técnica
Máxima e no indicador central de Integridade. Os dois cartões gratuitos
de Classe 0 da PR70 conservam o comportamento anterior. O teto
permanente, o custo base, o orçamento, a validade, ANALISE e as entradas
de MONTAGENS conservam seu papel na preparação. A mudança atua no
resumo de execução do personagem. O desconto de PE e os cartões das
invocações ficam fora do escopo desta entrega.

## Ensaio

- Duas descartáveis nativas, Era e Ciclo. Passaram 12 cenários por
  cópia, incluindo limites, recuperação de Integridade, derrota,
  controle de piso, Liberação e Técnica Máxima.
- O feitiço comum de Classe 3 passou de 9 para 12 PE no estágio 2 e
  ficou acima do teto 1 no estágio 3. O de Classe 1 passou de 3 para
  4 PE e continuou dentro do teto 1. A recuperação restituiu o preço
  inicial. Nos trunfos, os exemplos passaram de 14 para 17 PE e de
  25 para 30 PE, ambos acima do teto 2 no estágio 3.
- `FICHA!D37` e `FICHA AMALDIÇOADA!D81` voltaram por edição real nas
  duas cópias, com as fórmulas novas. Código e Editor salvos e relidos
  integralmente em ambas.
- Entradas de ensaio restauradas. Na releitura de 209 células por cópia,
  incluindo 153 em MONTAGENS, as únicas diferenças previstas foram as
  41 fórmulas. Valores de entrada, notas e validações foram conferidos,
  com zero erros nativos nos intervalos relidos.
- Geração integral `78c44defd6fc1285`. Passaram os 95 checks do smoke
  local e dois complementares, além do replay do transporte sobre o
  snapshot privado da PR70. A aplicação nativa usou o delta incremental.
  Evidências privadas em `nuvem-b47/saidas/correcao-conjuracao-integridade/`.

## Entrega incremental

O gerador em `ficha-v01/conjuracao_integridade.py` emite o plano das 41
fórmulas. O preparador `preparar_conjuracao_integridade.js` exige os
hashes ensaiados de Código e Editor da PR70. Ele verifica o conteúdo
dos 251 contextos e permite apenas as 40 mudanças de recuperação.

Para uma promoção futura, primeiro obtenha um snapshot atualizado das
41 fórmulas com o idioma e os IDs de aba, além de Código e Editor
completos. Valide as três entradas no preparador antes de gravar. A
migração gera somente alterações de `userEnteredValue` para essas
fórmulas e dispõe de plano reverso. Se o estado divergir, prepare um
novo ensaio em cópia a partir da versão encontrada. Após aplicar,
releia as fórmulas e os arquivos, confirme a edição real e compare os
dados de montagem com o snapshot.

Hashes SHA-256 relidos na Era e no Ciclo:

- Código `6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8`.
- Editor `165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466`.
