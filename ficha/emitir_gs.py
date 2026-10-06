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
    desenho = _Img.open(caminho).convert("RGBA")
    img = desenho.resize((bw * 2, bh * 2), filtro)
    buf = io.BytesIO()
    _png_de_uma_cor(img, desenho).save(buf, "PNG", **_PNG_DE_UMA_COR)
    return base64.b64encode(buf.getvalue()).decode()


# 19/09/2026, pedido do Mizuki: as imagens (as pinceladas, a moldura da foto, o selo, as gotinhas) tinham cor
# fixa, e num tema verde o selo vermelho e a pincelada roxa destoavam. Toda a arte da ficha e de UMA cor, e o
# que varia e o alfa (a textura do pincel, o desgaste do selo). Entao ela sai como PNG de PALETA: 256 entradas
# iguais, e o indice de cada pixel e o proprio alfa (tRNS e a rampa 0..255). Trocar a cor da imagem vira trocar
# os 768 bytes da paleta e refazer o CRC do bloco -- coisa que o Apps Script faz em milissegundos, sem
# reprocessar a imagem. Ver pngComCor_ no Codigo.gs.
_PNG_DE_UMA_COR = {"transparency": bytes(range(256)), "optimize": False}
_TOLERANCIA_DE_COR = 48   # quanto a cor de um pixel opaco pode se afastar da media antes de a imagem nao ser "de uma cor"


def _png_de_uma_cor(img, desenho=None):
    """a cor sai do `desenho` (a arte antes de reduzida), quando vem: 03/10/2026, o Pillow 10 reduz o RGBA com o alfa
    pre-multiplicado, e o LANCZOS estoura a cor na beira do traco. A media da arte reduzida saia 1 a 3 tons fora da
    desenhada, e o canto da moldura da foto (ver ficha-v01/moldura_foto.py), que emenda na borda da regua, saia 8E81C9
    em vez de 8A7EC4. O alfa, que e o desenho, continua o da arte reduzida."""
    from PIL import Image as _Img
    opacos = [p for p in (desenho or img).getdata() if p[3] > 128]
    if not opacos:
        raise SystemExit("emitir_gs: imagem de arte sem nenhum pixel opaco")
    media = tuple(round(sum(p[i] for p in opacos) / len(opacos)) for i in range(3))
    pior = max(abs(p[i] - media[i]) for p in opacos for i in range(3))
    if pior > _TOLERANCIA_DE_COR:
        raise SystemExit(f"emitir_gs: a arte tem mais de uma cor (desvio {pior} da media {media}); ela nao pode "
                         "virar PNG de uma cor sem perder o desenho")
    p = _Img.frombytes("P", img.size, bytes(img.getchannel("A").getdata()))
    p.putpalette(list(media) * 256)
    return p

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

_TEXTO_DE_FORMULA = re.compile(r'("(?:[^"]|"")*")')
_REFERENCIA = re.compile(r"(?<![A-Za-z0-9_.])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![A-Za-z0-9_(])")
_MINIMO_DO_BLOCO = 8


def desloca(formula, linhas):
    """a fórmula como ela fica `linhas` abaixo quando o Sheets a copia: a linha de toda referência sem cifrão anda,
    e o que está entre aspas fica como está. O sheets-de-mentira.js faz a mesma conta, do lado do script."""
    def anda(m):
        return m.group(0) if m.group(3) else f"{m.group(1)}{m.group(2)}{int(m.group(4)) + linhas}"
    partes = _TEXTO_DE_FORMULA.split(formula)
    return "".join(p if i % 2 else _REFERENCIA.sub(anda, p) for i, p in enumerate(partes))


def _blocos_para_baixo(vals):
    """os retângulos de fórmula que são a primeira linha copiada para baixo: [primeira linha, coluna, última linha,
    última coluna]. A aba de contas tem uma linha por feitiço com cem fórmulas iguais a menos da linha: escritas
    todas, elas eram meio megabyte de script. Só a primeira linha vai para o ABAS, e o construir() preenche o resto
    com uma cópia, que é o que o Sheets faz quando alguém arrasta a alça da célula."""
    por = {(t[0], t[1]): t for t in vals}
    cols = {}
    for (r, c), t in por.items():
        if isinstance(t[2], str) and t[2].startswith("="):
            cols.setdefault(c, []).append(r)
    corridas = {}
    for c, linhas in cols.items():
        linhas.sort()
        i = 0
        while i < len(linhas):
            ra, j = linhas[i], i
            base = por[(ra, c)]
            while (j + 1 < len(linhas) and linhas[j + 1] == linhas[j] + 1
                   and por[(linhas[j + 1], c)][2] == desloca(base[2], linhas[j + 1] - ra) and por[(linhas[j + 1], c)][3:] == base[3:]):
                j += 1
            if j > i:
                corridas.setdefault((ra, linhas[j]), []).append(c)
            i = j + 1
    blocos = []
    for (ra, rb), cs in corridas.items():
        cs.sort()
        k = 0
        while k < len(cs):
            m = k
            while m + 1 < len(cs) and cs[m + 1] == cs[m] + 1:
                m += 1
            if (rb - ra) * (m - k + 1) >= _MINIMO_DO_BLOCO:
                blocos.append([ra, cs[k], rb, cs[m]])
            k = m + 1
    return sorted(blocos)


# ---------------------------------------------------------------------------------------------
# AS FILEIRAS QUE SÃO CÓPIA. A FICHA AMALDIÇOADA tem treze fileiras de cartas de feitiço iguais, e escrita por
# extenso ela pesava 200 KB no Ficha.gs. A aba declara `copias`: [primeira linha, última linha, [a linha onde cada
# cópia começa]]. No ABAS fica só a primeira fileira, e, de cada cópia, só o que é DIFERENTE dela (a fórmula que
# aponta para a conta de outro feitiço). O Ficha.gs refaz as cópias quando carrega (expandirCopias_, no modelo.gs.js),
# e todo o resto do script continua lendo o ABAS inteiro. `expandir` é a mesma conta, aqui, para quem lê o Ficha.gs
# de fora: o conferir-ficha-xlsx.py e o medidas/ver-aba.py.
# ---------------------------------------------------------------------------------------------
_A1 = re.compile(r"^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$")


def _linhas_do_a1(a1):
    m = _A1.match(a1.replace("$", ""))
    return int(m.group(2)), int(m.group(4) or m.group(2))


def _desce_a1(a1, dl):
    m = _A1.match(a1)
    return f"{m.group(1)}{int(m.group(2)) + dl}" + (f":{m.group(3)}{int(m.group(4)) + dl}" if m.group(3) else "")


def _pares_de_copia(aba):
    """[(primeira linha do molde, última, quantas linhas a cópia desce)]"""
    return [(k[0], k[1], d - k[0]) for k in aba.get("copias") or [] for d in k[2]]


def expandir(aba):
    """a aba com as fileiras copiadas escritas por extenso. Não mexe na que não declara `copias`."""
    pares = _pares_de_copia(aba)
    if not pares:
        return aba
    out = dict(aba)
    vals = list(aba["vals"])
    escritas = {(t[0], t[1]) for t in vals}
    fundos, merges = list(aba["fundos"]), list(aba["merges"])
    bordas = [[b[0], b[1], b[2], list(b[3])] for b in aba.get("bordas") or []]
    dv, caixas, formatos = list(aba.get("dv") or []), list(aba.get("caixas") or []), list(aba.get("formatos") or [])
    for r1, r2, dl in pares:
        dentro = lambda lin: r1 <= lin <= r2
        vals += [[t[0] + dl, t[1]] + list(t[2:]) for t in aba["vals"] if dentro(t[0]) and (t[0] + dl, t[1]) not in escritas]
        fundos += [[f[0] + dl] + list(f[1:]) for f in aba["fundos"] if dentro(f[0])]
        merges += [[m[0] + dl, m[1], m[2] + dl, m[3]] for m in aba["merges"] if dentro(m[0]) and dentro(m[2])]
        for b, molde in zip(bordas, aba.get("bordas") or []):
            b[3] += [_desce_a1(x, dl) for x in molde[3] if all(dentro(l) for l in _linhas_do_a1(x))]
        ja = {d[0] for d in aba.get("dv") or []}
        dv += [[_desce_a1(d[0], dl), d[1]] for d in aba.get("dv") or []
               if all(dentro(l) for l in _linhas_do_a1(d[0])) and _desce_a1(d[0], dl) not in ja]
        caixas += [[c[0], c[1] + dl, c[2]] for c in aba.get("caixas") or [] if dentro(c[1]) and dentro(c[1] + c[2] - 1)]
        ja = {f[0] for f in aba.get("formatos") or []}
        formatos += [[_desce_a1(f[0], dl), f[1]] for f in aba.get("formatos") or []
                     if all(dentro(l) for l in _linhas_do_a1(f[0])) and _desce_a1(f[0], dl) not in ja]
    out.update(vals=vals, fundos=fundos, merges=merges, bordas=bordas)
    for k, v in (("dv", dv), ("caixas", caixas), ("formatos", formatos)):
        if k in aba:
            out[k] = v
    return out


def _forma_canonica(aba):
    """a aba numa forma que não depende da ordem das listas, para comparar duas"""
    lista = lambda xs: sorted(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in xs)
    out = {k: v for k, v in aba.items() if k not in ("vals", "fundos", "merges", "bordas", "dv", "caixas", "formatos")}
    for k in ("vals", "fundos", "merges", "dv", "caixas", "formatos"):
        out[k] = lista(aba.get(k) or [])
    out["bordas"] = [[b[0], b[1], b[2], sorted(b[3])] for b in aba.get("bordas") or []]
    return json.dumps(out, ensure_ascii=False, sort_keys=True)


def compactar(aba):
    """a aba sem o que as cópias repetem do molde. Para se a cópia expandida não devolver a aba inteira, igual."""
    pares = _pares_de_copia(aba)
    if not pares:
        return aba

    def de_onde(lin):
        """quantas linhas acima está a linha do molde de que esta é cópia, ou None"""
        for r1, r2, dl in pares:
            if r1 + dl <= lin <= r2 + dl:
                return dl
        return None
    por = {(t[0], t[1]): t for t in aba["vals"]}
    out = dict(aba)
    out["vals"] = [t for t in aba["vals"]
                   if de_onde(t[0]) is None or list(por.get((t[0] - de_onde(t[0]), t[1]), [None, None])[2:]) != list(t[2:])]
    tem_fundo = {json.dumps(f) for f in aba["fundos"]}
    out["fundos"] = [f for f in aba["fundos"] if de_onde(f[0]) is None or json.dumps([f[0] - de_onde(f[0])] + list(f[1:])) not in tem_fundo]
    tem_mescla = {tuple(m) for m in aba["merges"]}
    out["merges"] = [m for m in aba["merges"] if de_onde(m[0]) is None or de_onde(m[0]) != de_onde(m[2])
                     or (m[0] - de_onde(m[0]), m[1], m[2] - de_onde(m[0]), m[3]) not in tem_mescla]

    def sai_a1(a1, tem):
        l1, l2 = _linhas_do_a1(a1)
        dl = de_onde(l1)
        return dl is not None and dl == de_onde(l2) and _desce_a1(a1.replace("$", ""), -dl) in tem
    out["bordas"] = [[b[0], b[1], b[2], [x for x in b[3] if not sai_a1(x, set(b[3]))]] for b in aba.get("bordas") or []]
    if aba.get("dv"):
        tem_dv = {(d[0], d[1]) for d in aba["dv"]}
        fora = lambda d: (de_onde(_linhas_do_a1(d[0])[0]) is not None and de_onde(_linhas_do_a1(d[0])[0]) == de_onde(_linhas_do_a1(d[0])[1])
                          and (_desce_a1(d[0], -de_onde(_linhas_do_a1(d[0])[0])), d[1]) in tem_dv)
        out["dv"] = [d for d in aba["dv"] if not fora(d)]
    if aba.get("caixas"):
        tem_cx = {tuple(c) for c in aba["caixas"]}
        out["caixas"] = [c for c in aba["caixas"] if de_onde(c[1]) is None or (c[0], c[1] - de_onde(c[1]), c[2]) not in tem_cx]
    if aba.get("formatos"):
        tem_fmt = {(f[0], f[1]) for f in aba["formatos"]}
        out["formatos"] = [f for f in aba["formatos"]
                           if de_onde(_linhas_do_a1(f[0])[0]) is None or (_desce_a1(f[0], -de_onde(_linhas_do_a1(f[0])[0])), f[1]) not in tem_fmt]
    if _forma_canonica(expandir(out)) != _forma_canonica(aba):
        raise SystemExit(f"emitir_gs: as fileiras copiadas da aba {aba['nome']} nao voltam iguais: alguma copia difere do molde "
                         "de um jeito que a copia nao sabe escrever (uma celula que o molde tem e a copia nao, por exemplo)")
    return out


# ---------------------------------------------------------------------------------------------
# AS ABAS QUE MORAM EM OUTRO ARQUIVO (06/10/2026). A aba de invocações sozinha, com uma ficha, levou o Ficha.gs de 760
# para 950 KB, acima do teto de 900 KB por arquivo que o conferir-ficha-xlsx.py guarda; com as doze fichas passaria de
# 1,3 MB. Como o Habilidades.gs, ela vai num arquivo de script à parte: {arquivo: (a variável, as abas)}. O arquivo só
# declara a lista; quem junta é o juntarAbas_ do Ficha.gs (modelo.gs.js), no arquivo que carregar por último, porque o
# Apps Script não promete a ordem em que carrega os arquivos. Cada aba de fora diz depois de qual ela entra (`depois`).
# ---------------------------------------------------------------------------------------------
SEPARADAS = {"Invocacoes.gs": ("ABAS_DA_INVOCACAO", ("INVOCAÇÕES", "DADOS_INVOC"))}


def abas_cruas(caminho=None):
    """o ABAS como está escrito no Ficha.gs e nos arquivos à parte, na ordem em que o script o junta"""
    caminho = caminho or SAIDA
    abas = json.loads(re.search(r"var ABAS = ([\s\S]*?);\n\nvar ARTE = ", open(caminho, encoding="utf-8").read()).group(1))
    for arq, (var, _) in SEPARADAS.items():
        p = os.path.join(os.path.dirname(caminho), arq)
        if not os.path.exists(p):
            continue
        for e in json.loads(re.search(r"var %s = ([\s\S]*?);\n\nif \(typeof juntarAbas_" % var, open(p, encoding="utf-8").read()).group(1)):
            i = next((k for k, a in enumerate(abas) if a["nome"] == e.get("depois")), len(abas) - 1)
            abas.insert(i + 1, e)
    return abas


def abas_do_script(caminho=None):
    """o ABAS como o script o usa: as abas dos arquivos à parte no lugar, e as fileiras copiadas escritas por extenso"""
    return [expandir(a) for a in abas_cruas(caminho)]


def emitir(wb, ordem, imgs=None, arte_dir=None, limpa=None, extras=None):
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
        # A base e a cor pintada que a aba mais usa -- None (celula sem pintura) nunca conta, senao
        # vira a base de verdade numa aba com mais vazio que pintura, e o Ficha.gs manda o script
        # pintar o retangulo inteiro de "sem cor": setBackgrounds trava, e a aba sai sem nada. 17/09/2026,
        # achado do Mizuki no GLOSSARIO -- a DADOS_INV tinha o mesmo problema, oculta, e nunca apareceu.
        _fundo_cnt_pintado = Counter({c: n for c, n in fundo_cnt.items() if c is not None})
        BASE = _fundo_cnt_pintado.most_common(1)[0][0] if _fundo_cnt_pintado else "#120F1D"
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
        # Duas linhas de folga embaixo do que tem conteúdo, menos nas abas com lombada: ali a faixa de
        # tinta (colunas A:B) tem de ir até a última linha, e uma folga que nenhuma célula pinta ficaria
        # com o fundo comum — a lombada aparecia cortada nas paletas claras (19/09/2026). Essas duas
        # abas terminam no fim da lombada, ver ficha-v01/correcoes_borda.py.
        ncols, nrows = max(max_c, 12), max_r + (0 if nome in ("FICHA", "FICHA PESSOAL", "FICHA AMALDIÇOADA", "INVOCAÇÕES", "INVOCAÇÃO") else 2)
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
        # 01/10/2026: a nota da caixa, o grupo de linhas e de colunas, o formato de número, a cor de aviso e as
        # faixas travadas. Só a aba que nasce no gerador (a FICHA PESSOAL) declara, e as outras saem como saíam.
        abas[-1].update((extras or {}).get(nome, {}))
        # a aba que pede: as fórmulas que são a linha de cima copiada saem do ABAS, e fica a lista dos retângulos
        if abas[-1].get("abaixo"):
            blocos = _blocos_para_baixo(vals)
            fora = {(r, c) for ra, c1, rb, c2 in blocos for r in range(ra + 1, rb + 1) for c in range(c1, c2 + 1)}
            abas[-1]["vals"] = [t for t in vals if (t[0], t[1]) not in fora]
            abas[-1]["abaixo"] = blocos
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

_LIMIAR_LINHA = 2000


def _sem_linha_gigante(obj, nivel=0):
    """json.dumps que nunca deixa uma linha passar de ~2000 caracteres.

    Achado em 18/09/2026: o `Ficha.gs` compacto (um `var ABAS = [...]` numa
    linha só) tinha uma linha de 256 mil caracteres e outra (o `ARTE`, com a
    arte em base64) de 131 mil — o navegador do Mizuki fechava sozinho uns
    segundos depois de rodar `construir()`. O indent padrão do `json.dumps`
    resolve a linha, mas explode o TAMANHO do arquivo (testado: o ABAS sozinho
    ia pra 900 KB, perto do limite de ~1 MB do Apps Script) porque expande
    TODO nível, até `[1,1,"",0]`. Aqui só desce um nível quando o pedaço
    inteiro, compacto, já passaria do piso — uma lista de milhares de células
    vira uma célula por linha, mas cada célula continua numa linha só.

    Uma STRING sozinha que já é maior que o piso (a arte em base64 de uma
    imagem grande) vira pedaços concatenados por `+` — deixa de ser um valor
    JSON válido sozinho, mas o Apps Script lê `var ARTE = {...}` como CÓDIGO,
    não como JSON, então roda igual. O `conferir-ficha-xlsx.py` cola os
    pedaços de volta (troca `"+"` por nada) antes de validar como JSON.
    """
    compacto = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if len(compacto) <= _LIMIAR_LINHA:
        return compacto
    ind, ind0 = "  " * (nivel + 1), "  " * nivel
    if isinstance(obj, list):
        # 01/10/2026: os itens curtos vão vários por linha, até o piso. Com um por linha, as doze mil células do ABAS
        # gastavam um quinto do arquivo só em recuo e quebra de linha, e o Mizuki reclamou do tamanho do script.
        # Item que desceu de nível (tem quebra de linha dentro) continua sozinho na linha dele.
        linhas, atual = [], ""
        for x in obj:
            t = _sem_linha_gigante(x, nivel + 1)
            if "\n" in t or len(t) > _LIMIAR_LINHA // 2:
                if atual:
                    linhas.append(atual); atual = ""
                linhas.append(t)
            elif atual and len(atual) + 1 + len(t) > _LIMIAR_LINHA:
                linhas.append(atual); atual = t
            else:
                atual = atual + "," + t if atual else t
        if atual:
            linhas.append(atual)
        return "[\n" + ",\n".join(ind + l for l in linhas) + "\n" + ind0 + "]"
    if isinstance(obj, dict):
        partes = [ind + json.dumps(k, ensure_ascii=False) + ":" + _sem_linha_gigante(v, nivel + 1)
                  for k, v in obj.items()]
        return "{\n" + ",\n".join(partes) + "\n" + ind0 + "}"
    if isinstance(obj, str) and json.dumps(obj, ensure_ascii=False) == '"' + obj + '"':
        # string "limpa" (sem aspas, barra ou caractere de controle pra escapar) — a arte em
        # base64 é sempre assim. Corta em pedaços de 4000 e concatena com "+"; uma string que
        # precisasse de escape fica de fora desse corte e desce pro "fica como está" de baixo.
        pedaco = 4000
        partes = [obj[i:i + pedaco] for i in range(0, len(obj), pedaco)]
        return (" +\n" + ind).join('"' + p + '"' for p in partes)
    return compacto  # string/número atômico que já é maior que o piso sozinho: fica como está


def escrever(wb, ordem, caixas=None, imgs=None, arte_dir=None, limpa=None, extras=None):
    abas, arte = emitir(wb, ordem, imgs, arte_dir, limpa, extras)
    for a in abas:
        medidas = a.pop("caixas_medidas")
        if caixas is None:
            a["caixas"] = medidas
        else:
            a["caixas"] = caixas if a["nome"] == "FICHA" else []
    abas = [compactar(a) for a in abas]
    celulas = sum(len(a["vals"]) for a in abas)
    # as abas que moram em outro arquivo saem do ABAS, cada uma dizendo depois de qual ela entra
    fora = {}
    for arq, (var, nomes) in SEPARADAS.items():
        saem = [a for a in abas if a["nome"] in nomes]
        for a in saem:
            antes = [b["nome"] for b in abas[:abas.index(a)] if b["nome"] not in nomes]
            a["depois"] = antes[-1] if antes else None
        if saem:
            fora[arq] = (var, saem)
            abas = [a for a in abas if a["nome"] not in nomes]
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    corpo = open(os.path.join(AQUI, "modelo.gs.js"), encoding="utf-8").read()
    with open(SAIDA, "w", encoding="utf-8") as fp:
        fp.write("// GERADO POR ficha/emitir_gs.py — não edite este arquivo na mão.\n")
        fp.write("// O layout e as fórmulas moram no gerador Python, que os dez\n")
        fp.write("// validadores conferem. Aqui é só o transporte.\n\n")
        fp.write("var ABAS = " + _sem_linha_gigante(abas) + ";\n\n")
        fp.write("var ARTE = " + _sem_linha_gigante(arte) + ";\n\n")
        fp.write(corpo)
    for arq, (var, saem) in fora.items():
        with open(os.path.join(os.path.dirname(SAIDA), arq), "w", encoding="utf-8") as fp:
            fp.write("// GERADO POR ficha/emitir_gs.py — não edite este arquivo na mão.\n")
            fp.write("// As abas " + " e ".join(a["nome"] for a in saem) + ", que não cabem no Ficha.gs. Cole este arquivo no mesmo projeto\n")
            fp.write("// do Apps Script, ao lado do Ficha.gs e do Codigo.gs: sem ele a ficha é montada sem essas abas.\n\n")
            fp.write(f"var {var} = " + _sem_linha_gigante(saem) + ";\n\n")
            fp.write(f"if (typeof juntarAbas_ === 'function') juntarAbas_({var});\n")
    return SAIDA, celulas, len(arte)
