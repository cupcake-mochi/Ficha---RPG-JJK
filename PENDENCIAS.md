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

### B31 · O retorno do teste da Ficha Amaldiçoada — **FEITO em 02/10/2026, menos o ponto 7 (a seção 8 da `FICHA`), que espera a resposta dele; falta ver no Sheets**

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

