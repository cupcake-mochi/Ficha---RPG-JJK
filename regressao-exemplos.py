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
# 23/11/2026: a devolução Leve do Toque (R53, "Toque, Aura e proximidade"). Montagens que o livro escreve em
# prosa, fora do tecnica-do-livro.json, e a regra da Máxima, que tira a devolução do Toque.
TOQUE = [
    ("Toque + Precisão, Classe 3", 3, ["Precisão"], [], False, 9, "9 − 2 + 2 = 9d8 de dano (Formas, o exemplo da tabela)"),
    ("Iori, Toque + Prende", 1, ["Prende"], [], False, 3, "A conta é 3 − 1 + 1 = 3"),
    ("Rika, Toque + Reação", 2, ["Reação"], ["Tempo"], False, 5, "O saldo fica 6 − 2 + 1 = 5"),
    ("Máxima com Toque", 3, ["Precisão"], [], True, 10, "a Máxima: Toque não concede sua devolução automática (9 − 2 + 3)"),
]
for nome, c, mel, livres, lib, esperado, fonte in TOQUE:
    r = conferir({"classe": c, "familias_livres": livres, "familias_fechadas": [], "melhorias": mel,
                  "restricoes": [], "forma": "Toque", "liberacao_maxima": lib})
    got = int(r["dano"].replace("d8", ""))
    ok = got == esperado and not r["erros"]
    falhas += not ok
    print(f"  [{'BATE' if ok else 'NAO BATE'}] {nome:26} validador da {got}d8, o livro: {fonte}" + (f"  {r['erros']}" if r["erros"] else ""))
print(f"\n{'OS ' + str(len(TEC['feiticos_prontos']) + len(TOQUE)) + ' EXEMPLOS DO LIVRO BATEM' if not falhas else str(falhas) + ' FALHA(S)'}")
sys.exit(1 if falhas else 0)
