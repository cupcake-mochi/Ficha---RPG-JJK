# Parte 3c · desenho inicial aprovado

Aba nativa ESTUDO 3C, sheetId 47007, na cópia de revisão. Fonte: mockup/prototipo_custom_3c.py. É somente estudo: não alimenta CONFIGURAÇÃO, menus da ficha, contas nem ANALISE. O usuário aprovou o desenho inicial e autorizou o complemento de autonomia/limites com ajustes. Capacidade e custo gerais ainda não estão fechados.

## Decisões recebidas

- BASE DO LIVRO opcional para Formas, Melhorias, Restrições, aptidões, Talentos e tipos de entidade. Uma base herda as automações existentes; Nenhuma permite criar do zero com campos próprios.
- Famílias novas são acrescentadas às nove publicadas e contam nos mesmos limites. O usuário pediu que CONFIGURAÇÃO permita alterar as quantidades de Livres, Fechadas e Neutras.

## Desenho apresentado nesta rodada

Primeiro conjunto: Famílias e peças de feitiço. Aptidões/Bênçãos, Talentos, tipos/Talentos de entidade, condições e tipos de dano terão desenho próprio depois deste conjunto.

Proposta para o personagem: duas quantidades editáveis, Livres e Fechadas; Neutras = total de famílias disponíveis − Livres − Fechadas. Campo de campanha vazio usa 2 Livres e 3 Fechadas do catálogo. O livro tem nove famílias e, portanto, quatro Neutras; com a família ilustrativa, o total vai a dez e o saldo Neutras a cinco. A soma acima do total produz aviso. Os limites próprios das entidades permanecem; alterá-los também seria outra decisão de regra.

Família: nome, estado Livre/Neutra/Fechada, MESTRE VIU e descrição. A família ganha estado junto das nove existentes e entra nas listas das peças e entidades, sem substituir uma família publicada.

Forma: base opcional, família, peso, resolução, tipo de resultado, exigência de TR, disponibilidade na Classe 0, restrição embutida, alcance/área e texto de efeito/requisitos. O quadro explicita que personagem e entidade têm faixas de Classe diferentes. O detalhamento final ainda deve separar as bases de alcance e área; valores demonstrativos não são novas regras.

Melhoria: base opcional, família, peso, TR, requisitos/repetição e efeito. Restrição: base opcional, devolução Leve/Média, frequência e efeito/requisitos. Herança conserva as verificações específicas já existentes. Novas automações precisam de campos explícitos: não interpretar prosa nem silenciosamente tratar texto como regra calculável.

Formas, Melhorias e Restrições preencherão os menus e cartões existentes das aplicações. Não criar outro conjunto de feitiços, seguindo a orientação do usuário para o grupo 7.

## Inventário e orçamento em aberto

| Tipo | Posições independentes no gerador | Total |
|---|---|---:|
| Forma | 45 técnica + 12 × 13 entidades | 201 |
| Melhoria | 165 técnica + 12 × 52 entidades | 789 |
| Restrição | 83 técnica + 12 × 26 entidades | 395 |
| Família | 12 × 9 seleções nas entidades | 108 |

O catálogo de Famílias também é referenciado pelas Formas e Melhorias e pelos estados da técnica. Portanto, 108 seleções não fecha sozinho a capacidade necessária de um catálogo em que cada peça possa apontar para uma família diferente. Uma mesma definição pode ser reutilizada. Condições entram como opções de Melhoria no gerador; não existem outros treze campos diretos de condição a somar à contagem.

Outras posições levantadas: 12 aptidões/Bênçãos, 12 Talentos do personagem, 12 tipos de entidade, 132 Talentos de entidade e 156 tipos de dano. A soma do inventário, incluindo nove Famílias por entidade, é 1.817 seleções, não uma quantidade já aprovada de cartões. Revisar dependências de catálogo antes da proposta final de capacidade.

Não foi fechado orçamento nem gerado código de integração da 3c. O estudo tem 543 pedidos de desenho e aproximadamente 212 KB de JSON, que não representam o tamanho final dos .gs. A capacidade precisa de desenho de armazenamento, divisão abaixo de 900 KiB por .gs e medição nativa na descartável antes de ser fechada. Os 376.821 ms da montagem 3b não são previsão para a 3c.

## Validação do estudo

Oito lotes nativos aplicados somente na aba nova. Leitura de 24 controles, 129 notas e cinco fórmulas: zero erros de fórmula. Testes nativos de quantidades 4/1, excesso 10/3 e retirada da família de exemplo passaram; entradas do estudo restauradas. O exemplo final mostra 2 Livres, 3 Fechadas e 5 Neutras para dez famílias. Inspeção visual em 100% e visão de conjunto em 75%; corrigida uma quebra de texto na coluna CAMPANHA. Bordas dos moldes e do rodapé completas nas vistas inspecionadas.

Evidências em ../evidencias-3b/prototipo-3c-*. Fonte do estudo versionável; não importar XLSX no Google. Desenho inicial aprovado, incluindo Neutras calculadas. Aprovar o desenho não fecha capacidade ou custos ainda não medidos.


## Complemento aprovado · autonomia e nove espaços

Autonomia é individual em cada uma das 12 fichas de invocação, padrão Autônoma. CONFIGURAÇÃO permite ajustar limites de abertas/Livres por perfil de Trilha e o ganho adicional da Não autônoma; não existe escolha global de autonomia. Uma Livre nova também aumenta o total aberto em uma, sem conceder outra Aberta comum. Exige ordens prévias para ações, exceto Reação. É regra do sistema prevista para o futuro Guia de Criação, ainda não abordada no livro de regras atual.

O usuário aprovou seguir após ver o complemento em ESTUDO 3C, linhas 127–162, pedindo autonomia individual, nove espaços físicos e linha de respiro antes de DEFINIÇÃO. As cinco primeiras entradas mantêm seus endereços, as extras ficam na segunda fileira e DEFINIÇÃO desce só uma linha; habilidades ficam no lugar. A capacidade física não concede escolhas por si. Este complemento foi integrado e validado na revisão; os demais moldes e o orçamento geral da 3c continuam em aberto.


Validação encerrada: nove espaços e modo individual nas 12 entidades; tabela B133:G149; cinco cenários nativos e leitura de 108 rótulos passaram, com restauração completa. Fonte e notas do Guia de Criação conferidas. ANALISE7, 7485 chaves. A capacidade/custo geral do custom3c continua em aberto.
