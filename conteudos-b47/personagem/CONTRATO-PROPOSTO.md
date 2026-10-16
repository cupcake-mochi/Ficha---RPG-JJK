# Contrato da entrega — base comum revisão 1

Referência lida: `ae16895967d23044f558f31638df23c0fbdd7598:conteudos-b47/comum/contrato.json`.
Capacidades adotadas: **10 Formas, 10 Aptidões/Bênçãos e 10 Talentos**, compartilhados. Não há multiplicação por aplicação ou invocação.

## Fachada

`b47_personagem.aplica(layout, contexto)` recebe:

| Entrada | Conteúdo |
|---|---|
| `fam`, `inv`, `criacao`, `pecas` | Metadados dos produtores canônicos, depois de Famílias e peças |
| `capacidades` | Mapa do contrato comum; os três grupos desta frente |
| `inicio` | Primeira linha nova, estritamente depois do fim real de CONFIGURAÇÃO |
| `abas` | Três nomes reservados pelo integrador para os auxiliares |
| `bloqueia_extensao` | Expressão opcional; padrão conserva a verificação de rota 3 do núcleo recebido |
| `verificacoes` | Expressões estruturadas opcionais para as exceções e requisitos de história abaixo |
| `chave_aviso_uso` | Callback opcional que fecha as chaves dos avisos das cartas |

O retorno inclui `antes`/`depois` por aba/célula, `entradas` em triplas chave/endereço/booleano, `registros`, `catalogos`, `inicio`/`fim` e o plano de emissão. O manifesto cobre valores/fórmulas; mesclas, estilos, notas, validações e alturas estão no layout modificado, para a migração central comparar. A transformação contém objetos de execução; usar `exporta()` para emitir as quatro colunas, sem serializar todo o contexto.

A API de nível inferior `planilha.emitir(livro, Contrato)` aceita todas as referências do editor por parâmetro. É possível usar outro posicionamento aprovado sem reescrever o motor.

## Campos e vazios

Comuns: nome, base opcional, tipo, MESTRE VIU, requisitos e efeito. Vazio herda somente uma base válida do livro. `Nenhuma` na base cria sem base; em Família/Restrição embutida remove o vínculo herdado. Zero e Não são explícitos. MESTRE VIU é lembrete e não libera um cadastro inválido.

| Contrato comum | Campo interno | Representação |
|---|---|---|
| `categoria` | `ce` | Aptidão/Bênção: — ou 1/2/3; Talento: 1/2/3 |
| `classe_zero` | `classe_0` | Sim/Não no editor, booleano no motor |
| `peso` | `peso` | Sem custo/Leve/Média/Pesada; códigos 0/1/2/3 no motor |
| `resultado` | `resultado` | Dano/Cura/Vida temporária/Efeito; códigos canônicos 0/1/2/3 |
| `alcance` / `area` | Duas escadas + 14 bases textuais | Estrutura detalhada abaixo |

A exportação usa `categoria` e `classe_zero`, sem reutilizar nomes com outro sentido. Os campos TIPO de Forma/Talento também são exportados crus para diagnosticar colagens de tipo incorreto; são duas extensões simples às listas lógicas iniciais do contrato.

Alcance e área são independentes:

- `alcance_escada`: Fixo ou alcance.
- `area_escada`: Fixo, raio ou comprimento.
- Para cada dimensão, `<dimensao>_personagem_classe_0`, `_classes_1_a_5`, `_classes_6_e_7`.
- Para cada dimensão, `<dimensao>_entidade_classe_0`, `_classes_1_a_5`, `_classe_6`, `_classe_7`.

Bases dinâmicas usam texto em metros, como `4,5 m`; Fixo conserva texto literal. Não há valores demonstrativos preenchidos como regra. Os prefixos, o centro, a largura e os degraus próprios das Formas publicadas são herdados. Uma segunda dimensão explicitamente preenchida em uma base de um componente ganha saída separada; a descrição continua responsável por alvos/origem que não possuam campo mecânico. Sem base, os componentes são exibidos separadamente. Comprimento usa os aumentos existentes de Alcance e Área. Não há interpretação de prosa.

## Requisitos e aquisição

Aptidões/Bênçãos: nível mínimo, Refino/Lapidação mínimo e escolha consumida/Gratuita. Categoria vazia ou — mantém consumo de uma escolha. Uma base gratuita herda sua gratuidade; é possível declarar consumo explicitamente. As duas iniciais do livro continuam automáticas e fora do menu; gratuitas custom aparecem nas cartas e custam zero escolhas, sem aumentar o orçamento.

Aptidões não recebem um nível mínimo oculto por CE. Bênçãos usam Lapidação 1/4/7 para CE 1/2/3, além dos requisitos declarados. Bases preservam identidade, predecessoras em ordem, atributos e as exceções nomeadas. Aliases da mesma aptidão não permitem repetir uma aquisição; as variantes de Aptidão/Bênção Própria compartilham a limitação de uma por personagem.

Talentos mantêm níveis de CE 1/7/13, rotas e custo de CE em espaços. Há cinco lugares pagos e sete do Leque; Leque depende da abertura existente e não ocupa espaços. Requisitos textuais adicionais são mostrados na carta e não executados.

O motor recebe `Contexto` com atributos, origem, aprendizado, voto do iniciante e concessões nomeadas. Para as fórmulas da ficha, `verificacoes` pode fornecer:

- `voto_iniciante`, `cesta_permitida`, `petala_permitida`, `aprendeu_dominio_simples`, `aprendeu_extensao`, `tecnica_inata`.
- `concessoes`: mapa identidade do livro → expressão booleana da concessão já aprovada.

Ausência de um registro estruturado de aprendizado/origem produz pedido de conferência manual na carta. Não se infere aprendizado de notas ou da descrição, nem se inventa uma aprovação. Os requisitos numéricos e a ordem das predecessoras continuam calculados.

## Menus, identidade e exportação

Livro permanece antes do custom. Duplicata literal, inclusive diferença só de caixa, exclui todos os custom envolvidos; o livro permanece. MATCH/VLOOKUP/COUNTIF escapam `~ * ?`. Inválidos e parciais continuam exportados crus com aviso. Catálogos são recompostos por fórmula; limpar não deixa uma definição em cache.

Identidade herdada é auxiliar, não substitui o nome exibido. É usada nas verificações de Cone/Linha, Restrições embutidas e requisitos nomeados. Restrições embutidas consultam o catálogo vivo de Restrições, inclusive custom válido, e mantêm peso, frequência, teto e limite. A devolução paga somente Melhorias. A Forma não recebe desconto de Família Livre na entidade.

Reservas já publicadas: `custom.forma.N.*`, `custom.aptidao.N.*`, `custom.talento.N.*` e `aviso.custom.<grupo>.N`. A emissão desta entrega tem **500 linhas** de cadastro/aviso. Propõe-se acrescentar, mediante conciliação do contrato, **24 avisos de uso**: `aviso.personagem.aptidao.N` e `aviso.personagem.talento.N`, N de 1 a 12. O patch 01 fornece esse callback; o patch 03 ensina o leitor a tratar esses avisos e os novos textos literais.

Nenhum módulo/patch escolhe FORMATO nem adiciona 11 aos formatos conhecidos. O integrador fecha a versão conjunta, esquema e leitor antes de gerar a entrega canônica. ANALISE 10 e bot permanecem intactos neste ramo.
