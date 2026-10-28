## Carteira viva: inventário e equipamento · 28/10/2026 · não instalada

PR 31, main ef361cc reconferida sem novos commits. Três perfis novos: equipados
5 campos, equipáveis 88, itens 36; mais quatro notas vivas sem escrita em suas
fórmulas protegidas. Estoque pessoal limpo, fórmulas e instruções restauradas,
catálogos/configurações preservados. Contratos anteriores/assinatura v1 iguais.
Variante decimal nativa 0,1 reconhecida somente nas fórmulas exatas de Volume.
417 cenários direcionados e 101 financeiros passaram; coleção atual 921.
Leitura de 161 entradas/guardas em cada oficial sem divergência ou escrita.
Projeção Sheets API em cópia privada: 133 alvos, 10.450 comparações preservadas,
sem erros; carga 0,3 de 5 igual ao modelo (Traje 1). Cópia na lixeira/aba fechada.
Não é execução Apps Script/diários/OAuth nem criação completa.

Relatório r53/inicializacao/INVENTARIO-2026-10-28.md e README atualizado.
Próximo: campos restantes da CARTEIRA e propriedades de recuperação; depois
entidades/cartões/MONTAGENS. Ainda faltam arte, orquestração/conferência final,
automações/notas vivas, novo responsável e integração drive.file/prova nativa.
Criação bloqueada, fora do pacote/bot. Sem merge/deploy, escopo novo ou chamada
paga. GPT-6 Astra / Alto; revisão focal Médio. Entradas abaixo são históricas.

# técnica e Famílias · 28/10/2026 · não instalada

Main ef361cc incorporada por a72adc0 (PRs 41–43). XP manual/missões congeladas
reconciliados; backup 13 das oficiais registrado por outro trabalho, não reaplicar.
PR 31: dois perfis novos, 11 entradas de técnica e 19 de Famílias, preservando
catálogos/derivados. 782 cenários locais (101/82/78/243/278), mais 87 de XP manual.
84 entradas/guardas lidas em cada oficial, zero divergências e nenhuma escrita.
Projeção Sheets API em cópia privada: 30 alvos restaurados, 8.132 comparações
preservadas sem diferença; duas Famílias custom, inclusive nome com *, Neutra.
Fórmulas via API exigiram variante exata com ponto e vírgula; não confundir com
execução Apps Script. Cópia na lixeira. Relatório TECNICA-FAMILIAS-2026-10-28.md
em r53/inicializacao e README atualizado.

CI Linux do código `763a78bd5fd3d799dd1273f24b6839a5c118d47a` aprovado em
28/10/2026 às 08:39:49 Brasília: [40681468287](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40681468287).
Confirmados os 782 cenários, 15 verificações de abertura, 2.076 de missões e
87 de XP manual, pacote de nove arquivos, sintaxe de 277 fontes Python/220 JS-GS,
catálogo/progressão/Kaori e demais regressões. Run duplicado 40681461827
cancelado. O primeiro run 40681047195 falhou por bases ausentes, corrigidas
sem mudar expectativas. Registro final só documental `[skip ci]`, sem repetir
suíte, instalar pacote ou liberar criação.

Próximo: inventário/equipamento. Também faltam campos pessoais da CARTEIRA,
entidades/cartões/MONTAGENS, arte/recuperações, orquestração/conferência final,
automações, novo responsável e integração drive.file/prova nativa completa.
Criação bloqueada; fora do pacote/bot, sem merge/deploy ou novos escopos.
GPT-6 Astra / Alto; revisão focal Médio. Entradas abaixo são históricas.

# Grau, Origem e treinos da Carteira · 27/10/2026

Smoke inclui `r53/testes/inicializacao_formacao.js`: 190 cenários novos.
Inicialização total 692 (101/80/78/243/190), assinatura financeira v1 fixa,
contrato gerado conferido sem regeneração, falhas por escrita e matriz parcial
recusada. Guardas do salário usam a fórmula instalada pelo módulo Salarios.
Leitura das oficiais foi somente leitura, 457 conferências cada; não executou
os novos perfis no Apps Script. Ver FORMACAO-2026-10-27.md na inicialização.

CI Linux do código `73dffdac18bdd55b9a3b5b52a9cd7665fdc9dfeb` aprovado em
27/10 às 14:00:26 Brasília: [40546156146](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40546156146).
692 cenários de inicialização confirmados no log; pacote de nove arquivos,
regressões, catálogo/progressão/Kaori, sintaxe de 277 fontes Python e 219 JS/GS.
Run duplicado 40546148817 cancelado. Fechamento posterior só documental com
`[skip ci]`, sem repetir a bateria ou publicar pacote.

# Escolhas, recursos e condições da Carteira · 27/10/2026

O smoke inclui `r53/testes/inicializacao_pessoal.js`: 243 cenários novos,
contrato público conferido contra fonte sem regenerar, falhas de escrita,
limites, concorrência, notas, fórmulas e variantes Google. Total de inicialização
502 (101/80/78/243), sem somar ao bot. Guarda de diário acima de 9.000 bytes
UTF-8 exige zero escrita; recursos/condições separados por esse limite real.
Projeção Sheets API não é execução Apps Script: ver
`r53/inicializacao/ESCOLHAS-RECURSOS-2026-10-27.md`. Não libera criação.

# Inicialização parcial da Carteira · 27/10/2026

O smoke inclui `r53/testes/inicializacao_financeiro.js` (101 cenários),
`inicializacao_progressao.js` (80) e `inicializacao_identidade.js` (78).
Executor por perfis fixos, nível/base de XP e 14 textos/notas; não entram no
pacote. A assinatura financeira v1 anterior é uma expectativa fixa conferida.
São provas offline de protocolo/escopo; não executam fórmulas Google nem
liberam criação. Ensaio nativo e limites em
`r53/inicializacao/NIVEL-TEXTOS-2026-10-27.md`. Sem confundir projeção Sheets API
com execução dos diários Apps Script.

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

## Correção do preparo do CI

O run 40681047195 no código a92cba8 passou os 782 cenários, mas falhou em dois
testes recém-incluídos pela main: abertura_salario e missoes_sem_registros.
Ambos usam git show de bases históricas que faltavam no checkout raso.
O workflow passa a buscar somente os dois commits fixos 9536746 e 57117fb,
com SHA completo e depth=1, antes do smoke. Nenhuma expectativa/comparação
foi removida ou alterada. O run duplicado 40681039147 foi cancelado.
