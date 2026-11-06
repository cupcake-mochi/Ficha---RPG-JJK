# Frágil em Melhorias de dano, tempo, mira e área · 06/11/2026

Base PR81 `bfe00a5`. Reprodução dos 14 casos em
`AUDITORIA-FRAGIL-CATALOGO-2026-11-06.md`.
Referência R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Frágil exclui Salto, Estilhaço, Quebra Coisa, Rasga Escudo,
Rápido, Reação, Silencioso, Sem Ver, Fura, Sem Cobertura e
Perseguir do teto de gasto interrompível. As exclusões da
PR81 permanecem no cálculo.

Maior, Escolher e Contorno ficam fora do teto quando o cartão
só tem uma área instantânea. O cálculo permite declarar o custo
desses ajustes em uma Forma de área com Fica, Terreno ou Efeito
Próprio. A pessoa que monta o cartão continua declarando quais
compras de fato deixam um efeito interrompível. O texto de
Escolher descreve expressamente a lista que permanece com Fica.
O limite Leve, os descontos e as escolhas salvas são preservados.

## Entrega incremental

Geração `2cc6f80b1789c0f0`. A comparação de 280.001 posições
e dos metadados de 26 abas encontrou mudanças somente nas 753
fórmulas de CK, CP e FX de DADOS_R53, nos 251 contextos.
EditorR53 e MONTAGENS são idênticos à PR81.

O teto usa LET para compartilhar o padrão entre as quatro vagas
de Melhoria. Os dois avisos de Frágil usam o mesmo teto calculado.
O pacote final ocupa cinco partes e 4.228.440 bytes em Base64,
com margem de 21.560 bytes dentro da capacidade reservada.

`preparar_fragil_catalogo.js` valida o Código ensaiado da PR81 e
o retrato atual das 753 fórmulas. O plano escreve apenas
`userEnteredValue`, fornece reversão e troca apenas o bloco
de moldes de recuperação no Código. Passaram os testes locais
de transporte, reversão em pt_BR e en_US e recuperação simulada.

## Ensaio no Google Sheets

Passaram 24 cenários por descartável, Era e Ciclo. Os 14 casos
do pente-fino ficaram em REVISAR com devolução zero e o aviso
específico de Frágil. As três combinações de ajuste de área com
Fica ficaram VÁLIDAS e devolveram 2 pontos. Maior com Terreno
também conservou o crédito. Maior com Estilhaço, sem efeito em
andamento, devolveu zero. Os controles de Passo, Guarda e Fica,
além de Sangra e Barulho em Classe 0, passaram.

As seis fórmulas focais em CK2, CP2, FX2, CK41, CP41 e FX41 e as
21 entradas de teste foram repostas em cada cópia. A releitura
de 624 células por descartável, incluindo 539 posições de
MONTAGENS, encontrou zero diferenças e zero erros. As duas
cópias voltaram à PR81. Evidências privadas em
`nuvem-b47/saidas/correcao-fragil-catalogo/`.

O smoke local passou. A instalação integral e a recuperação por
edição real ficam para o ensaio de instalação desta geração.
