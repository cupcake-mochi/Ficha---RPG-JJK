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
import estilo, dados, aba_ficha, abas_resto

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
abas_resto.tecnica(wb, CAT, DEC, ref)
abas_resto.mesa(wb, CAT, DEC, R)
abas_resto.quem_e(wb, CAT, DEC)

# o indice de celulas: quem quiser achar um campo da FICHA le daqui, em vez de
# decorar coordenada. Serve ao validador hoje e ao Apps Script depois.
dados.indice(wb, R)

# a ordem em que as abas abrem
wb.move_sheet("FICHA", -wb.sheetnames.index("FICHA"))
saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ficha-projeto-m.xlsx")
wb.save(saida)
print(f"ficha escrita: {saida}")
print(f"abas: {wb.sheetnames}")
