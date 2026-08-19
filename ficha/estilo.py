# -*- coding: utf-8 -*-
"""Paleta, fontes e helpers da ficha do Projeto M.

Nada de cor nem de fonte esta escolhido aqui: tudo le do decisoes-ficha.json,
que e o dono das decisoes A5 (a cor de estado) e C4 (as tres fontes).
"""
import json, os
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))

# --- paleta (DESIGN secao 2; os papeis foram corrigidos por contraste) ----
FUNDO       = "120F1D"
PAINEL      = "211C35"
PAINEL_ALTO = "30294D"
LINHA       = "493F54"
BLOCO       = "756588"
TEXTO_FRACO = "998BA9"
TEXTO       = "F4F1F7"

# --- a cor de estado, decisao A5: le os tres degraus, nao os escreve -----
_G = {g["nome"]: g["hex"] for g in DEC["A5_acento"]["degraus"]}
OSSO, AMBAR, VERMELHO = _G["osso"], _G["ambar"], _G["vermelho"]

# --- fontes, decisao C4 --------------------------------------------------
CORPO  = DEC["C4_fontes"]["corpo"]["fonte"]      # Roboto: unica que o celular nao troca
TITULO = DEC["C4_fontes"]["titulo"]["fonte"]     # Oswald: condensada
MARCA  = DEC["C4_fontes"]["marca"]["fonte"]      # Noto Sans JP: so kanji, so no PC

# --- escala tipografica (DESIGN secao 4) --------------------------------
PT_ROTULO  = 9
PT_VALOR   = 11
PT_TITULO  = 12
PT_GRANDE  = 28

LARG_COL   = 4.0     # ~28 px; 46 colunas dao ~1288 px
ALT_LIN    = 15

def fill(c):
    return PatternFill("solid", start_color=c, end_color=c)

def fonte(nome=None, pt=PT_VALOR, cor=TEXTO, negrito=False, italico=False):
    return Font(name=nome or CORPO, size=pt, color=cor, bold=negrito, italic=italico)

def borda(cor=LINHA, estilo="thin", lados="tblr"):
    s = Side(style=estilo, color=cor)
    n = Side(style=None)
    return Border(top=s if "t" in lados else n, bottom=s if "b" in lados else n,
                  left=s if "l" in lados else n, right=s if "r" in lados else n)

CENTRO   = Alignment("center", "center")
CENTRO_Q = Alignment("center", "center", wrap_text=True)
ESQ      = Alignment("left", "center", indent=1)
ESQ_Q    = Alignment("left", "top", wrap_text=True, indent=1)

def pinta(ws, c1, r1, c2, r2, cor):
    """pinta um retangulo, celula a celula (o Sheets ignora fill de range)"""
    f = fill(cor)
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(row=r, column=c).fill = f

def escreve(ws, c, r, valor, **kw):
    cel = ws.cell(row=r, column=c, value=valor)
    cel.font = fonte(kw.get("nome"), kw.get("pt", PT_VALOR), kw.get("cor", TEXTO),
                     kw.get("negrito", False), kw.get("italico", False))
    cel.alignment = kw.get("alinha", CENTRO)
    if kw.get("fundo"):
        cel.fill = fill(kw["fundo"])
    if kw.get("borda"):
        cel.border = kw["borda"]
    if kw.get("formato"):
        cel.number_format = kw["formato"]
    return cel

def junta(ws, c1, r1, c2, r2):
    if (c1, r1) != (c2, r2):
        ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)

def rotulo(ws, c1, r, c2, txt, cor=TEXTO_FRACO, nome=None):
    """rotulo de campo: caixa alta, pequeno.

    Na fonte de titulo por padrao. A MESA passa a de corpo de proposito:
    decisao C4, o app de celular troca qualquer fonte fora da lista curta.
    """
    junta(ws, c1, r, c2, r)
    return escreve(ws, c1, r, txt.upper(), nome=nome or TITULO, pt=PT_ROTULO, cor=cor)
