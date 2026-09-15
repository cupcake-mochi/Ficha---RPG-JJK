# -*- coding: utf-8 -*-
"""Regressao completa: o catalogo reproduz TODOS os numeros impressos na
ficha-exemplo-kaori.docx? Le os dois lados.

v0.240 do sistema: a .docx vendorizada era a de 07/09, com a CD `10 + 2 + maestria` e a
Integridade `20 + 8 x (nivel - 1)`, e as contas daqui eram as mesmas -- um confirmava o outro.
A .docx voltou a ser copia da que o gerador da ficha publica, a maestria e a Integridade saem
das formulas do catalogo, e as outras contas sao as do capitulo 1 do manual."""
import json, re, sys
from docx import Document
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
DOC = Document('repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx')

KAORI = {"Força":3, "Constituição":2, "Destreza":2, "Inteligência":1, "Essência":1}
# a técnica da Kaori usa Força: "Ataque de conjuração d20 + 3 + 1", na tabela Números da Kaori
CAMINHO, NIVEL, PROTECAO, TECNICA = "Bastião", 2, 1, "Força"

C = CAT["caminhos"][CAMINHO]
F = CAT["progressao"]["formulas"]
con, des, forca = KAORI["Constituição"], KAORI["Destreza"], KAORI["Força"]
tec, ess = KAORI[TECNICA], KAORI["Essência"]
_mm = re.search(r"1 \+ quantos de \(([\d,\s]+)\) <= nivel", F["maestria"])
_integ = F["integridade"].split("#")[0].replace("Essência", str(ess)).replace("nivel", str(NIVEL))
if not _mm or not re.fullmatch(r"[\d\s+\-*()]+", _integ):
    raise SystemExit("a formula da maestria ou da Integridade no catalogo mudou de forma: "
                     f"{F['maestria']!r} · {F['integridade']!r}")
maestria = 1 + sum(1 for a in _mm.group(1).split(",") if int(a) <= NIVEL)
CALC = {
    "Vida":          str((C["vida_inicial"] + con) + (C["vida_por_nivel"] + con) * (NIVEL - 1)),
    "Energia":       str(C["pe_por_nivel"] * NIVEL),
    "Integridade":   str(eval(_integ)),
    "Defesa":        str(10 + des + PROTECAO),
    "Iniciativa":    f"d20 + {des}",
    "Deslocamento":  "9 m",
    "Maestria":      str(maestria),
    "CD de feitiço": str(8 + tec + maestria),
    "Conjuração":    f"d20 + {tec + maestria}",
    "Corpo a corpo": f"d20 + {forca + maestria}",
    "À distância":   f"d20 + {des + maestria}",
}
# le a tabela de numeros derivados da ficha
IMPRESSO = {}
for t in DOC.tables:
    for r in t.rows:
        cel = [c.text.strip() for c in r.cells]
        for i in (0, 3):
            if len(cel) > i + 2 and cel[i] in CALC:
                IMPRESSO[cel[i]] = cel[i + 2]

print(f"{'campo':16} {'catalogo':>12}   {'ficha .docx':>12}")
falhas = 0
for campo, meu in CALC.items():
    dela = IMPRESSO.get(campo, "<nao achei>")
    ok = meu.replace(" ", "") == dela.replace(" ", "")
    falhas += not ok
    print(f"  {campo:16} {meu:>12}   {dela:>12}   {'BATE' if ok else 'NAO BATE'}")

# pericias treinadas: as duas fixas do Caminho aparecem marcadas?
marcadas = re.findall(r'■\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõç ]+)',
                      '\n'.join(c.text for t in DOC.tables for r in t.rows for c in r.cells))
marcadas = [m.strip() for m in marcadas]
print(f"\n  pericias treinadas na ficha: {len(marcadas)}  ({', '.join(marcadas)})")
for fixa in C["pericias_fixas"]:
    achou = any(fixa in m for m in marcadas)
    falhas += not achou
    print(f"  [{'BATE' if achou else 'NAO BATE'}] fixa do {CAMINHO}: {fixa}")

# as Familias que a Kaori marcou existem no manual?
livres = ["Controle", "Castigo"]; fechadas = ["Área", "Auxiliares", "Amparo"]
fantasma = [f for f in livres + fechadas if f not in CAT["familias"]]
falhas += bool(fantasma)
print(f"\n  Familias da Kaori: Livres {livres}, Fechadas {fechadas}")
print(f"  [{'OK' if not fantasma else 'PROBLEMA'}] todas existem no manual"
      f"{'' if not fantasma else ': ' + str(fantasma)}")
print(f"\n{'TODOS OS NUMEROS BATEM' if not falhas else f'{falhas} FALHA(S)'}")
# ate a v0.240 do sistema ele imprimia NAO BATE e saia com 0, e o rodar-tudo.sh le a saida
sys.exit(1 if falhas else 0)
