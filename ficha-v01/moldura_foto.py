# -*- coding: utf-8 -*-
"""A moldura da foto da CARTEIRA sai de dentro da caixa (limpeza 28, 03/10/2026).

A moldura era uma imagem DENTRO da célula da foto, e uma célula guarda uma coisa só: o jogador tinha de soltar a foto
por cima. Nas palavras do Mizuki: "tem que ser uma imagem 'solta' por cima que o jogador põe, oq não é muito bom". A
moldura solta por cima da caixa, com o miolo transparente, também não serve: "o jogador quando clicar vai acabar
clicando na imagem ao invés do fundo". Ficou a B+ do estudo: "vamos de B+ ... a parte central ser uma celula só
mesclada, que o jogador clica e insere".

  · a caixa da foto (a mesclagem onde a moldura morava) fica livre, com "FOTO / 顔" escrito, que a imagem inserida
    substitui, e a nota de como inserir. Uma célula tem uma fonte só, e a Yuji Syuku (a do 呪術廻戦 do cabeçalho) é a
    que tem as letras e o kanji; a Oswald do desenho antigo não tem o 顔;
  · a moldura vai para o anel de uma célula em volta da caixa. As retas são borda média na régua, que a troca de
    paleta já repinta (repintarBordas_). Os dois cantos chanfrados, em cima à esquerda e embaixo à direita como no
    desenho antigo, são uma imagem pequena dentro da célula do canto: o mesmo traço "/", de canto a canto da célula;
  · a CARTEIRA declara onde a caixa está (`foto`), porque a caixa da paleta se ancora nela (acharCaixaDaFoto_, no
    Codigo.gs), e até aqui a caixa era achada pela imagem da moldura.

A foto continua do mesmo tamanho. O que muda no desenho é a margem de uma célula entre a linha e a foto.
"""
import json, os
from openpyxl.utils import get_column_letter as L

import indice_ficha as ix
from correcoes_borda import _acha_ou_cria

AQUI = os.path.dirname(os.path.abspath(__file__))
ARTE_VELHA = "carteira-2.png"          # a moldura de dentro da caixa, desenhada pelo ficha_layout.desenha_arte
ARTE_CANTO = "carteira-canto.png"
TRACO = ["medium", "FF8A7EC4"]         # a régua média de toda caixa da ficha
REGUA = (0x8A, 0x7E, 0xC4)             # a régua de fábrica: o canto continua a borda, e nasce na cor dela
BLOCO = "FF756588"                     # a cor do 呪術廻戦 do cabeçalho e do "FOTO 顔" da moldura antiga
TEXTO = "FOTO\n顔"
FONTE = ["Yuji Syuku", 22.0, BLOCO, False, False]  # o piso do kanji da ficha: abaixo de 22 o traço da Yuji Syuku funde
NOTA = "Clique na caixa e use Inserir › Imagem › Inserir imagem na célula."


def _aba(layout, nome):
    return next(a for a in layout["abas"] if a["nome"] == nome)


def trocas(layout):
    aba = _aba(layout, "CARTEIRA")
    im = next((i for i in aba["imagens"] if i["arquivo"] == ARTE_VELHA), None)
    if im is None:
        raise SystemExit(f"moldura_foto: a moldura da foto ({ARTE_VELHA}) não está na CARTEIRA")
    canto = f"{L(im['col'])}{im['lin']}"
    caixa = next((m for m in aba["mescladas"] if m.split(":")[0] == canto), None)
    if caixa is None:
        raise SystemExit(f"moldura_foto: a moldura em CARTEIRA!{canto} não tem a caixa mesclada dela")
    (l1, c1), (l2, c2) = (ix._lc(x) for x in caixa.split(":"))
    a1, b1, a2, b2 = l1 - 1, c1 - 1, l2 + 1, c2 + 1           # o anel: uma célula para fora da caixa
    if a1 < 1 or b1 < 1:
        raise SystemExit(f"moldura_foto: a caixa {caixa} encosta na borda da aba, e o anel não cabe")
    cel = {r[0]: r for r in aba["celulas"]}
    lados = {}
    for c in range(c1, b2 + 1):                  # em cima, depois do canto chanfrado
        lados.setdefault((a1, c), {})["top"] = TRACO
    for r in range(a1, l2 + 1):                  # à direita, até o canto chanfrado de baixo
        lados.setdefault((r, b2), {})["right"] = TRACO
    for c in range(b1, c2 + 1):                  # embaixo, até o canto chanfrado
        lados.setdefault((a2, c), {})["bottom"] = TRACO
    for r in range(l1, a2 + 1):                  # à esquerda, depois do canto chanfrado de cima
        lados.setdefault((r, b1), {})["left"] = TRACO
    anel = set(lados) | {(a1, b1), (a2, b2)}
    for r, c in sorted(anel):
        k = f"{L(c)}{r}"
        if cel.get(k, [None, None])[1] not in (None, ""):
            raise SystemExit(f"moldura_foto: o anel da foto passaria por CARTEIRA!{k}, que tem valor")
        if any(ix._lc(m.split(":")[0])[0] <= r <= ix._lc(m.split(":")[1])[0] and
               ix._lc(m.split(":")[0])[1] <= c <= ix._lc(m.split(":")[1])[1] for m in aba["mescladas"]):
            raise SystemExit(f"moldura_foto: o anel da foto passaria por CARTEIRA!{k}, que está numa caixa mesclada")
    celulas = {}
    for (r, c), ls in sorted(lados.items()):
        k = f"{L(c)}{r}"
        base = cel.get(k, [None, None, None])[2]
        fonte, fundo, bordas, alinha, fmt = (json.loads(json.dumps(layout["estilos"][base])) if base is not None
                                             else [None, None, None, None, None])
        celulas[k] = (None, _acha_ou_cria(layout, [fonte, fundo, {**(bordas or {}), **ls}, alinha, fmt]))
    base = cel.get(canto, [None, None, None])[2]
    _, fundo, bordas, alinha, fmt = (json.loads(json.dumps(layout["estilos"][base])) if base is not None
                                     else [None, None, None, None, None])
    celulas[canto] = (TEXTO, _acha_ou_cria(layout, [FONTE, fundo, bordas, ["center", "center", True, 0], fmt]))
    # o tamanho de cada canto, no pixel do script: a largura limpa da coluna e a altura da linha (a 22 é mais alta)
    larg = round(8 * layout["_meta"]["largura_limpa"]["exportada"] - 1)
    alt = {int(r): round(p * 4 / 3) for r, p in aba["linhas_alt"]}
    cantos = [dict(arquivo=ARTE_CANTO, col=c, lin=r, larg=larg, alt=alt.get(r, 21), desloc_x=0, desloc_y=0)
              for r, c in ((a1, b1), (a2, b2))]
    return {"caixa": caixa, "foto": [l1, c1, l2, c2], "anel": [a1, b1, a2, b2], "celulas": celulas,
            "cantos": cantos, "nota": {canto: NOTA}}


def aplica(layout, tr):
    aba = _aba(layout, "CARTEIRA")
    por = {r[0]: r for r in aba["celulas"]}
    n = 0
    for k, (valor, estilo) in tr["celulas"].items():
        if k in por:
            if por[k][1] != valor or por[k][2] != estilo:
                por[k][1], por[k][2] = valor, estilo
                n += 1
        else:
            aba["celulas"].append([k, valor, estilo])
            n += 1
    antes = len(aba["imagens"])
    aba["imagens"] = [i for i in aba["imagens"] if i["arquivo"] != ARTE_VELHA] + tr["cantos"]
    n += abs(len(aba["imagens"]) - antes) + 1
    aba.setdefault("notas", {}).update(tr["nota"])
    aba["foto"] = tr["foto"]
    return n


def desenha(tr):
    """o canto chanfrado: o traço "/" de canto a canto, na régua, num quadrado que o emitir_gs estica para a célula de
    cada canto (28 x 21 em cima, 28 x 27 embaixo). A espessura sai perto dos 2 px da borda média nas duas."""
    from PIL import Image, ImageDraw
    lado, esp = 240, 17
    # o transparente também na cor da régua: o emitir_gs reduz a arte, e a redução misturava a beira do traço com o preto
    # do transparente, e o canto saía 8E81C9, um roxo mais claro que a borda na cor de fábrica
    img = Image.new("RGBA", (lado, lado), REGUA + (0,))
    d = ImageDraw.Draw(img)
    # a faixa x + y = lado ± k em volta da diagonal, mais longa que o quadrado: o recorte faz as pontas chegarem aos
    # dois cantos, e o emitir_gs suaviza a beira quando reduz
    k = esp / 2 * 2 ** 0.5
    d.polygon([(-lado, 2 * lado - k), (2 * lado, -lado - k), (2 * lado, -lado + k), (-lado, 2 * lado + k)],
              fill=REGUA + (255,))
    img.save(os.path.join(AQUI, "arte", ARTE_CANTO))
    return img
