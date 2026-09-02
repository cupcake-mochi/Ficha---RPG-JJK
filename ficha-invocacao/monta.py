# -*- coding: utf-8 -*-
"""Monta a ficha da invocacao do Projeto M em .xlsx.

Planilha SEPARADA, por escolha do Mizuki: o que a ficha do personagem sabe
(nivel, Essencia, Inteligencia) entra aqui como celula que o jogador digita.
No dia em que ela virar aba da ficha grande, essas tres celulas viram
formula apontando para a FICHA e nada mais muda.

Nenhum numero esta escrito aqui: tudo vem do invocacao.json, cujo dono
declarado e o capitulo 16 do Manual da Guilda.
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ficha"))

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
from estilo import (CORPO, TITULO, DOCUMENTO, SERIE, PT_ROTULO, PT_VALOR,
                    PT_TITULO, PT_GRANDE, LARG_COL, ALT_LIN, FUNDO, PAINEL,
                    PAINEL_ALTO, LINHA, BLOCO, TEXTO_FRACO, TEXTO, TINTA,
                    OSSO, AMBAR, VERMELHO, txt, regua, pinta, junta, secao,
                    campo, barra, cor_de_estado, base, lombada)

INV = json.load(open(os.path.join(RAIZ, "invocacao.json"), encoding="utf-8"))

COLS = 46
wb = Workbook()
wb.remove(wb.active)
wb._fonts[0] = Font(name=CORPO, size=PT_VALOR, color=TEXTO)

# ====================================================================== DADOS
# a aba de apoio: as listas dos menus, as tabelas de PROCV, e o espelho dos
# cinco atributos dela -- o espelho existe porque INDICE/CORRESP precisa de
# celulas contiguas, e na aba de cima elas estao espalhadas pelo desenho.
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
c = tabela(c, "tab_tipos", ["tipo", "base"],
           [[k, v] for k, v in INV["tipos"].items()])
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

# as tres escadas de progressao, cada uma numa coluna
P = INV["progressao"]
for nome_e, valores in [("e_marcos", P["marcos"]), ("e_maestria", P["maestria_em"]),
                        ("e_classe", P["classe_em"])]:
    d.column_dimensions[L(c)].width = 10
    txt(d, c, 2, nome_e, pt=PT_ROTULO, cor=TEXTO_FRACO)
    for i, v in enumerate(valores):
        txt(d, c, 3 + i, v)
    REF[nome_e] = f"DADOS!${L(c)}$3:${L(c)}${2+len(valores)}"
    c += 1

ESPELHO = c + 1          # o espelho dos cinco atributos dela, preenchido depois
REF["espelho"] = f"DADOS!${L(ESPELHO)}$3:${L(ESPELHO)}$7"
pinta(d, 1, 1, c + 3, 30, FUNDO)

# ================================================================= INVOCAÇÃO
ws = base(wb, "INVOCAÇÃO", COLS, 92)
R = {}

def dv(formula, c1, r1, c2=None, r2=None):
    v = DataValidation(type="list", formula1=formula, allow_blank=True,
                       showDropDown=False)
    ws.add_data_validation(v)
    v.add(f"{L(c1)}{r1}:{L(c2 or c1)}{r2 or r1}")

def cel(c, r):
    return f"${L(c)}${r}"

def entrada(c, r, larg, rot, valor=None, pt=16, cor=OSSO):
    """celula que o JOGADOR digita: valor em osso, regua embaixo."""
    return campo(ws, c, r, larg, rot, valor, pt=pt, cor=cor)

def derivada(c, r, larg, rot, formula, pt=16):
    """celula que a planilha calcula: valor em branco, para separar das de cima."""
    return campo(ws, c, r, larg, rot, formula, pt=pt, cor=TEXTO, nome=TITULO)

lombada(ws, 92, "INVOCAÇÃO", "PROJETO - M")
pinta(ws, 3, 1, COLS, 2, PAINEL_ALTO)
txt(ws, 4, 1, "A FICHA DA INVOCAÇÃO", nome=TITULO, pt=18, cor=OSSO, ate=(30, 2))
txt(ws, 32, 1, f'capítulo 16 · sistema v{INV["_meta"]["versao_do_sistema"]}',
    nome=SERIE, pt=8, cor=TEXTO_FRACO, al="right", ate=(COLS, 2))

# ------------------------------------------------------------- 01 O DONO
r = secao(ws, 4, "01", "O DONO — o que a ficha dele decide", c2=30)
R["nivel"]     = entrada(4, r, 5, "nível do dono", 2, pt=20)
R["ess_dono"]  = entrada(11, r, 5, "essência dele", 0)
R["int_dono"]  = entrada(18, r, 5, "inteligência dele", 0)
NIV, ESS, INT = cel(4, r + 1), cel(11, r + 1), cel(18, r + 1)

MAE = f'(1+COUNTIF({REF["e_maestria"]},"<="&{NIV}))'
MAR = f'COUNTIF({REF["e_marcos"]},"<="&{NIV})'
CLA = f'COUNTIF({REF["e_classe"]},"<="&{NIV})'
R["maestria"] = derivada(25, r, 5, "maestria", f"={MAE}")
R["marcos"]   = derivada(32, r, 5, "marcos", f"={MAR}")
R["classe"]   = derivada(39, r, 6, "maior classe · PE de invocar", f"={CLA}")
MAEC, MARC, CLAC = cel(25, r + 1), cel(32, r + 1), cel(39, r + 1)
txt(ws, 4, r + 3, "estas três da esquerda você digita; no dia em que isto virar aba da "
    "ficha grande, elas puxam da FICHA por fórmula e nada mais muda.",
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 3))
r += 5

# -------------------------------------------------------- 02 A INVOCAÇÃO
r = secao(ws, r, "02", "A INVOCAÇÃO", c2=30)
R["nome"]    = entrada(4, r, 11, "nome", None, pt=18)
R["tipo"]    = entrada(17, r, 8, "tipo", None, pt=12)
R["trilha"]  = entrada(27, r, 6, "trilha", None, pt=12)
R["sintonia"] = entrada(35, r, 10, "sintonia", "—", pt=12)
dv(REF["tipos"], 17, r + 1)
dv(REF["trilhas"], 27, r + 1)
dv(REF["sintonia"], 35, r + 1)
TIPO, TRI, SIN = cel(17, r + 1), cel(27, r + 1), cel(35, r + 1)
txt(ws, 4, r + 3, "a Sintonia é o degrau de nível 2 do Evocador, e as três rotas dela "
    "mexem nesta ficha: " + " · ".join(
        f'{k} {v["efeito"]}' for k, v in INV["sintonia"]["rotas"].items()),
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 4))
r += 6

# ---------------------------------------------------- 03 OS ATRIBUTOS DELA
A = INV["atributos"]
r = secao(ws, r, "03", "OS ATRIBUTOS DELA — são dela, e ela não copia os seus", c2=34)
ATR = {}
for i, a in enumerate(A["lista"]):
    c1 = 4 + i * 7
    txt(ws, c1, r, a.upper(), nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(c1 + 5, r))
    ATR[a] = txt(ws, c1, r + 1, 0, nome=TITULO, pt=24, cor=OSSO, al="center",
                 ate=(c1 + 5, r + 2))
    regua(ws, c1, r + 3, c1 + 5, LINHA)
CELS = [cel(4 + i * 7, r + 1) for i in range(5)]
GASTO_A = "+".join(CELS)
DISP_A = f'({A["pontos_na_criacao"]}+{MARC})'
r += 4
R["pontos_atributo"] = derivada(4, r, 8, "pontos gastos · de", f"={GASTO_A}", pt=12)
R["pontos_disp"]     = derivada(14, r, 8, "disponíveis", f"={DISP_A}", pt=12)
aviso = (f'=IF({GASTO_A}>{DISP_A},"estourou o total",'
         f'IF(MAX({",".join(CELS)})>{A["teto"]},"estourou o teto de {A["teto"]}",'
         f'IF({GASTO_A}<{DISP_A},"sobrou ponto","ok")))')
R["aviso_atributo"] = campo(ws, 24, r, 20, "conferência", aviso, pt=12, cor=AMBAR,
                            nome=TITULO)
txt(ws, 4, r + 3, f'{A["pontos_na_criacao"]} pontos na criação com teto {A["teto_na_criacao"]}, '
    f'mais {A["por_marco"]} por marco, teto {A["teto"]}. Mesma regra da sua ficha.',
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 3))
r += 5

# espelho na DADOS, para o INDICE/CORRESP do acerto e dos TR
for i, a in enumerate(A["lista"]):
    txt(d, ESPELHO, 3 + i, f"=INVOCAÇÃO!{CELS[i]}")
d.column_dimensions[L(ESPELHO)].width = 10
txt(d, ESPELHO, 2, "espelho", pt=PT_ROTULO, cor=TEXTO_FRACO)
ESP = REF["espelho"]
NOMES_A = REF["atributos"]

def valor_de(escolha):
    return f"INDEX({ESP},MATCH({escolha},{NOMES_A},0))"

# --------------------------------------------------- 04 O QUE ENCARA O DADO
r = secao(ws, r, "04", "O QUE ENCARA O DADO — o número é dela, o ritmo é seu", c2=36)
R["atr_acerto"] = entrada(4, r, 8, "atributo do acerto", None, pt=12)
dv(NOMES_A, 4, r + 1)
ACE = cel(4, r + 1)
R["acerto"] = derivada(14, r, 5, "acerto", f'=IF({ACE}="","",{valor_de(ACE)}+{MAEC})')
R["defesa_de"] = entrada(21, r, 9, "defesa usa, dele", None, pt=12)
dv(REF["defesa_de"], 21, r + 1)
DEFDE = cel(21, r + 1)
R["defesa"] = derivada(32, r, 5, "defesa",
    f'=10+{CELS[1]}+FLOOR(IF({DEFDE}="{A["lista"][4]}",{ESS},{INT})/2,1)')
_presa = INV["sintonia"]["rotas"]["Presa"]["critico_a_partir_de"]
R["critico"] = derivada(39, r, 6, "crítico com",
    f'=IF({SIN}="Presa","{_presa} ou 20","20")', pt=12)
txt(ws, 4, r + 3, "acerto e Teste de Resistência rolam d20 + isto. A Defesa é passiva, "
    "e a maestria não entra nela.", pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 3))
r += 4

R["tr_treinado"] = entrada(4, r, 8, "qual TR ela treina", None, pt=12)
dv(REF["trs"], 4, r + 1)
R["fisico_de"] = entrada(14, r, 7, "o físico dela usa", None, pt=12)
dv(REF["fisico_de"], 14, r + 1)
TREI, FIS = cel(4, r + 1), cel(14, r + 1)
r += 3
for i, (t, atrs) in enumerate(INV["testes_de_resistencia"].items()):
    c1 = 4 + (i % 2) * 20
    rr = r + (i // 2) * 2
    escolha = FIS if len(atrs) > 1 else f'"{atrs[0]}"'
    txt(ws, c1, rr, t, nome=DOCUMENTO, pt=11, cor=TEXTO, ate=(c1 + 10, rr))
    txt(ws, c1 + 11, rr, f'=IFERROR({valor_de(escolha)}+IF({TREI}="{t}",{MAEC},0),"")',
        nome=TITULO, pt=12, cor=OSSO, al="right", ate=(c1 + 15, rr))
    regua(ws, c1, rr + 1, c1 + 15, LINHA)
txt(ws, 4, r + 4, "ela treina um só. A sua maestria entra nele, e nos outros três não — "
    "igual a qualquer ficha.", pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 4))
r += 6

# ------------------------------------------------------- 05 VIDA E MORTE
V, M = INV["vida"], INV["morte"]
r = secao(ws, r, "05", "VIDA E MORTE", c2=30)
BASE_T = f'IFERROR(VLOOKUP({TIPO},{REF["tab_tipos"]},2,FALSE),0)'
CON = CELS[2]
CRUA = f'({BASE_T}+(2+{CON})*{NIV})'
FORTE = f'FLOOR({V["multiplicador_corpo_forte"]}*({BASE_T}+2*{NIV})+{CON}*{NIV},1)'
CORPO_T = f'IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},4,FALSE),"cru")'
_p = INV["sintonia"]["rotas"]["Parrudo"]["multiplicador_maestria"]
PARR = f'IF({SIN}="Parrudo",{_p}*{MAEC},0)'
VMAX = f'=IF({TIPO}="","",IF({CORPO_T}="forte",{FORTE},{CRUA})+{PARR})'

R["vida_max"] = derivada(4, r, 6, "vida máxima", VMAX, pt=20)
VMAXC = cel(4, r + 1)
R["vida"] = entrada(12, r, 6, "vida agora", None, pt=20)
VC = cel(12, r + 1)
txt(ws, 20, r + 1, barra(VC, VMAXC, cor_de_estado(VC, VMAXC)), ate=(31, r + 1))
regua(ws, 20, r + 2, 31, LINHA)
R["corpos"] = derivada(33, r, 5, "corpos em campo",
    f'=IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},2,FALSE),"")')
R["area"] = derivada(40, r, 5, "área bate ×",
    f'=IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},5,FALSE),"")')
r += 4

REGUA = f'{M["multiplicador_regua"]}*{CRUA}'
R["regua"] = derivada(4, r, 7, "régua da morte", f'=IF({TIPO}="","",{REGUA})', pt=14)
R["meia_regua"] = derivada(13, r, 7, "metade dela", f'=IF({TIPO}="","",{REGUA}/2)', pt=14)
R["volta_com"] = derivada(22, r, 7, "volta com", f'=IF({TIPO}="","",FLOOR({VMAXC}/2,1))', pt=14)
txt(ws, 31, r, "MORRE DE VEZ SE", nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(COLS, r))
txt(ws, 31, r + 1, "o excedente passar da metade, ou um golpe só causar a régua inteira",
    pt=9, cor=TEXTO, ate=(COLS, r + 2))
r += 4
txt(ws, 4, r, "a régua sai da vida CRUA do tipo, nunca da do corpo forte — é a mesma "
    "para um corpo, cinco, ou o corpo grande. Ela some no zero: sem Inconsciente, "
    "sem Sequela, sem Cicatriz. A vida cheia volta no descanso longo.",
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 1))
r += 3

# --------------------------------------------------------- 06 O ORÇAMENTO
r = secao(ws, r, "06", "O ORÇAMENTO — compra o que ela FAZ, nunca número", c2=36)
O = INV["orcamento"]
MULT = f'IFERROR(VLOOKUP({TRI},{REF["tab_trilhas"]},3,FALSE),1)'
ORC = f'FLOOR(({O["base"]}+{O["por_marco"]}*{MARC})*{MULT},1)'
R["orcamento"] = derivada(4, r, 6, "orçamento", f"={ORC}", pt=20)
ORCC = cel(4, r + 1)
r += 4

# quantos slots cada grupo precisa: o maior orcamento que existe comprando as
# entradas mais baratas. Derivado, nunca escrito na mao -- com 4 por grupo a
# ficha ja estourava no nivel 6 do Servo, e o teto real e 9 Traco e 6 Comando.
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

SLOTS = []
NOMES_SLOT = []
for grupo, ref_lista, ref_tab, col0, quantos in [
        ("TRAÇO", REF["traco"], REF["tab_traco"], 4, N_TRACO),
        ("COMANDO", REF["comando"], REF["tab_comando"], 26, N_COMANDO)]:
    txt(ws, col0, r, f"{grupo} · até {quantos}", nome=TITULO, pt=PT_ROTULO,
        cor=BLOCO, ate=(col0 + 17, r))
    for i in range(quantos):
        rr = r + 1 + i
        pinta(ws, col0, rr, col0 + 17, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
        txt(ws, col0, rr, "—", cor=OSSO, pt=11, ate=(col0 + 12, rr))
        dv(ref_lista, col0, rr)
        pc = col0 + 13
        txt(ws, pc, rr, f'=IFERROR(VLOOKUP({cel(col0, rr)},{ref_tab},2,FALSE),0)',
            nome=TITULO, pt=11, cor=TEXTO_FRACO, al="right", ate=(col0 + 17, rr))
        SLOTS.append(cel(pc, rr))
        NOMES_SLOT.append((grupo.lower().replace("ç", "c").replace("ã", "a"),
                           i + 1, cel(col0, rr)))
r += max(N_TRACO, N_COMANDO) + 2

GASTO = "+".join(SLOTS)
R["gasto"] = derivada(4, r, 6, "gasto", f"={GASTO}", pt=14)
R["sobra"] = campo(ws, 12, r, 6, "sobra",
    f'=IF({ORCC}-({GASTO})<0,"estourou "&(({GASTO})-{ORCC}),{ORCC}-({GASTO}))',
    pt=14, cor=AMBAR, nome=TITULO)
txt(ws, 20, r, "O QUE ELE NÃO COMPRA A PREÇO NENHUM", nome=TITULO, pt=8,
    cor=TEXTO_FRACO, ate=(COLS, r))
txt(ws, 20, r + 1, " · ".join(INV["nao_compra"]), pt=9, cor=TEXTO, ate=(COLS, r + 2))
txt(ws, 4, r + 4, "o Servo monta com o orçamento da ficha mais metade, porque é um corpo "
    "só e não cinco. Todo orçamento é múltiplo de 4, então fecha redondo.",
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 4))
r += 6

# ------------------------------------------------------------- 07 INVESTIR
r = secao(ws, r, "07", "INVESTIR — o ataque, e toda invocação tem", c2=32)
# PROCV aproximado, e nao INDICE/CORRESP: a primeira coluna da tabela e a
# faixa em ordem crescente, que e exatamente o que o PROCV com VERDADEIRO le.
# O INDICE/CORRESP devolvia sempre a primeira faixa -- pego pela regressao.
COLI = f'IF({TRI}="Matilha",3,2)'
DANO = f'=IF({NIV}="","",VLOOKUP({NIV},{REF["tab_investir"]},{COLI},TRUE))'
R["investir"] = derivada(4, r, 7, "dano do investir", DANO, pt=20)
txt(ws, 14, r, "POR CORPO", nome=TITULO, pt=8, cor=TEXTO_FRACO, ate=(24, r))
txt(ws, 14, r + 1, f'=IF({TRI}="Matilha","cada um dos cinco rola isto",'
    f'IF({TRI}="","","o corpo em campo rola isto"))', pt=10, cor=TEXTO, ate=(30, r + 1))
txt(ws, 4, r + 3, "você e todas as suas invocações somados entregam uma Rotina. "
    "O número de dados sempre desce — a soma nunca passa do que você faria sozinho.",
    pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 3))
r += 5

# --------------------------------------------------------------- 08 NA MESA
C = INV["custo"]
F = INV["ficha_dela"]
r = secao(ws, r, "08", "NA MESA — o que não muda", c2=30)
for i, (rot, valor) in enumerate([
        ("invocar", f'=("custa "&{CLAC}&" PE e a Ação Padrão")'),
        ("comandar", '="a Ação Padrão, toda rodada"'),
        ("iniciativa", '="a sua, e ela age logo depois de você"'),
        ("deslocamento", f'=({F["deslocamento"]}&" metros")'),
        ("amarra", f'=({F["amarra"]}&" metros — além disso não pode ser comandada, e não some")')]):
    rr = r + i
    pinta(ws, 4, rr, COLS, rr, PAINEL if i % 2 == 0 else PAINEL_ALTO)
    txt(ws, 4, rr, rot, nome=TITULO, pt=9, cor=TEXTO_FRACO, ate=(12, rr))
    txt(ws, 13, rr, valor, pt=10, cor=TEXTO, ate=(COLS, rr))

# ------------------------------------------------- 09 O QUE FICA PENDENTE
# a regra do repositorio: onde a regra nao existe, nao se inventa -- a ficha
# marca como pendente em vez de chutar numero.
VOZ = INV["sintonia"]["rotas"]["Voz"]
r += 6
r = secao(ws, r, "09", "O QUE ESTA FICHA NÃO CALCULA, E POR QUÊ", c2=36)
pinta(ws, 4, r, COLS, r + 3, PAINEL)
txt(ws, 4, r, "a CD dos efeitos dela", nome=TITULO, pt=10, cor=AMBAR, ate=(20, r))
txt(ws, 4, r + 1,
    f'=IF({SIN}="Voz","a Voz manda subir a CD dela, e a invocação não tem fórmula '
    f'de CD em documento nenhum — combine com o mestre","")',
    pt=9, cor=TEXTO, ate=(COLS, r + 1))
txt(ws, 4, r + 2, VOZ["nota_na_ficha"], pt=8, cor=TEXTO_FRACO, ate=(COLS, r + 3))
R["cd_pendente"] = ws.cell(row=r + 1, column=4)

# o indice: quem quiser achar um campo le daqui, em vez de decorar coordenada.
# Serve ao validador e ao teste de regressao. Mesmo molde do dados.indice da
# ficha grande.
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
# os oito slots de compra nao passam pelo R: eles nao tem rotulo proprio
for i, sl in enumerate(SLOTS):
    txt(d, IDX, 3 + len(R) + i, f"slot_pontos_{i+1}")
    txt(d, IDX + 1, 3 + len(R) + i, sl.replace("$", ""))
for i, (grupo, n_, coord) in enumerate(NOMES_SLOT):
    txt(d, IDX, 3 + len(R) + len(SLOTS) + i, f"{grupo}_{n_}")
    txt(d, IDX + 1, 3 + len(R) + len(SLOTS) + i, coord.replace("$", ""))

# a INVOCAÇÃO abre primeiro; a DADOS fica escondida atrás dela
wb.move_sheet("INVOCAÇÃO", -1)

saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ficha-invocacao.xlsx")
wb.save(saida)
print(f"ficha escrita: {saida}")
print(f"abas: {wb.sheetnames}")
print(f"campos indexados: {len(R)}")
