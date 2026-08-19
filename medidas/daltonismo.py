# -*- coding: utf-8 -*-
"""Simula protanopia e deuteranopia sobre a paleta proposta.
Nao adianta escolher cor bonita se ~8% dos homens nao distinguem duas delas.
Matriz de Brettel/Vienot, a padrao para simulacao."""
import numpy as np
def rgb(h): return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def hexa(v): return "%02X%02X%02X" % tuple(int(max(0,min(1,c))*255) for c in v)
def lin(c): return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def slin(c): return np.where(c <= 0.0031308, c*12.92, 1.055*np.power(np.clip(c,0,1),1/2.4)-0.055)
M   = np.array([[0.31399,0.63951,0.04649],[0.15537,0.75789,0.08670],[0.01775,0.10945,0.87262]])
Mi  = np.linalg.inv(M)
PROT = np.array([[0,1.05118294,-0.05116099],[0,1,0],[0,0,1]])
DEUT = np.array([[1,0,0],[0.9513092,0,0.04866992],[0,0,1]])
def simula(h, mat):
    lms = M @ lin(rgb(h)); return hexa(slin(Mi @ (mat @ lms)))
def lum(h):
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return sum(k*f(int(h[i:i+2],16)/255) for k,(i) in zip((0.2126,0.7152,0.0722),(0,2,4)))
def contraste(a,b):
    la,lb = lum(a),lum(b); return (max(la,lb)+0.05)/(min(la,lb)+0.05)

CORES = {"painel":"211C35","roxo_claro":"756588","carmim":"E0526B",
         "vermelho":"C2334D","roxo_energia":"9D5CE8","osso":"E8DCD4","ambar":"D89B3A"}
print("COMO CADA COR APARECE PARA QUEM TEM DEFICIENCIA DE VISAO DE COR\n")
print(f"{'cor':14} {'normal':>9} {'protanopia':>12} {'deuteranopia':>14}")
for n,h in CORES.items():
    print(f"  {n:12} #{h}  #{simula(h,PROT)}  #{simula(h,DEUT)}")
print("\nOS PARES QUE PRECISAM SER DISTINGUIVEIS  (vida vs energia, e destaque vs base)\n")
for a,b,rot in [("carmim","roxo_energia","vida carmim vs PE roxo"),
                ("carmim","roxo_claro","vida carmim vs bloco roxo-claro"),
                ("ambar","carmim","ambar vs carmim"),
                ("osso","roxo_claro","osso vs roxo-claro")]:
    n  = contraste(CORES[a], CORES[b])
    p  = contraste(simula(CORES[a],PROT), simula(CORES[b],PROT))
    d  = contraste(simula(CORES[a],DEUT), simula(CORES[b],DEUT))
    pior = min(n,p,d)
    v = "distingue" if pior >= 3 else ("fraco" if pior >= 2 else "VIRA A MESMA COR")
    print(f"  {rot:34} normal {n:4.2f} · prot {p:4.2f} · deut {d:4.2f}   {v}")
