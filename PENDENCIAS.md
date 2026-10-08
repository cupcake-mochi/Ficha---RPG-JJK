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

> **⚠ Na sua mão:** *colar o `Codigo.gs` novo no projeto do Apps Script, rodar o `construir()` do `Ficha.gs` novo numa planilha nova, trocar a `A1` da central para `0.246`, e conferir no Sheets que o menu do refino escolhido vira número.* **Vai ter campo na Ficha Pessoal, e fica registrado** *(aba de itens e equipamentos, bio, foto e afins):* *a `Couraça` (+1 de Defesa vestindo uniforme) e a arma sem o requisito de Força, que tira a Destreza da Defesa.* **Fechado em 01/10/2026, no B26:** *a Ficha Pessoal existe. A `Couraça` saiu do livro na v0.270 do sistema, e o campo dela não entra, por decisão do Mizuki. A arma sem o requisito de Força ganhou a marca dela na aba, com a punição que ele decidiu no mesmo dia (desvantagem ao atacar com ela), que ainda não está no livro.*


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

### B13 · A `Voz` soma um número que não existe — **FECHADO na ficha da invocação em 19/09/2026, na v0.251 do sistema; na aba INVOCAÇÃO da ficha principal fica só a nota, e o bloco entra com a remodelagem das invocações**

> ***19/09/2026, v0.251 do sistema: o livro escreveu a regra, e a ficha da invocação a calcula.*** **A CD dos efeitos é `8 + o atributo dela + a maestria do dono`, com o atributo escolhido na montagem; a arma só mexe no acerto, nunca na CD (decisão dele: "Pra CD, sim... sempre vai ser so o atributo da invocação").** *Cinco entradas pedem Teste de Resistência do alvo — `Fisgada`, `Agarrar`, `Arrastar` e o `Jorro` contra o Físico, o `Chamariz` contra o Espírito —, e a `Voz` e o `Preito` na CD não somam, porque dão o mesmo número em todo nível de 2 a 30.*
>
> **Feito aqui, e passando nos 16 validadores:** *os dois capítulos vendorizados de novo, byte a byte;* *o `invocacao.json` ganha `cd_base`, `efeitos_com_tr` e `cd_bonus`, a `Voz` perde o `PENDENTE`, e o `Servo` ganha o `Preito`;* ***a seção 9 do `constroi.py` deixa de ser "o que a ficha não calcula" e vira "A CD DOS EFEITOS"*** *— cinco campos: o atributo da montagem, o Preito na CD (só no Servo), o bônus, a CD e uma conferência que avisa quando o acerto usa outro atributo, que só vale com arma. O bônus é o **maior** da `Voz` e do `Preito`, e nunca a soma.* *O atributo da CD é um campo próprio, e não o "atributo do acerto" da seção 4: com arma o acerto muda e a CD não pode ir junto.* ***O `conferir-invocacao.py` foi de `209` para `238` checagens, a regressão de `138` para `184` (o modelo lê a base e as faixas do bônus do texto dos capítulos, e não só do json), e o arnês tem `45` perturbações, `16` novas, com o `Preito` valendo o dobro e a CD seguindo a arma como contra-testes.***
>
> **A aba `INVOCAÇÃO` da ficha principal ficou pela metade, de propósito.** *Ela veio da exportação do Sheets e não bate com o `constroi.py`: o bloco final começa na linha `113`, e o do gerador na `114`, e há edições à mão no meio (o `d20 +` mudou de coluna). Copiar as linhas do gerador não serve; o bloco tem de ser montado nas coordenadas da aba principal.* **Já mudou o texto que mentia:** *a nota `D116` dizia "a CD não tem fórmula… ainda", e agora diz a conta e manda somar à mão, pela `_TROCAS_DO_LIVRO` (chave por texto). O `Ficha.gs` novo é `679cd7be`, e a única diferença para o de antes (`4d5fe0b9`) é essa linha; o `Codigo.gs` continua `d1a6b448`.* ***Decisão do Mizuki em 19/09/2026: fica só a nota por ora.*** *O bloco de campos (as coordenadas da aba principal, pelo `ficha_layout.py`, com o desenho aprovado no Sheets) entra junto da remodelagem das invocações e do Evocador que ele anunciou.*
>
> **O que a ficha da invocação não calcula, e diz na própria seção 9:** *o resto do `Preito` (as perícias e os Testes de Resistência somam metade da maestria, e a escolha pode ser o acerto ou a Defesa) e a invocação com arma (o livro ainda não diz quem treina a invocação numa arma, nem se o dado da arma soma ao `Investir`).* *As duas ficam para a remodelagem das invocações e do Evocador que ele anunciou.*


> ***Decisão do Mizuki: forma B*** — **`CD dos efeitos dela = 8 + atributo dela + maestria do dono`**, *no molde do Teste de Resistência dela.* **Ela vai entrar junto da revisão das invocações**, *que ele anunciou.* **O que ainda falta decidir:**
>
> - *qual atributo dela entra: escolhido na montagem, como o TR treinado, ou pelo efeito;*
> - *quais Traços e Comandos pedem TR — hoje nenhum diz como resolve (`Fisgada`, `Jorro`, `Graúdo`, `Agarrar`, `Arrastar`, `Chamariz`);*
> - *o `Preito` do `Servo` (capítulo 35) também soma metade da maestria nessa CD, e não aparecia aqui.*
>
> **Metade de maestria `1` vale `1`**, *decisão dele na v0.246 do sistema: a `Voz` fica `+1` do nível 2 ao 25 e `+2` do 26 em diante.* **A guarda do `conferir-invocacao.py` estava cega**: *ficava verde em 8 de 10 jeitos de escrever a CD. Agora qualquer `CD` em palavra inteira no capítulo 16 acende, e acendeu na perturbação com a linha de tabela.*
>
> **O `Jorro` ataca e empurra**, *decisão dele: o livro dizia "ataca" e a peça 15 dizia "empurra".* **O capítulo 16 vendorizado, o `invocacao.json` e a `ficha-invocacao.xlsx` foram atualizados.** ***Fechado em 19/09/2026:*** *a aba `CATÁLOGO` da ficha vinha da exportação da planilha e ainda dizia "ataca em linha ou em área" na `P16`. O gerador passou a escrever "Ataca e empurra em linha ou em área", pela `_TROCAS_DO_LIVRO` do `correcoes_texto.py` (chave por texto, não por endereço), o comparador conta como limpeza 21, e o `conferir-ficha-xlsx.py` confere a célula contra a linha do capítulo 16. A planilha viva só muda ao colar o `Ficha.gs` novo e rodar o `construir()`.* **Outras duas entradas mudam regra entre o livro e a peça 15 e ficam para a revisão:** *a `Montaria` ("uma pessoa" contra "uma pessoa ou mais") e o `Remoto` (a peça fala em gate fora da cena).* *Medido em 19/09/2026: o CATÁLOGO da ficha já diz da `Montaria` o que o livro diz ("uma pessoa ou mais"), e segue a peça 15 no `Remoto` ("Dentro da cena, para qualquer um; fora da cena, com…"), que o livro resume em "além dos 18 metros da amarra".*
>
> *A pesquisa em outros sistemas e as tabelas de CD por nível estão em `Claude/agentes-2026-09-16/b13-pesquisa/`, fora deste repositório.*
>
> **19/09/2026, o Mizuki respondeu as três perguntas que faltavam.** *(1) O atributo da CD é escolhido na montagem, um dos cinco, e não muda depois.* *(2) Pedem Teste de Resistência do alvo `Fisgada`, `Agarrar` e `Arrastar` (Físico), o empurrão do `Jorro` (Físico) e o `Chamariz` (Espírito); o `Graúdo` fica de fora.* *(3) A `Voz` e o `Preito` na CD não acumulam.* **A conta achou uma coisa que ele não tinha visto:** *as duas dão o mesmo número em todo nível de 2 a 30 (`+1` até o 25, `+2` do 26 em diante), então "não acumulam" deixa a CD do `Preito` sem efeito para quem tem a `Voz`, e a regra escrita tem de dizer isso.* **As duas leituras minhas ganharam o "de acordo" dele no mesmo dia:** *o atributo da CD é o mesmo do acerto "a não ser que ela use alguma arma", e os TR por efeito.* **A ressalva abriu um ponto novo:** *o livro não diz se a invocação pode empunhar arma, e com arma o acerto segue o atributo da arma. Fica para a versão do sistema decidir entre a CD guardar o atributo da montagem, a CD seguir o acerto, ou invocação não usar arma.* **A regra mora no livro do sistema, então a ficha só segue depois dele.** *O rascunho com o texto proposto, a conta e a lista do que falta está em `sistema/03-mecanica/RASCUNHO-cd-da-invocacao.md`, no repositório do sistema (`Claude 2`), e não foi commitado.*


*Achado original, até a v0.250 — o que está acima já o fechou.*

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
| perícias treinadas | ~~8 ou 9, o jogador escolhe~~ **o livro de hoje: 9 perícias e 2 ofícios, ou 10 e nenhum**, e a ficha deduz a rota (B22), mostrando 9 e 2 enquanto couber (B23) |
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
| `manual.txt` | o PDF do Manual da Guilda (o de coluna única), `pdftotext -layout` — **reextraído na v0.263 do sistema** |
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

### B21 · O texto do catálogo não é conferido contra o livro — **FECHADO em 19/09/2026**

**Achado na v0.246 do sistema:** *com o texto velho do `Rápido` no `catalogo-projeto-m.json`, o `conferir-catalogo.py`, o `conferir-decisoes.py` e o `revisao-cetica.py` saíram verdes.* **O catálogo confere contagem e nome, e não a frase.**

*Medido na mesma hora: das 66 Melhorias com texto, 57 aparecem exatas no `manual.txt` normalizado, e as 9 que não aparecem são artefato do `pdftotext -layout`* — **hífen de quebra, número de página e troca de página no meio da tabela**, *e não texto divergente.* **Uma checagem de frase precisa tolerar isso**, e as Restrições guardam o texto em `o_que_muda`, não em `efeito`.

**Como fechou.** O `conferir-catalogo.py` ganhou a seção *O texto do catálogo, contra o livro*, que confere cinco
campos: `melhorias.efeito` (66), `restricoes.o_que_muda` (19), `pericias.descricao` (23), `origens.em_uma_linha` (7) e
`caminhos.em_uma_linha` (1). A comparação não é por igualdade, porque o `pdftotext` mete no meio da frase o nome da
coluna vizinha, o número da página e até uma palavra dentro de outra (`deslocaPróprio mesmento`): todo caractere da
frase do catálogo tem de aparecer, em ordem, numa janela do livro, com no máximo 4 cortes, 20 caracteres num corte e
30 no total. Os tetos saíram da medição das 14 frases reais que o PDF parte (no máximo 3 cortes, 11 caracteres, 22 no
total); sem eles, uma palavra trocada passava, porque as letras dela se espalham pelo texto seguinte. Três controles
no próprio validador: aceita a frase partida do `Abre Ferida`, reprova o `−2` trocado por `−3`, reprova
`próximo turno` trocado por `turno seguinte`. Não entram os campos que são anotação nossa, escrita sem acento
(`embutido`, `alcance` e `nota` das Formas, `excecao` das Melhorias).

**O que a checagem achou, e foi corrigido.** Melhorias, Restrições, Origens e Caminhos passaram inteiros. **As
descrições de 13 das 23 perícias não estavam no livro:** onze seguiam uma versão velha (`carregar alguém que não
consegue andar`, `O lado técnico`, `sacar que alguém está prestes a conjurar`), a Acrobacia levava um `3` de página no
meio da frase, e a do Provocar levava, depois da segunda frase, o texto de uma caixa lateral do PDF (*Analisar a
técnica do inimigo*). Esse lixo não chegava na ficha, porque o GLOSSÁRIO corta em duas frases, mas o texto velho
chegava. Cada uma passou a ser o texto do livro, tirado por código da seção *Perícias* do capítulo 3, com a
quantidade de frases que a entrada já tinha e no máximo duas, que é o corte do GLOSSÁRIO. O `Ficha.gs` mudou só no
`Exemplo:` dessas 13 linhas do GLOSSÁRIO. Sentir Energia perdeu, no catálogo, `É a perícia mais rolada da mesa`, que o
livro não diz. **O catálogo continua na v0.246**, e a lista `conferido_contra_o_livro` da `_meta` passou a dizer
`pericias (nomes e descricao)`.

> **⚠ Na sua mão:** a mudança só aparece no GLOSSÁRIO da planilha viva depois de colar o `Ficha.gs` novo e rodar o
> `construir()`. As 13 células estão na coluna K, nas linhas das perícias.

### B22 · A ficha que conta sozinha — **FEITA em 17/09/2026, e testada no Sheets pelo Mizuki no mesmo dia**

**O Mizuki redesenhou a FICHA no Sheets e pediu as contas:** *atributo com a caixa pequena (o que o jogador distribui) e a grande (o total), pontos de marco de Corpo por atributo, o `Marco Escolhido` com Refino, Atributo e Feitiço, o `Buff/Debuff` da Defesa, as caixas `X de Y` de pontos, perícias, ofícios, Testes de Resistência e aptidões, as perícias do Caminho marcadas sozinhas, e aviso e nota nas caixas de conta.* **É a limpeza 12 da `ficha-v01`, no `ficha_automatica.py`**, *com as contas intermediárias numa tabela `contas da ficha` escondida na `DADOS`.*

**O que o livro decide, e a ficha lê do `manual.txt` e do catálogo:**

| caixa | conta |
|---|---|
| atributo grande | o pequeno + os marcos de Corpo nele; aviso se passar de 6 |
| Pontos Disponíveis | 9 da criação + 1 por marco que já passou; aviso se passar de 3 antes do primeiro marco |
| Marco Escolhido | Refino + Atributo + Feitiço contra os marcos que já passaram |
| Perícias e Ofícios | 9 e 2, ou 10 e nenhum; cada marco de Corpo dá +1 perícia ou ofício, ou uma especialização do nível 10 em diante |
| Testes de Resistência | 2 |
| Aptidões | 2 de graça + 1 por escolha de Refino, e 2 quando o refino já está em 10 |
| espaços de feitiço | + 1 por escolha de Leque |
| Passivas do Leque | uma por escolha de Leque, e elas não custam espaço |

- ***Decisão do Mizuki: a rota do ofício é deduzida.*** *(O B23 trocou o que a ficha mostra: 9 e 2 enquanto couber.)* *A ficha mostrava o máximo de cada lista; quando o jogador marca além da base de uma, entende que o marco de Corpo foi para ela; e se passar nas duas, as duas caixas dizem quantos passaram.* **O máximo de uma lista só vem de rota que ainda cabe** — *sem isso, 10 perícias sem marco mostravam "1 de 1" ofício, e marcar esse ofício já passava.*
- ***Decisão do Mizuki: as Passivas dividem em duas colunas, a normal e a do Leque, com duas linhas a mais.*** *Só a coluna normal entra na conta de Feitiços Disponíveis.*
- **Aptidões no teto dependem da ordem das escolhas**, *que a ficha não guarda.* **Medido:** *a ordem só muda o número em quatro combinações, todas no nível 26 ou 30, e em uma aptidão.* *A ficha conta como se as escolhas de Refino tivessem sido as últimas, e a nota manda conferir com o mestre.*
- **O Caminho marca sozinho só as duas perícias fixas.** *O pedido incluía ofício e Teste de Resistência, e o livro dá os dois à escolha: o "ofício fixo" do catálogo e da tabela dos Caminhos era resto do manual da v0.104, sem capítulo nem peça no sistema, e saiu.*

**Achado no caminho: o índice da `DADOS` guardava endereço como texto**, *e as linhas inseridas pelo Sheets o deixaram apontando para o lugar antigo — a vida em D23 com ela em D26.* **A caixinha de ± da planilha viva parou por isso.** *Agora o endereço é `=ADDRESS(ROW(FICHA!D26),COLUMN(FICHA!D26),4)`, derivado dos rótulos, e anda sozinho (limpeza 11, `indice_ficha.py`).* **A mesma derivação, rodada no layout de antes, reproduz os 38 endereços de texto que ele tinha.** *O extrator passou a achar as barras e os campos de mesa pelo rótulo, e a mover junto com as linhas as imagens que mantém.*

**Como é conferido.** *A `regressao-kaori-na-ficha.py` recalcula doze casos no LibreOffice e compara as quinze caixas de cada um com um modelo de força bruta, que testa rota e divisão dos marcos de Corpo uma a uma e conta as aptidões marco a marco; o `conferir-ficha-xlsx.py` confere o índice em fórmula e o `Codigo.gs`; o `regressao-delta.js` roda a marcação das perícias do Caminho no node.*

> ~~**⚠ Na sua mão:** colar o `Codigo.gs` novo, rodar o `construir()` e conferir no Sheets~~ **testado pelo Mizuki em 17/09/2026**, *com a lista de pedidos que virou o B23.*

### B23 · O desenho da mesa, na segunda rodada — **FEITA em 17/09/2026, e falta testar no Sheets**

**O Mizuki testou o B22 e mandou a exportação nova com os pedidos da mesa.** *É a limpeza 13, no `ficha_layout.py`, que roda antes de todas, e mudanças nas limpezas 11 e 12 e no `Codigo.gs`.*

| pedido | o que ficou |
|---|---|
| foto maior na CARTEIRA | a caixa vai de D8:J18 para C8:K21, sem coluna nova, e a moldura é redesenhada em 386 × 460 |
| margem da direita | coluna AU de respiro na CARTEIRA, na INVOCAÇÃO e no CATÁLOGO; o que o CATÁLOGO pintava depois dela sai |
| portador, registrado por, servidor | `Coloque o nome do personagem aqui` e `Nick do jogador` de exemplo; `MESA DE ORIGEM` vira `SERVIDOR USADO`, com nota |
| nome do sistema | `=UPPER(DADOS!$F$1)`, e a `DADOS` escreve o `_meta.sistema` do catálogo |
| técnica declarada | `TÉCNICA MARCIAL DECLARADA` na rota Técnica Marcial, `ESTILO DECLARADO` na Sem Técnica, `TÉCNICA AMALDIÇOADA DECLARADA` no resto |
| duas Restrições Celestiais | o menu de Origem sai das `rotas_de_criacao`: `corpo pela técnica` é Fundamento, `sem energia` é Técnica Marcial |
| Caminho e Trilha | a ficha nasce com `Escolha seu Caminho` e `Escolha sua Trilha`; o menu da Trilha filtra pelo Caminho, e trocar o Caminho devolve para o texto de escolha a Trilha que não é dele |
| 9 e 2 | a ficha mostra 9 perícias e 2 ofícios enquanto essa rota couber, e passa para 10 e nenhum quando só ela cabe |
| caixa das escolhas | diz o que falta da criação e do marco de Corpo, e a conta sem ofício quando nenhum ofício está marcado; letra 10, para caber em duas linhas |
| aptidões de graça | as duas primeiras linhas vêm com `Cobrir-se de energia` e `Canalizar energia`, ou `Defesa sem Armadura` e `Estímulo Muscular` na Restrição sem energia; a nota muda com a Origem |
| Marco Escolhido | rótulos `Refino`, `Corpo` e `Leque` |
| Buff/Debuff | ao lado da Defesa, Iniciativa, CD, Conjuração, Corpo a Corpo, À Distância e Deslocamento; o EQUIPAMENTO volta a ser uma caixa só |
| maiúscula | `Um atributo passou de 6`, `Na criação, nenhum acima de 3`, `Especialização só no nível 10` |
| notas | no título da caixa quando ele é texto; nota nova na Defesa, nos Buff/Debuff, nos ataques, no Deslocamento, nos Feitiços, nas Passivas, na caixa das escolhas, na Trilha e na CARTEIRA |
| proteção | aviso em toda fórmula da FICHA e da CARTEIRA, menos as três barras de agora; o resultado das perícias, ofícios e Testes de Resistência entra |

- **Os nomes das aptidões e Bênçãos de graça saem do `manual.txt`.** *O texto das quatro notas é resumo do manual, e o `conferir-ficha-xlsx.py` confere que os números delas estão lá.*
- **O rótulo da técnica segue o capítulo 7:** *a Sem Técnica monta um estilo; Corpo Amaldiçoado e Restrição sem energia são da rota Técnica Marcial; a Restrição corpo pela técnica é Fundamento.*
- **A caixa das escolhas estava em letra 14, numa linha.** *A frase mais longa medida tem 98 caracteres, e em 14 ela corta.*

**Como é conferido.** *A `regressao-kaori-na-ficha.py` recalcula vinte casos no LibreOffice, com 25 caixas cada, e os casos novos cobrem a caixa das escolhas, as linhas de graça, a Restrição sem energia, a semente da Sem Técnica e os sete Buff/Debuff. O `conferir-ficha-xlsx.py` confere a CARTEIRA, o menu de Origem, a trava por varredura e as notas. O `regressao-delta.js` roda no node a Trilha de outro Caminho e o lugar da nota, e o `arnes-delta.py` perturba as duas e a marcação das perícias do Caminho.*

> **⚠ Na sua mão:** *colar o `Codigo.gs` novo, rodar o `construir()` do `Ficha.gs` novo numa planilha nova e passar o personagem para ela.* **No Sheets, conferir:** *a Trilha voltando para `Escolha sua Trilha` ao trocar o Caminho, a nota das aptidões de graça mudando ao escolher a Restrição sem energia, o aviso ao apagar o resultado de uma perícia, e se a foto da CARTEIRA ficou no tamanho certo.*

### B24 · O `construir()` podia deixar a planilha em inglês — **FECHADO em 18/09/2026**

*Achado ao vivo: a `CARTEIRA` mostrava `Emitida 18.09.2026` certo, mas o Mizuki notou que a
planilha não estava em português.*

O `finally` do `construir()` restaurava `ss.getSpreadsheetLocale()` — **o idioma que a planilha
já tinha antes de rodar**, não `pt_BR`. Uma planilha nova do Google Sheets nasce no idioma da
**conta** de quem criou, não do produto: se a conta já for `en_US`, "devolver o idioma de antes"
devolve `en_US`, e a ficha de um sistema em português fica com o resto do arquivo — moeda, data
por extenso, o que quer que dependa do locale — em inglês, sem erro nenhum aparecer.

**Como fechou.** *`ficha/modelo.gs.js` — o `finally` força `'pt_BR'` sempre, em vez de devolver a
variável `idioma` capturada no começo.* **O `conferir-ficha-xlsx.py` ganhou a checagem que
confirma isso e a que proíbe o padrão velho de voltar** — *perturbada numa cópia isolada,
revertendo pro `setSpreadsheetLocale(idioma)`: as duas acendem, e restaurando ficam verdes.*

> **⚠ Na sua mão:** *como qualquer mudança no `Ficha.gs`, só pega rodando o `construir()` de novo
> numa planilha nova.*

### B25 · A Bateria de Cores — o botão de paleta na CARTEIRA

*Pedido do Mizuki em 17-18/09/2026: um menu de paleta embaixo da foto, com uma lista grande de
cores que repintam a ficha inteira, cada uma com versão clara e escura, e a paleta do livro
("Mizuki") obrigatória entre elas.*

**Sessenta e um temas, cento e vinte e duas escolhas.** Trinta e dois de cor e humor (mais o
`Mizuki` e o `Noite`, a roxa atual), dez comemorativos (ocidentais e asiáticos) e dezenove de
conto, criatura e lenda — da Ásia e do próprio anime. Nenhuma cor foi inventada: todas saem de
paleta real do Color Hunt ou de pesquisa cultural, e o `medidas/paletas-grandes/derivar.py`
deriva as duas versões de cada uma e mede contraste WCAG antes de aceitar — piso `4,5` para
texto e `3,0` para acento, contra fundo E painel, com folga até `4,7` e `3,3`. As 122 passam.

**Os treze papéis por tema são os do `ficha/estilo.py`** — `FUNDO`, `PAINEL`, `PAINEL_ALTO`,
`LINHA`, `TEXTO`, `TEXTO_FRACO`, mais seis que ninguém tinha nomeado antes: `TINTA`, `PAPEL`,
`PAINEL_BAIXO`, `BLOCO`, o `3B3360` dos menus grandes e o `8A7EC4` do fio embaixo do valor —, e
o `ACENTO`, que é papel novo: hoje ele pinta a `FAIXA` dos títulos de seção, que na paleta atual
mal se destaca do resto e em cada tema novo ganha uma cor de verdade.

**Como funciona.** O `construir()` cria a caixa (`configurarPaleta_`, chamado do próprio
`Ficha.gs`) duas linhas abaixo da foto, do tamanho dela, com um menu suspenso das 122 opções — e
o `onOpen` cria a mesma caixa numa ficha que já foi montada antes desta rodada, sem precisar
remontar. Escolher uma opção dispara o `onEdit`, que troca os treze hex de ANTES pelos treze de
AGORA em toda aba, fundo e fonte, em bloco (`getBackgrounds`/`setBackgrounds`,
`getFontColors`/`setFontColors` — rápido mesmo em milhares de células). O que já estava pintado
com outra cor, fora das treze, não muda.

> **⚠ A régua (a borda) fica de fora desta rodada.** *O Apps Script não lê cor de borda em
> bloco — só célula a célula —, e são cerca de 19 mil bordas na ficha inteira. Fundo e fonte
> cobrem quase tudo que se vê; a régua continua na cor de quando a ficha foi montada até isso
> ter um jeito mais rápido, talvez pela API avançada do Sheets, que pede uma ativação sua no
> projeto do Apps Script.*

**O Mizuki testou, e a caixa não nascia — achado e consertado em 18/09/2026.**
`configurarPaleta_` ancorava a caixa procurando a foto com `cart.getImages()`, que só enxerga
imagem **solta** sobre a grade (`OverGridImage`). Mas esta ficha nunca solta imagem — decisão do
Mizuki de 15/09/2026, registrada bem ali em cima em `montarAba_` (`Ficha.gs`) e conferida pela
linha "o molde põe a imagem na célula, e não solta": toda foto (a da CARTEIRA inclusive) entra
**dentro** da célula, com `newCellImage()`. Pra essa ficha `getImages()` sempre volta uma lista
vazia, `configurarPaleta_` caía direto no `'sem foto pra ancorar'`, e a caixa nunca aparecia —
nem no `construir()`, nem no `onOpen`. Os 16 validadores passavam porque nenhum roda a função de
verdade contra um Sheets, só leem o texto do arquivo — o mesmo motivo por trás do B18 e do B24.

*O conserto: uma função nova, `acharCaixaDaFoto_`, varre os **valores** da CARTEIRA
(`getRange(...).getValues()`, uma leitura só) até achar uma célula com `CellImage` — reconhecida
pela propriedade `valueType` igual a `SpreadsheetApp.ValueType.IMAGE` (é propriedade, não método;
o `verificar()` do `modelo.gs.js` já fazia essa leitura certa, `configurarPaleta_` que tinha o
jeito próprio e errado) — pega a mesclagem de quem achar, e usa a mais alta em linhas. Mesma
ideia de "a maior imagem da aba" de antes, só que medida em linha e não em pixel, porque sem
`OverGridImage` não tem pixel pra medir. `conferir-ficha-xlsx.py` ganhou duas checagens novas que
travam essa dupla — `acharCaixaDaFoto_` lendo `valueType`, nunca `getImages`, e
`configurarPaleta_` passando por ela — pra essa classe de bug não voltar calada.*

**Como é conferido.** *Todos os 16 validadores passam.* `conferir-ficha-xlsx.py` ganhou as duas
checagens novas de cima, mais a do `onEdit` reescrita pra usar o mesmo recorte de função que a
checagem vizinha já tinha — o jeito antigo media com um regex que parava no primeiro `}`, e a
caixa nova de CARTEIRA tem um `{ ... }` inline que acendia o alarme errado.

**O Mizuki testou de verdade (Kaori.xlsx, 18/09/2026) e trouxe três problemas — os três
consertados.**

1. *A caixa nasceu sem moldura.* `configurarPaleta_` nunca chamava `.setBorder(...)` — o rótulo e
   o valor só tinham fundo e fonte, nenhuma borda, enquanto toda caixa irmã (CAMINHO, NÍVEL, ...)
   fecha com moldura média na cor da régua. Comparado célula a célula contra `O17:O18` no
   `Kaori.xlsx`: as duas células da paleta agora levam `setBorder(true, true, true, true, false,
   false, '#8A7EC4', SOLID_MEDIUM)`, igual às outras.

2. *A fonte do valor estava errada.* Toda caixa de campo escreve a resposta em `Castoro` 15 — a
   paleta escrevia em `Roboto` 12, porque a função nunca olhou pra fonte das caixas irmãs antes de
   inventar a própria. Trocado para `Castoro` 15, e o rótulo também alinhado ao padrão real
   (`Oswald` 8, sem negrito, `texto_fraco` sobre `painel_alto` — não `texto` sobre `acento`, que
   era um estilo à parte que ninguém pediu).

3. *A cor não mudava nunca, em nenhuma escolha — nem "Noite · Escuro" pra ela mesma faria
   diferença.* Duas causas, as duas na mesma função: **(a)** a caixa da paleta é mesclada
   (`C24:K24`), e um edit numa célula mesclada devolve em `e.range` só a célula-âncora — o
   `aplicarPaleta_` comparava contra o endereço do range inteiro, que nunca bate, e voltava sem
   fazer nada. **(b)** mesmo consertando (a), o valor inicial gravado era `'Noite · Escuro'` — um
   tema de verdade do catálogo — e o `Noite` do catálogo saiu do `derivar.py`, que ajusta cada
   tema pro contraste WCAG e por isso os treze tons dele **não são mais**, em nenhum dos treze, os
   mesmos hex que a ficha usa de fábrica (`PALETA_DE_FABRICA_`, o que `montarAba_` grava desde que
   a ficha nasce). O "antes" do primeiro repaint buscava cor que a ficha nunca teve — `troca`
   saía vazio pra ficha inteira, não só pra caixa nova, e simulado em Node contra os dois
   catálogos isso bate: zero das doze cores de `Noite · Escuro` aparece em lugar nenhum da ficha
   de verdade. O valor inicial virou `'Escolha uma paleta'` — fora do catálogo, então
   `coresDoNome_` devolve null pra ele e o "antes" cai no `|| PALETA_DE_FABRICA_` que já existia,
   só que ninguém acionava. O menu também virou `allowInvalid(true)`, igual ao do Caminho e da
   Trilha — o valor inicial não é opção de verdade da lista, só convite.

> **⚠ Isso é análise de código, não teste no Sheets de verdade — de novo.** *Os três consertos
> acima saíram de comparar o `Kaori.xlsx` que o Mizuki mandou contra a documentação oficial do
> Apps Script (o jeito que `e.range` reporta célula mesclada) e de simular a troca de cor em Node
> com os dois catálogos de cor lado a lado — não de abrir uma planilha Google. Continua valendo
> testar ao vivo antes de considerar o B25 fechado.*

> **⚠ Na sua mão, e nesta ordem:** *cola o `Codigo.gs` novo por cima do antigo no editor do Apps
> Script. Se a caixa da paleta já existe numa ficha (criada pela versão anterior, com o bug),
> `configurarPaleta_` é idempotente e não vai reconstruí-la sozinha — apague o intervalo nomeado
> `PALETA_ESCOLHIDA` primeiro (Dados > Intervalos nomeados) antes de reabrir, ou rode o
> `construir()` de novo numa planilha nova. Depois, testa trocando a paleta umas duas ou três
> vezes seguidas, inclusive voltando pra uma que já usou — e confere as três coisas que voltaram
> erradas: a moldura da caixa, a fonte `Castoro` no valor, e a cor mudando de verdade em toda a
> ficha.* **A galeria com as 61 pra escolher visualmente está em**
> `https://claude.ai/artifact/Ht87g8xjbgsVkbdsse5bHm`.

**Segunda rodada de teste de verdade (`Kaori.xlsx`, manhã de 18/09/2026) — quatro problemas, dois
já iam para o commit consertados, um pedido de posição atendido, e um achado grande que fica
esperando decisão.**

1. *A caixa mudou de lugar.* Pedido do Mizuki: rótulo na linha 26, valor nas linhas 27-28 (duas
   linhas, não uma), caixa duas colunas mais estreita que a foto, sobrando à direita. `configurarPaleta_`
   media a partir do fim da foto (`caixaFoto.getLastRow()`) por deslocamento, não endereço fixo — só
   os deslocamentos mudaram: rótulo vai para `+5` (era `+2`), valor para `+6` com duas linhas de
   altura (era `+3` com uma), e a largura perde duas colunas (`caixaFoto.getNumColumns() - 2`).
   Continua andando sozinha se a foto mudar de novo.

2. *A borda não mudava de cor — e dava pra consertar sem ler célula por célula, ao contrário do
   que a v0.250 tinha registrado aqui.* A suposição de "19 mil bordas, uma leitura por célula"
   presumia que a cor da borda variava célula a célula, do jeito que fundo e fonte variam. Não
   varia: o script inteiro usa só duas cores de borda — a régua (`8A7EC4`) e um branco fixo de três
   trechos que não é régua e não deveria mudar de tema — e as duas já vêm inteiras do `ABAS`, a
   mesma lista que o `Ficha.gs` usa pra montar a ficha (lado, traço, cor, faixas, por aba).
   `repintarBordas_`, função nova, não lê nada: pega o `ABAS`, re-desenha toda faixa marcada com a
   régua velha na régua nova, e faz o mesmo na caixa da própria paleta (que não mora no `ABAS`,
   por nascer depois, em `configurarPaleta_`). Simulado em Node contra o `ABAS` de verdade: das 20
   faixas com régua no script inteiro, as 20 pegam a cor nova; as 3 do branco fixo, nenhuma.

   > **O Mizuki perguntou se são mesmo só duas, lembrando das cores diferentes no artefato da
   > galeria.** *São duas na PLANILHA — no `Kaori.xlsx` que ele mandou, contei toda borda de toda
   > aba, célula por célula, sem confiar no `ABAS`: `19.364` bordas na régua (`8A7EC4`) e `13` no
   > branco fixo (as três da CARTEIRA), nenhuma terceira cor em lugar nenhum — bate quase exato
   > com a estimativa antiga de "19 mil". As cores diferentes que ele viu são do artefato da
   > galeria (a peça HTML que mostra os 61 temas lado a lado): cada card ali usa a régua DAQUELE
   > tema como prévia — Blush mostra `CC0000`, Aquarela mostra `06C62A`, e por aí vai —, o que é
   > exatamente o que passa a acontecer na ficha de verdade depois do B25: a régua muda de cor
   > conforme o tema escolhido. Dentro de UM tema escolhido, a planilha inteira usa uma régua só.*

3. **O OSSO virou 14º papel — resolvido por PAPEL DE FUNDO, não por tema.** Decisão do Mizuki:
   sim, vira uma 14ª opção; e o pedido dele foi além — como o mesmo `OSSO` cai em cima de fundos
   diferentes dentro do MESMO tema (fundo, painel, painel_alto, menu_grande, acento — contados no
   `Kaori.xlsx`: **1505, 342, 254, 120 e 24 células**, nessa ordem, mais um punhado em papel/tinta),
   uma cor só por tema não bastava — exatamente o "muitas caixas usam degradê" que ele apontou.

   *Como ficou.* `derivar.py` ganhou `resolve_osso_por_papel`: pra cada um dos treze papéis de
   fundo, testa `TEXTO` e `TEXTO_FRACO` da própria variante contra aquele fundo (contraste WCAG,
   piso `4,5` — o mesmo do `TEXTO` normal); se nenhum dos dois cruza o piso, tenta os dois da
   variante oposta (escapa pro claro ou pro escuro, o que contrastar); se ainda assim nenhum
   cruza, fica com o melhor entre preto e branco puro — e qualquer caso que caia nesse último
   degrau entra em `PROBLEMAS`, pra alguém olhar. Rodado nos 61 temas (122 entradas × 13 papéis =
   1.586 combinações): **nenhuma caiu em `PROBLEMAS`** — todas acham um `TEXTO`/`TEXTO_FRACO` (da
   própria variante ou da oposta) que já cruza o piso, sem precisar do preto/branco de emergência.
   O resultado mora em `osso_por_papel` dentro de cada entrada do `PALETAS`, e o `Codigo.gs` ficou
   maior por causa disso (97 mil caracteres só nessa variável, ainda quebrada em linhas de até
   113 — bem longe do 1 MB do Apps Script).

   *`repintarPaleta_` agora lê fundo e fonte da mesma célula ao mesmo tempo* (antes eram duas
   passadas separadas): quando a fonte é `OSSO`, acha o papel do fundo ANTIGO daquela célula
   (papel não muda entre paletas, só o hex muda) e escreve o `osso_por_papel` da paleta NOVA pra
   aquele papel; toda outra fonte continua pela troca de sempre. Simulado em Node com os cinco
   papéis que o `Kaori.xlsx` realmente usa, saindo da fábrica pra `Mizuki · Claro`: as cinco
   combinações resultantes passam no mesmo contraste `4,5` — `painel_alto`, por exemplo, sai
   `#F5B7D4` de fundo com `#1E1320` de fonte, contraste `10,78`.

   > **⚠ Ainda é análise de código — o `Kaori.xlsx` mostrou o problema, mas o teste de verdade,
   > de novo, é reabrir a ficha e trocar de paleta ao vivo.** *A pergunta que ainda cabe: o osso
   > "de verdade" (a barra de vida, em `corDeEstado_`) não tem célula fixa própria — ele é só o
   > fundo/fonte padrão de qualquer campo de vida/energia/integridade que NÃO está em aviso. Com
   > o osso virando repintável, a barra de vida cheia passa a mudar de cor com o tema também (por
   > exemplo, escura em tema claro), e só o âmbar/vermelho do aviso continuam fixos. Se isso for
   > um problema — Mizuki queria a barra de vida cheia SEMPRE na mesma cor, tema nenhum — é outra
   > conversa, e essa eu não decidi sozinho: como ela usa o valor de OSSO só por estar em cima do
   > mesmo papel de fundo que todo o resto do texto, hoje não tem como distinguir uma célula da
   > outra sem mexer no gerador Python pra marcar essas células à parte.*

**Terceira rodada (manhã de 18/09/2026) — o crash explicado, e mais dois problemas.**

1. **O crash era o `Ficha.gs`, não o `Código.gs`.** O Mizuki confirmou: a aba do navegador
   fecha, o Apps Script fecha e a planilha recarrega, sempre poucos segundos depois de rodar
   `construir()` — batendo com a segunda suspeita, não a primeira. O `Ficha.gs` (gerado por
   `ficha/emitir_gs.py`, não escrito à mão) tinha **duas linhas** de verdade gigantes: o
   `var ABAS = [...]` inteiro numa linha de **256 mil caracteres**, e o `var ARTE = {...}` (a arte
   em base64) numa de **131 mil** — o `Código.gs` já tinha sido corrigido nessa frente, o
   `Ficha.gs` nunca. `emitir_gs.py` ganhou `_sem_linha_gigante`: desce um nível (lista vira uma
   linha por item, dicionário vira uma linha por chave) só quando o pedaço inteiro, compacto, já
   passaria de 2.000 caracteres — testei primeiro o `indent=2` do próprio `json`, que resolve a
   linha mas incha o arquivo (o ABAS sozinho foi para quase 900 KB, perto do limite de ~1 MB do
   Apps Script, por expandir até `[1,1,"",0]`); o corte por tamanho evita as duas pontas. A única
   coisa que **não** dá pra cortar assim é uma STRING sozinha maior que o piso — a arte em base64
   de uma imagem grande —, porque partir uma string no meio deixa de ser um valor JSON válido.
   Pra essas, o corte vira pedaços concatenados por `+` (ainda roda igual — o Apps Script lê
   `var ARTE = {...}` como código, não como JSON), e o `conferir-ficha-xlsx.py` cola os pedaços
   de volta (troca `"+"` por nada) antes de validar. O `Ficha.gs` de agora: **maior linha caiu de
   256 mil para 4.031 caracteres**, arquivo foi de 390 KB pra 487 KB — ainda bem longe do limite
   —, e os 16 validadores continuam passando.

2. **A caixa da paleta tinha o formato errado de novo.** O rótulo (linha 26) está certo — até a
   coluna I —, mas o valor (linhas 27-28) tinha a MESMA largura do rótulo; o pedido era o valor
   ir até a coluna M, dois além da largura da foto, não dois aquém. `configurarPaleta_` agora usa
   duas larguras: `largRotulo` (foto menos duas colunas) e `largValor` (foto mais duas). Como as
   duas caixas deixaram de ter o mesmo tamanho, o rótulo ganhou intervalo nomeado próprio
   (`PALETA_ROTULO`) — antes o `repintarBordas_` reconstruía o rótulo a partir do valor por
   deslocamento (`offset`), o que só funcionava enquanto os dois tinham a mesma largura.

3. **"As partes externas da ficha continuam sem pintar" — achado o motivo, e não era papel
   nenhum ficando de fora.** `getLastRow()`/`getLastColumn()`, que `repintarPaleta_` usava pra
   saber até onde ler cada aba, só contam célula com **valor** — confirmado direto na
   documentação do Google. A CARTEIRA tem 14 linhas (39 a 52) de fundo puro, sem nenhum valor,
   só cor — a extensão decorativa do cartão pra baixo —, e todas as outras abas têm sobra
   parecida. `getLastRow()` parava antes delas, então nunca entravam na leitura nem na troca:
   exatamente as bordas externas que ficavam pretas depois de qualquer troca de tema, em
   qualquer paleta. O conserto usa o tamanho que já existe pronto no `ABAS` (`spec.rows` e
   `spec.cols` — o mesmo que `montarAba_` pinta por inteiro quando a ficha nasce) em vez de
   perguntar pro Sheets onde ele acha que os dados acabam.

> **⚠ Ainda é análise de código — o crash em si eu não posso reproduzir aqui** (não abro Apps
> Script de verdade). *A contagem de linha e o `node --check` confirmam que o `Ficha.gs` não tem
> mais nenhuma linha nem perto do tamanho que travava antes; o resto (posição da caixa, pintura
> das bordas externas) é análise contra o `Kaori.xlsx` mais simulação em Node, não Sheets ao
> vivo. Continua valendo testar tudo de novo: colar os DOIS arquivos (`Ficha.gs` E `Código.gs`)
> atualizados, `construir()` numa planilha nova, e trocar de paleta olhando as bordas do cartão
> (linhas 39-52 da CARTEIRA) e não só o miolo.*

**Quarta rodada (manhã de 18/09/2026) — a caixa da paleta sobrevivia ao próprio `construir()`.**

O Mizuki testou de novo e mandou o `Kaori.xlsx`: fundo 100% certo em toda aba, sem sobrar nenhum
hex de fábrica em lugar nenhum — conferi célula por célula, zero. Bordas também: das 19.364
faixas na régua, todas viraram a régua nova, **menos 45** — e as 45 formavam um retângulo exato
em `C26:M28`, a caixa da própria paleta.

*O motivo: o intervalo nomeado da paleta sobrevive ao `construir()` apagar e recriar a
CARTEIRA.* O Google não documenta isso, mas testado (simulado em Node): quando a aba nasce nova
com o MESMO NOME ("CARTEIRA"), o intervalo nomeado antigo religa nela sozinho, mesmo a aba de
verdade sendo outra por dentro. `configurarPaleta_` só checava "o nome já existe e ainda aponta
pra algo vivo?" — e a resposta seguia sim, rodada após rodada, então a função nunca rodava de
novo pra valer. A caixa visível era a de uma versão **anterior** do `Codigo.gs` (linha 23/24 ou
26/28 com a borda ainda na régua velha), sobrevivendo por baixo de uma ficha inteira nova.

*O conserto:* `configurarPaleta_(ss, force)` ganhou o parâmetro `force`. O `construir()` (que já
decidiu apagar a CARTEIRA inteira) chama com `force=true` — remove o intervalo nomeado velho
incondicionalmente, exista ele válido ou não, e recria a caixa do zero, sempre. O `onOpen` chama
sem `force`, porque continua precisando ser idempotente: reabrir a ficha não pode apagar uma
paleta que o jogador já escolheu. Simulado em Node com um intervalo "antigo, mas ainda válido"
(o caso que o Google não documenta): sem `force`, a função corretamente NÃO mexe; com `force`,
remove os dois nomes e recria — confirmando as duas metades do conserto. `conferir-ficha-xlsx.py`
ganhou duas checagens novas pra essa dupla não se desalinhar de novo.

> **⚠ O crash que fecha a aba "logo após terminar de construir"** *continua sem explicação — o
> `Ficha.gs` já não tem linha gigante (a causa mais provável, corrigida na rodada passada), e
> dessa vez o `construir()` terminou e produziu o `Kaori.xlsx` certinho antes de fechar, então não
> travou o trabalho. Se continuar acontecendo depois desse conserto, o próximo passo é um print
> do que aparece na hora exata do fechamento (se aparece alguma coisa) — sem isso não tenho como
> saber se é outro arquivo grande, é o navegador redesenhando a planilha inteira de uma vez
> depois de milhares de células mudarem de cor, ou é outra coisa.*

**Quinta rodada — os dois motivos de verdade do "trava a partir da segunda troca", achados com
calma, sem pressa, exatamente como o Mizuki pediu.**

*O crash "fecha o Apps Script sozinho" saiu explicado antes de mais nada: navegador Brave, sem
crash report, sem tela de erro — a marca do Memory Saver do próprio Brave hibernando a aba sob
pressão de memória (confirmado depois, o Mizuki desligou e testou). Não é bug do script.*

Voltando ao foco pedido: **duas causas bem diferentes**, uma escondida atrás da outra.

1. **A repintura inteira não cabe em 30 segundos, e o Apps Script mata a execução no meio sem
   avisar ninguém.** `aplicarPaleta_` rodava dentro do `onEdit(e)` simples — que tem exatamente
   30 segundos de orçamento, sempre, sem exceção. Repintar fundo e fonte de ~29 mil células em 7
   abas, mais a régua, é trabalho de verdade, e o `paleta_atual` (a propriedade que guarda "qual
   tema está valendo agora") só é gravada no FIM de `repintarPaleta_` — uma execução morta no
   meio nunca chega lá. A troca seguinte compara contra um "antes" que não é o que está pintado
   de verdade, erra o alvo, e a partir daí cada troca nova erra mais um pouco. Isso explica os
   sinais que o Mizuki mandou: a CARTEIRA presa em "Mizuki · Escuro" mesmo com "Mizuki · Claro"
   selecionado, e depois com "Eucalipto · Claro" selecionado — a ficha nunca chegou a terminar de
   virar nem um nem outro, só ficou acumulando tentativas cortadas pela metade.

   *O conserto:* a troca de paleta saiu do `onEdit(e)` simples e ganhou um **gatilho instalável**
   próprio — mesma função `aplicarPaleta_`, só que citada fora do `onEdit(e)`, instalada uma vez
   por `configurarPaleta_` (idempotente, confere se já existe antes de criar outro). Gatilho
   instalável tem o orçamento normal, 6 minutos, não 30 segundos.

   > **⚠ Isso pede autorização nova.** *Criar gatilho é um escopo que o script não usava até
   > agora — na próxima vez que rodar `construir()` (ou qualquer função na mão) depois de colar o
   > `Codigo.gs` novo, o Google vai pedir pra autorizar de novo. É esperado, só aceitar.*

2. **Mesmo com tempo de sobra, a borda do resto da ficha só acompanhava a PRIMEIRA troca — nunca
   mais depois disso.** Bug achado direto no código, sem precisar do Sheets: `repintarBordas_`
   comparava `b[2]` — a cor ORIGINAL gravada no `ABAS`, que o `Ficha.gs` grava uma vez só e nunca
   muda depois, sempre `8A7EC4` — contra `deRegua`, a régua da paleta ANTERIOR. Isso só bate na
   primeiríssima troca (quando "a paleta anterior" ainda é a de fábrica, `8A7EC4`). Na segunda
   troca em diante, `deRegua` já é a régua de um tema de verdade — nunca mais `8A7EC4` —, a
   comparação nunca mais batia, e a borda do resto da ficha parava de acompanhar pra sempre. Só a
   borda da própria caixa da paleta continuava mudando, porque ela não faz essa comparação, só
   repinta direto — **exatamente** o "só mudou a borda do botão da paleta, o resto travou" que o
   Mizuki descreveu depois da troca pro Eucalipto.

   *O conserto:* `repintarBordas_` passou a comparar contra `PALETA_DE_FABRICA_.regua` — uma
   constante FIXA, a mesma sempre, não o "antes" de cada troca — porque toda faixa de régua do
   `ABAS` tem essa cor gravada, sempre, sem exceção. E `repintarPaleta_` passou a chamar sem
   comparar "mudou de verdade" antes: já que a comparação de dentro não depende mais de
   histórico, chamar sempre deixa a régua se autocorrigir sozinha, mesmo que uma troca anterior
   tenha ficado pra trás. Simulado em Node com duas trocas seguidas (Fábrica→Mizuki, depois
   Mizuki→Eucalipto): as mesmas cinco abas com régua pegam a cor nova nas duas vezes — antes do
   conserto, a segunda vinha vazia.

*Sobre a borda "branquinha" no `AK17` da FICHA e "sem borda" no `B4` do GLOSSÁRIO:* conferi as
duas células, e as duas — e toda borda das duas abas inteiras, sem exceção — vieram uniformes na
régua atual (`CB015E`) no `Kaori.xlsx` que o Mizuki mandou, sem anomalia nenhuma nos dados. A
explicação mais provável é a MESMA causa 1: o print foi tirado no meio de uma repintura que
ainda não tinha terminado (ou que já tinha morrido no timeout), mostrando um estado que o arquivo
exportado depois já não tinha mais. Vale conferir essas duas células de novo depois dos dois
consertos, numa ficha nova.

> **⚠ Pra testar isso direito: `construir()` numa planilha nova (ou apagando o intervalo nomeado
> velho, mas nova é mais simples), autorizar de novo quando o Google pedir, e trocar de paleta
> DUAS vezes seguidas** — a primeira já funcionava antes; é a segunda que prova os dois
> consertos.

**19/09/2026 — o Mizuki voltou: os dois consertos acima não bastaram.** Testando de novo, ele
garantiu que o `AK17` e o `B4` deram errado NA HORA do `construir()`, antes de qualquer troca de
paleta — descartando de vez a explicação 1 (print no meio de uma repintura) pros dois. E a
mudança de cor continuava travando depois de algumas trocas — "cores dos arredores das páginas
não estão mudando, o fundo da parte principal da carteira também não" —, com só o `GLOSSÁRIO` e o
`CATÁLOGO` acompanhando direito.

*Sobre a borda:* ele mandou dois arquivos — `Kaori.xlsx` e `Kaori_Sem Correção.xlsx` — pra eu
comparar. Os dois vieram **idênticos** nas duas células: `AK17` só com borda inferior (a mesma
dos vizinhos `AJ17`/`AL17`), sem branco nenhum; `B4` com as quatro bordas, incluindo a esquerda.
E a caixa da paleta, nos dois arquivos, ainda estava em `"Escolha uma paleta"` — nenhuma troca de
tema tinha acontecido ainda naquela exportação. Isso quer dizer duas coisas: (1) nos dados que
saíram do Sheets, a borda das duas células está certa, sem anomalia; e (2) esses dois arquivos
não servem pra testar o bug de cor, porque neles a paleta nunca foi trocada — o print que mostrou
a borda branca é de um momento que a exportação em xlsx não capturou. A suspeita que sobra, sem
poder tocar no Sheets ao vivo pra confirmar, é um soluço de redesenho do próprio Sheets (borda que
só atualiza na tela depois de um scroll ou de um F5) — não um dado errado.

*Sobre a cor travando — esse sim, achado e consertado.* Simulei a repintura inteira em Node, com
os dados REAIS de célula do `Kaori.xlsx` (fundo e fonte de toda `CARTEIRA`, `FICHA`, `INVOCAÇÃO`,
`GLOSSÁRIO` e `CATÁLOGO`, lidos direto do arquivo) passando pela função `repintarPaleta_` de
verdade, sem simulação de regra nenhuma — o código roda contra o dado como está. Rodando quatro
trocas seguidas, incluindo o `Eucalipto` que o Mizuki citou, sem nada interromper no meio: **zero
travamento**, as mesmas milhares de células mudam em toda troca. Isso prova que o ALGORITMO está
certo — o problema só aparece fora dele.

O que falta simular é o que o próprio Mizuki suspeitou: *"possivelmente por causa de tentar mudar
ao longo que a ficha já tá mudando"*. E ele tinha razão. **Nada no código impedia duas execuções
de `aplicarPaleta_` de rodar ao mesmo tempo** — o gatilho instalável (do conserto 1, ali em cima)
resolve o orçamento de tempo, mas não impede que uma SEGUNDA troca dispare antes da PRIMEIRA
terminar de escrever, se o Mizuki (ou eu, testando) trocar de tema rápido demais. `LockService`
não existia em nenhuma linha do projeto até este conserto.

Simulei a corrida direto: duas trocas partindo do MESMO estado (nenhuma sabe da outra), e a
escrita de cada aba chega intercalada — metade das abas fica com o resultado de uma troca por
cima, metade com o da outra, exatamente como acontece de verdade quando cada aba é uma ida e
volta HTTP separada ao Sheets. O resultado bate ponto a ponto com o relato: três das cinco abas
ficam com a paleta ERRADA na tela (a que "perdeu" a corrida para aquela aba especificamente),
enquanto a propriedade `paleta_atual` grava só o nome da paleta que "venceu" por último — nenhuma
das duas bate com o que está realmente pintado. Tentando uma TERCEIRA troca depois, normal, sem
pressa nenhuma: as três abas que ficaram com o resultado errado **não mudam mais nunca — zero
células, `fundoMudou=0`, `fonteMudou=0`** —, e as duas que por acaso bateram com `paleta_atual`
continuam funcionando perfeitamente. É o mesmo padrão do relato: algumas abas travadas, outras
não, e piora a cada troca nova que dispara em cima de uma anterior ainda rodando.

*Por que trava pra sempre, e não só uma vez:* `repintarPaleta_` só sabe repintar um hex batendo
CONTRA O ESPERADO de cada um dos treze papéis da paleta anterior (`papelPorHexAntes`) — não
existe "cor mais parecida", é igualdade exata de string. Uma célula com hex de uma mistura de
duas paletas não bate com o papel de paleta nenhuma, de tema nenhum, pra sempre — nenhuma troca
futura acha ela de novo. A borda não sofre disso porque `repintarBordas_` sempre mira um alvo
FIXO (a régua atual), não compara contra histórico nenhum; só fundo e fonte, que são
diferença-contra-o-antes, é que travam.

*O conserto:* `aplicarPaleta_` agora pega um `LockService.getDocumentLock()` antes de LER
`paleta_atual` — não só antes de repintar — e só solta depois de escrever o novo valor. Ler
antes do lock também travaria: a segunda execução podia ler um `paleta_atual` que a primeira
ainda não tinha escrito, e a mistura continuava possível mesmo com lock em volta só do repaint.
`tryLock(300000)` espera até cinco minutos (sobra um do orçamento de seis do gatilho instalável);
se a fila estourar isso, a troca é abandonada em silêncio — melhor que travar uma célula pro resto
da vida da ficha. `conferir-ficha-xlsx.py` ganhou duas checagens novas pra isso: que o lock existe
E que ele embrulha a leitura, o repaint e a escrita juntos, não só o repaint.

> **⚠ Se o `Kaori.xlsx` que o Mizuki está testando já tem célula travada de um teste anterior a
> este conserto, o lock sozinho não desfaz isso** — ele impede a mistura NOVA, não limpa a que já
> aconteceu. Pra testar limpo: `construir()` de novo (reconstrói tudo do zero, sem mistura
> nenhuma) antes de repetir o teste de trocar de tema.

**19/09/2026, segunda leva do mesmo dia — o Mizuki testou de novo, mesmo depois do lock: "nem
tudo está mudando" continuava, com só duas abas de sete acompanhando direito.** Ele mandou um
código antigo dele, de outra ficha, **não pra copiar** — só de referência, pra eu entender o
raciocínio. E o raciocínio dele era o certo: aquele código nunca compara contra "qual era a
paleta anterior" — ele monta UM mapa com a cor de TODAS as paletas de uma vez (`mapaCores`,
hex → índice do papel), e qualquer célula com QUALQUER dessas cores é reconhecida, não importa de
qual paleta ela veio.

*Por que o lock não bastava:* o lock impede uma corrida NOVA, mas não cura uma célula que já
ficou presa numa cor de paleta antiga — de uma corrida de ANTES do lock existir, ou de qualquer
outro motivo. `repintarPaleta_` só reconhecia uma célula comparando contra os treze papéis da
paleta IMEDIATAMENTE anterior (`papelPorHexAntes`); uma célula presa em uma cor de duas ou mais
trocas atrás nunca mais era achada, porque a busca só olhava um passo pra trás.

*O conserto, inspirado direto no código que o Mizuki mandou:* uma função nova,
`papelPorHexGlobal_`, registra o papel de cada hex nas 61 paletas inteiras (as 122 entradas) mais
a de fábrica — não só a anterior. `repintarPaleta_` agora confere PRIMEIRO contra a paleta
anterior (sem ambiguidade nenhuma, decide sozinha no caminho normal) e SÓ SE NÃO ACHAR cai nesse
mapa global — uma busca de resgate. Simulei a corrida de novo (duas trocas partindo do mesmo
estado, sem lock nenhum, pior caso possível) e testei uma terceira troca normal depois: antes
deste conserto, as três abas que tinham ficado com a paleta errada da corrida davam
`fundoMudou=0, fonteMudou=0` — travadas pra sempre. Com o mapa global, a MESMA terceira troca
repinta as três inteiras, igual a uma troca sem corrida nenhuma. A célula não precisa mais
"lembrar" de qual foi a última paleta — só precisa ter alguma cor de alguma paleta válida, e ela
volta a acompanhar.

*Uma ressalva honesta:* dos 1296 hex distintos que as 61 paletas usam, nove se repetem entre
PAPÉIS diferentes (ex.: `453636` é `painel_alto` em cinco temas escuros e `linha` no Sálvia
escuro) — pra esses nove, o mapa global escolhe um papel de forma arbitrária (o primeiro tema a
registrar aquele hex). Isso só importa pra uma célula que JÁ estava presa (a paleta anterior não
resolveu, senão a busca de resgate nem entra), e mesmo errando o papel por um desses nove, a
célula sai de uma cor errada pra uma cor VÁLIDA de algum papel — nunca mais fica parada de vez.
`conferir-ficha-xlsx.py` ganhou duas checagens novas pra isso.

*Sobre o `AK17` e o `B4` — reaberto, porque o Mizuki garantiu que é no `construir()`, não na
troca.* Fui atrás dos TRÊS lugares onde essa borda existe, de forma independente: a planilha viva
original que o Mizuki exporta do Sheets (`ficha-v01/original.xlsx` — atenção: desde o commit que criou
o GLOSSÁRIO ele já é uma exportação de ficha MONTADA, com o GLOSSÁRIO dentro, e não o desenho puro; ver o
comparador, abaixo), o `ABAS` que o gerador Python extrai dela, e o `Kaori.xlsx` que saiu do
`construir()` de verdade. **As três concordam, sem exceção:** `AK17` tem só a borda de baixo — e
isso não é exclusivo dela: a linha 17 INTEIRA da área de atributos (de `AG17` a `AP17`, nove
células) tem exatamente essa mesma borda "só embaixo", uma linha divisória entre o rótulo do
atributo (linha 16, com `FOR`/`DEX`/`CON`/`INT`) e a caixa de baixo (linha 18/19, `ESS`) — não é
AK17 sozinha que está diferente, a fileira inteira é assim por desenho. E o `B4` do `GLOSSÁRIO`
tem as quatro bordas nas três fontes, igual a TODOS os outros títulos de seção da mesma aba
(`PERÍCIAS`, `OFÍCIOS`, `ATRIBUTO`, `CONCEITOS` — todos com o mesmo box de quatro lados). Não achei
nenhum dado errado em lugar nenhum da cadeia.

Pesquisei na internet por esse padrão específico — borda de célula MESCLADA que sai errada na
tela depois de um `setBorder()` — e achado relatado é exatamente esse: sem um `SpreadsheetApp.flush()`
no meio, a fila de operações do Apps Script pode ficar represada, e a TELA (não o dado) mostra um
estado que já não é o que foi escrito por último. O `construir()` inteiro — mesclar, pintar
fundo, pintar borda, em sete abas — não tinha UM flush() sequer até o fim da função inteira.
Não é prova (não consigo abrir o Sheets pra ver a tela travada de verdade), é uma tentativa
dirigida, de custo baixo: um `SpreadsheetApp.flush()` a mais, uma vez por `construir()` (não por
aba), logo depois que as sete abas terminam de nascer — mesclagem, fundo E borda das sete já
commitados — e antes de fórmula/menu/índice começarem.

> **⚠ Se isso não resolver, o próximo passo já está definido: pedir um F5 na aba do Sheets logo
> depois do `construir()` terminar (sem trocar de paleta nem tocar em mais nada), e comparar a
> borda de `AK17`/`B4` ANTES e DEPOIS do F5** — se a borda mudar só com o refresh, é 100%
> renderização e não dado; se continuar igual, sobra a hipótese de algo na ordem de escrita que
> ainda não achei olhando o código parado.

**Sobre o terceiro print, o erro `TypeError: Cannot read properties of null (reading 'getRange')`
em `indice @ Código.gs:18`:** esse é um erro DIFERENTE do "a aba fecha sozinha" — é uma mensagem
de erro limpa, o que quer dizer que a aba NÃO travou, ela rodou e avisou o motivo. `indice()` lê a
aba `DADOS` (`SpreadsheetApp.getActive().getSheetByName('DADOS')`) — se ela devolve `null` na
linha 18, é porque a aba `DADOS` não existia NAQUELE momento. O seletor de função no topo do
editor, no print, mostra **`indice`** selecionado — e `indice()` sozinha só funciona numa ficha
que já passou pelo `construir()`; rodada numa planilha nova ou no meio de uma reconstrução (depois
que o `construir()` apaga as abas velhas e antes de terminar de criar as novas), `DADOS` ainda não
existe, e ela quebra exatamente assim. Dentro do PRÓPRIO `construir()`, `indice()` só é chamada na
linha 66 do `modelo.gs.js`, DEPOIS que as sete abas (`DADOS` inclusive) já nasceram — não achei
um jeito de `construir()` disparar esse erro sozinho. **Vale conferir se o seletor estava mesmo em
`indice` e não em `construir()` no momento do clique** — se estava, é engano de qual função rodar,
não bug; se o seletor JÁ estava em `construir()` e mesmo assim caiu nesse erro, isso seria uma
pista nova e bem mais séria, que eu ainda não expliquei.

*Sobre o crash crônico da aba do Apps Script fechando:* pesquisei por relatos parecidos. A
execução do Apps Script roda no SERVIDOR do Google, não no navegador — fechar ou travar a aba não
para o `construir()` no meio; é por isso que o `Kaori.xlsx` sai certinho mesmo quando a aba
"morre" durante a execução, como o PENDENCIAS já registrava antes. O que os relatos apontam como
causa comum, além do que já foi descartado aqui (linha gigante, Memory Saver do Brave), é o
próprio EDITOR (o painel de código, não a execução) engasgando com projeto grande enquanto o
"Registro de execução" fica atualizando — não achei um relato específico que bata 100% com este
caso. Recomendo, da próxima vez que acontecer: abrir o painel de **Execuções** (o relógio, na
barra lateral esquerda do editor, separado do "Registro de execução") depois que a aba voltar, e
ver se o `construir()` aparece lá como CONCLUÍDO — se aparecer, o problema é só a aba travando
durante a espera, não a montagem em si, e dá pra ignorar com segurança.

Sources:
- [Apps script stops working every day until resaved](https://support.google.com/docs/thread/203065819/apps-script-stops-working-every-day-until-resaved?hl=en)
- [Troubleshooting | Apps Script | Google for Developers](https://developers.google.com/apps-script/guides/support/troubleshooting)
- [Apps Script's new V8 runtime | Google Workspace Blog](https://workspace.google.com/blog/developers-practitioners/data-processing-just-got-easier-apps-scripts-new-v8-runtime)
- [Merged Cells not showing up correctly when creating Web in Apps Scripts](https://support.google.com/docs/thread/324146308/merged-cells-not-showing-up-correctly-when-creating-web-in-apps-scripts?hl=en)
- [Apply multiple different border styles to a cell](https://groups.google.com/g/google-apps-script-community/c/vCKNYuD5fmw)

**19/09/2026, terceira leva — o Mizuki testou e as cores "estão entrando bem"; sobraram o glossário,
o tinta, a legibilidade e três detalhes.** O que ele confirmou: o ORIGEM saiu certo e o aviso vermelho
"ficou ótimo". O que apontou: o glossário seguia sem borda esquerda, o `tinta` (o cartão da CARTEIRA e
a lombada das outras abas) não acompanhava a paleta, e em várias caixas a fonte era escura sobre fundo
escuro. Tudo abaixo foi conferido contra dado, não contra impressão.

1. **O ORIGEM e o GLOSSÁRIO agora se corrigem NA FONTE, e não só no `Ficha.gs`.** Regerei o `Ficha.gs`
   pela pipeline de verdade (`ficha-v01/monta.py`) e comparei com o arquivo que eu vinha emendando à
   mão: idênticos, fora o ORIGEM — então a pipeline é confiável, e um conserto só no `Ficha.gs` morreria
   na próxima regeração. Módulo novo, `ficha-v01/correcoes_borda.py`: dá à caixa ORIGEM, célula a célula,
   a borda da CAMINHO (as duas têm dez colunas; a borda branca fina era engano de formatação manual).
   A exceção que eu tinha posto no `conferir-ficha-xlsx.py` saiu, porque agora o `.xlsx` gerado e o
   script concordam sozinhos. **Glossário:** o título da página ("O GLOSSÁRIO") saía sem a borda da
   esquerda porque o CATÁLOGO, de onde o estilo vem, guarda a ponta esquerda do título numa célula à
   parte (`C1:C2`, com borda própria) e o `glossario.py` copiava só o canto (top+bottom). Ganhou a
   borda esquerda em `glossario._estilo_com_borda`. Antes eu tinha dito que "o CATÁLOGO também não
   tem" — vale a correção: em dado ele não tem NO canto, mas tem na célula ao lado, e é isso que se vê.

2. **O âmbar de texto padrão agora segue a paleta.** São seis células (o "sobrou ponto" da INVOCAÇÃO, o
   "MORRE DE VEZ", o "A CD DOS EFEITOS DELA", o "O QUE O ORÇAMENTO NÃO COMPRA"). O âmbar de ESTADO da
   vida/energia/integridade continua fixo (decisão A5, é regra condicional). Medido: o acento cru da
   paleta só garante 3,3 contra fundo e painel, e essas células moram em painel e painel_alto — abaixo
   de 3,0 em 45 de 244 combinações. Por isso o `derivar.py` ganhou `aviso_por_papel` (acento mantido se
   cruza 4,5, senão só a luminosidade ajustada, mesmo matiz). No `Codigo.gs` as células são achadas pelo
   ENDEREÇO no `ABAS` (`celulasDeAviso_`), e não pela cor — depois da primeira troca a fonte delas já não
   é âmbar, e uma busca por cor não acharia elas de novo.

3. **O `tinta` é pastel nos temas claros.** O `tinta = com_luz_carater(escura, 0.06, 0.50)` da rodada
   passada fez o tinta escuro ganhar matiz, mas ele seguia ESCURO nos claros — a CARTEIRA e as lombadas
   saíam marrons no "Brasa · Claro", no meio de uma ficha pêssego. Nos claros ele agora é um pastel do
   mesmo matiz (`L=0.94`, saturação ≥ 0,55, um degrau abaixo do fundo); nos escuros continua o quase
   preto de antes. `texto/tinta` entrou nas medidas do `derivar.py` (piso 4,5): as 122 passam.

4. **Legibilidade — o "problema grande".** Cada cor era trocada pelo SEU papel, e nenhuma checagem olhava o
   PAR: no claro o `texto` e o `texto_fraco` viram escuros, e o `acento` escuro do Brasa Claro é fundo
   de barra de título ("PERÍCIAS", "9 de 23 na criação") — fonte escura em fundo escuro. Agora, depois
   da troca de papéis, cada célula passa por `fonteLegivel_`: se o par novo lê pior que o par de FÁBRICA
   da mesma célula (`contrasteDeFabrica_`, lido do `ABAS`, sem histórico), a fonte vira uma cor DA
   PALETA que leia (texto, texto_fraco, linha, bloco, acento, papel, fundo, painel, tinta, da variante
   nova e da oposta), a que mais se aproxima do contraste do desenho; branco e preto puro só por último,
   com penalidade — o Mizuki disse que não se obriga a usar preto e branco. Piso de 3,0 pro texto que
   nasceu discreto (o "caminho" em `AH38`, com 2,0 na ficha de fábrica, e a lombada girada: o Mizuki
   disse que "se perdem no fundo"), teto de 4,5 pro resto. Simulado nas 122 entradas a partir do estado
   de fábrica exato (montado do `ABAS`): **1.309 células de texto piores que o desenho sem a rede, 0 com
   ela; 459 abaixo de 3,0, 0 com ela.** Cadeia de 6 trocas (Brasa Claro → Mizuki Escuro → Noite Claro →
   Eucalipto Escuro → Sálvia Claro → Brasa Claro): 0 células ilegíveis em cada passo, fundos idênticos
   ao caminho direto da fábrica, 15 fontes diferentes (deriva de papel, todas legíveis). Depois de uma
   corrida entre duas trocas + uma terceira normal: 0 fundos diferentes, 0 ilegíveis. Exemplo, Brasa
   Claro: "ATRIBUTOS" sobre a barra `740A03` passa de `E8DCD4` (contraste ~1,5) pra `FCEAE3` (10,1); a
   nota da barra, pra `FAB4B2` (6,8).

5. **A lombada da FICHA ia até a linha 144 de 150** (e a da INVOCAÇÃO até a 120 de 126). Na ficha de
   fábrica não se via, porque o tinta e o fundo escuros quase não se distinguem; numa paleta clara a faixa
   aparecia cortada. Estendida em `correcoes_borda._lombada_ate_o_fim`, e o emissor deixou de dar as duas
   linhas de folga embaixo dessas duas abas (`emitir_gs.py`), porque uma folga que nenhuma célula pinta
   fica com o fundo comum — o tamanho das abas não mudou (150 e 126).

6. **Caixinha de espera embaixo da paleta.** Uma linha do tamanho do menu, logo abaixo dele ("Aguarde de
   30 a 40 segundos para ver o tema inteiro — depende do tema."), com intervalo nomeado próprio
   (`PALETA_AVISO`) pra a borda dela ser repintada junto com a régua. O prazo saiu do que o Mizuki
   observou testando; eu não medi. Começou em "20 a 30" e virou "30 a 40" na primeira rodada no Sheets
   (19/09/2026), quando ele cronometrou 30 a 40 s.

7. **A arte não troca de cor com a paleta, então foi feita pra ler nos dois extremos.** Medido nos dois
   prints: o miolo da moldura da foto era `12101D` nos dois temas (a imagem tinha um miolo roxo-escuro
   quase opaco — `gera.moldura` agora aceita `fundo`, e a moldura sai SEM miolo: o fundo da célula, que
   segue o tema, aparece); a pincelada clara do meio, `E0D0D0`, sumiria inteira no tinta pastel — virou
   um meio-tom (`826E6C`, luminância 0,17, que dá o mesmo contraste, 4,0, contra o tinta escuro e contra o
   pastel). A pincelada de cima (`706080`) e os selos vermelhos já eram meio-tom e ficaram.

> **⚠ Nada disso foi testado no Sheets.** Os validadores (`conferir-ficha-xlsx.py`, com 10 checagens novas
> nesta leva) e as simulações em Node passam, mas a tela é o Mizuki quem vê. O que olhar primeiro: (a) o
> "Brasa · Claro" na CARTEIRA, no GLOSSÁRIO e na INVOCAÇÃO; (b) a lombada da FICHA até a linha 150; (c)
> a borda esquerda do título do GLOSSÁRIO; (d) o tempo real da troca, que decide se a caixinha diz a
> verdade. E `construir()` de novo antes — as bordas, a lombada, a arte e a caixinha nascem no
> `construir()`, não na troca.

**19/09/2026, quarta leva — o erro do `PALETA_AVISO`, a fonte da caixinha, o comparador vermelho e a inicial
minúscula.** O Mizuki confirmou que as cores estão mudando por completo, que as fontes leem bem e que a
borda do glossário mudou; algumas imagens ficam "meio perdidas", mas funcionais. Sobrou isto:

1. **`construir()` caindo com "O intervalo "PALETA_AVISO" não existe." dentro do `acharCaixaDaFoto_`.** O erro
   era meu, da caixinha de espera: `configurarPaleta_` chamava `ss.removeNamedRange(...)` às cegas, dentro de
   `try/catch`, pra os TRÊS nomes. O Spreadsheet Service não estoura na hora num nome que não existe: enfileira a
   operação, e o erro aparece na PRÓXIMA leitura (o `getValues()` do `acharCaixaDaFoto_`), fora do `catch`. Os dois
   nomes antigos só passavam porque já existiam de uma rodada anterior; o `PALETA_AVISO` era novo, e uma planilha
   NOVA, sem nenhum dos três, teria caído igual. Agora `removerNomesDaPaleta_` lista `ss.getNamedRanges()` e remove
   só o que existe. Provado em Node com um simulador que reproduz o comportamento adiado: o código antigo repete
   exatamente o erro do print (planilha nova e "só os dois antigos"); o novo passa nos três estados (nenhum nome,
   dois, os três) e cria os três. `conferir-ficha-xlsx.py` ganhou uma checagem que proíbe `removeNamedRange` às
   cegas. **A fonte da caixinha caiu de 9 pra 7** (o texto de 68 caracteres passava da largura do menu).

2. **O `comparar-ficha-01.py` estava vermelho com 5.551 diferenças, e eu tinha deixado de lado sem entender.** Na
   rodada passada eu disse que "já falhava antes" e não mexi — foi pressa: um validador que nasce vermelho não
   protege nada, e eu ainda somei ~68 diferenças minhas (ORIGEM e lombada) sem declarar. A causa: o
   `original.xlsx` deixou de ser o desenho puro do Mizuki no commit `5b44c99` (o mesmo que criou o GLOSSÁRIO) e passou a
   ser uma exportação de ficha MONTADA — com o GLOSSÁRIO dentro, com as duas linhas de folga que o script pinta, com a
   DADOS_INV pintada célula a célula, e com o estado da personagem que ele jogava. O comparador cobrava tudo isso
   como defeito do gerador. Separei o joio: **GLOSSÁRIO** sai da comparação célula a célula (o próprio `glossario.py`
   já dizia que o comparador "sabe" que ela não tem original — mas o `for` não sabia); **célula vazia só com o formato
   de corpo** e **célula com o fundo de base** (o script pinta a aba antes de escrever qualquer célula); as
   limpezas 15 a 20 declaram o que é meu (ORIGEM, lombada, inicial maiúscula) e o que é estado de jogo (a Origem do
   Kaori, duas caixas de seleção marcadas, o resultado solto de fórmula matricial, o embrulho `DUMMYFUNCTION` e a
   cauda de aspas que ele infla a cada ida e volta pelo Sheets); e a condicional de aviso vermelho da FICHA sai porque
   o `construir()` a refaz inteira (`corDeEstado_`). Resultado: **5.619 → 0**, e os 50 textos capitalizados batem
   exatamente com as 50 células que o gerador mudou. **Teste de mutação:** estraguei o `.xlsx` gerado de 7 jeitos
   (fundo de caixa com valor, borda da CAMINHO, texto de rótulo, alinhamento de caixa vazia de digitar, fundo de
   célula vazia não-base, fonte Arial numa célula vazia, fundo da barra de vida) — o comparador pega os 7. O último
   escapava por uma frouxidão que já existia na regra das barras "agora" (ela engolia qualquer diferença da célula,
   não só o valor); apertei. **Um resíduo, fechado em 19/09/2026:** `X11` (a Origem) estava numa lista fixa de UMA
   célula (`ESTADO_DA_PERSONAGEM`). Agora o endereço sai do rótulo `ORIGEM` da FICHA (o valor mora na linha de baixo), e o
   comparador para com mensagem se o rótulo não aparecer exatamente uma vez. Mutação: apontar pra célula errada faz o
   comparador acusar `FICHA!X11`.

3. **Inicial minúscula em texto curto da INVOCAÇÃO e do CATÁLOGO.** Módulo novo, `ficha-v01/correcoes_texto.py`
   (50 células): a primeira letra sobe em texto digitado ("técnica", "capítulo 16", "prende o alvo", as descrições
   do CATÁLOGO) e nas mensagens que as fórmulas da INVOCAÇÃO devolvem ("Sobrou ponto", "Estourou o total", "Estourou o
   teto de 6", "Ok", "Cada um dos cinco rola isto", "Custa … PE e a Ação Padrão"). A notação de dado ("d20 +") fica
   minúscula. Conferido antes: nenhuma fórmula nem script compara contra esses textos. A etiqueta do GLOSSÁRIO
   ("Capítulo 1 · 2 · 13") tinha o mesmo defeito e foi junto. **A ficha de invocação solta** (`ficha-invocacao/constroi.py`) ficou de fora
   nessa rodada, porque emitia as mensagens em minúscula e o `regressao-invocacao.py` testava exatamente essas. **Fechado
   em 19/09/2026, decisão do Mizuki: capitaliza nas duas.** O `constroi()` passou a rodar, no fim, a mesma
   `correcoes_texto.corrige_valor` da ficha principal (carregada por caminho) sobre a INVOCAÇÃO e o CATÁLOGO: 44 textos
   digitados e as mensagens das fórmulas. A DADOS fica como está. Seis asserções do `regressao-invocacao.py` passaram a
   esperar `Ok`, `Estourou o total`, `Estourou o teto de N`, `Estourou`; o `conferir-invocacao.py` aceita as duas formas
   da primeira letra ao comparar o texto do catálogo com o `invocacao.json` e ganhou duas checagens (nenhum texto abre em
   minúscula, e as mensagens das fórmulas abrem em maiúscula). Mutação: com a passada desligada, as duas acendem.
   Passam o `conferir-invocacao.py` (209), o `regressao-invocacao.py` (138, recalculadas no LibreOffice) e o
   `arnes-invocacao.py` (30 perturbações).

> **Visto no Sheets em 19/09/2026 (primeira rodada de teste):** o `construir()` terminou sem erro e sem fechar; a
> caixinha na fonte 7 lê nos dois temas (contraste medido no print, `14:1`); a CARTEIRA em Brasa Claro e Eucalipto
> Claro repinta fundo, borda (`2 px` nos dois), fonte e as imagens (kanji do cabeçalho, as duas pinceladas, o selo, a
> moldura da foto); a divisória aparece embaixo do cabeçalho. **O tempo da troca foi de 30 a 40 s**, e a caixinha
> passou de "20 a 30" para "de 30 a 40 segundos" (o texto só muda na planilha viva digitando na célula ou rodando o
> `construir()`, porque o `onOpen` não refaz uma caixinha que já existe). A borda saiu na tela com um desvio de cor
> nas cores fortes (Brasa `CC3500` → `C04217`, Eucalipto `5EA12B` → `699E34`); o controle é o retângulo de seleção do
> próprio Sheets, `#1a73e8`, que o print também mostra deslocado (`#4374E6`), e o código põe a régua na borda sem
> transformação. Só a CARTEIRA teve print. FICHA, GLOSSÁRIO, INVOCAÇÃO e CATÁLOGO foram conferidos pelo Mizuki a olho,
> que respondeu "tá certinho", e essa parte do registro é palavra dele, não medida minha.

**19/09/2026, quinta leva — a arte muda de cor com o tema, e uma divisória entre a moldura e o miolo.** O Mizuki
testou o Eucalipto Claro: as cores e as fontes estão certas, mas as imagens (pinceladas, moldura da foto, selo,
gotinhas) seguiam roxas e vermelhas numa ficha toda verde. E a moldura (cabeçalho e lombada, em tinta) e o miolo
(em fundo) viraram dois pastéis quase iguais, sem nada entre eles.

1. **A arte recolore com a paleta.** Imagem não troca de cor sozinha, e guardar uma versão por tema não cabe (6
   imagens × 122 = mais de 5 MB, e o projeto passa de 1 MB). Mas toda a arte da ficha é de UMA cor — o que varia é
   o alfa (a textura do pincel, o desgaste do selo) —, então o emissor (`emitir_gs.py`) passou a escrever cada uma
   como **PNG de paleta**: 256 entradas iguais, o índice do pixel é o próprio alfa, e a `tRNS` é a rampa 0..255
   (metade do tamanho do RGBA, e o `Ficha.gs` caiu de 498 KB pra 427 KB). Recolorir é reescrever os 768 bytes da
   paleta e refazer o CRC do bloco (`pngComCor_`, no `Codigo.gs`): milissegundos, nenhum pixel tocado. Uma trava
   no emissor recusa achatar uma imagem que tenha mais de uma cor de verdade. **Quem segue quem:** pinceladas de
   cima e moldura da foto seguem o `bloco` (discretas); a pincelada clara do meio, o `acento`; o selo e as
   gotinhas, a `régua` (a cor mais saturada do tema). A cor é escolhida pelo mesmo `fonteLegivel_` das fontes,
   contra o fundo que a célula da imagem tem DEPOIS da troca (piso 3,0). **A foto do jogador é protegida:** o
   `construir()` marca cada imagem nossa com o título de alt `PM-ARTE:<arquivo>` (e a descrição guarda a cor
   atual, pra não reenviar imagem que já está certa), e a troca só toca em imagem com esse título — a foto que o
   jogador pôs no lugar da moldura não tem. Testado: nas 122 paletas, 732 de 732 imagens recoloridas, 0 erros, pior
   contraste imagem×fundo 2,74; repetir a mesma paleta não reenvia nada; com uma foto de jogador no lugar da moldura,
   ela não é tocada. **`regressao-arte.js`** (novo, no node, ligado ao `conferir-ficha-xlsx.py`) confere cada uma
   das 6 imagens com um parser de PNG e um CRC-32 próprios: bloco a bloco o CRC bate, as 256 entradas viram a cor
   pedida, e IHDR/tRNS/IDAT saem byte a byte iguais (o alfa não mexeu). Mutação: um bit errado no CRC e uma
   paleta só meio preenchida — o teste pega os dois. A existência de `setAltTextTitle`/`getAltTextTitle` foi
   conferida na documentação do Google (`CellImageBuilder`/`CellImage`).

2. **Divisória entre a moldura e o miolo**, na cor da régua e no traço médio das outras bordas (a régua só tem 1,8
   de contraste contra o fundo — num traço fino ela sumiria; se pesar, é a constante `DIVISORIA_TRACO` em
   `correcoes_borda.py`). Onde passa: FICHA — embaixo do cabeçalho (linha 5, da coluna C pra direita) e à direita
   da lombada (coluna B, da 6 até a 150); INVOCAÇÃO — à direita da lombada, de cima a baixo; CARTEIRA — embaixo do
   cabeçalho (linha 4). Nasce no gerador, então o `construir()` já a desenha e a troca de paleta a repinta com a
   régua (ela entra no mesmo `bordas` do `ABAS`). O comparador declara as 365 células que ela toca, incluindo o
   perímetro dos blocos mesclados; o validador prova por expansão de faixa que ela cobre a moldura inteira.

> **Uma linha preta que eu NÃO expliquei — o Mizuki conferiu a lista em 19/09/2026 e respondeu que está certa, então
> o registro trata como fechada e reabre se ela voltar.** No print da FICHA (Eucalipto Claro) há uma linha de 1 px em
> `#000000` exatamente no limite entre a moldura e o miolo (`y=200` e `x=103` no print). Medi os pixels: é preto
> puro, só na FICHA (a CARTEIRA não tem). Não vem de borda nenhuma dos dados (todas as bordas do script são a
> régua), o `.xlsx` exportado não tem painéis congelados, e nenhum código põe preto ali. Na ficha escura ela
> sumia contra o tinta escuro. A minha suspeita é o **divisor de congelamento do Sheets** (linhas e colunas
> congeladas até a 5 e a B) — se você congelou à mão, é isso, e não é recolorível. Confere em Ver → Congelar. Se
> for isso, a divisória nova fica bem ao lado dele.

**25/09/2026 — numa cópia da ficha a cor não trocava; na original, trocava.** Achado do Mizuki, com a
original e a cópia exportadas (as duas `.xlsx` saíram iguais, célula a célula: o defeito era do script).
"Arquivo › Fazer uma cópia" leva o `Codigo.gs`, mas **não leva gatilho instalável** — ele é de quem o criou —, e o
`onOpen` da cópia, sem autorização, não consegue criar outro. A primeira saída (um menu "Ativar a troca de paleta",
uma vez por cópia) ele recusou: *"queria q só de copiar já funcionasse"*. O código antigo dele fazia tudo no
`onEdit` simples e cabia nos 30 s porque só mexia em fundo e fonte; o nosso também repinta a arte e a régua.

*O esquema:* a troca voltou pro gatilho simples, em passos (a cor de cada aba visível, a régua de cada aba, e cada
imagem da arte por último — 16). Antes de cada passo o `convergirPaleta_` confere se ele cabe no orçamento de 25 s
pelo tempo que o mesmo passo levou da última vez (medido e guardado na planilha), e cada passo termina com
`SpreadsheetApp.flush()`, senão o Sheets só executa a escrita na leitura seguinte e o tempo cai no passo errado. O
que não cabe continua no próximo clique (`onSelectionChange`, também gatilho simples). Nada pede autorização. O
gatilho instalável velho da original se apaga sozinho na primeira troca.

*As medidas dele (12:17 e 12:18):* a troca inteira somava ~32 s em duas execuções — cores 15 a 18 s, régua 7 s,
arte 7 a 9 s; o JS, medido no node, ~100 ms por aba: o tempo é todo do Sheets. *"exigir isso do usuario é meio
chato"*. O primeiro corte que ele aprovou — **as cores partirem da ficha de fábrica, sem ler a planilha** — foi
medido (versões d e e, 12:55 a 13:06) e **ficou mais lento**: a FICHA foi de 4,8 s para 7,6 a 9,0 s, e medindo por
dentro, ler custa pouco e o que pesa é **gravar**, ~0,5 ms por célula em cada gravação (a FICHA grava o fundo em 3,6 s
e a fonte em 3,9 s). Desfeito: a troca voltou a ler, e **a cor pintada à mão pelo jogador volta a ficar**. Antes de
desfazer, a versão de fábrica foi conferida contra o `repintarPaleta_` antigo nos 122 temas (igual) e contra o
`Kaori.xlsx` dele (fundo igual em toda célula; fonte em 12 de ~20 mil, que eram caminho do antigo).

*O que ficou (versão f), pelo pedido dele* — *"ele so troca as cores e as bordas, menos com as imagens, e ai ele
finaliza; as imagens ele dá start dnv caso alguém mexa na ficha"*:

- a troca vai **aba por aba, cor e régua juntas**, começando pela que o jogador está olhando (a CARTEIRA, onde a
  caixa mora), depois a FICHA; a arte vai por último. Com os tempos dele, cor e régua de todas somam 22 a 25 s,
  colado no orçamento: o que sobrar é de uma aba que ele não está vendo;
- **nenhum aviso**: o que sobra termina na próxima vez que alguém mexer na ficha — clique ou edição —, e **a aba em
  que ele clica passa na frente**, então abrir uma aba atrasada a pinta primeiro;
- passo ainda não medido (a primeira troca de uma cópia) usa uma estimativa pelos tempos dele, e não mais 6 s fixos;
- a caixinha diz "O tema leva uns 20 segundos. O que faltar termina enquanto você usa a ficha.", e o
  `verTemposDaPaleta` mostra cada passo de cor por dentro (lê, conta, grava fundo, grava fonte).

*Conferido:* o `regressao-paleta.js`, com o custo calibrado pelos tempos dele, prevê a troca fazendo cor e régua
das cinco abas numa execução de ~25 s e a arte no clique seguinte; com o Sheets 40% mais lento, sobram a INVOCAÇÃO e
o CATÁLOGO, e clicar numa delas a pinta primeiro; três vezes mais lento, nenhuma execução passa de 30 s, e nunca
aparece aviso.

*Medido no Sheets (versão f, 13:25 e 13:27) — "funcionou":* cor e régua das cinco abas na execução da troca, 24,7 s
e 22,9 s (cores 18,4 e 17,8 s, régua 6,3 e 5,1 s); a arte, 7,6 e 7,0 s, no clique seguinte, sem aviso. O "do começo
ao fim" do relatório (46 e 58 s) conta a espera até o clique. Ele viu as cópias mais lentas, mas funcionando. **Fica
colado no orçamento de 25 s:** num dia lento, a última aba (o GLOSSÁRIO) passa pro clique seguinte, calada. Se um dia
precisar de folga, o corte é gravar menos célula (hoje a fonte é gravada na aba inteira, e só a célula com texto
precisa).

### B26 · A Ficha Pessoal — **FEITA em 01/10/2026, e montada no Sheets pelo Mizuki no mesmo dia; o retorno dele é o B27**

*Pedido do Mizuki em 30/09/2026: a aba de pertences e histórico do personagem. O desenho foi fechado com ele por
estudo, em dezoito rodadas, antes de qualquer linha de gerador (`mockup/ficha-pessoal-estudo.html`).*

**A aba `FICHA PESSOAL` nasce no gerador, entre a `FICHA` e a `DADOS`.** *Como o `GLOSSÁRIO`, ela não tem planilha
viva por trás: é o `ficha-v01/ficha_pessoal.py` (a limpeza 22). São 87 linhas e 72 colunas: a folha vai de `A` a `AU`, com a largura de coluna, o cabeçalho e a lombada da `FICHA`, e
o painel de XP vem depois, com cada coluna na largura do que guarda. Toda linha tem a mesma altura, e o título de
cada seção ocupa duas linhas mescladas.*

- **Dossiê:** *foto (12 colunas por 19 linhas, mais alta que larga), `Nome` (espelho da `CARTEIRA`), `Grau` (menu das
  cinco patentes), idade, altura, olhos, cabelo, pele, gênero, aparência, história, personalidade, laços e anotações.*
- **Em uso:** *`Mão principal` e `Mão secundária` (menus com o `Soco` e o que está nos equipáveis guardados; arma de
  duas mãos ocupa a secundária, e arma `Versátil` abre a opção das duas mãos, com o dado um passo acima) e `Vestindo`
  (menu que só lista o que o Grau libera). Embaixo de cada um, a linha de detalhe e as marcas de treino, de Força, de
  Grau e do Selo de gesto.*
- **Treino em armas:** *as 52 armas em 13 categorias, uma caixa de seleção por arma e uma por grupo, num grupo de
  linhas que fecha.*
- **Fileira:** *carga contra `5 + Força`, ienes, salário do Grau, requisito de Força e situação do Traje.*
- **Equipáveis guardados** *(seis linhas com menu, duas livres) e* **itens guardados** *(doze linhas).*
- **Painel de missões e XP,** *depois da coluna `AU`, num grupo de colunas que nasce fechado: duas tabelas de 50
  missões (tipo, adicional, desconto e total), o XP total, o que falta para o próximo nível e a tabela de níveis.*
- **Extensão do painel,** *num segundo grupo de colunas, dentro do primeiro, também fechado: mais duas tabelas de
  50 missões, do mesmo tamanho. O XP total soma as quatro (200 linhas). Pedido dele: "já vi mt player lotando essas
  tabelas".*

**Três caixas da `FICHA` mudaram.** *O `EQUIPAMENTO` deixou de ser menu e espelha o que está vestido e o escudo da mão
secundária, montando o mesmo nome que a tabela de equipamento da `DADOS` usa: a Defesa não mudou de conta. O `XP` mostra
a soma das missões do painel. O `DESLOCAMENTO` cai pela metade com uniforme ou escudo sem a Força, ou com a carga
acima do limite.* **A ficha nasce vestindo o `Traje 1`, que é o do kit inicial:** *antes o `EQUIPAMENTO` nascia
vazio. Até o refino 2 a Defesa é a mesma; do refino 3 em diante o cobrir-se protege mais que o `Traje 1`, e quem
quiser ele escolhe `Sem uniforme`.*

**O catálogo ganhou quatro chaves.** *`equipamento` (as 52 armas, as listas de treino, as faixas de projétil, a
munição, o soco, o Volume, as situações do Traje e o Grau mínimo do Revestimento), `patentes` (o salário) e `missoes`
(os tamanhos e o desconto da semana) saem do livro da v0.330, e o `conferir-catalogo.py` relê cada tabela do
`manual.txt` desta pasta, que é o da v0.263: bate tudo, coluna a coluna. A única regra em que o livro de hoje está à
frente do `manual.txt` é a soma dos itens leves, que não arredonda mais (v0.327); a ficha segue o livro de hoje, e o
validador imprime a diferença. A quarta chave, `fora_do_livro`, guarda o que ele decidiu em 01/10 e o livro ainda não
tem.*

**Regras que o Mizuki decidiu em 01/10/2026 e que ainda não estão no livro** *(a ficha já segue estas)*:

| regra | o que ele decidiu |
|---|---|
| arma sem o requisito de Força | desvantagem ao atacar com ela |
| uniforme ou escudo sem o requisito de Força | veste, com deslocamento pela metade e desvantagem em TR Físico |
| carga acima do limite | a mesma punição, sem acumular |
| missão solo | `Solo simples` 75 XP e `Solo complexa` 150 XP |
| XP adicional | multiplicador: 1,25x, 1,50x ou 2x |
| arredondamento do XP | múltiplo de 12,5, para baixo; quem dá 12,5 exato ainda paga, e menos que isso não paga |
| situação do Traje | *fica para revisão dele; a nota da caixa repete o texto de hoje* |

**O que o `Codigo.gs` faz pela aba, tudo em gatilho simples:** *a caixa do grupo marca e desmarca o grupo inteiro, e a
da arma acerta a do grupo; escolher o Caminho marca o treino dele; anotar missão sobe o nível da `FICHA`; apagar o
`Vol.` de um item traz a conta de volta; e três notas mudam com a ficha (o requisito de Força, a carga e a situação
do Traje).*

> **Quatro escolhas minhas que ele ainda não comentou, e que são fáceis de trocar:**
> 1. *o XP só sobe o nível, nunca desce: quem começou a campanha acima do nível 2, ou sobe na mão, não perde o nível
>    por anotar uma missão;*
> 2. *o XP para de subir o nível no 20, que é o limiar do feito do livro; quem já passou dele sobe normalmente;*
> 3. *desmarcar a caixa do grupo desmarca o grupo inteiro, e ela só aparece marcada com o grupo inteiro;*
> 4. *o desconto do menu é metade a cada missão (50%, 25%, 12,5%, 6,25%), e o livro escreve 12% e 6%.*

> **⚠ A troca de paleta ficou mais pesada.** *A aba tem 6.264 células (a `FICHA` tem 7.050). Cor e régua de todas as
> abas deixaram de caber numa execução: a troca pinta a `CARTEIRA`, a `FICHA`, a `FICHA PESSOAL` e o `GLOSSÁRIO`, e o
> resto termina no clique seguinte, sem aviso, como a arte já terminava. O `regressao-paleta.js` passou a cobrar isso,
> e a estimativa do passo de régua passou a contar as faixas da aba.*
> *A primeira versão da aba tinha 90 colunas e 7.380 células, com o painel na grade de 28 px e cada célula de missão
> mesclada; o painel passou a ter colunas de largura própria, e a aba perdeu um terço das células e 481 mesclagens. Depois vieram as
> duas linhas do título e a extensão, e ela foi a 87 linhas por 72 colunas.*

**Toda linha da aba tem a mesma altura.** *A primeira versão dava 27 px às linhas de título de seção. Como a linha é da planilha inteira, duas linhas da lista de missões e uma da tabela de níveis saíam mais gordas que as vizinhas, e o Mizuki pediu para tirar ("dá certa agonia, a galera vai reclamar"). Em uma linha comum o título ficava pequeno, e ele pediu o equivalente a duas: o título de seção ocupa duas linhas mescladas, em Oswald 14. O `regressao-pessoal.js` cobra as duas coisas: nenhuma linha do corpo foge da altura padrão, e todo título ocupa duas linhas.*

**Como foi conferido.** *O `regressao-ficha-pessoal.py` preenche doze casos na ficha gerada, manda o LibreOffice
recalcular e compara com a regra montada do catálogo: as caixas da aba, a Defesa da `FICHA` pelo espelho, os menus que
mudam, as 144 combinações de tipo, adicional e desconto, e o que falta para o próximo nível. O `regressao-pessoal.js`
roda o script num Sheets de mentira montado do `ABAS`. O `regressao-construir.js` roda o `construir()` inteiro num
Sheets de mentira rigoroso (método que o Apps Script não tem, faixa fora da aba, matriz de tamanho errado e mesclagem
cruzada estouram), confere o que ficou montado e usa a planilha pelo `onEdit`. O `arnes-pessoal.py` planta trinta e um
defeitos numa cópia e confere que cada um acende a checagem dele. O `medidas/ver-aba.py` desenha a aba a partir do `ABAS`, com os valores
recalculados, para olhar e comparar com o estudo.* **Os vinte validadores passam.**

> **O que só o Sheets diz, e falta ele testar:** *os dois grupos (o de linhas do treino e o de colunas do painel, que
> nasce fechado), no computador e no celular; se os grupos sobrevivem à cópia da planilha; as caixas de seleção nos
> títulos dos grupos; os menus que leem coluna com célula vazia; a cor de aviso; o formato do iene; os dois grupos de colunas, um dentro do outro; o tempo do
> `construir()`, que ganhou 340 mesclagens (as fórmulas, que passaram de 280 para 801, agora vão em 143 lotes, e
> não mais uma a uma); e o tempo real da troca de paleta.*

### B27 · O cabeçalho do estudo, o título no acento, a barra do tema e a revisão das 122 paletas — **FEITO em 01/10/2026, e falta testar no Sheets**

*O Mizuki montou a ficha com a Ficha Pessoal no Sheets, trocou de tema e mandou sete pontos. A troca de cor
funciona; o que ele apontou é desenho e cor.*

| o que ele apontou | o que mudou |
|---|---|
| o topo da Ficha Pessoal ficou pior que o do estudo | o cabeçalho voltou ao molde do estudo: a marca 呪術, o título e uma linha de apoio à esquerda; o nome e, embaixo, o Caminho, a Trilha e o nível à direita |
| a `FICHA` devia ter o mesmo cabeçalho, como a `CARTEIRA` tem o dela | a `FICHA` ganhou o mesmo molde, com o título `FICHA DE REGISTRO`; a Ficha Pessoal copia dela e troca o título e a linha de apoio |
| a faixa de título de seção devia se destacar, como no `GLOSSÁRIO` e no `CATÁLOGO` | a faixa da Ficha Pessoal usava o painel alto, o mesmo do rótulo; passou a usar o acento, que é o papel das faixas daquelas duas abas |
| as barras não acompanham a paleta, inclusive a da carga | a barra cheia deixou de ser o osso escrito na fórmula e passou a ser uma cor do tema |
| imagem e fonte em cor "nada a ver" (o roxo do `Alfazema · Claro`); revisar as 122 | duas regras novas na derivação das paletas e três no `Codigo.gs`, e as 122 foram olhadas uma a uma |
| o aviso "Pense bem!" ao clicar no `+` do painel de XP | as fórmulas que moram em coluna ou linha de grupo ficaram sem trava |
| o cabeçalho devia acompanhar o painel aberto | a faixa de tinta e a divisória de baixo dela vão até a última coluna da aba |

**O cabeçalho é a limpeza 23, o `ficha-v01/cabecalho.py`.** *Roda logo depois do desenho da mesa e antes do índice,
porque o nome da personagem muda de célula (de `D3` para `AB2`) e o índice da `DADOS` publica o endereço dele; o número
da `CARTEIRA`, que lia `FICHA!D3`, passa a ler o lugar novo. O carimbo de versão continua, na linha de apoio da
`FICHA` ("Projeto M · v0.258 · em dia"). A palavra `CATÁLOGO` saiu do cabeçalho: para o Mizuki, catálogo é a aba da
invocação. A linha 3 perdeu a altura maior que tinha para o nome grande, e as cinco linhas ficaram iguais.*

**A barra cheia mora numa célula da `DADOS`.** *As três barras da `FICHA` (vida, energia e integridade) e as duas da
Ficha Pessoal (carga e XP) leem a conta `cor da barra cheia`, que nasce no osso de fábrica. A troca de tema ganhou um
passo, o primeiro, que grava ali a `barra` do tema; nenhuma fórmula é reescrita. O âmbar e o vermelho de vida baixa
continuam fixos, pela decisão A5.* **A barra do tema é viva onde pode e neutra onde não pode.** *Mostrei ao Mizuki três
opções (neutra, viva e cor do texto) e ele respondeu: "porque não mescla? deixa a melhor opção a depender da paleta
mesmo". A regra do `derivar.py`: a barra é a primeira cor viva do tema (a tinta de enfeite, depois a régua, depois o
acento, cada uma acertada para ler 3,0 sobre o painel) que não é parente do âmbar nem do vermelho, medido no círculo
de matiz do OKLCH (mais de 35 graus do vermelho e mais de 30 do âmbar, com croma de 0,08 para cima). Quando as três
são da família do âmbar ou do vermelho, ela é neutra: o matiz da régua com pouca croma, clara nos temas escuros, como
o osso era, e de tom médio nos claros.* **Das 122, 68 saem vivas e 54 neutras.** *Viva: o azul do Meia-Noite, o turquesa
do Recife, o verde do Carnaval, e no Alfazema claro, que é todo dourado, o azul do acento. Neutra: o Brasa, o Rubi, o
Kitsune, o Mizuki claro.*

**A revisão das cores, com a medida que a puxou.** *Rodei a troca de verdade (o `convergirPaleta_` do `Codigo.gs`) nas
122, num Sheets de mentira, e olhei o resultado tema por tema (`medidas/pintar-paletas.js` e `medidas/ver-paletas.py`).
O `bloco` e a `linha` são a tinta de enfeite: só pintam a pincelada, a moldura da foto e as letras de enfeite (o
呪術廻戦, o número da carteira, a lombada), e nenhuma célula os usa de fundo. Eles saíam da segunda cor do meio da
paleta, no matiz que ela tivesse, e dois defeitos apareceram:*

1. **Cor fraca entrando como terceira cor.** *No `Alfazema · Claro` a ficha é amarela, a borda é dourada, o acento é
   azul e a tinta de enfeite saía num roxo acinzentado. Regra nova no `derivar.py`: se a tinta de enfeite tem pouca
   croma (abaixo de 0,10, medida em OKLCH) e o matiz dela não é parente nem da régua nem do acento (mais de 40 graus dos
   dois), ela vira um tom da própria régua. Pega 12 das 122: Alfazema (as duas), Sálvia (as duas), Ardósia claro, Terra
   claro, Céu de Verão (as duas), Tengu escuro, Tanuki (as duas) e Momotaro escuro. Quando a cor tem força (o verde do
   Carnaval, o turquesa do Recife, o magenta do Neon), ela fica.*
2. **A rede de legibilidade trocando de matiz ao acaso.** *Quando uma letra ou uma imagem não lia sobre o fundo, o
   `Codigo.gs` a trocava pela cor da paleta de contraste mais parecido, qualquer que fosse. Medido nas 122, em quatro
   abas: a lombada era trocada em 585 células (350 por uma cor da variante oposta do tema, 160 pelo acento, 75 pelo
   bloco), a marca e o número em 152, e o selo caía no bloco em três temas e numa cor da variante oposta em seis.
   Regra nova, "ajusta o valor, não troca de cor": o `bloco` e a `linha` já saem do `derivar.py` lendo 3,5 e 3,0
   sobre a tinta, o fundo e o papel, no mesmo matiz, mais escuros ou mais claros; a rede só oferece cor de texto; a
   letra de enfeite é achada pelo endereço no `ABAS`, e não pela cor que tem (antes, bastava a rede trocar a lombada
   pelo acento uma vez para ela ser "acento" em toda troca seguinte); e a imagem que não aparece vai para o acento do
   tema e, se nem ele aparecer, para a cor dela no mesmo matiz. Nas 122: 673 imagens na cor do papel delas, 59 no
   acento, nenhuma no terceiro caso.*

*Fora o `bloco`, a `linha` e a `barra`, nenhum papel de nenhuma paleta mudou de hex: fundo, painéis, régua, acento e
texto são os que ele já aprovou. O `PALETAS` do `Codigo.gs` deixou de ser colado à mão: o `derivar.py --aplicar` o
reescreve, e o `conferir-ficha-xlsx.py` confere que os dois são iguais.*

**Como foi conferido.** *O `regressao-paleta.js` ganhou nove checagens com referência que não depende do `Codigo.gs`:
a barra gravada na célula certa com a cor do tema, as letras de enfeite no papel delas depois de uma e de duas
trocas, a lombada que uma troca antiga deixou "acento" voltando para a linha, cada imagem das 122 na cor que a regra
manda, e o `bloco`, a `linha` e a `barra` lendo sobre os fundos onde moram. O `arnes-paleta.py`, novo, planta sete
defeitos numa cópia e confere que cada um acende a checagem dele (roda à mão: são oito rodadas, uns dois minutos). O
`conferir-ficha-xlsx.py` ganhou quinze checagens (o cabeçalho das duas abas, o carimbo, a faixa no acento, as cinco
barras, a rede só com cor de texto, o `PALETAS` igual ao derivado). O `comparar-ficha-01.py` cobra a limpeza 23 célula
a célula. O `regressao-pessoal.js` cobra que nenhuma faixa travada encoste em grupo, e o `arnes-pessoal.py` ganhou a
perturbação dela (são 31).* **Os vinte validadores passam.**

> **Duas coisas que eu não mexi, para ele decidir:**
> 1. **o título de seção da `FICHA`.** *Ela tem a caixa do número no acento e a faixa do título no painel alto, que é
>    o desenho dele. Não mexi. Passar a faixa para o acento, como na Ficha Pessoal, é uma limpeza pequena.*
> 2. **a régua de alguns temas é mais forte do que a paleta de origem.** *A derivação mede saturação em HLS, que engana
>    no claro: um quase branco como `FFF5F5` (Blush) tem saturação 1,0 lá, e a régua sai vermelho vivo `CC0000`. É por
>    isso que o `Alfazema · Claro` é uma ficha amarela de borda dourada. Ele disse que a maioria está boa, então não
>    toquei em fundo, painel nem régua; se quiser, é outra rodada.*

> **O que só o Sheets diz, e falta ele testar:** *a `SPARKLINE` lendo a cor de uma célula (a conta é a mesma, mas só o
> Sheets desenha a barra); abrir e fechar o painel de XP sem o aviso da trava; o cabeçalho novo no computador e no
> celular; e o tempo da troca, que ganhou um passo curto. Ficha montada antes desta data não tem a célula da barra: a
> troca de tema pula o passo e a barra fica no osso, como estava. Para ganhar tudo, é rodar o `construir()` de novo.*

### B28 · O `construir()` estourou os seis minutos — **REFEITO em 01/10/2026, e medido por ele no Sheets: 220 s com cinco abas**

*Achado do Mizuki em 01/10/2026, com o registro do editor: `Execução iniciada` às 15:08:19 e `Exceeded maximum execution
time` às 15:14:19. O registro não dizia em que etapa a montagem estava, porque o `construir()` só escrevia no fim.*

**Duas decisões dele:** *"Pode tirar o catalogo e invocação, isso vai ganhar tempo e reduzir o codigo, depois implementamos
dnv diferente com a att"* e *"Busque otimzar o codigo e o teste se possivel, para ver se os resultados se mantiveram"*.

**1. A `INVOCAÇÃO`, o `CATÁLOGO` e a `DADOS_INV` saíram da ficha.** *É a limpeza 24, `ficha-v01/sem_invocacao.py`: as três
continuam no `layout.json`, que é a cópia da planilha viva, e saem da ficha gerada, por último (o `GLOSSÁRIO` nasce na
posição da `INVOCAÇÃO` e usa os estilos do `CATÁLOGO`). A montagem para se alguma aba que fica citar uma delas; nenhuma
cita. A ficha de invocação separada (`ficha-invocacao/`, o `invocacao.json` e os três validadores dela) não foi tocada. A
decisão está no `decisoes-ficha.json`, em `C6_documento.abas_removidas_em_01_10`.*

**2. O `construir()` vai menos vezes ao servidor, e a planilha que ele deixa é a mesma.** *O que pesa no Apps Script é a ida
ao servidor, e a montagem fazia isso célula a célula em quatro lugares:*

| o que era | o que ficou | chamadas, nas cinco abas |
|---|---|---|
| uma chamada de `merge()` por mesclagem | a mesclagem de uma linha que se repete nas linhas de baixo vai numa chamada de `mergeAcross()` | 897 → 310 |
| as fórmulas numa fila, gravadas depois das abas | todas as abas nascem primeiro, vazias e do tamanho certo, e a fórmula vai na mesma gravação dos valores | 112 → 0 |
| uma trava por célula de fórmula, três idas ao servidor cada | uma trava por faixa de fórmulas vizinhas; as células travadas são as mesmas | 333 → 228 |
| a nota de regra lia a mesclagem, a fórmula e o valor da célula de cima, nota por nota | a aba é lida uma vez, e as notas voltam numa gravação | 256 → 16 |
| cada aba era movida para o lugar | elas já nascem na ordem | 11 → 1 |

*A ficha de oito abas fazia 1.195 chamadas de mesclagem e 111 travas; a de cinco faz 310 e 76.* **Isto é contagem de chamada, e não tempo:** *o Apps Script não roda fora do Google, e eu não sei quanto cada
etapa levava. Por isso o registro mudou:* **cada etapa vai para o registro na hora, com o tempo dela.** *Se a execução
expirar de novo, o registro diz onde.*

**3. O acabamento pode rodar sozinho.** *A cor de estado, as notas, as travas e a caixa da paleta viraram a função
`acabamento_`, que o `construir()` chama no fim. Se a montagem das abas passar de quatro minutos e meio, ele para ali,
deixa a planilha em português e escreve `FALTA O ACABAMENTO: rode a função acabar()`. O `acabar()` roda quantas vezes
precisar sem duplicar trava nem nota.*

**4. Os dois arquivos ficaram menores,** *sem mudar o conteúdo: o `Ficha.gs` foi de 633 KB para 442 KB (as três abas a
menos, e as células curtas vão várias por linha) e o `Codigo.gs` de 240 KB para 199 KB (cada variante de paleta numa
linha). Somados, de 873 KB para 641 KB, e de 26.728 linhas para 3.139. O `PALETAS` continua igual ao
`paletas-grandes.json`, cor por cor.*

**Como foi conferido.** *O Sheets de mentira do `regressao-construir.js` virou módulo (`medidas/sheets-de-mentira.js`) e
passou a guardar tudo o que o `construir()` grava: valor, fórmula, formato, borda, mesclagem, nota, menu, caixa de seleção,
trava, grupo, altura e largura. O `medidas/comparar-construir.js` monta a planilha com o script do commit `aef825f` (sem
as três abas) e com o da pasta, e compara:* **as cinco abas saem iguais, célula a célula**, *e o `ABAS` delas é o mesmo.
O `regressao-construir.js` ganhou onze checagens (fórmula junto do valor, nenhuma fórmula gravada antes de a aba citada
existir ou fora do inglês, mesclagem em lote sem mesclar nada a mais, as travas da `FICHA` e da `CARTEIRA` cobrindo toda
fórmula e só fórmula, a nota no título, e o `acabar()` sozinho, repetido e depois de uma montagem que passou do teto). O
`arnes-pessoal.py` foi de 31 para 40 perturbações; duas não acenderam na primeira rodada (a aba preenchida antes de as
outras nascerem, e o `acabar()` em português), e viraram checagem: o Sheets de mentira agora acusa as duas. Os vinte passam.*

**O que só o Sheets diz, e falta:** *o tempo de verdade do `construir()`; se o `setValues` grava as fórmulas como o
`setFormulas` gravava (a documentação diz que sim: texto que começa com `=` é fórmula); se o `mergeAcross()` deixa as
mesmas mesclagens na tela; e se as abas nascem na ordem pedida (se não nascerem, o script move, como antes).*

### B29 · A Ficha Amaldiçoada — **FEITA em 01/10/2026, e falta montar no Sheets**

*Pedido do Mizuki, depois de quatro rodadas de estudo (`mockup/ficha-amaldicoada-estudo.html`):* **"pode fazer o codigo,
considerando 3 colunas mesmo, é oq gostaram, so q ta mt amassadinho"**, *e antes disso:* *"a ficha amaldiçoada tem que ser
basicamente 'tudo' que já de pra automatizar e calcular para o jogador"*.

**O que entrou.** *A aba `FICHA AMALDIÇOADA`, depois da `FICHA`, e a aba oculta `DADOS_AM`, com as tabelas e as contas dela
(como a `INVOCAÇÃO` tinha a `DADOS_INV`). É a limpeza 25, `ficha-v01/ficha_amaldicoada.py`. A aba tem dez seções, cada uma
num grupo de linhas que fecha: Técnica, Orçamento (com o índice de preços por Classe), Feitiços (36 lugares em três lotes de
12), Classe 0, Liberação Máxima (3), Técnica Máxima, Expansão de Domínio, Passivas (5 pagas e 7 do Leque), Aptidões (12) e
Pactos (3). Uma linha de saltos no alto leva a cada seção.*

**A página mais larga, e por que não é a grade da FICHA.** *Ele pediu as três cartas por fileira com a página mais larga
("dar mais colunas a pagina"). A aba não usa a grade de colunas de 28 px: cada carta tem cinco colunas na largura do que
guardam (112, 140, 112, 56 e 56 px), 476 px no total, contra os 364 px da carta do estudo. São 21 colunas e 1.596 px, e as
seções de cima se alinham nas mesmas colunas. Com isso a aba tem 11 mil células em 537 linhas; na grade de 28 px seriam 33
mil, e a troca de tema dela não caberia num passo do gatilho simples.* **O preço:** *ela cabe inteira num monitor de 1920 px;
num notebook de 1366 px pede zoom de 75% ou rolar para o lado. A decisão está no `decisoes-ficha.json`, em
`C6_documento.largura_fora_do_notebook`.*

**A conta.** *Tudo mora em fórmula, na `DADOS_AM`: uma linha por feitiço, e a carta só mostra o resultado. Nenhuma fórmula usa
`LET` nem `LAMBDA`. A carta calcula: os pontos, o preço de cada peça pela Classe, o desconto de Família Livre, a devolução
das Restrições (com o teto de 2 × Classe, o que se perde, e a que o Selo já obriga), os dados, o PE, a ação, como resolve, o
alcance pelas escadas, o Ampliar em cada Classe acima, e os avisos: Família Fechada, limite de Melhorias e de Restrições,
orçamento estourado, duas Restrições de frequência, os quatro pares que o livro proíbe, o teto de dados somando alvos e
repetições, e as regras da Liberação Máxima. A ficha só calcula e só conta o espaço do feitiço que tem nome.*

**De onde sai cada número.** *As Formas, as Melhorias, as condições, as Restrições e a progressão saem do
`catalogo-projeto-m.json`. As Passivas, as aptidões (com a caixa de regra de cada uma), as escadas de alcance, a Classe 0, a
Liberação, a Técnica Máxima, o Domínio e os pactos não estão no catálogo, que está na v0.258: saem do
`ficha-v01/tecnica-do-livro.json`, que o `ficha-v01/extrair_tecnica.py` lê dos capítulos do livro (v0.330) e que carrega a
versão de onde saiu. O que o livro só escreve em frase é conferido contra a frase.* **Levar essas tabelas para o catálogo é
decisão do Mizuki, e não foi feito.**

**O que ficou diferente do estudo, e por quê:**

1. **A `Passiva Própria` e a `Aptidão Própria` são entradas do menu** *(`Passiva Própria (CP 1)`, `(CP 2)`, `(CP 3)`), e a
   carta tem uma caixa "seu texto". No estudo a mesma caixa mostrava o texto do livro ou o do jogador; na planilha uma
   célula é fórmula ou é digitada, não as duas.*
2. **Na Classe 0 a Restrição Leve devolve o dado que a Melhoria Leve tirou.** *O estudo ignorava a Restrição. O livro diz
   "cabe uma Melhoria Leve e uma Restrição Leve numa Classe 0, tirando um dado para pagar".* **É leitura minha, e falta ele
   confirmar.**
3. **A Liberação Máxima, a Técnica Máxima e o Domínio nascem fechados,** *porque a ficha nova está no nível 2.*
4. **O menu mostra só o nome da peça,** *e o preço aparece ao lado, depois de escolhida ("−2 · Média · Livre"). No estudo o
   menu trazia o preço, que muda de carta para carta; no Sheets a lista do menu é uma só.*
5. **O `+` é da fileira inteira:** *abre as três cartas dela. Isso já era assim no estudo.*

**O que a aba não faz:** *não toca a seção 8 da `FICHA` (ele ainda não decidiu se ela vira espelho ou sai), e não desenha as
rotas sem Fundamento (Técnica Marcial, Sem Técnica e Restrição Celestial).*

**O `construir()` com a aba nova.** *A aba tem 1.272 mesclagens e 374 células de menu. Para ela não triplicar a montagem:*

| o que | como | chamadas |
|---|---|---|
| as treze fileiras de cartas de feitiço, e as de Passiva e de aptidão | só a primeira de cada tipo é mesclada; as outras recebem o formato dela por cópia, e a mesclagem vem junto. O script confere se veio, e se não veio mescla uma a uma | 573 de mesclagem na planilha inteira (eram 310 sem a aba), e 17 cópias |
| os menus e as caixas de seleção do Selo | uma regra por lista, numa matriz do tamanho da aba, gravada de uma vez | 1 |
| os 52 grupos de linhas | nascem todos, fecham todos numa chamada, e os que nascem abertos são abertos | 53 + 1 + 12 |
| a conta de cada feitiço, 75 fórmulas iguais a menos da linha | só a primeira linha vai no `Ficha.gs`; o script a copia para baixo | 9 cópias |

*O `Ficha.gs` também escreve cada fileira de cartas uma vez só: no arquivo fica a primeira e, das outras, só o que é diferente
(a fórmula que aponta para a conta de outro feitiço); o script refaz as cópias quando carrega (`expandirCopias_`). Sem isso
ele teria 1,2 MB. Ficou com 637 KB; com o `Codigo.gs`, 838 KB. Antes de sair a invocação, os dois somavam 873 KB.*

**O tempo.** *Ele mediu a montagem de cinco abas em 220 s (abas criadas 70, as cinco abas 51, menus 8, acabamento 90, dos
quais 83 são as travas), e disse que não vê problema em demorar. Com as duas abas novas a minha conta, por número de chamadas,
é de 60 a 70 s a mais:* **uns 285 s, dentro dos 360.** *É estimativa. O teto para o acabamento começar desceu de 270 para
250 s, porque o acabamento leva 90: se a montagem passar disso, o registro pede o `acabar()`.*

**A troca de tema.** *A aba entra na troca como as outras, num passo de cor e num de régua. Ela é a terceira da ordem: a
troca pinta a `CARTEIRA`, a `FICHA` e a `FICHA AMALDIÇOADA`, e a `FICHA PESSOAL`, o `GLOSSÁRIO` e a arte terminam no clique
seguinte, sem aviso. A aba em que o jogador está passa na frente, como antes.*

**Como foi conferido.** *Entrou o `regressao-amaldicoada.py`, no `rodar-tudo.sh`. Ele preenche onze fichas na planilha gerada,
recalcula no LibreOffice e compara com a regra, escrita de novo em Python:* **os 33 feitiços prontos do livro saem com os
dados que o livro imprime, e nenhum é acusado de erro; 429 cartas batem caixa por caixa (151 com erro, de propósito): as sorteadas em cinco níveis, com Famílias Livres e
Fechadas, e uma ficha de casos de borda, com um feitiço para cada regra que o sorteio quase nunca monta; e o Orçamento, o índice, a Classe 0, a Técnica Máxima, o Domínio, as
Passivas, as aptidões e os pactos batem em quatro fichas.** *Ele também monta a planilha no Sheets de mentira e confere que
a aba fica com as mesmas fórmulas, valores, mesclagens, menus, caixas e grupos da planilha gerada, e que o plano B da
mesclagem deixa a aba igual. O `arnes-amaldicoada.py`, rodado à mão, planta trinta defeitos, um de cada vez, e cada um
acende a checagem dele. Na primeira volta quatro passaram calados: um era o nome da checagem errado no arnês, e três eram
buraco de verdade (o teto da devolução na conta do Ampliar, as duas Restrições de frequência e os pares proibidos), que
o sorteio não montava. Foi daí que veio a ficha de casos de borda, e com ela os trinta acendem. O `medidas/ver-aba.py` desenha a aba (`--aba "FICHA AMALDIÇOADA"`), e eu olhei.*

**O que só o Sheets diz, e falta ele testar:** *o tempo de verdade; se a cópia de formato traz a mesclagem (se não trouxer, o
registro diz "FILEIRAS MESCLADAS UMA A UMA" e a montagem demora mais); o `setDataValidations` com os menus e as caixas de
seleção juntos; abrir e fechar grupo dentro de grupo; a ligação dos saltos; a página de 1.596 px no monitor dele e no
celular; e se os textos compridos das aptidões cabem na caixa.*

**Achado no livro, para ele decidir:** *a tabela `Base por Classe` dá `9 m` e `18 m` para "`Cura` e `Onda`", e a tabela
`Formas` diz que a `Onda` é uma esfera de raio `3 m` centrada em quem conjura. A aba segue a tabela `Formas`, como o estudo.*

### B30 · O menu das mãos só lista o `Soco` — **RESPONDIDO e FEITO em 01/10/2026; falta ver no Sheets, e a frase do `Alcance` no livro fica para revisão dele**

*Achado do Mizuki em 01/10/2026, mexendo na ficha montada com o código do commit `8c7279a`, com duas fotos do `EM USO` da
`FICHA PESSOAL`: o menu da `Mão principal` só com `Soco` e o da `Mão secundária` só com `—`. Palavras dele: "n ta
aparecendo a lista de armas, da pra escrever e funciona, mas a lista n aparece".*

**O que o gerador fazia, e continua fazendo.** *É o desenho do estudo (B26): o menu das mãos lista o `Soco` e o que estiver
nos `Equipáveis guardados` (linhas 69 a 76 da aba; as seis primeiras têm o menu das 52 armas), pelas tabelas
`menu_principal` e `menu_secundaria` do `ficha-v01/ficha_pessoal.py`. A ficha nasce com os equipáveis vazios, e por isso
o menu nasce só com o `Soco`. A arma digitada na mão sem estar guardada é aceita (o menu só avisa) e a linha de baixo diz
"Não está nos equipáveis guardados".*

**A resposta dele:** *"A, manter com aviso visivel e uma nota na caixa aonde fica a escolha de item (na mão) explicando.
Por sinal, seria bom se no momento da arma ser escolhida, como logo abaixo mostra propriedades e afins, poderia colocar
uma nota apresentando o que cada propriedade faz".* **Três coisas entraram:**

- **O aviso visível.** *Sem nenhuma arma guardada, a linha embaixo da `Mão principal` diz `d4 · para outra arma, guarde ela
  nos Equipáveis guardados`; sem arma de uma mão nem escudo guardado, a da secundária diz `Mão livre · arma de uma mão ou
  escudo guardado aparece aqui`. Cada mão conta só o que serve a ela: o escudo não conta para a principal, e a arma de duas
  mãos não conta para a secundária. Com algo guardado, as duas linhas voltam ao texto de antes.*
- **A nota na caixa de escolha.** *A nota das duas mãos saiu do rótulo e foi para a caixa em que a arma é escolhida, e abre
  dizendo que a arma tem de estar nos `EQUIPÁVEIS GUARDADOS`, mais abaixo na aba. O `Vestindo` não mudou: a nota dele
  continua no rótulo.*
- **A nota das propriedades.** *A linha embaixo de cada mão (a que mostra o dado e as propriedades) ganhou uma nota que
  muda com a arma: o nome dela e, uma por linha, cada propriedade com o que faz. É mais uma "nota viva" da `DADOS`, que o
  `notasVivas_` do `Codigo.gs` já copiava para a caixa quando o `EM USO` ou os equipáveis mudam: o script não ganhou código
  novo, só as duas linhas na tabela. O `Soco` e o escudo têm a frase do livro. A arma digitada que não está guardada fica
  sem nota.*

**De onde vem o texto.** *O `catalogo-projeto-m.json` traz as propriedades de cada arma, mas não o que elas fazem. O texto
sai do capítulo de Equipamento do livro (v0.330), pelo `ficha-v01/extrair_equipamento.py`, que grava o
`ficha-v01/equipamento-do-livro.json`: as tabelas `Propriedades` e `Restrições de arma`, e, onde a tabela só aponta ("Ver
Munição"), as frases da seção apontada, que têm de estar no capítulo palavra por palavra. A ficha acrescenta só o número
da arma em uso: as duas faixas no `Longo Alcance` e o X da recarga na `Munição`. As `Duas mãos` entram pela coluna `mão`
do catálogo, sem a frase "No catálogo ela aparece como o 2 da coluna mão". Levar esse texto para o catálogo é decisão do
Mizuki, e não foi feito.*

**O índice da aba andou três colunas na `DADOS`,** *porque a tabela das propriedades entrou antes dele: o
`IDXP_COL_CAMPO` do `Codigo.gs` passou de 116 para 119. É a única linha de código que mudou no `Codigo.gs`.*

**Como foi conferido.** *O `regressao-ficha-pessoal.py` ganhou a nota de cada mão e o aviso em todos os casos (são vinte
agora), com a nota montada de novo a partir do arquivo lido do livro: cinco armas que juntas têm as treze propriedades em
uso, a arma não guardada, só o escudo guardado e só a arma de duas mãos guardada. O `regressao-pessoal.js` confere as cinco
notas vivas, a caixa de cada uma e a nota da caixa de escolha. Entrou o `arnes-ficha-pessoal.py`, rodado à mão, com treze
defeitos plantados nessas contas: os treze acendem, e o contra-teste fica verde. O `arnes-pessoal.py` ganhou dois.*

**O `Alcance` no corpo a corpo: a ficha já segue a resposta dele, e a frase do livro fica para revisão.** *A propriedade
`Alcance` manda ver a seção "Alcance no corpo a corpo", que diz "As Armas Longas chegam a 3 m". Onze armas têm `Alcance`, e
só três são da categoria `Armas Longas` (Lança, Naginata e Yari); as outras oito são Bastão, Bō, Kusarigama, Chicote,
Corrente, Espadão, Nodachi e Odachi, e o livro não diz se elas chegam a 3 m. Perguntei, com três opções, e ele respondeu
em 01/10/2026:* **"sim é A"** *(toda arma com `Alcance` chega a 3 m), e depois:* **"pode mexer na ficha, anotado é pra
mexer no livro essa confusão"**. *Na ficha, a nota de toda arma com `Alcance` termina em "Nesta arma: 3 m", como o `Longo
Alcance` e a `Munição` já traziam o número da arma. Os 3 m saem da frase do livro, pelo `extrair_equipamento.py`; o que é
decisão dele, e o livro ainda não diz, é que valem para as onze.* **Para a revisão do livro (dele, no Claude 2, que eu não
edito):** *a frase "As Armas Longas chegam a 3 m" da seção "Alcance no corpo a corpo" precisa dizer que é toda arma com a
propriedade `Alcance`, e não a categoria `Armas Longas`.*

**O que só o Sheets diz:** *se a nota de 860 caracteres da arma mais carregada aparece inteira ao passar o mouse, e como
a nota fica no celular.*

### B31 · O retorno do teste da Ficha Amaldiçoada — **FEITO em 02/10/2026; o ponto 7 (a seção 8 da `FICHA`) virou o B32; falta ver no Sheets**

*Em 01/10/2026, à noite, o Mizuki montou a `FICHA AMALDIÇOADA` no Sheets com o código do B29 (a montagem funcionou),
trocou para uma paleta rosa e mandou oito pontos, com fotos e a planilha exportada (`Kaori.xlsx`). Sete entraram; o
ponto 7 é desenho novo e ficou para estudo.*

1. **Os textos pequenos ao lado dos títulos de seção saíram.** *Palavras dele: "achei bem inuteis esses textos pequenos
   adicionais, melhor remover". O título de cada seção vai de ponta a ponta (`D` a `T`).*
2. **O nome de cada carta, e a Classe na carta de feitiço, estão na cor de título.** *Ele achou que a paleta ficou "meio
   ruim nas caixas dos feitiços, liberações" e pediu "as cores de titulo em alguns pontos chave". Os pontos são escolha
   minha: o nome e a Classe (105 caixas). O estado da carta (`Na regra`, `⚠ 1 erro`) ficou fora, na cor do painel,
   porque o âmbar de aviso não se lê sobre o acento.* **Falta ele dizer se quer a cor de título em mais ou em menos
   lugares.**
3. **Duas linhas de respiro embaixo do último pacto,** *vazias e fora de grupo, para ele não colar no fim da aba. A aba
   tem 539 linhas agora.*
4. **A troca de paleta não grava mais na célula a cor de aviso que estava acesa.** *A `Livres · Fechadas` dele continuou
   vermelha depois de preenchida certo. A planilha exportada mostrou o vermelho gravado como fundo da célula: o
   `getBackgrounds()` e o `getFontColors()` do Sheets devolvem a cor que a regra condicional está mostrando, e não a da
   célula, e o `repintarCoresDaAba_` gravava de volta o que leu. A caixa nasce em `⚠ 0 de 2`, a troca pegou o vermelho
   aceso e deixou ele gravado. Agora, quando a troca lê o vermelho de estado (`#C2334D`) no fundo, ou o âmbar de estado
   na fonte de uma célula que não nasceu âmbar, ela parte da cor de fábrica daquela célula. Vale para a `FICHA` também,
   e a troca seguinte desfaz o vermelho que uma troca antiga deixou gravado: a planilha dele se conserta na próxima troca
   de paleta, depois de colar o `Codigo.gs` novo.*
5. **A caixa calculada em que alguém digita por cima volta a ser a conta, com um aviso na tela.** *Ele digitou 3 no `No
   domínio` do Orçamento e nada mudou: a caixa só mostra o custo do degrau escolhido na seção do Domínio, e o número
   digitado apagou a conta sem aviso. A `FICHA` avisa pela trava; esta aba não pode ter trava, porque quase tudo nela
   mora em linha de grupo, e trava em linha de grupo faz o Sheets avisar quem clica no `+`. Então a conta volta depois:
   o `devolverConta_` do `Codigo.gs`, chamado pelo `onEdit`, regrava a fórmula da caixa (o `ABAS` do `Ficha.gs` traz a
   fórmula de cada uma) e mostra um aviso por 8 segundos. Só volta fórmula que é referência pura a uma célula
   (`=DADOS_AM!$GH$22`), porque a planilha vive em português, e fórmula com vírgula entre argumentos gravada por script
   nesse idioma vira erro. Por isso a conta de toda caixa calculada da aba passou a morar na `DADOS_AM` (a tabela
   `mostra`), e as 727 caixas calculadas da aba só apontam para ela. Apagar a caixa também devolve a conta; as caixas de
   escolher e de escrever ficam como o jogador pôs.*
6. **A caixa de seleção do Selo saiu da carta.** *Palavras dele: "o selo n obriga restrição nenhuma é algo mais
   narrativo, pode remover". A devolução da Restrição não olha mais para o Selo, e a aba ficou sem caixa de
   seleção. Na volta da bateria achei uma sobra: a nota do rótulo `SELO` ainda dizia "Restrição que cobra a mesma coisa não devolve.", e essa
   frase saiu. A nota ficou "O que você sempre faz para conjurar. Não custa nem devolve ponto."*
7. **O "menu rápido" na seção 8 da `FICHA`: não foi feito.** *Ele pediu trocar a seção 8 por um menu retrátil com o que
   foi pego na `FICHA AMALDIÇOADA` (Passivas, aptidões, feitiços). A seção 8 hoje também serve às rotas sem Fundamento,
   onde vira "Bênçãos e Katas". Ficou a pergunta: o menu rápido substitui a seção 8 só para quem tem Fundamento (A,
   indicado) ou para todo mundo (B). Nos dois casos, é estudo com opções de desenho antes de construir.*
   **Respondido em 02/10/2026:** *"B - Por sinal o 'ficha amaldiçoada' tem q se modificar para cada origem, é pra aquele
   menu funcionar para todo mundo igualmente". O menu vale para todo mundo, e a Ficha Amaldiçoada passa a mudar conforme
   a Origem, que no livro decide a rota de criação: Fundamento, Sem Técnica (`Manejo`, `Auge`, a semente, sem Domínio),
   Técnica Marcial com energia (Corpo Amaldiçoado: `Kata`, `Ruptura`, `Ōgi`, sem Domínio) e sem energia (Restrição
   Celestial: Bênçãos e Lapidação no lugar das aptidões e do refino). O primeiro estudo do menu está em
   `mockup/menu-rapido-estudo.html` (`python3 mockup/estudo_menu_rapido.py`), publicado em
   https://claude.ai/artifact/2KvUsQ9NaraBWNBM8dc7TV: quatro formas (A colunas, B tabela de combate, C mini-cartas, D nomes
   com nota) nas quatro rotas. A pergunta da rodada é qual forma; a seguinte é como a Ficha Amaldiçoada muda em cada rota.*
   **Escolha de 02/10/2026:** *"pior q eu gostei das mine cartinhas, so acho que o espaço pra descrição poderia ser maior,
   tipo... ocupas uma ou duas linhas pra baixo, tem q caber o resumo todo de forma visualizável, qualquer coisa é só fazer
   ser retrateis pra caber melhor". O segundo estudo (mesmo link) mede cada resumo do livro na caixa de cada variação:
   uma ou duas linhas a mais não fazem caber tudo, e a altura que faz caber é 3 linhas no feitiço, 4 na Passiva e 5 na
   aptidão e na Bênção (C3), ou a mesma com só as duas primeiras sempre à vista e o resto num grupo por fileira (C4).
   O resumo da aptidão é a primeira frase da caixa de regra; a caixa inteira (até 1.303 letras) fica na Ficha Amaldiçoada.*
   **Escolha de 02/10/2026:** *"pode ser C3, mas aumente a largura delas, assim você vai ter mais espaço para caber por
   exemplo o tipo de resolvição, q nem o 'aliado auto...' que n coube ali e a descrição vai ter mais espaço para aparecer".
   A seção 8 já vai de D a AT, então carta mais larga é menos carta por fileira. O terceiro estudo (mesmo link) compara a
   C3 de quatro por fileira com três por fileira (13 colunas) e duas por fileira (21 colunas), todas na medida.*
   **Escolha de 02/10/2026:** *"vamos lá, três por fileira, MAS... 1 aumentar o tamanho da altura das descrições é necessario,
   colocar menu retratil para cada grupo é quase obrigatorio, colocar menu retratil para cada grupo de 2 feitiços é
   obrigatorio (um encima do outro eu digo)"*. *O quarto estudo (mesmo link) tem cada bloco (Feitiços, Liberações/Técnica
   Máxima/Domínio, Passivas, Aptidões) num grupo, e cada par de fileiras empilhadas num grupo dentro dele (a leitura é
   minha: grupo de linha fecha a linha inteira, então dois feitiços um em cima do outro são duas fileiras, seis cartas).
   Em cima de cada par fica uma linha que leva o + e diz quais cartas ele guarda ("Feitiços 7 a 12"), porque o + do Sheets
   fica na linha antes do grupo e dois grupos colados no mesmo nível viram um só. O resumo ganhou um botão de folga sobre a
   altura justa (2, 3 e 4 linhas): +1 dá 3, 4 e 5, com 141 linhas no caso cheio e 62 à vista como nasce.*
   **Fechado em 02/10/2026:** *"duas linhas e fechamos"*. *Resumo de 4 linhas no feitiço, 5 na Passiva e 6 na aptidão e na
   Bênção: 163 linhas no caso cheio, 70 à vista como nasce. Na medida conservadora da página cabem perto de 170, 260 e 300
   letras. Na mesma mensagem ele perguntou como ficam as peças criadas (Efeito Próprio, Restrição Própria, Passiva,
   Aptidão e Bênção Própria): a carta de feitiço da Ficha Amaldiçoada não tem lugar para o texto do Efeito Próprio nem da
   Restrição Própria, só o nome no menu e o preço. Ficou a pergunta, com três opções.*
   **Respondido em 02/10/2026:** *"as caixas de descrição, tanto no menu rapido, quanto no ficha amaldiçoada, o plano era
   revelar a descrição que o player escrever, com a narrativazinha dele e talz, a ficha amaldiçoada apresenta o calculo,
   menu rapido as informações do jogador. Ent seria B, o 'como é', mas a gente precisa ajustar o tamanho no menu rapido
   pra caber melhor e compensar nos menus retrateis".* *O quinto estudo (mesmo link): a carta do feitiço mostra o
   "Como é" do jogador, onde ele descreve também a peça criada; a caixa tem 7 linhas, medidas para caber tudo o que
   aparece no "Como é" da Ficha Amaldiçoada (476 px, 5 linhas, perto de 346 letras). A Técnica Máxima e o Domínio
   viram cartas da largura da seção (5 linhas), porque a caixa de lá ocupa a aba inteira. Passivas e aptidões mostram o
   "seu texto" e, quando ele está vazio, o texto do livro em cinza; a Passiva Livre e a Regra Própria abrem o bloco das
   Passivas (14 lugares). Cada fileira tem um grupo que fecha a descrição (o + na linha dos números): 216 linhas com tudo
   aberto, 59 como nasce, 34 com as descrições fechadas, 40 grupos, nenhum colado. Preço novo: a FICHA passa de umas 7 mil
   para umas 16 mil células na troca de tema, e a troca dela pode ter de ser repartida.*
   **Decidido em 02/10/2026:** *"Pode ser A"*: *antes de construir o menu, a rodada de como a Ficha Amaldiçoada muda em
   cada rota, e depois a aba nas quatro rotas e o menu numa construção só. O primeiro estudo das rotas está em
   `mockup/rotas-estudo.html` (`python3 mockup/estudo_rotas.py`), publicado em https://claude.ai/artifact/WkNP6o5RUuiRQN7Zaw5U6k:
   o que o livro muda em cada parte da aba (quase tudo é nome; a Expansão de Domínio some fora do Fundamento; a semente
   do Sem Técnica e o equipamento da Técnica Marcial são peças novas; as Bênçãos e a Lapidação entram no lugar das
   aptidões e do refino, com os mesmos números nas duas de graça), e três formas de pôr na aba o que só uma rota tem
   (A linha da rota na Técnica, B seção da rota, C o script esconde o que a rota não usa), com a Régua, a Redoma, a
   Fisga e a Bancada do livro. Ficam para as rodadas seguintes: a CD da rota de arma (o atributo é o da arma da Kata,
   e a FICHA tem uma caixa só), e se as Passivas do Fundamento valem na Técnica Marcial (o livro não diz).*
   **Escolha de 02/10/2026:** *"Eu gosto da C, n vou menitr, vamos testar"*. *A forma C: o desenho da linha da rota, e o
   onEdit esconde na Ficha Amaldiçoada o que a rota não usa quando a Origem muda na FICHA (a linha da rota no
   Fundamento, a Expansão de Domínio fora dele, a linha do Estímulo Muscular fora da Restrição Celestial sem energia).
   Antes de construir, um teste de bancada para ele rodar numa planilha em branco: `medidas/teste-esconder-rota.gs`
   (montarTeste, e o roteiro de seis passos fica escrito na aba FICHA). Ele confere o que o Sheets de mentira não sabe:
   se a linha escondida pelo script continua escondida quando o grupo em volta abre e fecha, se o Domínio volta como
   estava (fechado ou aberto), e se funciona numa cópia só com o gatilho simples. Rodado contra uma imitação mínima do
   Sheets no node, sem erro.*
   **Resultado do teste e decisões (02/10/2026):** *os passos 1 a 3 funcionaram (o script esconde e mostra por rota, e
   o Domínio volta como estava); no passo 4 "volta revelada": abrir o grupo em volta revela a linha que o hideRows
   escondeu. No passo 5 ele estranhou "refino, aptidão e outros seguem lá", que eram os rótulos fixos da aba de teste
   (na aba de verdade o título e as caixas viram Bênçãos e Lapidação por fórmula). Com isso ele voltou para a A: "Acho
   que seguirmos com o plano A vai ser melhor mesmo". A linha da rota fica na Técnica, sem script, e o Domínio diz que
   a rota não tem. Na CD da rota de arma, A: uma CD por grupo na linha da rota (atributo, conjuração e CD de cada
   grupo), e a linha de cima da Técnica diz "Por grupo" quando os grupos misturam atributos. Fica a dúvida da caixa de
   CD da própria FICHA na rota de arma. Pergunta seguinte: as Passivas do Fundamento no menu da Técnica Marcial.*
   **Respondido em 02/10/2026: "B".** *Na Técnica Marcial (as duas rotas), o menu de Passiva traz as 6 do capítulo da
   Técnica Marcial (Calo, Maldição do Inventário, Leitura, Segundo Fôlego, Contragolpe, Aliança) e a Passiva Própria;
   uma Passiva do Fundamento entra como Passiva Própria, com o mestre. A Regra Própria segue na seção da Técnica em
   todas as rotas. Com isso o desenho fechou, e a construção da aba nas quatro rotas e do menu rápido começa.*
8. **Toda caixa da aba abre em letra maiúscula.** *Palavras dele: "Textos em minusculo, sempre bom padronizar o maisculo
   na letra inicial". Vale para o que a ficha calcula e para o que nasce escrito: os menus de pacto viraram `Permanente`,
   `Temporário`, `De restrição` e `Um espaço de feitiço`, o estado virou `Na regra`, o Domínio diz `Não fecha` e `Rola`.*

**Para a revisão do livro (dele, no Claude 2, que eu não edito):** *a regra de que a Restrição que o Selo já obriga não
devolve ponto continua no livro da v0.330, e a ficha não a aplica mais. Ela está em quatro lugares:*

| arquivo | linha | o que diz |
|---|---|---|
| `40-fundamento.md` | 864 | a Restrição Própria "não pode repetir o que o seu Selo já obriga" |
| `40-fundamento.md` | 874 | "Restrição que o seu Selo já obriga não devolve ponto." |
| `20-criacao-de-personagem.md` | 135 | no passo do Selo: "Restrição que o Selo já obriga não devolve ponto." |
| `42-tecnica-marcial.md` | 99 | a Restrição que pede "estar com a minha arma" não devolve ponto, porque "O Selo já obriga isso" |

*Em 02/10/2026 ele explicou a leitura: "o ponto q a restrição do selo é mais narrativa, ela n realmente aplica uma
restrição nos feitiços, é só algo que você é obrigado a fazer e qualquer feitiço". O Selo não entra na conta de
Restrição, e as quatro linhas saem do livro. A da Técnica Marcial é a única em que isso muda número: nessa rota o Selo é
ter a arma em uso ("O seu Selo é ter o equipamento em uso"), e sem a linha uma Restrição "estar com a minha arma" devolve
ponto por uma coisa que o lutador marcial já faz o tempo todo. É para ele olhar quando mexer no capítulo; a ficha não
tem a rota marcial e não muda por isso.*

**Como foi conferido.** *O `regressao-amaldicoada.py` ganhou sete checagens: o título de cada seção de ponta a ponta, as
duas linhas de respiro, as 727 caixas calculadas como referência pura, o nome e a Classe na cor de título, o estado fora
dela, nenhuma caixa abrindo em minúscula em nenhuma das onze fichas, e a aba sem caixa de seleção. O
`regressao-construir.js` digita por cima do `No domínio` no Sheets de mentira e confere que a conta volta com um aviso,
que apagar a caixa também devolve, que a Forma e o nome do feitiço ficam como o jogador pôs, e que a fórmula que não é
referência pura não é regravada. O `regressao-paleta.js` acende o vermelho e o âmbar na grade que a troca lê e confere
que a planilha termina igual à da troca sem aviso, e que a troca seguinte desfaz o vermelho gravado por uma antiga. Nos
arneses: o `arnes-pessoal.py` ganhou quatro defeitos (46), o `arnes-paleta.py` dois (9), e o `arnes-amaldicoada.py` perdeu
o da caixa do Selo e ganhou seis (35). O `arnes-amaldicoada.py` tinha um erro de aspas na perturbação da proteção do
cobrir-se, e não rodava; foi consertado antes da volta. Rodado nas perturbações novas ou mexidas (16 e 17, do Domínio;
18, da vaga do Leque; e 27 a 32, as seis do B31), acendeu as nove, cada uma na checagem dela. A bateria inteira passou
antes: os vinte e um.*

**O que só o Sheets diz, e falta ele ver:** *o aviso na tela quando digita por cima; a conta voltando na planilha em
português; a paleta rosa com o nome das cartas no acento; e a `Livres · Fechadas` dele saindo do vermelho na primeira
troca de paleta depois de colar o `Codigo.gs` novo. A aba mudou de forma (o respiro, as caixas que apontam para a
`DADOS_AM`, a caixa do Selo que saiu): para ver, é montar de novo com o `Ficha.gs` novo.*

### B32 · As quatro rotas da Ficha Amaldiçoada e o menu rápido na seção 8 da `FICHA` — **FEITO em 02/10/2026, e montado no Sheets pelo Mizuki no mesmo dia: "está funcionando"**

*O ponto 7 do B31, com o desenho fechado lá, rodada a rodada. Pela escolha dele ("Pode ser A": as rotas antes, e tudo
numa construção só), a aba nas quatro rotas e o menu foram feitos juntos.*

1. **A `FICHA AMALDIÇOADA` muda conforme a Origem da `FICHA`, na forma A do estudo.** *A rota sai das marcas que a
   `FICHA` já tinha (sem energia, Técnica Marcial, Sem Técnica): Fundamento, Sem Técnica, Técnica Marcial com energia
   (o Corpo Amaldiçoado) e Técnica Marcial sem energia (a Restrição Celestial). O que o livro muda de rota para rota
   saiu dos capítulos pelo `extrair_tecnica.py` (a chave `rotas` do `tecnica-do-livro.json`, conferida frase a frase):*
   - *os nomes: os títulos, o Selo, o Orçamento, os lotes, as caixas de graça e os saltos dizem `Manejo`, `Liberação
     Máxima` e `Auge` no Sem Técnica, `Kata`, `Ruptura` e `Ōgi` na Técnica Marcial, e Bênçãos e Lapidação no lugar das
     aptidões e do refino na sem energia;*
   - *a linha da rota, na seção da Técnica: a rota, a semente (Sem Técnica) ou o equipamento (Técnica Marcial), o que a
     semente dá ou se o golpe simples fere maldição, e, na rota de arma, os três grupos com o atributo, a conjuração e a
     CD de cada um (a Lâmina Longa acerta com o maior entre Força e Destreza). A linha de cima da Técnica diz o atributo
     das armas quando os grupos concordam, e "Por grupo" quando misturam (a CD na rota de arma, resposta A);*
   - *os menus: a Técnica Marcial compra as Passivas do capítulo dela e a Passiva Própria (resposta B), o Sem Técnica as
     duas listas, a sem energia compra Bênçãos, e o Corpo Amaldiçoado não compra a Extensão de Domínio;*
   - *a Expansão de Domínio: fora do Fundamento a seção diz que a rota não tem, e não gasta espaço de feitiço;*
   - *a linha do Estímulo Muscular, nas Bênçãos da sem energia: a perícia, o Teste de Resistência e os usos (1× por
     cena, 2× na Lapidação 10).*

   *A aba foi de 539 para 548 linhas. O link de cada salto passou a citar a célula do nome dele na `DADOS_AM`, que muda
   com a rota.*
2. **O menu rápido no lugar da seção 8 da `FICHA` (`ficha-v01/menu_rapido.py`, a limpeza 26).** *Das linhas 119 a 345:
   os feitiços (36 lugares), as Liberações com a Técnica Máxima e o Domínio, as Passivas (14 lugares, a Passiva Livre e a
   Regra Própria primeiro) e as aptidões (14, as duas de graça primeiro). Mini-cartas três por fileira, de 13 colunas
   cada; a Técnica Máxima e o Domínio em carta da largura da seção. São 42 grupos: um por bloco, um por par de fileiras
   empilhadas (o + mora na linha que diz "Feitiços 7 a 12") e um pela descrição de cada fileira. A seção nasce com 63 das
   227 linhas à vista (o primeiro par de cada bloco aberto), e fica em 45 com as descrições fechadas.*

   *Nada ali se digita. Cada caixa aponta para uma célula da `DADOS_AM`, onde a lista é montada sem buraco: o feitiço de
   nome apagado some, e o de baixo sobe. A carta de feitiço mostra a Classe, o nome, o PE, a Forma, como resolve e o
   "Como é" que o jogador escreveu; a de Passiva e a de aptidão, o "seu texto", ou "Do livro: ..." quando ele está vazio.
   Os títulos dizem os nomes da rota e quantos de cada ("FEITIÇOS · 6 de 36"). As linhas do menu ficam fora da trava de
   fórmula (moram em grupo), e quem escreve por cima recebe a conta de volta com aviso, como na Ficha Amaldiçoada.*

   *Saiu com a seção 8: as seis caixas dela no índice (feitiços disponíveis, Passivas, as duas aptidões de graça,
   aptidões disponíveis e Passivas do Leque), o "Refino Atual" impresso, as notas e o aviso vermelho delas no
   `Codigo.gs`, e as notas de graça que o `onEdit` refazia quando a Origem mudava. A conta, o aviso e a nota dessas
   coisas moram na Ficha Amaldiçoada. As duas contas da `DADOS` que liam a seção (aptidões e Passivas do Leque anotadas)
   leem a Ficha Amaldiçoada.*
3. **O que mudou do estudo.** *O menu tem 227 linhas e 42 grupos, e o estudo dizia 216 e 40: as legendas de par e as
   linhas de respiro entre fileiras que o estudo não desenhou. A carta da Técnica Máxima sem nome fica vazia, como a de
   feitiço; a regressão achou ela mostrando a Forma que a aba já traz escolhida ("Projétil") e "Rola". Antes do nível
   dela, o PE mostra "—", como na aba (o desenho da Kaori mostrou "— PE"). O texto do livro, quando o jogador não
   escreveu o dele, vai inteiro se cabe na caixa (a medida do estudo: perto de 260 letras na Passiva, 300 na aptidão e
   na Bênção), e a primeira frase se não cabe. O estudo dizia "a primeira frase" para toda aptidão; a leitura de deixar
   inteiro o que cabe é minha, e fica para ele vetar: 11 das 29 aptidões e Bênçãos e 1 das 24 Passivas vão pela primeira
   frase. O desenho mostrou o Canalizar energia inteiro (553 letras) cortado na caixa. O texto do livro não sai em cinza como no estudo: a cor viria de regra condicional, que não muda
   com a paleta, e o "Do livro:" na frente já separa do texto dele.*
4. **O preço.** *A `FICHA` foi de 150 para 347 linhas, de 7.050 para 16.309 células.*
   - *A troca de paleta passa de 30 s se pintar a `FICHA` de uma vez num Sheets lento. A aba grande vai em trechos de até
     7.500 células, com a régua logo depois do primeiro (a parte de cima é a que ele vê primeiro). A promessa da troca
     mudou: o clique na caixa da paleta pinta a `CARTEIRA` e a `FICHA`, e a Ficha Amaldiçoada, a Ficha Pessoal, o
     Glossário e a arte terminam nos dois cliques seguintes (antes era no primeiro), sem aviso. A aba em que ele clica
     continua passando na frente.*
   - *O `Ficha.gs` foi de 640 para 703 KB (o `Codigo.gs` tem 205 KB). As fileiras de três cartas do menu vão por cópia de
     formato da primeira, como na Ficha Amaldiçoada: sem isso eram 735 KB e mais de 900 chamadas de mesclagem.*
   - *Quem já escreveu na seção 8 de hoje (os feitiços, as Passivas e as aptidões da Kaori, por exemplo): a seção nova não
     tem onde digitar. O que estava lá passa para a Ficha Amaldiçoada, e o menu mostra.*

**Como foi conferido.** *O `regressao-amaldicoada.py` ganhou cinco fichas (as quatro rotas e uma, `menu`, que escreve o
que só o jogador escreve e deixa feitiço sem nome no meio) e duas seções: as quatro rotas (títulos, linha da rota,
grupos de arma, linha de cima da Técnica, menus de cada rota, Domínio, caixas de graça e Estímulo) e o menu rápido em
toda ficha recalculada (a ordem de leitura das cartas, a lista sem buraco, o "Como é", as Liberações, a Técnica Máxima e
o Domínio, as Passivas e as aptidões com o texto do jogador ou o do livro, as duas de graça da rota e os títulos). O
`regressao-construir.js` confere que as caixas do menu só apontam para a `DADOS_AM`, que as mesclagens das fileiras
copiadas chegam na aba montada, e que escrever por cima do menu devolve a conta (com a devolução desligada no
`Codigo.gs`, ela acusa). O `comparar-ficha-01.py` declara a limpeza 26 e fecha em IGUAIS. O `conferir-ficha-xlsx.py`
confere o que saiu do índice e do `Codigo.gs` e as cartas de graça do menu pela rota. A Kaori ficou com o que continua na
`FICHA` (Defesa, X de Y, espaços de feitiço, ataques: 10 de 10 e 20 de 20). Nos arneses: o `arnes-amaldicoada.py` foi de
35 para 57 defeitos (12 das rotas e 10 do menu); o 44, que trocava `>=3` por `>=2` numa fórmula que trata o Sem
Técnica antes, não mudava nada e foi reescrito para fazer o que o nome diz; o `arnes-paleta.py` de 9 para 10 (a troca que pintasse só o primeiro
trecho da `FICHA`), e três trechos dele que tinham ficado velhos com a troca em trechos foram atualizados. Rodados nesta
volta: os 26 da Amaldiçoada que são novos ou mudaram (23, 34 a 57) acendem, cada um na checagem dele; os 10 da paleta e
os 46 da pessoal também. O `medidas/ver-aba.py --aba FICHA` desenha a `FICHA` com a Kaori da Ficha Amaldiçoada, e foi
por ele que o "— PE" e o texto cortado apareceram. A bateria inteira passou: os vinte e um, e a seção do menu na
regressão com 115 checagens (3 gerais e 7 em cada uma das 16 fichas).*

**Montado no Sheets em 02/10/2026.** *Ele colou os dois arquivos, montou e respondeu "pode fazer comit e está
funcionando", com a planilha exportada (`Kaori.xlsx`, uma ficha nova, sem personagem: o menu nasce com "FEITIÇOS · 0 de
36"). Na mesma mensagem ele apontou o número da `CARTEIRA`, que é o B33.*

**O que ele não detalhou, e fica para quando usar:** *abrir e fechar os grupos do
menu (o + de cada par na linha da legenda, o da descrição na linha dos números); escrever por cima de uma carta do menu
(o aviso e a conta voltando); trocar a Origem na `FICHA` e ver a Ficha Amaldiçoada e o menu mudarem de nome, e o Domínio
dizer que a rota não tem; e trocar de paleta, contando os cliques até a última aba terminar.*

### B33 · O número da `CARTEIRA` não acompanha a versão do sistema — **FEITO em 04/10/2026: o catálogo foi posto em dia com o livro reconstruído (ver o B36); em 07/10/2026 o número passou a mostrar a versão com o ponto, `Nº M-1.0` (no fim do B41)**

*Em 02/10/2026, depois de montar o B32: "por sinal a versão n atualizo automatico", com a foto do carimbo da `CARTEIRA`:
`Nº M-0258-····` e `Emitida 02.10.2026`. O livro está na v0.331.*

*O número é `"Nº M-" & DADOS!B1 & "-" & as quatro primeiras letras do nome` (os pontos são o nome vazio da ficha nova), e
a `DADOS!B1` é o `_meta.versao` do `catalogo-projeto-m.json`, que está em 0.258. Foi de propósito: na reextração do
`manual.txt` da v0.263 (22/09/2026, commit 7f83e35) ficou escrito que "o carimbo fica em 0.258, de propósito. Ele é a
versão do CATÁLOGO". As listas da ficha (perícias, Caminhos, Trilhas, equipamento, legados) saem do catálogo, conferido
contra o `manual.txt` da v0.263; só a Ficha Amaldiçoada e a nota das armas leem os capítulos direto, na v0.330. O
número diz a verdade sobre os dados; o que ele não faz é andar sozinho com o livro.*

*Opções levadas a ele: pôr o catálogo em dia com o livro (reextrair o `manual.txt` do PDF da versão atual, conferir, e o
número vai junto), ou o número passar a mostrar a versão do livro em que a ficha foi gerada, ou deixar como está. O
`manual.txt` sai do PDF de coluna única do livro, que estava sendo refeito em segundo plano na hora.*

**Respondido em 02/10/2026: "A".** *Medido antes de mexer: o PDF de coluna única da v0.331
(`Projeto-M-Manual-da-Guilda.pdf`, 380 páginas, gravado às 16:31; o `-A-atual` é um retrato antigo, sem o Incursor), com
`pdftotext -layout`, numa cópia isolada do repositório no lugar do `manual.txt`. A v0.331 está no disco do Claude 2
sem commit, e o CHANGELOG dela diz que "a revisão ampla de nomes, texto e apresentação artística permanece para a
próxima etapa". Passam com o livro novo: o `conferir-kaori.py`, o `conferir-progressao.py`, o `revisao-cetica.py` e o
`regressao-exemplos.py`. Falham sete no `conferir-catalogo.py` e três no `conferir-decisoes.py`:*

| o que | é o livro que mudou? |
|---|---|
| seis Caminhos e dezoito Trilhas ("São seis Caminhos nesta edição, três Trilhas em cada um"); o catálogo tem cinco e quinze | sim: o **Incursor** (d6, vida 6, 4 por nível, 6 PE, Destreza · Força, `Acrobacia` · `Intuição`, treina as treze categorias) e as Trilhas Assassino, Pugilista e Malabarista |
| as Trilhas | sim: dez das quinze mudaram de nome. Brasa virou Combatente Amaldiçoado; Elo, Sutura e Perímetro viraram Arquiteto, Analista e Socorrista; Torrente, Explosivo e Arremate viraram Condutor Armado, Ressonante e Catalisador; Servo, Matilha e Coro viraram Invocação Principal, Parceria e Múltiplas Invocações. Muro, Punho, Estocada, Batedor e Executor ficaram |
| (sem falha no conferidor) as perícias fixas do Bastião | sim: `Atletismo` · `Provocar`; o catálogo tem `Intimidação` |
| a linha 23 da progressão | sim: o nível 23 dá "degrau de Caminho" (era "—") |
| as fontes de vida temporária `Aprumo` e `Crosta`, e de energia `Braseiro` e `Trindade` (`decisoes-ficha.json`); o número do Parrudo | sim: os nomes sumiram do livro com as Trilhas novas |
| armas, treino por categoria, munição, carga | não, ao que parece: no PDF novo o número da página caiu no começo da linha da tabela ("15    Taco…"), e o leitor só tirava do fim. A confirmar no conserto do leitor |

*Na ficha, isso pega o menu de Caminho e o de Trilha, as perícias marcadas pelo Caminho, o treino de arma (o
`Codigo.gs` nomeia os Caminhos), a Empunhadura do Arremate (agora `Arma Condutora`, do Condutor Armado), as notas que
citam Caminho e Trilha, o C1 (o Caminho oculto do menu) e o `decisoes-ficha.json`. A pergunta que espera ele: fazer
agora, contra a v0.331 sem commit, ou depois da revisão de nomes.*

### B34 · A seção 7 da `FICHA` vira "Habilidades" — **FEITA em 02/10/2026 (forma C, escrita à mão, a carta acima do nível riscada); falta montar no Sheets**

*Pedido dele em 02/10/2026, antes de pôr o catálogo em dia: "Recomendo que refaçamos o 'anotações' (ja que agora caminho
da 5 habilidades) e outras partes do ficha que necessitam de 'atualização', para aproveitar melhor das novas partes da
ficha que foram feitas", com protótipos de como pode ficar a seção, "que provavelmente vai mudar para 'habilidades'". E,
no meio da rodada: "nem precisa de automação AINDA (deixar preparado é o ideal), ja q o livro está sendo reescrito,
deixando claro isso".*

*O livro novo (capítulo 35, v0.331 no disco do Claude 2, sem commit) dá ao Caminho cinco degraus, nos níveis 2, 7, 15,
23 e 30, e à Trilha quatro entregas, nos níveis 2, 11, 19 e 27; um degrau pode trazer mais de uma habilidade (o nível 7
do Bastião traz três; o nível 2 do Assassino, cinco). O texto do livro de um nível vai de 136 a 8.562 letras (mediana
944): nenhuma caixa da ficha comporta o texto inteiro, e o jogador anota o nome e um resumo. A seção de hoje tem 30
linhas, doze caixas de 11 colunas por 4 linhas, e não usa as colunas AM a AT.*

*O estudo está em `mockup/habilidades-estudo.html` (`python3 mockup/estudo_habilidades.py`, que lê os nomes e o começo do
texto de cada nível do capítulo 35 só para o exemplo), publicado em https://claude.ai/artifact/VaWxcwKG8eTGUMTVgq8bGq:
quatro formas, todas escritas à mão, com uma caixa fixa por degrau e por entrega e lugar para as escolhas da Trilha e
para as anotações. A três colunas (a de hoje com cinco linhas, 38 linhas), B linha do tempo (uma lista na ordem dos
níveis, 51), C cartas (a linguagem do menu rápido, 36) e D consulta (uma linha por degrau com uso e resumo de uma
linha, o texto num grupo que nasce fechado, 51 com tudo aberto e 24 como nasce). Preparado para o livro: o nível de
cada caixa é fixo, e mais tarde o nome e o texto podem vir de lá pela Trilha e pelo nível sem refazer a seção. A
página também lista o que mais na FICHA pede atualização, na minha leitura (a Progressão contando de novo o que a Ficha
Amaldiçoada conta, a CD por grupo na rota de arma, os nomes da rota no Marco Escolhido), cada um para uma rodada
própria.*

*A pergunta que espera ele: qual forma, valendo misturar. Depois: a caixa acima do nível do personagem diz "Abre no
nível 15" ou fica vazia; e o nome da seção.*

**Escolha de 02/10/2026: "Vai a C mesmo".** *As cartas, na linguagem do menu rápido: um bloco para o Caminho (cinco
cartas e uma de anotação) e um para a Trilha (quatro cartas, as escolhas e uma de anotação), três por fileira, cada
fileira com o seu grupo. O nome da seção é "Habilidades", o que ele mesmo pôs no pedido. Pergunta seguinte: a carta de
um degrau que o personagem ainda não alcançou diz "Abre no nível 15" ou fica vazia.*

**Respondido em 02/10/2026: "A e o texto fica 'riscado' (esqueci o nome), até desbloquear".** *A carta diz quando abre,
e o que estiver escrito nela fica riscado até o nível chegar. O aviso foi para a etiqueta do nível, que ganhou três
colunas ("Nível 15" quando abriu, "Abre no 15" quando não), porque o nome é onde o jogador escreve e não pode ser conta.
O estudo foi atualizado com isso (mesmo link).*

**Como ficou (a limpeza 27, `ficha-v01/habilidades.py`).** *A seção 7 vai da linha 88 à 124: o título "HABILIDADES", o
bloco do Caminho (as cartas dos níveis 2, 7, 15, 23 e 30, e uma de anotação) e o da Trilha (2, 11, 19 e 27, as escolhas
da Trilha e uma de anotação), três por fileira, com um grupo por bloco e um pelo texto de cada fileira; nasce aberta a
primeira fileira de cada bloco. O nome e o texto de cada carta são do jogador. A etiqueta de nível e o título de cada
bloco ("CAMINHO · BASTIÃO · CINCO DEGRAUS") são conta numa tabela da `DADOS_AM`, e a caixa da FICHA só aponta para ela:
fica fora da trava, e quem escreve por cima recebe a conta de volta, como no menu rápido. O riscado é regra de cor
declarada no ABAS (`=LEFT($D$92,4)="Abre"` sobre o nome e o texto da carta), que o `corDeEstado_` junta às regras dele,
porque ele troca todas as regras da FICHA; ela só risca, sem mudar cor, para não brigar com a troca de paleta. O menu
rápido passou a começar na linha 125 (o `menu_rapido.trocas` recebe a linha e as células da seção 7 que não pode
apagar). A arte de respingos que morava no canto da seção foi para o lado do título (AQ a AS, três linhas), onde as
cartas não chegam. Os níveis das cartas são os do livro novo (cap. 35 da v0.331); o catálogo da v0.258 e o
`manual.txt` da v0.263 ainda dão ao Caminho só quatro degraus (sem o 23): é o atraso do B33.*

**Como foi conferido.** *O `regressao-amaldicoada.py` lê os níveis das cartas na tabela "Entregas por nível" do capítulo
35 do livro (quando o livro está na máquina) e confere, em toda ficha recalculada, a etiqueta de cada carta pelo nível e
o título de cada bloco pelo Caminho e pela Trilha (a ficha `menu` escolhe Bastião e Muro). O `regressao-construir.js`
confere que as 11 contas da seção só apontam para a `DADOS_AM`, que a FICHA montada tem as 9 regras de riscar junto com as
outras, e que escrever por cima da etiqueta devolve a conta. O `comparar-ficha-01.py` declara a limpeza 27 e fecha em
IGUAIS; o `conferir-ficha-xlsx.py` confere a arte no lugar novo. O `medidas/ver-aba.py` desenha a riscada (a regra de
fórmula) e a Kaori com quatro habilidades escritas, até a do nível 15; o desenho bate com o estudo. Nos arneses: o
`arnes-amaldicoada.py` vai a 60 (a etiqueta abrindo um nível depois, o Caminho de volta a quatro degraus, o título
esquecendo a Trilha) e o `arnes-pessoal.py` a 48 (o riscado apagado pelo corDeEstado_, a etiqueta que não volta). No
caminho, o `tecnica-do-livro.json` e o `equipamento-do-livro.json` passaram a dizer v0.331: o livro no disco do Claude 2
virou v0.331 durante a rodada, e a bateria acusou os dois arquivos; o conteúdo que a Ficha Amaldiçoada e a Ficha Pessoal
leem é o mesmo, e só o carimbo mudou (o Ficha.gs não mudou com isso).*

**O que só o Sheets diz, e falta ele ver:** *o riscado aparecendo e sumindo quando o NÍVEL muda; a etiqueta "Abre no 15"
cabendo nas três colunas; os grupos de cada fileira; e a arte ao lado do título.*

### B35 · A foto da `CARTEIRA` entra na célula, com a moldura em volta — **FEITA em 03/10/2026 (a B+) e MONTADA NO SHEETS: em 07/10/2026 o Mizuki disse "B35 funciono normalmente"; a ligação com a `FICHA PESSOAL` foi feita no B38**

*Pedido dele em 03/10/2026: "Sabe no ficha aonde temos a foto? Então, é uma 'imagem', então não dá pra inserir imagem
nela, tem que ser uma imagem 'solta' por cima que o jogador põe, oq não é muito bom. Eu não sei se teria alguma forma de
manter a imagem, o contorno bunitinho, sem fazer com que o jogador tenha q inserir a imagem do personagem encima da
célula ao invés de na célula. Porque na célula também daria pra ligar a imagem no ficha com o espaço no ficha pessoal".
A moldura era a imagem `carteira-2` DENTRO da caixa `C8:K21`, e uma célula guarda uma coisa só.*

*As opções: A, a moldura solta por cima com o miolo transparente; B, só a borda da célula (perde os cantos chanfrados);
C, a moldura cortada em pedaços nas células em volta; e a B+, a borda no anel em volta da caixa e os dois chanfros como
imagem pequena na célula do canto. A A caiu com a pergunta dele: "se for A, o jogador quando clicar vai acabar clicando
na imagem ao invés do fundo, não?" (a imagem solta pega o clique no retângulo inteiro, até no transparente).*

**Escolha de 03/10/2026: "vamos de B+ ... ai a gente fazer a parte central ser uma celula só mesclada, que o jogador
clica e insere".**

**Como ficou (a limpeza 28, `ficha-v01/moldura_foto.py`).** *A caixa `C8:K21` continua mesclada e do mesmo tamanho
(252 x 300), sem imagem dentro, com "FOTO / 顔" escrito em Yuji Syuku 22 (a fonte do 呪術廻戦 do cabeçalho, a única
das três que tem as letras e o kanji; 22 é o piso de kanji da ficha) e a nota "Clique na caixa e use Inserir › Imagem
› Inserir imagem na célula."; a imagem inserida toma o lugar do texto. A moldura foi para o anel `B7:L22`: as retas
são borda média na régua (que a troca de paleta já repinta), e os chanfros de cima à esquerda (`B7`) e de baixo à
direita (`L22`), os mesmos do desenho antigo, são a arte `carteira-canto`, o traço "/" de canto a canto da célula
(28 x 21 em cima, 28 x 27 embaixo, porque a linha 22 é mais alta). Fica uma margem de uma célula entre a linha e a
foto.*

*Três coisas que a rodada achou e consertou:*
- *a caixa da paleta se ancorava na imagem mais alta da `CARTEIRA` (`acharCaixaDaFoto_`), que era a moldura; com a
  caixa vazia, ia ancorar noutra arte. A `CARTEIRA` passou a declarar a caixa da foto (`foto` no ABAS), e a função lê
  essa caixa primeiro. O `regressao-construir.js` só via que a caixa nascia na CARTEIRA; agora confere o lugar
  (`C26:I26`, `C27:M28`, `C29:M29`, o do Kaori.xlsx);*
- *a troca de paleta põe na arte um piso de contraste de 3,0, e a borda não tem piso: em 30 das 122 paletas a régua lê
  menos de 3,0 contra a tinta, e o canto sairia de outra cor que a reta em que emenda. O canto segue a régua exata
  (`ARTE_DA_BORDA_`, no `Codigo.gs`);*
- *a arte embutida saía 1 a 3 tons fora da cor desenhada (o Pillow 10 reduz com o alfa pré-multiplicado, e o LANCZOS
  estoura a beira do traço), e o canto nascia 8E81C9 contra a borda 8A7EC4. O `emitir_gs.py` passou a tirar a cor da
  arte desenhada, antes da redução; as outras artes mudaram 1 a 3 tons, para a cor que foi desenhada.*

*Conferido pelo `conferir-ficha-xlsx.py` (a regra da moldura, lida do que o script manda para o Sheets: a caixa
declarada é mesclada, sem imagem, com o convite e a nota; o anel com a régua no lado de fora e reta nenhuma nas quinas;
cada quina com uma imagem só, o traço "/" na régua, que a troca pinta na régua exata), pelo `regressao-paleta.js` (os 2
cantos saem na régua exata nas 122 paletas, a troca de verdade), pelo `regressao-construir.js` (o lugar da caixa da
paleta), pelo `regressao-arte.js` (oito imagens, sem a moldura antiga e com os dois cantos) e pelo comparador (IGUAIS,
com a limpeza 28). O `arnes-moldura.py`, novo e rodado à mão, planta nove defeitos na moldura; o `arnes-pessoal.py` vai
a 51 (a caixa da paleta de volta na imagem mais alta e a CARTEIRA sem declarar a caixa, que param a montagem, e
a caixa declarada uma linha mais curta, que tira a caixa da paleta do lugar) e o `arnes-paleta.py` a 11 (o
canto passando pelo piso da arte).*

**O que fica para depois:**
- *a ligação com a `FICHA PESSOAL` (ele: "num geral o jogador colocaria a imagem na carteira e ela iria para o ficha
  pessoal"). A caixa "FOTO DO PERSONAGEM" da FICHA PESSOAL passaria a ser `=CARTEIRA!C8`, e a documentação do Google
  não diz se uma fórmula que aponta para uma célula com imagem inserida mostra a imagem. Espera o teste dele numa
  planilha em branco: uma imagem inserida na `A1`, `=A1` na `B1` e numa outra aba. Se não mostrar, o caminho é o
  `IMAGE` com o link da foto;*
- *o que só o Sheets diz: se a imagem dentro da célula do canto encosta nas bordas da célula ou fica com folga (se
  ficar, aparece um vãozinho na quina, e a saída é a B, só a borda), e a foto inserida no lugar do "FOTO / 顔".*

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

### B36 · A ficha posta em dia com o livro reconstruído — **FEITA em 04/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele conferiu o Incursor, a Defesa e a carga acima do limite ("Sim" nos três), e pediu a mudança da arma sem a Força, que está na terceira etapa do B40**

*Pedido dele em 04/10/2026, antes de mesclar a revisão do livro (a PR #2 do JJK---Project): "atualize a ficha do sistema
pfvr, colocando o que faltava e modificando o que foi mudado (origens ainda vão ser mudadas, mas siga como estão agora)".
O livro passou a ser a candidata editorial reconstruída (`LIVRO-COMPLETO.md`, 382 páginas), e o B33 fechou junto: o
carimbo da `CARTEIRA` passou de `0.258` para `0.331 · 04/10`.*

**De onde o livro entra agora.** *O `manual.txt` deixou de sair do PDF com `pdftotext`: o `extrair-manual.py` o tira do
`LIVRO-COMPLETO.md`, sem as marcas de formatação, com o `#` dos títulos e as tabelas uma fileira por linha (" | " entre
as colunas). O `manual-fonte.json` guarda o arquivo e o hash. O `livro.py` lê seção e tabela. Os dois extratores
(`extrair_tecnica.py` e `extrair_equipamento.py`) deixaram de ler os capítulos do HD e leem o `manual.txt`, que mora aqui.
O catálogo foi remontado do livro e é conferido por outro caminho no `conferir-catalogo.py` (reescrito: 134 checagens,
e 14 perturbações numa cópia acendem todas).*

| o que mudou no livro | o que mudou na ficha |
|---|---|
| seis Caminhos: entrou o **Incursor** (6 + 4 de vida, 6 PE, Acrobacia · Intuição, as treze categorias) | menu de Caminho com seis, tabela de Caminhos da DADOS escrita pelo catálogo (a vida e o PE da FICHA leem a faixa nova), o treino de arma do Incursor |
| o Bastião treina `Atletismo` · `Provocar` | a perícia fixa marcada sozinha |
| dezoito Trilhas, dez com nome novo | menu de Trilha; a Empunhadura do Arremate virou Arma Condutora (Condutor Armado), e o Treino de Combate (Parceria) entrou no mesmo aviso |
| `Incapacitado` virou `Guarda Aberta` | menu de condição |
| Passiva virou **Talento**, Classe Passiva virou **Categoria de Efeito**, Passiva Livre virou **Expressão da técnica** | os textos e rótulos da FICHA AMALDIÇOADA e do menu rápido (CP → CE); as chaves internas continuam `passivas` e `classe_passiva` |
| a Restrição da Classe 0 não devolve mais o dado | a conta da Classe 0 |
| Salto, Queima e **Estilhaço** acrescentam dados; o Remate conta 25% no teto de 4 × Classe | a checagem do teto do feitiço |
| a Técnica Máxima monta com 8, 12 e 16 pontos (eram 8, 8 e 12) | a tabela da DADOS_AM, lida do livro |
| o Toque fica em 1,5 m também na Classe 0; a Onda vai a raio 4,5 m nas Classes 6 e 7; o último degrau de distância é "visão a olho nu" | o alcance das cartas |
| arma empunhada sem a Força: deslocamento pela metade e **sem Destreza na Defesa**; uniforme ou escudo sem a Força: **sem a proteção dele** | a FICHA PESSOAL reescreve o DESLOCAMENTO e a DEFESA da FICHA |
| carga acima do limite: **não anda** (era a metade) | o DESLOCAMENTO vai a 0 m |
| o Volume é decimal (Traje 1 = 0,3; Broquel = 0,5; armas de 0,1 a 4) e soma sem arredondar | a carga |
| XP: desconto da semana até a 7ª e "metade da anterior"; arredonda para baixo **só no fim**, e o positivo menor que 1 vira 1 | o Total de cada missão (o múltiplo de 12,5 saiu do `fora_do_livro`) |
| os Legados viraram narrativo, de rolagem e de exceção; Reencarnado virou **Encarnado** | o catálogo, como o livro está hoje (ele avisou que as Origens ainda vão mudar) |
| as fontes de reserva temporária mudaram (Embalo, Refluxo, Proteger a Manifestação) | a A2 do `decisoes-ficha.json` |
| os vetos de combinação (Rápido, Reação, Atrasar, Parado, Armado, Carregar) estão na tabela de Combinar peças | a A3, com sete pares |

*Conferido pelos validadores da bateria, cada um posto no texto novo; os arneses de decisão, de delta, de invocação, da
pessoal e do feitiço passam com as perturbações novas. A prova da conta da FICHA AMALDIÇOADA deixou de ser os 33
feitiços prontos (o livro novo não tem a tabela) e passou a ser os **10 exemplos de montagem** que o livro imprime, cada
um com a frase do resultado conferida: Fio de Arrasto, Peso nas Mãos, Corte Medido nas Classes 2, 3 e 5, o Salto de
exemplo, a Rede de contenção, o Projétil e a Aura com Fura, e o Corte de ruptura. Os dez saem iguais na planilha e no
`conferir_feitico.py`.*

**O que fica para ele, e fica fora desta rodada:**

- **Montar no Sheets** *e conferir o Incursor no menu, a DEFESA com arma pesada sem a Força e a carga acima do limite.*

**O que ele decidiu depois, ainda em 04/10/2026, e já está na ficha:**

- **A vida inicial da Vanguarda: "Toda vida inicial é a máxima do dado".** *A tabela de Características dela no livro
  reconstruído só traz "Vida por nível 5". O ganho por nível é a média do dado para cima, e os cinco Caminhos que o livro
  numera obedecem (12/7 é d12, 8/5 é d8, 6/4 é d6); 5 por nível é o d8, então a Vanguarda começa com 8. O número não
  mudou, mudou a fonte: o `fora_do_livro` do catálogo guarda a regra, e o `conferir-catalogo.py` confere os seis
  Caminhos contra ela. A checagem antiga só via se o catálogo e o `fora_do_livro` batiam entre si, e ficava verde com 10
  nos dois; a nova acende.*
- **A troca de duas perícias por arma: "Até duas armas, ja q todo caminho da no máximo duas pericias".** *O livro diz
  "pode trocar duas das cinco perícias por treino em uma arma específica", sem dizer quantas vezes. A ficha já fazia
  assim desde a extensão de 17/09/2026 (o menu vai até "2 armas (-4 pericias)"); agora a decisão está registrada.*
- **A falha e a posição da semana na mesma missão: "Sim, falta colocar as duas opções".** *O livro aplica as duas ("Sua
  terceira missão da semana era longa e terminou em falha com metade da recompensa. A conta é 200 × ½ × ½ = 50 XP."). O
  menu de desconto da FICHA PESSOAL ganhou, para cada posição que paga menos que cheio, a versão com falha pela metade
  dela (da "3ª · 50% · falha", que paga 25%, à "7ª · 3,125% · falha"); a "Falha · metade" continua para as duas
  primeiras. A `regressao-ficha-pessoal.py` passa todas as combinações pela planilha e confere o exemplo do livro.*

**Achado na bateria final:** *a troca da faixa dos Caminhos na FICHA (`DADOS!$N$5:$U$10`, para caber o Incursor) passou o
escape do `re.sub` para dentro da fórmula, e a vida e o PE da FICHA davam `Err:508`. Só a `regressao-kaori-na-ficha.py`
viu, porque as outras comparam o script com a planilha gerada, e os dois saíam quebrados iguais. Consertado no
`dados_catalogo.py`, e o `conferir-ficha-xlsx.py` passou a reprovar fórmula com barra invertida.*

**Fica para outra rodada:**

- **A ficha da invocação** (`ficha-invocacao/`) *segue o capítulo 16 da v0.251. O livro reconstruído reescreveu as
  invocações e trocou as Trilhas do Evocador; refazê-la é uma rodada própria, e ele decidiu em 04/10/2026 que fica para outra parte do trabalho ("pode deixar a reconstrução das invocações na ficha para depois mesmo, isso irei fazer em outra parte"). O `invocacao.json` declara a pendência, e
  o `conferir-invocacao.py` acende se a declaração sair.*
- **A ficha .docx da Kaori** *é de 07/09 e marca Intimidação. O `conferir-kaori.py` passou a ler o quadro da Kaori no
  livro, que vence a .docx onde os dois trazem o campo.*

**Achado em 06/10/2026, e consertado: o `comparar-ficha-01.py` saía vermelho desde esta rodada.** *Com o `original.xlsx`
no lugar (a exportação de 17/09/2026), ele terminava em "22 DIFERENÇA(S) NÃO EXPLICADA(S)", todas da tabela dos
Caminhos: vinte células de `DADOS!N4:T10` (a coluna `O`, que era o dado e virou os atributos naturais; `T5`, o Provocar;
as linhas 8 e 9, com o Emanador antes do Evocador; a linha 10, do Incursor) e as duas fórmulas da `FICHA` que leem a
faixa (`J26` e `J30`, de `$U$9` para `$U$10`). Ninguém viu porque do B36 ao B39 a bateria rodou sem o `original.xlsx`,
que é gitignored e só mora no checkout principal, e o comparador parava em "falta ficha-v01/original.xlsx".*

**As causas são duas, e nenhuma das 22 é mudança indevida.** *(1) A limpeza 8 só aceitava célula das colunas `A` a `L`
(a trava de 15/09 contra a coluna `AB`), e a tabela dos Caminhos mora de `N` a `T`: o `dados_catalogo.valores()` já a
trazia, e a regra a barrava. (2) O `monta.py` troca a faixa nas fórmulas da `FICHA` e o comparador não refazia a troca;
como a ficha automática embrulha essas duas em `IFERROR` depois, a limpeza 12 dele esperava a fórmula com a faixa de
antes. As mudanças foram conferidas uma a uma: a `FICHA` lê a tabela por `VLOOKUP` pelo nome do Caminho, nas colunas 3, 4
e 5; o `Codigo.gs` lê pelo cabeçalho ("Caminho", "perícia fixa"); nada lê a coluna `O`; e a ordem das linhas é a do menu
e a do livro (Bastião, Vanguarda, Guia, Emanador, Evocador, Incursor).*

| peça | o que mudou |
|---|---|
| `ficha-v01/dados_catalogo.py` | `e_dos_caminhos` (a célula é da tabela), `com_a_faixa` e `trocas_na_ficha` (o que o `troca_na_ficha` aplica): uma função, dois leitores. O que o `monta.py` escreve não mudou (o `Ficha.gs` e o `Habilidades.gs` saem iguais) |
| `comparar-ficha-01.py` | refaz a troca da faixa na ordem do `monta.py` (depois do índice, antes do TR) e ganha duas regras na limpeza 8: a célula da tabela dos Caminhos com o valor do catálogo, e a fórmula da `FICHA` em que só a faixa muda |
| `ficha-v01/extrair.py` e `layout.json` | a frase da limpeza 8 declara a tabela dos Caminhos e a faixa (a mesma frase nos dois; o extrator a escreve igual) |
| `conferir-ficha-xlsx.py` | duas checagens novas: a tabela dos Caminhos traz os seis do menu, na ordem, com os atributos, a vida, o PE e as perícias fixas do catálogo; e a vida e o PE da `FICHA` leem a tabela da primeira linha à última |

**Por que o `conferir-ficha-xlsx.py` entrou:** *o comparador só vê o que difere da exportação. A linha do Incursor
vazia e a faixa parada em `$U$9` saem iguais a ela, e nenhum validador cobrava o que a tabela diz (só o menu, na coluna
`A`). As duas checagens novas leem a tabela pelo cabeçalho, como o `Codigo.gs`, e o catálogo direto.*

**Conferido:** *o comparador fecha em IGUAIS, com 20 células da tabela e 2 fórmulas contadas, e as outras contagens
iguais às de antes do conserto. Dez defeitos plantados na ficha gerada: os oito que diferem da exportação acendem no
comparador (outra perícia em `T5`, o nome errado e outra vida na linha 10, `O6` em negrito, `U5` escrita fora da
tabela, a faixa até a linha 11, a coluna 2 no `VLOOKUP`), e os dois que voltam a ser iguais a ela (a linha 10 vazia, a
faixa de volta a `$U$9`) acendem no `conferir-ficha-xlsx.py`, com a Intimidação de volta em `T5`.* **Bateria, com o
`original.xlsx` copiado do checkout principal: os vinte e um de antes do B40 passaram, e, com o B40 já na `main` e o
conserto em cima dele, os vinte e dois passaram.**

**Fica como está:** *o `layout.json` é de uma exportação anterior à do `original.xlsx` de 17/09 (o extrator, rodado
hoje numa cópia, escreve outro arquivo: a exportação já traz a ficha automática montada). O comparador fecha assim desde
antes, e reextrair é rodada própria.*

### B37 · As cartas de Habilidades trazem o livro, numa coluna só — **FEITA em 05/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele disse que o texto cabe ("Cabe sim")**

*Pergunta do Mizuki sobre as cartas da seção 7 (B34), que nasceram escritas à mão e prontas para o livro: "nas caixas
de habilidades dos caminhos e trilhas, imagino que vai ser automatico / mas... vai caber? kkkk".*

**A medida.** A caixa de texto da carta tem 13 colunas de 28 px por 6 linhas de 21 px, em Roboto 10: umas 7 linhas,
perto de 340 letras. Medidas com a fonte, contra o livro reconstruído, as 109 cartas (6 Caminhos com 5 cada, 15 Trilhas
e as 3 rotas do Batedor com 4 cada, menos o nível 7 do Incursor, que é espalhado): o texto inteiro cabe em 4, a carta
típica pede 23 linhas e a maior, 133 (o nível 2, que é a mecânica central de cada Caminho e Trilha, pede 47 no meio).
O primeiro parágrafo cabe em 108, mas às vezes não diz o principal (o Chega Mais abria só com "O raio de Olhos Em Mim
aumenta para 9 m."). Aumentar a caixa não dava.

*A primeira versão, abaixo, foi a de três cartas por fileira com o resumo; a coluna única, mais abaixo, substituiu o
resumo pelo texto inteiro.*

**O que ele escolheu:** *"B - mas dando permissão para o jogador apagar o texto e colocar oq preferir"*: o nome e o
resumo do livro na carta, o texto inteiro na nota. E, perguntado no mesmo dia: a rota do Batedor se escolhe no menu de
Trilha (*"No menu de Trilha"*), e o nome tem duas linhas (*"Nome em duas linhas"*). A Rajada Marcial do Pugilista, que
o livro dá no nível 7 e que "Não acrescenta um novo degrau de Trilha no nível 7", vai na carta 7 do Caminho: *"No caso
do pungilista, o nv7 seria do caminho mesmo, sei que é uma trilha ligada a um nv do caminho, mas é aonde pensei"*.

**Como ficou:**

| peça | o que faz |
|---|---|
| `ficha-v01/extrair_habilidades.py` | lê do `manual.txt` o nome, o resumo e o texto de cada habilidade, e grava o `habilidades-do-livro.json`. O começo de cada uma é a marca do livro ("Nível N:", "Nível N.", o título "Nível N — Nome", um título com "nível N" ou com o nome); cada marca abre um trecho, e o trecho vai para a habilidade dona dela (o Pugilista intercala o nível 7 no meio do 2). O resumo é o primeiro parágrafo; se ele é curto (menos de 80 letras) ou só a linha de ficha ("Reação + 2 PE."), leva o seguinte junto, e tudo fica em frases inteiras até 330 letras: com a fonte, todos cabem em 6 linhas, uma de folga. O nome vai inteiro até 75 letras (os de até 73 cabem nas duas linhas; os de 84 ou mais pedem três); acima, "as primeiras e mais N", em 3 nomes do nível 2. `--confere` refaz e compara, e todo texto gravado tem de estar no manual |
| `ficha_automatica.trilhas_do_menu` | o menu de Trilha com o Batedor aberto nas três rotas ("Batedor · Yumi"), lidas dos títulos do livro; a Vanguarda passa a ter 5 entradas, e o menu, 20 |
| `ficha-v01/habilidades.py` | publica na DADOS_AM o endereço do nome e do texto de cada carta (ADDRESS, que anda com a planilha), põe o nome em duas linhas (31,5 pt) e escreve o `apps-script/Habilidades.gs` |
| `apps-script/Habilidades.gs` | o texto do livro, 111 habilidades (a 111ª é a carta 7 do Incursor com a Rajada Marcial). Mora num terceiro arquivo do Apps Script porque são uns 220 KB, e o `Ficha.gs` iria a 950 KB, acima do teto de 900 KB que o `conferir-ficha-xlsx.py` guarda; a montagem também não ganha 111 células de texto longo |
| `Codigo.gs`: `habilidadesDaFicha_`, `cartasDaFicha_`, `habilidadeQueFica_` | quando o Caminho ou a Trilha mudam, escreve o nome e o resumo como valor solto (não fórmula: o `devolverConta_` devolveria a conta por cima do jogador) e o texto na nota. Só reescreve a carta vazia ou ainda com um texto do livro daquela carta; o que o jogador escreveu fica, e a nota continua sendo o livro. Apagar a carta deixa ela vazia, e ela volta a encher na próxima troca de Caminho ou de Trilha |

**Conferido:** pela `regressao-amaldicoada.py` (o `--confere`, o endereço de cada carta, o nome em duas linhas, o
`Habilidades.gs` igual ao gerador e abaixo do teto, todo Caminho e toda Trilha do menu com as cartas completas, o menu
com as rotas do livro, a carta junta do Pugilista, e o nome e o resumo dentro da medida); pelo `regressao-delta.js` (a
conta do script contra o livro inteiro: todo Caminho com cada Trilha dele, a troca, o que o jogador escreveu, a carta
apagada, sem Caminho, o Pugilista); e pelo `regressao-construir.js`, na planilha montada, pelo onEdit de verdade. O
`arnes-delta.py` planta 6 defeitos novos (vai a 37), o `arnes-pessoal.py` 3 (vai a 54) e o `arnes-amaldicoada.py` 3 (vai a
63); todos acendem. *O do nome em uma linha só passava calado na primeira rodada: a checagem media a altura contra a
constante do próprio gerador, e mudar a constante mudava a checagem junto. Agora ela mede contra a linha comum da FICHA
(o dobro de 15,75 pt).*

**Fica para ele, no Sheets:** colar o `Habilidades.gs` (o `COMO-SUBIR.md` virou "Colar os três arquivos"); ver a
altura da caixa (ver a coluna única, abaixo); e ver se o projeto aceita os três arquivos juntos (o teto de ~1 MB que o projeto usa é por arquivo, e as fontes que
achei falam em 50 MB por projeto, nenhuma delas oficial).


**A coluna única, no mesmo dia.** *Pedido dele depois de ver a primeira versão: "faça ser apenas uma coluna ao invés de
três / assim o texto vai ter bastante espaço, mantenha uma boa altura em linhas pra cada carta e vemos se agora cabe
tudo. Não só isso, como n esqueça do espaçamento de uma linha entre uma carta e outra".* Na largura da seção (D a AT,
1.204 px), o texto inteiro pede 9 linhas na carta típica, mas o nível 2 vai a 62 (o do Evocador). Medido: altura igual
de 15 linhas cabia 83 de 111 (a seção iria a uns 170 linhas); do tamanho da maior de cada nível, 111 de 111 e uns 287.
Ele escolheu *"Acompanha a Escolha, mas ainda tendo a caixa retratil da descrição"*, e pediu o texto legível: *"n
esqueça de tentar deixar de forma legivel, espaçar os paragrafos e talz"*.

| o que mudou | como |
|---|---|
| a carta | a largura da seção: a etiqueta e o nome numa linha, a caixa do texto em 4 linhas, num grupo que abre e fecha (nasce aberto), e uma linha vazia antes da carta seguinte. A seção vai de 37 para 77 linhas (da 88 à 164), e o menu rápido começa na 165 |
| o texto | o texto inteiro do livro, na carta; o resumo e o nome encurtado saíram (o nome inteiro cabe numa linha: o maior tem 685 de 1.114 px). Legível: uma linha em branco entre os parágrafos, a tabela e a lista inteiras, e os subtítulos do livro numa linha própria, em negrito (texto rico, `setRichTextValue`). Sai a marca "Nível 7: Ataque Extra." do começo, que a etiqueta e o nome já dizem |
| a caixa estica | o `linhasDoTexto_` conta as linhas pela largura de cada letra da Roboto 10 (`ficha-v01/larguras-roboto-10.json`, do `medir_fonte.py`: somar as letras dá a medida da frase com 0,16% de diferença no meio e 0,56% no pior caso), e o `alturaDaCaixa_` divide a altura pelas 4 linhas da caixa (no texto mais longo, uns 285 px cada, longe de qualquer teto de altura de linha). Estica quando o Caminho ou a Trilha mudam e quando o jogador escreve numa caixa, as livres inclusive |
| a nota | só aparece quando o texto da carta não é o do livro: aí ela mostra o livro |

**Conferido:** o `regressao-delta.js` (70 checagens: o script conta as linhas dos 111 textos igual ao gerador em
Python, a caixa comporta o texto e sobra só o arredondamento, o negrito cai exatamente nos subtítulos, os parágrafos vêm
separados); o `regressao-construir.js` (pelo onEdit de verdade: as cartas, a altura de cada caixa, o negrito, o texto do
jogador sem negrito e com o livro na nota, a caixa livre que estica); e a `regressao-amaldicoada.py` (a largura da
seção, a linha vazia entre as cartas, o grupo que abre e fecha, a medida do `Habilidades.gs` igual à das colunas da
planilha, e toda letra do livro na tabela). Os arneses ganham os defeitos da coluna única: 65 no `arnes-amaldicoada`, 57
no `arnes-pessoal` e os do `arnes-delta`. O `medidas/ver-aba.py` desenha as cartas com o livro e a altura que o script
dá, e passou a respeitar as quebras de linha do texto (o Sheets respeita).

**Fica para ele, no Sheets:** a altura da linha de texto é estimada (18 px por linha de Roboto 10); se sobrar ou faltar
espaço embaixo do texto, o número mora no `LINHA_PX` do `habilidades.py`.

**O nível 7 da Vanguarda, no mesmo dia.** *O Mizuki notou que a Vanguarda era o único Caminho com uma habilidade só no
nível 7 ("o nv7 do vanguarda é o unico caminho com só uma habilidade, né?") e escreveu a segunda: "Execução Preparada:
1× por Sequência, ao Concluir depois de duas ou mais Conduções, imponha −1 a um TR adicional da Conclusão."* Ela entrou
primeiro no livro (D42 do `JJK---Project`, que o registra em `revisao-interfaces/CORRECOES-APLICADAS.md`), e daí na ficha:

| o que mudou | como |
|---|---|
| `manual.txt` | tirado de novo do `LIVRO-COMPLETO.md` (hash `e747cf74…`). Só mudaram a linha da tabela da Vanguarda ("Ataque Extra e Execução Preparada") e o parágrafo novo |
| a carta 7 da Vanguarda | "Ataque Extra e Execução Preparada", com os dois textos |
| o subtítulo | o extrator tirava a marca "Nível 7: Ataque Extra." inteira do começo do parágrafo, porque a etiqueta e o nome da carta já diziam. Com duas habilidades na mesma carta, a segunda ficava sem nome. Agora, quando a carta junta mais de uma e o parágrafo abre com o nome de uma delas, o nome fica, como subtítulo em negrito, como já ficava no Bastião 7, que o livro escreve com títulos. Mudou em três cartas: Vanguarda 7 (Ataque Extra e Execução Preparada), Vanguarda 2 (Sequência de Condução e Escola de Arma) e Executor 2 (Finta de Execução) |

**Conferido:** a `regressao-amaldicoada.py` ganhou a checagem do subtítulo. Ela acha no `manual.txt`, na seção de cada
Caminho e Trilha, os parágrafos "Nível N: Nome." de carta que junta habilidades, e exige o nome em subtítulo seguido do
texto, no `Habilidades.gs` e no que o extrator tira hoje (são 5 nomes, entre eles a Execução Preparada). O
`arnes-amaldicoada.py` vai a 66: o extrator que volta a tirar o nome acende a checagem nova.

### B38 · A foto da `CARTEIRA` na `FICHA PESSOAL`, e o nome da técnica da `CARTEIRA` na `FICHA AMALDIÇOADA` — **FEITA em 05/10/2026; a foto ele testou no Sheets (07/10/2026: "B35 funciono normalmente", respondendo sobre a ligação da foto com a `FICHA PESSOAL`); o nome da técnica ele testou no mesmo dia: "Funciona"**

*Pedido dele em 05/10/2026: "uma coisa q é bom implementar na ficha e notei q faltou / 1 - A imagem que for colocada
na carteira aparecer no ficha pessoal / 2 - Nome da técnica aparecer na ficha amaldiçoada". As duas seguem o que a
ficha já faz com o nome do personagem: a `CARTEIRA` é onde se escreve, e as outras abas mostram.*

**A foto (a ligação que o B35 deixou para depois).** A caixa FOTO DO PERSONAGEM da `FICHA PESSOAL` virou
`=CARTEIRA!$C$8`, o canto da caixa da foto que a `CARTEIRA` declara (`foto`, do `moldura_foto.py`, o mesmo endereço que o
`Codigo.gs` usa para ancorar a caixa da paleta). *A documentação do Google não diz se uma fórmula que aponta para uma
célula com imagem inserida mostra a imagem: procurei em 05/10/2026 e só achei a função `IMAGE`, com link, e um relato de
que o `IMPORTRANGE` não traz imagem inserida de outro arquivo, que é outro caso.* Por isso a caixa ficou fora da trava:
se a foto não aparecer, o jogador insere a mesma foto nela, por cima da conta, sem aviso. A nota diz isso.

**O nome da técnica.** Perguntado, ele escolheu *"Espelha a CARTEIRA"*: o jogador escreve uma vez, no campo TÉCNICA
DECLARADA da `CARTEIRA`, e a caixa NOME DA TÉCNICA da `FICHA AMALDIÇOADA` mostra. Ela é referência pura para uma conta da
`DADOS_AM` (`=CARTEIRA!$O$27&""`), como toda caixa calculada da aba: quem escreve por cima recebe a conta de volta pelo
onEdit. O aviso dessa caixa é outro: *"O nome da técnica vem da CARTEIRA, e a caixa voltou. Para mudar, escreva na
TÉCNICA DECLARADA de lá."* A aba declara a caixa em `da_carteira`, e o `devolverConta_` escolhe o aviso por ela. O
campo da `CARTEIRA` é achado pelo rótulo (a caixa logo abaixo de "TÉCNICA … DECLARADA"), e o gerador para se não houver
caixa ali.

| peça | o que mudou |
|---|---|
| `ficha-v01/ficha_pessoal.py` | a caixa da foto aponta para a foto da `CARTEIRA` e entra nas `livres` (fora da trava); a nota nova |
| `ficha-v01/ficha_amaldicoada.py` | `campo_da_tecnica`, a caixa NOME DA TÉCNICA com a conta, a nota, e `da_carteira` na aba |
| `ficha-v01/monta.py` | passa `da_carteira` para o `Ficha.gs` |
| `apps-script/Codigo.gs` | o `devolverConta_` escolhe o aviso da `CARTEIRA` |

**Conferido:** o `conferir-ficha-xlsx.py` (uma caixa só da `FICHA PESSOAL` aponta para a foto declarada, do tamanho de uma
foto, com a nota e fora da trava); o `regressao-pessoal.js` (a trava cobre toda fórmula da aba, menos o Volume dos
itens, o que mora em grupo e, agora, só a fórmula que é exatamente a referência da foto); a `regressao-amaldicoada.py`
(a caixa aponta para a conta, a conta lê o campo achado pelo rótulo na planilha gerada, a aba declara a caixa, e a Kaori,
com "Peso Emprestado" escrito na `CARTEIRA`, mostra o nome depois de recalculada no LibreOffice); e o
`regressao-construir.js` (escrever por cima devolve a conta, e o aviso manda escrever na `CARTEIRA`, e o da caixa comum
não). Os arneses ganham: o `arnes-moldura.py` 2 (a caixa que deixa de apontar e a que entra na trava; vai a 11), o
`arnes-pessoal.py` 2 (o aviso que esquece a `CARTEIRA` e a aba que não declara a caixa; vai a 59) e o
`arnes-amaldicoada.py` 3 (a caixa escrita à mão, o script que não sabe de onde ela vem, e o campo uma linha abaixo, que
para o gerador; vai a 69). Todos acendem.

**Fica para ele, no Sheets:** inserir uma foto na caixa FOTO da `CARTEIRA` e olhar a `FICHA PESSOAL`. Se a foto não
aparecer, me avise: o plano B é o jogador inserir nas duas, e o C é o script copiar a imagem (o Apps Script lê e grava
imagem de célula, pela documentação dele).

### B39 · As duas aptidões de graça do menu rápido mostram o valor — **FEITA em 06/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele disse "Certinho"**

*Pedido dele em 06/10/2026: "na ficha, tem as aptidões (e lapidações) base, seria bom se o mecanico (pelo menor o
valor), estivesse incluso / ja q é um acesso rapido da ficha amaldiçoada".* **As cartas das duas de graça, no menu rápido
da `FICHA` (seção 8), traziam só o "Do livro:", e o valor morava na `FICHA AMALDIÇOADA`, nas caixas do cabeçalho de
APTIDÕES E REFINO.** *Agora a carta abre com o mesmo valor, e depois vem o texto do livro:*

- **Cobrir-se de Energia:** *"Proteção 1 · Reação de Cobrir-se: RD 1 por 2 PE. Do livro: …"*
- **Canalizar Energia:** *"+1d4 na arma. Do livro: …"*

*Na Restrição Celestial sem energia são a Defesa sem Armadura e o Estímulo Muscular, com os mesmos números na
Lapidação, e a reação vira "Reação da Defesa".* **A carta lê as três caixas da `FICHA AMALDIÇOADA`, e não refaz a conta:**
*a regra continua num lugar só.* Como o menu é montado antes da aba, os três endereços passaram a nascer no layout, como o
do Refino, e a aba confere que a caixa sai neles.

| peça | o que mudou |
|---|---|
| `ficha-v01/ficha_amaldicoada.py` | `apt_cobrir`, `apt_canalizar` e `apt_reacao` no layout, e a aba confere que a caixa sai neles |
| `ficha-v01/menu_rapido.py` | o texto das duas cartas de graça abre com o valor |
| `apps-script/Ficha.gs` | as duas fórmulas novas (e só elas: o resto do arquivo saiu igual) |

**Conferido:** a `regressao-amaldicoada.py` refaz o valor pelo refino de cada uma das 20 fichas de teste, nas quatro
rotas, e confere a carta recalculada no LibreOffice (354 checagens, todas passando); o `arnes-amaldicoada.py` ganha 2
(a carta volta a mostrar só o livro, e a do Canalizar mostra a proteção do Cobrir-se; vai a 71), e os dois acendem.
**Dos vinte e um, vinte passam; o `comparar-ficha-01.py` pede o `original.xlsx`, que é a exportação da planilha viva e não
está no repositório.** *Rodado numa máquina de nuvem com o Python 3.12 (o 3.11 não lê as f-strings do gerador), o
LibreOffice Calc instalado na hora e as fontes baixadas do Google Fonts. O `Ficha.gs` e o `Habilidades.gs` saíram iguais
aos commitados antes da mudança; o `.xlsx` e a arte da carteira, não (outra versão de `openpyxl`, de Pillow e das
fontes), e por isso não foram subidos daqui: rode o `monta.py` na sua máquina para o `.xlsx` acompanhar.*

**Fica para ele:** colar o `Ficha.gs` novo no Sheets e olhar o menu rápido.

**Achado de passagem, para depois:** o `manual.txt` saiu do livro de antes da D43 (`manual-fonte.json`, hash
`e747cf74…`). O livro de hoje tem a D43 (Condição, Prende e Cerca pedem TR), o nome Ciclo Maldito e a D44 (a Execução
Preparada da Vanguarda com −2): a carta 7 da Vanguarda ainda diz −1. Puxar o livro novo é rodar o `extrair-manual.py` e
pôr o catálogo em dia, que é uma passada própria.


### B40 · A aba `INVOCAÇÕES`, a invocação refeita depois do livro reconstruído — **CONSTRUÍDA E MONTADA NO SHEETS em 07/10/2026 (quatro etapas, no fim desta seção): ele testou a grade, o inventário, a devolução da conta e a ficha sem travas. Ficam com ele a regra da arma sem a Força no livro, a lista da revisão e o destino da `ficha-invocacao/` antiga**

*Pedido dele em 06/10/2026: "precisamos olhar o como fazer a ficha de invocação após a atualização do sistema", com
protótipos antes de aplicar. É a pendência que o B36 deixou ("pode deixar a reconstrução das invocações na ficha para
depois mesmo, isso irei fazer em outra parte").*

**O que o livro mudou.** *A invocação deixou de ser ficha derivada do dono (orçamento da Trilha, Traço, Comando, Investir,
Sintonia) e virou **entidade**, com ficha própria: 9 pontos de atributo e 1 por marco, ataque e CD com a maestria do
invocador, três Famílias abertas com uma Livre, uma básica, especiais montadas por Classe e pontos, talentos por marco,
quatro formas de aquisição (capítulo 17), e as regras de campo num capítulo à parte (16). Da `ficha-invocacao/` de
antes, que segue a v0.251, quase nada serve; ela e os três validadores dela não foram tocados nesta rodada.*

**O estudo, em cinco rodadas** *(`mockup/invocacao-estudo.html`, `python3 mockup/estudo_invocacao.py`).*

| rodada | o que eu trouxe | o que ele disse |
|---|---|---|
| 1 | quatro formas, numa página de site com campos soltos | *"Eu n gostei de nenhuma das opções ... algo mais, visualmente atrativo, semelhante as outras paginas ... tendo como colocar a imagem da invocação, nome e afins"*, e o estudo *"no formato de ficha de excel/planilhas"* |
| 2 | a aba na grade da planilha: A deitadas e empilhadas, B deitadas lado a lado, C em pé | *"Que tal fazer a A+B? umas 2-3 colunas com a mesma lista que temos na A, ai umas 5-6 linhas ... mantem o 'conjunto' ali na esquerda"*; Buff/Debuff *"que nem no sistema da ficha principal"*; Liberação Máxima, Expansão e Técnica Máxima, *"n precisa de automação para liberar ou n essas abas, so deixa oculto"* |
| 3 | a grade de fichas, o conjunto à esquerda, o Buff/Debuff e os trunfos | *"2 x 6 acho q fica bom, so recomendo aumentar a largura da imagem"* |
| 4 | a foto com 15 colunas | *"Deixa um pouco mais largo e ta bom assim, de uma avaliada se falta nada na ficha e ta aprovado"* |
| 5 | a foto com 17 colunas, e a conferência contra o livro | *"aprovado"* |

**O que a conferência contra o livro acrescentou, e ele aprovou:** *o tipo de dano e a resolução (ataque ou Teste de
Resistência) em cada habilidade; o equipamento, com o limite de carga de 5 + Força; o bônus de cada perícia treinada; a
reserva da domada e a carga do talismã; cinco menus de Família, porque as Trilhas do Evocador abrem uma ou duas a mais; o
grupo fechado "Repertório da Trilha", com três cartas e três talentos de Categoria 1 para as escolhas a mais da
Invocação Principal e do Repertório do Conjunto; e, no conjunto, o Aprimoramento de Vínculo, a beneficiária, os três usos
da rodada e o limite de quatro ativas em Múltiplas Invocações.*

**A primeira etapa da construção: uma ficha, para medir.** *Combinado com ele antes de aprovar: montar uma ficha no
gerador, medir o `construir()` no Sheets, e só então repetir para as doze. `ficha_invocacoes.N_COLUNAS` e
`N_FILEIRAS` estão em 1 e 1; a grade fechada é 2 e 6.*

| peça | o que é |
|---|---|
| `ficha-v01/extrair_invocacao.py` e `ficha-v01/invocacao-do-livro.json` | o que a aba lê do livro e o catálogo não tem: a progressão da entidade, os pontos e o PE por Classe, as Formas, o alcance e a área, os talentos, os tipos, as aquisições, os trunfos da domada, as Trilhas e os aprimoramentos do Evocador. 53 frases do livro conferidas palavra por palavra, cada uma com a conta que a aba tira dela, e os dois exemplos do capítulo 17 |
| `ficha-v01/ficha_invocacoes.py` | **a limpeza 29.** A aba `INVOCAÇÕES`, depois da `FICHA AMALDIÇOADA`, e a aba oculta `DADOS_INVOC`, depois da `DADOS_AM`: as tabelas do livro, uma linha de conta por ficha e uma por carta de habilidade. As Melhorias, as condições, as Restrições e os pares proibidos são os da `FICHA AMALDIÇOADA` (`ficha_amaldicoada.regras()`) |
| `apps-script/Invocacoes.gs` | **o quarto arquivo do Apps Script.** Com uma ficha o `Ficha.gs` foi de 760 para 950 KB, acima do teto de 900 KB por arquivo; com as doze passaria de 1,3 MB. As duas abas saem do `Ficha.gs` e moram aqui. O arquivo só declara a lista delas, e o `juntarAbas_` do `Ficha.gs` as põe no `ABAS`, cada uma depois da aba que ela nomeia, no arquivo que carregar por último, porque o Apps Script não promete a ordem dos arquivos. Sem ele no projeto a ficha é montada sem as duas abas |
| `apps-script/Codigo.gs` | o `onEdit` devolve a conta de quem escrever por cima de uma caixa calculada da aba, como na `FICHA AMALDIÇOADA` |
| `regressao-invocacoes.py` | **entra no `rodar-tudo.sh`, que passa a ter vinte e dois.** Os exemplos do livro com o número que o livro imprime, o Buff/Debuff, o que a ficha recusa, e 18 fichas sorteadas com 157 cartas (77 fora da regra, de propósito) contra a regra escrita de novo em Python |
| `medidas/ver-aba.py --aba "INVOCAÇÕES"` | desenha a aba com o Cão de sombra do livro |

**O que mudou do estudo, e por quê.** *O estudo foi desenhado numa grade de colunas finas, como os outros. Com doze
fichas a aba teria 120 mil células nessa grade, e a troca de tema é feita célula a célula. Como a `FICHA AMALDIÇOADA`,
cada coluna tem a largura do que guarda:*

- **A ficha são três blocos de cinco colunas de 96 px** *(a foto, os números e a mesa), que são também as três cartas de
  habilidade de cada fileira. Cada carta fica com 480 px, a largura das da `FICHA AMALDIÇOADA`; no estudo ela tinha 364,
  o tamanho que ele achou "mt amassadinho" lá. A foto fica com 480 por 399 px.*
- **O Buff/Debuff fica embaixo do número, e não ao lado**, *em toda caixa calculada: é o que deixa cada valor numa
  coluna só. O atributo mostra o total, os pontos embaixo e o Buff/Debuff embaixo dos pontos.*
- **A carta de habilidade ganhou a linha AMPLIAR**, *como a de feitiço: a mesma especial numa Classe maior, com o dano e o
  PE de cada Classe que o nível já liberou. É o "poderá ser ampliada para 4d8 por 6 PE" do Cão de sombra.*
- **A ficha ficou mais larga:** *1.496 px, contra 1.204 no estudo. Com uma ficha a aba tem 1.985 px (o
  `decisoes-ficha.json` guarda); com as duas colunas, perto de 3.500.*
- **A lista do conjunto ainda não leva até a ficha:** *é texto; a ligação pede o número da aba, e entra com a grade.*

**Conferido:** *a bateria inteira rodou em 06/10/2026 com o `original.xlsx`: dos vinte e dois, vinte e um passam, a `regressao-invocacoes.py` entre eles (os exemplos do livro batem um a um, e as 157 cartas sorteadas também). O que sai vermelho é o `comparar-ficha-01.py`, pelas 22 diferenças do B36 descritas abaixo, que são de antes desta rodada. O `construir()` roda inteiro no Sheets de mentira com a aba nova, nas duas ordens de carga dos arquivos, e a troca de tema passa a aba em passos, como a `FICHA`. O `Ficha.gs` ficou com 760 KB e o `Invocacoes.gs` com 170. Nada disto rodou no Sheets de verdade.*

**O que fica para ele:**

- **Colar o `Invocacoes.gs` no projeto do Apps Script, como quarto arquivo** *(e o `Ficha.gs` e o `Codigo.gs` novos),
  rodar o `construir()` e mandar o registro de tempo: é ele que diz se as doze fichas cabem, e em quantas execuções.*
- **Olhar a aba no Sheets:** *a foto inserida na caixa, o Buff/Debuff embaixo do número, os grupos de linhas e os dois de
  colunas (o conjunto e a coluna de fichas), e os menus de Melhoria, que só trazem as Famílias abertas da ficha.*

**O que falta fazer aqui, depois da medida:**

- *a grade de 2 × 6, com as fileiras de fichas vindo por cópia de formato;*
- *a ligação de cada linha da lista do conjunto com a ficha dela;*
- *um arnês para a aba, como o `arnes-amaldicoada.py`;*
- *decidir com ele o que fazer da `ficha-invocacao/` e dos três validadores da invocação de antes.*

**Achado de passagem:** *o `comparar-ficha-01.py` já saía vermelho antes desta rodada, com o `original.xlsx` de
17/09/2026: 22 diferenças não explicadas na `DADOS` e na `FICHA`, todas do B36 (o Incursor na tabela dos Caminhos, o
Bastião com Provocar, a faixa `N5:U10`). Conferido numa cópia do commit `676f093`, sem nada desta rodada. Ele não
aparecia porque as últimas rodadas rodaram sem o `original.xlsx`.* **Consertado no mesmo dia: ver o fim do B36.**


#### B40, segunda etapa (07/10/2026): a medida dele, a grade de 2 × 6 e o retorno de quem leu a aba

**A medida, com uma ficha.** *Ele colou os quatro arquivos, rodou o `construir()` e mandou o registro: "Deu certinho,
apareceu aq". `FICHA PRONTA em 288s`, numa execução só. Abas criadas 62,9 s · CARTEIRA 5,2 · FICHA 38,5 · FICHA
AMALDIÇOADA 23,4 · **INVOCAÇÕES 8,0** · FICHA PESSOAL 8,2 · DADOS 5,1 · DADOS_AM 15,5 · **DADOS_INVOC 18,6** · GLOSSÁRIO
1,4 · menus 12,8 (350 menus) · travas 81,3 (70 travas) · o resto do acabamento 6. A planilha que ele exportou
(`Ficha - Era da Revolução.xlsx`) não tem erro de fórmula em nenhuma das duas abas da invocação.*

**O que a medida diz das doze fichas.** *Sobravam 72 s dos 360, e as doze fichas trazem dez vezes as células de uma:
a aba vai de 203 × 26 para 1.196 × 45 (54 mil células) e a `DADOS_INVOC` de 86 × 406 para 159 × 446 (71 mil). Pela
medida, a aba visível custa de 1,3 a 2,1 s por mil células e a oculta 0,5 a 0,6: a `INVOCAÇÕES` deve levar de 80 a 110 s
e a `DADOS_INVOC` uns 40. A montagem das abas sozinha fica perto dos 300 s, e com o acabamento passa dos 360. **Não cabe
mais numa execução.***

| o que mudou | por quê |
|---|---|
| **`N_COLUNAS, N_FILEIRAS = 2, 6`** no `ficha_invocacoes.py` | a grade que ele fechou. Doze fichas, 156 cartas de habilidade, 5.188 mesclagens, 1.093 faixas de menu |
| **as fileiras de fichas vêm por cópia** | a segunda fileira é o molde da terceira à sexta, em cinco trechos (o que fica entre as fileiras de cartas, que já eram cópia da primeira). A primeira não serve de molde, porque divide as linhas com o conjunto. A cópia vai coluna de fichas por coluna de fichas (`k[5]` do `copias`), porque a lombada do nome atravessa os trechos e o Sheets não copia meia mesclagem. O `compactar` do `emitir_gs.py` passou a exigir que as duas pontas de uma mesclagem estejam na MESMA cópia, e a diz qual lista não voltou quando o desenho não fecha |
| **a linha de cada carta na `DADOS_INVOC` é igual em todas** | o nível em que a carta abre e o título dela estavam escritos dentro da fórmula, e a coluna de erros sozinha pesava 535 KB. Agora saem das colunas `abre` e `tit`, e a fórmula é preenchida para baixo |
| **o `Invocacoes.gs` ficou com 437 KB** | com a grade ligada e nada mais ele saía com 1,2 MB, acima do teto de 900 KB por arquivo. O `Ficha.gs` tem 790 KB |
| **o `construir()` para sozinho, e o `continuar()` segue** (`ficha/modelo.gs.js`) | antes de começar cada aba ele estima o custo dela pela medida de 06/10 (2,4 ms por célula na aba visível e 0,7 na oculta, o pior de cada tipo com uns 15% a mais) e, se a conta passar de 300 s, guarda em que aba parou (propriedade `montagem_parada`) e pede o `continuar()`. A primeira aba de cada execução sempre é montada. O `acabar()` recusa rodar por cima de uma montagem parada, e o `construir()` do zero esquece a parada de antes logo no começo. Pela conta, são **duas execuções**: a primeira para antes da `DADOS_INVOC`, e a segunda faz ela, o `GLOSSÁRIO`, os menus e o acabamento |
| **a lista do conjunto leva até cada ficha** | a `DADOS_INVOC` publica a tabela de saltos (a caixa, o alvo e a célula do texto), e o `ligarSaltos_` do `Codigo.gs`, que já fazia os dez da `FICHA AMALDIÇOADA`, escreve as doze ligações no acabamento. O alvo é o número da lombada da ficha, que fica à vista com a fileira e a coluna fechadas. Quem escrever por cima de uma linha recebe a conta de volta, e a ligação é refeita na hora |
| **a régua da aba troca de cor em quatro partes** | a troca de tema tem 30 s por execução. A aba tem 7.810 faixas de borda e 25 chamadas, contra 8 da `FICHA AMALDIÇOADA`, e o passo dela sozinho passava do tempo num Sheets lento (o teste 8 da `regressao-paleta.js`). A aba com mais de 8 chamadas vai em partes (`borda:INVOCAÇÕES:0` a `:3`); as outras continuam num passo só, com o nome de sempre. A cor da aba vai em oito passos. **A troca de tema inteira fica bem mais longa** do que era com cinco abas |

**O retorno de quem leu a aba.** *Ele mostrou a aba a um amigo e trouxe os pontos durante a rodada:*

| o que ele disse | o que mudou |
|---|---|
| *"ele achou desnecessario ter o 'tarefa' na ficha, pq o player iria escrever algo q ele fala pro mestre na mesa assim?"* | saiu a caixa `TAREFA` |
| *"tira esse 'abre no' e coloca ou só o nível que nem o primeiro, fica mais bonitinho"* (o amigo, sobre a coluna dos talentos) | o rótulo de cada talento é sempre `NV 6 · CE 1`. Quem escolher um talento antes da hora continua vendo o aviso ao lado. O título da carta de habilidade ainda diz `ABRE NO NÍVEL`, e ele não falou dele |
| *"n tem necessidade dessas caixas q basicamente vc muda durante o turno, tipo movimento ali. reduzir, vida, modificadores, energia e essas coisas tudo bem"*; *"Básica do ciclo n faz sentido ter, estado, ordem, n faz sentido"*; *"pra q esse tbm"* (a faixa do Vínculo); *"mais coisa do turno"* (os três usos) | saíram de cada ficha o `MOVIMENTO` que resta, a `BÁSICA DO CICLO`, o `ESTADO` e a `ORDEM PENDENTE`; e do conjunto a `REAÇÃO COLETIVA`, o `DANO NO TURNO`, o `VÍNCULO`, o `APRIMORAMENTO DE VÍNCULO` com a beneficiária e os três usos da rodada. Sem o estado, o conjunto mostra o limite de ativas (`ATIVAS, NO MÁXIMO`: 2, ou 4 com Múltiplas Invocações) e não mais a contagem, e a lista e o título da ficha não dizem mais "em campo". O deslocamento com o Buff/Debuff embaixo já estava nos números da ficha, e por isso as duas caixas de movimento da mesa não foram aproveitadas |
| *"ideal o vida máxima ficar lado a lado com vida atual, vida temporaria e ter um redutor automatico, semelhante a ficha de player"* | a mesa abre com `VIDA ATUAL`, `VIDA MÁXIMA`, `TEMPORÁRIA`, `± PERDA / GANHO` e a reserva, e a barra embaixo, na largura inteira. A caixa de ± é do `onEdit` (`redutorDaInvocacao_`): digita −9, ela aplica na vida atual e se limpa, com a mesma conta da `FICHA` (`aplicaPasso_`: a perda gasta a temporária primeiro, e a vida não passa da máxima). Em branco, a vida atual está cheia. A `VIDA MÁXIMA` continua também nos números, com o Buff/Debuff dela. O teto da temporária (metade da máxima), que a `FICHA` prende, não foi posto aqui |
| *"ideal alongar a foto, ficar mt quadradinha achatada é dificil ed achar imagens, ser um pouco, n mt, mais alta que larga ajuda"* | a foto passou de 480 × 399 para **480 × 546 px** (26 linhas). As Famílias saíram de baixo dela e foram para baixo das perícias, no bloco dos números; as anotações e o corpo ganharam as linhas que sobraram na mesa. A ficha desceu só três linhas (198 por fileira) |
| *"a carga n funciona como escrito"*; e, quando perguntei de qual carga: *"carga, a q a invocação carrega, ela em si n pode carregar itens, lembra? precisa de caracteristica"* | saiu a caixa `CARGA MÁXIMA` dos números, que dava a entender que a entidade leva 5 + Força de Volume em itens. O livro (Invocações em campo): "Uma entidade carrega o que suas mãos permitem segurar"; "Transportar carga adicional ou personagens exige uma característica própria ... que ocupe um de seus talentos"; "Sem o talento, fica limitada ao que pode segurar e ao equipamento que pode vestir, dentro do mesmo limite". O limite fica só no título do equipamento, dizendo do que ele é (`EQUIPAMENTO · VESTE E EMPUNHA ATÉ 8 DE VOLUME`), e a nota da caixa diz que transportar pede a característica. O `TR TREINADO` foi para o lugar da caixa, ao lado dos quatro testes. Na conferência achei também um furo na carga do talismã: com ele carregado o `RETORNO` mostrava os 2 × Classe cheios, e o livro abate o que a carga adiantou ("o retorno custaria 8 PE ao todo: os 2 adiantados e mais 6 no retorno"). Agora mostra 6 |
| *"a ficha ta sem o nome nome, que é ciclo maldito e pode por a versão como 1.0, isso vale pra ficha toda"* | o `_meta.sistema` do arquivo de dados é `Ciclo Maldito` e o `_meta.versao` é `1.0`; o carimbo do `decisoes-ficha.json` acompanha. O cabeçalho de cada aba já lia o nome da `DADOS!F1`, e a lombada de cada aba, que vinha escrita da exportação (`PROJETO M`), passa a dizer o nome do arquivo de dados (uma limpeza no `monta.py`, com a diferença registrada no comparador). A versão vai ao Sheets com apóstrofo, como todo texto com cara de número, senão a célula ficaria com 1. O número da `CARTEIRA` passa a ser `Nº M-10-…`: o `M-` não foi mexido |
| *"8 de volume, tá certo isso? n era 5 + força? e n era ideal só ser uma versão 'menor' do inventario do jogador, aonde tem item equipado, item guardado (caso tenha possibilidade) e talz"*; e, das três formas que mostrei: *"pode ser a C, é mais simples, ai faz uma listinha maior de itens guardados, talvez até dividir em duas colunas"* | o 8 estava certo (5 + a Força 3 do Cão de sombra do exemplo). A caixa de texto do equipamento virou um inventário pequeno: três lugares fixos em uso (`MÃO 1`, `MÃO 2`, `VESTE`), cada um com o Volume ao lado, e a lista `GUARDADO · SÓ COM A CARACTERÍSTICA DE TRANSPORTE`, com seis linhas. O título soma as caixas de Volume e compara com o limite (`EQUIPAMENTO · 2,5 DE 8 DE VOLUME`); acima dele acende e diz `PASSOU DO LIMITE`. As linhas saíram das condições (7 para 5) e das anotações (12 para 6), e a ficha não cresceu. **A lista ficou numa coluna só:** as colunas do bloco têm os 96 px das cartas, e com cinco delas duas colunas iguais de item e Volume deixariam o nome do item em uma coluna de 96 px. A aba não tem menu de itens: o nome e o Volume são digitados |

**Conferido:** *a bateria inteira rodou até o fim em 07/10/2026, na versão da carga da entidade (`fb714ae`), com o `original.xlsx`: dos vinte e dois validadores, vinte e um passaram. O que saiu vermelho foi uma checagem da `regressao-amaldicoada.py` ("a aba nova não triplica a montagem"), e o defeito era da conta dela: contava uma cópia por destino na `INVOCAÇÕES`, e desde a grade de 2 × 6 cada destino é copiado uma vez por coluna de fichas (168 cópias na planilha, contra o teto de 133 que ela calculava; com as faixas na conta o teto é 172). Consertada a conta, e depois do inventário pequeno, rodaram de novo e passaram doze dos vinte e dois, os que leem a planilha gerada, o script ou este arquivo: `regressao-construir.js`, `regressao-invocacoes.py` (39 fichas em 19 planilhas, nos doze lugares, com os dois casos do equipamento), `conferir-ficha-xlsx.py`, `regressao-pessoal.js`, `regressao-amaldicoada.py`, `arnes-pessoal.py`, `comparar-ficha-01.py` (IGUAIS, fora as 13 limpezas declaradas), `conferir-decisoes.py`, `arnes-decisoes.py`, `regressao-delta.js`, `regressao-kaori-na-ficha.py` e `regressao-ficha-pessoal.py`; e a `regressao-paleta.js`, que não está na bateria. Os outros dez passaram na bateria e não foram rodados de novo depois do inventário. O `Invocacoes.gs` tem 446 KB.*

**Em 07/10/2026 ele montou a grade no Sheets: "rodou, a ficha salvou certinho".** *Não mandou os registros de tempo; a estimativa de custo de cada aba continua sem conferência contra o Sheets.*

**O que fica para ele:**

- **Colar os quatro arquivos de novo** *(`Ficha.gs`, `Codigo.gs`, `Invocacoes.gs` e o `Habilidades.gs`, que não mudou),
  rodar o `construir()` e, quando o registro terminar em `rode a função continuar()`, rodar o `continuar()`. Mandar os
  dois registros: eles dizem se a estimativa de custo está certa.*
- **Olhar a aba:** *a caixa de ± (digitar −5 numa ficha com nome), a lista do conjunto levando até cada ficha, a segunda
  coluna de fichas, que nasce fechada, e as fileiras 2 a 6, fechadas.*

**O que falta fazer aqui:**

- *~~um arnês para a aba~~ feito na terceira etapa, abaixo (`arnes-invocacoes.py`);*
- *decidir com ele o que fazer da `ficha-invocacao/` e dos três validadores da invocação de antes.*

#### A terceira etapa (07/10/2026, à noite): o retorno dele depois de montar tudo no Sheets

*Ele rodou o `construir()` e o `continuar()` com o inventário pequeno e passou a lista de testes que eu tinha pedido. O
`construir()` parou sozinho antes da `INVOCAÇÕES`, como desenhado; nesse dia o Sheets estava bem mais lento que na
véspera (abas criadas em **164,9 s**, contra 62,9; `FICHA` em 55,6 s, contra 38,5; `FICHA AMALDIÇOADA` em 37,6 s,
contra 23,4). Os registros do `continuar()` e do `acabar()` ele mandou depois, e estão na tabela abaixo.* **O que funcionou, nas palavras dele:** *o título e a lista
do conjunto preenchendo sozinhos, a caixa de ±, o inventário, as fichas fechadas, os erros das cartas, a troca de tema;
o Incursor no menu, a carga acima do limite, as cartas de Habilidades ("cabe sim"), o nome da técnica (B38:
"Funciona"), o menu rápido (B39: "Certinho") e a foto na `FICHA PESSOAL` (B35/B38: "funciono normalmente").*

| o que ele disse | o que mudou |
|---|---|
| *"1.3: Parou de funcionar, os links da ficha amaldiçoada também"* (a lista do conjunto e os saltos da linha 7 não levam a lugar nenhum) | **a causa: o `acabar()` não tinha sido rodado.** O registro do `continuar()`, que ele mandou depois, termina em `AS ABAS ESTÃO DE PÉ em 304s, MAS FALTA O ACABAMENTO: rode a função acabar()`; sem o acabamento a ficha fica sem saltos e sem a trava de aviso, que ele também não viu ao escrever por cima da perícia. Ele rodou o `acabar()` (166 s: 10 saltos, 12 ligações da lista, 70 travas) e disse: "funciona certinho". Mesmo assim mudou, porque um acabamento cortado no meio das travas daria no mesmo: **as travas são a última etapa**, depois dos saltos e da caixa da paleta; o acabamento do `construir()` não as começava se a execução já tivesse passado de 190 s (as travas levaram 148,2 s no `acabar()` dele, contra 81 e 83 s de antes). Isto valeu por uma etapa: as travas saíram na quarta, abaixo. **E um defeito meu, achado na conferência:** o `onEdit` da `INVOCAÇÕES` religava a lista com vírgula entre os argumentos do `HYPERLINK`, e a planilha vive em português, onde a vírgula não vale; quem escrevesse por cima de uma linha da lista ficava com as doze em erro. O `ligarSaltosDe_` escolhe o separador pelo idioma da planilha, e a `regressao-construir.js` ganhou o teste que faltava (não havia nenhum do religamento) |
| *"1.4: seria bom ao preencher a vida máxima, a vida atual preencher tbm, na criação da ficha, pq a vida atual fica com nada mesmo após criação da invocação"* | a `VIDA ATUAL` nasce apontando para a conta nova `vida0` da `DADOS_INVOC` (a máxima, quando a ficha tem nome; em branco na ficha vazia). É caixa livre (`livres`, no `ABAS`): o jogador escreve por cima, a caixa de ± grava o número, e enquanto ninguém mexe ela acompanha a máxima |
| *"1.7: Recomendo tirar o aviso de clicks, pode vir a incomodar o jogador"* | nada: perguntei de qual aviso ele falava (o script não mostra nenhum durante a troca de tema desde 25/09), e ele respondeu *"Achei q avisava, erro meu"* |
| *"2.2: a gente precisa mexer nessa penalidade, ideal é ser só a desvantagem no ataque e metade do deslocamento, mas tem q mexer no livro tbm, ja pode atualizar na ficha"* (a arma empunhada sem a Força) | a `DEFESA` da `FICHA` deixa de perder a Destreza; o deslocamento continua caindo pela metade; a desvantagem, que não é número, está na nota do requisito de Força (`FICHA PESSOAL`) e na nota do CORPO A CORPO e do À DISTÂNCIA. A regra mora no `fora_do_livro` do arquivo de dados (`arma_sem_a_forca`), com a frase que o livro ainda traz; o `conferir-catalogo.py` acende no dia em que o livro mudar. **O livro continua com a frase antiga: mudar lá é dele** |
| *"6: Escrevi por cima da pericia e n corrigiu. Esses de codigo ideal só impedir de poder modificar. Mas por exemplo, na ficha amaldiçoada q n leva codigo na celula, ele funciona certinho"* | o Sheets não impede o dono da planilha de escrever numa célula (a trava só avisa), e cada jogador é dono da cópia dele. O que dá é devolver a conta na hora, e agora **toda caixa calculada volta, em toda aba** (`devolverConta_`): `FICHA`, `CARTEIRA`, `FICHA PESSOAL` (em grupo ou não), além das duas que já voltavam. A fórmula de fábrica está no `ABAS` em inglês; a `formulaNoIdioma_` a escreve na pontuação do português (ponto e vírgula no argumento, vírgula no número, barra invertida na matriz, o que está entre aspas intacto). Se mesmo assim a caixa mostrar `#ERROR!`, o script a grava como o `construir()` grava, com a planilha em inglês por um instante. Ficam de fora as caixas livres: vida, energia e integridade da `FICHA`, o Volume de um item e a foto da `FICHA PESSOAL`, a vida atual de uma invocação. As travas de aviso ficaram nesta etapa, até ele testar a devolução no Sheets de verdade; ele testou, e elas saíram na quarta etapa, abaixo |
| *"de resto pode aplicar tbm oq vc falou q falta"*: o livro | o `manual.txt` saiu do livro de hoje (v0.340 do `JJK---Project`, hash `bbaf760b…`, baixado do GitHub para a área de rascunho, porque o clone do disco é de 03/10). Três mudanças: o nome (**Ciclo Maldito** em todo o texto), a **D44** (a Execução Preparada da Vanguarda impõe −2, e a carta de nível 7 diz) e a **D43** (*"Condição, Prende e Cerca sempre pedem TR ... Numa ficha de ataque, o acerto aplica o dano e as outras peças; depois, cada alvo acertado faz o TR registrado"*). Pela D43: o texto das três peças no arquivo de dados é o do livro novo; a carta de feitiço de ataque com uma delas diz **`Acerto + TR`** (coluna nova `peça que pede TR` na `DADOS_AM`); a carta de habilidade da invocação diz `Ataque +4 · TR CD 12`; o exemplo `Peso nas Mãos` do `extrair_tecnica.py` usa a frase nova |
| *"de resto pode aplicar tbm oq vc falou q falta"*: o arnês | `arnes-invocacoes.py`, 26 defeitos plantados no gerador (os números da ficha, a entrada e o retorno, o conjunto, a vida que nasce cheia, o inventário, as cartas, a D43) contra a `regressao-invocacoes.py`, e um contra-teste. Roda à mão, como o da Amaldiçoada |

**Os tempos, pelos dois registros dele (07/10/2026, Sheets lento).** *O `continuar()` montou tudo o que faltava numa execução
só e fechou em 304 s, a 56 s do teto do Apps Script:*

| etapa | estimativa | levou |
|---|---|---|
| `DADOS` | 3,5 s | 12,7 s |
| `DADOS_AM` | 18 s | 35,4 s |
| `DADOS_INVOC` (157 × 450) | 49 s | **89,6 s** |
| `GLOSSÁRIO` | — | 3,7 s |
| menus (1.342) | fora da conta | **35,1 s** |
| travas, no `acabar()` | 81 a 83 s | **148,2 s** |

*A estimativa da aba oculta passa de 0,7 para 1,4 ms por célula, o limite da execução desce de 300 para 270 s (os menus
vêm depois da última aba e ninguém os contava) e o teto das travas fica em 190 s. Num dia lento a montagem vai a três
execuções (`construir()`, `continuar()`, `continuar()`), e a última faz o acabamento. O tempo da `INVOCAÇÕES` e o da
`FICHA PESSOAL` ficaram fora do pedaço do registro que ele mandou (as duas juntas, uns 126 s).*

**Dois rótulos das Habilidades, no mesmo dia.** *"cinco degraus fica ruim, coloca 'cinco níveis'. Quatro entregas pra ser
trilha - Quatro níveis, coisas assim q n precisa circundar a informação, só ser direto". O título do bloco diz `CAMINHO ·
CINCO NÍVEIS` e `TRILHA · QUATRO NÍVEIS`. Procurei o mesmo vício nas outras abas e não achei outro rótulo que diga nível
com outra palavra; o `DEGRAU` do Domínio é o termo do livro. Perguntei se o `Abre no 7` da etiqueta das cartas acima do
nível também vira `Nível 7`.*

**A revisão que ele pediu** (*"revisione a ficha se falta algo do sistema nela e me avise"*). *Comparei o capítulo 20 do
livro (Referências e fichas: os modelos de ficha que o próprio livro traz) e as frases "anote" e "registre" dos outros
capítulos com os rótulos e as notas das cinco abas. Não é uma leitura do livro inteiro regra por regra. O que o livro
manda registrar e a ficha não tem onde:*

1. **O traço e os dois Legados da Origem** *(e as escolhas que um Legado pede). A `FICHA` só tem o menu de Origem; os 90
   Legados estão no arquivo de dados e nenhuma aba os usa.*
2. **Sequelas, Cicatrizes e Exaustão.** *A Sequela muda a janela da próxima queda e só sai no descanso longo; a
   Exaustão tem três degraus; a Cicatriz é permanente.*
3. **Condições e usos gastos do personagem.** *A ficha da invocação tem a caixa; a do jogador não.*
4. **Munição:** *na arma, na reserva e "precisa recarregar", por arma. A `FICHA PESSOAL` só tem a quantidade do item.*
5. **As escolhas do Traje:** *o tipo de TR e as perícias (uma a quatro, pela maestria). A aba só tem a situação.*
6. **Resistências e imunidades** *(os dois tipos do Alicerce do Bastião, a imunidade a Envenenado do Corpo Amaldiçoado,
   as dos Legados).*
7. **Na `INVOCAÇÕES`:** *a Integridade da entidade com alma, e os outros modos de deslocamento.*
8. **Na `FICHA AMALDIÇOADA`:** *o espaço de feitiço ocupado por uma invocação adquirida por espaço conhecido não entra
   na conta dos espaços livres.*

*Ficou de fora de propósito, pela decisão dele de 07/10 (ficha de mesa sem caixa de turno): Padrão, Bônus, Movimento e
Reação, a queda em andamento (janela, tratamento) e a folha de entidades na mesa. Nada disto foi construído: a lista é
para ele decidir.*

**Conferido na terceira etapa:** *a bateria inteira rodou até o fim em 07/10/2026, à noite, com o `original.xlsx` e com tudo desta
etapa dentro (o livro v0.340, os tempos novos e os dois rótulos): vinte e um dos vinte e dois passaram, e a
`regressao-paleta.js`, que não mora na bateria, também. O vigésimo segundo era o `arnes-pessoal.py`, com sete defeitos
plantados que citavam o código de antes (o separador do salto, a devolução só da referência pura, a chamada do
acabamento); foram atualizados, ganharam doze novos (a pontuação do idioma, a devolução em cada aba, a caixa livre, a
reserva em inglês, o religamento do salto, o teto das travas) e ele passa: 80 perturbações acendem a checagem certa. Um
deles não acendia por falta de teste (a caixa de ± com a vida atual apagada), e a `regressao-construir.js` ganhou esse
caso. O `comparar-ficha-01.py` fecha em IGUAIS. O `arnes-invocacoes.py` estava rodando quando esta etapa foi para o git
(os cinco primeiros defeitos tinham acendido); o resultado inteiro entra no próximo registro. A primeira bateria desta
etapa morreu no décimo sexto validador, quando a sessão reiniciou.* **Nada desta etapa rodou no Sheets de verdade**, *e a
devolução da conta na pontuação do português é a parte que só o teste dele confirma.*

**O que fica para ele, depois desta etapa:**

- **Colar os três arquivos que mudaram** *(`Ficha.gs`, `Codigo.gs` e `Invocacoes.gs`; o `Habilidades.gs` mudou uma letra,
  o −2 da Execução Preparada) e montar: `construir()`, `continuar()` quantas vezes o registro pedir, `acabar()` se ele
  pedir. Mandar o registro de cada execução.*
- **Testar a devolução da conta:** *escrever por cima do total de uma perícia da `FICHA`, de uma caixa da `CARTEIRA` e de
  uma da `FICHA PESSOAL`. Tem de voltar sozinha, com um aviso, e não pode ficar `#ERROR!`.*
- **Mudar o livro** *na regra da arma sem a Força, e decidir o que entra da revisão.*

#### A quarta etapa (07/10/2026, à noite): ele testou a terceira no Sheets, e as travas de aviso saíram

*Ele colou os quatro arquivos, montou e mandou o resultado dos seis testes:*

| teste | o que ele viu |
|---|---|
| a devolução da conta | *"Passou nas três abas, com aviso no canto. Nenhuma ficou em #ERROR!."* |
| a invocação nova | *"Vida começou cheia: 8/8."* |
| a arma sem a Força | *"Bō exigindo 3, personagem com 0: Defesa continuou 11; deslocamento 9 → 4,5 m."* |
| Condição, Prende e Cerca | *"As três cartas mostraram 'Acerto + TR'."* |
| as Habilidades | *"'Cinco níveis', 'Quatro níveis' e Execução Preparada com −2 conferidos."* |
| os links | *"Lista de invocações e saltos da Amaldiçoada funcionando; cliquei e confirmei os destinos."* |

**A pontuação do português funciona no Sheets de verdade:** *a `formulaNoIdioma_` escreve a fórmula de fábrica com ponto e
vírgula, vírgula no número e barra invertida na matriz, e nenhuma caixa ficou em `#ERROR!`. Era a parte que só o teste
dele confirmava.*

**As travas de aviso saíram.** *Com a conta voltando sozinha, a trava virou um segundo aviso para a mesma coisa, e era a
etapa mais lenta da montagem (81, 83 e 148,2 s nas três medidas dele). O `protegerFormulas_` saiu do `Codigo.gs`; no
lugar dele o acabamento tem o `tirarTravasDeFormula_`, que só tira as travas de uma ficha montada antes (pela
descrição `fórmula · ...`) e deixa as que o jogador ou o mestre criaram. A `FICHA PESSOAL` não declara mais faixas
travadas (`protegidas` saiu do `ABAS`); declara as `livres`. Sem as travas o acabamento levou 17,4 s no registro dele, e
o teto da montagem sobe de 250 para 300 s; o `TETO_DAS_TRAVAS_` e o recado `FALTAM AS TRAVAS` da terceira etapa saíram.*

**O que a trava fazia e a devolução não faz**, *para ele saber: a conta só volta quando o `onEdit` enxerga a edição na
própria caixa. Recortar uma caixa calculada e colar noutro lugar esvazia a origem sem avisar o script (o evento é o do
destino), e inserir ou apagar linha não gera evento nenhum. A trava de aviso também não impedia nenhum dos dois.*

**Conferido na quarta etapa:** *a `regressao-construir.js` ganhou o teste que escreve por cima de cada conta, uma a uma (433
da `FICHA`, 9 da `CARTEIRA`, 286 da `FICHA PESSOAL`), e todas voltam; o teste do `acabar()` numa ficha com três travas
de antes e uma do mestre; e saíram os que cobravam a trava. O `arnes-pessoal.py` trocou as perturbações das travas
pelas da devolução. O `arnes-invocacoes.py` rodou inteiro: 23 dos 26 defeitos acenderam de primeira e três passaram
calados, por lacuna de teste, e não por defeito da ficha: a linha da CONTA das cartas sorteadas não era conferida (a
devolução sem o teto de 2 × Classe e a devolução além do gasto), e o único teste do TR usava Cego e Prende juntos. A
`regressao-invocacoes.py` confere agora a conta de 114 cartas sorteadas e o TR das cartas de ataque, e ganhou os casos
`Laço` (só Prende) e `Garra` (Toque com duas Restrições Médias, que passa do teto); replantados, os três acendem.*
*A bateria inteira rodou até o fim com a ficha sem travas: vinte e um dos vinte e dois passaram, e a `regressao-paleta.js`
também. O vigésimo segundo era de novo o `arnes-pessoal.py`, com três defeitos plantados que citavam o que saiu com as
travas (dois da função que juntava as fórmulas em faixas, e o teto da montagem, que mudou de número); os dois primeiros
saíram, o terceiro foi acertado, e ele passa: 78 perturbações acendem a checagem certa. Esta etapa não tinha rodado no
Sheets de verdade quando foi para o git.*

**Ele montou a versão sem travas, do zero, ainda em 07/10/2026**, *e conferiu os três pontos: escreveu por cima do total de uma
perícia e "a fórmula voltou sozinha, com aviso no canto, sem perguntar 'editar mesmo assim?' e sem #ERROR!"; os links
das invocações e os saltos da Amaldiçoada "funcionaram após reconstruir"; e a montagem levou **11 min 14 s somando as
execuções, com cerca de 14 s de acabamento**, sem travas. O registro completo de cada execução ele não mandou (só o
resumo), então o tempo de cada aba nessa montagem não está conferido.*

### B41 · A revisão: o que o livro manda registrar e a ficha não tinha — **ESTUDO ENTREGUE em 07/10/2026; espera ele escolher as formas**

*Da lista da revisão (terceira etapa do B40) ele escolheu, em 07/10/2026: "Traços, sequelas, cicatrizes, exaustão,
resistencias e imunidades, integridade da entidade com alma, espaço de feitiço ocupado por invocação". Ficaram de fora
as condições e usos gastos do personagem, a munição e as escolhas do Traje. Ele escreveu "Traços", e o item era "o
traço e os dois Legados": perguntei se os Legados entram.*

**O que cada um é, no livro:**

| item | a regra | o que a ficha precisa |
|---|---|---|
| traço | Escolhas da Origem: "Um traço: escreva um detalhe importante da sua história"; não dá bônus | uma linha de texto |
| Sequelas | uma por queda encerrada; 0, 1, 2 ou 3 antes de cair dão janela de 3, 2 ou 1 rodada, ou Derrotado na hora; saem no descanso longo | um número de 0 a 3 e a janela da próxima queda |
| Cicatrizes | depois da segunda queda na mesma missão, registrada com o mestre; permanente, sem modificador | texto |
| Exaustão | da quarta luta do dia em diante, um degrau por luta, até 3; 1: desvantagem em perícias e ofícios; 2: deslocamento até 4,5 m; 3: desvantagem em ataques e TRs | um número de 0 a 3, o efeito, e o limite de 4,5 m no DESLOCAMENTO |
| resistências e imunidades | vêm de habilidade (o Alicerce do Bastião: dois tipos por descanso longo), de Origem (o Corpo Amaldiçoado é imune a Envenenado) e de Legado | texto |
| Integridade da entidade | "Criaturas que não sejam personagens jogadores usam metade da vida máxima, arredondada para baixo, com mínimo 1"; o corpo não autônomo não tem alma | atual, máxima (conta) e um menu de com ou sem alma |
| espaço por invocação | "um espaço dá uma entidade do seu nível. A vaga continua ocupada quando ela está recolhida" | uma caixa no Orçamento da `FICHA AMALDIÇOADA`, que conta as fichas com aquisição `Espaço conhecido` |

**O estudo:** *`mockup/revisao-estudo.png` (montado por `python3 mockup/estudo_revisao.py mockup/revisao-estudo.html`, e a foto
pelo Firefox sem tela). Quatro blocos, desenhados como a planilha, com o novo em âmbar:*

1. *Sequelas, Exaustão, resistências e imunidades, na `FICHA`: **A** uma linha embaixo das barras, na seção 2; **B** uma
   linha no fim da seção 3; **C** dividido (o estado com as barras, as proteções com a Defesa).*
2. *Traço e cicatrizes: **A** o traço na `FICHA`, embaixo da Origem, e as cicatrizes na `FICHA PESSOAL`, ao lado da
   Aparência; **B** os dois no dossiê da `FICHA PESSOAL`.*
3. *Integridade da entidade: **A** uma linha embaixo da barra de vida, com o estágio; **B** a mesma, sem o estágio.*
4. *O espaço por invocação: uma caixa `EM INVOCAÇÕES` no Orçamento, sem forma para escolher.*

*Indiquei A, B e A. Nada foi construído.*

**O número da `CARTEIRA` (B33), no mesmo dia.** *"atualiza la pra 1.0". O número era `"Nº M-"` + a versão sem o ponto + o
nome, do tempo em que a versão era 0.258 e saía `M-0258`; com a versão em 1.0 saía `M-10`. Passa a mostrar a versão
como é escrita, `Nº M-1.0-KAOR` (uma limpeza no `monta.py`, com a diferença contada no comparador e a checagem no
`conferir-ficha-xlsx.py`). O `M` do número eu não mexi.*

**A pasta `ficha-invocacao/` antiga.** *Perguntei se apagava ou guardava, e ele respondeu "pode atualizar". Não ficou claro
o que atualizar numa pasta que a aba nova substituiu, e perguntei de novo antes de mexer.*

