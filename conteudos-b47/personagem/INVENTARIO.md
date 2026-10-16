# Produtores, consumidores e exceções conferidos

Base de código do inventário: `ae16895967d23044f558f31638df23c0fbdd7598`.
Foram lidos os planos vigentes, estudo/protótipos 3c, contrato ANALISE, checkpoint PC e R52 textual. O catálogo executável permanece o recebido; não foi substituído silenciosamente pelo texto R52.

| Grupo | Produtor recebido | Consumidores efetivos | Ponte desta entrega |
|---|---|---|---|
| Formas | `catalogo-projeto-m.json`, `tecnica-do-livro.json`, `ficha_amaldicoada.regras` | Feitiços, Liberações, Classe 0 e Técnica Máxima; 45 escolhas | Tabela de 15 colunas, menus normal/Classe 0, três faixas de alcance |
| Formas de entidade | `invocacao-do-livro.json`, `ficha_invocacoes.regras` | Básicas, especiais e escolhas da Trilha; 13 × 12 = 156 | Tabela de 11 colunas, quatro faixas, dois menus por entidade e nove Famílias próprias |
| Aptidões/Bênçãos | `ficha_amaldicoada.regras`, progressão de Refino/Lapidação | 12 cartas; resumo de compras; Menu Rápido e iniciais automáticas | Tabela de dez colunas, consumo individual, requisitos e avisos nas cartas |
| Talentos do personagem | Catálogos Fundamento/Marcial normalizados | Cinco cartas pagas, sete do Leque, orçamento e Menu Rápido | Tabela de sete colunas, custo/CE/rota e avisos nos lugares existentes |

As referências de catálogo são reescritas com Tokenizer no layout inteiro, incluindo fórmulas do Menu Rápido já produzidas antes desta etapa. As tabelas originais do livro continuam como referência. Não são criados feitiços ou cartas de resultado adicionais.

Fontes de consumo conferidas: `ficha-v01/ficha_amaldicoada.py` (regras/trocas/Classe 0/TM/cartas), `ficha-v01/ficha_invocacoes.py` (regras/trocas/menuf/cartas), `ficha-v01/menu_rapido.py`, `custom_criacao.py`, `custom_pecas.py`, `familias_invocacao.py`, `ficha_automatica.py` e `analise.py`. O contador antigo da FICHA é redirecionado pelo Menu Rápido para a conta atual da amaldiçoada; o módulo altera essa conta atual.

Os objetos de menu são menos numerosos que as posições finais: o gerador copia validações junto com os blocos de cartas. Os testes preservam os destinos dos menus originais e auditam as 45 + 156 posições nos metadados, sem chamar essa contagem de prova nativa das cópias.

## Exceções preservadas

- Explosão/Aura: aumento de área do personagem já na Classe 6; na entidade só na Classe 7. Cone/Linha também conservam suas bases distintas.
- Cone Classe 0 parte de 3 m, abaixo do primeiro degrau de comprimento. A subida respeita esse degrau intermediário e satura no topo.
- Toque/Aura herdam Corpo a Corpo embutida. Uma embutida diferente usa sua própria devolução/frequência; restrição nunca paga Forma.
- Onda conserva o resultado e a indisponibilidade de Classe 0 recebidos. Cura, Apoio e Efeito mantêm tipos de resultado próprios; nenhuma descrição é transformada em bônus.
- Família Livre da técnica não abre nem barateia uma Forma de entidade. Valem as aberturas da própria invocação.
- Energia Reversa, Circulação, Regravação, Kokusen, Cesta, Domínio Simples, Pétala, Extensão e Ritual conservam requisitos nomeados. Concessões de criação são explícitas no contexto.
- Bênçãos conservam Lapidação e requisitos de atributo, incluindo a alternativa Força/Destreza de Represália.
- Gratuidade das duas iniciais é distinta da gratuidade de uma entrada custom selecionada. CE ausente não concede gratuidade.
- Textos de Talentos como Reserva Profunda continuam descritivos onde o núcleo recebido já os tratava assim; o módulo não cria automação numérica pela prosa.

## Limites de responsabilidade

Tipos/Talentos de entidade pertencem à outra frente. Tipos de dano e Condições pertencem ao integrador. Não há novos cadastros para Kata/Manejo/missão nesta entrega: os conteúdos usam os consumidores e rotas já existentes. O motor cobre Formas das entidades, não seus Talentos.

Desenho seguido: cartões B:G e J:O, rótulos, base opcional, notas e textos no molde aprovado. A grade definitiva de D, retirada de estudos, migração preenchida, contrato final e geração GS pertencem ao integrador.
