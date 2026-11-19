# Buff/Debuff colado como texto · 09/11/2026

Colar um inteiro com sinal como texto (`-2`, `+2`, `2`) num campo de
Buff/Debuff da entidade agora produz a mesma conta que o número.
Antes, as famílias `u`, `us` e `ut` passavam a entrada por `N()`, que
transforma texto em zero. A planilha preserva o tipo e o valor
digitado; o caminho numérico continua o mesmo.

Nas descartáveis Era e Ciclo, a colagem real pela interface deu o
mesmo resultado do controle numérico:

| cópia | nível | colado | DQ2/DZ2/EC2 | CON | PV | Vigor | pontos |
|---|---|---|---|---|---|---|---|
| Era | 10 | texto `-2` | −2 | −2 | 10 | −4 | 0 |
| Era | 10 | número −2 | −2 | −2 | 10 | −4 | 0 |
| Ciclo | 2 | texto `+2` | 2 | 2 | 14 | 4 | 0 |
| Ciclo | 2 | número 2 | 2 | 2 | 14 | 4 | 0 |

Conta da Era: `5 + (−2) + (3 + 0 − 2) × 9 − 2 = 10`. Ciclo:
`5 + 2 + (3 + 0 + 2) × 1 + 2 = 14`. Na Era, o próprio `-2` textual
em `O21` (Buff de Força) levou a resistência Física a −2.

## Delta

168 fórmulas de `DADOS_INVOC`, linhas 2 a 13 (12 entidades):

- `DO:DS` · `u0`–`u4`, Buff/Debuff de atributo;
- `DW:EA` · `us0`–`us4`, Buff/Debuff de status;
- `EB:EE` · `ut0`–`ut3`, Buff/Debuff de TR.

Cada uma troca `=N(ref)` por:

```
=IF(ISTEXT(ref),IF(REGEXMATCH(ref,"^[+-]?[0-9]+$"),
  VALUE(SUBSTITUTE(ref,"+","")),0),N(ref))
```

Só sinal ASCII, sem espaço em volta. Ficam valendo zero: vazio,
`" 2"`, `"2 "`, o sinal tipográfico `−2`, `--2`, `+-2`, `abc`, `+`
e decimais textuais (`1,5`, `1.5`). `DT:DV` (texto, `&""`) e os
pontos `DJ:DN` da PR92 não mudam.

A função nova é `ajuste_textual()` em `ficha-v01/ficha_invocacoes.py`.
Geração `6701a3e4b549d436` (antes `ec14f1ff36db9816`), comparada em
280.056 posições de 26 abas: só as 168 fórmulas divergem. Os `.gs`
foram regenerados; o pacote integral não foi gerado nem instalado.

## Validação

**No Sheets (pt_BR, duas QAs):**

- Snapshot fresco antes de aplicar: os 168 alvos eram `=N(ref)` nas duas.
- Instalação por `updateCells` em dois blocos por cópia (`DO2:DS13`,
  `DW2:EE13`), relidos byte a byte iguais ao delta.
- Colagem real: apóstrofo e valor em `INVOCAÇÕES!O21`, **Editar ›
  Copiar**, **Editar › Colar especial › Só os valores** em `Q21`
  (Constituição), `R26` (Vida máxima) e `P31` (Vigor). A releitura
  confirmou texto nos três destinos e os números da tabela acima.
- Controle numérico pelos mesmos três campos, resultado idêntico.
- Na Era, `1,5`, `abc` e `−2` tipográfico gravados como texto deram 0
  nas três colunas.

**Só local:**

- `r53/testes/buffs_entidades.js`: geração, aplicação e reversão em
  pt_BR e en_US, recusa de alvo divergente e tabela de semântica dos
  casos acima (incluindo `-0`, `+12`, espaços e decimais).
- Smoke `nuvem-b47/conferir.py --smoke` passou.

## Limitações

- Decimal textual fica fora até checar o comportamento regional:
  em pt_BR o separador é vírgula e `VALUE` depende do locale.
- O ensaio em Sheets foi só em pt_BR; en_US foi coberto localmente.
- A MONTAGENS não foi comparada célula a célula nesta rodada. A
  grade segue 9543 × 9 nas duas cópias e nenhuma escrita da rodada
  tocou essa aba (todas estão listadas acima e na reposição).
- Uma tentativa de `findReplace` por regex na Era devolveu erro interno
  do Sheets sem aplicar nada (revisão inalterada); troquei por
  `updateCells`.
- A cópia pelo menu deixou o texto da `O21` na área de transferência
  do sistema.

## Reposição

`O21`, `Q21`, `R26` e `P31` voltaram a número 0 com o
`userEnteredFormat` inteiro do baseline (formato `B/D`, bordas, cores,
fonte). A nota da `O21` ficou intacta. Os valores dependentes batem
com o snapshot fresco: Era CON 0, PV 32, Vigor 0; Ciclo CON 0, PV 8,
Vigor 0. A aba do navegador usada no teste foi fechada. As 168
fórmulas novas continuam instaladas nas duas QAs.

## Retomada

Ramo `codex/corrige-colagem-buffs-20261109`, empilhado sobre a PR92.
Plano versionado: `buffs_entidades_delta.json`. Evidência sanitizada:
`buffs_entidades_validacao_2026-11-09.json`. Privados em
`nuvem-b47/saidas/correcao-colagem-buffs-20261109/`.

O preparador `preparar_buffs_entidades.js` recebe os diretórios GS de
antes e depois e o destino do plano JSON. `pedidos(delta, snapshot)`
só gera a atualização se os 168 alvos baterem com a base; para
reverter, passe o snapshot posterior e `true` como terceiro argumento.
