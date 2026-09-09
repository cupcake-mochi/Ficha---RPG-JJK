# A planilha viva — cópia de referência

**Isto não é o `ficha-v01/`.** Aquela pasta é um marco congelado da v0.1, com gerador e
harness de comparação próprios — não se mexe nela. Esta pasta é outra coisa: a cópia
mais recente da planilha que o Mizuki usa de verdade no Google Sheets, exportada por
ele e trazida pra cá pra servir de referência quando o gerador Python (`ficha/`)
precisar alcançar o que ela já tem.

Sem gerador, sem harness, sem comparação automática — é só o arquivo, atualizado à mão
toda vez que o Mizuki manda uma exportação nova.

## Estado

`Ficha-PROJETO-M-0.1.xlsx` — exportada por ele em **09/09/2026**, e ela é **fiel**:
nada foi corrigido por cima.

> **⚠ A versão anterior desta pasta NÃO era fiel, e isso foi consertado aqui.** *O
> arquivo `Ficha-PROJETO-M-0.1_4.xlsx` era a exportação de 08/09 **com dois consertos
> aplicados por mim por cima** — os 8 ofícios e o comentário do `Z37`.* **Uma cópia
> "corrigida" que não bate com a planilha real é uma terceira fonte de verdade**, e
> esta sessão inteira foi sobre o custo disso. *Agora o arquivo é o que a planilha é, e
> o que falta aplicar está escrito abaixo em vez de escondido dentro do `.xlsx`.*

### O que JÁ está aplicado na planilha viva

- **As seis notas**, rodadas por ele em 09/09 pelo `corrigir-notas-temp.gs`:
  `AF23` (vida temporária, agora com o teto de metade da vida máxima), `AF27`
  (energia temporária), `AF31` (integridade temporária — o `B17`), e `AM23`/`AM27`/
  `AM31` (as caixinhas de `±`, com a da Integridade avisando do acoplamento).
- **O acoplamento do dano de alma** no `Código.gs`: perder Integridade pela caixinha
  passa a tirar vida no mesmo tanto (`B20`). *Testado por ele na planilha real em
  09/09/2026 e conferido: funciona.*
- **As três barras "agora"** (`D23`, `D27`, `D31`) voltaram a ser `=J23`, `=J27` e
  `=J31` — o molde limpo, em vez do estado com personagem em campo que a exportação
  anterior tinha.

### O que AINDA NÃO está aplicado — e é o próximo clique dele

> **⚠⚠ Os 8 ofícios continuam em `INTELIGÊNCIA` na planilha real.**
>
> *Medido na exportação de 09/09: `K75`, `K76`, `K78`, `K79`, `X75`, `X76`, `X78` e
> `X79` estão todas em `INTELIGÊNCIA`.* **O `corrigir-oficios.gs` desta pasta nunca foi
> rodado.** *A correção existe no catálogo e no gerador Python desde a v0.221 — é só a
> planilha que está atrás.*
>
> **A fonte é a peça 7 §6 do `JJK---Project`:** `Condução`, `Arrombamento`,
> `Caligrafia`, `Entalhador` e `Alfaiate` → **Destreza**; `Forja` → **Força**;
> `Jogatina` e `Instrumento` → **Essência**. *As outras 3 (`Herbalismo`, `Burocracia`,
> `Culinária`) já estão certas por coincidência.*

*Detalhe sem importância:* `AM23`, `AM27` e `AM31` vieram com `0` em vez de vazio,
resto do teste do acoplamento. Não faz nada — o `aplicarDelta_` tem `if (!passo)
return;` logo no começo.

## Os scripts desta pasta

| arquivo | o que faz | rodado? |
|---|---|---|
| `corrigir-notas-temp.gs` | escreve as 6 notas de `AF23`/`AF27`/`AF31` e `AM23`/`AM27`/`AM31` | **sim**, 09/09/2026 |
| `corrigir-oficios.gs` | põe o atributo certo nas 8 células de ofício | **não** — é o que falta |
