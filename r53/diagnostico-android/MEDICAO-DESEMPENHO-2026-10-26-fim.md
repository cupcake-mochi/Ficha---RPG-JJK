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

## Cortes da noite na cópia (`1kAXc_Wb…`, "TESTE cortes K7-MONTAGENS-Classe", projeto `1gICM0DK…`)

Cópia nova da Era da Revolução (Codigo `452445ac`, EditorR53 `68f21a08`, módulo `52fc6903`, os mesmos da oficial). Edições
pelo navegador, uma por vez; duração do onEdit no registro de Execuções, todas concluídas, nenhum erro. Entre as duas
rodadas, o trecho de `preparar_cortes_noite.js` (sha256 `2f5249c7…`) devolveu módulo `9dc3480a`, Codigo `dc1aa740` e
EditorR53 `c3d31096`; salvo e relido igual.

| Edição | Antes | Depois |
|---|---:|---:|
| a. CONFIGURAÇÃO AS51 = texto curto (primeira depois de abrir) | 20,5 s | 24,2 s |
| b. AS51 apagar | 14,8 s | 15,6 s |
| c. AS51 = texto | 19,7 s | 15,9 s |
| d. AS51 apagar | 21,5 s | 14,3 s |
| e. FICHA AMALDIÇOADA E71 = 1 (primeira no cartão) | 19,3 s | 18,8 s |
| f. E71 = 0 | 16,8 s | 13,7 s |
| g. E71 = 1 | 17,8 s | 13,4 s |
| h. E71 = 0 | 19,3 s | 14,9 s |
| i. FICHA AN11 (XP) = 50 | 25,9 s | 14,5 s |

A primeira edição depois de abrir paga a leitura e guarda (a abertura apaga as versões guardadas; as marcas só se
apagam pelas células delas, mas a cópia nova não tinha nenhuma). Da segunda em diante: habilidade custom 19,7–21,5 →
14,3–15,9 s, cartão 16,8–19,3 → 13,4–14,9 s, XP 25,9 → 14,5 s. Na XP, as duas rodadas devolveram a conta
(`=DADOS!$CZ$47`); antes, o nível AH11 foi de 10 para 2 (o número digitado); depois ficou em 2 (já era o da conta,
então essa rodada não prova sozinha que o nível fica parado; o node prova, `marcas_custom.js`).

## Caixas de ± sem abrir o módulo (cópia `1aNuAcj2…`, "TESTE caixas delta (descartável)", projeto `1kIcshvU…`) · 26/10, 23:40–23:49

Cópia nova da Era da Revolução pelo `/copy` (sem abrir a oficial). Os dez arquivos do script batiam com os das oficiais
(Codigo `dc1aa740`, EditorR53 `c3d31096`, Analise `2ea7e9d4`…). O trecho do `preparar_caixas_delta.js` rodou com o bloco
baixado do commit `36d08ad` (hash `be124889` conferido na página) e devolveu Codigo `07a66b0a`; salvo, recarregado, só o
Codigo mudou. Edições pelo navegador, uma a cada ~20 s, duração do onEdit no registro de Execuções, todas concluídas.

| FICHA!AM26 (± da vida) | aquecimento | −3/+3 alternados | mediana |
|---|---:|---|---:|
| antes (Codigo `dc1aa740`) | 13,2 s | 11,5 / 11,2 / 15,4 / 11,6 s | 11,5 s |
| depois (Codigo `07a66b0a`) | 11,2 s | 13,1 / 11,2 / 10,4 / 10,7 s | 10,9 s |

Média 12,4 → 11,4 s: o ~1 s esperado aparece, mas dentro da oscilação do Google (±2–4 s por edição). Depois, as outras
caixas: integridade 65/65 −1 → 64 (12,3 s), +5 → 65, preso no máximo (14,4 s); energia 0 sem máximo +2 → 2 (11,4 s).
Todas as caixas limparam. Vida 53 → 50 → … → 47, coerente com os ± digitados.
