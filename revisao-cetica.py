# -*- coding: utf-8 -*-
"""Revisao cetica da ESPECIFICACAO contra o catalogo e contra o manual.
Procura ativamente o erro no que eu mesmo escrevi."""
import json, re
SPEC = open('ESPECIFICACAO-ficha-digital.md', encoding='utf-8').read()
MAN = open('manual.txt', encoding='utf-8').read()
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
falhas = []
def checa(desc, cond, detalhe=""):
    print(f"  [{'OK' if cond else 'FALHA'}] {desc}{'' if cond else '  <- ' + detalhe}")
    if not cond: falhas.append(desc)

print("AFIRMACOES DA SPEC vs CATALOGO")
checa("as 9 Familias da spec sao as do catalogo",
      all(f in SPEC for f in CAT["familias"]),
      str([f for f in CAT["familias"] if f not in SPEC]))
checa("as 23 pericias aparecem na spec",
      all(p in SPEC for p in CAT["pericias"]),
      str([p for p in CAT["pericias"] if p not in SPEC]))
checa("os 11 oficios aparecem na spec",
      all(o in SPEC for o in CAT["oficios"]),
      str([o for o in CAT["oficios"] if o not in SPEC]))
checa("as 15 Trilhas aparecem na spec",
      all(t in SPEC for t in CAT["trilhas"]),
      str([t for t in CAT["trilhas"] if t not in SPEC]))
checa("as 10 Formas aparecem na spec",
      all(f in SPEC for f in CAT["formas"]),
      str([f for f in CAT["formas"] if f not in SPEC]))
orfas = sum(1 for v in CAT["melhorias"].values() if v["familia"] in ["Alcance","Mira","Tempo","Marca"])
checa(f"a spec diz '27 das 66' e a conta da {orfas}", f"**27 das 66" in SPEC and orfas == 27, f"conta={orfas}")

print("\nAFIRMACOES DA SPEC vs MANUAL")
for frase, agulha in [
    ("Vida do Bastiao 12/7 e PE 4",        "Bastião       d12    12                 7           4"),
    ("teto de dano e 4 x Classe",          "Teto de dano = 4 × Classe em dados"),
    ("devolucao maxima e 2 x Classe",      "Devolução máxima = 2 × Classe"),
    ("Liberacao Maxima da + Classe",       "Liberação Máxima = + Classe em dados"),
    ("a Forma nao conta como Melhoria",    "A Forma não conta como Melhoria."),
    ("Classe 0 e gratis",                  "Classe 0 é\ngrátis."),
    ("arredondamento contra voce",         "Arredonde para cima"),
]:
    checa(frase, agulha.replace("\n"," ") in MAN.replace("\n"," "), "nao achei no manual")

print("\nO QUE A SPEC PODE ESTAR DEIXANDO DE FORA")
for termo, onde in [("PE da Liberação Máxima", "custo em PE da Liberacao Maxima"),
                    ("Restrições: até 2", "teto de Restricoes"),
                    ("três feitiços conhecidos", "feiticos do nivel 2")]:
    print(f"  [{'presente' if termo in SPEC else 'AUSENTE'}] {onde}  ('{termo}')")

print(f"\n{'REVISAO LIMPA' if not falhas else str(len(falhas)) + ' PROBLEMA(S)'}")
