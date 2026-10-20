"""Casos legados comprovados e ambíguos; nunca recuperar regras da prosa."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from migracao import planejar
CTX=dict(nivel=13,classe_maxima=4,origem_permissao='Contexto mecânico explicitamente conferido',permite_dano=True,permite_cura=True,permite_vt=True,
         dest_dano='Inimigo válido',dest_cura='Aliado disposto',dest_vt='Aliado disposto',tr_dano='Físico',tr_controle='Físico')
class Migracao(unittest.TestCase):
 def test_mescla_unica_nao_inventa_parcelas(self):
  old=dict(nome='Mescla',classe=3,forma='Projétil',dados='4d8',descricao='Causa dano e cura',funcoes_comprovadas=['Dano','Cura'])
  r=planejar(old,CTX);self.assertEqual(r['status'],'revisar');self.assertIn('Mescla antiga',' '.join(r['problemas']));self.assertEqual(r['original'],old)
 def test_texto_nao_prova_funcao(self):
  r=planejar(dict(nome='Cura',classe=3,forma='Projétil',descricao='Cura 9d8',dados='9d8'),CTX)
  self.assertEqual(r['status'],'revisar');self.assertFalse(r['proposta']['cura'])
 def test_toque_tira_antiga_inclusao_e_recalcula(self):
  old=dict(nome='Contato',classe=3,forma='Toque',melhorias=['Certeiro'],restricoes=['Corpo a Corpo'],funcoes_comprovadas=['Dano'])
  antes=copy.deepcopy(old);r=planejar(old,CTX)
  self.assertEqual(r['status'],'automatico');self.assertEqual(r['resultado']['devolucao'],2);self.assertEqual(r['resultado']['dano_d8'],9)
  self.assertEqual(r['proposta']['m1'],'Precisão');self.assertEqual(r['proposta']['r1'],'');self.assertEqual(old,antes)
 def test_cura_provada_preserva_funcao_e_troca_forma(self):
  r=planejar(dict(nome='Socorro',classe=3,forma='Cura',funcoes_comprovadas=['Cura']),CTX)
  self.assertEqual(r['status'],'automatico');self.assertEqual(r['proposta']['forma'],'Projétil');self.assertEqual(r['resultado']['cura_d8'],6)
 def test_onda_ambigua_nao_escolhe_cura(self):
  r=planejar(dict(nome='Onda',classe=3,forma='Onda',dados='4d8'),CTX);self.assertEqual(r['status'],'revisar')
 def test_opcao_nova_precisa_ser_conferida(self):
  r=planejar(dict(nome='Proteção',classe=3,forma='Projétil',melhorias=['Firmeza'],funcoes_comprovadas=['Dano']),CTX)
  self.assertEqual(r['status'],'revisar');self.assertIn('Firmeza',' '.join(r['problemas']))
if __name__=='__main__':unittest.main()
