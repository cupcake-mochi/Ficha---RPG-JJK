# Pendências · o que precisa de decisão antes de construir

Cada item traz **o que está em aberto**, **por que importa**, as **opções com o preço de cada uma**, e **o que acontece se ninguém decidir**.

---

## As cinco que travavam a construção: decididas

**Estão fechadas, e o dono delas é o `DECISOES-bloco-A.md`.** Não repito os valores aqui — se o mesmo número mora em dois documentos, um dia os dois discordam, e isso já aconteceu neste projeto com as Famílias.

| | decisão |
|---|---|
| A1 · onde o catálogo mora | cópia local fixa, com uma célula puxando a versão corrente da central |
| A2 · vida temporária | não empilha, fica o maior · some no fim da cena · gasta primeiro |
| A2b · onde a regra mora | sobe para o capítulo de vida, energia e alma — vida **e** energia |
| A3 · `Rápido` + `Lento` | trava na ficha; o manual fica calado |
| A4 · vida e PE | atual editável **e** caixinha de delta, os dois |
| A5 · o acento colorido | cor de estado no número: osso → âmbar → vermelho |

O `conferir-decisoes.py` confere que esse documento, o `decisoes-ficha.json` e este arquivo continuam de acordo, e que tudo que a decisão atribui ao manual está mesmo lá.

**Entrega pendente do A2b:** o texto está escrito em `manual-temporario.md`, pronto para colar. Ele mexe no repositório do manual, então quem aplica é você.

---

## Dívida · dá para começar sem, mas ela volta

### B1 · O manual está fora da identidade visual — **FECHADO NA v0.200, e invertido**

O gerador do manual usava ameixa `741B47`; o servidor e o PDF usam `#211C35` e
`#756588`.

> **⚠ Conferido em 02/09/2026, no commit `ccec9d2`: a divergência morreu, e não
> foi para a paleta que este item supunha.** *A **v0.200** unificou as duas
> paletas do projeto numa terceira, a **`Neve Saturado`**, e ela entrou nos
> quatro geradores de uma vez — o do manual, o do livro, o da ficha de papel e o
> do bloco de inimigo.*
>
> **Ela é clara e rosada:** `ink 251727` · `crimson BC2A6E` · `rule F8C7DC` ·
> papel `FDF0F6`. *O `741B47` não aparece mais em gerador nenhum.*
>
> **Então o item inverteu:** o manual não estava fora e voltou para a paleta do
> servidor — ele foi para uma terceira, junto com o livro e a ficha de papel.
> **Quem está numa paleta própria hoje é a ficha digital**, escura
> (`FUNDO 120F1D` · `PAINEL 211C35` · `TEXTO F4F1F7`).
>
> *Papel claro e tela escura é diferença de mídia, e a decisão **C4** desta pasta
> escolheu a paleta do servidor de propósito. Mas isso deixou de ser "o manual
> está errado" e passou a ser uma pergunta de desenho: a ficha digital fica
> escura enquanto todo o material impresso é claro?* **Ela está em aberto, e é do
> Mizuki.**

### B2 · Falta um segundo caso de teste

A Kaori é nível 2, e ela já deixou passar **dois** defeitos:

- não expôs a divergência das Famílias, porque as cinco que ela usa são justamente as cinco que as duas listas têm em comum
- não pegaria o erro de maestria, que só aparece do nível 8 em diante

**Precisa de uma ficha de nível alto** (15 ou mais) como segundo caso, e de preferência com Famílias Livres que a Kaori não usa. Quem é esse personagem é escolha sua.

### B3 · Equipamento entra na ficha?

A ficha de papel não tem campo de equipamento, mas o capítulo 12 existe e **Traje e Revestimento desligam a proteção inicial**, que entra na Defesa.

Enquanto não entrar, a Defesa fica presa em `10 + Destreza + proteção da aptidão`, e qualquer personagem com equipamento terá a Defesa errada na ficha.

### B4 · A checagem 7 das Famílias precisa subir

Não é dúvida, é ação pendente. O `repo-conserto/checagem-7-familias.py` está
pronto, acende no estado atual e apaga numa cópia corrigida. Ele conserta um
erro que **hoje está na ficha em branco que os seus jogadores usam**.

Isso é independente da ficha digital e vale sozinho.

> **⚠ Ele não roda desta pasta, e isso é da natureza dele.** *É um **fragmento**
> para colar no `conferir-ficha.py` do outro repositório: ele chama `bloco()`,
> `ler()`, `erro()` e `lista_js()`, que são helpers de lá, e lê
> `../../manual/gerador/partB.js` e o `dados.js`, que não existem aqui.* **Rodar
> ele solto dá `NameError: bloco`** — o que é esperado, não defeito.
>
> *Ele também tem duas cópias idênticas nesta pasta, e isso é o **B15**.*

### B5 · `Lento` nomeia duas coisas diferentes

Achado ao fechar o A3.

| onde | o que `Lento` é |
|---|---|
| tabela de condições (p.32 e p.117) | condição de nível Leve: *"deslocamento pela metade, e sem Ação Bônus"* |
| tabela de Restrições (p.121) | Restrição Média: *"custa a rodada inteira"* |

As duas listas vão aparecer na ficha, e o jogador vai ver a mesma palavra em dois
menus significando coisas diferentes. Pior: as duas mexem em Ação Bônus, então a
confusão é plausível na mesa, não só na leitura.

É a armadilha de *"a mesma palavra carregando duas escalas"*, e ela já mordeu
este projeto antes com a palavra `Classe`.

**Não é decisão de agora, e o conserto é caro:** renomear qualquer uma das duas
mexe no manual publicado. Fica registrado.

> **⚠ Uma desambiguação na ficha foi escrita e DESFEITA em 02/09/2026.** *Ela
> punha `Lento (condição)` e `Lento (restrição)` nos dois menus, com a colisão
> derivada das duas listas.* **Foi revertida a pedido do Mizuki: aquela rodada
> era para a ficha da invocação, e mexer na ficha do personagem estava fora do
> escopo.** *O `ficha/dados.py`, o `ficha-projeto-m.xlsx`, o `apps-script/Ficha.gs`
> e o `conferir-ficha-xlsx.py` voltaram byte a byte ao que eram.*
>
> *Se um dia isso voltar à mesa, o desenho já foi medido: a colisão é
> `set(condicoes) & set(restricoes)`, e derivá-la faz um nome novo ganhar rótulo
> sozinho.*

### B6 · O desconto do `Rápido` + `Lento` continua disponível fora da ficha

Consequência escolhida do A3, não descuido.

A ficha recusa a montagem. O manual continua sem a frase, então **quem monta feitiço no papel, de cabeça, ou pelo gerador do manual continua com um terço do orçamento de desconto** — e com a Família Tempo Livre, com o `Rápido` de graça.

Se um dia quiser fechar, o molde da frase já existe no próprio `Rápido`: *"Não entra no mesmo feitiço que Reação."* O texto está pronto no `DECISOES-bloco-A.md`.

### B7 · Botão desenhado não funciona no celular

Achado ao fechar o A4.

O `botão de descanso longo` do documento de desenho não roda no app de celular do Sheets — botão desenhado é coisa de navegador. E o descanso é justamente uma das coisas que se aperta na mesa, pelo telefone.

**Já corrigido no desenho:** o substituto é caixa de seleção ou lista suspensa fazendo papel de botão, que o gatilho pega normalmente. Fica registrado porque a ideia de "botão" pode voltar.

### B8 · O `Estopim` soma um número que não existe

Achado escrevendo a fórmula da CD de feitiço.

O manual **desta pasta** é explícito na p.192: *"Não existe 'atributo de
conjuração' na ficha padrão."* A conta é `10 + 2 + maestria`, com o `2` fixo. E
ele diz que **algumas habilidades de Caminho trocam esse 2 por um atributo**, e
que a habilidade diz qual.

O problema: **nenhuma habilidade daquele manual faz essa troca.** A única coisa
que menciona atributo de conjuração é o `Estopim`, nível 11 do Emanador —
*"todo feitiço seu soma o seu atributo de conjuração no dano"* — e ele **usa** o
número sem que nada o tenha concedido.

**A ficha não inventa.** A CD e o ataque de conjuração usam o `2` fixo, e existe
uma célula de troca ao lado, vazia, para quando a regra existir.

> **⚠ Isto FECHOU no sistema na v0.117, e a ficha continua certa contra o
> manual dela.** *O `2` fixo morreu junto com o mecanismo, e a CD virou
> `8 + o atributo da sua técnica + maestria` — está no capítulo 10 do manual
> vivo, e em mais três lugares.* **O `manual.txt` daqui, congelado na v0.104,
> ainda escreve `CD de feitiço = 10 + 2 + maestria` na linha 536.**
>
> **Então este item não se conserta sozinho: ele é parte do B11.** Mudar a
> fórmula da ficha agora a põe à frente do manual que ela declara como fonte, e
> a regra deste repositório é a inversa — *onde a ficha e o manual discordarem,
> o manual vence.* **Conserta-se junto com a re-extração, nunca antes dela.**

### B9 · A ficha da invocação — **FECHADA**

Ela existe: `ficha-invocacao/ficha-invocacao.xlsx`, planilha separada, com o
`invocacao.json` como dono dos valores e três validadores em cima.

**Mas ela fechou contra um manual que não é o `manual.txt` daqui**, e isso é o
item B11 abaixo.

### B10 · A aba `TÉCNICA` saiu da ficha

O bloco de montagem de feitiço ficou ruim de ler e de usar: doze linhas de rótulo empilhadas, com um vão grande em cima, e nada calculado ainda. O Mizuki preferiu tirar a deixar torto.

**O que some junto:** a linha de uso rápido da `MESA` deixa de puxar dela e passa a ser digitada à mão.

**O que ela precisa ter quando voltar:** o bloco horizontal em vez de vertical, e os seis campos que o sistema calcula sozinho — ação, alcance, alvo, como resolve, custo em PE e dano. Isso está medido no `medidas/bloco-feitico.py` e descrito na seção 10 do `DESIGN-ficha-digital.md`.

Ela volta junto com a trava de montagem, que é o próximo pedaço caro.

### B11 · O `manual.txt` e o `catalogo-projeto-m.json` estão 96 versões atrás

O catálogo se declara **v0.104**, fonte *"Manual da Guilda (199 p.)"*, e o
`manual.txt` tem **16 capítulos**. O sistema está na **v0.200** e o manual vivo
tem **18**. No capítulo de Invocações a diferença não é de texto, é de mecânica:

| o que o `manual.txt` daqui diz | o que vale hoje | morreu em |
|---|---|---|
| a ficha da invocação é **derivada** da do dono | ficha própria, cinco atributos dela | v0.180 |
| vender número devolve orçamento (`−1 de acerto → 4 pontos`) | a venda não existe mais | v0.180 |
| `Servo` = `5 × h` | corpo forte, `2,5 × (base + 2 × nível) + Con × nível` | v0.178 |
| morre de vez pela metade da **vida máxima** | pela metade da **régua**, que é `5 ×` a vida crua do tipo | v0.178 |
| `Investir` sem número | tabela de sete faixas, `1d6` a `15d6` | v0.178 |
| `Casco`, *"mais vida"* sem número | `Parrudo`, `5 ×` a maestria | v0.184/v0.185 |

**Por isso a ficha da invocação não lê do `manual.txt`.** Ela lê de
`capitulo-16-invocacoes.md` e `capitulo-35-caminhos-e-trilhas.md`, cópias do
repositório do sistema, com o `conferir-invocacao.py` guardando a divergência:
se o `manual.txt` for re-extraído e a mecânica morta sumir dele, a checagem 9
muda de estado e cobra a decisão.

**Re-extrair o `manual.txt` é trabalho de verdade, e tem estilhaço:** o
`conferir-decisoes.py` cobra a string do `Casco`, o `conferir-catalogo.py` cobra
contagens contra páginas do PDF de 199 p., e o `revisao-cetica.py` lê dele. Não
dá para fazer de passagem.

### B12 · A checagem do C1 nunca acendia — **CONSERTADA**

O `conferir-decisoes.py` tinha esta linha, e ela existia para avisar quando o
Evocador podia voltar ao menu:

```python
checa("o motivo do C1 ainda vale: o manual segue sem o numero do Casco",
      "Casco — as suas invocações têm mais vida." in MAN, ...)
```

Ela lia o `manual.txt`, que está congelado. **A frase nunca sai de lá, então a
checagem saía verde para sempre e não tinha como mudar de estado.** Um guarda
que não pode acender não guarda nada.

**Hoje ela lê o dono vivo daquele número** — o `capitulo-35-caminhos-e-trilhas.md`
vendorizado — e cobra que a decisão C1 **declare** o estado de hoje dos três
motivos dela, em vez de continuar escrita como se ainda valessem. São sete
checagens, e o `arnes-decisoes.py` tem oito perturbações provando que cada uma
acende: cinco no lado do JSON e três no lado dos arquivos, inclusive o caso de
o `manual.txt` ser re-extraído.

**Os três motivos do C1 caíram:** entregas de Trilha na **v0.164**, o `Casco`
virando `Parrudo` com número na **v0.184/v0.185**, e a ficha da invocação no
**B9** desta rodada. A decisão de o Evocador voltar ao menu continua sendo do
Mizuki, e agora ela está declarada em vez de implícita.

### B13 · A `Voz` soma um número que não existe

Achado montando a ficha da invocação, e é a mesma forma do B8.

A `Voz` é uma das três rotas da `Sintonia` do Evocador (capítulo 35):
*"a CD dos efeitos das suas invocações sobe em `1`, e vira `metade da sua
maestria` a partir do nível 7"*.

**A invocação não tem fórmula de CD em documento nenhum** — nem no capítulo 16,
nem na peça 15. A rota soma `+1` num número que o sistema não produz.

**A ficha não inventa:** ela marca como pendente na seção 09 e manda combinar
com o mestre, e o `conferir-invocacao.py` tem uma checagem que acende no dia em
que o capítulo 16 ganhar uma CD.

### B14 · O Teste de Resistência treinado — **não é bug da ficha, é o B11**

Registrado errado na primeira passada desta rodada, e corrigido aqui.

O `catalogo-projeto-m.json` traz `bonus_se_treinado: 2`, e o `aba_ficha.py` usa
esse `2`. **A peça 1 §4 do sistema diz `TR = d20 + atributo do TR + maestria`**,
e o `+2` fixo morreu na **v0.117**.

**Mas a ficha está certa contra o manual dela.** O `manual.txt` desta pasta não
só usa o `+2` — ele nega a maestria com todas as letras, na linha 636:

> *"treino vale +2 fixo aqui, e não maestria. Maestria não entra em Teste de
> Resistência nunca."*

E o manual vivo, no capítulo 10, diz o contrário:

> *"Teste de Resistência = d20 + atributo do TR + maestria, e a maestria só
> entra se você for treinado nele."*

**Consertar a ficha antes de re-extrair o manual quebraria a regra deste
repositório**, que é *o manual vence*. Fica como parte do **B11**, junto com o
B8, que é o mesmo defeito no outro número.

*A ficha da invocação usa a maestria, e isso é de propósito: ela declara o
capítulo vivo como dono, e não o `manual.txt`. As duas fichas discordam entre si
até a re-extração, e isso está declarado nos dois lados.*

### B15 · Quatro arquivos tinham duas cópias — **RESOLVIDO**

Achado indo mexer no B4.

| arquivo | ficou em | a cópia da raiz |
|---|---|---|
| `checagem-7-familias.py` | `repo-conserto/` | apagada |
| `divergencia-familias.py` | `repo-conserto/` | apagada |
| `daltonismo.py` | `medidas/` | apagada |
| `paleta.py` | `medidas/` | apagada |

As quatro eram idênticas, nenhuma era importada por nada, e a documentação
estava dividida: o `PENDENCIAS` e o `LEIA-ME` apontavam para a subpasta, o
`ESPECIFICACAO` e os dois `HANDOFF` para o nome pelado da raiz. Um comentário do
`conferir-decisoes.py` cita `medidas/daltonismo.py`, o que já fazia da subpasta o
dono de fato.

> ***Decisão do Mizuki: apagar as da raiz.*** *As referências pelo nome pelado
> nos três documentos foram acertadas para o caminho da subpasta, e não sobrou
> nenhuma solta.*

Era a lição nº 9 na camada de arquivo: hoje eram iguais, e no dia em que alguém
editasse uma delas divergiriam em silêncio, sem validador que alcançasse.


---

## O que já foi decidido, e não deve ser reaberto

| | |
|---|---|
| plataforma | Google Sheets |
| automação | Apps Script, rodado uma vez por você na ficha-modelo |
| paleta | `#211C35` e `#756588`, com os papéis corrigidos por contraste |
| celular | aba `MESA` própria, de 12 colunas, lendo da `FICHA` por fórmula |
| progressão | automática do nível 2 ao 30; **o XP fica manual** |
| feitiços | linha de uso rápido na `MESA`, bloco completo na `TÉCNICA` |
| perícias treinadas | 8 ou 9, o jogador escolhe |
| `Queima` | conta como repetição no teto de dano |
| largura | desenhar para ~1300 px, que cabe em notebook |
| **o bloco A inteiro** | **`DECISOES-bloco-A.md`** |

---

## Isolamento · esta pasta não escreve no repositório do sistema

**Registrado em 02/09/2026, com uma conversa aberta em paralelo sobre o
Bestiário.** Se você chegou aqui de uma conversa nova, leia isto antes de mexer
em número.

**O que esta pasta faz:** ela **lê** o repositório do sistema e guarda cópias
declaradas do que precisa. Ela nunca edita nada lá. Os arquivos vendorizados
são estes, e cada um diz de onde veio:

| arquivo aqui | de onde veio, no `JJK---Project` |
|---|---|
| `manual.txt` | o PDF do Manual da Guilda, `pdftotext -layout` — **congelado na v0.104** |
| `capitulo-16-invocacoes.md` | `sistema/05-material/livro/manual/60-invocacoes.md` |
| `capitulo-35-caminhos-e-trilhas.md` | `sistema/05-material/livro/manual/35-caminhos-e-trilhas.md` |
| `repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx` | o repositório do PDF |

**A ficha da invocação foi construída assim de propósito:** planilha separada,
com o capítulo vendorizado como dono, e sem tocar em nenhum arquivo do sistema.
Ela não depende de nada que esteja em obra do outro lado.

### A re-extração do `manual.txt` (B11) — o bloqueio que eu escrevi já venceu

> **⚠ Escrito em 02/09/2026 mandando esperar a v0.201 fechar, e conferido no
> mesmo dia: ela fechou, e mais quatro depois dela.** *O sistema estava na v0.200
> quando eu escrevi, e está na **v0.205**.* **Um aviso que manda esperar uma
> coisa que já aconteceu é dívida, então ele foi reescrito em vez de mantido.**

O que eu tinha escrito: *não re-extraia, porque a v0.201 mexe na pressão do
chefe, que mexe no `72`, que é a base da régua de condição.* **Isso aconteceu, e
o efeito nesta pasta foi zero** — a régua trocou de pergunta e nenhum preço se
moveu, e o capítulo de dano e condições do livro não mudou uma linha.

**Medido contra o commit `ccec9d2` (v0.205):**

| o que mudou entre a v0.200 e a v0.205 | esta ficha lê? |
|---|---|
| `45-aptidoes-e-refino.md` — o `Kokusen` sai do catálogo de aptidões e entra a `Circulação` | **não.** O `catalogo-projeto-m.json` não tem chave de aptidões |
| o PDF do Manual da Guilda (repaginou) | **sim, indiretamente** — o `manual.txt` sai dele, e as páginas citadas podem ter andado |
| as peças 19, 23 e 26, e cinco validadores do sistema | **não.** Esta pasta não lê peça |
| o manual do Fundamento, v7.22 → v7.24 | **não diretamente** — o capítulo 9 do livro não mudou |
| a peça 15, cinco linhas | **não muda número nenhum da ficha da invocação** (veja abaixo) |

**Então o B11 não está mais bloqueado pelo motivo que eu dei.**

> **⚠ E o segundo motivo que eu dei também estava errado.** *Escrevi que a
> repaginação do livro moveria as contagens do `conferir-catalogo.py`.* **Ele
> não lê número de página:** *o `p.26` da saída é prosa na etiqueta, e a
> checagem compara `len(CAT[chave])` contra um número escrito no próprio
> código.* **Repaginar não quebra nada ali.** *Medido lendo o código, que é o
> que a lição do projeto manda fazer com número sobre ferramenta.*

O que o B11 é de verdade, medido: **re-extrair o `manual.txt` e acertar as
contagens do `catalogo-projeto-m.json`** contra o livro vivo. Quem lê o
`manual.txt` são o `conferir-decisoes.py` (que cobra frases literais), o
`revisao-cetica.py` e o `conferir-kaori.py` — e é nas **frases** que ele morde,
não nas páginas.

**O que muda no conteúdo, entre a v0.104 e a v0.205:** o `Kokusen` sai do
catálogo de aptidões e entra a `Circulação`; o TR treinado vira maestria; a CD
de feitiço vira `8 + atributo da técnica + maestria`; a `Base por Classe` separa
`Apoio` de `Cura e Onda`. Os dois últimos são o **B8** e o **B14**.

**A ordem continua sendo:** re-extrair o `manual.txt` e subir o
`catalogo-projeto-m.json` primeiro; **B8** e **B14** só depois disso.

### A ficha da invocação foi conferida contra a v0.205, e está inteira

Os dois capítulos vendorizados vieram **byte a byte idênticos** do commit
`ccec9d2`. Nenhum número que a planilha usa se moveu, e os três validadores dela
continuam verdes.

> **A peça 15 mudou cinco linhas na v0.201, e vale saber o que:** a coluna
> *"rodadas de chefe concentrando"* caiu para um terço — o corpo do `Coro` sai da
> luta em `0,6` rodada de chefe contra `1,7` de antes, e o corpo forte em `1,4`
> contra `4,2`. **Nenhum corpo perdeu vida:** o que triplicou foi o dano de rodada
> do chefe, na tabela de inimigo. A razão de `2,5 ×` entre os dois corpos não se
> moveu, e é ela que sustenta o argumento do `Servo`.
>
> *Isso é fato de mesa, não conserto de ficha: uma invocação hoje aguenta bem
> menos foco de chefe do que aguentava. É item de playtest.*

### O que é seguro mexer sem esperar nada

- a ficha da invocação e os três validadores dela — eles leem os capítulos
  vendorizados, não o `manual.txt`
- o **B12**, que já foi consertado nesta rodada
- o **B4**, que é do repositório do PDF e não toca no sistema
- o **B15**, que é arrumação de arquivo desta pasta
- o **B7** e o **B10**, que são desenho da ficha

