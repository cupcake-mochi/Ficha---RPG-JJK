# Ficha digital do Projeto M · documento de desenho

Isto **não** é a especificação de conteúdo (essa é a `ESPECIFICACAO-ficha-digital.md`, e ela diz *o que* a ficha tem). Este documento diz *como ela se parece e como ela se comporta*: paleta, tipografia, estrutura de abas, e o que a automação faz.

Tudo aqui foi medido ou tem fonte. Onde eu não tinha certeza, está escrito.

---

## 1 · O que já está fechado

| decisão | quem decidiu |
|---|---|
| A plataforma é **Google Sheets** | por eliminação: jogadores recusaram site e PDF |
| A automação é por **Apps Script**, rodado uma vez no modelo | Mizuki |
| A paleta parte de **`#211C35`** e **`#756588`** | Mizuki, são as cores do servidor |
| Vida e PE têm **total calculado** e **atual editável**, mais **temporário** | Mizuki |
| Perícias treinadas são **8 ou 9**, o jogador escolhe | Mizuki, conforme p.29 do manual |
| `Queima` **conta** como repetição no teto de dano | Mizuki |
| Precisa **abrir no celular** sem ficar ruim | Mizuki |

---

## 2 · A paleta

Derivada das suas duas cores. Nenhum valor foi escolhido no olho: o contraste decide o que pode receber texto.

| papel | hex | de onde veio |
|---|---|---|
| fundo | `#120F1D` | o seu roxo, escurecido 45% |
| painel | `#211C35` | **a sua cor** |
| painel alto | `#30294D` | o seu roxo, clareado 45% |
| linha e borda | `#493F54` | o seu roxo-claro, escurecido |
| bloco | `#756588` | **a sua cor** |
| texto fraco | `#998BA9` | o seu roxo-claro, clareado 30% |
| texto | `#F4F1F7` | branco com um toque do roxo |

### Contraste medido (WCAG: 4.5 para texto pequeno, 3.0 para texto grande)

| par | contraste | pode |
|---|---|---|
| texto sobre fundo | 16.88 | tudo |
| texto sobre painel | 14.64 | tudo |
| texto fraco sobre painel | 5.16 | tudo |
| **`#756588` sobre painel** | **3.10** | **só texto grande** |
| linha sobre painel | 1.66 | só bloco, nunca texto |

> **O achado que muda o desenho:** a sua segunda cor, `#756588`, **não serve para rótulo de campo**. Ela fica em 3.10 e o mínimo é 4.5.
>
> A saída não é trocar de cor, é trocar de papel: `#756588` vira **bloco e preenchimento**, e a versão 30% mais clara (`#998BA9`) vira **texto**. Continua sendo a sua cor, e passa a ser legível.

---

## 3 · A regra de cor, e por que ela não é opinião

Você pediu conceito de game design em vez de gosto. Três coisas decidem, e a terceira é a que quase ninguém testa.

### 3.1 · A proporção 60-30-10

Convenção de interface adaptada da decoração: **60% da tela na cor dominante, 30% na secundária, 10% no acento.** O acento só funciona porque é raro. Se ele aparece em toda caixa, ele deixa de ser acento e vira ruído.

Aplicado aqui: fundo `#120F1D` domina, painel `#211C35` e bloco `#756588` fazem os 30%, e o acento fica reservado para **vida, energia e alerta**. Nada mais.

### 3.2 · Cor não pode carregar informação sozinha

A WCAG é direta: *"cor não é usada como o único meio visual de transmitir informação, indicar uma ação, pedir uma resposta ou distinguir um elemento visual."*

Traduzido para a ficha: se o campo de perícia estourada fica vermelho, ele também precisa de um texto, um ícone ou uma borda. Vermelho sozinho não conta.

### 3.3 · O teste que derrubou a proposta original

Simulei a paleta em protanopia e deuteranopia, que juntas atingem cerca de 8% dos homens. O resultado:

| par | visão normal | protanopia | deuteranopia | veredito |
|---|---|---|---|---|
| carmim vs roxo energia | 1.09 | 1.00 | 1.23 | **vira a mesma cor** |
| carmim vs bloco roxo-claro | 1.41 | 1.25 | 1.68 | **vira a mesma cor** |
| âmbar vs carmim | 1.55 | 1.71 | 1.38 | **vira a mesma cor** |
| **osso vs roxo-claro** | 3.93 | 4.01 | 3.92 | distingue |

**Sobre base roxa, quase nenhum acento colorido sobrevive.** O roxo já mistura vermelho e azul, e a deficiência vermelho-verde achata tudo para o mesmo ponto. Um jogador com deuteranopia veria a barra de vida e a de energia na **mesma cor**.

### 3.4 · A regra que sai disso

> **A cor decora e reforça. Ela nunca é o que distingue.**
>
> O que separa vida de energia é **posição, rótulo e tamanho do número**. A cor entra por cima, para quem enxerga ela.

> **Decidido (A5): a cor entra como estado, não como decoração.** Osso quando cheio, âmbar abaixo da metade, vermelho abaixo de um quarto. Os três degraus e a medida de daltonismo estão no `DECISOES-bloco-A.md`.

Na prática:

- **Vida** e **Energia** ficam em blocos de tamanhos e posições fixas, com rótulo escrito. Se a cor sumir, a ficha continua legível.
- O acento colorido vai no **número grande**, onde 3.0 de contraste basta.
- **Osso `#E8DCD4`** é a única cor que passa em tudo e sobrevive ao daltonismo. Ela é a cor de trabalho.
- **Alerta de regra estourada** usa **fundo** colorido com texto branco, nunca texto colorido. Assim o contraste é do branco, e passa sempre. E vem com texto junto, por causa da 3.2.

---

## 4 · Tipografia e escala

O protótipo errou aqui por um fator de 1.8, e o erro está medido.

| elemento | protótipo | o certo |
|---|---|---|
| rótulo de campo | 5–6 pt | **9–10 pt** |
| valor de campo | 8–9 pt | **11–12 pt** |
| número de destaque | 15–22 pt | **28–36 pt** |
| título de seção | 7 pt | **11–12 pt** |
| largura de coluna | 2.35 | **3.6 a 4.1** |

### A fonte é um risco que precisa ser tratado

O arquivo declarava `Oswald` e `Lexend`, mas **4362 células saíram em Calibri 11**, que é o default do openpyxl para toda célula pintada sem estilo explícito. E o Sheets substitui qualquer fonte que ele não tenha carregada.

Duas correções, e as duas são obrigatórias:

1. **Definir a fonte padrão do documento** no `.xlsx`, não só nas células com texto.
2. **O script aplica a fonte em tudo** depois da importação, o que é o único jeito de garantir no Sheets.

### Estrutura: quadrado, não linha

O que dá personalidade não é só tamanho, é **forma e camada**:

```
o certo                        o que o protótipo fez
┌─────────┐
│   FOR   │  rótulo            ┌────────────┬─────┐
│   +3    │  grande            │   FORÇA    │  3  │
│  ( 3 )  │  base, menor       └────────────┴─────┘
└─────────┘
quadrado, 3 camadas            linha, 2 camadas
```

Com coluna de 4.0 (28 px), quatro colunas dão 112 px de largura; sete linhas de 15 px dão 105 px de altura. Vira quadrado.

**O que a plataforma não faz:** hexágono, canto arredondado, borda decorativa. Imagem flutuante fica *por cima* da célula e bloqueia a digitação, então serve de ornamento em área morta, nunca de moldura de campo editável.

**O que substitui:** caracteres de canto (`◣ ◢ ◤ ◥`) para simular chanfro, borda parcial em L, e kanji como marca. Chanfro lê bem no gênero.

---

## 5 · A estrutura de abas, e por que o celular exige uma a mais

### A conta que decide

```
celular retrato     350 px úteis   →  12 colunas de 4.0
notebook 1366      1300 px úteis   →  46 colunas
```

**No celular cabem 26% da ficha de PC.** Não existe grade que sirva aos dois: a grade é fixa, a tela não.

### A saída não é encolher, é separar por função

No celular ninguém preenche ficha. No celular se **consulta**, e se mexe em três ou quatro coisas. Ninguém escolhe Caminho no telefone; a pessoa olha quanto de PE sobrou.

| aba | largura | para quê | quem usa |
|---|---|---|---|
| `FICHA` | 46 col | criação e progressão | PC, uma vez por personagem |
| `TÉCNICA` | 46 col | Fundamento, Famílias, montagem de feitiço | PC, quando sobe de Classe |
| `QUEM É` | 46 col | a ficção | PC, uma vez |
| **`MESA`** | **12 col** | **o que muda durante a sessão** | **celular, toda rodada** |

**A `MESA` lê tudo por fórmula da `FICHA`.** Nenhum número duplicado, que é a lição nº 9 do próprio projeto.

### O que entra na MESA

Vida atual e máxima · PE atual e máximo · Integridade e o estágio · Defesa · os três ataques · CD de feitiço · os 4 Testes de Resistência · **só as 8 ou 9 perícias treinadas** · os feitiços com custo · as condições ativas.

### O que fica de fora

Atributos crus, Origem, Trilha, Legados, aparência, história, laços, o catálogo de Melhorias, e as 15 perícias não treinadas. Nada disso muda durante a sessão.

---

## 6 · As três reservas, e como elas se comportam

O sistema tem três, e cada uma tem conta diferente.

| reserva | máximo | quem mexe |
|---|---|---|
| **Vida** | `(inicial do Caminho + Con) + (por nível + Con) × (nível − 1)` | dano e cura |
| **Energia (PE)** | `PE por nível do Caminho × nível` | conjurar e descansar |
| **Integridade** (alma) | `20 + 8 × (nível − 1)`, plana e igual para todos | dano de alma |

### O modelo de campo que isso pede

Cada reserva precisa de **três células**, não uma:

```
   MÁXIMO        calculado por fórmula, travado contra edição
   ATUAL         o jogador digita
   TEMPORÁRIO    o jogador digita, e some sozinho no fim da cena
```

> **Decidido (A4): os dois.** O `ATUAL` aceita edição direta **e** existe uma caixinha de delta ao lado, onde o jogador digita `-9` ou `+4` e o script aplica e limpa. O porquê está no `DECISOES-bloco-A.md`, e o resumo é que o gatilho não roda sem sinal — sem o atual editável, a ficha vira pedra na mão do jogador no meio da sessão.

O `MÁXIMO` continua travado contra edição, porque ele é fórmula.

### O estágio de alma se calcula sozinho

O manual dá quatro estágios por fração de Integridade perdida:

| perdida | estágio | o que pega |
|---|---|---|
| 1/4 | 1 | desvantagem em testes de perícia |
| 1/2 | 2 | deslocamento pela metade, e todo feitiço custa +1 PE por Classe |
| 3/4 | 3 | desvantagem em ataques e TRs; não conjura acima de metade da Classe máxima |
| toda | 4 | você não é mais você; o que sobra é decisão do mestre |

**O jogador nunca marca isso.** A ficha lê a Integridade atual e mostra o estágio e o efeito. É uma das automações que mais valem, porque estágio de alma é fácil de esquecer na mesa.

### Descanso longo

Devolve toda a Integridade e a vida máxima, e **limpa os estágios**. O script pode ter um botão `descanso longo` que faz os três de uma vez.

---

## 7 · O que o Apps Script faz

Roda **uma vez**, por você, na ficha-modelo. Os jogadores copiam o modelo pronto e não rodam nada.

| o que | por quê |
|---|---|
| **checkbox nativo** em perícias, ofícios, TRs e Famílias | `requireCheckbox()`; o `.xlsx` não carrega checkbox, só texto `☐` |
| **aplicar a fonte** em toda a planilha | resolve o Calibri, e garante no Sheets |
| **proteger as células de fórmula** | o jogador não apaga a Vida sem querer |
| **notas nos cabeçalhos** | a regra fica disponível ao passar o mouse, sem ocupar pixel |
| **formatação condicional** | acende quando as perícias passam de 9, quando as Famílias não são 2 e 3, quando o feitiço estoura o orçamento |
| **descanso, por caixa de seleção** | curto devolve 25% do PE; longo devolve tudo e limpa estágio |
| **entrada por delta** | digitar `-9` no dano em vez de recalcular a vida atual |

> **O que precisa ficar claro:** o script roda no Sheets, não no arquivo `.xlsx`. O `.xlsx` é só o veículo do layout. Quem faz a ficha ser ficha é o script.

### Duas coisas medidas sobre o script, e uma delas mata o botão

**Botão desenhado não funciona no app de celular do Sheets.** Ele é coisa de navegador. E o descanso é justamente uma das coisas que se aperta pelo telefone, na `MESA`.

O substituto é **caixa de seleção ou lista suspensa fazendo papel de botão**: o jogador marca a caixa, o gatilho roda e desmarca. Isso funciona no celular.

**E o script sobrevive à cópia.** Quando o jogador copia a planilha, o código vai junto. Escrito como gatilho simples — daqueles que só mexem na própria planilha — ele nem pede autorização.

O que ele **não** faz é rodar sem sinal. O gatilho roda no servidor do Google; sem rede, o que o jogador digitou fica parado no campo até o telefone sincronizar. É por isso que nada que o script faz pode ser o único caminho para uma coisa que se precisa fazer no meio da sessão.

---

## 8 · Uma lacuna nova, achada escrevendo isto

**Vida temporária não tem regra geral no manual.**

Ela aparece em pelo menos três lugares que a concedem:

- `Apoio` (Forma): cada ponto que sobra vira 3 de vida temporária
- `Fluxo` (aptidão): ao conjurar Classe 3 ou mais, 2 × Classe de vida temporária
- `Vento a Favor` (feitiço de exemplo): 9 de vida temporária

Mas o manual **não diz** se ela empilha, quando ela some, nem se é consumida antes da vida normal.

A **energia** temporária tem essa regra, e ela está enterrada dentro do `Braseiro`, o nível 11 da Trilha Brasa: *"nunca passa de 2 acumulados e some no fim da cena. Energia temporária gasta como PE, e gasta primeiro."*

Duas coisas seguem daí:

1. A ficha digital **não pode automatizar vida temporária** sem essa regra. O campo fica, o comportamento não.
2. Uma regra que vale para o sistema inteiro está escrita dentro de uma entrega de Trilha de nível 11. Quem não joga Brasa nunca lê. **Isso é candidato a subir para o capítulo de vida, energia e alma.**

> **Decidido (A2).** A vida temporária não empilha: fica a maior. Some no fim da cena, e é gasta antes da vida normal — e essa última parte já era do manual, porque a Melhoria `Rasga Escudo` só faz sentido se for.
>
> A regra sobe para o capítulo de vida, energia e alma, **as duas, vida e energia**. O texto está pronto em `manual-temporario.md`, e quem aplica no repositório do manual é o Mizuki.
>
> A energia continua **acumulando** até o teto que a fonte declarar, e o teto de 2 é do `Braseiro`, não do sistema. Os detalhes no `DECISOES-bloco-A.md`.

---

---

## 10 · O bloco de feitiço: seis dos nove campos são calculados

Você propôs `Nome · Classe · Melhorias · Restrições · Ação · Alcance · Duração · Alvo · Descrição`, e achou que automatizar isso daria trabalho.

**Dá o contrário.** O seu sistema define quase tudo a partir de quatro escolhas.

| campo | o jogador faz | de onde sai |
|---|---|---|
| Nome | **digita** | dele |
| Forma | **escolhe** | dropdown das 10 |
| Classe | **escolhe** | dropdown |
| Melhorias | **escolhe** | dropdown das 66, filtrado pelas Famílias Fechadas |
| Restrições | **escolhe** | dropdown das 19 |
| Descrição | **digita** | dele |
| **Ação** | nada | Padrão por default; `Rápido` → Bônus; `Reação` → Reação; `Lento` → Completa; `Carregar` → +1 turno |
| **Alcance** | nada | tabela base por Forma e Classe, mais os degraus que `Longe` e `Muito Longe` sobem |
| **Alvo** | nada | Forma, mais `Mais Um`, `Rajada` e `Salto` |
| **Como resolve** | nada | Forma; `Certeiro` tira o acerto, `Inescapável` tira os dois |
| **Custo em PE** | nada | `3 × Classe`, e `+1 por Classe` no estágio 2 de alma |
| **Dano** | nada | pontos não gastos, em d8 |

Rodado contra os dois feitiços publicados no manual:

```
Marca do Carrasco   escolhas: Projétil, Classe 3, Marca+Queima, Uma Vez
   Ação           Ação Padrão
   Alcance        18 m
   Alvo           um alvo
   Como resolve   rolagem de acerto
   Custo em PE    9 (+3 se estágio 2 de alma)

Domo de Gelo        escolhas: Explosão, Classe 3, Terreno+Maior, Condicional
   Alcance        raio 3 m a 18 m
   Alvo           área
   Como resolve   Teste de Resistência, metade no sucesso
```

**Duração é o único que fica de fora.** Ela não é derivável: a maioria dos feitiços resolve na hora, e quando dura, a duração vem escrita na Melhoria (`Fica` dura 1 minuto, `Armado` dura a cena). Esse campo continua digitado, ou vira uma lista curta.

### Uma contradição que a ficha deve recusar

Testando, apareceu: **`Rápido` (Melhoria) e `Lento` (Restrição) no mesmo feitiço se contradizem.** Um diz Ação Bônus, o outro diz rodada inteira.

A regra de ouro nº 7 proíbe duas Restrições que cobram a mesma coisa, mas **não alcança Melhoria contra Restrição.** Hoje isso cai no "o mestre pode recusar". A ficha digital consegue pegar sozinha, e vale a pena: é o tipo de coisa que passa quando sete mestres conferem no olho.

> **Decidido (A3): vira trava na ficha, e o manual fica calado.** A ficha recusa a montagem; o `conferir_feitico.py` já checa, e o `arnes.py` prova que a checagem acende e que ela fica quieta quando devia.
>
> A trava pega **dois** pares, e eles têm fontes diferentes: `Rápido` + `Reação` está escrito no manual e nunca tinha sido automatizado; `Rápido` + `Lento` é decisão da ficha.
>
> E o problema era maior do que parecia: com as duas juntas o jogador embolsa **um terço do orçamento do feitiço**, em qualquer Classe. A conta está no `DECISOES-bloco-A.md`.

---

## 11 · Onde o catálogo mora, e por que isso é o maior risco do projeto

Este é o assunto que ainda não tinha sido levantado, e ele é o mais caro.

A ficha embute o catálogo: as 66 Melhorias, as 19 Restrições, os 5 Caminhos, as 23 perícias. Se cada jogador tem uma **cópia** do modelo, então:

- cada ficha carrega a sua própria cópia do catálogo
- o manual muda (o projeto está em versão 0.10x e continua andando)
- **todas as fichas em circulação ficam desatualizadas ao mesmo tempo, e ninguém sabe quais**

Isso é a lição nº 9 do projeto — *"um número que mora em dois documentos vai divergir"* — multiplicada pelo número de jogadores. E é exatamente o defeito que acabou de ser achado nas Famílias, só que distribuído.

### As três saídas, com o preço de cada uma

| saída | como | o que custa |
|---|---|---|
| **catálogo central** | uma planilha só com a aba `DADOS`, e as fichas puxam por `IMPORTRANGE` | cada ficha precisa autorizar o acesso uma vez; se a central sair do ar ou for renomeada, as fichas quebram; fica mais lento |
| **cópia com carimbo** | cada ficha guarda o catálogo e uma célula com a versão dele; um validador compara com a versão corrente | não conserta nada sozinho, mas **você sabe** qual ficha está atrasada, e o jogador vê um aviso |
| **cópia surda** | como está hoje | de graça, e é a que garante o problema |

**A do meio é a mais barata que resolve alguma coisa**, e ela combina com o jeito do projeto: não impede a divergência, mas faz ela aparecer. As seis checagens do `conferir-ficha.py` funcionam assim.

> **Decidido (A1): a do meio, com um detalhe que veio de medir a plataforma.** A ficha guarda a cópia do catálogo, e uma célula só puxa da central o número da versão corrente. Se a central sumir, a ficha perde o aviso e **não perde nenhum menu**.
>
> Duas coisas medidas mudaram o preço da tabela acima. **A cópia local não é opcional em saída nenhuma**, porque no Sheets uma lista suspensa só aponta para intervalo da mesma planilha. E **renomear a central não quebra nada** — o `IMPORTRANGE` guarda o identificador do arquivo, não o nome. O que quebra é apagar, ou perder o acesso.
>
> O catálogo inteiro dá 245 linhas, então "fica mais lento" também não era preço real. Detalhes no `DECISOES-bloco-A.md`.

---

## 12 · Um bug latente na fórmula de Defesa

A fórmula do protótipo é `= 10 + Destreza + 1`, com o `1` escrito na mão.

O manual diz: *"Sem Traje e sem Revestimento, a sua proteção é 1/3 do refino + 1."*

O `1` está certo **hoje**, porque a ficha nasce no nível 2 com refino 1. Ele fica errado em dois momentos:

1. **refino 3**, quando a proteção vira 2
2. **qualquer equipamento**, porque Traje, Revestimento e escudo **desligam** a aptidão e entregam a proteção deles no lugar

A correção é a proteção virar célula própria, calculada:

```
proteção = SE(tem equipamento ; proteção do equipamento ; ARRED.ABAIXO(refino/3) + 1)
Defesa   = 10 + Destreza + proteção
```

Isso é a armadilha nº 1 do projeto aparecendo de novo: *"esse número já inclui o que eu estou somando nele?"*

---

## 14 · A progressão, do nível 2 ao 30

**Decidido: a ficha acompanha o personagem a campanha inteira, e calcula sozinha.** O jogador digita o nível; **o XP fica manual**, porque automatizar faixa de XP não paga o trabalho.

### Todas as colunas saem de fórmula

Testei as cinco colunas numéricas da tabela da página 192 contra fórmula, nos trinta níveis:

| coluna | fórmula | confere |
|---|---|---|
| maestria | `1 + quantos de (10, 18, 26) ≤ nível` | 30/30 |
| espaços de feitiço | `2 + (nível ÷ 2) + marcos alcançados` | 30/30 |
| refino de graça | `1 + marcos alcançados` | 30/30 |
| Classe máxima | `quantos de (1, 5, 9, 13, 17, 21, 26) ≤ nível` | 30/30 |
| Classe 0 grátis | `2 + quantos de (5, 11, 17) ≤ nível` | 30/30 |
| Integridade | `20 + 8 × (nível − 1)` | por definição |

**A ficha não precisa carregar a tabela.** Ela calcula, e por isso nunca desatualiza em relação a ela. Os marcos são 6, 10, 14, 18, 22, 26 e 30, e cada um dá de graça `+1 ponto de atributo`, `+1 de refino` e `+1 espaço de feitiço`.

### O que NÃO sai de fórmula, e vira catálogo

As entregas de regra, que são vinte linhas: degrau de Caminho (níveis 2, 7, 15, 30), entrega de Trilha (2, 11, 19, 27), abertura de Classe, liberação de Passiva, Técnica Máxima no 17, e as três Liberações Máximas (10, 20, 30).

Essas a ficha **avisa**, não aplica: no nível 11 ela diz *"entrega de Trilha disponível"* e o jogador escolhe.

### O erro que este teste pegou, e ele era meu

A especificação dizia *"maestria: 1, e sobe +1 a cada oito níveis"*. Essa frase é ambígua, e a leitura natural dela é `1 + nível÷8`. **Essa fórmula erra nos níveis 8, 9, 16, 17, 24 e 25**, dando maestria alta demais e com ela `+1` na CD de feitiço e `+1` no ataque de conjuração.

A tabela da página 192 é a dona: a maestria vira 2 no nível **10**, 3 no **18**, 4 no **26**.

> **E a Kaori não pegaria isso nunca.** Ela é nível 2, e o erro só aparece do 8 em diante. É a segunda vez nesta conversa que o caso de teste único passa por cima de um defeito: a primeira foi ele não expor a divergência das Famílias. **Uma ficha de nível alto precisa entrar como segundo caso de teste.**

O `conferir-progressao.py` reproduz as trinta linhas e traz contra-teste: ele prova que a fórmula antiga reprova nos seis níveis, senão a checagem seria trivialmente verdadeira.

---

## 15 · Feitiços em dois níveis de detalhe

**Decidido: uma página de uso rápido, e o bloco completo em outro lugar que ela puxa.**

### A linha de uso rápido, na `MESA`

Uma linha por feitiço, com o que se olha no meio do turno:

```
NOME              CL   AÇÃO      ALCANCE   ALVO       DANO    PE   RESOLVE
Marca do Carrasco  3   Padrão    18 m      um alvo    6d8      9   acerto
Domo de Gelo       3   Padrão    r 3 m/18  área       5d8      9   TR, metade
```

Sete colunas, e **seis delas são calculadas** (seção 10). Cabe nas 12 colunas do celular se as colunas forem estreitas e o nome truncar.

### O bloco completo, na `TÉCNICA`

O formato que você descreveu, um bloco por feitiço: `Nome · Classe · Forma · Melhorias · Restrições · Ação · Alcance · Duração · Alvo · Como resolve · Dano · PE · Descrição`.

**A `MESA` puxa da `TÉCNICA` por fórmula.** O jogador monta uma vez no PC, e a linha de uso rápido aparece sozinha no celular. Nenhum dado digitado duas vezes.

### Por que essa divisão e não uma página só

No meio do turno ninguém lê as Melhorias que comprou; lê o dano e o alcance. Na hora de montar o feitiço ninguém precisa da linha compacta. **São dois momentos diferentes, e o mesmo dado serve os dois em formatos diferentes.**

---

## 16 · As cinco que faltavam: decididas

As cinco decisões que travavam a construção estão fechadas, e **o dono delas é o `DECISOES-bloco-A.md`**, com os valores em `decisoes-ficha.json`.

Não repito nenhum número aqui de propósito. Se o mesmo valor morar neste documento e lá, um dia os dois discordam — que é a lição nº 9 do projeto, e ela já custou caro nas Famílias.

| | onde este documento falava disso |
|---|---|
| A1 · onde o catálogo mora | seção 11 |
| A2 · vida temporária | seção 8 |
| A3 · `Rápido` + `Lento` | seção 10 |
| A4 · delta ou valor absoluto | seção 6 |
| A5 · o acento colorido | seção 3 |

Cada uma dessas seções ganhou uma linha dizendo o que foi decidido e apontando para cá. O `conferir-decisoes.py` confere que os documentos continuam de acordo.

### Já decidido, para não reabrir

| | |
|---|---|
| plataforma | Google Sheets |
| automação | Apps Script, uma vez no modelo |
| paleta | as duas cores do servidor, com os papéis corrigidos por contraste |
| celular | aba `MESA` própria, 12 colunas |
| progressão | automática do 2 ao 30; **XP manual** |
| feitiços | uso rápido na `MESA`, bloco completo na `TÉCNICA` |
| perícias | 8 ou 9, o jogador escolhe |
| `Queima` | conta no teto de dano |
