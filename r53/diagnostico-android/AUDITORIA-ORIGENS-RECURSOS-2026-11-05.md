# Auditoria de recursos e estados das Origens

Registro histórico do diagnóstico anterior à correção. O01–O04 foram
tratados na própria PR67; veja `CORRECAO-ORIGENS-RECURSOS-2026-11-05.md`
para implementação, ensaios e limites da investigação de O05. Os resultados
originais abaixo foram preservados como evidência, não representam o head novo.

Diagnóstico separado sobre PR66 `f2bc70fd27b73db1cda3260b108f1c78371daea9`.
A revisão dessa PR está em `REVISAO-PR66-2026-11-05.md`: dois checks
SUCCESS e sem novo bloqueio no escopo de Existência Artificial.
Este ramo não corrige produção, não faz merge e não altera a PR31.

Livro R66, `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
seções Núcleo Dependente e Fôlego Recuperado. As mesmas regras essenciais
também constam do catálogo versionado `ficha-v01/origens-do-livro.json`.
Não é necessário atualizar o catálogo para reproduzir estes achados.

## Método

Duas cópias descartáveis já usadas nos ensaios da pilha, com PR66 instalada.
Snapshot novo antes das escritas. Entradas preparadas pela API; recálculo
das fórmulas no Google. Os descansos foram escolhas reais de FICHA!D45 pela
interface, aguardando retorno ao convite e conferindo O45. Nomes das menores
vieram das listas válidas CP/CQ da DADOS_CUSTOM e foram escritos nas entradas
R44/AH44 da FICHA PESSOAL; S52/AG52 conservaram as fórmulas de espelho.
Essa preparação por API não dispara a carga dos textos das cartas: caixas
de descrição vazias nessa preparação não foram contabilizadas como defeito.

Assumem-se a história Manutenção e as permissões de mesa necessárias para
Núcleo Dependente. Legados são texto de história, não um validador automático
dessas permissões. Não se afirma uma concessão de habilidade por história.
Buff de PE preservado em 10: base do Caminho Vanguarda 50/10 + Buff 10
resultou em 60/20 na Era/Ciclo. Níveis 10/2, Classes disponíveis 3/1.
Condições de carga e demais impedimentos mantidos nos controles de movimento.

## O01 — Núcleo Dependente não aumenta os PE máximos

Com Essência 3 e a menor na primeira vaga, os máximos continuaram 60/20.
O esperado é 65/23: dois marcos na Era, nenhum no Ciclo. Na segunda vaga,
com Essência 4, continuaram 60/20 em vez de 68/24. A fórmula J30 não
consulta a menor, a Essência nem seus marcos. P2: reserva máxima menor.
O saldo atual não deveria ser preenchido ao máximo por esta correção.

## O02 — Núcleo Dependente conserva uma barra de Integridade

A regra retira a barra, mas J34 continuou com 92/28, com Essência 3;
com Essência 4, 101/29. O esperado é ausência da barra, representada por
máximo zero no contrato atual. A fórmula geral não consulta a menor.
Com 1 PE comum e Integridade atual zero, o recálculo ainda levou o
deslocamento a zero nas duas cópias; esperado 9 m, pois a Origem não tem
a barra e está ativa. Essa consequência foi confirmada, não apenas inferida.
P1: estágios e consumidores de Integridade podem atuar em quem não possui
essa reserva. A eventual derrota em SOCORRO é risco derivado; não foi
gravada uma nova derrota para demonstrá-lo.

## O03 — inatividade do Núcleo não alcança movimento e Bloquear

Com ambos os tipos de PE zerados, a ficha mostrou 9 m e `2d10 + 0`.
Esperados metade do deslocamento normal e indicação de que não pode bloquear.
Com 1 PE comum ou 1 temporário, os controles de 9 m, rolagem e Defesa 11
conferem. A segunda vaga também não alterou o comportamento sem energia.
P2: indicação de movimento e ação indisponíveis. Defesa 11 deve permanecer.
Falhas automáticas em testes e outras ações/Reações são regras de mesa;
não se demonstrou uma execução automática delas pela ficha.

## O04 — Fôlego Recuperado não soma a Classe ao descanso curto

Com menor válida de Sem Energia, a recuperação foi somente a normal.
Fora, com Exaustão 2, a Era recuperou 3 em vez de 6 PE e o Ciclo 1 em vez de 2.
Em local propício, na segunda vaga, recuperaram 15/5 em vez de 18/6.
O menu voltou ao convite e O45 registrou esses ganhos: não é apenas uma
escolha que ficou pendente. Fora com grau 3, PE zero foi preservado como
esperado; a menor não pode vencer uma recuperação proibida. P2.

`descansar_` não lê Classe nem valida essa menor, e `contaDoDescanso_`
não acrescenta o bônus. Essa omissão já existia antes da PR66. O futuro
ajuste deve reconhecer a Origem/base válida, as duas vagas, o teto e as
proibições. Usar Classe disponível da progressão, sem inferir pela última
montagem ou maior Kata conhecida. Não dar bônus a uma escolha incompatível.

## O05 — dois eventos de descanso atingiram o tempo de execução

Na cópia Ciclo, dois onEdit reais ficaram com D45 ainda na escolha e sem
recuperar os PE. A página de Execuções do projeto vinculado registrou
Tempo limite atingido e Tempo máximo de execução excedido:

| Início local em 05/11 | Duração informada pelo Google | Resultado |
| --- | --- | --- |
| 10:32:28 | 30,568 s | Tempo limite atingido |
| 10:39:32 | 30,467 s | Tempo limite atingido |

O primeiro era uma tentativa exploratória com Fôlego; o segundo um controle
sem a menor. Não entram nos oito eventos concluídos nem nas contas de bônus.
A primeira tentativa não foi mantida intacta até a investigação do log;
não se usa seu PE como medição mecânica. O log confirma que ela terminou
por tempo, não a causa nem o ponto de interrupção. As repetições conclusivas
estão no JSON. O controle sem menor concluiu após repetir com o mesmo código.

É uma pendência operacional confirmada, de causa ainda não isolada. Não
se atribui o problema à PR66 nem à leitura adicional sem comparação causal.
Não foi executado um A/B válido com o código anterior. O Codigo.gs salvo e
relido após reabrir permaneceu no SHA `d5845c03…`, igual ao ensaio anterior.
Não foi instalada uma correção nova ou um helper de instrumentação.
As durações são do Apps Script: não medem abertura Android, RAM ou o tempo
isolado da conta. A promoção futura precisa considerar essa intermitência.

## Cobertura, restauração e próximos passos

Vinte e quatro cenários/perfis nativos concluídos: 16 perfis de recálculo
nas duas cópias (incluindo controles e uma repetição) e oito descansos por
edição real. Os dois timeouts ficam separados. No controle sem Núcleo e
no controle de menor incompatível com Latente, os máximos gerais, a Defesa,
Bloquear e o deslocamento conservaram seus resultados esperados.

O diagnóstico local reproduz dez contas:
seis conformes e quatro divergentes. Exit zero significa execução completa,
não aprovação das regras. Não está incluído no smoke como teste verde.

Quatorze campos por cópia foram restaurados, preservando fórmulas como
fórmulas. A comparação de 1.609 células materializadas por cópia não encontrou
diferenças em valores/fórmulas, notas ou validações, nem erros de fórmula.
Formatos também foram comparados nos intervalos cujo snapshot os continha,
sem diferença. Não houve nova derrota, escrita em SOCORRO, mudança de catálogo,
construção da ficha, acionador ou instalação de helper. Não foi uma varredura
integral de todas as abas. Snapshots/leituras/recibos privados permanecem em
`nuvem-b47/saidas/auditoria-origens-recursos/`, ignorado pelo Git.

Este ramo entrega diagnóstico e roteiro reproduzível, sem consertos. Para a
próxima correção, começar pelo contrato de ausência da barra e PE máximos
do Núcleo; validar as duas vagas, base custom válida, controles incompatíveis,
PE temporários e consumidores de Integridade. O descanso deve preservar
requisitos, limites e capacidade de processamento; investigar O05 antes de
ampliar as leituras do evento. Condições narrativas continuam com a mesa.

Núcleo Dependente e Fôlego não esgotam todas as Origens, custos/Classes ou
combinações custom. Metabolismo Flexível é uma escolha de conversão, não
uma recuperação automática obrigatória: não entrou como defeito confirmado.
Aplicar cura não identifica a fonte da cura; não se classificou como bug
uma cura inválida que o operador teria informado como válida.

Sem oficiais, jogador, PR31, acionadores novos ou alterações de acesso.
Sol/High para investigar/corrigir; Sol/Medium para revisão. Não mudar ajustes.
