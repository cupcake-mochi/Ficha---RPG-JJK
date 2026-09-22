# Como isto vira uma ficha de verdade

**Mudou.** Não tem mais upload nem conversão: a planilha nasce dentro do Google Sheets, montada por um script.

O caminho antigo, pelo `.xlsx`, morreu numa prova. O registro do script devolveu `imagens: 0` — imagem que vem da importação **não é visível pela API**, então nem dava para consertar o tamanho dela. E ela não era a única coisa que a conversão quebrava: fonte, altura de linha, caixa de seleção e o fundo das células mescladas quebravam junto.

Agora nada é traduzido, então nada se perde na tradução.

---

## Os quatro passos

### 1 · Gerar

A ficha é desenhada **no Sheets**, e a pasta `ficha-v01/` é a cópia dela. Exporta a planilha em `.xlsx`, salva como `ficha-v01/original.xlsx`, e roda:

```bash
python3 ficha-v01/extrair.py
python3 ficha-v01/monta.py
./rodar-tudo.sh
```

Sai o `apps-script/Ficha.gs`. Se os dezesseis validadores não passarem, não sobe.

> **O `ficha/monta.py` foi aposentado em 14/09/2026, no B18.** *Ele ficou dez versões atrás da planilha viva, e o `Ficha.gs` que ele gerava montava uma ficha antiga.*

### 2 · Planilha em branco

[sheets.new](https://sheets.new) — cria uma planilha vazia. Dá um nome a ela.

**Instala as três fontes agora**, antes de rodar o script. Numa célula qualquer, seletor de fonte → **Mais fontes**:

```
Oswald  ·  Castoro  ·  Yuji Syuku
```

### 3 · Colar os dois arquivos

**Extensões → Apps Script.**

Apaga o que estiver no `Código.gs` e cola o conteúdo de **`apps-script/Codigo.gs`**.

Depois, no `+` ao lado de **Arquivos**, escolhe **Script**, dá o nome `Ficha`, e cola o conteúdo de **`apps-script/Ficha.gs`**.

> O `Ficha.gs` passa de 100 KB, e boa parte é a arte em base64. É normal ele demorar a colar.

Salva com `Ctrl+S`.

### 4 · Executar

No seletor de funções, escolhe **`construir`** e clica em **▶ Executar**.

Na primeira vez ele pede autorização: **Revisar permissões** → tua conta → **Avançado** → **Acessar** → **Permitir**.

**Demora.** São seis abas, mais de mil células com valor, seis imagens e as caixas de seleção. Conta com um a dois minutos, e não é travamento.

Quando terminar, o registro escreve:

```
FICHA PRONTA em 74s · CARTEIRA: 61 células, 4 imagens · FICHA: ... · cor de estado: 6 regra(s) · notas: 5 nota(s) · protegidas: 15 célula(s)
```

**Não vai ter pop-up.** O aviso vai para o registro de propósito: `alert()` abre na aba da planilha e trava a execução esperando um clique que você não vê.

---

## Se quiser refazer

Roda `construir` de novo. Ela **apaga as abas e monta tudo do zero** — então qualquer coisa que você tenha digitado na ficha se perde.

Enquanto estiver ajustando o desenho, isso é o que você quer. Depois que tiver personagem preenchido, não rode mais.

---

## Publicar para os jogadores

Compartilha como **somente leitura** e manda cada um fazer **Arquivo → Fazer uma cópia**.

A cópia leva os dois arquivos de script junto. O `onEdit` é gatilho simples: funciona na cópia **sem ninguém autorizar nada**, e é ele que faz a caixinha de `±` aplicar dano.

### A planilha central do carimbo

1. Cria outra planilha, escreve a versão do catálogo na `A1` — hoje `0.258` —, e compartilha como leitura.
2. Na ficha, aba `DADOS`, célula `D1`:

```
=IMPORTRANGE("id-da-central";"A1")
```

3. Autoriza uma vez.

Quando o manual mudar, você muda **uma célula** na central e toda ficha em circulação avisa sozinha que está atrasada. Se a central sumir, a ficha perde o aviso e não perde mais nada.

> **⚠ Em 14/09/2026 o catálogo foi da v0.104 à v0.239.** *A aba `DADOS` passou a sair do catálogo, e não da planilha exportada: saíram a condição `Petrificado` e a entrada `Nível`, a Restrição `Lento` virou `Atrasar`, e entrou a Melhoria `Efeito Próprio`.* **Para a planilha viva acompanhar:** *rode o `construir()` do `Ficha.gs` novo numa planilha nova, troque a `A1` da central para `0.239`, e exporte de novo para a `ficha-v01` quando puder.* **As fichas antigas passam a mostrar o aviso de versão, como a A1 prevê.**

> **⚠ Em 16/09/2026 o catálogo foi à v0.246, e a FICHA mudou de desenho num ponto.** *O `EQUIPAMENTO` virou menu de uniforme e escudo, e entrou o `REFINO ESCOLHIDO` ao lado do `BLOQUEAR` — é o B3.* **Para a planilha viva acompanhar:** *cole o `Codigo.gs` novo, rode o `construir()` do `Ficha.gs` novo numa planilha nova, passe o personagem para ela, troque a `A1` da central para `0.246`, e exporte de novo para a `ficha-v01` quando puder.*

> **⚠ Em 17/09/2026 a FICHA passou a contar sozinha (B22).** *Ela saiu da exportação que o Mizuki mandou com o desenho novo, e agora o índice da `DADOS` é fórmula: pode inserir linha no Sheets à vontade, que ele acompanha.* **O mesmo passo a passo de cima vale:** *`Codigo.gs` novo, `construir()` numa planilha nova, e o personagem passado para ela.* **Exporte para a `ficha-v01/original.xlsx` sempre que mudar o desenho, antes de pedir conta nova.**

> **⚠ Na segunda rodada do mesmo dia (B23)** *a FICHA ganhou as caixinhas de Buff/Debuff, o Caminho e a Trilha nascendo em `Escolha…`, e a CARTEIRA ganhou a foto maior.* **O `Codigo.gs` novo é obrigatório:** *é ele que devolve a Trilha ao trocar o Caminho, que muda a nota das aptidões de graça com a Origem, e que põe aviso em toda fórmula.*

> **⚠ Em 20/09/2026 o catálogo foi da v0.246 à v0.258, e o desenho da FICHA não mudou.** *Três coisas de regra entraram: a Concentração e o `Carregar` passaram a rolar contra **a CD de quem te feriu**, e não mais contra `10` ou metade do dano (v0.253 do sistema); entraram as Melhorias `Concentrada` e `Duradoura`, na Família `Tempo` (v0.254), e o `Alvo de Caça`, na Família `Marca` (v0.255).* **A lista de Melhorias da `DADOS` foi de 66 para 69**, *e a coluna inteira desceu três linhas: as três últimas entradas (`Remenda`, `Condição` e `Efeito Próprio`) caíram em células que estavam vazias na exportação e saem em corpo `11` em vez de `12`. É só aparência, e nenhum validador cobre isso — se incomodar, corrija no Sheets e exporte de novo.* **Para a planilha viva acompanhar:** *rode o `construir()` do `Ficha.gs` novo numa planilha nova, passe o personagem para ela, e **troque a `A1` da central para `0.258`** — sem isso toda ficha nova nasce com o aviso `⚠ v0.258 · a atual é a v0.246`, que é o aviso ao contrário.* **O `Codigo.gs` não mudou.**

---

## Quando a ficha mudar

A mudança acontece no Sheets. Exporta de novo, refaz o passo 1, cola o `Ficha.gs` novo por cima do antigo e roda `construir` numa planilha nova. Ficha de jogador não se migra: ele copia o modelo novo e transcreve.

---

## O que ainda não está pronto

- **A montagem de feitiço não trava sozinha.** As oito regras de ouro e os dois pares incompatíveis rodam no `conferir_feitico.py`, mas ainda não viraram Apps Script. É o próximo pedaço caro, e o que mais vale.
- **Equipamento é campo digitado**, até o catálogo do capítulo 12 entrar.
- **O Evocador voltou ao menu em 14/09/2026**, e a decisão C1 registra isso.

O resto está no `PENDENCIAS.md`.
