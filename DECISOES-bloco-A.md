# Bloco A · as cinco decisões que travavam a construção

Decididas pelo Mizuki em 18/08/2026.

Este documento é o **dono** das cinco. Os valores em forma de dado moram no `decisoes-ficha.json`, e é de lá que o script, o validador e a ficha leem. O `PENDENCIAS.md` e o `DESIGN-ficha-digital.md` apontam para cá em vez de repetir — se o número morar em dois documentos, os dois divergem, e isso já aconteceu neste projeto com as Famílias.

O `conferir-decisoes.py` confere que este documento, o JSON e os outros dois continuam falando a mesma coisa.

---

## A1 · O catálogo mora numa cópia local, com aviso vivo

**Cada ficha guarda o catálogo inteiro.** Fixo, dentro dela, e nunca depende de rede para funcionar.

Ao lado dele, **uma célula só** puxa da planilha central o número da versão corrente. Se as duas versões diferirem, a ficha mostra um aviso ao jogador.

### O que mudou em relação ao que estava escrito

Duas coisas foram medidas e contradizem o preço do `PENDENCIAS` antigo.

**A cópia local não é opcional.** No Google Sheets, uma lista suspensa só consegue apontar para um intervalo da **mesma** planilha. Então nem na saída "catálogo central" a ficha ficaria sem cópia — ela só teria uma cópia que se atualiza sozinha. Isso derruba metade da vantagem que a central parecia ter.

**Renomear a central não quebra nada.** O `IMPORTRANGE` guarda o identificador do arquivo, não o nome. O que quebra de verdade é apagar a central, ou o jogador perder o acesso a ela.

E o catálogo inteiro dá 245 linhas. Nesse tamanho, "fica mais lento" não é preço real.

### O que isso obriga na construção

| | |
|---|---|
| a aba `DADOS` | carrega o catálogo e a versão dele numa célula |
| a célula da versão corrente | um `IMPORTRANGE` de uma célula só, apontando para a central |
| se a central sumir | a ficha perde o aviso, e **nenhum menu suspenso esvazia** |
| o aviso | texto visível, não só cor — o jogador lê "sua ficha está na v0.10, a atual é v0.12" |

---

## A2 · Vida temporária: não empilha, fica o maior

**Vida temporária não soma com vida temporária.** Fonte nova chega, você fica com a maior das duas. Some no fim da cena, e é gasta antes da vida normal.

### O que aqui é do manual, e o que é decisão

Isso importa porque a regra de não inventar vale.

**"Gasta primeiro" já é do manual.** A Melhoria `Rasga Escudo` diz: *"o dano ignora pontos de vida temporários e barreiras: bate direto na vida."* Se a temporária não fosse consumida antes, essa Melhoria não teria o que ignorar. A regra existe, só estava implícita.

**"Não empilha" e "some no fim da cena" são decisão.** Elas copiam a forma da regra que o `Braseiro` dá para a energia temporária, e batem com o que qualquer jogador de d20 já espera.

### Por que não dá para copiar o teto de 2

A energia temporária tem teto: *"nunca passa de 2 acumulados"*. A vida temporária não pode ter um número desses, porque as fontes variam demais:

| onde | quanto |
|---|---|
| `Apoio` (Forma) | 3 por ponto que sobra |
| `Fluxo` (Legado 2) | 2 × Classe |
| `Aprumo` (Trilha, nível 11) | 1d10 + atributo de ataque |
| `Crosta` (Arremate, nível 19) | a sua maior Classe |
| `Vento a Favor` (feitiço, p.137) | 9 |
| `Muralha` (feitiço, p.137) | 18 |

De 2 a 18. Qualquer teto fixo aqui seria invenção. O "fica o maior" resolve o mesmo problema sem escolher número nenhum.

> O `PENDENCIAS` antigo dizia três fontes. São seis. As três que faltavam são `Aprumo`, `Crosta` e `Muralha`.

### E a energia continua diferente da vida

Vale registrar, porque é fácil achar que as duas viraram a mesma regra e elas não viraram.

O `Braseiro` diz *"nunca passa de 2 **acumulados**"*. Ou seja, a energia temporária **acumula** até um teto. A vida temporária **não acumula**, fica a maior. São dois comportamentos, e os dois estão certos: o teto de 2 é do `Braseiro`, não do sistema, e hoje o `Braseiro` é a única fonte de energia temporária que existe no manual.

### A2b · Isso sobe para o capítulo p.15

O capítulo **Vida, energia e alma** tem as três reservas e para aí. Nenhuma palavra sobre temporário, nem de vida nem de energia.

As duas regras sobem para lá. O texto proposto está no `manual-temporario.md`, pronto para colar — **eu não mexi no repositório do manual.**

Com isso, a regra da energia temporária deixa de ser lida só por quem joga Brasa.

---

## A3 · `Rápido` + `Lento` vira trava só na ficha

A ficha recusa a montagem. **O manual fica calado.**

### O tamanho do problema

Isso não era só contradição de texto. Era desconto.

`Rápido` é Melhoria Pesada. `Lento` é Restrição que devolve Média. Com as duas no mesmo feitiço, o jogador paga a que vale e embolsa a devolução da que não vale:

```
Classe  orçamento  Rápido custa  Lento devolve  economia  % do orçamento
     1          3             2              1         1        33%
     3          9             5              3         3        33%
     5         15             8              5         5        33%
     7         21            11              7         7        33%
```

Um terço do orçamento, em toda Classe. E com a Família Tempo Livre, o `Rápido` — a Pesada mais forte da Família — sai **de graça**.

### O que fica em aberto, e é escolha registrada

O manual continua sem a frase. Então **quem monta feitiço no papel ou no gerador do manual continua com o desconto disponível**, e continua dependendo de o mestre perceber.

Isso é dívida conhecida, não descuido. Está no `PENDENCIAS.md` como B6.

> O molde da frase, se um dia você quiser escrever: o manual já resolve exatamente esse tipo de briga na entrada do próprio `Rápido`, com *"Não entra no mesmo feitiço que Reação."* Bastaria a mesma forma.

### O que a ficha checa

Duas incompatibilidades, e elas têm fontes diferentes:

| par | fonte |
|---|---|
| `Rápido` + `Reação` | **manual**, tabela da Família Tempo |
| `Rápido` + `Lento` | **ficha**, decisão A3 |

A primeira nunca tinha sido automatizada em lugar nenhum, apesar de estar escrita. Entra junto.

---

## A4 · Vida e PE têm o atual editável **e** uma caixinha de delta

O jogador digita `-9` na caixinha e o script aplica e limpa. Se preferir, edita o atual direto.

### O que foi medido, e mudou o preço

**O script sobrevive à cópia.** Quando o jogador copia a planilha, o código vai junto. Escrito como gatilho simples — daqueles que só mexem na própria planilha e em mais nada — ele nem pede autorização. O `PENDENCIAS` antigo dizia que o delta "some se alguém copiar a ficha para fora do modelo". Não some.

**Mas ele não roda sem sinal.** O gatilho roda no servidor do Google. O jogador digita `-9` no celular, o campo fica com `-9` escrito, e nada acontece até o telefone sincronizar.

É por isso que os dois entram, e não só o delta: **o atual editável é o que impede a ficha de virar pedra na mão do jogador no meio da sessão.** A célula já precisava ser editável de qualquer jeito, então o custo disso é zero.

### Um achado que vale independente desta decisão

**Botão desenhado não funciona no app de celular do Sheets.** O `botão de descanso longo` que estava no documento de desenho não ia funcionar justamente onde ele mais serve, que é na aba `MESA`.

O substituto é caixa de seleção ou lista suspensa fazendo papel de botão. O gatilho pega isso normalmente.

---

## A5 · A cor entra como estado, não como decoração

Vida e Energia ficam em **osso** quando cheias, viram **âmbar** abaixo da metade e **vermelho** abaixo de um quarto.

```
cheio               osso      #E8DCD4
abaixo da metade    âmbar     #D89B3A
abaixo de 1/4       vermelho  #C2334D
```

### Por que essa sobrevive ao daltonismo e a outra não

A proposta de colorir Vida de vermelho e Energia de roxo morre na medida: para quem tem deuteranopia, **as duas viram a mesma cor** (1.09 de contraste na visão normal, 1.23 na deuteranopia).

A cor de estado passa, e a razão é estrutural: os três degraus estão em **claridades** diferentes, não em matizes diferentes. Quem não distingue vermelho de verde ainda distingue claro de escuro.

```
par                                normal   protan   deuter
osso (cheio) vs âmbar (metade)       1.80     1.88     1.69
âmbar (metade) vs vermelho (1/4)     2.24     2.51     1.95
osso (cheio) vs vermelho (1/4)       4.03     4.74     3.31

sobre o painel:  osso 12.18 · âmbar 6.76 · vermelho 3.02
```

### E a regra de sempre continua valendo

A cor não é o único meio de dizer nada. Sob esse esquema o número **já diz sozinho** que está baixo — a cor só chega junto. É o uso certo dela.

Vermelho na ficha continua querendo dizer "olha isso". Agora ele quer dizer duas coisas que são a mesma: regra violada, e vida acabando.

---

# Bloco C · as quatro que saíram do "falta algo antes de construir"

Decididas em 18/08/2026, depois de fechar o bloco A. Os valores estão no `decisoes-ficha.json` como `C1` a `C4`.

## C1 · O Evocador sai do menu, por enquanto

**O Caminho continua no manual e continua no catálogo. Quem some é a opção no menu da ficha.** Essa distinção não é preciosismo: o catálogo espelha o manual, e mexer nele para resolver um problema da ficha é exatamente como as Famílias divergiram.

O motivo é que o Evocador tem três buracos empilhados:

- as entregas de Trilha dos níveis 2, 11, 19 e 27 estão em escrita, e o próprio manual manda combinar com o mestre até saírem
- o `Casco` diz *"as suas invocações têm mais vida"* sem número, enquanto as outras duas opções da mesma escolha têm
- **a ficha da invocação não existe em versão nenhuma da ficha.** O manual tem um capítulo inteiro para ela — capítulo 14, nove páginas, com seção própria de ficha na p.180 e catálogo próprio na p.182 — e nem a especificação, nem o documento de desenho, nem a `ficha-em-branco.docx` têm um campo sequer

A ficha imprime `Evocador — em escrita, fale com o mestre` no lugar da opção.

O `conferir-decisoes.py` checa que o motivo ainda vale: se o `Casco` ganhar número no manual, a checagem acende e o Evocador pode voltar.

## C2 · O carimbo é a versão do projeto

**Hoje `0.104`**, de 18/08/2026. A dona dela é a entrada do topo do `CHANGELOG` do repositório do sistema.

Não é a `v7.10` do Manual do Fundamento: essa é só de um capítulo, e o catálogo saiu do PDF inteiro.

O catálogo ganhou o campo `_meta.versao`, que ele não tinha — sem ele a decisão A1 não tinha o que carimbar.

## C3 · A proteção vira célula, e ela é uma escolha

```
proteção = SE(usa equipamento ; a do equipamento ; ARRED.ABAIXO(refino/3) + 1)
Defesa   = 10 + Destreza + proteção
```

O protótipo tinha `10 + Destreza + 1`, com o `1` na mão. Ele acerta hoje por coincidência, porque a ficha nasce no nível 2 com refino 1, e erra no refino 3.

**A célula de equipamento entra agora vazia.** O catálogo do capítulo 12 entra depois; até lá o jogador digita o número. O que importa é que a fórmula já sabe que o equipamento **desliga** a aptidão em vez de somar com ela.

## C4 · Três fontes, e uma regra dura para o celular

| papel | fonte | onde |
|---|---|---|
| corpo | **Roboto** | todas as abas |
| título e número grande | **Oswald** | só nas abas de PC |
| marca em kanji | **Noto Sans JP** | só ornamento, área morta, só no PC |

**A `MESA` usa só Roboto, e isso é regra, não preferência.** O app de celular do Sheets tem menos fontes que o navegador e troca sem avisar as que estão fora da lista curta. Roboto está nela; Oswald não.

O `conferir-ficha-xlsx.py` reprova o arquivo se aparecer qualquer outra fonte na `MESA` — e reprovou, na primeira vez que rodou.

### O que foi medido

```
                    linha de feitiço da MESA        x/maiúscula
                    (o espaço é 336 px)
  Roboto                    308 px                     0.74
  Lexend                    333 px                     0.75      sem respiro
  Noto Sans JP              301 px                     0.74
  Oswald                    247 px                     0.71      20% mais estreita
  Anton                     273 px                     0.85
  Bebas Neue                230 px                     1.00      caixa alta, cansa
```

A razão x/maiúscula é o que separa fonte de texto de fonte de título. A primeira versão da medida usou só a altura de x e **aprovou a Bebas Neue como fonte de corpo**, o que está errado: nela a minúscula tem o tamanho da maiúscula.
