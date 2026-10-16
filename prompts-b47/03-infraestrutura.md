# Chat 3 — infraestrutura delimitada (outro Codex/Work)

Cole em outro chat de nuvem conectado ao repositório. Modelo recomendado: **GPT-6.1 Sol; Medium**.

```text
Você cuida da infraestrutura delimitada do Ciclo Maldito B47. Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK. Trabalhe em codex/b47-infra, criado da base comum do planejamento, não do main antigo. Se o ambiente exigir outro ramo de tarefa, use a mesma base e informe o nome. Não sobrescreva trabalho existente.

Leia PLANO-RETOMADA-B47.md, PLANO-PARALELO-B47.md, ESQUEMA-ANALISE.md e o topo vigente de PENDENCIAS.md. Registre SHA inicial, ramo e ferramentas disponíveis. Leia também AGENTS.md, NUVEM.md e nuvem-b47/TESTES.md. Execute bash nuvem-b47/preparar.sh e .venv/bin/python nuvem-b47/conferir.py --smoke; ative .venv para os testes antigos. As entradas/fontes/bases de teste e a consulta textual R52 estão no Git. Não dependa de arquivos fora do checkout. Registre impedimentos reais de instalação/conexão, sem pedir acesso remoto ao PC. O chat 1 implementa a redução de capacidade e integra; Claude audita o contrato/consumidores. Você pode começar agora sem esperar a redução, fazendo ferramentas independentes das quantidades atuais.

O bootstrap de nuvem já está implementado em nuvem-b47/; use-o e não duplique sua preparação. Sua entrega tem dois limites: (1) inventariar testes/dependências e criar executor focal separado que rode os testes selecionados, registre comandos/exit codes, distinga executado/impedido/falhou e evite repetir geração pesada sem necessidade; (2) preparar manifesto dos .gs com nomes/tamanhos/hashes e avaliar envio por mecanismo oficial do Apps Script, incluindo destino explícito, persistência, leitura posterior e limitações reais de autenticação/salvamento. Teto por .gs: 900.000 bytes. Não implemente uma nova plataforma de deploy.

As ferramentas não enviam nada por padrão. Teste localmente com fixtures pequenas e sem credenciais; documente os comandos de envio e o que exige autorização humana/serviço disponível. Só o integrador executará upload ou escrita no Google. Não prometa contornar consentimento nem presuma acesso ao Google por ter acesso ao Git. Não transfira tokens do PC, não versione segredos e não use endpoints não documentados.

Edite somente infra-b47/: ferramentas novas, testes próprios, instruções e relatório. Não edite núcleo, contratos, apps-script, arquivos gerados, planos centrais ou rodar-tudo.sh. Se precisar integrar o executor ao roteiro central, entregue a alteração proposta ou patch dentro da sua pasta para o integrador aplicar. Não faça uma segunda otimização de carregamento do núcleo em paralelo: o integrador escolherá os gargalos após medir a redução.

Autorizo commits e push apenas no seu ramo de tarefa. Entregue links/SHAs, instruções de aplicação/reversão e comandos de teste. Não faça merge em ramos compartilhados/main, force push, alterações na ficha oficial/bot/acessos ou mensagens automáticas a outros chats. O integrador revisará e integrará os commits; não presuma comunicação ou memória compartilhada entre sessões.

Nunca importe Excel no Google. original.xlsx não está versionado; identifique comparadores impedidos. Respeite recursos da nuvem e execute trabalhos pesados em série no seu ambiente. Não declare simulação como teste nativo. Se o envio oficial exigir um acesso indisponível, documente a dependência e o caminho funcional e conclua as ferramentas locais; não deixe isso virar investigação sem limite. C/D permanecem na fila.

Modelo inicial recomendado: GPT-6.1 Sol, Medium. Ao iniciar, em cada checkpoint e ao encerrar, SEMPRE recomende modelo e esforço para a PRÓXIMA ação, com um motivo curto, mesmo que seja manter. Suba a recomendação para High somente se uma dificuldade concreta justificar. Não invente o modelo em execução ou disponibilidade; não troque configurações, abra agentes/chats ou bloqueie trabalho independente autorizado por causa da recomendação. Responda em português do Brasil.
```
