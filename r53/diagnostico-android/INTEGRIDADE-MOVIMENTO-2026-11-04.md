# Integridade, movimento e Vigília

Base `528e20e` da PR62, pronta para revisão. Escopo A01, A02, A05 e A06.
Regras conferidas no livro R66, commit `e3058ad…`, em Estágios de Integridade,
Exaustão e Integridade, Movimento e terreno, e Vigília.

- A01. O estágio 2 ou 3 reduz pela metade o movimento do personagem e da
  entidade. No personagem, o limite de Exaustão e a metade pela Integridade
  são comparados, com arredondamento da distância reduzida para baixo em
  passos de 1,5 m. O estágio 4 mostra movimento zero. O tratamento existente
  de carga, do corpo e dos ajustes de campanha permanece na conta.
- A02. Uma entidade com alma e vida máxima zero tem Integridade máxima zero.
  Vida máxima positiva ainda concede mínimo 1. Sem alma mantém a barra vazia.
  Máximo zero não gera um estágio de queda por si só.
- A05. O estágio 3 passa a informar a redução da Classe máxima e o estágio 4
  informa Inconsciente e Derrotado. O texto não altera montagem de feitiços
  nem o registro de SOCORRO. A guarda da ficha sem barra foi preservada.
- A06. Vigília reduz a Exaustão que afeta movimento em um estágio, mantendo o
  estágio registrado. A conta exige rota sem energia, Lapidação 4 ou mais,
  Vigília selecionada e compras dentro do limite. Os efeitos já manuais da
  Exaustão continuam sendo aplicados pela mesa.

Foram usadas duas cópias descartáveis. As fórmulas foram escritas pelo
Sheets e o recálculo foi lido nativamente. A Era passou em 16 cenários e
o Ciclo em nove. A Era também passou no controle adicional com a origem
Sem Energia e os contadores de rota, Lapidação e compra calculados pelas
fórmulas da ficha. Lapidação 4, compra 1 de 1 e Exaustão marcada 2 deram
movimento 9 m com Vigília.

Entre os casos conferidos estão 9 m → 4,5 m e 6 m → 3 m com Integridade e
Exaustão; 7,5 m → 3 m pela escala; máximo de entidade 0 e 1; controle
Sem alma; estágios 3 e 4; Vigília com Exaustão 2 e 3, Lapidação insuficiente,
sem vaga e fora da rota; Corpo Exaurido; carga imóvel; troca de campanha
explícita. Os 57 campos de preparação foram restaurados e relidos iguais
(30 Era, 27 Ciclo). O lote de 40 fórmulas e uma nota foi relido sem erros nas
duas descartáveis.

O plano offline distingue as sete fórmulas e a nota do modelo dos 41 alvos
nas fichas montadas. DADOS_INVOC guarda um molde e preenche as 12 linhas.
O preparador exige o Codigo da PR62 e gera separadamente a atualização
do modelo usado pelo Apps Script para restaurar fórmulas. Esse código é
preparado offline. A instalação nas descartáveis ocorreu depois dos
ensaios de recálculo, para a validação do onEdit descrita abaixo. Uma
aplicação futura exige snapshot atual do código e dos alvos. Não usar
geração integral como migração.

A geração `cb692d3f96e4e754` foi empacotada. A comparação de valores e
notas das 26 abas encontrou somente as sete fórmulas e a nota previstas.
Os alvos do lote nativo coincidem com a saída final do gerador. A matriz
adicional de deslocamento corporal executou 44 cenários no Sheets da Era,
todos aprovados. A aba de QA ficou na descartável para consulta.

O preparador `preparar_integridade_movimento.js` oferece `planejar` e
`prepararCodigo`. A proposta de Codigo.gs tem SHA-256
`9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631`.
O teste do modelo incremental passou também contra os fragmentos compactados
do snapshot privado. A bateria integral do pacote foi interrompida localmente
por pressão de memória. O smoke do GitHub é a execução de referência dessa
bateria.

A primeira rodada de CI identificou comparações históricas de D37 na pilha
51–56 e em SOCORRO. Os testes passaram a conferir tanto a guarda histórica
quanto sua transição exata para o resumo atual. As suítes focais passaram
com 60 e 100 verificações, respectivamente.

## Restauração por edição real

O Codigo.gs foi instalado nas duas descartáveis após confirmar as bases
da Era (PR62, `3767fb0f…`) e do Ciclo (pilha 51–56, `8a0f2ed6…`). Na
cópia do Ciclo, os nove módulos complementares conferidos coincidiam com
a base conhecida. Após salvar e reabrir os dois editores, o Codigo.gs
relido em ambos tinha o SHA-256 da proposta acima. O preparador continua
exigindo a base da PR62.

Em cada cópia, sete fórmulas foram sobrescritas individualmente pela
interface do Sheets com marcadores de texto:

- FICHA!D37 e O67, resumo de Integridade e deslocamento final.
- DADOS_CONFIG!F12 e G12, valores de deslocamento da configuração.
- INVOCAÇÕES!W18, X18 e S24, espelhos de máximo, estágio e deslocamento.

Os 14 marcadores apareceram após a edição. As 14 execuções do acionador
simples onEdit concluíram e restauraram a fórmula exata registrada antes
da edição, sem reposição manual ou pela API. DADOS_CONFIG foi ocultada
novamente nas duas cópias. A leitura final comparou 44 alvos por cópia:
40 fórmulas e uma nota da PR, mais os três espelhos de invocação. Nenhuma
divergência ou erro de fórmula nesses alvos. As 36 fórmulas internas de
DADOS_INVOC foram relidas nessa comparação. A aba auxiliar fica fora da
rota de restauração automática do onEdit.

O teste local `integridade_movimento.js` também passou novamente com o
snapshot privado. A instalação e as edições deste ensaio ficaram nas
descartáveis.
