# Parte 3b · estudo para aprovação

A parte 3a foi testada pelo agente a pedido do usuário. Teste focal nativo na cópia de revisão: Defesa 20, Proteção 7, deslocamento 4,5 m, volumes 3 e 2,1, troca por zero, rota sem energia com 50 PE, restrição da marcante herdada, ferramenta com volume zero e menor com texto próprio. Nome duplicado invalida os dois cadastros. As 156 entradas temporárias foram restauradas e relidas, sem diferenças; 13 abas/17 faixas ficaram sem erros de fórmula.

Protótipo: [ESTUDO 3B](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit?gid=47005). É uma aba de estudo; não alimenta a ficha ou ANALISE. Não altera as abas de produção.

## Moldes propostos

- Caminho: vida inicial, vida por nível, dado da variante de vida rolada, PE por nível; até dois atributos naturais e duas perícias fixas; permissão da troca de duas perícias por categoria de arma; treino de todas as categorias ou lista de categorias. Opções fechadas em menus. Números do exemplo seguem a Vanguarda, não uma regra nova.
- Trilha: nome e Caminho vinculado, lido do livro mais o Caminho custom. Cada rota com funcionamento diferente tem um nome no menu, como já acontece com Batedor. Escolhas mecânicas específicas ainda precisam de levantamento antes da integração.
- Caminho e Trilha têm nome e texto por nível, de 1 a 30. Vazio não concede habilidade. O nível 1 permite registrar campanhas que o usem; não muda o nível inicial da campanha. Os níveis 6–20 ficam num grupo e os níveis altos noutro; o título do 21 fica visível como referência. O texto não é interpretado como fórmula.
- Perícia/Ofício: molde curto com tipo, nome, atributo (fixo para perícia; padrão para ofício), MESTRE VIU e descrição. O título e o rótulo do atributo mudam por fórmula quando o tipo muda. São os cinco atributos do sistema, incluindo Constituição.
- Na FICHA, proposta de linhas próprias para perícias/ofícios custom com treino, especialização e resultado. Elas entram nas contas existentes sem aumentar as escolhas concedidas. Preservar posições antigas e chaves do contrato é requisito da integração.

## Capacidade: conta corrigida

A primeira estimativa de 36 registros considerou apenas os catálogos do personagem. Ela foi substituída antes da construção porque não cobria criações distintas em todas as posições das entidades.

| Tipo | Posições independentes a cobrir | Registros propostos |
|---|---|---:|
| Caminho | Uma escolha do personagem | 1 |
| Trilha | Uma escolha do personagem | 1 |
| Perícia | 23 da FICHA + 12 entidades × 7 posições + 1 da FICHA AMALDIÇOADA | 108 |
| Ofício | 11 da FICHA + 12 entidades × 1 posição | 23 |
| Total da 3b | 2 cartões longos + 131 curtos | 133 |

Com os 25 da 3a: 158 registros propostos. Um cadastro pode ser reutilizado em vários lugares; a conta acima permite nomes diferentes em todos os lugares. Os 36 seletores de Classe da escolha de Trilha das entidades são controles numéricos, não definições de Trilha do personagem; não contam como registros. O inventário inicial os classificava por conter a palavra Trilha, por isso não usar a soma bruta dos menus como capacidade.

Perícias e ofícios das entidades precisam receber livro + custom nesta parte. Tipos de entidade e Talentos continuam na 3c. Também integrar as listas de perícia/ofício usadas pela Origem custom, Caminho e opções de capacidade, sem criar escolhas extras.

## Geometria e custo

Na CONFIGURAÇÃO, a proposta é colocar os novos cartões abaixo do cartão 25 da 3a. Dois cartões longos para Caminho/Trilha e um molde curto compartilhado por Perícia/Ofício evitam multiplicar a progressão por todos os registros. Não mexer na altura dos cartões da 3a nem fechar linhas que escondam bônus/campanha.

O estudo contém quatro exemplos, 29 controles validados e grupos retráteis. Os pedidos de desenho não medem o custo de produção. A quantidade final depende de gerar a integração, manter cada .gs abaixo de 900 KiB e medir construir() nativamente em cópia descartável. Distribuir dados e desenho em arquivos novos se necessário; não substituir medição real por tamanho do protótipo.

## Verificação e próximo passo

Conferidos visualmente os painéis de Caminho, Trilha, progressão e os moldes curtos. Os 29 controles existem, os dois grupos foram relidos da estrutura nativa e a troca Perícia→Ofício atualizou título e atributo; exemplo restaurado. Evidências fora do Git em evidencias-custom/teste-delegado-3a.json e prototipo-3b-*.png.

Aguardando aprovação do desenho, como pede o PROMPT-CHATGPT-CONFIGURACAO.md. Pergunta atual considera 133 registros; a pergunta anterior com 36 está superada. Não iniciar código de produção da 3b sem esse ok. Antes de integrar, mapear os campos particulares das Trilhas e a relação entre progressão textual e efeitos numéricos já automatizados, perguntando ao usuário se houver nova decisão de regra.
