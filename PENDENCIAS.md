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

> **⚠ Na sua mão:** *colar o `Codigo.gs` novo no projeto do Apps Script, rodar o `construir()` do `Ficha.gs` novo numa planilha nova, trocar a `A1` da central para `0.246`, e conferir no Sheets que o menu do refino escolhido vira número.* **Vai ter campo na Ficha Pessoal, e fica registrado** *(aba de itens e equipamentos, bio, foto e afins):* *a `Couraça` (+1 de Defesa vestindo uniforme) e a arma sem o requisito de Força, que tira a Destreza da Defesa.*


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

