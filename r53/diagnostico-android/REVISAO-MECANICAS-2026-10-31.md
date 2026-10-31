# Revisão mecânica em cópias descartáveis · 30–31/10/2026

Base `main` 5ea10b482f638dc767a3aa07af21796007c90487; ramo separado
`codex/revisao-mecanicas-20261030`. Só duas cópias nativas de QA receberam
alterações. Nenhuma escrita nas oficiais, na ficha do jogador ou na PR31.
Não houve instalação de Apps Script, reconstrução, novo acionador, ampliação
de acesso, Office ou ensaio de paleta.

## Resultados e falhas encontradas

**1. Cura/vida temporária guardada podia ficar indisponível sem invalidar o cartão.**
O emissor de cartões combina o flag da função com sua porta de permissão.
Ao fechar Amparo, os flags efetivos de cura e vida temporária ficam falsos
e seus pontos efetivos ficam zero. O aviso anterior verificava justamente
esses flags, já bloqueados; assim, uma versão com `Cura` salva podia apresentar
`valida=TRUE`, sem aviso e sem produzir a cura registrada.

Reprodução: preparar cura no cartão, fechar Amparo, reler entrada, versão
oculta, resultado e diagnóstico. Antes: cura salva na MONTAGENS, resultado
zero, aviso vazio e validade verdadeira. Depois do delta de diagnóstico:
resultado continua zero, escolha salva permanece e aparece
`Amparo Fechada: função de cura salva indisponível`, com validade falsa.
O teste também cobriu a entrada ainda numérica e a entrada mascarada por `—`.

Correção preparada no gerador: `avisos_cartoes_r53.formula_avisos_funcoes`
consulta a função da **Classe ativa**, preservada na MONTAGENS, e a entrada
direta. Não abre a permissão, não redistribui pontos nem altera as contas.
Conserva o aviso de Trunfo e diagnostica funções salvas incompatíveis com
modalidades fixas. O modelo regenerado mudou **244 fórmulas em GA**;
as outras cinco já eram iguais. Todas as demais células, metadados do layout,
geometrias R53 e contrato da ANALISE ficaram iguais à base.

**2. A recuperação automática ao reabrir Amparo não foi aprovada.**
No uso real do editor da cópia da Era, o fechamento terminou e mascarou campos.
A reabertura e uma repetição controlada atingiram o limite do acionador simples:
**30,561 s e 30,454 s**, conforme a tela de Execuções do projeto copiado.
Os campos continuaram como `—`, enquanto os pontos permaneciam guardados.
Isso é uma falha de recuperação, separada do aviso corrigido no item 1.

O fluxo usava a cópia com 36 cartões pessoais de teste preenchidos. A comparação
da reabertura teve 57 divergências, decorrentes dos campos não recuperados;
não são 57 defeitos aritméticos distintos. Alterar uma Família pela API não
dispara `onEdit`; por isso, a primeira mudança pela API não foi aceita como
prova da recuperação. As duas execuções reais com tempo limite e a releitura
posterior são a evidência deste item. Não foi isolado o custo de cada operação
da rotina nem preparada uma correção de desempenho nesta entrega. Não se
generalizam esses tempos para Android ou para todas as edições.

**3. Havia uma colisão de ID na ferramenta antiga de QA.**
`gerar_nativo.py` reservava 53018005 para `DADOS_R53_TESTES`, mas esse ID agora
pertence à R53_EVENTOS. Aplicar os pedidos antigos numa cópia atual poderia
sobrescrever a aba de eventos. O catálogo de ensaio passou para 53018901,
ausente nas duas cópias atuais. A ferramenta antiga não foi aplicada neste
ensaio. Ainda é necessário conferir metadados e criar as abas de QA apropriadas
antes de usar seus pedidos; alterar a constante não autoriza aplicar em produção.

O conferidor antigo de Morrendo **não estava desatualizado**: seu cenário
configura deliberadamente frações e teto diferentes em `regressao-campanha.py`.
Suas expectativas foram preservadas, com um comentário explicativo. Os casos
novos abaixo verificam separadamente os valores padrão do livro.

## Cobertura nativa

Oráculos aritméticos escritos a partir de `referencias-r53/LIVRO-COMPLETO.md`;
não se usou o próprio avaliador do produto para calcular esses resultados.
As matrizes alteram entradas reais dos cartões e preparam versões ocultas;
não substituem fórmulas calculadas por uma segunda implementação.

| Bateria | Cenários | Verificações aprovadas |
|---|---:|---:|
| Dano, cura, PV temporários, cura coletiva e mescla, Classes 1–7, Era | 35 | 315 |
| Mesma matriz, Ciclo | 35 | 315 |
| Toque com/sem Melhoria, pessoal, coletivo e montagens inválidas, Era | 36 | 315 |
| Famílias Livres: desconto sem reduzir base/Forma nem redistribuir saldo | 36 | 315 |
| Morrendo: arredondamentos, exemplos 23/93/395, Sequelas e extras | 9 | 54 |
| 12 grupos de entidade: especiais Classes 1–7 e básicas | 108 | 720 |
| Ampliação: mudar/restaurar Forma, função, compra e versão preparada | 5 | 10 |
| Vida, PE e Classe máxima nos seis Caminhos, níveis 2 e 30 | 12 | 36 |
| **Total antes dos reensaios do delta** | **276** | **2.080** |

Depois do delta, as 35 montagens pessoais e os 108 casos de entidade da cópia
do Ciclo foram relidos: **1.035 verificações adicionais aprovadas**. São
repetições de cenários, não 143 situações inéditas. A recuperação de Amparo
reprovada acima permanece fora dos totais aprovados.

Entre os casos negativos conferidos estão orçamento negativo, distribuição
acima do saldo, números fracionários/negativos, compras repetidas, Toque com
Longe, teto coletivo compartilhado e Melhoria Média em básica de Classe 0.
O alerta de mudança de compras na Ampliação continua ativo. Nenhum aviso
legítimo foi removido para tornar a ficha verde.

A cura individual paga a base Média além dos pontos de cura. PV temporários
individuais pagam Leve; coletivos pagam Média mais a Forma. As mesclas dividem
o saldo. Um desconto libera saldo, mas não aumenta automaticamente os pontos
já destinados à cura. Nas entidades, o orçamento menor e as básicas em d6
seguem suas tabelas próprias. Os 12 grupos foram fixtures aritméticas isoladas:
isso não aprova adquirir ou manter 12 entidades num personagem.

Na comparação antes/depois dos diagnósticos da Era foram normalizadas células
vazias omitidas pela API: **45.225 posições comparadas**, sem mudanças fora
de FX/FY/GA e sem erros de cálculo retornados. Isto mede preservação de valores,
não constitui 45.225 testes independentes de regras.

## Fonte, transporte e entrega incremental

Fontes GS regeneradas com `--somente-gs`, geração **8c38acf72c7e6a33**.
Geração limitada a 1.800 MB, pico observado de 595.108 KiB, sem swap no processo.
O pacote integral regenerado é artefato do repositório; **não foi instalado**
nas cópias, nas oficiais ou em ficha preenchida.

Validação local: **52 testes Python**, **89 casos do motor**, **584 verificações
do editor** e smoke do transporte/pacote/regressões aprovados. Os oito testes
focais finais cobrem guardas, reversão, repetição, normalização regional e
preservação de false/zero/erros nos recibos. Esses números são separados da
conferência nativa e não demonstram que o fluxo de Amparo com tempo limite passou.

`r53/diagnosticos_funcoes.py` prepara somente GA e reversão exata, offline.
Exige snapshot atual de **A:M e GA** da DADOS_R53 e o modelo correspondente
à base instalada. Confere os 249 IDs, as fórmulas de nome/Classe/entradas
efetivas e o diagnóstico anterior; recusa layouts divergentes e leituras
incompletas. Assim, manter um ID com uma entrada deslocada não basta para
autorizar o delta. A equivalência aceita separadores regionais, aspas
dispensáveis e a redução nativa de `B1683:B1683` para `B1683`; intervalos reais
continuam sendo intervalos.

Ensaio da migração na cópia do Ciclo: 244 escritas iniciais, repetição zero;
três diagnósticos (comum, Máxima e entidade) revertidos, relidos e reaplicados
com as guardas finais; nova preparação com **zero pedidos e 249 atualizadas**.
As guardas precisam ser relidas imediatamente antes de aplicar: um plano
offline não trava a API contra edições concorrentes.

Para uma ficha existente, o procedimento é: autorização para o alvo, snapshot
nativo completo novo, confirmação da base/layout/código atual, ensaio numa
cópia, preparação guardada, aplicação somente de GA e releitura. Nunca executar
`construir()`/`continuar()` nem instalar o pacote inteiro por causa deste delta.
O módulo otimizado arquivado das oficiais não contém DADOS_R53/MONTAGENS; se
essa base permanecer instalada, não há molde dessas abas para corrigir nele.
Outras versões precisam de conferência específica antes de qualquer aplicação.
O delta de GA não corrige o tempo limite de recuperação do item 2.

Evidências completas, snapshots, cópias e capturas permanecem na pasta privada
ignorada `nuvem-b47/saidas/revisao-mecanicas-20261030/`. Não foram versionados
dados pessoais, credenciais ou snapshots. As duas cópias de QA foram movidas
para a lixeira recuperável após os ensaios;
os backups nativos da aplicação anterior da PR44 não pertencem a este descarte.

## Limites e próxima manutenção

O ensaio cobre as combinações e os limites descritos, além das regressões
locais do projeto; não prova todas as situações de jogo, adjudicações em prosa,
ações de todas as Trilhas ou custos pagos durante uma sessão. Gravar entradas
pela API não valida automações de Caminho, armas, salários ou persistência por
evento. As regressões locais dessas rotinas não foram chamadas de testes nativos.
Carteira viva/PR31, a ficha do jogador e experimentos de cores ficaram fora.

Pendência prioritária identificada: corrigir e ensaiar a recuperação de Amparo
com cartões preenchidos e prazo do acionador simples. O diagnóstico incremental
pode ser revisado separadamente; esta revisão **não certifica a ficha como 100%
livre de erros** nem libera promoção automática.
