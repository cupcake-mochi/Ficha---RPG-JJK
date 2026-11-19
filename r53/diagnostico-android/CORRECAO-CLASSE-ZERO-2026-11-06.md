# Alcance e repertório de Classe 0 · 06/11/2026

Base PR71 em `c54f74a`. A R66 descreve os benefícios individuais e
o repertório por nível em Feitiços de Classe 0, no commit
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

- O resumo de alcance dos sete cartões pessoais usa 4,5 m para
  Impulso, Guarda e Firmeza aplicados como benefícios individuais
  sem dano, ou 1,5 m com Toque. O alcance de dano, a utilidade sem
  essas peças e a rejeição de benefícios coletivos seguem as regras
  existentes.
- Se a quantidade ativa passar do teto, cada cartão preenchido
  indica revisão e fica inválido até a seleção voltar ao limite.
  A ficha conserva as montagens e deixa o jogador decidir quais nomes
  manter. Vagas extras com Prática Cotidiana indisponível guardam os
  dados e ficam fora da contagem ativa, com seu aviso de requisito.
- O delta altera 23 fórmulas. Preserva as células de entrada, as 251
  definições de contexto, os endereços da ANALISE e MONTAGENS.

## Validação nativa

Sete cenários passaram em cada descartável (Era e Ciclo). No nível 2,
dois cartões válidos mostraram Impulso a 4,5 m e Toque a 1,5 m, com
duas extras preservadas e inativas. Cinco comuns ficaram em revisão
com o limite de dois. Depois de retirar o excesso, as linhas comuns
3 e 4 voltaram a ficar válidas sem depender da ordem física.

No nível 5, três comuns e duas extras ficaram válidas com Prática
Cotidiana. Sete cartões no mesmo nível ficaram em revisão. No nível
25, o limite subiu a sete e o benefício coletivo continuou inválido.
Ao retirar Prática Cotidiana, a contagem voltou a cinco e preservou os
nomes das duas extras. Os controles de alcance, dados de dano e custo
zero passaram. Foram usados marcadores temporários de preparação para
isolar o cálculo.

Código e Editor foram salvos, reabertos e relidos integralmente nas
duas cópias. Quatro fórmulas voltaram por edição real. Na Era, o alcance
em `FICHA AMALDIÇOADA!R323` e a validade interna em `DADOS_R53!FY41`.
No Ciclo, o alcance extra em `FICHA AMALDIÇOADA!R566` e a contagem em
`DADOS_CUSTOM!B135`.

As 44 entradas temporárias foram repostas por cópia e as duas abas
internas voltaram a ficar ocultas. A releitura comparou 408 células
por cópia, incluindo 266 posições de MONTAGENS, notas e validações.
As únicas mudanças foram as 23 fórmulas previstas, sem erros nativos
nos intervalos. Evidência privada em
`nuvem-b47/saidas/correcao-classe-zero/`.

## Instalação incremental

Geração integral `f655b21dc9d2e46f`. A comparação do pacote expandido
com a PR71 conferiu 280.001 posições e os metadados de 26 abas, com
apenas os 23 valores de fórmula previstos. Passaram os 96 checks do
smoke local. A aplicação nas cópias usou
`preparar_classe_zero.js`, com snapshot das 23 fórmulas e os dois
arquivos do Apps Script na versão ensaiada da PR71. O preparador
verifica os hashes e as fórmulas anteriores. Ele produz gravações
somente em `userEnteredValue` e oferece plano reverso.

A recuperação atualiza 12 fórmulas do Editor. O módulo histórico
recebe as dez fórmulas visíveis originais e a rota curta trata as
fórmulas internas e as duas vagas extras. O atalho continua usando
a assinatura do Editor. Os preparadores históricos devem ser
executados a partir dos respectivos commits ensaiados.

Para uma eventual promoção, obter um snapshot novo antes de gravar.
Se a planilha ou o código divergirem do estado ensaiado, preparar um
delta próprio a partir da versão encontrada e repetir em uma cópia.

Hashes SHA-256 relidos nas duas descartáveis:

- Código `e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e`.
- Editor `13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55`.
