# XP congelado preso à mesma missão pelo nome · 12/11/2026

**Substituído no mesmo dia pela linha congelada** (`CORRECAO-XP-LINHA-CONGELADA-2026-11-12.md`), a pedido do Mizuki.

Pedido do Mizuki. O caso foi confirmado na QA da Era (3900 → 4100).

## O problema

1. Alguém digita o XP total na `FICHA!AN11`.
2. As missões que já estavam no painel ficam congeladas: a nota de cada uma ganha `[XP congelado: x · id]`. O total
   digitado já inclui o XP delas.
3. A pessoa apaga o nome de uma dessas missões e digita de novo.
4. O salário dá outro id para a missão redigitada, diferente do id dono da marca. O `salarioXpCongelado_` vê o id novo,
   descongela, e a missão conta outra vez.

**Só congela quem estava no painel na hora do XP digitado.** As missões que entram depois são normais: o XP delas vem
da fórmula, apagar tira o XP e redigitar põe de volta.

## As duas saídas pesadas com o Mizuki

| | linha congelada | nome no registro (escolhida) |
|---|---|---|
| redigitar o mesmo nome | não soma | não soma |
| redigitar com erro de digitação | não soma | soma de novo |
| missão nova numa linha que foi congelada | dá 0 sem aviso | conta inteira |

O Mizuki escolheu o nome no registro, a saída que não pede nada complexo. O erro de digitação fica mais raro porque a
comparação ignora maiúscula, espaço e acento.

## A regra agora

- **Quando decide:** só quando a caixa forma missão (nome e tipo), no caminho do `salarioSincronizar_` que lê a
  `DADOS_SALARIOS`. A função recebe o mapa dos registros (`map`).
- **Mesma missão:** com um id diferente do dono da marca, a caixa olha o registro do dono. Se for a mesma caixa
  (`col:linha`) com o mesmo nome, é a mesma missão. Ela segue congelada, o total não mexe e a marca passa para o id
  novo. O `salarioMesmoNome_` compara sem diferença de maiúscula, espaço, acento e do apóstrofo que protege nome com
  `=`, `+`, `-` ou `@`.
- **Missão nova:** com outro nome, a missão é nova e conta inteira, como antes.
- **Caixa vazia:** guarda a marca com 0. Antes a marca saía, e apagar nome e tipo e redigitar os dois contava de novo.
- **Edição que não forma missão:** nome sem tipo, tipo sem nome ou o caminho que não lê os registros. A marca só
  acompanha o valor e espera.

**Limite.** Uma missão de verdade nova, na mesma caixa e com exatamente o mesmo nome da antiga (outra "Patrulha"),
fica congelada e não conta. Basta dar um nome diferente.

## Onde mudou

| arquivo | o quê |
|---|---|
| `apps-script/Salarios.gs` | o novo `salarioMesmoNome_`; o `salarioXpCongelado_(ss,atuais,map)` com a regra acima; a chamada do caminho que lê os registros passa o `map` |
| `r53/diagnostico-android/preparar_xp_congelado_nome.js` e `xp_congelado_nome_salario.json` | o preparador (três pares, depois do `preparar_trava_nivel_missao.js`) e o trecho para o console do editor das QAs |
| `r53/testes/xp_congelado_nome.js` (novo, no smoke) | o preparador e o trecho: ida e volta, recusa de repetir e de código divergente, e um editor de mentira |
| `r53/testes/xp_atualizar.js` | os casos novos (abaixo); a caixa vazia agora espera a marca com 0; "nome novo conta inteira" passou a "nome diferente" |
| `missoes_enxutas.js`, `missoes_sem_registros.js`, `salario_lote.js` | a cadeia ganhou o preparador novo no fim |

**Casos novos no `xp_atualizar.js`:**
- **Redigitar com variação:** congelada, nome apagado, "  missao   b " no lugar de "Missão B". O total não mexe, a marca
  passa para o id novo com 200, e trocar o tipo depois continua sem mexer.
- **Nome e tipo apagados:** a caixa fica com `[XP congelado: 0 · id]`.
  - Redigitando nome e depois tipo, o total não mexe.
  - Redigitando tipo e depois nome, também não.
- **Outro nome na caixa liberada:** "Missão D" depois de "Missão B". O nome sem tipo espera; com o tipo, conta inteira
  (+50) e a marca sai.

**Smoke completo:** 162 OK, saída 0.

## QAs: instalado depois (12/11)

No Ciclo, por outra sessão (`6ecbe5931682`). Na Era, junto com a linha congelada, que substituiu esta regra. O ensaio
desta regra na Era ficou sem repor e foi reposto na sessão da linha congelada. O texto abaixo é de quando estava
pendente.

O ensaio no Sheets e a instalação no Codigo das duas QAs não foram feitos. O Claude in Chrome estava desconectado, e o
navegador do app não tinha a conta Google. Falta, quando o Chrome voltar:

1. **Instalar nas duas QAs:** gere o trecho com o comando abaixo, cole no console do editor, clique no editor e salve
   com Ctrl+S. Ele recusa se o Codigo instalado não tiver os três pedaços antigos.

   ```bash
   node r53/diagnostico-android/preparar_xp_congelado_nome.js > trecho.js
   ```

2. **Ensaiar na Era** (nível 10, XP 3700):
   - duas missões no painel;
   - XP digitado na AN11;
   - apagar e redigitar o nome de uma delas: o total não mexe;
   - apagar nome e tipo e redigitar os dois: o total não mexe;
   - um nome diferente: conta inteira.
3. **Repor:**
   - painel e notas com `updateCells` em `userEnteredValue,note`;
   - as linhas novas do `DADOS_SALARIOS` limpas;
   - `DADOS!CZ54` = 3700 e `FICHA!AH11` = 10.

## Fora deste conserto

- **Oficiais:** nada foi aplicado. O mesmo trecho serve.
- **O rascunho da linha congelada:** continua sem commit no clone `ficha-integracao-5156-20261104`, no ramo
  `codex/xp-congelado-mesma-missao-20261112`. Há uma cópia nas notas da sessão. Pode ser descartado.
