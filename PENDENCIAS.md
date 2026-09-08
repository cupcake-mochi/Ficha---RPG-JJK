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

### B16 · A caixinha de ± ignorava a vida temporária — **CONSERTADO**

A **A2** decidiu que a temporária *gasta primeiro*, e o `decisoes-ficha.json`
carrega isso escrito nos dois campos: `gasta_antes_da_vida_normal` e
`gasta_antes_do_pe_normal`. A **A4** construiu a caixinha de ±. **As duas nunca
foram ligadas.**

O `aplicarDelta_` do `apps-script/Codigo.gs` lia três células do índice —
`vida`, `vida_max` e `vida_delta` — e nunca a quarta, `vida_temp`, que o índice
publica desde sempre. Resultado na mesa: o dano descia direto na reserva e o
campo TEMP ficava parado na tela, valendo nada.

**O que mudou:** a conta saiu para um `aplicaPasso_` puro, sem planilha em
volta, e o passo negativo come a temporária antes de tocar a reserva. O campo
TEMP desce junto. Ganho não devolve temporária — ela é extra por cima, e quem
concede é a fonte.

**Como isso é conferido:** o `regressao-delta.js` roda o `aplicaPasso_` no node
contra o exemplo publicado no `manual-temporario.md` (18 temporários, 20 de
dano, dois descem na vida) e contra os dois campos da A2, e o `arnes-delta.py`
perturba os três arquivos. Nenhum número esperado está escrito no teste.

> **`Rasga Escudo` não passa pela caixinha.** A Melhoria ignora a temporária, e
> o script não tem como saber que o dano é dela. Quem toma esse dano edita a
> reserva na mão — a A4 mantém o atual editável exatamente para casos assim, e a
> nota que aparece ao passar o mouse no campo TEMP diz isso.

**Conferido na planilha viva, 05/09/2026.** O Mizuki colou o `Codigo.gs` no
editor de Apps Script da ficha e rodou o `testeDelta`: as cinco passaram. O
`testeDelta` mora no próprio `Codigo.gs` porque o `onEdit` é gatilho simples e
não se executa à mão — chamado pelo seletor de função ele quebra, já que o `e`
vem vazio.

### B17 · O campo TEMP da INTEGRIDADE não tem fonte no manual

A ficha tem `integridade_temp` no índice e o campo na tela, mas **nada no
sistema concede integridade temporária**. Procurei o termo no `manual.txt`, no
`catalogo-projeto-m.json` e nas decisões: são seis fontes de vida temporária
(`Apoio`, `Fluxo`, `Aprumo`, `Crosta`, `Vento a Favor`, `Muralha`) e uma de
energia (`Braseiro`, teto 2). De integridade, zero.

**O campo não faz mal** — vazio, o `aplicaPasso_` passa por ele sem efeito, e a
nota do campo agora diz que regra nenhuma o concede. **Mas ele é uma pergunta em
aberto:** ou algo deveria conceder, ou o campo sai da linha da Integridade.

*Decisão tua. Não é dívida técnica: é desenho de sistema.*

### B18 · O `Ficha.gs` está atrás da planilha viva, e o `construir()` apaga tudo

O `apps-script/Ficha.gs` é o transporte do gerador: o `construir()` **apaga
todas as abas e monta do zero**. Comparando o que ele emite com a ficha que
está em uso hoje, ele está atrás em pelo menos quatro pontos:

| | o `Ficha.gs` monta | a ficha viva tem |
|---|---|---|
| abas | 5 (CARTEIRA, FICHA, MESA, QUEM É, DADOS) | 6 — com INVOCAÇÃO, CATÁLOGO e DADOS_INV |
| `J31` · integridade máxima | `=20+8*($AH$11-1)` | `=20+(AJ17+5)*($AH$11-1)` |
| lista de Caminhos | para no `Emanador` | tem o `Evocador` |
| linhas da FICHA | 94 | 135 |

**Rodar o `construir()` hoje devolveria uma ficha antiga e levaria as abas de
invocação junto.** Ele só volta a ser seguro depois que o gerador Python
emitir o estado atual — e aí o `emitir_gs.py` regera o `Ficha.gs`.

*Não é dívida de código: é uma arma carregada no editor. Fica registrado para
ninguém apertar o gatilho por engano.*

#### ⚠ O diagnóstico mudou, e ele desmonta duas das quatro linhas

**Decisão do Mizuki na v0.220 do outro repositório: *"B18 precisa ser corrigido"*.
Indo aplicar, as quatro linhas da tabela acima não são quatro problemas do mesmo
tipo — são um conserto, uma decisão dele, e duas consequências.**

| linha | o que ela é de verdade |
|---|---|
| `J31` · integridade máxima | **CONSERTO, e foi feito** — ver abaixo |
| lista de Caminhos | **não é atraso: é a decisão `C1`**, que tirou o Evocador do menu de propósito. O `decisoes-ficha.json` já diz que os três motivos dela expiraram e que **voltar é decisão do Mizuki**. O gerador está obedecendo uma decisão, não ficando para trás |
| abas 5 × 6 | as três que faltam — `INVOCAÇÃO`, `CATÁLOGO`, `DADOS_INV` — vêm do `ficha-invocacao/`, que é **outro gerador, com o `invocacao.json` de dono**. Juntar os dois num caderno só é desenho, e não conserto |
| linhas da FICHA · 94 × 135 | consequência das duas de cima, e não causa própria |

**Feito na v0.221 — a fórmula da Integridade:**

*O `aba_ficha.py` escrevia `=20+8*(NIV-1)`, que é a Integridade PLANA.* **Ela
deixou de ser plana na v0.145 do sistema**, pela decisão da v0.70: ela escala com
Essência, e a fórmula de hoje é `20 + (Essência + 5) × (nível − 1)` — que é
exatamente o `=20+(AJ17+5)*($AH$11-1)` da planilha viva. **O gerador é que estava
atrás, e agora ele emite a de hoje.**

> **E o `8` também morava dentro do `conferir-kaori.py`**, escrito na mão. *Número
de regra dentro de validador envelhece calado.* **O capítulo 15 do livro foi
vendorizado aqui como `capitulo-15-dano-e-condicoes.md`**, no mesmo molde dos
capítulos 16 e 35, e o validador lê a fórmula de lá.

**⚠ E isso deixou o `conferir-kaori.py` VERMELHO, de propósito, num ponto só:**

*A regra pede `26` para a Kaori — nível 2, Essência 1 — e a ficha de exemplo
vendorizada em `repos/JJK---PDF---RPG-main/ficha/` imprime `28`.* **Ela é de antes
da v0.145.** *Os outros dez campos batem.*

> **O conserto é re-vendorizar aquela ficha, e ele NÃO foi feito aqui porque a
> pasta é cópia de outro repositório.** *A do `JJK---Project` já imprime `26` — mas
> ela é outro documento (29 parágrafos e 40 tabelas contra 28 e 38), e trocar uma
> pela outra dentro de uma pasta rotulada como cópia de um terceiro repositório é
> decisão de quem cuida daquela vendorização.*

#### ⚠⚠ E indo regerar a planilha apareceu um SEGUNDO gatilho carregado

**Rodar o `monta.py` hoje produz uma planilha que o `conferir-ficha-xlsx.py`
REPROVA**, e não por causa do conserto acima: *`[FALHA] nenhuma cor de texto fora
da paleta <- {'3D2E78': 6}`*.

*Isolado: a falha aparece rodando o `monta.py` a partir do fonte **sem nenhuma
mudança minha**, então ela é anterior a esta leva.* **As seis células são os
números de seção da FICHA — `01` a `06` —, e o `3D2E78` é o `PAINEL_ALTO` do
`estilo.py`, que é cor de FUNDO sendo usada como cor de TEXTO.**

> **O `ficha-projeto-m.xlsx` commitado PASSA na checagem, e o regerado não.** *Ou
o artefato foi salvo antes de o `secao()` passar a usar o `PAINEL_ALTO`, ou ele
foi mexido à mão depois.* **De um jeito ou de outro, o artefato commitado e o
gerador que deveria produzi-lo não estão dizendo a mesma coisa.**

**Por isso a v0.221 mexeu só no FONTE.** *O `ficha/ficha-projeto-m.xlsx` e o
`apps-script/Ficha.gs` ficaram como estavam:* **regerar hoje trocaria um artefato
verde por um vermelho, por um motivo que não tem nada a ver com o `B18`.**
*Consertar a cor — ou soltar o `PAINEL_ALTO` na paleta de texto — vem antes de
regerar, e é decisão tua.*

#### Feito depois — o gerador alcançou perícias, ofícios e feitiços, e o segundo gatilho foi desarmado

**A `conferir-ficha-xlsx.py` estava certa em reprovar, e errada no motivo.** *O
`PAINEL_ALTO` como cor de texto não é acidente: é o `secao()` do `estilo.py`
fazendo exatamente o que o próprio docstring dele diz — "o número da seção entra
grande e apagado: ornamento que também orienta".* **A checagem nunca soube disso.**
Ela ganhou o `3D2E78` na paleta permitida, com o motivo escrito ao lado — e um
contra-teste provou que ela continua pegando cor de verdade fora do padrão
(injetei um magenta aleatório numa célula e a checagem acendeu igual).

**E o `aba_ficha.py` fechou boa parte da distância que faltava — não pela
comparação de linhas, que era consequência e não causa, mas em CONTEÚDO:**

- **Ofícios ganharam fórmula.** Até aqui o gerador só escrevia o nome — sem
  atributo, sem bônus, sem nada. Agora cada um lê o `atributo_padrao` do
  catálogo (novo campo, ao lado de `descricao`) e soma maestria do mesmo jeito
  que perícia já somava.
  > **⚠⚠ E o atributo padrão de 8 dos 11 ofícios estava ERRADO onde ele já
  > existia — na planilha viva, não aqui.** *Ela tinha os onze fixos em
  > `INTELIGÊNCIA`, e só três (`Herbalismo`, `Burocracia`, `Culinária`) estavam
  > certos por coincidência.* `Condução`, `Arrombamento`, `Caligrafia`,
  > `Entalhador` e `Alfaiate` são **Destreza**; `Forja` é **Força**; `Jogatina`
  > e `Instrumento` são **Essência** — a peça 7 §6 do `JJK---Project` é a fonte
  > ("atributo padrão | a vizinha que decide"). **O catálogo, o gerador e a
  > planilha viva foram corrigidos juntos**, e o Mizuki recebeu um Apps Script
  > (`planilha-viva/corrigir-oficios.gs`) pra rodar na conta real dele.
  > *E o livro (capítulo 12) diz que ofício "resolve com o que a situação
  > pedir" — não é trava como perícia, é sugestão de partida. O campo chama-se
  > `atributo_padrao`, não `atributo`, por isso.*
- **Especialização entrou, em perícias e ofícios.** Peça 11 §3: do nível 10 em
  diante, especializar soma metade da maestria por cima de quem já treina. A
  ficha ganhou um segundo checkbox (`Espec`, ao lado do `Trein` que já
  existia) com a fórmula certa. *Decisão do Mizuki: não trava nível nem exige
  o `Trein` marcado — fica na escolha do jogador, com a tabela de marco como
  referência, do mesmo jeito que o resto da ficha não conta nada contra o
  orçamento da criação.*
- **`Bloquear` entrou** — `2d10 + (Defesa − 11)`, peça 23. A planilha viva já
  tinha; o gerador não.
- **Aptidões e Feitiços nasceu do zero.** Classe 0 (5 linhas, o teto no nível
  30), feitiços conhecidos (24 linhas, o mesmo teto), Pontos/PE derivados da
  Classe (`3 × Classe`, peça 19), Passiva Livre, e um contador que conta SLOT
  preenchido — não ponto gasto, o mesmo erro que a planilha viva já tinha
  corrigido em paralelo e que a v0.221 não sabia.

**Tudo isso foi provado com o LibreOffice recalculando de verdade** — não só
"não deu erro": uma Kaori hipotética no nível 10, com `Furtividade`
Treinada+Especializada, devolveu exatamente `atributo + maestria +
⌊maestria/2⌋`; `Forja` com `Trein` devolveu o valor usando **Força**, não mais
Inteligência; `Bloquear` devolveu `2d10 + 3` batendo com a Defesa daquele nível;
um feitiço de Classe 3 devolveu Pontos/PE = 9.

**A FICHA tinha 94 linhas antes desta leva; hoje tem 142.** Ainda faltam as
três abas de invocação (`INVOCAÇÃO`, `CATÁLOGO`, `DADOS_INV`) e o menu de
Caminhos continua sem o Evocador — as duas seguem exatamente como a seção
anterior já registrou: a primeira é outro gerador com dono próprio, a segunda
é a decisão `C1` esperando o Mizuki.

#### E a revisão em cima disso achou três coisas, duas delas minhas

*O Mizuki notou que a leva acima rodou em Sonnet e pediu uma revisão no Opus,
mirada nos dois pontos que eu mesmo tinha marcado como "desenho meu, sem
segunda cabeça": a seção 08 e a tabela de atributo dos ofícios.* **A tabela
passou — os onze batem com a peça 7 §5, e o resumo dela ("cinco em Destreza,
três em Inteligência, duas em Essência, uma em Força") fecha.** *O resto não
passou.*

**1 · O atributo do ofício estava CRAVADO na fórmula, e a regra diz o contrário.**
A peça 7 §5 escreve o padrão de cada ofício e fecha com a cláusula que ela
mesma chama de *"a que importa"*: **"o mestre troca quando a ficção pedir, e
diz qual antes da rolagem"**. *Eu tinha tratado ofício como perícia — atributo
fixo, apontado direto na fórmula —, e trocar na mesa exigiria editar fórmula.*
**Hoje o atributo é célula editável, pré-preenchida com o padrão, com menu
suspenso dos cinco, e o total lê dela.** *Perícia continua cravada, e isso está
certo: "o atributo dela é o da tabela e não muda".*

**2 · As Passivas pagas não existiam, e elas comem espaço de feitiço.**
*O manual é explícito: Passiva "é paga com espaços de feitiço conhecido", e a
Classe é o preço — `1` custa 1 espaço, `2` custa 2, `3` custa 3, com teto de
cinco pagas.* **Meu contador só subtraía feitiço, então ele MENTIA para
qualquer ficha com Passiva paga.** *Entrou a tabela das cinco, e o contador
passou a subtrair a SOMA das Classes — soma, e não contagem, porque uma Classe
3 come três espaços. A Passiva Livre ficou de fora do teto, como o manual manda.*

**3 · ⚠⚠ O `IFS` não existe no formato `.xlsx`, e ele estava mentindo em silêncio.**
*Para o atributo virar célula eu escrevi `IFERROR(IFS(...),0)` — que é o idioma
da planilha viva.* **Recalculando de verdade, a Forja devolveu `2` onde devia
devolver `5`.** *O `IFS` é "future function" no OOXML: sem o prefixo `_xlfn.`
ele vira `#NAME?`, e o `IFERROR` engolia o erro e devolvia zero para o
atributo.* **Número errado, sem aviso, numa célula que parece funcionar.**

> **E o prefixo não é a saída, porque ele quebraria o outro lado:** *o destino
> de verdade é o Apps Script montando nativo no Sheets, e lá `_xlfn.IFS` não
> existe.* **A saída é `IF` aninhado, que funciona nos dois.** *A planilha viva
> usa `IFS` sem problema porque ela nasceu dentro do Sheets e nunca passou por
> um `.xlsx` — o idioma dela não é portável, e copiá-lo foi o erro.*
>
> *Vale para o Mizuki saber: qualquer `.xlsx` exportado da planilha viva vai
> mostrar `#NAME?` nessas células. Não é defeito da planilha dele; é o formato.*

**Um quarto achado, dormente e pré-existente:** *a coluna `Atributos` da aba
`DADOS` continha `lista, escala, criacao, nota, pagina` — as CHAVES do bloco do
catálogo, e não os cinco atributos.* **O `dados.py` fazia `list(CAT["atributos"])`
onde devia fazer `CAT["atributos"]["lista"]`.** *Ninguém usava a coluna, então
ela nunca acusou — e foi justamente nela que o menu novo do ofício precisou se
pendurar.*

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

