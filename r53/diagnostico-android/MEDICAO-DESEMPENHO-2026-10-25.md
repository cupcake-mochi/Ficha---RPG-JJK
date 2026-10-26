# Medição de desempenho no Google · 25/10/2026 (Claude)

Cópia descartável da Ciclo Maldito oficial, criada pelo Drive:
`1ZJLQzIDCv5BaD_QvNo_jne_B2YSEDTbYFDj1tCaWfGs` ("TESTE desempenho — pode apagar"),
projeto `1Ane40rqYgeEB-brWEfkzqN2kpT7g7Dnr8VnEIcGDbaT4pCM50z4RdHv3`. As oficiais
não foram tocadas. O código instalado na cópia é o das oficiais **antes** da
correção da corrida (`d92f846e…`). As funções de medição estão em
`medir_carga.gs`, coladas no arquivo vazio `AnaliseFontes.gs` da cópia.

## Edições pelo acionador simples (registro de Execuções)

| Edição | Duração | Status |
|---|---:|---|
| Caminho Emanador (personagem novo, caminho leve) | 19,1 s | concluído |
| Trilha Ressonante (caminho leve) | 15,8 s | concluído |
| XP 3000 (caminho geral, abre o módulo) | 30,8 s | **tempo limite** |
| ± da vida −3 (caminho geral, abre o módulo) | 30,6 s | **tempo limite** |
| Clique (`onSelectionChange`) | 1,7–2,4 s | concluído |
| Abrir a planilha (`onOpen`) | 22,2 s | concluído |

## As mesmas edições pelo editor (sem o corte de 30 s)

`medirEdicoes` grava a célula e chama o `onEdit`. A 1ª edição abre o módulo; a
2ª já o encontra aberto (cada gatilho real é uma execução nova e sempre o abre).

| Rodada | XP 1ª | XP 2ª | vida 1ª | vida 2ª |
|---|---:|---:|---:|---:|
| com ANALISE (1) | 33,2 s | 30,5 s | 17,3 s | 17,0 s |
| com ANALISE (2) | 40,8 s | 27,2 s | 17,6 s | 18,9 s |
| sem ANALISE | 36,8 s | 29,6 s | 16,7 s | 15,6 s |

## Abrir o módulo (`medirModulo`, uma execução)

| Etapa | Inteiro (21,4 MB) | Sem a montagem (8,3 MB, 31 tabelas) |
|---|---:|---:|
| descompactar | 3.331 ms | não medido (proporcional: ~1,3 s) |
| hash | 423 ms | não medido (~0,2 s) |
| correções de texto (`r53Correcao*`) | 4.472 ms | não medido (~1,7 s) |
| compilar | 618 ms | 242 ms |
| rodar escopo global | 1.546 ms | 194 ms |

## Operações básicas (`medirLeituras`)

| Operação | com ANALISE (2 amostras) | sem ANALISE |
|---|---:|---:|
| primeira leitura de uma célula | 3,1 / 2,4 s | 1,7 s |
| leitura seguinte, nada pendente | 2 ms | 2 ms |
| ler a DADOS inteira | 7,0 / 7,5 s | 7,0 s |
| ler a FICHA inteira | 6,6 / 7,6 s | 6,8 s |
| gravar célula solta e ler | 4,8 / 5,3 s | 4,7 s |
| gravar XP e ler | 4,5 / 5,2 s | 3,3 s |
| gravar Caminho e ler (ida/volta) | 5,6 · 4,8 / 4,9 · 5,1 s | 4,0 · 5,5 s |
| apagar e `flush` | 2,5 / 2,4 s | 2,5 s |

## Leitura dos números

- Gravar e depois ler custa ~5 s mesmo numa célula que nada usa: o custo é da
  planilha inteira, não das fórmulas que dependem da célula.
- Ler a DADOS ou a FICHA inteiras custa ~7 s cada. O caminho geral do XP lê a
  DADOS duas vezes (`onEdit` e `nivelPelaXP_`).
- Tirar a ANALISE muda pouco (de 0 a ~1,5 s, dentro da variação entre rodadas).
- Abrir o módulo custa ~10 s e é pago em toda edição que não seja Caminho,
  Trilha ou treino; as correções de texto aplicadas por cima do pacote são a
  maior fatia (4,5 s).

## Depois: opção 1 e pacote leve (segunda cópia)

Cópia nova da oficial, com a ANALISE: `1kQuSggqnX1C6hu07HlTRXd_UYyyBGLJdHDgdM4Oyovg`
("TESTE pacote leve — pode apagar"), projeto
`1Sl3XTWIfZTb8o1EVfnhy46TJ0dFCXDqgPWmlMbFSrMDCPkB6-6vdd3iY`. Medido antes e depois
de rodar `instalar_pacote_leve.js` no editor dela. O módulo gerado no navegador
tem o mesmo SHA-256 do testado no node:
`2667ef41d84e44f565228bae47d7a6b9cf08bb7bfef8c60f2467383075aaee53`.

| Medida | Antes | Depois |
|---|---:|---:|
| Pacote de dados (base64) | 3,6 MB em 5 arquivos | 1,9 MB em 3 arquivos |
| Módulo descompactado | 21,4 MB | 8,3 MB |
| Abrir o módulo (`medirAbrirModulo`) | 11,4 s | 1,8 s |
| XP pelo editor, 1ª / 2ª | 29,9 / 27,2 s | 22,2 / 17,9 s |
| ± da vida pelo editor, 1ª / 2ª | 17,2 / 17,6 s | 9,3 / 9,0 s |

Pelo acionador simples, na planilha, depois do pacote leve (todas concluídas e
conferidas na tela):

| Edição | Duração | Resultado |
|---|---:|---|
| Caminho Emanador | 10,2 s | concluído |
| Trilha Ressonante | 10,5 s | concluído |
| Vida atual = 20 (edição comum) | 10,6 s | concluído |
| ± da vida −3 | 11,5 s | vida 20 → 17, caixa limpa |
| Vida temporária 100 | 12,0 s | cortada para 25 (metade da máxima 50) |
| Abrir a planilha (`onOpen`) | 2,1 s | concluído (era 17,9 s) |
| Clique (`onSelectionChange`) | 1,6–3,2 s | concluído |

O XP pelo editor continua alto porque a caixa de XP é uma conta: escrever nela
devolve a fórmula (gravar e reler, ~5 s) antes de subir o nível. O jogador sobe
XP pelas missões da FICHA PESSOAL, que já têm caminho próprio.

## As quatro opções

1. **Ler uma vez e gravar no fim, nas edições comuns** — feita no `Codigo.gs`: o
   índice sai do molde (`indiceEstatico_`, igual ao do caminho leve nas 89 chaves),
   a DADOS só é lida quando a edição precisa (Caminho e XP) e por faixa fixa
   (`faixaDoMolde_`), e ±, temporária e descanso leem numa ida só (`lerCelulas_`).
   No contador do node: ± da vida 8 → 1 leitura, temporária 6 → 1, XP 11 → 4,
   célula comum 4 → 0.
2. **Escopo global preguiçoso** — não precisou de mudança à parte: sem as tabelas
   da montagem, rodar o escopo global caiu de 1,5 s para 0,2 s (medido).
3. **Pacote leve** — feita. Sai o que só serve para montar (DADOS_R53, MONTAGENS,
   catálogo e as tabelas da ANALISE) e os remendos `r53Correcao*` passam a vir
   embutidos. `construir`, `continuar` e `acabar` recusam com aviso: a montagem
   precisa do pacote completo, que continua no repositório.
4. **Aliviar a ANALISE** — não aplicada na planilha. Apagar a aba inteira mudou de
   0 a 1,5 s (dentro da variação) e ela é o contrato do bot. O molde dela já saiu
   do módulo de edição na opção 3; só deixa de existir a volta automática da
   fórmula quando alguém escreve na ANALISE oculta.

## O que ainda falha, com o pacote leve (mesma cópia)

| Edição pelo acionador simples | Duração | Status |
|---|---:|---|
| CARTEIRA, célula qualquer (A1) e o desfazer | 30,7 s e 30,6 s | tempo limite |
| FICHA AMALDIÇOADA, célula livre (B500) | 30,6 s | tempo limite |
| FICHA PESSOAL, arma na mão principal (D64) | 30,6 s | tempo limite |
| CARTEIRA, troca de paleta | 14,9 s (cor visível em ~10 s) | concluído |

- **Sincronização das Famílias em cópia nova.** `r53SincronizarFamilias_` compara o
  amparo atual com `r53_amparo_direto` das propriedades do documento, que não vão
  na cópia da planilha. Sem estado anterior, toda edição em CARTEIRA, FICHA
  AMALDIÇOADA, INVOCAÇÕES e CONFIGURAÇÃO tenta acertar os 249 cartões (81 idas no
  contador do node), estoura e não grava o estado: repete em toda edição.
- **FICHA PESSOAL.** `textoDaCapacidade_` e `pessoalEditada_` releem o índice
  pessoal da DADOS em toda edição da aba, e o caminho das notas faz `flush`, lê a
  DADOS inteira pelo `getDataRange` e reescreve as notas vivas (12 idas no node).
- **Força e atributos.** `fichaMexeNaPessoal_` lê a DADOS inteira e refaz as notas
  vivas (8 idas).

## Consertos 1–3, no node

Contador de idas (Sheets de mentira, onEdit de verdade), antes → depois:

| Edição | Leituras antes | Leituras depois |
|---|---:|---:|
| CARTEIRA / FICHA AMALDIÇOADA / INVOCAÇÕES / CONFIGURAÇÃO, cópia sem estado | varredura dos 249 cartões | 1 |
| FICHA PESSOAL, arma na mão (D64) | 12 | 2 |
| FICHA PESSOAL, item da mochila (D104) | 12 | 2 |
| FICHA PESSOAL, capacidade marcante da Origem | 13 | 6 |
| FICHA PESSOAL, texto da capacidade | 7 | 3 |
| FICHA, Força (atributo base) | 8 | 2 |

As notas gravadas são as mesmas de antes (`r53/testes/pessoal_leve.js`). Módulo leve
com os remendos novos: `9d1cec81cf90bac42dd044d619843857b9c5fff3538ea0b8a0909899ff62fdce`
(a partir do `2667ef41…` instalado na cópia). `EditorR53.gs` de transporte novo:
`d2e572232a58643addb44847710cd0b4568ba5b8f8c95e8ac9d894e777ab48ef`.

## Consertos 1–3 no Google · 26/10/2026 (cópia nova)

Cópia nova da Ciclo Maldito oficial feita pelo Drive na gustavohmoura12:
`1xcXsFSkK8AffAe-mJ5pWFPztvYgy7hlFpZ_v8TK4NR0` ("TESTE consertos 1-3 — pode apagar —
25-10-2026"), projeto `1_K6fs0OnMnPuFBZlVLCxr6AwhQUepMw76eurRZh_w24nuTdUY7RICTcU`. As
oficiais não foram tocadas. Instalado de fábrica: `Codigo.gs` `d92f846e…`, `EditorR53`
`bc300464…`, módulo completo `2f153f65…` com a cadeia de correções. É o caso "cópia nova"
do conserto 1 (sem `r53_amparo_direto`) e o mesmo caminho de instalação das oficiais.

Instalação pelo console do editor: o bloco novo do `r53SincronizarFamilias_`
(`bc300464…` → `d2e57223…`) e o pacote leve do zero com os 22 remendos
(`instalar_pacote_leve.js`, remendos baixados do commit `9231191` e conferidos pelo
SHA-256 `f69a2e0c…`): 21,4 → 8,3 MB, 31 tabelas cortadas, 3 travas, módulo `9d1cec81…`,
o mesmo hash calculado no node a partir do `2667ef41…`. Projeto salvo e editor recarregado:
`EditorR53` `d2e57223…`, módulo declarado e real `9d1cec81…`.

Pelo acionador simples (registro de Execuções), edições feitas à mão na planilha:

| Edição | Antes | Depois |
|---|---:|---:|
| CARTEIRA A1 = x | 30,707 s, tempo limite | — |
| CARTEIRA A1 apagada (1ª depois, grava o estado das Famílias) | — | 10,577 s, concluído |
| CARTEIRA A1 = x (2ª) | — | 12,390 s, concluído |
| CARTEIRA A1 apagada (3ª) | — | 10,869 s, concluído |
| FICHA AMALDIÇOADA B452 = x / apagada | 30,783 s, tempo limite | 12,763 s, concluído |
| FICHA PESSOAL D66 apagada (linha da mão; a conta voltou) | 30,766 s, tempo limite | — |
| FICHA PESSOAL D64 apagada (arma na mão) | 30,975 s, tempo limite | 11,331 s, concluído |
| FICHA PESSOAL D64 = Soco | 31,002 s, tempo limite | 10,191 s, concluído |
| FICHA D21 Força 0 → 1 / 1 → 10 | 30,692 s, tempo limite | 12,644 s, concluído |
| FICHA D21 Força 10 → vazio | — | 10,639 s, concluído |
| FICHA D21 Força vazio → 0 | — | 11,692 s, concluído |

Conferido na tela: a nota embaixo da mão voltou ao texto do Soco ("O dado desarmado é d4 com
maestria 1…"); a conta da D66 apagada voltou. Células devolvidas ao original (A1 e B452
vazias, D64 Soco, D21 0). Reescolher o mesmo valor no menu não dispara o gatilho, por isso a
arma foi medida apagando e voltando. A B500 da FICHA AMALDIÇOADA está num grupo recolhido;
usei a B452, também fora dos cartões. O "antes" desta cópia é sem o pacote leve (o que os
jogadores têm hoje); o "depois" soma pacote leve e consertos 1–3.

## Missões e cartão nas oficiais de 26/10 (cópia nova, pelo navegador)

Cópia da Ciclo Maldito oficial feita em 26/10 às 09:19, com o pacote leve `fef2a94b`
instalado: `1HI96ICu-kf_tzvEm-mKWswQqY1yuqQLc5OHxHf5Fg1A` ("TESTE missões e cartão —
pode apagar"), projeto `1VZL7GoZHax9lW4LGh0QPfO7QZ203-147J0eGtyAYwXSIedC_fBaSnRFm`.
Edições feitas à mão na planilha; duração do registro de Execuções. Tudo voltou ao
valor de antes no fim.

| Edição pelo acionador simples | Logo depois de copiar | Planilha já aquecida |
|---|---:|---:|
| FICHA PESSOAL, nome de missão (AW15 / AW16) | 30,6 e 30,6 s, tempo limite | — |
| FICHA PESSOAL, tipo da missão (AX15 Curta / AX16 Padrão) | 30,4 e 30,6 s, tempo limite | — |
| FICHA PESSOAL, troca do tipo (AX16 Longa) | — | 30,6 s, tempo limite |
| FICHA PESSOAL, apagar as duas missões | — | 30,5 s, tempo limite |
| FICHA AMALDIÇOADA, pontos do cartão (E71 = 1 / volta a 0) | 30,4 e 30,6 s, tempo limite | 23,2 / 25,6 / 23,4 / 26,0 s, concluído |
| FICHA, célula vazia (AX460, atalho) | 14,0 s | 7,4 s |
| onOpen | 20,8 s | — |

- **Cópia recém-criada aquece:** nos primeiros minutos tudo custa mais (célula vazia
  14,0 → 7,4 s depois de ~4 min parada). O cartão só conclui depois de aquecer.
- **Missões estouram sempre:** mesmo aquecida, toda edição no painel de missões
  (rows 15–87, AW:BT) passa dos 30 s. O XP total aparece porque é fórmula, mas o registro
  da missão, a nota com a data e a subida de nível não terminam.

Perfil pelo gatilho (`medir_perfil.gs` como último arquivo da cópia: cada função global
de salário/cartão que passa de 0,3 s escreve no registro quando termina; não pede
autorização, ao contrário de rodar pelo editor numa cópia nova):

Missão (nome em AW15), tempo desde o carregamento:

| Rotina | Duração | Termina em |
|---|---:|---:|
| `r53SalarioAreaPropria_` (primeira chamada ao Sheets) | 1,2 s | 1,2 s |
| `salarioEstado_` (DADOS_SALARIOS!L2, espera o recálculo) | 3,3 s | 4,8 s |
| `salarioSincronizar_` (getLastRow, registros A:G, painel 73×24 em notas e valores) | 9,8 s | 14,7 s |
| ↳ `salarioMissoesAtuais_` (notas + valores do painel) | 3,1 s | 14,7 s |
| `salarioMissaoDireta_` (DADOS!AQ4:DP100, XP total, nível da FICHA) | 10,4 s | 25,1 s |
| gravação dos registros, das notas e flush | — | corta aos 30,6 s |

Cartão (E71 = 1, 23,4 s, concluído):

| Rotina | Duração | Termina em |
|---|---:|---:|
| `r53SalarioAreaPropria_` | 1,6 s | 1,6 s |
| trava, releitura das entradas diretas | ~3,8 s | ~5,4 s |
| `r53ValoresCartao_` (área do cartão, espera o recálculo) | 4,3 s | 9,7 s |
| `r53LerVersao_` (versão salva na MONTAGENS) | 3,9 s | 13,8 s |
| `r53Amparo_` via `r53Porta_` (DADOS_R53_CATALOGO!X10:AJ10) | 3,2 s | 17,0 s |
| gravação e flush | ~4,1 s | 21,1 s |

Nesta cópia cada ida ao servidor custa ~1,2–1,6 s mesmo sem recálculo pendente, e as
leituras de outra aba custam 3–4 s. A missão faz umas dez idas em sequência; o cartão,
umas oito.

## Missões enxutas na mesma cópia (26/10, 10:46–10:55)

Corte do `preparar_missoes_enxutas.js` instalado só no Codigo da cópia `1HI96ICu…` (versão 1 do projeto é a de
antes). Edições pelo navegador, uma por vez, cada uma esperando a anterior concluir. No fim, AW15:AX20 vazio e
XP total 0 de novo.

| Edição | Duração | onEdit | Status |
|---|---:|---:|---|
| AW15 nome | 21,7 s | 19,5 s | Concluído |
| AX15 Curta | 27,7 s | 24,3 s | Concluído |
| AX15 Longa | 22,8 s | 21,2 s | Concluído |
| AW20 nome | 17,5 s | 16,1 s | Concluído |
| AX20 Padrão | 21,4 s | 19,6 s | Concluído |
| apagar AW15:AX15 | 25,3 s | 22,3 s | Concluído |
| apagar AW20:AX20 | 27,0 s | 25,1 s | Concluído |

Antes, todas cortavam aos 30,6 s. Perfil típico: `r53SalarioAreaPropria_` 2,3–3,7 s; `salarioSincronizar_` 7,6–11,4 s
(dos quais `salarioMissoesAtuais_`, notas e valores do painel, 4,1–6,2 s); `salarioMissaoDireta_` 4,1–5,9 s
(era 10,4 s); gravação e flush 4–5 s. A folga no pior caso é de ~2 s: o que sobra de peso é a leitura
dos registros (DADOS_SALARIOS, outra aba) e as duas leituras do painel.

## Segundo corte na mesma cópia (26/10, 11:06–11:27)

Com a DADOS lida só quando o nível pode subir. 14 onEdits, todos concluídos:

| Edição | Duração | onEdit |
|---|---:|---:|
| AW15 nome / AX15 Curta / AX15 Longa | 22,2 / 24,9 / 21,3 s | 20,4 / 22,7 / 18,8 s |
| AW20 nome / AX20 Padrão | 16,4 / 20,3 s | 14,3 / 18,2 s |
| apagar AW15:AX15 / AW20:AX20 | 21,3 / 22,8 s | 19,2 / 20,5 s |
| AW25 nome / AX25 Final de arco (XP 300) | 16,6 / 22,8 s | 14,7 / 20,5 s |
| AW26 nome / AX26 Final de arco (XP 600, **nível 3 → 4**) | 19,5 / 21,4 s | 17,9 / 19,0 s |
| apagar AW25:AX25 / AW26:AX26 | 24,9 / 24,6 s | 21,5 / 22,1 s |

`salarioMissaoDireta_` só passou de 0,3 s na subida de nível (3,3 s) e numa execução em que o serviço
Planilhas falhou ao acessar o documento durante o registro ("Salários: O serviço Planilhas apresentou falha…",
apanhado pelo try do salário; a edição concluiu, mas o registro daquela missão ficou TRUE até a próxima edição
de missão varrer o painel). Pior caso 24,9 s (antes deste corte, 27,7 s). O que sobra: primeira ida ao Sheets
1,5–7 s, registros + notas + valores do painel 8–12 s, gravação e flush 4–6 s.

## Quanto custa cada leitura do caminho das missões (26/10, 11:34–11:38, `medir_leituras_missao.gs`)

Pelo editor, na cópia `1HI96ICu…`: grava uma missão em AW15:AX15, faz flush, lê numa ordem e apaga. Em ms:

| Ordem | 1ª | 2ª | 3ª | 4ª |
|---|---|---|---|---|
| registros, notas, painel11 | registros 8770 | notas 3140 | painel11 3633 | |
| literais, notas, registros, cabeçalho | literais 4534 | notas 7 | registros 8644 | cabeçalho 4569 |
| notas, literais, registros, cabeçalho | notas 3579 | literais 5 | registros 7713 | cabeçalho 4610 |
| painel15, notas, registros, cabeçalho | painel15 3545 | notas 17 | registros 5380 | cabeçalho 2816 |
| cabeçalho, literais, notas, registros | cabeçalho 3285 | literais 9 | notas 15 | registros 6758 |
| registros, notas, painel11 | registros 11121 | notas 2598 | painel11 2763 | |
| literais, notas, registros, cabeçalho | literais 3775 | notas 10 | registros 8017 | cabeçalho 3217 |

- A primeira leitura da FICHA PESSOAL custa 3,3–4,5 s; as seguintes da mesma aba saem quase de graça (5–17 ms).
  A exceção é ler fórmula (painel11 ou cabeçalho) depois de outra aba: paga de novo, 2,8–4,6 s.
- **Os registros (DADOS_SALARIOS!A2:G) custam 5,4–11,1 s em qualquer posição.** É a leitura mais cara do caminho.
- Ordem mais barata: painel e notas da FICHA PESSOAL primeiro (uma espera só) e o cabeçalho junto deles, nunca
  depois dos registros.

## Terceiro corte na cópia (26/10, 11:43–11:56, painel antes dos registros, valores antes das notas)

Mesmas edições da rodada anterior, uma por vez pelo navegador, na cópia `1HI96ICu…` (nível 3, XP 0 no início).

| Edição | Duração | R53_ONEDIT |
|---|---|---|
| AW15 nome / AX15 Curta | 18,3 / 16,7 s | 16,2 / 14,1 s |
| AX15 Longa | 11,3 s | 9,8 s |
| AW20 nome / AX20 Padrão | 16,4 / 15,4 s | — / 13,5 s |
| apagar AW15:AX15 / AW20:AX20 | 18,9 / 14,8 s | 15,7 / 12,3 s |
| AW25 nome / AX25 Final de arco | 11,6 / 15,8 s | 9,3 / 13,4 s |
| AW26 nome / AX26 Final de arco (**nível 3 → 4**) | 12,3 / 16,4 s | 10,0 / 14,5 s |
| apagar AW25:AX26 | 12,9 s | 11,2 s |
| AH11 = 3 (restauração, outro caminho) | 14,2 s | 11,8 s |

Todas concluídas. **Pior caso 18,9 s** (antes deste corte, 24,9 s; antes dos cortes, 30 s com timeout). Média das
missões ≈ 15 s. Alguns logs vieram sem linhas (PERFIL/R53_ONEDIT), mas as execuções terminaram. Ao apagar as
missões o nível ficou em 4, como no código de antes (o nível não desce); a cópia foi devolvida ao estado inicial.
