# -*- coding: utf-8 -*-
"""A gramatica visual da ficha do Projeto M, lida da Ficha (PROJETO M) 0.1.

Ela nao foi inventada aqui: cada medida saiu do arquivo que o Mizuki editou no
Sheets. A ficha da invocacao usava outra gramatica -- a `regua`, um fio embaixo
do valor -- e a ficha de player evoluiu para OUTRA COISA, de tres faixas:

    rotulo    Oswald 8   sobre PAINEL_ALTO   (a faixa clara de cima)
    VALOR     Oswald 16  sobre PAINEL        (o poco escuro)
    legenda   Roboto 8   sobre PAINEL_ALTO   (a faixa clara de baixo, opcional)

E o cabecalho de secao e dois pedacos na mesma linha:

    numero    Oswald 22  sobre FAIXA         D:F, duas linhas de altura
    titulo    Oswald 12  sobre PAINEL_ALTO   G em diante

As medidas, lidas da FICHA de player:
  · campo de atributo: 7 colunas, vao de 1  ->  D:J  L:R  T:Z  AB:AH  AJ:AP
  · campo de registro: 10 colunas, vao de 1 ->  D:M  O:X  Z:AI  AK:AT
  · valor grande (vida, energia, integridade): Oswald 22, duas linhas
  · valor de atributo: Oswald 24, duas linhas
  · linha de lista (pericia): caixa D · nome E:L Castoro 10 · atributo M:N
    Oswald 8 · valor O:P Oswald 10, tudo sobre PAINEL
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "ficha"))
from estilo import (CORPO, TITULO, DOCUMENTO, SERIE, FUNDO, PAINEL, PAINEL_ALTO,
                    FAIXA, PAINEL_BAIXO, LINHA, TINTA, TEXTO, TEXTO_FRACO, OSSO,
                    AMBAR, txt, pinta, junta, regua)

COLS = 46

# as grades de campo, lidas da ficha de player
GRADE_7  = [4, 12, 20, 28, 36]        # D L T AB AJ, sete colunas cada
GRADE_10 = [4, 15, 26, 37]            # D O Z AK, dez colunas cada
LARG_7, LARG_10 = 6, 9                # quantas colunas o merge cobre a mais

PT_ROT, PT_VAL, PT_GRANDE, PT_ATR = 8, 16, 22, 24
PT_TIT_SEC, PT_NUM_SEC = 12, 22
PT_LEG, PT_NOTA = 8, 9


def secao(ws, r, numero, titulo, ate=24):
    """o cabecalho: numero grande na FAIXA, titulo no PAINEL_ALTO."""
    pinta(ws, 4, r, 6, r + 1, FAIXA)
    txt(ws, 4, r, numero, nome=TITULO, pt=PT_NUM_SEC, cor=OSSO, al="center",
        ate=(6, r + 1))
    pinta(ws, 7, r, ate, r, PAINEL_ALTO)
    txt(ws, 7, r, titulo, nome=TITULO, pt=PT_TIT_SEC, cor=OSSO, ate=(ate, r))
    return r + 2


def campo(ws, c, r, larg, rotulo, valor, pt=PT_VAL, cor=OSSO, nome=TITULO,
          legenda=None, alto=1):
    """rotulo na faixa clara, valor no poco escuro, legenda opcional embaixo.

    Devolve a celula do VALOR, que e onde o jogador digita ou a formula mora.
    """
    c2 = c + larg
    pinta(ws, c, r, c2, r, PAINEL_ALTO)
    txt(ws, c, r, rotulo.upper(), nome=TITULO, pt=PT_ROT, cor=OSSO, al="center",
        ate=(c2, r))
    pinta(ws, c, r + 1, c2, r + alto, PAINEL)
    cel = txt(ws, c, r + 1, valor, nome=nome, pt=pt, cor=cor, al="center",
              ate=(c2, r + alto))
    if legenda is not None:
        pinta(ws, c, r + alto + 1, c2, r + alto + 1, PAINEL_ALTO)
        txt(ws, c, r + alto + 1, legenda, nome=CORPO, pt=PT_LEG, cor=OSSO,
            al="center", ate=(c2, r + alto + 1))
    return cel


def linha_lista(ws, c, r, larg_nome, nome_item, valor, atributo=None,
                pt_valor=10, zebra=False):
    """a linha de lista da ficha de player: nome em Castoro, valor em Oswald."""
    c2 = c + larg_nome
    pinta(ws, c, r, c2 + (4 if atributo else 2), r,
          PAINEL_ALTO if zebra else PAINEL)
    txt(ws, c, r, nome_item, nome=DOCUMENTO, pt=10, cor=OSSO, ate=(c2, r))
    cc = c2 + 1
    if atributo is not None:
        txt(ws, cc, r, atributo, nome=TITULO, pt=PT_ROT, cor=TEXTO_FRACO,
            al="center", ate=(cc + 1, r))
        cc += 2
    return txt(ws, cc, r, valor, nome=TITULO, pt=pt_valor, cor=OSSO,
               al="right", ate=(cc + 2, r))


# a linha de Teste de Resistencia, na forma que a ficha de player ganhou na
# atualizacao de 04/09: caixa/nome/Extra/atributo/valor, com o Extra entrando
# na conta. As larguras sao as dela -- nome 7 colunas, Extra 1, atributo 5,
# valor 5 -- lidas de AC74:AI74, AJ74, AK74:AO74 e AP74:AT74.
LARG_TR_NOME, LARG_TR_ATR, LARG_TR_VAL = 6, 4, 4

def linha_tr(ws, c, r, nome_tr, atributo, formula_valor, zebra=False):
    """Devolve (celula do Extra, celula do valor)."""
    fundo = PAINEL_ALTO if zebra else PAINEL
    c_nome = c
    c_extra = c_nome + LARG_TR_NOME + 1
    c_atr = c_extra + 1
    c_val = c_atr + LARG_TR_ATR + 1
    pinta(ws, c, r, c_val + LARG_TR_VAL, r, fundo)
    txt(ws, c_nome, r, nome_tr, nome=DOCUMENTO, pt=10, cor=OSSO,
        ate=(c_nome + LARG_TR_NOME, r))
    extra = txt(ws, c_extra, r, None, nome=TITULO, pt=10, cor=OSSO, al="center")
    txt(ws, c_atr, r, atributo, nome=TITULO, pt=PT_ROT, cor=TEXTO_FRACO,
        al="center", ate=(c_atr + LARG_TR_ATR, r))
    val = txt(ws, c_val, r, formula_valor, nome=TITULO, pt=10, cor=OSSO,
              al="right", ate=(c_val + LARG_TR_VAL, r))
    return extra, val


def cabecalho_tr(ws, c, r, ate):
    """a faixa de rotulo em cima das linhas de TR, com o Extra nomeado."""
    pinta(ws, c, r, ate, r, PAINEL_ALTO)
    txt(ws, c, r, "TESTE", nome=TITULO, pt=PT_ROT, cor=OSSO,
        ate=(c + LARG_TR_NOME, r))
    txt(ws, c + LARG_TR_NOME + 1, r, "Extra", nome=DOCUMENTO, pt=6, cor=OSSO,
        al="center")
    txt(ws, c + LARG_TR_NOME + 2, r, "USA", nome=TITULO, pt=PT_ROT, cor=OSSO,
        al="center", ate=(c + LARG_TR_NOME + 2 + LARG_TR_ATR, r))
    txt(ws, c + LARG_TR_NOME + LARG_TR_ATR + 4, r, "d20 +", nome=TITULO,
        pt=PT_ROT, cor=OSSO, al="right", ate=(ate, r))


def nota(ws, r, texto, ate=COLS, cor=TEXTO_FRACO):
    txt(ws, 4, r, texto, nome=CORPO, pt=PT_NOTA, cor=cor, ate=(ate, r + 1))
    return r + 2


def aviso(ws, r, titulo, texto, ate=COLS):
    """o bloco de pendencia: faixa ambar, do jeito que a ficha marca o que
    ela nao calcula."""
    pinta(ws, 4, r, ate, r, PAINEL_ALTO)
    txt(ws, 4, r, titulo.upper(), nome=TITULO, pt=PT_ROT, cor=AMBAR, ate=(ate, r))
    pinta(ws, 4, r + 1, ate, r + 2, PAINEL)
    txt(ws, 4, r + 1, texto, nome=CORPO, pt=PT_NOTA, cor=TEXTO, ate=(ate, r + 2))
    return r + 3
