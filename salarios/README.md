# Emissão e salários

Extensão incremental da R53, baseada no `main` d56623a. A fonte é `apps-script/Salarios.gs`; a ficha preenchida nunca passa por `construir()` ou `continuar()`, nem por importação Office.

## Uso

Em CONFIGURAÇÃO, abra **14 · Emissão e salários** pelo atalho no painel inicial. A seção fica em C320:Q355.

- G323: data de emissão fixa, editável. G324 grava o dia atual em Brasília e desmarca depois de salvar. Uma reemissão posterior ao último salário reinicia o próximo ciclo sem retirar créditos; uma data anterior não repete períodos pagos.
- G325: ativa o salário. Desligar pausa a apuração; religar apura períodos pendentes.
- G326: intervalo em dias corridos, padrão 30. G327: participações para salário completo, padrão 3. G328: parcela mínima, padrão 25%. G329: exige participação; desmarcar concede a referência integral.
- G339:G343: salário por Grau. P339:P344: pesos das missões. Os valores do livro são ¥150.000, ¥300.000, ¥600.000, ¥1.200.000 e ¥2.400.000; curta/padrão 1, longa 2, final de arco 3. Solos começam em 0 porque o livro não define seu peso salarial; a campanha pode alterá-lo.
- G333, G348:G351: vencimento, início, participações, previsão e último fechamento. G334 mostra os créditos acumulados; G335 mantém visível a referência integral do Grau atual.

O saldo manual continua em **FICHA PESSOAL!O86**, inclusive fórmulas como `=150000-500`. **W86 — TOTAL DISPONÍVEL** soma esse resultado aos créditos do histórico **SALÁRIOS**. Não copie os créditos para O86: isso somaria a mesma renda duas vezes. Para gastar, continue descontando do campo manual; ele pode ficar negativo enquanto o total disponível permanece positivo.

## Missões e fechamento

Os quatro blocos de missões (AW, BC, BI e BO, linhas 15–87) são monitorados. Ao completar nome e tipo, a missão recebe data e identidade persistentes na nota da célula, e um registro na aba técnica oculta DADOS_SALARIOS. Corrigir nome/tipo conserva a data. Para substituir por outra missão, limpe primeiro o nome antigo. Nomes iguais em linhas independentes são aceitos. Copiar/mover uma missão com sua nota conserva sua identidade, contando uma vez.

Missões anteriores à instalação não recebem uma data presumida. Para informá-la ou corrigir uma data, selecione a missão e use **Salários → Data da missão selecionada**. Não é possível alterar pagamentos fechados por essa operação. Uma missão sem nome ou tipo válido não participa; remover uma missão do painel retira sua participação de períodos ainda abertos.

O ciclo inclui sua data inicial e exclui o dia do próximo fechamento: emissão em 20/10, intervalo 30, primeiro pagamento em 19/11; missões de 19/11 pertencem ao próximo ciclo. O Grau vigente antes dessa fronteira é registrado no fechamento. Alterações de Grau observadas pelo módulo têm histórico próprio; no primeiro ciclo, usa-se como referência o Grau existente ao iniciar o acompanhamento. A planilha não reconstrói mudanças anteriores à instalação.

Pagamento: `floor(referência × [mínimo + (1 − mínimo) × min(participações, meta) / meta])`. Sem verificação de missões, paga-se a referência. Períodos fechados guardam Grau, referência, meta, pesos, parcela e valor; mudanças posteriores não reescrevem esses registros. As regras configuradas valem para os períodos ainda não fechados, inclusive pendentes.

Há apuração ao editar emissão/regras, preencher missões ou alterar Grau. O menu **Ativar conferência diária** instala dois acionadores: um diário entre 03h e 04h em America/Sao_Paulo e outro para registrar edições. A edição instalável tem orçamento de seis minutos e não disputa os trinta segundos dos cartões/XP. Os acionadores usam a conta que os instala e somente o documento vinculado. Acionadores instaláveis não acompanham uma cópia: ative o diário em cada ficha copiada; existe uma alternativa pelos eventos simples de abertura/edição, sujeita ao limite de trinta segundos do Google. Com o diário ativo, a abertura só mostra os controles, e o vencimento é processado pela rotina diária ou pelo menu Conferir salários agora. G325 permite pausar pagamentos sem apagar o histórico.

## Integridade e instalação

O histórico de pagamentos é a fonte do último fechamento. Um bloqueio do documento serializa chamadas concorrentes; a gravação é confirmada antes de liberar o bloqueio. Uma interrupção depois de gravar um crédito não permite repeti-lo na próxima execução. A proteção do histórico é um aviso contra edições acidentais, não um mecanismo de aprovação do mestre.

O instalador é idempotente e recusa uma área de configuração ocupada ou uma instalação parcial. Ele não modifica O86 nem os cartões da R53. Um arquivo vazio, ainda sem nome de personagem, não recebe pagamentos.

O empacotador R53 inclui Salarios.gs como módulo leve separado. Para atualização do pacote antigo sem regravar megabytes de catálogos, a publicação incremental anexa a mesma fonte ao Codigo.gs existente e adiciona duas chamadas aos eventos. Nunca instalar a fonte nas duas posições simultaneamente. A geração integral posterior substitui esse Codigo.gs e publica Salarios.gs separadamente.

Para preparar essa atualização, guarde uma leitura atual do Codigo.gs em `salarios/saidas/Codigo-antes.gs` e execute `node salarios/preparar_incremental.js`. O preparador confere o hash do pacote R53, recusa uma segunda anexação e valida a sintaxe do resultado. Ele não acessa o Google. Antes da instalação, faça backup nativo, snapshot dos alvos e ensaie em uma cópia nativa da oficial. `instalarSalarios()` aplica somente a extensão; `ativarSalarioDiario()` instala a rotina após essa aplicação.

A publicação de 20/10 precisou de retomada pela API: o serviço Planilhas interrompeu o instalador após criar as duas abas, ambas ainda vazias. `retomar_api.js` prepara os 132 pedidos a partir dos snapshots nativos privados dessa situação e da cópia ensaiada. O lote reutiliza as abas, preserva O86 e não transporta missões ou salários de QA. Foi ensaiado em uma segunda cópia antes da oficial. **Não reenviar esse lote em uma ficha já migrada.** O preparador recusa abas preenchidas, missões anteriores não tratadas e datas diferentes da rodada registrada.

O contrato ANALISE12 conserva suas chaves existentes; o campo de ienes anterior continua representando o ajuste manual de O86. O total e o histórico de salários estão nos campos novos descritos acima. Nenhuma aprovação do bot é concedida pelo módulo.

## Verificar

```powershell
node salarios/testes.js
python -X utf8 r53/empacotar_script.py
node r53/testes/pacote_runtime.js
```

`teste-nativo.gs` só pode ser executado na cópia QA cujo ID está fixado no próprio teste. Não o instale na oficial. Evidências e snapshots privados ficam em `salarios/saidas/`, ignorada pelo Git.

Fonte das regras: `manual.txt`, seção **Recompensas da guilda**, e `referencias-r53/LIVRO-COMPLETO.md`. Referência técnica: [acionadores instaláveis](https://developers.google.com/apps-script/guides/triggers/installable) e [Lock/flush](https://developers.google.com/apps-script/reference/lock/lock).
