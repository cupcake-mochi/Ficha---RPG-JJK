# Especialização: sem treino e sem marco de Corpo · 11/11/2026

Duas falhas da mesma regra do livro R66. A primeira saiu do pente fino de 11/11 (`CORRECAO-OFICIOS-TR-2026-11-11.md`).
O Mizuki escolheu o caminho A: **aviso na caixa**. A segunda foi achado dele no mesmo dia.

## O que o livro diz

- **Especialização:** "Se você tiver especialização numa perícia ou ofício treinado, acrescente metade da maestria".
  Ela só vale com o treino.
- **Corpo:** cada marco de Corpo dá "treino em uma perícia ou ofício". A partir do nível 10, pode especializar um já
  treinado em vez do novo treino. Ou seja, cada especialização gasta uma escolha de Corpo.

## O que estava errado

1. **Especialização sem treino somava.** Nas 23 perícias e nos 11 ofícios, marcar só a especialização dava maestria e
   meia sem gastar vaga de treino. Na QA Era, E109 marcado com D109 desmarcado deu 3 (maestria 2 + 1).
2. **"1 a mais" sem dizer o motivo.** No nível 10, com especialização marcada e nenhum Corpo no marco, os contadores
   de perícias e ofícios diziam só "1 a mais". O resumo dizia "tire uma perícia, um ofício ou uma especialização",
   sem falar do Corpo.

## A regra agora

| situação | caixa |
|---|---|
| especialização marcada, treino desmarcado | **Marque o treino** |
| as duas marcadas | a conta normal (maestria e meia) |
| texto colado na especialização ("x") | não conta como marcada, nem avisa |
| valor fixado pela CONFIGURAÇÃO | o valor fixo, sem aviso |
| ofício com o menu de atributo errado e especialização sem treino | Marque o treino (aparece primeiro) |

Os contadores checam nesta ordem:

| ordem | condição | contador (AK89 e AF114) | resumo (AK105) |
|---|---|---|---|
| 1 | especialização abaixo do nível 10 | Especialização só no nível 10 | (igual a antes) |
| 2 | **mais especializações que Corpo no marco** | **Especialização sem marco de Corpo** | **Marcou N especialização(ões) sem marco de Corpo: escolha Corpo no Marco Escolhido ou tire a marcação** |
| 3 | treinos a mais | N a mais | (igual a antes) |

## O que mudou no modelo

Em 280.056 posições, mudaram **37 células**, todas na FICHA:

- 34 contas: P80:P90, AF79:AF90, N108:N113 e AA108:AA112;
- 3 contadores: AK89, AF114 e AK105.

**Geradores:**

- `ficha-v01/configuracao.py`, função `avisa_treino`. Ela lê as duas caixas no próprio `IF` da conta, sem endereço
  escrito à mão. O aviso fica por fora do aviso de atributo. O `anterior` recusa um aviso adulterado: outra caixa,
  ou outra linha da DADOS_CONFIG.
- `ficha-v01/ficha_automatica.py`: os dois contadores e o resumo.

**Camada:** `preparar_especializacao.js`, com o delta em `especializacao_delta.json`. A reversão é atômica.

**Comparadores históricos:** a camada vem dentro da dos ofícios. Isso vale para `menu_oficios`, `bencaos_imunidades`,
`buff_decimal`, `buffs_entidades`, `integridade_movimento`, `origens_recursos`, `pilha_5156`, `reserva_bolsa` e
`vida_bloquear_molde`.

**Teste:** `r53/testes/especializacao.js`, no smoke. **Smoke completo: 157 OK, saída 0.**

## Instalação nas duas QAs

A instalação usou `findReplace` literal na célula inteira, uma célula por pedido. Era e Ciclo deram **37 de 37**.

## Ensaio (entradas repostas depois)

| QA | entrada | resultado |
|---|---|---|
| Era (nível 10, Corpo 0) | E80 e E108 marcados, sem treino | P80 e N108: Marque o treino. AK89 e AF114: Especialização sem marco de Corpo. AK105: Marcou 2 especializações sem marco de Corpo: escolha Corpo no Marco Escolhido ou tire a marcação |
| Era | D80 e D108 marcados, Corpo 2 | P80 = 3 e N108 = 3; contadores "8 de 9" e "1 de 2"; resumo "Falta: 8 perícias e 1 ofício" |
| Ciclo (nível 2) | E81 marcado, sem treino | P81: Marque o treino. Contadores: Especialização só no nível 10 (o aviso do nível vem primeiro) |

## Fora deste conserto

- **Texto em caixa numérica.** Resolvido no mesmo dia, com aviso na caixa (decisão do Mizuki): ver
  `CORRECAO-TEXTO-EXTRA-2026-11-11.md`.
- **Oficiais.** Nada foi aplicado. Isso fica para o Mizuki, junto com a mescla da pilha na main.
