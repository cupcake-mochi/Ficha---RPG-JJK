#!/usr/bin/env python3
"""Audita leituras locais da descartável v10; nunca acessa Google nem libera revisão.

Usa os diretórios produzidos no roteiro nativo de 16/10. As leituras contêm
entradas privadas: ficam em nuvem-b47/saidas, fora do Git. A saída só contém
contagens, hashes, nomes dos testes e coordenadas de divergências.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from openpyxl.utils.cell import get_column_letter as L, range_boundaries
from migracao import OFICIAL, REVISAO, canonical, equivalent, raw, sha, value
from lotes import pt


def ler(pasta, destino):
    result = {}
    files = sorted(pasta.glob('*.json')) if pasta.is_dir() else [pasta]
    if not files: raise ValueError('Leituras ausentes: '+str(pasta))
    for path in files:
        response = json.loads(path.read_text())['response']
        if response['spreadsheetId'] != destino: raise ValueError('Destino divergente')
        for sheet in response['sheets']:
            cells = result.setdefault(sheet['properties']['title'], {})
            for grid in sheet.get('data', []):
                for y, row in enumerate(grid.get('rowData', []), grid.get('startRow', 0)+1):
                    for x, cell in enumerate(row.get('values', []), grid.get('startColumn', 0)+1):
                        coord = L(x)+str(y)
                        if coord in cells: raise ValueError('Leitura sobreposta: '+coord)
                        cells[coord] = cell
    return result


def efetivo(cell):
    v = cell.get('effectiveValue', {})
    return cell.get('formattedValue', '') if 'errorValue' in v else next(iter(v.values()), '')


def literal(v):
    return v[2:-1].replace('""', '"') if isinstance(v, str) and v.startswith('="') and v.endswith('"') else v


def mesma_faixa(a, b):
    def norm(v):
        v = canonical(v)
        match = re.fullmatch(r'=(.*!)(\$?[A-Z]+\$?\d+):(\$?[A-Z]+\$?\d+)', v)
        return '='+match[1]+match[2] if match and match[2] == match[3] else v
    return norm(a) == norm(b)


def auditar(p, modelo):
    plan = json.loads((p/'plano.json').read_text()); dest = plan['destino']
    if dest in (REVISAO, OFICIAL) or dest == plan['backup_id']:
        raise ValueError('Este auditor aceita apenas descartável distinta do backup')
    if sha(modelo) != plan['alvo_sha256']: raise ValueError('Modelo divergente')
    target = raw(modelo)
    before = ler(p/'preservacao-antes', dest)
    after = ler(p/'preservacao-final', dest)
    audit = ler(p/'auditoria-final', dest)
    metadata = json.loads((p/'metadata-depois.json').read_text())
    if metadata['spreadsheetId'] != dest: raise ValueError('Metadados de outro destino')
    dims = {s['properties']['title']: s['properties']['gridProperties']['rowCount'] for s in metadata['sheets']}
    checks = []; differences = []
    def check(name, ok): checks.append({'teste': name, 'ok': bool(ok)})
    preserved = 0; formulas_changed = []
    for sheet in before.keys() | after.keys():
        for coord in before.get(sheet, {}).keys() | after.get(sheet, {}).keys():
            a = before.get(sheet, {}).get(coord, {}); b = after.get(sheet, {}).get(coord, {})
            expected = plan['valores_alterados'].get(sheet, {}).get(coord, value(a))
            # The only additional change in the preserved blocks: Sheets
            # adjusts this formula automatically when deleting the old tail.
            if sheet == 'CONFIGURAÇÃO' and coord == 'G160' and equivalent(value(a), '=COUNTIF(\'DADOS_CRIACAO\'!$H$2:$H$328,"?*")'):
                expected = target[sheet][coord]
            if not equivalent(expected, value(b)) or a.get('note', '') != b.get('note', ''):
                differences.append([sheet, coord, 'preservação'])
            if not equivalent(value(a), value(b)): formulas_changed.append([sheet, coord])
            preserved += 1
    check('entradas/notas preservadas; mudanças de fórmula iguais ao modelo', not differences)
    written = 0
    for sheet, cells in plan['valores_alterados'].items():
        for coord, expected in cells.items():
            if range_boundaries(coord)[1] > dims[sheet]: continue
            if coord in plan['entradas'].get(sheet, {}): continue
            written += 1
            if not equivalent(expected, value(audit.get(sheet, {}).get(coord, {}))):
                differences.append([sheet, coord, 'alvo'])
    check('valores/fórmulas planejados coincidem após a remoção da cauda', not differences)
    inputs = 0
    for sheet, cells in plan['entradas'].items():
        for coord, a in cells.items():
            b = audit.get(sheet, {}).get(coord, {}); inputs += 1
            if not equivalent(value(a), value(b)) or a.get('note', '') != b.get('note', ''):
                differences.append([sheet, coord, 'entrada mapeada'])
    check('entradas e notas mapeadas restauradas', not differences)
    errors = [[s, c] for s, cells in audit.items() for c, v in cells.items()
              if 'errorValue' in v.get('effectiveValue', {})]
    check('sem erros de fórmula nos intervalos afetados lidos', not errors)
    tab = next(a for a in modelo['layout']['abas'] if a['nome'] == 'CONFIGURAÇÃO')
    config = {**after['CONFIGURAÇÃO'], **audit['CONFIGURAÇÃO']}; menus = 0; menu_diffs = []
    for menu in tab['menus']:
        expected = '='+pt(menu['formula'].lstrip('='))
        for region in menu['onde'].split():
            c, r, cc, rr = range_boundaries(region)
            for y in range(r, rr+1):
                for x in range(c, cc+1):
                    coord = L(x)+str(y); actual = config.get(coord, {}).get('dataValidation', {})
                    condition = actual.get('condition', {}); values = condition.get('values', [])
                    kind = {'list': 'ONE_OF_RANGE', 'custom': 'CUSTOM_FORMULA'}[menu['tipo']]
                    menus += 1
                    # Historical literal lists above the migration boundary
                    # are preserved byte for byte, including their strictness.
                    if y < 733 and actual == before['CONFIGURAÇÃO'].get(coord, {}).get('dataValidation', {}):
                        continue
                    if condition.get('type') != kind or len(values) != 1 or not mesma_faixa(expected, values[0]['userEnteredValue']) or bool(actual.get('strict')) != bool(menu.get('estrito')):
                        menu_diffs.append(coord)
    check('menus de CONFIGURAÇÃO correspondem ao modelo', not menu_diffs)
    a = audit['ANALISE']; rows = [[efetivo(a.get(c+str(r), {})) for c in 'ABCD'] for r in range(1, 7358)]
    keys = [row[0] for row in rows[1:]]
    check('7356 chaves únicas e ordenadas', len(set(keys)) == 7356 and keys == [target['ANALISE']['A'+str(r)] for r in range(2, 7358)])
    contract_diffs = []
    for r in range(2, 7358):
        for col in 'CD':
            if rows[r-1]['ABCD'.index(col)] != literal(target['ANALISE'].get(col+str(r), '')):
                contract_diffs.append(col+str(r))
        if not equivalent(value(a.get('B'+str(r), {})), target['ANALISE'].get('B'+str(r))):
            contract_diffs.append('B'+str(r))
    check('fórmulas, fontes e partes da ANALISE correspondem ao modelo', not contract_diffs)
    spec = importlib.util.spec_from_file_location('leitor', Path(__file__).resolve().parent.parent/'ler-analise.py')
    reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
    ficha = reader.de_linhas(rows); verdict, warnings = reader.relatorio(ficha)
    check('formato 10; somente aviso esperado de escolhas incompletas', ficha.get('formato.versao', {}).get('valor') == 10 and verdict == 'reprovada' and len(warnings) == 1 and warnings[0].startswith('aviso.escolhas_de_pericia '))
    run = json.loads((p/'cenarios-plano.json').read_text())
    restored = 0
    by_id = {s['properties']['sheetId']: s['properties']['title'] for s in metadata['sheets']}
    for req in run['restore']:
        req = req['updateCells']; start = req['start']; sheet = by_id[start['sheetId']]
        coord = L(start['columnIndex']+1)+str(start['rowIndex']+1)
        expected = value(req['rows'][0]['values'][0]); actual = {**after.get(sheet, {}), **audit.get(sheet, {})}.get(coord, {})
        if not equivalent(expected, value(actual)): differences.append([sheet, coord, 'restauração cenário'])
        restored += 1
    check('48 entradas temporárias restauradas por releitura', restored == 48 and not differences)
    def scenario(name):
        return {s: {c: efetivo(v) for c, v in cells.items()} for s, cells in ler(p/'cenarios'/f'{name}.json', dest).items()}
    valid = scenario('validos'); t = valid['DADOS_PROGRESSAO']; m = valid['DADOS_MELHORIAS']; q = valid['DADOS_RESTRICOES']; f = valid['DADOS_CRIACAO']
    check('nomes com curinga são literais', not t.get('G2') and not t.get('G3'))
    check('primeira Perícia/Ofício após livro', t.get('AG25') == 'Rito*' and t.get('AJ13') == 'Primeiro ofício')
    check('décimas vagas e atributos', [t.get(c) for c in ['AG34', 'AH34', 'AJ22', 'AK22']] == ['Última perícia ? ~', 'Destreza', 'Último ofício *', 'Constituição'])
    check('pools das décimas vagas', t.get('AV11') == 'Última perícia ? ~' and t.get('AW11') == 'Último ofício *')
    check('primeira/décima Família compartilhadas', f.get('H11') == 'Familia * ? ~ B47' and f.get('H20') == 'Ultima Familia B47')
    check('primeira/última Melhoria herdadas', m.get('O84') == 'Melhoria * ? ~ B47' and m.get('O113') == 'Ultima melhoria B47' and not m.get('M2') and not m.get('M31'))
    # Leve=1; preço em Família Livre=1+3*1=4, conforme regra existente.
    check('Melhoria do zero: Família, peso e TR', [m.get(c) for c in ['O85', 'P85', 'Q85', 'R85', 'W85']] == ['Nova melhoria B47', 'Familia * ? ~ B47', 1, 4, 1])
    check('primeira/última Restrição herdadas', q.get('M25') == 'Restricao * ? ~ B47' and q.get('M54') == 'Ultima restricao B47' and not q.get('K2') and not q.get('K31'))
    check('Restrição do zero: devolução/frequência', [q.get(c) for c in ['M26', 'O26', 'P26']] == ['Nova restricao B47', 1, 1])
    check('mesmo cadastro nas 12 nonas posições', len(valid['ANALISE']) == 12 and set(valid['ANALISE'].values()) == {'Familia * ? ~ B47'})
    t = scenario('tipo_incorreto')['DADOS_PROGRESSAO']
    check('tipo incorreto invalida somente a Perícia', bool(t.get('G11')) and not t.get('AG34') and t.get('AJ22') == 'Último ofício *')
    t = scenario('duplicado')['DADOS_PROGRESSAO']
    check('duplicata literal invalida ambos', bool(t.get('G2')) and bool(t.get('G3')) and not t.get('AG25'))
    t = scenario('tipo_apagado_vazio')['DADOS_PROGRESSAO']
    check('tipo vazio sem cadastro não acusa problema', not t.get('G4') and not t.get('G13'))
    ok = all(c['ok'] for c in checks)
    return {'resultado': 'PARCIAL' if ok else 'FALHA', 'destino': dest, 'backup_id': plan['backup_id'],
            'alvo_sha256': plan['alvo_sha256'], 'snapshot_sha256': plan['snapshot_sha256'],
            'revisao_liberada': False, 'codigo_vinculado': 'PENDENTE: não salvo/relido/executado',
            'escopo': 'Leituras e cálculos Sheets; não cobre Apps Script, visual ou latência nativos',
            'planilha': {'resultado': 'OK' if ok else 'FALHA', 'checagens': checks,
                         'abas_auditadas': len(audit), 'celulas_lidas': sum(map(len, audit.values())),
                         'valores_alvo': written, 'entradas_notas_mapeadas': inputs,
                         'celulas_preservacao': preserved, 'formulas_atualizadas_preservacao': len(formulas_changed),
                         'entradas_cenarios_restauradas': restored, 'menus_conferidos': menus,
                         'erros_formula': errors, 'divergencias': differences,
                         'menus_divergentes': menu_diffs, 'contrato_divergente': contract_diffs},
            'arquivos_de_evidencia': {str(f.relative_to(p)): sha(json.loads(f.read_text())) for f in sorted(p.rglob('*.json')) if f.parent.name in ('auditoria-final', 'preservacao-final', 'preservacao-antes', 'cenarios')}}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('leituras', 'modelo', 'saida'): ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args(); result = auditar(args.leituras, json.loads(args.modelo.read_text()))
    args.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('resultado', 'destino', 'revisao_liberada')}))
    for check in result['planilha']['checagens']: print(('OK ' if check['ok'] else 'FALHA ')+check['teste'])
    sys.exit(result['resultado'] == 'FALHA')
