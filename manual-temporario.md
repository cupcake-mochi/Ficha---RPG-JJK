# Texto proposto para o manual · vida e energia temporárias

**Onde entra:** capítulo *Vida, energia e alma* (p.15), depois de `Integridade` e antes de `Arredondamento`.

**Por que entra:** hoje o capítulo tem as três reservas e não fala de temporário. A regra da energia temporária existe, mas mora dentro do `Braseiro`, nível 11 da Trilha Brasa — quem não joga Brasa nunca lê. A da vida temporária não existe em lugar nenhum, e seis coisas no manual concedem ela.

**Eu não mexi no repositório do manual.** Isto é para você colar.

---

## O texto

> ### Vida e energia temporárias
>
> Algumas coisas te dão vida ou energia **temporária**. Ela é um extra por cima da reserva, não um aumento dela: a sua vida máxima e o seu PE máximo não mudam.
>
> **As duas gastam primeiro.** O dano come a vida temporária antes de tocar a sua vida. O feitiço queima a energia temporária antes de tocar o seu PE.
>
> **As duas somem no fim da cena**, gastas ou não. Não passam para a cena seguinte, e descanso não devolve o que sumiu.
>
> **Vida temporária não empilha.** Se você já tem vida temporária e ganha mais, você fica com a maior das duas — nunca com a soma. Não importa de onde cada uma veio.
>
> **Energia temporária acumula até o teto que a fonte declarar.** Hoje só o `Braseiro` concede energia temporária, e o teto dele é 2.
>
> > **Exemplo.** Kaori tem 9 de vida temporária do `Vento a Favor`. Um aliado conjura `Muralha` nela, que dá 18. Ela fica com 18, não com 27 — a maior das duas, e os 9 somem.
> >
> > Ela toma 20 de dano. Os 18 temporários vão embora e os 2 que sobram descem na vida dela. Se o ataque tivesse a Melhoria `Rasga Escudo`, os 20 iriam direto na vida e os 18 continuariam lá.

---

## O que precisa mudar junto

**Uma linha no `Braseiro`.** Ele hoje carrega a regra inteira, e três quartos dela sobem para o capítulo. O que sobra é o teto:

> Nível 11: **Braseiro**. Quando o seu Classe 0 acerta, você ganha 2 de energia temporária, e ela nunca passa de 2 acumulados.

O resto — *"some no fim da cena"*, *"gasta como PE"*, *"gasta primeiro"* — passa a estar no capítulo e não precisa ser repetido aqui. Se ficar repetido, é um número morando em dois lugares, e um dia eles divergem.

---

## De onde cada frase saiu

Nada aqui foi inventado do zero. O que é decisão está marcado.

| frase | de onde |
|---|---|
| gasta antes da vida normal | **manual.** A Melhoria `Rasga Escudo` diz *"o dano ignora pontos de vida temporários e barreiras: bate direto na vida"* — só faz sentido se ela for gasta antes |
| gasta antes do PE normal | **manual.** `Braseiro`: *"Energia temporária gasta como PE, e gasta primeiro"* |
| some no fim da cena (energia) | **manual.** `Braseiro` |
| some no fim da cena (vida) | **decisão A2a.** Copia a forma da energia |
| não empilha, fica o maior (vida) | **decisão A2a.** Nenhum teto *numérico* serviria: as fontes vão de 2 a 18 |
| teto de metade da vida máxima (vida) | **livro, capítulo 10.** *"tem **teto de metade da sua vida máxima**"* — e o dono da conta é a peça 1 §5.1.1 do outro repositório |
| acumula até o teto da fonte (energia) | **manual.** *"nunca passa de 2 acumulados"* é do `Braseiro`, não do sistema |

> **⚠ A linha do teto entrou na v0.222, e ela estava faltando desde o começo.**
> *A tabela dizia "nenhum teto numérico serviria" e parava ali, o que se lia como
> "não há teto".* **Há, e ele é proporcional — que é justamente o formato que
> resolve o problema que a frase levanta:** *o teto numérico não serve porque as
> fontes vão de `2` a `18`; o teto de metade da vida máxima serve porque ele
> acompanha a ficha em vez de a fonte.*
>
> **E ele morde de verdade.** *A peça 1 §5.1.1 mede: o `Fluxo` nunca é cortado
> (entrega `2` a `14`), e o `Apoio` puro é cortado **sempre**, em toda Classe —
> um `Apoio` de Classe 1 entrega `9` num Emanador de nível 2 cujo teto é `7`.*
> **O teto vira o limite real do `Apoio`, e não a Classe do feitiço.**

### As seis fontes de vida temporária que o manual já tem

`Apoio` (Forma, 3 por ponto que sobra) · `Fluxo` (Legado 2, 2 × Classe) · `Aprumo` (Trilha nível 11, 1d10 + atributo de ataque) · `Crosta` (Arremate nível 19, a sua maior Classe) · `Vento a Favor` (feitiço da p.137, 9) · `Muralha` (feitiço da p.137, 18).

O exemplo do texto usa duas delas de propósito: são as duas maiores, e é nelas que "empilha ou não" muda mais o número.
