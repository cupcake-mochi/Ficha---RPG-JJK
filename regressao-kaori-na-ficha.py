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

shutil.rmtree(d, ignore_errors=True)
print(f"\n{'A FICHA REPRODUZ A KAORI' if not falhas else f'{falhas} NÚMERO(S) ERRADO(S)'}")
sys.exit(1 if falhas else 0)
