# Expansão da domada e gastos de espaços · 07/11/2026

Auditoria sobre `109dff6`, com a implementação da PR85 `735d499` nas
descartáveis Era e Ciclo. Referência R66 do livro,
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, seções
Expansão da domada, Degraus da Expansão e Acerto do domínio.

Foram executados 210 cenários em cada cópia. As contas de PE e Acerto
tiveram os valores esperados. Foram confirmadas duas lacunas de
validação, além de uma classificação de metadados a revisar.

## D01 · Requisitos informativos sem validação automática

A Expansão usa o cálculo legado de INVOCAÇÕES. O campo `pede` consulta
o texto da tabela de requisitos, sem avaliar tipo, nível da domada,
refino do invocador ou especialização em Ocultismo.

Em cada cópia foram ensaiadas 24 combinações, na primeira e na última
entidade. Seis atendiam aos requisitos numéricos/tipo e 18 não atendiam.
O texto exibido permaneceu o da tabela em ambos os grupos.

| Caso | Exigência não atendida | Exibição observada |
| --- | --- | --- |
| Domada 10, Incompleta, refino 3 | Refino mínimo 4 | `Nível 10 dela e seu refino 4.` |
| Domada 13, Completa, refino 10 | Nível mínimo 14 | `Incompleta, nível 14 dela e seu refino 5.` |
| Domada 14, Sem Barreiras, refino 8 | Refino mínimo 10 | `Completa, seu refino 10 e sua especialização em Ocultismo.` |
| Domada 14, Sem Barreiras, refino 10, sem especialização | Especialização em Ocultismo | O mesmo texto informativo |
| Shikigami de técnica ou Corpo amaldiçoado de criação | Tipo que não recebe esse trunfo | O texto do degrau selecionado |

O domínio não tem o estado VÁLIDO/REVISAR dos cartões R53. O achado é
ausência de validação automática; não é um falso retorno de VÁLIDO do
domínio. Há instruções escritas que continuam exigindo conferência da mesa.

## D02 · Gasto do domínio sem conferência conjunta das especiais

O total básico de espaços da entidade está correto. O campo `esp`
calcula `INT((2 + nível / 2) / 2)`, e o cabeçalho de habilidades mostra
essa capacidade total. Ele não se apresenta como saldo restante.

O consumo acumulado de domínio é 2 para Incompleta, 3 para Completa
e 5 para Sem Barreiras. Esses custos constam na tabela de aquisição,
mas não são somados às especiais conhecidas para conferir ocupação
total ou emitir um aviso conjunto.

Foram nove cenários por entidade, na primeira e na última, totalizando
18 por cópia. A conta abaixo é o orçamento independente pelo livro.

| Nível | Domínio | Especiais | Ocupação / capacidade | Resultado observado |
| --- | --- | --- | --- | --- |
| 14 | Nenhum | 2 | 2 / 4 | Controle dentro do limite |
| 14 | Incompleta | 2 | 4 / 4 | Controle no limite |
| 14 | Completa | 1 | 4 / 4 | Controle no limite |
| 14 | Completa | 2 | 5 / 4 | Duas especiais válidas individualmente; sem alerta conjunto |
| 14 | Sem Barreiras | 0 | 5 / 4 | Sem alerta de que o domínio sozinho excede a capacidade |
| 17 | Sem Barreiras | 0 | 5 / 5 | Controle no limite |
| 30 | Sem Barreiras | 3 | 8 / 8 | Controle no limite |
| 30 | Sem Barreiras | 4 | 9 / 8 | Quatro especiais válidas individualmente; sem alerta conjunto |
| 30 | Completa | 4 | 7 / 8 | Controle dentro do limite |

Os seis casos de estouro por cópia não receberam uma conferência
global. A validade individual das especiais avaliou suas montagens,
sem descontar o domínio do repertório. A Trilha usada nesta matriz
era a seleção vazia do modelo, sem ganhos adicionais de escolha.

As lacunas D01 e D02 pertencem ao fluxo legado. O próprio cabeçalho
do gerador já declara a limitação de não conferir aquisição de
trunfos e gasto de espaços de domínio. Esta rodada reproduz sua
consequência nativa; não identifica regressão introduzida pela PR85.

## M01 · Classificação dos Acertos na ANALISE

As 12 chaves `invocacao.N.exp.acerto` têm fórmula de leitura de uma
célula calculada, mas a coluna D as classifica como `entrada`.
Nos mesmos grupos, PE e requisito são classificados como `resultado`.
O padrão foi confirmado nas duas cópias e na fonte do gerador.

Exemplo da primeira entidade, linha 2948 da ANALISE:

- A contém `invocacao.1.exp.acerto`.
- B lê INVOCAÇÕES!Q226, que aponta para DADOS_INVOC!JI2.
- C informa a origem correta, `'INVOCAÇÕES'!Q226`.
- D contém `entrada`.

O seletor de tipo em `ficha-v01/analise.py` inclui `pe`, `dados`,
`acao` e `pede` entre os resultados, e deixa `acerto` no ramo de
entrada. A classificação precisa ser padronizada com o papel do
campo calculado. O valor e o endereço de origem estavam corretos.
Não foi demonstrado impacto em consumidores externos nem erro de
dano causado por esse metadado. Nenhum tipo foi alterado nesta auditoria.

## Contas conferidas nas 12 posições

Foram 168 controles aritméticos por cópia. As sete Classes foram
ensaiadas com Mira Normal e Livre. As posições distribuíram os três
degraus, quatro entidades por degrau, nas duas modalidades de Família.
O invocador ficou no nível 30 enquanto variava o nível fixo das domadas.
Os níveis menores foram usados para conferir aritmética, sem tratá-los
como aquisição válida de domínio.

| Classe | Pontos da especial | Acerto normal | Acerto com Mira Livre | PE (6× / 7× Classe) |
| --- | --- | --- | --- | --- |
| 1 | 2 | 1d8 | 1d8 | 6 / 7 |
| 2 | 4 | 2d8 | 3d8 | 12 / 14 |
| 3 | 6 | 3d8 | 4d8 | 18 / 21 |
| 4 | 9 | 5d8 | 7d8 | 24 / 28 |
| 5 | 11 | 6d8 | 8d8 | 30 / 35 |
| 6 | 13 | 7d8 | 10d8 | 36 / 42 |
| 7 | 16 | 9d8 | 12d8 | 42 / 49 |

Os valores corresponderam ao livro em todos os controles. A ficha
usou a Classe da domada e o desconto de Família dela.
O controle de 6× usou os seletores Incompleta e Completa; o de 7× usou
Sem Barreiras. A matriz não certifica uma seleção independente de modo
fechado para quem mantém Sem Barreiras registrado como grau adquirido.

## Cuidados para uma futura correção

O campo atual de degrau também seleciona a exibição de PE. A R66
permite a quem adquiriu Sem Barreiras abrir no modo fechado por
6 × Classe ou aberto por 7 × Classe. Ao automatizar gastos permanentes,
é necessário distinguir aquisição e modo de abertura: usar o custo de
Completa não pode reduzir de cinco para três os espaços já adquiridos.
Esta separação é um ponto de projeto, sem alegar que a ficha analisa
o texto livre para descobrir o modo de abertura.

O custo acumulado 2/3/5 já inclui os degraus anteriores. Ampliações de
uma mesma especial não podem virar novas vagas conhecidas; Liberação
e Máxima conservam suas aquisições próprias. Os ganhos das Trilhas
precisam de controles separados antes de implementar um saldo global.

Principais fontes para revisão: `ficha-v01/ficha_invocacoes.py`
(`esp`, `d_hab`, `d_ep`, `d_ea`, `d_er`),
`ficha-v01/familias_invocacao.py` (Famílias Livres do Acerto) e
`ficha-v01/analise.py` (classificação da exportação histórica).

## Preservação e evidências

Os ensaios usaram somente as duas descartáveis identificadas. Foram
restauradas 332 entradas por cópia, incluindo as 108 posições de
Família das 12 entidades, os controles de refino/especialização e
as oito especiais usadas no ensaio de orçamento.

A comparação de 4.443 posições por cópia, incluindo 2.072 de MONTAGENS,
encontrou zero diferenças e zero erros de fórmula nos intervalos
conferidos. Valores, notas, validações, versões e o trecho da ANALISE
voltaram ao snapshot inicial. As fórmulas e o código instalado não
receberam correções. As edições via API ensaiaram cálculo nativo;
eventos onEdit não integram esta matriz.

Snapshots, plano, resultados dos 210 cenários por cópia e metadados
das 12 exportações estão em `nuvem-b47/saidas/auditoria-expansao-domada/`,
fora do Git. O relatório sanitizado registra os achados para revisão.
