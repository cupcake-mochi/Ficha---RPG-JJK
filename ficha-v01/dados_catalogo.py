# -*- coding: utf-8 -*-
"""A aba DADOS que sai do catalogo, e nao da exportacao.

v0.239 do sistema, decisao do Mizuki em 14/09/2026: o catalogo foi da v0.104 a v0.239, e a aba
DADOS da planilha viva ainda carregava o de antes. A planilha viva continua dona do DESENHO
desta aba; o catalogo e dono do CONTEUDO dela.

O monta.py escreve estes valores por cima do layout.json, e o comparar-ficha-01.py le a mesma
funcao para contar a limpeza. Uma funcao, dois leitores: e a licao no 9.

So as doze listas -- colunas A a L, titulo na linha 3 e itens da 4 em diante -- e o carimbo
em B1 e D1. A tabela dos Caminhos, os marcos e a tabela de pericias ficam como vieram: as
formulas da FICHA leem delas, e elas batem com o catalogo.
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
        ("L", "Trilhas", list(CAT["trilhas"])),
    ]


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
    return val


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
            estilo = existentes[f"{col}4"][2] if f"{col}4" in existentes else None
            aba["celulas"].append([coord, v, estilo])
            mudou += 1
    return mudou
