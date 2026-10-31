"""Regressões de metadados: mapeamento físico, classificação e migração fechada."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'r53'), str(ROOT/'ficha-v01')]
import referencias_origem as R
import extensoes_custom as E
import configuracao_horizontal as H
import origens_analise as A


def modelo(origem, formula="=IF(ISBLANK('FICHA AMALDIÇOADA'!$F$392),\"\",'FICHA AMALDIÇOADA'!$F$392&\"\")"):
    return {'layout': {'abas': [{'nome': 'ANALISE', 'celulas': [
        ['A2', 'passiva.1.categoria', 0], ['B2', formula, 0], ['C2', origem, 0], ['D2', 'entrada', 0]]}]},
        'r53': {'esquema': 2}, 'analise': {'linhas': ['contrato de domínio inalterado']}}


def snapshot(origin, formula=None):
    m = modelo(origin, formula) if formula else modelo(origin)
    values = [dict(userEnteredValue={'formulaValue' if isinstance(v, str) and v.startswith('=') else 'stringValue': v})
              for _, v, _ in m['layout']['abas'][0]['celulas']]
    return {'sheets': [{'properties': {'title': 'ANALISE', 'sheetId': 123},
        'data': [{'startRow': 8, 'rowData': [{'values': values}]}]}]}


class OrigensTest(unittest.TestCase):
    def test_literal_e_formula_constante_preservam_tipo(self):
        for before, expected in [("'FICHA AMALDIÇOADA'!F379", "'FICHA AMALDIÇOADA'!F392"),
                                  ('="\'FICHA AMALDIÇOADA\'!$F$379"', '="\'FICHA AMALDIÇOADA\'!$F$392"')]:
            with self.subTest(before=before):
                self.assertEqual(R.mover(before, E.coord), expected)

    def test_lista_intervalo_extremos_absolutos_aba_repetida(self):
        value = '="\'INVOCAÇÕES\'!$D$52:\'INVOCAÇÕES\'!$H$251  FICHA!D92 FICHA!D103"'
        expected = '="\'INVOCAÇÕES\'!$D$65:\'INVOCAÇÕES\'!$H$277  FICHA!D105 FICHA!D129"'
        self.assertEqual(R.mover(value, E.coord), expected)
        self.assertEqual(R.mover("'INVOCAÇÕES'!D:D", E.coord), "'INVOCAÇÕES'!D:D")
        self.assertEqual(R.mover("'INVOCAÇÕES'!52:53", E.coord), "'INVOCAÇÕES'!65:66")

    def test_apostrofos_no_nome_nao_sao_consumidos(self):
        source = "'D''água'''!$A$1"
        seen = []
        def move(aba, addr):
            seen.append((aba, addr)); return '$B$2'
        self.assertEqual(R.mover(source, move), "'D''água'''!$B$2")
        self.assertEqual(seen, [("D'água'", '$A$1')])

    def test_prosa_strings_e_expressao_dinamica_intactas(self):
        for v in [None, 3, 'CE 3', 'Veja FICHA!D103 para detalhes', '=INDIRECT("FICHA!D103")',
                  '="FICHA!D103"&" extra"', '"FICHA!D103"', "'A'!D1:'B'!D2"]:
            with self.subTest(v=v):
                self.assertEqual(R.mover(v, E.coord), v)

    def test_extensoes_movem_so_coluna_c_e_formulas_reais(self):
        cells = [['A2', 'chave', 0], ['B2', "='FICHA'!D103", 0],
                 ['C2', '="\'FICHA\'!D103"', 0], ['D2', '="FICHA!D103"', 0]]
        layout = {'abas': [{'nome': 'ANALISE', 'celulas': cells}]}
        E.deslocar(layout)
        self.assertEqual(cells[1][1], "='FICHA'!D129")
        self.assertEqual(cells[2][1], '="\'FICHA\'!D129"')
        self.assertEqual(cells[3][1], '="FICHA!D103"')

    def test_horizontal_lista_de_origens(self):
        source = '="\'CONFIGURAÇÃO\'!B737 \'CONFIGURAÇÃO\'!D797 FICHA!D11"'
        self.assertEqual(R.mover(source, lambda s, a: H.faixa(a) if s == H.NOME else a),
                         '="\'CONFIGURAÇÃO\'!AK9 \'CONFIGURAÇÃO\'!BD9 FICHA!D11"')

    def test_cache_nao_vaza_mapa_da_expansao_de_cartoes(self):
        old = E.INSERCOES
        try:
            E.INSERCOES = {'INVOCAÇÕES': [(100, 10), (200, 10)]}; E.formula.cache_clear()
            cells = [['B2', "='INVOCAÇÕES'!D210", 0], ['C2', '="\'INVOCAÇÕES\'!D210"', 0]]
            E.deslocar({'abas': [{'nome': 'ANALISE', 'celulas': cells}]})
            self.assertEqual(cells[1][1], '="\'INVOCAÇÕES\'!D230"')
            self.assertEqual(cells[0][1], "='INVOCAÇÕES'!D230")
        finally:
            E.INSERCOES = old; E.formula.cache_clear()

    def test_auditoria_separa_unica_multipla_intervalo_constante(self):
        rows = {1: ['chave', 'valor', 'célula', 'parte'],
            2: ['a', "='FICHA'!D11", "FICHA!D11", 'entrada'],
            3: ['b', '=TEXTJOIN(" · ",TRUE,FICHA!D11,FICHA!N11)', 'FICHA!D11 FICHA!N11', 'entrada'],
            4: ['c', '=SUM(FICHA!D11:D12)', 'FICHA!D11:D12', 'resultado'],
            5: ['d', '="esquema2"', '', 'cabeçalho']}
        report = A.auditar(rows)
        self.assertFalse(report['divergentes'])
        self.assertEqual(report['contagens'], {'referencia_unica': 1, 'multiplas_ou_intervalos': 2,
                                               'constantes_ou_sem_referencia_direta': 1})
        self.assertEqual(A.conferir_compostas(report)['origens_conferidas'], 3)
        self.assertFalse(A.conferir_compostas(report)['revisao'])
        report['compostas'][0]['declarada'] = 'FICHA!D103'
        self.assertTrue(A.conferir_compostas(report)['revisao'])
        rows[6] = rows[2]
        with self.assertRaisesRegex(ValueError, 'duplicada'): A.auditar(rows)

    def test_plano_por_chave_preserva_literal_formula_e_so_c(self):
        old, new = "'FICHA AMALDIÇOADA'!F379", "'FICHA AMALDIÇOADA'!F392"
        changes = A.diferencas(modelo('="'+old+'"'), modelo('="'+new+'"'))
        for c in [old, '="'+old+'"']:
            plan = A.plano(changes, [snapshot(c)])
            self.assertEqual(plan['celulas'], 1)
            request = plan['pedidos'][0]['updateCells']
            self.assertEqual(request['start'], {'sheetId': 123, 'rowIndex': 8, 'columnIndex': 2})
            self.assertEqual(request['fields'], 'userEnteredValue')
            expected = {'formulaValue': '="'+new+'"'} if c.startswith('=') else {'stringValue': new}
            self.assertEqual(request['rows'][0]['values'], [{'userEnteredValue': expected}])
        self.assertEqual(A.plano(changes, [snapshot(new)])['ja_atualizadas'], 1)

    def test_recusa_b_d_c_chaves_alteradas_sem_plano_parcial(self):
        old, new = "'FICHA AMALDIÇOADA'!F379", "'FICHA AMALDIÇOADA'!F392"
        changes = A.diferencas(modelo(old), modelo(new))
        for mutate in [lambda c: c[0].update(userEnteredValue={'stringValue': 'outra'}),
                       lambda c: c[1].update(userEnteredValue={'formulaValue': '=FICHA!D1'}),
                       lambda c: c[2].update(userEnteredValue={'stringValue': 'FICHA!D1'}),
                       lambda c: c[3].update(userEnteredValue={'stringValue': 'aviso'})]:
            s = snapshot(old); mutate(s['sheets'][0]['data'][0]['rowData'][0]['values'])
            with self.assertRaises(ValueError): A.plano(changes, [s])

    def test_delta_recusa_mudancas_mecanicas_ou_estilos(self):
        a = modelo('FICHA!D1'); b = copy.deepcopy(a)
        for column in [0, 1, 3]:
            b = copy.deepcopy(a); b['layout']['abas'][0]['celulas'][column][1] = 'outra'
            with self.assertRaisesRegex(ValueError, 'fora'): A.diferencas(a, b)
        b = copy.deepcopy(a); b['r53']['esquema'] = 3
        with self.assertRaises(ValueError): A.diferencas(a, b)
        b = copy.deepcopy(a); b['layout']['abas'][0]['celulas'][2][2] = 99
        with self.assertRaises(ValueError): A.diferencas(a, b)

    def test_locale_nao_confunde_matriz_ou_conteudo_textual(self):
        self.assertEqual(A.assinatura_formula('=IF(FICHA!A1,1,2)'), A.assinatura_formula("=IF('FICHA'!$A$1;1;2)"))
        self.assertNotEqual(A.assinatura_formula('=SUM({1,2})'), A.assinatura_formula('=SUM({1;2})'))
        self.assertNotEqual(A.assinatura_formula('="a,b"'), A.assinatura_formula('="a;b"'))

    def test_limites_detectam_aba_ausente_e_fora_da_grade(self):
        m = modelo("'FICHA AMALDIÇOADA'!F392")
        m['layout']['abas'][0].update(linhas=3, colunas=4)
        self.assertTrue(A.validar_limites(m)['erros'])
        m['layout']['abas'].append(dict(nome='FICHA AMALDIÇOADA', linhas=392, colunas=6, celulas=[]))
        self.assertFalse(A.validar_limites(m)['erros'])
        m['layout']['abas'][1]['linhas'] = 391
        self.assertTrue(A.validar_limites(m)['erros'])

    def test_manifesto_em_clone_novo_recusa_modelo_divergente(self):
        old, new = "'FICHA AMALDIÇOADA'!F379", "'FICHA AMALDIÇOADA'!F392"
        record = dict(linha=2, chave='passiva.1.categoria', antes=old, depois=new, tipo='unica')
        self.assertEqual(A.mudancas_manifesto({'mudancas': [record]}, modelo(new))[0]['b'], modelo(new)['layout']['abas'][0]['celulas'][1][1])
        with self.assertRaises(ValueError): A.mudancas_manifesto({'mudancas': [record]}, modelo(old))
        with self.assertRaises(ValueError): A.mudancas_manifesto({'mudancas': [record, record]}, modelo(new))


if __name__ == '__main__':
    unittest.main()
