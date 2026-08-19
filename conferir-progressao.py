# -*- coding: utf-8 -*-
"""As formulas de progressao reproduzem a tabela impressa do manual (p.192)?
Nasceu de um erro real: a formula de maestria escrita como 'a cada oito niveis'
dava +1 de CD e de ataque de conjuracao em seis dos trinta niveis."""
import json, sys
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
P = CAT["progressao"]; TAB = P["tabela_impressa"]; MARCOS = P["marcos"]
def marcos_ate(n): return sum(1 for m in MARCOS if m <= n)
F = {
 "maestria": lambda n: 1 + sum(1 for a in (10,18,26) if a <= n),
 "espacos":  lambda n: 2 + n//2 + marcos_ate(n),
 "refino":   lambda n: 1 + marcos_ate(n),
 "classe":   lambda n: sum(1 for a in (1,5,9,13,17,21,26) if a <= n),
 "classe0":  lambda n: 2 + sum(1 for a in (5,11,17) if a <= n),
}
falhas = []
print(f"{'coluna':12} {'confere':>9}   onde falha")
for campo, f in F.items():
    ruins = sorted(int(n) for n in TAB if f(int(n)) != TAB[n][campo])
    if ruins: falhas.append((campo, ruins))
    print(f"  {campo:12} {len(TAB)-len(ruins):>4}/{len(TAB)}   {ruins if ruins else ''}")
# contra-teste: a formula ERRADA tem que reprovar, senao esta checagem nao prova nada
errada = lambda n: 1 + n//8
pega = sorted(int(n) for n in TAB if errada(int(n)) != TAB[n]["maestria"])
print(f"\n  [contra-teste] a fórmula antiga (1 + nivel//8) erra nos níveis {pega}")
print(f"  -> a checagem distingue as duas, então ela não é trivialmente verdadeira")
print(f"\n{'TUDO BATE' if not falhas else str(len(falhas)) + ' COLUNA(S) FORA'}")
sys.exit(1 if falhas else 0)
