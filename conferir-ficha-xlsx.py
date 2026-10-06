# -*- coding: utf-8 -*-
"""Confere o .xlsx gerado contra as decisoes. Nada e digitado aqui.

A checagem que mais vale e a da fonte: o prototipo declarava Oswald e Lexend
e saiu com 4362 celulas em Calibri, porque o openpyxl poe Calibri em toda
celula pintada sem estilo explicito. Um erro que so aparece abrindo o arquivo.
"""
import json, os, sys
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter as L

FALHAS = []
def checa(desc, cond, det=""):
    print(f"  [{'OK' if cond else 'FALHA'}] {desc}" + ("" if cond else f"  <- {det}"))
    if not cond: FALHAS.append(desc)

ARQ = "ficha-v01/ficha-projeto-m-0.1.xlsx"
if not os.path.exists(ARQ):
    print(f"FALTA O ARQUIVO '{ARQ}'. Gere com:  python3 ficha-v01/monta.py"); sys.exit(1)

CAT = json.load(open("catalogo-projeto-m.json", encoding="utf-8"))
DEC = json.load(open("decisoes-ficha.json", encoding="utf-8"))
wb  = load_workbook(ARQ)

_F = DEC["C4_fontes"]
CORPO = _F["corpo"]["fonte"]
PERMITIDAS = {_F[p]["fonte"] for p in ("corpo", "titulo", "documento", "serie", "marca")}
KANJI_PISO = _F["kanji_piso_pt"]
PALETA = {"120F1D","211C35","30294D","493F54","756588","998BA9","F4F1F7"} | \
         {g["hex"] for g in DEC["A5_acento"]["degraus"]}

print("AS ABAS")
esperadas = DEC["C6_documento"]["abas"]
checa("as abas decididas existem", all(a in wb.sheetnames for a in esperadas),
      str([a for a in esperadas if a not in wb.sheetnames]))
checa("a CARTEIRA abre primeiro (C6: ela é o documento)",
      wb.sheetnames[0] == "CARTEIRA", wb.sheetnames[0])
checa("a DADOS fica escondida", wb["DADOS"].sheet_state == "hidden")

print("\nA FONTE  (o defeito que matou o protótipo)")
contagem, fora = {}, {}
for ws in wb:
    for linha in ws.iter_rows():
        for cel in linha:
            if cel.font and cel.font.name:
                contagem[cel.font.name] = contagem.get(cel.font.name, 0) + 1
                if cel.font.name not in PERMITIDAS:
                    fora.setdefault(cel.font.name, []).append(f"{ws.title}!{cel.coordinate}")
for f, n in sorted(contagem.items(), key=lambda x: -x[1]):
    print(f"      {f:16} {n:>6} células")
checa("nenhuma célula saiu numa fonte que não foi escolhida", not fora,
      str({k: (len(v), v[:2]) for k, v in fora.items()}))
checa("a fonte padrão do documento é a de corpo",
      wb._fonts[0].name == CORPO, str(wb._fonts[0].name))

print("\nTODA FONTE USADA EXISTE MESMO NO SHEETS?")
# Esta checagem existe porque eu propus DUAS fontes que nao existem la, uma
# atras da outra. A lista do Google Fonts nao e a lista do Sheets.
CONF = set(_F["fontes_confirmadas_no_sheets"]["existem"])
NAO  = set(_F["fontes_confirmadas_no_sheets"]["NAO_existem"])
for papel in ("corpo", "titulo", "documento", "serie", "marca"):
    f = _F[papel]["fonte"]
    checa(f"{papel:10} usa '{f}', que foi conferida no seletor de fontes",
          f in CONF, f"'{f}' nao esta na lista conferida"
                     + (" (e esta na lista das que NAO existem)" if f in NAO else ""))
usadas = {c.font.name for ws in wb for l in ws.iter_rows() for c in l
          if c.font and c.font.name}
checa("nenhuma célula usa fonte fora da lista conferida",
      usadas <= CONF, str(sorted(usadas - CONF)))

print("\nO KANJI, E O PISO MEDIDO")
kanji = [(ws.title, c.coordinate, c.font.size, c.value)
         for ws in wb for l in ws.iter_rows() for c in l
         if isinstance(c.value, str) and any("\u4e00" <= ch <= "\u9fff" for ch in c.value)]
for aba, coord, pt, v in kanji:
    print(f"      {aba}!{coord}  {v}  {pt} pt")
checa(f"nenhum kanji abaixo de {KANJI_PISO} pt (abaixo disso o traço funde)",
      all(k[2] >= KANJI_PISO for k in kanji), str([k for k in kanji if k[2] < KANJI_PISO]))

print("\nA ARTE  (C5: desenhada por código, nunca baixada)")
import os as _os
pecas = DEC["C5_arte"]["pecas"]
faltando = [p for p in pecas if not _os.path.exists(f"arte/{p}.png")]
checa(f"as {len(pecas)} peças existem", not faltando, str(faltando))
checa("o gerador da arte está junto", _os.path.exists("arte/gera.py"))
usadas = sum(len(ws._images) for ws in wb)
checa("a ficha usa a arte", usadas >= 5, f"{usadas} imagens")

print("\nA REGRA DURA DO CELULAR  (o app de celular troca fonte que ele não tem)")
# Ela valia na aba MESA, e a MESA saiu da planilha viva. Decisão do Mizuki, 14/09/2026:
# "Ainda vamos manter sem, por enquanto". As duas pontas continuam amarradas: se a aba
# voltar para a decisão C6, o arquivo tem de ter ela, e vice-versa.
if "MESA" in DEC["C6_documento"]["abas"] or "MESA" in wb.sheetnames:
    checa("a MESA está na decisão C6 e no arquivo, as duas",
          "MESA" in wb.sheetnames and "MESA" in DEC["C6_documento"]["abas"])
    if "MESA" in wb.sheetnames:
        so_corpo = {c.font.name for l in wb["MESA"].iter_rows() for c in l
                    if c.font and c.font.name}
        checa(f"a MESA usa só {CORPO}", so_corpo <= {CORPO}, str(so_corpo))
        checa("a MESA tem 12 colunas com largura definida",
              all(L(c) in wb["MESA"].column_dimensions for c in range(1, 13)))
        _lm = wb["MESA"].column_dimensions["A"].width
        checa("a largura de coluna está na faixa medida (3.6 a 4.1)", 3.6 <= _lm <= 4.1, str(_lm))
else:
    print("  [--] sem aba de celular na decisão C6 nem no arquivo: a regra do celular não tem onde valer")

print("\nA LARGURA DAS ABAS DE PC")
# as abas de PC saem da decisão C6, e não de uma lista escrita aqui:
# a TÉCNICA saiu da ficha e esta linha envelheceu junto
# 14/09/2026: cada aba com a largura dela, e não a da MESA; as ocultas ficam de fora,
# porque ninguém as vê. As da invocação têm gerador e validador próprios, e o nome
# delas sai do arquivo que aquele gerador escreve.
_INV = set(load_workbook("ficha-invocacao/ficha-invocacao.xlsx").sheetnames) - {"DADOS"}
_LIMPA = json.load(open("ficha-v01/layout.json", encoding="utf-8"))["_meta"].get("largura_limpa")
def _px_col(w):
    """a conta do Sheets, a mesma do emissor: pixel = 8 x largura - 1 (medidas/larguras-sheets.json),
    com a largura da limpeza 2 voltando a ser a exportada. Até 15/09/2026 aqui era 7 x largura."""
    if _LIMPA and abs(w - _LIMPA["no_layout"]) < 1e-6:
        w = _LIMPA["exportada"]
    return round(8 * w - 1)
for aba in [a for a in DEC["C6_documento"]["abas"]
            if a in wb.sheetnames and wb[a].sheet_state != "hidden"]:
    larg = wb[aba].column_dimensions["A"].width or 4.0
    # 01/10/2026: a coluna de um grupo fechado (o painel de XP da FICHA PESSOAL) não ocupa tela
    n = sum(1 for c in range(1, 60) if L(c) in wb[aba].column_dimensions and not wb[aba].column_dimensions[L(c)].hidden)
    px = n * _px_col(larg)
    if aba in _INV:
        print(f"  [--] {aba}: {n} colunas ≈ {px:.0f} px — aba da invocação, fica com o conferir-invocacao.py")
        continue
    # 01/10/2026: a FICHA AMALDIÇOADA é mais larga que o notebook, por decisão do Mizuki ("dar mais colunas a pagina"), e
    # as colunas dela não têm todas a mesma largura. A largura dela é a soma de cada coluna, e tem de ser a decidida.
    _fora = DEC["C6_documento"].get("largura_fora_do_notebook", {}).get(aba)
    if _fora:
        px = sum(_px_col(wb[aba].column_dimensions[L(c)].width) for c in range(1, wb[aba].max_column + 1))
        checa(f"{aba}: {n} colunas, {px:.0f} px, a largura que o Mizuki decidiu (mais larga que o notebook de 1366)",
              px == _fora["px"] and px > 1366, f"{px:.0f} px, e a decisão diz {_fora['px']}")
        continue
    checa(f"{aba}: {n} colunas ≈ {px:.0f} px, cabe em notebook de 1366",
          1200 <= px <= 1366, f"{px:.0f} px")

print("\nA COR  (nada fora da paleta decidida)")
fora_c = {}
for ws in wb:
    for linha in ws.iter_rows():
        for cel in linha:
            for cor in (cel.font.color if cel.font else None,):
                if cor is not None and cor.rgb and isinstance(cor.rgb, str):
                    h = cor.rgb[-6:].upper()
                    if h not in PALETA and h != "000000":
                        fora_c.setdefault(h, []).append(f"{ws.title}!{cel.coordinate}")
checa("nenhuma cor de texto fora da paleta", not fora_c,
      str({k: len(v) for k, v in fora_c.items()}))

print("\nAS DECISÕES APARECEM NO ARQUIVO")
ws = wb["DADOS"]
textos = [c.value for l in ws.iter_rows() for c in l if isinstance(c.value, str)]
c1 = DEC["C1_evocador"]
checa(f"o menu de Caminhos tem os {len(c1['caminhos_no_menu'])} da decisão C1",
      all(c in textos for c in c1["caminhos_no_menu"]))
menu = [c.value for c in ws["A"][3:3+6] if c.value]
# 14/09/2026: o Evocador voltou ao menu. O menu da DADOS tem de ser o da C1, na ordem,
# e o caminho oculto, se a C1 voltar a ter um, não pode estar nele.
checa("o menu de Caminhos da DADOS é o da decisão C1, na ordem",
      menu == c1["caminhos_no_menu"], str(menu))
if c1.get("caminho_oculto"):
    checa(f"o {c1['caminho_oculto']} NÃO está no menu de Caminhos",
          c1["caminho_oculto"] not in menu, str(menu))
# 06/10/2026: a tabela dos Caminhos sai do catálogo desde 04/10 (o Incursor, o Provocar do Bastião), e ninguém cobrava o
# que ela diz: o comparador só vê o que difere da exportação, e a linha do Incursor vazia ou a faixa da vida parada na
# linha de antes saem iguais a ela. Lida pelo cabeçalho, como o Codigo.gs lê.
_cab_cam = [c for l in ws.iter_rows() for c in l if c.value == "Caminho"]
_tab_cam, _lin_cam = [], []
if len(_cab_cam) == 1:
    _r, _c = _cab_cam[0].row, _cab_cam[0].column
    _tit = {}
    while ws.cell(row=_r, column=_c + len(_tit)).value:
        _tit[ws.cell(row=_r, column=_c + len(_tit)).value] = _c + len(_tit)
    while ws.cell(row=_r + 1 + len(_tab_cam), column=_c).value:
        _lin_cam.append(_r + 1 + len(_tab_cam))
        _tab_cam.append([ws.cell(row=_lin_cam[-1], column=_tit[t]).value if t in _tit else None
                         for t in ("Caminho", "atributos naturais", "vida inicial", "vida por nível", "PE por nível",
                                   "perícia fixa 1", "perícia fixa 2")])
_cam_cat = [[n, " · ".join(CAT["caminhos"][n]["atributos_naturais"]), CAT["caminhos"][n]["vida_inicial"],
             CAT["caminhos"][n]["vida_por_nivel"], CAT["caminhos"][n]["pe_por_nivel"]] + CAT["caminhos"][n]["pericias_fixas"]
            for n in c1["caminhos_no_menu"]]
checa(f"a tabela dos Caminhos da DADOS traz os {len(_cam_cat)} do menu, na ordem, com a vida, o PE e as perícias fixas do catálogo",
      _tab_cam == _cam_cat, str([l for l in _tab_cam if l not in _cam_cat] or [l[0] for l in _tab_cam]))
import re as _re_cam
_faixas_cam = [(c.coordinate, int(m.group(1)), int(m.group(2))) for l in wb["FICHA"].iter_rows() for c in l
               if isinstance(c.value, str) for m in _re_cam.finditer(r"DADOS!\$N\$(\d+):\$U\$(\d+)", c.value)]
checa("a vida e o PE da FICHA leem a tabela dos Caminhos da primeira linha à última (o Incursor entra na conta)",
      bool(_lin_cam) and len(_faixas_cam) >= 3 and all((a, b) == (_lin_cam[0], _lin_cam[-1]) for _, a, b in _faixas_cam),
      f"a tabela vai da linha {_lin_cam[:1]} à {_lin_cam[-1:]}; as faixas: {_faixas_cam}")
checa("o carimbo de versão está na DADOS",
      str(ws["B1"].value) == CAT["_meta"]["versao"], str(ws["B1"].value))

f = wb["FICHA"]
formulas = [c.value for l in f.iter_rows() for c in l
            if isinstance(c.value, str) and c.value.startswith("=")]
checa("a FICHA tem fórmula, e não número digitado", len(formulas) >= 20, str(len(formulas)))
# 04/10/2026: a troca da faixa dos Caminhos passou o escape do re.sub para dentro da fórmula (DADOS!\$N\$5), e a vida e o
# PE davam Err:508; as regressões que comparam o script com a planilha gerada não viam, porque as duas saíam iguais
_barra = [(a.title, c.coordinate) for a in wb.worksheets for l in a.iter_rows() for c in l
          if isinstance(c.value, str) and c.value.startswith("=") and "\\" in c.value]
checa("nenhuma fórmula da planilha tem barra invertida (escape que vazou da geração)", not _barra, str(_barra[:6]))
checa("existe o aviso de catálogo desatualizado (A1)",
      any("a atual é a v" in x for x in formulas))
checa("a Defesa soma uma célula de proteção, não uma constante (C3)",
      any(x.startswith("=10+") and "+$" in x for x in formulas),
      str([x for x in formulas if x.startswith("=10+")][:2]))
checa("a proteção sai do refino, e não de um 1 escrito na mão (C3)",
      any("FLOOR(" in x and "/3" in x for x in formulas))
checa("a maestria usa a lista de marcos, não 'a cada 8 níveis'",
      any('COUNTIF' in x and 'm_maestria' not in x for x in formulas) and
      not any("/8" in x for x in formulas))
checa("o estágio de alma é calculado, não marcado",
      any("estágio 4" in x.lower() for x in formulas))

print("\nFORMATO DE DATA E NÚMERO  (o Sheets fala inglês)")
# 'aaaa' nao quebra a formula: ela roda e devolve o dia da semana. Erro que
# so aparece olhando a planilha pronta, entao ele vira checagem.
TOKENS_PT = ["aaaa", "aa/", "/aa", "dd.mm.aaaa"]
todas = [(ws.title, c.coordinate, c.value) for ws in wb for l in ws.iter_rows()
         for c in l if isinstance(c.value, str) and c.value.startswith("=")]
ruins = [(a, co, v) for a, co, v in todas
         if "TEXT(" in v and any(t in v for t in TOKENS_PT)]
checa("nenhum formato de data em português dentro de TEXT()", not ruins,
      str(ruins[:2]))
datas = [v for _, _, v in todas if "TODAY()" in v]
checa("as datas usam yyyy", all("yyyy" in v for v in datas) if datas else True,
      str(datas))

print("\nCADA FÓRMULA PUXA O ATRIBUTO CERTO")
# a ordem do catalogo e Forca, Destreza, Constituicao. Ler atributo por POSICAO
# fazia a Vida somar Destreza; esta checagem existe por causa desse bug.
IDX = {}
dd = wb["DADOS"]
# desde 17/09/2026 a célula do índice é fórmula (ADDRESS), e o indice_ficha.py lê as duas formas
sys.path.insert(0, "ficha-v01")
from indice_ficha import endereco as _endereco
for rr in range(5, 200):
    k, v = dd.cell(row=rr, column=53).value, _endereco(dd.cell(row=rr, column=54).value)
    if k and v: IDX[k] = v
checa("a ficha publica o índice das próprias células", len(IDX) >= 20, str(len(IDX)))
for campo, atributo in [("vida_max", "Constituição"), ("defesa", "Destreza"),
                        ("corpo a corpo", "Força"), ("à distância", "Destreza")]:
    alvo = IDX.get("atr_" + atributo, "?")
    form = f[IDX[campo]].value if campo in IDX else ""
    checa(f"{campo} usa {atributo} ({alvo})",
          isinstance(form, str) and alvo in form.replace("$", ""),
          str(form)[:80])

print("\nA DEFESA COM UNIFORME, ESCUDO E REFINO ESCOLHIDO  (B3, v0.246 do sistema)")
# O número mora na regressao-kaori-na-ficha.py, que recalcula dez casos no LibreOffice. Aqui fica a
# estrutura que a regressão supõe: a tabela da DADOS é a do catálogo, o menu aponta para ela, o campo
# novo está no índice com o rótulo em cima, e as três fórmulas leem o que devem ler.
import re
_EQC = CAT.get("equipamento_defesa", {})
_esp = []
for _u, _vu in _EQC.get("uniformes", {}).items():
    _esp.append((_u, _vu["protecao"], _vu["teto_de_destreza"], "sim"))
for _e, _ve in _EQC.get("escudos", {}).items():
    _esp.append((_e, _ve["protecao"], _ve["teto_de_destreza"], "não"))
for _u, _vu in _EQC.get("uniformes", {}).items():
    for _e, _ve in _EQC.get("escudos", {}).items():
        _ts = [t for t in (_vu["teto_de_destreza"], _ve["teto_de_destreza"]) if t is not None]
        _esp.append((f"{_u} + {_e}", _vu["protecao"] + _ve["protecao"], min(_ts) if _ts else None, "sim"))
_menu_eq = [v for v in f.data_validations.dataValidation if IDX.get("equipamento") and
            str(v.sqref) == IDX["equipamento"].replace("$", "")]
# 01/10/2026: o EQUIPAMENTO deixou de ser menu e passou a espelhar a FICHA PESSOAL (o que está vestido e o
# escudo da mão secundária). A tabela é a mesma, e agora se acha pela fórmula da PROTEÇÃO, que lê as quatro
# colunas dela; que o espelho monta um nome que a tabela tem, quem confere é o regressao-ficha-pessoal.py.
_feq = str(f[IDX.get("equipamento", "A1")].value)
_faixa = str(f[IDX.get("proteção", "A1")].value)
_mf = re.search(r"DADOS!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)", _faixa)
_lida = []
from openpyxl.utils import column_index_from_string as _ci
if _mf:
    for _r in range(int(_mf.group(2)), int(_mf.group(4)) + 1):
        _c0 = _ci(_mf.group(1))
        _vals = [dd.cell(row=_r, column=_c0 + k).value for k in range(4)]
        _lida.append((_vals[0], _vals[1], None if _vals[2] == "—" else _vals[2], _vals[3]))
checa("o EQUIPAMENTO da FICHA não é mais menu: é fórmula que lê a FICHA PESSOAL",
      not _menu_eq and _feq.startswith("=") and "'FICHA PESSOAL'!" in _feq, _feq[:90])
checa("a PROTEÇÃO lê a tabela de equipamento da DADOS, quatro colunas",
      bool(_mf) and _ci(_mf.group(3)) - _ci(_mf.group(1)) == 3, _faixa[:90])
checa("a tabela de equipamento é a do catálogo: uniforme, escudo e cada par, com o menor teto",
      bool(_esp) and _lida == _esp, f"{len(_lida)} linhas lidas, {len(_esp)} esperadas")
_camp = IDX.get("refino escolhido", "")
# 17/09/2026: o campo mora no `Marco Escolhido` que o Mizuki desenhou, com o rótulo `Refino`, e o menu
# dele divide a mesma validação com os outros menus de marco
_menu_r = [v for v in f.data_validations.dataValidation if _camp and _camp.replace("$", "") in str(v.sqref).split()]
_nmarcos = len(CAT["progressao"]["marcos"])
checa("o refino escolhido está no índice, com o rótulo em cima e menu de 0 até os marcos",
      bool(_camp) and f.cell(row=f[_camp].row - 1, column=f[_camp].column).value in ("REFINO ESCOLHIDO", "Refino")
      and bool(_menu_r) and _menu_r[0].formula1 == '"' + ",".join(map(str, range(_nmarcos + 1))) + '"',
      f"{_camp} · {[v.formula1 for v in _menu_r]}")
_fd, _fp = str(f[IDX.get("defesa", "A1")].value), str(f[IDX.get("proteção", "A1")].value)
checa("a Defesa corta a Destreza pelo teto da tabela (coluna 3), e soma a proteção",
      "MIN(" in _fd and ",3,FALSE)" in _fd and ("+" + IDX.get("proteção", "?")) in _fd.replace("$", ""), _fd[:90])
checa("a Defesa soma o Buff/Debuff (17/09/2026)",
      not IDX.get("buff de defesa") or IDX["buff de defesa"] in _fd.replace("$", ""), _fd[-60:])
checa("a proteção desliga a passiva pela coluna 4, soma a da tabela pela 2, e a passiva lê o refino escolhido",
      ",4,FALSE)" in _fp and ",2,FALSE)" in _fp and _camp.replace("$", "") in _fp.replace("$", ""), _fp[:90])
_fa = [c.value for l in f.iter_rows() for c in l if isinstance(c.value, str) and "Refino Atual" in c.value]
# desde 17/09/2026 a caixa lê a tabela de contas da DADOS: segue a referência até chegar no campo
def _alcanca(formula, alvo, fundo=4):
    if not isinstance(formula, str) or fundo == 0:
        return False
    if alvo in formula.replace("$", ""):
        return True
    return any(_alcanca(dd[c.replace("$", "")].value, alvo, fundo - 1)
               for c in re.findall(r"DADOS!(\$?[A-Z]+\$?\d+)", formula))
# 02/10/2026: o Refino Atual impresso saiu com a seção 8 da FICHA (o menu rápido), e o refino que a conta usa mora na
# FICHA AMALDIÇOADA, que lê a conta do refino atual da DADOS
_am = wb["DADOS_AM"]
_ref_am = next((_am.cell(row=c.row, column=c.column + 1).value for l in _am.iter_rows() for c in l if c.value == "refino"), None)
checa("o Refino Atual impresso saiu com a seção 8, e o refino da FICHA AMALDIÇOADA soma o refino escolhido",
      not _fa and _alcanca(_ref_am, _camp.replace("$", "")), f"{len(_fa)} impresso(s) · {str(_ref_am)[:80]}")

print("\nA FICHA AUTOMÁTICA  (17/09/2026)")
# O número mora na regressao-kaori-na-ficha.py, que recalcula doze casos no LibreOffice contra um modelo
# de força bruta. Aqui fica o que a regressão não vê: o índice anda sozinho, e o Codigo.gs sabe das
# caixas novas.
_bb = [dd.cell(row=rr, column=54).value for rr in range(5, 200) if dd.cell(row=rr, column=53).value]
checa("todo endereço do índice é fórmula ADDRESS, e anda quando a planilha muda de forma",
      bool(_bb) and all(isinstance(v, str) and v.startswith("=ADDRESS(ROW(FICHA!") for v in _bb),
      str([v for v in _bb if not (isinstance(v, str) and v.startswith("=ADDRESS("))][:3]))
# 02/10/2026: as aptidões disponíveis e as Passivas do Leque saíram com a seção 8; a conta delas mora na FICHA AMALDIÇOADA
_NOVAS = ["pontos disponíveis", "pontos de corpo", "marcos escolhidos", "perícias disponíveis",
          "ofícios disponíveis", "testes disponíveis"]
_SAIRAM = ["feitiços disponíveis", "passivas", "aptidão de graça 1", "aptidão de graça 2", "aptidões disponíveis", "passivas do leque"]
checa("as seis caixas de conta estão no índice, e as seis da seção 8 saíram dele",
      all(k in IDX for k in _NOVAS) and not any(k in IDX for k in _SAIRAM),
      str([k for k in _NOVAS if k not in IDX] + [k for k in _SAIRAM if k in IDX]))
_CODA = open("apps-script/Codigo.gs", encoding="utf-8").read()
_avisos = re.search(r"var avisos = \[(.*?)\]", _CODA, re.S)
checa("o Codigo.gs avisa em vermelho e anota as seis caixas de conta",
      bool(_avisos) and all(f"'{k}'" in _avisos.group(1) and re.search(rf"'{k}':\s*'", _CODA) for k in _NOVAS),
      str([k for k in _NOVAS if not (_avisos and f"'{k}'" in _avisos.group(1))]))
# 17/09/2026: a trava virou varredura de toda fórmula da FICHA e da CARTEIRA, porque o resultado das
# perícias, dos ofícios e dos Testes de Resistência ficava de fora da lista. O que se confere: o script
# varre as fórmulas, as livres são só as três barras de agora, e cada linha de perícia, ofício e Teste
# (a caixa de seleção com o nome ao lado) tem o resultado em fórmula, que é o que a varredura trava.
_mprot = re.search(r"function protegerFormulas_\(ss, idx\)\s*\{(.*?)\n\}", _CODA, re.S)
_livres = re.search(r"var LIVRES_DA_TRAVA = \[(.*?)\];", _CODA)
checa("o Codigo.gs trava toda fórmula da FICHA e da CARTEIRA, e deixa livres só as três barras de agora",
      bool(_mprot and _livres) and "getFormulas()" in _mprot.group(1) and "'CARTEIRA'" in _mprot.group(1)
      and sorted(re.findall(r"'([^']+)'", _livres.group(1))) == ["energia", "integridade", "vida"]
      and all(k in IDX for k in ["vida", "energia", "integridade"]),
      _livres.group(1) if _livres else "sem LIVRES_DA_TRAVA")
_sem_resultado = []
for _l in f.iter_rows():
    for _c in _l:
        if _c.value is True or _c.value is False:
            _nome = next((f.cell(row=_c.row, column=_c.column + k).value for k in (1, 2)
                          if isinstance(f.cell(row=_c.row, column=_c.column + k).value, str)
                          and f.cell(row=_c.row, column=_c.column + k).value.strip()), None)
            if not _nome:
                continue
            _res = [f.cell(row=_c.row, column=cc).value for cc in range(_c.column + 1, min(_c.column + 16, f.max_column + 1))]
            _ate = next((i for i, v in enumerate(_res[2:], 2) if v is True or v is False), len(_res))
            if not any(isinstance(v, str) and v.startswith("=") for v in _res[:_ate]):
                _sem_resultado.append(f"{_c.coordinate} {_nome}")
checa("toda perícia, ofício e Teste de Resistência tem o resultado em fórmula, e a varredura trava",
      not _sem_resultado, str(_sem_resultado[:4]))
# a nota que aponta para campo que o índice não publica some calada no Apps Script
_mnotas = re.search(r"function notasDeRegra_\(ss, idx\)\s*\{(.*?)\n\}", _CODA, re.S)
_mobj = re.search(r"var notas = \{(.*?)\n  \};", _mnotas.group(1), re.S) if _mnotas else None
_chaves = set(re.findall(r"^\s{4}'([^']+)':", _mobj.group(1), re.M)) if _mobj else set()
_bl = re.search(r"\[([^\]]*)\]\.forEach\(function \(k\) \{\s*notas\['buff de ' \+ k\]", _mnotas.group(1)) if _mnotas else None
_chaves |= {"buff de " + k for k in re.findall(r"'([^']+)'", _bl.group(1))} if _bl else set()
_chaves |= set(re.findall(r"notas\['([^']+)'\] =", _mnotas.group(1))) if _mnotas else set()
checa("toda nota do Codigo.gs aponta para um campo que o índice publica",
      len(_chaves) >= 30 and all(k in IDX for k in _chaves), str(sorted(k for k in _chaves if k not in IDX)))
_NOTA_PEDIDA = ["defesa", "iniciativa", "conjuração", "corpo a corpo", "à distância", "deslocamento",
                "escolhas de perícia", "trilha"] + \
               ["buff de " + k for k in ["defesa", "iniciativa", "cd de feitiço", "conjuração", "corpo a corpo",
                                         "à distância", "deslocamento"]]
checa("a Defesa, as caixas de Buff/Debuff e os ataques têm nota (17/09/2026; os Feitiços e as Passivas saíram com a seção 8)",
      all(k in _chaves for k in _NOTA_PEDIDA), str([k for k in _NOTA_PEDIDA if k not in _chaves]))
checa("a nota mora no título quando o de cima é texto (tituloOuCaixa_ no alvoDaNota_)",
      bool(_mnotas) and "alvoDaNota_(c, valores, formulas, mescladas)" in _mnotas.group(1) and "function tituloOuCaixa_(" in _CODA
      and "tituloOuCaixa_(acima)" in _CODA)
_marcos_rot = [f.cell(row=f[IDX[k]].row - 1, column=f[IDX[k]].column).value
               for k in ("refino escolhido", "marco corpo", "marco leque") if k in IDX]
checa("o Marco Escolhido tem os rótulos Refino, Corpo e Leque, e as notas falam deles",
      _marcos_rot == ["Refino", "Corpo", "Leque"] and "Refino, Corpo ou Leque" in _CODA
      and "Atributo (Corpo)" not in _CODA, str(_marcos_rot))
# as aptidões de graça: os nomes saem do manual pelo ficha_automatica.regras(). Desde 02/10/2026 elas aparecem no menu
# rápido da FICHA, que lê a carta "De graça" da DADOS_AM, e essa lê o rótulo da rota: as duas aptidões, ou as duas Bênçãos
# na Restrição Celestial sem energia. A nota que o script punha na caixa da seção 8 saiu com ela, e a da FICHA AMALDIÇOADA
# é do gerador (a regressao-amaldicoada confere).
import ficha_automatica as _fa_mod
_RG = _fa_mod.regras(CAT)
def _segue_am(v, fundo=3):
    """a fórmula de referência pura dentro da DADOS_AM, seguida até a que faz conta"""
    m = re.fullmatch(r"=\$?([A-Z]+)\$?(\d+)", v or "") if isinstance(v, str) else None
    return _segue_am(_am[f"{m.group(1)}{m.group(2)}"].value, fundo - 1) if m and fundo else v
_gr_am = [next((c for l in _am.iter_rows() for c in l if c.value == f"De graça {i}"), None) for i in (1, 2)]
_gr_nome = [_am.cell(row=c.row, column=c.column + 3) if c else None for c in _gr_am]
def _nomes_da_rota(v):
    """o INDEX da linha de rótulos da rota: os nomes de cada rota, juntos"""
    m = re.fullmatch(r"=INDEX\(\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+),1,.*\)", v or "") if isinstance(v, str) else None
    return " | ".join(str(c.value) for l in _am[f"{m.group(1)}{m.group(2)}:{m.group(3)}{m.group(4)}"] for c in l) if m else v
_gr_fim = [_nomes_da_rota(_segue_am(c.value)) if c else None for c in _gr_nome]
_no_menu = {c.value for l in f.iter_rows() for c in l if isinstance(c.value, str) and c.value.startswith("=DADOS_AM!")}
checa("as duas cartas de graça do menu rápido vêm com as de graça, trocando pelas Bênçãos sem energia",
      all(c is not None and f"=DADOS_AM!${c.column_letter}${c.row}" in _no_menu for c in _gr_nome)
      and all(isinstance(v, str) and a in v and b in v for v, a, b in zip(_gr_fim, _RG["bencaos_de_graca"], _RG["aptidoes_de_graca"])),
      str(_gr_fim)[:120])
checa("as notas de graça da seção 8 saíram do Codigo.gs com ela", "notasDeGraca_" not in _CODA and "NOTAS_DE_GRACA" not in _CODA)
_oned = re.search(r"function onEdit\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
checa("o onEdit devolve a Trilha de outro Caminho para o texto de escolha",
      bool(_oned) and "trilhaDoCaminho_(e, idx)" in _oned.group(1))
_vt = [v for v in f.data_validations.dataValidation if IDX.get("trilha") and IDX["trilha"].replace("$", "") in str(v.sqref).split()]
_mt = re.search(r"DADOS!\$([A-Z]+)\$(\d+)", _vt[0].formula1) if _vt else None
_filtro = dd[f"{_mt.group(1)}{int(_mt.group(2)) + 1}"].value if _mt else ""
checa("o menu da Trilha começa no texto de escolha e filtra as Trilhas pelo Caminho da ficha",
      bool(_mt) and dd[f"{_mt.group(1)}{_mt.group(2)}"].value == _fa_mod.ESCOLHA_TRILHA
      and isinstance(_filtro, str) and "FILTER(" in _filtro and IDX["caminho"].replace("$", "") in _filtro.replace("$", ""),
      f"{_vt[0].formula1 if _vt else '?'} · {str(_filtro)[:70]}")
checa("a ficha nasce com Escolha seu Caminho e Escolha sua Trilha",
      f[IDX["caminho"]].value == _fa_mod.ESCOLHA_CAMINHO and f[IDX["trilha"]].value == _fa_mod.ESCOLHA_TRILHA,
      f"{f[IDX['caminho']].value} · {f[IDX['trilha']].value}")
checa("o onEdit marca as perícias fixas quando o Caminho muda",
      bool(_oned) and "marcarPericiasDoCaminho_(e, idx)" in _oned.group(1))
checa("a tabela dos Caminhos da DADOS não tem mais ofício fixo, que o livro não tem",
      not any(c.value == "ofício fixo" for l in dd.iter_rows() for c in l))

print("\nO DESENHO DA MESA  (17/09/2026, a segunda rodada)")
# O comparador prova que só as células declaradas mudaram. Aqui fica o que elas têm de dizer.
import ficha_layout as _flm
_ct = wb["CARTEIRA"]
_cv = {c.coordinate: c.value for l in _ct.iter_rows() for c in l if c.value not in (None, "")}
_abaixo = lambda rot: next((_ct.cell(row=_ct[k].row + 1, column=_ct[k].column).value for k, v in _cv.items() if v == rot), "?")
checa("a CARTEIRA traz o portador e o registrado por com texto de exemplo, e o SERVIDOR USADO no lugar da mesa",
      _abaixo("PORTADOR") == _flm.NOME_PORTADOR and _abaixo("REGISTRADO POR") == _flm.NICK
      and "SERVIDOR USADO" in _cv.values() and "MESA DE ORIGEM" not in _cv.values(),
      f"{_abaixo('PORTADOR')} · {_abaixo('REGISTRADO POR')}")
_sis = [k for k, v in _cv.items() if isinstance(v, str) and "DADOS!$F$1" in v]
_mnome = [c.coordinate for l in dd.iter_rows() for c in l if c.value == CAT["_meta"]["sistema"]]
checa("o nome do sistema sai da DADOS, que o escreve do catálogo, na CARTEIRA e na FICHA",
      bool(_sis) and _mnome == ["F1"] and any("DADOS!$F$1" in str(c.value) for l in f.iter_rows(max_row=5) for c in l)
      and "ERA DA REVOLUÇÃO" not in _cv.values(),
      f"{_sis} · {_mnome}")
_nome_f = str(f[IDX["nome"]].value)
checa("a FICHA puxa o nome da CARTEIRA e ignora o texto de exemplo",
      _flm.NOME_PORTADOR in _nome_f and "CARTEIRA!" in _nome_f, _nome_f[:80])
_tec = [v for v in _cv.values() if isinstance(v, str) and "DECLARADA" in v]
checa("o rótulo da técnica declarada muda com a rota: amaldiçoada, marcial ou estilo",
      len(_tec) == 1 and all(x in _tec[0] for x in ("TÉCNICA AMALDIÇOADA DECLARADA", "TÉCNICA MARCIAL DECLARADA",
                                                   "ESTILO DECLARADO")), str(_tec)[:100])
_vo = [v for v in f.data_validations.dataValidation if IDX["origem"].replace("$", "") in str(v.sqref).split()]
_mo2 = re.search(r"DADOS!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)", _vo[0].formula1) if _vo else None
_lista_o = [dd[f"{_mo2.group(1)}{r}"].value for r in range(int(_mo2.group(2)), int(_mo2.group(4)) + 1)] if _mo2 else []
_rc = [r["origem"] for r in CAT["rotas_de_criacao"] if r["origem"].startswith("Restrição Celestial")]
checa("o menu de Origem é a lista das rotas de criação, com as duas Restrições Celestiais",
      _lista_o == _fa_mod.origens_do_menu(CAT) and len(_rc) == 2 and all(x in _lista_o for x in _rc),
      f"{len(_lista_o)} origens · {_rc}")
_esc = f[IDX.get("escolhas de perícia", "A1")]
# a letra do desenho sai da exportação do Mizuki, e não da constante: comparar com a constante deixava a
# checagem verde com ela de volta em 14 (o arnes da rodada de 17/09/2026 achou)
_lay_o = json.load(open("ficha-v01/layout.json", encoding="utf-8"))
_ab_o = next(a for a in _lay_o["abas"] if a["nome"] == "FICHA")
_cel_o = [r for r in _ab_o["celulas"] if r[0] == IDX.get("escolhas de perícia")]
_sz_o = _lay_o["estilos"][_cel_o[0][2]][0][1] if _cel_o and _cel_o[0][2] is not None else None
checa("a caixa das escolhas de perícia fica em letra menor que a do desenho, para a frase caber",
      _sz_o is not None and _esc.font.sz == _flm.FONTE_DAS_ESCOLHAS < _sz_o and bool(_esc.alignment.wrap_text),
      f"desenho {_sz_o} · ficha {_esc.font.sz} · quebra {_esc.alignment.wrap_text}")
_margem = {a: wb[a].max_column for a in ("FICHA", "CARTEIRA")}
checa("a CARTEIRA acaba na mesma coluna da FICHA, com a margem da direita",
      len(set(_margem.values())) == 1, str(_margem))

print("\nO CABEÇALHO NO MOLDE DO ESTUDO, O TÍTULO NO ACENTO E A BARRA NA COR DO TEMA  (01/10/2026)")
# Pedidos do Mizuki testando a Ficha Pessoal no Sheets: o cabeçalho da FICHA e da FICHA PESSOAL como o do estudo (a marca
# e o título à esquerda, o nome e o Caminho à direita), a faixa de título de seção no acento como no GLOSSÁRIO, a barra
# cheia seguindo a paleta, e a tinta de enfeite sem "roxo nada a ver". O comparador prova que só as células declaradas
# mudaram; aqui fica o que elas têm de dizer.
sys.path.insert(0, "ficha-v01")
import cabecalho as _cab, ficha_pessoal as _fpm
_fp = wb[_fpm.NOME]
_cor_de = lambda c: (c.fill.fgColor.rgb or "")[-6:] if c.fill and c.fill.fill_type == "solid" else None
_topo = lambda ws: {c.coordinate: c.value for l in ws.iter_rows(max_row=_cab.ULTIMA_LINHA) for c in l if c.value not in (None, "")}
_tf, _tp = _topo(f), _topo(_fp)
checa("a FICHA abre com a marca, o título e a linha de apoio à esquerda, e o nome e o Caminho à direita",
      _tf.get(_cab.C_MARCA[0]) == _cab.MARCA and f[_cab.C_MARCA[0]].font.name == "Yuji Syuku"
      and _tf.get(_cab.C_TITULO[0]) == _cab.TITULO_DA_FICHA and IDX["nome"] == _cab.C_NOME[0]
      and all(IDX[k].replace("$", "") in str(_tf.get(_cab.C_QUEM[0])).replace("$", "") for k in ("caminho", "trilha", "nivel"))
      and len(_tf) == 5, str(sorted(_tf)))
checa("o carimbo de versão continua na FICHA, na linha de apoio, e a palavra CATÁLOGO saiu do cabeçalho",
      all(x in str(_tf.get(_cab.C_APOIO[0])) for x in ("DADOS!$F$1", "em dia", "a atual é a v", "DADOS!$B$1", "DADOS!$D$1"))
      and "CATÁLOGO" not in _tf.values() and "CATÁLOGO" not in _tp.values(), str(_tf.get(_cab.C_APOIO[0]))[:90])
checa("a FICHA PESSOAL abre com o mesmo cabeçalho, com o título e a linha de apoio dela, e espelha o nome e o Caminho",
      _tp.get(_cab.C_MARCA[0]) == _cab.MARCA and _tp.get(_cab.C_TITULO[0]) == _fpm.NOME
      and _fpm.APOIO in str(_tp.get(_cab.C_APOIO[0])) and "CARTEIRA!" in str(_tp.get(_cab.C_NOME[0]))
      and _tp.get(_cab.C_QUEM[0]) == f"=FICHA!{_cab.C_QUEM[0]}" and len(_tp) == 5, str(sorted(_tp.items()))[:160])
_alt_cab = [(n, r) for n, ws in (("FICHA", f), (_fpm.NOME, _fp)) for r in range(1, _cab.ULTIMA_LINHA + 1) if ws.row_dimensions[r].height]
checa("as cinco linhas do cabeçalho têm a mesma altura nas duas abas (nenhuma declara altura própria)", not _alt_cab, str(_alt_cab))
# (a célula de dentro de uma caixa mesclada não guarda cor própria: vale a do canto)
_miolo = {(r, c) for m in _fp.merged_cells.ranges for r in range(m.min_row, m.max_row + 1) for c in range(m.min_col, m.max_col + 1)
          if (r, c) != (m.min_row, m.min_col)}
_sem_tinta = [c.coordinate for l in _fp.iter_rows(min_row=1, max_row=_cab.ULTIMA_LINHA, min_col=3, max_col=_fp.max_column) for c in l
              if (c.row, c.column) not in _miolo and _cor_de(c) != "0A0810"]
checa(f"a faixa de tinta do cabeçalho da FICHA PESSOAL vai até a última coluna ({L(_fp.max_column)}), por cima do painel de XP",
      _fp.max_column == _fpm.PAINEL_FIM and not _sem_tinta, str(_sem_tinta[:6]))
_num = [k for k, v in _cv.items() if isinstance(v, str) and "Nº M-" in v]
checa("o número da CARTEIRA lê o nome no lugar novo dele",
      len(_num) == 1 and f"FICHA!${''.join(ch for ch in _cab.C_NOME[0] if ch.isalpha())}${''.join(ch for ch in _cab.C_NOME[0] if ch.isdigit())}" in _cv[_num[0]],
      str(_cv.get(_num[0]) if _num else None))
_faixas_fp = [c for l in _fp.iter_rows(min_row=_cab.ULTIMA_LINHA + 2) for c in l
              if c.value not in (None, "") and c.font and c.font.name == "Oswald" and c.font.sz == 14]
_gl = wb["GLOSSÁRIO"]
_faixas_gl = {_cor_de(c) for l in _gl.iter_rows() for c in l if c.value in ("ATRIBUTOS", "PERÍCIAS")}
checa(f"as {len(_faixas_fp)} faixas de título de seção da FICHA PESSOAL têm o fundo do acento, o mesmo das do GLOSSÁRIO",
      len(_faixas_fp) >= 8 and {_cor_de(c) for c in _faixas_fp} == {"211940"} and _faixas_gl == {"211940"},
      f"{ {_cor_de(c) for c in _faixas_fp} } · glossário {_faixas_gl}")
# a barra cheia: a conta da DADOS, e as cinco barras que a leem
_cel_barra = [dd.cell(row=c.row, column=c.column + 1) for l in dd.iter_rows() for c in l
              if c.value == _fpm.COR_DA_BARRA and str(dd.cell(row=c.row, column=c.column + 1).value).startswith("#")]
_ref_barra = f"DADOS!${L(_cel_barra[0].column)}${_cel_barra[0].row}" if len(_cel_barra) == 1 else "?"
_barras = [(n, c.coordinate, str(c.value)) for n, ws in (("FICHA", f), (_fpm.NOME, _fp)) for l in ws.iter_rows() for c in l
           if isinstance(c.value, str) and "SPARKLINE" in c.value]
checa(f"as {len(_barras)} barras (vida, energia, integridade, carga e XP) leem a cor da barra cheia na DADOS, que nasce no osso",
      len(_cel_barra) == 1 and _cel_barra[0].value == "#E8DCD4" and len(_barras) == 5
      and all(_ref_barra in v and "E8DCD4" not in v for _, _, v in _barras), f"{_ref_barra} · {[(n, c) for n, c, v in _barras if _ref_barra not in v or 'E8DCD4' in v]}")
checa("o âmbar e o vermelho de vida baixa continuam escritos nas três barras da FICHA (decisão A5)",
      sum(1 for n, _, v in _barras if n == "FICHA" and "#C2334D" in v and "#D89B3A" in v) == 3)
_passos = re.search(r"function passosDaPaleta_\(primeira\)\s*\{(.*?)\n\}", _CODA, re.S)
_pb = re.search(r"function pintarBarra_\(ss, agora\)\s*\{(.*?)\n\}", _CODA, re.S)
checa("a troca de paleta grava a barra do tema nessa célula, achada pelo índice da FICHA PESSOAL, e é o primeiro passo",
      bool(_passos) and "var passos = ['barra'];" in _passos.group(1) and bool(_pb) and "indicePessoal_()[CAMPO_DA_BARRA_]" in _pb.group(1)
      and "agora.barra" in _pb.group(1) and f"var CAMPO_DA_BARRA_ = '{_fpm.COR_DA_BARRA}';" in _CODA)
_cand = re.search(r"function candidatosDeFonte_\(agora, oposta\)\s*\{(.*?)\n\}", _CODA, re.S)
checa("a rede de legibilidade só troca letra por cor de letra (texto e texto fraco), e nunca pelo acento, pelo bloco ou por um fundo",
      bool(_cand) and "['texto', 'texto_fraco'].forEach" in _cand.group(1)
      and not any(f"'{k}'" in _cand.group(1) for k in ("acento", "bloco", "linha", "papel", "fundo", "painel", "tinta")))
_rep2 = re.search(r"function repintarCoresDaAba_\(ss, spec, nomeAntigo, nomeNovo, trecho\)\s*\{(.*?)\n\}", _CODA, re.S)
checa("a letra de enfeite (a marca, o número, a lombada) é achada pelo endereço no ABAS, e não pela cor que tem",
      bool(_rep2) and "celulasDeEnfeite_(spec)" in _rep2.group(1) and "agora[enfeites[ra + ',' + c]]" in _rep2.group(1))
# o PALETAS do Codigo.gs é o que o derivar.py escreve, sem edição à mão
_pg = json.load(open("medidas/paletas-grandes/paletas-grandes.json", encoding="utf-8"))
_mp2 = re.search(r"var PALETAS = (\{.*?\n\});\n", _CODA, re.S)
_pal2 = json.loads(_mp2.group(1)) if _mp2 else {}
_dif_pal = [(n, v, k) for n in _pg for v in ("claro", "escuro") for k, h in _pg[n][v]["cores"].items()
            if _pal2.get(n, {}).get(v, {}).get(k) != h]
checa(f"o PALETAS do Codigo.gs é, cor por cor, o que o derivar.py gravou no paletas-grandes.json ({len(_pg)} temas, com a barra)",
      len(_pg) == 61 and list(_pal2) == list(_pg) and not _dif_pal and all("barra" in _pg[n][v]["cores"] for n in _pg for v in ("claro", "escuro")),
      str(_dif_pal[:4]))
# a barra cheia de cada tema: viva onde a cor não é parente do âmbar nem do vermelho de vida baixa, neutra onde é.
# A conta é refeita aqui, sem ler o derivar.py: croma e matiz em OKLCH, e o contraste WCAG sobre o painel.
import math as _m
def _oklch(h):
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g_, b_ = (f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    l = (0.4122214708 * r + 0.5363325363 * g_ + 0.0514459929 * b_) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g_ + 0.1073969566 * b_) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g_ + 0.6299787005 * b_) ** (1 / 3)
    a_ = 1.9779984951 * l - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l + 0.7827717662 * m_ - 0.8086757660 * s_
    return _m.hypot(a_, bb), _m.degrees(_m.atan2(bb, a_)) % 360
_longe = lambda h, de: min(abs(_oklch(h)[1] - _oklch(de)[1]) % 360, 360 - abs(_oklch(h)[1] - _oklch(de)[1]) % 360)
def _lum2(h):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return sum(k * f(int(h[i:i + 2], 16) / 255) for k, i in zip((0.2126, 0.7152, 0.0722), (0, 2, 4)))
_ct2 = lambda x, y: (max(_lum2(x), _lum2(y)) + 0.05) / (min(_lum2(x), _lum2(y)) + 0.05)
_vivas, _neutras, _barra_ruim = 0, 0, []
for _n in _pg:
    for _v in ("claro", "escuro"):
        _c = _pg[_n][_v]["cores"]
        _croma = _oklch(_c["barra"])[0]
        _viva = _croma >= 0.08 and _longe(_c["barra"], "C2334D") > 35 and _longe(_c["barra"], "D89B3A") > 30
        _neutra = _croma <= 0.06
        _vivas, _neutras = _vivas + _viva, _neutras + (_neutra and not _viva)
        if not (_viva or _neutra) or _ct2(_c["barra"], _c["painel"]) < 3.0:
            _barra_ruim.append((_n, _v, _c["barra"]))
checa(f"a barra cheia é viva em {_vivas} temas e neutra em {_neutras}: nenhuma viva é parente do âmbar nem do vermelho de vida baixa, e todas leem sobre o painel",
      _vivas + _neutras == 122 and _vivas >= 40 and _neutras >= 20 and not _barra_ruim, str(_barra_ruim[:4]))
_enf = [(n, v) for n in _pg for v in ("claro", "escuro") if any("enfeite no tom da régua" in a for a in _pg[n][v]["avisos"])]
checa(f"em {len(_enf)} das 122 a tinta de enfeite sai no tom da régua, porque a segunda cor do tema é fraca e sem parente; o Alfazema é uma delas",
      6 <= len(_enf) <= 30 and ("Alfazema", "claro") in _enf, str(_enf[:5]))

print("\nAS NOTAS DE REGRA DO Codigo.gs")
# v0.240 do sistema, o resto do B8: a fórmula da CD já era a do manual, e a nota que aparece ao
# passar o mouse continuava dizendo "o 2 é fixo". Nenhum validador lia as notas. A fórmula sai do
# manual.txt, e a nota tem de trazê-la.
import re as _rn
_MANN = " ".join(open("manual.txt", encoding="utf-8").read().split())
_CODN = open("apps-script/Codigo.gs", encoding="utf-8").read()
_mcd = _rn.search(r"CD de feitiço = ([^.]+)\.", _MANN)
_mno = _rn.search(r"'cd de feitiço':\s*((?:'[^']*'\s*\+?\s*)+)", _CODN)
_nota = "".join(_rn.findall(r"'([^']*)'", _mno.group(1))) if _mno else ""
# v0.246 do sistema, o B3: a nota do EQUIPAMENTO mandava digitar a proteção e citava o capítulo 12,
# e o escudo somava calado. O campo virou menu, e o refino escolhido ganhou nota.
_nq = _rn.search(r"'equipamento':\s*((?:'[^']*'\s*\+?\s*)+)", _CODN)
_nr = _rn.search(r"'refino escolhido':\s*((?:'[^']*'\s*\+?\s*)+)", _CODN)
_np = _rn.search(r"'proteção':\s*((?:'[^']*'\s*\+?\s*)+)", _CODN)
_txt = lambda m: "".join(_rn.findall(r"'([^']*)'", m.group(1))) if m else ""
checa("as notas do equipamento, da proteção e do refino escolhido dizem a regra de hoje",
      "FICHA PESSOAL" in _txt(_nq) and "capítulo 12" not in _txt(_nq) and "digite" not in _txt(_nq)
      and "Escudo soma" in _txt(_np) and "no máximo uma por marco" in _txt(_nr),
      f"equipamento: {_txt(_nq)[:50]} · proteção: {_txt(_np)[:50]} · refino: {_txt(_nr)[:50]}")
checa("a nota da CD de feitiço traz a fórmula do manual",
      bool(_mcd) and _mcd.group(1) in _nota,
      f"manual: {_mcd.group(1) if _mcd else '?'} · nota: {_nota[:80]}")

print("\nO SCRIPT QUE CONSTRÓI A PLANILHA")
import os as _o
GS = "apps-script/Ficha.gs"
checa("o script foi emitido", _o.path.exists(GS))
if _o.path.exists(GS):
    g = open(GS, encoding="utf-8").read()
    checa("ele avisa que é gerado, e não editado na mão", "não edite este arquivo" in g)
    # 06/10/2026: a INVOCAÇÕES e a DADOS_INVOC moram no Invocacoes.gs, que se junta ao ABAS quando o script carrega
    GS_INV = "apps-script/Invocacoes.gs"
    g_inv = open(GS_INV, encoding="utf-8").read() if _o.path.exists(GS_INV) else ""
    checa(f"ele e o Invocacoes.gs trazem as {len(DEC['C6_documento']['abas'])} abas decididas", all(f'"{a}"' in g + g_inv for a in DEC["C6_documento"]["abas"]))
    checa("o Invocacoes.gs só declara as abas dele e chama a junção: quem carregar por último junta",
          "var ABAS_DA_INVOCACAO = " in g_inv and "if (typeof juntarAbas_ === 'function') juntarAbas_(ABAS_DA_INVOCACAO);" in g_inv
          and "if (typeof ABAS_DA_INVOCACAO !== 'undefined' && ABAS_DA_INVOCACAO) juntarAbas_(ABAS_DA_INVOCACAO);" in g and "function " not in g_inv)
    checa(f"o Invocacoes.gs cabe no Apps Script ({len(g_inv) / 1024:.0f} KB, o teto é de 900 por arquivo)", 0 < len(g_inv) / 1024 < 900)
    checa("ele traz a arte embutida, sem depender de URL",
          '.png":"' in g.split("var ARTE")[1][:400] and "http" not in g.split("var ARTE")[1][:200])
    checa("ele define as caixas de seleção pela posição medida",
          '"caixas"' in g and "insertCheckboxes" in g)
    checa("a altura de linha vai em pixel, e não em ponto convertido",
          "setRowHeight" in g)
    # O idioma da planilha manda na pontuação de toda fórmula que o script escreve. Em 15/09/2026 a
    # montagem numa planilha em português deixou #ERROR! em todas as fórmulas com vírgula. O
    # construir() tem de trocar para inglês antes de montar, e forçar pt_BR num finally que venha
    # depois da última escrita.
    #
    # 18/09/2026: era "devolver o idioma de antes", lido de ss.getSpreadsheetLocale() no começo —
    # e uma planilha nova do Google Sheets nasce no idioma da CONTA de quem criou, não do produto.
    # "Devolver" repunha en_US quando a conta já era en_US, e a ficha saía em inglês sem ninguém
    # ter pedido. A ficha é em português sempre, então o fim é sempre pt_BR, não o que estava antes.
    _fc = _rn.search(r"function construir\(\) \{(.*?)\n\}\n", g, _rn.S)
    _corpo = _fc.group(1) if _fc else ""
    _virg = [x for x in formulas if "," in _rn.sub(r'"[^"]*"', "", x)]
    _i_le = _corpo.find("getSpreadsheetLocale()")
    _i_troca = _corpo.find("setSpreadsheetLocale('en_US')")
    _i_monta = _corpo.find("montarAba_(")
    _i_ultima = max(_corpo.find(k) for k in ("menusSuspensos_(", "acabamento_("))
    _i_final = _corpo.find("} finally {")
    _i_volta = _corpo.find("setSpreadsheetLocale('pt_BR')")
    checa(f"a ficha tem {len(_virg)} fórmula(s) com vírgula, então o idioma da montagem importa", len(_virg) > 0)
    checa("o construir() monta em inglês e força pt_BR num finally, depois da última escrita",
          0 <= _i_le < _i_troca < _i_monta and 0 <= _i_ultima < _i_final < _i_volta,
          f"lê {_i_le} · troca {_i_troca} · monta {_i_monta} · última {_i_ultima} · finally {_i_final} · volta {_i_volta}")
    checa("o pt_BR final não é o idioma capturado no começo — senão uma planilha que nasceu em "
          "inglês ficaria em inglês", "setSpreadsheetLocale(idioma)" not in _corpo)
    tam = len(g) / 1024
    checa(f"o arquivo cabe no Apps Script ({tam:.0f} KB, o limite é ~1 MB)", tam < 900)
    # A caixa desmarcada vale FALSO, e FALSO nao e "". A formula antiga somava
    # maestria em TODA pericia com a caixa vazia. A checagem precisa ser
    # exata: so as celulas que REALMENTE tem caixa, lidas do proprio script.
    import re as _re, json as _j
    cx = []
    for bloco in _re.findall(r'"caixas":(\[\[.*?\]\])', g):
        cx += _j.loads(bloco)
    tem_caixa = {f"${L(c)}${r}" for c, r0, n in cx for r in range(r0, r0 + n)}
    checa(f"o script sabe de {len(tem_caixa)} células com caixa de seleção",
          len(tem_caixa) >= 30, str(len(tem_caixa)))
    erradas = [c.value for l in f.iter_rows() for c in l
               if isinstance(c.value, str) and c.value.startswith("=")
               and any(cel + '=""' in c.value for cel in tem_caixa)]
    checa("nenhuma fórmula testa vazio numa célula que tem caixa de seleção",
          not erradas, str(erradas[:2]))

print("\nOS DADOS DO SCRIPT, CONFERIDOS SEM EXECUTAR")
# Nao existe runtime de JavaScript aqui: quem executa Apps Script e o Google.
# O que da para conferir e a METADE de dados do script -- e o 'Range not found'
# que quebrou a montagem era dessa metade, entao vale.
if _o.path.exists(GS):
    import json as _js
    # 01/10/2026: o ABAS como o script o usa. As fileiras de cartas da FICHA AMALDIÇOADA que sao copia vem escritas so
    # uma vez no Ficha.gs, e o proprio script as expande quando carrega; aqui quem expande e o emitir_gs.expandir.
    sys.path.insert(0, "ficha")
    import emitir_gs as _eg
    dados = _eg.abas_do_script(GS)
    nomes = {a["nome"] for a in dados}
    checa("as abas do script são as decididas", nomes == set(DEC["C6_documento"]["abas"]),
          str(nomes ^ set(DEC["C6_documento"]["abas"])))
    fora, artefalta, estilo_ruim = [], [], []
    for a in dados:
        nc, nr = a["cols"], a["rows"]
        for v in a["vals"]:
            if not (1 <= v[0] <= nr and 1 <= v[1] <= nc): fora.append((a["nome"], v[:2]))
            if len(v) > 3 and v[3] >= len(a["estilos"]): estilo_ruim.append((a["nome"], v[:2]))
        for m in a["merges"]:
            if not (m[2] <= nr and m[3] <= nc): fora.append((a["nome"], "merge", m))
        for im in a["imgs"]:
            if not (1 <= im[0] <= nr and 1 <= im[1] <= nc): fora.append((a["nome"], "img", im))
        for cx in a.get("caixas", []):
            if not (1 <= cx[1] and cx[1] + cx[2] - 1 <= nr): fora.append((a["nome"], "caixa", cx))
    checa("nada cai fora dos limites da aba", not fora, str(fora[:3]))
    checa("toda célula com estilo aponta para um estilo que existe", not estilo_ruim,
          str(estilo_ruim[:3]))

    # ESTA e a checagem do erro que quebrou a montagem: menu suspenso aponta
    # para outra aba, e a aba de destino nasce depois. Por isso ele foi movido
    # para o fim -- e por isso a checagem confere que a origem existe.
    ruins = []
    for a in dados:
        for alvo, fonte in a["dv"]:
            aba_fonte = fonte.split("!")[0].strip("=") if "!" in fonte else a["nome"]
            if aba_fonte not in nomes:
                ruins.append((a["nome"], fonte))
    checa("todo menu suspenso puxa de uma aba que existe", not ruins, str(ruins[:3]))
    checa("os menus são aplicados só depois de todas as abas nascerem",
          "menusSuspensos_" in g and "setDataValidation" not in
          g[g.index("function montarAba_"):g.index("function mat_")])


    # E os menus RODADOS: o menusSuspensos_ do script num Sheets de mentira, que recusa o endereço
    # que o de verdade recusa. Em 15/09/2026 a montagem parou em 'Range not found', porque o Sheets
    # exporta menu de itens como lista escrita, "a,b,c", e a checagem de cima deixava ela passar:
    # lista escrita não tem aba, então caía na própria aba e saía verde.
    import shutil as _sh, subprocess as _sp
    _ini = g.find("function menusSuspensos_(")
    _node = _sh.which("node") or _sh.which("nodejs")
    if _ini < 0:
        checa("o script tem o menusSuspensos_", False)
    elif not _node:
        print("  [--] node nao existe nesta maquina: os menus nao foram rodados")
    else:
        _prof, _fim = 0, None
        for _k in range(g.index("{", _ini), len(g)):
            if g[_k] == "{":
                _prof += 1
            elif g[_k] == "}":
                _prof -= 1
                if _prof == 0:
                    _fim = _k + 1
                    break
        _abas = [{"nome": a["nome"], "dv": a["dv"]} for a in dados]
        _prog = ("const ABAS = " + _js.dumps(_abas, ensure_ascii=False) + ";\n" + """
const A1 = /^[A-Z]+[0-9]+(:[A-Z]+[0-9]+)?$/;
const regras = [];
const ss = {
  getSheetByName: (nome) => ({ getRange(r) {
    if (!A1.test(r)) throw new Error('Range not found: ' + nome + '!' + r);
    return { setDataValidation: (v) => regras.push([nome, r, v]) };
  } }),
  getRange(r) {
    const m = /^'?([^'!]+)'?!([A-Z]+[0-9]+(:[A-Z]+[0-9]+)?)$/.exec(r);
    if (!m || !ABAS.some((a) => a.nome === m[1])) throw new Error('Range not found: ' + r);
    return { faixa: r };
  },
};
const SpreadsheetApp = { newDataValidation() {
  const v = {};
  const b = { requireValueInList(l) { v.lista = l; return b; },
              requireValueInRange(f) { v.faixa = f.faixa; return b; },
              setAllowInvalid() { return b; }, build() { return v; } };
  return b;
} };
""" + g[_ini:_fim] + """
try { menusSuspensos_(ss); console.log(JSON.stringify({ regras })); }
catch (e) { console.log(JSON.stringify({ erro: e.message })); }
""")
        _r = _sp.run([_node, "-e", _prog], capture_output=True, text=True)
        try:
            _saida = _js.loads(_r.stdout.strip().splitlines()[-1])
        except Exception:
            _saida = {"erro": (_r.stderr or _r.stdout)[-300:]}
        checa("os menus rodam num Sheets que recusa endereço inválido", "erro" not in _saida,
              _saida.get("erro", ""))
        if "erro" not in _saida:
            _esp = {}
            for a in dados:
                for alvo, fonte in a["dv"]:
                    _ml = _re.fullmatch(r'"(.*)"', fonte)
                    _esp[(a["nome"], alvo.replace("$", ""))] = (
                        {"lista": _ml.group(1).split(",")} if _ml else {"faixa": fonte.replace("$", "")})
            _got = {(n, r): v for n, r, v in _saida["regras"]}
            checa(f"cada um dos {len(_esp)} menus sai com a lista ou a faixa da planilha exportada",
                  _got == _esp, str([k for k in _esp if _got.get(k) != _esp[k]][:3]))

    # As bordas, o formato da célula vazia e as imagens, contra a planilha que o monta.py gerou. Em
    # 15/09/2026 a ficha montada no Sheets saiu sem caixa nenhuma: o emissor só levava a borda de cima,
    # e só de célula com valor -- 1615 lados de 6272 na FICHA --, deixava a caixa vazia de digitar sem
    # alinhamento, e punha a imagem solta, com o tamanho do arquivo e não o da tela.
    from openpyxl.utils.cell import range_boundaries as _rb
    import base64 as _b64, struct as _st

    def _cor_x(c):
        rgb = getattr(c, "rgb", None) if c is not None else None
        if not isinstance(rgb, str) or rgb.upper() == "00000000":
            return None
        return "#" + rgb[-6:].upper()

    # A borda de célula que mora numa mesclagem conta para o BLOCO: o Sheets só guarda formato no
    # canto dela, e a borda aplicada numa célula de dentro some -- foram os contornos da direita e
    # de baixo que faltaram na montagem de 15/09/2026. Faixa que corta mesclagem é defeito.
    _lados_scr, _lados_viva, _cortes = set(), set(), []
    for a in dados:
        ws_ = wb[a["nome"]]
        _dono = {}
        for m in ws_.merged_cells.ranges:
            for rr in range(m.min_row, m.max_row + 1):
                for cc in range(m.min_col, m.max_col + 1):
                    _dono[(rr, cc)] = m.coord
        _blocos = set(_dono.values())
        for b in a.get("bordas", []):
            if len(b) != 4 or not isinstance(b[3], list):
                continue
            for fx in b[3]:
                if fx in _blocos:
                    _lados_scr.add((a["nome"], fx, b[0], b[1], b[2]))
                    continue
                mc, mr, xc, xr = _rb(fx)
                for rr in range(mr, xr + 1):
                    for cc in range(mc, xc + 1):
                        if (rr, cc) in _dono:
                            _cortes.append((a["nome"], fx, b[0], _dono[(rr, cc)]))
                        _lados_scr.add((a["nome"], f"{L(cc)}{rr}", b[0], b[1], b[2]))
        for linha in ws_.iter_rows():
            for cel in linha:
                for lado in ("top", "bottom", "left", "right"):
                    s = getattr(cel.border, lado)
                    if s is not None and s.style:
                        onde = _dono.get((cel.row, cel.column), cel.coordinate)
                        _lados_viva.add((a["nome"], onde, lado, s.style, _cor_x(s.color) or "#000000"))
    checa(f"as bordas do script são as da planilha, e a de mesclagem vai no bloco inteiro ({len(_lados_viva)} lados)",
          len(_lados_viva) > 0 and _lados_scr == _lados_viva and not _cortes,
          f"faltam {len(_lados_viva - _lados_scr)}, sobram {len(_lados_scr - _lados_viva)}, "
          f"faixas que cortam mesclagem {len(_cortes)}: {(_cortes or sorted(_lados_viva - _lados_scr))[:2]}")

    # Achado testando no Sheets em 19/09/2026: a caixa ORIGEM nasceu com borda branca fina em três
    # lados (engano de formatação manual), e a troca de paleta nunca repintava ela porque branco não é
    # a régua. O ficha-v01/correcoes_borda.py dá a ela a borda da CAMINHO. E o título do GLOSSÁRIO saía
    # sem a borda da esquerda, porque o CATÁLOGO, de onde o estilo vem, guarda a ponta esquerda numa
    # célula a parte (C1:C2) que o GLOSSÁRIO não copiava.
    def _tem_lado(nome_aba, faixa, lado, traco="medium", cor="#8A7EC4"):
        _aba = next(a for a in dados if a["nome"] == nome_aba)
        return any(b[0] == lado and b[1] == traco and b[2] == cor and faixa in b[3] for b in _aba["bordas"])
    checa("a caixa ORIGEM tem a régua média nos quatro lados, igual à CAMINHO",
          all(_tem_lado("CARTEIRA", "AK17:AT17", l) for l in ("top", "bottom", "left", "right")))
    checa("nenhuma borda branca fixa sobrou na CARTEIRA (a troca de paleta não repinta o que não é régua)",
          not any(b[2] == "#FFFFFF" for b in next(a for a in dados if a["nome"] == "CARTEIRA")["bordas"]))
    checa("o título do GLOSSÁRIO (B1:V2) tem a borda da esquerda, e não só a de cima e a de baixo",
          all(_tem_lado("GLOSSÁRIO", "B1:V2", l) for l in ("top", "bottom", "left")))

    _vazias, _fmt_ruim = 0, []
    for a in dados:
        _tem = {(v[0], v[1]): a["estilos"][v[3]] for v in a["vals"] if len(v) > 3}
        for linha in wb[a["nome"]].iter_rows():
            for cel in linha:
                if cel.__class__.__name__ == "MergedCell" or cel.value is not None:
                    continue
                al = cel.alignment
                quer = (al.horizontal or "left",
                        "middle" if al.vertical in (None, "center") else al.vertical,
                        bool(al.wrap_text), bool(cel.font.i), bool(cel.font.b))
                if quer == ("left", "middle", False, False, False):
                    continue
                _vazias += 1
                e = _tem.get((cel.row, cel.column))
                got = None if e is None else (
                    e[4], "middle" if e[5] in ("middle", "center") else e[5],
                    bool(e[8]) if len(e) > 8 else False, bool(e[7]) if len(e) > 7 else False, bool(e[3]))
                if got != quer:
                    _fmt_ruim.append((a["nome"], cel.coordinate, quer, got))
    checa(f"as {_vazias} células vazias levam o alinhamento, a quebra, o itálico e o negrito da planilha",
          _vazias > 0 and not _fmt_ruim, str(_fmt_ruim[:3]))

    _lay = _js.load(open("ficha-v01/layout.json", encoding="utf-8"))
    # 17/09/2026: a limpeza 13 aumenta a foto da CARTEIRA, então a caixa esperada é a de depois dela
    sys.path.insert(0, "ficha-v01")
    import ficha_layout as _fl
    for _nome, _ims in _fl.trocas(_js.load(open("ficha-v01/layout.json", encoding="utf-8")))["imagens"].items():
        next(a for a in _lay["abas"] if a["nome"] == _nome)["imagens"] = _ims
    # 02/10/2026: a limpeza 27 (as Habilidades) põe a arte de respingos ao lado do título da seção 7
    import habilidades as _hb
    _fl7 = next(a for a in _lay["abas"] if a["nome"] == "FICHA")
    _fl7["imagens"] = [_hb.arte_no_titulo(i, _hb.linha_do_titulo(_fl7, 7)) if i["arquivo"] == _hb.ARTE else i for i in _fl7["imagens"]]
    # 03/10/2026: a limpeza 28 (moldura_foto.py) tira a moldura de dentro da caixa da foto e põe um canto em cada quina
    import moldura_foto as _mf
    _lmf = _js.load(open("ficha-v01/layout.json", encoding="utf-8"))
    _fl.aplica(_lmf, _fl.trocas(_lmf))
    _cmf = next(a for a in _lay["abas"] if a["nome"] == "CARTEIRA")
    _cmf["imagens"] = [i for i in _cmf["imagens"] if i["arquivo"] != _mf.ARTE_VELHA] + _mf.trocas(_lmf)["cantos"]
    _mart = _re.search(r"var ARTE = (\{.*?\});\n", g, _re.S)
    # 18/09/2026: a arte grande vem em pedaços concatenados por "+" (emitir_gs._sem_linha_gigante),
    # pra nenhuma linha do Ficha.gs travar o editor do Apps Script — colada de volta antes do JSON.
    _arte = _js.loads(_re.sub(r'"\s*\+\s*"', '', _mart.group(1))) if _mart else {}
    _por = {a["nome"]: a for a in dados}
    _img_ruim, _n_img = [], 0
    for la in _lay["abas"]:
        sp = _por.get(la["nome"])
        for i in la["imagens"]:
            _n_img += 1
            cand = [im for im in (sp["imgs"] if sp else []) if str(im[4]).startswith(i["arquivo"][:-4] + "-")]
            if len(cand) > 1:          # a mesma arte em duas caixas (os cantos da moldura da foto): a da célula da imagem
                cand = [im for im in cand if im[0] <= i["lin"] <= im[2] and im[1] <= i["col"] <= im[3]]
            if len(cand) != 1 or len(cand[0]) != 5:
                _img_ruim.append((la["nome"], i["arquivo"], "sem caixa no script"))
                continue
            l1, c1, l2, c2, chave = cand[0]
            cpx = lambda c: next((px for x1, x2, px in sp["largs"] if x1 <= c <= x2), sp["larg"])
            rpx = lambda r: sp["alturas"].get(str(r), 21)
            x0 = sum(cpx(c) for c in range(1, i["col"])) + i.get("desloc_x", 0)
            y0 = sum(rpx(r) for r in range(1, i["lin"])) + i.get("desloc_y", 0)
            bx, by = sum(cpx(c) for c in range(1, c1)), sum(rpx(r) for r in range(1, l1))
            bw = sum(cpx(c) for c in range(c1, c2 + 1))
            bh = sum(rpx(r) for r in range(l1, l2 + 1))
            tx = max(cpx(c) for c in range(c1, c2 + 1))
            ty = max(rpx(r) for r in range(l1, l2 + 1))
            if (abs(bx - x0) > tx or abs(bx + bw - x0 - i["larg"]) > tx
                    or abs(by - y0) > ty or abs(by + bh - y0 - i["alt"]) > ty):
                _img_ruim.append((la["nome"], i["arquivo"], "caixa longe da imagem da planilha",
                                  (bx, by, bw, bh), (x0, y0, i["larg"], i["alt"])))
            ws_ = wb[la["nome"]]
            for rr in range(l1, l2 + 1):
                for cc in range(c1, c2 + 1):
                    if ws_.cell(rr, cc).value not in (None, ""):
                        _img_ruim.append((la["nome"], i["arquivo"], "valor embaixo", rr, cc))
            for m in ws_.merged_cells.ranges:
                if m.coord == f"{L(c1)}{l1}:{L(c2)}{l2}":
                    continue          # a exportação da ficha montada já traz a caixa mesclada
                if not (m.max_row < l1 or m.min_row > l2 or m.max_col < c1 or m.min_col > c2):
                    _img_ruim.append((la["nome"], i["arquivo"], "mesclagem cortada", str(m)))
            png = _b64.b64decode(_arte.get(chave, ""))[:24]
            wh = _st.unpack(">II", png[16:24]) if len(png) >= 24 else (0, 0)
            if wh != (2 * bw, 2 * bh):
                _img_ruim.append((la["nome"], i["arquivo"], "arte fora do formato da caixa", wh, (2 * bw, 2 * bh)))
    checa(f"as {_n_img} imagens entram dentro da célula, numa caixa livre do tamanho da tela",
          _n_img > 0 and not _img_ruim, str(_img_ruim[:3]))
    checa("o molde põe a imagem na célula, e não solta", "newCellImage" in g and "insertImage" not in g)

    # B25, achado testando no Sheets em 18/09/2026: configurarPaleta_ ancorava a caixa da paleta
    # com cart.getImages(), que só enxerga imagem SOLTA sobre a grade — e a linha acima prova que
    # esta ficha nunca solta imagem. getImages() sempre vinha vazio, e a caixa nunca nascia. A
    # checagem abaixo trava as duas partes do conserto: acharCaixaDaFoto_ lê o VALOR da célula
    # (a propriedade valueType da CellImage, não getImages), e configurarPaleta_ passa pela função
    # nova em vez de voltar a chamar getImages direto.
    _acha = re.search(r"function acharCaixaDaFoto_\(sh\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("acharCaixaDaFoto_ acha a foto pelo valueType da CellImage, não por getImages",
          bool(_acha) and "getImages" not in _acha.group(1)
          and "valueType" in _acha.group(1) and "SpreadsheetApp.ValueType.IMAGE" in _acha.group(1)
          # 03/10/2026: a caixa da foto fica vazia até o jogador inserir a imagem, e a CARTEIRA declara onde ela mora
          and _acha.group(1).find("spec.foto") >= 0 and _acha.group(1).find("spec.foto") < _acha.group(1).find("valueType"))
    _confp = re.search(r"function configurarPaleta_\(ss, force\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("configurarPaleta_ ancora a caixa da paleta em acharCaixaDaFoto_, não em getImages direto",
          bool(_confp) and "acharCaixaDaFoto_(" in _confp.group(1) and "getImages" not in _confp.group(1))

    # B25, achado testando no Sheets em 18/09/2026: o intervalo nomeado da paleta sobrevive ao
    # construir() apagar e recriar a CARTEIRA (mesmo nome de aba, o Google parece religar por
    # nome) — sem o force, "já existia" continuava batendo pra sempre depois da primeira rodada,
    # e a caixa antiga (posição, largura, borda na régua velha) nunca era recriada por uma versão
    # nova do Codigo.gs, mesmo colando o arquivo certo.
    checa("configurarPaleta_ recebe force e remove o intervalo nomeado velho quando force é true",
          bool(_confp) and "force" in _confp.group(1) and "removerNomesDaPaleta_(ss)" in _confp.group(1))
    # Achado testando no Sheets em 19/09/2026: removeNamedRange num nome que não existe não estoura na
    # hora, estoura na PRÓXIMA leitura, fora do try/catch — o construir() caiu com "O intervalo
    # "PALETA_AVISO" não existe." dentro do acharCaixaDaFoto_. Só se remove o que getNamedRanges lista.
    checa("nenhum removeNamedRange às cegas: os nomes da paleta saem por getNamedRanges, só os que existem",
          re.sub(r"/\*\*.*?\*/", "", _CODA, flags=re.S).count("removeNamedRange(") == 0
          and "ss.getNamedRanges().forEach" in _CODA)
    checa("o construir() chama configurarPaleta_ com force, não deixa a caixa da paleta sobreviver à rodada",
          "configurarPaleta_(ss, true)" in g)

    # B25, achado testando no Sheets em 18/09/2026: repintar a ficha inteira não cabe nos 30
    # segundos do onEdit simples, e o Apps Script mata a execução no meio sem avisar — a paleta
    # ficava "travada" a partir da segunda troca. De 18/09 a 25/09/2026 a saída foi um gatilho
    # instalável (6 minutos). Em 25/09/2026 o Mizuki achou que numa CÓPIA da ficha a cor não trocava:
    # a cópia não leva gatilho instalável, e criar um pede autorização de quem copia. Ele quer que só
    # copiar baste, como no código antigo dele. A troca voltou pro gatilho simples, em passos que cabem
    # no orçamento, e continua no próximo clique (onSelectionChange) — tudo sem autorização. As
    # checagens abaixo substituem as três do gatilho instalável, que deixou de existir.
    checa("a troca de paleta no onEdit simples passa por continuarPaleta_, com o valor antigo da caixa",
          bool(_oned) and "continuarPaleta_(inicio, e.oldValue, true)" in _oned.group(1)
          and "ehCelulaDaPaleta_(e.range)" in _oned.group(1))
    _conv = re.search(r"function convergirPaleta_\(inicio, orcamento, dica, primeira\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("convergirPaleta_ confere o tempo ANTES de cada passo e grava o progresso DEPOIS de cada um",
          bool(_conv) and re.search(r"for \(var i = 0; i < passos\.length; i\+\+\) \{.*?Date\.now\(\) - inicio.*?"
                                    r"> orcamento.*?props\.setProperty\(PROP_PENDENTE_, novo\).*?return passo;.*?"
                                    r"props\.setProperties\(\{ paleta_feito", _conv.group(1), re.S) is not None)
    checa("cada passo termina com SpreadsheetApp.flush(), pra o tempo dele não cair no passo seguinte",
          bool(_conv) and re.search(r"repintarBordas_\(ss, [^;]*;\s*\}\s*(//[^\n]*\n\s*)*SpreadsheetApp\.flush\(\);\s*feito\[passo\] = novo;",
                                    _conv.group(1)) is not None)
    _orc = re.search(r"var ORCAMENTO_SIMPLES_ = (\d+);", _CODA)
    checa("o orçamento de cada chamada fica abaixo dos 30 s do gatilho simples, com folga de pelo menos 5 s",
          bool(_orc) and int(_orc.group(1)) <= 25000, _orc.group(1) if _orc else "sem ORCAMENTO_SIMPLES_")
    # E pra caber de uma vez, sem clique: a régua pinta a caixa de quatro lados iguais numa operação só
    # (3.420 faixas viram 1.305), e as abas ocultas ficam fora da troca (29 mil células viram 20 mil).
    _rb2 = re.search(r"function repintarBordas_\(ss, paraRegua, soAba\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("a régua pinta numa operação só a caixa que tem os quatro lados no mesmo traço",
          bool(_rb2) and "l.top === l.left && l.top === l.bottom && l.top === l.right" in _rb2.group(1)
          and "todos || lado === 'top'" in _rb2.group(1))
    _pp = re.search(r"function passosDaPaleta_\(primeira\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("as abas ocultas ficam fora dos passos de cor da troca",
          bool(_pp) and "return !spec.oculta;" in _pp.group(1))
    # Com os tempos do Mizuki (25/09/2026) ainda não cabia. Partir da ficha de fábrica sem ler a planilha foi
    # medido e ficou mais lento (o custo é gravar, não ler): a troca voltou a ler, e a cor pintada à mão fica.
    # O pedido dele: cor e régua na troca, a arte quando alguém mexer na ficha, sem aviso. Aba por aba,
    # começando pela que o jogador está olhando, e a aba em que ele clica passa na frente.
    _rca = re.search(r"function repintarCoresDaAba_\(ss, spec, nomeAntigo, nomeNovo, trecho\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("a troca de cor de cada aba lê a planilha e parte do que está pintado (a cor pintada à mão fica)",
          bool(_rca) and "faixa.getBackgrounds()" in _rca.group(1) and "faixa.getFontColors()" in _rca.group(1)
          and "coresDoNome_(nomeAntigo)" in _rca.group(1))
    checa("cor e régua de cada aba vão juntas, e a aba que o jogador está olhando vem primeiro",
          bool(_pp) and "passosDaPaleta_(primeira)" in _CODA and "(b.nome === primeira) - (a.nome === primeira)" in _pp.group(1)
          and re.search(r"passos\.push\('cor:' \+ spec\.nome \+ \(t \? ':' \+ t\[0\] \+ '-' \+ t\[1\] : ''\)\);\s*if \(i === 0 && \(spec\.bordas \|\| \[\]\)\.length\) passos\.push\('borda:'", _pp.group(1)) is not None)
    _onsc2 = re.search(r"function onSelectionChange\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("o clique leva a aba em que o jogador clicou pra frente da fila",
          bool(_onsc2) and "e && e.range" in _onsc2.group(1) and "onde ? onde.getSheet().getName() : null" in _CODA)
    _cont2 = re.search(r"function continuarPaleta_\(inicio, dica, marcar, onde\)\s*\{(.*?)\n\}", _CODA, re.S)
    _conv2 = re.search(r"function convergirPaleta_\(inicio, orcamento, dica, primeira\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("a troca não mostra aviso nenhum ao jogador",
          bool(_cont2) and bool(_conv2) and "toast(" not in _cont2.group(1) and "toast(" not in _conv2.group(1))
    checa("o primeiro passo de uma chamada fresca sempre roda (um passo lento não fica parado pra sempre)",
          bool(_conv) and "var fresca = andou === 0" in _conv.group(1) and "!fresca &&" in _conv.group(1))
    _onsc = re.search(r"function onSelectionChange\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
    _onop = re.search(r"function onOpen\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("o clique (onSelectionChange) e a abertura (onOpen) continuam uma troca pendente",
          bool(_onsc) and "continuarPaleta_(" in _onsc.group(1) and bool(_onop) and "continuarPaleta_(" in _onop.group(1))
    _codsc = re.sub(r"/\*\*.*?\*/", "", _CODA, flags=re.S)
    checa("nenhum gatilho instalável é criado: a cópia de um jogador não o levaria",
          "newTrigger(" not in _codsc)
    _aplp = re.search(r"function aplicarPaleta_\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("aplicarPaleta_ só apaga o gatilho instalável velho da original, e não repinta nada",
          bool(_aplp) and "ScriptApp.deleteTrigger(t)" in _aplp.group(1) and "repintar" not in _aplp.group(1))
    checa("o construir() (configurarPaleta_ com force) zera o registro de passos, porque a ficha nasce de fábrica",
          bool(_confp) and "PROP_FEITO_" in _confp.group(1) and "PROP_PENDENTE_" in _confp.group(1))

    # B25, achado testando no Sheets em 18/09/2026: nada serializava duas execuções da troca —
    # trocar de tema rápido demais (a segunda troca disparando antes do repaint da primeira terminar)
    # deixava fundo/fonte de algumas células com uma mistura das duas paletas, um hex que não bate
    # com o papel de nenhum tema. É o "trava depois de algumas tentativas" que o Mizuki descreveu, e
    # o próprio Mizuki suspeitou da causa. O LockService serializa. Desde 25/09/2026 ele mora em
    # continuarPaleta_, com tryLock(0): quem não pega volta na hora, e o pendente fica pro próximo clique.
    _cont = re.search(r"function continuarPaleta_\(inicio, dica, marcar, onde\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("continuarPaleta_ usa LockService pra serializar trocas simultâneas",
          bool(_cont) and "LockService.getDocumentLock()" in _cont.group(1)
          and "tryLock(0)" in _cont.group(1) and "releaseLock()" in _cont.group(1))
    checa("o lock embrulha a leitura do estado, o repaint E a escrita — a convergirPaleta_ inteira",
          bool(_cont) and re.search(r"tryLock\(0\).*convergirPaleta_\(.*releaseLock\(\)", _cont.group(1), re.S) is not None)

    # B25, achado testando no Sheets em 19/09/2026, mesmo com o LockService: `repintarPaleta_` só
    # reconhecia uma célula comparando contra os doze papéis da paleta IMEDIATAMENTE anterior — uma
    # célula presa na cor de uma paleta de DUAS ou mais trocas atrás (de uma corrida de antes deste
    # conserto, ou de qualquer outro motivo) nunca mais era achada, porque a busca só olhava um
    # passo pra trás. `papelPorHexGlobal_` é a busca de resgate: o papel de um hex em QUALQUER uma
    # das 61 paletas, não só a anterior — chamada só quando a paleta anterior não acha nada, então
    # o caminho normal (sem corrupção) nunca muda de comportamento.
    _phg = re.search(r"function papelPorHexGlobal_\(\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("papelPorHexGlobal_ existe e registra a paleta de fábrica mais as 61 do catálogo",
          bool(_phg) and "PALETA_DE_FABRICA_" in _phg.group(1) and "Object.keys(PALETAS)" in _phg.group(1))
    _rep = re.search(r"function repintarCoresDaAba_\(ss, spec, nomeAntigo, nomeNovo, trecho\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("repintarCoresDaAba_ cai pra papelPorHexGlobal_ quando a paleta anterior não reconhece a célula",
          bool(_rep) and "papelPorHexAntes[f] || papelPorHexGlobal[f]" in _rep.group(1)
          and "papelPorHexAntes[t] || papelPorHexGlobal[t]" in _rep.group(1))

    # A5/B25, achado testando no Sheets em 19/09/2026: o vermelho de "passou da conta" só trocava a
    # FONTE, deixando o FUNDO no que o tema daquela hora estivesse — nalgumas paletas claras o
    # vermelho quase sumia dentro do fundo, sem contraste garantido nenhum. O vermelho (não o
    # âmbar, que é aviso mais brando) passou a forçar fundo E fonte junto, pra ficar legível
    # não importa o tema.
    _cde = re.search(r"function corDeEstado_\(ss, idx\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("o vermelho de corDeEstado_ força fundo E fonte branca, não só a fonte",
          bool(_cde) and _cde.group(1).count("setBackground('#C2334D').setFontColor('#FFFFFF')") == 2)

    # B25, 19/09/2026, o "problema grande" do Mizuki testando no Sheets: fonte escura em cima de fundo
    # escuro ("9 de 23 na criação" no Brasa Claro), porque cada cor trocava pelo SEU papel e nenhuma
    # checagem olhava o PAR. A rede de segurança lê o contraste que a célula tinha na ficha de fábrica
    # (do ABAS, sem histórico) e troca a fonte por uma cor da paleta quando o par novo lê pior.
    _rep = re.search(r"function repintarCoresDaAba_\(ss, spec, nomeAntigo, nomeNovo, trecho\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("repintarCoresDaAba_ passa cada fonte pela checagem de legibilidade contra o fundo NOVO da célula",
          bool(_rep) and "fonteLegivel_(novaFonte, novoFundo, desenho[ra][c]" in _rep.group(1)
          and "contrasteDeFabrica_(spec)" in _rep.group(1))
    _leg = re.search(r"function fonteLegivel_\(.*?\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("a checagem de legibilidade tem piso de 3,0 pro texto discreto e só cai em branco/preto por último",
          bool(_leg) and "PISO_DISCRETO_" in _leg.group(1) and "extremo" in _leg.group(1)
          and "var PISO_DISCRETO_ = 3.0;" in _CODA)
    checa("o âmbar de texto padrão segue a paleta, achado pelo endereço no ABAS (reversível), não pela cor",
          "celulasDeAviso_(spec)" in _rep.group(1) and "avisoNovo[papelDoFundo]" in _rep.group(1)
          and "aviso_por_papel" in _CODA)

    # A troca de paleta lê o PALETAS do próprio Codigo.gs: confere de verdade, nas 122 entradas, o que o
    # derivar.py prometia — o tinta CLARO nos temas claros (o cartão inteiro e a lombada não ficam
    # marrons no meio de um tema pêssego), o texto lendo sobre ele, e o aviso com contraste em cada fundo.
    _mp = re.search(r"var PALETAS = (\{.*?\n\});\n", _CODA, re.S)
    _pal = _js.loads(_mp.group(1)) if _mp else {}
    def _lum(h):
        f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return sum(k * f(int(h[i:i + 2], 16) / 255) for k, i in zip((0.2126, 0.7152, 0.0722), (0, 2, 4)))
    def _ct(a, b):
        la, lb = _lum(a), _lum(b)
        return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
    _tinta_ruim = [(n, v) for n, t in _pal.items() for v in ("claro", "escuro")
                   if (_lum(t[v]["tinta"]) < 0.6 if v == "claro" else _lum(t[v]["tinta"]) > 0.05)]
    checa(f"o tinta é pastel nas {len(_pal)} paletas claras e quase preto nas escuras, e o texto lê sobre ele",
          len(_pal) == 61 and not _tinta_ruim
          and all(_ct(t[v]["texto"], t[v]["tinta"]) >= 4.5 for t in _pal.values() for v in ("claro", "escuro")),
          str(_tinta_ruim[:3]))
    _aviso_ruim = [(n, v, k) for n, t in _pal.items() for v in ("claro", "escuro")
                   for k, h in t[v].get("aviso_por_papel", {}).items() if _ct(h, t[v][k]) < 4.5]
    checa("o aviso_por_papel lê (4,5) sobre cada um dos fundos onde o âmbar padrão mora",
          len(_pal) == 61 and not _aviso_ruim and all("aviso_por_papel" in t[v] for t in _pal.values()
                                                       for v in ("claro", "escuro")), str(_aviso_ruim[:3]))

    # 19/09/2026: a lombada (fundo tinta, colunas A:B) da FICHA parava na linha 144 de 150, e a da
    # INVOCAÇÃO na 120 de 126 — invisível na ficha escura de fábrica, cortada numa paleta clara.
    for _nome_l in ("FICHA",):
        _al = next(a for a in dados if a["nome"] == _nome_l)
        _m2 = {}
        for _fx in _al["fundos"]:
            for _cc in range(_fx[1], min(_fx[2], 2) + 1):
                _m2[(_fx[0], _cc)] = _fx[3].upper()
        for _mg in _al["merges"]:      # a mesclagem só guarda a cor no canto: o bloco todo é a cor dele
            if _mg[1] <= 2:
                for _rr in range(_mg[0], _mg[2] + 1):
                    for _cc in (1, 2):
                        _m2[(_rr, _cc)] = _m2.get((_mg[0], _mg[1]), _al["fundo_base"].upper())
        _sem = [r for r in range(1, _al["rows"] + 1)
                if any(_m2.get((r, cc), _al["fundo_base"].upper()) != "#0A0810" for cc in (1, 2))]
        checa(f"a lombada da {_nome_l} (A:B em tinta) vai até a última das {_al['rows']} linhas",
              not _sem, f"sem lombada nas linhas {_sem[:6]}")

    # 19/09/2026, pedido do Mizuki: o texto curto que abria frase, título ou mensagem com a inicial
    # minúscula na INVOCAÇÃO e no CATÁLOGO ("técnica", "prende o alvo", "sobrou ponto"). A notação de dado
    # ("d20 +") fica minúscula de propósito.
    _minusc = []
    for _nome_t in ("GLOSSÁRIO",):
        for _v in next(a for a in dados if a["nome"] == _nome_t)["vals"]:
            _s = _v[2]
            if isinstance(_s, str) and not _s.startswith("=") and _s.strip() and _s.strip()[0].isalpha() \
                    and _s.strip()[0].islower() and not re.match(r"^\s*d\d", _s):
                _minusc.append((_nome_t, _v[0], _v[1], _s[:30]))
    checa("nenhum texto do GLOSSÁRIO abre com a inicial minúscula",
          not _minusc, str(_minusc[:3]))
    # 01/10/2026: a INVOCAÇÃO, o CATÁLOGO e a DADOS_INV saíram da ficha (ficha-v01/sem_invocacao.py), e com elas as
    # checagens do Jorro do CATÁLOGO e das mensagens das fórmulas da INVOCAÇÃO. O que se cobra agora é que nenhuma
    # das três volte, nem no .xlsx nem no script, e que nada do que ficou as cite.
    import sem_invocacao as _si
    _voltou = [n for n in _si.ABAS_FORA if n in wb.sheetnames or any(a["nome"] == n for a in dados)]
    _cita = [(a["nome"], v[0], v[1]) for a in dados for v in a["vals"] if isinstance(v[2], str) and v[2].startswith("=") and _si.cita(v[2])]
    _cita += [(a["nome"], d[0]) for a in dados for d in a.get("dv", []) if _si.cita("=" + str(d[1]))]
    checa("a INVOCAÇÃO, o CATÁLOGO e a DADOS_INV saíram da ficha, e nenhuma fórmula ou menu do que ficou cita uma delas",
          not _voltou and not _cita and list(DEC["C6_documento"]["abas_removidas_em_01_10"]["quais"]) == list(_si.ABAS_FORA),
          f"voltou {_voltou} · cita {_cita[:3]}")

    # 19/09/2026, pedido do Mizuki: uma linha simples entre a moldura da ficha (cabeçalho e lombada, em tinta)
    # e o miolo (em fundo), que numa paleta clara viravam dois pastéis quase iguais sem nada entre eles.
    def _cobre(nome_aba, lado, celulas):
        """as (linha, coluna) de `celulas` que NÃO têm a borda `lado` na régua média"""
        _ab = next(a for a in dados if a["nome"] == nome_aba)
        _ok = set()
        for _b in _ab["bordas"]:
            if _b[0] == lado and _b[1] == "medium" and _b[2] == "#8A7EC4":
                for _fx in _b[3]:
                    _c1, _r1, _c2, _r2 = _rb(_fx)
                    for _rr in range(_r1, _r2 + 1):
                        for _cc in range(_c1, _c2 + 1):
                            _ok.add((_rr, _cc))
        return [x for x in celulas if x not in _ok]
    _f, _c = (next(a for a in dados if a["nome"] == n_) for n_ in ("FICHA", "CARTEIRA"))
    _falta = {
        "FICHA, embaixo do cabeçalho (linha 5)": _cobre("FICHA", "bottom", [(5, c) for c in range(3, _f["cols"] + 1)]),
        "FICHA, à direita da lombada (coluna B)": _cobre("FICHA", "right", [(r, 2) for r in range(6, _f["rows"] + 1)]),
        "CARTEIRA, embaixo do cabeçalho (linha 4)": _cobre("CARTEIRA", "bottom", [(4, c) for c in range(1, _c["cols"] + 1)]),
    }
    for _onde, _sem in _falta.items():
        checa(f"a divisória na régua cobre a moldura inteira: {_onde}", not _sem, f"sem divisória em {_sem[:5]}")

    # 19/09/2026, pedido do Mizuki: "as imagens têm cores fixas, e vai rolar o que rolou no Eucalipto". A arte
    # inteira é de UMA cor (o que varia é o alfa) e sai como PNG de paleta; a troca de paleta reescreve a
    # paleta e o CRC (pngComCor_) e reenvia a imagem. O regressao-arte.js prova a recoloração no node.
    # Desde 25/09/2026 a troca roda em passos: a ordem mora em passosDaPaleta_, e a arte vem depois das cores.
    _rep_arte = re.search(r"function passosDaPaleta_\(primeira\)\s*\{(.*?)\n\}", _CODA, re.S)
    _pap = re.search(r"var PAPEL_DA_ARTE_ = \{(.*?)\};", _CODA, re.S)
    _prefixos = {re.sub(r"-\d+x\d+\.png$", "", k) for k in _js.loads(re.sub(r'"\s*\+\s*"', "", re.search(r"var ARTE = (\{.*?\n\});", g, re.S).group(1)))}
    checa("a troca de paleta recolore a arte, depois do fundo (é dele que a cor depende)",
          bool(_rep_arte) and _rep_arte.group(1).find("push('arte") > _rep_arte.group(1).find("push('cor:") >= 0
          and _rep_arte.group(1).find("push('arte") > _rep_arte.group(1).find("push('borda:") >= 0)
    checa(f"cada uma das {len(_prefixos)} imagens da ficha tem um papel de paleta em PAPEL_DA_ARTE_",
          bool(_pap) and all(f"'{p_}'" in _pap.group(1) for p_ in _prefixos), str(sorted(_prefixos)))
    checa("o construir() marca a imagem como NOSSA (título de alt PM-ARTE:), pra a troca nunca tocar na foto do jogador",
          "setAltTextTitle('PM-ARTE:' + im[4])" in g and "TAG_ARTE_ + im[4]" in _CODA)
    if _node:
        _r = _sp.run([_node, "regressao-arte.js"], capture_output=True, text=True, timeout=120)
        checa("a recoloração da arte gera PNG bem formado, com a cor pedida e sem mexer no alfa (regressao-arte.js)",
              _r.returncode == 0, (_r.stdout + _r.stderr).strip()[-300:])
        # 25/09/2026: a troca em passos, no gatilho simples, contra a mesma troca feita de uma vez só.
        _r = _sp.run([_node, "regressao-paleta.js"], capture_output=True, text=True, timeout=300)
        checa("a troca de paleta em passos cabe nos 30 s e sai igual à feita de uma vez (regressao-paleta.js)",
              _r.returncode == 0, (_r.stdout + _r.stderr).strip()[-300:])
    else:
        print("  [--] node nao existe nesta maquina: a recoloracao da arte nao foi rodada")

    # A caixinha que avisa da espera da troca de paleta, com o intervalo nomeado próprio pra a borda dela
    # ser repintada junto com a régua.
    _cfg = re.search(r"function configurarPaleta_\(ss, force\)\s*\{(.*?)\n\}", _CODA, re.S)
    _rb = re.search(r"function repintarBordas_\(ss, paraRegua, soAba\)\s*\{(.*?)\n\}", _CODA, re.S)
    checa("a caixa de aviso da espera existe, tem intervalo nomeado, e a borda dela é repintada",
          bool(_cfg) and "NOME_CEL_PALETA_AVISO_" in _cfg.group(1) and "TEXTO_AVISO_PALETA_" in _cfg.group(1)
          and "var TEXTO_AVISO_PALETA_ = 'O tema leva uns 20 segundos. O que faltar termina enquanto você usa a ficha.';" in _CODA
          and bool(_rb) and "NOME_CEL_PALETA_AVISO_" in _rb.group(1))

    # A pincelada clara do meio da CARTEIRA é de meio-tom, que lê no tinta claro e no escuro. (Até 03/10/2026 esta
    # checagem também via a moldura da foto sem miolo opaco: a moldura saiu de dentro da caixa, ver abaixo.)
    from PIL import Image as _PImg
    _pinc = _PImg.open("ficha-v01/arte/carteira-3.png").convert("RGBA")
    _cores_pinc = {p[:3] for p in _pinc.getdata() if p[3] > 200}
    checa("a pincelada do meio é de meio-tom (lê nos dois extremos)",
          len(_cores_pinc) == 1 and 0.12 < _lum("%02X%02X%02X" % list(_cores_pinc)[0]) < 0.24)

    # 03/10/2026, pedido do Mizuki: a foto entra NA célula, e não solta por cima ("a parte central ser uma celula só
    # mesclada, que o jogador clica e insere"), com a moldura em volta (a B+ do estudo: "vamos de B+"). A moldura solta
    # por cima foi recusada: "o jogador quando clicar vai acabar clicando na imagem ao invés do fundo". A regra, lida do
    # que o script manda para o Sheets:
    #   · a CARTEIRA declara a caixa da foto, e ela é uma caixa mesclada, sem imagem nenhuma dentro, com o convite
    #     escrito e a nota de como inserir;
    #   · no anel de uma célula em volta, cada célula tem o lado de fora na régua média, menos as duas quinas chanfradas
    #     (em cima à esquerda e embaixo à direita, como no desenho antigo da moldura);
    #   · cada quina chanfrada tem uma imagem na célula dela, só nela, o traço "/" de canto a canto, que nasce na régua
    #     e que a troca de paleta pinta na régua exata, a cor da borda em que ela emenda.
    from openpyxl.utils.cell import range_boundaries as _rbx
    _car = next(a for a in dados if a["nome"] == "CARTEIRA")
    _ft = _car.get("foto")
    _lados_regua = {}
    for _b in _car["bordas"]:
        if _b[1] == "medium" and str(_b[2]).upper() == "#8A7EC4":
            for _fx in _b[3]:
                _c1, _r1, _c2, _r2 = _rbx(_fx)
                for _rr in range(_r1, _r2 + 1):
                    for _cc in range(_c1, _c2 + 1):
                        _lados_regua.setdefault((_rr, _cc), set()).add(_b[0])
    _mold_ruim = []
    if not (_ft and len(_ft) == 4 and list(_ft) in [list(m) for m in _car["merges"]]):
        _mold_ruim.append(f"a caixa da foto {_ft} não é uma caixa mesclada da CARTEIRA")
    else:
        _l1, _c1, _l2, _c2 = _ft
        _dentro = [im[4] for im in _car["imgs"] if not (im[2] < _l1 or im[0] > _l2 or im[3] < _c1 or im[1] > _c2)]
        if _dentro:
            _mold_ruim.append(f"imagem dentro da caixa da foto: {_dentro}")
        _v = next((v for v in _car["vals"] if v[0] == _l1 and v[1] == _c1), None)
        if not _v or _v[2] != "FOTO\n顔":
            _mold_ruim.append(f"a caixa da foto não tem o convite: {_v}")
        if "Inserir imagem na célula" not in dict((n[0], n[1]) for n in _car.get("notas", [])).get(f"{L(_c1)}{_l1}", ""):
            _mold_ruim.append("a caixa da foto não tem a nota de como inserir")
        _quinas = {(_l1 - 1, _c1 - 1), (_l2 + 1, _c2 + 1)}
        _anel = {}
        for _cc in range(_c1 - 1, _c2 + 2):
            _anel.setdefault((_l1 - 1, _cc), set()).add("top"); _anel.setdefault((_l2 + 1, _cc), set()).add("bottom")
        for _rr in range(_l1 - 1, _l2 + 2):
            _anel.setdefault((_rr, _c1 - 1), set()).add("left"); _anel.setdefault((_rr, _c2 + 1), set()).add("right")
        for _k, _ls in sorted(_anel.items()):
            if _k in _quinas:          # a quina é chanfrada: reta nenhuma no lado de fora dela
                if _ls & _lados_regua.get(_k, set()):
                    _mold_ruim.append(f"a quina {L(_k[1])}{_k[0]} tem reta em {sorted(_ls & _lados_regua.get(_k, set()))}")
                continue
            if not _ls <= _lados_regua.get(_k, set()):
                _mold_ruim.append(f"{L(_k[1])}{_k[0]} sem a régua em {sorted(_ls - _lados_regua.get(_k, set()))}")
        _pap_mf = re.search(r"var PAPEL_DA_ARTE_ = \{(.*?)\};", _CODA, re.S).group(1)
        _borda_mf = re.search(r"var ARTE_DA_BORDA_ = \{(.*?)\};", _CODA, re.S)
        _arte_mf = _js.loads(_re.sub(r'"\s*\+\s*"', '', _re.search(r"var ARTE = (\{.*?\});\n", g, _re.S).group(1)))
        for _q in sorted(_quinas):
            _im = [im for im in _car["imgs"] if im[:4] == [_q[0], _q[1], _q[0], _q[1]]]
            if len(_im) != 1:
                _mold_ruim.append(f"a quina {L(_q[1])}{_q[0]} não tem uma imagem só, na célula dela: {_im}")
                continue
            _pref = re.sub(r"-\d+x\d+\.png$", "", _im[0][4])
            if f"'{_pref}': 'regua'" not in _pap_mf or not _borda_mf or f"'{_pref}': true" not in _borda_mf.group(1):
                _mold_ruim.append(f"a quina {_im[0][4]} não segue a régua exata na troca (PAPEL_DA_ARTE_ e ARTE_DA_BORDA_)")
            _png = _PImg.open(__import__("io").BytesIO(_b64.b64decode(_arte_mf[_im[0][4]]))).convert("RGBA")
            _w, _h = _png.size
            _a = lambda x, y: _png.getpixel((min(_w - 1, max(0, round(x * (_w - 1)))), min(_h - 1, max(0, round(y * (_h - 1))))))[3]
            _cor = {p[:3] for p in _png.getdata() if p[3] > 200}
            if not (_a(0.02, 0.98) > 128 and _a(0.98, 0.02) > 128 and _a(0.5, 0.5) > 128
                    and _a(0.02, 0.02) == 0 and _a(0.98, 0.98) == 0 and _cor == {(0x8A, 0x7E, 0xC4)}):
                _mold_ruim.append(f"a quina {_im[0][4]} não é o traço / de canto a canto na régua: {sorted(_cor)[:2]}")
    checa("a foto entra na célula: a caixa livre, com o convite e a nota, a moldura em volta na régua, e as duas quinas "
          "chanfradas em imagem na célula do canto, na régua exata", not _mold_ruim, str(_mold_ruim[:3]))
    # 05/10/2026, pedido do Mizuki: "A imagem que for colocada na carteira aparecer no ficha pessoal". Uma caixa só da
    # FICHA PESSOAL aponta para o canto da caixa da foto que a CARTEIRA declara; ela é do tamanho de uma foto (uma
    # mesclagem de 10 linhas ou mais), tem a nota que manda inserir na CARTEIRA, e fica fora da trava: se a referência
    # não mostrar a imagem inserida na célula (a documentação do Google não diz), o jogador insere a foto por cima.
    _fpa = next(a for a in dados if a["nome"] == "FICHA PESSOAL")
    _liga = f"=CARTEIRA!${L(_ft[1])}${_ft[0]}" if _ft and len(_ft) == 4 else None
    _aponta = [v for v in _fpa["vals"] if isinstance(v[2], str) and v[2].replace("$", "") == (_liga or "?").replace("$", "")]
    _foto_ruim = []
    if len(_aponta) != 1:
        _foto_ruim.append(f"{len(_aponta)} caixa(s) da FICHA PESSOAL apontam para a foto da CARTEIRA ({_liga})")
    else:
        _r, _c = _aponta[0][0], _aponta[0][1]
        _mf = next((m for m in _fpa["merges"] if m[0] == _r and m[1] == _c), None)
        if not _mf or _mf[2] - _mf[0] + 1 < 10:
            _foto_ruim.append(f"a caixa {L(_c)}{_r} não é do tamanho de uma foto: {_mf}")
        if "CARTEIRA" not in dict((n[0], n[1]) for n in _fpa.get("notas", [])).get(f"{L(_c)}{_r}", ""):
            _foto_ruim.append(f"a caixa {L(_c)}{_r} não tem a nota que manda inserir a foto na CARTEIRA")
        for _fx in _fpa.get("protegidas", []):
            _x1, _y1, _x2, _y2 = _rbx(_fx)
            if _y1 <= _r <= _y2 and _x1 <= _c <= _x2:
                _foto_ruim.append(f"a caixa {L(_c)}{_r} está na trava {_fx}")
    checa("a FICHA PESSOAL mostra a foto da CARTEIRA: uma caixa do tamanho de uma foto aponta para a caixa dela, com a nota, "
          "e fora da trava", not _foto_ruim, str(_foto_ruim[:3]))

    # A função que o Excel não tem sai do .xlsx embrulhada em IFERROR(__xludf.DUMMYFUNCTION("...")),
    # e remontada assim ela falha calada: foram as barras vazias de 15/09/2026. O script leva a de dentro.
    _embr = _re.compile(r'^=IFERROR\(__xludf\.DUMMYFUNCTION\("(.*)"\),(.*)\)$', _re.S)
    _n_emb, _emb_ruim = 0, []
    for a in dados:
        _sv = {(v[0], v[1]): v[2] for v in a["vals"]}
        for linha in wb[a["nome"]].iter_rows():
            for cel in linha:
                _me = _embr.match(cel.value) if isinstance(cel.value, str) else None
                if _me:
                    _n_emb += 1
                    if _sv.get((cel.row, cel.column)) != "=" + _me.group(1).replace('""', '"').strip():
                        _emb_ruim.append((a["nome"], cel.coordinate, str(_sv.get((cel.row, cel.column)))[:50]))
        _emb_ruim += [(a["nome"], v[0], v[1]) for v in a["vals"] if isinstance(v[2], str) and "__xludf" in v[2]]
    checa(f"as {_n_emb} fórmulas que o Sheets exportou embrulhadas saem com a função de dentro",
          _n_emb > 0 and not _emb_ruim, str(_emb_ruim[:3]))

    # A largura, a altura, o texto com cara de número e o fundo de base: o que a volta pelo Sheets
    # mostrou em 15/09/2026. Exportada de novo, a ficha montada vinha com as colunas da INVOCAÇÃO, do
    # CATÁLOGO, da DADOS e da DADOS_INV 12% mais estreitas -- o emissor fazia 7 x largura, e o Sheets
    # faz 8 x largura - 1 --, com altura em linha que a viva não declara, com "1" virando número, e
    # com a DADOS_INV pintada por inteiro.
    from collections import Counter as _Ct
    _med = _js.load(open("medidas/larguras-sheets.json", encoding="utf-8"))
    _pr = [p for p in _med["pares"] if round(8 * p[1] - 1) != p[0]]
    checa(f"a conta do Sheets reproduz os {len(_med['pares'])} pares de largura medidos",
          len(_med["pares"]) >= 3 and not _pr, str(_pr[:3]))
    _larg_r, _alt_r, _num_r, _fundo_r, _n_num = [], [], [], [], 0
    # o fundo se conta num arquivo aberto de novo: as checagens de cima leem a DADOS até a linha 199,
    # e o openpyxl cria célula vazia em cada leitura
    _wb_limpo = load_workbook(ARQ)
    for a in dados:
        ws_ = wb[a["nome"]]
        _w = {}
        for k, d in ws_.column_dimensions.items():
            if d.width:
                for cc in range(d.min, d.max + 1):
                    _w[cc] = d.width
        _base = ws_.column_dimensions["A"].width or 4.0
        for cc in range(1, a["cols"] + 1):
            quer = _px_col(_w.get(cc) or _base)
            tem = next((px for x1, x2, px in a["largs"] if x1 <= cc <= x2), a["larg"])
            if quer != tem:
                _larg_r.append((a["nome"], L(cc), quer, tem))
        _decl = {str(int(k)): max(2, int(round(d.height * 4 / 3))) for k, d in ws_.row_dimensions.items() if d.height}
        if a["alturas"] != _decl:
            _alt_r.append((a["nome"], sorted(set(a["alturas"].items()) ^ set(_decl.items()))[:3]))
        _sv = {(v[0], v[1]): v[2] for v in a["vals"]}
        _cnt = _Ct()
        for linha in ws_.iter_rows():
            for cel in linha:
                if cel.__class__.__name__ == "MergedCell":
                    continue
                if isinstance(cel.value, str) and _re.fullmatch(r"-?\d+(?:\.\d+)?", cel.value):
                    _n_num += 1
                    if _sv.get((cel.row, cel.column)) != "'" + cel.value:
                        _num_r.append((a["nome"], cel.coordinate, _sv.get((cel.row, cel.column))))
        for linha in _wb_limpo[a["nome"]].iter_rows():
            for cel in linha:
                if cel.__class__.__name__ != "MergedCell":
                    _cnt[_cor_x(cel.fill.start_color) if cel.fill and cel.fill.fill_type else None] += 1
        # 17/09/2026: None (celula sem pintura) nunca vira base -- vira null no Ficha.gs, e o script
        # trava tentando pintar a aba inteira de "sem cor" (achado do Mizuki no GLOSSARIO). A DADOS_INV
        # tinha o mesmo problema, oculta, e nunca apareceu.
        _cnt_pintado = _Ct({k: v for k, v in _cnt.items() if k is not None})
        _base_certa = _cnt_pintado.most_common(1)[0][0] if _cnt_pintado else "#120F1D"
        if a.get("fundo_base", "?") != _base_certa:
            _fundo_r.append((a["nome"], a.get("fundo_base", "?"), _cnt.most_common(2)))
    checa("cada coluna sai com a largura da planilha, pela conta do Sheets", not _larg_r, str(_larg_r[:3]))
    checa("cada linha sai com a altura que a planilha declara, e só ela", not _alt_r, str(_alt_r[:2]))
    checa(f"os {_n_num} textos com cara de número vão com apóstrofo", _n_num > 0 and not _num_r, str(_num_r[:3]))
    checa("o fundo de base de cada aba é o que a planilha mais usa", not _fundo_r, str(_fundo_r[:2]))

    # As fórmulas que citam uma aba que ainda não nasceu. A montagem segue a ordem do ABAS -- a
    # CARTEIRA antes da FICHA, a FICHA antes da DADOS, a INVOCAÇÃO antes da DADOS_INV --, e fórmula
    # gravada antes de a aba existir fica em #REF!. Elas têm de ser gravadas depois do laço das abas.
    _ordem, _cedo = [a["nome"] for a in dados], 0
    for _i, a in enumerate(dados):
        for v in a["vals"]:
            if isinstance(v[2], str) and v[2].startswith("="):
                _txt = _re.sub(r'"[^"]*"', '""', v[2])
                for _m in _re.finditer(r"(?:'([^']+)'|([A-Za-zÀ-ÿ_][\wÀ-ÿ]*))!", _txt):
                    _alvo = _m.group(1) or _m.group(2)
                    if _alvo in _ordem and _ordem.index(_alvo) > _i:
                        _cedo += 1
                        break
    _mc = _re.search(r"function construir\(\) \{(.*?)\n\}\n", g, _re.S)
    _mm = _re.search(r"function montarAba_\(aba, spec\) \{(.*?)\n\}\n", g, _re.S)
    _cc = _mc.group(1) if _mc else ""
    # 01/10/2026: o construir() estourou os seis minutos do Apps Script, e as fórmulas deixaram de esperar numa fila
    # (144 chamadas de setFormulas). Agora TODAS as abas nascem primeiro, vazias e do tamanho certo, e cada uma é
    # preenchida depois, com as fórmulas na mesma gravação dos valores. O que se cobra é a mesma coisa de antes: a
    # aba citada já existe quando a fórmula é gravada.
    _cria = _cc.find("criarAba_(")
    _fim_cria = _cc.find("});", _cria) if _cria >= 0 else -1
    _monta = _cc.find("montarAba_(")
    _fnc = _re.search(r"function criarAba_\(ss, spec, posicao\) \{(.*?)\n\}\n", g, _re.S)
    _fnc = _fnc.group(1) if _fnc else ""
    checa(f"{_cedo} fórmula(s) citam uma aba que nasce depois da delas, então a ordem da gravação importa",
          _cedo > 0)
    checa("todas as abas nascem, do tamanho certo, antes de a primeira ser preenchida, e as fórmulas vão com os valores",
          bool(_mm) and "r.setValues(v)" in _mm.group(1) and ".setFormula" not in g.split("function construir()")[1]
          and 0 <= _cria < _fim_cria < _monta and "insertSheet(spec.nome, posicao)" in _fnc
          and all(k in _fnc for k in ("deleteColumns(", "deleteRows(", "insertColumnsAfter(", "insertRowsAfter("))
          and "insertSheet(" not in _mm.group(1),
          f"cria {_cria} · fim do laço {_fim_cria} · monta {_monta}")
    # o acabamento pode rodar sozinho, e o construir() passa a vez a ele quando a montagem demora
    _fa = _re.search(r"function acabar\(\) \{(.*?)\n\}\n", g, _re.S)
    _fa = _fa.group(1) if _fa else ""
    checa("o construir() registra cada etapa na hora e, se a montagem passar do teto, deixa o acabamento para o acabar()",
          "rel.etapa(spec.nome)" in _cc and "rel.passou() > TETO_DA_MONTAGEM_" in _cc and "acabamento_(ss, feito, rel)" in _cc
          and "acabamento_(ss, feito, rel)" in _fa and "setSpreadsheetLocale('en_US')" in _fa
          and _fa.find("} finally {") < _fa.find("setSpreadsheetLocale('pt_BR')")
          and bool(_re.search(r"var TETO_DA_MONTAGEM_ = (\d+);", g)) and int(_re.search(r"var TETO_DA_MONTAGEM_ = (\d+);", g).group(1)) <= 300000,
          "falta o relógio, o teto ou o acabar()")

    arte_usada = {im[4] for a in dados for im in a["imgs"]}
    embutida = set(_re.findall(r'"([^"]+\.png)":"', g.split("var ARTE")[1][:200000]))
    checa("toda imagem usada está embutida no script", arte_usada <= embutida,
          str(sorted(arte_usada - embutida)))
    fontes_gs = {e[0] for a in dados for e in a["estilos"]}
    checa("o script só usa fonte conferida no seletor", fontes_gs <= CONF,
          str(sorted(fontes_gs - CONF)))

print(f"\n{'A FICHA CONFERE' if not FALHAS else f'{len(FALHAS)} PROBLEMA(S)'}")
sys.exit(1 if FALHAS else 0)
