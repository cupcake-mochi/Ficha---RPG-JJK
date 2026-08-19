# -*- coding: utf-8 -*-
"""DECISAO DO MIZUKI: Queima conta como repeticao para o teto de 4 x Classe.
Busca exaustiva: existe montagem LEGAL em todo o resto que ainda estoura o teto?
Se existir, a ficha digital precisa recusar, porque nenhum mestre pega isso no olho."""
import itertools, math, json
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
MEL, RES = CAT["melhorias"], CAT["restricoes"]
ESPALHA = {"Salto": 0.5, "Queima": 0.5}          # somam metade dos dados
DIVIDEM = {"Mais Um", "Rajada"}                   # contam no teto mas nao fazem crescer
FREQ = {"Uma Vez", "Condicional", "Aquecer", "Dívida"}
TETO_MEL = lambda c: 2 if c <= 2 else (3 if c <= 4 else 4)
def preco(peso, c, livre):
    p = math.ceil({"Leve": c/2, "Media": c, "Pesada": c*1.5}[peso])
    return max(1, p - math.ceil(c/2)) if livre else p
def devolve(niv, c): return math.ceil({"Leve": c/2, "Media": c}[niv])

print(f"{'Cl':>3} {'orc':>4} {'teto':>5} {'pior':>6}  {'Melhorias':<22} {'Restricoes':<24} {'Livres':<18}")
for c in range(1, 8):
    teto, melhor, como = 4*c, 0, None
    fams = list(CAT["familias"])
    for livres in itertools.combinations(fams, 2):
        for nm in range(1, TETO_MEL(c)+1):
            for mel in itertools.combinations(ESPALHA, min(nm, 2)):
                custo = sum(preco(MEL[m]["peso"], c, MEL[m]["familia"] in livres) for m in mel)
                for nr in range(0, 3):
                    for res in itertools.combinations(RES, nr):
                        if len([r for r in res if r in FREQ]) >= 2: continue   # regra 7
                        dev = min(2*c, sum(devolve(RES[r]["devolve"].replace("é","e"), c) for r in res))
                        liquido = custo - min(dev, custo)                      # regra 1
                        base = 3*c - liquido
                        if base < 0: continue
                        total = base + sum(base*ESPALHA[m] for m in mel)
                        if total > melhor: melhor, como = total, (mel, res, livres)
    m, r, lv = como
    print(f"{c:>3} {3*c:>4} {teto:>5} {melhor:>6.1f}  {' + '.join(m):<22} {' + '.join(r):<24} "
          f"{' + '.join(lv):<18} {'ESTOURA' if melhor > teto else 'cabe'}")
