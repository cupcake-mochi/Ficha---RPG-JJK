# Expansão da domada e metadados · 07/11/2026

Correção dos achados D01, D02 e M01 da
`AUDITORIA-EXPANSAO-DOMADA-2026-11-07.md`. Base de implementação PR85
`735d499`, retomada em `e88010a`. Geração `ed25e7759cd26b7e`.
Referência mecânica: R66 do livro,
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

## Comportamento corrigido

- O requisito deixa de ser apenas a consulta de um texto. O domínio informa
  `REVISAR` para tipo incompatível, nível próprio insuficiente, refino do
  invocador insuficiente, falta de especialização em Ocultismo e estouro
  de espaços. Sem Barreiras conserva os mínimos anteriores, inclusive nível 14.
- O cabeçalho soma especiais normais conhecidas e o domínio adquirido.
  No nível 14, Completa mais duas especiais mostra `2+3 de 4` e pede revisão.
  O campo de requisito também informa `espaços excedidos: 5/4`.
- A aquisição continua registrada no seletor existente: Incompleta ocupa
  2 espaços, Completa 3 e Sem Barreiras 5 **no total**. Não soma 2+3+5.
  Sem Barreiras mostra os dois custos de abertura, fechado/aberto, por
  exemplo `24/28 PE` na Classe 4. Usar o custo fechado não reduz a aquisição.
- As 12 chaves `invocacao.N.exp.acerto` passam de `entrada` a `resultado`
  na coluna D da ANALISE. Chaves, fórmulas de B e origens de C são preservadas.

Cada cartão normal identificado por `entidade.N.esp.K` ocupa uma vaga quando
tem nome. Classe em uso e versões preparadas não multiplicam essa identidade.
Básicas, Liberações, Máxima e escolhas adicionais da Trilha conservam suas
aquisições separadas; não entram no orçamento básico nem concedem vagas
genéricas para pagar domínio. A capacidade total original `GV` não foi alterada.
Nenhuma compra, versão, nome ou escolha é apagada para corrigir o orçamento.

Não existe registro estruturado de técnica própria ou do histórico de
aquisição de cada etapa. Mesmo quando os requisitos automáticos passam,
a ficha pede conferir técnica própria e etapas. Tipo custom fica em revisão
de permissão expressa; possuir reserva de PE não aprova Expansão automaticamente.
Não foram implementados novos ganhos ou validadores das escolhas de Trilha.

## Alterações técnicas delimitadas

`ficha-v01/expansao_domada.py` aplica a conferência depois do layout final,
sem inserir linhas, colunas ou chaves. O exportador em `analise.py` corrige
o papel do Acerto. A geração produz:

- `expansao_domada_plano.json`: 36 fórmulas em DADOS_INVOC, nas colunas
  IE, JH e JJ, linhas 2 a 13; mais 12 classificações na ANALISE.
- `expansao_domada_notas.json`: 36 notas das âncoras que mostram essas contas.
- `expansao_domada_suporte.json`: 48 moldes **inalterados**, usados só na
  recuperação de edições mistas: os 12 Acertos JI e A:B:C dos 12 registros.

Não há substituição global de coordenadas. Os moldes de ANALISE vêm do
contrato exportado; a recuperação mantém o escape dos apóstrofos nos literais
de origem e usa RichText como a recuperação já instalada.

O primeiro ensaio misto confirmou uma falha da proposta incremental:
o pacote Android instalado omite ANALISE do conjunto carregado. O ajuste
inicial procurava essa aba e interrompia a continuação do editor antigo.
Isso foi corrigido e os eventos foram repetidos. O ajuste reconhece essa
separação somente no caminho da base conhecida; não cria uma ANALISE parcial
nem força a carga de catálogos. A recuperação leve cobre os blocos mistos
testados, agrupa as escritas por coluna e conserva as notas no retrato legado.

O Código final foi salvo, recarregado/relido nas duas descartáveis e comparado
integralmente à proposta. SHA-256:
`5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef`.
Os demais arquivos instalados foram preservados. O pacote integral novo
**não** foi instalado nas cópias nem em fichas oficiais.

## Ensaios concluídos

**512 cenários nativos por descartável**, Era e Ciclo:

| Grupo | Por cópia | Cobertura |
| --- | ---: | --- |
| Requisitos | 144 | 12 combinações nas 12 entidades; fronteiras de nível/refino, especialização, tipos e nível herdado |
| Orçamento | 108 | 9 combinações nas 12 entidades; sem domínio, 2/3/5 espaços, no limite e acima dele |
| PE | 252 | 7 Classes × 3 degraus × 12 entidades; fechado/aberto em Sem Barreiras |
| Trilha e versões | 8 | Primeira e última entidade; extras, básicas e trunfos separados; sete versões em uma identidade |

A matriz usou edição via API para conferir o cálculo nativo. Separadamente,
passaram **oito edições reais de recuperação**, quatro em cada cópia:

1. Excluir IE2:IE13 recuperou os 12 cabeçalhos.
2. Excluir JH2:JJ13 recuperou as 36 fórmulas, incluindo os Acertos inalterados.
3. Excluir A2948:D2948 recuperou o primeiro registro completo.
4. Excluir A3960:D3960 recuperou o último registro completo.

As duas origens recuperadas conservaram seus apóstrofos e as tags voltaram
como `resultado`. A seleção real de Completa também passou nas duas fichas:
o degrau foi mantido e o cenário de 5/4 mostrou o aviso na interface. Os eventos
finais consultados terminaram como `Concluído`. Depois de salvar Código novo,
as fichas foram recarregadas antes dos eventos finais; tentativas anteriores
com o código antigo em uso não integram o aceite.

Todas as entradas temporárias foram restauradas. A conferência final de
**4.658 posições por cópia**, incluindo **2.072 de MONTAGENS**, encontrou
somente os 84 alvos previstos: 48 células e 36 notas. Zero diferenças fora
desse conjunto e zero erros de fórmula nos intervalos lidos. Cada alvo foi
comparado à fórmula/tag/nota proposta. As 108 posições de Família permaneceram
preservadas. Os grupos abertos foram recolhidos e DADOS_INVOC, DADOS_R53,
ANALISE e MONTAGENS ficaram ocultas.

## Verificações locais e transporte

- Comparação integral de **280.001 posições e metadados de 26 abas**:
  somente 48 valores/fórmulas e 36 notas alterados. O retrato incremental
  também foi comparado ao modelo novo, incluindo notas.
- Planejamento, reversão das células, recusa de base divergente, proteção
  de notas próprias e recuperação focal/mista passaram em `pt_BR` e `en_US`.
- A carga do pacote realmente instalado foi reproduzida localmente com
  ANALISE ausente; os 36 cálculos foram ajustados sem inventar outra aba.
- O relatório local de `conferir.py --smoke` aprovou **119 verificações**.
  Testes focais e análise de sintaxe incluíram os módulos novos.

A fonte crescida excedeu o limite anterior de compressão. O empacotador
usa Zopfli fixado nas dependências de preparação como último recurso,
produzindo **gzip padrão**, relido e comparado ao conteúdo original. O Google
continua com `Utilities.ungzip`; não recebe biblioteca, rede ou permissão nova.
O teto de preparação local passou de 60 para 180 segundos; o limite de execução
do Apps Script não mudou.

O pacote cabe nos mesmos cinco arquivos: 3.854.032 bytes Base64, margem de
395.968 bytes. Isso é tamanho de transporte, não medição de RAM ou velocidade
de abertura. O hash da fonte descomprimida é
`691adc854197976c1921e7f8039bd75d5bc31627be46dc4bff820f17e05344ba`.

## Futura atualização de uma ficha existente

1. Tirar snapshot novo do projeto, metadados, 48 células, 36 notas e entradas
   a preservar. Começar por uma cópia descartável da ficha que será atualizada.
2. `preparar_expansao_domada.js` exige Código da PR85 com SHA-256
   `7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7`.
   `prepararCelulas` exige as 48 origens esperadas e permite preparar a reversão
   conferindo o estado final. `prepararNotas` recusa notas anteriores diferentes.
3. Instalar apenas o Código incremental conferido, os 48 valores/fórmulas e
   as 36 notas. Reler Código salvo, recarregar a ficha e repetir os ensaios
   focais de cálculo, recuperação e preservação. Nunca usar construir/continuar.
4. Uma oficial sem a pilha anterior não atende a essa base. Preparar e testar
   a integração das correções anteriores antes de reutilizar este delta.
   Não colar o Código das QAs sobre um projeto diferente.

O contrato ANALISE12/esquema2 conserva chaves, endereços e tipos de valores.
No degrau Sem Barreiras, o resultado textual `exp.pe` passa a exibir o par de
custos; consumidores externos desse texto não foram ensaiados nesta tarefa.

Snapshots, código instalado/relido, resultados e imagens ficam fora do Git em
`nuvem-b47/saidas/correcao-expansao/`. Nenhuma oficial, ficha de jogador ou PR31
foi alterada. Sem merge, acionador novo ou mudança de acesso. Próxima etapa:
Sol/Medium para revisão da entrega; Sol/High para eventual integração e ensaio.
