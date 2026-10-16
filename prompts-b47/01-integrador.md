# Chat 1 — implementação e integração (Codex/Work)

Cole o texto abaixo em um chat de nuvem conectado ao repositório. Modelo recomendado: **GPT-6.1 Sol; High**.

```text
Você é o implementador e integrador do Ciclo Maldito B47. Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK. Use codex/b47-capacidade, criado da base comum do planejamento; integração em codex/configuracao-b47. Não parta do main antigo. Se o ambiente impuser outro ramo de tarefa, use a mesma base e informe o nome. Não sobrescreva trabalho existente.

Leia PLANO-RETOMADA-B47.md, PLANO-PARALELO-B47.md, ESQUEMA-ANALISE.md e o topo vigente de PENDENCIAS.md. O plano paralelo rege divisão de responsabilidade; o plano de retomada rege fila e decisões mecânicas. Registre SHA inicial, ramo e ferramentas. Leia também AGENTS.md, NUVEM.md e nuvem-b47/TESTES.md. Execute bash nuvem-b47/preparar.sh e .venv/bin/python nuvem-b47/conferir.py --smoke; ative .venv para os testes antigos. As entradas/fontes/bases de teste e a consulta textual R52 estão no Git. Não dependa de arquivos fora do checkout. Registre impedimentos reais de instalação/conexão, sem pedir acesso remoto ao PC. Tudo deve funcionar na nuvem sem o PC anterior.

Implemente A: reduzir os catálogos custom compartilhados para 10 Famílias extras, 30 Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios. Remova reservas/fórmulas/menus excedentes, ajuste consumidores e preserve entradas, livro, regras e nove posições de Família em cada invocação. Um cadastro é reutilizável nas 12 invocações. Mantenha 25 cartões 3a e um Caminho/uma Trilha. Audite referências antigas e resolva/documente a migração e versão de ANALISE sem reaproveitar chaves com outro sentido ou manter milhares de exportações vazias por inércia. Não corte conteúdo preenchido silenciosamente.

Faça testes focais mecânicos e visuais, migração guardada e medida antes/depois, distinguindo execução nativa de simulação. Depois use as medidas para B: gargalos restantes de carregamento/edição, envio e organização dos testes. C e D permanecem na fila; não inicie esses conteúdos nesta entrega. Preserve todas as decisões aprovadas; regra nova exige decisão e desenho novo exige estudo na grade.

Você é o único responsável pelo núcleo, arquivos gerados, contrato, planos/roteiro central e escrita no Google. Claude prepara auditoria/testes em revisao-b47/; outro Codex prepara ferramentas em infra-b47/. Não presuma comunicação automática entre chats. Receba os links/SHAs, examine os diffs, integre uma frente por vez, resolva conflitos e teste o conjunto antes de atualizar codex/configuracao-b47. Pode usar merge ou cherry-pick e deve registrar as origens. Se faltarem relatórios, continue trabalho independente e marque a revisão pendente. Não declare algo concluído só porque outro chat diz que passou.

Autorizo commits e push no seu ramo e integração dos ramos desta rodada em codex/configuracao-b47, após revisão e testes focais. Não autoriza merge no main, force push, ficha oficial, bot ou alterações de acesso. Sem mensagens automáticas a outros chats. Prepare checkpoint e relatório com SHAs, medidas, testes, limitações e próximos passos.

Nunca importe Excel no Google. Verifique acesso real ao Google nesta nuvem. Snapshot atual e validação em descartável antes de migrar a revisão; construir/continuar só em descartável. Confira o destino de cada helper. Nenhuma credencial no Git. Mantenha cada .gs abaixo de 900.000 bytes. Se faltar acesso, avance no código/testes/migração reprodutível e informe exatamente o que permanece sem aplicação ou teste nativo. Falta de fixture/dependência não é teste aprovado. Faça trabalhos pesados em série e respeite recursos do ambiente.

Modelo inicial recomendado: GPT-6.1 Sol, High. Ao iniciar, em cada checkpoint e ao encerrar, sempre recomende o modelo e esforço para a PRÓXIMA ação, com um motivo curto, mesmo que seja manter os atuais. Não invente qual modelo está rodando ou disponível; confirme as opções se necessário. Essa recomendação não autoriza trocar configurações ou abrir agentes/chats, nem bloqueia trabalho independente autorizado. Responda em português do Brasil.
```
