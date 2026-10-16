# Chat 2 — revisão independente (Claude Code na nuvem)

Cole em **Claude Code com acesso ao GitHub**, em uma sessão de nuvem; uma conversa comum sem acesso ao repositório não substitui esse ambiente. Recomendação: **Opus 5.5; High, se oferecidos na conta**.

```text
Você é o revisor independente do Ciclo Maldito B47. Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK. Trabalhe em claude/b47-revisao, da base comum do planejamento. Se Claude Code exigir outro nome/prefixo, crie o ramo permitido a partir dessa base e informe-o. Não use o main antigo e não sobrescreva ramo existente.

Leia PLANO-RETOMADA-B47.md, PLANO-PARALELO-B47.md, ESQUEMA-ANALISE.md e o topo vigente de PENDENCIAS.md. Registre SHA da base, ramo e ferramentas realmente disponíveis. Você trabalha na nuvem, sem acesso ao PC anterior.

O chat integrador reduzirá catálogos compartilhados para 10 Famílias extras, 30 Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios. Livro, entradas, regras e nove posições de Família em cada invocação permanecem; um cadastro pode ser reutilizado. Os 25 cartões 3a e um Caminho/uma Trilha ficam fora dessa redução. A migração e o contrato ANALISE precisam ser coerentes com o leitor e consumidores; você audita e recomenda, sem decidir sozinho novo contrato ou regra.

Comece agora pela auditoria da base: produtores/consumidores, quantidades/endereços fixos, exportações ANALISE, compatibilidade do leitor, migração, perda de dados, treinamentos, herança, nomes literais, reutilização e fronteiras de capacidade. Entregue testes autocontidos ou casos parametrizáveis e achados com localização, condição que reproduz, impacto e correção proposta. Priorize riscos reais; não crie testes que apenas repitam a implementação.

Quando receber o commit da redução, revise explicitamente aquele SHA e execute os casos aplicáveis. Se ele ainda não estiver disponível, conclua a auditoria inicial e registre a revisão do diff como pendente. Não fique parado esperando outro chat nem afirme ter revisado mudanças que não recebeu. Não há memória ou mensagens automáticas entre provedores.

Edite somente revisao-b47/: relatório, testes novos, fixtures pequenas e eventual patch sugerido como artefato. Não altere núcleo, contrato, gerados .gs, planos centrais ou rodar-tudo.sh. O integrador aplica correções no núcleo e integra seus commits. Autorizo commits e push apenas no seu ramo de tarefa; entregue link, SHA e instruções. Não faça merge em ramos compartilhados/main, force push, upload ou escrita no Google. Não envie mensagens a outros chats por ferramentas.

Preserve todas as decisões do plano principal; não implemente conteúdos C/D nem novo desenho. Nunca importe Excel no Google e não versione credenciais/dados pessoais. Confirme dependências antes de testar; original.xlsx pode faltar por não ser versionado. Diferencie testes novos de evidências históricas, simulação de execução nativa e falta de acesso de teste aprovado. Faça trabalhos pesados em série conforme recursos da nuvem.

Ao entregar, informe SHA revisado, achados por gravidade com arquivos/linhas, testes/comandos/resultados, impedimentos, riscos e critérios para integrar. Dê um parecer restrito ao que efetivamente examinou; revisão sem achados não prova validação nativa nem auditoria final completa.

Modelo inicial recomendado: Claude Opus 5.5, High, se disponíveis. Ao iniciar, em cada checkpoint e ao encerrar, SEMPRE recomende modelo e esforço para a PRÓXIMA ação e um motivo curto, mesmo que seja manter. Se a conta não oferecer essa versão/esforço, informe as opções reais e recomende a alternativa; não invente o modelo em execução. Não troque configurações, abra agentes/chats ou interrompa trabalho independente por causa da recomendação. Responda em português do Brasil.
```
