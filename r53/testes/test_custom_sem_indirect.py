"""DADOS_CUSTOM sem INDIRECT (15/11/2026): o gerador e os .gs gerados concordam; nada volátil sobra.

python -m unittest r53.testes.test_custom_sem_indirect

As faixas de cada tipo passam por trocas depois do custom.py (custom_progressao.py troca as faixas de perícias e
ofícios pela DADOS_PROGRESSAO, pela própria cadeia da faixa). Por isso a comparação com o gerador é da forma:
seletor, chaves, ordem e padrão, com toda faixa trocada por R. Que as faixas são as mesmas de antes da troca fica
com r53/testes/custom_sem_indirect.js (ida e volta do conversor).
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'ficha-v01')]
import custom  # noqa: E402
import indice_ficha as ix  # noqa: E402

FAIXA = re.compile(r"'[A-Z_]+'!\$[A-Z]+\$\d+:\$[A-Z]+\$\d+")


def celulas(nome):
    """{(linha, coluna): fórmula} de um .gs gerado (cadeias JSON dentro do JS)."""
    texto = (ROOT / 'apps-script' / nome).read_text(encoding='utf-8')
    return {(int(r), int(c)): json.loads(f) for r, c, f in
            re.findall(r'\[\s*(\d+),\s*(\d+),\s*("(?:[^"\\]|\\.)*")', texto)}


def forma(f):
    return FAIXA.sub('R', f)


def problemas(formula):
    """O que não pode existir numa fórmula da DADOS_CUSTOM depois da troca."""
    out = []
    if 'INDIRECT(' in formula.upper():
        out.append('INDIRECT volátil')
    # SWITCH com referência direta não devolve faixa no Sheets: o menu fica vazio.
    if re.search(r"SWITCH\([^()]*'?[A-Z_]+'?!\$[A-Z]+\$\d+:", formula):
        out.append('SWITCH devolvendo faixa')
    return out


def lista(sel):
    o = custom.escolha_faixa(sel, {k: 'R' for k in custom.CAMPOS}, 'R')
    return f'=IFERROR(UNIQUE(FILTER({o},{o}<>"")),"")'


class CustomSemIndirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custom_gs = celulas('Custom.gs')
        cls.origens_gs = celulas('Origens.gs')

    def test_listas_dos_cartoes_na_forma_do_gerador(self):
        # O seletor é a célula TIPO do cartão na CONFIGURAÇÃO; ela mudou de lugar no redesenho da aba e vem da fórmula.
        seletores = {}
        for n in range(1, custom.QUANTIDADE + 1):
            for i in range(7):
                f = self.custom_gs.get((2, 110 + (n - 1) * 7 + i), '')
                m = re.match(r"=IFERROR\(UNIQUE\(FILTER\(CHOOSE\(IFERROR\(MATCH\(('CONFIGURAÇÃO'!\$[A-Z]+\$\d+),", f)
                self.assertTrue(m, (n, i, f[:80]))
                self.assertEqual(forma(f), lista(m.group(1)), (n, i))
                seletores.setdefault(n, set()).add(m.group(1))
        self.assertTrue(all(len(s) == 1 for s in seletores.values()), 'um seletor por cartão')
        self.assertEqual(len({next(iter(s)) for s in seletores.values()}), custom.QUANTIDADE, 'cartões com seletores distintos')

    def test_conferencias_na_forma_do_gerador(self):
        for n in range(1, custom.QUANTIDADE + 1):
            row = n + 1
            juntas = forma(''.join(f for (r, c), f in self.origens_gs.items() if r == row and isinstance(f, str)))
            o = custom.escolha_faixa(f'$B{row}', {k: 'R' for k in custom.CAMPOS}, 'R')
            for i in range(7):
                self.assertIn(f'COUNTIF({o},${ix._letras(5 + i)}{row})=0', juntas, (n, i))
            self.assertEqual(juntas.count(f'COUNTIF({o},'), 7, n)

    def test_nada_volatil_nem_switch_de_faixa(self):
        total = 0
        for nome, cel in (('Custom.gs', self.custom_gs), ('Origens.gs', self.origens_gs)):
            for k, f in cel.items():
                if isinstance(f, str):
                    self.assertEqual(problemas(f), [], (nome, k))
                    total += f.count('CHOOSE(IFERROR(MATCH(')
        self.assertEqual(total, 525)

    def test_chaves_do_conversor_na_ordem_do_gerador(self):
        node = subprocess.run(['node', '-e', "process.stdout.write(JSON.stringify(require('./r53/diagnostico-android/preparar_custom_sem_indirect.js').CHAVES))"],
                              cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(node.stdout), list(custom.CAMPOS))

    def test_defeitos_plantados_acendem(self):
        sel = "'CONFIGURAÇÃO'!$T$14"
        bom = lista(sel)
        self.assertEqual(problemas(bom), [])
        # 1. A forma antiga (INDIRECT de texto).
        self.assertIn('INDIRECT volátil', problemas(bom.replace('CHOOSE(', 'INDIRECT(SWITCH(', 1)))
        # 2. SWITCH com a faixa direta: a armadilha que esvaziou o menu na cópia descartável.
        vazio = custom.faixa(100, 160)
        switch = custom.escolha(sel, {k: vazio for k in custom.CAMPOS}, vazio)
        self.assertIn('SWITCH devolvendo faixa', problemas(f'=IFERROR(UNIQUE(FILTER({switch},{switch}<>"")),"")'))
        # 3. Gerador com as chaves noutra ordem: a comparação de forma recusa.
        trocado = custom.escolha_faixa(sel, {k: 'R' for k in reversed(list(custom.CAMPOS))}, 'R')
        self.assertNotEqual(f'=IFERROR(UNIQUE(FILTER({trocado},{trocado}<>"")),"")', bom)
        # 4. Padrão esquecido (índice 9 sem nona faixa) muda a forma.
        sem_padrao = bom.replace(',R)', ')', 1)
        self.assertNotEqual(sem_padrao, bom)


if __name__ == '__main__':
    unittest.main()
