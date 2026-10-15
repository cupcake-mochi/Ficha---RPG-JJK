# -*- coding: utf-8 -*-
"""B47: bônus e mudanças, na CONFIGURAÇÃO fixa em Mizuki Escuro.

Somar acumula com a conta e com o Buff/Debuff existente. Trocar por fixa o
resultado final (decisão do Mizuki nesta rodada), inclusive em zero. Duas
trocas na mesma caixa são conflito; entrada ligada inválida não vira zero.
As escolhas e os diagnósticos são publicados na ANALISE, formato 3.
"""
import json
import os
import re
from openpyxl.formula import Tokenizer
import indice_ficha as ix

NOME, DADOS = "CONFIGURAÇÃO", "DADOS_CONFIG"
INICIO, QUANTIDADE = 11, 30
FIM = INICIO + QUANTIDADE - 1
COLUNAS = ("B", "C", "D", "E", "F", "G")
CAMPOS = ("ligado", "caixa", "como", "valor", "tipo_de_fonte", "fonte")
FONTES = ("Pacto", "Origem", "Origem custom", "Item", "Técnica", "Decisão do mestre")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CF = "'CONFIGURAÇÃO'!"


def ref(aba, coord):
    l, c = ix._lc(coord)
    return f"'{aba}'!${ix._letras(c)}${l}"


def qualifica(formula, aba):
    """Move uma fórmula para a aba de apoio sem mudar suas referências locais."""
    itens = Tokenizer(formula).items
    return "=" + "".join(
        f"'{aba}'!{t.value}" if t.type == "OPERAND" and t.subtype == "RANGE"
        and "!" not in t.value and re.fullmatch(r"\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?", t.value)
        else t.value for t in itens)


def apresentacao(formula):
    corpo = formula[1:]
    if corpo.startswith('"d20 + "&'):
        return corpo[len('"d20 + "&'):], "d20"
    if corpo.endswith('&" m"'):
        return corpo[:-len('&" m"')], "metros"
    return corpo, "numero"


def envolve(formula, linha):
    """Preserva a fórmula antiga e suas referências; acrescenta só a configuração."""
    base, modo = apresentacao(formula)
    b, c, d, e = (f"{DADOS}!${col}${linha}" for col in "BCDE")
    mostra = lambda v: f'"d20 + "&({v})' if modo == "d20" else f'({v})&" m"' if modo == "metros" else v
    soma = mostra(f'IF(({base})="","",({base})+{b})')
    return f'=IF({e}<>"",NA(),IF({c}=1,{mostra(d)},IF({b}=0,{formula[1:]},{soma})))'


def anterior(formula):
    """Lê e valida o envoltório para os testes antigos continuarem cobrando a conta-base.

    Não aceita uma fórmula adulterada só porque ela contém o marcador.
    O comportamento com efeitos é recalculado na regressão de configuração.
    """
    if not isinstance(formula, str) or not formula.startswith("=IF(DADOS_CONFIG!"):
        return formula
    itens = Tokenizer(formula).items
    for i, t in enumerate(itens[:-4]):
        m = re.fullmatch(r"DADOS_CONFIG!\$B\$(\d+)", t.value)
        if not m or [x.value for x in itens[i + 1:i + 4]] != ["=", "0", ","]:
            continue
        nivel, corpo = 0, []
        for x in itens[i + 4:]:
            if x.type == "SEP" and x.subtype == "ARG" and nivel == 0:
                break
            if x.subtype == "OPEN": nivel += 1
            if x.subtype == "CLOSE": nivel -= 1
            corpo.append(x.value)
        original = "=" + "".join(corpo)
        if envolve(original, int(m.group(1))) != formula:
            raise ValueError("envoltório dos bônus e mudanças adulterado")
        return original
    raise ValueError("fórmula da configuração sem conta-base válida")


def alvos(layout, pessoal):
    idx = ix.indice(layout)
    out = []
    for rot, chave in (("Vida máxima", "vida_max"), ("PE máximo", "energia_max"),
                       ("Integridade máxima", "integridade_max"), ("Defesa", "defesa"),
                       ("Proteção", "proteção"), ("Iniciativa", "iniciativa"),
                       ("CD de feitiço", "cd de feitiço"), ("Conjuração", "conjuração"),
                       ("Corpo a corpo", "corpo a corpo"), ("À distância", "à distância"),
                       ("Deslocamento", "deslocamento")):
        out.append((rot, "FICHA", idx[chave]))
    # O limite pertence à conta da carga; todas as punições leem esta célula.
    h = pessoal["H"]["limite de carga"].split("!")[-1].replace("$", "")
    out.append(("Limite de carga", "DADOS", h))
    cat = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    f = ix._Ficha(layout)
    for grupo, nomes in (("Perícia", cat["pericias"]), ("Ofício", cat["oficios"]),
                         ("TR", [n for n, v in cat["testes_de_resistencia"].items() if isinstance(v, dict)])):
        for nome in nomes:
            rotulo = f.unico(nome)
            linha, col = ix._lc(rotulo)
            candidatos = [(ix._lc(c)[1], c) for c, v in f.val.items()
                          if ix._lc(c)[0] == linha and ix._lc(c)[1] > col
                          and isinstance(v, str) and v.startswith("=")]
            if not candidatos:
                raise ValueError(f"sem resultado para {grupo} · {nome}")
            out.append((f"{grupo} · {nome}", "FICHA", min(candidatos)[1]))
    return out


def trocas(layout, pessoal):
    destinos = alvos(layout, pessoal)
    celulas, antes = {}, {}
    for linha, (nome, aba, coord) in enumerate(destinos, 2):
        valor = next(r[1] for r in ix._aba(layout, aba)["celulas"] if r[0] == coord)
        if not isinstance(valor, str) or not valor.startswith("="):
            raise ValueError(f"{aba}!{coord}: o alvo não é calculado")
        antes.setdefault(aba, {})[coord] = valor
        celulas.setdefault(aba, {})[coord] = envolve(valor, linha)
    return {"alvos": destinos, "antes": antes, "celulas": celulas}


def _aba(nome, linhas, colunas):
    return {"nome": nome, "estado": "visible" if nome == NOME else "hidden",
            "linhas": linhas, "colunas": colunas, "grade": False, "celulas": [],
            "mescladas": [], "menus": [], "condicional": [], "imagens": [],
            "colunas_larg": [], "linhas_alt": [], "notas": {}, "altura_padrao": 18,
            "grupos": {"linhas": [], "colunas": []}}


def abas(layout, tr):
    """Dois painéis: entradas à esquerda, efeitos por caixa à direita."""
    n = max(FIM + 4, len(tr["alvos"]) + 13)
    a, h = _aba(NOME, n, 13), _aba(DADOS, max(len(tr["alvos"]), QUANTIDADE) + 3, 16)
    # Os papéis vêm do Mizuki Escuro do Codigo.gs, a fonte da paleta.
    codigo = open(os.path.join(RAIZ, "apps-script", "Codigo.gs"), encoding="utf-8").read()
    cores = json.loads(re.search(r"var PALETAS = (\{.*?\n\});\n", codigo, re.S).group(1))["Mizuki"]["escuro"]
    estilos = {}
    for nome, fonte, tam, tinta, fundo, alinha, wrap in (
        ("fundo", "Roboto", 10, "texto", "fundo", "left", False),
        ("titulo", "Oswald", 18, "acento", "papel", "left", False),
        ("secao", "Oswald", 12, "texto", "painel_alto", "left", False),
        ("rotulo", "Oswald", 10, "texto", "painel_alto", "center", True),
        ("entrada", "Roboto", 10, "texto", "painel", "left", True),
        ("numero", "Roboto", 10, "texto", "painel", "right", False),
        ("caixa", "Roboto", 10, "texto", "painel", "center", False),
        ("calc", "Roboto", 10, "texto", "papel", "left", True),
        ("nota", "Roboto", 10, "texto_fraco", "fundo", "left", True)):
        e = [[fonte, tam, cores[tinta].lstrip("#"), False, False], cores[fundo].lstrip("#"),
             {lado: ["thin", cores["regua"].lstrip("#")]
              for lado in ("top", "bottom", "left", "right")}
             if nome in ("rotulo", "entrada", "numero", "caixa", "calc") else None,
             [alinha, "center", wrap, 0], None]
        if e not in layout["estilos"]:
            layout["estilos"].append(e)
        estilos[nome] = layout["estilos"].index(e)
    a.update(padrao=["Roboto", 10, "#" + cores["texto"].lstrip("#")],
             fundo_base="#" + cores["fundo"].lstrip("#"), paleta_fixa=True)
    for r in range(1, n + 1):
        for c in range(1, 14):
            a["celulas"].append([f"{ix._letras(c)}{r}", None, estilos["fundo"]])
    def poe(coord, valor, estilo="entrada", mescla=None, nota=None):
        a["celulas"].append([coord, valor, estilos[estilo]])
        if mescla:
            a["mescladas"].append(coord + ":" + mescla)
        if nota:
            a["notas"][coord] = nota
    larguras = (24, 60, 186, 95, 60, 115, 155, 24, 180, 80, 80, 205, 24)
    a["colunas_larg"] = [[c, c, (px + 1) / 8] for c, px in enumerate(larguras, 1)]
    a["linhas_alt"] = [[r, 31.5] for r in range(INICIO, n + 1)] + [[1, 12], [2, 24], [3, 12], [4, 9], [5, 18], [6, 12], [7, 15.75], [8, 15.75], [9, 18], [10, 24]]
    a["congeladas"] = 10
    poe("B2", "CONFIGURAÇÃO", "titulo", "L3")
    poe("B5", "Somar acumula com a conta e o Buff/Debuff. Trocar por fixa o resultado final, inclusive zero.", "nota", "G6")
    poe("I5", "Mizuki Escuro · paleta fixa", "nota", "L5")
    poe("B7", f'=COUNTIFS(B{INICIO}:B{FIM},TRUE)&" ligados de {QUANTIDADE}"', "nota", "G7")
    poe("I7", f'=IF({DADOS}!$P$2="","","⚠ "&{DADOS}!$P$2)', "calc", "L8")
    poe("B9", "BÔNUS E MUDANÇAS", "secao", "G9")
    poe("I9", "RESULTADOS", "secao", "L9")
    notas = ("Marque para aplicar. Desmarcado, o efeito fica guardado.",
             "Escolha a caixa afetada. Os resultados à direita mostram todas as opções.",
             "Somar acumula. Trocar por substitui o valor final e todos os bônus da caixa. Duas trocas ligadas na mesma caixa são conflito.",
             "Número, sem unidade. Negativo reduz; zero é válido. Para deslocamento, informe metros (ex.: 4,5).",
             "Tipo da coisa que concede a mudança.",
             "Nome da habilidade, pacto, item ou decisão que justifica a mudança. Obrigatório quando ligado; o mestre confere pelo bot.")
    for col, rot, nota in zip(COLUNAS, ("LIGADO", "CAIXA", "COMO", "VALOR", "TIPO DE FONTE", "FONTE"), notas):
        poe(col + "10", rot, "rotulo", nota=nota)
    for col, rot in zip("IJKL", ("CAIXA", "SOMA", "TROCA", "EM USO")):
        poe(col + "10", rot, "rotulo")
    for r in range(INICIO, FIM + 1):
        for col in COLUNAS:
            poe(f"{col}{r}", False if col == "B" else None,
                "caixa" if col == "B" else "numero" if col == "E" else "entrada")
    for linha, (nome, aba, coord) in enumerate(tr["alvos"], 2):
        r = INICIO + linha - 2
        poe(f"I{r}", nome, "calc")
        poe(f"J{r}", f"={DADOS}!B{linha}", "numero")
        poe(f"K{r}", f'=IF({DADOS}!C{linha}=1,{DADOS}!D{linha},"")', "numero")
        poe(f"L{r}", f'=IF({DADOS}!E{linha}<>"","⚠ "&{DADOS}!E{linha},{ref(aba, coord)})', "calc")
    a["menus"] = [
        {"tipo": "list", "formula": f"{DADOS}!$A$2:$A${len(tr['alvos']) + 1}", "onde": f"C{INICIO}:C{FIM}", "vazio_ok": True, "mostra_seta": True},
        {"tipo": "list", "formula": '"somar,trocar por"', "onde": f"D{INICIO}:D{FIM}", "vazio_ok": True, "mostra_seta": True},
        {"tipo": "list", "formula": f"{DADOS}!$O$2:$O${len(FONTES) + 1}", "onde": f"F{INICIO}:F{FIM}", "vazio_ok": True, "mostra_seta": True}]
    a["condicional"] = [{"tipo": "expression", "onde": f"B{INICIO}:G{FIM}",
                          "formula": [f'AND($B{INICIO}=TRUE,OR($C{INICIO}="",$D{INICIO}="",NOT(ISNUMBER($E{INICIO})),$F{INICIO}="",$G{INICIO}=""))'],
                          "cor_texto": "FFFFFF", "fundo": "C2334D"}]
    # As caixas numéricas são exportadas pelo mecanismo de formatos existente.
    a["grupos"]["linhas"] = [[INICIO + 15, FIM, False]]
    for j, fonte in enumerate(FONTES, 2):
        h["celulas"].append([f"O{j}", fonte, None])
    for col, rot in zip("ABCDEFGH", ("caixa", "soma", "trocas", "valor da troca", "problema", "conta anterior", "base numérica", "em uso")):
        h["celulas"].append([col + "1", rot, None])
    for col, rot in zip("KLMOP", ("efeito", "válido", "problema", "tipo de fonte", "avisos")):
        h["celulas"].append([col + "1", rot, None])
    rs = lambda col: f"{CF}${col}${INICIO}:${col}${FIM}"
    for j, (nome, aba, coord) in enumerate(tr["alvos"], 2):
        original = qualifica(tr["antes"][aba][coord], aba)
        base, _ = apresentacao(tr["antes"][aba][coord])
        cel = {"A": nome,
               "B": f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{j},{rs("D")},"somar")',
               "C": f'=COUNTIFS({rs("B")},TRUE,{rs("C")},A{j},{rs("D")},"trocar por")',
               "D": f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{j},{rs("D")},"trocar por")',
               "E": f'=IF(COUNTIFS({rs("B")},"<>FALSE",{rs("C")},A{j},$L$2:$L${QUANTIDADE + 1},0)>0,"Entrada inválida",IF(C{j}>1,"Conflito: mais de uma troca",""))',
               "F": original, "G": qualifica("=" + base, aba), "H": f"={ref(aba, coord)}"}
        h["celulas"] += [[f"{c}{j}", v, None] for c, v in cel.items()]
    for j in range(2, QUANTIDADE + 2):
        r = INICIO + j - 2
        ligado, caixa, como, valor, tipo, fonte = (f"{CF}${c}${r}" for c in COLUNAS)
        valido = (f'=IF(ISBLANK({ligado}),1,IF(NOT(ISLOGICAL({ligado})),0,IF(NOT({ligado}),1,IF(AND('
                  f'COUNTIFS($A$2:$A${len(tr["alvos"]) + 1},{caixa})=1,'
                  f'OR({como}="somar",{como}="trocar por"),ISNUMBER({valor}),'
                  f'COUNTIFS($O$2:$O${len(FONTES) + 1},{tipo})=1,LEN(TRIM({fonte}&""))>0),1,0))))')
        h["celulas"] += [[f"K{j}", j - 1, None], [f"L{j}", valido, None],
                          [f"M{j}", f'=IF(L{j}=1,"","Efeito {j - 1}: confira ligado, caixa, como, valor e fonte")', None]]
    # Um resumo curto na tela, detalhes completos na ANALISE.
    h["celulas"].append(["P2", f'=IF(COUNTIFS(L2:L{QUANTIDADE + 1},0)>0,"Efeito ligado inválido: confira os campos",IF(COUNTIFS(C2:C{len(tr["alvos"]) + 1},">1")>0,"Conflito: desligue uma das trocas da mesma caixa",""))', None])
    a["condicional_gs"] = [{"faixas": ["I7", f"L{INICIO}:L{INICIO + len(tr['alvos']) - 1}"], "contem": "⚠", "fundo": "#C2334D", "fonte": "#FFFFFF"}]
    h["colunas_larg"] = [[1, 16, 24]]
    return a, h


def aplica(layout, tr):
    for aba, mudancas in tr["celulas"].items():
        for r in ix._aba(layout, aba)["celulas"]:
            if r[0] in mudancas:
                r[1] = mudancas[r[0]]
    a, h = abas(layout, tr)
    layout["abas"] += [a, h]
    return a


def exporta(tr):
    """Campos individuais preservam posições vazias e evitam texto ambíguo no bot."""
    linhas = []
    for n in range(1, QUANTIDADE + 1):
        r = INICIO + n - 1
        for campo, col in zip(CAMPOS, COLUNAS):
            origem = ref(NOME, f"{col}{r}")
            valor = f'=N({origem})&""' if campo == "ligado" else f'=IF(ISBLANK({origem}),"",{origem}&"")'
            linhas.append([f"efeito.{n}.{campo}", valor, origem.replace("$", ""), "configuração"])
        linhas.append([f"aviso.efeito.{n}", f'={DADOS}!$M${n + 1}&""', f"{DADOS}!M{n + 1}", "aviso"])
    for n, (nome, aba, coord) in enumerate(tr["alvos"], 2):
        chave = ix._norm(nome).replace(" · ", ".").replace(" ", "_")
        linhas.append([f"aviso.efeito_caixa.{chave}", f'={DADOS}!$E${n}&""', f"{DADOS}!E{n}", "aviso"])
    return linhas
