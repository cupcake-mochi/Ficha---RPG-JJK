# Propriedades financeiras separadas da ativação

30/10/2026 · PR31 · protótipo autorizado pelo mantenedor · não instalado.

`propriedades.gs` acrescenta um perfil independente para as cinco propriedades
financeiras depois de as células terem sido inicializadas pelo REST ou por outro
caminho comprovado. Não muda a assinatura/diário financeiro v1, a sequência de601
fases, o contrato REST ou o pacote instalado. Não cria comando/menu público.

## O que foi implementado

- `r53NovaFichaPropriedadesPrevia(ss, contexto)`: prévia sem gravação, somente
  no contexto interno confiável de uma cópia ativa, distinta do modelo/oficiais/
  cadastradas. Células financeiras precisam estar no pós-estado exato, com fórmulas
  protegidas. Não importa um diário REST ou um booleano do navegador como prova.
- `r53NovaFichaPropriedadesAplicar(ss, contexto, assinatura)`: trata apenas
  as quatro chaves do documento e `salario_edicao` do script. Diário próprio
  `r53_nova_ficha_propriedades_financeiras_v1`, mesma trava/executor de retomada,
  até quatro escritas por chamada. Não escreve células nem reexecuta o financeiro.
- Preservação: hash das fórmulas/configuração, células financeiras limpas e todas
  as outras propriedades de documento/script, incluindo diários/editor/paleta.
  O diário deste próprio perfil é a única exclusão adicional do hash. Valores
  privados não são incluídos em prévia/resultado/diário: somente hashes.
- A retomada fica vinculada ao projeto e à chave temporária da execução. Essa
  chave não identifica o dono Google nem autoriza o backend; troca/rotação recusa
  a operação. Nenhum e-mail ou chave temporária é retornado ou gravado em claro.
- Qualquer acionador visível da conta impede a limpeza, inclusive na retomada.
  O módulo nunca cria/remove acionadores. A lista da conta não prova ausência
  global de rotinas instaladas por outras pessoas; criação continua bloqueada.
- `r53NovaFichaAtivacaoConferir(ss, contexto)` é só inspeção: confere os três
  handlers salariais esperados, tipos, fontes, arquivo nos eventos de planilha,
  duplicatas e marca do projeto. Mesmo se compatíveis, não atesta horário,
  evento real, outras contas ou identidade ao bot, nem declara ativação concluída.

## Limites

O integrador continua responsável pelo contexto confiável. Estas funções não
podem receber contexto do jogador em endpoint/menu e tratá-lo como autorização.
O protótipo ainda não é uma ação pública pronta. Não há ponte autenticada de
atestado Apps Script para o backend `drive.file` nesta entrega.

O resultado de propriedades pode indicar `propriedadesPreparadas=true`, mas
`ativacaoConcluida`, `financeiroConcluido`, `responsavelVerificadoPeloBot` e
`criacaoDisponivel` permanecem falsos. A inspeção não instala as três rotinas e
não transfere a responsabilidade de uma conta para outra.

O [Google documenta que a chave temporária gira a cada30 dias e é específica do script](https://developers.google.com/apps-script/reference/base/session#gettemporaryactiveuserkey).
Ela serve só para detectar troca de execução nesta operação. Os
[acionadores instaláveis são visíveis por conta e executam como seu criador](https://developers.google.com/apps-script/guides/triggers/installable#restrictions).
Não inferir identidade/ausência global a partir dessas duas APIs.

## Testes e próximos passos

46 cenários novos offline aprovados em `r53/testes/inicializacao_propriedades.js`,
incluindo as fronteiras antes/depois de cada escrita, chaves já ausentes, outra
execução/projeto, contextos inválidos, resíduos/notas, concorrência em alvos e
propriedades alheias, recibo terminal, perfil errado e inspeção sem atestado.
Uma expectativa de pós-condição precisou explicitar cinco passos na fixture:
com o limite normal de quatro, a mudança era recusada na retomada, antes do
fechamento; não houve relaxamento da guarda nem expectativa ampliada.

101 cenários financeiros e47 de contrato REST aprovados. Hash REST preservado:
`1001e7c3605c754b5bf04c33cfd65542c90ef4b897deffda40167a2bafb30439`.
O teste novo entra no CI do produtor. CI completo e ensaio nativo ainda pendentes.

Próximo ensaio: cópia privada nova, financeiro no pós-estado, cinco resíduos
fictícios e sentinelas alheias. Aplicar/retomar sem células alteradas, repetir,
inspecionar sem criar acionadores, invalidar a autorização do projeto e enviar
a cópia à lixeira. A conta correta faz login/avisos Google. Não usar cópias ou
concessões revogadas de ensaios anteriores.

Depois faltam ativação própria verificável, demais domínios/conferência conjunta,
concorrência/CAS e prova integrada de Era, Ciclo e servidor. Sem oficial/jogador,
merge, publicação, faturamento, escopo OAuth das Guias ou chamada paga alterados.
Conforme AGENTS: Sol/Alto na implementação integrada; Médio na revisão focal.
