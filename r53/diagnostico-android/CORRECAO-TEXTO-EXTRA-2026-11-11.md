# Texto no Extra e em Trein/Espec · 11/11/2026

O pente fino de 11/11 achou este defeito (`CORRECAO-OFICIOS-TR-2026-11-11.md`). Um "dois" escrito no Extra, ou um "x"
colado na caixa de Treino ou de Especialização, dava **#VALUE!** no total da perícia. Os ofícios e os TRs faziam o
mesmo. O Mizuki escolheu o **aviso na caixa**, e não ler o texto como 0.

## A regra agora

| entrada | caixa do total |
|---|---|
| Extra vazio ou com número | a conta normal |
| Extra com texto ("dois", "abc") | **Extra só aceita número** |
| texto em Trein ou Espec ("x" colado) | **Apague o texto em Trein/Espec** |
| "2" colado como texto no Extra | a conta normal (o Sheets soma, como antes) |
| valor fixado pela CONFIGURAÇÃO | o valor fixo, sem aviso |

Os avisos ficam por fora dos outros. A ordem é esta:

1. texto no Extra;
2. texto em Trein/Espec;
3. especialização sem treino;
4. atributo do menu;
5. a conta.

O ISERROR repete a operação da própria conta (`Extra+0` e `IF(caixa;…)`). Assim, só avisa quando a conta quebraria. O
treino dos TRs já usa `=TRUE` e não quebra com texto, por isso os TRs só ganham o aviso do Extra.

## O que mudou no modelo

Em 280.056 posições, mudaram **38 células**, todas na FICHA:

| grupo | células | avisos |
|---|---|---|
| perícias | P80:P90 e AF79:AF90 (23) | Extra e Trein/Espec |
| ofícios | N108:N113 e AA108:AA112 (11) | Extra e Trein/Espec |
| TRs | AP108:AP111 (4) | Extra |

- **Gerador:** `ficha-v01/configuracao.py`, função `avisa_texto`.
  - Ela acha o Extra na própria conta: é a única referência relativa que não é menu, treino nem especialização.
    Nenhum endereço é escrito à mão.
  - O `anterior` recusa um aviso adulterado: outro Extra, outra caixa ou outra linha da DADOS_CONFIG.
- **Camada:** `preparar_texto_extra.js`, com o delta em `texto_extra_delta.json`. A reversão é atômica.
- **Comparadores históricos:** a camada vem dentro da da especialização em `especializacao`, `menu_oficios`,
  `bencaos_imunidades`, `buff_decimal`, `buffs_entidades`, `integridade_movimento`, `origens_recursos`, `pilha_5156`,
  `reserva_bolsa` e `vida_bloquear_molde`.
- **Teste:** `r53/testes/texto_extra.js`, no smoke. **Smoke completo: 158 OK, saída 0.**

## Instalação nas duas QAs

A instalação usou `findReplace` literal na célula inteira, uma célula por pedido. Era e Ciclo deram **38 de 38**.

**AP109 (TR de Vigor):** o modelo escreve `'FICHA'!$T$19`, e o Sheets guarda `FICHA!$T$19`, sem aspas. A busca
literal só achou a célula com o texto no formato do Sheets. Isso vale para qualquer instalação futura dessa célula.

## Ensaio (entradas repostas depois)

| QA | entrada | resultado |
|---|---|---|
| Era | R80 = 2 (número) | P80 = 2, conta normal |
| Era | R81 "dois" | P81: Extra só aceita número |
| Era | D82 "x" | P82: Apague o texto em Trein/Espec |
| Era | O108 "abc" | N108: Extra só aceita número |
| Era | R108 "x" | AA108: Apague o texto em Trein/Espec |
| Era | AJ110 "três" | AP110: Extra só aceita número |
| Era | contadores durante o ensaio | AK89 "9 de 9", AF114 "2 de 2", AK105 normal, sem erro |
| Ciclo | R81 "dois", AJ109 "um" | P81 e AP109: Extra só aceita número |

## Fora deste conserto

- **Oficiais.** Nada foi aplicado. Isso fica para o Mizuki, junto com a mescla da pilha na main.
