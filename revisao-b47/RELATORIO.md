# Revisão B47 — auditoria inicial da base (chat 2)

**Data:** 16/10/2026 · **SHA auditado:** `4187df37640b5e0966cdb342f56f9ee0a0daf16a` (preparação de nuvem, mesma base de `claude/b47-revisao`, `codex/b47-capacidade`, `codex/b47-infra` e `codex/configuracao-b47` no momento da auditoria).
**Ramo desta entrega:** `claude/kind-feynman-sewhec`. É o nome exigido pela plataforma; foi criado a partir de `origin/claude/b47-revisao` (4187df3), sem reescrever ramo existente. Equivale ao ramo lógico `claude/b47-revisao`.

**Commit da redução (A): revisado** — ver a seção "Revisão do commit A" logo abaixo. As seções seguintes são a auditoria da base 4187df3, feita antes de A existir.

## Revisão da resposta do integrador — topo `8276ca6` de `codex/b47-capacidade`

O integrador incorporou a infra (`b8ab7b5`) e esta revisão (até `38ef85b`) e publicou três commits próprios: `e5871e3`, `f1ff7a6` e `8276ca6`. Revisei o diff do núcleo desde `4610c88` e rodei tudo numa worktree temporária do `8276ca6`. `codex/configuracao-b47` continuava em 4187df3.

| Achado | Estado em `8276ca6` | Como foi conferido |
|---|---|---|
| R1 / A1 sobras de `.gs` | **Resolvido.** Selo de geração no emissor e no carregador, estendido também às abas separadas (`juntarAbas_`), `COMPLEMENTOS_ESPERADOS_`, recusa no `montar_()`, limpeza de sobras na pasta, `abas_cruas` conferindo o selo | `test_carregador.py`: 4/4, incluindo o projeto com sobras da v9 recusado |
| R2 / A2 leitor | **Resolvido.** `aviso.custom.*` não vazio reprova; qualquer valor de erro reprova; `--teste` falha com erro exportado | `test_leitor.py`: 34 ok, 0 falhas |
| B1 nomes no `normaliza` | **Resolvido.** Campos `.nome/.descricao/.efeito/.requisitos/.texto` são lidos como texto | `test_leitor.py`, checagem de leitura do campo de nome |
| R3 colisão do formato 4 | **Registrado** no ESQUEMA (linhas ~249+), com a orientação de confirmar a variante do bot | leitura |
| R4 lotes não atômicos | **Documentado** no manifesto dos lotes (`atomico_entre_lotes: false` e procedimento de falha parcial). `lotes.py` também amplia a grade antes de escrever colunas auxiliares | leitura |
| R5 TIPO apagado | **Resolvido.** Cartão vazio com TIPO em branco não acende aviso; "repetido" só com NOME preenchido | `test_fronteiras.py`: 15/15 |
| R6 `COMPLEMENTOS` fixo | **Resolvido** (1..9) | leitura |
| B3 fórmulas > 8.192 | **Resolvido.** As validações da 3a foram fatiadas em colunas auxiliares (`DADOS_CUSTOM` 285+, partes ≤ 5.000), mantendo mensagens e fontes publicadas; `testar-validacao3a.py` | `test_enderecos.py`: o risco sumiu |
| I2 envio sem remoção | **Resolvido.** `--remover` explícito em `infra-b47/apps_script.py` | `test_infra_envio.py --perfil b47-v10 --ref HEAD`: 4/4 sem patch; 10/10 com os cenários E3 |
| M2–M5, B4 | resolvidos em `2f3c62f` | bateria abaixo |

Resultados em `8276ca6`:
- `bash rodar-tudo.sh --b47-focal`: **23/23 etapas exit 0** em 6 min 33 s, agora incluindo testes da infra, do selo, da validação 3a e as contraprovas desta revisão.
- `bash revisao-b47/rodar.sh b47-v10`: **exit 0**. Contrato 38, leitor 34, endereços 5, carregador 4, peças 55, fronteiras 15, migração 22.
- A regeneração reproduz os `.gs` versionados; só o XLSX muda, por data.

Ajustes que o integrador fez nesta pasta e que adotei: o perfil `b47-v10`; o `--analise` como caminho; a leitura recursiva das mensagens no `test_leitor.py`, necessária com a 3a fatiada; e a checagem de B1 pela leitura real. Eu ajustei o `test_infra_envio.py`: remoto montado da v9, pasta limpa, selo já presente no núcleo e mensagem de recusa sem depender do texto exato.

**Riscos restantes, não bloqueantes:**
- os endereços de catálogo em texto de `INDIRECT` (DADOS_CUSTOM) já são derivados, mas não seriam alcançados por `troca_refs`;
- o "⚠" segue inconsistente entre catálogos, o que é cosmético agora que o leitor reprova qualquer aviso custom;
- B5: `migracao-criacao.py` fora da lista histórica do `NUVEM.md`.

**Parecer:** nada bloqueante da revisão local ficou aberto em `8276ca6`. Integração em `codex/configuracao-b47` liberada do ponto de vista desta revisão. Seguem pendentes, sem que eu possa verificar daqui:
- a aplicação e validação nativas (roteiro: descartável antes da revisão);
- a atualização do bot para o formato 10 e a confirmação da variante do formato 4.

## Revisão do commit A — `2f3c62f` (código) e `4610c88` (registro), ramo `codex/b47-capacidade`

Revisei o diff de `ficha-v01/` (capacidades, custom_*, analise), `ficha/` (emissor e carregador), `ler-analise.py`, `capacidade-b47/migracao.py` e `lotes.py`, além de `ROTEIRO-NATIVO`, `ESQUEMA` e relatório. A bateria rodou numa worktree temporária do `4610c88`. `codex/configuracao-b47` ainda estava em 4187df3, então **não revisei a integração**.

### Reprodução independente das provas do integrador

| Comando no SHA `4610c88` | Resultado |
|---|---|
| `bash rodar-tudo.sh --b47-focal` (14 etapas, 6 min) | **14/14 exit 0**: capacidade 13, migração 19 (sintética), peças 54, progressão 47, treinos 6, Famílias 20, cópias, construção simulada, textos (66 grupos, 7 cenários), leitor `TESTE: OK`. As contagens batem com o relatório deles |
| `monta.py` na worktree | os **20 `.gs` regenerados são iguais byte a byte** aos versionados; no XLSX só muda `docProps/core.xml` (data) |
| `test_contrato.py --perfil alvo-real-separado` | **38/38**: formato 10, 7.356 chaves, 10/30/30/10/10 sem chave acima da capacidade, fontes na CONFIGURAÇÃO sem compartilhamento, **6.706 chaves fora dos catálogos preservadas** com parte, aba e ordem |
| `test_enderecos.py --perfil alvo-real-separado` | 0 falhas. Faixas derivadas (`AG2:AG34`, `AJ2:AJ23`), sem faixa morta, sem nome cru em COUNTIF/MATCH/VLOOKUP. Riscos: endereços derivados ainda em texto de INDIRECT; B3 (25 fórmulas de 11.395 caracteres) |
| `test_pecas_capacidade.py` / `test_fronteiras.py` | 55/55 (o `regressao-pecas.py` deles já é parametrizado) / 13 ok + 2 riscos (R5) |
| `test_carregador.py` | 3/3 com os `.gs` versionados; **falha** com as sobras da v9 no projeto (R1) |
| `test_leitor.py` | 15 falhas bloqueantes (R2 = A2 sem mudança) |

### Achados anteriores resolvidos por A

- **M2:** faixas de Perícia/Ofício e o "—" derivados de `len(livro) + capacidade` (`custom_progressao.py`).
- **M3:** `capacidades.py` deriva `INICIO_FAMILIAS` do fim da progressão; CONFIGURAÇÃO com 1.731 linhas, sem faixa morta.
- **M5:** `criterio()` no cadastro de treino e nas posições da FICHA. `test_fronteiras.py` confirma "Lua*" literal em Perícia e Ofício.
- **M4:** `migracao.py` compara com o molde do gerador, então "Neutra"/"Nenhuma"/falso não contam como dado. Também:
  - bloqueia vaga retirada preenchida, registro parcial, treino sem tipo, excesso por tipo, nota fora de campo e fórmula de entrada movida;
  - exige snapshot de até 15 min, cobertura da cauda da grade e prova descartável;
  - recusa a oficial.
  
  A ordem dos lotes escreve as entradas do jogador por último.
- **B4:** regressões parametrizadas pelas constantes.
- **A1:** em parte. O `construir()` não trava mais: há um só `PecasAnalise`, e os três antigos saíram do Git e do manifesto.

### Achados no commit A

**R1 — ALTA (condicional à aplicação): sobra de `PecasAnalise2–4.gs` no projeto Apps Script corrompe a ANALISE sem aviso.**
- Onde: `ficha/modelo.gs.js`. A redução tirou as guardas 2–4, mas cada complemento antigo termina chamando `juntarValores_` sozinho, e nada recusa um complemento de outra geração. `ROTEIRO-NATIVO.md` passo 7 manda removê-los **à mão**. O relatório deles registra que a sessão não tem ferramenta de Apps Script, então a aplicação tende a ser manual no editor.
- Reproduz: `test_carregador.py --perfil alvo-real-separado` com as sobras da v9. A guarda **passa** e a ANALISE monta 14.222 chaves (240 repetidas, 6.626 obsoletas) numa grade de 7.359.
- Correção validada: `patches/carregador-selo-de-geracao-v10.diff`, rebaseado em `4610c88`. `test_patch_carregador.py --patch carregador-selo-de-geracao-v10.diff`: **7/7**. A pasta gerada constrói com ANALISE = contrato; com sobras, recusa citando os arquivos, e nada delas entra. O patch também amplia `COMPLEMENTOS` de 1 para até 9 (R6).
- Combina com I2: a ferramenta de envio do chat 3 bloqueia os remotos obsoletos sem opção de removê-los (`patches/infra-remover-explicito.diff`).

**R2 — ALTA: A2 continua.** `ler-analise.py` aceita o formato 10, mas segue aprovando avisos de cadastro de Família/Melhoria/Restrição/3a e valores de erro.
- `test_leitor.py --perfil alvo-real-separado`: 15 falhas bloqueantes.
- Correção validada: `patches/ler-analise-avisos-custom-v10.diff`, **31/31** bloqueantes.
- O bot segue sem atualização para o formato 10 (registrado por eles).

**R3 — MÉDIA: M1 parcial.** O ESQUEMA documenta o formato 10 (retiradas, novas chaves, migração), mas não registra que `codex/analise-tr-pericias-carga` usa "formato 4" com outro conteúdo e já foi conferido no bot. Falta a tabela formato → conteúdo e a confirmação do que o bot reconhece.

**R4 — MÉDIA: os lotes de migração não são atômicos entre si.** `lotes.py` limpa `A733:P<fim>` no início e escreve as entradas no fim, em vários `batchUpdate` de até 100 KB.
- Se a aplicação parar no meio (erro, cota, sessão), a cópia fica com os cadastros apagados até reaplicar a partir do snapshot/backup. O `backup_id` torna isso recuperável, mas o roteiro não diz o que fazer em falha parcial.
- Proposta: aplicar limpeza, repintura e entradas da CONFIGURAÇÃO no mesmo `batchUpdate` quando couber, ou registrar no roteiro a retomada obrigatória a partir do backup e o critério de "lote parcial".

**R5 — BAIXA: apagar o TIPO de um cartão vazio de Perícia/Ofício acende quatro avisos.**
- Os avisos são "Tipo incompatível…", "Preencha NOME…", "Nome repetido no livro ou custom" e "Escolha um atributo válido". O "repetido" aparece porque `COUNTIF` com critério vazio conta células em branco. Com "⚠", o leitor e o bot reprovam a ficha.
- Onde: `custom_progressao.py`, fórmula `G{r}`.
- `test_fronteiras.py` reproduz nos dois catálogos. A migração não causa isso, porque os cartões novos vêm do molde com o TIPO preenchido; só a edição manual causa.
- Correção: na condição de "cartão vazio", tratar `B=""` como a categoria e não avaliar repetição com NOME vazio.

**R6 — BAIXA: `ficha/emitir_gs.py` fixa `range(1,2)`.** Se a parte de peças da ANALISE passar de 3.000 linhas (C, com Formas etc.), a geração cai com `KeyError`. A falha é ruidosa, não silenciosa. O patch v10 de R1 amplia.

**Permanecem:** B1 (`normaliza` de nomes), B2 (" · " em nomes), B3 (fórmulas > 8.192 na 3a), B5 (`migracao-criacao.py` fora da lista de receitas históricas do `NUVEM.md`) e o risco de endereços em texto de `INDIRECT`, agora derivados mas ainda imunes a `troca_refs`.

### Parecer sobre A

Mecanicamente, A está consistente com o plano: capacidades centralizadas, contrato 10 coerente e completo, consumidores derivados, migração com guardas fortes e provas reproduzidas aqui. **Integração recomendada**, com duas condições antes da aplicação nativa:
1. R1: o patch do selo (ou equivalente) ou, no mínimo, envio pela ferramenta do chat 3 com remoção explícita e conferência.
2. R2: o patch do leitor e a atualização do bot antes de publicar o formato 10 para jogadores.

R3/R4 pedem decisão ou registro no roteiro; R5/R6 podem ir junto ou depois. Este parecer não cobre validação nativa, que ninguém executou, nem a integração em `codex/configuracao-b47`, que não existia.

## Combinação simulada A + infra + revisão (antes da integração oficial)

`codex/configuracao-b47` continuava em 4187df3. Para antecipar a integração, montei numa worktree temporária: `origin/codex/b47-capacidade` (4610c88) + merge de `origin/codex/b47-infra` (b8ab7b5) + este ramo. Nada foi publicado dessa combinação.

| Verificação | Sem patches | Com os 3 patches propostos* |
|---|---|---|
| Merges | **sem conflito** (as frentes tocam pastas distintas) | — |
| `unittest` de `infra-b47` | OK | 15/15 |
| `infra-b47/executar.py smoke pecas-estrutura textos --permitir-pesados` | 4 etapas executadas | — |
| Manifesto `.gs` da infra × `capacidade-b47/manifesto-gs.json` | **idênticos** (20 arquivos, mesmos hashes, 5.670.234 bytes) | — |
| `test_infra_envio.py --perfil alvo-real-separado --ref HEAD`, com o remoto = projeto v9 atual (23 `.gs`) | a ferramenta **bloqueia** `PecasAnalise2–4` sem opção de removê-los: **o passo 7 do ROTEIRO-NATIVO não tem caminho seguro** (I2 vira impedimento) | 10/10: pacote = gerados + `appsscript`; o projeto resultante constrói com ANALISE = contrato |
| `bash rodar-tudo.sh --b47-focal` (integrador) | 14/14 | **14/14** (6 min 12 s) |
| `bash revisao-b47/rodar.sh alvo-real-separado` | falhas R1, R2 | **exit 0**: contrato 38, leitor 31, endereços 4, carregador 4 (incluindo sobras v9 recusadas), peças 55, fronteiras 13, migração 22; só riscos (R5, B1, B3, INDIRECT) |

\* `carregador-selo-de-geracao-v10.diff`, `ler-analise-avisos-custom-v10.diff` e `infra-remover-explicito.diff`, todos aplicados com `git apply`, seguidos de `python ficha-v01/monta.py`. Os patches mudam 10 `.gs` gerados: selo e lista de complementos esperados.

Pendências para o integrador, além dos patches:
- `infra-b47/MANIFESTO-BASE.json` descreve a v9 (23 arquivos) e deve ser regenerado depois de A.
- O README da infra ainda chama o envio de "regenerar o manifesto após A".

## Ambiente e ferramentas realmente usados

| Item | Estado |
|---|---|
| Python | 3.12.3 no `.venv` (`PYTHON=python3.12 bash nuvem-b47/preparar.sh`; o `python3` padrão é 3.13 e o `preparar.sh` o recusa) |
| Node | v22.22.0 (referência 20; diagnóstico aceita ≥ 18) |
| LibreOffice | 24.2.7.2, presente |
| Recursos | 4 CPUs, 15 GiB, sem swap; trabalhos pesados em série |
| `conferir.py --smoke` | **exit 0**: referências/hashes, 23 `.gs` abaixo do teto, fontes, 115 fontes Python, 38 JS/GS, 3 verificadores |
| Google Sheets/Apps Script | **não usado**. Sem escrita, leitura ou upload. Nenhuma validação nativa feita |
| Bot (Closure's Lab) | fora do repositório; não examinado |

## Achados por gravidade

### ALTA

**A1 — Carregador do Apps Script fixa quatro `PecasAnalise*.gs`; após a redução, o `construir()` trava ou monta a ANALISE com chaves obsoletas.**
- Onde: `ficha-v01/monta.py:503-504` divide a parte de peças da ANALISE em blocos de 3.000 linhas, então a quantidade de arquivos varia com a capacidade. `ficha/emitir_gs.py:455` só conhece 1–4. `ficha/modelo.gs.js:129-132` e `:186-189` juntam CONTRATO_PECAS_1–4; `:334-345` exige os quatro em `montar_()`. `emitir_gs.escrever` (`:706-790`) não apaga arquivos que deixaram de ser gerados. `juntarValores_` (`:144`) aceita qualquer célula ainda ausente, sem conferir origem nem grade.
- Reproduz: `test_carregador.py --perfil simulado-alvo` (geração completa numa worktree temporária, só com as constantes trocadas para 10/30/30/20).
  - Projeto com os arquivos antigos (situação natural do projeto Apps Script, que guarda arquivos até alguém apagá-los): a guarda **passa**. A ANALISE montada fica com 14.222 células de chave, **240 repetidas e 6.626 obsoletas** (ex.: `custom.melhoria.376.nome`), escritas até a linha 18.949 numa aba de 7.359.
  - Projeto sem os arquivos antigos: `Falta o PecasAnalise2.gs`, e o `construir()` não roda.
- Impacto: na descartável, o contrato reduzido sai corrompido de forma silenciosa, com chaves duplicadas e fórmulas para linhas de catálogo que não existem mais; ou a construção fica impossível. Também atinge B (envio/manifesto).
- Correção proposta e **validada fora do núcleo**: `patches/carregador-selo-de-geracao.diff`.
  - O emissor grava `GERACAO_` e `COMPLEMENTOS_ESPERADOS_` no `Ficha.gs`, sela cada complemento e apaga da pasta os complementos não produzidos.
  - O carregador ignora complementos de outra geração, só exige os esperados e recusa construir citando as sobras ("Apague do projeto…"), antes de alterar abas.
  - `test_patch_carregador.py`: simulado-alvo 7/7, com 1 PecasAnalise e sobras recusadas sem entrar na ANALISE; base 5/5, com 4 PecasAnalise. Todos os `.gs` ficam abaixo do teto.
  - Ao aplicar: atualizar `regressao-construir.js:92`, que tem a lista fixa dos arquivos ausentes.

**A2 — `ler-analise.py` (embrião do bot) aprova fichas com cadastro custom inválido e com valores de erro.**
- Onde: `ler-analise.py:90-110` (`relatorio`). Para `aviso.*` fora de `aviso.efeito*`, só acende texto com "⚠", "acima", "falta", "sem treino", "não cumprido" ou "pede ". Os avisos de cadastro dos formatos 8/9 (`aviso.custom.familia/melhoria/restricao.N`) e dos 25 cartões 3a (`aviso.custom.N`) são publicados **sem "⚠"**: `custom_criacao.py:259` e `custom_pecas.py:412-413`. Os de treino e Caminho/Trilha (formato 6) têm "⚠". Valores de erro (`#REF!`, `#N/A`…) nunca são verificados.
- Reproduz: `test_leitor.py`. As mensagens são colhidas das próprias fórmulas geradas: as **5 de Família, 9 de Melhoria e 8 de Restrição** saem "aprovada", assim como os avisos dos cartões 3a. `#REF!` em qualquer aviso custom, em `defesa` ou em `custom.melhoria.1.nome` também sai "aprovada".
- Impacto: são exatamente as chaves que a redução e a migração mexem. Um registro cortado ou mal mapeado que gere aviso, ou um `#REF!` deixado por linha apagada, passa como ficha aprovada. O histórico "TESTE:OK" do leitor não cobria esses casos.
- Correção proposta: `patches/ler-analise-avisos-custom.diff`.
  - `aviso.custom.*` não vazio passa a ser problema.
  - Qualquer valor de erro do Sheets reprova a ficha.
  - `test_leitor.py --com-patch`: 26/26 checagens bloqueantes. **O bot precisa da mesma regra**; não foi possível verificá-lo daqui.

### MÉDIA

**M1 — Versão do contrato: a redução precisa de formato novo, e o número 4 já tem dois sentidos.**
- `ESQUEMA-ANALISE.md:15`: chave não muda de sentido; mudança de regra sobe a versão. A redução retira 11.592 chaves (simulação: 18.948 → 7.356) e exige `formato.versao` > 9. `ler-analise.py:18` só conhece 1–9. `test_contrato.py` faz essa checagem: na simulação acende `formato emitido 9` com chaves retiradas.
- Colisão: `origin/codex/analise-tr-pericias-carga` (0fa4aad, rascunho) emite **formato 4 = TR/perícias/carga**, com chaves inexistentes no v9 (`carga.limite`, `invocacao.N.tr.*.bonus`…). Segundo `VALIDACAO-ANALISE-TR.txt`, esse formato foi **conferido no bot** (502 testes). Na base, o formato 4 são as regras de campanha.
- Recomendação: antes de fixar o número da redução, o integrador confirma com o usuário quais formatos o bot reconhece. Registrar no ESQUEMA uma tabela formato → conteúdo, o destino desse ramo e as chaves descontinuadas. Não decidi o número.

**M2 — Faixas de Perícia/Ofício com número de linha escrito à mão, inclusive em endereços dentro de texto (`INDIRECT`).**
- Onde: `custom_progressao.py:181, 231-238, 242, 297` usam `rg(33,155)`, `rg(36,143)` e `rg(36,144)`, isto é, 23 perícias do livro + 131 vagas e 11 ofícios + 131 vagas. `:153` grava `'—'` fixo em `AJ144`. As faixas viram também texto de `INDIRECT` na DADOS_CUSTOM (375 ocorrências, `custom.py:180,240`).
- Reproduz: `test_enderecos.py --perfil simulado-alvo`.
  - `DADOS_PROGRESSAO!AG2:AG155` aparece em 306 referências, mas os dados terminam na linha 44.
  - `AJ2:AJ144` tem um buraco de 111 linhas, mascarado pelo "—".
  - Na base, as mesmas faixas coincidem com os dados.
- Impacto: menus e validações de Origem 3a, FICHA AMALDIÇOADA e INVOCAÇÕES passam a apontar faixas com sobra. Se a separação Perícia/Ofício mover colunas com `troca_refs` (troca por token, `custom_criacao.py:48-63`), os endereços em texto não são reescritos e ficam velhos em silêncio. Hoje o `str.replace` de `custom_progressao.py:245` ainda os alcança.
- Correção: derivar de `len(livro) + capacidade`, manter o "—" logo após a faixa derivada e gerar o texto do `INDIRECT` da mesma variável.

**M3 — Faixa morta na CONFIGURAÇÃO com Famílias em linha fixa.**
- `custom_criacao.py:21` (`INICIO = 1805`). O código só recusa ficar maior (`:69`). Com 20 registros curtos, a progressão termina na linha 1015 e sobram **788 linhas vazias**, com fundo (`:217-219`) e altura (`:237`).
- O plano A pede retirar alturas, grupos e células excedentes. Derivar `INICIO` do fim da progressão.
- Medido por `test_enderecos.py`. O espaçador de 86 linhas da base (linha 791) é proposital e fica abaixo da tolerância.

**M4 — Migração: o que conta como "dado", a renumeração e a separação Perícia/Ofício.**
- Todo cartão nasce com `estado = Neutra`, `base = Nenhuma` e MESTRE VIU falso. Uma guarda por "célula vazia" acusa os 1.502 cartões de Família, Melhoria e Restrição como preenchidos. Uma guarda que só olha NOME perde registros parciais: o próprio gerador avisa "Preencha NOME" quando há efeito sem nome.
- Treino: as 131 vagas misturam tipos. Separar em 10+10 exige mapa explícito. O mesmo nome como Perícia e Ofício era inválido, porque a checagem de repetição em `custom_progressao.py:132` não distingue tipo, e pode passar a ser válido.
- Entregue: `migracao_guarda.py`, uma proposta de guarda e plano a partir do snapshot da ANALISE, que já exporta o cadastro cru de todos os registros, inclusive inválidos.
  - Bloqueia perda de dado, tipo ausente e referências por nome a cadastro que sumiria (`*.pecas`/`*.restricoes` em listas " · ", `invocacao.N.familia.N`, perícias/ofícios).
  - Mantém o número por padrão; `--compactar` renumera e lista a troca.
  - `test_migracao.py`: 22/22, com padrões conferidos contra o molde real do gerador.
- Não substitui o snapshot nativo integral, que guarda formato e notas, nem a validação em descartável.

**M5 — Nomes com `*`, `?` e `~` em Perícias/Ofícios custom não são literais.**
- Famílias, Melhorias e Restrições escapam com `criterio()`, conforme a decisão dos formatos 8/9. O treino (`custom_progressao.py:132`) e as posições da FICHA (`:387, 394-395`) usam COUNTIF/VLOOKUP crus.
- `test_enderecos.py` acha centenas de usos crus nas posições `personagem.pericia_custom` e `personagem.oficio_custom` (FICHA, DADOS_CONFIG, DADOS_PROGRESSAO) e 393 no próprio cadastro de treino.
- Um nome como `Luta*` passa a casar outros nomes e invalida a vaga. Corrigir junto com a separação.
- **Prova mecânica** (`test_fronteiras.py`, LibreOffice): com "Lua X" na vaga 1 e "Lua*" na última, a Perícia "Lua*" recebe "Nome repetido no livro ou custom" e sai do catálogo. Isso vale na base (vaga 131) e na simulação (vaga 20). A Família, no mesmo caso, trata o nome como literal.

### BAIXA / informativo

- **B1** — `normaliza` (`ler-analise.py:21`) converte nomes: `'007'` → 7, `'1,5'` → 1.5, `'VERDADEIRO'` → 1. Isso muda a impressão digital e faz "1" e "01" colidirem. Recomendação: não normalizar campos de texto (`*.nome`, `*.descricao`, `*.efeito`, `*.requisitos`).
- **B2** — Nenhuma validação impede " · " em nomes, e esse é o separador das listas da ANALISE (`*.pecas`, `*.restricoes`, `.familias`). A guarda avisa.
- **B3** — **A calculadora local nunca validou os avisos dos 25 cartões 3a.**
  - `DADOS_CUSTOM!U2:U26` tem fórmulas de **11.211 caracteres**, acima do limite de 8.192 do xlsx. São as únicas acima do limite, nos dois perfis, segundo `test_enderecos.py`.
  - No LibreOffice, exatamente essas 25 células (e o `S` que as junta) saem `#NAME?`; V, W e X calculam normalmente. A sonda está em `revisao-b47/sonda_libreoffice_name.py`.
  - Prefixar `SWITCH` com `_xlfn.` não muda o resultado. Logo não é função desconhecida; a correlação com o comprimento é exata, mas a causa não foi provada além disso.
  - No Sheets a evidência histórica não registra erro. Localmente, o `#NAME?` ficava invisível por causa do filtro de A2.
  - Recomendação: quebrar a fórmula em colunas auxiliares (fora de A) ou registrar a limitação da calculadora local.
- **B4** — Testes antigos com literais da capacidade atual, a atualizar **a partir das constantes**, não trocando números à mão:
  - `regressao-construir.js:92, 122-128` (1805, 4033, 14306, 877, 131, 318, 789, 395 e a lista de PecasAnalise);
  - `regressao-pecas.py:42, 47, 49, 68, 128, 133, 211`;
  - `regressao-criacao.py:44, 59, 61`;
  - `regressao-progressao.py:36`;
  - `regressao-familias-invocacao.py:67, 74, 93`.
  
  Preservar os casos de primeira/última vaga, negativos e de herança.
- **B5** — `migracao-criacao.py` (raiz) tem o ID da revisão e as linhas 1805+ fixos (`:109-112, 139`), e não consta da lista de receitas históricas do `NUVEM.md:73`. Risco de ser reaproveitado na migração da redução.
- **B6** — `custom_pecas.py:386-387` usa `range(1, len(regs)//2)`. Com capacidade ímpar, o último cartão fica fora das cópias (é emitido explicitamente). Para 30 não há efeito.

## Revisão da frente de infraestrutura (`origin/codex/b47-infra` = `b8ab7b5`)

Revisado por ter interação direta com A1; o resto da frente (executor, recibos) só foi lido. Fora do meu escopo de edição: correções vão como patch para o chat 3/integrador.

**I1 — ALTA em conjunto com A1: o pacote de envio leva as sobras locais ao projeto.**
- Onde: `infra-b47/apps_script.py`, `locais()`, que empacota todo `*.gs` da pasta, e `preparar()`, cuja guarda só olha remotos ausentes localmente.
- Reproduz: `test_infra_envio.py` (E1). Gerando a redução simulada sem o patch de A1, a pasta tem `PecasAnalise1` novo e `PecasAnalise2–4` velhos. O `preparar` aceita e o pacote leva os quatro.
  - O `conferir` posterior daria "igual", porque compara o pacote com a releitura, não com a geração.
  - O projeto resultante é o cenário de A1: 6.626 chaves obsoletas.
- Correção: o patch `carregador-selo-de-geracao.diff` resolve na origem, porque o emissor apaga sobras e declara `COMPLEMENTOS_ESPERADOS_`. O patch abaixo faz a ferramenta conferir essa declaração.

**I2 — MÉDIA: depois da redução, a remoção legítima dos remotos obsoletos fica sem caminho.**
- Com a pasta certa, `preparar` bloqueia "Revisar .gs remotos ausentes localmente" para `PecasAnalise2–4`. A guarda está correta, mas não há opção para autorizar a remoção. O integrador teria de editar o pacote à mão, justamente onde a ferramenta deveria proteger.
- Patch proposto: `patches/infra-remover-explicito.diff`.
  - Cria `--remover NOME`, repetível, aceito só para remotos ausentes localmente e registrado na saída.
  - Recusa `PecasAnalise*` local que o `Ficha.gs` não declara.
- Validação, `test_infra_envio.py --com-patch-infra`, junto do patch de A1: 10 ok.
  - O pacote fica igual aos arquivos gerados + `appsscript`.
  - O projeto resultante constrói e monta a ANALISE = contrato.
  - `--remover Codigo` é recusado; remover uma sobra só ainda bloqueia as outras; sobra recolocada é recusada.
  - O E1 continua falhando de propósito: sem o patch de A1, a ferramenta não tem como distinguir sobra.
- Os 15 testes próprios do chat 3 passam com e sem o patch.

Sem achado: `exportar-baseline.py --destino` existe na base. A guarda de `scriptId`, a preservação de manifesto/HTML, o limite de 900.000 bytes e a proteção de entrada/saída estão coerentes com o plano.

## O que a auditoria confirmou sem achado

Mecânica na capacidade reduzida (simulação, cálculo local no LibreOffice):
- `test_pecas_capacidade.py`: o `regressao-pecas.py` do integrador, só com os literais 789/395 trocados pelas constantes, passa **53/53** checagens mecânicas com 30/30. Isso inclui Melhoria 30 válida, herança da última Restrição (30), sete pares base/custom no personagem e nas entidades, curingas, repetidos, Classe 0 e nona Família da entidade. As 3 checagens que contam o contrato v9 não se aplicam.
  - Calibração na base: 56/56, igual ao original.
  - A troca está em `patches/regressao-pecas-parametrizada.diff` (B4).
- `test_fronteiras.py`: primeira e última vaga de Família (10) e treino (20) válidas e no catálogo; repetido sem diferenciar maiúsculas recusado; treino sem TIPO recusado; Ofício na última vaga entra no catálogo de ofícios. A exceção é o curinga do treino (M5).

Simulação 10/30/30/20, comparada à base pelo `test_contrato.py`:
- As **6.706 chaves fora dos catálogos** se mantêm com a mesma parte, aba de origem e ordem. Isso inclui as nove posições de Família × 12 invocações (`invocacao.N.familia.1–9`), as 23+11 posições custom do personagem, regras, efeitos e 3a.
- Só os 34 `aviso.personagem.*_custom.N` mudam de fonte, pela faixa derivada.
- Contadores de treino (`DADOS!AK13:AK15`) idênticos.
- As referências de DADOS_AM/DADOS_INVOC ao catálogo derivam das constantes (`troca_refs`).
- Os menus de entidade (`DADOS_MELHORIAS` colunas 40+2i) mantêm 12×2.

## Testes, comandos e resultados (SHA 4187df3)

| Comando | Natureza | Resultado |
|---|---|---|
| `bash nuvem-b47/preparar.sh` (Python 3.12) / `conferir.py --smoke` | preparação | ok / exit 0 |
| `nuvem-b47/exportar-baseline.py` | gerador real | ok, 12 s |
| `test_contrato.py --perfil base-v9` | teste novo, gerador real | 32/32 |
| `test_contrato.py --perfil simulado-alvo` | **simulação** | 31 ok, 2 falhas (versão do formato) — esperado, M1 |
| `test_leitor.py` | teste novo, gerador real + leitor real | 12 ok, 14 falhas bloqueantes — A2 |
| `test_leitor.py --com-patch` | patch proposto | 26/26 bloqueantes; 4 riscos (B1, padrão do ⚠) |
| `test_enderecos.py --perfil base-v9` | teste novo | 0 falhas; 3 riscos (texto em INDIRECT, M5, fórmulas > 8.192) |
| `test_enderecos.py --perfil simulado-alvo` | **simulação** | 1 falha (M2); 5 riscos (M2 buraco/texto, M3 faixa morta de 788 linhas, M5, B3) |
| `test_carregador.py --perfil base-v9` | `.gs` versionados em VM | 3/3 |
| `test_carregador.py --perfil simulado-alvo` | **simulação** em worktree | 4 falhas — A1 |
| `test_patch_carregador.py` (simulado / base) | patch proposto em worktree | 7/7 e 5/5 |
| `test_migracao.py` | guarda proposta | 22/22 |
| `test_pecas_capacidade.py --perfil base-v9` / `simulado-alvo` | regressão do integrador parametrizada, LibreOffice | 56/56 / 53 ok (3 do contrato v9 não se aplicam) |
| `test_fronteiras.py --perfil base-v9` / `simulado-alvo` | teste novo, LibreOffice | 8 ok + 1 risco (M5) / 8 ok + 1 risco (M5) |
| `test_infra_envio.py` (ferramenta do chat 3 em `b8ab7b5`) | **simulação** + snapshot remoto falso | 3 ok, 1 falha (I1), 1 risco (I2) |
| `test_infra_envio.py --com-patch-infra` | patches propostos de A1 + I2 | 10 ok, 1 falha (E1 sem o patch de A1, esperada) |
| `unittest` de `infra-b47` em worktree de `b8ab7b5`, sem e com o patch | testes do chat 3 | 15/15 e 15/15 |
| leitor com patch sobre `ficha-projeto-m-0.1.xlsx` recalculado no LibreOffice (2 min 30 s) | calculadora local | REPROVADA com 26 avisos: o esperado da ficha vazia (faltam perícias) + 25 `#NAME?` de B3, que o leitor atual esconde |
| `bash revisao-b47/rodar.sh base-v9` / `simulado-alvo` | bateria em série | exit 1 / exit 1 (falhas acima; logs `bateria-*.log`) |

Os resultados JSON de cada teste estão em `nuvem-b47/saidas/revisao-b47/` (não versionados).
- **Simulação** = só as constantes trocadas; não é a implementação de A.
- **Evidência histórica** = `referencias-b47/evidencias`, `VALIDACAO.json` e relatórios anteriores; nada aqui as repete nem as valida.
- **Sem acesso nativo:** nenhuma checagem foi feita no Sheets/Apps Script.

## Impedimentos

- Commit A revisado (`2f3c62f`/`4610c88`); a integração em `codex/configuracao-b47` ainda não existia.
- Sem Google: migração, envio, construção e leitura nativa não testados.
- Bot fora do repositório: a compatibilidade dele com A2/M1 não foi verificada.
- `regressao-construir.js` e a bateria antiga não foram rodados, por estarem fora do escopo deste papel e serem pesados. A preparação já registrou a execução deles na base.

## Critérios para integrar A (proposta)

1. `test_contrato.py --perfil <alvo-real-…>`, com o perfil ajustado ao contrato publicado: sem falhas. Formato novo e registrado no ESQUEMA; nenhuma chave acima da capacidade; fontes na CONFIGURAÇÃO sem compartilhamento; 6.706 chaves preservadas com ordem.
2. `test_carregador.py --perfil <alvo-real-…>` sobre os `.gs` regenerados: guarda passa e ANALISE montada = contrato. A1 corrigido, por este patch ou equivalente. Envio pela ferramenta do chat 3 com remoção explícita dos `PecasAnalise*` obsoletos (I2) e conferência contra o que a geração declarou (I1).
3. Leitor corrigido (A2), conhecendo o formato novo; bot atualizado ou explicitamente pendente.
4. `test_enderecos.py`: nenhuma faixa além dos dados; endereços de `INDIRECT` derivados; nenhuma faixa morta acima de 100 linhas.
5. Migração: snapshot atual da revisão e plano sem bloqueios (`migracao_guarda.py` ou equivalente) antes da descartável; descartável antes da revisão.
6. Regressões antigas parametrizadas pelas constantes, com casos negativos, primeira/última vaga, herança, nomes literais e reutilização.

## Parecer

Restrito ao que examinei: código do gerador, carregador e leitor em 4187df3, simulação local da redução e testes novos. Encontrei **dois problemas altos que quebram a redução mesmo com as constantes corretas** (A1, A2) e quatro médios que pedem decisão ou derivação. Isso não é revisão do commit A, nem validação nativa, nem auditoria final completa.
