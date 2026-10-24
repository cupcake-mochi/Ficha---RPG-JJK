# Emissão e salários

Extensão incremental da R53, baseada no `main` d56623a. A fonte é `apps-script/Salarios.gs`; a ficha preenchida nunca passa por `construir()` ou `continuar()`, nem por importação Office.

## Uso

Em CONFIGURAÇÃO, a seção **14 · Emissão e salários** fica em K35:Q95, junto ao painel inicial.

Na CARTEIRA, **AT3**, à direita de “Emitida”, é um checkbox nativo inicialmente desmarcado. Marcar grava o dia atual em America/Sao_Paulo na emissão e desmarca ao salvar. O39 oferece a mesma ação nas configurações. A data fica fixa até nova alteração.

Os últimos dez créditos aparecem em **CONFIGURAÇÃO!K78:Q95**, do mais recente para o mais antigo. SALÁRIOS é somente a escrituração técnica oculta, assim como DADOS_SALARIOS; nenhuma guia salarial extra aparece na navegação do jogador. Os lançamentos integrais permanecem preservados.

- O38: data de emissão fixa, editável. O39 grava o dia atual em Brasília e desmarca depois de salvar. Uma reemissão posterior ao último salário reinicia o próximo ciclo sem retirar créditos; uma data anterior não repete períodos pagos.
- O40: ativa o salário. Desligar pausa a apuração; religar apura períodos pendentes.
- O41: intervalo em dias corridos, padrão 30. O42: participações para salário completo, padrão 3. O43: parcela mínima, padrão 25%. O44: exige participação; desmarcar concede a referência integral.
- O54:O58: salário por Grau. O62:O67: pesos das missões. Os valores do livro são ¥150.000, ¥300.000, ¥600.000, ¥1.200.000 e ¥2.400.000; curta/padrão 1, longa 2, final de arco 3. Solos começam em 1 por decisão da campanha de 24/10/2026; a campanha pode alterá-lo. Essa mudança do instalador só afeta instalações novas, sem regravar pesos nem créditos existentes.
- O48, O69:O72: vencimento, início, participações, previsão e último fechamento. O49 mostra os créditos acumulados; O50 mantém visível a referência integral do Grau atual.

O saldo manual continua em **FICHA PESSOAL!O86**, inclusive fórmulas como `=150000-500`. **W86 — TOTAL DISPONÍVEL** soma esse resultado aos créditos do histórico **SALÁRIOS**. Não copie os créditos para O86: isso somaria a mesma renda duas vezes. Para gastar, continue descontando do campo manual; ele pode ficar negativo enquanto o total disponível permanece positivo.

## Missões e fechamento

Os quatro blocos de missões (AW, BC, BI e BO, linhas 15–87) são monitorados. Ao completar nome e tipo, a missão recebe data e identidade persistentes na nota da célula, e um registro na aba técnica oculta DADOS_SALARIOS. Corrigir nome/tipo conserva a data. Para substituir por outra missão, limpe primeiro o nome antigo. Nomes iguais em linhas independentes são aceitos. Copiar/mover uma missão com sua nota conserva sua identidade, contando uma vez.

Missões anteriores à instalação não recebem uma data presumida. Para informá-la ou corrigir uma data, selecione a missão e use **Salários → Data da missão selecionada**. Não é possível alterar pagamentos fechados por essa operação. Uma missão sem nome ou tipo válido não participa; remover uma missão do painel retira sua participação de períodos ainda abertos.

O ciclo inclui sua data inicial e exclui o dia do próximo fechamento: emissão em 20/10, intervalo 30, primeiro pagamento em 19/11; missões de 19/11 pertencem ao próximo ciclo. O Grau vigente antes dessa fronteira é registrado no fechamento. Alterações de Grau observadas pelo módulo têm histórico próprio; no primeiro ciclo, usa-se como referência o Grau existente ao iniciar o acompanhamento. A planilha não reconstrói mudanças anteriores à instalação.

Pagamento: `floor(referência × [mínimo + (1 − mínimo) × min(participações, meta) / meta])`. Sem verificação de missões, paga-se a referência. Períodos fechados guardam Grau, referência, meta, pesos, parcela e valor; mudanças posteriores não reescrevem esses registros. As regras configuradas valem para os períodos ainda não fechados, inclusive pendentes.

Há apuração ao editar emissão/regras, preencher missões ou alterar Grau. O checkbox de emitir hoje só reinicia o ciclo aberto e atualiza a previsão, sem reabrir pagamentos. O menu **Ativar conferência diária** instala três acionadores: um diário entre 03h e 04h em America/Sao_Paulo outro para registrar edições e um de abertura para revisar ajudas e paleta. A edição instalável tem orçamento de seis minutos e não disputa os trinta segundos dos cartões/XP. Os acionadores usam a conta que os instala e somente o documento vinculado. Acionadores instaláveis não acompanham uma cópia: ative o diário em cada ficha copiada; o checkbox de reemissão funciona pelo evento simples, mas a apuração completa deve usar a rotina instalada ou o menu. Com o diário ativo, a abertura só mostra os controles, e o vencimento é processado pela rotina diária ou pelo menu Conferir salários agora. O40 permite pausar pagamentos sem apagar o histórico.

## Integridade e instalação

O histórico de pagamentos é a fonte do último fechamento. Um bloqueio do documento serializa chamadas concorrentes; a gravação é confirmada antes de liberar o bloqueio. Uma interrupção depois de gravar um crédito não permite repeti-lo na próxima execução. A proteção do histórico é um aviso contra edições acidentais, não um mecanismo de aprovação do mestre.

O instalador é idempotente e recusa uma área de configuração ocupada ou uma instalação parcial. Ele não modifica O86 nem os cartões da R53. Um arquivo vazio, ainda sem nome de personagem, não recebe pagamentos.

O empacotador R53 inclui Salarios.gs como módulo leve separado. Para atualização do pacote antigo sem regravar megabytes de catálogos, a publicação incremental anexa a mesma fonte ao Codigo.gs existente e adiciona duas chamadas aos eventos. Nunca instalar a fonte nas duas posições simultaneamente. A geração integral posterior substitui esse Codigo.gs e publica Salarios.gs separadamente.

Para preparar essa atualização, guarde uma leitura atual do Codigo.gs em `salarios/saidas/Codigo-antes.gs` e execute `node salarios/preparar_incremental.js`. O preparador confere o hash do pacote R53, recusa uma segunda anexação e valida a sintaxe do resultado. Ele não acessa o Google. Antes da instalação, faça backup nativo, snapshot dos alvos e ensaie em uma cópia nativa da oficial. `instalarSalarios()` aplica somente a extensão; `ativarSalarioDiario()` instala a rotina após essa aplicação.

A publicação de 20/10 precisou de retomada pela API: o serviço Planilhas interrompeu o instalador após criar as duas abas, ambas ainda vazias. `retomar_api.js` prepara os 132 pedidos a partir dos snapshots nativos privados dessa situação e da cópia ensaiada. O lote reutiliza as abas, preserva O86 e não transporta missões ou salários de QA. Foi ensaiado em uma segunda cópia antes da oficial. **Não reenviar esse lote em uma ficha já migrada.** O preparador recusa abas preenchidas, missões anteriores não tratadas e datas diferentes da rodada registrada.

O contrato ANALISE12 conserva suas chaves existentes; o campo de ienes anterior continua representando o ajuste manual de O86. O total e o histórico de salários estão nos campos novos descritos acima. Nenhuma aprovação do bot é concedida pelo módulo.

## Ajuste de navegação · segunda rodada de 20/10

O painel saiu de C320:Q355 para o espaço livre K35:Q95. A migração nativa preservou a data, os valores e os pesos já configurados, ocultou a escrituração e dividiu a antiga mesclagem AH3:AT3 da carteira em AH3:AS3 + AT3. Não foram inseridas linhas nem deslocadas as regras de campanha.

`node salarios/painel_api.js <snapshot-nativo.json>` prepara os 178 pedidos locais a partir de `updatedSpreadsheet`, incluindo os dados dos dois alvos, suas mesclagens e as propriedades de SALÁRIOS. Não acessa o Google. Exige o painel antigo e destino vazio, conserva as configurações e o estilo da carteira, e recusa repetição. Sem argumento, gera somente o modelo do painel, que não deve ser aplicado diretamente a uma ficha preenchida. O snapshot e o lote ficam em `saidas/`, fora do Git.

O teste nativo `teste-carteira-nativo.gs` é bloqueado fora da nova cópia QA. Validou dois ciclos (150000 integral e 37500 reduzido), total 337000 com gastos manuais, e nova conferência sem crédito duplicado. Na segunda rodada, o evento simples da cópia salvou a data e excedeu trinta segundos. Essa ocorrência foi corrigida na terceira rodada abaixo. Para automação confiável, ative o diário de cada cópia: isso instala também a edição com orçamento de seis minutos. A oficial já tem esses dois acionadores. A abertura com rotina ativa agora evita ler saldos em recálculo, deixando a apuração ao acionador.

No Discord, `GC:ficha` leu a cópia atualizada e o seletor abriu Limites da análise. A ficha vazia recebeu as falhas de criação esperadas; a referência R53-04 manteve zero erros/pendências/ajustes, com conferência parcial. Esse bot não certifica datas de missão nem o histórico salarial; os testes de salários foram feitos na planilha.

## Verificar

```powershell
node salarios/testes.js
python -X utf8 r53/empacotar_script.py
node r53/testes/pacote_runtime.js
```

`teste-nativo.gs` só pode ser executado na cópia QA cujo ID está fixado no próprio teste. Não o instale na oficial. Evidências e snapshots privados ficam em `salarios/saidas/`, ignorada pelo Git.

Fonte das regras: `manual.txt`, seção **Recompensas da guilda**, e `referencias-r53/LIVRO-COMPLETO.md`. Referência técnica: [acionadores instaláveis](https://developers.google.com/apps-script/guides/triggers/installable) e [Lock/flush](https://developers.google.com/apps-script/reference/lock/lock).

## Correção da abertura · terceira rodada de 20/10

O perfil nativo isolou 42,374 s nas notas e 35,300 s na revisão da paleta; a abertura original levou 81,244 s no ensaio com prazo ampliado. Mesmo agrupando as leituras, o evento simples ainda excedia 30 s. O `onOpen` agora monta os controles e continua eventual troca de paleta; a revisão completa fica em `revisarAbertura`, chamada pelo novo acionador instalável `salarioAposAbrir`, com orçamento de seis minutos. O diário e a edição já instalados são preservados, sem duplicação. Cópias recebem os dados prontos; ao ativar a conferência diária, instalam também essa revisão de abertura.

As doze notas são lidas por duas faixas de uma coluna, mantendo a preservação de texto manual e a correção de ajuda duplicada. A revisão da paleta conserva a escolha e atualiza opções/aviso sem ler o valor calculado nem forçar recálculo. O checkbox não varre missões nem fecha períodos: atualiza emissão, ciclo e previsão pelo registro técnico. A fórmula compara dias inteiros, pois datas gravadas no Sheets carregam um horário e poderiam excluir missões do próprio dia da emissão. Créditos anteriores e O86 permanecem intactos.

`node salarios/corrigir_abertura.js <Codigo-atual.gs> <Codigo-corrigido.gs>` prepara a atualização do pacote antigo sem alterar os cinco arquivos comprimidos. Os bytes originais são validados pelo SHA-256 antes de substituir funções por âncoras únicas; âncora divergente ou correção duplicada interrompe o carregamento. As âncoras mínimas da base R53 estão em `abertura_r53_original.json`, sem depender do histórico Git disponível em um clone. A geração integral usa diretamente as fontes corrigidas.

Resultados e tempos da publicação estão em `VALIDACAO.json`. Evidências nativas e fontes relidas permanecem em `saidas/`, fora do Git.
