# -*- coding: utf-8 -*-
"""Regressao contra os feiticos ja publicados no manual (p.137).
Se o validador nao reproduz exemplo impresso, o validador esta errado."""
from conferir_feitico import conferir

EXEMPLOS = [
 ("Marca do Carrasco", {"classe":3, "familias_livres":[], "familias_fechadas":[],
   "melhorias":["Marca","Queima"], "restricoes":["Uma Vez"]}, 6),
 ("Domo de Gelo", {"classe":3, "familias_livres":[], "familias_fechadas":[],
   "melhorias":["Terreno","Maior"], "restricoes":["Condicional"], "forma":"Explosão"}, 5),
]
for nome, f, dano_impresso in EXEMPLOS:
    try:
        r = conferir(f)
        got = int(r["dano"].replace("d8",""))
        print(f"  [{'BATE' if got==dano_impresso else 'NAO BATE'}] {nome:20} validador da {got}d8, "
              f"manual p.137 imprime {dano_impresso}d8   (custo {r['custo_bruto']}, "
              f"restricao devolveu {r['restricao_devolveu']})")
    except KeyError as e:
        print(f"  [ERRO] {nome}: Melhoria {e} nao esta no catalogo")
