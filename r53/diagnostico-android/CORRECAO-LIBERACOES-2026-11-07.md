# Liberações Máximas por nível de aquisição · 07/11/2026

A correção parte da PR84 `74d83b7` e da auditoria registrada em
`37b9af5`, no ramo `codex/auditoria-liberacoes-20261107`.
A R66 do livro, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
recebe a primeira Liberação no nível 10, a segunda no 20 e a terceira no 30.

## Comportamento

Cada cartão pessoal passa a incorporar seu requisito de aquisição.
Antes do nível exigido, o estado é REVISAR e o aviso informa a posição
e o nível mínimo. Ao atingir o nível, esse aviso desaparece. Reduzir o
nível volta a pedir revisão e conserva a montagem preenchida.

O gerador usa os requisitos de contexto já existentes nos trunfos das
entidades. A mesma função emite o aviso no editor estruturado e nos
cartões diretos. Os requisitos das entidades mantêm suas expressões.
O avaliador isolado de peças continua separado dos avisos contextuais
de aquisição. Os testes locais conferem a emissão desses requisitos;
a aprovação completa foi ensaiada no Google Sheets.

O resultado usa os avisos existentes de DADOS_R53 e alimenta os estados
e a ANALISE pelos vínculos atuais. Permanecem ativos os avisos de Classe
mínima 3, preparação e mudança de identidade numa Ampliação.

## Artefatos e atualização incremental

Geração `913e7d60d156ef11`. A comparação de 280.001 posições e dos
metadados de 26 abas encontrou mudanças de conteúdo somente em
DADOS_R53!GA38:GA40. EditorR53, entradas e versões de MONTAGENS mantêm
sua representação. O transporte atualiza também os moldes de recuperação
e as duas guardas que admitem esses alvos.

`preparar_liberacoes.js` exige o Código incremental ensaiado da PR84,
com SHA-256 `da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e`,
e snapshot atual das três células. Recusa valores anteriores divergentes,
alvos incompletos ou duplicados, código incompatível e reaplicação.
Emite os três pedidos de escrita, a reversão e o Código proposto.
O ensaio local conferiu pt_BR e en_US, preservação do restante do Código,
recuperação das três fórmulas, colagem parcial e os alvos legados.

Para atualizar uma ficha existente, encadear as correções até a base
ensaiada, guardar snapshot novo das fórmulas e do código, preparar e
revisar o delta, aplicar em cópia e reler antes de qualquer promoção.
Não usar construção ou continuação da construção numa ficha preenchida.

O pacote integral foi regenerado e validado, com cinco partes e
4.249.696 bytes em Base64, margem de 304 bytes da reserva atual.
A aplicação nativa desta etapa foi incremental.

## Ensaios nas duas descartáveis

Era e Ciclo receberam as três fórmulas e o Código incremental após
snapshots atuais. O código foi salvo, recarregado e relido integralmente
nas duas, com SHA-256
`7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7`.

Passaram 39 cenários por cópia.

| Escopo | Cenários por cópia | Resultado |
| --- | --- | --- |
| Três posições nos níveis 9, 10, 19, 20, 29 e 30 | 18 | Nove posições bloqueadas e nove aprovações legítimas. Montagens de Classe 3 conservaram 12d8 e 14 PE. |
| Redução de nível após preparar as três | 3 | Todas voltaram a REVISAR, com compras conservadas. |
| Classe mínima, preparação, Ampliação e cartões vazios | 12 | Avisos legítimos preservados e cartões vazios sem estado de aprovação. |
| Nível insuficiente junto de Classe mínima ou preparação | 6 | Os dois avisos apareceram juntos em cada cartão. |

As três fórmulas foram apagadas juntas pela interface do Sheets em
cada cópia. Voltaram idênticas às propostas. Os dois onEdit terminaram
como Concluído, com 6,174 s na Era e 10,850 s no Ciclo. Esses valores
são a duração de execução registrada pelo Apps Script.

A conferência visual no nível 19 mostrou a primeira Liberação válida
e a segunda em revisão com o requisito de nível 20, sem cortar o aviso.
Os grupos abertos para conferir foram recolhidos depois.

Foram restauradas as 58 entradas temporárias. A comparação de 1.118
posições por cópia, incluindo 777 de MONTAGENS, encontrou zero diferenças
e zero erros nos intervalos conferidos. A conferência final com as três
células adicionais cobriu 1.121 posições e encontrou somente o delta
previsto, com notas e validações dos alvos preservadas. DADOS_R53 voltou
a ficar oculta. A correção permanece instalada nas duas descartáveis.

Passaram o smoke local, os testes focais de requisitos e Corrói, e o
teste de transporte e recuperação. Evidências privadas, snapshots e
capturas em `nuvem-b47/saidas/correcao-liberacoes/`, fora do Git.
