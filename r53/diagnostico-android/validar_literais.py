"""Conferência completa de A:D após converter constantes, sem dados no relatório."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'nuvem-b47/saidas/diagnostico-mobile-20261023/c-compactacao'


def cells(doc):
    result = {}
    assert doc['spreadsheetId'] == '1VO61vXu8FjsDvc27c5c_ke93be-4Ta2rGaToDCv0Wgc'
    for sheet in doc['sheets']:
        assert sheet['properties']['title'] == 'ANALISE'
        for block in sheet.get('data', []):
            for row, data in enumerate(block.get('rowData', []), block.get('startRow', 0) + 1):
                for col, cell in enumerate(data.get('values', []), block.get('startColumn', 0)):
                    result[chr(65 + col) + str(row)] = cell
    return result


def main():
    before, after = {}, {}
    for start in (1, 4001, 8001, 12001, 16001):
        before.update(cells(json.loads((PRIVATE / f'analise-antes-{start}.json').read_text())))
        after.update(cells(json.loads((PRIVATE / f'analise-depois-{start}.json').read_text())))
    converted = 0
    for address in before.keys() | after.keys():
        old, new = before.get(address, {}), after.get(address, {})
        assert old.get('effectiveValue') == new.get('effectiveValue'), address + ': valor'
        assert 'errorValue' not in new.get('effectiveValue', {}), address
        for field in ('note', 'dataValidation'):
            assert old.get(field) == new.get(field), address + ': ' + field
        if old.get('userEnteredValue') != new.get('userEnteredValue'):
            formula = old.get('userEnteredValue', {}).get('formulaValue', '')
            assert address.startswith('C') and re.fullmatch(r'="(?:[^"]|"")*"', formula), address
            assert new.get('userEnteredValue') == {'stringValue': old['effectiveValue']['stringValue']}, address
            converted += 1
    keys = [cell['effectiveValue']['stringValue'] for addr, cell in after.items()
            if addr.startswith('A') and addr != 'A1' and cell.get('effectiveValue', {}).get('stringValue')]
    assert len(keys) == len(set(keys)) == 18393
    assert converted == 15869
    result = dict(convertidas=converted, valores_diferentes=0, erros=0, chaves=len(keys),
                  chaves_unicas=len(set(keys)), total_celulas_conferidas=len(before.keys() | after.keys()),
                  preservacao='Valores e tipos de A:D, notas e validações idênticos ao snapshot')
    Path(__file__).with_name('ANALISE-LITERAL-2026-10-23.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
