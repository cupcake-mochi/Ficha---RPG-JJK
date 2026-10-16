# Entidades C+D · roteiro de teste nativo (para o integrador)

Só numa **cópia descartável** própria, nunca na ficha oficial nem na revisão preenchida. Sem importar Excel no
Google. Esta frente não executou nada no Google: todo o roteiro está **pendente**.

## 0. Preparação (integrador)

1. No ramo de tarefa do integrador, a partir de `codex/configuracao-b47` (`7752c91` ou sucessor), aplicar
   `patches/02-copias-de-complemento.patch`, `patches/01-entidades-no-gerador.patch` e
   `patches/03-testes-comuns-com-entidades.patch`, nessa ordem (todos em `revisao-b47/cd-entidades/`).
2. Conferir local: `.venv/bin/python revisao-b47/cd-entidades/conferir_patches.py --base <ramo> --regressao`
   (worktree descartável; esperado 13 ok, com 1 risco preexistente do `INDIRECT` das Condições).
3. Gerar os `.gs` pelo fluxo normal. Arquivos novos: `Entidades.gs` e `EntidadesPainel.gs`. Todos os `.gs` vão
   para o projeto da descartável (o carregador recusa montar sem os dois).
4. Montar a descartável com `construir()` **do zero**. A migração por lotes não serve aqui: ela não passa pelo
   carregador e esconderia o defeito que o patch 02 corrige.

Endereços abaixo são da geração conferida (base `7752c91` + 02 + 01). Eles são derivados: se algo acima
mudar, localize pelos títulos de seção `ENTIDADES CUSTOM · TIPOS` / `ENTIDADES CUSTOM · TALENTOS`.

| Campo | Tipo 1 | Tipo 10 | Talento 1 | Talento 20 |
|---|---|---|---|---|
| NOME | B1879 | J1991 | B2021 | J2273 |
| MESTRE VIU | F1879 | N1991 | F2021 | N2273 |
| BASE DO LIVRO | E1881 | M1993 | E2023 | M2275 |
| VIDA / CATEGORIA | E1882 | M1994 | E2024 | M2276 |
| TALISMÃ | E1883 | M1995 | — | — |
| RESERVA DE PE | E1885 | M1997 | — | — |
| DEFINIÇÃO / REQUISITOS | B1889 | J2001 | B2031 | J2283 |
| EFEITO | B1894 | J2006 | B2036 | J2288 |
| aviso | B1903 | J2015 | B2045 | J2297 |

Invocação 1: nome `INVOCAÇÕES!I13`, tipo `I43`, talismã `L47`, talentos `J80:J87`, Trilha `J182:J184`.
Nível da ficha: `FICHA!AH11`. Leituras em `DADOS_INVOC` linha 2 (invocação 1): vida `GF`, entrada `GZ`,
rótulo da reserva `IB`, ganhos `GX`, talentos marcados `GY`, aviso de talento `IF`.

## 1. Estrutura e carregador (patch 02)

- [ ] `DADOS_ENTIDADES` existe, oculta, 37 × 38.
- [ ] CONFIGURAÇÃO: 10 cartões de tipo e 20 de talento, com todos os rótulos, `Nenhuma` na base e caixas de
      MESTRE VIU **em todos os cartões**, não só no primeiro par.
- [ ] Patch 02, nas seções antigas: o 2º par de Famílias custom (linha ~953), de Melhorias (~1037), de
      Restrições (~1426) e de Danos mostra os rótulos (`TIPO`, `NOME`, `MESTRE VIU`, `ESTADO`). Antes do 02,
      o carregador JS os perdia (1296 células na geração conferida).
- [ ] Menus: BASE com `Nenhuma` + os 5 tipos do livro (ou + talentos do livro); VIDA/TALISMÃ/RESERVA/CATEGORIA
      com as listas fechadas e validação estrita.
- [ ] Texto longo em DEFINIÇÃO/EFEITO estica a linha do par e volta a 25 px quando apagado.

## 2. Tipos (cenário A do teste local)

FICHA no nível 14. Nas 12 invocações, talismã `Com carga`. Cadastros:

| Vaga | NOME | BASE | VIDA | TALISMÃ | RESERVA |
|---|---|---|---|---|---|
| 1 | Golem de Papel | | Corpo de criação | | |
| 2 | Gaiola de Talismã | | | Usa | |
| 3 | Rancor Contido | | | | Maldição domada |
| 4 | Herdeiro Criado | Corpo amaldiçoado de criação | | | |
| 5 | Domada Fabricada | Maldição domada | Corpo de criação | | |
| 10 | Shiki Sem Talismã | Shikigami de criação | | Não usa | |

Escolha nas invocações 1–12, nesta ordem: Golem de Papel, Gaiola de Talismã, Rancor Contido, Herdeiro Criado,
Domada Fabricada, Shiki Sem Talismã, Shikigami de criação, Corpo amaldiçoado de criação, Maldição domada,
Shikigami de técnica, Golem de Papel, Golem de Papel.

- [ ] Vida: 57 nas invocações 1, 4, 5, 8, 11, 12; 44 nas demais.
- [ ] Entrada: 2 nas invocações 2 e 7; 4 nas demais.
- [ ] Reserva no rótulo de domada (`RESERVA · MÁX. …`) nas invocações 3, 5 e 9; comum nas demais.
- [ ] Nenhum aviso nos seis cadastros; cartões vazios sem aviso.
- [ ] Alma, autonomia e as nove Famílias das 12 invocações iguais às de antes dos cadastros.

## 3. Inválidos e nomes literais (cenário B)

- [ ] Tipo custom `Maldição domada` → aviso de nome repetido. A invocação com `Maldição domada` continua domada
      e com vida 44.
- [ ] `Lua X` (sem campos) e `Lua*` (VIDA Corpo de criação): só `Lua*` dá vida 57; `Lua X` fica 44.
- [ ] `Eco Duplo` e `eco duplo` → os dois avisados e fora do menu.
- [ ] Cartão só com VIDA e sem NOME → `Preencha NOME`.

## 4. Talentos (cenário C)

Cadastros: Sopro Curto (CAT 1, efeito próprio); Muralha (CAT 3); Escama Fina (base Escama, resto em branco);
Eco Leve (base Eco, CAT 1); Sem Categoria (sem base, sem CAT); Base Errada (base inexistente colada);
Rubina (CAT 2) **antes** de Ru*na (CAT 1); Leitura (CAT 1); Último Talento na vaga 20 (CAT 2).

- [ ] Sopro Curto no 1º ganho (nível 1) sem aviso; Muralha no 2º ganho (nível 6) acusa teto 1; no 4º ganho
      (nível 14) é aceita.
- [ ] O 5º ganho (nível 18) continua fechado no nível 14; cinco talentos com quatro ganhos acusam excesso.
- [ ] Escama Fina herda CAT 3 e o texto do livro na carta; Eco Leve fica com CAT 1.
- [ ] `Ru*na` é tratado literalmente (CAT 1), sem confundir com Rubina (CAT 2).
- [ ] Sem Categoria, Base Errada e qualquer nome do livro repetido ficam fora do menu, com aviso.
- [ ] Menu da Trilha (`J182:J184`) oferece Sopro Curto e Eco Leve, mas não Muralha nem Escama Fina.
- [ ] O mesmo talento custom escolhido nas 12 invocações.

## 5. ANALISE e limpeza

- [ ] `custom.tipo_entidade.1.nome` … `custom.talento_entidade.20.efeito` e os 30 `aviso.custom.*_entidade.N`
      presentes no fim. As chaves anteriores ficam inalteradas (comparar com a leitura antes do teste).
- [ ] Restaurar a descartável, apagando cadastros e escolhas, e conferir que as 12 invocações voltam aos
      valores iniciais.

Registrar evidências (capturas, leituras JSON) em pasta própria do integrador, sem dados de jogador.
