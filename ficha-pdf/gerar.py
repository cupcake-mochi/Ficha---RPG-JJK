#!/usr/bin/env python3
"""Gera a ficha em PDF preenchível do Ciclo Maldito (protótipo).

Uma única montagem, quatro paletas: Mizuki claro/escuro e Eclipse claro/escuro.
As cores vêm de medidas/paletas-grandes/paletas-grandes.json, as mesmas da planilha.
As contas são JavaScript de formulário (AcroForm), rodam no Acrobat Reader e no
leitor do Firefox; leitores sem JavaScript mostram os campos, mas não calculam.

Uso: python3 ficha-pdf/gerar.py            -> ficha-pdf/saidas/*.pdf
"""
import json
import logging
import os
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject, BooleanObject)
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logging.getLogger('pypdf').setLevel(logging.ERROR)  # aviso inofensivo do reportlab

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SAIDAS = os.path.join(AQUI, 'saidas')
W, H = A4
M = 22  # margem

pdfmetrics.registerFont(TTFont('Oswald', os.path.join(RAIZ, 'arte/fontes/Oswald.ttf')))
pdfmetrics.registerFont(TTFont('Yuji', os.path.join(RAIZ, 'arte/fontes/YujiSyuku.ttf')))

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
ESPACOS = [2, 3, 3, 4, 4, 6, 6, 7, 7, 9, 9, 10, 10, 12, 12, 13, 13, 15, 15, 16,
           16, 18, 18, 19, 19, 21, 21, 22, 22, 24]
REFINO = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5,
          5, 6, 6, 6, 6, 7, 7, 7, 7, 8]
CLASSE_MAX = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
              6, 6, 6, 6, 6, 7, 7, 7, 7, 7]
CLASSE_0 = [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

N_FEITICOS = 9
N_CLASSE0 = 3
N_ITENS = 14


def slug(t):
    tr = str.maketrans('áàâãéêíóôõúçÁÉÍÓÚÇ ', 'aaaaeeiooouc' + 'aeiouc_')
    return t.translate(tr).lower()


# ---------------------------------------------------------------- JavaScript
# Cabeçalho comum: d = documento, n() lê número, c() lê caixa marcada, s() põe sinal.
JS_BASE = (
    "var d=this;"
    "function n(f){var x=d.getField(f);if(!x)return 0;"
    "var v=parseFloat(String(x.value).replace(',','.').replace('+',''));return isNaN(v)?0:v;}"
    "function c(f){var x=d.getField(f);return !!x&&x.value!='Off'&&x.value!=''&&x.value!==false;}"
    "function t(f){var x=d.getField(f);return x?String(x.value):'';}"
    "function s(v){return (v>=0?'+':'')+v;}"
    "function niv(){var l=Math.round(n('nivel'));return l<1?1:(l>30?30:l);}"
)


def tabela_js(nome, valores):
    return "var %s=[%s];" % (nome, ','.join(str(v) for v in valores))


def js_calc(corpo):
    return JS_BASE + corpo


# ---------------------------------------------------------------- desenho
class Ficha:
    def __init__(self, caminho, paleta, modo):
        self.caminho = caminho
        self.nome_paleta = paleta
        self.modo = modo
        dados = json.load(open(os.path.join(RAIZ, 'medidas/paletas-grandes/paletas-grandes.json')))
        cores = dados[paleta][modo]['cores']
        self.osso = dados[paleta][modo]['osso_por_papel']
        self.k = {k: HexColor('#' + v) for k, v in cores.items()}
        self.kos = {k: HexColor('#' + v) for k, v in self.osso.items()}
        self.c = canvas.Canvas(caminho, pagesize=A4)
        self.c.setTitle('Ciclo Maldito · ficha de personagem · %s %s' % (paleta, modo))
        self.c.setAuthor('Projeto M')
        self.calc = []          # (nome, js) na ordem de cálculo
        self.alinhar = {}       # nome -> 0/1/2
        self.numericos = set()  # campos de entrada numérica

    # coordenadas: y medido do topo
    def Y(self, y, h=0):
        return H - y - h

    def ret(self, x, y, w, h, cor, borda=None, r=4, lw=0.8):
        c = self.c
        c.setFillColor(cor)
        if borda is not None:
            c.setStrokeColor(borda)
            c.setLineWidth(lw)
        c.roundRect(x, self.Y(y, h), w, h, r, stroke=1 if borda is not None else 0, fill=1)

    def txt(self, x, y, s, tam=7, cor=None, fonte='Oswald', alinh='e'):
        c = self.c
        c.setFillColor(cor or self.k['texto'])
        c.setFont(fonte, tam)
        yy = self.Y(y) - tam * 0.8
        if alinh == 'c':
            c.drawCentredString(x, yy, s)
        elif alinh == 'd':
            c.drawRightString(x, yy, s)
        else:
            c.drawString(x, yy, s)

    def fundo(self):
        self.c.setFillColor(self.k['fundo'])
        self.c.rect(0, 0, W, H, stroke=0, fill=1)

    def painel(self, x, y, w, h, titulo=None, sub=None):
        self.ret(x, y, w, h, self.k['painel'], self.k['linha'], r=5, lw=0.6)
        if titulo:
            self.ret(x, y, w, 13, self.k['bloco'], r=5)
            # tira reta embaixo da faixa arredondada
            self.c.setFillColor(self.k['bloco'])
            self.c.rect(x, self.Y(y + 13), w, 6, stroke=0, fill=1)
            self.c.setFillColor(self.k['painel'])
            self.c.rect(x + 0.3, self.Y(y + 13 + 4), w - 0.6, 4, stroke=0, fill=1)
            self.txt(x + 6, y + 2.5, titulo, 8, self.kos['bloco'])
            if sub:
                self.txt(x + w - 6, y + 3.5, sub, 6, self.kos['bloco'], alinh='d')

    # ---- campos
    def campo(self, nome, x, y, w, h, tipo='entrada', tam=8, alinh=0, multi=False,
              valor='', dica='', numero=False):
        """tipo: entrada (o jogador escreve), auto (calculado), ajuste (±)."""
        if tipo == 'auto':
            fundo, borda, cor = self.k['painel_alto'], self.k['linha'], self.k['texto']
            flags = 'readOnly'
        elif tipo == 'ajuste':
            fundo, borda, cor = self.k['tinta'], self.k['linha'], self.k['texto']
            flags = ''
        else:
            fundo, borda, cor = self.k['tinta'], self.k['linha'], self.k['texto']
            flags = ''
        if multi:
            flags = (flags + ' multiline').strip()
        self.c.acroForm.textfield(
            name=nome, tooltip=dica or nome, value=valor,
            x=x, y=self.Y(y, h), width=w, height=h,
            fontName='Helvetica-Bold' if tipo == 'auto' else 'Helvetica',
            fontSize=tam, borderStyle='solid', borderWidth=0.6,
            borderColor=borda, fillColor=fundo, textColor=cor,
            fieldFlags=flags, forceBorder=True)
        self.alinhar[nome] = alinh
        if numero:
            self.numericos.add(nome)

    def auto(self, nome, x, y, w, h, js, tam=10, dica=''):
        self.campo(nome, x, y, w, h, 'auto', tam, alinh=1, dica=dica)
        self.calc.append((nome, js_calc(js)))

    def ajuste(self, nome, x, y, w=22, h=12, dica='ajuste: bônus ou penalidade'):
        self.campo(nome, x, y, w, h, 'ajuste', 7, alinh=1, dica=dica, numero=True)

    def caixa(self, nome, x, y, tam=8, dica=''):
        self.c.acroForm.checkbox(
            name=nome, tooltip=dica or nome, checked=False, buttonStyle='check',
            x=x, y=self.Y(y, tam), size=tam, borderWidth=0.6,
            borderColor=self.k['linha'], fillColor=self.k['tinta'],
            textColor=self.k['texto'], forceBorder=True)

    def menu(self, nome, x, y, w, h, opcoes, valor, tam=8, dica=''):
        self.c.acroForm.choice(
            name=nome, tooltip=dica or nome, value=valor, options=opcoes,
            x=x, y=self.Y(y, h), width=w, height=h, fontName='Helvetica',
            fontSize=tam, borderWidth=0.6, borderColor=self.k['linha'],
            fillColor=self.k['tinta'], textColor=self.k['texto'], fieldFlags='combo')

    def rotulo(self, x, y, s, tam=6.5, cor=None, alinh='e'):
        self.txt(x, y, s, tam, cor or self.k['texto_fraco'], alinh=alinh)

    def legenda_ajuste(self, x, y):
        self.rotulo(x, y, '±', 7)

    # ---------------------------------------------------------- página 1
    def cabecalho(self, titulo, pagina):
        k = self.k
        self.ret(M, 16, W - 2 * M, 36, k['bloco'], r=6)
        self.txt(M + 10, 21, '呪術', 22, self.kos['bloco'], fonte='Yuji')
        self.txt(M + 64, 20, 'CICLO MALDITO', 17, self.kos['bloco'])
        self.txt(M + 64, 40, titulo, 7.5, self.kos['bloco'])
        self.txt(W - M - 10, 22, '%s · %s' % (self.nome_paleta, self.modo), 7, self.kos['bloco'], alinh='d')
        self.txt(W - M - 10, 34, 'ficha em PDF · protótipo · livro R53 · pág. %d/3' % pagina, 6.5,
                 self.kos['bloco'], alinh='d')

    def pagina1(self):
        self.fundo()
        self.cabecalho('FICHA DE PERSONAGEM · IDENTIDADE, ATRIBUTOS E TREINOS', 1)
        k = self.k
        cw = W - 2 * M

        # --- identidade
        y = 58
        self.painel(M, y, cw, 58)
        linhas = [
            [('PERSONAGEM', 'nome', 170), ('JOGADOR', 'jogador', 110), ('ORIGEM', 'origem', 110),
             ('NÍVEL', 'nivel', 40), ('GRAU', 'grau', 40), ('XP', 'xp', 51)],
        ]
        x = M + 6
        for rot, nome, w in linhas[0]:
            self.rotulo(x, y + 4, rot)
            num = nome in ('nivel', 'grau', 'xp')
            valor = {'nivel': '2', 'grau': '4'}.get(nome, '')
            self.campo(nome, x, y + 12, w, 15, alinh=1 if num else 0, valor=valor, numero=num, tam=9)
            x += w + 4
        x = M + 6
        self.rotulo(x, y + 31, 'CAMINHO')
        self.menu('caminho', x, y + 39, 110, 15, ['-'] + list(CAMINHOS), '-')
        x += 114
        self.rotulo(x, y + 31, 'TRILHA')
        self.campo('trilha', x, y + 39, 110, 15)
        x += 114
        self.rotulo(x, y + 31, 'ROTA (TÉCNICA INATA, SEM TÉCNICA, MARCIAL)')
        self.campo('rota', x, y + 39, 140, 15)
        x += 144
        self.rotulo(x, y + 31, 'TR FÍSICO USA')
        self.menu('tr_fis_atr', x, y + 39, 55, 15, ['-', 'FOR', 'DES'], '-',
                  dica='escolhido na criação e fixo')
        x += 59
        self.rotulo(x, y + 31, 'ATRIB. DA TÉCNICA')
        self.menu('tec_atr', x, y + 39, cw - (x - M) - 6, 15, ['-', 'FOR', 'DES', 'CON', 'INT', 'ESS'], '-')

        # --- atributos
        y = 122
        bw = (cw - 4 * 6) / 5
        for i, (sig, nome) in enumerate(ATRIBUTOS):
            x = M + i * (bw + 6)
            self.painel(x, y, bw, 52)
            self.txt(x + bw / 2, y + 5, nome, 7.5, k['texto_fraco'], alinh='c')
            self.campo('atr_' + sig, x + bw / 2 - 20, y + 16, 40, 28, tam=18, alinh=1, numero=True,
                       dica='%s: de 0 a 6 (na criação, até 3)' % nome.title())
        # --- progressão automática por nível
        y = 180
        self.painel(M, y, cw, 42, 'PROGRESSÃO DO NÍVEL', 'automático pelo nível · ± para marcos e exceções')
        caixas = [
            ('maestria', 'MAESTRIA', "var T=[1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,4,4,4,4,4];"
                                      "event.value=s(T[niv()-1]+n('maestria_aj'));"),
            ('espacos', 'ESPAÇOS', tabela_js('T', ESPACOS) + "event.value=T[niv()-1]+n('espacos_aj');"),
            ('classe0', 'CLASSE 0', tabela_js('T', CLASSE_0) + "event.value=T[niv()-1]+n('classe0_aj');"),
            ('classe_max', 'CLASSE MÁX.', tabela_js('T', CLASSE_MAX) + "event.value=T[niv()-1]+n('classe_max_aj');"),
            ('refino', 'REFINO', tabela_js('T', REFINO) + "event.value=T[niv()-1]+n('refino_aj');"),
        ]
        bw = (cw - 12) / 5
        for i, (nome, rot, js) in enumerate(caixas):
            x = M + 6 + i * bw
            self.rotulo(x, y + 17, rot)
            self.auto(nome, x, y + 25, 50, 13, js, 9)
            self.legenda_ajuste(x + 54, y + 27)
            self.ajuste(nome + '_aj', x + 61, y + 25.5)

        # --- recursos
        y = 226
        rw = (cw - 12) / 3
        recursos = [
            ('vida', 'VIDA', True,
             "var C={%s};var k=C[t('caminho')];"
             "if(!k){event.value='-';}else{var con=n('atr_con'),l=niv();"
             "event.value=(k[0]+con)+(k[1]+con)*(l-1)+n('vida_aj');}" %
             ','.join("'%s':[%d,%d]" % (nm, v[0], v[1]) for nm, v in CAMINHOS.items())),
            ('pe', 'ENERGIA (PE)', False,
             "var C={%s};var k=C[t('caminho')];"
             "if(!k){event.value='-';}else{event.value=k*niv()+n('pe_aj');}" %
             ','.join("'%s':%d" % (nm, v[2]) for nm, v in CAMINHOS.items())),
            ('integ', 'INTEGRIDADE', False,
             "event.value=20+(n('atr_ess')+5)*(niv()-1)+n('integ_aj');"),
        ]
        for i, (nome, rot, temp, js) in enumerate(recursos):
            x = M + i * (rw + 6)
            self.painel(x, y, rw, 62, rot)
            self.rotulo(x + 6, y + 19, 'ATUAL')
            self.campo(nome + '_atual', x + 6, y + 27, 52, 26, tam=15, alinh=1, numero=True)
            self.txt(x + 63, y + 31, '/', 15, k['texto_fraco'])
            self.rotulo(x + 72, y + 19, 'MÁXIMO')
            self.auto(nome + '_max', x + 72, y + 27, 46, 26, js, 14)
            self.rotulo(x + 124, y + 19, '±')
            self.ajuste(nome + '_aj', x + 122, y + 34)
            if temp:
                self.rotulo(x + 150, y + 19, 'TEMP.')
                self.campo('vida_temp', x + 148, y + 27, rw - 154, 26, tam=12, alinh=1, numero=True)
            elif nome == 'pe':
                self.rotulo(x + 150, y + 19, 'NOTAS')
                self.campo('pe_notas', x + 148, y + 27, rw - 154, 26, tam=7, multi=True)
            else:
                self.rotulo(x + 150, y + 19, 'ESTÁGIO')
                self.campo('integ_estagio', x + 148, y + 27, rw - 154, 26, tam=10, alinh=1)
        # vida rolada (variante)
        self.rotulo(M + 6, y + 55, 'Variante de vida rolada: use o ± para a diferença.', 5.5)

        # --- combate
        y = 294
        self.painel(M, y, cw, 82, 'COMBATE', 'automático pelos atributos e pela maestria · ± para itens, condições e efeitos')
        # linha 1: defesa
        x = M + 6
        yy = y + 18
        self.rotulo(x, yy, 'PROTEÇÃO DO TRAJE/REVEST.')
        self.campo('prot_equip', x, yy + 8, 54, 14, alinh=1, numero=True,
                   dica='vazio = sem Traje/Revestimento: usa Cobrir-se de Energia (1 + Refino/3)')
        x += 100
        self.rotulo(x, yy, 'ESCUDO')
        self.campo('escudo', x, yy + 8, 30, 14, alinh=1, numero=True)
        x += 36
        self.rotulo(x, yy, 'TETO DE DES')
        self.campo('teto_des', x, yy + 8, 30, 14, alinh=1, numero=True, dica='vazio = sem teto')
        x += 54
        self.rotulo(x, yy, 'PROTEÇÃO')
        self.auto('protecao', x, yy + 8, 30, 14,
                  "var e=t('prot_equip').replace(/\\s/g,'');"
                  "var b=(e==='')?1+Math.floor(n('refino')/3):n('prot_equip');"
                  "event.value=b+n('escudo')+n('protecao_aj');", 9)
        self.ajuste('protecao_aj', x + 33, yy + 9)
        x += 62
        self.rotulo(x, yy, 'DEFESA')
        self.auto('defesa', x, yy + 6, 36, 18,
                  "var de=n('atr_des');if(t('teto_des').replace(/\\s/g,'')!=='')de=Math.min(de,n('teto_des'));"
                  "event.value=10+de+n('protecao')+n('defesa_aj');", 12)
        self.ajuste('defesa_aj', x + 39, yy + 9)
        x += 68
        self.rotulo(x, yy, 'BLOQUEAR')
        self.auto('bloquear', x, yy + 8, 60, 14,
                  "var b=n('defesa')-11;event.value='2d10 '+(b>=0?'+ '+b:'- '+(-b));", 9)
        x += 66
        self.rotulo(x, yy, 'INICIATIVA')
        self.auto('iniciativa', x, yy + 8, 30, 14, "event.value=s(n('atr_des')+n('iniciativa_aj'));", 9)
        self.ajuste('iniciativa_aj', x + 33, yy + 9)
        x += 60
        self.rotulo(x, yy, 'DESLOC.')
        self.auto('deslocamento', x, yy + 8, 36, 14, "event.value=(9+n('desloc_aj'))+' m';", 9)
        self.ajuste('desloc_aj', x + 39, yy + 9)

        # linha 2: ataques
        x = M + 6
        yy = y + 48
        ataques = [
            ('cd_tec', 'CD DA TÉCNICA',
             "var a=t('tec_atr');if(a==='-'||a===''){event.value='-';}else{"
             "event.value=8+n('atr_'+a.toLowerCase())+n('maestria')+n('cd_tec_aj');}"),
            ('atq_tec', 'ATAQUE DA TÉCNICA',
             "var a=t('tec_atr');if(a==='-'||a===''){event.value='-';}else{"
             "event.value=s(n('atr_'+a.toLowerCase())+n('maestria')+n('atq_tec_aj'));}"),
            ('atq_cac', 'CORPO A CORPO',
             "event.value=s(n('atr_for')+n('maestria')+n('atq_cac_aj'));"),
            ('atq_dist', 'À DISTÂNCIA',
             "event.value=s(n('atr_des')+n('maestria')+n('atq_dist_aj'));"),
            ('carga', 'CARGA (5 + FOR)',
             "event.value=5+n('atr_for')+n('carga_aj');"),
        ]
        bw = (cw - 12) / 5
        for i, (nome, rot, js) in enumerate(ataques):
            x = M + 6 + i * bw
            self.rotulo(x, yy, rot)
            self.auto(nome, x, yy + 8, 44, 18, js, 12)
            self.legenda_ajuste(x + 49, yy + 12)
            self.ajuste(nome + '_aj', x + 56, yy + 11)
        self.rotulo(M + 6, y + 74, 'Ataques somam a maestria; arma sem treino tem desvantagem. '
                    'O dano de cada arma ou feitiço fica na página 2.', 5.5)

        # --- perícias (coluna esquerda)
        y = 382
        lw = 284
        rh = 17.6
        self.painel(M, y, lw, 30 + rh * len(PERICIAS), 'PERÍCIAS', 'T = treinada · E = especialista')
        self.rotulo(M + 6, y + 17, 'T   E')
        self.rotulo(M + 166, y + 17, 'ATRIB.')
        self.rotulo(M + 207, y + 17, '±')
        self.rotulo(M + 238, y + 17, 'TOTAL')
        for i, (nome, atr) in enumerate(PERICIAS):
            s_ = slug(nome)
            yy = y + 26 + i * rh
            if i % 2 == 0:
                self.c.setFillColor(self.k['painel_baixo'])
                self.c.rect(M + 2, self.Y(yy - 2.5, rh), lw - 4, rh, stroke=0, fill=1)
            self.caixa('per_%s_t' % s_, M + 6, yy + 2, 9, 'treinada: soma a maestria')
            self.caixa('per_%s_e' % s_, M + 19, yy + 2, 9, 'especialista: + metade da maestria')
            self.txt(M + 34, yy + 2.5, nome, 8, k['texto'], fonte='Helvetica')
            self.txt(M + 166, yy + 3, SIGLA[atr], 7, k['texto_fraco'])
            self.ajuste('per_%s_aj' % s_, M + 200, yy + 1)
            self.auto('per_' + s_, M + 232, yy, 42, 12.5,
                      "var m=n('maestria'),v=n('atr_%s');if(c('per_%s_t')){v+=m;if(c('per_%s_e'))v+=Math.floor(m/2);}"
                      "event.value=s(v+n('per_%s_aj'));" % (atr, s_, s_, s_), 9)

        # --- coluna direita
        rx = M + lw + 8
        rw2 = cw - lw - 8
        rh = 16.2  # linhas da direita um pouco mais baixas, sobra espaço para o estado
        # TRs
        y = 382
        trs = [('fis', 'Físico', None), ('vig', 'Vigor', 'con'), ('itl', 'Intelecto', 'int'), ('esp', 'Espírito', 'ess')]
        self.painel(rx, y, rw2, 30 + rh * 4, 'TESTES DE RESISTÊNCIA', 'T = treinado (Origem + Caminho)')
        self.rotulo(rx + 6, y + 17, 'T')
        self.rotulo(rx + 120, y + 17, 'ATRIB.')
        self.rotulo(rx + 182, y + 17, '±')
        self.rotulo(rx + 212, y + 17, 'TOTAL')
        for i, (sg, nome, atr) in enumerate(trs):
            yy = y + 26 + i * rh
            self.caixa('tr_%s_t' % sg, rx + 6, yy + 2, 9)
            self.txt(rx + 20, yy + 2.5, nome, 8, k['texto'], fonte='Helvetica')
            self.txt(rx + 120, yy + 3, 'FOR/DES' if atr is None else SIGLA[atr], 7, k['texto_fraco'])
            self.ajuste('tr_%s_aj' % sg, rx + 175, yy + 1)
            if atr is None:
                js = ("var a=t('tr_fis_atr');if(a==='-'||a===''){event.value='-';}else{"
                      "var v=n('atr_'+a.toLowerCase());if(c('tr_fis_t'))v+=n('maestria');"
                      "event.value=s(v+n('tr_fis_aj'));}")
            else:
                js = ("var v=n('atr_%s');if(c('tr_%s_t'))v+=n('maestria');event.value=s(v+n('tr_%s_aj'));"
                      % (atr, sg, sg))
            self.auto('tr_' + sg, rx + 206, yy, 42, 12.5, js, 9)

        # Ofícios
        y = 382 + 30 + rh * 4 + 6
        oh = 30 + rh * len(OFICIOS)
        self.painel(rx, y, rw2, oh, 'OFÍCIOS', 'sem treino, normalmente não tenta')
        self.rotulo(rx + 6, y + 17, 'T')
        self.rotulo(rx + 120, y + 17, 'PADRÃO')
        self.rotulo(rx + 182, y + 17, '±')
        self.rotulo(rx + 212, y + 17, 'TOTAL')
        for i, (nome, atr) in enumerate(OFICIOS):
            s_ = slug(nome)
            yy = y + 26 + i * rh
            if i % 2 == 0:
                self.c.setFillColor(self.k['painel_baixo'])
                self.c.rect(rx + 2, self.Y(yy - 2.5, rh), rw2 - 4, rh, stroke=0, fill=1)
            self.caixa('of_%s_t' % s_, rx + 6, yy + 2, 9)
            self.txt(rx + 20, yy + 2.5, nome, 8, k['texto'], fonte='Helvetica')
            self.txt(rx + 120, yy + 3, SIGLA[atr], 7, k['texto_fraco'])
            self.ajuste('of_%s_aj' % s_, rx + 175, yy + 1)
            self.auto('of_' + s_, rx + 206, yy, 42, 12.5,
                      "if(!c('of_%s_t')){event.value='-';}else{"
                      "event.value=s(n('atr_%s')+n('maestria')+n('of_%s_aj'));}" % (s_, atr, s_), 9)

        # Estado
        y = y + oh + 6
        eh = 382 + 30 + 17.6 * len(PERICIAS) - y
        self.painel(rx, y, rw2, eh, 'SE A VIDA CHEGAR A 0 · MORRENDO')
        cols = [('morr_aguentar', 'AGUENTAR', "event.value=Math.ceil(n('vida_max')/4);"),
                ('morr_ins1', 'INSISTIR 1ª', "event.value=Math.min(Math.ceil(n('vida_max')/3),15*n('classe_max'));"),
                ('morr_ins2', 'INSISTIR 2ª+', "event.value=Math.min(Math.ceil(n('vida_max')/2),15*n('classe_max'));")]
        cw3 = (rw2 - 12) / 3
        for i, (nome, rot, js) in enumerate(cols):
            x = rx + 6 + i * cw3
            self.rotulo(x, y + 17, rot)
            self.auto(nome, x, y + 25, cw3 - 8, 14, js, 9, dica='cura necessária para levantar')
        self.rotulo(rx + 6, y + 44, 'SEQUELAS')
        for i in range(3):
            self.caixa('sequela_%d' % (i + 1), rx + 48 + i * 13, y + 44, 9)
        self.rotulo(rx + 96, y + 44, 'JANELA')
        self.auto('morr_janela', rx + 124, y + 42, rw2 - 130, 13,
                  "var q=(c('sequela_1')?1:0)+(c('sequela_2')?1:0)+(c('sequela_3')?1:0);"
                  "event.value=q>=3?'Derrotado':(3-q)+(3-q==1?' rodada':' rodadas');", 8)
        self.rotulo(rx + 6, y + 60, 'EXAUSTÃO')
        self.campo('exaustao', rx + 48, y + 58, 30, 13, alinh=1, numero=True)
        self.rotulo(rx + 84, y + 60, 'CONDIÇÕES')
        self.campo('condicoes', rx + 124, y + 58, rw2 - 130, 13, tam=7)
        self.rotulo(rx + 6, y + 76, 'RESISTÊNCIAS E IMUNIDADES')
        self.campo('resistencias', rx + 6, y + 84, rw2 - 12, eh - 90, tam=7, multi=True)

        self.c.showPage()

    # ---------------------------------------------------------- página 2
    def pagina2(self):
        self.fundo()
        self.cabecalho('A TÉCNICA · FUNDAMENTO, FEITIÇOS E HABILIDADES', 2)
        k = self.k
        cw = W - 2 * M
        y = 58
        self.painel(M, y, cw, 150, 'FUNDAMENTO')
        x = M + 6
        self.rotulo(x, y + 18, 'NOME DA TÉCNICA')
        self.campo('tec_nome', x, y + 26, 200, 15, tam=9)
        self.rotulo(x + 206, y + 18, 'TIPOS DE DANO')
        self.campo('tec_dano', x + 206, y + 26, 150, 15, tam=8)
        self.rotulo(x + 362, y + 18, 'SELO')
        self.campo('tec_selo', x + 362, y + 26, cw - 374, 15, tam=8)
        self.rotulo(x, y + 46, 'REGRA · A FRASE QUE EXPLICA COMO ELA FUNCIONA')
        self.campo('tec_regra', x, y + 54, cw - 12, 24, tam=8, multi=True)
        self.rotulo(x, y + 83, 'DESCRIÇÃO E EXPRESSÃO DA TÉCNICA')
        self.campo('tec_descricao', x, y + 91, cw - 12, 24, tam=8, multi=True)
        self.rotulo(x, y + 120, 'FAMÍLIAS LIVRES')
        fw = (cw - 12 - 10) / 5
        for i in range(2):
            self.campo('fam_livre_%d' % (i + 1), x + i * (fw + 2), y + 128, fw, 15, tam=8)
        self.rotulo(x + 2 * (fw + 2) + 6, y + 120, 'FAMÍLIAS FECHADAS')
        for i in range(3):
            self.campo('fam_fechada_%d' % (i + 1), x + (2 + i) * (fw + 2) + 6, y + 128, fw - 2, 15, tam=8)

        # feitiços
        y = 214
        rh = 36
        fh = 30 + rh * N_FEITICOS + 16 * N_CLASSE0 + 14
        self.painel(M, y, cw, fh, 'FEITIÇOS', 'PE = 3 × Classe · ± para Liberação, Melhorias e efeitos')
        cols = [('NOME', 6, 150), ('CLASSE', 160, 34), ('PE', 198, 30), ('±', 230, 22),
                ('AÇÃO', 256, 60), ('ALCANCE', 320, 70), ('ACERTO / TR', 394, 70), ('DANO', 468, cw - 474)]
        for rot, dx, _w in cols:
            self.rotulo(M + dx, y + 17, rot)
        for i in range(N_FEITICOS):
            yy = y + 26 + i * rh
            if i % 2 == 0:
                self.c.setFillColor(self.k['painel_baixo'])
                self.c.rect(M + 2, self.Y(yy - 2, rh), cw - 4, rh, stroke=0, fill=1)
            p = 'f%d_' % (i + 1)
            self.campo(p + 'nome', M + 6, yy, 150, 13, tam=8)
            self.campo(p + 'classe', M + 160, yy, 34, 13, alinh=1, numero=True)
            self.auto(p + 'pe', M + 198, yy, 30, 13,
                      "var cl=t('%sclasse').replace(/\\s/g,'');if(cl===''){event.value='';}else{"
                      "event.value=3*n('%sclasse')+n('%spe_aj');}" % (p, p, p), 8)
            self.ajuste(p + 'pe_aj', M + 230, yy + 0.5)
            self.campo(p + 'acao', M + 256, yy, 60, 13, tam=7)
            self.campo(p + 'alcance', M + 320, yy, 70, 13, tam=7)
            self.campo(p + 'acerto', M + 394, yy, 70, 13, tam=7)
            self.campo(p + 'dano', M + 468, yy, cw - 474, 13, tam=7)
            self.campo(p + 'efeito', M + 6, yy + 15, cw - 12, 17, tam=7, multi=True,
                       dica='como é: alvos, resolução, duração, Melhorias e Restrições')
        yy = y + 26 + N_FEITICOS * rh + 2
        self.rotulo(M + 6, yy, 'CLASSE 0 · grátis em PE, fora dos espaços')
        for i in range(N_CLASSE0):
            y0 = yy + 9 + i * 16
            self.campo('c0_%d_nome' % (i + 1), M + 6, y0, 150, 13, tam=8)
            self.campo('c0_%d_efeito' % (i + 1), M + 160, y0, cw - 166, 13, tam=7)

        # habilidades
        y = y + fh + 6
        hh = H - 22 - y
        self.painel(M, y, cw, hh, 'HABILIDADES DE CAMINHO, TRILHA E APTIDÕES',
                    'nome, quando usa, o que gasta e o que faz')
        self.campo('habilidades', M + 6, y + 18, cw - 12, hh - 24, tam=7.5, multi=True)
        self.c.showPage()

    # ---------------------------------------------------------- página 3
    def pagina3(self):
        self.fundo()
        self.cabecalho('QUEM É · HISTÓRIA, ORIGEM E EQUIPAMENTO', 3)
        k = self.k
        cw = W - 2 * M
        half = (cw - 8) / 2
        y = 58
        self.painel(M, y, half, 200, 'APARÊNCIA E PERSONALIDADE')
        self.campo('aparencia', M + 6, y + 18, half - 12, 176, tam=8, multi=True)
        self.painel(M + half + 8, y, half, 200, 'HISTÓRIA E MOTIVO PARA ESTAR NO GRUPO')
        self.campo('historia', M + half + 14, y + 18, half - 12, 176, tam=8, multi=True)

        y = 264
        self.painel(M, y, cw, 140, 'ORIGEM', 'traço, capacidade marcante e duas menores')
        x = M + 6
        self.rotulo(x, y + 18, 'TRAÇO')
        self.campo('origem_traco', x, y + 26, cw - 12, 15, tam=8)
        tw = (cw - 12 - 8) / 3
        for i, rot in enumerate(['MARCANTE', 'MENOR 1', 'MENOR 2']):
            xx = x + i * (tw + 4)
            self.rotulo(xx, y + 46, rot)
            self.campo('origem_%s' % slug(rot), xx, y + 54, tw, 15, tam=8)
            self.campo('origem_%s_texto' % slug(rot), xx, y + 71, tw, 34, tam=7, multi=True)
        self.rotulo(x, y + 110, 'LEGADOS DE HISTÓRIA · vínculos e acontecimentos, sem efeito mecânico')
        self.campo('legados', x, y + 118, cw - 12, 16, tam=7)

        # equipamento
        y = 410
        eh = 250
        self.painel(M, y, half, eh, 'EQUIPAMENTO', 'Volume conta para a carga')
        self.rotulo(M + 6, y + 17, 'ITEM')
        self.rotulo(M + half - 42, y + 17, 'VOLUME')
        for i in range(N_ITENS):
            yy = y + 26 + i * 15
            self.campo('item_%d' % (i + 1), M + 6, yy, half - 54, 13, tam=7.5)
            self.campo('item_%d_vol' % (i + 1), M + half - 44, yy, 38, 13, alinh=1, numero=True)
        yy = y + 26 + N_ITENS * 15 + 4
        self.rotulo(M + 6, yy + 3, 'CARGA USADA / LIMITE')
        js = ("var u=0;for(var i=1;i<=%d;i++)u+=n('item_'+i+'_vol');"
              "var l=n('carga');event.value=u+' / '+l+(u>l?'  · acima do limite':'');" % N_ITENS)
        self.auto('carga_usada', M + 96, yy, half - 102, 14, js, 8)

        x2 = M + half + 8
        self.painel(x2, y, half, 120, 'TRAJE, ARMAS E DINHEIRO')
        self.rotulo(x2 + 6, y + 18, 'TRAJE · SITUAÇÃO, TR E PERÍCIAS DO TRAJE')
        self.campo('traje', x2 + 6, y + 26, half - 12, 28, tam=7, multi=True)
        self.rotulo(x2 + 6, y + 58, 'TREINO COM ARMAS')
        self.campo('treino_armas', x2 + 6, y + 66, half - 12, 15, tam=7)
        self.rotulo(x2 + 6, y + 86, 'IENES (¥)')
        self.campo('ienes', x2 + 6, y + 94, 110, 16, tam=9, alinh=1)
        self.rotulo(x2 + 124, y + 86, 'ONDE GUARDA O RESTO')
        self.campo('guardado', x2 + 124, y + 94, half - 130, 16, tam=7)

        self.painel(x2, y + 126, half, eh - 126, 'LAÇOS E INSTITUIÇÃO')
        self.campo('lacos', x2 + 6, y + 144, half - 12, eh - 126 - 24, tam=7.5, multi=True)

        y = y + eh + 6
        self.painel(M, y, cw, H - 22 - y, 'ANOTAÇÕES')
        self.campo('anotacoes', M + 6, y + 18, cw - 12, H - 22 - y - 24, tam=7.5, multi=True)
        self.c.showPage()

    def salvar(self):
        self.pagina1()
        self.pagina2()
        self.pagina3()
        self.c.save()


# ---------------------------------------------------------------- pós-processo
def ligar_contas(caminho, ficha):
    """Acrescenta as ações de cálculo (/AA /C), a ordem (/CO), o alinhamento e as fontes do formulário."""
    r = PdfReader(caminho)
    w = PdfWriter()
    w.append(r)
    campos = {}
    for pg in w.pages:
        for a in pg.get('/Annots', []) or []:
            o = a.get_object()
            alvo = o['/Parent'].get_object() if '/Parent' in o and '/T' not in o else o
            nome = alvo.get('/T')
            if nome is not None:
                campos[str(nome)] = (alvo, a if '/T' in o else o['/Parent'])
    js = lambda s: DictionaryObject({NameObject('/S'): NameObject('/JavaScript'),
                                     NameObject('/JS'): TextStringObject(s)})
    ordem = ArrayObject()
    faltando = []
    for nome, corpo in ficha.calc:
        if nome not in campos:
            faltando.append(nome)
            continue
        alvo, ref = campos[nome]
        aa = alvo.get('/AA', DictionaryObject())
        aa[NameObject('/C')] = js(corpo)
        alvo[NameObject('/AA')] = aa
        ordem.append(ref if hasattr(ref, 'idnum') else alvo.indirect_reference)
    for nome, q in ficha.alinhar.items():
        if nome in campos and q:
            campos[nome][0][NameObject('/Q')] = NumberObject(q)
    # Sem filtro de teclas (/K): no pdf.js ele fazia valores digitados se perderem.
    # Texto não numérico num campo de número conta como 0.
    if faltando:
        sys.exit('campos de cálculo sem widget: %s' % faltando)
    af = w._root_object['/AcroForm']
    def fonte(base):
        return w._add_object(DictionaryObject({
            NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
            NameObject('/BaseFont'): NameObject(base),
            **({} if base == '/ZapfDingbats' else {NameObject('/Encoding'): NameObject('/WinAnsiEncoding')})}))
    dr = DictionaryObject()
    dr[NameObject('/Font')] = DictionaryObject({
        NameObject('/Helv'): fonte('/Helvetica'), NameObject('/HeBo'): fonte('/Helvetica-Bold'),
        NameObject('/ZaDb'): fonte('/ZapfDingbats')})
    af[NameObject('/DR')] = dr
    af[NameObject('/DA')] = TextStringObject('/Helv 0 Tf 0 g')
    af[NameObject('/CO')] = ordem
    af[NameObject('/NeedAppearances')] = BooleanObject(True)
    # abre com o cálculo inicial (valores padrão de nível e Grau)
    w._root_object[NameObject('/OpenAction')] = js(
        "try{this.calculateNow();}catch(e){}")
    with open(caminho, 'wb') as f:
        w.write(f)
    return len(ordem)


def main():
    os.makedirs(SAIDAS, exist_ok=True)
    for paleta, modo in PALETAS:
        nome = 'ficha-ciclo-maldito-%s-%s.pdf' % (slug(paleta), modo)
        caminho = os.path.join(SAIDAS, nome)
        f = Ficha(caminho, paleta, modo)
        f.salvar()
        n = ligar_contas(caminho, f)
        print('%-45s %3d contas' % (nome, n))


if __name__ == '__main__':
    main()
