# -*- coding: utf-8 -*-
"""MESA (celular, 12 colunas), TECNICA (montagem de feitico) e QUEM E (ficcao).
A MESA nao guarda numero nenhum: ela le tudo da FICHA por formula."""
from estilo import *
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

def _base(wb, nome, cols):
    ws = wb.create_sheet(nome)
    ws.sheet_view.showGridLines = False
    for c in range(1, cols + 1):
        ws.column_dimensions[L(c)].width = LARG_COL
    for r in range(1, 90):
        ws.row_dimensions[r].height = ALT_LIN
    pinta(ws, 1, 1, cols, 90, FUNDO)
    return ws

# ====================================================================== MESA
def mesa(wb, CAT, DEC, R):
    """12 colunas = 336 px. Decisao C4: aqui SO a fonte de corpo, porque o app
    de celular troca qualquer fonte que ele nao tenha."""
    C = 12
    ws = _base(wb, "MESA", C)

    def rot_mesa(ws_, c1, r_, c2, txt):
        return rotulo(ws_, c1, r_, c2, txt, nome=CORPO)

    F = "FICHA!"
    r = 1
    pinta(ws, 1, 1, C, 2, PAINEL_ALTO)
    junta(ws, 1, 1, C, 2)
    escreve(ws, 1, 1, f"={F}{R['nome'].coordinate}", pt=14, cor=OSSO, alinha=ESQ)
    r = 4

    def linha(rot, formula, cor=OSSO, pt=14):
        nonlocal r
        pinta(ws, 1, r, C, r + 2, PAINEL)
        rot_mesa(ws, 1, r, 5, rot)
        junta(ws, 1, r + 1, 5, r + 2)
        escreve(ws, 1, r + 1, formula, pt=pt, cor=cor)
        return r

    # as duas reservas que se olha toda rodada, lado a lado
    for i, nome_r in enumerate(["vida", "energia"]):
        c1 = 1 + i * 6
        pinta(ws, c1, r, c1 + 4, r + 4, PAINEL)
        rot_mesa(ws, c1, r, c1 + 4, nome_r)
        junta(ws, c1, r + 1, c1 + 4, r + 3)
        escreve(ws, c1, r + 1, f"={F}{R[nome_r][1:].replace('$','')}", pt=PT_GRANDE, cor=OSSO)
        junta(ws, c1, r + 4, c1 + 4, r + 4)
        escreve(ws, c1, r + 4, f'="de "&{F}{R[nome_r+"_max"][1:].replace("$","")}',
                pt=PT_ROTULO, cor=TEXTO_FRACO)
    r += 6

    # o resto do que muda na sessao
    campos = ["defesa", "iniciativa", "corpo a corpo", "à distância",
              "conjuração", "cd de feitiço", "deslocamento", "maestria"]
    for i, k in enumerate(campos):
        c1 = 1 + (i % 2) * 6
        rr = r + (i // 2) * 3
        pinta(ws, c1, rr, c1 + 4, rr + 2, PAINEL if (i // 2) % 2 == 0 else PAINEL_ALTO)
        rot_mesa(ws, c1, rr, c1 + 4, k)
        junta(ws, c1, rr + 1, c1 + 4, rr + 2)
        escreve(ws, c1, rr + 1, f"={F}{R[k][1:].replace('$','')}", pt=14, cor=OSSO)
    r += 3 * ((len(campos) + 1) // 2) + 1

    # o estagio de alma, que e a automacao que mais vale na mesa
    pinta(ws, 1, r, C, r + 1, PAINEL_ALTO)
    rot_mesa(ws, 1, r, C, "estado da alma")
    junta(ws, 1, r + 1, C, r + 1)
    escreve(ws, 1, r + 1, f"={F}{R['estagio_alma'].replace(chr(36),'')}",
            pt=PT_ROTULO, cor=TEXTO_FRACO, alinha=ESQ)
    r += 3

    # a linha de uso rapido dos feiticos: puxa da TECNICA, decisao ja fechada
    escreve(ws, 1, r, "FEITIÇOS", nome=CORPO, pt=PT_TITULO, cor=BLOCO, alinha=ESQ)
    r += 1
    cabec = [("nome", 4), ("cl", 1), ("dano", 2), ("pe", 1), ("alcance", 2), ("resolve", 2)]
    cc = 1
    for h, w in cabec:
        junta(ws, cc, r, cc + w - 1, r)
        escreve(ws, cc, r, h.upper(), pt=PT_ROTULO, cor=TEXTO_FRACO)
        cc += w
    # linhas em branco, para o jogador escrever a mao. A TECNICA saiu da ficha
    # e com ela o calculo do feitico; quando ela voltar, estas linhas puxam de
    # la de novo em vez de serem digitadas.
    for i in range(6):
        rr = r + 1 + i
        pinta(ws, 1, rr, C, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
        cc = 1
        for h, w in cabec:
            junta(ws, cc, rr, cc + w - 1, rr)
            escreve(ws, cc, rr, None, pt=PT_ROTULO, cor=TEXTO,
                    alinha=ESQ if h == "nome" else CENTRO)
            cc += w
    return ws

# =================================================================== TECNICA
def tecnica(wb, CAT, DEC, ref):
    C = 46
    ws = _base(wb, "TÉCNICA", C)
    def dv(formula, c1, r1, c2, r2):
        v = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
        ws.add_data_validation(v); v.add(f"{L(c1)}{r1}:{L(c2)}{r2}")

    pinta(ws, 1, 1, C, 2, PAINEL_ALTO)
    junta(ws, 1, 1, C, 2)
    escreve(ws, 1, 1, "TÉCNICA · o Fundamento e os feitiços", nome=TITULO, pt=16, cor=OSSO, alinha=ESQ)

    r = 4
    escreve(ws, 1, r, "FAMÍLIAS · 2 Livres, 3 Fechadas", nome=TITULO, pt=PT_TITULO, cor=BLOCO, alinha=ESQ)
    r += 1
    for i in range(5):
        c1 = 1 + i * 9
        rot = "livre" if i < 2 else "fechada"
        pinta(ws, c1, r, c1 + 7, r + 2, PAINEL)
        rotulo(ws, c1, r, c1 + 7, rot)
        junta(ws, c1, r + 1, c1 + 7, r + 2)
        escreve(ws, c1, r + 1, None, pt=PT_VALOR, cor=OSSO)
        dv(ref["Famílias"], c1, r + 1, c1 + 7, r + 1)
    r += 4

    escreve(ws, 1, r, "FEITIÇOS · seis dos nove campos a ficha calcula sozinha",
            nome=TITULO, pt=PT_TITULO, cor=BLOCO, alinha=ESQ)
    r += 1
    LIN = ["nome", "forma", "classe", "melhoria 1", "melhoria 2", "restrição 1",
           "restrição 2", "ação", "alcance", "alvo", "dano", "pe"]
    for b in range(6):                       # seis blocos de feitico
        topo = 6 + b * 12                    # a MESA aponta para B{topo}
        while topo < r:
            topo += 12
        pinta(ws, 1, topo, 22, topo + 11, PAINEL if b % 2 == 0 else PAINEL_ALTO)
        for j, campo in enumerate(LIN):
            rr = topo + j
            rotulo(ws, 1, rr, 1, "")
            junta(ws, 1, rr, 1, rr)
            junta(ws, 2, rr, 8, rr)
            escreve(ws, 2, rr, None, pt=PT_ROTULO, cor=OSSO, alinha=ESQ)
            junta(ws, 9, rr, 22, rr)
            escreve(ws, 9, rr, campo, pt=PT_ROTULO, cor=TEXTO_FRACO, alinha=ESQ)
        dv(ref["Formas"],     2, topo + 1, 8, topo + 1)
        dv(ref["Melhorias"],  2, topo + 3, 8, topo + 4)
        dv(ref["Restrições"], 2, topo + 5, 8, topo + 6)
    return ws

# =================================================================== QUEM E
def quem_e(wb, CAT, DEC):
    C = 46
    ws = _base(wb, "QUEM É", C)
    pinta(ws, 1, 1, C, 2, PAINEL_ALTO)
    junta(ws, 1, 1, C, 2)
    escreve(ws, 1, 1, "QUEM É · a ficção", nome=TITULO, pt=16, cor=OSSO, alinha=ESQ)
    r = 4
    for titulo, altura in [("aparência", 6), ("história", 10), ("laços", 6),
                           ("o que ele quer", 4), ("o que ele esconde", 4),
                           ("notas de mesa", 8)]:
        rotulo(ws, 3, r, C, titulo)
        junta(ws, 3, r + 1, C, r + altura)
        escreve(ws, 3, r + 1, None, pt=PT_ROTULO, cor=TEXTO, alinha=ESQ_Q)
        # o preenchimento vem DEPOIS da mesclagem: mesclar apaga o estilo de
        # tudo que nao e o canto, e ai o bloco abre branco no Sheets
        pinta(ws, 3, r, C, r + altura, PAINEL)
        regua(ws, 3, r + altura + 1, C, LINHA)
        r += altura + 2
    return ws
