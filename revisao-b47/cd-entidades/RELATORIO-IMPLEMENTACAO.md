# B47 C+D · Tipos e Talentos de entidade · relatório de implementação (frente Claude)

16/10/2026. Sem escrita no Google, Apps Script remoto, ficha oficial, bot ou acessos. Nada do núcleo foi
editado neste ramo: as mudanças fora de `revisao-b47/cd-entidades/` estão em patches.

## Objetivo e escopo

Implementar os moldes aprovados `TIPO DE ENTIDADE` e `TALENTO · ENTIDADE`
(`mockup/prototipo_custom_3c_restante.py`) como módulo do gerador, com testes:

- **Tipos**: base do livro opcional; VIDA (Normal/Corpo de criação), TALISMÃ (Não usa/Usa) e RESERVA DE PE
  (Normal/Maldição domada) funcionam como três chaves independentes. Em branco herdam a base válida; sem
  base valem o normal. Valor explícito sobrescreve a base. Autonomia e alma continuam na invocação.
- **Talentos**: base opcional, CATEGORIA 1–3 (herda da base; sem base é obrigatória), requisitos e efeito em
  texto. Orçamento, abertura por nível, teto por ganho e Trilha só com CE 1 continuam sendo as contas
  existentes da ficha, agora sobre o catálogo livro + custom válido.
- **Consumidores**: as 12 invocações usam o catálogo unido nos menus e nas buscas. As três comparações por
  nome de tipo viram consulta aos funcionamentos efetivos. As 9 Famílias, limites, alma e autonomia não
  mudam (provado célula a célula).
- Fora do escopo, por instrução: Formas (outro Codex), Tipos de dano/Condições/D (integrador) e
  redesenho de interface.

## Base, ramo e SHAs

| | |
|---|---|
| Ramo | `claude/b47-cd-entidades` |
| Base inicial registrada | `0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd` (plano C+D; `dce00ab` ancestral) |
| Avanço sem reescrita | fast-forward para `ae16895` (contrato comum); merge de `7752c91` (dano/Condições) em `df917d5` |
| Núcleo testado | árvore de `7752c91` (`codex/configuracao-b47`) + os patches desta pasta |
| Commits desta frente | `50bcc00` (módulo e testes), `8b5913f` (patches e conferidor), este commit (documentos e patch 03) |

## Entregáveis e ordem de incorporação

1. `patches/02-copias-de-complemento.patch`: correção do carregador JS. É independente e pode entrar
   antes de tudo (ver achado A).
2. `patches/01-entidades-no-gerador.patch`: `ficha-v01/entidades_custom.py` (cópia idêntica do módulo
   desta pasta) e `monta.py` (depois de `custom_danos`: aplica, junta antes/depois, exporta ANALISE no fim
   e entra em `--exportar-pecas`). Inclui também `emitir_gs.py` (`Entidades.gs` com `ABAS_DAS_ENTIDADES`,
   `EntidadesPainel.gs` com `VALORES_ENTIDADES_`), `modelo.gs.js` (ordem das abas, junções, guarda
   "Falta o Entidades.gs") e `regressao-construir.js` (ausência dos dois arquivos).
3. `patches/03-testes-comuns-com-entidades.patch`: `testar-carregamento.js` tira abas/chaves do modelo, e
   `testar-comuns.py` separa as chaves de entidade, mantendo exatas as 7436 + 80 de dano/Condições.

Depois de aplicar: regenerar os `.gs` pelo fluxo do integrador. Contrato e divergências em
[PROPOSTA-CONTRATO.md](PROPOSTA-CONTRATO.md); roteiro nativo em [ROTEIRO-NATIVO.md](ROTEIRO-NATIVO.md).

## Contrato esperado (resumo)

10 tipos × `nome, mestre_viu, base, vida, talisma, reserva_pe, definicao, efeito` + aviso, e 20 talentos ×
`nome, mestre_viu, base, categoria, requisitos, efeito` + aviso: **230 chaves** novas no fim da ANALISE.
As 7436 da base ficam idênticas e na mesma ordem. Aba oculta `DADOS_ENTIDADES` com 37 × 38 células.
Cartões na CONFIGURAÇÃO depois do fim calculado da seção anterior (na geração conferida, 1875–2299;
derivado, não fixo). Na DADOS_INVOC, 228 referências trocadas e 12/12 comparações de cada tipo
substituídas.

## Comandos e resultados (Linux, Python 3.12 venv, Node 22, LibreOffice 24.2)

| Comando | Resultado |
|---|---|
| `nuvem-b47/conferir.py --smoke` | OK: 163 fontes Python, 44 JS/GS, catálogo/progressão/Kaori |
| `test_entidades_mecanica.py` (10/20, Calc local) | **35/35** |
| `test_entidades_mecanica.py --tipos 1 --talentos 1` | recusado de propósito (cenários usam 6/10) |
| `test_entidades_estrutura.py` (10x20, 5x7, 1x1) | **51/51** |
| `conferir_patches.py --regressao` (02 → 01 → 03) | **13 ok, 1 risco preexistente** (achado B) |
| `conferir_patches.py --so 02` | 4/4: carregador JS = Python em todas as abas na base |
| `conferir_patches.py --so 01` (01 → 03) | 10 ok, 1 risco: sem o 02, a lacuna da base continua (1296 células) |
| `testar-comuns.py` (integrador), com 01+03, base pré-dano `ae16895` | 10/10 (sem os patches: 10/10) |
| `testar-carregamento.js` (integrador), com 01+03 | OK, 8 ordens, 19 abas, 7666 chaves |

A mecânica cobre:

- **Herança:** com base, sem base e sobrescrita (`Não usa` sobre base que usa).
- **Combinações independentes:** cada uma das três chaves isolada e a combinação Domada + Corpo de criação.
- **Vagas:** primeira e última, de tipo e de talento.
- **Inválidos:** duplicatas (livro, custom, maiúsculas), nome ausente, base inexistente, CE fora de 1–3.
- **Nomes literais:** `Lua*` e `Ru*na`, com contraprova de que o curinga casaria sem escape.
- **Talentos:** orçamento e excesso, abertura e teto por ganho, Trilha só com CE 1, mesmo talento nas
  12 invocações.
- **Cartões vazios:** sem aviso.
- **Regressão:** com catálogos vazios, as 2016 células das 12 fichas da DADOS_INVOC são iguais ao gerador
  sem o módulo, e alma, autonomia e Famílias também.

A geração completa só rodou em worktrees temporárias. Nenhuma saída canônica do checkout foi regravada, e
todos os 24 `.gs` ficaram abaixo de 900.000 bytes (maior: `Analise.gs`, 816.379).

## Testes impedidos

- **Todo o roteiro nativo** ([ROTEIRO-NATIVO.md](ROTEIRO-NATIVO.md)): sem conta Google por instrução.
  Inclui a confirmação nativa do achado A em `construir()` de cópia nova.
- **Bot**: externo, não tocado.

## Achados para o integrador

**A. Alta: o carregador JS perde valores de cartões copiados quando o molde chega por complemento.** É
anterior a esta frente. O `juntarAbas_` expande `copias` assim que a CONFIGURAÇÃO entra, mas os valores do
molde estão em `PecasPainel.gs`/`CriacaoPainel.gs`/`DanosPainel.gs` e chegam depois pelo `juntarValores_`,
que não os copia. O `compactar` já tinha tirado as células repetidas. A referência Python
(`emitir_gs.abas_do_script`) junta antes e expande depois, por isso os testes Python passam. A regressão JS
compara JS com JS e também não vê. Medido nos `.gs` versionados de `ae16895`: 1232 células ausentes
(Famílias 336 em 953–1007, Melhorias 504 em 1037–1399, Restrições 392 em 1426–1732; rótulos `TIPO`,
`NOME`, `MESTRE VIU`, `ESTADO`, padrões e caixas). Em `7752c91`: 1296 (+64 de Danos). O efeito esperado é
`construir()` de cópia nova sem esses rótulos a partir do 2º par de cartões. As cópias migradas por lotes
não passam pelo carregador. **Isso não foi verificado no Google.** O patch 02 resolve: carregador JS = Python
em todas as abas, em três ordens, e a regressão JS não ganha falha. Reproduzir:
`node sonda_carregador_copias.js apps-script <ref.json>` depois de `referencia_carregador.py`.

**B. Média: `regressao-construir.js` falha na base `7752c91`.** O simulador para em
`INDIRECT(IF('CONFIGURAÇÃO'!B1013="Condição",…))` (menu de Condição). A falha é idêntica com ou sem os
patches desta frente. Pode ser limitação do simulador, já que houve prova focal nativa, mas hoje a
regressão principal fica vermelha.

**C. Baixa.** A lista de ausências de `regressao-construir.js` não inclui `Danos.gs`/`DanosPainel.gs`,
cobertos pelo `testar-carregamento.js`. Os testes comuns fixavam contagens (18 abas, 7436), e o patch 03 trata.

## Riscos e dependências

- **Migração por lotes** (`capacidade-b47/migracao.py`): não conhece `DADOS_ENTIDADES` nem o bloco novo. Fichas
  existentes precisam de lote próprio, decisão do integrador.
- **Texto do tipo:** não aparece na invocação, que não tem área para isso (ver PROPOSTA-CONTRATO).
- **Formas** (outro Codex): só dividem a CONFIGURAÇÃO. A ordem no `monta.py` decide a posição; os endereços
  são derivados.
- **`copias` nos cartões de entidade:** ficou de fora até o patch 02 entrar.
- **Capacidades:** sugerido `TIPOS_ENTIDADE`/`TALENTOS_ENTIDADE` em `capacidades.py`.

## Revisão cruzada

`codex/b47-cd-personagem` apareceu em `e9af8d3` às 22:19 UTC, depois desta implementação. A revisão vai
num relatório separado nesta pasta.

## Próxima ação

Integrador: aplicar 02 → 01 → 03 num ramo de tarefa, rodar `conferir_patches.py --base <ramo> --regressao`,
regenerar os `.gs` e seguir o roteiro nativo na descartável, começando por `construir()` do zero (achado A).
Recomendação: o modelo do integrador em esforço High, porque é integração com o núcleo e com o contrato.
