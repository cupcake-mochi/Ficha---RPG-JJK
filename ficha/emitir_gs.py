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
    """a cor em #RRGGBB, e None quando nao ha cor. O openpyxl escreve 'sem cor' como 00000000; o
    preto e FF000000. Ate 15/09/2026 os dois viravam None, e o texto preto da planilha viva saia
    claro no Sheets."""
    if c is None or not isinstance(getattr(c, "rgb", None), str) or c.rgb.upper() == "00000000":
        return None
    return "#" + c.rgb[-6:].upper()


_PESO_TRACO = {"hair": 0, "dotted": 1, "dashed": 2, "thin": 3, "mediumDashed": 4, "medium": 5,
               "double": 6, "thick": 7}


def _faixas_de_borda(lados, dono):
    """{(lado, traco, cor): celulas} -> [[lado, traco, cor, [A1, ...]]].

    A borda de celula que mora numa mesclagem vai para o BLOCO inteiro. O Sheets so guarda formato no
    canto de cima a esquerda da mesclagem, e o .xlsx guarda a borda da direita e a de baixo nas
    celulas de dentro: aplicada nelas, ela sumia. As soltas vizinhas viram uma faixa -- a de cima e a
    de baixo pela linha, a da esquerda e a da direita pela coluna. O traco mais grosso vai por
    ultimo, para ganhar a aresta que duas bordas dividem."""
    from openpyxl.utils import get_column_letter as L
    out = []
    for (lado, traco, cor), todas in sorted(lados.items(), key=lambda kv: (_PESO_TRACO.get(kv[0][1], 3), kv[0])):
        blocos, cels = set(), []
        for r, c in todas:
            if (r, c) in dono:
                blocos.add(dono[(r, c)])
            else:
                cels.append((r, c))
        por = {}
        for r, c in cels:
            fixo, anda = (r, c) if lado in ("top", "bottom") else (c, r)
            por.setdefault(fixo, []).append(anda)
        a1 = []
        for fixo in sorted(por):
            seq = sorted(por[fixo])
            ini = ant = seq[0]
            for x in seq[1:] + [None]:
                if x is None or x != ant + 1:
                    if lado in ("top", "bottom"):
                        a1.append(f"{L(ini)}{fixo}" if ini == ant else f"{L(ini)}{fixo}:{L(ant)}{fixo}")
                    else:
                        a1.append(f"{L(fixo)}{ini}" if ini == ant else f"{L(fixo)}{ini}:{L(fixo)}{ant}")
                    ini = x
                if x is not None:
                    ant = x
        out.append([lado, traco, cor, sorted(blocos) + a1])
    return out


def _caixa(im, larg, largs, alturas):
    """A caixa de celulas em que a imagem entra, no mesmo pixel que o script aplica: as colunas e as
    linhas cujo meio cai dentro do retangulo que ela ocupa na planilha viva. A faixa mais fina que
    meia linha fica na linha onde cai o meio dela. Devolve (lin1, col1, lin2, col2, larg, alt)."""
    def cpx(c):
        for c1, c2, px in largs:
            if c1 <= c <= c2:
                return px
        return larg
    def rpx(r):
        return alturas.get(str(r), 21)
    def faixa(ini, tam, px):
        dentro, pos, i = [], 0, 1
        while pos < ini + tam:
            if ini <= pos + px(i) / 2 <= ini + tam:
                dentro.append(i)
            pos += px(i)
            i += 1
        if not dentro:
            pos, i = 0, 1
            while pos + px(i) <= ini + tam / 2:
                pos += px(i)
                i += 1
            dentro = [i]
        return dentro
    x0 = sum(cpx(c) for c in range(1, im["col"])) + im.get("desloc_x", 0)
    y0 = sum(rpx(r) for r in range(1, im["lin"])) + im.get("desloc_y", 0)
    cols, lins = faixa(x0, im["larg"], cpx), faixa(y0, im["alt"], rpx)
    return (lins[0], cols[0], lins[-1], cols[-1],
            sum(cpx(c) for c in cols), sum(rpx(r) for r in lins))


def _redimensiona(caminho, bw, bh):
    """a arte no formato exato da caixa, com o dobro dos pixels. Dentro da celula o Sheets encaixa a
    imagem sem esticar, e a faixa de pincel da planilha viva e esticada."""
    import io
    from PIL import Image as _Img
    filtro = getattr(getattr(_Img, "Resampling", _Img), "LANCZOS")
    img = _Img.open(caminho).convert("RGBA").resize((bw * 2, bh * 2), filtro)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

def _linha_alta(pts):
    """altura em PIXEL, medida pela maior letra da linha.

    O .xlsx guarda altura em ponto e o Sheets le em pixel; foi por isso que o
    'd20 + 0' aparecia cortado pela metade. 1 pt = 1.333 px, mais folga.
    """
    return max(21, int(max(pts) * 1.34) + 7) if pts else 21

_EMBRULHO = re.compile(r'^=IFERROR\(__xludf\.DUMMYFUNCTION\("(.*)"\),(.*)\)$', re.S)


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
    if isinstance(v, str):
        # FUNCAO QUE O EXCEL NAO TEM: o Sheets exporta a SPARKLINE como
        # IFERROR(__xludf.DUMMYFUNCTION("..."),""), com as aspas dobradas. Remontada assim, ela falha
        # calada e sobra o "" -- foram as barras de vida, energia e integridade vazias em 15/09/2026.
        m = _EMBRULHO.match(v)
        if m:
            return "=" + m.group(1).replace('""', '"').strip()
    if isinstance(v, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", v):
        # e o inteiro tambem: o "1" de secao da INVOCACAO voltava da ida e volta como numero
        return "'" + v
    return v

def _alturas(ws, por_fonte, so_declaradas=False):
    """a altura de cada linha em pixel: a que a aba declara, e senao a da maior letra.

    A planilha viva exporta a altura que o Sheets mostra, em ponto, e 1 pt = 4/3 px
    devolve o pixel exato. As linhas espacadoras de 4,5 pt da FICHA so existem assim."""
    # A ficha-v01 so leva a altura que a planilha viva declara: a da maior letra era do gerador
    # aposentado, e dava 27 px na linha 9 da CARTEIRA e 23 px na DADOS_INV, que a viva tem em 21.
    out = {} if so_declaradas else {str(r): _linha_alta(p) for r, p in por_fonte.items()}
    for k, dim in ws.row_dimensions.items():
        if dim.height:
            out[str(int(k))] = max(2, int(round(dim.height * 4 / 3)))
    return out

def _px_largura(w, limpa=None):
    """a largura do .xlsx em pixel, pela conta do Sheets: pixel = 8 x largura - 1, medida em
    medidas/larguras-sheets.json. Ate 15/09/2026 era 7 x largura, e cada ida e volta pelo Sheets
    estreitava as colunas da INVOCACAO, do CATALOGO, da DADOS e da DADOS_INV em 12%. A largura que a
    limpeza 2 do extrator reescreveu volta a ser a exportada antes da conta."""
    if limpa and abs(w - limpa["no_layout"]) < 1e-6:
        w = limpa["exportada"]
    return int(round(8 * w - 1))

def _larguras(ws, limpa=None):
    """as colunas que fogem da largura da coluna A, em faixas de pixel"""
    base = ws.column_dimensions["A"].width or 4.0
    out = []
    for k, dim in ws.column_dimensions.items():
        if dim.width and abs(dim.width - base) > 1e-6:
            out.append([dim.min, dim.max, _px_largura(dim.width, limpa)])
    return sorted(out)

def emitir(wb, ordem, imgs=None, arte_dir=None, limpa=None):
    from collections import Counter
    import estilo as _est
    # o formato de fabrica da celula no script: a vazia com este formato nao precisa ser escrita
    padrao = (_est.CORPO, _est.PT_VALOR, "#" + _est.TEXTO.upper())
    abas, redimensionar = [], {}
    for nome in ordem:
        ws = wb[nome]
        vals, estilos, chaves, fundos, bordas, merges = [], [], {}, [], [], []
        alturas, max_c, max_r = {}, 0, 0
        dono = {}
        for m in ws.merged_cells.ranges:
            for rr in range(m.min_row, m.max_row + 1):
                for cc in range(m.min_col, m.max_col + 1):
                    dono[(rr, cc)] = m.coord
        bordas_lados, fundo_cnt = {}, Counter()
        for linha in ws.iter_rows():
            for c in linha:
                r, col = c.row, c.column
                # A borda sai de TODA celula, e dos quatro lados: a mesclada carrega a borda do bloco,
                # e a vazia carrega a da caixa de digitar. Ate 15/09/2026 so a de cima entrava, e so
                # em celula com valor -- a FICHA saia do Sheets com 1615 lados de borda, e a viva tem 6272.
                if c.border:
                    for lado in ("top", "bottom", "left", "right"):
                        s = getattr(c.border, lado)
                        if s is not None and s.style:
                            bordas_lados.setdefault((lado, s.style, _cor(s.color) or "#000000"),
                                                    set()).add((r, col))
                if c.__class__.__name__ == "MergedCell":
                    continue
                f, a = c.font, c.alignment
                pintado = _cor(c.fill.start_color) if c.fill and c.fill.fill_type else None
                fundo_cnt[pintado] += 1
                if c.value is None and pintado is None and (not f or not f.name):
                    continue
                max_c, max_r = max(max_c, col), max(max_r, r)
                if c.value is not None:
                    # a formula vai separada, com setFormula, e o construir() monta em ingles
                    vals.append([r, col, _valor(c.value)])
                    alturas.setdefault(r, []).append(f.size or 11)
                if pintado:
                    fundos.append([r, col, pintado])   # comprimido depois, em faixas
                if f and f.name:
                    ch = (f.name, f.size, _cor(f.color), bool(f.bold),
                          a.horizontal or "left",
                          "middle" if a.vertical in (None, "center") else a.vertical,
                          int(a.textRotation or 0), bool(f.italic), bool(a.wrap_text))
                    if c.value is None:
                        # A celula vazia entra quando o formato dela nao e o de fabrica do script: a
                        # caixa de digitar centrada, a que quebra texto, a de fonte propria. Ate
                        # 15/09/2026 nenhuma entrava, e as caixas vazias saiam alinhadas a esquerda.
                        if ch == padrao + (False, "left", "middle", 0, False, False):
                            continue
                        vals.append([r, col, ""])
                    if ch not in chaves:
                        chaves[ch] = len(estilos)
                        estilos.append(list(ch))
                    vals[-1].append(chaves[ch])
        # o fundo em faixas: 15 mil celulas pintadas viravam 15 mil entradas.
        # Vizinhas da mesma cor na mesma linha viram uma faixa so, e a cor de
        # base nem entra -- o script ja comeca com ela.
        # A base e o fundo que a aba mais usa, e None quando ela e sem pintura: a DADOS_INV da viva
        # tem 2680 celulas sem pintura e 1170 escuras, e saia pintada por inteiro.
        BASE = fundo_cnt.most_common(1)[0][0] if fundo_cnt else "#120F1D"
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
        larg_px = _px_largura(ws.column_dimensions["A"].width or 4.0, limpa)
        largs_px, alt_px = _larguras(ws, limpa), _alturas(ws, alturas, so_declaradas=imgs is not None)
        ncols, nrows = max(max_c, 12), max_r + 2
        if imgs is not None:
            # a ficha-v01: a imagem entra DENTRO da celula, numa caixa medida no pixel do script, e a
            # arte vai no formato da caixa. [lin1, col1, lin2, col2, arte]
            imgs_aba = []
            for i in imgs.get(nome, []):
                l1, c1, l2, c2, bw, bh = _caixa(i, larg_px, largs_px, alt_px)
                chave = f"{i['arquivo'][:-4]}-{bw}x{bh}.png"
                redimensionar[chave] = (i["arquivo"], bw, bh)
                imgs_aba.append([l1, c1, l2, c2, chave])
                ncols, nrows = max(ncols, c2), max(nrows, l2)
        else:
            import estilo
            imgs_aba = [[i["lin"], i["col"], i["lin"], i["col"], i["nome"]]
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
            "nome": nome, "cols": ncols, "rows": nrows, "larg": larg_px, "padrao": list(padrao), "fundo_base": BASE,
            "vals": vals, "estilos": estilos, "fundos": fundos,
            "bordas": _faixas_de_borda(bordas_lados, dono),
            "merges": merges, "dv": dv, "imgs": imgs_aba, "caixas_medidas": medidas,
            "alturas": alt_px, "largs": largs_px,
            "oculta": ws.sheet_state == "hidden",
        })
    arte = {}
    pasta = arte_dir or ARTE
    if arte_dir:
        for chave, (arquivo, bw, bh) in sorted(redimensionar.items()):
            arte[chave] = _redimensiona(os.path.join(pasta, arquivo), bw, bh)
    else:
        for f in sorted(os.listdir(pasta)):
            if f.endswith(".png") and f not in ARTE_FORA and "contato" not in f:
                arte[f] = base64.b64encode(open(os.path.join(pasta, f), "rb").read()).decode()
    return abas, arte

def escrever(wb, ordem, caixas=None, imgs=None, arte_dir=None, limpa=None):
    abas, arte = emitir(wb, ordem, imgs, arte_dir, limpa)
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
