# Páginas de leitura e versão do arquivo

28/10/2026 · PR31, fora do pacote/bot e não instalado. Main produtor ef361cc e
bot main de42447 reconferidas. Criação continua bloqueada.

## O que foi implementado

`conferencia_paginas.gs` acrescenta duas funções internas de integração:

- `r53NovaFichaConferenciaPlano`: confere a sequência v2 concluída e retorna
  protocolo, assinatura, hash do coordenador e quantidades.
- `r53NovaFichaConferenciaPagina`: confere até quatro perfis conhecidos,
  reconfere coordenador/registros e retorna só hash de estados e contadores.

Não executam Aplicar, não escrevem células/imagens e não gravam nem checkpoint
em DocumentProperties. Cache volátil é descartado, trava do documento liberada
em sucesso/erro. Índice é inteiro dentro do plano fixo; não recebe endereços,
nomes de perfis, plano arbitrário ou configuração de escrita do navegador.

Limite de 631 perfis (599 + até 32 recuperações), 158 páginas. O plano normal
sem recuperações tem 150 páginas; último lote não é truncado. Orçamento local
180 s por página: estouro recusa o lote inteiro, sem marcar progresso parcial.
Não é garantia de latência Google. Nenhuma URL/rede foi adicionada ao produtor.

O progresso fica a cargo do integrador. Isso permite observar a versão Drive
antes/depois de cada chamada sem a própria página alterar o documento para
salvar seu cursor. O leitor anterior com checkpoint continua disponível; não
apagar seu registro ou migrar automaticamente uma rodada para a outra.

Protocolo `carteira-conferencia-pagina-1`: saída contém assinatura, sequência,
perfis/porPagina/paginas e quatro indicadores falsos. A página acrescenta índice,
quantidade lida e hash do lote. Não retorna arquivo/modelo, conteúdos, notas,
validações privadas ou imagens. Contexto/hash continuam sem ser autenticação.

## Consumidor e limites

Na PR84 do bot, `carteira_viva/leitura_temporal.py` implementa uma guarda interna,
em memória. Observa versão Google autenticada antes/depois do plano e de cada
lote, conserva a mesma versão por toda a rodada e reconfere contexto/acesso.
Alterar e depois restaurar o conteúdo não redefine a versão esperada da operação.
Não guarda tokens nem oferece rota ou comando para habilitar a criação.

Repetição da última página não avança duas vezes. Erro temporário/cancelamento
não confirma o lote; erro de acesso/contexto, versão alterada ou resposta inválida
invalida a rodada. Prazo total padrão 30 min, configurável só no código até 1 h.
Reinício do processo exige nova leitura, sem repetir a inicialização. A finalização
faz nova observação da versão e do contexto depois da última página.

A guarda usa `versao_drive_estavel_observada`, não um selo de snapshot. Cálculos
podem mudar sem uma edição percebida; bloqueio de conteúdo também não congela
resultados de fórmulas externas. `consistencia_temporal_verificada`, imagens,
conferência final e criação continuam falsos. A etapa de preservação global,
arte, automações/treinos/notas e responsável ainda precisa de conferência própria.

## Caminho de execução ainda não entregue

As funções GS recebem objetos internos de planilha. Não são um endpoint HTTP
publicado que a Carteira consiga chamar só com um ID. O par de callbacks Python
é uma interface de integração, não transporte Google implementado.

A API `scripts.run` exige implantação como executável de API, um projeto Cloud
padrão em comum e token com todos os escopos usados pelo projeto. Não presumir
que `drive.file` autoriza executar esse projeto de SpreadsheetApp, ou passar um
objeto Spreadsheet como JSON. Não foi feita publicação, habilitação de API,
concessão adicional ou alteração das fichas oficiais para obter essa execução.

Próxima integração precisa preservar o acesso por arquivo escolhido: adaptar a
validação/estado ao backend e ao Sheets REST, ou apresentar separadamente uma
rota de execução do produtor compatível e suas permissões. Não ampliar escopos
ou tornar criar_por_modelo permissivo para contornar essa lacuna. Prova de código
instalado, autorização, isolamento, fila/cotas e execução nativa seguem pendentes.

## Testes

16 cenários offline novos passaram: 631 perfis em 158 páginas, lote final,
nenhuma gravação (incluindo propriedades), repetição, índices/tipos inválidos,
assinatura, prazo, registro mudado, sequência incompleta e liberação de trava.
Os perfis grandes usam operações pequenas controladas; não é aplicação/leitura
nativa de 631 perfis reais sobre uma ficha. Teste anterior de financeiro/progressão
e Classe 0 real em VM continua separado.

`r53/testes/gerar_contrato_paginas.js` produz uma amostra sintética chamando as
funções GS reais em VM. `--conferir` valida o JSON sem regenerar. A mesma saída
foi copiada para fixtures do consumidor e aceita pelo teste Python. Isso prova
formato de saída, não autenticação, execução remota ou cálculo Google.

Comando: `node r53/testes/inicializacao_conferencia_paginas.js`.
CI completo desta continuação em fechamento; total previsto 2.952 cenários.
Sem Google/Discord, oficial/jogador, acesso novo, modelo pago, merge/deploy/Gateway.
Sol Alto para adaptador/integração; Médio para revisão focal.

## Referências consultadas

- [File.version](https://developers.google.com/workspace/drive/api/reference/rest/v3/files):
  contador crescente de mudanças do arquivo; `headRevisionId` não é a revisão
  nativa do Sheets, pois esse campo é para conteúdo binário.
- [Restrições de conteúdo](https://developers.google.com/workspace/drive/api/guides/content-restrictions):
  não são imutabilidade e não congelam resultados de cálculos.
- [LockService](https://developers.google.com/apps-script/reference/lock/lock-service):
  coordena trechos de código, sem bloquear edição humana da planilha.
- [Execução pela API](https://developers.google.com/apps-script/api/how-tos/execute):
  requisitos de implantação, projeto, escopos e tipos básicos de parâmetros.
