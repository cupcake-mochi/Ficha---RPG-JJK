# Prompts de retomada — Ciclo Maldito B47 C+D

A+B estão concluídos em `dce00ab8a244f53218c978293d10c5c1894b1ef8`. A continuação foi planejada em **três chats no total**, conforme [PLANO-PARALELO-CD-B47.md](PLANO-PARALELO-CD-B47.md). Publicar estes textos não inicia C/D; usar o bloco integral de cada prompt autoriza a frente delimitada.

| Chat | Prompt completo para colar | Recomendação de planejamento |
|---|---|---|
| 1 — este chat Codex: comuns, integração, Google e D | [01-integrador C+D](prompts-b47/cd/01-integrador.md) | GPT-6.1 Sol · High |
| 2 — outro Codex: personagem e Formas | [02-personagem-codex](prompts-b47/cd/02-personagem-codex.md) | GPT-6.1 Sol · High |
| 3 — Claude: entidades e revisão cruzada | [03-entidades-claude](prompts-b47/cd/03-entidades-claude.md) | Confirmar modelo/esforço reais no seletor da conta |

Todos partem do commit que publica este plano em `codex/configuracao-b47`, registrando o SHA completo e preservando `dce00ab` como ancestral. O integrador pode continuar neste chat; os outros prompts são para dois chats separados conectados ao repositório. Não usar `main`, sobrescrever ramos existentes ou presumir memória compartilhada.

Preparação: [NUVEM.md](NUVEM.md) e `AGENTS.md`. Auxiliares editam apenas suas pastas e entregam patches para o núcleo; só o integrador gera GS, escreve no Google e atualiza a integração. O usuário compartilha links/SHAs; os prompts não autorizam mensagens automáticas nem abertura de outros chats/agentes. Oficial, bot, main, force push e acessos permanecem fora do escopo.

Estimativa provisória conjunta: **8–14h de trabalho ativo**, revista no primeiro checkpoint. Não é estimativa por chat nem promessa de prazo. C pode avançar em paralelo; integração e D dependem da combinação testada.

## Histórico de prompts A+B

Os textos abaixo e os arquivos antigos são preservados para rastreabilidade. Não usar essa divisão histórica para iniciar C+D.

O antigo prompt único foi substituído pela divisão em três chats. Leia o [plano paralelo](PLANO-PARALELO-B47.md) junto do [plano principal e fila](PLANO-RETOMADA-B47.md).

| Chat | Prompt completo | Modelo e esforço recomendados |
|---|---|---|
| 1 — Codex/Work: implementador e integrador | [01-integrador](prompts-b47/01-integrador.md) | GPT-6.1 Sol · High |
| 2 — Claude Code na nuvem: revisor independente | [02-revisor-claude](prompts-b47/02-revisor-claude.md) | Opus 5.5 · High, se disponível |
| 3 — outro Codex/Work: infraestrutura | [03-infraestrutura](prompts-b47/03-infraestrutura.md) | GPT-6.1 Sol · Medium |

Preparação comum: [NUVEM.md](NUVEM.md), `bash nuvem-b47/preparar.sh` e `.venv/bin/python nuvem-b47/conferir.py --smoke`. Os prompts completos já exigem essa verificação.

Pode iniciar os três simultaneamente com acesso ao repositório e ramos próprios da mesma base. Só o chat 1 integra no ramo `codex/configuracao-b47` e escreve na cópia nativa de revisão. `main` e ficha oficial continuam fora da autorização. Se a plataforma criar outro nome de ramo, informar esse nome ao integrador.

Os prompts autorizam publicação nos ramos de tarefa e integração delimitada, pedem evidências e exigem recomendação de modelo/esforço em cada checkpoint. Cole o bloco integral de cada arquivo no chat correspondente. A configuração do modelo é escolhida pelo usuário no seletor da plataforma; o prompt não a altera.

Compartilhe o link do commit e relatório de cada frente com o integrador. Os chats não presumem mensagens ou memória compartilhada. Falta de acesso ao Google na nuvem deve ser registrada, sem impedir o trabalho independente de código/testes.
