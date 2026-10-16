# Revisão cruzada · frente de personagem (`codex/b47-cd-personagem`)

SHA revisado: `e9af8d336716385488b442e31a6f1a596ed19068` (série `patches/base-7752c91/`). Base: `7752c91` +
esta frente (`f0ed96a`). Linux, Python 3.12, Node 22, LibreOffice 24.2. Sem Google. Revisão **parcial**: ver
"Não feito".

## Reproduzido

- `conteudos-b47/personagem/validar.py`: **73/73**, 20 s, igual ao relatório deles.
- Série deles 01 → 02 → 03 aplica limpo em `7752c91`; geração completa OK.

## Achados

**P1. Média/alta: transporte registrado só em tempo de execução.** O patch 02 deles faz
`emitir_gs.SEPARADAS.update(...)`/`COMPLEMENTOS.update(...)` dentro do `monta.py`. Quem importa
`emitir_gs` depois (`abas_cruas`/`abas_do_script`: `conferir-ficha-xlsx.py`, `regressao-progressao.py`,
`conferir-copias.py`, `capacidade-b47/previas.py`, `medidas/`) não conhece os arquivos novos. Medido na
geração combinada: a referência Python não tem `DADOS_FORMAS`, `DADOS_APTIDOES`, `DADOS_TALENTOS`, e faltam
2096 células da ANALISE e 1003 da CONFIGURAÇÃO que o carregador JS tem. `regressao-progressao.py`:
"fragmentos recompõem todas as abas do modelo" **falha só com a série deles** (base e série de entidades
passam). Sugestão: declarar os arquivos em `emitir_gs.py` (como Danos/Entidades) ou expor um registro
importável que os leitores Python também usem.

**P2. Média: as duas séries não aplicam juntas.** Os dois patches 01 inserem depois de `custom_danos`, e
os dois mexem na linha `ordem` do `modelo.gs.js`. Entregue aqui:
`patches/com-personagem/01-entidades-no-gerador.patch`, gerado por `preparar_patches.py` sobre
`7752c91` + série deles. Ordem testada: deles 01→02→03, entidades 02, entidades 01 (com-personagem),
entidades 03. Geração combinada OK: ANALISE 8190 = 7436 + 230 (entidades) + 524 (personagem).

**P3. Média: fatiamento da ANALISE.** O 02 deles corta `PecasAnalise*.gs` em `_AN_FIM_PECAS`. Linhas
acrescentadas depois das de personagem não caem em complemento nenhum e voltam para `Analise.gs` (já
816 KB). As entidades exportam antes de `_AN_FIM_PECAS` por isso; uma próxima frente precisa saber.

**P4. Baixa/atenção: margem de tamanho.** Combinado: 34 `.gs`, todos abaixo de 900 KB, mas
`Configuracao.gs` 843.040 e `Ficha.gs` 824.274 bytes. Pouca folga para D.

**P5. Positivo.** Os cartões deles também dependem de `copias`; com o patch 02 desta pasta, o carregador
JS não perde nenhuma célula em relação à referência Python, na combinação.

**P6. Positivo: convivência célula a célula sem colisão.** `comparar_frentes.py` sobre modelos
`--exportar-pecas` de base, só entidades, só personagem e combinado:

| Aba | entidades | personagem | as duas | combinado reproduz cada uma |
|---|---:|---:|---:|---|
| DADOS_INVOC | 264 | 3120 | 0 | sim |
| DADOS_AM | 0 | 1199 | 0 | sim |
| DADOS_ENTIDADES | 550 | 0 | 0 | sim |
| DADOS_FORMAS / APTIDOES / TALENTOS | 0 | 5944 / 1566 / 876 | 0 | sim, a menos de 290/100/80 referências à CONFIGURAÇÃO deslocadas +426 linhas (bloco de entidades antes); 0 diferenças depois de normalizar a linha |
| Menus INVOCAÇÕES / FICHA AMALDIÇOADA | 3 / 0 | 24 / 4 | 0 | sim |

Nenhuma célula ou menu é alterado pelas duas frentes; endereços derivados funcionam na combinação.

**P7. Alta: regressão na FICHA AMALDIÇOADA sem nenhum cadastro (LibreOffice 24.2).** Recálculo da base
`7752c91` e da combinação, catálogos vazios, 31.134 fórmulas de FICHA/INVOCAÇÕES/FICHA AMALDIÇOADA/
DADOS_INVOC/DADOS_AM/DADOS: 76 valores mudam, **nenhum** lê `DADOS_FORMAS` (único lugar com `LET`) e
nenhum vem das entidades (0 células da DADOS_AM alteradas por elas). Erros: 13 na base → 25.

- `FICHA AMALDIÇOADA!P42:S42` (0/0/0/3 → `#VALUE!`), via `DADOS_AM!KV21:KV24` ← `HM17/HM20/HM21/HM22`.
  `HM17` soma `IFERROR(VLOOKUP(...,'DADOS_TALENTOS'!$AQ$2:$AW$34,2,FALSE),0)+...`. Provável causa: vaga em
  branco busca `""` e casa com linha custom vazia do catálogo unido, que devolve texto `""`; o `+` fica fora
  do `IFERROR`. Correção sugerida: linha custom inválida/vazia com categoria numérica 0 (como em
  `DADOS_ENTIDADES`) ou não buscar quando a vaga está vazia.
- `FICHA AMALDIÇOADA!F379,G379,L379,...` (vazio → `CE ` / ` esp.`), via `DADOS_AM!HT/HU`: mesma causa
  (`HQ` vira `""`, não 0).
- `FICHA!D368`, `S368` (cartas de Aptidão): o texto "Do livro" passou de resumo a descrição completa
  (`VLOOKUP(...,'DADOS_APTIDOES'!$BF$2:$BO$45,10,...)` em vez de `$CD$2:$CM$35`). Mudança de
  comportamento sem cadastro, a confirmar com o usuário/molde.

Lista completa (76) em `nuvem-b47/saidas/` não versionado; reproduzir com modelos `--exportar-pecas` e
`comum_cd.recalcular`. Recomendo a frente de personagem rodar o mesmo cenário vazio antes da incorporação.

## Da base do integrador (não é da frente de personagem)

- `regressao-progressao.py`: "formato 10 explícito" falha já em `7752c91` (ANALISE foi para 11).
- `regressao-construir.js`: falha em `INDIRECT(IF(...))` do menu de Condição (ver relatório de implementação).

## Não feito (impedido pelo limite de uso desta sessão)

- Recálculo com cadastros preenchidos e das 560 fórmulas com `LET` da `DADOS_FORMAS`: o LibreOffice 24.2
  daqui não tem `LET` (exige 24.8+). Só o cenário vazio foi feito (P7).
- Leitura linha a linha de `motor.py`/`consumidores.py`/`planilha.py` contra o livro.

Próxima ação: frente de personagem corrige P7; integrador concilia P1–P3 antes de juntar as séries. Recomendação: modelo do integrador, High.
