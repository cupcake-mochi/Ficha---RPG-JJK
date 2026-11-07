import unittest

from r53.testes.test_sem_volta import avaliar_montagem


class CorroiMiraLivre(unittest.TestCase):
    def test_requisito_em_todas_as_vagas_e_modalidades(self):
        for direta in (False, True):
            for modalidade in ('Comum', 'Entidade', 'Liberação Máxima',
                               'Liberação de entidade', 'Técnica Máxima', 'Máxima de entidade'):
                for familia in ('Neutra', 'Normal', 'Livre', 'Fechada'):
                    for pos in range(1, 5):
                        with self.subTest(direta=direta, modalidade=modalidade,
                                          familia=familia, pos=pos):
                            r = avaliar_montagem(direta, modalidade=modalidade,
                                                 fam_Mira=familia, p_dano=1,
                                                 **{f'm{pos}': 'Corrói'})
                            self.assertEqual('Corrói exige Mira Livre' in r['avisos'], familia != 'Livre')
                            self.assertEqual(r['valida'], familia == 'Livre', r['avisos'])
                            self.assertEqual(r['devolucao'], 0)

    def test_desconto_e_controle_fura(self):
        for direta in (False, True):
            for modalidade, preco_corroi, preco_fura in (
                ('Comum', 3, 1), ('Entidade', 4, 2),
            ):
                for peca, preco in (('Corrói', preco_corroi), ('Fura', preco_fura)):
                    livre = avaliar_montagem(direta, modalidade=modalidade,
                                              fam_Mira='Livre', m1=peca, p_dano=1)
                    self.assertTrue(livre['valida'], livre['avisos'])
                    self.assertEqual(livre['melhorias_pagas'], preco)
                neutra = avaliar_montagem(direta, modalidade=modalidade,
                                           fam_Mira='Neutra', m1='Fura', p_dano=1)
                self.assertTrue(neutra['valida'], neutra['avisos'])
                self.assertEqual(neutra['melhorias_pagas'], 3)

    def test_basicas_preservam_o_limite_de_preco(self):
        for direta in (False, True):
            for modalidade in ('Classe 0', 'Básica'):
                for familia in ('Neutra', 'Livre'):
                    r = avaliar_montagem(direta, modalidade=modalidade, classe=0,
                                         fam_Mira=familia, m1='Corrói', p_dano=0)
                    self.assertFalse(r['valida'])
                    self.assertIn('Classe 0 aceita somente Melhoria Leve', r['avisos'])
                    self.assertEqual('Corrói exige Mira Livre' in r['avisos'], familia != 'Livre')
