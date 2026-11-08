# AQ02 · Validação do nível obtido das invocações · 08/11/2026

## Resultado

Texto numérico como `7` agora é interpretado como nível 7, sem promover
a entidade ao nível do invocador. Números inteiros de 1 a 30 são válidos.
Frações, zero, negativos, valores acima de 30, booleanos, texto livre e
erros de fórmula são sinalizados. A entrada original é preservada.

Em Criação e Maldição domada, uma entrada inválida mostra **REVISAR** no
título e na lista. As contas ficam provisoriamente no nível 1; isso não
aprova a entidade nem corrige sua montagem. Campo realmente vazio ou
fórmula que devolve vazio mantém a prévia histórica no nível do invocador.
Nível válido continua limitado pelo invocador. Espaço conhecido e Lista
de ritual continuam acompanhando o invocador, ignorando o campo obtido.

Aplicação incremental e testes concluídos somente nas duas descartáveis
Era/Ciclo. Sem merge, oficiais, ficha de jogador ou PR31.

## Escopo e contrato

Sobre a PR89, o delta tem **36 fórmulas, duas notas e 12 validações**:

- DADOS_INVOC!DH2:DH13: validação tipada; 0 para ausência, -1 para inválido,
  1–30 para um nível válido. Texto só com os dígitos de 1–30 é convertido
  explicitamente, sem conversões ambíguas de separadores ou booleanos.
- DADOS_INVOC!HG2:HG13 e JK2:JK13: aviso no título e na lista.
- INVOCAÇÕES!K46/O12: ajuda; mantida a distribuição original das notas.
- As 12 caixas de nível obtido recebem menu estrito 1–30.

São 50 pedidos por cópia, sem escrever compras, versões ou entradas.
Os 60 moldes vizinhos de apoio são inalterados na instalação; servem à
recuperação dos blocos testados. O preparador também confere esses moldes.
Mantidos os 49 suportes da PR89, os IF da PR88 e o escape da ANALISE.

Não há inserção de linhas/colunas ou mudança de chave, tipo declarado,
fórmula ou endereço na ANALISE. O modelo completo confirmou a preservação.
O valor de `invocacao.N.nivel_fixo`, que já lê DH, passa a -1 quando a
entrada é inválida; 0 continua significando ausência. O campo calculado
`invocacao.N.nivel` usa a prévia mínima 1 nesse caso. O consumidor/bot não
foi alterado nem validado nesta entrega; o aviso visível exige revisão.

## Instalação ensaiada

Backups novos persistidos antes da escrita: código integral, metadados com
formatação condicional, entradas, alvos, vizinhos e MONTAGENS inteira.
Código inicial relido integralmente nas duas QAs:

`ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352`.

O incremento exige essa base, localidade reconhecida e valores/notas/
validações anteriores exatos. Houve nova conferência nativa do pré-estado
antes dos 50 pedidos e releitura de todos os alvos depois deles.
Os 60 vizinhos do snapshot anterior também coincidiram com o suporte.

Código final salvo, projetos reabertos e conteúdo integral relido igual
à proposta nas duas:

`b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e`.

O usuário concluiu as autorizações Google pedidas nas QAs.
`verificarPacoteR53` concluiu nas duas: geração instalada antiga
e142593fdc5be157, 21 abas do módulo, 251 contextos do editor, 249 no módulo,
sem sobras. Essa geração antiga é esperada no incremento.

O código incremental conserva o ajuste da PR89 e depois aplica o novo.
No pacote integral, o modelo já nasce atualizado; o bootstrap confere o
novo estado, sem reaplicar a ajuda antiga da PR89 sobre as notas novas.

## Testes nativos

**240 observações de entidade aprovadas**, com tipos e entradas relidos:

- 192: 24 variantes × dois níveis de invocador (30/9) × duas aquisições
  fixas × duas cópias, distribuídas pelas 12 entidades.
- 48 controles de Espaço conhecido/Lista de ritual com campo obtido
  irrelevante, inclusive inválido: nível do invocador e sem aviso indevido.
- Nível normalizado, limite efetivo, avisos no título/lista e valores
  numéricos de vida/espaços conferidos. Cada entrada manteve o tipo original.
  Não se apresenta isso como nova auditoria de todas as fórmulas de vida.

As variantes incluem números 1/7/30/31/-3/0/7,5; TRUE/FALSE; texto 7,
Nível 7, espaço e 7,5; fórmulas numéricas, de texto, vazia, fracionada,
booleana e com erros NA/divisão por zero; além de célula vazia.
Erros foram injetados só nas entradas de teste, mantidos como entrada e
isolados pelo validador; não propagaram para as contas observadas.

**Seis controles pela interface**, três em cada QA:

1. Menu escolheu 7 e produziu nível 7.
2. Digitar 7,5 foi recusado pelo Google, conservando o valor anterior.
3. Apagar a entrada repôs a prévia no nível do invocador.

**12 recuperações por edição real**, seis por cópia:

| Faixa apagada na interface | Células por cópia | Resultado |
| --- | ---: | --- |
| DH2:DH13 | 12 | Fórmulas novas completas |
| HG2:HG13 | 12 | Títulos completos |
| JK2:JK13 | 12 | Lista completa |
| DG2:DI3 | 6 | Nível e vizinhas iniciais |
| HF12:HH13 | 6 | Títulos e vizinhas finais |
| JJ12:JK13 | 4 | Lista e vizinha final |

A igualdade foi conferida fórmula por fórmula antes da edição seguinte.
Leituras ainda vazias durante o evento foram aguardadas, sem repetir a
edição. Histórico nativo: oito onEdit por cópia Concluído — seis de
recuperação e dois de entrada (menu/apagar). As recusas de fração não
geram edição. Total: 16 onEdit Concluído; duas verificações manuais também
concluídas. Durações não são benchmark de Android ou latência garantida.

## Preservação e artefatos

**49 entradas/cópia restauradas**. Comparadas **86.178 posições/cópia**,
incluindo **85.887 de MONTAGENS inteira (A1:I9543)**. Retornos omitidos da
API foram tratados como vazios. Somente os 50 campos previstos mudaram;
zero diferenças extras em valores, fórmulas, tipos, notas ou validações
lidos. Metadados, incluindo formatação condicional, idênticos antes/depois.
Auxiliares ocultas, visuais restaurados e todas as abas de teste fechadas.

Geração integral **fe4f36eb411d303b**. Comparação de 280.056 posições/
26 abas: somente 36 fórmulas, duas notas e 12 menus/indicadores de estrito;
modelo incremental igual ao integral. Pacote com cinco partes,
3.860.568 bytes Base64; fonte SHA-256
`548d696de460364631914d7f1ec5f8c96cee9569d979264790f594f5d05a6fd7`.
**Pacote integral não instalado.**

Smoke local: 124 verificações aprovadas, saída zero. Testes focais de
transporte, snapshots, suporte, recusa atômica, reversão e recuperação
passaram em pt_BR/en_US, inclusive com o pacote antigo disponível.
Modelo comparado integralmente; verificadores/sintaxe incluídos no smoke.
As guardas offline de suporte e de não interceptar FO receberam ainda
repetição focal depois do smoke; o código Google não mudou com isso.
Primeira geração encerrada com 143 foi descartada como aprovação; a
execução persistente final de geração/pacote/modelo/smoke terminou toda em 0.

Nativo somente em pt_BR. Calc não executado. Não certifica todas as
colagens arbitrárias, mecânicas ou desempenho Android. Avisos mecânicos
legítimos não foram removidos para obter aprovação.

## Revisão e atualização de outras fichas

Ramo `codex/validacao-nivel-obtido-20261108`, empilhado sobre a PR89.
O parecer anterior está no ancestral 0a1ad65. Revisão: Sol/Medium.
Implementação/novo ensaio: Sol/High; sem mudar configurações ou delegar.

Para aplicar futuramente em outra ficha, obter autorização específica e
snapshot atual primeiro. Conferir a base real instalada; o preparador
desta entrega exige o código final da PR89, não uma oficial antiga.
Executar `conferirSuporte`, `prepararCelulas`, `prepararNotas` e
`prepararValidacoes` sobre as leituras atuais; preparar o código, ensaiar
em descartável, salvar/reabrir/reler e conferir todo o delta. Não substituir
o pacote integral nem executar construir()/continuar() numa ficha preenchida.

Evidência sanitizada em `nivel_obtido_validacao_2026-11-08.json`.
Privados apenas em `nuvem-b47/saidas/validacao-nivel-obtido-20261108/`,
ignorado: backups, matriz, pedidos, releituras, recuperações e capturas.
Nenhum snapshot, dado pessoal ou credencial incluído no Git.
