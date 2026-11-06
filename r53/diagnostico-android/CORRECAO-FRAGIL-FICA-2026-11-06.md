# Frágil e Fica · 06/11/2026

Base PR76 `4911da8`. Regra R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Os casos originais estão em `AUDITORIA-FRAGIL-FICA-2026-11-06.md`.

Precisão fica fora do teto de gastos que pode financiar Frágil.
Nas duas posições de Restrição, só Precisão devolve zero e pede revisão.
Em montagens mistas, a declaração manual continua limitada ao gasto
admissível, depois dos descontos e até o preço Leve. A identificação
dos efeitos interrompíveis das demais Melhorias segue a declaração
de quem monta a ficha.

Fica exige uma Forma de área e pelo menos um dado de dano efetivo.
Isso inclui o arredondamento de Toca a Alma. O controle com Explosão
e dois dados iniciais continua válido quando resta um dado.

## Ensaio nativo

Passaram 13 cenários por descartável, Era e Ciclo. Foram testadas as
duas posições de Frágil, Precisão sozinha, Guarda sozinha, as duas
juntas, declaração acima do custo admissível, Projétil, Linha só de
cura e Explosão com dano antes e depois de Toca a Alma.

As três fórmulas do primeiro cartão testadas no Google Sheets foram
comparadas com a geração final. Após repor as 15 entradas de teste e
as três fórmulas, foram relidas 596 células por cópia, incluindo 532
posições de MONTAGENS, sem diferenças ou erros. As descartáveis
voltaram à PR76. Evidências privadas em
`nuvem-b47/saidas/correcao-fragil-fica/`.

## Entrega incremental

Geração `2048c458847ad339`. A comparação com a PR76 conferiu 280.001
posições e os metadados de 26 abas. Somente 753 fórmulas de DADOS_R53
mudaram, nas colunas CK, CP e FX de 251 contextos. EditorR53 e dados
de MONTAGENS são idênticos à PR76.

`preparar_fragil_fica.js` exige o Código ensaiado da PR76 e snapshot
atual das 753 fórmulas. Gera Código proposto, Código de reversão e
pedidos de gravação e reversão somente de `userEnteredValue`. No
Código, só o conteúdo compactado da recuperação dessas fórmulas
muda. O preparo, a reversão e a recuperação foram testados localmente.
O ensaio nativo foi focal nas três fórmulas do primeiro cartão. A
instalação integral e a recuperação por edição real da nova geração
ficam pendentes antes de uma promoção.
