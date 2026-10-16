#!/usr/bin/env python3
"""Normaliza leituras CellData nativas, sem rede, sem credenciais e sem escrita Google."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from openpyxl.utils.cell import range_boundaries, get_column_letter as L
from migracao import sha


def a1(value):
    sheet, area = value.rsplit('!', 1)
    if sheet.startswith("'") and sheet.endswith("'"):
        sheet = sheet[1:-1].replace("''", "'")
    return sheet, area


def fatiar(metadata, ranges, limite=8000):
    sheets = {s['properties']['title']: s['properties'] for s in metadata['sheets']}
    chunks = []
    for name, areas in ranges.items():
        props = sheets[name]; grid = props['gridProperties']
        for area in areas:
            c, r, cc, rr = range_boundaries(area)
            cc = min(cc, grid['columnCount']); rr = min(rr, grid['rowCount'])
            if c > cc or r > rr: continue  # inexistência provada pelos metadados
            if cc-c+1 > limite: raise ValueError('Faixa larga demais')
            step = max(1, limite//(cc-c+1))
            for start in range(r, rr+1, step):
                end = min(start+step-1, rr)
                quoted = "'"+name.replace("'", "''")+"'"
                chunks.append({'arquivo': f'{len(chunks):04d}.json',
                               'range': f'{quoted}!{L(c)}{start}:{L(cc)}{end}',
                               'sheetId': props['sheetId']})
    return {'spreadsheetId': metadata['spreadsheetId'], 'metadata_sha256': sha(metadata),
            'limite_celulas_por_bloco': limite, 'chunks': chunks}


def normalizar(metadata, plan, blocks, backup_id, captured_at):
    if plan['metadata_sha256'] != sha(metadata): raise ValueError('Metadados divergentes')
    dest = metadata['spreadsheetId']
    if plan['spreadsheetId'] != dest or not backup_id or backup_id == dest:
        raise ValueError('Destino/backup inválido')
    names = [c['arquivo'] for c in plan['chunks']]
    if len(set(names)) != len(names) or set(blocks) != set(names):
        raise ValueError('Leituras incompletas ou repetidas')
    cells = {}; ranges = {}
    for chunk in plan['chunks']:
        block = blocks[chunk['arquivo']]; response = block['response']
        if block['range'] != chunk['range'] or response.get('spreadsheetId') != dest:
            raise ValueError('Leitura de outro destino/faixa')
        name, area = a1(chunk['range']); c, r, cc, rr = range_boundaries(area)
        sheets = response.get('sheets', [])
        if len(sheets) != 1 or sheets[0]['properties']['title'] != name or sheets[0]['properties']['sheetId'] != chunk['sheetId']:
            raise ValueError('Aba não comprovada pela resposta')
        data = sheets[0].get('data')
        if not isinstance(data, list) or len(data) != 1: raise ValueError('GridData ausente ou ambíguo')
        grid = data[0]; y0 = grid.get('startRow', 0); x0 = grid.get('startColumn', 0)
        if not r-1 <= y0 <= rr-1 or not c-1 <= x0 <= cc-1:
            raise ValueError('Origem fora da faixa')
        if y0+len(grid.get('rowData', [])) > rr:
            raise ValueError('Linhas fora da faixa')
        dest_cells = cells.setdefault(name, {})
        for dy, row in enumerate(grid.get('rowData', [])):
            for dx, cell in enumerate(row.get('values', [])):
                y, x = y0+dy+1, x0+dx+1
                if y > rr or x > cc: raise ValueError('Célula fora da faixa')
                coord = L(x)+str(y)
                value = {k: deepcopy(cell[k]) for k in ('userEnteredValue', 'note') if k in cell}
                if coord in dest_cells: raise ValueError('Célula repetida em blocos')
                if value: dest_cells[coord] = value
        ranges.setdefault(name, []).append(area)
    return {'spreadsheetId': dest, 'backup_id': backup_id, 'captured_at': captured_at,
            'metadata': metadata, 'ranges': ranges, 'cells': cells}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('metadata', 'faixas', 'saida'): ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--partes', type=Path); ap.add_argument('--backup-id'); ap.add_argument('--captured-at')
    args = ap.parse_args(); metadata = json.loads(args.metadata.read_text())
    ranges = json.loads(args.faixas.read_text())['faixas_necessarias']; plan = fatiar(metadata, ranges)
    if args.partes:
        if not args.captured_at: ap.error('--captured-at é obrigatório para normalizar')
        blocks = {p.name: json.loads(p.read_text()) for p in args.partes.glob('*.json')}
        result = normalizar(metadata, plan, blocks, args.backup_id, args.captured_at)
    else: result = plan
    args.saida.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n')
    print(args.saida)


if __name__ == '__main__': main()
