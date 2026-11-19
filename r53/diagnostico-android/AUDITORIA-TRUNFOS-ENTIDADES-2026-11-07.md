# Revisão da PR85 e auditoria dos trunfos · 07/11/2026

## Revisão da PR85

Revisado o head `735d499` sobre a PR84 `74d83b7`. A PR85 está aberta,
sem conflitos com sua base e com dois checks smoke aprovados no head
conferido. Não foi encontrado bloqueio novo na correção de aquisição.

Foram relidos o gerador dos requisitos, a adaptação dos cartões diretos,
a inclusão das três fórmulas nos moldes e as duas guardas da recuperação.
Passaram novamente os cinco testes focais Python de Liberações e Corrói,
e o teste JS de transporte, reversão e recuperação, usando o snapshot
privado do Código anterior da PR84. A nova geração e os ensaios de
instalação por edição real continuam registrados no relatório da PR85.

As fórmulas GA38:GA40 foram conferidas nas descartáveis. Ambas continuam
com DADOS_R53 oculta e com a correção da PR85 instalada. Esta rodada
acrescenta auditoria e não altera o código da PR85.

## Referência e alcance

Referência mecânica R66,
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, seções
Trunfos das domadas, Técnica Máxima e Melhorias da Técnica Máxima.

Foram conferidas, em cada descartável, as identidades dos 48 trunfos
das 12 entidades, suas 48 fórmulas de nível e suas 48 fórmulas de requisito.
Cada expressão usa a linha da própria entidade e o nível correto da vaga.

O ensaio comportamental usou a primeira e a última entidade, com três
Liberações e uma Máxima em cada uma. O invocador permaneceu no nível 30
enquanto variava o nível fixo da domada. A descrição de QA declarou
técnica própria; no ensaio de Toca a Alma, declarou também Regra de alma.
Essas permissões específicas continuam dependendo da adjudicação da mesa.

## Progressão, dados, custo e tipo

Passaram 74 cenários por descartável, sem divergências.

| Escopo | Casos por cópia | Conferência |
| --- | --- | --- |
| Três Liberações e uma Máxima nas entidades 1 e 12, em seis níveis | 48 | Níveis 9, 10, 19, 20, 29 e 30. As Liberações exigiram 10, 20 e 30; a Máxima exigiu 17. |
| Fronteiras da Máxima nas duas entidades | 10 | Níveis 16, 17, 21, 25 e 26. A tabela usou o nível da domada. |
| Tipos sem trunfo nas duas entidades | 16 | Shikigami de técnica e Corpo amaldiçoado de criação pediram revisão nos quatro cartões. |

As Liberações de Classe 3 conservaram seis pontos, 9d8 e 14 PE.
A Máxima usou 19d8/25 PE, 22d8/30 PE e 26d8/35 PE nas faixas
correspondentes, com orçamentos 8, 12 e 16. O nível 30 do invocador
não promoveu a domada de nível menor para uma faixa superior.

Foram restauradas 135 entradas temporárias por cópia. A comparação de
2.502 posições por cópia, incluindo 1.184 de MONTAGENS, encontrou zero
diferenças e zero erros nos intervalos conferidos.

## Melhorias da Máxima

A matriz local conferiu 60 montagens, em dois modos de entrada e nas
modalidades pessoal e de entidade. As 15 peças seguintes tiveram o
resultado esperado.

| Resultado | Peças |
| --- | --- |
| Pedir revisão | Salto, Queima, Estilhaço, Acúmulo, Remate, Fica, Inescapável, Armado e Segura |
| Permitir neste contexto | Quebra Coisa, Rajada, Mais Um, Precisão, Fura e Toca a Alma |

O ensaio nativo repetiu as 15 peças nas Máximas das entidades 1 e 12,
totalizando mais 30 cenários por descartável. A Família de cada peça
foi aberta em uma posição válida; as nove posições de Família foram
incluídas no snapshot e restauradas ao final.

Passaram os 30 cenários em cada cópia. Foram conferidos preços e saldo,
aprovação das peças permitidas e aviso específico das proibidas. Na
Classe 5, Rajada exibiu cinco tiros, Mais Um exibiu dois destinatários,
Fura ignorou oito de RD e Toca a Alma reduziu 19d8 para 9d8. O custo
da Máxima permaneceu 25 PE.

Foram restauradas 153 entradas temporárias por cópia, incluindo as
18 posições de Família das duas entidades. A comparação de 2.610
posições por cópia, incluindo 1.184 de MONTAGENS, encontrou zero
diferenças e zero erros nos intervalos conferidos.

## Estado de entrega

Foram 104 cenários nativos por cópia nesta rodada e 60 montagens locais
adicionais. Não foi confirmado erro novo nesses escopos. A PR85 continua
pronta para revisão. O pacote integral mantém a margem estreita de
304 bytes já registrada na correção; esta auditoria não mudou seu conteúdo.

O pente-fino geral não está encerrado por esta rodada. Expansão da
domada e seus gastos de espaços têm procedimentos próprios, que não
foram validados por esta matriz de Liberações, Máxima e Melhorias.

Evidências privadas em `nuvem-b47/saidas/auditoria-trunfos-entidades/`,
com snapshots, resultados nativos, conferências de referências e a
matriz local. Esses arquivos permanecem fora do Git.
