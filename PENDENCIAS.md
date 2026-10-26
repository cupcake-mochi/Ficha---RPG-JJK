## Inventário da FICHA PESSOAL: menus destravados · 26/10/2026 (Claude) · aplicado nas duas oficiais

O Mizuki viu que os itens guardados e os equipáveis guardados não aceitavam escrita. Nas duas oficiais (e na
cópia de teste) os menus `D92:D99` (DADOS_CUSTOM!AA), `D104:D109` e `Z104:Z109` (DADOS_CUSTOM!AU) estavam
**estritos**, embora o molde (`apps-script/Ficha.gs`, gerado por `ficha-v01/`) só ponha `D44` em
`menus_estritos`; não achei quando travaram. Pedido dele: itens guardados só de escrever, e duas vagas livres nos
equipáveis (o desenho original: "seis linhas com menu, duas livres"). Feito pela API do Sheets: `D98:D99`,
`D104:D109` e `Z104:Z109` sem validação; `D92:D97` seguem com o menu. **Gerador em dia (26/10):** quem
alargava o menu era o `integra()` do `ficha-v01/custom.py`; agora ele põe o catálogo só em `D92:D97`
(`EQUIP_MENU`, o desenho do `ficha_pessoal.py`) e não põe menu nos itens guardados. As contas que puxam o
catálogo ficam, então um nome do catálogo escrito à mão ainda preenche. Regerado: no molde só mudou o `dv`
da FICHA PESSOAL; o selo da geração passou a `2d3a0bf73db57661` (as oficiais seguem no módulo instalado).

## Experiência da cópia de teste · 26/10/2026 · bordas pelo tema e listas sem INDIRECT

`r53/diagnostico-android/experimento_bordas_listas.gs` (só na cópia `1xcXsFSk…`, com o medidor `MedidaTeste`
que grava cada onEdit na aba oculta `R53_MEDIDA`). `experimentoBordas()` passa as bordas das seis abas para a vaga
ACCENT5 do tema e a troca de paleta escreve a régua em ACCENT5 e ACCENT6; `experimentoListas()` troca as 225
`INDIRECT(SWITCH(...))` da DADOS_CUSTOM por `CHOOSE(MATCH(...))` e confere em todos os estados dos seletores.
Medida 1 (sem as mudanças, tempo do script): FICHA 8,4 e 10,9 s; paleta 15,5 e 22,8 s.

## Cartas antes das caixas que esticam · 26/10/2026 (Claude) · no ramo, fora das oficiais

Pente fino depois da instalação: no arnês quase toda edição já fica entre ~7 e ~9 s. Na CONFIGURAÇÃO, o
texto das habilidades custom esticava as caixas (27 alturas gravadas) e só depois lia as cartas, que
então esperavam o recálculo (~16 s). A ordem inverteu (remendo 33; módulo `bddccf83…`, mapa do atalho
regerado, igual fora o hash): as duas leem antes de gravar e as cartas gravam na FICHA. `leituras_curtas.js`
segue sem diferença. Na FICHA PESSOAL, a segunda espera das missões só aparece quando se escreve por
cima de uma conta: a XP precisa da conta recalculada, então fica.

## Leituras curtas · 26/10/2026 (Claude) · instalado nas duas oficiais (ver r53/OFICIAIS.md)

As últimas leituras de aba inteira que o arnês achou no onEdit saíram (remendos 23–32 do pacote
leve; o `Codigo.gs` tem o mesmo texto). Custo modelado, antes → depois:

- habilidades custom da CONFIGURAÇÃO (AK9:AX64): ~20 s → ~7 s (lia DADOS_AM e a FICHA inteiras);
- saltos do topo da FICHA AMALDIÇOADA e da INVOCAÇÕES: ~18 s → ~11 s (a tabela vem só nas colunas
  dela, e religa só o salto em que se escreveu; caixa, alvo e nome são fixos, os outros já estavam certos);
- cartas da FICHA e caixas que esticam: ~16 s → ~11 s (só o retângulo das células usadas);
- `indiceEstatico_()` no lugar do `indice()` nas habilidades da CONFIGURAÇÃO, na caixa de
  habilidade e nas células livres: 15 células da FICHA saíram do mapa do atalho, porque o módulo
  já não lê nada nelas.

Módulo leve novo `fef2a94b…` (o da cópia de teste, `9d1cec81…`, mais o incremento do 23º em
diante: `node r53/diagnostico-android/instalar_pacote_leve.js --incremento 22 …`). O mapa do atalho
foi regerado para ele. O bloco do Caminho (`apps-script/Caminho.gs`) não muda: o gerador tira as
funções do `Codigo.gs` de antes desses remendos. Teste novo `r53/testes/leituras_curtas.js` roda a
exportação célula a célula no mapa (34 mil edições) com os dois módulos e confere as mesmas
células, formatos, alturas e propriedades, e custo nunca maior. O que sobra de mais caro (~13–16 s)
é a leitura do retângulo das habilidades custom da CONFIGURAÇÃO, a Classe da FICHA (DADOS A1:EG100)
e o salário da FICHA PESSOAL. Falta medir no Google.

## Atalho das células livres · 26/10/2026 (Claude) · instalado nas duas oficiais

Arnês novo (`r53/arnes_custo.js`) roda o onEdit instalado inteiro contra a oficial exportada
(`r53/xlsx_para_json.py`) e conta as idas ao servidor, com custo calibrado nas medições do Google.
Com pacote leve e consertos 1–3, as edições comuns já estão no piso (uma espera de recálculo).
O que sobrava: edição em célula onde o script não faz nada (texto livre, nome, descrição) ainda
lia o Amparo das Famílias (CARTEIRA, FICHA AMALDIÇOADA, INVOCAÇÕES, CONFIGURAÇÃO) e abria o
módulo só para concluir que não havia o que fazer: ~8,6 s no modelo (FICHA e FICHA PESSOAL ~3,9 s).
Com o atalho: ~2,2 s, sem leitura.

- `r53/atalho_livre.js` gera `r53/atalho_livre.gs`: mapa de onde cada uma das seis abas age, por
  força bruta no módulo (três valores, e.value espiado), mais cartões, entradas do Amparo
  rastreadas pelas fórmulas (P37 da AMALDIÇOADA, Famílias das INVOCAÇÕES, F140:G145 da
  CONFIGURAÇÃO, Trilha), salário, Caminho, paleta e versão pública. Vale só para o módulo
  `fef2a94b…` (era `9d1cec81…` até as leituras curtas) e o catálogo `e4502f59…`; com outro hash se desliga sozinho.
- Trilha e Caminho marcam `r53_amparo_sujo`: a próxima edição nas quatro abas sincroniza e desmarca.
  Achado de passagem: desde o `97abf4f` a FICHA não sincroniza as Famílias, então a troca de Trilha
  só chegava aos cartões na próxima edição dessas abas; a marca mantém isso.
- `r53/diagnostico-android/preparar_atalho.js` liga o atalho no `r53OnEditOriginal_` (reaplicar
  troca só o mapa). Teste: `r53/testes/atalho_livre.js` (4.814 verificações com a exportação em
  `nuvem-b47/saidas/atalho/`; sem ela, só as peças puras).
- Regerar o mapa depois de trocar módulo, catálogo ou layout:
  `node r53/atalho_livre.js <projeto .json> <ficha .json>`.
- Falta medir no Google (cópia descartável) antes das oficiais.

## Fila de desempenho da ficha · 25/10/2026 (Claude) · FILA ATIVA

Ramo `codex/otimizacao-android-r53` (commits `97abf4f`, `2ecb5ec`, `06b7d0d`, `5930122`),
ainda fora da `main`. Medições e decisões em
[MEDICAO-DESEMPENHO](r53/diagnostico-android/MEDICAO-DESEMPENHO-2026-10-25.md); instruções
de instalação no topo do `AGENTS.md`. As duas oficiais (`r53/OFICIAIS.md`) **não** receberam
nada desta fila: o Mizuki pediu para corrigir antes de aplicar.

Feito e medido em cópia de teste (`1kQuSgg…`, "TESTE pacote leve"): leitura única nas
edições comuns da FICHA e pacote leve. ± da vida 30,6 s (morria) → 11,5 s; Caminho
19,1 → 10,2 s; abrir o módulo 11,4 → 1,8 s; onOpen 17,9 → 2,1 s.

**Consertos 1–3 feitos (commits `79ee9cb`, `ac73543`) e medidos no Google em 26/10** numa
cópia nova da oficial na gustavohmoura12 (`1xcXsFSk…`, "TESTE consertos 1-3"): as 6 edições
do antes estouraram (30,7–31,0 s); as 9 do depois concluíram em 10,2–12,8 s (CARTEIRA,
FICHA AMALDIÇOADA, arma na mão, Força). Tabela em MEDICAO-DESEMPENHO. Lá foi instalado o
pacote leve do zero com os 22 remendos (sai `9d1cec81…`, igual ao node) e o `EditorR53`
`d2e57223…`: é o ensaio do item 5. A cópia antiga `1kQuSgg…` (cupcakemochi1201) não recebeu
nada; para ela continua valendo o caminho abaixo:
- `EditorR53.gs`: colar por inteiro a saída de
  `node r53/editor_lazy.js apps-script/EditorR53.gs <saída>`; instalado `bc300464…` → `d2e57223…`.
- módulo: `node r53/diagnostico-android/instalar_pacote_leve.js --incremento 14 2667ef41d84e44f565228bae47d7a6b9cf08bb7bfef8c60f2467383075aaee53 9d1cec81cf90bac42dd044d619843857b9c5fff3538ea0b8a0909899ff62fdce`
  gera o trecho do console; ele confere o hash instalado e aplica só os remendos 15–22.
  Salvar o projeto e conferir o hash `9d1cec81…` no `r53Modulo_`.
- Medir pelo gatilho: CARTEIRA A1 (duas vezes: a 1ª grava o estado), FICHA AMALDIÇOADA B500,
  arma na mão D64, Força. Antes: 30,6–30,7 s (tempo limite) nas três primeiras.
- Prompt pronto para outro Claude fazer isso pelo navegador (trechos embutidos, simulados num
  editor de mentira com o módulo `2667ef41…` real):
  `r53/diagnostico-android/PROMPT-INSTALAR-MEDIR-COPIA-2026-10-25.md`. Nesta sessão o Claude in
  Chrome não conectou: o app só instalou a ponte da extensão para o Edge (não para o Brave), e a
  sessão não achou o Edge mesmo depois de conectado.

Fila, nesta ordem:

1. **Sincronização das Famílias em cópia nova (crítico).** *Feito no código (`79ee9cb`):
   sem `r53_amparo_direto`, grava o amparo atual e não sincroniza; no node a edição fora dos
   cartões faz 1 leitura (era a varredura de 249 cartões). `cartoes_diretos_runtime.js` 584.* `r53SincronizarFamilias_`
   (`apps-script/EditorR53.gs`) usa `r53_amparo_direto` das propriedades do documento, que
   não vão na cópia da planilha. Sem estado, cada edição em CARTEIRA, FICHA AMALDIÇOADA,
   INVOCAÇÕES e CONFIGURAÇÃO tenta acertar os 249 cartões, estoura e não grava: medido
   30,6–30,7 s (tempo limite) três vezes. Proposta: sem estado guardado, gravar o atual e
   não sincronizar (a cópia herda os cartões já acertados da oficial). O EditorR53.gs
   instalado é o transporte de `r53/editor_lazy.js`; o código fica legível nele.
2. **FICHA PESSOAL (alto).** *Feito no código (`ac73543`): `indicePessoal_` sai do molde
   (`indiceDoMolde_`), tabelas da DADOS só nas colunas delas (`tabelaLida_`), notas vivas só no
   retângulo das caixas (`notasVivasLeves_`). Contador do node: arma na mão 12 → 2 leituras,
   capacidade da Origem 13 → 6; mesmas notas gravadas (`pessoal_leve.js`, 51).* Arma na mão (D64) estourou (30,6 s). `textoDaCapacidade_` e
   `pessoalEditada_` releem o índice pessoal (`indicePessoal_`: `getLastRow` + leitura) em
   toda edição da aba; o caminho das notas faz `flush`, `getDataRange` da DADOS e refaz as
   notas vivas (12 idas no contador). Mesmo remédio da FICHA: índice do molde,
   `faixaDoMolde_`, leitura agrupada.
3. **Força e atributos (médio).** *Feito no código (`ac73543`): o onEdit comum chama
   `fichaMexeNaPessoalLeve_` (8 → 2 leituras, mesmas notas). `fichaMexeNaPessoal_` e
   `notasVivas_` ficaram intactas e o `Caminho.gs` gerado saiu idêntico.* `fichaMexeNaPessoal_` lê a DADOS inteira e refaz as notas
   vivas (8 idas). Atenção: o `caminho_leve.js` extrai essa função e procura a linha
   `var dados = ss.getSheetByName('DADOS').getDataRange().getValues();` dela.
4. **Medir o que está no limite.** *Medido em 26/10 numa cópia nova da oficial (tabela e perfil
   por rotina em MEDICAO-DESEMPENHO): toda edição no painel de missões da FICHA PESSOAL estoura os
   30 s, mesmo com a planilha aquecida (o XP total aparece porque é fórmula; registro, data e nível
   não terminam). O cartão conclui em 23–26 s aquecido e estoura logo depois de copiar. Próximo
   passo: cortar idas no caminho da missão (`salarioEstado_` + `salarioSincronizar_` +
   `salarioMissaoDireta_`, ~10 idas) e no do cartão (`r53ValoresCartao_`, `r53LerVersao_`,
   `r53Amparo_`).* Missões da FICHA PESSOAL (27,8 s medido pelo ChatGPT;
   colunas AW:BT recolhidas) e edição de cartão (~20 s).
5. **Aplicar nas oficiais**, com o aval do Mizuki: primeiro o `Codigo.gs` da corrida
   (`r53/saidas/caminho-corrida/Codigo.gs`, ignorado; refazer trocando o bloco final do
   Codigo instalado pelo `apps-script/Caminho.gs`), depois o trecho de
   `instalar_pacote_leve.js` (já com os 22 remendos: sai `9d1cec81…` direto, sem o incremento),
   e o `EditorR53.gs` novo (`d2e57223…`). Se os remendos da FICHA mudarem,
   regenerar `pacote_leve_remendos.json` e o hash esperado.

Fora da fila, sem efeito para o jogador: `regressao-construir`, `-pessoal` e `-paleta`
falham pelo Sheets de mentira desatualizado (já falhavam antes); a corrida do personagem
novo (Trilha terminando antes do Caminho) ficou aberta por decisão dele;
`PaletaAndroid.gs` (591 KB) carrega em toda execução.

Como medir: `r53/diagnostico-android/medir_carga.gs` (colar num arquivo vazio de uma
cópia), registro em `script.google.com/u/1/home/projects/<id>/executions`. O editor proíbe
`new Function` em código assíncrono da página; o seletor de funções só lista as do arquivo
aberto.

## R53 publicada na oficial · 19/10/2026

A ficha oficial foi atualizada, limpa e validada no mesmo endereço. Cartões diretos,
Formas custom, notas e ajustes da ficha estão integrados. Zero erros de fórmula nas
25 abas; sete visíveis; exportação final com 18.394 chaves e nenhum teste ativo.
Código confirmado em sete módulos, 29 legados incorporados e manifesto preservado.
Backup e provas em [ENTREGA](r53/ENTREGA.md). Este estado prevalece sobre o histórico abaixo.
Ramo de entrega: `codex/publicacao-r53`. Não repetir migração/inserções nem executar
construir()/continuar(). Aguardar os campos na troca de Classe. Sol/High para
manutenção integrada; Medium para conferência focal.

## Histórico anterior (não é fila ativa)

## Fechamento global R53 concluído na revisão · 19/10/2026

Cartões diretos, Formas custom, notas e proteção de troca de Classe foram
aplicados e conferidos. [Entrega e limites](r53/ENTREGA.md) prevalecem sobre os
checkpoints antigos abaixo. Foram preservados 290 campos de configuração;
sete arquivos relidos iguais; zero erros nas 26 abas; exportação real válida.
O fluxo custom e Amparo foram testados nativamente, com os limites assíncronos
documentados. A ficha oficial não foi alterada; sem commit/push/publicação.
Não reaplicar inserções, migrações anteriores nem construir()/continuar().
Sol/High para manutenção integrada, Medium para conferência focal.

## Cartões diretos R53 · aplicados na revisão · 19/10/2026

Este bloco substitui os estados antigos de painel/checkbox Editar abaixo.
Os 249 cartões estão editáveis no próprio local; aplicação incremental concluída
na revisão, com backup, 232 campos preservados e sete arquivos de código relidos.
Zero erros nas 26 abas; sete visíveis inspecionadas. Classes, pontos, Amparo,
dados fixos e redutor deslocado conferidos no Google. Exportações reais da revisão
e da QA válidas. Detalhes e limites em [ENTREGA](r53/ENTREGA.md).

Sem pendências desta implementação na revisão. Oficial intacta; sem commit/push
ou publicação oficial. Não repetir inserção de linhas, lotes ou limpeza antiga.
Manutenção integrada: Sol/High; conferência focal: Medium.

## B85 · R53 implementada e validada na cópia · 19/10/2026

[Entrega, ficha de revisão e roteiro](r53/ENTREGA.md). Este bloco substitui os checkpoints parciais anteriores. Os 249 cartões estão integrados, incluindo as 36 Liberações e 12 máximas de entidades. MONTAGENS permanece oculta; as duas abas de testes e os exemplos sintéticos foram retirados da entrega.

89 casos aprovados no Google Sheets; 14 testes unitários, 54 verificações do editor e 12 de migração do armazenamento. Cópia nativa com sete modalidades válidas, edição/reabertura preservando pontos e máximas de entidade conferidas. Contrato ANALISE12 real validado com 10.173 chaves R53. Zero erros de fórmula nas 26 abas, inspeção das sete visíveis e 249 caixas Editar válidas.

Nenhuma pendência obrigatória de implementação desta entrega. Oficial preservada; sem commit, push ou publicação. Registros de recuperação ocultos e snapshots locais mantidos. B84 continua sendo otimização futura de carregamento sob demanda. Para manutenção de integração, Sol/High; conferência focal, Medium.

## Extensões custom e numeração · concluídas na oficial

Quinze áreas retráteis aplicadas e treze listas de CONFIGURAÇÃO numeradas
01–13. Valores, escolhas e limites preservados; zero erros nas 22 abas;
código 36/36 relido igual após recarregar. Cópia e backup retirados para a
lixeira. Sem pendência deste pedido. [Fechamento](acabamento-b47/EXTENSOES-CUSTOM.md).

## Ajuste visual posterior concluído · CONFIGURAÇÃO horizontal

Oficial atualizada e validada: 14 listas recolhíveis à direita, cartões em
pares, índice e uma abertura com legenda por lista. 2.575 notas inúteis ou
repetidas removidas; 1.420 específicas preservadas. Código 36/36 relido igual,
campos/validações/8.190 chaves preservados e zero erros nas 22 abas. Dois
temporários deste ajuste movidos para a lixeira. Sem pendências deste pedido.
[Fechamento e provas](acabamento-b47/CONFIGURACAO-HORIZONTAL.md).

## B47 · entrega concluída na oficial · 17/10/2026

**Limpeza posterior solicitada pelo usuário:** 33 planilhas temporárias B47, incluindo backups e revisão de exemplos, movidas para a lixeira. Oficial preservada e relida com 22 abas. Links de cópias/backups abaixo são históricos; não recriar. Código e provas necessários permanecem no Git, dados pessoais não. [Inventário](acabamento-b47/LIMPEZA-B47.json).

**Oficial B47 validada e liberada para cópias.** Estado vigente em
[RETOMADA-D.md](acabamento-b47/RETOMADA-D.md) e
[fechamento](acabamento-b47/OFICIAL-FECHAMENTO.md). Este bloco prevalece sobre
os registros históricos abaixo. C, D, testes antigos e medidas concluídos.

Janela acompanhada autorizada; backup novo conferido. 35 GS + manifesto
relidos iguais (36/36); construção final FICHA PRONTA. Comparação completa:
22 abas, 66.242 fórmulas, 8.190 chaves únicas, zero erros e diferenças
inesperadas. Regras condicionais iguais por API. Cópia com troca de paleta
interrompida validada e controles restaurados; persistência confirmada depois
da queda do PC. Dados do personagem fora do Git; revisão preenchida intacta.

Nenhuma pendência obrigatória desta entrega. B84 é otimização futura de
carregamento sob demanda, não implementada nem necessária demonstrada ao
fechamento atual. Sol/Médio para manutenção focal, se houver novo pedido.

## Histórico desta retomada · regressões no Google · 17/10/2026

Amaldiçoada concluída: 20 fichas/80 blocos nativos, 354 verificações totais
(dados/livro, estrutura e VM), 442 entradas restauradas sem diferenças.
As 11 falhas antigas foram reproduzidas e explicadas sem relaxar números.
Prova `acabamento-b47/REGRESSAO-AMALDICOADA-NATIVA.json`.

Usuário pediu priorizar o cálculo nativo. Ficha Pessoal: 33 cenários e 118
asserções originais aprovados, entradas restauradas e 39 blocos sem diferenças
(`acabamento-b47/REGRESSAO-PESSOAL-NATIVA.json`). Calc não executado neste
Windows. Configuração também aprovada nativamente: sete cenários, 529
asserções mecânicas, somas cobrindo todas as 86 caixas de C e 191 entradas
restauradas sem diferenças (`REGRESSAO-CONFIGURACAO-NATIVA.json`).
Progressão: nove cenários/15 asserções e 26 checagens estruturais aprovados,
incluindo `livro_base` histórico nativo dos GS 03a459e, verificado contra a
fixture compactada, com expansão estrita dos moldes. Famílias: todos
os 13 cenários/130 resultados e sete checagens estruturais aprovados.
Entradas restauradas exatamente nas duas frentes. Campanha também concluída:
12 cenários, 18 asserções e 26.689 valores históricos conferidos; 36 diferenças
classificadas com endereço/valor exatos e cinco contraprovas, nenhuma restante.
Prova `acabamento-b47/REGRESSAO-CAMPANHA-NATIVA.json`. Custom concluído:
dez cenários/31 asserções e 27.318 valores anteriores conferidos, zero erros
ou diferenças inesperadas; Latente permite a marcante publicada e rejeita a
própria. 185 entradas restauradas exatamente (`REGRESSAO-CUSTOM-NATIVA.json`).
Item 3 concluído pelo backend Google. Restam medidas/perfil e oficial
acompanhada. O risco Latente deixou de estar pendente nativamente.

D permanece concluída; dados do personagem fora do Git.
Estado vigente no topo de `acabamento-b47/RETOMADA-D.md`.

## B47 · parada para troca de chat · 17/10/2026, noite

D concluída e em `main`. Corrigido bug das ajudas de tipo dobradas em cópias (publicado na revisão). Carga da ficha pessoal: a ficha segue o livro; teste corrigido. Manutenção de testes antigos pela metade e roteiro da oficial aguardando o usuário. Ponto exato em [RETOMADA-D.md](acabamento-b47/RETOMADA-D.md); prompt em [PROMPT-CONTINUAR-POS-B47.md](prompts-b47/PROMPT-CONTINUAR-POS-B47.md).

## B47 · fechamento, revisão e merge · 17/10/2026

Cópia funcional com troca de paleta interrompida: sem deriva. S58 corrigida. Construção do zero com o código final: FICHA PRONTA, fórmulas idênticas à revisão. Bateria executada e classificada; falhas são anteriores à sessão e precisam de manutenção de teste ou decisão de regra (carga da ficha pessoal +0,8). Revisão sem bloqueio para `main`. [Detalhes](acabamento-b47/RETOMADA-D.md).

## D · CONCLUÍDA na revisão · 17/10/2026

Fundo de CONFIGURAÇÃO aplicado e provado nativamente; 12 ajudas mantidas; deriva de paleta corrigida (`paleta_base` em `Codigo.gs`, bateria pertinente aprovada, publicado e relido 36/36 no projeto da revisão); auditoria final da planilha inteira sem diferenças. Fora de D: `INVOCAÇÕES!S58` sem causa conhecida, dois testes com falha antiga, promoção da revisão a decidir. [Fechamento](acabamento-b47/RETOMADA-D.md).

## D · aplicada na revisão e auditada · 17/10/2026, noite

Fundo de CONFIGURAÇÃO aplicado na revisão por `repeatCell` com guarda e releitura nativas (conector Sheets): faixa idêntica à descartável, zero mudança fora das 3.988 células. Apps Script auditado: 35 GS + manifesto iguais, contêiner = revisão, 0 acionadores instaláveis. 12 ajudas de INVOCAÇÕES mantidas (`onOpen` canônico). Deriva de paleta da descartável: causa reproduzida (cópia sem `paleta_feito` + troca interrompida), correção `paleta_base` proposta com bateria 51/51, **não aplicada, aguarda decisão**. Detalhes no topo de [RETOMADA-D.md](acabamento-b47/RETOMADA-D.md). D não declarada concluída.

## D · fundo pela interface interrompido · conector Sheets disponível · 17/10/2026

12 ajudas de INVOCAÇÕES entraram na revisão pelo `onOpen` canônico ao abrir a planilha; usuário decidiu manter. Fundo de CONFIGURAÇÃO começou pela interface (colar formatação) e um lote danificou cartões (29 mesclagens, 381 formatos, 2 validações; valores intactos); o usuário corrigiu à mão, **correção ainda não conferida**. Conector Google Sheets agora disponível e testado em leitura: retomar o fundo por `repeatCell` com guarda nativa. Detalhes no topo de [RETOMADA-D.md](acabamento-b47/RETOMADA-D.md). D não concluída.

## D · fotografia da revisão por exportação · 17/10/2026

Revisão após fuso + retirada dos estudos (feitos por outra sessão, com backup e snapshot) conferida por exportação somente leitura: igual ao snapshot e ao backup nas 22 abas, zero erros, 8.190 chaves. Plano do fundo de CONFIGURAÇÃO pronto (3.988 células, 313 intervalos), **não aplicado**: esta sessão não tem escrita Sheets nem Apps Script. Achado: deriva de cor de fonte na FICHA da descartável após o ensaio de paleta; a revisão está correta. Detalhes, itens confirmados/pendentes em [RETOMADA-D.md](acabamento-b47/RETOMADA-D.md). D não concluída.

## D autorizada · checkpoint de abertura · 16/10/2026

Atualização D: retirada dos estudos ensaiada, fundo canônico corrigido na descartável, textos longos restaurados exatamente, seis grupos de entidades restaurados e 35 GS + manifesto da cópia relidos iguais. Retenção A+B no modelo integrado: 83 verificações, zero falhas bloqueantes, dois riscos de manutenção documentados. Detalhes e **próxima ação vigente na última seção** de [RETOMADA-D.md](acabamento-b47/RETOMADA-D.md). A revisão ainda não recebeu D; não declarar fechamento.

C está concluída e publicada em `21f1620`. Após esse fechamento, o usuário autorizou D e pediu checkpoints frequentes devido ao saldo de 2% semanal. [Retomada vigente de D](acabamento-b47/RETOMADA-D.md) e [prompt portátil](acabamento-b47/PROMPT-RETOMADA.md). A auditoria dos estudos e o [ensaio de retirada](acabamento-b47/ENSAIO-RETIRADA-ESTUDOS-CLASSIFICADO.json) passaram: cópia D com 22 abas, zero diferenças inesperadas/erros e 8.190 chaves. Doze ajudas novas em notas vazias foram conferidas individualmente contra a fonte canônica. Próximo bloco: acabamento visual e demais testes D. A revisão permanece no estado validado de C, com os estudos ainda presentes.

## Histórico: C concluída na revisão nativa · parada antes de D · 16/10/2026

Limite confirmado: concluir somente C e parar antes de D. Construção conjunta
concluída (22 abas, 35 GS e manifesto relidos iguais); 467.365 células sem erro
na leitura vazia. [Cenários preenchidos](conteudos-b47/comum/CENARIOS-C-NATIVOS.json):
1.216 verificações, incluindo os 201 seletores de Forma, 24 cartas de
Aptidões/Talentos, Tipos/Talentos nas 12 entidades e interações com Condições
e dano custom. Restauração confirmada em 18 blocos: valores, notas e validações.

[Migração 10→11 ensaiada](conteudos-b47/comum/MIGRACAO-C-DESCARTAVEL.json) na cópia
preenchida: 26 abas, zero erros de fórmula/diferenças inesperadas, 8.190 chaves
únicas, 3.837 notas antigas preservadas. Das 7.356 chaves antigas, somente a
versão mudou; o leitor mantém o mesmo aviso anterior. Código vinculado:
35 GS e manifesto persistidos e relidos iguais. Lotes próprios preservam as
entradas e não removem abas/linhas; não reutilizar lotes A+B.

**A revisão autorizada recebeu C e está no formato 11. D não foi iniciada.**
[Prova da revisão](conteudos-b47/comum/MIGRACAO-C-REVISAO.json): backup novo,
63 blocos de snapshot + 63 de releitura idêntica, 133 lotes confirmados e
76 blocos finais. Zero erros de fórmula/diferenças inesperadas; 8.190 chaves
únicas; entradas nos mesmos endereços e 3.837 notas antigas preservadas.
[35 GS e manifesto relidos iguais](conteudos-b47/comum/NATIVO-CODIGO-REVISAO-C.json).
As 7.356 chaves anteriores mantêm os valores, salvo `formato.versao: 10→11`.
O leitor mantém o único aviso anterior, de escolhas de perícia incompletas;
isso é preenchimento da ficha, não erro novo de conteúdo ou fórmula.

[Fechamento e limite](conteudos-b47/comum/FECHAMENTO-C.md). Não iniciar D,
remover estudos, reorganizar o desenho ou ampliar a bateria sem nova instrução.
Oficial, bot, main e acessos permanecem fora do escopo.
Recomendação para eventual retomada: GPT-6.1 Sol, Médio, começando pela
leitura deste fechamento. Nenhuma execução adicional ficou agendada.

## Histórico · C integrada localmente · prova conjunta então em andamento

Recebidas personagem `e9af8d3` e entrega parcial Claude `045f699`; o usuário
transferiu para este integrador o restante após o limite de créditos. Nenhuma
entrega futura de Claude é bloqueadora. [Conciliação, testes, cópias e próximos
passos](conteudos-b47/comum/INTEGRACAO-CD.md).

Núcleo local: ANALISE 11, **8.190 chaves**, três frentes, **35 GS** da geração
`9273911dd8b6f47a`, maior 840.243 bytes. Passaram 75 testes de personagem,
7 da combinação, 37 checagens do carregador/20 ordens, compactação de 22 abas
+ três fixtures, 150 checagens da construção simulada em três fases, nove
casos de notas e smoke. Achados de vazios numéricos/lógicos e resumos da
revisão cruzada corrigidos; recálculo nativo completo ainda pendente.

Ensaio focal de personagem/comuns: 291 asserções de herança, 91 em dez
cenários negativos/literais/sem base, 94 entradas restauradas exatamente,
31.580 células finais sem erro. Essa cópia ainda tem GS/ANALISE principal v10;
não é prova da combinação final. Nova descartável de construção integrada
`14Ad8e5hUECLimCFuilEGSIxrhv0IWpDUEjEBR4N8N-Q` criada; envio/releitura e
testes Apps Script em andamento. **35 GS e manifesto salvos/relidos iguais**
([prova](conteudos-b47/comum/NATIVO-CODIGO-INTEGRADO.json)); ao iniciar construir
nessa nova descartável, o Google pediu autorização do novo projeto, concluída
pelo usuário. Execução reiniciada às 20:41:27 locais; construção ainda em
andamento, sem conclusão declarada. Três testes
adicionais do módulo canônico de entidades passaram, incluindo três pares de
capacidades e guardas. Preservar as cópias e recibos anteriores.

Revisão preenchida permanece no fechamento A+B/formato 10. Não executar
construir/continuar nela nem repetir lotes antigos. Faltam prova conjunta,
D, migração v10→v11 em descartável e aplicação guardada da revisão.
Oficial, bot, main e acessos intactos. Calc ausente neste Windows.
Recomendação: GPT-6.1 Sol, High, para testes nativos e preservação na migração.

## Histórico · comuns locais e fórmulas nativas · 16/10/2026

Primeira entrega do integrador: dez Tipos de dano compartilhados e Condições
como modalidade dos mesmos 30 cadastros de Melhoria. Fontes e leitor no
formato 11 inicial, 7.436 chaves (80 novas, 7.356 anteriores preservadas salvo
versão). Geração `7adee586c04accf6`, 22 GS, maior 816.375 bytes. A revisão
preenchida continua no fechamento A+B/formato 10; não houve migração C nela.

[Relatório](conteudos-b47/comum/RELATORIO.md) e
[provas/hashes](conteudos-b47/comum/VALIDACAO.json): dez testes locais,
12 checagens do carregador/oito ordens, compactação de 18 abas + três fixtures,
sete cenários de texto. Na nova descartável
`1BzVzrqjKsarh6DCAu6FGZ_yOxy0aBzttfX4n1JH2QFI`, 48 asserções de fórmulas,
12 seleções de reuso, 29 campos restaurados e 968 células sem erro. Os 80
campos foram testados em CD_TESTE_ANALISE; ANALISE principal e GS vinculados
permaneceram v10 nesse ensaio. Isso não encerra C nem valida o código nativo novo.

Claude `50bcc00` disponível no Git, ainda em revisão e sem relatório recebido;
personagem não recebido. Continuar revisão/integração das frentes, validar o
pacote combinado no Apps Script e executar D antes de migrar a revisão.
Calc ausente. Oficial, bot, main e acessos intactos. Próximo modelo/esforço
recomendado: GPT-6.1 Sol, High, para preservar contratos durante integração.

## C+D iniciados · contrato comum inicial · 16/10/2026

Usuário usou o prompt 1 e iniciou o integrador. Base comum confirmada:
`0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd`, checkout inicial limpo e os dois
ramos remotos iguais. [Contrato inicial](conteudos-b47/comum/CONTRATO.md) e
[campos/capacidades estruturados](conteudos-b47/comum/contrato.json) disponíveis
para conciliar as frentes: dez cadastros de cada tipo novo, vinte Talentos de
entidade, Condições dentro das 30 Melhorias. Endereços derivados e formato 11
ainda proposto; não declarar conteúdo integrado nem prova nativa nova.

Smoke com PYTHONUTF8=1 passou; Calc permanece ausente. Nenhuma geração integral
ou escrita Google nesta preparação. Personagem/entidades ainda não recebidos.
Próximo trabalho independente: Tipos de dano e Condições, com testes focais.
Recomendação: GPT-6.1 Sol, High, para integração e preservação do contrato.

## Planejamento preparado · divisão C+D · 16/10/2026

Usuário aprovou publicar a divisão em três chats no total: integrador atual
(Tipos de dano, Condições, núcleo, integração, Google e D), outro Codex
(Formas para personagem/entidades, Aptidões/Bênçãos e Talentos do personagem)
e Claude (Tipos/Talentos de entidade e revisão cruzada de personagem).

[Plano C+D](PLANO-PARALELO-CD-B47.md) e [três prompts](PROMPT-WORK-B47.md)
publicados como preparação. O uso de cada prompt inicia/autoriza sua frente;
esta publicação não implementa C/D nem abre chats. A+B permanecem concluídos
em `dce00ab`. Núcleo/Google só com integrador; auxiliares entregam módulos,
patches e testes isolados. Estimativa provisória conjunta: 8–14h de trabalho
ativo, revista no primeiro checkpoint. Bot, oficial, main e acessos fora.

Próxima ação: usar os três prompts, mantendo a mesma base de preparação e
registrando o SHA real. Codex: recomendação de planejamento GPT-6.1 Sol, High;
Claude: confirmar opções reais da conta e recomendar modelo/esforço disponíveis.

## Checkpoint vigente de implementação · A+B nativos concluídos · 16/10/2026

10 Famílias extras, 30 Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios
compartilhados; livro, 25 cartões 3a, Caminho/Trilha e nove Famílias por
invocação preservados. C/D não iniciadas; esta entrega encerra somente A+B.

A revisão Google está em ANALISE 10: 7.356 chaves únicas nas quatro colunas,
509 entradas/notas exatas, zero erros de fórmula e zero divergências em
400.917 células de 17 abas. Mais 22.094 células superiores/carteira/ficha
pessoal/cache conferidas contra o backup; única mudança esperada G160 ao
remover a cauda. Os 20 GS e manifesto foram relidos integralmente iguais.
Quatro estudos e três grupos superiores preservados; só 793–794 ocultas.

Construção integral, visual, menus, casos negativos, textos e gatilhos da
cópia funcional sem ativação manual concluídos. B inclui visibilidade herdada,
bootstrap Windows/LF e remoção de formatação redundante comprovada nativamente.
19/19 guardas/migração e sete contraprovas da coalescência passaram.

Base `ad1b55d`; correções PC `1448436`, `50ba7c7`, `1341d48`; produção GS
continua f1ff7a6/geração f85ffda549994a3f. Publicação em `codex/b47-capacidade`
e integração por avanço normal em `codex/configuracao-b47`. Oficial, main,
bot e acessos intactos. Bot/formato 10 e variante histórica 4 são pendências
externas; Calc/fcntl indisponíveis no Windows estão documentados.

[Checkpoint e caminhos privados](capacidade-b47/RETOMADA-PC.md) ·
[Prova da descartável](capacidade-b47/VALIDACAO-NATIVA-PC.json) ·
[Prova final da revisão](capacidade-b47/REVISAO-NATIVA-PC.json) ·
[Publicação e SHAs](capacidade-b47/PUBLICACAO.md).
Este checkpoint prevalece sobre os registros históricos abaixo.

Próxima ação/modelo: **GPT-6.1 Sol, High**, para revisar o fechamento e o uso de
A+B. C/D dependem de nova autorização; não há início automático da próxima etapa.

---

## Checkpoint anterior · A+B local e Sheets descartável · 16/10/2026

Redução local implementada: 10 Famílias, 30 Melhorias, 30 Restrições,
10 Perícias e 10 Ofícios compartilhados. ANALISE 10/7.356 chaves, sem reutilizar
namespaces dos treinos retirados; livro, 25 cartões 3a, Caminho/Trilha e nove
Famílias por entidade preservados. Medidas, comandos, resultados e SHAs em
[capacidade-b47/RELATORIO.md](capacidade-b47/RELATORIO.md).

A revisão Google permanece no formato 9 e não recebeu escrita nesta rodada.
A retomada criou backup nativo, snapshot integral das faixas alteradas e uma
descartável: 102 lotes confirmados, ANALISE 10/7.356 chaves, 22 checagens,
zero erros em 118.493 células de 11 abas; 48 entradas temporárias restauradas.
Detalhes e IDs em [NATIVO-PARCIAL](capacidade-b47/NATIVO-PARCIAL.md).
Apps Script/navegador não estão disponíveis para salvamento/execução. A prova
é PARCIAL e não libera a revisão: falta código vinculado, visual, gatilhos,
construção/medidas nativas e testes combinados. Seguir
[ROTEIRO-NATIVO](capacidade-b47/ROTEIRO-NATIVO.md), com snapshot renovado
antes de uma aplicação futura.

Recebidas e integradas infra `b8ab7b5` e revisão `287b2c1` no ramo alternativo
`claude/kind-feynman-sewhec`. A listagem inicial era incompleta porque o fetch
buscava só main. A combinação recebeu testes e correções de carregamento misto,
remoção explícita, avisos/erros do leitor e validações 3a longas. As origens estão
no relatório. A revisão externa reproduziu A em `4610c88`; o novo `efd8dd8`
auditou o núcleo em `8276ca6`, integrado em `3323803`, com teste de envio 10/10.
Ferramentas posteriores em `186e844`/`6a226c3` receberam testes do integrador. Oficial,
main, bot e acessos não foram alterados. C/D seguem
na fila. O roteiro focal concluiu 23 etapas após reexecução de Progressão;
a evidência conserva o resultado bruto e a correção histórica exata.
Este checkpoint prevalece sobre as contagens históricas abaixo.

Próxima ação/modelo: **GPT-6.1 Sol, High**, para salvar/reler o código da
descartável, validar o conjunto nativo e só depois migrar a revisão preservando entradas.

---

## Preparação para nuvem · 16/10/2026

[NUVEM.md](NUVEM.md) e [AGENTS.md](AGENTS.md) são a entrada de execução. Dependências Python fixadas, fontes/licenças, quatro fixtures históricas com hashes e texto de consulta da R52 estão no Git. Gerador, contratos, arte e exemplo DOCX já eram versionados. Regressões não devem procurar referências nas pastas do PC; os caminhos ativos de campanha/custom/progressão/Famílias foram ajustados. O comparador dispõe de original.xlsx histórico em fixtures. Há setup, diagnóstico/smoke e CI sem Google. Expectativas antigas de formatos 5/6/7 continuam uma pendência de manutenção em A/B, não uma aprovação da versão 9. Helpers de migração da sessão antiga dependem de snapshots/IDs daquela sessão e não são o fluxo de retomada. Somente o integrador obtém nova leitura/snapshot e aplica mudanças nativas quando a nuvem dispuser de acesso direto autorizado. Esta preparação não aplica redução ou migração. Validação em cópia isolada: instalação e 67 checks de smoke; exportação atual; 54 checks mecânicos; sete cenários de texto; compactação de 20 abas/fixtures; geração completa com os 23 .gs idênticos byte a byte aos versionados. Detalhes em nuvem-b47/VALIDACAO.json. Nenhuma aplicação no Google nesta preparação.

## Retomada portátil vigente · 16/10/2026

O plano consolidado, as tarefas restantes e as decisões estão em [PLANO-RETOMADA-B47.md](PLANO-RETOMADA-B47.md). Este documento passa a ser o ponto de entrada para outra máquina/Work e prevalece sobre os checkpoints históricos abaixo. Prompt: [PROMPT-WORK-B47.md](PROMPT-WORK-B47.md). Contrato: [ESQUEMA-ANALISE.md](ESQUEMA-ANALISE.md). Ramo: `codex/configuracao-b47`; implementação atual84d8f8c.

Rota: A)capacidade → B)carregamento/envio e roteiro de testes → C)conteúdos restantes3c → D)interface e auditoria final. Alvos:10Famílias extras,30Melhorias,30Restrições,10Perícias e10Ofícios compartilhados. Não houve redução aplicada nesta publicação. Manter checagens focais durante o trabalho e a revisão abrangente ao final. Não rodar montagem na revisão preenchida ou na oficial.

Execução paralela vigente: [PLANO-PARALELO-B47.md](PLANO-PARALELO-B47.md), com três [prompts](PROMPT-WORK-B47.md). Ramos de tarefa: `codex/b47-capacidade`, `claude/b47-revisao` e `codex/b47-infra`; partem da mesma publicação deste plano. Chat 1 integra as frentes em `codex/configuracao-b47`; chat 2/3 escrevem só em `revisao-b47/` e `infra-b47/`. Ao usar os prompts, estão autorizados commits/push nos ramos próprios e integração revisada pelo chat 1. Sem merge no main, force push ou alteração na ficha oficial. Todos devem sempre recomendar modelo/esforço para a próxima ação. Esta publicação é documentação, não aplica redução ou migração. Os registros abaixo descrevem a implementação anterior à limpeza, já salva no Google.

---

## Estado vigente · 16/10/2026 · Melhorias/Restrições encerradas; PAUSA SOLICITADA

Etapa de Melhorias e Restrições integrada e validada na cópia nativa de revisão 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0. Usuário pediu pausar ao terminar esta etapa. NÃO iniciar Formas ou outro catálogo até uma nova retomada. Não criar automação. Ficha oficial e bot intactos.

Migração pontual: 66 lotes, sem construir() e sem importar Excel. Guarda de 4.270 fórmulas passou; 13.808 valores/fórmulas anteriores preservados; 1.184 menus atualizados; somente B4031, antes vazia, recebeu o cabeçalho. ANALISE 9 da revisão: 75.796 células comparadas, 18.948 chaves únicas, zero diferenças; 13 abas sem erros. As 9.082 chaves anteriores foram preservadas. Provas pecas-revisao-guarda.json, pecas-revisao-preservacao.json e pecas-revisao-analise-conferida.json em ../evidencias-3b/.

Código: os 13 arquivos alterados/novos foram salvos e relidos integralmente após recarga de outra sessão. A correção final de Codigo.gs também foi salva pelo usuário, recarregada e comparada integralmente. Projeto com 23 .gs, soma 9.543.357 bytes e máximo 843.661 bytes por arquivo. Evidências pecas-scripts-nuvem-conferidos.json e pecas-scripts-manifesto-correcao-texto.json. Nenhum helper temporário no projeto.

Testes locais: 54 verificações focais; 22 ordens de carregamento e 19 ausências; 150 verificações do fluxo de construção em três fases. conferir-copias.py passou em 20 abas/fixtures. O leitor completo python3 ler-analise.py --teste também terminou com código0 e TESTE:OK:18.948chaves, formato9; somente o aviso esperado da ficha vazia, faltando escolhas de perícia/ofício. Prova pecas-leitor-final.json. No Google: 15 pares base/custom iguais em 17 campos; todas as 395 entradas do cenário restauradas exatamente. Dos 566 valores consultados, 16 diferenças contra o workbook focal eram simétricas nos pares de invocação, pelas Famílias Livres já presentes na cópia; não eram divergências entre livro e custom. Detalhes em pecas-cenario-nativo/.

Visual e texto: primeiros/últimos cartões, carteira/foto/paleta, FICHA e nove Famílias de invocação conferidos nas capturas pecas-*.jpg. Textos vizinhos de 2.401/3.545 caracteres esticaram as linhas a 110/186 px; apagar um lado preservou o outro; limpar ambos devolveu 25 px. O último cartão mostrou 2.755 caracteres inteiros e bordas contínuas. A primeira limpeza atingiu o limite de 30 s: corrigido esticarCaixas_ para ler os limites da edição somente quatro vezes, sem repetir chamadas de Range em 1.219 grupos. Sete cenários focais passaram. Reteste nativo completo curto/longo/limpeza: 25/68/25 px nas sete linhas; execuções concluídas em 18,769/12,998/11,862 s. Todos os três campos e notas restaurados exatamente. Evidências pecas-textos-correcao-final.json, pecas-textos-restauracao-conferida.json e pecas-gatilhos-nativos-final.json. Captura final limpa: pecas-revisao-ultima-restricao-restaurada.jpg.

Capacidades desta implementação: 789 Melhorias e 395 Restrições, como limites superiores para cobrir os espaços existentes. NÃO é fechamento de capacidade/custo geral da 3c. Ainda faltam Formas, aptidões/Bênçãos, Talentos, tipos/Talentos de entidade, condições e danos; depois medição nativa de construir() na descartável e reunião/limpeza da interface. Todos os protótipos e as escolhas mecânicas restantes já aprovados continuam válidos; não reabrir sem motivo.

Nenhum commit ou push pelo agente. Ao encerrar, índice preparado apenas com arquivos desta etapa; mensagem em mensagem-de-commit.txt. Comando, a partir desta pasta: git commit -F mensagem-de-commit.txt. Retomada principal: ../RETOMAR-B47.md. A implementação nativa está salva; nenhuma autorização Google nem reconexão é necessária para encerrar.

---

## Histórico anterior · peças na cópia nativa

Melhorias/Restrições implementadas localmente: 789/395 registros, cobrindo as vagas atuais; capacidade global/custo ainda não fechados. Geração03 concluiu, 23 .gs, 9.542.502 bytes totais; maior Configuracao.gs843.661. Alturas/caixas expansíveis foram transportadas para PecasPainel.gs, sem alterar a grade. Notas só se propagam nas cópias com sétimo campo true; legado preserva ajuda só no primeiro cartão. Otimizadas inserção de mesclagens e conferência de bordas, com comparação de valores/estilos/bordas contra openpyxl.

Cópia NATIVA1D215acC6Dxhu8i7x0aF7pmiNbJ95_U1CiH4980QozLk agora migrada pontualmente, ANALISE9/18.948 chaves. 66 lotes agrupados aplicados, manifesto e progresso em evidencias-3b/pecas-lotes-nativos/agrupados e pecas-progresso-nativo.json. NUNCA reutilizar esses lotes diretamente na revisão sem nova leitura/guarda. Review1EdEX... e oficial sem alterações nesta retomada; nenhum .gs desta etapa salvo no editor ainda.

Regressão focal54checagens passou. Nativo: 15 pares base/custom iguais em17 campos;566 consultas,550 valores coincidentes com calculadora local.16 diferenças de contexto em ambos os membros dos pares de invocação vieram das Famílias Livres presentes na cópia, ausentes no workbook focal. Índice de preços0 do cenário provocou spill na exibição; cenário corrigido para1, sem alteração de produção. Todas395células restauradas e relidas com igualdade integral. Varredura de erros após restauração: zero em FICHA, CARTEIRA, FICHA AMALDIÇOADA (separada), INVOCAÇÕES, FICHA PESSOAL, DADOS_AM, DADOS_INVOC, DADOS_MELHORIAS, DADOS_RESTRICOES, DADOS_CRIACAO, DADOS_CUSTOM, DADOS_PROGRESSAO, ANALISE. Evidências em pecas-cenario-nativo/. Menus/checkboxes/notas de primeiro e último cartões relidos nativamente. Imagens pecas-nativo-*.jpg são capturas reais; as pecas-previa-*.png continuam prévias locais.

Usuário reconectou Brave. CUA editor2140372548 (Código.gs salvo antigo), teste2140372597; browser3. Sessão de testes serial61481 está rodando conferir-copias.py final, depois regressao-construir.js3fases, tetos3G/1,5G/duasCPUs. Não iniciar outro trabalho pesado simultâneo. Próximo: fechar testes, salvar os arquivos alterados/novos com leitura integral antes/depois no Apps Script, terminar visual nativo, migrar revisão com guarda, atualizar contrato/roteiros e preparar índice/mensagem sem commit. Formas e demais tipos3c continuam pendentes; não declarar3c concluída.

## Histórico anterior · atualização da retomada · 16/10/2026

A regressão focal de Melhorias/Restrições passou54checagens; prova evidencias-3b/pecas-regressao.json e log correspondente. Inclui herança em ambas as fichas e Classe0, nome literal com curingas, nona Família, TR/Controle, última vaga, inválidos e limites da devolução. Corrigidas duas falhas encontradas: referências de linha impediam a herança; campos numéricos de linhas excluídas precisavam ser0 para não cobrar caixas vazias. conferir-copias.py também passou com testes de complementos em duas ordens e idempotência, nas15abas antigas mais2fixtures. Geração integral em execução serial no momento deste registro (sessão92187, PID8956, memória~300MB; não iniciar outro teste pesado antes de terminar). Ainda não há .gs novos entregues.

Nova cópia NATIVA de teste, feita integralmente da revisão pelo Drive, sem Excel:1D215acC6Dxhu8i7x0aF7pmiNbJ95_U1CiH4980QozLk, “TESTE DESCARTÁVEL — B47 — Melhorias e Restrições3c”, pasta ChatGPT. Metadados em evidencias-3b/pecas-teste-metadata.json; mesmos19sheetIds da revisão. Até este registro a cópia está SEM MIGRAÇÃO, idêntica à revisão/ANALISE8. Revisão e oficial sem alterações. Usar essa nova cópia para a migração pontual de peças antes de mexer na revisão; não confundir com a antiga descartável reservada ao construir() integral.

CUA nesta retomada retorna zero navegadores; tentativa explícita de abrir IAB devolveu “Browser is not available:iab”. Pedido assíncrono para reconectar Brave está pendente; não repetir autorizações Google nem pedir permissões já dadas. open_in_codex da revisão ficou queued. As quatro prévias pecas-previa-*.png foram renderizadas LOCALMENTE da grade/estilos e inspecionadas: primeiros/últimos cartões sem bordas faltando. Não são capturas do Google e não substituem a conferência visual nativa. Próximo trabalho independente: concluir geração e testes do carregador/custos, preparar migração pontual na nova cópia nativa e testar as contas pelo MCP. Salvamento dos scripts e visual Google dependem da conexão do navegador.

---

## Retomada em andamento · Melhorias e Restrições (16/10/2026)

Usuário retomou a tarefa. HEAD confirmado3f17952, feito pelo usuário; árvore estava limpa. As aprovações anteriores continuam válidas, sem perguntas novas. Implementação LOCAL em ficha-v01/custom_pecas.py:789Melhorias +395Restrições, bases opcionais, catálogos unidos, identidade herdada nas contas de feitiços/invocações e Classe0. ANALISE9 local proposta,18948chaves; contratos anteriores devem ficar nos mesmos endereços. Gerador exporta --exportar-pecas. Arquivos .gs desta etapa AINDA NÃO regenerados nem enviados ao Google.

Nativo continua integralmente na etapa Famílias/ANALISE8: apenas metadados e sentinelas foram lidos nesta retomada. Oficial intacta. Não executar construir() na revisão. Copia descartável autorizada permanece a mesma.

Infraestrutura: compactação de notas repetidas em emitir_gs.py/modelo.gs.js; preserva exceções, inclusive nota vazia, e precisa suportar complementos em qualquer ordem. conferir-copias.py passou nas15abas atuais mais2fixtures antes de acrescentar o último teste explícito de ordem dos complementos; repetir esse teste com a versão final. Novo regressao-pecas.py em execução focal local, sem resultado concluído ainda. Fonte/exportação principal em ../evidencias-3b/pecas-modelo.json; baseline anterior em pecas-modelo-anterior.json. Não declarar Melhoria/Restrição prontas antes de testar, regenerar, medir arquivos e conferir visual/mecânica no Sheets. Formas e demais moldes da3c ainda pendentes.

Próximo: concluir regressão focal e corrigir falhas; geração integral serial sob os limites já determinados; ajustar divisão de arquivos para<=900000bytes, conferir carregamento/roundtrip/construção simulada; migração nativa pontual com backup e restauração dos testes; salvar fontes no projeto e reler. Capacidade/custo gerais da3c só fecham após os demais catálogos e medição nativa na descartável. Nenhum commit/push pelo agente. Não preparar um commit misturando fonte nova e .gs antigos.

---

## Encerramento antes de desligar — Famílias 3c (15/10/2026)

Etapa de Famílias implementada na cópia nativa de revisão e nos geradores. Não declarar a parte3c inteira concluída. Usuário avisou às23:54 que desligará à meia-noite; nenhum novo bloco foi iniciado após esse aviso.

**Aprovações recebidas:** todos os moldes restantes do ESTUDO3C estão aprovados; aptidão/Bênção pode consumir escolha ou ser explicitamente gratuita; tipo de entidade do zero pode combinar vida, talismã e reserva dePE separadamente. Autonomia e alma continuam por invocação. Não perguntar novamente.

**Entregue nesta etapa:**318registros de Família em CONFIGURAÇÃO, linhas1805–4029; limites da técnica emB153:G164, Livres/Fechadas editáveis e Neutras por saldo. DADOS_CRIACAO oculta;108menus de entidade unidos ao catálogo. Estados da técnica não concedem Livre à entidade. ANALISE formato8:9082chaves (7485anteriores +1597), leitor atualizado e esquema documentado em ../ESQUEMA-ANALISE.md. Bot e oficial intactos.

**Testes:**31checagens focais passaram;8cenários mecânicos nativos,18entradas restauradas e relidas;318checkboxes +318menus de estado +108menus de Família auditados;3843mesclagens verificadas. A bateria simulada conserva175checagens em3fases: principal162, acabamento6, continuação7. A principal foi repetida após a correção de altura, com retorno0 do subprocesso registrado em criacao-familias-principal-exit.json. O invólucro da sessão chegou a informar143 mesmo após esse retorno0; não apresentar o comando agregado interrompido como execução0. Logs e resultado consolidado estão em ../evidencias-3b/criacao-familias-construir-*.

**Correção visual confirmada no Sheets:** textos de2303/3423caracteres crescem; limpar primeiro/último cartão devolve exatamente25px por linha, preservando o desenho. Grupo de autoaltura declara minima=25; demais grupos mantêm o comportamento anterior. Três descrições de teste vazias e dimensões restauradas. ANALISE inteira relida após o teste:9082chaves, zero diferenças nas quatro colunas, zero erros. Corrigidas24notas nativas antigas de sete para nove vagas (fonte já dizia nove). Carteira/foto/seletor de paleta, grupo7, nove vagas de invocação e respiro da Definição conferidos visualmente.

**Código salvo no Google:** oito arquivos da integração foram relidos integralmente após recarregar, iguais aos locais, inclusive a última correção de altura. Prova criacao-familias-scripts-salvos.json. Projeto tem16arquivos,7243296bytes ao todo, maior Configuracao.gs888244bytes. Esses números NÃO fecham custo/capacidade gerais da3c. Leitor --teste terminou0; aviso de escolhas de perícia da ficha vazia é esperado. Nenhuma construção nativa integral foi executada nesta etapa. Não executar construir() na revisão nem na oficial; a descartável autorizada é12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc.

**Retomada exata:** começar integração dos catálogos aprovados de Forma/Melhoria/Restrição; depois aptidão/Bênção, Talentos, tipo de entidade, condição e dano. Ver inventário em ../evidencias-3b/inventario-3c-atual/ e roteiro TESTE-CUSTOM-3C.md. Preservar bases opcionais e automações publicadas. Depois medir capacidade/tamanho/tempo na descartável e só então reunir/limpar a interface. As abas ESTUDO são temporárias; não removê-las enquanto houver dependências ou integração pendente.

**Navegadores:** IAB4 contém a revisão; IAB7 foi usado para salvar o código, que já está persistido. Brave caiu duas vezes durante colagem grande, inclusive após reconectar; não pedir nova autorização Google nem reconexões repetidas sem necessidade concreta. Usar o código local como referência e conferir antes de sobrescrever alterações externas.

Nenhum commit/push pelo agente. Alterações desta etapa preparadas com git add e mensagem em mensagem-de-commit.txt; usuário decide quando executar o commit. Não iniciar Formas hoje por causa do desligamento.

---

## Parte 3c em implementação · decisões recebidas (15/10/2026)

Usuário aprovou os moldes restantes do ESTUDO 3C (linhas178–258), aptidão/Bênção com escolha consumida ou gratuidade explícita, e combinação independente de vida/talismã/reserva de PE para tipos de entidade do zero. Autonomia e alma continuam na própria invocação. Não reabrir essas aprovações. Estudo ampliado para268linhas,391pedidos,24controles e91notas;19preenchimentos testados e restaurados;530células anteriores comparadas sem diferenças. Capturas prototipo-3c-restante-*.png e prova JSON em ../evidencias-3b/.

Código de integração começou por Famílias em ficha-v01/custom_criacao.py:318registros como limite superior de cobertura (210referências de peças da técnica +108aberturas de entidades), estados independentes e limites em CONFIGURAÇÃO B153:G164. Fonte local e leitor passam a formato8, preservando as7485chaves anteriores e acrescentando1597. Nova DADOS_CRIACAO oculta; três .gs Criacao/CriacaoPainel/CriacaoAnalise. Geração inicial completou, maior arquivo893044bytes e soma7221288bytes; NÃO é custo final da3c nem tempo de construir() nativo. Regressão focal em andamento. Encontrada e corrigida qualificação ausente no resumo Q37 antes de aplicar ao Google; a geração integral ainda precisa ser repetida após essa correção.

ATENÇÃO: a revisão nativa ainda só recebeu o protótipo nesta rodada. Catálogo/limites de Famílias, ANALISE8 e scripts novos NÃO foram aplicados nem salvos no projeto do Google. Oficial e bot intactos. Não marcar a3c concluída. Seguir por testes das Famílias, demais catálogos, migração pontual nativa, visual/mecânica e medição final na descartável. Inventário atualizado JSON:1817escolhasdiretas; limite conservador de2036registros em uso ao considerar Famílias318 e danos165 (inclui J12livre e8equipamentos). Esse número não aprova nem obriga criar2036cartões; armazenamento/custo gerais continuam abertos.

---

## Orientação vigente de interface (15/10/2026)

Usuário pediu concluir todas as funções antes de limpar a interface. Edição final reunida em CONFIGURAÇÃO; estudos temporários saem ao final, após validação de independência das fórmulas/menus. Escolhas e resultados permanecem nos espaços originais das fichas. Reduzir informação expositiva e organizar campos de edição no acabamento final; notas contextuais para o que ajuda a configurar, documentação técnica fora da interface. Não apagar nem redesenhar os estudos nesta rodada. Fila mecânica 3c abaixo permanece vigente; desenho aprovado não é aprovação de capacidade/custo ainda não medidos. Detalhes em ESTUDO-CUSTOM-3C.md.

---

## Acabamento do ESTUDO 3C (15/10/2026)

Coluna B ampliada de 70 para 130 px somente no estudo; REGRA passa a 255 px e “Não autônoma · Livres adicionais” cabe em uma linha. AUTONOMIA · EXEMPLO e a nota visível esclarecem que o menu só muda a demonstração; a escolha real continua individual em INVOCAÇÕES. Corrigidas 28 notas antigas de sete para nove caixas. Fontes dos dois protótipos atualizadas. Migração nativa delimitada de 32 pedidos, sem reconstrução: somente dois textos mudaram, dez fórmulas e todas as validações preservadas, zero erros nas faixas lidas. Visual conferido em 100%, texto e bordas completos; captura ../evidencias-3b/estudo3c-largura-corrigida.png. Nenhuma alteração mecânica; não repetir bateria pesada por este acabamento.

Fila vigente: fechar capacidade/armazenamento/custo geral da 3c; integrar Família/Forma/Melhoria/Restrição com desenho já aprovado; apresentar os demais moldes antes de construí-los; depois concluir integração ANALISE e bateria final mecânica/visual, incluindo construção nativa medida na descartável. Bônus, regras de campanha, 3a, 3b e autonomia/nove espaços já implementados na revisão. Bot permanece em outro trabalho. Não reabrir aprovações já recebidas.

---

## Estado vigente · nove Famílias e autonomia concluídas na revisão (15/10/2026)

Este registro substitui o andamento anterior. A revisão nativa 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0 tem nove espaços de Família em cada uma das 12 entidades, AUTONOMIA individual abaixo da aquisição (padrão Autônoma) e uma linha vazia antes de DEFINIÇÃO. A Definição desceu uma linha usando a folga existente; habilidades e as cinco primeiras escolhas não mudaram de endereço. A antiga escolha 7 foi preservada na nova posição; texto, nota e formatação de texto da Definição preservados nas 12 entidades.

CONFIGURAÇÃO B133:G149 contém apenas limites/ganhos: abertas/Livres para padrão, Parceria/Múltiplas e Principal, mais o ganho da Não autônoma. Em branco usa o sistema. Autônoma: 3/1, 4/1 ou 5/2; Não autônoma soma UMA Livre nova ao total aberto e às Livres. Não existe seletor global de autonomia. Exige ordem prévia para ações, exceto Reação. Notas identificam regra do sistema prevista para o Guia de Criação, ainda não abordada no livro de regras atual; não chamar de regra da mesa. ALMA/Integridade não foram alteradas por essa escolha.

Aplicados 44 lotes de migração delimitada, sem reconstrução nem importação de Excel. Backup antes e pré-leitura recente preservados. Auditoria de 4.222 células alteradas (4.024 fórmulas) sem divergências/erros; 7.485 chaves únicas, 108 menus de Família e 108 rótulos conferidos. Cinco cenários nativos passaram: nona Família abre menus; Não autônoma dá o bônus correto e desconto sem mudar a segunda entidade; duplicata; campanha nove com nona Livre; limite incompatível avisa. Rótulos Livre/aberta tinham uma referência sem aba: o visual encontrou e a correção foi testada em modo Não autônoma/restaurada. Entradas anteriores e cenário de teste restaurados, zero diferenças, nenhum teste ativo. Grupos abertos para ver a entidade 12 foram recolhidos novamente.

Código de cinco fontes salvo no projeto vinculado e relido integralmente após recarga: Invocacoes, Configuracao, Analise, AnaliseFontes e ProgressaoAnalise iguais aos locais. Maior .gs 845.461 bytes <900 KiB; soma 6.050.642 bytes. ANALISE agora formato 7; contrato em ../ESQUEMA-ANALISE.md e leitor local atualizado. Bot não alterado.

Testes locais: cenários escalares de perfis, nove vagas, descontos, independência, ganho configurável, vazio=Autônoma e rótulos emitidos passaram; estrutura final passou após a correção; construção simulada completa e 122 paletas passaram; leitor passou. Construção/paleta antecederam só a correção de qualificação dos rótulos, que recebeu teste nativo, teste local e nova estrutura. A última geração de rótulos escreveu os artefatos até Habilidades.gs mas a sessão retornou143; exportação nova independente conferiu os 108 rótulos gerados e a estrutura inteira, e o ZIP local está íntegro. Não foi repetido construir() nativo integral, arnês longo ou bateria de 24 validadores. Não usar a medição antiga 376.821 ms como tempo desta etapa.

Evidências: ../evidencias-3b/autonomia9-*.json/log/png. Capturas autonomia9-entrega.png, autonomia9-nota-guia.png, autonomia9-configuracao.png e autonomia9-invocacao12-100.png. A aba INVOCAÇÕES fica aberta para revisão. Oficial e compartilhamento intactos.

Próximo: continuar a parte 3c. O desenho inicial de Família/Forma/Melhoria/Restrição foi aprovado, assim como o complemento de autonomia com os ajustes do usuário. Capacidade e custo gerais da 3c ainda NÃO foram fechados; inventário agora soma1.817 seleções (Famílias108). Rever dependências do catálogo e apresentar os demais moldes antes da integração. Não reabrir a aprovação já dada. Índice preparado de forma delimitada; git diff --cached --check passou. mensagem-de-commit.txt pronta. Nenhum commit/push pelo agente.

---

## Próxima decisão · ESTUDO 3C apresentado (15/10/2026)

A correção do grupo 7 abaixo está concluída, testes e restauração encerrados. Criada somente ESTUDO 3C (47007), com proposta de limites de Famílias e moldes de Família/Forma/Melhoria/Restrição. Fonte mockup/prototipo_custom_3c.py; descrição e inventário em ESTUDO-CUSTOM-3C.md. Sem integração com contas/ANALISE ou construção de novos blocos de produção.

Proposta pendente: Livres/Fechadas editáveis; Neutras calculadas pelo total livro + custom. Testes do estudo (4/1, excesso, sem família custom) passaram e entradas restauradas; 24 controles, 129 notas, cinco fórmulas sem erro. Visual conferido em 100% e conjunto em 75%; imagens prototipo-3c-familias.png, prototipo-3c-forma-melhoria.png e prototipo-3c-restricao-alcance.png em ../evidencias-3b/.

Capacidade 3c e custo final NÃO fechados: o inventário conta 1.769 seleções, não cartões aprovados. Famílias têm referências pelas peças além dos 60 menus de entidades. Antes de fechar a capacidade, revisar esse vínculo, propor armazenamento e medir tamanho de .gs/tempo nativo na descartável. Outros moldes (aptidões/Bênçãos, Talentos, entidades, condições/danos) ainda precisam ser apresentados. Não implementar regras novas ou integrar a 3c antes do ok exigido pelo prompt.

---

## Estado vigente · correção do grupo 7 concluída (15/10/2026)

Este registro substitui as pendências históricas de conexão, salvamento e cenário ativo abaixo. A cópia de revisão recebeu a correção nativa sem reconstrução e sem importação de Excel. FICHA agora tem 436 linhas: Perícias em 12+11 vagas e Ofícios em 6+5, com a divisória contínua até o fim. Removido o painel duplicado de habilidades. Caminho/Trilha custom preenchem as nove cartas existentes do grupo 7, nos níveis publicados (2/7/15/23/30 e 2/11/19/27). Textos manuais são preservados e a referência fica na nota. CONFIGURAÇÃO permanece Mizuki Escuro fixo. Origens continuam usando seu painel existente.

Seis fontes alteradas foram salvas no projeto vinculado e relidas integralmente, iguais aos arquivos locais: Codigo, Ficha, Configuracao e três Progressao. Maior .gs: 824.900 bytes, abaixo de 900 KiB. ANALISE continua no formato 6, com 7.387 chaves; níveis não aplicáveis exportam vazio e o cache interno CB2:CC10 não é exportado.

Testes nativos: cinco verificações das duas colunas (totais, escolhas, especialização, duplicata cruzada, trocar por zero) e oito verificações das cartas (preenchimento, texto longo completo, riscado de nível futuro, vida/PE, anotação manual e trocas livro/custom) passaram. Seis gatilhos onEdit concluíram entre 9,443 e 15,733 s. Logs das duas trocas chegaram à etapa final sem erros. Restauração de 74 entradas/notas, alturas e releitura integral das faixas: zero diferenças. Nenhum cenário de teste permanece ativo; auditoria final sem erros de fórmula nas áreas alteradas. Capturas finais das tabelas e nove níveis aprovados mostram bordas completas.

Regressão de progressão completa, 74 verificações de delta/cartas, 122 paletas e leitor aprovados. Construção simulada completa passou com código de saída 0, confirmado em correcao-grupo7-construir-exit.json. Não foi repetida a montagem nativa inteira nesta correção: os 376.821 ms registrados abaixo pertencem à integração anterior. Bateria integral de 23 validadores e arnês pessoal longo não repetidos. Limitação FILTER da regressão antiga 3a continua documentada, com contraprova no Sheets.

Evidências em ../evidencias-3b/correcao-grupo7-*.json e logs; capturas correcao-duas-colunas-entrega.png e correcao-niveis-grupo7-entrega.png. Oficial, bot e compartilhamento intactos. HEAD 4e0f6c7, feito pelo usuário. Arquivos desta correção e do estudo adicionados de forma delimitada ao índice; git diff --cached --check passou. mensagem-de-commit.txt preparada. Nenhum commit/push pelo agente.

Próximo: inventário e protótipo da 3c antes de construir. BASE DO LIVRO opcional já aprovada; Famílias novas acrescentadas às nove, com limites preservados. O usuário pediu limites configuráveis; apresentar Livres/Fechadas editáveis e Neutras como saldo para aprovação do desenho. Não há aprovação de um protótipo 3c nem capacidade final medida ainda.

---

## Continuação · teste delegado da 3a e protótipo 3b (15/10/2026)

Usuário autorizou o agente a fazer o teste e seguir a fila. Teste focal na revisão concluído: equipamentos/volumes/Defesa/Proteção/deslocamento, troca por zero, marcante herdada, rota sem energia, ferramenta com volume zero, menor e duplicatas passaram. As 156 entradas temporárias foram restauradas e relidas; 13 abas/17 faixas sem erros de fórmula. Evidência: evidencias-custom/teste-delegado-3a.json. Não repetir montagem nativa nem bateria pesada sem mudança que justifique.

Criada somente a aba ESTUDO 3B (47005), com Caminho/Trilha, textos por nível e molde curto Perícia/Ofício. 29 controles e dois grupos nativos conferidos; troca de tipo por fórmula passou. Fonte do estudo em mockup/prototipo_custom_3b.py. Não há integração 3b/novo formato ANALISE. Detalhes em ESTUDO-CUSTOM-3B.md.

Conta inicial de 36 substituída por 133: Caminho 1 + Trilha 1 + perícias (23 + 12×7 + 1 =108) + ofícios (11+12=23). Total proposto com 3a:158. Inclui as 12 entidades; seletores de Classe não são registros. Capacidade final ainda exige tamanho real dos scripts e tempo nativo, após integrar. Não afirmar que 36 cobrem toda a ficha.

Aguardar resposta à pergunta atual do protótipo antes de código de produção, por exigência explícita do prompt do usuário. Pergunta anterior com 36 está superada. Trabalho autorizado independente: mapear campos particulares das Trilhas e dependências da progressão; não decidir novas regras sem perguntar. Oficial e bot intactos. HEAD encontrado4099df2 (commit anterior feito pelo usuário), sem commit/push pelo agente.

---

## Estado atual · montagem nativa concluída e 3a pronta para teste (15/10/2026)

Após autorização do usuário, construir() terminou na cópia nativa descartável 12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc com “FICHA PRONTA”. Duas execuções iniciais concluídas montaram as primeiras sete abas em 141.988 e 235.950 ms. A instalação individual dos menus estourou seis minutos numa tentativa intermediária. Corrigido CONFIGURAÇÃO para usar validacao_em_matriz, mecanismo já existente: geração09 e regressao-construir04 aprovadas. A retomada final terminou em 289.568 ms; menus em cerca de 67,5 s. Soma do caminho concluído: 667.506 ms (11min7,5s), excluindo o erro transitório inicial e a tentativa com timeout. Não é tempo de uma única execução nem nova montagem integral após a correção; as primeiras sete abas foram reaproveitadas.

Conferência final: 13 abas/17 faixas, nenhum erro de fórmula. CONFIGURAÇÃO tem os 204 menus esperados, 55 checkboxes e 175 seletores estritos, sem divergências de fonte/tipo. DADOS_CUSTOM: 4.904 entradas não vazias iguais ao gerador, hash normalizado a622495473116fb3. ANALISE: 6.174 chaves únicas, hash 31674ef52774dd62. Localidade final pt_BR. Teste preenchido confirmou Defesa 20, Proteção 7, deslocamento 4,5 m, volumes 3 e 2,1; trocar por 0 fixa Defesa em 0. Base Latente invalida marcante própria; Origem do zero permite; rota marcial sem energia mantém 50 Pontos de Esforço. As 121 entradas usadas foram restauradas e relidas: zero diferenças.

Revisão visual: carteira/foto/paleta, cabeçalhos das abas visíveis, recursos/sequelas/defesas, inventário e foto da FICHA PESSOAL, glossário e grades de CONFIGURAÇÃO (bônus, regras, XP, vida e cartões). Sem bordas quebradas nas vistas inspecionadas. CONFIGURAÇÃO permanece Mizuki Escuro fixo, sem congelamento. Capturas e consolidação em evidencias-custom/fechamento-montagem-base-r52.json. Nenhum XLSX foi importado no Google; oficial e revisão preenchida não foram reconstruídas.

Helper temporário removido do projeto da revisão. Código.gs relido após recarregar editor independente: igualdade integral com o local, 252.444 caracteres, sem medirCustomB47. Configuracao.gs atualizado também foi relido integralmente. Nenhuma execução em andamento. A cópia descartável conserva o script antigo copiado da oficial: recebeu a montagem atual por execução do projeto da revisão, servindo como evidência de construção, fórmulas e visual; não como entrega de script vinculado aos jogadores. A revisão preenchida 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0 tem os dez scripts atuais e é o destino do teste manual. Nunca executar construir() nela.

Capacidade 3a: 25 cartões (1 Origem + 1 Marcante + 2 Menores + 8 equipáveis + 1 uniforme + 12 itens). Dez scripts somam 4.762.350 bytes; maior 806.439 bytes, abaixo de 900 KiB. Demais regressões focais anteriores continuam válidas; a bateria integral de 22 validadores e o arnês de 114 mutações não foram repetidos nesta correção de metadado.

Próximo passo: usuário testar 3a pelo TESTE-CONFIGURACAO.md; partes 3b/3c aguardam esse teste conforme prompt. Nenhuma decisão de regra pendente. HEAD encontrado 10ee014, feito anteriormente pelo usuário. Cinco arquivos da correção de menus e documentação preparados no índice, com mensagem-de-commit.txt; nenhum commit/push pelo agente. Antes de integração futura, atualizar referências remotas e comparar origin/main.

---

## Histórico de checkpoints (superado pelo estado acima)

## Teste nativo · correção de tempo em validação (15/10/2026)

Autorização concluída. Teste somente na cópia nativa descartável 12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc. Oficial e revisão preenchida não são destino de construir(). Primeira tentativa teve erro transitório insertSheet; as duas seguintes montaram as sete primeiras abas em 141.988ms e aproximadamente235s, com pausas normais. Quarta montou as seis restantes em221s, mas excedeu seis minutos durante a instalação dos menus. Log construir-nativo-tentativa-04-estouro-menus.log preservado. Auditoria intermediária das13abas/17faixas: zero erros de fórmula; DADOS_CUSTOM4904 entradas e ANALISE6174 chaves coincidiram com o gerador.

Correção pequena: CONFIGURAÇÃO passa a validacao_em_matriz=True; mesmo mecanismo existente das abas maiores, preserva menus estritos e checkboxes. Geração09 e regressao-construir04 aprovadas (tetos3G/duasCPUs, serial). Configuracao.gs salvo e relido de editor independente:560664 caracteres, igualdade integral. Quinta execução iniciada13:50:48, helper medirCustomB47, retomada índice7. Editor CUA17, cópia CUA16. Não remover helper enquanto executa. Faltam término real, conferência dos menus/cálculos e acabamento visual, restauração das entradas temporárias, limpeza do helper e documentação final.

HEAD encontrado10ee014 (commit custom3a já feito pelo usuário; não pelo agente). Alteração nova limitada a custom.py, Configuracao.gs e artefato local regenerado, mais documentação. Nenhum commit/push pelo agente. 3b/3c continuam aguardando teste do usuário.

---

## Teste nativo · aguardando autorização manual no navegador do usuário (15/10/2026)

Cópia nativa da oficial criada: 12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc, “TESTE DESCARTÁVEL — base B47 — construção custom R52”. Construir recria abas; somente essa cópia é destino. Helper temporário medir-construir-base-nativo.gs anexado ao Código.gs do projeto da revisão, salvo e relido integralmente em editor independente CUA15 (254.392 caracteres, igualdade exata local+helper). Chave de estado B47_MEDICAO_CUSTOM_R52_BASE. Guardas impedem revisão/oficial como destino.

Revisar permissões aberto, mas o usuário relatou popup inacessível no app e pediu link para autorizar manualmente no navegador dele. Tentativa cancelada pela interface, confirmado “Execução cancelada”, sem log TESTE e sem início do corpo confirmado. Nenhuma permissão concedida pelo agente. Projeto pronto: https://script.google.com/u/0/home/projects/1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf/edit . Usuário deve selecionar medirCustomB47 e Executar; nunca construir diretamente na revisão. CUA15 e cópia CUA16 mantidas para retomada. Base antes da montagem registrada em evidencias-custom/base-antes-construir-r52.png.

Após autorização, ler logs e medir montagem real; se pausa automática, repetir medirCustomB47 para retomar. Depois conferir mecanicamente e visualmente o resultado em todas as abas, remover helper e reler Código.gs em editor independente. Atualizar tempo/resultado/documentação; nenhum commit/push. O teste completo ainda não aconteceu.

---

## Estado atual · parte 3a pronta para teste do usuário (15/10/2026)

Implementados 25 cartões em CONFIGURAÇÃO J:O para Origem, Marcante, Menor, Arma, Escudo, Uniforme, Item comum e Ferramenta amaldiçoada. Menus fechados para opções fixas; equipamento/item conservam digitação livre. Custom válido alimenta menus e contas. BASE DO LIVRO opcional, quatro rotas e quatro perícias distintas conforme decisões do usuário. MESTRE VIU é registro do jogador; aprovação continua no bot.

Correção R52 aplicada: Origens do livro e bases herdadas mantêm marcantes publicadas, exceto Restrição corporal. Menores e Legados continuam personalizáveis. Origem totalmente homebrew aceita marcante própria, confirmado pelo usuário. Cinco cenários nativos passaram; 34 entradas restauradas e comparadas novamente por leitura independente. Os 224 campos da rodada anterior também foram relidos nesta finalização: todos coincidem com o backup.

Validação: regressão custom03 (custom vazio = IGUAIS; equipamento, volumes, Defesa/Proteção, rotas, entradas inválidas e R52), conferir-ficha02, construir03 em simulador, comparador03, pessoal02, paleta (122 combinações) e leitor aprovados. Auditoria de 13 abas nativas: zero erros de fórmula. ANALISE5 com 6.174 chaves únicas, preservando as 5.274 anteriores. DADOS_CUSTOM: 4.904 valores/fórmulas não vazios idênticos ao gerador (normalizados apenas separadores/aspas), digest eb15a4d5eb678e6e. Bateria integral de 22 validadores e arnês de 114 mutações NÃO repetidos nesta etapa.

Revisão visual nativa: carteira/foto/seletor de paleta, cabeçalhos das abas, capacidades e inventário da FICHA PESSOAL, grades de regras/XP/vida, primeiro cartão e cartões24/25. Sem bordas quebradas nas vistas inspecionadas. CONFIGURAÇÃO mantém Mizuki Escuro fixo e zero linhas congeladas. Evidências em ../evidencias-custom/*r52.png. Não houve importação de XLSX para o Google. Oficial, bot e compartilhamento não foram alterados.

Os dez scripts vinculados foram salvos e comparados integralmente em editor independente. A tentativa de medir construir() NÃO iniciou o corpo da função: Google exigiu autorização, execução cancelada. Nenhuma permissão concedida. O helper temporário foi removido e Código.gs foi relido de uma aba nova: igualdade integral com o arquivo local (252.444 caracteres), evidência limpeza-teste-nativo.json. Editor fechado; não há execução em andamento. Usuário resolveu a janela OAuth. Não repetir a tentativa nem executar construir/continuar sobre a revisão preenchida.

Capacidade: 1 Origem + 1 Marcante + 2 Menores + 8 equipáveis + 1 uniforme + 12 itens = 25. Dez .gs somam 4.762.318 bytes; maior Analise.gs = 806.439 bytes, abaixo de 900 KiB. O tempo REAL de construir() permanece pendente de execução autorizada pelo usuário em planilha descartável. Não confundir o simulador com medição nativa e não fechar capacidade definitiva sem esse dado.

Próximos passos: usuário testar 3a pelo TESTE-CONFIGURACAO.md; resolver a medição nativa antes do fechamento definitivo. 3b/3c aguardam esse teste conforme prompt. Nenhuma decisão de regra pendente. 30 arquivos preparados no índice Git; mensagem-de-commit.txt pronta e ignorada pelo Git. Nenhum commit/push. Evidência consolidada: evidencias-custom/fechamento-para-teste-r52.json. Antes de futura integração, fazer fetch e comparar origin/main. Worktree codex/configuracao-b47, HEAD d0427b6.

---

## Histórico de checkpoints (superado pelo estado acima)

## Estado atual · 3a / correção R52 em andamento

Usuário confirmou: Origens do livro usam marcantes publicadas; exceção Restrição corporal. Origem inteiramente homebrew sem base pode ter marcante própria. Menores e Legados de história continuam personalizáveis. PDF R52 fornecido pelo usuário conferido nas páginas 95 e 99–100; texto extraído em evidencias-custom/r52-texto.txt. Ainda ajustar código/menus/diagnósticos e repetir testes focais.

Migração nativa dos cartões, contas e ANALISE5 aplicada à cópia de revisão. 25 cartões, 6174 chaves. Detectado e corrigido deslocamento de referências futuras: apoio foi reaplicado depois de expandir CONFIGURAÇÃO, preparador corrigido. Testes nativos de equipamento/volume/Defesa/Proteção/rotas passaram. Sem Energia mantém PE como Pontos de Esforço (50 no cenário), não zero. TODOS os 224 campos temporários restaurados nesta retomada; backup em evidencias-custom/restaurar-entradas-nativas.json. Nenhum teste temporário deve ficar na cópia.

Scripts vinculados estão PARCIALMENTE atualizados e exigem conclusão: dez arquivos existem; Pessoal.gs foi encontrado com apenas a função padrão myFunction() numa leitura independente. Não confiar só no clipboard logo após colar; confirmar salvamento em outra aba após recarregar. Custom.gs também precisa auditoria. Codigo/Ficha/Origens foram editados, Analise/AnaliseFontes/Configuracao ainda pendentes. Não executar construir na cópia preenchida. Fontes completas estão no disco e recuperáveis. Abas CUA 9 e 10 são editores criados pelo agente; 3 é Sheets.

Geração07 local e regressao-custom-02, comparador-02, regressao-construir-02 aprovados antes da R52. Correções do conferir-ficha-xlsx ainda aguardam nova rodada. Falta revisão visual de todas as abas, terminar testes novos, medir construir nativo em cópia descartável, atualizar contrato/roteiro/checkpoint e preparar índice/mensagem sem commit/push. 3b/3c aguardam teste do usuário.

---

## Custom · protótipo revisado com listas e bordas (15/10/2026)

Feedback do usuário aplicado na aba ESTUDO CUSTOM, sheetId 2139799909: bordas limpas e refeitas por caixa mesclada, opções fechadas com menus. R51 confirmado em manual.txt:2039 e origens-do-livro.json: quatro opções de perícia para escolher uma; todas as oito entradas do livro têm quatro. Origem agora tem quatro seletores separados.

Opções fechadas: rota (Fundamento/Manejos/Técnica Marcial), base de referência, perícias, ofício, categoria de arma, mãos, dano, propriedades, grau e vínculo a Origem/marcante. Propriedades de arma usam quatro posições separadas, suficientes para todas as armas do catálogo atual (máximo observado: quatro). Rota e base continuam campos de estudo; a associação completa aos efeitos de criação precisa ser tratada na integração, sem inferir tudo pelo nome. O rótulo anterior LIMIAR DE FEITO não representava o campo do dossiê: foi corrigido para TALENTO CE 4, registro textual que o R51 já usa na Restrição corporal.

As sete primeiras posições de cada cartão são opções fechadas e as seis seguintes são valores/texto. Isso permite validação estrita e troca das listas por fórmula, sem script ao escolher o tipo. Campos não usados permanecem vazios. Três cartões agora nas linhas 9, 38 e 67; até a linha 92. Listas auxiliares em colunas ocultas I:CB, na própria aba de estudo.

Conferência nativa: 69 fórmulas sem erros, 21 menus estritos por intervalo; 16 campos fechados preenchidos pertencem às listas permitidas. Troca Arma→Origem mostrou quatro listas de perícias e as três rotas; tipo Arma restaurado. Bordas e três cartões inspecionados; fontes e dados das outras abas não foram alterados. Evidência: verificacao-prototipo-v2.json, pedidos-prototipo-v2.json, moldes-propostos-v2.json e prototipo-v2-*.jpg.

Capacidade mínima continua 25 registros para a 3a. Estimativa sintética atualizada para 26 linhas + 3 de respiro por cartão: 725 linhas e 115382 bytes de envelope. Não é tamanho final do .gs nem tempo real do construir(); a medição completa segue pendente da implementação. O estudo não alimenta contas nem altera ANALISE 4. Integração da parte 3a ainda não iniciada. Sem novo commit/push.

---

## B47 · parte 3a: inventário e protótipo para aprovação (15/10/2026)

A campanha já está registrada no commit d0427b6, encontrado ao retomar; não fui eu que fiz esse commit. Criado inventariar-custom.py, de leitura, sem executar o gerador ou mudar fórmulas. Varredura das 12 abas: 126 validações, 116 fontes distintas e 3.419 caixas com menu. As 12 listas originais da DADOS também foram registradas, inclusive as sem menu direto.

Usuário aprovou Origem-base, marcantes e menores em registros separados e menus nos campos hoje livres conservando digitação avulsa. Capacidade mínima para a parte 3a: 1 Origem + 1 marcante + 2 menores + 8 equipáveis + 1 uniforme + 12 itens = 25 registros. Mãos reutilizam equipáveis; ferramenta ocupa o mesmo inventário. Isso não dimensiona 3b/3c nem alternativas ilimitadas.

Protótipo nativo na aba ESTUDO CUSTOM, sheetId 2139799909, na cópia de revisão. Três cartões (Arma, Menor e Origem), menu de oito tipos, checkbox MESTRE VIU, notas e trinta rótulos por fórmula. Mudança Arma→Escudo→Arma conferida; zero erros após corrigir o separador da localidade. Três visões inspecionadas. Não alimenta a ficha e não altera ANALISE 4. Exemplos são apenas de desenho.

Aguardar aprovação do desenho/campos, conforme o prompt do usuário, antes de implementar a parte 3a. Ainda verificar a política de nomes duplicados e detalhar a base da rota/da ferramenta sem inventar novas regras. Medida sintética: 25 registros/16 campos/20 linhas por registro = 99.084 bytes de envelope, não tamanho final. Tempo real do construir() e custo completo da ANALISE 5 não medidos; medir na implementação antes de fechar a capacidade definitiva. Grupos de linhas não podem esconder bônus/regras do lado esquerdo.

Evidências em ../evidencias-custom/: INVENTARIO-CUSTOM.md, inventario-custom.json, DECISOES-E-INTEGRACAO.md, prototipo-custom.py, pedidos-prototipo.json, verificacao-prototipo.json e imagens prototipo-*.jpg. Oficial, gerador de produção e scripts vinculados não foram alterados nesta rodada. Nenhum novo commit/push.

---

## Estado atual · parte 2 concluída para revisão (15/10/2026)

Regras de campanha construídas após aprovação do levantamento e protótipo. CAMPANHA vazia conserva o livro; zero é explícito. XP começa em zero no nível inicial, vida inicial é fixa e os dados seguintes ficam registrados. Morte permanente foi retirada da interface/contrato a pedido do usuário. Sequelas extras em FICHA!J50:M50 somam às três caixas; descanso curto conserva, longo limpa todas.

CONFIGURAÇÃO sem linhas congeladas (faixa cinza removida a pedido do usuário); mantém bônus B:G/10:40, regras B43:G59, XP B62:G94 e vida B97:G129, em Mizuki Escuro fixo. RESULTADOS removido; J:O reservado ao custom. ANALISE 4 tem 5.274 chaves únicas, preservando as 5.156 anteriores. O bot precisa reconhecer o formato 4 antes da publicação; não foi alterado nesta etapa.

Validação desta etapa: regressão de campanha (13 cenários), comparador IGUAIS com CAMPANHA vazia, conferência da ficha, montagem completa, bônus, paleta (122 combinações) e leitor passaram, um por vez sob teto de 3G/duas CPUs. Logs finais em ../evidencias-campanha/resultados-validacao.json. Falhas intermediárias foram corrigidas e seus logs mantidos. A bateria integral agora com 21 validadores e o arnês de 114 mutações NÃO foram repetidos nesta etapa; a validação anterior continua registrada no histórico.

Cópia nativa atualizada pontualmente, sem XLSX e sem executar construir() sobre ela. Cinco scripts alterados salvos e comparados integralmente. Testes nativos: início 5/custo 700; vida rolada 40; prazo 5 menos três Sequelas = 2; entradas inválidas com erro visível; descanso longo registrou “Sequelas 3 → 0”. Todos os dados de teste restaurados, exemplos de bônus preservados, avisos novos vazios e 5.274 chaves sem erros de fórmula. Grades de regras, XP e vida inspecionadas. Oficial e compartilhamento intactos.

Evidências duráveis: ../evidencias-campanha/testes-nativos-parte2.json, fechamento-parte2.json e imagens *implementad*.jpg. Roteiro atualizado em TESTE-CONFIGURACAO.md. Próxima etapa: inventário completo dos menus para dimensionar os cartões custom, medir custo e apresentar protótipo antes de construir a parte 3a. Nenhum cartão custom construído.

Não executar commit/push. Arquivos preparados no índice e mensagem em mensagem-de-commit.txt, ignorada pelo Git. Antes de integração futura, atualizar e conferir origin/main; não houve integração nesta etapa.

---

## B47 — protótipo de campanha pronto (15/10/2026)

Levantamento aprovado. Decisões: XP zero no nível inicial; vida inicial fixa do Caminho e dados nos níveis seguintes; morte permanente Livro Não, com opção Sim na campanha.

Protótipo somente na aba ESTUDO CAMPANHA da cópia nativa de revisão (sheetId 47003): regras B43:G60; tabela de XP B62:G94; registro de vida B97:G129. 75 fórmulas sem erros; nível inicial 5, custo alternativo, zero, seletor Sim/Não e restauração aprovados. Evidências e imagens em `../evidencias-campanha/`. A ficha e o gerador não recebem novas regras nesta etapa.

Aguardar aprovação do desenho antes da construção, conforme o prompt do usuário. A seguir: regras/cópia EM USO/DADOS_CONFIG, testes de equivalência com CAMPANHA vazia, ANALISE 4. Custo do nível 1 para 2 e ampliação do registro de Sequelas acima de três continuam condicionados a decisão se essas opções forem usadas. Não executar commit/push.

## B47 — parte 2: levantamento pronto para aprovação (15/10/2026)

A parte 1 já está registrada em `f2ea62c` (encontrada assim ao retomar). Nesta etapa foi acrescentado apenas `levantar-regras-campanha.py`: varredura de leitura das fórmulas do artefato interno do gerador, sem importação para Sheets, sem alterar fórmulas ou o contrato ANALISE 3.

Resultado: 38.939 fórmulas lidas; 21.404 contêm literais numéricos; zero falhas de tokenização; 16 parâmetros propostos, associados a 61 células (19 fórmulas e 42 valores/textos). A associação semântica cobre a lista B47; a varredura bruta não declara que todo número é uma regra. O teste distingue número de referência, texto, nome de função e notação científica.

Relatório e evidência completos: `../evidencias-campanha/REGRAS-CAMPANHA.md` e `regras-campanha.json`. Fonte: `manual.txt` e `manual-fonte.json` do R51. Conflito que exige decisão: o plano diz morte permanente Sim; o R51 usa derrota sem morte automática por padrão. Confirmar também a separação dos tetos/treinos e, antes do protótipo, a forma de configurar XP, registrar vida rolada e Sequelas acima de três.

Aguardando aprovação da lista conforme o passo 2 do prompt do usuário. Depois: protótipo em grade → aprovação → construção e testes de equivalência. Nenhum bloco novo foi construído. Nenhum commit/push executado nesta etapa.

# Pendências · o que precisa de decisão antes de construir

## B47 · bônus e mudanças · fechamento de 15/10/2026

A CONFIGURAÇÃO oferece 30 efeitos para 50 caixas da ficha e mantém a paleta fixa Mizuki Escuro. Somar acumula com a conta e o Buff/Debuff existente; trocar por fixa o resultado final, inclusive zero. Duas trocas ligadas da mesma caixa geram conflito. Entradas ligadas inválidas mostram aviso; uma caixa de seleção apagada conta como desligada.

A ANALISE usa o formato 3, com 5.156 chaves: preserva as 4.896 anteriores e acrescenta 180 campos e 80 avisos de efeitos. O transporte usa oito arquivos de Apps Script, incluindo AnaliseFontes.gs e Configuracao.gs. Os comparadores carregam todas as abas e complementos.

A [cópia nativa de revisão](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit) foi feita diretamente da base do servidor. Preserva imagens, moldura da foto, seletor de paleta e proporções. As grades da CONFIGURAÇÃO têm separação vertical. A ficha oficial não foi alterada. O roteiro nativo está em [TESTE-CONFIGURACAO.md](TESTE-CONFIGURACAO.md).

**Validação:** os 20 validadores foram cobertos pela bateria inicial e pelas repetições corrigidas. A rodada inicial aprovou 18; montagem e arnês foram revalidados após implementar cabeçalho congelado no simulador. O arnês detectou 113 defeitos na rodada completa e o defeito restante do Buff/Debuff da vida numa repetição isolada, com base limpa e contra-teste verdes. Esse cenário passou a exigir as três ocorrências da conta-base no envoltório dos efeitos. Os logs conservam as falhas das rodadas anteriores; não houve uma única execução integral verde dos 20 validadores.

Também passaram a regressão de paleta (122 combinações, incluindo a cor fixa da CONFIGURAÇÃO) e o leitor (`TESTE: OK`, formato 3, versão textual `1.0`). No Sheets foram conferidos soma com Buff/Debuff, troca por zero, conflito, entrada inválida, caixa apagada e restauração de fórmulas. As 5.156 chaves são únicas e não apresentaram erros de fórmula.

**Pendências para as próximas partes:**

- Adequar o desenho ao plano aprovado: BÔNUS E MUDANÇAS em B:G, linhas 10–40; REGRAS DE CAMPANHA abaixo, a partir da linha 43; CONTEÚDO CUSTOM em J:O. O painel RESULTADOS atual em I:L ocupa o espaço reservado ao custom e deverá ceder lugar aos cartões no protótipo aprovado.
- Levantar as regras fixas nas fórmulas, conferir os valores no R51 e apresentar a lista antes de construir o bloco de campanha. O teste com CAMPANHA vazia deve preservar as contas atuais.
- Inventariar os menus antes de definir a quantidade de cartões custom e medir tamanho e tempo de montagem. Caminho usa grupo de níveis 6–20. Cada bloco novo exige protótipo na grade e aprovação.
- Integrar o formato 3 ao bot antes de publicar esta versão para os jogadores. Regras e custom serão formatos posteriores; o bot é tratado em outro projeto.

---

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

> **⚠ Na sua mão:** *colar o `Codigo.gs` novo no projeto do Apps Script, rodar o `construir()` do `Ficha.gs` novo numa planilha nova, trocar a `A1` da central para `0.246`, e conferir no Sheets que o menu do refino escolhido vira número.* **Vai ter campo na Ficha Pessoal, e fica registrado** *(aba de itens e equipamentos, bio, foto e afins):* *a `Couraça` (+1 de Defesa vestindo uniforme) e a arma sem o requisito de Força, que tira a Destreza da Defesa.* **Fechado em 01/10/2026, no B26:** *a Ficha Pessoal existe. A `Couraça` saiu do livro na v0.270 do sistema, e o campo dela não entra, por decisão do Mizuki. A arma sem o requisito de Força ganhou a marca dela na aba, com a punição que ele decidiu no mesmo dia (desvantagem ao atacar com ela), que ainda não está no livro.*


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

**25/09/2026 — numa cópia da ficha a cor não trocava; na original, trocava.** Achado do Mizuki, com a
original e a cópia exportadas (as duas `.xlsx` saíram iguais, célula a célula: o defeito era do script).
"Arquivo › Fazer uma cópia" leva o `Codigo.gs`, mas **não leva gatilho instalável** — ele é de quem o criou —, e o
`onOpen` da cópia, sem autorização, não consegue criar outro. A primeira saída (um menu "Ativar a troca de paleta",
uma vez por cópia) ele recusou: *"queria q só de copiar já funcionasse"*. O código antigo dele fazia tudo no
`onEdit` simples e cabia nos 30 s porque só mexia em fundo e fonte; o nosso também repinta a arte e a régua.

*O esquema:* a troca voltou pro gatilho simples, em passos (a cor de cada aba visível, a régua de cada aba, e cada
imagem da arte por último — 16). Antes de cada passo o `convergirPaleta_` confere se ele cabe no orçamento de 25 s
pelo tempo que o mesmo passo levou da última vez (medido e guardado na planilha), e cada passo termina com
`SpreadsheetApp.flush()`, senão o Sheets só executa a escrita na leitura seguinte e o tempo cai no passo errado. O
que não cabe continua no próximo clique (`onSelectionChange`, também gatilho simples). Nada pede autorização. O
gatilho instalável velho da original se apaga sozinho na primeira troca.

*As medidas dele (12:17 e 12:18):* a troca inteira somava ~32 s em duas execuções — cores 15 a 18 s, régua 7 s,
arte 7 a 9 s; o JS, medido no node, ~100 ms por aba: o tempo é todo do Sheets. *"exigir isso do usuario é meio
chato"*. O primeiro corte que ele aprovou — **as cores partirem da ficha de fábrica, sem ler a planilha** — foi
medido (versões d e e, 12:55 a 13:06) e **ficou mais lento**: a FICHA foi de 4,8 s para 7,6 a 9,0 s, e medindo por
dentro, ler custa pouco e o que pesa é **gravar**, ~0,5 ms por célula em cada gravação (a FICHA grava o fundo em 3,6 s
e a fonte em 3,9 s). Desfeito: a troca voltou a ler, e **a cor pintada à mão pelo jogador volta a ficar**. Antes de
desfazer, a versão de fábrica foi conferida contra o `repintarPaleta_` antigo nos 122 temas (igual) e contra o
`Kaori.xlsx` dele (fundo igual em toda célula; fonte em 12 de ~20 mil, que eram caminho do antigo).

*O que ficou (versão f), pelo pedido dele* — *"ele so troca as cores e as bordas, menos com as imagens, e ai ele
finaliza; as imagens ele dá start dnv caso alguém mexa na ficha"*:

- a troca vai **aba por aba, cor e régua juntas**, começando pela que o jogador está olhando (a CARTEIRA, onde a
  caixa mora), depois a FICHA; a arte vai por último. Com os tempos dele, cor e régua de todas somam 22 a 25 s,
  colado no orçamento: o que sobrar é de uma aba que ele não está vendo;
- **nenhum aviso**: o que sobra termina na próxima vez que alguém mexer na ficha — clique ou edição —, e **a aba em
  que ele clica passa na frente**, então abrir uma aba atrasada a pinta primeiro;
- passo ainda não medido (a primeira troca de uma cópia) usa uma estimativa pelos tempos dele, e não mais 6 s fixos;
- a caixinha diz "O tema leva uns 20 segundos. O que faltar termina enquanto você usa a ficha.", e o
  `verTemposDaPaleta` mostra cada passo de cor por dentro (lê, conta, grava fundo, grava fonte).

*Conferido:* o `regressao-paleta.js`, com o custo calibrado pelos tempos dele, prevê a troca fazendo cor e régua
das cinco abas numa execução de ~25 s e a arte no clique seguinte; com o Sheets 40% mais lento, sobram a INVOCAÇÃO e
o CATÁLOGO, e clicar numa delas a pinta primeiro; três vezes mais lento, nenhuma execução passa de 30 s, e nunca
aparece aviso.

*Medido no Sheets (versão f, 13:25 e 13:27) — "funcionou":* cor e régua das cinco abas na execução da troca, 24,7 s
e 22,9 s (cores 18,4 e 17,8 s, régua 6,3 e 5,1 s); a arte, 7,6 e 7,0 s, no clique seguinte, sem aviso. O "do começo
ao fim" do relatório (46 e 58 s) conta a espera até o clique. Ele viu as cópias mais lentas, mas funcionando. **Fica
colado no orçamento de 25 s:** num dia lento, a última aba (o GLOSSÁRIO) passa pro clique seguinte, calada. Se um dia
precisar de folga, o corte é gravar menos célula (hoje a fonte é gravada na aba inteira, e só a célula com texto
precisa).

### B26 · A Ficha Pessoal — **FEITA em 01/10/2026, e montada no Sheets pelo Mizuki no mesmo dia; o retorno dele é o B27**

*Pedido do Mizuki em 30/09/2026: a aba de pertences e histórico do personagem. O desenho foi fechado com ele por
estudo, em dezoito rodadas, antes de qualquer linha de gerador (`mockup/ficha-pessoal-estudo.html`).*

**A aba `FICHA PESSOAL` nasce no gerador, entre a `FICHA` e a `DADOS`.** *Como o `GLOSSÁRIO`, ela não tem planilha
viva por trás: é o `ficha-v01/ficha_pessoal.py` (a limpeza 22). São 87 linhas e 72 colunas: a folha vai de `A` a `AU`, com a largura de coluna, o cabeçalho e a lombada da `FICHA`, e
o painel de XP vem depois, com cada coluna na largura do que guarda. Toda linha tem a mesma altura, e o título de
cada seção ocupa duas linhas mescladas.*

- **Dossiê:** *foto (12 colunas por 19 linhas, mais alta que larga), `Nome` (espelho da `CARTEIRA`), `Grau` (menu das
  cinco patentes), idade, altura, olhos, cabelo, pele, gênero, aparência, história, personalidade, laços e anotações.*
- **Em uso:** *`Mão principal` e `Mão secundária` (menus com o `Soco` e o que está nos equipáveis guardados; arma de
  duas mãos ocupa a secundária, e arma `Versátil` abre a opção das duas mãos, com o dado um passo acima) e `Vestindo`
  (menu que só lista o que o Grau libera). Embaixo de cada um, a linha de detalhe e as marcas de treino, de Força, de
  Grau e do Selo de gesto.*
- **Treino em armas:** *as 52 armas em 13 categorias, uma caixa de seleção por arma e uma por grupo, num grupo de
  linhas que fecha.*
- **Fileira:** *carga contra `5 + Força`, ienes, salário do Grau, requisito de Força e situação do Traje.*
- **Equipáveis guardados** *(seis linhas com menu, duas livres) e* **itens guardados** *(doze linhas).*
- **Painel de missões e XP,** *depois da coluna `AU`, num grupo de colunas que nasce fechado: duas tabelas de 50
  missões (tipo, adicional, desconto e total), o XP total, o que falta para o próximo nível e a tabela de níveis.*
- **Extensão do painel,** *num segundo grupo de colunas, dentro do primeiro, também fechado: mais duas tabelas de
  50 missões, do mesmo tamanho. O XP total soma as quatro (200 linhas). Pedido dele: "já vi mt player lotando essas
  tabelas".*

**Três caixas da `FICHA` mudaram.** *O `EQUIPAMENTO` deixou de ser menu e espelha o que está vestido e o escudo da mão
secundária, montando o mesmo nome que a tabela de equipamento da `DADOS` usa: a Defesa não mudou de conta. O `XP` mostra
a soma das missões do painel. O `DESLOCAMENTO` cai pela metade com uniforme ou escudo sem a Força, ou com a carga
acima do limite.* **A ficha nasce vestindo o `Traje 1`, que é o do kit inicial:** *antes o `EQUIPAMENTO` nascia
vazio. Até o refino 2 a Defesa é a mesma; do refino 3 em diante o cobrir-se protege mais que o `Traje 1`, e quem
quiser ele escolhe `Sem uniforme`.*

**O catálogo ganhou quatro chaves.** *`equipamento` (as 52 armas, as listas de treino, as faixas de projétil, a
munição, o soco, o Volume, as situações do Traje e o Grau mínimo do Revestimento), `patentes` (o salário) e `missoes`
(os tamanhos e o desconto da semana) saem do livro da v0.330, e o `conferir-catalogo.py` relê cada tabela do
`manual.txt` desta pasta, que é o da v0.263: bate tudo, coluna a coluna. A única regra em que o livro de hoje está à
frente do `manual.txt` é a soma dos itens leves, que não arredonda mais (v0.327); a ficha segue o livro de hoje, e o
validador imprime a diferença. A quarta chave, `fora_do_livro`, guarda o que ele decidiu em 01/10 e o livro ainda não
tem.*

**Regras que o Mizuki decidiu em 01/10/2026 e que ainda não estão no livro** *(a ficha já segue estas)*:

| regra | o que ele decidiu |
|---|---|
| arma sem o requisito de Força | desvantagem ao atacar com ela |
| uniforme ou escudo sem o requisito de Força | veste, com deslocamento pela metade e desvantagem em TR Físico |
| carga acima do limite | a mesma punição, sem acumular |
| missão solo | `Solo simples` 75 XP e `Solo complexa` 150 XP |
| XP adicional | multiplicador: 1,25x, 1,50x ou 2x |
| arredondamento do XP | múltiplo de 12,5, para baixo; quem dá 12,5 exato ainda paga, e menos que isso não paga |
| situação do Traje | *fica para revisão dele; a nota da caixa repete o texto de hoje* |

**O que o `Codigo.gs` faz pela aba, tudo em gatilho simples:** *a caixa do grupo marca e desmarca o grupo inteiro, e a
da arma acerta a do grupo; escolher o Caminho marca o treino dele; anotar missão sobe o nível da `FICHA`; apagar o
`Vol.` de um item traz a conta de volta; e três notas mudam com a ficha (o requisito de Força, a carga e a situação
do Traje).*

> **Quatro escolhas minhas que ele ainda não comentou, e que são fáceis de trocar:**
> 1. *o XP só sobe o nível, nunca desce: quem começou a campanha acima do nível 2, ou sobe na mão, não perde o nível
>    por anotar uma missão;*
> 2. *o XP para de subir o nível no 20, que é o limiar do feito do livro; quem já passou dele sobe normalmente;*
> 3. *desmarcar a caixa do grupo desmarca o grupo inteiro, e ela só aparece marcada com o grupo inteiro;*
> 4. *o desconto do menu é metade a cada missão (50%, 25%, 12,5%, 6,25%), e o livro escreve 12% e 6%.*

> **⚠ A troca de paleta ficou mais pesada.** *A aba tem 6.264 células (a `FICHA` tem 7.050). Cor e régua de todas as
> abas deixaram de caber numa execução: a troca pinta a `CARTEIRA`, a `FICHA`, a `FICHA PESSOAL` e o `GLOSSÁRIO`, e o
> resto termina no clique seguinte, sem aviso, como a arte já terminava. O `regressao-paleta.js` passou a cobrar isso,
> e a estimativa do passo de régua passou a contar as faixas da aba.*
> *A primeira versão da aba tinha 90 colunas e 7.380 células, com o painel na grade de 28 px e cada célula de missão
> mesclada; o painel passou a ter colunas de largura própria, e a aba perdeu um terço das células e 481 mesclagens. Depois vieram as
> duas linhas do título e a extensão, e ela foi a 87 linhas por 72 colunas.*

**Toda linha da aba tem a mesma altura.** *A primeira versão dava 27 px às linhas de título de seção. Como a linha é da planilha inteira, duas linhas da lista de missões e uma da tabela de níveis saíam mais gordas que as vizinhas, e o Mizuki pediu para tirar ("dá certa agonia, a galera vai reclamar"). Em uma linha comum o título ficava pequeno, e ele pediu o equivalente a duas: o título de seção ocupa duas linhas mescladas, em Oswald 14. O `regressao-pessoal.js` cobra as duas coisas: nenhuma linha do corpo foge da altura padrão, e todo título ocupa duas linhas.*

**Como foi conferido.** *O `regressao-ficha-pessoal.py` preenche doze casos na ficha gerada, manda o LibreOffice
recalcular e compara com a regra montada do catálogo: as caixas da aba, a Defesa da `FICHA` pelo espelho, os menus que
mudam, as 144 combinações de tipo, adicional e desconto, e o que falta para o próximo nível. O `regressao-pessoal.js`
roda o script num Sheets de mentira montado do `ABAS`. O `regressao-construir.js` roda o `construir()` inteiro num
Sheets de mentira rigoroso (método que o Apps Script não tem, faixa fora da aba, matriz de tamanho errado e mesclagem
cruzada estouram), confere o que ficou montado e usa a planilha pelo `onEdit`. O `arnes-pessoal.py` planta trinta e um
defeitos numa cópia e confere que cada um acende a checagem dele. O `medidas/ver-aba.py` desenha a aba a partir do `ABAS`, com os valores
recalculados, para olhar e comparar com o estudo.* **Os vinte validadores passam.**

> **O que só o Sheets diz, e falta ele testar:** *os dois grupos (o de linhas do treino e o de colunas do painel, que
> nasce fechado), no computador e no celular; se os grupos sobrevivem à cópia da planilha; as caixas de seleção nos
> títulos dos grupos; os menus que leem coluna com célula vazia; a cor de aviso; o formato do iene; os dois grupos de colunas, um dentro do outro; o tempo do
> `construir()`, que ganhou 340 mesclagens (as fórmulas, que passaram de 280 para 801, agora vão em 143 lotes, e
> não mais uma a uma); e o tempo real da troca de paleta.*

### B27 · O cabeçalho do estudo, o título no acento, a barra do tema e a revisão das 122 paletas — **FEITO em 01/10/2026, e falta testar no Sheets**

*O Mizuki montou a ficha com a Ficha Pessoal no Sheets, trocou de tema e mandou sete pontos. A troca de cor
funciona; o que ele apontou é desenho e cor.*

| o que ele apontou | o que mudou |
|---|---|
| o topo da Ficha Pessoal ficou pior que o do estudo | o cabeçalho voltou ao molde do estudo: a marca 呪術, o título e uma linha de apoio à esquerda; o nome e, embaixo, o Caminho, a Trilha e o nível à direita |
| a `FICHA` devia ter o mesmo cabeçalho, como a `CARTEIRA` tem o dela | a `FICHA` ganhou o mesmo molde, com o título `FICHA DE REGISTRO`; a Ficha Pessoal copia dela e troca o título e a linha de apoio |
| a faixa de título de seção devia se destacar, como no `GLOSSÁRIO` e no `CATÁLOGO` | a faixa da Ficha Pessoal usava o painel alto, o mesmo do rótulo; passou a usar o acento, que é o papel das faixas daquelas duas abas |
| as barras não acompanham a paleta, inclusive a da carga | a barra cheia deixou de ser o osso escrito na fórmula e passou a ser uma cor do tema |
| imagem e fonte em cor "nada a ver" (o roxo do `Alfazema · Claro`); revisar as 122 | duas regras novas na derivação das paletas e três no `Codigo.gs`, e as 122 foram olhadas uma a uma |
| o aviso "Pense bem!" ao clicar no `+` do painel de XP | as fórmulas que moram em coluna ou linha de grupo ficaram sem trava |
| o cabeçalho devia acompanhar o painel aberto | a faixa de tinta e a divisória de baixo dela vão até a última coluna da aba |

**O cabeçalho é a limpeza 23, o `ficha-v01/cabecalho.py`.** *Roda logo depois do desenho da mesa e antes do índice,
porque o nome da personagem muda de célula (de `D3` para `AB2`) e o índice da `DADOS` publica o endereço dele; o número
da `CARTEIRA`, que lia `FICHA!D3`, passa a ler o lugar novo. O carimbo de versão continua, na linha de apoio da
`FICHA` ("Projeto M · v0.258 · em dia"). A palavra `CATÁLOGO` saiu do cabeçalho: para o Mizuki, catálogo é a aba da
invocação. A linha 3 perdeu a altura maior que tinha para o nome grande, e as cinco linhas ficaram iguais.*

**A barra cheia mora numa célula da `DADOS`.** *As três barras da `FICHA` (vida, energia e integridade) e as duas da
Ficha Pessoal (carga e XP) leem a conta `cor da barra cheia`, que nasce no osso de fábrica. A troca de tema ganhou um
passo, o primeiro, que grava ali a `barra` do tema; nenhuma fórmula é reescrita. O âmbar e o vermelho de vida baixa
continuam fixos, pela decisão A5.* **A barra do tema é viva onde pode e neutra onde não pode.** *Mostrei ao Mizuki três
opções (neutra, viva e cor do texto) e ele respondeu: "porque não mescla? deixa a melhor opção a depender da paleta
mesmo". A regra do `derivar.py`: a barra é a primeira cor viva do tema (a tinta de enfeite, depois a régua, depois o
acento, cada uma acertada para ler 3,0 sobre o painel) que não é parente do âmbar nem do vermelho, medido no círculo
de matiz do OKLCH (mais de 35 graus do vermelho e mais de 30 do âmbar, com croma de 0,08 para cima). Quando as três
são da família do âmbar ou do vermelho, ela é neutra: o matiz da régua com pouca croma, clara nos temas escuros, como
o osso era, e de tom médio nos claros.* **Das 122, 68 saem vivas e 54 neutras.** *Viva: o azul do Meia-Noite, o turquesa
do Recife, o verde do Carnaval, e no Alfazema claro, que é todo dourado, o azul do acento. Neutra: o Brasa, o Rubi, o
Kitsune, o Mizuki claro.*

**A revisão das cores, com a medida que a puxou.** *Rodei a troca de verdade (o `convergirPaleta_` do `Codigo.gs`) nas
122, num Sheets de mentira, e olhei o resultado tema por tema (`medidas/pintar-paletas.js` e `medidas/ver-paletas.py`).
O `bloco` e a `linha` são a tinta de enfeite: só pintam a pincelada, a moldura da foto e as letras de enfeite (o
呪術廻戦, o número da carteira, a lombada), e nenhuma célula os usa de fundo. Eles saíam da segunda cor do meio da
paleta, no matiz que ela tivesse, e dois defeitos apareceram:*

1. **Cor fraca entrando como terceira cor.** *No `Alfazema · Claro` a ficha é amarela, a borda é dourada, o acento é
   azul e a tinta de enfeite saía num roxo acinzentado. Regra nova no `derivar.py`: se a tinta de enfeite tem pouca
   croma (abaixo de 0,10, medida em OKLCH) e o matiz dela não é parente nem da régua nem do acento (mais de 40 graus dos
   dois), ela vira um tom da própria régua. Pega 12 das 122: Alfazema (as duas), Sálvia (as duas), Ardósia claro, Terra
   claro, Céu de Verão (as duas), Tengu escuro, Tanuki (as duas) e Momotaro escuro. Quando a cor tem força (o verde do
   Carnaval, o turquesa do Recife, o magenta do Neon), ela fica.*
2. **A rede de legibilidade trocando de matiz ao acaso.** *Quando uma letra ou uma imagem não lia sobre o fundo, o
   `Codigo.gs` a trocava pela cor da paleta de contraste mais parecido, qualquer que fosse. Medido nas 122, em quatro
   abas: a lombada era trocada em 585 células (350 por uma cor da variante oposta do tema, 160 pelo acento, 75 pelo
   bloco), a marca e o número em 152, e o selo caía no bloco em três temas e numa cor da variante oposta em seis.
   Regra nova, "ajusta o valor, não troca de cor": o `bloco` e a `linha` já saem do `derivar.py` lendo 3,5 e 3,0
   sobre a tinta, o fundo e o papel, no mesmo matiz, mais escuros ou mais claros; a rede só oferece cor de texto; a
   letra de enfeite é achada pelo endereço no `ABAS`, e não pela cor que tem (antes, bastava a rede trocar a lombada
   pelo acento uma vez para ela ser "acento" em toda troca seguinte); e a imagem que não aparece vai para o acento do
   tema e, se nem ele aparecer, para a cor dela no mesmo matiz. Nas 122: 673 imagens na cor do papel delas, 59 no
   acento, nenhuma no terceiro caso.*

*Fora o `bloco`, a `linha` e a `barra`, nenhum papel de nenhuma paleta mudou de hex: fundo, painéis, régua, acento e
texto são os que ele já aprovou. O `PALETAS` do `Codigo.gs` deixou de ser colado à mão: o `derivar.py --aplicar` o
reescreve, e o `conferir-ficha-xlsx.py` confere que os dois são iguais.*

**Como foi conferido.** *O `regressao-paleta.js` ganhou nove checagens com referência que não depende do `Codigo.gs`:
a barra gravada na célula certa com a cor do tema, as letras de enfeite no papel delas depois de uma e de duas
trocas, a lombada que uma troca antiga deixou "acento" voltando para a linha, cada imagem das 122 na cor que a regra
manda, e o `bloco`, a `linha` e a `barra` lendo sobre os fundos onde moram. O `arnes-paleta.py`, novo, planta sete
defeitos numa cópia e confere que cada um acende a checagem dele (roda à mão: são oito rodadas, uns dois minutos). O
`conferir-ficha-xlsx.py` ganhou quinze checagens (o cabeçalho das duas abas, o carimbo, a faixa no acento, as cinco
barras, a rede só com cor de texto, o `PALETAS` igual ao derivado). O `comparar-ficha-01.py` cobra a limpeza 23 célula
a célula. O `regressao-pessoal.js` cobra que nenhuma faixa travada encoste em grupo, e o `arnes-pessoal.py` ganhou a
perturbação dela (são 31).* **Os vinte validadores passam.**

> **Duas coisas que eu não mexi, para ele decidir:**
> 1. **o título de seção da `FICHA`.** *Ela tem a caixa do número no acento e a faixa do título no painel alto, que é
>    o desenho dele. Não mexi. Passar a faixa para o acento, como na Ficha Pessoal, é uma limpeza pequena.*
> 2. **a régua de alguns temas é mais forte do que a paleta de origem.** *A derivação mede saturação em HLS, que engana
>    no claro: um quase branco como `FFF5F5` (Blush) tem saturação 1,0 lá, e a régua sai vermelho vivo `CC0000`. É por
>    isso que o `Alfazema · Claro` é uma ficha amarela de borda dourada. Ele disse que a maioria está boa, então não
>    toquei em fundo, painel nem régua; se quiser, é outra rodada.*

> **O que só o Sheets diz, e falta ele testar:** *a `SPARKLINE` lendo a cor de uma célula (a conta é a mesma, mas só o
> Sheets desenha a barra); abrir e fechar o painel de XP sem o aviso da trava; o cabeçalho novo no computador e no
> celular; e o tempo da troca, que ganhou um passo curto. Ficha montada antes desta data não tem a célula da barra: a
> troca de tema pula o passo e a barra fica no osso, como estava. Para ganhar tudo, é rodar o `construir()` de novo.*

### B28 · O `construir()` estourou os seis minutos — **REFEITO em 01/10/2026, e medido por ele no Sheets: 220 s com cinco abas**

*Achado do Mizuki em 01/10/2026, com o registro do editor: `Execução iniciada` às 15:08:19 e `Exceeded maximum execution
time` às 15:14:19. O registro não dizia em que etapa a montagem estava, porque o `construir()` só escrevia no fim.*

**Duas decisões dele:** *"Pode tirar o catalogo e invocação, isso vai ganhar tempo e reduzir o codigo, depois implementamos
dnv diferente com a att"* e *"Busque otimzar o codigo e o teste se possivel, para ver se os resultados se mantiveram"*.

**1. A `INVOCAÇÃO`, o `CATÁLOGO` e a `DADOS_INV` saíram da ficha.** *É a limpeza 24, `ficha-v01/sem_invocacao.py`: as três
continuam no `layout.json`, que é a cópia da planilha viva, e saem da ficha gerada, por último (o `GLOSSÁRIO` nasce na
posição da `INVOCAÇÃO` e usa os estilos do `CATÁLOGO`). A montagem para se alguma aba que fica citar uma delas; nenhuma
cita. A ficha de invocação separada (`ficha-invocacao/`, o `invocacao.json` e os três validadores dela) não foi tocada. A
decisão está no `decisoes-ficha.json`, em `C6_documento.abas_removidas_em_01_10`.*

**2. O `construir()` vai menos vezes ao servidor, e a planilha que ele deixa é a mesma.** *O que pesa no Apps Script é a ida
ao servidor, e a montagem fazia isso célula a célula em quatro lugares:*

| o que era | o que ficou | chamadas, nas cinco abas |
|---|---|---|
| uma chamada de `merge()` por mesclagem | a mesclagem de uma linha que se repete nas linhas de baixo vai numa chamada de `mergeAcross()` | 897 → 310 |
| as fórmulas numa fila, gravadas depois das abas | todas as abas nascem primeiro, vazias e do tamanho certo, e a fórmula vai na mesma gravação dos valores | 112 → 0 |
| uma trava por célula de fórmula, três idas ao servidor cada | uma trava por faixa de fórmulas vizinhas; as células travadas são as mesmas | 333 → 228 |
| a nota de regra lia a mesclagem, a fórmula e o valor da célula de cima, nota por nota | a aba é lida uma vez, e as notas voltam numa gravação | 256 → 16 |
| cada aba era movida para o lugar | elas já nascem na ordem | 11 → 1 |

*A ficha de oito abas fazia 1.195 chamadas de mesclagem e 111 travas; a de cinco faz 310 e 76.* **Isto é contagem de chamada, e não tempo:** *o Apps Script não roda fora do Google, e eu não sei quanto cada
etapa levava. Por isso o registro mudou:* **cada etapa vai para o registro na hora, com o tempo dela.** *Se a execução
expirar de novo, o registro diz onde.*

**3. O acabamento pode rodar sozinho.** *A cor de estado, as notas, as travas e a caixa da paleta viraram a função
`acabamento_`, que o `construir()` chama no fim. Se a montagem das abas passar de quatro minutos e meio, ele para ali,
deixa a planilha em português e escreve `FALTA O ACABAMENTO: rode a função acabar()`. O `acabar()` roda quantas vezes
precisar sem duplicar trava nem nota.*

**4. Os dois arquivos ficaram menores,** *sem mudar o conteúdo: o `Ficha.gs` foi de 633 KB para 442 KB (as três abas a
menos, e as células curtas vão várias por linha) e o `Codigo.gs` de 240 KB para 199 KB (cada variante de paleta numa
linha). Somados, de 873 KB para 641 KB, e de 26.728 linhas para 3.139. O `PALETAS` continua igual ao
`paletas-grandes.json`, cor por cor.*

**Como foi conferido.** *O Sheets de mentira do `regressao-construir.js` virou módulo (`medidas/sheets-de-mentira.js`) e
passou a guardar tudo o que o `construir()` grava: valor, fórmula, formato, borda, mesclagem, nota, menu, caixa de seleção,
trava, grupo, altura e largura. O `medidas/comparar-construir.js` monta a planilha com o script do commit `aef825f` (sem
as três abas) e com o da pasta, e compara:* **as cinco abas saem iguais, célula a célula**, *e o `ABAS` delas é o mesmo.
O `regressao-construir.js` ganhou onze checagens (fórmula junto do valor, nenhuma fórmula gravada antes de a aba citada
existir ou fora do inglês, mesclagem em lote sem mesclar nada a mais, as travas da `FICHA` e da `CARTEIRA` cobrindo toda
fórmula e só fórmula, a nota no título, e o `acabar()` sozinho, repetido e depois de uma montagem que passou do teto). O
`arnes-pessoal.py` foi de 31 para 40 perturbações; duas não acenderam na primeira rodada (a aba preenchida antes de as
outras nascerem, e o `acabar()` em português), e viraram checagem: o Sheets de mentira agora acusa as duas. Os vinte passam.*

**O que só o Sheets diz, e falta:** *o tempo de verdade do `construir()`; se o `setValues` grava as fórmulas como o
`setFormulas` gravava (a documentação diz que sim: texto que começa com `=` é fórmula); se o `mergeAcross()` deixa as
mesmas mesclagens na tela; e se as abas nascem na ordem pedida (se não nascerem, o script move, como antes).*

### B29 · A Ficha Amaldiçoada — **FEITA em 01/10/2026, e falta montar no Sheets**

*Pedido do Mizuki, depois de quatro rodadas de estudo (`mockup/ficha-amaldicoada-estudo.html`):* **"pode fazer o codigo,
considerando 3 colunas mesmo, é oq gostaram, so q ta mt amassadinho"**, *e antes disso:* *"a ficha amaldiçoada tem que ser
basicamente 'tudo' que já de pra automatizar e calcular para o jogador"*.

**O que entrou.** *A aba `FICHA AMALDIÇOADA`, depois da `FICHA`, e a aba oculta `DADOS_AM`, com as tabelas e as contas dela
(como a `INVOCAÇÃO` tinha a `DADOS_INV`). É a limpeza 25, `ficha-v01/ficha_amaldicoada.py`. A aba tem dez seções, cada uma
num grupo de linhas que fecha: Técnica, Orçamento (com o índice de preços por Classe), Feitiços (36 lugares em três lotes de
12), Classe 0, Liberação Máxima (3), Técnica Máxima, Expansão de Domínio, Passivas (5 pagas e 7 do Leque), Aptidões (12) e
Pactos (3). Uma linha de saltos no alto leva a cada seção.*

**A página mais larga, e por que não é a grade da FICHA.** *Ele pediu as três cartas por fileira com a página mais larga
("dar mais colunas a pagina"). A aba não usa a grade de colunas de 28 px: cada carta tem cinco colunas na largura do que
guardam (112, 140, 112, 56 e 56 px), 476 px no total, contra os 364 px da carta do estudo. São 21 colunas e 1.596 px, e as
seções de cima se alinham nas mesmas colunas. Com isso a aba tem 11 mil células em 537 linhas; na grade de 28 px seriam 33
mil, e a troca de tema dela não caberia num passo do gatilho simples.* **O preço:** *ela cabe inteira num monitor de 1920 px;
num notebook de 1366 px pede zoom de 75% ou rolar para o lado. A decisão está no `decisoes-ficha.json`, em
`C6_documento.largura_fora_do_notebook`.*

**A conta.** *Tudo mora em fórmula, na `DADOS_AM`: uma linha por feitiço, e a carta só mostra o resultado. Nenhuma fórmula usa
`LET` nem `LAMBDA`. A carta calcula: os pontos, o preço de cada peça pela Classe, o desconto de Família Livre, a devolução
das Restrições (com o teto de 2 × Classe, o que se perde, e a que o Selo já obriga), os dados, o PE, a ação, como resolve, o
alcance pelas escadas, o Ampliar em cada Classe acima, e os avisos: Família Fechada, limite de Melhorias e de Restrições,
orçamento estourado, duas Restrições de frequência, os quatro pares que o livro proíbe, o teto de dados somando alvos e
repetições, e as regras da Liberação Máxima. A ficha só calcula e só conta o espaço do feitiço que tem nome.*

**De onde sai cada número.** *As Formas, as Melhorias, as condições, as Restrições e a progressão saem do
`catalogo-projeto-m.json`. As Passivas, as aptidões (com a caixa de regra de cada uma), as escadas de alcance, a Classe 0, a
Liberação, a Técnica Máxima, o Domínio e os pactos não estão no catálogo, que está na v0.258: saem do
`ficha-v01/tecnica-do-livro.json`, que o `ficha-v01/extrair_tecnica.py` lê dos capítulos do livro (v0.330) e que carrega a
versão de onde saiu. O que o livro só escreve em frase é conferido contra a frase.* **Levar essas tabelas para o catálogo é
decisão do Mizuki, e não foi feito.**

**O que ficou diferente do estudo, e por quê:**

1. **A `Passiva Própria` e a `Aptidão Própria` são entradas do menu** *(`Passiva Própria (CP 1)`, `(CP 2)`, `(CP 3)`), e a
   carta tem uma caixa "seu texto". No estudo a mesma caixa mostrava o texto do livro ou o do jogador; na planilha uma
   célula é fórmula ou é digitada, não as duas.*
2. **Na Classe 0 a Restrição Leve devolve o dado que a Melhoria Leve tirou.** *O estudo ignorava a Restrição. O livro diz
   "cabe uma Melhoria Leve e uma Restrição Leve numa Classe 0, tirando um dado para pagar".* **É leitura minha, e falta ele
   confirmar.**
3. **A Liberação Máxima, a Técnica Máxima e o Domínio nascem fechados,** *porque a ficha nova está no nível 2.*
4. **O menu mostra só o nome da peça,** *e o preço aparece ao lado, depois de escolhida ("−2 · Média · Livre"). No estudo o
   menu trazia o preço, que muda de carta para carta; no Sheets a lista do menu é uma só.*
5. **O `+` é da fileira inteira:** *abre as três cartas dela. Isso já era assim no estudo.*

**O que a aba não faz:** *não toca a seção 8 da `FICHA` (ele ainda não decidiu se ela vira espelho ou sai), e não desenha as
rotas sem Fundamento (Técnica Marcial, Sem Técnica e Restrição Celestial).*

**O `construir()` com a aba nova.** *A aba tem 1.272 mesclagens e 374 células de menu. Para ela não triplicar a montagem:*

| o que | como | chamadas |
|---|---|---|
| as treze fileiras de cartas de feitiço, e as de Passiva e de aptidão | só a primeira de cada tipo é mesclada; as outras recebem o formato dela por cópia, e a mesclagem vem junto. O script confere se veio, e se não veio mescla uma a uma | 573 de mesclagem na planilha inteira (eram 310 sem a aba), e 17 cópias |
| os menus e as caixas de seleção do Selo | uma regra por lista, numa matriz do tamanho da aba, gravada de uma vez | 1 |
| os 52 grupos de linhas | nascem todos, fecham todos numa chamada, e os que nascem abertos são abertos | 53 + 1 + 12 |
| a conta de cada feitiço, 75 fórmulas iguais a menos da linha | só a primeira linha vai no `Ficha.gs`; o script a copia para baixo | 9 cópias |

*O `Ficha.gs` também escreve cada fileira de cartas uma vez só: no arquivo fica a primeira e, das outras, só o que é diferente
(a fórmula que aponta para a conta de outro feitiço); o script refaz as cópias quando carrega (`expandirCopias_`). Sem isso
ele teria 1,2 MB. Ficou com 637 KB; com o `Codigo.gs`, 838 KB. Antes de sair a invocação, os dois somavam 873 KB.*

**O tempo.** *Ele mediu a montagem de cinco abas em 220 s (abas criadas 70, as cinco abas 51, menus 8, acabamento 90, dos
quais 83 são as travas), e disse que não vê problema em demorar. Com as duas abas novas a minha conta, por número de chamadas,
é de 60 a 70 s a mais:* **uns 285 s, dentro dos 360.** *É estimativa. O teto para o acabamento começar desceu de 270 para
250 s, porque o acabamento leva 90: se a montagem passar disso, o registro pede o `acabar()`.*

**A troca de tema.** *A aba entra na troca como as outras, num passo de cor e num de régua. Ela é a terceira da ordem: a
troca pinta a `CARTEIRA`, a `FICHA` e a `FICHA AMALDIÇOADA`, e a `FICHA PESSOAL`, o `GLOSSÁRIO` e a arte terminam no clique
seguinte, sem aviso. A aba em que o jogador está passa na frente, como antes.*

**Como foi conferido.** *Entrou o `regressao-amaldicoada.py`, no `rodar-tudo.sh`. Ele preenche onze fichas na planilha gerada,
recalcula no LibreOffice e compara com a regra, escrita de novo em Python:* **os 33 feitiços prontos do livro saem com os
dados que o livro imprime, e nenhum é acusado de erro; 429 cartas batem caixa por caixa (151 com erro, de propósito): as sorteadas em cinco níveis, com Famílias Livres e
Fechadas, e uma ficha de casos de borda, com um feitiço para cada regra que o sorteio quase nunca monta; e o Orçamento, o índice, a Classe 0, a Técnica Máxima, o Domínio, as
Passivas, as aptidões e os pactos batem em quatro fichas.** *Ele também monta a planilha no Sheets de mentira e confere que
a aba fica com as mesmas fórmulas, valores, mesclagens, menus, caixas e grupos da planilha gerada, e que o plano B da
mesclagem deixa a aba igual. O `arnes-amaldicoada.py`, rodado à mão, planta trinta defeitos, um de cada vez, e cada um
acende a checagem dele. Na primeira volta quatro passaram calados: um era o nome da checagem errado no arnês, e três eram
buraco de verdade (o teto da devolução na conta do Ampliar, as duas Restrições de frequência e os pares proibidos), que
o sorteio não montava. Foi daí que veio a ficha de casos de borda, e com ela os trinta acendem. O `medidas/ver-aba.py` desenha a aba (`--aba "FICHA AMALDIÇOADA"`), e eu olhei.*

**O que só o Sheets diz, e falta ele testar:** *o tempo de verdade; se a cópia de formato traz a mesclagem (se não trouxer, o
registro diz "FILEIRAS MESCLADAS UMA A UMA" e a montagem demora mais); o `setDataValidations` com os menus e as caixas de
seleção juntos; abrir e fechar grupo dentro de grupo; a ligação dos saltos; a página de 1.596 px no monitor dele e no
celular; e se os textos compridos das aptidões cabem na caixa.*

**Achado no livro, para ele decidir:** *a tabela `Base por Classe` dá `9 m` e `18 m` para "`Cura` e `Onda`", e a tabela
`Formas` diz que a `Onda` é uma esfera de raio `3 m` centrada em quem conjura. A aba segue a tabela `Formas`, como o estudo.*

### B30 · O menu das mãos só lista o `Soco` — **RESPONDIDO e FEITO em 01/10/2026; falta ver no Sheets, e a frase do `Alcance` no livro fica para revisão dele**

*Achado do Mizuki em 01/10/2026, mexendo na ficha montada com o código do commit `8c7279a`, com duas fotos do `EM USO` da
`FICHA PESSOAL`: o menu da `Mão principal` só com `Soco` e o da `Mão secundária` só com `—`. Palavras dele: "n ta
aparecendo a lista de armas, da pra escrever e funciona, mas a lista n aparece".*

**O que o gerador fazia, e continua fazendo.** *É o desenho do estudo (B26): o menu das mãos lista o `Soco` e o que estiver
nos `Equipáveis guardados` (linhas 69 a 76 da aba; as seis primeiras têm o menu das 52 armas), pelas tabelas
`menu_principal` e `menu_secundaria` do `ficha-v01/ficha_pessoal.py`. A ficha nasce com os equipáveis vazios, e por isso
o menu nasce só com o `Soco`. A arma digitada na mão sem estar guardada é aceita (o menu só avisa) e a linha de baixo diz
"Não está nos equipáveis guardados".*

**A resposta dele:** *"A, manter com aviso visivel e uma nota na caixa aonde fica a escolha de item (na mão) explicando.
Por sinal, seria bom se no momento da arma ser escolhida, como logo abaixo mostra propriedades e afins, poderia colocar
uma nota apresentando o que cada propriedade faz".* **Três coisas entraram:**

- **O aviso visível.** *Sem nenhuma arma guardada, a linha embaixo da `Mão principal` diz `d4 · para outra arma, guarde ela
  nos Equipáveis guardados`; sem arma de uma mão nem escudo guardado, a da secundária diz `Mão livre · arma de uma mão ou
  escudo guardado aparece aqui`. Cada mão conta só o que serve a ela: o escudo não conta para a principal, e a arma de duas
  mãos não conta para a secundária. Com algo guardado, as duas linhas voltam ao texto de antes.*
- **A nota na caixa de escolha.** *A nota das duas mãos saiu do rótulo e foi para a caixa em que a arma é escolhida, e abre
  dizendo que a arma tem de estar nos `EQUIPÁVEIS GUARDADOS`, mais abaixo na aba. O `Vestindo` não mudou: a nota dele
  continua no rótulo.*
- **A nota das propriedades.** *A linha embaixo de cada mão (a que mostra o dado e as propriedades) ganhou uma nota que
  muda com a arma: o nome dela e, uma por linha, cada propriedade com o que faz. É mais uma "nota viva" da `DADOS`, que o
  `notasVivas_` do `Codigo.gs` já copiava para a caixa quando o `EM USO` ou os equipáveis mudam: o script não ganhou código
  novo, só as duas linhas na tabela. O `Soco` e o escudo têm a frase do livro. A arma digitada que não está guardada fica
  sem nota.*

**De onde vem o texto.** *O `catalogo-projeto-m.json` traz as propriedades de cada arma, mas não o que elas fazem. O texto
sai do capítulo de Equipamento do livro (v0.330), pelo `ficha-v01/extrair_equipamento.py`, que grava o
`ficha-v01/equipamento-do-livro.json`: as tabelas `Propriedades` e `Restrições de arma`, e, onde a tabela só aponta ("Ver
Munição"), as frases da seção apontada, que têm de estar no capítulo palavra por palavra. A ficha acrescenta só o número
da arma em uso: as duas faixas no `Longo Alcance` e o X da recarga na `Munição`. As `Duas mãos` entram pela coluna `mão`
do catálogo, sem a frase "No catálogo ela aparece como o 2 da coluna mão". Levar esse texto para o catálogo é decisão do
Mizuki, e não foi feito.*

**O índice da aba andou três colunas na `DADOS`,** *porque a tabela das propriedades entrou antes dele: o
`IDXP_COL_CAMPO` do `Codigo.gs` passou de 116 para 119. É a única linha de código que mudou no `Codigo.gs`.*

**Como foi conferido.** *O `regressao-ficha-pessoal.py` ganhou a nota de cada mão e o aviso em todos os casos (são vinte
agora), com a nota montada de novo a partir do arquivo lido do livro: cinco armas que juntas têm as treze propriedades em
uso, a arma não guardada, só o escudo guardado e só a arma de duas mãos guardada. O `regressao-pessoal.js` confere as cinco
notas vivas, a caixa de cada uma e a nota da caixa de escolha. Entrou o `arnes-ficha-pessoal.py`, rodado à mão, com treze
defeitos plantados nessas contas: os treze acendem, e o contra-teste fica verde. O `arnes-pessoal.py` ganhou dois.*

**O `Alcance` no corpo a corpo: a ficha já segue a resposta dele, e a frase do livro fica para revisão.** *A propriedade
`Alcance` manda ver a seção "Alcance no corpo a corpo", que diz "As Armas Longas chegam a 3 m". Onze armas têm `Alcance`, e
só três são da categoria `Armas Longas` (Lança, Naginata e Yari); as outras oito são Bastão, Bō, Kusarigama, Chicote,
Corrente, Espadão, Nodachi e Odachi, e o livro não diz se elas chegam a 3 m. Perguntei, com três opções, e ele respondeu
em 01/10/2026:* **"sim é A"** *(toda arma com `Alcance` chega a 3 m), e depois:* **"pode mexer na ficha, anotado é pra
mexer no livro essa confusão"**. *Na ficha, a nota de toda arma com `Alcance` termina em "Nesta arma: 3 m", como o `Longo
Alcance` e a `Munição` já traziam o número da arma. Os 3 m saem da frase do livro, pelo `extrair_equipamento.py`; o que é
decisão dele, e o livro ainda não diz, é que valem para as onze.* **Para a revisão do livro (dele, no Claude 2, que eu não
edito):** *a frase "As Armas Longas chegam a 3 m" da seção "Alcance no corpo a corpo" precisa dizer que é toda arma com a
propriedade `Alcance`, e não a categoria `Armas Longas`.*

**O que só o Sheets diz:** *se a nota de 860 caracteres da arma mais carregada aparece inteira ao passar o mouse, e como
a nota fica no celular.*

### B31 · O retorno do teste da Ficha Amaldiçoada — **FEITO em 02/10/2026; o ponto 7 (a seção 8 da `FICHA`) virou o B32; falta ver no Sheets**

*Em 01/10/2026, à noite, o Mizuki montou a `FICHA AMALDIÇOADA` no Sheets com o código do B29 (a montagem funcionou),
trocou para uma paleta rosa e mandou oito pontos, com fotos e a planilha exportada (`Kaori.xlsx`). Sete entraram; o
ponto 7 é desenho novo e ficou para estudo.*

1. **Os textos pequenos ao lado dos títulos de seção saíram.** *Palavras dele: "achei bem inuteis esses textos pequenos
   adicionais, melhor remover". O título de cada seção vai de ponta a ponta (`D` a `T`).*
2. **O nome de cada carta, e a Classe na carta de feitiço, estão na cor de título.** *Ele achou que a paleta ficou "meio
   ruim nas caixas dos feitiços, liberações" e pediu "as cores de titulo em alguns pontos chave". Os pontos são escolha
   minha: o nome e a Classe (105 caixas). O estado da carta (`Na regra`, `⚠ 1 erro`) ficou fora, na cor do painel,
   porque o âmbar de aviso não se lê sobre o acento.* **Falta ele dizer se quer a cor de título em mais ou em menos
   lugares.**
3. **Duas linhas de respiro embaixo do último pacto,** *vazias e fora de grupo, para ele não colar no fim da aba. A aba
   tem 539 linhas agora.*
4. **A troca de paleta não grava mais na célula a cor de aviso que estava acesa.** *A `Livres · Fechadas` dele continuou
   vermelha depois de preenchida certo. A planilha exportada mostrou o vermelho gravado como fundo da célula: o
   `getBackgrounds()` e o `getFontColors()` do Sheets devolvem a cor que a regra condicional está mostrando, e não a da
   célula, e o `repintarCoresDaAba_` gravava de volta o que leu. A caixa nasce em `⚠ 0 de 2`, a troca pegou o vermelho
   aceso e deixou ele gravado. Agora, quando a troca lê o vermelho de estado (`#C2334D`) no fundo, ou o âmbar de estado
   na fonte de uma célula que não nasceu âmbar, ela parte da cor de fábrica daquela célula. Vale para a `FICHA` também,
   e a troca seguinte desfaz o vermelho que uma troca antiga deixou gravado: a planilha dele se conserta na próxima troca
   de paleta, depois de colar o `Codigo.gs` novo.*
5. **A caixa calculada em que alguém digita por cima volta a ser a conta, com um aviso na tela.** *Ele digitou 3 no `No
   domínio` do Orçamento e nada mudou: a caixa só mostra o custo do degrau escolhido na seção do Domínio, e o número
   digitado apagou a conta sem aviso. A `FICHA` avisa pela trava; esta aba não pode ter trava, porque quase tudo nela
   mora em linha de grupo, e trava em linha de grupo faz o Sheets avisar quem clica no `+`. Então a conta volta depois:
   o `devolverConta_` do `Codigo.gs`, chamado pelo `onEdit`, regrava a fórmula da caixa (o `ABAS` do `Ficha.gs` traz a
   fórmula de cada uma) e mostra um aviso por 8 segundos. Só volta fórmula que é referência pura a uma célula
   (`=DADOS_AM!$GH$22`), porque a planilha vive em português, e fórmula com vírgula entre argumentos gravada por script
   nesse idioma vira erro. Por isso a conta de toda caixa calculada da aba passou a morar na `DADOS_AM` (a tabela
   `mostra`), e as 727 caixas calculadas da aba só apontam para ela. Apagar a caixa também devolve a conta; as caixas de
   escolher e de escrever ficam como o jogador pôs.*
6. **A caixa de seleção do Selo saiu da carta.** *Palavras dele: "o selo n obriga restrição nenhuma é algo mais
   narrativo, pode remover". A devolução da Restrição não olha mais para o Selo, e a aba ficou sem caixa de
   seleção. Na volta da bateria achei uma sobra: a nota do rótulo `SELO` ainda dizia "Restrição que cobra a mesma coisa não devolve.", e essa
   frase saiu. A nota ficou "O que você sempre faz para conjurar. Não custa nem devolve ponto."*
7. **O "menu rápido" na seção 8 da `FICHA`: não foi feito.** *Ele pediu trocar a seção 8 por um menu retrátil com o que
   foi pego na `FICHA AMALDIÇOADA` (Passivas, aptidões, feitiços). A seção 8 hoje também serve às rotas sem Fundamento,
   onde vira "Bênçãos e Katas". Ficou a pergunta: o menu rápido substitui a seção 8 só para quem tem Fundamento (A,
   indicado) ou para todo mundo (B). Nos dois casos, é estudo com opções de desenho antes de construir.*
   **Respondido em 02/10/2026:** *"B - Por sinal o 'ficha amaldiçoada' tem q se modificar para cada origem, é pra aquele
   menu funcionar para todo mundo igualmente". O menu vale para todo mundo, e a Ficha Amaldiçoada passa a mudar conforme
   a Origem, que no livro decide a rota de criação: Fundamento, Sem Técnica (`Manejo`, `Auge`, a semente, sem Domínio),
   Técnica Marcial com energia (Corpo Amaldiçoado: `Kata`, `Ruptura`, `Ōgi`, sem Domínio) e sem energia (Restrição
   Celestial: Bênçãos e Lapidação no lugar das aptidões e do refino). O primeiro estudo do menu está em
   `mockup/menu-rapido-estudo.html` (`python3 mockup/estudo_menu_rapido.py`), publicado em
   https://claude.ai/artifact/2KvUsQ9NaraBWNBM8dc7TV: quatro formas (A colunas, B tabela de combate, C mini-cartas, D nomes
   com nota) nas quatro rotas. A pergunta da rodada é qual forma; a seguinte é como a Ficha Amaldiçoada muda em cada rota.*
   **Escolha de 02/10/2026:** *"pior q eu gostei das mine cartinhas, so acho que o espaço pra descrição poderia ser maior,
   tipo... ocupas uma ou duas linhas pra baixo, tem q caber o resumo todo de forma visualizável, qualquer coisa é só fazer
   ser retrateis pra caber melhor". O segundo estudo (mesmo link) mede cada resumo do livro na caixa de cada variação:
   uma ou duas linhas a mais não fazem caber tudo, e a altura que faz caber é 3 linhas no feitiço, 4 na Passiva e 5 na
   aptidão e na Bênção (C3), ou a mesma com só as duas primeiras sempre à vista e o resto num grupo por fileira (C4).
   O resumo da aptidão é a primeira frase da caixa de regra; a caixa inteira (até 1.303 letras) fica na Ficha Amaldiçoada.*
   **Escolha de 02/10/2026:** *"pode ser C3, mas aumente a largura delas, assim você vai ter mais espaço para caber por
   exemplo o tipo de resolvição, q nem o 'aliado auto...' que n coube ali e a descrição vai ter mais espaço para aparecer".
   A seção 8 já vai de D a AT, então carta mais larga é menos carta por fileira. O terceiro estudo (mesmo link) compara a
   C3 de quatro por fileira com três por fileira (13 colunas) e duas por fileira (21 colunas), todas na medida.*
   **Escolha de 02/10/2026:** *"vamos lá, três por fileira, MAS... 1 aumentar o tamanho da altura das descrições é necessario,
   colocar menu retratil para cada grupo é quase obrigatorio, colocar menu retratil para cada grupo de 2 feitiços é
   obrigatorio (um encima do outro eu digo)"*. *O quarto estudo (mesmo link) tem cada bloco (Feitiços, Liberações/Técnica
   Máxima/Domínio, Passivas, Aptidões) num grupo, e cada par de fileiras empilhadas num grupo dentro dele (a leitura é
   minha: grupo de linha fecha a linha inteira, então dois feitiços um em cima do outro são duas fileiras, seis cartas).
   Em cima de cada par fica uma linha que leva o + e diz quais cartas ele guarda ("Feitiços 7 a 12"), porque o + do Sheets
   fica na linha antes do grupo e dois grupos colados no mesmo nível viram um só. O resumo ganhou um botão de folga sobre a
   altura justa (2, 3 e 4 linhas): +1 dá 3, 4 e 5, com 141 linhas no caso cheio e 62 à vista como nasce.*
   **Fechado em 02/10/2026:** *"duas linhas e fechamos"*. *Resumo de 4 linhas no feitiço, 5 na Passiva e 6 na aptidão e na
   Bênção: 163 linhas no caso cheio, 70 à vista como nasce. Na medida conservadora da página cabem perto de 170, 260 e 300
   letras. Na mesma mensagem ele perguntou como ficam as peças criadas (Efeito Próprio, Restrição Própria, Passiva,
   Aptidão e Bênção Própria): a carta de feitiço da Ficha Amaldiçoada não tem lugar para o texto do Efeito Próprio nem da
   Restrição Própria, só o nome no menu e o preço. Ficou a pergunta, com três opções.*
   **Respondido em 02/10/2026:** *"as caixas de descrição, tanto no menu rapido, quanto no ficha amaldiçoada, o plano era
   revelar a descrição que o player escrever, com a narrativazinha dele e talz, a ficha amaldiçoada apresenta o calculo,
   menu rapido as informações do jogador. Ent seria B, o 'como é', mas a gente precisa ajustar o tamanho no menu rapido
   pra caber melhor e compensar nos menus retrateis".* *O quinto estudo (mesmo link): a carta do feitiço mostra o
   "Como é" do jogador, onde ele descreve também a peça criada; a caixa tem 7 linhas, medidas para caber tudo o que
   aparece no "Como é" da Ficha Amaldiçoada (476 px, 5 linhas, perto de 346 letras). A Técnica Máxima e o Domínio
   viram cartas da largura da seção (5 linhas), porque a caixa de lá ocupa a aba inteira. Passivas e aptidões mostram o
   "seu texto" e, quando ele está vazio, o texto do livro em cinza; a Passiva Livre e a Regra Própria abrem o bloco das
   Passivas (14 lugares). Cada fileira tem um grupo que fecha a descrição (o + na linha dos números): 216 linhas com tudo
   aberto, 59 como nasce, 34 com as descrições fechadas, 40 grupos, nenhum colado. Preço novo: a FICHA passa de umas 7 mil
   para umas 16 mil células na troca de tema, e a troca dela pode ter de ser repartida.*
   **Decidido em 02/10/2026:** *"Pode ser A"*: *antes de construir o menu, a rodada de como a Ficha Amaldiçoada muda em
   cada rota, e depois a aba nas quatro rotas e o menu numa construção só. O primeiro estudo das rotas está em
   `mockup/rotas-estudo.html` (`python3 mockup/estudo_rotas.py`), publicado em https://claude.ai/artifact/WkNP6o5RUuiRQN7Zaw5U6k:
   o que o livro muda em cada parte da aba (quase tudo é nome; a Expansão de Domínio some fora do Fundamento; a semente
   do Sem Técnica e o equipamento da Técnica Marcial são peças novas; as Bênçãos e a Lapidação entram no lugar das
   aptidões e do refino, com os mesmos números nas duas de graça), e três formas de pôr na aba o que só uma rota tem
   (A linha da rota na Técnica, B seção da rota, C o script esconde o que a rota não usa), com a Régua, a Redoma, a
   Fisga e a Bancada do livro. Ficam para as rodadas seguintes: a CD da rota de arma (o atributo é o da arma da Kata,
   e a FICHA tem uma caixa só), e se as Passivas do Fundamento valem na Técnica Marcial (o livro não diz).*
   **Escolha de 02/10/2026:** *"Eu gosto da C, n vou menitr, vamos testar"*. *A forma C: o desenho da linha da rota, e o
   onEdit esconde na Ficha Amaldiçoada o que a rota não usa quando a Origem muda na FICHA (a linha da rota no
   Fundamento, a Expansão de Domínio fora dele, a linha do Estímulo Muscular fora da Restrição Celestial sem energia).
   Antes de construir, um teste de bancada para ele rodar numa planilha em branco: `medidas/teste-esconder-rota.gs`
   (montarTeste, e o roteiro de seis passos fica escrito na aba FICHA). Ele confere o que o Sheets de mentira não sabe:
   se a linha escondida pelo script continua escondida quando o grupo em volta abre e fecha, se o Domínio volta como
   estava (fechado ou aberto), e se funciona numa cópia só com o gatilho simples. Rodado contra uma imitação mínima do
   Sheets no node, sem erro.*
   **Resultado do teste e decisões (02/10/2026):** *os passos 1 a 3 funcionaram (o script esconde e mostra por rota, e
   o Domínio volta como estava); no passo 4 "volta revelada": abrir o grupo em volta revela a linha que o hideRows
   escondeu. No passo 5 ele estranhou "refino, aptidão e outros seguem lá", que eram os rótulos fixos da aba de teste
   (na aba de verdade o título e as caixas viram Bênçãos e Lapidação por fórmula). Com isso ele voltou para a A: "Acho
   que seguirmos com o plano A vai ser melhor mesmo". A linha da rota fica na Técnica, sem script, e o Domínio diz que
   a rota não tem. Na CD da rota de arma, A: uma CD por grupo na linha da rota (atributo, conjuração e CD de cada
   grupo), e a linha de cima da Técnica diz "Por grupo" quando os grupos misturam atributos. Fica a dúvida da caixa de
   CD da própria FICHA na rota de arma. Pergunta seguinte: as Passivas do Fundamento no menu da Técnica Marcial.*
   **Respondido em 02/10/2026: "B".** *Na Técnica Marcial (as duas rotas), o menu de Passiva traz as 6 do capítulo da
   Técnica Marcial (Calo, Maldição do Inventário, Leitura, Segundo Fôlego, Contragolpe, Aliança) e a Passiva Própria;
   uma Passiva do Fundamento entra como Passiva Própria, com o mestre. A Regra Própria segue na seção da Técnica em
   todas as rotas. Com isso o desenho fechou, e a construção da aba nas quatro rotas e do menu rápido começa.*
8. **Toda caixa da aba abre em letra maiúscula.** *Palavras dele: "Textos em minusculo, sempre bom padronizar o maisculo
   na letra inicial". Vale para o que a ficha calcula e para o que nasce escrito: os menus de pacto viraram `Permanente`,
   `Temporário`, `De restrição` e `Um espaço de feitiço`, o estado virou `Na regra`, o Domínio diz `Não fecha` e `Rola`.*

**Para a revisão do livro (dele, no Claude 2, que eu não edito):** *a regra de que a Restrição que o Selo já obriga não
devolve ponto continua no livro da v0.330, e a ficha não a aplica mais. Ela está em quatro lugares:*

| arquivo | linha | o que diz |
|---|---|---|
| `40-fundamento.md` | 864 | a Restrição Própria "não pode repetir o que o seu Selo já obriga" |
| `40-fundamento.md` | 874 | "Restrição que o seu Selo já obriga não devolve ponto." |
| `20-criacao-de-personagem.md` | 135 | no passo do Selo: "Restrição que o Selo já obriga não devolve ponto." |
| `42-tecnica-marcial.md` | 99 | a Restrição que pede "estar com a minha arma" não devolve ponto, porque "O Selo já obriga isso" |

*Em 02/10/2026 ele explicou a leitura: "o ponto q a restrição do selo é mais narrativa, ela n realmente aplica uma
restrição nos feitiços, é só algo que você é obrigado a fazer e qualquer feitiço". O Selo não entra na conta de
Restrição, e as quatro linhas saem do livro. A da Técnica Marcial é a única em que isso muda número: nessa rota o Selo é
ter a arma em uso ("O seu Selo é ter o equipamento em uso"), e sem a linha uma Restrição "estar com a minha arma" devolve
ponto por uma coisa que o lutador marcial já faz o tempo todo. É para ele olhar quando mexer no capítulo; a ficha não
tem a rota marcial e não muda por isso.*

**Como foi conferido.** *O `regressao-amaldicoada.py` ganhou sete checagens: o título de cada seção de ponta a ponta, as
duas linhas de respiro, as 727 caixas calculadas como referência pura, o nome e a Classe na cor de título, o estado fora
dela, nenhuma caixa abrindo em minúscula em nenhuma das onze fichas, e a aba sem caixa de seleção. O
`regressao-construir.js` digita por cima do `No domínio` no Sheets de mentira e confere que a conta volta com um aviso,
que apagar a caixa também devolve, que a Forma e o nome do feitiço ficam como o jogador pôs, e que a fórmula que não é
referência pura não é regravada. O `regressao-paleta.js` acende o vermelho e o âmbar na grade que a troca lê e confere
que a planilha termina igual à da troca sem aviso, e que a troca seguinte desfaz o vermelho gravado por uma antiga. Nos
arneses: o `arnes-pessoal.py` ganhou quatro defeitos (46), o `arnes-paleta.py` dois (9), e o `arnes-amaldicoada.py` perdeu
o da caixa do Selo e ganhou seis (35). O `arnes-amaldicoada.py` tinha um erro de aspas na perturbação da proteção do
cobrir-se, e não rodava; foi consertado antes da volta. Rodado nas perturbações novas ou mexidas (16 e 17, do Domínio;
18, da vaga do Leque; e 27 a 32, as seis do B31), acendeu as nove, cada uma na checagem dela. A bateria inteira passou
antes: os vinte e um.*

**O que só o Sheets diz, e falta ele ver:** *o aviso na tela quando digita por cima; a conta voltando na planilha em
português; a paleta rosa com o nome das cartas no acento; e a `Livres · Fechadas` dele saindo do vermelho na primeira
troca de paleta depois de colar o `Codigo.gs` novo. A aba mudou de forma (o respiro, as caixas que apontam para a
`DADOS_AM`, a caixa do Selo que saiu): para ver, é montar de novo com o `Ficha.gs` novo.*

### B32 · As quatro rotas da Ficha Amaldiçoada e o menu rápido na seção 8 da `FICHA` — **FEITO em 02/10/2026, e montado no Sheets pelo Mizuki no mesmo dia: "está funcionando"**

*O ponto 7 do B31, com o desenho fechado lá, rodada a rodada. Pela escolha dele ("Pode ser A": as rotas antes, e tudo
numa construção só), a aba nas quatro rotas e o menu foram feitos juntos.*

1. **A `FICHA AMALDIÇOADA` muda conforme a Origem da `FICHA`, na forma A do estudo.** *A rota sai das marcas que a
   `FICHA` já tinha (sem energia, Técnica Marcial, Sem Técnica): Fundamento, Sem Técnica, Técnica Marcial com energia
   (o Corpo Amaldiçoado) e Técnica Marcial sem energia (a Restrição Celestial). O que o livro muda de rota para rota
   saiu dos capítulos pelo `extrair_tecnica.py` (a chave `rotas` do `tecnica-do-livro.json`, conferida frase a frase):*
   - *os nomes: os títulos, o Selo, o Orçamento, os lotes, as caixas de graça e os saltos dizem `Manejo`, `Liberação
     Máxima` e `Auge` no Sem Técnica, `Kata`, `Ruptura` e `Ōgi` na Técnica Marcial, e Bênçãos e Lapidação no lugar das
     aptidões e do refino na sem energia;*
   - *a linha da rota, na seção da Técnica: a rota, a semente (Sem Técnica) ou o equipamento (Técnica Marcial), o que a
     semente dá ou se o golpe simples fere maldição, e, na rota de arma, os três grupos com o atributo, a conjuração e a
     CD de cada um (a Lâmina Longa acerta com o maior entre Força e Destreza). A linha de cima da Técnica diz o atributo
     das armas quando os grupos concordam, e "Por grupo" quando misturam (a CD na rota de arma, resposta A);*
   - *os menus: a Técnica Marcial compra as Passivas do capítulo dela e a Passiva Própria (resposta B), o Sem Técnica as
     duas listas, a sem energia compra Bênçãos, e o Corpo Amaldiçoado não compra a Extensão de Domínio;*
   - *a Expansão de Domínio: fora do Fundamento a seção diz que a rota não tem, e não gasta espaço de feitiço;*
   - *a linha do Estímulo Muscular, nas Bênçãos da sem energia: a perícia, o Teste de Resistência e os usos (1× por
     cena, 2× na Lapidação 10).*

   *A aba foi de 539 para 548 linhas. O link de cada salto passou a citar a célula do nome dele na `DADOS_AM`, que muda
   com a rota.*
2. **O menu rápido no lugar da seção 8 da `FICHA` (`ficha-v01/menu_rapido.py`, a limpeza 26).** *Das linhas 119 a 345:
   os feitiços (36 lugares), as Liberações com a Técnica Máxima e o Domínio, as Passivas (14 lugares, a Passiva Livre e a
   Regra Própria primeiro) e as aptidões (14, as duas de graça primeiro). Mini-cartas três por fileira, de 13 colunas
   cada; a Técnica Máxima e o Domínio em carta da largura da seção. São 42 grupos: um por bloco, um por par de fileiras
   empilhadas (o + mora na linha que diz "Feitiços 7 a 12") e um pela descrição de cada fileira. A seção nasce com 63 das
   227 linhas à vista (o primeiro par de cada bloco aberto), e fica em 45 com as descrições fechadas.*

   *Nada ali se digita. Cada caixa aponta para uma célula da `DADOS_AM`, onde a lista é montada sem buraco: o feitiço de
   nome apagado some, e o de baixo sobe. A carta de feitiço mostra a Classe, o nome, o PE, a Forma, como resolve e o
   "Como é" que o jogador escreveu; a de Passiva e a de aptidão, o "seu texto", ou "Do livro: ..." quando ele está vazio.
   Os títulos dizem os nomes da rota e quantos de cada ("FEITIÇOS · 6 de 36"). As linhas do menu ficam fora da trava de
   fórmula (moram em grupo), e quem escreve por cima recebe a conta de volta com aviso, como na Ficha Amaldiçoada.*

   *Saiu com a seção 8: as seis caixas dela no índice (feitiços disponíveis, Passivas, as duas aptidões de graça,
   aptidões disponíveis e Passivas do Leque), o "Refino Atual" impresso, as notas e o aviso vermelho delas no
   `Codigo.gs`, e as notas de graça que o `onEdit` refazia quando a Origem mudava. A conta, o aviso e a nota dessas
   coisas moram na Ficha Amaldiçoada. As duas contas da `DADOS` que liam a seção (aptidões e Passivas do Leque anotadas)
   leem a Ficha Amaldiçoada.*
3. **O que mudou do estudo.** *O menu tem 227 linhas e 42 grupos, e o estudo dizia 216 e 40: as legendas de par e as
   linhas de respiro entre fileiras que o estudo não desenhou. A carta da Técnica Máxima sem nome fica vazia, como a de
   feitiço; a regressão achou ela mostrando a Forma que a aba já traz escolhida ("Projétil") e "Rola". Antes do nível
   dela, o PE mostra "—", como na aba (o desenho da Kaori mostrou "— PE"). O texto do livro, quando o jogador não
   escreveu o dele, vai inteiro se cabe na caixa (a medida do estudo: perto de 260 letras na Passiva, 300 na aptidão e
   na Bênção), e a primeira frase se não cabe. O estudo dizia "a primeira frase" para toda aptidão; a leitura de deixar
   inteiro o que cabe é minha, e fica para ele vetar: 11 das 29 aptidões e Bênçãos e 1 das 24 Passivas vão pela primeira
   frase. O desenho mostrou o Canalizar energia inteiro (553 letras) cortado na caixa. O texto do livro não sai em cinza como no estudo: a cor viria de regra condicional, que não muda
   com a paleta, e o "Do livro:" na frente já separa do texto dele.*
4. **O preço.** *A `FICHA` foi de 150 para 347 linhas, de 7.050 para 16.309 células.*
   - *A troca de paleta passa de 30 s se pintar a `FICHA` de uma vez num Sheets lento. A aba grande vai em trechos de até
     7.500 células, com a régua logo depois do primeiro (a parte de cima é a que ele vê primeiro). A promessa da troca
     mudou: o clique na caixa da paleta pinta a `CARTEIRA` e a `FICHA`, e a Ficha Amaldiçoada, a Ficha Pessoal, o
     Glossário e a arte terminam nos dois cliques seguintes (antes era no primeiro), sem aviso. A aba em que ele clica
     continua passando na frente.*
   - *O `Ficha.gs` foi de 640 para 703 KB (o `Codigo.gs` tem 205 KB). As fileiras de três cartas do menu vão por cópia de
     formato da primeira, como na Ficha Amaldiçoada: sem isso eram 735 KB e mais de 900 chamadas de mesclagem.*
   - *Quem já escreveu na seção 8 de hoje (os feitiços, as Passivas e as aptidões da Kaori, por exemplo): a seção nova não
     tem onde digitar. O que estava lá passa para a Ficha Amaldiçoada, e o menu mostra.*

**Como foi conferido.** *O `regressao-amaldicoada.py` ganhou cinco fichas (as quatro rotas e uma, `menu`, que escreve o
que só o jogador escreve e deixa feitiço sem nome no meio) e duas seções: as quatro rotas (títulos, linha da rota,
grupos de arma, linha de cima da Técnica, menus de cada rota, Domínio, caixas de graça e Estímulo) e o menu rápido em
toda ficha recalculada (a ordem de leitura das cartas, a lista sem buraco, o "Como é", as Liberações, a Técnica Máxima e
o Domínio, as Passivas e as aptidões com o texto do jogador ou o do livro, as duas de graça da rota e os títulos). O
`regressao-construir.js` confere que as caixas do menu só apontam para a `DADOS_AM`, que as mesclagens das fileiras
copiadas chegam na aba montada, e que escrever por cima do menu devolve a conta (com a devolução desligada no
`Codigo.gs`, ela acusa). O `comparar-ficha-01.py` declara a limpeza 26 e fecha em IGUAIS. O `conferir-ficha-xlsx.py`
confere o que saiu do índice e do `Codigo.gs` e as cartas de graça do menu pela rota. A Kaori ficou com o que continua na
`FICHA` (Defesa, X de Y, espaços de feitiço, ataques: 10 de 10 e 20 de 20). Nos arneses: o `arnes-amaldicoada.py` foi de
35 para 57 defeitos (12 das rotas e 10 do menu); o 44, que trocava `>=3` por `>=2` numa fórmula que trata o Sem
Técnica antes, não mudava nada e foi reescrito para fazer o que o nome diz; o `arnes-paleta.py` de 9 para 10 (a troca que pintasse só o primeiro
trecho da `FICHA`), e três trechos dele que tinham ficado velhos com a troca em trechos foram atualizados. Rodados nesta
volta: os 26 da Amaldiçoada que são novos ou mudaram (23, 34 a 57) acendem, cada um na checagem dele; os 10 da paleta e
os 46 da pessoal também. O `medidas/ver-aba.py --aba FICHA` desenha a `FICHA` com a Kaori da Ficha Amaldiçoada, e foi
por ele que o "— PE" e o texto cortado apareceram. A bateria inteira passou: os vinte e um, e a seção do menu na
regressão com 115 checagens (3 gerais e 7 em cada uma das 16 fichas).*

**Montado no Sheets em 02/10/2026.** *Ele colou os dois arquivos, montou e respondeu "pode fazer comit e está
funcionando", com a planilha exportada (`Kaori.xlsx`, uma ficha nova, sem personagem: o menu nasce com "FEITIÇOS · 0 de
36"). Na mesma mensagem ele apontou o número da `CARTEIRA`, que é o B33.*

**O que ele não detalhou, e fica para quando usar:** *abrir e fechar os grupos do
menu (o + de cada par na linha da legenda, o da descrição na linha dos números); escrever por cima de uma carta do menu
(o aviso e a conta voltando); trocar a Origem na `FICHA` e ver a Ficha Amaldiçoada e o menu mudarem de nome, e o Domínio
dizer que a rota não tem; e trocar de paleta, contando os cliques até a última aba terminar.*

### B33 · O número da `CARTEIRA` não acompanha a versão do sistema — **FEITO em 04/10/2026: o catálogo foi posto em dia com o livro reconstruído (ver o B36); em 07/10/2026 o número passou a mostrar a versão com o ponto, `Nº M-1.0` (no fim do B41)**

*Em 02/10/2026, depois de montar o B32: "por sinal a versão n atualizo automatico", com a foto do carimbo da `CARTEIRA`:
`Nº M-0258-····` e `Emitida 02.10.2026`. O livro está na v0.331.*

*O número é `"Nº M-" & DADOS!B1 & "-" & as quatro primeiras letras do nome` (os pontos são o nome vazio da ficha nova), e
a `DADOS!B1` é o `_meta.versao` do `catalogo-projeto-m.json`, que está em 0.258. Foi de propósito: na reextração do
`manual.txt` da v0.263 (22/09/2026, commit 7f83e35) ficou escrito que "o carimbo fica em 0.258, de propósito. Ele é a
versão do CATÁLOGO". As listas da ficha (perícias, Caminhos, Trilhas, equipamento, legados) saem do catálogo, conferido
contra o `manual.txt` da v0.263; só a Ficha Amaldiçoada e a nota das armas leem os capítulos direto, na v0.330. O
número diz a verdade sobre os dados; o que ele não faz é andar sozinho com o livro.*

*Opções levadas a ele: pôr o catálogo em dia com o livro (reextrair o `manual.txt` do PDF da versão atual, conferir, e o
número vai junto), ou o número passar a mostrar a versão do livro em que a ficha foi gerada, ou deixar como está. O
`manual.txt` sai do PDF de coluna única do livro, que estava sendo refeito em segundo plano na hora.*

**Respondido em 02/10/2026: "A".** *Medido antes de mexer: o PDF de coluna única da v0.331
(`Projeto-M-Manual-da-Guilda.pdf`, 380 páginas, gravado às 16:31; o `-A-atual` é um retrato antigo, sem o Incursor), com
`pdftotext -layout`, numa cópia isolada do repositório no lugar do `manual.txt`. A v0.331 está no disco do Claude 2
sem commit, e o CHANGELOG dela diz que "a revisão ampla de nomes, texto e apresentação artística permanece para a
próxima etapa". Passam com o livro novo: o `conferir-kaori.py`, o `conferir-progressao.py`, o `revisao-cetica.py` e o
`regressao-exemplos.py`. Falham sete no `conferir-catalogo.py` e três no `conferir-decisoes.py`:*

| o que | é o livro que mudou? |
|---|---|
| seis Caminhos e dezoito Trilhas ("São seis Caminhos nesta edição, três Trilhas em cada um"); o catálogo tem cinco e quinze | sim: o **Incursor** (d6, vida 6, 4 por nível, 6 PE, Destreza · Força, `Acrobacia` · `Intuição`, treina as treze categorias) e as Trilhas Assassino, Pugilista e Malabarista |
| as Trilhas | sim: dez das quinze mudaram de nome. Brasa virou Combatente Amaldiçoado; Elo, Sutura e Perímetro viraram Arquiteto, Analista e Socorrista; Torrente, Explosivo e Arremate viraram Condutor Armado, Ressonante e Catalisador; Servo, Matilha e Coro viraram Invocação Principal, Parceria e Múltiplas Invocações. Muro, Punho, Estocada, Batedor e Executor ficaram |
| (sem falha no conferidor) as perícias fixas do Bastião | sim: `Atletismo` · `Provocar`; o catálogo tem `Intimidação` |
| a linha 23 da progressão | sim: o nível 23 dá "degrau de Caminho" (era "—") |
| as fontes de vida temporária `Aprumo` e `Crosta`, e de energia `Braseiro` e `Trindade` (`decisoes-ficha.json`); o número do Parrudo | sim: os nomes sumiram do livro com as Trilhas novas |
| armas, treino por categoria, munição, carga | não, ao que parece: no PDF novo o número da página caiu no começo da linha da tabela ("15    Taco…"), e o leitor só tirava do fim. A confirmar no conserto do leitor |

*Na ficha, isso pega o menu de Caminho e o de Trilha, as perícias marcadas pelo Caminho, o treino de arma (o
`Codigo.gs` nomeia os Caminhos), a Empunhadura do Arremate (agora `Arma Condutora`, do Condutor Armado), as notas que
citam Caminho e Trilha, o C1 (o Caminho oculto do menu) e o `decisoes-ficha.json`. A pergunta que espera ele: fazer
agora, contra a v0.331 sem commit, ou depois da revisão de nomes.*

### B34 · A seção 7 da `FICHA` vira "Habilidades" — **FEITA em 02/10/2026 (forma C, escrita à mão, a carta acima do nível riscada); falta montar no Sheets**

*Pedido dele em 02/10/2026, antes de pôr o catálogo em dia: "Recomendo que refaçamos o 'anotações' (ja que agora caminho
da 5 habilidades) e outras partes do ficha que necessitam de 'atualização', para aproveitar melhor das novas partes da
ficha que foram feitas", com protótipos de como pode ficar a seção, "que provavelmente vai mudar para 'habilidades'". E,
no meio da rodada: "nem precisa de automação AINDA (deixar preparado é o ideal), ja q o livro está sendo reescrito,
deixando claro isso".*

*O livro novo (capítulo 35, v0.331 no disco do Claude 2, sem commit) dá ao Caminho cinco degraus, nos níveis 2, 7, 15,
23 e 30, e à Trilha quatro entregas, nos níveis 2, 11, 19 e 27; um degrau pode trazer mais de uma habilidade (o nível 7
do Bastião traz três; o nível 2 do Assassino, cinco). O texto do livro de um nível vai de 136 a 8.562 letras (mediana
944): nenhuma caixa da ficha comporta o texto inteiro, e o jogador anota o nome e um resumo. A seção de hoje tem 30
linhas, doze caixas de 11 colunas por 4 linhas, e não usa as colunas AM a AT.*

*O estudo está em `mockup/habilidades-estudo.html` (`python3 mockup/estudo_habilidades.py`, que lê os nomes e o começo do
texto de cada nível do capítulo 35 só para o exemplo), publicado em https://claude.ai/artifact/VaWxcwKG8eTGUMTVgq8bGq:
quatro formas, todas escritas à mão, com uma caixa fixa por degrau e por entrega e lugar para as escolhas da Trilha e
para as anotações. A três colunas (a de hoje com cinco linhas, 38 linhas), B linha do tempo (uma lista na ordem dos
níveis, 51), C cartas (a linguagem do menu rápido, 36) e D consulta (uma linha por degrau com uso e resumo de uma
linha, o texto num grupo que nasce fechado, 51 com tudo aberto e 24 como nasce). Preparado para o livro: o nível de
cada caixa é fixo, e mais tarde o nome e o texto podem vir de lá pela Trilha e pelo nível sem refazer a seção. A
página também lista o que mais na FICHA pede atualização, na minha leitura (a Progressão contando de novo o que a Ficha
Amaldiçoada conta, a CD por grupo na rota de arma, os nomes da rota no Marco Escolhido), cada um para uma rodada
própria.*

*A pergunta que espera ele: qual forma, valendo misturar. Depois: a caixa acima do nível do personagem diz "Abre no
nível 15" ou fica vazia; e o nome da seção.*

**Escolha de 02/10/2026: "Vai a C mesmo".** *As cartas, na linguagem do menu rápido: um bloco para o Caminho (cinco
cartas e uma de anotação) e um para a Trilha (quatro cartas, as escolhas e uma de anotação), três por fileira, cada
fileira com o seu grupo. O nome da seção é "Habilidades", o que ele mesmo pôs no pedido. Pergunta seguinte: a carta de
um degrau que o personagem ainda não alcançou diz "Abre no nível 15" ou fica vazia.*

**Respondido em 02/10/2026: "A e o texto fica 'riscado' (esqueci o nome), até desbloquear".** *A carta diz quando abre,
e o que estiver escrito nela fica riscado até o nível chegar. O aviso foi para a etiqueta do nível, que ganhou três
colunas ("Nível 15" quando abriu, "Abre no 15" quando não), porque o nome é onde o jogador escreve e não pode ser conta.
O estudo foi atualizado com isso (mesmo link).*

**Como ficou (a limpeza 27, `ficha-v01/habilidades.py`).** *A seção 7 vai da linha 88 à 124: o título "HABILIDADES", o
bloco do Caminho (as cartas dos níveis 2, 7, 15, 23 e 30, e uma de anotação) e o da Trilha (2, 11, 19 e 27, as escolhas
da Trilha e uma de anotação), três por fileira, com um grupo por bloco e um pelo texto de cada fileira; nasce aberta a
primeira fileira de cada bloco. O nome e o texto de cada carta são do jogador. A etiqueta de nível e o título de cada
bloco ("CAMINHO · BASTIÃO · CINCO DEGRAUS") são conta numa tabela da `DADOS_AM`, e a caixa da FICHA só aponta para ela:
fica fora da trava, e quem escreve por cima recebe a conta de volta, como no menu rápido. O riscado é regra de cor
declarada no ABAS (`=LEFT($D$92,4)="Abre"` sobre o nome e o texto da carta), que o `corDeEstado_` junta às regras dele,
porque ele troca todas as regras da FICHA; ela só risca, sem mudar cor, para não brigar com a troca de paleta. O menu
rápido passou a começar na linha 125 (o `menu_rapido.trocas` recebe a linha e as células da seção 7 que não pode
apagar). A arte de respingos que morava no canto da seção foi para o lado do título (AQ a AS, três linhas), onde as
cartas não chegam. Os níveis das cartas são os do livro novo (cap. 35 da v0.331); o catálogo da v0.258 e o
`manual.txt` da v0.263 ainda dão ao Caminho só quatro degraus (sem o 23): é o atraso do B33.*

**Como foi conferido.** *O `regressao-amaldicoada.py` lê os níveis das cartas na tabela "Entregas por nível" do capítulo
35 do livro (quando o livro está na máquina) e confere, em toda ficha recalculada, a etiqueta de cada carta pelo nível e
o título de cada bloco pelo Caminho e pela Trilha (a ficha `menu` escolhe Bastião e Muro). O `regressao-construir.js`
confere que as 11 contas da seção só apontam para a `DADOS_AM`, que a FICHA montada tem as 9 regras de riscar junto com as
outras, e que escrever por cima da etiqueta devolve a conta. O `comparar-ficha-01.py` declara a limpeza 27 e fecha em
IGUAIS; o `conferir-ficha-xlsx.py` confere a arte no lugar novo. O `medidas/ver-aba.py` desenha a riscada (a regra de
fórmula) e a Kaori com quatro habilidades escritas, até a do nível 15; o desenho bate com o estudo. Nos arneses: o
`arnes-amaldicoada.py` vai a 60 (a etiqueta abrindo um nível depois, o Caminho de volta a quatro degraus, o título
esquecendo a Trilha) e o `arnes-pessoal.py` a 48 (o riscado apagado pelo corDeEstado_, a etiqueta que não volta). No
caminho, o `tecnica-do-livro.json` e o `equipamento-do-livro.json` passaram a dizer v0.331: o livro no disco do Claude 2
virou v0.331 durante a rodada, e a bateria acusou os dois arquivos; o conteúdo que a Ficha Amaldiçoada e a Ficha Pessoal
leem é o mesmo, e só o carimbo mudou (o Ficha.gs não mudou com isso).*

**O que só o Sheets diz, e falta ele ver:** *o riscado aparecendo e sumindo quando o NÍVEL muda; a etiqueta "Abre no 15"
cabendo nas três colunas; os grupos de cada fileira; e a arte ao lado do título.*

### B35 · A foto da `CARTEIRA` entra na célula, com a moldura em volta — **FEITA em 03/10/2026 (a B+) e MONTADA NO SHEETS: em 07/10/2026 o Mizuki disse "B35 funciono normalmente"; a ligação com a `FICHA PESSOAL` foi feita no B38**

*Pedido dele em 03/10/2026: "Sabe no ficha aonde temos a foto? Então, é uma 'imagem', então não dá pra inserir imagem
nela, tem que ser uma imagem 'solta' por cima que o jogador põe, oq não é muito bom. Eu não sei se teria alguma forma de
manter a imagem, o contorno bunitinho, sem fazer com que o jogador tenha q inserir a imagem do personagem encima da
célula ao invés de na célula. Porque na célula também daria pra ligar a imagem no ficha com o espaço no ficha pessoal".
A moldura era a imagem `carteira-2` DENTRO da caixa `C8:K21`, e uma célula guarda uma coisa só.*

*As opções: A, a moldura solta por cima com o miolo transparente; B, só a borda da célula (perde os cantos chanfrados);
C, a moldura cortada em pedaços nas células em volta; e a B+, a borda no anel em volta da caixa e os dois chanfros como
imagem pequena na célula do canto. A A caiu com a pergunta dele: "se for A, o jogador quando clicar vai acabar clicando
na imagem ao invés do fundo, não?" (a imagem solta pega o clique no retângulo inteiro, até no transparente).*

**Escolha de 03/10/2026: "vamos de B+ ... ai a gente fazer a parte central ser uma celula só mesclada, que o jogador
clica e insere".**

**Como ficou (a limpeza 28, `ficha-v01/moldura_foto.py`).** *A caixa `C8:K21` continua mesclada e do mesmo tamanho
(252 x 300), sem imagem dentro, com "FOTO / 顔" escrito em Yuji Syuku 22 (a fonte do 呪術廻戦 do cabeçalho, a única
das três que tem as letras e o kanji; 22 é o piso de kanji da ficha) e a nota "Clique na caixa e use Inserir › Imagem
› Inserir imagem na célula."; a imagem inserida toma o lugar do texto. A moldura foi para o anel `B7:L22`: as retas
são borda média na régua (que a troca de paleta já repinta), e os chanfros de cima à esquerda (`B7`) e de baixo à
direita (`L22`), os mesmos do desenho antigo, são a arte `carteira-canto`, o traço "/" de canto a canto da célula
(28 x 21 em cima, 28 x 27 embaixo, porque a linha 22 é mais alta). Fica uma margem de uma célula entre a linha e a
foto.*

*Três coisas que a rodada achou e consertou:*
- *a caixa da paleta se ancorava na imagem mais alta da `CARTEIRA` (`acharCaixaDaFoto_`), que era a moldura; com a
  caixa vazia, ia ancorar noutra arte. A `CARTEIRA` passou a declarar a caixa da foto (`foto` no ABAS), e a função lê
  essa caixa primeiro. O `regressao-construir.js` só via que a caixa nascia na CARTEIRA; agora confere o lugar
  (`C26:I26`, `C27:M28`, `C29:M29`, o do Kaori.xlsx);*
- *a troca de paleta põe na arte um piso de contraste de 3,0, e a borda não tem piso: em 30 das 122 paletas a régua lê
  menos de 3,0 contra a tinta, e o canto sairia de outra cor que a reta em que emenda. O canto segue a régua exata
  (`ARTE_DA_BORDA_`, no `Codigo.gs`);*
- *a arte embutida saía 1 a 3 tons fora da cor desenhada (o Pillow 10 reduz com o alfa pré-multiplicado, e o LANCZOS
  estoura a beira do traço), e o canto nascia 8E81C9 contra a borda 8A7EC4. O `emitir_gs.py` passou a tirar a cor da
  arte desenhada, antes da redução; as outras artes mudaram 1 a 3 tons, para a cor que foi desenhada.*

*Conferido pelo `conferir-ficha-xlsx.py` (a regra da moldura, lida do que o script manda para o Sheets: a caixa
declarada é mesclada, sem imagem, com o convite e a nota; o anel com a régua no lado de fora e reta nenhuma nas quinas;
cada quina com uma imagem só, o traço "/" na régua, que a troca pinta na régua exata), pelo `regressao-paleta.js` (os 2
cantos saem na régua exata nas 122 paletas, a troca de verdade), pelo `regressao-construir.js` (o lugar da caixa da
paleta), pelo `regressao-arte.js` (oito imagens, sem a moldura antiga e com os dois cantos) e pelo comparador (IGUAIS,
com a limpeza 28). O `arnes-moldura.py`, novo e rodado à mão, planta nove defeitos na moldura; o `arnes-pessoal.py` vai
a 51 (a caixa da paleta de volta na imagem mais alta e a CARTEIRA sem declarar a caixa, que param a montagem, e
a caixa declarada uma linha mais curta, que tira a caixa da paleta do lugar) e o `arnes-paleta.py` a 11 (o
canto passando pelo piso da arte).*

**O que fica para depois:**
- *a ligação com a `FICHA PESSOAL` (ele: "num geral o jogador colocaria a imagem na carteira e ela iria para o ficha
  pessoal"). A caixa "FOTO DO PERSONAGEM" da FICHA PESSOAL passaria a ser `=CARTEIRA!C8`, e a documentação do Google
  não diz se uma fórmula que aponta para uma célula com imagem inserida mostra a imagem. Espera o teste dele numa
  planilha em branco: uma imagem inserida na `A1`, `=A1` na `B1` e numa outra aba. Se não mostrar, o caminho é o
  `IMAGE` com o link da foto;*
- *o que só o Sheets diz: se a imagem dentro da célula do canto encosta nas bordas da célula ou fica com folga (se
  ficar, aparece um vãozinho na quina, e a saída é a B, só a borda), e a foto inserida no lugar do "FOTO / 顔".*

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

### B36 · A ficha posta em dia com o livro reconstruído — **FEITA em 04/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele conferiu o Incursor, a Defesa e a carga acima do limite ("Sim" nos três), e pediu a mudança da arma sem a Força, que está na terceira etapa do B40**

*Pedido dele em 04/10/2026, antes de mesclar a revisão do livro (a PR #2 do JJK---Project): "atualize a ficha do sistema
pfvr, colocando o que faltava e modificando o que foi mudado (origens ainda vão ser mudadas, mas siga como estão agora)".
O livro passou a ser a candidata editorial reconstruída (`LIVRO-COMPLETO.md`, 382 páginas), e o B33 fechou junto: o
carimbo da `CARTEIRA` passou de `0.258` para `0.331 · 04/10`.*

**De onde o livro entra agora.** *O `manual.txt` deixou de sair do PDF com `pdftotext`: o `extrair-manual.py` o tira do
`LIVRO-COMPLETO.md`, sem as marcas de formatação, com o `#` dos títulos e as tabelas uma fileira por linha (" | " entre
as colunas). O `manual-fonte.json` guarda o arquivo e o hash. O `livro.py` lê seção e tabela. Os dois extratores
(`extrair_tecnica.py` e `extrair_equipamento.py`) deixaram de ler os capítulos do HD e leem o `manual.txt`, que mora aqui.
O catálogo foi remontado do livro e é conferido por outro caminho no `conferir-catalogo.py` (reescrito: 134 checagens,
e 14 perturbações numa cópia acendem todas).*

| o que mudou no livro | o que mudou na ficha |
|---|---|
| seis Caminhos: entrou o **Incursor** (6 + 4 de vida, 6 PE, Acrobacia · Intuição, as treze categorias) | menu de Caminho com seis, tabela de Caminhos da DADOS escrita pelo catálogo (a vida e o PE da FICHA leem a faixa nova), o treino de arma do Incursor |
| o Bastião treina `Atletismo` · `Provocar` | a perícia fixa marcada sozinha |
| dezoito Trilhas, dez com nome novo | menu de Trilha; a Empunhadura do Arremate virou Arma Condutora (Condutor Armado), e o Treino de Combate (Parceria) entrou no mesmo aviso |
| `Incapacitado` virou `Guarda Aberta` | menu de condição |
| Passiva virou **Talento**, Classe Passiva virou **Categoria de Efeito**, Passiva Livre virou **Expressão da técnica** | os textos e rótulos da FICHA AMALDIÇOADA e do menu rápido (CP → CE); as chaves internas continuam `passivas` e `classe_passiva` |
| a Restrição da Classe 0 não devolve mais o dado | a conta da Classe 0 |
| Salto, Queima e **Estilhaço** acrescentam dados; o Remate conta 25% no teto de 4 × Classe | a checagem do teto do feitiço |
| a Técnica Máxima monta com 8, 12 e 16 pontos (eram 8, 8 e 12) | a tabela da DADOS_AM, lida do livro |
| o Toque fica em 1,5 m também na Classe 0; a Onda vai a raio 4,5 m nas Classes 6 e 7; o último degrau de distância é "visão a olho nu" | o alcance das cartas |
| arma empunhada sem a Força: deslocamento pela metade e **sem Destreza na Defesa**; uniforme ou escudo sem a Força: **sem a proteção dele** | a FICHA PESSOAL reescreve o DESLOCAMENTO e a DEFESA da FICHA |
| carga acima do limite: **não anda** (era a metade) | o DESLOCAMENTO vai a 0 m |
| o Volume é decimal (Traje 1 = 0,3; Broquel = 0,5; armas de 0,1 a 4) e soma sem arredondar | a carga |
| XP: desconto da semana até a 7ª e "metade da anterior"; arredonda para baixo **só no fim**, e o positivo menor que 1 vira 1 | o Total de cada missão (o múltiplo de 12,5 saiu do `fora_do_livro`) |
| os Legados viraram narrativo, de rolagem e de exceção; Reencarnado virou **Encarnado** | o catálogo, como o livro está hoje (ele avisou que as Origens ainda vão mudar) |
| as fontes de reserva temporária mudaram (Embalo, Refluxo, Proteger a Manifestação) | a A2 do `decisoes-ficha.json` |
| os vetos de combinação (Rápido, Reação, Atrasar, Parado, Armado, Carregar) estão na tabela de Combinar peças | a A3, com sete pares |

*Conferido pelos validadores da bateria, cada um posto no texto novo; os arneses de decisão, de delta, de invocação, da
pessoal e do feitiço passam com as perturbações novas. A prova da conta da FICHA AMALDIÇOADA deixou de ser os 33
feitiços prontos (o livro novo não tem a tabela) e passou a ser os **10 exemplos de montagem** que o livro imprime, cada
um com a frase do resultado conferida: Fio de Arrasto, Peso nas Mãos, Corte Medido nas Classes 2, 3 e 5, o Salto de
exemplo, a Rede de contenção, o Projétil e a Aura com Fura, e o Corte de ruptura. Os dez saem iguais na planilha e no
`conferir_feitico.py`.*

**O que fica para ele, e fica fora desta rodada:**

- **Montar no Sheets** *e conferir o Incursor no menu, a DEFESA com arma pesada sem a Força e a carga acima do limite.*

**O que ele decidiu depois, ainda em 04/10/2026, e já está na ficha:**

- **A vida inicial da Vanguarda: "Toda vida inicial é a máxima do dado".** *A tabela de Características dela no livro
  reconstruído só traz "Vida por nível 5". O ganho por nível é a média do dado para cima, e os cinco Caminhos que o livro
  numera obedecem (12/7 é d12, 8/5 é d8, 6/4 é d6); 5 por nível é o d8, então a Vanguarda começa com 8. O número não
  mudou, mudou a fonte: o `fora_do_livro` do catálogo guarda a regra, e o `conferir-catalogo.py` confere os seis
  Caminhos contra ela. A checagem antiga só via se o catálogo e o `fora_do_livro` batiam entre si, e ficava verde com 10
  nos dois; a nova acende.*
- **A troca de duas perícias por arma: "Até duas armas, ja q todo caminho da no máximo duas pericias".** *O livro diz
  "pode trocar duas das cinco perícias por treino em uma arma específica", sem dizer quantas vezes. A ficha já fazia
  assim desde a extensão de 17/09/2026 (o menu vai até "2 armas (-4 pericias)"); agora a decisão está registrada.*
- **A falha e a posição da semana na mesma missão: "Sim, falta colocar as duas opções".** *O livro aplica as duas ("Sua
  terceira missão da semana era longa e terminou em falha com metade da recompensa. A conta é 200 × ½ × ½ = 50 XP."). O
  menu de desconto da FICHA PESSOAL ganhou, para cada posição que paga menos que cheio, a versão com falha pela metade
  dela (da "3ª · 50% · falha", que paga 25%, à "7ª · 3,125% · falha"); a "Falha · metade" continua para as duas
  primeiras. A `regressao-ficha-pessoal.py` passa todas as combinações pela planilha e confere o exemplo do livro.*

**Achado na bateria final:** *a troca da faixa dos Caminhos na FICHA (`DADOS!$N$5:$U$10`, para caber o Incursor) passou o
escape do `re.sub` para dentro da fórmula, e a vida e o PE da FICHA davam `Err:508`. Só a `regressao-kaori-na-ficha.py`
viu, porque as outras comparam o script com a planilha gerada, e os dois saíam quebrados iguais. Consertado no
`dados_catalogo.py`, e o `conferir-ficha-xlsx.py` passou a reprovar fórmula com barra invertida.*

**Fica para outra rodada:**

- **A ficha da invocação** (`ficha-invocacao/`) *segue o capítulo 16 da v0.251. O livro reconstruído reescreveu as
  invocações e trocou as Trilhas do Evocador; refazê-la é uma rodada própria, e ele decidiu em 04/10/2026 que fica para outra parte do trabalho ("pode deixar a reconstrução das invocações na ficha para depois mesmo, isso irei fazer em outra parte"). O `invocacao.json` declara a pendência, e
  o `conferir-invocacao.py` acende se a declaração sair.*
- **A ficha .docx da Kaori** *é de 07/09 e marca Intimidação. O `conferir-kaori.py` passou a ler o quadro da Kaori no
  livro, que vence a .docx onde os dois trazem o campo.*

**Achado em 06/10/2026, e consertado: o `comparar-ficha-01.py` saía vermelho desde esta rodada.** *Com o `original.xlsx`
no lugar (a exportação de 17/09/2026), ele terminava em "22 DIFERENÇA(S) NÃO EXPLICADA(S)", todas da tabela dos
Caminhos: vinte células de `DADOS!N4:T10` (a coluna `O`, que era o dado e virou os atributos naturais; `T5`, o Provocar;
as linhas 8 e 9, com o Emanador antes do Evocador; a linha 10, do Incursor) e as duas fórmulas da `FICHA` que leem a
faixa (`J26` e `J30`, de `$U$9` para `$U$10`). Ninguém viu porque do B36 ao B39 a bateria rodou sem o `original.xlsx`,
que é gitignored e só mora no checkout principal, e o comparador parava em "falta ficha-v01/original.xlsx".*

**As causas são duas, e nenhuma das 22 é mudança indevida.** *(1) A limpeza 8 só aceitava célula das colunas `A` a `L`
(a trava de 15/09 contra a coluna `AB`), e a tabela dos Caminhos mora de `N` a `T`: o `dados_catalogo.valores()` já a
trazia, e a regra a barrava. (2) O `monta.py` troca a faixa nas fórmulas da `FICHA` e o comparador não refazia a troca;
como a ficha automática embrulha essas duas em `IFERROR` depois, a limpeza 12 dele esperava a fórmula com a faixa de
antes. As mudanças foram conferidas uma a uma: a `FICHA` lê a tabela por `VLOOKUP` pelo nome do Caminho, nas colunas 3, 4
e 5; o `Codigo.gs` lê pelo cabeçalho ("Caminho", "perícia fixa"); nada lê a coluna `O`; e a ordem das linhas é a do menu
e a do livro (Bastião, Vanguarda, Guia, Emanador, Evocador, Incursor).*

| peça | o que mudou |
|---|---|
| `ficha-v01/dados_catalogo.py` | `e_dos_caminhos` (a célula é da tabela), `com_a_faixa` e `trocas_na_ficha` (o que o `troca_na_ficha` aplica): uma função, dois leitores. O que o `monta.py` escreve não mudou (o `Ficha.gs` e o `Habilidades.gs` saem iguais) |
| `comparar-ficha-01.py` | refaz a troca da faixa na ordem do `monta.py` (depois do índice, antes do TR) e ganha duas regras na limpeza 8: a célula da tabela dos Caminhos com o valor do catálogo, e a fórmula da `FICHA` em que só a faixa muda |
| `ficha-v01/extrair.py` e `layout.json` | a frase da limpeza 8 declara a tabela dos Caminhos e a faixa (a mesma frase nos dois; o extrator a escreve igual) |
| `conferir-ficha-xlsx.py` | duas checagens novas: a tabela dos Caminhos traz os seis do menu, na ordem, com os atributos, a vida, o PE e as perícias fixas do catálogo; e a vida e o PE da `FICHA` leem a tabela da primeira linha à última |

**Por que o `conferir-ficha-xlsx.py` entrou:** *o comparador só vê o que difere da exportação. A linha do Incursor
vazia e a faixa parada em `$U$9` saem iguais a ela, e nenhum validador cobrava o que a tabela diz (só o menu, na coluna
`A`). As duas checagens novas leem a tabela pelo cabeçalho, como o `Codigo.gs`, e o catálogo direto.*

**Conferido:** *o comparador fecha em IGUAIS, com 20 células da tabela e 2 fórmulas contadas, e as outras contagens
iguais às de antes do conserto. Dez defeitos plantados na ficha gerada: os oito que diferem da exportação acendem no
comparador (outra perícia em `T5`, o nome errado e outra vida na linha 10, `O6` em negrito, `U5` escrita fora da
tabela, a faixa até a linha 11, a coluna 2 no `VLOOKUP`), e os dois que voltam a ser iguais a ela (a linha 10 vazia, a
faixa de volta a `$U$9`) acendem no `conferir-ficha-xlsx.py`, com a Intimidação de volta em `T5`.* **Bateria, com o
`original.xlsx` copiado do checkout principal: os vinte e um de antes do B40 passaram, e, com o B40 já na `main` e o
conserto em cima dele, os vinte e dois passaram.**

**Fica como está:** *o `layout.json` é de uma exportação anterior à do `original.xlsx` de 17/09 (o extrator, rodado
hoje numa cópia, escreve outro arquivo: a exportação já traz a ficha automática montada). O comparador fecha assim desde
antes, e reextrair é rodada própria.*

### B37 · As cartas de Habilidades trazem o livro, numa coluna só — **FEITA em 05/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele disse que o texto cabe ("Cabe sim")**

*Pergunta do Mizuki sobre as cartas da seção 7 (B34), que nasceram escritas à mão e prontas para o livro: "nas caixas
de habilidades dos caminhos e trilhas, imagino que vai ser automatico / mas... vai caber? kkkk".*

**A medida.** A caixa de texto da carta tem 13 colunas de 28 px por 6 linhas de 21 px, em Roboto 10: umas 7 linhas,
perto de 340 letras. Medidas com a fonte, contra o livro reconstruído, as 109 cartas (6 Caminhos com 5 cada, 15 Trilhas
e as 3 rotas do Batedor com 4 cada, menos o nível 7 do Incursor, que é espalhado): o texto inteiro cabe em 4, a carta
típica pede 23 linhas e a maior, 133 (o nível 2, que é a mecânica central de cada Caminho e Trilha, pede 47 no meio).
O primeiro parágrafo cabe em 108, mas às vezes não diz o principal (o Chega Mais abria só com "O raio de Olhos Em Mim
aumenta para 9 m."). Aumentar a caixa não dava.

*A primeira versão, abaixo, foi a de três cartas por fileira com o resumo; a coluna única, mais abaixo, substituiu o
resumo pelo texto inteiro.*

**O que ele escolheu:** *"B - mas dando permissão para o jogador apagar o texto e colocar oq preferir"*: o nome e o
resumo do livro na carta, o texto inteiro na nota. E, perguntado no mesmo dia: a rota do Batedor se escolhe no menu de
Trilha (*"No menu de Trilha"*), e o nome tem duas linhas (*"Nome em duas linhas"*). A Rajada Marcial do Pugilista, que
o livro dá no nível 7 e que "Não acrescenta um novo degrau de Trilha no nível 7", vai na carta 7 do Caminho: *"No caso
do pungilista, o nv7 seria do caminho mesmo, sei que é uma trilha ligada a um nv do caminho, mas é aonde pensei"*.

**Como ficou:**

| peça | o que faz |
|---|---|
| `ficha-v01/extrair_habilidades.py` | lê do `manual.txt` o nome, o resumo e o texto de cada habilidade, e grava o `habilidades-do-livro.json`. O começo de cada uma é a marca do livro ("Nível N:", "Nível N.", o título "Nível N — Nome", um título com "nível N" ou com o nome); cada marca abre um trecho, e o trecho vai para a habilidade dona dela (o Pugilista intercala o nível 7 no meio do 2). O resumo é o primeiro parágrafo; se ele é curto (menos de 80 letras) ou só a linha de ficha ("Reação + 2 PE."), leva o seguinte junto, e tudo fica em frases inteiras até 330 letras: com a fonte, todos cabem em 6 linhas, uma de folga. O nome vai inteiro até 75 letras (os de até 73 cabem nas duas linhas; os de 84 ou mais pedem três); acima, "as primeiras e mais N", em 3 nomes do nível 2. `--confere` refaz e compara, e todo texto gravado tem de estar no manual |
| `ficha_automatica.trilhas_do_menu` | o menu de Trilha com o Batedor aberto nas três rotas ("Batedor · Yumi"), lidas dos títulos do livro; a Vanguarda passa a ter 5 entradas, e o menu, 20 |
| `ficha-v01/habilidades.py` | publica na DADOS_AM o endereço do nome e do texto de cada carta (ADDRESS, que anda com a planilha), põe o nome em duas linhas (31,5 pt) e escreve o `apps-script/Habilidades.gs` |
| `apps-script/Habilidades.gs` | o texto do livro, 111 habilidades (a 111ª é a carta 7 do Incursor com a Rajada Marcial). Mora num terceiro arquivo do Apps Script porque são uns 220 KB, e o `Ficha.gs` iria a 950 KB, acima do teto de 900 KB que o `conferir-ficha-xlsx.py` guarda; a montagem também não ganha 111 células de texto longo |
| `Codigo.gs`: `habilidadesDaFicha_`, `cartasDaFicha_`, `habilidadeQueFica_` | quando o Caminho ou a Trilha mudam, escreve o nome e o resumo como valor solto (não fórmula: o `devolverConta_` devolveria a conta por cima do jogador) e o texto na nota. Só reescreve a carta vazia ou ainda com um texto do livro daquela carta; o que o jogador escreveu fica, e a nota continua sendo o livro. Apagar a carta deixa ela vazia, e ela volta a encher na próxima troca de Caminho ou de Trilha |

**Conferido:** pela `regressao-amaldicoada.py` (o `--confere`, o endereço de cada carta, o nome em duas linhas, o
`Habilidades.gs` igual ao gerador e abaixo do teto, todo Caminho e toda Trilha do menu com as cartas completas, o menu
com as rotas do livro, a carta junta do Pugilista, e o nome e o resumo dentro da medida); pelo `regressao-delta.js` (a
conta do script contra o livro inteiro: todo Caminho com cada Trilha dele, a troca, o que o jogador escreveu, a carta
apagada, sem Caminho, o Pugilista); e pelo `regressao-construir.js`, na planilha montada, pelo onEdit de verdade. O
`arnes-delta.py` planta 6 defeitos novos (vai a 37), o `arnes-pessoal.py` 3 (vai a 54) e o `arnes-amaldicoada.py` 3 (vai a
63); todos acendem. *O do nome em uma linha só passava calado na primeira rodada: a checagem media a altura contra a
constante do próprio gerador, e mudar a constante mudava a checagem junto. Agora ela mede contra a linha comum da FICHA
(o dobro de 15,75 pt).*

**Fica para ele, no Sheets:** colar o `Habilidades.gs` (o `COMO-SUBIR.md` virou "Colar os três arquivos"); ver a
altura da caixa (ver a coluna única, abaixo); e ver se o projeto aceita os três arquivos juntos (o teto de ~1 MB que o projeto usa é por arquivo, e as fontes que
achei falam em 50 MB por projeto, nenhuma delas oficial).


**A coluna única, no mesmo dia.** *Pedido dele depois de ver a primeira versão: "faça ser apenas uma coluna ao invés de
três / assim o texto vai ter bastante espaço, mantenha uma boa altura em linhas pra cada carta e vemos se agora cabe
tudo. Não só isso, como n esqueça do espaçamento de uma linha entre uma carta e outra".* Na largura da seção (D a AT,
1.204 px), o texto inteiro pede 9 linhas na carta típica, mas o nível 2 vai a 62 (o do Evocador). Medido: altura igual
de 15 linhas cabia 83 de 111 (a seção iria a uns 170 linhas); do tamanho da maior de cada nível, 111 de 111 e uns 287.
Ele escolheu *"Acompanha a Escolha, mas ainda tendo a caixa retratil da descrição"*, e pediu o texto legível: *"n
esqueça de tentar deixar de forma legivel, espaçar os paragrafos e talz"*.

| o que mudou | como |
|---|---|
| a carta | a largura da seção: a etiqueta e o nome numa linha, a caixa do texto em 4 linhas, num grupo que abre e fecha (nasce aberto), e uma linha vazia antes da carta seguinte. A seção vai de 37 para 77 linhas (da 88 à 164), e o menu rápido começa na 165 |
| o texto | o texto inteiro do livro, na carta; o resumo e o nome encurtado saíram (o nome inteiro cabe numa linha: o maior tem 685 de 1.114 px). Legível: uma linha em branco entre os parágrafos, a tabela e a lista inteiras, e os subtítulos do livro numa linha própria, em negrito (texto rico, `setRichTextValue`). Sai a marca "Nível 7: Ataque Extra." do começo, que a etiqueta e o nome já dizem |
| a caixa estica | o `linhasDoTexto_` conta as linhas pela largura de cada letra da Roboto 10 (`ficha-v01/larguras-roboto-10.json`, do `medir_fonte.py`: somar as letras dá a medida da frase com 0,16% de diferença no meio e 0,56% no pior caso), e o `alturaDaCaixa_` divide a altura pelas 4 linhas da caixa (no texto mais longo, uns 285 px cada, longe de qualquer teto de altura de linha). Estica quando o Caminho ou a Trilha mudam e quando o jogador escreve numa caixa, as livres inclusive |
| a nota | só aparece quando o texto da carta não é o do livro: aí ela mostra o livro |

**Conferido:** o `regressao-delta.js` (70 checagens: o script conta as linhas dos 111 textos igual ao gerador em
Python, a caixa comporta o texto e sobra só o arredondamento, o negrito cai exatamente nos subtítulos, os parágrafos vêm
separados); o `regressao-construir.js` (pelo onEdit de verdade: as cartas, a altura de cada caixa, o negrito, o texto do
jogador sem negrito e com o livro na nota, a caixa livre que estica); e a `regressao-amaldicoada.py` (a largura da
seção, a linha vazia entre as cartas, o grupo que abre e fecha, a medida do `Habilidades.gs` igual à das colunas da
planilha, e toda letra do livro na tabela). Os arneses ganham os defeitos da coluna única: 65 no `arnes-amaldicoada`, 57
no `arnes-pessoal` e os do `arnes-delta`. O `medidas/ver-aba.py` desenha as cartas com o livro e a altura que o script
dá, e passou a respeitar as quebras de linha do texto (o Sheets respeita).

**Fica para ele, no Sheets:** a altura da linha de texto é estimada (18 px por linha de Roboto 10); se sobrar ou faltar
espaço embaixo do texto, o número mora no `LINHA_PX` do `habilidades.py`.

**O nível 7 da Vanguarda, no mesmo dia.** *O Mizuki notou que a Vanguarda era o único Caminho com uma habilidade só no
nível 7 ("o nv7 do vanguarda é o unico caminho com só uma habilidade, né?") e escreveu a segunda: "Execução Preparada:
1× por Sequência, ao Concluir depois de duas ou mais Conduções, imponha −1 a um TR adicional da Conclusão."* Ela entrou
primeiro no livro (D42 do `JJK---Project`, que o registra em `revisao-interfaces/CORRECOES-APLICADAS.md`), e daí na ficha:

| o que mudou | como |
|---|---|
| `manual.txt` | tirado de novo do `LIVRO-COMPLETO.md` (hash `e747cf74…`). Só mudaram a linha da tabela da Vanguarda ("Ataque Extra e Execução Preparada") e o parágrafo novo |
| a carta 7 da Vanguarda | "Ataque Extra e Execução Preparada", com os dois textos |
| o subtítulo | o extrator tirava a marca "Nível 7: Ataque Extra." inteira do começo do parágrafo, porque a etiqueta e o nome da carta já diziam. Com duas habilidades na mesma carta, a segunda ficava sem nome. Agora, quando a carta junta mais de uma e o parágrafo abre com o nome de uma delas, o nome fica, como subtítulo em negrito, como já ficava no Bastião 7, que o livro escreve com títulos. Mudou em três cartas: Vanguarda 7 (Ataque Extra e Execução Preparada), Vanguarda 2 (Sequência de Condução e Escola de Arma) e Executor 2 (Finta de Execução) |

**Conferido:** a `regressao-amaldicoada.py` ganhou a checagem do subtítulo. Ela acha no `manual.txt`, na seção de cada
Caminho e Trilha, os parágrafos "Nível N: Nome." de carta que junta habilidades, e exige o nome em subtítulo seguido do
texto, no `Habilidades.gs` e no que o extrator tira hoje (são 5 nomes, entre eles a Execução Preparada). O
`arnes-amaldicoada.py` vai a 66: o extrator que volta a tirar o nome acende a checagem nova.

### B38 · A foto da `CARTEIRA` na `FICHA PESSOAL`, e o nome da técnica da `CARTEIRA` na `FICHA AMALDIÇOADA` — **FEITA em 05/10/2026; a foto ele testou no Sheets (07/10/2026: "B35 funciono normalmente", respondendo sobre a ligação da foto com a `FICHA PESSOAL`); o nome da técnica ele testou no mesmo dia: "Funciona"**

*Pedido dele em 05/10/2026: "uma coisa q é bom implementar na ficha e notei q faltou / 1 - A imagem que for colocada
na carteira aparecer no ficha pessoal / 2 - Nome da técnica aparecer na ficha amaldiçoada". As duas seguem o que a
ficha já faz com o nome do personagem: a `CARTEIRA` é onde se escreve, e as outras abas mostram.*

**A foto (a ligação que o B35 deixou para depois).** A caixa FOTO DO PERSONAGEM da `FICHA PESSOAL` virou
`=CARTEIRA!$C$8`, o canto da caixa da foto que a `CARTEIRA` declara (`foto`, do `moldura_foto.py`, o mesmo endereço que o
`Codigo.gs` usa para ancorar a caixa da paleta). *A documentação do Google não diz se uma fórmula que aponta para uma
célula com imagem inserida mostra a imagem: procurei em 05/10/2026 e só achei a função `IMAGE`, com link, e um relato de
que o `IMPORTRANGE` não traz imagem inserida de outro arquivo, que é outro caso.* Por isso a caixa ficou fora da trava:
se a foto não aparecer, o jogador insere a mesma foto nela, por cima da conta, sem aviso. A nota diz isso.

**O nome da técnica.** Perguntado, ele escolheu *"Espelha a CARTEIRA"*: o jogador escreve uma vez, no campo TÉCNICA
DECLARADA da `CARTEIRA`, e a caixa NOME DA TÉCNICA da `FICHA AMALDIÇOADA` mostra. Ela é referência pura para uma conta da
`DADOS_AM` (`=CARTEIRA!$O$27&""`), como toda caixa calculada da aba: quem escreve por cima recebe a conta de volta pelo
onEdit. O aviso dessa caixa é outro: *"O nome da técnica vem da CARTEIRA, e a caixa voltou. Para mudar, escreva na
TÉCNICA DECLARADA de lá."* A aba declara a caixa em `da_carteira`, e o `devolverConta_` escolhe o aviso por ela. O
campo da `CARTEIRA` é achado pelo rótulo (a caixa logo abaixo de "TÉCNICA … DECLARADA"), e o gerador para se não houver
caixa ali.

| peça | o que mudou |
|---|---|
| `ficha-v01/ficha_pessoal.py` | a caixa da foto aponta para a foto da `CARTEIRA` e entra nas `livres` (fora da trava); a nota nova |
| `ficha-v01/ficha_amaldicoada.py` | `campo_da_tecnica`, a caixa NOME DA TÉCNICA com a conta, a nota, e `da_carteira` na aba |
| `ficha-v01/monta.py` | passa `da_carteira` para o `Ficha.gs` |
| `apps-script/Codigo.gs` | o `devolverConta_` escolhe o aviso da `CARTEIRA` |

**Conferido:** o `conferir-ficha-xlsx.py` (uma caixa só da `FICHA PESSOAL` aponta para a foto declarada, do tamanho de uma
foto, com a nota e fora da trava); o `regressao-pessoal.js` (a trava cobre toda fórmula da aba, menos o Volume dos
itens, o que mora em grupo e, agora, só a fórmula que é exatamente a referência da foto); a `regressao-amaldicoada.py`
(a caixa aponta para a conta, a conta lê o campo achado pelo rótulo na planilha gerada, a aba declara a caixa, e a Kaori,
com "Peso Emprestado" escrito na `CARTEIRA`, mostra o nome depois de recalculada no LibreOffice); e o
`regressao-construir.js` (escrever por cima devolve a conta, e o aviso manda escrever na `CARTEIRA`, e o da caixa comum
não). Os arneses ganham: o `arnes-moldura.py` 2 (a caixa que deixa de apontar e a que entra na trava; vai a 11), o
`arnes-pessoal.py` 2 (o aviso que esquece a `CARTEIRA` e a aba que não declara a caixa; vai a 59) e o
`arnes-amaldicoada.py` 3 (a caixa escrita à mão, o script que não sabe de onde ela vem, e o campo uma linha abaixo, que
para o gerador; vai a 69). Todos acendem.

**Fica para ele, no Sheets:** inserir uma foto na caixa FOTO da `CARTEIRA` e olhar a `FICHA PESSOAL`. Se a foto não
aparecer, me avise: o plano B é o jogador inserir nas duas, e o C é o script copiar a imagem (o Apps Script lê e grava
imagem de célula, pela documentação dele).

### B39 · As duas aptidões de graça do menu rápido mostram o valor — **FEITA em 06/10/2026 e MONTADA NO SHEETS: em 07/10/2026 ele disse "Certinho"**

*Pedido dele em 06/10/2026: "na ficha, tem as aptidões (e lapidações) base, seria bom se o mecanico (pelo menor o
valor), estivesse incluso / ja q é um acesso rapido da ficha amaldiçoada".* **As cartas das duas de graça, no menu rápido
da `FICHA` (seção 8), traziam só o "Do livro:", e o valor morava na `FICHA AMALDIÇOADA`, nas caixas do cabeçalho de
APTIDÕES E REFINO.** *Agora a carta abre com o mesmo valor, e depois vem o texto do livro:*

- **Cobrir-se de Energia:** *"Proteção 1 · Reação de Cobrir-se: RD 1 por 2 PE. Do livro: …"*
- **Canalizar Energia:** *"+1d4 na arma. Do livro: …"*

*Na Restrição Celestial sem energia são a Defesa sem Armadura e o Estímulo Muscular, com os mesmos números na
Lapidação, e a reação vira "Reação da Defesa".* **A carta lê as três caixas da `FICHA AMALDIÇOADA`, e não refaz a conta:**
*a regra continua num lugar só.* Como o menu é montado antes da aba, os três endereços passaram a nascer no layout, como o
do Refino, e a aba confere que a caixa sai neles.

| peça | o que mudou |
|---|---|
| `ficha-v01/ficha_amaldicoada.py` | `apt_cobrir`, `apt_canalizar` e `apt_reacao` no layout, e a aba confere que a caixa sai neles |
| `ficha-v01/menu_rapido.py` | o texto das duas cartas de graça abre com o valor |
| `apps-script/Ficha.gs` | as duas fórmulas novas (e só elas: o resto do arquivo saiu igual) |

**Conferido:** a `regressao-amaldicoada.py` refaz o valor pelo refino de cada uma das 20 fichas de teste, nas quatro
rotas, e confere a carta recalculada no LibreOffice (354 checagens, todas passando); o `arnes-amaldicoada.py` ganha 2
(a carta volta a mostrar só o livro, e a do Canalizar mostra a proteção do Cobrir-se; vai a 71), e os dois acendem.
**Dos vinte e um, vinte passam; o `comparar-ficha-01.py` pede o `original.xlsx`, que é a exportação da planilha viva e não
está no repositório.** *Rodado numa máquina de nuvem com o Python 3.12 (o 3.11 não lê as f-strings do gerador), o
LibreOffice Calc instalado na hora e as fontes baixadas do Google Fonts. O `Ficha.gs` e o `Habilidades.gs` saíram iguais
aos commitados antes da mudança; o `.xlsx` e a arte da carteira, não (outra versão de `openpyxl`, de Pillow e das
fontes), e por isso não foram subidos daqui: rode o `monta.py` na sua máquina para o `.xlsx` acompanhar.*

**Fica para ele:** colar o `Ficha.gs` novo no Sheets e olhar o menu rápido.

**Achado de passagem, para depois:** o `manual.txt` saiu do livro de antes da D43 (`manual-fonte.json`, hash
`e747cf74…`). O livro de hoje tem a D43 (Condição, Prende e Cerca pedem TR), o nome Ciclo Maldito e a D44 (a Execução
Preparada da Vanguarda com −2): a carta 7 da Vanguarda ainda diz −1. Puxar o livro novo é rodar o `extrair-manual.py` e
pôr o catálogo em dia, que é uma passada própria.


### B40 · A aba `INVOCAÇÕES`, a invocação refeita depois do livro reconstruído — **CONSTRUÍDA E MONTADA NO SHEETS em 07/10/2026 (quatro etapas, no fim desta seção): ele testou a grade, o inventário, a devolução da conta e a ficha sem travas. Ficam com ele a regra da arma sem a Força no livro, a lista da revisão e o destino da `ficha-invocacao/` antiga**

*Pedido dele em 06/10/2026: "precisamos olhar o como fazer a ficha de invocação após a atualização do sistema", com
protótipos antes de aplicar. É a pendência que o B36 deixou ("pode deixar a reconstrução das invocações na ficha para
depois mesmo, isso irei fazer em outra parte").*

**O que o livro mudou.** *A invocação deixou de ser ficha derivada do dono (orçamento da Trilha, Traço, Comando, Investir,
Sintonia) e virou **entidade**, com ficha própria: 9 pontos de atributo e 1 por marco, ataque e CD com a maestria do
invocador, três Famílias abertas com uma Livre, uma básica, especiais montadas por Classe e pontos, talentos por marco,
quatro formas de aquisição (capítulo 17), e as regras de campo num capítulo à parte (16). Da `ficha-invocacao/` de
antes, que segue a v0.251, quase nada serve; ela e os três validadores dela não foram tocados nesta rodada.*

**O estudo, em cinco rodadas** *(`mockup/invocacao-estudo.html`, `python3 mockup/estudo_invocacao.py`).*

| rodada | o que eu trouxe | o que ele disse |
|---|---|---|
| 1 | quatro formas, numa página de site com campos soltos | *"Eu n gostei de nenhuma das opções ... algo mais, visualmente atrativo, semelhante as outras paginas ... tendo como colocar a imagem da invocação, nome e afins"*, e o estudo *"no formato de ficha de excel/planilhas"* |
| 2 | a aba na grade da planilha: A deitadas e empilhadas, B deitadas lado a lado, C em pé | *"Que tal fazer a A+B? umas 2-3 colunas com a mesma lista que temos na A, ai umas 5-6 linhas ... mantem o 'conjunto' ali na esquerda"*; Buff/Debuff *"que nem no sistema da ficha principal"*; Liberação Máxima, Expansão e Técnica Máxima, *"n precisa de automação para liberar ou n essas abas, so deixa oculto"* |
| 3 | a grade de fichas, o conjunto à esquerda, o Buff/Debuff e os trunfos | *"2 x 6 acho q fica bom, so recomendo aumentar a largura da imagem"* |
| 4 | a foto com 15 colunas | *"Deixa um pouco mais largo e ta bom assim, de uma avaliada se falta nada na ficha e ta aprovado"* |
| 5 | a foto com 17 colunas, e a conferência contra o livro | *"aprovado"* |

**O que a conferência contra o livro acrescentou, e ele aprovou:** *o tipo de dano e a resolução (ataque ou Teste de
Resistência) em cada habilidade; o equipamento, com o limite de carga de 5 + Força; o bônus de cada perícia treinada; a
reserva da domada e a carga do talismã; cinco menus de Família, porque as Trilhas do Evocador abrem uma ou duas a mais; o
grupo fechado "Repertório da Trilha", com três cartas e três talentos de Categoria 1 para as escolhas a mais da
Invocação Principal e do Repertório do Conjunto; e, no conjunto, o Aprimoramento de Vínculo, a beneficiária, os três usos
da rodada e o limite de quatro ativas em Múltiplas Invocações.*

**A primeira etapa da construção: uma ficha, para medir.** *Combinado com ele antes de aprovar: montar uma ficha no
gerador, medir o `construir()` no Sheets, e só então repetir para as doze. `ficha_invocacoes.N_COLUNAS` e
`N_FILEIRAS` estão em 1 e 1; a grade fechada é 2 e 6.*

| peça | o que é |
|---|---|
| `ficha-v01/extrair_invocacao.py` e `ficha-v01/invocacao-do-livro.json` | o que a aba lê do livro e o catálogo não tem: a progressão da entidade, os pontos e o PE por Classe, as Formas, o alcance e a área, os talentos, os tipos, as aquisições, os trunfos da domada, as Trilhas e os aprimoramentos do Evocador. 53 frases do livro conferidas palavra por palavra, cada uma com a conta que a aba tira dela, e os dois exemplos do capítulo 17 |
| `ficha-v01/ficha_invocacoes.py` | **a limpeza 29.** A aba `INVOCAÇÕES`, depois da `FICHA AMALDIÇOADA`, e a aba oculta `DADOS_INVOC`, depois da `DADOS_AM`: as tabelas do livro, uma linha de conta por ficha e uma por carta de habilidade. As Melhorias, as condições, as Restrições e os pares proibidos são os da `FICHA AMALDIÇOADA` (`ficha_amaldicoada.regras()`) |
| `apps-script/Invocacoes.gs` | **o quarto arquivo do Apps Script.** Com uma ficha o `Ficha.gs` foi de 760 para 950 KB, acima do teto de 900 KB por arquivo; com as doze passaria de 1,3 MB. As duas abas saem do `Ficha.gs` e moram aqui. O arquivo só declara a lista delas, e o `juntarAbas_` do `Ficha.gs` as põe no `ABAS`, cada uma depois da aba que ela nomeia, no arquivo que carregar por último, porque o Apps Script não promete a ordem dos arquivos. Sem ele no projeto a ficha é montada sem as duas abas |
| `apps-script/Codigo.gs` | o `onEdit` devolve a conta de quem escrever por cima de uma caixa calculada da aba, como na `FICHA AMALDIÇOADA` |
| `regressao-invocacoes.py` | **entra no `rodar-tudo.sh`, que passa a ter vinte e dois.** Os exemplos do livro com o número que o livro imprime, o Buff/Debuff, o que a ficha recusa, e 18 fichas sorteadas com 157 cartas (77 fora da regra, de propósito) contra a regra escrita de novo em Python |
| `medidas/ver-aba.py --aba "INVOCAÇÕES"` | desenha a aba com o Cão de sombra do livro |

**O que mudou do estudo, e por quê.** *O estudo foi desenhado numa grade de colunas finas, como os outros. Com doze
fichas a aba teria 120 mil células nessa grade, e a troca de tema é feita célula a célula. Como a `FICHA AMALDIÇOADA`,
cada coluna tem a largura do que guarda:*

- **A ficha são três blocos de cinco colunas de 96 px** *(a foto, os números e a mesa), que são também as três cartas de
  habilidade de cada fileira. Cada carta fica com 480 px, a largura das da `FICHA AMALDIÇOADA`; no estudo ela tinha 364,
  o tamanho que ele achou "mt amassadinho" lá. A foto fica com 480 por 399 px.*
- **O Buff/Debuff fica embaixo do número, e não ao lado**, *em toda caixa calculada: é o que deixa cada valor numa
  coluna só. O atributo mostra o total, os pontos embaixo e o Buff/Debuff embaixo dos pontos.*
- **A carta de habilidade ganhou a linha AMPLIAR**, *como a de feitiço: a mesma especial numa Classe maior, com o dano e o
  PE de cada Classe que o nível já liberou. É o "poderá ser ampliada para 4d8 por 6 PE" do Cão de sombra.*
- **A ficha ficou mais larga:** *1.496 px, contra 1.204 no estudo. Com uma ficha a aba tem 1.985 px (o
  `decisoes-ficha.json` guarda); com as duas colunas, perto de 3.500.*
- **A lista do conjunto ainda não leva até a ficha:** *é texto; a ligação pede o número da aba, e entra com a grade.*

**Conferido:** *a bateria inteira rodou em 06/10/2026 com o `original.xlsx`: dos vinte e dois, vinte e um passam, a `regressao-invocacoes.py` entre eles (os exemplos do livro batem um a um, e as 157 cartas sorteadas também). O que sai vermelho é o `comparar-ficha-01.py`, pelas 22 diferenças do B36 descritas abaixo, que são de antes desta rodada. O `construir()` roda inteiro no Sheets de mentira com a aba nova, nas duas ordens de carga dos arquivos, e a troca de tema passa a aba em passos, como a `FICHA`. O `Ficha.gs` ficou com 760 KB e o `Invocacoes.gs` com 170. Nada disto rodou no Sheets de verdade.*

**O que fica para ele:**

- **Colar o `Invocacoes.gs` no projeto do Apps Script, como quarto arquivo** *(e o `Ficha.gs` e o `Codigo.gs` novos),
  rodar o `construir()` e mandar o registro de tempo: é ele que diz se as doze fichas cabem, e em quantas execuções.*
- **Olhar a aba no Sheets:** *a foto inserida na caixa, o Buff/Debuff embaixo do número, os grupos de linhas e os dois de
  colunas (o conjunto e a coluna de fichas), e os menus de Melhoria, que só trazem as Famílias abertas da ficha.*

**O que falta fazer aqui, depois da medida:**

- *a grade de 2 × 6, com as fileiras de fichas vindo por cópia de formato;*
- *a ligação de cada linha da lista do conjunto com a ficha dela;*
- *um arnês para a aba, como o `arnes-amaldicoada.py`;*
- *decidir com ele o que fazer da `ficha-invocacao/` e dos três validadores da invocação de antes.*

**Achado de passagem:** *o `comparar-ficha-01.py` já saía vermelho antes desta rodada, com o `original.xlsx` de
17/09/2026: 22 diferenças não explicadas na `DADOS` e na `FICHA`, todas do B36 (o Incursor na tabela dos Caminhos, o
Bastião com Provocar, a faixa `N5:U10`). Conferido numa cópia do commit `676f093`, sem nada desta rodada. Ele não
aparecia porque as últimas rodadas rodaram sem o `original.xlsx`.* **Consertado no mesmo dia: ver o fim do B36.**


#### B40, segunda etapa (07/10/2026): a medida dele, a grade de 2 × 6 e o retorno de quem leu a aba

**A medida, com uma ficha.** *Ele colou os quatro arquivos, rodou o `construir()` e mandou o registro: "Deu certinho,
apareceu aq". `FICHA PRONTA em 288s`, numa execução só. Abas criadas 62,9 s · CARTEIRA 5,2 · FICHA 38,5 · FICHA
AMALDIÇOADA 23,4 · **INVOCAÇÕES 8,0** · FICHA PESSOAL 8,2 · DADOS 5,1 · DADOS_AM 15,5 · **DADOS_INVOC 18,6** · GLOSSÁRIO
1,4 · menus 12,8 (350 menus) · travas 81,3 (70 travas) · o resto do acabamento 6. A planilha que ele exportou
(`Ficha - Era da Revolução.xlsx`) não tem erro de fórmula em nenhuma das duas abas da invocação.*

**O que a medida diz das doze fichas.** *Sobravam 72 s dos 360, e as doze fichas trazem dez vezes as células de uma:
a aba vai de 203 × 26 para 1.196 × 45 (54 mil células) e a `DADOS_INVOC` de 86 × 406 para 159 × 446 (71 mil). Pela
medida, a aba visível custa de 1,3 a 2,1 s por mil células e a oculta 0,5 a 0,6: a `INVOCAÇÕES` deve levar de 80 a 110 s
e a `DADOS_INVOC` uns 40. A montagem das abas sozinha fica perto dos 300 s, e com o acabamento passa dos 360. **Não cabe
mais numa execução.***

| o que mudou | por quê |
|---|---|
| **`N_COLUNAS, N_FILEIRAS = 2, 6`** no `ficha_invocacoes.py` | a grade que ele fechou. Doze fichas, 156 cartas de habilidade, 5.188 mesclagens, 1.093 faixas de menu |
| **as fileiras de fichas vêm por cópia** | a segunda fileira é o molde da terceira à sexta, em cinco trechos (o que fica entre as fileiras de cartas, que já eram cópia da primeira). A primeira não serve de molde, porque divide as linhas com o conjunto. A cópia vai coluna de fichas por coluna de fichas (`k[5]` do `copias`), porque a lombada do nome atravessa os trechos e o Sheets não copia meia mesclagem. O `compactar` do `emitir_gs.py` passou a exigir que as duas pontas de uma mesclagem estejam na MESMA cópia, e a diz qual lista não voltou quando o desenho não fecha |
| **a linha de cada carta na `DADOS_INVOC` é igual em todas** | o nível em que a carta abre e o título dela estavam escritos dentro da fórmula, e a coluna de erros sozinha pesava 535 KB. Agora saem das colunas `abre` e `tit`, e a fórmula é preenchida para baixo |
| **o `Invocacoes.gs` ficou com 437 KB** | com a grade ligada e nada mais ele saía com 1,2 MB, acima do teto de 900 KB por arquivo. O `Ficha.gs` tem 790 KB |
| **o `construir()` para sozinho, e o `continuar()` segue** (`ficha/modelo.gs.js`) | antes de começar cada aba ele estima o custo dela pela medida de 06/10 (2,4 ms por célula na aba visível e 0,7 na oculta, o pior de cada tipo com uns 15% a mais) e, se a conta passar de 300 s, guarda em que aba parou (propriedade `montagem_parada`) e pede o `continuar()`. A primeira aba de cada execução sempre é montada. O `acabar()` recusa rodar por cima de uma montagem parada, e o `construir()` do zero esquece a parada de antes logo no começo. Pela conta, são **duas execuções**: a primeira para antes da `DADOS_INVOC`, e a segunda faz ela, o `GLOSSÁRIO`, os menus e o acabamento |
| **a lista do conjunto leva até cada ficha** | a `DADOS_INVOC` publica a tabela de saltos (a caixa, o alvo e a célula do texto), e o `ligarSaltos_` do `Codigo.gs`, que já fazia os dez da `FICHA AMALDIÇOADA`, escreve as doze ligações no acabamento. O alvo é o número da lombada da ficha, que fica à vista com a fileira e a coluna fechadas. Quem escrever por cima de uma linha recebe a conta de volta, e a ligação é refeita na hora |
| **a régua da aba troca de cor em quatro partes** | a troca de tema tem 30 s por execução. A aba tem 7.810 faixas de borda e 25 chamadas, contra 8 da `FICHA AMALDIÇOADA`, e o passo dela sozinho passava do tempo num Sheets lento (o teste 8 da `regressao-paleta.js`). A aba com mais de 8 chamadas vai em partes (`borda:INVOCAÇÕES:0` a `:3`); as outras continuam num passo só, com o nome de sempre. A cor da aba vai em oito passos. **A troca de tema inteira fica bem mais longa** do que era com cinco abas |

**O retorno de quem leu a aba.** *Ele mostrou a aba a um amigo e trouxe os pontos durante a rodada:*

| o que ele disse | o que mudou |
|---|---|
| *"ele achou desnecessario ter o 'tarefa' na ficha, pq o player iria escrever algo q ele fala pro mestre na mesa assim?"* | saiu a caixa `TAREFA` |
| *"tira esse 'abre no' e coloca ou só o nível que nem o primeiro, fica mais bonitinho"* (o amigo, sobre a coluna dos talentos) | o rótulo de cada talento é sempre `NV 6 · CE 1`. Quem escolher um talento antes da hora continua vendo o aviso ao lado. O título da carta de habilidade ainda diz `ABRE NO NÍVEL`, e ele não falou dele |
| *"n tem necessidade dessas caixas q basicamente vc muda durante o turno, tipo movimento ali. reduzir, vida, modificadores, energia e essas coisas tudo bem"*; *"Básica do ciclo n faz sentido ter, estado, ordem, n faz sentido"*; *"pra q esse tbm"* (a faixa do Vínculo); *"mais coisa do turno"* (os três usos) | saíram de cada ficha o `MOVIMENTO` que resta, a `BÁSICA DO CICLO`, o `ESTADO` e a `ORDEM PENDENTE`; e do conjunto a `REAÇÃO COLETIVA`, o `DANO NO TURNO`, o `VÍNCULO`, o `APRIMORAMENTO DE VÍNCULO` com a beneficiária e os três usos da rodada. Sem o estado, o conjunto mostra o limite de ativas (`ATIVAS, NO MÁXIMO`: 2, ou 4 com Múltiplas Invocações) e não mais a contagem, e a lista e o título da ficha não dizem mais "em campo". O deslocamento com o Buff/Debuff embaixo já estava nos números da ficha, e por isso as duas caixas de movimento da mesa não foram aproveitadas |
| *"ideal o vida máxima ficar lado a lado com vida atual, vida temporaria e ter um redutor automatico, semelhante a ficha de player"* | a mesa abre com `VIDA ATUAL`, `VIDA MÁXIMA`, `TEMPORÁRIA`, `± PERDA / GANHO` e a reserva, e a barra embaixo, na largura inteira. A caixa de ± é do `onEdit` (`redutorDaInvocacao_`): digita −9, ela aplica na vida atual e se limpa, com a mesma conta da `FICHA` (`aplicaPasso_`: a perda gasta a temporária primeiro, e a vida não passa da máxima). Em branco, a vida atual está cheia. A `VIDA MÁXIMA` continua também nos números, com o Buff/Debuff dela. O teto da temporária (metade da máxima), que a `FICHA` prende, não foi posto aqui |
| *"ideal alongar a foto, ficar mt quadradinha achatada é dificil ed achar imagens, ser um pouco, n mt, mais alta que larga ajuda"* | a foto passou de 480 × 399 para **480 × 546 px** (26 linhas). As Famílias saíram de baixo dela e foram para baixo das perícias, no bloco dos números; as anotações e o corpo ganharam as linhas que sobraram na mesa. A ficha desceu só três linhas (198 por fileira) |
| *"a carga n funciona como escrito"*; e, quando perguntei de qual carga: *"carga, a q a invocação carrega, ela em si n pode carregar itens, lembra? precisa de caracteristica"* | saiu a caixa `CARGA MÁXIMA` dos números, que dava a entender que a entidade leva 5 + Força de Volume em itens. O livro (Invocações em campo): "Uma entidade carrega o que suas mãos permitem segurar"; "Transportar carga adicional ou personagens exige uma característica própria ... que ocupe um de seus talentos"; "Sem o talento, fica limitada ao que pode segurar e ao equipamento que pode vestir, dentro do mesmo limite". O limite fica só no título do equipamento, dizendo do que ele é (`EQUIPAMENTO · VESTE E EMPUNHA ATÉ 8 DE VOLUME`), e a nota da caixa diz que transportar pede a característica. O `TR TREINADO` foi para o lugar da caixa, ao lado dos quatro testes. Na conferência achei também um furo na carga do talismã: com ele carregado o `RETORNO` mostrava os 2 × Classe cheios, e o livro abate o que a carga adiantou ("o retorno custaria 8 PE ao todo: os 2 adiantados e mais 6 no retorno"). Agora mostra 6 |
| *"a ficha ta sem o nome nome, que é ciclo maldito e pode por a versão como 1.0, isso vale pra ficha toda"* | o `_meta.sistema` do arquivo de dados é `Ciclo Maldito` e o `_meta.versao` é `1.0`; o carimbo do `decisoes-ficha.json` acompanha. O cabeçalho de cada aba já lia o nome da `DADOS!F1`, e a lombada de cada aba, que vinha escrita da exportação (`PROJETO M`), passa a dizer o nome do arquivo de dados (uma limpeza no `monta.py`, com a diferença registrada no comparador). A versão vai ao Sheets com apóstrofo, como todo texto com cara de número, senão a célula ficaria com 1. O número da `CARTEIRA` passa a ser `Nº M-10-…`: o `M-` não foi mexido |
| *"8 de volume, tá certo isso? n era 5 + força? e n era ideal só ser uma versão 'menor' do inventario do jogador, aonde tem item equipado, item guardado (caso tenha possibilidade) e talz"*; e, das três formas que mostrei: *"pode ser a C, é mais simples, ai faz uma listinha maior de itens guardados, talvez até dividir em duas colunas"* | o 8 estava certo (5 + a Força 3 do Cão de sombra do exemplo). A caixa de texto do equipamento virou um inventário pequeno: três lugares fixos em uso (`MÃO 1`, `MÃO 2`, `VESTE`), cada um com o Volume ao lado, e a lista `GUARDADO · SÓ COM A CARACTERÍSTICA DE TRANSPORTE`, com seis linhas. O título soma as caixas de Volume e compara com o limite (`EQUIPAMENTO · 2,5 DE 8 DE VOLUME`); acima dele acende e diz `PASSOU DO LIMITE`. As linhas saíram das condições (7 para 5) e das anotações (12 para 6), e a ficha não cresceu. **A lista ficou numa coluna só:** as colunas do bloco têm os 96 px das cartas, e com cinco delas duas colunas iguais de item e Volume deixariam o nome do item em uma coluna de 96 px. A aba não tem menu de itens: o nome e o Volume são digitados |

**Conferido:** *a bateria inteira rodou até o fim em 07/10/2026, na versão da carga da entidade (`fb714ae`), com o `original.xlsx`: dos vinte e dois validadores, vinte e um passaram. O que saiu vermelho foi uma checagem da `regressao-amaldicoada.py` ("a aba nova não triplica a montagem"), e o defeito era da conta dela: contava uma cópia por destino na `INVOCAÇÕES`, e desde a grade de 2 × 6 cada destino é copiado uma vez por coluna de fichas (168 cópias na planilha, contra o teto de 133 que ela calculava; com as faixas na conta o teto é 172). Consertada a conta, e depois do inventário pequeno, rodaram de novo e passaram doze dos vinte e dois, os que leem a planilha gerada, o script ou este arquivo: `regressao-construir.js`, `regressao-invocacoes.py` (39 fichas em 19 planilhas, nos doze lugares, com os dois casos do equipamento), `conferir-ficha-xlsx.py`, `regressao-pessoal.js`, `regressao-amaldicoada.py`, `arnes-pessoal.py`, `comparar-ficha-01.py` (IGUAIS, fora as 13 limpezas declaradas), `conferir-decisoes.py`, `arnes-decisoes.py`, `regressao-delta.js`, `regressao-kaori-na-ficha.py` e `regressao-ficha-pessoal.py`; e a `regressao-paleta.js`, que não está na bateria. Os outros dez passaram na bateria e não foram rodados de novo depois do inventário. O `Invocacoes.gs` tem 446 KB.*

**Em 07/10/2026 ele montou a grade no Sheets: "rodou, a ficha salvou certinho".** *Não mandou os registros de tempo; a estimativa de custo de cada aba continua sem conferência contra o Sheets.*

**O que fica para ele:**

- **Colar os quatro arquivos de novo** *(`Ficha.gs`, `Codigo.gs`, `Invocacoes.gs` e o `Habilidades.gs`, que não mudou),
  rodar o `construir()` e, quando o registro terminar em `rode a função continuar()`, rodar o `continuar()`. Mandar os
  dois registros: eles dizem se a estimativa de custo está certa.*
- **Olhar a aba:** *a caixa de ± (digitar −5 numa ficha com nome), a lista do conjunto levando até cada ficha, a segunda
  coluna de fichas, que nasce fechada, e as fileiras 2 a 6, fechadas.*

**O que falta fazer aqui:**

- *~~um arnês para a aba~~ feito na terceira etapa, abaixo (`arnes-invocacoes.py`);*
- *decidir com ele o que fazer da `ficha-invocacao/` e dos três validadores da invocação de antes.*

#### A terceira etapa (07/10/2026, à noite): o retorno dele depois de montar tudo no Sheets

*Ele rodou o `construir()` e o `continuar()` com o inventário pequeno e passou a lista de testes que eu tinha pedido. O
`construir()` parou sozinho antes da `INVOCAÇÕES`, como desenhado; nesse dia o Sheets estava bem mais lento que na
véspera (abas criadas em **164,9 s**, contra 62,9; `FICHA` em 55,6 s, contra 38,5; `FICHA AMALDIÇOADA` em 37,6 s,
contra 23,4). Os registros do `continuar()` e do `acabar()` ele mandou depois, e estão na tabela abaixo.* **O que funcionou, nas palavras dele:** *o título e a lista
do conjunto preenchendo sozinhos, a caixa de ±, o inventário, as fichas fechadas, os erros das cartas, a troca de tema;
o Incursor no menu, a carga acima do limite, as cartas de Habilidades ("cabe sim"), o nome da técnica (B38:
"Funciona"), o menu rápido (B39: "Certinho") e a foto na `FICHA PESSOAL` (B35/B38: "funciono normalmente").*

| o que ele disse | o que mudou |
|---|---|
| *"1.3: Parou de funcionar, os links da ficha amaldiçoada também"* (a lista do conjunto e os saltos da linha 7 não levam a lugar nenhum) | **a causa: o `acabar()` não tinha sido rodado.** O registro do `continuar()`, que ele mandou depois, termina em `AS ABAS ESTÃO DE PÉ em 304s, MAS FALTA O ACABAMENTO: rode a função acabar()`; sem o acabamento a ficha fica sem saltos e sem a trava de aviso, que ele também não viu ao escrever por cima da perícia. Ele rodou o `acabar()` (166 s: 10 saltos, 12 ligações da lista, 70 travas) e disse: "funciona certinho". Mesmo assim mudou, porque um acabamento cortado no meio das travas daria no mesmo: **as travas são a última etapa**, depois dos saltos e da caixa da paleta; o acabamento do `construir()` não as começava se a execução já tivesse passado de 190 s (as travas levaram 148,2 s no `acabar()` dele, contra 81 e 83 s de antes). Isto valeu por uma etapa: as travas saíram na quarta, abaixo. **E um defeito meu, achado na conferência:** o `onEdit` da `INVOCAÇÕES` religava a lista com vírgula entre os argumentos do `HYPERLINK`, e a planilha vive em português, onde a vírgula não vale; quem escrevesse por cima de uma linha da lista ficava com as doze em erro. O `ligarSaltosDe_` escolhe o separador pelo idioma da planilha, e a `regressao-construir.js` ganhou o teste que faltava (não havia nenhum do religamento) |
| *"1.4: seria bom ao preencher a vida máxima, a vida atual preencher tbm, na criação da ficha, pq a vida atual fica com nada mesmo após criação da invocação"* | a `VIDA ATUAL` nasce apontando para a conta nova `vida0` da `DADOS_INVOC` (a máxima, quando a ficha tem nome; em branco na ficha vazia). É caixa livre (`livres`, no `ABAS`): o jogador escreve por cima, a caixa de ± grava o número, e enquanto ninguém mexe ela acompanha a máxima |
| *"1.7: Recomendo tirar o aviso de clicks, pode vir a incomodar o jogador"* | nada: perguntei de qual aviso ele falava (o script não mostra nenhum durante a troca de tema desde 25/09), e ele respondeu *"Achei q avisava, erro meu"* |
| *"2.2: a gente precisa mexer nessa penalidade, ideal é ser só a desvantagem no ataque e metade do deslocamento, mas tem q mexer no livro tbm, ja pode atualizar na ficha"* (a arma empunhada sem a Força) | a `DEFESA` da `FICHA` deixa de perder a Destreza; o deslocamento continua caindo pela metade; a desvantagem, que não é número, está na nota do requisito de Força (`FICHA PESSOAL`) e na nota do CORPO A CORPO e do À DISTÂNCIA. A regra mora no `fora_do_livro` do arquivo de dados (`arma_sem_a_forca`), com a frase que o livro ainda traz; o `conferir-catalogo.py` acende no dia em que o livro mudar. **O livro continua com a frase antiga: mudar lá é dele** |
| *"6: Escrevi por cima da pericia e n corrigiu. Esses de codigo ideal só impedir de poder modificar. Mas por exemplo, na ficha amaldiçoada q n leva codigo na celula, ele funciona certinho"* | o Sheets não impede o dono da planilha de escrever numa célula (a trava só avisa), e cada jogador é dono da cópia dele. O que dá é devolver a conta na hora, e agora **toda caixa calculada volta, em toda aba** (`devolverConta_`): `FICHA`, `CARTEIRA`, `FICHA PESSOAL` (em grupo ou não), além das duas que já voltavam. A fórmula de fábrica está no `ABAS` em inglês; a `formulaNoIdioma_` a escreve na pontuação do português (ponto e vírgula no argumento, vírgula no número, barra invertida na matriz, o que está entre aspas intacto). Se mesmo assim a caixa mostrar `#ERROR!`, o script a grava como o `construir()` grava, com a planilha em inglês por um instante. Ficam de fora as caixas livres: vida, energia e integridade da `FICHA`, o Volume de um item e a foto da `FICHA PESSOAL`, a vida atual de uma invocação. As travas de aviso ficaram nesta etapa, até ele testar a devolução no Sheets de verdade; ele testou, e elas saíram na quarta etapa, abaixo |
| *"de resto pode aplicar tbm oq vc falou q falta"*: o livro | o `manual.txt` saiu do livro de hoje (v0.340 do `JJK---Project`, hash `bbaf760b…`, baixado do GitHub para a área de rascunho, porque o clone do disco é de 03/10). Três mudanças: o nome (**Ciclo Maldito** em todo o texto), a **D44** (a Execução Preparada da Vanguarda impõe −2, e a carta de nível 7 diz) e a **D43** (*"Condição, Prende e Cerca sempre pedem TR ... Numa ficha de ataque, o acerto aplica o dano e as outras peças; depois, cada alvo acertado faz o TR registrado"*). Pela D43: o texto das três peças no arquivo de dados é o do livro novo; a carta de feitiço de ataque com uma delas diz **`Acerto + TR`** (coluna nova `peça que pede TR` na `DADOS_AM`); a carta de habilidade da invocação diz `Ataque +4 · TR CD 12`; o exemplo `Peso nas Mãos` do `extrair_tecnica.py` usa a frase nova |
| *"de resto pode aplicar tbm oq vc falou q falta"*: o arnês | `arnes-invocacoes.py`, 26 defeitos plantados no gerador (os números da ficha, a entrada e o retorno, o conjunto, a vida que nasce cheia, o inventário, as cartas, a D43) contra a `regressao-invocacoes.py`, e um contra-teste. Roda à mão, como o da Amaldiçoada |

**Os tempos, pelos dois registros dele (07/10/2026, Sheets lento).** *O `continuar()` montou tudo o que faltava numa execução
só e fechou em 304 s, a 56 s do teto do Apps Script:*

| etapa | estimativa | levou |
|---|---|---|
| `DADOS` | 3,5 s | 12,7 s |
| `DADOS_AM` | 18 s | 35,4 s |
| `DADOS_INVOC` (157 × 450) | 49 s | **89,6 s** |
| `GLOSSÁRIO` | — | 3,7 s |
| menus (1.342) | fora da conta | **35,1 s** |
| travas, no `acabar()` | 81 a 83 s | **148,2 s** |

*A estimativa da aba oculta passa de 0,7 para 1,4 ms por célula, o limite da execução desce de 300 para 270 s (os menus
vêm depois da última aba e ninguém os contava) e o teto das travas fica em 190 s. Num dia lento a montagem vai a três
execuções (`construir()`, `continuar()`, `continuar()`), e a última faz o acabamento. O tempo da `INVOCAÇÕES` e o da
`FICHA PESSOAL` ficaram fora do pedaço do registro que ele mandou (as duas juntas, uns 126 s).*

**Dois rótulos das Habilidades, no mesmo dia.** *"cinco degraus fica ruim, coloca 'cinco níveis'. Quatro entregas pra ser
trilha - Quatro níveis, coisas assim q n precisa circundar a informação, só ser direto". O título do bloco diz `CAMINHO ·
CINCO NÍVEIS` e `TRILHA · QUATRO NÍVEIS`. Procurei o mesmo vício nas outras abas e não achei outro rótulo que diga nível
com outra palavra; o `DEGRAU` do Domínio é o termo do livro. Perguntei se o `Abre no 7` da etiqueta das cartas acima do
nível também vira `Nível 7`.*

**A revisão que ele pediu** (*"revisione a ficha se falta algo do sistema nela e me avise"*). *Comparei o capítulo 20 do
livro (Referências e fichas: os modelos de ficha que o próprio livro traz) e as frases "anote" e "registre" dos outros
capítulos com os rótulos e as notas das cinco abas. Não é uma leitura do livro inteiro regra por regra. O que o livro
manda registrar e a ficha não tem onde:*

1. **O traço e os dois Legados da Origem** *(e as escolhas que um Legado pede). A `FICHA` só tem o menu de Origem; os 90
   Legados estão no arquivo de dados e nenhuma aba os usa.*
2. **Sequelas, Cicatrizes e Exaustão.** *A Sequela muda a janela da próxima queda e só sai no descanso longo; a
   Exaustão tem três degraus; a Cicatriz é permanente.*
3. **Condições e usos gastos do personagem.** *A ficha da invocação tem a caixa; a do jogador não.*
4. **Munição:** *na arma, na reserva e "precisa recarregar", por arma. A `FICHA PESSOAL` só tem a quantidade do item.*
5. **As escolhas do Traje:** *o tipo de TR e as perícias (uma a quatro, pela maestria). A aba só tem a situação.*
6. **Resistências e imunidades** *(os dois tipos do Alicerce do Bastião, a imunidade a Envenenado do Corpo Amaldiçoado,
   as dos Legados).*
7. **Na `INVOCAÇÕES`:** *a Integridade da entidade com alma, e os outros modos de deslocamento.*
8. **Na `FICHA AMALDIÇOADA`:** *o espaço de feitiço ocupado por uma invocação adquirida por espaço conhecido não entra
   na conta dos espaços livres.*

*Ficou de fora de propósito, pela decisão dele de 07/10 (ficha de mesa sem caixa de turno): Padrão, Bônus, Movimento e
Reação, a queda em andamento (janela, tratamento) e a folha de entidades na mesa. Nada disto foi construído: a lista é
para ele decidir.*

**Conferido na terceira etapa:** *a bateria inteira rodou até o fim em 07/10/2026, à noite, com o `original.xlsx` e com tudo desta
etapa dentro (o livro v0.340, os tempos novos e os dois rótulos): vinte e um dos vinte e dois passaram, e a
`regressao-paleta.js`, que não mora na bateria, também. O vigésimo segundo era o `arnes-pessoal.py`, com sete defeitos
plantados que citavam o código de antes (o separador do salto, a devolução só da referência pura, a chamada do
acabamento); foram atualizados, ganharam doze novos (a pontuação do idioma, a devolução em cada aba, a caixa livre, a
reserva em inglês, o religamento do salto, o teto das travas) e ele passa: 80 perturbações acendem a checagem certa. Um
deles não acendia por falta de teste (a caixa de ± com a vida atual apagada), e a `regressao-construir.js` ganhou esse
caso. O `comparar-ficha-01.py` fecha em IGUAIS. O `arnes-invocacoes.py` estava rodando quando esta etapa foi para o git
(os cinco primeiros defeitos tinham acendido); o resultado inteiro entra no próximo registro. A primeira bateria desta
etapa morreu no décimo sexto validador, quando a sessão reiniciou.* **Nada desta etapa rodou no Sheets de verdade**, *e a
devolução da conta na pontuação do português é a parte que só o teste dele confirma.*

**O que fica para ele, depois desta etapa:**

- **Colar os três arquivos que mudaram** *(`Ficha.gs`, `Codigo.gs` e `Invocacoes.gs`; o `Habilidades.gs` mudou uma letra,
  o −2 da Execução Preparada) e montar: `construir()`, `continuar()` quantas vezes o registro pedir, `acabar()` se ele
  pedir. Mandar o registro de cada execução.*
- **Testar a devolução da conta:** *escrever por cima do total de uma perícia da `FICHA`, de uma caixa da `CARTEIRA` e de
  uma da `FICHA PESSOAL`. Tem de voltar sozinha, com um aviso, e não pode ficar `#ERROR!`.*
- **Mudar o livro** *na regra da arma sem a Força, e decidir o que entra da revisão.*

#### A quarta etapa (07/10/2026, à noite): ele testou a terceira no Sheets, e as travas de aviso saíram

*Ele colou os quatro arquivos, montou e mandou o resultado dos seis testes:*

| teste | o que ele viu |
|---|---|
| a devolução da conta | *"Passou nas três abas, com aviso no canto. Nenhuma ficou em #ERROR!."* |
| a invocação nova | *"Vida começou cheia: 8/8."* |
| a arma sem a Força | *"Bō exigindo 3, personagem com 0: Defesa continuou 11; deslocamento 9 → 4,5 m."* |
| Condição, Prende e Cerca | *"As três cartas mostraram 'Acerto + TR'."* |
| as Habilidades | *"'Cinco níveis', 'Quatro níveis' e Execução Preparada com −2 conferidos."* |
| os links | *"Lista de invocações e saltos da Amaldiçoada funcionando; cliquei e confirmei os destinos."* |

**A pontuação do português funciona no Sheets de verdade:** *a `formulaNoIdioma_` escreve a fórmula de fábrica com ponto e
vírgula, vírgula no número e barra invertida na matriz, e nenhuma caixa ficou em `#ERROR!`. Era a parte que só o teste
dele confirmava.*

**As travas de aviso saíram.** *Com a conta voltando sozinha, a trava virou um segundo aviso para a mesma coisa, e era a
etapa mais lenta da montagem (81, 83 e 148,2 s nas três medidas dele). O `protegerFormulas_` saiu do `Codigo.gs`; no
lugar dele o acabamento tem o `tirarTravasDeFormula_`, que só tira as travas de uma ficha montada antes (pela
descrição `fórmula · ...`) e deixa as que o jogador ou o mestre criaram. A `FICHA PESSOAL` não declara mais faixas
travadas (`protegidas` saiu do `ABAS`); declara as `livres`. Sem as travas o acabamento levou 17,4 s no registro dele, e
o teto da montagem sobe de 250 para 300 s; o `TETO_DAS_TRAVAS_` e o recado `FALTAM AS TRAVAS` da terceira etapa saíram.*

**O que a trava fazia e a devolução não faz**, *para ele saber: a conta só volta quando o `onEdit` enxerga a edição na
própria caixa. Recortar uma caixa calculada e colar noutro lugar esvazia a origem sem avisar o script (o evento é o do
destino), e inserir ou apagar linha não gera evento nenhum. A trava de aviso também não impedia nenhum dos dois.*

**Conferido na quarta etapa:** *a `regressao-construir.js` ganhou o teste que escreve por cima de cada conta, uma a uma (433
da `FICHA`, 9 da `CARTEIRA`, 286 da `FICHA PESSOAL`), e todas voltam; o teste do `acabar()` numa ficha com três travas
de antes e uma do mestre; e saíram os que cobravam a trava. O `arnes-pessoal.py` trocou as perturbações das travas
pelas da devolução. O `arnes-invocacoes.py` rodou inteiro: 23 dos 26 defeitos acenderam de primeira e três passaram
calados, por lacuna de teste, e não por defeito da ficha: a linha da CONTA das cartas sorteadas não era conferida (a
devolução sem o teto de 2 × Classe e a devolução além do gasto), e o único teste do TR usava Cego e Prende juntos. A
`regressao-invocacoes.py` confere agora a conta de 114 cartas sorteadas e o TR das cartas de ataque, e ganhou os casos
`Laço` (só Prende) e `Garra` (Toque com duas Restrições Médias, que passa do teto); replantados, os três acendem.*
*A bateria inteira rodou até o fim com a ficha sem travas: vinte e um dos vinte e dois passaram, e a `regressao-paleta.js`
também. O vigésimo segundo era de novo o `arnes-pessoal.py`, com três defeitos plantados que citavam o que saiu com as
travas (dois da função que juntava as fórmulas em faixas, e o teto da montagem, que mudou de número); os dois primeiros
saíram, o terceiro foi acertado, e ele passa: 78 perturbações acendem a checagem certa. Esta etapa não tinha rodado no
Sheets de verdade quando foi para o git.*

**Ele montou a versão sem travas, do zero, ainda em 07/10/2026**, *e conferiu os três pontos: escreveu por cima do total de uma
perícia e "a fórmula voltou sozinha, com aviso no canto, sem perguntar 'editar mesmo assim?' e sem #ERROR!"; os links
das invocações e os saltos da Amaldiçoada "funcionaram após reconstruir"; e a montagem levou **11 min 14 s somando as
execuções, com cerca de 14 s de acabamento**, sem travas. O registro completo de cada execução ele não mandou (só o
resumo), então o tempo de cada aba nessa montagem não está conferido.*

### B41 · A revisão: o que o livro manda registrar e a ficha não tinha — **CONSTRUÍDA e MONTADA NO SHEETS em 08/10/2026: 7 dos 8 pontos passaram no teste dele, e um pente-fino achou mais três; as correções das duas rodadas estão no fim desta seção (as caixas de texto que esticam, uma montagem de cada vez, o link que abre a ficha recolhida, o aviso do atual acima do máximo, o glossário). Falta ele ver as correções no Sheets**

*Da lista da revisão (terceira etapa do B40) ele escolheu, em 07/10/2026: "Traços, sequelas, cicatrizes, exaustão,
resistencias e imunidades, integridade da entidade com alma, espaço de feitiço ocupado por invocação". Ficaram de fora
as condições e usos gastos do personagem, a munição e as escolhas do Traje. Ele escreveu "Traços", e o item era "o
traço e os dois Legados": perguntei se os Legados entram.*

**O que cada um é, no livro:**

| item | a regra | o que a ficha precisa |
|---|---|---|
| traço | Escolhas da Origem: "Um traço: escreva um detalhe importante da sua história"; não dá bônus | uma linha de texto |
| Sequelas | uma por queda encerrada; 0, 1, 2 ou 3 antes de cair dão janela de 3, 2 ou 1 rodada, ou Derrotado na hora; saem no descanso longo | um número de 0 a 3 e a janela da próxima queda |
| Cicatrizes | depois da segunda queda na mesma missão, registrada com o mestre; permanente, sem modificador | texto |
| Exaustão | da quarta luta do dia em diante, um degrau por luta, até 3; 1: desvantagem em perícias e ofícios; 2: deslocamento até 4,5 m; 3: desvantagem em ataques e TRs | um número de 0 a 3, o efeito, e o limite de 4,5 m no DESLOCAMENTO |
| resistências e imunidades | vêm de habilidade (o Alicerce do Bastião: dois tipos por descanso longo), de Origem (o Corpo Amaldiçoado é imune a Envenenado) e de Legado | texto |
| Integridade da entidade | "Criaturas que não sejam personagens jogadores usam metade da vida máxima, arredondada para baixo, com mínimo 1"; o corpo não autônomo não tem alma | atual, máxima (conta) e um menu de com ou sem alma |
| espaço por invocação | "um espaço dá uma entidade do seu nível. A vaga continua ocupada quando ela está recolhida" | uma caixa no Orçamento da `FICHA AMALDIÇOADA`, que conta as fichas com aquisição `Espaço conhecido` |

**O estudo:** *`mockup/revisao-estudo.png` (montado por `python3 mockup/estudo_revisao.py mockup/revisao-estudo.html`, e a foto
pelo Firefox sem tela). Quatro blocos, desenhados como a planilha, com o novo em âmbar:*

1. *Sequelas, Exaustão, resistências e imunidades, na `FICHA`: **A** uma linha embaixo das barras, na seção 2; **B** uma
   linha no fim da seção 3; **C** dividido (o estado com as barras, as proteções com a Defesa).*
2. *Traço e cicatrizes: **A** o traço na `FICHA`, embaixo da Origem, e as cicatrizes na `FICHA PESSOAL`, ao lado da
   Aparência; **B** os dois no dossiê da `FICHA PESSOAL`.*
3. *Integridade da entidade: **A** uma linha embaixo da barra de vida, com o estágio; **B** a mesma, sem o estágio.*
4. *O espaço por invocação: uma caixa `EM INVOCAÇÕES` no Orçamento, sem forma para escolher.*

*Indiquei A, B e A. Nada foi construído nesse dia; a construção está no fim desta seção.*

**O número da `CARTEIRA` (B33), no mesmo dia.** *"atualiza la pra 1.0". O número era `"Nº M-"` + a versão sem o ponto + o
nome, do tempo em que a versão era 0.258 e saía `M-0258`; com a versão em 1.0 saía `M-10`. Passa a mostrar a versão
como é escrita, `Nº M-1.0-KAOR` (uma limpeza no `monta.py`, com a diferença contada no comparador e a checagem no
`conferir-ficha-xlsx.py`). O `M` do número eu não mexi.*

**A pasta `ficha-invocacao/` antiga: apagada em 08/10/2026.** *Perguntei se apagava ou guardava, ele respondeu "pode atualizar", perguntei
de novo e ele disse: "é pra apagar kkk". Saíram a pasta (a planilha solta, o `constroi.py`, o `monta.py`, a `gramatica.py`,
a `previa.py` e quatro scripts de conserto), os três validadores dela (`conferir-invocacao.py`, `regressao-invocacao.py` e
`arnes-invocacao.py`) e os dois arquivos que só eles liam: o `invocacao.json` e o `capitulo-16-invocacoes.md`. A bateria
passa de vinte e dois para **dezenove** validadores. O `conferir-ficha-xlsx.py` deixou de abrir a planilha solta para
saber o nome das abas dela; o C1 do `decisoes-ficha.json` aponta a aba `INVOCAÇÕES` como a ficha da invocação, e o
`conferir-decisoes.py` cobra isso e que a pasta não exista. O `HANDOFF-sessao-invocacoes.md`, de setembro, ficou: é
histórico. Tudo continua no git, do commit `0b3339c` para trás.*



#### A construção (08/10/2026)

**O que ele escolheu das formas:** *"1 - A, mas acredito que pode ser +- como na C, colocar espaços separados e talz"; "2 - B, mas acho
que ter um espaço para acesso na ficha pra ver pelo menos o legado de exceção/mecanico seria ideal, lembrando q da pra
criar legado, ent n precisa fazer lista acho eu"; "3 - A"; "4 - Perfeito". E, dos Legados: "Ambos" (entram o traço e os
dois Legados).*

| onde | o que entrou |
|---|---|
| `FICHA`, embaixo das barras | uma linha com quatro caixas separadas, no passo das caixas do REGISTRO: `SEQUELAS` e `EXAUSTÃO` (menus de 0 a 3, com a consequência escrita embaixo: a janela da próxima queda, e o efeito do degrau), `RESISTÊNCIAS` e `IMUNIDADES` (texto). Embaixo, `LEGADO 1` e `LEGADO 2`, que espelham o dossiê da `FICHA PESSOAL` (o nome, o tipo e o que faz). Do degrau 2 de Exaustão em diante o `DESLOCAMENTO` fica em até 4,5 m, sem aumentar o que já está menor |
| `FICHA PESSOAL`, no dossiê | `CICATRIZES` divide a linha da aparência; `TRAÇO · UMA FRASE DA SUA HISTÓRIA` entra em cima da história; e os dois Legados fecham o dossiê, de ponta a ponta: o nome, o tipo (menu: Narrativo, De rolagem, De exceção) e o que faz, em texto livre. O dossiê foi de 27 para 35 linhas |
| `INVOCAÇÕES`, em cada ficha | uma linha embaixo da barra de vida: `ALMA` (menu: Com alma, Sem alma), `INTEGRIDADE ATUAL` (nasce cheia e é livre, como a vida), `INTEGRIDADE MÁXIMA` (metade da vida máxima, para baixo, mínimo 1) e `ESTÁGIO` (pelo que falta, em fração exata). Sem alma, a máxima fica em traço. As condições e as anotações cederam duas linhas cada, e a ficha não cresceu |
| `FICHA AMALDIÇOADA`, no Orçamento | a caixa `EM INVOCAÇÕES`: conta as fichas da aba `INVOCAÇÕES` com nome e aquisição `Espaço conhecido`, e desconta dos livres; como o Talento e o Domínio, o feitiço do Leque não a paga |

**Como as linhas entraram no meio da `FICHA`.** *As seções 1 a 6 vêm da planilha exportada, e até aqui tudo o que as limpezas
acrescentaram entrou no fim da aba. O `ficha-v01/linhas_novas.py` abre oito linhas depois da linha em branco que fica
embaixo da faixa do estágio de Integridade, antes de qualquer limpeza, e desloca o que aponta para baixo dali: as
células, as mesclagens (a lombada, que atravessa, estica), os menus, as regras de cor, as alturas e a âncora das
imagens da `FICHA`; as fórmulas da `FICHA`, e as da `CARTEIRA` e do índice da `DADOS` que a citam; e as coordenadas do
`_meta`. Daí em diante as limpezas acham as caixas pelo rótulo e pelo índice, como já faziam. O
`ficha-v01/estado_do_personagem.py` preenche as linhas. O `comparar-ficha-01.py` usa o mesmo mapa para comparar a
exportação com a ficha gerada (a linha 39 da exportação é a 47 da gerada), e fecha em IGUAIS, contando as caixas
novas. Quem lê o `layout.json` por conta própria (o `conferir-ficha-xlsx.py`, a `regressao-kaori-na-ficha.py`) passa a
usar o `linhas_novas.carrega()`.*

**O espaço por invocação atravessa duas abas.** *A `FICHA AMALDIÇOADA` é gerada antes da `INVOCAÇÕES` e não sabe o endereço
dela: a `DADOS_INVOC` publica a contagem numa coluna com o cabeçalho `espaços por invocação`, e o Orçamento a acha pelo
cabeçalho (`INDEX` e `MATCH` na linha 1).*

**Os Legados na `FICHA` mostram os dois, e não só os de exceção ou de rolagem.** *Ele pediu "pelo menos o legado de
exceção/mecanico". O espelho mostra os dois Legados, com o tipo escrito ao lado do nome: os narrativos do livro também
têm uso de mesa. Se ele preferir só os mecânicos, é uma troca na conta do espelho. Avisei.*

**O que não entrou.** *A Exaustão não muda sozinha a recuperação de PE fora de ambiente propício (a nota da caixa diz a
porcentagem de cada degrau), nem marca a desvantagem nas perícias, nos ofícios, nos ataques e nos TRs: o texto embaixo
da caixa diz o efeito, e a rolagem é da mesa. As Sequelas também não mexem em conta nenhuma. O limite de 4,5 m é a
única consequência que virou conta.*

**Dois testes traziam endereço da `FICHA` escrito à mão, e a bateria os acendeu.** *Com as oito linhas, a
`regressao-amaldicoada.py` lia o menu do atributo de conjuração em `Z51` (hoje `Z59`) e falhava em três fichas; e o
`arnes-pessoal.py` plantava um defeito na nota da mão principal em `D41` (hoje `D49`). Nenhum era defeito da ficha. A
regressão passa a achar a caixa pelo rótulo, na planilha gerada; o arnês segue com o endereço no trecho, e avisa
sozinho quando ele ficar velho.*

**Conferido (08/10/2026).** *A bateria inteira rodou até o fim com tudo dentro: dezessete dos dezenove passaram de
primeira, e a `regressao-paleta.js` também. Os dois que acenderam foram os do parágrafo de cima; consertados, a
`regressao-amaldicoada.py` rodou inteira de novo e passa, e o `arnes-pessoal.py` também (78 defeitos plantados acendem,
e o contra-teste fica verde). Dos arneses que rodam à mão, só os defeitos novos: os cinco do `arnes-invocacoes.py` (a
Integridade com a vida inteira, a entidade sem alma com Integridade, o estágio 1 na metade, a atual em branco, e o
`Prende` sem TR) e os dois do `arnes-amaldicoada.py` (a invocação por espaço conhecido que não desconta, e a domada
que desconta) acendem; os outros 25 e 71 não rodaram de novo, e os trechos deles existem todos no código de hoje.
Tamanhos: `Ficha.gs` perto de 820 KB (o teto é 900). Nada disto rodou no Sheets de verdade: as oito linhas novas mudam
o endereço de quase tudo na `FICHA`, e quem tem ficha montada precisa montar de novo.*

#### O teste no Sheets (08/10/2026): 7 de 8, as caixas que esticam e uma montagem de cada vez

*O Mizuki mandou o resumo do teste (o relatório inteiro e os registros estão em `Downloads/Testes-ficha-2026-10-08/`): os três
arquivos colados, a planilha reconstruída e a lista conferida, "7 dos 8 pontos passaram". Passaram as Sequelas, a
Exaustão (com o deslocamento que já era de 3 m ficando em 3 m), os Legados, o traço e as cicatrizes, a Integridade da
invocação, o `EM INVOCAÇÕES` do Orçamento e o resto da `FICHA`. A montagem levou três execuções: 272, 196 e 165 segundos.*

**O que falhou: resistências e imunidades.** *"Textos de aproximadamente 170 caracteres ficam cortados pela altura das
caixas." Cabiam duas linhas e meia. E, medindo o livro, o mesmo problema estava escondido nos Legados, que o teste fez
com texto curto: os 85 Legados têm de 58 a 546 letras (os de exceção, que ele pediu para ver na `FICHA`, têm mediana de
352), e a caixa de três linhas da `FICHA PESSOAL` e o espelho de duas linhas da `FICHA` cortavam a maior parte.*

*As quatro caixas passam a esticar com o que for escrito, como as cartas de Habilidades. Cada aba declara as dela no
`ABAS`, em `esticam`, em grupos (os gatilhos, a aba cujas linhas mudam de altura e, para cada texto, a largura em
pixels, as células que o formam, as linhas que esticam e a altura das que não mudam), e o `esticarCaixas_` do
`Codigo.gs` conta as linhas com a medida da Roboto 10 que já existia (`linhasDoTexto_`). As caixas de um grupo podem
dividir linhas: todas partem da altura comum, e cada caixa aumenta as dela até o texto caber:*

- *resistências e imunidades dividem a linha com as Sequelas e a Exaustão: estica só a linha de baixo, pelo texto mais
  comprido das duas; a linha do número fica como está;*
- *escrever o nome, o tipo ou o texto de um Legado na `FICHA PESSOAL` estica a caixa dele ali e o espelho da `FICHA`
  (o espelho junta os três, e é isso que se mede);*
- *apagar o texto devolve a altura comum.*

**Os links em `#ERROR!`, e uma montagem de cada vez.** *O relatório: "Leitura dos valores calculados de oito abas encontrou
inicialmente 22 #ERROR!, todos em links: Amaldiçoada D7:G7,J7:M7,P7:Q7 e Invocações D21:D32", com o registro em `FICHA
PRONTA`; "duas tentativas anteriores à continuação final iniciaram no servidor e falharam, com sobreposição"; e rodar o
`acabar()` de novo consertou os 22. O registro da execução final diz `idioma de antes: en_US`, e toda execução devolve
o português no fim, mesmo quando para no meio: a planilha só amanhece em inglês com outra execução ainda rodando (ou
morta sem chegar ao `finally`). Cada execução troca o idioma da planilha inteira; se a outra devolveu o português no
meio do caminho, o que esta escreveu depois saiu com vírgula numa planilha que pedia ponto e vírgula, e os saltos são a
última fórmula que a montagem escreve. É a causa mais provável, e não está provada: não reproduzi no Sheets.*

- *`umaDeCadaVez_` (no `ficha/modelo.gs.js`): o `construir()`, o `continuar()` e o `acabar()` pegam a trava do script
  (`LockService.getScriptLock()`, e não a do documento, que é a da troca de paleta), e quem não a pega para na hora com
  o recado "já tem uma montagem rodando nesta planilha", sem tocar em nada. O corpo da montagem passou a se chamar
  `montar_`, e o do acabamento, `soOAcabamento_`.*
- *`conferirSaltos_` (no `Codigo.gs`): depois que a planilha volta ao português, a montagem e o `acabar()` leem o que
  cada caixa de salto mostra; as que estiverem em erro são escritas de novo com ponto e vírgula, e o registro diz
  quantas eram (`saltos conferidos depois do idioma: …`). O registro não diz mais `PRONTA` com link quebrado sem contar.*
- *o `verificar()` acusa salto em erro.*

**Conferido.** *A `regressao-construir.js` ganha os testes das quatro caixas (o texto do teste, de 169 letras; um Legado de 538;
o segundo texto que não encolhe a caixa do primeiro; apagar), dos saltos em erro escritos de novo e do `verificar()`, e da
trava (o `construir()` e o `acabar()` param com o recado, e a montagem que termina a solta). O `conferir-ficha-xlsx.py`
confere que as caixas declaradas são as mesclagens da planilha gerada, que o espelho lê as três caixas que o script
mede e que os 85 Legados do livro cabem esticados; e as duas entradas com a trava. O `arnes-pessoal.py` ganha doze
defeitos. Nada disto rodou no Sheets de verdade: a trava e a conferência dos saltos só se confirmam lá.*

#### O pente-fino no Sheets (08/10/2026): três problemas, e o link que abre a ficha

*No mesmo dia ele mandou um segundo relatório (`Downloads/Pente-fino-ficha-2026-10-08/`), de uso comum pelo navegador, com
"três problemas concretos" e "dificuldades de navegação", e escreveu: "Mais alguns problemas extras"; depois, sobre as
dificuldades: "a parte do 'Também há dificuldades de navegação: Missões/XP fica escondido atrás de um pequeno +' pode
ignorar, o resto é mais importante, tirando" (a mensagem chegou cortada aí; perguntei o que vinha depois).*

| o que o relatório achou | o que foi feito |
|---|---|
| "Vida acima da máxima: após usar os controles de combate e trocar de Caminho, ficou 25/23, sem aviso" | a caixa do atual fica vermelha enquanto ele passar do máximo, na vida, na energia e na integridade (uma regra a mais no `corDeEstado_`, antes das do atual baixo). **O atual não desce sozinho**: ver abaixo |
| "Cicatrizes corta texto: uma descrição de 189 caracteres ficou parcialmente escondida" | as seis caixas de texto livre do dossiê esticam (aparência, cicatrizes, traço, história, laços e personalidade), num grupo só, porque dividem linhas |
| "Glossário: os cabeçalhos NOME e ATRIBUTO estão invertidos na tabela de perícias" | trocados no `glossario.py`: estava assim desde que a aba nasceu, em 17/09 |
| "os links das invocações chegam ao cabeçalho sem abrir a ficha recolhida" | o `abrirFichaDaInvocacao_`, no `onSelectionChange`: a seleção que chega no número da ficha (onde o link cai) abre o grupo da fileira e o da coluna de fichas dela. Clicar nesse número com a ficha fechada também a abre. O `ABAS` da `INVOCAÇÕES` declara o que abrir (`abrir`) |
| "Missões/XP fica escondido atrás de um pequeno +" | nada, a pedido dele |
| "Em 100%, alguns controles exigem rolagem lateral; em 75%, os textos auxiliares ficam pequenos" | nada: é a largura da página, que foi escolha do estudo |
| "Uma alteração rápida de Energia ficou pendente uma vez", sem se repetir | nada: o próprio relatório não a classifica como defeito. Três edições em menos de dois segundos disputam o `onEdit`, e a caixa de ± que ficar preenchida é aplicada quando for editada de novo |

**Por que o atual não desce sozinho.** *Descer o atual para o máximo assim que o máximo cai parece o certo, e estraga a ficha
num engano: quem escolher o nível errado no menu, ou apagar o Caminho para trocar, veria a vida cair para o máximo
errado e ficar lá depois de consertar o menu. O vermelho avisa, e a caixa de ± já não deixa a cura passar do máximo.
Perguntei, e ele decidiu: "Só aviso vermelho, descer automático pode ser ruim."*

**O gatilho do link roda a cada clique.** *O `onSelectionChange` já existia, para a troca de paleta, e a regra dele era
"clique sem pendente custa uma leitura de propriedade, e não lê a aba". O gatilho novo olha primeiro o endereço da
seleção, que quase nunca é o de uma ficha, e só então pergunta em que aba está. Não sei se o Sheets dispara o
`onSelectionChange` quando a seleção muda por um link, e não por um clique: só o teste dele diz. Se não disparar,
clicar no número da ficha abre do mesmo jeito.*

**Conferido.** *A `regressao-construir.js` ganha os testes do dossiê (as cicatrizes com 192 letras; a história com 2135 e a
personalidade com 799, que dividem linhas, cabendo as duas), do link (a ficha 8, recolhida nas duas direções, abre; outra
célula não abre nada) e da regra do atual acima do máximo; o `conferir-ficha-xlsx.py`, as seis caixas do dossiê contra
as mesclagens da planilha e os cabeçalhos do glossário; o `arnes-pessoal.py`, mais dez defeitos (são 98). O teste
"clique sem pendente" da `regressao-paleta.js` passa a entregar um endereço na seleção, como o Sheets entrega.*

**A bateria inteira, com as duas rodadas do dia dentro.** *Rodou até o fim: dezoito dos dezenove passaram, e a `regressao-paleta.js`
também. O décimo nono era o `arnes-pessoal.py`, com 97 dos 98 defeitos acendendo a checagem certa: o que não acendeu
("o clique comum volta a ler a aba") roda a `regressao-paleta.js`, e o arnês não a levava para a cópia em que planta o
defeito. Ela entrou na lista da cópia, e o mesmo defeito, plantado à mão numa cópia com ela, acende a checagem certa; o
arnês inteiro não rodou de novo depois disso (leva perto de quarenta minutos). Os arneses que rodam à mão
(`arnes-amaldicoada.py` e `arnes-invocacoes.py`) não rodaram nesta rodada: os trechos deles existem todos no código de
hoje. Nada disto rodou no Sheets de verdade.*

### B42 · Buff/Debuff dos máximos: vida, energia, Integridade, Proteção e carga — **CONSTRUÍDO E MONTADO NO SHEETS em 08/10/2026 (a forma A do estudo): 8 dos 9 itens passaram no teste dele, e a correção do número grande da invocação ele testou no mesmo dia (os quatro testes passaram). Em 09/10/2026 ele decidiu que o bônus sobe o atual na ficha recém-criada, como já estava: nada em aberto**

*Junto com a decisão do aviso vermelho ele pediu: "existe a possibilidade do jogador ganhar vida máxima extra de alguma forma,
como no caso da lapidação e/ou habilidades de técnica, seria interessante uma caixa que pudesse permitir o jogador
aumentar os máximos dos valores da ficha, entre carga, vida, energia e integridade. Oq recomendo fazermos? Já q quase
tudo a ficha automaticamente corrige de valor pro original. Talvez fazer uma guia só pra mexer nesses valores?"*

*Recomendei não abrir guia nova (mais uma aba na montagem, que já leva três execuções, e o lugar que o jogador mais
esquece), e sim uma caixa ao lado de cada máximo, igual às de Buff/Debuff que a `FICHA` já tem na Defesa, na iniciativa,
na CD, na conjuração, nos ataques e no deslocamento: o bônus entra na própria conta do máximo, e a ficha não o
"corrige de volta". Aceita negativo (o livro manda pagar vida máxima ao Insistir numa queda). Ele: "Então podemos sim,
colocar essas caixas, lembrando q tem muitos locais aonde podem ter mais ou menos nesse valor". A caixa guarda o
saldo, e o jogador pode digitar a conta inteira nela (`=5+10-3`); a alternativa que registra cada origem com nome, uma
tabela de ajustes na `FICHA PESSOAL`, eu ofereci e ele não pediu.*

**O estudo:** *`mockup/maximos-estudo.png` (montado por `python3 mockup/estudo_maximos.py mockup/maximos-estudo.html`), com
três posições na linha de cada barra: **A** logo depois do máximo, antes da barra; **B** depois da barra, antes do
temporário; **C** no fim da linha, depois da caixa de ±. Ele: "Opção A, lembrando de fazer isso até em invocações e
outros menus que possam ser alterados assim".*

| onde | o que fazer |
|---|---|
| `FICHA`, as três barras | a caixa `Buff/Debuff` de duas colunas logo depois do máximo; a barra perde 3 das 15 colunas. O máximo vira a conta do livro mais a caixa; o teto da temporária, os estágios de Integridade e o aviso vermelho acompanham |
| `FICHA`, a Proteção | a mesma caixa, no fim da caixa da Proteção: é o único número de combate do Registro sem ela (o Bloquear sai da Defesa, e segue o Buff/Debuff dela) |
| `FICHA PESSOAL`, a carga | a caixa no fim da carga; a barra dela passa de 5 para 3 colunas, e o limite vira 5 + Força + a caixa |
| `INVOCAÇÕES` | nada: cada ficha já tem a caixinha `B/D` embaixo de todo número calculado (atributos, ataque, CD, Defesa, vida máxima, deslocamento e os quatro TRs), e a Integridade máxima da entidade é metade da vida máxima |
| Maestria, espaços de feitiço, Refino de graça, Classe máxima, Classe 0 | ficam de fora, a menos que ele peça: a Maestria vem só do nível, e as outras são contagens de progressão (os espaços já recebem o Marco e os pactos) |

**A construção (08/10/2026).** *A `FICHA` já tinha a engrenagem dessas caixas, a que pôs o Buff/Debuff ao lado da Defesa e dos
ataques em 17/09, e as novas entram por ela, sem módulo novo:*

- *`ficha_layout.py`: a `PROTEÇÃO` entra na lista `COM_BUFF` (a caixa toma as duas últimas colunas dela, como nas
  outras), e a lista nova `DOS_MAXIMOS` leva a caixa para a linha das três barras: o rótulo e a caixa de duas colunas
  logo depois do máximo, uma coluna de vão, e a barra, com a conta e o estilo do canto dela, três colunas adiante
  (`P26:Q27` a caixa da vida, `S26:AD27` a barra);*
- *`indice_ficha.py`: a caixa ao lado de "VIDA - Atual/Máxima" entra no índice como `buff de vida` (e `buff de
  energia`, `buff de integridade`, `buff de proteção`);*
- *`ficha_automatica.py`: cada máximo vira `IFERROR((a conta do livro)+a caixa,"")`, e a Proteção soma a dela. A
  Defesa soma a Proteção, e sobe junto. Sem Caminho o máximo continua vazio;*
- *`ficha_pessoal.py`: na carga, o rótulo e a barra cedem duas colunas à caixa (`L:M`), e o limite é 5 + Força + a caixa;*
- *`Codigo.gs`: as notas das quatro caixas da `FICHA` (a dos máximos fala da Lapidação, do custo de Insistir e de
  escrever a conta, `=5+10-3`); a da carga é do gerador.*

*A caixa é número digitado, e não conta: o `onEdit` não a devolve. O `comparar-ficha-01.py` fecha em IGUAIS sem regra
nova, porque as trocas passam pelo `ficha_layout.py` e pelo `ficha_automatica.py`, que ele já refaz.*

**O que acompanha sozinho.** *O teto da vida temporária (metade da máxima), os estágios de Integridade, a cor da barra, o
aviso vermelho do atual acima do máximo e, na carga, o "acima" e o deslocamento zerado.*

**Conferido (08/10/2026).** *Testes novos: a `regressao-kaori-na-ficha.py` compara dois casos iguais fora as quatro caixas, com a
conta feita pelo LibreOffice (vida 23 e 28 com +5, energia 8 e 5 com −3, Integridade 26 e 36 com +10, Proteção 1 e 3
com +2), e a Defesa do modelo passa a somar o Buff/Debuff da Proteção; a `regressao-ficha-pessoal.py` ganha a carga com
bônus e com redução (a mesma carga passa do limite com −5); a `regressao-construir.js`, que as caixas nascem em 0, que o
máximo as soma, que o que o jogador digita nelas fica sem aviso, e as notas; o `conferir-ficha-xlsx.py`, a posição de
cada caixa (logo depois do máximo, duas colunas, a barra depois do vão), a soma por fora da conta do livro, a Proteção
e a carga. Defeitos plantados: três no `arnes-pessoal.py` (são 101) e dois no `arnes-ficha-pessoal.py`, que roda à mão e
rodou só com esses dois: acendem. O desenho foi conferido contra o estudo pelo `medidas/ver-aba.py`.*

*A bateria inteira rodou até o fim com tudo dentro e **os dezenove passaram**, e a `regressao-paleta.js` também. (Uma
primeira rodada foi cortada no meio porque ele precisou reiniciar o computador; esta é a segunda, inteira.) A frase final
do `rodar-tudo.sh` ainda dizia "os vinte e dois passaram", do tempo dos três validadores da invocação antiga, e foi
acertada depois da rodada. Os outros arneses que rodam à mão (`arnes-amaldicoada.py`, `arnes-invocacoes.py`) não rodaram.
Nada disto rodou no Sheets de verdade.*

#### O teste dele no Sheets (08/10/2026): 8 de 9

*Ele colou os três arquivos, reconstruiu e mandou o relatório (`Downloads/Testes-buff-ficha-2026-10-08/`): "8 dos 9 itens
passaram". A montagem levou três execuções (243, 189 e 111 s; "9min03s de execução") e terminou em `FICHA PRONTA` com
"saltos conferidos depois do idioma: nenhum em erro", sem pedir o `acabar()`. Antes dela, uma tentativa apareceu como
cancelada depois de 21 s, sem causa confirmada, e outra parou com "Service Spreadsheets failed while accessing document",
que é erro do serviço do Google, e não do script.*

| item | resultado |
|---|---|
| negativos e contas na caixa | passou: com −3 os máximos foram a 16/5/22 sem mexer nos atuais; `=5+10-3` ficou como fórmula e mostrou 12 |
| o atual acima do máximo | passou: as três caixas ficaram vermelhas |
| Proteção e Defesa | passou: com +5 a Proteção foi de 1 a 6 e a Defesa de 11 a 16 |
| carga | passou: "0,3 de 10" com +5; com −20, "acima", em vermelho, e o deslocamento em 0 m |
| caixas de texto | passou: resistências (386 letras), imunidades (397), cicatrizes (205), história (1.392), o Legado (662) e o espelho dele na `FICHA` (694), todos com o fim à vista |
| o link que abre a ficha recolhida | passou: a lista levou a `H207` e abriu as linhas 209 a 402; levou a `AA9` e abriu as colunas da sétima ficha. **O Sheets dispara o `onSelectionChange` quando a seleção muda por um link**, que era a dúvida |
| glossário e conferência dos saltos | passaram |
| o bônus do máximo numa ficha nova | o relatório dá como falha: com +5, vida 19/19 virou 24/24 (e energia e Integridade idem). Ver abaixo |

**O bônus sobe o atual numa ficha recém-criada, e ficou assim.** *O atual nasce como `=máximo` (a ficha nasce cheia, desde
a limpeza das barras), e enquanto ninguém mexe nele ele acompanha o máximo, com o bônus ou sem. Assim que o atual vira
número (o jogador digita, ou usa a caixa de ±), o bônus muda só o máximo: o relatório confirma ("Após preencher
manualmente os atuais com 19/8/25, os bônus preservaram os atuais corretamente"). Quem errou foi a minha instrução de
teste, que dizia "o atual não muda" sem dizer que a ficha nova nasce cheia. Não mexi: a alternativa (o atual de fábrica
descontar o bônus positivo) faria a ficha de quem tem um bônus permanente nascer com a vida abaixo do máximo. Expliquei a
ele, e a troca é uma fórmula se ele preferir.*

**O número grande da invocação.** *"Clicar no número grande '2' em I207 não abriu a invocação mesmo após espera. Clicar no
pequeno número lateral em H207 abriu." O `abrir` da `INVOCAÇÕES` passa a declarar três células por ficha (o número da
lombada, o número grande e o título), e as três abrem a fileira e a coluna de fichas. A `regressao-construir.js` confere
as 36 entradas e que o número grande (`I207`) e o título abrem.*

**O que o teste não cobriu.** *A trava de uma montagem de cada vez ("Não foram provocadas duas montagens simultâneas"), os
links das doze invocações (testou duas) e o aplicativo de celular.*

**Conferido (a correção do número grande).** *Passam a `regressao-construir.js`, a `regressao-pessoal.js`, a `regressao-delta.js`,
a `regressao-paleta.js`, o `comparar-ficha-01.py` (IGUAIS), o `conferir-ficha-xlsx.py`, o `conferir-decisoes.py`, a
`regressao-invocacoes.py` e o `arnes-pessoal.py` (101 defeitos plantados acendem, e o contra-teste fica verde). A bateria
inteira não rodou de novo para esta mudança, que é uma lista mais comprida no `ABAS` da `INVOCAÇÕES`. Não rodou no Sheets.*

**A correção do número grande, testada por ele (08/10/2026, 23h45).** *Ele colou o `Codigo.gs` e o `Invocacoes.gs` na ficha já
montada, sem reconstruir, e mandou o resultado: "Esta correção funcionou na ficha já montada. Os quatro testes passaram na
segunda invocação recolhida": o número grande "2" abriu, o título abriu, o número pequeno lateral abriu, e o link da lista
"abriu automaticamente". Fica confirmado no Sheets que a lista `abrir` é lida na hora do clique, e que trocar os dois
arquivos basta, sem montar de novo.*

**O que continua sem teste no Sheets.** *A trava de uma montagem de cada vez (ninguém provocou duas execuções juntas) e dez
das doze invocações.*

**As quatro pendências que ficaram com ele, respondidas em 09/10/2026.** *(1) O bônus na ficha recém-criada: "N entendi,
exemplifique"; expliquei com exemplo, e espera a resposta dele. (2) A trava de uma montagem de cada vez: "N precisa, pq
só eu rodo esse construir"; fica sem teste no Sheets, por decisão dele. (3) A regra da arma sem a Força no livro: "Ja
mudei". Conferi e não achei a mudança: o `main` do `JJK---Project` no GitHub continua na v0.340, de 06/10, e a cópia
local (`Claude 2/.claude/worktrees/ficha-amaldicoada-b31-8d7a7a`) também, as duas com "você não soma Destreza à Defesa
enquanto empunhar a arma". Perguntei onde ele mudou. Enquanto o livro novo não chega ao repositório, o `manual.txt`
fica como está e a regra continua no `fora_do_livro` do arquivo de dados (`arma_sem_a_forca`); a ficha já aplica a regra
nova. (4) A mensagem que chegou cortada em "tirando": "N tinha nada".*

**O bônus na ficha recém-criada: fica como está (09/10/2026).** *Com o exemplo (ficha nova, vida 19/19, +5 no Buff/Debuff), ele
respondeu "Pode sim, adicionar", que servia para os dois lados; perguntei qual, e ele escolheu "Fica 24/24": o bônus soma
também no atual enquanto a ficha está intocada. É o que a ficha já faz, e nada mudou. Do livro: "vou atualizar jaja";
quando a regra da arma sem a Força estiver no `JJK---Project`, falta reler o livro (`extrair-manual.py`) e tirar o
`arma_sem_a_forca` do `fora_do_livro`.*

### B43 · O descanso, e duas notas — **CONSTRUÍDO E MONTADO NO SHEETS em 09/10/2026 (o descanso na forma A, e as duas notas): os nove itens passaram no teste dele**

*Perguntou "falta mais algo na ficha?", e da lista que eu trouxe respondeu três itens.*

**As escolhas do Traje:** *"Só escreve na nota que o jogador tem que escrever quais ele escolheu". A nota da `SITUAÇÃO DO TRAJE`,
na `FICHA PESSOAL`, ganha: "A ficha não guarda o tipo de TR nem as perícias do Traje: escreva quais você escolheu em
LAÇOS E ANOTAÇÕES, no dossiê. Essas escolhas são suas, e valem para qualquer Traje que você vestir." (o livro: "Anote o
TR e as perícias na ficha. Essas escolhas são suas e valem para qualquer Traje que vestir").*

**Os outros modos de deslocamento da invocação:** *"n precisa, só colocar uma nota". A nota do `DESLOCAMENTO` de cada ficha
ganha: "A ficha só conta o terrestre: se a entidade voa, escala ou nada, escreva o modo e a distância em CORPO, SENTIDOS E
COMUNICAÇÃO."*

*As duas notas estão no `ficha_pessoal.py` e no `ficha_invocacoes.py`, e a ficha gerada já as traz. São notas do `ABAS`:
só aparecem numa planilha montada de novo, e por isso vão no mesmo pacote do descanso.*

**O descanso:** *"Problema q tem tipos, ficaria na ficha e como fariamos?". Um menu na `FICHA` com os quatro tipos do livro; o
`onEdit` aplica e limpa o menu, como a caixa de ±, e avisa o que mudou. O que cada um faz, pela tabela do livro:*

| o menu | vida | PE | Integridade | Sequelas | Exaustão |
|---|---|---|---|---|---|
| Curto · lugar propício | não muda | +25% do máximo | não muda | ficam | fica |
| Curto · fora | não muda | +25%, +15%, +5% ou nada, pelo degrau de Exaustão | não muda | ficam | fica |
| Longo · lugar propício | volta ao máximo | volta ao máximo | volta ao máximo | saem | sai |
| Longo · fora | vai à metade do máximo, se estiver abaixo | idem | volta ao máximo | saem | fica |

*A recuperação arredonda para baixo, com mínimo 1 quando a fração é positiva, e não passa do máximo. O que a ficha não
sabe fazer sozinha: o "máximo perdido por Insistir", que o livro manda restaurar no descanso longo, mora no Buff/Debuff
da vida junto com os outros bônus, e a ficha não sabe que parte dele é de Insistir; e os usos por dia e as condições, que
ela não guarda.*

**O estudo:** *`mockup/descanso-estudo.png` (montado por `python3 mockup/estudo_descanso.py mockup/descanso-estudo.html`), com
três lugares: **A** uma linha própria entre as barras e o estado, com o registro do último descanso ao lado (a `FICHA`
cresce três linhas); **B** ao lado dos atributos, nas dez colunas livres à direita da Essência, com o registro resumido
embaixo; **C** na linha do estado, como quinta caixa, sem registro. Indiquei a A.*

**A construção do descanso (09/10/2026).** *Ele: "Pode ser A". A linha entra entre a faixa do estágio de Integridade e o estado:
o `linhas_novas.py` passa a abrir onze linhas, e não oito (a linha 39 da exportação é a 50 da gerada), e o
`estado_do_personagem.py` põe nas três primeiras o rótulo `DESCANSO` com o menu (o convite "Escolha o descanso" e os
quatro tipos), e `O ÚLTIMO DESCANSO` com o registro, no resto da linha. O índice publica `descanso` e `último descanso`.*

*No `Codigo.gs`, o `descansar_` (chamado pelo `onEdit` da `FICHA`) lê os atuais, os máximos, as Sequelas e a Exaustão,
faz a conta no `contaDoDescanso_`, escreve só o que mudou (o atual que nasceu como conta numa ficha intocada fica como
está), escreve o registro (`textoDoDescanso_`: "Longo, fora de lugar propício · vida 3 → 11 · PE 8 → 30 · …"), devolve o
menu ao convite e avisa no canto. Se o descanso é longo e o Buff/Debuff da vida está negativo, o aviso lembra de zerar
o máximo perdido por Insistir. A vida temporária, os usos por dia e as condições ficam com o jogador.*

**Conferido.** *A conta bate com os quatro exemplos do livro: Rina com 1 de 10 PE vai a 3, e com 9 vai a 10; com 8 PE máximos
fora de lugar propício, 2, 1, 1 ou zero pelo degrau de Exaustão; Mei com 3 de 23 de vida vai a 11, e com 18 fica em 18; 60
PE com 8 vai a 30. A `regressao-construir.js` roda esses e o caminho inteiro pelo menu (a conta, o menu de volta ao
convite, o registro, um aviso só, o lembrete de Insistir); o `conferir-ficha-xlsx.py` confere que o menu do gerador é o
que o script aplica e onde a linha fica; o `arnes-pessoal.py` ganha onze defeitos (são 112). O desenho foi conferido
contra o estudo pelo `medidas/ver-aba.py`.*

*A bateria inteira rodou até o fim com o descanso e as duas notas dentro, e **os dezenove passaram** (o `arnes-pessoal.py`
com os 112 defeitos acendendo a checagem certa), e a `regressao-paleta.js` também. Os arneses que rodam à mão
(`arnes-amaldicoada.py`, `arnes-invocacoes.py`, `arnes-ficha-pessoal.py`) não rodaram: os trechos deles existem todos no
código de hoje. Nada disto rodou no Sheets de verdade; como a `FICHA` cresceu três linhas, é preciso montar de novo.*

#### O teste dele no Sheets (09/10/2026): os nove itens passaram, e o construir() que não recomeçava sozinho

*Ele colou os três arquivos, reconstruiu e mandou o relatório (`Downloads/Testes-descanso-2026-10-09/`): "Os nove itens da
imagem passaram no Sheets". Com máximos de 20 de vida, 100 PE e 25 de Integridade: o longo fora levou a vida de 5 a 10 e o
PE de 10 a 50, devolveu a Integridade, zerou as Sequelas e deixou a Exaustão em 2; o longo em lugar propício levou tudo
ao máximo; o curto em lugar propício deu +25 PE mesmo com Exaustão 3; o curto fora deu 35, 25, 15 e 10 a partir de 10,
pelos degraus 0 a 3. O menu voltou ao convite e o registro e o aviso saíram em todos, com o lembrete de Insistir quando o
Buff/Debuff da vida estava em −5. Numa ficha ainda cheia o longo disse "nada mudou" e preservou as contas dos atuais. As
duas notas estão certas, e nada saiu do lugar abaixo das barras. A montagem levou três execuções (225, 211 e 129 s).*

**A falha do começo da montagem, que se repetiu.** *O relatório: "As primeiras tentativas de construir falharam com timeout do
serviço de planilhas / erro genérico do editor ... Após restar só __montando__, criei uma guia em branco e excluí a
temporária". O registro da falha: `Service Spreadsheets timed out while accessing document`, na linha do `finally` que
devolve o português. Já tinha acontecido na montagem do B42. O Mizuki explicou o que via: "ao clicar em construir, ele
deleta todas as guias e deixa o 'montagem', mas ao deixar ele n consegue deletar o montagem em seguida, por justamente
ser a ultima guia". São duas coisas:*

- *o estouro de tempo é do serviço do Google, apagando as abas antigas de uma ficha cheia; não tem conserto do lado do
  script, só tentar de novo;*
- *tentar de novo é que não funcionava: o `construir()` começava apagando a `__montando__` que tinha sobrado, que era a
  única aba da planilha, e o Sheets não deixa apagar a última. Era defeito meu, e pedia a limpeza à mão.*

*O `montar_` passa a aproveitar a `__montando__` que houver (`getSheetByName(...) || insertSheet(...)`), apaga cada aba
antiga numa tentativa própria (`_comRetentativa_`), e a volta ao português, no `finally`, é tentada de novo e não esconde
mais o erro da montagem: se ela falhar, o erro que aparece é o primeiro, e se a montagem terminou e só o idioma ficou em
inglês o recado manda rodar o `acabar()`. O mesmo no `acabar()`. A `regressao-construir.js` monta a ficha inteira numa
planilha em que só sobrou a `__montando__`, e confere que o erro que aparece é o da montagem; os dois defeitos
plantados no `arnes-pessoal.py` (são 114) acendem, conferidos à mão um a um.*

**Conferido.** *Passam a `regressao-construir.js`, a `regressao-pessoal.js`, a `regressao-paleta.js`, o `comparar-ficha-01.py`
(IGUAIS), o `conferir-ficha-xlsx.py` e o `conferir-decisoes.py`. O `arnes-pessoal.py` inteiro e a bateria não rodaram
para esta mudança: ele disse "se n quiser usar arnes e deixar o gpt ficar fazendo os testes manualmente, pode". Não rodou
no Sheets, e só aparece na próxima vez que a primeira tentativa de montar falhar.*

### B44 · A otimização das paletas e as bordas do Buff/Debuff, feitas no Sheets pelo outro agente — **TRAZIDAS PARA O REPOSITÓRIO em 09/10/2026; já estão aplicadas e testadas por ele na planilha**

*O Mizuki mandou o pacote `Downloads/Entrega-ficha-2026-10-09/Ficha-e-codigos-2026-10-09.zip` (os quatro `.gs` e a planilha
exportada): "Chat fez algumas atualizações na ficha, atualize os arquivos locais e salve no git. de merge também ao fim". As
anotações do agente que monta e testa a ficha (o GPT) estão em `Downloads/Otimizacao-paletas-2026-10-09/` (`Integracao.txt`,
`Resultado-dos-testes.txt`, os dois `.diff`).*

| arquivo do pacote | o que tinha | o que foi feito aqui |
|---|---|---|
| `Codigo.gs` | a troca de paleta otimizada (345 linhas a mais, 28 a menos, só na parte da paleta) | adotado como está: o `Codigo.gs` é escrito à mão, não tem gerador |
| `Ficha.gs` | uma linha: `P25:Q25`, `P29:Q29` e `P33:Q33` na lista de bordas esquerdas da `FICHA` | levado para o gerador (abaixo); o `Ficha.gs` gerado tem as mesmas bordas, em outra ordem na lista |
| `Invocacoes.gs` | igual ao do repositório | nada |
| `Habilidades.gs` | **a versão de 05/10**, com "imponha −1" na Execução Preparada do Vanguarda | **não entrou**: o do repositório é o de 07/10, com o −2 do livro v0.340, e o agente diz que não mexeu nesse arquivo. Avisei o Mizuki para conferir qual está no projeto dele |
| a planilha exportada | a ficha montada, na paleta `Mizuki · Escuro` | comparada célula a célula com a que o gerador produz: iguais, fora o que o script cria na montagem (a caixa da paleta, os saltos, a cor da barra e a caixa da imagem do Marco). Não entrou no git |

**A troca de paleta, pelo que o agente escreveu e mediu.** *A `CARTEIRA` termina inteira (fundo, texto, bordas e as imagens) antes
das outras abas, mesmo quando o jogador muda de aba no meio; o fundo e a fonte de cada trecho são gravados juntos, com uma
confirmação só, antes de o passo ser dado como pronto; as grades de fábrica, os contrastes e o mapa de cores são
reaproveitados dentro da execução; as 122 opções ganharam a descrição das cores ("Noite · Escuro · roxo e lilás"), e os
nomes antigos continuam valendo (`nomeCanonicoDaPaleta_`); o menu que já existe é atualizado no `onOpen` sem perder a
escolha; o aviso deixou de prometer 20 segundos e diz "Veja a CARTEIRA primeiro; o restante termina enquanto você usa a
ficha. Durante a troca de cores, não feche nem recarregue esta página." Medido por ele no Sheets: a soma dos passos foi de
91,7 para 79,9 s no Noite Claro e de 94,1 para 80,9 s no Noite Escuro, em quatro execuções em vez de cinco, com a
`CARTEIRA` pronta em cerca de 10 s. Não precisou reconstruir.*

**As bordas, no gerador.** *O rótulo `Buff/Debuff` das três barras saía aberto do lado esquerdo: o molde dele é o rótulo que
fica colado em outra caixa e usa a borda direita dela, e ali ele fica sozinho, depois de um vão. O `ficha_layout.py`
passa a dar a ele a própria borda esquerda (o `_estilo` aprendeu a acrescentar lados). Sem isso a próxima geração do
`Ficha.gs` apagaria o conserto do agente.*

**Os testes, postos em dia com o desenho novo.** *A `regressao-paleta.js` cobrava a cor e a régua da `CARTEIRA` e da `FICHA` na
primeira execução; passa a cobrar a `CARTEIRA` inteira, com a arte, abrindo a execução, e a `FICHA` começando nela (o
último trecho da `FICHA` foi para a segunda execução, que é a troca que o desenho novo faz), e o relatório de tempos no
formato novo. O `conferir-ficha-xlsx.py` aceita a medida entre o `flush` e o registro do passo, e cobra o texto novo do
aviso. O Sheets de mentira aprendeu `Range.setWrap` e `Sheet.setRowHeight`, que a caixa da paleta passou a usar.*

**Conferido.** *Passam a `regressao-paleta.js`, a `regressao-construir.js`, a `regressao-pessoal.js`, a `regressao-delta.js`, a
`regressao-arte.js`, o `comparar-ficha-01.py` (IGUAIS), o `conferir-ficha-xlsx.py` e o `conferir-decisoes.py`; e o
`arnes-paleta.py` inteiro (os 11 defeitos plantados na troca de paleta acendem no código novo, e o contra-teste fica
verde). A bateria inteira e o `arnes-pessoal.py` não rodaram (os trechos dele existem todos no código de hoje). Eu não
revisei a otimização linha a linha: li as mudanças, e a garantia de que ela pinta igual vem dos testes daqui e dos que
o agente fez no Sheets.*

### B45 · A ficha passa a ler o livro final (R43), e não mais a candidata — **FEITA em 10/10/2026; falta o Mizuki montar e testar no Sheets** *(o diagnóstico de 09/10 vem primeiro, depois o andamento e o fechamento)*

*O Mizuki fechou a revisão das regras do livro em 09/10/2026. O livro do sistema passou a ser o R42 (no `JJK---Project`,
`sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`, desde a v0.354 de lá). O `manual.txt` daqui ainda sai da
candidata editorial (`planejamento-editorial/consolidacao/lote-01/LIVRO-COMPLETO.md`, como está na v0.340), que não recebeu
a revisão. Ele mandou seguir com a ficha: "pode seguir em ordem".*

**O que foi medido, numa cópia do repositório fora desta pasta:**

- A bateria como está passa: os dezenove (o `comparar-ficha-01.py` precisa do `ficha-v01/original.xlsx`, que o
  `.gitignore` deixa fora).
- O `manual.txt` de hoje é exatamente o que o `extrair-manual.py` tira da candidata.
- Trocando só o `manual.txt` pelo texto do R42 (o mesmo `extrair-manual.py`, com o caminho do R42), doze validadores
  continuam passando e sete reprovam. O texto tem 13.053 linhas (eram 12.905); 480 títulos mudaram de nível, 200 títulos
  da candidata não existem com o mesmo nome no R42, e 150 do R42 são novos.

| validador que reprova com o R42 | o que ele diz | o que é |
|---|---|---|
| `conferir-catalogo.py` (11 falhas) | `Troca` não está no livro; `De Novo` é Pesada; `Concentrada` e `Duradoura` não são achadas; as condições mudaram de forma; três frases do `fundamento` e as de efeito de `Perseguir`, `Empurrão`, `Fica`, `Certeiro`, `De Novo` e `Assinatura` não estão no livro; uniforme e escudo sem a Força; a carga; a vida inicial da Vanguarda | regra da revisão, mais forma |
| `conferir-kaori.py` | o quadro da Kaori mudou de forma | forma (o título virou "Exemplo: Kaori") |
| `revisao-cetica.py` | não acha a frase do teto de dano | forma (a frase foi reescrita; o número é o mesmo) |
| `regressao-kaori-na-ficha.py` | não acha o teto do refino, os exemplos de Defesa ou a fórmula do cobrir-se | forma, a confirmar |
| `regressao-ficha-pessoal.py` | o `equipamento-do-livro.json` não bate com o livro | regra da revisão (equipamento sem a Força, carga) |
| `regressao-amaldicoada.py` | o `tecnica-do-livro.json` não acha a seção "Proteção e presença"; o `habilidades-do-livro.json` não bate; a carta que junta duas habilidades não acha "Nível N: Nome." | forma (o R42 deu título próprio a cada habilidade) e texto novo das cartas |
| `regressao-invocacoes.py` | o livro não diz mais a frase da devolução das Restrições | regra da revisão (a devolução não cobre a Forma) |

**As regras da revisão que alcançam a ficha, pelo que os validadores acusaram.** *A lista completa das decisões está no
`JJK---Project`, em `ciclo-maldito-r41/revisao-de-regras/MUDANCAS-DE-REGRA.md`.*

- A Melhoria `Troca` saiu, e `De Novo` passou de Média para Pesada.
- `Certeiro` voltou a não ter rolagem de acerto; `Perseguir`, `Empurrão`, `Fica` e a Restrição `Assinatura` têm texto novo.
- Arma, uniforme e escudo sem a Força pedida: a arma dá desvantagem nos ataques e metade do deslocamento (a ficha já
  faz isso, pela chave `fora_do_livro.arma_sem_a_forca`); **o uniforme e o escudo passam a proteger**, com metade do
  deslocamento e desvantagem em Teste de Resistência Físico (a ficha hoje zera a proteção); as penalidades não acumulam.
- A carga acima do limite deixa de travar o personagem: até o dobro do limite ele anda com a mesma penalidade.
- A vida inicial da Vanguarda (`8 + Constituição`) está no livro, e sai do `fora_do_livro`.
- Nas invocações, a devolução das Restrições não cobre a Forma.
- Continuam fora do livro: as missões solo e os multiplicadores de XP.

**O plano, em três fatias que o Mizuki consegue testar no Sheets uma por vez:**

1. **Os leitores passam a aceitar as duas formas do livro,** sem trocar a fonte. Nada muda na planilha; a bateria continua
   passando com a candidata, e a lista de reprovações com o R42 encolhe para o que é regra.
2. **A fonte passa a ser o R42,** com o catálogo, o equipamento, a técnica, as habilidades e a invocação extraídos de
   novo. O `Ficha.gs` e o `Habilidades.gs` são gerados outra vez. É aqui que a planilha muda: as cartas de Habilidades
   trazem o texto do R42, e a lista de Melhorias perde a `Troca`.
3. **A conta da Defesa e da carga** segue a regra nova do uniforme, do escudo e do peso. É a única das três que muda
   número que a ficha calcula, e por isso vai separada.

*Este registro é só o diagnóstico. Os números saíram de duas rodadas da bateria em cópias do repositório, e os arquivos
desta pasta não foram alterados além desta entrada.*

#### B45, andamento de 10/10/2026: a fonte já é o R42 na cópia de trabalho; falta a parte que muda conta da planilha

*Nada disto foi commitado. Está na cópia de trabalho, com o patch guardado fora do repositório.*

**Feito, e conferido um a um (não pela bateria inteira):**

- `extrair-manual.py` lê o R42. Ele devolve a forma de título às 48 linhas só em negrito que o livro final usa no
  capítulo de Caminhos ("**Fluidez no nível 15**", "**Conduções**"), um nível abaixo do título em que estão.
- `catalogo-projeto-m.json`: saiu a `Troca` (68 Melhorias); `De Novo` é Pesada; o efeito de `Perseguir`, `Empurrão`,
  `Fica`, `Certeiro`, `De Novo`, `Desarma o Feitiço`, `Armado`, `Segura` e `Sugar` e o texto da `Assinatura` são os do
  R42; a vida inicial da Vanguarda e a arma sem a Força saíram do `fora_do_livro`, porque o livro passou a trazê-las; a
  chave `_pendente` lista três regras que o livro traz e a planilha ainda não segue.
- `conferir-catalogo.py` passa (lê as Melhorias que dividem um título, as condições um nível abaixo do grupo, e as
  frases novas). `conferir-kaori.py`, `revisao-cetica.py`, `conferir-progressao.py`, `conferir-decisoes.py` e
  `regressao-exemplos.py` passam.
- `extrair_equipamento.py`: uma frase mudou (a propriedade Leve).
- `extrair_habilidades.py`: 111 habilidades, como antes; 33 cartas mudam de texto. Dois ajustes: o parágrafo "Nível N."
  logo abaixo do título da habilidade não abre um trecho próprio, e todo título de terceiro nível fecha o dono anterior
  (a apresentação do Batedor ia parar na carta do nível 27 da Estocada). No R42 o `Preservar o Aprimoramento` é uma das
  Intervenções do nível 11 da Invocação Principal; na candidata estava no 19.

**Falta, e é o que muda conta na planilha.** *São cinco regras; cada uma mexe em fórmula gerada, em regressão e em arnês.*

| regra do R42 | o que a planilha faz hoje | onde |
|---|---|---|
| Restrição paga Melhorias, nunca a Forma (item 143) | a devolução paga a Forma também | `conferir_feitico.py` (regra 1), `ficha_amaldicoada.py` |
| a devolução da especial da entidade não cobre a Forma (item 143) | cobre | `extrair_invocacao.py`, `ficha_invocacoes.py` |
| pacto não concede aptidão nem espaço de feitiço; modifica feitiço, energia, aptidão ou Estilo (itens 34 a 36) | o menu "o pacto concede" tem aptidão, espaço conhecido e PE, e o pacto permanente de espaço soma um espaço conhecido | `extrair_tecnica.py` (pactos), `ficha_amaldicoada.py` (linhas do teto, dos espaços de pacto e do menu) |
| o limite de metade da Essência conta o pacto permanente e o de restrição (itens 37 e 186) | conta só o permanente | `ficha_amaldicoada.py` |
| uniforme e escudo sem a Força protegem, com penalidade; carga até o dobro anda com penalidade (itens 157 e 158) | zera a proteção; acima do limite avisa que não anda | `defesa_equipamento.py`, `ficha_pessoal.py` |

**Depois delas:** *gerar de novo (`monta.py`), o que troca o `Ficha.gs`, o `Habilidades.gs` e a planilha de referência;
acertar o teste da carta que junta habilidades (ele procura "Nível N: Nome.", forma que o R42 não usa mais); rodar a
bateria inteira; e o Mizuki testar no Sheets.*

#### B45, fechamento de 10/10/2026: a planilha segue o livro final; falta o Mizuki montar e testar no Sheets

*Substitui a tabela "Falta" do andamento acima. O Mizuki respondeu à pergunta do menu de pactos: "A" (o menu passa a
oferecer o que o pacto modifica, sem conta atrás).*

**As cinco regras da tabela, e mais três que o extrator das invocações só mostrou depois de passar da primeira frase:**

| regra do livro final | o que a planilha passou a fazer | onde |
|---|---|---|
| Restrição paga Melhorias, nunca a Forma | a devolução aproveitada para no gasto em Melhorias; o resto aparece como "Devolução perdida: N pontos sem Melhoria para pagar" | `ficha_amaldicoada.py`, `conferir_feitico.py` |
| na especial da entidade, "a Forma fica fora dessa conta" | a mesma conta, na carta da especial e na linha de cada Classe | `ficha_invocacoes.py`, `extrair_invocacao.py` |
| o pacto concede uma mecânica única: modifica um feitiço, a energia, uma aptidão ou um Estilo | o menu do pacto oferece essas quatro, lidas da frase do livro, e nenhuma soma espaço, aptidão ou PE | `extrair_tecnica.py`, `ficha_amaldicoada.py` |
| o limite de metade da Essência conta o permanente e o de restrição | a caixa `PERMANENTES` virou `VAGAS` e conta os dois | `ficha_amaldicoada.py` |
| uniforme e escudo sem a Força protegem, com metade do deslocamento e desvantagem em TR Físico | a Defesa não muda mais com a Força; o deslocamento cai pela metade | `ficha_pessoal.py`, `Codigo.gs` (a nota do deslocamento) |
| carga acima do limite e até o dobro: metade do deslocamento; acima do dobro: não se desloca | 4,5 m entre o limite e o dobro, 0 m acima do dobro; as três penalidades cortam uma vez só | `ficha_pessoal.py` |
| Classe 0 e básica da entidade: a Restrição Leve "devolve o dado que a Melhoria tirou" | com Melhoria e Restrição, os dados voltam ao valor do nível | `ficha_amaldicoada.py`, `ficha_invocacoes.py` |
| Acerto da Expansão da domada: pontos de especial da maior Classe, menos o preço Médio de Inescapável, com o desconto da Família Livre | "Acerto 5d8" na Classe 4 sem a Mira Livre (9 − 4), "Acerto 7d8" com ela (9 − 2); era Classe d8 | `ficha_invocacoes.py` |
| a entidade "segue as regras gerais de Carga" | acima do limite é aviso e o deslocamento dela cai pela metade; acima do dobro é erro e vai a 0 m | `ficha_invocacoes.py` |

**Uma leitura minha, para o Mizuki confirmar no teste.** *O livro diz que o pacto de restrição ocupa vaga e que, "com
permissão do mestre, ele pode existir mesmo sem vaga". A caixa `VAGAS` conta os dois tipos, e o aviso (⚠) só aparece
quando há um pacto permanente e as vagas não fecham. Um personagem de Essência 0 com um pacto de restrição mostra
"1 de 0" sem aviso.*

**O que mais mudou de texto, sem mudar conta:** *16 Bênçãos (entraram `Represália` e `Sangue Frio`); o Acerto do
primeiro degrau do Domínio ("Quando houver Acerto, rola como um feitiço"); as Formas de área passaram a dizer "metade
do resultado do dano no sucesso"; `Projetar Energia` gasta até metade do Refino; 33 cartas de habilidade.*

**Os extratores aprenderam o formato do livro final**, *que tirou do título o que a candidata punha nele:* a Categoria
de Efeito dos Talentos e das Bênçãos ("Categoria de Efeito: 2." na primeira linha), o nível do aprimoramento do
Evocador ("Nível 2.") e o nível das seções (um a menos em vários capítulos). *Os dois formatos são lidos.*

**O `_pendente` do catálogo ficou vazio**, *e o `conferir-catalogo.py` cobra que fique.*

**Testes novos:** *na regressão da AMALDIÇOADA, dois feitiços em que a Forma custa e a Restrição sobra, os três pactos
por ficha (o de restrição com vaga, sem vaga e junto de permanentes) e a Classe 0 com Melhoria e Restrição; na das
INVOCAÇÕES, a domada sem a Mira Livre, a entidade acima do dobro da carga e o deslocamento dela; na da FICHA PESSOAL,
a carga acima do dobro, o uniforme sem a Força e o texto das duas notas. Os três arneses ganharam o defeito de cada
regra.*

**O livro foi a R43 no mesmo dia.** *O Mizuki mandou a correção da ordem do Bloquear ("estava vindo depois da rolagem
de acerto"): a escolha entre a Defesa e Bloquear vem antes da rolagem do atacante. Na ficha isso é só texto: onze
linhas do `manual.txt` e três cartas de habilidade (`Olhos Em Mim` do Bastião, a do nível 2 do Incursor, com o
`Instante Decisivo`, e a do nível 27 do Pugilista, com o `Redirecionar a Força`, em que o novo alvo passa a usar só a
Defesa). O `Ficha.gs`, o `Invocacoes.gs` e o `Codigo.gs` saem iguais com a R42 e com a R43; só o `Habilidades.gs` muda.*

**Conferido:** *a bateria inteira passa (os dezenove), sobre o estado com a R43. Os defeitos novos dos arneses
acenderam: os nove das INVOCAÇÕES, os da AMALDIÇOADA e os da FICHA PESSOAL (a lista com o resultado de cada um está na
mensagem do commit).* **Não rodou no Sheets.**

**O roteiro do teste no Sheets.** *Cole os quatro arquivos de `apps-script/` e rode o `construir()`.*

| nº | onde | o que fazer | o que tem de aparecer |
|---|---|---|---|
| 1 | FICHA AMALDIÇOADA, um feitiço | Classe 3, Forma `Explosão`, nenhuma Melhoria, Restrição `Atrasar` | dano `7d8` (9 pontos − 2 da Explosão; a devolução de 3 não paga a Forma) e o aviso "Devolução perdida: 3 pontos sem Melhoria para pagar". Antes saía `9d8` |
| 2 | o mesmo feitiço | trocar para Classe 2, `Projétil`, Melhoria `Fura`, Restrição `Atrasar` | dano `6d8` (6 − 2 da Fura + 2 devolvidos), sem aviso |
| 3 | FICHA AMALDIÇOADA, PACTOS | abrir o menu à direita da forma do pacto | quatro opções: `Um feitiço`, `A energia`, `Uma aptidão`, `Um Estilo` |
| 4 | PACTOS, caixa `VAGAS` | com Essência 2, pôr um pacto `Permanente` e um `Pacto de restrição` | `⚠ 2 de 1` |
| 5 | a mesma caixa | apagar o `Permanente` e pôr um segundo `Pacto de restrição` | `2 de 1`, sem o aviso (o de restrição pode existir sem vaga, com permissão do mestre) |
| 6 | FICHA AMALDIÇOADA, ORÇAMENTO, `ESPAÇOS` | com um pacto `Permanente` preenchido, no nível 2 | `3` (2 + metade do nível; o pacto não soma mais) |
| 7 | FICHA AMALDIÇOADA, Classe 0 | uma linha com Melhoria Leve e sem Restrição; depois pôr uma Restrição Leve | no nível 2: `1d8` só com a Melhoria, e `2d8` com a Restrição junto |
| 8 | FICHA PESSOAL, `VESTINDO` | com Força menor que a que o uniforme pede | a `DEFESA` da FICHA não cai, o `DESLOCAMENTO` mostra `4,5 m`, e a nota do requisito de Força diz que a peça protege normalmente |
| 9 | FICHA PESSOAL, carga | passar do limite (5 + Força) sem chegar ao dobro; depois passar do dobro | `4,5 m` no primeiro caso e `0 m` no segundo, com a nota da carga dizendo qual |
| 10 | INVOCAÇÕES, uma domada de nível 14 com Expansão | Famílias sem a `Mira` entre as duas primeiras; depois com a `Mira` na primeira | `Acerto 5d8` e depois `Acerto 7d8` |
| 11 | INVOCAÇÕES, uma básica | Melhoria Leve sem Restrição; depois com uma Restrição Leve | um dado a menos no primeiro caso, e o dado de volta no segundo |
| 12 | Habilidades, Pugilista nível 27 | ler a carta | "Ele não pode Bloquear esse ataque" |

#### B45, a revisão de 11/10/2026: uma segunda leitura achou quatro coisas que tinham ficado, e um defeito antigo dos testes

*O Mizuki pediu, numa outra conversa: "analise a nova documentação, o livro foi atualizado e juntamente a isso algumas informações
ficaram salvas nas pastas locais, revisione a ficha se as informações estão todas corretas".*

**O que aconteceu, para não repetir.** *Aquela conversa trabalhava numa cópia parada no commit de 09/10 (`3e05cea`) e não buscou o
GitHub antes de começar: refez o B45 inteiro sem saber que ele já estava fechado e publicado desde a véspera (`d5e26e5`). Só
descobriu na hora de enviar. As duas versões chegaram às mesmas regras por caminhos separados, o que serve de conferência
cruzada; onde diferiam, valeu a de 10/10, que tem a resposta do Mizuki sobre o menu dos pactos ("A"), a carga da invocação e a
bateria inteira. Da de 11/10 entrou só o que a de 10/10 não tinha, que é a lista abaixo. A "informação salva nas pastas
locais" era este B45.*

**Como foi a segunda leitura.** *A lista `MUDANCAS-DE-REGRA.md` do livro lida inteira, item por item, procurando onde a ficha toca
em cada regra; e as 148 notas distintas da planilha gerada, lidas uma a uma contra o livro final.*

| item da lista do livro | como estava na ficha de 10/10 | como ficou |
|---|---|---|
| [23] Talismã: saiu a frase "se a próxima entrada for o retorno de uma entidade caída, abata somente o valor adiantado" e o exemplo dela | o `RETORNO` da `INVOCAÇÕES` abatia a carga: Classe 4 com o talismã carregado mostrava `6 PE` | mostra `8 PE` (2 × Classe), com ou sem carga; a nota diz que a carga não abate o retorno. A carga continua valendo na entrada comum (`2 PE`) |
| [160] Reação de Cobrir-se de Energia: tira só a proteção passiva | a nota dizia "você fica sem proteção até o fim do seu próximo turno" | "como Reação e 2 PE"; perde só a proteção passiva da aptidão, e Traje, Revestimento e escudo continuam valendo |
| [94] Cicatriz: o jogador escolhe vantagem em Intimidação e desvantagem em Persuasão, ou nenhum dos dois | a nota dizia "não dá modificador" | a nota traz a escolha e manda escrever qual foi |
| [14] passar no TR reduz o resultado do dano | no arquivo de dados as quatro Formas de área ainda diziam "TR; metade dos dados no sucesso" | "TR; metade do resultado do dano no sucesso", como o livro. A carta da ficha mostra só "TR, metade", e não muda |
| [1] e [16] o Acerto de dano do domínio | a regra não aparecia em nota nenhuma | a nota do Acerto, na `FICHA AMALDIÇOADA`, e a da Expansão da domada, na `INVOCAÇÕES`, dizem como ele é montado |

**Li e não pediu mudança:** *o que a ficha não mostra (Ritual, a economia de ações da invocação, as três barreiras, o Rescaldo, a
recarga da Técnica Máxima, Insistir, o XP guardado, a Quebra Coisa na Técnica Máxima, que a ficha nunca proibiu) e o que a
versão de 10/10 já tinha certo. Os textos das Melhorias e das Restrições do arquivo de dados estão literais no livro (67
de 68; o Efeito Próprio é resumo).*

**Um defeito antigo dos testes.** *A `regressao-delta.js` terminava com `process.exit(1)`, que corta a saída quando ela vai para um
cano e passa de 64 KB; as cartas de Habilidades imprimem o texto inteiro do livro na falha, e o `arnes-delta.py` podia não
achar o nome da checagem que acendeu (na cópia de 09/10 um defeito ficou "sem veredito"). Passa a usar `process.exitCode`.*

**Testes.** *A `regressao-invocacoes.py` cobra os `8 PE` do retorno, e o defeito plantado do `arnes-invocacoes.py` foi invertido (o
retorno voltar a abater a carga). O `conferir-ficha-xlsx.py` ganhou dez checagens: o menu das formas e o do que o pacto
modifica, a vaga, a Troca fora de todas as abas, e as notas da carga, das Cicatrizes, das Restrições, da Reação e do
retorno, mais a frase do TR e o livro de origem.*

**Fica com o Mizuki.** *(1) O item [23]: eu li "o caso não acontece" como "a carga não abate o retorno"; se a intenção for outra, é
uma linha. (2) A variante de rolar a vida [147] está no livro e a ficha continua no valor fixo. (3) O número da `CARTEIRA`
continua 1.0. (4) No roteiro do teste acima entra um item: **13**, `INVOCAÇÕES`, um shikigami de criação de nível 13 com o
`TALISMÃ` carregado: `ENTRADA` `2 PE` e `RETORNO` `8 PE` (antes `6 PE`).*

**Conferido, sobre a versão juntada (a de 10/10 mais as correções acima).** *Um por vez, e cada um dentro de um teto de memória
(`systemd-run --user --scope -p MemoryMax=6G`): no meio desta rodada o computador do Mizuki reiniciou por falta de RAM, com
três regressões encadeadas e um arnês que tinha ficado órfão rodando junto. Passam: `conferir-catalogo.py` (TUDO VERDE),
`conferir-kaori.py`, `conferir-progressao.py`, `regressao-exemplos.py`, `arnes.py`, `revisao-cetica.py`,
`conferir-decisoes.py`, `arnes-decisoes.py`, `conferir-ficha-xlsx.py` (com as dez checagens novas), `regressao-delta.js`,
`arnes-delta.py` (os 40 acendem), `regressao-pessoal.js`, `regressao-construir.js`, `regressao-paleta.js`,
`regressao-arte.js`, `comparar-ficha-01.py` (IGUAIS), os quatro `--confere` dos extratores, `regressao-invocacoes.py` (54),
`regressao-amaldicoada.py` (354) e `regressao-ficha-pessoal.py` (104). O defeito novo do `arnes-invocacoes.py` (o retorno
voltar a abater a carga) acende. **Não rodaram** sobre a versão juntada: `regressao-kaori-na-ficha.py` (nada do que mudou toca
na FICHA, e ela passou na bateria de 10/10), `arnes-pessoal.py`, o `rodar-tudo.sh` de uma vez e os arneses manuais
inteiros. Pico de memória medido: 1,7 GB na `regressao-ficha-pessoal.py`, 1,2 GB na `regressao-amaldicoada.py`. **Nada disto
rodou no Sheets.***

#### B46, fechamento de 14/10/2026: a ficha segue o livro R51 — **FECHADO E APLICADO NA FICHA OFICIAL**

*Continua o trabalho salvo no commit de andamento `547eb3f`. Esse commit já existia ao retomar; o registro antigo ainda dizia que tudo estava apenas no `git add`. As correções deste fechamento ficaram preparadas no Git, sem novo commit nem push.*

**Fonte e decisões preservadas.** O `manual.txt` e os cinco extratores seguem o Ciclo Maldito R51, em `/home/mizuki/JJK-v0.341-para-subir/sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`. O estudo aprovado é `mockup/origens-estudo.html`: três cartas no dossiê, capacidade criada com o mestre como primeira opção e nome livre, painel fechado depois da AU só com as escolhas, Morrendo com prazo explicado, três caixinhas de Sequelas, ofício compatível aberto, criada acompanhando até o fim da Classe e tamanho do ganho no pacto. Nenhuma regra nova foi escolhida neste fechamento.

**Item por item da seção E de `MUDANCAS-DE-REGRA.md`.** Os procedimentos que dependem da decisão da mesa continuam como texto do livro; este fechamento não acrescenta calculadoras de reparo, criação ou ritual.

| item | o R51 e o que fica na ficha |
|---|---|
| 24 | O reparo por alguém de Classe menor usa teste Difícil e recupera 1/3 do máximo se o corpo está uma Classe acima, ou 1/4 se está duas ou mais; igual ou abaixo, metade, para baixo. Fonte e texto das invocações atualizados. |
| 33 | Criação por ofício compatível, base `8 + atributo + Maestria`, com dificuldade pela diferença de Classe; sem receita, projeto ou prazo antigo. Procedimento no texto extraído, sem decisão automática de materiais ou tempo. |
| 188 | Ofício compatível registrado no Corpo Amaldiçoado e nas doze fichas de INVOCAÇÕES. O menu também aceita outro nome escrito pelo jogador. |
| 189 | A aquisição `Criação` acompanha o invocador até o fim da Classe do nível inicial/fixo informado. Inicial 6, invocador 11: nível 8; invocador 7: nível 7. A domada com inicial/fixo 6 conserva 6. O modelo da regressão e os defeitos plantados acompanham a regra. |
| 190 | As fontes de vantagem na criação e a vantagem após falha são as do texto extraído; não há concessão automática de vantagem na ficha. |
| 40 | Exemplos de pacto atualizados no texto do R51; Promessas não recebem tamanho. |
| 151 | Cada pacto tem `TAMANHO DO GANHO`: Pequeno, Médio, Grande, Enorme e `Sem tamanho (Promessa)`. |
| 191 | Pacto temporário não ocupa vaga, mesmo que a perda seja permanente. `VAGAS` continua contando somente Permanente e Pacto de restrição. |
| 192 | O temporário fora do turno usa Reação e gatilho percebido, depois dos dados e antes das consequências; texto atualizado, sem refazer rolagem. |
| 46 | O R51 permite duas compras de Acerto, Dificuldade, Alcance, Tamanho e Rerrolagem no ritual; as demais, uma. Está na fonte atual; a ficha não monta um ritual automaticamente. |
| 101 | A Cortina traz o teto pelo Refino: 1–3, 150 m; 4–6, 300 m; 7 ou mais, 400 m. |
| 193 | As sete Origens e os dois ramos da Restrição Celestial substituem os Legados mecânicos. Há 8 catálogos, 14 marcantes e 67 menores. Na FICHA PESSOAL, marcante e duas menores têm menu, texto e frequência; Legados de história são texto livre, sem efeito. Ofício compatível e CE4 ficam registrados com a indicação de aplicabilidade. A FICHA espelha os nomes e frequências, e o painel mostra somente as escolhas e os Legados de história. |
| 194 | O Ataque sem Prenúncio traz a ordem de anúncio do R47 no texto da capacidade extraída. |
| 195 | Morrendo: Aguentar `ROUNDUP(máximo/4)`, sem teto; Insistir `MIN(ROUNDUP(máximo/3),15×Classe)` na primeira escolha da cena e `MIN(ROUNDUP(máximo/2),15×Classe)` nas seguintes. O prazo é 3 rodadas menos as Sequelas marcadas; três dão derrota imediata. O descanso longo desmarca todas. Saiu o lembrete antigo de perda de máximo por Insistir. A Levanta e o Segundo Fôlego trazem o texto novo. |
| 196 | Os textos atualizados do Olho adicional, das Origens, dos pactos, da Progressão e dos Legados de história vêm do R51. |
| 197 | Recomposição recupera `4 × maior Classe`, Categoria de Efeito 2, Ação Padrão e uma vez por descanso curto, como no texto extraído do R51. |

**O fechamento técnico.** A comparação entre CARTEIRA e FICHA considera a margem do miolo com o painel recolhido; a CARTEIRA não mudou. O `Ficha.gs` tinha 958.893 bytes e excedia o teto de 900 KiB do teste. Somente os valores da tabela `origem_cap` saíram para o novo `apps-script/Origens.gs`; a geometria, os estilos e as fórmulas da DADOS continuam no arquivo principal. Todos os `.gs` ficaram abaixo do teto. A junção foi conferida nas seis ordens de carga possíveis e uma repetição não duplica células. Sem `Origens.gs`, a montagem avisa antes de alterar abas.

As regressões passaram a usar as três cartas, as caixinhas, o Híbrido, `Restrição Celestial · Sem Energia`, a criada até o fim da Classe e o painel AV:AX. O comparador confere os valores e estilos do painel, sua mesclagem e larguras; só equipara `""` a célula vazia na serialização das tabelas, mantendo a checagem de estilo. Ele lista todas as diferenças, sem cortar depois das primeiras 40. Os arneses manuais listam todos os trechos envelhecidos antes de gerar. A preparação das cópias para o LibreOffice percorre as células existentes ao adaptar IFS/TEXTJOIN, evitando materializar células vazias, sem tirar verificações. O arnês pessoal executa dois testes Node em cópias isoladas por vez, depois da base limpa, e reúne todos os resultados na ordem declarada; os testes com LibreOffice continuam seriais e a bateria inteira permanece no mesmo escopo de 5 GiB. A bateria falha se o Node estiver ausente, em vez de anunciar dezenove sucessos após pular um teste.

**Conferido.** A bateria completa pós-retomada terminou com `OS DEZENOVE PASSARAM`, saída 0, sob o teto de 5 GiB e sem swap. Incluiu a versão final com as descrições retráteis e o arnês pessoal com duas cópias Node isoladas por vez. Passaram também `regressao-paleta.js` e `regressao-arte.js` após a regeneração final. Os cinco extratores passaram no `--confere`; os três casos selecionados de nível no arnês de invocações detectaram seus defeitos com base limpa. A comparação de planilha terminou em `IGUAIS`. Registros da rodada final: `/home/mizuki/.codex/visualizations/2026/10/14/01a13a4e-5b5b-7582-b8d5-590fcd4ead0a/b46-final-corrigido.log` e `/home/mizuki/.codex/visualizations/2026/10/14/01a13a4e-5b5b-7582-b8d5-590fcd4ead0a/b46-grupo-paleta.log` e `/home/mizuki/.codex/visualizations/2026/10/14/01a13a4e-5b5b-7582-b8d5-590fcd4ead0a/b46-grupo-arte.log`.

**A comparação com o estudo.** As duas abas foram desenhadas por `medidas/ver-aba.py`, a partir do `Ficha.gs` e das células recalculadas, e inspecionadas por renderização local. Na FICHA, o exemplo Vanguarda 10 com Constituição total 4 mostrou vida máxima 93, Classe máxima 3, Aguentar 24, Insistir 31/45 e prazo de 2 rodadas com uma caixinha marcada. Na FICHA PESSOAL, o texto completo da Zenin coube após o ajuste de altura; as outras duas cartas acompanharam a mesma altura, sem cortar texto.

Bate com o estudo: três cartas lado a lado com texto e frequência; Legados de história abaixo; espelho dos nomes e frequências; painel só das escolhas; linha de Morrendo com prazo explícito e as três Sequelas. Diferenças registradas: (1) o R51 usa **Zenin**, em vez do **Zenin · Akashi** do estudo, e a frequência reúne os componentes do clã; (2) a criada recebe nome escrito no próprio menu, sem uma caixa separada de NOME DA CRIADA; (3) a procedência aparece na frequência, sem as etiquetas gráficas DO LIVRO/CRIADA; (4) o painel usa uma caixa mesclada de 720 px, em vez das cartas separadas no painel de 520 px do estudo, e tem altura fixa de 2.217 px para o pior caso do livro, que pede 1.626; (5) ofício e CE4 permanecem visíveis com a indicação de onde se aplicam, enquanto o estudo os omite nas outras Origens; (6) o âmbar do estudo, usado para destacar a proposta, dá lugar às cores de fábrica que a paleta troca. As barras SPARKLINE e a arte com máscara têm limitações nessa renderização local: essas imagens locais não são capturas do Sheets. A conferência nativa posterior está registrada abaixo.

**O roteiro no Sheets.** Atualize **os cinco arquivos** no mesmo projeto: `Codigo.gs`, `Ficha.gs`, `Habilidades.gs`, `Invocacoes.gs` e `Origens.gs`. Monte de novo com `construir()`, continuando se o registro pedir. Esta montagem é do autor do modelo; o jogador apenas copia a planilha pronta. Os máximos calculados não devem ser sobrescritos: use os atributos, escolhas e Buff/Debuff para montar os cenários.

| nº | aba e caixa | o que fazer | valor esperado e conta |
|---|---|---|---|
| 1 | FICHA, Caminho, Nível e Constituição; depois Morrendo | Vanguarda, nível 10, Constituição total 4, Buff/Debuff de vida 0; confirme vida máxima 93 e CLASSE MÁXIMA 3. Deixe as três Sequelas desmarcadas. | Vida: `8+4+(5+4)×9=93`. AGUENTAR **24** (`93/4=23,25`, para cima); INSISTIR 1ª **31** (`93/3=31`, teto `15×3=45`); INSISTIR 2ª **45** (`93/2=46,5 → 47`, limitado a 45). PRAZO **3 rodadas**. |
| 2 | FICHA, SEQUELAS (F48, H48 e J48) e PRAZO (AK41) | Marque duas; marque a terceira; desmarque todas. | Duas: **1 rodada** (`3−2=1`); três: **Derrotado na hora**; nenhuma: **3 rodadas**. Cada caixa conta uma, independentemente de qual foi marcada. |
| 3 | FICHA, DESCANSO | Com duas Sequelas e vida atual 3 do máximo 93, escolha `Longo · fora`. | As três caixinhas desmarcam; PRAZO volta a **3 rodadas**. Vida atual vai a **46** (`floor(93/2)`). O menu volta a `Escolha o descanso` e O ÚLTIMO DESCANSO registra a alteração. Não aparece o lembrete antigo de perda de máximo por Insistir. |
| 4 | FICHA, as caixas calculadas do Morrendo | Tente escrever por cima de AGUENTAR ou PRAZO; depois mude uma Sequela. | A fórmula volta pelo onEdit; o número e o prazo continuam seguindo o máximo, a Classe e as caixinhas. A linha não guarda tratamento acumulado nem escolhas de Insistir na cena. |
| 5 | FICHA, ORIGEM; FICHA PESSOAL, MARCANTE (D44) e menores (R44, AH44) | Escolha `Descendente`, marcante `Zenin`; abra o menu de uma menor. | A primeira opção é **✎ Criada com o mestre**. Mostra **Cofre da Família** e não mostra **Ensaio Partilhado**. Troque a marcante para **Kamo**: aparece **Ensaio Partilhado** e sai **Cofre da Família**. |
| 6 | FICHA PESSOAL, MENOR 1 e texto (R45) | Escolha `✎ Criada com o mestre`, escreva o efeito na caixa; depois volte a `Cofre da Família`. | Com a criada e sem texto anterior, a caixa fica vazia e aceita o texto do jogador. Voltando à do livro, a fórmula e o texto integral do R51 voltam. Repita na MARCANTE e na MENOR 2. Um nome não listado pode ser escrito diretamente no menu. |
| 7 | FICHA PESSOAL, as três cartas, Legados de história (D54) e CE4 (D58) | Escreva um texto comprido em uma capacidade criada, depois um curto na segunda; faça o mesmo em Legados de história e CE4. | As caixas esticam para caber o texto; a segunda não corta a primeira. Ao apagar, voltam à altura comum. Legados de história não alteram número da ficha. |
| 8 | FICHA, painel depois da coluna AU | Abra o `+`; altere uma capacidade e os Legados de história na FICHA PESSOAL. | O painel começa fechado; aberto, mostra marcante, duas menores, frequência e texto, e os Legados escritos. Não mostra o catálogo. O espelho embaixo das barras acompanha os nomes e frequências. |
| 9 | FICHA PESSOAL, OFÍCIO COMPATÍVEL e CE4 | Escolha Corpo Amaldiçoado na FICHA; selecione um ofício e escreva outro nome. Depois escolha `Restrição Celestial · Restrição corporal` e registre o CE4. | O ofício aceita nome fora da lista; a indicação diz que repara o corpo. CE4 é registro livre da concessão específica da Restrição corporal; não entra como terceira capacidade menor. |
| 10 | INVOCAÇÕES, ficha 1, aquisição, nível inicial/fixo e NÍVEL | Dê nome à entidade, tipo Shikigami de criação, aquisição `Criação`, inicial/fixo **6**, invocador **11**. Depois ponha o invocador em **7**. | NÍVEL **8** no primeiro caso (`min(11,8)`), **7** no segundo (`min(7,8)`). A Classe inicial é 2, níveis 5–8. |
| 11 | INVOCAÇÕES, a mesma ficha | Tipo Maldição domada, aquisição `Maldição domada`, inicial/fixo **6**, invocador **11**. Abra OFÍCIO COMPATÍVEL em outra ficha e escreva um nome livre. | A domada conserva NÍVEL **6**. O ofício é registrado em cada uma das doze fichas e aceita texto fora da lista. |
| 12 | FICHA AMALDIÇOADA, cada PACTO, TAMANHO DO GANHO (primeiro: P523) | Abra o menu nos três pactos. | Cinco opções: **Pequeno, Médio, Grande, Enorme, Sem tamanho (Promessa)**. Não há tamanho mecânico para a Promessa. |
| 13 | FICHA AMALDIÇOADA, VAGAS | Com Essência total **2**, preencha um Permanente e um Pacto de restrição; depois troque o Permanente por Temporário ou Promessa. | Primeiro **⚠ 2 de 1** (`floor(2/2)=1` vaga); depois **1 de 1**, porque só o de restrição continua ocupando vaga. |
| 14 | FICHA AMALDIÇOADA, Cortina e Recomposição | Confira o texto com Refino 3, 4 e 7 e o texto da Recomposição com maior Classe 3. | Cortina: **150, 300 e 400 m**. Recomposição: **12 de vida** (`4×3`), CE2, Padrão, uma vez por descanso curto. São regras de consulta, sem ativar cura automaticamente. |
| 15 | CARTEIRA, PALETA; depois FICHA e FICHA PESSOAL | Troque uma paleta clara e uma escura, abra o painel da Origem e confira as caixinhas e as três cartas. | Fundo, fonte e bordas recebem o tema; nenhum bloco novo conserva indevidamente a cor de fábrica. A CARTEIRA termina primeiro; os demais passos continuam pelos gatilhos simples existentes. |
| 16 | Uma cópia nova da planilha pronta | Use Arquivo → Fazer uma cópia; abra-a e mude capacidade, Sequela, descanso e paleta. | Os comportamentos acima funcionam sem criar gatilho instalável, rodar função de ativação ou pedir autorização ao jogador. A cópia foi testada sem ativação adicional; ver o registro abaixo. |

**Aplicação real no Sheets em 14/10/2026.** A ficha oficial foi atualizada no mesmo arquivo, após cópia de segurança. Os cinco arquivos foram salvos e conferidos por leitura integral no editor; a montagem terminou com `FICHA PRONTA`, 1.375 menus e nenhum link em erro. `verificar()` terminou em `TUDO DE PÉ`; a leitura das nove abas não encontrou erros de fórmula. A paleta anterior, Mizuki · Escuro · ameixa e rosa, foi restaurada.

Na cópia nova, sem ativação ou gatilho instalável, passaram: Morrendo 93/Classe 3 → 24/31/45; três Sequelas → derrota imediata; descanso longo fora → vida 3→46, três caixas limpas e menu restaurado; fórmula sobrescrita com 999 → 24 novamente; filtro Zenin/Cofre e Kamo/Ensaio Partilhado; texto personalizado nas três cartas e restauração do livro; criada inicial 6 com invocador 11→8 e 7→7; domada →6; pactos Permanente+Restrição →2 de 1 e Temporário+Restrição →1 de 1; cinco tamanhos nos três pactos; menus de ofício abertos nas doze invocações; troca clara/escura nas cartas, Morrendo e painel da Origem.

**Pedido adicional: descrições retráteis.** As linhas 45–50 da FICHA PESSOAL formam um grupo aberto de fábrica, com +/− antes das descrições. Menus na linha 44 e frequências na 51 ficam visíveis. A linha 42 explica o controle. Ataque sem Prenúncio, a maior marcante do livro (4.706 caracteres), expandiu a caixa para 2.004 px no Sheets; o final do texto ficou visível, com espaço de sobra. Recolher e reabrir foi testado na cópia e o grupo foi aplicado à oficial. O gerador também incorpora o grupo e o aviso, sem deslocar os campos. Dos arneses manuais, rodaram os três casos de nível da `arnes-invocacoes.py` (9, 10 e 11): base limpa e os três defeitos acenderam suas checagens. Não rodaram os arneses manuais completos de INVOCAÇÕES, FICHA AMALDIÇOADA, `arnes-ficha-pessoal.py` e `arnes-paleta.py`; os 38 trechos do primeiro e os 77 do segundo foram conferidos antes de gerar.

**Arquivos no Google.** [Ficha oficial](https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit); [backup anterior](https://docs.google.com/spreadsheets/d/1mGW7bPsBenSQpSS7TGis6_JJswl2a5tVxcYpq3mHusQ/edit); [cópia de verificação](https://docs.google.com/spreadsheets/d/16kySXV3sJ0wdU2Eq15yqB2jic3-s0wBcu1jCxSrIkPE/edit).

#### B47, andamento de 14/10/2026: a aba ANALISE para o bot (fase 1 testada no Sheets; 1 falha no validador local)

*O plano inteiro (ANALISE e CONFIGURAÇÃO, estudos aprovados, o esquema de chaves) mora fora do repositório, em
`/media/mizuki/HD Externo II/Claude/Planejamento-ficha/B47-analise-e-configuracao/` (PLANO.md, ESQUEMA-ANALISE.md e os dois
estudos em HTML). Decisões do Mizuki: a CONFIGURAÇÃO na forma B, fixa em Mizuki Escuro, para mestre e jogador, com conteúdo
custom de "tudo"; o bot só responde no chat; títulos sem artigo; a aba se chama ANALISE, sem acento.*

**Feito (fase 1):** `ficha-v01/analise.py` monta a aba ANALISE, oculta, fora da troca de paleta, com quatro colunas
(chave, valor, célula, parte) e 2.650 chaves além do cabeçalho: entradas da FICHA (atributos, marcos, perícias, ofícios, TRs,
Sequelas, Buff/Debuff), da FICHA PESSOAL (Origem, equipamento, itens, missões, treino de armas), da FICHA AMALDIÇOADA
(cada lugar de feitiço com as peças juntas, passivas, aptidões, pactos) e da INVOCAÇÕES (cada ficha e cada carta),
resultados e avisos. Vai num arquivo à parte, `apps-script/Analise.gs` (482 KB), juntado pelo `juntarAbas_`; o
`Codigo.gs` devolve a conta a quem escrever nela.
O leitor de teste `ler-analise.py` (raiz) lê a aba pelo link aberto (CSV do gviz) ou da ficha gerada recalculada no
LibreOffice, normaliza os valores (vírgula decimal, VERDADEIRO/FALSO) e responde como o bot: aprovada ou reprovada, com
os avisos. `python3 ler-analise.py --teste` passa (2.650 chaves; a ficha em branco sai reprovada pelas perícias que
faltam escolher, o que está certo). A ANALISE entrou na lista de abas do `decisoes-ficha.json` e no `comparar-ficha-01.py`,
e o `conferir-ficha-xlsx.py` ganhou quatro checagens dela.
**Conferido na implementação original:** conferir-ficha-xlsx (A FICHA CONFERE), comparar-ficha-01 (IGUAIS), conferir-decisoes, regressao-construir.js,
regressao-paleta.js, regressao-pessoal.js e o `ler-analise.py --teste`. Na implementação original, o `rodar-tudo.sh` inteiro ainda não havia rodado; a rodada final está registrada abaixo.
**Teste no Sheets (roteiro):**
1. Colar os seis `.gs` (`Codigo`, `Ficha`, `Habilidades`, `Invocacoes`, `Origens` e o novo `Analise`) e montar.
2. A aba ANALISE existe e está oculta (Exibir › Abas ocultas), com 2.650 chaves e última linha com dado em 2.651.
3. Escrever qualquer coisa numa célula da coluna B dela: a fórmula volta.
4. Com a ficha aberta por link, rodar `python3 ler-analise.py <link da ficha>`: tem de listar as chaves e o veredito.
5. A troca de paleta não pinta a ANALISE.
**Teste nativo iniciado em 14/10/2026.** O B47 já estava no commit `220d76d` ao abrir esta rodada; só o prompt de teste estava no `git add`. Nenhum commit ou push foi feito nesta rodada. Backup antes de montar: [cópia de segurança](https://docs.google.com/spreadsheets/d/1m401H6QPAsxCbvGypwW1P7mWkmwgoxXphgAChR01r5E/edit). O backup não recebeu execução nem ativação; o teste usa o projeto já ligado à oficial.

A primeira montagem terminou às 15:50:21, após início às 15:36:04 (14 min 17 s, incluindo a tentativa que falhou no serviço do Google e os intervalos de continuação). A soma das etapas concluídas foi de 626 s; a ANALISE levou 31,6 s. A primeira tentativa parou às 15:36:57 em `criarAba_`, com erro do serviço Spreadsheets, não com a exclusão da última guia. As tentativas seguintes terminaram com `FICHA PRONTA`, 1.375 menus e nenhum salto em erro.

| defeito encontrado | esperado | observado antes da correção |
|---|---|---|
| ANALISE!B5, B9 e B2643, pelo CSV | `Ciclo Maldito R51`, `Latente` e `Falta: 9 perícias e 2 ofícios, ou 10 perícias sem ofício` | os textos vinham vazios; os mesmos valores estavam certos na leitura nativa. O leitor dizia `APROVADA` para a ficha em branco. O gviz escolhia tipo numérico para a coluna B mista e descartava os textos. |
| ANALISE!A1:D2651 | folha neutra, sem tema | fundo `#120F1D` e texto `#F4F1F7`, herdados do padrão do gerador. |
| ANALISE!C2651 | `'FICHA PESSOAL'!AN86` | `FICHA PESSOAL'!AN86`: o Sheets tratava a primeira aspa do literal como escape. |

Correções feitas somente no gerador: todos os valores da coluna B saem como texto, inclusive números e caixas 0/1; os endereços começando por aspa saem como fórmula de texto; a aba declara fundo branco e texto preto próprios. `ficha-v01/monta.py` transmite esse padrão ao emissor. Os `.gs` foram regenerados, sem edição manual. `ler-analise.py` não mudou. Antes da correção, o teste de edição de ANALISE!B26 já passou: ao escrever `teste B47`, voltou `=N(FICHA!$D$80)`, valor 0, com o aviso no canto.

A primeira bateria identificou apenas uma diferença de fundo entre o arquivo local (sem preenchimento) e o script (branco); foi interrompida antes dos testes longos. O gerador passou a gravar fundo branco também no arquivo local e foi regenerado novamente. O script da ANALISE permaneceu idêntico ao já enviado.

**Roteiro nativo concluído, itens 1–7.**

| item | resultado na ficha oficial |
|---|---|
| 1 — seis scripts e montagem | Os seis arquivos foram substituídos e conferidos por leitura integral; o Analise.gs corrigido também foi conferido contra a regeneração final. A montagem corrigida terminou em `FICHA PRONTA` às 16:13:01: **15 min 22 s** desde 15:57:39, incluindo a tentativa com erro e as pausas de continuação; **662 s de etapas concluídas**. ANALISE: **10,8 s**. `verificar()` terminou em `TUDO DE PÉ`. |
| 2 — existência, ocultação e limites | ANALISE não aparece na barra de guias e aparece no menu de todas as páginas. Cabeçalhos `chave · valor · célula · parte`; **2.650 chaves**, última linha com dado **2.651**. As linhas 2.652–2.653 e as colunas E:L são margem vazia do transporte, sem chaves extras. Ao finalizar o teste, foi ocultada novamente. |
| 3 — referências e caixas | Formato **1**, ficha **1.0**, livro **Ciclo Maldito R51**, Origem **Latente** = FICHA!X11. ANALISE!B26 e B98: **0→1→0** ao marcar/desmarcar FICHA!D80 e F48; o leitor por link também leu **1** nas duas. Defesa **11** em ANALISE!B2617 = FICHA!D59. Aviso de ANALISE!B2643 = FICHA!AK92, texto integral da falta de escolhas de perícia. As marcações foram restauradas. |
| 4 — fórmula devolvida | Escrita de `teste B47 final` em ANALISE!B26: voltou `=N(FICHA!$D$80)&""`, valor **0**, e apareceu o aviso de caixa calculada. Aba ocultada depois. |
| 5 — paleta | Troca para Mizuki Claro e retorno a **Mizuki · Escuro · ameixa e rosa**, a paleta anterior. As **10.604 células usadas** da ANALISE conservaram fundo branco e texto preto nos dois temas. O relatório de paleta confirmou os **37 passos concluídos**, sem ANALISE na lista. |
| 6 — leitor por link | O comando solicitado terminou com saída **0**, **2.650 chaves**, cabeçalho e textos completos, **REPROVADA: 1 aviso(s)** pela falta de perícias da ficha em branco. Nenhum formato cru inesperado; caixas saem como texto 0/1 e são normalizadas para inteiros. Saída inteira em `leitor-final.txt` na pasta de evidências abaixo. |
| 7 — B46 preservado | FICHA, FICHA PESSOAL, FICHA AMALDIÇOADA e INVOCAÇÕES foram abertas e inspecionadas nos temas claro e escuro. Cartas, agrupamento retrátil, Morrendo, Sequelas, técnica e lista de invocações montaram como no B46. A leitura de **dez abas** em **12 faixas limitadas** encontrou **zero erros de fórmula**. |

**Evidências nativas:** `/home/mizuki/.codex/visualizations/2026/10/14/01a13a4e-5b5b-7582-b8d5-590fcd4ead0a/b47/`: montagens inicial e corrigida, `verificar-final.txt`, `paleta-final.txt`, `registro-nativo-final.json`, saída do leitor antes/depois e capturas das abas. A oficial termina em branco, com as duas marcações de teste desfeitas, paleta original e ANALISE oculta. Nenhuma execução ou autorização foi feita no backup.

**Bateria final concluída: 18 dos 19 validadores passaram.** A rodada inteira após a regeneração final terminou em `ALGUM VALIDADOR FALHOU`, saída 1, com teto de 5 GiB, sem swap e limite de duas CPUs. A única falha foi na comparação integral do ABAS em `regressao-amaldicoada.py`, linha 1342: o JavaScript do teste carrega `Ficha.gs`, `Invocacoes.gs` e `Origens.gs`, mas não carrega o `Analise.gs` novo. Compara **9 abas com 10**, e acusa a checagem das fileiras copiadas. Não há célula divergente: as **772 fórmulas**, os **479 rótulos/valores** e as **1.368 mesclagens** da FICHA AMALDIÇOADA passaram. Uma leitura isolada de diagnóstico confirmou que as nove abas comuns são iguais; incluindo `Analise.gs` somente nessa leitura, as dez abas também são iguais, na ordem original. Nenhum arquivo de teste ou script gerado foi editado para contornar a falha. O validador ficou sem correção porque o pedido restringe os consertos ao gerador.

Os **114 defeitos simulados** do arnês pessoal foram detectados e o contra-teste ficou verde. A regressão de INVOCAÇÕES passou e o comparador final terminou em `IGUAIS`. Depois, passaram `regressao-paleta.js` (`TODOS PASSARAM`, saída 0) e `ler-analise.py --teste` (`TESTE: OK`, saída 0), um por vez sob o mesmo teto de memória. Não rodaram os arneses manuais fora da bateria. Registros preservados na pasta de evidências: `b47-final-corrigido.log`, `b47-paleta.log`, `b47-leitor-teste.log` e `b47-diagnostico-comparador.log`.

**Saída inteira do leitor pelo link, com a ficha oficial em branco e a ANALISE oculta:**

```text
2650 chaves · {'cabeçalho': 4, 'entrada': 1629, 'resultado': 601, 'aviso': 416}
  formato.versao = 1
  ficha.versao = '1.0'
  ficha.livro = 'Ciclo Maldito R51'
  nome = ''
  caminho = 'Escolha seu Caminho'
  origem = 'Latente'
  nivel = 2
  vida_max = 0
  defesa = 11

REPROVADA: 1 aviso(s)
  - aviso.escolhas_de_pericia (FICHA!AK92): Falta: 9 perícias e 2 ofícios, ou 10 perícias sem ofício
```

**Pendência fora do gerador:** incluir o novo arquivo no carregamento do comparador de `regressao-amaldicoada.py`; ele permanece sem alteração nesta rodada. Os sete itens do teste nativo da fase 1 foram concluídos. Nenhuma regra ou desenho das fichas foi alterado. A fase 2, CONFIGURAÇÃO, fica para outra rodada.


## Parte 3a · implementação autorizada (15/10/2026)

Usuário aprovou prosseguir após as correções de borda e listas do ESTUDO CUSTOM. Testes visuais e mecânicos devem acompanhar a implementação. Origem aceita BASE DO LIVRO opcional: uma base existente herda seu funcionamento; “Nenhuma” permite Origem inteiramente nova, escolhendo Fundamento, Manejos, Técnica Marcial com energia ou sem energia. Sem base, não herdar capacidades/benefícios exclusivos de uma Origem existente; cadastrar capacidades e alterações numéricas em BÔNUS E MUDANÇAS. Essas decisões foram confirmadas explicitamente pelo usuário. Não reabrir aprovação global do protótipo.

Ainda não há alteração de produção custom na planilha. Base local da parte 2 preservada em evidencias-custom/base-parte2-local.xlsx. Implementação em andamento; manter oficial e bot intactos. Sem commit/push.


## Parte 3a · integração local em teste (15/10/2026)

Código novo em ficha-v01/custom.py: 25 cartões J:O, oito tipos, sete campos fechados + seis livres, listas dinâmicas estritas, diagnósticos por registro, catálogos combinados, menus e contas de equipamento/Origem. Origem sem base e quatro rotas aprovada; não reabrir. ANALISE 5 tem 6.174 chaves e preservou integralmente as 5.274 anteriores no teste estrutural. Novos arquivos Custom.gs (apoio) e Pessoal.gs (valores da FICHA PESSOAL); Origens.gs também transporta diagnósticos custom e AnaliseFontes.gs inclui C:D. Todos abaixo de 900 KiB na geração 04 (maior 806.439 bytes). Nenhum commit/push.

Geração 04 completou. Corrigidos sobreposição J6:O7 com reserva J7:O8 e preservação do Buff de Proteção. Primeira regressão mecânica: custom vazio IGUAIS em todos os valores preexistentes; cenários preenchidos tiveram #NAME? porque LibreOffice exige prefixo OOXML _xlfn para SWITCH/TEXTJOIN. Mini teste isolado comprovou a diferença; adaptação apenas no calculador de teste, preservando fórmulas nativas. Segunda rodada em execução sob 3G/duas CPUs, log evidencias-custom/regressao-custom-02.log. Não declarar mecânica aprovada antes de ler o fim.

Cópia nativa ainda SEM cartões de produção; oficial e scripts vinculados intactos nesta rodada. Preparador pontual em evidencias-custom/preparar-custom-nativo.js lê os .gs gerados, compara com HEAD, prepara 122 mudanças de conta e oito menus; não importa XLSX e não grava no Google. Guardas pendem de leitura nativa fresca. Pedidos de painel precisam manter lotes curtos (os blocos de 40 linhas ficaram com 69KB; reduzir para 10 antes de aplicar). Depois da regressão: validações, migração, testes/inspeção visual de todas as abas afetadas, atualização e conferência dos dez scripts vinculados. Ainda medir construir() nativo numa cópia descartável antes de fixar capacidade final. 3b/3c só após usuário testar 3a.

---


### 15/10/2026 · parte 3b aprovada e em implementação

Usuário aprovou o desenho/capacidade de 133 registros (1 Caminho, 1 Trilha, 131 curtos) e BASE DO LIVRO opcional da Trilha. Categorias são categorias de arma; rótulo esclarecido. Código em custom_progressao.py acrescenta os cartões sem mover os anteriores, listas livro + custom, contas de vida/PE/dado, treinos, especializações, textos por nível e BÔNUS E MUDANÇAS para linhas novas. ANALISE 6 é aditiva; 6.174 chaves anteriores preservadas. Nova geração: 7.385 chaves, três arquivos Progressao*.gs; maior arquivo 821.457 bytes.

Primeira calculadora local conferiu Caminho 49 vida/35 PE, atributo e especialização, troca por zero, custo de troca por arma, Trilha Múltiplas Invocações (4 ativas/4 famílias), texto por nível, duplicatas e números/atributos inválidos. A checagem estrutural teve falso desvio de representação (antes do transporte SPARKLINE / escape de texto); corrigida para comparar o mesmo estágio emitido e passou. Repetição completa incluindo vida rolada pendente.

ATENÇÃO: ainda não instalado na revisão nem scripts vinculados. Falta montagem simulada/nativa e inspeção visual. Não publicar oficial, não fazer commit/push. Continuar com testes locais, guardas da migração pontual em medidas/preparar-progressao-nativa.js, instalação nativa e rollback dos dados de teste. Não registrar tarefa completa antes desses passos. Evidências em ../evidencias-3b/.


### Retomada após interrupção · 15/10/2026

Parte 3b instalada PARCIALMENTE na cópia de revisão 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0: estrutura, DADOS_PROGRESSAO, painéis, menus, reparo dos fundos e 568 mudanças de contas aplicados. 280 células anteriores conferidas por guarda: zero divergências antes da escrita. ANALISE ainda formato 5; faltam 82 pedidos do grupo contrato do manifesto. Nenhum dado temporário de jogador foi inserido. Oficial intacta. Não reaplicar mesclagens/grupos do painel.

Scripts vinculados: somente Código.gs e Ficha.gs enviados e conferidos integralmente; Analise.gs e demais existentes precisam conferência/envio, mais três Progressao*.gs novos. Navegador desconectou em colagem grande; retomar com lotes menores. Não há montagem nativa 3b medida.

Testes locais: regressão de progressão, construção simulada, 122 verificações de paleta e leitor passaram. ANALISE 6 gerada tem 7.387 chaves, preservando as quatro colunas das 6.174 anteriores (exceto versão). Regressão 3a completa teve UMA falha ligada ao FILTER de CP3 no LibreOffice 24.2; fórmula CP3 idêntica à base. Necessário contraprovar no Sheets, sem enfraquecer teste. Evidências em ../evidencias-3b/. Próximos: concluir scripts/contrato, testes mecânicos nativos com restauração, inspeção visual de todas as abas afetadas e montagem na descartável. Sem commit/push.


### 15/10/2026 · migração 3b e testes nativos concluídos; medição em andamento

ANALISE 6 instalada: 7.387 chaves únicas, zero erros de fórmula. Testes nativos passaram: Caminho 49 vida/35 PE; vida rolada 45, dado acima de d8 rejeitado; perícia 5/ofício especializado 3, troca por zero; Trilha herdada Múltiplas 4/4 e sem base com efeitos 5/5; duplicata e número/atributo inválidos diagnosticados. Caso Latente + Tentativa e Erro passou no Sheets (CP3 retorna a marcante, D51 sem aviso), contraprova da limitação FILTER do LibreOffice. Seleção real de Caminho preencheu perícia custom fixa, marcou Acrobacia e apenas categoria Yumi. Entradas e seis mudanças auxiliares do onEdit restauradas; 76 entradas relidas sem diferenças. Auditoria de 13 abas de produção, em faixas limitadas, zero erros. Evidências testes-nativos-3b.json e auditoria-nativa-restaurada.json.

Texto longo revelou corte: corrigido em custom_progressao.py + Codigo.gs com expansão dos pares de cartões na CONFIGURAÇÃO e espelho da FICHA. Nativo mostrou descrição integral e final nos dois locais. Novas regressões de expansão + construção completa simulada passaram (regressao-construir-texto-longo-final.log). Reaplicadas 307 bordas da nova área da FICHA após verificar ausência na coluna direita. Dados do segundo ensaio restaurados; falta última leitura de conferência.

Os 13 scripts foram enviados, GRAVADOS e conferidos novamente após recarga. Ctrl+S/Salvar deixou a interface em espera; executar indice(), função só de leitura, concluiu a gravação. Manter um único editor; abas paralelas podem devolver estados antigos. Editor atual no Brave, projeto de revisão.

Medição NATIVA 3b começou às 16:05:18 de 15/10. Arquivo temporário MedicaoProgressao.gs no projeto da revisão, função medirProgressaoB47; destino fixo descartável 12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc, título TESTE DESCARTÁVEL — base B47 — construção custom R52. Guardas impedem revisão/oficial como destino. Chave ScriptProperties B47_MEDICAO_PROGRESSAO_R52_BASE; continuar rodando a mesma função até complete=true. Fonte temporária salva em evidencias-3b/MedicaoProgressao.gs. Remover arquivo remoto após terminar. Não executar construir() diretamente na revisão! Ainda faltam terminar medição, inspeção visual final das demais abas, documentação e git add/mensagem. Sem commit/push.


### Fechamento da parte 3b · 15/10/2026

Parte 3b concluída na cópia de revisão: 1 Caminho, 1 Trilha e 131 registros de perícia/ofício; 158 registros com a 3a. Treze scripts persistidos e conferidos após recarga. ANALISE 6: 7.387 chaves únicas e quatro colunas anteriores preservadas. Menus/cálculos/treinos/vida rolada/Trilha opcional/entidades testados nativamente. Textos longos expandem configuração e espelho; bordas reparadas; nova área FICHA alinhada à paleta atual sem tocar na CONFIGURAÇÃO fixa. Dados de teste restaurados e relidos, sem diferenças; todas as entradas/fórmulas das novas áreas conferidas. Não há ensaio ativo.

Montagem NATIVA na descartável concluída: 188.812 + 188.009 = 376.821 ms, duas execuções concluídas; falha inicial do serviço Planilhas registrada fora dessa soma. CONFIGURAÇÃO 29,1 s, menus 58,9 s, ANALISE 24 s. Revisão e descartável sem erros de fórmula nas faixas auditadas. 14 abas construídas; CONFIGURAÇÃO com 188 checkboxes e 488 seletores/575 células validadas. Instrumentação MedicaoProgressao.gs removida e ausência confirmada após recarga.

Regressão autônoma de progressão passou, incluindo vida rolada, contrato e valores inválidos; construção simulada e expansão de texto passaram, paleta 122 e leitor passaram. Snapshot 3a gzip versionado e conferido contra 03a459e; validador novo integrado ao rodar-tudo (23). Limitação registrada: uma falha local de FILTER na regressão antiga 3a, contraprova nativa aprovada; teste não enfraquecido. Bateria integral e arnês pessoal longo não repetidos. Maior script 837.710 bytes <900 KiB.

Próxima etapa funcional: 3c, mediante inventário e novo protótipo aprovado, conforme prompt. Não há decisão de regra pendente da 3b. Oficial, bot, compartilhamento e main intactos. Preparar git add e mensagem-de-commit.txt; NÃO commit/push. Roteiro/limitações em TESTE-CONFIGURACAO.md e ESTUDO-CUSTOM-3B.md; contrato em ../ESQUEMA-ANALISE.md. Evidências ../evidencias-3b/.


### Checagem adicional do gatilho (15/10, após fechamento provisório)

ATENÇÃO: uma checagem final encontrou timeout real de onEdit ao escolher Caminho (30,973 s), embora os treinos já fossem gravados. Não considerar encerrada antes de corrigir e retestar. Codigo.gs foi otimizado: habilidadesDaFicha_ lê valores/notas em duas matrizes e não regrava notas idênticas. Mantém textos, notas e alturas. Regressão completa de construção em evidencias-3b/regressao-construir-desempenho-final.log. Ainda em teste nativo; editor precisa perder foco do arquivo antes de salvar para garantir persistência. Arquivo de medição permanece removido.

Há novamente um cenário temporário na revisão (Caminho Teste, atributos nível5 etc.) para medir o gatilho. Backup antes do ensaio: evidencias-3b/qa-antes-tempo-onedit.json. Restaurar diferenças de FICHA e FICHA PESSOAL contra esse backup (userEnteredValue e note) e as 76 entradas contra qa-backup-nativo.json; o último contém faixas vazias sem rowData, portanto restaurar também vazios! Definição de alvos está no roteiro/regressao-progressao. Não finalizar sem restauração/readback.


### 15/10 · diagnóstico do limite na troca de Caminho

Última medição nativa: 30,980 s, limite. Perfil: índice 1,805 s; perícias 3,483 s; Trilha 4,875 s; cartas 5,840 s; troca por arma 5,871 s. Interrupção dentro de fichaMexeNaPessoal_, após isso. O Código agora reutiliza a leitura DADOS para índice/perícias/Trilha, lê notas em matriz e não regrava altura de cartas cujo texto se manteve. Mantém releitura das notas vivas depois das mudanças, para não usar cálculo antigo. Código salvo foi conferido igual ao local.

Novo ajuste em teste: gravarCaixas_ usa RangeList.setValue(true/false), evitando a leitura da validação de cada checkbox por check/uncheck. Só duas linhas funcionais e o comentário mudaram; preparado no editor Brave. Salvamento automático fica preso; aguardando confirmação manual da versão e reteste nativo de ida/volta livro/custom. Regressão completa de construção passou com o ajuste (regressao-construir-treinos-final.log); simulador passou a implementar o método real RangeList.setValue. Logs B47 tempo registram etapas, sem conteúdo de jogador. Não declarar a 3b encerrada antes do reteste e da restauração. O cenário e os backups são os mesmos do item acima (qa-antes-tempo-onedit.json + 76 alvos de qa-backup-nativo.json). Ainda sem commit/push.


### Editor íntegro reposto · último estado

Após a tentativa de salvar, apareceram caracteres acidentais e uma seleção incompleta no editor; o usuário confirmou ter digitado por cima sem querer. Reposto o Código.gs inteiro com colagem única, focando explicitamente o editor. Leitura posterior por locator do textbox + Control+A/Control+C, seguida de AX, conferiu 256.072 caracteres exatamente iguais ao arquivo local. A versão inclui RangeList.setValue para os treinos e logs B47 tempo. Salvamento automático ainda em espera: pedido manual enviado. Não recolocar caracteres nem executar antes de confirmar persistência. Para copiar, focar o textbox “Editor content;Press Alt+F1 for Accessibility Options.” via locator.press; atalhos sem foco podem selecionar a página inteira. Evitar colagens sucessivas sem checar foco/estado.

O restante permanece: cenário QA ativo, restaurar após os dois testes de Caminho (livro/custom), sem commit/push. Arquivos da 3b já adicionados de forma delimitada ao índice; git diff --cached --check passou. Não considerar a parte finalizada só por estarem adicionados.


### Encerramento confirmado da 3b · 15/10/2026, 17h

A pendência do gatilho foi resolvida e substitui os avisos de encerramento provisório acima. Caminho do livro Vanguarda: onEdit concluído em 13,690 s, 65/65 caixas de treino marcadas. Volta real para Caminho Teste: concluído em 15,051 s, somente AM81:AM83 (Yumi), perícia custom Rituais Urbanos preenchida e treinada. Todas as etapas chegaram ao fim, sem erro nos registros. O gargalo era check/uncheck sobre a lista de treinos: a gravação booleana em lote com RangeList.setValue resolveu, mantendo as caixas e as regras. Leituras e notas também foram agrupadas; alturas de textos mantidos não são regravadas.

Código.gs completo restaurado após digitação acidental, salvo pelo usuário e relido após recarga: 256.072 caracteres idênticos ao arquivo local. Regressão completa de construção com o novo método passou (regressao-construir-treinos-final.log). Permanecem logs de duração das etapas no Codigo.gs para diagnóstico; o helper de montagem MedicaoProgressao.gs continua removido.

Cenário temporário retirado. Conferência integral de userEnteredValue/notas da FICHA e FICHA PESSOAL contra o backup: zero diferenças. Os 76 alvos também voltaram ao original, incluindo vazios; três entradas das entidades/técnica vazias; CONFIGURAÇÃO B781 = 2. Auditoria final das áreas novas: zero erros. Capturas finais visual-configuracao-3b-entrega.png e visual-ficha-3b-entrega.png mostram cartões/grades/paleta sem dados de teste. Demais abas e carteira já foram inspecionadas na rodada.

Parte 3b concluída: 133 novos cadastros, 158 com a 3a, ANALISE 6 com 7.387 chaves. A montagem nativa e as demais validações/limitação FILTER constam do fechamento anterior e dos roteiros; bateria integral de 23 e arnês pessoal longo não repetidos. Oficial e bot intactos; sem Excel importado. Próximo bloco: 3c, com inventário e protótipo aprovado antes de construir. Arquivos adicionados ao índice de forma delimitada, mensagem-de-commit.txt preparada, sem commit/push. Não há cenário ativo nem decisão de regra pendente nesta parte.


## Correção solicitada após a 3b · 15/10/2026 (em andamento)

Prioridade atual: corrigir borda/lombada e reorganizar Perícias/Ofícios em duas colunas; Caminho e Trilha custom devem preencher as nove cartas EXISTENTES do grupo 7. O usuário escolheu seguir exatamente os níveis do livro: Caminho 2/7/15/23/30 e Trilha 2/11/19/27. Origens continuam nas caixas/painel já existentes. Não criar espelho paralelo.

Código local implementado em custom_progressao.py e Codigo.gs. Cadastro longo mostra apenas os nove níveis; antigos campos de níveis não aplicáveis continuam como chaves vazias no contrato v6 (7.387 chaves). Nomes/textos de habilidades preenchem cartas existentes; memória do último automático em DADOS_PROGRESSAO CB2:CC10 permite trocar custom/livro sem perder anotações manuais. Perícias 23 e Ofícios 11 mantidos em duas colunas; duplicatas entre colunas contam como inválidas. Removidos 160 finais da FICHA (596→436 linhas); lombada/borda continuadas até o fim. CONFIGURAÇÃO permanece fixa.

Migração nativa JÁ APLICADA na revisão, sem construir() e sem Excel: 37 lotes, guardas de fórmula conferidas, entradas remapeadas. Antes da operação, releitura das entradas não tinha diferenças. Dados anteriores de habilidades custom estavam vazios, nenhum texto manual no bloco removido. Backup: evidencias-3b/correcao-grupo7-antes.json; manifesto e pedidos correcao-grupo7-*. FICHA 436x50; DADOS_PROGRESSAO 157x81; demais tamanhos iguais. Leitura após migração: zero erros de fórmula nas áreas alteradas. Primeiro visual nativo mostrou a borda até a linha436 e tabela de Ofício; captura correcao-pericias-nativa-esquerda.png. Ainda faltam visual amplo, textos/risco de nível e testes mecânicos nativos da correção.

Testes locais: 74 checagens de delta/cartas passaram; regressao-progressao (estrutura e cálculos independentes) passou; construção completa simulada corrigida e aprovada em correcao-grupo7-construir-final.log. A primeira execução detectou que o simulador retorna IF como texto: produção agora só consulta catálogo custom se os flags K7/K8 forem 1, e o teste fornece explicitamente os resultados de fórmula para o cenário de altura. O teste de altura foi atualizado para o cartão EXISTENTE, em vez do espelho removido. Não foi enfraquecida uma falha real. Não repetir tudo sem necessidade.

PENDÊNCIA CRÍTICA: entrega dos seis scripts alterados ao editor vinculado. Código.gs (versão anterior ao pequeno filtro de flags; 257.342 caracteres) e Ficha.gs foram colados e conferidos. Não se confirmou persistência após recarga: Código talvez salvo, Ficha ainda indicava alteração pendente. Configuracao.gs NÃO foi colado; tentativa de copiar seu conteúdo grande derrubou duas vezes a conexão nativa do Brave (hipótese de limite de mensagem, não confirmada). Progressao.gs, ProgressaoPainel.gs e ProgressaoAnalise.gs ainda não enviados. A última versão de Codigo.gs local inclui também filtro K7/K8 e precisa ser reinstalada. Snapshot da versão colada antes do filtro em evidencias-3b/Codigo-grupo7-colado-antes-filtro.gs; HEAD dos seis arquivos em evidencias-3b/codigo-antes-correcao-grupo7/. Não declarar entrega concluída nem testar presumindo persistência.

Navegador: sessão Brave passou de3→4→5 durante reconexões; aba Apps Script2140372220 foi criada pelo agente. Último estado: Debugger unattached. Pedi ao usuário reconectar extensão e manter aba aberta. Não usar handles velhos capturados em closures; função deve receber o tab atual como parâmetro. Não abrir editor concorrente enquanto houver gravações pendentes. Para Configuracao grande, evitar repetir cópia integral que derruba a conexão; considerar colagem/conferência por trechos COM verificações de foco. Não usar modelo interno do Monaco nem APIs ocultas. Todos os arquivos atuais locais estão íntegros.

NENHUM CENÁRIO DE TESTE NOVO FOI ATIVADO. Backup já pronto para teste futuro: evidencias-3b/correcao-grupo7-antes-teste.json (FICHA/FP valores e notas, CONFIG737–792, cache CB2:CC10). Acrescentar backups de outros alvos que usar, como CONFIG879+ e B11:G12. Depois restaurar inclusive vazios e reler sem diferenças. Antes de testar de verdade, concluir instalação/persistência dos seis scripts. IAB aba2 da revisão continua acessível. Brave demais abas são do usuário, não inspecionar.

Decisões da 3c já respondidas: BASE DO LIVRO opcional aprovada para Formas/Melhorias/Restrições/aptidões/Talentos/tipos de entidade; Famílias custom ACRESCENTADAS às nove do livro, mantendo limites. Usuário lembrou que CONFIGURAÇÃO deve permitir alterar quantidades de Livres/Fechadas/Neutras. Inventário do código: Livres e Fechadas são limites fixos do catálogo; Neutras são as restantes. Anunciei protótipo com dois limites editáveis e saldo Neutras calculado, ainda sujeito à aprovação do desenho. Sem implementação nem protótipo3c nesta correção. Retomar3c depois de fechar estes ajustes.

HEAD atual 4e0f6c7 (commit da3b feito pelo usuário). Mudanças desta correção AINDA NÃO adicionadas ao índice. Sem commit/push. Antes de fechar: revisar diff, atualizar roteiros/contrato, git add delimitado e mensagem-de-commit.txt.

---



Teste nativo das duas colunas concluído, 5 verificações passaram; 21 entradas restauradas com zero diferenças, nenhum cenário ativo. Evidência correcao-grupo7-mecanica-nativa.json. Instalação de scripts e cartões nativos ainda pendentes por conexão do editor.

### Experiência da cópia de teste: resultado (26/10)
- Bordas pelo tema (ACCENT5/6): descartadas pelo Mizuki. A troca de paleta passou dos 30 s com o passo do tema e a cópia ficou lenta.
- Listas da DADOS_CUSTOM sem INDIRECT (CHOOSE/MATCH): conteúdo igual nos estados conferidos e FICHA de 10,9 → 4,3 s, mas CONFIGURAÇÃO 19 s e a cópia travou em "alterando" com as três experiências juntas. Inconclusivo; não instalado. Se voltar, testar numa cópia limpa de uma oficial só com essa troca.
- Oficiais intocadas: seguem com o pacote leve fef2a94b. O remendo 33 (bddccf83) continua só no Git.

## Missões enxutas · 26/10/2026 (Claude) · no ramo, fora das oficiais

Retomado do chat que parou no limite (item 4 da fila). Edições no painel de missões da FICHA PESSOAL
estouravam os 30 s nas oficiais. O corte (`r53/diagnostico-android/preparar_missoes_enxutas.js`, pares em
`missoes_enxutas.json`, aplicado depois do `preparar_missoes.js`; o `apps-script/Salarios.gs` é o resultado):
- por fórmula, fora da CONFIGURAÇÃO e da CARTEIRA, a edição não lê mais o estado em DADOS_SALARIOS!L2
  (ninguém o usa nesse caminho; a leitura esperava o recálculo, ~3,3 s no perfil);
- os registros de missões saem numa ida só (`A2:G` aberta), sem getLastRow nem getMaxRows;
- o XP total e o nível vêm dos espelhos da DADOS (CY47:CZ48: `xp total` é a conta da FICHA PESSOAL!AW11,
  `nível` é N(FICHA!AH11)), dentro da faixa AQ4:DP100 que já se lia. Uma ficha sem os espelhos lê como antes.
No caso comum, as leituras caem de 9 para 4 (`r53/testes/missoes_enxutas.js`, com 48 cenários e as mesmas
células, notas e nível). `salarios/testes.js` aprendeu a faixa aberta. Falta medir numa cópia e instalar.
