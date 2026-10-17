"""Normalizações de representação observadas na releitura real do Sheets."""
import importlib.util
from pathlib import Path
import unittest
import lotes_cd as l
spec=importlib.util.spec_from_file_location('conferencia_cd',Path(__file__).with_name('conferir-migracao-cd.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class Representacao(unittest.TestCase):
    def test_numero_sem_decimais_e_expoente_explicito(self):
        self.assertTrue(c.equivalente_nativo('=IF(A1>15.0,1E99,9.0)','=IF(A1>15;1E+99;9)'))

    def test_numero_fracionario_realmente_diferente(self):
        self.assertFalse(c.equivalente_nativo('=1.5','=15'))

    def test_nao_normaliza_textos(self):
        self.assertFalse(c.equivalente_nativo('="9.0"','="9"'))
        self.assertFalse(c.equivalente_nativo('007',7))

    def test_nao_normaliza_enderecos(self):
        self.assertFalse(c.equivalente_nativo('=SUM(A1)','=SUM(A2)'))
        self.assertFalse(c.equivalente_nativo('=X1E99','=X1E9'))

    def test_booleano_nao_equivale_a_numero(self):
        self.assertFalse(c.equivalente_nativo(False,0))

    def test_menu_de_uma_celula(self):
        r=lambda v:{'condition':{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':v}]},'strict':True,'showCustomUi':True}
        self.assertEqual(l.canon_rule(r("='DADOS_FORMAS'!JQ2:JQ2")),l.canon_rule(r('=DADOS_FORMAS!$JQ$2')))
        self.assertNotEqual(l.canon_rule(r('=DADOS_FORMAS!JQ2:JQ3')),l.canon_rule(r('=DADOS_FORMAS!JQ2')))


if __name__=='__main__':unittest.main()
