# Plano da rodada nas oficiais · 16/11/2026

**Só plano.** Nada foi aplicado nas oficiais, nas QAs ou em cópia nenhuma. Nenhum agente foi usado. Os links das duas
oficiais (Era da Revolução e Ciclo Maldito) estão em `r53/OFICIAIS.md`; aqui não vai ID de planilha nem de projeto.

Base lida: `codex/corrige-colagem-atributos-20261108` em `bf0ee8a` (merge do #121), depois de `git fetch`.

## Decidido pelo Mizuki em 16/11 ("Seguir recomendações")

- **D1:** a R67 (#117) fica para a rodada seguinte.
- **D2 + D3:** um preparador novo de molde, para as fórmulas de #91–#103 e as 225 da DADOS_CUSTOM sem INDIRECT.
  Ensaio numa QA antes das oficiais. Entra depois do #110 e antes do achatador.
- **D4:** as notas de FICHA!AH10 e AN10 com o texto novo, pela API.
- **D5:** forma B. A cadeia roda na Fase 0, sem Google. Na oficial vai o resultado conferido.

- **Ensaio (16/11, "Liberar o ensaio" e depois "Ensaio pelo Codex"):** o ensaio da seção 7 vai para o Codex, que
  instalou a cadeia nas QAs. O Claude não tem canal para levar ao Google arquivos desse tamanho: Codigo de 1,3 MB e
  mais de 10 MB de fórmulas na DADOS_R53. O conector e o console passam tudo pelas mensagens, e o navegador do app
  bloqueia o localhost.
  - O pacote fica fora do git, em `02-RPG/_trabalho/rodada-oficiais-20261116/`:
    - `fase0/`: os finais da cadeia;
    - `referencia/`: o trecho do molde e os hashes esperados.
  - O roteiro está em `_handoffs/PROMPT-codex-ensaio-rodada-oficiais-2026-11-16.md`.
  - O ensaio também gera o plano de planilha composto (antes = a oficial de hoje, depois = o fim), que vai para a
    oficial na forma B.

O ok para a rodada nas oficiais ainda não foi dado: vem depois do ensaio.

### Feito depois da decisão (16/11, sem Google)

- **D2 + D3 prontos:** `preparar_molde_api.js`, com o plano congelado `molde_api_plano.json` e o teste
  `r53/testes/molde_api.js` (no smoke).
  - São 593 fórmulas no molde: FICHA 54, FICHA PESSOAL 292, DADOS_CONFIG 22 e DADOS_CUSTOM 225.
  - Ficam de fora a DADOS_INVOC e a DADOS_AM, porque o onEdit não restaura essas abas, e os 8 valores de menu do
    #101, porque o restaurador só devolve fórmula.
  - Cada "antes" foi conferido igual ao modelo instalado nas QAs, e cada "depois" igual ao gerador atual.
  - Exige o Codigo `4f660022` e recusa se o ajuste já estiver lá.
  - No teste privado, com o Codigo real e o módulo: o modelo sai com as 593 novas, e continua assim depois do
    achatador.
  - Custo: +52 mil caracteres no Codigo e ~10–20 ms por carga do módulo no node. No Apps Script, medir no ensaio.
- **D4 pronto:** `notas_nivel_xp.json` com o antes e o depois das notas de FICHA!AH10 e AN10. O "antes" é o texto do
  main (#50); na rodada, a nota da oficial tem de estar igual a ele, senão para.
- **Fase 0, parte do código: fechada ("Terminar a Fase 0").** O `reproduzir_cadeia_oficiais.js` refaz, sem Google,
  a cadeia inteira: de `52302778` até `4f6600227cd1…` no Codigo, de `08badae1` até `676337f1` no EditorR53, e de
  `9dc3480a` até `bd42b535` no módulo.
  - São 42 passos, e cada preparador roda num worktree no commit do próprio PR. Todos os hashes da seção 3 bateram,
    sem exceção. O roteiro leva ~35 s.
  - Comparação byte a byte:
    - 35 dos 42 arquivos têm um igual, do mesmo hash, guardado em privado daquela época
      (`ficha-integracao-5156-20261104/nuvem-b47/saidas/`), que saiu das QAs. Entre eles estão o Codigo `b709ad14`
      (#90) e o EditorR53 `676337f1` (#75).
    - Os 5 da cauda (#105–#110) e as cinco partes do módulo saíram iguais aos de `02-RPG/_trabalho/rodada-oficiais-20261116/`.
    - O fim, `4f6600227cd1`, é o hash que as duas QAs registraram depois do #110
      (`CORRECAO-XP-LINHA-CONGELADA-2026-11-12.md`).
  - Os dois que faltavam em privado, o #61 (`5b81e86d`) e o #62 (`3767fb0f`), agora existem.
  - O `0292582a` do #105, que era inferido, está confirmado.
  - Por cima do resultado, o `molde_api.js` privado passou nas 25 verificações: o molde e o achatador sobre o Codigo
    e o módulo que a Fase 0 gerou.
  - O que a reprodução precisou (está no cabeçalho do roteiro):
    - o gzip com o byte de sistema 3, como no Linux e no navegador. No Windows, o Node grava 10 e o hash muda do #70
      em diante;
    - #60, #61 e #62 refazem a mesma troca a partir do `8a0f2ed6`, cada um com os arquivos do próprio commit;
    - no head do #65 e do #88, o `prepararCodigo` já faz as duas etapas. Os meio-termos `170273ca` e `8935211c`
      ficaram dentro do PR;
    - o #105 é um trecho de console. O roteiro faz a mesma troca no node, com as frases do commit do #105.
  - Os arquivos gerados ficam fora do git.

## Resumo

- As oficiais pararam em **03/11** (Codigo `52302778`, módulo `9dc3480a`, EditorR53 `08badae1`, SalarioLote
  `aaaa74f3`). Depois disso só entrou o aviso âmbar das caixas ± (16/11, só planilha). É exatamente o ponto de onde as
  QAs partiram, então a cadeia ensaiada nelas serve para as oficiais.
- Do **#51 ao #121** são 71 PRs. **42 mexem no que vai instalado** (código, planilha ou os dois); 15 são só auditoria
  ou documento; 2 já estão nas oficiais (#116 e #120). As QAs terminaram com Codigo `4f660022`, módulo `bd42b535` e
  EditorR53 `676337f1`.
- **Quatro pontos não fecham só com preparador** e precisam de decisão sua (seção 4): a R67 (#117), o restaurador
  que devolve fórmula antiga (#91–#103), o molde da DADOS_CUSTOM sem INDIRECT (#119) e dois textos que moram só no
  módulo (#107/#110).
- **Os preparadores não rodam na base de hoje.** Vários leem arquivos vivos do repositório (`apps-script/EditorR53.gs`,
  `r53/atalho_livre.gs`, os `*_runtime.js`), que mudaram depois. Cada um tem de rodar no commit do próprio PR
  (seção 5). Isso pede uma escolha sua entre repetir a cadeia na oficial ou instalar o resultado já conferido.

## 1. De onde as oficiais partem

Pelo `r53/OFICIAIS.md`, as duas estão iguais:

| Arquivo do projeto | Hash instalado | Desde |
|---|---|---|
| Codigo | `52302778…` | 27/10 (XP digitado na caixa) |
| EditorR53 | `08badae1…` | 03/11 (Amparo, PR48) |
| SalarioLote | `aaaa74f3…` | 03/11 (Amparo, PR48) |
| Analise (pedaço 2) | `2ea7e9d4…` | 27/10 |
| Ficha, Invocacoes (pedaços 0 e 1) | `6012dcb3…`, `ebf20bb1…` | 26/10 |
| Configuracao, Origens (pedaços vazios) | `bb784c6d…`, `90095228…` | 26/10 |
| LotePaleta, PaletaSegundoPlano | `848e878b…`, `a5a0e83d…` | 26/10 |
| módulo (descompactado) | `9dc3480a…` | 27/10 |

Backup nativo mais recente: **versão 15** nas duas (03/11). Planilha: talentos grátis (03/11) e aviso âmbar nas
caixas ± (16/11), as duas pela API.

**Conferência de que as QAs partiram daqui:**
- `preparar_pilha_5156.js` exige o Codigo `52302778` e o módulo `9dc3480a`;
- `pratica_cotidiana_plano.json` exige o EditorR53 `08badae1`;
- o plano da Prática copia o formato da linha 18.409 da ANALISE, que só existe depois dos talentos de 03/11.

O `r53/diagnostico-android/PROMPT-CONTINUAR-2026-11-12.md` diz "falta tudo de #63 em diante". Pelo `OFICIAIS.md`, falta
desde o **#51**: nada de 04/11 em diante foi registrado nas oficiais. O primeiro passo da rodada confirma isso lendo os
hashes.

## 2. O que entrou, PR a PR

Legenda: **código** = o que vai no Apps Script instalado; **planilha** = o que vai pela API do Sheets. "FA" é a FICHA
AMALDIÇOADA. Os números de célula saem dos planos e deltas versionados nesta pasta.

### 2.1 #51–#56: corpos da Restrição, Bloquear, cura, Origem custom, Morrendo e socorro

Vão juntos num preparador só, `preparar_pilha_5156.js` (#57).
- **Código:** Codigo `52302778` → `8a0f2ed6` (módulo `9dc3480a` conferido, sem mudar).
- **Planilha:** 11 valores e 3 notas (`pilha_5156_plano.json`):
  - FICHA: J26, D37, Z56, D59, O67;
  - DADOS_CUSTOM: CP3, CQ3, BE12, B126, B127;
  - DADOS: DW15;
  - FA: notas D73, J73, P73.
- A aba SOCORRO nasce sozinha no primeiro registro. O preparador não cria aba.

### 2.2 #57–#90: a pilha de correções com preparador

Cada linha é um passo. A base de cada preparador é o "depois" do anterior. Todo passo recusa se o hash não bater.
Os moldes de recuperação (o que o onEdit usa para devolver a fórmula) vão junto no código.

| PR | Assunto | Preparador | Codigo (EditorR53) | Planilha |
|---|---|---|---|---|
| #57 | preparação da pilha 51–56 | `preparar_pilha_5156.js` | ver 2.1 | ver 2.1 |
| #58, #59 | auditorias | — | — | — |
| #60 | ajuste ± e colagens | `preparar_recursos_fila.js` (atalho + runtime) | `8a0f2ed6` → `6aec0d0a` | — |
| #61 | máximo zero | o mesmo, no commit do #61 | → `5b81e86d` | — |
| #62 | TEMP em colagens e invocações | o mesmo, no commit do #62 | → `3767fb0f` | — |
| #63 | movimento e Integridade | `preparar_integridade_movimento.js` | → `9f64aa8c` | 40 fórmulas e 1 nota (FICHA D37/O67, DADOS_CONFIG F12/G12, INVOCAÇÕES, 36 em DADOS_INVOC) |
| #64 | equipamento | `preparar_equipamento.js` | → `a09bf672` | 55 células e 8 validações |
| #65 | bênçãos, imunidades e a revisão da imunidade custom | `preparar_bencaos_imunidades.js` (duas etapas) | → `170273ca` → `19ae4c19` | 6 + 2 alvos (FICHA 6, FA 1, DADOS_AM 1) |
| #66 | descanso das Origens | `preparar_descanso_origens.js` | → `d5845c03` | — |
| #67 | Origens e recursos | `preparar_origens_recursos.js` | → `bae62817` | 8 (FICHA 4, DADOS_CUSTOM 4) |
| #68 | auditoria | — | — | — |
| #69 | Reserva Excedente e Bolsa | `preparar_reserva_bolsa.js` | → `4b0d2cc1` | 6 (FICHA 2, DADOS 1, DADOS_CUSTOM 2, FICHA PESSOAL 1) |
| #70 | Prática Cotidiana | `preparar_pratica_cotidiana.js` (Codigo **e** EditorR53) | → `50f3aa55` (`08badae1` → `98413975`) | 922 células, 11 notas, linhas novas em 4 abas, mesclas, formatos e o mapa da R53_LOTE |
| #71 | conjuração e Integridade | `preparar_conjuracao_integridade.js` | → `6b22b689` (`165fc80d`) | 41 (FICHA 1, FA 40) |
| #72 | Classe 0 | `preparar_classe_zero.js` | → `e45999e3` (`13cf7ddf`) | 23 (DADOS_CUSTOM 1, FA 12, DADOS_R53 10) |
| #73 | alcance de cura | `preparar_alcance_cura.js` | → `5c8c7493` (`aa77309c`) | 36 na FA |
| #74 | Guarda, Impulso, Firmeza | `preparar_alcance_beneficios.js` | → `2005362b` (`2ed5d1e1`) | 36 na FA |
| #75 | Carregar, Armado, Guarda | `preparar_tempo_feiticos.js` | → `21a59ce6` (`676337f1`) | 108 (DADOS_R53 36, FA 72) |
| #76 | Rajada e Tudo ou Nada | `preparar_rajada_alvos.js` | → `6062ac46` | 1.004 fórmulas da DADOS_R53 (CK, CP, EH, FX) |
| #77 | Frágil e Fica | `preparar_fragil_fica.js` | → `cc5b05bf` | 753 (CK, CP, FX) |
| #78 | Sem Volta na Classe 0 | `preparar_sem_volta.js` | → `01e64224` | 753 (CK, CP, FX) |
| #79 | devoluções incompatíveis | `preparar_devolucoes_incompativeis.js` | → `30306ed0` | 502 (CK, CP) |
| #80 | restrições agrupadas | `preparar_restricoes_agrupadas.js` | → `9fc4f2eb` | 753 |
| #81 | Frágil instantâneo | `preparar_fragil_instantaneo.js` | → `e44e7f0c` | 753 |
| #82 | Frágil no catálogo | `preparar_fragil_catalogo.js` | → `ec0bbd15` | 753 (CK, CP, FX) |
| #83 | forma e função | `preparar_forma_funcao.js` | → `cf8dc596` | 251 |
| #84 | Corrói e Mira Livre | `preparar_corroi.js` | → `da89202e` | 251 |
| #85 | Liberações | `preparar_liberacoes.js` | → `7512bf62` | DADOS_R53!GA38:GA40 |
| #86 | Expansão da domada | `preparar_expansao_domada.js` | → `5b7bb420` | 48 (DADOS_INVOC 36, ANALISE 12) e 36 notas nas INVOCAÇÕES |
| #87 | repertório das Trilhas | `preparar_repertorio_trilha.js` | → `26b78470` | 102 (DADOS_INVOC 52, DADOS_R53 36, INVOCAÇÕES 14), 14 notas, 3 mesclas, 5 menus |
| #88 | especiais e erro por entidade | `preparar_contagem_especiais.js`, depois `preparar_isolamento_nomes.js` | → `8935211c` → `36ca73ef` | 24 fórmulas (DADOS_INVOC IE e JJ) |
| #89 | nível das entidades de Criação | `preparar_criacao_nivel_fixo.js` | → `ffd349c9` | 13 na DADOS_INVOC, 3 notas |
| #90 | nível obtido das invocações | `preparar_nivel_obtido.js` | → `b709ad14` | 36 valores, 2 notas, 12 validações |

De #76 a #82 o mesmo bloco da DADOS_R53 (CK, CP, FX: 251 linhas cada) é reescrito sete vezes, uma por PR. Cada
plano exige o "antes" exato, então ou vão os sete em ordem, ou um plano só com o antes de hoje e o depois do #82
(seção 5).

### 2.3 #91–#103: só planilha (sem preparador de código)

Nas QAs foram só pela API. **O Codigo e o módulo não mudaram** (ver o ponto D2 da seção 4).

| PR | Assunto | Planilha |
|---|---|---|
| #91 | perícias das entidades | 24 fórmulas (DADOS_INVOC GU2:GU13, HT2:HT13) e a nota INVOCAÇÕES!L42 |
| #92 | atributos colados como texto | 60 (DADOS_INVOC DJ2:DN13) |
| #93 | Buff/Debuff colado como texto | 168 (DADOS_INVOC DO2:DS13, DW2:EE13) |
| #94 | ponto fora de 0–6 | 12 (DADOS_INVOC HL2:HL13) |
| #95 | TR treinado | 12 (DADOS_INVOC HG2:HG13) |
| #96 | Buff/Debuff decimal | 206: FICHA 11, DADOS_AM 5, DADOS_INVOC 168, DADOS_CONFIG 22. Os 168 da DADOS_INVOC são os mesmos do #93: vem **depois** dele. |
| #97 | mapa | — |
| #98 | pontos na FICHA | FICHA Z15 e AK14 |
| #99 | auditoria | — |
| #100 | atributo vazio | 4 na FICHA |
| #101 | ofícios e TR Físico | 20 na FICHA. Recusa um menu que o jogador já trocou. |
| #102 | Especialização | 37 na FICHA |
| #103 | texto no Extra | 38 na FICHA |

Os deltas estão nos `*_delta.json` desta pasta. Nas QAs, #96 e #100–#103 foram por `findReplace` literal, uma célula
por pedido, conferindo a contagem de cada resposta. Lição do #96: o Sheets guarda `'FICHA'!$X$1` sem as aspas, e o
texto procurado tem de vir no formato do Sheets.

### 2.4 #104–#121: XP, frequência, CONFIGURAÇÃO, avisos, R67 e desempenho

| PR | Assunto | Código | Planilha |
|---|---|---|---|
| #104, #106 | auditorias | — | — |
| #105 | "uma vez por cena" | `instalar_frequencia_cena.js`: módulo `9dc3480a` → `bd42b535` e caminho leve `98fb3594` → `97972ea0`. O Codigo vai de `b709ad14` para `0292582a`: não está escrito em nenhum documento, mas é a única mudança entre o #90 e a base do #107. Conferir no ensaio. | — |
| #107 | um nível por missão | `preparar_trava_nivel_missao.js`: `0292582a` → `b5861c14` | — |
| #108 | corte de 25 XP | `preparar_corte_xp_missao.js` (292 moldes): → `c175d838` | `findReplace` com regex na FICHA PESSOAL!BA15:BS87 (292 de 292); DADOS!CR9:CS9 e CR15:CS15; 8 notas (AZ14, BA14, BF14, BG14, BL14, BM14, BR14, BS14) |
| #109 | XP congelado, nome | `preparar_xp_congelado_nome.js`: → `6ecbe593` | — |
| #110 | XP congelado, linha | `preparar_xp_linha_congelada.js`: → `4f660022` | — |
| #111, #112 | fechamento e auditoria | — | — |
| #113 | textos da CONFIGURAÇÃO | — | notas E45, E64, E99, F47:F57, F59, F100:F129 e o texto de C98. **Sem** o P26, que era só das QAs. |
| #114 | B/D decimal âmbar nas INVOCAÇÕES | — | 1 regra condicional (36 faixas, com os endereços do conserto do mesmo dia) e a nota de O21 |
| #115 | pontas do mapa | — | — |
| #116 | aviso âmbar nas caixas ± | — | **já nas oficiais** (16/11, #120) |
| #117 | Técnica Máxima R67 | **sem preparador** (ponto D1) | 40 `findReplace` com regex na DADOS_R53, cartões da FA e das 12 domadas, DADOS_AM!HM38 |
| #118 | Controle R68 | — | — (o texto não aparece na planilha) |
| #119 | módulo achatado e DADOS_CUSTOM sem INDIRECT | `preparar_modulo_achatado.js`, **por último** | 2 `findReplace` na DADOS_CUSTOM: 225 fórmulas / 4725 ocorrências, depois 225 / 525 |
| #120 | aviso âmbar nas oficiais | — | **já nas oficiais** |
| #121 | pente fino e teste no celular | — | — |

Detalhes do #114 na oficial:
- a INVOCAÇÕES da oficial tem **4 regras** (a âmbar do ± no índice 0 e as três antigas). A regra do B/D entra no
  índice 4, não no 3 como nas QAs;
- as faixas certas são as do conserto (linha da caixa ± + 8, + 13 e + 18; O:S e AH:AL), não as da primeira leva.

## 3. A cadeia, de ponta a ponta

```
Codigo     52302778 ─#51-56→ 8a0f2ed6 ─#60→ 6aec0d0a ─#61→ 5b81e86d ─#62→ 3767fb0f ─#63→ 9f64aa8c ─#64→ a09bf672
           ─#65→ 170273ca → 19ae4c19 ─#66→ d5845c03 ─#67→ bae62817 ─#69→ 4b0d2cc1 ─#70→ 50f3aa55 ─#71→ 6b22b689
           ─#72→ e45999e3 ─#73→ 5c8c7493 ─#74→ 2005362b ─#75→ 21a59ce6 ─#76→ 6062ac46 ─#77→ cc5b05bf ─#78→ 01e64224
           ─#79→ 30306ed0 ─#80→ 9fc4f2eb ─#81→ e44e7f0c ─#82→ ec0bbd15 ─#83→ cf8dc596 ─#84→ da89202e ─#85→ 7512bf62
           ─#86→ 5b7bb420 ─#87→ 26b78470 ─#88→ 8935211c → 36ca73ef ─#89→ ffd349c9 ─#90→ b709ad14
           ─#105→ 0292582a ─#107→ b5861c14 ─#108→ c175d838 ─#109→ 6ecbe593 ─#110→ 4f660022
           ─molde (D2+D3)→ (hash do trecho gerado) ─#119→ (achatado)
EditorR53  08badae1 ─#70→ 98413975 ─#71→ 165fc80d ─#72→ 13cf7ddf ─#73→ aa77309c ─#74→ 2ed5d1e1 ─#75→ 676337f1
módulo     9dc3480a ─#105→ bd42b535 ─#119→ (achatado, 3 partes em vez de 5)
SalarioLote, LotePaleta, PaletaSegundoPlano: sem mudança
```

Os #51–#56 entram pelo `preparar_pilha_5156.js` do #57. No #65 e no #88, o preparador do head vai direto ao segundo
hash (o primeiro é um meio-termo dentro do PR). Os hashes completos estão no `reproduzir_cadeia_oficiais.js` (`PASSOS`),
que refaz a cadeia toda sem Google (Fase 0, 16/11: os 42 passos bateram). A QA do Ciclo pulou alguns
passos de código em cópias descartáveis (#60–#62 e o #108/#109 por outra sessão), mas as duas QAs fecharam no mesmo
`4f660022`.

## 4. Onde o preparador não serve: decisões suas

Nada desta seção roda sem você. `construir()` e o pacote inteiro estão fora da rodada.

### D1. A R67 (#117) não tem caminho por preparador

- Nas QAs foi aplicada pela API, conferida e **desfeita**: nenhuma QA ficou com a R67.
- O `EditorR53.gs` muda junto, porque o editor da Classe reescreve a conta da MONTAGEM (R356). Mudaram os contextos
  44 (pessoal) e 204–248 (as domadas). Sem o EditorR53 novo, **trocar de Classe na oficial reescreve a R356 com a conta
  antiga**.
- O molde do módulo também guarda as fórmulas antigas da DADOS_R53 e dos cartões.

Opções:
1. **Deixar a R67 para a rodada seguinte** (recomendo). Esta rodada já é grande, e as QAs não têm a R67 para servir
   de ensaio.
2. Escrever um preparador novo: EditorR53 inteiro trocado com conferência de contexto (como o do #70) e um ajuste do
   molde. Depois, ensaio numa QA.
3. Pacote inteiro. Proibido sem você.

### D2. Fórmula trocada só pela API volta antiga se alguém escrever por cima (#91–#103)

- O onEdit devolve a conta pelo molde do módulo (`devolverConta_`). Isso vale para a FICHA, a FICHA PESSOAL, a
  INVOCAÇÕES, a CONFIGURAÇÃO e as DADOS_*.
- De #57 a #90, cada preparador levava o molde junto. **De #91 a #103 não**: o molde instalado ainda tem a fórmula
  de antes.
- Efeito: quem digitar por cima de uma dessas células e apagar recebe a fórmula **antiga**. As células visíveis são as
  da FICHA:
  - Z15 e AK14 (#98);
  - as 4 do #100, as 20 do #101, as 37 do #102 e as 38 do #103;
  - os 11 Buff/Debuff do #96.

  As outras ficam em abas ocultas: DADOS_INVOC, DADOS_AM e DADOS_CONFIG.
- As QAs estão assim hoje. Não foi testado: é leitura do código.

Opções:
1. **Preparador novo de molde** (recomendo): um `r53Ajustar*` no modelo do `pilha_5156_molde.gs`, que aceita só a
   fórmula antiga exata ou a nova, para todas as células de #91–#103. Ensaio numa QA (digitar por cima de Z15 e conferir
   que volta a nova) antes das oficiais. Entra antes do achatador.
2. Aceitar por esta rodada e acertar na próxima montagem.
3. Pacote inteiro. Proibido sem você.

### D3. O molde da DADOS_CUSTOM continua com INDIRECT (#119)

- O `findReplace` pela API troca as 225 fórmulas. O molde do pacote, porém, ainda tem INDIRECT.
- Quem editar DF2/DG2 (ou outra dessas células) recebe de volta a versão com INDIRECT. Foi isso que deixou a cópia
  DEPOIS com 523 de 525.
- A conta dá o mesmo resultado; só volta a ser volátil naquela célula.
- O `preparar_custom_sem_indirect.js` não remenda o módulo: ele reescreve os `.gs` e imprime os pedidos.
  O `Custom.gs` não existe no projeto instalado (saiu na limpeza de 26/10), e o `Origens.gs` instalado é só um pedaço
  vazio do módulo. Então "o molde vem junto com o Custom.gs e o Origens.gs novos" só acontece por remendo no módulo ou
  pelo pacote.

Opções:
1. **Juntar ao preparador de molde do D2** (recomendo), com as 225 fórmulas novas.
2. Aceitar. A DADOS_CUSTOM é oculta, e o jogador não edita ali.

### D4. Textos que moram só no módulo (#107, #110)

- O caminho de reserva `nivelPelaMissao_` e a ajuda da caixa do NÍVEL (#107), e a ajuda da caixa de XP (#110), ficaram
  "para a próxima montagem".
- O caminho de reserva não roda com o salário instalado: sem efeito.
- As ajudas são as notas de FICHA!AH10 e AN10. Nas oficiais essas notas existem (postas pela API em 27/10) e podem
  ganhar o texto novo pela API, como as do #108.

Pergunta: trocar as duas notas pela API nesta rodada?

### D5. Repetir a cadeia ou instalar o resultado (seção 5)

## 5. Como rodar a cadeia

**O problema.** Os preparadores leem arquivos vivos do repositório:
- `apps-script/EditorR53.gs`, nos passos #70–#75. Ele mudou em 14/11 com a R67;
- `r53/atalho_livre.gs`, no #60–#62;
- `apps-script/Descanso.gs` e `ReservaBolsa.gs`;
- os `r53/*_runtime.js`, que mudaram em #72, #75, #76, #80, #85 e #87.

Rodados na base de hoje, eles não reproduzem os hashes ensaiados. Os que conferem recusam (o #70 recusa porque os
contextos 44 e 204–248 mudaram). Cada passo tem de rodar **no commit do próprio PR**: `git worktree add` no topo de
cada ramo da pilha, ou no merge de cada PR do #93 em diante.

**Fase 0 (vale para as duas formas):**
- **feito em 16/11, sem Google:** rodar a cadeia inteira, passo a passo, cada um no seu commit, conferindo **todos**
  os hashes da seção 3:

  ```
  node r53/diagnostico-android/reproduzir_cadeia_oficiais.js <Codigo 52302778> <EditorR53 08badae1> <partes do módulo 9dc3480a> <pasta-nova>
  ```

  Saída, fora do git: os arquivos finais (Codigo `4f660022`, EditorR53 `676337f1`, módulo `bd42b535`) e um Codigo ou
  EditorR53 por passo. Comparados com os arquivos guardados das QAs, saíram iguais (ver "Feito depois da decisão").
- **falta, e precisa do Google (só leitura):**
  - ler o projeto inteiro de uma oficial e conferir a partida (seção 1);
  - ler o projeto da QA e conferir que os finais saem iguais ao que está lá hoje. Isso já foi conferido contra os
    arquivos e os hashes registrados, mas não contra uma leitura de hoje;
  - ler as células-alvo e compor o plano de planilha num só (antes = a oficial, depois = o fim da cadeia).

Depois, duas formas de levar à oficial:

| | A. Repetir a cadeia na oficial | B. Instalar o resultado conferido (recomendo) |
|---|---|---|
| Código | ~32 colagens no editor, cada uma conferindo o hash de antes e de depois | 3 trocas (Codigo, EditorR53, partes do módulo), conferindo o hash de partida (seção 1) e o de chegada (seção 3) |
| Planilha | ~35 lotes, cada um com o "antes" exato do passo anterior; o bloco CK/CP/FX da DADOS_R53 sete vezes | os mesmos alvos num plano só: antes = a oficial de hoje, depois = o fim da cadeia. A Fase 0 compõe e confere esse plano |
| Tempo estimado | várias horas por oficial | ~1 h por oficial |
| Risco | parar no meio deixa a oficial num estado que nenhuma QA teve; um jogador que copiar nessa hora leva esse estado | menos janelas abertas; o estado final é o mesmo da QA (fora a R67 e o achatador) |
| O que prova | cada passo na própria oficial | cada passo na Fase 0 e no ensaio; na oficial, o começo e o fim |

Você pediu "os preparadores conferindo o hash a cada passo". Na forma B isso acontece na Fase 0 e no ensaio, e na
oficial só se conferem a partida e a chegada. A escolha é sua.

## 6. Ordem da rodada

Para cada oficial, **com você no PC**, uma de cada vez, a Era primeiro:

1. **Leitura** (só leitura): os dez hashes da seção 1 e o módulo `9dc3480a`. Divergiu, para tudo.
2. **Backup nativo do projeto:** versão 16, "Antes da rodada de 16/11", implantação de biblioteca arquivada em
   seguida, como as anteriores. Se der, também uma cópia da planilha no Drive.
3. **Código**, conferindo o hash a cada passo. Forma A: os passos da seção 3, na ordem. Forma B: Codigo, EditorR53 e
   módulo do #105. Nos dois casos, o #105 vem depois do #90 e antes do #107. Depois do #110 entra o
   `preparar_molde_api.js` (D2 + D3), pelo trecho gerado uma vez e usado igual no ensaio e nas oficiais.
4. **Ctrl+S**, recarregar e reler os hashes: o Codigo com o hash que o trecho do molde imprime, EditorR53
   `676337f1`, módulo `bd42b535`.
5. **Planilha pela API** (o `batchUpdate` não dispara o onEdit), relendo os alvos antes de cada lote:
   1. #51–#90 (seção 2.2), na ordem;
   2. #91–#103 (seção 2.3). O #96 vai depois do #93;
   3. #108: o `findReplace` da FICHA PESSOAL!BA15:BS87 (tem de dizer 292), DADOS!CR9:CS9 e CR15:CS15, e as 8 notas;
   4. #113: as notas e o C98 da CONFIGURAÇÃO; D4: as notas de FICHA!AH10 e AN10 (`notas_nivel_xp.json`);
   5. #114: a regra no índice 4 da INVOCAÇÕES e a nota de O21;
   6. #119: os dois `findReplace` da DADOS_CUSTOM, **num `batchUpdate` só, só pela API**. As respostas têm de dizer
      225/4725 e 225/525. Outro número: desfazer pelo histórico de versões.

   **Nunca** usar localizar e substituir pela interface: ele dispara o onEdit, e o restaurador desfaz.
6. **Por último, `preparar_modulo_achatado.js`**, depois Ctrl+S. Ele recusa Codigo já achatado. Reler: 3 partes, e o
   texto que o `new Function` recebe igual ao de antes (o trecho confere).
7. **Conferência:** reler os hashes e uma amostra das células de cada PR; nenhum erro de fórmula nas abas.
   - Abrir a ficha **sem** editar nada de personagem;
   - nenhum `construir()`, `continuar()` ou acionador;
   - nenhuma função rodada no editor fora as colagens.
8. **Registro** no `r53/OFICIAIS.md` (seção 9), e só então a segunda oficial.

## 7. Ensaio antes, numa cópia

As QAs já têm #51–#110 e não têm a R67, o achatador nem a troca do INDIRECT. Por isso não servem para ensaiar a rodada
inteira. O ensaio é:
- uma **cópia fria de cada oficial** (cópia do Drive, que leva o projeto junto);
- a seção 6 inteira nela, igual;
- no fim, comparar com a QA: o projeto deve sair igual ao da QA mais o achatador, e as células-alvo iguais às da QA
  (fora os restos de teste dela);
- testar no Sheets, nas duas cópias:
  - um ± de vida;
  - um Buff decimal na FICHA e numa entidade;
  - uma missão no painel;
  - o XP total digitado;
  - escolher um cartão de Classe 0;
  - um menu de cartão custom (Arma e Origem);
  - se D2 entrar: digitar por cima de Z15 e conferir que volta a fórmula nova;
- medir algumas edições, como no teste do celular de 16/11.

Liberado por você em 16/11 e passado ao Codex (ver "Decidido pelo Mizuki em 16/11"). Hashes esperados no ensaio:
- Codigo `4f660022…` antes do molde e `b3ed2f7e7b80…` depois do trecho do molde;
- EditorR53 `676337f1…`;
- módulo `bd42b535…`;
- no achatador, o texto que o `new Function` recebe: `35d00ae28bfa…`, em 3 partes.

## 8. Riscos

- **Rodada parada no meio.** A oficial fica num estado que nenhuma QA teve. Para voltar:
  - o código, pela versão 16 do projeto;
  - a planilha, pelos pedidos inversos de cada plano. Os preparadores geram a reversão; ela só vale se o alvo ainda
    estiver com o valor proposto.

  Ou pelo histórico de versões da planilha, que leva junto qualquer coisa feita depois.
- **Jogador copiando a oficial durante a rodada** leva o estado do meio. Fazer num horário calmo.
- **O Codigo do #105** (`0292582a`) era inferido. A Fase 0 confirmou o hash.
- **O caminho leve** precisa ser `98fb3594` para o instalador do #105. Nada na cadeia mexe nele, mas não está escrito
  em documento que a oficial tem esse hash. O instalador confere e recusa.
- **Autorizações.** Nas QAs, depois do #90, você autorizou o Google para rodar o `verificarPacoteR53`. Nas oficiais
  nenhuma função é rodada no editor, então não deve aparecer pedido. Se aparecer, paro e pergunto.
- **A FX da DADOS_R53** só aceita lotes de ~40 linhas; lote maior dá "service unavailable" (visto no #117).
- **O `PraticaCotidiana.gs`**, ao repor as linhas 252–253, escreve a fórmula de antes da R67. Não muda número: ali a
  Máxima é sempre falsa.
- **Fichas já copiadas por jogadores** não recebem nada disto.
- **Um `construir()` com o `Codigo.gs` instalado** remonta as abas sem as mudanças só de planilha (#91–#103, #108,
  #113, #114, #116 e o INDIRECT). Isso já vale para o aviso âmbar de 16/11.

## 9. O registro no `r53/OFICIAIS.md`

Uma seção nova no topo, no formato das anteriores:
- a frase de autorização sua, entre aspas;
- versão de backup e horário de cada projeto;
- tabela antes/depois dos arquivos do projeto;
- a lista do que foi pela API, por PR, com as contagens das respostas;
- o que ficou de fora (D1 a D4, conforme sua decisão);
- como voltar.

Sem ID completo no git.

## 10. O que não rodou

- Nada no Google: nem leitura das oficiais, nem cópia, nem QA. Os hashes da seção 1 são os do `OFICIAIS.md` de 03/11,
  não uma leitura de hoje.
- Da Fase 0, a parte do código está fechada e bate (#57–#110, 42 passos). Ainda faltam, e todas pedem Google:
  - a leitura de hoje da oficial e da QA;
  - o plano de planilha composto.
- O plano de planilha de cada passo (#51–#103) não foi recomposto na Fase 0. Os pedidos continuam nos preparadores e
  nos planos de cada PR.
- O `preparar_molde_api.js` não rodou no Google: nem em QA, nem em cópia, nem no editor. O custo no Apps Script não
  foi medido.
- Nenhum número de regra muda: o molde só repete no modelo as fórmulas que já foram pela API.
