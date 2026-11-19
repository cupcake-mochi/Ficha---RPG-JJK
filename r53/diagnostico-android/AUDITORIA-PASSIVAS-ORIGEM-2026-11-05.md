> Atualização: P01/P02 têm correção e ensaios separados em
> `CORRECAO-RESERVA-BOLSA-2026-11-05.md`/JSON. P03 continua pendente.
> Os resultados abaixo preservam o diagnóstico anterior à correção.

# Reservas, carga e repertório das Origens

Diagnóstico sobre PR67 `971228d2b82980a331a8ebcc577bde6f4fa8b804`.
Ramo separado `codex/auditoria-passivas-origem-20261105`; nenhuma correção de
produção aplicada. Livro R66, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
O catálogo versionado contém as mesmas regras. Esta rodada não certifica o
livro atual fora dessa referência nem todas as mecânicas da ficha.

## Método

Duas descartáveis Era/Ciclo, com o mesmo incremento PR67. Metadados e snapshots
novos antes de escrever. Preparação de estados pela API, cálculo pelo Sheets
nativo. Bolsa Orgânica e Prática Cotidiana foram selecionadas pela interface na
primeira vaga; Reserva Excedente, na segunda. Nas duas vagas houve controles de
recálculo adicionais. Não se infere que a preparação por API testou o onEdit.

Vanguarda nos níveis 10/2, Força 3, PE atual zero, Buff de PE zero e Buff de carga
zero nos controles. Essência foi alterada pelo campo de base AJ21, preservando
a fórmula AJ19; Força, por D21. Maestria efetiva lida como 2/1, sem confundir com
Classe disponível. Não se usou troca manual de fórmulas para obter os defeitos.

Vinte releituras de cenários por cópia, incluindo controles e repetições. O replay
independente compara 52 campos: 28 conformes e 24 divergentes por **três causas**.
Não são 24 bugs. Mais uma leitura focal conferiu o mostrador visível P59, e a
inspeção estrutural confirmou as cinco linhas de Classe 0, D323:T327.

## P01 — Reserva Excedente não aumenta os PE máximos

A menor corporal aumenta o máximo em duas vezes a Essência, acompanhando o
atributo. Com Essência 3 na primeira vaga, J30 manteve 50/10 em vez de 56/16.
Com Essência 4 na segunda, manteve 50/10 em vez de 58/18. A seleção real pela
interface repetiu esse resultado. O saldo zero foi preservado em todos esses
estados; a correção futura também não deve preenchê-lo.

J30 tem a guarda de configuração e o acréscimo de Núcleo da PR67, mas não há
termo para Reserva Excedente. O catálogo e o texto da menor estão corretos.
Compensação existente: somar 8 no Buff P30 produziu 58/18, como esperado para
Essência 4. Portanto, não é impossível montar a ficha corretamente; falta aplicar
o ganho publicado à escolha e atualizar o valor quando o atributo muda. P2.

Uma futura automação deve preservar CONFIGURAÇÃO “trocar por”, as duas vagas e
a herança custom válida. Também deve considerar Buffs que já compensam essa
regra: não somar automaticamente sobre uma compensação antiga sem revisão.

## P02 — Bolsa Orgânica não entra no limite de carga

A menor do Híbrido aumenta a capacidade em Maestria Volume; o dobro acompanha
o novo limite. Com Força 3, o limite normal é 8. Com a menor em qualquer vaga,
CZ41 continuou em 8, em vez de 10/9 para Maestria 2/1.

O impacto não ficou só no número: Bastão válido, Volume unitário 1, quantidade
inteira 8 ou 16, mais 0,3 já presentes, reproduziu os consumidores nas duas cópias:

| Carga | Resultado sem compensação | Esperado com Bolsa |
| --- | --- | --- |
| 8,3 | Deslocamento 4,5 m; carga acima | 9 m; dentro de 10/9 |
| 16,3 | Deslocamento zero; acima do dobro de 8 | 4,5 m; acima do limite, abaixo do dobro de 10/9 |

Não foi aplicada uma penalidade falsa para produzir verde: o consumidor de carga
está seguindo o limite que recebeu. O ponto ausente é o benefício em CZ41. P2,
com consequência mecânica demonstrada.

**Ajuste manual explicitamente existente:** a nota de L85 orienta usar o Buff de
carga para habilidades. Somar Maestria em L86 produziu limites 10/9 e restaurou
os dois resultados de movimento esperados. Isso delimita o achado como benefício
publicado ainda dependente de ajuste manual, e não falha do campo de Buff.
Migração futura deve evitar duplicar essa compensação e conservar “trocar por”.

## P03 — Prática Cotidiana não aparece no total e falta espaço no nível alto

A menor corporal concede dois feitiços adicionais de Classe 0, fora da quantidade
normal. Com a escolha na primeira vaga, HM10 continuou em 3/2 nos níveis 10/2;
com a segunda vaga, o mesmo. O total com a menor é 5/4. No nível 30, HM10 ficou
em 5, enquanto o total é 7. O mostrador nativo FICHA AMALDIÇOADA!P59 confirmou
“5 feitiços grátis · 6d8 cada”. Ele lê KV32, que concatena HM10/HM11.

Existem somente cinco linhas dedicadas, D323:T327. No nível 30, faltam duas
linhas para registrar o ganho além das cinco normais. `N_ZERO` corresponde ao
máximo da tabela geral, sem reservar duas posições adicionais para a menor.

**Limite da reprodução:** as linhas disponíveis aceitaram nomes de teste e
retornaram Utilidade. Não foi demonstrado bloqueio de conjuração da terceira
ou quarta linha nem se atribui esse comportamento ao aviso antigo de nível:
o motor R53 já substitui a saída antiga dessas linhas. O achado confirmado é
mostrador incompleto e capacidade física insuficiente para sete entradas. P2.

Não compensar com “feitiços extras” de Classe comum: a menor não concede vagas
de Talento/invocação nem feitiços comuns. A correção exige estudar o registro
de duas aplicações extras e seu transporte, preservando os 249 contextos
existentes, seus IDs, ANALISE12/esquema2, cartões e entradas já preenchidas.
Não inserir linhas globalmente nem apenas elevar um número sem prover o espaço.

## Controles que passaram e limites da cobertura

- Manifestação Instintiva, na primeira vaga, concedeu uma vaga de Talento de
  Origem. Traço Incorporado, na segunda, também. Construção Especializada, na
  primeira, idem. Retirar a menor voltou a zero. Conferidos HM51 nas duas cópias.
- Coexistência concedeu dois feitiços de Origem e os incluiu no total gratuito,
  HM53/HM55, nas duas cópias. Não se afirma que todo o uso dos cartões foi testado.
- As compensações manuais de PE e carga funcionaram, com saldo de PE preservado.
- Catálogo de Origens revisto para separar efeitos passivos numéricos de escolhas
  e capacidades de cena. Rerrolagens, vantagens, sentidos, decisões do mestre,
  Reserva Impregnada, Metabolismo Flexível e usos por cena não foram tratados
  como erros novos por não dispararem automaticamente. Não foi simulado combate.
- Especialidade Antiga exige uma competência escolhida em Conhecimento Reavivado.
  Não foi demonstrada concessão automática incorreta nem testada uma automação
  dessa escolha; continua fora do resultado desta rodada. Não usar a perícia-base
  da Origem como substituta silenciosa dessa escolha adicional.
- As antigas suites cartas_custom/marcas_custom continuam dependendo de fixture
  histórica privada ausente. Não foram contadas como aprovadas nem refeitas contra
  uma exportação incompatível. As demais cartas/Bênçãos mantêm os limites de
  cobertura dos relatórios anteriores.

## Preservação e reprodução

Os dois Codigo.gs foram relidos integralmente e continuam no SHA da PR67
`bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130`.
Não foram regravados. Snapshots, leituras e recibos estão somente em
`nuvem-b47/saidas/auditoria-passivas-origem/`, ignorado pelo Git.

Inventário, Buff de carga, nomes de teste, segunda vaga e demais preparações
que já tinham sido desfeitos durante os controles foram relidos. Ao encerrar,
nove diferenças restantes de entrada por cópia foram restauradas. Comparação
de 1.939 células por cópia nos campos presentes nos snapshots não encontrou
diferenças; zero erros de fórmula retornados nos intervalos finais. Notas não
foram escritas; nas linhas de Classe 0 o snapshot focal não pediu notas e,
portanto, a igualdade delas não foi incluída na certificação. Interface final
das duas cópias inspecionada, sem as escolhas e nomes de QA.

Replay: `node r53/testes/auditoria_passivas_origem.js <ensaios.json privado>`.
Sem argumento, imprime só os alvos e a quantidade estrutural de linhas. O comando
não escreve no Google; saída zero indica execução concluída, **não aprovação**
das regras. O JSON ao lado contém somente o resultado sanitizado do replay.

Próxima correção sugerida: P01/P02 em incremento próprio, com preflight e atenção
a compensações antigas; P03 requer uma entrega estrutural separada. Não retirar
avisos legítimos nem trocar o contrato para ocultar o problema. Sem merge,
oficiais, jogador, PR31, novos acionadores, agentes ou mudanças de acesso.
Sol/High para implementar/ensaiar; Sol/Medium para revisar. Não mudar ajustes.
