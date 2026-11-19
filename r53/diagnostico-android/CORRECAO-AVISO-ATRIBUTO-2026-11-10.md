# Menu de atributo sem #N/A · 10/11/2026

Achado 1 da `AUDITORIA-COMBATE-JOGADOR-2026-11-10.md`. O Mizuki escolheu o caminho A: **aviso na caixa**.

## O que estava errado

Os menus de atributo da FICHA não são estritos: Z67 (técnica), AK67 (corpo a corpo) e AE70 (distância). As contas
usam `IFS` sem caso padrão. Com o menu vazio ou com um nome fora dos cinco, por exemplo "FORCA" sem cedilha, a CD,
a Conjuração e os ataques viravam **#N/A**. O erro também saía na ANALISE, e o bot recebia "#N/A".

## A regra agora

| menu | caixa |
|---|---|
| um dos cinco nomes, com qualquer caixa ("força" passa) | a conta normal |
| vazio, "FORCA", "Sabedoria", qualquer outro texto | **Escolha o atributo** |
| qualquer valor, com a caixa fixada pela CONFIGURAÇÃO ("trocar por") | o valor fixo, sem aviso |

O menu não é reescrito. O aviso fica até o jogador escolher.

## O que mudou no modelo

A geração era `66aa9dde4fdec0b1` e passou a `10101178be8ab3cb`. Em 280.056 posições, só mudaram **4 fórmulas**, todas na
linha 63 da FICHA: D63 (CD), O63 (Conjuração), Z63 (Corpo a corpo) e AK63 (À distância).

- **Gerador:** `ficha-v01/configuracao.py`, função `avisa_menu`. O aviso fica por fora do envoltório da
  CONFIGURAÇÃO, como a Defesa fixa do corpo real. O menu é lido do próprio `IFS` da conta, sem endereço escrito à
  mão. O `anterior` desfaz o aviso exato para os comparadores e recusa um aviso adulterado.
- **Camada:** `preparar_aviso_atributo.js`, com o delta em `aviso_atributo_delta.json`. A reversão é atômica.
- **Comparadores históricos:** a camada vem antes da do Buff decimal em `bencaos_imunidades`,
  `integridade_movimento`, `pilha_5156`, `origens_recursos`, `reserva_bolsa`, `buffs_entidades`, `buff_decimal` e
  `vida_bloquear_molde`. Este último continua fora do smoke, como antes.
- **Teste:** `r53/testes/aviso_atributo.js` está no smoke. Ele confere o plano, o modelo, a reversão, o `anterior`
  do Python, os pedidos em pt_BR e en_US e a tabela da regra.
- **Smoke completo:** 153 OK, saída 0.

## Instalação nas duas QAs

A instalação usou `findReplace` literal na célula inteira, uma célula por pedido. O texto procurado é o "antes"
exato, então cada resposta com 1 ocorrência prova que a célula batia antes da troca. Era e Ciclo deram 4 de 4.

## Ensaio (entradas repostas depois)

| QA | entrada | resultado |
|---|---|---|
| Era | menus intactos | CD 10, d20 + 2 nos três (igual a antes) |
| Era | Z67 vazio, AK67 "FORCA", AE70 "Sabedoria" | as quatro caixas: Escolha o atributo |
| Era | o mesmo, na ANALISE | `cd_de_feitico`, `conjuracao`, `corpo_a_corpo`, `a_distancia` = Escolha o atributo |
| Era | Z67 "força" | CD 10, d20 + 2 |
| Era | CD fixada em 15 pela CONFIGURAÇÃO, Z67 vazio | CD 15; Conjuração avisa |
| Ciclo | AK67 "CONSTITUICAO" | Corpo a corpo: Escolha o atributo; os outros normais |

No fim do ensaio, as duas QAs voltaram ao estado anterior:

- menus em ESSÊNCIA, FORÇA e DESTREZA;
- linha 11 da CONFIGURAÇÃO da Era desligada e vazia, sem erro no P2;
- Era com CD 10 e d20 + 2; Ciclo com CD 9 e d20 + 1.

## Bot

Não mudou. O conferidor dos derivados (`ficha_derivados_b47.py`) compara o valor com os cinco atributos possíveis.
"Escolha o atributo" não bate com nenhum, então o campo vira problema de conta, como já acontecia com "#N/A". A
diferença é que agora a mensagem diz o que fazer.

## Fora deste trabalho

- **Constituição nos menus de ataque** (achado 2 da auditoria): ficou como está. O Mizuki não pediu para tirar.
- Menu estrito (caminho B): não foi feito.
- As oficiais e a ficha do jogador não foram tocadas. O pacote integral não foi reinstalado, e `construir()` não
  rodou.
