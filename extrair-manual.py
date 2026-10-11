# -*- coding: utf-8 -*-
"""Gera o manual.txt a partir do livro reconstruído do sistema (LIVRO-COMPLETO.md).

Uso: python3 extrair-manual.py <clone do JJK---Project>

Desde 11/10/2026 o livro do sistema é o Ciclo Maldito na edição R43, em
sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md (de 04/10 a 10/10 era a candidata editorial
reconstruída, em planejamento-editorial/). O manual.txt deixa de sair do PDF com pdftotext: sai deste Markdown, sem as marcas de
formatação, menos o # dos títulos (o nível do título fica, para os validadores acharem a seção), e as tabelas ficam uma linha por fileira, com as colunas separadas por " | ". Assim os
validadores leem frase e tabela sem depender da diagramação do PDF.

O manual-fonte.json guarda de qual arquivo e de qual hash o manual.txt saiu.
"""
import hashlib, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
# 11/10/2026: o livro principal do sistema, desde a v0.341, mora em ciclo-maldito-r41/ (a pasta guarda o nome da edição em
# que nasceu; o texto de hoje é o R43). A candidata de planejamento-editorial/ ficou guardada e não recebeu a revisão.
REL = "sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md"

def texto(md):
    out = []
    for l in md.splitlines():
        if l.startswith("<!--") or l.startswith("<a id="):
            continue
        # 11/10/2026: na edição R43 os subtítulos que agrupam habilidades ("Proteção de aliados", "Fluidez no nível 15")
        # deixaram de ser título e viraram um parágrafo inteiro em negrito. Aqui eles voltam a ser título de nível 3,
        # que é o que eram no livro de antes e o que os extratores procuram. Ficam de fora a linha "Nível N.", a frase
        # em negrito (termina em pontuação) e a linha de custo de uma habilidade (tem " · ").
        m = re.fullmatch(r"\*\*([^*]+)\*\*", l.strip())
        if m and not re.search(r"[.:?!]$", m.group(1)) and "·" not in m.group(1):
            out.append("### " + m.group(1))
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
        "livro": "Ciclo Maldito, edição R43, como está na v0.358 do JJK---Project (lida em 11/10/2026)",
        "gerado_por": "extrair-manual.py"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("manual.txt gerado de", REL)
