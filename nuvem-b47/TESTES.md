# Selecionar testes em um clone de nuvem

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
Demais regressões continuam pendentes no topo de `RETOMADA-D.md`.

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
