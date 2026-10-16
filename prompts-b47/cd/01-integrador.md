# B47 C+D — prompt 1, integrador Codex

Usar neste chat ou em um Codex conectado ao repositório. Recomendação de planejamento: GPT-6.1 Sol, High. Cole o bloco integral.

```text
Continue o Ciclo Maldito B47 como implementador dos conteúdos comuns e integrador de C+D.
Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK.

A+B estão concluídos em dce00ab8a244f53218c978293d10c5c1894b1ef8. Não reinicie A/B nem reaplique os 102 lotes antigos. Sua tarefa agora é C+D conforme PLANO-PARALELO-CD-B47.md, que substitui a antiga divisão de A+B para esta rodada. Leia-o integralmente.

BASE E PREPARAÇÃO
Trabalhe em codex/b47-capacidade atualizado a partir da publicação do plano C+D; integração em codex/configuracao-b47. Confira alterações locais e refs remotas explícitas antes de atualizar. Não use main, não sobrescreva trabalho e não suponha fetch de todos os ramos. Registre SHA completo inicial, ramo, ambiente e ferramentas. Confira que dce00ab é ancestral e identifique o commit comum de preparação dos três chats. Se houver divergência/avanços, examine o diff antes de integrar.

Leia AGENTS.md, NUVEM.md, nuvem-b47/TESTES.md, o topo de PENDENCIAS.md, seções C/D e decisões de PLANO-RETOMADA-B47.md, ESTUDO-CUSTOM-3C.md, seus protótipos em mockup/, ESQUEMA-ANALISE.md e capacidade-b47/RETOMADA-PC.md. O checkpoint vigente de A+B prevalece sobre relatos antigos de nativo pendente. Faça preparação/smoke documentados no ambiente real; no PC reutilize o ambiente existente se confirmado. Não regenere tudo por rotina nem repita testes antigos sem motivo.

RESPONSABILIDADES
Você é dono exclusivo do núcleo, leitor, esquema ANALISE, arquivos gerados, documentação central, integração e Google. Outro Codex trabalha em conteudos-b47/personagem/ (Formas, Aptidões/Bênçãos e Talentos do personagem). Claude trabalha em revisao-b47/cd-entidades/ (Tipos e Talentos de entidade, depois revisão cruzada de personagem). Eles entregam módulos, patches e testes; incorpore-os na fonte canônica após examinar os diffs. Não presuma que código isolado já está integrado.

Prepare em conteudos-b47/comum/ o contrato de campos/tipos, vazios/herança/base opcional, capacidades pequenas e compartilhadas dos tipos novos, interfaces dos módulos, destinos no desenho aprovado e proposta de exportação/namespaces. As capacidades de A+B não são automaticamente as dos tipos novos. Derive endereços de capacidades e evite centenas de cartões por multiplicar posições de uso. Concilie propostas das frentes; não reutilize chaves ANALISE com outro sentido. Feche eventual versão nova e compatibilidade do leitor com testes, sem alterar o bot.

Implemente Tipos de dano unidos ao catálogo do livro e menus consumidores. Integre Condições como opções de Melhoria segundo o estudo aprovado, sem segundo mecanismo nem execução de prosa. Cruze o inventário real de menus, incluindo menções históricas a propriedades/aprimoramentos, Kata/Manejo e missão; não invente escopo nem omita consumidor existente.

Receba links/SHAs e relatórios pelo usuário ou leia os ramos no Git. Integre uma frente por vez, registre origem e SHA testado, resolva conflitos e teste o conjunto antes de atualizar codex/configuracao-b47. Aplique patches só depois de conferir base, alvo e ordem; não execute migrações recebidas sem guardas. Revise entidades e confira a revisão de personagem feita pelo Claude. Se uma entrega estiver pendente, avance o que for independente e registre a dependência, sem declarar conclusão/revisão inexistente. Não envie mensagens automáticas nem abra outros chats/agentes.

PRESERVAÇÃO E D
Preserve todas as decisões aprovadas: base opcional/livro disponível, herança e exceções, não interpretar texto como regra, nove Famílias e autonomia individual nas 12 invocações. Formas pertencem à frente de personagem mas também precisam funcionar nas entidades, com faixas próprias. Aptidão/Bênção só é gratuita se explícito; vida/talismã/reserva de PE de tipo do zero são independentes; autonomia/alma ficam na invocação. Não reabra os moldes já aprovados sem mudança concreta. Regra nova/ampliação de escopo exige decisão do usuário.

Após C integrada, execute D: reúna edição em CONFIGURAÇÃO, preserve referência Forma B e escolhas/resultados nas fichas originais, use notas para ajuda contextual e mantenha relatórios/orçamentos fora da interface do jogador. Apresente estudo enxuto na grade antes de construir mudança nova de desenho ainda sujeita à aprovação. Retire estudos/exemplos somente após auditar dependências. Faça bateria final e interações, carteira/foto/paleta, dimensões/bordas/textos, menus, grupo 7 e invocações; ANALISE inteira/leitor/erros; código persistido/gatilhos/cópia funcional sem ativação manual. Restaure cenários temporários. A prova de A+B não valida automaticamente a nova combinação.

GOOGLE E AUTORIZAÇÃO
Autorizo executar C+D neste papel, commits/push no seu ramo, integração revisada/testada em codex/configuracao-b47 e aplicação nativa guardada na cópia de revisão. Sem main, force push, oficial, bot ou alterações de acesso. Não importar Excel no Google. Cada GS deve ficar abaixo de 900.000 bytes.
Revisão: 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0.
Descartável de construção: 12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc.
Oficial somente leitura: 1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro.
Confirme acesso/ferramentas/conta e o destino de cada helper. Novo snapshot e backup nativos, guardas e prova conjunta em descartável precedem migração pontual da revisão. Nunca construir/continuar na revisão preenchida ou oficial; não repetir lotes antigos, contornar guarda ou usar snapshot vencido. Preserve as descartáveis que guardam evidência; copie para cenários destrutivos quando necessário. Releia integralmente código/manifesto salvo. Sem Google disponível, avance localmente e discrimine o que falta aplicar/testar; não declare prova nativa sem execução. Credenciais, dados pessoais e snapshots de jogador ficam fora do Git.

ENTREGA E COMUNICAÇÃO
Mantenha checkpoints com SHAs/ramos, frentes recebidas/pendentes, comandos/resultados e testes impedidos, modelo/código efetivamente testados, medidas nativas separadas de simulação, estado real do Google e próximos passos. Testes focais durante desenvolvimento; bateria final em D, com trabalhos pesados em série por ambiente. Corrija defeitos introduzidos sem adiar para o fim. Não altere expectativas apenas para produzir verde.
8–14h é faixa provisória restante do conjunto, não por chat nem promessa de relógio; reestime no primeiro checkpoint com evidência. Bot/formato 10 e variante histórica 4 continuam externos.
Recomendação inicial: GPT-6.1 Sol, High, pela integração e preservação de dados/regras. Ao iniciar, em cada checkpoint e ao encerrar, recomende modelo/esforço para a próxima ação com motivo curto, sem afirmar o modelo atual nem trocar configurações. Responda em português do Brasil.
```
