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
for nome, chave, declarado, pag in [("pericias","pericias",23,26), ("oficios","oficios",11,28),
        ("Familias","familias",9,105), ("Melhorias","melhorias",66,116),
        ("condicoes","condicoes",14,118), ("Trilhas","trilhas",15,78), ("Formas","formas",10,140)]:
    n = len(CAT[chave]); ok = n == declarado
    if not ok: falhas.append(f"{nome}: {n} != {declarado}")
    print(f"  [{'OK' if ok else 'FALHA'}] {nome:10} {n:3}   manual p.{pag} declara {declarado}")

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
