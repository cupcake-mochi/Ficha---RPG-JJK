#!/usr/bin/env python3
"""Equivalência lexical observada no Google; mudanças semânticas continuam bloqueadas."""
import unittest
from migracao import canonical, equivalent


class FormulasNativasTest(unittest.TestCase):
    def test_referencia_nativa_observada(self):
        self.assertTrue(equivalent('=IF(\'DADOS_PROGRESSAO\'!$K$2="","Livro + custom nos menus.","⚠ "&\'DADOS_PROGRESSAO\'!$K$2)',
                                   '=IF(DADOS_PROGRESSAO!$K$2="";"Livro + custom nos menus.";"⚠ "&DADOS_PROGRESSAO!$K$2)'))

    def test_texto_literal_nao_perde_aspas(self):
        self.assertFalse(equivalent('="\'DADOS\'!A1"', '="DADOS!A1"'))
        self.assertFalse(equivalent('=IF(A1;"a;b";"x")', '=IF(A1,"a,b","x")'))

    def test_decimal_e_texto(self):
        self.assertTrue(equivalent('=IF(A1;0,5;"1,5")', '=IF(A1,0.5,"1,5")'))
        self.assertFalse(equivalent('="0,5"', '="0.5"'))

    def test_nome_com_apostrofo_espacos_ou_pontuacao(self):
        for formula in ["='O''Brien'!A1", "='foo''DADOS'!A1", "='Dados 1'!A1", "='Dados;1'!A1"]:
            self.assertEqual(canonical(formula), formula)

    def test_endereco_condicao_e_mensagem_continuam_exatos(self):
        for different in ['=DADOS!B1', '=DADOS!A2', '=IF(DADOS!A1,1,0)']:
            self.assertFalse(equivalent("='DADOS'!A1", different))
        self.assertFalse(equivalent('=IF(A1,"Obrigatório","")', '=IF(A1,"Opcional","")'))

    def test_booleano_nao_vira_numero(self):
        self.assertFalse(equivalent(False, 0)); self.assertFalse(equivalent(True, 1))


if __name__ == '__main__': unittest.main(verbosity=2)
