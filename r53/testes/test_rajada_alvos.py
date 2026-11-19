from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo


class RajadaAlvos(unittest.TestCase):
    def avaliar(self, livre, **entradas):
        dados = dict(nome='QA', nivel=30, classe=3, preparada=True,
                     permite_dano=True, permite_cura=True,
                     dest_dano='Alvo', dest_cura='Aliado',
                     origem_permissao='Definição', **entradas)
        with patch.object(modelo, 'ARVORE', modelo.arvore(livre)):
            return modelo.calcular(dados)

    def test_rajada_individual_limita_tiros_pelos_dados_e_classe(self):
        for livre in (False, True):
            for forma, dados, tiros in [('Projétil', 6, 4), ('Projétil', 1, 1), ('Toque', 3, 3)]:
                with self.subTest(livre=livre, forma=forma, dados=dados):
                    r = self.avaliar(livre, forma=forma, dano=True, p_dano=dados, m1='Rajada')
                    self.assertTrue(r['valida'])
                    self.assertEqual(r['tiros'], tiros)

    def test_rajada_rejeita_area_e_ausencia_de_dados(self):
        for livre in (False, True):
            for entradas in (
                dict(forma='Explosão', dano=True, p_dano=2),
                dict(cura=True, p_cura=4),
                dict(dano=True, p_dano=0),
            ):
                with self.subTest(livre=livre, entradas=entradas):
                    r = self.avaliar(livre, m1='Rajada', **entradas)
                    self.assertFalse(r['valida'])
                    self.assertEqual(r['tiros'], 0)
                    self.assertIn('Rajada exige alvo individual', r['avisos'])

    def test_tudo_ou_nada_sem_dano_nao_financia_em_nenhum_slot(self):
        for livre in (False, True):
            for slot in (1, 2):
                restricao = {f'r{slot}': 'Tudo ou Nada', f'r{slot}_valida': True}
                for entradas in (dict(cura=True, p_cura=2), dict(dano=True, p_dano=0),
                                 dict(controle='Sem dano', dano=True, p_dano=1)):
                    with self.subTest(livre=livre, slot=slot, entradas=entradas):
                        r = self.avaliar(livre, m1='Guarda', **restricao, **entradas)
                        self.assertFalse(r['valida'])
                        self.assertEqual(r[f'retorno_r{slot}'], 0)
                        self.assertEqual(r['devolucao'], 0)
                        self.assertIn('Tudo ou Nada exige dano por TR', r['avisos'])

    def test_tudo_ou_nada_considera_arredondamento_de_toca_a_alma(self):
        for livre in (False, True):
            for pontos in (1, 2):
                r = self.avaliar(livre, dano=True, p_dano=pontos, m1='Toca a Alma',
                                 permite_alma=True, r1='Tudo ou Nada', r1_valida=True,
                                 res_dano='TR', tr_dano='Espírito')
                self.assertEqual(r['dano_d8'], pontos // 2)
                self.assertEqual(r['valida'], pontos == 2)
                self.assertEqual(r['retorno_r1'], 2 if pontos == 2 else 0)

    def test_resolucao_explicita_continua_sendo_validada(self):
        tr = dict(dano=True, p_dano=2, res_dano='TR', tr_dano='Vigor')
        for slot in (1, 2):
            restricao = {f'r{slot}': 'Tudo ou Nada', f'r{slot}_valida': True}
            r = self.avaliar(False, m1='Guarda', **tr, **restricao)
            self.assertTrue(r['valida'])
            self.assertEqual(r[f'retorno_r{slot}'], 2)
            self.assertEqual(r['devolucao'], 2)
        self.assertFalse(self.avaliar(False, m1='Rajada', **tr)['valida'])
        self.assertTrue(self.avaliar(True, m1='Rajada', **tr)['valida'])
        self.assertFalse(self.avaliar(False, dano=True, p_dano=2,
                                     r1='Tudo ou Nada', r1_valida=True)['valida'])
