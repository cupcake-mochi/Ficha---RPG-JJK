# -*- coding: utf-8 -*-
"""Mede a largura de cada letra da Roboto 10 e grava em ficha-v01/larguras-roboto-10.json.

    python3 ficha-v01/medir_fonte.py CAMINHO/Roboto.ttf

Por que existe: desde 05/10/2026 as cartas de Habilidades da seção 7 da FICHA são uma coluna só, e a caixa do texto
estica conforme o texto do Caminho e da Trilha escolhidos ("Acompanha a Escolha, mas ainda tendo a caixa retratil da
descrição"). Quem estica é o Codigo.gs, que precisa saber quantas linhas o texto ocupa, e o Apps Script não mede fonte.
Esta tabela vai no Habilidades.gs, e o script e o gerador contam as linhas com ela, do mesmo jeito.

A fonte não mora no repositório: a Roboto é a variável do google/fonts (ofl/roboto/Roboto[wdth,wght].ttf), na instância
padrão (peso 400). Rodar de novo só faz falta se a fonte da caixa mudar. Mede cada letra que aparece no texto do livro
(habilidades-do-livro.json) e as do teclado; letra que não está na tabela usa a média.
"""
import json, os, string, sys
from PIL import ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "larguras-roboto-10.json")
PT = 10.0
PX = PT * 96 / 72                         # 10 pt na tela: 13,33 px


def letras():
    hab = json.load(open(os.path.join(AQUI, "habilidades-do-livro.json"), encoding="utf-8"))
    txt = "".join(h["nome"] + h["texto"] for g in ("caminhos", "trilhas", "no_caminho")
                  for por in hab[g].values() for h in por.values())
    extra = string.ascii_letters + string.digits + string.punctuation + " áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ—–·×÷−→«»“”‘’…ºª°"
    return sorted(set(txt + extra) - {"\n"})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python3 ficha-v01/medir_fonte.py CAMINHO/Roboto.ttf")
    F = ImageFont.truetype(sys.argv[1], PX)
    lg = {ch: round(F.getlength(ch), 3) for ch in letras()}
    media = round(sum(lg.values()) / len(lg), 3)
    json.dump({"fonte": "Roboto", "pt": PT, "px": round(PX, 3), "de_onde": "google/fonts ofl/roboto/Roboto[wdth,wght].ttf, peso 400",
               "media": media, "larguras": lg}, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{SAIDA}: {len(lg)} letras, média {media} px")
