# -*- coding: utf-8 -*-
"""A aba DADOS: o catalogo inteiro, o carimbo de versao, e as colunas de apoio
que as formulas da FICHA consultam. Nada e digitado: tudo sai do catalogo."""
import os
from estilo import *
from openpyxl.utils import get_column_letter as L

def monta(wb, CAT, DEC):
    ws = wb.create_sheet("DADOS")
    ws.sheet_state = "hidden"
    ref = {}          # onde cada lista ficou, para os menus suspensos

    def col(c, titulo, itens, larg=22):
        ws.column_dimensions[L(c)].width = larg
        escreve(ws, c, 3, titulo, nome=TITULO, pt=PT_ROTULO, cor=TEXTO_FRACO)
        for i, v in enumerate(itens):
            escreve(ws, c, 4 + i, v, alinha=ESQ)
        if itens:
            ref[titulo] = f"DADOS!${L(c)}$4:${L(c)}${3+len(itens)}"
        return c + 1

    # --- o carimbo, decisao A1 + C2 --------------------------------------
    escreve(ws, 1, 1, "VERSÃO DO CATÁLOGO", nome=TITULO, pt=PT_ROTULO, cor=TEXTO_FRACO, alinha=ESQ)
    escreve(ws, 2, 1, CAT["_meta"]["versao"], negrito=True, alinha=ESQ)
    escreve(ws, 3, 1, "versão corrente (puxada da central)", pt=PT_ROTULO, cor=TEXTO_FRACO, alinha=ESQ)
    # a celula viva: uma so, e se ela falhar a ficha continua inteira
    escreve(ws, 4, 1, CAT["_meta"]["versao"], negrito=True, alinha=ESQ)
    escreve(ws, 1, 2, "cole aqui o IMPORTRANGE da central em D1 quando ela existir; "
                      "enquanto não existir, D1 fica igual a B1 e o aviso some",
            pt=PT_ROTULO, cor=TEXTO_FRACO, alinha=ESQ)
    ref["carimbo_local"], ref["carimbo_central"] = "DADOS!$B$1", "DADOS!$D$1"

    # --- a desambiguacao do B5 -------------------------------------------
    # `Lento` nomeia duas coisas: condicao de nivel Leve (deslocamento pela
    # metade, sem Acao Bonus) e Restricao Media (custa a rodada inteira). Na
    # ficha o jogador veria a mesma palavra em dois menus.
    #
    # A colisao e DERIVADA das duas listas, e nao escrita aqui: se outra
    # aparecer um dia, ela ganha rotulo sozinha. O catalogo continua com os
    # nomes crus -- quem ganha o rotulo e o MENU.
    COLIDEM = set(CAT["condicoes"]) & set(CAT["restricoes"])

    def rotula(nome, tipo):
        return f"{nome} ({tipo})" if nome in COLIDEM else nome

    # --- as listas -------------------------------------------------------
    c = 1
    # C1: o Evocador sai do MENU. O catalogo continua com os cinco.
    c = col(c, "Caminhos", DEC["C1_evocador"]["caminhos_no_menu"])
    c = col(c, "Perícias", list(CAT["pericias"]))
    c = col(c, "Ofícios", CAT["oficios"])
    c = col(c, "Famílias", list(CAT["familias"]))
    c = col(c, "Formas", list(CAT["formas"]))
    c = col(c, "Melhorias", list(CAT["melhorias"]), 26)
    c = col(c, "Restrições", [rotula(x, "restrição") for x in CAT["restricoes"]])
    c = col(c, "Condições", [rotula(x, "condição") for x in CAT["condicoes"]])
    c = col(c, "Origens", list(CAT["origens"]))
    c = col(c, "Testes", [t for t in CAT["testes_de_resistencia"]
                          if isinstance(CAT["testes_de_resistencia"][t], dict)])
    c = col(c, "Atributos", list(CAT["atributos"]))
    c = col(c, "Trilhas", list(CAT["trilhas"]))

    # --- tabela dos Caminhos, para o PROCV ------------------------------
    base = c + 1
    escreve(ws, base, 3, "tabela dos Caminhos", nome=TITULO, pt=PT_ROTULO, cor=TEXTO_FRACO)
    cabec = ["Caminho", "dado", "vida inicial", "vida por nível", "PE por nível",
             "perícia fixa 1", "perícia fixa 2", "ofício fixo"]
    for j, h in enumerate(cabec):
        ws.column_dimensions[L(base + j)].width = 15
        escreve(ws, base + j, 4, h, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for i, (nome, d) in enumerate(CAT["caminhos"].items()):
        fx = d["pericias_fixas"] + ["", ""]
        for j, v in enumerate([nome, d["dado"], d["vida_inicial"], d["vida_por_nivel"],
                               d["pe_por_nivel"], fx[0], fx[1], d.get("oficio_fixo", "")]):
            escreve(ws, base + j, 5 + i, v, alinha=ESQ)
    n = len(CAT["caminhos"])
    ref["tabela_caminhos"] = f"DADOS!${L(base)}$5:${L(base+7)}${4+n}"

    # --- as colunas de marco, para os CONT.SE da progressao -------------
    P = CAT["progressao"]
    mc = base + 9
    for j, (titulo, valores) in enumerate([
            ("marcos", P["marcos"]),
            ("maestria", [10, 18, 26]),
            ("classe", [1, 5, 9, 13, 17, 21, 26]),
            ("classe 0", [5, 11, 17])]):
        cc = mc + j
        ws.column_dimensions[L(cc)].width = 10
        escreve(ws, cc, 4, titulo, pt=PT_ROTULO, cor=TEXTO_FRACO)
        for i, v in enumerate(valores):
            escreve(ws, cc, 5 + i, v)
        ref["m_" + titulo.replace(" ", "")] = f"DADOS!${L(cc)}$5:${L(cc)}${4+len(valores)}"

    # --- a tabela das pericias, para o PROCV do atributo ----------------
    pc = mc + 5
    escreve(ws, pc, 4, "perícia", pt=PT_ROTULO, cor=TEXTO_FRACO)
    escreve(ws, pc + 1, 4, "atributo", pt=PT_ROTULO, cor=TEXTO_FRACO)
    ws.column_dimensions[L(pc)].width = 22
    ws.column_dimensions[L(pc + 1)].width = 16
    for i, (nome, d) in enumerate(CAT["pericias"].items()):
        escreve(ws, pc, 5 + i, nome, alinha=ESQ)
        escreve(ws, pc + 1, 5 + i, d["atributo"], alinha=ESQ)
    ref["tabela_pericias"] = f"DADOS!${L(pc)}$5:${L(pc+1)}${4+len(CAT['pericias'])}"

    pinta(ws, 1, 1, pc + 2, 5 + len(CAT["melhorias"]) + 2, FUNDO)
    for r in range(1, 6 + len(CAT["melhorias"])):
        ws.row_dimensions[r].height = ALT_LIN
    return ref


def indice(wb, R):
    """publica onde cada campo da FICHA ficou, na DADOS, coluna BA em diante."""
    ws = wb["DADOS"]
    c = 53
    ws.column_dimensions[L(c)].width = 22
    ws.column_dimensions[L(c + 1)].width = 14
    escreve(ws, c, 4, "campo", pt=PT_ROTULO, cor=TEXTO_FRACO)
    escreve(ws, c + 1, 4, "célula", pt=PT_ROTULO, cor=TEXTO_FRACO)
    i = 0
    for chave, v in R.items():
        if hasattr(v, "coordinate"):
            coord = v.coordinate
        elif isinstance(v, str) and v.startswith("$"):
            coord = v.replace("$", "")
        else:
            continue
        escreve(ws, c, 5 + i, chave, alinha=ESQ)
        escreve(ws, c + 1, 5 + i, coord, alinha=ESQ)
        i += 1
    return i
