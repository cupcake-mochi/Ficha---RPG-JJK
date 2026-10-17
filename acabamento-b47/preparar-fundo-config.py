"""Prepara correção do fundo padrão em espaços novos de CONFIGURAÇÃO, sem rede.

Somente células sem formatação explícita e sem valor são elegíveis. O formato
vem da construção canônica nativa, não de uma paleta inventada neste roteiro.
"""
import argparse
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('comparacao', Path(__file__).with_name('comparar-estudos.py'))
cmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp)


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def formats(folder, kind):
    cells, ids, sheets = {}, set(), set()
    for i in range(3):
        r = read(folder / 'formatos' / f'{kind}-{i}.json')['response']
        ids.add(r['spreadsheetId'])
        assert len(r['sheets']) == 1
        s = r['sheets'][0]
        assert s['properties']['title'] == 'CONFIGURAÇÃO'
        sheets.add(s['properties']['sheetId'])
        for grid in s['data']:
            for y, row in enumerate(grid.get('rowData', [])):
                for x, cell in enumerate(row.get('values', [])):
                    key = grid.get('startRow', 0) + y, grid.get('startColumn', 0) + x
                    assert key not in cells
                    cells[key] = cell.get('userEnteredFormat', {})
    assert len(ids) == len(sheets) == 1
    return cells, ids.pop(), sheets.pop()


def prepare(folder):
    current, dest, sheet_id = formats(folder, 'descartavel')
    canonical, source, _ = formats(folder, 'canonica')
    assert dest != source
    plan = read(folder / 'plano-depois.json')
    assert plan['spreadsheetId'] == dest
    values, _ = cmp.load(folder, 'depois', plan)
    selected, styles = set(), set()
    for y in range(1732, 2812):
        for x in range(16):
            old, new = current.get((y, x), {}), canonical.get((y, x), {})
            if not old and new.get('backgroundColor') and new.get('textFormat'):
                coord = cmp.L(x + 1) + str(y + 1)
                assert not values['CONFIGURAÇÃO'].get(coord, {}).get('userEnteredValue'), coord
                selected.add((y, x))
                styles.add(json.dumps(new, sort_keys=True))
    assert selected and len(styles) == 1, 'Formato-base ausente ou ambíguo'
    style = json.loads(styles.pop())
    # Unir trechos horizontais e depois linhas consecutivas com o mesmo trecho.
    spans = {}
    for y in range(1732, 2812):
        x = 0
        while x < 16:
            if (y, x) not in selected:
                x += 1
                continue
            begin = x
            while x < 16 and (y, x) in selected:
                x += 1
            spans.setdefault((begin, x), []).append(y)
    ranges = []
    for (x, xx), rows in sorted(spans.items()):
        start = prev = rows[0]
        for y in rows[1:] + [None]:
            if y is not None and y == prev + 1:
                prev = y
                continue
            ranges.append({'sheetId': sheet_id, 'startRowIndex': start,
                           'endRowIndex': prev + 1, 'startColumnIndex': x, 'endColumnIndex': xx})
            start = prev = y
    covered = {(y, x) for r in ranges for y in range(r['startRowIndex'], r['endRowIndex'])
               for x in range(r['startColumnIndex'], r['endColumnIndex'])}
    assert covered == selected
    return {'spreadsheetId': dest, 'fonte_canonica': source, 'celulas': len(selected),
            'requests': [{'repeatCell': {'range': r, 'cell': {'userEnteredFormat': style},
                                       'fields': 'userEnteredFormat'}} for r in ranges]}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidencias', required=True, type=Path)
    p.add_argument('--saida', required=True, type=Path)
    a = p.parse_args()
    result = prepare(a.evidencias)
    a.saida.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf8')
    print(json.dumps({'destino': result['spreadsheetId'], 'celulas': result['celulas'], 'pedidos': len(result['requests'])}))
