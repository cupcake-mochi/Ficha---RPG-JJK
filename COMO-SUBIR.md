# Como isto vira uma ficha de verdade

Do repositório até a planilha na mão do jogador. São seis passos, e só o quinto tem chance de dar errado.

**Você faz isso uma vez.** Os jogadores copiam o modelo pronto e não rodam nada.

---

## 1 · Gerar o arquivo

```bash
python3 ficha/monta.py
```

Sai o `ficha/ficha-projeto-m.xlsx`, com as seis abas.

**Nunca edite o `.xlsx` na mão.** Ele é saída, não fonte — na próxima vez que você rodar o gerador, a sua edição some. Se algo precisa mudar, muda no gerador.

Antes de subir, confira:

```bash
./rodar-tudo.sh
```

Dez validadores. Se algum falhar, o arquivo não está pronto.

## 2 · Importar no Google Sheets

Drive → **Novo** → Upload → escolhe o `.xlsx`.

Depois abre ele e vai em **Arquivo → Salvar como Planilhas Google**. Isso converte de verdade; sem esse passo ele fica em modo de compatibilidade e algumas coisas não funcionam.

O que **sobrevive** à importação: layout, cores, fontes, fórmulas, mesclagens, larguras, texto girado, imagens.

O que **não sobrevive**, e é por isso que existe o passo 4: caixa de seleção nativa, formatação condicional, proteção de célula e as notas.

## 3 · Instalar as fontes na planilha

Três das cinco não vêm carregadas. Numa célula qualquer, abre o seletor de fonte → **Mais fontes** → e adiciona:

```
Oswald · Shippori Mincho · Yuji Syuku
```

`Roboto` e `Courier New` já estão lá.

**Faça isso antes do passo 4.** O script aplica fonte, e ele não consegue aplicar uma que a planilha não conhece.

> A `MESA` usa só Roboto de propósito. O app de celular tem menos fontes que o navegador e troca as outras sem avisar.

## 4 · Rodar o script, uma vez

**Extensões → Apps Script.** Apaga o que estiver lá, cola o conteúdo de `apps-script/Codigo.gs`, salva.

Na lista de funções escolhe **`montarFicha`** e clica em executar.

Na primeira vez o Google pede autorização. Ele vai mostrar um aviso de "app não verificado" — é o seu próprio script, e o caminho é **Avançado → Ir para (nome do projeto)**.

O que ele faz:

| | |
|---|---|
| caixa de seleção | nas perícias, ofícios e testes |
| cor de estado | vida e energia viram âmbar abaixo da metade, vermelho abaixo de um quarto |
| proteção | as células de fórmula avisam antes de serem sobrescritas |
| notas | a regra aparece ao passar o mouse |
| fonte | garante Roboto na `MESA` |

**O `onEdit` não precisa de nada.** Ele é gatilho simples: roda sozinho, inclusive nas cópias dos jogadores, sem ninguém autorizar nada. É ele que faz a caixinha de `±` funcionar.

## 5 · A arte (o passo que pode dar errado)

A arte não vai junto na importação de um jeito confiável. Ela entra pelo script, em base64, **sem depender de nenhum arquivo hospedado**.

```bash
python3 arte/gera.py --base64
```

Isso imprime uma linha por peça. Cola tudo dentro do `var ARTE = { ... }` no `Codigo.gs`, e depois chama, por exemplo:

```javascript
colarArte('selo-封', 'CARTEIRA', 'AL25');
```

**Por que assim e não por URL:** `IMAGE()` do Sheets só aceita endereço público. Isso significaria hospedar a arte em algum lugar e a ficha quebrar no dia em que aquele lugar sair do ar. Em base64 a imagem mora dentro da planilha.

**O custo:** o base64 é grande, e colar sete peças deixa o `Codigo.gs` gordo. Se incomodar, cola só o selo e a moldura — são os dois que mais fazem diferença.

## 6 · Publicar o modelo

Compartilha a planilha como **somente leitura** com o servidor, e manda os jogadores fazerem **Arquivo → Fazer uma cópia**.

Cada cópia leva o script junto e o `±` funciona de cara.

### A planilha central do carimbo

A decisão A1 pede uma segunda planilha, só com o número da versão do catálogo.

1. Cria uma planilha nova, escreve `0.104` na `A1`, e compartilha como leitura.
2. Na ficha-modelo, na aba `DADOS`, célula `D1`, põe:

```
=IMPORTRANGE("id-da-planilha-central";"A1")
```

3. Autoriza uma vez, quando ele pedir.

Quando você fechar uma versão nova do manual, muda **uma célula** na central e toda ficha em circulação passa a mostrar o aviso sozinha.

> Se a central sumir, a ficha perde o aviso e **não perde mais nada**. Nenhum menu depende dela — foi por isso que a A1 ficou assim.

---

## Quando o manual mudar

```bash
python3 ficha/monta.py     # regera com o catálogo novo
./rodar-tudo.sh            # os dez têm que passar
```

Sobe o `.xlsx` novo como um modelo novo, e muda a versão na central. As fichas antigas continuam funcionando e passam a avisar que estão atrasadas.

**Ficha de jogador não se migra.** Ele copia o modelo novo e transcreve, ou continua na antiga sabendo que está atrasado. Automatizar migração de planilha é caro e quebra mais do que conserta.

---

## O que ainda não está pronto

Está tudo listado no `PENDENCIAS.md`, mas os três que você vai sentir primeiro:

- **A montagem de feitiço não trava sozinha na planilha ainda.** A regra existe e roda no `conferir_feitico.py`, mas ela ainda não virou Apps Script. É o próximo pedaço caro.
- **Equipamento é campo digitado**, até o catálogo do capítulo 12 entrar.
- **O Evocador está fora do menu**, e volta quando as entregas de Trilha dele saírem.
