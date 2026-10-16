#!/usr/bin/env python3
"""Contraprovas de cobertura/identidade das leituras REST, sem Google."""
from copy import deepcopy
import unittest
from snapshot import fatiar, normalizar, a1


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.meta = {'spreadsheetId': 'DESCARTAVEL', 'sheets': [{'properties': {
            'title': "Família d'água'", 'sheetId': 7,
            'gridProperties': {'rowCount': 3, 'columnCount': 3}}}]}
        self.plan = fatiar(self.meta, {"Família d'água'": ['A1:E5']}, limite=3)
        self.blocks = {}
        for i, chunk in enumerate(self.plan['chunks']):
            self.blocks[chunk['arquivo']] = {'range': chunk['range'], 'response': {
                'spreadsheetId': 'DESCARTAVEL', 'sheets': [{'properties': {
                    'title': "Família d'água'", 'sheetId': 7}, 'data': [{'startRow': i}]}]}}
        self.blocks['0000.json']['response']['sheets'][0]['data'][0]['rowData'] = [
            {'values': [{'userEnteredValue': {'boolValue': False}, 'note': 'Nota\ncompleta'},
                        {'userEnteredValue': {'stringValue': '007'}}]}]

    def run_snapshot(self, blocks=None):
        return normalizar(self.meta, self.plan, self.blocks if blocks is None else blocks,
                          'BACKUP', '2026-10-16T16:00:00Z')

    def test_offsets_tipos_notas_e_grade(self):
        s = self.run_snapshot(); cells = s['cells']["Família d'água'"]
        self.assertEqual(cells['A1']['userEnteredValue'], {'boolValue': False})
        self.assertEqual(cells['A1']['note'], 'Nota\ncompleta')
        self.assertEqual(cells['B1']['userEnteredValue'], {'stringValue': '007'})
        self.assertEqual(s['ranges']["Família d'água'"], ['A1:C1', 'A2:C2', 'A3:C3'])
        self.assertEqual(a1(self.plan['chunks'][0]['range'])[0], "Família d'água'")

    def test_bloco_ausente_nao_vira_vazio(self):
        b = deepcopy(self.blocks); del b['0001.json']
        with self.assertRaisesRegex(ValueError, 'incompletas'): self.run_snapshot(b)

    def test_outro_destino(self):
        b = deepcopy(self.blocks); b['0000.json']['response']['spreadsheetId'] = 'OUTRO'
        with self.assertRaisesRegex(ValueError, 'outro destino'): self.run_snapshot(b)

    def test_faixa_trocada(self):
        b = deepcopy(self.blocks); b['0000.json']['range'] = "'Família d''água'''!A2:C2"
        with self.assertRaisesRegex(ValueError, 'outro destino/faixa'): self.run_snapshot(b)

    def test_aba_trocada(self):
        b = deepcopy(self.blocks); b['0000.json']['response']['sheets'][0]['properties']['sheetId'] = 8
        with self.assertRaisesRegex(ValueError, 'Aba não comprovada'): self.run_snapshot(b)

    def test_resposta_sem_grid(self):
        b = deepcopy(self.blocks); del b['0001.json']['response']['sheets'][0]['data']
        with self.assertRaisesRegex(ValueError, 'GridData ausente'): self.run_snapshot(b)

    def test_linha_excedente_inclusive_vazia(self):
        b = deepcopy(self.blocks); b['0000.json']['response']['sheets'][0]['data'][0]['rowData'].append({})
        with self.assertRaisesRegex(ValueError, 'Linhas fora'): self.run_snapshot(b)

    def test_coluna_excedente(self):
        b = deepcopy(self.blocks); b['0000.json']['response']['sheets'][0]['data'][0]['rowData'][0]['values'] += [{}, {}]
        with self.assertRaisesRegex(ValueError, 'Célula fora'): self.run_snapshot(b)

    def test_metadata_mudou(self):
        self.meta['sheets'][0]['properties']['gridProperties']['rowCount'] = 4
        with self.assertRaisesRegex(ValueError, 'Metadados divergentes'): self.run_snapshot()


if __name__ == '__main__': unittest.main(verbosity=2)
