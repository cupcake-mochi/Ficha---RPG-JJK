# -*- coding: utf-8 -*-
"""Gera o manual.txt a partir do livro reconstruído do sistema (LIVRO-COMPLETO.md).

Uso: python3 extrair-manual.py <clone do JJK---Project>

Desde 04/10/2026 o livro do sistema é a candidata editorial reconstruída, montada em
sistema/05-material/livro/planejamento-editorial/consolidacao/lote-01/LIVRO-COMPLETO.md a partir
das 23 fontes. O manual.txt deixa de sair do PDF com pdftotext: sai deste Markdown, sem as marcas de
formatação, menos o # dos títulos (o nível do título fica, para os validadores acharem a seção), e as tabelas ficam uma linha por fileira, com as colunas separadas por " | ". Assim os
validadores leem frase e tabela sem depender da diagramação do PDF.

O manual-fonte.json guarda de qual arquivo e de qual hash o manual.txt saiu.
"""
import hashlib, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
REL = "sistema/05-material/livro/planejamento-editorial/consolidacao/lote-01/LIVRO-COMPLETO.md"

def texto(md):
    out = []
    for l in md.splitlines():
        if l.startswith("<!--") or l.startswith("<a id="):
            continue
        s = re.sub(r"<[^>]+>", "", l)
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
        s = s.replace("**", "").replace("`", "")
        s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", s)
        if re.match(r"^\|[\s:|-]+\|$", s.strip()):
            continue
        if s.startswith("|"):
            s = " | ".join(c.strip() for c in s.strip().strip("|").split("|"))
        s = re.sub(r"^(#+)\s*", r"\1 ", s)
        s = re.sub(r"^>\s?", "", s)
        out.append(s)
    return "\n".join(out).strip() + "\n"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fonte = Path(sys.argv[1]) / REL
    md = fonte.read_text(encoding="utf-8")
    (RAIZ / "manual.txt").write_text(texto(md), encoding="utf-8")
    (RAIZ / "manual-fonte.json").write_text(json.dumps({
        "arquivo": REL, "sha256": hashlib.sha256(md.encode()).hexdigest(),
        "livro": "candidata editorial reconstruída, revisada em 04/10/2026 e em 05/10/2026 (382 páginas)",
        "gerado_por": "extrair-manual.py"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("manual.txt gerado de", REL)
