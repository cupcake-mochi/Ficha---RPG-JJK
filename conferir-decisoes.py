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
import json, os, re, sys, math

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
      "ignora vida temporária e barreiras" in MAN,
      "sem essa frase, 'gasta primeiro' vira invencao")
# v0.239 do sistema: o capitulo "Vida, energia e alma" ganhou as duas regras, e a da energia
# saiu de dentro do Braseiro. Decisao do Mizuki: toda fonte temporaria nao acumula, e o teto e
# metade do maximo. A A2 desta pasta segue o capitulo, e o manual-temporario.md ficou superado.
checa("o capitulo tem a regra da vida temporaria, com teto de metade da vida maxima",
      "Vida temporária é anteparo, e não vida" in MAN and "teto de metade da sua vida máxima" in MAN)
checa("o capitulo tem a regra da energia temporaria, com teto de metade do PE maximo",
      "Energia temporária segue a regra da vida temporária" in MAN and
      "teto de metade do seu PE máximo" in MAN)
A2 = DEC["A2_temporario"]
checa("a A2 segue o capitulo: nenhuma temporaria acumula",
      A2["vida"].get("empilha") is False and A2["energia"].get("empilha") is False)
checa("a A2 segue o capitulo: o teto e metade do maximo, nas duas",
      A2["vida"].get("teto") == "metade da vida máxima" and
      A2["energia"].get("teto") == "metade do PE máximo",
      f'vida: {A2["vida"].get("teto")!r} · energia: {A2["energia"].get("teto")!r}')

def no_manual(nome):
    """O pdftotext -layout parte a celula de tabela em duas linhas, e a coluna do lado entra
    no meio do nome ("Vento a ... Favor"): as palavras tem de aparecer em ordem, e perto."""
    rx = r"\b" + r"\b(?:\s+\S+){0,15}?\s+\b".join(re.escape(p) for p in nome.split()) + r"\b"
    return re.search(rx, MAN) is not None

for reserva in ("vida", "energia"):
    fontes = A2[reserva]["fontes_no_manual"]
    faltando = [f for f in fontes if not no_manual(f)]
    checa(f"as {len(fontes)} fontes de {reserva} temporaria existem no manual",
          bool(fontes) and not faltando, str(faltando))
checa("o manual-temporario.md se declara superado pelo capitulo",
      "SUPERADO" in le("manual-temporario.md")[:900],
      "o texto proposto ja entrou no manual; sem o aviso ele parece pendente")

for par in DEC["A3_incompatibilidades"]["pares"]:
    existe = (par["a"] in CAT["melhorias"] or par["a"] in CAT["restricoes"]) and \
             (par["b"] in CAT["melhorias"] or par["b"] in CAT["restricoes"])
    checa(f"o par {par['a']} + {par['b']} nomeia pecas que existem", existe)
    if par["fonte"] == "manual":
        # v0.246 do sistema: o veto das Restricoes vem depois do das Melhorias, na mesma
        # frase ("...que Reação nem com a Restrição Atrasar ."). A busca fica presa na linha
        # da Melhoria `a` da tabela Tempo, para o veto do `Rápido` nao valer pela `Reação`.
        _linha = re.search(r"\b" + re.escape(par["a"]) + r"\s+(?:Leve|Média|Pesada)\s+(.{0,400}?)"
                           r"(?=\s\S+\s+(?:Leve|Média|Pesada)\s|$)", MAN)
        _frase = _linha and re.search(r"Não entra no mesmo feitiço que(?:\s+\S+){0,14}?\s+"
                                      + re.escape(par["b"]) + r"\b", _linha.group(1))
        checa(f"  ...e o manual escreve mesmo esse par, na linha do {par['a']}", bool(_frase),
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

# ---------------------------------------------------------------- 4
print("\nO BLOCO C  (as quatro que sairam do 'falta algo antes de construir')")

# C1: o Evocador some do MENU, nunca do catalogo. O catalogo espelha o manual.
c1 = DEC["C1_evocador"]
checa("o catalogo continua com os cinco Caminhos do manual",
      len(CAT["caminhos"]) == 5, f"achei {len(CAT['caminhos'])}")
# 14/09/2026: o Evocador VOLTOU ao menu, e o Mizuki confirmou no B18. O caminho oculto
# pode ser nulo, e as duas formas continuam amarradas ao catalogo.
_oculto = [c1["caminho_oculto"]] if c1.get("caminho_oculto") else []
checa("o caminho oculto, se existe, continua no catalogo (some so do menu)",
      all(c in CAT["caminhos"] for c in _oculto), str(_oculto))
checa("todo Caminho do menu da ficha existe no catalogo",
      all(c in CAT["caminhos"] for c in c1["caminhos_no_menu"]),
      str([c for c in c1["caminhos_no_menu"] if c not in CAT["caminhos"]]))
checa("menu + oculto = o catalogo inteiro, sem sobra nem falta",
      set(c1["caminhos_no_menu"]) | set(_oculto) == set(CAT["caminhos"])
      and not (set(c1["caminhos_no_menu"]) & set(_oculto)))
# ------------------------------------------------------------------------
# C1: o motivo da decisao tem de estar em dia com a realidade.
#
# A versao ANTIGA desta checagem lia o manual.txt procurando a frase
# 'Casco - as suas invocacoes tem mais vida.' e passava enquanto ela estivesse
# la. Como o manual.txt deste repositorio esta congelado na v0.104, a frase
# nunca sai -- entao ela saia VERDE para sempre e nunca podia acender. Um
# guarda que nao pode mudar de estado nao guarda nada.
#
# Hoje ela le o dono VIVO daquele numero: o capitulo 35 vendorizado. Se o
# Parrudo (ex-Casco) tem numero la, o motivo do C1 caiu, e a decisao tem de
# DECLARAR que caiu -- em vez de continuar escrita como se ainda valesse.
if not os.path.exists("capitulo-35-caminhos-e-trilhas.md"):
    print("\nFALTA O ARQUIVO 'capitulo-35-caminhos-e-trilhas.md', e ele e o dono")
    print("  vivo do numero do Parrudo. Sem ele a checagem do C1 nao confere nada.")
    print("  copie de: <clone do JJK---Project>/sistema/05-material/livro/manual/")
    print("            35-caminhos-e-trilhas.md")
    sys.exit(1)
CAP35 = ' '.join(le('capitulo-35-caminhos-e-trilhas.md').split())
m_par = re.search(r"\*\*`Parrudo`\*\*[^|]*?`(\d+) ×` a sua maestria", CAP35)
checa("o capitulo 35 da um numero ao Parrudo, o ex-Casco",
      m_par is not None,
      "se o Parrudo perdeu o numero, o motivo do C1 voltou a valer e este bloco "
      "todo precisa ser relido")
# v0.239 do sistema: o manual.txt foi reextraido e passou a ter o numero do Parrudo. A
# checagem que guardava a DIVERGENCIA acendeu, como devia, e virou a da CONCORDANCIA: o
# capitulo vendorizado continua dono, e o manual.txt tem de dizer o mesmo.
m_man = re.search(r"Parrudo — as suas invocações têm mais vida, equivalente a (\d+) × a sua maestria", MAN)
checa("o manual.txt reextraido da ao Parrudo o mesmo numero do capitulo 35",
      m_par is not None and m_man is not None and m_man.group(1) == m_par.group(1),
      f"capitulo: {m_par.group(1) if m_par else None} · manual.txt: {m_man.group(1) if m_man else None}")
mh = c1.get("motivo_hoje", {})
PRECISA_MH = {"estado", "entregas_de_trilha", "numero_do_casco",
              "ficha_da_invocacao"}
faltando_mh = sorted(PRECISA_MH - set(mh))
checa("o C1 declara o estado de hoje dos tres motivos dele",
      not faltando_mh, "falta declarar: " + str(faltando_mh))
if m_par:
    checa("o numero que o C1 declara e o mesmo do capitulo 35",
          m_par.group(1) + " x a maestria" in mh.get("numero_do_casco", ""),
          "o capitulo diz " + m_par.group(1) + ", o C1 diz "
          + repr(mh.get("numero_do_casco", "")))
checa("o C1 registra que a decisao de voltar ao menu e do Mizuki",
      "Mizuki" in mh.get("estado", ""))
checa("o C1 aponta a ficha da invocacao como fechada",
      "ficha-invocacao" in mh.get("ficha_da_invocacao", ""))
checa("o C1 explica por que a checagem velha nao servia",
      "congelado" in mh.get("por_que_a_checagem_velha_nao_servia", ""))

# C2: o carimbo e a versao do projeto, e o dono dela e o CHANGELOG.
c2 = DEC["C2_carimbo"]
checa("a versao do carimbo tem forma de versao do projeto",
      c2["versao_corrente"].count(".") == 1 and
      all(p.isdigit() for p in c2["versao_corrente"].split(".")))
checa("o catalogo carrega a versao que a ficha carimba",
      CAT["_meta"].get("versao") == c2["versao_corrente"],
      f"_meta.versao = {CAT['_meta'].get('versao')!r}, carimbo = {c2['versao_corrente']!r}")

# C3: a Defesa nao pode ter numero de protecao escrito na mao.
c3 = DEC["C3_defesa"]
checa("a formula da Defesa nao tem constante de protecao embutida",
      "+ protecao" in c3["formula_defesa"] and
      not any(f"+ {n}" in c3["formula_defesa"] for n in "0123456789"),
      c3["formula_defesa"])
checa("a protecao da aptidao sai do refino, e nao de um numero fixo",
      "refino" in c3["formula_protecao"])
checa("o manual continua dizendo que o equipamento desliga a aptidao",
      "Traje" in MAN and "Revestimento" in MAN)

# C4: a MESA e o unico lugar onde a fonte nao pode ser escolha livre.
c4 = DEC["C4_fontes"]
SEGURAS = {"Arial", "Comic Sans MS", "Courier New", "Georgia", "Roboto", "Verdana"}
checa("a fonte de corpo esta na lista que o Sheets carrega sem 'mais fontes'",
      c4["corpo"]["fonte"] in SEGURAS,
      f"{c4['corpo']['fonte']} nao esta em {sorted(SEGURAS)}; o app de celular trocaria")
checa("a regra da MESA nomeia a mesma fonte do corpo",
      c4["corpo"]["fonte"] in c4["regra_dura"])
med = c4["medido"]
checa("a fonte de corpo escolhida cabe na linha de 336 px da MESA",
      med["linha_de_feitico_da_MESA_em_336px"][c4["corpo"]["fonte"]] <= 336)
checa("a fonte de titulo e mais estreita que a de corpo, que e o motivo dela",
      med["linha_de_feitico_da_MESA_em_336px"][c4["titulo"]["fonte"]] <
      med["linha_de_feitico_da_MESA_em_336px"][c4["corpo"]["fonte"]])
checa("nenhuma fonte escolhida e display caixa-alta",
      all(med["x_sobre_maiuscula"][c4[p]["fonte"].replace(" ", "")] <= 0.90
          for p in ("corpo", "titulo")),
      "x/maiuscula acima de 0.90 cansa em bloco de texto")

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
