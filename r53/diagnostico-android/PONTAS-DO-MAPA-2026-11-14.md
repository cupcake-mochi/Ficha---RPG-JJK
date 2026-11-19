# As pontas do mapa de cobertura · 14/11/2026

O Mizuki pediu para resolver as pontas que o `MAPA-COBERTURA-2026-11-10.md` deixava abertas antes da rodada das
oficiais ("consegue resolver essas pontas?", e depois do plano, "Pode seguir"). Uma por uma:

| ponta | resultado |
|---|---|
| Caixa B/D mostra "B/D 2" para 1,5 | consertada: `CORRECAO-AVISO-DECIMAL-BD-2026-11-14.md` (#114) |
| Regressão da Kaori sem LibreOffice | ensaio pela API no Ciclo: os seis números batem (abaixo) |
| `cartas_custom.js`, `marcas_custom.js` | históricos: só rodam com a exportação de 25/10, no Linux |
| Cura do Exaurido no Android | o menu não existe no app do Android; no celular vale a caixa ± (abaixo) |
| Rajada na caixa ± | a varredura que eu propus não é segura; espera decisão do Mizuki (abaixo) |
| Ordem de Refino dos Talentos | fica como limite: a ficha não sabe a ordem |

## Kaori pela API (QA do Ciclo)

A `regressao-kaori-na-ficha.py` preenche a Kaori numa cópia do `.xlsx` e manda o LibreOffice recalcular. No Windows não
há LibreOffice. O núcleo dela foi repetido na QA do Ciclo, que tem as mesmas fórmulas da ficha instalada.

Entradas, pela API (sem onEdit): `FICHA!D11` Bastião, nível 2 (`AH11`, já estava), FOR 3, DES 2, CON 2, INT 1, ESS 1
(`D21`, `L21`, `T21`, `AB21`, `AJ21`), atributo da técnica FORÇA (`Z67`), Origem no padrão "Escolha sua Origem" (`X11`),
como na ficha gerada.

| número | célula | esperado (livro) | lido |
|---|---|---|---|
| vida máxima | J26 | 23 | 23 |
| energia máxima | J30 | 8 | 18 = 8 + 10 do Buff/Debuff de energia (`P30` = 10 no Ciclo) |
| Integridade máxima | J34 | 26 | 26 |
| Defesa | D59 | 13 | 13 |
| maestria | D67 | 1 | 1 |
| CD de feitiço | D63 | 12 | 12 |

Os seis batem. Ficaram de fora deste ensaio as outras partes da regressão: os TR treinados, a Defesa com equipamento,
os casos da ficha automática e o Buff/Debuff dos máximos. Elas continuam no script, que roda no Linux com o LibreOffice.

**Achado:** o Ciclo tem `FICHA!P30` (Buff/Debuff de energia) = 10, sobra de teste como o `P26` que o Mizuki mandou
zerar em 14/11. Não foi mexido: espera a decisão dele.

**Reposição:** D11 "Escolha seu Caminho", X11 "Restrição Celestial · Restrição corporal", os cinco atributos 0, Z67
ESSÊNCIA. Relido depois: Defesa 0, CD 9, maestria 1, vida máxima 0, energia máxima 10.

## `cartas_custom.js` e `marcas_custom.js`

Os dois comparam o módulo montado até o 35º remendo com o montado até o 37º, a partir da exportação da cópia de teste
de 25/10 (`nuvem-b47/saidas/atalho/oficial-era.json` e `projeto-leve.json`, fora do git). Os remendos 36 e 37 já estão
instalados há semanas, e a exportação está no SSD do Linux. No Windows os dois saem com "sem a ficha exportada,
pulado". Ficam como testes históricos: rodam no Linux, se precisar. Nada foi apagado.

## Cura do Exaurido no Android

A cura do Exaurido tem duas entradas:

- **Recursos → Aplicar cura**, que divide por dois. É um menu de script com caixa de confirmação, e o app do Google
  Sheets no Android não mostra menus de script nem essas caixas. No celular ela não existe, e não há o que testar.
- **A caixa ± (`FICHA!AM26`)**, que aplica o número como foi digitado (o contrato do `CURA-EXAURIDO-2026-11-04.md`).
  O onEdit roda no Android: a medição de 26/10 (commit `e5647c2`) teve 16 edições concluídas na oficial pelo celular.

No celular, o Corpo Exaurido digita na caixa ± a metade da cura, já arredondada para baixo. Uma nota na caixa ± dizendo
isso seria uma mudança de texto na FICHA; fica como sugestão para o Mizuki.

## Rajada na caixa ±

O `r53DeltaExecutar_` (`apps-script/Codigo.gs`) aplica **o valor do evento**, não o que está na caixa. É de propósito:
−5 e −3 seguidos na mesma caixa contam os dois, e a caixa só é limpa se ainda tiver o valor daquele evento.

A proposta era: numa edição de ±, varrer as outras caixas ± da aba e aplicar o número que tivesse ficado parado. Não é
segura. Um evento atrasado (ainda na fila, com a trava esperando até 12 s) é indistinguível de um evento perdido. A
varredura aplicaria o número, e depois o evento atrasado aplicaria de novo: dano ou cura em dobro. E um evento perdido
no meio da rajada nem deixa rastro, porque o seguinte sobrescreve a caixa.

O que dá para fazer sem esse risco é só visual. A caixa ± com número fica com cor de "pendente", e a nota diz: "se o
número continuar aqui depois de alguns segundos, ele não foi aplicado: digite de novo". O número fica parado na caixa
justamente quando o evento se perdeu. Espera a decisão do Mizuki.

## Ordem de Refino dos Talentos

"Aptidões a mais no teto" supõe a ordem de Refino mais favorável, porque a ficha não sabe em que ordem o jogador
escolheu. Saber pediria uma coluna nova para o jogador registrar a ordem: mais trabalho na mesa por um ganho pequeno.
Fica como limite conhecido.
