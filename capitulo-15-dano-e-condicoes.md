# Dano, Condições e Cobertura

## Tipos de dano

Todo dano deste sistema tem um tipo, e os catorze tipos se dividem em três grupos. O grupo importa porque várias habilidades resistem a um grupo inteiro em vez de a um tipo só.

> | grupo | tipos |
> |---|---|
> | **Físicos** | `Cortante` · `Perfurante` · `Concussão` |
> | **Elementais** | `Fogo` · `Frio` · `Elétrico` · `Ácido` · `Trovejante` · `Veneno` |
> | **Especiais** | `Radiante` · `Necrótico` · `Psíquico` · `Energia Reversa` · `Alma` |

A lista é fechada. Quando uma arma, um feitiço ou uma habilidade disser de que tipo é o dano, ou a que tipo ela resiste, o nome sai daqui.

### Catálogo

O número do dano vem da arma ou do feitiço. O tipo diz quem resiste a ele e como a mesa descreve o golpe.

#### Físicos

**`Cortante`** — causado por lâminas, fios e superfícies afiadas. Rasga tecidos e carne, deixando ferimentos abertos e sangramento visível.

**`Perfurante`** — causado por pontas, agulhas e projéteis. Concentra toda a força em um único ponto, perfurando defesas para atingir órgãos e estruturas internas.

**`Concussão`** — causado por socos, impactos com objetos pesados e quedas. Transmite força bruta para fraturar ossos, desorientar e mover o alvo do lugar.

#### Elementais

**`Fogo`** — causado por chamas e calor extremo. Incendeia alvos, consome o ambiente e continua queimando após o impacto.

**`Frio`** — causado por temperaturas congelantes. Drena o calor do corpo, travando articulações e enrijecendo os músculos.

**`Elétrico`** — causado por descargas e correntes elétricas. Percorre o organismo provocando espasmos violentos e eletrificando condutores.

**`Ácido`** — causado por compostos químicos corrosivos. Corrói a matéria continuamente, degradando equipamentos e pele ao mesmo tempo.

**`Trovejante`** — causado por ondas de choque sonoras e deslocamento de ar. Empurra estruturas, estoura tímpanos e estilhaça o ambiente.

**`Veneno`** — causado por toxinas e substâncias nocivas. Age de forma insidiosa dentro do organismo, enfraquecendo a vítima antes da queda.

#### Especiais

**`Radiante`** — causado por luz abrasadora ou julgamento espiritual. Queima o alvo de dentro para fora, e pode cegar antes de causar o dano físico.

**`Necrótico`** — causado por forças de decomposição e podridão. Atrofia a carne viva, escurece a pele e dificulta a regeneração dos ferimentos.

**`Psíquico`** — causado por trauma mental puro e colapso da consciência. Bate diretamente na mente, causando dor agonizante sem deixar marcas externas no corpo.

**`Energia Reversa`** — causado pela inversão da energia em maldições. Desmonta a biologia da maldição, desestruturando tecidos.

**`Alma`** — causado por ataques diretos à essência espiritual. Ele gasta Integridade em vez de vida, e tem quatro estágios próprios. Os quatro estágios estão na tabela `Estágios de dano na alma`.

### Nomes repetidos

Seis desses nomes você já viu em outro lugar, e ali eles querem dizer outra coisa.

**Nomes repetidos**
{: .tab-titulo }

| onde o nome aparece | o que ele é ali |
|---|---|
| `Fogo`, `Ácido`, `Veneno` como **Tema** do Fundamento | rótulo de sabor pendurado numa técnica, sem efeito próprio |
| `Cortante`, `Trovejante`, `Alma` dentro de `Passo Cortante`, `Palma Trovejante`, `Toca a Alma` | pedaço do nome de um feitiço pronto |
| os catorze desta seção | o tipo do dano na hora que ele cai |

Um não puxa o outro. Um feitiço com o Tema `Fogo` só causa dano do tipo `Fogo` se o texto dele disser isso.

> **Exemplo.** A Mei tem uma habilidade que dá resistência a `Fogo`. O inimigo acerta ela com `Palma Trovejante`, que causa dano `Trovejante`. Os dois são Elementais, e isso não basta: a resistência dela nomeia um tipo, e `Trovejante` não é `Fogo`. Ela toma o dano inteiro.

### Dano na alma

**Integridade é a vida da alma**, e a fórmula dela é `20 + (Essência + 5) × (nível − 1)`, do capítulo 1, *Como Jogar*. Por exemplo, 6 de dano na alma tiram 6 de vida e 6 de Integridade.

> **Cada ponto de dano na alma tira 1 de vida e 1 de Integridade.**
>
> Caso você chegue a `0` de vida antes da sua Integridade, você fica `Inconsciente`.
>
> **Dano na alma entra cheio**, sem redução pela metade.
>
> Ao receber, faça um **Teste de Resistência de Espírito** contra a CD do atacante. Numa falha, você também avança um estágio na hora, mesmo que a fração ainda não tenha fechado.
>
> Esse teste só pode ser feito uma vez por rodada.

**Estágios de dano na alma**
{: .tab-titulo }

| Integridade perdida | Estágio | O que pega |
|---|---|---|
| 1/4 | **1** | Desvantagem em testes de perícia. |
| 1/2 | **2** | Deslocamento pela metade, e todo feitiço custa +1 PE por Classe. |
| 3/4 | **3** | Desvantagem em ataques e Testes de Resistência. Você não conjura acima de metade da sua Classe máxima. |
| Toda | **4** | Você não é mais você. O que sobra é decisão do mestre. |

**Cura comum não devolve o que a alma perdeu.** Só descanso longo, ou a Melhoria `Remenda`, no capítulo 9, *Fundamento*. O descanso longo devolve toda a Integridade e limpa os estágios.

**Nenhum feitiço passa de 2 × Classe em dados na alma.**

#### Dano direto na alma

Existe um dano na alma que não leva o corpo junto: ele tira Integridade e **só** Integridade.

> **Dano na alma que atravessa não tira vida.** Ele desconta da Integridade, e os estágios valem igual.

Isso não é o padrão — é exceção, e ela precisa estar escrita no efeito. **Hoje existe uma:** o `Cisão`, no capítulo 15, *Ferramenta Amaldiçoada*.

## Condições

**Condição** é um estado nomeado que muda o que você consegue fazer enquanto durar. São treze, e cada uma tem um **nível**: `Leve`, `Média` ou `Pesada`.

> **O nível faz duas coisas, e são as duas contas que a condição pede.**
> É o que ela **custa para comprar** dentro de um feitiço.
> É o que ela **custa para tirar** de alguém, em pontos de energia.

### Como ler

Cada condição abre dizendo **quando** ela vale. Depois vem um parágrafo por efeito, e cada
efeito tem nome próprio: `Deslocamento`, `Seus ataques`, `Contra você`, `Ação`, `Testes` e
`Sai quando`. Os mesmos seis nomes aparecem em todas as treze, então quem aprende um
reconhece nas outras.

No fim do capítulo, a tabela `Condições em uma linha` traz as treze resumidas, para
consulta na mesa.

### Nível `Leve`

#### `Lento`

Enquanto está `Lento`, você sofre os seguintes efeitos.

**Deslocamento.** Cai pela metade.

**Ação.** Você não pode usar Ação Bônus.

#### `Incapacitado`

Enquanto está `Incapacitado`, você sofre os seguintes efeitos.

**Ação.** Você não pode `Bloquear`.

**Contra você.** Todo ataque corpo a corpo **que acertar** é crítico.

**Só o corpo a corpo.** *Ataque de conjuração e ataque à distância não críticam por causa desta condição — e o feitiço de Toque é conjuração, mesmo saindo encostado em você.* O crítico dobra o dado da arma e mais nada; o capítulo 1, `Crítico`, é quem diz o que entra.

#### `Derrubado`

Você está no chão. Enquanto está `Derrubado`, você sofre os seguintes efeitos.

**Deslocamento.** Só se move rastejando, com metade do deslocamento. Levantar custa a sua Ação de Movimento, quando não for efeito de duração.

**Seus ataques.** Desvantagem.

**Contra você.** Vantagem a até **1,5 m**, desvantagem de mais longe.

#### `Agarrado`

Enquanto está `Agarrado`, você sofre os seguintes efeitos.

**Deslocamento.** É `0`.

**Ataque à distância.** Quem atira contra alguém que está agarrando outra pessoa tem 50% de chance de errar o alvo pretendido: role `1d10`, e em 6 ou mais você acerta o alvo desejado; em 5 ou menos, acerta quem está agarrando.

**Sai quando.** Quem agarrou ficar `Incapacitado`, ou alguma coisa tirar você do alcance dele.

#### `Desarmado`

A sua arma está no chão ou na mão de outro. Enquanto está `Desarmado`, você sofre o seguinte
efeito.

**Seus ataques.** Você bate desarmado até pegar a arma de volta.

#### `Surdo`

Você não ouve. Enquanto está `Surdo`, você sofre os seguintes efeitos.

**Testes.** Falha automática no que precise de audição.

**Iniciativa.** `−2`.

### Nível `Média`

#### `Calado`

Enquanto está `Calado`, você sofre o seguinte efeito.

**Conjuração.** Você não conjura. Nada que precise de voz, gesto ou Selo que exija falar sai.

#### `Enfeitiçado`

Enquanto está `Enfeitiçado`, você sofre os seguintes efeitos.

**Seus ataques.** Você não ataca quem enfeitiçou, nem mira efeito nocivo nele.

**Contra você.** Ele tem vantagem em teste social contra você.

**Sai quando.** O alvo enfeitiçado recebe um ataque ou um efeito ofensivo.

### Nível `Pesada`

> **Só as de nível `Pesada` dão Teste de Resistência no fim de cada turno do alvo.**
> **E só cabe uma delas por feitiço.**

#### `Impedido`

Enquanto está `Impedido`, você sofre os seguintes efeitos.

**Deslocamento.** É `0`.

**Seus ataques.** Desvantagem.

**Testes.** Desvantagem no Teste de Resistência Físico.

**Contra você.** Vantagem.

#### `Cego`

Você não enxerga. Enquanto está `Cego`, você sofre os seguintes efeitos.

**Testes.** Falha automática no que precise de vista.

**Seus ataques.** Desvantagem.

**Contra você.** Vantagem.

#### `Amedrontado`

Enquanto está `Amedrontado`, você sofre os seguintes efeitos.

**Seus ataques.** Desvantagem, enquanto você enxergar a fonte do medo.

**Testes.** Desvantagem, enquanto você enxergar a fonte do medo.

**Deslocamento.** Você não se aproxima da fonte do medo por vontade própria.

#### `Envenenado`

Enquanto está `Envenenado`, você sofre os seguintes efeitos.

**Seus ataques.** Desvantagem.

**Testes.** Desvantagem em todo teste de perícia.

#### `Atordoado`

Enquanto está `Atordoado`, você sofre os seguintes efeitos.

**Ação.** Você perde a Ação Padrão e não usa reação. Quem tem mais de uma Ação Padrão no
turno — um chefe, um capanga grande — perde **uma** das suas ações, e não todas.

> **Exemplo.** A Rina fica `Atordoada`. Ela perde a Ação Padrão daquele turno e não usa reação, então ninguém leva ataque de oportunidade dela. A Defesa continua a mesma: `Atordoado` não abre a guarda de ninguém. No fim do turno dela, como é uma condição `Pesada`, ela faz o Teste de Resistência e pode sair sozinha.

### Condições em uma linha

Para consulta na mesa. O efeito inteiro de cada uma está na entrada dela.

**Condições em uma linha**
{: .tab-titulo }

| condição | nível | o que faz |
|---|---|---|
| `Lento` | `Leve` | deslocamento pela metade, sem Ação Bônus |
| `Incapacitado` | `Leve` | não `Bloqueia`, e todo ataque corpo a corpo que acertar é crítico — só ele |
| `Derrubado` | `Leve` | rasteja; desvantagem nos seus ataques; vantagem a quem ataca de perto |
| `Agarrado` | `Leve` | deslocamento `0` |
| `Desarmado` | `Leve` | bate desarmado até pegar a arma de volta |
| `Surdo` | `Leve` | falha no que precise de audição, `−2` na iniciativa |
| `Calado` | `Média` | não conjura |
| `Enfeitiçado` | `Média` | não ataca quem enfeitiçou; ele tem vantagem social contra você |
| `Impedido` | `Pesada` | deslocamento `0`, desvantagem nos ataques e no Físico |
| `Cego` | `Pesada` | falha no que precise de vista, desvantagem nos ataques |
| `Amedrontado` | `Pesada` | desvantagem enquanto vir a fonte, e não se aproxima dela |
| `Envenenado` | `Pesada` | desvantagem nos ataques e em todo teste de perícia |
| `Atordoado` | `Pesada` | perde a Ação Padrão e a reação |

### `Inconsciente`, `Exaustão` e `Invisível`

Estas três não são condição.

**`Inconsciente`, `Exaustão` e `Invisível`**
{: .tab-titulo }

| não é condição | onde ela está |
|---|---|
| `Inconsciente` | é cair a 0 de vida, com regra própria no capítulo 1, *Como Jogar* |
| `Exaustão` | é relógio de descanso, e mora no capítulo 5, *Descanso e Recuperação* |
| `Invisível` | é benefício, e as condições são compradas para aplicar num alvo |

### Comprar uma condição

> **Existe uma Melhoria `Condição`, e o preço dela é o nível da condição que você escolheu.**
> Escolher `Derrubado` custa `Leve`. Escolher `Atordoado` custa `Pesada`.

Você aponta a condição na tabela `Condições em uma linha`, lê o nível dela, e esse é o preço. Não existe pacote nem grupo de compra.

> **Exemplo.** O Kaito está montando um feitiço de Classe 2 que derruba quem for acertado. Ele compra a Melhoria `Condição` e escolhe `Derrubado`, que é `Leve`. Numa Classe 2 isso custa `1` ponto, e ele fica com o resto do orçamento em dados de dano. Se ele quisesse `Impedido`, que é `Pesada`, o mesmo feitiço pagaria `3` e sairia bem menor.

### Tirar uma condição

> **Tirar uma condição de alguém custa `1` ponto de energia por nível: `1` para `Leve`, `2` para `Média`, `3` para `Pesada`.**

Você só faz isso se tiver uma habilidade que tire condição, e cada habilidade dessas tem um teto de quanta energia ela gasta por uso. O teto é que decide o que você alcança: com teto `2` você limpa `Leve` e `Média`, e a `Pesada` fica fora até o teto subir.

> **Exemplo.** A Mei tem uma habilidade de tirar **uma** condição com teto de `2` pontos de energia por uso. O aliado dela está `Calado`, que é `Média`: ela gasta `2` e limpa. No turno seguinte o mesmo aliado fica `Cego`, que é `Pesada`: ela precisaria de `3`, e não consegue até a habilidade dela crescer.

## Cobertura

Cobertura é o que está entre você e quem está atirando. São três degraus, e você lê o que enxerga do alvo para saber em qual deles ele está. A pergunta que o mestre faz é sempre a mesma: daqui, quanto do corpo dele dá para acertar?

**Degraus de cobertura**
{: .tab-titulo }

| cobertura | o que ela dá | exemplo |
|---|---|---|
| **Parcial** (`1/4`) | **`+2` de Defesa e `+2` no Teste de Resistência Físico** | mureta, tronco, uma criatura no caminho |
| **Boa** (`1/2`) | **`+5` de Defesa e `+5` no Teste de Resistência Físico** | seteira, olhando por cima de uma parede, metade do corpo atrás de um canto |
| **Total** | **você não pode ser escolhido como alvo** | parede inteira, do outro lado da porta |

> **Vale contra o que vem do outro lado da cobertura, e só.** Quem está atrás de uma mureta não ganha nada contra quem já está do outro lado dela.
>
> **Só a maior conta.** Duas coberturas parciais não viram uma boa.

A **Total** tira você da lista de alvos possíveis, e não dá número nenhum. Um efeito que pega área continua alcançando quem está atrás dela, se o efeito não precisar de linha até o alvo.

> **Exemplo.** O Sousuke está agachado atrás do capô de um carro, com meio corpo de fora. Isso é cobertura **Boa**: a Defesa dele sobe `5` contra quem atira do outro lado do estacionamento. Ele decide se jogar inteiro para trás do carro e passa a ter cobertura **Total**, então ninguém do outro lado consegue escolher ele como alvo. Mas um feitiço de área que estoura embaixo do carro não precisa de linha até ele, e alcança do mesmo jeito. Como a **Total** não dá número, o Teste de Resistência Físico dele sai limpo, sem os `5` que ele tinha um segundo antes.
