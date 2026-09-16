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
for r in range(5, 200):
    k, v = dd.cell(row=r, column=53).value, dd.cell(row=r, column=54).value
    if k and v:
        IDX[k] = v
if not IDX:
    print("a ficha nao publicou o indice de celulas; regere com monta.py"); sys.exit(1)

for nome, v in KAORI.items():
    ws[IDX["atr_" + nome]] = v
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
                _c.value = _c.value.replace("IFS(", "_xlfn.IFS(")
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
    wsc[IDX["atr_Destreza"]] = des
    wsc[IDX["equipamento"]] = eq or None
    wsc[IDX["refino escolhido"]] = esc
    wbc.move_sheet("FICHA", -wbc.sheetnames.index("FICHA"))
    for _ws in wbc:
        for _l in _ws.iter_rows():
            for _c in _l:
                if isinstance(_c.value, str) and _c.value.startswith("=") and "IFS(" in _c.value \
                        and "_xlfn.IFS(" not in _c.value:
                    _c.value = _c.value.replace("IFS(", "_xlfn.IFS(")
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
    ok = lido == str(esp) and txt.endswith(f"{refino}/{_TETO_REF}")
    falhas += not ok
    print(f"  {rot:42} {lido + ' · ' + txt.split(': ')[-1]:>16} {str(esp) + ' · ' + str(refino):>10}   "
          f"{'BATE' if ok else 'NÃO BATE'}")
shutil.rmtree(d2, ignore_errors=True)
if _regra(2, int(_mex1.group(1)), f"Traje {_mex1.group(2)}", 0)[0] != int(_mex1.group(3)):
    print("  a regra montada aqui não reproduz o exemplo do livro: o teste mediria contra si mesmo")
    falhas += 1

print(f"\n{'A FICHA REPRODUZ A KAORI E A DEFESA DO LIVRO' if not falhas else f'{falhas} NÚMERO(S) ERRADO(S)'}")
sys.exit(1 if falhas else 0)
