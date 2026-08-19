# -*- coding: utf-8 -*-
"""Monta a ficha do Projeto M em .xlsx.

O .xlsx e o veiculo do layout; quem faz a ficha ser ficha e o Apps Script,
rodado uma vez no modelo. Nenhum numero esta escrito aqui: tudo vem do
catalogo-projeto-m.json e do decisoes-ficha.json.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpyxl import Workbook
from openpyxl.styles import Font
import estilo, dados, aba_ficha, aba_carteira, abas_resto, emitir_gs

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
DEC = json.load(open(os.path.join(RAIZ, "decisoes-ficha.json"), encoding="utf-8"))

wb = Workbook()
wb.remove(wb.active)

# a fonte padrao do documento, e nao so das celulas com texto: foi isso que
# deixou 4362 celulas em Calibri no prototipo
wb._fonts[0] = Font(name=estilo.CORPO, size=estilo.PT_VALOR, color=estilo.TEXTO)

ref = dados.monta(wb, CAT, DEC)
R   = aba_ficha.monta(wb, CAT, DEC, ref)
CAR = aba_carteira.monta(wb, CAT, DEC, ref, R)

# o nome mora na CARTEIRA, e a FICHA le dele. Um dado, um dono.
R["nome"].value = f"=IF(CARTEIRA!{CAR['nome'].coordinate}=\"\",\"\",CARTEIRA!{CAR['nome'].coordinate})"
abas_resto.mesa(wb, CAT, DEC, R)
abas_resto.quem_e(wb, CAT, DEC)

# o indice de celulas: quem quiser achar um campo da FICHA le daqui, em vez de
# decorar coordenada. Serve ao validador hoje e ao Apps Script depois.
dados.indice(wb, R)

# a TÉCNICA saiu: o bloco de feitiço dela ficou ruim e o Mizuki preferiu
# tirar até ele ser refeito. Está registrado no PENDENCIAS como B10.
ordem = ["CARTEIRA", "FICHA", "MESA", "QUEM É", "DADOS"]

# a ordem em que as abas abrem
for i, aba in enumerate([a for a in ordem if a != "DADOS"]):
    wb.move_sheet(aba, i - wb.sheetnames.index(aba))
saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ficha-projeto-m.xlsx")
wb.save(saida)

# e o mesmo desenho, agora como script que constrói a planilha por dentro
gs, celulas, pecas = emitir_gs.escrever(wb, ordem, R.get("_caixas"))
print(f"script escrito: {gs}")
print(f"  {celulas} células, {pecas} peças de arte embutidas")
print(f"ficha escrita: {saida}")
print(f"abas: {wb.sheetnames}")
