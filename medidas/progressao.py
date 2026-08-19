# -*- coding: utf-8 -*-
"""A tabela de progressao do manual (p.192) sai de formula?
Se sair, a ficha calcula do nivel 2 ao 30 sem carregar tabela nenhuma,
e nunca desatualiza. Se nao sair, a tabela vira catalogo e precisa de dono."""
import re, json
L = open('manual.txt', encoding='utf-8').read().split('\n')
TAB = {}
for raw in L[10695:10765]:
    s = re.sub(r'\s+', ' ', raw.strip())
    m = re.match(r'^(\d{1,2}) ([\d.]+|—) (\d) (\d{1,2}) (\d) (\d) (\d) (\d)(?: (.*))?$', s)
    if m:
        n = int(m.group(1))
        TAB[n] = {"xp": m.group(2), "maestria": int(m.group(3)), "espacos": int(m.group(4)),
                  "refino": int(m.group(5)), "classe": int(m.group(6)),
                  "passiva": int(m.group(7)), "classe0": int(m.group(8)),
                  "entrega": (m.group(9) or "—").strip()}
print(f"linhas lidas da tabela impressa: {len(TAB)}  (níveis {min(TAB)} a {max(TAB)})\n")

MARCOS = [6, 10, 14, 18, 22, 26, 30]
def marcos_ate(n): return sum(1 for m in MARCOS if m <= n)
# as formulas que o manual declara em texto
F = {
 "maestria": lambda n: 1 + n // 8,
 "espacos":  lambda n: 2 + n // 2 + marcos_ate(n),
 "refino":   lambda n: 1 + marcos_ate(n),
 "classe":   lambda n: sum(1 for a in (1, 5, 9, 13, 17, 21, 26) if a <= n),
 "classe0":  lambda n: 2 + sum(1 for a in (5, 11, 17) if a <= n),
}
print(f"{'campo':10} {'confere':>8}  onde falha")
falhas_tot = 0
for campo, f in F.items():
    ruins = [(n, F[campo](n), d[campo]) for n, d in sorted(TAB.items()) if f(n) != d[campo]]
    falhas_tot += len(ruins)
    ok = f"{len(TAB)-len(ruins)}/{len(TAB)}"
    det = "" if not ruins else "  ".join(f"nv{n}: fórmula {a}, tabela {b}" for n,a,b in ruins[:4])
    print(f"  {campo:10} {ok:>8}  {det}")
print()
if not falhas_tot:
    print("TODAS AS COLUNAS NUMÉRICAS SAEM DE FÓRMULA.")
    print("A ficha calcula do nível 2 ao 30 sem carregar a tabela.")
# o que NAO sai de formula
print("\nO QUE NÃO SAI DE FÓRMULA (precisa ficar como catálogo):\n")
for n, d in sorted(TAB.items()):
    if d["entrega"] != "—":
        print(f"  nível {n:2}  {d['entrega']}")
json.dump(TAB, open('_progressao.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
