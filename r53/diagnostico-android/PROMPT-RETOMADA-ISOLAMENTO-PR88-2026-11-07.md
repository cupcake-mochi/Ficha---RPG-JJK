# Prompt de retomada · isolamento de erros da PR88 · 07/11/2026

Continue a correção já autorizada abaixo. O trabalho foi interrompido a meu
pedido para trocar do Linux para o Windows. Leia o estado salvo antes de
alterar qualquer coisa. Responda em português.

## Repositório e ponto de partida

- Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK
- **Checkpoint WIP: `codex/wip-isolamento-pr88-20261107`. Comece por ele.**
- PR que deve receber a correção final: https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/88
- Branch da PR88: `codex/contagem-especiais-20261107`.
- Head remoto da PR88 na pausa: `4d22fb71f222da220712aec668b90ee1b52a94e4`.
- O WIP inclui o diagnóstico da revisão, incorporado localmente no commit
  `30040c5`, e a implementação ainda não concluída. Não iniciar pela main.

Leia primeiro:

1. Todos os AGENTS.md aplicáveis, especialmente o topo do AGENTS.md da ficha.
2. `r53/diagnostico-android/REVISAO-PR88-ERROS-NOMES-2026-11-07.md`.
3. `r53/diagnostico-android/CORRECAO-CONTAGEM-ESPECIAIS-2026-11-07.md`.
4. `ficha-v01/expansao_domada.py`, os preparadores e testes citados abaixo.

O WIP está separado para preservar a PR88 enquanto a entrega ainda não
está pronta. Não dar merge. Ao concluir os ensaios, integrar a correção
na branch da PR88 preservando quaisquer atualizações remotas de terceiros.
Não usar force push nem substituir trabalho concorrente.

## Pedido autorizado

Corrigir na PR88 o isolamento dos erros dos nomes, testar nas duas
descartáveis, conferir recuperação por edição real e preservar montagens.
Deixar pronto para revisão, **sem merge, sem editar oficiais, jogador ou
PR31**. Não abrir agentes ou chats extras.

## Falha confirmada e proposta atual

R88-01: a soma avalia LEN em todo `DADOS_R53!B2:B253` antes de aplicar a
identidade. Um erro no nome da Básica 1 (`INVOCAÇÕES!J71`, registro
`entidade.1.bas.1`) contamina os 12 cabeçalhos e, com domínio preenchido,
os 12 requisitos de especiais normais. Reproduzido com `=1/0` e `=NA()`
nas duas QAs. A comparação A/B confirmou regressão introduzida pela PR88.

A implementação WIP **filtra primeiro os nomes da categoria/entidade**,
depois calcula seu comprimento em texto. Não usa IFERROR global para
retornar zero. Um erro no nome da própria especial deve continuar visível;
erros em básicas, extras ou outra entidade não devem contaminar sua soma.
Preservar números, zero e FALSE como nomes não vazios, e excluir `=""`.

Arquivos já alterados/criados:

- `ficha-v01/expansao_domada.py`: nova contagem com FILTER antes de LEN;
  gera também o delta contra a soma global antiga.
- `ficha-v01/monta.py`: exporta `isolamento_nomes_plano.json`.
- `r53/diagnostico-android/expansao_domada_plano.json` e
  `repertorio_normal_plano.json`: propostas cumulativas atualizadas.
- `r53/diagnostico-android/isolamento_nomes_plano.json`: 24 fórmulas,
  `DADOS_INVOC!IE2:IE13` e `JJ2:JJ13`, sobre a primeira versão da PR88.
- `r53/diagnostico-android/preparar_isolamento_nomes.js`: preparação estrita
  de código/células e reversão sobre o código instalado da PR88.
- `r53/testes/isolamento_nomes.js` e `isolamento_nomes_modelo.js`, testes
  anteriores de contagem e testes Python atualizados.
- `nuvem-b47/conferir.py`: novo teste registrado.

## O que realmente passou

- Protótipo nativo na QA Era: **nove casos aprovados**, incluindo erros fora
  da categoria/entidade, erros próprios preservados, número, vazio, zero e
  FALSE. As células do protótipo foram restauradas em finally.
- Três testes Python de Expansão passaram.
- Novo teste JS de preparação, duas localidades, reversão, recuperação e
  carregamento do módulo Android antigo passou com os insumos privados.
- O teste de contagem anterior passou com as propostas novas.
- As rotas de preparação a partir da base PR87 e da primeira PR88 produziram
  exatamente o mesmo código proposto, SHA-256
  `36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc`.

**Ainda não foi feita a aplicação da correção final nas QAs. Não houve
releitura fresca do código dos projetos nesta etapa, matriz final nas duas
cópias, edição real de recuperação, smoke final ou atualização da PR88.**
O protótipo não substitui essas validações.

## Interrupção e artefatos incompletos

A sessão de ferramentas reiniciou enquanto eram colhidos os snapshots
e executada a geração. Depois o usuário pediu parar e salvar.

- A geração parou antes de emitir as fontes GS finais. Não há processo
  de geração/empacotamento deixado em execução.
- `apps-script/` continua na geração anterior **c59bcb593daf38af**. As
  propostas JSON novas ainda não estão sincronizadas com esses GS.
- `nuvem-b47/saidas/isolamento-pr88/antes-0.json` e `antes-1.json` ficaram
  **truncados/inválidos**. Não usar como backup nem como snapshot de aplicação.
- O arquivo de status da geração não foi produzido. **Refazer a geração
  e o empacotamento em série**, após conferir memória disponível.
- **Refazer snapshots frescos e completos antes de aplicar qualquer coisa.**

## Alvos autorizados: somente descartáveis

Era:
https://docs.google.com/spreadsheets/d/1LBZOf9vJmd02xNvAyMX5r0NDRL-NInzicc7l5q3HBDQ/edit

Projeto Era:
https://script.google.com/u/0/home/projects/1IBTaNa9I6DzZXQlXQcre-oMd8b0rqq55hDXF5AODp3jdkhFigt31ccIG/edit

Ciclo:
https://docs.google.com/spreadsheets/d/1HQqGOVGky5qlGOyk8h4QgOQb4Zwq3BXWaM65Q7vGgqU/edit

Projeto Ciclo:
https://script.google.com/u/0/home/projects/1WHzpRRE_B9bMY2V1oVkjQgOTFRKdRSkT4BtXadCRxUy-UCNnAuFJ6EhC/edit

Código instalado esperado, sem esta correção:
`8935211c6e87cd4515b0df860bd0d71524f316d08e42013f86cc9fa6b1d53bea`.
O preparador novo exige esse hash. Relê-lo integralmente antes de aplicar;
se divergir, investigar e preservar as alterações, não sobrescrever.
Verificar conexões disponíveis no Windows; não presumir navegador, login
ou acesso aos arquivos privados do Linux. Avisar se o Google pedir autorização.

## Próximos passos concretos

1. Conferir Git/AGENTS/conexões, preservar o WIP e alterações concorrentes.
2. Reler código e metadados das duas QAs e colher backup/snapshot válido
   das 24 fórmulas, entradas temporárias e montagens envolvidas.
3. Concluir geração GS e empacotamento; comparar o modelo antigo da PR88
   com o novo: apenas 24 fórmulas, sem outros deltas mecânicos/metadados.
4. Ensaiar instalação incremental nas duas descartáveis, com código salvo
   e relido integralmente. Não instalar o pacote integral.
5. Repetir os controles de números/textos/booleanos/vazios da PR88. Testar
   erro em básica/extra, erro em outra entidade e erro na própria especial,
   com `=1/0` e `=NA()`. Manter erro na origem e avisos legítimos; não zerar
   orçamento para esconder a montagem com problema.
6. Conferir recuperação por edição real de IE2:IE13, JH2:JJ13, IE2:IF3 e
   IE12:IF13 nas duas QAs. Preservar os 12 moldes IF inalterados e o escape
   dos literais da ANALISE. O bloco IE:IF já teve timeout antes desses moldes.
   Acrescentar controle de recuperação com erro próprio, sem apagar o erro
   ou contaminar outra entidade. API de escrita não dispara onEdit.
7. Restaurar todas as entradas; comparar montagens/valores/tipos/notas/
   validações, conferir visual e ocultação das auxiliares. Rodar os checks
   adequados, salvar relatório/evidência sanitizada e atualizar a PR88.
8. Conferir checks no novo head e deixar pronta para revisão, sem merge.

## Evidências e limites

Os arquivos privados não estão no Git. No HD do Linux, a pasta de trabalho
era `Claude/02-RPG/_trabalho/ficha-integracao-5156-20261104/`, dentro de
`/media/mizuki/HD Externo II/`. Evidências relativas à raiz do repositório:

- `nuvem-b47/saidas/isolamento-pr88/`: protótipo, propostas e base GS;
  snapshots antes-0/1 inválidos, conforme acima.
- `nuvem-b47/saidas/correcao-contagem/`: entrega anterior da PR88.
- `nuvem-b47/saidas/integracao-5156/`: cinco partes antigas das QAs usadas
  pelo teste opcional de transporte. Se indisponíveis, obter cópia fresca
  nativa dos projetos; não tratar ausência da fixture como teste aprovado.

Usar Google Sheets nativo. Nunca importar Excel/Office, executar
construir()/continuar() em ficha preenchida, ampliar acesso ou criar
acionadores. Não versionar snapshots, dados pessoais ou credenciais.
Preservar mecânicas, custom, salários, fotos, montagens, contextos,
12 invocações, nove posições de Família e contrato ANALISE12/esquema2.
PR31 deve permanecer intocada; último head conhecido
`765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.

Recomendar Sol/High para implementar/ensaiar e Sol/Medium para revisão,
sem alterar configurações automaticamente. Não afirmar 100% ou validação
final antes dos ensaios pendentes. Começar com estado encontrado e próxima
ação concreta.
