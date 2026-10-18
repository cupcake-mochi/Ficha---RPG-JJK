# Ciclo Maldito B47 — plano e retomada

**Estado vigente · 17/10/2026:** A+B+C+D, regressões antigas, medidas e oficial concluídos. Oficial liberada para cópias; [fechamento](acabamento-b47/OFICIAL-FECHAMENTO.md). Estados e restrições históricas abaixo cedem à autorização delimitada do roteiro oficial. Não repetir montagem. B84 permanece otimização futura.

**Histórico após A+B, 16/10/2026:** A+B estão concluídos nativamente e publicados em `dce00ab8a244f53218c978293d10c5c1894b1ef8`. O [checkpoint atual](PENDENCIAS.md) e [checkpoint PC](capacidade-b47/RETOMADA-PC.md) prevalecem sobre os estados históricos de A/B abaixo. C/D ainda não começaram. A divisão preparada para essa continuação está em [PLANO-PARALELO-CD-B47.md](PLANO-PARALELO-CD-B47.md), com [três prompts novos](PROMPT-WORK-B47.md). Publicar o plano não inicia as frentes; usar cada prompt autoriza seu papel. As seções C/D e decisões mecânicas deste documento continuam válidas.

Estado consolidado em **16/10/2026**. Este é o ponto de entrada vigente para continuar o projeto, inclusive em outro computador ou pelo Work. Em caso de conflito com checkpoints antigos de `PENDENCIAS.md`, a rota deste documento prevalece.

A execução em três chats e os limites de edição/publicação estão em [PLANO-PARALELO-B47.md](PLANO-PARALELO-B47.md). Esse suplemento substitui o antigo prompt único para esta rodada.

## Projeto e estado real

- Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK
- Ramo de trabalho: `codex/configuracao-b47`. O `main` ainda não contém esta sequência de trabalho; continuar a partir deste ramo.
- Base anterior à redução: `84d8f8c`, Melhorias e Restrições custom. Fechamento local da redução em `f3a3fbd`; retomada e prova nativa parcial em `186e844`/`6a226c3`, com revisão adicional integrada em `3323803`.
- [Cópia nativa de revisão](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit#gid=47001).
- [Apps Script da revisão](https://script.google.com/u/0/home/projects/1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf/edit).
- [Ficha oficial — somente leitura](https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit).
- [Descartável reservada à construção integral](https://docs.google.com/spreadsheets/d/12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc/edit).
- [Descartável dos testes de Melhorias/Restrições](https://docs.google.com/spreadsheets/d/1D215acC6Dxhu8i7x0aF7pmiNbJ95_U1CiH4980QozLk/edit).

**Redução local e Sheets descartável validados; aplicação na revisão pendente.**
O gerador usa 10 Famílias, 30 Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios,
com ANALISE 10/7.356 chaves. A revisão Google continua na capacidade anterior e
no formato 9: nela houve somente leitura. A retomada criou backup nativo e
migrou a descartável `1hBogVNW0vqeLYwa0PNl04Y2Nel9-7nrCoODWq1FKsb4`:
102 lotes confirmados, 22 checagens, zero erros nas faixas afetadas lidas.
Código Apps Script vinculado ainda não foi salvo/relido; a prova permanece
PARCIAL e não libera a revisão. Estado, IDs e próximos passos em
[capacidade-b47/NATIVO-PARCIAL.md](capacidade-b47/NATIVO-PARCIAL.md);
medidas locais em [RELATORIO.md](capacidade-b47/RELATORIO.md). O bot pertence a outro trabalho.

## O que já está implementado e validado na revisão

- ANALISE e leitor, atualmente no formato 9, com 18.948 chaves únicas.
- BÔNUS E MUDANÇAS; regras de campanha; tabela de XP; vida rolada; Morrendo e Sequelas extras.
- Custom 3a: Origem, Marcante, Menor, Arma, Escudo, Uniforme, Item comum e Ferramenta amaldiçoada.
- Custom 3b: Caminho, Trilha, Perícia e Ofício. Habilidades preenchem os cartões originais do grupo 7.
- Famílias custom e limites de Famílias da técnica.
- Autonomia individual e nove posições de Família em cada uma das 12 invocações.
- Melhorias e Restrições custom, bases opcionais e herança das verificações do livro, nos cartões existentes.

O fechamento anterior passou 54 verificações focais, 22 ordens de carregamento, 19 ausências de arquivos e 150 verificações de construção simulada em três fases. Houve testes mecânicos e visuais no Sheets, restauração das 395 entradas do cenário e comparação integral das 75.796 células da ANALISE. A correção final de texto passou sete cenários locais e o ciclo nativo curto/longo/limpeza. Os 13 arquivos alterados/novos foram salvos e relidos integralmente no Google. São resultados históricos da versão anterior à limpeza, não testes já realizados no próximo ambiente.

## Rota fechada para a próxima retomada: 1 + 2 primeiro

1. **A — reduzir capacidade e medir.**
2. **B — tratar carregamento, envio e organização dos testes, usando a medição de A.**
3. **C — concluir os conteúdos restantes da 3c sobre a estrutura menor.**
4. **D — polir a interface e fazer a auditoria completa de entrega.**

As etapas 1/2/3 comparadas nas estimativas da conversa significam capacidade, carregamento/envio e acabamento/testes finais. A lista A–D acima inclui também os conteúdos que ainda precisam ser construídos.

Checagens **focais, mecânicas e visuais** acompanham cada mudança. A bateria completa e a revisão de todas as telas ficam para o fechamento. Corrigir problemas encontrados na entrega que os introduziu; não acumular defeitos conhecidos para o final.

## A — capacidade, migração e medida

| Definições custom adicionais ao livro | Capacidade v9 (ainda na revisão) | Alvo / gerador v10 |
|---|---:|---:|
| Famílias | 318 | **10** |
| Melhorias | 789 | **30** |
| Restrições | 395 | **30** |
| Perícias/Ofícios | 131 vagas intercambiáveis | **10 Perícias + 10 Ofícios** |
| Total desses grupos | 1.633 | **90** |

Essas definições são compartilhadas pelo personagem e por todas as invocações. Uma definição pode ser escolhida em vários lugares. A capacidade do catálogo não deve ser multiplicada pelo número de posições de uso. Os conteúdos do livro continuam disponíveis. As nove posições físicas de Família por invocação e os limites mecânicos permanecem.

Os 25 cartões compartilhados da 3a e os cadastros de um Caminho/uma Trilha ficam fora desta redução inicial. Capacidades de tipos futuros serão pequenas, normalmente 10/20/30; não construir outra reserva de centenas de cadastros sem uma nova decisão explícita.

- [x] Confirmar ramo, estado do Git e disponibilidade de ferramentas no novo ambiente. (Local; ver relatório.)
- [x] Guardar backup nativo integral e snapshot das faixas alteradas antes da migração descartável. Feito na retomada de 16/10; snapshot relido antes do envio. Renovar backup/snapshot para a revisão ou outra tentativa futura.
- [x] Centralizar capacidades e derivar faixas/posições delas; remover dependências de endereços fixados para as quantidades antigas. (Local; ver relatório.)
- [x] Implementar os alvos da tabela, distinguindo 10 Perícias de 10 Ofícios. (Local; ver relatório.)
- [x] Retirar também fórmulas, menus, notas, alturas e grupos excedentes. Apenas esconder cartões não resolve o peso. (Local; ver relatório.)
- [x] Auditar painéis de treino e tabelas de apoio afetados, preservando escolhas, regras e resultados. (Local; ver relatório.)
- [x] Mapear entradas/referências por identidade; 509 entradas/notas restauradas na descartável. Não cortar campos preenchidos nem associar silenciosamente um identificador a outro cadastro. Revisão futura exige nova guarda.
- [x] Resolver e documentar a versão do contrato ANALISE: chaves mantidas/descontinuadas, fontes e leitor. Não reaproveitar uma chave com outro sentido. A retirada de vagas afeta o contrato; não manter milhares de exportações vazias por inércia nem removê-las silenciosamente. (Local; ver relatório.)
- [x] Ajustar testes à capacidade nova, preservando casos negativos, herança, nomes literais, primeira/última vaga, reutilização e integridade da migração. (Local; ver relatório.)
- [x] Aplicar migração pontual na cópia de revisão somente depois de validar em descartável e confirmar acesso. (16/10: migração C na revisão, ver `conteudos-b47/comum/MIGRACAO-C-REVISAO.json`.)
- [x] Medir antes/depois: linhas, fórmulas, tamanho dos arquivos e tempos disponíveis. Pós-D: `acabamento-b47/MEDIDAS-POS-D.md`; contagens atuais/históricas, gatilhos Google e VM separados; construção nativa de 821 s reutilizada. Sem baseline nativa v9 ou latência isolada de persistência inventadas.
- [x] Registrar resultados parciais e delimitar B restante: código vinculado, testes visuais/gatilhos e medidas nativas. Pacote REST reduzido de 260/116.025 para 102/20.058 lotes/pedidos, com equivalência provada; ver NATIVO-PARCIAL.md. Não estimar tempo Apps Script por resultados VM/API.

## B — gargalos restantes e fluxo de trabalho

- [x] Perfilar o que resta lento após A: abertura, edição, seleção/expansão medidas na cópia funcional; montagem nativa D reutilizada, persistência confirmada sem tempo isolado. `acabamento-b47/MEDIDAS-POS-D.md`.
- [ ] Otimização futura B84: evitar integralmente preparar estruturas de construção em operações pequenas. Perfil concluído; inicialização global ainda expande ABAS. Guardas/idempotência/quatro leituras de Range já existem. Carregamento sob demanda não implementado nem demonstrado necessário à entrega atual; fica fora do item 2 de medidas desta retomada.
- [x] Avaliar método oficial de envio: infra integrada com manifesto/hashes, snapshot remoto, retirada explícita e conferência posterior. Fluxo offline testado; envio Apps Script real ainda pendente por falta de ferramenta/autenticação compatível.
- [x] Verificar ferramentas, escopos e autenticação disponíveis separadamente. Drive/Sheets funcionaram; Apps Script/navegador não estão expostos neste ambiente. Não presumir que a conexão Drive fornece esse acesso.
- [x] Delimitar a investigação e registrar dependência/caminho funcional em NATIVO-PARCIAL.md e ROTEIRO-NATIVO.md, sem contornar rede/credenciais nem depender do PC.
- [x] Consolidar os testes novos no roteiro geral. (17/10: `rodar-tudo.sh` inclui os testes novos que rodam sem dados privados; os que pedem leituras nativas e os de expectativa histórica estão listados em `acabamento-b47/BATERIA-D.json`.)
- [ ] Usar testes focais durante o desenvolvimento; repetir bateria mais ampla quando uma mudança, falha ou interação justificar.
- [x] Confirmar edição, salvamento, primeira/última vaga, cópia funcional e equivalência mecânica das funções alteradas. (C: cenários nativos; 17/10: cópia funcional com troca de paleta interrompida igual à revisão, ver `acabamento-b47/COPIA-FUNCIONAL-D.json`.)

## C — conteúdos restantes da 3c

> Concluída em 16/10/2026 (`21f1620`): ver `conteudos-b47/comum/FECHAMENTO-C.md` e as provas citadas lá.

Os desenhos e campos dos estudos já foram aprovados. Não reabrir a aprovação geral sem uma mudança concreta. Capacidade/custo dos tipos ainda não construídos precisam ser fechados segundo a estratégia pequena acima.

- [x] **Formas:** base opcional, Família, Peso, resolução, resultado, TR, Classe 0, restrição embutida, efeito/requisitos e alcance/área. Separar alcance e tamanho da área e conservar faixas distintas de personagem/entidade. Os valores demonstrativos do estudo não são regras novas.
- [x] **Aptidões/Bênçãos:** base opcional; escolha consumida ou gratuidade explícita. Categoria de Efeito vazia não torna a capacidade gratuita.
- [x] **Talentos do personagem:** cadastro, base opcional, requisitos/custos/efeitos e integração com os lugares existentes.
- [x] **Tipos de entidade:** base opcional; do zero, combinar separadamente funcionamentos existentes de vida, talismã e reserva de PE. Autonomia e alma são escolhidas na própria invocação.
- [x] **Talentos de entidade:** cadastro e integração com orçamento, requisitos e cartões atuais.
- [x] **Tipos de dano:** catálogo custom unido ao livro e menus consumidores.
- [x] **Condições:** o estudo aprovado as trata como opções de Melhoria; integrar suas informações e requisitos sem inventar um segundo mecanismo ou executar prosa como regra.
- [x] Em cada grupo, completar menus, cálculos, avisos, exportação ANALISE, roteiro de teste no Sheets e testes focais, incluindo base herdada e criação sem base.
- [x] Cruzar o inventário de menus ao fechar: propriedades/aprimoramentos, Kata/Manejo ou missão citados em históricos devem ser verificados contra consumidores reais. Não presumir automaticamente um novo escopo nem deixar uma opção existente de fora; registrar a conclusão e pedir decisão quando houver regra/escopo novo.

## D — interface e fechamento completo

> Concluída em 17/10/2026: ver o topo de `acabamento-b47/RETOMADA-D.md`.

- [x] Apresentar estudo enxuto na grade antes de construir o novo desenho. (estudos aprovados antes de C.)
- [x] Reunir a edição em CONFIGURAÇÃO, com seções claras, tabelas para registros simples e cartões para tipos complexos. (C; fundo padrão dos espaços novos aplicado em D.)
- [x] Conservar a referência Forma B: regras/efeitos à esquerda e edição custom organizada; mudanças de desenho devem ser apresentadas ao usuário.
- [x] Levar explicações úteis para notas. Inventário, orçamento, histórico de aprovação e relatórios técnicos ficam na documentação, não no fluxo do jogador. (inclui as 12 ajudas de tipo de entidade, mantidas em D.)
- [x] Retirar estudos/exemplos depois de auditar dependências de fórmulas, menus e scripts. (`acabamento-b47/AUDITORIA-ESTUDOS.json`; revisão com 22 abas.)
- [x] Preservar escolhas e resultados nos lugares originais da FICHA, FICHA PESSOAL, FICHA AMALDIÇOADA e INVOCAÇÕES. (comparações integrais de C e D.)
- [x] Executar bateria completa da versão final e casos de interação entre conteúdos/regras. (17/10: executada; aprovados e falhas anteriores a D, todas com causa registrada, em `acabamento-b47/BATERIA-D.json`. As expectativas históricas não foram alteradas.)
- [x] Revisar carteira/foto/paleta, bordas, dimensões, textos, menus, inventário, grupo 7, áreas recolhidas e todas as invocações. (descartável D: interações; revisão: leitura visual.)
- [x] Auditar ANALISE inteira, leitor, erros de fórmula, cópia funcional e persistência do código. (`acabamento-b47/FOTO-REVISAO-POS-FUNDO.json`, `NATIVO-CODIGO-REVISAO-D.json`, `COPIA-FUNCIONAL-D.json`.)
- [x] Construir do zero somente em descartável; medir tempo e custo reais. Restaurar entradas temporárias. (17/10: 4 execuções, 821 s; ver `acabamento-b47/CONSTRUCAO-D.json`.)
- [x] Entregar versão revisável e pendências explícitas. Oficial B47 publicada na janela acompanhada autorizada de 17/10; comparação completa e cópia funcional aprovadas. Integração em `main` autorizada; prova em acabamento-b47/OFICIAL-B47.json.

## Decisões que devem ser preservadas

- CONFIGURAÇÃO fixa em Mizuki Escuro, fora da troca de paleta. Rótulos claros; ajuda contextual em notas.
- “Trocar por” fixa o resultado final da caixa, inclusive zero, substituindo os bônus dela.
- XP começa em zero no nível inicial da campanha. Vida rolada mantém vida inicial fixa do Caminho, com dados nos níveis seguintes e Constituição conforme a regra existente.
- Menores e Legados são personalizáveis. Marcantes de Origens do livro seguem opções publicadas, inclusive famílias próprias do Descendente; exceção da criação da Restrição corporal. Origem totalmente homebrew, sem base do livro, pode ter marcante própria.
- Origem do zero permite Fundamento, Manejos e Técnica Marcial com ou sem energia; não herda benefícios exclusivos sem base.
- Caminho usa níveis 2/7/15/23/30 e Trilha 2/11/19/27 nos cartões originais do grupo 7.
- Menus em opções fechadas; equipamentos/itens mantêm os campos de digitação livre autorizados.
- Famílias novas somam às nove do livro. Estados da técnica não concedem automaticamente Livre à entidade. Livres/Fechadas da técnica são configuráveis; Neutras é saldo do total.
- Autonomia individual, padrão Autônoma. Não autônoma recebe uma Família Livre nova, que aumenta também o total aberto em uma; precisa de ordem prévia para ações, exceto Reação. É regra prevista para o Guia de Criação. CONFIGURAÇÃO ajusta ganhos/limites, não escolhe autonomia globalmente.
- MESTRE VIU é lembrete; aprovação de custom pertence ao bot, no chat. Não transformar descrição livre em automação numérica implícita.
- Toda opção do livro continua disponível junto do custom válido; preservar herança e exceções nomeadas.

## Arquivos e validação

- Gerador: `ficha-v01/monta.py`; fontes de capacidades em `custom_progressao.py`, `custom_criacao.py` e `custom_pecas.py` na mesma pasta.
- `.gs` são gerados; `apps-script/Codigo.gs` é a exceção editada diretamente. Teto de **900.000 bytes por .gs**.
- Contrato: [ESQUEMA-ANALISE.md](ESQUEMA-ANALISE.md). O início contém histórico; a seção de formato 9 descreve a implementação atual.
- Estudos: [ESTUDO-CUSTOM-3B.md](ESTUDO-CUSTOM-3B.md), [ESTUDO-CUSTOM-3C.md](ESTUDO-CUSTOM-3C.md), fontes em `mockup/prototipo_custom_3b.py`, `prototipo_custom_3c.py` e `prototipo_custom_3c_restante.py`.
- Desenhos originais: [plano](referencias-b47/PLANO-CONFIGURACAO.html) e [rodada 2](referencias-b47/estudo-configuracao-rodada-2.html). As decisões novas deste documento prevalecem sobre capacidade/histórico antigos.
- Roteiros: [TESTE-CONFIGURACAO.md](TESTE-CONFIGURACAO.md), [TESTE-CUSTOM-3C.md](TESTE-CUSTOM-3C.md) e arquivos `TESTE-*` aplicáveis.
- Regressões relevantes: `regressao-configuracao.py`, `regressao-campanha.py`, `regressao-custom.py`, `regressao-progressao.py`, `regressao-familias-invocacao.py`, `regressao-criacao.py`, `regressao-pecas.py`, `regressao-textos-custom.js`, `regressao-construir.js`, `conferir-copias.py`, `comparar-ficha-01.py` e `ler-analise.py`.
- Evidências mínimas do fechamento anterior: [referencias-b47/evidencias](referencias-b47/evidencias). Relatórios antigos não provam uma migração futura.

No computador original, trabalho pesado é serial e limitado:

```bash
systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 -p CPUQuota=200% nice -n15 env NODE_OPTIONS=--max-old-space-size=1500 <comando>
```

Em ambiente diferente, verificar os limites disponíveis e usar um equivalente adequado antes de trabalhos pesados. O PC original tem 15 GB e já reiniciou por RAM. Não elevar tetos nem matar processos por padrão amplo.

`ficha-v01/original.xlsx` continua ignorado no diretório de entrada, mas uma cópia histórica independente agora está versionada em `nuvem-b47/fixtures/original.xlsx`; o comparador a utiliza quando a entrada local falta. As bases das regressões de campanha/custom e o modelo anterior à 3c também estão no Git, com hashes e origem. O gerador usa o `ficha-v01/layout.json` versionado. **Nunca importar Excel no Google Sheets.** Um workbook local usado como artefato/calculadora de teste não autoriza importação na ficha nativa.

Não executar `construir()`/`continuar()` sobre a revisão preenchida ou a oficial. Conferir em código o destino de qualquer helper antes de executá-lo; a montagem integral usa exclusivamente a descartável.

## Retomada em outro ambiente

A preparação executável está em [NUVEM.md](NUVEM.md), com dependências fixadas, fontes e bases de teste versionadas e diagnóstico/smoke. Leia também [nuvem-b47/TESTES.md](nuvem-b47/TESTES.md): expectativas históricas de formatos 5/6/7 não viraram automaticamente testes aprovados da versão 9. A consulta R52 textual está no Git, separada do manual R51 do gerador.

Leia este documento e o contrato no próprio repositório. Não depender de `../PLANO.md`, `../RETOMAR-B47.md`, caminhos de disco ou abas do Brave do computador anterior. As informações essenciais estão versionadas aqui.

Antes de afirmar aplicação no Google, confirmar ferramentas, conta, acesso, salvamento e leitura posterior. Se o ambiente não acessar Sheets/Apps Script, avançar no código, testes e migração reprodutível que forem independentes; informar precisamente o que não foi aplicado/testado nativamente. Autorizações de conta são realizadas pelo usuário. Não declarar execução ou validação que não aconteceu.

Manter checkpoints neste documento e em `PENDENCIAS.md`: feito, testes, alterações nativas confirmadas, próximo passo e dependências. Não alterar regras sem perguntar; desenhos novos precisam de estudo e aprovação. Sem mensagens ao outro chat, mudanças de compartilhamento ou trabalho no bot.

## Tempo e escopo

O restante completo da ficha foi estimado em aproximadamente **10–18 horas, centro de 14 horas**, com capacidade reduzida primeiro. O cenário 1+2 foi estimado em 9–17 horas, centro de 13 horas; a diferença de uma hora é menor que a incerteza e não deve orientar decisões como se fosse medida. São hipóteses de planejamento, incluem limpeza e conteúdos restantes e serão revistas após A. O bot não entra nessa conta.

A publicação deste planejamento foi autorizada. Os três prompts agora incluem autorização delimitada para commits/push nos respectivos ramos de tarefa e para o chat 1 integrar as frentes em `codex/configuracao-b47`, após revisão e testes. Essa autorização vale quando o usuário iniciar as tarefas com esses prompts. Não autoriza merge em `main`, publicação na ficha oficial, force push ou mudanças de acesso. As restrições históricas de Git abaixo de checkpoints antigos não substituem essa divisão vigente.

Use [PROMPT-WORK-B47.md](PROMPT-WORK-B47.md) para escolher os três prompts de nuvem. A primeira entrega integrada é A + B; C + D ficam organizadas para a continuação. Cada chat deve sempre recomendar modelo e esforço para a próxima ação.


## Checkpoint · capacidade e desempenho local · 16/10/2026

Base confirmada: `4187df37640b5e0966cdb342f56f9ee0a0daf16a`.
Ramo de implementação: `codex/b47-capacidade`; destino de integração autorizado:
`codex/configuracao-b47`. Nenhum trabalho em main. O
[relatório da rodada](capacidade-b47/RELATORIO.md) reúne medidas, comandos,
contrato, validação e limitações. [Roteiro nativo](capacidade-b47/ROTEIRO-NATIVO.md).

Acesso Drive/Sheets comprovado por conector, com leitura atual dos catálogos
vazios. Não há ferramenta Apps Script ou navegador conectado nesta sessão;
nenhuma escrita/migração ou montagem Google realizada. Snapshot integral atual,
validação descartável, código salvo/relido, aplicação na revisão e tempos nativos
continuam pendentes. Os testes locais/sintéticos não substituem essas etapas.

A listagem completa do remoto corrigiu a consulta inicial, restrita a `main`:
infra `b8ab7b5` e revisão `287b2c1` (ramo alternativo
`claude/kind-feynman-sewhec`) foram recebidas, revisadas e integradas separadamente.
Seus testes focais aplicáveis foram executados no alvo real; selos de geração, guardas de envio,
leitor e validações longas foram corrigidos antes da publicação. O relatório
registra limites e resultados. A revisão independente reproduziu A em
`4610c88` (14/14 etapas); as correções e a combinação posterior foram testadas
pelo integrador, sem nova auditoria externa do SHA final.
O roteiro focal concluiu 23 etapas após a reexecução integral de Progressão;
a evidência mantém a falha histórica inicial e a prova exata da fatoração.
C e D não foram iniciadas. A estrutura menor já está pronta para essas etapas,
mas a estimativa restante depende primeiro da aplicação e medida nativas de A+B.

Próxima ação: disponibilizar um caminho oficial para
salvar/reler Apps Script; executar o roteiro nativo sem PC anterior.
Recomendação: **GPT-6.1 Sol, High**, por envolver preservação de entradas e
integração de contrato/código na mesma cópia.
