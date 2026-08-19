# -*- coding: utf-8 -*-
"""A aba FICHA, no registro de documento (decisao C6).

Regua no lugar de caixa, secoes numeradas, lombada na lateral, e as tres
reservas com SPARKLINE colorido pela cor de estado (A5). Nenhum numero
derivado e digitado: tudo formula.
"""
from estilo import *
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

COLS, LINHAS = 46, 92

def monta(wb, CAT, DEC, ref):
    ws = base(wb, "FICHA", COLS, LINHAS)
    R = {}
    def dv(f, c1, r1, c2, r2):
        v = DataValidation(type="list", formula1=f, allow_blank=True, showDropDown=False)
        ws.add_data_validation(v); v.add(f"{L(c1)}{r1}:{L(c2)}{r2}")

    lombada(ws, LINHAS, "PROJETO M", "FICHA DE REGISTRO")

    # ------------------------------------------------------------- cabecalho
    pinta(ws, 3, 1, COLS, 5, TINTA)
    txt(ws, 4, 2, "GUILDA · FICHA DE REGISTRO", nome=TITULO, pt=9, cor=BLOCO, ate=(24, 2))
    R["nome"] = txt(ws, 4, 3, None, nome=DOCUMENTO, pt=26, cor=OSSO, ate=(26, 4))
    txt(ws, 4, 5, "o nome do portador vai na CARTEIRA e cai aqui sozinho",
        nome=CORPO, pt=8, cor=LINHA, ate=(26, 5))
    txt(ws, 34, 2, "CATÁLOGO", nome=TITULO, pt=8, cor=TEXTO_FRACO, al="right", ate=(COLS, 2))
    txt(ws, 34, 3,
        f'=IF({ref["carimbo_local"]}={ref["carimbo_central"]},'
        f'"v"&{ref["carimbo_local"]}&" · em dia",'
        f'"⚠ v"&{ref["carimbo_local"]}&" · a atual é a v"&{ref["carimbo_central"]})',
        nome=SERIE, pt=10, cor=BLOCO, al="right", ate=(COLS, 3))
    arte(ws, "pincelada-roxa.png", 3, 6, 1180, 12)

    # ------------------------------------------------------------- 01 quem é
    r = secao(ws, 8, "01", "QUEM É")
    R["caminho"] = campo(ws, 4, r, 8, "caminho", None)
    dv(ref["Caminhos"], 4, r + 1, 12, r + 1)
    R["trilha"] = campo(ws, 14, r, 8, "trilha", None)
    dv(ref["Trilhas"], 14, r + 1, 22, r + 1)
    R["origem"] = campo(ws, 24, r, 8, "origem", None)
    dv(ref["Origens"], 24, r + 1, 32, r + 1)
    R["nivel"] = campo(ws, 34, r, 4, "nível", 2, pt=20, cor=OSSO, nome=TITULO)
    R["xp"] = campo(ws, 40, r, 6, "xp · na mão", 0, pt=12, cor=TEXTO_FRACO, nome=SERIE)
    NIV = "$" + L(34) + "$" + str(r + 1)
    CAM = "$" + L(4) + "$" + str(r + 1)
    r += 4

    # ------------------------------------------------------------- 02 o corpo
    r = secao(ws, r, "02", "O CORPO")
    for i, a in enumerate(CAT["atributos"]["lista"]):
        c1 = 4 + i * 8
        txt(ws, c1, r, a[:3].upper(), nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(c1 + 6, r))
        R["atr_" + a] = txt(ws, c1, r + 1, 0, nome=TITULO, pt=24, cor=OSSO, ate=(c1 + 6, r + 2))
        txt(ws, c1, r + 3, a, nome=CORPO, pt=8, cor=LINHA, ate=(c1 + 6, r + 3))
        regua(ws, c1, r + 4, c1 + 6, LINHA)
    FOR = f'${L(R["atr_Força"].column)}${R["atr_Força"].row}'
    CON = f'${L(R["atr_Constituição"].column)}${R["atr_Constituição"].row}'
    DES = f'${L(R["atr_Destreza"].column)}${R["atr_Destreza"].row}'
    r += 6

    # as tres reservas, com o medidor nativo
    TAB = ref["tabela_caminhos"]
    formulas = [
        ("vida", f'=IF({CAM}="","",(VLOOKUP({CAM},{TAB},3,FALSE)+{CON})'
                 f'+(VLOOKUP({CAM},{TAB},4,FALSE)+{CON})*({NIV}-1))'),
        ("energia", f'=IF({CAM}="","",VLOOKUP({CAM},{TAB},5,FALSE)*{NIV})'),
        ("integridade", f'=20+8*({NIV}-1)'),
    ]
    for nome_r, f_max in formulas:
        txt(ws, 4, r, nome_r.upper(), nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(14, r))
        atual = txt(ws, 4, r + 1, 0, nome=TITULO, pt=22, cor=OSSO, ate=(8, r + 2))
        mx = txt(ws, 10, r + 1, f_max, nome=CORPO, pt=10, cor=TEXTO_FRACO, ate=(14, r + 2))
        ca, cm = f"${L(4)}${r+1}", f"${L(10)}${r+1}"
        txt(ws, 16, r + 1, barra(ca, cm, cor_de_estado(ca, cm)), ate=(30, r + 2))
        tp = campo(ws, 32, r, 5, "temp", 0, pt=11, cor=TEXTO_FRACO, nome=SERIE)
        dl = campo(ws, 39, r, 5, "±", None, pt=11, cor=OSSO, nome=SERIE)
        R[nome_r], R[nome_r + "_max"] = ca, cm
        R[nome_r + "_temp"] = f"${L(32)}${tp.row}"
        R[nome_r + "_delta"] = f"${L(39)}${dl.row}"
        r += 4
    ITG, ITGM = R["integridade"], R["integridade_max"]
    R["estagio_alma"] = f"${L(4)}${r}"
    txt(ws, 4, r,
        f'=IF({ITG}=""," ",IF({ITG}<=0,"estágio 4 · você não é mais você",'
        f'IF({ITG}<={ITGM}/4,"estágio 3 · desvantagem em ataques e TRs",'
        f'IF({ITG}<={ITGM}/2,"estágio 2 · metade do deslocamento, +1 PE por Classe",'
        f'IF({ITG}<={ITGM}*3/4,"estágio 1 · desvantagem em perícias","alma inteira")))))',
        nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(COLS, r))
    r += 3

    # -------------------------------------------------- 03 o que cai sozinho
    r = secao(ws, r, "03", "O QUE CAI SOZINHO")
    MAE = f'(1+COUNTIF({ref["m_maestria"]},"<="&{NIV}))'
    REFI = f'(1+COUNTIF({ref["m_marcos"]},"<="&{NIV}))'
    pos = lambda i: (4 + (i % 4) * 11, r + (i // 4) * 4)
    C_PROT, R_PROT = pos(1); C_EQUI, R_EQUI = pos(2)
    PROT, EQUI = f"${L(C_PROT)}${R_PROT+1}", f"${L(C_EQUI)}${R_EQUI+1}"
    campos = [
        ("defesa",        f'=10+{DES}+{PROT}', TITULO),
        ("proteção",      f'=IF({EQUI}="",FLOOR({REFI}/3,1)+1,{EQUI})', TITULO),
        ("equipamento",   None, DOCUMENTO),
        ("iniciativa",    f'="d20 + "&{DES}', TITULO),
        ("cd de feitiço", f'=10+2+{MAE}', TITULO),
        ("conjuração",    f'="d20 + "&(2+{MAE})', TITULO),
        ("corpo a corpo", f'="d20 + "&{FOR}', TITULO),
        ("à distância",   f'="d20 + "&{DES}', TITULO),
        ("maestria",      f'={MAE}', TITULO),
        ("deslocamento",  "9 m", TITULO),
    ]
    for i, (rot, val, fnt) in enumerate(campos):
        c1, rr = pos(i)
        campo(ws, c1, rr, 9, rot, val, pt=16, cor=OSSO if val else TEXTO, nome=fnt)
        R[rot] = f"${L(c1)}${rr+1}"
    r += 12

    # ------------------------------------------------------- 04 progressao
    r = secao(ws, r, "04", "PROGRESSÃO · você só digita o nível")
    prog = [("espaços de feitiço", f'=2+INT({NIV}/2)+COUNTIF({ref["m_marcos"]},"<="&{NIV})'),
            ("refino de graça",    f'={REFI}'),
            ("classe máxima",      f'=COUNTIF({ref["m_classe"]},"<="&{NIV})'),
            ("classe 0 grátis",    f'=2+COUNTIF({ref["m_classe0"]},"<="&{NIV})')]
    for i, (rot, val) in enumerate(prog):
        c1 = 4 + i * 11
        campo(ws, c1, r, 9, rot, val, pt=16, cor=OSSO, nome=TITULO)
        R[rot] = f"${L(c1)}${r+1}"
    r += 4

    # --------------------------------------------------------- 05 pericias
    r = secao(ws, r, "05", "PERÍCIAS · marque as 8 ou 9 treinadas", c2=30)
    p0 = r
    for i, (nome_p, d) in enumerate(CAT["pericias"].items()):
        cc, rr = 4 + (i // 12) * 14, r + (i % 12)
        txt(ws, cc, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 1, rr, nome_p, nome=DOCUMENTO, pt=10, cor=TEXTO, ate=(cc + 8, rr))
        txt(ws, cc + 9, rr, d["atributo"][:3], nome=TITULO, pt=8, cor=LINHA, ate=(cc + 10, rr))
        cel_atr = f'${L(R["atr_" + d["atributo"]].column)}${R["atr_" + d["atributo"]].row}'
        txt(ws, cc + 11, rr, f'={cel_atr}+IF(${L(cc)}${rr}="",0,{MAE})',
            nome=TITULO, pt=10, cor=OSSO, al="right", ate=(cc + 12, rr))
        regua(ws, cc, rr + 1, cc + 12, TINTA)
    R["perícias treinadas"] = f'=COUNTA(${L(4)}${p0}:${L(4)}${p0+11})' \
                              f'+COUNTA(${L(18)}${p0}:${L(18)}${p0+11})'
    r += 13

    # ------------------------------------------------- 06 oficios e testes
    r = secao(ws, r, "06", "OFÍCIOS E TESTES DE RESISTÊNCIA", c2=34)
    for i, of in enumerate(CAT["oficios"]):
        cc, rr = 4 + (i // 6) * 11, r + (i % 6)
        txt(ws, cc, rr, None, al="center", cor=OSSO)
        txt(ws, cc + 1, rr, of, nome=DOCUMENTO, pt=10, ate=(cc + 9, rr))
        regua(ws, cc, rr + 1, cc + 9, TINTA)
    TRS = [t for t, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)]
    BON = CAT["testes_de_resistencia"]["bonus_se_treinado"]
    for i, t in enumerate(TRS):
        rr = r + i
        txt(ws, 28, rr, None, al="center", cor=OSSO)
        txt(ws, 29, rr, t, nome=DOCUMENTO, pt=10, ate=(36, rr))
        atr = CAT["testes_de_resistencia"][t]["atributo"]
        txt(ws, 37, rr, " ou ".join(a[:3] for a in atr), nome=TITULO, pt=8,
            cor=LINHA, ate=(41, rr))
        cel_atr = f'${L(R["atr_"+atr[0]].column)}${R["atr_"+atr[0]].row}'
        txt(ws, 42, rr, f'={cel_atr}+IF(${L(28)}${rr}="",0,{BON})',
            nome=TITULO, pt=10, cor=OSSO, al="right", ate=(COLS, rr))
        regua(ws, 28, rr + 1, COLS, TINTA)
    arte(ws, "respingo.png", 43, r + 7, 90)
    return R
