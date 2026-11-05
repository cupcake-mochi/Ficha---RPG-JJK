# Núcleo Dependente, Fôlego Recuperado e execução do descanso

PR67, sobre PR66 `f2bc70fd27b73db1cda3260b108f1c78371daea9`.
Corrige O01–O04 da auditoria ao lado e investiga O05. Livro R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Somente duas cópias descartáveis receberam o incremento. Sem merge,
alteração das oficiais, ficha do jogador, PR31 ou acionadores novos.

## Regras corrigidas

Núcleo soma Essência aos PE máximos e, em cada marco 6/10/14/18/22/26/30,
soma novamente metade da Essência arredondada para baixo. A alteração do
máximo não preenche o saldo. O máximo de Integridade passa a zero, que é
o contrato existente para ausência de barra; o saldo antigo não é apagado.
Os consumidores passam a ignorar seus estágios. Sem PE comum nem temporário,
o movimento fica pela metade, arredondado para baixo em passos de 1,5 m,
e Bloquear indica a proibição. Defesa permanece igual. As outras ações e
falhas automáticas da inatividade continuam sob controle da mesa.

Fôlego acrescenta a maior Classe disponível à recuperação normal do curto,
limitada ao máximo. Não vence uma recuperação proibida nem altera o longo.
Ambas as vagas são reconhecidas. As duas regras aceitam base herdada somente
quando o cadastro custom é válido; escrever o nome da base não basta.

O gerador produz quatro helpers DADOS_CUSTOM B128:B131 e quatro fórmulas
da FICHA: J30 (PE), J34 (Integridade), Z56 (Bloquear), O67 (movimento).
Não mudam chaves, tipos ou endereços da ANALISE. A opção explícita de
CONFIGURAÇÃO “trocar por” continua definindo o máximo final de PE. A ausência
de barra prevalece sobre um ajuste de Integridade, como as restrições físicas.
Uma configuração incompleta continua produzindo seu aviso legítimo.

## Investigação de tempo

O caminho antigo inicializava o módulo completo antes de processar D45.
`Descanso.gs` é gerado extraindo as mesmas oito funções de `Codigo.gs` e
um índice estático de 18 endereços. A edição isolada do menu passa por essa
rotina sem decodificar, remendar e iniciar o módulo pesado. Colagens que
atingem outras linhas/colunas continuam no caminho completo. A trava do
documento e o flush ao sair impedem duas recuperações pelo mesmo menu.
Se outra operação ocupa a trava, o usuário recebe uma orientação para repetir.
A continuação de paleta pendente existente é preservada, sem ensaio de cores.
O descanso pelo menu Recursos com queda ativa também usa a rotina extraída.

Instrumentação temporária usou somente relógio e log, sem leituras extras do
Sheets. Um controle Sem Energia sem Fôlego, no Ciclo, recuperou 5 PE nas duas
versões:

| Medida | Antes | Depois |
| --- | ---: | ---: |
| Execução informada pelo Google | 24,961 s | 13,986 s |
| Entre entrada e saída do handler instrumentado | 17,817 s | 11,329 s |
| Inicialização do módulo pesado | Executada | Não executada |

Antes, 7,449 s transcorreram entre a entrada e o ponto anterior à avaliação
do módulo; incluem decodificação, verificações, remendos e outras etapas.
A avaliação isolada levou 0,543 s, a leitura do descanso 5,341 s e o restante
do descanso após ela 4,313 s. Não confundir todo o intervalo com parsing.
Os custos fora do handler variaram também. Um par não identifica a causa
única dos dois timeouts históricos nem garante a eliminação futura deles.
Não são medições de abertura Android, memória ou tempo de recálculo isolado.
Os perfis temporários foram retirados antes dos ensaios finais.

## Validação

Local: 88 cenários de descanso; dez contas da auditoria agora conformes;
transporte atômico/idempotente, recusa de base divergente, igualdade entre
funções extraídas e fonte, limites do dispatcher, colagens e liberação de
trava mesmo em falha. Replay do modelo antigo real com a cadeia de remendos
confere os oito alvos. Smoke completo aprovado; geração `95250bc5cf94a1b0`,
zero SOBRAS e oito fórmulas iguais ao plano incremental. O pacote integral
foi preparado e compilado, sem ser instalado nas cópias ou oficiais.

No Google, nas duas descartáveis:

- Núcleo com Essência 3: PE 65/23, Integridade máxima zero; com Essência 4
  na segunda vaga: PE 68/24. PE comum 1 ou temporário 1 ativa movimento 9 m
  e Bloquear; ambos zero resultam em 4,5 m e proibição, Defesa 11 preservada.
- Níveis 5/6/10/14/18/22/26/30, Essência 3: 16 perfis conferidos e saldo
  zero preservado. Custom válida recebe o benefício; rota incompatível não.
- Ajuste final de PE 50 e zero respeitado; ajuste de Integridade 99 mantém
  ausência da barra. O ensaio inicial com fonte incompleta foi recusado com
  o erro esperado da CONFIGURAÇÃO, depois preenchido corretamente.
- Fôlego custom válido em propício: PE 18/6; segunda vaga fora com grau 2:
  6/2; grau 3: zero; perto do teto: 59→60 e 19→20. Cada edição real de D45
  foi relida somente como concluída após o retorno do menu ao convite.
- Vida e Integridade atual zero com Núcleo e 1 PE: Registrar queda ofereceu
  Aguentar e gravou Morrendo; não declarou derrota por Integridade. O longo
  fora pelo menu Recursos recuperou vida 77/37 e PE 65/23, encerrou a queda
  e manteve a ausência de barra.
- Restauração por edição real: J30, J34, Z56 e O67 individualmente e os
  quatro helpers por colagem em B128:B131. Os oito alvos foram relidos iguais
  ao plano em cada cópia; uma edição adicional de B128 confirmou o valor
  adulterado antes de sua recuperação automática. Dezesseis alvos conferidos.

Ao concluir, 24 entradas alteradas por cópia foram restauradas, inclusive
CONFIGURAÇÃO e SOCORRO; DADOS_CUSTOM voltou a ficar oculta. Releitura de
1.433 células por cópia, comparada ao snapshot com somente os oito alvos
novos, encontrou zero diferenças de valores/fórmulas, notas e validações e
zero erros de fórmula nesses intervalos. Codigo.gs foi reaberto e relido
integralmente igual ao SHA proposto nas duas cópias, sem perfil QA67.

Uma repetição final do smoke local excedeu 60 s em `pacote_runtime.js`
com memória disponível menor que 800 MB e swap cheia. O mesmo teste isolado
concluiu aprovado; não se modificou o limite nem o resultado para ocultar a
ocorrência. O smoke completo anterior passou com o mesmo código de produção;
a conferência do head final também deve considerar os checks do GitHub.

O JSON contém resultados sanitizados. Snapshots, fontes instaladas e leituras
completas ficam somente em `nuvem-b47/saidas/correcao-origens-recursos/`, ignorado
pelo Git. As cópias são ambientes de ensaio, não novos modelos oficiais.

## Atualizar uma instalação existente, em etapa futura

1. Confirmar a cadeia até PR66 e obter snapshot novo do código, das oito
   células, entradas, notas e validações. Para base divergente, interromper
   e apurar o delta; não fazer substituição global nem instalar o pacote inteiro.
2. `preparar_origens_recursos.prepararCodigo` exige Codigo.gs SHA-256
   `d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084`.
   A proposta final é
   `bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130`.
   Inclui o molde de restauração e a rotina leve; substitui somente Codigo.gs.
3. Preparar as oito fórmulas por `planejar(snapshot)`, com locale, conferindo
   todas as fórmulas anteriores antes de escrever. As quatro células de helper
   devem estar vazias. O plano conserva notas, formatos e validações.
4. Ensaiar primeiro numa cópia, reler o código salvo e as oito fórmulas,
   conferir recálculo, restauração por edição e menus. Guardar reversão do
   snapshot, inclusive do código. Não executar construir/continuar.

A promoção não está autorizada nesta tarefa. Modelo recomendado: Sol/Medium
para revisão independente, Sol/High para nova investigação; sem mudar ajustes.
