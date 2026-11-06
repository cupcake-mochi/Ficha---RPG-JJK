from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo


class FragilFica(unittest.TestCase):
    def avaliar(self, livre, *, catalogo_extra=None, **entradas):
        dados = dict(nome='QA', nivel=30, classe=3, preparada=True, dano=True,
                     p_dano=2, permite_dano=True, dest_dano='Alvo',
                     permite_alma=True, origem_permissao='Definição')
        with patch.object(modelo, 'ARVORE', modelo.arvore(livre)):
            return modelo.calcular({**dados, **entradas}, catalogo_extra=catalogo_extra)

    def test_precisao_sozinha_nao_financia_nenhuma_posicao(self):
        for livre in (False, True):
            for slot in (1, 2):
                for classe, modo in ((0, 'Classe 0'), (3, 'Comum')):
                    with self.subTest(livre=livre, slot=slot, classe=classe):
                        restricao = {f'r{slot}': 'Frágil', f'r{slot}_valida': True}
                        r = self.avaliar(livre, classe=classe, modalidade=modo,
                                         m1='Precisão', fragil_pago=1, **restricao)
                        self.assertFalse(r['valida'])
                        self.assertEqual(r[f'retorno_r{slot}'], 0)
                        self.assertEqual(r['devolucao'], 0)
                        self.assertIn('Frágil exige Melhorias interrompíveis pagas', r['avisos'])

    def test_melhorias_instantaneas_nao_financiam_fragil(self):
        melhorias = ('Passo', 'Empurrão', 'Longe · um degrau', 'Longe · três degraus',
                     'Mais Um', 'Rajada', 'Remate')
        for livre in (False, True):
            for slot in (1, 2):
                for melhoria in melhorias:
                    with self.subTest(livre=livre, slot=slot, melhoria=melhoria):
                        restricao = {f'r{slot}': 'Frágil', f'r{slot}_valida': True}
                        r = self.avaliar(livre, m1=melhoria, fragil_pago=2, **restricao)
                        self.assertFalse(r['valida'])
                        self.assertEqual(r[f'retorno_r{slot}'], 0)
                        self.assertEqual(r['devolucao'], 0)
                        self.assertIn('Frágil exige Melhorias interrompíveis pagas', r['avisos'])

    def test_mistura_separa_o_gasto_de_guarda_e_passo(self):
        for livre in (False, True):
            for familia, declarado, credito, valido in (
                ('Normal', 3, 2, True), ('Normal', 4, 2, False),
                ('Livre', 1, 1, True), ('Livre', 2, 1, False),
            ):
                with self.subTest(livre=livre, familia=familia, declarado=declarado):
                    r = self.avaliar(livre, m1='Passo', m4='Guarda',
                                     fam_Auxiliares=familia, fragil_pago=declarado,
                                     r2='Frágil', r2_valida=True)
                    self.assertEqual(r['retorno_r2'], credito)
                    self.assertEqual(r['valida'], valido)
                    if not valido:
                        self.assertIn('Frágil: gasto interrompível não pode exceder o gasto real', r['avisos'])

    def test_efeito_proprio_pode_manter_gasto_declarado(self):
        for livre in (False, True):
            for nome, credito, valido in (('Efeito Próprio', 2, True), ('Passo', 0, False)):
                opcao = dict(nome=nome, tipo='melhorias', familia='Auxiliares',
                             peso=2, repeticoes=1, classe_minima=0, cadastro_valido=1,
                             rotulo_base='Melhoria de teste')
                r = self.avaliar(livre, catalogo_extra={'Melhoria de teste': opcao},
                                 m1='Melhoria de teste', fragil_pago=2,
                                 r1='Frágil', r1_valida=True)
                self.assertEqual(r['retorno_r1'], credito)
                self.assertEqual(r['valida'], valido, r['avisos'])

    def test_guarda_preserva_o_preco_pago_depois_do_desconto(self):
        for livre in (False, True):
            for declarado, valido in ((1, True), (2, False)):
                r = self.avaliar(livre, m1='Precisão', m2='Guarda',
                                 fam_Auxiliares='Livre', fragil_pago=declarado,
                                 r1='Frágil', r1_valida=True)
                self.assertEqual(r['pago_m2'], 1)
                self.assertEqual(r['retorno_r1'], 1)
                self.assertEqual(r['valida'], valido)
            r = self.avaliar(livre, m1='Guarda', fragil_pago=3,
                             r1='Frágil', r1_valida=True)
            self.assertTrue(r['valida'])
            self.assertEqual(r['retorno_r1'], 2)

    def test_fica_exige_area_e_dados_efetivos(self):
        for livre in (False, True):
            for forma, dados, valido in (
                ('Projétil', 2, False), ('Explosão', 1, False), ('Explosão', 2, True),
            ):
                with self.subTest(livre=livre, forma=forma, dados=dados):
                    r = self.avaliar(livre, classe=4, forma=forma, p_dano=dados,
                                     m1='Fica', m2='Toca a Alma')
                    self.assertEqual(r['dano_d8'], dados // 2)
                    self.assertEqual(r['valida'], valido)
                    if not valido:
                        self.assertIn('Fica exige área de dano', r['avisos'])
