# -*- coding: utf-8 -*-
"""Integridade referencial do catalogo: todo nome citado existe na tabela dona.
Nasceu de um bug real: a tabela de Familias tinha 'Area' e as Melhorias
apontavam para 'Area' com acento. Lição 9 do projeto, acontecendo dentro do
proprio arquivo que existe para evitar ela."""
import json, sys
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
falhas = []

def checa(nome, itens, campo, dono):
    orfas = sorted({v[campo] for v in itens.values() if v.get(campo) and v[campo] not in dono})
    print(f"  [{'OK' if not orfas else 'FALHA'}] {nome}")
    if orfas:
        falhas.append(f"{nome}: {orfas}")
        for o in orfas: print(f"          '{o}' nao existe na tabela dona")

print("INTEGRIDADE REFERENCIAL")
checa("toda Melhoria aponta para uma Familia que existe", CAT["melhorias"], "familia", CAT["familias"])
checa("toda Forma aponta para uma Familia que existe",    CAT["formas"],    "familia", CAT["familias"])
checa("toda pericia aponta para um atributo que existe",  CAT["pericias"],  "atributo",
      {a.replace("Forca","Forca") for a in CAT["atributos"]["lista"]})

print("\nCONTAGENS DECLARADAS NO MANUAL")
# v0.239 do sistema: o numero e a pagina moravam aqui, e as duas coisas envelheceram -- o
# catalogo tinha catorze condicoes e o manual passou a dizer treze. Agora cada contagem sai da
# frase em que o proprio manual a declara, lida do manual.txt. Melhorias, Formas e Restricoes o
# manual nao conta por extenso, e por isso cada nome delas tem de aparecer nele.
import re
MAN = " ".join(open("manual.txt", encoding="utf-8").read().split())
_U = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
      "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
EXT = {p: n for n, p in enumerate(_U)}
EXT.update({"uma": 1, "duas": 2, "vinte": 20, "trinta": 30})
EXT.update({f"vinte e {p}": 20 + n for n, p in enumerate(_U[1:10], 1)})
EXT.update({"vinte e uma": 21, "vinte e duas": 22})
_NUM = "|".join(sorted(map(re.escape, EXT), key=len, reverse=True))

def declarado(rx):
    m = re.search(rx.replace("NUM", "(" + _NUM + ")"), MAN)
    return (EXT[m.group(1)], m.group(0)) if m else (None, None)

for nome, chave, rx in [("pericias", "pericias", r"\bNUM perícias"), ("oficios", "oficios", r"\bNUM ofícios"),
                        ("Familias", "familias", r"divididas em NUM Famílias"),
                        ("condicoes", "condicoes", r"\bas NUM condições")]:
    n = len(CAT[chave]); d, frase = declarado(rx)
    ok = d == n
    if not ok: falhas.append(f"{nome}: {n} != {d}")
    print(f"  [{'OK' if ok else 'FALHA'}] {nome:10} {n:3}   o manual declara {d}: '{frase}'")
mt = re.search(r"São (" + _NUM + r") Caminhos, (" + _NUM + r") Trilhas em cada um", MAN)
dc, dt = (EXT[mt.group(1)], EXT[mt.group(1)] * EXT[mt.group(2)]) if mt else (None, None)
for nome, chave, d in (("Caminhos", "caminhos", dc), ("Trilhas", "trilhas", dt)):
    n = len(CAT[chave]); ok = d == n
    if not ok: falhas.append(f"{nome}: {n} != {d}")
    print(f"  [{'OK' if ok else 'FALHA'}] {nome:10} {n:3}   o manual declara {d}: '{mt.group(0) if mt else None}'")

def no_manual(nome):
    """o pdftotext -layout parte a celula de tabela, e a coluna do lado entra no meio do nome"""
    rx = r"\b" + r"\b(?:\s+\S+){0,25}?\s+\b".join(re.escape(p) for p in nome.split()) + r"\b"   # "Abre ... Ferida" tem 16 no meio
    return re.search(rx, MAN) is not None

for nome, chave in (("Melhorias", "melhorias"), ("Formas", "formas"), ("Restricoes", "restricoes")):
    faltam = [x for x in CAT[chave] if not no_manual(x)]
    if faltam: falhas.append(f"{nome} que o manual nao tem: {faltam}")
    print(f"  [{'OK' if not faltam else 'FALHA'}] as {len(CAT[chave])} {nome} do catalogo aparecem no manual"
          + (f"  <- faltam {faltam}" if faltam else ""))

print("\nTRAVAS DE ESTRUTURA")
sem_pericia = [a for a in CAT["atributos"]["lista"]
               if not any(v["atributo"] == a for v in CAT["pericias"].values())]
ok = sem_pericia == ["Constituição"]
if not ok: falhas.append("Constituição deveria ser o unico atributo sem pericia")
print(f"  [{'OK' if ok else 'FALHA'}] Constituição e o unico atributo sem pericia (achei: {sem_pericia})")
tr = [t for t in CAT["trilhas"].values()]
ok = all(tr.count(c) == 3 for c in CAT["caminhos"])
if not ok: falhas.append("nem todo Caminho tem 3 Trilhas")
print(f"  [{'OK' if ok else 'FALHA'}] cada um dos 5 Caminhos tem exatamente 3 Trilhas")

print(f"\n{'TUDO VERDE' if not falhas else str(len(falhas)) + ' FALHA(S): ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
