# Retomada no PC · 16/10/2026 · A+B concluídos

Base dos dois ramos remotos confirmada por `git ls-remote`: `ad1b55de210e534b950a3e66ecb2f91f2f2b8d27`.
Checkout independente em `D:\JJK - Project\B47\repositorio`, ramo `codex/b47-capacidade`.
Integração continua em `codex/configuracao-b47`; main não é a base.
Os 20 GS de produção permanecem os de f1ff7a6, sem regeneração.

Correções desta retomada: `14484368662d37e85e3dddff589cfe120a88775d`
(linhas ocultas), `50ba7c7e196b05f912c00803a683b36e27801bb9`
(bootstrap Windows/LF) e `1341d48b7a7801037baab9da3972b6495f7461d2`
(coalescência de formatos, continuação/fracionamento e sete contraprovas).
Os dois ramos autorizados recebem o mesmo fechamento, sem reescrever história.

## Ambiente e portabilidade

Windows 11 Pro 10.0.26300; Python 3.12.14, Node 24.19.0,
Git 2.56.0.windows.2 e Git Bash 5.3.15. Aproximadamente 3,5 GiB livres
na inspeção inicial. Geração pesada não foi repetida; exportações foram seriais.
Python e Node são os runtimes locais fornecidos pelo aplicativo.
O bootstrap passou após reconhecer `.venv/Scripts/python.exe` e restaurar
os bytes LF do checkout. `.gitattributes` agora preserva LF também no Windows.
Smoke passou: 149 fontes Python, 39 JS/GS e catálogo/progressão/Kaori.
Calc não está instalado; a bateria POSIX de infra depende de `fcntl` e fica
impedida neste Python Windows. Não converter esses impedimentos em aprovação.

## Acesso e código nativo

Drive/Sheets e navegador integrado autenticado funcionam. O usuário concluiu
a autorização do projeto de teste; execução de leitura `indice` confirmou acesso.
Projeto vinculado à descartável migrada:
`1_SBUy-sPZ7oH4DtmHuV6JqNediJYeE4xxVIiCb0iAxNs0K6wjsoJX6Ks`.
Snapshot dos 23 GS anteriores e manifesto guardado antes de escrever.
Os 20 GS atuais e o manifesto foram relidos integralmente após recarregar:
hashes iguais, nenhuma divergência. Os três PecasAnalise2–4 foram retirados.
A descartável foi renomeada para TESTE DESCARTÁVEL B47 — PLANILHA E SCRIPT v10 VALIDADOS — 2026-10-16, retirando o rótulo antigo de script pendente.
Os nomes antigos Código/Invocações foram alinhados a Codigo/Invocacoes,
registrados nominalmente no pacote da infra. HTML ausente; manifesto preservado.
A área de transferência transporta CRLF; a leitura foi normalizada para LF
antes da comparação com os bytes canônicos.

O helper `nativo-pc.gs` é de ensaio, não pertence aos 20 GS de produção.
Foi removido da descartável e da cópia funcional. Uma tentativa de remoção
não persistiu; uma aba independente confirmou o arquivo ainda presente.
A exclusão foi refeita, salva e recarregada. Os 20 GS da descartável e da
cópia foram relidos integralmente iguais; manifesto da descartável preservado.

## Provas já colhidas nesta retomada

- ANALISE atual relida pelas quatro colunas: 7.356 chaves únicas,
  zero divergências contra o modelo e zero erros.
- Auditoria Apps Script: zero erros em 277.971 células de 11 abas;
  versão 10 e geração f85ffda549994a3f; 8,343 s dentro da função nativa.
- 57 verificações nativas de fronteiras, cinco catálogos, reuso de Família/
  Perícia nas 12 invocações, autonomia individual e 23/11 menus passaram.
  O ensaio parou ao tentar inserir tipo incorreto por setValue: a validação
  estrita recusou a escrita. As 96 entradas/notas foram restauradas e a API
  confirmou também as validações, sem divergências.
- Três negativos pela API passaram: tipo incorreto excluído do pool,
  duplicata literal exclui ambos, TIPO vazio em cartão vazio não gera aviso.
  Trinta campos restaurados, releitura de entradas/notas/validações igual.
- Reuso dos cinco catálogos nas 12 invocações: 12 verificações passaram;
  nove escolhas distintas de Família preservadas. 96 entradas/notas restauradas.
  Duas asserções de herança falharam por comparar também os nomes dos menus.
  A contraprova nativa mostrou números e identidade canônica iguais ao livro;
  U/V de Melhoria e Q de Restrição exibem deliberadamente o nome custom.
  Leituras originais e falhas conservadas; produção não foi alterada para isso.
- Texto nativo com onEdit invocado: 2.600 caracteres → 88 px; vizinho de
  3.740 → 153 px; limpar um lado conserva 153; limpar ambos → 25 px.
  Última Restrição, 3.520 caracteres → 104 px; limpar → 25 px.
  Etapas entre 2,109 e 2,751 s; conjunto 19,788 s. Valores, notas e alturas
  restaurados. Na cópia funcional sem ativação manual, o gatilho espontâneo
  elevou a última Restrição de 25 para 104 px e a limpeza devolveu 25 px.
  Execuções simples concluídas: onOpen 18,835 s; onEdit 9,216 e 6,181 s.
- Testes locais adicionais: contrato 38, endereços 5, leitor 34, carregador 4,
  sete cenários de texto, envio 8, fórmulas nativas 6 e snapshot 9 passaram.
  Há o risco documentado de endereços em texto INDIRECT; não foi introduzido aqui.

## Construção e cópia funcional

Destino conferido: `12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc`;
projeto vinculado `1KfdoGDV3hUUALfsot73W0n0TBWWj-mfxnsJUIjxfst1GW1OBjqT9QK3K`.
Snapshot prévio de seis GS/manifesto e pacote atual preservado. Os 20 GS e
manifesto novos foram salvos, recarregados e relidos iguais pelo helper da infra.
Primeira tentativa cancelada em 5,06 s; outra falhou no serviço Sheets ao
criar abas e deixou apenas a aba temporária. Estado confirmado antes de
recomeçar do zero, só na reservada. A montagem seguinte concluiu em três
execuções nativas de aproximadamente 169, 208 e 295 s (672 s somados).
Resultado FICHA PRONTA: 17 abas, 1.968 menus, idioma pt_BR. `verificar()`
retornou TUDO DE PÉ. ANALISE inteira: 7.356 chaves, quatro colunas iguais ao
modelo; zero erros nativos nas grades completas de 11 abas.

Cópia funcional nativa: `162TNmcd53kEfCnwDV48UAfsteiwd44gBXocVJu_Bvqo`.
Nenhuma função manual executada nela. Capturas dos cinco catálogos nas
primeiras/últimas vagas e menus consumidores mostram livro e nomes literais.
22 entradas do cenário visual restauradas; 96 campos/notas/validações relidos
iguais. Texto e as 12 alturas dos ensaios também voltaram aos originais.
Interface nativa: recarregar até navegação aceita 4,965 s; editar até indicador
salvo 2,812 s. Releitura pela API 1,187 s confirmou a entrada temporária,
depois limpa e relida vazia. São tempos de cliente/automação e conector,
separados das durações de acionadores, VM e Calc; não há baseline nativo
equivalente nesta retomada para afirmar redução percentual.

A inspeção visual revelou um defeito real da migração: retirar o grupo v9
não desocultava suas antigas linhas 793–874. `lotes.py` agora limpa
hiddenByUser na região reconstruída e reaplica a visibilidade de cada grupo.
Correção pontual conferida em descartável e cópia, sem repetir os 102 lotes:
só 793–794 ocultas, conforme modelo; 96 entradas/notas/validações iguais.
19/19 casos de migração passaram, incluindo contraprova de linhas ocultas
e preservação dos controles anteriores à linha 733. Produção GS inalterada.

Prova conjunta da descartável em [VALIDACAO-NATIVA-PC.json](VALIDACAO-NATIVA-PC.json).
## Revisão nativa concluída

Prova final: [REVISAO-NATIVA-PC.json](REVISAO-NATIVA-PC.json).
Revisão `1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0` em ANALISE 10:
7.356 chaves únicas, quatro colunas conferidas, 509 entradas/notas exatas.
As grades nativas completas de 17 abas foram relidas em 59 blocos:
400.917 células, zero erros de fórmula e zero divergências. Conferidos também
14.676 valores planejados, 3.302 notas e 4.725 validações.

Mais 22.094 células foram comparadas ao backup nas áreas CONFIGURAÇÃO!A1:P732,
DADOS_CUSTOM!CB2:CC10, CARTEIRA e FICHA PESSOAL: zero diferenças inesperadas.
A única mudança esperada foi G160: COUNTIF ajustado automaticamente ao remover
a cauda antiga de DADOS_CRIACAO. Os 25 cartões 3a e seus controles permanecem
preservados. Quatro estudos com propriedades iguais às anteriores. Estrutura:
21 abas, 2.544 mesclagens iguais ao prefixo preservado + modelo novo, três
grupos superiores iguais e somente linhas 793–794 ocultas. CONFIGURAÇÃO tem
1.731 linhas; ANALISE tem 7.357 linhas. Nenhuma aba apagada/reconstruída.

Os 20 GS e manifesto foram relidos integralmente numa aba independente após
a aplicação, todos iguais ao pacote f85ffda549994a3f/f1ff7a6, sem HTML/helper.
A interface nativa mostra as Restrições 29/30 completas no final da revisão;
captura privada `revisao-final-restricoes29-30.png`.

Backup integral final: `1fb3rdEteWSNL1tMEukRTkMirEffFkhPJiCOvewvs-Ug`;
anterior renovado preservado: `1_8p7Py7R6edi3IDyhoUuuyLgRPBt2q2DawfJw2yK4oM`.
23 GS/manifesto antigos em `script-revisao-pre-envio-final.json`.
Metadados completos foram recuperados por respostas limitadas: 28.592
mesclagens e quatro grupos, relidos iguais. O coletor Apps Script contou as
mesmas 28.592 mesclagens antes de expirar nos grupos; seu relatório parcial
não foi usado como snapshot completo. Helper removido dos dois projetos.

Snapshot guardado: 91 blocos de valores/notas, incluindo vazios/caudas;
190.892 células preenchidas. Snapshot da recuperação em 20:00:47.849Z e
releitura idêntica imediatamente antes do envio em 20:09:05.136Z; idade
592s dentro do limite de 15min. Backup e prova conjunta do alvo exato
conferidos antes de gerar/aplicar. O diário de continuação não reautoriza
aplicar o plano desde zero nem reutilizar esses snapshots em outro dia.

## Gargalos e recuperação do envio

O primeiro lote de 629 pedidos teve timeout; valores/notas integrais,
largura e grupo antigos foram relidos inalterados, sem repetição cega.
Novo plano guardado: 120 blocos lógicos, com seis pedidos iniciais isolados
e até 50 merges por fração, demais pedidos na mesma ordem. Cinco testes de
integridade passaram. Ensaio em descartável do backup
`1ZCqyuhel-NMlpXb522nj-tIgs75_-f8V9Wi7LRejAgk`: desmesclagem 27,043s;
623 merges fracionados em cerca de 2s por chamada. Essa cópia é diagnóstico,
não a cópia funcional nem um novo backup.

Bloco 0046: timeout, porém 45 valores/notas/formatos de âncoras confirmados
por releitura; não foi repetido. Bloco 0047 e primeira fração: releitura
confirmou o estado anterior reconstruído do snapshot + prefixo confirmado.

Contraprova nativa isolou trabalho de formatação redundante: updateCells na
âncora já formata toda a mescla. Controles com 1×6 e 4×6 células deram valores,
userEnteredFormat e effectiveFormat iguais com/sem repeatCell adicional,
também visualmente. As 44 escritas sem a repetição terminaram em 3,041s na
descartável; a revisão confirmou as mesmas 44. O gerador deixa de emitir essa
repetição. Sete testes portáteis preservam formatos diferentes, notas e demais
pedidos, e recusam hash adulterado/reinício em zero. A bateria de migração
foi repetida após a mudança: 19/19 aprovados, incluindo todas as guardas.

Os 120 blocos lógicos foram concluídos: 119 respostas da API e um bloco
confirmado pela releitura; 19.222 pedidos efetivos. Foram coalescidas 837
repetições de formato; valores, notas, validações, merges e exclusões de
cauda conservaram a ordem do plano. Não reaplicar os blocos já concluídos.
Diários: `revisao-envio-fracionado/`, `revisao-lote46-confirmacao-releitura.json`,
`revisao-lote47-coalescido.json` e `revisao-envio-coalescido/`.

Oficial, bot, acessos e main intactos. C/D não iniciadas. Pendências externas:
bot/formato 10 e variante histórica do formato 4; limitações locais de Calc e
fcntl no Windows registradas acima. Não há baseline nativo equivalente nesta
retomada para afirmar redução percentual de latência.

## Arquivos e HD anterior

Evidências privadas em `D:\JJK - Project\B47\evidencias\2026-10-16\`:
script-descartavel-antes/depois/conferencia, script-construcao-antes/depois/
conferencia, pacotes, leituras ANALISE, snapshots de cenários, logs nativos,
capturas PNG, preparação/smoke e o patch das alterações antigas da ficha.
Modelos exportados: alvo em `repositorio\nuvem-b47\saidas\pecas-modelo.json`;
base v9 em `evidencias\2026-10-16\modelo-v9.json`, exportada de arquivo Git
isolado em `D:\JJK - Project\B47\base-v9-4187df3`.
Não presumir disponíveis os snapshots da nuvem anterior.

`E:\Claude\Ficha\Ficha---RPG-JJK` está em main/df80ec8, atrás 47,
com alterações preparadas em Ficha.gs, conferir-ficha-xlsx.py e ficha/modelo.gs.js.
Patch integral preservado; nada sobrescrito. Claude2 localizada em
`E:\Claude\Claude 2`, repositório diferente JJK---Project, com várias mudanças
locais e main atrás 59. Consulta feita com safe.directory só no comando,
sem mudar configuração global. `E:\Closure Lab` existe; contém projetos
do bot, que não foram modificados. As pastas antigas não são dependências.

Próxima ação/modelo: **GPT-6.1 Sol, High**, para revisar o checkpoint e acompanhar o uso de A+B. C/D exigem nova autorização.
