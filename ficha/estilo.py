# -*- coding: utf-8 -*-
"""Paleta e helpers da ficha do Projeto M.
A base e' o ameixa 741B47 do manual, para a ficha conversar com o livro.
O resto e' escuro, porque JJK e' preto com energia colorida por cima."""
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# --- paleta -------------------------------------------------------------
FUNDO     = "0C0A0D"   # quase preto, levemente arroxeado
PAINEL    = "17121A"   # painel sobre o fundo
PAINEL2   = "1F1822"   # painel alternado
AMEIXA    = "741B47"   # a cor do manual
AMEIXA_ESC= "4A1130"
AMEIXA_CLR= "A8306A"
ENERGIA   = "7B3FBF"   # roxo de energia amaldicoada
SANGUE    = "B02840"
TEXTO     = "F2E9EC"
TEXTO_FRACO="8A7580"
OSSO      = "E8DCD4"

TITULO  = "Oswald"     # condensada; se faltar, cai no default do Sheets
CORPO   = "Lexend"
MONO    = "Roboto Mono"

def fill(c): return PatternFill("solid", start_color=c, end_color=c)

def borda(cor=AMEIXA, w="thin", lados="tblr"):
    s = Side(style=w, color=cor)
    n = Side(style=None)
    return Border(top=s if "t" in lados else n, bottom=s if "b" in lados else n,
                  left=s if "l" in lados else n, right=s if "r" in lados else n)

CENTRO = Alignment("center", "center", wrap_text=False)
ESQ    = Alignment("left", "center", indent=1)
CENTRO_W = Alignment("center", "center", wrap_text=True)

def pinta(ws, ini, fim, cor):
    """pinta um retangulo inteiro, celula a celula"""
    from openpyxl.utils import range_boundaries
    c1, r1, c2, r2 = range_boundaries(f"{ini}:{fim}")
    f = fill(cor)
    for r in range(r1, r2+1):
        for c in range(c1, c2+1):
            ws.cell(r, c).fill = f

def caixa(ws, ref, texto=None, cor=PAINEL, fonte=None, alinha=CENTRO, borda_=None, merge=True):
    """merge + pinta + escreve, tudo de uma vez.
    merge=False para fundo grande que vai receber caixas menores por cima."""
    ini, fim = ref.split(":") if ":" in ref else (ref, ref)
    if ini != fim and merge: ws.merge_cells(ref)
    pinta(ws, ini, fim, cor)
    cel = ws[ini]
    if texto is not None: cel.value = texto
    if fonte: cel.font = fonte
    cel.alignment = alinha
    if borda_:
        from openpyxl.utils import range_boundaries
        c1, r1, c2, r2 = range_boundaries(f"{ini}:{fim}")
        for r in range(r1, r2+1):
            for c in range(c1, c2+1):
                lados = ("t" if r == r1 else "") + ("b" if r == r2 else "") + \
                        ("l" if c == c1 else "") + ("r" if c == c2 else "")
                if lados: ws.cell(r, c).border = borda(borda_, "thin", lados)
    return cel

def rotulo(cor=TEXTO_FRACO, sz=6):
    return Font(name=TITULO, size=sz, bold=True, color=cor)
def valor(sz=14, cor=TEXTO, bold=True, nome=None):
    return Font(name=nome or TITULO, size=sz, bold=bold, color=cor)
def corpo(sz=7, cor=TEXTO, bold=False):
    return Font(name=CORPO, size=sz, bold=bold, color=cor)
