"""O diagnóstico cobre a rota de registro livre sem afrouxar contas."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import modelo as M
from formulas import evaluate

def calcular(**entries):
 env={**M.DEFAULTS,'nome':'Teste','classe':3,'nivel':13,'preparada':True,**entries}
 for k,e in M.arvore(True).items():env[k]=evaluate(e,env,M.OPCOES)
 return env
class CartaoDireto(unittest.TestCase):
 def test_description_replaces_extra_permission_form(self):
  v=calcular(dano=True,p_dano=4);self.assertTrue(v['valida'],v['avisos']);self.assertEqual(v['dano_d8'],4)
 def test_mixed_pool_still_pays_base(self):
  v=calcular(dano=True,cura=True,p_dano=3,p_cura=3);self.assertTrue(v['valida'],v['avisos']);self.assertEqual(v['base_funcoes'],3);self.assertEqual(v['sem_uso'],0)
 def test_overspend_still_rejected(self):
  v=calcular(dano=True,cura=True,p_dano=4,p_cura=4);self.assertFalse(v['valida']);self.assertIn('excede',v['avisos'])
 def test_closed_family_still_rejected(self):
  v=calcular(cura=True,p_cura=2,fam_Amparo='Fechada');self.assertFalse(v['valida']);self.assertIn('Amparo Fechada',v['avisos'])
 def test_zero_and_maximum_still_have_own_limits(self):
  self.assertFalse(calcular(modalidade='Classe 0',classe=0,cura=True)['valida'])
  self.assertFalse(calcular(modalidade='Técnica Máxima',nivel=26,dano=True,cura=True)['valida'])
 def test_invalid_numeric_distribution_still_rejected(self):
  self.assertFalse(calcular(dano=True,p_dano=1.5)['valida']);self.assertFalse(calcular(dano=True,p_dano=-1)['valida'])
if __name__=='__main__':unittest.main()
