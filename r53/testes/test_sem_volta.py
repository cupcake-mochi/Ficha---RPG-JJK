from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo


def avaliar_montagem(livre, **entradas):
    dados = dict(nome='QA', nivel=30, classe=3, preparada=True, dano=True,
                 p_dano=2, permite_dano=True, permite_cura=True,
                 permite_vt=True, dest_dano='Alvo', dest_cura='Aliado',
                 dest_vt='Aliado', origem_permissao='Definição')
    with patch.object(modelo, 'ARVORE', modelo.arvore(livre)):
        return modelo.calcular({**dados, **entradas})


class SemVoltaClasseZero(unittest.TestCase):
    avaliar = staticmethod(avaliar_montagem)

    def test_sem_volta_nao_financia_efeitos_garantidos(self):
        for livre in (False, True):
            for pos in (1, 2):
                restricao = {f'r{pos}': 'Sem Volta', f'r{pos}_valida': True}
                for entrada in (dict(dano=False, p_dano=0, cura=True, p_cura=2, m1='Guarda'),
                                dict(dano=False, p_dano=0, vt=True, p_vt=2, m1='Guarda'),
                                dict(cura=True, p_cura=1, m1='Guarda'),
                                dict(dano=False, p_dano=0, m1='Guarda'),
                                dict(m1='Inescapável')):
                    with self.subTest(livre=livre, pos=pos, entrada=entrada):
                        r = self.avaliar(livre, **restricao, **entrada)
                        self.assertFalse(r['valida'])
                        self.assertEqual(r[f'retorno_r{pos}'], 0)
                        self.assertEqual(r['devolucao'], 0)
                        self.assertIn('Sem Volta exige possibilidade de falha completa', r['avisos'])

    def test_declaracao_preserva_mescla_realmente_dependente(self):
        for livre in (False, True):
            declaracao = {'sem_volta_declarada': True} if livre else {'dependencias': modelo.DECLARACAO_SEM_VOLTA}
            r = self.avaliar(livre, m1='Guarda', cura=True, p_cura=1,
                             r1='Sem Volta', r1_valida=True, **declaracao)
            self.assertTrue(r['valida'])
            self.assertEqual(r['devolucao'], 3)
            puro = self.avaliar(livre, dano=False, p_dano=0, m1='Guarda',
                                cura=True, p_cura=2, r1='Sem Volta',
                                r1_valida=True, **declaracao)
            self.assertFalse(puro['valida'])
            self.assertEqual(puro['devolucao'], 0)
            ataque = self.avaliar(livre, m1='Precisão', r1='Sem Volta', r1_valida=True)
            self.assertTrue(ataque['valida'])
            self.assertEqual(ataque['devolucao'], 2)

    def test_resolucao_estruturada_automatica_ou_com_dano_parcial(self):
        dados = dict(m1='Guarda', r1='Sem Volta', r1_valida=True,
                     dependencias=modelo.DECLARACAO_SEM_VOLTA)
        auto = self.avaliar(False, **dados, res_dano='Automático')
        self.assertFalse(auto['valida'])
        self.assertEqual(auto['retorno_r1'], 0)
        for tudo_valido in (False, True):
            tr = self.avaliar(False, **dados, res_dano='TR', tr_dano='Vigor',
                              r2='Tudo ou Nada', r2_valida=tudo_valido)
            self.assertEqual(tr['valida'], tudo_valido)
            self.assertEqual(tr['retorno_r1'], 3 if tudo_valido else 0)

    def test_classe_zero_so_devolve_nas_restricoes_validas_do_escopo(self):
        for livre in (False, True):
            for restricao, forma, devolucao in (
                ('Sobrecusto', 'Projétil', 0), ('Queima-Roupa', 'Projétil', 0),
                ('Queima-Roupa', 'Explosão', 1), ('Barulho', 'Projétil', 1),
            ):
                r = self.avaliar(livre, classe=0, modalidade='Classe 0', forma=forma,
                                 m1='Precisão', r1=restricao, r1_valida=True)
                self.assertEqual(r['valida'], bool(devolucao))
                self.assertEqual(r['retorno_r1'], devolucao)
                self.assertEqual(r['dano_d8'], 1 + devolucao)
                self.assertEqual(r['pe'], 0)
            normal = self.avaliar(livre, m1='Guarda', r1='Sobrecusto', r1_valida=True)
            self.assertTrue(normal['valida'])
            self.assertEqual(normal['devolucao'], 3)
            self.assertEqual(normal['pe'], 15)
