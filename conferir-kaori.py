# -*- coding: utf-8 -*-
"""Regressao completa: o catalogo reproduz TODOS os numeros impressos na
ficha-exemplo-kaori.docx? Le os dois lados; nada esta escrito na mao aqui."""
import json, re
from docx import Document
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
DOC = Document('repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx')

# A INTEGRIDADE NAO MORA MAIS AQUI. Ate a v0.145 do sistema ela era plana —
# `20 + 8 x (nivel - 1)` — e este arquivo guardava esse 8 escrito na mao. A
# decisao da v0.70 entrou na v0.145 e ela passou a escalar com Essencia. Numero
# de regra dentro de validador envelhece calado, entao a formula se le do dono:
# o capitulo 15 do livro, vendorizado aqui.
def regra_da_integridade():
    m = re.search(r'fórmula dela é `(\d+) \+ \(Essência \+ (\d+)\) × \(nível − 1\)`',
                  open('capitulo-15-dano-e-condicoes.md', encoding='utf-8').read())
    if not m:
        raise SystemExit('!! nao achei a formula da Integridade no capitulo 15 vendorizado — '
                         'ou ela mudou de forma la, ou o capitulo saiu do lugar')
    return int(m.group(1)), int(m.group(2))

ITG_BASE, ITG_SOMA = regra_da_integridade()

# ---------------------------------------------------------------------------
# AS DIVERGENCIAS DECLARADAS, no molde da checagem 12 do JJK---Project.
#
# A pasta `repos/` e' copia de um TERCEIRO repositorio — o do PDF publicado —,
# e nao do sistema. Entao quando o sistema muda uma regra, aquela ficha fica
# atras ate alguem re-publicar o PDF, e isso nao e' defeito deste repositorio:
# e' atraso de um artefato downstream.
#
# So que "vermelho permanente" nao e' registro: e' um validador que as pessoas
# param de ler, e aí o proximo desvio de verdade entra junto sem ninguem ver.
# Entao a divergencia CONHECIDA fica declarada aqui, com o motivo e a versao —
# ela passa, e reporta. Qualquer OUTRA reprova.
#
# Tirar uma linha daqui e' o conserto: re-vendorize a ficha do repositorio do
# PDF depois que ele for republicado, e a linha sai junto.
DIVERGENCIAS = {
    "Integridade": (
        "a v0.145 do sistema tirou a Integridade PLANA (`20 + 8 x (nivel-1)`) e "
        "pos a Essencia dentro dela. A ficha vendorizada e' de ANTES disso e "
        "imprime o valor plano. A ficha equivalente no JJK---Project ja imprime "
        "o certo, e trocar uma pela outra aqui misturaria as fontes: sao "
        "documentos diferentes (29 paragrafos e 40 tabelas contra 28 e 38)."
    ),
}

KAORI = {"Força":3, "Constituição":2, "Destreza":2, "Inteligência":1, "Essência":1}
CAMINHO, NIVEL, PROTECAO = "Bastião", 2, 1

C = CAT["caminhos"][CAMINHO]
con, des, forca = KAORI["Constituição"], KAORI["Destreza"], KAORI["Força"]
maestria = 1 + NIVEL // 8
CALC = {
    "Vida":          str((C["vida_inicial"] + con) + (C["vida_por_nivel"] + con) * (NIVEL - 1)),
    "Energia":       str(C["pe_por_nivel"] * NIVEL),
    "Integridade":   str(ITG_BASE + (KAORI["Essência"] + ITG_SOMA) * (NIVEL - 1)),
    "Defesa":        str(10 + des + PROTECAO),
    "Iniciativa":    f"d20 + {des}",
    "Deslocamento":  "9 m",
    "Maestria":      str(maestria),
    "CD de feitiço": str(10 + 2 + maestria),
    "Conjuração":    f"d20 + {2 + maestria}",
    "Corpo a corpo": f"d20 + {forca}",
    "À distância":   f"d20 + {des}",
}
# le a tabela de numeros derivados da ficha
IMPRESSO = {}
for t in DOC.tables:
    for r in t.rows:
        cel = [c.text.strip() for c in r.cells]
        for i in (0, 3):
            if len(cel) > i + 2 and cel[i] in CALC:
                IMPRESSO[cel[i]] = cel[i + 2]

print(f"{'campo':16} {'catalogo':>12}   {'ficha .docx':>12}")
falhas, declaradas, resolvidas = 0, [], []
for campo, meu in CALC.items():
    dela = IMPRESSO.get(campo, "<nao achei>")
    ok = meu.replace(" ", "") == dela.replace(" ", "")
    if ok:
        estado = "BATE"
        if campo in DIVERGENCIAS:
            estado = "BATE (a divergencia FECHOU)"
            resolvidas.append(campo)
    elif campo in DIVERGENCIAS:
        estado = "diverge, DECLARADA"
        declaradas.append(campo)
    else:
        estado = "NAO BATE"
        falhas += 1
    print(f"  {campo:16} {meu:>12}   {dela:>12}   {estado}")

for campo in declaradas:
    print(f"\n  ~~ divergencia declarada em `{campo}`:")
    for linha in DIVERGENCIAS[campo].split(". "):
        if linha.strip():
            print(f"     {linha.strip().rstrip('.')}.")

# E o outro lado: uma linha que FECHOU tem de sair da lista, senao a lista vira
# desculpa permanente. E' a mesma forma do `fechada na vX.YYY` do ESTADO-revisao.
for campo in resolvidas:
    print(f"  !! `{campo}` esta na lista de divergencias e os dois lados agora "
          f"BATEM — tire a linha de DIVERGENCIAS, senao ela guarda um desvio "
          f"futuro de graca")
    falhas += 1

# pericias treinadas: as duas fixas do Caminho aparecem marcadas?
marcadas = re.findall(r'■\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wáéíóúâêôãõç ]+)',
                      '\n'.join(c.text for t in DOC.tables for r in t.rows for c in r.cells))
marcadas = [m.strip() for m in marcadas]
print(f"\n  pericias treinadas na ficha: {len(marcadas)}  ({', '.join(marcadas)})")
for fixa in C["pericias_fixas"]:
    achou = any(fixa in m for m in marcadas)
    print(f"  [{'BATE' if achou else 'NAO BATE'}] fixa do {CAMINHO}: {fixa}")

# as Familias que a Kaori marcou existem no manual?
livres = ["Controle", "Castigo"]; fechadas = ["Área", "Auxiliares", "Amparo"]
fantasma = [f for f in livres + fechadas if f not in CAT["familias"]]
print(f"\n  Familias da Kaori: Livres {livres}, Fechadas {fechadas}")
print(f"  [{'OK' if not fantasma else 'PROBLEMA'}] todas existem no manual"
      f"{'' if not fantasma else ': ' + str(fantasma)}")
if falhas:
    print(f"\n{falhas} FALHA(S)")
    raise SystemExit(1)
if declaradas:
    print(f"\nOK — todos os numeros batem, com {len(declaradas)} divergencia(s) "
          f"DECLARADA(S) contra a ficha vendorizada do repositorio do PDF.")
    print("   Elas nao sao defeito deste repositorio; sao atraso daquele artefato.")
else:
    print("\nTODOS OS NUMEROS BATEM")
