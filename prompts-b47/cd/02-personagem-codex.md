# B47 C+D — prompt 2, personagem e Formas no Codex

Usar em outro chat Codex conectado ao repositório. Recomendação de planejamento: GPT-6.1 Sol, High. Cole o bloco integral.

```text
Implemente a frente de personagem e Formas do Ciclo Maldito B47 C+D.
Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK.

A+B estão concluídos em dce00ab8a244f53218c978293d10c5c1894b1ef8. Não refaça A/B. Leia integralmente PLANO-PARALELO-CD-B47.md: ele rege a divisão nova; o antigo plano paralelo de A+B é histórico.

BASE E PREPARAÇÃO
Crie/use codex/b47-cd-personagem a partir do commit que publicou o plano C+D em codex/configuracao-b47, preservando dce00ab como ancestral. Não use main. Confira alterações locais, refs remotas explícitas e trabalho existente; não resete nem sobrescreva ramo. Se a plataforma exigir outro nome, mantenha a base e informe o nome real. Registre SHA completo inicial e o commit comum de preparação; se o ramo de integração avançou, examine as diferenças antes de escolher/atualizar a base.

Leia AGENTS.md, NUVEM.md, nuvem-b47/TESTES.md, topo vigente de PENDENCIAS.md, C/D e decisões de PLANO-RETOMADA-B47.md, ESTUDO-CUSTOM-3C.md e protótipos correspondentes, ESQUEMA-ANALISE.md e capacidade-b47/RETOMADA-PC.md. Confirme ferramentas e faça preparação/smoke conforme NUVEM.md para o ambiente real. Não dependa de disco do PC, sessão de navegador, caminhos antigos ou memória dos outros chats.

ÁREA E CONTRATO
Edite diretamente somente conteudos-b47/personagem/: módulos de implementação, testes/fixtures, propostas, patches e relatório. O integrador é dono exclusivo de ficha-v01/, ficha/, apps-script/, leitor, contrato ANALISE, testes centrais, planos e Google. Não regenere/commite GS nem regrave saídas canônicas. Alteração necessária fora da sua pasta deve virar patch revisável nela, com base, alvo e ordem de aplicação. Não aplique o patch ao núcleo neste ramo. Módulo isolado não equivale a integração de produção.

O contrato comum será fechado pelo integrador em conteudos-b47/comum/. Não fique parado esperando: inventarie produtores/consumidores, leia exceções do livro, prepare casos mecânicos e módulos parametrizados, e publique proposta de campos/capacidade/interface na sua pasta. Não fixe endereços globais, escolha versão ANALISE nem reutilize namespaces unilateralmente. Informe dependência real de contrato quando afetar a integração. Capacidades dos tipos novos devem ser pequenas/compartilhadas; não copiar automaticamente as quantidades de A+B nem multiplicar registros por posições de uso.

IMPLEMENTAÇÃO
1. Formas: base opcional, Família, Peso, resolução, resultado, TR, Classe 0, restrição embutida, efeito/requisitos e alcance/área. Separe alcance de tamanho da área. Você responde pelas Formas do personagem E das entidades, preservando as faixas distintas; não deixe esse consumidor sem implementação porque a frente se chama personagem. Valores demonstrativos do estudo não são regras novas.
2. Aptidões/Bênçãos: base opcional; consumo de escolha ou gratuidade explícita. Efeito/categoria vazia não concede gratuidade. Preservar as rotas e verificações existentes.
3. Talentos do personagem: cadastro, base opcional, requisitos/custos/efeitos e integração proposta nos cartões/lugares existentes.

Em cada grupo entregue menus livro+custom válido, cálculos, avisos, proposta de exportação/patches de consumidores e roteiro de teste nativo para o integrador. Preserve base herdada e criação sem base, exceções nomeadas e regras aprovadas. Texto livre não vira automação. Não redesenhe a interface, não crie nova mecânica e não reabra aprovações sem mudança concreta. Tipos/Talentos de entidade são do Claude; Tipos de dano, Condições e D são do integrador.

TESTES E ENTREGA
Faça testes focais significativos: primeira/última vaga, nomes literais com * ? ~, tipo incorreto, duplicata, base e sem base, consumo/gratuidade explícita, requisitos/limites, reutilização e limpeza. Formas devem ter casos de personagem e entidade. Mostre o local real de qualquer falha, não só uma asserção que reproduz a implementação. Execute em série os trabalhos pesados por ambiente. Se faltar Calc/fixture/ferramenta, registre o teste impedido e avance o independente; não mude expectativa só para passar. Não execute a bateria completa sem necessidade nem geração integral que regrave arquivos fora da sua área.

Autorizo implementação local, commits e push somente no seu ramo de tarefa e dentro da área/patches descritos. Sem integração em codex/configuracao-b47, main, force push, Google, Apps Script remoto, ficha oficial, bot ou alterações de acesso. Não importar Excel no Google. Não enviar mensagens automáticas, abrir chats/agentes ou acessar a sessão do PC de outro chat. Não versionar credenciais, dados pessoais ou snapshots de jogador.

Publique relatório em conteudos-b47/personagem/ com objetivo/escopo, base e SHA testado, ramo, arquivos, módulos/patches e ordem de incorporação, contrato esperado, comandos/resultados, testes impedidos, ausência de escrita Google, riscos/dependências e próxima ação/modelo/esforço. Entregue commits pequenos e utilizáveis; continue tarefas independentes enquanto outra entrega estiver pendente. No final informe SHA completo publicado, link do commit/relatório e exatamente o que o integrador precisa fazer. Não declare aplicação nativa nem integração que não executou. O usuário repassará os links; não presuma memória compartilhada.

A estimativa 8–14h refere-se ao conjunto restante C+D, não ao seu chat nem a prazo garantido. Recomendação inicial: GPT-6.1 Sol, High, para preservar herança/requisitos e consumidores. Ao iniciar, em cada checkpoint e ao encerrar, recomende modelo/esforço para a próxima ação com motivo curto, sem afirmar o modelo atual nem trocar configurações. Responda em português do Brasil.
```
