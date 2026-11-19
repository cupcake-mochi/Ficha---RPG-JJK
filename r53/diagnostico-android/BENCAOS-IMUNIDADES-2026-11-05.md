# Bênçãos e imunidades — primeira rodada nativa

Base PR64 `ffdee60`, em ramo de diagnóstico separado. Livro R66 de
JJK---Project `e3058ad29180fdec2efec75b512446c49bf87b3d`, seções Estímulo
Muscular, Casco e Corpo Amaldiçoado. Sem correções novas de produção.
Ensaios de recálculo por API nas duas descartáveis Era/Ciclo, não oficiais.
Esses ensaios não acionam onEdit. Eventos reais de equipamento constam no
relatório da PR64, não substituem os eventos destas mecânicas.

## B01 — Casco não entra nos cálculos

Nas duas cópias, configuração Vanguarda, Sem Energia, nível 26,
Constituição 4 e uma escolha de Refino/Lapidação. Lapidação calculada 8,
uma Bênção comprada de uma disponível, Casco em FICHA AMALDIÇOADA!D443.
Não há substituição da vida por CONFIGURAÇÃO: C2 e D2 de DADOS_CONFIG são 0.
A vida base calculada é 261, incluindo o ajuste P26 preexistente de 24.

Com Casco e sem Casco, J26 permanece 261 e AP109 permanece 4. Esperados
274 e 5 com Casco, respectivamente. O texto mostrado da Bênção está
correto, mas as fórmulas de vida máxima e TR de Vigor não consultam a
compra. Vida atual permanece 6 e Integridade máxima 145 nos dois casos,
conforme esperado para essas duas medidas. O gerador não possui uma rota
numérica de Casco identificada nesta revisão.

Antes de implementar, testar também nível 30, requisitos insuficientes,
orçamento excedido, ajustes/substituições e interação com Corpo Quebradiço.
Conferir restauração das fórmulas alteradas por edição real.

## B02 — texto de Estímulo exclui desarmados

FICHA AMALDIÇOADA!L437 informa `+NdX na arma`. A nota do gerador em
`ficha_amaldicoada.py`, chave `apt_canalizar`, reforça “só na arma”.
A R66, seção Estímulo Muscular, inclui arma **ou desarmados** e exclui o
adicional de Katas. O texto pode induzir a negar o bônus de golpe desarmado.
Não foi demonstrada uma rolagem automática incorreta, pois esta rodada
conferiu o adicional mostrado. A correção precisa preservar a exclusão de
Katas e a regra de crítico.

Os cinco degraus numéricos mostrados passaram nas duas cópias:

| Nível | Escolhas de Lapidação | Lapidação calculada | Adicional |
|---|---|---|---|
| 2 | 0 | 1 | 1d4 |
| 10 | 0 | 3 | 2d4 |
| 22 | 0 | 6 | 3d4 |
| 30 | 1 | 9 | 4d4 |
| 30 | 2 | 10 | 4d6 |

## I01 — risco de Exaustão em Corpo Amaldiçoado

A R66 diz que a Origem não adquire estágios de Exaustão e é imune a
Envenenado. Nas duas cópias, Corpo Amaldiçoado e O48=2 resultam em O67
de 4,5 m. Com O48=0, o movimento volta a 9 m. A fórmula de O67 considera
Vigília, mas não contém dispensa pela Origem para esse teto.

Primeiro foi uma escrita por API de um grau permitido pelo menu 0–3.
Depois, na Era, O48=2 foi digitado pela interface. O valor permaneceu,
O49 mostrou desvantagem em perícias/ofícios e o teto de 4,5 m, e O67
permaneceu em 4,5 m na releitura posterior. Não houve rejeição ou diálogo
na edição. Esse ensaio real confirma que o estado incompatível chega
aos cálculos, sem provar que o Google gerou Exaustão automaticamente.
Não foi aplicada uma condição Envenenado, dano ou imunidade de combate.
AK48 permanece livre nas leituras; ausência de texto automático nessa
caixa, isoladamente, não prova que uma condição esteja sendo aplicada.

## Restauração e próximos ensaios

Sete entradas por cópia restauradas e relidas iguais: Caminho, Origem,
nível, Constituição, escolha de Refino/Lapidação, seleção de Casco e
Exaustão. Não foram alteradas as fórmulas de produção nesta rodada.
Evidência privada em `nuvem-b47/saidas/correcao-equipamento/reteste-20261105.json`,
ignorada pelo Git. Ela contém também os snapshots e resultados.

Os textos do catálogo das outras onze Bênçãos foram comparados com as
seções de corpo, perseguição e combate da R66. Não apareceu outra
divergência textual nessa leitura. Isso não testa montagem ou eventos.

Ainda não há cobertura nativa de todas as Bênçãos/imunidades: faltam Ímpeto,
Presilha, Faro, Sem Pegada, Vulto, Esteio, Antecipar, Represália, Sangue Frio,
Campo e Assombro. Algumas descrevem resolução de mesa, não cálculos
automáticos; comparar cada regra com texto, requisitos e efeitos existentes.
Defesa sem Armadura e Vigília têm evidências nas rodadas anteriores.
Não declarar a ficha 100% auditada com esta amostra.

Sem merge, oficiais, jogador, PR31, acionadores ou acesso novo.
Sol/High para os próximos ensaios e implementação, Sol/Medium para revisão.
Não alterar configurações automaticamente.
