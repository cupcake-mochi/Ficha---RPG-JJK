# Devoluções de Queima-Roupa e Tempo · 06/11/2026

Base PR78 `262e264`. Reproduções em
`AUDITORIA-DEVOLUCOES-INCOMPATIVEIS-2026-11-06.md`. Regra R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

A Restrição incompatível perde seu crédito em qualquer das duas
vagas. Queima-Roupa é bloqueada em Toque, Aura, uso exclusivamente
pessoal e com Longe. Atrasar com Rápido, Parado com Reação e
Carregar com Armado também deixam de devolver pontos.

Os avisos de incompatibilidade são preservados. A devolução
própria de Toque e o crédito de outra Restrição válida continuam
no cálculo, sujeitos ao teto da montagem. O custo das Melhorias,
as escolhas, os textos e o armazenamento das montagens permanecem
iguais.

## Entrega incremental

Geração `d83d3c969a6469cb`. A comparação de 280.001 posições
e dos metadados de 26 abas confirmou alterações somente em 502
fórmulas, nas colunas CK e CP de DADOS_R53, para os 251 contextos
da entrega. EditorR53 e MONTAGENS são idênticos à PR78.

`preparar_devolucoes_incompativeis.js` exige um snapshot atual das
502 fórmulas e o Código ensaiado da PR78. Gera pedidos limitados
a `userEnteredValue`, o Código proposto e os arquivos de reversão.
O bloco de recuperação inclui as fórmulas novas e as fórmulas de
montagem já atendidas pela PR78. O teste local confere as 502
fórmulas reconstruídas pelo bloco e testa as guardas e a reversão
em pt_BR e en_US.

## Ensaio nativo

Passaram 20 cenários por descartável, Era e Ciclo. Os sete casos
inválidos conservaram os avisos e perderam o crédito indevido.
Toque conservou 2 pontos, e Barulho conservou 2 quando combinado
com Queima-Roupa inválido em Aura. Os controles de Tempo, Sem
Volta e Classe 0 passaram. A leitura de resultados retornou zero
erros de fórmula.

As quatro fórmulas focais de DADOS_R53, em CK2, CP2, CK41 e CP41,
e as 21 entradas temporárias foram repostas. A comparação de
622 células por cópia, incluindo 539 posições de MONTAGENS,
encontrou zero diferenças. As duas descartáveis voltaram à PR78.
Evidências privadas em
`nuvem-b47/saidas/correcao-devolucoes-incompativeis/`.

O smoke local passou. A aplicação integral dos 502 alvos e a
recuperação por edição real da geração nova ficam para o ensaio
de instalação. O teste nativo desta entrega verificou o cálculo
nas fórmulas focais e a reversão das alterações de ensaio.
