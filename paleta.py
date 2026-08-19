# -*- coding: utf-8 -*-
"""Deriva uma paleta a partir das duas cores do servidor e MEDE cada par.
Nada aqui e' escolhido no olho: contraste WCAG decide o que pode receber texto."""
import colorsys
BASE, CLARO = "211c35", "756588"

def rgb(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))
def hexa(t): return "%02X%02X%02X" % tuple(max(0,min(255,round(c))) for c in t)
def lum(h):
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return sum(k*f(c/255) for k,c in zip((0.2126,0.7152,0.0722), rgb(h)))
def contraste(a,b):
    la, lb = lum(a), lum(b)
    return (max(la,lb)+0.05)/(min(la,lb)+0.05)
def ajusta(h, fator):
    r,g,b = [c/255 for c in rgb(h)]
    hh,l,s = colorsys.rgb_to_hls(r,g,b)
    l2 = max(0, min(1, l*fator))
    return hexa([c*255 for c in colorsys.hls_to_rgb(hh, l2, s)])

P = {
 "fundo":        ajusta(BASE, 0.55),   # mais fundo que a base, para a base virar painel
 "painel":       BASE,                 # a cor do servidor
 "painel_alto":  ajusta(BASE, 1.45),   # bloco que sobe do painel
 "linha":        ajusta(CLARO, 0.62),  # divisoria e borda
 "roxo_claro":   CLARO,                # a segunda cor do servidor
 "texto":        "F4F1F7",
 "texto_fraco":  ajusta(CLARO, 1.30),
}
print("A PALETA, DERIVADA DAS SUAS DUAS CORES\n")
for k,v in P.items(): print(f"  {k:13} #{v}")
print("\nCONTRASTE  (4.5 = texto pequeno · 3.0 = texto grande · abaixo disso nao usar)\n")
PARES = [("texto",       "fundo"),      ("texto",       "painel"),
         ("texto",       "painel_alto"),("texto_fraco", "painel"),
         ("texto_fraco", "fundo"),      ("roxo_claro",  "fundo"),
         ("roxo_claro",  "painel"),     ("linha",       "painel")]
for a,b in PARES:
    c = contraste(P[a], P[b])
    v = "texto pequeno OK" if c >= 4.5 else ("so texto grande" if c >= 3 else "so bloco, nunca texto")
    print(f"  {a:12} sobre {b:12} {c:5.2f}   {v}")
print("\nCANDIDATAS A COR DE DESTAQUE  (precisa ler sobre painel E sobre fundo)\n")
for nome, cor in [("vermelho sangue","C2334D"), ("carmim claro","E0526B"),
                  ("roxo energia","9D5CE8"), ("osso","E8DCD4"), ("ambar","D89B3A")]:
    cp, cf = contraste(cor, P["painel"]), contraste(cor, P["fundo"])
    ok = "SERVE" if min(cp,cf) >= 4.5 else ("so numero grande" if min(cp,cf) >= 3 else "nao serve")
    print(f"  {nome:16} #{cor}   sobre painel {cp:5.2f} · sobre fundo {cf:5.2f}   {ok}")
