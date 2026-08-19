# -*- coding: utf-8 -*-
"""Gera a arte da ficha. Nada baixado de lugar nenhum: tudo desenhado aqui,
com PIL, para nao entrar arte de terceiro num material que vai circular.

Sao cinco pecas, e cada uma tem um trabalho:
  selo        o carimbo vermelho, com kanji de verdade em fonte de pincel
  pincelada   o risco de tinta que separa secao
  respingo    a sujeira que tira a cara de vetor limpo
  moldura     o lugar da foto na carteirinha
  textura     o ruido de papel, quase invisivel, que mata o chapado
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

random.seed(4)                      # o mesmo desenho toda vez que rodar
AQUI   = os.path.dirname(os.path.abspath(__file__))
FONTES = "/tmp/claude-1000/-media-mizuki-HD-Externo-II-Claude-Ficha/1ff06321-19ca-4c78-a1e7-69f0754d387b/scratchpad/fontes"
VERMELHO = (194, 51, 77)
OSSO     = (232, 220, 212)
BLOCO    = (117, 101, 136)

def desgasta(img, forca=0.35, escala=3):
    """come as bordas com ruido: e o que faz o carimbo parecer carimbado"""
    w, h = img.size
    ruido = Image.new("L", (w // escala, h // escala))
    ruido.putdata([random.randint(0, 255) for _ in range(ruido.width * ruido.height)])
    ruido = ruido.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    a = img.getchannel("A")
    nova = Image.new("L", (w, h))
    nova.putdata([0 if (n < 255 * forca) else v
                  for v, n in zip(a.getdata(), ruido.getdata())])
    img.putalpha(nova)
    return img

def selo(texto="封", lado=420):
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m, esp = 18, 16
    d.rounded_rectangle([m, m, lado - m, lado - m], radius=10,
                        outline=VERMELHO + (255,), width=esp)
    f = ImageFont.truetype(os.path.join(FONTES, "YujiSyuku.ttf"), int(lado * 0.52))
    d.text((lado // 2, lado // 2 + 6), texto, font=f, fill=VERMELHO + (255,), anchor="mm")
    return desgasta(img, 0.30)

def pincelada(larg=1600, alt=120, cor=OSSO):
    """Um risco de pincel.

    A v1 sorteava falha coluna a coluna e saiu com cara de codigo de barras:
    listra vertical no lugar de pincel seco. Aqui o corpo do traco e continuo
    e as falhas sao manchas ALONGADAS na horizontal, que e como pincel seco
    falha de verdade -- ele arrasta, nao pisca.
    """
    img = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    meio = alt / 2
    # corpo continuo, com as duas bordas tremendo em frequencias diferentes
    cima, baixo = [], []
    for x in range(larg):
        t = x / larg
        grossura = (alt * 0.40) * (1 - t) ** 0.5
        desvio = math.sin(t * 2.6) * alt * 0.07 + math.sin(t * 9.1) * alt * 0.015
        cima.append((x, meio + desvio - grossura / 2 + math.sin(t * 27) * alt * 0.02))
        baixo.append((x, meio + desvio + grossura / 2 + math.sin(t * 19 + 1) * alt * 0.02))
    d.polygon(cima + baixo[::-1], fill=cor + (255,))
    # o pincel seca: manchas horizontais, mais frequentes e maiores no fim
    vazio = Image.new("L", (larg, alt), 255)
    dv = ImageDraw.Draw(vazio)
    for _ in range(230):
        t = random.random() ** 0.45          # concentra no fim do traco
        x = t * larg
        comp = random.uniform(8, 90) * (0.3 + t)
        esp = random.uniform(0.8, 3.0)
        y = meio + math.sin(t * 2.6) * alt * 0.07 + random.uniform(-alt * 0.17, alt * 0.17)
        dv.line([(x, y), (x + comp, y + random.uniform(-1.5, 1.5))],
                fill=0, width=max(1, int(esp)))
    a = img.getchannel("A")
    img.putalpha(Image.composite(a, Image.new("L", (larg, alt), 0), vazio))
    return img.filter(ImageFilter.GaussianBlur(0.5))


def respingo(lado=300, cor=VERMELHO, n=26):
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        ang = random.uniform(0, math.tau)
        dist = random.uniform(0, lado * 0.45) ** 1.3 / lado ** 0.3
        x = lado / 2 + math.cos(ang) * dist * 3
        y = lado / 2 + math.sin(ang) * dist * 3
        r = random.uniform(1.5, 9) * (1 - dist / lado * 2)
        if r > 0.6:
            d.ellipse([x - r, y - r, x + r, y + r], fill=cor + (255,))
    return img.filter(ImageFilter.GaussianBlur(0.4))

def moldura(larg=360, alt=460):
    """o lugar da foto: canto chanfrado, que e o que o desenho pediu e a
    planilha nao faz sozinha"""
    img = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ch = 34
    pts = [(0, ch), (ch, 0), (larg, 0), (larg, alt - ch), (larg - ch, alt), (0, alt)]
    d.polygon(pts, fill=(18, 15, 29, 235), outline=BLOCO + (255,))
    d.line(pts + [pts[0]], fill=BLOCO + (255,), width=3)
    f = ImageFont.truetype(os.path.join(FONTES, "Oswald.ttf"), 20)
    d.text((larg // 2, alt // 2 - 10), "FOTO", font=f, fill=BLOCO + (170,), anchor="mm")
    fj = ImageFont.truetype(os.path.join(FONTES, "YujiSyuku.ttf"), 30)
    d.text((larg // 2, alt // 2 + 26), "顔", font=fj, fill=BLOCO + (110,), anchor="mm")
    return img

def textura(larg=1400, alt=900):
    """ruido de papel: quase invisivel, e e ele que tira o chapado do fundo"""
    img = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    px = img.load()
    for y in range(alt):
        for x in range(larg):
            if random.random() < 0.10:
                v = random.randint(0, 16)
                px[x, y] = (255, 255, 255, v)
    return img.filter(ImageFilter.GaussianBlur(0.3))

def base64_das_pecas():
    """imprime o base64 de cada peca, para colar no ARTE do Codigo.gs (C5)"""
    import base64, io
    for nome, img in PECAS().items():
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        b = base64.b64encode(buf.getvalue()).decode()
        print(f"  '{nome.replace('.png','')}': '{b}',")


def PECAS():
    return {
        "selo-封.png":      selo("封"),
        "selo-呪.png":      selo("呪"),
        "pincelada.png":    pincelada(),
        "pincelada-roxa.png": pincelada(1600, 120, BLOCO),
        "respingo.png":     respingo(),
        "moldura-foto.png": moldura(),
        "textura.png":      textura(),
    }


if __name__ == "__main__":
    import sys
    if "--base64" in sys.argv:
        base64_das_pecas(); raise SystemExit
    pecas = PECAS()
    for nome, img in pecas.items():
        img.save(os.path.join(AQUI, nome))
        print(f"  {nome:22} {img.size[0]}x{img.size[1]}")
    print(f"\n{len(pecas)} peças, todas desenhadas por código. Regera igual: seed fixa.")
