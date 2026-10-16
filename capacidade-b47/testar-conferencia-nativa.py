#!/usr/bin/env python3
"""Contraprovas offline sobre leituras reais; nenhuma escrita Google.

Requer os artefatos privados locais e o modelo exato. Injeta corrupção só em
memória para garantir que a conferência não aceita perda, fonte ou menu errado.
"""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('auditor', Path(__file__).with_name('conferir-nativo.py'))
auditor = importlib.util.module_from_spec(spec); spec.loader.exec_module(auditor)
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--leituras', type=Path, required=True); ap.add_argument('--modelo', type=Path, required=True)
args = ap.parse_args(); model = json.loads(args.modelo.read_text())
plan = json.loads((args.leituras/'plano.json').read_text()); dest = plan['destino']
read = auditor.ler; original = {}
def cached(path, spreadsheet_id):
    key = str(path)
    if key not in original: original[key] = read(path, spreadsheet_id)
    return deepcopy(original[key])
with patch.object(auditor, 'ler', cached): baseline = auditor.auditar(args.leituras, model)
assert baseline['resultado'] == 'PARCIAL' and baseline['planilha']['resultado'] == 'OK'
assert baseline['revisao_liberada'] is False
print('OK prova de planilha nunca libera migração da revisão')
cases = [
    ('preservacao-final', 'FICHA', 'B14', 'userEnteredValue', {'stringValue': 'entrada alterada'}),
    ('auditoria-final', 'CONFIGURAÇÃO', next(iter(plan['entradas']['CONFIGURAÇÃO'])), 'note', 'nota alterada'),
    ('auditoria-final', 'FICHA', 'N413', 'userEnteredValue', {'formulaValue': '=0'}),
    ('auditoria-final', 'ANALISE', 'A2', 'effectiveValue', {'stringValue': 'chave alterada'}),
    ('auditoria-final', 'ANALISE', 'C3', 'effectiveValue', {'stringValue': 'FICHA!A999'}),
    ('auditoria-final', 'CONFIGURAÇÃO', 'B799', 'dataValidation', {'condition': {'type': 'ONE_OF_RANGE', 'values': [{'userEnteredValue': '=DADOS_PROGRESSAO!$AM$3'}]}, 'strict': True}),
    ('auditoria-final', 'DADOS_AM', 'AB2', 'effectiveValue', {'errorValue': {'type': 'REF', 'message': 'contraprova'}}),
]
for folder, sheet, coord, field, value in cases:
    def corrupt(path, spreadsheet_id):
        data = cached(path, spreadsheet_id)
        if path.name == folder: data.setdefault(sheet, {}).setdefault(coord, {})[field] = deepcopy(value)
        return data
    with patch.object(auditor, 'ler', corrupt): result = auditor.auditar(args.leituras, model)
    assert result['resultado'] == 'FALHA', (folder, sheet, coord, field)
    assert not result['revisao_liberada']
    print('OK recusa corrupção:', sheet, coord, field)
assert auditor.mesma_faixa("='DADOS_PROGRESSAO'!$AM$2:$AM$2", '=DADOS_PROGRESSAO!$AM$2')
assert not auditor.mesma_faixa('=DADOS_PROGRESSAO!$AM$2:$AM$3', '=DADOS_PROGRESSAO!$AM$2')
print('OK colapsar faixa unitária não aceita outra célula nem faixa maior')
print('9 contraprovas OK')
