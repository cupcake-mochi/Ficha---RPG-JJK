# revisao-b47 — revisão independente da redução de capacidade (chat 2)

Pasta do revisor. Só lê o núcleo; não regenera `.gs` versionados, não escreve no Google e não altera
`ficha-v01/`, `ficha/`, `apps-script/`, contrato, planos ou `rodar-tudo.sh`. Relatório: [RELATORIO.md](RELATORIO.md).

## Preparação

```bash
PYTHON=python3.12 bash nuvem-b47/preparar.sh      # o python3 padrão desta nuvem é 3.13
.venv/bin/python nuvem-b47/conferir.py --smoke
```

Requer Node ≥ 18 (sondas do carregador) e Git (worktrees temporárias). LibreOffice só para a conferência opcional do leitor.

## Bateria

```bash
bash revisao-b47/rodar.sh base-v9          # estado publicado: só as falhas reais da base acendem
bash revisao-b47/rodar.sh simulado-alvo    # SIMULAÇÃO 10/30/30/20 trocando só as constantes
```

| Arquivo | O que prova | Custo |
|---|---|---|
| `test_contrato.py` | chaves únicas; 1..capacidade por catálogo com campos e aviso; fontes na CONFIGURAÇÃO sem célula compartilhada; 6.706 chaves fora dos catálogos preservadas com parte/aba/ordem; retirar chave exige `formato.versao` novo; leitor conhece o formato | ~10 s (gerador `--exportar-analise`) |
| `test_leitor.py` | `ler-analise.py` reprova cada mensagem real de aviso de cadastro (colhida das fórmulas geradas) e valores de erro (`#REF!`…) | ~15 s; `--com-patch` testa o patch proposto |
| `test_enderecos.py` | faixas sobre tabelas de catálogo que terminam além dos dados (endereço fixo), buracos internos, endereços em texto (`INDIRECT`), faixa morta na CONFIGURAÇÃO, nome custom cru em COUNTIF/MATCH/VLOOKUP | ~20 s (`--exportar-pecas`, 45 MB) |
| `test_carregador.py` | `.gs` montados num VM: guarda de `montar_()` e ANALISE montada = contrato; no modo simulado, gera numa worktree temporária e testa projeto com/sem arquivos antigos | base ~2 s; simulado ~40 s |
| `test_migracao.py` + `migracao_guarda.py` | guarda de migração proposta: molde vazio derivado do gerador, primeira/última vaga, corte, compactação, separação Perícia/Ofício, tipo ausente, curingas, nomes repetidos, separador ` · `, reutilização por nome | ~15 s |
| `test_patch_carregador.py` | aplica `patches/carregador-selo-de-geracao.diff` numa worktree e repete os cenários do carregador | ~40 s por perfil |
| `sonda_libreoffice_name.py` | B3: quais avisos 3a viram `#NAME?` no LibreOffice (rodar da raiz, sozinho) | ~2,5 min |

Perfis em [casos/perfis.json](casos/perfis.json). Para revisar o commit A: fazer checkout do SHA, escolher/ajustar
`alvo-real-treino-unico` ou `alvo-real-separado` conforme o contrato publicado (nomes de chave, campos, capacidades)
e rodar `bash revisao-b47/rodar.sh <perfil>`. Perfis com `trocas` vazias rodam o gerador real; não fingem redução.

Saídas JSON: `nuvem-b47/saidas/revisao-b47/` (ignorada pelo Git), cacheadas por SHA/perfil quando o núcleo está limpo.
Código de saída 1 = falha bloqueante; `RISCO` só é relatado.

## Patches propostos (não aplicados)

- `patches/carregador-selo-de-geracao.diff` — `ficha/emitir_gs.py` e `ficha/modelo.gs.js`.
- `patches/ler-analise-avisos-custom.diff` — `ler-analise.py`.

`git apply --check revisao-b47/patches/<arquivo>` a partir da raiz. Depois de aplicar, o integrador regenera os `.gs`
pelo fluxo normal e atualiza `regressao-construir.js` (lista fixa de arquivos ausentes).

## Fixture

`fixtures/contrato-v9.json.gz`: chave, parte e aba de origem das 18.948 chaves exportadas em 4187df3
(`python ficha-v01/monta.py --exportar-analise`). É referência do formato 9, não snapshot de planilha.
