# -*- coding: utf-8 -*-
"""Tipos e Talentos de entidade custom, recalculados no LibreOffice (calculadora local, nunca no Google).

Todas as invocações em nível 14 (Classe 4, Constituição 0): vida comum 5 + 3×13 = 44, corpo de criação
5 + 4×13 = 57; entrada 4 PE, com talismã carregado CEILING(4/2) = 2; domada mostra RESERVA · MÁX.
Talentos no nível 14: ganhos dos níveis 1, 6, 10 e 14 abertos, tetos 1, 1, 2 e 3 (livro p. 375).

    python revisao-b47/cd-entidades/test_entidades_mecanica.py [--tipos 6 --talentos 10]
"""
import argparse

from openpyxl.utils import get_column_letter as L

import comum_cd as c
import entidades_custom as ec

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--tipos', type=int, default=ec.TIPOS)
ap.add_argument('--talentos', type=int, default=ec.TALENTOS)
args = ap.parse_args()
P = c.Placar(f'entidades mecanica {args.tipos}-{args.talentos}')
if args.tipos < 6 or args.talentos < 10:
    raise SystemExit('os cenários usam 6 tipos e 10 talentos; capacidades maiores também servem')
m_ent, tr_p = c.exportar(args.tipos, args.talentos)
m_base, _ = c.exportar(None)
mod, base, tr = c.carregar(m_ent), c.carregar(m_base), c.carregar(tr_p)
g, cf = tr['geo'], tr['geo']['colf']
F = g['fichas']
NT, NL = args.tipos, args.talentos
tipo = lambda n: {k: v for k, v in next(x for x in tr['registros']['tipo_entidade'] if x['n'] == n).items()}
tal = lambda n: {k: v for k, v in next(x for x in tr['registros']['talento_entidade'] if x['n'] == n).items()}
CFG, IV, DI, DE = 'CONFIGURAÇÃO', 'INVOCAÇÕES', 'DADOS_INVOC', ec.NOME
print(f'SHA {c.sha()} · capacidades {NT}/{NL} · cartões CONFIGURAÇÃO {tr["inicio"]}–{tr["fim"]}\n')


def ficha(i, nome, tipo_nome=None, carga=True, talentos=()):
    e = {(IV, F[i]['nome']): nome, ('FICHA', g['nivel_ficha']): 14}
    if tipo_nome:
        e[(IV, F[i]['tipo'])] = tipo_nome
    if carga:
        e[(IV, F[i]['talisma'])] = 'Com carga'
    for k, t in talentos:
        e[(IV, F[i]['tal'][k])] = t
    return e


def cad_tipo(n, **campos):
    g_ = tipo(n)
    return {(CFG, g_[k]): v for k, v in campos.items()}


def cad_tal(n, **campos):
    g_ = tal(n)
    return {(CFG, g_[k]): v for k, v in campos.items()}


def junta(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


# Cenário A: combinações independentes, herança, sobrescrita, última vaga, reutilização, livro intacto
A_TIPOS = junta(
    cad_tipo(1, nome='Golem de Papel', vida='Corpo de criação'),
    cad_tipo(2, nome='Gaiola de Talismã', talisma='Usa'),
    cad_tipo(3, nome='Rancor Contido', reserva_pe='Maldição domada'),
    cad_tipo(4, nome='Herdeiro Criado', base='Corpo amaldiçoado de criação'),
    cad_tipo(5, nome='Domada Fabricada', base='Maldição domada', vida='Corpo de criação'),
    cad_tipo(NT, nome='Shiki Sem Talismã', base='Shikigami de criação', talisma='Não usa'))
A_FICHAS = [('Golem de Papel', 57, 4, False), ('Gaiola de Talismã', 44, 2, False), ('Rancor Contido', 44, 4, True),
            ('Herdeiro Criado', 57, 4, False), ('Domada Fabricada', 57, 4, True), ('Shiki Sem Talismã', 44, 4, False),
            ('Shikigami de criação', 44, 2, False), ('Corpo amaldiçoado de criação', 57, 4, False),
            ('Maldição domada', 44, 4, True), ('Shikigami de técnica', 44, 4, False),
            ('Golem de Papel', 57, 4, False), ('Golem de Papel', 57, 4, False)]
A = junta(A_TIPOS, *[ficha(i, f'E{i+1}', t) for i, (t, *_) in enumerate(A_FICHAS)])

# Cenário B: inválidos ficam fora do catálogo e não alteram contas; nomes literais
B = junta(
    cad_tipo(1, nome='Maldição domada', vida='Corpo de criação'),
    cad_tipo(2, nome='Lua X'),
    cad_tipo(3, nome='Lua*', vida='Corpo de criação'),
    cad_tipo(4, nome='Eco Duplo', vida='Corpo de criação'),
    cad_tipo(5, nome='eco duplo'),
    cad_tipo(6, vida='Corpo de criação'),
    ficha(0, 'B1', 'Maldição domada'), ficha(1, 'B2', 'Lua*'), ficha(2, 'B3', 'Lua X'), ficha(3, 'B4', 'Eco Duplo'),
    # contraprova: a mesma busca SEM escape precisa casar o curinga, senão o teste literal não discrimina
    {(DE, 'AZ1'): f'=VLOOKUP("Lua*",{tr["catalogos"]["tipo_entidade"]},2,FALSE)'})

# Cenário C: talentos
C = junta(
    cad_tal(1, nome='Sopro Curto', categoria=1, efeito='Texto próprio do sopro.'),
    cad_tal(2, nome='Muralha', categoria=3, efeito='Texto da muralha.'),
    cad_tal(3, nome='Escama Fina', base='Escama'),
    cad_tal(4, nome='Eco Leve', base='Eco', categoria=1),
    cad_tal(5, nome='Sem Categoria', efeito='Falta a categoria.'),
    cad_tal(6, nome='Base Errada', base='Inexistente', categoria=1),
    cad_tal(7, nome='Rubina', categoria=2, efeito='Outra pedra.'),     # antes de "Ru*na": um curinga casaria aqui
    cad_tal(8, nome='Ru*na', categoria=1, efeito='Runa literal.'),
    cad_tal(9, nome='Leitura', categoria=1),
    cad_tal(NL, nome='Último Talento', categoria=2, efeito='Última vaga.'),
    ficha(0, 'C1', talentos=[(0, 'Sopro Curto'), (1, 'Muralha')]),
    ficha(1, 'C2', talentos=[(0, 'Sopro Curto'), (1, 'Leitura'), (2, 'Último Talento'), (3, 'Muralha'), (4, 'Escama Fina')]),
    ficha(2, 'C3', talentos=[(0, 'Ru*na'), (3, 'Escama Fina')]),
    ficha(3, 'C4', talentos=[(0, 'Eco Leve'), (2, 'Eco Leve')]),
    *[ficha(i, f'C{i+1}', talentos=[(0, 'Sopro Curto')]) for i in range(4, 12)],
    {(DE, 'AZ1'): f'=VLOOKUP("Ru*na",{tr["catalogos"]["talento_entidade"]},2,FALSE)'})

# Cenário D: só livro, para comparar a DADOS_INVOC inteira com o gerador sem o módulo
D = junta(*[ficha(i, f'D{i+1}', t, talentos=[(0, 'Leitura'), (2, 'Fluxo')]) for i, (t, *_) in enumerate(A_FICHAS[6:10] * 3)])

leitura = [(DI, L(cf[k]) + str(2 + i)) for i in range(12) for k in ('vida', 'ent', 'd_res', 'ntal', 'ttal', 'd_tal')
           + tuple(f'ce{j}' for j in range(8)) + tuple(f'd_tt{j}' for j in range(8))]
leitura += [(DE, L(col) + str(r)) for r in range(2, max(NT, NL) + 2) for col in (ec.TR['erro'], ec.LR['erro'])]
nbt, nbl = 5, 15
leitura += [(DE, L(col) + str(r)) for r in range(2, nbl + NL + 2) for col in ec.LC.values()]
leitura += [(DE, L(col) + str(r)) for r in range(2, nbt + NT + 2) for col in ec.TC.values()]
leitura += [(DE, 'AZ1')]
try:
    R = c.recalcular(mod, {'A': A, 'B': B, 'C': C, 'D': D}, leitura, prefixo='cd-ent')
    cols_d = sorted(set(cf.values()))
    leitura_d = [(DI, L(col) + str(2 + i)) for i in range(12) for col in cols_d]
    RD = c.recalcular(mod, {'D': D}, leitura_d, prefixo='cd-ent-d')['D']
    RB = c.recalcular(base, {'D': D}, leitura_d, prefixo='cd-base-d')['D']
except RuntimeError as e:
    P.impedido('recálculo no LibreOffice', str(e))
    P.fim()

v = lambda cen, i, k: R[cen][(DI, L(cf[k]) + str(2 + i))]
erro_t = lambda cen, n: R[cen][(DE, L(ec.TR['erro']) + str(n + 1))] or ''
erro_l = lambda cen, n: R[cen][(DE, L(ec.LR['erro']) + str(n + 1))] or ''

# --- A
for i, (nome, vida, ent, domada) in enumerate(A_FICHAS):
    obtido = (v('A', i, 'vida'), v('A', i, 'ent'), str(v('A', i, 'd_res')).startswith('RESERVA · MÁX'))
    P.check(f'A · invocação {i+1} ({nome}): vida {vida}, entrada {ent}, reserva {"domada" if domada else "comum"}',
            obtido == (vida, ent, domada), obtido)
P.check('A · seis tipos custom válidos, sem aviso', all(erro_t('A', n) == '' for n in (1, 2, 3, 4, 5, NT)),
        [erro_t('A', n) for n in (1, 2, 3, 4, 5, NT)])
vazios_t, vazios_l = range(6, NT), range(1, NL + 1)
P.check('A · cartões vazios (só BASE Nenhuma e MESTRE VIU falso) não geram aviso',
        all(erro_t('A', n) == '' for n in vazios_t) and all(erro_l('A', n) == '' for n in vazios_l),
        [n for n in vazios_t if erro_t('A', n)] + [-n for n in vazios_l if erro_l('A', n)])

# --- B
P.check('B · nome igual a tipo do livro é recusado e não muda a domada do livro',
        'repetido' in erro_t('B', 1) and (v('B', 0, 'vida'), str(v('B', 0, 'd_res')).startswith('RESERVA · MÁX')) == (44, True),
        (erro_t('B', 1), v('B', 0, 'vida')))
P.check('B · contraprova: busca sem escape casa "Lua*" com "Lua X" (curingas ativos no Calc)', R['B'][(DE, 'AZ1')] == 0,
        R['B'][(DE, 'AZ1')], nivel='risco')
P.check('B · "Lua*" é literal: só ele usa corpo de criação, "Lua X" continua comum',
        (v('B', 1, 'vida'), v('B', 2, 'vida'), erro_t('B', 2), erro_t('B', 3)) == (57, 44, '', ''),
        (v('B', 1, 'vida'), v('B', 2, 'vida'), erro_t('B', 2), erro_t('B', 3)))
P.check('B · "Eco Duplo" e "eco duplo" recusados; a invocação não ganha corpo de criação',
        'repetido' in erro_t('B', 4) and 'repetido' in erro_t('B', 5) and v('B', 3, 'vida') == 44,
        (erro_t('B', 4), erro_t('B', 5), v('B', 3, 'vida')))
P.check('B · cadastro com campo e sem NOME pede o nome', erro_t('B', 6) == 'Preencha NOME', erro_t('B', 6))

# --- C
txt = lambda i, k: str(v('C', i, f'd_tt{k}') or '')
P.check('C · talento sem base CE 1 no ganho do nível 1: categoria 1, texto próprio, sem erro',
        (v('C', 0, 'ce0'), txt(0, 0)) == (1, 'Texto próprio do sopro.'), (v('C', 0, 'ce0'), txt(0, 0)))
P.check('C · CE 3 no ganho do nível 6 acusa o teto 1', 'vai até a 1' in txt(0, 1), txt(0, 1))
P.check('C · CE 3 no ganho do nível 14 é aceito', v('C', 1, 'ce3') == 3 and 'Categoria' not in txt(1, 3),
        (v('C', 1, 'ce3'), txt(1, 3)))
P.check('C · ganho do nível 18 continua fechado no nível 14 (orçamento)', 'abre no nível 18' in txt(1, 4), txt(1, 4))
P.check('C · cinco talentos com quatro ganhos: contagem acusa excesso', (v('C', 1, 'ttal'), v('C', 1, 'ntal')) == (5, 4)
        and str(v('C', 1, 'd_tal')).startswith('⚠'), (v('C', 1, 'ttal'), v('C', 1, 'ntal'), v('C', 1, 'd_tal')))
P.check('C · base Escama em branco herda CE 3 e o texto do livro', v('C', 2, 'ce3') == 3 and len(txt(2, 3)) > 10,
        (v('C', 2, 'ce3'), txt(2, 3)))
P.check('C · base Eco com CE 1 sobrescreve a categoria', (v('C', 3, 'ce0'), v('C', 3, 'ce2')) == (1, 1),
        (v('C', 3, 'ce0'), v('C', 3, 'ce2')))
P.check('C · contraprova: busca sem escape casa "Ru*na" com "Rubina" (CE 2)', R['C'][(DE, 'AZ1')] == 2,
        R['C'][(DE, 'AZ1')], nivel='risco')
P.check('C · "Ru*na" é literal (CE 1), não confunde "Rubina" (CE 2)', v('C', 2, 'ce0') == 1, v('C', 2, 'ce0'))
P.check('C · última vaga de talento válida no ganho do nível 10', v('C', 1, 'ce2') == 2 and 'Categoria' not in txt(1, 2),
        (v('C', 1, 'ce2'), txt(1, 2)))
P.check('C · mesmo talento custom reutilizado nas 12 invocações (oito restantes + duas primeiras)',
        all(v('C', i, 'ce0') == 1 for i in [0, 1] + list(range(4, 12))), [v('C', i, 'ce0') for i in range(12)])
inval = {5: 'CATEGORIA', 6: 'BASE', 9: 'repetido'}
P.check('C · sem categoria, base inválida e nome do livro são recusados',
        all(t in erro_l('C', n) for n, t in inval.items()), {n: erro_l('C', n) for n in inval})
cat = {R['C'][(DE, L(ec.LC['nome']) + str(r))]: (R['C'][(DE, L(ec.LC['ce']) + str(r))], R['C'][(DE, L(ec.LC['trilha']) + str(r))])
       for r in range(2, nbl + NL + 2)}
P.check('C · catálogo unido traz livro + custom válido e exclui os inválidos',
        all(n in cat for n in ('Leitura', 'Escama', 'Sopro Curto', 'Último Talento', 'Ru*na')) and
        not any(n in cat for n in ('Sem Categoria', 'Base Errada')), sorted(k for k in cat if k))
P.check('C · menu da Trilha aceita só Categoria 1 (Sopro Curto e Eco Leve sim; Muralha e Escama Fina não)',
        cat.get('Sopro Curto', (0, ''))[1] == 'Sopro Curto' and cat.get('Eco Leve', (0, ''))[1] == 'Eco Leve'
        and not cat.get('Muralha', (0, ''))[1] and not cat.get('Escama Fina', (0, ''))[1],
        {k: cat.get(k) for k in ('Sopro Curto', 'Eco Leve', 'Muralha', 'Escama Fina')})

# --- D
dif = [(a1, RB[(a, a1)], RD[(a, a1)]) for (a, a1) in RB if RB[(a, a1)] != RD[(a, a1)]]
P.check(f'D · catálogos custom vazios: as {len(RB)} células das 12 fichas da DADOS_INVOC são iguais ao gerador sem o módulo',
        not dif, dif[:5])
pres = [k for k in cf if k in ('alma', 'autonomia') or k.startswith('f') and k[1:].isdigit()]
P.check('D · alma, autonomia e as nove Famílias de cada invocação continuam iguais', all(
    RB[(DI, L(cf[k]) + str(2 + i))] == RD[(DI, L(cf[k]) + str(2 + i))] for k in pres for i in range(12)), pres)
P.fim(dict(capacidades=[NT, NL]))
