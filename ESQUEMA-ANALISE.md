> **Retomada B47 — 16/10/2026:** gerador local no formato **10**, com **7.356 chaves**; revisão nativa ainda no **9**, com **18.948**. Consulte “Formato 10” ao final para a retirada explícita de chaves, fontes e migração. As seções anteriores registram versões históricas. Rota vigente: [PLANO-RETOMADA-B47.md](PLANO-RETOMADA-B47.md).

# O esquema da aba ANALISE (o "contrato" com o bot)

Rascunho de 14/10/2026, tirado da ficha do commit `547eb3f` (B46 em andamento): o índice da FICHA (DADOS, colunas BA e
BB), o índice da FICHA PESSOAL (DADOS, colunas DO e DP), e as tabelas das abas ocultas DADOS_AM (uma linha por feitiço)
e DADOS_INVOC (uma linha por invocação). A ficha já calcula quase tudo isto: a ANALISE só junta num lugar, com chave fixa.

## Formato

- Quatro colunas: **A chave · B valor · C célula · D parte**. Linha 1: os cabeçalhos. Linha 2 em diante: os dados.
- A chave é minúscula, sem acento, com ponto entre os níveis e o número do item quando há lista: `feitico.7.peca.2`.
- O valor sai como texto: número com ponto decimal, `VERDADEIRO`/`FALSO` viram `1`/`0`, e lista sai separada por ` · `.
- Célula vazia sai vazia. O bot trata vazio e ausente do mesmo jeito.
- Nunca se reaproveita uma chave com outro sentido: se a regra mudar, entra uma chave nova e `formato.versao` sobe.

## Partes

### 1. cabeçalho
| chave | o que é |
|---|---|
| `formato.versao` | a versão deste esquema (começa em 1) |
| `ficha.versao` | `DADOS!B1` (hoje 1.0) |
| `ficha.livro` | o livro de onde a ficha saiu (R51) |
| `ficha.sistema` | `DADOS!F1` (Ciclo Maldito) |

### 2. entradas (o que o jogador escolheu)
| grupo | chaves | de onde |
|---|---|---|
| identidade | `nome`, `caminho`, `trilha`, `origem`, `nivel`, `xp`, `grau` | índice da FICHA e da FICHA PESSOAL |
| atributos | `atributo.<nome>.base`, `atributo.<nome>.corpo` (5 cada) | `atr_base_*`, `corpo_*` |
| marcos | `marco.corpo`, `marco.leque`, `marco.refino`, `marcos.escolhidos` | `marco corpo`, `marco leque`, `refino escolhido` |
| treinos | `pericia.<nome>.treino`, `pericia.<nome>.especialista`, `oficio.<nome>.treino`, `tr.<nome>.treino` | a lista de perícias da FICHA |
| armas | `treino.arma.<categoria>`, `treino.grupo.<grupo>` | a área "treino" da FICHA PESSOAL |
| Origem | `origem.marcante`, `origem.menor.1`, `origem.menor.2`, `origem.marcante.texto`, `origem.menor.N.texto`, `origem.oficio_compativel`, `origem.ce4`, `origem.legados` | índice da FICHA PESSOAL (B46) |
| estado | `sequela.1..3`, `exaustao`, `resistencias`, `imunidades` | índice da FICHA |
| buff | `buff.<caixa>` (vida, energia, integridade, defesa, proteção, iniciativa, CD, conjuração, corpo a corpo, à distância, deslocamento, carga) | índice da FICHA |
| equipamento | `em_uso.principal`, `em_uso.secundaria`, `em_uso.vestindo`, `equipavel.N.nome`, `equipavel.N.grau`, `item.N.nome`, `item.N.qtd` | FICHA PESSOAL |
| missões | `missao.N.tipo`, `missao.N.adicional`, `missao.N.desconto`, `missao.N.xp` | FICHA PESSOAL (4 blocos) |
| técnica | `tecnica.rota`, `tecnica.familias.livres`, `tecnica.familias.fechadas`, `tecnica.semente` | DADOS_AM |
| feitiços | `feitico.N.classe`, `.nome`, `.forma`, `.peca.1..4`, `.restricao.1..2`, `.liberacao` | DADOS_AM, "conta de feitiço" (36 lugares) |
| Classe 0 | `classe0.N.forma`, `.melhoria`, `.restricao` | DADOS_AM |
| passivas e aptidões | `passiva.N.nome`, `aptidao.N.nome` | DADOS_AM, cartas |
| domínio | `dominio.degrau`, `dominio.espacos` | FICHA AMALDIÇOADA |
| pactos | `pacto.N.nome`, `.forma`, `.modifica`, `.tamanho`, `.dou`, `.recebo`, `.clausula` | FICHA AMALDIÇOADA (3 lugares) |
| invocações | `invocacao.N.nome`, `.tipo`, `.aquisicao`, `.nivel_fixo`, `.talisma`, `.oficio`, `.ponto.<atributo>`, `.familia.1..5`, `.pericia.1..7`, `.talento.1..8`, `.feitico.K.*` | DADOS_INVOC, "conta de ficha" (12 fichas) |
| habilidades | `habilidade.N.nivel`, `.nome`, `.livre` | cartas da seção 7 da FICHA |

### 3. configuração (B47)
| chave | o que é |
|---|---|
| `regra.<nome>` | o valor EM USO de cada regra de campanha (nível inicial, pontos de atributo, teto, vida por nível, curva de XP, morte permanente, deslocamento base...) |
| `regra.<nome>.campanha` | o que o jogador escreveu em CAMPANHA (vazio = livro) |
| `efeito.N.ligado`, `.caixa`, `.como`, `.valor`, `.tipo_de_fonte`, `.fonte` | seis campos separados por efeito; N de 1 a 30, parte `configuração` |
| `custom.N.tipo`, `custom.N.nome`, `custom.N.mestre_viu` | a lista do conteúdo custom |
| `custom.N.campo.<nome>` | cada campo do molde do item (para o bot tirar a impressão digital do texto) |

### 4. resultados (o que a ficha calculou)
`vida.max`, `energia.max`, `integridade.max`, `defesa`, `protecao`, `iniciativa`, `cd`, `conjuracao`, `corpo_a_corpo`,
`a_distancia`, `maestria`, `deslocamento`, `espacos_de_feitico`, `classe.maxima`, `refino`, `carga`, `carga.limite`,
`xp.total`, `morrendo.aguentar`, `morrendo.insistir.1`, `morrendo.insistir.2`, `morrendo.prazo`, e de cada feitiço
`feitico.N.pe`, `.dano`, `.alcance`, `.resolve`, e de cada invocação `invocacao.N.nivel`, `.classe`, `.vida.max`,
`.entrada`, `.retorno`.

### 5. avisos (o primeiro filtro)
A ficha já marca o que passou do limite. Cada aviso vira uma chave, vazia quando está tudo certo:
- `aviso.pontos_de_atributo`, `aviso.pericias`, `aviso.oficios`, `aviso.testes`: os X de Y da FICHA;
- `aviso.aptidoes`, `aviso.passivas`, `aviso.vagas_de_pacto`: FICHA AMALDIÇOADA;
- `feitico.N.erros`, `feitico.N.avisos`: as colunas `erros` e `avisos` que a DADOS_AM já calcula por feitiço;
- `invocacao.N.erros`, `invocacao.N.avisos`: o mesmo na DADOS_INVOC;
- `aviso.forca.principal`, `aviso.forca.secundaria`, `aviso.forca.vestindo`, `aviso.grau`, `aviso.carga`: FICHA PESSOAL;
- `aviso.origem.menor_repetida`, `aviso.origem.menor_de_outra_origem`: B47, contas novas.

## A ordem de leitura do bot

1. Confere `formato.versao`. Se não conhece a versão, para e avisa.
2. Compara cada `regra.*` com a campanha cadastrada nele.
3. Para cada `custom.N`, monta a impressão digital (o tipo, o nome e os campos, normalizados) e procura nos aprovados.
4. Refaz as contas a partir das entradas e compara com os resultados.
5. Junta os avisos.
6. Responde no chat: aprovada, pendente do mestre ou reprovada, com a lista.

## Em aberto

- O tamanho: com 36 feitiços × 12 campos, 12 invocações × 40 e o resto, passa de 1.500 linhas. É fórmula de referência,
  barata, mas entra no tempo do `construir()`. Medir na construção.

## Decidido

- O nome da aba é **ANALISE**, sem acento (o Mizuki, 14/10/2026: "sem acento"). O endereço do CSV fica sem codificação.

## Implementação de bônus e mudanças · 14/10/2026

O gerador parte do `main` atualizado em `15e0af9`, que já incorpora a ANALISE 2. O contrato desta etapa é **formato 3**, pois resultados podem passar a incluir efeitos. São **5.156 chaves**: as 4.896 anteriores preservadas, 180 campos dos 30 efeitos, 30 avisos individuais (`aviso.efeito.N`) e 50 avisos por caixa (`aviso.efeito_caixa.<nome>`).

`ligado` sai como texto `1`/`0`; `valor` sai como texto numérico, com a pontuação decimal da localidade. `como` aceita `somar` ou `trocar por`. Fontes: Pacto, Origem, Origem custom, Item, Técnica ou Decisão do mestre. O nome da fonte é obrigatório quando ligado; isso registra a justificativa, não equivale à aprovação pelo mestre.

Somar acumula com a conta e o Buff/Debuff existente. Trocar por fixa o resultado final, inclusive zero, sobrepondo todos os bônus. Duas trocas da mesma caixa geram conflito. Uma entrada ligada inválida gera aviso e impede um resultado silenciosamente aceito; linha desligada não altera a conta. A CONFIGURAÇÃO permanece em Mizuki Escuro, fora das trocas de paleta.

Na etapa de bônus registrada acima, `regra.*` e `custom.*` ainda eram planejamento. O formato 4 abaixo já emite as regras; custom continua planejado. O bot deve reconhecer e conferir os efeitos do formato 3 antes de publicar a ficha para jogadores.

[Cópia nativa para revisão](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit). A base do servidor consultada ainda tinha ANALISE 1; cópias de validação do bot já continham ANALISE 2. A revisão preserva a apresentação da base e recebe o contrato atualizado, sem importar XLSX. A oficial não foi alterada.

## Regras de campanha — formato 4 (15/10/2026, validado na cópia de revisão)

O formato passa a **4**, com **5.274 chaves**: as 5.156 anteriores preservadas e 118 novas. Os novos campos são:

- `regra.<nome>` e `regra.<nome>.campanha`, para 14 parâmetros: `nivel_inicial`, `atributos_pontos`, `atributos_teto_criacao`, `atributos_teto`, `pericias_com_oficio`, `oficios_criacao`, `pericias_sem_oficio`, `deslocamento_base`, `morrendo_aguentar`, `morrendo_insistir_1`, `morrendo_insistir_2`, `morrendo_teto`, `morrendo_prazo`, `vida_rolada`.
- `regra.xp.N` e `regra.xp.N.campanha`, para N de 1 a 29: custo para sair do nível N. O nível 30 encerra a progressão. O livro não define o custo 1→2; vazio não deve virar zero.
- `vida.rolagem.N`, para N de 2 a 30: resultado do dado guardado, sem Constituição. Primeiro nível conserva a vida inicial fixa do Caminho.
- `sequela.extras`: quantidade além das três caixas de marcar. Descanso longo zera caixas e extras; curto conserva.
- `aviso.regras_campanha` e `aviso.vida_rolada`: avisos das entradas inválidas/incompletas.

Os campos `.campanha` vazios usam o livro; zero é uma entrada explícita. Os valores são texto, com a pontuação decimal da localidade, como nos formatos anteriores. `vida_rolada` usa Sim/Não. As frações de Morrendo são números (1/4 = 0,25), não texto para avaliar.

**XP zero corresponde ao nível inicial da campanha**, por decisão do usuário. O nível continua editável manualmente; a fórmula inicial apenas acompanha a configuração enquanto não for substituída. A tabela DADOS lê os acumulados ajustados. A subida por missão/XP mantém o comportamento anterior e o Limiar do nível 20.

Vida rolada: vida inicial fixa + Constituição por nível + resultados guardados dos níveis seguintes + Buff/Debuff. Mantém a prioridade dos efeitos: trocar por fixa o resultado final, incluindo zero. Rolagem exigida ausente ou fora do dado do Caminho produz aviso/erro visível, nunca um resultado aleatório ou zero presumido.

**Morte permanente foi retirada da interface e das chaves**, por pedido do usuário: não há automação na ficha que use esse registro. A regra pode continuar no cadastro da campanha do bot; este contrato não emite `regra.morte_permanente`.

O bot precisa reconhecer o formato 4 e conferir as regras/rolagens antes da publicação para jogadores. Validação local e testes na cópia nativa concluídos: 5.274 chaves únicas, sem erros de fórmula, dados temporários restaurados. Isso não equivale à publicação na ficha oficial.


## Conteúdo custom — formato 5 (15/10/2026)

São **6.174 chaves**: as 5.274 do formato 4 foram preservadas e entram 900 chaves para os 25 cartões da parte 3a. Os cartões ocupam CONFIGURAÇÃO J:O, com 29 linhas por registro. O cadastro cru é exportado mesmo quando inválido; só definições válidas entram nos catálogos que alimentam a ficha.

Para cada N de 1 a 25: `custom.N.tipo`, `.nome`, `.mestre_viu`, `.efeito`, `.campo.<nome>` e `aviso.custom.N`. As 31 chaves semânticas de campo são fixas, inclusive quando não utilizadas pelo tipo: campo não utilizado sai vazio. Números continuam texto, na localidade da planilha; zero é explícito. MESTRE VIU sai 1/0 e é apenas lembrete do jogador. A ficha não atesta aprovação; essa conferência continua pertencendo ao bot, no chat.

Tipos da 3a: Origem, Marcante, Menor, Arma, Escudo, Uniforme, Item comum e Ferramenta amaldiçoada. Ferramenta deriva de uma base do livro ou de um registro básico válido; não deriva de outra ferramenta. Campos numéricos alimentam as contas próprias. Texto de efeito nunca é interpretado automaticamente como bônus: alterações adicionais vão em BÔNUS E MUDANÇAS.

Origem oferece quatro opções distintas de perícia, rota, BASE DO LIVRO opcional, ofício e registro de CE4. BASE DO LIVRO = Nenhuma (ou vazia) conserva a criação do zero aprovada pelo usuário. Uma base existente herda seu funcionamento e suas marcantes publicadas. As quatro rotas são Fundamento, Manejos, Técnica Marcial com energia e Técnica Marcial sem energia. Sem energia conserva PE como Pontos de Esforço.

**Correção R52, páginas 95 e 99–100:** menores e Legados de história podem ser personalizados; marcantes de Origens do livro seguem as opções publicadas, inclusive para famílias próprias do Descendente. Restrição Celestial · Restrição corporal conserva sua criação específica. O usuário confirmou separadamente que Origens inteiramente homebrew do zero podem ter marcante própria. Um registro de marcante ligado a uma base do livro sem essa permissão é diagnosticado e excluído dos menus; seleções antigas incompatíveis mostram aviso. Essa correção pontual não declara todo o catálogo migrado da R51 para R52.

A integração com o bot precisa reconhecer formato 5 e conferir os registros e as regras. O bot e a ficha oficial não foram alterados nesta etapa. Partes 3b/3c aguardam teste do usuário na 3a.


## Caminho, Trilha, perícia e ofício custom — formato 6 (15/10/2026)

São **7.387 chaves**: todas as 6.174 anteriores permanecem na mesma ordem e com as quatro colunas preservadas, exceto formato.versao, agora 6. Entram 1.213 chaves; valores e números continuam texto na localidade da planilha.

- `custom.caminho.nome`, `.mestre_viu`, `.efeito`, `.campo.<nome>`: números, atributos naturais, duas perícias fixas e treino de arma; `.nivel.N.nome/.texto`, N de 1 a 30.
- `custom.trilha.nome`, `.mestre_viu`, `.efeito`, `.campo.caminho`, `.campo.base_do_livro` e os mesmos pares por nível. BASE DO LIVRO é opcional: Nenhuma usa criação própria; uma base existente herda apenas suas automações. Texto não concede números automaticamente.
- `custom.treino.N.tipo/.nome/.mestre_viu/.atributo/.efeito`, N de 1 a 131, em registros compartilhados de Perícia/Ofício. Atributo fixo para perícia, padrão editável no personagem para ofício.
- `personagem.pericia_custom.N.<campo>`, N de 1 a 23; `personagem.oficio_custom.N.<campo>`, N de 1 a 11. Campos: nome, treino, especializacao, atributo, resultado e bonus. Treinos/especializações entram nos orçamentos existentes; não são escolhas adicionais.
- `aviso.custom.caminho`, `aviso.custom.trilha`, `aviso.custom.treino.N`, `aviso.personagem.pericia_custom.N`, `aviso.personagem.oficio_custom.N`; avisos de efeitos por linha em `aviso.efeito_caixa.pericia_custom.N` e `.oficio_custom.N`.
- `aviso.efeito_caixa.invocacoes.teto_de_ativas` e `.familias_da_trilha`: dois alvos novos de BÔNUS E MUDANÇAS para Trilhas próprias.

Cadastros crus continuam exportados mesmo inválidos; apenas definições válidas aparecem nos catálogos. Nome repetido com livro/custom, número inválido ou atributo inexistente gera aviso. MESTRE VIU continua sendo lembrete, sem representar aprovação.

Capacidade: 1 Caminho + 1 Trilha + 131 registros curtos (108 posições independentes de perícia e 23 de ofício, incluindo entidades e Ficha Amaldiçoada). Somados aos 25 da 3a: 158 cadastros. A CONFIGURAÇÃO usa paleta fixa, as áreas novas da FICHA seguem a paleta do personagem. Textos longos expandem os cartões e seu espelho.

Contrato e cenários mecânicos conferidos na cópia nativa de revisão. A integração do bot precisa reconhecer formato 6 antes da publicação para jogadores; bot e oficial não foram modificados. A parte 3c continua separada e exige seu próprio protótipo.


### Revisão do grupo7 · formato6 preservado

Escolha explícita do usuário: custom usa os mesmos níveis do livro — Caminho2/7/15/23/30, Trilha2/11/19/27 — e os mesmos cartões da FICHA. As chaves `.nivel.N.nome/.texto` de1 a30 continuam presentes por compatibilidade; níveis não aplicáveis retornam texto vazio e não correspondem a entrada editável. Não há chave removida nem novo formato; total7.387. Os campos das23 perícias e11 ofícios continuam com o mesmo índice/semântica, mas as colunas de origem e as fórmulas acompanham a distribuição em duas colunas. Cache CB2:CC10 é memória interna de preenchimento, sem benefício/exportação.


## Formato 7 · autonomia e nove Famílias (15/10/2026, validado na revisão)

7485 chaves únicas. Preserva as chaves anteriores; agrega Famílias 6–9 no fim do contrato. `invocacao.N.familia.6` até `.9` são entradas; `invocacao.N.autonomia` exporta Autônoma ou Não autônoma, com vazio usando Autônoma; `.limite_familias` e `.limite_livres` são os limites efetivos. N vai de 1 a 12. As chaves `.familias` agregam as nove escolhas. `.definicao` mantém o sentido e aponta uma linha abaixo para abrir respiro.

Regras novas: `regra.invocacao_familias_` + `abertas_padrao`, `livres_padrao`, `abertas_parceria`, `livres_parceria`, `abertas_principal`, `livres_principal`, `livres_nao_autonoma`; cada uma tem a chave efetiva e o sufixo `.campanha`. As fontes são as colunas G/F das linhas 139–145 de CONFIGURAÇÃO. O leitor local reconhece 7. O bot não foi alterado. A opção de autonomia é individual; Não autônoma concede uma nova Livre, somada também ao total aberto, e exige ordem exceto para Reação. Regra futura do Guia de Criação.

## Formato 8 · Famílias custom e limites da técnica (15/10/2026)

9.082 chaves únicas: as 7.485 anteriores conservam ordem, sentido e fontes, exceto `formato.versao`, agora 8. Entram 1.597 chaves. Conferência nativa integral: 9.082 chaves únicas e nenhum valor de erro. Leitor local aceita 1–8; bot e ficha oficial não foram modificados.

- `custom.familia.N.nome`, `.estado`, `.mestre_viu`, `.descricao`, N de 1 a 318, nessa ordem por registro. Exporta o cadastro cru, inclusive inválido; vazio continua vazio, e MESTRE VIU sai 1/0. Parte `configuração`.
- `aviso.custom.familia.N`, N de 1 a 318: problema do cadastro. Apenas registros válidos entram no catálogo unido às nove Famílias do livro. Nome duplicado, estado inválido e caixa não lógica geram aviso; nomes com `*`, `?` ou `~` são comparados literalmente.
- `regra.familias_livres`, `regra.familias_fechadas` e seus sufixos `.campanha`: G157/F157 e G158/F158 em CONFIGURAÇÃO. Campanha vazia usa 2 Livres e 3 Fechadas do livro.
- `regra.familias_neutras`: G159, saldo do total válido menos os limites Livres/Fechadas; excesso permanece visível como saldo negativo e aviso.
- `regra.familias_total`: G160, nove do livro mais os cadastros válidos.
- `aviso.regras_familias`: B162, incoerência nos limites.

O estado da Família custom pertence à técnica do personagem. As nove escolhas de cada entidade usam o catálogo de nomes, mas mantêm suas próprias posições Livres e seu próprio orçamento. Cadastrar uma Família Livre na técnica não a torna Livre automaticamente na entidade. A família não concede efeito numérico pela descrição nem atesta aprovação do mestre.

Cobertura desta implementação: 210 referências de Família nas peças da técnica + 108 aberturas de entidade = 318 registros possíveis. Capacidade, tamanho e tempo gerais da 3c ainda não estão fechados; Formas/Melhorias/Restrições e os demais catálogos permanecem em integração separada.

## Formato 9 · Melhorias e Restrições custom (16/10/2026)

Validado na cópia nativa descartável de peças e aplicado à revisão por migração pontual de 66 lotes. A ANALISE completa da revisão também foi relida e comparada: 75.796 células iguais, 18.948 chaves únicas e nenhum erro nas 13 abas verificadas. São 18.948 chaves únicas. As 9.082 anteriores conservam ordem, sentido e fontes, exceto `formato.versao`, agora 9. Entram 9.866 chaves. As quatro colunas foram relidas e comparadas integralmente no Sheets: 75.796 células, nenhuma diferença. O leitor local aceita os formatos 1–9. Bot e ficha oficial não foram alterados.

- `custom.melhoria.N.nome`, `.base`, `.familia`, `.peso`, `.exige_tr`, `.requisitos`, `.efeito`, `.mestre_viu`, N de 1 a 789.
- `custom.restricao.N.nome`, `.base`, `.devolucao`, `.frequencia`, `.efeito`, `.mestre_viu`, N de 1 a 395.
- `aviso.custom.melhoria.N` e `aviso.custom.restricao.N`: problema do respectivo cadastro. Cadastros inválidos continuam exportados, mas ficam fora dos menus.

BASE DO LIVRO é opcional. Campos em branco herdam a base, incluindo a identidade usada nas verificações nomeadas. `Nenhuma` em Família remove o vínculo herdado. Criações sem base precisam de Peso ou Devolução; textos de efeito/requisito não geram automações novas. MESTRE VIU continua sendo lembrete, sem aprovação. Os menus existentes recebem livro e custom; não há novos cartões de resultados.

Nomes com `*`, `?` e `~` são literais. Uma Família Livre na técnica não concede automaticamente desconto de Livre à entidade: vale a posição escolhida na ficha da invocação. Restrições continuam pagando somente Melhorias, com os tetos e incompatibilidades existentes.

As quantidades cobrem os espaços atuais: 165 + 624 Melhorias e 83 + 312 Restrições entre personagem e entidades. São limites de cobertura desta implementação, ainda sujeitos à apresentação conjunta de capacidade e custo da 3c antes do fechamento.

## Formato 10 · capacidade compartilhada reduzida (16/10/2026)

**Implementado no gerador local; aplicação e validação nativa pendentes.** São
**7.356 chaves**. A revisão Google permanece no formato 9 até uma migração
pontual com snapshot novo, teste descartável e salvamento/conferência do código.
O leitor local aceita 1–10; o bot não foi alterado.

Capacidades adicionais ao livro: **10 Famílias, 30 Melhorias, 30 Restrições,
10 Perícias e 10 Ofícios**. Cada definição serve ao personagem e às 12 entidades;
não se multiplicam catálogos pelas posições de uso. Mantidos 25 cartões 3a,
um Caminho, uma Trilha e as nove posições de Família em cada invocação.

- Permanecem `custom.familia.1..10.*`, `custom.melhoria.1..30.*`,
  `custom.restricao.1..30.*` e seus avisos, com a mesma semântica de cadastro cru.
  Seus cartões/fontes mudam de endereço; a coluna C acompanha a nova origem.
- Descontinuadas Famílias 11–318 (1.540 chaves), Melhorias 31–789 (6.831),
  Restrições 31–395 (2.555) e os 131 registros intercambiáveis
  `custom.treino.N.*`/`aviso.custom.treino.N` (786). Total: **11.712 chaves**.
- Entram **120 chaves**: `custom.pericia.N.tipo/.nome/.mestre_viu/.atributo/.efeito`
  e `custom.oficio.N.tipo/.nome/.mestre_viu/.atributo/.efeito`, N de 1 a 10,
  mais `aviso.custom.pericia.N` e `aviso.custom.oficio.N`. TIPO é fixo e validado
  conforme o catálogo; colar outro tipo gera erro e exclui o registro do menu.
- As **7.236 chaves retidas** preservam significado e parte. A posição física
  da linha da ANALISE deixa de ser critério de compatibilidade: leitores devem
  buscar a coluna A. Os avisos de treino do personagem passam a consultar os
  pools de dez definições; continuam existindo 23 escolhas de Perícia e 11 de
  Ofício no personagem. Livro, orçamentos, herança e regras não mudam.
- Ausente não significa cadastro apagável: a migração verifica os campos crus,
  inclusive registros parciais, notas e MESTRE VIU isolado. Slots retirados
  preenchidos bloqueiam a operação. Não se compactam Famílias/peças em outros
  índices silenciosamente. Os treinos recebem namespaces novos: um manifesto
  explícito mapeia cada registro antigo, em ordem, para Perícia ou Ofício,
  preservando os cinco campos e notas; exceder dez de um tipo bloqueia.

`capacidade-b47/migracao.py` planeja a transição a partir de modelos reais e
snapshot nativo recente. Nunca acessa a rede. Snapshot incompleto, divergência
em célula fora de entrada, nota manual fora de campo, fórmula de entrada movida,
excesso de capacidade, oficial como destino ou revisão sem prova descartável
bloqueiam. Fixtures antigas e snapshots sintéticos servem só aos testes locais.
Não manter as chaves retiradas como milhares de exportações vazias. Os três
fragmentos de transporte `PecasAnalise2.gs` a `PecasAnalise4.gs` foram retirados;
o envio ao projeto Google deve retirar esses arquivos antigos também.

### Leitura e variantes históricas

O leitor local rejeita valores de erro e todo `aviso.custom.*` não vazio, mesmo
sem ⚠. Campos de nome/descrição/efeito/requisitos/texto preservam texto literal
(`007`, `1,5`, `VERDADEIRO` não viram números ou booleanos nesses campos). Os
selos dos arquivos Apps Script protegem a geração, sem acrescentar chaves da
ANALISE nem alterar os 7.356 registros.

A auditoria `b50a716` registrou uma colisão histórica: o rascunho
`0fa4aad` em `codex/analise-tr-pericias-carga` chamava de formato 4 um conjunto
de TR/perícias/carga diferente do formato 4 de campanha desta sequência. Esse
rascunho e o bot não foram integrados/alterados. O formato 10 deriva da v9
`4187df3` e não resolve retroativamente essa colisão; confirmar a variante do
bot antes de publicar para jogadores. Nenhuma chave foi reciclada aqui.

| Formato / origem | Conteúdo nesta sequência | Estado do consumidor bot |
|---|---|---|
| 1 · contrato inicial | identidade, escolhas, resultados e avisos | legado, fora da validação atual |
| 2 · main 15e0af9 | amplia entradas de magia e entidades; 4.896 chaves | legado, fora da validação atual |
| 3 · B47 | bônus e mudanças; 5.156 chaves | integração histórica do bot não revalidada |
| 4 · campanha B47 | regras, XP e vida rolada; 5.274 chaves | confirmar variante consumida |
| 4 · rascunho paralelo 0fa4aad | TR/perícias/carga; outro conteúdo | auditoria relata teste no bot; não integrado aqui |
| 5 · B47 | 25 cartões 3a; 6.174 chaves | não revalidado nesta entrega |
| 6 · B47 | Caminho/Trilha e treinos; 7.387 chaves | não revalidado nesta entrega |
| 7 · B47 | autonomia e nove Famílias; 7.485 chaves | não revalidado nesta entrega |
| 8 · B47 | Famílias custom; 9.082 chaves | não revalidado nesta entrega |
| 9 · B47 | Melhorias/Restrições; 18.948 chaves | não revalidado nesta entrega |
| 10 · esta entrega | capacidade compartilhada reduzida; 7.356 chaves | reconhecimento/compatibilidade pendentes antes de jogadores |
