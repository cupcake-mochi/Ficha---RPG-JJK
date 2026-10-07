# -*- coding: utf-8 -*-
"""A aba INVOCAÇÕES: as entidades do personagem, cada uma com a ficha dela, e o conjunto. É a limpeza 29.

Não existe planilha viva desta aba. O desenho foi fechado com o Mizuki por estudo, em cinco rodadas, em 06/10/2026
(mockup/invocacao-estudo.html), e a aba nasce inteira aqui, como a FICHA AMALDIÇOADA. As decisões dele:
  · a ficha DEITADA, com a foto à esquerda, os números no meio e a mesa à direita ("algo mais de lado"), "visualmente
    atrativo, semelhante as outras paginas", com foto, nome, caixas e menus;
  · várias fichas numa grade ("A+B ... umas 2-3 colunas ... umas 5-6 linhas ... o jogador decide aonde vai preencher"):
    ele fechou em 2 colunas de 6, cada coluna com o grupo de colunas dela e cada fileira com o grupo de linhas;
  · o conjunto à esquerda, com a lista de todas ("mantem o conjunto ali na esquerda com a lista grande de invocações");
  · valor automático com Buff/Debuff ("que nem no sistema da ficha principal");
  · Liberação Máxima, Técnica Máxima e Expansão num grupo que nasce fechado, sem automação para liberar;
  · a foto larga ("aumentar a largura da imagem ... pra caber algo legal").

A GRADE. O estudo foi desenhado numa grade de colunas finas, como os outros. A aba não: com 2 colunas de 6 fichas ela
teria 120 mil células, e a troca de tema é feita célula a célula. Como a FICHA AMALDIÇOADA, cada coluna tem a largura
do que guarda: a ficha são três blocos de cinco colunas de 96 px (a foto, os números, a mesa), que são também as três
cartas de habilidade de cada fileira, com 480 px cada, a largura das cartas de lá. O Buff/Debuff fica embaixo do número,
e não ao lado, para todo valor caber numa coluna.

AS CONTAS moram numa aba oculta própria, a DADOS_INVOC: as tabelas do livro, uma linha de conta por ficha e uma por
carta de habilidade. A aba só mostra o resultado. Nenhuma fórmula usa LET nem LAMBDA (a regressão recalcula no
LibreOffice).

DE ONDE SAI CADA NÚMERO. A progressão da entidade, os pontos e o PE por Classe, as Formas, o alcance, os talentos, os
tipos, as aquisições, os trunfos e o que o Evocador muda saem do ficha-v01/invocacao-do-livro.json, que o
extrair_invocacao.py lê dos capítulos 16 e 17 do manual.txt. As Melhorias, as condições, as Restrições e os pares
proibidos são os da FICHA AMALDIÇOADA (catalogo-projeto-m.json e decisoes-ficha.json), lidos por ficha_amaldicoada.regras().

O QUE ESTA ABA NÃO FAZ: as Intervenções de Vínculo (são ações; a aba guarda os pontos), a lista de ritual e a
fabricação. Ela não confere quem pode ter trunfo (o livro os dá à domada com técnica própria), nem se os degraus de
Domínio da domada gastaram espaço de especial. A Integridade da entidade com alma não tem caixa: o capítulo 17 não dá
a máxima dela.
"""
import json, math, os, re

import indice_ficha as ix
import ficha_pessoal as fp
import ficha_amaldicoada as fa

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "INVOCAÇÕES"
IV = f"'{NOME}'!"
DADOS_IV = "DADOS_INVOC"
DI = f"{DADOS_IV}!"
APOIO = "as entidades, a montagem e a mesa"

# ---------------------------------------------------------------------------------------------
# A grade. A, B e C como na FICHA; o conjunto em três colunas; cada coluna de fichas com a lombada do nome, três blocos
# de cinco colunas e uma de respiro entre eles.
# ---------------------------------------------------------------------------------------------
# Quantas fichas a aba traz. O Mizuki fechou 2 × 6; a primeira etapa da construção monta uma só, para ele medir o
# construir() antes de a grade inteira entrar.
N_COLUNAS, N_FILEIRAS = 2, 6
PX_FINA, PX_CONJ, PX_BLOCO = 28, 107, 96
N_CONJ, N_BLOCO = 3, 5
C_CONJ = 4                                   # D, E e F; a G é o respiro
PASSO_COL = 1 + 3 * (N_BLOCO + 1)            # a lombada, e três blocos com o respiro depois de cada um
C = ix._col
L = ix._letras
_a1, _abs, _faixa, _A, _se = fa._a1, fa._abs, fa._faixa, fa._A, fa._se


def lombada(k):
    return C_CONJ + N_CONJ + 1 + PASSO_COL * k


def blocos(k):
    """a primeira coluna de cada um dos três blocos da coluna de fichas k"""
    return [lombada(k) + 1 + (N_BLOCO + 1) * j for j in range(3)]


COLS = lombada(N_COLUNAS - 1) + PASSO_COL - 1          # a última é o respiro da direita
PX_COLUNAS = [PX_FINA] * 3 + [PX_CONJ] * N_CONJ + [PX_FINA] + ([PX_FINA] + ([PX_BLOCO] * N_BLOCO + [PX_FINA]) * 3) * N_COLUNAS
assert len(PX_COLUNAS) == COLS

# as linhas de uma ficha, contadas da faixa do nome
L0 = 9                                       # a primeira fileira de fichas, e o conjunto
N_ATR, N_PER, N_FAM, N_TAL, N_TALX, N_LIB = 5, 7, 5, 8, 3, 3
N_BAS, N_ESP, N_EXT = 2, 8, 3
N_MEL, N_RES = 4, 2
# a carta de habilidade
F_TIT, F_NOME, F_ROT, F_TXT, F_TXT_FIM, F_N1, F_N2, F_N3, F_ALC, F_MEL, F_RES, F_CONTA, F_AMP, F_AV = 0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 14, 16, 17, 19
ALT = 21
ALT_TRUNFO = 8
O = {"hab": 43, "h": 45, "tal": 67, "mais": 77, "m": 79, "trilha": 145, "x": 147, "talx": 169, "trunfos": 174, "lib": 176,
     "tm": 185, "fim": 192}
PASSO_LIN = O["fim"] + 3
ABRE_BAS, ABRE_ESP = (1, 11), (1, 4, 8, 12, 16, 20, 24, 28)
# as dez cartas na ordem em que o nível abre: a primeira fileira é o que uma entidade de nível baixo tem
ORDEM = [("bas", 0), ("esp", 0), ("esp", 1), ("bas", 1), ("esp", 2), ("esp", 3), ("esp", 4), ("esp", 5), ("esp", 6), ("esp", 7)]
LIN = L0 + PASSO_LIN * N_FILEIRAS - 3 + fa.RESPIRO
N_ROL = N_COLUNAS * N_FILEIRAS

TINTA, FUNDO, PAINEL, ALTO, PAPEL, ACENTO = fa.TINTA, fa.FUNDO, fa.PAINEL, fa.ALTO, fa.PAPEL, fa.ACENTO
OSSO, TEXTO, FRACO = fa.OSSO, fa.TEXTO, fa.FRACO
_CAIXA = fa._CAIXA
ESTILOS = dict(fa.ESTILOS)
ESTILOS.update({
    "numero":   [["Oswald", 14.0, OSSO, False, False], ACENTO, _CAIXA, ["center", "center", False, 0], None],
    "lombada":  [["Oswald", 9.0, OSSO, False, False], TINTA, None, ["center", "top", False, 90], None],
    "lomb_num": [["Oswald", 9.0, OSSO, False, False], ACENTO, None, ["center", "center", False, 0], None],
    # a caixa da foto: a mesma da CARTEIRA (ver moldura_foto.py), para a imagem inserida na célula
    "foto":     [["Yuji Syuku", 22.0, "FF756588", False, False], PAPEL, _CAIXA, ["center", "center", True, 0], None],
    # o que o jogador digita em número: os pontos de atributo, e o Buff/Debuff embaixo de cada valor calculado
    "pontos":   [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], '0" pt"'],
    "bd":       [["Roboto", 9.0, FRACO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], '"B/D "+0;"B/D "-0;"B/D "0'],
    "digita":   [["Oswald", 16.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "rol":      [["Roboto", 9.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
    "barra":    fp.ESTILOS["barra"],
})
T_ERRO, T_AVISO = fa.T_ERRO, fa.T_AVISO
VERMELHO, BRANCO, AMBAR = fa.VERMELHO, fa.BRANCO, fa.AMBAR
NA_REGRA, DENTRO, SEM_NOME = fa.NA_REGRA, fa.DENTRO, fa.SEM_NOME
FORMA_INICIAL = fa.FORMA_INICIAL
TEXTO_FOTO = "FOTO\n式神"

ATRS = [("Força", "FOR"), ("Destreza", "DES"), ("Constituição", "CON"), ("Inteligência", "INT"), ("Essência", "ESS")]
TESTES = [("Físico", None), ("Vigor", 2), ("Intelecto", 3), ("Espírito", 4)]
DOMADA, SH_CRIACAO, CORPO_CRIACAO = "Maldição domada", "Shikigami de criação", "Corpo amaldiçoado de criação"
COM_CARGA, SEM_CARGA = "Com carga", "Sem carga"
RESOLVE = ["Ataque", "TR Físico", "TR Vigor", "TR Intelecto", "TR Espírito"]
PRINCIPAL, PARCERIA, MULTIPLAS = "Invocação Principal", "Parceria", "Múltiplas Invocações"
PROPRIO = "Talento Próprio"
# as peças que a conta cita pelo nome, além das que a FICHA AMALDIÇOADA já confere contra o catálogo
PECAS_CITADAS = ("Precisão",)


def sinal(x):
    return f'IF({x}>=0,"+","−")&ABS({x})'


def regras():
    """tudo o que a aba lê: o invocacao-do-livro.json, e as peças da FICHA AMALDIÇOADA"""
    LIV = json.load(open(os.path.join(RAIZ, "ficha-v01", "invocacao-do-livro.json"), encoding="utf-8"))
    CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    TEC = json.load(open(os.path.join(RAIZ, "ficha-v01", "tecnica-do-livro.json"), encoding="utf-8"))
    RA = fa.regras(CAT, TEC)
    nomes_pecas = [p["nome"] for p in RA["pecas"]]
    falta = [n for n in PECAS_CITADAS + tuple(LIV["reduzidas"]) if n not in nomes_pecas]
    falta += [f["nome"] for f in LIV["formas"] if f["nome"] not in CAT["formas"]] + [n for n in CAT["formas"] if n not in [f["nome"] for f in LIV["formas"]]]
    falta += [t for t in (DOMADA, SH_CRIACAO, CORPO_CRIACAO) if t not in [x["nome"] for x in LIV["tipos"]]]
    falta += [t for t in (PRINCIPAL, PARCERIA, MULTIPLAS) if t not in LIV["trilhas"] or CAT["trilhas"].get(t) != "Evocador"]
    if falta or LIV["familias"] != RA["familias"]:
        raise SystemExit(f"ficha_invocacoes: o livro e o catalogo nao batem em {falta or 'Familias'}: a conta da aba cita esses nomes")
    if len(LIV["progressao"]) != 7 or LIV["marcos"] != CAT["progressao"]["marcos"] or len(LIV["tecnica_maxima"]) != 3:
        raise SystemExit("ficha_invocacoes: a progressao da entidade nao tem mais sete Classes, ou os marcos mudaram")
    # o preço de cada peça por Classe: Leve, Média e Pesada, e as três com o desconto da Família Livre, que na entidade
    # é metade da Classe PARA BAIXO, com desconto mínimo de 1 e preço mínimo de 1 (no Fundamento é para cima)
    classes = []
    for c in LIV["classes"]:
        k = c["classe"]
        cheio = [fa.preco(p, k) for p in (1, 2, 3)]
        classes.append({"classe": k, "precos": cheio + [max(1, p - max(1, k // 2)) for p in cheio], "limite": c["melhorias"],
                        "pontos": c["pontos"]})
    lim = {int(c): int(m) for faixa, m, _ in TEC["melhorias_por_classe"] for c in range(int(faixa[0]), int(faixa[-1]) + 1)}
    if any(lim[c["classe"]] != c["limite"] for c in classes):
        raise SystemExit("ficha_invocacoes: o limite de Melhorias da entidade deixou de ser o do Fundamento")
    do_fund = {f["nome"]: f for f in RA["formas"]}
    formas = []
    for f in LIV["formas"]:
        g = do_fund[f["nome"]]
        if fa.PESO.get(f["custa"], 0) != g["peso"] or int(f["embutida"]) != g["embutida"]:
            raise SystemExit(f"ficha_invocacoes: a Forma {f['nome']} da entidade nao custa mais o que custa no Fundamento")
        formas.append({"nome": f["nome"], "exige": f["exige"] or "", "peso": g["peso"], "embutida": g["embutida"], "tipo": g["tipo"],
                       "resolve": "Ataque" if g["resolve"] == "Acerto" else "TR" if g["tr"] else "—", "tr": g["tr"],
                       "grau1": g["grau1"], "grau2": g["grau2"], "alvos": g["alvos"],
                       "na_zero": int(f["nome"] not in ("Cura", "Onda"))})
    # o alcance de cada Forma em cada faixa de Classe da entidade (0, 1 a 5, 6 e 7), degrau a degrau, pelas escadas do
    # Fundamento, partindo das bases do capítulo 17
    esc = TEC["escadas"]
    def a_base(forma, escada, faixa):
        t = LIV["area"].get(forma) if escada in ("raio", "comprimento") else LIV["alcance"].get(forma)
        if t is None or t[faixa].startswith("Indispon"):
            return None
        m = re.match(r"(\d+(?:,\d+)?)", t[faixa])
        return m.group(1) + " m" if m else None
    alcance = []
    for f in formas:
        for faixa, nome_da_faixa in enumerate(("classe 0", "classes 1 a 5", "classe 6", "classe 7")):
            partes = []
            for parte in fa.ALCANCE[f["nome"]]:
                if parte is None:
                    partes.append([""] * fa.GRAUS_NA_TABELA)
                    continue
                antes, escada, _, depois = parte
                depois = depois.replace("em você", "nela")
                if escada is None:
                    partes.append([antes + depois] * fa.GRAUS_NA_TABELA)
                    continue
                b = a_base(f["nome"], escada, faixa)
                partes.append(["—" if b is None else antes + fa.sobe(esc[escada], b, g) + depois for g in range(fa.GRAUS_NA_TABELA)])
            alcance.append([f"{f['nome']} · {nome_da_faixa}"] + [fa._ini(x) for x in partes[0]] + partes[1])
    # os talentos: o texto inteiro é o do Catálogo (o tecnica-do-livro.json), e o Próprio entra uma vez por Categoria
    faz = {p["nome"]: p["faz"] for p in TEC["passivas"]}
    talentos = []
    for t in LIV["talentos"]:
        if t["nome"] not in faz:
            raise SystemExit(f"ficha_invocacoes: o talento {t['nome']} da entidade nao esta nos Talentos do livro")
        if t["nome"] == PROPRIO:
            talentos += [{"nome": f"{PROPRIO} (CE {k})", "ce": k, "faz": "Escreva nas Anotações o benefício, o gatilho, o alcance, os usos, "
                          "o custo e se ele pode ser desligado, fechados com o mestre."} for k in t["ce"]]
        else:
            talentos.append({"nome": t["nome"], "ce": t["ce"], "faz": faz[t["nome"]]})
    teto = {n: x["ce"] for x in LIV["teto_de_ce"] for n in x["niveis"]}
    abre_tal = [1] + LIV["marcos"]
    if sorted(teto) != abre_tal or len(abre_tal) != N_TAL:
        raise SystemExit("ficha_invocacoes: os niveis em que a entidade ganha talento nao sao mais o 1 e os marcos")
    return {"LIV": LIV, "classes": classes, "formas": formas, "alcance": alcance, "pecas": RA["pecas"], "restricoes": RA["restricoes"],
            "pares": RA["pares"], "familias": RA["familias"], "notas_familia": RA["notas_familia"], "talentos": talentos,
            "abre_tal": abre_tal, "teto_tal": [teto[n] for n in abre_tal],
            "pericias": [[n, v["atributo"]] for n, v in CAT["pericias"].items()],
            "reduzidas": LIV["reduzidas"]}


# ---------------------------------------------------------------------------------------------
# Onde cada caixa mora. Uma função só, lida pela aba, pelas contas da DADOS_INVOC, pela regressão e pelo desenhador.
# ---------------------------------------------------------------------------------------------
def lugares():
    """[(número da ficha, fileira, coluna de fichas)], coluna por coluna: a 1 é a de cima da primeira coluna"""
    return [(k * N_FILEIRAS + j + 1, j, k) for k in range(N_COLUNAS) for j in range(N_FILEIRAS)]


def linha_da_fileira(j):
    return L0 + PASSO_LIN * j


def celulas_da_ficha(r, k):
    """os endereços das caixas de uma ficha: as de digitar, as de menu e as que a planilha calcula"""
    sp = lombada(k)
    a, b, c = ([x + i for i in range(N_BLOCO)] for x in blocos(k))
    g = {"lombada_num": _a1(sp, r), "lombada": _a1(sp, r + 2), "numero": _a1(a[0], r), "titulo": _a1(a[1], r),
         # --- quem ela é
         "nome": _a1(a[0], r + 4), "foto": _a1(a[0], r + 6), "tipo": _a1(a[0], r + 27), "aquis": _a1(a[0], r + 31),
         "nivel_fixo": _a1(a[2], r + 31), "talisma": _a1(a[3], r + 31),
         "fam_rot": _a1(a[0], r + 34), "fam": [_a1(a[i], r + 36) for i in range(N_FAM)],
         # --- os números
         "status": [_a1(b[i], r + 4) for i in range(5)], "pontos_rot": _a1(b[0], r + 7),
         "total": [_a1(b[i], r + 9) for i in range(N_ATR)], "pts": [_a1(b[i], r + 11) for i in range(N_ATR)],
         "buff": [_a1(b[i], r + 12) for i in range(N_ATR)],
         "stat": [_a1(b[i], r + 15) for i in range(5)], "bstat": [_a1(b[i], r + 17) for i in range(5)],
         "tr": [_a1(b[i], r + 20) for i in range(4)], "btr": [_a1(b[i], r + 22) for i in range(4)], "carga": _a1(b[4], r + 20),
         "acerto": _a1(b[0], r + 25), "fis": _a1(b[2], r + 25), "trT": _a1(b[4], r + 25),
         "per_rot": _a1(b[0], r + 28), "per": [_a1(b[0], r + 29 + i) for i in range(N_PER)],
         "perb": [_a1(b[3], r + 29 + i) for i in range(N_PER)],
         # --- a mesa
         "vida": _a1(c[0], r + 4), "vida_max": _a1(c[1], r + 4), "temp": _a1(c[2], r + 4), "delta": _a1(c[3], r + 4),
         "reserva_rot": _a1(c[4], r + 3), "reserva": _a1(c[4], r + 4), "barra": _a1(c[0], r + 6),
         "cond": _a1(c[0], r + 9), "notas": _a1(c[0], r + 18), "equip_rot": _a1(c[0], r + 28), "equip": _a1(c[0], r + 29),
         "corpo": _a1(c[0], r + 34),
         # --- embaixo
         "def": _a1(a[0], r + 40), "hab": _a1(a[0], r + O["hab"]),
         "tal_rot": _a1(a[0], r + O["tal"]), "tal_nv": [_a1(a[0], r + O["tal"] + 1 + i) for i in range(N_TAL)],
         "tal": [_a1(a[1], r + O["tal"] + 1 + i) for i in range(N_TAL)], "tal_txt": [_a1(a[4], r + O["tal"] + 1 + i) for i in range(N_TAL)],
         "talx": [_a1(a[1], r + O["talx"] + 1 + i) for i in range(N_TALX)], "talx_txt": [_a1(a[4], r + O["talx"] + 1 + i) for i in range(N_TALX)],
         "cartas": {}, "lib": [], "blocos": (a, b, c), "r": r}
    # as cartas de habilidade: a primeira fileira, as três de "mais habilidades" e a do repertório da Trilha
    pos = [(r + O["h"], x) for x in blocos(k)] + [(r + O["m"] + (ALT + 1) * (i // 3), blocos(k)[i % 3]) for i in range(len(ORDEM) - 3)]
    for (tipo, n), p in zip(ORDEM, pos):
        g["cartas"][(tipo, n)] = p
    for n in range(N_EXT):
        g["cartas"][("ext", n)] = (r + O["x"], blocos(k)[n])
    for n in range(N_LIB):
        c0, r0 = blocos(k)[n], r + O["lib"]
        g["lib"].append({"r0": r0, "c0": c0, "classe": _a1(c0, r0 + 1), "nome": _a1(c0 + 1, r0 + 1), "pe": _a1(c0 + 4, r0 + 1),
                         "como": _a1(c0, r0 + 2), "pontos": _a1(c0, r0 + 6), "acao": _a1(c0, r0 + 7)})
    c0, r0 = blocos(k)[0], r + O["tm"]
    g["tm"] = {"r0": r0, "c0": c0, "nome": _a1(c0, r0 + 1), "pe": _a1(c0 + 4, r0 + 1), "como": _a1(c0, r0 + 2),
               "dados": _a1(c0, r0 + 6), "acao": _a1(c0, r0 + 7)}
    c0 = blocos(k)[1]
    g["exp"] = {"r0": r0, "c0": c0, "nome": _a1(c0, r0 + 1), "pe": _a1(c0 + 4, r0 + 1), "como": _a1(c0, r0 + 2),
                "degrau": _a1(c0, r0 + 6), "acerto": _a1(c0 + 2, r0 + 6), "pede": _a1(c0, r0 + 7)}
    return g


def celulas_da_carta(r0, c0):
    """os endereços das caixas de uma carta de habilidade"""
    a, b, c, d, e = (c0 + k for k in range(5))
    return {"titulo": _a1(a, r0 + F_TIT), "classe": _a1(a, r0 + F_NOME), "nome": _a1(b, r0 + F_NOME), "estado": _a1(e, r0 + F_NOME),
            "como": _a1(a, r0 + F_TXT), "forma": _a1(a, r0 + F_N1), "dano": _a1(c, r0 + F_N1), "pe": _a1(e, r0 + F_N1),
            "tdano": _a1(a, r0 + F_N2), "rmenu": _a1(c, r0 + F_N2), "acao": _a1(a, r0 + F_N3), "resolve": _a1(c, r0 + F_N3),
            "alcance": _a1(a, r0 + F_ALC),
            "mel": [_a1(b, r0 + F_MEL + i) for i in range(N_MEL)], "preco": [_a1(e, r0 + F_MEL + i) for i in range(N_MEL)],
            "res": [_a1(b, r0 + F_RES + i) for i in range(N_RES)], "dev": [_a1(e, r0 + F_RES + i) for i in range(N_RES)],
            "conta": _a1(b, r0 + F_CONTA), "ampliar": _a1(b, r0 + F_AMP), "avisos": _a1(a, r0 + F_AV)}


def celulas_do_conjunto():
    d, e, f = C_CONJ, C_CONJ + 1, C_CONJ + 2
    r = L0
    return {"nivel": _a1(d, r + 4), "maestria": _a1(e, r + 4), "trilha": _a1(f, r + 4),
            "usa": _a1(d, r + 8), "ativas": _a1(e, r + 8), "corpos": _a1(f, r + 8),
            "rol_rot": _a1(d, r + 11), "rol": [_a1(d, r + 12 + i) for i in range(N_ROL)]}


# ---------------------------------------------------------------------------------------------
# A DADOS_INVOC: as tabelas, uma linha por ficha e uma por carta de habilidade.
# ---------------------------------------------------------------------------------------------
def trocas(layout, cor_da_barra=None):
    """a DADOS_INVOC inteira, e os endereços que a aba lê dela"""
    R = regras()
    LIV = R["LIV"]
    idx = ix.indice(layout)
    falta = [k for k in ("nivel", "maestria", "trilha", "atr_Essência", "atr_Inteligência", "nome") if not idx.get(k)]
    if falta:
        raise SystemExit(f"o indice da DADOS nao publica {falta}: a aba INVOCAÇÕES le essas caixas da FICHA")
    dados = ix._aba(layout, "DADOS")
    dcel = {r[0]: r for r in dados["celulas"]}
    cab = next(r[0] for r in dados["celulas"] if r[1] == "marcos")
    lin_cab = ix._lc(cab)[0]
    e_txt = next(r[2] for r in dados["celulas"] if ix._lc(r[0]) == (lin_cab + 1, 1))
    e_num = dcel[f"{cab[:-len(str(lin_cab))]}{lin_cab + 1}"][2]
    D = fa._Dados(dcel[cab][2], e_txt, e_num)
    F_ = lambda k: _A(idx[k], "FICHA!")
    CJ = celulas_do_conjunto()
    n_classes = len(R["classes"])

    # --- as tabelas do livro
    D.tabela("prog", ["nível da entidade", "classe máxima da entidade", "dados da básica", "pontos da especial"],
             [[p["de"], p["classe"], p["basica"], p["pontos"]] for p in LIV["progressao"]])
    PROG = D.faixa("prog")
    D.tabela("marcos", ["marco de atributo"], [[m] for m in LIV["marcos"]])
    MARCOS = D.faixa("marcos")
    D.tabela("classe", ["classe da especial", "leve", "média", "pesada", "leve livre", "média livre", "pesada livre",
                        "limite de melhorias", "pontos da classe"],
             [[c["classe"]] + c["precos"] + [c["limite"], c["pontos"]] for c in R["classes"]])
    PRECOS = _faixa(D.T["classe"][0] + 1, 2, D.T["classe"][0] + 6, 1 + n_classes)
    preco_da_classe = lambda c: _faixa(D.T["classe"][0] + 1, 1 + c, D.T["classe"][0] + 6, 1 + c)
    LIMITE, PONTOS = D.faixa("classe", so=7), D.faixa("classe", so=8)
    D.tabela("classe0", ["classe da escolha da trilha"], [[c] for c in range(0, n_classes + 1)])
    D.tabela("classe_lib", ["classe da liberação"], [[c] for c in range(3, n_classes + 1)])
    D.tabela("formas", ["forma", "a forma exige", "peso da forma", "restrição embutida", "tipo de dano da forma", "como resolve",
                        "resolve por teste", "degrau da primeira parte", "degrau da segunda parte", "mostra mais alvos", "existe na classe 0"],
             [[f["nome"], f["exige"], f["peso"], f["embutida"], f["tipo"], f["resolve"], f["tr"], f["grau1"], f["grau2"], f["alvos"],
               f["na_zero"]] for f in R["formas"]])
    forma_col = lambda k: D.faixa("formas", so=k)
    G_ = fa.GRAUS_NA_TABELA
    D.tabela("alcance", ["alcance de"] + [f"primeira parte +{g}" for g in range(G_)] + [f"segunda parte +{g}" for g in range(G_)], R["alcance"])
    ALC1 = _faixa(D.T["alcance"][0] + 1, 2, D.T["alcance"][0] + G_, D.T["alcance"][2])
    ALC2 = _faixa(D.T["alcance"][0] + 1 + G_, 2, D.T["alcance"][0] + 2 * G_, D.T["alcance"][2])
    D.tabela("pecas", ["peça", "família da peça", "peso da peça", "peça de controle", "efeito pela classe reduzida"],
             [[p["nome"], p["familia"] or "", p["peso"], int(p["familia"] == "Controle"), int(p["nome"] in R["reduzidas"])] for p in R["pecas"]])
    PECAS = D.faixa("pecas")
    D.tabela("res", ["menu de restrição", "restrição", "o que devolve", "é de frequência", "menu de restrição leve"],
             [[r["rotulo"], r["nome"], r["devolve"], r["frequencia"], r["rotulo"] if r["devolve"] == 1 else ""] for r in R["restricoes"]])
    RES = D.faixa("res")
    D.tabela("talentos", ["talento", "categoria de efeito", "o que o talento faz", "menu de talento da trilha"],
             [[t["nome"], t["ce"], t["faz"], t["nome"] if t["ce"] == 1 else ""] for t in R["talentos"]])
    TALENTOS = D.faixa("talentos")
    D.tabela("tipos", ["tipo de entidade"], [[t["nome"]] for t in LIV["tipos"]])
    D.tabela("aquis", ["aquisição", "acompanha o nível"], [[a["nome"], int(a["acompanha"])] for a in LIV["aquisicoes"]])
    AQUIS = D.faixa("aquis")
    D.tabela("familias", ["família"], [[f] for f in R["familias"]])
    D.tabela("atributos", ["atributo"], [[n] for n, _ in ATRS])
    ATRIBUTOS = D.faixa("atributos")
    D.tabela("testes", ["teste de resistência"], [[n] for n, _ in TESTES])
    D.tabela("fisico", ["físico usa"], [["Força"], ["Destreza"]])
    D.tabela("pericias", ["perícia", "atributo da perícia"], R["pericias"])
    PERICIAS = D.faixa("pericias")
    D.tabela("carga", ["carga do talismã"], [[SEM_CARGA], [COM_CARGA]])
    D.tabela("danos", ["tipo de dano"], [[x] for x in LIV["tipos_de_dano"]])
    D.tabela("resolve", ["resolução"], [[x] for x in RESOLVE])
    D.tabela("pontos", ["pontos no atributo"], [[x] for x in range(0, 7)])
    D.tabela("maxima", ["nível da técnica máxima", "dados fixos", "pontos de montagem da máxima", "pe da máxima"],
             [[m["de"], m["dados"], m["pontos"], m["pe"]] for m in LIV["tecnica_maxima"]])
    MAXIMA = D.faixa("maxima")
    D.tabela("expansao", ["degrau da expansão", "aquisição do degrau", "requisito do degrau"],
             [[x["degrau"], x["custa"], x["pede"]] for x in LIV["expansao"]])
    EXPANSAO = D.faixa("expansao")
    SEM_BARREIRA = LIV["expansao"][-1]["degrau"]
    D.tabela("usa", ["a defesa usa"], [["Essência"], ["Inteligência"]])

    # --- as contas do conjunto: o que vem da FICHA e o que o conjunto escolhe
    H, ordem_das_contas = {}, []
    c_contas = D.prox

    def reserva(nome):
        H[nome] = _abs(c_contas + 1, 2 + len(ordem_das_contas))
        ordem_das_contas.append(nome)
    for nome in ("nível", "maestria", "trilha", "a defesa usa", "valor da defesa", "parcela da defesa", "teto de ativas",
                 "corpos mantidos", "fichas com nome", "famílias da trilha", "cor da barra"):
        reserva(nome)
    D.tabela("contas", ["contas do conjunto", "valor do conjunto"], [[None, None] for _ in ordem_das_contas])

    # --- uma linha por ficha
    LUG = lugares()
    fichas_c = [celulas_da_ficha(linha_da_fileira(j), k) for _, j, k in LUG]
    entradas = (["ficha", "nome", "tipo", "aquis", "nfixo", "talisma"] + [f"p{i}" for i in range(N_ATR)] + [f"u{i}" for i in range(N_ATR)] +
                ["acerto", "fis", "trT"] + [f"us{i}" for i in range(5)] + [f"ut{i}" for i in range(4)] +
                ["vida_c", "temp", "reserva"] + [f"f{i}" for i in range(N_FAM)] +
                [f"per{i}" for i in range(N_PER)] + [f"tal{i}" for i in range(N_TAL)] + [f"tx{i}" for i in range(N_TALX)] +
                [f"lc{i}" for i in range(N_LIB)] + ["exp"])
    contas = (["tem", "acomp", "n", "cl", "db"] + [f"t{i}" for i in range(N_ATR)] + ["gastos", "disp", "marc", "acima", "va", "atq", "cd",
               "def", "cri", "vida", "atual", "desl", "vf"] + [f"tr{i}" for i in range(4)] + ["nper", "tper", "esp", "nbas", "ntal", "ttal",
               "ent", "ret", "resmax", "carga", "nfam", "rep", "maxfam"] +
              # o que a aba mostra
              ["d_titulo", "d_lomb", "d_mae", "d_ent", "d_ret", "d_pontos", "d_atq", "d_cd", "d_desl"] + [f"d_tr{i}" for i in range(4)] +
              ["d_per"] + [f"d_pb{i}" for i in range(N_PER)] + ["d_res", "d_equip", "d_fam", "d_hab", "d_tal"] +
              [f"ce{i}" for i in range(N_TAL)] + [f"d_tt{i}" for i in range(N_TAL)] +
              [f"d_xt{i}" for i in range(N_TALX)] + [f"d_lp{i}" for i in range(N_LIB)] + [f"d_ld{i}" for i in range(N_LIB)] +
              ["d_mp", "d_md", "d_ep", "d_ea", "d_er", "d_rol"])
    nomes_f = entradas + contas
    cFi = D.prox
    colf = {k: cFi + i for i, k in enumerate(nomes_f)}
    FCOL = lambda k: _faixa(colf[k], 2, colf[k], 1 + len(LUG))          # a coluna inteira, para INDEX e COUNTIFS
    NIV, MAE, TRI = H["nível"], H["maestria"], H["trilha"]

    def linha_de_ficha(n, i, g):
        P = lambda k: f"${L(colf[k])}{n}"
        Rg = lambda a, b: f"${L(colf[a])}{n}:${L(colf[b])}{n}"
        da = lambda cel: f'={_A(cel, IV)}&""'
        o = {"ficha": i, "nome": da(g["nome"]), "tipo": da(g["tipo"]), "aquis": da(g["aquis"]), "nfixo": f"=N({_A(g['nivel_fixo'], IV)})",
             "talisma": da(g["talisma"]), "acerto": da(g["acerto"]), "fis": da(g["fis"]), "trT": da(g["trT"]),
             "vida_c": da(g["vida"]), "temp": f"=N({_A(g['temp'], IV)})", "reserva": da(g["reserva"]), "exp": da(g["exp"]["degrau"])}
        for k in range(N_ATR):
            o[f"p{k}"], o[f"u{k}"] = f"=N({_A(g['pts'][k], IV)})", f"=N({_A(g['buff'][k], IV)})"
        for k in range(5):
            o[f"us{k}"] = f"=N({_A(g['bstat'][k], IV)})"
        for k in range(4):
            o[f"ut{k}"] = f"=N({_A(g['btr'][k], IV)})"
        for k in range(N_FAM):
            o[f"f{k}"] = da(g["fam"][k])
        for k in range(N_PER):
            o[f"per{k}"] = da(g["per"][k])
        for k in range(N_TAL):
            o[f"tal{k}"] = da(g["tal"][k])
        for k in range(N_TALX):
            o[f"tx{k}"] = da(g["talx"][k])
        for k in range(N_LIB):
            o[f"lc{k}"] = f"=MAX(3,MIN({n_classes},N({_A(g['lib'][k]['classe'], IV)})))"
        # --- daqui para baixo a fórmula é a mesma em toda linha: só as próprias colunas
        TT, PP, FF, PER, TAL = Rg("t0", f"t{N_ATR - 1}"), Rg("p0", f"p{N_ATR - 1}"), Rg("f0", f"f{N_FAM - 1}"), Rg("per0", f"per{N_PER - 1}"), Rg("tal0", f"tal{N_TAL - 1}")
        nn, cl, tem = P("n"), P("cl"), P("tem")
        o["tem"] = f'=IF({P("nome")}<>"",1,0)'
        o["acomp"] = f'=IFERROR(VLOOKUP({P("aquis")},{AQUIS},2,FALSE),1)'
        o["n"] = f'=IF({P("acomp")}=1,{NIV},MAX(1,MIN({NIV},IF({P("nfixo")}=0,{NIV},{P("nfixo")}))))'
        o["cl"] = f"=VLOOKUP(MAX(1,{nn}),{PROG},2,TRUE)"
        o["db"] = f"=VLOOKUP(MAX(1,{nn}),{PROG},3,TRUE)"
        for k in range(N_ATR):
            o[f"t{k}"] = f'={P(f"p{k}")}+{P(f"u{k}")}'
        o["gastos"] = f"=SUM({PP})"
        o["marc"] = f'=COUNTIF({MARCOS},"<="&{nn})'
        o["disp"] = f'=9+{P("marc")}'
        o["acima"] = "=" + "+".join(f'MAX(0,{P(f"p{k}")}-3)' for k in range(N_ATR))
        o["va"] = f'=IFERROR(INDEX({TT},1,MATCH({P("acerto")},{ATRIBUTOS},0)),"")'
        o["atq"] = f'=IF({P("va")}="","",{P("va")}+{MAE}+{P("us0")})'
        o["cd"] = f'=IF({P("va")}="","",8+{P("va")}+{MAE}+{P("us1")})'
        o["def"] = f'=10+{P("t1")}+{H["parcela da defesa"]}+{P("us2")}'
        o["cri"] = f'=IF({P("tipo")}="{CORPO_CRIACAO}",1,0)'
        o["vida"] = f'=5+{P("t2")}+(3+{P("cri")}+{P("t2")})*({nn}-1)+{P("us3")}'
        o["atual"] = f'=IF({P("vida_c")}="",{P("vida")},MAX(0,MIN(IFERROR(VALUE({P("vida_c")}),{P("vida")}),{P("vida")})))'
        o["desl"] = f'=9+{P("us4")}'
        o["vf"] = f'=IF({P("fis")}="Destreza",{P("t1")},{P("t0")})'
        for k, (nome_tr, atr) in enumerate(TESTES):
            base = P("vf") if atr is None else P(f"t{atr}")
            o[f"tr{k}"] = f'={base}+IF({P("trT")}="{nome_tr}",{MAE},0)+{P(f"ut{k}")}'
        o["nper"] = f'=4+INT({P("p3")}/2)'
        o["tper"] = f'=COUNTIF({PER},"?*")'
        o["esp"] = f"=INT((2+{nn}/2)/2)"
        o["nbas"] = f"=IF({nn}>={ABRE_BAS[1]},2,1)"
        o["ntal"] = f'=1+{P("marc")}'
        o["ttal"] = f'=COUNTIF({TAL},"?*")'
        o["ent"] = f'=IF(AND({P("tipo")}="{SH_CRIACAO}",{P("talisma")}="{COM_CARGA}"),MAX(1,CEILING({cl}/2,1)),{cl})'
        # o retorno da caída custa 2 × Classe; a carga do talismã abate só o que adiantou (Classe 4: 8 ao todo, os 2
        # adiantados e mais 6 no retorno). Sem carga a entrada é a Classe, e a conta dá os 2 × Classe.
        o["ret"] = f'={cl}+{P("ent")}'
        o["resmax"] = f'={nn}*(1+INT({P("p4")}/3))'
        o["carga"] = f'=5+{P("t0")}'
        o["nfam"] = f'=COUNTIF({FF},"?*")'
        o["rep"] = "=" + "+".join(f'IF({P(f"f{k}")}="",0,IF(COUNTIF({FF},{P(f"f{k}")})>1,1,0))' for k in range(N_FAM))
        o["maxfam"] = f"={H['famílias da trilha']}"
        # --- o que a aba mostra
        o["d_titulo"] = (f'=IF({tem}=0,"INVOCAÇÃO {i} · lugar vazio",{P("nome")}&" · "&{P("tipo")}&" · nível "&{nn}&" · vida "&{P("atual")}&" de "&{P("vida")})')
        o["d_lomb"] = f'=IF({tem}=0,"VAZIA",UPPER({P("nome")}))'
        o["d_mae"] = f"={sinal(MAE)}"
        o["d_ent"] = f'={P("ent")}&" PE"'
        o["d_ret"] = f'={P("ret")}&" PE"'
        o["d_pontos"] = (f'=IF(OR({P("gastos")}>{P("disp")},{P("acima")}>{P("marc")}),"{T_ERRO} ",IF(AND({tem}=1,{P("gastos")}<{P("disp")}),"{T_AVISO}",""))'
                         f'&"ATRIBUTOS · "&{P("gastos")}&" DE "&{P("disp")}&" PONTOS"&IF({P("acima")}>{P("marc")}," · ACIMA DE 3 SÓ COM MARCO","")')
        o["d_atq"] = f'=IF({P("atq")}="","",{sinal(P("atq"))})'
        o["d_cd"] = f'=IF({P("cd")}="","",{P("cd")})'
        o["d_desl"] = f'=SUBSTITUTE({P("desl")}&" m",".",",")'
        for k in range(4):
            o[f"d_tr{k}"] = f'={sinal(P(f"tr{k}"))}'
        o["d_per"] = f'=IF({P("tper")}>{P("nper")},"{T_ERRO} ","")&"PERÍCIAS · "&{P("tper")}&" DE "&{P("nper")}'
        for k in range(N_PER):
            pk = P(f"per{k}")
            o[f"d_pb{k}"] = f'=IF({pk}="","",IFERROR({sinal(f"(INDEX({TT},1,MATCH(VLOOKUP({pk},{PERICIAS},2,FALSE),{ATRIBUTOS},0))+{MAE})")},""))'
        o["d_res"] = f'=IF({P("tipo")}="{DOMADA}","RESERVA · MÁX. "&{P("resmax")},"RESERVA DE PE")'
        o["d_equip"] = f'="EQUIPAMENTO · CARGA ATÉ "&{P("carga")}&" DE VOLUME"'
        o["d_fam"] = (f'=IF(OR({P("rep")}>0,{P("nfam")}>{P("maxfam")}),"{T_ERRO} ","")&"FAMÍLIAS · "&{P("nfam")}&" ABERTAS"'
                      f'&IF({P("rep")}>0," · REPETIDA","")&IF({P("nfam")}>{P("maxfam")}," · O LIMITE É "&{P("maxfam")},"")')
        o["d_hab"] = (f'="HABILIDADES · básica de "&{P("db")}&"d6 · "&{P("esp")}&IF({P("esp")}>1," espaços"," espaço")&" de especial até a Classe "&{cl}'
                      f'&" · "&{P("ntal")}&IF({P("ntal")}>1," talentos"," talento")')
        o["d_tal"] = f'=IF({P("ttal")}>{P("ntal")},"{T_ERRO} ","")&"TALENTOS · "&{P("ttal")}&" DE "&{P("ntal")}'
        for k in range(N_TAL):
            abre, teto, tk = R["abre_tal"][k], R["teto_tal"][k], P(f"tal{k}")
            o[f"ce{k}"] = f"=IFERROR(VLOOKUP({tk},{TALENTOS},2,FALSE),0)"
            o[f"d_tt{k}"] = (f'=IF({tk}="","",IF({abre}>{nn},"{T_ERRO} Este talento abre no nível {abre}",IF({P(f"ce{k}")}>{teto},'
                             f'"{T_ERRO} Categoria "&{P(f"ce{k}")}&": este ganho vai até a {teto} · ","")&IFERROR(VLOOKUP({tk},{TALENTOS},3,FALSE),"")))')
        for k in range(N_TALX):
            tk = P(f"tx{k}")
            o[f"d_xt{k}"] = f'=IF({tk}="","",IFERROR(VLOOKUP({tk},{TALENTOS},3,FALSE),""))'
        for k in range(N_LIB):
            ck = P(f"lc{k}")
            o[f"d_lp{k}"] = f'=CEILING(4.5*{ck},1)&" PE"'
            o[f"d_ld{k}"] = f'=INDEX({PONTOS},{ck})&" pontos + "&{ck}&"d8"'
        n_tm = LIV["tecnica_maxima"][0]["de"]
        o["d_mp"] = f'=IF({nn}<{n_tm},"—",VLOOKUP({nn},{MAXIMA},4,TRUE)&" PE")'
        o["d_md"] = f'=IF({nn}<{n_tm},"Abre no nível {n_tm}",VLOOKUP({nn},{MAXIMA},2,TRUE)&" fixos · "&VLOOKUP({nn},{MAXIMA},3,TRUE)&" pontos")'
        o["d_ep"] = f'=IF({P("exp")}="{SEM_BARREIRA}",7,6)*{cl}&" PE"'
        o["d_ea"] = f'="Acerto "&{cl}&"d8"'
        o["d_er"] = f'=IFERROR(VLOOKUP({P("exp")},{EXPANSAO},3,FALSE),"Escolha o degrau")'
        o["d_rol"] = (f'={i}&" · "&IF({tem}=0,"vazia",{P("nome")}&" · nv "&{nn}&" · "&{P("atual")}&"/"&{P("vida")})')
        return [o[k] for k in nomes_f]

    D.tabela("fichas", [("conta de ficha" if k == "ficha" else k) for k in nomes_f], [[None] for _ in LUG])
    for i, ((num, _, _), g) in enumerate(zip(LUG, fichas_c)):
        for j, v in enumerate(linha_de_ficha(2 + i, num, g)):
            D.poe(cFi + j, 2 + i, v)
    FI = lambda k, i: _abs(colf[k], 2 + i, DI)

    # --- as contas do conjunto, agora que as fichas têm endereço
    formulas = {
        "nível": f"=MAX(1,N({F_('nivel')}))",
        "maestria": f"=N({F_('maestria')})",
        "trilha": f'={F_("trilha")}&""',
        "a defesa usa": f'={_A(CJ["usa"], IV)}&""',
        "valor da defesa": f'=IF({H["a defesa usa"]}="Inteligência",N({F_("atr_Inteligência")}),N({F_("atr_Essência")}))',
        "parcela da defesa": f"=INT({H['valor da defesa']}/2)",
        "teto de ativas": f'=IF({H["trilha"]}="{MULTIPLAS}",4,2)',
        "corpos mantidos": f"={H['valor da defesa']}+{H['teto de ativas']}",
        "fichas com nome": f"=SUM({FCOL('tem')})",
        "famílias da trilha": f'=IF({H["trilha"]}="{PRINCIPAL}",5,IF(OR({H["trilha"]}="{PARCERIA}",{H["trilha"]}="{MULTIPLAS}"),4,3))',
        "cor da barra": f"={cor_da_barra}" if cor_da_barra else f'="#{OSSO[2:]}"',
    }
    assert set(formulas) == set(ordem_das_contas)
    for i, k in enumerate(ordem_das_contas):
        D.poe(c_contas, 2 + i, k)
        D.poe(c_contas + 1, 2 + i, formulas[k])
    HI = {k: v.replace("$" + L(c_contas + 1) + "$", DI + "$" + L(c_contas + 1) + "$") for k, v in H.items()}

    # --- a lista do conjunto leva até cada ficha (07/10/2026). A ligação dentro da planilha pede o número da aba, que só
    # existe depois que ela nasce: é o acabamento do construir() que escreve cada uma (ligarSaltos_, no Codigo.gs), lendo
    # daqui a caixa da lista, o alvo e a célula do texto, como nos saltos da FICHA AMALDIÇOADA. O alvo é o número da
    # lombada da ficha, que fica à vista com a fileira e a coluna de fichas fechadas.
    D.tabela("saltos", ["salto", "caixa do salto", "alvo do salto", "nome do salto"],
             [[f"Invocação {i + 1}", fp._endereco(celulas_do_conjunto()["rol"][i], IV), fp._endereco(fichas_c[i]["lombada_num"], IV),
               FI("d_rol", i)] for i in range(len(LUG))])

    # --- os menus de cada ficha: só as Famílias abertas dela aparecem
    menus = []
    c_p0, c_f0 = D.T["pecas"][0], D.T["formas"][0]
    for i in range(len(LUG)):
        FAMS = f"${L(colf['f0'])}${2 + i}:${L(colf[f'f{N_FAM - 1}'])}${2 + i}"
        aberta = lambda fam: f'OR({fam}="",COUNTIF({FAMS},{fam})>0)'
        c0 = D.prox
        D.tabela(f"menu{i}", [f"menu de melhoria da ficha {i + 1}", f"menu de melhoria leve da ficha {i + 1}"],
                 [[(lambda n: f'=IF({aberta(f"${L(c_p0 + 1)}{n}")},${L(c_p0)}{n},"")'),
                   (lambda n: f'=IF(AND(${L(c_p0 + 2)}{n}=1,{aberta(f"${L(c_p0 + 1)}{n}")}),${L(c_p0)}{n},"")')] for _ in R["pecas"]])
        D.tabela(f"menuf{i}", [f"menu de forma da ficha {i + 1}", f"menu de forma da classe 0 da ficha {i + 1}"],
                 [[(lambda n: f'=IF({aberta(f"${L(c_f0 + 1)}{n}")},${L(c_f0)}{n},"")'),
                   (lambda n: f'=IF(AND(${L(c_f0 + 10)}{n}=1,{aberta(f"${L(c_f0 + 1)}{n}")}),${L(c_f0)}{n},"")')] for _ in R["formas"]])
        menus.append({"mel": D.faixa(f"menu{i}", so=0, aba=DI), "leve": D.faixa(f"menu{i}", so=1, aba=DI),
                      "forma": D.faixa(f"menuf{i}", so=0, aba=DI), "forma0": D.faixa(f"menuf{i}", so=1, aba=DI)})

    # --- a conta de cada carta de habilidade: uma linha por carta
    nomes = (["lugar", "ficha", "tipo", "abre", "tit", "classe", "nome", "forma", "tdano", "rmenu"] + [f"m{i}" for i in range(1, N_MEL + 1)] +
             [f"r{i}" for i in range(1, N_RES + 1)] +
             ["tem", "nv", "mx", "db", "atk", "cdf", "lf"] + [f"f{i}" for i in range(1, N_MEL + 1)] + [f"w{i}" for i in range(1, N_MEL + 1)] +
             [f"k{i}" for i in range(N_MEL + 1)] + [f"x{i}" for i in range(N_MEL + 1)] + ["ct", "rdz", "emb", "tp", "tr"] +
             [f"c{i}" for i in range(1, N_RES + 1)] + [f"b{i}" for i in range(1, N_RES + 1)] + [f"n{j}" for j in range(1, 7)] +
             ["dL", "dM", "nm", "nr", "g", "dv0", "dv", "usa", "perde", "pts", "s", "d", "dep"] +
             [f"d{c['classe']}" for c in R["classes"]] + [f"t{c['classe']}" for c in R["classes"]] +
             ["erros", "ne", "avisos", "na", "estado", "linha", "titulo", "pe", "acao", "rs", "resolve", "dano", "lg", "mr", "q1", "q2", "alcance",
              "conta", "ampliar"] + [f"pt{i}" for i in range(1, N_MEL + 1)] + [f"dt{i}" for i in range(1, N_RES + 1)])
    cC = D.prox
    col = {k: cC + i for i, k in enumerate(nomes)}
    TIPO = {"bas": 0, "esp": 1, "ext": 2}
    cartas = []                               # (ficha de 0, tipo, número, células, título)
    for i, g in enumerate(fichas_c):
        for (tipo, n), pos in g["cartas"].items():
            titulo = {"bas": f"BÁSICA {n + 1}", "esp": f"ESPECIAL {n + 1}", "ext": f"ESCOLHA DA TRILHA {n + 1}"}[tipo]
            abre = ABRE_BAS[n] if tipo == "bas" else ABRE_ESP[n] if tipo == "esp" else 0
            cartas.append((i, tipo, n, celulas_da_carta(*pos), titulo, abre))
    FAMT = _faixa(colf["f0"], 2, colf[f"f{N_FAM - 1}"], 1 + len(LUG))

    def linha_de_carta(n, carta):
        i, tipo, num, cel, titulo, abre = carta
        P = lambda k: f"${L(col[k])}{n}"
        Rg = lambda a, b: f"${L(col[a])}{n}:${L(col[b])}{n}"
        M, RR, BB, KK, CC, NN = Rg("m1", f"m{N_MEL}"), Rg("r1", f"r{N_RES}"), Rg("b1", f"b{N_RES}"), Rg("k0", f"k{N_MEL}"), Rg("c1", f"c{N_RES}"), Rg("n1", "n6")
        WW = Rg("w1", f"w{N_MEL}")
        tem_m = lambda nome: f'COUNTIF({M},"{nome}")'
        tem_b = lambda nome: f'COUNTIF({BB},"{nome}")'
        tem = lambda nome: f'({tem_m(nome)}+{tem_b(nome)})'
        Cc, forma, lf, fi = P("classe"), P("forma"), P("lf"), P("ficha")
        da_forma = lambda k: f"IF({lf}=0,0,INDEX({forma_col(k)},{lf}))"
        da_ficha = lambda k: f"INDEX({FCOL(k)},{fi})"
        FAMS = f"INDEX({FAMT},{fi},0)"
        o = {"lugar": f"Ficha {i + 1} · {titulo.capitalize()}", "ficha": i + 1, "tipo": TIPO[tipo], "abre": abre, "tit": titulo,
             "classe": 0 if tipo == "bas" else f"=MAX({0 if tipo == 'ext' else 1},MIN({n_classes},N({_A(cel['classe'], IV)})))",
             "nome": f'={_A(cel["nome"], IV)}&""', "forma": f'={_A(cel["forma"], IV)}&""', "tdano": f'={_A(cel["tdano"], IV)}&""',
             "rmenu": f'={_A(cel["rmenu"], IV)}&""'}
        for k in range(N_MEL):
            o[f"m{k + 1}"] = f'={_A(cel["mel"][k], IV)}&""'
        for k in range(N_RES):
            o[f"r{k + 1}"] = f'={_A(cel["res"][k], IV)}&""'
        # --- daqui para baixo a fórmula é a mesma em toda linha
        o["tem"] = f'=IF({P("nome")}<>"",1,0)'
        o["nv"], o["mx"], o["db"] = "=" + da_ficha("n"), "=" + da_ficha("cl"), "=" + da_ficha("db")
        o["atk"], o["cdf"] = "=" + da_ficha("atq"), "=" + da_ficha("cd")
        o["lf"] = f"=IFERROR(MATCH({forma},{forma_col(0)},0),0)"
        for k in range(1, N_MEL + 1):
            mk, fk, wk = P(f"m{k}"), P(f"f{k}"), P(f"w{k}")
            o[f"f{k}"] = f'=IFERROR(VLOOKUP({mk},{PECAS},2,FALSE),"")'
            o[f"w{k}"] = f"=IFERROR(VLOOKUP({mk},{PECAS},3,FALSE),0)"
            # o código de preço: o peso, e três a mais se a Família é uma das Livres da ficha
            o[f"k{k}"] = f'=IF(OR({wk}=0,{Cc}=0),0,{wk}+3*IF(AND({fk}<>"",OR({fk}={da_ficha("f0")},{fk}={da_ficha("f1")})),1,0))'
            o[f"x{k}"] = f'=IF(OR({wk}=0,{fk}=""),0,IF(COUNTIF({FAMS},{fk})=0,1,0))'
        # a Forma não recebe o desconto da Família Livre
        o["k0"] = f"=IF({Cc}=0,0,{da_forma(2)})"
        o["x0"] = f'=IF({lf}=0,0,IF(INDEX({forma_col(1)},{lf})="",0,IF(COUNTIF({FAMS},INDEX({forma_col(1)},{lf}))=0,1,0)))'
        o["ct"] = "=" + "+".join(f"IFERROR(VLOOKUP({P(f'm{k}')},{PECAS},4,FALSE),0)" for k in range(1, N_MEL + 1))
        o["rdz"] = "=TEXTJOIN(\", \",TRUE," + ",".join(f'IF(IFERROR(VLOOKUP({P(f"m{k}")},{PECAS},5,FALSE),0)=1,{P(f"m{k}")},"")' for k in range(1, N_MEL + 1)) + ")"
        o["emb"], o["tp"], o["tr"] = "=" + da_forma(3), "=" + da_forma(4), "=" + da_forma(6)
        for k in range(1, N_RES + 1):
            o[f"c{k}"] = f"=IFERROR(VLOOKUP({P(f'r{k}')},{RES},3,FALSE),0)"
            o[f"b{k}"] = f'=IFERROR(VLOOKUP({P(f"r{k}")},{RES},2,FALSE),"")'
        for j in range(1, 7):
            o[f"n{j}"] = f"=COUNTIF({KK},{j})"
        o["dL"] = f"=COUNTIF({CC},1)"
        o["dM"] = f"=COUNTIF({CC},2)+{P('emb')}"
        o["nm"] = f'=COUNTIF({M},"?*")'
        o["nr"] = f'=COUNTIF({RR},"?*")+{P("emb")}'
        o["g"] = f"=IF({Cc}=0,0,SUMPRODUCT({NN},INDEX({PRECOS},MAX(1,{Cc}),0)))"
        o["dv0"] = f"=IF({Cc}=0,0,{P('dL')}*CEILING({Cc}/2,1)+{P('dM')}*{Cc})"
        o["dv"] = f"=MIN(2*{Cc},{P('dv0')})"
        o["usa"] = f"=MIN({P('dv')},{P('g')})"
        o["perde"] = f"={P('dv')}-{P('usa')}"
        o["pts"] = f"=IF({Cc}=0,0,INDEX({PONTOS},MAX(1,{Cc})))"
        o["s"] = f"={P('pts')}-{P('g')}+{P('usa')}"
        # na básica o dano são os dados do nível, e a Melhoria Leve tira um
        o["d"] = f"=IF({Cc}=0,MAX(0,{P('db')}-IF({P('nm')}>0,1,0)),MAX(0,{P('s')}))"
        o["dep"] = f"=IF({Cc}=0,0,(" + "+".join(f"IF({tem_m(x)}>0,1,0)" for x in fa.SOMAM_METADE) + f")*FLOOR({P('d')}/2,1))"
        for c in R["classes"]:
            k = c["classe"]
            gk = f"SUMPRODUCT({NN},{preco_da_classe(k)})"
            o[f"d{k}"] = f"=MAX(0,{c['pontos']}-{gk}+MIN({2 * k},{P('dL')}*{math.ceil(k / 2)}+{P('dM')}*{k},{gk}))"
            dk, tp = P(f"d{k}"), P("tp")
            o[f"t{k}"] = (f'=IF({tp}=2,3*{dk}&" de vida temp.",IF({tp}=3,"sem dano",IF({dk}=0,IF({tp}=1,"sem cura","sem dano"),'
                          f'IF({tp}=1,"cura ","")&{dk}&"d8")))')
        NV, MAXC = P("nv"), P("mx")
        cac, tudo, ines = "Corpo a Corpo", "Tudo ou Nada", "Inescapável"
        erros = [
            _se(f'{P("abre")}>{NV}', f'"Este lugar abre no nível "&{P("abre")}'),
            _se(f"{Cc}>{MAXC}", f'"Classe "&{Cc}&": o nível "&{NV}&" libera até a "&{MAXC}'),
            _se(f'{P("x0")}=1', f'"A Forma "&{forma}&" pede "&INDEX({forma_col(1)},{lf})&" aberta"'),
            _se(f'AND({Cc}=0,{lf}>0,{da_forma(10)}=0)', f'{forma}&" não existe na Classe 0"'),
        ] + [_se(f'{P(f"x{k}")}=1', f'"Família Fechada: "&{P(f"m{k}")}') for k in range(1, N_MEL + 1)] + [
            _se(f'AND({Cc}>0,{P("nm")}>INDEX({LIMITE},MAX(1,{Cc})))', f'{P("nm")}&" Melhorias: a Classe "&{Cc}&" aceita "&INDEX({LIMITE},MAX(1,{Cc}))'),
            _se(f'AND({Cc}=0,{P("nm")}>1)', '"A básica aceita uma Melhoria"'),
            _se(f'AND({Cc}=0,COUNTIF({WW},">1")>0)', '"A básica só aceita Melhoria Leve"'),
            _se(f'AND({Cc}>0,{P("nr")}>{N_RES})', f'{P("nr")}&" Restrições"&IF({P("emb")}=1,", contando a que a Forma "&{forma}&" já traz","")&": o limite é {N_RES}"'),
            _se(f'AND({Cc}=0,COUNTIF({RR},"?*")>1)', '"A básica aceita uma Restrição Leve"'),
            _se(f'AND({Cc}=0,COUNTIF({CC},2)>0)', '"A básica só aceita Restrição Leve"'),
            _se(f'AND({Cc}>0,{P("s")}<0)', f'"Orçamento estourado: faltam "&(-{P("s")})&IF({P("s")}<-1," pontos"," ponto")'),
            _se("+".join(f"IFERROR(VLOOKUP({P(f'r{k}')},{RES},4,FALSE),0)" for k in range(1, N_RES + 1)) + ">1",
                f'{P("b1")}&" e "&{P("b2")}&" são as duas de frequência"'),
        ] + [_se(f"AND({tem(a)}>0,{tem(b)}>0)", f'"{a} não entra com {b}"') for a, b in R["pares"]] + [
            _se(f'AND({tem_b(cac)}>0,{P("emb")}=0,OR({forma}="Cone",{forma}="Linha"))', f'"{cac} não entra em "&{forma}'),
            _se(f'AND({tem_b(cac)}>0,{P("emb")}=1)', f'"A Forma "&{forma}&" já traz o {cac}"'),
            _se(f'AND({tem_b(tudo)}>0,{P("tr")}=0)', f'"{tudo} só entra em habilidade de Teste de Resistência"'),
            _se(f'AND({tem_m(ines)}>0,OR({P("nm")}>1,{P("nr")}>0))', f'"{ines} não aceita outra peça"'),
            _se(f'AND({Cc}>0,{P("d")}*IF({tem_m(fa.MULTIPLICA[0])}>0,{fa.MULTIPLICA[1]},1)+{P("dep")}>4*{Cc})',
                f'({P("d")}*IF({tem_m(fa.MULTIPLICA[0])}>0,{fa.MULTIPLICA[1]},1)+{P("dep")})&" dados somando repetições'
                f'"&IF({tem_m(fa.MULTIPLICA[0])}>0," e o Remate","")&": o teto da Classe "&{Cc}&" é "&4*{Cc}'),
        ]
        conta_txt = lambda x: f'IF({x}="",0,(LEN({x})-LEN(SUBSTITUTE({x}," · ","")))/3+1)'
        o["erros"] = f'=IF({P("tem")}=0,"",TEXTJOIN(" · ",TRUE,{",".join(erros)}))'
        o["ne"] = "=" + conta_txt(P("erros"))
        com_dano = f'AND({Cc}>0,{P("tp")}=0)'
        avisos = [
            _se(f'{P("dv0")}>2*{Cc}', f'"A devolução parou no teto de "&2*{Cc}'),
            _se(f'{P("perde")}>0', f'"Devolução perdida: "&{P("perde")}&IF({P("perde")}>1," pontos"," ponto")&" sem peça para pagar"'),
            _se(f'AND({P("ct")}>0,{com_dano},{P("d")}=0)', '"Controle sem dano: uma rodada a mais e CD +2"'),
            _se(f'AND({P("ct")}>0,{com_dano},{P("d")}>0,{P("d")}<={Cc})', '"Controle com saldo até a Classe: uma rodada a mais"'),
            _se(f'AND({Cc}>0,{P("rdz")}<>"")', f'"Efeito de "&{P("rdz")}&" pela Classe "&MAX(1,{Cc}-1)'),
        ]
        o["avisos"] = f'=IF({P("tem")}=0,"",TEXTJOIN(" · ",TRUE,{",".join(avisos)}))'
        o["na"] = "=" + conta_txt(P("avisos"))
        o["estado"] = (f'=IF({P("tem")}=0,IF({P("nm")}+COUNTIF({RR},"?*")>0,"{SEM_NOME}",""),IF({P("ne")}>0,"{T_ERRO} "&{P("ne")}&IF({P("ne")}>1," erros"," erro"),'
                       f'IF({P("na")}>0,"{T_AVISO}"&{P("na")}&IF({P("na")}>1," avisos"," aviso"),"{NA_REGRA}")))')
        o["linha"] = (f'=IF({P("tem")}=0,"",IF({P("ne")}+{P("na")}=0,"{DENTRO}",{P("erros")}&IF(AND({P("ne")}>0,{P("na")}>0)," · ","")&{P("avisos")}))')
        o["titulo"] = f'=IF({P("abre")}>{NV},{P("tit")}&" · ABRE NO NÍVEL "&{P("abre")},{P("tit")})'
        o["pe"] = f'=IF({P("tem")}=0,"",IF({Cc}=0,"Sem PE",3*{Cc}&" PE"))'
        o["acao"] = (f'=IF({P("tem")}=0,"",IF({Cc}=0,"A atuação básica dela",IF({tem_b("Atrasar")}>0,"Sua Ação Completa",IF({tem_m("Rápido")}>0,"Sua Bônus",'
                     f'IF({tem_m("Reação")}>0,"Sua Reação","Sua Padrão")))&" + a básica dela"&IF({tem_m("Reação")}>0," e a coletiva","")'
                     f'&IF({tem_b("Carregar")}>0," · em dois turnos","")))')
        # a resolução: a do menu, ou a que a Forma traz
        o["rs"] = f'=IF({P("rmenu")}<>"",{P("rmenu")},IF({lf}=0,"",INDEX({forma_col(5)},{lf})))'
        rs = P("rs")
        atq_total = f'({P("atk")}+2*IF({tem_m("Precisão")}>0,1,0))'
        o["resolve"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",IF({tem_m(ines)}>0,"Automático",IF({rs}="Ataque",IF({P("atk")}="","Ataque","Ataque "&{sinal(atq_total)}),'
                        f'IF(LEFT({rs},2)="TR",{rs}&IF({P("cdf")}="",""," · CD "&{P("cdf")})&IF({tem_m("Certeiro")}>0," · metade",""),"Sem rolagem"))))')
        tC = f'INDEX({Rg("t1", f"t{n_classes}")},1,MAX(1,{Cc}))'
        tC = f'UPPER(LEFT({tC},1))&MID({tC},2,99)'
        tipo_do_dano = f'IF({P("tdano")}="",""," "&{P("tdano")})'
        o["dano"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",IF({Cc}=0,IF(OR({P("tp")}>=1,{P("d")}=0),"Sem dano",{P("d")}&"d6"&{tipo_do_dano}),'
                     f'IF(OR({P("tp")}>=1,{P("d")}=0),{tC},{tC}&{tipo_do_dano}&IF({P("dep")}>0," · +"&{P("dep")}&"d8",""))))')
        o["lg"] = f'={tem_m("Longe")}+3*{tem_m("Muito Longe")}'
        o["mr"] = f'={tem_m("Maior")}+3*{tem_m("Muito Maior")}'
        grau = lambda k: f'IF({lf}=0,0,CHOOSE(1+INDEX({forma_col(k)},{lf}),0,{P("lg")},{P("mr")},{P("lg")}+{P("mr")}))'
        o["q1"], o["q2"] = "=" + grau(7), "=" + grau(8)
        na_tabela = f"({lf}-1)*4+IF({Cc}=0,1,IF({Cc}<=5,2,IF({Cc}=6,3,4)))"
        alvos = tem_m("Mais Um")
        o["alcance"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",INDEX({ALC1},{na_tabela},1+MIN({G_ - 1},{P("q1")}))&'
                        f'INDEX({ALC2},{na_tabela},1+MIN({G_ - 1},{P("q2")}))&'
                        f'IF(INDEX({forma_col(9)},{lf})=1,IF({alvos}>0," · +"&{alvos}&IF({alvos}>1," alvos"," alvo"),"")&'
                        f'IF({tem_m("Rajada")}>0,IF({Cc}=0," · 1 tiro"," · "&(MAX(1,{Cc}-1)+1)&" tiros"),""),""))')
        o["conta"] = (f'=IF({P("tem")}=0,"",IF({Cc}=0,{P("db")}&"d6"&IF({P("nm")}>0," − 1 = "&{P("d")}&"d6"," da básica do nível "&{NV}),'
                      f'{P("pts")}&" − "&{P("g")}&" + "&{P("usa")}&" = "&{P("s")}&" · teto "&4*{Cc}&"d8"&'
                      f'IF({P("emb")}=1," · a Forma devolve "&{Cc},"")&IF({P("perde")}>0," · perde "&{P("perde")},"")))')
        termos = [f'IF(AND({k}>{Cc},{k}<={MAXC}),"{k} → "&{P(f"t{k}")}&", {3 * k} PE","")' for k in range(2, n_classes + 1)]
        o["ampliar"] = (f'=IF({P("tem")}=0,"",IF({Cc}=0,"A básica não amplia: os dados dela sobem com o nível",IF({Cc}>={MAXC},'
                        f'"Já está na maior Classe que o nível liberou",TEXTJOIN(" · ",TRUE,{",".join(termos)}))))')
        pesos = ",".join(f'"{p}"' for p in list(fa.NOME_DO_PESO) + [p + " · Livre" for p in fa.NOME_DO_PESO])
        for k in range(1, N_MEL + 1):
            kk, wk = P(f"k{k}"), P(f"w{k}")
            o[f"pt{k}"] = (f'=IF(OR({P("tem")}=0,{wk}=0),"",IF({Cc}=0,"−1 dado","−"&INDEX({PRECOS},MAX(1,{Cc}),MAX(1,{kk}))&" · "&CHOOSE(MAX(1,{kk}),{pesos})))')
        for k in range(1, N_RES + 1):
            c = P(f"c{k}")
            o[f"dt{k}"] = f'=IF(OR({P("tem")}=0,{P(f"r{k}")}=""),"",IF({Cc}=0,"não devolve","+"&IF({c}=1,CEILING({Cc}/2,1),{Cc})))'
        return [o[k] for k in nomes]

    D.tabela("cartas", [("conta de habilidade" if k == "lugar" else k) for k in nomes], [[None] for _ in cartas])
    for i, carta in enumerate(cartas):
        for j, v in enumerate(linha_de_carta(2 + i, carta)):
            D.poe(cC + j, 2 + i, v)
    CARTA = lambda k, i: _abs(col[k], 2 + i, DI)

    aba_dados = {
        "nome": DADOS_IV, "estado": "hidden", "linhas": D.linhas, "colunas": D.prox - 2,
        "colunas_larg": [[1, D.prox - 2, dados["colunas_larg"][0][2]]], "linhas_alt": [],
        "altura_padrao": dados.get("altura_padrao"), "grade": dados["grade"],
        "celulas": [[k, v[0], v[1]] for k, v in D.cel.items()],
        "mescladas": [], "menus": [], "condicional": [], "imagens": [],
        "abaixo": True,
    }
    return {"aba_dados": aba_dados, "R": R, "D": D, "H": HI, "FI": FI, "CARTA": CARTA, "fichas_c": fichas_c, "cartas": cartas,
            "menus": menus, "CJ": CJ, "LUG": LUG, "colf": colf, "col": col, "nomes_f": nomes_f, "nomes_c": nomes}


# ---------------------------------------------------------------------------------------------
# A aba.
# ---------------------------------------------------------------------------------------------
NOTAS = {
    "nome": "O nome da invocação. A ficha só calcula quem tem nome.",
    "foto": "Clique na caixa e use Inserir › Imagem › Inserir imagem na célula.",
    "tipo": "O tipo combina origem e corpo. O shikigami de técnica é a referência; o corpo de criação ganha 4 + Constituição de vida "
            "por nível; o shikigami de criação mora num talismã; a domada conserva o nível em que foi domada.",
    "aquis": "Como ela foi obtida. Espaço conhecido e lista de ritual acompanham o seu nível. Domada e criada ficam no nível em que "
             "foram obtidas: escreva ele ao lado.",
    "nivel_fixo": "Só para a domada e a criada: o nível em que ela foi obtida, até o seu. Em branco, a ficha usa o seu nível.",
    "talisma": "Só o shikigami de criação: a carga deixada no talismã no descanso longo adianta parte da próxima entrada. O "
               "talismã ocupa 0,5 de Volume.",
    "nivel": "O nível dela. Com espaço conhecido ou lista de ritual é o seu; domada e criada ficam no nível em que foram obtidas.",
    "classe": "A maior Classe que o nível dela permite: sobe nos níveis 5, 9, 13, 17, 21 e 26.",
    "maestria": "Sempre a sua, mesmo numa domada de nível menor. Vem da FICHA.",
    "entrada": "Manifestar custa a maior Classe dela em PE, e a sua Ação Bônus. Com o talismã carregado, metade, para cima. "
               "Recolher não custa PE.",
    "retorno": "Trazer de volta quem caiu sem ser destruída: o dobro da entrada. Ela volta com metade da vida máxima.",
    "pontos": "9 pontos, cada atributo entre 0 e 3, e mais 1 ponto nos níveis 6, 10, 14, 18, 22, 26 e 30. O teto é 6.",
    "atributo": "O número grande é o total. Embaixo dele, os pontos que você distribuiu, e embaixo o Buff/Debuff.",
    "bd": "Buff/Debuff: o que você digitar aqui soma, ou tira, do número de cima.",
    "ataque": "Atributo de acerto + a sua maestria.",
    "cd": "8 + atributo de acerto + a sua maestria.",
    "defesa": "10 + Destreza dela + metade da sua Essência ou Inteligência, a que o conjunto escolheu. Com traje ou revestimento, a "
              "proteção entra no lugar dessa metade: acerte a diferença no Buff/Debuff.",
    "vida": "5 + Constituição + (3 + Constituição) × (nível − 1). No corpo amaldiçoado de criação, 4 no lugar do 3.",
    "desl": "O deslocamento terrestre-base é de 9 m.",
    "tr": "O atributo do teste, mais a sua maestria no treinado. O Físico usa Força ou Destreza, a que você escolher embaixo.",
    "carga": "5 + Força, em Volume: o que ela veste, empunha ou leva.",
    "acerto": "Escolhido na montagem. Vale para o ataque e para a CD. Com arma empunhada, o ataque usa o atributo da arma e tem "
              "desvantagem, porque a entidade não tem treino em armas.",
    "pericias": "4 + metade da Inteligência, para baixo. O número ao lado é o atributo da perícia mais a sua maestria.",
    "delta": "Escreva −9 ou +5 e aperte Enter: a ficha aplica na vida atual e limpa a caixa. A perda gasta a vida temporária "
             "primeiro, e a vida não passa da máxima.",
    "vida_atual": "Em branco, a vida está cheia. Curar não funciona a zero: use o retorno ou o descanso longo.",
    "reserva": "Só a maldição domada com técnica própria: nível × (1 + um terço da Essência dela). Escreva quanto ainda resta. O "
               "descanso curto recupera um quarto.",
    "equip": "Registre o que ela veste e empunha, a proteção e os requisitos. Arma empunhada: ataque pelo atributo da arma, com "
             "desvantagem, e o dano da arma.",
    "corpo": "Tamanho, membros, sentidos, como entende ordens e como avisa o que achou. O que ela não tem aqui, ela não faz.",
    "familias": "Três Famílias abertas, uma delas Livre. As Trilhas do Evocador abrem mais uma (Parceria e Múltiplas Invocações) ou "
                "duas, com uma segunda Livre (a principal da Invocação Principal). As outras ficam Fechadas e somem dos menus.",
    "definicao": "Uma ou duas frases: o que ela é e o que faz na equipe. Tudo o que a ficha concede precisa caber aqui.",
    "talentos": "Um talento no nível 1 e outro nos níveis 6, 10, 14, 18, 22, 26 e 30. Os do nível 1 e 6 vão até a Categoria de "
                "Efeito 1, o do 10 até a 2, e os outros até a 3.",
    "nome_carta": "Dê um nome à habilidade: a ficha só calcula a carta de quem tem nome.",
    "classe_carta": "A Classe da especial. Ela define os pontos, o PE (3 × Classe) e quantas Melhorias cabem. A básica é sempre "
                    "Classe 0 e não custa PE.",
    "tdano": "Cada ataque tem o seu tipo de dano. A aparência de energia pura usa Força.",
    "rmenu": "Trocar ataque por Teste de Resistência, ou o contrário, não custa pontos. Em branco, vale o que a Forma traz.",
    "melhorias": "As Classes 1 e 2 aceitam 2 Melhorias, a 3 e a 4 aceitam 3, e da 5 em diante 4. A Forma não conta. O menu só traz "
                 "as Famílias abertas, e a da Família Livre sai mais barata. A básica aceita uma Melhoria Leve, que custa um dado.",
    "restricoes": "Até duas, contando o Corpo a Corpo que Toque e Aura já trazem. Restrição paga peças: o que passar do que foi gasto "
                  "some. Na básica cabe uma Restrição Leve, que não devolve nada.",
    "ampliar": "A mesma especial usada numa Classe maior, até a maior que o nível dela liberou. A conta inteira é refeita.",
    "trilha": "Só o Evocador: as escolhas a mais da Invocação Principal (níveis 8, 16 e 24 da invocação) e do Repertório do Conjunto "
              "(nível 27). Cada escolha é uma básica (Classe 0), uma especial ou um talento de Categoria 1.",
    "trunfos": "O livro dá os três só à maldição domada com técnica própria. A ficha não confere isso.",
    "lib": "A domada conhece uma no nível 10, duas no 20 e três no 30. Classe 3 ou maior, e não ocupa espaço de especial. "
           "Custa 3 × Classe × 1,5 PE, para cima.",
    "tm": "A faixa usa o nível dela, que não sobe com o seu. Os pontos pagam Forma e Melhorias, sem comprar dados.",
    "exp": "O refino, a maestria e a especialização são os seus. Posição, vida e Teste de Resistência de Vigor são os dela.",
    "c_usa": "Escolhido ao obter a primeira entidade. Vale para a Defesa de todas e para o limite de corpos mantidos.",
    "c_ativas": "Quantas entidades podem estar ativas ao mesmo tempo. O limite geral é de duas; a Trilha Múltiplas Invocações "
                "leva a quatro durante o combate.",
    "c_corpos": "Quantos corpos amaldiçoados você mantém, ativos e inativos: o atributo da Defesa mais as entidades ativas.",
    "c_rol": "Todas as fichas da aba, com o nível e a vida de cada uma. Clique numa linha e siga a ligação para ir até a ficha.",
}


class _Folha(fa._Folha):
    def estilo(self, nome):
        if nome not in self._e:
            novo = json.loads(json.dumps(ESTILOS[nome]))
            chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
            for i, e in enumerate(self.layout["estilos"]):
                if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
                    self._e[nome] = i
                    break
            else:
                self.layout["estilos"].append(novo)
                self._e[nome] = len(self.layout["estilos"]) - 1
        return self._e[nome]


def _carta(f, tr, r0, c0, i, n_ficha, tipo, com_nota):
    """a carta de uma habilidade: o título, a descrição (que fecha), os números de mesa e a montagem (que fecha)"""
    D, M = tr["D"], tr["menus"][n_ficha]
    a, b, c, d, e = (c0 + k for k in range(5))
    v = lambda k: f"={tr['CARTA'](k, i)}"
    nota = (lambda k: NOTAS[k]) if com_nota else (lambda k: None)
    cel = celulas_da_carta(r0, c0)
    assert f.add("rot", a, r0 + F_TIT, e, r0 + F_TIT, v("titulo")) == cel["titulo"]
    assert f.add("classe_carta", a, r0 + F_NOME, a, r0 + F_NOME, 0 if tipo == "bas" else 1, nota("classe_carta")) == cel["classe"]
    assert f.add("nome", b, r0 + F_NOME, d, r0 + F_NOME, None, nota("nome_carta")) == cel["nome"]
    assert f.add("estado", e, r0 + F_NOME, e, r0 + F_NOME, v("estado")) == cel["estado"]
    f.add("rot", a, r0 + F_ROT, e, r0 + F_ROT, "COMO É")
    assert f.add("txt", a, r0 + F_TXT, e, r0 + F_TXT_FIM) == cel["como"]
    assert f.add("cel", a, r0 + F_N1, b, r0 + F_N1, FORMA_INICIAL) == cel["forma"]
    assert f.add("dano", c, r0 + F_N1, d, r0 + F_N1, v("dano")) == cel["dano"]
    assert f.add("dano", e, r0 + F_N1, e, r0 + F_N1, v("pe")) == cel["pe"]
    assert f.add("cel", a, r0 + F_N2, b, r0 + F_N2, None, nota("tdano")) == cel["tdano"]
    assert f.add("cel", c, r0 + F_N2, e, r0 + F_N2, None, nota("rmenu")) == cel["rmenu"]
    assert f.add("cel", a, r0 + F_N3, b, r0 + F_N3, v("acao")) == cel["acao"]
    assert f.add("cel", c, r0 + F_N3, e, r0 + F_N3, v("resolve")) == cel["resolve"]
    assert f.add("peq", a, r0 + F_ALC, e, r0 + F_ALC, v("alcance")) == cel["alcance"]
    f.add("rot", a, r0 + F_MEL, a, r0 + F_MEL + N_MEL - 1, "MELHORIAS", nota("melhorias"))
    for k in range(N_MEL):
        assert f.add("cel_esq", b, r0 + F_MEL + k, d, r0 + F_MEL + k) == cel["mel"][k]
        f.add("peq", e, r0 + F_MEL + k, e, r0 + F_MEL + k, v(f"pt{k + 1}"))
    f.add("rot", a, r0 + F_RES, a, r0 + F_RES + N_RES - 1, "RESTRIÇÕES", nota("restricoes"))
    for k in range(N_RES):
        assert f.add("cel_esq", b, r0 + F_RES + k, d, r0 + F_RES + k) == cel["res"][k]
        f.add("peq", e, r0 + F_RES + k, e, r0 + F_RES + k, v(f"dt{k + 1}"))
    f.add("rot", a, r0 + F_CONTA, a, r0 + F_CONTA, "CONTA")
    assert f.add("conta", b, r0 + F_CONTA, e, r0 + F_CONTA, v("conta")) == cel["conta"]
    f.add("rot", a, r0 + F_AMP, a, r0 + F_AMP + 1, "AMPLIAR", nota("ampliar"))
    assert f.add("conta", b, r0 + F_AMP, e, r0 + F_AMP + 1, v("ampliar")) == cel["ampliar"]
    assert f.add("conta", a, r0 + F_AV, e, r0 + ALT - 1, v("linha")) == cel["avisos"]
    if tipo != "bas":
        f.menu(cel["classe"], D.faixa("classe0" if tipo == "ext" else "classe", so=0, aba=DI))
    f.menu(cel["forma"], M["forma0"] if tipo == "bas" else M["forma"])
    f.menu(cel["tdano"], D.faixa("danos", aba=DI))
    f.menu(cel["rmenu"], D.faixa("resolve", aba=DI))
    f.menu(f"{cel['mel'][0]}:{cel['mel'][-1]}", M["leve"] if tipo == "bas" else M["mel"])
    f.menu(f"{cel['res'][0]}:{cel['res'][-1]}", D.faixa("res", so=4 if tipo == "bas" else 0, aba=DI))


def aba(layout, tr):
    """a aba inteira, pronta para entrar em layout['abas']. Lê o cabeçalho e a lombada da FICHA do `layout`, que por
    isso tem de vir depois das correções de borda."""
    import cabecalho as cab
    R, H, D, FI, CJ = tr["R"], tr["H"], tr["D"], tr["FI"], tr["CJ"]
    LIV = R["LIV"]
    ficha = ix._aba(layout, "FICHA")
    fcel = {r[0]: r for r in ficha["celulas"]}
    f = _Folha(layout)
    B1 = blocos(0)                                   # os blocos da primeira coluna de fichas: o cabeçalho se alinha neles

    # --- o cabeçalho (linhas 1 a 7) e a lombada (colunas A e B), no molde da FICHA, como na FICHA AMALDIÇOADA
    vazio = cab._estilo(layout, "vazio")
    for lin in range(1, 8):
        for col in range(1, COLS + 1):
            fonte = "A" if col == 1 else "B" if col == 2 else "C" if col == 3 else "AU" if col == COLS else "AD"
            molde = fcel.get(f"{fonte}{lin}")
            if lin > cab.ULTIMA_LINHA and col > 2:
                continue
            if lin <= cab.ULTIMA_LINHA - 1 and col > 3:
                estilo = vazio
            elif molde is None:
                continue
            else:
                estilo = molde[2]
            f.cel[_a1(col, lin)] = (None, estilo)
            f.dentro.add((lin, col))

    def no_cabecalho(estilo, c1, l1, c2, l2, valor):
        for l in range(l1, l2 + 1):
            for c in range(c1, c2 + 1):
                f.dentro.discard((l, c))
                f.cel.pop(_a1(c, l), None)
        f.add(cab._estilo(layout, estilo), c1, l1, c2, l2, valor)
    no_cabecalho("marca", C_CONJ, 2, C_CONJ, 4, cab.MARCA)
    no_cabecalho("titulo", C_CONJ + 1, 2, B1[0] + N_BLOCO - 1, 3, NOME)
    no_cabecalho("apoio", C_CONJ + 1, 4, B1[0] + N_BLOCO - 1, 4, f'=DADOS!$F$1&" · {APOIO}"')
    no_cabecalho("nome", B1[1], 2, B1[2] + N_BLOCO - 1, 3, f"=FICHA!{cab.C_NOME[0]}")
    no_cabecalho("quem", B1[1], 4, B1[2] + N_BLOCO - 1, 4, f"=FICHA!{cab.C_QUEM[0]}")
    pincel = [dict(im) for im in ficha["imagens"] if im["lin"] <= 7]
    if len(pincel) != 1:
        raise SystemExit(f"a FICHA devia ter uma imagem no cabecalho, e tem {len(pincel)}")
    ult = COLS - 2
    pincel[0]["larg"] = sum(PX_COLUNAS[pincel[0]["col"] - 1:ult])
    f.add("canvas", pincel[0]["col"], 6, ult, 6)
    alturas = [list(a) for a in ficha["linhas_alt"] if a[0] <= 7]
    lomb = {m.split(":")[0]: m for m in ficha["mescladas"] if ix._lc(m.split(":")[1])[1] <= 2}
    textos = {"FICHA DE REGISTRO": NOME}
    liso = [next(fcel[_a1(col, l)][2] for l in range(ficha["linhas"], 0, -1) if _a1(col, l) in fcel and fcel[_a1(col, l)][1] is None)
            for col in (1, 2)]
    for canto, m in lomb.items():
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
        if l2 > LIN:
            raise SystemExit(f"ficha_invocacoes: a lombada da FICHA ({m}) passa da última linha da aba ({LIN})")
        f.mesclas.append(m)
        f.cel[canto] = (textos.get(fcel[canto][1], fcel[canto][1]), fcel[canto][2])
        for l in range(l1, l2 + 1):
            for c in range(c1, c2 + 1):
                f.dentro.add((l, c))
    for lin in range(8, LIN + 1):
        for col in (1, 2):
            if (lin, col) not in f.dentro:
                f.cel[_a1(col, lin)] = (None, liso[col - 1])
                f.dentro.add((lin, col))

    def caixa(c1, c2, lin, rotulo, valor=None, estilo="val", nota=None, alt=2):
        """o rótulo numa linha e o valor nas de baixo"""
        f.add("rot", c1, lin, c2, lin, rotulo, nota)
        return f.add(estilo, c1, lin + 1, c2, lin + alt, valor)

    # --- o conjunto: três colunas, à esquerda, nas linhas da primeira fileira de fichas
    d, e, g_ = C_CONJ, C_CONJ + 1, C_CONJ + 2
    r = L0
    f.add("faixa", d, r, g_, r + 1, "O CONJUNTO")
    assert caixa(d, d, r + 3, "SEU NÍVEL", f"={H['nível']}", "num", "Vem da FICHA.") == CJ["nivel"]
    assert caixa(e, e, r + 3, "MAESTRIA", f"={sinal(H['maestria'])}", "num", NOTAS["maestria"]) == CJ["maestria"]
    assert caixa(g_, g_, r + 3, "TRILHA", f'=IF(OR({H["trilha"]}="",LEFT({H["trilha"]},7)="Escolha"),"—",{H["trilha"]})', "cel",
                 "Vem da FICHA. Só as Trilhas do Evocador mudam esta aba.") == CJ["trilha"]
    assert caixa(d, d, r + 7, "DEFESA USA", "Essência", "cel", NOTAS["c_usa"]) == CJ["usa"]
    f.menu(CJ["usa"], D.faixa("usa", aba=DI))
    assert caixa(e, e, r + 7, "ATIVAS, NO MÁXIMO", f"={H['teto de ativas']}", "num", NOTAS["c_ativas"]) == CJ["ativas"]
    assert caixa(g_, g_, r + 7, "CORPOS MANTIDOS", f"={H['corpos mantidos']}", "num", NOTAS["c_corpos"]) == CJ["corpos"]
    # 07/10/2026: saíram do conjunto a REAÇÃO COLETIVA, o DANO NO TURNO, os Pontos de Vínculo, o Aprimoramento de Vínculo
    # com a beneficiária e os três usos da rodada; e de cada ficha o MOVIMENTO que resta, a BÁSICA DO CICLO, o ESTADO e a
    # ORDEM PENDENTE. O retorno que o Mizuki trouxe: "n tem necessidade dessas caixas q basicamente vc muda durante o
    # turno ... vida, modificadores, energia e essas coisas tudo bem", e, da faixa do Vínculo, "pra q esse tbm". Com o
    # estado fora, o conjunto mostra o limite de ativas, e não mais a contagem. O deslocamento, com o Buff/Debuff
    # embaixo, já está nos números da ficha.
    assert f.add("rot", d, r + 11, g_, r + 11, f'="AS INVOCAÇÕES · "&{H["fichas com nome"]}&" DE {N_ROL}"', NOTAS["c_rol"]) == CJ["rol_rot"]
    for i in range(N_ROL):
        assert f.add("rol", d, r + 12 + i, g_, r + 12 + i, f"={FI('d_rol', i)}") == CJ["rol"][i]
    if r + 12 + N_ROL - 1 >= L0 + O["hab"]:
        raise SystemExit("ficha_invocacoes: a lista do conjunto desce até as habilidades da primeira fileira, que fecham em grupo")

    # --- as fichas
    for i, ((num, j, k), g) in enumerate(zip(tr["LUG"], tr["fichas_c"])):
        r, sp = g["r"], lombada(k)
        a, b, c = g["blocos"]
        A1, A5, B5, C5 = a[0], a[4], b[4], c[4]
        v = lambda nome: f"={FI(nome, i)}"
        nota = (lambda nome: NOTAS[nome]) if i == 0 else (lambda nome: None)
        # a lombada da ficha: o número e o nome em pé, que ficam à vista com a coluna de fichas fechada... e a faixa do nome
        assert f.add("lomb_num", sp, r, sp, r + 1, num) == g["lombada_num"]
        assert f.add("lombada", sp, r + 2, sp, r + O["fim"], v("d_lomb")) == g["lombada"]
        assert f.add("numero", A1, r, A1, r + 1, num) == g["numero"]
        assert f.add("faixa", a[1], r, C5, r + 1, v("d_titulo")) == g["titulo"]
        # --- à esquerda: quem ela é
        assert caixa(A1, A5, r + 3, "NOME", None, "val", nota("nome")) == g["nome"]
        assert f.add("foto", A1, r + 6, A5, r + 24, TEXTO_FOTO, nota("foto")) == g["foto"]
        assert caixa(A1, A5, r + 26, "TIPO", LIV["tipos"][0]["nome"], "cel", nota("tipo")) == g["tipo"]
        f.menu(g["tipo"], D.faixa("tipos", aba=DI))
        assert caixa(A1, a[1], r + 30, "AQUISIÇÃO", LIV["aquisicoes"][0]["nome"], "cel", nota("aquis")) == g["aquis"]
        f.menu(g["aquis"], D.faixa("aquis", so=0, aba=DI))
        assert caixa(a[2], a[2], r + 30, "OBTIDA NO NÍVEL", None, "cel", nota("nivel_fixo")) == g["nivel_fixo"]
        assert caixa(a[3], A5, r + 30, "TALISMÃ", SEM_CARGA, "cel", nota("talisma")) == g["talisma"]
        f.menu(g["talisma"], D.faixa("carga", aba=DI))
        assert f.add("rot", A1, r + 34, A5, r + 34, v("d_fam"), nota("familias")) == g["fam_rot"]
        for n, rot in enumerate(("LIVRE", "LIVRE · TRILHA", "ABERTA", "ABERTA", "ABERTA · TRILHA")):
            f.add("rot", a[n], r + 35, a[n], r + 35, rot)
            assert f.add("cel", a[n], r + 36, a[n], r + 37) == g["fam"][n]
        f.menu(f"{g['fam'][0]}:{_a1(a[N_FAM - 1], r + 36)}", D.faixa("familias", aba=DI))
        # --- no meio: os números
        for n, (rot, val, est, nt) in enumerate((("NÍVEL", v("n"), "num", "nivel"), ("CLASSE", v("cl"), "num", "classe"),
                                                 ("MAESTRIA", v("d_mae"), "num", "maestria"), ("ENTRADA", v("d_ent"), "num", "entrada"),
                                                 ("RETORNO", v("d_ret"), "num", "retorno"))):
            assert caixa(b[n], b[n], r + 3, rot, val, est, nota(nt)) == g["status"][n]
        assert f.add("rot", b[0], r + 7, B5, r + 7, v("d_pontos"), nota("pontos")) == g["pontos_rot"]
        for n, (nome_atr, sigla) in enumerate(ATRS):
            f.add("rot", b[n], r + 8, b[n], r + 8, sigla, nota("atributo") if n == 0 else None)
            assert f.add("num", b[n], r + 9, b[n], r + 10, v(f"t{n}")) == g["total"][n]
            assert f.add("pontos", b[n], r + 11, b[n], r + 11, 0) == g["pts"][n]
            assert f.add("bd", b[n], r + 12, b[n], r + 12, 0, nota("bd") if n == 0 else None) == g["buff"][n]
        f.menu(f"{g['pts'][0]}:{g['pts'][-1]}", D.faixa("pontos", aba=DI))
        for n, (rot, campo, nt) in enumerate((("ATAQUE", "d_atq", "ataque"), ("CD", "d_cd", "cd"), ("DEFESA", "def", "defesa"),
                                              ("VIDA MÁXIMA", "vida", "vida"), ("DESLOCAMENTO", "d_desl", "desl"))):
            assert caixa(b[n], b[n], r + 14, rot, v(campo), "num", nota(nt)) == g["stat"][n]
            assert f.add("bd", b[n], r + 17, b[n], r + 17, 0) == g["bstat"][n]
        for n, (nome_tr, _) in enumerate(TESTES):
            assert caixa(b[n], b[n], r + 19, nome_tr.upper(), v(f"d_tr{n}"), "num", nota("tr") if n == 0 else None) == g["tr"][n]
            assert f.add("bd", b[n], r + 22, b[n], r + 22, 0) == g["btr"][n]
        assert caixa(B5, B5, r + 19, "CARGA MÁXIMA", v("carga"), "num", nota("carga")) == g["carga"]
        assert caixa(b[0], b[1], r + 24, "ATRIBUTO DE ACERTO", None, "cel", nota("acerto")) == g["acerto"]
        f.menu(g["acerto"], D.faixa("atributos", aba=DI))
        assert caixa(b[2], b[3], r + 24, "FÍSICO USA", "Força", "cel") == g["fis"]
        f.menu(g["fis"], D.faixa("fisico", aba=DI))
        assert caixa(B5, B5, r + 24, "TR TREINADO", None, "cel") == g["trT"]
        f.menu(g["trT"], D.faixa("testes", aba=DI))
        assert f.add("rot", b[0], r + 28, B5, r + 28, v("d_per"), nota("pericias")) == g["per_rot"]
        for n in range(N_PER):
            assert f.add("cel_esq", b[0], r + 29 + n, b[2], r + 29 + n) == g["per"][n]
            assert f.add("cel", b[3], r + 29 + n, B5, r + 29 + n, v(f"d_pb{n}")) == g["perb"][n]
        f.menu(f"{g['per'][0]}:{g['per'][-1]}", D.faixa("pericias", so=0, aba=DI))
        # --- à direita: a mesa. 07/10/2026, o retorno que o Mizuki trouxe de quem leu a aba: saiu a TAREFA ("pq o player
        # iria escrever algo q ele fala pro mestre na mesa assim?") e saiu o que muda de turno em turno ("n tem
        # necessidade dessas caixas q basicamente vc muda durante o turno"; "Básica do ciclo n faz sentido ter, estado,
        # ordem, n faz sentido"). A vida fica como na FICHA do jogador: "ideal o vida máxima ficar lado a lado com vida
        # atual, vida temporaria e ter um redutor automatico, semelhante a ficha de player". A caixa de ± é do onEdit
        # (redutorDaInvocacao_, no Codigo.gs), que lê os endereços de `redutores`, no ABAS.
        assert caixa(c[0], c[0], r + 3, "VIDA ATUAL", None, "digita", nota("vida_atual")) == g["vida"]
        assert caixa(c[1], c[1], r + 3, "VIDA MÁXIMA", f"={FI('vida', i)}", "num", nota("vida")) == g["vida_max"]
        assert caixa(c[2], c[2], r + 3, "TEMPORÁRIA", None, "digita") == g["temp"]
        assert caixa(c[3], c[3], r + 3, "± PERDA / GANHO", None, "digita", nota("delta")) == g["delta"]
        assert f.add("rot", C5, r + 3, C5, r + 3, v("d_res"), nota("reserva")) == g["reserva_rot"]
        assert f.add("digita", C5, r + 4, C5, r + 5) == g["reserva"]
        assert f.add("barra", c[0], r + 6, C5, r + 6,
                     f'=IFERROR(SPARKLINE({FI("atual", i)},{{"charttype","bar";"max",MAX(1,{FI("vida", i)});"color1",{H["cor da barra"]}}}),"")') == g["barra"]
        assert caixa(c[0], C5, r + 8, "CONDIÇÕES E USOS GASTOS", None, "txt", None, alt=7) == g["cond"]
        assert caixa(c[0], C5, r + 17, "ANOTAÇÕES", None, "txt", None, alt=9) == g["notas"]
        assert f.add("rot", c[0], r + 28, C5, r + 28, v("d_equip"), nota("equip")) == g["equip_rot"]
        assert f.add("txt", c[0], r + 29, C5, r + 31) == g["equip"]
        assert caixa(c[0], C5, r + 33, "CORPO, SENTIDOS E COMUNICAÇÃO", None, "txt", nota("corpo")) == g["corpo"]
        # --- embaixo: a definição, e as habilidades
        assert caixa(A1, C5, r + 39, "DEFINIÇÃO", None, "txt", nota("definicao")) == g["def"]
        assert f.add("lote", A1, r + O["hab"], C5, r + O["hab"], v("d_hab")) == g["hab"]
        com_nota = i == 0
        for n_c, carta in enumerate(tr["cartas"]):
            if carta[0] != i:
                continue
            _, tipo, n, _, _, _ = carta
            r0, c0 = g["cartas"][(tipo, n)]
            _carta(f, tr, r0, c0, n_c, i, tipo, com_nota and (tipo, n) in (("bas", 0), ("ext", 0)))
        assert f.add("rot", A1, r + O["tal"], C5, r + O["tal"], v("d_tal"), nota("talentos")) == g["tal_rot"]
        for n in range(N_TAL):
            lin = r + O["tal"] + 1 + n
            # 07/10/2026: o rótulo é sempre o nível e a Categoria. Antes, o talento que o nível ainda não abriu mostrava
            # "ABRE NO 6" no lugar; o retorno que o Mizuki trouxe: "tira esse abre no e coloca só o nível, que nem o
            # primeiro, fica mais bonitinho". Quem escolher um talento antes da hora continua vendo o aviso ao lado.
            assert f.add("rot", A1, lin, A1, lin, f"NV {R['abre_tal'][n]} · CE {R['teto_tal'][n]}") == g["tal_nv"][n]
            assert f.add("cel_esq", a[1], lin, a[3], lin) == g["tal"][n]
            assert f.add("peq_esq", A5, lin, C5, lin, v(f"d_tt{n}")) == g["tal_txt"][n]
        f.menu(f"{g['tal'][0]}:{g['tal'][-1]}", D.faixa("talentos", so=0, aba=DI))
        f.add("lote", A1, r + O["mais"], C5, r + O["mais"], "MAIS HABILIDADES · a segunda básica no nível 11, e as especiais 3 a 8, do nível 8 ao 28")
        f.add("lote", A1, r + O["trilha"], C5, r + O["trilha"],
              "REPERTÓRIO DA TRILHA · só o Evocador: as escolhas a mais da Invocação Principal e do Repertório do Conjunto", nota("trilha"))
        f.add("rot", A1, r + O["talx"], C5, r + O["talx"], "TALENTOS DA TRILHA · CATEGORIA 1")
        for n in range(N_TALX):
            lin = r + O["talx"] + 1 + n
            f.add("rot", A1, lin, A1, lin, "TRILHA · CE 1")
            assert f.add("cel_esq", a[1], lin, a[3], lin) == g["talx"][n]
            assert f.add("peq_esq", A5, lin, C5, lin, v(f"d_xt{n}")) == g["talx_txt"][n]
        f.menu(f"{g['talx'][0]}:{g['talx'][-1]}", D.faixa("talentos", so=3, aba=DI))
        f.add("lote", A1, r + O["trunfos"], C5, r + O["trunfos"],
              "TRUNFOS · Liberação Máxima, Técnica Máxima e Expansão de Domínio, para quem tem técnica própria", nota("trunfos"))
        for n, lb in enumerate(g["lib"]):
            r0, c0 = lb["r0"], lb["c0"]
            f.add("rot", c0, r0, c0 + 4, r0, f"LIBERAÇÃO MÁXIMA {n + 1}", NOTAS["lib"] if i == 0 and n == 0 else None)
            assert f.add("classe_carta", c0, r0 + 1, c0, r0 + 1, 3) == lb["classe"]
            f.menu(lb["classe"], D.faixa("classe_lib", aba=DI))
            assert f.add("nome", c0 + 1, r0 + 1, c0 + 3, r0 + 1) == lb["nome"]
            assert f.add("estado", c0 + 4, r0 + 1, c0 + 4, r0 + 1, v(f"d_lp{n}")) == lb["pe"]
            assert f.add("txt", c0, r0 + 2, c0 + 4, r0 + 5) == lb["como"]
            assert f.add("dano", c0, r0 + 6, c0 + 4, r0 + 6, v(f"d_ld{n}")) == lb["pontos"]
            assert f.add("cel", c0, r0 + 7, c0 + 4, r0 + 7, "Sua Ação Completa + a básica dela") == lb["acao"]
        tm, ex = g["tm"], g["exp"]
        r0, c0 = tm["r0"], tm["c0"]
        f.add("rot", c0, r0, c0 + 4, r0, "TÉCNICA MÁXIMA", nota("tm"))
        assert f.add("nome", c0, r0 + 1, c0 + 3, r0 + 1) == tm["nome"]
        assert f.add("estado", c0 + 4, r0 + 1, c0 + 4, r0 + 1, v("d_mp")) == tm["pe"]
        assert f.add("txt", c0, r0 + 2, c0 + 4, r0 + 5) == tm["como"]
        assert f.add("dano", c0, r0 + 6, c0 + 4, r0 + 6, v("d_md")) == tm["dados"]
        assert f.add("cel", c0, r0 + 7, c0 + 4, r0 + 7, "Sua Ação Completa + a básica dela") == tm["acao"]
        c0 = ex["c0"]
        f.add("rot", c0, r0, c0 + 4, r0, "EXPANSÃO DE DOMÍNIO", nota("exp"))
        assert f.add("nome", c0, r0 + 1, c0 + 3, r0 + 1) == ex["nome"]
        assert f.add("estado", c0 + 4, r0 + 1, c0 + 4, r0 + 1, v("d_ep")) == ex["pe"]
        assert f.add("txt", c0, r0 + 2, c0 + 4, r0 + 5) == ex["como"]
        assert f.add("cel", c0, r0 + 6, c0 + 1, r0 + 6) == ex["degrau"]
        f.menu(ex["degrau"], D.faixa("expansao", so=0, aba=DI))
        assert f.add("dano", c0 + 2, r0 + 6, c0 + 4, r0 + 6, v("d_ea")) == ex["acerto"]
        assert f.add("peq", c0, r0 + 7, c0 + 4, r0 + 7, v("d_er")) == ex["pede"]

    # --- a conta de cada caixa calculada mora na DADOS_INVOC, e a caixa só aponta para ela, como na FICHA AMALDIÇOADA: é o
    # que deixa o onEdit devolver a conta a quem escrever por cima. A barra fica de fora (o desenho dela não se aponta).
    com_conta = [(coord, v) for coord, (v, _) in f.cel.items()
                 if isinstance(v, str) and v.startswith("=") and not fa.REFERENCIA_PURA.fullmatch(v) and "SPARKLINE" not in v
                 and ix._lc(coord)[0] >= L0]
    c_mostra = D.tabela("mostra", ["caixa calculada", "o que a caixa mostra"], [[coord, v] for coord, v in com_conta])
    for i, (coord, _) in enumerate(com_conta):
        f.cel[coord] = (f"={_abs(c_mostra + 1, 2 + i, DI)}", f.cel[coord][1])
    tr["aba_dados"].update({"linhas": D.linhas, "colunas": D.prox - 2, "celulas": [[k, v[0], v[1]] for k, v in D.cel.items()]})

    canvas = f.estilo("canvas")
    for lin in range(1, LIN + 1):
        for col in range(1, COLS + 1):
            if (lin, col) not in f.dentro:
                f.cel[_a1(col, lin)] = (None, canvas)

    # --- os grupos de linhas. As fichas da mesma fileira dividem as linhas, e os grupos são da fileira. A primeira
    # fileira divide as linhas com o conjunto, e por isso o grupo dela fecha só das habilidades para baixo.
    grupos = []
    for j in range(N_FILEIRAS):
        r = linha_da_fileira(j)
        grupos.append([r + O["hab"] + 1, r + O["fim"], False] if j == 0 else [r + 2, r + O["fim"], True])
        fileiras = [r + O["h"]] + [r + O["m"] + (ALT + 1) * n for n in range(3)] + [r + O["x"]]
        for n, r0 in enumerate(fileiras):
            grupos += [[r0 + F_ROT, r0 + F_TXT_FIM, not (j == 0 and n == 0)], [r0 + F_MEL, r0 + ALT - 1, True]]
        grupos.append([r + O["mais"] + 1, r + O["m"] + (ALT + 1) * 2 + ALT - 1, True])
        grupos.append([r + O["trilha"] + 1, r + O["talx"] + N_TALX, True])
        grupos.append([r + O["trunfos"] + 1, r + O["fim"], True])
    for a_ in grupos:
        for b_ in grupos:
            if a_ is not b_ and b_[0] == a_[1] + 1:
                raise SystemExit(f"ficha_invocacoes: os grupos {a_[:2]} e {b_[:2]} estao colados")
    # --- os grupos de colunas: o conjunto, e cada coluna de fichas (a lombada do nome fica de fora, à vista)
    grupos_col = [[C_CONJ, C_CONJ + N_CONJ, False]] + [[lombada(k) + 1, lombada(k) + PASSO_COL - 1, k > 0] for k in range(N_COLUNAS)]

    # --- as fileiras de cartas que são cópia da primeira: o script mescla a primeira e copia o formato para as outras.
    # A cópia vai coluna de fichas por coluna de fichas (`faixas`), porque a lombada de cada uma atravessa as fileiras
    # de cartas, e o Sheets não copia meia mesclagem.
    faixas = [[lombada(k) + 1, lombada(k) + PASSO_COL - 2] for k in range(N_COLUNAS)]
    das_cartas = (O["h"], O["m"], O["m"] + ALT + 1, O["x"])
    cheias = [linha_da_fileira(j) + x for j in range(N_FILEIRAS) for x in das_cartas]
    copia = [[cheias[0], cheias[0] + ALT - 1, cheias[1:], faixas[0][0], faixas[-1][1], faixas]]
    # --- e o resto de cada fileira de fichas (07/10/2026, a grade de 2 × 6): o que fica entre as fileiras de cartas é
    # igual da segunda fileira em diante, e a segunda é o molde das outras. A primeira não serve de molde, porque divide
    # as linhas com o conjunto. Só os números de cada ficha (a fórmula que aponta para a linha dela na DADOS_INVOC, o
    # menu das Famílias dela) vêm escritos em cada cópia.
    if N_FILEIRAS > 2:
        cortes = [-1] + [x for c in das_cartas for x in (c, c + ALT - 1)] + [O["fim"] + 1]
        trechos = [(cortes[i] + 1, cortes[i + 1] - 1) for i in range(0, len(cortes), 2)]
        for a_, b_ in trechos:
            if b_ - a_ >= 1:
                copia.append([linha_da_fileira(1) + a_, linha_da_fileira(1) + b_, [linha_da_fileira(j) + a_ for j in range(2, N_FILEIRAS)],
                              faixas[0][0], faixas[-1][1], faixas])

    corpo = f"{L(C_CONJ)}{L0}:{L(COLS)}{LIN}"
    condicional = [{"faixas": [corpo], "contem": T_ERRO, "fundo": VERMELHO, "fonte": BRANCO},
                   {"faixas": [corpo], "comeca": T_AVISO, "fonte": AMBAR},
                   {"faixas": [corpo], "contem": SEM_NOME, "fonte": AMBAR}]
    base = ficha["colunas_larg"][0][2]
    return {
        "nome": NOME, "estado": "visible", "linhas": LIN, "colunas": COLS,
        "colunas_larg": [[i + 1, i + 1, base if px == PX_FINA else (px + 1) / 8] for i, px in enumerate(PX_COLUNAS)],
        "linhas_alt": alturas, "altura_padrao": ficha.get("altura_padrao"), "grade": False,
        "celulas": [[k, v[0], v[1]] for k, v in f.cel.items()],
        "mescladas": f.mesclas,
        "menus": [{"onde": " ".join(onde), "tipo": "list", "formula": formula, "vazio_ok": True, "mostra_seta": True}
                  for formula, onde in f.menus.items()],
        "condicional": [], "imagens": pincel, "notas": f.notas,
        "grupos": {"linhas": grupos, "colunas": grupos_col},
        "condicional_gs": condicional,
        "protegidas": [],
        "copias": copia,
        "validacao_em_matriz": True,
        # a caixa de ± de cada ficha, com a vida atual, a temporária e a máxima dela: o onEdit aplica e limpa
        "redutores": [[g["delta"], g["vida"], g["temp"], g["vida_max"]] for g in tr["fichas_c"]],
    }


def aplica(layout, tr):
    """põe a INVOCAÇÕES depois da FICHA AMALDIÇOADA e a DADOS_INVOC depois da DADOS_AM. Devolve a aba."""
    folha = aba(layout, tr)
    layout["abas"].insert(next(i for i, a in enumerate(layout["abas"]) if a["nome"] == fa.NOME) + 1, folha)
    layout["abas"].insert(next(i for i, a in enumerate(layout["abas"]) if a["nome"] == fa.DADOS_AM) + 1, tr["aba_dados"])
    return folha
