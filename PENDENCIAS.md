# Pendências · o que precisa de decisão antes de construir

Cada item traz **o que está em aberto**, **por que importa**, as **opções com o preço de cada uma**, e **o que acontece se ninguém decidir**.

---

## As cinco que travavam a construção: decididas

**Estão fechadas, e o dono delas é o `DECISOES-bloco-A.md`.** Não repito os valores aqui — se o mesmo número mora em dois documentos, um dia os dois discordam, e isso já aconteceu neste projeto com as Famílias.

| | decisão |
|---|---|
| A1 · onde o catálogo mora | cópia local fixa, com uma célula puxando a versão corrente da central |
| A2 · vida e energia temporárias | não acumulam, fica a maior · teto de metade do máximo · some no fim da cena · gasta primeiro |
| A2b · onde a regra mora | **aplicada no sistema**: capítulo 1, *Vida, energia e alma* |
| A3 · `Rápido` + `Atrasar` | trava na ficha e, desde a v0.246 do sistema, no manual — com a `Reação` + `Atrasar` e `Parado` junto |
| A4 · vida e PE | atual editável **e** caixinha de delta, os dois |
| A5 · o acento colorido | cor de estado no número: osso → âmbar → vermelho |

O `conferir-decisoes.py` confere que esse documento, o `decisoes-ficha.json` e este arquivo continuam de acordo, e que tudo que a decisão atribui ao manual está mesmo lá.

~~**Entrega pendente do A2b**~~ **APLICADA no sistema, com texto próprio:** *a vida temporária está no capítulo 1 desde a v0.108, e a energia temporária desde a v0.239.* **O `manual-temporario.md` ficou marcado como superado.**

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

### B3 · Equipamento entra na ficha? — **FECHADO em 16/09/2026, na opção A com o refino escolhido, e falta testar no Sheets**

> **⚠ O texto abaixo está velho em duas coisas.** *A planilha viva já tem o campo `EQUIPAMENTO` (`Z40` da FICHA), que troca a proteção passiva pelo número digitado; e o capítulo de equipamento do livro é o 50, e não o 12.* **O defeito continua, medido em 21.632 combinações legais de nível, Destreza, refino, uniforme e escudo:**
>
> | como o jogador preenche o `Z40` | saem erradas | pior erro |
> |---|---|---|
> | vazio | `80,8%` | `7` — nível 6, Revestimento 2 + Torre, Destreza 0: livro `18`, planilha `11` |
> | com a proteção certa | `52,4%` | `6` — a `D40` ignora o teto de Destreza |
>
> *Digitar `Traje 2` no campo dá `#VALUE!` na Defesa e no Bloquear.*
>
> ***Decisão do Mizuki: opção A*** — **um menu com as 27 combinações de uniforme e escudo, e a tabela na `DADOS`.** *Sobra erro em `8,4%` das combinações, de até `2`, e ele é todo do refino escolhido nos marcos: a planilha só conhece o `REFINO DE GRAÇA` (`O54`), e a linha "Refino Atual" da página de aptidões imprime ele.* **Em aberto: se entra um campo de escolhas de Refino.** *A tabela do menu precisa de dono — a proposta é uma chave nova no catálogo, conferida contra o `manual.txt`.*
>
> *A medida, as fórmulas das três opções e o recálculo no LibreOffice estão em `Claude/agentes-2026-09-16/b3-conta/`, fora deste repositório.* **A ficha de papel do sistema também dizia que o escudo desligava a proteção, e isso fechou na v0.246 de lá.**

**Como fechou.** ***Decisão do Mizuki: o campo das escolhas de Refino entra*** — *"Pode seguir na opção Sim, mas lembre-se de colocar o formato correto e afins".* **É a limpeza 10 da `ficha-v01`, no `defesa_equipamento.py`:**

- *o `EQUIPAMENTO` virou menu das 27 combinações de uniforme e escudo, e a tabela delas mora na `DADOS`, saída da chave nova `equipamento_defesa` do catálogo;*
- *o `REFINO ESCOLHIDO` entrou no vão ao lado do `BLOQUEAR`, com o estilo dele célula a célula, menu de `0` a `7`, índice próprio na `DADOS` e nota ao passar o mouse;*
- *a Defesa corta a Destreza pelo menor teto, a proteção soma o escudo por cima do cobrir-se, e o refino — o da proteção e o "Refino Atual" impresso — soma as escolhas, no máximo uma por marco que já passou, até `10`.*

**Como é conferido.** *O `conferir-catalogo.py` lê as três tabelas e as três frases de regra do `manual.txt`; o `conferir-ficha-xlsx.py` confere a tabela, os dois menus, o índice, as três fórmulas e as notas; o `regressao-kaori-na-ficha.py` recalcula dez casos no LibreOffice, com os dois exemplos que o livro publica; e o `comparar-ficha-01.py` conta a limpeza.* **O catálogo foi à `v0.246`, junto do `manual.txt`.**

> **⚠ Na sua mão:** *colar o `Codigo.gs` novo no projeto do Apps Script, rodar o `construir()` do `Ficha.gs` novo numa planilha nova, trocar a `A1` da central para `0.246`, e conferir no Sheets que o menu do refino escolhido vira número.* **Continua sem campo, e fica registrado:** *a `Couraça` (+1 de Defesa vestindo uniforme) e a arma sem o requisito de Força, que tira a Destreza da Defesa.*


A ficha de papel não tem campo de equipamento, mas o capítulo 12 existe e **Traje e Revestimento desligam a proteção inicial**, que entra na Defesa.

Enquanto não entrar, a Defesa fica presa em `10 + Destreza + proteção da aptidão`, e qualquer personagem com equipamento terá a Defesa errada na ficha.

### B4 · A checagem 7 das Famílias precisa subir — **FECHADO em 14/09/2026, na v0.239 do repositório do sistema**

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

**Como fechou.** *O trecho entrou no `conferir-ficha.py` do `Claude 2` como bloco `8`, porque o `7` já era o do bloco de inimigo.* **O `dados.js` da ficha passou a ter as nove Famílias do manual, e as duas fichas `.docx` foram regeradas.**

- *A checagem também lê do manual quantas Famílias são, em vez de ter o `9` escrito nela.*
- *Ela confere as Famílias da Kaori no `make.js` contra a peça 8, e as duas fichas publicadas contra o manual.*
- **Acendeu no estado antigo pelos quatro motivos certos, e o arnês deu onze de onze.**

*O `repo-conserto/` fica como registro do fragmento original.*

### B5 · `Lento` nomeia duas coisas diferentes — **RESOLVIDO no sistema, na v0.139**

> **A Restrição virou `Atrasar`, e a condição continua `Lento`.** *O conserto "caro" que este item previa foi feito do lado do manual.* **O catálogo desta pasta ficou com o nome velho até a sincronização de 14/09/2026**, *e agora os dois menus não colidem mais.*

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

### B6 · O desconto do `Rápido` + `Atrasar` continua disponível fora da ficha — **FECHADO em 16/09/2026, na v0.246 do sistema**

**Como fechou.** *O manual e o livro passaram a escrever o veto no `Rápido`, e a mesma leitura achou a `Reação` com o `Atrasar` e com o `Parado`.* **Os quatro pares da A3 têm fonte `manual` agora**, *o `manual.txt` foi reextraído do livro da v0.246, e o `catalogo-projeto-m.json` levou o texto novo do `Rápido`, da `Reação` e do `Levanta`.* **O `arnes.py` ganhou os dois pares da `Reação` e o `Rápido` + `Parado` como contra-teste, que fica quieto.**


> *A Restrição se chamava `Lento` quando este item foi escrito.*

Consequência escolhida do A3, não descuido.

A ficha recusa a montagem. O manual continua sem a frase, então **quem monta feitiço no papel, de cabeça, ou pelo gerador do manual continua com um terço do orçamento de desconto** — e com a Família Tempo Livre, com o `Rápido` de graça.

Se um dia quiser fechar, o molde da frase já existe no próprio `Rápido`: *"Não entra no mesmo feitiço que Reação."* O texto está pronto no `DECISOES-bloco-A.md`.

### B7 · Botão desenhado não funciona no celular

Achado ao fechar o A4.

O `botão de descanso longo` do documento de desenho não roda no app de celular do Sheets — botão desenhado é coisa de navegador. E o descanso é justamente uma das coisas que se aperta na mesa, pelo telefone.

**Já corrigido no desenho:** o substituto é caixa de seleção ou lista suspensa fazendo papel de botão, que o gatilho pega normalmente. Fica registrado porque a ideia de "botão" pode voltar.

### B8 · O `Estopim` soma um número que não existe — **FECHADO em 15/09/2026, na v0.240 do sistema**

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
> **Reextraído na v0.239 do sistema, ele escreve a CD de hoje.**
>
> **Então este item não se conserta sozinho: ele é parte do B11.** Mudar a
> fórmula da ficha agora a põe à frente do manual que ela declara como fonte, e
> a regra deste repositório é a inversa — *onde a ficha e o manual discordarem,
> o manual vence.* **Conserta-se junto com a re-extração, nunca antes dela.**

**Como fechou.** *A planilha viva já calculava a CD de hoje — `8 + atributo da técnica + maestria`, com o atributo escolhido em `ATRIBUTO DE CONJURAÇÃO` —, e a exportação de 14/09 trouxe isso.* **Sobravam três restos, e os três foram consertados:**

- *a nota da célula `cd de feitiço` no `Codigo.gs` dizia "o 2 é fixo"; o `conferir-ficha-xlsx.py` passou a cobrar dela a fórmula do `manual.txt`;*
- *o `conferir-kaori.py` conferia contra a ficha da Kaori de 07/09, com as contas da mesma época. A cópia vendorizada voltou a ser a do sistema, e a maestria e a Integridade saem das fórmulas do catálogo. E ele imprimia `NAO BATE` e saía com 0: agora ele falha;*
- *o catálogo escrevia a Integridade como `20 + 8 × (nível − 1)`, que morreu na v0.145.*

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

### B11 · O `manual.txt` e o `catalogo-projeto-m.json` estão 96 versões atrás — **FECHADO em 14/09/2026: o `manual.txt` reextraído, e o catálogo na v0.239**

> **Estado em 14/09/2026, na v0.239 do sistema.** *O `manual.txt` saiu do PDF de hoje, e as duas guardas que esperavam ele congelado viraram guardas de concordância.*
>
> **O catálogo foi à v0.239.** *Saíram a condição `Petrificado`, que o sistema tirou na v0.198, e a entrada `Nível`, que era um pedaço do capítulo de condições colado como Melhoria. A Restrição `Lento` virou `Atrasar`, a `Condicao` ganhou o acento, entrou a Melhoria `Efeito Próprio`, e 23 Melhorias e 10 Restrições ganharam o texto do livro.* **Quatro Restrições devolvem `Leve ou Media`:** *o `conferir_feitico.py` conta o menor, e o `teto-fechado.py`, que mede o pior caso, conta o maior.*
>
> **A aba `DADOS` passou a sair do catálogo**, *decisão do Mizuki, pela limpeza 8 do `comparar-ficha-01.py`.* **O `conferir-catalogo.py` lê as contagens das frases do manual**, *e cobra que cada Melhoria, Forma e Restrição do catálogo apareça nele.*
>
> **Ficou por conferir contra o livro, e o `_meta` do catálogo declara:** *fundamento, Origens, sub-origem, rotas de criação, Legados, progressão, Testes de Resistência e atributos.* **Nenhum validador desta pasta lê os Legados.**
>
> **Na sua mão:** *rodar o `construir()` do `Ficha.gs` novo numa planilha nova, trocar a `A1` da central para `0.239`, e exportar de novo para a `ficha-v01` quando puder.*

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

> **⚠ Na v0.239 do sistema o `manual.txt` foi reextraído, e a guarda seguinte acendeu como devia.** *Ela passou a cobrar que o `manual.txt` e o capítulo 35 deem o mesmo número ao Parrudo.*

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

### B13 · A `Voz` soma um número que não existe — **FORMA DECIDIDA em 16/09/2026, e falta a regra**

> ***Decisão do Mizuki: forma B*** — **`CD dos efeitos dela = 8 + atributo dela + maestria do dono`**, *no molde do Teste de Resistência dela.* **Ela vai entrar junto da revisão das invocações**, *que ele anunciou.* **O que ainda falta decidir:**
>
> - *qual atributo dela entra: escolhido na montagem, como o TR treinado, ou pelo efeito;*
> - *quais Traços e Comandos pedem TR — hoje nenhum diz como resolve (`Fisgada`, `Jorro`, `Graúdo`, `Agarrar`, `Arrastar`, `Chamariz`);*
> - *o `Preito` do `Servo` (capítulo 35) também soma metade da maestria nessa CD, e não aparecia aqui.*
>
> **Metade de maestria `1` vale `1`**, *decisão dele na v0.246 do sistema: a `Voz` fica `+1` do nível 2 ao 25 e `+2` do 26 em diante.* **A guarda do `conferir-invocacao.py` estava cega**: *ficava verde em 8 de 10 jeitos de escrever a CD. Agora qualquer `CD` em palavra inteira no capítulo 16 acende, e acendeu na perturbação com a linha de tabela.*
>
> **O `Jorro` ataca e empurra**, *decisão dele: o livro dizia "ataca" e a peça 15 dizia "empurra".* **O capítulo 16 vendorizado, o `invocacao.json` e a `ficha-invocacao.xlsx` foram atualizados.** ***Na sua mão:*** *a aba `CATÁLOGO` da ficha viva ainda diz "ataca em linha ou em área" na `P16`, porque ela vem da exportação da planilha.* **Outras duas entradas mudam regra entre o livro e a peça 15 e ficam para a revisão:** *a `Montaria` ("uma pessoa" contra "uma pessoa ou mais") e o `Remoto` (a peça fala em gate fora da cena).*
>
> *A pesquisa em outros sistemas e as tabelas de CD por nível estão em `Claude/agentes-2026-09-16/b13-pesquisa/`, fora deste repositório.*


Achado montando a ficha da invocação, e é a mesma forma do B8.

A `Voz` é uma das três rotas da `Sintonia` do Evocador (capítulo 35):
*"a CD dos efeitos das suas invocações sobe em `1`, e vira `metade da sua
maestria` a partir do nível 7"*.

**A invocação não tem fórmula de CD em documento nenhum** — nem no capítulo 16,
nem na peça 15. A rota soma `+1` num número que o sistema não produz.

**A ficha não inventa:** ela marca como pendente na seção 09 e manda combinar
com o mestre, e o `conferir-invocacao.py` tem uma checagem que acende no dia em
que o capítulo 16 ganhar uma CD.

### B14 · O Teste de Resistência treinado — **FECHADO em 15/09/2026, na v0.240 do sistema**

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

**Como fechou.** *A planilha somava `IF(<caixa>=TRUE,2,0)` nos quatro TRs.* **A `ficha-v01` ganhou a limpeza 9, no `tr_treinado.py`:** *o termo somado sai do `bonus_se_treinado` do catálogo, que virou `maestria`, e a célula sai do índice da `DADOS`.* **O `regressao-kaori-na-ficha.py` recalcula os quatro TRs no LibreOffice** — *Físico `4` e Vigor `3`, que com o `2` davam `5` e `4`* —, **e o `conferir-catalogo.py` confere o bloco de TRs contra a tabela e as frases do capítulo 1.** *A ficha de papel do sistema imprimia o mesmo `+ 2`, e fechou na mesma versão, com a checagem 10 do `conferir-ficha.py` de lá.*

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
| `manual.txt` | o PDF do Manual da Guilda, `pdftotext -layout` — **reextraído na v0.240 do sistema** |
| `capitulo-16-invocacoes.md` | `sistema/05-material/livro/manual/60-invocacoes.md` |
| `capitulo-35-caminhos-e-trilhas.md` | `sistema/05-material/livro/manual/35-caminhos-e-trilhas.md` |
| `repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx` | o repositório do PDF |

**A ficha da invocação foi construída assim de propósito:** planilha separada,
com o capítulo vendorizado como dono, e sem tocar em nenhum arquivo do sistema.
Ela não depende de nada que esteja em obra do outro lado.

### A re-extração do `manual.txt` (B11) — o bloqueio que eu escrevi já venceu — **FEITA em 14/09/2026**

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
`catalogo-projeto-m.json` primeiro; **B8** e **B14** só depois disso. *Os dois fecharam na v0.240 do sistema.*

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

### B17 · O campo TEMP da INTEGRIDADE não tem fonte no manual — **TIRADO DA FILA em 14/09/2026**

> *Palavras do Mizuki: "Só apague isso da fila, não se preocupe com essa questão".* **O campo continua na
> ficha, vazio e sem efeito, e o texto abaixo fica como registro.**

A ficha tem `integridade_temp` no índice e o campo na tela, mas **nada no
sistema concede integridade temporária**. Procurei o termo no `manual.txt`, no
`catalogo-projeto-m.json` e nas decisões: são seis fontes de vida temporária
(`Apoio`, `Fluxo`, `Aprumo`, `Crosta`, `Vento a Favor`, `Muralha`) e uma de
energia (`Braseiro`, teto 2). De integridade, zero.

**O campo não faz mal** — vazio, o `aplicaPasso_` passa por ele sem efeito, e a
nota do campo agora diz que regra nenhuma o concede. **Mas ele é uma pergunta em
aberto:** ou algo deveria conceder, ou o campo sai da linha da Integridade.

*Decisão tua. Não é dívida técnica: é desenho de sistema.*

### B18 · O `Ficha.gs` está atrás da planilha viva, e o `construir()` apaga tudo — **FECHADO em 14/09/2026**

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

> **Fechado em 14/09/2026.** *O Mizuki mandou a planilha exportada, e o `Ficha.gs`
> passou a sair da `ficha-v01`, que é a cópia dela.* **O `ficha/monta.py` foi
> aposentado:** *ele sai com uma mensagem apontando o caminho novo, e o código fica
> como registro.*
>
> - **Três limpezas novas no extrator.** *A 5 esvazia no molde os três campos de dano
>   e o equipamento. A 6 troca o Arial que sobra pela fonte de corpo, decidida por ele.
>   A 7 devolve o carimbo de versão, que o Sheets em português leu como `104`.*
> - **O emissor lê a `ficha-v01`.** *Fórmula matricial vai em `ARRAYFORMULA`, texto com
>   cara de número vai com apóstrofo, e a altura, a largura, as caixas e as imagens são
>   as da planilha.*
> - **A decisão C6 tem as seis abas da planilha viva.** *Palavras dele sobre a `MESA`
>   e a `QUEM É`: "Ainda vamos manter sem, por enquanto".*
> - **A decisão C1 registra o Evocador de volta ao menu**, confirmado por ele.
> - **O `conferir-ficha-xlsx.py` e o `regressao-kaori-na-ficha.py` leem a `ficha-v01`.**
>   *A Kaori passou a esperar Integridade `26` e CD `12`, que é o que o livro publica.
>   O `28` e o `13` eram das fórmulas aposentadas, e o gerador velho também estava nelas:
>   um confirmava o outro.*
>
> **Os dezesseis validadores passam**, e cinco perturbações novas acendem em cópia
> isolada, com um contra-teste verde.
>
> **⚠ Três coisas ficam registradas.** *O `construir()` continua apagando todas as abas:
> rode numa planilha nova, nunca na que tem personagem.* **O `Ficha.gs` novo ainda não
> rodou no Sheets:** *daqui se confere só a metade de dados dele.* **E as abas
> `INVOCAÇÃO` e `CATÁLOGO` têm cerca de `1610` e `1785` px de largura**, *acima
> dos `1366` de notebook que a ficha pede. Elas são do gerador da invocação, e o
> `conferir-ficha-xlsx.py` só imprime a largura delas.*
>
> **⚠ E o `construir()` parou no primeiro teste no Sheets, em 15/09/2026, com `Range not found` no `menusSuspensos_`.** *Oito dos doze menus da FICHA vêm da exportação como lista escrita, `"a,b,c"`, e o script passava a lista ao `getRange`.* **O molde passou a montar esses menus por `requireValueInList`, e o `conferir-ficha-xlsx.py` roda o `menusSuspensos_` no node, num Sheets de mentira que recusa endereço inválido.** *A checagem de antes deixava a lista passar, porque lista escrita não tem aba. O arnês deu cinco de cinco, com o `Ficha.gs` que parou como contra-teste.*
>
> **⚠ E a segunda montagem terminou com `#ERROR!` em toda fórmula com vírgula.** *A planilha nova estava em português, e o `setFormula` lê a pontuação no idioma da planilha — o comentário do molde dizia o contrário. Na exportação dela, as 104 fórmulas com vírgula quebraram, e as que quebraram sem vírgula dependiam de uma delas.* **O `construir()` passou a montar em inglês e devolver o idioma de antes num `finally`**, *e o `conferir-ficha-xlsx.py` confere essa ordem no script, com o `Ficha.gs` que deu `#ERROR!` como contra-teste.*
>
> **⚠ E a formatação da montada não era a da viva.** *Comparando a exportação da viva com a da montada: o emissor só levava a borda de cima, e só de célula com valor — na FICHA, 1615 lados de 6272 —; a caixa vazia de digitar saía sem alinhamento, a quebra de texto e o itálico não eram escritos, o texto preto saía claro, e as imagens entravam soltas, com o tamanho do arquivo e não o da tela.* **O emissor passou a levar os quatro lados de toda célula, mesclada e vazia inclusive, e o formato das vazias.** **E as imagens entram dentro da célula, por decisão do Mizuki em 15/09/2026:** *numa caixa mesclada medida no pixel do script, com a arte redimensionada para ela, porque o Sheets encaixa sem esticar.* *O `conferir-ficha-xlsx.py` confere as bordas lado a lado, as vazias e as caixas das imagens, e o arnês deu onze de onze, com o `Ficha.gs` de antes deste conserto como contra-teste.*
>
> **O que ainda difere, e fica registrado:** *as três faixas de pincel passam de 11 a 14 px para 21 px de altura, que é a linha em que caem; o selo da FICHA perde o deslocamento de 29×15 px; a `INVOCAÇÃO` e o `CATÁLOGO` têm coluna de 35 px contra os 39 da viva; e a `DADOS_INV`, escondida, sai com fundo e altura de linha diferentes.* **Imagem em célula some quando o Sheets exporta `.xlsx`:** *o `extrair.py` passou a guardar o tamanho de tela e, se a exportação vier sem imagem, mantém as do layout anterior e avisa.* **Nada disso rodou no Sheets ainda:** *a imagem em base64 dentro da célula só é confirmada por guia da comunidade, e a borda aplicada em pedaço de mesclagem também precisa ser vista na planilha.*
>
> **⚠ E 47 fórmulas eram gravadas antes de a aba que elas citam existir.** *A montagem segue a ordem das abas: a CARTEIRA cita a FICHA, a FICHA cita a DADOS, a INVOCAÇÃO cita a DADOS_INV. Fórmula gravada assim fica em `#REF!`.* **O `montarAba_` passou a guardar as fórmulas numa fila, e o `construir()` grava a fila depois que as seis abas existem**, *ainda em inglês.* *O `conferir-ficha-xlsx.py` confere essa ordem, e o arnês deu cinco de cinco. Das três causas que o Gemini apontou para o `#REF!`, esta é a que procedia: nenhuma fórmula tem barra invertida, e o idioma já estava resolvido.*
>
> **⚠ E a terceira montagem saiu quase igual à viva, com dois defeitos.** *Faltavam os contornos da direita e de baixo das caixas mescladas: o Sheets só guarda formato no canto de cima à esquerda da mesclagem, e o `.xlsx` guarda essas bordas nas células de dentro — na FICHA, 2008 lados de baixo e 363 da direita moravam nelas.* **A borda de célula mesclada passou a ir para o bloco inteiro, com o traço mais grosso aplicado por último.** *E as quatro barras — vida, energia e integridade na FICHA, a vida na INVOCAÇÃO — ficavam vazias: o Sheets exporta a `SPARKLINE` embrulhada em `IFERROR(__xludf.DUMMYFUNCTION(...))`, que remontada falha calada.* **O emissor tira o embrulho.** *O `conferir-ficha-xlsx.py` confere as bordas bloco a bloco e as fórmulas desembrulhadas, e o arnês deu sete de sete.*
>
> **⚠ E a ida e volta pelo Sheets mostrou mais cinco defeitos.** *O Mizuki exportou a ficha montada, e ela voltou com as colunas da INVOCAÇÃO, do CATÁLOGO, da DADOS e da DADOS_INV 12% mais estreitas: o emissor fazia pixel = 7 × largura, e o Sheets faz 8 × largura − 1, medido em oito pares no `medidas/larguras-sheets.json`.* **A DADOS perdia a tabela de perícias da coluna AB** *— o `dados_catalogo.e_da_lista` via `"AB"` dentro de `"ABCDEFGHIJKL"`, desde a v0.239 do sistema, e o comparador contava a perda como limpeza.* *E a linha 9 da CARTEIRA e as da DADOS_INV ganhavam altura que a viva não declara, o `"1"` de seção virava número, e a DADOS_INV saía pintada por inteiro.* **Os cinco estão consertados, e a imagem que a exportação traz de dentro da célula — ancorada no canto da caixa, com tamanho sem sentido — é reconhecida pelo extrator, que mantém as do layout.** *O arnês deu oito de oito, e a volta simulada, com a exportação no lugar da viva, passa no extrator, na montagem, no `conferir-ficha-xlsx.py` e no comparador.* **Essa exportação não entrou como `original.xlsx`:** *ela guarda as larguras estreitadas. A próxima, depois de montar com o `Ficha.gs` novo, pode entrar.*

### B19 · O teto da temporária não é aplicado pela planilha — **FECHADO em 15/09/2026, testado no Sheets pelo Mizuki**

**O capítulo 1 do manual põe teto de metade do máximo na vida e na energia temporárias**, *e a A2 desta pasta segue ele desde 14/09/2026.* **A planilha não aplica o teto:** *a caixinha de ± come a temporária antes da reserva, mas quem digita a temporária pode passar da metade do máximo.* **A nota da célula avisa.**

*O conserto é o `Codigo.gs` prender o campo TEMP em metade do máximo quando ele é editado.* **Ele precisa ser testado no Sheets, que daqui não roda.**

> **Escrito na v0.240 do sistema, e ainda não testado no Sheets.** *O `onEdit` chama o `prenderTemp_`, que usa o `tetoTemp_`: metade do máximo, arredondada para baixo, com piso de 1. Campo vazio fica vazio, e sem máximo não há teto.* **O `regressao-delta.js` confere o `tetoTemp_` contra o exemplo do capítulo 1, e o `arnes-delta.py` ganhou nove perturbações.** *O que falta: colar o `Codigo.gs` na planilha, digitar um TEMP acima da metade e ver ele descer. O `testeTeto()` roda do editor.*
>
> *O "fica a maior" da A2 não entrou: quem digita a temporária pode estar trocando de fonte ou zerando no fim da cena, e o script não sabe qual.*
>
> **Testado no Sheets em 15/09/2026, e funcionou.**

### B20 · Seis chaves do catálogo nunca conferidas contra o livro — **FECHADO em 15/09/2026, na v0.240 do sistema**

**`atributos`, `fundamento`, `origens`, `legados`, `legados_formatos` e `progressao` estavam na lista das não conferidas, e estavam atrás do livro.**

- **Legados:** *um `Sem Patente` na Latente e um `Nunca Estive Lá` na Restrição Celestial que o livro não tem, sete Desliga faltando, o `Peso Real` no formato errado, e a entrada da Sem Técnica cortada em cinco Origens.* **Os 90 foram refeitos do capítulo 7**, *com formato, relógio e, na Restrição Celestial, o ramo. O campo `alcanca` saiu: ele não era texto do livro, e nenhum código o lia.*
- **Progressão:** *a entrega de dezoito níveis estava cortada, e o XP não estava na tabela.*
- **Origens:** *só duas tinham a frase de abertura, e sem acento. Agora as sete e a Sem Técnica levam a do livro.*
- **Atributos:** *a página 12 era de uma paginação antiga, e saiu.*
- **Fundamento:** *a frase "o `Remate` é a única peça acima dos pontos contra um alvo" virou a regra do livro: só a Liberação Máxima passa dos pontos contra um alvo só.*

**O `conferir-catalogo.py` lê as seis do `manual.txt`**, *reextraído do livro da v0.240 — os dezesseis validadores passaram com ele antes da troca.* **Os preços de Melhoria, a devolução, a Liberação e o teto são recalculados classe a classe pela tabela `Números da montagem`.** *A lista das chaves não conferidas ficou vazia.*

> **Achado, decidido pelo Mizuki em 15/09/2026: fica como está.** *O livro diz que "Só a Liberação Máxima passa dos pontos da Classe em dano contra um alvo só", e a Melhoria `Remate` dá +25% de dano contra alvo abaixo de metade da vida.* **Os pontos da Classe contam dados, e o `Remate` multiplica o dano final**, *então as duas regras valem juntas e o catálogo não muda. A decisão está na v0.241 do sistema.*

### B21 · O texto do catálogo não é conferido contra o livro

**Achado na v0.246 do sistema:** *com o texto velho do `Rápido` no `catalogo-projeto-m.json`, o `conferir-catalogo.py`, o `conferir-decisoes.py` e o `revisao-cetica.py` saíram verdes.* **O catálogo confere contagem e nome, e não a frase.**

*Medido na mesma hora: das 66 Melhorias com texto, 57 aparecem exatas no `manual.txt` normalizado, e as 9 que não aparecem são artefato do `pdftotext -layout`* — **hífen de quebra, número de página e troca de página no meio da tabela**, *e não texto divergente.* **Uma checagem de frase precisa tolerar isso**, e as Restrições guardam o texto em `o_que_muda`, não em `efeito`.

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

