import unittest

from r53.testes.test_sem_volta import avaliar_montagem


class FormaFuncao(unittest.TestCase):
    def test_requisitos_das_cinco_pecas(self):
        sem_dano = dict(dano=False, p_dano=0)
        cura = dict(cura=True, p_cura=2)
        casos = (
            ('Escolher', 'Projétil', {}, 'Escolher e Contorno exigem Forma de área', 0),
            ('Escolher', 'Toque', {}, 'Escolher e Contorno exigem Forma de área', 2),
            ('Contorno', 'Projétil', {}, 'Escolher e Contorno exigem Forma de área', 0),
            ('Contorno', 'Toque', {}, 'Escolher e Contorno exigem Forma de área', 2),
            ('Perseguir', 'Cone', {}, 'Perseguir exige alvo individual', 0),
            ('Perseguir', 'Explosão', {}, 'Perseguir exige alvo individual', 0),
            ('Reserva', 'Projétil', {}, 'Reserva exige dados de cura', 0),
            ('Reserva', 'Projétil', {**sem_dano, 'vt': True, 'p_vt': 2},
             'Reserva exige dados de cura', 0),
            ('Sugar', 'Projétil', {**sem_dano, **cura}, 'Sugar exige dano inicial efetivo', 0),
            ('Sugar', 'Projétil', dict(m2='Toca a Alma', permite_alma=True, p_dano=1),
             'Sugar exige dano inicial efetivo', 0),
            ('Escolher', 'Cone', {}, '', 0),
            ('Contorno', 'Cone', {}, '', 0),
            ('Perseguir', 'Projétil', {}, '', 0),
            ('Reserva', 'Projétil', {**sem_dano, **cura}, '', 0),
            ('Reserva', 'Projétil', dict(cura=True, p_cura=1, p_dano=1, dependencias='Parcelas independentes'), '', 0),
            ('Sugar', 'Projétil', {}, '', 0),
            ('Sugar', 'Projétil', dict(m2='Toca a Alma', permite_alma=True, p_dano=2), '', 0),
        )
        for livre in (False, True):
            for peca, forma, entradas, aviso, devolucao in casos:
                for pos in (1, 4):
                    with self.subTest(livre=livre, peca=peca, forma=forma, entradas=entradas, pos=pos):
                        r = avaliar_montagem(livre, forma=forma, **{f'm{pos}': peca}, **entradas)
                        self.assertEqual(r['valida'], not aviso, r['avisos'])
                        if aviso:
                            self.assertIn(aviso, r['avisos'])
                        self.assertEqual(r['devolucao'], devolucao)
                        if entradas.get('m2') == 'Toca a Alma':
                            self.assertEqual(r['dano_d8'], entradas['p_dano'] - 1)

    def test_avisos_independentes_na_mesma_montagem(self):
        for livre in (False, True):
            r = avaliar_montagem(livre, m1='Contorno', m2='Reserva', m4='Sugar',
                                 dano=False, p_dano=0, vt=True, p_vt=1)
            self.assertIn('Escolher e Contorno exigem Forma de área', r['avisos'])
            self.assertIn('Reserva exige dados de cura', r['avisos'])
            self.assertIn('Sugar exige dano inicial efetivo', r['avisos'])
