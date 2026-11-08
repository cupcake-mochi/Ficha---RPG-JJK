# AQ01 · Criação conserva o nível fabricado · 08/11/2026

## Resultado

Criação agora usa o nível de fabricação registrado, limitado pelo nível
do invocador. Com fabricação no 1 e invocador no 30, o shikigami fica no
nível 1, com 5 PV e um espaço de especial (Constituição e ajuste manual
zero). Antes chegava indevidamente ao 4, com 14 PV e dois espaços.
Corpos de criação também conservam seu nível, com sua própria escala de vida.

Correção aplicada por incremento nas duas descartáveis Era/Ciclo, com
**312 casos de cálculo, 26 conferências de débito e dez edições reais
aprovados**. Oficiais, fichas de jogador, PR88, PR31 e main preservados.
Sem merge ou instalação do pacote integral.

## Regra, fonte e escopo

A referência é a seção Aquisição de
[Invocações na R66](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/manual/60-invocacoes.md),
corroborada por
[Fabricação de entidades](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/planejamento-editorial/invocacoes/fabricacao/lote-01/FABRICACAO-DE-ENTIDADES.md).
A entidade não melhora quando seu fabricante sobe de nível ou a repara;
uma versão mais poderosa exige novo projeto. AQ01 era uma regra R44
preexistente, não uma regressão da PR88.

`aquisicao-criacao-r66.json` registra o trecho e o commit da correção focal.
A extração conserva sua fonte histórica para as outras regras e declara
essa reconciliação no metadado do catálogo. Não se reescreveu o manual
histórico como se toda a extração fosse R66. A guarda recusa mudança na
frase histórica até que a reconciliação seja revista.

O nível em branco mantém a prévia histórica no nível do invocador.
**Preencha o nível obtido/fabricado para fixá-lo.** Essa compatibilidade foi
testada e está explícita na ajuda; o vazio não registra automaticamente
um nível permanente nem aprova uma fabricação.

O delta integral tem **13 valores/fórmulas e três notas**:

- `DADOS_INVOC!BQ5`: Criação deixa de usar o sinalizador 2 e passa a 0.
- `DADOS_INVOC!FO2:FO13`: retirado o ramo de crescimento até o fim da Classe.
- `INVOCAÇÕES!I46`, `K46`, `O12`: ajuda de aquisição, nível obtido e nível calculado.

A previsão inicial de 36 notas foi corrigida ao comparar o modelo real:
ele possui essas três ajudas somente no primeiro cartão. Sua distribuição
foi preservada; não foram acrescentadas notas nas outras entidades.

## Aplicação e recuperação

Código dos dois projetos relido integralmente antes da escrita:
`36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc`.
O preparador exige essa base, valores e notas atuais exatos, localidades
pt_BR/en_US e snapshots completos. As entradas e os alvos foram conferidos
novamente imediatamente antes dos 16 pedidos por cópia.

Código final salvo, projetos reabertos e conteúdo integral relido igual:
`ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352`.
O incremento atualiza os moldes do pacote antigo e preserva a representação
compacta do pacote novo, sem alterar seu hash ao carregar. O teste também
cobre idempotência e recusa de base/nota divergente antes de mutações.

Um ensaio intermediário de `FM2:FQ3` terminou como Concluído, mas o editor
antigo não repôs quatro fórmulas vizinhas de FM/FQ. Foram repostas do backup
e acrescentados 24 moldes inalterados ao caminho leve. O suporte final tem
49 moldes: FM/FN/FP/FQ nas 12 entidades e BP5. Eles não são novos deltas da
instalação. Mantidos os moldes IF da PR88 e o escape da ANALISE.

Após esse ajuste, foram repetidas **cinco edições reais por cópia**:

| Faixa apagada pela interface | Células por cópia | Resultado final |
| --- | ---: | --- |
| FO2:FO13 | 12 | Todas as fórmulas recuperadas |
| FN2:FP3 | 6 | Bloco misto inicial recuperado |
| FN12:FP13 | 6 | Bloco misto final recuperado |
| BP5:BQ5 | 2 | Rótulo e sinalizador numérico recuperados |
| FM2:FQ3 | 10 | Bloco maior completo pelo caminho leve |

As dez execuções finais constam como **Concluído** no histórico nativo.
Foram aceitas somente após igualdade completa dos dados lidos. Uma leitura
temporária vazia de FO ocorreu enquanto o evento ainda terminava; a
releitura passou sem outra edição. Durações observadas: até 27,017 s.
Isso não certifica latência Android nem recuperação de colagens arbitrárias.

## Matriz de cálculo

Invocadores nos níveis 30 e 9; níveis obtidos
`[1,4,5,8,9,12,13,16,17,20,21,26]`, nas 12 entidades das duas cópias:

| Grupo | Casos totais |
| --- | ---: |
| Espaço conhecido | 48 |
| Lista de ritual | 48 |
| Maldição domada | 48 |
| Criação | 48 |
| Obtido vazio, invocador 12 e 16 | 48 |
| Fabricada no 9 com invocador 9/10; registro de novo projeto no 10 | 72 |
| **Total** | **312** |

Foram comparados presença, nível, Classe máxima, dados da básica, capacidade
de especiais e vida máxima, com oráculo independente da fórmula de nível.
Constituição e ajuste manual de vida foram lidos da entidade. Os dois
corpos de Criação e os cinco tipos publicados foram exercitados. O registro
de novo projeto testa a mudança do nível informado, não todo o procedimento
de fabricação, seus testes ou materiais.

O débito de espaços foi conferido em JM2, HM19 e R55 em cada uma das 26
configurações. Espaço conhecido debitou 12; as demais aquisições, zero.
A matriz usou a API do Sheets, que não dispara onEdit. Foi executada antes
da ampliação dos moldes de recuperação; esse ajuste não alterou as 13 contas
ou as três notas. Não se apresenta a matriz como repetida após só esse suporte.

Esses ensaios não aprovam toda definição de entidade, montagem, aquisição
de Talentos ou quantidade efetivamente ativa. Avisos independentes não
foram removidos para obter aprovação.

## Preservação e verificações locais

**49 entradas por cópia restauradas**, com fórmulas e tipos originais.
Comparadas **86.082 posições por cópia**, incluindo **85.887 de MONTAGENS**
(aba inteira, A1:I9543). A API retornou 36.972 posições explícitas nessa
aba; caudas omitidas foram tratadas como vazias. Zero diferenças inesperadas
nos valores digitados/calculados, fórmulas, tipos, notas e validações lidos.
Somente os 16 deltas previstos permanecem. Metadados antes/depois iguais.

DADOS_INVOC voltou a ficar oculta. As duas fichas restauradas foram
inspecionadas visualmente e capturadas no Sheets. Não houve escrita de
formatação, versões ou compras; a comparação delimitada não certifica
todos os atributos de formatação de todas as abas.

Geração **72fa80b901f2249c**. Comparação de **280.056 posições/26 abas**:
somente 13 valores e três notas diferentes, metadados preservados e modelo
incremental igual ao integral. Pacote local em cinco partes, 3.858.456 bytes
Base64, fonte SHA-256
`a00542d6f0601302740bdbc52043d8722a551636592cd84aff513a1de5ff5e30`.
**Pacote integral não instalado.**

Smoke final: **123 verificações aprovadas**, saída zero. Testes focais de
transporte, snapshots, reversão, recuperação, recusa atômica e carregamento
das partes antigas recém-lidas também passaram. No Windows, PYTHONUTF8=1
foi necessário para os subprocessos do smoke; uma tentativa anterior sem
essa propagação falhou em cp1252 e não conta como aprovação.

Regressão e perturbações legadas de invocações foram atualizadas para a
regra de nível fixo. LibreOffice não foi executado; a prova de cálculo
desta entrega é a matriz nativa descrita. Testes opcionais pulados pelo
smoke por falta de fixture não equivalem a cobertura executada.

Evidência sanitizada: `criacao_nivel_fixo_validacao_2026-11-08.json`.
Snapshots, scripts, leituras e capturas somente na pasta privada ignorada
`nuvem-b47/saidas/criacao-nivel-fixo/retomada-08/`.

Ramo de implementação `codex/criacao-nivel-fixo-20261108`, sobre o WIP
31e5133 e a auditoria fe52bb1. PR88 preservada em ab05bcf; PR31 em 765e3b2.
Próxima ação: revisão focal com Sol/Medium; Sol/High para novo ensaio ou
fronteira mecânica, sem alterar configurações ou delegar a subagentes.
