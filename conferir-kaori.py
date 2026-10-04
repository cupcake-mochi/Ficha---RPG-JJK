# -*- coding: utf-8 -*-
"""Regressao completa: o catalogo reproduz TODOS os numeros impressos da Kaori? Le os dois lados.

04/10/2026: o livro reconstruido imprime o quadro da Kaori em Criar um personagem (Descendente, Bastiao da Trilha
Muro, nivel 2). Ele passa a ser a primeira referencia: os numeros que o quadro traz saem de la, e os que ele nao traz
(Integridade, maestria, corpo a corpo e a distancia) continuam vindo da .docx. As pericias fixas do Bastiao mudaram no
livro (Atletismo e Provocar), e a .docx, que e de 07/09, marca Intimidacao: a checagem delas passou a ler o quadro do
livro, que treina Atletismo, e a frase do Caminho.

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
# e o quadro do livro, que vence a .docx onde os dois trazem o campo
sys.path.insert(0, ".")
import livro as Lv
_q = dict(f for f in Lv.tabela(Lv.secao("Kaori"), "Campo")[1] if len(f) == 2)
_ve = re.match(r"(\d+) PV e (\d+) PE\.", _q.get("Vida e energia", ""))
_df = re.match(r"(\d+):", _q.get("Defesa", ""))
if not (_ve and _df):
    raise SystemExit(f"o quadro da Kaori no manual.txt mudou de forma: {_q}")
LIVRO = {"Vida": _ve.group(1), "Energia": _ve.group(2), "Defesa": _df.group(1), "Deslocamento": _q["Deslocamento"].rstrip("."),
         "Iniciativa": _q["Iniciativa"].rstrip("."), "Conjuração": _q["Ataque de sua técnica"].rstrip("."),
         "CD de feitiço": _q["CD de sua técnica"].rstrip(".")}
IMPRESSO.update(LIVRO)
_atr = dict((n, int(v)) for n, v in re.findall(r"(\w+) (\d)", _q["Atributos"]))
if _atr != KAORI:
    raise SystemExit(f"os atributos da Kaori no livro ({_atr}) nao sao os deste script ({KAORI})")

print(f"{'campo':16} {'catalogo':>12}   {'livro/.docx':>12}")
falhas = 0
for campo, meu in CALC.items():
    dela = IMPRESSO.get(campo, "<nao achei>")
    ok = meu.replace(" ", "") == dela.replace(" ", "")
    falhas += not ok
    print(f"  {campo:16} {meu:>12}   {dela:>12}   {'BATE' if ok else 'NAO BATE'}")

# pericias: o quadro do livro treina Atletismo, uma das fixas do Bastiao, com d20 + Forca + maestria
_atl = _q.get("Atletismo treinado", "").rstrip(".")
ok = "Atletismo" in C["pericias_fixas"] and _atl == f"d20 + {forca + maestria}"
falhas += not ok
print(f"\n  [{'BATE' if ok else 'NAO BATE'}] Atletismo treinado, fixa do {CAMINHO}: livro {_atl!r}, catalogo d20 + {forca + maestria}")
_fx = re.search(r"Perícias treinadas \| (\w+) e (\w+), mais cinco à sua escolha\.", " ".join(Lv.texto().split()))
ok = bool(_fx) and list(_fx.groups()) == C["pericias_fixas"]
falhas += not ok
print(f"  [{'BATE' if ok else 'NAO BATE'}] fixas do {CAMINHO} no catalogo {C['pericias_fixas']}, no livro {list(_fx.groups()) if _fx else None}")

# as Familias que a Kaori marcou existem no manual?
_fam = re.search(r"Suas Famílias Livres são (\w+) e (\w+)\. (\w+), (\w+) e (\w+) estão Fechadas\.", " ".join(Lv.texto().split()))
if not _fam:
    raise SystemExit("a frase das Familias da Kaori no manual.txt mudou de forma")
livres, fechadas = list(_fam.groups()[:2]), list(_fam.groups()[2:])
fantasma = [f for f in livres + fechadas if f not in CAT["familias"]]
falhas += bool(fantasma)
print(f"\n  Familias da Kaori: Livres {livres}, Fechadas {fechadas}")
print(f"  [{'OK' if not fantasma else 'PROBLEMA'}] todas existem no manual"
      f"{'' if not fantasma else ': ' + str(fantasma)}")
print(f"\n{'TODOS OS NUMEROS BATEM' if not falhas else f'{falhas} FALHA(S)'}")
# ate a v0.240 do sistema ele imprimia NAO BATE e saia com 0, e o rodar-tudo.sh le a saida
sys.exit(1 if falhas else 0)
