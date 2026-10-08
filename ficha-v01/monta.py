# -*- coding: utf-8 -*-
"""Monta a Ficha (PROJETO M) 0.1 em .xlsx, a partir do layout.json.

    python3 ficha-v01/extrair.py    # o desenho do .xlsx do Mizuki -> layout.json
    python3 ficha-v01/monta.py      # layout.json -> ficha-projeto-m-0.1.xlsx
    python3 comparar-ficha-01.py    # prova que os dois batem

Por que o desenho mora num JSON e nao em codigo: esta ficha nasceu editada a
mao no Google Sheets -- 8 mil celulas, 317 mesclagens, 105 estilos. Escrever
isso como chamada de funcao seria transcrever um dump com sintaxe de Python, e
qualquer edicao futura dela vai continuar acontecendo no Sheets, nao aqui. O
JSON e o desenho; este arquivo e a maquina que o toca.

Onde a ficha vive e o Google Sheets, e isso decide duas coisas:
  · o IFS das 16 celulas fica CRU. No Excel ele daria #NAME?, e esta aceito.
  · o SPARKLINE das 3 celulas continua. Ele nao existe no Excel.
"""
import json, os, sys
from openpyxl.worksheet.formula import ArrayFormula
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import Rule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.drawing.image import Image as Img
from openpyxl.comments import Comment

AQUI = os.path.dirname(os.path.abspath(__file__))
LAYOUT = json.load(open(os.path.join(AQUI, "layout.json"), encoding="utf-8"))

# v0.239 do sistema, decisao do Mizuki: a aba DADOS sai do catalogo, e nao da exportacao. O
# layout.json continua copia fiel da planilha viva; o conteudo da DADOS e escrito por cima
# dele aqui. Ver dados_catalogo.py.
# 17/09/2026, a segunda rodada: o desenho que a mesa pediu -- as caixinhas de Buff/Debuff, o Refino/Corpo/Leque,
# a foto maior, os textos da CARTEIRA e a margem da direita. Vem antes de tudo, porque o indice sai dos
# rotulos que ela deixa. Ver ficha_layout.py.
import ficha_layout
_FL = ficha_layout.trocas(LAYOUT)
print(f"o desenho da mesa: {ficha_layout.aplica(LAYOUT, _FL)} mudanca(s) na exportacao")
ficha_layout.desenha_arte(_FL)

# 01/10/2026: o cabecalho da FICHA no molde do estudo da Ficha Pessoal -- a marca, o titulo e a linha de apoio a
# esquerda, o nome e o Caminho a direita. Vem antes do indice porque o nome muda de celula. Ver cabecalho.py.
import cabecalho
_CAB = cabecalho.trocas(LAYOUT)
print(f"o cabecalho no molde do estudo: {cabecalho.aplica(LAYOUT, _CAB)} mudanca(s) na exportacao")

# 17/09/2026: o indice da DADOS passa a guardar o endereco em formula, derivado dos rotulos da FICHA.
# Ele vem antes de tudo porque as limpezas de baixo leem por ele. Ver indice_ficha.py.
import indice_ficha
print(f"o indice da DADOS em formula: {indice_ficha.aplica(LAYOUT, indice_ficha.trocas(LAYOUT))} "
      f"celula(s) diferentes da exportacao")

import dados_catalogo
_DADOS_CAT = dados_catalogo.valores()
for _a in LAYOUT["abas"]:
    if _a["nome"] == "DADOS":
        print(f"a DADOS sai do catalogo v{_DADOS_CAT['B1']}: "
              f"{dados_catalogo.aplica(_a, _DADOS_CAT)} celula(s) diferentes da exportacao")
print(f"a vida e o PE da FICHA leem a faixa {dados_catalogo.faixa_dos_caminhos(json.load(open(os.path.join(dados_catalogo.RAIZ, 'decisoes-ficha.json'), encoding='utf-8')))}: "
      f"{dados_catalogo.troca_na_ficha(LAYOUT)} formula(s)")

# v0.240 do sistema, o B14: o Teste de Resistencia treinado soma a maestria, e nao 2. O termo sai do
# catalogo, e a celula dele sai do indice da DADOS. Ver tr_treinado.py.
import tr_treinado
_TR = tr_treinado.trocas(LAYOUT)
print(f"o TR treinado soma o termo do catalogo: {tr_treinado.aplica(LAYOUT, _TR)} formula(s) "
      f"diferentes da exportacao")

# v0.246 do sistema, o B3 na opcao A: o EQUIPAMENTO vira menu de uniforme e escudo, a tabela sai do
# catalogo para a DADOS, e o REFINO ESCOLHIDO entra ao lado do BLOQUEAR. Ver defesa_equipamento.py.
import defesa_equipamento
_DE = defesa_equipamento.trocas(LAYOUT)
print(f"a Defesa com uniforme, escudo e refino escolhido: {defesa_equipamento.aplica(LAYOUT, _DE)} "
      f"celula(s) diferentes da exportacao")

# 17/09/2026: a ficha automatica -- os X de Y, os marcos, o atributo que soma o Corpo, e as Passivas do
# Leque em coluna propria. Ver ficha_automatica.py.
import ficha_automatica
_FA = ficha_automatica.trocas(LAYOUT)
print(f"a ficha automatica: {ficha_automatica.aplica(LAYOUT, _FA)} mudanca(s) na exportacao")

# 01/10/2026: a FICHA PESSOAL -- o que ela muda na FICHA (o EQUIPAMENTO e o XP viram espelho, o
# DESLOCAMENTO cai pela metade com a punicao) e as tabelas dela na DADOS. A aba em si entra mais abaixo,
# depois das correcoes de borda, porque ela copia o cabecalho e a lombada da FICHA. Ver ficha_pessoal.py.
import ficha_pessoal
_FP = ficha_pessoal.trocas(LAYOUT)
print(f"a Ficha Pessoal, na FICHA e na DADOS: {ficha_pessoal.aplica(LAYOUT, _FP)} mudanca(s) na exportacao")

# o cabecalho escreveu o endereco do Caminho, da Trilha e do nivel antes de as limpezas de cima rodarem: se alguma
# delas mexer nas linhas da FICHA, a formula dele aponta para o lugar antigo, e a montagem para aqui.
_quem = next(r[1] for a in LAYOUT["abas"] if a["nome"] == "FICHA" for r in a["celulas"] if r[0] == cabecalho.C_QUEM[0])
if _quem != cabecalho.quem(LAYOUT):
    raise SystemExit(f"o cabecalho da FICHA le o Caminho no lugar antigo: {_quem} != {cabecalho.quem(LAYOUT)}")

# 19/09/2026: enganos de formatacao manual da planilha viva (a caixa ORIGEM com borda branca), corrigidos
# na saida. Ver correcoes_borda.py.
# 02/10/2026, limpeza 26: o menu rapido. A secao 8 da FICHA deixa de ser digitada e mostra o que esta na FICHA
# AMALDICOADA. Ele le as contas da aba (as trocas dela, que so entra no layout mais abaixo, depois das bordas) e vem
# antes das correcoes de borda, porque a FICHA cresce e a lombada tem de ir ate a ultima linha. Ver menu_rapido.py.
# 02/10/2026, limpeza 27: as Habilidades. A secao 7 deixa de ser "Anotacoes" e vira cartas, uma por degrau de Caminho e
# uma por entrega de Trilha, escritas pelo jogador. Ela cresce, e o menu rapido comeca onde ela termina. Ver habilidades.py.
import ficha_amaldicoada, menu_rapido, habilidades
_FAM = ficha_amaldicoada.trocas(LAYOUT)
_HB = habilidades.trocas(LAYOUT, _FAM)
_MR = menu_rapido.trocas(LAYOUT, _FAM, r0=_HB["fim"], guarda=frozenset(_HB["_estilos"]))
print(f"as habilidades na secao 7 da FICHA: {habilidades.aplica(LAYOUT, _HB)} mudanca(s), da linha {_HB['r7']} a {_HB['fim'] - 1}")
print(f"o menu rapido na secao 8 da FICHA: {menu_rapido.aplica(LAYOUT, _MR)} mudanca(s), da linha {_MR['r0']} a {_MR['fim']}, "
      f"{len(_MR['grupos'])} grupo(s)")
import correcoes_borda
print(f"as bordas corrigidas: {correcoes_borda.aplica(LAYOUT)} celula(s) diferentes da exportacao")

# 03/10/2026, limpeza 28: a moldura da foto da CARTEIRA sai de dentro da caixa, pedido do Mizuki, para o jogador inserir
# a foto NA celula, e nao solta por cima. As retas viram borda na regua e os dois cantos chanfrados, imagem pequena na
# celula do canto. Ver moldura_foto.py.
import moldura_foto
_MF = moldura_foto.trocas(LAYOUT)
print(f"a moldura da foto em volta da caixa: {moldura_foto.aplica(LAYOUT, _MF)} mudanca(s), a caixa {_MF['caixa']} livre")
moldura_foto.desenha(_MF)

# 19/09/2026: o texto curto que abre frase ou titulo com a inicial minuscula, na INVOCACAO e no CATALOGO.
# Ver correcoes_texto.py.
import correcoes_texto
print(f"os textos com inicial maiuscula: {correcoes_texto.aplica(LAYOUT)} celula(s) diferentes da exportacao")

# ---------------------------------------------------------------------------------------------
# O NOME DO SISTEMA NA LOMBADA (07/10/2026). O Mizuki: "a ficha ta sem o nome, que é ciclo maldito e pode por a versão
# como 1.0, isso vale pra ficha toda". O cabeçalho de cada aba já lê o nome da DADOS!F1, que vem do arquivo de dados
# (_meta.sistema); o texto em pé na lateral da FICHA vinha escrito da exportação, "PROJETO M", e as abas novas o copiam
# de lá. Ele passa a dizer o nome que o arquivo de dados dá.
# ---------------------------------------------------------------------------------------------
LOMBADA_DE_ANTES = "PROJETO M"
_SISTEMA = json.load(open(os.path.join(dados_catalogo.RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))["_meta"]["sistema"].upper()
_n_lomb = 0
for _a in LAYOUT["abas"]:
    for _c in _a["celulas"]:
        if _c[1] == LOMBADA_DE_ANTES:
            _c[1] = _SISTEMA
            _n_lomb += 1
if not _n_lomb:
    raise SystemExit("monta: nao achei o texto da lombada para por o nome do sistema")
print(f"o nome do sistema na lombada ({_SISTEMA}): {_n_lomb} celula(s) diferentes da exportacao")

# 17/09/2026: o GLOSSARIO, entre a DADOS e a INVOCACAO -- o que cada atributo, pericia, oficio e
# termo da ficha quer dizer. Nao tem planilha viva por tras, ao contrario das outras seis: nasce
# inteiro aqui, reaproveitando os estilos que o CATALOGO ja usa. Ver glossario.py.
import glossario
_pos_gloss = next(i for i, a in enumerate(LAYOUT["abas"]) if a["nome"] == "INVOCAÇÃO")
_ABA_GLOSS = glossario.aba(LAYOUT)
LAYOUT["abas"].insert(_pos_gloss, _ABA_GLOSS)
print(f"o glossario: {_ABA_GLOSS['linhas']} linha(s), {len(_ABA_GLOSS['celulas'])} celula(s)")

# 01/10/2026: a FICHA PESSOAL, entre a FICHA e o GLOSSARIO, pedido do Mizuki. Como o GLOSSARIO, ela nao tem
# planilha viva por tras: nasce inteira no ficha_pessoal.py, do desenho que ele fechou por estudo.
_pos_fp = next(i for i, a in enumerate(LAYOUT["abas"]) if a["nome"] == "FICHA") + 1
_ABA_FP = ficha_pessoal.aba(LAYOUT, _FP)
LAYOUT["abas"].insert(_pos_fp, _ABA_FP)
print(f"a Ficha Pessoal: {_ABA_FP['linhas']} linha(s), {_ABA_FP['colunas']} coluna(s), {len(_ABA_FP['celulas'])} celula(s)")

# 01/10/2026: a FICHA AMALDICOADA, depois da FICHA, e a aba oculta das contas dela, a DADOS_AM, depois da DADOS.
# Tambem nasce inteira no gerador, do desenho que o Mizuki fechou por estudo. Vem depois da FICHA PESSOAL porque le
# o cabecalho e a lombada da FICHA ja corrigidos, e nao muda nenhuma celula das outras abas. Ver ficha_amaldicoada.py.
_ABA_AM = ficha_amaldicoada.aplica(LAYOUT, _FAM)
print(f"a Ficha Amaldiçoada: {_ABA_AM['linhas']} linha(s), {_ABA_AM['colunas']} coluna(s), {len(_ABA_AM['celulas'])} celula(s), "
      f"{len(_ABA_AM['mescladas'])} mesclagem(ns), {len(_ABA_AM['grupos']['linhas'])} grupo(s) de linhas; "
      f"a DADOS_AM: {_FAM['aba_dados']['linhas']} linha(s), {_FAM['aba_dados']['colunas']} coluna(s)")

# 06/10/2026, limpeza 29: a INVOCAÇÕES, depois da FICHA AMALDICOADA, e a aba oculta das contas dela, a DADOS_INVOC. E a
# invocacao refeita depois do livro reconstruido (a entidade com ficha propria, capitulos 16 e 17), no desenho que o
# Mizuki fechou por estudo. Nasce inteira no gerador e nao muda nenhuma celula das outras abas. Ver ficha_invocacoes.py.
import ficha_invocacoes
_FIV = ficha_invocacoes.trocas(LAYOUT, _FP["H"][ficha_pessoal.COR_DA_BARRA])
_ABA_IV = ficha_invocacoes.aplica(LAYOUT, _FIV)
print(f"a aba de invocações: {_ABA_IV['linhas']} linha(s), {_ABA_IV['colunas']} coluna(s), {len(_ABA_IV['celulas'])} celula(s), "
      f"{len(_ABA_IV['mescladas'])} mesclagem(ns), {sum(len(m['onde'].split()) for m in _ABA_IV['menus'])} faixa(s) de menu, "
      f"{len(_FIV['cartas'])} carta(s) em {len(_FIV['LUG'])} ficha(s); a DADOS_INVOC: {_FIV['aba_dados']['linhas']} linha(s), "
      f"{_FIV['aba_dados']['colunas']} coluna(s)")

# 01/10/2026: a INVOCACAO, o CATALOGO e a DADOS_INV saem da ficha, decisao do Mizuki quando o construir() estourou
# os seis minutos do Apps Script. Saem por ultimo: o GLOSSARIO nasce na posicao da INVOCACAO e usa os estilos do
# CATALOGO. A montagem para se alguma aba que fica ainda citar uma delas. Ver sem_invocacao.py.
import sem_invocacao
print(f"as abas que sairam da ficha: {', '.join(sem_invocacao.aplica(LAYOUT))}")

# a paleta e a fonte de corpo saem do estilo.py, que e o dono delas -- e ele
# ganhou as quatro cores desta versao na v0.1 (decisao do Mizuki: uma paleta so)
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "ficha"))
from estilo import CORPO, PT_VALOR, TEXTO

wb = Workbook()
wb.remove(wb.active)
# a fonte padrao do DOCUMENTO, e nao so das celulas com texto: sem isto o
# Excel/Sheets poe a dele em toda celula vazia que leve preenchimento, e foi
# assim que 3165 celulas voltaram em Arial 10 do Sheets.
wb._fonts[0] = Font(name=CORPO, size=PT_VALOR, color=TEXTO)

def monta_fonte(v):
    if not v:
        return None
    nome, tam, cor, neg, ital = v
    return Font(name=nome, size=tam, color=cor, bold=neg, italic=ital)

def monta_borda(v):
    if not v:
        return None
    return Border(**{lado: Side(style=est, color=cor)
                     for lado, (est, cor) in v.items()})

ESTILOS = []
for e in LAYOUT["estilos"]:
    fonte, fundo, bordas, alinha, fmt = e
    ESTILOS.append({
        "font": monta_fonte(fonte),
        "fill": PatternFill("solid", start_color=fundo, end_color=fundo) if fundo else None,
        "border": monta_borda(bordas),
        "alignment": (Alignment(horizontal=alinha[0], vertical=alinha[1],
                                wrap_text=alinha[2], textRotation=alinha[3])
                      if alinha else None),
        "number_format": fmt,
    })

for a in LAYOUT["abas"]:
    ws = wb.create_sheet(a["nome"])
    ws.sheet_state = a["estado"]
    ws.sheet_view.showGridLines = a["grade"]
    if a.get("altura_padrao"):
        ws.sheet_format.defaultRowHeight = a["altura_padrao"]
        ws.sheet_format.customHeight = True

    for cmin, cmax, larg in a["colunas_larg"]:
        for c in range(cmin, cmax + 1):
            ws.column_dimensions[L(c)].width = larg
    for lin, alt in a["linhas_alt"]:
        ws.row_dimensions[lin].height = alt

    # o valor ANTES da mesclagem: mesclar apaga o estilo de tudo que nao e o
    # canto, e ai o bloco abre branco
    for reg in a["celulas"]:
        coord, valor, ie = reg[0], reg[1], reg[2]
        cel = ws[coord]
        if valor is not None:
            # o quarto campo, quando existe, e a faixa de uma formula MATRICIAL:
            # sem ele ela volta como formula comum e o Sheets recalcula outra
            # coisa. Registro de tres campos continua valendo -- e a maioria.
            cel.value = ArrayFormula(reg[3], valor) if len(reg) > 3 else valor
        if ie is not None:
            st = ESTILOS[ie]
            if st["font"]:          cel.font = st["font"]
            if st["fill"]:          cel.fill = st["fill"]
            if st["border"]:        cel.border = st["border"]
            if st["alignment"]:     cel.alignment = st["alignment"]
            if st["number_format"]: cel.number_format = st["number_format"]

    for faixa in a["mescladas"]:
        ws.merge_cells(faixa)

    for m in a["menus"]:
        v = DataValidation(type=m["tipo"], formula1=m["formula"],
                           allow_blank=m["vazio_ok"],
                           showDropDown=not m["mostra_seta"])
        ws.add_data_validation(v)
        for parte in m["onde"].split():
            v.add(parte)

    for cf in a["condicional"]:
        dxf = DifferentialStyle(
            font=Font(color=cf["cor_texto"]) if cf["cor_texto"] else None,
            fill=PatternFill(bgColor=cf["fundo"]) if cf["fundo"] else None)
        ws.conditional_formatting.add(
            cf["onde"], Rule(type=cf["tipo"], dxf=dxf, formula=cf["formula"]))

    # o que so a aba nascida no gerador declara: a nota da caixa, e as linhas e colunas que fecham em grupo
    for coord, texto in a.get("notas", {}).items():
        ws[coord].comment = Comment(texto, "Projeto M")
    # um grupo dentro do outro soma um nivel: a extensao do painel de XP mora dentro do painel
    for l1, l2, fechado in a.get("grupos", {}).get("linhas", []):
        for r in range(l1, l2 + 1):
            ws.row_dimensions[r].outlineLevel = (ws.row_dimensions[r].outlineLevel or 0) + 1
            ws.row_dimensions[r].hidden = bool(ws.row_dimensions[r].hidden) or fechado
    for c1, c2, fechado in a.get("grupos", {}).get("colunas", []):
        for c in range(c1, c2 + 1):
            ws.column_dimensions[L(c)].outlineLevel = (ws.column_dimensions[L(c)].outlineLevel or 0) + 1
            ws.column_dimensions[L(c)].hidden = bool(ws.column_dimensions[L(c)].hidden) or fechado
    if a.get("grupos"):
        # o botao de fechar fica antes do grupo: em cima da lista de treino, e na coluna antes do painel
        ws.sheet_properties.outlinePr.summaryBelow = False
        ws.sheet_properties.outlinePr.summaryRight = False

    for im in a["imagens"]:
        caminho = os.path.join(AQUI, "arte", im["arquivo"])
        if not os.path.exists(caminho):
            print(f"  [aviso] falta a arte {im['arquivo']}")
            continue
        img = Img(caminho)
        img.width, img.height = im["larg"], im["alt"]
        img.anchor = ws.cell(row=im["lin"], column=im["col"]).coordinate
        ws.add_image(img)

saida = os.path.join(AQUI, "ficha-projeto-m-0.1.xlsx")
wb.save(saida)
print(f"ficha escrita: {saida}")
print(f"abas: {wb.sheetnames}")

# E o mesmo desenho como o script que constroi a planilha dentro do Sheets. Desde
# 14/09/2026 o Ficha.gs sai DAQUI, e nao do ficha/monta.py: a planilha viva e editada
# no Sheets, e esta pasta e a copia dela. Decisao do Mizuki no B18.
import emitir_gs
# o que o script precisa e a pasta de trabalho nao guarda do jeito dele: as notas, os grupos, o formato de
# numero, a cor de aviso e as faixas travadas da aba que as declara
def _extras(a):
    fmt = [[r[0], LAYOUT["estilos"][r[2]][4]] for r in a["celulas"] if r[2] is not None and LAYOUT["estilos"][r[2]][4]]
    def fundos(grupos):
        """[primeira, ultima, fechado, profundidade]: a profundidade e quantos grupos contem este, ele inclusive"""
        return [[g[0], g[1], g[2], sum(1 for o in grupos if o[0] <= g[0] and g[1] <= o[1])] for g in grupos]
    out = {"notas": sorted([k, v] for k, v in a.get("notas", {}).items()),
           "grupos": {"lin": fundos(a["grupos"]["linhas"]), "col": fundos(a["grupos"]["colunas"])} if a.get("grupos") else None,
           "formatos": fmt if a.get("grupos") else [], "condicional": a.get("condicional_gs", []),
           # 01/10/2026, a FICHA AMALDICOADA: as fileiras de cartas que sao copia da primeira, a validacao numa matriz so,
           # e, na DADOS_AM, as colunas que o script preenche para baixo a partir da primeira linha
           "copias": a.get("copias", []), "validacao_em_matriz": a.get("validacao_em_matriz", False),
           "abaixo": a.get("abaixo", []),
           # 02/10/2026, o menu rapido da FICHA: as linhas que a trava de formula do script deixa de fora
           "sem_trava": a.get("sem_trava", []),
           # 03/10/2026, a CARTEIRA: a caixa da foto, onde a caixa da paleta se ancora (ver moldura_foto.py)
           "foto": a.get("foto"),
           # 05/10/2026, a FICHA AMALDICOADA: a caixa que espelha a CARTEIRA (o nome da tecnica), para o aviso de quem
           # escreve por cima dela dizer onde se escreve
           "da_carteira": a.get("da_carteira", []),
           # 07/10/2026, a INVOCAÇÕES: a caixa de ± da vida de cada ficha, que o onEdit aplica (redutorDaInvocacao_)
           "redutores": a.get("redutores", []),
           # 07/10/2026: as caixas que nascem com conta e sao do jogador (o devolverConta_ nao as devolve)
           "livres": a.get("livres", [])}
    return {k: v for k, v in out.items() if v}

gs, celulas, pecas = emitir_gs.escrever(
    wb, [a["nome"] for a in LAYOUT["abas"]],
    extras={a["nome"]: _extras(a) for a in LAYOUT["abas"]},
    imgs={a["nome"]: a["imagens"] for a in LAYOUT["abas"]},
    arte_dir=os.path.join(AQUI, "arte"),
    limpa=LAYOUT["_meta"].get("largura_limpa"))
print(f"script escrito: {gs}")
print(f"  {celulas} células, {pecas} peças de arte embutidas")
# 05/10/2026: o texto das habilidades de Caminho e de Trilha, num script à parte (ver habilidades.py)
_hab_gs = os.path.join(os.path.dirname(AQUI), "apps-script", "Habilidades.gs")
_n, _t = habilidades.escreve_gs(_hab_gs)
print(f"script escrito: {_hab_gs}\n  {_n} habilidades, {_t // 1024} KB")
