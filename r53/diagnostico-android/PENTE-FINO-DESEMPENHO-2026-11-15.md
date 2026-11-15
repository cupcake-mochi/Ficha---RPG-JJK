# Pente fino de desempenho do onEdit — 15/11/2026

Pergunta do Mizuki: "atualmente não tá tendo estouros? passe um pente fino, tem usuário de telefone".

Nada foi mexido nas oficiais. Os testes rodaram em três cópias descartáveis, todas na conta do navegador:

| Cópia | Planilha | Scripts |
|---|---|---|
| B | oficial limpa | antigos |
| A | oficial com colunas do atraso | novos |
| D | atraso inteiro + R67 | novos |

## Estouros hoje

- Nenhum estouro registrado nas oficiais.
- Medição a frio, com 25–28 min parada antes da edição, uma amostra por cópia:

| Cópia | Tempo |
|---|---|
| B | 8,3 s |
| A | 11,7 s |
| D | 13,7 s |

- Medição antiga no Android (25 e 26/10): 8,9–23,1 s. O limite do acionador simples é 30 s.
- A margem existe, mas é curta no celular.

## Onde o tempo vai (logs `PRE` + `R53_ONEDIT`, cópia D)

Uma edição de Buff/Debuff (FICHA!L59) se divide em três partes:

| Parte | Tempo | O que é |
|---|---|---|
| Partida do Apps Script | ≈ 2–2,5 s | Igual com scripts antigos e novos. O `onSelectionChange`, que é vazio, também leva ≈ 2 s. |
| Primeira pergunta à planilha | 1–4,4 s | `e.range.getSheet().getName()` espera o recálculo que a própria edição disparou. |
| Corpo | 2,6–4,3 s | `r53OnEditOriginal_`, flush e salário. |

**Correção do que eu tinha dito antes:** a cadeia de 7 restauradores antes do `r53SalarioOnEdit_` **não** é o custo. Testei um filtro que pergunta o nome da aba uma vez só e pula os restauradores que não são daquela aba. O tempo só mudou de lugar: quem paga é a primeira chamada à planilha, seja ela qual for.

## Lixo encontrado e efeito medido (D, morna, 3 edições cada)

| Item | Total (s) | Espera do recálculo (s) | Veredito |
|---|---|---|---|
| Antes (JSON.parse, sem filtro) | 10,9 / 7,8 / 9,2 | — | — |
| Filtro por aba no onEdit | 11,2 / 9,2 / 6,6 | 4,4 / 2,8 / 1,4 | sem ganho; o custo só mudou de lugar |
| 525 INDIRECT → CHOOSE+MATCH | 8,2 / 5,6 / 9,5 | 2,0 / 1,0 / 2,6 | ganho pequeno (≈ 1 s na média), dentro do ruído |
| Literais da migração → JSON.parse | — | — | ganho incerto (medido antes) |

- **INDIRECT voláteis (DADOS_CUSTOM)**
  - São 225 fórmulas, todas no molde `INDIRECT(SWITCH(seletor;"Origem";"faixa";…;"Ferramenta amaldiçoada";"faixa";padrão))`: a linha 2 (DF:JZ, as listas dos menus da CONFIGURAÇÃO) e JY/JZ das linhas 3–26 (as conferências).
  - Todas têm as mesmas 8 chaves, na mesma ordem.
  - `SWITCH` com referência direta **não serve**: no Sheets ele não devolve faixa, e a lista some.
  - A forma que funciona é `CHOOSE(IFERROR(MATCH(seletor;{"Origem";…};0);9);faixa1;…;faixa8;padrão)`.
  - Conferido na D linha a linha (BYROW + TEXTJOIN) em dois estados do seletor, "Arma" e "Origem", com linhas de teste: 0 linhas diferentes nos dois.
- **TODAY em DADOS_SALARIOS!Q3:** é um só. Não vale mexer.
- **Literais de migração no Codigo:** ≈ 600 KB, e o `r53Modulo_` remonta o módulo em toda execução (patches de texto, `new Function` e cerca de 15 `r53Ajustar*`). Isso fica no corpo e ainda não foi medido isoladamente.

## A montagem do módulo (`r53Modulo_`), medida

Toda execução começa com `R53_MODULO_` vazio, então toda edição remonta o módulo. Pus um cronômetro em cada etapa, na D, em 6 edições de L59 com a cópia morna:

| Etapa | Tempo |
|---|---|
| base64 + ungzip + texto | 0,9–1,9 s |
| SHA-256 do código | 0,08–0,23 s |
| remendos de texto (`split`/`replace` no código inteiro) | 0,4–1,0 s |
| `new Function(code)` | 0,22–0,65 s |
| ~15 `r53Ajustar*` | 0,07–0,33 s |
| **total do módulo** | **1,7–4,1 s** |

- O módulo é 60–85% do corpo do onEdit, que vai de 2,1 a 4,8 s.
- O código descompactado tem **8.730.984 caracteres**, e o onEdit precisa de uma fração disso.

Corte possível, do mais simples ao mais trabalhoso:

1. **Aplicar os remendos na hora de empacotar**, não em toda edição. Ganha ≈ 0,4–1,0 s. O texto final do módulo fica igual; muda só o hash conferido.
2. **Tirar o SHA-256 da execução**, conferindo na instalação. Ganha ≈ 0,1–0,2 s.
3. **Separar o que o onEdit usa do resto** (construir, dados das abas). Diminui a descompactação e o `new Function`. Pode ganhar ≈ 1–2 s, mas mexe na arquitetura e precisa de estudo.

Depois do módulo, quem mais pesa é a espera do recálculo (1–3 s). Ela depende do que a célula editada alimenta na planilha, não do código.

## Como a troca foi feita na D (para levar ao gerador)

Fiz duas buscas-e-trocas com regex em DADOS_CUSTOM!DF2:JZ26, incluindo fórmulas.

1. `"('[A-Z_]+'!\$[A-Z]+\$[0-9]+:\$[A-Z]+\$[0-9]+)"` vira `$1`, e depois `INDIRECT\((SWITCH\([^()]*\))\)` vira `$1`. Essa forma intermediária ainda está errada.
2. `SWITCH\(([^;()"]+);"Origem";([^;()"]+!\$[^;()"]+);"Marcante";…;"Ferramenta amaldiçoada";([^;()"]+);([^;()"]+)\)` vira `CHOOSE(IFERROR(MATCH($1;{"Origem";"Marcante";"Menor";"Arma";"Escudo";"Uniforme";"Item comum";"Ferramenta amaldiçoada"};0);9);$2;…;$10)`.

O certo é mudar no gerador das fórmulas da DADOS_CUSTOM, não na planilha à mão.
