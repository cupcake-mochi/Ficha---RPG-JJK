# Revisão da integração salarial · 24/10/2026

**Correção local validada; ensaio e tempo completo no Google ainda pendentes.**
Nenhuma escrita foi feita em planilhas, projetos Apps Script ou acionadores nesta sessão.

## Base e evidência recebida

- Trabalho em `codex/otimizacao-android-r53`, atualizado em `27d848f91a159ac26b5da2a3f713ae64894663b9`.
- Conferido `a353fc2b1c39f5ad098c04a2990ffdeee1f43b68` em `claude/project-thread-0fb9fh`; só acrescentava o registro do ensaio, agora incorporado ao plano.
- Nesse registro, o trecho salarial terminou em 9,6 s, com créditos de 75.000 e 112.500. O total informado de 337.500 inclui saldo anterior; os dois novos créditos somam 187.500. Não confundir os valores nem tratar 9,6 s como duração integral do onEdit.
- Cópia salarial indicada no plano: `1ESL-AageFm_eo9ybp1ITFAAKm1t6I2FKJyYp8-SFOYU`. Definitiva A: `1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8`. IDs não foram usados para escrita nesta etapa.

## Correção

O retorno de `r53SalarioLote_` após 12 s deixava de entregar a edição ao restante do wrapper.
O preparador agora renomeia a entrada existente para `r53OnEditOriginal_` e acrescenta
a entrada que chama `r53SalarioOnEdit_`. O corpo original é preservado, retirando
somente a chamada salarial antiga quando presente. O evento original, incluindo
`range`, `source`, `value` e `oldValue`, chega à mesma rotina uma única vez.

A edição termina e confirma suas escritas antes de iniciar o fechamento salarial.
Isso elimina a necessidade de enfileirar/reproduzir efeitos de cartões, XP ou cores.
Se essa primeira parte consumir 8 s ou mais, apenas a conferência salarial aguarda
uma nova edição. O limite é uma admissão conservadora, não uma garantia sobre a
latência das APIs. Edições sempre demoradas podem adiar o salário repetidamente;
o ensaio nativo deve verificar essa situação antes de aceitar a solução.

As áreas próprias de emissão, missões, Grau e saldo conservam o tratamento pelo
`salarioEditar_`. O cache é invalidado antes de tratar uma edição de regra/Grau,
mesmo que ela esgote o prazo e adie a conferência. C27 não inicia o lote. Rotinas instaláveis existentes continuam
responsáveis pelo salário nos projetos em que estão ativadas. Não há criação
de acionadores, alteração de permissões ou reconstrução de ficha.

Antes da primeira escrita salarial, `salario_lote_reparar=1` é persistido nas
propriedades do documento. O próximo vencimento só entra no cache depois de
`SpreadsheetApp.flush()` concluir sob bloqueio. Falhas mantêm a marca e invalidam
o cache. Uma tentativa de concluir a fila de escritas também acontece sob o
bloqueio quando há erro de setter; a marca permanece para a próxima conferência.

Na recuperação, o livro persistido é relido diretamente, sem confiar no resumo
por fórmulas. Créditos confirmados determinam o ciclo aberto. Mesmo sem novos
créditos, estado e painel são recompostos. Livro com lacuna, valor inválido ou
identidade repetida interrompe a recuperação para revisão, preservando os dados.
O caminho normal mantém a leitura única de DADOS_SALARIOS.

O preparador aceita instalação sem SalarioLote ou atualização da experiência
`a2ca590` com SHA-256 conhecido. Recusa módulo desconhecido, chamada órfã,
duplicação de módulo/entrada e reaplicação da integração. Mantém os outros
arquivos e o manifesto exatamente como recebidos. Não publica nem executa nada.
O teste entrou no smoke, com fixture pública da fonte anterior para funcionar
também no clone raso do CI, sem subprocesso Git nem acesso à rede.

O padrão de solo no instalador novo passou a 1, conforme decisão já registrada
no plano. Esse ajuste de fonte não regrava pesos nem salários de fichas existentes.
O fechamento em lote continua sendo um delta experimental separado; o pacote
integral não passa a instalá-lo automaticamente.

## Verificação local

Todos os comandos abaixo passaram nesta sessão:

| Comando | Resultado |
| --- | --- |
| `node r53/testes/salario_lote.js` | 28 cenários: evento único, lote acima de 12 s, edição lenta, limpeza/colagem, recuperação, cache, bloqueio, paleta e atualização do projeto |
| `node salarios/testes.js` | 112 verificações de regras, missões, Grau, idempotência e falhas |
| `node salarios/testar_abertura.js` | Patches estritos, abertura e paleta |
| `node r53/testes/lote_paleta.js` | Regressão do lote de cores |
| `node r53/testes/paleta_segundo_plano.js` | Bordas, arte e quatro cenários |
| `.venv/bin/python nuvem-b47/conferir.py --smoke` | Pacote de nove arquivos, runtime, salários, notas, sintaxe e referências |
| `git diff --check` | Sem problemas |

A matriz injeta falhas no livro, L2, O48, O69:O72, status e publicação do cache;
simula flush com zero, parte ou todos os blocos persistidos, e um resumo por
fórmulas antigo. A tentativa seguinte conserva os créditos já pagos e restaura
o painel. Uma edição original que lança erro permanece com o erro original.

Os tempos desses testes são de um relógio simulado. O caso lento tem 17.500 ms
do início do wrapper ao fim do flush salarial, com a edição original já atendida.
Esse número **não mede o Google**. O log `R53_ONEDIT` agora registra `ms`,
`edicaoMs` e a fase final; os logs `SAL` continuam registrando as etapas do lote.
Timeout imposto pelo Google pode impedir o log final; nesse caso, consultar
também o estado e a duração da execução no Apps Script.

## Rede e login

Os primeiros testes no terminal sem permissão adicional falharam na conexão ao
proxy. Repetidos com rede habilitada para o comando, os três destinos retornaram
`Tunnel connection failed: 403 Forbidden`: `script.googleapis.com`,
`oauth2.googleapis.com` e `accounts.google.com`.

O status atual do ambiente e `/etc/codex/network-policy.json` ainda indicam
configuração restrita, sem esses domínios. O status da aplicação da política
é `unknown`; a negativa observada nos requests é a prova prática do bloqueio.
GitHub e o registro npm funcionaram pela rota autorizada. Nenhum bypass foi usado.

Clasp **3.4.1** instalado em `nuvem-b47/saidas/clasp/`; login não iniciado.
O script local ignorado `nuvem-b47/saidas/salario-20261024/login-google.sh`
testa os destinos antes do OAuth. Usa `-A` com arquivo dentro de `auth/`,
diretório com modo 700 e umask 077. O código OAuth só deve ser informado no
terminal seguro, nunca pelo chat; senha e tokens também nunca passam pelo chat.
Nenhuma credencial foi gerada ou versionada. Antes de usar o script, a
configuração de rede publicada precisa estar aplicada à sessão e permitir os
destinos Google necessários. Não foi solicitado consentimento de conta nesta etapa.

## Continuação nativa necessária

1. Retestar rede e concluir OAuth pelo fluxo seguro. Ler projeto, planilha e
   acionadores atuais. Não assumir que a cópia ainda tem o código do ensaio.
2. Obter snapshot atual e uma cópia descartável para este ensaio. Guardar código
   integral e estado salarial antes da alteração, incluindo livro, L2, missões,
   painel, O86, W86, pesos e cores. Não executar construir/continuar.
3. Preparar o delta sobre a captura atual usando
   `node r53/diagnostico-android/preparar_salario_lote.js captura.json candidato.json`.
   Inspecionar o diff; recusa por divergência exige revisar o código, nunca
   contornar a guarda. Não publicar o pacote integral regenerado.
4. Instalar e reler o delta somente na descartável. Preparar M:N apenas se
   ausente; não repetir emissão nem apagar livro para forçar um vencimento.
   Usar dados fictícios em uma nova cópia de ensaio com períodos vencidos.
5. Editar de fato uma entrada cuja rota atualize um cartão/XP e fechar os dois
   períodos. Conferir valores, fronteiras, painel e efeito da edição original.
   Repetir a edição e conferir ausência de duplicação. Exercitar C27 e as áreas
   próprias; confirmar histórico, saldo manual e cores.
6. Em outra cópia do cenário ainda vencido, instalar apenas um helper temporário
   com guarda do ID dessa QA: envolver `r53SalarioFechar_`, chamar o corpo original,
   fazer flush das escritas e lançar uma exceção deliberada antes da publicação
   do cache. Executar uma edição. Conferir marca de recuperação e cache ausente.
   Remover o helper e reler o código. Editar novamente: mesmo livro, L2/painel
   reparados, cache futuro, marca removida. Ensaiar também falha antes da escrita
   e após o livro/antes do painel. Nunca instalar essa injeção na definitiva.
7. Registrar duração real de cada execução completa, logs `R53_ONEDIT` e `SAL`,
   inclusive recuperação, segunda edição e edição lenta. A meta permanece ~22 s;
   execuções perto/acima de 30 s impedem promoção e exigem outra estratégia.
   Chamar pelo editor com prazo de seis minutos não prova o acionador simples.
8. Só depois do ensaio satisfatório: snapshot novo da definitiva A, preflight
   dos dados/código, delta restrito, releitura e conferência de preservação.

Próxima ação recomendada: GPT-6.1 com esforço alto para o ensaio e interpretação
dos tempos; médio para conferência do registro. Não alterar o modelo automaticamente.
