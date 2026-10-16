# Selecionar testes em um clone de nuvem

| Comando | Escopo e entradas | Limite |
|---|---|---|
| `python nuvem-b47/conferir.py --smoke` | Dependências fixadas, referências/hashes, fontes, sintaxe e verificadores catálogo/progressão/Kaori | Leve; não executa montagem nem Google |
| `python nuvem-b47/exportar-baseline.py` | Executa gerador atual uma vez, produz modelo de peças e descomprime baseline anterior do Git | Pesado; saída local em `nuvem-b47/saidas/` |
| `python regressao-pecas.py --modelo nuvem-b47/saidas/pecas-modelo.json --anterior nuvem-b47/saidas/pecas-modelo-anterior.json --estrutura` | Integridade estrutural e preservação do contrato de Melhorias/Restrições na versão 9 | Expectativas atuais ainda 789/395; atualizar com critério durante A |
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
