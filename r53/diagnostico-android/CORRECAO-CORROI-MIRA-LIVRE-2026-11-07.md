# Corrói exige Mira Livre · 07/11/2026

A correção parte da PR83 `b6c1ac1` e da auditoria em
`AUDITORIA-MIRA-2026-11-07.md`. A referência é a R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, entrada
Corrói do catálogo.

A árvore de validação acrescenta o aviso `Corrói exige Mira Livre`
quando a peça está em qualquer uma das quatro vagas e a Família
Mira daquele cartão tem outro estado. Nos cartões de entidade,
a leitura usa as Famílias da própria entidade. A categoria Normal
das entidades e a categoria Neutra pessoal recebem a verificação.

A compra continua registrada com seu preço. Os avisos existentes
de Família Fechada e de preço incompatível com Classe 0 permanecem.
Fura conserva o acesso normal a Mira aberta e seu desconto.

## Geração e atualização incremental

Geração `604968957e08baef`. A comparação de 280.001 posições e
dos metadados de 26 abas encontrou mudanças de conteúdo apenas
nas 251 fórmulas de FX em DADOS_R53. EditorR53, os registros de
MONTAGENS, os endereços e as entradas mantêm sua representação.

`preparar_corroi.js` confere as fórmulas anteriores e o hash do
Código da PR83. Propõe a troca das 251 fórmulas de FX e somente
do bloco dos moldes de recuperação no Código. Produz a reversão
e exige snapshot atualizado do destino.

O pacote integral de geração passou no verificador de integridade
e ocupa cinco partes, com 4.249.548 bytes em Base64. A capacidade
reservada é de 4.250.000 bytes, com margem de 452 bytes.

Passaram os testes de transporte e reversão em pt_BR e en_US,
a recuperação simulada e o smoke local. A matriz local conferiu
212 montagens, incluindo as quatro vagas, os modos estruturado
e direto, as modalidades máximas e as básicas.

## Google Sheets nativo

As descartáveis Era e Ciclo estavam com a PR83 instalada. Foram
guardados snapshots atuais de FX2 e da primeira especial das
12 entidades, totalizando 13 fórmulas focais por cópia.

Passaram 104 cenários em cada cópia.

| Cartões | Cenários por cópia | Conferência |
| --- | --- | --- |
| Pessoal | 8 | Corrói nas vagas 1 e 4, com Mira Neutra, Livre e Fechada. Fura com Mira Neutra e Livre. |
| 12 entidades | 96 | Corrói nas vagas 1 e 4, com Mira Normal, Livre e Fechada. Fura com Mira Normal e Livre, em cada entidade. |

Corrói pediu revisão com o aviso específico fora de Mira Livre.
Com Mira Livre, os cartões ficaram válidos. Os avisos legítimos
de Família Fechada também apareceram. No teste de Classe 3,
Corrói conservou preço 5 sem desconto, preço 3 no cartão pessoal
com Mira Livre e preço 4 nas entidades com Mira Livre. Fura
conservou preços 3, 1 e 2 nos respectivos controles.

As Famílias das entidades foram alteradas pelos nove espaços
nativos da própria entidade, respeitando a primeira posição Livre
e a posição aberta Normal conferidas no cálculo. As caixas de
cura e PV temporários indisponíveis receberam o marcador nativo
previsto pela validação.

Foram repostas 330 entradas por cópia, incluindo as nove posições
de Família e os cartões das 12 entidades. A comparação cobriu
5.218 posições por cópia, incluindo 3.647 de MONTAGENS, com zero
diferenças e zero erros nos intervalos conferidos. As 13 fórmulas
focais foram restauradas e relidas integralmente em cada cópia.

As descartáveis voltaram à PR83. A instalação integral da nova
correção e a recuperação por edição real ainda aguardam ensaio.
Evidências privadas em `nuvem-b47/saidas/correcao-corroi/`.
