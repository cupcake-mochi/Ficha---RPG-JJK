# Buff/Debuff decimal contra o dono · 10/11/2026

Pendência aberta na PR93 ("Buff/Debuff decimal e leitura diferente entre fichas"). O Mizuki escolheu
**arredondar contra o dono**, como manda a especificação ("sempre para o lado que não te favorece"), e deu o
ok depois de ouvir o risco ("okey, tome cuidado então, pode seguir").

## O que estava errado

- **Duas leituras.** A ficha do jogador lia o Buff/Debuff com `IFERROR(VALUE(x&""),0)`: texto decimal valia
  conforme a região da planilha, e "1/2" virava data (um número de cinco dígitos). As invocações aceitavam só
  inteiro com sinal. A mesma colagem contava numa ficha e zerava na outra.
- **Decimal escondido.** A caixa B/D tem o formato `"B/D "+0`. Um 1,5 entrava na conta como 1,5 e aparecia
  como "B/D 2".

## A regra agora (as duas fichas, a mesma fórmula)

| entrada | vale | por quê |
|---|---|---|
| 2, "+2", "2" | 2 | inteiro passa igual |
| 1,5 (número ou texto "1,5"/"1.5") | 1 | ganho desce |
| 0,5 | 1 | ganho nunca fica abaixo de 1 |
| −1,5 | −2 | custo sobe |
| −0,5 | −1 | custo sobe |
| "1/2", "abc", " 2", data, vazio | 0 | texto só vale quando é número simples |

O texto vale quando bate com `^[+-]?[0-9]+([.,][0-9]+)?$`. Vírgula e ponto são aceitos e a conta não depende da
região. A leitura está em `ficha-v01/leitura_buff.py` e é usada por `ficha_automatica.py`, `custom.py`,
`defesa_equipamento.py`, `campanha.py`, `ficha_amaldicoada.py` e `ficha_invocacoes.py`.

**Risco que o Mizuki aceitou:** quem já tem um Buff decimal digitado vê o número mudar na hora da instalação.
Por exemplo, um +1,5 que somava 1,5 passa a somar 1.

## O que mudou no modelo

Geração `c8c2dae1ce50fa1b`. Comparando a geração anterior com a nova, mudaram **206 fórmulas**, todas pela troca
do leitor (`preparar_buff_decimal.js` recusa qualquer outra diferença):

| aba | fórmulas | onde |
|---|---|---|
| FICHA | 11 | J26, J30, J34, D59, O59, AK59, D63, O63, Z63, AK63, O67 |
| DADOS_AM | 5 | coluna KV, linhas 4, 5, 11, 13, 15 |
| DADOS_INVOC | 168 | DO:DS e DW:EE das 12 entidades (14 por linha) |
| DADOS_CONFIG | 22 | F2:G12 |

Os 11 Buff/Debuff do jogador são L59 Defesa, W59 Proteção, AS59 Iniciativa, L63 CD, W63 Conjuração,
AS63 À distância, AH63 Corpo a corpo, P26 Vida, P30 Energia, P34 Integridade e W67 Deslocamento.

- `buff_decimal_delta.json`: os 206 pares antes/depois.
- `preparar_buff_decimal.reverterModelo` é a camada que os comparadores históricos descascam antes da
  Reserva/Bolsa. É atômica: confere tudo numa cópia antes de gravar.
- `r53/testes/buff_decimal.js` está no smoke. Ele confere:
  - o gerador Python e o JS escrevem o mesmo leitor;
  - o modelo bate com o depois;
  - a reversão parcial é recusada;
  - os pedidos saem certos em pt_BR e en_US, e a vírgula do regex sobrevive;
  - a tabela da regra.
- Testes que ganharam a camada nova: `bencaos_imunidades`, `integridade_movimento`, `pilha_5156`,
  `origens_recursos`, `reserva_bolsa`, `buffs_entidades` e `vida_bloquear_molde`.
  - `vida_bloquear_molde.js` **já falhava antes** desta mudança: não descasca a camada das bênçãos. Ele não está
    no smoke e segue assim.

## Instalação nas duas QAs (só as fórmulas, sem `construir()`)

A instalação foi feita por localizar e substituir nativo do Sheets, célula por célula. Cada resposta informa
quantas trocas fez, e foi essa contagem que conferi.

- **Entidades:** troca por regex nas faixas DO2:DS13 e DW2:EE13. Era e Ciclo: 60 + 108 = **168** cada.
- **Jogador:** 43 pedidos, total esperado de **87** ocorrências. Era e Ciclo: 87, na mesma sequência pedido a
  pedido.
- Achado da instalação: o Sheets guarda `'FICHA'!$X$1` como `FICHA!$X$1`, sem aspas. A primeira leva com aspas
  achou 0 e foi refeita sem elas.

## Ensaio (entradas repostas depois)

| QA | entrada | resultado |
|---|---|---|
| Era | entidade 1,5 / "0,5" / −1,5 / "−0,5" / "1/2" | 1 / 1 / −2 / −1 / 0 |
| Era | entidade 0,5 / "1.5" / "+2" / −2 / "abc" | 1 / 1 / 2 / −2 / 0 |
| Era | Deslocamento "1,5" / 2,5 / "1/2" (base 9 m) | 10 m / 11 m / 9 m |
| Era | Defesa −0,5 (base 11) | 10 |
| Ciclo | entidade 1,5 / "0,5" / −1,5 / "−0,5" / "1/2" | 1 / 1 / −2 / −1 / 0 |
| Ciclo | Deslocamento "1,5" (base 9 m) | 10 m |

Ao final, INVOCAÇÕES O21:S21 mostra "B/D 0", FICHA W67 e L59 estão em 0, DADOS_CONFIG F5 = 11, F12 = 9 m e
DADOS_INVOC DO2:DS2 = 0 nas duas.

**Achado do ensaio:** gravar texto pela API apagou a máscara "B/D" de algumas caixas (P21, R21, S21). A máscara
foi devolvida só no formato de número, com o mesmo padrão das vizinhas. Não sei se a digitação manual faz o mesmo;
não testei.

**O formato da caixa B/D ficou como estava.** Nenhum formato do Sheets mostra bem decimal e inteiro ao mesmo
tempo: `General` põe um "-" solto no negativo e `0.##` deixa uma vírgula sobrando no inteiro. Como a conta agora
usa o valor arredondado, o "B/D 2" de um 1,5 digitado mostra o arredondamento visual da célula, não o que a
conta soma (1). A entrada continua sendo do jogador.

## Fora deste trabalho

- As oficiais e a ficha do jogador não foram tocadas.
- O pacote integral não foi reinstalado.
- `construir()` e `continuar()` não rodaram.
