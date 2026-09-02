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

### B1 · O manual está fora da identidade visual

O gerador do manual usa ameixa `741B47`; o servidor e o PDF usam `#211C35` e `#756588`. Os dois roxos **não aparecem em nenhum arquivo do repositório**.

Com a ficha indo para a paleta do servidor, **o manual passa a ser o que está fora**. Isso é um item de correção do repositório, não da ficha.

### B2 · Falta um segundo caso de teste

A Kaori é nível 2, e ela já deixou passar **dois** defeitos:

- não expôs a divergência das Famílias, porque as cinco que ela usa são justamente as cinco que as duas listas têm em comum
- não pegaria o erro de maestria, que só aparece do nível 8 em diante

**Precisa de uma ficha de nível alto** (15 ou mais) como segundo caso, e de preferência com Famílias Livres que a Kaori não usa. Quem é esse personagem é escolha sua.

### B3 · Equipamento entra na ficha?

A ficha de papel não tem campo de equipamento, mas o capítulo 12 existe e **Traje e Revestimento desligam a proteção inicial**, que entra na Defesa.

Enquanto não entrar, a Defesa fica presa em `10 + Destreza + proteção da aptidão`, e qualquer personagem com equipamento terá a Defesa errada na ficha.

### B4 · A checagem 7 das Famílias precisa subir

Não é dúvida, é ação pendente. O `repo-conserto/checagem-7-familias.py` está pronto, acende no estado atual e apaga numa cópia corrigida. Ele conserta um erro que **hoje está na ficha em branco que os seus jogadores usam**.

Isso é independente da ficha digital e vale sozinho.

### B5 · `Lento` nomeia duas coisas diferentes

Achado ao fechar o A3.

| onde | o que `Lento` é |
|---|---|
| tabela de condições (p.32 e p.117) | condição de nível Leve: *"deslocamento pela metade, e sem Ação Bônus"* |
| tabela de Restrições (p.121) | Restrição Média: *"custa a rodada inteira"* |

As duas listas vão aparecer na ficha, e o jogador vai ver a mesma palavra em dois menus significando coisas diferentes. Pior: as duas mexem em Ação Bônus, então a confusão é plausível na mesa, não só na leitura.

É a armadilha de *"a mesma palavra carregando duas escalas"*, e ela já mordeu este projeto antes com a palavra `Classe`.

**Não é decisão de agora, e o conserto é caro:** renomear qualquer uma das duas mexe no manual publicado. Fica registrado.

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

O manual é explícito na p.192: *"Não existe 'atributo de conjuração' na ficha padrão."* A conta é `10 + 2 + maestria`, com o `2` fixo. E ele diz que **algumas habilidades de Caminho trocam esse 2 por um atributo**, e que a habilidade diz qual.

O problema: **nenhuma habilidade do manual faz essa troca.** Procurei em todas. A única coisa que menciona atributo de conjuração é o `Estopim`, nível 11 do Emanador — *"todo feitiço seu soma o seu atributo de conjuração no dano"* — e ele **usa** o número sem que nada o tenha concedido.

Então hoje o Emanador chega no nível 11 e ganha uma entrega que soma zero, ou que o mestre inventa na hora. É a mesma forma do `Casco`: uma entrega que aponta para um número que o sistema não produz.

**A ficha não inventa.** A CD e o ataque de conjuração usam o `2` fixo, e existe uma célula de troca ao lado, vazia, para quando a regra existir.

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

### B12 · A checagem do C1 nunca vai acender

O `conferir-decisoes.py` tem esta linha, e ela existe para avisar quando o
Evocador pode voltar ao menu:

```python
checa("o motivo do C1 ainda vale: o manual segue sem o numero do Casco",
      "Casco — as suas invocações têm mais vida." in MAN, ...)
```

Ela lê o `manual.txt`, que está congelado. **A string vai continuar lá para
sempre, então a checagem sai verde toda vez e nunca vai mudar de estado.**

E o motivo que ela guarda já expirou: dos três buracos que o C1 listou, as
entregas de Trilha fecharam na **v0.164** e o `Casco` virou `Parrudo` com número
na **v0.184/v0.185**. O terceiro era a ficha da invocação, que é o B9 acima.

**A decisão de o Evocador voltar ao menu é do Mizuki.** O que está registrado
aqui é que os três motivos dela caíram.

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

### B14 · O Teste de Resistência treinado da ficha do personagem está atrasado

Não é da invocação, e apareceu ao lado dela.

O `catalogo-projeto-m.json` traz `bonus_se_treinado: 2`, e o `aba_ficha.py` usa
esse `2`. **A peça 1 §4 do sistema diz `TR = d20 + atributo do TR + maestria`**,
e o `+2` fixo morreu na **v0.117** — a entrada daquela versão registra que
*"o `+2` fixo entregava 65% e a maestria entrega 65%, e a mudança inteira caiu
no TR que ninguém treinou"*.

Na ficha isso já erra no nível 2 (`+2` contra maestria `1`) e erra mais no 30
(`+2` contra `4`). **A ficha da invocação usa a maestria**, que é a regra viva,
então hoje as duas fichas discordam entre si.

Junto com ele: o **B8** (`Estopim` somando um atributo de conjuração que não
existe) fechou no sistema na **v0.117** — o `2` fixo morreu e o acerto passou a
levar maestria. A ficha ainda usa o `2`.


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
