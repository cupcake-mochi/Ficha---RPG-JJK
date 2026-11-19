# Reserva Excedente e Bolsa Orgânica · 05/11/2026

P01/P02 da auditoria da PR68 corrigidos em incremento separado sobre
`6a5440ab6aed7ee953dc8686dd3dfd7e9b5e19f3`. Livro de referência:
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d` (R66).
Sem merge ou aplicação nas oficiais, jogador ou PR31.

## Comportamento corrigido

- Reserva Excedente válida soma 2×Essência aos PE máximos, em qualquer vaga.
  Essência 3: 50/10 → 56/16 nas cópias Era/Ciclo; Essência 4: 58/18.
  Alterar a capacidade/atributo não recarrega o saldo atual.
- Bolsa Orgânica válida soma Maestria ao limite de carga. Força 3:
  8 → 10/9, conforme Maestria 2/1. Excesso e limite duplo acompanham o novo
  teto; no nível 30, Maestria 4 leva o limite a 12.
- Origem publicada e base custom validada recebem o benefício. Origem
  incompatível ou cadastro inválido não recebe. Buff e Somar continuam
  aditivos; um Trocar por válido define o resultado final, inclusive zero.

`ficha-v01/passivas_origem.py` calcula dois helpers novos (B132:B133 de
DADOS_CUSTOM) e envolve somente as fórmulas de FICHA!J30 e DADOS!CZ41.
Duas notas explicam a aplicação automática e a revisão de compensações.
Total: quatro fórmulas e duas notas, sem mudar layout, ANALISE12/esquema2,
249 contextos, invocações, Família ou catálogo. A paridade integral do modelo,
retirados esses seis alvos e o metadado de geração, passou.

## Recuperação de fórmulas

O ensaio real encontrou outra lacuna: DADOS!CZ41 não era encaminhada pelo
onEdit antigo à recuperação. O código novo inclui uma guarda específica
para essa célula, antes do pipeline pesado. Colagens que a abrangem restauram
somente CZ41; as outras células da DADOS não são regravadas. A guarda compara
linhas/colunas antes de consultar o nome da aba nas edições comuns.

Houve ensaios intermediários em que CZ41 permaneceu texto. Não foram
contados como sucesso nem reparados manualmente para aprovar o teste.
Após salvar/reabrir e repetir com o código definitivo, as duas cópias
recuperaram a fórmula integral. J30 e a colagem B132:B133 também foram
restaurados: oito fórmulas conferidas, por edição nativa, no total.
Um registro temporário de diagnóstico na Era foi retirado; os dois
Codigo.gs foram relidos integralmente com o mesmo hash final.

## Validação e limites

- 207 verificações locais: modelo integral, seis alvos, atomicidade,
  idempotência, reversão, conversão de idioma, roteamento estreito e guardas.
- 26 cenários por modelo (52 registros), incluindo ambas as vagas,
  Essência zero/3/4, Maestria, remoção, custom válida/inválida, carga leve/
  excedida/limite duplo, Buff, Somar, Trocar por e controles de Núcleo/Fôlego.
- Configuração incompleta conservou o aviso/erro legítimo. O ensaio no
  nível 30 identificou Integridade parcial na fixture; ela foi corrigida
  para o controle de movimento, sem modificar a regra para esconder o efeito.
- Fôlego recuperou 15/3 PE pelo menu real e voltou ao sentinela. Esse ensaio
  usou a mesma implementação matemática antes da última guarda estreita de
  CZ41; as recuperações finais usaram o código definitivo.
- O preflight recusou Buff de PE/carga e Somar com compensações possíveis,
  inclusive +2/−2 que se anulam. Não foram apagados ajustes para instalar.
- Smoke completo final e pacote passaram. Uma tentativa anterior excedeu
  60 s na montagem local sob pressão de memória; o limite não foi aumentado.
- Dezoito entradas restantes por cópia restauradas ao encerrar; preparações
  já desfeitas nos controles não entram nessa contagem. 1.899 células por
  cópia relidas sem diferenças de valores/fórmulas, notas e validações,
  exceto os seis alvos novos esperados, sem erros nos intervalos. DADOS e
  DADOS_CUSTOM voltaram à visibilidade anterior. SOCORRO não foi escrita.

Esses testes não medem RAM, abertura Android ou latência geral. P03,
Prática Cotidiana, continua pendente em entrega estrutural separada.

## Atualização de fichas existentes

Não instalar a geração integral nas fichas existentes. Primeiro integrar e
ensaiar a cadeia anterior até PR67. Este preparador exige exatamente o
Codigo.gs PR67 de hash `bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130`.
Em cópia descartável, fazer snapshot novo do código e dos seis alvos, com
valores efetivos e o contexto `AUX` do preparador (inclui C11:F40).

`preparar_reserva_bolsa.js` gera o código incremental e o plano de escrita
preciso. Rodar `planejar(snapshot)` antes de qualquer gravação. Capacidade
ativa com Buff/Somar não zero ou ambíguo exige conferir com o responsável
qual parcela é compensação antiga; o programa não deduz nem subtrai essa
parcela. Notas novas avisam sobre esse cuidado. Trocar por válido já exclui
o acréscimo automático e permanece final. Um estado inválido é recusado.

Aplicar somente os pedidos retornados pelo preflight e o Codigo.gs preparado,
salvar, reabrir e reler o código e os alvos. Repetir cálculo, remoção e
recuperação por edição real na cópia. Para reverter, usar o snapshot do código
e o plano inverso com guarda dos valores novos exatos. Snapshot e ensaio
novos são necessários antes de eventual aplicação autorizada nas oficiais.

Geração: `326e5d03a6aac4ee`, zero SOBRAS. Código incremental final:
`4b0d2cc1952ac3726a47a1969c66c04e30658f7397a927f7af0930615ee9daa9`.
O pacote integral foi gerado/testado, mas não instalado. Fontes nativas,
snapshots e registros completos permanecem ignorados pelo Git em
`nuvem-b47/saidas/correcao-reserva-bolsa/`. Evidência sanitizada: JSON ao lado.

Sol/Medium para revisão; Sol/High para o próximo ensaio estrutural.
Não alterar configurações automaticamente.
