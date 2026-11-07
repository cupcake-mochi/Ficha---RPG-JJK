# Auditoria da progressão das Liberações Máximas · 07/11/2026

Depois da instalação da PR84 `74d83b7`, o pente-fino confirmou um
erro de aprovação nos três cartões pessoais de Liberação Máxima.
As posições ainda não recebidas pela progressão aparecem como VÁLIDO.
O achado foi reproduzido nas duas descartáveis e fica separado da
correção de Corrói. Este registro contém auditoria, sem correção mecânica.

## Regra e reprodução

A R66 do livro, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
estabelece a primeira Liberação no nível 10, a segunda no 20 e a terceira
no 30. Foram conferidas as seções de progressão e de Liberação Máxima
na revisão local do livro. A aquisição da posição é distinta do requisito
de Classe mínima 3.

Foi preparada uma montagem de Classe 3 em cada posição, com Projétil,
nove pontos de dano, sem Melhorias nem Restrições. Foram alternados os
níveis 9, 10, 19, 20, 29 e 30. Os campos G332, M332 e S332 da
FICHA AMALDIÇOADA mostraram VÁLIDO, sem aviso, em todos os cenários.
Cada montagem retornou 12d8 e custo de 14 PE.

| Nível | Posições recebidas | Posições aprovadas | Aprovações indevidas |
| --- | --- | --- | --- |
| 9 | Nenhuma | 1, 2 e 3 | 1, 2 e 3 |
| 10 | 1 | 1, 2 e 3 | 2 e 3 |
| 19 | 1 | 1, 2 e 3 | 2 e 3 |
| 20 | 1 e 2 | 1, 2 e 3 | 3 |
| 29 | 1 e 2 | 1, 2 e 3 | 3 |
| 30 | 1, 2 e 3 | 1, 2 e 3 | Nenhuma |

São nove combinações com aprovação indevida e nove controles de
aprovação legítima por cópia. Trata-se de um defeito de progressão
reproduzido em várias fronteiras, não de nove defeitos independentes.
As classes máximas exibidas foram 3 nos níveis 9 e 10, 5 nos níveis
19 e 20 e 7 nos níveis 29 e 30. A classe escolhida era permitida.

## Alcance da apuração

No modelo, o requisito específico da Liberação exige Classe mínima 3,
mas não incorpora o nível de aquisição de cada posição. O requisito de
nível da Técnica Máxima demonstra que já há tratamento de progressão
para outro contexto. As fórmulas de preparação e a configuração do
editor examinadas também não forneceram essa validação por posição.

O avaliador local reproduziu o resultado nos modos estruturado e direto.
Foram 36 cenários, com 18 divergências esperadas e 18 controles válidos.
O ensaio nativo executou 18 cenários na Era e 18 no Ciclo, com o mesmo
resultado nas duas cópias e zero erros de fórmula nos intervalos lidos.

O achado demonstra aprovação local incorreta dos três cartões pessoais.
Não mede uso em combate nem confirma uma falha adicional no limite
global de repertório. A progressão das Liberações das entidades ainda
requer apuração própria antes de ampliar o alcance de uma correção.

## Restauração e evidência

Foram repostas as 52 entradas temporárias por cópia. A releitura de
1.118 posições por cópia, incluindo 777 de MONTAGENS, encontrou zero
diferenças em relação ao snapshot anterior a este ensaio e zero erros
nos intervalos conferidos. O nível anterior e as três montagens foram
restaurados. DADOS_R53 voltou a ficar oculta.

A conferência final mais ampla da instalação da PR84 também cobriu
5.218 posições por cópia, incluindo 3.647 de MONTAGENS, sem diferenças
nem erros. As duas descartáveis ficaram com a PR84 instalada.

Evidência privada em `nuvem-b47/saidas/instalacao-corroi/`, nos arquivos
`liberacoes-local.json`, `contextos-liberacao.json`,
`liberacoes-0-antes.json`, `liberacoes-0-resultado.json`,
`liberacoes-1-antes.json` e `liberacoes-1-resultado.json`.
Snapshots e dados de teste permanecem fora do versionamento.
