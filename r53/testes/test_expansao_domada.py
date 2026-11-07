import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ficha-v01'))
import expansao_domada as E


class ExpansaoDomada(unittest.TestCase):
    def test_formulas_e_limites_do_contrato(self):
        for row in range(2, 14):
            formulas = E.formulas(row, [f"'INVOCAÇÕES'!P{n}" for n in range(1, 9)], '$BN$2:$BN$6')
            self.assertEqual(set(formulas), {'IE', 'JH', 'JJ'})
            for formula in formulas.values():
                quoted, balance = False, 0
                for char in formula:
                    if char == '"':
                        quoted = not quoted
                    elif not quoted:
                        balance += (char == '(') - (char == ')')
                        self.assertGreaterEqual(balance, 0, formula)
                self.assertEqual(balance, 0, formula)
                self.assertFalse(quoted)
                self.assertNotIn('MONTAGENS!', formula)
            self.assertIn('"Incompleta",2,"Completa",3,"Sem Barreiras",5,0', formulas['IE'])
            self.assertIn('FICHA!$E$87<>TRUE', formulas['JJ'])
            self.assertIn('DADOS_AM!$HM$6', formulas['JJ'])
            self.assertIn('técnica própria e etapas', formulas['JJ'])
            self.assertIn('tipo custom: conferir permissão', formulas['JJ'])
            self.assertIn(f'6*$FP{row}&"/"&7*$FP{row}', formulas['JH'])

    def test_nao_conta_versoes_ou_identidades_duplicadas(self):
        for nomes in ([], ['P1'] * 8, ['P'+str(i) for i in range(7)]):
            with self.assertRaises(ValueError):
                E.formulas(2, nomes, '$BN$2:$BN$6')


if __name__ == '__main__':
    unittest.main()
