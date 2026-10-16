# B47 C+D — entrega de personagem e Formas

## Objetivo e estado

Entregues motor, emissão de fórmulas vivas, editor no molde aprovado, pontes dos consumidores, testes, proposta de contrato e três patches revisáveis. Cobertura: Formas **do personagem e das 12 entidades**, Aptidões/Bênçãos e Talentos do personagem.

**É uma entrega isolada para incorporação.** O núcleo canônico não foi alterado neste ramo; os patches não foram aplicados a ele. Não houve geração ou commit de GS/XLSX, migração preenchida, aplicação ou validação Google. C integrada e D continuam com o integrador.

## Base, ramo e commits

- SHA inicial e preparação comum: `0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd`.
- Ancestral A+B obrigatório confirmado: `dce00ab8a244f53218c978293d10c5c1894b1ef8`.
- O remoto avançou durante a tarefa para `ae16895967d23044f558f31638df23c0fbdd7598`. O diff foi examinado: somente contrato comum e documentação. Incorporado por fast-forward, sem reset/rebase ou sobrescrita.
- Base dos patches e contrato lido: `ae16895967d23044f558f31638df23c0fbdd7598`.
- Ramo real: `codex/b47-cd-personagem`, em clone independente. Não foi usado main como base.
- Motor/testes: [9dd4c9aea411ed121f8ecc8a5d06592d5aa0764b](https://github.com/cupcake-mochi/Ficha---RPG-JJK/commit/9dd4c9aea411ed121f8ecc8a5d06592d5aa0764b).
- Código completo de emissão/consumo/patches e SHA de teste: [523e2887e82756a0f566bc73e5e1073c58e2580f](https://github.com/cupcake-mochi/Ficha---RPG-JJK/commit/523e2887e82756a0f566bc73e5e1073c58e2580f).
- Adaptação dos patches ao avanço do integrador e **SHA final testado**: [ffaca820b3be591d4985ae00067d22615c516236](https://github.com/cupcake-mochi/Ficha---RPG-JJK/commit/ffaca820b3be591d4985ae00067d22615c516236).
- O fechamento documental e o SHA final de publicação são informados na resposta da tarefa. [VALIDACAO.json](VALIDACAO.json) identifica o SHA exato testado e hashes dos arquivos de código/teste/patch.

Todas as edições próprias ficam em `conteudos-b47/personagem/`. A incorporação do contrato comum foi recebida do integrador, não editada por esta frente. Sem force push, acesso a sessão de outro chat, mensagens automáticas ou agentes.

Na conferência final, a integração avançou para `7752c9115f168effe74092d125dfdd5352bd44a3`. Seu diff foi examinado: dano/Condições, formato 11 inicial e alterações nos três alvos dos patches; o contrato comum de campos/capacidades permaneceu igual. Esse commit não foi mesclado ao ramo da frente. A série adicional `patches/base-7752c91/` foi preparada e testada em cópias desses arquivos exatos, preservando a ordem depois dos produtores comuns e seus transportes/leitor.

## Arquivos e comportamento

| Arquivo | Entrega |
|---|---|
| `b47_personagem/fontes_livro.py` | Leitura dos catálogos canônicos e transcrição explícita de requisitos nomeados |
| `motor.py` | Validação, pools, herança, alcance/área nos dois contextos, consumo, requisitos e custos |
| `planilha.py` | Fórmulas parametrizadas, entradas cruas, auxiliares curtos, validações e exportação |
| `consumidores.py` | Tabelas compatíveis, menus, substituição de referências, identidade herdada, embutidas e consumo |
| `interface.py` | Fachada `aplica/layout/contexto`, cartões, notas, listas compartilhadas e textos que esticam |
| `usos.py` | Avisos nas 12 cartas de Aptidão/Bênção e 12 de Talento; contexto estruturado e conferência manual |
| `transporte.py` | Proposta de arquivos e fatias por colunas, derivadas das células emitidas |
| `fixture_base.py` | Prefixo canônico em memória com bloqueio de escrita externa à área |
| `test_motor.py`, `test_planilha.py`, `test_patches.py` | Casos mecânicos, consumidores reais, preservação, sintaxe e patches |
| `teste-carregamento.js` | Seis ordens de carregamento do template proposto, sem serviços Google |
| `preparar_patches.py`, `patches/` | Preparação reproduzível dos três diffs, sem aplicá-los ao núcleo |
| `validar.py` | Executor focal serial, logs locais ignorados e evidência pequena |

Detalhamento mecânico e divergências de nomes em [CONTRATO-PROPOSTO.md](CONTRATO-PROPOSTO.md); fontes e consumidores em [INVENTARIO.md](INVENTARIO.md). Capacidades adotadas do integrador: 10/10/10, compartilhadas. Livro continua disponível; cadastro inválido sai do menu, mas permanece exportado.

As dez Formas foram comparadas às tabelas reais recebidas nas Classes 0–7, seis degraus e nos dois contextos. O caso de área diferente na Classe 6 da entidade está coberto. Aptidões respeitam aquisição em ordem e consumo/gratuidade; Talentos usam seus custos e lugares atuais. Efeito/requisito livre não gera bônus automático.

## Comandos e resultados

Ambiente: Windows; Python 3.12.14; Node 24.19.0; Git 2.56.0.windows.2. Aproximadamente 3,9 GiB livres na leitura de memória anterior à fixture; trabalhos de modelo executados em série.

1. `git ls-remote --heads`, clone sem checkout, inspeção de refs/histórico e criação do ramo a partir do SHA de preparação. Nenhum ramo de personagem remoto existia inicialmente.
2. `bash nuvem-b47/preparar.sh`, com Python nativo informado em PYTHON e PYTHONUTF8=1: dependências fixadas e diagnóstico passaram. A primeira tentativa de caminho do Bash não existia; usada a instalação Git Bash encontrada pelo executável Git, sem modificar o bootstrap.
3. `python nuvem-b47/conferir.py --smoke`: preparação inicial passou, incluindo 152 fontes Python, 40 JS/GS e catálogo/progressão/Kaori. Smoke de fechamento passou com 166 fontes Python, 41 JS/GS e os mesmos três verificadores; os 20 GS canônicos foram apenas lidos, sem regeneração.
4. `python conteudos-b47/personagem/validar.py --evidencia`: **73 testes passaram, zero falhas/erros**, em 47,0 s do executor sobre `ffaca820b3be591d4985ae00067d22615c516236`. Inclui as duas séries de patches; hashes e detalhes em [VALIDACAO.json](VALIDACAO.json). A rodada anterior de 72 testes em 523e288 também passou.
5. Os testes dos patches fazem `git apply --check` e aplicação em **cópias temporárias dentro desta pasta**, AST Python, sintaxe Node e seis ordens de VM. Não aplicam patches aos caminhos reais do núcleo.
6. `git diff --check` e auditoria do diff contra a base de incorporação: somente a área autorizada.

Resultados cobrem primeira/última vaga dos três tipos; nomes literais e duplicatas; tipo/base incorretos; base e sem base; zero/Não explícitos; requisitos e limites; reuso e limpeza; integridade das mesclas e dos campos anteriores; tabelas de três/quatro faixas; 45/156 destinos nos metadados; 24 avisos de uso; manifesto de células completo; transporte sem perda de colunas. Os testes de sintaxe incluem as fórmulas alteradas nas tabelas reais.

Falhas encontradas e corrigidas, preservadas no histórico de execução local:

- Alias de Cura Classe 0 mostrava prefixo junto a `—`; corrigida a saída indisponível. O teste aponta Forma/contexto/Classe/degrau reais.
- Colisão inicial de nome com `livro.py` do núcleo; os auxiliares passaram a um pacote próprio `b47_personagem`.
- Validação de Forma em `ENSAIO_FORMAS!AD11` chegava a 10.835 caracteres; diagnósticos separados em auxiliares, sem retirar verificações.
- A asserção inicial contava objetos de menu como posições finais; foi substituída por auditoria dos destinos/metadados e conservação dos menus existentes, considerando cópias.
- Uma fixture usava `Condicional` sem escolher Leve/Média; corrigido o dado de entrada para o rótulo publicado, mantendo as expectativas de frequência/limite.
- No ensaio do patch do leitor, corrigido o nome da função chamada pela fixture para `relatorio`; as expectativas de literal e reprovação permaneceram.

Logs extensos estão em `_local/testes.log`, ignorados. A evidência publicada contém resumo e hashes, sem snapshot de jogador.

## Custo medido e limites da prova

As medidas são do modelo/JSON de teste, **não bytes de GS emitidos ou latência nativa**:

| Auxiliar do ensaio | Células | Bytes JSON | Maior fórmula |
|---|---:|---:|---:|
| Formas | 5.944 | 1.094.125 | 774 caracteres |
| Aptidões/Bênçãos | 1.566 | 105.985 | 256 |
| Talentos | 876 | 64.969 | 256 |

Os valores de Formas são propostos em cinco fragmentos por colunas. Cada estimativa de dados fica abaixo de 240.001 bytes; há margem para serialização, mas o integrador deve medir todos os GS finais contra 900.000 bytes. As escadas e os índices são compartilhados entre degraus; nenhuma capacidade de catálogo foi multiplicada pelas 201 posições.

Calc ausente: recálculo de fórmulas impedido. `fcntl` indisponível: agregado POSIX da infra impedido. Sheets/Apps Script e inspeção visual/gatilhos não executados por esta frente. Esses itens não são resultados verdes, e o formato 11 não é declarado implementado.

## Ordem exata para o integrador

1. Receber este ramo e seus commits próprios; conferir diff/base. Incorporar 9dd4c9a → 523e288 → ffaca82 e o fechamento documental, em ordem, ou mesclar preservando o histórico.
2. Ler e conciliar o contrato proposto com `conteudos-b47/comum/`: detalhes de alcance/área, campos TIPO crus, nomes de auxiliares/arquivos, 24 avisos de uso e flags de aprendizado/concessões. O contrato de versão continua sendo decisão conjunta do integrador.
3. Executar o roteiro focal desta pasta. Para 7752c91, revisar/aplicar a série de `patches/base-7752c91/`: 01 → 02 → 03. A série na raiz é somente para a base ae16895; não aplicar as duas. O segundo depende do primeiro. O terceiro preserva textos novos/avisos e prepara LET no cálculo local; não escolhe nova versão.
4. Fechar produtor/leitor/esquema da ANALISE conjunta e executar testes de combinação com Condições/Melhorias e a entrega de entidades. Providenciar revisão cruzada do SHA real desta frente.
5. Gerar canonicamente, medir cada GS, conferir selos/ausências/ordens e adaptar o transporte se necessário. Só então executar [ROTEIRO-NATIVO.md](ROTEIRO-NATIVO.md) com snapshot novo, descartável, restauração e leitura posterior.
6. Integrar no ramo de integração e realizar D dentro do papel do integrador. Esta frente não fez essa integração.

Alvos dos patches: 01 — `ficha-v01/monta.py`; 02 — `ficha-v01/monta.py` e `ficha/modelo.gs.js`; 03 — `ler-analise.py`. Nenhum patch altera GS gerado, bot, oficial, acesso ou main.

As duas séries passaram por aplicação em fixtures e carregamento simulado em seis ordens cada. Isso comprova a aplicação textual/sintaxe das propostas nos dois SHAs, não recálculo ou validação nativa da combinação com dano/Condições.

## Riscos e próxima ação

Revisão cruzada, recálculo Calc/Sheets, equivalência nativa dos novos consumidores e geração final ainda são dependências reais. Campos de história/concessão sem fonte estruturada exigem conferência manual; o código não tenta deduzi-los da descrição. A migração central deve auditar também notas/formatos/validações/alturas, além do manifesto de valores/fórmulas. A organização final da interface é D.

Próxima ação: revisão do SHA publicado e conciliação/incorporação pelo integrador, com **GPT-6.1 Sol, High**, pela interação entre herança, contratos e transporte. Nenhuma escrita Google foi realizada.
