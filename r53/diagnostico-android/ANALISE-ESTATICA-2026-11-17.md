# ANALISE estática · 17/11/2026

Pedido do Mizuki ("Sim, fase 1"), depois da medição numa cópia da Era (fase 0).

## Por quê

- As 18.480 fórmulas da coluna B da ANALISE pesavam em toda execução de script da ficha. Só o bot lê essa aba.
- Na cópia da Era, com a coluna congelada (4 amostras de cada):
  - ± de ~17,1 s para ~14,1 s na execução inteira;
  - `R53_ONEDIT` de ~10,9 s para ~8,4 s.
- Exportando em três partes, cada uma levou de 14 a 19 s. O CSV saiu igual ao vivo: zero diferenças nas 18.500 linhas,
  nas quatro colunas.
- Guardar os modelos numa coluna da própria ANALISE vazou para o CSV do bot (+1,7 MB). Por isso eles moram numa aba
  oculta à parte.
- Nenhuma das 18.480 fórmulas lê a própria ANALISE. A exportação em blocos não depende da ordem.

## O que entrou

| Onde | O quê |
|---|---|
| `apps-script/AnaliseEstatica.gs` (novo) | exportador, aba `ANALISE_MODELOS`, caixa da CARTEIRA, marca de desatualizada, menu Bot |
| `r53/empacotar_script.py` | o arquivo fica fora do módulo comprimido; ganchos no `onEdit` e no `onOpen` da entrada do pacote |
| `nuvem-b47/conferir.py` | o pacote publica `AnaliseEstatica.gs` |
| `ficha/modelo.gs.js` e `apps-script/Ficha.gs` | o `acabar_` do `construir()` exporta no fim (só com o pacote R53) |
| `r53/diagnostico-android/preparar_analise_estatica.js` (novo) | os dois ganchos num Codigo já instalado (oficiais, QAs) |
| `r53/testes/analise_estatica.js` (novo) | planilha falsa, ganchos, preparador; 24 defeitos plantados |
| `ESQUEMA-ANALISE.md` | formato 13: `analise.estado`, `analise.exportada_em` |

Decisões do Mizuki (17/11):
- a exportação sai pelo menu Bot **e** por uma caixa na CARTEIRA (AT4), porque o app do Android não tem menu;
- o `construir()` exporta no fim;
- a CARTEIRA avisa quando a ANALISE está desatualizada (AH4, ao lado da caixa).

## Como funciona

- **Exportar:**
  1. escreve os modelos na coluna B em blocos de 6.500 linhas (4.000 na caixa, desde 18/11);
  2. espera o cálculo (`flush`);
  3. troca cada bloco pelo valor (`copyTo` com `contentsOnly`) e espera de novo (`flush`);
  4. guarda o progresso e a duração do bloco depois de cada um.

  Um bloco só começa se o tempo já gasto mais a duração do último bloco couber no limite. Na caixa o limite é 16 s
  (18 s até 18/11) contados do começo do `onEdit`, para caber nos 30 s do gatilho simples. Se não couber, o texto diz
  "exportando N/T · toque de novo".
- **A caixa lê a planilha uma vez só** (os modelos). O número de modelos e as linhas de estado vêm das propriedades
  do documento. Motivo: com a ANALISE viva, cada leitura custa de 2 a 3 s, do tamanho que for (ver a prova abaixo).
- **A caixa só existe depois da primeira exportação** (é ela que instala). A primeira sai pelo menu (PC) ou pelo
  `construir()`; no celular a caixa só reexporta.
- **Primeira edição depois de exportar:** marca `desatualizada` na ANALISE e na CARTEIRA. As edições seguintes só leem
  uma propriedade do documento.
- **Escrita à mão na coluna B congelada:** é apagada e marca `desatualizada`.
- **Cópia da ficha:** a primeira edição lê o estado na própria ANALISE.
- **Menu Bot:** junta as fórmulas vivas da coluna B aos modelos antes de exportar. É por ele que entra fórmula nova de
  um preparador. A caixa não junta, para caber no tempo.
- **Ganchos:** moram no Codigo de entrada do pacote, não no `apps-script/Codigo.gs`.
  - O `caminho_leve.js` reconstrói a história do `onEdit` de lá por trechos exatos.
  - O `onEdit` de lá é o de dentro do módulo, chamado depois do gancho.
  - Sem o pacote, a montagem deixa a ANALISE viva.

## Prova numa cópia da Era (17/11)

Cópia nativa (Google Planilhas) com o Codigo da oficial, o `AnaliseEstatica.gs` e os dois ganchos do preparador. A caixa
e o ± foram disparados por uma sonda no `onSelectionChange`, que chama o `analiseNaEdicao_` e o `onEdit` de verdade (o
painel do navegador estava escondido e não aceitava digitação em célula).

**A primeira versão estourou os 30 s.** O que a medição mostrou:

| Passo | Tempo |
|---|---|
| Qualquer leitura da planilha com a ANALISE viva (10 linhas, 18.499 linhas, `getLastRow`) | 2 a 3 s cada |
| Ler as 18.499 fórmulas da coluna B | 7,9 s |
| Gravar a aba de modelos | 13,4 s |
| Um bloco de 6.000 linhas (ler modelos 1,8 s, cálculo 3,9 s, congelar 4,3 s) | 10,1 s |
| Abertura do gatilho antes do código | ~7 s |

Também mostrou que **escrita pendente se perde quando o tempo acaba**: a aba de modelos ficou criada e vazia. Daí as
correções: uma leitura por marcação, `flush` antes de guardar qualquer propriedade que aponte para o que foi escrito,
aba de modelos vazia é refeita, e o limite medido pela duração do último bloco.

**Depois das correções:**

| Rodada | Execução inteira | Resultado |
|---|---|---|
| Caixa, 1ª (2 blocos) | 26,6 s | exportando 13.000/18.480 |
| Caixa, 2ª (1 bloco) | 16,4 s | em dia |
| ± (primeira edição, marca) | 15,0 s, `R53_ONEDIT` 6,0 s | desatualizada |
| ± (segunda edição) | 11,5 s, `R53_ONEDIT` 6,2 s | desatualizada |
| Reexportar pela caixa, 1ª (2 blocos) | 21,6 s | exportando |
| Reexportar pela caixa, 2ª (1 bloco) | 15,6 s | em dia |

- **CSV do bot:** comparado com o da ficha viva, linha a linha nas 18.502 linhas. Só 3 diferenças, as esperadas:
  `formato.versao` 12 → 13, e as linhas novas `analise.estado` e `analise.exportada_em`. A aba de modelos não vazou
  para o CSV.
- **±:** na fase 0, a ANALISE viva dava `R53_ONEDIT` ~10,9 s e execução ~17,1 s. Aqui foi ~6 s e 11,5–15 s (duas
  amostras só).
- **No celular, reexportar leva duas marcações** (~22 s e ~16 s).

## Buracos conhecidos

- **Não rodou no Sheets:**
  - o item "Exportar para o bot" do menu (precisa autorizar o script, e isso é com o Mizuki). O menu Bot apareceu
    na barra, então o gancho do `onOpen` funciona;
  - a montagem pelo `construir()`;
  - um clique de verdade na caixa (foi pela sonda);
  - a troca de paleta.
- Edição feita por menu de script (Aplicar cura e afins) não passa pelo `onEdit` e não marca `desatualizada`.
- A troca de paleta pinta as linhas da CARTEIRA que ela conhece. A linha 4 (caixa e texto) pode ficar com as cores da
  paleta de quando foi instalada. Não foi conferido.
- O menu numa execução só é estimativa: ~2 s de leitura, ~3 s para juntar as fórmulas vivas e ~6 s por bloco (três
  blocos), uns 25 s.
- Se a aba de modelos sumir, a caixa tenta refazer: são ~21 s e pode estourar o tempo. O menu refaz com folga.

## Fase 3 · oficiais (só o Mizuki, no PC, depois de backup)

A ordem importa: **o bot precisa ler o formato 13 antes** (PR à parte no RPG---BOT). Em cada oficial:

1. Versão de backup no Apps Script.
2. Arquivo novo `AnaliseEstatica`, com o conteúdo de `apps-script/AnaliseEstatica.gs`.
3. No console do editor, com o Codigo aberto, o trecho de `node r53/diagnostico-android/preparar_analise_estatica.js`.
   Ele só mexe no Codigo de entrada, fora do módulo comprimido. O hash do módulo e o atalho calado não mudam, e não
   precisa achatar de novo. Para desfazer: `--reverter`.
4. Salvar e recarregar a planilha.
5. Menu Bot > Exportar para o bot. Ele cria a `ANALISE_MODELOS`, instala a caixa e exporta.
6. Medir o ± (o `R53_ONEDIT`) e baixar o CSV da ANALISE para conferir `analise.estado = em_dia`.

As oficiais **não** precisam do pacote novo: a mudança do módulo (`acabar_`) só vale para montar ficha nova.

### Feito em 17/11 (registro completo em `r53/OFICIAIS.md`, seção "ANALISE estática")

- Bot primeiro: RPG---BOT#104 mesclada antes da primeira oficial.
- Era e Ciclo: backup, arquivo `AnaliseEstatica`, ganchos (Codigo `c7f388f70e0a` → `57a8398fa8c5`), exportação.
- **O passo 5 não funcionou pelo menu:** "Bot > Exportar para o bot" deu erro genérico, sem execução registrada. Pelo
  editor (Executar `exportarParaOBot`) saiu: Era 93 s, Ciclo 129 s (a Ciclo pediu autorização). A estimativa de ~25 s
  do menu ficou bem abaixo do real, mas a execução pelo editor tem o limite de 6 min.
- CSV das duas: formato 13, `em_dia`, sem `#`. Na Ciclo, igual ao vivo de antes fora das três linhas esperadas.
- **Passo 6 (medir o ±) não saiu:** a única edição medida, na Ciclo, caiu num erro do servidor da Google depois de 150 s.
- **18/11, Ciclo:** o menu Bot funcionou (67,4 s). A caixa AT4, clicada de verdade, exportou em três marcações:
  24,1 s, 26,0 s e **29,1 s**. A última passou a menos de 1 s do limite de 30 s. O bloco garantido de 6.500 linhas
  era lento demais na oficial. **Ajuste (18/11):** a caixa passou a blocos de 4.000 linhas e limite de 16 s; menu e
  montagem seguem com 6.500. Conta esperada na oficial: ~5 marcações de ~20–23 s.
- **O ajuste não resolveu (instalado nas duas oficiais em 18/11, medido na Ciclo):** as marcações deram 26,2 s
  (3.988/18.480), 16,3 s (**sem avanço**) e 26,5 s (7.988/18.480). Um bloco de 4.000 linhas custa quase o mesmo que
  um de 6.500, então o tempo é dominado por custo fixo (o recálculo no `flush`), não pelo número de linhas. E o tempo
  antes do primeiro bloco às vezes passa de 8 s (metade do limite), e aí a marcação não faz bloco nenhum. A exportação
  foi terminada pelo menu (70,7 s), e o CSV saiu igual ao anterior. Próximo passo: medir onde vão os segundos dentro
  do `onEdit` da caixa antes de mexer de novo.
- Continua sem rodar: a marca `desatualizada` numa oficial, a caixa no celular, o menu na Era, a paleta.

### Medição da caixa por dentro (18/11, cópia descartável do Ciclo)

Cópia "TESTE caixa da ANALISE (descartável) 18-11 · Ciclo", com marcações de tempo no `AnaliseEstatica.gs`. A caixa foi
clicada de verdade pelo painel do navegador. Tempos contados do começo do `onEdit` (o `t0`):

| Passo | Tempo |
|---|---|
| Fora do código (abertura do gatilho, desmarcar a caixa, aviso) | ~7 s |
| Primeiro toque na planilha (trava, propriedades, abas) | 1,4 a 4 s |
| Ler a `ANALISE_MODELOS` inteira (18.480 linhas) | ~5 a 7 s |
| Ler só as 4.000 linhas do bloco | 3,4 a 4,5 s |
| Primeiro `flush` (cálculo das fórmulas do bloco) | 4,5 a 6,6 s |
| Segundo `flush` (congelar) | 3,4 a 4,6 s |
| Fechamento (propriedades e texto) | 0,5 a 3,7 s |

**Mudança testada** (no `AnaliseEstatica.gs` do repositório, ainda não nas oficiais):
- a caixa lê só as linhas do bloco; o total e as fórmulas já exportadas ficam nas propriedades
  (`analise_modelos_total`, `analise_exportar_feitas`). Ficha instalada antes disso lê a lista inteira uma vez;
- a caixa só escreve o estado na ANALISE quando ele muda;
- cópia da ficha: a caixa vem junto e a propriedade não. O instalador agora reconhece a caixa (antes pagava ~3 s a
  cada marcação e o texto "exportando N/T" nunca aparecia).

Resultado: exportou tudo pela caixa e o CSV saiu idêntico ao de referência. Mas as marcações com bloco deram 21,4,
26,4, 24,5 e 30,3 s, e na reexportação 28,6, 30,2, 28,0, 29,0 e 25,7 s. Ganho de 3 a 4 s por marcação, engolido
pela variação do Google. **Não resolve.**

**Tirar o primeiro `flush` não funciona:** sem ele, o `copyTo` com `contentsOnly` grava vazio. As 18 mil chaves
saíram em branco (o teste escrevia `__velho__` antes da fórmula para provar que o valor era novo). A cópia foi
restaurada e reexportada, com CSV de novo igual à referência.

O bloco custa ~15 s quase sem depender do tamanho (leitura ~4 s, dois `flush` ~9 s). Somado aos ~7 s de fora e ao
primeiro toque, a marcação fica em 25–30 s.

**Meio bloco por marcação também não resolve** (testado na mesma cópia, ramo local
`claude/analise-caixa-metades-teste`, commit `d259b92`, fora da PR). Cada bloco foi dividido em calcular e congelar,
que podiam cair em marcações separadas. O CSV saiu igual à referência, mas:

| Marcação | Código | Execução inteira | O que fez |
|---|---|---|---|
| 10:02:53 | 8,7 s | 13,9 s | só congelar |
| 10:02:23 | 16,1 s | 21,9 s | só calcular |
| 10:03:24 | 18,3 s | 24,9 s | calcular e congelar |
| 10:05:35 | 16,5 s | 30,1 s | só calcular |

O tempo fora do código (abertura do gatilho, desmarcar a caixa, aviso) variou de 6 a 14 s, e a metade de calcular
sozinha (leitura ~3–5 s mais o flush ~4–6 s, mais o primeiro toque ~3 s) já chega no limite quando ele vem alto. O
que manda é a variação do Google, não o tamanho do trabalho.

O que protege a exportação mesmo assim: o progresso é gravado depois de cada `flush`. Uma marcação que estoura os 30 s
perde só o pedaço em andamento, e a caixa fica marcada; o toque seguinte desmarca sem exportar.

**Qualquer toque exporta (18/11, `450709a1a988` na cópia):** marcar ou desmarcar a caixa continua a exportação, para
o toque depois de um estouro não ser perdido. Apagar a célula não exporta. Os textos passaram a "toque de novo".
Na cópia:
- marcar (10:12:07) e desmarcar 8 s depois, com a primeira ainda rodando (10:12:15). O desmarcar entrou no exportador
  (13,2 s, achou a trava ocupada) e desmarcou a caixa. A primeira estourou (30,7 s), mas o bloco dela já estava
  gravado: o texto ficou em 0/18.480 e a marcação seguinte pulou para 7.988;
- depois, uma marcação por bloco: 32,3, 26,1, 23,0 e 31,1 s, todas concluídas (o corte não é exato nos 30 s);
- CSV igual à referência (`8d40252463892e70`).

### Nas oficiais, 18/11 depois da instalação

- Ciclo, caixa: 5 toques de 20,1, 18,7, 18,3, 19,9 e 20,7 s (antes 24 a 29 s), todos concluídos; CSV igual.
  Ler só o bloco e escrever o estado só quando muda tirou ~6 s de cada toque.
- Era, menu: 73,7 s, CSV igual ao de antes.
- Cópia de teste: editar o portador marcou `desatualizada` como devia, mas a edição levou 29,97 s (19,9 s dentro do
  código da ficha, pelo `R53_ONEDIT`) e a seguinte 29,55 s. Não é a ANALISE: na segunda o estado já era desatualizada
  e a marca só lê uma propriedade. É o que está mais perto do limite agora.

### Editar o portador da CARTEIRA perto dos 30 s (18/11, cópia de teste)

Medido com embrulhos temporários nas funções do onEdit, já tirados. Quatro edições do portador: 29,97, 29,55,
27,43 e **30,68 s (tempo limite)**, depois 22,6 e 22,9 s. Numa de 22,9 s, dentro do código (19,6 s):

- `analiseNaEdicao_` 1,7 s (primeiro toque na planilha, que alguém sempre paga);
- 4,3 s logo depois do `salarioEditar_`: o portador (CARTEIRA linhas 9–15, colunas O–AS) é a área `nome` do
  salário, que no modo fórmula (`SALARIO_.formula = true`) só trava e dá flush, e a chamada seguinte espera o recálculo;
- `r53Editar_` 4,9 s: nenhum cartão no portador, mas `r53SincronizarFamilias_` lê o Amparo
  (`DADOS_R53_CATALOGO!X10:AJ10`, 4,4 s) em toda edição da CARTEIRA. O Amparo é o estado da Família Amparo, escolhido
  na FICHA AMALDIÇOADA, na INVOCAÇÕES e na CONFIGURAÇÃO;
- carga do módulo 3,7 s e o `onEdit` do módulo 4,2 s.

Testados na cópia (só nela, não no git nem nas oficiais):

- **A:** no `r53Editar_`, sem cartão na área, não sincroniza o Amparo quando a edição é na CARTEIRA linhas 9–12;
- **B:** no `salarioEditar_`, `nome` só vale fora do modo fórmula.

Com os dois: 13,2, 12,4, 14,4 e 12,4 s (código 7,4 s; o `r53Editar_` caiu para 0,26 s e o buraco de 4,3 s sumiu).
O nome continuou gravado, chegou à FICHA PESSOAL e a ANALISE foi marcada `desatualizada`. Hashes na cópia:
EditorR53 `676337f165f7` → `addf731166ea`, Codigo do pacote `57a8398fa8c5` → `fc43e080e87c`.
