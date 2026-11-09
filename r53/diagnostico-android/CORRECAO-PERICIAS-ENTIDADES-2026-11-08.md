# Perícias válidas e distintas nas entidades · 08/11/2026

O resumo de perícias passou a contar escolhas válidas e distintas.
Atletismo repetido fica gravado nas duas linhas, ocupa uma vaga e acende
o aviso REPETIDA. Uma perícia custom retirada do catálogo mantém o nome,
deixa de ocupar vaga e recebe o aviso FORA DO CATÁLOGO. O aviso de limite
usa a quantidade válida distinta. Quando há mais de um problema, o
cabeçalho mostra os avisos juntos.

A nota de Ofício Compatível orienta a cadastrar um novo ofício em
CONFIGURAÇÃO e então escolhê-lo no menu. O campo conserva a validação
estrita e a ajuda sobre reparo.

## Alteração e aplicação nas descartáveis

O gerador reaproveita os bônus já calculados para identificar escolhas
que ainda resolvem no catálogo. A comparação dos nomes é literal e
segue a igualdade de texto do Sheets, que aceita diferença de caixa.
O limite segue usando a Inteligência base.

O delta tem 24 fórmulas em `DADOS_INVOC!GU2:GU13` e `HT2:HT13` e
uma nota em `INVOCAÇÕES!L42`. A comparação das fontes regeneradas
cobriu 280.056 posições em 26 abas. Confirmou o delta exato e a
preservação da estrutura, das fórmulas ANALISE e das validações.
Geração `8c985bea26747123`. O pacote local tem cinco partes e
SHA-256 `16a290ea799752a6de0625dfe9f7caf020e7b165008e5e442b65992771743bcb`.

Cada descartável recebeu 25 alterações em um único lote, com snapshot
fresco e releitura dos alvos. A aplicação alterou somente células e a
nota. O pacote integral foi regenerado para o Git e para os testes
locais. Os projetos Apps Script das cópias seguem com a instalação
anterior.

## Validação

Passaram 52 observações nativas em Era e Ciclo, distribuídas entre
as entidades 1 e 12. A matriz inclui as 23 perícias, os quatro TRs,
os degraus de Maestria, o limite por Inteligência, zero, bônus
negativos, escolhas válidas com o mesmo bônus e lacunas entre linhas.

O teste custom usou um nome com `~*?` e também a variante minúscula.
Conferiu retirada e reposição do cadastro sem mudar a seleção, além
do cabeçalho com repetição, escolha fora do catálogo e excesso ao
mesmo tempo. Na retirada o bônus sumiu. Na reposição voltou.

Pela interface nativa, Atletismo repetido ficou gravado e o cabeçalho
vermelho exibiu `⚠ PERÍCIAS · 3 DE 4 · REPETIDA` nas duas cópias.
Um ofício sintético cadastrado em CONFIGURAÇÃO foi aceito em ambas.
A Era aceitou a digitação. Na Ciclo a primeira digitação foi recusada,
mas a opção estava no menu e pôde ser escolhida normalmente.
As duas abas de teste foram fechadas.

Foram restauradas 63 entradas por cópia. A comparação de 86.494
posições em cada cópia inclui toda MONTAGENS `A1:I9543`, com 85.887
posições. Os únicos 25 campos diferentes são as fórmulas e a nota
do plano. Os metadados, incluindo formatação condicional, coincidem.
O cadastro temporário de ofício foi conferido à parte após restauração.

Passaram o teste do preparador e o smoke local. O preparador verifica
aplicação, reversão, repetição segura e recusa de alvos divergentes em
pt_BR e en_US. A validação em Sheets foi nativa em pt_BR. O Google
simplifica intervalos de uma célula na releitura. A comparação aceita
essa forma equivalente, preservando os demais caracteres da fórmula.

## Retomada

Ramo `codex/corrige-pericias-entidades-20261108`, empilhado sobre a PR90.
O plano é `pericias_entidades_delta.json` e a evidência sanitizada é
`pericias_entidades_validacao_2026-11-08.json`. Os snapshots e capturas
ficaram no diretório ignorado
`nuvem-b47/saidas/correcao-pericias-entidades-20261108/`.

Para reproduzir o delta, execute `preparar_pericias_entidades.js` com
a pasta GS anterior, a pasta nova e o destino JSON. O preparador local
gera pedidos com `pedidos(delta, snapshot)` e pedidos de reversão com
o terceiro argumento `true`. O snapshot precisa conter a localidade,
os IDs de abas e o conteúdo atual de todos os alvos. A aplicação desta
rodada foi restrita às duas descartáveis.
