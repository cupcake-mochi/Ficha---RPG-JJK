import unittest

from r53.testes.test_sem_volta import avaliar_montagem


class DevolucoesIncompativeis(unittest.TestCase):
    def test_bloqueia_so_a_restricao_incompativel(self):
        casos = (
            ('Queima-Roupa', {'forma': 'Toque'}, 2, 'incompatível com Forma/pessoal'),
            ('Queima-Roupa', {'forma': 'Aura'}, 0, 'incompatível com Forma/pessoal'),
            ('Queima-Roupa', {'pessoal': True}, 0, 'incompatível com Forma/pessoal'),
            ('Queima-Roupa', {'m2': 'Longe · um degrau'}, 0, 'não aceita Longe'),
            ('Atrasar', {'m1': 'Rápido'}, 0, 'Atrasar e Rápido incompatíveis'),
            ('Parado', {'m1': 'Reação'}, 0, 'Reação incompatível'),
            ('Carregar', {'m1': 'Armado'}, 0, 'Armado e Carregar incompatíveis'),
        )
        for livre in (False, True):
            for nome, variante, credito, aviso in casos:
                for pos in (1, 2):
                    with self.subTest(livre=livre, restricao=nome, variante=variante, vaga=pos):
                        dados = {'m1': 'Guarda', **variante, f'r{pos}': nome, f'r{pos}_valida': True}
                        r = avaliar_montagem(livre, **dados)
                        self.assertFalse(r['valida'])
                        self.assertIn(aviso, r['avisos'])
                        self.assertEqual(r[f'retorno_r{pos}'], 0)
                        self.assertEqual(r['devolucao'], credito)
                        outra = 3 - pos
                        r = avaliar_montagem(livre, **dados, **{f'r{outra}': 'Barulho', f'r{outra}_valida': True})
                        self.assertEqual(r[f'retorno_r{pos}'], 0)
                        self.assertEqual(r[f'retorno_r{outra}'], 2)

    def test_preserva_controles_validos(self):
        casos = (
            ('Queima-Roupa', 'Projétil', 'Guarda', 3),
            ('Queima-Roupa', 'Explosão', 'Guarda', 2),
            ('Atrasar', 'Projétil', 'Precisão', 2),
            ('Parado', 'Projétil', 'Precisão', 2),
            ('Carregar', 'Projétil', 'Rápido', 3),
        )
        for livre in (False, True):
            for nome, forma, melhoria, credito in casos:
                with self.subTest(livre=livre, restricao=nome, forma=forma):
                    r = avaliar_montagem(livre, forma=forma, m1=melhoria, r2=nome, r2_valida=True)
                    self.assertTrue(r['valida'], r['avisos'])
                    self.assertEqual(r['devolucao'], credito)
