"""Monta mesclagens já validadas sem procurar duplicatas a cada inserção."""
from openpyxl.worksheet.merge import MergedCellRange


def aplica(ws, faixas):
    # Mesmo procedimento de Worksheet.merge_cells, com inserção direta no
    # conjunto. O layout já declara faixas únicas, sem sobreposição. A busca
    # de inclusão do MultiCellRange.add tornava 28 mil mesclagens quadráticas.
    for faixa in faixas:
        mescla = MergedCellRange(ws, faixa)
        ws.merged_cells.ranges.add(mescla)
        ws._clean_merge_range(mescla)
