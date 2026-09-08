# A planilha viva — cópia de referência

**Isto não é o `ficha-v01/`.** Aquela pasta é um marco congelado da v0.1, com gerador e
harness de comparação próprios — não se mexe nela. Esta pasta é outra coisa: a cópia
mais recente da planilha que o Mizuki usa de verdade no Google Sheets, exportada por
ele e trazida pra cá pra servir de referência quando o gerador Python (`ficha/`)
precisar alcançar o que ela já tem.

Sem gerador, sem harness, sem comparação automática — é só o arquivo, atualizado à mão
toda vez que o Mizuki manda uma exportação nova.

## Estado

`Ficha-PROJETO-M-0.1_4.xlsx` — a versão que ele mandou em 08/09/2026, com duas
correções aplicadas por cima do que ele enviou:

- **os 8 ofícios com atributo errado**, consertados. A planilha tinha as 11 células de
  atributo de ofício fixas em `INTELIGÊNCIA`, e só 3 (`Herbalismo`, `Burocracia`,
  `Culinária`) estavam certas por coincidência — as outras 8 usam a peça 7 §6 do
  `JJK---Project` como fonte (`Condução`, `Arrombamento`, `Caligrafia`, `Entalhador`,
  `Alfaiate` → Destreza; `Forja` → Força; `Jogatina`, `Instrumento` → Essência). O
  mesmo conserto foi entregue ao Mizuki como Apps Script, pra ele rodar na planilha
  real — ver `corrigir-oficios.gs` nesta pasta.
- **o comentário grudado em `Z37`** (Bloquear), que era cópia do comentário de `Z40`
  — o Mizuki já apagou isso na planilha dele, replicado aqui pra bater.

Nada além disso foi tocado: números, fórmulas e layout são exatamente o que ele mandou.
