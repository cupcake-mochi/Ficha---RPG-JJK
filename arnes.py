# -*- coding: utf-8 -*-
"""Arnes de perturbacao: prova que cada checagem acende quando devia.
Regra 2 da skill: a base tem que passar limpa antes de perturbar."""
from conferir_feitico import conferir, mostra

BASE = {"classe": 3, "familias_livres": ["Castigo", "Mira"],
        "familias_fechadas": ["Amparo", "Área", "Auxiliares"],
        "melhorias": ["Precisão", "Fura"], "restricoes": ["Gesto"]}

print("=" * 66)
print("PASSO 1 - a base passa limpa?  (sem isso, toda perturbacao e falso positivo)")
r = mostra("feitico base", BASE)
assert not r["erros"], "BASE JA FALHA: o arnes inteiro seria falso positivo"
print("\n  base limpa. pode perturbar.\n")

print("=" * 66)
print("PASSO 2 - cada perturbacao acende a checagem certa?")
PERTURBACOES = [
    ("R3 teto de Melhorias", {**BASE, "melhorias": ["Precisão","Fura","Certeiro","De Novo"]}, "R3"),
    ("R3 teto de Restricoes", {**BASE, "restricoes": ["Gesto","Parado","Barulho"]}, "R3"),
    ("R7 duas de frequencia", {**BASE, "restricoes": ["Uma Vez","Aquecer"]}, "R7"),
    ("Familia fechada",       {**BASE, "melhorias": ["Precisão","Junto"]}, "Familia fechada"),
    ("R2b espalhar o dano",   {**BASE, "melhorias": ["Salto","Queima"], "restricoes": ["Gesto","Barulho"],
                               "familias_livres": ["Castigo","Área"], "familias_fechadas": ["Amparo","Mira","Tempo"]}, "R2b"),
    ("A3 Rapido + Lento",     {**BASE, "melhorias": ["Rápido"], "restricoes": ["Lento"]}, "A3"),
    ("A3 Rapido + Reacao",    {**BASE, "melhorias": ["Rápido","Reação"], "restricoes": []}, "A3"),
]
for nome, f, esperado in PERTURBACOES:
    erros = conferir(f)["erros"]
    acendeu = any(esperado in e for e in erros)
    print(f"  [{'ACENDEU' if acendeu else 'NAO ACENDEU'}] {nome:26} -> {erros if erros else 'nada'}")

print()
print("=" * 66)
print("PASSO 3 - contra-teste: a checagem A3 fica quieta quando devia?")
print("  (sem isso ela poderia estar acendendo para qualquer feitico)")
SOZINHAS = [
    ("so Rapido, sem Lento",  {**BASE, "melhorias": ["Rápido"], "restricoes": ["Gesto"]}),
    ("so Lento, sem Rapido",  {**BASE, "melhorias": ["Precisão"], "restricoes": ["Lento"]}),
    ("so Reacao, sem Rapido", {**BASE, "melhorias": ["Reação"], "restricoes": ["Gesto"]}),
]
for nome, f in SOZINHAS:
    a3 = [e for e in conferir(f)["erros"] if e.startswith("A3")]
    print(f"  [{'QUIETA' if not a3 else 'ACENDEU A TOA'}] {nome:26} -> {a3 if a3 else 'nenhum erro A3'}")
