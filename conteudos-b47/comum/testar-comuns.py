"""Integridade da entrega de dano/Condições; cálculo real exige Sheets/Calc."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'ficha-v01'))
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import range_boundaries
import custom_danos
import custom_condicoes


def tab(model, name):
    return next(a for a in model['layout']['abas'] if a['nome'] == name)


def values(model, name):
    return {c[0]: c[1] for c in tab(model, name)['celulas']}


def analysis(model):
    cells = values(model, 'ANALISE')
    return {value: [cells.get(col+address[1:]) for col in 'BCD']
            for address, value in cells.items() if address.startswith('A') and address != 'A1'}


class Comuns(unittest.TestCase):
    def test_01_contrato_retido(self):
        before, after = analysis(BASE), analysis(MODEL)
        self.assertEqual(len(before), 7356)
        self.assertEqual(len(after), 7436)
        self.assertFalse(set(before)-set(after))
        for key in before:
            if key != 'formato.versao':
                self.assertEqual(before[key], after[key], key)

    def test_02_novos_campos_sem_colisao(self):
        before, after = analysis(BASE), analysis(MODEL)
        expected = {row[0] for row in custom_danos.exporta(MODEL['danos'])+custom_condicoes.exporta(MODEL['condicoes'])}
        self.assertEqual(set(after)-set(before), expected)
        self.assertEqual(len(expected), 80)
        self.assertEqual(after['formato.versao'][0], '11')

    def test_03_primeira_ultima_e_capacidade(self):
        regs = MODEL['danos']['registros']
        self.assertEqual([g['n'] for g in regs], list(range(1,11)))
        self.assertEqual(regs[0]['r'], 1735)
        self.assertEqual(regs[-1]['r']+26, MODEL['danos']['fim'])
        for count in (1,3,10,20):
            result = custom_danos.registros(5000,count)
            self.assertEqual(len(result),count)
            self.assertEqual(len({g['nome'] for g in result}), count)
        for count in (0,-1,1.5,True):
            with self.assertRaises(ValueError): custom_danos.registros(5000,count)

    def test_04_consumidores_dano(self):
        menus = [m for m in tab(MODEL,'INVOCAÇÕES')['menus'] if 'DADOS_DANOS' in m['formula']]
        self.assertEqual(sum(len(m['onde'].split()) for m in menus),156)
        # A caixa livre da técnica não vira um menu nem perde a entrada.
        self.assertEqual(values(BASE,'FICHA AMALDIÇOADA').get('J12'),values(MODEL,'FICHA AMALDIÇOADA').get('J12'))
        self.assertEqual(tab(BASE,'FICHA AMALDIÇOADA')['menus'],tab(MODEL,'FICHA AMALDIÇOADA')['menus'])

    def test_05_livro_preservado(self):
        cells = values(MODEL,'DADOS_DANOS')
        book = json.loads((ROOT/'ficha-v01/invocacao-do-livro.json').read_text(encoding='utf-8'))['tipos_de_dano']
        self.assertEqual([cells['M'+str(r)] for r in range(2,17)],book)
        self.assertEqual(len(set(book)),15)
        self.assertEqual(tab(MODEL,'DADOS_DANOS')['linhas'],26)

    def test_06_sem_deslocamento_das_entradas(self):
        a,b = values(BASE,'CONFIGURAÇÃO'),values(MODEL,'CONFIGURAÇÃO')
        for key,address,boolean in BASE['entradas']:
            self.assertEqual(a.get(address),b.get(address),key)
        self.assertEqual(MODEL['inicio'],BASE['inicio'])
        self.assertEqual(MODEL['fim'],BASE['fim'])
        self.assertEqual(len(MODEL['registros']),len(BASE['registros']))

    def test_07_condicao_compartilha_trinta_melhorias(self):
        self.assertEqual(len(MODEL['condicoes']['entradas']),30)
        newmenus = {m['onde']:m for m in tab(MODEL,'CONFIGURAÇÃO')['menus']}
        for g in MODEL['condicoes']['registros']:
            self.assertIn('BT$2:$BT$3',newmenus[g['modalidade']]['formula'])
        self.assertEqual(tab(BASE,'CONFIGURAÇÃO')['linhas'],MODEL['danos']['inicio']-4)

    def test_08_sem_sobrepor_mesclagens_anteriores(self):
        before = set(tab(BASE,'CONFIGURAÇÃO')['mescladas'])
        after = set(tab(MODEL,'CONFIGURAÇÃO')['mescladas'])
        self.assertTrue(before <= after)
        rects = [range_boundaries(x) for x in after-before]
        for x in rects:
            self.assertGreater(x[1],1731)
        for i,a in enumerate(rects):
            for b in rects[i+1:]:
                overlap = a[0]<=b[2] and b[0]<=a[2] and a[1]<=b[3] and b[1]<=a[3]
                self.assertFalse(overlap,(a,b))

    def test_09_formulas_tokenizaveis(self):
        count = 0
        for tr in [MODEL['danos'],MODEL['condicoes']]:
            for cells in tr['depois'].values():
                for value in cells.values():
                    if isinstance(value,str) and value.startswith('='):
                        self.assertTrue(Tokenizer(value).items)
                        count += 1
        self.assertGreater(count,200)

    def test_10_leitor_texto_literal(self):
        spec=importlib.util.spec_from_file_location('leitor_comuns',ROOT/'ler-analise.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for field in ['nome','definicao','efeito']:
            for literal in ['  123  ','FALSE','=1+2','*?~']:
                key='custom.dano.1.'+field
                self.assertEqual(module.de_linhas([[key,literal,'','configuração']])[key]['valor'],literal)
        self.assertIn(11,module.FORMATOS_CONHECIDOS)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo',type=Path,required=True)
    parser.add_argument('--base',type=Path,required=True)
    args=parser.parse_args()
    MODEL=json.loads(args.modelo.read_text(encoding='utf-8'))
    BASE=json.loads(args.base.read_text(encoding='utf-8'))
    unittest.main(argv=[sys.argv[0]],verbosity=2)
