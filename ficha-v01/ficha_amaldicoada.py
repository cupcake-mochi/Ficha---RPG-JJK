# -*- coding: utf-8 -*-
"""A aba FICHA AMALDIÇOADA: a técnica, o orçamento de espaços, os feitiços montados peça a peça, a Classe 0, as
Liberações Máximas, a Técnica Máxima, a Expansão de Domínio, as Passivas, as aptidões e os pactos. É a limpeza 25.

Não existe planilha viva desta aba. O desenho foi fechado com o Mizuki por estudo, em quatro rodadas, em 01/10/2026
(mockup/ficha-amaldicoada-estudo.html), e a aba nasce inteira aqui, como a FICHA PESSOAL. As decisões dele:
  · feitiço MONTADO, e tudo o que der para calcular, calculado ("a ficha amaldiçoada tem que ser basicamente
    'tudo' que já de pra automatizar e calcular para o jogador");
  · cartas ("Todos gostaram mais da opção de cartas"), TRÊS por fileira, com a página mais larga que a da FICHA
    ("dar mais colunas a pagina", porque a carta de 13 colunas estava "mt amassadinho");
  · descrição e montagem em grupos que fecham; 36 lugares de feitiço em três lotes; Passivas e aptidões em carta;
    três pactos que fecham; o índice de preços com menu de Classe.

A GRADE. A FICHA e a FICHA PESSOAL são desenhadas numa grade de colunas de 28 px, e cada caixa é uma mesclagem.
Esta aba não: cada carta tem cinco colunas na largura do que guardam (112, 140, 112, 56 e 56 px), e as seções de
cima se alinham nas mesmas colunas. São 21 colunas no lugar de 61, e por isso a aba inteira tem umas dez mil células:
é o que faz a troca de tema dela caber num passo do gatilho simples, e o construir() fazer um terço das mesclagens.

AS CONTAS moram numa aba oculta própria, a DADOS_AM (como a INVOCAÇÃO tinha a DADOS_INV): as tabelas das peças, os
preços por Classe e uma linha de conta por feitiço. A carta só mostra o resultado. Nenhuma fórmula usa LET nem
LAMBDA: a regressão recalcula a ficha no LibreOffice, que não tem as duas.

DE ONDE SAI CADA NÚMERO. As Formas, as Melhorias, as condições, as Restrições, as Famílias e a progressão saem do
catalogo-projeto-m.json. As Passivas, as aptidões, as escadas de alcance, a Classe 0, a Liberação, a Técnica Máxima,
o Domínio e os pactos saem do ficha-v01/tecnica-do-livro.json, que o extrair_tecnica.py lê dos capítulos do livro:
o catálogo ainda não os tem, e levá-los para lá é decisão do Mizuki.

O QUE ESTA ABA NÃO FAZ: não toca a seção 8 da FICHA (ele ainda não decidiu se ela vira espelho ou sai), e não
desenha as rotas sem Fundamento (Técnica Marcial, Sem Técnica e Restrição Celestial).
"""
import json, math, os, re

import indice_ficha as ix
import ficha_pessoal as fp

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOME = "FICHA AMALDIÇOADA"
AM = f"'{NOME}'!"
DADOS_AM = "DADOS_AM"
DA = f"{DADOS_AM}!"
APOIO = "técnica, feitiços e aptidões"      # a linha de apoio do cabeçalho

# ---------------------------------------------------------------------------------------------
# A grade: A, B e C como na FICHA (a lombada e o respiro), três cartas de cinco colunas com uma
# coluna de respiro entre elas, e a margem da direita.
# ---------------------------------------------------------------------------------------------
PX_FINA = 28
PX_CARTA = (112, 140, 112, 56, 56)           # a, b, c, d, e
CARTAS = (4, 10, 16)                         # a primeira coluna de cada carta: D, J e P
COLS = CARTAS[-1] + len(PX_CARTA)            # a margem da direita é a coluna U
PX_COLUNAS = [PX_FINA] * 3 + list(PX_CARTA) + [PX_FINA] + list(PX_CARTA) + [PX_FINA] + list(PX_CARTA) + [PX_FINA]
C = ix._col
L = ix._letras
C1, CN = C("D"), C("T")                      # a primeira e a última coluna de conteúdo

# Quantos lugares a aba tem. O teto de feitiços do livro: 24 espaços no nível 30, mais um feitiço por escolha de
# Leque (sete marcos), mais um espaço por pacto permanente (metade da Essência; a tabela do livro vai até 3).
N_FEITICOS, POR_LOTE, N_LIB = 36, 12, 3
PAGAS, DO_LEQUE = 5, 7
N_APT, APT_LOTE = 12, 6
N_PACTOS, N_ZERO, N_MEL, N_RES = 3, 5, 4, 2
FX = 2                                       # o título de seção ocupa duas linhas, como na FICHA PESSOAL
RESPIRO = 2                                  # linhas de fundo embaixo do último pacto, para ele não colar no fim da aba

# as linhas de uma carta, contadas da primeira dela
F_TIT, F_ROT, F_TXT, F_TXT_FIM, F_N1, F_N2, F_MEL, F_RES, F_CONTA, F_AMP, F_AV = 0, 1, 2, 6, 7, 8, 9, 13, 15, 16, 18
ALT_F = 20                                   # a carta de feitiço; a fileira tem uma linha vazia a mais
ALT_P = 7                                    # a de Passiva: o menu, e o grupo com "o que faz" e o texto do jogador
TXT_APT = 12                                 # linhas da regra da aptidão: a mais comprida do livro tem 1.300 letras
ALT_A = 7 + TXT_APT                          # a de aptidão: o menu, o requisito em duas linhas, e o grupo

SECOES = [("tecnica", "TÉCNICA", "Técnica"), ("orcamento", "ORÇAMENTO", "Orçamento"), ("feiticos", "FEITIÇOS", "Feitiços"),
          ("zero", "CLASSE 0", "Classe 0"), ("lib", "LIBERAÇÃO MÁXIMA", "Liberação"), ("tm", "TÉCNICA MÁXIMA", "T. Máxima"),
          ("dominio", "EXPANSÃO DE DOMÍNIO", "Domínio"), ("passivas", "PASSIVAS", "Passivas"),
          ("aptidoes", "APTIDÕES E REFINO", "Aptidões"), ("pactos", "PACTOS", "Pactos")]
# as seções que nascem fechadas: o nível 2 da ficha nova ainda não chegou em nenhuma das três
NASCE_FECHADA = ("lib", "tm", "dominio")

# ---------------------------------------------------------------------------------------------
# As cores e as fontes: as da FICHA PESSOAL, pelos papéis da paleta de fábrica. A troca de paleta acha
# o papel de cada célula pela cor que ela tem, então nenhuma cor nova pode entrar aqui.
# ---------------------------------------------------------------------------------------------
TINTA, FUNDO, PAINEL, ALTO, PAPEL, ACENTO = fp.TINTA, fp.FUNDO, fp.PAINEL, fp.ALTO, fp.PAPEL, fp.ACENTO
OSSO, TEXTO, FRACO = fp.OSSO, fp.TEXTO, fp.FRACO
_CAIXA = fp._CAIXA
ESTILOS = {
    "canvas":    [None, FUNDO, None, None, None],
    "faixa":     [["Oswald", 14.0, OSSO, False, False], ACENTO, _CAIXA, ["left", "center", False, 0], None],
    "rot":       [["Oswald", 8.0, OSSO, False, False], ALTO, _CAIXA, ["center", "center", False, 0], None],
    "val":       [["Roboto", 11.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "num":       [["Oswald", 16.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "cel":       [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "cel_esq":   [["Roboto", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
    "peq":       [["Roboto", 9.0, FRACO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "peq_esq":   [["Roboto", 9.0, FRACO, False, False], PAINEL, _CAIXA, ["left", "center", False, 0], None],
    "peq_txt":   [["Roboto", 9.0, FRACO, False, False], PAINEL, _CAIXA, ["left", "center", True, 0], None],
    "txt":       [["Roboto", 10.0, TEXTO, False, False], PAPEL, _CAIXA, ["left", "top", True, 0], None],
    "txt_peq":   [["Roboto", 9.0, TEXTO, False, False], PAPEL, _CAIXA, ["left", "top", True, 0], None],
    "conta":     [["Roboto", 9.0, TEXTO, False, False], PAPEL, _CAIXA, ["left", "center", True, 0], None],
    # O nome de cada carta (e a Classe, na de feitiço) fica na cor de título: pedido do Mizuki em 01/10/2026, ao usar a aba
    # no Sheets. Com as caixas da carta coladas uma na outra e as três tintas do painel parecidas, a carta não tinha
    # começo. O estado continua escuro, porque a cor de aviso dele (âmbar na letra) não se lê em cima do acento.
    "nome":      [["Castoro", 11.0, OSSO, False, False], ACENTO, _CAIXA, ["left", "center", False, 0], None],
    "nome_menu": [["Roboto", 10.0, OSSO, False, False], ACENTO, _CAIXA, ["left", "center", False, 0], None],
    "classe_carta": [["Oswald", 10.0, OSSO, False, False], ACENTO, _CAIXA, ["center", "center", False, 0], '"Classe "0'],
    "estado":    [["Roboto", 9.0, OSSO, False, False], ALTO, _CAIXA, ["center", "center", False, 0], None],
    "classe":    [["Oswald", 10.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], '"Classe "0'],
    "dano":      [["Oswald", 11.0, OSSO, False, False], PAINEL, _CAIXA, ["center", "center", False, 0], None],
    "lote":      [["Oswald", 9.0, OSSO, False, False], PAPEL, _CAIXA, ["left", "center", False, 0], None],
    "salto":     [["Oswald", 8.0, OSSO, False, False], PAPEL, _CAIXA, ["center", "center", False, 0], None],
    "dica":      [["Roboto", 9.0, FRACO, False, False], FUNDO, None, ["left", "center", False, 0], None],
}

# os textos que a ficha escreve e que a cor de aviso procura: tudo o que está fora da regra abre com o primeiro, e
# o aviso que não é erro abre com o segundo. Uma regra de cor só, na aba inteira, pinta os dois.
T_ERRO, T_AVISO = "⚠", "! "
VERMELHO, BRANCO, AMBAR = fp.VERMELHO, fp.BRANCO, fp.AMBAR
NA_REGRA = "Na regra"
DENTRO = "Dentro das regras que a ficha confere"
SEM_NOME = "Dê um nome"
FORMA_INICIAL = "Projétil"
NEUTRA, LIVRE, FECHADA = "Neutra", "Livre", "Fechada"
PERMANENTE, ESPACO_DE_PACTO = "Permanente", "Um espaço de feitiço"
PROPRIA_P, PROPRIA_A, PROPRIA_B = "Passiva Própria", "Aptidão Própria", "Bênção Própria"

# As quatro rotas de criação (02/10/2026): a aba muda conforme a Origem escolhida na FICHA, para o menu rápido da seção 8
# ler a mesma coisa em qualquer ficha. O desenho fechado com o Mizuki foi a forma A do estudo mockup/rotas-estudo.html:
# uma linha da rota na Técnica, sem script; a forma C (o script esconde o que a rota não usa) foi testada no Sheets e
# saiu, porque abrir o grupo em volta revela a linha escondida. 1 é o Fundamento (as cinco Origens principais e a
# Restrição Celestial pelo corpo), 2 o Sem Técnica, 3 a Técnica Marcial com energia (Corpo Amaldiçoado) e 4 a Técnica
# Marcial sem energia (Restrição Celestial pelo ramo sem energia).
NOMES_DAS_ROTAS = ("Fundamento", "Sem Técnica", "Técnica Marcial com energia", "Técnica Marcial sem energia")
# o Equipamento da Técnica Marcial: os três grupos de arma, ou a ferramenta, que declara na criação se o golpe simples
# usa ela (o livro: "Coisa que dá para usar para atacar" e "Coisa que você só carrega")
EQUIPAMENTO = ("Três grupos de arma", "Ferramenta de atacar", "Ferramenta de carregar")
N_GRUPOS = 3

# As peças que mudam a conta, pelo nome que têm no catálogo. Cada uma é conferida contra ele em regras(): peça que
# mudar de nome no livro para a montagem, em vez de deixar uma fórmula procurando um nome que não existe mais.
PECAS_CITADAS = ("Longe", "Muito Longe", "Maior", "Muito Maior", "Mais Um", "Rajada", "Salto", "Queima", "Rápido",
                 "Reação", "Certeiro", "Inescapável", "Toca a Alma")
RESTRICOES_CITADAS = ("Corpo a Corpo", "Atrasar", "Carregar", "Tudo ou Nada")
# as quatro Restrições de frequência (manual p.124; a mesma lista do conferir_feitico.py, que o validador compara)
FREQUENCIA = ("Uma Vez", "Condicional", "Aquecer", "Dívida")
# as duas peças que SOMAM metade dos dados ao total (o Mais Um e a Rajada dividem, e a soma das partes não cresce):
# a conta do conferir_feitico.py, do manual p.135
SOMAM_METADE = ("Salto", "Queima")
# como os dados de cada Forma aparecem: 0 dano, 1 cura, 2 vida temporária (3 por ponto), 3 sem dano
TIPO_DE_DANO = {"Cura": 1, "Onda": 1, "Apoio": 2, "Efeito": 3}
PESO = {"Leve": 1, "Media": 2, "Média": 2, "Pesada": 3}
NOME_DO_PESO = ("Leve", "Média", "Pesada")
# O alcance de cada Forma: (antes, escada, o que sobe o degrau, depois), duas vezes. É a tabela `Formas` do livro
# lida como estrutura; os números saem da `Base por Classe` e das `Escadas`. No Cone e na Linha o comprimento sobe
# com as peças de Alcance e com as de Área (a Técnica Máxima de exemplo leva a Linha de 18 m a 60 m com o Muito Longe).
ALCANCE = {
    "Projétil": (("", "alcance", "longe", ", um alvo"), None),
    "Toque":    (("1,5 m, um alvo", None, None, ""), None),
    "Explosão": (("raio ", "raio", "maior", ""), (", a ", "alcance", "longe", "")),
    "Aura":     (("raio ", "raio", "maior", ", em você"), None),
    "Cone":     (("cone de ", "comprimento", "ambos", ""), None),
    "Linha":    (("linha de ", "comprimento", "ambos", " por 1,5 m"), None),
    "Cura":     (("um aliado a ", "alcance", "longe", ""), None),
    "Apoio":    (("um aliado a ", "alcance", "longe", ""), None),
    "Onda":     (("raio ", "raio", "maior", ", em você"), None),
    "Efeito":   (("fora de combate", None, None, ""), None),
}
GRAU = {None: 0, "longe": 1, "maior": 2, "ambos": 3}
MAIS_ALVOS = ("Projétil", "Toque")           # as Formas de um alvo, onde o Mais Um e a Rajada aparecem no alcance
GRAUS_NA_TABELA = 6                          # de 0 a 5 degraus: dois Longe e um Muito Longe já passam do topo


def _a1(col, lin):
    return f"{L(col)}{lin}"


def _abs(col, lin, aba=""):
    return f"{aba}${L(col)}${lin}"


def _faixa(c1, l1, c2, l2, aba=""):
    return f"{aba}${L(c1)}${l1}:${L(c2)}${l2}"


def _A(coord, aba=""):
    lin, col = ix._lc(coord)
    return _abs(col, lin, aba)


# a fórmula que só aponta para uma célula de outra aba: é a única que o onEdit sabe devolver (ver `com_conta`, em aba())
REFERENCIA_PURA = re.compile(r"=(?:'[^']+'|[A-Z_]+)!\$?[A-Z]+\$?\d+")


def _ini(texto):
    """a letra inicial maiúscula: toda caixa da aba abre assim (pedido do Mizuki em 01/10/2026). O que vem do livro em
    minúscula (o degrau do Domínio, a forma do pacto, o que o refino escala) passa por aqui antes de ir para a tabela."""
    return texto[:1].upper() + texto[1:] if isinstance(texto, str) else texto


def _metros(texto):
    """o número de um degrau: '4,5 m' é 4.5, e o degrau sem número ('o que você enxergar') é o infinito"""
    m = re.search(r"\d+(?:,\d+)?", texto)
    return float(m.group(0).replace(",", ".")) if m else math.inf


def sobe(escada, base, degraus):
    """o degrau da escada a `degraus` da base. A base que não é degrau (o Cone de 3 m da Classe 0) fica logo abaixo
    do primeiro degrau maior que ela. Passou do topo, para no topo."""
    if base in escada:
        i = escada.index(base)
    elif not degraus:
        return base
    else:
        i = next(k for k, d in enumerate(escada) if _metros(d) >= _metros(base)) - 1
    return escada[min(len(escada) - 1, i + degraus)]


def preco(peso, classe, livre=False):
    """o preço da peça de peso 1 (Leve), 2 (Média) ou 3 (Pesada): metade da Classe, a Classe, uma vez e meia, para
    cima. Família Livre tira metade da Classe, com mínimo de 1. É a conta do conferir_feitico.py."""
    p = math.ceil(classe * (0.5, 1, 1.5)[peso - 1])
    return max(1, p - math.ceil(classe / 2)) if livre else p


def regras(CAT=None, TEC=None):
    """tudo o que a aba lê do catálogo e do tecnica-do-livro.json, já na forma em que ela usa"""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    if TEC is None:
        TEC = json.load(open(os.path.join(RAIZ, "ficha-v01", "tecnica-do-livro.json"), encoding="utf-8"))
    DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))
    falta = [n for n in PECAS_CITADAS if n not in CAT["melhorias"]] + [n for n in RESTRICOES_CITADAS + FREQUENCIA if n not in CAT["restricoes"]]
    falta += [n for n in list(TIPO_DE_DANO) + list(ALCANCE) + [FORMA_INICIAL] if n not in CAT["formas"]]
    falta += [n for n in CAT["formas"] if n not in ALCANCE]
    if falta:
        raise SystemExit(f"ficha_amaldicoada: o catalogo nao tem (ou tem a mais) {falta}: a conta da aba cita essas pecas pelo nome")

    familias = list(CAT["familias"])
    # as peças do menu de Melhoria: as do catálogo, com cada condição no lugar da Melhoria `Condição` (ela custa o
    # nível da condição) e o Efeito Próprio nos três pesos (quem decide o peso é o mestre)
    pecas = []
    for n, m in CAT["melhorias"].items():
        if n == "Condição":
            pecas += [{"nome": c, "familia": m["familia"], "peso": PESO[p]} for c, p in CAT["condicoes"].items()]
        elif n == "Efeito Próprio":
            pecas += [{"nome": f"{n} ({p})", "familia": None, "peso": i + 1} for i, p in enumerate(NOME_DO_PESO)]
        else:
            pecas.append({"nome": n, "familia": m["familia"], "peso": PESO[m["peso"]]})
    nomes = [p["nome"] for p in pecas]
    if len(set(nomes)) != len(nomes):
        raise SystemExit("ficha_amaldicoada: duas pecas com o mesmo nome no menu de Melhoria")
    # as Restrições do menu: a que devolve "Leve ou Média" entra duas vezes, uma em cada nível
    restricoes = []
    for n, r in CAT["restricoes"].items():
        niveis = r["devolve"].split(" ou ")
        for nv in niveis:
            restricoes.append({"rotulo": n if len(niveis) == 1 else f"{n} ({NOME_DO_PESO[PESO[nv] - 1]})", "nome": n,
                               "devolve": PESO[nv], "frequencia": int(n in FREQUENCIA)})
    do_livro = {f["nome"]: f for f in TEC["formas"]}
    formas = []
    for n, f in CAT["formas"].items():
        res = do_livro[n]["resolve"]
        formas.append({"nome": n, "familia": f["familia"], "peso": PESO[f["custa"]] if f["custa"] else 0,
                       "embutida": int("embutido" in f), "tipo": TIPO_DE_DANO.get(n, 0),
                       "resolve": "Acerto" if res.startswith("Rolagem") else "TR, metade" if res.startswith("Teste") else "Automático",
                       "tr": int(res.startswith("Teste")),
                       "grau1": GRAU[ALCANCE[n][0][2]], "grau2": GRAU[ALCANCE[n][1][2]] if ALCANCE[n][1] else 0,
                       "alvos": int(n in MAIS_ALVOS), "na_zero": int(TEC["base_por_classe"].get(n, {"classe_0": ""})["classe_0"] != "—")})
    # o alcance de cada Forma em cada faixa de Classe (0, 1 a 5, 6 e 7), degrau a degrau
    esc, base = TEC["escadas"], TEC["base_por_classe"]
    if "raio 3 m" not in do_livro["Onda"]["o_que_e"] or esc["raio"][0] != "3 m":
        raise SystemExit("ficha_amaldicoada: a Onda do livro nao e mais uma esfera de raio 3 m")

    def a_base(forma, escada, faixa):
        if forma == "Onda":                  # a `Base por Classe` não traz o raio dela; a tabela `Formas` traz
            return esc["raio"][0]
        t = base[forma][faixa]
        if t == "—":
            return None
        if escada == "raio":
            return re.search(r"raio (\d+(?:,\d+)? m)", t).group(1)
        if "raio" in t:                      # "raio 3 m, a 18 m": o alcance é o que vem depois da vírgula
            return re.search(r", a (\d+(?:,\d+)? m)", t).group(1)
        return re.match(r"(\d+(?:,\d+)?)", t).group(1) + " m"       # "18 m" e "18 × 1,5 m"
    alcance = []
    for f in formas:
        for faixa in ("classe_0", "classes_1_a_5", "classes_6_e_7"):
            partes = []
            for parte in ALCANCE[f["nome"]]:
                if parte is None:
                    partes.append([""] * GRAUS_NA_TABELA)
                    continue
                antes, escada, _, depois = parte
                if escada is None:
                    partes.append([antes + depois] * GRAUS_NA_TABELA)
                    continue
                b = a_base(f["nome"], escada, faixa)
                partes.append(["—" if b is None else antes + sobe(esc[escada], b, g) + depois for g in range(GRAUS_NA_TABELA)])
            alcance.append([f"{f['nome']} · {faixa.replace('_', ' ')}"] + [_ini(x) for x in partes[0]] + partes[1])
    prog = CAT["progressao"]
    limiares = lambda chave: [int(x) for x in re.search(r"\(([\d,]+)\)", prog["formulas"][chave]).group(1).split(",")]
    # o teto de feitiços do livro tem de caber nos lugares da aba
    teto = 2 + CAT["_meta"]["nivel_maximo"] // 2 + 2 * len(prog["marcos"]) + N_PACTOS
    if teto > N_FEITICOS or PAGAS != TEC["passivas_pagas"]["cinco"] or DO_LEQUE != len(prog["marcos"]) or N_LIB != len(TEC["liberacao"]["niveis"]):
        raise SystemExit(f"ficha_amaldicoada: os lugares da aba nao cobrem o teto do livro ({teto} feiticos)")
    if N_ZERO != max(TEC["classe_0"]["quantos"]) or N_APT < 2 * len(prog["marcos"]) - 3:
        raise SystemExit("ficha_amaldicoada: os lugares de Classe 0 ou de aptidao nao cobrem o teto do livro")
    cp = {int(l["classe_passiva"]): l["nivel"] for l in TEC["classe_passiva"] if l["classe_passiva"].isdigit()}
    ROT = TEC["rotas"]
    # As Passivas do menu, com a rota de cada uma (02/10/2026, resposta "B" do Mizuki): o Fundamento lista as do capítulo
    # dele; a Técnica Marcial, só as dela e a Passiva Própria (uma do Fundamento entra como Própria, com o mestre); o Sem
    # Técnica, as duas listas, porque o livro diz que elas "servem todos". A Livre da Técnica Marcial (o Calo) não entra:
    # Passiva Livre mora na caixa da Técnica.
    passivas = []
    marciais = {p["nome"]: p for p in ROT["passivas_marciais"]}
    for p in TEC["passivas"]:
        if p["nome"] == "Regra Própria":
            continue                          # tem caixa própria, na seção da técnica
        if p["nome"] == PROPRIA_P:
            passivas += [{"nome": f"{PROPRIA_P} (CP {k})", "cp": k, "faz": p["faz"] + " Escreva a sua na caixa de baixo.",
                          "fund": 1, "marc": 1} for k in sorted(cp)]
        else:
            passivas.append({"nome": p["nome"], "cp": int(p["classe_passiva"]), "faz": p["faz"], "fund": 1, "marc": int(p["nome"] in marciais)})
    for p in ROT["passivas_marciais"]:
        if p["classe_passiva"].isdigit() and p["nome"] not in [x["nome"] for x in passivas]:
            passivas.append({"nome": p["nome"], "cp": int(p["classe_passiva"]), "faz": p["faz"], "fund": 0, "marc": 1})
    # As aptidões e as Bênçãos numa tabela só: a Restrição Celestial sem energia lê as Bênçãos, as outras rotas as
    # aptidões, e o Corpo Amaldiçoado não compra a Extensão de Domínio
    aptidoes = []
    for lista, propria, bencao, gratis in ((TEC["aptidoes"], PROPRIA_A, 0, TEC["aptidoes_de_graca"]),
                                           (ROT["bencaos"], PROPRIA_B, 1, ROT["bencaos_de_graca"])):
        for a in lista:
            if a["nome"] == propria:
                aptidoes += [{"nome": f"{propria} (CP {k})", "requisito": a["requisito"], "cp": k, "escala": a["escala"],
                              "faz": a["faz"] + " Escreva a sua na caixa de baixo.", "gratis": 0, "bencao": bencao, "extensao": 0}
                             for k in (int(x) for x in re.findall(r"\d", a["classe_passiva"]))]
            else:
                aptidoes.append({"nome": a["nome"], "requisito": a["requisito"],
                                 "cp": int(a["classe_passiva"]) if a["classe_passiva"].isdigit() else a["classe_passiva"], "escala": a["escala"],
                                 "faz": a["faz"], "gratis": int(a["nome"] in gratis), "bencao": bencao,
                                 "extensao": int(a["nome"] == "Extensão de Domínio")})
    if len({a["nome"] for a in aptidoes}) != len(aptidoes) or not any(a["extensao"] for a in aptidoes):
        raise SystemExit("ficha_amaldicoada: uma aptidao e uma Bencao com o mesmo nome, ou a Extensao de Dominio sumiu do livro")
    # os nomes de cada rota, que a aba escreve por fórmula; os do Sem Técnica e os da Técnica Marcial são os do livro
    st, tm_ = ROT["nomes"]["Sem Técnica"], ROT["nomes"]["Técnica Marcial"]
    ben = ROT["bencaos_de_graca"]
    rotulos = {
        "feitiço": ["Feitiço", st["feitico"], tm_["feitico"], tm_["feitico"]],
        "feitiços": ["Feitiços", st["feitico"] + "s", tm_["feitico"] + "s", tm_["feitico"] + "s"],
        "liberação": ["Liberação Máxima", st["liberacao"], tm_["liberacao"], tm_["liberacao"]],
        "técnica máxima": ["Técnica Máxima", st["tecnica_maxima"], tm_["tecnica_maxima"], tm_["tecnica_maxima"]],
        "aptidões": ["Aptidões", "Aptidões", "Aptidões", "Bênçãos"],
        "escala": ["Refino", "Refino", "Refino", "Lapidação"],
        "o que escala": ["O refino escala", "O refino escala", "O refino escala", "A Lapidação escala"],
        "graça 1": [TEC["aptidoes_de_graca"][0]] * 3 + [ben[0]],
        "graça 2": [TEC["aptidoes_de_graca"][1]] * 3 + [ben[1]],
        "reação": ["Reação de Cobrir-se"] * 3 + ["Reação da Defesa"],
        "selo": ["Selo", "Selo", "Selo · ter o equipamento em uso", "Selo · ter o equipamento em uso"],
        "peça da rota": ["—", "Semente", "Equipamento", "Equipamento"],
        "o que ela dá": ["—", "O que a semente dá", "Golpe simples", "Golpe simples"],
        "grupo": ["—", "—", "Grupo", "Grupo"],
        "estímulo": ["—", "—", "—", ben[1]],
    }
    lim = {}
    for faixa, mel, _ in TEC["melhorias_por_classe"]:
        m = re.match(r"(\d)(?: e (\d)| em diante)?", faixa)
        for c in range(int(m.group(1)), (int(m.group(2)) if m.group(2) else 7 if "diante" in faixa else int(m.group(1))) + 1):
            lim[c] = int(mel)
    classes = [{"classe": c, "precos": [preco(p, c) for p in (1, 2, 3)] + [preco(p, c, True) for p in (1, 2, 3)], "limite": lim[c]}
               for c in range(1, len(limiares("classe")) + 1)]
    for c, livro in zip(classes, TEC["numeros_da_montagem"]):      # a conta daqui contra a tabela impressa
        if c["precos"][:3] != [livro["leve"], livro["media"], livro["pesada"]]:
            raise SystemExit(f"ficha_amaldicoada: o preco da Classe {c['classe']} nao bate com a tabela Numeros da montagem")
    dom = TEC["dominio"]
    return {
        "familias": familias, "pecas": pecas, "restricoes": restricoes, "formas": formas, "alcance": alcance,
        "pares": [(p["a"], p["b"]) for p in DEC["A3_incompatibilidades"]["pares"]],
        "classes": classes, "passivas": passivas, "aptidoes": aptidoes, "cp": cp, "rotulos": rotulos,
        "sementes": [_ini(x) for x in ROT["sementes"]], "grupos": ROT["grupos_de_arma"],
        "zero": TEC["classe_0"], "liberacao": TEC["liberacao"], "tm": TEC["tecnica_maxima"], "dominio": dom,
        "pactos": TEC["pactos"], "versao_do_livro": TEC["_meta"]["versao_do_livro"],
        "notas_familia": CAT["familias"],
    }


# ---------------------------------------------------------------------------------------------
# Onde cada caixa mora. Uma função só, lida pela aba, pelas contas da DADOS_AM, pela regressão e pelo desenhador.
# ---------------------------------------------------------------------------------------------
def _fileiras(n, por=3):
    """[(posição na fileira, fileira)] dos n lugares"""
    return [(i % por, i // por) for i in range(n)]


def geometria():
    g = {"saltos": 7, "sec": {}, "fim": {}}
    lin = 9

    def abre(nome):
        g["sec"][nome] = lin
        return lin + FX - 1                  # a última linha do título: o resto da seção conta dela

    def fecha(nome, ultima):
        g["fim"][nome] = ultima
        return ultima + 2                    # uma linha vazia entre a seção e o título da próxima

    # --- a técnica
    t = abre("tecnica")
    # a linha da rota (02/10/2026): o rótulo e o menu da peça da rota (a semente, ou o equipamento), e os três grupos de
    # arma com o atributo, a conjuração e a CD de cada um. Ela existe em toda ficha, e os rótulos dizem o que vale na rota.
    R_ = 6                                   # as cinco linhas da rota e a linha vazia embaixo
    g.update({"tec_caixas": t + 1, "rota_lin": t + 5, "regra": t + 5 + R_, "descricao": t + 9 + R_, "regra_propria": t + 16 + R_,
              "familias": t + 20 + R_})
    g.update({"nome_tecnica": f"D{t + 2}", "tipo_dano": f"J{t + 2}", "atributo": f"L{t + 2}", "conjuracao": f"P{t + 2}",
              "cd": f"R{t + 2}", "cp_regra": f"P{t + 17 + R_}", "espacos_regra": f"R{t + 17 + R_}", "resumo_familias": f"Q{t + 21 + R_}",
              "rota_nome": f"D{t + 6}", "rota_menu": f"J{t + 6}", "rota_extra": f"P{t + 6}",
              "grupos_menu": [f"{c}{t + 8}" for c in ("D", "J", "P")], "grupos_conta": [f"{c}{t + 9}" for c in ("D", "J", "P")]})
    # as nove Famílias: uma caixa por coluna de 112 ou 140 px, e as duas de 56 juntas
    g["cols_fam"] = [("D", "D"), ("E", "E"), ("F", "F"), ("G", "H"), ("J", "J"), ("K", "K"), ("L", "L"), ("M", "N"), ("P", "P")]
    lin = fecha("tecnica", t + 21 + R_)
    # --- o orçamento e o índice de preços
    t = abre("orcamento")
    g.update({"orc_caixas": t + 1, "indice": t + 5, "classe_do_indice": f"D{t + 6}"})
    g["cols_orc"] = [("D", "E"), ("F", "H"), ("J", "K"), ("L", "N"), ("P", "P"), ("Q", "Q"), ("R", "T")]
    g["cols_indice"] = [("E", "E"), ("F", "F"), ("G", "H"), ("J", "J"), ("K", "K"), ("L", "L"), ("M", "N"), ("P", "T")]
    lin = fecha("orcamento", t + 6)
    # --- os feitiços: três lotes de 12, quatro fileiras de três cartas cada
    t = abre("feiticos")
    g["feiticos"], g["lotes_feitico"] = [], []
    lin = t + 2
    por_lote = POR_LOTE // 3
    for lote in range(N_FEITICOS // POR_LOTE):
        if lote:
            g["lotes_feitico"].append({"faixa": lin, "ini": lin + 1, "de": lote * POR_LOTE + 1, "ate": (lote + 1) * POR_LOTE})
            lin += 2
        for fileira in range(por_lote):
            for k in range(3):
                g["feiticos"].append((lin, CARTAS[k]))
            lin += ALT_F + 1
        if lote:
            g["lotes_feitico"][-1]["fim"] = lin - 2
    lin = fecha("feiticos", lin - 2)
    # --- a Classe 0
    t = abre("zero")
    g.update({"zero_cab": t + 1, "zero_ini": t + 2, "zero_fim": t + 1 + N_ZERO})
    g["cols_zero"] = {"nome": ("D", "E"), "forma": ("F", "H"), "mel": ("J", "K"), "res": ("L", "N"), "dano": ("P", "Q"), "alcance": ("R", "T")}
    lin = fecha("zero", t + 1 + N_ZERO)
    # --- a Liberação Máxima: uma fileira de três
    t = abre("lib")
    g["libs"] = [(t + 2, CARTAS[k]) for k in range(N_LIB)]
    lin = fecha("lib", t + 2 + ALT_F - 1)
    # --- a Técnica Máxima
    t = abre("tm")
    g.update({"tm_caixas": t + 1, "tm_mel": t + 5, "tm_como": t + 7,
              "tm_nome": f"D{t + 2}", "tm_forma": f"J{t + 2}", "tm_dano": f"L{t + 2}", "tm_pe": f"P{t + 2}", "tm_montagem": f"R{t + 2}"})
    g["cols_tm_mel"] = [("J", "K"), ("L", "N"), ("P", "Q"), ("R", "T")]
    lin = fecha("tm", t + 11)
    # --- a Expansão de Domínio
    t = abre("dominio")
    g.update({"dom_caixas": t + 1, "dom_tabela": t + 5, "dom_textos": t + 10, "dom_como": t + 15,
              "degrau": f"D{t + 2}", "dom_custa": f"F{t + 2}", "dom_requisito": f"J{t + 2}", "dom_refino": f"P{t + 2}",
              "dom_corrida": f"R{t + 2}", "dom_nome": f"P{t + 6}"})
    g["cols_dom"] = [("D", "E"), ("F", "F"), ("G", "H"), ("J", "J"), ("K", "K"), ("L", "L"), ("M", "N")]
    lin = fecha("dominio", t + 19)
    # --- as Passivas: cinco pagas, e sete do Leque num lote que fecha
    t = abre("passivas")
    g["passivas"], lin = [], t + 2
    for k, f in _fileiras(PAGAS):
        g["passivas"].append((lin + f * (ALT_P + 1), CARTAS[k]))
    lin += ((PAGAS + 2) // 3) * (ALT_P + 1)
    g["lote_leque"] = {"faixa": lin, "ini": lin + 1}
    lin += 2
    for k, f in _fileiras(DO_LEQUE):
        g["passivas"].append((lin + f * (ALT_P + 1), CARTAS[k]))
    lin += ((DO_LEQUE + 2) // 3) * (ALT_P + 1)
    g["lote_leque"]["fim"] = lin - 2
    lin = fecha("passivas", lin - 2)
    # --- as aptidões: seis à vista e seis num lote
    t = abre("aptidoes")
    # a linha do Estímulo Muscular (02/10/2026): a perícia e o Teste de Resistência que a Bênção de graça da Restrição
    # Celestial sem energia escolhe na criação, e os usos por cena
    g.update({"apt_caixas": t + 1, "apt_refino": f"D{t + 2}", "apt_compradas": f"F{t + 2}", "estimulo": t + 5,
              "estimulo_pericia": f"D{t + 6}", "estimulo_teste": f"J{t + 6}", "estimulo_usos": f"P{t + 6}"})
    g["cols_apt"] = [("D", "E"), ("F", "H"), ("J", "K"), ("L", "N"), ("P", "T")]
    g["aptidoes"], lin = [], t + 8
    for k, f in _fileiras(APT_LOTE):
        g["aptidoes"].append((lin + f * (ALT_A + 1), CARTAS[k]))
    lin += (APT_LOTE // 3) * (ALT_A + 1)
    g["lote_apt"] = {"faixa": lin, "ini": lin + 1}
    lin += 2
    for k, f in _fileiras(N_APT - APT_LOTE):
        g["aptidoes"].append((lin + f * (ALT_A + 1), CARTAS[k]))
    lin += ((N_APT - APT_LOTE) // 3) * (ALT_A + 1)
    g["lote_apt"]["fim"] = lin - 2
    lin = fecha("aptidoes", lin - 2)
    # --- os pactos: três lugares, um embaixo do outro, cada um com o grupo dele
    t = abre("pactos")
    g.update({"pac_caixas": t + 1, "pac_permanentes": f"D{t + 2}"})
    g["pactos"] = [t + 5 + 10 * i for i in range(N_PACTOS)]
    fecha("pactos", g["pactos"][-1] + 8)
    g["linhas"] = g["fim"]["pactos"] + RESPIRO
    return g


def celulas_do_feitico(r0, c0):
    """os endereços das caixas de digitar e de menu de uma carta de feitiço, e os das que a ficha calcula"""
    a, b, c, d, e = (c0 + k for k in range(5))
    return {
        "classe": _a1(a, r0), "nome": _a1(b, r0), "estado": _a1(d, r0), "como": _a1(a, r0 + F_TXT),
        "forma": _a1(a, r0 + F_N1), "dano": _a1(b, r0 + F_N1), "pe": _a1(c, r0 + F_N1), "resolve": _a1(d, r0 + F_N1),
        "acao": _a1(a, r0 + F_N2), "alcance": _a1(b, r0 + F_N2),
        "mel": [_a1(b, r0 + F_MEL + i) for i in range(N_MEL)], "preco": [_a1(d, r0 + F_MEL + i) for i in range(N_MEL)],
        "res": [_a1(b, r0 + F_RES + i) for i in range(N_RES)], "dev": [_a1(d, r0 + F_RES + i) for i in range(N_RES)],
        "conta": _a1(b, r0 + F_CONTA), "ampliar": _a1(b, r0 + F_AMP), "avisos": _a1(b, r0 + F_AV),
    }


def celulas_da_passiva(r0, c0):
    return {"nome": _a1(c0, r0), "cp": _a1(c0 + 2, r0), "custo": _a1(c0 + 3, r0), "faz": _a1(c0, r0 + 2), "texto": _a1(c0 + 1, r0 + 5)}


def celulas_da_aptidao(r0, c0):
    return {"nome": _a1(c0, r0), "cp": _a1(c0 + 3, r0), "requisito": _a1(c0, r0 + 1), "faz": _a1(c0, r0 + 4),
            "escala": _a1(c0 + 1, r0 + 4 + TXT_APT), "texto": _a1(c0 + 1, r0 + 5 + TXT_APT)}


def celulas_do_pacto(r):
    return {"nome": f"E{r}", "forma": f"L{r}", "concede": f"P{r}", "dou": f"D{r + 2}", "recebo": f"L{r + 2}", "clausula": f"D{r + 7}"}


# ---------------------------------------------------------------------------------------------
# A DADOS_AM: as tabelas, as contas e uma linha por feitiço.
# ---------------------------------------------------------------------------------------------
class _Dados:
    """escreve tabelas lado a lado, do cabeçalho na linha 1 para baixo, e guarda onde cada uma ficou"""
    def __init__(self, e_cab, e_txt, e_num):
        self.cel, self.T, self.prox, self.linhas = {}, {}, 1, 1
        self.e_cab, self.e_txt, self.e_num = e_cab, e_txt, e_num

    def poe(self, col, lin, v):
        if v is None:
            return
        texto = isinstance(v, str) and not v.startswith("=")
        self.cel[_a1(col, lin)] = (v, self.e_txt if texto else self.e_num)
        self.linhas = max(self.linhas, lin)

    def tabela(self, nome, cabecalhos, linhas):
        col = self.prox
        for j, t in enumerate(cabecalhos):
            self.cel[_a1(col + j, 1)] = (t, self.e_cab)
        for i, linha in enumerate(linhas):
            for j, v in enumerate(linha):
                self.poe(col + j, 2 + i, v(2 + i) if callable(v) else v)
        self.T[nome] = (col, 2, 1 + len(linhas), len(cabecalhos))
        self.prox = col + len(cabecalhos) + 1
        return col

    def faixa(self, nome, so=None, ate=None, aba=""):
        """a tabela inteira; `so` é uma coluna dela (de 0), `ate` corta nas primeiras colunas"""
        col, l1, l2, n = self.T[nome]
        if so is not None:
            return _faixa(col + so, l1, col + so, l2, aba)
        return _faixa(col, l1, col + (ate or n) - 1, l2, aba)

    def celula(self, nome, linha, coluna, aba=""):
        col, l1, _, _ = self.T[nome]
        return _abs(col + coluna, l1 + linha, aba)


def _conta_da_ficha(layout, nome):
    """a célula de uma das "contas da ficha" da DADOS, pelo nome dela"""
    dados = ix._aba(layout, "DADOS")
    cel = {r[0]: r[1] for r in dados["celulas"]}
    cab = next(c for c, v in cel.items() if v == "contas da ficha")
    lin, col = ix._lc(cab)
    for l in range(lin + 1, lin + 200):
        if cel.get(_a1(col, l)) == nome:
            return _abs(col + 1, l, "DADOS!")
    raise SystemExit(f"ficha_amaldicoada: a DADOS nao tem a conta {nome!r}")


def _se(cond, texto):
    return f'IF({cond},{texto},"")'


def trocas(layout, CAT=None, TEC=None):
    """a DADOS_AM inteira, e os endereços que a aba lê dela.
    {"aba_dados": a aba, "G": geometria, "R": regras, "D": o construtor, "H": contas, "F": colunas da conta de feitiço}"""
    R = regras(CAT, TEC)
    G = geometria()
    idx = ix.indice(layout)
    falta = [k for k in ("nivel", "maestria", "classe máxima", "atr_Essência", "cd de feitiço", "conjuração", "classe 0 grátis", "nome")
             if not idx.get(k)]
    if falta:
        raise SystemExit(f"o indice da DADOS nao publica {falta}: a Ficha Amaldiçoada le essas caixas da FICHA")
    dados = ix._aba(layout, "DADOS")
    dcel = {r[0]: r for r in dados["celulas"]}
    cab = next(r[0] for r in dados["celulas"] if r[1] == "marcos")
    lin_cab = ix._lc(cab)[0]
    e_txt = next(r[2] for r in dados["celulas"] if ix._lc(r[0]) == (lin_cab + 1, 1))
    e_num = dcel[f"{cab[:-len(str(lin_cab))]}{lin_cab + 1}"][2]
    D = _Dados(dcel[cab][2], e_txt, e_num)

    F_ = lambda k: _A(idx[k], "FICHA!")
    # --- a rota de criação, pelas três marcas que a FICHA calcula da Origem (a sem energia também é Técnica Marcial, e
    # por isso vem primeiro), e os nomes de cada rota numa tabela: a aba escreve INDEX(nome, rota)
    D.tabela("rota", ["rota da ficha"],
             [[f'=IF(N({_conta_da_ficha(layout, "sem energia")})=1,4,IF(N({_conta_da_ficha(layout, "técnica marcial")})=1,3,'
               f'IF(N({_conta_da_ficha(layout, "sem técnica")})=1,2,1)))']])
    ROTA = D.celula("rota", 0, 0)
    D.tabela("rotulos", ["rótulo da rota"] + [n.lower() for n in NOMES_DAS_ROTAS],
             [[k] + v for k, v in R["rotulos"].items()] + [["nome da rota"] + list(NOMES_DAS_ROTAS)])
    _rot = {k: i for i, k in enumerate(list(R["rotulos"]) + ["nome da rota"])}
    rotulo = lambda k, aba="": f'INDEX({_faixa(D.T["rotulos"][0] + 1, 2 + _rot[k], D.T["rotulos"][0] + 4, 2 + _rot[k], aba)},1,{ROTA if not aba else aba + ROTA})'
    # --- as Famílias: o estado de cada uma, lido do menu da aba
    D.tabela("fam", ["família da técnica", "estado da família", "família livre", "família fechada"],
             [[f, f"={_A(_a1(C(G['cols_fam'][i][0]), G['familias'] + 1), AM)}&\"\"",
               (lambda i_: lambda n: f'=IF(${L(D.prox + 1)}{n}="{LIVRE}",1,0)')(i),
               (lambda i_: lambda n: f'=IF(${L(D.prox + 1)}{n}="{FECHADA}",1,0)')(i)] for i, f in enumerate(R["familias"])])
    FAM = D.faixa("fam")
    livre = lambda fam: f"IFERROR(VLOOKUP({fam},{FAM},3,FALSE),0)"
    fechada = lambda fam: f"IFERROR(VLOOKUP({fam},{FAM},4,FALSE),0)"
    D.tabela("estado", ["estado de família"], [[LIVRE], [NEUTRA], [FECHADA]])
    # --- os preços por Classe: Leve, Média e Pesada, e as três com o desconto de Família Livre
    D.tabela("classe", ["classe do feitiço", "leve", "média", "pesada", "leve livre", "média livre", "pesada livre", "limite de melhorias"],
             [[c["classe"]] + c["precos"] + [c["limite"]] for c in R["classes"]])
    PRECOS = _faixa(D.T["classe"][0] + 1, 2, D.T["classe"][0] + 6, 1 + len(R["classes"]))
    preco_da_classe = lambda c: _faixa(D.T["classe"][0] + 1, 1 + c, D.T["classe"][0] + 6, 1 + c)
    # --- as Formas
    c0 = D.prox
    col_f = lambda k, n: f"${L(c0 + k)}{n}"
    D.tabela("formas", ["forma", "família da forma", "peso da forma", "código de preço da forma", "forma fechada", "restrição embutida",
                        "tipo de dano", "como resolve", "resolve por teste", "degrau da primeira parte", "degrau da segunda parte",
                        "mostra mais alvos", "existe na classe 0", "menu de forma", "menu de forma da classe 0"],
             [[f["nome"], f["familia"] or "", f["peso"],
               (lambda n: f"=IF({col_f(2, n)}=0,0,{col_f(2, n)}+3*{livre(col_f(1, n))})"),
               (lambda n: f"={fechada(col_f(1, n))}"),
               f["embutida"], f["tipo"], f["resolve"], f["tr"], f["grau1"], f["grau2"], f["alvos"], f["na_zero"],
               (lambda n: f'=IF({col_f(4, n)}=1,"",{col_f(0, n)})'),
               (lambda n: f'=IF(AND({col_f(12, n)}=1,{col_f(4, n)}=0),{col_f(0, n)},"")')] for f in R["formas"]])
    forma_col = lambda k: D.faixa("formas", so=k)
    # --- o alcance: uma linha por Forma e por faixa de Classe, e uma coluna por degrau subido
    D.tabela("alcance", ["alcance de"] + [f"primeira parte +{g}" for g in range(GRAUS_NA_TABELA)] +
             [f"segunda parte +{g}" for g in range(GRAUS_NA_TABELA)], R["alcance"])
    ALC1 = _faixa(D.T["alcance"][0] + 1, 2, D.T["alcance"][0] + GRAUS_NA_TABELA, D.T["alcance"][2])
    ALC2 = _faixa(D.T["alcance"][0] + 1 + GRAUS_NA_TABELA, 2, D.T["alcance"][0] + 2 * GRAUS_NA_TABELA, D.T["alcance"][2])
    # --- as peças do menu de Melhoria
    c0p = D.prox
    col_p = lambda k, n: f"${L(c0p + k)}{n}"
    D.tabela("pecas", ["peça", "família da peça", "peso da peça", "código de preço", "peça fechada", "peça de controle",
                       "menu de melhoria", "menu de melhoria leve"],
             [[p["nome"], p["familia"] or "", p["peso"],
               (lambda n: f"={col_p(2, n)}+3*{livre(col_p(1, n))}"),
               (lambda n: f"={fechada(col_p(1, n))}"),
               int(p["familia"] == "Controle"),
               (lambda n: f'=IF({col_p(4, n)}=1,"",{col_p(0, n)})'),
               (lambda n: f'=IF(AND({col_p(2, n)}=1,{col_p(4, n)}=0),{col_p(0, n)},"")')] for p in R["pecas"]])
    PECAS = D.faixa("pecas")
    # --- as Restrições
    D.tabela("res", ["menu de restrição", "restrição", "o que devolve", "é de frequência", "menu de restrição leve"],
             [[r["rotulo"], r["nome"], r["devolve"], r["frequencia"], r["rotulo"] if r["devolve"] == 1 else ""] for r in R["restricoes"]])
    RES = D.faixa("res")
    # --- as Passivas e a Classe Passiva
    cPa = D.prox
    D.tabela("passivas", ["passiva", "classe passiva", "o que a passiva faz", "do fundamento", "da técnica marcial", "menu de passiva"],
             [[p["nome"], p["cp"], p["faz"], p["fund"], p["marc"],
               (lambda n: f'=IF(OR(AND({ROTA}<=2,${L(cPa + 3)}{n}=1),AND({ROTA}>=2,${L(cPa + 4)}{n}=1)),${L(cPa)}{n},"")')]
              for p in R["passivas"]])
    D.tabela("cp", ["classe passiva liberada", "libera no nível"], [[k, v] for k, v in sorted(R["cp"].items())])
    # --- as aptidões: as duas de graça ficam fora do menu
    cAp = D.prox
    ap = lambda k, n: f"${L(cAp + k)}{n}"
    D.tabela("aptidoes", ["aptidão", "requisito da aptidão", "classe passiva da aptidão", "o que o refino escala", "o que a aptidão faz",
                          "menu de aptidão", "é bênção", "é a extensão de domínio", "de graça"],
             [[a["nome"], a["requisito"], _ini(a["cp"]), _ini(a["escala"]), a["faz"],
               # a Restrição Celestial sem energia compra Bênção; as outras rotas, aptidão; o Corpo Amaldiçoado não compra a
               # Extensão de Domínio; as duas de graça ficam fora do menu
               (lambda n: f'=IF({ap(8, n)}=1,"",IF({ROTA}=4,IF({ap(6, n)}=1,{ap(0, n)},""),IF(OR({ap(6, n)}=1,AND({ROTA}=3,{ap(7, n)}=1)),"",{ap(0, n)})))'),
               a["bencao"], a["extensao"], a["gratis"]] for a in R["aptidoes"]])
    # --- a peça da rota: o menu da linha da rota mostra as sementes no Sem Técnica e o equipamento na Técnica Marcial
    D.tabela("sementes", ["semente"], [[x] for x in R["sementes"]])
    D.tabela("equipamento", ["equipamento"], [[x] for x in EQUIPAMENTO])
    n_menu = max(len(R["sementes"]), len(EQUIPAMENTO))
    D.tabela("menu_rota", ["menu da peça da rota"],
             [[f'=IF({ROTA}=2,IFERROR(INDEX({D.faixa("sementes", so=0)},{k + 1}),""),IF({ROTA}>=3,IFERROR(INDEX({D.faixa("equipamento", so=0)},{k + 1}),""),""))']
              for k in range(n_menu)])
    equip = f'{_A(geometria()["rota_menu"], AM)}&""'
    cGr = D.prox
    D.tabela("grupos", ["grupo de arma", "acerta com força", "acerta com destreza", "menu de grupo"],
             [[g, int("Força" in ats), int("Destreza" in ats),
               (lambda n: f'=IF(AND({ROTA}>=3,{equip}="{EQUIPAMENTO[0]}"),${L(cGr)}{n},"")')] for g, ats in R["grupos"].items()])
    # --- a Classe 0, a Liberação, a Técnica Máxima, o Domínio e os pactos
    z = R["zero"]
    D.tabela("zero", ["nível da classe 0", "quantos de classe 0", "dados da classe 0"], [list(l) for l in zip(z["niveis"], z["quantos"], z["dados"])])
    D.tabela("lib", ["nível da liberação"], [[n] for n in R["liberacao"]["niveis"]])
    D.tabela("classe_lib", ["classe da liberação"], [[c["classe"]] for c in R["classes"] if c["classe"] >= R["liberacao"]["classe_minima"]])
    D.tabela("tm", ["nível da técnica máxima", "dados da técnica máxima", "pontos de montagem"],
             [[f["de"], f["dados"], f["montagem"]] for f in R["tm"]["faixas"]])
    D.tabela("dom", ["degrau do domínio", "espaços do degrau", "nível do degrau", "refino do degrau", "o degrau abre em"],
             [[d["degrau"], d["espacos"], d["nivel"] or 0, d["refino"], _ini(d["abre_em"])] for d in R["dominio"]["degraus"]])
    D.tabela("pacto_forma", ["forma do pacto", "quando se fecha"], [[_ini(f["forma"]), f["quando"]] for f in R["pactos"]["formas"]])
    D.tabela("pacto_concede", ["o pacto concede"], [[_ini(c["concede"])] for c in R["pactos"]["concede"]])
    if PERMANENTE not in [_ini(f["forma"]) for f in R["pactos"]["formas"]] or ESPACO_DE_PACTO not in [_ini(c["concede"]) for c in R["pactos"]["concede"]]:
        raise SystemExit("ficha_amaldicoada: o livro nao tem mais o pacto permanente ou o espaco de feitico que ele concede")

    # --- a conta de cada feitiço: uma linha por lugar, as 36 de feitiço e as 3 de Liberação
    nomes = (["lugar", "liberação", "vaga", "classe", "nome", "forma"] + [f"m{i}" for i in range(1, N_MEL + 1)] +
             [f"r{i}" for i in range(1, N_RES + 1)] +
             ["tem", "lf"] + [f"k{i}" for i in range(N_MEL + 1)] + [f"x{i}" for i in range(N_MEL + 1)] +
             ["ct", "emb", "tp", "tr"] + [f"c{i}" for i in range(1, N_RES + 1)] + [f"b{i}" for i in range(1, N_RES + 1)] +
             [f"n{j}" for j in range(1, 7)] + ["dL", "dM", "nm", "nr", "g", "dv0", "dv", "usa", "perde", "s", "d", "dep"] +
             [f"d{c['classe']}" for c in R["classes"]] + [f"t{c['classe']}" for c in R["classes"]] +
             ["erros", "ne", "avisos", "na", "estado", "linha", "pe", "acao", "resolve", "dano", "lg", "mr", "q1", "q2", "alcance",
              "conta", "ampliar"] + [f"pt{i}" for i in range(1, N_MEL + 1)] + [f"dt{i}" for i in range(1, N_RES + 1)])
    cF = D.prox
    col = {k: cF + i for i, k in enumerate(nomes)}
    lugares = [("Feitiço", 0, i + 1, celulas_do_feitico(*pos)) for i, pos in enumerate(G["feiticos"])] + \
              [("Liberação", 1, i + 1, celulas_do_feitico(*pos)) for i, pos in enumerate(G["libs"])]
    n_classes = len(R["classes"])
    H = {}                                   # as contas com nome, escritas mais abaixo; a conta de feitiço cita três delas

    def linha_de_feitico(n, lugar):
        rot, lib, vaga, cel = lugar
        P = lambda k: f"${L(col[k])}{n}"
        Rg = lambda a, b: f"${L(col[a])}{n}:${L(col[b])}{n}"
        M, RR, BB, KK, CC, NN = Rg("m1", f"m{N_MEL}"), Rg("r1", f"r{N_RES}"), Rg("b1", f"b{N_RES}"), Rg("k0", f"k{N_MEL}"), Rg("c1", f"c{N_RES}"), Rg("n1", "n6")
        tem_m = lambda nome: f'COUNTIF({M},"{nome}")'
        tem_b = lambda nome: f'COUNTIF({BB},"{nome}")'
        tem = lambda nome: f'({tem_m(nome)}+{tem_b(nome)})'
        Cc, forma, lf = P("classe"), P("forma"), P("lf")
        da_forma = lambda k: f"IF({lf}=0,0,INDEX({forma_col(k)},{lf}))"
        o = {"lugar": f"{rot} {vaga}", "liberação": lib, "vaga": vaga,
             "classe": f"=MAX(1,MIN({n_classes},N({_A(cel['classe'], AM)})))",
             "nome": f'={_A(cel["nome"], AM)}&""', "forma": f'={_A(cel["forma"], AM)}&""'}
        for i in range(N_MEL):
            o[f"m{i + 1}"] = f'={_A(cel["mel"][i], AM)}&""'
        for i in range(N_RES):
            o[f"r{i + 1}"] = f'={_A(cel["res"][i], AM)}&""'
        # --- daqui para baixo a fórmula é a mesma em toda linha: só as próprias colunas, sem endereço da aba
        o["tem"] = f'=IF({P("nome")}<>"",1,0)'
        o["lf"] = f"=IFERROR(MATCH({forma},{forma_col(0)},0),0)"
        o["k0"], o["x0"] = "=" + da_forma(3), "=" + da_forma(4)
        for i in range(1, N_MEL + 1):
            o[f"k{i}"] = f"=IFERROR(VLOOKUP({P(f'm{i}')},{PECAS},4,FALSE),0)"
            o[f"x{i}"] = f"=IFERROR(VLOOKUP({P(f'm{i}')},{PECAS},5,FALSE),0)"
        o["ct"] = "=" + "+".join(f"IFERROR(VLOOKUP({P(f'm{i}')},{PECAS},6,FALSE),0)" for i in range(1, N_MEL + 1))
        o["emb"], o["tp"], o["tr"] = "=" + da_forma(5), "=" + da_forma(6), "=" + da_forma(8)
        for i in range(1, N_RES + 1):
            o[f"c{i}"] = f"=IFERROR(VLOOKUP({P(f'r{i}')},{RES},3,FALSE),0)"
            o[f"b{i}"] = f'=IFERROR(VLOOKUP({P(f"r{i}")},{RES},2,FALSE),"")'
        for j in range(1, 7):
            o[f"n{j}"] = f"=COUNTIF({KK},{j})"
        o["dL"] = f"=COUNTIF({CC},1)"
        o["dM"] = f"=COUNTIF({CC},2)+{P('emb')}"
        o["nm"] = f'=COUNTIF({M},"?*")'
        o["nr"] = f'=COUNTIF({RR},"?*")+{P("emb")}'
        o["g"] = f"=SUMPRODUCT({NN},INDEX({PRECOS},{Cc},0))"
        o["dv0"] = f"={P('dL')}*CEILING({Cc}/2,1)+{P('dM')}*{Cc}"
        o["dv"] = f"=MIN(2*{Cc},{P('dv0')})"
        o["usa"] = f"=MIN({P('dv')},{P('g')})"
        o["perde"] = f"={P('dv')}-{P('usa')}"
        o["s"] = f"=3*{Cc}-{P('g')}+{P('usa')}"
        o["d"] = f"=MAX(0,{P('s')})+{P('liberação')}*{Cc}"
        o["dep"] = "=(" + "+".join(f"IF({tem_m(x)}>0,1,0)" for x in SOMAM_METADE) + f")*FLOOR({P('d')}/2,1)"
        for c in R["classes"]:
            k = c["classe"]
            gk = f"SUMPRODUCT({NN},{preco_da_classe(k)})"
            o[f"d{k}"] = (f"=MAX(0,{3 * k}-{gk}+MIN({2 * k},{P('dL')}*{math.ceil(k / 2)}+{P('dM')}*{k},{gk}))+{P('liberação')}*{k}")
            dk, tp = P(f"d{k}"), P("tp")
            o[f"t{k}"] = (f'=IF({tp}=2,3*{dk}&" de vida temp.",IF({tp}=3,"sem dano",IF({dk}=0,IF({tp}=1,"sem cura","sem dano"),'
                          f'IF({tp}=1,"cura ","")&{dk}&"d8")))')
        # os erros, na ordem do estudo
        NIV, MAXC, LIBS = H["nível"], H["maior classe"], H["liberações"]
        cac, tudo, ines = "Corpo a Corpo", "Tudo ou Nada", "Inescapável"
        erros = [
            _se(f'AND({P("liberação")}=1,{P("vaga")}>{LIBS})', f'"O nível "&{NIV}&" dá "&{LIBS}&" Liberação Máxima"'),
            _se(f"{Cc}>{MAXC}", f'"Classe "&{Cc}&": o nível "&{NIV}&" libera até a "&{MAXC}'),
            _se(f'{P("x0")}=1', f'"Família Fechada: a Forma "&{forma}'),
        ] + [_se(f'{P(f"x{i}")}=1', f'"Família Fechada: "&{P(f"m{i}")}') for i in range(1, N_MEL + 1)] + [
            _se(f'{P("nm")}>INDEX({D.faixa("classe", so=7)},{Cc})',
                f'{P("nm")}&" Melhorias: a Classe "&{Cc}&" aceita "&INDEX({D.faixa("classe", so=7)},{Cc})'),
            _se(f'{P("nr")}>{N_RES}', f'{P("nr")}&" Restrições"&IF({P("emb")}=1,", contando a que a Forma "&{forma}&" já traz","")&": o limite é {N_RES}"'),
            _se(f'{P("s")}<0', f'"Orçamento estourado: faltam "&(-{P("s")})&IF({P("s")}<-1," pontos"," ponto")'),
            _se("+".join(f"IFERROR(VLOOKUP({P(f'r{i}')},{RES},4,FALSE),0)" for i in range(1, N_RES + 1)) + ">1",
                f'{P("b1")}&" e "&{P("b2")}&" são as duas de frequência"'),
        ] + [_se(f"AND({tem(a)}>0,{tem(b)}>0)", f'"{a} não entra com {b}"') for a, b in R["pares"]] + [
            _se(f'AND({tem_b(cac)}>0,{P("emb")}=0,OR({forma}="Cone",{forma}="Linha"))', f'"{cac} não entra em "&{forma}'),
            _se(f'AND({tem_b(cac)}>0,{P("emb")}=1)', f'"A Forma "&{forma}&" já traz o {cac}"'),
            _se(f'AND({tem_b(tudo)}>0,{P("tr")}=0)', f'"{tudo} só entra em feitiço de Teste de Resistência"'),
            _se(f'AND({tem_m(ines)}>0,OR({P("nm")}>1,{P("nr")}>0))', f'"{ines} não aceita outra peça"'),
            _se(f'AND({P("liberação")}=1,{Cc}<{R["liberacao"]["classe_minima"]})',
                f'"Liberação Máxima é de Classe {R["liberacao"]["classe_minima"]} ou mais"'),
            _se(f'AND({P("liberação")}=1,OR({P("tp")}=1,{P("tp")}=2))', '"Liberação Máxima não serve para cura"'),
            _se(f'AND({P("liberação")}=1,{tem_m(ines)}+{tem_m("Toca a Alma")}>0)', '"Esta peça não entra numa Liberação Máxima"'),
            _se(f'{P("d")}+{P("dep")}>4*{Cc}',
                f'({P("d")}+{P("dep")})&" dados somando alvos e repetições: o teto da Classe "&{Cc}&" é "&4*{Cc}'),
        ]
        conta_txt = lambda x: f'IF({x}="",0,(LEN({x})-LEN(SUBSTITUTE({x}," · ","")))/3+1)'
        o["erros"] = f'=IF({P("tem")}=0,"",TEXTJOIN(" · ",TRUE,{",".join(erros)}))'
        o["ne"] = "=" + conta_txt(P("erros"))
        avisos = [
            _se(f'{P("dv0")}>2*{Cc}', f'"A devolução parou no teto de "&2*{Cc}'),
            _se(f'{P("perde")}>0', f'"Devolução perdida: "&{P("perde")}&IF({P("perde")}>1," pontos"," ponto")&" sem peça para pagar"'),
            _se(f'AND({P("ct")}>0,{P("d")}=0)', '"Controle sem dano: uma rodada a mais e CD +2"'),
            _se(f'AND({P("ct")}>0,{P("d")}>0,{P("d")}<={Cc})', '"Controle com um quarto do teto: uma rodada a mais"'),
        ]
        o["avisos"] = f'=IF({P("tem")}=0,"",TEXTJOIN(" · ",TRUE,{",".join(avisos)}))'
        o["na"] = "=" + conta_txt(P("avisos"))
        o["estado"] = (f'=IF({P("tem")}=0,IF({P("nm")}+{P("nr")}-{P("emb")}>0,"{SEM_NOME}",""),IF({P("ne")}>0,"{T_ERRO} "&{P("ne")}&IF({P("ne")}>1," erros"," erro"),'
                       f'IF({P("na")}>0,"{T_AVISO}"&{P("na")}&IF({P("na")}>1," avisos"," aviso"),"{NA_REGRA}")))')
        o["linha"] = (f'=IF({P("tem")}=0,"",IF({P("ne")}+{P("na")}=0,"{DENTRO}",{P("erros")}&IF(AND({P("ne")}>0,{P("na")}>0)," · ","")&{P("avisos")}))')
        o["pe"] = f'=IF({P("tem")}=0,"",IF({P("liberação")}=1,CEILING(4.5*{Cc},1),3*{Cc})&" PE")'
        carrega = f'IF({tem_b("Carregar")}>0," +1 turno","")'
        o["acao"] = (f'=IF({P("tem")}=0,"",IF({P("liberação")}=1,"Rodada inteira",IF({tem_b("Atrasar")}>0,IF({tem_b("Carregar")}>0,"Rodada +1 turno","Rodada inteira"),'
                     f'IF({tem_m("Rápido")}>0,"Bônus",IF({tem_m("Reação")}>0,"Reação","Padrão"))&{carrega})))')
        o["resolve"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",IF({tem_m(ines)}>0,"Automático",IF({tem_m("Certeiro")}>0,"TR para metade",'
                        f'INDEX({forma_col(7)},{lf}))))')
        tC = f'INDEX({Rg("t1", f"t{n_classes}")},1,{Cc})'
        tC = f'UPPER(LEFT({tC},1))&MID({tC},2,99)'
        o["dano"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",IF(OR({P("tp")}>=2,{P("d")}=0),{tC},{tC}&" = "&FLOOR({P("d")}*4.5,1)&'
                     f'IF({P("dep")}>0," · +"&{P("dep")}&"d8","")))')
        o["lg"] = f'={tem_m("Longe")}+3*{tem_m("Muito Longe")}'
        o["mr"] = f'={tem_m("Maior")}+3*{tem_m("Muito Maior")}'
        grau = lambda k: f'IF({lf}=0,0,CHOOSE(1+INDEX({forma_col(k)},{lf}),0,{P("lg")},{P("mr")},{P("lg")}+{P("mr")}))'
        o["q1"], o["q2"] = "=" + grau(9), "=" + grau(10)
        na_tabela = f"({lf}-1)*3+IF({Cc}>=6,3,2)"
        alvos = tem_m("Mais Um")
        o["alcance"] = (f'=IF(OR({P("tem")}=0,{lf}=0),"",INDEX({ALC1},{na_tabela},1+MIN({GRAUS_NA_TABELA - 1},{P("q1")}))&'
                        f'INDEX({ALC2},{na_tabela},1+MIN({GRAUS_NA_TABELA - 1},{P("q2")}))&'
                        f'IF(INDEX({forma_col(11)},{lf})=1,IF({alvos}>0," · +"&{alvos}&IF({alvos}>1," alvos"," alvo"),"")&'
                        f'IF({tem_m("Rajada")}>0," · "&({Cc}+1)&" tiros",""),""))')
        o["conta"] = (f'=IF({P("tem")}=0,"",3*{Cc}&" − "&{P("g")}&" + "&{P("usa")}&IF({P("liberação")}=1," + "&{Cc},"")&" = "&{P("d")}&"d8 · teto "&4*{Cc}&'
                      f'IF({P("emb")}=1," · a Forma devolve "&{Cc},"")&IF({P("perde")}>0," · perde "&{P("perde")},""))')
        termos = [f'IF(AND({k}>{Cc},{k}<={MAXC}),"{k} → "&{P(f"t{k}")}&", "&IF({P("liberação")}=1,{math.ceil(4.5 * k)},{3 * k})&" PE","")'
                  for k in range(2, n_classes + 1)]
        o["ampliar"] = (f'=IF({P("tem")}=0,"",IF({Cc}>={MAXC},"Já está na maior Classe que o nível liberou",TEXTJOIN(" · ",TRUE,{",".join(termos)})))')
        pesos = ",".join(f'"{p}"' for p in list(NOME_DO_PESO) + [p + " · Livre" for p in NOME_DO_PESO])
        for i in range(1, N_MEL + 1):
            k = P(f"k{i}")
            o[f"pt{i}"] = f'=IF(OR({P("tem")}=0,{k}=0),"","−"&INDEX({PRECOS},{Cc},{k})&" · "&CHOOSE({k},{pesos}))'
        for i in range(1, N_RES + 1):
            c = P(f"c{i}")
            o[f"dt{i}"] = f'=IF(OR({P("tem")}=0,{P(f"r{i}")}=""),"","+"&IF({c}=1,CEILING({Cc}/2,1),{Cc}))'
        return [o[k] for k in nomes]

    # as contas com nome vêm ANTES na escrita das fórmulas (a conta de feitiço cita três), mas moram depois na aba:
    # por isso os endereços delas são calculados primeiro
    c_contas = cF + len(nomes) + 1
    ordem_das_contas = []

    def reserva(nome):
        H[nome] = _abs(c_contas + 1, 2 + len(ordem_das_contas))
        ordem_das_contas.append(nome)
    for nome in ("nível", "maestria", "maior classe", "marcos", "refino", "essência", "escolhas de Leque", "liberações",
                 "classe 0 quantos", "classe 0 dados", "espaços do nível", "espaços de pacto", "espaços", "feitiços montados",
                 "classe passiva da regra própria", "espaços da regra própria", "espaços em passivas", "espaços no domínio",
                 "sem espaço", "cabem", "livres", "passivas pagas", "passivas do Leque", "aptidões anotadas", "aptidões compráveis",
                 "pactos permanentes", "teto de pactos", "classe do índice", "famílias livres", "famílias fechadas",
                 "metade do refino", "terço do refino", "degrau do domínio", "dados da técnica máxima", "montagem da técnica máxima",
                 "gasto da técnica máxima", "fechada na técnica máxima", "rota", "equipamento", "arma",
                 "atributo do grupo 1", "atributo do grupo 2", "atributo do grupo 3", "valor do grupo 1", "valor do grupo 2",
                 "valor do grupo 3", "atributos dos grupos", "usos do estímulo"):
        reserva(nome)

    D.tabela("feit", [("conta de feitiço" if k == "lugar" else k) for k in nomes],
             [[None] for _ in lugares])                # só o lugar da tabela; as células vêm logo abaixo
    for i, lugar in enumerate(lugares):
        for j, v in enumerate(linha_de_feitico(2 + i, lugar)):
            D.poe(cF + j, 2 + i, v)
    FEIT = lambda k, i=None: (_abs(col[k], 2 + i, DA) if i is not None else _faixa(col[k], 2, col[k], 1 + len(lugares)))

    # --- as contas com nome
    passivas_c = [celulas_da_passiva(*p) for p in G["passivas"]]
    aptidoes_c = [celulas_da_aptidao(*p) for p in G["aptidoes"]]
    pactos_c = [celulas_do_pacto(r) for r in G["pactos"]]
    PASS, CPT, DOM, GRU = D.faixa("passivas"), D.faixa("cp"), D.faixa("dom"), D.faixa("grupos")
    cp_de = lambda cel: f'IFERROR(VLOOKUP({_A(cel, AM)},{PASS},2,FALSE),0)'
    tm_mel = [_a1(C(a), G["tm_mel"]) for a, _ in G["cols_tm_mel"]]
    tm_cod = [f'IFERROR(VLOOKUP({_A(G["tm_forma"], AM)},{D.faixa("formas", ate=4)},4,FALSE),0)'] + \
             [f'IFERROR(VLOOKUP({_A(m, AM)},{PECAS},4,FALSE),0)' for m in tm_mel]
    tm_fech = [f'IFERROR(VLOOKUP({_A(G["tm_forma"], AM)},{D.faixa("formas", ate=5)},5,FALSE),0)'] + \
              [f'IFERROR(VLOOKUP({_A(m, AM)},{PECAS},5,FALSE),0)' for m in tm_mel]
    formulas = {
        "nível": f"=N({F_('nivel')})",
        "maestria": f"=N({F_('maestria')})",
        "maior classe": f"=MAX(1,MIN({n_classes},N({F_('classe máxima')})))",
        "marcos": f"=N({_conta_da_ficha(layout, 'marcos que já passou')})",
        "refino": f"=MAX(1,N({_conta_da_ficha(layout, 'refino atual')}))",
        "essência": f"=N({F_('atr_Essência')})",
        "escolhas de Leque": f"=MIN(N({_conta_da_ficha(layout, 'escolhas de Leque')}),{H['marcos']})",
        "liberações": f'=COUNTIF({D.faixa("lib")},"<="&{H["nível"]})',
        "classe 0 quantos": f'=IFERROR(INDEX({D.faixa("zero", so=1)},MATCH({H["nível"]},{D.faixa("zero", so=0)},1)),0)',
        "classe 0 dados": f'=IFERROR(INDEX({D.faixa("zero", so=2)},MATCH({H["nível"]},{D.faixa("zero", so=0)},1)),0)',
        "espaços do nível": f"=2+INT({H['nível']}/2)+{H['marcos']}",
        "espaços de pacto": "=" + "+".join(f'IF(AND({_A(p["forma"], AM)}="{PERMANENTE}",{_A(p["concede"], AM)}="{ESPACO_DE_PACTO}"),1,0)' for p in pactos_c),
        "espaços": f"={H['espaços do nível']}+{H['espaços de pacto']}",
        "feitiços montados": f"=SUM({_faixa(col['tem'], 2, col['tem'], 1 + N_FEITICOS)})",
        "classe passiva da regra própria": f"=N({_A(G['cp_regra'], AM)})",
        "espaços da regra própria": f"=MAX(0,{H['classe passiva da regra própria']}-1)",
        "espaços em passivas": "=" + "+".join(cp_de(p["nome"]) for p in passivas_c[:PAGAS]) + f"+{H['espaços da regra própria']}",
        "degrau do domínio": f'={_A(G["degrau"], AM)}&""',
        "espaços no domínio": f"=IF({ROTA}<>1,0,IFERROR(VLOOKUP({H['degrau do domínio']},{DOM},2,FALSE),0))",
        "sem espaço": f"=IF({H['espaços em passivas']}+{H['espaços no domínio']}>{H['espaços']},1,0)",
        "cabem": f"={H['espaços']}+{H['escolhas de Leque']}-{H['espaços em passivas']}-{H['espaços no domínio']}",
        "livres": f"={H['cabem']}-{H['feitiços montados']}",
        "passivas pagas": "=" + "+".join(f'IF({_A(p["nome"], AM)}<>"",1,0)' for p in passivas_c[:PAGAS]),
        "passivas do Leque": "=" + "+".join(f'IF({_A(p["nome"], AM)}<>"",1,0)' for p in passivas_c[PAGAS:]),
        "aptidões anotadas": "=" + "+".join(f'IF({_A(a["nome"], AM)}<>"",1,0)' for a in aptidoes_c),
        "aptidões compráveis": f"=MAX(0,N({_conta_da_ficha(layout, 'máximo de aptidões')})-{len([a for a in R['aptidoes'] if a['gratis'] and not a['bencao']])})",
        "pactos permanentes": "=" + "+".join(f'IF({_A(p["forma"], AM)}="{PERMANENTE}",1,0)' for p in pactos_c),
        "teto de pactos": f"=FLOOR({H['essência']}/2,1)",
        "classe do índice": f"=IF(N({_A(G['classe_do_indice'], AM)})<1,{H['maior classe']},MIN({n_classes},N({_A(G['classe_do_indice'], AM)})))",
        "famílias livres": f'=COUNTIF({D.faixa("fam", so=1)},"{LIVRE}")',
        "famílias fechadas": f'=COUNTIF({D.faixa("fam", so=1)},"{FECHADA}")',
        "metade do refino": f"=MAX(1,FLOOR({H['refino']}/2,1))",
        "terço do refino": f"=MAX(1,FLOOR({H['refino']}/3,1))",
        "dados da técnica máxima": f'=IFERROR(VLOOKUP({H["nível"]},{D.faixa("tm")},2,TRUE),0)',
        "montagem da técnica máxima": f'=IFERROR(VLOOKUP({H["nível"]},{D.faixa("tm")},3,TRUE),0)',
        "gasto da técnica máxima": "=" + "+".join(f"IF({k}=0,0,INDEX({PRECOS},{H['maior classe']},{k}))" for k in tm_cod),
        "fechada na técnica máxima": "=" + "+".join(tm_fech),
        "rota": f"={ROTA}",
        "equipamento": "=" + equip,
        "arma": f'=IF(AND({ROTA}>=3,{equip}="{EQUIPAMENTO[0]}"),1,0)',
        # o atributo de cada grupo de arma: o da tabela do livro; na Lâmina Longa, que acerta com os dois, o maior
        **{f"atributo do grupo {i + 1}": (f'=IF(OR({H["arma"]}=0,{_A(G["grupos_menu"][i], AM)}=""),"",IF(IFERROR(VLOOKUP({_A(G["grupos_menu"][i], AM)},{GRU},2,FALSE),0)=1,'
                                          f'IF(AND(IFERROR(VLOOKUP({_A(G["grupos_menu"][i], AM)},{GRU},3,FALSE),0)=1,N({F_("atr_Destreza")})>N({F_("atr_Força")})),"Destreza","Força"),"Destreza"))')
           for i in range(N_GRUPOS)},
        **{f"valor do grupo {i + 1}": f'=IF({H[f"atributo do grupo {i + 1}"]}="",0,IF({H[f"atributo do grupo {i + 1}"]}="Força",N({F_("atr_Força")}),N({F_("atr_Destreza")})))'
           for i in range(N_GRUPOS)},
        # quantos atributos diferentes os grupos escolhidos usam: um só, e a linha de cima da Técnica mostra o número
        "atributos dos grupos": "=" + "+".join(
            f'IF(AND({H[f"atributo do grupo {i + 1}"]}<>""' + "".join(f',{H[f"atributo do grupo {i + 1}"]}<>{H[f"atributo do grupo {j + 1}"]}' for j in range(i)) + '),1,0)'
            for i in range(N_GRUPOS)),
        "usos do estímulo": f'=IF({H["refino"]}>=10,2,1)&"× por cena"',
    }
    assert list(formulas) and set(formulas) == set(ordem_das_contas), set(formulas) ^ set(ordem_das_contas)
    D.prox = c_contas
    D.tabela("contas", ["contas da amaldiçoada", "valor da amaldiçoada"], [[k, formulas[k]] for k in ordem_das_contas])
    HA = {k: v.replace("$" + L(c_contas + 1) + "$", DA + "$" + L(c_contas + 1) + "$") for k, v in H.items()}     # com o nome da aba

    # --- uma linha por Passiva e por aptidão anotada: o que a carta mostra
    cP = D.prox
    pp = lambda k, n: f"${L(cP + k)}{n}"
    D.tabela("carta_passiva", ["carta de passiva", "passiva anotada", "classe passiva anotada", "nível que libera", "o que ela faz",
                               "classe passiva na carta", "custo na carta"],
             [[f"Passiva {i + 1}" + (" · Leque" if i >= PAGAS else ""),
               f'={_A(p["nome"], AM)}&""',
               (lambda n: f"=IFERROR(VLOOKUP({pp(1, n)},{PASS},2,FALSE),0)"),
               (lambda n: f"=IFERROR(VLOOKUP({pp(2, n)},{CPT},2,FALSE),0)"),
               (lambda n: f'=IFERROR(VLOOKUP({pp(1, n)},{PASS},3,FALSE),"")'),
               (lambda n: f'=IF({pp(2, n)}=0,"",IF({pp(3, n)}>{H["nível"]},"{T_ERRO} Nível "&{pp(3, n)},"CP "&{pp(2, n)}))'),
               ((lambda n, j=i - PAGAS + 1: f'=IF({pp(2, n)}=0,"",IF({j}>{H["escolhas de Leque"]},"{T_ERRO} Vaga","Grátis"))') if i >= PAGAS
                else (lambda n: f'=IF({pp(2, n)}=0,"",{pp(2, n)}&" esp.")'))]
              for i, p in enumerate(passivas_c)])
    APT = D.faixa("aptidoes")
    cA = D.prox
    aa = lambda k, n: f"${L(cA + k)}{n}"
    D.tabela("carta_aptidao", ["carta de aptidão", "aptidão anotada", "requisito na carta", "classe passiva na carta de aptidão",
                               "o refino escala na carta", "o que a aptidão anotada faz"],
             [[f"Aptidão {i + 1}", f'={_A(a["nome"], AM)}&""',
               (lambda n: f'=IF({aa(1, n)}="","","Requisito: "&IFERROR(VLOOKUP({aa(1, n)},{APT},2,FALSE),""))'),
               (lambda n: f'=IF({aa(1, n)}="","",IFERROR(IF(ISNUMBER(VLOOKUP({aa(1, n)},{APT},3,FALSE)),"CP "&VLOOKUP({aa(1, n)},{APT},3,FALSE),'
                          f'VLOOKUP({aa(1, n)},{APT},3,FALSE)),""))'),
               (lambda n: f'=IF({aa(1, n)}="","",IFERROR(VLOOKUP({aa(1, n)},{APT},4,FALSE),""))'),
               (lambda n: f'=IF({aa(1, n)}="","",IFERROR(VLOOKUP({aa(1, n)},{APT},5,FALSE),""))')]
              for i, a in enumerate(aptidoes_c)])
    # --- a Classe 0: uma linha por lugar
    cZ = D.prox
    zz = lambda k, n: f"${L(cZ + k)}{n}"
    cz = G["cols_zero"]
    zero_c = [{k: _a1(C(v[0]), G["zero_ini"] + i) for k, v in cz.items()} for i in range(N_ZERO)]
    abre_no = lambda i: next(n for n, q in zip(R["zero"]["niveis"], R["zero"]["quantos"]) if q >= i + 1)
    FORMAS5 = D.faixa("formas")
    D.tabela("carta_zero", ["classe 0 anotada", "forma da classe 0", "melhoria da classe 0", "restrição da classe 0", "linha da forma",
                            "dados dela", "dano na carta", "alcance na carta"],
             [[f"Classe 0 · {i + 1}", f'={_A(z_["forma"], AM)}&""', f'={_A(z_["mel"], AM)}&""', f'={_A(z_["res"], AM)}&""',
               (lambda n: f"=IFERROR(MATCH({zz(1, n)},{forma_col(0)},0),0)"),
               # a Melhoria Leve tira um dado; a Restrição Leve devolve o dado, e só paga a Melhoria
               (lambda n: f'={H["classe 0 dados"]}-IF({zz(2, n)}<>"",1,0)+IF(AND({zz(2, n)}<>"",{zz(3, n)}<>""),1,0)'),
               (lambda n, i=i: f'=IF({i + 1}>{H["classe 0 quantos"]},"Nível {abre_no(i)}",IF({zz(4, n)}=0,"",IF(INDEX({forma_col(6)},{zz(4, n)})>=2,"—",'
                               f'{zz(5, n)}&"d8 = "&FLOOR({zz(5, n)}*4.5,1))))'),
               (lambda n, i=i: f'=IF(OR({i + 1}>{H["classe 0 quantos"]},{zz(4, n)}=0),"",INDEX({ALC1},({zz(4, n)}-1)*3+1,'
                               f'1+IF(OR(AND({zz(2, n)}="Longe",INDEX({forma_col(9)},{zz(4, n)})<>2),AND({zz(2, n)}="Maior",INDEX({forma_col(9)},{zz(4, n)})>=2)),1,0))&'
                               f'INDEX({ALC2},({zz(4, n)}-1)*3+1,1+IF(AND({zz(2, n)}="Longe",INDEX({forma_col(10)},{zz(4, n)})=1),1,0)))')]
              for i, z_ in enumerate(zero_c)])
    # --- os saltos da linha 7: o Codigo.gs escreve a ligação de cada um no acabamento, com o número da aba
    cs = _cols_dos_saltos()
    # o nome do salto muda com a rota nas quatro seções que mudam de nome; o link que o Codigo.gs escreve cita a célula
    # do nome (a coluna "nome do salto"), e não o texto
    def curto_de(sid, curto):
        if sid == "feiticos":
            return f'={rotulo("feitiços")}'
        if sid == "aptidoes":
            return f'={rotulo("aptidões")}'
        if sid == "lib":                     # só a Técnica Marcial muda o nome (Ruptura); o salto curto fica "Liberação"
            return f'=IF({ROTA}>=3,{rotulo("liberação")},"{curto}")'
        if sid == "tm":
            return f'=IF({ROTA}=1,"{curto}",{rotulo("técnica máxima")})'
        return curto
    cS = D.prox
    D.tabela("saltos", ["salto", "caixa do salto", "alvo do salto", "nome do salto"],
             [[curto_de(sid, curto), fp._endereco(_a1(C(cs[i][0]), G["saltos"]), AM), fp._endereco(f"D{G['sec'][sid]}", AM),
               f"{DADOS_AM}!${L(cS)}${2 + i}"]          # o endereço com o nome da aba: o link do script cita a outra aba
              for i, (sid, _, curto) in enumerate(SECOES)])

    aba_dados = {
        "nome": DADOS_AM, "estado": "hidden", "linhas": D.linhas, "colunas": D.prox - 2,
        "colunas_larg": [[1, D.prox - 2, dados["colunas_larg"][0][2]]], "linhas_alt": [],
        "altura_padrao": dados.get("altura_padrao"), "grade": dados["grade"],
        "celulas": [[k, v[0], v[1]] for k, v in D.cel.items()],
        "mescladas": [], "menus": [], "condicional": [], "imagens": [],
        # as fórmulas que são a linha de cima copiada (a conta de feitiço tem cem por linha): o emitir_gs.py acha os
        # retângulos, o script grava a primeira linha de cada um e preenche o resto para baixo
        "abaixo": True,
    }
    return {"aba_dados": aba_dados, "G": G, "R": R, "D": D, "H": HA, "FEIT": FEIT, "lugares": lugares, "col": col,
            "rotulo": lambda k: rotulo(k, DA), "ROTA": DA + ROTA,
            "passivas_c": passivas_c, "aptidoes_c": aptidoes_c, "pactos_c": pactos_c, "zero_c": zero_c, "tm_mel": tm_mel}


def _cols_dos_saltos():
    return [("D", "D"), ("E", "E"), ("F", "F"), ("G", "H"), ("J", "J"), ("K", "K"), ("L", "L"), ("M", "N"), ("P", "P"), ("Q", "Q")]


# ---------------------------------------------------------------------------------------------
# A aba.
# ---------------------------------------------------------------------------------------------
NOTAS = {
    "nome_feitico": "Dê um nome ao feitiço: a ficha só calcula a carta e só conta o espaço de feitiço de quem tem nome.",
    "classe": "A Classe do feitiço. Ela define os pontos (3 × Classe), o PE e quantas Melhorias cabem.",
    "melhorias": "As Classes 1 e 2 aceitam 2 Melhorias, a 3 e a 4 aceitam 3, e da 5 em diante 4. A Forma não conta no limite. "
                 "Família Livre sai metade da Classe mais barata, e Família Fechada some do menu.",
    "restricoes": "Até duas. Restrição só paga peça: o que passar do que foi gasto some.",
    "ampliar": "O mesmo feitiço lançado numa Classe maior, até a maior que o nível liberou. A conta inteira é refeita com os "
               "números da Classe nova.",
    "atributo": "Escolhido na criação, e não muda. É o menu ATRIBUTO DE CONJURAÇÃO da FICHA: aqui ele aparece espelhado. Na "
                "Técnica Marcial de arma, é o atributo da arma usada na Kata: a linha da rota mostra o de cada grupo.",
    "rota_nome": "Vem da Origem escolhida na FICHA. O Fundamento é a rota das cinco Origens principais e da Restrição Celestial "
                 "pelo corpo; o Sem Técnica, a da sub-origem; a Técnica Marcial, a do Corpo Amaldiçoado (com energia) e a da "
                 "Restrição Celestial sem energia.",
    "rota_menu": "No Sem Técnica, a semente: a aptidão que vem aberta, sem os gates de nível e de refino, e é o assunto do "
                 "Fundamento. Ela conta como uma aptidão a mais. Na Técnica Marcial, o equipamento: três grupos de arma, ou uma "
                 "ferramenta, que declara se o golpe simples usa ela. No Fundamento, nada.",
    "grupos": "Na rota de arma, três das treze categorias, diferentes entre si. A CD e a conjuração de cada Kata usam o atributo "
              "da arma dela. A Lâmina Longa acerta com Força ou Destreza, e a ficha usa o maior.",
    "estimulo": "A Bênção de graça da Restrição Celestial sem energia: escolha uma perícia e um Teste de Resistência na criação. "
                "Cada uso dá vantagem numa rolagem de um dos dois; 1 por cena, 2 com a Lapidação em 10.",
    "conjuracao": "d20 + o atributo da técnica + maestria. Vem da FICHA.",
    "cd": "8 + o atributo da técnica + maestria. Vem da FICHA.",
    "regra": "Uma frase, verificável pela mesa, sem número. Todo feitiço tem de caber nela.",
    "selo": "O que você sempre faz para conjurar. Não custa nem devolve ponto. Na Técnica Marcial, o Selo é ter o equipamento em uso.",
    "passiva_livre": "De graça. Não rola dado, não muda número, não faz ninguém rolar. Na Técnica Marcial, o exemplo do livro é o Calo.",
    "regra_propria": "Só se a técnica impõe uma regra ao mundo. Uma frase, verificável, simétrica, sem dano direto e com limite por "
                     "cena. Não conta nas cinco Passivas pagas.",
    "cp_regra": "Na criação ela vem na Classe Passiva 1, de graça. A 2 libera no nível {n2} e custa 1 espaço; a 3 libera no nível "
                "{n3} e custa 2. Deixe em branco se a técnica não tem Regra Própria.",
    "familias": "O Fundamento tem {livres} Famílias Livres e {fechadas} Fechadas. As outras ficam Neutras.",
    "maior_classe": "Sobe nos níveis 1, 5, 9, 13, 17, 21 e 26. Vem da FICHA.",
    "espacos": "2 + metade do nível + um por marco alcançado. Pacto permanente que concede um espaço de feitiço soma aqui.",
    "leque": "Cada escolha de Leque no marco dá um feitiço a mais, que só pode ser feitiço, e uma Passiva. A escolha é marcada na "
             "FICHA, em Marco Escolhido.",
    "em_feiticos": "Os feitiços com nome. Classe 0 e Liberação Máxima não ocupam espaço.",
    "em_passivas": "Cada Passiva paga custa a Classe Passiva dela em espaços. A Regra Própria acima da Classe Passiva 1 entra aqui. "
                   "Passiva e Domínio só gastam espaço: o feitiço do Leque não paga nenhum dos dois.",
    "no_dominio": "A Expansão de Domínio custa 2, 3 ou 5 espaços, conforme o degrau.",
    "livres": "Os espaços, mais os feitiços do Leque, menos o que já foi gasto.",
    "indice": "Escolha a Classe e a fileira mostra os números dela. Em branco, mostra os da sua maior Classe.",
    "zero_indice": "Não muda com o menu: quantos feitiços de Classe 0 o nível dá, e os dados deles.",
    "zero_mel": "Cabe uma Melhoria Leve, e ela tira um dado.",
    "zero_res": "Cabe uma Restrição Leve. Ela devolve o dado que a Melhoria tirou, e só isso: Restrição só paga peça.",
    "tm_dano": "Fixo pela faixa de nível. Nenhum ponto compra mais dados.",
    "tm_pe": "{pe} × a sua maior Classe.",
    "tm_montagem": "Os pontos de montagem compram só a Forma e as Melhorias, nos preços da sua maior Classe. O que sobrar se perde.",
    "dom_refino": "Vem da FICHA. Sobe nos marcos.",
    "dom_pe": "{pe} × a sua maior Classe. Sem barreira, {pe_sem} ×.",
    "dom_dura": "Metade do refino, em rodadas. No mínimo uma.",
    "dom_raio": "{raio} m × refino. A incompleta para em {teto}, e sem barreira são {sem}.",
    "dom_desconto": "O desconto de PE de cada feitiço seu dentro do domínio: um terço do refino na incompleta, metade na completa, e "
                    "2 × maestria sem barreira. Nenhum feitiço custa menos de 1 PE.",
    "dom_barreira": "A vida da barreira por fora: {vida} × metade do refino. Por dentro ela não quebra.",
    "dom_acerto": "O que o domínio garante que acontece com quem está lá dentro. Uma frase, escrita com o mestre, cabendo na Regra.",
    "dom_efeito": "O que o domínio permite você fazer lá dentro que você não faria fora. Quase nunca é dano.",
    "dom_corrida": "Dois domínios sobrepostos: quem segura o domínio e toma dano testa Vigor. As falhas contam até metade da Essência.",
    "seu_texto": "Para a entrada Própria do menu, escreva aqui o texto dela, fechado com o mestre. Nas outras, é espaço para anotação.",
    "passiva_custo": "A Passiva paga custa a Classe Passiva dela em espaços de feitiço. A do Leque não custa nada, mas só existe "
                     "com a escolha de Leque no marco.",
    "apt_refino": "Começa em 1, e cada marco dá +1. Escolher Refino no marco dá mais +1. O teto é 10. Na Restrição Celestial sem "
                  "energia é a Lapidação, nos mesmos degraus.",
    "apt_compradas": "Cada escolha de Refino, marcada na FICHA, compra uma aptidão; com o refino já em 10, duas. A semente do Sem "
                     "Técnica dá uma a mais.",
    "apt_cobrir": "De graça no refino 1. Sem Traje e sem Revestimento, a proteção é 1/3 do refino + 1. Na Restrição Celestial sem "
                  "energia é a Defesa sem Armadura, com os mesmos números na Lapidação.",
    "apt_canalizar": "De graça no refino 1. 1d4 a mais na arma a cada 3 pontos de refino. No refino 10 os dados viram d6. Na "
                     "Restrição Celestial sem energia é o Estímulo Muscular, com o mesmo dano na arma, e só na arma.",
    "apt_reacao": "Como Reação, Redução de Dano de 1,5 × refino num golpe. Você fica sem proteção até o fim do seu próximo turno.",
    "permanentes": "Metade da Essência, para baixo, na campanha inteira. Temporário, Promessa e de restrição não têm teto.",
    "concede": "Só o pacto permanente concede. Um espaço de feitiço soma no Orçamento.",
}


class _Folha:
    def __init__(self, layout):
        self.layout, self.cel, self.mesclas, self.dentro = layout, {}, [], set()
        self.menus, self.notas, self._e = {}, {}, {}

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
                    raise SystemExit(f"ficha_amaldicoada: a caixa {coord} cai em cima de outra, em {_a1(c, l)}")
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
        self.menus.setdefault(formula, []).append(onde)


def _carta_de_feitico(f, tr, r0, c0, i, lib, com_nota):
    """a carta de um feitiço: o título, a descrição (que fecha), os números de mesa e a montagem (que fecha)"""
    D, R, FEIT = tr["D"], tr["R"], tr["FEIT"]
    a, b, c, d, e = (c0 + k for k in range(5))
    v = lambda k: f"={FEIT(k, i)}"
    nota = (lambda k: NOTAS[k]) if com_nota else (lambda k: None)
    cel = celulas_do_feitico(r0, c0)
    assert f.add("classe_carta", a, r0, a, r0, R["liberacao"]["classe_minima"] if lib else 1, nota("classe")) == cel["classe"]
    assert f.add("nome", b, r0, c, r0, None, nota("nome_feitico")) == cel["nome"]
    assert f.add("estado", d, r0, e, r0, v("estado")) == cel["estado"]
    f.add("rot", a, r0 + F_ROT, e, r0 + F_ROT, "COMO É")
    assert f.add("txt", a, r0 + F_TXT, e, r0 + F_TXT_FIM) == cel["como"]
    assert f.add("cel", a, r0 + F_N1, a, r0 + F_N1, FORMA_INICIAL) == cel["forma"]
    f.add("dano", b, r0 + F_N1, b, r0 + F_N1, v("dano"))
    f.add("dano", c, r0 + F_N1, c, r0 + F_N1, v("pe"))
    f.add("cel", d, r0 + F_N1, e, r0 + F_N1, v("resolve"))
    f.add("cel", a, r0 + F_N2, a, r0 + F_N2, v("acao"))
    f.add("peq", b, r0 + F_N2, e, r0 + F_N2, v("alcance"))
    f.add("rot", a, r0 + F_MEL, a, r0 + F_MEL + N_MEL - 1, "MELHORIAS", nota("melhorias"))
    for k in range(N_MEL):
        assert f.add("cel_esq", b, r0 + F_MEL + k, c, r0 + F_MEL + k) == cel["mel"][k]
        f.add("peq", d, r0 + F_MEL + k, e, r0 + F_MEL + k, v(f"pt{k + 1}"))
    f.add("rot", a, r0 + F_RES, a, r0 + F_RES + N_RES - 1, "RESTRIÇÕES", nota("restricoes"))
    for k in range(N_RES):
        assert f.add("cel_esq", b, r0 + F_RES + k, c, r0 + F_RES + k) == cel["res"][k]
        f.add("peq", d, r0 + F_RES + k, e, r0 + F_RES + k, v(f"dt{k + 1}"))
    f.add("rot", a, r0 + F_CONTA, a, r0 + F_CONTA, "CONTA")
    f.add("conta", b, r0 + F_CONTA, e, r0 + F_CONTA, v("conta"))
    f.add("rot", a, r0 + F_AMP, a, r0 + F_AMP + 1, "AMPLIAR", nota("ampliar"))
    f.add("conta", b, r0 + F_AMP, e, r0 + F_AMP + 1, v("ampliar"))
    f.add("rot", a, r0 + F_AV, a, r0 + F_AV + 1, "AVISOS")
    f.add("conta", b, r0 + F_AV, e, r0 + F_AV + 1, v("linha"))
    f.menu(cel["classe"], D.faixa("classe_lib" if lib else "classe", so=0, aba=DA))
    f.menu(cel["forma"], D.faixa("formas", so=13, aba=DA))
    f.menu(f"{cel['mel'][0]}:{cel['mel'][-1]}", D.faixa("pecas", so=6, aba=DA))
    f.menu(f"{cel['res'][0]}:{cel['res'][-1]}", D.faixa("res", so=0, aba=DA))


def aba(layout, tr):
    """a aba inteira, pronta para entrar em layout['abas']. Lê o cabeçalho e a lombada da FICHA do `layout`, que por
    isso tem de vir depois das correções de borda."""
    import cabecalho as cab
    R, G, H, D = tr["R"], tr["G"], tr["H"], tr["D"]
    ficha = ix._aba(layout, "FICHA")
    fcel = {r[0]: r for r in ficha["celulas"]}
    idx = ix.indice(layout)
    f = _Folha(layout)
    LIN = G["linhas"]
    FF = lambda k: _A(idx[k], "FICHA!")
    NIV, MAXC, REF, MAE = H["nível"], H["maior classe"], H["refino"], H["maestria"]
    ROT, ROTA = tr["rotulo"], tr["ROTA"]

    # --- o cabeçalho (linhas 1 a 7) e a lombada (colunas A e B), no molde da FICHA. As colunas daqui não são as de
    # lá: a tinta de cada linha vem de uma célula da FICHA que tem o mesmo papel (a lombada, o respiro, o miolo).
    vazio = cab._estilo(layout, "vazio")
    for lin in range(1, 8):
        for col in range(1, COLS + 1):
            fonte = "A" if col == 1 else "B" if col == 2 else "C" if col == 3 else "AU" if col == COLS else "AD"
            molde = fcel.get(f"{fonte}{lin}")
            if lin > cab.ULTIMA_LINHA and col > 2:
                continue                                        # da pincelada para baixo, só a lombada vem da FICHA
            if lin <= cab.ULTIMA_LINHA - 1 and col > 3:
                estilo = vazio                                  # o miolo do cabeçalho é só tinta
            elif molde is None:
                continue
            else:
                estilo = molde[2]
            f.cel[_a1(col, lin)] = (None, estilo)
            f.dentro.add((lin, col))

    def no_cabecalho(estilo, c1, l1, c2, l2, valor):
        for l in range(l1, l2 + 1):
            for c in range(C(c1), C(c2) + 1):
                f.dentro.discard((l, c))
                f.cel.pop(_a1(c, l), None)
        f.add(cab._estilo(layout, estilo), c1, l1, c2, l2, valor)
    no_cabecalho("marca", "D", 2, "D", 4, cab.MARCA)
    no_cabecalho("titulo", "E", 2, "H", 3, NOME)
    no_cabecalho("apoio", "E", 4, "H", 4, f'=DADOS!$F$1&" · {APOIO}"')
    no_cabecalho("nome", "J", 2, "T", 3, f"=FICHA!{cab.C_NOME[0]}")
    no_cabecalho("quem", "J", 4, "T", 4, f"=FICHA!{cab.C_QUEM[0]}")
    # a pincelada da linha 6: a mesma arte da FICHA, esticada na largura desta aba. Ela para antes das duas últimas
    # colunas, como lá.
    pincel = [dict(im) for im in ficha["imagens"] if im["lin"] <= 7]
    if len(pincel) != 1:
        raise SystemExit(f"a FICHA devia ter uma imagem no cabecalho, e tem {len(pincel)}")
    ult = COLS - 2
    pincel[0]["larg"] = sum(PX_COLUNAS[pincel[0]["col"] - 1:ult])
    f.add("canvas", pincel[0]["col"], 6, ult, 6)
    alturas = [list(a) for a in ficha["linhas_alt"] if a[0] <= 7]
    # a lombada: a tinta até a última linha, e os dois nomes nas mesmas linhas da FICHA
    lomb = {m.split(":")[0]: m for m in ficha["mescladas"] if ix._lc(m.split(":")[1])[1] <= 2}
    textos = {"FICHA DE REGISTRO": NOME}
    liso = [next(fcel[_a1(col, l)][2] for l in range(ficha["linhas"], 0, -1) if _a1(col, l) in fcel and fcel[_a1(col, l)][1] is None)
            for col in (1, 2)]
    for canto, m in lomb.items():
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
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

    def titulo(sec):
        """a faixa do título, de ponta a ponta. Até 01/10/2026 ela tinha um texto pequeno ao lado ("0 montados · cabem 3 no
        nível 2"); o Mizuki achou inútil ao usar a aba no Sheets, e saiu."""
        lin = G["sec"][sec]
        texto = next(t for s, t, _ in SECOES if s == sec)
        # 02/10/2026: as seções que mudam de nome com a rota, e o Domínio, que só o Fundamento tem
        por_rota = {"feiticos": "feitiços", "lib": "liberação", "tm": "técnica máxima"}
        if sec in por_rota:
            texto = f"=UPPER({ROT(por_rota[sec])})"
        elif sec == "aptidoes":
            texto = f'=UPPER({ROT("aptidões")}&" e "&{ROT("escala")})'
        elif sec == "dominio":
            texto = f'=IF({ROTA}=1,"{texto}","{texto} · ESTA ROTA NÃO TEM")'
        f.add("faixa", "D", lin, "T", lin + FX - 1, texto)

    # --- os saltos: um nome de seção por caixa, na linha 7. O acabamento do construir() liga cada um à seção.
    for (sid, _, curto), (c1, c2) in zip(SECOES, _cols_dos_saltos()):
        f.add("salto", c1, G["saltos"], c2, G["saltos"], curto)
    f.add("dica", "R", G["saltos"], "T", G["saltos"], "← Clique num nome para ir à seção")

    # --- a técnica
    titulo("tecnica")
    t = G["tec_caixas"]
    atributo = ix._Ficha(layout)
    atributo = atributo.abaixo(atributo.unico("ATRIBUTO DE CONJURAÇÃO"))
    f.caixa("D", "H", t, "NOME DA TÉCNICA")
    f.caixa("J", "K", t, "TIPO DE DANO")
    # na Técnica Marcial de arma, o atributo é o da arma da Kata: com os grupos num atributo só, a linha mostra ele e os
    # números dele; com dois, "Por grupo", e a linha da rota mostra os números de cada grupo
    ARMA, NAT = H["arma"], H["atributos dos grupos"]
    at = [H[f"atributo do grupo {i + 1}"] for i in range(N_GRUPOS)]
    vg = [H[f"valor do grupo {i + 1}"] for i in range(N_GRUPOS)]
    primeiro = lambda xs: f'IF({at[0]}<>"",{xs[0]},IF({at[1]}<>"",{xs[1]},{xs[2]}))'
    buff_conj, buff_cd = f'IFERROR(VALUE({FF("buff de conjuração")}&""),0)', f'IFERROR(VALUE({FF("buff de cd de feitiço")}&""),0)'
    conj_de = lambda v: f'"d20 + "&({MAE}+{v}+{buff_conj})'
    cd_de = lambda v: f'(8+{MAE}+{v}+{buff_cd})'
    pela_arma = lambda um, nenhum: f'IF({NAT}=0,"{nenhum}",IF({NAT}=1,{um},"Por grupo"))'
    f.caixa("L", "N", t, "ATRIBUTO DA TÉCNICA", f'=IF({ARMA}=1,{pela_arma(primeiro(at) + "&\", das armas\"", "Escolha os grupos")},FICHA!{_A(atributo)})',
            nota=NOTAS["atributo"])
    f.caixa("P", "Q", t, "CONJURAÇÃO", f'=IF({ARMA}=1,{pela_arma(conj_de(primeiro(vg)), "—")},{FF("conjuração")})', "num", NOTAS["conjuracao"])
    f.caixa("R", "T", t, "CD", f'=IF({ARMA}=1,{pela_arma(cd_de(primeiro(vg)), "—")},{FF("cd de feitiço")})', "num", NOTAS["cd"])
    # --- a linha da rota (02/10/2026): existe em toda ficha, e os rótulos dizem o que vale na rota escolhida
    t = G["rota_lin"]
    menu_rota = H["equipamento"]
    f.add("rot", "D", t, "H", t, "ROTA", NOTAS["rota_nome"])
    f.add("rot", "J", t, "N", t, f'=UPPER({ROT("peça da rota")})', NOTAS["rota_menu"])
    f.add("rot", "P", t, "T", t, f'=UPPER({ROT("o que ela dá")})')
    f.add("cel", "D", t + 1, "H", t + 1, f"={ROT('nome da rota')}")
    assert f.add("cel", "J", t + 1, "N", t + 1) == G["rota_menu"]
    f.menu(G["rota_menu"], D.faixa("menu_rota", so=0, aba=DA))
    f.add("cel", "P", t + 1, "T", t + 1,
          f'=IF({ROTA}=2,IF({menu_rota}="","","Aberta, sem os gates de nível e de refino · conta como uma aptidão a mais"),'
          f'IF({ROTA}=3,"Fere maldição: o Corpo Amaldiçoado tem Canalizar energia",IF({ROTA}=4,IF({menu_rota}="","",'
          f'IF({menu_rota}="{EQUIPAMENTO[2]}","Não fere maldição: só as Katas ferem","Fere maldição")),"—")))')
    for i, (c1, c2) in enumerate((("D", "H"), ("J", "N"), ("P", "T"))):
        f.add("rot", c1, t + 2, c2, t + 2, f'=IF({ARMA}=1,"GRUPO {i + 1}","—")', NOTAS["grupos"] if i == 0 else None)
        assert f.add("cel", c1, t + 3, c2, t + 3) == G["grupos_menu"][i]
        f.menu(G["grupos_menu"][i], D.faixa("grupos", so=3, aba=DA))
        assert f.add("cel", c1, t + 4, c2, t + 4,
                     f'=IF({at[i]}="","",{at[i]}&" · "&{conj_de(vg[i])}&" · CD "&{cd_de(vg[i])})') == G["grupos_conta"][i]
    t = G["regra"]
    f.add("rot", "D", t, "T", t, "REGRA", NOTAS["regra"])
    f.add("txt", "D", t + 1, "T", t + 2)
    t = G["descricao"]
    f.add("rot", "D", t, "K", t, "DESCRIÇÃO")
    f.add("txt", "D", t + 1, "K", t + 5)
    f.add("rot", "L", t, "T", t, f'=UPPER({ROT("selo")})', NOTAS["selo"])
    f.add("txt", "L", t + 1, "T", t + 2)
    f.add("rot", "L", t + 3, "T", t + 3, "PASSIVA LIVRE", NOTAS["passiva_livre"])
    f.add("txt", "L", t + 4, "T", t + 5)
    t = G["regra_propria"]
    cpn = R["cp"]
    f.add("rot", "D", t, "N", t, "REGRA PRÓPRIA", NOTAS["regra_propria"])
    f.add("txt", "D", t + 1, "N", t + 2)
    f.add("rot", "P", t, "Q", t, "CLASSE PASSIVA", NOTAS["cp_regra"].format(n2=cpn[2], n3=cpn[3]))
    assert f.add("cel", "P", t + 1, "Q", t + 2) == G["cp_regra"]
    f.menu(G["cp_regra"], D.faixa("cp", so=0, aba=DA))
    f.add("rot", "R", t, "T", t, "ESPAÇOS")
    cpr = H["classe passiva da regra própria"]
    assert f.add("cel", "R", t + 1, "T", t + 2,
                 f'=IF({cpr}=0,"—",IF(IFERROR(VLOOKUP({cpr},{D.faixa("cp", aba=DA)},2,FALSE),0)>{NIV},'
                 f'"{T_ERRO} Nível "&VLOOKUP({cpr},{D.faixa("cp", aba=DA)},2,FALSE),IF({cpr}>1,{cpr}-1,"De graça")))') == G["espacos_regra"]
    t = G["familias"]
    CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    n_livres, n_fechadas = CAT["fundamento"]["familias_livres"], CAT["fundamento"]["familias_fechadas"]
    for fam, (c1, c2) in zip(R["familias"], G["cols_fam"]):
        f.add("rot", c1, t, c2, t, fam.upper(), R["notas_familia"][fam][:1].upper() + R["notas_familia"][fam][1:] + ".")
        f.add("cel", c1, t + 1, c2, t + 1, NEUTRA)
        f.menu(_a1(C(c1), t + 1), D.faixa("estado", aba=DA))
    f.add("rot", "Q", t, "T", t, "LIVRES · FECHADAS", NOTAS["familias"].format(livres=n_livres, fechadas=n_fechadas))
    nl, nf = H["famílias livres"], H["famílias fechadas"]
    assert f.add("cel", "Q", t + 1, "T", t + 1,
                 f'=IF(OR({nl}<>{n_livres},{nf}<>{n_fechadas}),"{T_ERRO} ","")&{nl}&" de {n_livres} · "&{nf}&" de {n_fechadas}"') == G["resumo_familias"]

    # --- o orçamento e o índice de preços
    titulo("orcamento")
    t = G["orc_caixas"]
    sem = H["sem espaço"]
    caixas = [("MAIOR CLASSE", f"={MAXC}", "maior_classe"), ("ESPAÇOS", f"={H['espaços']}", "espacos"),
              ("DO LEQUE", f'="+"&{H["escolhas de Leque"]}', "leque"), (f'="EM "&UPPER({ROT("feitiços")})', f"={H['feitiços montados']}", "em_feiticos"),
              ("EM PASSIVAS", f'=IF({sem}=1,"{T_ERRO} ","")&{H["espaços em passivas"]}', "em_passivas"),
              ("NO DOMÍNIO", f'=IF({sem}=1,"{T_ERRO} ","")&{H["espaços no domínio"]}', "no_dominio"),
              ("LIVRES", f'=IF({H["livres"]}<0,"{T_ERRO} ","")&{H["livres"]}', "livres")]
    G["orcamento"] = {}
    for (rot, formula, nota), (c1, c2) in zip(caixas, G["cols_orc"]):
        G["orcamento"][nota] = f.caixa(c1, c2, t, rot, formula, "num", NOTAS[nota])
    t = G["indice"]
    ci = H["classe do índice"]
    PRE = D.faixa("classe", aba=DA)
    f.add("rot", "D", t, "D", t, "PREÇOS DA", NOTAS["indice"])
    assert f.add("classe", "D", t + 1, "D", t + 1, 1) == G["classe_do_indice"]
    f.menu(G["classe_do_indice"], D.faixa("classe", so=0, aba=DA))
    itens = [("PONTOS E PE", f"=3*{ci}"), ("LEVE", f"=INDEX({PRE},{ci},2)"), ("MÉDIA", f"=INDEX({PRE},{ci},3)"),
             ("PESADA", f"=INDEX({PRE},{ci},4)"), ("DEVOLUÇÃO MÁX.", f"=2*{ci}"), ("TETO DE DADOS", f"=4*{ci}"),
             ("MELHORIAS", f"=INDEX({PRE},{ci},8)"),
             ("CLASSE 0", f'={H["classe 0 quantos"]}&" feitiços grátis · "&{H["classe 0 dados"]}&"d8 cada"')]
    G["itens_do_indice"] = {}
    for (rot, formula), (c1, c2) in zip(itens, G["cols_indice"]):
        f.add("rot", c1, t, c2, t, rot, NOTAS["zero_indice"] if rot == "CLASSE 0" else None)
        G["itens_do_indice"][rot] = f.add("cel", c1, t + 1, c2, t + 1, formula)

    # --- os feitiços
    titulo("feiticos")
    for i, (r0, c0) in enumerate(G["feiticos"]):
        _carta_de_feitico(f, tr, r0, c0, i, False, i < 3)
    for lote in G["lotes_feitico"]:
        f.add("lote", "D", lote["faixa"], "T", lote["faixa"], f'=UPPER({ROT("feitiços")})&" {lote["de"]} A {lote["ate"]} · abra quando faltar lugar"')

    # --- a Classe 0
    titulo("zero")
    t, cz = G["zero_cab"], G["cols_zero"]
    for k, rot, nota in (("nome", "NOME", None), ("forma", "FORMA", None), ("mel", "MELHORIA LEVE", NOTAS["zero_mel"]),
                         ("res", "RESTRIÇÃO LEVE", NOTAS["zero_res"]), ("dano", "DANO", None), ("alcance", "ALCANCE", None)):
        f.add("rot", cz[k][0], t, cz[k][1], t, rot, nota)
    cZ = D.T["carta_zero"][0]
    for i, z in enumerate(tr["zero_c"]):
        lin = G["zero_ini"] + i
        f.add("cel_esq", *cz["nome"][:1], lin, cz["nome"][1], lin)
        f.add("cel", cz["forma"][0], lin, cz["forma"][1], lin, FORMA_INICIAL)
        f.add("cel_esq", cz["mel"][0], lin, cz["mel"][1], lin)
        f.add("cel_esq", cz["res"][0], lin, cz["res"][1], lin)
        f.add("dano", cz["dano"][0], lin, cz["dano"][1], lin, f"={_abs(cZ + 6, 2 + i, DA)}")
        f.add("peq", cz["alcance"][0], lin, cz["alcance"][1], lin, f"={_abs(cZ + 7, 2 + i, DA)}")
    faixa_z = lambda k: f"{cz[k][0]}{G['zero_ini']}:{cz[k][0]}{G['zero_fim']}"
    f.menu(faixa_z("forma"), D.faixa("formas", so=14, aba=DA))
    f.menu(faixa_z("mel"), D.faixa("pecas", so=7, aba=DA))
    f.menu(faixa_z("res"), D.faixa("res", so=4, aba=DA))

    # --- a Liberação Máxima
    titulo("lib")
    for i, (r0, c0) in enumerate(G["libs"]):
        _carta_de_feitico(f, tr, r0, c0, N_FEITICOS + i, True, True)

    # --- a Técnica Máxima
    tm = R["tm"]
    n_tm = tm["faixas"][0]["de"]
    dados_tm, mont_tm, gasto_tm, fech_tm = (H[k] for k in ("dados da técnica máxima", "montagem da técnica máxima",
                                                           "gasto da técnica máxima", "fechada na técnica máxima"))
    titulo("tm")
    t = G["tm_caixas"]
    assert f.caixa("D", "H", t, "NOME") == G["tm_nome"]
    assert f.caixa("J", "K", t, "FORMA", FORMA_INICIAL, "cel") == G["tm_forma"]
    f.menu(G["tm_forma"], D.faixa("formas", so=13, aba=DA))
    assert f.caixa("L", "N", t, "DANO", f'=IF({dados_tm}=0,"Nível {n_tm}",{dados_tm}&"d8 = "&FLOOR({dados_tm}*4.5,1))', "num",
                   NOTAS["tm_dano"]) == G["tm_dano"]
    assert f.caixa("P", "Q", t, "PE", f'=IF({dados_tm}=0,"—",{tm["pe_por_classe"]}*{MAXC})', "num",
                   NOTAS["tm_pe"].format(pe=tm["pe_por_classe"])) == G["tm_pe"]
    assert f.caixa("R", "T", t, "MONTAGEM", f'=IF({dados_tm}=0,"—",IF(OR({gasto_tm}>{mont_tm},{fech_tm}>0),"{T_ERRO} ","")&{gasto_tm}&" de "&{mont_tm}'
                   f'&IF({fech_tm}>0," · Família Fechada",""))', "num", NOTAS["tm_montagem"]) == G["tm_montagem"]
    t = G["tm_mel"]
    f.add("rot", "D", t, "H", t, "MELHORIAS · NOS PREÇOS DA MAIOR CLASSE")
    for (c1, c2), cel in zip(G["cols_tm_mel"], tr["tm_mel"]):
        assert f.add("cel_esq", c1, t, c2, t) == cel
        f.menu(cel, D.faixa("pecas", so=6, aba=DA))
    t = G["tm_como"]
    f.add("rot", "D", t, "T", t, "COMO É")
    f.add("txt", "D", t + 1, "T", t + 4)

    # --- a Expansão de Domínio
    dom = R["dominio"]
    titulo("dominio")
    t = G["dom_caixas"]
    deg, DOM = H["degrau do domínio"], D.faixa("dom", aba=DA)
    meio, terco = H["metade do refino"], H["terço do refino"]
    assert f.caixa("D", "E", t, "DEGRAU", None, "cel") == G["degrau"]
    f.menu(G["degrau"], D.faixa("dom", so=0, aba=DA))
    assert f.caixa("F", "H", t, "CUSTA", f'=IF(OR({ROTA}<>1,{deg}=""),"—",{H["espaços no domínio"]}&" espaços")', "cel") == G["dom_custa"]
    assert f.caixa("J", "N", t, "REQUISITO",
                   f'=IF({ROTA}<>1,"Só o Fundamento tem",IF({deg}="","—",IF(AND({NIV}>=IFERROR(VLOOKUP({deg},{DOM},3,FALSE),0),{REF}>=IFERROR(VLOOKUP({deg},{DOM},4,FALSE),0)),"",'
                   f'"{T_ERRO} ")&IFERROR(VLOOKUP({deg},{DOM},5,FALSE),"")))', "cel") == G["dom_requisito"]
    assert f.caixa("P", "Q", t, "REFINO", f'=IF({ROTA}<>1,"—",{REF})', "num", NOTAS["dom_refino"]) == G["dom_refino"]
    assert f.caixa("R", "T", t, "NA CORRIDA", f'=IF({ROTA}<>1,"—","Cai na "&MAX(1,FLOOR({H["essência"]}/2,1))&"ª falha")', "cel",
                   NOTAS["dom_corrida"]) == G["dom_corrida"]
    t = G["dom_tabela"]
    raio, teto_inc = dom["raio_por_refino"].replace(",", "."), dom["raio_da_incompleta"].split(" ")[0].replace(",", ".")
    virgula = lambda x: f'SUBSTITUTE({x}&" m",".",",")'
    nomes_d = [d["degrau"] for d in dom["degraus"]]
    cab_d = [("AO ABRIR", None), ("PE", NOTAS["dom_pe"].format(pe=dom["pe_por_classe"], pe_sem=dom["pe_por_classe_sem_barreira"])),
             ("DURA", NOTAS["dom_dura"]),
             ("RAIO", NOTAS["dom_raio"].format(raio=dom["raio_por_refino"], teto=dom["raio_da_incompleta"], sem=dom["raio_sem_barreira"])),
             ("FEITIÇO LÁ DENTRO", NOTAS["dom_desconto"]), ("BARREIRA", NOTAS["dom_barreira"].format(vida=dom["vida_da_barreira"])),
             ("O ACERTO", None)]
    dura = f'={meio}&IF({meio}>1," rodadas"," rodada")'
    sua = lambda cond: f'&IF({cond}," · a sua","")'
    linhas_d = [
        [f'="{nomes_d[0]}"' + sua(f'{deg}="{nomes_d[0]}"'), f"={dom['pe_por_classe']}*{MAXC}", dura,
         "=" + virgula(f"MIN({teto_inc},{raio}*{REF})"), f'="−"&{terco}&" PE"', "Não fecha", "Rola"],
        [f'="{nomes_d[1]}"' + sua(f'OR({deg}="{nomes_d[1]}",{deg}="{nomes_d[2]}")'), f"={dom['pe_por_classe']}*{MAXC}", dura,
         "=" + virgula(f"{raio}*{REF}"), f'="−"&{meio}&" PE"', f'={dom["vida_da_barreira"]}*{meio}&" de vida"', "Acontece"],
        [f'="Sem barreira"' + sua(f'{deg}="{nomes_d[2]}"'), f"={dom['pe_por_classe_sem_barreira']}*{MAXC}", dura,
         dom["raio_sem_barreira"], f'="−"&2*{MAE}&" PE"', "Não tem", "Acontece"],
    ]
    so_fund = lambda v: f'=IF({ROTA}<>1,"—",{v[1:]})' if isinstance(v, str) and v.startswith("=") else v
    linhas_d = [[so_fund(v) for v in linha] for linha in linhas_d]
    G["dominio_tabela"] = []
    for (rot, nota), (c1, c2) in zip(cab_d, G["cols_dom"]):
        f.add("rot", c1, t, c2, t, rot, nota)
    for j, linha in enumerate(linhas_d):
        G["dominio_tabela"].append([f.add("cel_esq" if k == 0 else "cel", c1, t + 1 + j, c2, t + 1 + j, v)
                                    for k, (v, (c1, c2)) in enumerate(zip(linha, G["cols_dom"]))])
    f.add("rot", "P", t, "T", t, "NOME DO DOMÍNIO")
    assert f.add("val", "P", t + 1, "T", t + 3) == G["dom_nome"]
    t = G["dom_textos"]
    f.add("rot", "D", t, "K", t, "ACERTO", NOTAS["dom_acerto"])
    f.add("txt", "D", t + 1, "K", t + 3)
    f.add("rot", "L", t, "T", t, "EFEITO", NOTAS["dom_efeito"])
    f.add("txt", "L", t + 1, "T", t + 3)
    t = G["dom_como"]
    f.add("rot", "D", t, "T", t, "COMO É POR DENTRO")
    f.add("txt", "D", t + 1, "T", t + 4)

    # --- as Passivas
    titulo("passivas")
    cP = D.T["carta_passiva"][0]
    for i, ((r0, c0), cel) in enumerate(zip(G["passivas"], tr["passivas_c"])):
        a, b, c, d, e = (c0 + k for k in range(5))
        assert f.add("nome_menu", a, r0, b, r0) == cel["nome"]
        assert f.add("peq", c, r0, c, r0, f"={_abs(cP + 5, 2 + i, DA)}") == cel["cp"]
        assert f.add("peq", d, r0, e, r0, f"={_abs(cP + 6, 2 + i, DA)}", NOTAS["passiva_custo"] if i in (0, PAGAS) else None) == cel["custo"]
        f.add("rot", a, r0 + 1, e, r0 + 1, "O QUE FAZ")
        assert f.add("txt", a, r0 + 2, e, r0 + 4, f"={_abs(cP + 4, 2 + i, DA)}") == cel["faz"]
        f.add("rot", a, r0 + 5, a, r0 + 6, "SEU TEXTO", NOTAS["seu_texto"] if i == 0 else None)
        assert f.add("txt", b, r0 + 5, e, r0 + 6) == cel["texto"]
        f.menu(cel["nome"], D.faixa("passivas", so=5, aba=DA))
    f.add("lote", "D", G["lote_leque"]["faixa"], "T", G["lote_leque"]["faixa"],
          "PASSIVAS DO LEQUE · uma por escolha de Leque, sem custar espaço")

    # --- as aptidões e o refino
    titulo("aptidoes")
    t = G["apt_caixas"]
    anot, comp = H["aptidões anotadas"], H["aptidões compráveis"]
    cx = G["cols_apt"]
    assert f.caixa(*cx[0], t, f'=UPPER({ROT("escala")})', f"={REF}", "num", NOTAS["apt_refino"]) == G["apt_refino"]
    assert f.caixa(*cx[1], t, "COMPRADAS", f'=IF({anot}>{comp},"{T_ERRO} ","")&{anot}&" de "&{comp}', "num", NOTAS["apt_compradas"]) == G["apt_compradas"]
    G["apt_cobrir"] = f.caixa(*cx[2], t, f'=UPPER({ROT("graça 1")})', f'="Proteção "&(FLOOR({REF}/3,1)+1)', "val", NOTAS["apt_cobrir"])
    G["apt_canalizar"] = f.caixa(*cx[3], t, f'=UPPER({ROT("graça 2")})',
                                 f'="+"&IF({REF}>=9,4,IF({REF}>=6,3,IF({REF}>=3,2,1)))&IF({REF}>=10,"d6","d4")&" na arma"', "val", NOTAS["apt_canalizar"])
    G["apt_reacao"] = f.caixa(*cx[4], t, f'=UPPER({ROT("reação")})', f'="RD "&FLOOR(1.5*{REF},1)&" por 2 PE"', "val", NOTAS["apt_reacao"])
    # a linha do Estímulo Muscular: a perícia e o Teste de Resistência escolhidos na criação, e os usos
    t = G["estimulo"]
    sem_en = lambda txt: f'=IF({ROTA}=4,"{txt}","—")'
    f.add("rot", "D", t, "H", t, sem_en("ESTÍMULO: PERÍCIA"), NOTAS["estimulo"])
    f.add("rot", "J", t, "N", t, sem_en("ESTÍMULO: TESTE DE RESISTÊNCIA"))
    f.add("rot", "P", t, "T", t, sem_en("ESTÍMULO: USOS"))
    assert f.add("cel", "D", t + 1, "H", t + 1) == G["estimulo_pericia"]
    assert f.add("cel", "J", t + 1, "N", t + 1) == G["estimulo_teste"]
    assert f.add("cel", "P", t + 1, "T", t + 1, f'=IF({ROTA}=4,{H["usos do estímulo"]},"—")') == G["estimulo_usos"]
    n_per = len(CAT["pericias"])
    n_tr = len([k for k, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)])
    f.menu(G["estimulo_pericia"], f"DADOS!$B$4:$B${3 + n_per}")
    f.menu(G["estimulo_teste"], f"DADOS!$J$4:$J${3 + n_tr}")
    cA = D.T["carta_aptidao"][0]
    for i, ((r0, c0), cel) in enumerate(zip(G["aptidoes"], tr["aptidoes_c"])):
        a, b, c, d, e = (c0 + k for k in range(5))
        assert f.add("nome_menu", a, r0, c, r0) == cel["nome"]
        assert f.add("peq", d, r0, e, r0, f"={_abs(cA + 3, 2 + i, DA)}") == cel["cp"]
        # o requisito em duas linhas: o mais comprido do livro tem 120 letras
        assert f.add("peq_txt", a, r0 + 1, e, r0 + 2, f"={_abs(cA + 2, 2 + i, DA)}") == cel["requisito"]
        f.add("rot", a, r0 + 3, e, r0 + 3, "O QUE FAZ")
        assert f.add("txt_peq", a, r0 + 4, e, r0 + 3 + TXT_APT, f"={_abs(cA + 5, 2 + i, DA)}") == cel["faz"]
        f.add("rot", a, r0 + 4 + TXT_APT, a, r0 + 4 + TXT_APT, f'=UPPER({ROT("o que escala")})')
        assert f.add("peq_esq", b, r0 + 4 + TXT_APT, e, r0 + 4 + TXT_APT, f"={_abs(cA + 4, 2 + i, DA)}") == cel["escala"]
        f.add("rot", a, r0 + 5 + TXT_APT, a, r0 + 6 + TXT_APT, "SEU TEXTO", NOTAS["seu_texto"] if i == 0 else None)
        assert f.add("txt", b, r0 + 5 + TXT_APT, e, r0 + 6 + TXT_APT) == cel["texto"]
        f.menu(cel["nome"], D.faixa("aptidoes", so=5, aba=DA))
    f.add("lote", "D", G["lote_apt"]["faixa"], "T", G["lote_apt"]["faixa"],
          f'=UPPER({ROT("aptidões")})&" {APT_LOTE + 1} A {N_APT} · abra quando faltar lugar"')

    # --- os pactos
    titulo("pactos")
    t = G["pac_caixas"]
    perm, teto = H["pactos permanentes"], H["teto de pactos"]
    assert f.caixa("D", "E", t, "PERMANENTES", f'=IF({perm}>{teto},"{T_ERRO} ","")&{perm}&" de "&{teto}', "num", NOTAS["permanentes"]) == G["pac_permanentes"]
    f.add("rot", "F", t, "T", t, "COMO O PACTO SE FECHA")
    f.add("conta", "F", t + 1, "T", t + 2,
          " ".join(f"{p['forma'][:1].upper()}{p['forma'][1:]}: {p['quando']}." for p in R["pactos"]["formas"]))
    for i, (r, cel) in enumerate(zip(G["pactos"], tr["pactos_c"])):
        f.add("rot", "D", r, "D", r, f"PACTO {i + 1}")
        assert f.add("nome", "E", r, "K", r) == cel["nome"]
        assert f.add("cel", "L", r, "N", r) == cel["forma"]
        assert f.add("cel", "P", r, "T", r, None, NOTAS["concede"] if i == 0 else None) == cel["concede"]
        f.menu(cel["forma"], D.faixa("pacto_forma", so=0, aba=DA))
        f.menu(cel["concede"], D.faixa("pacto_concede", so=0, aba=DA))
        f.add("rot", "D", r + 1, "K", r + 1, "O QUE EU DOU")
        f.add("rot", "L", r + 1, "T", r + 1, "O QUE EU RECEBO")
        assert f.add("txt", "D", r + 2, "K", r + 5) == cel["dou"]
        assert f.add("txt", "L", r + 2, "T", r + 5) == cel["recebo"]
        f.add("rot", "D", r + 6, "T", r + 6, "CLÁUSULA, COM QUEM FOI FECHADO E O QUE ACONTECE SE QUEBRAR")
        assert f.add("txt", "D", r + 7, "T", r + 8) == cel["clausula"]

    # --- a conta de cada caixa calculada mora na DADOS_AM, e a caixa só aponta para ela (01/10/2026). O Mizuki digitou um
    # número por cima do NO DOMÍNIO, a conta sumiu sem aviso, e nada mais lia a caixa. Esta aba não tem trava de fórmula
    # (trava em linha de grupo faz o Sheets avisar quem clica no +), então quem devolve a conta é o onEdit do Codigo.gs,
    # que conhece a fórmula de cada caixa pelo ABAS. Ele só consegue gravar o que vale em qualquer idioma de planilha: a
    # referência pura, sem vírgula entre argumentos e sem decimal. Por isso toda conta sai daqui.
    com_conta = [(coord, v) for coord, (v, _) in f.cel.items()
                 if isinstance(v, str) and v.startswith("=") and not REFERENCIA_PURA.fullmatch(v) and ix._lc(coord)[0] >= G["saltos"]]
    c_mostra = D.tabela("mostra", ["caixa calculada", "o que a caixa mostra"], [[coord, v] for coord, v in com_conta])
    for i, (coord, _) in enumerate(com_conta):
        f.cel[coord] = (f"={_abs(c_mostra + 1, 2 + i, DA)}", f.cel[coord][1])
    tr["aba_dados"].update({"linhas": D.linhas, "colunas": D.prox - 2, "celulas": [[k, v[0], v[1]] for k, v in D.cel.items()]})

    # --- o resto da folha é fundo, pintado célula a célula: é ele que diz ao script qual é a cor de base
    canvas = f.estilo("canvas")
    for lin in range(1, LIN + 1):
        for col in range(1, COLS + 1):
            if (lin, col) not in f.dentro:
                f.cel[_a1(col, lin)] = (None, canvas)

    # --- os grupos de linhas: a seção, o lote e, dentro deles, o que fecha em cada fileira de cartas
    grupos = [[G["sec"][s] + FX, G["fim"][s], s in NASCE_FECHADA] for s, _, _ in SECOES]
    grupos += [[l["ini"], l["fim"], True] for l in G["lotes_feitico"] + [G["lote_leque"], G["lote_apt"]]]
    fileiras = lambda cartas: sorted({r0 for r0, _ in cartas})
    for k, r0 in enumerate(fileiras(G["feiticos"]) + fileiras(G["libs"])):
        grupos += [[r0 + F_ROT, r0 + F_TXT_FIM, k > 0], [r0 + F_MEL, r0 + ALT_F - 1, k > 0]]
    grupos += [[r0 + 1, r0 + ALT_P - 1, k > 0] for k, r0 in enumerate(fileiras(G["passivas"]))]
    grupos += [[r0 + 3, r0 + ALT_A - 1, k > 0] for k, r0 in enumerate(fileiras(G["aptidoes"]))]
    grupos += [[r + 1, r + 8, k > 0] for k, r in enumerate(G["pactos"])]
    # dois grupos vizinhos na mesma profundidade virariam um só no Sheets: tem de haver uma linha entre eles
    for a_ in grupos:
        for b_ in grupos:
            if a_ is not b_ and b_[0] == a_[1] + 1:
                raise SystemExit(f"ficha_amaldicoada: os grupos {a_[:2]} e {b_[:2]} estao colados")

    # --- as fileiras de cartas que são cópia da primeira: o script mescla a primeira e copia o formato para as outras
    def copias(cartas, altura):
        linhas = fileiras(cartas)
        cheias = [r for r in linhas if sum(1 for r0, _ in cartas if r0 == r) == 3]
        # só as colunas das cartas: a lombada tem mesclagens que atravessam as fileiras, e o Sheets não copia meia mesclagem
        return [cheias[0], cheias[0] + altura - 1, cheias[1:], C1, CN] if len(cheias) > 1 else None
    copia = [c for c in (copias(G["feiticos"] + G["libs"], ALT_F), copias(G["passivas"], ALT_P), copias(G["aptidoes"], ALT_A)) if c]

    corpo = f"D{G['saltos'] + 2}:T{LIN}"
    condicional = [{"faixas": [corpo], "contem": T_ERRO, "fundo": VERMELHO, "fonte": BRANCO},
                   {"faixas": [corpo], "comeca": T_AVISO, "fonte": AMBAR},
                   {"faixas": [corpo], "contem": SEM_NOME, "fonte": AMBAR}]
    base = ficha["colunas_larg"][0][2]
    return {
        "nome": NOME, "estado": "visible", "linhas": LIN, "colunas": COLS,
        # a coluna de 28 px na largura da FICHA; as outras, pela conta do Sheets (pixel = 8 x largura - 1)
        "colunas_larg": [[i + 1, i + 1, base if px == PX_FINA else (px + 1) / 8] for i, px in enumerate(PX_COLUNAS)],
        "linhas_alt": alturas, "altura_padrao": ficha.get("altura_padrao"), "grade": False,
        "celulas": [[k, v[0], v[1]] for k, v in f.cel.items()],
        "mescladas": f.mesclas,
        "menus": [{"onde": " ".join(onde), "tipo": "list", "formula": formula, "vazio_ok": True, "mostra_seta": True}
                  for formula, onde in f.menus.items()],
        "condicional": [], "imagens": pincel, "notas": f.notas,
        "grupos": {"linhas": grupos, "colunas": []},
        "condicional_gs": condicional,
        # nenhuma fórmula desta aba é travada: quase todas moram em linha de grupo, e trava em linha de grupo faz o
        # Sheets avisar quem clica no + (o achado do painel de XP da FICHA PESSOAL)
        "protegidas": [],
        "copias": copia,
        # menus e caixas de seleção numa gravação só: são mais de duzentas faixas
        "validacao_em_matriz": True,
    }


def aplica(layout, tr):
    """põe a FICHA AMALDIÇOADA depois da FICHA e a DADOS_AM depois da DADOS. Devolve a aba, para o monta.py contar."""
    folha = aba(layout, tr)
    layout["abas"].insert(next(i for i, a in enumerate(layout["abas"]) if a["nome"] == "FICHA") + 1, folha)
    layout["abas"].insert(next(i for i, a in enumerate(layout["abas"]) if a["nome"] == "DADOS") + 1, tr["aba_dados"])
    return folha
