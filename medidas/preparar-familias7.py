"""Migração delimitada da capacidade de Famílias. Não usa rede nem Excel."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT.parent/'evidencias-3b'
B = json.loads((EVID/'layout-familias5-pacote.json').read_text())['layout']
A = json.loads((EVID/'layout-familias7-pacote.json').read_text())['layout']
before = {s['nome']: {c[0]: c[1] for c in s['celulas']} for s in B['abas']}
after = {s['nome']: s for s in A['abas']}
backup = json.loads((EVID/'familias7-antes-nativo.json').read_text())
live = {}
for obj in backup.values():
    for sheet in obj['sheets']:
        for block in sheet.get('data', []):
            for r, row in enumerate(block.get('rowData', []), block.get('startRow', 0)+1):
                for c, cell in enumerate(row.get('values', []), block.get('startColumn', 0)+1):
                    live[sheet['properties']['title'], r, c] = cell
ids = {'INVOCAÇÕES': 161192554, 'DADOS_INVOC': 1471151297, 'ANALISE': 1893369489}


def col(n):
    out = ''
    while n:
        n, r = divmod(n-1, 26)
        out = chr(65+r)+out
    return out


def lc(coord):
    text, row = re.fullmatch(r'([A-Z]+)(\d+)', coord).groups()
    return int(row), sum((ord(c)-64)*26**i for i, c in enumerate(text[::-1]))


def grid(name, r, c, rr=None, cc=None):
    return dict(sheetId=ids[name], startRowIndex=r-1, endRowIndex=rr or r,
                startColumnIndex=c-1, endColumnIndex=cc or c)


def pt(s):
    quoted, out = False, ''
    for i, ch in enumerate(s):
        if ch == '"':
            quoted = not quoted
        if not quoted:
            if ch == ',': ch = ';'
            elif ch == '.' and s[i-1:i].isdigit() and s[i+1:i+2].isdigit(): ch = ','
        out += ch
    return out


def uv(value):
    if value is None or value == '': return {}
    if isinstance(value, bool): return {'boolValue': value}
    if isinstance(value, (int, float)): return {'numberValue': value}
    return {'formulaValue': pt(value)} if value.startswith('=') else {'stringValue': value.lstrip("'")}


def canon(value):
    value = value or {}
    if value.get('formulaValue'):
        return {'formulaValue': re.sub(r"'([A-Za-z_][A-Za-z_0-9]*)'!", r'\1!', value['formulaValue'])}
    return {} if value.get('stringValue') == '' else value


req, guards = [], []
req.append({'updateSheetProperties': {'properties': {'sheetId': ids['DADOS_INVOC'], 'gridProperties': {'columnCount': 465}},
                                      'fields': 'gridProperties.columnCount'}})
req.append({'updateSheetProperties': {'properties': {'sheetId': ids['ANALISE'], 'gridProperties': {'rowCount': after['ANALISE']['linhas']+2}},
                                      'fields': 'gridProperties.rowCount'}})
for i in range(12):
    name, r, c = 'INVOCAÇÕES', 48+198*(i % 6), 15+19*(i//6)
    for row in (r+1, r+2):
        for column in range(c, c+5):
            cell = live.get((name, row, column), {})
            if canon(cell.get('userEnteredValue')) or cell.get('note'):
                raise ValueError(f'Conteúdo na folga a reaproveitar: {col(column)}{row}')
    inp = live[name, r, c]['userEnteredFormat']
    head = live[name, r-1, c]['userEnteredFormat']
    req.append({'unmergeCells': {'range': grid(name, r, c, r+2, c+4)}})
    req.append({'setDataValidation': {'range': grid(name, r+1, c, r+1, c+4)}})
    for rr, fmt in ((r, inp), (r+1, head), (r+2, inp)):
        req.append({'repeatCell': {'range': grid(name, rr, c, rr, c+4), 'cell': {'userEnteredFormat': fmt},
                                   'fields': 'userEnteredFormat'}})
    for j, (start, end) in enumerate(((c, c+1), (c+2, c+4)), 6):
        for rr in (r+1, r+2):
            req.append({'mergeCells': {'range': grid(name, rr, start, rr, end), 'mergeType': 'MERGE_ALL'}})
        coord = col(start)+str(r+1)
        note = after[name]['notas'][coord]
        for rr, value in ((r+1, 'FAMÍLIA '+str(j)), (r+2, None)):
            req.append({'updateCells': {'start': {'sheetId': ids[name], 'rowIndex': rr-1, 'columnIndex': start-1},
                                         'rows': [{'values': [{'userEnteredValue': uv(value), 'note': note}]}],
                                         'fields': 'userEnteredValue,note'}})
        req.append({'setDataValidation': {'range': grid(name, r+2, start), 'rule': {'condition': {
            'type': 'ONE_OF_RANGE', 'values': [{'userEnteredValue': '=DADOS_INVOC!$BS$2:$BS$10'}]}, 'showCustomUi': True}}})
    if i < 6:
        for rr, px in ((r,32), (r+1,20), (r+2,25)):
            req.append({'updateDimensionProperties': {'range': {'sheetId': ids[name], 'dimension': 'ROWS',
                                        'startIndex': rr-1, 'endIndex': rr}, 'properties': {'pixelSize': px}, 'fields': 'pixelSize'}})

for name in ('DADOS_INVOC', 'ANALISE'):
    for coord, value, *_ in after[name]['celulas']:
        old = before[name].get(coord)
        if uv(old) == uv(value): continue
        r, c = lc(coord)
        actual = live.get((name, r, c), {}).get('userEnteredValue')
        outside = (name == 'DADOS_INVOC' and c > 463) or (name == 'ANALISE' and r > 7390)
        if not outside and canon(actual) != canon(uv(old)):
            raise ValueError(f'Guarda divergente: {name} {coord}: {actual} != {uv(old)}')
        guards.append([name, coord, uv(old), uv(value)])
        req.append({'updateCells': {'start': {'sheetId': ids[name], 'rowIndex': r-1, 'columnIndex': c-1},
                                    'rows': [{'values': [{'userEnteredValue': uv(value)}]}], 'fields': 'userEnteredValue'}})
req.append({'copyPaste': {'source': grid('ANALISE', 7388,1,7388,4), 'destination': grid('ANALISE',7389,1,7412,4),
                          'pasteType': 'PASTE_FORMAT', 'pasteOrientation': 'NORMAL'}})
out = EVID/'familias7-pedidos'
out.mkdir(exist_ok=True)
chunks, batch, size = [], [], 0
for item in req:
    length = len(json.dumps(item, ensure_ascii=False))
    if batch and (size+length > 55000 or len(batch) >= 120):
        chunks.append(batch); batch, size = [], 0
    batch.append(item); size += length
if batch: chunks.append(batch)
for i, chunk in enumerate(chunks):
    (out/f'{i:03}.json').write_text(json.dumps(chunk, ensure_ascii=False, separators=(',', ':')))
(EVID/'familias7-manifesto.json').write_text(json.dumps({'requests':len(req), 'lotes':len(chunks), 'guards':guards}, ensure_ascii=False))
print(json.dumps({'requests':len(req), 'lotes':len(chunks), 'guards':len(guards)}))
