"""Extração das opções do livro, sem aceitar catálogo vazio ou truncado."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ficha-v01'))
from extrair_tecnica import sementes, capitulo
from ficha_amaldicoada import regras, _Dados


class Sementes(unittest.TestCase):
    nomes = ['Domínio Simples', 'Energia Reversa', 'Pétala', 'Aptidão Própria']

    def test_livro_e_catalogo_publicado(self):
        self.assertEqual(sementes(capitulo('13. Rotas de criação')), self.nomes)
        self.assertEqual(regras()['sementes'], self.nomes)

    def test_titulos_irmaos_e_filhos_sem_absorver_secao_seguinte(self):
        for nivel in (5, 6):
            trecho = ['##### Sementes', 'Escolha uma das quatro opções abaixo.']
            trecho += ['#' * nivel + ' ' + nome for nome in self.nomes]
            trecho += ['#### Cura', '##### Não é uma semente']
            self.assertEqual(sementes(trecho), self.nomes)

    def test_rejeita_falta_e_duplicacao(self):
        for nomes in ([], self.nomes[:3], self.nomes[:3] + self.nomes[:1]):
            trecho = ['##### Sementes', 'Escolha uma das quatro opções abaixo.']
            trecho += ['##### ' + nome for nome in nomes]
            with self.assertRaises(ValueError):
                sementes(trecho)

    def test_faixa_inclui_quatro_valores_sem_cabecalho(self):
        dados = _Dados(0, 1, 2)
        dados.prox = 93  # CO, posição usada na DADOS_AM atual
        dados.tabela('sementes', ['semente'], [[n] for n in regras()['sementes']])
        self.assertEqual(dados.faixa('sementes', so=0), '$CO$2:$CO$5')
        self.assertEqual([dados.cel[f'CO{i}'][0] for i in range(2, 6)], self.nomes)


if __name__ == '__main__':
    unittest.main()
