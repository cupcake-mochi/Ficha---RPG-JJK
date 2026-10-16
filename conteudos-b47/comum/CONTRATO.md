# Contrato inicial C+D B47

Base comum: `0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd`. Contrato estruturado em [contrato.json](contrato.json). Esta publicação inicia a preparação do integrador, não comprova conteúdo integrado nem aplicação no Google.

## Capacidades iniciais

O integrador adota dez cadastros compartilhados para cada novo tipo e vinte para Talentos de entidade. São 70 definições novas, reutilizáveis no personagem e nas 12 invocações. Vinte Talentos de entidade permitem variedade entre invocações sem reservar as 132 posições de uso como cadastros independentes. Dez Formas custom somam ao catálogo integral do livro, não limitam o total de aplicações conhecidas. Essa é a escolha inicial de implementação parametrizada dentro da estratégia pequena aprovada; rever com inventário/custo real antes de fechar a geração. Nenhum preenchimento pode ser descartado para acomodar capacidade.

Condições usam as mesmas 30 Melhorias: modalidade Melhoria/Condição, sem novos cartões. Condição usa Controle por padrão e exige TR; não permitir desligar a exigência com Não. Base opcional de Condição deve corresponder a uma condição publicada; preservar as regras da base. Sem base, peso explícito e texto descrevem a condição; nenhum texto produz números implicitamente.

## Interface e destinos

As listas de campos reproduzem os moldes aprovados. São nomes lógicos para intercâmbio, sem obrigar frentes que já começaram a reescrever sua API. Divergências devem ser declaradas no relatório para adaptação antes de incorporar.

- Módulo preferencial: `aplica(layout, contexto)`, com `fam`, `inv`, `criacao`, `pecas`, `capacidades` e `inicio` fornecidos pelo integrador. Um módulo pode consumir apenas os elementos necessários.
- Retorno: transformação com `antes`/`depois` por aba/célula, `entradas` como triplas chave/endereço/booleano, registros, catálogos e limites início/fim. `exporta(tr)` emite as quatro colunas ANALISE existentes.
- CONFIGURAÇÃO é o editor; fichas e invocações continuam os consumidores. Novas seções são acrescentadas depois do fim calculado da seção anterior. Não fixar linha global nem deslocar os campos existentes por conta própria. D pode reorganizar seções depois, com mapeamento explícito e preservação de entradas/notas.
- Os helpers do gerador usam fórmulas em inglês e referências citadas de aba. Faixas derivam do número de registros; espelhar livro em auxiliares ocultas e acrescentar somente custom válido. Não substituir o catálogo original por uma lista que perca exceções/identidade canônica.
- Campo vazio e Nenhuma na base significam sem base. Campo mecânico vazio herda apenas quando a base é válida. Zero/Não são valores explícitos; não usar truthiness para decidir herança. Categoria vazia/— não concede gratuidade. As entradas cruas são exportadas inclusive quando inválidas; o pool exclui inválidos e avisos explicam o motivo.
- Nome/efeito/requisitos/definição são texto literal, inclusive iniciando com `=` quando escritos como texto. MESTRE VIU é booleano e lembrete; não autoriza custom automaticamente.

## Exportação e integração

Reserva lógica: `custom.forma.N.*`, `custom.aptidao.N.*`, `custom.talento.N.*`, `custom.tipo_entidade.N.*`, `custom.talento_entidade.N.*`, `custom.dano.N.*` e `aviso.custom.<tipo>.N`. Condição acrescenta `custom.melhoria.N.modalidade`, sem redefinir as chaves existentes. N começa em 1 e conserva identidade.

Proposta de formato 11 para a combinação C: manter as chaves de v10 e acrescentar as novas, além da mudança de `formato.versao`. A versão só será marcada implementada quando produtores/leitor/contrato/testes concordarem. Cada entrega deve dizer que campos foram realmente integrados. Bot permanece externo: documentar compatibilidade pendente sem mexer nele.

Chat 2 responde por Formas nos dois contextos. Claude responde pelos tipos/Talentos de entidade e preserva autonomia/alma individuais. Integrador responde por dano/Condições, contrato, aplicação de patches e código canônico. Frentes podem entregar propostas distintas, mas não criar namespaces/endereço global conflitantes na produção. O integrador concilia antes de ligar o código.

## Checkpoint inicial do integrador

Windows, Python 3.12.14, Node 24.19.0, Git 2.56.0.windows.2. Checkout limpo no início, `codex/b47-capacidade` em `0d4d64e`; os dois ramos remotos confirmados nessa base. Ramos das frentes ainda não apareceram na consulta inicial; não significa que seus chats não estejam trabalhando.

Smoke com `PYTHONUTF8=1` passou: 152 fontes Python, 40 JS/GS e verificadores de catálogo/progressão/Kaori. Primeira tentativa sem UTF-8 falhou no verificador de catálogo; execução direta e smoke com a configuração Windows documentada passaram. Calc ausente; nenhuma conta local dependente de Calc foi declarada aprovada. GS existentes ainda não regenerados; nenhuma escrita Google nesta preparação.

Próximo passo: implementar dano/Condições com testes focais e conciliar as entregas externas. Recomendação de planejamento: GPT-6.1 Sol, High, para preservar referências e contrato durante integração.
