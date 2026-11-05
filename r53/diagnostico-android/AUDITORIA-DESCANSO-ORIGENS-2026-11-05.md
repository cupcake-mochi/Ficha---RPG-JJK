# Revisão da PR65 e auditoria dos descansos

Atualização: D01/D02 receberam correção separada na PR66. Consulte
`CORRECAO-DESCANSO-ORIGENS-2026-11-05.md` para os 18 cenários nativos
aprovados e a restauração, incluindo o ensaio de menu com queda ativa
após autorização pelo usuário. O restante conserva o diagnóstico anterior.

PR65 revisada no head `5f6abeae7517b51544edf3e2abb5b6c159aef9c5`.
Os dois checks estão SUCCESS, sem conflito. Teste focal dos seis alvos,
preflight/reversão, atualização da primeira PR65 e igualdade entre as duas
rotas de preparação passou novamente. Não apareceu outro bloqueio no
escopo de fórmulas e transporte corrigido pela PR65. A PR continua pronta
para revisão; isso não certifica todas as mecânicas.

O restante é diagnóstico separado, sem alteração de código de produção.
Base do livro: R66, JJK---Project
`e3058ad29180fdec2efec75b512446c49bf87b3d`, Existência Artificial → Repouso.
A capacidade diz que qualquer local conta como ambiente propício para
os descansos curtos e longos, conservando os demais requisitos. Também
dispensa Exaustão. Nos ensaios, assume-se que o descanso pode ser realizado
em segurança e satisfaz os outros requisitos; não se dispensou essa regra.

## D01 — descanso de Corpo Amaldiçoado não considera o local propício

Em ambas as descartáveis, Origem Corpo Amaldiçoado, marcante Existência
Artificial, Caminho Vanguarda, Exaustão zero e PE atual zero. Os máximos
calculados eram 60 na Era e 20 no Ciclo. Por edição real, escolher
FICHA!D45 = Longo · fora recuperou 30 e 10 PE, respectivamente. Esperados
60 e 20 pela regra de ambiente propício da Origem.

O menu voltou a Escolha o descanso e O45 registrou o ganho parcial.
Logo, houve processamento; não é hipótese de evento perdido ou latência.
Vida também foi modificada pelo descanso, mas a asserção deste achado é
a recuperação de PE, sem confundi-la com o procedimento de reparo.

## D02 — o descanso ainda usa a Exaustão bruta da Origem imune

Na mesma montagem, com PE zero e Exaustão marcada 3, Curto · fora não
recuperou PE em nenhuma cópia. O45 registrou nada mudou, embora O49
mostrasse que o estágio não aplica penalidades. Esperados 15 e 5 PE.
O grau foi preservado no ensaio para testar a compatibilidade com o valor
marcado; não se afirma que a Origem possa adquirir Exaustão pelo livro.

Controle por edição real: Curto · lugar propício com os mesmos máximos
e grau 3 devolveu corretamente 15 e 5 PE. Depois, novo Curto · fora com
PE zerado reproduziu o resultado zero. A execução curta exploratória
inicial ainda tinha a marcante antiga da fixture; o resultado foi repetido
após preencher Existência Artificial e foi o mesmo.

## Causa e alcance

Em `apps-script/Codigo.gs`, `contaDoDescanso_` usa DESCANSOS_[tipo].propicio
diretamente e indexa PE_DO_DESCANSO_CURTO_ com a Exaustão bruta. O estado
lido por `descansar_` tem Origem, mas não fornece imunidade nem a regra de
ambiente propício ao cálculo. A rotina considera Exaurido e Recuperação
Abundante, mas não Existência Artificial.

São duas manifestações relacionadas, em rotina que já existia antes da
PR65 e não foi alterada por ela. O ajuste de aviso/movimento da PR65 não
corrige esses consumidores da Exaustão. As duas pendências continuam
abertas, sem camuflar o resultado com checks verdes.

Antes de corrigir, incluir controles de outra Origem, custom válida com
base Corpo Amaldiçoado, cadastro inválido, máximos pequenos, perda zero,
limite de PE, descanso com queda ativa e preservação das regras de Corpo
Exaurido/Recuperação Abundante. Reusar a validação da base; não confiar no
texto bruto do cadastro. Não zerar o grau marcado só para evitar a falha.

## Evidências e restauração

Três cenários definitivos por cópia e uma execução exploratória por cópia,
todos pela interface do Google Sheets. As escritas por API prepararam e
restauraram os estados; as escolhas de descanso foram edições reais.
Nenhuma autorização nova foi pedida. Não foram adicionados helpers,
acionadores ou scripts de QA. Teste local histórico de descanso passou
nos seus 66 cenários; eles não cobrem essas regras de Origem.

Treze entradas por cópia foram restauradas e relidas iguais ao snapshot:
Caminho, Origem, vida, PE, Integridade, menu e resumo do descanso,
Exaustão, marcante, três caixas de Sequela e Sequelas extras. SOCORRO
estava encerrado e seus valores foram relidos iguais após os testes.
Não se ensaiou uma queda ativa nesta rodada.

Snapshots e leituras em
`nuvem-b47/saidas/auditoria-descanso-origens/evidencias-20261105.json`,
ignorado pelo Git. Não versionar dados, snapshots ou credenciais.

PR65 permanece no mesmo head. Sem merge, oficiais, jogador ou PR31;
PR31 conferida no hash `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
Sol/High para implementar/ensaiar a correção, Sol/Medium para revisão.
Não alterar configurações automaticamente.
