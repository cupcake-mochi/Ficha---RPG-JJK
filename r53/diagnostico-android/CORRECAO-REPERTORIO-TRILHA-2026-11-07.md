# Repertório extra das Trilhas · correção e ensaio · 07/11/2026

## Resultado e base

As duas lacunas T01/T02 de `AUDITORIA-REPERTORIO-TRILHA-2026-11-07.md`
foram corrigidas e ensaiadas nas descartáveis Era e Ciclo. Nenhuma montagem
foi apagada para resolver excessos: a ficha mostra consumo/limite e REVISAR.
Três capacidades e três talentos na Principal de nível 24 passam a mostrar
**6/3**, enquanto uma capacidade e dois talentos permanecem dentro de **3/3**.

Ramo `codex/repertorio-trilha-20261107`, baseado na auditoria `81b1745` e na
PR86 `6568838badd1a92b130dd46058527fa089da655f`. A revisão deve comparar com
o ramo `codex/expansao-espacos-analise-20261107`, sem incluir a PR31.
Referência mecânica: livro R66, commit
`e3058ad29180fdec2efec75b512446c49bf87b3d` de `cupcake-mochi/JJK---Project`.

## Comportamento corrigido

- Principal: concede 0/1/2/3 escolhas nos níveis próprios 7/8, 16 e 24;
  exige Caminho Evocador e aquisição da Trilha a partir do nível 2.
- Conjunto: exige Múltiplas Invocações e nível 27 do invocador. O limite é
  metade do atributo **permanente** escolhido, arredondada para baixo.
- Parceria, Caminho diferente ou Trilha desconhecida não concedem extras;
  escolhas preenchidas continuam salvas e recebem aviso para revisão.
- Os três cartões e três talentos compartilham o limite de cada entidade.
  As oito versões de um cartão não multiplicam aquisições. Os extras não
  consomem espaços comuns nem o orçamento da Expansão da domada.
- Talentos isolados também aparecem no consumo e podem acionar REVISAR
  no cabeçalho, mesmo sem qualquer cartão de capacidade preenchido.

O atributo do Conjunto agora tem seleção explícita em `INVOCAÇÕES!D35:F36`,
com rótulo e explicação em `D34:F39`. É independente da seleção da Defesa.
Essência usa `FICHA!AJ21`; Inteligência usa `FICHA!AB21`. Buff/Debuff não
aumenta a concessão. A seleção vazia ou inválida pede revisão quando há
escolhas do Conjunto. O menu não escolhe atributo automaticamente.

`ficha-v01/repertorio_trilha.py` aplica a alteração após o layout final e a
Expansão da domada. A tabela aditiva ocupa `DADOS_INVOC!DA16:DD28`.
São **102 valores/fórmulas**, **14 notas**, três novas mesclas e um menu;
nenhuma aba, linha ou coluna foi inserida. Os 36 avisos GA dos cartões
extras incorporam a validação comum e os 12 cabeçalhos mostram o consumo.
Chaves, tipos e fórmulas da ANALISE não mudam nesta entrega.

## Recuperação e pacote antigo

O caminho leve recupera a tabela, os cabeçalhos e os avisos sem carregar os
catálogos pesados em edições alheias ou na escolha do atributo. Inclui 72
fórmulas vizinhas FY/FZ **inalteradas** para recuperar blocos mistos FY:GA.
Os moldes legados de Prática também recebem as 36 fórmulas GA novas, evitando
que uma recuperação genérica posterior restaure o aviso vazio antigo.

O módulo Android efetivamente instalado não contém DADOS_R53 nem ANALISE.
O ajuste incremental respeita isso: não injeta uma aba parcial no módulo;
a recuperação externa continua responsável pelas fórmulas de DADOS_R53.
Na geração integral, o ajuste também aceita o modelo completo. As
pré-condições verificam a base inteira antes de mutações do retrato.
O escape existente dos literais da ANALISE foi preservado.

Durante os testes, apagar juntas as mesclas do novo seletor recuperou
inicialmente apenas um dos dois rótulos. A recuperação foi ajustada para
recompor ambos quando qualquer um é atingido, preservando a entrada D35.
O ensaio foi repetido com sucesso nas duas cópias. O teste confirma a falha
e sua correção; não estabelece sozinho a causa interna do evento do Google.

A revisão final também detectou que o critério `?*` ignorava nomes de
cartões numéricos ou booleanos. O consumo usa agora `<>`: vazio não ocupa
vaga, e número 7, zero, FALSE e texto "0" ocupam uma cada. Os tipos das
entradas são preservados; não há conversão global de nomes ou coordenadas.

Fontes regeneradas: **d09f5a8d7aa821e6**, 26 abas e 251 contextos.
Pacote integral: cinco partes, 3.858.804 bytes Base64; SHA-256 da fonte
`113f07c232609edc71a866a89031bd7c8c72158f178f6257bab30ed258db2c60`.
**Esse pacote integral não foi instalado.** As QAs receberam somente a
aplicação incremental. Código salvo e relido integralmente nas duas:
`26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c`.

## Validação nativa e preservação

Foram aceitos **234 casos no Google Sheets**, 117 por cópia:

- 38 configurações nas entidades 1 e 12: 76 casos por cópia, incluindo
  fronteiras 7/8, 15/16, 23/24, 26/27; atributos 0–6 e ímpares; buff;
  mistura de talentos/capacidades; atributo independente da Defesa;
  Classe 0, slot 3 isolado e oito versões de uma identidade.
- Três configurações nas 12 entidades: 36 casos por cópia, cobrindo talento
  antes/depois do nível 8 e talento mais capacidade excedendo o limite.
  Os avisos dos 36 cartões foram comparados ao aviso da entidade.
- Cinco casos de tipo do nome por cópia após o ajuste final do critério.
  Essa alteração focal foi seguida desses dez casos e recuperação real;
  os 224 casos anteriores não foram repetidos integralmente sem motivo.

A escrita da matriz pela API nativa não dispara onEdit. Separadamente,
**16 ações por edição real** foram aceitas, oito por cópia: apagar a tabela
de 52 células; apagar dois blocos de nove fórmulas FY:GA nas entidades 1/12;
apagar o primeiro cabeçalho mesclado; apagar a área dos dois rótulos;
selecionar Inteligência e depois Essência; apagar as 12 contagens já com
o critério final. A recuperação funcionou e a seleção alterou 2/1 com
aviso para 2/3 sem aviso, mantendo a Defesa em Inteligência.
Tentativas que falharam antes do ajuste não entram nas 16 ações aprovadas.

As entradas temporárias foram repostas. A comparação final, refeita após
o reinício do PC e a última alteração, cobriu **13.644 posições por cópia**,
incluindo **11.988 posições de MONTAGENS**, com as oito versões dos 36
contextos extras. Houve **118 células com alterações previstas**, zero
diferenças inesperadas, zero alvos divergentes e zero erros de fórmula nos
intervalos lidos. Valores digitados/calculados, tipos, notas, validações e
formatação foram comparados, permitindo apenas o delta declarado.
As 118 posições incluem sobreposições entre valores, notas e formatação.
Isso é uma comparação delimitada, não varredura de todas as células.

Os 96 registros amostrados da ANALISE ficaram inalterados: 84 origens
diretas e 12 multicélula anteriormente conferidas. As três mesclas novas
foram relidas; DADOS_INVOC, DADOS_R53, ANALISE e MONTAGENS voltaram a ficar
ocultas. O seletor foi conferido visualmente nas duas cópias com as entradas
de teste removidas. Menus existentes não mudaram; seus comandos não foram
todos repetidos nesta rodada.

## Verificações locais

- `nuvem-b47/conferir.py --smoke`: **120 verificações aprovadas**, zero falhas,
  na geração final. É conferência local, separada da execução nativa acima.
- `r53/testes/repertorio_trilha.js`: pré-condições, reversão de valores,
  notas, UI, guardas leves, mesclas, moldes antigos e módulo Android real.
- `r53/testes/repertorio_trilha_modelo.js`: **280.056 posições, 26 abas**;
  equivalência incremental/integral, somente o delta previsto, aplicação
  idempotente e recusa de bases divergentes.
- Transporte íntegro, cinco partes, 11 arquivos GS e 15 entradas públicas;
  sintaxe e recuperação de recursos/origens verificadas pelo smoke.

Evidência sanitizada: `repertorio_trilha_validacao_2026-11-07.json`.
Snapshots, código instalado, leituras brutas e capturas ficam apenas na pasta
ignorada `nuvem-b47/saidas/correcao-repertorio/`; não foram versionados.

## Atualização futura de fichas existentes

Nada foi aplicado às oficiais ou à ficha do jogador. A PR31 permanece
intocada no SHA `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`. Sem merge,
acionadores novos, ampliação de acesso ou construir()/continuar().

Para futura instalação, primeiro colher backup e snapshot frescos do código,
dos 102 alvos, das 14 notas e da área D34:F39, incluindo formatos, validações
e mesclas. O preparador `preparar_repertorio_trilha.js` exige Código PR86
com SHA `5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef`,
locale conhecido e valores anteriores exatos. A área do seletor deve estar
vazia e livre de notas/validações; conferir mesclas antes de aplicar.

Preparar código, células, notas e UI antes de qualquer aplicação. Aplicar
somente em cópia nova do destino e repetir recuperação por edição real,
seleção e preservação. A reversão de valores fornecida pelo preparador não
desfaz notas, formatos e mesclas: recuperação completa exige os respectivos
snapshots e o código anterior. Se a base diferir, integrar e ensaiar a
diferença; não substituir código mais recente ou da PR31 pela versão QA.

A definição da entidade, requisitos específicos dos talentos e a condição
de exatamente uma invocação ativa da Principal continuam dependendo de
conferência da mesa. Entidades registradas não são contadas como ativas.
Tipos/Trilhas custom desconhecidos pedem revisão; não recebem aprovação
universal. Esta entrega não afirma que todas as mecânicas da ficha foram
auditadas nem mede desempenho Android ou tempo dos comandos.

Modelo/esforço recomendado: **Sol/Medium** para revisão; **Sol/High** para
integração futura e ensaio de uma base diferente. Configurações preservadas.
