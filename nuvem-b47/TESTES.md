# Selecionar testes em um clone de nuvem

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
