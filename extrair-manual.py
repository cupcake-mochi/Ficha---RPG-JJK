# -*- coding: utf-8 -*-
"""Gera o manual.txt a partir do livro reconstruído do sistema (LIVRO-COMPLETO.md).

Uso: python3 extrair-manual.py [LIVRO-COMPLETO.md] [--confere]

R53: a fonte portátil padrão está em referencias-r53/. O fluxo histórico
abaixo descreve versões anteriores; não é a fonte ativa.

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
REL = "referencias-r53/LIVRO-COMPLETO.md"
LIVRO = "Ciclo Maldito R53, 411 páginas; publicação 3a810995e5211e2c21c90b02c8a5f43f67fa9d8a"

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

def extrair(fonte=None,confere=False):
    fonte=Path(fonte) if fonte else RAIZ/REL
    if fonte.is_dir():fonte=fonte/REL
    md=fonte.read_text(encoding="utf-8")
    meta={"arquivo":REL,"sha256":hashlib.sha256(md.encode()).hexdigest(),
          "livro":LIVRO,"gerado_por":"extrair-manual.py"}
    manual=texto(md);metadata=json.dumps(meta,ensure_ascii=False,indent=2)+"\n"
    if confere:
        if (RAIZ/'manual.txt').read_text()!=manual or (RAIZ/'manual-fonte.json').read_text()!=metadata:
            raise SystemExit('Manual ou metadados desatualizados: execute extrair-manual.py')
    else:
        (RAIZ/'manual.txt').write_text(manual)
        (RAIZ/'manual-fonte.json').write_text(metadata)
    return meta

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument('fonte',nargs='?');p.add_argument('--confere',action='store_true');a=p.parse_args()
    m=extrair(a.fonte,a.confere);print('manual.txt conferido' if a.confere else 'manual.txt gerado',m['livro'])
