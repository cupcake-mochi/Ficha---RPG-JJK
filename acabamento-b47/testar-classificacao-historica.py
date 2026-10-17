"""Contraprovas: a manutenção histórica não pode esconder um defeito."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'capacidade-b47'))
from contratos_historicos import classificar_vazio


class Classificacao(unittest.TestCase):
    def test_rotulos_exatos(self):
        for row in [47+198*i for i in range(6)]:
            for col,before in [('P','LIVRE · TRILHA'),('S','ABERTA · TRILHA'),('AI','LIVRE · TRILHA'),('AL','ABERTA · TRILHA')]:
                accepted,pending=classificar_vazio([['INVOCAÇÕES',col+str(row),before,'ABERTA']],lambda *_:None)
                self.assertEqual((len(accepted),len(pending)),(1,0))
    def test_valor_numerico_nunca_e_excecao(self):
        change=['FICHA','J26',45,46]
        self.assertEqual(classificar_vazio([change],lambda *_:None),([],[change]))
    def test_mesmo_texto_fora_dos_enderecos_nao_passsa(self):
        for sheet,coord in [('FICHA','P47'),('INVOCAÇÕES','P48'),('INVOCAÇÕES','O47')]:
            change=[sheet,coord,'LIVRE · TRILHA','ABERTA']
            self.assertEqual(classificar_vazio([change],lambda *_:None),([],[change]))
    def test_destino_do_cabecalho_e_obrigatorio(self):
        change=['INVOCAÇÕES','I51','DEFINIÇÃO',None]
        self.assertEqual(classificar_vazio([change],lambda *_:None),([],[change]))
        self.assertEqual(len(classificar_vazio([change],lambda s,c:'DEFINIÇÃO' if c=='I52' else None)[0]),1)
    def test_texto_ou_resultado_diferente_continua_falha(self):
        for before,after in [('LIVRE','ABERTA'),('LIVRE · TRILHA','FECHADA'),('ABERTA · TRILHA',None)]:
            change=['INVOCAÇÕES','P47',before,after]
            self.assertEqual(classificar_vazio([change],lambda *_:None),([],[change]))


if __name__=='__main__':unittest.main(verbosity=2)
