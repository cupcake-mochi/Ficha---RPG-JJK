# -*- coding: utf-8 -*-
"""Monta a ficha da invocacao do Projeto M em .xlsx.

Planilha SEPARADA, por escolha do Mizuki: o que a ficha do personagem sabe
(nivel, Essencia, Inteligencia) entra aqui como celula que o jogador digita.
No dia em que ela virar aba da ficha grande, essas tres celulas viram formula
apontando para a FICHA e nada mais muda.

O DESENHO e o da ficha de player, e nao um proprio: as tres faixas -- rotulo
claro, poco escuro, legenda -- estao no gramatica.py, medidas da Ficha
(PROJETO M) 0.1. A primeira versao desta ficha usava a `regua` do estilo.py, e
o Mizuki pediu que ela ficasse tao legivel quanto a que a mesa ja usa.

Nenhum numero esta escrito aqui: tudo vem do invocacao.json, cujo dono
declarado sao os capitulos 16 e 35 do Manual da Guilda.
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "ficha"))
sys.path.insert(0, AQUI)

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
from estilo import (CORPO, TITULO, DOCUMENTO, SERIE, PT_ROTULO, PT_VALOR,
                    LARG_COL, ALT_LIN, FUNDO, PAINEL, PAINEL_ALTO, FAIXA,
                    PAINEL_BAIXO, LINHA, BLOCO, TEXTO_FRACO, TEXTO, TINTA,
                    OSSO, AMBAR, VERMELHO, txt, regua, pinta, junta, base,
                    lombada, barra, cor_de_estado)
import gramatica as G
from gramatica import COLS, GRADE_7, GRADE_10, LARG_7, LARG_10

INV = json.load(open(os.path.join(RAIZ, "invocacao.json"), encoding="utf-8"))

wb = Workbook()
wb.remove(wb.active)
wb._fonts[0] = Font(name=CORPO, size=PT_VALOR, color=TEXTO)

# ====================================================================== DADOS
d = wb.create_sheet("DADOS")
d.sheet_state = "hidden"
REF = {}

def lista(c, titulo, itens, larg=22):
    d.column_dimensions[L(c)].width = larg
    txt(d, c, 1, titulo, nome=TITULO, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for i, v in enumerate(itens):
        txt(d, c, 2 + i, v)
    REF[titulo] = f"DADOS!${L(c)}$2:${L(c)}${1+len(itens)}"

lista(1, "tipos",     list(INV["tipos"]))
lista(2, "trilhas",   list(INV["trilhas"]))
lista(3, "atributos", list(INV["atributos"]["lista"]))
lista(4, "trs",       list(INV["testes_de_resistencia"]))
lista(5, "sintonia",  ["—"] + list(INV["sintonia"]["rotas"]))
lista(6, "defesa_de", INV["ficha_dela"]["defesa_escolha"])
lista(7, "fisico_de", INV["testes_de_resistencia"]["Físico"])
lista(8, "traco",     ["—"] + list(INV["traco"]))
lista(9, "comando",   ["—"] + list(INV["comando"]))

def tabela(c, titulo, cabec, linhas, larg=16):
    txt(d, c, 1, titulo, nome=TITULO, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for j, h in enumerate(cabec):
        d.column_dimensions[L(c + j)].width = larg
        txt(d, c + j, 2, h, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for i, lin in enumerate(linhas):
        for j, v in enumerate(lin):
            txt(d, c + j, 3 + i, v)
    REF[titulo] = f"DADOS!${L(c)}$3:${L(c+len(cabec)-1)}${2+len(linhas)}"
    return c + len(cabec) + 1

c = 11
c = tabela(c, "tab_tipos", ["tipo", "base"], [[k, v] for k, v in INV["tipos"].items()])
c = tabela(c, "tab_trilhas", ["trilha", "corpos", "mult", "corpo", "area"],
           [[k, v["corpos"], v["orcamento_multiplicador"], v["corpo"],
             v["vulneravel_a_area"]] for k, v in INV["trilhas"].items()])
c = tabela(c, "tab_traco", ["traço", "pontos"],
           [["—", 0]] + [[k, v] for k, v in INV["traco"].items()])
c = tabela(c, "tab_comando", ["comando", "pontos"],
           [["—", 0]] + [[k, v] for k, v in INV["comando"].items()])
c = tabela(c, "tab_investir", ["de", "uma", "matilha"],
           [[f["de"], f["uma"], f["matilha"]] for f in INV["investir"]["faixas"]])
c = tabela(c, "tab_trs", ["tr", "atributo"],
           [[t, a[0]] for t, a in INV["testes_de_resistencia"].items()])

P = INV["progressao"]
for nome_e, valores in [("e_marcos", P["marcos"]), ("e_maestria", P["maestria_em"]),
                        ("e_classe", P["classe_em"])]:
    d.column_dimensions[L(c)].width = 10
    txt(d, c, 2, nome_e, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for i, v in enumerate(valores):
        txt(d, c, 3 + i, v)
    REF[nome_e] = f"DADOS!${L(c)}$3:${L(c)}${2+len(valores)}"
    c += 1

ESPELHO = c + 1
REF["espelho"] = f"DADOS!${L(ESPELHO)}$3:${L(ESPELHO)}$7"
pinta(d, 1, 1, c + 3, 30, FUNDO)

# ================================================================= INVOCAÇÃO
ws = base(wb, "INVOCAÇÃO", COLS, 120)
R = {}

def dv(formula, c1, r1, c2=None, r2=None):
    v = DataValidation(type="list", formula1=formula, allow_blank=True,
                       showDropDown=False)
    ws.add_data_validation(v)
    v.add(f"{L(c1)}{r1}:{L(c2 or c1)}{r2 or r1}")

def cel(c, r):
    return f"${L(c)}${r}"

lombada(ws, 120, "INVOCAÇÃO", "PROJETO - M")
pinta(ws, 3, 1, COLS, 2, PAINEL_ALTO)
txt(ws, 4, 1, "A FICHA DA INVOCAÇÃO", nome=TITULO, pt=18, cor=OSSO, ate=(30, 2))
txt(ws, 32, 1, "capítulo 16 · Projeto - M",
    nome=SERIE, pt=8, cor=TEXTO_FRACO, al="right", ate=(COLS, 2))

# ------------------------------------------------------------- 01 O DONO
r = G.secao(ws, 4, "1", "O DONO", ate=28)
R["nivel"]    = G.campo(ws, GRADE_10[0], r, LARG_10, "nível do dono", 2, pt=G.PT_GRANDE, alto=2)
R["ess_dono"] = G.campo(ws, GRADE_10[1], r, LARG_10, "essência do dono", 0, pt=G.PT_GRANDE, alto=2)
R["int_dono"] = G.campo(ws, GRADE_10[2], r, LARG_10, "inteligência do dono", 0, pt=G.PT_GRANDE, alto=2)
NIV, ESS, INT = cel(GRADE_10[0], r+1), cel(GRADE_10[1], r+1), cel(GRADE_10[2], r+1)

MAE = f'(1+COUNTIF({REF["e_maestria"]},"<="&{NIV}))'
MAR = f'COUNTIF({REF["e_marcos"]},"<="&{NIV})'
CLA = f'COUNTIF({REF["e_classe"]},"<="&{NIV})'
R["maestria"] = G.campo(ws, GRADE_10[3], r, LARG_10, "maestria", f"={MAE}", alto=2)
MAEC = cel(GRADE_10[3], r+1)
r += 4
R["marcos"] = G.campo(ws, GRADE_10[0], r, LARG_10, "marcos", f"={MAR}")
R["classe"] = G.campo(ws, GRADE_10[1], r, LARG_10, "maior classe", f"={CLA}")
MARC, CLAC = cel(GRADE_10[0], r+1), cel(GRADE_10[1], r+1)
r = G.nota(ws, r + 3, "Copie estes três da sua ficha. O resto desta seção a "
           "planilha calcula.")

# -------------------------------------------------------- 02 A INVOCAÇÃO
r = G.secao(ws, r + 1, "2", "A INVOCAÇÃO", ate=24)
R["nome"]     = G.campo(ws, 4, r, 20, "nome", None, pt=18, nome=DOCUMENTO)
R["tipo"]     = G.campo(ws, 26, r, LARG_10, "tipo", None, pt=12, nome=CORPO)
R["trilha"]   = G.campo(ws, 37, r, LARG_10, "trilha", None, pt=12, nome=CORPO)
dv(REF["tipos"], 26, r + 1)
dv(REF["trilhas"], 37, r + 1)
TIPO, TRI = cel(26, r + 1), cel(37, r + 1)
r += 3
R["sintonia"] = G.campo(ws, 4, r, LARG_10, "sintonia", "—", pt=12, nome=CORPO)
dv(REF["sintonia"], 4, r + 1)
SIN = cel(4, r + 1)
txt(ws, 15, r, "O QUE A TRILHA DECIDE", nome=TITULO, pt=G.PT_ROT, cor=BLOCO,
    ate=(COLS, r))
txt(ws, 15, r + 1, "quantos corpos você põe em campo, quanta vida cada um tem, e o "
    "tamanho do orçamento", nome=CORPO, pt=G.PT_NOTA, cor=TEXTO, ate=(COLS, r + 2))
r = G.nota(ws, r + 3, "A Sintonia é a escolha de nível 2 do Evocador. "
           "Presa: crítico com 19 ou 20. Parrudo: mais vida, 5 × a sua maestria. "
           "Voz: sobe a CD dos efeitos dela — veja a seção 9.")

# ---------------------------------------------------- 03 OS ATRIBUTOS DELA
A = INV["atributos"]
r = G.secao(ws, r + 1, "3", "OS ATRIBUTOS DELA", ate=32)
ATR = {}
for i, a in enumerate(A["lista"]):
    ATR[a] = G.campo(ws, GRADE_7[i], r, LARG_7, a[:3], 0, pt=G.PT_ATR,
                     legenda=a, alto=2)
CELS = [cel(GRADE_7[i], r + 1) for i in range(5)]
GASTO_A = "+".join(CELS)
DISP_A = f'({A["pontos_na_criacao"]}+{MARC})'
r += 5
R["pontos_atributo"] = G.campo(ws, GRADE_10[0], r, LARG_10, "pontos gastos", f"={GASTO_A}", pt=12)
R["pontos_disp"]     = G.campo(ws, GRADE_10[1], r, LARG_10, "disponíveis", f"={DISP_A}", pt=12)
aviso_f = (f'=IF({GASTO_A}>{DISP_A},"estourou o total",'
           f'IF(MAX({",".join(CELS)})>{A["teto"]},"estourou o teto de {A["teto"]}",'
           f'IF({GASTO_A}<{DISP_A},"sobrou ponto","ok")))')
R["aviso_atributo"] = G.campo(ws, GRADE_10[2], r, LARG_10 + 11, "conferência",
                              aviso_f, pt=12, cor=AMBAR)
r = G.nota(ws, r + 3, f'Distribua {A["pontos_na_criacao"]} pontos, nenhum acima '
           f'de {A["teto_na_criacao"]}. A cada marco ela ganha {A["por_marco"]} ponto, '
           f'até o teto de {A["teto"]}. É a mesma regra da sua ficha.')

for i, a in enumerate(A["lista"]):
    txt(d, ESPELHO, 3 + i, f"=INVOCAÇÃO!{CELS[i]}")
d.column_dimensions[L(ESPELHO)].width = 10
txt(d, ESPELHO, 2, "espelho", pt=PT_ROTULO, cor=TEXTO_FRACO)
ESP, NOMES_A = REF["espelho"], REF["atributos"]

def valor_de(escolha):
    return f"INDEX({ESP},MATCH({escolha},{NOMES_A},0))"

# --------------------------------------------------- 04 O QUE ENCARA O DADO
r = G.secao(ws, r + 1, "4", "ACERTO, DEFESA E TESTES DE RESISTÊNCIA", ate=34)
R["atr_acerto"] = G.campo(ws, GRADE_10[0], r, LARG_10, "atributo do acerto", None,
                          pt=11, nome=CORPO)
dv(NOMES_A, GRADE_10[0], r + 1)
ACE = cel(GRADE_10[0], r + 1)
R["acerto"] = G.campo(ws, GRADE_10[1], r, LARG_10, "acerto",
                      f'=IF({ACE}="","",{valor_de(ACE)}+{MAEC})')
R["defesa_de"] = G.campo(ws, GRADE_10[2], r, LARG_10, "defesa usa, do dono", None,
                         pt=11, nome=CORPO)
dv(REF["defesa_de"], GRADE_10[2], r + 1)
DEFDE = cel(GRADE_10[2], r + 1)
R["defesa"] = G.campo(ws, GRADE_10[3], r, LARG_10, "defesa",
    f'=10+{CELS[1]}+FLOOR(IF({DEFDE}="{A["lista"][4]}",{ESS},{INT})/2,1)')
r += 3
_presa = INV["sintonia"]["rotas"]["Presa"]["critico_a_partir_de"]
R["critico"] = G.campo(ws, GRADE_10[0], r, LARG_10, "crítico com",
                       f'=IF({SIN}="Presa","{_presa} ou 20","20")', pt=12)
R["tr_treinado"] = G.campo(ws, GRADE_10[1], r, LARG_10, "qual TR ela treina", None,
                           pt=11, nome=CORPO)
dv(REF["trs"], GRADE_10[1], r + 1)
R["fisico_de"] = G.campo(ws, GRADE_10[2], r, LARG_10, "o físico dela usa", None,
                         pt=11, nome=CORPO)
dv(REF["fisico_de"], GRADE_10[2], r + 1)
TREI, FIS = cel(GRADE_10[1], r + 1), cel(GRADE_10[2], r + 1)
r += 3
txt(ws, 4, r, "TESTES DE RESISTÊNCIA · ela treina um, e você escolhe qual no "
    "campo acima", nome=TITULO, pt=G.PT_ROT, cor=BLOCO, ate=(COLS, r))
r += 1
# a forma e a da ficha de player depois da atualizacao de 04/09: cada linha
# ganhou uma coluna Extra, e ela ENTRA na conta. Aqui o "treinado" nao e caixa
# por linha e sim o menu de cima -- a invocacao treina exatamente UM, e um menu
# diz isso melhor que quatro caixas das quais so uma pode estar marcada.
G.cabecalho_tr(ws, 4, r, 24)
G.cabecalho_tr(ws, 26, r, COLS)
r += 1
for i, (t, atrs) in enumerate(INV["testes_de_resistencia"].items()):
    c1 = 4 + (i % 2) * 22
    rr = r + (i // 2)
    escolha = FIS if len(atrs) > 1 else f'"{atrs[0]}"'
    _extra = f"${L(c1 + G.LARG_TR_NOME + 1)}${rr}"
    e_cel, v_cel = G.linha_tr(
        ws, c1, rr, t, " ou ".join(a[:3] for a in atrs),
        f'=IFERROR({valor_de(escolha)}+IF({TREI}="{t}",{MAEC},0)+N({_extra}),"")',
        zebra=(i // 2) % 2 == 1)
    R["tr_" + t] = v_cel
    R["tr_extra_" + t] = e_cel
r = G.nota(ws, r + 3, "Role d20 e some o número da coluna. O Extra é para bônus "
           "que a planilha não conhece; deixe vazio se não houver. A Defesa não se "
           "rola: o inimigo rola contra ela.")

# ------------------------------------------------------- 05 VIDA E MORTE
V, M = INV["vida"], INV["morte"]
r = G.secao(ws, r + 1, "5", "VIDA E MORTE", ate=20)
BASE_T = f'IFERROR(VLOOKUP({TIPO},{REF["tab_tipos"]},2,FALSE),0)'
CON = CELS[2]
CRUA = f'({BASE_T}+(2+{CON})*{NIV})'
FORTE = f'FLOOR({V["multiplicador_corpo_forte"]}*({BASE_T}+2*{NIV})+{CON}*{NIV},1)'
CORPO_T = f'IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},4,FALSE),"cru")'
_p = INV["sintonia"]["rotas"]["Parrudo"]["multiplicador_maestria"]
PARR = f'IF({SIN}="Parrudo",{_p}*{MAEC},0)'
VMAX = f'=IF({TIPO}="","",IF({CORPO_T}="forte",{FORTE},{CRUA})+{PARR})'

R["vida_max"] = G.campo(ws, GRADE_10[0], r, LARG_10, "vida máxima", VMAX,
                        pt=G.PT_GRANDE, alto=2)
VMAXC = cel(GRADE_10[0], r + 1)
R["vida"] = G.campo(ws, GRADE_10[1], r, LARG_10, "vida agora", None,
                    pt=G.PT_GRANDE, alto=2)
VC = cel(GRADE_10[1], r + 1)
R["corpos"] = G.campo(ws, GRADE_10[2], r, LARG_10, "corpos em campo",
    f'=IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},2,FALSE),"")', alto=2)
R["area"] = G.campo(ws, GRADE_10[3], r, LARG_10, "área bate ×",
    f'=IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},5,FALSE),"")', alto=2)
r += 4
pinta(ws, 4, r, COLS, r, PAINEL_ALTO)
txt(ws, 4, r, "A BARRA", nome=TITULO, pt=G.PT_ROT, cor=OSSO, ate=(14, r))
pinta(ws, 15, r, COLS, r, PAINEL)
txt(ws, 15, r, barra(VC, VMAXC, cor_de_estado(VC, VMAXC)), ate=(COLS, r))
r += 2
REGUA = f'{M["multiplicador_regua"]}*{CRUA}'
R["regua"] = G.campo(ws, GRADE_10[0], r, LARG_10, "régua da morte",
                     f'=IF({TIPO}="","",{REGUA})')
R["meia_regua"] = G.campo(ws, GRADE_10[1], r, LARG_10, "metade dela",
                          f'=IF({TIPO}="","",{REGUA}/2)')
R["volta_com"] = G.campo(ws, GRADE_10[2], r, LARG_10, "volta com",
                         f'=IF({TIPO}="","",FLOOR({VMAXC}/2,1))')
r += 3
r = G.aviso(ws, r, "morre de vez",
            "quando o dano que passar de zero for maior que a metade da régua, ou "
            "quando um golpe só causar a régua inteira. Fora desses dois casos ela "
            "só cai, e você reinvoca.")
r = G.nota(ws, r, "No zero ela sai do campo. Ela não fica Inconsciente e não ganha "
           "Sequela nem Cicatriz. Reinvocar custa os PE de novo, e ela volta com "
           "metade da vida; a vida cheia volta no descanso longo.")

# --------------------------------------------------------- 06 O ORÇAMENTO
r = G.secao(ws, r + 1, "6", "O ORÇAMENTO", ate=32)
O = INV["orcamento"]
MULT = f'IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},3,FALSE),1)'
ORC = f'FLOOR(({O["base"]}+{O["por_marco"]}*{MARC})*{MULT},1)'
R["orcamento"] = G.campo(ws, GRADE_10[0], r, LARG_10, "orçamento", f"={ORC}",
                         pt=G.PT_GRANDE, alto=2)
ORCC = cel(GRADE_10[0], r + 1)

def _cabem(precos, orc):
    n = soma = 0
    for pr in sorted(precos):
        if soma + pr > orc:
            break
        soma += pr
        n += 1
    return n

_orc_teto = int((O["base"] + O["por_marco"] * len(INV["progressao"]["marcos"]))
                * max(t["orcamento_multiplicador"] for t in INV["trilhas"].values()))
N_TRACO = _cabem(INV["traco"].values(), _orc_teto)
N_COMANDO = _cabem([v for v in INV["comando"].values() if v > 0], _orc_teto)

SLOTS, NOMES_SLOT = [], []
r += 4
for grupo, ref_lista, ref_tab, col0, quantos in [
        ("TRAÇO", REF["traco"], REF["tab_traco"], 4, N_TRACO),
        ("COMANDO", REF["comando"], REF["tab_comando"], 26, N_COMANDO)]:
    pinta(ws, col0, r, col0 + 19, r, PAINEL_ALTO)
    txt(ws, col0, r, f"{grupo} · até {quantos}", nome=TITULO, pt=G.PT_ROT,
        cor=OSSO, ate=(col0 + 19, r))
    for i in range(quantos):
        rr = r + 1 + i
        pinta(ws, col0, rr, col0 + 19, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
        txt(ws, col0, rr, "—", nome=DOCUMENTO, pt=10, cor=OSSO, ate=(col0 + 14, rr))
        dv(ref_lista, col0, rr, col0 + 14, rr)
        pc = col0 + 15
        txt(ws, pc, rr, f'=IFERROR(VLOOKUP({cel(col0, rr)},{ref_tab},2,FALSE),0)',
            nome=TITULO, pt=11, cor=OSSO, al="right", ate=(col0 + 19, rr))
        SLOTS.append(cel(pc, rr))
        NOMES_SLOT.append((grupo.lower().replace("ç", "c").replace("ã", "a"),
                           i + 1, cel(col0, rr)))
r += max(N_TRACO, N_COMANDO) + 2

GASTO = "+".join(SLOTS)
R["gasto"] = G.campo(ws, GRADE_10[0], r, LARG_10, "gasto", f"={GASTO}")
R["sobra"] = G.campo(ws, GRADE_10[1], r, LARG_10, "sobra",
    f'=IF({ORCC}-({GASTO})<0,"estourou "&(({GASTO})-{ORCC}),{ORCC}-({GASTO}))',
    cor=AMBAR)
r += 3
r = G.nota(ws, r, "Escolha Traço e Comando até o orçamento acabar. O Servo tem "
           "metade a mais que as outras duas Trilhas. Nada aqui compra dano, Defesa, "
           "acerto ou vida — esses saem dos atributos dela.")

# ------------------------------------------------------------- 07 INVESTIR
r = G.secao(ws, r + 1, "7", "INVESTIR", ate=28)
COLI = f'IF({TRI}="Matilha",3,2)'
DANO = f'=IF({NIV}="","",VLOOKUP({NIV},{REF["tab_investir"]},{COLI},TRUE))'
R["investir"] = G.campo(ws, GRADE_10[0], r, LARG_10, "dano do investir", DANO,
                        pt=G.PT_GRANDE, alto=2)
G.campo(ws, GRADE_10[1], r, LARG_10 + 22, "por corpo",
        f'=IF({TRI}="Matilha","cada um dos cinco rola isto",'
        f'IF({TRI}="","","o corpo em campo rola isto"))', pt=11, nome=CORPO, alto=2)
r = G.nota(ws, r + 4, "É o dano dela quando você gasta a Ação Padrão comandando. "
           "Você e as suas invocações somados causam o dano de uma rodada sua "
           "sozinho.")

# --------------------------------------------------------------- 08 NA MESA
F = INV["ficha_dela"]
r = G.secao(ws, r + 1, "8", "NA MESA", ate=24)
for i, (rot, valor) in enumerate([
        ("invocar", f'=("custa "&{CLAC}&" PE e a Ação Padrão")'),
        ("comandar", '="a Ação Padrão, toda rodada"'),
        ("iniciativa", '="a sua, e ela age logo depois de você"'),
        ("deslocamento", f'=({F["deslocamento"]}&" metros")'),
        ("amarra", f'=({F["amarra"]}&" metros — além disso não pode ser comandada, '
                   f'e não some")')]):
    rr = r + i
    pinta(ws, 4, rr, COLS, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
    txt(ws, 4, rr, rot.upper(), nome=TITULO, pt=G.PT_ROT, cor=TEXTO_FRACO, ate=(14, rr))
    txt(ws, 15, rr, valor, nome=CORPO, pt=G.PT_NOTA, cor=OSSO, ate=(COLS, rr))
r += 6

# ------------------------------------------------- 09 O QUE FICA PENDENTE
VOZ = INV["sintonia"]["rotas"]["Voz"]
r = G.secao(ws, r, "9", "O QUE A FICHA NÃO CALCULA", ate=32)
pinta(ws, 4, r, COLS, r, PAINEL_ALTO)
txt(ws, 4, r, "A CD DOS EFEITOS DELA", nome=TITULO, pt=G.PT_ROT, cor=AMBAR,
    ate=(COLS, r))
pinta(ws, 4, r + 1, COLS, r + 3, PAINEL)
R["cd_pendente"] = txt(ws, 4, r + 1,
    f'=IF({SIN}="Voz","A Voz sobe a CD dos efeitos dela, e o sistema ainda não diz '
    f'qual é essa CD. Combine com o mestre.","")',
    nome=CORPO, pt=G.PT_NOTA, cor=TEXTO, ate=(COLS, r + 1))
txt(ws, 4, r + 2, VOZ["nota_na_ficha"], nome=CORPO, pt=G.PT_LEG, cor=TEXTO_FRACO,
    ate=(COLS, r + 3))

# ================================================================= CATALOGO
cat = base(wb, "CATÁLOGO", COLS, 64)
pinta(cat, 3, 1, COLS, 2, PAINEL_ALTO)
txt(cat, 4, 1, "O CATÁLOGO — o que dá para comprar", nome=TITULO, pt=16, cor=OSSO,
    ate=(30, 2))
txt(cat, 32, 1, "capítulo 16", nome=SERIE, pt=8, cor=TEXTO_FRACO, al="right",
    ate=(COLS, 2))
rc = 4
for grupo, chave, glosa in [
        ("TRAÇO", "traco", "o corpo dela. Vale sempre, sem gastar ação."),
        ("COMANDO", "comando", "o que ela faz quando você gasta a Ação Padrão "
                               "comandando.")]:
    pinta(cat, 4, rc, COLS, rc, FAIXA)
    txt(cat, 4, rc, grupo, nome=TITULO, pt=G.PT_TIT_SEC, cor=OSSO, ate=(20, rc))
    txt(cat, 21, rc, glosa, nome=CORPO, pt=G.PT_NOTA, cor=TEXTO_FRACO, ate=(COLS, rc))
    rc += 1
    pinta(cat, 4, rc, COLS, rc, PAINEL_ALTO)
    txt(cat, 4, rc, "PONTOS", nome=TITULO, pt=G.PT_ROT, cor=OSSO, al="center", ate=(7, rc))
    txt(cat, 8, rc, "NOME", nome=TITULO, pt=G.PT_ROT, cor=OSSO, ate=(15, rc))
    txt(cat, 16, rc, "O QUE FAZ", nome=TITULO, pt=G.PT_ROT, cor=OSSO, ate=(COLS, rc))
    rc += 1
    for i, (nome_e, pts) in enumerate(sorted(INV[chave].items(), key=lambda kv: kv[1])):
        rr = rc + i
        pinta(cat, 4, rr, COLS, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
        txt(cat, 4, rr, pts, nome=TITULO, pt=11, cor=OSSO, al="center", ate=(7, rr))
        txt(cat, 8, rr, nome_e, nome=DOCUMENTO, pt=10, cor=OSSO, ate=(15, rr))
        txt(cat, 16, rr, INV[chave + "_texto"].get(nome_e, ""), nome=CORPO, pt=G.PT_NOTA,
            cor=TEXTO, ate=(COLS, rr))
    rc += len(INV[chave]) + 2

pinta(cat, 4, rc, COLS, rc, FAIXA)
txt(cat, 4, rc, "INVENTAR O SEU", nome=TITULO, pt=G.PT_TIT_SEC, cor=OSSO, ate=(20, rc))
txt(cat, 21, rc, "escreva o efeito, ache na régua o preço, e leve para o mestre "
    "aprovar", nome=CORPO, pt=G.PT_NOTA, cor=TEXTO_FRACO, ate=(COLS, rc))
rc += 1
for grupo, chave in [("TRAÇO", "regua_traco"), ("COMANDO", "regua_comando")]:
    pinta(cat, 4, rc, COLS, rc, PAINEL_ALTO)
    txt(cat, 4, rc, f"régua de {grupo}", nome=TITULO, pt=G.PT_ROT, cor=OSSO, ate=(COLS, rc))
    rc += 1
    for i, (pts, quando) in enumerate(sorted(INV[chave].items(), key=lambda kv: int(kv[0]))):
        rr = rc + i
        pinta(cat, 4, rr, COLS, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
        txt(cat, 4, rr, int(pts), nome=TITULO, pt=11, cor=OSSO, al="center", ate=(7, rr))
        txt(cat, 8, rr, quando, nome=CORPO, pt=G.PT_NOTA, cor=TEXTO, ate=(COLS, rr))
    rc += len(INV[chave]) + 1

pinta(cat, 4, rc, COLS, rc, PAINEL_ALTO)
txt(cat, 4, rc, "O QUE O ORÇAMENTO NÃO COMPRA", nome=TITULO, pt=G.PT_ROT,
    cor=AMBAR, ate=(COLS, rc))
rc += 1
for i, (item, porque) in enumerate(INV["nao_compra"].items()):
    rr = rc + i
    pinta(cat, 4, rr, COLS, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
    txt(cat, 4, rr, item, nome=DOCUMENTO, pt=10, cor=OSSO, ate=(17, rr))
    txt(cat, 18, rr, porque, nome=CORPO, pt=G.PT_NOTA, cor=TEXTO_FRACO, ate=(COLS, rr))

# ------------------------------------------------------------------ INDICE
IDX = c + 3
d.column_dimensions[L(IDX)].width = 22
d.column_dimensions[L(IDX + 1)].width = 12
txt(d, IDX, 2, "campo", pt=PT_ROTULO, cor=TEXTO_FRACO)
txt(d, IDX + 1, 2, "célula", pt=PT_ROTULO, cor=TEXTO_FRACO)
for a, celula in ATR.items():
    R["atr_" + a] = celula
for i, (chave, v) in enumerate(R.items()):
    txt(d, IDX, 3 + i, chave)
    txt(d, IDX + 1, 3 + i, v.coordinate)
for i, sl in enumerate(SLOTS):
    txt(d, IDX, 3 + len(R) + i, f"slot_pontos_{i+1}")
    txt(d, IDX + 1, 3 + len(R) + i, sl.replace("$", ""))
for i, (grupo, n_, coord) in enumerate(NOMES_SLOT):
    txt(d, IDX, 3 + len(R) + len(SLOTS) + i, f"{grupo}_{n_}")
    txt(d, IDX + 1, 3 + len(R) + len(SLOTS) + i, coord.replace("$", ""))

for i, aba in enumerate(["INVOCAÇÃO", "CATÁLOGO"]):
    wb.move_sheet(aba, i - wb.sheetnames.index(aba))

saida = os.path.join(AQUI, "ficha-invocacao.xlsx")
wb.save(saida)
print(f"ficha escrita: {saida}")
print(f"abas: {wb.sheetnames}")
print(f"campos indexados: {len(R)} · slots: {N_TRACO} Traço e {N_COMANDO} Comando")
