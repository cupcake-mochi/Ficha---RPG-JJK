# Prompts de retomada — Ciclo Maldito B47

O antigo prompt único foi substituído pela divisão em três chats. Leia o [plano paralelo](PLANO-PARALELO-B47.md) junto do [plano principal e fila](PLANO-RETOMADA-B47.md).

| Chat | Prompt completo | Modelo e esforço recomendados |
|---|---|---|
| 1 — Codex/Work: implementador e integrador | [01-integrador](prompts-b47/01-integrador.md) | GPT-6.1 Sol · High |
| 2 — Claude Code na nuvem: revisor independente | [02-revisor-claude](prompts-b47/02-revisor-claude.md) | Opus 5.5 · High, se disponível |
| 3 — outro Codex/Work: infraestrutura | [03-infraestrutura](prompts-b47/03-infraestrutura.md) | GPT-6.1 Sol · Medium |

Pode iniciar os três simultaneamente com acesso ao repositório e ramos próprios da mesma base. Só o chat 1 integra no ramo `codex/configuracao-b47` e escreve na cópia nativa de revisão. `main` e ficha oficial continuam fora da autorização. Se a plataforma criar outro nome de ramo, informar esse nome ao integrador.

Os prompts autorizam publicação nos ramos de tarefa e integração delimitada, pedem evidências e exigem recomendação de modelo/esforço em cada checkpoint. Cole o bloco integral de cada arquivo no chat correspondente. A configuração do modelo é escolhida pelo usuário no seletor da plataforma; o prompt não a altera.

Compartilhe o link do commit e relatório de cada frente com o integrador. Os chats não presumem mensagens ou memória compartilhada. Falta de acesso ao Google na nuvem deve ser registrada, sem impedir o trabalho independente de código/testes.
