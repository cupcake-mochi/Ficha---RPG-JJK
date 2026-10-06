# -*- coding: utf-8 -*-
"""Regressao contra os feiticos que o livro publica montados.
Se o validador nao reproduz exemplo impresso, o validador esta errado.

04/10/2026: o livro reconstruido nao tem mais os dois feiticos da p.137 (Marca do Carrasco e Domo de Gelo). Os
exemplos agora sao os de montagem do livro novo, que o ficha-v01/extrair_tecnica.py le do manual.txt e confere pela
frase de cada um (chave feiticos_prontos do tecnica-do-livro.json): o mesmo oraculo da regressao-amaldicoada.py,
passado aqui pelo conferir_feitico.py, sem a planilha."""
import json, sys
from conferir_feitico import conferir

TEC = json.load(open("ficha-v01/tecnica-do-livro.json", encoding="utf-8"))
falhas = 0
for e in TEC["feiticos_prontos"]:
    f = {"classe": e["classe"], "familias_livres": e.get("livres", []), "familias_fechadas": [],
         "melhorias": e["mel"], "restricoes": [r.split("|")[0] for r in e["res"]], "forma": e["forma"],
         "liberacao_maxima": e["lib"]}
    try:
        r = conferir(f)
        got = int(r["dano"].replace("d8", ""))
        ok = got == e["dados"] and not r["erros"]
        falhas += not ok
        print(f"  [{'BATE' if ok else 'NAO BATE'}] {e['nome']:20} validador da {got}d8, o livro imprime {e['dados']}d8"
              f"   (custo {r['custo_bruto']}, restricao devolveu {r['restricao_devolveu']})" + (f"  {r['erros']}" if r["erros"] else ""))
    except KeyError as k:
        falhas += 1
        print(f"  [ERRO] {e['nome']}: {k} nao esta no catalogo")
print(f"\n{'OS ' + str(len(TEC['feiticos_prontos'])) + ' EXEMPLOS DO LIVRO BATEM' if not falhas else str(falhas) + ' FALHA(S)'}")
sys.exit(1 if falhas else 0)
