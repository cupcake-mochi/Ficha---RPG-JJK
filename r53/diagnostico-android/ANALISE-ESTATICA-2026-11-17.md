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
  "exportando N/T · marque de novo".
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
  montagem seguem com 6.500. Conta esperada na oficial: ~5 marcações de ~20–23 s. Ainda não instalado nas oficiais.
- Continua sem rodar: a marca `desatualizada` numa oficial, a caixa no celular, o menu na Era, a paleta.
