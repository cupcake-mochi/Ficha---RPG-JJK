"""Regressão do defeito observado no editor nativo: pontos zero viravam FALSE."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'ficha-v01'))
import configuracao_horizontal as horizontal
import extensoes_custom as extensoes

class TiposNoLayout(unittest.TestCase):
 def test_numeros_e_caixas_conservam_o_tipo_apos_as_duas_transformacoes(self):
  for ordem in [(False,0,True,1,0.0,1.0),(1.0,1,True,0.0,0,False)]:
   for transformacao in [horizontal.formula,extensoes.formula]:
    transformacao.cache_clear()
    for original in ordem:
     with self.subTest(transformacao=transformacao.__module__,valor=repr(original)):
      resultado=transformacao(original,'MONTAGENS')
      self.assertEqual(type(resultado),type(original))
      self.assertEqual(resultado,original)

if __name__=='__main__':unittest.main()
