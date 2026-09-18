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
    n = sum(1 for c in range(1, 60) if L(c) in wb[aba].column_dimensions)
    px = n * _px_col(larg)
    if aba in _INV:
        print(f"  [--] {aba}: {n} colunas ≈ {px:.0f} px — aba da invocação, fica com o conferir-invocacao.py")
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
checa("o carimbo de versão está na DADOS",
      str(ws["B1"].value) == CAT["_meta"]["versao"], str(ws["B1"].value))

f = wb["FICHA"]
formulas = [c.value for l in f.iter_rows() for c in l
            if isinstance(c.value, str) and c.value.startswith("=")]
checa("a FICHA tem fórmula, e não número digitado", len(formulas) >= 20, str(len(formulas)))
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
_faixa = _menu_eq[0].formula1 if _menu_eq else ""
_mf = re.search(r"DADOS!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)", _faixa)
_lida = []
if _mf:
    from openpyxl.utils import column_index_from_string as _ci
    for _r in range(int(_mf.group(2)), int(_mf.group(4)) + 1):
        _c0 = _ci(_mf.group(1))
        _vals = [dd.cell(row=_r, column=_c0 + k).value for k in range(4)]
        _lida.append((_vals[0], _vals[1], None if _vals[2] == "—" else _vals[2], _vals[3]))
checa("o menu do EQUIPAMENTO aponta para uma coluna da DADOS", bool(_mf and _mf.group(1) == _mf.group(3)), _faixa)
checa("a tabela do menu é a do catálogo: uniforme, escudo e cada par, com o menor teto",
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
checa("o Refino Atual impresso soma o refino escolhido",
      len(_fa) == 1 and _alcanca(_fa[0], _camp.replace("$", "")), str(_fa)[:90])

print("\nA FICHA AUTOMÁTICA  (17/09/2026)")
# O número mora na regressao-kaori-na-ficha.py, que recalcula doze casos no LibreOffice contra um modelo
# de força bruta. Aqui fica o que a regressão não vê: o índice anda sozinho, e o Codigo.gs sabe das
# caixas novas.
_bb = [dd.cell(row=rr, column=54).value for rr in range(5, 200) if dd.cell(row=rr, column=53).value]
checa("todo endereço do índice é fórmula ADDRESS, e anda quando a planilha muda de forma",
      bool(_bb) and all(isinstance(v, str) and v.startswith("=ADDRESS(ROW(FICHA!") for v in _bb),
      str([v for v in _bb if not (isinstance(v, str) and v.startswith("=ADDRESS("))][:3]))
_NOVAS = ["pontos disponíveis", "pontos de corpo", "marcos escolhidos", "perícias disponíveis",
          "ofícios disponíveis", "testes disponíveis", "aptidões disponíveis", "passivas do leque"]
checa("as oito caixas de conta estão no índice", all(k in IDX for k in _NOVAS), str([k for k in _NOVAS if k not in IDX]))
_CODA = open("apps-script/Codigo.gs", encoding="utf-8").read()
_avisos = re.search(r"var avisos = \[(.*?)\]", _CODA, re.S)
checa("o Codigo.gs avisa em vermelho e anota as oito caixas de conta",
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
                "feitiços disponíveis", "passivas", "escolhas de perícia", "trilha"] + \
               ["buff de " + k for k in ["defesa", "iniciativa", "cd de feitiço", "conjuração", "corpo a corpo",
                                         "à distância", "deslocamento"]]
checa("a Defesa, as caixas de Buff/Debuff, os ataques, os Feitiços e as Passivas têm nota (17/09/2026)",
      all(k in _chaves for k in _NOTA_PEDIDA), str([k for k in _NOTA_PEDIDA if k not in _chaves]))
checa("a nota mora no título quando o de cima é texto (tituloOuCaixa_ no alvoDaNota_)",
      bool(_mnotas) and "alvoDaNota_(ficha, c)" in _mnotas.group(1) and "function tituloOuCaixa_(" in _CODA)
_marcos_rot = [f.cell(row=f[IDX[k]].row - 1, column=f[IDX[k]].column).value
               for k in ("refino escolhido", "marco corpo", "marco leque") if k in IDX]
checa("o Marco Escolhido tem os rótulos Refino, Corpo e Leque, e as notas falam deles",
      _marcos_rot == ["Refino", "Corpo", "Leque"] and "Refino, Corpo ou Leque" in _CODA
      and "Atributo (Corpo)" not in _CODA, str(_marcos_rot))
# as aptidões de graça: os nomes saem do manual pelo ficha_automatica.regras(), e o texto das notas tem
# de trazer os números que o manual dá
import ficha_automatica as _fa_mod
_RG = _fa_mod.regras(CAT)
_mgr = re.search(r"var NOTAS_DE_GRACA = \{(.*?)\n\};", _CODA, re.S)
_gr = dict(re.findall(r"^  '([^']+)':\s*((?:'[^']*'\s*\+?\s*)+)", _mgr.group(1), re.M)) if _mgr else {}
_gr = {k: "".join(re.findall(r"'([^']*)'", v)) for k, v in _gr.items()}
checa("as notas de graça cobrem as duas aptidões e as duas Bênçãos que o manual dá",
      sorted(_gr) == sorted(_RG["aptidoes_de_graca"] + _RG["bencaos_de_graca"]), f"{sorted(_gr)}")
_MANG = re.sub(r"\s+([,.:;])", r"\1", " ".join(open("manual.txt", encoding="utf-8").read().split()))
_numeros = {_RG["aptidoes_de_graca"][0]: ["1/3 do refino + 1", "1,5 × refino", "por 2 PE"],
            _RG["aptidoes_de_graca"][1]: ["2d4 no 3", "3d4 no 6", "4d6"],
            _RG["bencaos_de_graca"][0]: ["1/3 da Lapidação + 1", "1,5 × Lapidação", "por 2 PE"],
            _RG["bencaos_de_graca"][1]: ["1× por cena", "2d4 na 3", "3d4 na 6", "4d6"]}
_fora = [(k, x) for k, xs in _numeros.items() for x in xs if x not in _MANG or x not in _gr.get(k, "")]
checa("as notas de graça trazem os números do manual", not _fora, str(_fora[:3]))
_aps = [f[IDX[k]].value for k in ("aptidão de graça 1", "aptidão de graça 2") if k in IDX]
checa("as duas primeiras linhas de aptidão vêm com as de graça, trocando pelas Bênçãos sem energia",
      len(_aps) == 2 and all(isinstance(v, str) and a in v and b in v for v, a, b in
                             zip(_aps, _RG["bencaos_de_graca"], _RG["aptidoes_de_graca"])), str(_aps)[:120])
_oned = re.search(r"function onEdit\(e\)\s*\{(.*?)\n\}", _CODA, re.S)
checa("o onEdit devolve a Trilha de outro Caminho para o texto de escolha e refaz as notas de graça",
      bool(_oned) and "trilhaDoCaminho_(e, idx)" in _oned.group(1) and "notasDeGraca_(" in _oned.group(1))
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
      bool(re.search(r"function onEdit\(e\)\s*\{[^}]*marcarPericiasDoCaminho_\(e, idx\)", _CODA)))
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
      bool(_sis) and _mnome == ["F1"] and "DADOS!$F$1" in str(f["D2"].value) and "ERA DA REVOLUÇÃO" not in _cv.values(),
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
_margem = {a: wb[a].max_column for a in ("FICHA", "CARTEIRA", "INVOCAÇÃO", "CATÁLOGO")}
checa("a CARTEIRA, a INVOCAÇÃO e o CATÁLOGO acabam na mesma coluna da FICHA, com a margem da direita",
      len(set(_margem.values())) == 1, str(_margem))

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
checa("as notas do equipamento, da proteção e do refino escolhido dizem a regra do menu",
      "Escolha" in _txt(_nq) and "capítulo 12" not in _txt(_nq) and "digite" not in _txt(_nq)
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
    checa("ele traz as seis abas", all(f'"{a}"' in g for a in DEC["C6_documento"]["abas"]))
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
    _i_ultima = max(_corpo.find(k) for k in ("menusSuspensos_(", "corDeEstado_(", "protegerFormulas_("))
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
    dados = _js.loads(_re.search(r"var ABAS = (\[.*?\]);\n", g, _re.S).group(1))
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
    _mart = _re.search(r"var ARTE = (\{.*?\});\n", g, _re.S)
    _arte = _js.loads(_mart.group(1)) if _mart else {}
    _por = {a["nome"]: a for a in dados}
    _img_ruim, _n_img = [], 0
    for la in _lay["abas"]:
        sp = _por.get(la["nome"])
        for i in la["imagens"]:
            _n_img += 1
            cand = [im for im in (sp["imgs"] if sp else []) if str(im[4]).startswith(i["arquivo"][:-4] + "-")]
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
    _mm = _re.search(r"function montarAba_\(ss, spec\) \{(.*?)\n\}\n", g, _re.S)
    _cc = _mc.group(1) if _mc else ""
    _laco = _cc.find("montarAba_(")
    _fim_laco = _cc.find("});", _laco) if _laco >= 0 else -1
    _grava = _cc.find("escreverFormulas_(")
    _fn = g.find("function escreverFormulas_(")
    checa(f"{_cedo} fórmula(s) citam uma aba que nasce depois da delas, então a ordem da gravação importa",
          _cedo > 0)
    checa("as fórmulas são gravadas depois que todas as abas nascem, e não dentro do montarAba_",
          bool(_mm) and ".setFormula(" not in _mm.group(1) and 0 <= _laco < _fim_laco < _grava
          and _fn >= 0 and ".setFormula(" in g[_fn:_fn + 400],
          f"laço {_laco} · fim do laço {_fim_laco} · gravação {_grava}")

    arte_usada = {im[4] for a in dados for im in a["imgs"]}
    embutida = set(_re.findall(r'"([^"]+\.png)":"', g.split("var ARTE")[1][:200000]))
    checa("toda imagem usada está embutida no script", arte_usada <= embutida,
          str(sorted(arte_usada - embutida)))
    fontes_gs = {e[0] for a in dados for e in a["estilos"]}
    checa("o script só usa fonte conferida no seletor", fontes_gs <= CONF,
          str(sorted(fontes_gs - CONF)))

print(f"\n{'A FICHA CONFERE' if not FALHAS else f'{len(FALHAS)} PROBLEMA(S)'}")
sys.exit(1 if FALHAS else 0)
