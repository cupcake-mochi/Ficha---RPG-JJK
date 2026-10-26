# Medições do fim de 26/10/2026 (Claude)

## ± da vida: onde vão os ~10 s (cópia `1QPKjsv6…`, "TESTE vida", projeto `1w1KcHfH…`)

Teste do Mizuki na oficial Era da Revolução (16:08–16:10, depois do SalarioLote novo): 10 edições, todas concluídas,
execução 9,9–23,8 s, edição 8,4–22,2 s (nenhuma passou pela conferência do salário, todas acima de 8 s; quatro delas
começaram no mesmo segundo). Ele sentiu "ainda meio lento os cálculos de perda e ganho".

Na cópia, com marcas dentro do módulo (uma depois de cada rotina do caminho da FICHA) e o perfil por rotina
(`medir_perfil.gs` no fim do SalarioLote), FICHA!AM26 = −3 / +3 / −3: execução 14,2 / 10,0 / 12,1 s. Perfil da
de 10,0 s (onEdit 8,6 s):

| Trecho | Tempo |
|---|---:|
| subir o script, antes do onEdit | ~1,4 s |
| primeira chamada à planilha e as conferências do salário, antes do módulo | ~1,1 s |
| abrir o módulo (`r53Modulo_`) | 1,3 s |
| `aplicarDelta_`: a leitura de ±, atual, máximo e temporária (primeira leitura da FICHA) | 3,0 s |
| as outras 13 rotinas da FICHA (conta, caixa que estica, descanso, temp, perícias, trilha, habilidades, XP, armas, ficha pessoal) | 0,03 s |
| `flush` do fim (a vida gravada recalcula a ficha) | 2,9 s |

Experimento: sem o `SpreadsheetApp.flush()` explícito do `r53SalarioOnEdit_`, três ± deram 11,0 / 11,8 / 12,3 s:
o fim da execução faz a mesma espera. Descartado.

Conclusão: o ± já está quase no piso (subir, primeira chamada, uma leitura, gravar). O que sobra de cortável é abrir
o módulo (~1,3 s), com um caminho global só para as caixas de ± (as células viriam de um mapa gerado, como o do
atalho das células livres). A primeira leitura e a gravação não somem.
