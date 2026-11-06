import unittest
from unittest.mock import patch

from r53.testes.test_sem_volta import avaliar_montagem, modelo


class RestricoesAgrupadas(unittest.TestCase):
    def test_pares_excludentes_contam_o_maior_credito_elegivel(self):
        pares = (
            ('Atrasar', 'Parado', 3, 'repetem impedimento'),
            ('Barulho', 'Assinatura', 2, 'escolha uma exposição'),
            ('Barulho', 'Barulho', 2, 'Não repetir o mesmo impedimento'),
            ('Recuo · Lento', 'Fraqueza · TR Físico', 3, 'não se combinam'),
            ('Fraqueza · TR Físico', 'Peso Morto', 3, 'não se combinam'),
            ('Recuo · Lento', 'Peso Morto', 2, 'não se combinam'),
            ('Uma Vez', 'Aquecer', 2, 'um grupo de frequência'),
            ('Condicional · Média', 'Aquecer', 3, 'um grupo de frequência'),
            ('Uma Vez', 'Condicional · Média', 3, 'um grupo de frequência'),
        )
        for livre in (False, True):
            for primeira, segunda, credito, aviso in pares:
                for r1, r2 in ((primeira, segunda), (segunda, primeira)):
                    with self.subTest(livre=livre, r1=r1, r2=r2):
                        r = avaliar_montagem(livre, m1='Guarda', m2='Precisão',
                                             r1=r1, r2=r2, r1_valida=True, r2_valida=True)
                        self.assertFalse(r['valida'])
                        self.assertIn(aviso, r['avisos'])
                        self.assertEqual(r['devolucao'], credito)

    def test_restricao_incompativel_perde_credito_nas_duas_vagas(self):
        for livre in (False, True):
            for melhoria, restricao, aviso in (
                ('Reação', 'Atrasar', 'Reação incompatível'),
                ('Remate', 'Aquecer', 'Remate não combina com Aquecer'),
            ):
                for pos in (1, 2):
                    with self.subTest(livre=livre, melhoria=melhoria, vaga=pos):
                        outra = 3 - pos
                        r = avaliar_montagem(livre, m1=melhoria,
                                             **{f'r{pos}': restricao, f'r{pos}_valida': True,
                                                f'r{outra}': 'Barulho', f'r{outra}_valida': True})
                        self.assertFalse(r['valida'])
                        self.assertIn(aviso, r['avisos'])
                        self.assertEqual(r[f'retorno_r{pos}'], 0)
                        self.assertEqual(r['devolucao'], 2)

    def test_grupo_conserva_credito_elegivel_e_combinacao_independente_soma(self):
        for livre in (False, True):
            grupo = avaliar_montagem(livre, m1='Guarda', m2='Precisão',
                                     r1='Fraqueza · TR Físico', r1_valida=False,
                                     r2='Recuo · Lento', r2_valida=True)
            self.assertFalse(grupo['valida'])
            self.assertEqual(grupo['devolucao'], 2)
            independente = avaliar_montagem(livre, m1='Guarda', m2='Precisão',
                                           r1='Sangra', r1_valida=True, r2='Barulho', r2_valida=True)
            self.assertTrue(independente['valida'], independente['avisos'])
            self.assertEqual(independente['devolucao'], 5)

    def test_restricao_propria_usa_o_grupo_de_frequencia_do_catalogo(self):
        entradas = dict(nome='QA', nivel=30, classe=3, preparada=True,
                        dano=True, p_dano=2, permite_dano=True, dest_dano='Alvo',
                        origem_permissao='Definição', m1='Guarda', m2='Precisão',
                        r1='Uma Vez', r1_valida=True, r2='Limitação própria', r2_valida=True)
        for livre in (False, True):
            with patch.object(modelo, 'ARVORE', modelo.arvore(livre)):
                for frequencia, credito in ((1, 3), (0, 5)):
                    catalogo = {'Limitação própria': dict(nome='custom.restricao.1',
                                tipo='restricoes', peso=2, frequencia=frequencia)}
                    r = modelo.calcular(entradas, catalogo_extra=catalogo)
                    self.assertEqual(r['valida'], not frequencia, r['avisos'])
                    self.assertEqual(r['devolucao'], credito)

    def test_classe_zero_aceita_somente_credito_leve_valido(self):
        for livre in (False, True):
            for restricao, forma, credito in (
                ('Sangra', 'Projétil', 0), ('Atrasar', 'Projétil', 0),
                ('Carregar', 'Projétil', 0), ('Sem Volta', 'Projétil', 0),
                ('Condicional · Média', 'Projétil', 0), ('Sobrecusto', 'Projétil', 0),
                ('Queima-Roupa', 'Projétil', 0), ('Queima-Roupa', 'Explosão', 1),
                ('Barulho', 'Projétil', 1), ('Aquecer', 'Projétil', 1),
            ):
                with self.subTest(livre=livre, restricao=restricao, forma=forma):
                    r = avaliar_montagem(livre, classe=0, modalidade='Classe 0', forma=forma,
                                         m1='Precisão', r1=restricao, r1_valida=True)
                    self.assertEqual(r['valida'], bool(credito), r['avisos'])
                    self.assertEqual(r['devolucao'], credito)
                    self.assertEqual(r['dano_d8'], 1 + credito)
