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

Saem o `apps-script/Ficha.gs` e o `apps-script/Habilidades.gs`. Se os vinte e um validadores não passarem, não sobe.

> **O `ficha/monta.py` foi aposentado em 14/09/2026, no B18.** *Ele ficou dez versões atrás da planilha viva, e o `Ficha.gs` que ele gerava montava uma ficha antiga.*

### 2 · Planilha em branco

[sheets.new](https://sheets.new) — cria uma planilha vazia. Dá um nome a ela.

**Instala as três fontes agora**, antes de rodar o script. Numa célula qualquer, seletor de fonte → **Mais fontes**:

```
Oswald  ·  Castoro  ·  Yuji Syuku
```

### 3 · Colar os quatro arquivos

**Extensões → Apps Script.**

Apaga o que estiver no `Código.gs` e cola o conteúdo de **`apps-script/Codigo.gs`**.

Depois, no `+` ao lado de **Arquivos**, escolhe **Script**, dá o nome `Ficha`, e cola o conteúdo de **`apps-script/Ficha.gs`**.

De novo no `+`, **Script**, nome `Habilidades`, e cola o conteúdo de **`apps-script/Habilidades.gs`**. *Desde 05/10/2026: é o texto do livro que vai nas cartas de Habilidades da seção 7 da `FICHA`, e mora num arquivo à parte porque no `Ficha.gs` passaria do teto de tamanho. Sem ele a ficha monta igual, mas escolher o Caminho e a Trilha não escreve as cartas, e a tela avisa.*

E mais uma vez no `+`, **Script**, nome `Invocacoes`, e cola o conteúdo de **`apps-script/Invocacoes.gs`**. *Desde 06/10/2026: são as abas `INVOCAÇÕES` e `DADOS_INVOC`, que não cabem no `Ficha.gs`. Sem ele a ficha monta igual, mas sem essas duas abas. A ordem em que os arquivos aparecem no projeto não importa.*

> O `Ficha.gs` tem uns 790 KB, o `Habilidades.gs` uns 210 KB, o `Codigo.gs` uns 220 KB e o `Invocacoes.gs` uns 440 KB. É normal eles demorarem a colar.

Salva com `Ctrl+S`.

### 4 · Executar

No seletor de funções, escolhe **`construir`** e clica em **▶ Executar**.

Na primeira vez ele pede autorização: **Revisar permissões** → tua conta → **Avançado** → **Acessar** → **Permitir**.

**Demora.** São nove abas (três ocultas), milhares de células com valor, as imagens e as caixas de seleção. Em 01/10/2026 a montagem estourou os seis minutos que o Apps Script dá, e foi reescrita para ir menos vezes ao servidor: **com cinco abas ela levou 220 segundos, medidos pelo Mizuki.** Com a `FICHA AMALDIÇOADA` e a `DADOS_AM` a conta é de uns 285 segundos, e **esse tempo ainda não foi medido.** Não é travamento.

Enquanto roda, o registro mostra cada etapa na hora, com o tempo dela:

```
0s · abas criadas (0.8s)
9s · CARTEIRA (8.2s)
31s · FICHA (22.4s)
...
```

Quando terminar, o registro escreve:

```
FICHA PRONTA em 74s · CARTEIRA: 1503 células, 9 fórmulas, 4 imagens · FICHA: ... · cor de estado: 10 regra(s) · notas: ... · protegidas: ... · tempos: abas criadas 0.8s, CARTEIRA 8.2s, ...
```

Os números do exemplo são inventados: servem só para mostrar o formato. **Se a execução expirar de novo, me mande o registro inteiro:** ele diz em que etapa ela estava e quanto cada uma levou.

**Na `FICHA AMALDIÇOADA` o registro diz como as fileiras de cartas vieram.** O normal é `fileiras copiadas`. Se aparecer `FILEIRAS MESCLADAS UMA A UMA`, a aba está certa do mesmo jeito, mas a montagem demorou mais: me avise, porque aí vale tirar a cópia do caminho.

**Desde 07/10/2026 a montagem não cabe mais numa execução**, por causa da aba `INVOCAÇÕES` com as doze fichas. O `construir()` para sozinho antes de começar uma aba que pode não acabar nos seis minutos, e o registro termina em **`A MONTAGEM PAROU ANTES DA ABA … rode a função continuar()`**. No seletor de funções, escolhe **`continuar`** e clica em **▶ Executar**: ela segue de onde parou. Se o registro pedir de novo, roda de novo. Pela conta são duas execuções ao todo (o `construir()` e um `continuar()`), e a última termina em `FICHA PRONTA`. Enquanto o registro pedir o `continuar()`, a planilha está pela metade: as abas existem, e as últimas estão vazias. *Com uma ficha só, em 06/10/2026, o Mizuki mediu 288 segundos numa execução.*

**Se o registro terminar em `FALTA O ACABAMENTO: rode a função acabar()`** (ou, desde 07/10/2026, em `FALTAM AS TRAVAS DO ACABAMENTO: rode a função acabar()`), as abas já estão de pé e falta o acabamento inteiro (a cor de estado, as notas, os saltos, a caixa da paleta e as travas) ou só as travas, que são a última etapa e a mais lenta. No seletor de funções, escolhe **`acabar`** e clica em **▶ Executar**. Ela pode rodar quantas vezes precisar, sem estragar nada.

**Depois de montar, um teste de um minuto (B38):** insira uma foto na caixa FOTO da `CARTEIRA` (clique nela e use Inserir › Imagem › Inserir imagem na célula) e olhe a caixa FOTO DO PERSONAGEM da `FICHA PESSOAL`. Ela aponta para a da `CARTEIRA`, e a documentação do Google não diz se a foto aparece por referência. **Se não aparecer, me avise.** Enquanto isso, dá para inserir a mesma foto direto na `FICHA PESSOAL`.

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

- **A `FICHA AMALDIÇOADA` confere a montagem de feitiço** desde 01/10/2026 (B29): as regras de ouro e os pares incompatíveis viraram fórmula, e a carta avisa. Ela não impede de escolher: avisa.
- **A seção 8 da `FICHA` continua como estava.** Falta decidir se ela vira espelho da `FICHA AMALDIÇOADA` ou sai.
- **As rotas sem Fundamento** (Técnica Marcial, Sem Técnica e Restrição Celestial) ainda não têm lugar na `FICHA AMALDIÇOADA`.
- **Equipamento é campo digitado**, até o catálogo do capítulo 12 entrar.
- **O Evocador voltou ao menu em 14/09/2026**, e a decisão C1 registra isso.

O resto está no `PENDENCIAS.md`.
