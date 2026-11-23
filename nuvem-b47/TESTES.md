# Testes fora do smoke: pente fino · 20/11/2026

Base main 78fc37d (depois da pilha de 19/11, merge 8c68939). Rodado no Windows com node 26 e Python 3.12 +
`requirements.txt`. O smoke (`nuvem-b47/conferir.py --smoke`) segue verde: 160 OK. A última etapa dele, que passa os 380 `.js`/`.gs` numa linha de comando só, estoura o limite do Windows (WinError 206); rodada em lotes, passa. No ubuntu do CI isso não acontece. Regra usada: a expectativa só
mudou onde o código atual está certo pela regra vigente; o resto saiu como aposentado (o teste imprime
`APOSENTADO` e sai com 0, o código antigo fica como registro). A planilha não mudou: nenhum `.gs`, gerador ou
fonte de regra foi tocado. As exceções são texto: a spec, o `decisoes-ficha.json` e uma nota de diagnóstico.

## R53: quebrados pelo merge de 19/11

| teste | antes | depois | motivo |
|---|---|---|---|
| `r53/testes/cartoes_diretos_runtime.js` | falha | OK, 589 | 251 cartões (bc4bd46: entram `classe0.6` e `classe0.7`). Na R67 (7b645e5), o PV temporário da Máxima virou função com porta do Amparo; o traço de bloqueado agora é provado na Máxima com o Amparo fechado. |
| `r53/testes/cartao_leve.js` | falha | OK, 50 | Compara o código de 3e77909 com o atual. A linha 1 (`R53_EDITOR_`) é configuração, não runtime: o código antigo roda com a configuração atual. |
| `r53/testes/cartao_versao.js` | falha | OK, 117 | Mesmo motivo, base ce0cb65. |
| `r53/testes/test_compactar.py` | falha | OK | O compactador passou a exigir a ref `sem_volta_declarada` quando o caso é livre (262e264). O teste monta as refs por caso. |

## R53: nascidos na pilha

| teste | antes | depois | motivo |
|---|---|---|---|
| `r53/testes/deslocamento_molde.js` | falha | OK, 22 | A fórmula gerada passou a embrulhar o molde num `LET(movNucleo, …)`. O teste agora prova o envoltório, não mais a cópia literal. A nota está no `DESLOCAMENTO-CORPORAL-2026-11-04.md`. |
| `r53/testes/auditoria_eventos_recursos.js` | falha | OK, 4/4 | O redutor passa por `r53DeltaExecutar_` (15019f2). O simulador ganhou a faixa numérica, `flush`, `toast`, `LockService` e as três funções extraídas. |
| `r53/testes/delta_fila.js` | falha | APOSENTADO | Exige zero diferença contra f484f49 (27/10). Desde então entraram 16 `.gs` novos e a R53_EVENTOS, com 140.060 diferenças legítimas. A paridade de geração é do `pacote_runtime.js` (smoke). |
| os outros 31 `.js` de `r53/testes` fora do smoke | OK | OK | Sem mudança. |
| 7 que pedem arquivo privado (`*_modelo.js`, `fila_loader.js`) | falha | não tocados | Precisam do modelo nativo, que fica fora do repositório. |

## Bateria `rodar-tudo.sh`: expectativa velha

| teste | antes | depois | motivo |
|---|---|---|---|
| `arnes.py` | falha | OK | Usava `Certeiro` e `Junto`, que saíram do catálogo na R53 (`r53/migracao.py`: Certeiro→Precisão, Junto→Mais Um). Agora as perturbações usam `Sem Cobertura` e `Divide`. |
| `regressao-delta.js` + `arnes-delta.py` | falha | OK, 77; 40 perturbações | cb04317: máximo zero explícito trava em 0; máximo em branco é "sem máximo". A âncora do arnês acompanhou a linha nova. |
| `revisao-cetica.py` | falha | REVISAO LIMPA | Agulhas com o texto R53 do livro. A spec ainda dizia "29 das 68 Melhorias"; o catálogo R53 tem 25 das 61. A linha agora traz o número novo e o antigo, com a data. |
| `arnes-pessoal.py` | base suja (o `regressao-pessoal.js` falhava) | base limpa; passo 2 com âncoras novas | Acompanha o `regressao-pessoal.js`. A nota regravada ganhou a linha nova do `notasVivas_` (getNotes em lote, 17/10). A caixa livre ancora na lista `livres` da FICHA PESSOAL, porque FICHA e AMALDIÇOADA também têm uma. O onEdit cego para a aba é pego pelo Volume apagado. Aposentadas: as duas de missão (o bloco saiu) e a do dossiê (desde a leitura curta, tirar a guarda não lê a DADOS inteira). Cada âncora nova foi conferida isolada e acende a checagem certa. O passo 2b (97 perturbações, quase todas com o `construir()` inteiro) não coube no teto de 1 h desta rodada e não foi tocado. |
| `regressao-paleta.js` | falha | OK, 51 | O simulador não tinha `getNumRows/getNumColumns` nem as bordas da faixa; o código passou a ler isso. |
| `regressao-pessoal.js` | falha | OK, 48 | Simulador ganhou `Utilities`, `PropertiesService` e `ScriptApp`. Dois blocos aposentados: o grupo do treino (97abf4f: editar vai por `r53CaminhoLeve_`, coberto por `caminho_integrado.js`) e missão→nível (a célula NÍVEL virou fórmula em cfe4ad2/ed4ff8c, coberta por `missoes_integradas`, `trava_nivel_missao` e `xp_*`). A troca de arma não relê a DADOS (leitura curta, 25/10). |
| `regressao-pecas.py --estrutura` | falha | OK | Duas checagens aposentadas: comparavam com o contrato v9 pela transformação do formato 10 (B47). Depois vieram o formato 11 e a R53: hoje são 18.408 chaves, não 7.356. Fica a checagem de que não há treino custom. |
| `conteudos-b47/comum/testar-carregamento.js` | falha | APOSENTADO | Exige modelo = abas dos `.gs`. Os `.gs` têm as camadas do `r53/` (R53_EVENTOS e 91 chaves da Prática Cotidiana): 26 abas e 18.499 chaves contra 25 e 18.408. Paridade coberta por `pacote_runtime.js`. |
| `comparar-ficha-01.py` | falha | APOSENTADO | A referência é de 14/09: 12.376 diferenças, todas de evolução. |
| `conferir-ficha-xlsx.py` | falha (WinError 206) | falha, 29 de 222 | Passava o programa do node pela linha de comando, que estoura no Windows; agora vai pelo stdin. Rodado contra o `.xlsx` regerado com `monta.py` (o versionado é de 18/10, pré-R53, e não foi trocado): 193 OK, 29 FALHA. **Não aposentado**: cada falha pede julgamento próprio. Grupos: C2 carimbo (2); abas e tetos da R53: `DADOS_R53`, `DADOS_R53_CATALOGO`, `MONTAGENS` e .gs acima de 900 KB (3); leitura do código da troca de paleta no onEdit (8; uma delas só caiu porque o worktree rodou o `regressao-paleta.js` da main, e o desta PR passa); textos R43/R51 do catálogo (4); B42 Buff/Debuff e onEdit da Trilha e das perícias (4); largura, cores, aviso A1, imagens, fórmulas embrulhadas, ordem de criação das abas, INVOCAÇÕES e CONFIGURAÇÃO (8). Ver follow-up. |
| `regressao-custom.py` | falha | APOSENTADO | É o retrato da migração C (formato 11, 17/10): exige as 5.274 chaves da analise-v4 só com formato 10→11. Com a R53 o cabeçalho é formato 12 e livro R53, e chaves de ofício mudaram; na CONFIGURAÇÃO regerada a J6 está vazia. O próprio TESTES.md já o listava como expectativa de etapa anterior. |
| `decisoes-ficha.json` (para `conferir-decisoes`/`arnes-decisoes`) | falha | falta 1 | Atualizadas as fontes da Forma Apoio (saiu na R53) e os textos A3. **C2 fica aberto:** o JSON diz versão corrente `1.0` e a planilha carimba `R53` (b7eaa00). É decisão do Mizuki, não expectativa. |

## Falha real (não é teste velho)

- `regressao-exemplos`: o `conferir_feitico.py` não aplica a devolução Leve do Toque (R53). O Peso nas Mãos dá
  2d8; o livro diz 3d8. O conserto é no conferidor, não no teste.
- `regressao-amaldicoada`, `regressao-invocacoes`, `regressao-familias-invocacao`: o modelo de peças ainda é
  pré-R53 (sem pesos em degraus; as Formas Cura, Apoio, Onda e Efeito saíram). **23/11:** a conta de carta
  passou para o `regressao-r53-planilha.py`, sem LibreOffice. Gabarito: os casos do autor R53
  (`r53/testes/casos.json`, menos os 12 que pedem catálogo próprio) e os 10 exemplos de montagem do livro, cada um
  reproduzido antes pelo avaliador local. Motor: as fórmulas reais da `DADOS_R53` numa cópia descartável da
  oficial, no Planilhas; a própria planilha escreve OK ou o que divergiu. Resultado: 94 de 94 na cópia da Ciclo e
  22 de 22 (lote 3) na da Era, com contra-teste. A carta usa a variante "registro livre" do modelo, que dispensa
  os avisos de tipo de TR; o gabarito da planilha segue a mesma. Evidência: `R53-PLANILHA-2026-11-23.json`.
  Os três antigos ficam como estão, fora do conjunto: o que eles conferiam além da carta (desenho da
  `INVOCAÇÕES`, as 8.190 chaves da `ANALISE`, autonomia das nove Famílias na `DADOS_INVOC`) não tem substituto.

## Ambiente (LibreOffice ausente neste PC)

`regressao-kaori-na-ficha`, `regressao-ficha-pessoal`, `regressao-configuracao` (a parte de estrutura passa),
`regressao-campanha`, `regressao-progressao` e `regressao-pecas` sem `--estrutura` param no passo do `soffice`.
Não dizem nada sobre a expectativa. Verdes sem mudança: `conferir-catalogo`, `conferir-kaori`, `conferir-progressao`,
`regressao-construir` (687 s), `exportar-baseline`, `conferir-copias`, `regressao-arte`, `regressao-textos-custom`
e os 9 `testar-*` da B47.

# Base do delta_fila e editor_runtime aposentado · 27/10/2026

`r53/testes/delta_fila.js` compara a geração com o f484f49 e não aceita
mudança nenhuma. A base antiga, fa54ab6, não tinha o `Caminho.gs` nem o
`Eventos.gs` e acusava 17 mudanças de evolução normal (versão fixa na CARTEIRA
e na FICHA, validações da FICHA PESSOAL, aviso do Ritual em DADOS_AM, somas da
DADOS_INVOC) e a aba R53_EVENTOS. Um defeito plantado na CONFIGURAÇÃO acendeu.
`r53/testes/editor_runtime.js` saiu: dependia do `EditorR53-prototipo.gs`, que
vem do `modelo-r53.json` e de um retrato nativo que não existem em nenhum
checkout. O controlador vigente segue coberto pelo `cartoes_diretos_runtime.js`.

# Integração salarial · 24/10/2026

O smoke inclui `r53/testes/salario_lote.js`: 28 cenários da edição original,
recuperação de escritas/flush e cache confirmado. A fixture
`r53/testes/salario-lote-a2ca590-fixture.gs` é a fonte pública exata do módulo
experimental anterior; seu hash é conferido pelo preparador no teste de
atualização. Não contém dados nativos e dispensa histórico Git no clone raso.
Tempos da VM são simulados; o ensaio em cópia e a medição integral no Google
seguem pendentes, conforme `r53/diagnostico-android/SALARIO-INTEGRACAO-2026-10-24.md`.

# Manutenção Android e Sementes · 23/10/2026

O smoke exige os nove módulos atuais, incluindo `PaletaAndroid.gs`.
`r53/testes/test_sementes.py` cobre a extração delimitada do livro e a faixa;
`r53/testes/paleta_concorrente.js` cobre progresso e término entre callbacks;
`r53/testes/delta_fila.js` exige somente as 12 diferenças esperadas da geração
em relação ao commit fa54ab6, que precisa estar disponível no histórico Git.
Esse comparador é focal, não parte do smoke de clones rasos. Validação nativa
de Sementes e limites da aplicação em `r53/diagnostico-android/FILA-VALIDADA-2026-10-23.md`.

# R53 publicada · 19/10/2026

O diagnóstico detecta a R53, reconstrói seu pacote a partir das fontes GS
versionadas e verifica os arquivos publicados. Não depende do modelo ignorado
em `r53/saidas/`, de Office, de conta Google ou do PC anterior. Partes comprimidas
continuam abaixo de 900 KB; o controlador direto tem orçamento explícito de
1,2 MB, validado pela instalação nativa. Não aplicar o teto antigo de transporte
a fontes legíveis que são incorporadas ao pacote.

O smoke inclui `r53/testes/pacote_runtime.js`: equivalência integral de abas e
geração, autonomia sem módulos antigos, entradas públicas, caminho rápido de
edição e rejeição de parte adulterada. Isso não substitui os testes nativos,
registrados em `r53/ENTREGA.md` e `PUBLICACAO-OFICIAL-R53.json`.

# Histórico: extensões custom e numeração · 18/10/2026

Oficial validada em `acabamento-b47/EXTENSOES-CUSTOM-VALIDACAO.json`.
Os exportadores de domínio seguem antes da apresentação. Após
`configuracao_horizontal.aplica`, `extensoes_custom.aplica` insere linhas em
FICHA, FICHA AMALDIÇOADA e INVOCAÇÕES. Use `extensoes_custom.coord/linha`
para traduzir roteiros antigos; não executar endereços antigos na oficial.

- `node acabamento-b47/testar-familias-custom.js`: treze cenários do controle
  das vagas existentes, sem chamar Google ou conceder benefícios.
- `acabamento-b47/testar-extensoes-custom.py`: exportações sem dados privados
  conferem referências, índices literais, identidade ANALISE, mesclas e grupos.
- `acabamento-b47/aplicar-extensoes-custom.py`: planejador offline de migração;
  exige snapshots atuais. Recusa seletores antigos preenchidos sem migração
  explícita por nome. Não executar na oficial que já foi migrada.
- `acabamento-b47/conferir-extensoes-custom.py`: comparação de snapshots,
  inclusive `--oficial`; 58.511 células e 8.190 chaves/valores preservados,
  corpos vazios sem cadastros válidos e zero erros nas 22 abas.

Testes preenchidos no Google cobriram treino/bônus, atributo de Ofício,
estado da técnica, independência por entidade, troca de vaga e limite Livre.
Os 36 arquivos dos dois projetos foram relidos iguais após recarregar.
Nenhum XLSX foi importado; snapshots/recibos permanecem fora do Git.

# Selecionar testes em um clone de nuvem

## Apresentação horizontal de CONFIGURAÇÃO · 17/10/2026

Oficial reorganizada em 14 listas (400 × 238), sem mudança de regras. Os
exportadores de domínio continuam anteriores à transformação física; use
`configuracao_horizontal.coord/faixa` para traduzir um roteiro de teste nativo.
Não aplicar endereços verticais antigos diretamente à oficial.

`node acabamento-b47/testar-configuracao-horizontal.js` cobre quatro cenários
de altura compartilhada entre categorias, com leitura em lote. O comparador
offline `acabamento-b47/conferir-configuracao-horizontal.py` recebe snapshots
nativos antes/depois e o alvo, sem escrever no Google. Validação nativa final:
2.960 campos, 1.110 validações e 8.190 chaves/valores preservados; zero erros
nas 22 abas; 36/36 arquivos relidos iguais. [Prova](../acabamento-b47/CONFIGURACAO-HORIZONTAL-VALIDACAO.json).

## Fechamento da oficial · 17/10/2026

Oficial B47 concluída e validada; não repetir construir/continuar como teste.
Transporte de criação retomável: `node acabamento-b47/testar-retomada-criacao.js`
(8 cenários), fases continua/acabamento de regressao-construir.js (8/6), total
22 verificações. Fonte e prova em RETOMADA-CRIACAO.json. Payload ABAS/ARTE
inalterado. Comparação integral de exportações nativas aprovada pelo
conferir-oficial.py: zero erros/diferenças, 22 abas e 66.242 fórmulas.
O comparador de estilos resolve estilos por workbook e calcula limites de
grade uma vez; mantém o oráculo semântico, sem ignorar células/estilos.
Regras condicionais conferidas separadamente pela API. A comparação de
exportações é somente leitura local, sem importação no Google.

## Alternativa nativa pós-D · 17/10/2026

Por pedido do usuário, as regressões mecânicas estão sendo executadas em uma
descartável Google copiada da construção final, sem importar XLSX. Os
adaptadores `acabamento-b47/regressao-pessoal-nativa.py` e
`regressao-configuracao-nativa.py` emitem planos offline e conferem respostas
CellData pelas asserções dos testes originais. O envio/leitura ocorre pelo
conector autorizado; os recibos ficam fora do Git. Não executam LibreOffice
e não devem ser apresentados como aprovação desse backend.

Ficha Pessoal: 33 cenários/118 verificações. Configuração: sete cenários/529
verificações mecânicas, incluindo as 86 caixas de C (o laço antigo de somas
cobria só 50). Entradas restauradas e comparadas também em notas, formatos e
validações. Provas `REGRESSAO-*-NATIVA.json` em `acabamento-b47/`.
Item 3 concluído pelo backend Google: também Progressão (15 asserções e 26
estruturais, com referência histórica), Famílias (13 cenários), Campanha e
Custom (comparações históricas completas; diferenças exatas classificadas),
Amaldiçoada (20 fichas, 354 verificações de dados/livro, estrutura e VM).
As receitas e limites estão no topo de `RETOMADA-D.md` e nas respectivas
provas. Nenhuma aprovação do Google é apresentada como execução do Calc.

| Comando | Escopo e entradas | Limite |
|---|---|---|
| `python nuvem-b47/conferir.py --smoke` | Dependências fixadas, referências/hashes, fontes, sintaxe e verificadores catálogo/progressão/Kaori | Leve; não executa montagem nem Google |
| `python nuvem-b47/exportar-baseline.py` | Executa gerador atual uma vez, produz modelo de peças e descomprime baseline anterior do Git | Pesado; saída local em `nuvem-b47/saidas/` |
| `python regressao-pecas.py --modelo nuvem-b47/saidas/pecas-modelo.json --anterior nuvem-b47/saidas/pecas-modelo-anterior.json --estrutura` | Integridade estrutural e preservação do contrato de Melhorias/Restrições na versão 10 | Capacidades 30/30 e comparação por chave; fontes compactadas conferidas explicitamente |
| Mesmo comando sem `--estrutura` | Contas independentes e herança em cartões | Requer Calc; nunca importar o XLSX produzido no Sheets |
| `node regressao-textos-custom.js nuvem-b47/saidas/pecas-modelo.json` | Sete cenários do gatilho de altura/texto em VM com modelo recém-gerado | Endereços atuais; adaptar após a redução |
| `python conferir-copias.py` | Compactação e reexpansão Python/JS das abas do Apps Script | Usa `.gs` versionados; regenerar se o núcleo mudar |
| `node regressao-construir.js` | Construção simulada em três fases e uso da ficha | Pesado; não é construção nativa |
| `python regressao-familias-invocacao.py` | Nove posições, autonomia e orçamento das Famílias | Gera modelo e recalcula com Calc; resultados agora ficam dentro do checkout |
| `python ler-analise.py --teste` | Leitor e contas no workbook local | Requer dependências de cálculo; código de saída/avisos devem ser registrados |
| `bash rodar-tudo.sh` | Roteiro histórico agregado | Não usar como teste rápido nem como única prova da versão final |

Ative `.venv` antes dos comandos acima: alguns testes usam `python3` em subprocessos. O diagnóstico retorna falha se faltar dependência essencial e registra a ausência de Calc separadamente. Nenhum teste impedido é convertido em aprovação.

Os testes `regressao-campanha.py`, `regressao-custom.py` e `regressao-progressao.py` foram escritos para etapas anteriores: contêm expectativas de formato 5/6/7, respectivamente. A versão atual exporta 9. A preparação de nuvem disponibiliza suas entradas e remove os caminhos de pastas irmãs; não elimina falhas reais de expectativa acumuladas. O chat integrador deve auditar/atualizar essas regressões no contexto de A/B preservando casos e contrato. Não afirmar que toda a bateria passa antes disso. `rodar-tudo.sh` ainda não inclui todas as regressões novas e não é alterado por este bootstrap.

As bases XLSX e JSON são históricas independentes, identificadas em `referencias.json`. Para provar migração nativa é necessário um novo snapshot da planilha atual; nenhum snapshot antigo deve substituir essa guarda. As evidências em `referencias-b47/evidencias/` provam apenas o fechamento anterior.

Saídas/logs atuais ficam em `nuvem-b47/saidas/` (ignorada). Publique relatórios pequenos na pasta do seu papel, com SHA exato testado, comandos, resultados, limites e recomendação de próximo modelo/esforço. Não versione modelos de 44 MB repetidos, venv ou logs volumosos.

## Rodada de capacidade · formato 10 local

Roteiro focal serial: `bash rodar-tudo.sh --b47-focal`. Não roda Google. Faz
smoke, exporta a v9 **4187df3 em worktree temporário**, exporta o modelo atual,
gera artefatos e executa capacidade, migração sintética, peças, progressão,
primeira/última Perícia/Ofício, Famílias/autonomia, compactação, construção
simulada, texto e leitor. Resultados e logs em `nuvem-b47/saidas/focal/`.
Falha de instalação/geração interrompe dependentes para não reutilizar modelos
velhos. Os demais testes registram cada falha sem convertê-la em aprovação.

As regressões de progressão/Famílias e as verificações estruturais de
campanha/custom foram atualizadas para o contrato 10. As comparações congeladas
v3/v4 reconhecem somente as transformações exatas já aprovadas no formato 7:
agregar nove Famílias e deslocar Definição uma linha; o hash v3 original e todas
as linhas v4 continuam sendo exigidos, sem aceitar outras diferenças. `--estrutura` em
`regressao-campanha.py`/`regressao-custom.py` verifica apenas a parte anterior ao
cálculo. Não equivale à bateria mecânica completa desses históricos nem remove
a limitação conhecida de FILTER no Calc. `libreoffice` e `soffice` são aceitos
nos roteiros alterados e no leitor. Famílias fornece as tabelas compartilhadas
atuais e abre no máximo três cenários por processo de Calc para conter memória.

`capacidade-b47/previas.py` usa a grade emitida para mostrar cartões vazios,
sem recalcular fórmulas e sem fontes remotas. São prévias locais, não capturas
Sheets. `--png` rasteriza os metadados sem navegador, usando DejaVu Sans como
substituto de Roboto; o ambiente bloqueia navegação file:// no Chromium. `capacidade-b47/migracao.py` e `lotes.py` só preparam artefatos offline;
o [roteiro nativo](../capacidade-b47/ROTEIRO-NATIVO.md) descreve o que exige
snapshot atual, descartável, código salvo/relido e aplicação posterior.

As entradas da tabela inicial de capacidades 789/395 e versão 9 descrevem a
base histórica. A regressão de peças agora exige 30/30 e formato 10; a v9
completa para comparar a redução pode ser exportada por
`python capacidade-b47/exportar-base.py`. Os três fragmentos PecasAnalise2–4
saíram da entrega local e devem sair também do projeto Apps Script no envio.

A integração inclui os testes próprios de `infra-b47/` e as sondas externas com
perfil `b47-v10`. O leitor agora falha se exportar erro de fórmula; namespaces
IFS/SWITCH/TEXTJOIN são qualificados na calculadora local. As validações 3a foram
divididas em auxiliares (máximo 5.031 caracteres); `testar-validacao3a.py` cobre
oito tipos válidos e negativos. `testar-geracao.js` e `testar-envio.py` verificam
arquivos de gerações diferentes e retirada explícita. O roteiro central aceita
`--b47-infra` para seleções do executor da outra frente.

## Retomada nativa parcial

`capacidade-b47/snapshot.py` e seus nove testes normalizam leituras CellData
nativas, sem rede/credenciais. `testar-formulas-nativas.py` tem seis casos de
normalização estrita das fórmulas do Sheets. `testar-equivalencia-lotes.py`
compara efeitos dos lotes offline, incluindo uma contraprova de alteração
retida; não envia nada ao Google. Essas três etapas foram incluídas no roteiro
focal, agora com 26 etapas; o agregado inteiro de 26 não foi executado nesta
retomada. Migração sintética foi repetida: 19/19.

`conferir-nativo.py --leituras <diretorio> --modelo <json> --saida <json>`
audita as leituras privadas da descartável coletadas pelo roteiro. Não acessa
Google nem libera revisão: nível superior sempre PARCIAL quando as checagens
passam. `testar-conferencia-nativa.py --leituras <diretorio> --modelo <json>`
injeta corrupção em memória nessas leituras para conferir a recusa. Sem os
artefatos privados, são testes impedidos, não aprovados por uma fixture vazia.
Eles ficam fora do agregado portátil/CI. Rodada de 16/10: 22 checagens e nove
contraprovas; teste de envio da nova revisão efd8dd8: 10/10; smoke final passou.

[NATIVO-PARCIAL.md](../capacidade-b47/NATIVO-PARCIAL.md) registra os 102 lotes
reais confirmados, cálculos e restauração na descartável. Não houve upload de
Apps Script ou execução de construir/continuar; testes de gatilhos, alturas,
visual Google, latência e migração da revisão continuam pendentes.
