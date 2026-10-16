# Entidades C+D · contrato proposto e divergências

Frente Claude: Tipos de entidade e Talentos de entidade custom. Contrato comum de referência:
[conteudos-b47/comum/contrato.json](../../conteudos-b47/comum/contrato.json), revisão 1 (`ae16895`).
Nada aqui é decisão final. Versão ANALISE, namespaces de produção e endereços são do integrador.

## O que segue o contrato comum sem divergência

| Item | Contrato | Entrega |
|---|---|---|
| Capacidades | `tipo_entidade` 10, `talento_entidade` 20 | `TIPOS, TALENTOS = 10, 20`; parâmetros via `contexto['capacidades']` |
| Campos de tipo | `nome, mestre_viu, base, vida, talisma, reserva_pe, definicao, efeito` | mesma ordem e nomes (`CAMPOS['tipo']`) |
| Campos de talento | `nome, mestre_viu, base, categoria, requisitos, efeito` | idem (`CAMPOS['talento']`) |
| Opções | vida `Normal da entidade/Corpo de criação`; talismã `Não usa/Usa`; reserva `Normal da entidade/Maldição domada`; categoria `1/2/3` | listas fechadas na aba oculta, menus estritos |
| Interface | `aplica(layout, contexto)`; `exporta(tr)` com 4 colunas | `aplica(layout, {'inv', 'fam', 'criacao', 'capacidades'?, 'inicio'?})` |
| Transformação | `antes, depois, entradas, registros, catalogos, inicio, fim` | todas presentes; `entradas` = `[chave, A1 da CONFIGURAÇÃO, booleano]` |
| Chaves | `custom.{tipo}.{N}.{campo}`, `aviso.custom.{tipo}.{N}`, N 1-based fixo | `custom.tipo_entidade.N.*`, `custom.talento_entidade.N.*`, `aviso.custom.tipo_entidade.N`, `aviso.custom.talento_entidade.N` |
| Base | vazio ou `Nenhuma` = sem base; vazio herda só com base válida; `Não`/explícito sobrescreve | idem; nada usa truthiness (`"Não usa"` sobrescreve base que usa talismã) |
| Cadastro vazio | sem aviso só com padrões e MESTRE VIU falso | idem (teste A) |
| Parcial | preservar e avisar nome ausente | `Preencha NOME`; o cadastro cru continua exportado |
| Duplicata | todos os nomes duplicados fora do pool, inclusive colisão com livro | todos os custom repetidos (sem diferenciar maiúsculas) recebem aviso e saem; o livro fica |
| Busca | literal, escapar `~ * ?` | `criterio()` do núcleo em COUNTIF/MATCH/VLOOKUP; consumidores reescritos com `buscas_literais` |
| Livro | manter posições e identidades; custom válido acrescenta | livro espelhado da DADOS_INVOC nas primeiras linhas dos catálogos, custom depois |
| Texto | não executa regra | nenhum texto vira conta; EFEITO do talento vai para a carta existente (em branco com base, usa o texto do livro) |

Total ANALISE novo: 10 × (8 + aviso) + 20 × (6 + aviso) = **230 linhas**, acrescentadas no fim, depois de
Peças/Condições/Danos. As linhas existentes ficam idênticas e na mesma ordem (provado por `conferir_patches.py`
na base `7752c91`: 7436 + 230).

## Escolhas desta frente que o integrador pode trocar

1. **Aba oculta `DADOS_ENTIDADES`** (38 colunas; linhas = max(capacidades) + max(livro) + 3 = 37). Blocos:
   registros crus de tipo (A–K), catálogo de tipos (M–P: nome, vida de criação, usa talismã, reserva domada),
   listas (R–W), registros crus de talento (Y–AG), catálogo de talentos (AI–AL, as 4 colunas da tabela
   `talentos` da DADOS_INVOC). Nome livre: só `NOME` no módulo.
2. **Arquivos GS** `Entidades.gs` (`ABAS_DAS_ENTIDADES`) e `EntidadesPainel.gs` (`VALORES_ENTIDADES_`), no
   padrão de Danos. As alturas e o `esticam` da CONFIGURAÇÃO continuam no `PecasPainel.gs`, porque o
   `METADADOS_COMPLEMENTARES` dele já leva todos.
3. **Sem `copias`** nos cartões de entidade. Ver o achado do carregador no relatório: com o patch 02
   aplicado, declarar `copias` passa a ser seguro e reduz `Configuracao.gs`/`EntidadesPainel.gs`. Fica para
   o integrador decidir depois de aplicar o 02.
4. **Consumidores.** As 12 invocações trocam as comparações por nome
   (`tipo="Corpo amaldiçoado de criação"` etc.) por consulta aos funcionamentos efetivos do catálogo unido
   (`VLOOKUP(...,TIPOS,k,FALSE)=1`, k = 2/3/4). Todas as subfaixas da tabela `talentos` e a coluna de nomes
   de `tipos` passam a apontar para os catálogos unidos (228 referências). Alma, autonomia e Famílias
   não são tocadas.
5. **Capacidades fora de `capacidades.py`.** O integrador centralizou `DANOS = 10` lá. Sugestão:
   `TIPOS_ENTIDADE = 10`, `TALENTOS_ENTIDADE = 20` em `capacidades.py` e o módulo importando, como
   `custom_danos`. Não fiz para não editar o núcleo fora do patch.

## Divergências declaradas

- **MESTRE VIU** exportado como `N(célula)&""` (`"0"`/`"1"`), igual ao `custom_pecas`. O contrato diz
  "booleano"; o leitor atual trata texto. Se o formato 11 quiser `TRUE/FALSE`, trocar nas duas frentes.
- **Categoria herdada**: com base válida e CATEGORIA em branco, vale a categoria do livro. O contrato fala de
  "Categoria vazia/— não concede gratuidade", que é regra de Aptidão; aqui não há gratuidade e, sem base,
  CATEGORIA é obrigatória (aviso `Escolha CATEGORIA DE EFEITO`).
- **Texto do tipo não aparece na invocação.** A nota do protótipo diz que EFEITO E REQUISITOS do tipo são
  "exibidos na ficha selecionada", mas a ficha de invocação não tem área de texto de tipo: a tabela `tipos`
  do livro só tem o nome. Criar essa área seria redesenho da interface, fora do escopo. DEFINIÇÃO e EFEITO
  do tipo ficam no cartão da CONFIGURAÇÃO e na ANALISE. Se o usuário quiser exibir, é decisão de interface.
- **Tipo do livro com nome repetido**: a regra de duplicata vale também para o nome igual a um tipo do livro
  (`Maldição domada` custom é recusado), e o livro não muda.

## Dependências e interação com outras frentes

- **Formas (outro Codex)**: as Formas de entidade não passam por este módulo. O único ponto comum é a
  CONFIGURAÇÃO: cada módulo começa em `config['linhas'] + 4`. A ordem de chamada no `monta.py` define quem
  vem antes. Esta entrega entra depois de `custom_danos`.
- **Danos/Condições (integrador)**: nenhum campo compartilhado. `custom_danos` também remapeia faixas da
  DADOS_INVOC (tabela de dano); as faixas não se sobrepõem (estrutura 51/51 na base `7752c91`).
- **Formato 11 e leitor/bot**: as chaves novas são acréscimo. `ler-analise.py` já trata `aviso.custom.*`
  de forma genérica. O bot externo continua sem mudança.
- **Migração de fichas existentes**: `DADOS_ENTIDADES` é uma aba nova, e o bloco novo da CONFIGURAÇÃO fica
  depois de Danos. Os lotes de `capacidade-b47/migracao.py` (`shrinking`/`cut_tail`) não conhecem a aba
  nova. Isso é trabalho do integrador na migração por lotes.
