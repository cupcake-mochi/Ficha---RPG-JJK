# -*- coding: utf-8 -*-
"""Gera o manual.txt a partir do livro reconstruído do sistema (LIVRO-COMPLETO.md).

Uso: python3 extrair-manual.py <clone do JJK---Project>

Desde 10/10/2026 (B45) o livro do sistema é o livro final, o Ciclo Maldito (R43; desde 14/10/2026, B46, o R51), em
sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md (a pasta guarda o nome da edição R41).
De 04/10 a 09/10/2026 a fonte foi a candidata editorial reconstruída, em
planejamento-editorial/consolidacao/lote-01/LIVRO-COMPLETO.md, que não recebeu a revisão de regras
do Mizuki de 07 a 09/10. O manual.txt deixa de sair do PDF com pdftotext: sai deste Markdown, sem as marcas de
formatação, menos o # dos títulos (o nível do título fica, para os validadores acharem a seção), e as tabelas ficam uma linha por fileira, com as colunas separadas por " | ". Assim os
validadores leem frase e tabela sem depender da diagramação do PDF.

O manual-fonte.json guarda de qual arquivo e de qual hash o manual.txt saiu.
"""
import hashlib, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
REL = "sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md"
LIVRO = "Ciclo Maldito R51, o livro final, como está na v0.364 do JJK---Project (lido em 14/10/2026)"

def texto(md):
    out = []
    nivel = 0                       # o nível do último título de verdade
    for l in md.splitlines():
        if l.startswith("<!--") or l.startswith("<a id="):
            continue
        if l.startswith("#"):
            nivel = len(l) - len(l.lstrip("#"))
        # B45: o livro final rebaixou 48 títulos de grupo do capítulo de Caminhos a uma linha só em negrito, sem
        # pontuação no fim ("**Fluidez no nível 15**", "**Conduções**"). Na candidata eles eram título, e os
        # leitores daqui acham a seção pelo título. A linha volta a ser título, um nível abaixo do título em que está.
        m = re.fullmatch(r"\*\*([^*]+[^*.:!?…])\*\*", l.strip())
        if m and nivel:
            l = "#" * min(nivel + 1, 6) + " " + m.group(1)
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
        "livro": LIVRO,
        "gerado_por": "extrair-manual.py"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("manual.txt gerado de", REL)
