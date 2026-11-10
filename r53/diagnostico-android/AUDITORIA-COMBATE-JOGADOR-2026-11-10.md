# Iniciativa, CD e ataques do jogador · 10/11/2026

Item 2 do `MAPA-COBERTURA-2026-11-10.md`. O item 1 (travas da criação) foi coberto pela PR98. Auditoria só de
leitura e ensaio. Nenhuma fórmula mudou.

**Fonte:** o livro Ciclo Maldito R66 (`JJK---Project`, `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`):
Maestria, Iniciativa, Bônus de ataque e "Atributo, ataque e CD". A `ESPECIFICACAO-ficha-digital.md` é da v0.240 e
bate com o livro nesses pontos.

## As fórmulas contra o livro

| caixa | livro R66 | ficha | bate? |
|---|---|---|---|
| Maestria (D67) | +1 até o 9, +2 no 10, +3 no 18, +4 no 26 (nível 1 também é +1) | `1 + quantos de 10, 18, 26 ≤ nível` (DADOS!X5:X7) | sim, nos 30 níveis |
| Iniciativa (AK59) | d20 + Destreza | d20 + L19 + Buff | sim |
| CD de feitiço (D63) | 8 + atributo da técnica + maestria | 8 + D67 + atributo de Z67 + Buff | sim |
| Conjuração (O63) | d20 + atributo da técnica + maestria | D67 + atributo de Z67 + Buff | sim |
| Corpo a corpo (Z63) | d20 + Força + maestria; Fineza permite Destreza | D67 + atributo de AK67 + Buff | sim, com o menu (ver abaixo) |
| À distância (AK63) | d20 + Destreza + maestria, inclui arremessos | D67 + atributo de AE70 + Buff | sim, com o menu |

Os quatro também aceitam o ajuste, o valor fixo e o erro da CONFIGURAÇÃO (DADOS_CONFIG linhas 7 a 11), como as
outras caixas.

## Ensaio na QA Era (nível 10, maestria 2)

A Kaori do caso de teste (Força 3, Constituição 2, Destreza 2, Inteligência 1, Essência 1, técnica em Força),
levada ao nível 10:

| caixa | esperado | ficha |
|---|---|---|
| Iniciativa | d20 + 2 | d20 + 2 |
| CD de feitiço | 8 + 3 + 2 = 13 | 13 |
| Conjuração | d20 + 5 | d20 + 5 |
| Corpo a corpo (FORÇA) | d20 + 5 | d20 + 5 |
| Corpo a corpo (DESTREZA, Fineza) | d20 + 4 | d20 + 4 |
| À distância (DESTREZA) | d20 + 4 | d20 + 4 |
| À distância (FORÇA, arremesso por habilidade) | d20 + 5 | d20 + 5 |

Ao final, os pontos voltaram a 0 e os menus voltaram a ESSÊNCIA, FORÇA e DESTREZA. A ficha mostra de novo
CD 10, d20 + 2 nos três ataques e Iniciativa d20 + 0, como antes.

A Defesa da QA Era mostra 0 porque a Marcante dela é Corpo Exaurido, que zera a Defesa de propósito. Não é deste
recorte.

## Achados

### 1. Menu de atributo vazio ou escrito errado vira #N/A (erro)

Os três menus (Z67 da técnica, AK67 do corpo a corpo, AE70 da distância) **não são estritos**. A fórmula usa
`IFS` sem caso padrão, então qualquer valor fora dos cinco nomes quebra a caixa.

| entrada em Z67 | CD e Conjuração |
|---|---|
| vazio (apagou com Delete) | #N/A |
| "FORCA" (sem cedilha, colado ou digitado) | #N/A |
| "força" (minúscula) | 13 / d20 + 5 (o Sheets compara sem caixa) |

O mesmo acontece com AK67 vazio no corpo a corpo. O #N/A também sai na ANALISE (`cd_de_feitico`, `conjuracao`,
`corpo_a_corpo`, `a_distancia`), que o bot lê. Uma ficha com o menu apagado chega ao bot com "#N/A" nesses campos.

Caminhos possíveis (decisão do Mizuki):

- **A.** A própria caixa mostra "Escolha o atributo" no lugar do #N/A, sem reescrever o menu. É o mesmo padrão das
  PR94 e PR98 e resiste à colagem.
- **B.** Os três menus passam a ser estritos. Isso barra a digitação, mas a colagem passa por cima (achado da PR92).
- **C.** A e B juntos.

### 2. Constituição no menu de ataque não tem fonte no livro (decisão)

Os dois menus de ataque oferecem os cinco atributos. O livro abre exceções para:

- Destreza no corpo a corpo, pela Fineza;
- Essência ou Inteligência, pelo Compasso e pelo talento da categoria de armas;
- Força no arremesso com arma de uma mão, por habilidade.

Nada no R66 deixa atacar com **Constituição**. Manter as cinco opções é mais simples. Tirar a Constituição segue
o livro à risca.

### 3. Um atributo por personagem, não por arma (limite de desenho)

Fineza, Compasso e o arremesso valem arma por arma. A ficha tem uma caixa de corpo a corpo e uma de distância, e
o jogador escolhe o atributo da arma que mais usa. Só fica anotado.

## Fora deste recorte

- A CD da Kata, que usa o atributo de ataque da arma, mora na FICHA AMALDIÇOADA.
- A Defesa já foi conferida na AUDITORIA-EQUIPAMENTO.
- As oficiais e a ficha do jogador não foram tocadas. A QA Ciclo não foi usada, porque a geração é a mesma e o
  recorte foi só de leitura.
