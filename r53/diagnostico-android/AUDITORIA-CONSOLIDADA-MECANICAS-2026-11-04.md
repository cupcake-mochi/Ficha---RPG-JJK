# Auditoria consolidada de mecânicas · 04/11/2026

A análise ampliada encontrou **dez achados mecânicos**, incluindo o da PR58,
e uma falha no teste histórico. Não são vinte bugs: as vinte divergências do
ensaio de eventos incluem a mesma causa repetida nas doze invocações.
Nenhum código de produção foi corrigido nesta entrega.

Base auditada: pilha PRs 51–58 e relatório inicial da PR59 `bf94e7e`.
Livro: R66, `cupcake-mochi/JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Os testes nativos usaram cópias descartáveis das candidatas integradas Era e
Ciclo. Isso não significa que as oficiais receberam a pilha nem certifica uma
versão futura do livro. Oficiais, jogador e PR31 não foram alterados; sem merge.

## Achados, um por um

| ID | Problema e reprodução mínima | Evidência | Prioridade sugerida |
|---|---|---|---|
| A00 | TEMP com máximo zero: PV=9/PE=6 temporários permanecem aceitos. | Sheets na PR58; helpers locais. | P2 |
| A01 | Integridade 13/26 indica estágio 2, mas deslocamento base 9 continua 9 m. Base 6 com Exaustão 2 dá 4,5 em vez de 3 m. Entidade 8/16 também conserva 9 m. | Repetido nas cópias Era e Ciclo. | P2 |
| A02 | Entidade com vida máxima 0 mantém Integridade máxima 1. O mínimo 1 só vale com vida máxima positiva. | Repetido nas duas cópias; controles positivos e Sem alma conformes. | P2, caso de fronteira |
| A03 | Colagem X13:Y13 com −5 na caixa ± e 7 na reserva de PE apaga ambos. A vida é descontada corretamente, mas o 7 é perdido. | Helper e cadeia completa do onEdit locais, sem exceções intermediárias. Controle X13 isolado preserva o 7. | P1, perda de entrada |
| A04 | Colagem AF26:AR26 deixa TEMP 15 com máximo 20; edição isolada AF26 limita a 10. | Helper e onEdit completo locais. | P2 |
| A05 | Resumo do estágio 3 não lembra a redução de Classe máxima; estágio 4 usa “Você não é mais você mesmo”, sem Inconsciente/Derrotado. | Fórmula e textos lidos no Sheets. Não é falha comprovada de SOCORRO. | P2, informação mecânica |
| A06 | Vigília válida, Lapidação 4, uma compra de uma disponível e Exaustão real 2: deslocamento fica 4,5 m em vez de 9 m. | Repetido nas duas cópias. Buff +4,5 não resolve, pois continua sujeito ao MIN da Exaustão. | P2 |
| A07 | Cada uma das 12 invocações aceita TEMP 15 com vida máxima 20, acima do teto 10. | OnEdit completo local em todos os redutores publicados. | P2 |
| A08 | Com vida/PE atuais e máximos zero, +5 na caixa ± produz 5, ultrapassando o máximo. | OnEdit completo local em PV e PE; mesma divergência no helper do atalho. | P2, caso de fronteira |
| A09 | Recursos 20/20, duas edições −5 e −3 antes da primeira execução: termina em 17, não 12. | OnEdit completo local em personagem e entidade; helper do atalho também perde a primeira entrada. Controles processados um de cada vez terminam em 12. | P1, perda de operação |

A03/A04/A07/A08/A09 **ainda não foram reproduzidos como eventos reais no Google**.
O navegador continuou retornando “Local browser use is disabled in Work settings”.
A simulação executa código real com serviços simulados; ela não mede a fila do
Google, concorrência entre servidores, latência Android nem frequência de ocorrência.
Não se atribuem os 19–20 segundos relatados pelo usuário a A09 sem medição.

### Causas e cuidados para a futura correção

- **A00:** `tetoTemp_` retorna o valor sem teto quando `max <= 0`.
- **A01/A06:** o deslocamento aplica carga e Exaustão marcada, mas não consulta
  Integridade nem Vigília. Não dividir tudo cegamente: usar o menor limite entre
  Integridade/Exaustão, respeitar restrições corporais e conferir ajustes de campanha.
  Buff/Debuff pode conter compensações manuais antigas; a migração não deve dobrá-las.
- **A02:** `ficha-v01/ficha_invocacoes.py` usa `MAX(1,INT(vida/2))` sem guarda positiva.
- **A03:** `redutorDaInvocacao_` lê a primeira célula, mas limpa `e.range` inteiro.
- **A04:** `prenderTemp_` exige igualdade literal do A1, em vez de identificar
  células atingidas no intervalo. O ensaio usa caixas completas, não meia mescla.
- **A07:** o caminho INVOCAÇÕES trata ±, mas não aplica o teto ao TEMP editado.
- **A08:** `aplicaPasso_` e `r53LivrePasso_` usam a verdade lógica de `max` para
  decidir se limitam o saldo. Zero passa a significar “sem limite”. É outro ponto
  de correção além do teto de temporários; não confundir os dois consumidores.
- **A09:** os consumidores leem o conteúdo atual da caixa, não o passo do evento.
  Na fila de dois eventos, o primeiro já encontra −3, consome e limpa; o segundo
  encontra vazio. Trocar somente por `e.value` não basta sem estudar consumo único,
  preservação de entrada nova e repetição de evento atrasado. Não criar acionadores
  como atalho para contornar o problema.

## Cobertura executada

| Domínio | Conferência realizada | Resultado e limite |
|---|---|---|
| Montagem, custos, cura/VT, condições, Máxima, Liberação, Formas e Famílias custom | Todos os 89 casos versionados recalculados em abas novas de QA nativa (16 + 73), além do avaliador local. | 89/89 conformes, inclusive rejeições esperadas. Testa o modelo, não cliques dos cartões. |
| Perícias | 23 perícias da FICHA real, sem treino, treinadas e especializadas com Buff +1; atributos 2/3/4/5/6 e Maestria 3. | 69/69 conformes. Comparação independente: atributo; atributo+3; atributo+3+1+1. Não usa a fórmula como oráculo. |
| Progressão e XP | `xp_nivel`, `xp_atualizar`. | 20.643 verificações/9.900 combinações e 87 verificações locais. |
| Caminhos, Trilhas e treino em armas | `caminho_corrida`, `caminho_integrado`. | 17 e 52 verificações locais, incluindo seis Caminhos, texto pessoal, troca concorrente de Trilha e treino de grupo. |
| Cartões, Classes e persistência | `cartoes_diretos_runtime`. | 584 verificações locais; 249 contextos. |
| Aptidões/Bênçãos/Talentos e custom | `test_motor`, `test_usos_ritual`, `ritual_loader`; Vigília nas duas cópias. | 50, 3 e 10 testes locais; o loader usa fixture, não módulo instalado. A06 confirmado no Sheets. |
| Descanso, cura e socorro | Suites focais da pilha já executadas nesta auditoria. | 66, 35 e 98 verificações locais conformes; não repetir autorizações/menus já ensaiados como se fossem novos. |
| Vida, Bloquear e deslocamento corporal | `vida_bloquear_molde`, `deslocamento_molde`. | 19 e 20 verificações de molde/incremento; não certificam todas as combinações de condições. |
| Missões e salários | `missoes_integradas`, `salario_lote`, `salario_lote_aba`. | 2.709, 95 e 49 verificações locais. Sem emitir salário nativo, alterar carteira ou PR31. |
| ANALISE e tipos | `test_origens_analise`, `test_contrato`, `test_intervalos_qualificados`, `test_integridade_tipos`. | 14, 7, 3 e 1 testes. Escape de apóstrofos, tipos e contrato preservados. |
| Referências do GS | Auditoria estática das 26 abas das fontes. | 70.801 fórmulas e 161.721 referências explícitas; nenhuma ocorrência retornada. Não resolve INDIRECT. |
| Erros nativos | Leitura de `effectiveValue.errorValue` de todas as 31 abas de cada candidata copiada, fora das abas auxiliares da auditoria. | 62 abas lidas, zero erros retornados. Ausência de #REF/#ERROR não garante correção de regra. |
| Recursos e eventos | 25 cenários com onEdit completo/atalho reais em ambiente local; 18 cenários nativos iniciais, cinco de Vigília, confirmação na segunda cópia. | 5 eventos locais conformes e 20 divergentes por causas listadas. O diagnóstico não é suíte verde. |

### Falhas e lacunas dos próprios testes

**B01 — `menu_origem.js` não acompanha a evolução da pilha.** O teste enumera os
arquivos Apps Script de hoje e tenta buscar todos no commit histórico
`93a109ce…`. `Socorro.gs` não existia nele, então a execução termina antes das
asserções. Isso não prova defeito no menu. O verificador focal
`menu_origem_molde.js` passou suas 19 verificações, incluindo paridade com as
duas fórmulas atuais. Não foi alterada a expectativa histórica para esconder a falha.

`cartas_custom.js` e `marcas_custom.js` saíram com código zero, mas escreveram
“sem a ficha exportada, pulado”. **São dois testes não executados**, não aprovações.
Dependem de fixture privada de um módulo antigo; não foram alimentados com uma
exportação diferente para fabricar resultado. Das 18 suítes ampliadas inicialmente
selecionadas, 15 passaram, duas foram puladas e uma falhou por B01.

## O que não foi tratado como defeito

- Vida/energia temporárias, condições e usos por dia têm partes explicitamente
  manuais; a rotina de descanso documenta isso em `Codigo.gs`.
- Dano de Alma exige registrar vida e Integridade. Uma caixa ± genérica não
  identifica o tipo do golpe; a falta dessa inferência não virou um bug novo.
- Cartões guardam montagens por Classe. Penalidade transitória não autoriza
  apagar compras ou versões preparadas. Custos/Classe em combate ainda pedem
  aplicação da regra; a omissão no resumo está delimitada em A05.
- Um menu aceitar estado incompatível não comprova, sozinho, que a automação
  concedeu esse estado. Imunidades de Origem e condições narrativas não receberam
  “validação automática aprovada” sem uma fonte estruturada e um cenário completo.
- Avisos de orçamento, Classe 0, Famílias e incompatibilidades foram conservados.
  Não foi removido “CE” nem modificada a correção do consumidor RPG---BOT.

## Preservação, revisão e próximo trabalho

Restaurados e relidos por igualdade de `userEnteredValue`: lotes de 15 e 5 campos
na Era, 10 e 75 no Ciclo. Há campos repetidos entre lotes; não somar como células
únicas. Fórmulas originais foram restauradas como fórmulas. A segunda varredura
nativa do Ciclo ocorreu após a restauração. Abas auxiliares de montagem permanecem
somente na descartável Era. Não executar construir/continuar nas cópias preenchidas.

Evidências completas e IDs: `nuvem-b47/saidas/auditoria-ampliada/`, ignorado.
Manifesto sanitizado: `AUDITORIA-CONSOLIDADA-MECANICAS-2026-11-04.json`.
Geradores/diagnósticos reproduzíveis: `auditoria_montagem_nativa.py`,
`auditoria_eventos_recursos.js` e `auditoria_onedit_recursos.js` em `r53/testes/`.
Os diagnósticos retornam JSON com divergências; exit zero significa execução
concluída, não aprovação de todas as regras.

A análise desta base está consolidada. **Não é certificação de ausência de todos
os bugs.** O bloqueio operacional restante é repetir colagens/fila como eventos
reais no Sheets quando o controle do navegador for habilitado. Correções e
aplicações são trabalho posterior, separado desta auditoria, começando por A09/A03.
Antes de promover qualquer correção: revisar, ensaiar no Google e obter backup
atual dos alvos autorizados. PR31 permanece em `765e3b24…`.

Recomendação conforme AGENTS: Sol/High para corrigir os eventos e integrar as
regras; Sol/Medium para revisão independente. Nenhuma configuração foi alterada.
