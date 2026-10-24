#!/usr/bin/env python3
"""Três estudos de estilo para a ficha em PDF (só visual, sem campos).

A · Registro   documento oficial da escola: dossiê, carimbo, régua, código de barras
B · Talismã    ofuda e pincel: selos de atributo, ensō nos recursos, tinta
C · Expansão   painel de mangá/HUD: cantos cortados, sombra deslocada, retícula

Cada estudo tem a página 1 (personagem) e uma proposta de página 4
(repertório em cartões), preenchidos com a Kaori do livro, no Mizuki escuro.
Arte toda desenhada por código, reaproveitando arte/gera.py.

Uso: python3 ficha-pdf/estudos/estilos.py  ->  ficha-pdf/estudos/saidas/
"""
import importlib.util
import json
import math
import os
import random
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SAIDAS = os.path.join(AQUI, 'saidas')
TMP = tempfile.mkdtemp(prefix='estilos-')
W, H = A4

FONTES = os.path.join(RAIZ, 'arte/fontes')
pdfmetrics.registerFont(TTFont('Oswald', os.path.join(FONTES, 'Oswald.ttf')))
pdfmetrics.registerFont(TTFont('Yuji', os.path.join(FONTES, 'YujiSyuku.ttf')))

_spec = importlib.util.spec_from_file_location('gera', os.path.join(RAIZ, 'arte/gera.py'))
arte = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arte)

# ---------------------------------------------------------------- conteúdo (Kaori, cap. 4)
KAORI = {
    'nome': 'Kaori', 'jogador': 'Suii', 'origem': 'Descendente', 'caminho': 'Bastião',
    'trilha': 'Muro', 'nivel': '2', 'grau': '4', 'xp': '0',
    'atr': [('FOR', 'Força', 3, '力'), ('DES', 'Destreza', 2, '速'), ('CON', 'Constituição', 2, '体'),
            ('INT', 'Inteligência', 1, '知'), ('ESS', 'Essência', 1, '魂')],
    'recursos': [('VIDA', 23, 23), ('ENERGIA', 8, 8), ('INTEGRIDADE', 26, 26)],
    'combate': [('DEFESA', '13'), ('BLOQUEAR', '2d10+2'), ('INICIATIVA', '+2'), ('DESLOC.', '9 m'),
                ('CD TÉCNICA', '12'), ('ATAQUE TÉC.', '+4'), ('CORPO A CORPO', '+4'), ('DISTÂNCIA', '+3')],
    'maestria': '+1',
    'tr': [('Físico', 'FOR', '+4', True), ('Vigor', 'CON', '+3', True),
           ('Intelecto', 'INT', '+1', False), ('Espírito', 'ESS', '+1', False)],
}
PERICIAS = [('Atletismo', 'FOR', 3), ('Acrobacia', 'DES', 2), ('Furtividade', 'DES', 2),
            ('Pontaria', 'DES', 2), ('Prestidigitação', 'DES', 2), ('Investigação', 'INT', 1),
            ('Intuição', 'INT', 1), ('Ocultismo', 'INT', 1), ('Religião', 'INT', 1),
            ('História', 'INT', 1), ('Hierarquia', 'INT', 1), ('Medicina', 'INT', 1),
            ('Sobrevivência', 'INT', 1), ('Natureza', 'INT', 1), ('Lidar com Animais', 'INT', 1),
            ('Tecnologia', 'INT', 1), ('Sentir Energia', 'ESS', 1), ('Percepção', 'ESS', 1),
            ('Persuasão', 'ESS', 1), ('Enganação', 'ESS', 1), ('Intimidação', 'ESS', 1),
            ('Atuação', 'ESS', 1), ('Provocar', 'ESS', 1)]
TREINADAS = {'Atletismo', 'Provocar', 'Intuição', 'História', 'Hierarquia', 'Sobrevivência',
             'Sentir Energia', 'Percepção', 'Intimidação'}


def pericias():
    out = []
    for nome, sg, v in PERICIAS:
        t = nome in TREINADAS
        out.append((nome, sg, '%+d' % (v + (1 if t else 0)), t))
    return out


FEITICO = {
    'nome': 'Peso nas Mãos', 'classe': '1', 'pe': '3', 'acao': 'Ação Padrão',
    'alcance': 'Toque · 1,5 m', 'acerto': 'd20+4 vs Defesa', 'dano': '3d8 Concussão',
    'forma': 'Toque', 'tr': 'TR Físico CD 12',
    'melhorias': 'Condição: Derrubado (1)', 'restricoes': 'Toque · Leve (devolve 1)',
    'como': 'Cumpre o Selo e encosta as duas mãos no alvo. No acerto, 3d8 e o alvo faz TR '
            'Físico; na falha, fica Derrubado por uma rodada. No erro, PE e ação continuam gastos.',
}


# ---------------------------------------------------------------- cores e arte
def paleta(nome='Mizuki', modo='escuro'):
    d = json.load(open(os.path.join(RAIZ, 'medidas/paletas-grandes/paletas-grandes.json')))
    cores = d[nome][modo]['cores']
    k = {n: HexColor('#' + v) for n, v in cores.items()}
    k['osso_bloco'] = HexColor('#' + d[nome][modo]['osso_por_papel']['bloco'])
    k['rgb'] = {n: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for n, v in cores.items()}
    k['carimbo'] = HexColor('#C2334D')   # o vermelho do selo (arte/gera.py)
    return k


def alpha(cor, a):
    return Color(cor.red, cor.green, cor.blue, alpha=a)


def salva(img, nome):
    p = os.path.join(TMP, nome)
    img.save(p)
    return p


def ensō(lado, cor, seed=1):
    """Círculo de pincel aberto, mais grosso no começo e seco no fim."""
    random.seed(seed)
    img = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = lado / 2
    r = lado * 0.40
    ini = random.uniform(-100, -70)
    passos = 900
    for i in range(passos):
        t = i / passos
        ang = math.radians(ini + t * 335)
        rr = r + math.sin(t * 7) * lado * 0.008
        x, y = c + math.cos(ang) * rr, c + math.sin(ang) * rr
        g = lado * 0.065 * (1 - t) ** 0.6 + lado * 0.012
        d.ellipse([x - g, y - g, x + g, y + g], fill=cor + (255,))
    img = arte.desgasta(img, 0.18, 2)
    return img.filter(ImageFilter.GaussianBlur(0.6))


def ruido_papel(larg, alt, cor, seed=3):
    random.seed(seed)
    img = Image.new('RGBA', (larg, alt), (0, 0, 0, 0))
    px = img.load()
    for y in range(alt):
        for x in range(larg):
            if random.random() < 0.12:
                px[x, y] = cor + (random.randint(4, 22),)
    return img.filter(ImageFilter.GaussianBlur(0.4))


def recolore(caminho, cor):
    img = Image.open(caminho).convert('RGBA')
    novo = Image.new('RGBA', img.size, cor + (255,))
    novo.putalpha(img.getchannel('A'))
    return novo


def kanji_marca(texto, tam, cor, a=18):
    f = ImageFont.truetype(os.path.join(FONTES, 'YujiSyuku.ttf'), tam)
    img = Image.new('RGBA', (int(tam * len(texto) * 1.05), int(tam * 1.2)), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), texto, font=f, fill=cor + (a,))
    return img


# ---------------------------------------------------------------- base de desenho
class Base:
    def __init__(self, c, k):
        self.c, self.k = c, k

    def Y(self, y, h=0):
        return H - y - h

    def txt(self, x, y, s, tam=8, cor=None, fonte='Oswald', al='e'):
        c = self.c
        c.setFillColor(cor if cor is not None else self.k['texto'])
        c.setFont(fonte, tam)
        yy = self.Y(y) - tam * 0.78
        if fonte == 'Oswald' and al == 'e' and any(ord(ch) > 0x2E80 for ch in s):
            # texto misto: o kanji sai na fonte de pincel, o resto na Oswald
            xx = x
            for ch in s:
                f = 'Yuji' if ord(ch) > 0x2E80 else 'Oswald'
                c.setFont(f, tam)
                c.drawString(xx, yy, ch)
                xx += pdfmetrics.stringWidth(ch, f, tam)
            return
        {'c': c.drawCentredString, 'd': c.drawRightString}.get(al, c.drawString)(x, yy, s)

    def poly(self, pts, fill=None, stroke=None, lw=1):
        c = self.c
        p = c.beginPath()
        p.moveTo(pts[0][0], self.Y(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(x, self.Y(y))
        p.close()
        if fill is not None:
            c.setFillColor(fill)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
        c.drawPath(p, fill=1 if fill is not None else 0, stroke=1 if stroke is not None else 0)

    def img(self, caminho, x, y, w, h):
        self.c.drawImage(caminho, x, self.Y(y, h), w, h, mask='auto')

    def linha(self, x1, y1, x2, y2, cor, lw=0.6, dash=None):
        c = self.c
        c.setStrokeColor(cor)
        c.setLineWidth(lw)
        c.setDash(*(dash or []))
        c.line(x1, self.Y(y1), x2, self.Y(y2))
        c.setDash()

    def fundo(self, cor=None):
        self.c.setFillColor(cor or self.k['fundo'])
        self.c.rect(0, 0, W, H, stroke=0, fill=1)

    def girado(self, x, y, ang, fn):
        c = self.c
        c.saveState()
        c.translate(x, self.Y(y))
        c.rotate(ang)
        fn()
        c.restoreState()


# ================================================================ A · REGISTRO
class Registro(Base):
    nome = 'A-registro'

    def fundo_papel(self):
        self.fundo()
        p = salva(ruido_papel(600, 850, self.k['rgb']['texto']), 'papelA.png')
        self.img(p, 0, 0, W, H)
        # faixa lateral do dossiê
        k = self.k
        self.c.setFillColor(k['papel'])
        self.c.rect(0, 0, 30, H, stroke=0, fill=1)
        self.linha(30, 0, 30, H, k['linha'], 1.2)
        self.linha(33, 0, 33, H, k['linha'], 0.4)

        def lateral():
            self.c.setFillColor(k['texto_fraco'])
            self.c.setFont('Oswald', 7)
            self.c.drawString(0, 0, 'ESCOLA TÉCNICA JUJUTSU  ·  REGISTRO DE FEITICEIRO  ·  USO INTERNO  ·  '
                                    'NÃO RASURAR  ·  CICLO MALDITO')
        self.girado(18, 820, 90, lateral)
        self.txt(15, 18, '呪', 13, k['bloco'], 'Yuji', 'c')

    def aba(self, y, num, rot):
        """Aba de pasta saindo da faixa lateral."""
        k = self.k
        self.poly([(30, y), (46, y + 3), (46, y + 37), (30, y + 40)], fill=k['bloco'])
        self.txt(38, y + 5, num, 7, k['osso_bloco'], al='c')

        def r():
            self.c.setFillColor(k['osso_bloco'])
            self.c.setFont('Oswald', 5.5)
            self.c.drawCentredString(0, 0, rot)
        self.girado(40.5, y + 24, 90, r)

    def regua(self, x, y, w, grosso=True):
        k = self.k
        self.linha(x, y, x + w, y, k['linha'], 1.4 if grosso else 0.6)
        self.linha(x, y + 2.5, x + w, y + 2.5, k['linha'], 0.4)

    def secao(self, x, y, w, num, titulo, nota=''):
        k = self.k
        self.txt(x, y, num, 13, k['bloco'])
        self.txt(x + 22, y + 1.5, titulo, 10.5, k['texto'])
        if nota:
            self.txt(x + w, y + 4, nota, 6, k['texto_fraco'], al='d')
        self.regua(x, y + 16, w)

    def campo_linha(self, x, y, w, rot, valor):
        k = self.k
        self.txt(x, y, rot, 5.8, k['texto_fraco'])
        self.txt(x + 2, y + 8, valor, 10, k['texto'], 'Helvetica')
        self.linha(x, y + 22, x + w, y + 22, k['linha'], 0.6, [1, 1.5])

    def cantos(self, x, y, w, h, cor, t=6, lw=1.2):
        for cx, cy, dx, dy in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            self.linha(cx, cy, cx + dx * t, cy, cor, lw)
            self.linha(cx, cy, cx, cy + dy * t, cor, lw)

    def barras(self, x, y, w, h):
        random.seed(53)
        xx = x
        self.c.setFillColor(self.k['texto'])
        while xx < x + w:
            bw = random.choice([0.6, 0.6, 1.2, 1.8])
            self.c.rect(xx, self.Y(y, h), bw, h, stroke=0, fill=1)
            xx += bw + random.choice([0.6, 1.2, 1.8])

    def pagina1(self):
        k = self.k
        self.fundo_papel()
        X, R = 58, W - 26
        cw = R - X
        # cabeçalho
        self.txt(X, 26, 'REGISTRO DE FEITICEIRO', 25, k['texto'])
        self.txt(X, 56, 'CICLO MALDITO  ·  FICHA DE PERSONAGEM  ·  DOCUMENTO OFICIAL', 7, k['texto_fraco'])
        self.txt(X, 70, 'Nº  M-R53-0002', 9, k['bloco'], 'Helvetica-Bold')
        self.barras(X + 90, 69, 120, 11)
        self.txt(X + 216, 71, 'EMITIDA 24.10.2026', 7, k['texto_fraco'])
        # foto + carimbo
        fx, fy, fw, fh = R - 96, 22, 96, 122
        moldura = salva(arte.moldura(360, 460, k['rgb']['tinta'] + (255,)), 'molduraA.png')
        self.img(moldura, fx, fy, fw, fh)
        selo = salva(recolore(os.path.join(RAIZ, 'arte/selo-呪.png'), (194, 51, 77)), 'seloA.png')

        def carimbo():
            self.c.drawImage(selo, -27, -27, 54, 54, mask='auto')
        self.girado(fx - 6, fy + fh - 10, 14, carimbo)
        self.regua(X, 86, fx - X - 14)
        # identidade em linhas de formulário
        y = 96
        cols = [('PORTADOR', 'Kaori', 150), ('REGISTRADO POR', 'Suii', 100), ('NÍVEL', '2', 34), ('GRAU', '4', 34)]
        x = X
        for rot, v, w in cols:
            self.campo_linha(x, y, w, rot, v)
            x += w + 10
        y = 126
        cols = [('ORIGEM', 'Descendente', 110), ('CAMINHO', 'Bastião', 100), ('TRILHA', 'Muro', 80), ('XP', '0', 44)]
        x = X
        for rot, v, w in cols:
            self.campo_linha(x, y, w, rot, v)
            x += w + 10

        # 01 atributos
        self.aba(160, '01', 'ATRIBUTOS')
        y = 160
        self.secao(X, y, cw, '01', 'ATRIBUTOS', 'o número já é o modificador')
        bw = (cw - 4 * 10) / 5
        for i, (sg, nome, v, _kj) in enumerate(KAORI['atr']):
            x = X + i * (bw + 10)
            self.c.setFillColor(k['tinta'])
            self.c.rect(x, self.Y(y + 24, 50), bw, 50, stroke=0, fill=1)
            self.cantos(x, y + 24, bw, 50, k['bloco'])
            self.txt(x + 6, y + 28, sg, 7, k['bloco'])
            self.txt(x + bw / 2, y + 33, str(v), 28, k['texto'], al='c')
            self.txt(x + bw / 2, y + 64, nome.upper(), 5.8, k['texto_fraco'], al='c')

        # 02 recursos: réguas
        self.aba(244, '02', 'RECURSOS')
        y = 244
        self.secao(X, y, cw, '02', 'RECURSOS', 'atual / máximo  ·  ± ajuste')
        for i, (rot, at, mx) in enumerate(KAORI['recursos']):
            yy = y + 26 + i * 20
            self.txt(X, yy + 3, rot, 8, k['texto'])
            rx, rw = X + 70, cw - 70 - 96
            self.linha(rx, yy + 10, rx + rw, yy + 10, k['linha'], 1)
            n = 40
            for j in range(n + 1):
                tam = 6 if j % 10 == 0 else (4 if j % 5 == 0 else 2.2)
                self.linha(rx + rw * j / n, yy + 10, rx + rw * j / n, yy + 10 - tam, k['linha'], 0.5)
            self.c.setFillColor(k['bloco'])
            self.c.rect(rx, self.Y(yy + 13, 3), rw * at / mx, 3, stroke=0, fill=1)
            self.txt(R - 90, yy + 1, '%d' % at, 13, k['texto'], 'Helvetica-Bold')
            self.txt(R - 62, yy + 3, '/ %d' % mx, 10, k['texto_fraco'], 'Helvetica')
            self.c.setStrokeColor(k['linha'])
            self.c.rect(R - 22, self.Y(yy + 13, 11), 20, 11, stroke=1, fill=0)
            self.txt(R - 30, yy + 4, '±', 7, k['texto_fraco'])

        # 03 combate: tabela de carimbos
        self.aba(336, '03', 'COMBATE')
        y = 336
        self.secao(X, y, cw, '03', 'COMBATE', 'maestria +1')
        bw = cw / 8
        for i, (rot, v) in enumerate(KAORI['combate']):
            x = X + i * bw
            if i:
                self.linha(x, y + 24, x, y + 62, k['linha'], 0.4, [1, 1.5])
            self.txt(x + bw / 2, y + 26, rot, 5.6, k['texto_fraco'], al='c')
            self.txt(x + bw / 2, y + 37, v, 14 if len(v) < 5 else 10.5, k['texto'], al='c')
        self.regua(X, y + 66, cw, False)

        # 04 perícias com pontilhado
        self.aba(418, '04', 'TREINOS')
        y = 418
        self.secao(X, y, cw, '04', 'PERÍCIAS E RESISTÊNCIAS', '■ treinada   ◆ especialista   ± ajuste')
        lst = pericias()
        col = (cw - 20) / 2
        rh = 18.5
        for i, (nome, sg, v, t) in enumerate(lst):
            cx = X + (i // 12) * (col + 20)
            yy = y + 24 + (i % 12) * rh
            self.c.setStrokeColor(k['bloco'])
            self.c.setFillColor(k['bloco'] if t else k['fundo'])
            self.c.rect(cx, self.Y(yy + 1.5, 7), 7, 7, stroke=1, fill=1)
            self.txt(cx + 12, yy + 1, nome, 8.5, k['texto'], 'Helvetica')
            self.txt(cx + 12 + pdfmetrics.stringWidth(nome, 'Helvetica', 8.5) + 4, yy + 2.5, sg, 5.5, k['texto_fraco'])
            self.linha(cx + 105, yy + 8, cx + col - 34, yy + 8, k['linha'], 0.6, [0.5, 2])
            self.txt(cx + col, yy + 0.5, v, 10, k['texto'], 'Helvetica-Bold', 'd')
        # TRs no fim da segunda coluna
        cx = X + col + 20
        yy = y + 24 + 11 * rh + 8
        self.txt(cx, yy, 'TESTES DE RESISTÊNCIA', 7.5, k['bloco'])
        for i, (nome, sg, v, t) in enumerate(KAORI['tr']):
            y2 = yy + 13 + i * rh
            self.c.setStrokeColor(k['bloco'])
            self.c.setFillColor(k['bloco'] if t else k['fundo'])
            self.c.rect(cx, self.Y(y2 + 1.5, 7), 7, 7, stroke=1, fill=1)
            self.txt(cx + 12, y2 + 1, nome, 8.5, k['texto'], 'Helvetica')
            self.linha(cx + 105, y2 + 8, cx + col - 34, y2 + 8, k['linha'], 0.6, [0.5, 2])
            self.txt(cx + col, y2 + 0.5, v, 10, k['texto'], 'Helvetica-Bold', 'd')

        # rodapé: assinatura e selo 封 apagado
        y = 790
        self.regua(X, y, cw, False)
        self.linha(R - 180, y + 30, R, y + 30, k['linha'], 0.6)
        self.txt(R - 90, y + 33, 'ASSINATURA DO MESTRE RESPONSÁVEL', 5.8, k['texto_fraco'], al='c')
        self.txt(X, y + 10, 'Ciclo Maldito · livro R53 · pág. 1/4', 6, k['texto_fraco'])
        selo2 = salva(recolore(os.path.join(RAIZ, 'arte/selo-封.png'), k['rgb']['bloco']), 'seloA2.png')

        def c2():
            self.c.setFillAlpha(0.35)
            self.c.drawImage(selo2, -24, -24, 48, 48, mask='auto')
        self.girado(R - 210, y + 22, -9, c2)

    def pagina4(self):
        k = self.k
        self.fundo_papel()
        X, R = 58, W - 26
        cw = R - X
        self.txt(X, 26, 'REPERTÓRIO', 25, k['texto'])
        self.txt(X, 56, 'FICHAS CATALOGRÁFICAS DE FEITIÇOS, MANEJOS E KATAS  ·  UMA POR APLICAÇÃO', 7, k['texto_fraco'])
        self.regua(X, 74, cw)
        self.aba(90, '05', 'REPERTÓRIO')
        gw, gh = (cw - 14) / 2, 214
        for i in range(6):
            x = X + (i % 2) * (gw + 14)
            y = 90 + (i // 2) * (gh + 12)
            self.ficha_catalogo(x, y, gw, gh, FEITICO if i == 0 else None, i + 1)

    def ficha_catalogo(self, x, y, w, h, f, n):
        k = self.k
        self.c.setFillColor(k['papel'])
        self.c.setStrokeColor(k['linha'])
        self.c.setLineWidth(0.8)
        self.c.rect(x, self.Y(y, h), w, h, stroke=1, fill=1)
        # furo de fichário e aba numerada
        self.c.setFillColor(k['fundo'])
        self.c.circle(x + w / 2, self.Y(y + h - 9), 4, stroke=1, fill=1)
        self.poly([(x + w - 58, y), (x + w - 52, y - 9), (x + w - 6, y - 9), (x + w, y)], fill=k['bloco'])
        self.txt(x + w - 29, y - 7.5, 'Nº %02d' % n, 7, k['osso_bloco'], al='c')
        fv = f or {}
        self.txt(x + 8, y + 7, fv.get('nome', 'nome da aplicação'), 12,
                 k['texto'] if f else k['texto_fraco'])
        self.txt(x + w - 8, y + 9, 'CLASSE %s · %s PE' % (fv.get('classe', '__'), fv.get('pe', '__')), 8,
                 k['bloco'], al='d')
        self.linha(x + 6, y + 26, x + w - 6, y + 26, k['linha'], 1.2)
        self.linha(x + 6, y + 28.5, x + w - 6, y + 28.5, k['linha'], 0.4)
        linhas = [('AÇÃO', 'acao'), ('ALCANCE', 'alcance'), ('ACERTO', 'acerto'), ('TR', 'tr'),
                  ('DANO / CURA', 'dano'), ('MELHORIAS', 'melhorias'), ('RESTRIÇÕES', 'restricoes')]
        for j, (rot, ch) in enumerate(linhas):
            yy = y + 33 + j * 14
            self.txt(x + 8, yy + 2, rot, 5.8, k['texto_fraco'])
            self.txt(x + 62, yy, fv.get(ch, ''), 8, k['texto'], 'Helvetica')
            self.linha(x + 60, yy + 11, x + w - 8, yy + 11, k['linha'], 0.4, [0.5, 1.5])
        yy = y + 33 + 7 * 14 + 3
        self.txt(x + 8, yy, 'COMO É', 5.8, k['texto_fraco'])
        if f:
            self.paragrafo(x + 8, yy + 9, w - 16, f['como'], 7.3)
        for j in range(5):
            self.linha(x + 8, yy + 18 + j * 11, x + w - 8, yy + 18 + j * 11, k['linha'], 0.3, [0.5, 1.5])

    def paragrafo(self, x, y, w, texto, tam):
        palavras, linha, yy = texto.split(), '', y
        for p in palavras:
            t = (linha + ' ' + p).strip()
            if pdfmetrics.stringWidth(t, 'Helvetica', tam) > w:
                self.txt(x, yy, linha, tam, self.k['texto'], 'Helvetica')
                yy += tam + 3.7
                linha = p
            else:
                linha = t
        self.txt(x, yy, linha, tam, self.k['texto'], 'Helvetica')


# ================================================================ B · TALISMÃ
class Talisma(Base):
    nome = 'B-talisma'

    def fundo_tinta(self, seed=7):
        k = self.k
        self.fundo()
        marca = salva(kanji_marca('呪', 900, k['rgb']['bloco'], 16), 'marcaB.png')
        self.img(marca, 150, 120, 520, 620)
        random.seed(seed)
        for i, (x, y, s) in enumerate([(W - 150, 690, 150), (-30, 120, 120), (W - 120, -20, 110)]):
            arte.random.seed(seed + i)
            p = salva(arte.respingo(300, (194, 51, 77), 22), 'respB%d.png' % i)
            self.c.saveState()
            self.c.setFillAlpha(0.5)
            self.img(p, x, y, s, s)
            self.c.restoreState()

    def ofuda(self, x, y, w, h, titulo=None, kanji=None):
        """Faixa de papel de talismã: borda dupla, cantos amarrados, selo no topo."""
        k = self.k
        self.c.setFillColor(k['painel'])
        self.c.setStrokeColor(k['linha'])
        self.c.setLineWidth(1.4)
        self.c.rect(x, self.Y(y, h), w, h, stroke=1, fill=1)
        self.c.setLineWidth(0.5)
        self.c.rect(x + 3.5, self.Y(y + 3.5, h - 7), w - 7, h - 7, stroke=1, fill=0)
        for cx, cy in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
            self.c.setFillColor(k['bloco'])
            self.poly([(cx - 4, cy), (cx, cy - 4), (cx + 4, cy), (cx, cy + 4)], fill=k['bloco'])
        if titulo:
            tw = pdfmetrics.stringWidth(titulo, 'Oswald', 9) + 30
            self.c.setFillColor(k['fundo'])
            self.c.rect(x + 14, self.Y(y - 6, 13), tw, 13, stroke=0, fill=1)
            self.txt(x + 22, y - 4.5, titulo, 9, k['acento'])
            if kanji:
                self.txt(x + 14 + tw - 4, y - 5, kanji, 9, k['bloco'], 'Yuji', 'd')

    def selo_atributo(self, cx, cy, r, sg, nome, v, kj):
        k = self.k
        c = self.c
        c.setStrokeColor(k['bloco'])
        c.setFillColor(k['tinta'])
        c.setLineWidth(2.2)
        c.circle(cx, self.Y(cy), r, stroke=1, fill=1)
        c.setLineWidth(0.6)
        c.circle(cx, self.Y(cy), r - 5, stroke=1, fill=0)
        # dentes do selo
        for j in range(24):
            a = math.tau * j / 24
            c.line(cx + math.cos(a) * (r + 1.5), self.Y(cy) + math.sin(a) * (r + 1.5),
                   cx + math.cos(a) * (r + 4), self.Y(cy) + math.sin(a) * (r + 4))
        self.txt(cx, cy - r + 9, kj, 11, k['bloco'], 'Yuji', 'c')
        self.txt(cx, cy - 11, str(v), 26, k['texto'], al='c')
        self.txt(cx, cy + r + 8, nome.upper(), 7.5, k['texto_fraco'], al='c')
        self.txt(cx, cy + 15, sg, 6.5, k['acento'], al='c')

    def etiqueta(self, x, y, w, h, rot, v):
        """Ema/etiqueta pendurada: pentágono com furo e cordão."""
        k = self.k
        self.linha(x + w / 2, y - 10, x + w / 2, y + 6, k['carimbo'], 1)
        self.poly([(x, y + 8), (x + w / 2, y), (x + w, y + 8), (x + w, y + h), (x, y + h)],
                  fill=k['painel_alto'], stroke=k['linha'], lw=0.8)
        self.c.setFillColor(k['fundo'])
        self.c.circle(x + w / 2, self.Y(y + 7), 2, stroke=0, fill=1)
        self.txt(x + w / 2, y + 13, rot, 5.6, k['texto_fraco'], al='c')
        self.txt(x + w / 2, y + 23, v, 13 if len(v) < 5 else 10, k['texto'], al='c')

    def pagina1(self):
        k = self.k
        self.fundo_tinta()
        # cabeçalho: pincelada atrás do título, kanji vertical
        pin = salva(recolore(os.path.join(RAIZ, 'arte/pincelada.png'), k['rgb']['bloco']), 'pinB.png')
        self.img(pin, 30, 12, 470, 58)
        self.txt(56, 24, 'CICLO MALDITO', 26, k['osso_bloco'])
        self.txt(58, 64, 'FICHA DE PERSONAGEM  ·  呪術師の記録', 8, k['texto_fraco'])
        for i, ch in enumerate('呪術師'):
            self.txt(W - 34, 22 + i * 26, ch, 22, k['acento'], 'Yuji', 'c')
        self.linha(W - 50, 20, W - 50, 100, k['bloco'], 0.8)
        # identidade
        y = 92
        dados = [('NOME', 'Kaori', 130), ('JOGADOR', 'Suii', 80), ('ORIGEM', 'Descendente', 95),
                 ('CAMINHO', 'Bastião · Muro', 110), ('NÍVEL', '2', 30), ('GRAU', '4', 30)]
        x = 26
        for rot, v, w in dados:
            self.txt(x, y, rot, 6, k['texto_fraco'])
            self.txt(x, y + 9, v, 11, k['texto'], 'Helvetica')
            self.linha(x, y + 24, x + w, y + 24, k['bloco'], 0.8)
            x += w + 8
        # atributos como selos
        y = 150
        r = 34
        for i, (sg, nome, v, kj) in enumerate(KAORI['atr']):
            self.selo_atributo(70 + i * 108, y + r, r, sg, nome, v, kj)
        # recursos em ensō
        y = 248
        cores = ['carimbo', 'bloco', 'acento']
        for i, (rot, at, mx) in enumerate(KAORI['recursos']):
            cx = 26 + i * 184
            cor = self.k[cores[i]]
            rgb = (int(cor.red * 255), int(cor.green * 255), int(cor.blue * 255))
            p = salva(ensō(400, rgb, seed=i + 2), 'enso%d.png' % i)
            self.img(p, cx, y, 104, 104)
            self.txt(cx + 52, y + 34, str(at), 24, k['texto'], al='c')
            self.txt(cx + 52, y + 62, 'de %d' % mx, 8, k['texto_fraco'], al='c')
            self.txt(cx + 108, y + 32, rot, 12, k['texto'])
            self.txt(cx + 108, y + 50, 'temp. ____', 7, k['texto_fraco'])
            self.txt(cx + 108, y + 62, '± ____', 7, k['texto_fraco'])
        # combate: etiquetas penduradas num cordão
        y = 372
        self.linha(16, y - 8, W - 16, y - 8, k['carimbo'], 1.2)
        bw = (W - 52) / 8
        for i, (rot, v) in enumerate(KAORI['combate']):
            self.etiqueta(26 + i * bw + 3, y, bw - 6, 40, rot, v)
        # perícias num ofuda largo
        y = 438
        self.ofuda(22, y, W - 44, 380, 'PERÍCIAS', '技')
        col = (W - 44 - 40) / 2
        for i, (nome, sg, v, t) in enumerate(pericias()):
            cx = 40 + (i // 12) * (col + 10)
            yy = y + 16 + (i % 12) * 22
            self.c.setStrokeColor(k['bloco'])
            self.c.setFillColor(k['bloco'] if t else k['painel'])
            self.c.circle(cx + 4, self.Y(yy + 6), 4, stroke=1, fill=1)
            self.txt(cx + 14, yy + 1, nome, 9, k['texto'], 'Helvetica')
            self.txt(cx + col - 70, yy + 2, sg, 6.5, k['texto_fraco'])
            pin2 = salva(recolore(os.path.join(RAIZ, 'arte/pincelada.png'), k['rgb']['painel_alto']), 'pinB2.png')
            self.img(pin2, cx + col - 50, yy - 3, 50, 16)
            self.txt(cx + col - 22, yy + 0.5, v, 10.5, k['texto'], 'Helvetica-Bold', 'c')
            self.linha(cx + 14, yy + 17, cx + col - 54, yy + 17, k['linha'], 0.3)
        # TRs: quatro selos pequenos
        cx = 40 + col + 10
        yy = y + 16 + 11 * 22 + 6
        self.txt(cx, yy, 'TESTES DE RESISTÊNCIA', 8, k['acento'])
        for i, (nome, sg, v, t) in enumerate(KAORI['tr']):
            x = cx + i * (col / 4)
            self.c.setStrokeColor(k['carimbo'] if t else k['linha'])
            self.c.setFillColor(k['tinta'])
            self.c.setLineWidth(1.6)
            self.c.circle(x + 26, self.Y(yy + 42), 19, stroke=1, fill=1)
            self.txt(x + 26, yy + 34, v, 13, k['texto'], al='c')
            self.txt(x + 26, yy + 64, nome.upper(), 6.5, k['texto_fraco'], al='c')
        self.txt(W / 2, 826, 'Ciclo Maldito · livro R53 · pág. 1/4', 6, k['texto_fraco'], al='c')

    def pagina4(self):
        k = self.k
        self.fundo_tinta(11)
        pin = salva(recolore(os.path.join(RAIZ, 'arte/pincelada.png'), k['rgb']['bloco']), 'pinB.png')
        self.img(pin, 30, 12, 470, 58)
        self.txt(56, 24, 'REPERTÓRIO', 26, k['osso_bloco'])
        self.txt(58, 64, 'CADA FEITIÇO É UM TALISMÃ  ·  術式', 8, k['texto_fraco'])
        tw, th = (W - 44 - 2 * 12) / 3, 352
        for i in range(6):
            x = 22 + (i % 3) * (tw + 12)
            y = 92 + (i // 3) * (th + 22)
            self.talisma(x, y, tw, th, FEITICO if i == 0 else None)

    def talisma(self, x, y, w, h, f):
        k = self.k
        self.ofuda(x, y, w, h)
        fv = f or {}
        # selo da Classe no topo
        self.c.setStrokeColor(k['carimbo'])
        self.c.setFillColor(k['tinta'])
        self.c.setLineWidth(1.8)
        self.c.circle(x + w / 2, self.Y(y + 26), 16, stroke=1, fill=1)
        self.txt(x + w / 2, y + 18, fv.get('classe', ''), 16, k['texto'], al='c')
        self.txt(x + w / 2, y + 46, 'CLASSE', 5.5, k['texto_fraco'], al='c')
        self.txt(x + w / 2, y + 56, fv.get('nome', '_______________'), 12,
                 k['texto'] if f else k['texto_fraco'], al='c')
        self.txt(x + w / 2, y + 73, ('%s PE  ·  %s' % (fv['pe'], fv['acao'])) if f else 'PE · ação', 7.5,
                 k['acento'], al='c')
        self.linha(x + 14, y + 86, x + w - 14, y + 86, k['bloco'], 0.8)
        linhas = [('ALCANCE', 'alcance'), ('ACERTO', 'acerto'), ('TR', 'tr'), ('DANO', 'dano'),
                  ('MELHORIAS', 'melhorias'), ('RESTRIÇÕES', 'restricoes')]
        for j, (rot, ch) in enumerate(linhas):
            yy = y + 92 + j * 22
            self.txt(x + 12, yy, rot, 5.8, k['texto_fraco'])
            self.txt(x + 12, yy + 8, fv.get(ch, ''), 7.6, k['texto'], 'Helvetica')
            self.linha(x + 12, yy + 19, x + w - 12, yy + 19, k['linha'], 0.3)
        yy = y + 92 + 6 * 22 + 2
        self.txt(x + 12, yy, 'COMO É', 5.8, k['texto_fraco'])
        if f:
            Registro.paragrafo(self, x + 12, yy + 9, w - 24, f['como'], 7)
        # kanji vertical decorativo no rodapé do talismã
        self.txt(x + w / 2, y + h - 26, '呪', 15, k['carimbo'] if f else k['linha'], 'Yuji', 'c')


# ================================================================ C · EXPANSÃO
class Expansao(Base):
    nome = 'C-expansao'

    def chanfro(self, x, y, w, h, ch=10):
        return [(x + ch, y), (x + w, y), (x + w, y + h - ch), (x + w - ch, y + h), (x, y + h), (x, y + ch)]

    def painel(self, x, y, w, h, titulo=None, ch=10, sombra=True):
        k = self.k
        if sombra:
            self.poly([(px + 4, py + 4) for px, py in self.chanfro(x, y, w, h, ch)], fill=k['bloco'])
        self.poly(self.chanfro(x, y, w, h, ch), fill=k['painel'], stroke=k['texto'], lw=1.6)
        if titulo:
            tw = pdfmetrics.stringWidth(titulo, 'Oswald', 9.5) + 22
            self.poly([(x + 12, y - 7), (x + 12 + tw, y - 7), (x + 4 + tw, y + 7), (x + 4, y + 7)],
                      fill=k['texto'])
            self.txt(x + 18, y - 5.5, titulo, 9.5, k['fundo'])

    def reticula(self, x0, y0, w, h, cor, ang=1):
        """Retícula de mangá: pontos que crescem na diagonal."""
        c = self.c
        c.setFillColor(cor)
        passo = 7
        for i in range(int(w / passo) + 1):
            for j in range(int(h / passo) + 1):
                t = ((i / (w / passo)) + (j / (h / passo))) / 2
                t = t if ang > 0 else 1 - t
                r = 2.6 * max(0, t - 0.25)
                if r > 0.15:
                    off = passo / 2 if j % 2 else 0
                    c.circle(x0 + i * passo + off, self.Y(y0 + j * passo), r, stroke=0, fill=1)

    def velocidade(self, cx, cy, r0, r1, n, cor):
        random.seed(9)
        for i in range(n):
            a = math.tau * i / n + random.uniform(-0.02, 0.02)
            w = random.uniform(0.004, 0.012)
            p1 = (cx + math.cos(a - w) * r1, cy + math.sin(a - w) * r1)
            p2 = (cx + math.cos(a + w) * r1, cy + math.sin(a + w) * r1)
            p0 = (cx + math.cos(a) * r0 * random.uniform(0.9, 1.2), cy + math.sin(a) * r0 * random.uniform(0.9, 1.2))
            self.poly([p0, p1, p2], fill=cor)

    def hexagono(self, cx, cy, r):
        return [(cx + math.cos(math.radians(60 * i + 30)) * r, cy + math.sin(math.radians(60 * i + 30)) * r)
                for i in range(6)]

    def chip(self, x, y, w, h, v, cheio=True, tam=10):
        k = self.k
        self.poly([(x + 5, y), (x + w, y), (x + w - 5, y + h), (x, y + h)],
                  fill=k['texto'] if cheio else k['painel_alto'])
        self.txt(x + w / 2, y + (h - tam) / 2 + 0.5, v, tam, k['fundo'] if cheio else k['texto'], 'Helvetica-Bold', 'c')

    def cabecalho(self, titulo, sub, kanji):
        k = self.k
        self.fundo()
        self.velocidade(W - 90, 60, 40, 520, 70, alpha(k['bloco'], 0.25))
        self.reticula(0, 600, 220, 242, alpha(k['bloco'], 0.55))
        self.reticula(W - 200, 0, 200, 160, alpha(k['bloco'], 0.4), -1)
        marca = salva(kanji_marca(kanji, 300, k['rgb']['acento'], 26), 'marcaC%s.png' % len(kanji))
        self.img(marca, 250, 4, 330, 84)
        self.poly([(0, 20), (W, 8), (W, 62), (0, 74)], fill=k['bloco'])
        self.poly([(0, 74), (W, 62), (W, 66), (0, 78)], fill=k['texto'])
        self.txt(22, 24, titulo, 30, k['osso_bloco'])
        self.txt(24, 60, sub, 7.5, k['osso_bloco'])

    def pagina1(self):
        k = self.k
        self.cabecalho('CICLO MALDITO', 'FICHA DE PERSONAGEM  ·  領域展開', '領域展開')
        # identidade em faixas inclinadas
        y = 94
        self.painel(22, y, W - 44, 46, 'FEITICEIRO')
        dados = [('NOME', 'Kaori', 120), ('JOGADOR', 'Suii', 74), ('ORIGEM', 'Descendente', 92),
                 ('CAMINHO · TRILHA', 'Bastião · Muro', 110), ('NÍVEL', '2', 34), ('GRAU', '4', 34)]
        x = 34
        for rot, v, w in dados:
            self.txt(x, y + 10, rot, 6, k['texto_fraco'])
            self.txt(x, y + 21, v, 11, k['texto'], 'Helvetica-Bold')
            x += w + 8
        # atributos em hexágonos com linhas de velocidade
        y = 186
        for i, (sg, nome, v, kj) in enumerate(KAORI['atr']):
            cx = 72 + i * 112
            self.poly([(px + 4, py + 4) for px, py in self.hexagono(cx, y, 40)], fill=k['bloco'])
            self.poly(self.hexagono(cx, y, 40), fill=k['painel'], stroke=k['texto'], lw=1.8)
            self.poly(self.hexagono(cx, y, 33), stroke=k['linha'], lw=0.6)
            self.txt(cx, y - 18, str(v), 30, k['texto'], al='c')
            self.chip(cx - 22, y + 30, 44, 13, sg, True, 8)
            self.txt(cx, y + 48, nome.upper(), 6.5, k['texto_fraco'], al='c')
        # recursos em barras segmentadas
        y = 258
        self.painel(22, y, W - 44, 92, 'RECURSOS')
        cores = ['carimbo', 'acento', 'regua']
        for i, (rot, at, mx) in enumerate(KAORI['recursos']):
            yy = y + 14 + i * 25
            self.txt(36, yy + 3, rot, 9, k['texto'])
            x0, bw = 120, 330
            n = 24
            for j in range(n):
                sx = x0 + j * (bw / n)
                cheio = j < round(n * at / mx)
                self.poly([(sx + 3, yy), (sx + bw / n - 1, yy), (sx + bw / n - 4, yy + 13), (sx, yy + 13)],
                          fill=k[cores[i]] if cheio else k['painel_alto'])
            self.txt(x0 + bw + 14, yy, '%d' % at, 14, k['texto'], 'Helvetica-Bold')
            self.txt(x0 + bw + 40, yy + 3, '/ %d' % mx, 9, k['texto_fraco'], 'Helvetica')
            self.chip(W - 66, yy, 30, 13, '±', False, 8)
        # combate: losango grande da defesa + chips
        y = 368
        self.painel(22, y, W - 44, 84, 'COMBATE')
        cx, cy = 80, y + 42
        self.poly([(cx + 4, cy - 34 + 4), (cx + 38 + 4, cy + 4), (cx + 4, cy + 38 + 4), (cx - 38 + 4, cy + 4)], fill=k['carimbo'])
        self.poly([(cx, cy - 34), (cx + 38, cy), (cx, cy + 38), (cx - 38, cy)], fill=k['tinta'], stroke=k['texto'], lw=1.8)
        self.txt(cx, cy - 13, '13', 22, k['texto'], al='c')
        self.txt(cx, cy + 12, 'DEFESA', 6.5, k['texto_fraco'], al='c')
        resto = KAORI['combate'][1:]
        bw = (W - 44 - 140) / 4
        for i, (rot, v) in enumerate(resto):
            x = 140 + (i % 4) * bw
            yy = y + 12 + (i // 4) * 34
            self.txt(x, yy, rot, 6, k['texto_fraco'])
            self.chip(x, yy + 9, bw - 14, 17, v, True, 10)
        # perícias com losango de treino
        y = 474
        self.painel(22, y, W - 44, 344, 'PERÍCIAS  ·  RESISTÊNCIAS')
        col = (W - 44 - 36) / 2
        for i, (nome, sg, v, t) in enumerate(pericias()):
            cx = 36 + (i // 12) * (col + 8)
            yy = y + 14 + (i % 12) * 20
            d = 4.5
            self.poly([(cx + d, yy + 3), (cx + 2 * d, yy + 3 + d), (cx + d, yy + 3 + 2 * d), (cx, yy + 3 + d)],
                      fill=k['carimbo'] if t else None, stroke=k['texto'], lw=0.8)
            self.txt(cx + 15, yy + 1.5, nome, 9, k['texto'], 'Helvetica')
            self.txt(cx + col - 70, yy + 3, sg, 6.5, k['texto_fraco'])
            self.chip(cx + col - 42, yy, 36, 14, v, t, 9)
        cx = 36 + col + 8
        yy = y + 14 + 11 * 20 + 6
        self.txt(cx, yy, 'TESTES DE RESISTÊNCIA', 8, k['acento'])
        for i, (nome, sg, v, t) in enumerate(KAORI['tr']):
            x = cx + (i % 2) * (col / 2)
            y2 = yy + 14 + (i // 2) * 22
            self.txt(x, y2 + 2, nome, 9, k['texto'], 'Helvetica')
            self.chip(x + col / 2 - 52, y2, 36, 14, v, t, 9)
        self.txt(W / 2, 828, 'Ciclo Maldito · livro R53 · pág. 1/4', 6, k['texto_fraco'], al='c')

    def pagina4(self):
        k = self.k
        self.cabecalho('REPERTÓRIO', 'CARTAS DE TÉCNICA  ·  術式', '術式')
        cw, chh = (W - 44 - 2 * 14) / 3, 340
        for i in range(6):
            x = 22 + (i % 3) * (cw + 14)
            y = 100 + (i // 3) * (chh + 26)
            self.carta(x, y, cw, chh, FEITICO if i == 0 else None)

    def carta(self, x, y, w, h, f):
        k = self.k
        fv = f or {}
        self.poly([(px + 5, py + 5) for px, py in self.chanfro(x, y, w, h, 16)], fill=k['bloco'])
        self.poly(self.chanfro(x, y, w, h, 16), fill=k['painel'], stroke=k['texto'], lw=1.8)
        # arte da carta: retícula + kanji
        self.c.saveState()
        p = self.c.beginPath()
        p.rect(x + 8, self.Y(y + 40, 70), w - 16, 70)
        self.c.clipPath(p, stroke=0, fill=0)
        self.c.setFillColor(k['tinta'])
        self.c.rect(x + 8, self.Y(y + 40, 70), w - 16, 70, stroke=0, fill=1)
        self.reticula(x + 8, y + 40, w - 16, 70, alpha(k['bloco'], 0.7))
        self.velocidade(x + w / 2, y + 75, 8, 120, 40, alpha(k['acento'], 0.3))
        self.c.restoreState()
        self.txt(x + w / 2, y + 52, '重' if f else '?', 34, k['texto'] if f else k['linha'], 'Yuji', 'c')
        # hexágono da classe
        hx, hy = x + w - 22, y + 20
        self.poly(self.hexagono(hx, hy, 16), fill=k['carimbo'], stroke=k['texto'], lw=1.4)
        self.txt(hx, hy - 8, fv.get('classe', ''), 14, k['texto'], al='c')
        self.txt(x + 12, y + 8, fv.get('nome', 'nome'), 11.5, k['texto'] if f else k['texto_fraco'])
        self.txt(x + 12, y + 24, ('%s PE · %s' % (fv['pe'], fv['acao'])) if f else 'PE · ação', 7.5, k['acento'])
        linhas = [('ALCANCE', 'alcance'), ('ACERTO', 'acerto'), ('TR', 'tr'), ('DANO', 'dano'),
                  ('MELHORIAS', 'melhorias'), ('RESTRIÇÕES', 'restricoes')]
        for j, (rot, ch) in enumerate(linhas):
            yy = y + 118 + j * 20
            self.chip(x + 8, yy, 52, 12, rot, False, 5.8)
            self.txt(x + 64, yy + 2, fv.get(ch, ''), 7.4, k['texto'], 'Helvetica')
        yy = y + 118 + 6 * 20 + 4
        self.poly([(x + 8, yy), (x + w - 8, yy), (x + w - 8, y + h - 18), (x + w - 22, y + h - 8), (x + 8, y + h - 8)],
                  fill=k['tinta'], stroke=k['linha'], lw=0.6)
        if f:
            Registro.paragrafo(self, x + 14, yy + 6, w - 28, f['como'], 7)


# ---------------------------------------------------------------- saída
def main():
    os.makedirs(SAIDAS, exist_ok=True)
    k = paleta()
    for cls in (Registro, Talisma, Expansao):
        caminho = os.path.join(SAIDAS, 'estudo-%s.pdf' % cls.nome)
        c = canvas.Canvas(caminho, pagesize=A4)
        c.setTitle('Estudo de estilo · %s' % cls.nome)
        e = cls(c, k)
        e.pagina1()
        c.showPage()
        e.pagina4()
        c.showPage()
        c.save()
        print(caminho)


if __name__ == '__main__':
    main()
