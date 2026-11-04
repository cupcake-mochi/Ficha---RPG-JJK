# Correção da vida do Quebradiço e de Bloquear — PR53

Implementação no ramo `codex/auditoria-vida-corporal-20261104`, sobre PR52.
Substitui as pendências de implementação do relatório de auditoria ao lado.
Somente cópia descartável foi alterada. Sem merge, oficiais, jogador ou PR31.

## Comportamento

- FICHA!J26 aplica metade da vida normal ao Corpo Quebradiço com base corporal
  válida (DADOS_CUSTOM!B126), arredondando para baixo e com mínimo 1. Abrange
  aumentos de nível, Buff/Debuff e ajustes `somar`. Campos vazios e erros da
  conta-base são preservados; outros corpos não recebem essa redução.
- `trocar por` continua fixando o **valor final**, inclusive zero, conforme o
  contrato explícito já documentado em configuracao.py. É uma intervenção
  deliberada do mestre, não um aumento normal. Não há dupla redução.
- FICHA!Z56 mostra `Não pode bloquear` para Debilitado, Quebradiço e Exaurido
  com base corporal válida. Outros personagens conservam a fórmula anterior.
  Intermediários e suas fórmulas não foram alterados.

A implementação usa o índice de marcante e o rótulo BLOQUEAR para localizar
as caixas. Não há substituição global de coordenadas. `anterior()` reconhece
somente o envoltório exato da vida, exigindo duas contas-base idênticas.

GS regenerado sob limite de memória: geração `67df913e304304ad`.
Comparação integral das 26 abas-fonte contra a base, ignorando apenas selos
`geracao`: **somente FICHA!J26 e FICHA!Z56 mudaram**. ANALISE inteira, dados,
validações, notas e demais fórmulas iguais; 249 contextos preservados.
O XLSX intermediário do gerador não foi importado nem incluído na entrega.

## Validação

- `vida_bloquear_corporal.py --pedidos /tmp/pr53-testes.json`: estrutura e
  preparação de **21 cenários**, todos recalculados e aprovados no Google.
  Fórmulas extraídas do GS; na tabela de ensaio apenas a conta-base e as
  referências de entrada são controladas. Inclui pares/ímpares, mínimo 1,
  zero/negativo, vazio, erro intencional NA, outros corpos, base falsa,
  trocar por 30/0 e permissão/impedimento de Bloquear.
- Seis cenários integrados na FICHA: Quebradiço nível 1 = 4 PV; nível 2 = 6;
  com Buff 3 e somar 6 = 11; Exaurido e Próprio com os mesmos bônus = 22;
  trocar por 30 = 30. Corpo Próprio manteve `2d10 + 4` em Bloquear.
- Com máximo 11, Aguentar/Insistir passaram a 3/4, corrigindo a propagação
  do máximo antigo sem alterar suas próprias fórmulas.
- Progressão por rolagem: CONFIGURAÇÃO F59=Sim e F101=3, nível 2, vida inicial
  8, Buff 3 e somar 6: vida normal 20 e máximo final **10**.
- Descanso longo em lugar propício acionado **pela interface**, nesse cenário:
  vida **1 → 10**, menu resetado e registro confirmando o resultado. A cópia
  já continha o incremento de descanso da PR51; não foi reinstalado.
- Restauração nativa: apagar J26 pela interface devolveu a fórmula corrigida
  e 11 PV; substituir Z56 por 999 devolveu a fórmula e `Não pode bloquear`.
  Fórmulas relidas integralmente iguais ao esperado, normalizando apenas
  aspas opcionais nos nomes das abas. Não houve reposição manual entre a
  edição e a conferência de cada alvo.
- Código da cópia recarregado e relido inteiro, idêntico ao proposto.
- `vida_bloquear_molde.js`: **19 verificações** de paridade com GS,
  idempotência, guarda de hash/âncora, preservação de outros incrementos e
  rejeição de divergência sem aplicar parcialmente os dois moldes.
- Pacote/runtime aprovado, 60 cenários locais de descanso e 123 verificações
  do pacote leve aprovados. `git diff --check` aprovado.

A tabela de ensaio controla B126; não repete a bateria de cartões custom da
PR51. O ensaio de progressão usa o Caminho publicado Vanguarda, não um cartão
novo de Caminho custom. Não houve medição Android nem pente-fino universal.
A cópia é QA parcial, não um novo modelo para distribuir aos jogadores.

## Incremento para futura promoção

Não instalar pacote integral nem reconstruir ficha existente. Exige aprovação
específica, novo snapshot da planilha e de todos os arquivos do projeto,
conferência de B126 da PR51 e ensaio sobre cópia atual do alvo.

1. Conferir as fórmulas atuais de J26/Z56 e a compatibilidade do carregador.
2. Preparar outro arquivo com `preparar_vida_bloquear_loader.js entrada.gs
   SHA256 saida.gs`. O preparador é offline, exige hash do snapshot, uma
   única âncora e ausência do delta; não escreve no Google.
3. O helper `vida_bloquear_molde.gs` valida os dois moldes antes de alterar
   qualquer um; aceita somente fórmula antiga exata ou nova já aplicada.
4. Na cópia, salvar o incremento do Codigo.gs e atualizar somente os valores
   de fórmula de J26/Z56, preservando formatação e metadados. Conferir a
   vida atual: a redução do máximo não autoriza apagar ou recalcular entradas
   preenchidas silenciosamente. A migração não altera D26.
5. Recarregar/reler o código, testar restauração e dependentes. Só então
   preparar a promoção autorizada com snapshot fresco de cada destino.

Snapshot do Codigo.gs da QA antes: `fb87d449f3e532894f246082369d797641a791ae77cf48b9207f9fc25ee747d2`.
Depois e relido: `a4c69dafe55ff33b269a340edbdca9cf02cdeeee3519935c8223c9fb7fd40b8f`.
Arquivos brutos, snapshots e captura permanecem fora do Git.

Revisão: Sol/Medium. Aplicação integrada: Sol/High, conforme AGENTS.md.
Nenhuma configuração do usuário foi alterada.
