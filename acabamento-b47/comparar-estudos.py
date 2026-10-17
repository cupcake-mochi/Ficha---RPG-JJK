"""Compara snapshots completos, permitindo exclusivamente retirar os quatro estudos."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from openpyxl.utils.cell import get_column_letter as L

STUDIES = {'ESTUDO CAMPANHA', 'ESTUDO CUSTOM', 'ESTUDO 3B', 'ESTUDO 3C'}
FIELDS = ('userEnteredValue', 'effectiveValue', 'note', 'dataValidation', 'hyperlink', 'textFormatRuns')


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def load(folder, phase, plan):
    result, errors = {}, []
    files = {p.name for p in (folder / phase).glob('[0-9]*.json')}
    assert files == {c['arquivo'] for c in plan['chunks']}, 'Blocos incompletos/extras'
    for chunk in plan['chunks']:
        b = read(folder / phase / chunk['arquivo'])
        assert b['range'] == chunk['range']
        r = b['response']
        assert r['spreadsheetId'] == plan['spreadsheetId']
        assert len(r['sheets']) == 1
        s = r['sheets'][0]
        assert s['properties']['sheetId'] == chunk['sheetId']
        name = s['properties']['title']
        target = result.setdefault(name, {})
        for grid in s.get('data', []):
            for y, row in enumerate(grid.get('rowData', [])):
                for x, cell in enumerate(row.get('values', [])):
                    coord = L(grid.get('startColumn', 0) + x + 1) + str(grid.get('startRow', 0) + y + 1)
                    value = {k: cell[k] for k in FIELDS if cell.get(k) not in (None, {}, '', [])}
                    if value:
                        assert coord not in target, 'Célula duplicada'
                        target[coord] = value
                    if cell.get('effectiveValue', {}).get('errorValue'):
                        errors.append([name, coord])
    return result, errors


def compare(folder, phase, plan_after, removed, contextual_specs=None, timezone_proof=None, metadata=None):
    before, _ = load(folder, 'antes', read(folder / 'plano-antes.json'))
    after, errors = load(folder, phase, plan_after)
    expected = {n: v for n, v in before.items() if n not in (STUDIES if removed else set())}
    differences = []
    contextual = {}
    accepted = []
    temporal = None
    if timezone_proof:
        proof = read(timezone_proof)
        meta = read(metadata) if metadata else {}
        assert proof['resultado'] == 'OK' and proof['destino'] == plan_after['spreadsheetId']
        assert meta.get('spreadsheetId') == plan_after['spreadsheetId']
        assert meta['properties']['timeZone'] == proof['fuso_final'] == 'America/Sao_Paulo'
        assert proof['celula'] == 'CARTEIRA!AH3' and proof['formula_preservada']
        formula = '=\"Emitida \"&TEXT(TODAY();\"dd.mm.yyyy\")'
        assert proof['formula'] == formula and proof['valor_final'] == proof['esperado']
        assert before['CARTEIRA']['AH3']['userEnteredValue']['formulaValue'] == formula
        assert after['CARTEIRA']['AH3']['userEnteredValue']['formulaValue'] == formula
        temporal = proof
    if contextual_specs:
        specs = read(contextual_specs)
        spec = next(s for s in specs if s['nome'] == 'INVOCAÇÕES')['notas_contextuais']
        for i, coord in enumerate(spec['destinos']):
            source_coord = L(spec['coluna']) + str(spec['primeira'] + i)
            text = after[spec['fonte']].get(source_coord, {}).get('effectiveValue', {}).get('stringValue')
            if text:
                contextual[('INVOCAÇÕES', coord)] = text
    for name in expected.keys() | after.keys():
        a, b = expected.get(name, {}), after.get(name, {})
        if name not in expected or name not in after:
            differences.append({'aba': name, 'campo': 'presenca'})
        for coord in a.keys() | b.keys():
            for field in FIELDS:
                if a.get(coord, {}).get(field) != b.get(coord, {}).get(field):
                    delta = {'aba': name, 'celula': coord, 'campo': field}
                    if (field == 'note' and not a.get(coord, {}).get('note')
                            and b.get(coord, {}).get('note') == contextual.get((name, coord))
                            and (name, coord) in contextual):
                        accepted.append(delta)
                    elif (temporal and name == 'CARTEIRA' and coord == 'AH3' and field == 'effectiveValue'
                            and a.get(coord, {}).get(field) == {'stringValue': temporal['valor_anterior']}
                            and b.get(coord, {}).get(field) == {'stringValue': temporal['esperado']}):
                        delta['motivo'] = 'Fuso nativo alinhado ao manifesto, com fórmula temporal preservada'
                        accepted.append(delta)
                    else:
                        differences.append(delta)
    analysis = after.get('ANALISE', {})
    value = lambda c: next(iter(analysis.get(c, {}).get('effectiveValue', {}).values()), None)
    keys = [value('A' + str(r)) for r in range(2, 8192)]
    version = value('B2')
    # O contrato exporta formato.versao como texto; admite também número nativo.
    contract_ok = version in (11, '11') and len(keys) == len(set(keys)) == 8190 and all(keys)
    compact = json.dumps(after, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return {'resultado': 'OK' if not (differences or errors) and contract_ok else 'FALHA',
            'destino': plan_after['spreadsheetId'], 'fase': phase, 'abas': len(after),
            'estudos_retirados': sorted(STUDIES) if removed else [],
            'campos_conferidos': FIELDS, 'celulas_preservadas': sum(map(len, expected.values())),
            'notas_preservadas': sum(bool(c.get('note')) for s in expected.values() for c in s.values()),
            'validacoes_preservadas': sum(bool(c.get('dataValidation')) for s in expected.values() for c in s.values()),
            'ajudas_contextuais_acrescentadas_conferidas': [d for d in accepted if d['campo'] == 'note'],
            'ajuste_temporal_conferido': [d for d in accepted if d['campo'] == 'effectiveValue'],
            'diferencas': differences, 'erros_formula': errors,
            'analise': {'versao': version, 'chaves': len(keys), 'unicas': len(set(keys)), 'contrato_ok': contract_ok},
            'snapshot_depois_sha256': hashlib.sha256(compact.encode()).hexdigest()}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidencias', required=True, type=Path)
    p.add_argument('--fase', required=True)
    p.add_argument('--plano', required=True, type=Path)
    p.add_argument('--retirados', action='store_true')
    p.add_argument('--notas-contextuais', type=Path, help='Aceita somente acréscimo em nota vazia, idêntico à fonte canônica efetiva')
    p.add_argument('--prova-fuso', type=Path, help='Exceção estrita somente para a emissão TODAY da carteira')
    p.add_argument('--metadata', type=Path, help='Metadados finais atuais, obrigatórios com --prova-fuso')
    p.add_argument('--saida', required=True, type=Path)
    a = p.parse_args()
    r = compare(a.evidencias, a.fase, read(a.plano), a.retirados, a.notas_contextuais, a.prova_fuso, a.metadata)
    a.saida.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(r, ensure_ascii=False))
    sys.exit(0 if r['resultado'] == 'OK' else 1)
