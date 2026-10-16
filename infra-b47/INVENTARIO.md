# Testes e dependências B47

Inventário na base `4187df3`. A lista executável focal é
`python infra-b47/executar.py --listar`; não há seleção `todos`.
Python deve ser o da `.venv`, preparado pelo bootstrap. Os módulos fixados em
`requirements.txt` incluem openpyxl, Pillow e python-docx e suas transitivas.
Não há pacote npm obrigatório para as regressões Node.

| Seleção focal | Entrada/dependência além do Python | Custo/limite |
|---|---|---|
| `smoke` | Node, fontes, referências e hashes do bootstrap | Leve; sintaxe e três conferidores; não monta ficha |
| `baseline` | Gerador e fixtures Git; destino dentro de infra | Pesado, uma exportação atual reutilizável por recibo/hashes |
| `pecas-estrutura` | Baseline atual + histórico descomprimido | Sem Calc; expectativas de capacidade ainda 789/395 |
| `pecas-calculo` | Baseline, `libreoffice` ou `soffice` | Cálculo local, não nativo; pesado |
| `textos` | Node, baseline | Sete cenários de altura/texto em VM |
| `copias` | Node, `.gs` versionados | Roundtrip/ordens de complementos; pesado |
| `construcao` | Node, `.gs` versionados | Três fases simuladas; pesado |
| `familias` | Gerador, `libreoffice` ou `soffice` | Gera pacote próprio e calcula; pesado, nove posições/autonomia |
| `configuracao` | Workbook atual e comando `libreoffice` | Bônus/trocas/conflitos; pesado |
| `campanha` | `fixtures/base-parte1.xlsx`, `libreoffice` | Histórico formato 5; pesado |
| `custom` | `fixtures/base-parte2-local.xlsx`, `libreoffice` | Histórico formato 6; FILTER não equivale ao Sheets |
| `progressao` | `progressao-base3a.json.gz`, gerador, `libreoffice` | Histórico formato 7, exportação própria; pesado |
| `leitor` | Workbook atual e `libreoffice` | `ler-analise.py --teste`; pesado; avisos precisam ser lidos |
| `comparador` | Workbook atual + original histórico | Compara geração com layout; diferenças exigem contexto |

Todos os comandos exatos, flags e entradas para essas seleções estão no
inventário JSON do executor. Workbook atual é
`ficha-v01/ficha-projeto-m-0.1.xlsx`; ele existe na base, mas presença não prova
que foi regenerado após uma mudança do núcleo. Esta frente não o regenera.
Original histórico: primeiro o comparador tenta `ficha-v01/original.xlsx`
(ignorado), depois `nuvem-b47/fixtures/original.xlsx` (versionado, hash conferido
pelo diagnóstico). Portanto, **original histórico não é impedimento nesta
base**. Nunca confundir essa fixture com snapshot atual de uma ficha jogada.

As expectativas históricas 5/6/7 não provam contrato 9 nem a redução futura.
Atualizações pertencem ao integrador; o executor não troca expectativas ou
reclassifica falhas para obter verde. A redução também pode exigir atualizar
endereços de peças/textos antes de executá-los na combinação.

## Fora da seleção focal

Inventário do roteiro histórico e regressões adicionais, para evitar que a
seleção reduzida seja confundida com cobertura integral:

| Scripts | Entradas/dependências e finalidade |
|---|---|
| `conferir-catalogo.py`, `conferir-progressao.py`, `conferir-kaori.py` | Catálogos/manual/DOCX do Git; já chamados pelo smoke |
| `regressao-exemplos.py`, `arnes.py`, `revisao-cetica.py` | Conferidor de feitiços, manual, especificação e catálogos; regras/exemplos |
| `conferir-decisoes.py`, `arnes-decisoes.py` | Decisões/catálogos; arnês de mutações em cópias temporárias |
| `conferir-ficha-xlsx.py` | Workbook gerado, decisões/layout/fontes; inspeção estrutural/estilo |
| `regressao-kaori-na-ficha.py` | Workbook, exemplo Kaori e `libreoffice`; múltiplos recálculos |
| `regressao-delta.js`, `arnes-delta.py` | Node, `.gs`, layout; conta incremental e mutações |
| `regressao-ficha-pessoal.py`, `regressao-amaldicoada.py`, `regressao-invocacoes.py` | Workbooks/catálogos, `libreoffice`, Node em partes; lotes pesados de recálculo |
| `regressao-pessoal.js`, `arnes-pessoal.py` | Node e `.gs`; simulação/mutações; arnês tem concorrência própria, revisar recursos antes |
| `regressao-paleta.js`, `regressao-arte.js` | Node, `.gs`/arte e simulações de troca visual; não substituem inspeção nativa |
| `regressao-criacao.py --modelo <pacote> --base <xlsx>` | Pacote de Famílias atual, workbook anterior e Calc; parâmetros obrigatórios sem baseline compartilhada pronta nesta frente |
| `rodar-tudo.sh` | Agregado histórico, não inclui todas as regressões recentes; não executado nesta entrega |
| `medidas/daltonismo.py` | NumPy opcional fora do bootstrap; análise visual opcional |
| `repo-conserto/`, `medidas/arnes-regua-da-morte.py` | Históricos de outro projeto, fora da B47 |

Não importar testes Python como módulos para enumerá-los: muitos executam
gerações/recálculos no topo. O inventário foi feito por leitura de código.
Não executar helpers históricos `preparar-*-nativa`, migrações ou lotes contra
o Google com snapshots/IDs da sessão antiga.

## Ambiente diagnosticado nesta entrega

Linux, Python 3.12.14, Node 24.19.0, Git 2.52.0; dependências fixadas conferidas.
RAM disponível inicialmente cerca de 17 GB; limite cgroup 16 GiB, sem swap.
`soffice --version` retorna LibreOfficeDev 26.8.0.0.alpha0; o comando
`libreoffice` não existe. O bootstrap considera Calc presente porque aceita
`soffice`; testes que invocam literalmente `libreoffice` ficam impedidos no
executor. Não foi criado alias nem substituído motor de cálculo. A versão dev
não recebeu validação mecânica nesta frente.

`clasp` não foi encontrado. Sem credenciais/identidades Google configuradas e
sem API Apps Script conectada. Isso impede upload/teste nativo, sem impedir
manifesto, pacote, comparação ou fixtures locais.

Próxima ação: o integrador revisa esta frente e a combina após A.
Recomendação: GPT-6.1 Sol, Medium para revisão das ferramentas; High se surgir
conflito concreto entre capacidades, endereços e contrato.
