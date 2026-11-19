# Sem Volta e devoluções de Classe 0 · 06/11/2026

Base PR77 `fa2acaa`. Regra R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Diagnóstico em `AUDITORIA-SEM-VOLTA-CLASSE-ZERO-2026-11-06.md`.

Sem Volta pede revisão e deixa de devolver pontos em montagens com
benefícios garantidos reconhecidos pela ficha. A verificação considera
cura, PV temporários, Guarda, Impulso, Firmeza e Inescapável. A rota
estruturada também usa a resolução registrada para bloquear dano
automático e dano por TR que ainda ocorre no sucesso.

Nos cartões de descrição livre, a dependência pode ser declarada
com a linha exata `Sem Volta: pode falhar por completo` em COMO É,
quando todos os efeitos realmente dependem da resolução. A linha
só vale quando há dano ou uma peça de Controle que pode exigir TR.
Um feitiço exclusivamente de cura automática permanece inválido
mesmo com a declaração. A ficha usa a declaração explícita e os
campos estruturados disponíveis. A interpretação de outros detalhes
do texto livre continua a cargo de quem monta a ficha. A atualização
preserva as descrições existentes. Mesclas dependentes já salvas
podem precisar da linha para conservar a devolução.

Na Classe 0, Sobrecusto e Queima-Roupa em Projétil continuam
sinalizados como inválidos e deixam de aumentar o saldo.
Queima-Roupa em área permitida e Barulho conservam a devolução Leve.
Sobrecusto continua cobrando o adicional e devolvendo pontos nas
Classes que o permitem.

## Ensaio nativo

Passaram 18 cenários em cada descartável, Era e Ciclo. Foram
conferidas as duas posições de Sem Volta, cura e PV automáticos,
cura independente, mescla realmente dependente, ataque único e
os controles de Classe 0. Sobrecusto e Queima-Roupa em Projétil
mantiveram os 5d8 do controle. Barulho e Queima-Roupa em Explosão
continuaram em 6d8. Sobrecusto na Classe 3 mostrou 15 PE.

As seis fórmulas usadas no primeiro cartão comum e na primeira
vaga de Classe 0 foram comparadas com a geração final. As 21
entradas de teste e as seis fórmulas foram repostas. A releitura
de 622 células por cópia, incluindo 539 posições de MONTAGENS,
encontrou zero diferenças e zero erros. As descartáveis voltaram
à PR77. Evidências privadas em
`nuvem-b47/saidas/correcao-sem-volta/`.

## Entrega incremental

Geração `0e12da1540182de5`. Foram comparadas 280.001 posições e os
metadados de 26 abas. Somente 753 fórmulas de DADOS_R53 mudaram
nas colunas CK, CP e FX dos 251 contextos. EditorR53 e MONTAGENS
são idênticos à PR77.

`preparar_sem_volta.js` exige o Código ensaiado da PR77 e snapshot
atual das 753 fórmulas. Produz o Código proposto, o Código anterior
e os pedidos reversíveis de `userEnteredValue`. A preparação, a
reversão e a recuperação foram testadas localmente. No Google,
o ensaio foi focal nas seis fórmulas. A instalação integral e a
recuperação por edição real da nova geração ainda requerem ensaio.
