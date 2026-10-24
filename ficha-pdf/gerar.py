#!/usr/bin/env python3
"""Gera a ficha em PDF preenchível do Ciclo Maldito.

Estilo misto: moldura de painel de mangá (cantos cortados, sombra deslocada,
retícula) com o repertório em fichas catalográficas. Seis páginas, quatro
paletas (Mizuki claro/escuro, Eclipse claro/escuro), as mesmas da planilha.

Regras da casa:
- todo número calculado tem ao lado um campo ± que soma ao resultado;
- o que ainda não abriu pelo nível fica coberto pelo selo 封 e travado;
  o selo some sozinho ao chegar lá (ou pela caixa "ignorar selos").

As contas são JavaScript de formulário: rodam no Acrobat Reader e no Firefox.
Leitores sem JavaScript deixam preencher, mas não calculam nem abrem selos.

Uso: python3 ficha-pdf/gerar.py   ->  ficha-pdf/saidas/*.pdf
"""
import json
import logging
import math
import os
import random
import sys
import tempfile
import zlib
from contextlib import contextmanager

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject, StreamObject, TextStringObject)
from reportlab.lib.colors import Color, HexColor, transparent
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logging.getLogger('pypdf').setLevel(logging.ERROR)  # aviso inofensivo do reportlab

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SAIDAS = os.path.join(AQUI, 'saidas')
FONTES = os.path.join(RAIZ, 'arte/fontes')
TMP = tempfile.mkdtemp(prefix='ficha-pdf-')
W, H = A4
M = 22                      # margem
CW = W - 2 * M              # largura útil
PAGINAS = 6

pdfmetrics.registerFont(TTFont('Oswald', os.path.join(FONTES, 'Oswald.ttf')))
pdfmetrics.registerFont(TTFont('Yuji', os.path.join(FONTES, 'YujiSyuku.ttf')))

PALETAS = [('Mizuki', 'claro'), ('Mizuki', 'escuro'), ('Eclipse', 'claro'), ('Eclipse', 'escuro')]

# ---------------------------------------------------------------- regras (livro R53)
ATRIBUTOS = [('for', 'FORÇA'), ('des', 'DESTREZA'), ('con', 'CONSTITUIÇÃO'),
             ('int', 'INTELIGÊNCIA'), ('ess', 'ESSÊNCIA')]
SIGLA = {'for': 'FOR', 'des': 'DES', 'con': 'CON', 'int': 'INT', 'ess': 'ESS'}

# cap. 7 · atributo fixo de cada perícia
PERICIAS = [('Atletismo', 'for'), ('Acrobacia', 'des'), ('Furtividade', 'des'),
            ('Pontaria', 'des'), ('Prestidigitação', 'des'), ('Investigação', 'int'),
            ('Intuição', 'int'), ('Ocultismo', 'int'), ('Religião', 'int'),
            ('História', 'int'), ('Hierarquia', 'int'), ('Medicina', 'int'),
            ('Sobrevivência', 'int'), ('Natureza', 'int'), ('Lidar com Animais', 'int'),
            ('Tecnologia', 'int'), ('Sentir Energia', 'ess'), ('Percepção', 'ess'),
            ('Persuasão', 'ess'), ('Enganação', 'ess'), ('Intimidação', 'ess'),
            ('Atuação', 'ess'), ('Provocar', 'ess')]

# cap. 7 · atributo padrão do ofício (o mestre pode trocar conforme a tarefa)
OFICIOS = [('Condução', 'des'), ('Arrombamento', 'des'), ('Herbalismo', 'int'),
           ('Forja', 'for'), ('Caligrafia', 'des'), ('Burocracia', 'int'),
           ('Entalhador', 'des'), ('Alfaiate', 'des'), ('Culinária', 'int'),
           ('Instrumento', 'ess'), ('Jogatina', 'ess')]

# cap. 6 · vida no nível 1, vida por nível seguinte (ambos + CON), PE por nível
CAMINHOS = {'Bastião': (12, 7, 4), 'Vanguarda': (8, 5, 5), 'Guia': (8, 5, 5),
            'Emanador': (6, 4, 6), 'Evocador': (6, 4, 6), 'Incursor': (6, 4, 6)}

# cap. 9 · progressão dos níveis 1 a 30
MAESTRIA = [1] * 9 + [2] * 8 + [3] * 8 + [4] * 5
ESPACOS = [2, 3, 3, 4, 4, 6, 6, 7, 7, 9, 9, 10, 10, 12, 12, 13, 13, 15, 15, 16,
           16, 18, 18, 19, 19, 21, 21, 22, 22, 24]
REFINO = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5,
          5, 6, 6, 6, 6, 7, 7, 7, 7, 8]
CLASSE_MAX = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
              6, 6, 6, 6, 6, 7, 7, 7, 7, 7]
CLASSE_0 = [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
CLASSE0_ABRE = [None, None, 5, 11, 17]      # a 3ª, 4ª e 5ª vagas de Classe 0
LIBERACOES = [10, 20, 30]                   # cap. 10 · Liberação Máxima
# cap. 14 · Expansão de Domínio: espaços no total por degrau
DEGRAUS = {'Incompleta': 2, 'Completa': 3, 'Sem Barreiras': 5}

N_CARTOES = 12
N_TALENTOS = 6          # 5 pagos + o CE 4 da Restrição corporal
N_APTIDOES = 12
N_ITENS = 14


def slug(t):
    tr = str.maketrans('áàâãéêíóôõúçÁÉÍÓÚÇ ', 'aaaaeeiooouc' + 'aeiouc_')
    return t.translate(tr).lower()


# ---------------------------------------------------------------- JavaScript
# d = documento, n() lê número, c() lê caixa marcada, t() lê texto, s() põe sinal.
JS_BASE = (
    "var d=this;"
    "function n(f){var x=d.getField(f);if(!x)return 0;"
    "var v=parseFloat(String(x.value).replace(',','.').replace('+',''));return isNaN(v)?0:v;}"
    "function c(f){var x=d.getField(f);return !!x&&x.value!='Off'&&x.value!=''&&x.value!==false;}"
    "function t(f){var x=d.getField(f);return x?String(x.value):'';}"
    "function vazio(f){return t(f).replace(/\\s/g,'')==='';}"
    "function s(v){return (v>=0?'+':'')+v;}"
    "function niv(){var l=Math.round(n('nivel'));return l<1?1:(l>30?30:l);}"
    "function br(v){return String(Math.round(v*10)/10).replace('.',',');}"
)


def tabela(nome, valores):
    return "var %s=[%s];" % (nome, ','.join(str(v) for v in valores))


# ---------------------------------------------------------------- arte por código
def paleta(nome, modo):
    d = json.load(open(os.path.join(RAIZ, 'medidas/paletas-grandes/paletas-grandes.json')))
    cores = d[nome][modo]['cores']
    k = {n: HexColor('#' + v) for n, v in cores.items()}
    k['osso_bloco'] = HexColor('#' + d[nome][modo]['osso_por_papel']['bloco'])
    k['rgb'] = {n: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for n, v in cores.items()}
    k['carimbo'] = HexColor('#C2334D')     # o vermelho do selo (arte/gera.py)
    k['rgb']['carimbo'] = (194, 51, 77)
    return k


def alpha(cor, a):
    return Color(cor.red, cor.green, cor.blue, alpha=a)


def recolore(caminho, rgb):
    img = Image.open(caminho).convert('RGBA')
    novo = Image.new('RGBA', img.size, rgb + (255,))
    novo.putalpha(img.getchannel('A'))
    return novo


def kanji_marca(texto, tam, rgb, a):
    f = ImageFont.truetype(os.path.join(FONTES, 'YujiSyuku.ttf'), tam)
    img = Image.new('RGBA', (int(tam * len(texto) * 1.05), int(tam * 1.2)), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((0, 0), texto, font=f, fill=rgb + (a,))
    p = os.path.join(TMP, 'marca-%s-%s.png' % (len(texto), '-'.join(map(str, rgb))))
    img.save(p)
    return p


def imagem_selo(w, h, k, texto, escala=2):
    """O selo que cobre uma seção ainda fechada: véu, carimbo 封 e o aviso."""
    W_, H_ = int(w * escala), int(h * escala)
    img = Image.new('RGBA', (W_, H_), k['rgb']['fundo'] + (222,))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, W_ - 2, H_ - 2], outline=k['rgb']['carimbo'] + (255,), width=max(2, int(escala * 1.2)))
    lado = int(min(H_ * 0.78, 74 * escala))
    selo = recolore(os.path.join(RAIZ, 'arte/selo-封.png'), k['rgb']['carimbo']).resize((lado, lado))
    selo = selo.rotate(10, expand=True, resample=Image.BICUBIC)
    grande = int(min(H_ * 0.30, 22 * escala))
    peq = max(int(grande * 0.46), 8 * escala)
    fo = ImageFont.truetype(os.path.join(FONTES, 'Oswald.ttf'), grande)
    fp = ImageFont.truetype(os.path.join(FONTES, 'Oswald.ttf'), peq)
    larg_txt = max(d.textlength('SELADO', font=fo), d.textlength(texto, font=fp))
    total = selo.width + 10 * escala + larg_txt
    x0 = int((W_ - total) / 2)
    img.alpha_composite(selo, (max(0, x0), int((H_ - selo.height) / 2)))
    xt = x0 + selo.width + 10 * escala
    yc = H_ / 2
    d.text((xt, yc - grande * 0.62), 'SELADO', font=fo, fill=k['rgb']['texto'] + (255,))
    d.text((xt, yc + grande * 0.48), texto, font=fp, fill=k['rgb']['texto_fraco'] + (255,))
    return img


# ---------------------------------------------------------------- a ficha
class Ficha:
    def __init__(self, caminho, nome_paleta, modo):
        self.caminho = caminho
        self.nome_paleta, self.modo = nome_paleta, modo
        self.k = paleta(nome_paleta, modo)
        self.c = canvas.Canvas(caminho, pagesize=A4)
        self.c.setTitle('Ciclo Maldito · ficha de personagem · %s %s' % (nome_paleta, modo))
        self.c.setAuthor('Projeto M')
        self.pg = 0
        self.calc = []          # (nome, js) na ordem de cálculo
        self.alinhar = {}       # nome -> 0/1/2
        self.botoes = []        # segmentos e selos (botões desenhados no pós-processo)
        self.selos = []         # (botão, condição JS, campos travados)
        self.selando = None     # lista de campos enquanto desenha uma área selada
        self.travados = set()
        self.segmentos = {}     # prefixo -> quantidade
        self.marcas = []        # caixas de marcar com marca acesa pelo cálculo

    # ------------------------------------------------ primitivas (y medido do topo)
    def Y(self, y, h=0):
        return H - y - h

    def txt(self, x, y, s, tam=8, cor=None, fonte='Oswald', al='e'):
        c = self.c
        c.setFillColor(cor if cor is not None else self.k['texto'])
        yy = self.Y(y) - tam * 0.78
        if fonte == 'Oswald' and any(ord(ch) > 0x2E80 for ch in s):
            larg = sum(pdfmetrics.stringWidth(ch, 'Yuji' if ord(ch) > 0x2E80 else 'Oswald', tam) for ch in s)
            xx = x - (larg / 2 if al == 'c' else larg if al == 'd' else 0)
            for ch in s:
                f = 'Yuji' if ord(ch) > 0x2E80 else 'Oswald'
                c.setFont(f, tam)
                c.drawString(xx, yy, ch)
                xx += pdfmetrics.stringWidth(ch, f, tam)
            return
        c.setFont(fonte, tam)
        {'c': c.drawCentredString, 'd': c.drawRightString}.get(al, c.drawString)(x, yy, s)

    def rot(self, x, y, s, tam=6, cor=None, al='e'):
        self.txt(x, y, s, tam, cor or self.k['texto_fraco'], al=al)

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

    def linha(self, x1, y1, x2, y2, cor, lw=0.6, dash=None):
        c = self.c
        c.setStrokeColor(cor)
        c.setLineWidth(lw)
        c.setDash(*(dash or []))
        c.line(x1, self.Y(y1), x2, self.Y(y2))
        c.setDash()

    def img(self, caminho, x, y, w, h):
        self.c.drawImage(caminho, x, self.Y(y, h), w, h, mask='auto')

    @staticmethod
    def chanfro(x, y, w, h, ch=10):
        return [(x + ch, y), (x + w, y), (x + w, y + h - ch), (x + w - ch, y + h), (x, y + h), (x, y + ch)]

    @staticmethod
    def hexagono(cx, cy, r):
        return [(cx + math.cos(math.radians(60 * i + 30)) * r, cy + math.sin(math.radians(60 * i + 30)) * r)
                for i in range(6)]

    @staticmethod
    def inclinado(x, y, w, h, d=5):
        return [(x + d, y), (x + w, y), (x + w - d, y + h), (x, y + h)]

    def losango(self, cx, cy, r, fill=None, stroke=None, lw=0.8):
        self.poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill, stroke=stroke, lw=lw)

    # ------------------------------------------------ peças do estilo
    def painel(self, x, y, w, h, titulo=None, nota=None, ch=10):
        k = self.k
        self.poly([(px + 4, py + 4) for px, py in self.chanfro(x, y, w, h, ch)], fill=k['bloco'])
        self.poly(self.chanfro(x, y, w, h, ch), fill=k['painel'], stroke=k['texto'], lw=1.5)
        if titulo:
            tw = pdfmetrics.stringWidth(titulo, 'Oswald', 9) + 22
            self.poly([(x + 12, y - 7), (x + 12 + tw, y - 7), (x + 4 + tw, y + 7), (x + 4, y + 7)], fill=k['texto'])
            self.txt(x + 18, y - 5.2, titulo, 9, k['fundo'])
        if nota:
            self.txt(x + w - 12, y + 3, nota, 5.8, k['texto_fraco'], al='d')

    def reticula(self, x0, y0, w, h, cor, ang=1):
        c = self.c
        c.setFillColor(cor)
        passo = 7
        for i in range(int(w / passo) + 1):
            for j in range(int(h / passo) + 1):
                t = ((i / (w / passo)) + (j / (h / passo))) / 2
                t = t if ang > 0 else 1 - t
                r = 2.6 * max(0, t - 0.25)
                if r > 0.15:
                    c.circle(x0 + i * passo + (passo / 2 if j % 2 else 0), self.Y(y0 + j * passo), r, stroke=0, fill=1)

    def velocidade(self, cx, cy, r0, r1, n, cor, seed=9):
        random.seed(seed)
        for i in range(n):
            a = math.tau * i / n + random.uniform(-0.02, 0.02)
            w = random.uniform(0.004, 0.012)
            p0 = (cx + math.cos(a) * r0 * random.uniform(0.9, 1.2), cy + math.sin(a) * r0 * random.uniform(0.9, 1.2))
            self.poly([p0, (cx + math.cos(a - w) * r1, cy + math.sin(a - w) * r1),
                       (cx + math.cos(a + w) * r1, cy + math.sin(a + w) * r1)], fill=cor)

    def cabecalho(self, titulo, sub, kanji):
        k = self.k
        self.c.setFillColor(k['fundo'])
        self.c.rect(0, 0, W, H, stroke=0, fill=1)
        self.velocidade(W - 90, 60, 40, 560, 70, alpha(k['bloco'], 0.22), seed=self.pg + 3)
        self.reticula(0, 640, 200, 202, alpha(k['bloco'], 0.45))
        self.reticula(W - 190, 0, 190, 150, alpha(k['bloco'], 0.35), -1)
        self.img(kanji_marca(kanji, 300, k['rgb']['acento'], 24), 250, 2, 80 * len(kanji), 84)
        self.poly([(0, 18), (W, 6), (W, 60), (0, 72)], fill=k['bloco'])
        self.poly([(0, 72), (W, 60), (W, 64), (0, 76)], fill=k['texto'])
        self.txt(M, 22, titulo, 29, k['osso_bloco'])
        self.txt(M + 2, 58, sub, 7.5, k['osso_bloco'])

    def rodape(self):
        self.txt(W / 2, 832, 'CICLO MALDITO  ·  R53  ·  %d/%d' % (self.pg + 1, PAGINAS), 6,
                 self.k['texto_fraco'], al='c')

    def proxima(self):
        self.rodape()
        self.c.showPage()
        self.pg += 1

    # ------------------------------------------------ campos (sempre transparentes, sobre a arte)
    def _campo(self, nome, x, y, w, h, tam, cor, negrito=False, flags='', valor='', dica='', alinh=0):
        self.c.acroForm.textfield(
            name=nome, tooltip=dica or nome, value=valor, x=x, y=self.Y(y, h), width=w, height=h,
            fontName='Helvetica-Bold' if negrito else 'Helvetica', fontSize=tam,
            borderWidth=0, borderColor=transparent, fillColor=transparent, textColor=cor,
            fieldFlags=flags, forceBorder=False, maxlen=None)   # sem o limite padrão de 100 caracteres
        self.alinhar[nome] = alinh
        if self.selando is not None and 'readOnly' not in flags:
            self.selando.append(nome)

    def entrada(self, nome, x, y, w, h, tam=8.5, alinh=0, multi=False, valor='', dica='', caixa=True, cor=None):
        if caixa:
            self.poly(self.chanfro(x, y, w, h, min(4, h / 3)), fill=self.k['tinta'], stroke=self.k['linha'], lw=0.6)
        self._campo(nome, x + 2, y + 0.5, w - 4, h - 1, tam, cor or self.k['texto'],
                    flags='multiline' if multi else '', valor=valor, dica=dica, alinh=alinh)

    def auto(self, nome, x, y, w, h, js, tam=9, dica=''):
        """Valor calculado: etiqueta clara com o número escuro."""
        self.poly(self.inclinado(x, y, w, h, min(5, h / 3)), fill=self.k['texto'])
        self._campo(nome, x + 3, y + 0.5, w - 6, h - 1, tam, self.k['fundo'], negrito=True, flags='readOnly',
                    dica=dica or 'calculado', alinh=1)
        self.calc.append((nome, JS_BASE + js))

    def aj(self, nome, x, y, w=20, h=12):
        """O ± de um valor calculado."""
        self.txt(x - 5, y + (h - 7) / 2, '±', 7, self.k['texto_fraco'])
        self.poly(self.inclinado(x, y, w, h, 3), fill=self.k['painel_alto'], stroke=self.k['linha'], lw=0.5)
        self._campo(nome, x + 2, y + 0.5, w - 4, h - 1, 7, self.k['texto'], dica='ajuste: bônus ou penalidade', alinh=1)

    def marca(self, nome, x, y, s=9, forma='losango', dica=''):
        """Caixa de marcar: desenha a forma e põe a caixa transparente por cima."""
        k = self.k
        if forma == 'losango':
            self.losango(x + s / 2, y + s / 2, s / 2, stroke=k['texto'], lw=0.8)
            estilo = 'diamond'
        else:
            self.poly([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], stroke=k['texto'], lw=0.7)
            estilo = 'check'
        # marca visível em qualquer leitor: losango/quadrado cheio, por baixo da caixa, aceso pelo cálculo
        m = 1.6
        if forma == 'losango':
            pts = [(s / 2, m), (s - m, s / 2), (s / 2, s - m), (m, s / 2)]
        else:
            pts = [(m, m), (s - m, m), (s - m, s - m), (m, s - m)]
        self.botoes.append(dict(nome='mk_' + nome, pg=self.pg, x=x, y=y, w=s, h=s, pts=pts, cor='carimbo', baixo=True))
        self.marcas.append(nome)
        self.c.acroForm.checkbox(
            name=nome, tooltip=dica or nome, checked=False, buttonStyle=estilo, x=x, y=self.Y(y, s), size=s,
            borderWidth=0, borderColor=transparent, fillColor=transparent, textColor=k['carimbo'],
            forceBorder=False, fieldFlags='')   # sem o 'obrigatório' padrão (borda vermelha no leitor)
        if self.selando is not None:
            self.selando.append(nome)

    def menu(self, nome, x, y, w, h, opcoes, valor, tam=8.5, dica=''):
        self.poly(self.chanfro(x, y, w, h, 4), fill=self.k['tinta'], stroke=self.k['linha'], lw=0.6)
        self.c.acroForm.choice(
            name=nome, tooltip=dica or nome, value=valor, options=opcoes, x=x + 1, y=self.Y(y + 0.5, h - 1),
            width=w - 2, height=h - 1, fontName='Helvetica', fontSize=tam, borderWidth=0,
            borderColor=transparent, fillColor=transparent, textColor=self.k['texto'], fieldFlags='combo')
        if self.selando is not None:
            self.selando.append(nome)

    def barra(self, prefixo, x, y, w, h, n, cor):
        """Barra segmentada: contorno fixo; os segmentos cheios são botões que o cálculo mostra/esconde."""
        passo = w / n
        for i in range(n):
            sx = x + i * passo
            pts = [(sx + 3, y), (sx + passo - 1, y), (sx + passo - 4, y + h), (sx, y + h)]
            self.poly(pts, fill=self.k['painel_alto'], stroke=self.k['linha'], lw=0.4)
            self.botoes.append(dict(nome='%s%d' % (prefixo, i + 1), pg=self.pg, x=sx, y=y, w=passo, h=h,
                                    pts=[(px - sx, py - y) for px, py in pts], cor=cor))
        self.segmentos[prefixo] = n

    @contextmanager
    def selado(self, nome, x, y, w, h, condicao, texto):
        """Tudo o que for desenhado aqui dentro fica travado até a condição valer."""
        antes, self.selando = self.selando, []
        yield
        campos, self.selando = self.selando, antes
        caminho = os.path.join(TMP, '%s-%s-%s.png' % (nome, self.nome_paleta, self.modo))
        imagem_selo(w, h, self.k, texto).save(caminho)
        self.botoes.append(dict(nome=nome, pg=self.pg, x=x, y=y, w=w, h=h, imagem=caminho))
        self.selos.append((nome, condicao, campos))
        self.travados.update(campos)

    # ================================================== página 1 · personagem
    def pagina1(self):
        k = self.k
        self.cabecalho('CICLO MALDITO', 'FICHA DE PERSONAGEM  ·  呪術師', '呪術師')

        # --- feiticeiro
        y = 92
        self.painel(M, y, CW, 72, 'FEITICEIRO')
        x = M + 12
        for rot, nome, w, valor in [('NOME', 'nome', 150, ''), ('JOGADOR', 'jogador', 100, ''),
                                    ('ORIGEM', 'origem', 110, ''), ('NÍVEL', 'nivel', 40, '2'),
                                    ('GRAU', 'grau', 40, '4'), ('XP', 'xp', 47, '')]:
            self.rot(x, y + 9, rot)
            curto = nome in ('nivel', 'grau', 'xp')
            self.entrada(nome, x, y + 17, w, 16, tam=10 if not curto else 10, alinh=1 if curto else 0, valor=valor)
            x += w + 8
        x = M + 12
        self.rot(x, y + 38, 'CAMINHO')
        self.menu('caminho', x, y + 46, 110, 16, ['-'] + list(CAMINHOS), '-')
        x += 118
        self.rot(x, y + 38, 'TRILHA')
        self.entrada('trilha', x, y + 46, 110, 16)
        x += 118
        self.rot(x, y + 38, 'ROTA')
        self.entrada('rota', x, y + 46, 150, 16, dica='Técnica inata, Sem Técnica ou Técnica Marcial')
        x += 158
        self.rot(x, y + 38, 'TR FÍSICO')
        self.menu('tr_fis_atr', x, y + 46, 60, 16, ['-', 'FOR', 'DES'], '-', dica='escolhido na criação e fixo')
        x += 68
        self.rot(x, y + 38, 'ATRIB. TÉCNICA')
        self.menu('tec_atr', x, y + 46, W - M - 12 - x, 16, ['-', 'FOR', 'DES', 'CON', 'INT', 'ESS'], '-')

        # --- atributos em hexágono
        cy = 205
        for i, (sg, nome) in enumerate(ATRIBUTOS):
            cx = M + (i + 0.5) * CW / 5
            self.poly([(px + 4, py + 4) for px, py in self.hexagono(cx, cy, 31)], fill=k['bloco'])
            self.poly(self.hexagono(cx, cy, 31), fill=k['painel'], stroke=k['texto'], lw=1.8)
            self.poly(self.hexagono(cx, cy, 25), stroke=k['linha'], lw=0.6)
            self._campo('atr_' + sg, cx - 20, cy - 15, 40, 26, 22, k['texto'], negrito=True, alinh=1,
                        dica='%s: de 0 a 6 (na criação, até 3)' % nome.title())
            self.poly(self.inclinado(cx - 22, cy + 25, 44, 12, 4), fill=k['texto'])
            self.txt(cx, cy + 27, SIGLA[sg], 7.5, k['fundo'], al='c')
            self.txt(cx + 0.5, cy + 41, nome, 6, k['texto_fraco'], al='c')

        # --- progressão do nível
        y = 268
        self.painel(M, y, CW, 34, 'PROGRESSÃO')
        itens = [('maestria', 'MAESTRIA', tabela('T', MAESTRIA) + "event.value=s(T[niv()-1]+n('maestria_aj'));"),
                 ('espacos', 'ESPAÇOS', tabela('T', ESPACOS) + "event.value=T[niv()-1]+n('espacos_aj');"),
                 ('classe0', 'CLASSE 0', tabela('T', CLASSE_0) + "event.value=T[niv()-1]+n('classe0_aj');"),
                 ('classe_max', 'CLASSE MÁX.', tabela('T', CLASSE_MAX) + "event.value=T[niv()-1]+n('classe_max_aj');"),
                 ('refino', 'REFINO', tabela('T', REFINO) + "event.value=T[niv()-1]+n('refino_aj');")]
        for i, (nome, rot, js) in enumerate(itens):
            x = M + 12 + i * (CW - 24) / 5
            self.rot(x, y + 14, rot)
            self.auto(nome, x + 40, y + 11, 32, 14, js, 9)
            self.aj(nome + '_aj', x + 80, y + 12, w=18)

        # --- recursos
        y = 318
        self.painel(M, y, CW, 84, 'RECURSOS')
        for xx, r in [(318, 'ATUAL'), (366, 'MÁX.'), (408, '±'), (432, 'TEMP.')]:
            self.rot(xx, y + 7, r)
        caminhos = ','.join("'%s':[%d,%d,%d]" % (nm, *v) for nm, v in CAMINHOS.items())
        recursos = [
            ('vida', 'VIDA', 'carimbo',
             "var C={%s};var q=C[t('caminho')];if(!q){event.value='-';}else{var con=n('atr_con'),l=niv();"
             "event.value=(q[0]+con)+(q[1]+con)*(l-1)+n('vida_aj');}" % caminhos),
            ('pe', 'ENERGIA', 'acento',
             "var C={%s};var q=C[t('caminho')];if(!q){event.value='-';}else{event.value=q[2]*niv()+n('pe_aj');}"
             % caminhos),
            ('integ', 'INTEGRIDADE', 'regua', "event.value=20+(n('atr_ess')+5)*(niv()-1)+n('integ_aj');"),
        ]
        for i, (nome, rot, cor, js) in enumerate(recursos):
            yy = y + 16 + i * 22
            self.txt(M + 12, yy + 2, rot, 9, k['texto'])
            self.barra('seg_%s_' % nome, M + 82, yy + 1, 206, 13, 16, cor)
            self.entrada(nome + '_atual', 314, yy - 1, 38, 17, tam=11, alinh=1)
            self.txt(356, yy, '/', 12, k['texto_fraco'])
            self.auto(nome + '_max', 364, yy - 1, 38, 17, js, 11)
            self.aj(nome + '_aj', 410, yy + 1)
            if nome == 'vida':
                self.entrada('vida_temp', 432, yy - 1, 30, 17, tam=10, alinh=1)
        x = 476
        self.rot(x, y + 18, 'SEQUELAS')
        for i in range(3):
            self.marca('sequela_%d' % (i + 1), x + 46 + i * 14, y + 15, 10)
        self.rot(x, y + 40, 'EXAUSTÃO')
        self.entrada('exaustao', x + 46, y + 36, 30, 15, alinh=1)
        self.rot(x, y + 62, 'CONDIÇÕES')
        self.entrada('condicoes', x + 46, y + 58, W - M - 10 - x - 46, 15, tam=7)

        # --- combate
        y = 418
        self.painel(M, y, CW, 112, 'COMBATE')
        cx, cy = 70, y + 50
        self.losango(cx + 4, cy + 4, 38, fill=k['carimbo'])
        self.losango(cx, cy, 38, fill=k['tinta'], stroke=k['texto'], lw=1.8)
        self._campo('defesa', cx - 22, cy - 18, 44, 24, 20, k['texto'], negrito=True, flags='readOnly', alinh=1,
                    dica='calculado')
        self.calc.append(('defesa', None))   # entra na ordem depois da proteção (abaixo)
        self.txt(cx, cy + 9, 'DEFESA', 6.5, k['texto_fraco'], al='c')
        self.aj('defesa_aj', cx + 24, cy + 30)
        # linha A: proteção e defesa
        x0, ya = 128, y + 12
        self.rot(x0, ya, 'PROT. TRAJE')
        self.entrada('prot_equip', x0, ya + 9, 52, 15, alinh=1,
                     dica='vazio = sem Traje/Revestimento: usa Cobrir-se de Energia (1 + Refino/3)')
        self.rot(x0 + 60, ya, 'ESCUDO')
        self.entrada('escudo', x0 + 60, ya + 9, 30, 15, alinh=1)
        self.rot(x0 + 98, ya, 'TETO DES')
        self.entrada('teto_des', x0 + 98, ya + 9, 30, 15, alinh=1, dica='vazio = sem teto')
        self.rot(x0 + 140, ya, 'PROTEÇÃO')
        self.auto('protecao', x0 + 140, ya + 9, 32, 15,
                  "var b=vazio('prot_equip')?1+Math.floor(n('refino')/3):n('prot_equip');"
                  "event.value=b+n('escudo')+n('protecao_aj');", 9)
        self.aj('protecao_aj', x0 + 180, ya + 10.5)
        self.calc.remove(('defesa', None))
        self.calc.append(('defesa', JS_BASE +
                          "var de=n('atr_des');if(!vazio('teto_des'))de=Math.min(de,n('teto_des'));"
                          "event.value=10+de+n('protecao')+n('defesa_aj');"))
        self.rot(x0 + 216, ya, 'BLOQUEAR')
        self.auto('bloquear', x0 + 216, ya + 9, 52, 15,
                  "var b=n('defesa')-11+n('bloquear_aj');event.value='2d10 '+(b>=0?'+ '+b:'- '+(-b));", 8.5)
        self.aj('bloquear_aj', x0 + 276, ya + 10.5)
        self.rot(x0 + 312, ya, 'INICIATIVA')
        self.auto('iniciativa', x0 + 312, ya + 9, 34, 15, "event.value=s(n('atr_des')+n('iniciativa_aj'));", 9)
        self.aj('iniciativa_aj', x0 + 354, ya + 10.5)
        self.rot(x0 + 388, ya, 'DESLOC.')
        self.auto('deslocamento', x0 + 388, ya + 9, 34, 15, "event.value=(9+n('desloc_aj'))+' m';", 8.5)
        self.aj('desloc_aj', x0 + 430, ya + 10.5, w=14)
        # linha B: ataques e carga
        yb = y + 44
        ataques = [
            ('cd_tec', 'CD DA TÉCNICA', "var a=t('tec_atr');if(a==='-'||a===''){event.value='-';}else{"
                                         "event.value=8+n('atr_'+a.toLowerCase())+n('maestria')+n('cd_tec_aj');}"),
            ('atq_tec', 'ATAQUE DA TÉCNICA', "var a=t('tec_atr');if(a==='-'||a===''){event.value='-';}else{"
                                              "event.value=s(n('atr_'+a.toLowerCase())+n('maestria')+n('atq_tec_aj'));}"),
            ('atq_cac', 'CORPO A CORPO', "event.value=s(n('atr_for')+n('maestria')+n('atq_cac_aj'));"),
            ('atq_dist', 'À DISTÂNCIA', "event.value=s(n('atr_des')+n('maestria')+n('atq_dist_aj'));"),
            ('carga', 'CARGA', "event.value=5+n('atr_for')+n('carga_aj');"),
        ]
        for i, (nome, rot, js) in enumerate(ataques):
            x = x0 + i * 89
            self.rot(x, yb, rot)
            self.auto(nome, x, yb + 9, 40, 16, js, 10)
            self.aj(nome + '_aj', x + 48, yb + 11)
        # linha C: morrendo
        yc = y + 76
        morre = [('morr_aguentar', 'AGUENTAR', "event.value=Math.ceil(n('vida_max')/4)+n('morr_aguentar_aj');"),
                 ('morr_ins1', 'INSISTIR 1ª', "event.value=Math.min(Math.ceil(n('vida_max')/3),15*n('classe_max'))"
                                              "+n('morr_ins1_aj');"),
                 ('morr_ins2', 'INSISTIR 2ª+', "event.value=Math.min(Math.ceil(n('vida_max')/2),15*n('classe_max'))"
                                               "+n('morr_ins2_aj');")]
        for i, (nome, rot, js) in enumerate(morre):
            x = x0 + i * 89
            self.rot(x, yc, ('MORRENDO · ' if i == 0 else '') + rot)
            self.auto(nome, x, yc + 9, 40, 16, js, 9.5)
            self.aj(nome + '_aj', x + 48, yc + 11)
        x = x0 + 3 * 89
        self.rot(x, yc, 'JANELA')
        self.auto('morr_janela', x, yc + 9, 76, 16,
                  "var q=(c('sequela_1')?1:0)+(c('sequela_2')?1:0)+(c('sequela_3')?1:0);"
                  "var r=3-q+n('morr_janela_aj');"
                  "event.value=(q>=3||r<=0)?'Derrotado':r+(r==1?' rodada':' rodadas');", 8)
        self.aj('morr_janela_aj', x + 84, yc + 11, w=18)

        # --- perícias, resistências e ofícios
        y = 546
        self.painel(M, y, CW, 282, 'PERÍCIAS  ·  RESISTÊNCIAS  ·  OFÍCIOS')
        col = (CW - 24 - 16) / 2
        rh = 14.1
        for c in range(2):
            x = M + 12 + c * (col + 16)
            for xx, r in [(x, 'T'), (x + col - 96, 'ESP.'), (x + col - 70, '±'), (x + col - 34, 'TOTAL')]:
                self.rot(xx, y + 9, r)
        for i, (nome, atr) in enumerate(PERICIAS):
            s_ = slug(nome)
            x = M + 12 + (i // 12) * (col + 16)
            yy = y + 18 + (i % 12) * rh
            self.marca('per_%s_t' % s_, x, yy + 1, 9, dica='treinada: soma a maestria')
            self.txt(x + 14, yy + 1.5, nome, 8.3, k['texto'], 'Helvetica')
            self.txt(x + col - 116, yy + 2.5, SIGLA[atr], 6, k['texto_fraco'])
            self.marca('per_%s_e' % s_, x + col - 94, yy + 2, 7, 'quadrado', 'especialista: + metade da maestria')
            self.aj('per_%s_aj' % s_, x + col - 74, yy + 0.5, w=22)
            self.auto('per_' + s_, x + col - 42, yy, 42, 12,
                      "var m=n('maestria'),v=n('atr_%s');if(c('per_%s_t')){v+=m;if(c('per_%s_e'))v+=Math.floor(m/2);}"
                      "event.value=s(v+n('per_%s_aj'));" % (atr, s_, s_, s_), 8.5)
        # resistências
        yr = y + 18 + 12 * rh + 5
        x = M + 12
        self.txt(x, yr, 'TESTES DE RESISTÊNCIA', 7.5, k['acento'])
        trs = [('fis', 'Físico', None), ('vig', 'Vigor', 'con'), ('itl', 'Intelecto', 'int'), ('esp', 'Espírito', 'ess')]
        for i, (sg, nome, atr) in enumerate(trs):
            yy = yr + 12 + i * rh
            self.marca('tr_%s_t' % sg, x, yy + 1, 9, dica='treinado')
            self.txt(x + 14, yy + 1.5, nome, 8.3, k['texto'], 'Helvetica')
            self.txt(x + col - 116, yy + 2.5, 'FOR/DES' if atr is None else SIGLA[atr], 6, k['texto_fraco'])
            self.aj('tr_%s_aj' % sg, x + col - 74, yy + 0.5, w=22)
            if atr is None:
                js = ("var a=t('tr_fis_atr');if(a==='-'||a===''){event.value='-';}else{"
                      "var v=n('atr_'+a.toLowerCase());if(c('tr_fis_t'))v+=n('maestria');event.value=s(v+n('tr_fis_aj'));}")
            else:
                js = "var v=n('atr_%s');if(c('tr_%s_t'))v+=n('maestria');event.value=s(v+n('tr_%s_aj'));" % (atr, sg, sg)
            self.auto('tr_' + sg, x + col - 42, yy, 42, 12, js, 8.5)
        self.rot(x, yr + 12 + 4 * rh + 1, 'RESISTÊNCIAS E IMUNIDADES')
        self.entrada('resistencias', x + 96, yr + 12 + 4 * rh - 2, col - 96, 13, tam=7)
        # ofícios
        x = M + 12 + col + 16
        self.txt(x, yr, 'OFÍCIOS', 7.5, k['acento'])
        sub = (col - 8) / 2
        for i, (nome, atr) in enumerate(OFICIOS):
            s_ = slug(nome)
            xx = x + (i // 6) * (sub + 8)
            yy = yr + 12 + (i % 6) * 13
            self.marca('of_%s_t' % s_, xx, yy + 1, 8)
            self.txt(xx + 11, yy + 1.5, nome, 7, k['texto'], 'Helvetica')
            self.txt(xx + sub - 60, yy + 2.5, SIGLA[atr], 5.5, k['texto_fraco'])
            self.aj('of_%s_aj' % s_, xx + sub - 44, yy + 0.5, w=15, h=11)
            self.auto('of_' + s_, xx + sub - 26, yy, 26, 11,
                      "if(!c('of_%s_t')){event.value='-';}else{"
                      "event.value=s(n('atr_%s')+n('maestria')+n('of_%s_aj'));}" % (s_, atr, s_), 7.5)
        self.proxima()

    # ================================================== página 2 · técnica
    def pagina2(self):
        k = self.k
        self.cabecalho('TÉCNICA', 'FUNDAMENTO  ·  TALENTOS  ·  APTIDÕES  ·  術式', '術式')
        y = 94
        self.painel(M, y, CW, 146, 'FUNDAMENTO')
        x = M + 12
        self.rot(x, y + 9, 'NOME DA TÉCNICA')
        self.entrada('tec_nome', x, y + 17, 190, 18, tam=11)
        self.rot(x + 198, y + 9, 'TIPOS DE DANO')
        self.entrada('tec_dano', x + 198, y + 17, 120, 18)
        self.rot(x + 326, y + 9, 'SELO')
        self.entrada('tec_selo', x + 326, y + 17, CW - 24 - 326, 18, tam=7.5)
        meia = (CW - 24 - 12) / 2
        self.rot(x, y + 42, 'REGRA')
        self.entrada('tec_regra', x, y + 50, meia, 36, tam=7.8, multi=True)
        self.rot(x + meia + 12, y + 42, 'DESCRIÇÃO E EXPRESSÃO')
        self.entrada('tec_descricao', x + meia + 12, y + 50, meia, 36, tam=7.8, multi=True)
        self.rot(x, y + 94, 'FAMÍLIAS LIVRES')
        for i in range(2):
            xx = x + i * 92
            self.poly(self.inclinado(xx, y + 103, 86, 17, 5), fill=k['texto'])
            self._campo('fam_livre_%d' % (i + 1), xx + 5, y + 103.5, 76, 16, 8.5, k['fundo'], negrito=True, alinh=1)
        self.rot(x + 200, y + 94, 'FAMÍLIAS FECHADAS')
        for i in range(3):
            xx = x + 200 + i * 108
            self.poly(self.inclinado(xx, y + 103, 102, 17, 5), fill=k['painel_alto'], stroke=k['linha'], lw=0.5)
            self.linha(xx + 2, y + 118, xx + 12, y + 105, k['carimbo'], 1.2)
            self._campo('fam_fechada_%d' % (i + 1), xx + 14, y + 103.5, 84, 16, 8.5, k['texto'], negrito=True, alinh=1)

        # --- espaços do repertório
        y = 258
        self.painel(M, y, CW, 60, 'ESPAÇOS')
        self.barra('seg_esp_', M + 12, y + 12, 360, 16, 24, 'carimbo')
        js_usados = ("var f=0;for(var i=1;i<=%d;i++){if(!vazio('r'+i+'_nome'))f++;}"
                     "var tl=0;for(var j=1;j<=5;j++)tl+=n('tal_'+j+'_ce');"
                     "var D={%s};var ex=D[t('exp_degrau')]||0;" % (
                         N_CARTOES, ','.join("'%s':%d" % kv for kv in DEGRAUS.items())))
        self.auto('esp_usados', M + 384, y + 11, 104, 19,
                  js_usados + "var u=f+tl+ex+n('esp_entidades')+n('esp_usados_aj');var l=n('espacos');"
                  "event.value=u+' de '+l+(u>l?'  ACIMA':'');", 11)
        self.aj('esp_usados_aj', M + 496, y + 14, w=24)
        yl = y + 37
        for i, (nome, rot, js) in enumerate([
                ('esp_feiticos', 'FICHAS', js_usados + "event.value=f;"),
                ('esp_talentos', 'TALENTOS', js_usados + "event.value=tl;"),
                ('esp_expansao', 'EXPANSÃO', js_usados + "event.value=ex;")]):
            x = M + 12 + i * 92
            self.rot(x, yl + 3, rot)
            self.auto(nome, x + 44, yl, 30, 13, js, 8)
        x = M + 12 + 3 * 92
        self.rot(x, yl + 3, 'ENTIDADES')
        self.entrada('esp_entidades', x + 44, yl, 30, 13, alinh=1, dica='espaços trocados por entidades')

        # --- talentos pagos
        y = 336
        self.painel(M, y, CW, 186, 'TALENTOS PAGOS', 'MÁX. 5  ·  CE = ESPAÇOS')
        for i in range(N_TALENTOS):
            yy = y + 12 + i * 28.5
            cx = M + 24
            self.poly(self.hexagono(cx, yy + 11, 11.5), fill=k['carimbo'], stroke=k['texto'], lw=1)
            nome = 'tal_%d' % (i + 1)
            if i < 5:
                self._campo(nome + '_ce', cx - 8, yy + 4, 16, 14, 10, k['texto'], negrito=True, alinh=1,
                            dica='Categoria de Efeito: 1, 2 ou 3 (= espaços)')
            else:
                self.txt(cx, yy + 6, '4', 10, k['texto'], 'Helvetica-Bold', 'c')
            self.entrada(nome + '_nome', M + 44, yy, 200, 14, tam=9)
            self.entrada(nome + '_efeito', M + 44, yy + 15, CW - 56, 11, tam=7, caixa=False)
            self.linha(M + 44, yy + 26, W - M - 12, yy + 26, k['linha'], 0.4, [0.5, 1.5])
            if i == 5:
                self.rot(M + 252, yy + 4, 'CE 4  ·  RESTRIÇÃO CORPORAL')

        # --- aptidões e classe 0
        y = 540
        hw = (CW - 14) / 2
        self.painel(M, y, hw, 286, 'APTIDÕES')
        for i in range(N_APTIDOES):
            yy = y + 13 + i * 22.5
            self.txt(M + 12, yy + 3, '%02d' % (i + 1), 7.5, k['bloco'])
            valor = ['Cobrir-se de Energia', 'Canalizar Energia'][i] if i < 2 else ''
            self.entrada('apt_%d' % (i + 1), M + 30, yy, hw - 42 - (46 if i < 2 else 0), 15, tam=8.5,
                         valor=valor, caixa=False)
            self.linha(M + 30, yy + 15, M + hw - 12, yy + 15, k['linha'], 0.4, [0.5, 1.5])
            if i < 2:
                self.poly(self.inclinado(M + hw - 52, yy + 2, 40, 11, 3), fill=k['painel_alto'])
                self.txt(M + hw - 32, yy + 4, 'grátis', 6, k['texto'], al='c')
        x2 = M + hw + 14
        self.painel(x2, y, hw, 286, 'CLASSE 0')
        for i in range(5):
            yy = y + 12 + i * 54
            def vaga():
                self.entrada('c0_%d_nome' % (i + 1), x2 + 12, yy + 10, hw - 24, 15, tam=9)
                self.entrada('c0_%d_efeito' % (i + 1), x2 + 12, yy + 27, hw - 24, 22, tam=7, multi=True)
            if CLASSE0_ABRE[i]:
                lv = CLASSE0_ABRE[i]
                with self.selado('selo_c0_%d' % (i + 1), x2 + 6, yy - 2, hw - 12, 54,
                                 'ig||L>=%d' % lv, 'NÍVEL %d' % lv):
                    vaga()
            else:
                vaga()
        self.proxima()

    # ================================================== páginas 3 e 4 · repertório
    def ficha_catalogo(self, x, y, w, h, n):
        k = self.k
        p = 'r%d_' % n
        self.poly([(x + 4, y + 4), (x + w + 4, y + 4), (x + w + 4, y + h + 4), (x + 4, y + h + 4)], fill=k['bloco'])
        self.c.setFillColor(k['papel'])
        self.c.setStrokeColor(k['texto'])
        self.c.setLineWidth(1.2)
        self.c.rect(x, self.Y(y, h), w, h, stroke=1, fill=1)
        self.c.setFillColor(k['fundo'])
        self.c.circle(x + w / 2, self.Y(y + h - 9), 4, stroke=1, fill=1)
        self.poly([(x + w - 58, y), (x + w - 52, y - 9), (x + w - 6, y - 9), (x + w, y)], fill=k['bloco'])
        self.txt(x + w - 29, y - 7.5, 'Nº %02d' % n, 7, k['osso_bloco'], al='c')
        self._campo(p + 'nome', x + 6, y + 4, w - 128, 18, 11, k['texto'], negrito=True, dica='nome da aplicação')
        self.rot(x + w - 118, y + 9, 'CLASSE')
        self.entrada(p + 'classe', x + w - 92, y + 6, 18, 14, tam=9, alinh=1)
        self.rot(x + w - 70, y + 9, 'PE')
        self.auto(p + 'pe', x + w - 60, y + 6, 26, 14,
                  "if(vazio('%sclasse')){event.value='';}else{var cl=n('%sclasse');"
                  "event.value=(cl<=0?0:3*cl)+n('%spe_aj');}" % (p, p, p), 9)
        self.aj(p + 'pe_aj', x + w - 26, y + 7, w=18)
        self.linha(x + 6, y + 26, x + w - 6, y + 26, k['linha'], 1.2)
        self.linha(x + 6, y + 28.5, x + w - 6, y + 28.5, k['linha'], 0.4)
        linhas = [('AÇÃO', 'acao'), ('ALCANCE', 'alcance'), ('ACERTO', 'acerto'), ('TR', 'tr'),
                  ('DANO / CURA', 'dano'), ('MELHORIAS', 'melhorias'), ('RESTRIÇÕES', 'restricoes')]
        for j, (rot, ch) in enumerate(linhas):
            yy = y + 33 + j * 14
            self.rot(x + 8, yy + 2, rot, 5.8)
            self._campo(p + ch, x + 60, yy - 1, w - 68, 12.5, 7.6, k['texto'])
            self.linha(x + 60, yy + 11, x + w - 8, yy + 11, k['linha'], 0.4, [0.5, 1.5])
        yy = y + 33 + 7 * 14 + 3
        self.rot(x + 8, yy, 'COMO É', 5.8)
        for j in range(5):
            self.linha(x + 8, yy + 18 + j * 11, x + w - 8, yy + 18 + j * 11, k['linha'], 0.3, [0.5, 1.5])
        self._campo(p + 'como', x + 6, yy + 8, w - 12, h - (yy - y) - 20, 7.3, k['texto'], flags='multiline')

    def pagina_repertorio(self, inicio):
        self.cabecalho('REPERTÓRIO', 'FEITIÇOS  ·  MANEJOS  ·  KATAS  ·  術式', '術式')
        gw, gh = (CW - 14) / 2, 226
        for i in range(6):
            x = M + (i % 2) * (gw + 14)
            y = 100 + (i // 2) * (gh + 16)
            self.ficha_catalogo(x, y, gw, gh, inicio + i)
        self.proxima()

    # ================================================== página 5 · poderes avançados
    def pagina5(self):
        k = self.k
        self.cabecalho('PODERES AVANÇADOS', 'EXPANSÃO DE DOMÍNIO  ·  LIBERAÇÃO MÁXIMA  ·  TÉCNICA MÁXIMA  ·  領域展開', '領域展開')
        self.marca('ignorar_selos', W - M - 170, 80, 8, 'quadrado', 'abre todos os selos, para exceções da campanha')
        self.rot(W - M - 158, 81, 'IGNORAR SELOS')

        # --- expansão de domínio
        y = 96
        self.painel(M, y, CW, 314, 'EXPANSÃO DE DOMÍNIO')
        cw = CW - 24 - 166
        x = M + 12
        with self.selado('selo_exp', M + 3, y + 3, CW - 6, 308, 'ig||(L>=10&&R>=4)', 'NÍVEL 10  ·  REFINO 4'):
            self.rot(x, y + 9, 'DEGRAU')
            self.menu('exp_degrau', x, y + 17, 130, 17, ['-'] + list(DEGRAUS), '-')
            for j, linha_ in enumerate(['INCOMPLETA  ·  2 espaços  ·  nível 10, refino 4',
                                        'COMPLETA  ·  3 espaços  ·  nível 14, refino 5',
                                        'SEM BARREIRAS  ·  5 espaços  ·  refino 10, Ocultismo especialista']):
                self.rot(x + 140, y + 12 + j * 9, linha_, 5.8)
            self.rot(x, y + 44, 'NOME DO DOMÍNIO')
            self.entrada('exp_nome', x, y + 52, cw, 19, tam=12)
            self.rot(x, y + 78, 'ACERTO')
            self.entrada('exp_acerto', x, y + 86, cw, 46, tam=7.6, multi=True)
            self.rot(x, y + 140, 'TIPO DE DANO')
            self.entrada('exp_tipo', x, y + 148, cw / 2 - 4, 15, tam=8)
            self.rot(x + cw / 2 + 4, y + 140, 'ALVOS')
            self.entrada('exp_alvos', x + cw / 2 + 4, y + 148, cw / 2 - 4, 15, tam=8)
            self.rot(x, y + 172, 'EFEITO')
            self.entrada('exp_efeito', x, y + 180, cw, 46, tam=7.6, multi=True)
            self.rot(x, y + 234, 'APARÊNCIA')
            self.entrada('exp_aparencia', x, y + 242, cw, 30, tam=7.6, multi=True)
            self.rot(x, y + 280, 'ABRIR: AÇÃO COMPLETA E SELO  ·  AO TERMINAR: RESCALDO (SÓ CLASSE 0 ATÉ O FIM DA CENA)', 5.6)
            xs = W - M - 12 - 150
            base = "var g=t('exp_degrau');var C=n('classe_max'),R=n('refino');if(g==='-'||g===''){event.value='-';}else{"
            stats = [
                ('exp_abertura', 'ABERTURA', '6 × maior Classe em PE', "event.value=(6*C+n('exp_abertura_aj'))+' PE';}"),
                ('exp_raio', 'RAIO', '1,5 m × refino (Incompleta até 7,5 m)',
                 "var r=1.5*R;if(g==='Incompleta')r=Math.min(r,7.5);event.value=br(r+n('exp_raio_aj'))+' m';}"),
                ('exp_duracao', 'DURAÇÃO', 'metade do refino, no mínimo 1',
                 "var q=Math.max(1,Math.floor(R/2))+n('exp_duracao_aj');event.value=q+(q==1?' turno':' turnos');}"),
                ('exp_desconto', 'DESCONTO', 'refino ÷ 3 (Incompleta) ou ÷ 2',
                 "var q=(g==='Incompleta'?Math.floor(R/3):Math.floor(R/2))+n('exp_desconto_aj');event.value='-'+q+' PE';}"),
                ('exp_barreira', 'BARREIRA', '50 × metade do refino',
                 "if(g==='Incompleta'){event.value='sem barreira';}else{"
                 "event.value=(50*Math.floor(R/2)+n('exp_barreira_aj'))+' PV';}}"),
                ('exp_dados', 'ACERTO', '2 × maior Classe em d8 (Livre: ±)',
                 "event.value=(2*C+n('exp_dados_aj'))+'d8';}"),
            ]
            for i, (nome, rot, nota, js) in enumerate(stats):
                yy = y + 10 + i * 49
                self.rot(xs, yy, rot)
                self.auto(nome, xs, yy + 8, 112, 19, base + js, 11, dica=nota)
                self.aj(nome + '_aj', xs + 124, yy + 11, w=26)

        # --- liberações máximas
        y = 428
        self.painel(M, y, CW, 166, 'LIBERAÇÕES MÁXIMAS', 'CLASSE 3+  ·  AÇÃO COMPLETA')
        cw3 = (CW - 24 - 20) / 3
        for i, nv in enumerate(LIBERACOES):
            x = M + 12 + i * (cw3 + 10)
            p = 'lib%d_' % (i + 1)
            self.poly(self.chanfro(x, y + 12, cw3, 146, 8), fill=k['tinta'], stroke=k['linha'], lw=0.6)
            with self.selado('selo_lib%d' % (i + 1), x + 1, y + 13, cw3 - 2, 144, 'ig||L>=%d' % nv,
                             'NÍVEL %d' % nv):
                self.txt(x + 8, y + 18, 'NÍVEL %d' % nv, 7, k['acento'])
                self._campo(p + 'nome', x + 6, y + 27, cw3 - 12, 15, 10, k['texto'], negrito=True, dica='nome da Liberação')
                self.linha(x + 8, y + 42, x + cw3 - 8, y + 42, k['linha'], 0.5)
                self.rot(x + 8, y + 48, 'CLASSE')
                self.entrada(p + 'classe', x + 8, y + 56, 24, 14, alinh=1)
                self.rot(x + 40, y + 48, 'PE')
                self.auto(p + 'pe', x + 40, y + 56, 34, 14,
                          "if(vazio('%sclasse')){event.value='';}else{"
                          "event.value=Math.ceil(4.5*n('%sclasse'))+n('%spe_aj');}" % (p, p, p), 9)
                self.aj(p + 'pe_aj', x + 80, y + 57, w=16)
                self.rot(x + 104, y + 48, 'DANO EXTRA')
                self.auto(p + 'dano', x + 104, y + 56, 34, 14,
                          "if(vazio('%sclasse')){event.value='';}else{"
                          "event.value='+'+(n('%sclasse')+n('%sdano_aj'))+'d8';}" % (p, p, p), 8.5)
                self.aj(p + 'dano_aj', x + 144, y + 57, w=16)
                self.rot(x + 8, y + 78, 'PREÇO')
                for j, pr in enumerate(['Vazio', 'Sangue', 'Peso']):
                    self.marca(p + slug(pr), x + 8 + j * 50, y + 87, 8)
                    self.txt(x + 19 + j * 50, y + 87, pr, 7, k['texto'], 'Helvetica')
                self.rot(x + 8, y + 101, 'MONTAGEM E EFEITO')
                self.entrada(p + 'efeito', x + 8, y + 109, cw3 - 16, 44, tam=7, multi=True)

        # --- técnica máxima
        y = 612
        self.painel(M, y, CW, 214, 'TÉCNICA MÁXIMA', 'AÇÃO COMPLETA  ·  1 POR CENA')
        x = M + 12
        with self.selado('selo_tm', M + 3, y + 3, CW - 6, 208, 'ig||L>=17', 'NÍVEL 17'):
            faixa = "var l=niv();var f=l>=26?2:(l>=21?1:(l>=17?0:-1));if(f<0){event.value='-';}else{"
            for j, (nome, rot, js) in enumerate([
                    ('tm_dados', 'DADOS', "event.value=([24,28,32][f]+n('tm_dados_aj'))+'d8';}"),
                    ('tm_pontos', 'PONTOS', "event.value=[8,12,16][f]+n('tm_pontos_aj');}"),
                    ('tm_pe', 'PE', "event.value=5*n('classe_max')+n('tm_pe_aj');}")]):
                xx = x + j * 116
                self.rot(xx, y + 10, rot)
                self.auto(nome, xx, y + 18, 70, 19, faixa + js, 11)
                self.aj(nome + '_aj', xx + 80, y + 21, w=24)
            xx = x + 3 * 116
            self.rot(xx, y + 10, 'FUNÇÃO')
            for j, f in enumerate(['dano', 'cura', 'utilidade']):
                self.marca('tm_' + f, xx + j * 50, y + 23, 9)
                self.txt(xx + 12 + j * 50, y + 23.5, f, 7.5, k['texto'], 'Helvetica')
            self.rot(x, y + 46, 'NOME')
            self.entrada('tm_nome', x, y + 54, 200, 17, tam=10)
            self.rot(x + 210, y + 46, 'FORMA')
            self.entrada('tm_forma', x + 210, y + 54, CW - 24 - 210, 17, tam=8)
            self.rot(x, y + 78, 'MELHORIAS (ATÉ 4)')
            mw = (CW - 24 - 18) / 4
            for j in range(4):
                self.entrada('tm_melhoria_%d' % (j + 1), x + j * (mw + 6), y + 86, mw, 15, tam=7.5)
            self.rot(x, y + 108, 'COMO É')
            self.entrada('tm_como', x, y + 116, CW - 24, 88, tam=7.6, multi=True)
        self.proxima()

    def foto(self, x, y, w, h):
        """Moldura de foto (canto cortado, 顔). No Acrobat, clicar importa uma imagem."""
        k = self.k
        ch = 14
        pts = [(x, y + ch), (x + ch, y), (x + w, y), (x + w, y + h - ch), (x + w - ch, y + h), (x, y + h)]
        self.poly([(px + 3, py + 3) for px, py in pts], fill=k['bloco'])
        self.poly(pts, fill=k['tinta'], stroke=k['texto'], lw=1.2)
        self.txt(x + w / 2, y + h / 2 - 16, 'FOTO', 9, k['texto_fraco'], al='c')
        self.txt(x + w / 2, y + h / 2 - 3, '顔', 16, k['texto_fraco'], 'Yuji', 'c')
        self.botoes.append(dict(nome='foto', pg=self.pg, x=x + 3, y=y + 3, w=w - 6, h=h - 6, foto=True))

    # ================================================== página 6 · quem é
    def pagina6(self):
        k = self.k
        self.cabecalho('PERFIL', 'APARÊNCIA  ·  HISTÓRIA  ·  ORIGEM  ·  EQUIPAMENTO  ·  人物', '人物')
        hw = (CW - 14) / 2
        y = 94
        for i, (nome, titulo) in enumerate([('aparencia', 'APARÊNCIA E PERSONALIDADE'),
                                            ('historia', 'HISTÓRIA E MOTIVAÇÃO')]):
            x = M + i * (hw + 14)
            self.painel(x, y, hw, 178, titulo)
            if i == 0:
                self.foto(x + 10, y + 14, 112, 150)
                self.entrada(nome, x + 130, y + 12, hw - 140, 158, tam=8, multi=True)
            else:
                self.entrada(nome, x + 10, y + 12, hw - 20, 158, tam=8, multi=True)

        y = 290
        self.painel(M, y, CW, 150, 'ORIGEM')
        x = M + 12
        self.rot(x, y + 9, 'TRAÇO')
        self.entrada('origem_traco', x, y + 17, CW - 24, 15, tam=8)
        tw = (CW - 24 - 16) / 3
        for i, rot in enumerate(['MARCANTE', 'MENOR 1', 'MENOR 2']):
            xx = x + i * (tw + 8)
            self.rot(xx, y + 40, rot)
            self.entrada('origem_%s' % slug(rot), xx, y + 48, tw, 15, tam=8.5)
            self.entrada('origem_%s_texto' % slug(rot), xx, y + 65, tw, 42, tam=7, multi=True)
        self.rot(x, y + 115, 'LEGADOS DE HISTÓRIA')
        self.entrada('legados', x, y + 123, CW - 24, 18, tam=7.5)

        y = 458
        eh = 258
        self.painel(M, y, hw, eh, 'EQUIPAMENTO')
        self.rot(M + 12, y + 7, 'ITEM')
        self.rot(M + hw - 50, y + 7, 'VOLUME')
        for i in range(N_ITENS):
            yy = y + 16 + i * 14.6
            self._campo('item_%d' % (i + 1), M + 12, yy, hw - 72, 12.5, 7.8, k['texto'])
            self.linha(M + 12, yy + 12.5, M + hw - 60, yy + 12.5, k['linha'], 0.4, [0.5, 1.5])
            self.entrada('item_%d_vol' % (i + 1), M + hw - 52, yy, 40, 12.5, tam=8, alinh=1)
        yy = y + 16 + N_ITENS * 14.6 + 6
        self.rot(M + 12, yy + 3, 'CARGA')
        self.auto('carga_usada', M + 100, yy, hw - 112, 15,
                  "var u=0;for(var i=1;i<=%d;i++)u+=n('item_'+i+'_vol');var l=n('carga');"
                  "event.value=u+' / '+l+(u>l?'  ACIMA DO LIMITE':'');" % N_ITENS, 8.5,
                  dica='soma do Volume digitado nos itens; ajuste pelos itens')
        x2 = M + hw + 14
        self.painel(x2, y, hw, 124, 'TRAJE  ·  ARMAS  ·  DINHEIRO')
        self.rot(x2 + 10, y + 9, 'TRAJE')
        self.entrada('traje', x2 + 10, y + 17, hw - 20, 28, tam=7, multi=True, dica='situação, TR e perícias do Traje')
        self.rot(x2 + 10, y + 52, 'TREINO COM ARMAS')
        self.entrada('treino_armas', x2 + 10, y + 60, hw - 20, 15, tam=7.5)
        self.rot(x2 + 10, y + 82, 'IENES')
        self.entrada('ienes', x2 + 10, y + 90, 110, 18, tam=10, alinh=1)
        self.rot(x2 + 128, y + 82, 'GUARDADO EM')
        self.entrada('guardado', x2 + 128, y + 90, hw - 138, 18, tam=7.5)
        self.painel(x2, y + 140, hw, eh - 140, 'LAÇOS E INSTITUIÇÃO')
        self.entrada('lacos', x2 + 10, y + 152, hw - 20, eh - 140 - 20, tam=7.5, multi=True)

        y = 734
        self.painel(M, y, CW, 92, 'ANOTAÇÕES')
        self.entrada('anotacoes', M + 10, y + 12, CW - 20, 72, tam=7.5, multi=True)
        self.proxima()

    # ------------------------------------------------ montagem
    def js_visual(self):
        """Cálculo final: barras, régua de espaços e selos (mostra/esconde e trava/destrava)."""
        partes = [JS_BASE,
                  "var L=niv(),R=n('refino'),ig=c('ignorar_selos');",
                  "function mostra(nm,v){var b=d.getField(nm);if(!b)return;var q=v?display.visible:display.hidden;"
                  "if(b.display!=q)b.display=q;}",
                  "function trava(l,v){for(var i=0;i<l.length;i++){var f=d.getField(l[i]);if(f&&f.readonly!=v)f.readonly=v;}}",
                  "function barra(p,q,N){for(var i=1;i<=N;i++)mostra(p+i,i<=q);}",
                  "function prop(a,m,N){if(m<=0)return 0;return Math.round(N*Math.max(0,Math.min(a,m))/m);}"]
        for rec in ('vida', 'pe', 'integ'):
            partes.append("barra('seg_%s_',prop(n('%s_atual'),n('%s_max'),16),16);" % (rec, rec, rec))
        partes.append("barra('seg_esp_',Math.min(24,n('esp_usados')),24);")
        partes.append("var MK=%s;for(var j=0;j<MK.length;j++)mostra('mk_'+MK[j],c(MK[j]));" % json.dumps(self.marcas))
        for nome, cond, campos in self.selos:
            partes.append("var a=(%s);mostra('%s',!a);trava(%s,!a);" % (cond, nome, json.dumps(campos)))
        partes.append("event.value='';")
        return ''.join(partes)

    def salvar(self):
        self.pagina1()
        self.pagina2()
        self.pagina_repertorio(1)
        self.pagina_repertorio(7)
        self.pagina5()
        self.pagina6()
        self.c.save()


# ---------------------------------------------------------------- pós-processo
def _imagem(w, im):
    rgb, a = im.convert('RGB').tobytes(), im.getchannel('A').tobytes()

    def img(dados, cs):
        s = StreamObject()
        s._data = zlib.compress(dados)
        s.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Image'),
                  NameObject('/Width'): NumberObject(im.width), NameObject('/Height'): NumberObject(im.height),
                  NameObject('/ColorSpace'): NameObject(cs), NameObject('/BitsPerComponent'): NumberObject(8),
                  NameObject('/Filter'): NameObject('/FlateDecode')})
        return s
    principal = img(rgb, '/DeviceRGB')
    principal[NameObject('/SMask')] = w._add_object(img(a, '/DeviceGray'))
    return w._add_object(principal)


def _aparencia(w, largura, altura, conteudo, recursos=None):
    s = StreamObject()
    s._data = conteudo.encode('latin-1')
    s.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Form'),
              NameObject('/BBox'): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(largura), FloatObject(altura)]),
              NameObject('/Resources'): recursos or DictionaryObject()})
    return w._add_object(s)


def montar(caminho, ficha):
    """Contas (/AA /C) e ordem (/CO), alinhamento, fontes, botões de segmento e de selo, travas iniciais."""
    r = PdfReader(caminho)
    w = PdfWriter()
    w.append(r)
    af = w._root_object['/AcroForm']
    campos = {}
    for pg in w.pages:
        for a in pg.get('/Annots', []) or []:
            o = a.get_object()
            alvo = o['/Parent'].get_object() if '/Parent' in o and '/T' not in o else o
            if alvo.get('/T') is not None:
                campos[str(alvo['/T'])] = (alvo, a if '/T' in o else o['/Parent'])

    js = lambda s: DictionaryObject({NameObject('/S'): NameObject('/JavaScript'), NameObject('/JS'): TextStringObject(s)})

    # botões: segmentos de barra e selos
    for b in ficha.botoes:
        pg = w.pages[b['pg']]
        x0, y0 = b['x'], H - b['y'] - b['h']
        if b.get('foto'):
            ap = _aparencia(w, b['w'], b['h'], '')
        elif 'imagem' in b:
            im = _imagem(w, Image.open(b['imagem']))
            ap = _aparencia(w, b['w'], b['h'], 'q %.2f 0 0 %.2f 0 0 cm /Im0 Do Q' % (b['w'], b['h']),
                            DictionaryObject({NameObject('/XObject'): DictionaryObject({NameObject('/Im0'): im})}))
        else:
            rr, gg, bb = (v / 255 for v in ficha.k['rgb'][b['cor']])
            pts = ' '.join('%.2f %.2f %s' % (px, b['h'] - py, 'm' if i == 0 else 'l') for i, (px, py) in enumerate(b['pts']))
            ap = _aparencia(w, b['w'], b['h'], '%.3f %.3f %.3f rg %s h f' % (rr, gg, bb, pts))
        botao = DictionaryObject({
            NameObject('/Type'): NameObject('/Annot'), NameObject('/Subtype'): NameObject('/Widget'),
            NameObject('/FT'): NameObject('/Btn'), NameObject('/Ff'): NumberObject((1 << 16) | 1),
            NameObject('/T'): TextStringObject(b['nome']),
            NameObject('/Rect'): ArrayObject([FloatObject(x0), FloatObject(y0), FloatObject(x0 + b['w']), FloatObject(y0 + b['h'])]),
            # segmentos começam escondidos (barra vazia); selos começam visíveis (nível 2)
            NameObject('/F'): NumberObject(6 if 'pts' in b else 4), NameObject('/H'): NameObject('/N'),
            NameObject('/AP'): DictionaryObject({NameObject('/N'): ap}), NameObject('/MK'): DictionaryObject(),
            # uma ação vazia: o pdf.js só obedece ao mostrar/esconder em botões com ação
            NameObject('/A'): js('var _selo=0;'),
            NameObject('/P'): pg.indirect_reference})
        if b.get('foto'):
            botao[NameObject('/A')] = js('event.target.buttonImportIcon();')
            botao[NameObject('/MK')] = DictionaryObject({NameObject('/TP'): NumberObject(1),
                                                         NameObject('/IF'): DictionaryObject({
                                                             NameObject('/SW'): NameObject('/A'),
                                                             NameObject('/S'): NameObject('/P')})})
            botao[NameObject('/TU')] = TextStringObject('clique para pôr a foto do personagem')
            botao[NameObject('/Ff')] = NumberObject(1 << 16)     # botão comum: precisa aceitar clique
        ref = w._add_object(botao)
        if b.get('baixo'):
            pg[NameObject('/Annots')].insert(0, ref)    # por baixo: o clique continua indo para a caixa
        else:
            pg[NameObject('/Annots')].append(ref)
        af['/Fields'].append(ref)

    # campo invisível que roda o cálculo visual por último
    pg0 = w.pages[0]
    visual = DictionaryObject({
        NameObject('/Type'): NameObject('/Annot'), NameObject('/Subtype'): NameObject('/Widget'),
        NameObject('/FT'): NameObject('/Tx'), NameObject('/Ff'): NumberObject(1), NameObject('/T'): TextStringObject('visual'),
        NameObject('/Rect'): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(1), FloatObject(1)]),
        NameObject('/F'): NumberObject(2), NameObject('/DA'): TextStringObject('/Helv 1 Tf 0 g'),
        NameObject('/P'): pg0.indirect_reference})
    ref_visual = w._add_object(visual)
    pg0[NameObject('/Annots')].append(ref_visual)
    af['/Fields'].append(ref_visual)
    campos['visual'] = (visual, ref_visual)
    ficha.calc.append(('visual', ficha.js_visual()))

    ordem = ArrayObject()
    faltando = [nome for nome, _ in ficha.calc if nome not in campos]
    if faltando:
        sys.exit('campos de cálculo sem widget: %s' % faltando)
    for nome, corpo in ficha.calc:
        alvo, ref = campos[nome]
        aa = alvo.get('/AA', DictionaryObject())
        aa[NameObject('/C')] = js(corpo)
        alvo[NameObject('/AA')] = aa
        ordem.append(ref if hasattr(ref, 'idnum') else alvo.indirect_reference)
    for nome, q in ficha.alinhar.items():
        if nome in campos and q:
            campos[nome][0][NameObject('/Q')] = NumberObject(q)
    # travas iniciais (nível 2 por padrão): quem está sob selo começa só leitura
    for nome in ficha.travados:
        alvo = campos[nome][0]
        alvo[NameObject('/Ff')] = NumberObject(int(alvo.get('/Ff', 0)) | 1)

    def fonte(base):
        d = {NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
             NameObject('/BaseFont'): NameObject(base)}
        if base != '/ZapfDingbats':
            d[NameObject('/Encoding')] = NameObject('/WinAnsiEncoding')
        return w._add_object(DictionaryObject(d))
    af[NameObject('/DR')] = DictionaryObject({NameObject('/Font'): DictionaryObject({
        NameObject('/Helv'): fonte('/Helvetica'), NameObject('/HeBo'): fonte('/Helvetica-Bold'),
        NameObject('/ZaDb'): fonte('/ZapfDingbats')})})
    af[NameObject('/DA')] = TextStringObject('/Helv 0 Tf 0 g')
    af[NameObject('/CO')] = ordem
    # Falso: com True, leitores sem JavaScript redesenham os botões do zero e somem com os selos.
    af[NameObject('/NeedAppearances')] = BooleanObject(False)
    w._root_object[NameObject('/OpenAction')] = js('try{this.calculateNow();}catch(e){}')
    with open(caminho, 'wb') as f:
        w.write(f)
    return len(ordem)


def main():
    os.makedirs(SAIDAS, exist_ok=True)
    for nome_paleta, modo in PALETAS:
        nome = 'ficha-ciclo-maldito-%s-%s.pdf' % (slug(nome_paleta), modo)
        caminho = os.path.join(SAIDAS, nome)
        f = Ficha(caminho, nome_paleta, modo)
        f.salvar()
        n = montar(caminho, f)
        print('%-45s %3d contas · %d selos · %d KB' % (nome, n, len(f.selos), os.path.getsize(caminho) // 1024))


if __name__ == '__main__':
    main()
