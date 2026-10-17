"""Audita referências aos estudos em leituras nativas completas; não escreve no Google.

As entradas contêm dados privados. A saída resume contagens, hashes e locais de
referências; nunca publica valores ou fórmulas do personagem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from openpyxl.utils.cell import get_column_letter as L

ROOT = Path(__file__).resolve().parents[1]
STUDIES = {'ESTUDO CAMPANHA', 'ESTUDO CUSTOM', 'ESTUDO 3B', 'ESTUDO 3C'}


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leaves(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, path + '/' + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from leaves(child, path + '/' + str(i))
    else:
        yield path, value


def arguments(text, start):
    """Lê argumentos de uma chamada, respeitando parênteses e strings Sheets."""
    depth, quoted, begin, result, i = 0, False, start, [], start
    while i < len(text):
        char = text[i]
        if char == '"':
            if quoted and i + 1 < len(text) and text[i + 1] == '"':
                i += 2
                continue
            quoted = not quoted
        elif not quoted:
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    return result + [text[begin:i].strip()], i
                depth -= 1
            elif char in ',;' and depth == 0:
                result.append(text[begin:i].strip())
                begin = i + 1
        i += 1
    raise ValueError('Chamada incompleta')


def indirect_targets(formula, retained):
    """Aceita somente INDIRECT(SWITCH(...)) com todos os destinos literais.

    O seletor pode variar, mas não compõe o endereço: cada resultado/default
    precisa ser uma faixa A1 explícita em uma aba preservada.
    """
    targets = set()
    for match in re.finditer(r'\b(?:INDIRECT|INDIRETO)\s*\(', formula, re.I):
        args, _ = arguments(formula, match.end())
        if len(args) != 1:
            return None
        switch = re.match(r'^SWITCH\s*\(', args[0], re.I)
        if not switch:
            return None
        cases, end = arguments(args[0], switch.end())
        if end != len(args[0]) - 1 or len(cases) < 3:
            return None
        results = cases[2::2] + ([cases[-1]] if len(cases) % 2 == 0 else [])
        for value in results:
            ref = re.fullmatch(r'''"'((?:[^']|'')+)'!\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?"''', value)
            if not ref or ref[1].replace("''", "'") not in retained:
                return None
            targets.add(ref[1].replace("''", "'"))
    return sorted(targets)


def audit(folder, specs):
    meta = read(folder / 'metadata-integral.json')['updatedSpreadsheet']
    plan = read(folder / 'plano-antes.json')
    assert meta['spreadsheetId'] == plan['spreadsheetId'], 'Destino divergente'
    ids = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    assert STUDIES <= ids.keys(), 'Quatro estudos não comprovados'
    study_ids = {ids[n] for n in STUDIES}
    names = re.compile('|'.join(re.escape(n) for n in sorted(STUDIES)), re.I)
    gid = re.compile(r'(?:gid=|sheetId[=: ]+)(\d+)', re.I)
    findings = []
    dynamic = []
    resolved = []
    errors = []
    counts = dict(cells=0, formulas=0, validations=0, notes=0)
    blocks = []
    by_sheet = {}
    for chunk in plan['chunks']:
        path = folder / 'antes' / chunk['arquivo']
        block = read(path)
        response = block['response']
        assert block['range'] == chunk['range']
        assert response['spreadsheetId'] == plan['spreadsheetId']
        assert len(response['sheets']) == 1
        sheet = response['sheets'][0]
        name = sheet['properties']['title']
        assert sheet['properties']['sheetId'] == chunk['sheetId'] == ids[name]
        blocks.append({'arquivo': chunk['arquivo'], 'sha256': digest(path)})
        by_sheet.setdefault(name, dict(formulas=0, literals=0, notes=0, validations=0))
        for grid in sheet.get('data', []):
            for y, row in enumerate(grid.get('rowData', [])):
                for x, cell in enumerate(row.get('values', [])):
                    coord = L(grid.get('startColumn', 0) + x + 1) + str(grid.get('startRow', 0) + y + 1)
                    v = cell.get('userEnteredValue', {})
                    formula = v.get('formulaValue', '')
                    counts['cells'] += 1
                    counts['formulas'] += bool(formula)
                    counts['notes'] += bool(cell.get('note'))
                    counts['validations'] += bool(cell.get('dataValidation'))
                    by_sheet[name]['formulas'] += bool(formula)
                    by_sheet[name]['literals'] += bool(v) and not bool(formula)
                    by_sheet[name]['notes'] += bool(cell.get('note'))
                    by_sheet[name]['validations'] += bool(cell.get('dataValidation'))
                    if cell.get('effectiveValue', {}).get('errorValue'):
                        errors.append([name, coord])
                    if name in STUDIES:
                        continue
                    if re.search(r'\b(?:INDIRECT|INDIRETO)\s*\(', formula, re.I):
                        targets = indirect_targets(formula, ids.keys() - STUDIES)
                        if targets is None:
                            dynamic.append([name, coord])
                        else:
                            resolved.append({'aba': name, 'celula': coord, 'destinos': targets})
                    # Inclui menus, fórmulas, notas e hyperlinks, sem divulgar conteúdo.
                    for field, value in leaves({k: v for k, v in cell.items() if k != 'effectiveValue'}):
                        if isinstance(value, str) and (names.search(value) or any(int(m) in study_ids for m in gid.findall(value))):
                            findings.append({'aba': name, 'celula': coord, 'campo': field})
    assert set(by_sheet) == set(ids), 'Leitura incompleta de abas'
    for key, value in leaves({k: v for k, v in meta.items() if k != 'sheets'}):
        if key.endswith('/sheetId') and value in study_ids:
            findings.append({'metadado': key, 'tipo': 'sheetId de estudo'})
        elif isinstance(value, str) and names.search(value):
            findings.append({'metadado': key, 'tipo': 'nome de estudo'})
    for sheet in meta['sheets']:
        if sheet['properties']['title'] in STUDIES:
            continue
        for key, value in leaves(sheet):
            if key.endswith('/sheetId') and value in study_ids:
                findings.append({'aba': sheet['properties']['title'], 'metadado': key})
            elif isinstance(value, str) and (names.search(value) or any(int(m) in study_ids for m in gid.findall(value))):
                findings.append({'aba': sheet['properties']['title'], 'metadado': key})
    script_hits = []
    scripts = []
    for path in sorted((ROOT / 'apps-script').glob('*.gs')):
        source = path.read_text(encoding='utf8')
        scripts.append({'arquivo': path.name, 'sha256': digest(path)})
        for number, line in enumerate(source.splitlines(), 1):
            if names.search(line):
                script_hits.append([path.name, number])
    canonical = read(specs)
    assert len(canonical) == 22 and not STUDIES.intersection(s['nome'] for s in canonical)
    return {
        'resultado': 'SEM_REFERENCIAS_ESTATICAS' if not (findings or script_hits or errors or dynamic) else 'REVISAR',
        'destino': plan['spreadsheetId'], 'abas': len(ids),
        'estudos': [{'nome': n, 'sheetId': ids[n], **by_sheet[n]} for n in sorted(STUDIES)],
        'contagens': counts, 'referencias_entrantes': findings,
        'referencias_indiretas_a_revisar': dynamic, 'referencias_scripts': script_hits,
        'referencias_indiretas_resolvidas': resolved,
        'erros_formula': errors, 'intervalos_nomeados': len(meta.get('namedRanges', [])),
        'abas_canonicas': len(canonical), 'blocos': blocks, 'scripts': scripts,
        'limite': 'Ausência estática não substitui o ensaio nativo de remoção e comparação integral; conteúdo dos estudos permanece preservado na cópia/backup.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidencias', required=True, type=Path)
    p.add_argument('--specs', required=True, type=Path)
    p.add_argument('--saida', required=True, type=Path)
    a = p.parse_args()
    result = audit(a.evidencias, a.specs)
    a.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: result[k] for k in ('resultado', 'abas', 'contagens', 'referencias_entrantes', 'referencias_indiretas_a_revisar', 'referencias_scripts', 'erros_formula')}, ensure_ascii=False))
    sys.exit(0 if result['resultado'] == 'SEM_REFERENCIAS_ESTATICAS' else 1)
