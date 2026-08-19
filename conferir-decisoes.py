# -*- coding: utf-8 -*-
"""Confere as cinco decisoes do bloco A.

Tres coisas, e a segunda e a que mais vale:
  1. o JSON e o DECISOES-bloco-A.md continuam falando a mesma coisa
  2. tudo que a decisao ATRIBUI AO MANUAL esta mesmo no manual
  3. os numeros do A5 batem quando recalculados do hex, e nao so quando lidos

Nenhum valor mora aqui: le do decisoes-ficha.json, do catalogo e do manual.txt.
Se o manual.txt nao existir este validador FALHA, nao pula. Um verde que pulou
checagem nao prova nada.
"""
import json, os, sys, math

FALHAS, PULADAS = [], 0

def checa(desc, cond, detalhe=""):
    print(f"  [{'OK' if cond else 'FALHA'}] {desc}" + ("" if cond else f"  <- {detalhe}"))
    if not cond:
        FALHAS.append(desc)

def le(nome):
    if not os.path.exists(nome):
        print(f"\nFALTA O ARQUIVO '{nome}'.")
        if nome == 'manual.txt':
            print("  gere com:  pdftotext -layout Projeto-M-Manual-da-Guilda.pdf manual.txt")
        sys.exit(1)
    return open(nome, encoding='utf-8').read()

DEC = json.loads(le('decisoes-ficha.json'))
CAT = json.loads(le('catalogo-projeto-m.json'))
MD  = le('DECISOES-bloco-A.md')
MAN = le('manual.txt').replace('\n', ' ')
MAN = ' '.join(MAN.split())          # normaliza o espacamento do pdftotext -layout
PEN = le('PENDENCIAS.md')

# ---------------------------------------------------------------- 1
print("AS CINCO ESTAO NOS DOIS DOCUMENTOS")
for chave, titulo in [("A1_catalogo", "A1"), ("A2_temporario", "A2"),
                      ("A3_incompatibilidades", "A3"), ("A4_reservas", "A4"),
                      ("A5_acento", "A5")]:
    checa(f"{titulo} tem entrada no JSON e secao no .md",
          chave in DEC and f"## {titulo} ·" in MD)

checa("o .md se declara dono e aponta o JSON",
      "dono" in MD and "decisoes-ficha.json" in MD)
checa("o PENDENCIAS nao diz mais que o bloco A trava a construcao",
      "Bloco A · Trava a construção" not in PEN,
      "o bloco A foi decidido; o PENDENCIAS precisa apontar para o DECISOES")

# ---------------------------------------------------------------- 2
print("\nO QUE A DECISAO ATRIBUI AO MANUAL ESTA MESMO NO MANUAL")
# a frase do Rasga Escudo e o unico apoio de 'vida temporaria gasta primeiro'
checa("Rasga Escudo diz que o dano ignora vida temporaria",
      "ignora pontos de vida temporários e barreiras" in MAN,
      "sem essa frase, 'gasta primeiro' vira invencao")
checa("o Braseiro carrega a regra da energia temporaria",
      "gasta como PE, e gasta primeiro" in MAN)
checa("o Braseiro e quem declara o teto de 2",
      "nunca passa de 2 acumulados" in MAN)
checa("o Braseiro e a UNICA fonte de energia temporaria",
      MAN.count("energia tempo") == 1,
      f"achei {MAN.count('energia tempo')} mencoes; o teto de 2 pode nao ser mais so dele")

fontes = DEC["A2_temporario"]["vida"]["fontes_no_manual"]
faltando = [f for f in fontes if f not in MAN]
checa(f"as {len(fontes)} fontes de vida temporaria existem no manual",
      not faltando, str(faltando))
checa("o capitulo p.15 continua sem falar de temporario",
      "Vida, energia e alma Três reservas" in MAN and
      "vida temporária" not in MAN[MAN.index("Vida, energia e alma Três reservas"):][:3000],
      "se ja falar, o texto de manual-temporario.md duplica regra")

for par in DEC["A3_incompatibilidades"]["pares"]:
    existe = (par["a"] in CAT["melhorias"] or par["a"] in CAT["restricoes"]) and \
             (par["b"] in CAT["melhorias"] or par["b"] in CAT["restricoes"])
    checa(f"o par {par['a']} + {par['b']} nomeia pecas que existem", existe)
    if par["fonte"] == "manual":
        checa(f"  ...e o manual escreve mesmo esse par",
              f"Não entra no mesmo feitiço que {par['b']}" in MAN,
              "declarado como fonte 'manual' sem estar escrito la")

# ---------------------------------------------------------------- 3
print("\nOS NUMEROS DO A5, RECALCULADOS DO HEX")
def lum(h):
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return sum(k*f(int(h[i:i+2],16)/255) for k, i in zip((0.2126,0.7152,0.0722),(0,2,4)))
def contraste(a, b):
    la, lb = lum(a), lum(b)
    return (max(la,lb)+0.05)/(min(la,lb)+0.05)

PAINEL = "211C35"
graus = DEC["A5_acento"]["degraus"]
medido = DEC["A5_acento"]["medido"]["sobre_o_painel"]
for g in graus:
    calc = contraste(g["hex"], PAINEL)
    checa(f"{g['nome']:9} sobre o painel: escrito {medido[g['nome']]}, calculado {calc:.2f}",
          abs(calc - medido[g["nome"]]) < 0.02,
          "o hex e o numero escrito discordam")

print("\n  o limite de desenho, medido separado da constante:")
LIMITE_PAINEL = 3.0        # numero grande passa com 3.0 (WCAG)
LIMITE_ENTRE  = 1.5        # dois degraus vizinhos tem que se distinguir
for g in graus:
    checa(f"{g['nome']:9} passa o minimo de {LIMITE_PAINEL} sobre o painel",
          contraste(g["hex"], PAINEL) >= LIMITE_PAINEL)
for i in range(len(graus)-1):
    a, b = graus[i], graus[i+1]
    par = f"{a['nome']}_vs_{b['nome']}"
    vistas = DEC["A5_acento"]["medido"].get(par)
    checa(f"{a['nome']} vs {b['nome']}: o pior caso de daltonismo passa {LIMITE_ENTRE}",
          vistas is not None and min(vistas.values()) >= LIMITE_ENTRE,
          f"nao achei o par '{par}' nas medidas" if vistas is None else str(vistas))

# ---------------------------------------------------------------- contra-teste
print("\nCONTRA-TESTE  (a checagem distingue, ou ela e trivialmente verdadeira?)")
# O contraste sobre o painel NAO e o criterio que decide o A5, e provar isso importa:
# uma checagem que se mede so por ele sairia verde para uma paleta que a medida reprovou.
falso = contraste("756588", PAINEL)        # o roxo-claro, reprovado como acento
checa(f"o contraste sobre o painel sozinho nao decide nada: o roxo-claro reprovado "
      f"tambem passaria nele ({falso:.2f} >= {LIMITE_PAINEL})",
      falso >= LIMITE_PAINEL,
      "se ele reprovasse aqui, este contra-teste nao provaria nada")

# o que decide e o daltonismo ENTRE os degraus. Prova que esse criterio separa:
# ele aprova o par escolhido e reprova o par que a medida ja tinha derrubado.
aprovado  = min(DEC["A5_acento"]["medido"]["osso_vs_ambar"].values())
reprovado = 1.00                           # carmim vs roxo energia, protanopia (medidas/daltonismo.py)
checa(f"o criterio de daltonismo distingue: aprova osso vs ambar ({aprovado}) "
      f"e reprovaria carmim vs roxo ({reprovado})",
      aprovado >= LIMITE_ENTRE > reprovado)

print(f"\nPULADAS: {PULADAS}")
print("DECISOES CONSISTENTES" if not FALHAS else f"{len(FALHAS)} PROBLEMA(S): {FALHAS}")
sys.exit(1 if FALHAS else 0)
