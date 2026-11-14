# Continuação: ficha do Ciclo Maldito · depois da linha congelada · 12/11/2026

Versão do git, com os IDs das QAs cortados. A versão completa, com os IDs, o Mizuki tem no chat e no `_handoffs` do HD.
Os IDs completos das duas QAs também estão em `r53/diagnostico-android/PROMPT-RETOMADA-CRIACAO-2026-11-08.md`.

---

Responda em português informal, direto, sem português de Portugal. Você está continuando o pente fino da ficha do
Ciclo Maldito (RPG de mesa do Mizuki).

## Antes de tudo

1. **Clonar e conferir a base:**
   - clone `cupcake-mochi/Ficha---RPG-JJK`;
   - vá para o ramo `codex/corrige-colagem-atributos-20261108`, a base da pilha;
   - confira com `git log --oneline -3`. Na hora deste prompt, o topo era o merge do PR de fechamento, logo depois do
     #110 (`2e0ba52`);
   - rode `gh pr list --state open` e confira que não tem PR nova de outra sessão mexendo no mesmo assunto.
2. **Ler:**
   - `AGENTS.md`, só as três primeiras entradas;
   - `r53/diagnostico-android/CORRECAO-XP-LINHA-CONGELADA-2026-11-12.md`;
   - `r53/diagnostico-android/CORRECAO-CORTE-XP-25-2026-11-12.md`;
   - `r53/diagnostico-android/MAPA-COBERTURA-2026-11-10.md`, a lista do pente fino.

## Regras do Mizuki (valem sempre)

**Trabalho:**
- Cada conserto vai num ramo novo a partir da base da pilha, com uma PR para ela.
- Pode mesclar sem pedir quando a PR for sua, o CI estiver verde e ela estiver mesclável:
  `gh run watch <id> --exit-status`, depois `gh pr merge N --merge`.
- **Nunca:** auto-merge, main, PR31 (Carteira viva), PRs de outros, force push, ficha do jogador, acionadores,
  ampliação de acesso, importar Excel/Office, reinstalar o pacote inteiro ou rodar `construir()`.

**Oficiais:**
- Nas fichas oficiais, nada sem o ok dele no chat.
- Antes de qualquer mudança, uma versão de backup nativa do projeto.
- Teste antes numa QA.

**Planilha e git:**
- Mudança na planilha vai pela API do Sheets. As fórmulas usam `;` (pt_BR).
- Versione só evidência sanitizada: sem ID completo de planilha ou projeto no git.

**Agentes e planejamento:**
- Agente de pesquisa ou workflow: pergunte antes e diga quantos, o que cada um faz e o custo. Ele usa conta Pro.
- Mostre o plano e espere o ok quando a tarefa:
  - mexe em mais de 3 arquivos;
  - muda número de regra ou mecânica;
  - move ou apaga coisa.

**Comunicação:**
- Mudança de regra é decisão dele: pergunte.
- Sempre passe o link da PR.

**Testes:**
- Smoke: `python nuvem-b47/conferir.py --smoke`, que tem que sair com 0. As linhas "Salários: falha estado/ledger" são
  esperadas.
- O ambiente se monta com `bash nuvem-b47/preparar.sh` (Linux, com `.venv`).
- No Windows, se montar o ambiente der trabalho, o mesmo smoke roda no CI de toda PR (`.github/workflows/nuvem.yml`).
  Os testes `node r53/testes/*.js` rodam só com o Node.

**Mudança no `apps-script/Salarios.gs`:** entra como mais um preparador no fim da cadeia. A cadeia hoje é:
1. preparar_missoes
2. enxutas
3. sem_registros
4. xp_atualizar
5. trava_nivel_missao
6. xp_congelado_nome
7. xp_linha_congelada

Siga o modelo do `r53/diagnostico-android/preparar_xp_linha_congelada.js`. Os testes `missoes_enxutas.js`,
`missoes_sem_registros.js` e `salario_lote.js` conferem que a cadeia reproduz o Salarios.gs.

## As duas QAs (use só elas para ensaio)

| QA | planilha | projeto Apps Script | estado |
|---|---|---|---|
| Era | `1LBZOf9v…` | `1IBTaNa9…` | nível 10, XP 3700 (`DADOS!CZ54` = 3700), painel de missões vazio, `DADOS_SALARIOS` só com a linha 2 antiga e inativa |
| Ciclo | `1HQqGOVG…` | `1WHzpRRE…` | nível 2, XP 0, painel e `DADOS_SALARIOS` vazios |

O Codigo instalado das duas está no hash `4f6600227cd1`. É o arquivo que tem o `salarioMissaoDireta_`, com o corte de
25, o #109 e a linha congelada. A aba FICHA PESSOAL tem o sheetId 994525406, e a FICHA tem o 2091222604.

Como trabalhar nas QAs:
- **Navegador:** o Claude in Chrome, no Chrome do Mizuki, que tem a conta Google.
- **Código:**
  - gere o trecho com o preparador (`node r53/diagnostico-android/preparar_<nome>.js > trecho.js`);
  - cole no console do editor (`monaco.editor.getModels()`). O trecho troca só os pedaços e recusa se eles não
    baterem;
  - clique no editor (~900,600), aperte Ctrl+S e espere "Salvo no Google Drive";
  - recarregue e confira o hash SHA-256 (12 primeiros dígitos) do arquivo que tem o `salarioMissaoDireta_`.
- **Ensaio na planilha:**
  - navegue pela caixa de nome: clique nela (~60,101), digite o endereço e aperte Enter;
  - antes de digitar, confira com zoom qual célula está ativa. Numa vez a página não tinha carregado e o texto caiu na
    CARTEIRA;
  - para passar de célula, use a tecla Tab separada: um `\t` dentro do texto vira caractere na célula;
  - cada edição leva de 10 a 30 s até o onEdit terminar. Leia o resultado pela API.
- **Reposição:** pela API, que não dispara o onEdit:
  - painel e notas com `updateCells` em `userEnteredValue,note`, só nas colunas de nome e tipo. As colunas de TOTAL
    (BA, BG, BM, BS) têm fórmula;
  - as linhas novas do `DADOS_SALARIOS` limpas;
  - `DADOS!CZ54` e `FICHA!AH11` de volta aos valores de antes.

## O que está pendente

1. **Oficiais (precisa do ok dele).** Nada do dia 12/11 foi aplicado nelas; a última mudança é de 03/11, então falta
   tudo de #63 em diante (correção de 14/11: os links das duas oficiais estão no `r53/OFICIAIS.md`). Faça o backup
   nativo antes. Os textos da CONFIGURAÇÃO de 14/11 (`CORRECAO-ACHADOS-CONFIGURACAO-2026-11-14.md`) também entram.
   - **No Codigo instalado,** os três trechos, nesta ordem:
     1. `preparar_corte_xp_missao.js`, com os 292 moldes;
     2. `preparar_xp_congelado_nome.js`;
     3. `preparar_xp_linha_congelada.js`.

     Se a oficial ainda não tiver a trava de nível do #107 (`function salarioMissoesDaEdicao_(` ausente), o
     `preparar_trava_nivel_missao.js` vem antes. Confira o hash a cada passo.
   - **Na planilha,** a parte do #108, como na seção "Instalação nas duas QAs" do `CORRECAO-CORTE-XP-25-2026-11-12.md`:
     - `findReplace` com regex nas fórmulas da FICHA PESSOAL!BA15:BS87;
     - `DADOS!CR9:CS9` e `CR15:CS15`;
     - as 8 notas.
   - **Depois,** registre no `r53/OFICIAIS.md` o que foi aplicado.
2. **Aviso dentro da nota da missão congelada (opcional, pergunte).** Hoje a nota mostra só `[XP congelado: x · id]`.
   Uma frase como "já está no XP digitado: apagar ou mudar não altera o XP" pede mexer:
   - no atalho: o `r53/atalho_livre.js` gera o `r53/atalho_livre.gs`, que vai no fim do Codigo;
   - e no `salarioXpCongelado_`, juntos.
3. **Feito em 12–14/11:** a auditoria da CONFIGURAÇÃO (#112) e os achados decididos pelo Mizuki
   (`CORRECAO-ACHADOS-CONFIGURACAO-2026-11-14.md`). Fica como modelo para o próximo item. A auditoria era contra o livro R66. A fonte é
   `cupcake-mochi/JJK---Project`, `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`. Siga o modelo das
   auditorias anteriores (`AUDITORIA-PROGRESSAO-XP-2026-11-12.md`):
   - um documento por auditoria, com os achados;
   - ensaio numa QA, com a reposição;
   - cada conserto na sua PR;
   - número de regra é decisão dele.
4. **Decisões abertas dele (não decida sozinho):**
   - a redação do R66 na ficha inteira;
   - os atributos naturais;
   - o aviso AK85, que fica quando a Trilha troca.

## O que foi decidido em 12/11 (para não refazer)

- **Um nível por missão:** no máximo um, pelo livro R66 (#107).
- **Corte de 25:** a missão cujo XP final fica abaixo de 25 paga 0. É regra da casa e vale por missão (#108).
- **XP congelado:**
  - congelam as missões que estavam no painel quando a pessoa digita o XP total na FICHA!AN11. As anotadas depois são
    normais;
  - nada na linha congelada descongela, nem o mesmo nome, nem o nome com erro, nem outra missão;
  - missão nova vai numa linha vazia;
  - o Mizuki escolheu isso depois de comparar com o "nome no registro" do #109, que ficou substituído (#110).
- **Apagar missão:** a comum tira o XP dela. A congelada não muda o XP. O nível nunca desce pelo painel.
