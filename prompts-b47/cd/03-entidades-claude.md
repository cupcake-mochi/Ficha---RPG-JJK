# B47 C+D — prompt 3, entidades e revisão no Claude

Usar em Claude Code conectado ao repositório. Escolher no seletor um modelo disponível adequado a programação/revisão, com esforço alto se oferecido; informar o nome real sem presumir disponibilidade. Cole o bloco integral.

```text
Implemente a frente de entidades e faça a revisão cruzada de personagem do Ciclo Maldito B47 C+D.
Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK.

A+B estão concluídos em dce00ab8a244f53218c978293d10c5c1894b1ef8. Não repita a redução nem a revisão antiga como se C/D já estivessem implementadas. Leia integralmente PLANO-PARALELO-CD-B47.md, que substitui a antiga divisão A+B para esta rodada. Seu papel atual inclui implementar entidades em módulos/patches isolados, além de revisar personagem; não é apenas a auditoria histórica de A+B.

BASE E PREPARAÇÃO
Crie/use claude/b47-cd-entidades a partir do commit que publicou o plano C+D em codex/configuracao-b47, com dce00ab como ancestral. Não use main nem reutilize automaticamente claude/b47-revisao. Confira alterações locais, refs remotas explícitas e trabalho existente antes de atualizar; não resete nem sobrescreva. Se o serviço exigir outro prefixo/sufixo, preserve a base e informe o ramo real. Registre SHA completo inicial e o commit comum de preparação; examine avanços da integração antes de escolher/atualizar a base.

Leia AGENTS.md, NUVEM.md, nuvem-b47/TESTES.md, topo vigente de PENDENCIAS.md, C/D e decisões de PLANO-RETOMADA-B47.md, ESTUDO-CUSTOM-3C.md, mockup/prototipo_custom_3c_restante.py e os estudos aplicáveis, ESQUEMA-ANALISE.md e capacidade-b47/RETOMADA-PC.md. Faça preparação/smoke documentados para o ambiente real. Não dependa de caminhos/discos antigos, sessão do PC ou memória compartilhada com Codex.

ÁREA E CONTRATO
Edite diretamente somente revisao-b47/cd-entidades/: módulos, testes/fixtures, propostas, patches, relatório de implementação e revisão cruzada. O integrador altera núcleo, leitor, esquema ANALISE, arquivos gerados, documentação central e Google. Não edite diretamente ficha-v01/, ficha/, apps-script/ ou módulos da frente de personagem. Não regenere/commite GS. Mudanças necessárias fora da sua pasta são patches dentro dela, identificando base, alvo e ordem, para o integrador revisar/aplicar. Não aplique esses patches no núcleo deste ramo. Código isolado não é integração de produção.

O integrador fecha o contrato comum em conteudos-b47/comum/. Enquanto isso, avance inventário, regras/exceções do livro, módulos parametrizados e testes, publicando proposta de campos/capacidade/interface na sua pasta. Não fixe endereços globais, decida versão ANALISE ou reutilize namespaces unilateralmente. Registre dependências concretas de contrato; não espere a outra frente para tudo. Catálogos novos serão pequenos e compartilhados, sem copiar automaticamente capacidades de A+B nem multiplicar cadastros pelas posições de uso.

IMPLEMENTAÇÃO
1. Tipos de entidade: base opcional. Sem base, combinar separadamente os funcionamentos existentes de vida, talismã e reserva de PE. Não presumir que um desses campos concede os outros nem benefícios exclusivos de base não escolhida. Autonomia e alma permanecem na própria invocação.
2. Talentos de entidade: cadastro, orçamento, requisitos, custos/efeitos e integração proposta nos cartões existentes.
3. Menus livro+custom válido, cálculos, avisos, proposta de exportação ANALISE e patches para consumidores. Preserve 12 invocações, nove posições de Família por invocação, limites mecânicos e autonomia individual. Uma definição pode ser reutilizada em várias invocações.

Não invente regras, não execute texto livre como automação e não redesenhe a interface. Moldes e combinações descritos no plano já foram aprovados; não peça aprovação geral de novo sem mudança concreta. Formas, inclusive seus usos em entidades, pertencem ao outro Codex; você confere a interação. Tipos de dano, Condições e D pertencem ao integrador.

TESTES E REVISÃO CRUZADA
Prove herança com base, criação sem base, combinações independentes vida/talismã/PE, orçamento/requisitos de Talentos, primeira/última vaga, inválidos/duplicatas, nomes literais com * ? ~, reutilização nas 12 invocações e preservação de autonomia/alma/Famílias. Entregue roteiro nativo para o integrador. Use testes significativos e indique arquivo/local real das falhas; não altere expectativas apenas para verde. Testes impedidos por Calc/fixture/ferramenta são registrados como impedidos. Trabalho pesado em série por ambiente; sem geração integral que regrave saídas canônicas.

Depois que o usuário fornecer um SHA de personagem ou ele estiver disponível no Git, leia o diff desse SHA, revise Formas/Aptidões/Talentos do personagem e as interações com entidades. Registre SHA revisado, achados por gravidade, arquivo/local, reprodução, testes e limitações em um relatório separado na sua área. Não declare revisão de código não recebido. Não revise seu próprio trabalho como se fosse independente: o integrador revisará entidades. Não pare sua implementação aguardando personagem.

AUTORIZAÇÃO E ENTREGA
Autorizo implementação local e revisão descritas, commits e push somente no seu ramo de tarefa e área/patches delimitados. Sem integração em codex/configuracao-b47, main, force push, escrita no Google/Apps Script remoto, ficha oficial, bot ou alterações de acesso. Não importar Excel no Google. Não enviar mensagens automáticas, abrir outros chats/agentes nem acessar a sessão do PC de outro chat. Credenciais, dados pessoais e snapshots de jogador ficam fora do Git.

Publique relatório de implementação com objetivo/escopo, base e SHA testado, ramo, arquivos, módulos/patches e ordem de incorporação, contrato esperado, comandos/resultados, testes impedidos, nenhuma escrita Google, riscos/dependências e próxima ação/modelo/esforço. Entregue commits pequenos e utilizáveis; no final informe SHA completo publicado, links do commit/relatórios e o que o integrador precisa aplicar/testar. Distinguir implementação, revisão cruzada, integração e prova nativa; não declarar etapas não executadas. Troca entre chats é por Git/links fornecidos pelo usuário, sem memória presumida.

8–14h é a estimativa provisória do conjunto C+D, não do seu chat nem prazo de relógio. No início informe as opções reais do seletor/modelo/esforço que puder verificar e recomende uma para a próxima ação; se não puder verificar, diga isso sem inventar nomes ou equivalências. Repita a recomendação com motivo curto em checkpoints e no encerramento; não afirme qual modelo está rodando sem evidência nem altere configurações. Responda em português do Brasil.
```
