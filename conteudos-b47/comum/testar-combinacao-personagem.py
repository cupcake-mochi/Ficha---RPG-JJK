"""Contrato da combinação comum + personagem; não simula recálculo de fórmulas."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'ficha-v01'), str(ROOT/'conteudos-b47/personagem')]
from b47_personagem.motor import CAMPOS
from b47_personagem.interface import chave_contrato


def tabs(model):
    return {a['nome']: a for a in model['layout']['abas']}


def cells(model, name):
    return {v[0]:v[1] for v in tabs(model)[name]['celulas']}


def analysis(model):
    values = cells(model, 'ANALISE')
    return [(value, [values.get(col+address[1:]) for col in 'BCD'])
            for address, value in values.items() if address.startswith('A') and address != 'A1']


class Combinacao(unittest.TestCase):
    def test_contrato_anterior_preservado_na_ordem(self):
        before, after = analysis(BASE), analysis(MODEL)
        self.assertEqual(len(before),7436)
        self.assertEqual(len(after),8190 if 'entidades' in MODEL else 7960)
        self.assertEqual(after[:len(before)],before)
        self.assertEqual(len({k for k,_ in after}),len(after))

    def test_campos_aprovados_e_avisos_sem_sobras(self):
        expected = {chave_contrato(g,n,k,False) for g,ks in CAMPOS.items()
                    for n in range(1,11) for k in ks}
        expected |= {chave_contrato(g,n,'',True) for g in CAMPOS for n in range(1,11)}
        expected |= {f'aviso.personagem.{g}.{n}' for g in ('aptidao','talento') for n in range(1,13)}
        if 'entidades' in MODEL:
            contract=json.loads((ROOT/'conteudos-b47/comum/contrato.json').read_text(encoding='utf8'))
            for group,cap in [('tipo_entidade',10),('talento_entidade',20)]:
                expected |= {f'custom.{group}.{n}.{field}' for n in range(1,cap+1) for field in contract['campos'][group]}
                expected |= {f'aviso.custom.{group}.{n}' for n in range(1,cap+1)}
        after = analysis(MODEL)[7436:]
        self.assertEqual(len(expected),754 if 'entidades' in MODEL else 524)
        self.assertEqual({k for k,_ in after},expected)
        self.assertEqual({row[2] for _,row in after},{'configuração','aviso'})
        contract=json.loads((ROOT/'conteudos-b47/comum/contrato.json').read_text(encoding='utf8'))
        for g,ks in CAMPOS.items():
            self.assertEqual(set(contract['campos'][g]),
                {dict(ce='categoria',classe_0='classe_zero').get(k,k) for k in ks})

    def test_editor_novo_preserva_entradas_anteriores(self):
        a,b=cells(BASE,'CONFIGURAÇÃO'),cells(MODEL,'CONFIGURAÇÃO')
        self.assertTrue(set(a)<=set(b))
        for k,v in a.items():self.assertEqual(b[k],v,k)
        tr=MODEL['personagem']
        self.assertEqual(tr['inicio'],tabs(BASE)['CONFIGURAÇÃO']['linhas']+4)
        if 'entidades' in MODEL:
            self.assertEqual(MODEL['entidades']['inicio'],tr['fim']+4)
            self.assertEqual(MODEL['entidades']['fim'],tabs(MODEL)['CONFIGURAÇÃO']['linhas'])
        else:self.assertEqual(tr['fim'],tabs(MODEL)['CONFIGURAÇÃO']['linhas'])
        for group in CAMPOS:
            regs=[g for g in tr['registros'] if g['grupo']==group]
            self.assertEqual([g['n'] for g in regs],list(range(1,11)))
            for g in regs:
                self.assertEqual(set(g['campos']),set(CAMPOS[group]))
                self.assertTrue(set(g['campos'].values())<=set(b))

    def test_catalogos_e_formas_das_doze_entidades(self):
        tr=MODEL['personagem']
        expected={'DADOS_FORMAS','DADOS_APTIDOES','DADOS_TALENTOS'}
        if 'entidades' in MODEL:expected.add('DADOS_ENTIDADES')
        self.assertEqual(set(tabs(MODEL))-set(tabs(BASE)),expected)
        self.assertEqual(len([k for k in tr['catalogos'] if k.startswith('menu_entidade_')]),12)
        self.assertEqual(len(tr['avisos_uso']),24)
        for t in tr['tabelas'].values():
            self.assertEqual(t['total'],t['livro']+10)
            self.assertEqual(tabs(MODEL)[t['aba']]['estado'],'hidden')
        for g in MODEL['condicoes']['registros']:
            menu=next(m for m in tabs(MODEL)['CONFIGURAÇÃO']['menus']
                      if m['onde']==next(r['base'] for r in MODEL['registros']
                      if r['tipo']=='melhoria' and r['n']==g['n']))
            self.assertNotIn('INDIRECT',menu['formula'])

    def test_leitor_novo_texto_literal_e_avisos(self):
        spec=importlib.util.spec_from_file_location('leitor_cd',ROOT/'ler-analise.py')
        leitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(leitor)
        for field in ('base','alcance_personagem_classe_0','area_entidade_classe_6','familia'):
            key='custom.forma.1.'+field
            self.assertEqual(leitor.de_linhas([[key,'007','','configuração']])[key]['valor'],'007')
        for key in ('aviso.personagem.aptidao.12','aviso.personagem.talento.12'):
            self.assertEqual(leitor.relatorio(leitor.de_linhas([
                ['formato.versao','11','','cabeçalho'],
                [key,'Requisito pendente','','aviso']]))[0],'reprovada')
        for field in ('base','vida','talisma','reserva_pe'):
            key='custom.tipo_entidade.1.'+field
            self.assertEqual(leitor.de_linhas([[key,'007','','configuração']])[key]['valor'],'007')

    def test_entidades_capacidade_consumidores_e_notas(self):
        if 'entidades' not in MODEL:self.skipTest('Ensaio anterior à integração de entidades')
        tr=MODEL['entidades']
        self.assertEqual(tr['capacidades'],{'tipo_entidade':10,'talento_entidade':20})
        self.assertEqual(len(tr['entradas']),200)
        for group,n in tr['capacidades'].items():
            self.assertEqual([g['n'] for g in tr['registros'][group]],list(range(1,n+1)))
        self.assertEqual(list(tr['consumidores']['comparacoes'].values()),[12,12,12])
        self.assertTrue(all(k.startswith(('custom.tipo_entidade.','custom.talento_entidade.','aviso.custom.tipo_entidade.','aviso.custom.talento_entidade.'))
                            for k,_ in analysis(MODEL)[7960:]))
        plano=tabs(MODEL)['INVOCAÇÕES']['notas_contextuais']
        self.assertEqual(plano['fonte'],'DADOS_ENTIDADES')
        self.assertEqual(len(plano['destinos']),12)
        self.assertEqual(len(set(plano['destinos'])),12)
        data=cells(MODEL,'DADOS_ENTIDADES')
        self.assertEqual(tabs(MODEL)['DADOS_ENTIDADES']['colunas'],44)
        for row in range(2,14):
            self.assertIn("'INVOCAÇÕES'!",data['AM'+str(row)])
            self.assertNotIn("''INVOCAÇÕES'!",data['AM'+str(row)])
            self.assertTrue(data['AP'+str(row)].startswith('=TEXTJOIN('))

    def test_integracao_sem_sobrepor_mesclas(self):
        from openpyxl.utils.cell import range_boundaries
        occupied={}
        for region in tabs(MODEL)['CONFIGURAÇÃO']['mescladas']:
            c,r,cc,rr=range_boundaries(region)
            for y in range(r,rr+1):
                for x in range(c,cc+1):
                    self.assertNotIn((y,x),occupied,(region,occupied.get((y,x))))
                    occupied[(y,x)]=region


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--modelo',type=Path,required=True)
    p.add_argument('--base',type=Path,required=True)
    a=p.parse_args()
    MODEL=json.loads(a.modelo.read_text(encoding='utf8'))
    BASE=json.loads(a.base.read_text(encoding='utf8'))
    unittest.main(argv=[sys.argv[0]],verbosity=2)
