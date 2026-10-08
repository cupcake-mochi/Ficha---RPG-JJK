# -*- coding: utf-8 -*-
"""A aba FICHA PESSOAL: o dossiê do personagem, o que ele empunha e veste, o treino em armas, a carga,
o dinheiro, os pertences guardados e o painel de missões e XP. É a limpeza 22.

Não existe planilha viva desta aba. O desenho foi fechado com o Mizuki por estudo, em 30/09 e 01/10/2026
(o estudo está em mockup/ficha-pessoal-estudo.html), e a aba nasce inteira aqui, como o GLOSSÁRIO.

O que ela muda fora dela:
  · o EQUIPAMENTO da FICHA deixa de ser menu e passa a espelhar o que está vestido e o escudo da mão
    secundária. Ele monta o mesmo nome que a tabela de equipamento da DADOS usa ("Traje 1 + Broquel"),
    e por isso a Defesa não muda de conta;
  · o XP da FICHA passa a mostrar a soma das missões do painel, e o nível continua subindo por ele;
  · o DESLOCAMENTO da FICHA cai pela metade com uma arma empunhada sem a Força, e vai a zero com a carga
    acima do limite (04/10/2026: as duas regras passaram a ser do livro, e mudaram);
  · a DEFESA da FICHA perde a proteção do uniforme ou do escudo usado sem a Força. A arma empunhada sem a Força
    não mexe mais na Defesa (07/10/2026, decisão do Mizuki que o livro ainda não traz: desvantagem nos ataques
    com ela e metade do deslocamento; está no `fora_do_livro` do arquivo de dados);
  · a DADOS ganha, depois do índice, as tabelas que os menus e as contas desta aba leem.

De onde sai cada número: as armas, os escudos, os uniformes, o salário e os tipos de missão saem das
chaves `equipamento`, `equipamento_defesa`, `patentes` e `missoes` do catálogo, que o conferir-catalogo.py
confere contra o manual.txt. O desconto da semana, a falha, o arredondamento do XP e as punições de Força e de
carga entraram no livro reconstruído, e saem das chaves dele; o que o Mizuki decidiu em 01/10/2026 e o livro ainda
não traz (missão solo e os multiplicadores da guilda) sai da chave `fora_do_livro`.

Os endereços desta aba são do gerador, e por isso estão escritos aqui. O Codigo.gs não guarda nenhum: ele
lê o índice que esta limpeza publica na DADOS, sob "campo pessoal" e "célula pessoal".
"""
import json, os, re, unicodedata

import indice_ficha as ix

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "FICHA PESSOAL"
TIPOS_DE_LEGADO = ("Narrativo", "De rolagem", "De exceção")
FP = f"'{NOME}'!"

# ---------------------------------------------------------------------------------------------
# A grade. As colunas têm a largura das da FICHA, e a folha vai de A a AU como ela. Depois da AU
# vem o painel de XP, num grupo de colunas que nasce fechado.
# ---------------------------------------------------------------------------------------------
C = ix._col
COLS_FOLHA = 47                      # A a AU
PAINEL_INI = COLS_FOLHA + 1          # AV, o respiro; o painel começa na AW
# O painel não segue a grade de 28 px da folha: cada coluna dele tem a largura do que guarda. Com a grade, cada
# célula de missão era uma mesclagem (480 delas), e a aba tinha 90 colunas para a troca de paleta varrer.
C_MISSAO, C_XP, C_ADIC, C_DESC, C_TOTAL = 0, 1, 2, 3, 4
PX_BLOCO = [196, 112, 84, 112, 56]   # Missão, XP, Adicional, Desconto e Total, em pixel
B1 = PAINEL_INI + 1                  # o primeiro bloco
B2 = B1 + len(PX_BLOCO) + 1          # o segundo, com uma coluna de respiro no meio
# A extensão: mais dois blocos de missão, do mesmo tamanho, num grupo de colunas DENTRO do grupo do painel, que
# também nasce fechado. Pedido do Mizuki em 01/10/2026: "já vi mt player lotando essas tabelas".
EXT_INI = B2 + len(PX_BLOCO) + 1     # a coluna de respiro depois do segundo bloco fica de fora: é a margem do painel básico
B3 = EXT_INI
B4 = B3 + len(PX_BLOCO) + 1
PAINEL_FIM = B4 + len(PX_BLOCO)      # a margem da direita
BLOCOS = [B1, B2, B3, B4]
ULT = len(PX_BLOCO) - 1              # a última coluna de um bloco

# Toda linha da aba tem a mesma altura, e o título de seção ocupa DUAS linhas mescladas. A primeira versão dava 27 px
# à linha do título, e como a linha é da planilha inteira, duas linhas da lista de missões e uma da tabela de níveis
# saíam mais gordas que as vizinhas (achado do Mizuki em 01/10/2026: "dá certa agonia"). Em uma linha só o título
# ficava pequeno; com duas ele tem altura de título e nenhuma linha engorda.
FX = 2
EQUIP_MENU, EQUIP_LIVRE, ITENS_LINHAS = 6, 2, 6
L_DOSSIE = 8
DOSSIE_LINHAS = 35                   # 08/10/2026 (B41): eram 27; entraram o traço, as cicatrizes e os dois Legados
L_USO = L_DOSSIE + FX + DOSSIE_LINHAS + 1
L_TREINO = L_USO + FX + 5 + 1        # em uso: rótulo, valor em duas linhas, detalhe e marcas
L_FILEIRA = L_TREINO + FX + 13 + 1   # a lista de treino tem 13 linhas
L_EQUIP = L_FILEIRA + 3 + 1
L_ITENS = L_EQUIP + FX + 1 + EQUIP_MENU + EQUIP_LIVRE + 1
L_FIM = L_ITENS + FX + 1 + ITENS_LINHAS
L_MISSAO_CAB = L_DOSSIE + FX + 4     # o cabeçalho das missões; elas descem até duas linhas antes dos níveis
L_NIVEIS = L_EQUIP                   # o título dos níveis divide as linhas com o dos equipáveis

# o treino em armas: cinco colunas, com as categorias de cada uma na ordem do desenho
COLUNAS_TREINO = [(C("D"), 9, ["Lâmina Longa", "Machado"]),
                  (C("M"), 9, ["Arma de Fogo", "Arremesso"]),
                  (C("V"), 9, ["Porrete", "Ceifa", "Balestra"]),
                  (C("AE"), 8, ["Lâmina Curta", "Flexível", "Manopla"]),
                  (C("AM"), 8, ["Massa", "Armas Longas", "Yumi"])]

# as colunas da tabela de equipáveis: (rótulo, primeira, última)
COLS_EQUIP = [("Equipável", "D", "J"), ("Qtd.", "K", "L"), ("Categoria", "M", "R"), ("Mão", "S", "T"),
              ("Dado", "U", "V"), ("Propriedades", "W", "AD"), ("Força", "AE", "AF"), ("Vol.", "AG", "AH"),
              ("Grau", "AI", "AJ"), ("Estigma", "AK", "AP"), ("Desgaste", "AQ", "AT")]
COLS_ITENS = [[("Item", "D", "S"), ("Qtd.", "T", "U"), ("Vol.", "V", "X")],
              [("Item", "Z", "AO"), ("Qtd.", "AP", "AQ"), ("Vol.", "AR", "AT")]]

# ---------------------------------------------------------------------------------------------
# As cores e as fontes: as da FICHA, pelos papéis da paleta de fábrica. A troca de paleta acha o
# papel de cada célula pela cor que ela tem, então nenhuma cor nova pode entrar aqui.
# ---------------------------------------------------------------------------------------------
TINTA, FUNDO, PAINEL, ALTO, PAPEL = "FF0A0810", "FF120F1D", "FF1E1733", "FF3D2E78", "FF17131F"
# o ACENTO é o fundo da faixa de título de seção, como no GLOSSÁRIO e no CATÁLOGO. Até 01/10/2026 a faixa daqui usava
# o painel alto, o mesmo do rótulo, e num tema claro o título não se destacava das caixas (achado do Mizuki no Sheets).
ACENTO = "FF211940"
OSSO, TEXTO, FRACO, REGUA = "FFE8DCD4", "FFF4F1F7", "FF998BA9", "FF8A7EC4"
_CAIXA = {l: ["medium", REGUA] for l in ("top", "bottom", "left", "right")}
ESTILOS = {
    "canvas":   [None, FUNDO, None, None, None],
    "faixa":    [["Oswald", 14.0, OSSO, False, False], ACENTO, _CAIXA, ["left", "center", False, 0], None],
    "rot":      [["Oswald", 8.0, OSSO, False, False], ALTO, _CAIXA, ["center", "center", False, 0], None],
    "val":      [["Roboto", 11.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "num":      [["Oswald", 16.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "iene":     [["Oswald", 16.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], '"¥ "#,##0'],
    "cel":      [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "cel_esq":  [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
    "peq":      [["Roboto", 9.0, FRACO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "marca":    [["Oswald", 8.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "txt":      [["Roboto", 10.0, TEXTO, False, False], PAPEL, _CAIXA, ["left", "top", True, 0], None],
    "foto":     [["Oswald", 8.0, FRACO, False, False], PAPEL, _CAIXA, ["center", "center", True, 0], None],
    "barra":    [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
}

# os textos que a ficha escreve nas marcas, e que a cor de aviso procura
T_FALTA_FORCA = "Falta Força"
T_SEM_TREINO = "Sem treino"
T_NAO_CUMPRIDO = "Não cumprido"
T_PEDE_GRAU = "Pede "
T_ACIMA = " · acima"
SOCO, MAO_LIVRE, NAS_DUAS, SEM_UNIFORME = "Soco", "—", "Nas duas mãos", "Sem uniforme"
# o que a linha embaixo da mão diz quando nenhum equipável guardado serve a ela (B30: o menu nasce só com o Soco)
T_GUARDE_P = "para outra arma, guarde ela nos Equipáveis guardados"
T_GUARDE_S = "Mão livre · arma de uma mão ou escudo guardado aparece aqui"
# as propriedades que a nota da arma trata à parte: a primeira é a coluna mão do catálogo, e as outras ganham o número
# da arma em uso. O do Alcance é decisão do Mizuki de 01/10/2026 ("sim é A"): toda arma com a propriedade chega aos 3 m
# que o livro escreve para "as Armas Longas", e não só as três da categoria com esse nome. A frase do livro ele acerta
# depois; a ficha já segue a decisão.
DUAS_MAOS, LONGO_ALCANCE, MUNICAO, ALCANCE = "Duas mãos", "Longo Alcance", "Munição", "Alcance"
OUTRA_SITUACAO = "Outra Situação"
VERMELHO, BRANCO, AMBAR = "#C2334D", "#FFFFFF", "#D89B3A"
APOIO = "pertences e histórico do portador"      # a linha de apoio do cabeçalho, embaixo do título
COR_DA_BARRA = "cor da barra cheia"      # a conta da DADOS e o campo do índice: o Codigo.gs acha por este nome


def _ordem(s):
    """a ordem do menu: alfabética, sem o acento atrapalhar (o Bō depois do Bastão)"""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def _milhar(n):
    return f"{n:,}".replace(",", ".")


def _a1(col, lin):
    return f"{ix._letras(col)}{lin}"


def _abs(col, lin, aba=""):
    return f"{aba}${ix._letras(col)}${lin}"


def _faixa(c1, l1, c2, l2, aba=""):
    return f"{aba}${ix._letras(c1)}${l1}:${ix._letras(c2)}${l2}"


def _endereco(coord, aba):
    """o endereço em fórmula, que anda sozinho se alguém inserir linha (o mesmo molde do índice da FICHA)"""
    return f"=ADDRESS(ROW({aba}{coord}),COLUMN({aba}{coord}),4)"


def _endereco_faixa(c1, c2, aba):
    return (f"=ADDRESS(ROW({aba}{c1}),COLUMN({aba}{c1}),4)&\":\"&"
            f"ADDRESS(ROW({aba}{c2}),COLUMN({aba}{c2}),4)")


def tabela_da_defesa(dados, lin_cab):
    """a tabela de equipamento da Defesa (defesa_equipamento.py), que já traz cada escudo com a proteção dele. A proteção
    do escudo usado sem a Força sai dela, e não de uma tabela nova: o Codigo.gs acha o índice desta aba numa coluna fixa
    da DADOS (IDXP_COL_CAMPO), e uma tabela a mais antes dele empurraria o índice."""
    import defesa_equipamento as de
    cab = next(r[0] for r in dados["celulas"] if r[1] == de.CABECALHO[0] and ix._lc(r[0])[0] == lin_cab)
    c0 = ix._lc(cab)[1]
    fim = max(ix._lc(r[0])[0] for r in dados["celulas"] if ix._lc(r[0])[1] == c0 and r[1] not in (None, ""))
    return _faixa(c0, lin_cab + 1, c0 + 1, fim, "DADOS!")


def descontos(missoes):
    """o menu de desconto da missão: as posições da semana que pagam menos que cheio, da tabela do livro, e a falha
    que pagou metade. O livro aplica as duas juntas ("200 × ½ × ½ = 50 XP" na terceira longa que falhou), e o Mizuki
    decidiu em 04/10/2026 que o menu traz as duas opções: cada posição que paga menos ganha também a versão com falha,
    pela metade dela."""
    pos = []
    for p, pct in missoes["desconto_da_semana"].items():
        v = float(pct.rstrip("%").replace(",", ".")) / 100
        if v < 1:
            pos.append((f"{p} · {pct}", v))
    return pos + [("Falha · metade", 0.5)] + [(f"{n} · falha", v / 2) for n, v in pos]


def regras(CAT=None):
    """tudo o que a aba lê do catálogo, já na forma em que ela usa"""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    eq, ed, fora = CAT["equipamento"], CAT["equipamento_defesa"], CAT["fora_do_livro"]
    leve = eq["volume"]["leve"]
    vol = lambda v: leve if v == "leve" else v
    tiro, arr = eq["faixa_de_projetil"]["tiro"], eq["faixa_de_projetil"]["arremesso"]
    alcance = {n: f"{a} m, longa {b} m" for n, (a, b) in tiro.items()}
    alcance.update({n: f"{arr['faixa'][0]} m, longa {arr['faixa'][1]} m" for n in arr["armas"]})
    categorias = {c: lista for lista, cats in eq["treino"]["listas"].items() for c in cats}
    armas = []
    for n, a in eq["armas"].items():
        armas.append({"nome": n, "categoria": a["categoria"], "mao": a["mao"], "dado": a["dado"],
                      "propriedades": " · ".join(a["propriedades"]),
                      "forca": "—" if a["requer_forca"] is None else a["requer_forca"], "volume": vol(a["volume"]),
                      "alcance": alcance.get(n), "recarga": eq["municao"].get(n)})
    escudos = []
    for n, e in ed["escudos"].items():
        escudos.append({"nome": n, "categoria": "Escudo", "mao": 1, "dado": "—", "protecao": e["protecao"],
                        "propriedades": f"Proteção +{e['protecao']} · teto de Destreza {e['teto_de_destreza']}",
                        "forca": "—" if e["requer_forca"] is None else e["requer_forca"],
                        "volume": vol(eq["volume"]["de_uniforme_e_escudo"][n]), "alcance": None, "recarga": None})
    patentes = list(CAT["patentes"]["salario_por_mes"])
    uniformes = []
    for n, u in ed["uniformes"].items():
        minimo = eq["grau_minimo"].get(n, patentes[0])
        uniformes.append({"nome": n, "protecao": u["protecao"],
                          "teto": "—" if u["teto_de_destreza"] is None else u["teto_de_destreza"],
                          "forca": u["requer_forca"] or 0, "volume": vol(eq["volume"]["de_uniforme_e_escudo"][n]),
                          "ordem": patentes.index(minimo) + 1, "grau": minimo})
    tipos = [(k[0].upper() + k[1:], v) for k, v in CAT["missoes"]["tamanho"].items()] + list(fora["missoes_solo"].items())
    import ficha_automatica
    caminhos_todas = ficha_automatica.regras(CAT)["caminhos_todas_armas"]   # lido do manual.txt
    # o que cada propriedade faz: o catálogo não traz, e o equipamento-do-livro.json (extrair_equipamento.py) lê do livro.
    # Onde a tabela do livro só aponta ("Ver Munição"), entra a regra da seção apontada.
    LIV = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "equipamento-do-livro.json"), encoding="utf-8"))
    propriedades = []
    for pr in LIV["propriedades"] + LIV["restricoes"]:
        faz = pr["faz"]
        if pr["nome"] == DUAS_MAOS:                           # a frase sobre a coluna do catálogo não serve na ficha
            corte = " Aparece como 2 na coluna Mãos."
            assert faz.endswith(corte), faz
            faz = faz[:-len(corte)]
        propriedades.append((pr["nome"], " ".join([faz] + (LIV["a_regra_da_secao"][pr["ver"]] if pr["ver"] else []))))
    sem_texto = sorted({x for a in eq["armas"].values() for x in a["propriedades"]} - {n for n, _ in propriedades})
    assert not sem_texto and DUAS_MAOS in dict(propriedades) and all(k in dict(propriedades) for k in (LONGO_ALCANCE, MUNICAO, ALCANCE)), sem_texto
    return {
        "propriedades": propriedades, "texto_do_soco": LIV["soco"], "texto_do_escudo": LIV["escudo"],
        "alcance_da_propriedade": LIV["alcance_no_corpo_a_corpo"]["o_que_chega_mais_longe"],
        "armas": armas, "escudos": escudos, "uniformes": uniformes, "categorias": categorias,
        "conjurador": eq["treino"]["conjurador_treina"], "caminhos_todas": caminhos_todas,
        "patentes": [(p, "¥ " + _milhar(s), i + 1) for i, (p, s) in enumerate(CAT["patentes"]["salario_por_mes"].items())],
        "fundo_inicial": CAT["patentes"]["salario_por_mes"][patentes[0]],
        "situacoes": [s[0].upper() + s[1:] for s in eq["situacoes_do_traje"]] + [OUTRA_SITUACAO],
        "soco": [eq["soco_por_maestria"][str(i)] for i in range(1, 5)],
        "leve": leve, "limite_base": int(re.match(r"(\d+) \+ Força", eq["volume"]["limite"]).group(1)),
        "tipos": tipos, "multiplicadores": list(fora["xp_adicional"].items()), "descontos": descontos(CAT["missoes"]),
        "niveis": CAT["progressao"]["tabela_impressa"], "limiar": CAT["progressao"]["limiar_do_feito"]["nivel"],
    }


# ---------------------------------------------------------------------------------------------
# Onde cada caixa mora. Uma função só, lida pela aba, pelas contas da DADOS e pelo índice.
# ---------------------------------------------------------------------------------------------
def geometria(R):
    d, u = L_DOSSIE + FX - 1, L_USO + FX - 1          # a última linha do título: o que vem embaixo conta dela
    g = {
        "grau": f"AB{d + 2}", "nome": f"Q{d + 2}", "historia": f"Q{d + 18}",
        # 08/10/2026 (B41): o traço, as cicatrizes e os dois Legados (o nome, o tipo e o que faz)
        "traco": f"Q{d + 14}", "cicatrizes": f"AI{d + 10}",
        "legado_nome": [f"D{d + 32}", f"Y{d + 32}"], "legado_tipo": [f"Q{d + 32}", f"AM{d + 32}"],
        "legado_texto": [f"D{d + 33}", f"Y{d + 33}"],
        "principal": f"D{u + 2}", "secundaria": f"S{u + 2}", "vestindo": f"AH{u + 2}",
        "det_principal": f"D{u + 4}", "det_secundaria": f"S{u + 4}", "det_vestindo": f"AH{u + 4}",
        "marca_treino": f"D{u + 5}", "marca_forca_p": f"K{u + 5}",
        "marca_forca_s": f"S{u + 5}", "marca_selo": f"Z{u + 5}",
        "marca_grau": f"AH{u + 5}", "marca_forca_v": f"AO{u + 5}",
        "carga": f"D{L_FILEIRA + 1}", "carga_barra": f"I{L_FILEIRA + 1}", "ienes": f"O{L_FILEIRA + 1}",
        "salario": f"W{L_FILEIRA + 1}", "requisito": f"AF{L_FILEIRA + 1}", "situacao": f"AN{L_FILEIRA + 1}",
        "xp_total": _a1(B1, d + 2), "falta_rot": _a1(B2, d + 1), "falta": _a1(B2, d + 2),
        "falta_barra": _a1(B2 + C_ADIC, d + 2),
    }
    # o treino em armas: a caixa de cada grupo e de cada arma
    g["grupos"], g["armas"] = {}, {}
    por_cat = {}
    for a in R["armas"]:
        por_cat.setdefault(a["categoria"], []).append(a["nome"])
    fim = L_TREINO + FX - 1
    for col, larg, cats in COLUNAS_TREINO:
        lin = L_TREINO + FX
        for cat in cats:
            g["grupos"][cat] = (col, lin, larg)
            lin += 1
            for nome in por_cat[cat]:
                g["armas"][nome] = (col, lin, larg)
                lin += 1
        fim = max(fim, lin - 1)
    g["treino_ini"], g["treino_fim"] = L_TREINO + FX, fim
    g["equip_ini"], g["equip_fim"] = L_EQUIP + FX + 1, L_EQUIP + FX + EQUIP_MENU + EQUIP_LIVRE
    g["itens_ini"], g["itens_fim"] = L_ITENS + FX + 1, L_ITENS + FX + ITENS_LINHAS
    g["missao_ini"], g["missao_fim"] = L_MISSAO_CAB + 1, L_NIVEIS - 2
    g["niveis_ini"] = L_NIVEIS + FX + 1
    return g


# ---------------------------------------------------------------------------------------------
# As tabelas, as contas e o índice que vão para a DADOS, e as três caixas da FICHA que mudam.
# ---------------------------------------------------------------------------------------------
def trocas(layout, CAT=None):
    """{"celulas": {aba: {coord: (valor, coord_do_estilo)}}, "menus_sai": {aba: [coord]},
        "dados_colunas": (primeira, última), "H": contas, "T": tabelas, "indice": {campo: célula}}"""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    R = regras(CAT)
    G = geometria(R)
    idx = ix.indice(layout)
    falta = [k for k in ("atr_Força", "maestria", "nivel", "equipamento", "xp", "deslocamento", "caminho") if not idx.get(k)]
    if falta:
        raise SystemExit(f"o indice da DADOS nao publica {falta}: a Ficha Pessoal le essas caixas da FICHA")
    ficha, dados = ix._aba(layout, "FICHA"), ix._aba(layout, "DADOS")
    fcel = {r[0]: r for r in ficha["celulas"]}
    dcel = {r[0]: r for r in dados["celulas"]}
    lin_cab = ix._lc(next(r[0] for r in dados["celulas"] if r[1] == "marcos"))[0]
    ref_cab = next(r[0] for r in dados["celulas"] if r[1] == "marcos")
    ref_txt = next(r[0] for r in dados["celulas"] if ix._lc(r[0]) == (lin_cab + 1, 1))
    ref_num = f"{ref_cab[:-len(str(lin_cab))]}{lin_cab + 1}"
    # depois do índice da FICHA (BA e BB), com uma coluna de respiro
    c_idx = max(ix._lc(r[0])[1] for r in dados["celulas"] if r[1] == "célula" and ix._lc(r[0])[0] == lin_cab)
    c0 = c_idx + 2
    cel = {"FICHA": {}, "DADOS": {}}
    T = {}
    prox = [c0]

    def tabela(nome, cabecalhos, linhas):
        """escreve a tabela na próxima faixa livre, e guarda onde ela ficou: T[nome] = (coluna, primeira, última)"""
        col = prox[0]
        for j, t in enumerate(cabecalhos):
            cel["DADOS"][f"{ix._letras(col + j)}{lin_cab}"] = (t, ref_cab)
        for i, lin in enumerate(linhas):
            for j, v in enumerate(lin):
                if v is not None:
                    cel["DADOS"][f"{ix._letras(col + j)}{lin_cab + 1 + i}"] = (
                        v, ref_txt if isinstance(v, str) and not v.startswith("=") else ref_num)
        T[nome] = (col, lin_cab + 1, lin_cab + len(linhas), len(cabecalhos))
        prox[0] = col + len(cabecalhos) + 1
        return col

    def faixa_t(nome, colunas=None, so=None):
        col, l1, l2, n = T[nome]
        if so is not None:
            return _faixa(col + so, l1, col + so, l2, "DADOS!")
        return _faixa(col, l1, col + (colunas or n) - 1, l2, "DADOS!")

    # --- os equipáveis: as armas e os escudos, em ordem alfabética, com a caixa de treino de cada arma
    equip = sorted(R["armas"] + R["escudos"], key=lambda a: _ordem(a["nome"]))
    linhas = []
    for a in equip:
        if a["nome"] in G["armas"]:
            col, lin, _ = G["armas"][a["nome"]]
            marcado, caixa = f"={FP}{_abs(col, lin)}", _endereco(_a1(col, lin), FP)
        else:
            marcado, caixa = "=TRUE", None                     # o escudo não pede treino
        linhas.append([a["nome"], a["categoria"], a["mao"], a["dado"], a["propriedades"], a["forca"], a["volume"],
                       a["alcance"], a["recarga"], marcado, caixa])
    tabela("equip", ["equipável", "categoria do equipável", "mão do equipável", "dado do equipável",
                     "propriedades do equipável", "força do equipável", "volume do equipável",
                     "alcance do equipável", "recarga do equipável", "treino marcado", "caixa do treino"], linhas)
    EQUIP = faixa_t("equip")
    # --- as categorias de arma: a lista de treino, se o conjurador treina, e a caixa do grupo
    linhas = []
    for cat, lista in R["categorias"].items():
        col, lin, _ = G["grupos"][cat]
        linhas.append([cat, lista, "sim" if cat in R["conjurador"] else "não", f"={FP}{_abs(col, lin)}",
                       _endereco(_a1(col, lin), FP)])
    tabela("categ", ["categoria de arma", "lista de treino", "conjurador treina", "grupo marcado", "caixa do grupo"], linhas)
    tabela("todas", ["Caminho que treina todas as armas"], [[c] for c in R["caminhos_todas"]])
    tabela("unif", ["uniforme", "proteção do uniforme", "teto do uniforme", "força do uniforme", "volume do uniforme",
                    "ordem do grau mínimo", "grau mínimo"],
           [[u["nome"], u["protecao"], u["teto"], u["forca"], u["volume"], u["ordem"], u["grau"]] for u in R["uniformes"]])
    tabela("grau", ["patente", "salário por mês", "ordem da patente"], [list(p) for p in R["patentes"]])
    tabela("sit", ["situação do traje"], [[s] for s in R["situacoes"]])
    tabela("tipo", ["tipo de missão", "xp do tipo"], [list(t) for t in R["tipos"]])
    tabela("mult", ["adicional da missão", "multiplicador"], [list(t) for t in R["multiplicadores"]])
    tabela("desc", ["desconto da missão", "fração paga"], [list(t) for t in R["descontos"]])
    tabela("grau_ferramenta", ["grau da ferramenta"], [["—"]] + [[p[0]] for p in R["patentes"]])
    # o nível em que o XP sozinho para de subir: dali em diante o livro pede um feito
    tabela("limiar", ["limiar do feito"], [[R["limiar"]]])

    # --- as contas, no molde das "contas da ficha": nome e valor
    H, contas = {}, []
    c_contas = prox[0]

    def conta(nome, formula):
        H[nome] = f"DADOS!${ix._letras(c_contas + 1)}${lin_cab + 1 + len(contas)}"
        contas.append((nome, formula))

    P, S, V, GR = (_A(G[k], FP) for k in ("principal", "secundaria", "vestindo", "grau"))
    TAB = _faixa(C("D"), G["equip_ini"], C("AH"), G["equip_fim"], FP)
    desloc = {r: C(a) - C("D") + 1 for r, a, _ in COLS_EQUIP}      # a posição de cada coluna dentro da tabela
    FOR, MAE, NIV = (_A(idx[k], "FICHA!") for k in ("atr_Força", "maestria", "nivel"))
    UNIF, GRAUS = faixa_t("unif"), faixa_t("grau")

    def da_tabela(quem, coluna, numero=False, vazio='""'):
        v = f'VLOOKUP({quem},{TAB},{desloc[coluna]},FALSE)'
        return f'IFERROR(VALUE({v}&""),0)' if numero else f'IFERROR({v}&"",{vazio})'

    conta("força", f"=N({FOR})")
    conta("soco na principal", f'=IF(OR({P}="",{P}="{SOCO}"),1,0)')
    soco = H["soco na principal"]
    conta("categoria da principal", f'=IF({soco}=1,"{SOCO}",{da_tabela(P, "Categoria")})')
    conta("mão da principal", f'=IF({soco}=1,1,{da_tabela(P, "Mão", True)})')
    conta("dado da principal", f'=IF({soco}=1,CHOOSE(MIN(4,MAX(1,N({MAE}))),' + ",".join(f'"{d}"' for d in R["soco"]) +
          f'),{da_tabela(P, "Dado")})')
    conta("propriedades da principal", f'=IF({soco}=1,"",{da_tabela(P, "Propriedades")})')
    conta("força da principal", f'=IF({soco}=1,0,{da_tabela(P, "Força", True)})')
    conta("nas duas mãos", f'=IF(AND(ISNUMBER(SEARCH("Versátil",{H["propriedades da principal"]})),{S}="{NAS_DUAS}"),1,0)')
    d_ = H["dado da principal"]
    conta("dado em uso", f'=IF({H["nas duas mãos"]}=1,IF({d_}="d6","d8",IF({d_}="d8","d10",IF({d_}="d10","d12",{d_}))),{d_})')
    conta("alcance da principal", f'=IFERROR(VLOOKUP({P},{EQUIP},8,FALSE)&"","")')
    conta("recarga da principal", f'=IFERROR(VLOOKUP({P},{EQUIP},9,FALSE)&"","")')
    # treinada: a caixa da arma; se a arma foi digitada numa linha livre, a caixa do grupo da categoria dela
    conta("treino da principal",
          f'=IF({soco}=1,1,IF(IFERROR(VLOOKUP({P},{EQUIP},10,FALSE),'
          f'IFERROR(VLOOKUP({H["categoria da principal"]},{faixa_t("categ")},4,FALSE),FALSE))=TRUE,1,0))')
    conta("secundária vale", f'=IF(AND({H["mão da principal"]}<>2,{S}<>"",{S}<>"{MAO_LIVRE}",{S}<>"{NAS_DUAS}"),1,0)')
    sv = H["secundária vale"]
    conta("categoria da secundária", f'=IF({sv}=1,{da_tabela(S, "Categoria")},"")')
    conta("escudo na secundária", f'=IF(AND({sv}=1,{H["categoria da secundária"]}="Escudo"),1,0)')
    conta("dado da secundária", f'=IF({sv}=1,{da_tabela(S, "Dado")},"")')
    conta("propriedades da secundária", f'=IF({sv}=1,{da_tabela(S, "Propriedades")},"")')
    conta("força da secundária", f'=IF({sv}=1,{da_tabela(S, "Força", True)},0)')
    conta("alcance da secundária", f'=IF({sv}=1,IFERROR(VLOOKUP({S},{EQUIP},8,FALSE)&"",""),"")')
    conta("recarga da secundária", f'=IF({sv}=1,IFERROR(VLOOKUP({S},{EQUIP},9,FALSE)&"",""),"")')
    # quantos equipáveis guardados entram no menu de cada mão: com zero, a linha embaixo da mão diz como pôr um lá
    eq_nome, eq_cat, eq_mao = (_faixa(C(c_), G["equip_ini"], C(c_), G["equip_fim"], FP) for c_ in ("D", "M", "S"))
    conta("guardados para a principal", f'=SUMPRODUCT(--({eq_nome}<>""),--({eq_cat}<>"Escudo"))')
    conta("guardados para a secundária", f'=SUMPRODUCT(--({eq_nome}<>""),--((({eq_cat}="Escudo")+({eq_mao}=1))>0))')
    conta("uniforme vale", f'=IF(ISNUMBER(MATCH({V},{faixa_t("unif", so=0)},0)),1,0)')
    uv = H["uniforme vale"]
    for nome, col in (("proteção do uniforme", 2), ("teto do uniforme", 3), ("força do uniforme", 4),
                      ("volume do uniforme", 5), ("ordem do grau mínimo", 6), ("grau mínimo", 7)):
        vazio = '""' if nome in ("teto do uniforme", "grau mínimo") else "0"
        conta(nome, f'=IF({uv}=1,VLOOKUP({V},{UNIF},{col},FALSE),{vazio})')
    conta("ordem do grau", f"=IFERROR(VLOOKUP({GR},{GRAUS},3,FALSE),1)")
    conta("uniforme liberado", f'=IF(OR({uv}=0,{H["ordem do grau"]}>={H["ordem do grau mínimo"]}),1,0)')
    f_ = H["força"]
    conta("falta força na principal", f'=IF({H["força da principal"]}>{f_},1,0)')
    conta("falta força na secundária", f'=IF(AND({sv}=1,{H["força da secundária"]}>{f_}),1,0)')
    conta("falta força no uniforme", f'=IF(AND({uv}=1,{H["força do uniforme"]}>{f_}),1,0)')
    vols = [_faixa(C("AG"), G["equip_ini"], C("AG"), G["equip_fim"], FP)] + \
           [_faixa(C(cols[2][1]), G["itens_ini"], C(cols[2][1]), G["itens_fim"], FP) for cols in COLS_ITENS]
    conta("volume guardado", "=" + "+".join(f"SUM({v})" for v in vols))
    # o livro soma sem arredondar; o ROUND em duas casas só tira o resto de ponto flutuante (0,1 + 0,2)
    conta("carga", f'=ROUND({H["volume guardado"]}+{H["volume do uniforme"]},2)')
    conta("limite de carga", f'={R["limite_base"]}+{f_}')
    conta("carga acima", f'=IF({H["carga"]}>{H["limite de carga"]},1,0)')
    # 04/10/2026, as regras do livro reconstruído: arma empunhada sem a Força corta o deslocamento pela metade e tira a
    # Destreza da Defesa; uniforme ou escudo sem a Força não dá a proteção dele; carga acima do limite não deixa andar.
    # 07/10/2026: a arma sem a Força deixa de tirar a Destreza da Defesa e passa a dar desvantagem nos ataques com ela
    # ("ideal é ser só a desvantagem no ataque e metade do deslocamento", o Mizuki, que ainda vai mudar o livro). A
    # desvantagem não é número: fica na nota do requisito de Força e na nota dos ataques da FICHA
    conta("arma sem força", f'=IF(OR({H["falta força na principal"]}=1,AND({H["falta força na secundária"]}=1,'
                            f'{H["escudo na secundária"]}=0)),1,0)')
    conta("meia marcha", f'={H["arma sem força"]}')
    conta("proteção sem força", f'=IF({H["falta força no uniforme"]}=1,{H["proteção do uniforme"]},0)+'
                                f'IF(AND({H["falta força na secundária"]}=1,{H["escudo na secundária"]}=1),'
                                f'IFERROR(VLOOKUP({S},{tabela_da_defesa(dados, lin_cab)},2,FALSE),0),0)')
    conta("parado pela carga", f'={H["carga acima"]}')
    tot = [_faixa(b + C_TOTAL, G["missao_ini"], b + C_TOTAL, G["missao_fim"], FP) for b in BLOCOS]
    conta("xp total", "=" + "+".join(f"SUM({t})" for t in tot))
    conta("nível", f"=N({NIV})")
    niv_cab = next(r[0] for r in dados["celulas"] if r[1] == "nível" and ix._lc(r[0])[0] == lin_cab)
    c_niv = ix._lc(niv_cab)[1]
    n_niveis = sum(1 for n in R["niveis"] if int(n) >= 2)
    NIVEIS = _faixa(c_niv, lin_cab + 1, c_niv + 1, lin_cab + n_niveis, "DADOS!")
    conta("xp do próximo nível", f'=IFERROR(VLOOKUP({H["nível"]}+1,{NIVEIS},2,FALSE),"")')
    conta("xp deste nível", f'=IFERROR(VLOOKUP({H["nível"]},{NIVEIS},2,FALSE),0)')
    # a cor da barra cheia (vida, energia, integridade, carga e XP): nasce no osso da ficha de fábrica, e a troca de
    # paleta do Codigo.gs grava aqui a cor do tema. As barras leem esta célula, e por isso mudam sem ninguém
    # reescrever fórmula. O âmbar e o vermelho de vida baixa continuam fixos (decisão A5).
    conta(COR_DA_BARRA, f"#{OSSO[2:]}")
    for i, (nome, form) in enumerate(contas, start=1):
        cel["DADOS"][f"{ix._letras(c_contas)}{lin_cab + i}"] = (nome, ref_txt)
        cel["DADOS"][f"{ix._letras(c_contas + 1)}{lin_cab + i}"] = (form, ref_num)
    cel["DADOS"][f"{ix._letras(c_contas)}{lin_cab}"] = ("contas da pessoal", ref_cab)
    cel["DADOS"][f"{ix._letras(c_contas + 1)}{lin_cab}"] = ("valor da pessoal", ref_cab)
    prox[0] = c_contas + 3

    # --- os menus que mudam com a ficha: as duas mãos e o que o Grau deixa vestir
    eq_linhas = range(G["equip_ini"], G["equip_fim"] + 1)
    nome_, cat_, mao_ = (lambda l: _abs(C("D"), l, FP)), (lambda l: _abs(C("M"), l, FP)), (lambda l: _abs(C("S"), l, FP))
    tabela("menu_principal", ["menu da mão principal"],
           [[SOCO]] + [[f'=IF(AND({nome_(l)}<>"",{cat_(l)}<>"Escudo"),{nome_(l)},"")'] for l in eq_linhas])
    tabela("menu_secundaria", ["menu da mão secundária"],
           [[MAO_LIVRE], [f'=IF(AND({H["mão da principal"]}<>2,ISNUMBER(SEARCH("Versátil",{H["propriedades da principal"]}))),"{NAS_DUAS}","")']] +
           [[f'=IF(AND({H["mão da principal"]}<>2,{nome_(l)}<>"",OR({cat_(l)}="Escudo",N({mao_(l)})=1)),{nome_(l)},"")'] for l in eq_linhas])
    col_u = T["unif"][0]
    tabela("menu_vestindo", ["menu do vestindo"],
           [[SEM_UNIFORME]] + [[f'=IF({H["ordem do grau"]}>={_abs(col_u + 5, T["unif"][1] + i, "DADOS!")},'
                                f'{_abs(col_u, T["unif"][1] + i, "DADOS!")},"")'] for i in range(len(R["uniformes"]))])

    # --- as notas que mudam com a ficha: o Codigo.gs copia o texto para a nota da caixa
    fp_, fs_, fu_ = H["falta força na principal"], H["falta força na secundária"], H["falta força no uniforme"]
    esc = H["escudo na secundária"]
    SIT = _A(G["situacao"], FP)
    notas = [
        ("requisito de força",
         f'=IF({fp_}+{fs_}+{fu_}=0,"Tudo o que está em uso cabe na sua Força.",'
         f'IF({fp_}=1,{P}&" pede Força "&{H["força da principal"]}&". ","")&'
         f'IF({fs_}=1,{S}&" pede Força "&{H["força da secundária"]}&". ","")&'
         f'IF({fu_}=1,{V}&" pede Força "&{H["força do uniforme"]}&". ","")&"Você tem "&{f_}&"."&'
         f'IF(OR({fp_}=1,AND({fs_}=1,{esc}=0))," Empunhar uma arma sem a Força dá desvantagem nos ataques com ela e corta o '
         f'seu deslocamento pela metade.","")&'
         f'IF(OR({fu_}=1,AND({fs_}=1,{esc}=1))," Sem a Força, o uniforme ou o escudo não pode ser preparado e não dá a '
         f'proteção dele: a Defesa já desconta.",""))'),
        ("carga",
         f'=IF({H["carga acima"]}=1,"Você passou do limite: não pode se deslocar com essa carga. Largue ou guarde o que '
         f'passou antes de andar, nadar, escalar ou voar.","")'),
        ("situação do traje",
         f'=IF(AND({uv}=1,LEFT({V},5)<>"Traje"),"Só o Traje carrega situação. O Revestimento não tem.",'
         f'IF({SIT}="","",IF({SIT}="{OUTRA_SITUACAO}","Você pode criar a sua, em uma ou duas palavras. O mestre confere três '
         f'coisas: é condição física que ele já descreveu na cena; não decide o que uma perícia de Destreza já decide; e não '
         f'acontece toda cena.","Situação “"&LOWER({SIT})&"”: quando a cena estiver nessa condição, você tem vantagem no tipo de '
         f'Teste de Resistência e nas perícias que escolheu para o Traje (tantas quanto a sua maestria).")))'),
    ]
    # --- o que cada propriedade faz (pedido dele, 01/10/2026): a nota da linha embaixo da mão lista as da arma em uso
    c_prop = tabela("props", ["propriedade de arma", "o que a propriedade faz"], [[n, t] for n, t in R["propriedades"]])
    l_prop = T["props"][1]

    def nota_da_arma(quem, props, alc, rec, duas=None):
        """o nome da arma e, uma por linha, cada propriedade dela com o que faz"""
        partes = []
        for i, (nome, _) in enumerate(R["propriedades"]):
            n_, t_ = _abs(c_prop, l_prop + i, "DADOS!"), _abs(c_prop + 1, l_prop + i, "DADOS!")
            if nome == DUAS_MAOS:                             # no catálogo ela é o 2 da coluna mão, não uma propriedade
                if duas is None:
                    continue
                tem = duas
            else:                                             # cercada, para o Alcance não casar com o Longo Alcance
                tem = f'ISNUMBER(SEARCH(" · "&{n_}&" · "," · "&{props}&" · "))'
            mais = (f'&IF({alc}<>""," Nesta arma: "&{alc}&".","")' if nome == LONGO_ALCANCE else
                    f'&IF({rec}&""<>""," Nesta arma: "&{rec}&IF({rec}=1," ataque"," ataques")&" por carga.","")' if nome == MUNICAO else
                    f'&" Nesta arma: {R["alcance_da_propriedade"]}."' if nome == ALCANCE else "")
            partes.append(f'IF({tem},CHAR(10)&{n_}&": "&{t_}{mais},"")')
        return f'{quem}&' + "&".join(partes)

    cp_, cs_ = H["categoria da principal"], H["categoria da secundária"]
    notas += [
        ("arma da principal",
         f'=IF({H["soco na principal"]}=1,"{SOCO}"&CHAR(10)&"{R["texto_do_soco"]}",IF({cp_}="","",' +
         nota_da_arma(P, H["propriedades da principal"], H["alcance da principal"], H["recarga da principal"],
                      f'{H["mão da principal"]}=2') + "))"),
        ("arma da secundária",
         f'=IF(OR({H["secundária vale"]}=0,{cs_}=""),"",IF({esc}=1,{S}&CHAR(10)&"{R["texto_do_escudo"]}",' +
         nota_da_arma(S, H["propriedades da secundária"], H["alcance da secundária"], H["recarga da secundária"]) + "))"),
    ]
    alvo_nota = {"requisito de força": G["requisito"], "carga": G["carga"], "situação do traje": G["situacao"],
                 "arma da principal": G["det_principal"], "arma da secundária": G["det_secundaria"]}
    col_n = tabela("notas", ["nota viva", "texto da nota", "caixa da nota"],
                   [[n, f, _endereco(alvo_nota[n], FP)] for n, f in notas])

    # --- o índice da Ficha Pessoal: o campo e o endereço dele, em fórmula
    faixas_ = lambda a, b: _endereco_faixa(a, b, FP)
    missoes = [(f"missões {i}", faixas_(_a1(b, G["missao_ini"]), _a1(b + ULT, G["missao_fim"]))) for i, b in enumerate(BLOCOS, 1)]
    indice = [
        ("principal", _endereco(G["principal"], FP)), ("secundária", _endereco(G["secundaria"], FP)),
        ("vestindo", _endereco(G["vestindo"], FP)), ("grau", _endereco(G["grau"], FP)),
        ("situação do traje", _endereco(G["situacao"], FP)), ("xp total", _endereco(G["xp_total"], FP)),
        ("treino", faixas_(_a1(C("D"), G["treino_ini"]), _a1(C("AT"), G["treino_fim"]))),
        *missoes,
        ("equipáveis", faixas_(_a1(C("D"), G["equip_ini"]), _a1(C("AT"), G["equip_fim"]))),
        ("itens", faixas_(_a1(C("D"), G["itens_ini"]), _a1(C("AT"), G["itens_fim"]))),
        ("volume dos itens 1", faixas_(_a1(C(COLS_ITENS[0][2][1]), G["itens_ini"]), _a1(C(COLS_ITENS[0][2][1]), G["itens_fim"]))),
        ("volume dos itens 2", faixas_(_a1(C(COLS_ITENS[1][2][1]), G["itens_ini"]), _a1(C(COLS_ITENS[1][2][1]), G["itens_fim"]))),
        ("em uso", faixas_(_a1(C("D"), L_USO), _a1(C("AT"), L_USO + FX + 4))),
        ("fileira", faixas_(_a1(C("D"), L_FILEIRA), _a1(C("AT"), L_FILEIRA + 2))),
        (COR_DA_BARRA, _endereco(H[COR_DA_BARRA].replace("DADOS!", "").replace("$", ""), "DADOS!")),
    ]
    col_i = tabela("indice", ["campo pessoal", "célula pessoal"], [[k, v] for k, v in indice])
    # 08/10/2026 (B41): os três tipos de Legado do livro (Origens e Legados). A tabela vai por último, depois do índice,
    # para as colunas de antes não mudarem de lugar: o Codigo.gs acha o índice desta aba numa coluna fixa
    tabela("legado_tipo", ["tipo de legado"], [[t_] for t_ in TIPOS_DE_LEGADO])

    # as colunas depois do índice são desta limpeza: o que uma exportação trouxer de uma rodada anterior é
    # reescrito, e a célula que sobrar fica vazia. Antes delas, nada pode ser tocado.
    for coord, r in dcel.items():
        if ix._lc(coord)[1] >= c0 and coord not in cel["DADOS"] and r[1] is not None:
            cel["DADOS"][coord] = (None, coord)
    fora = [c for c in cel["DADOS"] if ix._lc(c)[1] < c0]
    if fora:
        raise SystemExit(f"a Ficha Pessoal escreveria na DADOS antes da coluna {ix._letras(c0)}: {fora[:5]}")

    # --- as três barras da FICHA (vida, energia e integridade): a cheia deixa de ser o osso escrito na fórmula e
    # passa a ler a cor do tema. O Sheets exporta a SPARKLINE embrulhada, com as aspas dobradas.
    osso_na_formula = f'""#{OSSO[2:]}""'
    barras = [c for c, r in fcel.items() if isinstance(r[1], str) and "SPARKLINE" in r[1]]
    if len(barras) != 3 or any(fcel[c][1].count(osso_na_formula) != 2 for c in barras):
        raise SystemExit(f"a FICHA devia ter 3 barras com o osso escrito duas vezes em cada, e tem {barras}")
    for c in barras:
        cel["FICHA"][c] = (fcel[c][1].replace(osso_na_formula, H[COR_DA_BARRA]), c)

    # --- as três caixas da FICHA
    eq_c, xp_c, des_c = idx["equipamento"], idx["xp"], idx["deslocamento"]
    cel["FICHA"][eq_c] = (f'=IF({uv}=1,{V}&IF({esc}=1," + "&{S},""),IF({esc}=1,{S},""))', eq_c)
    cel["FICHA"][xp_c] = (f'={H["xp total"]}', xp_c)
    des = fcel[des_c][1]
    m = re.match(r'^=\((.*)\)&" m"$', des) if isinstance(des, str) else None
    if not m:
        raise SystemExit(f"o DESLOCAMENTO da FICHA ({des_c}) devia ser '=(metros)&\" m\"', e e {des!r}")
    # 08/10/2026 (B41): a Exaustão no degrau 2 limita o deslocamento a 4,5 m, sem aumentar o que já está menor ("O limite
    # de 4,5 m não aumenta um deslocamento que já esteja menor ou zerado"). A caixa da Exaustão mora embaixo das barras
    # (estado_do_personagem.py); numa exportação de antes dela, a conta fica como era
    import estado_do_personagem as _ep
    metros = f'({m.group(1)})/IF({H["meia marcha"]}=1,2,1)'
    if idx.get("exaustão"):
        metros = f'MIN(IF(N({_A(idx["exaustão"])})>=2,{_ep.LIMITE_DA_EXAUSTAO},9999),{metros})'
    cel["FICHA"][des_c] = (f'=IF({H["parado pela carga"]}=1,0,{metros})&" m"', des_c)
    # e o espelho dos dois Legados: o nome, o tipo e o que faz, como estão escritos no dossiê
    for k_, campo in enumerate(("legado 1", "legado 2")):
        if idx.get(campo):
            nm, tp, tx = (_A(G[q][k_], FP) for q in ("legado_nome", "legado_tipo", "legado_texto"))
            cel["FICHA"][idx[campo]] = (f'=IF({nm}="","",{nm}&IF({tp}="",""," · "&{tp})&IF({tx}="","",": "&{tx}))', idx[campo])
    # a Defesa (defesa_equipamento.py) perde a proteção da peça usada sem a Força. Até 07/10/2026 perdia também a Destreza
    # com arma empunhada sem a Força; essa parte saiu (ver a conta "arma sem força", acima)
    df_c = idx["defesa"]
    dfm = re.match(r"^=10\+(IF\(.+?\)\)\))\+(\$[A-Z]+\$\d+)(.*)$", fcel[df_c][1]) if isinstance(fcel[df_c][1], str) else None
    if not dfm:
        raise SystemExit(f"a DEFESA da FICHA ({df_c}) nao tem a forma que o defesa_equipamento escreve: {fcel[df_c][1]!r}")
    cel["FICHA"][df_c] = (f'=10+{dfm.group(1)}+{dfm.group(2)}-{H["proteção sem força"]}{dfm.group(3)}', df_c)
    menus_sai = [m_["onde"] for m_ in ficha["menus"] if eq_c in m_["onde"].split()]
    return {"celulas": cel, "menus_sai": {"FICHA": menus_sai}, "dados_colunas": (c0, prox[0] - 2),
            "H": H, "T": T, "faixa_t": faixa_t, "R": R, "G": G, "indice_coluna": col_i, "lin_cab": lin_cab,
            "notas_coluna": col_n}


def _A(coord, aba=""):
    lin, col = ix._lc(coord)
    return f"{aba}${ix._letras(col)}${lin}"


# ---------------------------------------------------------------------------------------------
# A aba.
# ---------------------------------------------------------------------------------------------
def _titulo(f, lin, c1, c2, texto, nota=None):
    """o título de seção, em duas linhas mescladas; devolve a última linha dele, de onde o resto da seção conta"""
    f.add("faixa", c1, lin, c2, lin + FX - 1, texto, nota)
    return lin + FX - 1


class _Folha:
    def __init__(self, layout):
        self.layout, self.cel, self.mesclas, self.dentro = layout, {}, [], set()
        self.menus, self.notas, self.bools = [], {}, []
        self._e = {}

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

    def add(self, estilo, c1, l1, c2, l2, valor=None, nota=None):
        """uma caixa: mesclada se tiver mais de uma célula, com o valor e o estilo no canto"""
        c1, c2 = (C(c) if isinstance(c, str) else c for c in (c1, c2))
        coord = _a1(c1, l1)
        for l in range(l1, l2 + 1):
            for c in range(c1, c2 + 1):
                if (l, c) in self.dentro:
                    raise SystemExit(f"ficha_pessoal: a caixa {coord} cai em cima de outra, em {_a1(c, l)}")
                self.dentro.add((l, c))
        self.cel[coord] = (valor, self.estilo(estilo) if isinstance(estilo, str) else estilo)
        if (c1, l1) != (c2, l2):
            self.mesclas.append(f"{coord}:{_a1(c2, l2)}")
        if nota:
            self.notas[coord] = nota
        return coord

    def caixa(self, c1, c2, lin, rotulo, valor=None, estilo="val", nota=None):
        """o rótulo numa linha e o valor nas duas de baixo"""
        self.add("rot", c1, lin, c2, lin, rotulo, nota)
        return self.add(estilo, c1, lin + 1, c2, lin + 2, valor)

    def menu(self, onde, formula):
        self.menus.append({"onde": onde, "tipo": "list", "formula": formula, "vazio_ok": True, "mostra_seta": True})


NOTAS = {
    "grau": "A sua patente na instituição. Ela define o salário e libera o Revestimento 2 e 3. Não é o grau da "
            "ferramenta que você carrega.",
    "nome": "Vem da CARTEIRA: o nome do portador é digitado lá.",
    "traco": "Uma relação, uma lembrança, uma ambição ou um problema ainda aberto, numa frase. É uma das escolhas da Origem, "
             "e não dá bônus.",
    "cicatrizes": "Depois da segunda queda na mesma missão, registre com o mestre se ficou uma cicatriz e como ela é. Não dá "
                  "modificador, e a cura não a apaga.",
    "legado": "Você escolhe dois na criação, da lista da sua Origem ou escritos com o mestre; pelo menos um é narrativo. "
              "Escreva o nome aqui e o que ele faz na caixa de baixo, com a frequência de uso. A FICHA mostra os dois.",
    "legado_tipo": "Narrativo: uma pessoa, informação, relação ou acesso. De rolagem: vantagem, repetição ou mudança de um "
                   "teste. De exceção: dispensa uma exigência ou impede um efeito, com uma contrapartida.",
    "principal": "Para uma arma aparecer neste menu, escolha ela antes nos EQUIPÁVEIS GUARDADOS, mais abaixo nesta aba. "
                 "O menu lista o Soco e o que estiver guardado lá. Com arma de duas mãos aqui, a mão secundária fica "
                 "ocupada. A linha de baixo mostra o dado e as propriedades, e a nota dela diz o que cada uma faz.",
    "secundaria": "Para uma arma ou um escudo aparecer neste menu, escolha antes nos EQUIPÁVEIS GUARDADOS, mais abaixo "
                  "nesta aba. O menu lista as armas de uma mão e os escudos guardados lá. Com arma Versátil na mão "
                  "principal, aparece a opção de segurar a mesma arma nas duas mãos, e o dado sobe um passo.",
    "vestindo": "O menu só lista o que o seu Grau libera. O que você veste aqui e o escudo da mão secundária vão "
                "sozinhos para o EQUIPAMENTO da FICHA.",
    "selo": "O escudo ocupa a mão. Se o seu Selo é um gesto, com ele na mão a sua técnica não sai.",
    "treino": "Marque as armas em que você é treinado. A caixa no nome do grupo marca ou desmarca o grupo inteiro de uma "
              "vez. Bastião e Vanguarda já vêm com todas marcadas; os outros Caminhos, com Arma de Fogo e Balestra. Sem "
              "treino, o ataque com a arma sai com desvantagem.",
    "carga": "O limite é 5 + Força, em Volume. Cada item leve vale 0,1. Arrastar, empurrar ou levantar é o dobro.",
    "ienes": "Digite quanto você tem. A ficha nova começa com a mensalidade do Grau 4, que é o fundo da criação.",
    "salario": "Sai do Grau, pela tabela Salário por patente do livro.",
    "requisito": "Olha a arma de cada mão, o escudo e o uniforme. Quando algo pede mais Força do que você tem, a nota "
                 "da caixa de baixo diz o que falta e o que isso custa.",
    "situacao": "Todo Traje carrega uma situação, escolhida na criação, junto com um tipo de Teste de Resistência e tantas "
                "perícias quanto a sua maestria. Quando a cena estiver nessa condição, você tem vantagem só nesses. Vantagem "
                "não empilha: duas fontes valem uma.",
    "qtd": "Em branco vale 1.",
    "vol": "Quantidade vezes o Volume de um. O item leve vale 0,1. A carga soma esta coluna.",
    "vol_item": "Quantidade vezes 0,1, que é o item leve. Se o mestre pesar o item de outro jeito, digite o Volume da "
                "linha por cima; apagar a caixa traz a conta de volta.",
    "grau_ferramenta": "O grau da ferramenta amaldiçoada: a energia que a peça carrega. Arma comum fica em —. Não é a "
                       "sua patente.",
    "estigma": "O Estigma da ferramenta amaldiçoada, se ela tiver um. É digitado, porque pode ser criado.",
    "desgaste": "Só para ferramenta com Desgaste. Anote quantas missões restam: cada missão em que você usar o Estigma "
                "gasta uma.",
    "livre": "As duas últimas linhas são livres: digite a linha inteira, para o que não está na lista.",
    "linha_livre": "Linha livre: digite o nome e as outras colunas à mão. Serve para o que não está no menu das linhas "
                   "de cima. Na coluna Vol., digite o Volume da linha inteira.",
    "xp_total": "A soma da coluna Total de todas as missões. A caixa XP da FICHA mostra este mesmo número, e o nível "
                "sobe por ele.",
    "falta": "O XP acumulado que o próximo nível pede, menos o seu XP total. O nível é o da FICHA. Do 20 para o 21 o "
             "livro pede também um feito, e o 30 é o topo.",
    "xp": "Escolha o tipo da missão. {tipos}.",
    "adicional": "O multiplicador da missão, quando a mesa dá: {mults}. Em branco, a missão vale o XP do tipo.",
    "desconto": "Para a missão que pagou menos. Na sua semana, as duas primeiras pagam cheio, a terceira 50%, a quarta 25%, "
                "a quinta 12,5%, a sexta 6,25%, e cada uma depois paga metade da anterior. Missão que falhou e o mestre deu "
                "metade é Falha; se ela também foi da terceira em diante, escolha a posição com falha (a terceira longa "
                "que falhou paga 200 × ½ × ½ = 50). Em branco, paga cheio.",
    "total": "O XP do tipo, vezes o Adicional, vezes o Desconto, arredondado para baixo só no fim. Quando a conta dá mais "
             "que zero e menos que 1, a missão paga 1.",
    "extensao": "Mais duas tabelas de missão, para quando as duas primeiras encherem. O XP total soma as quatro. Elas ficam "
                "num grupo de colunas fechado, dentro do painel.",
    "niveis": "A curva do livro, fixa. Para subir é o que custa sair daquele nível. Acumulado é o XP total em que você "
              "chega nele. A seta marca o seu nível.",
    "foto": "Vem da CARTEIRA: insira a foto na caixa FOTO de lá (Inserir › Imagem › Inserir imagem na célula), e ela "
            "aparece aqui. Se não aparecer, insira a mesma foto nesta caixa.",
}


def aba(layout, tr):
    """a aba inteira, pronta para entrar em layout['abas']. Lê o cabeçalho e a lombada da FICHA do `layout`,
    que por isso tem de vir depois das correções de borda."""
    R, G, H = tr["R"], tr["G"], tr["H"]
    ficha = ix._aba(layout, "FICHA")
    f = _Folha(layout)
    estilos_fmt = {}

    # --- o cabeçalho (linhas 1 a 7) e a lombada (colunas A e B), copiados da FICHA
    fcel = {r[0]: r for r in ficha["celulas"]}
    lombada = {"FICHA DE REGISTRO": NOME}
    for coord, r in fcel.items():
        lin, col = ix._lc(coord)
        if col > COLS_FOLHA or lin > L_FIM or (lin > 7 and col > 2):
            continue
        valor = lombada.get(r[1], r[1]) if col <= 2 else r[1]
        if isinstance(valor, str) and valor.startswith("=") and "!" not in valor:
            valor = f"=FICHA!{coord}"                           # fórmula que lê a própria FICHA: aqui ela espelha
        f.cel[coord] = (valor, r[2])
        f.dentro.add((lin, col))
    for m in ficha["mescladas"]:
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
        if c2 <= COLS_FOLHA and l2 <= L_FIM and (l2 <= 7 or c2 <= 2):
            f.mesclas.append(m)
            for l in range(l1, l2 + 1):
                for c in range(c1, c2 + 1):
                    f.dentro.add((l, c))
    # a lombada da FICHA pode acabar antes do fim desta aba: as linhas que faltarem repetem a última
    for col in (1, 2):
        ultima = max(l for (l, c) in f.dentro if c == col)
        molde = next(fcel[_a1(col, l)][2] for l in range(ultima, 0, -1) if _a1(col, l) in fcel and fcel[_a1(col, l)][1] is None)
        for lin in range(1, L_FIM + 1):
            if (lin, col) not in f.dentro:
                f.cel[_a1(col, lin)] = (None, molde)
                f.dentro.add((lin, col))
    # o cabeçalho é o da FICHA (cabecalho.py, o molde do estudo): a marca, o título e a linha de apoio à esquerda, o
    # nome e o Caminho à direita. Aqui só mudam o título e a linha de apoio; o carimbo de versão fica na FICHA.
    import cabecalho as cab
    f.cel[cab.C_TITULO[0]] = (NOME, f.cel[cab.C_TITULO[0]][1])
    f.cel[cab.C_APOIO[0]] = (f'=DADOS!$F$1&" · {APOIO}"', f.cel[cab.C_APOIO[0]][1])
    # 01/10/2026, pedido do Mizuki com o painel de XP aberto: "o cabeçalho deve acompanhar a parte que foi ocultada".
    # A faixa de tinta e a divisória de baixo dela continuam por cima do painel, até a última coluna da aba.
    meio = C("AD")
    for lin in range(1, cab.ULTIMA_LINHA + 1):
        molde = fcel[_a1(meio, lin)][2]
        for col in range(COLS_FOLHA + 1, PAINEL_FIM + 1):
            f.cel[_a1(col, lin)] = (None, molde)
            f.dentro.add((lin, col))
    imagens = [dict(im) for im in ficha["imagens"] if im["lin"] <= 7]
    alturas = [list(a) for a in ficha["linhas_alt"] if a[0] <= 7]

    # --- o dossiê
    L = _titulo(f, L_DOSSIE, "D", "AT", "DOSSIÊ")
    # 05/10/2026, pedido do Mizuki: "A imagem que for colocada na carteira aparecer no ficha pessoal" (o B35 deixou a
    # ligação para depois). A caixa aponta para a caixa da foto da CARTEIRA. A documentação do Google não diz se a
    # referência mostra a imagem inserida na célula; se não mostrar, o jogador insere a foto aqui também, por cima da
    # conta, e por isso a caixa fica fora da trava (lá embaixo, com as livres). O endereço é o que a CARTEIRA declara
    # (`foto`, do moldura_foto.py), o mesmo que o Codigo.gs lê para ancorar a caixa da paleta.
    foto = next(a for a in layout["abas"] if a["nome"] == "CARTEIRA").get("foto")
    if not foto:
        raise SystemExit("ficha_pessoal: a CARTEIRA não declara a caixa da foto (moldura_foto.py)")
    foto_fp = f.add("foto", "D", L + 1, "O", L + 19, f"={_abs(foto[1], foto[0], 'CARTEIRA!')}", NOTAS["foto"])
    f.add("rot", "D", L + 21, "O", L + 21, "PERSONALIDADE")
    f.add("txt", "D", L + 22, "O", L + 29)
    f.caixa("Q", "Z", L + 1, "NOME", f"=FICHA!{ix.indice(layout)['nome']}", nota=NOTAS["nome"])
    f.caixa("AB", "AG", L + 1, "GRAU", R["patentes"][0][0], nota=NOTAS["grau"])
    f.caixa("AI", "AM", L + 1, "IDADE")
    f.caixa("AO", "AT", L + 1, "ALTURA")
    f.caixa("Q", "W", L + 5, "OLHOS")
    f.caixa("Y", "AE", L + 5, "CABELO")
    f.caixa("AG", "AM", L + 5, "PELE")
    f.caixa("AO", "AT", L + 5, "GÊNERO")
    # 08/10/2026 (B41), a forma B do estudo da revisão: as cicatrizes dividem a linha da aparência, o traço entra em
    # cima da história, e os dois Legados fecham o dossiê, de ponta a ponta. Os Legados são texto livre ("da pra criar
    # legado, ent n precisa fazer lista"), com o tipo num menu, e a FICHA os espelha embaixo das barras.
    f.add("rot", "Q", L + 9, "AG", L + 9, "APARÊNCIA")
    f.add("txt", "Q", L + 10, "AG", L + 11)
    f.add("rot", "AI", L + 9, "AT", L + 9, "CICATRIZES", NOTAS["cicatrizes"])
    assert f.add("txt", "AI", L + 10, "AT", L + 11) == G["cicatrizes"]
    f.add("rot", "Q", L + 13, "AT", L + 13, "TRAÇO · UMA FRASE DA SUA HISTÓRIA", NOTAS["traco"])
    assert f.add("txt", "Q", L + 14, "AT", L + 15) == G["traco"]
    f.add("rot", "Q", L + 17, "AT", L + 17, "HISTÓRIA")
    assert f.add("txt", "Q", L + 18, "AT", L + 23) == G["historia"]
    f.add("rot", "Q", L + 25, "AT", L + 25, "LAÇOS E ANOTAÇÕES")
    f.add("txt", "Q", L + 26, "AT", L + 29)
    for k, ((n1, n2), (t1, t2)) in enumerate(((("D", "P"), ("Q", "W")), (("Y", "AL"), ("AM", "AT")))):
        f.add("rot", n1, L + 31, n2, L + 31, f"LEGADO {k + 1}", NOTAS["legado"])
        f.add("rot", t1, L + 31, t2, L + 31, "TIPO", NOTAS["legado_tipo"])
        assert f.add("cel_esq", n1, L + 32, n2, L + 32) == G["legado_nome"][k]
        assert f.add("cel", t1, L + 32, t2, L + 32) == G["legado_tipo"][k]
        assert f.add("txt", n1, L + 33, t2, L + 35) == G["legado_texto"][k]
    f.menu(" ".join(G["legado_tipo"]), tr["faixa_t"]("legado_tipo"))
    f.menu(G["grau"], tr["faixa_t"]("grau", so=0))

    # --- em uso: as duas mãos e o que está vestido
    L = _titulo(f, L_USO, "D", "AT", "EM USO")
    P, S, V = (_A(G[k]) for k in ("principal", "secundaria", "vestindo"))
    # a nota das duas mãos mora na caixa em que se escolhe, e não no rótulo: pedido dele em 01/10/2026 (B30)
    assert f.caixa("D", "Q", L + 1, "MÃO PRINCIPAL", SOCO) == G["principal"]
    assert f.caixa("S", "AF", L + 1, "MÃO SECUNDÁRIA", MAO_LIVRE) == G["secundaria"]
    f.notas[G["principal"]], f.notas[G["secundaria"]] = NOTAS["principal"], NOTAS["secundaria"]
    f.caixa("AH", "AT", L + 1, "VESTINDO", R["uniformes"][0]["nome"], nota=NOTAS["vestindo"])
    f.menu(G["principal"], tr["faixa_t"]("menu_principal"))
    f.menu(G["secundaria"], tr["faixa_t"]("menu_secundaria"))
    f.menu(G["vestindo"], tr["faixa_t"]("menu_vestindo"))
    soco, duas = H["soco na principal"], H["nas duas mãos"]

    def detalhe(dado, prop, alc, rec, extra=""):
        return (f'{dado}&IF({prop}<>""," · "&{prop},"")&{extra}IF({alc}<>""," · "&{alc},"")&'
                f'IF({rec}<>""," · recarga a cada "&{rec},"")')
    f.add("peq", "D", L + 4, "Q", L + 4,
          f'=IF({soco}=1,{H["dado da principal"]}&IF({H["guardados para a principal"]}=0," · {T_GUARDE_P}",'
          f'" · sem propriedade · o dado sobe com a maestria"),'
          f'IF({H["categoria da principal"]}="","Não está nos equipáveis guardados",' +
          detalhe(H["dado em uso"], H["propriedades da principal"], H["alcance da principal"], H["recarga da principal"],
                  f'IF({duas}=1," · nas duas mãos",IF({H["mão da principal"]}=2," · duas mãos",""))&') + "))")

    def marca_forca(pede, falta, vale=None):
        t = (f'IF({pede}=0,"Sem requisito de Força",IF({falta}=1,"{T_FALTA_FORCA}: "&{H["força"]}&" de "&{pede},'
             f'"Força "&{H["força"]}&" de "&{pede}))')
        return f'=IF({vale}=0,"—",{t})' if vale else "=" + t
    f.add("marca", "D", L + 5, "J", L + 5, f'=IF({H["treino da principal"]}=1,"Treinada","{T_SEM_TREINO}: desvantagem")')
    f.add("marca", "K", L + 5, "Q", L + 5, marca_forca(H["força da principal"], H["falta força na principal"]))
    sv, esc = H["secundária vale"], H["escudo na secundária"]
    f.add("peq", "S", L + 4, "AF", L + 4,
          f'=IF({H["mão da principal"]}=2,"Ocupada: a arma da outra mão é de duas mãos",'
          f'IF({S}="{NAS_DUAS}",IF({duas}=1,"A mesma arma, nas duas mãos","A arma da outra mão não é Versátil"),'
          f'IF({sv}=0,IF({H["guardados para a secundária"]}=0,"{T_GUARDE_S}","Mão livre"),'
          f'IF({H["categoria da secundária"]}="","Não está nos equipáveis guardados",'
          f'IF({esc}=1,"Escudo · "&{H["propriedades da secundária"]},' +
          detalhe(H["dado da secundária"], H["propriedades da secundária"], H["alcance da secundária"],
                  H["recarga da secundária"]) + ")))))")
    f.add("marca", "S", L + 5, "Y", L + 5, marca_forca(H["força da secundária"], H["falta força na secundária"], sv))
    f.add("marca", "Z", L + 5, "AF", L + 5, f'=IF({esc}=1,"Trava Selo de gesto","Sem escudo")', NOTAS["selo"])
    uv = H["uniforme vale"]
    f.add("peq", "AH", L + 4, "AT", L + 4,
          f'=IF({uv}=0,"Sem uniforme: vale a proteção do cobrir-se","Proteção "&{H["proteção do uniforme"]}&" · "&'
          f'IF({H["teto do uniforme"]}&""="—","sem teto de Destreza","teto de Destreza "&{H["teto do uniforme"]}))')
    f.add("marca", "AH", L + 5, "AN", L + 5,
          f'=IF({uv}=0,"—",IF({H["uniforme liberado"]}=1,"Liberado no "&{_A(G["grau"])},"{T_PEDE_GRAU}"&{H["grau mínimo"]}))')
    f.add("marca", "AO", L + 5, "AT", L + 5, marca_forca(H["força do uniforme"], H["falta força no uniforme"], uv))

    # --- o treino em armas: uma caixa de seleção por arma e uma por grupo
    _titulo(f, L_TREINO, "D", "AT", "TREINO EM ARMAS", NOTAS["treino"])
    for cat, (col, lin, larg) in G["grupos"].items():
        f.add("rot", col, lin, col, lin, False)
        f.add("rot", col + 1, lin, col + larg - 1, lin, cat.upper())
    for nome, (col, lin, larg) in G["armas"].items():
        f.add("cel", col, lin, col, lin, False)
        f.add("cel_esq", col + 1, lin, col + larg - 1, lin, nome)
    usadas = {}
    for col, lin, larg in list(G["grupos"].values()) + list(G["armas"].values()):
        usadas.setdefault(col, set()).add(lin)
    for col, larg, _ in COLUNAS_TREINO:                      # a coluna mais curta termina em caixa vazia
        for lin in range(G["treino_ini"], G["treino_fim"] + 1):
            if lin not in usadas[col]:
                f.add("cel", col, lin, col + larg - 1, lin)

    # --- a fileira: carga, ienes, salário, requisito de Força e situação do Traje
    L = L_FILEIRA
    f.add("rot", "D", L, "M", L, "CARGA · LIMITE 5 + FORÇA", NOTAS["carga"])
    f.add("num", "D", L + 1, "H", L + 2, f'={H["carga"]}&" de "&{H["limite de carga"]}&IF({H["carga acima"]}=1,"{T_ACIMA}","")')
    f.add("barra", "I", L + 1, "M", L + 2,
          f'=IFERROR(SPARKLINE(MIN({H["carga"]},{H["limite de carga"]}),{{"charttype","bar";"max",{H["limite de carga"]};'
          f'"color1",IF({H["carga acima"]}=1,"{VERMELHO}",{H[COR_DA_BARRA]})}}),"")')
    f.caixa("O", "U", L, "IENES", R["fundo_inicial"], "iene", NOTAS["ienes"])
    f.caixa("W", "AD", L, "SALÁRIO POR MÊS", f'=IFERROR(VLOOKUP({_A(G["grau"])},{tr["faixa_t"]("grau")},2,FALSE),"—")',
            "num", NOTAS["salario"])
    fal = "+".join(H[k] for k in ("falta força na principal", "falta força na secundária", "falta força no uniforme"))
    f.caixa("AF", "AL", L, "REQUISITO DE FORÇA", f'=IF({fal}=0,"Cumprido","{T_NAO_CUMPRIDO}")', nota=NOTAS["requisito"])
    f.caixa("AN", "AT", L, "SITUAÇÃO DO TRAJE", None, nota=NOTAS["situacao"])
    f.menu(G["situacao"], tr["faixa_t"]("sit"))

    # --- os equipáveis guardados
    L = _titulo(f, L_EQUIP, "D", "AT", "EQUIPÁVEIS GUARDADOS", NOTAS["livre"])
    EQUIP = tr["faixa_t"]("equip")
    notas_col = {"Qtd.": NOTAS["qtd"], "Vol.": NOTAS["vol"], "Grau": NOTAS["grau_ferramenta"], "Estigma": NOTAS["estigma"],
                 "Desgaste": NOTAS["desgaste"]}
    for rot, a, b in COLS_EQUIP:
        f.add("rot", a, L + 1, b, L + 1, rot.upper(), notas_col.get(rot))
    da_dados = {"Categoria": 2, "Mão": 3, "Dado": 4, "Propriedades": 5, "Força": 6}
    esquerda = {"Equipável", "Categoria", "Propriedades", "Estigma"}
    for lin in range(G["equip_ini"], G["equip_fim"] + 1):
        com_menu = lin < G["equip_ini"] + EQUIP_MENU
        for rot, a, b in COLS_EQUIP:
            v = None
            if com_menu and rot in da_dados:
                v = f'=IF($D{lin}="","",IFERROR(VLOOKUP($D{lin},{EQUIP},{da_dados[rot]},FALSE),""))'
            elif com_menu and rot == "Vol.":
                v = f'=IF($D{lin}="","",IFERROR(IF($K{lin}="",1,$K{lin})*VLOOKUP($D{lin},{EQUIP},7,FALSE),""))'
            f.add("cel_esq" if rot in esquerda else "cel", a, lin, b, lin, v)
    for lin in range(G["equip_ini"] + EQUIP_MENU, G["equip_fim"] + 1):
        f.notas[f"D{lin}"] = NOTAS["linha_livre"]
    f.menu(f"D{G['equip_ini']}:D{G['equip_ini'] + EQUIP_MENU - 1}", tr["faixa_t"]("equip", so=0))
    f.menu(f"AI{G['equip_ini']}:AI{G['equip_fim']}", tr["faixa_t"]("grau_ferramenta"))

    # --- os itens guardados
    L = _titulo(f, L_ITENS, "D", "AT", "ITENS GUARDADOS")
    livres = [foto_fp]
    for cols in COLS_ITENS:
        (_, i1, i2), (_, q1, q2), (_, v1, v2) = cols
        f.add("rot", i1, L + 1, i2, L + 1, "ITEM")
        f.add("rot", q1, L + 1, q2, L + 1, "QTD.", NOTAS["qtd"])
        f.add("rot", v1, L + 1, v2, L + 1, "VOL.", NOTAS["vol_item"])
        for lin in range(G["itens_ini"], G["itens_fim"] + 1):
            f.add("cel_esq", i1, lin, i2, lin)
            f.add("cel", q1, lin, q2, lin)
            livres.append(f.add("cel", v1, lin, v2, lin, f'=IF(${i1}{lin}="","",IF(${q1}{lin}="",1,${q1}{lin})*{R["leve"]})'))

    # --- o painel de missões e XP, depois da AU
    L = _titulo(f, L_DOSSIE, B1, B2 + ULT, "MISSÕES E XP")
    _titulo(f, L_DOSSIE, B3, B4 + ULT, "MAIS MISSÕES", NOTAS["extensao"])
    f.add("rot", B1, L + 1, B1 + ULT, L + 1, "XP TOTAL", NOTAS["xp_total"])
    f.add("num", B1, L + 2, B1 + ULT, L + 3, f'={H["xp total"]}')
    f.add("rot", B2, L + 1, B2 + ULT, L + 1, f'=IF({H["nível"]}>=30,"NÍVEL MÁXIMO","FALTA PARA O NÍVEL "&({H["nível"]}+1))', NOTAS["falta"])
    f.add("num", B2, L + 2, B2 + C_XP, L + 3, f'=IF({H["xp do próximo nível"]}&""="","—",MAX(0,{H["xp do próximo nível"]}-{H["xp total"]}))')
    f.add("barra", B2 + C_ADIC, L + 2, B2 + ULT, L + 3,
          f'=IFERROR(SPARKLINE(MAX(0,{H["xp total"]}-{H["xp deste nível"]}),{{"charttype","bar";"max",'
          f'MAX(1,N({H["xp do próximo nível"]})-{H["xp deste nível"]});"color1",{H[COR_DA_BARRA]}}}),"")')
    textos = {"tipos": ", ".join(f"{n} {v}" for n, v in R["tipos"]), "mults": ", ".join(n for n, _ in R["multiplicadores"])}
    TIPO, MULT, DESC = (tr["faixa_t"](k) for k in ("tipo", "mult", "desc"))
    formulas_total = []
    for b in BLOCOS:
        cm, cx, ca, cd, ct = (b + k for k in (C_MISSAO, C_XP, C_ADIC, C_DESC, C_TOTAL))
        f.add("rot", cm, L_MISSAO_CAB, cx - 1, L_MISSAO_CAB, "MISSÃO")
        f.add("rot", cx, L_MISSAO_CAB, ca - 1, L_MISSAO_CAB, "XP", NOTAS["xp"].format(**textos))
        f.add("rot", ca, L_MISSAO_CAB, cd - 1, L_MISSAO_CAB, "ADICIONAL", NOTAS["adicional"].format(**textos))
        f.add("rot", cd, L_MISSAO_CAB, ct - 1, L_MISSAO_CAB, "DESCONTO", NOTAS["desconto"])
        f.add("rot", ct, L_MISSAO_CAB, b + ULT, L_MISSAO_CAB, "TOTAL", NOTAS["total"].format(**textos))
        for lin in range(G["missao_ini"], G["missao_fim"] + 1):
            x, a, d = (f"${ix._letras(c)}{lin}" for c in (cx, ca, cd))
            f.add("cel_esq", cm, lin, cx - 1, lin)
            f.add("cel_esq", cx, lin, ca - 1, lin)
            f.add("cel", ca, lin, cd - 1, lin)
            f.add("cel", cd, lin, ct - 1, lin)
            v = (f'ROUND(VLOOKUP({x},{TIPO},2,FALSE)*IF({a}="",1,VLOOKUP({a},{MULT},2,FALSE))*'
                 f'IF({d}="",1,VLOOKUP({d},{DESC},2,FALSE)),4)')
            # o livro: arredonda para baixo só o XP final; positivo e menor que 1 vira 1
            formulas_total.append(f.add("cel", ct, lin, b + ULT, lin,
                  f'=IF({x}="","",IFERROR(IF({v}>0,MAX(1,FLOOR({v},1)),0),""))'))
        f.menu(f"{ix._letras(cx)}{G['missao_ini']}:{ix._letras(cx)}{G['missao_fim']}", tr["faixa_t"]("tipo", so=0))
        f.menu(f"{ix._letras(ca)}{G['missao_ini']}:{ix._letras(ca)}{G['missao_fim']}", tr["faixa_t"]("mult", so=0))
        f.menu(f"{ix._letras(cd)}{G['missao_ini']}:{ix._letras(cd)}{G['missao_fim']}", tr["faixa_t"]("desc", so=0))
    L = _titulo(f, L_NIVEIS, B1, B2 + ULT, "NÍVEIS", NOTAS["niveis"])
    niveis = sorted(int(n) for n in R["niveis"] if int(n) >= 2)
    acumulado, linhas = 0, []
    for n in niveis:
        custo = str(R["niveis"][str(n)]["xp"])
        linhas.append((n, custo + (" e um feito" if n == 20 else ""), _milhar(acumulado)))
        if custo != "—":
            acumulado += int(custo.replace(".", ""))
    meio = (len(linhas) + 1) // 2
    for b, parte in ((B1, linhas[:meio]), (B2, linhas[meio:])):
        f.add("rot", b, L + 1, b, L + 1, "NÍVEL")
        f.add("rot", b + C_XP, L + 1, b + C_ADIC, L + 1, "PARA SUBIR")
        f.add("rot", b + C_DESC, L + 1, b + ULT, L + 1, "ACUMULADO")
        for i, (n, custo, ac) in enumerate(parte):
            lin = G["niveis_ini"] + i
            f.add("cel", b, lin, b, lin, f'=IF({H["nível"]}={n},"▸ {n}",{n})')
            f.add("cel", b + C_XP, lin, b + C_ADIC, lin, custo)
            f.add("cel", b + C_DESC, lin, b + ULT, lin, ac)

    # --- o resto da folha é fundo, pintado célula a célula: é ele que diz ao script qual é a cor de base
    canvas = f.estilo("canvas")
    for lin in range(1, L_FIM + 1):
        for col in range(1, PAINEL_FIM + 1):
            if (lin, col) not in f.dentro:
                f.cel[_a1(col, lin)] = (None, canvas)

    # --- o que o script precisa além das células: as notas, os grupos, o formato, a cor de aviso e as travas
    marcas = [G[k] for k in ("marca_forca_p", "marca_forca_s", "marca_forca_v")]
    condicional = [
        {"faixas": marcas, "contem": T_FALTA_FORCA, "fundo": VERMELHO, "fonte": BRANCO},
        {"faixas": [G["marca_grau"]], "contem": T_PEDE_GRAU, "fundo": VERMELHO, "fonte": BRANCO},
        {"faixas": [G["requisito"]], "contem": T_NAO_CUMPRIDO, "fundo": VERMELHO, "fonte": BRANCO},
        {"faixas": [G["carga"]], "contem": T_ACIMA, "fundo": VERMELHO, "fonte": BRANCO},
        {"faixas": [G["marca_treino"]], "contem": T_SEM_TREINO, "fonte": AMBAR},
    ]
    # as fórmulas que o jogador não deve apagar sem querer, em faixas (uma trava por célula levaria minutos);
    # o Vol. dos itens fica de fora, porque ele pode ser digitado por cima
    # 07/10/2026: a aba não declara mais faixas travadas. As travas de aviso saíram da ficha (ver LIVRES_DA_TRAVA, no
    # Codigo.gs): a conta em que alguém escreve por cima volta sozinha, em grupo ou não, e só as `livres` ficam.
    return {
        "nome": NOME, "estado": "visible", "linhas": L_FIM, "colunas": PAINEL_FIM,
        # a folha na largura da FICHA; no painel, cada coluna na largura dela (pixel = 8 x largura - 1, a conta do Sheets)
        "colunas_larg": [[1, PAINEL_INI, ficha["colunas_larg"][0][2]]] +
                        [[b + k, b + k, (px + 1) / 8] for b in BLOCOS for k, px in enumerate(PX_BLOCO)] +
                        [[b + len(PX_BLOCO), b + len(PX_BLOCO), ficha["colunas_larg"][0][2]] for b in BLOCOS],
        "linhas_alt": alturas,
        "altura_padrao": ficha.get("altura_padrao"), "grade": False,
        "celulas": [[k, v[0], v[1]] for k, v in f.cel.items()],
        "mescladas": f.mesclas, "menus": f.menus, "condicional": [], "imagens": imagens,
        "notas": f.notas,
        # o painel é um grupo de colunas fechado, e a extensão é outro, dentro dele, também fechado
        "grupos": {"linhas": [[G["treino_ini"], G["treino_fim"], False]],
                   "colunas": [[PAINEL_INI, PAINEL_FIM, True], [EXT_INI, PAINEL_FIM, True]]},
        "condicional_gs": condicional,
        # 07/10/2026: as caixas que nascem com conta e o jogador escreve por cima (a foto e o Volume de cada item). O
        # devolverConta_ do Codigo.gs devolve a conta de todas as outras, em grupo ou não
        "livres": sorted(livres),
    }


def aplica(layout, tr):
    """põe na FICHA e na DADOS o que a limpeza muda. Devolve quantas células mudaram. A aba entra à parte,
    pelo monta.py, depois das correções de borda."""
    n = ix.aplica(layout, tr["celulas"])
    for nome, saem in tr["menus_sai"].items():
        a = ix._aba(layout, nome)
        antes = len(a["menus"])
        a["menus"] = [m for m in a["menus"] if m["onde"] not in saem]
        n += antes - len(a["menus"])
    dados = ix._aba(layout, "DADOS")
    ultima = tr["dados_colunas"][1]
    if dados["colunas"] < ultima:
        dados["colunas"] = ultima
        dados["colunas_larg"] = [[c1, (ultima if c2 == max(x[1] for x in dados["colunas_larg"]) else c2), w]
                                 for c1, c2, w in dados["colunas_larg"]]
    return n
