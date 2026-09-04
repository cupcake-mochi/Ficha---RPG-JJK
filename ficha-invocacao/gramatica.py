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
