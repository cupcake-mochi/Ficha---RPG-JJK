# -*- coding: utf-8 -*-
"""A aba DADOS que sai do catalogo, e nao da exportacao.

v0.239 do sistema, decisao do Mizuki em 14/09/2026: o catalogo foi da v0.104 a v0.239, e a aba
DADOS da planilha viva ainda carregava o de antes. A planilha viva continua dona do DESENHO
desta aba; o catalogo e dono do CONTEUDO dela.

O monta.py escreve estes valores por cima do layout.json, e o comparar-ficha-01.py le a mesma
funcao para contar a limpeza. Uma funcao, dois leitores: e a licao no 9.

As doze listas -- colunas A a L, titulo na linha 3 e itens da 4 em diante --, o carimbo em B1 e
D1 e, desde 04/10/2026, a tabela dos Caminhos (N4 em diante): o livro reconstruido trouxe o
Incursor e mudou as pericias fixas do Bastiao, e a tabela deixou de "vir como veio". A coluna O,
que era o dado de vida, passa a guardar os atributos naturais: o livro novo nao tem mais dado, e
nenhuma formula le essa coluna (a FICHA le a 3, a 4 e a 5). Os marcos e a tabela de pericias
ficam como vieram, e batem com o catalogo.
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUNAS = "ABCDEFGHIJKL"


def listas(CAT, DEC):
    tr = CAT["testes_de_resistencia"]
    return [
        ("A", "Caminhos", list(DEC["C1_evocador"]["caminhos_no_menu"])),
        ("B", "Perícias", list(CAT["pericias"])),
        ("C", "Ofícios", list(CAT["oficios"])),
        ("D", "Famílias", list(CAT["familias"])),
        ("E", "Formas", list(CAT["formas"])),
        ("F", "Melhorias", list(CAT["melhorias"])),
        ("G", "Restrições", list(CAT["restricoes"])),
        ("H", "Condições", list(CAT["condicoes"])),
        # 17/09/2026: o menu de Origem abre a Sem Técnica nas cinco principais e a Restrição Celestial nos dois
        # ramos, na ordem das rotas de criação. A ficha precisa da rota; ver ficha_automatica.origens_do_menu.
        ("I", "Origens", __import__("ficha_automatica").origens_do_menu(CAT)),
        ("J", "Testes", [t for t in tr if isinstance(tr[t], dict)]),
        # a v0.104 escrevia aqui as CHAVES do dicionario (lista, escala, criacao, pagina)
        ("K", "Atributos", list(CAT["atributos"]["lista"])),
        # 05/10/2026: a Trilha com rotas entra uma vez por rota ("Batedor · Yumi"); ver ficha_automatica.trilhas_do_menu
        ("L", "Trilhas", [t for t, _ in __import__("ficha_automatica").trilhas_do_menu(CAT)]),
    ]


CAMINHOS_COL, CAMINHOS_LIN = "N", 4          # o cabecalho da tabela dos Caminhos
CAMINHOS_CAB = ["Caminho", "atributos naturais", "vida inicial", "vida por nível", "PE por nível", "perícia fixa 1", "perícia fixa 2"]
CAMINHOS_MAX = 7                              # linhas reservadas: a 11 ja tem os marcos e a tabela de pericias ao lado


def caminhos(CAT, DEC):
    """{celula: valor} da tabela dos Caminhos: o cabecalho e uma linha por Caminho do menu"""
    c0 = _col(CAMINHOS_COL)
    val = {f"{_letra(c0 + j)}{CAMINHOS_LIN}": t for j, t in enumerate(CAMINHOS_CAB)}
    nomes = list(DEC["C1_evocador"]["caminhos_no_menu"])
    if len(nomes) > CAMINHOS_MAX:
        raise SystemExit(f"a tabela dos Caminhos da DADOS cabe {CAMINHOS_MAX}, e o menu tem {len(nomes)}")
    for i in range(CAMINHOS_MAX):
        lin = CAMINHOS_LIN + 1 + i
        if i < len(nomes):
            d = CAT["caminhos"][nomes[i]]
            linha = [nomes[i], " · ".join(d["atributos_naturais"]), d["vida_inicial"], d["vida_por_nivel"], d["pe_por_nivel"]] + d["pericias_fixas"]
        else:
            linha = [None] * len(CAMINHOS_CAB)
        for j, v in enumerate(linha):
            val[f"{_letra(c0 + j)}{lin}"] = v
    return val


def faixa_dos_caminhos(DEC):
    """a faixa que o VLOOKUP da vida e do PE da FICHA le: da primeira linha do Caminho ate a ultima"""
    n = len(DEC["C1_evocador"]["caminhos_no_menu"])
    return f"DADOS!${CAMINHOS_COL}${CAMINHOS_LIN + 1}:$U${CAMINHOS_LIN + n}"


def _col(letras):
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def _letra(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def valores(CAT=None, DEC=None):
    """{celula: valor} de tudo que a DADOS recebe do catalogo."""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    if DEC is None:
        DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))
    # o nome do sistema tambem mora aqui (17/09/2026): a CARTEIRA e a FICHA leem dele, e ele sai do catalogo
    val = {"B1": CAT["_meta"]["versao"], "D1": CAT["_meta"]["versao"], "E1": "NOME DO SISTEMA", "F1": CAT["_meta"]["sistema"]}
    for col, titulo, itens in listas(CAT, DEC):
        val[f"{col}3"] = titulo
        for i, v in enumerate(itens):
            val[f"{col}{4 + i}"] = v
    val.update(caminhos(CAT, DEC))
    return val


def troca_na_ficha(layout, DEC=None):
    """a vida e o PE da FICHA leem a tabela dos Caminhos por VLOOKUP numa faixa escrita na formula: ela cresce com o
    menu. Devolve quantas formulas mudaram."""
    if DEC is None:
        DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))
    nova = faixa_dos_caminhos(DEC)
    ficha = next(a for a in layout["abas"] if a["nome"] == "FICHA")
    n = 0
    for reg in ficha["celulas"]:
        if isinstance(reg[1], str) and reg[1].startswith("="):
            novo = re.sub(r"DADOS!\$N\$5:\$U\$\d+", lambda _: nova, reg[1])
            if novo != reg[1]:
                reg[1], n = novo, n + 1
    return n


def e_da_lista(coord):
    """a celula e de uma das doze listas, do item um para baixo"""
    m = re.match(r"^([A-Z]+)(\d+)$", coord)
    # UMA letra: com `in COLUNAS` a coluna AB passava por lista, porque "AB" esta dentro de
    # "ABCDEFGHIJKL", e a tabela de pericias da DADOS saia vazia. Achado em 15/09/2026.
    return bool(m) and len(m.group(1)) == 1 and m.group(1) in COLUNAS and int(m.group(2)) >= 4


def aplica(aba, val):
    """poe os valores do catalogo nas celulas da aba DADOS do layout, e esvazia o que passou
    do fim de uma lista que encolheu. Devolve quantas celulas mudaram."""
    existentes = {reg[0]: reg for reg in aba["celulas"]}
    mudou = 0
    for reg in aba["celulas"]:
        if reg[0] in val:
            novo = val[reg[0]]
        elif e_da_lista(reg[0]):
            novo = None
        else:
            continue
        if reg[1] != novo:
            reg[1] = novo
            mudou += 1
    for coord, v in val.items():
        if coord not in existentes:
            col = re.match(r"^([A-Z]+)", coord).group(1)
            ref = f"{col}4" if col in COLUNAS and len(col) == 1 else f"{col}{CAMINHOS_LIN + 1}"
            estilo = existentes[ref][2] if ref in existentes else None
            aba["celulas"].append([coord, v, estilo])
            mudou += 1
    return mudou
