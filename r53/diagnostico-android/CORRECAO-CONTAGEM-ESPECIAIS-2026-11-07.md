# Contagem de especiais com nomes numéricos · 07/11/2026

## Resultado

Corrigido N01 de `AUDITORIA-REPERTORIO-NORMAL-2026-11-07.md`.
Nomes numéricos, zero, booleanos e fórmulas que devolvem número passam a
ocupar uma vaga por cartão normal. Nomes vazios, inclusive o resultado de
`=""`, não ocupam vaga. Nenhum nome foi convertido, nenhuma compra apagada
e nenhuma montagem foi regravada para resolver o excesso.

Na entidade de nível próprio 14, duas especiais chamadas 7/8 e domínio
Completo agora mostram **2+3 de 4**, com aviso de **5/4**. Uma especial mais
o mesmo domínio fica em **4/4**, sem falso alerta. Sem domínio, as especiais
continuam sendo contadas. O gasto de domínio permanece 2/3/5 no total.

Ramo `codex/contagem-especiais-20261107`, sobre a auditoria `95820b8` e a
PR87 `0554071051697790d9c807f2478f6c5816018aa1`. Revisar contra
`codex/repertorio-trilha-20261107`. Referência mecânica R66,
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

## Alteração e recuperação

`ficha-v01/expansao_domada.py` gera a contagem com `SUMPRODUCT`, a identidade
normal da própria entidade e o comprimento do nome convertido em texto
somente dentro do cálculo. Isso preserva o tipo digitado e distingue
ausência de nome de zero/FALSE. O padrão de identidade exclui básicas,
extras da Trilha, Liberações e Máxima; as versões não são somadas como
aquisições adicionais. Não houve substituição global de critérios.

São **24 fórmulas**: `DADOS_INVOC!IE2:IE13` e `JJ2:JJ13`.
Os requisitos de tipo, nível, refino, especialização e espaços permanecem.
Nenhuma nota, validação, entrada, mescla, dimensão ou chave da ANALISE mudou.

A recuperação existente da Expansão recebe os mesmos moldes corrigidos.
Foram acrescentadas **12 fórmulas IF2:IF13 inalteradas** ao seu suporte;
o suporte total passa de 48 para 60 moldes. Assim, apagar IE:IF nas duas
primeiras ou últimas linhas testadas recupera todo o bloco pelo caminho
leve. Não precisa carregar o editor integral apenas para a fórmula vizinha.
O escape de literais da ANALISE e os 48 moldes anteriores foram preservados.

O código incremental troca somente o runtime da Expansão na base PR87.
Todo o restante do código, inclusive recuperação de Prática, paleta,
salários, recursos e seletor do Conjunto, permanece igual. O ajuste do
retrato do pacote Android antigo também recebe as fórmulas corrigidas.
Foi conferido com as cinco partes efetivamente usadas nas QAs, que omitem
DADOS_R53 e ANALISE do módulo. Não foi injetada uma aba parcial.

## Falhas encontradas durante o ensaio

1. A primeira proposta com `COUNTIFS(...,"<>")` resolveu números, mas ainda
   contou um nome com fórmula `=""`. O caso nativo reprovou a proposta e as
   entradas foram restauradas. A fórmula por comprimento passou pelos dez
   tipos de entrada do protótipo e depois pela matriz completa.
2. O primeiro apagamento misto IE2:IF3, sem os moldes vizinhos, atingiu o
   limite de 30 segundos no editor legado e deixou quatro células vazias.
   A leitura do conector também expirou; o histórico do Apps Script
   confirmou o timeout do evento. As quatro fórmulas foram repostas
   manualmente na QA, com o snapshot, antes da nova tentativa. Os 12 moldes
   vizinhos foram incluídos e os testes reais foram repetidos com sucesso.

Essas tentativas intermediárias não entram nos oito eventos aprovados.
O histórico nativo das oito execuções finais mostra **Concluído**.
Não se está inferindo RAM, latência Android ou desempenho geral desses
registros de execução.

## Validação nativa e preservação

Foram **12 configurações × 12 entidades × duas cópias = 288 casos**:
texto comum, números, zero, booleanos, números como texto, fórmulas
numéricas, mistura texto/número, fórmula vazia/célula vazia, fórmulas
textuais, equações literais, uma escolha no limite e duas sem domínio.
Conferidos contagem, custo do domínio, capacidade, aviso no cabeçalho e
aviso de espaços no requisito. Todos tiveram os resultados esperados.

O invocador ficou no nível 30 e as entidades no nível próprio 14, como
Maldições domadas; domínio Completo, exceto o controle sem domínio.
A matriz não troca Classe, compras ou versões dos cartões. A escrita pela
API nativa do Sheets não dispara onEdit.

Separadamente, foram aceitas **oito edições reais**, quatro por cópia:

| Faixa apagada | Células recuperadas por cópia | Conferência |
| --- | --- | --- |
| IE2:IE13 | 12 | Contagem corrigida das 12 entidades |
| JH2:JJ13 | 36 | Requisitos, PE e Acerto preservados |
| IE2:IF3 | 4 | Contagens e vizinhas das posições iniciais |
| IE12:IF13 | 4 | Contagens e vizinhas das posições finais |

As fórmulas retornaram com seus valores e tipos esperados. Durante esses
ensaios, os nomes foram números 7/8 e o aviso continuou sendo 5/4. As oito
edições foram feitas na versão final do código. A matriz de 288 casos foi
feita antes da inclusão dos moldes IF: essa última alteração só acrescenta
recuperação de fórmulas inalteradas, sem mudar as 24 fórmulas testadas.

Foram restauradas **158 entradas por cópia**. Snapshot/releitura cobriram
**33.494 posições por cópia**, incluindo **31.968 de MONTAGENS** dos 96
cartões normais, com vazios implícitos nas caudas omitidas pela API.
Somente as 24 fórmulas previstas diferem; zero diferenças inesperadas,
zero alvos divergentes e zero erros de fórmula nos intervalos lidos.
Comparados valores digitados/calculados, tipos, notas e validações.
Formatação não foi escrita nem incluída nessa comparação delimitada.

DADOS_INVOC, DADOS_R53, ANALISE e MONTAGENS terminaram ocultas. O estado
restaurado e os cabeçalhos foram conferidos visualmente nas duas QAs.
Os metadados de arquivo e abas retornados pelo conector ficaram idênticos
ao snapshot inicial nas duas cópias.
Isso não constitui uma varredura integral de todas as células da ficha.

## Artefatos e testes locais

Geração final **c59bcb593daf38af**, concluída com código de saída zero.
Comparação do modelo: **280.056 posições, 26 abas, somente 24 fórmulas**;
metadados preservados e os 12 moldes IF conferidos como inalterados.
Os testes focais passaram para pt_BR/en_US: snapshots estritos, reversão,
recusa de base divergente, recuperação direta/mista, preservação dos
moldes anteriores e carregamento do módulo Android real.

Smoke: **121 verificações aprovadas**, zero falhas. Os dois testes focais
foram repetidos após reforçar as asserções de preservação dos moldes IF.
Pacote integral: cinco partes, 3.858.752 bytes Base64; SHA-256 da fonte
`d8bc545601483e53a97d11871703ddca62ea1f586ba5ab0b5a17fcfab4c92bfc`.
O pacote integral foi regenerado, **não instalado**.

Código incremental final salvo e relido integralmente nas duas QAs:
`8935211c6e87cd4515b0df860bd0d71524f316d08e42013f86cc9fa6b1d53bea`.
Evidência sanitizada: `contagem_especiais_validacao_2026-11-07.json`.
Snapshots, código instalado, leituras e capturas ficam somente em
`nuvem-b47/saidas/correcao-contagem/`, ignorado pelo Git.

## Aplicação futura e limites

Nada aplicado às oficiais ou ao jogador. PR31 preservada no SHA
`765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`. Sem merge, acionadores novos,
ampliação de acesso, construir()/continuar() ou importação Office.

`preparar_contagem_especiais.js` exige o Código PR87 exato, SHA-256
`26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c`,
e snapshot fresco das 24 fórmulas. Produz código e pedidos sem acessar o
Google. Verificar código/células do destino, guardar backup completo e
ensaiar uma cópia nova antes de futura aplicação autorizada. Reversão das
24 fórmulas exige que ainda sejam a proposta; reverter código exige o
backup anterior. Não colar o código QA sobre uma base diferente ou PR31.

Os quatro formatos de faixa listados foram ensaiados. Isso não garante
latência ou recuperação de toda colagem arbitrária que atravesse outras
áreas do editor legado. Outros critérios `?*` e a concessão dos extras
não receberam substituição global nesta correção.

Modelo/esforço: **Sol/Medium** para revisão; **Sol/High** para futura
integração/ensaio em base diferente. Configurações preservadas.
