# Corte do XP da missão abaixo de 25 · 12/11/2026

Achado 2 da `AUDITORIA-PROGRESSAO-XP-2026-11-12.md`: o menu de desconto parava no 7º da semana, e o livro dá no
mínimo 1 XP a toda missão positiva. O Mizuki aprovou uma regra da casa, fora do livro ("pode por").

## A regra

- Se o XP final da missão, depois do tipo, do adicional, da falha e do desconto da semana, arredondado para baixo,
  ficar **abaixo de 25**, a missão dá **0**. Exatamente 25 paga.
- **Cada missão se olha sozinha.** A soma da semana não entra na conta.
- **Vale para o passado.** As missões já anotadas passam a seguir a regra, porque a fórmula se recalcula. A exceção são
  as congeladas pelo XP digitado: na próxima edição do painel, o `salarioXpCongelado_` joga a diferença para a base, e
  o total não mexe. Até essa edição, o total mostra a missão congelada já com o corte.
- O número mora no catálogo: `fora_do_livro.xp_minimo_da_missao` = 25, com nota.

**Consequência.** Da 7ª missão da semana em diante, nada chega a 25. A maior missão possível é um Final de arco 2x
(600 XP), e na 7ª ela daria 18. Por isso o menu de desconto ficou com 10 linhas:

| linha | fração |
|---|---|
| 3ª · 50%, 4ª · 25%, 5ª · 12,5%, 6ª · 6,25% | as do livro |
| **7ª ou mais** | 0 |
| Falha · metade | 0,5 |
| 3ª · 50% · falha … 6ª · 6,25% · falha | metade da posição |

As versões com falha continuam com os nomes antigos, então as fichas que já usam esses nomes não quebram. As 10 linhas
cabem na `DADOS!CR5:CS15` de hoje. A CR15:CS15 fica vazia, e as fórmulas e o menu continuam apontando para a mesma
faixa.

**Ficha com a 7ª antiga escolhida.** Numa ficha com "7ª · 3,125%" ou "7ª · 3,125% · falha" já escolhido, a missão fica
com o TOTAL vazio (o `IFERROR` da fórmula) e o menu marca a caixa como inválida. Ela daria 0 de qualquer jeito. Basta
escolher "7ª ou mais".

## Conferência (fórmula no Sheets)

| missão | conta | antes | agora |
|---|---|---|---|
| Curta na 4ª | 50 × 25% = 12,5 | 12 | **0** |
| Padrão na 4ª | 100 × 25% = 25 | 25 | **25** |
| Final de arco 2x, 7ª ou mais | 600 × 0 | 18 (na 7ª) | **0** |
| Final de arco 2x na 6ª | 600 × 6,25% = 37,5 | 37 | 37 |
| Longa na 3ª com falha (exemplo do livro) | 200 × ½ × ½ | 50 | 50 |

## Onde mudou

| arquivo | o quê |
|---|---|
| `catalogo-projeto-m.json` | `fora_do_livro.xp_minimo_da_missao` e a nota. O `conferir-catalogo.py` passa. |
| `ficha-v01/ficha_pessoal.py` | `descontos()` corta o menu na primeira posição em que nem a maior missão chega ao corte ("Nª ou mais", fração 0). A fórmula do TOTAL vira `IF(FLOOR(v,1)>=25,FLOOR(v,1),0)`. A faixa guarda a 11ª linha vazia. As notas DESCONTO e TOTAL trocam o mínimo de 1 pela regra da casa. |
| `apps-script/*.gs` | geração `7201a34fd878a19c` → `c86ee6159f0e8463` (`monta.py` e `r53/caminho_leve.js`) |
| `salarios/missoes_moldes.json` e `apps-script/Salarios.gs` | as 292 fórmulas do `SALARIO_MISSOES_MOLDES_`, pela mesma troca |
| `r53/diagnostico-android/preparar_corte_xp_missao.js` | a troca de texto dos moldes, o trecho para o console das QAs e a camada do modelo (`explicar`, `comparar`, `reverterModelo`), com o delta em `corte_xp_missao_delta.json` |
| `r53/testes/corte_xp_missao.js` (novo, no smoke) | as três casas da fórmula iguais, a regra calculada pela própria fórmula contra as tabelas da DADOS, a camada atômica, o menu do Python e o trecho num editor de mentira |
| comparadores históricos | a camada entra por dentro da do texto no Extra em `bencaos_imunidades`, `buff_decimal`, `buffs_entidades`, `especializacao`, `integridade_movimento`, `menu_oficios`, `origens_recursos`, `pilha_5156`, `reserva_bolsa` e `vida_bloquear_molde` |
| `r53/testes/missoes_sem_registros.js` | a cadeia que parte do Salarios.gs de 57117fb ganhou o corte no fim |

**Por que o corte não virou passo da cadeia nos outros testes.** Os moldes nascem no primeiro passo
(`preparar_missoes.js` lê o json). Então o `salario_lote.js` e o `missoes_enxutas.js` já recebem os moldes novos do
json, e a cadeia reproduz o Salarios.gs sem passo novo. Só o `missoes_sem_registros.js` parte de um Salarios.gs antigo
do git, e nele a troca entra no fim.

**O que mudou no modelo.** Em 280.056 posições, 304 alterações: 292 fórmulas na FICHA PESSOAL (BA, BG, BM e BS, linhas
15 a 87), 4 caixas na DADOS (CR9:CS9 e CR15:CS15) e 8 notas nos cabeçalhos (AZ14, BA14, BF14, BG14, BL14, BM14, BR14 e
BS14). Fora disso, nada.

**Smoke completo:** 161 OK, saída 0. O `vida_bloquear_molde.js`, fora do smoke, também passa.

## Instalação nas duas QAs

As duas QAs partiram do modelo antigo, igual ao `antes` do delta, o que foi conferido na leitura. A troca foi feita
pela API, num pedido só por planilha:
- `findReplace` com regex nas fórmulas da FICHA PESSOAL!BA15:BS87. Ele só casa a fórmula antiga inteira e a reescreve
  com o corte;
- `updateCells` na CR9:CS9 e na CR15:CS15;
- as 8 notas.

| QA | fórmulas trocadas | conferência |
|---|---|---|
| Era (`1LBZOf9v…`) | **292 de 292** | BA15, BG50 e BS87 com o corte; CR9 "7ª ou mais", CS9 0, CR15:CS15 vazias |
| Ciclo (`1HQqGOVG…`) | **292 de 292** | idem |

**Codigo instalado (`SALARIO_MISSOES_MOLDES_`): PENDENTE.** O Claude in Chrome não estava conectado. Sem essa troca,
quem apagar uma fórmula do TOTAL recebe de volta o molde antigo. O trecho está pronto:

```bash
node r53/diagnostico-android/preparar_corte_xp_missao.js > trecho.js
```

Cole no console do editor do Apps Script, com o projeto aberto. Ele acha o arquivo com o `SALARIO_MISSOES_MOLDES_`,
recusa se não achar exatamente 292 moldes antigos e guarda o antes em `window.__corteXpAntes`. Depois é só clicar no
editor e salvar com Ctrl+S. O `--reverter` desfaz.

## Ensaio na Era (entradas repostas)

O ensaio foi pela API. A conta do TOTAL é só fórmula, e o onEdit não entra nela.

| linha 15 | TOTAL |
|---|---|
| Curta, 4ª · 25% (AX/AZ) | **0** |
| Padrão, 4ª · 25% (BD/BF) | **25** |
| Final de arco 2x, 7ª ou mais (BJ/BK/BL) | **0** |

O XP total foi de 3700 a 3725. Depois as 12 caixas de entrada foram limpas (valor e nota), sem tocar nas fórmulas.
Ficou assim:
- XP 3700 e `DADOS!CZ54` 3700;
- `FICHA!AH11` 10;
- `DADOS_SALARIOS` só com a linha 2 antiga e inativa.

## Fora deste conserto

- **Oficiais:** nada foi aplicado. Falta, nas oficiais:
  - as 292 fórmulas;
  - a CR9:CS9 e a CR15:CS15;
  - as 8 notas;
  - o `SALARIO_MISSOES_MOLDES_` do Codigo.

  O mesmo regex e o mesmo trecho servem.
