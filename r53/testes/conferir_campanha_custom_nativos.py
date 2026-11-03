#!/usr/bin/env python3
"""Confere recibos Google nativos, sem importar ou recalcular em Office.

Uso: python3 .../conferir_campanha_custom_nativos.py DIRETORIO_PRIVADO
Exige custom-resultados.json, campanha-resultados.json e indice.json.
Os oráculos são as regras dos ensaios regressao-custom/campanha, com o
endereço atual consultado no índice da própria ficha. Não aceita recibos ausentes.
"""
import json
import math
import sys
from pathlib import Path


def flatten(doc):
    result = {}
    for sheet in doc['sheets']:
        name = sheet['properties']['title']
        for block in sheet['data']:
            for i, row in enumerate(block.get('rowData', [])):
                for j, cell in enumerate(row.get('values', [])):
                    n, col = block.get('startColumn', 0) + j + 1, ''
                    while n:
                        n, m = divmod(n - 1, 26)
                        col = chr(65 + m) + col
                    value = cell.get('effectiveValue', {})
                    if 'errorValue' in value:
                        value = '#' + value['errorValue']['type']
                    else:
                        value = next(iter(value.values()), None)
                    result[name + '!' + col + str(block.get('startRow', 0) + i + 1)] = value
    return result


def main(folder):
    root = Path(folder)
    idx = json.loads((root / 'indice.json').read_text())
    custom, campaign = [
        {k: flatten(v) for k, v in json.loads((root / f'{n}-resultados.json').read_text()).items()}
        for n in ['custom', 'campanha']
    ]
    checks = []

    def check(label, ok, actual=None):
        checks.append({'nome': label, 'ok': bool(ok), **({'atual': actual} if not ok else {})})

    def value(data, case, cell):
        return data[case].get(cell)

    def f(case, key):
        return value(campaign, case, 'FICHA!' + idx[key])

    check('10 recibos custom', len(custom) == 10)
    check('12 recibos campanha', len(campaign) == 12)
    for n in range(2, 12):
        check(f'cadastro {n-1} válido', value(custom, 'completo', f'DADOS_CUSTOM!T{n}') is True)
    expected = [
        ('completo', 'FICHA!O59', 7), ('completo', 'FICHA!D59', 20),
        ('completo', 'FICHA!O67', '4,5 m'), ('completo', 'FICHA PESSOAL!AG92', 3),
        ('completo', 'FICHA PESSOAL!W93', 'Proteção +4 · teto de Destreza 1'),
        ('troca_zero', 'FICHA!D59', 0), ('ferramenta', 'FICHA PESSOAL!U92', '1d6'),
        ('ferramenta', 'FICHA PESSOAL!AG92', 0), ('ferramenta', 'FICHA PESSOAL!AI92', 'Grau 2'),
        ('ferramenta', 'FICHA PESSOAL!AK92', 'Estigma de teste'),
        ('ferramenta', 'FICHA PESSOAL!AQ92', 2), ('ferramenta', 'FICHA!D59', 20),
        ('ferramenta', 'FICHA PESSOAL!V104', .8),
        ('completo', 'DADOS_CUSTOM!B122', 'Fundamento'), ('completo', 'DADOS_CUSTOM!B123', 'Nenhuma'),
        ('marcial_sem', 'DADOS!AK30', 1), ('marcial_sem', 'DADOS!AK31', 0),
        ('marcial_sem', 'DADOS!AK32', 1), ('marcial_sem', 'FICHA!J30', 50),
        ('marcante_livro', 'DADOS_CUSTOM!T8', False), ('marcante_restricao', 'DADOS_CUSTOM!T8', True),
        ('base_latente', 'DADOS_CUSTOM!T7', True), ('base_latente', 'DADOS_CUSTOM!T8', False),
        ('completo', 'FICHA PESSOAL!D45', 'Texto marcante'), ('completo', 'FICHA PESSOAL!R45', 'Texto menor'),
        ('duplicado', 'DADOS_CUSTOM!T2', False), ('invalido', 'DADOS_CUSTOM!T4', False),
    ]
    for case, cell, expected_value in expected:
        actual = value(custom, case, cell)
        check(case + ' ' + cell, type(actual) is type(expected_value) and actual == expected_value, actual)
    check('volume fracionário', math.isclose(value(custom, 'completo', 'FICHA PESSOAL!V104'), 2.1))
    for case, cell in [('duplicado', 'S2'), ('invalido', 'S4')]:
        check(case + ' diagnóstico', bool(value(custom, case, 'DADOS_CUSTOM!' + cell)))
    check('diagnóstico Marcante própria', 'Marcante própria' in str(value(custom, 'marcante_livro', 'DADOS_CUSTOM!V8')))
    check('Marcante publicada aceita', not str(value(custom, 'base_latente', 'FICHA PESSOAL!D51')).startswith('⚠'))
    c = lambda case, cell: value(campaign, case, cell)
    check('atributos iniciais', c('atributos', 'DADOS!AK6') == c('vazia', 'DADOS!AK6') + 3)
    check('treinos', [c('treinos', 'DADOS!AK' + str(n)) for n in [19, 20, 27]] == [11, 3, 13])
    check('deslocamento com buff', str(f('deslocamento', 'deslocamento')).replace(',', '.') == '6.5 m')
    life, level = f('morrendo', 'vida_max'), f('morrendo', 'classe máxima')
    # O cenário de regressao-campanha.py configura deliberadamente estas
    # frações/teto; isto não é o oráculo da regra padrão do livro.
    check('Aguentar', f('morrendo', 'morrendo aguentar') == math.ceil(life * .5))
    check('Insistir', f('morrendo', 'morrendo insistir 1') == min(math.ceil(life * .25), 2 * level)
          and f('morrendo', 'morrendo insistir 2') == min(math.ceil(life * .75), 2 * level))
    check('prazo e sequelas', f('morrendo', 'morrendo prazo') == '2 rodadas')
    check('custo alternativo XP', c('xp', 'DADOS!AR8') == 0 and c('xp', 'DADOS!AR9') == 700)
    check('custo XP zero', c('xp_zero', 'DADOS!AR9') == 0)
    check('custo inicial pendente', c('xp_um_pendente', 'DADOS_CONFIG!Z3') == 'Pendente' and bool(c('xp_um_pendente', 'DADOS_CONFIG!Z33')))
    initial = next(c('rolada', f'DADOS!P{n}') for n in range(5, 11) if c('rolada', f'DADOS!N{n}') == 'Vanguarda')
    check('vida rolada', f('rolada', 'vida_max') == initial + 5 + 4 + 6 + 3 * 4 + 5, f('rolada', 'vida_max'))
    check('rolagem ausente diagnosticada', f('rolada_falta', 'vida_max') == '#N_A' and bool(c('rolada_falta', 'DADOS_CONFIG!AF32')))
    check('regra inválida visível', c('invalida', 'DADOS!AK6') == '#N_A')
    check('substituição por zero', f('troca_zero', 'vida_max') == 0)
    for case in ['atributos', 'treinos', 'xp', 'xp_zero', 'xp_um_pendente']:
        check(case + ': combate preservado', all(f(case, k) == f('vazia', k) for k in ['vida_max', 'energia_max', 'defesa', 'proteção', 'corpo a corpo', 'à distância']))
    result = {'verificacoes': len(checks), 'falhas': [c for c in checks if not c['ok']], 'checks': checks}
    (root / 'campanha-custom-conferencia.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, ensure_ascii=False))
    return bool(result['falhas'])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
