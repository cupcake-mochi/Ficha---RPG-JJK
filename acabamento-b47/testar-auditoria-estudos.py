"""Casos de segurança do classificador de referências indiretas."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('auditoria', Path(__file__).with_name('auditar-estudos.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Referencias(unittest.TestCase):
    def test_destinos_finitos(self):
        f = '=INDIRECT(SWITCH(A1;"tipo";"\'DADOS\'!A1:A2";"\'DADOS\'!B1"))'
        self.assertEqual(mod.indirect_targets(f, {'DADOS'}), ['DADOS'])

    def test_argumento_com_virgula_literal(self):
        f = '=INDIRECT(SWITCH(A1,"x,y","\'DADOS\'!A1","\'DADOS\'!B1"))'
        self.assertEqual(mod.indirect_targets(f, {'DADOS'}), ['DADOS'])

    def test_estudo_em_resultado(self):
        f = '=INDIRECT(SWITCH(A1;"x";"\'ESTUDO 3C\'!A1"))'
        self.assertIsNone(mod.indirect_targets(f, {'DADOS'}))

    def test_estudo_em_default(self):
        f = '=INDIRECT(SWITCH(A1;"x";"\'DADOS\'!A1";"\'ESTUDO 3C\'!A1"))'
        self.assertIsNone(mod.indirect_targets(f, {'DADOS'}))

    def test_endereco_em_celula(self):
        self.assertIsNone(mod.indirect_targets('=INDIRECT(A1)', {'DADOS'}))

    def test_endereco_composto(self):
        f = '=INDIRECT(SWITCH(A1;"x";"\'DADOS\'!"&B1))'
        self.assertIsNone(mod.indirect_targets(f, {'DADOS'}))


if __name__ == '__main__':
    unittest.main()
