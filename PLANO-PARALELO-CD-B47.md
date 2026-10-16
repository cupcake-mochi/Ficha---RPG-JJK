# B47 — divisão de C+D entre três chats

Planejamento aprovado para publicação em 16/10/2026. São **três chats no total**, contando o integrador atual: um integrador Codex, outro Codex para personagem e Claude para entidades. A publicação deste plano não inicia a implementação. Cada frente começa quando o usuário usar seu prompt; não abrir chats/agentes nem enviar mensagens automaticamente.

## Base e estado recebido

- Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK.
- A+B estão concluídos e publicados em `dce00ab8a244f53218c978293d10c5c1894b1ef8`, ancestral obrigatório desta rodada. Não repetir a redução, os 102 lotes antigos ou a migração já encerrada.
- Integração: `codex/configuracao-b47`. `main` não é a base.
- Base comum da preparação: o commit que publica este arquivo e os três prompts, nos ramos `codex/b47-capacidade` e `codex/configuracao-b47`. Resolver o SHA completo no início e registrá-lo. Se a integração avançou, conferir o histórico e as mudanças antes de escolher a base; não presumir que todos partiram do mesmo SHA.
- Estado nativo comprovado de A+B: ANALISE 10, 7.356 chaves, 509 entradas/notas preservadas, zero erros/divergências em 400.917 células de 17 abas e 20 GS mais manifesto relidos iguais. Provas em `capacidade-b47/RETOMADA-PC.md`, `VALIDACAO-NATIVA-PC.json` e `REVISAO-NATIVA-PC.json`.
- O topo de `PENDENCIAS.md` informa o estado recebido. A seção C/D e as decisões de `PLANO-RETOMADA-B47.md` regem conteúdo e mecânica. Este plano rege os novos papéis e substitui, para C+D, a divisão histórica de A+B em `PLANO-PARALELO-B47.md`.

## Responsabilidades e ramos

| Chat | Trabalho | Ramo de tarefa | Área de edição direta |
|---|---|---|---|
| 1 — integrador Codex, este chat | Tipos de dano, Condições, contratos comuns, integração, Google e D | `codex/b47-capacidade` | Núcleo, documentação central e arquivos gerados; `conteudos-b47/comum/` |
| 2 — outro Codex | Formas, Aptidões/Bênçãos e Talentos do personagem | `codex/b47-cd-personagem` | `conteudos-b47/personagem/` |
| 3 — Claude | Tipos e Talentos de entidade; depois revisão da frente de personagem | `claude/b47-cd-entidades` | `revisao-b47/cd-entidades/` |

Os ramos novos são nomes propostos: criar somente ao executar o respectivo prompt. Se já existirem, examinar seu estado e preservar trabalho. Se a plataforma exigir outro nome, manter a base e informar o nome real. Não resetar checkouts nem reescrever história. Não reutilizar automaticamente os ramos antigos de revisão/infraestrutura de A+B.

Cada frente entrega código de verdade em módulos isolados, fixtures e testes em sua pasta. Alterações necessárias fora dela são entregues como patches revisáveis dentro da própria pasta, indicando base, arquivo-alvo e ordem de aplicação. O integrador adapta/incorpora os módulos na fonte canônica e aplica os patches após revisão. Código em uma pasta de entrega e teste isolado não comprovam integração de produção.

Somente o integrador altera diretamente `ficha-v01/`, `ficha/`, `apps-script/`, `ler-analise.py`, `ESQUEMA-ANALISE.md`, testes centrais, planos, `PENDENCIAS.md` e roteiro geral. Não há duas frentes regenerando ou publicando os mesmos `.gs`. Somente o integrador atualiza `codex/configuracao-b47` e escreve no Google.

## Contrato inicial e trabalho que pode começar junto

O integrador prepara um contrato versionado em `conteudos-b47/comum/` com:

1. Campos e tipos, valores vazios, herança da base opcional e criação sem base.
2. Capacidades pequenas e compartilhadas para os tipos novos, justificadas pelos consumidores e custo. As quantidades 10/30/30/10/10 de A+B não se aplicam automaticamente a eles. Não multiplicar catálogo por todas as posições de uso nem criar centenas de cartões por inércia.
3. Interface dos módulos: entradas/saídas, registros e validações; destino dos campos no desenho aprovado e referências derivadas das capacidades.
4. Propostas de endereços/namespaces de exportação e compatibilidade com ANALISE 10. Só o integrador fecha o contrato e eventual nova versão; nunca reutilizar chave com outro sentido.
5. Regras para catálogo do livro + custom, nomes literais, duplicatas e referências entre os conteúdos das frentes.

As outras frentes não ficam paradas esperando isso: leem os estudos, inventariam produtores/consumidores, identificam exceções do livro e preparam casos mecânicos e módulos sem endereços globais fixos. Registram suas propostas na própria pasta. O integrador concilia as propostas no contrato comum; divergência de contrato é resolvida antes de ligar o módulo à produção. Decisão rotineira de implementação segue as regras aprovadas; regra nova ou ampliação de escopo exige decisão do usuário.

## Escopo do chat 2 — personagem e Formas

- **Formas:** base opcional, Família, Peso, resolução, resultado, TR, Classe 0, restrição embutida, efeito/requisitos e alcance/área. Separar alcance de tamanho da área. Embora esta frente se chame personagem, Formas também precisam funcionar nas aplicações das entidades, respeitando suas faixas próprias; não deixar esse consumidor para uma frente sem responsável.
- **Aptidões/Bênçãos:** base opcional; consumo de escolha ou gratuidade explícita. Categoria de Efeito vazia não concede gratuidade.
- **Talentos do personagem:** cadastro, base opcional, requisitos, custos e efeitos nos cartões/lugares já existentes.
- Em cada grupo: menus do livro e custom válido, cálculos, avisos, proposta de exportação, roteiro nativo e testes focais. Preservar heranças/exceções existentes; não executar descrições como regras.
- Provar primeira/última vaga, cadastro inválido, duplicatas, nomes com `*`, `?`, `~`, base e ausência de base, reutilização e limpeza. Testar Formas nos contextos de personagem e entidade.

## Escopo do chat 3 — entidades e revisão cruzada

- **Tipos de entidade:** base opcional. Criação do zero pode combinar separadamente os funcionamentos existentes de vida, talismã e reserva de PE. Autonomia e alma são escolhidas na própria invocação; não criar configuração global nem conceder benefícios de uma base não escolhida.
- **Talentos de entidade:** cadastro, orçamento, requisitos, custos/efeitos e integração com os cartões atuais.
- Preservar as 12 invocações, nove posições de Família por invocação, limites e autonomia individual; um cadastro pode ser reutilizado em várias invocações.
- Entregar módulos, patches para consumidores/menus/ANALISE, testes focais e roteiro nativo na área `revisao-b47/cd-entidades/`. Não editar diretamente o núcleo nem os módulos da outra frente.
- Depois de receber um SHA real de personagem pelo usuário ou Git, revisar esse SHA e registrar achados por gravidade com arquivo/local e caso reproduzível. Distinguir revisão cruzada do próprio trabalho: o integrador revisa a entrega de entidades. Não aguardar personagem para avançar a implementação própria.

## Escopo do integrador e etapa D

O integrador fecha contratos, implementa **Tipos de dano** unidos ao livro e menus consumidores e **Condições** como opções de Melhoria, conforme o estudo aprovado. Não criar um segundo mecanismo de Condições nem interpretar prosa como automação. Cruza o inventário real de menus para não omitir consumidores nem transformar menções históricas em escopo novo.

Recebe commits e relatórios, verifica base/diff, incorpora uma frente por vez e testa a combinação. Se uma entrega ainda não chegou, continua tarefas independentes e informa a dependência; não presume conclusão nem declara revisão recebida sem ter lido o SHA. Pode usar merge ou cherry-pick, evitando duplicar commits e registrando origem e resultado.

Depois de C integrada:

- Reunir edição em CONFIGURAÇÃO, com tabelas para registros simples e cartões para tipos complexos, preservando o desenho aprovado e a referência Forma B. Apresentar estudo enxuto na grade antes de construir mudança de desenho que ainda precise de aprovação; não reabrir aprovação dos moldes já aprovados sem mudança concreta.
- Priorizar campos editáveis e rótulos claros. Ajuda contextual em notas; inventário, orçamento, relatórios e demonstrações ficam na documentação.
- Auditar dependências antes de retirar estudos/exemplos. Preservar escolhas/resultados nas fichas e invocações originais.
- Executar bateria final e casos de interação; revisar carteira/foto/paleta, bordas, dimensões, textos longos/limpeza, menus, grupo 7 e áreas recolhidas.
- Auditar ANALISE inteira e leitor, erros de fórmula, persistência dos GS/manifesto, gatilhos e cópia funcional sem ativação manual. Construir do zero somente em descartável, medir tempos/custos e restaurar dados temporários.
- Entregar versão revisável com provas, SHAs e pendências explícitas. Nova rodada exige provas do modelo/código novo: resultados de A+B são referência, não aprovação automática de C+D.

## Preparação e limites comuns

Ler `AGENTS.md`, `NUVEM.md`, `nuvem-b47/TESTES.md`, este plano, seção C/D e decisões do plano principal, `ESTUDO-CUSTOM-3C.md`, fontes em `mockup/` e `ESQUEMA-ANALISE.md`. Históricos com capacidades/formatos antigos não substituem o checkpoint vigente.

Em Linux: `bash nuvem-b47/preparar.sh` e `.venv/bin/python nuvem-b47/conferir.py --smoke`. Em Windows/Git Bash, seguir `NUVEM.md` e usar `.venv/Scripts/python.exe` no smoke. Reutilizar ambiente comprovadamente preparado e conferir o diagnóstico; não reinstalar por rotina. Registrar ferramentas/versões, ramo, SHA inicial e arquivos sob responsabilidade. Smoke não equivale à validação final.

Fazer testes mecânicos significativos durante C; testes visuais nativos ficam com o integrador. Limitações reais de Calc, `fcntl`, fixtures ou acesso são testes impedidos, nunca resultados verdes. Trabalho pesado em série por ambiente, respeitando memória. Frentes auxiliares não executam geração integral que regrave saídas canônicas; podem testar modelos/fixtures locais em sua pasta.

Nenhuma memória compartilhada presumida entre Claude e Codex. Troca por commits, diffs e relatórios no Git, com links fornecidos pelo usuário; leitura do Git é permitida. Não enviar mensagens automáticas, abrir outros chats/agentes nem acessar a sessão do PC de outro chat. Não gravar credenciais, dados pessoais, snapshots de jogador ou saídas volumosas no Git.

## Google e autorizações quando cada prompt for usado

Os prompts autorizam C+D dentro de seus papéis: commits/push no ramo de tarefa e, somente para o integrador, integração revisada/testada em `codex/configuracao-b47` e aplicação nativa guardada na cópia de revisão. Publicar este planejamento não executa essas etapas.

- Revisão: `1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0`.
- Descartável de construção: `12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc`.
- Descartável migrada de A+B: `1hBogVNW0vqeLYwa0PNl04Y2Nel9-7nrCoODWq1FKsb4`; contém evidência anterior. Não sobrescrevê-la automaticamente; preparar uma cópia descartável para novos cenários destrutivos.
- Oficial somente leitura: `1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro`.

Confirmar ferramentas, conta e destino atuais. Snapshot e backup nativos novos, guardas e prova conjunta em descartável precedem nova migração pontual da revisão. Não repetir lotes antigos não idempotentes nem ignorar snapshot vencido/diferenças de conteúdo. `construir()`/`continuar()` nunca na revisão preenchida ou oficial. Salvar/reler código completo e manifesto; manter cada GS abaixo de 900.000 bytes. Não importar Excel no Google.

Sem merge em `main`, force push, ficha oficial, bot ou alterações de acesso. Bot/formato 10 e variante histórica 4 permanecem externos; mudanças de ANALISE exigem explicitar compatibilidade do leitor/consumidores, sem modificar o bot. Acesso Git não fornece acesso Google. Sem ferramenta nativa, avançar no trabalho local e discriminar a validação/aplicação pendente.

## Entrega de cada frente e sequência de integração

Cada frente publica na própria pasta um relatório com: objetivo/escopo; base e SHA testado; ramo; arquivos; módulos/patches e ordem de incorporação; contrato esperado; comandos e resultados; testes impedidos; efeitos no Google (nenhum para chats 2/3); riscos; dependências; próxima ação/modelo/esforço. O SHA final de publicação é informado na resposta, sem inventar autoidentificação do commit dentro dele.

1. Contrato comum e propostas das frentes, em paralelo com inventário/testes.
2. Entregas pequenas e utilizáveis de personagem e entidades, com testes próprios.
3. Integração incremental dos módulos/patches, revisão cruzada e testes das interações, incluindo Formas nas entidades e Condições/Melhorias.
4. Geração canônica pelo integrador e checagem de tamanho/contrato; validação nativa guardada.
5. D, bateria da versão final, revisão visual e publicação do fechamento.

## Tempo e modelos

Faixa provisória restante: **8–14 horas de trabalho ativo**, centro aproximado de 11h, antes de medir esta divisão. Referência por escopo: C 5–9h; D 3–5h. Não é uma estimativa por chat, nem um prazo garantido de relógio. A sobreposição de C pode reduzir o tempo decorrido; integração e D continuam em grande parte sequenciais. Reestimar no primeiro checkpoint usando progresso real, conflitos, custo dos novos catálogos e testes nativos. Esperas de acesso e recuperação de falhas externas não estão quantificadas. Não prometer metade do prazo nem converter automaticamente em dias/semanas.

Codex: manter a recomendação de planejamento **GPT-6.1 Sol, High** para implementação/integração. Claude: usar um modelo de programação/revisão disponível no seletor da conta, com esforço alto se oferecido; confirmar e informar o nome real, sem presumir disponibilidade ou equivalência. Em cada início/checkpoint/encerramento, recomendar modelo e esforço para a próxima ação com motivo curto; não afirmar qual está rodando nem trocar configurações automaticamente.

## Prompts prontos para colar

- [1 — integrador Codex](prompts-b47/cd/01-integrador.md)
- [2 — personagem e Formas, Codex](prompts-b47/cd/02-personagem-codex.md)
- [3 — entidades e revisão cruzada, Claude](prompts-b47/cd/03-entidades-claude.md)

Usar o bloco integral do arquivo correspondente. O prompt 1 pode ser usado neste chat; os outros dois em chats separados conectados ao mesmo repositório. Não usar os prompts históricos de A+B para iniciar C+D.
