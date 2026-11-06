# Rajada e Tudo ou Nada · 06/11/2026

Base PR75 `af22de9`, regra R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Diagnóstico em `AUDITORIA-RAJADA-ALVOS-2026-11-06.md`.

- Rajada exige Forma individual com dados de dano. Em área ou sem dados,
  o cartão pede revisão e mostra zero tiros no cálculo. Em uso individual,
  a quantidade continua limitada pela Classe e pelos dados disponíveis.
- Tudo ou Nada sem dano gera aviso e devolve zero, na primeira ou na
  segunda posição de Restrição. O cálculo ignora o desconto antes de
  totalizar o orçamento. O bloqueio também cobre o reforço Sem dano e
  montagem comum com função de dano registrada sem alocação de pontos.
  Se Toca a Alma reduzir um dado a zero, a Restrição também não devolve
  pontos. Com dano restante, a devolução volta a ser calculada normalmente.
- Nos cartões de descrição livre, ataque/TR continuam definidos em
  COMO É. Na rota com resolução estruturada, as verificações de Ataque
  e TR continuam ativas. A correção conserva os demais reembolsos.

## Ensaio nativo

Nove cenários por descartável, Era e Ciclo, no primeiro cartão de feitiço
comum. Foram conferidos área, ausência de dano, Rajada com um e seis
dados, Tudo ou Nada nas duas posições sem dano e com dano, Mais Um e
Carregar. Os dois casos de Tudo ou Nada sem dano ficaram em REVISAR
com devolução zero e saldo 3. Carregar manteve devolução 3 e saldo 6
na comparação com as fórmulas anteriores. O primeiro roteiro esperava
2 pontos de Carregar por engano, corrigido pela comparação nativa.

Na geração final, sete cenários foram repetidos em cada descartável.
Toca a Alma com um dado inicial deixou zero dados e zero devolução.
Com dois dados iniciais, restou um dado e a devolução foi 2. As
quatro fórmulas usadas no ensaio foram comparadas com a geração final.

Após o primeiro teste focal, 13 entradas e o recorte de cinco fórmulas foram
repostos em cada descartável. Uma das cinco, FY2, já era idêntica
à da PR75 e ficou fora do plano de instalação. A releitura de 324
células por cópia, incluindo 259 posições de MONTAGENS, após cada etapa
encontrou
zero diferenças e zero erros. O aviso e a devolução zero também
foram conferidos visualmente. Evidências privadas em
`nuvem-b47/saidas/correcao-rajada-alvos/`.

## Entrega incremental

Geração `7b36806bc7e5c2fe`. A comparação do pacote conferiu 280.001
posições e os metadados de 26 abas. Somente 1.004 fórmulas de
`DADOS_R53` mudaram, nas colunas CK, CP, EH e FX dos 251 contextos.
O arquivo EditorR53 e os dados de MONTAGENS são idênticos à PR75.

`preparar_rajada_alvos.js` exige o Código da PR75 ensaiado e um snapshot
atual com idioma, IDs das abas e fórmulas desses alvos. Gera Código
proposto, Código de reversão e pedidos somente de `userEnteredValue`.
A rota de recuperação usa moldes compactos, carregados apenas quando
uma edição atinge os alvos internos. A recuperação das 1.004 fórmulas
e o preparo e reversão foram testados localmente. A leitura de sete linhas
representativas de cada cópia também passou pela guarda de versão.
Para aplicar os pedidos completos, usar lotes por linha com releitura
de cada lote e guardar a reversão correspondente. O ensaio nativo foi
focal nas fórmulas. O Apps Script proposto e a instalação completa
ficam para um ensaio próprio antes de qualquer promoção.
