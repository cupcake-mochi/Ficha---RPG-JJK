# Parte 3b · integrada e validada na cópia de revisão

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

Desenho e capacidade de 133 registros aprovados pelo usuário em 15/10/2026 ("Ok, pode seguir"). Categorias significa categorias de arma; o rótulo passa a CATEGORIA DE ARMA. Também aprovada BASE DO LIVRO opcional para Trilha: uma base existente herda suas automações; Nenhuma cria do zero, com habilidades próprias e alterações numéricas em BÔNUS E MUDANÇAS. Não interpretar prosa para conceder benefícios.

Integração e capacidade fechadas em 15/10/2026. Os 133 registros novos estão na cópia de revisão, abaixo da 3a; as posições anteriores foram preservadas. CONFIGURAÇÃO mantém Mizuki Escuro; os novos blocos da FICHA acompanham a paleta atual. Textos longos expandem os dois cartões que compartilham linhas e o espelho da FICHA.

## Medição e validação da integração

- Treze scripts vinculados conferidos após gravação e recarga; maior: Configuracao.gs, **837.710 bytes**, abaixo de 900 KiB.
- Montagem real na cópia descartável da base: **188.812 + 188.009 = 376.821 ms (6 min 16,8 s)**, em duas execuções concluídas. Houve uma tentativa inicial com falha do serviço Planilhas na criação das abas, registrada separadamente; não entra no tempo das etapas concluídas. CONFIGURAÇÃO: 29,1 s; menus: 58,9 s; ANALISE: 24 s.
- A ficha construída tem 14 abas, ANALISE 6 com 7.387 chaves únicas, 188 checkboxes e 488 seletores na CONFIGURAÇÃO (575 células validadas, porque três seletores cobrem 30 linhas). Auditoria da revisão e da montagem descartável: zero erros de fórmula nas faixas conferidas.
- Cenários nativos: vida/PE 49/35; vida rolada 45 e dado excessivo rejeitado; perícia e especialização; troca por zero; Trilha herdada 4/4 e própria com efeitos 5/5; duplicatas e valores inválidos; seleção de Caminho marcando perícias fixas e somente categoria Yumi; menus nas entidades e Ficha Amaldiçoada.
- As 76 entradas do cenário, três entradas das entidades/técnica e seis mudanças auxiliares do gatilho foram restauradas. Todas as entradas e fórmulas das áreas novas foram comparadas com o gerador; um resíduo do teste visual em B781 foi removido e o nível 2 restaurado. Paleta: 4.647 âncoras/células independentes conferidas, cobrindo o retângulo de 9.350 células com suas mesclagens, sem divergências.
- Regressões de progressão (calculadora e contrato), construção completa simulada e expansão de texto passaram. Snapshot de comparação 3a versionado em ficha-v01/progressao-base3a.json.gz e conferido contra 03a459e. O teste gera seu pacote atual e não depende de evidências prévias para executar. Entrou no rodar-tudo.sh como 23º validador.
- A regressão antiga 3a apresentou uma falha local de FILTER no LibreOffice 24.2 para a marcante publicada da base Latente; CP3 permaneceu idêntica à 3a e o cenário passou nativamente no Sheets. O teste não foi enfraquecido. A bateria integral de 23 validadores e o arnês pessoal longo não foram repetidos nesta rodada.

O arquivo temporário MedicaoProgressao.gs foi removido, com ausência confirmada após recarga. Permanecem no Codigo.gs logs de duração das etapas do gatilho, sem o conteúdo do personagem. Oficial, bot e compartilhamento intactos. A parte 3c continua separada: levantamento/protótipo antes da construção. Evidências em ../evidencias-3b/.


### Validação final do gatilho e restauração

A seleção real de Vanguarda concluiu em **13,690 s**, marcando as 65 caixas de treino. A volta ao Caminho custom concluiu em **15,051 s**, mantendo somente os três checks de Yumi e preenchendo/treinando a perícia custom fixa. Corrigida a lentidão de check/uncheck sobre RangeList com gravação booleana em lote, além das leituras/notas agrupadas. O código inteiro foi conferido após salvar e recarregar. A regressão completa de construção passou com a mudança.

Ao retirar o cenário, comparadas todas as entradas e notas da FICHA/FICHA PESSOAL e os 76 alvos originais: **zero diferenças**. Áreas novas sem erros de fórmula. Evidências: tempos-onedit-final-completo.txt, fechamento-3b-gatilho.json, regressao-construir-treinos-final.log e capturas visual-*-3b-entrega.png em ../evidencias-3b/.
