# Descanso — evento antigo após o reset do menu

Correção adicional da PR51, sobre `5ad0d5969624b56b8584c6834ac8b22962d48ad1`.
Somente cópia descartável de QA recebeu código e entradas. Oficiais, jogador e PR31 não foram alterados. Não houve merge, novos acionadores nem ampliação de acesso.

## Defeito confirmado no Google

O uso de `e.value` eliminou uma leitura cara, mas passou a aceitar uma escolha antiga mesmo quando `FICHA!D45` já dizia `Escolha o descanso`.

Ensaio em Google Sheets nativo com o projeto vinculado à cópia. A rotina `descansar_` da PR51 foi instalada incrementalmente no módulo leve. Um helper exclusivo de QA, com guarda do ID da cópia, expôs essa mesma função para reapresentar o evento em execuções separadas do editor. Não foi usada uma reimplementação da conta.

Cenário: Origem corporal publicada, Corpo Exaurido, Recuperação Abundante, máximo de 10 PE e saldo inicial de 1 PE. O helper prepara o menu e chama `descansar_({range: menu, value: 'Curto · lugar propício'}, idx)`.

| Ensaio nativo | Resultado |
| --- | --- |
| Antes da guarda, primeiro evento | 1 → 5 PE, menu voltou ao convite |
| Antes da guarda, reapresentação sem nova escolha | **5 → 9 PE indevidamente**, retornou `true` |
| Depois da guarda, evento antigo com saldo 9 | 9 → 9 PE, retornou `false` |
| Depois da guarda, evento sem `value`, preparado em 1 PE | 1 → 5 PE, retornou `true`, menu voltou ao convite |
| Depois da guarda, reapresentação em 5 PE | **5 → 5 PE**, retornou `false` |
| Depois da guarda, nova escolha digitada no menu real da ficha | 5 → 9 PE, registro correto e menu voltou ao convite |

As duas primeiras chamadas com `value` terminaram às 12:36:20 e 12:36:55 de 04/11/2026 (São Paulo). A rejeição corrigida em 5 PE terminou às 12:41:26. A última linha foi edição real da célula, atendida pelo acionador simples existente, sem chamar o helper.

**Limite da conclusão:** a reapresentação foi provocada pelo ensaio. Isso confirma a vulnerabilidade da rotina no ambiente Google, mas não demonstra entrega espontânea duplicada pelo Google. O evento sem `value` foi construído no helper, não uma colagem real. Este ajuste não implementa transação/identificador de evento nem resolve interrupção entre escritas, execuções simultâneas ou repetição intencional após falha parcial.

## Correção

A célula `descanso` passa a integrar o mapa da leitura em lote já existente. Antes de calcular ou escrever, a rotina compara seu valor atual com a escolha do evento. Se o menu voltou ao convite ou passou a outra opção, retorna `false`, preservando recursos, registro e escolha atual.

Não acrescenta chamada ao Google nem amplia o retângulo lido. Preserva `e.value` e o caminho de reserva com `getValue`. Um novo descanso intencional do mesmo tipo continua permitido.

Atualizados `apps-script/Codigo.gs`, dois remendos incrementais em `pacote_leve_remendos.json` e os testes de descanso. A geração dos moldes continua `dc166800f8d86789`, pois não houve alteração de fórmulas ou catálogos.

## Validação

- `node r53/testes/descanso.js`: 60 cenários aprovados. Inclui os quatro tipos após reset, escolha mais recente, nova escolha intencional, leitura de reserva, recursos/registro/avisos preservados e uma única leitura no mesmo retângulo.
- `node r53/testes/pacote_leve.js`: 123 verificações aprovadas, incluindo aplicação e reversão dos remendos por âncoras.
- `python3 r53/empacotar_script.py`: pacote regenerado, fonte SHA-256 `192277965ce84be947056090209f477403cc50199ebd654b1aef5f00d9ac09f2`.
- `node r53/testes/pacote_runtime.js`: transporte aprovado no pacote regenerado, 26 abas de molde e 249 contextos preservados.
- Código da QA salvo, editor recarregado e 1.004.782 caracteres relidos integralmente iguais à proposta com helpers. Helpers não entram na fonte de produção nem na entrega incremental.
- Conferência visual do menu, registro e capacidades na cópia. Nenhuma mudança de formato ou layout.

As capturas e cópias integrais do script estão fora do Git, na pasta privada de análise desta sessão. Apenas este relatório sanitizado é versionado.

## Aplicação futura

Não instalar o pacote integral em ficha existente. Para uma ficha já com a PR51 anterior, os dois novos pares do fim de `pacote_leve_remendos.json` descrevem o delta exato. Para uma oficial que ainda não recebeu a PR51, reunir também os demais incrementos da PR, após novo snapshot, identificação do código instalado e ensaio em cópia. Conferir âncoras e código salvo, sem reconstruir a ficha.

Este ensaio usou Origem publicada. Os casos custom continuam cobertos pela bateria local e pela QA anterior da PR51, não foram repetidos no Google nesta revisão focal.

Modelo/esforço recomendado pelo AGENTS.md: Sol/Medium para revisar esta entrega, High para futura aplicação integrada. Nenhuma configuração foi alterada.
