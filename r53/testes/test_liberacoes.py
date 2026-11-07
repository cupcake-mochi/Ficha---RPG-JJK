import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ficha-v01'))
import montagens_r53 as R


class AquisicaoLiberacoes(unittest.TestCase):
    def test_contextos_recebem_o_nivel_da_posicao(self):
        fam = dict(G=dict(cd='D1', tm_nome='D2', tm_forma='D3', tm_dano='D4',
                          tm_pe='D5', tm_montagem='D6', tm_como=7),
                   H={'nível': "'FICHA'!$AH$11", 'maior classe': 'X1', 'classe 0 dados': 'X2'},
                   lugares=[('', lib, n, dict(classe='D'+str(20*n), nome='E'+str(20*n)))
                            for lib in (False, True) for n in (1, 2, 3)], zero_c=[])
        ctx = R.contextos(fam, dict(cartas=[], fichas_c=[]))
        for n in (1, 2, 3):
            lib = next(g for g in ctx if g['id'] == f'liberacao.{n}')
            comum = next(g for g in ctx if g['id'] == f'feitico.{n}')
            self.assertEqual(lib['requisito'], f"'FICHA'!$AH$11>={10*n}")
            self.assertIn(f'Liberação Máxima {n}: nível mínimo {10*n}', R.aviso_requisito(lib))
            self.assertEqual(R.aviso_requisito(comum), '""')

    def test_aviso_de_entidade_continua_exigindo_o_trunfo(self):
        requisito = 'AND(DADOS_INVOC!A2="Maldição domada",DADOS_INVOC!B2>=20)'
        self.assertEqual(R.aviso_requisito(dict(requisito=requisito)),
                         'IF('+requisito+',"","Trunfo exige maldição domada com técnica própria e nível de aquisição")')


if __name__ == '__main__':
    unittest.main()
