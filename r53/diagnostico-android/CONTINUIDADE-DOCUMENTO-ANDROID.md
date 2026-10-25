# Comparação da oficial e preparação da alternativa por cópia

23/10/2026. Base: `codex/otimizacao-android-r53`, `255b984`.
O usuário pediu continuar a investigação e autorizou usar a nova ficha como
alternativa caso a causa não fosse encontrada. Essa autorização não equivale
a uma conclusão de que a causa foi identificada ou de que a troca já acabou.

## Resultado desta etapa

A oficial e a cópia compartilhada abaixo foram lidas em 77 blocos CADA,
cobrindo 710.587 posições por documento, nas 27 abas. A comparação de todo o
conteúdo representado pela máscara foi exata:

- valores digitados e fórmulas;
- resultados/tipos retornados;
- notas, validações, textFormatRuns e chipRuns.

Não houve diferença. Os dois hashes de conteúdo são
`7799a8109be930d30ddf23736759ffbeb80345da64b7cc1f54aea14d12c1c127`.
Cada ficha tem 121.311 fórmulas, 27.383.151 bytes UTF-8 de texto de fórmulas,
6.440 células com validação e nenhum erro efetivo retornado. As propriedades
de abas e 60 regras condicionais também coincidem. O modifiedTime ficou
estável em cada arquivo durante as leituras. A API não fornece um snapshot
transacional: estabilidade é uma sentinela, não garantia de atomicidade.

A leitura inclui ANALISE integral, MONTAGENS e os dados/histórico salariais.
As permissões retornadas têm o mesmo proprietário e o mesmo acesso público
de leitor, sem descoberta pública. Não houve mudança de acesso.

Evidência sanitizada: `COMPARACAO-DOCUMENTOS-2026-10-23.json`.
Dados completos ficam em `nuvem-b47/saidas/diagnostico-documentos-20261023/`.

## Identificação dos documentos

- Oficial original: https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit
- Cópia compartilhada comparada: https://docs.google.com/spreadsheets/d/1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8/edit
- Existe outra cópia com o mesmo título, ID
  `1E9V_bvYXUsaCEmHr7dHa79REnRan9mopZ7JX7jkasMY`. Não confundir os controles.

Foi solicitada ao usuário a confirmação de qual cópia abriu no seu Android e
no do amigo. O registro sanitizado anterior confirma uma cópia funcional,
mas não informa o ID. A cópia compartilhada é a candidata examinada; não foi
declarada confirmação específica do usuário enquanto essa resposta não chegou.

## Conclusão da investigação com o acesso atual

Não foi encontrado defeito ou diferença nesses campos do conteúdo que
explique o travamento exclusivo da oficial. Isso favorece usar a cópia como
alternativa prática, preservando as mecânicas. Não demonstra que histórico,
cache, propriedades ou acionadores causam a falha.

A comparação não incluiu todos os formatos, mesclas, proteções, imagens,
comentários ou histórico. O código da cópia foi registrado anteriormente como
igual ao da oficial, mas não foi relido nesta etapa.

O Google Drive/Sheets está acessível. A busca pelas capacidades disponíveis e
por plugins não encontrou acesso utilizável ao navegador da sessão ou à API
de Apps Script. Os conectores atuais não leem propriedades, acionadores ou
execuções. O teste de um Script ID no endpoint de arquivos do Drive retornou
404; esse endpoint não verifica a existência/conteúdo de um projeto Apps Script.
Não concluir que o projeto foi apagado ou que falta acesso à própria planilha.

Foi preparado `auditar_contexto_android.gs`, que pode ser adicionado como arquivo
separado ao projeto vinculado e executado MANUALMENTE quando houver acesso ao
editor. Restringe os IDs conhecidos, lê somente propriedades de aparência,
marcadores salariais, intervalos nomeados e acionadores visíveis à conta. Não
chama o módulo pesado, não modifica células/propriedades, não instala eventos.
Teste local de quatro cenários passou, incluindo agenda herdada, erro parcial
de acesso e recusa de outro documento. Não foi instalado ou executado no Google.

Os registros anteriores contam três acionadores na oficial e zero na cópia.
Essa contagem ainda depende de releitura atual. Antes de mudar acionadores,
correlacionar uma tentativa Android com o painel Execuções e confirmar se esse
cliente de fato dispara algum evento. A documentação de gatilhos exige acesso
de edição para eventos de abertura; não presumir que o mesmo caminho roda para
um amigo com acesso apenas de leitura.

## Dependência concreta da alternativa por cópia

`DADOS_SALARIOS!L2` é atualmente idêntico nos dois documentos e contém `agenda`
apontando ao Script ID da ORIGINAL. Isso foi copiado como dado. Não prova que
existam acionadores instalados no novo projeto. O rótulo da configuração também
não comprova que a conferência diária esteja ativa na cópia.

As fontes Apps Script não contêm o ID fixo da oficial e não usam openById ou
openByUrl. Elas operam sobre a planilha vinculada. O código instalado foi
comparado no trabalho anterior; uma atualização exige captura atual própria.

Para concluir a alternativa sem perder automação:

1. Confirmar o ID da cópia que efetivamente abre e conferir alterações posteriores
   à captura. Se tiver havido edição em qualquer documento, reconciliar entradas
   e salários antes da troca. Não reaplicar os 37 lotes da promoção.
2. Com acesso ao projeto vinculado da cópia e à conta responsável, executar o
   diagnóstico somente de leitura. Conferir código atual e guardar a captura.
3. Na cópia escolhida, usar a função existente `ativarSalarioDiario()` pelo
   editor ou o menu **Salários → Ativar conferência diária** na interface web.
   Ela já possui idempotência: instala os handlers de diário, edição e revisão
   de abertura ausentes, atualiza o marcador de edição e vincula a agenda ao
   projeto atual. Pelo código, não é uma reemissão nem uma rotina de apagar
   créditos; ainda exige conferência do estado realmente instalado.
4. Reler os acionadores e os marcadores: agenda e salario_edicao devem apontar
   ao projeto da cópia, handlers sem duplicação e eventos vinculados à cópia.
   Repetir a abertura no Android APÓS essa configuração. Se o problema aparecer
   só então, há uma contraprova mais forte para investigar o contexto de eventos.
5. Em um ensaio de abertura, não usar `desativarSalarioDiario()` como se removesse
   todos os eventos: ela remove SOMENTE o diário; conserva edição e abertura.
   Qualquer reversão deve atingir só os eventos criados no ensaio e preservar
   o estado anterior. Não remover acionadores da original por tentativa.
6. Depois de aceitar a cópia com suas rotinas, passar a usar seu endereço nos
   locais que apontavam à ficha antiga, incluindo cadastro/leitura do bot quando
   aplicável. O contrato ANALISE permanece igual; nenhuma mudança no código do
   bot foi necessária para a comparação. Não enviar mensagens/comandos ao bot
   nem trocar vínculos externos automaticamente sem o escopo correspondente.
7. Preservar a original como contingência e histórico. Não excluir documentos,
   reconstruir fichas ou alterar permissões para efetuar a troca.

Nesta etapa não foram renomeadas ou modificadas as planilhas, nem instalados,
removidos ou ativados acionadores. A investigação do conteúdo está concluída;
a causa específica da falha permanece não isolada e a configuração das rotinas
da cópia é uma aplicação nativa pendente por falta de acesso ao Apps Script.

## Referências consultadas

- Google inclui criar uma cópia entre as formas de retomar trabalho com arquivo
  que falha: https://support.google.com/docs/answer/7505592?hl=en
  Isso é uma alternativa operacional, não prova da causa do defeito específico.
- Eventos simples: https://developers.google.com/apps-script/guides/triggers
- Eventos instaláveis e visibilidade por conta:
  https://developers.google.com/apps-script/guides/triggers/installable

Próxima ação: GPT-6.1 Sol, High, para conferir o estado do Apps Script e preparar
a troca; Medium para registrar a confirmação do ID e o aceite Android.
