"""Limites reais de linhas do transporte: conteúdo, altura e respiro."""
from pathlib import Path
import sys
import unittest
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'ficha'),str(ROOT/'ficha-v01')]
import emitir_gs


class Limites(unittest.TestCase):
    def emitir(self,nome,altura=None):
        wb=Workbook();ws=wb.active;ws.title=nome;ws['A1']='Texto'
        if altura:ws.row_dimensions[altura].height=18.75
        abas,_=emitir_gs.emitir(wb,[nome],imgs={},arte_dir=str(ROOT))
        return abas[0]

    def test_configuracao_inclui_respiro_com_altura_sem_conteudo(self):
        a=self.emitir('CONFIGURAÇÃO',30)
        self.assertEqual(a['rows'],32)
        self.assertEqual(a['alturas']['30'],25)

    def test_ficha_sem_margem_tambem_inclui_altura_declarada(self):
        a=self.emitir('FICHA',30)
        self.assertEqual(a['rows'],30)
        self.assertLessEqual(max(map(int,a['alturas'])),a['rows'])

    def test_politica_de_margem_sem_alturas_permanece(self):
        self.assertEqual(self.emitir('CONFIGURAÇÃO')['rows'],3)
        self.assertEqual(self.emitir('FICHA')['rows'],1)


if __name__=='__main__':unittest.main(verbosity=2)
