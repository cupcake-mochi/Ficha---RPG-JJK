# Pontos de atributo forçados por colagem · 09/11/2026

Retoma as três sondagens do parecer da PR90 (negativo, fração e 7
pontos), que tinham sido gravadas só pela API e ficaram classificadas
como "limite de defesa da fórmula". A pergunta era se a interface comum
consegue chegar nesses valores. **Consegue.** Isto é só parecer e
evidência, sem mudança de fórmula.

## O caminho

A caixa de pontos (`INVOCAÇÕES!O20:S20`) tem menu estrito
(`ONE_OF_RANGE`, `DADOS_INVOC!CN2:CN8`, 0 a 6). Digitar fora do menu é
recusado, mas **Editar › Colar especial › Só os valores** grava qualquer
número por cima do menu. O valor de origem veio da caixa de Buff/Debuff
`O21`, que não tem menu. A colagem também trouxe o formato numérico da
origem (`B/D`) para a caixa de pontos.

| cópia | colado em Q20 (CON) | gravado | resumo | conta |
|---|---|---|---|---|
| Era, nível 10 | número 7 | 7, menu estrito mantido | ⚠ 7 DE 11 · ACIMA DE 3 SÓ COM MARCO | CON 7, PV 102 |
| Ciclo, nível 2 | número −1 | −1, menu estrito mantido | −1 DE 9 PONTOS, sem erro | CON −1, PV 6 |

## O que passa sem aviso

Com o estado de colagem confirmado, gravei os mesmos tipos de número
pela API na Era (nível 10, 2 Marcos, orçamento 11):

| pontos FOR/DES/CON/INT/ESS | resumo | efeito |
|---|---|---|
| 4 / 4 / 3 / 1 / −1 | ATRIBUTOS · 11 DE 11 PONTOS, limpo | o −1 paga um ponto a mais nos outros; PV 62 |
| 3,5 / 3,5 / 3 / 1 / 0 | ATRIBUTOS · 11 DE 11 PONTOS, limpo | atributos 3,5 entram na conta; a caixa mostra "4 pt" |

O motivo está em `ficha-v01/ficha_invocacoes.py`:

- `acima = Σ MAX(0, p − 3)`: negativo não conta, fração conta pela metade.
- `gastos = SUM(pontos)`: negativo devolve orçamento.
- Não há conferência de inteiro nem de faixa 0–6 fora do menu.

**O 7 fica sem aviso em nível alto.** Na Era (nível 10) ele acusou erro
porque estourou os Marcos. Pela fórmula, a partir do nível 18 (4 Marcos)
uma distribuição como 7/3/3/0/0 fecha `acima = 4 ≤ 4` e não avisa,
apesar do teto 6 a partir do nível 14. Esse caso foi deduzido da
fórmula, não ensaiado no Sheets.

Detalhe à parte: o texto `7` colado vale 0 (regex `^[0-6]$` da PR92),
mas o número 7 colado vale 7. O texto já tem a faixa; o número não.

## Classificação

Deixa de ser só uma sondagem da API: é uma **lacuna real de validação
alcançável pela colagem comum**. Negativo e fração fecham o orçamento
sem aviso nenhum. O 7 passa sem aviso a partir do nível 18. Não muda
número de regra; falta a ficha recusar ou acusar o que o menu já recusa.

Correção possível, para decidir: tratar como erro no resumo
(`d_pontos`) qualquer ponto que não seja inteiro de 0 a 6, mantendo a
entrada como está. Isso segue o padrão das PRs 92 e 93 (não reescreve o
que a pessoa digitou) e não mexe em menu nem em montagem.

## Reposição

Era: `O20:S20` em 0 com `0" pt"`, `O21` em 0 (PV 32, "0 DE 11").
Ciclo: `Q20` em 0 com `0" pt"`, `O21` em 0 (PV 8, "0 DE 9"). Só o formato
numérico da `Q20` tinha mudado; os demais campos de formato foram
comparados com a vizinha `P20` e estavam iguais. Navegador fechado. A
cópia pelo menu deixou `-1` na área de transferência do sistema.

Nenhuma escrita fora das duas QAs. Nenhuma fórmula alterada.
