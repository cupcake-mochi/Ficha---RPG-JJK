# B47 C+D — personagem e Formas

Entrega isolada para incorporação pelo integrador. Implementa Formas do personagem e das entidades, Aptidões/Bênçãos e Talentos do personagem. Não altera o núcleo, a versão ANALISE ou o Google neste ramo.

- [Relatório e sequência de incorporação](RELATORIO.md).
- [Contrato, capacidades e adaptações propostas](CONTRATO-PROPOSTO.md).
- [Inventário de produtores e consumidores](INVENTARIO.md).
- [Roteiro nativo para o integrador](ROTEIRO-NATIVO.md).
- [Evidência da execução focal](VALIDACAO.json).

Para o avanço de integração `7752c9115f168effe74092d125dfdd5352bd44a3`, usar os três patches em `patches/base-7752c91/`. A série na raiz de `patches/` conserva a base inicial `ae16895`. Escolher uma série, na ordem 01 → 02 → 03.

No ambiente preparado, a partir da raiz:

```powershell
$env:PYTHONUTF8='1'
& .\.venv\Scripts\python.exe conteudos-b47/personagem/validar.py
```

Em Linux, usar o Python da venv POSIX no mesmo comando. O roteiro roda em série, constrói a fixture somente em memória e testa os patches em cópias temporárias dentro desta pasta. Logs ficam em `_local/`, ignorada. Não gera XLSX ou GS. Recriar os patches, se necessário: `python conteudos-b47/personagem/preparar_patches.py`.

Para uso como biblioteca, acrescente esta pasta ao caminho de módulos e importe `b47_personagem`. A fachada é `aplica(layout, contexto)` / `exporta(transformacao)`. O motor independente fica em `b47_personagem.motor`.
