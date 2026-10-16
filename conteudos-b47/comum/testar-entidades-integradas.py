"""Exercita o módulo canônico em capacidades diferentes, após personagem.

Sem rede, XLSX ou GS. A fixture impede escrita das fontes; estes testes não
recalculam fórmulas nem reaplicam o runner de injeção da entrega Claude.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'ficha-v01'),str(ROOT/'ficha'),str(ROOT/'conteudos-b47/personagem')]
import fixture_base
import b47_personagem
import entidades_custom as ec
from openpyxl.utils.cell import range_boundaries


def aba(layout,name):
    return next(a for a in layout['abas'] if a['nome']==name)


def cells(layout,name):
    return {c[0]:c[1] for c in aba(layout,name)['celulas']}


class EntidadesIntegradas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope=fixture_base.montar()
        cls.base=cls.scope['LAYOUT']
        b47_personagem.aplica(cls.base,dict(fam=cls.scope['_FAM'],inv=cls.scope['_FIV'],
            criacao=cls.scope['_CRIACAO'],pecas=cls.scope['_PECAS'],
            capacidades=json.loads((ROOT/'conteudos-b47/comum/contrato.json').read_text(encoding='utf8'))['capacidades'],
            abas={'forma':'DADOS_FORMAS','aptidao':'DADOS_APTIDOES','talento':'DADOS_TALENTOS'},
            inicio=aba(cls.base,'CONFIGURAÇÃO')['linhas']+4))

    def test_capacidades_parametricas_preservam_editor_e_consumidores(self):
        for nt,nl in [(10,20),(5,7),(1,1)]:
            with self.subTest(tipos=nt,talentos=nl):
                layout=deepcopy(self.base)
                before=cells(layout,'CONFIGURAÇÃO')
                am_before=cells(layout,'DADOS_AM')
                iv_before=cells(layout,'INVOCAÇÕES')
                tr=ec.aplica(layout,dict(inv=self.scope['_FIV'],
                    capacidades={'tipo_entidade':nt,'talento_entidade':nl}))
                self.assertEqual(tr['inicio'],aba(self.base,'CONFIGURAÇÃO')['linhas']+4)
                after=cells(layout,'CONFIGURAÇÃO')
                self.assertTrue(all(after[a]==v for a,v in before.items()))
                self.assertEqual(cells(layout,'DADOS_AM'),am_before)
                # Os campos livres do jogador não são substituídos por descrições de tipo.
                iv_after=cells(layout,'INVOCAÇÕES')
                self.assertEqual(len(self.scope['_FIV']['fichas_c']),12)
                self.assertTrue(all(iv_after[g['def']]==iv_before[g['def']]
                    for g in self.scope['_FIV']['fichas_c']))
                self.assertEqual(set(tr['consumidores']['comparacoes'].values()),{12})
                self.assertEqual(len(tr['registros']['tipo_entidade']),nt)
                self.assertEqual(len(tr['registros']['talento_entidade']),nl)
                exported=ec.exporta(tr)
                self.assertEqual(len(exported),9*nt+7*nl)
                self.assertEqual(len({x[0] for x in exported}),len(exported))
                for group,n in [('tipo_entidade',nt),('talento_entidade',nl)]:
                    self.assertIn(f'custom.{group}.{n}.nome',{x[0] for x in exported})
                metadata=aba(layout,'INVOCAÇÕES')['notas_contextuais']
                self.assertEqual(len(metadata['destinos']),12)
                self.assertEqual(len(metadata['gatilhos']),8*nt)
                self.assertEqual(aba(layout,ec.NOME)['colunas'],44)
                occupied=set()
                for region in aba(layout,'CONFIGURAÇÃO')['mescladas']:
                    c,r,cc,rr=range_boundaries(region)
                    points={(y,x) for y in range(r,rr+1) for x in range(c,cc+1)}
                    self.assertFalse(occupied & points,region)
                    occupied.update(points)

    def test_capacidades_invalidas_recusadas_sem_mutacao(self):
        for key in ('tipo_entidade','talento_entidade'):
            for value in (True,False,0,-1,31,1.5,'10'):
                with self.subTest(campo=key,valor=value):
                    count=len(self.base['abas'])
                    with self.assertRaises(ValueError):
                        ec.aplica(self.base,dict(inv=self.scope['_FIV'],capacidades={key:value}))
                    self.assertEqual(len(self.base['abas']),count)

    def test_inicio_sobreposto_e_reaplicacao_recusados(self):
        for value in (0,True,aba(self.base,'CONFIGURAÇÃO')['linhas']+2):
            with self.subTest(inicio=value):
                with self.assertRaises(ValueError):
                    ec.aplica(self.base,dict(inv=self.scope['_FIV'],inicio=value))
        layout=deepcopy(self.base)
        ec.aplica(layout,dict(inv=self.scope['_FIV']))
        before=cells(layout,'CONFIGURAÇÃO')
        with self.assertRaises(ValueError):
            ec.aplica(layout,dict(inv=self.scope['_FIV']))
        self.assertEqual(cells(layout,'CONFIGURAÇÃO'),before)


if __name__=='__main__':
    unittest.main(verbosity=2)
