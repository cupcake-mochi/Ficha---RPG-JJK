# -*- coding: utf-8 -*-
"""A CARTEIRA: a primeira aba, e o documento da pessoa.

Ela nao calcula quase nada de proposito. O trabalho dela e ser um objeto do
mundo -- foto, nome, numero de registro, selo carimbado -- e e a unica pagina
da ficha que existe por causa da ficcao e nao da regra.

O numero de registro sai do proprio personagem, entao ele muda quando o
personagem muda, e nao e mais um campo para o jogador esquecer de preencher.
"""
from estilo import *
from openpyxl.utils import get_column_letter as L

COLS, LINHAS = 46, 44

def monta(wb, CAT, DEC, ref, R):
    ws = base(wb, "CARTEIRA", COLS, LINHAS)
    F = "FICHA!"
    def da_ficha(chave):
        return F + R[chave].replace("$", "") if isinstance(R[chave], str) \
               else F + R[chave].coordinate

    pinta(ws, 1, 1, COLS, LINHAS, TINTA)
    arte(ws, "textura.png", 1, 1, 1300)

    # ------------------------------------------------------------- cabeçalho
    pinta(ws, 1, 1, COLS, 4, PAPEL)
    txt(ws, 3, 2, "呪術廻戦", nome=MARCA, pt=KANJI_PISO, cor=BLOCO, ate=(10, 3))
    txt(ws, 12, 2, "GUILDA DE FEITICEIROS", nome=TITULO, pt=13, cor=OSSO, ate=(30, 2))
    txt(ws, 12, 3, "carteira de registro · documento oficial",
        nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(30, 3))
    # o numero de registro se monta do personagem: versao, Caminho e nivel
    txt(ws, 34, 2,
        f'="Nº M-"&TEXT({ref["carimbo_local"]}*1000,"0000")&"-"&'
        f'IF({da_ficha("nome")}="","0000",UPPER(LEFT({da_ficha("nome")},4)))',
        nome=SERIE, pt=11, cor=BLOCO, al="right", ate=(COLS, 2))
    txt(ws, 34, 3, '="emitida "&TEXT(TODAY(),"dd.mm.aaaa")',
        nome=SERIE, pt=9, cor=TEXTO_FRACO, al="right", ate=(COLS, 3))
    arte(ws, "pincelada-roxa.png", 1, 5, 1240, 14)

    # ------------------------------------------------------------------ foto
    arte(ws, "moldura-foto.png", 4, 8, 205)
    txt(ws, 4, 22, "cole a foto por cima desta moldura", nome=CORPO, pt=8,
        cor=LINHA, ate=(13, 22))

    # ------------------------------------------------------------ o portador
    txt(ws, 15, 8, "PORTADOR", nome=TITULO, pt=9, cor=TEXTO_FRACO, ate=(25, 8))
    ws.merge_cells(start_row=9, start_column=15, end_row=12, end_column=34)
    nome = txt(ws, 15, 9, None, nome=DOCUMENTO, pt=30, cor=OSSO)
    txt(ws, 15, 13, None, nome=DOCUMENTO, pt=12, cor=TEXTO_FRACO, ate=(25, 13))
    arte(ws, "pincelada.png", 15, 15, 560, 11)

    campos = [("caminho", da_ficha("caminho")), ("trilha", da_ficha("trilha")),
              ("origem", da_ficha("origem")),   ("nível",  da_ficha("nivel")),
              ("mesa de origem", None),         ("registrado por", None)]
    for i, (rot, alvo) in enumerate(campos):
        c1 = 15 + (i % 3) * 11
        rr = 17 + (i // 3) * 4
        valor = f'=IF({alvo}="","—",{alvo})' if alvo else None
        campo(ws, c1, rr, 9, rot, valor, pt=14)

    # ------------------------------------------------------------- o carimbo
    arte(ws, "selo-封.png", 38, 25, 115)
    txt(ws, 37, 33, "SELO REGISTRADO", nome=TITULO, pt=8, cor=TEXTO_FRACO,
        al="right", ate=(COLS, 33))

    # -------------------------------------------------------- a técnica dele
    txt(ws, 4, 26, "TÉCNICA DECLARADA", nome=TITULO, pt=9, cor=TEXTO_FRACO, ate=(20, 26))
    txt(ws, 4, 27, None, nome=DOCUMENTO, pt=17, cor=OSSO, ate=(24, 28))
    regua(ws, 4, 29, 24, LINHA)
    txt(ws, 4, 30, None, nome=CORPO, pt=10, cor=TEXTO_FRACO, ate=(30, 31))
    txt(ws, 4, 32, "uma linha sobre o que a técnica é. o resto está na aba TÉCNICA.",
        nome=CORPO, pt=8, cor=LINHA, ate=(30, 32))
    arte(ws, "respingo.png", 31, 26, 100)

    # ------------------------------------------------------------- o rodapé
    regua(ws, 3, 37, COLS, LINHA)
    txt(ws, 3, 38, "esta carteira acompanha o portador entre mesas. "
                   "a ficha completa está nas páginas seguintes.",
        nome=CORPO, pt=9, cor=TEXTO_FRACO, ate=(30, 38))
    txt(ws, 34, 38,
        f'=IF({da_ficha("caminho")}="","—",'
        f'UPPER(LEFT({da_ficha("caminho")},3))&"-"&TEXT({da_ficha("nivel")},"00"))',
        nome=SERIE, pt=9, cor=LINHA, al="right", ate=(COLS, 38))
    return {"nome": nome}
