# Prática Cotidiana · 05/11/2026

P03 da auditoria de passivas, sobre a PR69 em `6928962`. Regra conferida no
livro R66, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

Prática Cotidiana acrescenta dois feitiços de Classe 0 em qualquer vaga de
menor da Restrição corporal, inclusive por herança custom válida. A mesma
passiva nas duas vagas continua valendo dois. As Formas, melhoria leve,
restrição leve, dano e alcance seguem os cartões de Classe 0 existentes.
O bloco de duas vagas fica no fim da FICHA AMALDIÇOADA, com indicação
junto ao bloco antigo. Retirar a passiva conserva os feitiços cadastrados
e indica que as vagas exigem revisão.

## Escopo da mudança

- `ficha-v01/pratica_cotidiana.py` acrescenta `classe0.6` e `classe0.7` em
  `D566:T567`. As linhas `D328:T328` e `P58` orientam onde encontrar as
  vagas. A Liberação continua na linha 329.
- Três auxiliares em `DADOS_CUSTOM!B134:B136` validam a herança, contam
  os sete espaços possíveis e mostram o excesso. O teto passa por
  `DADOS_AM!HM10`. Talentos e invocações usam suas regras anteriores.
- Os 249 contextos anteriores mantêm IDs, endereços e fórmulas. Os novos
  usam `DADOS_R53!252:253` e MONTAGENS nas linhas 9467 e 9505. A linha
  251 continua reservada a `r53.editor.gid`. ANALISE12/esquema2 recebe
  91 chaves no fim, das linhas 18410 a 18500.
- A recuperação consulta os dados das duas vagas somente quando uma
  edição toca seus alvos. Colagens com entradas e fórmulas recuperam
  as fórmulas e deixam o editor gravar a montagem. A restauração de
  literais usa escape para preservar apóstrofos e manter `0` como texto.
- O mapa de aparência incorpora as áreas novas e a indicação. O ensaio
  visual mostrou o cabeçalho `USAR` no bloco novo. O cabeçalho antigo
  `P322:Q322` ainda o encobre e fica registrado para revisão separada.

## Validação

- 214.408 verificações de paridade e transporte, incluindo os 249
  contextos anteriores. Os 94 checks do smoke local passaram, com
  pacote integral, recuperação e preflight. Geração `c09878807ae4a15e`,
  zero SOBRAS.
- Dez cenários por cópia nativa (Era e Ciclo). Níveis 2, 10 e 30 dão 4,
  5 e 7 vagas com a passiva. Ambas as vagas, escolha repetida, retirada,
  excesso, origem incompatível e custom válida/inválida conferidos.
  No nível 30, os cartões de Projétil deram `6d8`, iguais ao controle.
- Por edição real, recuperaram-se 17 células por cópia, incluindo
  fórmulas, registros e literais. Uma colagem recuperou quatro fórmulas
  e salvou os dois cartões. A mudança de Projétil para Toque persistiu
  em MONTAGENS e alterou o alcance de 9 m para 1,5 m nas duas cópias.
- Uma versão intermediária restaurou `0` como número. Repetição com o
  código final confirmou texto nas duas cópias. Uma navegação do ensaio
  na Era também atingiu seis células fora do alvo em DADOS_R53. Elas
  foram restauradas e comparadas com o modelo anterior. O teste correto
  foi repetido na seleção confirmada.
- Vinte entradas de ensaio restauradas por cópia, incluindo as montagens.
  Os eventos de limpeza da memória das versões concluíram nas duas.
  As abas auxiliares voltaram à visibilidade anterior. A releitura de
  1.750 células por cópia conferiu os 922 alvos de valor, 11 notas, oito
  validações novas e 230 campos históricos. Zero divergências e zero
  erros de fórmula nos intervalos relidos.

## Preparação incremental

Em cópia descartável, obter snapshot atual de valores, notas e grade,
dos exemplares de formato, das cinco partes de `R53_LOTE` e dos dois
arquivos do Apps Script. Incluir em `blankCells` as 26 células nativas
de `D328:T328` e `MONTAGENS!A9467:I9467`. O preflight recusa área ocupada,
grade divergente, falta de dados ou ID de aba diferente do snapshot.

`preparar_pratica_cotidiana.js` gera as requisições via
`planejarInstalacao(snapshot, metadata)`. `prepararCodigo` e
`prepararEditor` exigem os hashes exatos da PR69 instalados. Aplicar em
uma cópia, salvar e reabrir o código e conferir cálculo, colagem,
tipos e recuperação. Para eventual aplicação futura, guardar a cópia
nativa anterior e os dois arquivos originais para reversão.

Na instalação incremental, o catálogo pesado original conserva 249
contextos. O editor atualizado usa 251 e o verificador distingue os
dois números. O pacote integral gerado é uma entrega separada. Esta
validação foi feita apenas nas duas descartáveis, sem executar
`construir()` ou `continuar()`. Não houve aplicação nas oficiais,
na ficha do jogador ou alteração na PR31.

Código incremental salvo e relido
`279856ca058ca7eb6f774879102552c174b6b00f85b1fccc09667d9cbf8107ec`.
Editor relido
`98413975988095b99da8f260c7295b09d00f7f40ae85b4f14ec86f9e88ed6844`.
Evidências privadas em `nuvem-b47/saidas/correcao-pratica-cotidiana/`.
