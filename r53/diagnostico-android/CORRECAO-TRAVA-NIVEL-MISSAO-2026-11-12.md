# Um nível por missão · 12/11/2026

Achado 1 da `AUDITORIA-PROGRESSAO-XP-2026-11-12.md`. O livro R66 diz: "Você avança no máximo um nível por missão
concluída". Na ficha, uma missão com o adicional da guilda podia subir dois níveis. O Mizuki pediu a trava ("Põe trava
se for possível").

## Por que não basta "mais um nível por vez"

A subida de nível roda a cada caixa editada no painel de missões da FICHA PESSOAL. Na ordem natural de preencher, o
jogador digita o nome, o tipo e depois o adicional. Cada edição sobe o nível de novo. Por isso, uma trava de "um nível
por edição" ainda deixaria um Final de arco 2x subir dois níveis: um pelo tipo e outro pelo adicional.

## A regra que entrou

- **Nome ou tipo:** a edição que mexe no nome ou no tipo de uma missão conta como missão concluída e sobe no máximo um
  nível.
- **Adicional ou desconto:** a edição que mexe só nessas colunas não sobe o nível. O XP a mais fica guardado e conta na
  próxima missão, como manda o livro.
- **Várias linhas de uma vez:** colando linhas, cada linha que fica com tipo conta como uma missão.
- **Limiar do nível 20 e acertos à mão:** nada muda.
  - Sem o feito, o XP continua parando no 20.
  - Digitar o XP ou o nível na FICHA continua livre. É assim que o jogador registra o feito e sobe vários níveis de uma
    vez.

**Limite.** Mexer de novo no nome ou no tipo de uma missão já anotada conta como outra conclusão. Se houver XP guardado
para isso, o nível sobe mais um. Resolver isso pediria uma marca por missão nas notas, que o código do salário reescreve
a cada edição.

## Onde mudou

| arquivo | o quê |
|---|---|
| `apps-script/Salarios.gs` | `salarioNivelQueSobe_` ganha o teto; o novo `salarioMissoesDaEdicao_` conta as missões da edição; o `salarioMissaoDireta_` passa o nível atual mais essa conta. É o caminho que as fichas usam. |
| `apps-script/Codigo.gs` | `nivelQueSobe_` ganha o mesmo teto. O `nivelPelaMissao_` passa a trava simples de um nível por edição: esse caminho só roda numa ficha sem o código do salário. A ajuda da caixa do nível agora diz "no máximo um nível por missão". |
| `r53/diagnostico-android/preparar_trava_nivel_missao.js` e `trava_nivel_missao_salario.json` | o preparador da cadeia que reproduz o Salarios.gs (depois do `preparar_xp_atualizar.js`) e o trecho para o console do editor |
| `r53/testes/missoes_integradas.js` | os casos novos (abaixo); o caso antigo, que esperava o nível 6 numa missão só, agora espera o 2 |
| `r53/testes/trava_nivel_missao.js` (novo, no smoke) | o preparador e o trecho: ida e volta, recusa de repetir e de código divergente, e um editor de mentira |
| `missoes_enxutas.js`, `missoes_sem_registros.js`, `salario_lote.js` | a cadeia de preparadores ganhou o novo no fim |

Casos no `missoes_integradas.js`:
- uma missão sobe um nível, mesmo com XP para o 6;
- a missão seguinte sobe mais um;
- só o adicional e o desconto não sobem;
- colando três linhas com tipo e uma vazia, sobem três níveis;
- a trava do feito continua: no 20 não passa sozinho, e acima dele sobe um por missão.

No `missoes_sem_registros.js`, as 400 edições sorteadas continuam saindo iguais às do Salarios.gs de 57117fb.

**Smoke completo:** saída 0, nenhuma falha.

## Instalação nas duas QAs

Nas QAs, o código do salário mora dentro do Codigo instalado: é o arquivo que tem o `salarioMissaoDireta_` e o
`SALARIO_`. O trecho do preparador troca os dois pedaços, cada um exatamente uma vez, e guarda o antes em
`window.__travaNivelAntes`. Antes de gravar, um ensaio a seco na Era confirmou os dois pedaços.

O `nivelPelaMissao_` e a ajuda do nível moram no módulo compactado e não foram trocados nas QAs. Com o salário
instalado, esse caminho não roda. Os dois entram na próxima montagem.

| QA | Codigo instalado | depois de recarregar o editor |
|---|---|---|
| Era (`1LBZOf9v…`) | `0292582a1fff` → `b5861c145394` | hash confere, `salarioMissoesDaEdicao_` presente |
| Ciclo (`1HQqGOVG…`) | `0292582a1fff` → `b5861c145394` | hash confere, `salarioMissoesDaEdicao_` presente |

## Ensaio no Sheets (entradas repostas)

**Era.** Partiu do nível 10, com a base do XP posta em 4700 pela API (1000 guardados).

| edição | XP | nível | sem a trava |
|---|---|---|---|
| missão A, Final de arco | 5000 | 11 | 11 |
| adicional 2x na missão A | 5300 | **11** | 12 |
| missão B, Curta | 5350 | 12 | 12 |

**Ciclo.** Partiu do nível 2, sem XP. É o exemplo do livro, com o adicional digitado antes do tipo.

| edição | XP | nível | sem a trava |
|---|---|---|---|
| adicional 2x, nome e Final de arco (600) | 600 | **3** | 4 |

Na primeira edição depois de salvar o código, o nível ainda não tinha aparecido 18 s depois; apareceu na leitura seguinte, perto de 30 s. A planilha só mostra a
mudança quando o onEdit termina.

**Reposição.** Tudo pela API, que não dispara o onEdit:
- painel e notas das missões de ensaio limpos (as notas de antes estavam vazias);
- as linhas novas do `DADOS_SALARIOS` apagadas (na Era ficou a linha antiga, inativa);
- a base do XP e o nível voltaram: Era com 3700 e nível 10, Ciclo com 0 e nível 2.

## Fora deste conserto

- **Oficiais:** nada foi aplicado. Fica para o Mizuki. O mesmo trecho serve, e ele recusa se o código instalado não
  tiver os dois pedaços antigos.
- **Desconto do 8º em diante:** achado 2 da auditoria, explicado ao Mizuki, sem decisão ainda.
