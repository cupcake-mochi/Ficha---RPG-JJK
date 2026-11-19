# Cura recebida pelo Exaurido — investigação

Base: PR53 `c2ba96e009159608298082b2306723bd0a24d532`, sobre PR52/51.
Ramo separado `codex/auditoria-cura-exaurido-20261104`. Fontes alteradas apenas neste ramo; nada aplicado em produção. Sem merge, oficiais, jogador ou PR31.

## Regra e distinção necessária

Livro R65, commit `a98d4af981cd7166a403f7189eeb1bc3a22e4ad4`:
efeitos de cura recebidos pelo Corpo Exaurido recuperam metade da vida normal,
arredondada para baixo, mínimo 1 quando positiva. Descanso longo propício
recupera 25% do máximo e **não** recebe outra divisão por dois.

A caixa FICHA!AM26 (±) recebe uma variação final. `aplicarDelta_` usa
`aplicaPasso_`; o atalho `r53LivreDelta_` usa `r53LivrePasso_`. Nenhuma rota
classifica o valor positivo como cura nem lê o corpo. Isso permite ajustes
manuais e valores cuja redução já foi calculada. Dividir todo positivo por
dois mudaria esse contrato e duplicaria descontos já feitos pelo jogador.
A edição direta da vida atual também é uma entrada livre.

Não foi identificada uma entrada específica de cura recebida neste fluxo.
Não confundir cura produzida por um feitiço com cura recebida pelo conjurador:
a limitação depende do alvo, e não autoriza reduzir todo feitiço de quem
possui Corpo Exaurido.

## Testes

`node r53/testes/cura_ajuste_final.js`: seis cenários em cada uma das duas
funções reais, cobrindo positivo bruto, positivo já reduzido, mínimo positivo,
teto, dano consumindo temporária e positivo preservando temporária. Aprovados.
O teste não cria uma implementação paralela nem declara cura automática.

Cópia descartável nativa derivada da QA da PR53, sem instalar novos scripts.
Corpo Exaurido, base corporal publicada válida, máximo 20. Entradas de
preparação via API; aplicação do ± pela interface para
disparar onEdit. Não são medições de desempenho.

## Implementação aprovada e preparada

O usuário escolheu a opção explícita **Recursos → Aplicar cura**. O valor é
bruto, destinado ao personagem da FICHA, não às invocações. CuraRecebida.gs
aplica a metade somente com Corpo Exaurido e base corporal válida (B126),
arredonda para baixo, mínimo 1 para cura positiva e limita ao máximo.
Preserva vida temporária, vida acima do máximo e o contrato do ±.

A confirmação mostra o resultado antes de gravar. Cancelar, dados inválidos,
lock ocupado e alteração de vida/Origem durante o diálogo não gravam.
O lock é adquirido depois do diálogo; a releitura reduz conflitos, mas não
impede edições manuais ou outras rotas que não respeitem o mesmo lock.

Teste `cura_recebida.js`: 35 verificações aprovadas. Teste de empacotamento
confere a entrada pública e o registro do menu sem carregar o módulo pesado.
A ação fica em arquivo separado no pacote integral; nenhuma geração de abas
ou mudança das mecânicas de descanso é necessária.

## Evidência nativa e limites

Antes da instalação, no Exaurido com máximo 20 e vida 1:
- ±9 resultou em 10, campo de ajuste limpo.
- ±4 resultou em 5, sem nova redução.

Somente a cópia descartável recebeu o acréscimo ao Codigo e o registro do
menu no onOpen. Snapshot privado anterior SHA-256
`a4c69dafe55ff33b269a340edbdca9cf02cdeeee3519935c8223c9fb7fd40b8f`.
Código salvo, editor recarregado e releitura integral idêntica ao preparado.
O usuário concluiu a autorização solicitada pelo Google. Ensaios pela interface:
- Aplicar cura 9: confirmação exibiu ganho 4 e vida 1 → 5; após Sim,
  releitura nativa confirmou D26=5, J26=20 e AF26=0.
- Aplicar cura 1: confirmação exibiu ganho mínimo 1 e vida 5 → 6;
  escolhido Não, vida permaneceu 5, conferida na interface.
- Código salvo e relido integralmente antes do ensaio, sem divergências.

Cancelamento e mínimo foram vistos na interface; teto, dados inválidos,
conflito durante confirmação e corpos alternativos foram cobertos localmente,
não repetidos no Google. Android não testado. Descanso não foi reexecutado
nesta rodada: a ação não chama nem modifica suas rotas. Não equivale a
validação integral da ficha nem autoriza promoção automática.

## Atualização futura de fichas existentes

Exige autorização de destino, snapshot atual e ensaio em cópia. Confirmar
pré-requisitos das PR51–53, especialmente DADOS_CUSTOM!B126 e vida máxima.
Adicionar CuraRecebida.gs e uma chamada r53CuraMenu_ no onOpen existente,
preservando os demais serviços. Alternativamente, na migração incremental
ensaiada, anexar o conteúdo ao Codigo existente; nunca instalar nos dois
lugares simultaneamente. Conferir unicidade de funções, salvar, recarregar,
reler e testar o menu. Não instalar pacote integral nem reconstruir a ficha.
Nenhuma oficial, jogador ou PR31 foi alterado; nenhum merge foi realizado.

Revisão focal: Sol/Medium; implementação integrada: Sol/High, conforme AGENTS.md.
