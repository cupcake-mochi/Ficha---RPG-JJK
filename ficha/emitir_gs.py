# -*- coding: utf-8 -*-
"""Emite o Apps Script que constroi a ficha DENTRO do Google Sheets.

Por que isto existe: o caminho pelo .xlsx morreu numa prova. O registro do
script devolveu 'imagens: 0' -- imagem que vem da importacao do .xlsx nao e
visivel pela API do Sheets, entao nao da nem para consertar o tamanho dela.
E ela nao era a unica coisa que a conversao quebrava: fonte, altura de linha,
caixa de selecao e o fundo das celulas mescladas quebravam tambem.

Aqui a planilha nasce nativa. Nada e traduzido, entao nada se perde na traducao.

O emissor NAO redesenha nada: ele le a mesma pasta de trabalho que o monta.py
ja produz, celula a celula, e vira instrucao. Layout e formula continuam
sendo os mesmos que os dez validadores conferem.
"""
import base64, json, os, re
from openpyxl.worksheet.formula import ArrayFormula
from openpyxl.utils import get_column_letter as L

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ARTE = os.path.join(RAIZ, "arte")
SAIDA = os.path.join(RAIZ, "apps-script", "Ficha.gs")

# a textura sai: 600 KB de base64 para um ruido que nao aparece na tela
ARTE_FORA = {"textura.png"}

def _cor(c):
    if c is None or getattr(c, "rgb", None) is None or not isinstance(c.rgb, str):
        return None
    h = c.rgb[-6:].upper()
    return None if h in ("000000",) else "#" + h

def _linha_alta(pts):
    """altura em PIXEL, medida pela maior letra da linha.

    O .xlsx guarda altura em ponto e o Sheets le em pixel; foi por isso que o
    'd20 + 0' aparecia cortado pela metade. 1 pt = 1.333 px, mais folga.
    """
    return max(21, int(max(pts) * 1.34) + 7) if pts else 21

def _valor(v):
    """o valor como o Sheets tem de receber.

    FORMULA MATRICIAL: o openpyxl devolve um objeto, e o Sheets precisa do texto
    dentro de ARRAYFORMULA -- escrita crua, ela volta como formula comum.

    TEXTO COM CARA DE NUMERO: numa planilha em portugues o ponto e separador de
    milhar, e o setValues le "0.104" como 104. Foi assim que o carimbo de versao
    chegou na planilha viva. O apostrofo segura o texto."""
    if isinstance(v, ArrayFormula):
        t = v.text[1:] if v.text.startswith("=") else v.text
        return "=ARRAYFORMULA(" + t + ")"
    if isinstance(v, str) and re.fullmatch(r"\d+\.\d+", v):
        return "'" + v
    return v

def _alturas(ws, por_fonte):
    """a altura de cada linha em pixel: a que a aba declara, e senao a da maior letra.

    A planilha viva exporta a altura que o Sheets mostra, em ponto, e 1 pt = 4/3 px
    devolve o pixel exato. As linhas espacadoras de 4,5 pt da FICHA so existem assim."""
    out = {str(r): _linha_alta(p) for r, p in por_fonte.items()}
    for k, dim in ws.row_dimensions.items():
        if dim.height:
            out[str(int(k))] = max(2, int(round(dim.height * 4 / 3)))
    return out

def _larguras(ws):
    """as colunas que fogem da largura da coluna A, em faixas de pixel"""
    base = ws.column_dimensions["A"].width or 4.0
    out = []
    for k, dim in ws.column_dimensions.items():
        if dim.width and abs(dim.width - base) > 1e-6:
            out.append([dim.min, dim.max, int(round(dim.width * 7))])
    return sorted(out)

def emitir(wb, ordem, imgs=None, arte_dir=None):
    abas = []
    for nome in ordem:
        ws = wb[nome]
        vals, estilos, chaves, fundos, bordas, merges = [], [], {}, [], [], []
        alturas, max_c, max_r = {}, 0, 0
        for linha in ws.iter_rows():
            for c in linha:
                if c.__class__.__name__ == "MergedCell":
                    continue
                r, col = c.row, c.column
                f, a = c.font, c.alignment
                pintado = _cor(c.fill.start_color) if c.fill and c.fill.fill_type else None
                if c.value is None and pintado is None and (not f or not f.name):
                    continue
                max_c, max_r = max(max_c, col), max(max_r, r)
                if c.value is not None:
                    # formula vai separada: setValues trata o texto como digitado
                    # pelo usuario, e ai a pontuacao segue o idioma da planilha.
                    # Numa planilha em portugues, COUNTIF(a,b) vira erro de
                    # analise. O setFormula sempre usa a notacao americana.
                    vals.append([r, col, _valor(c.value)])
                    alturas.setdefault(r, []).append(f.size or 11)
                if pintado:
                    fundos.append([r, col, pintado])   # comprimido depois, em faixas
                if f and f.name:
                    ch = (f.name, f.size, _cor(f.color), bool(f.bold),
                          a.horizontal or "left", a.vertical or "middle",
                          int(a.textRotation or 0))
                    if ch not in chaves:
                        chaves[ch] = len(estilos)
                        estilos.append(list(ch))
                    estilos_id = chaves[ch]
                    vals[-1].append(estilos_id) if (c.value is not None) else None
                    if c.value is None:
                        continue
                if c.border and c.border.top and c.border.top.style:
                    bordas.append([r, col, _cor(c.border.top.color) or "#493F54"])
        # o fundo em faixas: 15 mil celulas pintadas viravam 15 mil entradas.
        # Vizinhas da mesma cor na mesma linha viram uma faixa so, e a cor de
        # base nem entra -- o script ja comeca com ela.
        BASE = "#120F1D"
        por_linha = {}
        for r, c, cor in fundos:
            if cor != BASE:
                por_linha.setdefault(r, {})[c] = cor
        faixas = []
        for r in sorted(por_linha):
            cols = sorted(por_linha[r])
            ini = ant = cols[0]
            for c in cols[1:] + [None]:
                if c is None or c != ant + 1 or por_linha[r][c] != por_linha[r][ini]:
                    faixas.append([r, ini, ant, por_linha[r][ini]])
                    if c is not None:
                        ini = c
                ant = c if c is not None else ant
        fundos = faixas

        for m in ws.merged_cells.ranges:
            merges.append([m.min_row, m.min_col, m.max_row, m.max_col])
            max_c, max_r = max(max_c, m.max_col), max(max_r, m.max_row)
        dv = []
        for v in ws.data_validations.dataValidation:
            if v.type == "list" and v.formula1:
                for rg in str(v.sqref).split():
                    dv.append([rg, v.formula1.replace("DADOS!", "DADOS!")])
        if imgs is not None:
            # a ficha-v01: a posicao de cada imagem sai do layout.json
            imgs_aba = [[i["lin"], i["col"], i["larg"], i["alt"], i["arquivo"]]
                        for i in imgs.get(nome, [])]
        else:
            import estilo
            imgs_aba = [[i["lin"], i["col"], i["larg"], i["alt"], i["nome"]]
                        for i in estilo.COLOCADAS
                        if i["aba"] == nome and i["nome"] not in ARTE_FORA]
        # as caixas de selecao, medidas: toda celula com VERDADEIRO ou FALSO, em faixas
        bools = sorted((c.column, c.row) for l in ws.iter_rows() for c in l
                       if isinstance(c.value, bool))
        medidas = []
        for col_b, lin_b in bools:
            if medidas and medidas[-1][0] == col_b and medidas[-1][1] + medidas[-1][2] == lin_b:
                medidas[-1][2] += 1
            else:
                medidas.append([col_b, lin_b, 1])
        abas.append({
            "nome": nome, "cols": max(max_c, 12), "rows": max_r + 2,
            "larg": int(round((ws.column_dimensions["A"].width or 4.0) * 7)),
            "vals": vals, "estilos": estilos, "fundos": fundos, "bordas": bordas,
            "merges": merges, "dv": dv, "imgs": imgs_aba, "caixas_medidas": medidas,
            "alturas": _alturas(ws, alturas), "largs": _larguras(ws),
            "oculta": ws.sheet_state == "hidden",
        })
    arte = {}
    pasta = arte_dir or ARTE
    usadas = {im[4] for a in abas for im in a["imgs"]}
    for f in sorted(os.listdir(pasta)):
        if arte_dir and f not in usadas:
            continue
        if f.endswith(".png") and f not in ARTE_FORA and "contato" not in f:
            arte[f] = base64.b64encode(open(os.path.join(pasta, f), "rb").read()).decode()
    return abas, arte

def escrever(wb, ordem, caixas=None, imgs=None, arte_dir=None):
    abas, arte = emitir(wb, ordem, imgs, arte_dir)
    for a in abas:
        medidas = a.pop("caixas_medidas")
        if caixas is None:
            a["caixas"] = medidas
        else:
            a["caixas"] = caixas if a["nome"] == "FICHA" else []
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    corpo = open(os.path.join(AQUI, "modelo.gs.js"), encoding="utf-8").read()
    with open(SAIDA, "w", encoding="utf-8") as fp:
        fp.write("// GERADO POR ficha/emitir_gs.py — não edite este arquivo na mão.\n")
        fp.write("// O layout e as fórmulas moram no gerador Python, que os dez\n")
        fp.write("// validadores conferem. Aqui é só o transporte.\n\n")
        fp.write("var ABAS = " + json.dumps(abas, ensure_ascii=False, separators=(",", ":")) + ";\n\n")
        fp.write("var ARTE = " + json.dumps(arte, ensure_ascii=False,
                                    separators=(",", ":")) + ";\n\n")
        fp.write(corpo)
    return SAIDA, sum(len(a["vals"]) for a in abas), len(arte)
