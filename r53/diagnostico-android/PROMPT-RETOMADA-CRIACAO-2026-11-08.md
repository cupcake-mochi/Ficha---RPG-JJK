# Pausa solicitada · Criação com nível fixo · 08/11/2026

> Retomada concluída no ramo `codex/criacao-nivel-fixo-20261108`. Consulte
> `CORRECAO-CRIACAO-NIVEL-FIXO-2026-11-08.md` para o estado final. O texto
> abaixo conserva o checkpoint histórico, anterior à correção ensaiada.

O usuário pediu parar e salvar porque vai mexer no disco E.
**Não retomar automaticamente.** Ao receber nova instrução para continuar,
verificar os caminhos disponíveis; não pressupor que o E permaneceu igual.

## Estado salvo

Ramo WIP separado `codex/wip-criacao-nivel-fixo-20261108`, iniciado em
`fe52bb1d5f0b98bf9cf4d30cdb7c585868fd8e74`, auditoria de AQ01.
Não é entrega pronta: não abrir PR de implementação como concluída.
Sem merge, oficiais, jogador, main ou PR31. Não delegar a subagentes.

AQ01: Criação cresce até o fim da Classe segundo R44, mas a referência
R66 mantém o nível fabricado. Ler a auditoria de aquisição de 07/11 e seu
JSON sanitizado antes de retomar. Referência R66 fixada em
`cupcake-mochi/JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Implementação parcial salva:

- `ficha-v01/aquisicao-criacao-r66.json`: referência explícita e trecho
  delimitado. O manual local histórico não foi reescrito como se fosse R66.
- `extrair_invocacao.py`: reconciliação focal com guarda da frase histórica,
  metadado de correção e `acompanha=False` em Criação.
- `invocacao-do-livro.json`: extração atualizada. A extração foi executada
  com sucesso, mas a conferência focal ainda falta.
- `ficha_invocacoes.py`: tabela booleana 1/0, remoção do ramo de fim de
  Classe e notas de aquisição/nível obtido/nível calculado atualizadas.
  Obtido vazio conserva a prévia histórica no nível do invocador; orientar
  preenchimento explícito, sem criar regra nova para o vazio.
- `r53/criacao_nivel_fixo_runtime.js`: esboço de recuperação leve dos
  valores e ajuste estrito do retrato antigo, ainda sem ensaio.
- `preparar_criacao_nivel_fixo.js`: esboço de preparador com base PR88 exata,
  snapshots, reversão e notas. Ainda não executado.
- `r53/testes/criacao_nivel_fixo.js`: teste focal escrito, não executado.
- `r53/empacotar_script.py`: adição parcial do runtime ao bootstrap.
  **Faltam a guarda no onEdit do bootstrap, o ajuste do retrato no
  carregador e a inclusão do novo arquivo na lista de legados.**

Os arquivos `criacao_nivel_fixo_plano.json`, `criacao_nivel_fixo_notas.json`
e `criacao_nivel_fixo_suporte.json` **ainda não existem**. Portanto os
módulos WIP que os exigem não estão executáveis. Não confundir com plano
validado, script instalado ou teste aprovado.

## Geração e artefatos privados

Diretório privado ignorado:
`nuvem-b47/saidas/criacao-nivel-fixo/`, no disco C, dentro do workspace.

- `base/`: todos os GS anteriores às alterações.
- `era-Codigo-fresco.gs` e `ciclo-Codigo-fresco.gs`: leituras integrais
  pela interface, ambas iguais à PR88 final, SHA-256
  `36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc`.
- `gerados-wip/apps-script/`: arquivos gerados nesta sessão, ainda sem
  comparação integral. O XLSX gerado também foi guardado nessa pasta;
  não importar para o Google. Os artefatos gerados versionados foram
  repostos à base depois dessa cópia, para não apresentar geração sem
  validação como entrega. O trabalho de fonte permanece salvo no WIP.
- `geracao.log`: a geração final com Python `-X utf8` terminou em saída 0.
  A primeira tentativa sem esse modo falhou em escrita cp1252. Não
  afrouxar hashes ou adicionar mudança mecânica para contornar encoding.

Não ficou processo de geração em execução. A sessão de comando foi
encerrada e retornou 0. Uma tentativa de comparar modelos no Node REPL
excedeu 30 s e reiniciou seu estado; **não produziu plano nem aprovação**.
Para leituras de modelos grandes, usar execução com tempo suficiente.

Os snapshots novos de metadados/células/MONTAGENS desta sessão ficaram
somente na memória das ferramentas; **não são backups de aplicação**.
Refazê-los e salvá-los integralmente antes de qualquer escrita futura.

## Google: somente leituras nesta sessão

Nenhuma escrita Google, aplicação de fórmula, nota ou instalação de código
foi feita. Nenhuma entrada de teste foi preenchida. Não há restauração
pendente nas planilhas. A interface só abriu os editores das descartáveis
para ler e guardar os scripts; não executou funções ou criou acionadores.

Alvos autorizados continuam somente as duas descartáveis:

- Era: `1LBZOf9vJmd02xNvAyMX5r0NDRL-NInzicc7l5q3HBDQ`.
  Script: `1IBTaNa9I6DzZXQlXQcre-oMd8b0rqq55hDXF5AODp3jdkhFigt31ccIG`.
- Ciclo: `1HQqGOVGky5qlGOyk8h4QgOQb4Zwq3BXWaM65Q7vGgqU`.
  Script: `1WHzpRRE_B9bMY2V1oVkjQgOTFRKdRSkT4BtXadCRxUy-UCNnAuFJ6EhC`.

Usar Sheets nativo e somente incremento estrito. Não instalar pacote
integral, importar Office ou chamar construir()/continuar() nas fichas.
PR88 e PR31 não foram modificadas nesta sessão.

## Retomada após autorização

1. Conferir estado local/remoto e acessos. Ler novamente os scripts das
   duas QAs e exigir a base exata; não aplicar usando o snapshot de hoje.
2. Revisar o fonte parcial e a referência. Repetir extração `--confere`.
   Comparar a geração guardada com `base/` (ou regenerar em série).
   Confirmar delta esperado: 13 valores/fórmulas (BQ5 e FO2:FO13) e
   36 notas. Criar os três JSONs com antes/depois exatos; suporte previsto
   é FN/FP nas 12 linhas e BP5, sem alterar esses vizinhos na instalação.
3. Completar a integração do runtime no empacotador. O preparador nativo
   já esboça a guarda e o ajuste do retrato; testar recuperação direta,
   mista, idempotência e recusa antes de mutações. Preservar os moldes
   IF e o escape da ANALISE da PR88.
4. Comparar integral/incremental, gerar pacote local e rodar os testes
   focais e o smoke apropriado. O pacote integral serve à conferência,
   não à instalação nas descartáveis.
5. Só após snapshots completos frescos, salvar o incremento nas QAs,
   reabrir/reler integralmente e conferir os hashes. Aplicar os alvos
   exatos com guarda imediatamente antes. Ensaiar quatro aquisições,
   limites de nível abaixo/igual/acima, obtido vazio, novo projeto,
   vida/espaços e débito. Fazer recuperações por onEdit real nas duas.
6. Restaurar todas as entradas, comparar MONTAGENS e metadados, ocultar
   auxiliares e conferir o visual. Salvar relatório honesto da correção
   e só então preparar PR de implementação, sem merge.

Sol/High para implementar/ensaiar; Sol/Medium para revisão posterior.
Não alterar configurações automaticamente.
