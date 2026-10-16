# B47 — três chats em paralelo

Plano aprovado para preparação em **16/10/2026**. Complementa [PLANO-RETOMADA-B47.md](PLANO-RETOMADA-B47.md): a rota continua A → B → C → D. Esta divisão organiza A+B; não inicia três frentes novas de conteúdo nem substitui os testes finais. A redução de capacidade ainda não foi aplicada.

## Chats, modelos e ramos

| Chat | Ambiente e recomendação inicial | Ramo próprio | Entrega |
|---|---|---|---|
| 1 — implementador e integrador | Codex/Work; GPT-6.1 Sol, High | `codex/b47-capacidade` | Redução, migração/ANALISE, medida e integração de A+B |
| 2 — revisor independente | Claude Code na nuvem; Opus 5.5, High, se disponível | `claude/b47-revisao` | Auditoria, riscos, testes isolados e revisão do commit reduzido |
| 3 — infraestrutura | Outro Codex/Work; GPT-6.1 Sol, Medium | `codex/b47-infra` | Ferramentas delimitadas de envio/conferência e execução focal de testes |

As recomendações são julgamentos para estas tarefas, não equivalências de desempenho entre fornecedores. Confirmar o seletor de cada conta: se o modelo ou esforço não existir, informar as opções reais e recomendar a alternativa, sem inventar disponibilidade. Referências: [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) e [modelos/esforço do Claude Code](https://code.claude.com/docs/en/model-config).

**Sempre recomendar modelo e esforço:** ao iniciar, em cada checkpoint e ao encerrar, cada chat deve indicar modelo, esforço e motivo para a próxima ação, mesmo quando recomendar manter os atuais. Não afirmar qual modelo está em execução sem conseguir verificar. A recomendação não autoriza trocar configurações, abrir agentes/chats nem interromper trabalho independente já autorizado.

## Base e publicação

- Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK.
- Integração: `codex/configuracao-b47`; o `main` está atrás e não é a base desta rodada.
- Base de código anterior à documentação: `84d8f8c`; planejamento portátil anterior: `f9d00b9`.
- Os três ramos desta rodada partem do mesmo commit que publica este plano. Registrar o SHA completo recebido no início. Não recriar um ramo existente nem sobrescrever trabalho remoto.
- O nome `claude/b47-revisao` é lógico: se a plataforma exigir outro prefixo/sufixo, usar o nome permitido, criado a partir da mesma base, e informar o nome completo. Vale o mesmo para ramos criados automaticamente no Work.
- Cada chat pode produzir commits e publicar apenas no seu ramo de tarefa, conforme a autorização do prompt colado pelo usuário. Não versionar credenciais, tokens, dados pessoais ou saídas temporárias volumosas.
- Só o chat 1 integra commits revisados em `codex/configuracao-b47`, resolve conflitos e testa a combinação. Não fazer force push. Merge em `main`, ficha oficial e alterações de acesso continuam dependentes de autorização específica.

Não há memória compartilhada presumida entre Claude e Codex. A troca é feita por commits, diffs e relatórios versionados; o usuário pode copiar o link do commit/relatório entre chats. Não usar ferramentas para enviar mensagens aos outros chats. Não declarar revisão de um commit que ainda não foi recebido.

## Limites de edição

| Área | Responsável |
|---|---|
| `ficha-v01/*`, `ficha/*`, `apps-script/*`, geração, capacidades e migração | Chat 1 |
| `ESQUEMA-ANALISE.md`, plano principal, `PENDENCIAS.md`, roteiro central e `rodar-tudo.sh` | Chat 1 |
| `revisao-b47/*`: auditoria e testes novos autocontidos | Chat 2 |
| `infra-b47/*`: ferramentas novas, testes próprios e instruções | Chat 3 |
| Cópia nativa de revisão e Apps Script vinculado | Somente chat 1, com acesso confirmado |

Chat 2 e chat 3 não regeneram nem publicam arquivos `.gs`, não editam arquivos compartilhados e não refatoram o gerador. Se precisarem de integração fora de sua pasta, descrevem o ajuste ou entregam um patch como artefato dentro da própria pasta para o chat 1 avaliar e aplicar. A revisão deve apontar também o local real do problema, não apenas um teste que reproduza o código.

Os três ambientes de nuvem têm checkouts separados, mas apontam para os mesmos documentos Google. Branch não isola uma planilha. Chat 2/3 usam código e fixtures locais; não executam upload ou escrita no Google. Teste de envio ao serviço fica com o integrador. Nunca transferir autenticação do PC ou gravar tokens no Git.

## Trabalho simultâneo e dependências

**Chat 1 — A:** reduzir catálogos compartilhados para 10 Famílias extras, 30 Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios. Remover estruturas excedentes; não apenas ocultar cartões. Preservar entradas, livro, regras e nove posições de Família em cada uma das 12 invocações. Manter os 25 cartões 3a e um Caminho/uma Trilha nesta primeira redução. Documentar a decisão de contrato ANALISE e testar migração, primeira/última vaga, reutilização e casos negativos. Medir antes/depois, separando simulação de dados nativos.

**Chat 2 — desde já:** mapear produtores e consumidores, endereços/quantidades fixos, riscos de perda e compatibilidade do leitor. Criar casos de teste que possam receber a nova capacidade como parâmetro, sem tomar o contrato futuro como decidido. Quando o commit A estiver disponível, revisar esse SHA, executar os casos aplicáveis e classificar falhas/limitações. Não redefinir sozinho contrato ou capacidade, nem bloquear a análise inicial esperando o commit futuro.

**Chat 3 — desde já:** inventariar testes/dependências; preparar executor focal separado e manifesto de `.gs` com nomes, tamanhos e hashes. Avaliar envio por mecanismo oficial do Apps Script, incluindo suporte real à verificação posterior e limitações de autenticação/salvamento. Criar modo local seguro que não envie nada por padrão; documentar comandos explícitos de envio e o destino exigido. Não implementar uma nova plataforma de deploy nem prometer eliminar consentimento do Google. Testar localmente sem credenciais; integração com o roteiro central será feita pelo chat 1.

**Depois de A:** chat 1 usa a medição para escolher os gargalos de B. Chat 3 oferece ferramentas, mas não faz em paralelo uma segunda otimização do núcleo. Chat 2 revisa a combinação final. C (conteúdos 3c restantes) e D (unificação/polimento/auditoria integral) continuam na fila do plano principal.

## Integração e evidências

1. Cada chat registra base, ramo e arquivos sob sua responsabilidade antes de editar. Verifica instruções do repositório e ferramentas realmente disponíveis.
2. Publica mudanças pequenas no próprio ramo e um relatório em sua pasta: objetivo; SHA testado; arquivos; comandos/resultados; testes impedidos; efeitos no Google; riscos; dependências; próxima ação/modelo/esforço.
3. O integrador verifica o diff e o SHA, integra uma frente por vez na sua área de trabalho e resolve conflitos. Pode incorporar commits com merge ou cherry-pick, registrando origem e evitando duplicação. Não executar comandos de migração enviados por outro chat sem conferir o destino e as guardas.
4. Executa testes focais adequados à combinação. Só então atualiza o ramo de integração `codex/configuracao-b47` e o checkpoint. Resultados antigos ou testes de outra base não equivalem a validar a integração.
5. Entrega A+B com revisão independente recebida ou explicitamente pendente, medidas e estado real de aplicação no Google. Falta de acesso nativo deixa validação/aplicação pendente; não autoriza declarar A+B concluída integralmente.

O integrador não presume que os outros chats terminaram: continua tarefas independentes, informa quais commits faltam e deixa o conjunto revisável. Não precisa ficar consultando branches repetidamente. O usuário pode fornecer os links ao final de cada frente.

## Regras comuns

Todas as decisões mecânicas do plano principal permanecem. Não alterar regra nem construir desenho novo sem a decisão/estudo correspondente. Checagens focais mecânicas e visuais acompanham mudanças; bateria completa e revisão de todas as telas ficam para D. Não adiar defeito conhecido introduzido pela mudança.

Nunca importar Excel no Google Sheets. Snapshot atual e validação em descartável precedem migração na revisão. `construir()`/`continuar()` somente em descartável, nunca revisão preenchida/oficial. Manter cada `.gs` abaixo de 900.000 bytes. Acesso ao Git não garante acesso ao Google; verificar conta, ferramentas e permissões no novo ambiente. Se faltar acesso, avançar nas partes locais e discriminar o que não foi aplicado/testado nativamente.

Conferir recursos da nuvem antes de geração pesada. Executar trabalhos pesados em série dentro de cada ambiente; a execução simultânea em ambientes separados não é o compartilhamento dos 15 GB do PC. `ficha-v01/original.xlsx` é ignorado e pode faltar; não declarar comparadores dependentes dele como aprovados. Não converter nem importar a ficha por Excel como contorno.

## Prompts para colar

- [Chat 1 — integrador](prompts-b47/01-integrador.md)
- [Chat 2 — Claude revisor](prompts-b47/02-revisor-claude.md)
- [Chat 3 — infraestrutura](prompts-b47/03-infraestrutura.md)

Esta publicação organiza e autoriza o fluxo descrito nos prompts quando forem usados. Não executa a redução, a migração, testes novos ou merges de implementação.
