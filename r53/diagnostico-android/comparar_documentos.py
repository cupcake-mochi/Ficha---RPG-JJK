"""Compara leituras nativas completas; sem rede e sem escrita nas planilhas.

Uso: python comparar_documentos.py <diretorio-privado>
Evidências com valores ficam privadas; relatório público só tem contagens,
endereços, nomes de campos e hashes, sem conteúdo de personagem.
"""
import hashlib
import json
import sys
from pathlib import Path
from collections import Counter

OFFICIAL = '1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro'
COPY = '1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8'
FIELDS = ('userEnteredValue', 'effectiveValue', 'note', 'dataValidation', 'textFormatRuns', 'chipRuns')


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def letter(index):
    out = ''
    while index:
        index, mod = divmod(index-1, 26)
        out = chr(65+mod)+out
    return out


def collect(folder, role, identity, plan, meta):
    expected = {f'{i:03}.json' for i in range(len(plan))}
    actual = {p.name for p in (folder/role).glob('*.json')}
    assert actual == expected, (role, 'Leitura incompleta', len(actual), len(expected))
    out, total, summary, errors = {}, 0, {}, []
    ranges = {}
    for i, step in enumerate(plan):
        doc = read(folder/role/f'{i:03}.json')
        assert doc['spreadsheetId'] == identity
        assert len(doc['sheets']) == 1
        sh = doc['sheets'][0]
        assert sh['properties']['title'] == step['tab']
        ranges.setdefault(step['tab'], []).append((step['start'], step['end'], step['cols']))
        total += (step['end']-step['start']+1)*step['cols']
        for block in sh.get('data', []):
            for row, item in enumerate(block.get('rowData', []), block.get('startRow', 0)+1):
                for col, cell in enumerate(item.get('values', []), block.get('startColumn', 0)+1):
                    assert step['start'] <= row <= step['end'] and 1 <= col <= step['cols']
                    if not cell:
                        continue
                    key = (step['tab'], row, col)
                    assert key not in out, key
                    assert not set(cell)-set(FIELDS), (key, set(cell))
                    out[key] = cell
                    formula = cell.get('userEnteredValue', {}).get('formulaValue')
                    counts = summary.setdefault(step['tab'], Counter())
                    counts['celulas_representadas'] += 1
                    if formula:
                        counts['formulas'] += 1
                        counts['bytes_formula_utf8'] += len(formula.encode())
                    if cell.get('dataValidation'):
                        counts['validacoes'] += 1
                    error = cell.get('effectiveValue', {}).get('errorValue')
                    if error:
                        errors.append(dict(aba=key[0], celula=letter(col)+str(row), tipo=error.get('type')))
    assert set(ranges) == {s['properties']['title'] for s in meta['sheets']}
    for sheet in meta['sheets']:
        prop = sheet['properties']
        row = 1
        for start, end, cols in ranges[prop['title']]:
            assert start == row and cols == prop['gridProperties']['columnCount']
            row = end+1
        assert row == prop['gridProperties']['rowCount']+1
    assert total == sum(s['properties']['gridProperties']['rowCount']*s['properties']['gridProperties']['columnCount'] for s in meta['sheets'])
    return out, total, summary, errors


def main(folder):
    plan = read(folder/'plano.json')
    ma, mb = read(folder/'oficial-meta.json'), read(folder/'copia-meta.json')
    a, total, sa, ea = collect(folder, 'oficial', OFFICIAL, plan, ma)
    b, total_b, sb, eb = collect(folder, 'copia', COPY, plan, mb)
    assert total == total_b
    stable = {}
    for role in ('oficial', 'copia'):
        before, after = read(folder/f'{role}-drive-antes.json'), read(folder/f'{role}-drive-depois.json')
        stable[role] = before['modified_time'] == after['modified_time']
    diffs, fields = [], Counter()
    for key in sorted(a.keys() | b.keys()):
        old, new = a.get(key, {}), b.get(key, {})
        changed = [field for field in FIELDS if old.get(field) != new.get(field)]
        if not changed:
            continue
        fields.update(changed)
        diffs.append(dict(aba=key[0], celula=letter(key[2])+str(key[1]), campos=changed))
    sensitive_tabs = {'SALÁRIOS', 'DADOS_SALARIOS', 'ANALISE', 'MONTAGENS'}
    sensitive = [d for d in diffs if d['aba'] in sensitive_tabs]
    result = dict(oficial=OFFICIAL, copia=COPY, blocos_por_documento=len(plan), abas=len(ma['sheets']),
        posicoes_por_documento=total, metadados_e_condicionais_iguais=ma['sheets']==mb['sheets'],
        modifiedTime_estavel=stable, leitura_estavel=all(stable.values()),
        campos_lidos=list(FIELDS), diferencas_por_campo=dict(fields), diferencas=diffs,
        diferencas_em_salarios_analise_montagens=sensitive,
        oficial_totais=dict(sum(sa.values(), Counter())), copia_totais=dict(sum(sb.values(), Counter())),
        oficial_abas={k: dict(v) for k, v in sa.items()}, copia_abas={k: dict(v) for k, v in sb.items()},
        erros_oficial=ea, erros_copia=eb,
        conteudo_oficial_sha256=digest([[list(k),v] for k,v in sorted(a.items())]),
        conteudo_copia_sha256=digest([[list(k),v] for k,v in sorted(b.items())]),
        limites=['Não lê Apps Script, propriedades, acionadores ou execuções.',
            'Não lê formatos completos, mesclas, proteções, imagens ou histórico; regras condicionais e propriedades das abas foram lidas.',
            'Ausência de erro efetivo não detecta erro interno mascarado por IFERROR.',
            'Estabilidade de modifiedTime é sentinela; leituras não são um snapshot transacional.',
            'Diferença de conteúdo não prova causa de abertura; ainda exige ensaio no cliente.'])
    (folder/'comparacao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('oficial_abas','copia_abas','diferencas')}, ensure_ascii=False))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
