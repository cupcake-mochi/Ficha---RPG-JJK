# Aquisição, nível e débito de invocações · 07/11/2026

## Resultado

**AQ01 [P2] confirmado: entidades obtidas por Criação sobem de nível
indevidamente até o fim da Classe.** Isso aumenta a vida e pode conceder
um espaço de especial antes da hora. É uma divergência entre a regra R44
ainda implementada e a referência R66 atual, não uma regressão da PR88.
Nenhuma correção foi aplicada nesta rodada de diagnóstico.

Foram 120 casos nativos nas duas descartáveis autorizadas, Era e Ciclo:
106 conformes e 14 divergentes, todas variações da mesma causa. O débito
de espaços conhecidos passou nos controles exercitados. Esta amostra
não encerra o pente-fino geral das mecânicas.

## Referência e causa

Livro consultado no repositório `cupcake-mochi/JJK---Project`, commit
`e3058ad29180fdec2efec75b512446c49bf87b3d`:

- [Invocações, Aquisição](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/manual/60-invocacoes.md):
  a entidade criada não sobe de nível junto com o invocador. Espaço de
  feitiço e lista de ritual acompanham o nível; a domada conserva o obtido.
- [Fabricação de entidades](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/planejamento-editorial/invocacoes/fabricacao/lote-01/FABRICACAO-DE-ENTIDADES.md):
  conserva-se o nível de fabricação; uma versão mais poderosa exige novo
  projeto. O exemplo da entidade de nível 9 explicita que ela continua
  no 9 quando a fabricante sobe de nível.

Na ficha, `ficha-v01/invocacao-do-livro.json:611` ainda registra Criação
como aquisição que acompanha o nível até o fim da Classe.
`extrair_invocacao.py:152` documenta expressamente a origem R44 dessa
interpretação. `ficha_invocacoes.py:374` transforma o sinalizador em 2 na
tabela de aquisições; `ficha_invocacoes.py:470` calcula, para esse valor,
o mínimo entre o nível do invocador e o último nível da Classe original.
As notas de aquisição e nível em `ficha_invocacoes.py:852` também ensinam
o crescimento antigo.

As duas QAs confirmam `DADOS_INVOC!BQ5 = 2` e o mesmo resultado da fórmula
em `FO2:FO13`. A PR88 altera as contagens IE/JJ e não introduziu essa
progressão. Sua correção permanece preservada.

## Reprodução e impacto

Invocador no nível 30; nível de obtenção preenchido explicitamente nos
12 cartões com `[1,4,5,8,9,12,13,16,17,20,21,26]`. Nos seis primeiros
casos de Criação foi usado Shikigami de criação; nos demais, Corpo
amaldiçoado de criação. Nenhuma validação foi removida.

| Nível obtido | Nível R66 | Nível nativo, nas duas cópias |
| --- | --- | --- |
| 1 | 1 | 4 |
| 4 | 4 | 4 |
| 5 | 5 | 8 |
| 8 | 8 | 8 |
| 9 | 9 | 12 |
| 12 | 12 | 12 |
| 13 | 13 | 16 |
| 16 | 16 | 16 |
| 17 | 17 | 20 |
| 20 | 20 | 20 |
| 21 | 21 | 25 |
| 26 | 26 | 30 |

São sete divergências por cópia. Os cinco resultados no fim da Classe
são controles coincidentes, não demonstração de que a regra esteja certa.

Exemplos com Constituição 0 e ajuste manual de vida 0:

| Caso | Esperado | Obtido |
| --- | --- | --- |
| Shikigami criado no 1 | nível 1, 1 espaço, 5 PV | nível 4, 2 espaços, 14 PV |
| Corpo criado no 13 | nível 13, 4 espaços, 53 PV | nível 16, 5 espaços, 65 PV |
| Corpo criado no 26 | nível 26, 7 espaços, 105 PV | nível 30, 8 espaços, 121 PV |

Classe máxima e dados da básica também foram comparados. Não divergem
nessa matriz, pois o crescimento indevido permanece dentro da mesma
Classe. Outros efeitos que dependem do nível não foram declarados
aprovados por consequência desses controles.

## Controles executados

Quatro aquisições × 12 entidades × duas cópias = **96 casos**. Além do
nível, foram comparados Classe máxima, dados da básica, capacidade de
especiais e vida máxima. O oráculo usa a regra R66 e a Constituição e
o ajuste manual lidos de cada entidade, sem reutilizar a fórmula de nível
da ficha. Resultado: 82 conformes e 14 divergentes.

| Aquisição | Nível esperado | Débito esperado/obtido por cópia |
| --- | --- | --- |
| Espaço conhecido | 30 | 12 / 12 |
| Lista de ritual | 30 | 0 / 0 |
| Maldição domada | nível obtido | 0 / 0 |
| Criação | nível fabricado | 0 / 0 |

O débito foi conferido no agregado `DADOS_INVOC!JM2`, no vínculo
`DADOS_AM!HM19` e no indicador visível `FICHA AMALDIÇOADA!R55`.
As três leituras concordaram em todos os cenários.

Mais **24 controles de nome** (12 por cópia) em Espaço conhecido:
texto, número 7, zero numérico, FALSE, TRUE, texto "0", fórmula numérica,
fórmula vazia, célula vazia, texto literal "=7", fórmula textual e espaço
em branco. Apenas fórmula vazia e célula vazia foram excluídas. Presença
e tipos foram preservados, com débito correto de 10 nas três leituras.
Todos esses 24 controles passaram.

Isso verifica aquisição/débito, não o teto de entidades efetivamente
ativas nem a validade completa de suas definições e montagens. Avisos
independentes de requisitos não foram apagados ou desabilitados.

## Preservação e limites

Entradas temporárias foram feitas exclusivamente pela API nativa do
Google Sheets nas duas descartáveis autorizadas. **49 entradas por cópia
foram restauradas**, incluindo fórmulas e tipos originais, em blocos de
finalização mesmo diante de eventual falha do ensaio.

A releitura final comparou **86.067 posições por cópia**, das quais
**85.887 de MONTAGENS** (`A1:I9543`, aba inteira). Nessa aba, a API trouxe
36.972 posições explícitas; caudas omitidas foram normalizadas como
vazias. Foram comparados valores digitados/calculados, fórmulas, tipos,
notas e validações: **zero diferenças inesperadas**. Os metadados antes
e depois também foram iguais. A comparação é delimitada aos campos e
intervalos declarados; não é um snapshot integral de todas as abas.

As duas cópias foram conferidas visualmente no Sheets após restauração.
Os nomes sintéticos foram removidos e as auxiliares permanecem ocultas.
Não houve escrita de formatação, notas ou validações; a comparação de
células não certifica todos os atributos de formatação.

Não houve edição de fórmulas, instalação de Apps Script, geração de
pacote, substituição de montagens ou novos acionadores. A API de entrada
não dispara onEdit; esta rodada não acrescenta teste de evento ou
recuperação. Testes de código/smoke não foram repetidos para este
diagnóstico sem mudança de implementação.

Evidência sanitizada: `aquisicao_invocacoes_resultados_2026-11-07.json`.
Snapshots, respostas completas, regras consultadas e capturas permanecem
somente em `nuvem-b47/saidas/aquisicao-invocacoes/`, ignorado pelo Git.
Nenhuma ficha oficial ou de jogador foi acessada ou modificada.

Ramo separado `codex/auditoria-aquisicao-invocacoes-20261107`, sobre
`bcb82fcda9c6916fa26fa1248d87da0b6a286f99`. PR88 aberta e preservada em
`ab05bcf9cc5f831dfe460544f935546e40296ea8`; PR31 aberta e preservada em
`765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`. Sem merge ou alteração de main.

## Próxima fronteira

Corrigir AQ01 em etapa própria: reconciliar catálogo e extração com a
referência atual, retirar a progressão automática de Criação e atualizar
notas, fórmulas e moldes de recuperação correspondentes. Exigir snapshots
frescos, delta incremental estrito e ensaios nativos nas duas QAs antes
de considerar a correção concluída. Não instalar o pacote integral.

Ampliar a matriz com invocador abaixo/igual/acima do nível obtido, nível
obtido vazio, fabricação de novo projeto e troca de aquisição. O vazio
não foi usado nesta matriz e não deve ganhar uma semântica nova por
suposição. Nenhuma substituição global de COUNTIF ou de coordenadas.

Sol/Medium para revisar este diagnóstico; Sol/High para corrigir e ensaiar.
Não alterar configurações automaticamente nem delegar a subagentes.
