"""Auditoria e plano offline de origens da ANALISE; nunca escreve no Google.

Compara modelos antes/depois e exige que a única mudança seja C. Em fichas
existentes, localiza por chave, confere B e D e recusa divergências. Intervalos
e fórmulas com múltiplas dependências não são reduzidos à primeira referência.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ficha-v01'))
from referencias_origem import referencias, texto
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import coordinate_to_tuple, range_boundaries


def valor(cell):
    v = cell.get('userEnteredValue', {})
    return next((v[k] for k in ('formulaValue', 'stringValue', 'numberValue', 'boolValue') if k in v), '')


def linhas_modelo(modelo):
    tab = next(a for a in modelo['layout']['abas'] if a['nome'] == 'ANALISE')
    rows = {}
    for pos, value, *_ in tab['celulas']:
        r, c = coordinate_to_tuple(pos)
        if c <= 4:
            rows.setdefault(r, [''] * 4)[c - 1] = value
    return rows


def linhas_snapshot(pacotes):
    rows = {}
    sid = None
    for snapshot in pacotes:
        for tab in snapshot['sheets']:
            if tab['properties']['title'] != 'ANALISE':
                continue
            actual = tab['properties']['sheetId']
            if sid is not None and actual != sid:
                raise ValueError('Snapshots de abas diferentes')
            sid = actual
            for block in tab.get('data', []):
                if block.get('startColumn', 0) != 0:
                    raise ValueError('A leitura deve conter A:D')
                for r, row in enumerate(block.get('rowData', []), block.get('startRow', 0) + 1):
                    if r in rows:
                        raise ValueError('Linhas sobrepostas no snapshot')
                    rows[r] = (row.get('values', []) + [{}] * 4)[:4]
    if sid is None:
        raise ValueError('ANALISE não encontrada')
    return sid, rows


def assinatura_formula(formula):
    if not isinstance(formula, str) or not formula.startswith('='):
        raise ValueError('B deve continuar sendo fórmula')
    # O Sheets usa ; e remove aspas dispensáveis de nomes de aba. TEXT e
    # matrizes são preservados; só separadores de argumentos são normalizados.
    tokens, stack = [], []
    for token in Tokenizer(formula).items:
        if token.type in ('FUNC', 'ARRAY', 'PAREN'):
            if token.subtype == 'OPEN':
                stack.append(token.type)
            elif token.subtype == 'CLOSE':
                if stack:
                    stack.pop()
        if token.type == 'WHITE-SPACE':
            continue
        if token.type == 'OPERAND' and token.subtype == 'RANGE':
            r = referencias(token.value)
            if r and len(r) == 1:
                tokens.append(('REF', r[0].aba, r[0].endereco.replace('$', '')))
                continue
        if token.type == 'SEP' and token.value in (',', ';') and (not stack or stack[-1] != 'ARRAY'):
            tokens.append(('SEP',))
        else:
            tokens.append((token.type, token.subtype, token.value))
    return tokens


def dependencias(formula):
    refs, unknown = [], []
    if not isinstance(formula, str) or not formula.startswith('='):
        return refs, unknown
    for t in Tokenizer(formula).items:
        if t.type == 'OPERAND' and t.subtype == 'RANGE':
            r = referencias(t.value)
            if r and len(r) == 1:
                p = (r[0].aba, r[0].endereco.replace('$', ''))
                if p not in refs:
                    refs.append(p)
            elif t.value not in unknown:
                unknown.append(t.value)
    return refs, unknown


def auditar(rows):
    """Separação estrutural: não certifica o significado de cada fórmula."""
    count = Counter()
    mismatches, compound, others = [], [], []
    keys = set()
    for row, values in sorted(rows.items()):
        if row == 1:
            continue
        key, b, c, part = values
        if not key:
            raise ValueError(f'Chave ausente na linha {row}')
        if key in keys:
            raise ValueError(f'Chave duplicada: {key}')
        keys.add(key)
        refs, unknown = dependencias(b)
        declared = referencias(c)
        if len(refs) == 1 and ':' not in refs[0][1] and not unknown:
            count['referencia_unica'] += 1
            target = [(r.aba, r.endereco.replace('$', '')) for r in declared] if declared is not None else None
            if target != refs:
                mismatches.append(dict(linha=row, chave=key, lida=refs, declarada=texto(c)))
        elif refs:
            count['multiplas_ou_intervalos'] += 1
            compound.append(dict(linha=row, chave=key, referencias=refs, declarada=texto(c), nomes=unknown))
        else:
            count['constantes_ou_sem_referencia_direta'] += 1
            others.append(dict(linha=row, chave=key, declarada=texto(c), nomes=unknown))
        if isinstance(b, str) and '#REF!' in b:
            count['formula_com_ref_quebrada'] += 1
    return dict(chaves=len(keys), contagens=dict(count), divergentes=mismatches, compostas=compound, outras=others)


def validar_limites(modelo):
    """Audita todas as origens estruturadas e dependências qualificadas de B."""
    grids = {a['nome']: (a['linhas'], a['colunas']) for a in modelo['layout']['abas']}
    checked, errors = 0, []
    for row, values in linhas_modelo(modelo).items():
        if row == 1:
            continue
        key, b, c, _ = values
        refs, _ = dependencias(b)
        refs += [(r.aba, r.endereco) for r in (referencias(c) or [])]
        for sheet, address in refs:
            checked += 1
            if sheet not in grids:
                errors.append(dict(linha=row, chave=key, aba=sheet, endereco=address, erro='aba ausente'))
                continue
            cols, rows = grids[sheet][1], grids[sheet][0]
            left, top, right, bottom = range_boundaries(address.replace('$', ''))
            if (right is not None and right > cols) or (bottom is not None and bottom > rows):
                errors.append(dict(linha=row, chave=key, aba=sheet, endereco=address, erro='fora da grade'))
    return dict(referencias_conferidas=checked, erros=errors)


def conferir_compostas(auditoria):
    """Compara a origem declarada com as dependências; não infere um conserto.

Uma faixa declarada pode ser a origem principal de um MAP/INDEX, enquanto B
também lê seletores e cabeçalhos. Não exige que C liste todas as dependências.
"""
    checked, review = 0, []
    for item in auditoria['compostas']:
        declared = referencias(item['declarada'])
        if not declared:
            review.append(dict(chave=item['chave'], motivo='origem não estruturada'))
            continue
        for ref in declared:
            checked += 1
            pair = (ref.aba, ref.endereco.replace('$', ''))
            if pair not in item['referencias']:
                review.append(dict(chave=item['chave'], origem=pair, motivo='comparar região/expressão manualmente'))
    return dict(formulas=len(auditoria['compostas']), origens_conferidas=checked, revisao=review)


def diferencas(antes, depois):
    """Falha se qualquer campo do layout, além de ANALISE C, mudar."""
    # Faz uma cópia sem duplicar milhões de objetos da geometria.
    def sem_c(modelo):
        layout = modelo['layout']
        return {**layout, 'abas': [
            {**tab, 'celulas': [[x[0], '<origem>', *x[2:]] if re.fullmatch(r'C[0-9]+', x[0]) else x for x in tab['celulas']]}
            if tab['nome'] == 'ANALISE' else tab for tab in layout['abas']]}
    if sem_c(antes) != sem_c(depois) or antes['r53'] != depois['r53'] or antes['analise'] != depois['analise']:
        raise ValueError('Mudança fora de ANALISE C ou nos contratos')
    aa, bb = linhas_modelo(antes), linhas_modelo(depois)
    if aa.keys() != bb.keys():
        raise ValueError('Linhas diferentes')
    changes = []
    for row in sorted(aa):
        a, b = aa[row], bb[row]
        if a[2] != b[2]:
            if a[:2] != b[:2] or a[3] != b[3]:
                raise ValueError('Chave, valor ou parte alterada')
            old, new = referencias(a[2]), referencias(b[2])
            if not old or not new or len(old) != len(new):
                raise ValueError('Origem não estruturada ou cardinalidade diferente')
            refs, names = dependencias(b[1])
            kind = 'unica' if len(refs) == 1 and ':' not in refs[0][1] and not names else 'composta'
            changes.append(dict(linha=row, chave=a[0], b=a[1], parte=a[3], antes=texto(a[2]), depois=texto(b[2]), tipo=kind))
    return changes


def plano(changes, snapshots):
    sid, rows = linhas_snapshot(snapshots)
    by_key = {}
    for row, cells in rows.items():
        key = valor(cells[0])
        if key in by_key:
            raise ValueError('Chave repetida na ficha existente')
        by_key[key] = (row, cells)
    ops, guards = [], []
    already = 0
    for change in changes:
        if change['chave'] not in by_key:
            raise ValueError('Chave ausente: ' + change['chave'])
        row, cells = by_key[change['chave']]
        current = valor(cells[2])
        if assinatura_formula(valor(cells[1])) != assinatura_formula(change['b']) or valor(cells[3]) != change['parte']:
            raise ValueError('B ou D difere do modelo conferido: ' + change['chave'])
        if texto(current) == change['depois']:
            already += 1
            continue
        if texto(current) != change['antes']:
            raise ValueError('C não tem a origem anterior esperada: ' + change['chave'])
        old = cells[2].get('userEnteredValue', {})
        if 'formulaValue' in old and texto(current) is not None:
            new = {'formulaValue': '="' + change['depois'].replace('"', '""') + '"'}
        elif 'stringValue' in old:
            new = {'stringValue': change['depois']}
        else:
            raise ValueError('Tipo de C inesperado')
        guards.append(dict(linha=row, chave=change['chave'], celulas=[c.get('userEnteredValue', {}) for c in cells]))
        ops.append((row, old, new))
    def requests(which):
        out = []
        for row, old, new in ops:
            cell = {'values': [{'userEnteredValue': new if which == 'depois' else old}]}
            if out:
                last = out[-1]['updateCells']
                if last['start']['rowIndex'] + len(last['rows']) == row - 1 and len(last['rows']) < 200:
                    last['rows'].append(cell)
                    continue
            out.append({'updateCells': {'start': {'sheetId': sid, 'rowIndex': row - 1, 'columnIndex': 2},
                'rows': [cell], 'fields': 'userEnteredValue'}})
        return out
    raw = json.dumps(guards, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return dict(versao=1, celulas=len(ops), ja_atualizadas=already, guardas=guards,
        guardas_sha256=hashlib.sha256(raw.encode()).hexdigest(), pedidos=requests('depois'), reversao=requests('antes'))


def mudancas_manifesto(manifesto, modelo):
    """Usa o manifesto público em clone novo, sem depender do snapshot antigo."""
    rows = linhas_modelo(modelo)
    seen = set()
    changes = []
    for item in manifesto['mudancas']:
        key, row = item['chave'], item['linha']
        if key in seen or row not in rows:
            raise ValueError('Manifesto com chave duplicada ou linha ausente')
        seen.add(key)
        current = rows[row]
        if current[0] != key or texto(current[2]) != item['depois']:
            raise ValueError('Manifesto não corresponde ao modelo gerado: ' + key)
        before, after = referencias(item['antes']), referencias(item['depois'])
        if not before or not after or len(before) != len(after):
            raise ValueError('Manifesto de origem inválido')
        changes.append({**item, 'b': current[1], 'parte': current[3]})
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--antes', type=Path)
    parser.add_argument('--depois', type=Path)
    parser.add_argument('--modelo', type=Path)
    parser.add_argument('--manifesto', type=Path, default=ROOT/'r53/diagnostico-android/ORIGENS-ANALISE-2026-10-30.json')
    parser.add_argument('--snapshot', nargs='*', type=Path)
    parser.add_argument('--saida', required=True, type=Path)
    args = parser.parse_args()
    if args.modelo and not (args.antes or args.depois):
        b = json.loads(args.modelo.read_text())
        changes = mudancas_manifesto(json.loads(args.manifesto.read_text()), b)
    elif args.antes and args.depois and not args.modelo:
        a, b = (json.loads(p.read_text()) for p in (args.antes, args.depois))
        changes = diferencas(a, b)
    else:
        parser.error('Use --modelo ou o par --antes/--depois')
    report = dict(mudancas=changes, auditoria=auditar(linhas_modelo(b)), limites=validar_limites(b))
    report['compostas'] = conferir_compostas(report['auditoria'])
    if args.snapshot:
        report['plano'] = plano(changes, [json.loads(p.read_text()) for p in args.snapshot])
    args.saida.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(mudancas=len(changes), tipos=dict(Counter(c['tipo'] for c in changes)),
        divergentes=len(report['auditoria']['divergentes']), chaves=report['auditoria']['chaves'],
        celulas_planejadas=report.get('plano', {}).get('celulas')), ensure_ascii=False))


if __name__ == '__main__':
    main()
