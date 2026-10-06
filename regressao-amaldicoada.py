# -*- coding: utf-8 -*-
"""Regressao da FICHA AMALDIÇOADA: preenche fichas na planilha GERADA, manda o LibreOffice recalcular e compara com a
regra, escrita aqui de novo, em Python, a partir do catalogo e do tecnica-do-livro.json.

Quem esta sendo julgada e a planilha: as formulas da aba e as contas dela na DADOS_AM. A regra daqui e a do capitulo
de Fundamento, do jeito que o estudo aprovado a escreveu (mockup/ficha-amaldicoada-estudo.modelo.html), sem ler
nenhuma formula e sem usar nenhuma tabela que o gerador montou.

  1. Os 33 feiticos prontos do livro: cada um sai com os dados que o livro imprime, e sem erro.
  2. Fichas sorteadas, em varios niveis e com varias Familias Livres e Fechadas: toda caixa de toda carta bate com a
     regra, a certa e a errada (o sorteio monta feitico ilegal de proposito, para as mensagens de erro aparecerem).
  3. O resto da aba: o Orcamento, o indice de precos, a Classe 0, a Tecnica Maxima, o Dominio, as Passivas, as
     aptidoes e os pactos.
  4. O Ficha.gs: montada no Sheets de mentira, a aba fica com as mesmas formulas da planilha gerada, celula a celula
     (e a prova de que o preenchimento para baixo e as fileiras copiadas nao trocam nenhuma).

    python3 regressao-amaldicoada.py
"""
import json, math, os, random, re, shutil, subprocess, sys, tempfile
from openpyxl import load_workbook

ARQ = "ficha-v01/ficha-projeto-m-0.1.xlsx"
if not os.path.exists(ARQ):
    print("gere a ficha antes:  python3 ficha-v01/monta.py"); sys.exit(1)
sys.path.insert(0, "ficha-v01")
import indice_ficha as ix, ficha_amaldicoada as fa

CAT = json.load(open("catalogo-projeto-m.json", encoding="utf-8"))
TEC = json.load(open("ficha-v01/tecnica-do-livro.json", encoding="utf-8"))
DEC = json.load(open("decisoes-ficha.json", encoding="utf-8"))
G = fa.geometria()
ABA, DAM = fa.NOME, fa.DADOS_AM
FALHAS = []


def checa(desc, cond, det=""):
    print(f"  [{'OK' if cond else 'FALHA'}] {desc}" + ("" if cond else f"  <- {det}"))
    if not cond:
        FALHAS.append(desc)


# ---------------------------------------------------------------------------------------------
# A regra, escrita de novo. Nada daqui vem do ficha_amaldicoada.py, fora os nomes das caixas.
# ---------------------------------------------------------------------------------------------
PROG = CAT["progressao"]
_lim = lambda chave: [int(x) for x in re.search(r"\(([\d,]+)\)", PROG["formulas"][chave]).group(1).split(",")]
conta = lambda lista, n: sum(1 for x in lista if x <= n)
maior_classe = lambda n: conta(_lim("classe"), n)
maestria = lambda n: 1 + conta(_lim("maestria"), n)
marcos = lambda n: conta(PROG["marcos"], n)
liberacoes = lambda n: conta(TEC["liberacao"]["niveis"], n)
PESO = {"Leve": 1, "Media": 2, "Média": 2, "Pesada": 3}
NOME_PESO = {1: "Leve", 2: "Média", 3: "Pesada"}


def preco(peso, c):
    return math.ceil(c / 2) if peso == 1 else c if peso == 2 else math.ceil(c * 1.5)


def preco_da_peca(peso, c, livre):
    return max(1, preco(peso, c) - math.ceil(c / 2)) if livre else preco(peso, c)


def limite_de_melhorias(c):
    return 2 if c <= 2 else 3 if c <= 4 else 4


PECAS = {}
for _n, _m in CAT["melhorias"].items():
    if _n == "Condição":
        for _c, _p in CAT["condicoes"].items():
            PECAS[_c] = {"familia": "Controle", "peso": PESO[_p]}
    elif _n == "Efeito Próprio":
        for _p in ("Leve", "Média", "Pesada"):
            PECAS[f"Efeito Próprio ({_p})"] = {"familia": None, "peso": PESO[_p]}
    else:
        PECAS[_n] = {"familia": _m["familia"], "peso": PESO[_m["peso"]]}
RESTR = {}
for _n, _r in CAT["restricoes"].items():
    _niveis = _r["devolve"].split(" ou ")
    for _nv in _niveis:
        RESTR[_n if len(_niveis) == 1 else f"{_n} ({NOME_PESO[PESO[_nv]]})"] = {"nome": _n, "devolve": PESO[_nv]}
FREQUENCIA = ["Uma Vez", "Condicional", "Aquecer", "Dívida"]
FORMAS = CAT["formas"]
POR_TR = ["Explosão", "Aura", "Cone", "Linha"]
PARES = [(p["a"], p["b"]) for p in DEC["A3_incompatibilidades"]["pares"]]
_m = lambda t: float(re.search(r"\d+(?:,\d+)?", t).group(0).replace(",", ".")) if re.search(r"\d", t) else math.inf
ESC = {k: [_m(x) for x in v] for k, v in TEC["escadas"].items()}


def metros(x):
    return TEC["escadas"]["alcance"][-1] if x == math.inf else (str(int(x)) if float(x).is_integer() else str(x).replace(".", ",")) + " m"


def sobe(escada, base, degraus):
    if base in escada:
        i = escada.index(base)
    else:
        if not degraus:
            return base
        i = next(k for k, d in enumerate(escada) if d >= base) - 1
    return escada[min(len(escada) - 1, i + degraus)]


def ini(t):
    """toda caixa da aba abre em maiúscula (pedido do Mizuki em 01/10/2026)"""
    return t[:1].upper() + t[1:]


def alcance(f, c):
    """o texto de alcance de um feitiço lançado na Classe c (0 é a Classe 0)"""
    return ini(_alcance(f, c))


def _alcance(f, c):
    faixa = 0 if c == 0 else 1 if c <= 5 else 2
    mel = [x for x in f["mel"] if x]
    longe = mel.count("Longe") + 3 * mel.count("Muito Longe")
    maior = mel.count("Maior") + 3 * mel.count("Muito Maior")
    alvos = mel.count("Mais Um")
    extra = (f" · +{alvos} alvo{'s' if alvos > 1 else ''}" if alvos else "") + (f" · {c + 1} tiros" if "Rajada" in mel else "")
    forma = f["forma"]
    if forma == "Projétil":
        return metros(sobe(ESC["alcance"], [9, 18, 36][faixa], longe)) + ", um alvo" + extra
    if forma == "Toque":
        return "1,5 m, um alvo" + extra
    if forma == "Explosão":
        return "raio " + metros(sobe(ESC["raio"], [3, 3, 4.5][faixa], maior)) + ", a " + metros(sobe(ESC["alcance"], [9, 18, 36][faixa], longe))
    if forma == "Aura":
        return "raio " + metros(sobe(ESC["raio"], [3, 3, 4.5][faixa], maior)) + ", em você"
    if forma == "Cone":
        return "cone de " + metros(sobe(ESC["comprimento"], [3, 4.5, 9][faixa], maior + longe))
    if forma == "Linha":
        return "linha de " + metros(sobe(ESC["comprimento"], [9, 18, 30][faixa], maior + longe)) + " por 1,5 m"
    if forma == "Cura":
        return "um aliado a " + metros(sobe(ESC["alcance"], [9, 9, 18][faixa], longe))
    if forma == "Apoio":
        return "um aliado a " + metros(sobe(ESC["alcance"], [4.5, 9, 18][faixa], longe))
    if forma == "Onda":                       # livro reconstruído: na Classe 6 a base do raio passa a 4,5 m
        return "raio " + metros(sobe(ESC["raio"], [3, 3, 4.5][faixa], maior)) + ", em você"
    return "fora de combate"


# as bases de alcance escritas acima sao as da tabela `Base por Classe` do livro: confere antes de usar
def _bases_do_livro():
    b = TEC["base_por_classe"]
    n = lambda t: [_m(x) for x in re.findall(r"\d+(?:,\d+)? m|\d+(?:,\d+)?(?= ×)", t)]
    esperado = {"Projétil": ([9], [18], [36]), "Explosão": ([3, 9], [3, 18], [4.5, 36]), "Aura": ([3], [3], [4.5]), "Cone": ([3], [4.5], [9]),
                "Linha": ([9, 1.5], [18, 1.5], [30, 1.5]), "Apoio": ([4.5], [9], [18])}
    return all(tuple(n(b[f][k]) for k in ("classe_0", "classes_1_a_5", "classes_6_e_7")) == tuple(esperado[f]) for f in esperado) \
        and n(b["Cura"]["classes_1_a_5"]) == [9] and n(b["Cura"]["classes_6_e_7"]) == [18]


def texto_do_dano(forma, dados, depois=0, curto=False):
    """o dano na caixa da carta abre em maiúscula; o curto é o do Ampliar, no meio da frase"""
    t = _texto_do_dano(forma, dados, depois, curto)
    return t if curto else ini(t)


def _texto_do_dano(forma, dados, depois=0, curto=False):
    if forma == "Efeito":
        return "sem dano"
    if forma == "Apoio":
        return f"{3 * dados} de vida temp."
    cura = forma in ("Cura", "Onda")
    if not dados:
        return "sem cura" if cura else "sem dano"
    t = ("cura " if cura else "") + f"{dados}d8"
    return t if curto else t + f" = {math.floor(dados * 4.5)}" + (f" · +{depois}d8" if depois else "")


def monta(f, c, fam, nivel, lib=False, vaga=1):
    """a carta de um feitiço lançado na Classe c: os números, os textos e os avisos, na ordem em que a ficha os escreve"""
    livre, fechada = (lambda k: fam.get(k) == "Livre"), (lambda k: fam.get(k) == "Fechada")
    forma, maxc, libs = FORMAS[f["forma"]], maior_classe(nivel), liberacoes(nivel)
    erros, avisos, gasto, precos = [], [], 0, []
    if lib and vaga > libs:
        erros.append(f"O nível {nivel} dá {libs} Liberação Máxima")
    if c > maxc:
        erros.append(f"Classe {c}: o nível {nivel} libera até a {maxc}")
    if forma["custa"]:
        gasto += preco_da_peca(PESO[forma["custa"]], c, livre(forma["familia"]))
    if forma["familia"] and fechada(forma["familia"]):
        erros.append(f"Família Fechada: a Forma {f['forma']}")
    mel = [x for x in f["mel"] if x]
    for nome in f["mel"]:
        if not nome:
            precos.append("")
            continue
        p = PECAS[nome]
        lv = bool(p["familia"]) and livre(p["familia"])
        pr = preco_da_peca(p["peso"], c, lv)
        gasto += pr
        precos.append(f"−{pr} · {NOME_PESO[p['peso']]}" + (" · Livre" if lv else ""))
        if p["familia"] and fechada(p["familia"]):
            erros.append(f"Família Fechada: {nome}")
    if len(mel) > limite_de_melhorias(c):
        erros.append(f"{len(mel)} Melhorias: a Classe {c} aceita {limite_de_melhorias(c)}")
    emb = "embutido" in forma
    res = [RESTR[x] for x in f["res"] if x]
    nr = len(res) + int(emb)
    if nr > 2:
        erros.append(f"{nr} Restrições" + (f", contando a que a Forma {f['forma']} já traz" if emb else "") + ": o limite é 2")
    bruto, devs = (c if emb else 0), []
    for x in f["res"]:
        if not x:
            devs.append("")
            continue
        d = preco(RESTR[x]["devolve"], c)
        bruto += d
        devs.append(f"+{d}")
    dv = min(2 * c, bruto)
    if bruto > 2 * c:
        avisos.append(f"A devolução parou no teto de {2 * c}")
    usa = min(dv, gasto)
    perde = dv - usa
    if perde:
        avisos.append(f"Devolução perdida: {perde} ponto{'s' if perde > 1 else ''} sem peça para pagar")
    s = 3 * c - gasto + usa
    if s < 0:
        erros.append(f"Orçamento estourado: faltam {-s} ponto{'s' if s < -1 else ''}")
    dados = max(0, s) + (c if lib else 0)
    bases = [x["nome"] for x in res]
    if sum(1 for b in bases if b in FREQUENCIA) > 1:
        erros.append(f"{bases[0]} e {bases[1]} são as duas de frequência")
    presentes = mel + bases
    for a, b in PARES:
        if a in presentes and b in presentes:
            erros.append(f"{a} não entra com {b}")
    if "Corpo a Corpo" in bases and not emb and f["forma"] in ("Cone", "Linha"):
        erros.append(f"Corpo a Corpo não entra em {f['forma']}")
    if "Corpo a Corpo" in bases and emb:
        erros.append(f"A Forma {f['forma']} já traz o Corpo a Corpo")
    if "Tudo ou Nada" in bases and f["forma"] not in POR_TR:
        erros.append("Tudo ou Nada só entra em feitiço de Teste de Resistência")
    if "Inescapável" in mel and (len(mel) > 1 or nr):
        erros.append("Inescapável não aceita outra peça")
    if lib:
        if c < 3:
            erros.append("Liberação Máxima é de Classe 3 ou mais")
        if f["forma"] in ("Cura", "Onda", "Apoio"):
            erros.append("Liberação Máxima não serve para cura")
        if "Inescapável" in mel or "Toca a Alma" in mel:
            erros.append("Esta peça não entra numa Liberação Máxima")
    # livro reconstruído: Salto, Queima e Estilhaço acrescentam metade, e o Remate conta como 25% a mais no teto
    depois = sum(dados // 2 for n in ("Salto", "Queima", "Estilhaço") if n in mel)
    remate = "Remate" in mel
    efetivo = dados * (1.25 if remate else 1) + depois
    if efetivo > 4 * c:
        t_ef = (str(int(efetivo)) if float(efetivo).is_integer() else str(efetivo).replace(".", ","))
        erros.append(f"{t_ef} dados somando repetições{' e o Remate' if remate else ''}: o teto da Classe {c} é {4 * c}")
    controle = any(PECAS[x]["familia"] == "Controle" for x in mel)
    if controle and dados == 0:
        avisos.append("Controle sem dano: uma rodada a mais e CD +2")
    elif controle and dados <= c:
        avisos.append("Controle com saldo até a Classe: uma rodada a mais")
    pe = math.ceil(4.5 * c) if lib else 3 * c
    if lib:
        acao = "Rodada inteira"
    elif "Atrasar" in bases:
        acao = "Rodada +1 turno" if "Carregar" in bases else "Rodada inteira"
    else:
        acao = ("Bônus" if "Rápido" in mel else "Reação" if "Reação" in mel else "Padrão") + (" +1 turno" if "Carregar" in bases else "")
    resolve = ("Automático" if "Inescapável" in mel else "TR para metade" if "Certeiro" in mel else
               "Acerto" if f["forma"] in ("Projétil", "Toque") else "TR, metade" if f["forma"] in POR_TR else "Automático")
    conta_txt = (f"{3 * c} − {gasto} + {usa}" + (f" + {c}" if lib else "") + f" = {dados}d8 · teto {4 * c}" +
                 (f" · a Forma devolve {c}" if emb else "") + (f" · perde {perde}" if perde else ""))
    return {"dados": dados, "depois": depois, "gasto": gasto, "usa": usa, "perde": perde, "erros": erros, "avisos": avisos, "pe": pe,
            "acao": acao, "resolve": resolve, "dano": texto_do_dano(f["forma"], dados, depois), "alcance": alcance(f, c),
            "conta": conta_txt, "precos": precos, "devs": devs, "curto": texto_do_dano(f["forma"], dados, curto=True)}


def carta(f, fam, nivel, lib=False, vaga=1):
    """o que a carta mostra, caixa por caixa"""
    if not f["nome"]:
        pecas = sum(1 for x in f["mel"] + f["res"] if x)
        return {k: "" for k in ("dano", "pe", "resolve", "acao", "alcance", "conta", "ampliar", "avisos", "p1", "p2", "p3", "p4", "d1", "d2")} | \
               {"estado": "Dê um nome" if pecas else ""}
    c, maxc = f["classe"], maior_classe(nivel)
    x = monta(f, c, fam, nivel, lib, vaga)
    ne, na = len(x["erros"]), len(x["avisos"])
    amp = []
    for k in range(c + 1, maxc + 1):
        y = monta(f, k, fam, nivel, lib, vaga)
        amp.append(f"{k} → {y['curto']}, {y['pe']} PE")
    return {"estado": (f"⚠ {ne} erro{'s' if ne > 1 else ''}" if ne else f"! {na} aviso{'s' if na > 1 else ''}" if na else "Na regra"),
            "dano": x["dano"], "pe": f"{x['pe']} PE", "resolve": x["resolve"], "acao": x["acao"], "alcance": x["alcance"], "conta": x["conta"],
            "ampliar": " · ".join(amp) if amp else "Já está na maior Classe que o nível liberou",
            "avisos": " · ".join(x["erros"] + x["avisos"]) or "Dentro das regras que a ficha confere",
            "p1": x["precos"][0], "p2": x["precos"][1], "p3": x["precos"][2], "p4": x["precos"][3], "d1": x["devs"][0], "d2": x["devs"][1],
            "_dados": x["dados"], "_pe": x["pe"], "_erros": ne}


# ---------------------------------------------------------------------------------------------
# A planilha: preencher, recalcular e ler
# ---------------------------------------------------------------------------------------------
PASTA = tempfile.mkdtemp(prefix="amaldicoada-")
FILA = []
WB0 = load_workbook(ARQ)


def indice_da_ficha(wb):
    dd, out = wb["DADOS"], {}
    for r in range(5, 200):
        k, v = dd.cell(row=r, column=53).value, ix.endereco(dd.cell(row=r, column=54).value)
        if k and v:
            out[k] = v
    return out


IDX = indice_da_ficha(WB0)
# 05/10/2026: o campo TÉCNICA DECLARADA da CARTEIRA, a caixa logo abaixo do rótulo (que diz TÉCNICA AMALDIÇOADA, TÉCNICA
# MARCIAL ou ESTILO DECLARADO); a caixa NOME DA TÉCNICA desta aba espelha ele. Achado na planilha gerada, e não no gerador.
_rot_tec = [c for linha in WB0["CARTEIRA"].iter_rows() for c in linha if isinstance(c.value, str) and "DECLARAD" in c.value]
CAMPO_TEC = f"{_rot_tec[0].column_letter}{_rot_tec[0].row + 1}" if len(_rot_tec) == 1 else None
FEITICOS = [fa.celulas_do_feitico(*p) for p in G["feiticos"]]
LIBS = [fa.celulas_do_feitico(*p) for p in G["libs"]]
PASSIVAS = [fa.celulas_da_passiva(*p) for p in G["passivas"]]
APTIDOES = [fa.celulas_da_aptidao(*p) for p in G["aptidoes"]]
PACTOS = [fa.celulas_do_pacto(r) for r in G["pactos"]]
FAMILIAS = list(CAT["familias"])
CEL_FAM = {f: f"{G['cols_fam'][i][0]}{G['familias'] + 1}" for i, f in enumerate(FAMILIAS)}
VAZIO = {"nome": "", "classe": 1, "forma": "Projétil", "mel": ["", "", "", ""], "res": ["", ""]}


def feitico(nome="", classe=1, forma="Projétil", mel=(), res=()):
    return {"nome": nome, "classe": classe, "forma": forma, "mel": (list(mel) + [""] * 4)[:4], "res": (list(res) + [""] * 2)[:2]}


def prepara(nome, ficha):
    """uma copia da ficha gerada, preenchida com `ficha`, na fila do LibreOffice"""
    copia = os.path.join(PASTA, nome + ".xlsx")
    shutil.copy(ARQ, copia)
    wb = load_workbook(copia)
    f, a = wb["FICHA"], wb[ABA]
    f[IDX["nivel"]] = ficha.get("nivel", 2)
    f[IDX["refino escolhido"]], f[IDX["marco leque"]], f[IDX["marco corpo"]] = ficha.get("refino", 0), ficha.get("leque", 0), ficha.get("corpo", 0)
    f[IDX["atr_base_Essência"]] = ficha.get("essencia", 0)
    # 02/10/2026: a rota vem da Origem da FICHA, e a CD de cada grupo de arma lê os atributos de lá
    if ficha.get("origem"):
        f[IDX["origem"]] = ficha["origem"]
    for k in ("caminho", "trilha"):              # 02/10/2026: o título dos blocos das Habilidades lê os dois
        if ficha.get(k):
            f[IDX[k]] = ficha[k]
    for atr, v in ficha.get("atributos", {}).items():
        f[IDX[f"atr_base_{atr}"]] = v
    for fam, estado in ficha.get("familias", {}).items():
        a[CEL_FAM[fam]] = estado

    def poe(cel, ft):
        a[cel["nome"]], a[cel["classe"]], a[cel["forma"]] = ft["nome"] or None, ft["classe"], ft["forma"]
        for c, v in zip(cel["mel"], ft["mel"]):
            a[c] = v or None
        for c, v in zip(cel["res"], ft["res"]):
            a[c] = v or None
    for cel, ft in zip(FEITICOS, ficha.get("feiticos", [])):
        poe(cel, ft)
    for cel, ft in zip(LIBS, ficha.get("libs", [])):
        poe(cel, ft)
    for cel, v in ficha.get("celulas", {}).items():
        a[cel] = v
    if ficha.get("tecnica_declarada") and CAMPO_TEC:      # 05/10/2026: escrito na CARTEIRA, como o jogador faz
        wb["CARTEIRA"][CAMPO_TEC] = ficha["tecnica_declarada"]
    # o IFS e o TEXTJOIN ficam crus na ficha, porque ela vive no Sheets; o LibreOffice só os reconhece com o prefixo do Excel
    for ws in wb:
        for linha in ws.iter_rows():
            for c in linha:
                if isinstance(c.value, str) and c.value.startswith("="):
                    c.value = re.sub(r"(?<![A-Z_.])(IFS|TEXTJOIN)\(", r"_xlfn.\1(", c.value)
    wb.save(copia)
    FILA.append(copia)


def recalcula_tudo():
    saida = os.path.join(PASTA, "saida")
    subprocess.run(["libreoffice", "--headless", "--convert-to", "xlsx", "--outdir", saida] + FILA, capture_output=True, timeout=900)
    out = {}
    for copia in FILA:
        feito = os.path.join(saida, os.path.basename(copia))
        if not os.path.exists(feito):
            print("o LibreOffice nao converteu; sem ele esta checagem NAO roda"); sys.exit(1)
        out[os.path.basename(copia)[:-5]] = load_workbook(feito, data_only=True)
    shutil.rmtree(PASTA, ignore_errors=True)
    return out


def txt(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return "" if v is None else str(v)


def le_carta(ws, cel):
    return {"estado": txt(ws[cel["estado"]].value), "dano": txt(ws[cel["dano"]].value), "pe": txt(ws[cel["pe"]].value),
            "resolve": txt(ws[cel["resolve"]].value), "acao": txt(ws[cel["acao"]].value), "alcance": txt(ws[cel["alcance"]].value),
            "conta": txt(ws[cel["conta"]].value), "ampliar": txt(ws[cel["ampliar"]].value), "avisos": txt(ws[cel["avisos"]].value),
            **{f"p{i + 1}": txt(ws[c].value) for i, c in enumerate(cel["preco"])}, **{f"d{i + 1}": txt(ws[c].value) for i, c in enumerate(cel["dev"])}}


def difere(lida, esperada):
    return [f"{k}: a ficha diz {lida[k]!r}, a regra {v!r}" for k, v in esperada.items() if not k.startswith("_") and lida[k] != v]


def contas(wb):
    """as contas com nome da DADOS_AM"""
    d = wb[DAM]
    col = next(c for c in range(1, d.max_column + 1) if d.cell(row=1, column=c).value == "contas da amaldiçoada")
    return {d.cell(row=r, column=col).value: d.cell(row=r, column=col + 1).value for r in range(2, d.max_row + 1) if d.cell(row=r, column=col).value}


# ---------------------------------------------------------------------------------------------
# As fichas
# ---------------------------------------------------------------------------------------------
def do_livro(p):
    return feitico(p["nome"], p["classe"], p["forma"], [m for m in p["mel"]],
                   [r.split("|")[0] + (f" ({NOME_PESO[PESO[r.split('|')[1]]]})" if "|" in r else "") for r in p["res"]])


# 04/10/2026: o livro reconstruído não tem mais a tabela de feitiços prontos; a prova da conta passou a ser os exemplos
# de montagem que ele imprime (tecnica-do-livro.json, chave feiticos_prontos). Cada exemplo diz as Famílias Livres que
# usa, e elas são da ficha, não do feitiço: os exemplos vão para uma ficha por conjunto de Famílias Livres.
PRONTOS = TEC["feiticos_prontos"]
_GRUPOS = {}
for _p in PRONTOS:
    _GRUPOS.setdefault(tuple(sorted(_p.get("livres", []))), []).append(_p)
LIVROS = {}
for _k, (_livres, _ps) in enumerate(sorted(_GRUPOS.items())):
    LIVROS["livro" if _k == 0 else f"livro_{_k + 1}"] = (_ps, {"nivel": 30, "leque": 7, "essencia": 6, "familias": {f: "Livre" for f in _livres},
        "feiticos": [do_livro(p) for p in _ps if not p["lib"]], "libs": [do_livro(p) for p in _ps if p["lib"]]})
LIVRO = LIVROS["livro"][1]


def sorteada(semente, nivel, cheia=True):
    rnd = random.Random(semente)
    fams = FAMILIAS[:]
    rnd.shuffle(fams)
    familias = {fams[0]: "Livre", fams[1]: "Livre", fams[2]: "Fechada", fams[3]: "Fechada", fams[4]: "Fechada"}
    pecas, restr = list(PECAS), list(RESTR)
    # as peças que mexem na conta e nas mensagens aparecem mais vezes que as outras
    quentes = ["Longe", "Longe", "Muito Longe", "Maior", "Muito Maior", "Mais Um", "Rajada", "Salto", "Queima", "Rápido", "Reação",
               "Certeiro", "Inescapável", "Toca a Alma", "Derrubado", "Cego", "Prende"]

    def um(lib):
        n_mel = rnd.choice([0, 0, 1, 1, 2, 2, 3, 4])
        mel = [rnd.choice(quentes if rnd.random() < 0.45 else pecas) for _ in range(n_mel)]
        rnd.shuffle(mel)
        mel = (mel + [""] * 4)[:4]
        rnd.shuffle(mel)                                         # a Melhoria pode estar em qualquer das quatro linhas
        res = [rnd.choice(restr) if rnd.random() < 0.55 else "" for _ in range(2)]
        return feitico("" if rnd.random() < 0.08 else f"Sorteado {rnd.randrange(999)}", rnd.randint(1, 7) if not lib else rnd.randint(1, 7),
                       rnd.choice(list(FORMAS)), mel, res)
    n = fa.N_FEITICOS if cheia else 9
    return {"nivel": nivel, "familias": familias, "leque": rnd.randint(0, 2), "refino": rnd.randint(0, 2), "essencia": rnd.randint(0, 6),
            "feiticos": [um(False) for _ in range(n)], "libs": [um(True) for _ in range(fa.N_LIB)]}


# a ficha da Kaori do estudo, com o que o resto da aba mostra: Passivas, aptidões, Domínio, Técnica Máxima, pactos
def _outras(nivel, refino, leque, essencia, dominio, cp_regra, passivas, aptidoes, pactos, zero, tm, indice=None):
    cel = {G["degrau"]: dominio, G["cp_regra"]: cp_regra, G["classe_do_indice"]: indice}
    for c, p in zip(PASSIVAS, passivas):
        cel[c["nome"]] = p
    for c, a in zip(APTIDOES, aptidoes):
        cel[c["nome"]] = a
    for c, (forma, concede) in zip(PACTOS, pactos):
        cel[c["forma"]], cel[c["concede"]] = forma, concede
    cz = G["cols_zero"]
    for i, (forma, mel, res) in enumerate(zero):
        lin = G["zero_ini"] + i
        cel[f"{cz['forma'][0]}{lin}"], cel[f"{cz['mel'][0]}{lin}"], cel[f"{cz['res'][0]}{lin}"] = forma, mel, res
    cel[G["tm_forma"]] = tm[0]
    for (c1, _), m in zip(G["cols_tm_mel"], tm[1]):
        cel[f"{c1}{G['tm_mel']}"] = m
    return {"nivel": nivel, "refino": refino, "leque": leque, "essencia": essencia, "celulas": {k: v for k, v in cel.items()}}


KAORI = {**_outras(10, 2, 0, 1, "Incompleta", 2, ["Raiz", "Fluxo", None, None, None, "Leitura"], ["Projetar Energia", "Barreira Simples", "Energia Reversa"],
                   [("Temporário", None), ("Permanente", "Um espaço conhecido"), (None, None)],
                   [("Toque", None, None), ("Projétil", "Empurrão", None), ("Cone", "Maior", "Parado"), ("Apoio", "Longe", None), ("Explosão", "Longe", None)],
                   ("Projétil", ["Fura"])),
         "familias": {"Controle": "Livre", "Castigo": "Livre", "Amparo": "Fechada", "Área": "Fechada", "Auxiliares": "Fechada"},
         "feiticos": [feitico("Estalo"), feitico("Perfurar", 1, "Projétil", ["Precisão"], ["Parado"]), feitico("Golpe Cru", 1, "Toque"),
                      feitico("Lança Negra", 2, "Projétil", ["Fura"], ["Atrasar"]),
                      feitico("Marca do Carrasco", 3, "Projétil", ["Marca", "Queima"], ["Uma Vez"]),
                      feitico("Palma Trovejante", 2, "Cone", ["Derrubado"], ["Atrasar"])],
         "libs": [feitico("Golpe do Voto", 3)]}
VELHO = {**_outras(30, 7, 0, 6, "Sem Barreiras", 3, ["Escama", "Afinidade", "Reserva Profunda", "Talento Próprio (CE 3)", "Eco"],
                   ["Domínio Simples", "Pétala", "Aptidão Própria (CE 2)", "Cortina"] * 3,
                   [("Permanente", "Um espaço conhecido"), ("Permanente", "Um espaço conhecido"), ("Permanente", "Uma aptidão")],
                   [("Linha", "Longe", "Gesto"), ("Aura", "Maior", None), ("Efeito", None, None), ("Projétil", "Longe", None), ("Cone", None, None)],
                   ("Linha", ["Muito Longe"]), 3),
         "feiticos": [feitico(f"F{i}", 7) for i in range(20)],
         "libs": [feitico("L1", 7), feitico("L2", 5), feitico("L3", 3)]}
MEIO = {**_outras(17, 1, 3, 3, "Completa", 1, ["Leitura", "Recomposição", "Costura", None, None, "Leitura de Feitiços", "Instinto", "Raiz", "Fluxo"],
                  ["Kokusen Constante"], [("Promessa", None), (None, None), ("Pacto de restrição", None)],
                  [("Projétil", None, None)] * 5, ("Onda", ["Limpa", "Junto", "Rápido"]), 5),
        "familias": {"Amparo": "Livre", "Tempo": "Fechada"},
        "feiticos": [feitico(f"F{i}", 5, "Cura", ["Junto"]) for i in range(12)], "libs": []}
NOVA = {"nivel": 2}
# Um feitiço para cada regra que o sorteio quase nunca monta. O arnês mostrou o buraco: tirar da ficha o teto da devolução na conta
# do Ampliar, o aviso das duas Restrições de frequência ou os pares proibidos passava calado, porque nenhuma carta sorteada caía ali.
BORDAS = {"nivel": 30, "feiticos": [
    # a Forma já devolve, as duas Restrições devolvem Média e o gasto passa de 2 × Classe: o teto da devolução muda os dados em toda Classe
    feitico("Teto da devolução", 3, "Toque", ["Sem Ver", "Corrói"], ["Atrasar", "Sangra"]),
    feitico("Duas de frequência", 4, "Projétil", ["Fura"], ["Uma Vez", "Aquecer"]),
    feitico("Frequência com nível", 5, "Explosão", ["Maior"], ["Condicional (Média)", "Dívida"]),
    feitico("Par na Melhoria", 6, "Projétil", ["Rápido", "Reação"]),
    feitico("Rápido que atrasa", 6, "Projétil", ["Rápido"], ["Atrasar"]),
    feitico("Reação que atrasa", 6, "Projétil", ["Reação"], ["Atrasar"]),
    feitico("Reação parada", 6, "Projétil", ["Reação"], ["Parado"]),
    feitico("Corpo no Cone", 3, "Cone", [], ["Corpo a Corpo"]),
    feitico("Corpo na Linha", 3, "Linha", ["Longe"], ["Corpo a Corpo"]),
    feitico("Corpo repetido", 3, "Aura", [], ["Corpo a Corpo"]),
    feitico("Tudo ou Nada no tiro", 2, "Projétil", ["Precisão"], ["Tudo ou Nada"]),
    feitico("Tudo ou Nada no TR", 2, "Explosão", [], ["Tudo ou Nada"]),
    feitico("Inescapável com peça", 5, "Projétil", ["Inescapável", "Longe"]),
    feitico("Inescapável com Restrição", 5, "Projétil", ["Inescapável"], ["Gesto"]),
    feitico("Carga lenta", 4, "Linha", ["Maior"], ["Atrasar", "Carregar"]),
    feitico("Reação carregada", 6, "Projétil", ["Reação"], ["Carregar"]),
    feitico("Salto demais", 4, "Projétil", ["Salto"], ["Atrasar"])],
    "libs": [feitico("Liberação baixa", 2), feitico("Liberação de cura", 4, "Cura"), feitico("Liberação na alma", 5, "Projétil", ["Toca a Alma"])]}

# As rotas que não são o Fundamento (02/10/2026): uma ficha por rota, com o que só ela tem preenchido. O Corpo
# Amaldiçoado leva três grupos que misturam atributo (a Lâmina Longa acerta com os dois) e um degrau de Domínio, que fora
# do Fundamento não pode gastar espaço; a Restrição Celestial sem energia, uma ferramenta que só se carrega e o Estímulo;
# a segunda Restrição, os três grupos da Fisga do livro, todos de Força.
GM = G["grupos_menu"]
ROTA_SEM = {"nivel": 10, "origem": "Feto · Sem Técnica",
            "celulas": {G["rota_menu"]: "Energia Reversa", PASSIVAS[0]["nome"]: "Contragolpe"}}
ROTA_CORPO = {"nivel": 12, "origem": "Corpo Amaldiçoado", "atributos": {"Força": 2, "Destreza": 3},
              "celulas": {G["rota_menu"]: "Três grupos de arma", GM[0]: "Lâmina Longa", GM[1]: "Arremesso", GM[2]: "Massa",
                          G["degrau"]: "Incompleta"}}
ROTA_CELESTE = {"nivel": 8, "origem": "Restrição Celestial · sem energia",
                "celulas": {G["rota_menu"]: "Ferramenta de carregar", G["estimulo_pericia"]: "Atletismo", G["estimulo_teste"]: "Físico"}}
ROTA_FISGA = {"nivel": 5, "origem": "Restrição Celestial · sem energia", "atributos": {"Força": 3},
              "celulas": {G["rota_menu"]: "Três grupos de arma", GM[0]: "Armas Longas", GM[1]: "Ceifa", GM[2]: "Flexível"}}

# O menu rápido da FICHA (02/10/2026): a Kaori com o que só o jogador escreve (o "Como é" de feitiço, da Técnica Máxima e
# do Domínio, o texto da Passiva Livre, da Regra Própria, de uma Passiva e de uma aptidão), e um feitiço sem nome no meio,
# que tem de sumir do menu com o de baixo subindo.
MENU_F = {**KAORI, "caminho": "Bastião", "trilha": "Muro", "celulas": {**KAORI["celulas"],
                               FEITICOS[0]["como"]: "Um estalo de dedos que racha o ar.", FEITICOS[3]["como"]: "A lança sai da sombra dela.",
                               G["tm_nome"]: "Sentença Negra", f"D{G['tm_como'] + 1}": "O céu escurece em volta do alvo.",
                               G["dom_nome"]: "Jardim de Agulhas", f"D{G['dom_como'] + 1}": "Um campo de agulhas pretas.",
                               f"L{G['descricao'] + 4}": "Ela sente a energia de quem mente.",
                               f"D{G['regra_propria'] + 1}": "Quem pisa na sombra dela não corre.",
                               PASSIVAS[1]["texto"]: "O Fluxo dela é um rio que não para.", APTIDOES[1]["texto"]: "Barreira em forma de guarda-chuva."},
          "feiticos": [feitico("Estalo"), feitico("", 2, "Cone"), feitico("Perfurar", 1, "Projétil", ["Precisão"], ["Parado"]),
                       feitico("Lança Negra", 2, "Projétil", ["Fura"], ["Atrasar"]), feitico(""), feitico("Golpe Cru", 1, "Toque")]}

FICHAS = {**{k: v[1] for k, v in LIVROS.items()}, "kaori": KAORI, "velho": VELHO, "meio": MEIO, "nova": NOVA, "bordas": BORDAS, "menu": MENU_F,
          "rota-sem": ROTA_SEM, "rota-corpo": ROTA_CORPO, "rota-celeste": ROTA_CELESTE, "rota-fisga": ROTA_FISGA,
          "sorteio-2": sorteada(11, 2, False), "sorteio-7": sorteada(12, 7), "sorteio-13": sorteada(13, 13),
          "sorteio-21": sorteada(14, 21), "sorteio-30": sorteada(15, 30)}
FICHAS["kaori"] = {**FICHAS["kaori"], "tecnica_declarada": "Peso Emprestado"}
# o arnes-amaldicoada.py roda esta regressão dezenas de vezes, e pede só algumas fichas para cada rodada ser curta
SO = [x for x in os.environ.get("AMALDICOADA_SO", "").split(",") if x]
if SO:
    FICHAS = {k: v for k, v in FICHAS.items() if k in SO or k in LIVROS}
    print(f"(rodada curta, só com as fichas {', '.join(FICHAS)})")
for _nome, _f in FICHAS.items():
    prepara(_nome, _f)
print(f"recalculando {len(FILA)} fichas no LibreOffice...")
WB = recalcula_tudo()

# ---------------------------------------------------------------------------------------------
print("\nO QUE A ABA LÊ DO LIVRO")
_r = subprocess.run([sys.executable, "ficha-v01/extrair_tecnica.py", "--confere"], capture_output=True, text=True)
if "nao esta nesta maquina" in _r.stdout:
    print("  [--] o livro não está nesta máquina: o tecnica-do-livro.json não foi comparado com ele")
else:
    checa("o tecnica-do-livro.json é o que o extrair_tecnica.py lê do livro hoje (" + TEC["_meta"]["versao_do_livro"] + ")", _r.returncode == 0,
          (_r.stdout + _r.stderr).strip()[-200:])
checa("os preços da aba são os da tabela Números da montagem do livro, nas sete Classes",
      all([preco(1, l["classe"]), preco(2, l["classe"]), preco(3, l["classe"]), 2 * l["classe"], 4 * l["classe"], 3 * l["classe"]] ==
          [l["leve"], l["media"], l["pesada"], l["devolucao"], l["teto"], l["pontos"]] for l in TEC["numeros_da_montagem"]))

print(f"\nOS {len(PRONTOS)} EXEMPLOS DE MONTAGEM DO LIVRO")
checa("as bases de alcance da regra daqui são as da tabela Base por Classe do livro", _bases_do_livro())
ruins, erros, cartas_ruins, _lidas = [], [], [], {}
for _nome_l, (_ps, _ficha_l) in LIVROS.items():
  ws = WB[_nome_l][ABA]
  nl = [p for p in _ps if not p["lib"]]
  ll = [p for p in _ps if p["lib"]]
  for p, cel, lib, vaga in [(p, FEITICOS[i], False, i + 1) for i, p in enumerate(nl)] + [(p, LIBS[i], True, i + 1) for i, p in enumerate(ll)]:
    esp = carta(do_livro(p), _ficha_l["familias"], 30, lib, vaga)
    lida = le_carta(ws, cel)
    _lidas[p["nome"]] = lida
    if p["dados"] is not None and esp["_dados"] != p["dados"]:
        ruins.append(f"{p['nome']}: a regra daqui dá {esp['_dados']}, o livro {p['dados']}")
    m = re.match(r"(?:Cura )?(\d+)d8", lida["dano"])
    na_ficha = int(m.group(1)) if m else int(lida["dano"].split(" ")[0]) // 3 if "vida temp" in lida["dano"] else 0
    if p["dados"] is not None and na_ficha != p["dados"]:
        ruins.append(f"{p['nome']}: a ficha dá {lida['dano']!r}, o livro {p['dados']} dados")
    if "pe" in p and lida["pe"] != f"{p['pe']} PE":
        ruins.append(f"{p['nome']}: a ficha cobra {lida['pe']!r}, o livro {p['pe']} PE")
    if lida["estado"].startswith("⚠"):
        erros.append(f"{p['nome']}: {lida['avisos']}")
    cartas_ruins += [f"{p['nome']} · {d}" for d in difere(lida, esp)]
checa(f"os {len(PRONTOS)} saem com os dados que o livro imprime, e com o PE dele", not ruins, "; ".join(ruins[:4]))
checa("nenhum exemplo do livro é acusado de erro pela ficha", not erros, "; ".join(erros[:3]))
checa(f"toda caixa das {len(PRONTOS)} cartas bate com a regra (dano, PE, ação, alcance, preços, conta, Ampliar e avisos)", not cartas_ruins,
      f"{len(cartas_ruins)}: " + "; ".join(cartas_ruins[:3]))
# o livro: "Uma Aura de Classe 3, sem desconto, tem Fura: custo 2 + 3, com devolução 3 de Corpo a Corpo" -- a Restrição
# embutida paga a Forma também, e a conta da carta mostra a devolução dela
checa("a Aura com Fura recebe a devolução 3 do Corpo a Corpo da Forma, e a carta mostra",
      "a Forma devolve 3" in _lidas["Aura com Fura"]["conta"] and _lidas["Aura com Fura"]["dano"].startswith("7d8"), str(_lidas["Aura com Fura"]))

# ---------------------------------------------------------------------------------------------
print("\nAS CARTAS DE FEITIÇO, FICHA POR FICHA")
total = com_erro = com_aviso = sem_nome = 0
mensagens = set()
for nome, ficha in FICHAS.items():
    ws = WB[nome][ABA]
    fam, nivel = ficha.get("familias", {}), ficha.get("nivel", 2)
    ruins = []
    lista = [(ft, FEITICOS[i], False, i + 1) for i, ft in enumerate((ficha.get("feiticos", []) + [VAZIO] * fa.N_FEITICOS)[:fa.N_FEITICOS])] + \
            [({**VAZIO, "classe": 3} if i >= len(ficha.get("libs", [])) else ficha["libs"][i], LIBS[i], True, i + 1) for i in range(fa.N_LIB)]
    for ft, cel, lib, vaga in lista:
        esp = carta(ft, fam, nivel, lib, vaga)
        lida = le_carta(ws, cel)
        ruins += [f"{'Liberação' if lib else 'feitiço'} {vaga} ({ft['nome'] or 'sem nome'}) · {d}" for d in difere(lida, esp)]
        total += 1
        com_erro += esp["estado"].startswith("⚠")
        com_aviso += esp["estado"].startswith("!")
        sem_nome += not ft["nome"]
        if ft["nome"]:
            x = monta(ft, ft["classe"], fam, nivel, lib, vaga)
            mensagens |= {re.sub(r"\d+", "N", m).split(":")[0][:28] for m in x["erros"] + x["avisos"]}
    checa(f"{nome} (nível {nivel}): as {len(lista)} cartas batem com a regra, caixa por caixa", not ruins, f"{len(ruins)}: " + "; ".join(ruins[:3]))
# toda caixa abre em maiúscula: o que a ficha calcula e o que nasce escrito, em todas as fichas preenchidas
minusculas = set()
for nome in FICHAS:
    for linha in WB[nome][ABA].iter_rows(min_row=G["saltos"]):
        for c in linha:
            t = c.value
            if isinstance(t, str):
                for marca in ("⚠ ", "! ", "← "):
                    if t.startswith(marca):
                        t = t[len(marca):]
                if t[:1].isalpha() and t[:1].islower() and not re.match(r"d\d", t):       # "d20 + 4" é dado, não palavra
                    minusculas.add(f"{c.coordinate}: {c.value[:40]}")
checa("nenhuma caixa da aba abre em letra minúscula, em nenhuma das fichas", not minusculas, f"{len(minusculas)}: " + "; ".join(sorted(minusculas)[:6]))
if not SO:
    checa(f"o sorteio cobriu o certo e o errado: {total} cartas, {com_erro} com erro, {com_aviso} só com aviso, {sem_nome} sem nome, "
          f"{len(mensagens)} mensagens diferentes", com_erro > 40 and com_aviso > 10 and sem_nome > 5 and len(mensagens) >= 25, str(sorted(mensagens)))

# ---------------------------------------------------------------------------------------------
print("\nO ORÇAMENTO, O ÍNDICE E A TÉCNICA")
CP_PASSIVA = {p["nome"]: int(p["classe_passiva"]) for p in TEC["passivas"] if p["classe_passiva"].isdigit()}
CP_PASSIVA.update({f"Talento Próprio (CE {k})": k for k in (1, 2, 3)})
ESPACOS_DO_DOMINIO = {d["degrau"]: d["espacos"] for d in TEC["dominio"]["degraus"]}
NIVEL_DA_CP = {int(l["classe_passiva"]): l["nivel"] for l in TEC["classe_passiva"] if l["classe_passiva"].isdigit()}


def refino_e_aptidoes(nivel, escolhas):
    """o refino e as aptidões que os marcos compram, contando as escolhas de Refino como as últimas"""
    n, r, apt = marcos(nivel), 1, 0
    k = min(escolhas, n)
    for i in range(n):
        r = min(10, r + 1)
        if i >= n - k:
            if r >= 10:
                apt += 2
            else:
                r, apt = r + 1, apt + 1
    return r, apt


for nome in [x for x in ("kaori", "velho", "meio", "nova") if x in FICHAS]:
    ficha, wb = FICHAS[nome], WB[nome]
    ws, f, cel, n = wb[ABA], wb["FICHA"], FICHAS[nome].get("celulas", {}), FICHAS[nome].get("nivel", 2)
    v = lambda c: txt(ws[c].value)
    passivas = [cel.get(c["nome"]) for c in PASSIVAS]
    pactos = [(cel.get(c["forma"]), cel.get(c["concede"])) for c in PACTOS]
    de_pacto = sum(1 for p in pactos if p == ("Permanente", "Um espaço conhecido"))
    espacos = 2 + n // 2 + marcos(n) + de_pacto
    leque = min(ficha.get("leque", 0), marcos(n))
    montados = sum(1 for ft in ficha.get("feiticos", []) if ft["nome"])
    cp_regra = cel.get(G["cp_regra"]) or 0
    em_passivas = sum(CP_PASSIVA[p] for p in passivas[:fa.PAGAS] if p) + max(0, cp_regra - 1)
    no_dominio = ESPACOS_DO_DOMINIO.get(cel.get(G["degrau"]), 0)
    livres = espacos + leque - montados - em_passivas - no_dominio
    sem = "⚠ " if em_passivas + no_dominio > espacos else ""
    esperado = {"maior_classe": str(maior_classe(n)), "espacos": str(espacos), "leque": f"+{leque}", "em_feiticos": str(montados),
                "em_passivas": f"{sem}{em_passivas}", "no_dominio": f"{sem}{no_dominio}", "livres": ("⚠ " if livres < 0 else "") + str(livres)}
    t = G["orc_caixas"] + 1
    lido = {k: v(f"{c1}{t}") for k, (c1, _) in zip(esperado, G["cols_orc"])}
    checa(f"{nome}: o Orçamento (maior Classe, espaços, Leque, feitiços, Passivas, Domínio e livres)", lido == esperado, f"{lido} != {esperado}")
    ci = cel.get(G["classe_do_indice"]) or (1 if nome == "nova" else maior_classe(n))
    zq = TEC["classe_0"]["quantos"][conta(TEC["classe_0"]["niveis"], n) - 1]
    zd = TEC["classe_0"]["dados"][conta(TEC["classe_0"]["niveis"], n) - 1]
    esp_i = [str(3 * ci), str(preco(1, ci)), str(preco(2, ci)), str(preco(3, ci)), str(2 * ci), str(4 * ci), str(limite_de_melhorias(ci)),
             f"{zq} feitiços grátis · {zd}d8 cada"]
    lido_i = [v(f"{c1}{G['indice'] + 1}") for c1, _ in G["cols_indice"]]
    checa(f"{nome}: o índice de preços da Classe {ci}, e a Classe 0 do nível", lido_i == esp_i, f"{lido_i} != {esp_i}")
    checa(f"{nome}: a Conjuração, a CD e o atributo são os da FICHA",
          v(G["conjuracao"]) == txt(f[IDX["conjuração"]].value) and v(G["cd"]) == txt(f[IDX["cd de feitiço"]].value) and v(G["atributo"]) != "")
    esp_r = "—" if not cp_regra else f"⚠ Nível {NIVEL_DA_CP[cp_regra]}" if NIVEL_DA_CP[cp_regra] > n else str(cp_regra - 1) if cp_regra > 1 else "De graça"
    checa(f"{nome}: a Regra Própria custa a diferença para a Classe Passiva 1, e avisa antes do nível", v(G["espacos_regra"]) == esp_r,
          f"{v(G['espacos_regra'])!r} != {esp_r!r}")
    fam = ficha.get("familias", {})
    nlv, nfe = sum(1 for e in fam.values() if e == "Livre"), sum(1 for e in fam.values() if e == "Fechada")
    esp_f = ("⚠ " if (nlv, nfe) != (2, 3) else "") + f"{nlv} de 2 · {nfe} de 3"
    checa(f"{nome}: a conta de Famílias Livres e Fechadas", v(G["resumo_familias"]) == esp_f, f"{v(G['resumo_familias'])!r} != {esp_f!r}")

    # --- a Classe 0
    ruins = []
    cz = G["cols_zero"]
    for i in range(fa.N_ZERO):
        lin = G["zero_ini"] + i
        forma = cel.get(f"{cz['forma'][0]}{lin}") or "Projétil"
        mel, res = cel.get(f"{cz['mel'][0]}{lin}"), cel.get(f"{cz['res'][0]}{lin}")
        if i + 1 > zq:
            abre = next(nv for nv, q in zip(TEC["classe_0"]["niveis"], TEC["classe_0"]["quantos"]) if q >= i + 1)
            esp_z = (f"Nível {abre}", "")
        else:
            dz = zd - (1 if mel else 0)           # livro reconstruído: a Restrição Leve não devolve o dado
            esp_z = ("—" if forma in ("Apoio", "Efeito") else f"{dz}d8 = {math.floor(dz * 4.5)}", alcance({"forma": forma, "mel": [mel]}, 0))
        lido_z = (v(f"{cz['dano'][0]}{lin}"), v(f"{cz['alcance'][0]}{lin}"))
        if lido_z != esp_z:
            ruins.append(f"linha {i + 1} ({forma}, {mel}, {res}): {lido_z} != {esp_z}")
    checa(f"{nome}: a Classe 0, linha por linha: os dados, a Melhoria que tira um, a Restrição que o devolve, o alcance e o nível que abre",
          not ruins, "; ".join(ruins[:3]))

    # --- a Técnica Máxima
    faixa = next((x for x in TEC["tecnica_maxima"]["faixas"] if x["de"] <= n <= x["ate"]), None)
    forma_tm = cel.get(G["tm_forma"]) or "Projétil"
    mel_tm = [cel.get(f"{c1}{G['tm_mel']}") for c1, _ in G["cols_tm_mel"]]
    if faixa is None:
        esp_t = (f"Nível {TEC['tecnica_maxima']['faixas'][0]['de']}", "—", "—")
    else:
        mc = maior_classe(n)
        livre, fechada = (lambda k: fam.get(k) == "Livre"), (lambda k: fam.get(k) == "Fechada")
        gasto = preco_da_peca(PESO[FORMAS[forma_tm]["custa"]], mc, livre(FORMAS[forma_tm]["familia"])) if FORMAS[forma_tm]["custa"] else 0
        fech = int(bool(FORMAS[forma_tm]["familia"]) and fechada(FORMAS[forma_tm]["familia"]))
        for m in [x for x in mel_tm if x]:
            gasto += preco_da_peca(PECAS[m]["peso"], mc, bool(PECAS[m]["familia"]) and livre(PECAS[m]["familia"]))
            fech += int(bool(PECAS[m]["familia"]) and fechada(PECAS[m]["familia"]))
        esp_t = (f"{faixa['dados']}d8 = {math.floor(faixa['dados'] * 4.5)}", str(TEC["tecnica_maxima"]["pe_por_classe"] * mc),
                 ("⚠ " if gasto > faixa["montagem"] or fech else "") + f"{gasto} de {faixa['montagem']}" + (" · Família Fechada" if fech else ""))
        if faixa["pe"] != TEC["tecnica_maxima"]["pe_por_classe"] * maior_classe(faixa["de"]):
            esp_t = ("a tabela do livro não bate com 5 × a maior Classe",)
    lido_t = (v(G["tm_dano"]), v(G["tm_pe"]), v(G["tm_montagem"]))
    checa(f"{nome}: a Técnica Máxima (dano fixo da faixa, PE e montagem nos preços da maior Classe)", lido_t == esp_t, f"{lido_t} != {esp_t}")

    # --- o Domínio
    ref, apt_marcos = refino_e_aptidoes(n, ficha.get("refino", 0))
    checa(f"{nome}: o refino da ficha é o que os marcos e as escolhas de Refino dão ({ref})", v(G["dom_refino"]) == str(ref) and v(G["apt_refino"]) == str(ref),
          f"{v(G['dom_refino'])} e {v(G['apt_refino'])}")
    deg = cel.get(G["degrau"])
    dom = TEC["dominio"]
    meio, terco, mc, mst = max(1, ref // 2), max(1, ref // 3), maior_classe(n), maestria(n)
    dura = f"{meio} rodada{'s' if meio > 1 else ''}"
    nomes = [d["degrau"] for d in dom["degraus"]]
    esp_d = [[nomes[0] + (" · a sua" if deg == nomes[0] else ""), str(dom["pe_por_classe"] * mc), dura, metros(min(7.5, 1.5 * ref)), f"−{terco} PE", "Não fecha", "Rola"],
             [nomes[1] + (" · a sua" if deg in nomes[1:] else ""), str(dom["pe_por_classe"] * mc), dura, metros(1.5 * ref), f"−{meio} PE",
              f"{dom['vida_da_barreira'] * meio} de vida", "Acontece"],
             ["Sem barreira" + (" · a sua" if deg == nomes[2] else ""), str(dom["pe_por_classe_sem_barreira"] * mc), dura, dom["raio_sem_barreira"],
              f"−{2 * mst} PE", "Não tem", "Acontece"]]
    lido_d = [[v(f"{c1}{G['dom_tabela'] + 1 + j}") for c1, _ in G["cols_dom"]] for j in range(3)]
    checa(f"{nome}: as três linhas do Domínio (PE, duração, raio, desconto e barreira)", lido_d == esp_d,
          str([(a, b) for la, lb in zip(lido_d, esp_d) for a, b in zip(la, lb) if a != b][:4]))
    d_ = next((d for d in dom["degraus"] if d["degrau"] == deg), None)
    esp_q = ("—", "—") if d_ is None else (f"{d_['espacos']} espaços", ("" if n >= (d_["nivel"] or 0) and ref >= d_["refino"] else "⚠ ") + ini(d_["abre_em"]))
    ess = ficha.get("essencia", 0)
    checa(f"{nome}: o degrau do Domínio (quanto custa, e o requisito de nível e de refino) e a corrida",
          (v(G["dom_custa"]), v(G["dom_requisito"])) == esp_q and v(G["dom_corrida"]) == f"Cai na {max(1, ess // 2)}ª falha",
          f"{(v(G['dom_custa']), v(G['dom_requisito']), v(G['dom_corrida']))} != {esp_q}")

    # --- as Passivas e as aptidões
    ruins = []
    FAZ = {p["nome"]: p["faz"] for p in TEC["passivas"]}
    for i, (c, p) in enumerate(zip(PASSIVAS, passivas)):
        if not p:
            esp_p = ("", "", "")
        else:
            cp = CP_PASSIVA[p]
            esp_p = (f"⚠ Nível {NIVEL_DA_CP[cp]}" if NIVEL_DA_CP[cp] > n else f"CE {cp}",
                     f"{cp} esp." if i < fa.PAGAS else "⚠ Vaga" if i - fa.PAGAS + 1 > leque else "Grátis",
                     FAZ[p] if p in FAZ else FAZ["Talento Próprio"] + " Escreva a sua na caixa de baixo.")
        lido_p = (v(c["cp"]), v(c["custo"]), v(c["faz"]))
        if lido_p != esp_p:
            ruins.append(f"Passiva {i + 1} ({p}): {lido_p} != {esp_p}")
    checa(f"{nome}: as doze cartas de Passiva (a Classe Passiva, o custo, a vaga do Leque e o que ela faz)", not ruins, "; ".join(ruins[:3]))
    ruins = []
    APT = {a["nome"]: a for a in TEC["aptidoes"]}
    aptidoes = [cel.get(c["nome"]) for c in APTIDOES]
    for i, (c, a) in enumerate(zip(APTIDOES, aptidoes)):
        if not a:
            esp_a = ("", "", "", "")
        else:
            base = APT[a.split(" (CE")[0]]
            cp = a[-2] if "(CE" in a else base["classe_passiva"]
            esp_a = (f"CE {cp}" if cp.isdigit() else ini(cp), f"Requisito: {base['requisito']}", ini(base["escala"]),
                     base["faz"] + (" Escreva a sua na caixa de baixo." if "(CE" in a else ""))
        lido_a = (v(c["cp"]), v(c["requisito"]), v(c["escala"]), v(c["faz"]))
        if lido_a != esp_a:
            ruins.append(f"aptidão {i + 1} ({a}): {[x[:40] for x in lido_a]} != {[x[:40] for x in esp_a]}")
    checa(f"{nome}: as doze cartas de aptidão (a Classe Passiva, o requisito, o que o refino escala e a regra do livro)", not ruins, "; ".join(ruins[:3]))
    anot = sum(1 for a in aptidoes if a)
    d4 = 4 if ref >= 9 else 3 if ref >= 6 else 2 if ref >= 3 else 1
    esp_c = (("⚠ " if anot > apt_marcos else "") + f"{anot} de {apt_marcos}", f"Proteção {ref // 3 + 1}", f"+{d4}{'d6' if ref >= 10 else 'd4'} na arma",
             f"RD {math.floor(1.5 * ref)} por 2 PE")
    lido_c = (v(G["apt_compradas"]), v(f"{G['cols_apt'][2][0]}{G['apt_caixas'] + 1}"), v(f"{G['cols_apt'][3][0]}{G['apt_caixas'] + 1}"),
              v(f"{G['cols_apt'][4][0]}{G['apt_caixas'] + 1}"))
    checa(f"{nome}: as aptidões compradas contra as que os marcos dão, e as duas de graça pelo refino", lido_c == esp_c, f"{lido_c} != {esp_c}")
    perm = sum(1 for p in pactos if p[0] == "Permanente")
    esp_pc = ("⚠ " if perm > ess // 2 else "") + f"{perm} de {ess // 2}"
    checa(f"{nome}: os pactos permanentes contra metade da Essência", v(G["pac_permanentes"]) == esp_pc, f"{v(G['pac_permanentes'])!r} != {esp_pc!r}")

# ---------------------------------------------------------------------------------------------
print("\nAS QUATRO ROTAS")
# a regra das rotas, do arquivo do livro: a rota pela Origem, os nomes de cada uma, o que cada uma compra
ROT_L = TEC["rotas"]
NOMES_R = {1: {"feitico": "Feitiço", "liberacao": "Liberação Máxima", "tecnica_maxima": "Técnica Máxima"},
           2: ROT_L["nomes"]["Sem Técnica"], 3: ROT_L["nomes"]["Técnica Marcial"], 4: ROT_L["nomes"]["Técnica Marcial"]}
rota_de = lambda origem: 4 if origem == "Restrição Celestial · sem energia" else 3 if origem == "Corpo Amaldiçoado" else 2 if "Sem Técnica" in origem else 1
_propria = lambda nome, cps: [f"{nome} (CE {k})" for k in cps]
PAS_FUND = [p["nome"] for p in TEC["passivas"] if p["classe_passiva"].isdigit()] + _propria("Talento Próprio", (1, 2, 3))
PAS_MARC = [p["nome"] for p in ROT_L["passivas_marciais"] if p["classe_passiva"].isdigit()] + _propria("Talento Próprio", (1, 2, 3))
_cps = lambda txt: [int(x) for x in re.findall(r"\d", txt)]
APT_LIV = [a["nome"] for a in TEC["aptidoes"] if a["nome"] not in TEC["aptidoes_de_graca"] and a["nome"] != "Aptidão Própria"] + \
          _propria("Aptidão Própria", _cps(next(a["classe_passiva"] for a in TEC["aptidoes"] if a["nome"] == "Aptidão Própria")))
BEN_LIV = [b["nome"] for b in ROT_L["bencaos"] if b["nome"] not in ROT_L["bencaos_de_graca"] and b["nome"] != "Bênção Própria"] + \
          _propria("Bênção Própria", _cps(next(b["classe_passiva"] for b in ROT_L["bencaos"] if b["nome"] == "Bênção Própria")))
MENU_PAS = {1: set(PAS_FUND), 2: set(PAS_FUND) | set(PAS_MARC), 3: set(PAS_MARC), 4: set(PAS_MARC)}
MENU_APT = {1: set(APT_LIV), 2: set(APT_LIV), 3: set(APT_LIV) - {"Extensão de Domínio"}, 4: set(BEN_LIV)}
up = lambda t: t.upper()


def coluna_da(wb, cabecalho, n):
    """os n valores de baixo do cabeçalho da DADOS_AM (a linha 1), sem os vazios"""
    d = wb[DAM]
    col = next(c for c in range(1, d.max_column + 1) if d.cell(row=1, column=c).value == cabecalho)
    return [txt(d.cell(row=r, column=col).value) for r in range(2, 2 + n) if txt(d.cell(row=r, column=col).value)]


for nome in [x for x in ("kaori", "rota-sem", "rota-corpo", "rota-celeste", "rota-fisga") if x in FICHAS]:
    ficha, wb = FICHAS[nome], WB[nome]
    ws, f, cel = wb[ABA], wb["FICHA"], FICHAS[nome].get("celulas", {})
    v = lambda c: txt(ws[c].value)
    rota = rota_de(ficha.get("origem", txt(WB0["FICHA"][IDX["origem"]].value)))
    nm = NOMES_R[rota]
    # os nomes: os títulos, o Selo, a linha da rota
    esp_tit = {"feiticos": up(nm["feitico"] + "s"), "lib": up(nm["liberacao"]), "tm": up(nm["tecnica_maxima"]),
               "aptidoes": "BÊNÇÃOS E LAPIDAÇÃO" if rota == 4 else "APTIDÕES E REFINO",
               "dominio": "EXPANSÃO DE DOMÍNIO" + ("" if rota == 1 else " · ESTA ROTA NÃO TEM")}
    lido_tit = {k: v(f"D{G['sec'][k]}") for k in esp_tit}
    checa(f"{nome}: os títulos das seções têm os nomes da rota {rota}", lido_tit == esp_tit, f"{lido_tit} != {esp_tit}")
    t = G["rota_lin"]
    marcial = rota >= 3
    esp_rota = {"nome": ["Fundamento", "Sem Técnica", "Técnica Marcial com energia", "Técnica Marcial sem energia"][rota - 1],
                "selo": "SELO · TER O EQUIPAMENTO EM USO" if marcial else "SELO",
                "peça": ["—", "SEMENTE", "EQUIPAMENTO", "EQUIPAMENTO"][rota - 1]}
    lido_rota = {"nome": v(G["rota_nome"]), "selo": v(f"L{G['descricao']}"), "peça": v(f"J{t}")}
    checa(f"{nome}: a linha da rota diz a rota, a peça dela e o Selo da rota", lido_rota == esp_rota, f"{lido_rota} != {esp_rota}")
    menu_r = cel.get(G["rota_menu"], "")
    esp_extra = ("—" if rota == 1 else
                 ("Aberta, sem os gates de nível e de refino · conta como uma aptidão a mais" if menu_r else "") if rota == 2 else
                 "Fere maldição: o Corpo Amaldiçoado tem Canalizar Energia" if rota == 3 else
                 "" if not menu_r else "Não fere maldição: só as Katas ferem" if menu_r == fa.EQUIPAMENTO[2] else "Fere maldição")
    checa(f"{nome}: o que a semente dá, ou se o golpe simples fere maldição", v(G["rota_extra"]) == esp_extra, f"{v(G['rota_extra'])!r} != {esp_extra!r}")
    # os grupos de arma: o atributo de cada um (o maior na Lâmina Longa), a conjuração e a CD pela conta da FICHA
    arma = marcial and menu_r == fa.EQUIPAMENTO[0]
    atr = {a: int(txt(f[IDX[f"atr_{a}"]].value) or 0) for a in ("Força", "Destreza")}
    mae = int(txt(f[IDX["maestria"]].value))
    usados = []
    for i in range(3):
        g = cel.get(GM[i], "")
        if not (arma and g):
            usados.append(None)
            continue
        ats = ROT_L["grupos_de_arma"][g]
        usados.append("Destreza" if ats == ["Destreza"] or (len(ats) == 2 and atr["Destreza"] > atr["Força"]) else "Força")
    esp_g = [("" if a is None else f"{a} · d20 + {mae + atr[a]} · CD {8 + mae + atr[a]}") for a in usados]
    esp_glab = [f"GRUPO {i + 1}" if arma else "—" for i in range(3)]
    lido_g = [v(c) for c in G["grupos_conta"]]
    lido_glab = [v(f"{c}{t + 2}") for c in ("D", "J", "P")]
    checa(f"{nome}: cada grupo de arma com o atributo, a conjuração e a CD dele", lido_g == esp_g and lido_glab == esp_glab,
          f"{lido_g} {lido_glab} != {esp_g} {esp_glab}")
    distintos = [a for i, a in enumerate(usados) if a and a not in usados[:i]]
    if arma:
        esp_top = (("Escolha os grupos", "—", "—") if not distintos else
                   (f"{distintos[0]}, das armas", f"d20 + {mae + atr[distintos[0]]}", str(8 + mae + atr[distintos[0]])) if len(distintos) == 1 else
                   ("Por grupo", "Por grupo", "Por grupo"))
    else:
        esp_top = tuple(txt(f[IDX[k]].value) if k != "atributo" else txt(f["Z51"].value) for k in ("atributo", "conjuração", "cd de feitiço"))
    lido_top = (v(G["atributo"]), v(G["conjuracao"]), v(G["cd"]))
    checa(f"{nome}: a linha de cima da Técnica (atributo, conjuração e CD)", lido_top == esp_top, f"{lido_top} != {esp_top}")
    # o que cada rota compra: os menus de Passiva e de aptidão, e o menu da peça da rota
    lido_pas = set(coluna_da(wb, "menu de passiva", 100))
    checa(f"{nome}: o menu de Passiva traz as da rota", lido_pas == MENU_PAS[rota], f"sobra {lido_pas - MENU_PAS[rota]}, falta {MENU_PAS[rota] - lido_pas}")
    lido_apt = set(coluna_da(wb, "menu de aptidão", 100))
    checa(f"{nome}: o menu de aptidão traz {'as Bênçãos' if rota == 4 else 'as aptidões'} da rota", lido_apt == MENU_APT[rota],
          f"sobra {lido_apt - MENU_APT[rota]}, falta {MENU_APT[rota] - lido_apt}")
    esp_menu = [] if rota == 1 else [x[:1].upper() + x[1:] for x in ROT_L["sementes"]] if rota == 2 else list(fa.EQUIPAMENTO)
    checa(f"{nome}: o menu da peça da rota", coluna_da(wb, "menu da peça da rota", 10) == esp_menu, str(coluna_da(wb, "menu da peça da rota", 10)))
    esp_gm = set(ROT_L["grupos_de_arma"]) if arma else set()
    checa(f"{nome}: o menu de grupo de arma só existe na rota de arma", set(coluna_da(wb, "menu de grupo", 20)) == esp_gm)
    # o Domínio: fora do Fundamento ele não gasta espaço, e as contas mostram "—"
    deg = cel.get(G["degrau"], "")
    esp_dom = ESPACOS_DO_DOMINIO.get(deg, 0) if rota == 1 else 0
    checa(f"{nome}: o Domínio gasta {esp_dom} espaço(s) nesta rota", int(float(contas(wb)["espaços no domínio"])) == esp_dom)
    if rota != 1:
        checa(f"{nome}: o Domínio mostra que a rota não tem", v(G["dom_requisito"]) == "Só o Fundamento tem" and v(G["dom_custa"]) == "—"
              and v(G["dom_refino"]) == "—", f"{v(G['dom_requisito'])!r} {v(G['dom_custa'])!r} {v(G['dom_refino'])!r}")
    # as Bênçãos de graça e o Estímulo Muscular na Restrição Celestial sem energia
    cx = G["apt_caixas"]
    esp_cx = (["LAPIDAÇÃO", "DEFESA SEM ARMADURA", "ESTÍMULO MUSCULAR", "REAÇÃO DA DEFESA"] if rota == 4 else
              ["REFINO", "COBRIR-SE DE ENERGIA", "CANALIZAR ENERGIA", "REAÇÃO DE COBRIR-SE"])
    lido_cx = [v(f"{c}{cx}") for c in ("D", "J", "L", "P")]
    checa(f"{nome}: as caixas das {'Bênçãos' if rota == 4 else 'aptidões'} de graça", lido_cx == esp_cx, f"{lido_cx} != {esp_cx}")
    ref = int(float(contas(wb)["refino"]))
    esp_est = (["ESTÍMULO: PERÍCIA", "ESTÍMULO: TESTE DE RESISTÊNCIA", "ESTÍMULO: USOS"], f"{2 if ref >= 10 else 1}× por cena") if rota == 4 else (["—"] * 3, "—")
    lido_est = ([v(f"{c}{G['estimulo']}") for c in ("D", "J", "P")], v(G["estimulo_usos"]))
    checa(f"{nome}: a linha do Estímulo Muscular", lido_est == esp_est, f"{lido_est} != {esp_est}")

# ---------------------------------------------------------------------------------------------
print("\nO MENU RÁPIDO DA FICHA")
# 02/10/2026: a seção 8 da FICHA mostra o que está na FICHA AMALDIÇOADA, em cartas e sem buraco. A regra daqui: o feitiço e a
# carta sem nome somem, e o de baixo sobe; a carta de feitiço traz a Classe, o nome, o PE, a Forma, como resolve e o "Como é"
# que o jogador escreveu; a de Passiva e a de aptidão, o texto do jogador, ou o do livro quando ele não escreveu; os nomes
# são os da rota. Os endereços saem da ficha gerada: cada caixa do menu aponta para uma linha de uma tabela da DADOS_AM.
F0, D0 = WB0["FICHA"], WB0[DAM]
_cab_am = {ix._letras(c): D0.cell(row=1, column=c).value for c in range(1, D0.max_column + 1)}
R0_MENU = next(c.row for linha in F0.iter_rows() for c in linha if c.column == 4 and c.value in (8, "8"))
MENU = {}
for linha in F0.iter_rows(min_row=R0_MENU):
    for c in linha:
        m = re.fullmatch(r"=DADOS_AM!\$([A-Z]+)\$(\d+)", str(c.value or ""))
        if m:
            MENU.setdefault(_cab_am.get(m.group(1)), []).append((c.row, c.column, int(m.group(2)), c.coordinate))
for k in MENU:
    MENU[k].sort()
CAMPOS_F = ["menu: classe", "menu: nome", "menu: pe", "menu: forma", "menu: resolve", "menu: como"]
_ordem = lambda k: [x[2] for x in MENU.get(k, [])]
checa(f"as {fa.N_FEITICOS} cartas de feitiço do menu leem a lista da DADOS_AM na ordem de leitura (fileira a fileira, da esquerda para a direita)",
      all(_ordem(k) == list(range(2, 2 + fa.N_FEITICOS)) for k in CAMPOS_F), str({k: _ordem(k)[:5] for k in CAMPOS_F}))
_n_pas, _n_apt = 2 + fa.PAGAS + fa.DO_LEQUE, 2 + fa.N_APT
checa(f"as {_n_pas} cartas de Passiva e as {_n_apt} de aptidão também, com a Livre, a Regra Própria e as duas de graça primeiro",
      all(_ordem(k) == list(range(2, 2 + _n_pas)) for k in ("classe passiva no menu", "passiva no menu", "texto da passiva no menu"))
      and all(_ordem(k) == list(range(2, 2 + _n_apt)) for k in ("classe passiva da aptidão no menu", "aptidão no menu", "texto da aptidão no menu")))
ROTULO = {D0.cell(row=r, column=ix._col(c) - 1).value: coord for _, _, r, coord in MENU.get("texto do rótulo", [])
          for c in [re.match(r"[A-Z]+", F0[coord].value.split("$")[1]).group(0)]}
# o texto do livro na carta: inteiro quando cabe na caixa, a primeira frase quando não (a medida do estudo do menu:
# perto de 260 letras na caixa de 5 linhas da Passiva, 300 na de 6 da aptidão)
TETO = {"passiva": 260, "aptidao": 300}


def resumo_do_livro(t, teto):
    if len(t) <= teto:
        return t
    frases = re.split(r"(?<=\.) ", t)
    return frases[0] if len(frases[0]) >= 25 or len(frases) == 1 else frases[0] + " " + frases[1]


FAZ_P = {p["nome"]: p["faz"] for p in ROT_L["passivas_marciais"] + TEC["passivas"]}
FAZ_A = {a["nome"]: a["faz"] for a in TEC["aptidoes"] + ROT_L["bencaos"]}
base_ = lambda nome: re.sub(r" \(CE \d\)$", "", nome)
_longos = [(n, len(resumo_do_livro(t, TETO[k]))) for k, d in (("passiva", FAZ_P), ("aptidao", FAZ_A)) for n, t in d.items()
           if len(resumo_do_livro(t, TETO[k])) > TETO[k]]
checa("todo texto do livro que o menu mostra cabe na caixa: inteiro, ou a primeira frase", not _longos, str(_longos))
CP_TODAS = {**{p["nome"]: p["classe_passiva"] for p in TEC["passivas"] + ROT_L["passivas_marciais"]},
            **{f"Talento Próprio (CE {k})": str(k) for k in (1, 2, 3)}}
BEN = {b["nome"]: b for b in ROT_L["bencaos"]}
APT_TODAS = {a["nome"]: a for a in TEC["aptidoes"]}
for nome in FICHAS:
    ficha, wb = FICHAS[nome], WB[nome]
    ws, f, cel = wb[ABA], wb["FICHA"], ficha.get("celulas", {})
    v = lambda c: txt(ws[c].value)
    m_ = lambda k: [txt(f[x[3]].value) for x in MENU.get(k, [])]          # a coluna que nenhuma caixa lê vem vazia
    um_ = lambda k, i: txt(f[MENU[k][i][3]].value) if len(MENU.get(k, [])) > i else "(nenhuma caixa lê)"
    rota = rota_de(ficha.get("origem", txt(WB0["FICHA"][IDX["origem"]].value)))
    nm = NOMES_R[rota]
    # os feitiços: só os que têm nome, na ordem da aba, com o que a carta da aba mostra
    nomeados = [i for i, ft in enumerate(ficha.get("feiticos", [])) if ft["nome"]]
    pad = lambda xs, n: xs + [""] * (n - len(xs))
    carta_aba = [le_carta(ws, FEITICOS[i]) for i in nomeados]
    esp_f = {"menu: nome": pad([ficha["feiticos"][i]["nome"] for i in nomeados], fa.N_FEITICOS),
             "menu: classe": pad([str(ficha["feiticos"][i]["classe"]) for i in nomeados], fa.N_FEITICOS),
             "menu: pe": pad([c["pe"] for c in carta_aba], fa.N_FEITICOS),
             "menu: forma": pad([ficha["feiticos"][i]["forma"] for i in nomeados], fa.N_FEITICOS),
             "menu: resolve": pad([c["resolve"] for c in carta_aba], fa.N_FEITICOS),
             "menu: como": pad([cel.get(FEITICOS[i]["como"]) or "" for i in nomeados], fa.N_FEITICOS)}
    ruins = [f"{k}: {m_(k)[:6]} != {e[:6]}" for k, e in esp_f.items() if m_(k) != e]
    checa(f"{nome}: o menu traz os {len(nomeados)} {nm['feitico'].lower()}s com nome, sem buraco, com a Classe, o PE, a Forma, como resolve e o Como é",
          not ruins, "; ".join(ruins[:2]))
    # as Liberações, no lugar delas
    libs = ficha.get("libs", [])
    esp_l = [(libs[i]["nome"] if i < len(libs) else "") for i in range(fa.N_LIB)]
    checa(f"{nome}: as cartas de {nm['liberacao']} no menu", m_("menu da liberação: nome") == esp_l, f"{m_('menu da liberação: nome')} != {esp_l}")
    # a Técnica Máxima e o Domínio, em carta larga
    tm_n = cel.get(G["tm_nome"]) or ""
    tm_f = cel.get(G["tm_forma"]) or txt(WB0[ABA][G["tm_forma"]].value)          # a Forma nasce escolhida na aba
    pe_tm = v(G["tm_pe"])                                       # "—" antes do nível dela
    esp_tm = [tm_n, (pe_tm + " PE" if pe_tm.isdigit() else pe_tm) if tm_n else "", tm_f if tm_n else "", cel.get(f"D{G['tm_como'] + 1}") or ""]
    lido_tm = [um_(k, 0) for k in ("nome dela", "pe dela", "forma dela", "como é dela")]
    checa(f"{nome}: a carta da {nm['tecnica_maxima']} traz o nome, o PE, a Forma e o Como é dela", lido_tm == esp_tm, f"{lido_tm} != {esp_tm}")
    deg = cel.get(G["degrau"]) or ""
    esp_dom = ([cel.get(G["dom_nome"]) or "", deg, cel.get(f"D{G['dom_como'] + 1}") or ""] if rota == 1 else
               ["Esta rota não tem Expansão de Domínio", "", ""])
    lido_dom = [um_(k, 1) for k in ("nome dela", "forma dela", "como é dela")]
    checa(f"{nome}: a carta do Domínio" + (" diz que a rota não tem" if rota != 1 else " traz o nome, o degrau e o Como é"),
          lido_dom == esp_dom, f"{lido_dom} != {esp_dom}")
    # as Passivas: a Livre, a Regra Própria, e as doze cartas sem buraco, com o texto do jogador ou o do livro
    pas = [(i, cel.get(c["nome"])) for i, c in enumerate(PASSIVAS) if cel.get(c["nome"])]
    livro = lambda seu, faz: seu if seu else ("Do livro: " + faz if faz else "")
    esp_p = ["Expressão da técnica", "Regra Própria"] + [p for _, p in pas]
    esp_pt = [cel.get(f"L{G['descricao'] + 4}") or "", cel.get(f"D{G['regra_propria'] + 1}") or "Esta técnica não tem Regra Própria"] + \
             [livro(cel.get(PASSIVAS[i]["texto"]), resumo_do_livro(FAZ_P[base_(p)], TETO["passiva"])) for i, p in pas]
    esp_pc = [None, None] + ["CE " + CP_TODAS[p] for _, p in pas]
    lido_pc = m_("classe passiva no menu")
    ruins = [x for x in (m_("passiva no menu") != pad(esp_p, _n_pas) and f"{m_('passiva no menu')[:5]} != {esp_p[:5]}",
                         m_("texto da passiva no menu") != pad(esp_pt, _n_pas) and f"{[t[:30] for t in m_('texto da passiva no menu')[:4]]} != {[t[:30] for t in esp_pt[:4]]}",
                         lido_pc[2:] != pad(esp_pc[2:], _n_pas - 2) and f"{lido_pc[2:6]} != {esp_pc[2:6]}") if x]
    checa(f"{nome}: as Passivas no menu, sem buraco, com a Classe Passiva e o texto do jogador ou o do livro", not ruins, "; ".join(ruins))
    # as aptidões: as duas de graça da rota, com o texto do livro, e as compradas sem buraco
    gracas = ROT_L["bencaos_de_graca"] if rota == 4 else TEC["aptidoes_de_graca"]
    fonte = BEN if rota == 4 else APT_TODAS
    apt = [(i, cel.get(c["nome"])) for i, c in enumerate(APTIDOES) if cel.get(c["nome"])]
    esp_a = list(gracas) + [a for _, a in apt]
    # 06/10/2026 (pedido do Mizuki): as duas de graça abrem com o valor da conta, refeito aqui pelo refino da ficha
    ref_m = int(float(contas(wb)["refino"]))
    d4_m = 4 if ref_m >= 9 else 3 if ref_m >= 6 else 2 if ref_m >= 3 else 1
    reacao_m = "Reação da Defesa" if rota == 4 else "Reação de Cobrir-se"
    valor_m = [f"Proteção {ref_m // 3 + 1} · {reacao_m}: RD {math.floor(1.5 * ref_m)} por 2 PE. ",
               f"+{d4_m}{'d6' if ref_m >= 10 else 'd4'} na arma. "]
    esp_at = [valor_m[k] + "Do livro: " + resumo_do_livro(fonte[g]["faz"], TETO["aptidao"]) for k, g in enumerate(gracas)] + \
             [livro(cel.get(APTIDOES[i]["texto"]), resumo_do_livro(FAZ_A[base_(a)], TETO["aptidao"])) for i, a in apt]
    ruins = [x for x in (m_("aptidão no menu") != pad(esp_a, _n_apt) and f"{m_('aptidão no menu')[:5]} != {esp_a[:5]}",
                         m_("texto da aptidão no menu") != pad(esp_at, _n_apt) and f"{[t[:30] for t in m_('texto da aptidão no menu')[:4]]} != {[t[:30] for t in esp_at[:4]]}") if x]
    checa(f"{nome}: as {'Bênçãos' if rota == 4 else 'aptidões'} no menu, as duas de graça primeiro, com o valor e o texto do livro, e as compradas com o do jogador ou o do livro", not ruins, "; ".join(ruins))
    # os títulos, pela rota
    apt_nome = "BÊNÇÃOS" if rota == 4 else "APTIDÕES"
    esp_tit = {"título": f"MENU RÁPIDO · {up(nm['feitico'])}S, TALENTOS E {apt_nome}",
               "feitiços": f"{up(nm['feitico'])}S  ·  {len(nomeados)} de {fa.N_FEITICOS}",
               "máximas": f"{up(nm['liberacao'])}, {up(nm['tecnica_maxima'])}" + (" E DOMÍNIO" if rota == 1 else ""),
               "passivas": f"TALENTOS  ·  {len(pas)} de {fa.PAGAS + fa.DO_LEQUE}, mais a Expressão e a Regra Própria",
               "aptidões": f"{apt_nome}  ·  {len(apt)} de {fa.N_APT}, mais as duas de graça"}
    lido_tit = {k: txt(f[ROTULO[k]].value) if k in ROTULO else "(nenhuma caixa lê)" for k in esp_tit}
    checa(f"{nome}: os títulos do menu dizem os nomes da rota {rota} e quantos de cada", lido_tit == esp_tit, f"{lido_tit} != {esp_tit}")

# ---------------------------------------------------------------------------------------------
print("\nAS HABILIDADES DA FICHA (SEÇÃO 7)")
# 02/10/2026 (B34): a seção 7 da FICHA virou cartas, uma por degrau de Caminho e uma por entrega de Trilha, escritas pelo
# jogador. A regra daqui: os níveis são os da tabela "Entregas por nível" do capítulo 35 do livro; a etiqueta da carta diz
# "Nível L" quando o nível da ficha chegou nele, e "Abre no L" quando não; o título do bloco diz o Caminho e a Trilha da
# FICHA quando estão escolhidos. O riscado é regra de cor do Sheets, e o regressao-construir.js confere.
_cab_hab = {D0.cell(row=1, column=c).value: c for c in range(1, D0.max_column + 1)}
_c_niv = _cab_hab["nível da carta"]
_lin_hab = [r for r in range(2, 40) if D0.cell(row=r, column=_c_niv).value not in (None, "")]
NIV_HAB = [int(D0.cell(row=r, column=_c_niv).value) for r in _lin_hab]
FONTE_HAB = [str(D0.cell(row=r, column=_c_niv - 1).value).split(" ")[0] for r in _lin_hab]
# 04/10/2026: os níveis saem das duas frases da Progressão do livro reconstruído, no manual.txt
_MANP = " ".join(open("manual.txt", encoding="utf-8").read().split())
_e1 = re.search(r"Você recebe habilidades de Caminho nos níveis (\d+), (\d+) e (\d+) e de Trilha nos níveis (\d+) e (\d+)\.", _MANP)
_e2 = re.search(r"Receba habilidades de Caminho no (\d+) e no (\d+), e de Trilha no (\d+) e no (\d+)\.", _MANP)
_cam = [int(x) for x in _e1.groups()[:3] + _e2.groups()[:2]] if _e1 and _e2 else []
_tri = [int(x) for x in _e1.groups()[3:] + _e2.groups()[2:]] if _e1 and _e2 else []
checa(f"as cartas estão nos níveis de entrega da Progressão do livro (Caminho {_cam}, Trilha {_tri})",
      bool(_cam) and NIV_HAB == _cam + _tri and FONTE_HAB == ["Caminho"] * len(_cam) + ["Trilha"] * len(_tri), f"{FONTE_HAB} {NIV_HAB}")
R7 = next(c.row for linha in F0.iter_rows() for c in linha if c.column == 4 and c.value in (7, "7"))
ETIQ, TIT = [], []
for linha in F0.iter_rows(min_row=R7, max_row=R0_MENU - 1):
    for c in linha:
        m = re.fullmatch(r"=DADOS_AM!\$([A-Z]+)\$(\d+)", str(c.value or ""))
        if m and _cab_am.get(m.group(1)) == "etiqueta da carta":
            ETIQ.append((c.row, c.column, int(m.group(2)), c.coordinate))
        elif m and _cab_am.get(m.group(1)) == "texto do título":
            TIT.append((c.row, int(m.group(2)), c.coordinate))
ETIQ.sort(); TIT.sort()
checa("as 9 etiquetas leem as cartas na ordem do bloco (o Caminho e depois a Trilha), e os 2 títulos, o do Caminho e o da Trilha",
      [x[2] for x in ETIQ] == list(range(2, 11)) and [x[1] for x in TIT] == [2, 3], f"{[x[2] for x in ETIQ]} {[x[1] for x in TIT]}")
_vazias = [f"{x[3]}" for x in ETIQ if F0.cell(row=x[0], column=x[1] + 3).value not in (None, "")]
checa("o nome de cada carta nasce vazio: quem escreve é o script, quando o Caminho ou a Trilha mudam", not _vazias, str(_vazias[:3]))
# 05/10/2026, a opção B (o nome e o resumo do livro na carta, o texto inteiro na nota, o jogador pode escrever por cima):
# o habilidadesDaFicha_ do Codigo.gs acha cada carta pelo endereço que a DADOS_AM publica, e lê o livro do Habilidades.gs.
# O regressao-delta.js roda a conta do script no node; aqui, o que ela lê.
import habilidades as _hb, extrair_habilidades as _xh, ficha_automatica as _fau
_r = subprocess.run([sys.executable, "ficha-v01/extrair_habilidades.py", "--confere"], capture_output=True, text=True)
checa("o habilidades-do-livro.json é o que o extrair_habilidades.py tira do manual.txt hoje, e cada texto está no manual",
      _r.returncode == 0, (_r.stdout + _r.stderr).strip()[-200:])
_c_cn, _c_ct = _cab_hab.get("célula do nome"), _cab_hab.get("célula do texto")
_end = lambda v: ix.endereco(v) or ""
_mesc_f = {str(m).split(":")[0]: str(m) for m in F0.merged_cells.ranges}
_ruins_end, _CN = [], ix._letras(_hb.CN)
for k, (lin, col, linha_am, _co) in enumerate(ETIQ):
    nm, tx = (_end(D0.cell(row=linha_am, column=c).value) if c else "" for c in (_c_cn, _c_ct))
    nm_ok = col == _hb.C1 and nm == ix._letras(col + _hb.TAG) + str(lin) and _mesc_f.get(nm, "").endswith(_CN + str(lin))
    tx_ok = tx == ix._letras(col) + str(lin + 1) and _mesc_f.get(tx, "").endswith(_CN + str(lin + _hb.CAIXA))
    if not (nm_ok and tx_ok):
        _ruins_end.append(f"carta {k + 1}: {nm} {tx}")
checa(f"cada carta tem a largura da seção (D a {_CN}), e a DADOS_AM publica o endereço do nome e do texto dela (ADDRESS)",
      bool(ETIQ) and not _ruins_end, "; ".join(_ruins_end[:3]))
# 05/10/2026: "n esqueça do espaçamento de uma linha entre uma carta e outra"; e a caixa do texto continua retrátil
_fim_carta = [x[0] + _hb.CAIXA for x in ETIQ]
_vaos = [r + 1 for r, prox in zip(_fim_carta, [x[0] for x in ETIQ][1:]) if prox > r + 1]
_vao_ruim = [r for r in _vaos if any(F0.cell(row=r, column=c).value not in (None, "") for c in range(_hb.C1, _hb.CN + 1))
             or any(m.min_row <= r <= m.max_row for m in F0.merged_cells.ranges if m.min_col <= _hb.CN and m.max_col >= _hb.C1)]
_seguidas = [(a, b) for a, b in zip([x[0] for x in ETIQ], [x[0] for x in ETIQ][1:]) if b - a != _hb.CAIXA + 2 and b - a < 2 * (_hb.CAIXA + 2)]
checa("entre uma carta e a seguinte do mesmo bloco há uma linha vazia, sem caixa nem mesclagem",
      bool(_vaos) and not _vao_ruim and not _seguidas, f"{_vao_ruim[:3]} {_seguidas[:3]}")
_caixa_grupo = [x[0] for x in ETIQ if not all(F0.row_dimensions[x[0] + 1 + k].outlineLevel > F0.row_dimensions[x[0]].outlineLevel
                                               and not F0.row_dimensions[x[0] + 1 + k].hidden for k in range(_hb.CAIXA))]
checa("a caixa do texto de cada carta é um grupo de linhas que abre e fecha, e nasce aberto", not _caixa_grupo, str(_caixa_grupo[:3]))
_gs = open("apps-script/Habilidades.gs", encoding="utf-8").read()
_m = re.search(r"var HABILIDADES_DO_LIVRO_ = (\[.*?\]);\n", _gs, re.S)
_lido = json.loads(_m.group(1)) if _m else []
_mm = re.search(r"var MEDIDA_DAS_CARTAS_ = (\{.*\});\s*$", _gs, re.S)
_MED = json.loads(_mm.group(1)) if _mm else {}
_esp = [dict(zip(("dono", "fonte", "nivel", "nome", "texto", "linhas", "titulos"), l)) for l in _hb.linhas_do_livro()]
checa(f"o Habilidades.gs é o livro que o gerador monta ({len(_esp)} habilidades), e cabe no teto do Apps Script ({len(_gs) // 1024} KB)",
      _lido == _esp and _MED == _hb.medida() and len(_gs) / 1024 < 900, f"{len(_lido)} lidas, {len(_esp)} esperadas")
# a largura da caixa sai das colunas da planilha gerada, e não da constante do gerador
_px = lambda c: 28 if abs(F0.column_dimensions[ix._letras(c)].width - 4.0) < 1e-6 else None
_larg = [_px(c) for c in range(_hb.C1, _hb.CN + 1)]
checa(f"a medida da carta no Habilidades.gs é a da planilha: {len(_larg)} colunas de 28 px, menos a folga ({_MED.get('largura')} px)",
      None not in _larg and _MED.get("largura") == sum(_larg) - _MED.get("respiro", -1), str(_larg[:3]))
_letras_livro = set("".join(l["nome"] + l["texto"] for l in _lido)) - {"\n"}
_sem = sorted(_letras_livro - set(_MED.get("larguras", {})))
checa(f"toda letra do texto do livro ({len(_letras_livro)}) tem a largura medida na tabela da Roboto 10", not _sem, "".join(_sem[:20]))
_CATj = json.load(open("catalogo-projeto-m.json", encoding="utf-8"))
_tem = lambda fonte, dono: sorted(l["nivel"] for l in _lido if l["fonte"] == fonte and l["dono"] == dono)
_menu_t = [t for t, _ in _fau.trilhas_do_menu(_CATj)]
_falta = [c for c in _CATj["caminhos"] if _tem("Caminho", c) != _cam] + [t for t in _menu_t if _tem("Trilha", t) != _tri]
checa(f"todo Caminho tem as {len(_cam)} cartas e toda Trilha do menu ({len(_menu_t)}, com as rotas do Batedor) tem as {len(_tri)}",
      bool(_cam) and not _falta, str(_falta[:4]))
_DADOS = WB0["DADOS"]
_L = [_DADOS.cell(row=r, column=12).value for r in range(4, 4 + len(_menu_t) + 1)]
checa("a lista de Trilhas da DADOS é a do menu, com o Batedor aberto nas três rotas do livro",
      _L[:-1] == _menu_t and _L[-1] in (None, "") and "Batedor" not in _L
      and [t for t in _menu_t if t.startswith("Batedor · ")] == [f"Batedor · {r}" for r in _xh.extrai()["rotas"]["Batedor"]], str(_L))
_junto = [l for l in _lido if l["fonte"] == _hb.FONTE_JUNTO]
checa("a Rajada Marcial do Pugilista mora na carta 7 do Caminho dele, junto da habilidade do Incursor no 7",
      [(l["dono"], l["nivel"]) for l in _junto] == [("Pugilista", 7)] and _CATj["trilhas"]["Pugilista"] == "Incursor"
      and _junto[0]["texto"].startswith(next(l["texto"] for l in _lido if l["fonte"] == "Caminho" and l["dono"] == "Incursor" and l["nivel"] == 7)),
      str([(l["dono"], l["nivel"]) for l in _junto]))
# 05/10/2026, o nível 7 da Vanguarda ganhou a Execução Preparada (D42 do livro): quando a carta junta mais de uma
# habilidade e o livro abre o parágrafo com o nome de uma delas ("Nível 7: Execução Preparada."), o nome fica na carta,
# como subtítulo em negrito. Antes, a marca saía inteira e a segunda habilidade ficava sem nome. A lista sai do
# manual.txt, pela seção de cada dono no capítulo, e não do extrator; e confere a carta do Habilidades.gs e o que o
# extrator tira hoje.
_man = open("manual.txt", encoding="utf-8").read().splitlines()
_ini6 = _man.index("## 6. Caminhos e Trilhas")
_fim6 = next(i for i in range(_ini6 + 1, len(_man)) if _man[i].startswith("## "))
_xe = _xh.extrai()
_cab_donos = {"### " + d.replace(" · ", ": ") for g in ("caminhos", "trilhas") for d in _xe[g]}
def _secao(dono):
    """do título do dono até o título do dono seguinte (ou o fim do capítulo): os subtítulos ### do meio são dele"""
    a = _man.index("### " + dono.replace(" · ", ": "), _ini6, _fim6)
    return _man[a + 1:next(i for i in range(a + 1, _fim6 + 1) if i == _fim6 or _man[i] in _cab_donos)]
_com_nome, _sem_nome = [], []
for l in _lido:
    if l["fonte"] not in (_hb.FONTE_CAMINHO, _hb.FONTE_TRILHA):
        continue
    partes = [p.strip() for p in re.split(r",| e ", l["nome"]) if p.strip()]
    if len(partes) < 2:
        continue
    ext = _xe["caminhos" if l["fonte"] == _hb.FONTE_CAMINHO else "trilhas"][l["dono"]][str(l["nivel"])]
    for linha in _secao(l["dono"]):
        m = re.match(rf"^Nível {l['nivel']}: ([^.]{{1,80}})\. (.+)", linha)
        if not (m and m.group(1) in partes):
            continue
        _com_nome.append((l["dono"], l["nivel"], m.group(1)))
        for onde, h in (("Habilidades.gs", l), ("extrator", ext)):
            if m.group(1) not in h["titulos"] or f"{m.group(1)}\n\n{m.group(2)}" not in h["texto"]:
                _sem_nome.append(f"{l['dono']} {l['nivel']}, {m.group(1)} ({onde})")
checa("a carta que junta duas habilidades mostra o nome de cada uma que o livro abre por \"Nível N: Nome.\", em subtítulo",
      ("Vanguarda", 7, "Execução Preparada") in _com_nome and not _sem_nome, f"{_sem_nome[:3]} · achadas {len(_com_nome)}")
# 05/10/2026, pedido do Mizuki: "Nome da técnica aparecer na ficha amaldiçoada". Ele escolheu "Espelha a CARTEIRA": a caixa
# NOME DA TÉCNICA é referência pura para uma conta da DADOS_AM (quem escreve por cima recebe a conta de volta, pelo onEdit),
# a conta lê o campo TÉCNICA DECLARADA da CARTEIRA, o script sabe que a caixa vem de lá (o aviso diz onde escrever), e,
# recalculada, a Kaori mostra o nome que está escrito na CARTEIRA dela.
_rot_nt = [c for linha in WB0[ABA].iter_rows() for c in linha if c.value == "NOME DA TÉCNICA"]
_cel_nt = f"{_rot_nt[0].column_letter}{_rot_nt[0].row + 1}" if len(_rot_nt) == 1 else None
_m_nt = re.fullmatch(rf"={DAM}!\$([A-Z]+)\$(\d+)", str(WB0[ABA][_cel_nt].value)) if _cel_nt else None
_conta_nt = str(WB0[DAM][_m_nt.group(1) + _m_nt.group(2)].value).replace("$", "") if _m_nt else None
_cru_am = json.loads(re.search(r"var ABAS = ([\s\S]*?);\n\nvar ARTE = ", open("apps-script/Ficha.gs", encoding="utf-8").read()).group(1))
_da_car = next((a.get("da_carteira") for a in _cru_am if a["nome"] == ABA), None)
_lido_nt = txt(WB["kaori"][ABA][_cel_nt].value) if "kaori" in WB and _cel_nt else None
checa("a caixa NOME DA TÉCNICA espelha a TÉCNICA DECLARADA da CARTEIRA: aponta para a conta, a conta lê o campo, o script "
      "avisa que ela vem de lá, e a Kaori recalculada mostra o nome escrito na CARTEIRA",
      bool(CAMPO_TEC and _m_nt) and _conta_nt == f'=CARTEIRA!{CAMPO_TEC}&""' and _da_car == [_cel_nt]
      and ("kaori" not in WB or _lido_nt == "Peso Emprestado"),
      f"campo {CAMPO_TEC}, caixa {_cel_nt}, conta {_conta_nt}, script {_da_car}, Kaori {_lido_nt!r}")
for nome in FICHAS:
    ficha, f = FICHAS[nome], WB[nome]["FICHA"]
    n = ficha.get("nivel", 2)
    esp = [f"Nível {L}" if L <= n else f"Abre no {L}" for L in NIV_HAB]
    lido = [txt(f[x[3]].value) for x in ETIQ]
    up_ = lambda k, padrao: "" if not ficha.get(k) else "  ·  " + ficha[k].upper()
    esp_t = ["CAMINHO" + up_("caminho", "") + "  ·  CINCO DEGRAUS", "TRILHA" + up_("trilha", "") + "  ·  QUATRO ENTREGAS"]
    lido_t = [txt(f[x[2]].value) for x in TIT]
    checa(f"{nome} (nível {n}): as etiquetas dizem o nível ou quando a carta abre, e os títulos dizem o Caminho e a Trilha",
          lido == esp and lido_t == esp_t, f"{lido} {lido_t} != {esp} {esp_t}")

# ---------------------------------------------------------------------------------------------
print("\nA ABA")
ws0 = WB0[ABA]
checa("a aba tem as linhas e as colunas que a geometria diz", ws0.max_row == G["linhas"] and ws0.max_column == fa.COLS, f"{ws0.max_row} x {ws0.max_column}")
# o retorno do Mizuki depois de usar a aba no Sheets (01/10/2026)
_mesc = {str(m) for m in ws0.merged_cells.ranges}
_tit = [f"D{G['sec'][sid]}:T{G['sec'][sid] + fa.FX - 1}" for sid, _, _ in fa.SECOES]
checa("o título de cada seção vai de ponta a ponta, sem o texto pequeno ao lado", all(t in _mesc for t in _tit), str([t for t in _tit if t not in _mesc]))
_resp = [r for r in range(G["fim"]["pactos"] + 1, G["linhas"] + 1)]
checa("embaixo do último pacto há duas linhas de respiro, vazias e fora de grupo",
      len(_resp) == 2 and all(ws0.cell(row=r, column=c).value is None for r in _resp for c in range(3, fa.COLS + 1))
      and all(not ws0.row_dimensions[r].outlineLevel for r in _resp), str(_resp))
_contas = [f"{c.coordinate}: {c.value[:50]}" for linha in ws0.iter_rows(min_row=G["saltos"]) for c in linha
           if isinstance(c.value, str) and c.value.startswith("=") and not fa.REFERENCIA_PURA.fullmatch(c.value)]
_n_calc = sum(1 for linha in ws0.iter_rows(min_row=G["saltos"]) for c in linha if isinstance(c.value, str) and c.value.startswith("="))
checa(f"as {_n_calc} caixas calculadas da aba só apontam para uma célula: a conta mora na DADOS_AM, e o script sabe devolver a caixa",
      _n_calc > 700 and not _contas, f"{len(_contas)}: " + "; ".join(_contas[:3]))
_cor = lambda coord: (ws0[coord].fill.fgColor.rgb or "")[-6:].upper()
_nomes = [c["nome"] for c in FEITICOS + LIBS + PASSIVAS + APTIDOES + PACTOS] + [c["classe"] for c in FEITICOS + LIBS]
_fora = [n for n in _nomes if _cor(n) != fa.ACENTO[-6:].upper()]
checa(f"o nome de cada carta (e a Classe, na de feitiço) está na cor de título: {len(_nomes)} caixas", not _fora, str(_fora[:6]))
_est = [c["estado"] for c in FEITICOS + LIBS if _cor(c["estado"]) == fa.ACENTO[-6:].upper()]
checa("o estado da carta fica fora da cor de título, para a cor de aviso se ler", not _est, str(_est[:4]))
larguras = [int(round(8 * ws0.column_dimensions[ix._letras(c)].width - 1)) for c in range(1, fa.COLS + 1)]
larguras = [28 if abs(ws0.column_dimensions[ix._letras(c)].width - 4.0) < 1e-6 else p for c, p in zip(range(1, fa.COLS + 1), larguras)]
checa(f"as três cartas têm {sum(fa.PX_CARTA)} px cada, e a página {sum(fa.PX_COLUNAS)} px", larguras == fa.PX_COLUNAS, str(larguras))
checa("os lugares cobrem o teto do livro: 24 espaços no nível 30, sete feitiços do Leque e três de pacto",
      fa.N_FEITICOS >= 2 + 30 // 2 + 2 * len(PROG["marcos"]) + 3 and fa.PAGAS + fa.DO_LEQUE == 12 and len(PASSIVAS) == 12 and len(APTIDOES) >= 11)
import conferir_feitico as _cf
checa("as quatro Restrições de frequência são as do conferir_feitico.py", set(fa.FREQUENCIA) == set(_cf.FREQUENCIA) == set(FREQUENCIA))
formulas_am = [c for linha in ws0.iter_rows() for c in linha if isinstance(c.value, str) and c.value.startswith("=")]
fora = [c.coordinate for c in formulas_am if "DADOS_AM!" not in c.value and "FICHA!" not in c.value and "DADOS!" not in c.value]
checa(f"nenhuma das {len(formulas_am)} fórmulas da aba faz conta: todas leem a DADOS_AM, a FICHA ou a DADOS", not fora, str(fora[:5]))
sem_let = [c.coordinate for ws in (WB0[ABA], WB0[DAM]) for linha in ws.iter_rows() for c in linha
           if isinstance(c.value, str) and c.value.startswith("=") and re.search(r"\b(LET|LAMBDA|MAP|REDUCE|BYROW|IFS|SWITCH)\(", c.value)]
checa("nenhuma fórmula usa LET, LAMBDA, IFS ou SWITCH (o LibreOffice da regressão não tem as duas primeiras)", not sem_let, str(sem_let[:5]))

# ---------------------------------------------------------------------------------------------
print("\nO FICHA.GS: A ABA MONTADA NO SHEETS DE MENTIRA")
PROG_JS = r"""
const fs = require('fs'), { criaSheets, CHAMADAS } = require('./medidas/sheets-de-mentira.js');
const S = criaSheets(fs.readFileSync('apps-script/Ficha.gs', 'utf8') + '\\n' + fs.readFileSync('apps-script/Invocacoes.gs', 'utf8'), fs.readFileSync('apps-script/Codigo.gs', 'utf8'), JSON.parse(process.argv[2] || '{}'));
if (process.argv[3] === 'sem-mesclagem') S.P.copiaTrazMesclagem = false;
S.ctx.construir();
const out = { registro: S.P.registros[S.P.registros.length - 1], orfas: S.P.orfas, chamadas: CHAMADAS, abas: {} };
for (const nome of ['FICHA AMALDIÇOADA', 'DADOS_AM']) {
  const A = S.acha(nome);
  out.abas[nome] = { formulas: Object.fromEntries(A.f), valores: Object.fromEntries(A.v), mesclagens: A.merges.map((m) => m.join()).sort(),
    menus: Object.fromEntries([...A.dv].map(([k, v]) => [k, v.faixa || v.lista])), caixas: [...A.caixas].sort(), grupos: Object.fromEntries(A.profL),
    fechados: A.fechL.map((g) => g.join()).sort(), notas: A.notas.size, numeros: Object.fromEntries(A.fmt), cf: A.cf.length };
}
console.log(JSON.stringify(out));
"""


def monta_no_sheets(modo=""):
    r = subprocess.run(["node", "-e", PROG_JS, "x", "{}", modo], capture_output=True, text=True, timeout=300)
    if r.returncode:
        print(r.stderr[-800:])
        return None
    return json.loads(r.stdout)


def formulas_do_xlsx(ws):
    sys.path.insert(0, "ficha")
    import emitir_gs
    out = {}
    for linha in ws.iter_rows():
        for c in linha:
            if isinstance(c.value, str) and c.value.startswith("="):
                out[f"{c.row},{c.column}"] = emitir_gs._valor(c.value)
    return out


M = monta_no_sheets()
checa("o construir() monta a planilha inteira, com a aba nova, sem estourar em nenhuma chamada", M is not None)
if M:
    for nome in (ABA, DAM):
        esperadas, feitas = formulas_do_xlsx(WB0[nome]), dict(M["abas"][nome]["formulas"])
        # os dez saltos viram ligação no acabamento: o texto da planilha gerada vira a fórmula HYPERLINK
        saltos = {k: f for k, f in feitas.items() if f.startswith("=HYPERLINK(")}
        feitas = {k: f for k, f in feitas.items() if k not in saltos}
        dif = [k for k in set(esperadas) | set(feitas) if esperadas.get(k) != feitas.get(k)]
        checa(f"{nome}: as {len(esperadas)} fórmulas montadas são as da planilha gerada, célula a célula"
              + (" (as preenchidas para baixo inclusive)" if nome == DAM else ""), not dif,
              f"{len(dif)}: " + "; ".join(f"{k}: {str(feitas.get(k))[:60]!r} != {str(esperadas.get(k))[:60]!r}" for k in dif[:2]))
        if nome == ABA:
            checa("os dez saltos da linha 7 viram ligação para o título de cada seção",
                  len(saltos) == len(fa.SECOES) and all(f'&range=D{G["sec"][s]}"' in saltos[f"{G['saltos']},{ix._col(c1)}"]
                                                        for (s, _, _), (c1, _) in zip(fa.SECOES, fa._cols_dos_saltos())), str(list(saltos.items())[:2]))
            # 02/10/2026: quatro saltos mudam de nome com a rota, e o link cita a célula do nome na DADOS_AM
            muda = [f"{G['saltos']},{ix._col(c1)}" for (s, _, _), (c1, _) in zip(fa.SECOES, fa._cols_dos_saltos()) if s in ("feiticos", "lib", "tm", "aptidoes")]
            checa("os quatro saltos que mudam de nome com a rota citam a célula do nome na DADOS_AM",
                  len(muda) == 4 and all(re.search(r'",DADOS_AM!\$[A-Z]+\$\d+\)$', saltos.get(k, "")) for k in muda), str([saltos.get(k) for k in muda][:2]))
    am = M["abas"][ABA]
    # os valores que não são fórmula: os rótulos, os textos e o que cada menu traz escolhido de fábrica
    saltos_v = {f"{G['saltos']},{ix._col(c1)}" for c1, _ in fa._cols_dos_saltos()}
    esp_v = {f"{c.row},{c.column}": c.value for linha in WB0[ABA].iter_rows() for c in linha
             if c.value is not None and not (isinstance(c.value, str) and c.value.startswith("=")) and f"{c.row},{c.column}" not in saltos_v}
    lido_v = {k: v for k, v in am["valores"].items() if not (isinstance(v, str) and v.startswith("IMAGEM "))}
    dif_v = [k for k in set(esp_v) | set(lido_v) if esp_v.get(k) != lido_v.get(k)]
    checa(f"os {len(esp_v)} rótulos, textos e valores de fábrica da aba chegam iguais, as fileiras copiadas inclusive", not dif_v,
          f"{len(dif_v)}: " + "; ".join(f"{k}: {lido_v.get(k)!r} != {esp_v.get(k)!r}" for k in sorted(dif_v)[:3]))
    # o ABAS que o script expande quando carrega é o mesmo que o gerador expande
    sys.path.insert(0, "ficha")
    import emitir_gs as _eg
    _js = subprocess.run(["node", "-e", "const fs=require('fs'),vm=require('vm'),c={};vm.createContext(c);vm.runInContext(fs.readFileSync('apps-script/Ficha.gs','utf8')+'\\n'+fs.readFileSync('apps-script/Invocacoes.gs','utf8'),c);"
                          "console.log(JSON.stringify(vm.runInContext('ABAS',c)))"], capture_output=True, text=True, timeout=120)

    def _norm(x):
        if isinstance(x, float) and x.is_integer():
            return int(x)
        if isinstance(x, list):
            return [_norm(y) for y in x]
        if isinstance(x, dict):
            return {k: _norm(v) for k, v in x.items() if k != "copias_feitas"}
        return x
    _do_script = _norm(json.loads(_js.stdout)) if _js.returncode == 0 else []
    _do_gerador = _norm(_eg.abas_do_script("apps-script/Ficha.gs"))
    _cru = _eg.abas_cruas("apps-script/Ficha.gs")
    _n_cru = next(len(a["vals"]) for a in _cru if a["nome"] == ABA)
    _n_cheio = next((len(a["vals"]) for a in _do_script if a["nome"] == ABA), 0)
    checa(f"as fileiras copiadas voltam inteiras quando o script carrega ({_n_cru} células escritas viram {_n_cheio}), iguais às que o gerador expande",
          len(_do_script) == len(_do_gerador) and all(_eg._forma_canonica(a) == _eg._forma_canonica(b) for a, b in zip(_do_script, _do_gerador))
          and _n_cheio > _n_cru)
    mescladas = sorted(f"{m.min_row},{m.min_col},{m.max_row},{m.max_col}" for m in WB0[ABA].merged_cells.ranges)
    checa(f"as {len(mescladas)} mesclagens da aba chegam iguais, com as fileiras de cartas vindo por cópia de formato", am["mesclagens"] == mescladas
          and "fileiras copiadas" in M["registro"], f"{len(am['mesclagens'])} montadas")
    ch = M["chamadas"]
    n_mescla = ch.get("Range.merge", 0) + ch.get("Range.mergeAcross", 0) + ch.get("Range.mergeVertically", 0)
    # 02/10/2026: o menu rápido da FICHA também copia as fileiras de cartas, uma cópia por fileira
    _copias_ficha = sum(len(k[2]) for a in _cru if a["nome"] == "FICHA" for k in a.get("copias") or [])
    # 06/10/2026: a INVOCAÇÕES também é montada nesta planilha. As mesclagens que ela faz fora das fileiras copiadas (as
    # que o Invocacoes.gs escreve) e as cópias dela saem da conta daqui; quem as mede é a regressao-invocacoes.py
    _inv = next((a for a in _cru if a["nome"] == "INVOCAÇÕES"), {})
    _mescla_inv, _copias_inv = len(_inv.get("merges") or []), sum(len(k[2]) for k in _inv.get("copias") or [])
    checa(f"a aba nova não triplica a montagem: {n_mescla} chamadas de mesclagem na planilha inteira (eram 310 sem ela; até {_mescla_inv} são da INVOCAÇÕES), "
          f"{ch.get('Range.copyTo', 0)} cópias ({_copias_ficha} do menu rápido, {_copias_inv} da INVOCAÇÕES)",
          n_mescla < 700 + _mescla_inv and 0 < _copias_ficha and ch.get("Range.copyTo", 0) < 40 + _copias_ficha + _copias_inv,
          f"{n_mescla} · {ch.get('Range.copyTo', 0)}")
    menus = {}
    for dv in WB0[ABA].data_validations.dataValidation:
        for rg in str(dv.sqref).split():
            (l1, c1), (l2, c2) = (ix._lc(x) for x in (rg.split(":") + [rg.split(":")[0]])[:2])
            for l in range(l1, l2 + 1):
                for c in range(c1, c2 + 1):
                    menus[f"{l},{c}"] = dv.formula1.replace("$", "")
    checa(f"os {len(menus)} menus chegam à célula certa com a lista certa, numa gravação só",
          {k: v.replace("$", "") for k, v in am["menus"].items()} == menus
          and ch.get("Range.setDataValidations", 0) == sum(1 for a in _cru if a.get("validacao_em_matriz")),      # uma por aba que pede
          f"{len(am['menus'])} montados, {ch.get('Range.setDataValidations', 0)} gravações")
    caixas = sorted(f"{c.row},{c.column}" for linha in WB0[ABA].iter_rows() for c in linha if isinstance(c.value, bool))
    # 01/10/2026: a caixa de seleção do Selo saiu da carta ("o selo n obriga restrição nenhuma é algo mais narrativo")
    checa("a aba não tem caixa de seleção: a do Selo saiu da carta", caixas == [] and am["caixas"] == [], f"{len(caixas)} na planilha, {len(am['caixas'])} montadas")
    prof = {str(r): (WB0[ABA].row_dimensions[r].outlineLevel or 0) for r in range(1, G["linhas"] + 1) if WB0[ABA].row_dimensions[r].outlineLevel}
    checa("os grupos de linhas têm a profundidade da planilha gerada (seção, lote e fileira)", {k: v for k, v in am["grupos"].items() if v} == prof)
    abertos = [f"{G['sec'][s] + fa.FX},{G['fim'][s]},1" for s, _, _ in fa.SECOES if s not in fa.NASCE_FECHADA]
    # as linhas que somem na aba montada (as de todo grupo fechado) são as que a planilha gerada traz escondidas
    escondidas = {r for r in range(1, G["linhas"] + 1) if WB0[ABA].row_dimensions[r].hidden}
    somem = {r for g in am["fechados"] for r in range(int(g.split(",")[0]), int(g.split(",")[1]) + 1)}
    r0 = G["feiticos"][0][0]
    checa("nascem abertas as seções que o nível 2 usa e a primeira fileira de cada tipo; o resto nasce fechado, como na planilha gerada",
          not any(g in am["fechados"] for g in abertos) and all(f"{G['sec'][s] + fa.FX},{G['fim'][s]},1" in am["fechados"] for s in fa.NASCE_FECHADA)
          and somem == escondidas and r0 + fa.F_MEL not in somem and G["feiticos"][3][0] + fa.F_MEL in somem,
          f"{len(am['fechados'])} grupos fechados; {len(somem ^ escondidas)} linha(s) diferentes")
    checa("nenhuma fórmula é gravada antes de a aba que ela cita existir, nem fora do inglês", not M["orfas"], str(M["orfas"][:3]))
    checa("a Classe aparece como 'Classe 3' e continua número", len(am["numeros"]) == fa.N_FEITICOS + fa.N_LIB + 1 and set(am["numeros"].values()) == {'"Classe "0'},
          f"{len(am['numeros'])}")
    # o plano B: se o Sheets não trouxer a mesclagem com o formato, o script faz uma a uma e a aba sai igual
    B = monta_no_sheets("sem-mesclagem")
    checa("se a cópia de formato não trouxer a mesclagem, o script percebe, mescla uma a uma e a aba sai igual",
          B is not None and B["abas"][ABA]["mesclagens"] == mescladas and "UMA A UMA" in B["registro"],
          "" if B is None else f"{len(B['abas'][ABA]['mesclagens'])} mesclagens · {B['registro'][:120]}")

print("\n" + "=" * 60)
if FALHAS:
    print(f"FALHOU: {len(FALHAS)} checagem(ns)")
    for x in FALHAS:
        print("  - " + x)
    sys.exit(1)
print("A FICHA AMALDIÇOADA BATE COM A REGRA")
