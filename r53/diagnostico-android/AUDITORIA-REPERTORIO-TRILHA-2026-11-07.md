# Revisão PR86 e repertório extra das Trilhas · 07/11/2026

## Resultado

A PR86 foi revisada no head `6568838badd1a92b130dd46058527fa089da655f`.
Está aberta, fora de rascunho, sem conflitos e com dois checks `smoke`
concluídos com `SUCCESS` nesse mesmo head. Não foram encontrados novos
bloqueios no escopo da correção da Expansão da domada e seus metadados.
Não houve merge nem alteração do ramo da PR86 nesta auditoria.

O pente-fino seguinte confirmou **duas lacunas legadas de validação do
repertório extra das Trilhas**, reproduzidas nas descartáveis Era e Ciclo.
Elas não foram introduzidas pela PR86. Permanecem sem correção neste ramo,
que contém somente o diagnóstico e a evidência sanitizada.

## Revisão da PR86

Foram examinados o gerador `ficha-v01/expansao_domada.py`, a aplicação
incremental, o runtime e a recuperação automática, as alterações da ANALISE,
o preparador com pré-condições, o empacotamento e os testes correspondentes.

Repetidos com sucesso:

- `node r53/testes/expansao_domada.js <Código-base-PR85>`: preparação estrita.
- `.venv/bin/python -m unittest r53.testes.test_expansao_domada`: dois testes.
- `node r53/testes/expansao_domada_modelo.js <pacote-base-PR85>`: comparação
  de 280.001 posições, 26 abas; somente 48 valores e 36 notas previstos,
  incluindo equivalência entre aplicação incremental e geração integral.

Os caminhos locais dos insumos privados estão no diretório ignorado
`nuvem-b47/saidas/correcao-expansao/`. A bateria nativa anterior de 512
cenários por QA não foi repetida sem necessidade. Seus resultados estão em
`CORRECAO-EXPANSAO-DOMADA-2026-11-07.md`.

As limitações já declaradas da PR86 continuam valendo: técnica própria,
histórico de aquisição e permissões de tipos custom exigem conferência da
mesa. Consumidores externos do texto de PE não foram ensaiados nesta rodada.
O pacote integral regenerado continua sem instalação nas QAs/oficiais.

## Referência mecânica

Livro R66 de `cupcake-mochi/JJK---Project`, commit
`e3058ad29180fdec2efec75b512446c49bf87b3d`, seções Repertório Ampliado,
Repertório de Parceria e Repertório do Conjunto:

- Invocação Principal acrescenta uma escolha nos níveis **8, 16 e 24 da
  própria entidade**: básica Classe 0, especial normal ou talento CE 1.
  O ganho total é 0/1/2/3; são alternativas para cada escolha.
- Parceria abre uma Família, mas mantém as quantidades normais de capacidades
  e talentos. Não concede esse repertório extra.
- Múltiplas Invocações recebe Repertório do Conjunto no **nível 27 do
  invocador**. Escolhe Essência ou Inteligência e cada entidade recebe metade
  do valor **permanente** desse atributo, arredondada para baixo. A Classe
  continua limitada pelo nível próprio da entidade.

Nenhuma conta de entidades registradas foi usada como quantidade de
invocações ativas. Essa distinção é necessária para a Invocação Principal.

## T01 — aquisição do repertório extra não é validada

**Evidência:** três cartões extras preenchidos em Parceria; primeiro extra
na Principal de nível 7; segundo no nível 15; terceiro no 23; extras do
Conjunto antes do nível 27 ou acima de metade do atributo permanente.
Todos mantiveram `FY=TRUE`, `FX` vazio e `GA` vazio nos cartões preenchidos.

O exemplo de buff usou atributo permanente 2 e ajuste temporário +4 nos dois
atributos candidatos. As células totais foram relidas como 6, mas o limite
do livro continua sendo uma escolha, qualquer que seja o atributo escolhido.
Três cartões permaneceram com montagem válida, sem alerta de aquisição.

**Causa localizada:** em `ficha-v01/montagens_r53.py`, `contextos()` marca
`extra=(tipo=='ext')`, permite Classes 0–7 e usa nível/Classe da entidade,
mas não fornece requisito de aquisição da Trilha aos contextos extras.
Essa configuração já existia antes da PR86. O requisito de nível da Classe
continua funcionando; o que falta é a concessão da escolha adicional.

Há nota visível explicando as regras de aquisição. Portanto o achado não
significa ausência de instruções, nem que o estado VÁLIDO já implementava
aprovação completa da aquisição. A lacuna é a falta de verificação mecânica
dessas instruções no estado/aviso da ficha.

## T02 — capacidades e talentos extras não compartilham limite

**Evidência:** na Principal, entidade de nível 24, foram preenchidos os três
cartões de capacidade e os três campos de talentos CE 1. As seis escolhas
ficaram registradas, com os três cartões válidos, os três textos de talento
resolvidos e nenhum aviso conjunto de **6 escolhas para limite 3**.
O mesmo ocorreu no Conjunto de nível 27 com atributo permanente 6.
O controle de uma capacidade mais dois talentos funcionou sem avisos.

Os talentos usados foram Leitura, Instinto e Raiz, presentes no catálogo CE 1
para entidades. Não foram usados textos livres para simular uma seleção.

**Causa localizada:** `ficha-v01/ficha_invocacoes.py` gera três cartões
`ext` e três entradas `talx`. As fórmulas `d_xt0..2` resolvem o texto de cada
talento por consulta, sem consolidar seu consumo com os cartões extras.
Os espaços comuns de especiais também não fazem essa conta, corretamente:
o ganho da Trilha é separado do orçamento base e da Expansão.

## Matriz nativa e edição real

Foram usadas somente as duas QAs descartáveis já identificadas nos relatórios
anteriores, com snapshot fresco antes das entradas temporárias. Nenhuma
oficial ou ficha de jogador foi editada.

São **20 configurações × entidades 1 e 12 = 40 cenários por cópia**,
totalizando 80. Por cópia: **22 excedentes e 18 controles**. Os 22 excedentes
são variações dos dois achados acima, não 22 defeitos independentes.
Nível próprio e totais dos atributos foram relidos em cada configuração.
Os 18 controles de montagem passaram em cada cópia.

Fronteiras cobertas: Principal 7/8, 15/16 e 23/24; Conjunto 26/27;
atributos permanentes 0/2/4/6; buff temporário; entidade de nível 7 com
invocador 27; capacidade/talento em mistura dentro e acima do limite.
O plano e resultados sanitizados estão em
`repertorio_trilha_resultados_2026-11-07.json`.

A matriz foi escrita pela API nativa do Sheets e **não** dispara `onEdit`.
Como prova focal adicional, em cada QA foi apagada por edição real a fórmula
calculada `INVOCAÇÕES!M173`. O código instalado recuperou automaticamente a
fórmula e o estado VÁLIDO na configuração Principal 24 com seis escolhas.
Isso valida a recuperação dessa célula; não equivale a ensaio de todas as
edições de Trilha, talentos e versões. Não foram feitas edições nativas de
nome/Classe que pudessem salvar as entradas temporárias no cache de versões.

## ANALISE e preservação

Nas duas QAs, foram auditadas 96 chaves ligadas aos extras/talentos da primeira
e última entidade: **84 referências diretas B↔C corretas** e **12 fórmulas
multicélula conferidas separadamente**. Para estas últimas, C lista as células
usadas na fórmula de B, na mesma ordem. Zero divergências nessa amostra;
isso não é uma releitura completa de toda a ANALISE.

Ao fim foram restauradas **183 entradas por cópia**, incluindo as escolhas
de Família tocadas pelo ensaio. A comparação de **3.535 posições por cópia**,
com valores digitados/calculados, tipos, fórmulas, notas e validações, encontrou
**zero diferenças e zero erros de fórmula** nos intervalos lidos.

A amostra inclui **1.998 posições de MONTAGENS**, das quais 1.776 são células
das oito versões dos seis contextos extras. Não houve perda das montagens
salvas. Os agrupamentos temporariamente abertos foram recolhidos e
DADOS_INVOC, DADOS_R53, ANALISE e MONTAGENS permanecem ocultas.
Nenhum script foi instalado ou alterado nesta rodada.

Snapshots, leituras brutas e capturas ficam somente em
`nuvem-b47/saidas/auditoria-repertorio-trilha/`, fora do Git.

## Próxima correção proposta

Criar uma validação específica da concessão e do orçamento comum dos extras,
preservando montagens que precisem de revisão. Não apagar escolhas, não
compensar o excesso retirando espaços do repertório base e não consumir
novamente o orçamento da Expansão da domada.

Para Conjunto, registrar explicitamente o atributo escolhido pela habilidade:
a escolha Essência/Inteligência desse benefício não deve ser inferida da
seleção usada para Defesa. Esta matriz usou ambos os atributos iguais para
que o resultado não dependesse de uma escolha ainda não representada.

A correção deve incluir os 12 registros, básicas Classe 0 e talentos isolados,
atributos ímpares, campos vazios/custom e edição real, além das fronteiras já
confirmadas. Esses casos adicionais não foram todos cobertos nesta rodada.

Ramo de auditoria separado: `codex/auditoria-repertorio-trilha-20261107`.
PR86 preservada. PR31 continua aberta no SHA
`765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`. Sem merge, alteração das oficiais,
ficha do jogador, acionadores ou permissões.

Modelo/esforço recomendado: **Sol/Medium** para revisão deste diagnóstico;
**Sol/High** para implementar e ensaiar a futura correção. Nenhuma configuração
de modelo foi alterada.
