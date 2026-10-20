"""Contrato observável: tipos/identidades não podem se perder na exportação."""
import json,sys,unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'ficha-v01'),str(ROOT/'r53')]
from r53.contrato import decodificar,ErroContrato
from montagens_r53 import CAMPOS,DEFAULTS_EDITOR
from modelo import INPUTS,DEFAULTS

class ContratoR53(unittest.TestCase):
 def ficha(self):
  schema=['classe']+[k for k,_,_ in CAMPOS]
  version={'classe':3,**{k:DEFAULTS_EDITOR[k] for k,_,_ in CAMPOS},'preparada':True,'funcao1':'Dano','pontos1':2,'funcao2':'Cura','pontos2':2,
           'origem_permissao':'vento "cortante"\nC:\\pasta\tsem inferência'}
  active={**DEFAULTS,'id':'feitico.1','nome':'FALSE','classe':3,'dano':True,'cura':True,'p_dano':2,'p_cura':2}
  vals={'formato.versao':12,'r53.montagem.esquema':2,'r53.versao.campos':json.dumps(schema),'r53.entrada.campos':json.dumps(INPUTS),
        'r53.feitico.1.versao.3':json.dumps([version[k] for k in schema]),'r53.feitico.1.entrada':json.dumps([active[k] for k in INPUTS])}
  return {k:dict(valor=v,celula='',parte='entrada') for k,v in vals.items()}
 def test_conserva_escolhas_pontos_booleanos_e_texto(self):
  r=decodificar(self.ficha())['feitico.1'];v=r['versoes']['3']
  self.assertEqual((v['funcao1'],v['pontos1'],v['funcao2'],v['pontos2']),('Dano',2,'Cura',2))
  self.assertIs(v['permite_dano'],False);self.assertEqual(type(v['pontos3']),int)
  self.assertIn('"cortante"\nC:\\pasta\t',v['origem_permissao']);self.assertEqual(r['ativa']['nome'],'FALSE')
 def test_booleano_nao_vira_quantidade(self):
  d=self.ficha();schema=json.loads(d['r53.versao.campos']['valor']);v=json.loads(d['r53.feitico.1.versao.3']['valor']);v[schema.index('pontos1')]=True
  d['r53.feitico.1.versao.3']['valor']=json.dumps(v)
  with self.assertRaises(ErroContrato):decodificar(d)
 def test_rejeita_versao_de_outra_classe(self):
  d=self.ficha();d['r53.feitico.1.versao.4']=d.pop('r53.feitico.1.versao.3')
  with self.assertRaises(ErroContrato):decodificar(d)
 def test_nao_aceita_json_truncado(self):
  d=self.ficha();d['r53.feitico.1.entrada']['valor']='[1,'
  with self.assertRaises(ErroContrato):decodificar(d)
 def test_esquema_antigo_ou_ausente_nao_aprova_formato12(self):
  d=self.ficha();del d['r53.entrada.campos']
  with self.assertRaises(ErroContrato):decodificar(d)
 def test_leitor_reprova_aviso_r53_sem_depender_de_icone(self):
  spec=importlib.util.spec_from_file_location('leitor',ROOT/'ler-analise.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  d=self.ficha();d['r53.feitico.1.avisos']=dict(valor='Distribuição excede o saldo',parte='aviso',celula='')
  self.assertEqual(m.relatorio(d)[0],'reprovada')
 def test_formato11_continua_suportado(self):
  spec=importlib.util.spec_from_file_location('leitor',ROOT/'ler-analise.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertEqual(m.relatorio({'formato.versao':dict(valor=11,parte='cabeçalho',celula='')})[0],'aprovada')

if __name__=='__main__':unittest.main()
