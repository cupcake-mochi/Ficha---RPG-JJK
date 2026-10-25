"""Intervalos nativos acompanham as inserções em todas as 12 invocações."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ficha-v01'))
import extensoes_custom as ex


class IntervalosQualificados(unittest.TestCase):
    def setUp(self):
        self.original = ex.INSERCOES
        ex.formula.cache_clear()

    def tearDown(self):
        ex.INSERCOES = self.original
        ex.formula.cache_clear()

    def test_duas_expansoes_em_todas_as_entidades(self):
        for col in ('Y', 'AR'):
            for i in range(6):
                def volume(step):
                    a, b, c, d = (n+step*i for n in (33,35,37,42))
                    return f"=SUM('INVOCAÇÕES'!${col}${a}:'INVOCAÇÕES'!${col}${b},'INVOCAÇÕES'!${col}${c}:'INVOCAÇÕES'!${col}${d})"
                ex.INSERCOES = {'INVOCAÇÕES': [(52+198*j,13) for j in range(6)]}
                ex.formula.cache_clear()
                intermediate = ex.formula(volume(198), 'DADOS_INVOC')
                self.assertEqual(intermediate, volume(211))
                ex.INSERCOES = {'INVOCAÇÕES': [(65+211*j,20) for j in range(6)]}
                ex.formula.cache_clear()
                self.assertEqual(ex.formula(intermediate, 'DADOS_INVOC'), volume(231))

    def test_nao_altera_texto_nomes_ou_outra_aba(self):
        ex.INSERCOES = {'INVOCAÇÕES': [(52,13)]}
        for text in ('="INVOCAÇÕES!Y60:INVOCAÇÕES!Y62"',
                     "=SUM('DADOS'!$Y$60:'DADOS'!$Y$62)", '=SUM(intervalo_nomeado)'):
            self.assertEqual(ex.formula(text, 'INVOCAÇÕES'), text)

    def test_formas_equivalentes_e_linha_absoluta(self):
        ex.INSERCOES = {'INVOCAÇÕES': [(52,13)]}
        for before, after in (
            ("=SUM('INVOCAÇÕES'!Y60:Y62)", "=SUM('INVOCAÇÕES'!Y73:Y75)"),
            ('=SUM(INVOCAÇÕES!Y60:INVOCAÇÕES!Y62)', '=SUM(INVOCAÇÕES!Y73:INVOCAÇÕES!Y75)'),
            ('=SUM(Y60:$Y$62)', '=SUM(Y73:$Y$75)')):
            self.assertEqual(ex.formula(before, 'INVOCAÇÕES'), after)


if __name__ == '__main__':
    unittest.main()
