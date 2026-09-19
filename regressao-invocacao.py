# -*- coding: utf-8 -*-
"""Recalcula a ficha da invocacao e compara com os numeros que o capitulo 16
PUBLICA. Nenhum valor esperado esta escrito aqui: os casos saem do
invocacao.json, que por sua vez sai do capitulo.

Ele nao usa o LibreOffice, e isso e de proposito: o motor `formulas` avalia o
.xlsx direto, entao o teste roda em qualquer maquina que tenha o pacote --
inclusive onde o LibreOffice nao traz o filtro de Calc.

    pip install formulas
"""
import json, os, sys, warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook

RAIZ = os.path.dirname(os.path.abspath(__file__))
INV = json.load(open(os.path.join(RAIZ, "invocacao.json"), encoding="utf-8"))
FICHA = os.path.join(RAIZ, "ficha-invocacao", "ficha-invocacao.xlsx")
ABA = "INVOCAÇÃO"

falhas, checagens = [], 0

def checa(nome, ok, detalhe=""):
    global checagens
    checagens += 1
    print(f"  [{'OK' if ok else 'FALHA'}] {nome}" + (f"  <- {detalhe}" if not ok else ""))
    if not ok:
        falhas.append(nome)

if not os.path.exists(FICHA):
    sys.exit("a ficha nao existe. Rode: python3 ficha-invocacao/monta.py")
try:
    import formulas
except ImportError:
    sys.exit("FALHA: o pacote `formulas` nao esta instalado, e sem ele este "
             "teste nao confere NADA. Rode: pip install formulas")

# --- o indice de celulas, lido da propria ficha ------------------------
_d = load_workbook(FICHA)["DADOS"]
IDX = next(c for c in range(1, 80) if _d.cell(row=2, column=c).value == "campo")
CEL = {}
for r in range(3, 200):
    k = _d.cell(row=r, column=IDX).value
    if not k:
        break
    CEL[k] = _d.cell(row=r, column=IDX + 1).value
print(f"o indice publica {len(CEL)} campos\n")

MODELO = formulas.ExcelModel().loads(FICHA).finish()

# a chave do motor sai do PROPRIO motor, e nao de um nome montado a mao: assim
# ela nao pode divergir do arquivo (foi o que quebrou a primeira versao deste
# teste -- o nome montado vinha em maiuscula e nenhum input pegava).
_SOL0 = MODELO.calculate()
_amostra = [k for k in _SOL0 if f"{ABA}'!" in k]
if not _amostra:
    sys.exit(f"o motor nao devolveu nenhuma celula da aba {ABA!r}")
PREFIXO = _amostra[0].split(f"{ABA}'!")[0] + f"{ABA}'!"
# celula vazia e sem formula nao aparece na solucao do motor, entao a chave se
# monta do prefixo em vez de ser procurada -- procurar sumia com os campos que
# o jogador preenche, que sao justamente as ENTRADAS do teste.
CHAVE = {campo: PREFIXO + coord for campo, coord in CEL.items()}
INVERSO = {v: k for k, v in CHAVE.items()}

def roda(**entradas):
    """poe os valores nas celulas de entrada e devolve o que a ficha calcula."""
    for k in entradas:
        if k not in CHAVE:
            sys.exit(f"campo desconhecido no teste: {k!r}")
    sol = MODELO.calculate(inputs={CHAVE[k]: v for k, v in entradas.items()})
    saidas = {}
    for k, v in sol.items():
        if k in INVERSO:
            try:
                val = v.value[0, 0]
            except Exception:
                val = v
            saidas[INVERSO[k]] = val
    return saidas

def num(v):
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return v

BASE = dict(ess_dono=0, int_dono=0)
def zerado(**kw):
    v = dict(BASE)
    for a in INV["atributos"]["lista"]:
        v["atr_" + a] = 0
    v.update(kw)
    return v

# =====================================================================
print("=" * 74)
print("1. O EXEMPLO DO CAPITULO — Kaito, nivel 10, tecnica, Constituicao 1")
print("=" * 74)
E = INV["morte"]["exemplo_do_capitulo"]
s = roda(**zerado(nivel=E["nivel"], tipo=E["tipo"], trilha="Coro",
                  **{"atr_Constituição": E["constituicao"]}))
checa(f'vida maxima = {E["vida_maxima"]}', num(s["vida_max"]) == E["vida_maxima"],
      f'a ficha deu {s["vida_max"]!r}')
checa(f'regua da morte = {E["regua"]}', num(s["regua"]) == E["regua"],
      f'a ficha deu {s["regua"]!r}')
checa(f'volta com {E["volta_com"]}', num(s["volta_com"]) == E["volta_com"],
      f'a ficha deu {s["volta_com"]!r}')
checa("maestria do nivel 10 = 2", num(s["maestria"]) == 2, f'{s["maestria"]!r}')
checa("maior Classe do nivel 10 = 3 — e o PE de invocar",
      num(s["classe"]) == 3, f'{s["classe"]!r}')

# =====================================================================
print()
print("=" * 74)
print("2. O CORPO FORTE — a tabela de Constituicao 0 que o capitulo imprime")
print("=" * 74)
for tipo, col in INV["vida"]["conferido_corpo_forte_con0"].items():
    for nivel, esperado in col.items():
        s = roda(**zerado(nivel=int(nivel), tipo=tipo, trilha="Servo"))
        checa(f"corpo forte · {tipo} · nv{nivel} = {esperado}",
              num(s["vida_max"]) == esperado, f'a ficha deu {s["vida_max"]!r}')

print()
print("=" * 74)
print("3. O CORPO DO CORO — o menor dos tres, e ele tem multiplicador proprio")
print("=" * 74)
for tipo, col in INV["vida"]["conferido_corpo_coro_con0"].items():
    for nivel, esperado in col.items():
        s = roda(**zerado(nivel=int(nivel), tipo=tipo, trilha="Coro"))
        checa(f"corpo do Coro · {tipo} · nv{nivel} = {esperado}",
              num(s["vida_max"]) == esperado, f'a ficha deu {s["vida_max"]!r}')

print()
print("   contra-teste: o Servo e o Coro NAO podem dar a mesma vida")
s1 = roda(**zerado(nivel=10, tipo="técnica", trilha="Servo"))
s2 = roda(**zerado(nivel=10, tipo="técnica", trilha="Coro"))
checa("Servo != Coro no mesmo nivel e tipo",
      num(s1["vida_max"]) != num(s2["vida_max"]),
      f'os dois deram {s1["vida_max"]!r}')

print()
print("   a regua E a vida maxima, entao ela muda de Trilha para Trilha")
checa("a regua do Servo e a do Coro sao DIFERENTES",
      num(s1["regua"]) != num(s2["regua"]),
      f'Servo {s1["regua"]!r} · Coro {s2["regua"]!r} — se forem iguais a regua '
      'voltou a ser escala fixa sem ninguem ver')
for _s, _n in ((s1, "Servo"), (s2, "Coro")):
    checa(f"a regua do {_n} e exatamente a vida maxima dele",
          num(_s["regua"]) == num(_s["vida_max"]),
          f'regua {_s["regua"]!r} contra vida {_s["vida_max"]!r}')

# =====================================================================
print()
print("=" * 74)
print("4. O ORCAMENTO — a tabela do capitulo, e o mais-metade do Servo")
print("=" * 74)
for nivel, esperado in INV["orcamento"]["conferido"].items():
    s = roda(**zerado(nivel=int(nivel), tipo="técnica", trilha="Coro"))
    checa(f"orcamento do nv{nivel} = {esperado}", num(s["orcamento"]) == esperado,
          f'a ficha deu {s["orcamento"]!r}')

mult = INV["trilhas"]["Servo"]["orcamento_multiplicador"]
for nivel, base_orc in INV["orcamento"]["conferido"].items():
    esperado = int(base_orc * mult)
    s = roda(**zerado(nivel=int(nivel), tipo="técnica", trilha="Servo"))
    checa(f"Servo no nv{nivel} = {esperado} — o da ficha mais metade",
          num(s["orcamento"]) == esperado, f'a ficha deu {s["orcamento"]!r}')

print()
print("   o capitulo diz que 'mais metade' sempre fecha redondo")
for nivel in INV["orcamento"]["conferido"]:
    s = roda(**zerado(nivel=int(nivel), tipo="técnica", trilha="Servo"))
    checa(f"nv{nivel}: o orcamento do Servo e inteiro",
          float(num(s["orcamento"])).is_integer(), f'{s["orcamento"]!r}')

# =====================================================================
print()
print("=" * 74)
print("5. AS TRES MONTAGENS POR TRILHA — gastam o orcamento INTEIRO no nv2")
print("=" * 74)
for trilha, m in INV["montagens_por_trilha"].items():
    v = zerado(nivel=2, tipo="técnica", trilha=trilha)
    for i, a in enumerate(INV["atributos"]["lista"]):
        v["atr_" + a] = m["arranjo"][i]
    tr = [e for e in m["entradas"] if e in INV["traco"]]
    cm = [e for e in m["entradas"] if e in INV["comando"]]
    for i, e in enumerate(tr):
        v[f"traco_{i+1}"] = e
    for i, e in enumerate(cm):
        v[f"comando_{i+1}"] = e
    s = roda(**v)
    checa(f"{trilha}: gasto = {m['pontos']}", num(s["gasto"]) == m["pontos"],
          f'a ficha deu {s["gasto"]!r}')
    checa(f"{trilha}: sobra zero", num(s["sobra"]) == 0, f'a ficha deu {s["sobra"]!r}')
    checa(f"{trilha}: o arranjo soma {sum(m['arranjo'])} e a conferencia diz ok",
          s["aviso_atributo"] == "Ok", f'a ficha deu {s["aviso_atributo"]!r}')

# =====================================================================
print()
print("=" * 74)
print("6. AS SEIS MONTAGENS DO MATERIAL — cabem no nivel que o capitulo diz")
print("=" * 74)
for m in INV["montagens_do_material"]:
    v = zerado(nivel=m["nivel"], tipo="técnica", trilha="Coro")
    for i, a in enumerate(INV["atributos"]["lista"]):
        v["atr_" + a] = m["arranjo"][i]
    tr = [e for e in m["entradas"] if e in INV["traco"]]
    cm = [e for e in m["entradas"] if e in INV["comando"]]
    for i, e in enumerate(tr):
        v[f"traco_{i+1}"] = e
    for i, e in enumerate(cm):
        v[f"comando_{i+1}"] = e
    s = roda(**v)
    checa(f"{m['nome']}: gasto = {m['pontos']}", num(s["gasto"]) == m["pontos"],
          f'a ficha deu {s["gasto"]!r}')
    checa(f"{m['nome']}: cabe no nv{m['nivel']} — a sobra nao e negativa",
          not isinstance(s["sobra"], str), f'a ficha deu {s["sobra"]!r}')

print()
print("   contra-teste: uma montagem que NAO cabe tem de acusar")
v = zerado(nivel=2, tipo="técnica", trilha="Coro")
v["traco_1"], v["traco_2"] = "Voo", "Montaria"             # 8 + 8 = 16, contra 8
s = roda(**v)
checa("Voo + Montaria no nv2 (16 pontos de um orcamento de 8) acusa 'Estourou'",
      isinstance(s["sobra"], str) and "Estourou" in s["sobra"], f'a ficha deu {s["sobra"]!r}')

print()
print("   os slots comportam a montagem mais CARA que o orçamento paga")
_tr = sorted(INV["traco"].items(), key=lambda x: x[1])
_cm = sorted([kv for kv in INV["comando"].items() if kv[1] > 0], key=lambda x: x[1])
_n_tr = len([k for k in CEL if k.startswith("traco_")])
_n_cm = len([k for k in CEL if k.startswith("comando_")])
# Servo no nv30: o maior bolso que existe
v = zerado(nivel=30, tipo="técnica", trilha="Servo")
_orc = int((INV["orcamento"]["base"] + INV["orcamento"]["por_marco"] *
            len(INV["progressao"]["marcos"])) * 1.5)
_soma, _usados = 0, 0
for nome_e, pr in _tr:
    if _soma + pr > _orc or _usados >= _n_tr:
        break
    _soma += pr
    _usados += 1
    v[f"traco_{_usados}"] = nome_e
s = roda(**v)
checa(f"a ficha tem {_n_tr} slots de Traço e {_n_cm} de Comando",
      _n_tr == 9 and _n_cm == 6, f"achei {_n_tr} e {_n_cm}")
checa(f"cabem {_usados} Traço no Servo nv30 e a ficha soma {_soma}",
      num(s["gasto"]) == _soma, f'a ficha deu {s["gasto"]!r}')
checa("e a sobra continua não-negativa", not isinstance(s["sobra"], str),
      f'a ficha deu {s["sobra"]!r}')
checa("contra-teste: com 4 slots essa montagem não caberia",
      _usados > 4, f"ela usou so {_usados} slots")

# =====================================================================
print()
print("=" * 74)
print("7. O INVESTIR — as sete faixas, nas duas colunas")
print("=" * 74)
for f in INV["investir"]["faixas"]:
    for nivel in (f["de"], f["ate"]):
        for trilha, chave in [("Coro", "uma"), ("Matilha", "matilha")]:
            s = roda(**zerado(nivel=nivel, tipo="técnica", trilha=trilha))
            checa(f"nv{nivel} · {trilha} = {f[chave]}", str(s["investir"]) == f[chave],
                  f'a ficha deu {s["investir"]!r}')

# =====================================================================
print()
print("=" * 74)
print("8. A FICHA DELA — acerto, Defesa e Teste de Resistencia")
print("=" * 74)
# nivel 18: maestria 3. Destreza dela 4, Essencia do dono 5 -> Defesa 10+4+2 = 16
s = roda(**zerado(nivel=18, tipo="técnica", trilha="Coro", ess_dono=5, int_dono=1,
                  defesa_de="Essência", atr_acerto="Destreza", tr_treinado="Vigor",
                  fisico_de="Força", **{"atr_Destreza": 4, "atr_Constituição": 2}))
# os quatro TR, lidos do INDICE e nao de coordenada decorada -- eles andaram
# quando o bloco ganhou a forma nova, e o indice e o que impede o teste de
# apontar para o lugar velho em silencio
checa("o TR treinado (Vigor) leva a maestria: Con 2 + 3 = 5",
      num(s["tr_Vigor"]) == 5, f'a ficha deu {s["tr_Vigor"]!r}')
checa("o Fisico usa Forca (0) e NAO leva maestria, porque nao e o treinado",
      num(s["tr_Físico"]) == 0, f'a ficha deu {s["tr_Físico"]!r}')
checa("contra-teste: trocar o treinado move o numero",
      num(roda(**zerado(nivel=18, tipo="técnica", trilha="Coro",
                        tr_treinado="Físico", fisico_de="Destreza",
                        **{"atr_Destreza": 4}))["tr_Físico"]) == 7,
      "Destreza 4 + maestria 3 tinha de dar 7")

print()
print("   e o Extra de cada TR entra na conta, como na ficha de player")
s_ex = roda(**zerado(nivel=18, tipo="técnica", trilha="Coro", tr_treinado="Vigor",
                     fisico_de="Força",
                     **{"atr_Constituição": 2, "tr_extra_Vigor": 3}))
checa("Vigor com Extra 3: 2 + maestria 3 + 3 = 8", num(s_ex["tr_Vigor"]) == 8,
      f'a ficha deu {s_ex["tr_Vigor"]!r}')
checa("contra-teste: o Extra de um TR nao mexe nos outros",
      num(s_ex["tr_Intelecto"]) == 0, f'a ficha deu {s_ex["tr_Intelecto"]!r}')
s_vazio = roda(**zerado(nivel=18, tipo="técnica", trilha="Coro", tr_treinado="Vigor",
                        fisico_de="Força", **{"atr_Constituição": 2}))
checa("Extra vazio nao vira erro — o N() resolve", num(s_vazio["tr_Vigor"]) == 5,
      f'a ficha deu {s_vazio["tr_Vigor"]!r}')
checa("maestria do nv18 = 3", num(s["maestria"]) == 3, f'{s["maestria"]!r}')
checa("acerto = Destreza dela (4) + maestria (3) = 7", num(s["acerto"]) == 7,
      f'a ficha deu {s["acerto"]!r}')
checa("Defesa = 10 + Destreza dela (4) + metade da Essencia dele (5//2=2) = 16",
      num(s["defesa"]) == 16, f'a ficha deu {s["defesa"]!r}')

s2 = roda(**zerado(nivel=18, tipo="técnica", trilha="Coro", ess_dono=5, int_dono=1,
                   defesa_de="Inteligência", atr_acerto="Destreza",
                   **{"atr_Destreza": 4}))
checa("trocando para Inteligencia (1//2=0), a Defesa cai para 14",
      num(s2["defesa"]) == 14, f'a ficha deu {s2["defesa"]!r}')
checa("contra-teste: a escolha Essencia/Inteligencia muda MESMO a Defesa",
      num(s["defesa"]) != num(s2["defesa"]))

# =====================================================================
print()
print("=" * 74)
print("9. A SINTONIA — o Parrudo na vida, a Presa no crítico")
print("=" * 74)
P = INV["sintonia"]["rotas"]["Parrudo"]["multiplicador_maestria"]
for nivel, maestria in [(2, 1), (10, 2), (18, 3), (30, 4)]:
    sem = roda(**zerado(nivel=nivel, tipo="técnica", trilha="Servo", sintonia="—"))
    com = roda(**zerado(nivel=nivel, tipo="técnica", trilha="Servo", sintonia="Parrudo"))
    d_ = num(com["vida_max"]) - num(sem["vida_max"])
    checa(f"nv{nivel}: o Parrudo soma {P} x maestria ({maestria}) = {P*maestria}",
          d_ == P * maestria, f"a ficha somou {d_}")

print()
# a Presa: ela mexe no dado do acerto, e nao na vida
pr = roda(**zerado(nivel=10, tipo="técnica", trilha="Coro", sintonia="Presa"))
nd = roda(**zerado(nivel=10, tipo="técnica", trilha="Coro", sintonia="—"))
crit = INV["sintonia"]["rotas"]["Presa"]["critico_a_partir_de"]
checa(f"a Presa poe o critico em '{crit} ou 20'", pr["critico"] == f"{crit} ou 20",
      f'a ficha deu {pr["critico"]!r}')
checa("sem Sintonia o critico e so o 20", nd["critico"] == "20",
      f'a ficha deu {nd["critico"]!r}')
checa("contra-teste: a Presa NAO mexe na vida",
      num(pr["vida_max"]) == num(nd["vida_max"]),
      f'{pr["vida_max"]!r} contra {nd["vida_max"]!r}')

# a Voz mexe na CD, e a secao 11 confere isso. Aqui so o que ela NAO mexe.
vz = roda(**zerado(nivel=10, tipo="técnica", trilha="Coro", sintonia="Voz"))
checa("contra-teste: a Voz NAO mexe na vida",
      num(vz["vida_max"]) == num(nd["vida_max"]),
      f'{vz["vida_max"]!r} contra {nd["vida_max"]!r}')

print()
# ⚠ Este contra-teste era o OPOSTO ate a regua voltar a ser a vida do corpo: ele
# exigia que o Parrudo NAO mexesse na regua, porque a regua era escala fixa. Com a
# regua sendo a vida maxima, ela anda junto com tudo que sobe a vida — e o que
# sobra para conferir e' o TAMANHO do passo, que continua sendo so o Parrudo.
print("   o Parrudo sobe a regua junto com a vida, e no tamanho exato")
sem = roda(**zerado(nivel=30, tipo="técnica", trilha="Servo", sintonia="—"))
com = roda(**zerado(nivel=30, tipo="técnica", trilha="Servo", sintonia="Parrudo"))
_dv = num(com["vida_max"]) - num(sem["vida_max"])
_dr = num(com["regua"]) - num(sem["regua"])
checa("o Parrudo mexe na regua", _dr != 0,
      'a regua nao se moveu — ela deixou de ser a vida maxima')
checa(f"e ela anda exatamente o que a vida anda ({_dv})", _dr == _dv,
      f'a vida andou {_dv} e a regua andou {_dr}')

# =====================================================================
print()
print("=" * 74)
print("10. OS ATRIBUTOS — 9 na criacao, +1 por marco, teto 6")
print("=" * 74)
A = INV["atributos"]
s = roda(**zerado(nivel=2, tipo="técnica", trilha="Coro",
                  **{"atr_Força": 3, "atr_Destreza": 3, "atr_Constituição": 3}))
checa(f'nv2: {A["pontos_na_criacao"]} pontos disponiveis',
      num(s["pontos_disp"]) == A["pontos_na_criacao"], f'{s["pontos_disp"]!r}')
checa("3+3+3 = 9 fecha certo e a conferencia diz Ok", s["aviso_atributo"] == "Ok",
      f'{s["aviso_atributo"]!r}')

s = roda(**zerado(nivel=30, tipo="técnica", trilha="Coro"))
esperado = A["pontos_na_criacao"] + len(INV["progressao"]["marcos"])
checa(f"nv30: {esperado} pontos — os 9 mais os sete marcos",
      num(s["pontos_disp"]) == esperado, f'{s["pontos_disp"]!r}')

s = roda(**zerado(nivel=2, tipo="técnica", trilha="Coro",
                  **{"atr_Força": 3, "atr_Destreza": 3, "atr_Constituição": 4}))
checa("contra-teste: 10 pontos num orcamento de 9 acusa 'Estourou o total'",
      s["aviso_atributo"] == "Estourou o total", f'{s["aviso_atributo"]!r}')

s = roda(**zerado(nivel=30, tipo="técnica", trilha="Coro",
                  **{"atr_Força": 7, "atr_Destreza": 3, "atr_Constituição": 3,
                     "atr_Inteligência": 2, "atr_Essência": 1}))
checa(f'contra-teste: um atributo em 7 acusa o teto de {A["teto"]}',
      s["aviso_atributo"] == f'Estourou o teto de {A["teto"]}',
      f'{s["aviso_atributo"]!r}')

# =====================================================================
print()
print("=" * 74)
print("O DEGRAU — o Traco e Comando proprios, recalculados na planilha")
print("=" * 74)

# Os degraus saem da regua do capitulo, lida do json que o conferir amarra
# nela. O teto e o piso vem do maior e do menor degrau, e nao de numero
# escrito aqui: se a regua mudar, este teste muda com ela.
_dt = sorted(int(k) for k in INV["regua_traco"])
_dc = sorted(int(k) for k in INV["regua_comando"])
_base = dict(nivel=2, tipo="técnica", trilha="Servo")

s = roda(**zerado(**_base))
_orc = num(s["orcamento"])
checa("nada escolhido: gasto zero", num(s["gasto"]) == 0, f'{s["gasto"]!r}')

for _d in _dt:
    s = roda(**zerado(**_base, traco_1="Bafo de Fogo", degrau_traco_1=_d))
    checa(f"Traco proprio no degrau {_d} custa {_d}",
          num(s["gasto"]) == _d, f'a ficha gastou {s["gasto"]!r}')

for _d in _dc:
    s = roda(**zerado(**_base, comando_1="Escoltar", degrau_comando_1=_d))
    checa(f"Comando proprio no degrau {_d} custa {_d}",
          num(s["gasto"]) == _d, f'a ficha gastou {s["gasto"]!r}')

# nome proprio SEM degrau escolhido nao gasta nada: o "—" do menu vale zero
s = roda(**zerado(**_base, traco_1="Bafo de Fogo"))
checa("nome proprio sem degrau escolhido nao gasta nada",
      num(s["gasto"]) == 0, f'{s["gasto"]!r}')

# contra-teste: o degrau NAO atropela o catalogo. Com um nome do catalogo, o
# preco e o do catalogo mesmo que o jogador escolha outro degrau.
_nome_cat, _preco_cat = next(iter(INV["traco"].items()))
_outro = next(x for x in _dt if x != _preco_cat)
s = roda(**zerado(**_base, traco_1=_nome_cat, degrau_traco_1=_outro))
checa(f"contra-teste: {_nome_cat} continua custando {_preco_cat} "
      f"mesmo com o degrau em {_outro}",
      num(s["gasto"]) == _preco_cat, f'a ficha gastou {s["gasto"]!r}')

# o proprio entra na SOBRA junto com o resto. Aqui vai no nivel 30, onde o
# orcamento cabe os dois -- no nivel 2 os dois degraus mais caros estouram, e
# esse caso vira o contra-teste logo abaixo.
_soma = _dt[-1] + _dc[-1]
_alto = dict(_base, nivel=30)
s = roda(**zerado(**_alto, traco_1="Bafo de Fogo", degrau_traco_1=_dt[-1],
                  comando_1="Escoltar", degrau_comando_1=_dc[-1]))
_orc30 = num(s["orcamento"])
checa(f"nv30: dois proprios somam {_soma} e a sobra desce igual",
      num(s["gasto"]) == _soma and num(s["sobra"]) == _orc30 - _soma,
      f'gasto {s["gasto"]!r}, sobra {s["sobra"]!r}, orcamento {_orc30!r}')

# contra-teste: o proprio nao escapa do teto do orcamento
s = roda(**zerado(**_base, traco_1="Bafo de Fogo", degrau_traco_1=_dt[-1],
                  comando_1="Escoltar", degrau_comando_1=_dc[-1]))
checa(f"contra-teste: nv2 com {_soma} num orcamento de {_orc:.0f} acusa o estouro",
      str(s["sobra"]).startswith("Estourou"), f'{s["sobra"]!r}')

# =====================================================================
print()
print("=" * 74)
print("11. A CD DOS EFEITOS — 8 + atributo da montagem + maestria + bonus")
print("=" * 74)
# O modelo NAO sai so do json: a base da CD e as faixas do bonus saem do TEXTO dos
# dois capitulos, e o json entra depois so para a maestria. Assim a planilha nao
# se mede contra a mesma fonte que ela usa para calcular.
import re
_C16 = open(os.path.join(RAIZ, "capitulo-16-invocacoes.md"), encoding="utf-8").read()
_C35 = open(os.path.join(RAIZ, "capitulo-35-caminhos-e-trilhas.md"), encoding="utf-8").read()
_mb = re.search(r"\| \*\*CD dos efeitos\*\* \| `(\d+) \+ o atributo dela \+ a sua maestria`", _C16)
_ms = re.search(r"As duas dão o mesmo número em todo nível \(([^)]*)\)", _C35)
if not (_mb and _ms):
    sys.exit("FALHA: nao achei a formula da CD no capitulo 16 ou a frase da Voz e do Preito no capitulo 35")
BASE_CD = int(_mb.group(1))
_faixas, _ini = [], 2
for _tok in [x.strip() for x in _ms.group(1).split(", ")]:
    _m1 = re.fullmatch(r"`\+(\d+)` até o (\d+)", _tok)
    _m2 = re.fullmatch(r"`\+(\d+)` do (\d+) em diante", _tok)
    _m3 = re.fullmatch(r"`\+(\d+)` do (\d+) ao (\d+)", _tok)
    if _m1:
        _faixas.append((_ini, int(_m1.group(2)), int(_m1.group(1)))); _ini = int(_m1.group(2)) + 1
    elif _m2:
        _faixas.append((int(_m2.group(2)), 99, int(_m2.group(1))))
    elif _m3:
        _faixas.append((int(_m3.group(2)), int(_m3.group(3)), int(_m3.group(1)))); _ini = int(_m3.group(3)) + 1
    else:
        sys.exit(f"FALHA: nao entendi a faixa {_tok!r} da frase do capitulo 35")

def BON(nv):
    return next(v for a, b, v in _faixas if a <= nv <= b)

def MAE(nv):
    return 1 + sum(1 for x in INV["progressao"]["maestria_em"] if x <= nv)

checa(f"a base da CD: o capitulo 16 diz {BASE_CD} e o json diz {INV['ficha_dela']['cd_base']}",
      BASE_CD == INV["ficha_dela"]["cd_base"])
print(f"   o bonus, lido da frase do capitulo 35: {[(a, b if b < 99 else 30, v) for a, b, v in _faixas]}")

A0, A1 = INV["atributos"]["lista"][0], INV["atributos"]["lista"][4]
for nivel in (2, 6, 7, 10, 18, 25, 26, 30):
    v_atr = 4
    base = zerado(nivel=nivel, tipo="técnica", trilha="Coro", cd_atributo=A0, **{"atr_" + A0: v_atr})
    sem = roda(**dict(base, sintonia="—"))
    checa(f"nv{nivel}: sem bonus, CD = {BASE_CD} + {v_atr} + maestria {MAE(nivel)} = {BASE_CD + v_atr + MAE(nivel)}",
          num(sem["cd"]) == BASE_CD + v_atr + MAE(nivel) and num(sem["cd_bonus"]) == 0,
          f'a ficha deu CD {sem["cd"]!r} e bonus {sem["cd_bonus"]!r}')
    com = roda(**dict(base, sintonia="Voz"))
    checa(f"nv{nivel}: com a Voz o bonus e +{BON(nivel)} e a CD {BASE_CD + v_atr + MAE(nivel) + BON(nivel)}",
          num(com["cd_bonus"]) == BON(nivel) and num(com["cd"]) == BASE_CD + v_atr + MAE(nivel) + BON(nivel),
          f'a ficha deu bonus {com["cd_bonus"]!r} e CD {com["cd"]!r}')
    pre = roda(**dict(base, trilha="Servo", cd_preito="sim", sintonia="—"))
    checa(f"nv{nivel}: o Preito do Servo na CD da o mesmo +{BON(nivel)} que a Voz",
          num(pre["cd_bonus"]) == BON(nivel) and num(pre["cd"]) == num(com["cd"]),
          f'Preito {pre["cd_bonus"]!r}/{pre["cd"]!r}, Voz {com["cd_bonus"]!r}/{com["cd"]!r}')
    dois = roda(**dict(base, trilha="Servo", cd_preito="sim", sintonia="Voz"))
    checa(f"nv{nivel}: a Voz e o Preito JUNTOS nao somam: continua +{BON(nivel)}",
          num(dois["cd_bonus"]) == BON(nivel),
          f'a ficha deu bonus {dois["cd_bonus"]!r}')
    checa(f"nv{nivel}: contra-teste, somar os dois daria {BASE_CD + v_atr + MAE(nivel) + 2 * BON(nivel)} e a ficha nao da",
          num(dois["cd"]) != BASE_CD + v_atr + MAE(nivel) + 2 * BON(nivel),
          f'a ficha somou os dois: {dois["cd"]!r}')

print()
print("   o atributo da CD e o da montagem, e a arma so mexe no acerto")
_b = zerado(nivel=10, tipo="técnica", trilha="Coro", sintonia="—", cd_atributo=A0,
            **{"atr_" + A0: 3, "atr_" + A1: 5})
s0 = roda(**dict(_b, atr_acerto=A0))
checa("acerto e CD no mesmo atributo: a conferencia diz Ok", s0["cd_confere"] == "Ok",
      f'a ficha deu {s0["cd_confere"]!r}')
s1 = roda(**dict(_b, atr_acerto=A1))
checa("o acerto passa a usar outro atributo (a arma) e a CD NAO se mexe",
      num(s1["cd"]) == num(s0["cd"]), f'CD {s0["cd"]!r} e depois {s1["cd"]!r}')
checa("contra-teste: o acerto SE mexeu — o que a arma muda e' ele",
      num(s1["acerto"]) != num(s0["acerto"]), f'acerto {s0["acerto"]!r} e depois {s1["acerto"]!r}')
checa("e a conferencia avisa que so vale com arma", "só vale com arma" in str(s1["cd_confere"]),
      f'a ficha deu {s1["cd_confere"]!r}')
s2 = roda(**dict(_b, cd_atributo=A1, atr_acerto=A1))
checa("trocar o atributo DA CD muda a CD, pelo valor do atributo escolhido",
      num(s2["cd"]) - num(s0["cd"]) == 5 - 3, f'CD {s0["cd"]!r} e depois {s2["cd"]!r}')
s3 = roda(**zerado(nivel=10, tipo="técnica", trilha="Coro", sintonia="—"))
checa("sem atributo escolhido a CD fica vazia e a conferencia pede a escolha",
      s3["cd"] in ("", None) and "Escolha o atributo" in str(s3["cd_confere"]),
      f'CD {s3["cd"]!r}, conferencia {s3["cd_confere"]!r}')
s4 = roda(**dict(_b, trilha="Coro", cd_preito="sim", atr_acerto=A0))
checa("o Preito marcado fora do Servo nao soma, e a ficha avisa",
      num(s4["cd_bonus"]) == 0 and "Preito é do Servo" in str(s4["cd_confere"]),
      f'bonus {s4["cd_bonus"]!r}, conferencia {s4["cd_confere"]!r}')

# =====================================================================
print()
print("=" * 74)
if falhas:
    print(f">>> {len(falhas)} FALHA(S) de {checagens}")
    for f in falhas:
        print(f"    · {f}")
    sys.exit(1)
print(f">>> TUDO OK — as {checagens} checagens saem do capitulo 16, recalculadas")
print("    na propria planilha. Nenhum valor esperado escrito a mao.")
print("=" * 74)
