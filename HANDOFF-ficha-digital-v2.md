# Ficha digital do Projeto M · onde o trabalho parou

Documento de passagem para uma conversa nova. Ele existe para você não ter que recontar nada: o que foi decidido, o que foi achado, e o que está esperando decisão sua.

Anexe junto: `ESPECIFICACAO-ficha-digital.md`, `catalogo-projeto-m.json`, e o manual em PDF.

---

## 1 · O que já está resolvido

**A plataforma está decidida, e por eliminação.** Os jogadores recusaram site e recusaram PDF. Sobrou planilha, e o destino é o Google Sheets, que é onde eles conseguem abrir.

**A especificação está escrita e conferida.** `ESPECIFICACAO-ficha-digital.md`, dez seções, com toda fórmula, todo catálogo e as travas de validação. Todo número dela foi conferido por script contra o manual.

**Os catálogos estão extraídos.** `catalogo-projeto-m.json` traz 23 perícias, 11 ofícios, 5 Caminhos, 15 Trilhas, 9 Famílias, 10 Formas, 66 Melhorias, 14 condições, 19 Restrições, 9 rotas de criação e 85 Legados. As contagens que o manual declara por extenso batem todas.

**O caso de teste passa.** Os onze números derivados da Kaori saem do catálogo e batem com a página 41 do manual e com a `ficha-exemplo-kaori.docx`.

---

## 2 · Quatro problemas achados no repositório

### O grave: a ficha imprime Famílias que não existem

| fonte | as nove |
|---|---|
| `manual/gerador/partB.js` | Alcance · Área · Mira · Controle · Auxiliares · Castigo · Tempo · Marca · Amparo |
| `gerador-ficha/dados.js` | Ataque · Área · Controle · Castigo · Amparo · Corpo · Movimento · Auxiliares · Percepção |

Só cinco coincidem. A ficha tem `Ataque`, `Corpo`, `Movimento` e `Percepção`, que não existem no manual e não têm uma Melhoria sequer. E não imprime `Alcance`, `Mira`, `Tempo` e `Marca`, que juntas são **27 das 66 Melhorias**.

Confirmado em três lugares: `dados.js`, tabela 15 da `ficha-em-branco.docx`, e o gerador do manual.

**Por que passou:** o `conferir-ficha.py` tem seis checagens e nenhuma confere Famílias. Toda outra cópia da ficha tem dono declarado; a lista de Famílias não tem.

**O conserto está pronto** em `checagem-7-familias.py`. Ela acende no estado atual do repositório e apaga numa cópia com o `dados.js` corrigido.

> A Kaori não expõe esse bug. As cinco Famílias que ela usa são exatamente as cinco que as duas listas têm em comum. Ela passa por coincidência.

### O de nome: `canalizado` não existe no manual

A ficha chama um dos dois golpes de `canalizado`. Essa palavra não aparece uma vez sequer no manual, que chama a mesma coisa de `feitiço de Toque`. O outro golpe, `golpe simples`, é igual nos dois.

### O de contagem: 8 ou 9 perícias

O handoff antigo dizia oito. O manual, na página 29, diz que o extra da Origem pode ser um ofício **ou uma nona perícia**. A ficha de papel já está certa: ela imprime "23, e você treina 8 (ou 9)". **Decidido: 8 ou 9, o jogador escolhe.** A ficha precisa de um campo que muda de natureza, não de oito linhas fixas.

### O da regra 2: o teto de dano

**Decidido: `Queima` conta como repetição para o teto de `4 × Classe`**, mesmo acontecendo no turno seguinte.

Com isso a busca exaustiva mostra que a regra morde de verdade:

| Classe | orçamento | teto | pior montagem legal |
|---|---|---|---|
| 1 | 3 | 4 | **6** |
| 3 | 9 | 12 | **18** |
| 5 | 15 | 20 | **30** |
| 7 | 21 | 28 | **42** |

Sempre `Salto` + `Queima` com o custo pago por duas Restrições Médias. O total vira `2 × orçamento`, ou seja `6 × Classe` contra teto de `4 × Classe`: **50% acima, em toda Classe**.

E essa montagem **passa nas outras sete regras de ouro**. Duas Melhorias dentro do limite, duas Restrições dentro do limite, nenhuma de frequência, devolução exatamente no teto, nada virando dado. É a única das oito que a montagem não denuncia sozinha, e por isso é a que mais paga o custo de automatizar.

---

## 3 · O protótipo, e por que ele falhou

Foi construído um protótipo em `.xlsx` para testar se planilha consegue não parecer planilha. **A resposta técnica é sim**, mas a primeira tentativa errou em três pontos, e os três estão medidos.

### Errou o tamanho, e por um fator de 1.8

| | |
|---|---|
| o que foi feito | 52 colunas × largura 2.35 = **~855 px** de ficha |
| o que cabia | 1300 a 1500 px de área útil no Sheets |
| a largura de coluna certa | **3.6 a 4.1**, não 2.35 |
| fonte usada | 6 a 8 pt |
| mínimo legível em tela | 9 a 10 pt no corpo |

**O erro conceitual:** a técnica do grid fino (coluna estreita, gridlines desligadas, layout por merge) foi copiada corretamente, mas ela é um **meio**, não um objetivo. O objetivo é ter resolução suficiente para desenhar. Grid fino sem aumentar a largura total só encolhe tudo.

### A fonte não é controlável

O arquivo declara `Oswald` e `Lexend`, mas **4362 das células estão em Calibri 11**, que é o default do openpyxl para toda célula pintada sem estilo explícito. E o Google Sheets substitui qualquer fonte que ele não tenha carregada.

Resultado: a tipografia aparece diferente no Excel e no Sheets, e nenhuma das duas é a escolhida. **A fonte padrão do documento precisa ser definida explicitamente**, e é mais seguro escolher uma que o Sheets já tenha.

### A paleta saiu da fonte errada

O protótipo partiu do ameixa `741B47`. Ele veio do código: `manual/gerador/helpers.js` e `gerador-ficha/helpers.js` declaram os dois `crimson: '741B47'`, e o comentário diz "a paleta é a mesma do manual".

**Mas a identidade do servidor e do PDF é outra:** `#211c35` (roxo-escuro) e `#756588` (roxo-claro).

Os dois roxos **não aparecem em nenhum arquivo do repositório.** Isso é a lição nº 9 de novo: a identidade visual mora em dois lugares e eles divergiram.

---

## 4 · O que medir antes de escolher a paleta

Contraste WCAG (4.5 é o mínimo para texto pequeno; 3.0 serve só para texto grande):

| par | contraste | veredito |
|---|---|---|
| roxo-escuro `211c35` vs branco | 16.38 | passa folgado |
| roxo-claro `756588` vs branco | 5.29 | passa |
| **roxo-claro sobre roxo-escuro** | **3.10** | **só texto grande** |
| **roxo-escuro vs ameixa `741B47`** | **1.55** | **reprova** |

Duas consequências:

**Os dois roxos não servem para texto pequeno um sobre o outro.** Rótulo de campo em `#756588` sobre fundo `#211c35` fica ilegível. Eles funcionam como fundo e bloco, não como fundo e texto.

**O ameixa do manual e o roxo do servidor brigam.** Com 1.55 de contraste, um sobre o outro vira mancha. Não dá para usar os dois como base e acento; ou escolhe um, ou entra uma terceira cor só para destaque.

---

## 5 · O que está esperando decisão sua

### A identidade visual, que hoje tem duas versões

O código do manual diz ameixa `741B47`. Você diz que o servidor e o PDF são `#211c35` e `#756588`. **Qual das duas é a identidade, e a outra é dívida?**

Se a resposta for o roxo, isso não é só a ficha: o gerador do manual também está fora da identidade, e vale um item de correção.

### A cor de destaque

Com base roxo-escuro e blocos roxo-claro, **falta uma terceira cor** para vida, energia e alerta de validação. As opções e o que cada uma traz:

- **vermelho sangue**, que lê como JJK e como dano
- **roxo saturado tipo Hollow Purple**, que lê como energia amaldiçoada mas briga com a base roxa
- **osso ou branco-sujo**, sóbrio, e o destaque vem do tamanho em vez da cor

### A largura, que é um trade-off real

Uma ficha desenhada para 1500 px enche a tela num monitor grande e **não cabe num notebook de 1366**, nem em celular. Uma desenhada para 1300 px cabe em quase tudo e sobra espaço no monitor grande.

**Onde os seus jogadores abrem a ficha?** A resposta muda o número.

### A densidade

O protótipo mostrou tudo de uma vez, sem rolagem, e foi isso que espremeu o texto. As duas saídas:

- **blocos maiores, e o jogador rola**, que é o que quase toda ficha digital faz
- **mais abas, cada uma menos densa**, que é o que a ficha de papel já faz com três páginas

---

## 6 · Os arquivos

| arquivo | o que é |
|---|---|
| `ESPECIFICACAO-ficha-digital.md` | a especificação completa, dez seções |
| `catalogo-projeto-m.json` | todos os catálogos em forma de dados |
| `conferir-catalogo.py` | integridade referencial e as contagens declaradas |
| `conferir-kaori.py` | regressão contra a ficha de exemplo |
| `conferir_feitico.py` | as oito regras de ouro aplicadas a um feitiço |
| `regressao-exemplos.py` | os feitiços publicados na página 137 |
| `arnes.py` | prova que cada checagem acende |
| `teto-fechado.py` | a busca exaustiva do teto de dano |
| `checagem-7-familias.py` | o conserto do bug das Famílias |
| `revisao-cetica.py` | confere a especificação contra o manual |
| `divergencia-familias.py` | mede a divergência das Famílias |
| `ficha/` | o protótipo em xlsx e o gerador dele |

**Nenhum arquivo do repositório foi editado.** Todo trabalho ficou em diretório próprio.

---

## 7 · Como continuar

1. **Decida a paleta e a largura** antes de escrever qualquer código. As duas mudam o layout inteiro, e refazer é caro.
2. **Refaça o protótipo com a largura certa**: coluna 3.6 a 4.1, corpo 9 a 10 pt, fonte padrão do documento definida.
3. **Só depois** entre na validação de feitiço, que é a parte cara e a que mais vale.
4. **Conserte as Famílias no repositório**, com a checagem 7. Isso é independente da ficha digital e vale por si.

### O que não mudar

- Onde a ficha e o manual discordarem, **o manual vence**.
- Onde a regra não existe, **não invente**: Trilhas do Evocador, nível 27 do `Arremate`, Pactos, Técnica Marcial, Estilo da Sombra e `Casco` estão em aberto.
- **Escolha de sabor é do Mizuki.** Traga opções com o trade-off calculado, em rodadas curtas.
- **Nunca edite nem comite nos repositórios.**
