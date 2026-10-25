"""Confere leituras CellData: todas as 108 vagas, duplicatas e autonomia.

Recebe somente a pasta privada com familias-0.json até familias-11.json.
Planilhas vazias podem omitir rowData/values: isso representa células vazias.
"""
import json
import sys
from pathlib import Path


def conferir(folder):
    checks = 0
    failures = []
    for scenario in range(12):
        obj = json.loads((folder/f'familias-{scenario}.json').read_text())
        cells = {}
        for sheet in obj['response']['sheets']:
            for block in sheet.get('data', []):
                for i, row in enumerate(block.get('rowData', [])):
                    for j, cell in enumerate(row.get('values', [])):
                        value = cell.get('effectiveValue', {})
                        cells[block.get('startRow',0)+i, block.get('startColumn',0)+j] = next(iter(value.values()), '')
        for i, exp in enumerate(obj['expected']):
            columns = list(range(141,146))+list(range(463,467))+list(range(211,214))+[467,468]
            expected = exp['f']+[exp['count'],exp['rep'],exp['max'],exp['mode'],exp['free']]
            for col, value in zip(columns, expected):
                actual = cells.get((i+1,col), '')
                checks += 1
                if actual != value:
                    failures.append(dict(cenario=scenario, entidade=i+1, coluna=col+1, esperado=value, obtido=actual))
    result = dict(cenarios=12, entidades=12, vagas=108, verificacoes=checks, falhas=failures)
    print(json.dumps(result, ensure_ascii=False))
    return not failures


if __name__ == '__main__':
    raise SystemExit(0 if conferir(Path(sys.argv[1])) else 1)
