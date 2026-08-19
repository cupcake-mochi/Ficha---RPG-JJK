# Como isto vira uma ficha de verdade

**Mudou.** Não tem mais upload nem conversão: a planilha nasce dentro do Google Sheets, montada por um script.

O caminho antigo, pelo `.xlsx`, morreu numa prova. O registro do script devolveu `imagens: 0` — imagem que vem da importação **não é visível pela API**, então nem dava para consertar o tamanho dela. E ela não era a única coisa que a conversão quebrava: fonte, altura de linha, caixa de seleção e o fundo das células mescladas quebravam junto.

Agora nada é traduzido, então nada se perde na tradução.

---

## Os quatro passos

### 1 · Gerar

```bash
python3 ficha/monta.py
./rodar-tudo.sh
```

Sai o `apps-script/Ficha.gs`. Se os dez validadores não passarem, não sobe.

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

> O `Ficha.gs` tem 112 KB e a maior parte é a arte em base64. É normal ele demorar a colar.

Salva com `Ctrl+S`.

### 4 · Executar

No seletor de funções, escolhe **`construir`** e clica em **▶ Executar**.

Na primeira vez ele pede autorização: **Revisar permissões** → tua conta → **Avançado** → **Acessar** → **Permitir**.

**Demora.** São seis abas, quase oitocentas células com valor, seis imagens e trinta e oito caixas de seleção. Conta com um a dois minutos, e não é travamento.

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

1. Cria outra planilha, escreve `0.104` na `A1`, compartilha como leitura.
2. Na ficha, aba `DADOS`, célula `D1`:

```
=IMPORTRANGE("id-da-central";"A1")
```

3. Autoriza uma vez.

Quando o manual mudar, você muda **uma célula** na central e toda ficha em circulação avisa sozinha que está atrasada. Se a central sumir, a ficha perde o aviso e não perde mais nada.

---

## Quando o manual mudar

```bash
python3 ficha/monta.py
./rodar-tudo.sh
```

Cola o `Ficha.gs` novo por cima do antigo e roda `construir` numa planilha nova. Ficha de jogador não se migra: ele copia o modelo novo e transcreve.

---

## O que ainda não está pronto

- **A montagem de feitiço não trava sozinha.** As oito regras de ouro e os dois pares incompatíveis rodam no `conferir_feitico.py`, mas ainda não viraram Apps Script. É o próximo pedaço caro, e o que mais vale.
- **Equipamento é campo digitado**, até o catálogo do capítulo 12 entrar.
- **O Evocador está fora do menu**, e volta quando as entregas de Trilha dele saírem.

O resto está no `PENDENCIAS.md`.
