# -*- coding: utf-8 -*-
"""Convivência célula a célula entre duas frentes (fora de CONFIGURAÇÃO/ANALISE, onde as linhas andam).

    python comparar_frentes.py base.json so_a.json so_b.json combinado.json

Modelos de `monta.py --exportar-pecas`. Para cada aba: quantas células cada frente muda, quantas as duas
mudam, e se o combinado reproduz cada frente isolada nas células só dela. Menus idem.
"""
import json
import sys

nomes = ('base', 'a', 'b', 'comb')
M = {n: json.load(open(p, encoding='utf-8')) for n, p in zip(nomes, sys.argv[1:5])}
cel = {n: {a['nome']: {c[0]: c[1] for c in a['celulas']} for a in m['layout']['abas']} for n, m in M.items()}


def dif(x, y):
    out = {}
    for aba in set(cel[x]) | set(cel[y]):
        p, q = cel[x].get(aba, {}), cel[y].get(aba, {})
        d = {k for k in set(p) | set(q) if p.get(k) != q.get(k)}
        if d:
            out[aba] = d
    return out


da, db = dif('base', 'a'), dif('base', 'b')
problemas = 0
for aba in sorted(set(da) | set(db)):
    if aba in ('CONFIGURAÇÃO', 'ANALISE'):
        continue
    a, b = da.get(aba, set()), db.get(aba, set())
    ambas = a & b
    ok_a = all(cel['comb'].get(aba, {}).get(k) == cel['a'].get(aba, {}).get(k) for k in a - b)
    ok_b = all(cel['comb'].get(aba, {}).get(k) == cel['b'].get(aba, {}).get(k) for k in b - a)
    problemas += bool(ambas) + (not ok_a) + (not ok_b)
    print(f'{aba:18} A {len(a):5} B {len(b):5} ambas {len(ambas):4} comb=A {ok_a} comb=B {ok_b}')
    for k in sorted(ambas)[:3]:
        for n in nomes:
            print(f'    {k} {n:5}: {str(cel[n].get(aba, {}).get(k))[:200]}')


def menus(n, aba):
    a = next((x for x in M[n]['layout']['abas'] if x['nome'] == aba), None)
    return {m['onde']: m['formula'] for m in (a or {}).get('menus', [])}


for aba in ('INVOCAÇÕES', 'FICHA', 'FICHA AMALDIÇOADA'):
    b0, ma, mb, mc = (menus(n, aba) for n in nomes)
    ca = {k for k in b0 if ma.get(k) != b0.get(k)}
    cb = {k for k in b0 if mb.get(k) != b0.get(k)}
    ok = all(mc.get(k) == ma.get(k) for k in ca - cb) and all(mc.get(k) == mb.get(k) for k in cb - ca)
    problemas += bool(ca & cb) + (not ok)
    print(f'menus {aba:17} A {len(ca):4} B {len(cb):4} ambas {len(ca & cb):3} comb ok {ok}')
print('PROBLEMAS', problemas)
sys.exit(1 if problemas else 0)
