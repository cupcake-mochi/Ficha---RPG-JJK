# revisao-b47/cd-entidades · Tipos e Talentos de entidade custom (frente Claude, C+D)

Entrega isolada: nada aqui altera o núcleo. O integrador aplica os patches. Relatório:
[RELATORIO-IMPLEMENTACAO.md](RELATORIO-IMPLEMENTACAO.md).

| Arquivo | Papel |
|---|---|
| `entidades_custom.py` | módulo `aplica(layout, contexto)` / `exporta(tr)`; cópia idêntica vai para `ficha-v01/` pelo patch 01 |
| `patches/02-copias-de-complemento.patch` | correção do carregador JS (`juntarValores_`): cópias de molde vindo de complemento; independente, aplicar primeiro |
| `patches/01-entidades-no-gerador.patch` | módulo no `monta.py` (depois de `custom_danos`), `Entidades.gs`/`EntidadesPainel.gs`, carregador, guardas |
| `patches/03-testes-comuns-com-entidades.patch` | testes de dano/Condições do integrador convivendo com as chaves de entidade |
| `PROPOSTA-CONTRATO.md` | alinhamento com `conteudos-b47/comum/contrato.json` e divergências declaradas |
| `ROTEIRO-NATIVO.md` | roteiro de teste em descartável (pendente; nada foi feito no Google) |
| `rodar_com_entidades.py` | roda o gerador real com o módulo injetado, sem editar o núcleo (só `--exportar-*` no checkout) |
| `comum_cd.py` | exportação em cache, recálculo LibreOffice, placar |
| `test_entidades_mecanica.py` | contas no Calc local: tipos, inválidos/literais, talentos, regressão (35 checks) |
| `test_entidades_estrutura.py` | contrato ANALISE, consumidores, diferenças restritas, cartões, `esticam` (51 checks) |
| `conferir_patches.py` | worktree descartável: patches, ANALISE antes/depois, geração completa, 900 KB, sonda, regressão JS |
| `referencia_carregador.py`, `sonda_carregador_copias.js` | carregador JS × referência Python, aba por aba, em três ordens |

```bash
.venv/bin/python revisao-b47/cd-entidades/test_entidades_mecanica.py          # ~1 min, LibreOffice
.venv/bin/python revisao-b47/cd-entidades/test_entidades_estrutura.py         # pares 10x20 5x7 1x1
.venv/bin/python revisao-b47/cd-entidades/conferir_patches.py --regressao     # ~5 min, worktree temporária
```

Saídas em `nuvem-b47/saidas/cd-entidades/` (ignorado). Trabalhos pesados em série.
