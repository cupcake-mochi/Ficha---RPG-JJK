# Requisito de Família de Corrói · 07/11/2026

O pente-fino continuou após a instalação e a recuperação nativa
da PR83. A referência foi a R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, entrada
Corrói do catálogo, que exige Mira como Família Livre.

## Erro confirmado

Corrói passou como VÁLIDO, sem aviso, com Mira Neutra. A reprodução
usou um cartão comum de Classe 3, nível 30, Projétil, 2d8 de dano
e apenas Corrói, sem Restrições. O saldo era 4, com crédito zero.
Isso permite aprovar uma compra cujo requisito de Família falta.

| Família | Compra | Resultado esperado | Era e Ciclo |
| --- | --- | --- | --- |
| Mira Neutra | Corrói na vaga 1 | Revisar requisito de Mira Livre | VÁLIDO, sem aviso |
| Mira Neutra | Corrói na vaga 4 | Revisar requisito de Mira Livre | VÁLIDO, sem aviso |
| Mira Livre | Corrói na vaga 1 | Válido | VÁLIDO, sem aviso |
| Mira Livre | Corrói na vaga 4 | Válido | VÁLIDO, sem aviso |
| Mira Fechada | Corrói na vaga 1 | Revisar | REVISAR, Família Fechada |
| Mira Neutra | Fura na vaga 1 | Válido | VÁLIDO, sem aviso |

O avaliador local confirmou o mesmo problema no modo estruturado
e no registro direto, em 12 controles de Corrói e Fura com Mira
Neutra, Livre e Fechada. A árvore em `r53/modelo.py` confere o
acesso a Famílias Fechadas e calcula o desconto de Família Livre,
mas falta o requisito exclusivo de Corrói.

## Escopo do ensaio

Foram seis cenários de requisito de Família e seis controles da
PR83 por descartável. Os seis controles da PR83 passaram nas duas.
As 18 entradas temporárias, incluindo o estado de Mira e as quatro
vagas de Melhoria, foram repostas. A releitura após a restauração
encontrou zero diferenças e zero erros nos intervalos conferidos.

A comparação com o snapshot anterior à instalação cobriu 861
posições por cópia, incluindo 539 de MONTAGENS, também sem
diferenças ou erros. As descartáveis permanecem com a PR83 e a
aba DADOS_R53 oculta.

Este registro documenta o erro de Corrói para correção própria.
A cobertura nativa desta rodada foi de cartões pessoais. O
requisito nas entidades ainda requer ensaio nativo.

Evidências privadas em
`nuvem-b47/saidas/instalacao-forma-funcao/`.
