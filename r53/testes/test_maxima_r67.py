"""Técnica Máxima R67 (livro v0.378, decisão do Mizuki em 12/11/2026).

A Forma e a base da função saem dos dados-base (1 ponto de preço = 1d8, nos preços da maior Classe); os pontos de
montagem pagam só as Melhorias. A tabela abaixo foi escrita à mão a partir do livro e conferida por uma conta feita
aqui, sem o modelo. Cada número também tem um defeito plantado: uma cópia do modelo.py com a regra antiga ou com um
erro de propósito, que este teste precisa reprovar.
"""
import importlib.util
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))
import modelo

# faixa: (modalidade, nível, maior Classe, dados-base, pontos de montagem, PE)
FAIXAS = [('Técnica Máxima', 17, 5, 24, 8, 25), ('Técnica Máxima', 21, 6, 28, 12, 30),
          ('Técnica Máxima', 26, 7, 32, 16, 35), ('Máxima de entidade', 17, 5, 19, 8, 25),
          ('Máxima de entidade', 21, 6, 22, 12, 30), ('Máxima de entidade', 26, 7, 26, 16, 35)]
# a tabela do pedido de 14/11/2026: dano P/A/E, cura P/A/E, PV temp. individual, PV temp. coletiva A/E
TABELA = {
    ('Técnica Máxima', 17): ([24, 21, 19], [19, 16, 14], 63, [48, 42]),
    ('Técnica Máxima', 21): ([28, 25, 22], [22, 19, 16], 75, [57, 48]),
    ('Técnica Máxima', 26): ([32, 28, 25], [25, 21, 18], 84, [63, 54]),
    ('Máxima de entidade', 17): ([19, 16, 14], [14, 11, 9], 48, [33, 27]),
    ('Máxima de entidade', 21): ([22, 19, 16], [16, 13, 10], 57, [39, 30]),
    ('Máxima de entidade', 26): ([26, 22, 19], [19, 15, 12], 66, [45, 36]),
}
FORMAS = ('Projétil', 'Aura', 'Explosão', 'Cone', 'Linha')
BASE = dict(nome='QA', preparada=True, tr_dano='Físico', tr_controle='Físico', permite_dano=True, permite_cura=True,
            permite_vt=True, dest_dano='Alvo', dest_cura='Aliado', dest_vt='Aliado', origem_permissao='Definição')


def precos(c):
    """Leve, Média e o preço de cada Forma, na maior Classe (conta independente do modelo)."""
    leve, media = math.ceil(c / 2), c
    return leve, media, {'Projétil': 0, 'Toque': 0, 'Aura': leve, 'Cone': leve, 'Linha': leve, 'Explosão': media}


def avaliar(mod, livre, **entradas):
    with patch.object(mod, 'ARVORE', mod.arvore(livre)):
        return mod.calcular({**BASE, **entradas})


def conferir(mod):
    """Todas as verificações da R67 num modelo; devolve a lista de falhas (vazia = modelo certo)."""
    falhas = []

    def igual(nome, obtido, esperado):
        if obtido != esperado:
            falhas.append(f'{nome}: esperado {esperado!r}, obtido {obtido!r}')

    for livre in (False, True):
        for modo, nivel, c, dados, pontos, pe in FAIXAS:
            leve, media, forma = precos(c)
            dano_t, cura_t, vti_t, vtc_t = TABELA[(modo, nivel)]
            if [dados - forma[f] for f in ('Projétil', 'Aura', 'Explosão')] != dano_t \
                    or [dados - media - forma[f] for f in ('Projétil', 'Aura', 'Explosão')] != cura_t \
                    or 3 * (dados - leve) != vti_t \
                    or [3 * (dados - media - forma[f]) for f in ('Aura', 'Explosão')] != vtc_t:
                falhas.append(f'tabela escrita à mão diverge da conta: {modo} {nivel}')
            b = dict(modalidade=modo, nivel=nivel, classe=c)
            for f in FORMAS:
                nome = f'{modo} {nivel} {f} livre={livre}'
                r = avaliar(mod, livre, **b, forma=f, dano=True)
                igual(nome + ' dano', (r['dano_d8'], r['saldo'], r['pe'], r['valida']), (dados - forma[f], pontos, pe, True))
                r = avaliar(mod, livre, **b, forma=f, cura=True)
                igual(nome + ' cura', (r['cura_d8'], r['saldo'], r['valida']), (dados - media - forma[f], pontos, True))
                vt = 3 * (dados - leve) if forma[f] == 0 else 3 * (dados - media - forma[f])
                r = avaliar(mod, livre, **b, forma=f, vt=True)
                igual(nome + ' PV temp.', (r['vida_temporaria'], r['saldo'], r['valida']), (vt, pontos, True))
            # sem dano: nada de resultado, pontos inteiros, reforço de Controle
            r = avaliar(mod, livre, **b, controle='Sem dano', m1='Condição · Derrubado', cd=15)
            igual(f'{modo} {nivel} sem dano', (r['dano_d8'], r['cura_d8'], r['vida_temporaria'], r['valida']), (0, 0, 0, True))
            igual(f'{modo} {nivel} sem dano reforço', (r['bonus_controle'], r['cd_controle']), (2, 17))
            if '+1 rodada no prazo curto' not in r['efeitos']:
                falhas.append(f'{modo} {nivel} sem dano: falta a rodada adicional')
            # Guarda em área: só a função paga base na Máxima
            r = avaliar(mod, livre, **b, forma='Explosão', dano=True, m1='Guarda')
            igual(f'{modo} {nivel} Explosão + Guarda', r['dano_d8'], dados - media)
        # Fenda de Arrasto (livro): Projétil + Passo + Empurrão, Alcance Livre: 2 de 8 pontos, 24d8
        r = avaliar(mod, livre, modalidade='Técnica Máxima', nivel=17, classe=5, dano=True,
                    m1='Passo', m2='Empurrão', fam_Alcance='Livre')
        igual('Fenda de Arrasto', (r['dano_d8'], r['melhorias_pagas'], r['sem_uso'], r['pe'], r['valida']), (24, 2, 6, 25, True))
        # antes estourava (8 − 5 da Explosão − 6), agora a Forma sai dos dados
        r = avaliar(mod, livre, modalidade='Técnica Máxima', nivel=17, classe=5, forma='Explosão', dano=True,
                    m1='Passo', m2='Empurrão')
        igual('Explosão + Passo + Empurrão', (r['saldo'], r['dano_d8'], r['valida']), (2, 19, True))
        # avisos
        M = dict(modalidade='Técnica Máxima', nivel=17, classe=5)
        for nome, entrada, trecho, deve in [
            ('duas funções', dict(dano=True, vt=True), 'Máxima escolhe uma função', True),
            ('nenhuma função', dict(), 'Máxima: marque a função', True),
            ('sem dano marcado', dict(controle='Sem dano'), 'Máxima: marque a função', False),
            ('sem dano com dano', dict(controle='Sem dano', dano=True), 'Sem dano descarta', True),
            ('sem dano não acusa reforço', dict(controle='Sem dano'), 'não recebe reforço', False),
            ('sem dano sem Controle', dict(controle='Sem dano'), 'Reforço exige Melhoria de Controle', False),
            ('Dano limitado na Máxima', dict(dano=True, controle='Dano limitado à Classe'), 'não recebe reforço', True),
            ('PV temp. liberada', dict(vt=True), 'Máxima escolhe', False),
            ('orçamento só Melhorias', dict(dano=True, m1='Condição · Derrubado', m2='Prende', m3='Cerca'), 'Orçamento excedido', True),
        ]:
            r = avaliar(mod, livre, **M, **entrada)
            if (trecho in r['avisos']) != deve:
                falhas.append(f'aviso {nome}: {trecho!r} {"ausente" if deve else "presente"} em {r["avisos"]!r}')
    return falhas


TROCAS_DEFEITO = {
    'Forma não sai dos dados': ("    restantes=dados_maxima-cf-base\n", "    restantes=dados_maxima-base\n"),
    'base não sai dos dados': ("    restantes=dados_maxima-cf-base\n", "    restantes=dados_maxima-cf\n"),
    'PV temp. individual com base Média': ("IF(tm,IF(OR(ref('cura'),AND(area,ref('vt'))),m,IF(ref('vt'),l,0)),",
                                          "IF(tm,IF(OR(ref('cura'),AND(area,ref('vt'))),m,IF(ref('vt'),m,0)),"),
    'Guarda coletiva paga base na Máxima': ("IF(tm,IF(OR(ref('cura'),AND(area,ref('vt'))),m,",
                                            "IF(tm,IF(OR(ref('cura'),AND(area,OR(ref('vt'),aux))),m,"),
    'saldo antigo': ("IF(tm,orc-pago,orc-base-cf-pago+devolucao)", "orc-base-cf-pago+devolucao"),
    'dano fixo antigo': ("IF(tm,\n            MAX(0,restantes),", "IF(tm,\n            dados_maxima,"),
    'cura fixa antiga': ("IF(tm,MAX(0,restantes),MAX(0,MIN(ref('p_cura')", "IF(tm,dados_maxima,MAX(0,MIN(ref('p_cura')"),
    'PV temp. bloqueada': ("IF(OR(semdano,zero,ref('vt').eq(False)),0,IF(tm,", "IF(OR(semdano,zero,tm,ref('vt').eq(False)),0,IF(tm,"),
    'sem reforço na Máxima sem dano': ("    semdano=AND(OR(comum,tm),ref('controle').eq('Sem dano'))\n",
                                       "    semdano=AND(comum,ref('controle').eq('Sem dano'))\n"),
    'sem aviso de função ausente': ("err(AND(tm,funcoes_tm.eq(0),semdano.eq(False)),", "err(AND(tm,funcoes_tm.eq(0),semdano.eq(False),False),"),
    'aviso antigo de PV temp.': ("err(AND(tm,funcoes_tm.gt(1)),", "err(AND(tm,OR(funcoes_tm.gt(1),ref('vt'))),"),
}


def mutante(velho, novo):
    fonte = (AQUI / 'modelo.py').read_text(encoding='utf-8')
    if fonte.count(velho) != 1:
        raise AssertionError(f'defeito plantado não encontrou o trecho: {velho[:60]!r}')
    spec = importlib.util.spec_from_loader('modelo_mutante', loader=None, origin=str(AQUI / 'modelo.py'))
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(AQUI / 'modelo.py')
    exec(compile(fonte.replace(velho, novo), mod.__file__, 'exec'), mod.__dict__)
    return mod


class MaximaR67(unittest.TestCase):
    def test_tabela_fenda_e_avisos(self):
        falhas = conferir(modelo)
        self.assertEqual(falhas, [], '\n'.join(falhas[:20]))

    def test_defeitos_plantados_acendem(self):
        for nome, (velho, novo) in TROCAS_DEFEITO.items():
            with self.subTest(defeito=nome):
                self.assertTrue(conferir(mutante(velho, novo)), f'o defeito {nome!r} passou sem ser visto')


if __name__ == '__main__':
    unittest.main()
