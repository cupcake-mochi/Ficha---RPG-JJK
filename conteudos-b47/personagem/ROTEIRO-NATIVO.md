# Roteiro nativo — execução pelo integrador

Este roteiro **não foi executado** nesta frente. Os testes de motor, modelo em memória e VM não substituem recálculo ou inspeção no Sheets.

## Preparar a combinação

1. Conciliar [CONTRATO-PROPOSTO.md](CONTRATO-PROPOSTO.md) com o contrato comum e a frente de entidades. Fechar os nomes dos auxiliares/arquivos e os campos de alcance/área, TIPO e avisos de uso. Usar as capacidades compartilhadas do contrato.
2. Incorporar os commits desta entrega no ramo do integrador. Rodar `python conteudos-b47/personagem/validar.py` com a venv preparada.
3. Revisar/aplicar os patches 01, 02 e 03 de `patches/base-7752c91/`, nessa ordem, para a integração `7752c9115f168effe74092d125dfdd5352bd44a3`. A série da raiz conserva a base inicial `ae16895967d23044f558f31638df23c0fbdd7598`. Escolher somente uma série. A fachada também permite chamar diretamente os módulos com outro contexto aprovado.
4. Fechar o FORMATO conjunto, esquema e formatos conhecidos do leitor. A base 7752c91 já publicou 11 inicial para dano/Condições; esta combinação ainda precisa conciliar os novos produtores. Os patches preservam a versão recebida.
5. Gerar as saídas canônicas uma vez, no ambiente do integrador, em série. Medir o tamanho **real** de cada GS e exigir menos de 900.000 bytes, inclusive Ficha/Configuração/Invocações após os novos controles e avisos. O fracionamento proposto para os dados de Formas não dispensa essa medição.
6. Executar os testes centrais pertinentes à combinação, incluindo carregamento/ausência de arquivo, compactação, leitor, nomes literais, grupos copiados e interações com Condições/Melhorias e entidades.

## Guardas e destino

Usar os destinos vigentes do plano central. Renovar snapshot/backup nativos e guardas; primeiro testar a combinação em descartável. Salvar e reler todos os GS e manifesto da geração nova. Construção integral somente na descartável reservada. Não importar XLSX no Google.

Os endereços do editor e avisos devem ser obtidos de `tr['registros']`, `tr['entradas']` e `tr['avisos_uso']` do modelo integrado, não de um endereço histórico. Guardar valores, notas, validações, alturas e demais metadados que o cenário alterará.

## Formas

1. Na primeira e na décima vaga, cadastrar nomes literais como `Forma *?~ inicial` e `Forma *?~ final`, com base do livro e demais campos vazios. Conferir nome, Família, peso, resolução, resultado, TR, Classe 0, embutida e alcance/área herdados. Comparar com uma aplicação do livro na mesma ficha/contexto.
2. Repetir a comparação para Projétil, Toque, Explosão, Aura, Cone, Linha, Cura, Apoio, Onda e Efeito. Cobrir feitiço, Liberação, Classe 0 e Técnica Máxima do personagem; básicas/especiais/escolhas da Trilha nas entidades.
3. Caso exato: Explosão de Classe 6 tem raio 4,5 m no personagem e 3 m na entidade; alcance 36 m em ambos. Na Classe 7 da entidade o raio passa a 4,5 m. Comparar o alias baseado no livro com esses mesmos resultados.
4. Testar Longe/Muito Longe e Maior/Muito Maior separadamente. Alterar a base de alcance sem alterar a área, e vice-versa. Verificar Cone Classe 0 de 3 m → 4,5 m no primeiro aumento de comprimento.
5. Criar Forma sem base com peso, resolução, resultado, TR/Classe 0 explícitos e bases próprias nos dois contextos. Nenhum número deve aparecer por ter sido mostrado no estudo. Uma segunda dimensão preenchida sobre uma base de um componente precisa aparecer separadamente.
6. Selecionar o mesmo cadastro em duas aplicações e nas 12 entidades. Família deve abrir somente onde consta nas nove posições da entidade; a classificação Livre da técnica não concede abertura nem desconto à Forma de entidade.
7. Conferir Corpo a Corpo embutida em Toque/Aura. Trocar por uma Restrição Leve e depois uma de frequência, inclusive custom válida. Testar duplicação com uma selecionada, duas de frequência, limite de duas e devolução que ultrapassa o gasto em Melhorias. A Forma continua sendo paga integralmente.
8. Base Cone/Linha renomeada continua recusando Corpo a Corpo. Tudo ou Nada exige TR, inclusive quando embutida. Uma resolução de ataque com TR explícito deve mostrar ambos; o seletor próprio da entidade continua tendo a precedência recebida.

## Aptidões/Bênçãos

1. Testar primeiras/últimas vagas com base e sem base. Selecionar a entrada nas cartas atuais e conferir Menu Rápido, requisito, CE e texto.
2. Uma entrada com CE vazia/— e escolha em branco custa uma escolha. Trocar para Gratuita custa zero; o orçamento disponível não aumenta. Limpar ESCOLHA volta à herança ou ao consumo padrão.
3. Uma base gratuita herda gratuidade, mas não se torna uma terceira capacidade inicial automática. As duas capacidades iniciais do livro continuam nos seus lugares próprios. Declarar consumo explicitamente sobre uma base gratuita precisa cobrar uma escolha.
4. Aptidão CE 3 sem requisito numérico adicional não ganha nível mínimo de Talento implicitamente. Bênção CE 2 exige Lapidação 4; CE 3 exige 7, sem aplicar os níveis 7/13 dos Talentos.
5. Energia Reversa exige Refino 7/nível 14; Circulação exige a aquisição anterior e Refino 8; a ordem inversa deve avisar. Aliases da mesma base não contornam repetição. As duas variantes de Aptidão/Bênção Própria continuam compartilhando a limitação de uma.
6. Verificar as concessões de criação com flags estruturados fornecidos pelo integrador. Conferir Domínio Simples com voto no Refino 4 e aprendizado registrado; Pétala, Cesta, Extensão e Ritual com suas alternativas. Sem fonte estruturada, a carta pede conferência manual e mantém o texto.
7. Bênção permanece na rota sem energia. Extensão conserva o bloqueio de origem/rota existente ou sua expressão explicitamente adaptada pelo integrador. Tipo incompatível com a base sai do catálogo.

## Talentos do personagem

1. Cadastrar primeira/última vaga, com base e sem base. Conferir CE, rota, requisitos e efeito nos cinco lugares pagos, nos sete do Leque e no Menu Rápido.
2. CE 1/2/3 ocupa 1/2/3 espaços quando pago e abre nos níveis 1/7/13. Leque custa zero espaços, mas exige a vaga existente liberada. Domínio, invocações e Regra Própria continuam no orçamento central.
3. Testar Fundamento/Manejos, Técnica Marcial e Sem Técnica. Uma seleção antiga que ficou incompatível precisa avisar na carta.
4. Texto como `ganhe +999` não altera atributo, dano ou PE. Requisitos textuais são mostrados para conferência; somente os campos estruturados alimentam contas.

## Negativos, limpeza e encerramento

1. Duplicar cada tipo, inclusive mudando só maiúsculas/minúsculas. Colidir com nome do livro. Ambos os custom duplicados saem do pool; o livro continua disponível.
2. Usar nomes distintos com `*`, `?` e `~`; eles não devem capturar vizinhos. Testar base de outro tipo, tipo colado incorreto, peso/CE/medida/checkbox inválido e registro parcial sem nome. Distinguir rejeição da validação estrita de um cadastro inválido já existente.
3. Limpar base, campos herdados e depois todo o cadastro. Conferir o retorno dos resultados e avisos e o desaparecimento das opções, sem sobras em todas as aplicações que o reutilizavam.
4. Testar textos longos nas duas cartas vizinhas e na décima de cada tipo. Apagar um lado conserva o outro; limpar ambos retorna ao piso de 25 px das linhas de texto. Conferir notas, bordas, menus, mesclas e o comportamento das cópias.
5. Auditar ANALISE inteira por chave. São 500 novas linhas de cadastro/aviso desta frente, mais os 24 avisos de uso se o callback proposto for adotado; o total conjunto depende das outras frentes. Cadastros inválidos continuam crus e com aviso. Campos textuais, inclusive `007`, devem preservar o literal.
6. Executar leitor da versão conjunta, varrer erros de fórmula e conferir GS/manifesto salvos/relidos. Construir cópia funcional na descartável e verificar os gatilhos sem ativação manual.
7. Restaurar todos os dados/notas/validações/alturas temporários e reler a igualdade. Registrar alvo, SHA da combinação, comandos, resultados e falhas com coordenada real. Só depois seguir o roteiro central de migração guardada da revisão.
