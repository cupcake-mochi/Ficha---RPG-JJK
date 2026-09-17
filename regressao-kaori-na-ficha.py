# -*- coding: utf-8 -*-
"""Regressao ponta a ponta: preenche a Kaori na ficha GERADA, manda o
LibreOffice recalcular, e compara com a ficha-exemplo-kaori.docx.

Isso e diferente do conferir-kaori.py, que confere o CATALOGO. Aqui quem esta
sendo julgada e a planilha: as formulas dela, as referencias de celula dela.
Foi assim que apareceu o bug de a Vida somar Destreza no lugar de Constituicao.
"""
import json, os, shutil, subprocess, sys, tempfile, csv
from openpyxl import load_workbook

ARQ = "ficha-v01/ficha-projeto-m-0.1.xlsx"
if not os.path.exists(ARQ):
    print("gere a ficha antes:  python3 ficha-v01/monta.py"); sys.exit(1)

KAORI = {"Força": 3, "Constituição": 2, "Destreza": 2, "Inteligência": 1, "Essência": 1}
CAMINHO, NIVEL = "Bastião", 2
# a chave e o nome no INDICE que a propria ficha publica na DADOS
# Os números saem da tabela `Números da Kaori` do livro do Projeto M, capítulo `Criação de
# Personagem`, na v0.237. Até 14/09/2026 aqui estavam 28 e 13, da ficha-exemplo antiga:
# Integridade `20 + 8 × (nível − 1)` e CD `10 + 2 + maestria`, duas fórmulas que o sistema
# aposentou (v0.145 e v0.117). O gerador velho estava nelas também, e por isso isto passava.
ESPERADO = {"vida_max": 23, "energia_max": 8, "integridade_max": 26, "defesa": 13,
            "maestria": 1, "cd de feitiço": 12}

d = tempfile.mkdtemp(prefix="kaori-")
copia = os.path.join(d, "kaori.xlsx")
shutil.copy(ARQ, copia)
wb = load_workbook(copia)
ws = wb["FICHA"]

# acha as celulas pelo rotulo impresso, e nao por coordenada decorada
def col_do_atributo():
    m = {}
    for linha in ws.iter_rows():
        for c in linha:
            if isinstance(c.value, str) and c.value in KAORI:
                m[c.value] = (c.column, c.row - 4)      # o numero fica 4 linhas acima
    return m

def acha_rotulo(txt):
    for linha in ws.iter_rows():
        for c in linha:
            if isinstance(c.value, str) and c.value.upper() == txt.upper():
                return c.column, c.row
    return None, None

# o indice que a ficha publica: nada de coordenada decorada aqui
IDX = {}
dd = wb["DADOS"]
# desde 17/09/2026 a célula do índice é fórmula (ADDRESS), e o indice_ficha.py lê as duas formas
sys.path.insert(0, "ficha-v01")
from indice_ficha import endereco as _endereco
for r in range(5, 200):
    k, v = dd.cell(row=r, column=53).value, _endereco(dd.cell(row=r, column=54).value)
    if k and v:
        IDX[k] = v
if not IDX:
    print("a ficha nao publicou o indice de celulas; regere com monta.py"); sys.exit(1)

# desde 17/09/2026 o número grande é fórmula: o jogador digita na caixa pequena
for nome, v in KAORI.items():
    ws[IDX.get("atr_base_" + nome, IDX["atr_" + nome])] = v
ws[IDX["caminho"]] = CAMINHO
ws[IDX["nivel"]]   = NIVEL
# o atributo da técnica: a Kaori declara Força, e o livro soma 3 no ataque de conjuração.
# A célula sai da própria fórmula da CD, e não de coordenada decorada.
import re as _re
_mt = _re.search(r'IFS\((\$?[A-Z]+\$?\d+)="FORÇA"', str(ws[IDX["cd de feitiço"]].value))
if not _mt:
    print("a CD de feitiço não lê o atributo da técnica por IFS: não sei onde escolher"); sys.exit(1)
ws[_mt.group(1).replace("$", "")] = "FORÇA"
# Os Testes de Resistência, o B14: a ficha soma a maestria no treinado e só o atributo nos outros.
# Os dois que a Kaori treina saem do exemplo do livro, a regra sai do capítulo 1, os nomes e os
# atributos saem do catálogo, e a maestria sai da própria ficha recalculada, conferida acima.
CAT = json.load(open("catalogo-projeto-m.json", encoding="utf-8"))
_MAN = " ".join(open("manual.txt", encoding="utf-8").read().split())
_ex = _MAN[_MAN.find("A Kaori, feiticeira de nível 2."):_MAN.find("CD dos feitiços dela")]
_mo = _re.search(r"Teste de Resistência: (\w+)", _ex)
_mc = _re.search(r"Teste de Resistência do Caminho: (\w+)", _ex)
_mr = _re.search(r"Teste de Resistência = d20 \+ atributo do TR \+ (\w+), e a (\w+) só entra "
                 r"se você for treinado nele", _MAN)
if not (_mo and _mc and _mr) or _mr.group(1) != _mr.group(2) or _mr.group(1) not in IDX:
    print("não achei no manual.txt os TRs da Kaori, ou a regra do TR com um termo que a ficha "
          "publica no índice"); sys.exit(1)
TREINADOS = {_mo.group(1), _mc.group(1)}
_TRC = CAT["testes_de_resistencia"]
TRS = {}
for _l in ws.iter_rows():
    for _c in _l:
        _n = _c.value.strip() if isinstance(_c.value, str) else None
        if _n not in _TRC or not isinstance(_TRC[_n], dict) or _n in TRS:
            continue
        for _d in ws[_c.row]:
            _v = _d.value
            _mb = (_re.search(r"IF\((\$?[A-Z]+\$?\d+)=TRUE,", _v)
                   if _d.column > _c.column and isinstance(_v, str) and _v.startswith("=") else None)
            if _mb:
                TRS[_n] = (_d.coordinate, _mb.group(1).replace("$", ""),
                           _re.search(r'IFS\((\$?[A-Z]+\$?\d+)="', _v))
                break
if set(TRS) != {t for t, v in _TRC.items() if isinstance(v, dict)}:
    print(f"não achei a fórmula de treino de todos os TRs na FICHA: {sorted(TRS)}"); sys.exit(1)
for _n, (_tot, _cx, _ma) in TRS.items():
    ws[_cx] = _n in TREINADOS
    # o Físico escolhe o atributo na criação, e o livro não diz qual a Kaori travou: a cópia usa o
    # primeiro que o catálogo lista, e o número esperado sai do mesmo atributo
    if _ma:
        ws[_ma.group(1).replace("$", "")] = _TRC[_n]["atributo"][0].upper()
# o LibreOffice exporta em csv SO a primeira aba, e a primeira agora e a
# CARTEIRA. Na copia, a FICHA vai para a frente -- o arquivo real nao muda.
wb.move_sheet("FICHA", -wb.sheetnames.index("FICHA"))
# O IFS fica cru na ficha, porque ela vive no Sheets. O LibreOffice só reconhece o IFS
# com o prefixo do Excel, então a CÓPIA ganha o prefixo; o arquivo real não muda.
for _ws in wb:
    for _l in _ws.iter_rows():
        for _c in _l:
            if isinstance(_c.value, str) and _c.value.startswith("=") and "IFS(" in _c.value \
                    and "_xlfn.IFS(" not in _c.value:
                _c.value = _re.sub(r"(?<![A-Z_.])IFS\(", "_xlfn.IFS(", _c.value)
wb.save(copia)

subprocess.run(["libreoffice", "--headless", "--convert-to",
                "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,true,true",
                "--outdir", d, copia],
               capture_output=True, timeout=240)
csvf = os.path.join(d, "kaori.csv")
if not os.path.exists(csvf):
    print("o LibreOffice nao converteu; sem ele esta checagem NAO roda")
    sys.exit(1)

linhas = list(csv.reader(open(csvf, encoding="utf-8")))
def le(coord):
    """le o valor recalculado da celula, pelo endereco que o indice deu"""
    col = "".join(ch for ch in coord if ch.isalpha())
    lin = int("".join(ch for ch in coord if ch.isdigit()))
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    if lin - 1 < len(linhas) and n - 1 < len(linhas[lin - 1]):
        return linhas[lin - 1][n - 1].strip()
    return "<fora do csv>"

print(f"Kaori · {CAMINHO} nível {NIVEL} · " +
      " ".join(f"{k[:3]}{v}" for k, v in KAORI.items()))
# os rotulos saem para variaveis porque aspas iguais dentro de uma f-string
# so compilam no Python 3.12 em diante, e o rodar-tudo.sh nao vai exigir isso
_c, _f, _m = "campo", "a ficha calcula", "manual p.41"
print(f"\n{_c:16} {_f:>16} {_m:>13}")
falhas = 0
for campo, esp in ESPERADO.items():
    lido = le(IDX[campo])
    ok = lido.replace(".0", "") == str(esp)
    falhas += not ok
    print(f"  {campo:16} {lido:>16} {esp:>13}   {'BATE' if ok else 'NÃO BATE'}")

_mae = le(IDX[_mr.group(1)]).replace(".0", "")
_t1, _t2 = "TR · treino", "atributo + treino"
print(f"\n{_t1:26} {_f:>6} {_t2:>18}")
for _n, (_tot, _cx, _ma) in TRS.items():
    _atr = KAORI[_TRC[_n]["atributo"][0]]
    esp = _atr + (int(_mae) if _n in TREINADOS else 0) if _mae.isdigit() else None
    lido = le(_tot)
    ok = esp is not None and lido.replace(".0", "") == str(esp)
    falhas += not ok
    _rot = _n + (" · treinado" if _n in TREINADOS else " · sem treino")
    print(f"  {_rot:24} {lido:>6} {str(esp):>18}   {'BATE' if ok else 'NÃO BATE'}")

shutil.rmtree(d, ignore_errors=True)

# ============================================================================================
# A DEFESA COM UNIFORME, ESCUDO E REFINO ESCOLHIDO — o B3, na v0.246 do sistema
# Cada caso vira uma copia da ficha gerada, e o LibreOffice recalcula todas numa passada. O numero
# esperado sai da regra do livro, montada aqui com os valores do catalogo -- que o conferir-catalogo
# confere contra as tabelas do manual -- e com as frases do manual.txt. Dois casos sao os exemplos
# que o proprio livro publica.
_EQ = CAT["equipamento_defesa"]
_MARCOS = CAT["progressao"]["marcos"]
_mteto = _re.search(r"o refino é um número de 1 a (\d+)\.", _MAN)
_mex1 = _re.search(r"com Destreza (\d+) e um Traje de degrau (\d+), a sua Defesa é (\d+)", _MAN)
_mex2 = _re.search(r"Com refino (\d+) a sua proteção passiva é (\d+)", _MAN)
if not (_mteto and _mex1 and _mex2 and "1/3 do refino + 1" in _MAN):
    print("não achei no manual.txt o teto do refino, os dois exemplos de Defesa ou a fórmula do "
          "cobrir-se"); sys.exit(1)
_TETO_REF = int(_mteto.group(1))

def _regra(nivel, des, equip, esc):
    """a Defesa pelo livro: refino de graça + escolhas (uma por marco que passou, até o teto), o
    cobrir-se desligado por uniforme, o escudo por cima, e o menor teto de Destreza"""
    m = sum(1 for x in _MARCOS if x <= nivel)
    refino = min(_TETO_REF, 1 + m + min(m, esc))
    partes = [p.strip() for p in equip.split("+")] if equip else []
    uni = [_EQ["uniformes"][p] for p in partes if p in _EQ["uniformes"]]
    escu = [_EQ["escudos"][p] for p in partes if p in _EQ["escudos"]]
    prot = (0 if uni else refino // 3 + 1) + sum(x["protecao"] for x in uni + escu)
    tetos = [x["teto_de_destreza"] for x in uni + escu if x["teto_de_destreza"] is not None]
    return 10 + min([des] + tetos) + prot, refino

# o refino do exemplo, alcançado no primeiro nível em que dá para chegar nele escolhendo Refino
_m = lambda n: sum(1 for x in _MARCOS if x <= n)
_alvo = int(_mex2.group(1))
_ano = next(n for n in range(1, 31) if 1 + 2 * _m(n) >= _alvo)
_esc6 = _alvo - 1 - _m(_ano)
CASOS = [
    # (rotulo, nivel, Destreza, equipamento, refino escolhido)
    ("sem nada, nível 2", 2, 2, "", 0),
    ("o exemplo do livro: Destreza e Traje", 2, int(_mex1.group(1)), f"Traje {_mex1.group(2)}", 0),
    ("Revestimento corta a Destreza", 10, 6, "Revestimento 1", 0),
    ("Revestimento 2 + Torre", 6, 0, "Revestimento 2 + Torre", 0),
    ("escudo soma no cobrir-se, com Refino", 18, 6, "Broquel", 4),
    (f"o exemplo do livro: refino {_mex2.group(1)}", _ano, 4, "", _esc6),
    ("Traje 3 + Médio no fim, refino no teto", 30, 6, "Traje 3 + Médio", 7),
    ("escolha acima dos marcos não conta", 2, 3, "", 7),
    ("escolha vinda como texto", 22, 5, "Médio", "3"),
    ("Revestimento 3 + Broquel", 26, 2, "Revestimento 3 + Broquel", 0),
]
d2 = tempfile.mkdtemp(prefix="defesa-")
arqs = []
for i, (rot, nv, des, eq, esc) in enumerate(CASOS):
    wbc = load_workbook(ARQ)
    wsc = wbc["FICHA"]
    wsc[IDX["nivel"]] = nv
    wsc[IDX.get("atr_base_Destreza", IDX["atr_Destreza"])] = des
    wsc[IDX["equipamento"]] = eq or None
    wsc[IDX["refino escolhido"]] = esc
    wbc.move_sheet("FICHA", -wbc.sheetnames.index("FICHA"))
    for _ws in wbc:
        for _l in _ws.iter_rows():
            for _c in _l:
                if isinstance(_c.value, str) and _c.value.startswith("=") and "IFS(" in _c.value \
                        and "_xlfn.IFS(" not in _c.value:
                    _c.value = _re.sub(r"(?<![A-Z_.])IFS\(", "_xlfn.IFS(", _c.value)
    arqs.append(os.path.join(d2, f"caso{i:02d}.xlsx"))
    wbc.save(arqs[-1])
subprocess.run(["libreoffice", "--headless", "--convert-to",
                "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,true,true",
                "--outdir", d2] + arqs, capture_output=True, timeout=600)
_atual = None
for _l in load_workbook(ARQ)["FICHA"].iter_rows():
    for _c in _l:
        if isinstance(_c.value, str) and "Refino Atual" in _c.value:
            _atual = _c.coordinate
_t3, _t4 = "a ficha calcula", "o livro"
print(f"\n{'Defesa com equipamento':44} {_t3:>16} {_t4:>10}")
for i, (rot, nv, des, eq, esc) in enumerate(CASOS):
    esp, refino = _regra(nv, des, eq, int(esc))
    f2 = os.path.join(d2, f"caso{i:02d}.csv")
    if not os.path.exists(f2):
        print(f"  {rot:42} o LibreOffice nao converteu"); falhas += 1; continue
    linhas = list(csv.reader(open(f2, encoding="utf-8")))
    lido = le(IDX["defesa"]).replace(".0", "")
    txt = le(_atual) if _atual else ""
    # desde 17/09/2026 a caixa segue com as aptidões depois do refino: "Refino Atual: 9/10 - Aptidões ..."
    _mref = _re.search(r"Atual: (\d+)/(\d+)", txt)
    ok = lido == str(esp) and bool(_mref) and (_mref.group(1), _mref.group(2)) == (str(refino), str(_TETO_REF))
    falhas += not ok
    print(f"  {rot:42} {lido + ' · ' + (_mref.group(1) + '/' + _mref.group(2) if _mref else txt[:12]):>16} {str(esp) + ' · ' + str(refino):>10}   "
          f"{'BATE' if ok else 'NÃO BATE'}")
shutil.rmtree(d2, ignore_errors=True)
if _regra(2, int(_mex1.group(1)), f"Traje {_mex1.group(2)}", 0)[0] != int(_mex1.group(3)):
    print("  a regra montada aqui não reproduz o exemplo do livro: o teste mediria contra si mesmo")
    falhas += 1

# ============================================================================================
# A FICHA AUTOMÁTICA — o atributo que soma o Corpo, os X de Y, os marcos e as Passivas do Leque
# (17/09/2026). Cada caso preenche uma cópia, o LibreOffice recalcula, e o texto de cada caixa é
# comparado com um modelo feito AQUI por força bruta: a rota do ofício e a divisão dos marcos de Corpo
# são testadas uma a uma, e as aptidões são contadas marco a marco. Nenhuma fórmula da planilha é
# copiada para o modelo; as regras saem do manual.txt e do catálogo, pelo mesmo leitor da limpeza.
import copy as _copy
sys.path.insert(0, "ficha-v01")
import indice_ficha as _ix, defesa_equipamento as _de, ficha_automatica as _fa, ficha_layout as _fl
_LAY = json.load(open("ficha-v01/layout.json", encoding="utf-8"))
# a mesma ordem do monta.py: o desenho da mesa antes do índice
_fl.aplica(_LAY, _fl.trocas(_LAY)); _ix.aplica(_LAY, _ix.trocas(_LAY)); _de.aplica(_LAY, _de.trocas(_LAY))
_FA = _fa.trocas(_LAY)
_R = _fa.regras(CAT)
_CX, _TX = _FA["caixas"], _FA["textos"]
_ATR = [n for n, _, _ in _ix.ATRS]
_PER, _OFI = list(CAT["pericias"]), list(CAT["oficios"])
_ROTAS = [(_R["pericias_com"], _R["oficios_com"]), (_R["pericias_troca"], _R["oficios_troca"])]

def _cabe(p, o, k):
    return k >= 0 and any(max(0, p - bp) + max(0, o - bo) <= k for bp, bo in _ROTAS)

def _a_mais(p, o, s, c):
    """o menor número de marcações a tirar (perícia, ofício ou especialização) para caber"""
    for r in range(0, p + o + s + 1):
        for dp in range(0, min(p, r) + 1):
            for do in range(0, min(o, r - dp) + 1):
                ds = r - dp - do
                if ds <= s and _cabe(p - dp, o - do, c - (s - ds)):
                    return r
    return None

def _maximo(lista, p, o, k):
    """o maior total que a lista alcança numa rota e numa divisão do Corpo que caibam"""
    melhor = None
    for bp, bo in _ROTAS:
        for xo in range(0, max(k, 0) + 1):
            xp = k - xo
            if o <= bo + xo and p <= bp + xp:
                v = bp + xp if lista == "p" else bo + xo
                melhor = v if melhor is None else max(melhor, v)
    # a lista pode crescer além do que já está marcado: o maximo é o que cabe com as outras marcações fixas
    return melhor

def _rota(p, o, k):
    """a rota que a ficha mostra: a de 9 e 2 enquanto ela couber, e a de 10 e nenhum só quando só ela cabe
    (decisão do Mizuki, 17/09/2026: a ficha nasce mostrando 9 perícias e 2 ofícios)"""
    cabe = [max(0, p - bp) + max(0, o - bo) <= k for bp, bo in _ROTAS]
    return 0 if cabe[0] or not cabe[1] else 1

def _lista(itens):
    """'2 perícias, 1 ofício e 1 escolha de Corpo', sem os itens que são zero"""
    v = [f"{n} {um if n == 1 else varios}" for n, um, varios in itens if n > 0]
    return v[0] if len(v) == 1 else ", ".join(v[:-1]) + " e " + v[-1]

# o que o manual e o catálogo dão para as caixas de ataque, independente da planilha
_mcd8 = _re.search(r"CD de feitiço = (\d+) \+ o atributo da sua técnica \+ maestria", _MAN)
_mdesl = _re.search(r"O seu deslocamento base é (\d+) metros", _MAN)
_mmae = _re.search(r"1 \+ quantos de \(([\d,]+)\) <= nivel", CAT["progressao"]["formulas"]["maestria"])
if not (_mcd8 and _mdesl and _mmae):
    print("não achei no manual.txt a CD ou o deslocamento, ou no catálogo a maestria"); sys.exit(1)
_MAE = [int(x) for x in _mmae.group(1).split(",")]
_ORIGENS = _fa.origens_do_menu(CAT)
_ST = next(o_ for o_ in _ORIGENS if o_.endswith(_fa.SEM_TECNICA))

def _texto(usados, total):
    return f"{usados - total} a mais" if usados > total else f"{total - usados} de {total}"

def _modelo(c):
    m = sum(1 for x in _MARCOS if x <= c["nivel"])
    out = {}
    base, usados = _R["pontos_criacao"] + m, sum(c["bases"])
    grandes = [b + k for b, k in zip(c["bases"], c["corpo"])]
    for n, g in zip(_ATR, grandes):
        out["atr_" + n] = str(g)
    if usados > base:
        out["pontos disponíveis"] = f"{usados - base} a mais"
    elif max(grandes) > _R["teto_atributo"]:
        out["pontos disponíveis"] = f"Um atributo passou de {_R['teto_atributo']}"
    elif m == 0 and max(c["bases"]) > _R["teto_criacao"]:
        out["pontos disponíveis"] = f"Na criação, nenhum acima de {_R['teto_criacao']}"
    else:
        out["pontos disponíveis"] = f"{base - usados} de {base}"
    out["pontos de corpo"] = "Pontos de Marco de Corpo Disponíveis - " + _texto(sum(c["corpo"]), c["corpo_m"])
    tot = c["refino_m"] + c["corpo_m"] + c["leque_m"]
    out["marcos escolhidos"] = (f"{tot - m} a mais" if tot > m else
                                "Escolha 1 a cada 4 Nv" if m == 0 else f"{m - tot} de {m} para escolher")
    p, o, s = len(c["per"]), len(c["ofi"]), len(c["espec"])
    k, esp_ = c["corpo_m"] - s, _R["especializa"]
    am = _a_mais(p, o, s, c["corpo_m"])
    if s > 0 and c["nivel"] < esp_:
        out["perícias disponíveis"] = out["ofícios disponíveis"] = f"Especialização só no nível {esp_}"
        out["escolhas de perícia"] = f"Especialização só no nível {esp_}: tire a marcação"
    elif am:
        out["perícias disponíveis"] = out["ofícios disponíveis"] = f"{am} a mais"
        out["escolhas de perícia"] = f"Marcou {am} a mais: tire uma perícia, um ofício ou uma especialização"
    else:
        i_ = _rota(p, o, k)
        bp, bo = _ROTAS[i_]
        cp, co = max(0, p - bp), max(0, o - bo)
        out["perícias disponíveis"] = _texto(p, bp + cp)
        out["ofícios disponíveis"] = _texto(o, bo + co)
        u, fp, fo = k - cp - co, max(0, bp - p), max(0, bo - o)
        if fp + fo + u == 0:
            out["escolhas de perícia"] = "Tudo escolhido"
        else:
            txt = "Falta: " + _lista([(fp, "perícia", "perícias"), (fo, "ofício", "ofícios"),
                                      (u, "escolha de Corpo", "escolhas de Corpo")])
            if u > 0 and fp + fo == 0:
                txt += " (+1 perícia, +1 ofício" + (" ou uma especialização" if c["nivel"] >= esp_ else "") + ")"
            bp2, bo2 = _ROTAS[1]
            if i_ == 0 and o <= bo2:
                u2 = k - max(0, p - bp2) - max(0, o - bo2)
                txt += ", ou " + _lista([(max(0, bp2 - p), "perícia", "perícias"),
                                         (u2, "escolha de Corpo", "escolhas de Corpo")]) + " sem ofício"
            out["escolhas de perícia"] = txt
    out["testes disponíveis"] = _texto(len(c["tr"]), _R["testes"])
    # as aptidões, marco a marco, com as escolhas de Refino nos últimos marcos
    r = min(c["refino_m"], m)
    se, st = c["origem"] == _R["sem_energia"], c["origem"].endswith(_fa.SEM_TECNICA)
    tm = c["origem"] in _R["marcial"]
    refino, apt = 1, _R["aptidoes_gratis"] + (_R["semente"] if st else 0)
    for marco in range(1, m + 1):
        refino = min(_R["teto_refino"], refino + 1)
        if marco > m - r:
            if refino >= _R["teto_refino"]:
                apt += _R["aptidoes_no_teto"]
            else:
                refino += 1
                apt += 1
    out["aptidões"] = (("Lapidação Atual: " if se else "Refino Atual: ") + f"{refino}/{_R['teto_refino']} - " +
                       ("Bênçãos" if se else "Aptidões") + " Disponíveis: " + _texto(c["aptidoes"], apt))
    gracas = _R["bencaos_de_graca"] if se else _R["aptidoes_de_graca"]
    out["aptidão de graça 1"], out["aptidão de graça 2"] = gracas
    # as caixas de ataque, pelas fórmulas do capítulo 1, com o Buff/Debuff do lado
    g = dict(zip(_ATR, grandes))
    mae = 1 + sum(1 for x in _MAE if x <= c["nivel"])
    b = lambda k_: c["buff"].get(k_, 0)
    out["defesa"] = str(_regra(c["nivel"], g["Destreza"], "", c["refino_m"])[0] + b("defesa"))
    out["iniciativa"] = f"d20 + {g['Destreza'] + b('iniciativa')}"
    out["cd de feitiço"] = str(int(_mcd8.group(1)) + g[c["atr_conj"]] + mae + b("cd de feitiço"))
    out["conjuração"] = f"d20 + {g[c['atr_conj']] + mae + b('conjuração')}"
    out["corpo a corpo"] = f"d20 + {g['Força'] + mae + b('corpo a corpo')}"
    out["à distância"] = f"d20 + {g['Destreza'] + mae + b('à distância')}"
    out["deslocamento"] = f"{int(_mdesl.group(1)) + b('deslocamento')} m"
    out["passivas do leque"] = "Passivas do Leque - " + _texto(len(c["leque_nomes"]), c["leque_m"])
    espacos = 2 + c["nivel"] // 2 + m + c["leque_m"]
    out["espaços de feitiço"] = str(espacos)
    palavra_feit = "Katas" if tm else "Manejos" if st else "Feitiços"
    out["feitiços"] = f"{palavra_feit} - Disponível: {espacos - sum(1 for x in c['feiticos'] if x > 0) - sum(c['passivas'])}"
    return out

_BASE = dict(nivel=2, bases=[3, 2, 2, 1, 1], corpo=[0, 0, 0, 0, 0], refino_m=0, corpo_m=0, leque_m=0,
             per=_PER[:9], ofi=_OFI[:2], espec=[], tr=["Físico", "Vigor"], aptidoes=2, leque_nomes=[],
             feiticos=[1, 1, 1], passivas=[0], leque_classes=[], origem="Latente", atr_conj="Essência", buff={})
CASOS2 = [
    ("criação cheia, nove e dois", {}),
    ("criação trocando os ofícios", dict(per=_PER[:10], ofi=[])),
    ("dez perícias e um ofício, sem marco", dict(per=_PER[:10], ofi=_OFI[:1])),
    ("marco de Corpo virando ofício", dict(nivel=10, bases=[3, 3, 2, 2, 1], corpo=[1, 0, 0, 0, 0], corpo_m=1, refino_m=1,
                                           per=_PER[:9], ofi=_OFI[:3])),
    ("marco de Corpo virando especialização", dict(nivel=10, bases=[3, 3, 2, 2, 1], corpo=[0, 1, 0, 0, 0], corpo_m=1, leque_m=1,
                                                   espec=_PER[:1])),
    ("especialização antes do nível 10", dict(nivel=6, bases=[3, 3, 2, 1, 1], corpo=[1, 0, 0, 0, 0], corpo_m=1, espec=_PER[:1])),
    ("passou nas duas listas", dict(nivel=10, bases=[3, 3, 2, 2, 1], corpo=[0, 0, 1, 0, 0], corpo_m=1, refino_m=1,
                                    per=_PER[:11], ofi=_OFI[:2])),
    ("refino no teto, rota pura", dict(nivel=30, bases=[4, 4, 3, 2, 3], refino_m=7, aptidoes=12)),
    ("refino misturado no nível 30", dict(nivel=30, bases=[4, 4, 3, 2, 3], corpo=[1, 1, 0, 0, 0], refino_m=5, corpo_m=2, aptidoes=5)),
    # a Passiva do Leque tem Classe 3 e não custa espaço: se a conta de Feitiços cobrar a coluna dela, cai
    ("Leque e Passivas", dict(nivel=14, bases=[3, 3, 2, 2, 2], refino_m=1, leque_m=2, leque_nomes=["Eco"],
                              leque_classes=[3], feiticos=[1, 1, 2, 0], passivas=[2, 1])),
    ("pontos a mais e TR a mais", dict(bases=[3, 3, 2, 1, 1], tr=["Físico", "Vigor", "Espírito"], aptidoes=3)),
    ("atributo acima de 6", dict(nivel=30, bases=[6, 4, 3, 2, 1], corpo=[1, 0, 0, 0, 0], corpo_m=1, marcos_extra=0)),
    # 17/09/2026, a segunda rodada: a caixa das escolhas, as aptidões de graça, as duas Restrições e o Buff/Debuff
    ("ficha em branco", dict(bases=[0, 0, 0, 0, 0], per=[], ofi=[], tr=[], feiticos=[], atr_conj="Força")),
    ("nove perícias sem ofício", dict(ofi=[])),
    ("Corpo por escolher no nível 10", dict(nivel=10, bases=[3, 3, 2, 2, 1], corpo=[1, 0, 0, 0, 0], corpo_m=1, refino_m=1)),
    ("dez perícias e Corpo, sem ofício", dict(nivel=6, bases=[3, 3, 2, 1, 1], corpo=[1, 0, 0, 0, 0], corpo_m=1,
                                             per=_PER[:10], ofi=[])),
    ("faltando da criação e do Corpo", dict(nivel=6, bases=[3, 3, 2, 1, 1], corpo=[0, 0, 1, 0, 0], corpo_m=1,
                                           per=_PER[:5], ofi=[])),
    ("Restrição Celestial sem energia", dict(origem=_R["sem_energia"], nivel=10, bases=[3, 3, 2, 2, 1],
                                             corpo=[0, 1, 0, 0, 0], corpo_m=1, refino_m=1, aptidoes=3,
                                             per=_PER[:10], ofi=_OFI[:2])),
    ("Sem Técnica com a semente", dict(origem=_ST, aptidoes=3, atr_conj="Inteligência")),
    ("Buff/Debuff em todas as caixas", dict(buff={"defesa": 1, "iniciativa": 2, "cd de feitiço": -1, "conjuração": 1,
                                                  "corpo a corpo": 3, "à distância": -2, "deslocamento": 3})),
]
if not all(o_ in _ORIGENS for o_ in (_R["sem_energia"], _ST)):
    print("a origem sem energia ou a Sem Técnica não estão no menu de Origem"); sys.exit(1)
# a célula de cada atributo escolhido sai da própria fórmula, e não de coordenada decorada
_wb0 = load_workbook(ARQ)["FICHA"]
_SEL = {}
for _k in ("conjuração", "corpo a corpo", "à distância"):
    _ms = _re.search(r'IFS\((\$?[A-Z]+\$?\d+)="FORÇA"', str(_wb0[IDX[_k]].value))
    if not _ms:
        print(f"a caixa {_k} não lê o atributo por IFS: não sei onde escolher"); sys.exit(1)
    _SEL[_k] = _ms.group(1).replace("$", "")
_GRACA = [IDX["aptidão de graça 1"], IDX["aptidão de graça 2"]]
d3 = tempfile.mkdtemp(prefix="auto-")
arqs3 = []
for i, (rot, mud) in enumerate(CASOS2):
    c = dict(_BASE, **mud)
    wbc = load_workbook(ARQ)
    wsc = wbc["FICHA"]
    wsc[IDX["nivel"]] = c["nivel"]
    wsc[IDX["caminho"]] = CAMINHO
    wsc[IDX["origem"]] = c["origem"]
    wsc[_SEL["conjuração"]] = c["atr_conj"].upper()
    wsc[_SEL["corpo a corpo"]], wsc[_SEL["à distância"]] = "FORÇA", "DESTREZA"
    for k_, v_ in c["buff"].items():
        wsc[IDX["buff de " + k_]] = v_
    for n, b, k in zip(_ATR, c["bases"], c["corpo"]):
        wsc[IDX["atr_base_" + n]] = b
        wsc[IDX["corpo_" + n]] = k
    wsc[IDX["refino escolhido"]], wsc[IDX["marco corpo"]], wsc[IDX["marco leque"]] = c["refino_m"], c["corpo_m"], c["leque_m"]
    for lista, caixas, marcadas in ((_PER, _CX["pericias"], c["per"]), (_OFI, _CX["oficios"], c["ofi"]),
                                    (_PER, _CX["pericias_espec"], c["espec"])):
        for nome, cx in zip(lista, caixas):
            wsc[cx] = nome in marcadas
    for nome, cx in zip([t for t, v in _TRC.items() if isinstance(v, dict)], _CX["testes"]):
        wsc[cx] = nome in c["tr"]
    # as duas de graça já vêm na ficha, em fórmula: a cópia não mexe nelas, e anota as outras
    assert c["aptidoes"] >= len(_GRACA)
    for j, cx in enumerate([x for x in _CX["aptidoes"] if x not in _GRACA], len(_GRACA)):
        wsc[cx] = f"aptidão {j + 1}" if j < c["aptidoes"] else None
    for j, cx in enumerate(_CX["leque_nome"]):
        wsc[cx] = c["leque_nomes"][j] if j < len(c["leque_nomes"]) else None
    for j, cx in enumerate(_CX["leque_classe"]):
        wsc[cx] = c["leque_classes"][j] if j < len(c["leque_classes"]) else 0
    for j, cx in enumerate(_CX["passivas_classe"]):
        wsc[cx] = c["passivas"][j] if j < len(c["passivas"]) else 0
    for j, cx in enumerate(_CX["feitico_classe"]):
        wsc[cx] = c["feiticos"][j] if j < len(c["feiticos"]) else 0
    wbc.move_sheet("FICHA", -wbc.sheetnames.index("FICHA"))
    for _ws in wbc:
        for _l in _ws.iter_rows():
            for _c in _l:
                if isinstance(_c.value, str) and _c.value.startswith("=") and "IFS(" in _c.value \
                        and "_xlfn.IFS(" not in _c.value:
                    _c.value = _re.sub(r"(?<![A-Z_.])IFS\(", "_xlfn.IFS(", _c.value)
    arqs3.append(os.path.join(d3, f"auto{i:02d}.xlsx"))
    wbc.save(arqs3[-1])
subprocess.run(["libreoffice", "--headless", "--convert-to",
                "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,true,true",
                "--outdir", d3] + arqs3, capture_output=True, timeout=900)
_ONDE = dict({"atr_" + n: IDX["atr_" + n] for n in _ATR},
             **{k: IDX[k] for k in ("pontos disponíveis", "pontos de corpo", "marcos escolhidos", "perícias disponíveis",
                                    "ofícios disponíveis", "testes disponíveis", "espaços de feitiço", "escolhas de perícia",
                                    "aptidão de graça 1", "aptidão de graça 2", "defesa", "iniciativa", "cd de feitiço",
                                    "conjuração", "corpo a corpo", "à distância", "deslocamento")},
             **{"aptidões": _TX["aptidoes"], "passivas do leque": _TX["passivas_do_leque"], "feitiços": _TX["feiticos"]})
print(f"\n{'A ficha automática · caso':44} {'caixas que batem':>18}")
for i, (rot, mud) in enumerate(CASOS2):
    c = dict(_BASE, **mud)
    esp = _modelo(c)
    f3 = os.path.join(d3, f"auto{i:02d}.csv")
    if not os.path.exists(f3):
        print(f"  {rot:42} o LibreOffice nao converteu"); falhas += 1; continue
    linhas = list(csv.reader(open(f3, encoding="utf-8")))
    erradas = []
    for campo, alvo in _ONDE.items():
        lido = le(alvo)
        lido = lido.replace(".0", "") if campo in ("espaços de feitiço", "defesa", "cd de feitiço") or campo.startswith("atr_") else lido
        if campo == "feitiços":
            lido = lido.split(" - Conhecidos")[0]
        if lido != esp[campo]:
            erradas.append(f"{campo}: a ficha diz {lido!r}, o modelo diz {esp[campo]!r}")
    falhas += len(erradas)
    print(f"  {rot:42} {len(_ONDE) - len(erradas):>8} de {len(_ONDE)}   {'BATE' if not erradas else 'NÃO BATE'}")
    for e_ in erradas:
        print(f"      {e_}")
shutil.rmtree(d3, ignore_errors=True)

print(f"\n{'A FICHA REPRODUZ A KAORI, A DEFESA DO LIVRO E AS CONTAS AUTOMÁTICAS' if not falhas else f'{falhas} NÚMERO(S) ERRADO(S)'}")
sys.exit(1 if falhas else 0)
