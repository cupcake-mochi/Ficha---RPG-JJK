# Ficha digital do Projeto M

Especificação de construção. Escrita para alguém que nunca viu este sistema conseguir montar a ficha sem ler as 199 páginas do manual, e sem ter que adivinhar qual número vem de onde.

Todo número aqui foi conferido contra o `Projeto-M-Manual-da-Guilda.pdf` (v7.10) e contra o repositório, por script. Onde eu não tinha certeza, está escrito que eu não tinha certeza.

> **Na v0.240 do sistema, as fórmulas da seção dos números derivados e o exemplo da Kaori foram trazidos para o manual de hoje:** *a Integridade, a CD, a conjuração, os dois ataques e o Teste de Resistência treinado.* **O resto deste documento continua conferido contra a v7.10**, e não foi relido.

---

## O que este documento é, e o que ele não é

**É** a lista completa do que a ficha precisa ter, com toda fórmula, toda lista fechada e toda regra que a ficha consegue recusar sozinha.

**Não é** escolha de plataforma. Planilha, HTML, bot ou VTT: a especificação vale igual nas quatro, e a decisão está na seção 10.

**Não é** o manual. Quando este documento e o manual discordarem, o manual vence, e o desacordo é bug deste arquivo.

### Como ler

| se você quer | vá para |
|---|---|
| entender o jogo em cinco minutos | seção 1 |
| começar a construir hoje | seção 2, e só depois volte |
| a lista de campos, campo a campo | seção 3 |
| a fórmula de um número específico | seção 4 |
| saber o que a ficha deve recusar | seção 5 |
| os catálogos para popular menu | seção 6 |
| testar se o que você fez está certo | seção 7 |
| o que não tem regra ainda | seção 9 |

---

## 1 · O sistema em uma página

Antes de qualquer campo, o que o jogo faz.

**O dado é o d20.** Você rola um d20, soma um número da ficha, e compara com uma dificuldade que o mestre diz. Igual ou maior, passou.

**Os cinco atributos** são Força, Destreza, Constituição, Inteligência e Essência. Eles vão de 0 a 6, e **o número é o modificador**. Atributo 3 soma 3. Não existe tabela de conversão, e isso é diferente da maioria dos sistemas de d20.

**Essência** é o atributo de energia amaldiçoada: sentir, projetar, impor presença. É o que em outro sistema seria Sabedoria e Carisma juntos.

**Maestria** é o bônus que cresce com o nível e entra em coisa treinada. Começa em 1.

**O que o personagem é feito**, na ordem em que se escolhe:

1. **Origem**: de onde veio a técnica. Nove rotas.
2. **Caminho**: o que ele faz numa luta. Cinco, e é o que decide vida e energia.
3. **Trilha**: a especialização dentro do Caminho. Três por Caminho.
4. **Fundamento**: a técnica dele. Uma frase de Regra, duas Famílias Livres, três Fechadas, e os feitiços.
5. **Legados**: duas coisas que ele já trazia de antes.

**Energia (PE)** é o combustível de feitiço. Um feitiço de Classe 1 custa 3 PE, um de Classe 2 custa 6, e assim por diante: sempre `3 × Classe`.

**Uma ficha nasce no nível 2**, com Grau 4 de patente. O teto é o nível 30.

> **Grau e nível não são a mesma coisa.** Nível é poder mecânico. Grau é a patente na hierarquia jujutsu, e ele começa em 4 e *desce* conforme o personagem sobe.

---

## 2 · A ficha mínima que já é útil

Se você tem pouco tempo, construa isto primeiro. São onze números, todos fórmula pura, nenhum depende de catálogo:

```
entra:  Caminho, nível, os cinco atributos
sai:    Vida, PE, Integridade, Defesa, Iniciativa, Deslocamento,
        Maestria, CD de feitiço, e os três ataques
```

Uma ficha que só faz isso já resolve o problema mais caro da guilda, que é dois mestres calculando a mesma coisa de jeitos diferentes. Tudo o mais é catálogo, e catálogo é trabalho, não é risco.

A seção 4 tem as onze fórmulas. A seção 7 tem o caso de teste para saber se você acertou.

---

## 3 · Anatomia: os quatro blocos

A ficha de papel tem quatro blocos, e a digital mantém a mesma divisão. Isso não é estética: um personagem atravessa mesas, e um mestre que já conhece a ficha de papel precisa achar as coisas no mesmo lugar.

### Bloco 1 · Identidade e números

**Campos de escolha livre:** nome do personagem, jogador, patente (começa em Grau 4), Caminho, Trilha, Origem, nível (começa em 2), XP.

**Os cinco atributos.** Escala 0 a 6. Na criação: **nove pontos distribuídos entre os cinco, nenhum acima de 3**.

**Os números derivados.** Nada aqui é escolha; tudo é fórmula, e a ficha digital deve calcular e travar contra edição manual. A lista está na seção 4.

> **A proteção 1 inicial não é equipamento.** Ela vem de `cobrir-se de energia`, uma aptidão gratuita do refino 1, e vale `⌊refino ÷ 3⌋ + 1`. Vestir Traje ou Revestimento **desliga** ela; o escudo **soma** por cima. Se a ficha somar a do uniforme com a do cobrir-se, a Defesa sai errada, e esse erro já viveu sete versões no repositório. *Até a v0.246 do sistema esta linha dizia que o escudo também desligava; o escudo soma desde a v0.42 de lá.*

### Bloco 2 · Perícias, ofícios e Testes de Resistência

**23 perícias**, cada uma com um atributo fixo que nunca muda. Constituição não tem nenhuma.

**Uma ficha treina 8 ou 9**, e quem decide é o jogador:

- o Caminho dá 2 fixas, mais 4 à escolha
- a Origem dá 2
- e sobra **um extra que pode ser um ofício livre, ou uma nona perícia no lugar dele**

Esse último ponto é o que faz a ficha precisar de um campo que muda de natureza conforme a escolha, em vez de oito linhas fixas.

**11 ofícios.** Ofício **não tem atributo fixo**: o mestre escolhe na hora, conforme o que você está fazendo com ele. Consertar uma tranca sob pressão pode ser Destreza; saber que tranca é aquela pode ser Inteligência. **Ofício sem treino você não tenta.**

**Quatro Testes de Resistência**, e dois deles são treinados na criação:

| teste | atributo |
|---|---|
| Físico | Força **ou** Destreza, escolhido e **travado na criação** |
| Vigor | Constituição |
| Intelecto | Inteligência |
| Espírito | Essência |

Treinado soma `+2`. O Físico é o único com escolha, e a ficha digital tem que travar essa escolha depois de feita.

### Bloco 3 · A técnica (Fundamento)

É a camada mais complexa, e a que mais se ganha em digitalizar, porque é a única com aritmética de verdade.

**A Regra.** Uma frase, verificável pela mesa, sem número. Nunca muda.

> A Kaori: *"Tudo que eu prendo entre as minhas mãos fica mais pesado."*

**Famílias.** As Melhorias estão divididas em nove Famílias. Na criação você escolhe:

- **duas Livres**: as Melhorias delas custam `metade da Classe` a menos, com mínimo de 1 ponto
- **três Fechadas**: você nunca compra nada delas, em Classe nenhuma
- as outras quatro ficam no preço normal

Fechar uma Família bloqueia as Formas dela junto. Quem fecha Amparo nunca vai curar, e Caminho nenhum contorna isso.

**Selo.** O gesto ou condição obrigatória para conjurar. Não custa nem devolve ponto.

> A Kaori: *"As duas mãos precisam se tocar antes."*

**Expressão da técnica.** Uma, de graça e sem ocupar espaço: uma manifestação ligada à Descrição. Não dá vantagem, não resolve teste e não revela informação. *Era a Passiva Livre até o livro reconstruído, que também chama a Passiva de Talento e a Classe Passiva de Categoria de Efeito.*

**Os feitiços.** Cada um tem um orçamento fechado:

```
Pontos       = 3 × Classe
Custo em PE  = 3 × Classe      (o mesmo número)
Teto de dano = 4 × Classe em dados, somando alvos e repetições
```

Cada ponto que sobra vira **um dado de dano**: um d8 que você rola quando o feitiço acerta.

Você gasta os pontos comprando **Melhorias**, e recupera pontos aceitando **Restrições**. E aqui está a trava mais importante do sistema inteiro:

> **Restrição paga Melhoria, e nunca vira dado de dano.** O que ela devolve a mais do que você gastou simplesmente some.

No nível 2: Classe 1, **três feitiços conhecidos**, mais **dois de Classe 0** que são grátis e não ocupam espaço.

### Bloco 4 · Quem é essa pessoa

Aparência, história, o que a Origem deu, o traço, **os dois Legados** (um Destranca obrigatório, mais um de qualquer formato), laços, o que a instituição sabe, e pacto se houver.

**Nada aqui rola dado.** Numa guilda com sete mestres, essa página é o que faz o personagem ser reconhecido numa mesa onde ele nunca jogou. Ela não é enfeite, e cortar ela para "economizar espaço" é o erro mais fácil de cometer numa ficha digital.

---

## 4 · Todas as fórmulas

Nenhuma destas é escolha. Todas devem ser calculadas pela ficha e travadas contra edição manual.

### Os números derivados

| campo | fórmula |
|---|---|
| Vida | `(vida inicial do Caminho + Con) + (vida por nível do Caminho + Con) × (nível − 1)` |
| Energia (PE) | `PE por nível do Caminho × nível` |
| Integridade | `20 + (Essência + 5) × (nível − 1)` |
| Defesa | `10 + Destreza + proteção` |
| Iniciativa | `d20 + Destreza` |
| Deslocamento | `9 m` |
| Maestria | `1`, e vira 2 no nível **10**, 3 no **18**, 4 no **26**. Ver o aviso abaixo |
| Proteção inicial | `⌊refino ÷ 3⌋ + 1`, e some se vestir equipamento |
| CD de feitiço | `8 + atributo da técnica + maestria` |
| Ataque de conjuração | `d20 + atributo da técnica + maestria` |
| Ataque corpo a corpo | `d20 + Força + maestria` |
| Ataque à distância | `d20 + Destreza + maestria` |
| Perícia treinada | `d20 + atributo + maestria` |
| Perícia sem treino | `d20 + atributo` |
| Teste de Resistência | `d20 + atributo do TR`, mais a maestria se treinado |

> **Cuidado com a maestria, e este erro já foi cometido.** A descrição "sobe +1 a cada oito níveis" é ambígua e produz `1 + nível÷8`, que **erra nos níveis 8, 9, 16, 17, 24 e 25**: dá maestria alta demais, e com ela `+1` na CD de feitiço e `+1` no ataque de conjuração.
>
> A tabela da página 192 do manual é a dona: a maestria vira 2 no nível **10**, 3 no **18** e 4 no **26**. A fórmula que reproduz as trinta linhas é `1 + quantos de (10, 18, 26) ≤ nível`.

### O orçamento de feitiço

| conta | valor |
|---|---|
| Pontos do feitiço | `3 × Classe` |
| Custo em PE | `3 × Classe` |
| Teto de dano | `4 × Classe` em dados, somando alvos e repetições |
| Dano contra um alvo só | para nos pontos da Classe, ou seja `3 × Classe` |
| Liberação Máxima | `+ Classe` em dados, e é ela que alcança o teto num alvo |
| PE da Liberação Máxima | `50%` a mais que a Classe dela, arredondando para cima |
| Feitiço de Classe 0 | grátis em PE, e não ocupa espaço de conhecido |
| Devolução máxima de Restrição | `2 × Classe` |
| Melhoria Leve | `Classe ÷ 2` |
| Melhoria Média | `Classe` |
| Melhoria Pesada | `Classe × 1,5` |
| Desconto de Família Livre | tira `Classe ÷ 2` do preço, com mínimo de 1 |
| Ponto não gasto | vira `1d8` de dano |

> **O teto de `4 × Classe` não é um número solto.** Ele é `3 × Classe` do orçamento mais `Classe` da Liberação Máxima. Por isso ele nunca morde num feitiço comum de alvo único: só é alcançável espalhando o dano, ou com Liberação.

### Arredondamento

> **Sempre para o lado que não te favorece.** Custo sobe, ganho desce, e o que você ganha nunca fica abaixo de 1.

Numa ficha digital isso quer dizer: `ceil` em custo, `floor` em benefício, e um `max(1, …)` em cima do resultado de ganho. Errar o sentido do arredondamento em uma peça só já produz duas fichas diferentes na mesma guilda.

### A tabela de Classe, pronta

| Classe | abre no nível | pontos e PE | Leve | Média | Pesada | devol. máx | Liberação | teto | dano cheio |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 3 | 1 | 1 | 2 | 2 | +1 | 4 | 3d8 |
| 2 | 5 | 6 | 1 | 2 | 3 | 4 | +2 | 8 | 6d8 |
| 3 | 9 | 9 | 2 | 3 | 5 | 6 | +3 | 12 | 9d8 |
| 4 | 13 | 12 | 2 | 4 | 6 | 8 | +4 | 16 | 12d8 |
| 5 | 17 | 15 | 3 | 5 | 8 | 10 | +5 | 20 | 15d8 |
| 6 | 21 | 18 | 3 | 6 | 9 | 12 | +6 | 24 | 18d8 |
| 7 | 26 | 21 | 4 | 7 | 11 | 14 | +7 | 28 | 21d8 |

---

## 5 · As travas: o que a ficha digital deve recusar

Isto é o que uma ficha digital faz que o papel não faz. Cada item abaixo é verificável por código.

### Na criação

| trava | regra |
|---|---|
| pontos de atributo | exatamente 9 distribuídos, e nenhum acima de 3 |
| perícias treinadas | 8, ou 9 se o jogador trocou o ofício extra |
| Testes de Resistência | exatamente 2 treinados |
| TR Físico | Força ou Destreza, e trava depois de escolhido |
| Famílias | exatamente 2 Livres e 3 Fechadas, sem repetir |
| Legados | exatamente 2, e um deles tem que ser Destranca |

### As oito regras de ouro do feitiço

Se um feitiço passa nas oito, ele é legal. O checklist do mestre é exatamente esta lista.

| # | regra | a ficha consegue checar? |
|---|---|---|
| 1 | Restrição paga Melhoria, nunca vira dado de dano. O excedente some | **sim** |
| 2 | Dano total, somando alvos e repetições, nunca passa de `4 × Classe` | **sim**, e é a que mais escapa no olho |
| 3 | Melhorias: 2 nas Classes 1 e 2, 3 nas 3 e 4, 4 da 5 em diante. Restrições: até 2. A Forma não conta | **sim** |
| 4 | Restrição devolve no máximo `2 × Classe` | **sim** |
| 5 | Liberação Máxima custa a rodada inteira, e você só tem as que o nível deu | **sim** |
| 6 | Feitiço em Ação Bônus ou Reação só permite mais um de Classe 0 no turno | parcial, depende do turno |
| 7 | Duas Restrições não podem ser as duas de frequência, nem cobrar a mesma coisa | **sim** na frequência, não no "mesma coisa" |
| 8 | Restrição que não atrapalhou em três sessões é trocada | **não.** É de mesa, não de código |

Mais duas notas que acompanham as oito:

- **Restrição que o Selo já obriga não devolve ponto.** A ficha precisa de um campo ligando as duas coisas.
- **O mestre pode recusar qualquer feitiço**, mesmo um que passe em tudo. A ficha valida; ela não aprova.

### Duas armadilhas de implementação

**A regra 3 usa "não conta" para duas coisas diferentes.** A Forma não conta no *limite de quantas Melhorias*, mas **conta no orçamento**: `Explosão` custa Leve, `Cura` custa Média, `Onda` custa Pesada. Um validador que esquece isso erra o dano para baixo, e ele erra em silêncio.

**A regra 7 tem uma lista fechada de Restrições de frequência**: `Uma Vez`, `Condicional`, `Aquecer`, `Dívida`, mais qualquer `Restrição Própria` que faça a mesma coisa. Escolha no máximo uma. As quatro primeiras dá para checar por código; a quinta precisa do mestre.

### As quatro peças que espalham dano

Só estas quatro fazem o total crescer acima do golpe base, e são as que a regra 2 existe para pegar:

`Salto` · `Rajada` · `Mais Um` · `Queima`

`Salto` e `Queima` **somam** metade dos dados. `Mais Um` e `Rajada` **dividem**, então a soma das partes não cresce, mas ainda contam no teto.

---

## 6 · Os catálogos

Todos saíram do manual por script e batem com a contagem que o próprio manual declara por extenso. O arquivo `catalogo-projeto-m.json` traz todos eles em forma de dados, com a descrição de cada item.

### Os seis Caminhos

> *Eram cinco até o livro reconstruído de 04/10/2026, que trouxe o Incursor, trocou as perícias fixas do Bastião e tirou o dado de vida. A Vanguarda não tem vida inicial na tabela dela: os 8 vêm do `fora_do_livro` do catálogo, até o livro decidir.*

| Caminho | vida no nível 1 | vida por nível | PE por nível | perícias fixas | atributos naturais | armas |
|---|---|---|---|---|---|---|
| Bastião | 12 | 7 | 4 | Atletismo · Provocar | Força · Constituição | as treze categorias |
| Vanguarda | 8 | 5 | 5 | Acrobacia · Percepção | Destreza · Força | as treze categorias |
| Guia | 8 | 5 | 5 | Persuasão · Medicina | Essência | Arma de Fogo e Balestra |
| Emanador | 6 | 4 | 6 | Ocultismo · Investigação | Inteligência · Essência | Arma de Fogo e Balestra |
| Evocador | 6 | 4 | 6 | Religião · Lidar com Animais | Inteligência · Essência | Arma de Fogo e Balestra |
| Incursor | 6 | 4 | 6 | Acrobacia · Intuição | Destreza · Força | as treze categorias |

### As 23 perícias, por atributo

| atributo | perícias | quantas |
|---|---|---|
| Força | Atletismo | 1 |
| Destreza | Acrobacia · Furtividade · Pontaria · Prestidigitação | 4 |
| Constituição | (nenhuma) | 0 |
| Inteligência | Investigação · Intuição · Ocultismo · Religião · História · Hierarquia · Medicina · Sobrevivência · Natureza · Lidar com Animais · Tecnologia | 11 |
| Essência | Sentir Energia · Percepção · Persuasão · Enganação · Intimidação · Atuação · Provocar | 7 |

### Os 11 ofícios

A Origem dá dois, e eles podem ser trocados por mais uma perícia livre. O atributo é o padrão da tabela do livro; a tarefa pode pedir outro.

| ofício | atributo padrão |
|---|---|
| Condução | Destreza |
| Arrombamento | Destreza |
| Herbalismo | Inteligência |
| Forja | Força |
| Caligrafia | Destreza |
| Burocracia | Inteligência |
| Entalhador | Destreza |
| Alfaiate | Destreza |
| Culinária | Inteligência |
| Instrumento | Essência |
| Jogatina | Essência |

### As nove Famílias

| Família | do que trata | Melhorias |
|---|---|---|
| Alcance | Aumentar distância; mover você ou um alvo | 7 |
| Área | Aumentar uma área; dividir um ataque; alcançar mais alvos | 8 |
| Mira | Melhorar o acerto; atravessar proteção | 8 |
| Controle | Aplicar condições; criar obstáculos; limitar movimento | 7 |
| Auxiliares | Dar vantagens e bônus; prejudicar rolagens | 9 |
| Castigo | Acrescentar dano em situações determinadas | 7 |
| Tempo | Mudar a ação, o momento ou a duração | 8 |
| Marca | Preparar ataques; rastrear; recuperar recursos | 7 |
| Amparo | Curar, proteger e remover condições | 7 |

### As dez Formas

| Forma | custa | Família | o que é |
|---|---|---|---|
| Projétil | nada | de todo mundo | Um alvo a até 18 m |
| Toque | nada | de todo mundo | Um alvo a até 1,5 m |
| Explosão | Leve | Área | Esfera de raio 3 m, num ponto a até 18 m |
| Aura | Leve | Área | Esfera de raio 3 m, centrada em você |
| Cone | Leve | Área | Cone de 4,5 m, partindo de você |
| Linha | Leve | Área | Linha de 18 m por 1,5 m, partindo de você |
| Cura | Media | Amparo | Um aliado a até 9 m. O saldo vira dados de cura, até 2 × Classe em d8 |
| Apoio | nada | Amparo | Um aliado a até 9 m. Cada ponto do saldo concede 3 pontos de vida temporária |
| Onda | Pesada | Amparo | Aliados numa esfera de raio 3 m centrada em você. Escolha cura ou apoio ao montar |
| Efeito | nada | de todo mundo | Uma aplicação fora de combate. Usa a escala de Efeitos fora de combate, sem dano ou vida temporária |

### As 13 condições, por nível

> *Eram catorze até a v0.198 do sistema, quando a `Petrificado` saiu. No livro reconstruído, a `Incapacitado` virou `Guarda Aberta`.*

- **Leve** (6): Lento · Guarda Aberta · Derrubado · Agarrado · Desarmado · Surdo
- **Media** (2): Calado · Enfeitiçado
- **Pesada** (5): Impedido · Cego · Amedrontado · Envenenado · Atordoado

### As 18 Trilhas

- **Bastião**: Muro · Punho · Combatente Amaldiçoado
- **Vanguarda**: Estocada · Batedor · Executor
- **Guia**: Arquiteto · Analista · Socorrista
- **Emanador**: Condutor Armado · Ressonante · Catalisador
- **Evocador**: Invocação Principal · Parceria · Múltiplas Invocações
- **Incursor**: Assassino · Pugilista · Malabarista

### As nove rotas de criação

**Sete Origens, mais a sub-origem `Sem Técnica`. Mas nove rotas de criação**, porque `Restrição Celestial` se divide em duas e `Sem Técnica` abre a sua. Origem e rota não são a mesma contagem, e a ficha precisa das duas.

| rota | vai para | jogável hoje |
|---|---|---|
| Latente | Fundamento | sim |
| Receptáculo | Fundamento | sim |
| Descendente | Fundamento | sim |
| Encarnado | Fundamento | sim |
| Feto | Fundamento | sim |
| Restrição Celestial · corpo pela técnica | Fundamento | sim |
| qualquer uma + Sem Técnica | Aptidão ou Estilo da Sombra | **não**: Estilo da Sombra esta sendo escrito |
| Corpo Amaldiçoado | Técnica Marcial | **não**: Tecnica Marcial esta sendo escrita |
| Restrição Celestial · energia pelo corpo | Técnica Marcial | **não**: Tecnica Marcial esta sendo escrita |

Seis das nove rodam. As três que faltam dependem de Técnica Marcial e de Estilo da Sombra, que estão sendo escritas.

> Escolher `Restrição Celestial` **não fecha a escolha**: ainda falta dizer se é pelo corpo ou pela energia, e um dos dois ramos não roda. Um dropdown simples de Origem não dá conta disso.

### Os Legados

São **85 entradas**, divididas por Origem e por tipo. Cada personagem escolhe dois, ambos da lista da própria Origem, e pelo menos um narrativo. *Até o livro reconstruído os tipos eram Destranca, Ajusta e Desliga.*

| tipo | o que oferece |
|---|---|
| narrativo | Uma pessoa, informação, relação, acesso ou característica da sua história. |
| rolagem | Vantagem, repetição ou mudança específica de um teste. |
| exceção | Dispensa uma exigência ou impede um efeito nomeado, com uma contrapartida. |


---

## 6b · A tira de referência rápida

A ficha de papel imprime quatro linhas de consulta no rodapé da última página. Elas não são campo, mas a digital deve mostrá-las em algum lugar, porque são o que o jogador consulta no meio da mesa.

| linha | conteúdo |
|---|---|
| O turno | movimento 9 m + ação padrão + ação bônus + reação |
| Arredondamento | sempre para o lado que não te favorece |
| Crítico | 20 natural, e dobra os dados. **Só onde há rolagem de acerto** |
| Os dois descansos | curto devolve 25% do PE máximo; longo devolve tudo em ambiente propício, e metade fora dele |

> **⚠ A tira mudou na v0.239 do sistema, e são quatro linhas.** *A linha dos dois golpes saiu: o "golpe canalizado" que ela descrevia está morto desde a v0.81, e a peça 5 registra isso.* **A dos descansos dava os 25% "em ambiente propício"**, *e eles valem em qualquer lugar.* **O `conferir-ficha.py` do sistema confere a tira da ficha de papel contra as peças.**

**O crítico dobra menos coisa do que parece.** Dobra os dados da arma se for arma, e os dados da Classe se for feitiço. **Não dobra Força, não dobra dado que veio de Melhoria, e não dobra dano fixo.** Numa ficha digital que calcula dano, esse é um erro fácil de cometer e difícil de notar.

> **Uma divergência de nome, achada aqui.** A ficha chama o primeiro golpe de **`canalizado`**, e essa palavra **não aparece uma única vez no manual**. O manual chama a mesma coisa de **`feitiço de Toque`**, e usa `golpe simples` para o outro, esse sim igual nos dois. É a mesma classe de problema das Famílias, em escala menor: um nome que só existe de um lado. Decidir qual fica é escolha do dono do sistema.

---

## 7 · O caso de teste: a Kaori

A `ficha-exemplo-kaori.docx` é uma ficha de nível 2 conferida. Se a sua ficha digital reproduz os números dela, a base está certa.

**Entrada:** Bastião, nível 2, Força 3, Constituição 2, Destreza 2, Inteligência 1, Essência 1, TR Físico travado em Força, técnica em Força.

**Saída esperada:**

| campo | valor | de onde vem |
|---|---|---|
| Vida | 23 | `(12 + 2) + (7 + 2) × 1` |
| Energia | 8 | `4 × 2` |
| Integridade | 26 | `20 + (1 + 5) × 1` |
| Defesa | 13 | `10 + 2 + 1` |
| Iniciativa | d20 + 2 | Destreza |
| Deslocamento | 9 m | fixo |
| Maestria | 1 | nível 2 |
| CD de feitiço | 12 | `8 + 3 + 1` |
| Conjuração | d20 + 4 | Força + maestria |
| Corpo a corpo | d20 + 4 | Força + maestria |
| À distância | d20 + 3 | Destreza + maestria |

**Perícias treinadas (8):** Atletismo, Intuição, História, Hierarquia, Sobrevivência, Sentir Energia, Percepção, Intimidação.

Atletismo é uma das duas fixas do Bastião, e o quadro da Kaori no livro reconstruído traz `Atletismo treinado | d20 + 4`. *A outra fixa passou de Intimidação para Provocar no livro reconstruído; a .docx da Kaori é de 07/09 e ainda marca Intimidação, e o `conferir-kaori.py` lê o quadro do livro.*

**Famílias:** Livres `Controle` e `Castigo`. Fechadas `Área`, `Auxiliares` e `Amparo`.

> **Cuidado ao usar a Kaori como único teste.** As cinco Famílias que ela toca são exatamente as cinco que a ficha de papel e o manual têm em comum. Ela passa sem expor a divergência descrita na seção 9. Um segundo caso de teste que use `Mira` ou `Alcance` pega o que ela não pega.

**Os feitiços dela estão em branco de propósito.** A peça de criação não lista os três, e inventar aqui seria escolha de sabor, que é do dono do sistema.

### Um contra-teste, para o caso de teste não ser trivial

A mesma Kaori como Emanador daria Vida 14 e PE 12, não 23 e 8. Se os dois casos dão o mesmo número, a sua ficha está ignorando o Caminho.

---

## 8 · O que o repositório já tem

**Não se começa do zero.** Existe um gerador funcionando em `sistema/05-material/gerador-ficha/`:

| arquivo | o que faz |
|---|---|
| `dados.js` | os catálogos e as constantes do nível 2 |
| `helpers.js` | paleta (ameixa `741B47`, a mesma do manual), campo, bloco, tabela |
| `ficha.js` | as três páginas, uma função por página |
| `make.js` | a Kaori, e a montagem do documento |

Ele sai em `.docx`, três páginas exatas, e monta tanto a versão em branco quanto a preenchida a partir da mesma função. **A ficha em branco é a mais alta**, porque linha vazia ocupa altura.

O layout já resolvido é referência boa para a digital:

- página 1: identidade, atributos, os números, TRs, 23 perícias, ofícios
- página 2: Regra, descrição, Famílias, Selo, Expressão da técnica, os feitiços
- página 3: aparência, história, traço, Legado, laços, instituição, pacto, e uma tira de referência rápida

E existe um validador dono, o `conferir-ficha.py`, com seis checagens que comparam o `dados.js` contra as peças de regra. Ele não lê o `.docx` e não precisa de `python-docx`.

> **Se você mexer no layout, confira que ainda cabe em três páginas.** `soffice --headless --convert-to pdf` e depois `pdfinfo | grep Pages`. Tem que dar 3.

---

## 9 · Divergências e pendências

### A divergência que precisa ser consertada antes de digitalizar

**A ficha imprime uma lista de Famílias que o manual não tem.**

| fonte | as nove |
|---|---|
| `manual/gerador/partB.js` | Alcance · Área · Mira · Controle · Auxiliares · Castigo · Tempo · Marca · Amparo |
| `gerador-ficha/dados.js` | Ataque · Área · Controle · Castigo · Amparo · Corpo · Movimento · Auxiliares · Percepção |

Só cinco coincidem. A ficha tem `Ataque`, `Corpo`, `Movimento` e `Percepção`, que não existem no manual e não têm uma Melhoria sequer. E não imprime `Alcance`, `Mira`, `Tempo` e `Marca`, que juntas são **30 das 69 Melhorias**. *Eram 27 das 66 até a v0.258 do sistema, quando a `Concentrada`, a `Duradoura` e o `Alvo de Caça` entraram no catálogo; o `revisao-cetica.py` lê os dois números daqui.*

Confirmado em três lugares: no `dados.js`, na tabela 15 da `ficha-em-branco.docx`, e no gerador do manual.

**Por que passou:** o `conferir-ficha.py` tem seis checagens (perícias, ofícios, Caminhos, Trilhas, constantes do nível 2, e os arquivos existirem). Nenhuma delas confere Famílias. Cada outra cópia da ficha tem um dono declarado; a lista de Famílias é a única que não tem.

**O conserto** está em `repo-conserto/checagem-7-familias.py`, pronta para colar no `conferir-ficha.py`. Ela acende no estado atual do repositório e apaga numa cópia com o `dados.js` corrigido.

> Isso é a lição nº 9 do projeto acontecendo de novo, na mesma camada em que ela custou mais caro: *"a única cópia que sai do repositório e vai para a mão de um jogador foi a última a ser conferida."*

**Onde a lista deveria morar:** hoje ela só existe impressa, no gerador do manual, que é saída. Saída não devia ser autoridade de ninguém. A checagem lê de lá porque é o que existe; se uma peça de `03-mecanica` passar a declarar as nove, é só trocar a fonte.

### As outras duas divergências, já conhecidas

| assunto | a `.docx` diz | o manual diz | use |
|---|---|---|---|
| Ofícios | 10 | 11 | **o manual** |
| Legados por ficha | um só, na criação | **dois**: um Destranca obrigatório, mais um de qualquer formato | **o manual** |

### O que não tem regra fechada

Não invente nada para estes. Deixe o campo aberto ou marcado como pendente.

- **As três Trilhas do Evocador** (`Servo`, `Matilha`, `Coro`): as entregas de nível 2, 11, 19 e 27 estão sendo escritas. O Caminho funciona; a Trilha não.
- **O nível 27 da Trilha `Arremate`**: casa vaga de propósito.
- **Pactos**: a regra completa está sendo escrita. Hoje entra só com aprovação do mestre e o preço escrito na ficha.
- **Técnica Marcial** e **Estilo da Sombra**: três das nove rotas de Origem dependem delas.
- **`Casco`**, a segunda opção da `Sintonia` do Evocador: diz "mais vida" sem número.

### A regra 2, agora fechada

**Decisão do dono do sistema: `Queima` conta como repetição para o teto**, mesmo acontecendo no turno seguinte.

Com isso a regra 2 vira código, e a busca exaustiva mostra que ela precisa mesmo existir:

| Classe | orçamento | teto | pior montagem legal | dá |
|---|---|---|---|---|
| 1 | 3 | 4 | `Salto` + `Queima`, custo pago por duas Restrições Médias | **6** |
| 3 | 9 | 12 | idem | **18** |
| 5 | 15 | 20 | idem | **30** |
| 7 | 21 | 28 | idem | **42** |

O padrão é uniforme: `Salto` e `Queima` somam metade dos dados cada uma, então o total vira `2 × orçamento`, que é `6 × Classe` contra um teto de `4 × Classe`. **Sempre 50% acima**, em toda Classe.

E o mais importante para a ficha digital: **essa montagem passa nas outras sete regras de ouro.** Duas Melhorias (dentro do limite), duas Restrições (dentro do limite), nenhuma delas de frequência, devolução exatamente no teto de `2 × Classe`, nada vira dado de dano. Um mestre conferindo no olho aprova, porque tudo o que dá para olhar está certo.

> **É a única das oito regras que a montagem não denuncia sozinha.** Por isso ela é a que mais paga o custo de automatizar, e a razão mais forte para a ficha ser digital em vez de papel.

---

## 10 · Ordem de construção

Independente da plataforma, esta ordem evita retrabalho.

1. **Os números derivados.** Fórmula pura, nenhum catálogo. Uma ficha que só calcula Vida, PE, Defesa, CD e ataques já é útil na mesa.
2. **Perícias, ofícios e Testes de Resistência.** Listas fechadas, atributo fixo, pouca regra.
3. **A camada de escolha**: Origem, Caminho, Trilha, os dois Legados. Aqui entram os catálogos, e é onde a plataforma começa a doer.
4. **O Fundamento e a montagem de feitiço.** Por último, porque é a parte com aritmética e validação, e a que mais se beneficia de já ter o resto funcionando.
5. **A página de ficção.** Texto livre, sem regra.

### Escolher a plataforma

Cinco perguntas eliminam opções, e elas se respondem antes de escrever código:

1. A guilda joga por onde? Discord, VTT, presencial?
2. A ficha é **preenchida** pelo jogador, ou **gerada** a partir das escolhas dele?
3. Ela precisa **validar** (recusar ficha ilegal), ou só guardar o que foi digitado?
4. Precisa **sincronizar** entre mestres, já que o personagem atravessa mesas?
5. Precisa **imprimir** bonito, ou é só de tela?

| plataforma | a favor | contra |
|---|---|---|
| Planilha | fórmula é nativa; qualquer mestre edita; zero hospedagem | fica feia; validação de feitiço é limitada; catálogo grande vira aba difícil |
| HTML de arquivo único | roda offline; cabe num arquivo; visual sob controle; dá para embutir o catálogo | salvar exige exportar JSON; não sincroniza entre pessoas |
| Bot de Discord | o servidor é onde a guilda já vive; rolagem no canal da mesa | ficha em chat é ruim de ler inteira; precisa de banco e hospedagem |
| Foundry VTT | VTT de verdade: mapa, rolagem, automação | curva alta; exige licença; só serve quem já usa |
| Roll20 | popular, baixo atrito para o jogador | ficha custom é limitada e chata de manter |

> Se a resposta da pergunta 4 for sim, isso empurra forte para algo com estado compartilhado, e derruba o HTML solto.

---

## Os arquivos que acompanham esta especificação

| arquivo | o que é |
|---|---|
| `catalogo-projeto-m.json` | todos os catálogos em forma de dados |
| `conferir-catalogo.py` | integridade referencial e as contagens declaradas |
| `conferir-kaori.py` | regressão contra a ficha de exemplo |
| `conferir_feitico.py` | as regras de ouro aplicadas a um feitiço |
| `regressao-exemplos.py` | os feitiços publicados no manual |
| `arnes.py` | prova que cada checagem acende |
| `repo-conserto/checagem-7-familias.py` | o conserto da divergência da seção 9 |
