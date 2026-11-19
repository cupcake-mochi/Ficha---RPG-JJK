# Auditoria ampliada de mecânicas · 04/11/2026

Diagnóstico sobre PR58 `11ab8d1`, ramo separado
`codex/auditoria-mecanicas-ampliada-20261104`. Nenhuma correção de produção,
merge, instalação em oficial ou alteração na PR31. Não declarar a ficha 100%.

## Método e limites

Livro conferido: R66, JJK---Project `e3058ad29180fdec2efec75b512446c49bf87b3d`,
`sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`, SHA256
`315ba23a9044234b8eab9e94ff1412d553b45c46089548809741777b1e287893`.
Regras usadas: Dano na alma/Estágios de Integridade, Exaustão e Integridade,
recursos temporários. Testes em cópia descartável da QA integrada da Era.

Nesta rodada, a API nativa do Sheets calculou as fórmulas; ela NÃO dispara
onEdit. O navegador informou “Local browser use is disabled in Work settings”.
Foi solicitado habilitá-lo, sem tentar contornar a configuração. Ensaios de
colagem abaixo são locais, com helpers reais e Range simulado, não eventos Google.

Snapshots, IDs, células completas e respostas privadas em
`nuvem-b47/saidas/auditoria-ampliada/`, ignorado. Os 15 campos alterados foram
restaurados por `userEnteredValue` e relidos iguais, inclusive fórmulas.
Duas abas novas de ensaio permanecem somente na cópia descartável.

## Achados

### A01 · Integridade não reduz o deslocamento calculado — reproduzido no Sheets

- FICHA: máximo 26, atual 13, base 9 m, sem carga, Exaustão ou restrição corporal:
  D37 indica estágio 2 e metade do deslocamento; O67 continua **9 m**, esperado 4,5 m.
- Base 12 m, mesmo estágio: **12 m**, esperado 6 m.
- Base 6 m e Exaustão 2: **4,5 m**, esperado 3 m pela regra de usar o menor limite.
- INVOCAÇÕES: máximo 16, atual 8; X18 indica estágio 2; S24 continua **9 m**,
  esperado 4,5 m.

As fórmulas de deslocamento não dependem da Integridade. A ficha oferece
Buff/Debuff manual; portanto o diagnóstico é falta de aplicação automática no
total exibido, não prova de que o jogador não possa ajustar o valor. A nota do
deslocamento enumera carga e Exaustão, mas não explicita esta exceção manual.
Uma futura correção precisa decidir como evitar dobrar ajustes manuais antigos.
Não basta dividir o total indiscriminadamente: combinar Exaustão, carga, Corpo
Exaurido e ajustes de campanha exige oráculo específico.

### A02 · Integridade mínima 1 com vida máxima zero — reproduzido no Sheets

Entidade com alma, vida máxima 32, Buff/Debuff de vida −32: V13 fica **0**, W18
fica **1**. A regra concede mínimo 1 somente quando a vida máxima é positiva.
O gerador `ficha-v01/ficha_invocacoes.py` usa `MAX(1,INT(vida/2))` sem essa guarda.
Controles positivos 1, 2 e 3 retornaram 1 corretamente; “Sem alma” retornou `—`.
É caso de fronteira obtido por ajuste explícito, não evidência de entidade comum
nascendo espontaneamente com vida zero.

### A03 · Colagem na caixa ± de entidade pode apagar a reserva vizinha — local

Helper real `redutorDaInvocacao_`, evento `X13:Y13`, X13=−5 e Y13=7:
vida 10/20 e temporária 3 viram vida 8/20 e temporária 0 corretamente, mas
**Y13 também é apagada**. O helper lê só a primeira célula e usa
`e.range.clearContent()` no intervalo inteiro. Controle editando apenas X13
preservou Y13. Y13 é a reserva de PE, não parte da caixa ±.

Reproduzido no helper isolado, ainda falta passar pela cadeia completa do
evento e por colagem real no Sheets. Prioridade maior por possível perda de entrada.

### A04 · Colagem abrangendo TEMP ignora seu teto — local

Helper real `prenderTemp_`, vida máxima 20 e TEMP=15: evento em AF26 corrige para
10; evento abrangendo `AF26:AR26` deixa **15**. A comparação exige igualdade
literal do A1. O teste usa o intervalo completo das caixas TEMP e ±, sem propor
editar parte de célula mesclada. Falta confirmar evento e mesclas pelo navegador.

### A05 · Avisos de estágio incompletos — texto confirmado no Sheets

FICHA!D37 no estágio 3 informa apenas desvantagem em ataques/TRs, sem lembrar
a redução da Classe máxima. No estágio 4, “Você não é mais você mesmo” omite
Inconsciente/Derrotado. O livro vigente explicita ambos; a entidade já lembra
Classe pela metade. É deficiência do resumo exibido, não prova de falha do
registro SOCORRO nem razão para remover avisos mecânicos legítimos.

### Anterior A00 · Temporários com máximo zero

Permanece confirmado, sem correção, na PR58 e em
`AUDITORIA-RESERVAS-2026-11-04.md`. Não contar vida e PE como causas diferentes.

## Cobertura e controles conformes

18 cenários nativos nas caixas da ficha/entidade:

- Sete níveis de Integridade com máximo 26: atuais 26, 20, 19, 13, 6, 0 e 17.
  Todos classificaram o estágio correto; a volta a 17 retornou ao estágio 1.
- Cinco cenários combinados de movimento: Exaustão isolada, dois casos de
  Integridade, meia marcha e impedimento por carga. Exaustão isolada → 4,5 m;
  meia marcha → 4,5 m; impedimento → 0 m. Não foi retestado o cálculo da carga,
  pois os sinalizadores internos foram fixados para isolar o consumidor.
- Entidade no estágio 2, entidade com máximo de vida zero e quatro controles
  de vida/alma descritos acima. O nome e valores da entidade eram dados de QA.

Montagem: 89 casos do avaliador local passaram. Dezesseis casos também passaram
em abas de ensaio nativas usando as fórmulas do modelo publicado: VT, custos de
Aura/Explosão, cura proibida em Classe 0, melhorias/restrições, distribuição
inválida/fracionária, condições de entidade, teto de cura/VT, Concentrada versus
Duradoura, TR compartilhado, Recuo, Mais Um e Família desconhecida. São regressões
contra expectativas versionadas, NÃO revalidação de todas as regras da R66 nem
teste dos cartões/menus instalados. Doze rejeições legítimas foram preservadas.

Suites locais adicionais: descanso 66, socorro 98, cura recebida 35 aprovados.
Diagnóstico novo de eventos: quatro casos, dois conformes e duas divergências.
Seu exit code zero apenas significa execução concluída; NÃO significa que
todas as mecânicas passaram. Nenhuma expectativa foi enfraquecida.

## Ainda na fila

1. Colagens A03/A04 por edição nativa e cadeia completa do onEdit.
2. Conferir teto de temporários em invocações: a rota de INVOCAÇÕES não chama
   `prenderTemp_`; é suspeita de cobertura, ainda não listada como defeito nativo.
3. Efeitos condicionais de Bênçãos (inclusive Vigília), imunidades de Origem,
   estágios de Integridade versus custos/Classe e o que é explicitamente manual.
4. Usos por descanso/cena, armaduras/armas, montagens custom e demais capacidades
   ainda não cobertas contra a R66. Testes históricos não garantem estes casos.
5. Após priorização, correções separadas com prevenção de regressão e ensaio
   nativo; não aplicar automaticamente os achados às oficiais.

PR57 e PR58: dois checks SUCCESS cada na conferência desta rodada. PR31 segue
aberta em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`, intocada.
Recomendação AGENTS: Sol/High para investigar/implementar; Sol/Medium para revisão.
