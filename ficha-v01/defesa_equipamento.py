# -*- coding: utf-8 -*-
"""A Defesa com uniforme e escudo, e o refino escolhido nos marcos. E o B3, na opcao A.

A planilha viva tinha um campo EQUIPAMENTO de numero: preenchido, ele trocava a protecao da aptidao
pelo que o jogador digitasse; vazio, valia `1/3 do refino de graca + 1`. Medido em 16/09/2026 contra
as 21.632 combinacoes legais de nivel, Destreza, refino, uniforme e escudo, a Defesa saia errada em
80,8% delas: o campo nao aplicava o teto de Destreza, nao somava o escudo por cima da aptidao, e o
refino nao contava as escolhas de Refino nos marcos.

Decisao do Mizuki: a opcao A, com o campo das escolhas de Refino. O EQUIPAMENTO vira menu das
combinacoes de uniforme e escudo, e a tabela delas vai para a DADOS. O campo das escolhas de Refino
mora, desde 17/09/2026, no `Marco Escolhido` que o Mizuki desenhou na planilha viva.

O monta.py aplica, e o comparar-ficha-01.py le a mesma funcao para contar a limpeza. Uma funcao,
dois leitores, no molde do tr_treinado.py.

Nenhum numero de equipamento mora aqui: a tabela sai da chave `equipamento_defesa` do catalogo, e o
teto do refino sai do manual.txt. Nenhum endereco esta escrito: as celulas da FICHA saem do indice
que a ficha publica na DADOS, e a tabela fica onde ela ja esta ou vai para a primeira faixa livre
da DADOS depois das tabelas que existem.
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CABECALHO = ["equipamento", "proteção", "teto de destreza", "desliga a passiva"]


def _col(letras):
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def _letras(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _lc(coord):
    m = re.match(r"^([A-Z]+)(\d+)$", coord)
    return int(m.group(2)), _col(m.group(1))


def _aba(layout, nome):
    return next(a for a in layout["abas"] if a["nome"] == nome)


def indice(layout):
    import indice_ficha
    return indice_ficha.indice(layout)


def tabela(CAT):
    """as linhas da tabela do menu: uniforme, escudo, e cada uniforme com cada escudo"""
    eq = CAT["equipamento_defesa"]
    uni, esc = eq["uniformes"], eq["escudos"]
    tracinho = lambda t: "—" if t is None else t
    linhas = []
    for u, v in uni.items():
        linhas.append([u, v["protecao"], tracinho(v["teto_de_destreza"]),
                       "sim" if eq["uniforme_desliga_a_protecao_de_energia"] else "não"])
    for e, v in esc.items():
        linhas.append([e, v["protecao"], tracinho(v["teto_de_destreza"]), "não"])
    for u, vu in uni.items():
        for e, ve in esc.items():
            tetos = [t for t in (vu["teto_de_destreza"], ve["teto_de_destreza"]) if t is not None]
            assert eq["dois_tetos"] == "vale o menor" and eq["escudo_soma_por_cima"]
            linhas.append([f"{u} + {e}", vu["protecao"] + ve["protecao"],
                           tracinho(min(tetos) if tetos else None),
                           "sim" if eq["uniforme_desliga_a_protecao_de_energia"] else "não"])
    return linhas


def teto_de_refino():
    man = " ".join(open(os.path.join(RAIZ, "manual.txt"), encoding="utf-8").read().split())
    m = re.search(r"o refino é um número de 1 a (\d+)\.", man)
    if not m:
        raise SystemExit("nao achei no manual.txt o teto do refino ('o refino é um número de 1 a N')")
    return int(m.group(1))


def _menu_cobre(aba, coord):
    return any(coord in m["onde"].split() for m in aba["menus"])


def trocas(layout, CAT=None):
    """o que a limpeza muda, sem mudar nada:
    {"celulas": {aba: {coord: (valor, coord_do_estilo)}}, "mescladas": {aba: [faixas]},
     "menus": {aba: [menus]}, "tabela": faixa}

    17/09/2026: a caixa do REFINO ESCOLHIDO passou a morar na planilha viva, dentro do `Marco
    Escolhido` que o Mizuki desenhou, e o `Buff/Debuff` entrou ao lado do EQUIPAMENTO. Esta limpeza
    deixou de criar caixa: ela escreve a tabela, as duas formulas e o menu que faltar, e sai vazia
    quando a planilha viva ja tem tudo igual."""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    idx = indice(layout)
    precisa = ["defesa", "proteção", "equipamento", "refino de graça", "atr_Destreza", "refino escolhido"]
    falta = [k for k in precisa if not idx.get(k)]
    if falta:
        raise SystemExit(f"o indice da DADOS nao publica {falta}")
    ficha, dados = _aba(layout, "FICHA"), _aba(layout, "DADOS")
    abs_ = lambda c: "$" + re.sub(r"(\d+)$", r"$\1", c)
    cel = {"FICHA": {}, "DADOS": {}}

    # --- a tabela: onde ela ja esta, ou na primeira faixa livre da DADOS antes do indice
    ref_cab = next(r[0] for r in dados["celulas"] if r[1] == "marcos")
    lin_cab, col_cab = _lc(ref_cab)
    ja = [r[0] for r in dados["celulas"] if r[1] == CABECALHO[0] and _lc(r[0])[0] == lin_cab]
    if ja:
        c0 = _lc(ja[0])[1]
    else:
        col_idx = _col("BA")
        ocupadas = {_lc(r[0])[1] for r in dados["celulas"] if r[1] is not None and _lc(r[0])[1] < col_idx}
        c0 = max(ocupadas) + 2
    ref_txt = next(r[0] for r in dados["celulas"] if _lc(r[0]) == (lin_cab + 1, 1))
    ref_num = _letras(col_cab) + str(lin_cab + 1)
    linhas = tabela(CAT)
    for j, t in enumerate(CABECALHO):
        cel["DADOS"][f"{_letras(c0 + j)}{lin_cab}"] = (t, ref_cab)
    for i, lin in enumerate(linhas):
        for j, v in enumerate(lin):
            cel["DADOS"][f"{_letras(c0 + j)}{lin_cab + 1 + i}"] = (v, ref_txt if j == 0 else ref_num)
    ini, fim = lin_cab + 1, lin_cab + len(linhas)
    T = f"DADOS!${_letras(c0)}${ini}:${_letras(c0 + 3)}${fim}"
    MENU_EQ = f"DADOS!${_letras(c0)}${ini}:${_letras(c0)}${fim}"

    # --- as formulas: o refino soma as escolhas, no maximo uma por marco que ja passou
    GRACA, EQ, DES, PROT = (abs_(idx["refino de graça"]), abs_(idx["equipamento"]),
                            abs_(idx["atr_Destreza"]), abs_(idx["proteção"]))
    campo = idx["refino escolhido"]
    ESC = f'MIN({GRACA}-1,IFERROR(VALUE({abs_(campo)}&""),0))'
    REFINO = f"MIN({teto_de_refino()},{GRACA}+{ESC})"
    PASSIVA = f"FLOOR({REFINO}/3,1)+1"
    BUFF = f'+IFERROR(VALUE({abs_(idx["buff de defesa"])}&""),0)' if idx.get("buff de defesa") else ""
    cel["FICHA"][idx["proteção"]] = (
        f'=IF({EQ}="",{PASSIVA},IF(VLOOKUP({EQ},{T},4,FALSE)="sim",0,{PASSIVA})'
        f"+VLOOKUP({EQ},{T},2,FALSE))", idx["proteção"])
    cel["FICHA"][idx["defesa"]] = (
        f'=10+IF({EQ}="",{DES},MIN({DES},IFERROR(VALUE(VLOOKUP({EQ},{T},3,FALSE)&""),{DES})))+{PROT}{BUFF}',
        idx["defesa"])

    marcos = len(CAT["progressao"]["marcos"])
    menus = {"FICHA": []}
    if not _menu_cobre(ficha, idx["equipamento"]):
        menus["FICHA"].append({"onde": idx["equipamento"], "tipo": "list", "formula": MENU_EQ,
                               "vazio_ok": True, "mostra_seta": True})
    if not _menu_cobre(ficha, campo):
        menus["FICHA"].append({"onde": campo, "tipo": "list",
                               "formula": '"' + ",".join(str(i) for i in range(marcos + 1)) + '"',
                               "vazio_ok": True, "mostra_seta": True})
    return {"celulas": cel, "mescladas": {"FICHA": []}, "menus": menus, "tabela": T, "refino": REFINO}


def aplica(layout, tr):
    """poe a limpeza no layout. Devolve quantas celulas mudaram de valor ou de estilo."""
    n = 0
    for nome, cels in tr["celulas"].items():
        aba = _aba(layout, nome)
        por = {r[0]: r for r in aba["celulas"]}
        for coord, (valor, ref) in cels.items():
            estilo = por[ref][2] if ref in por else None
            if coord in por:
                reg = por[coord]
                if reg[1] != valor or reg[2] != estilo:
                    reg[1], reg[2] = valor, estilo
                    n += 1
            else:
                aba["celulas"].append([coord, valor, estilo])
                n += 1
    for nome, faixas in tr["mescladas"].items():
        aba = _aba(layout, nome)
        aba["mescladas"] += [f for f in faixas if f not in aba["mescladas"]]
    for nome, menus in tr["menus"].items():
        aba = _aba(layout, nome)
        ja = {m["onde"] for m in aba["menus"]}
        aba["menus"] += [m for m in menus if m["onde"] not in ja]
    return n
