# -*- coding: utf-8 -*-
"""A tabela de golpes do §3.5 da peça 15, remedida contra o bestiário (peça 26).

A tabela que está publicada é da v0.58. Ela tem cinco linhas, e o §12 do
`conferir-invocacoes.py` deriva delas uma JANELA para conferir se a régua da
morte cai dentro. Trocar a regra da morte sem remedir a tabela faz a checagem
medir contra uma escala inventada.

De onde vem cada número deste arquivo — nenhum é chute, e nenhum é meu:

  CHEFE_DANO   manual `Fundamento-MANUAL-v7.docx`, tabela `Inimigos`,
               coluna `Chefe: dano`. Lida com python-docx.
  FAIXAS       o mesmo manual, a tabela de dano de feitiço por Classe.
               A coluna `Rotina` é a unidade `R` em que o §3.5 mede.
  CATEGORIA    peça 26 §4 — fator sobre a linha do manual, e as ações.
  golpe()      peça 26 §4.4 — o mestre rola o dano de uma AÇÃO, e ele é o
               de rodada dividido pelas ações da categoria.
  CRIT         peça 26 §4.4 — "metade do alvo em dado", então dobrar os dados
               soma outra metade: 1,5× na média.
  VULN         peça 15 §3.5 — a área cai UMA VEZ, com vulnerabilidade ×1,5.
  cru/forte    peça 15 §3.6 e §3.7 — as duas fórmulas de vida do corpo.

Roda sem argumento e imprime as sete seções. A casa final dele é o
`conferir-invocacoes.py` do JJK---Project; aqui ele fica porque o container
desta sessão é descartável e a medida não pode morrer com ele.
"""
import math

# --- manual, tabela `Inimigos` ------------------------------------------------
CHEFE_DANO = {2: 17, 5: 39, 10: 75, 15: 111, 20: 147, 25: 183, 30: 219}

# --- manual, dano de feitiço por Classe: (Rotina, num alvo, somando, máxima) ---
FAIXAS = [((1, 4), 13, 13, 18, None),
          ((5, 8), 31, 27, 36, None),
          ((9, 12), 45, 40, 54, None),
          ((13, 16), 63, 54, 72, None),
          ((17, 20), 76, 67, 90, 108),
          ((21, 25), 94, 81, 108, 126),
          ((26, 30), 108, 94, 126, 144)]

# --- peça 26 §4 ---------------------------------------------------------------
CATEGORIA = {'Ronda': (0.25, 1), 'Dupla': (0.50, 1),
             'Alcateia': (1.00, 3), 'Calamidade': (1.50, 5)}

CRIT, VULN = 1.5, 1.5
BASE_TIPO = {'talismã/corpo': 1, 'técnica': 2, 'maldição domada': 3}
NIVEIS = sorted(CHEFE_DANO)


def faixa(nv):
    for (a, b), *resto in FAIXAS:
        if a <= nv <= b:
            return resto
    raise ValueError(nv)


def rotina(nv):
    return faixa(nv)[0]


def meio_para_baixo(x):
    """peça 26 §4.1: o arredondamento é meio para BAIXO, e ele é declarado
    porque vinte e duas das cinquenta e seis células caem em ,5."""
    return math.ceil(x - 0.5)


def dano_rodada(cat, nv):
    return meio_para_baixo(CHEFE_DANO[nv] * CATEGORIA[cat][0])


def golpe(cat, nv):
    return dano_rodada(cat, nv) / CATEGORIA[cat][1]


def cru(base, con, nv):
    """peça 15 §3.6 — h, a fórmula crua. É o corpo do `Coro`."""
    return base + (2 + con) * nv


def forte(base, con, nv):
    """peça 15 §3.7 — `Servo` e o pool da `Matilha`. A Constituição fica FORA
    do multiplicador desde a v0.178."""
    return math.floor(2.5 * (base + 2 * nv) + con * nv)


def titulo(t):
    print('\n' + '=' * 78 + '\n' + t + '\n' + '=' * 78)


# =============================================================================
titulo('1. CONTRA-PROVA — o modelo bate na tabela pronta da peça 26 §4.1?')
PUBLICADO = {(10, 'Ronda'): (97, 19), (20, 'Ronda'): (165, 37), (30, 'Ronda'): (236, 55),
             (10, 'Dupla'): (195, 37), (20, 'Dupla'): (330, 73), (30, 'Dupla'): (472, 109),
             (10, 'Alcateia'): (390, 75), (20, 'Alcateia'): (660, 147),
             (30, 'Alcateia'): (945, 219),
             (10, 'Calamidade'): (585, 112), (20, 'Calamidade'): (990, 220),
             (30, 'Calamidade'): (1417, 328)}
mau = 0
for (nv, cat), (_vida, dano) in sorted(PUBLICADO.items()):
    calc = dano_rodada(cat, nv)
    if calc != dano:
        print(f'  DIVERGE  nv{nv} {cat}: calculei {calc}, a peça publica {dano}')
        mau += 1
print(f'  as {len(PUBLICADO)} células de dano do §4.1 fecham' if not mau
      else f'  {mau} célula(s) divergem — o modelo está errado, pare aqui')

# =============================================================================
titulo('2. O GOLPE ÚNICO DE INIMIGO — a peça 15 §3.5 publica 0,50 R para tudo')
print(f"  {'nv':>3} {'Rotina':>7} | " + ' | '.join(f'{c:>12}' for c in CATEGORIA))
por_cat = {c: [] for c in CATEGORIA}
for nv in NIVEIS:
    cel = []
    for c in CATEGORIA:
        r = golpe(c, nv) / rotina(nv)
        por_cat[c].append(r)
        cel.append(f'{golpe(c, nv):>5.1f} = {r:.2f}R')
    print(f'  {nv:>3} {rotina(nv):>7} | ' + ' | '.join(f'{x:>12}' for x in cel))
print()
for c in CATEGORIA:
    v = por_cat[c]
    print(f'  {c:<11} {min(v):.2f} R a {max(v):.2f} R')
todos = [x for v in por_cat.values() for x in v]
print(f'\n  As quatro juntas: {min(todos):.2f} R a {max(todos):.2f} R — um vão de '
      f'{max(todos)/min(todos):.1f}×,')
print('  e a tabela da v0.58 põe um único 0,50 R no lugar dele.')

# =============================================================================
titulo('3. AS OUTRAS LINHAS, na mesma escala')
LINHAS = {
    'golpe único de `Ronda`': lambda nv: golpe('Ronda', nv),
    'golpe único de `Calamidade`': lambda nv: golpe('Calamidade', nv),
    'golpe único de `Alcateia` (= o capanga, §5)': lambda nv: golpe('Alcateia', nv),
    'golpe único de `Dupla` (o maior da tabela, §4.4)': lambda nv: golpe('Dupla', nv),
    'área de `Alcateia`, com ×1,5': lambda nv: VULN * golpe('Alcateia', nv),
    'dois golpes de `Alcateia` na mesma rodada': lambda nv: 2 * golpe('Alcateia', nv),
    'crítico da `Dupla` (dobra os dados, §4.4)': lambda nv: CRIT * golpe('Dupla', nv),
    'área de `Dupla`, com ×1,5': lambda nv: VULN * golpe('Dupla', nv)}
med = {}
for nome, f in LINHAS.items():
    v = [f(nv) / rotina(nv) for nv in NIVEIS]
    med[nome] = v
    print(f'  {nome:<50} {min(v):.2f} a {max(v):.2f} R   (nv30: {v[-1]:.2f} R)')
print('\n  O que a peça 15 §3.5 publica hoje:')
for o, d in [('golpe único de inimigo (~meia Rotina)', 0.50),
             ('dois golpes na mesma rodada', 1.00),
             ('área de rotina, com ×1,5', 0.75),
             ('área grande, com ×1,5', 1.88),
             ('Expansão de Domínio, acerto garantido', 3.00)]:
    print(f'    {o:<50} {d:.2f} R')
print('\n  `área grande` e `Expansão` não têm derivação em documento nenhum do')
print('  projeto, e a peça 26 §6.4 diz que a Expansão NÃO acrescenta dano — ela')
print('  garante o acerto, o que vale 1,92× de saída efetiva e vira degrau de')
print('  categoria. Nenhum golpe do bestiário chega perto de 3,00 R.')

# =============================================================================
titulo('4. A RÉGUA DE HOJE (5 × h) EM ROTINAS — o §12 confere 2,50 R')
print('  REGUA_R = 5 × AREA_ROTINA = 2,50 R usa h = MEIA ROTINA, que é o ALVO')
print('  de design. O h de uma ficha carrega a Constituição, e some do alvo:\n')
print(f"  {'nv':>3} {'Rotina':>7} | " + ' | '.join('CON {}'.format(c).rjust(22) for c in (0, 3, 6)))
for nv in NIVEIS:
    R = rotina(nv)
    cel = [f'h {cru(2, c, nv):>4} → {5*cru(2, c, nv):>5} = {5*cru(2, c, nv)/R:5.2f} R'
           for c in (0, 3, 6)]
    print(f'  {nv:>3} {R:>7} | ' + ' | '.join(f'{x:>22}' for x in cel))
print()
for c in (0, 3, 6):
    v = [5 * cru(2, c, nv) / rotina(nv) for nv in NIVEIS]
    print(f'  CON {c}: a régua vale de {min(v):.2f} R a {max(v):.2f} R')
print('\n  Nenhuma ficha joga com a régua de 2,50 R que a checagem confere.')

# =============================================================================
titulo('5. OS CORPOS, e quem os apaga com UM golpe (base `técnica`)')
for rotulo, corpo in (('CORPO CRU — o `Coro`', cru),
                      ('CORPO FORTE — `Servo` e o pool da `Matilha`', forte)):
    print(f'\n  {rotulo}')
    print(f"    {'nv':>3} | " + ' | '.join('CON {}'.format(c).rjust(6) for c in (0, 3, 6))
          + '  |  quem apaga (CON 0 / 3 / 6)')
    for nv in NIVEIS:
        vs = [corpo(2, c, nv) for c in (0, 3, 6)]
        quem = []
        for vm in vs:
            mata = [k for k in CATEGORIA if golpe(k, nv) >= vm]
            crit = [k for k in CATEGORIA if CRIT * golpe(k, nv) >= vm and k not in mata]
            quem.append('+'.join(x[:4] for x in mata) if mata else
                        ('só crít ' + '+'.join(x[:4] for x in crit) if crit else 'ninguém'))
        print(f'    {nv:>3} | ' + ' | '.join(f'{v:>6}' for v in vs)
              + '  |  ' + ' / '.join(quem))

# =============================================================================
titulo('6. A JANELA do §12, nível a nível, com a coluna remedida')
print('  piso = 2 × o maior golpe que tem de devolver o corpo de pé')
print('  teto = 2 × o menor golpe que tem de matar em definitivo\n')
COMUNS = ['golpe único de `Ronda`', 'golpe único de `Calamidade`',
          'golpe único de `Alcateia` (= o capanga, §5)',
          'golpe único de `Dupla` (o maior da tabela, §4.4)',
          'área de `Alcateia`, com ×1,5']
MATAM = ['dois golpes de `Alcateia` na mesma rodada',
         'crítico da `Dupla` (dobra os dados, §4.4)']
print(f"  {'nv':>3} | {'maior comum':>11} {'piso':>6} | {'menor que mata':>14} "
      f"{'teto':>6} | {'2,50 R cabe?':>12}")
for i, nv in enumerate(NIVEIS):
    c = max(med[k][i] for k in COMUNS)
    m = min(med[k][i] for k in MATAM)
    piso, teto = 2 * c, 2 * m
    print(f'  {nv:>3} | {c:>11.2f} {piso:>6.2f} | {m:>14.2f} {teto:>6.2f} | '
          f'{"sim" if piso <= 2.5 < teto else "NÃO":>12}')
print('\n  A janela anda com o nível, e uma régua fixa em R não anda com ela.')

# =============================================================================
titulo('7. A REGRA NOVA no corpo cru — de que Constituição para cima ele vive')
print('  régua = a vida máxima daquele corpo; gatilho B = um golpe causa a régua inteira\n')
print(f"  {'nv':>3} | {'maior golpe':>11} {'com área ×1,5':>13} | "
      f"{'CON mín. vs golpe':>17} | {'CON mín. vs área':>16}")


def con_minimo(corpo, alvo, nv):
    for c in range(0, 11):
        if corpo(2, c, nv) > alvo:
            return c
    return None


for nv in NIVEIS:
    g = max(golpe(k, nv) for k in CATEGORIA)
    print(f'  {nv:>3} | {g:>11.1f} {VULN*g:>13.1f} | '
          f'{con_minimo(cru, g, nv):>17} | {con_minimo(cru, VULN*g, nv):>16}')
print('\n  E o mesmo no corpo forte:')
print(f"  {'nv':>3} | {'CON mín. vs golpe':>17} | {'CON mín. vs área':>16}")
for nv in NIVEIS:
    g = max(golpe(k, nv) for k in CATEGORIA)
    print(f'  {nv:>3} | {con_minimo(forte, g, nv):>17} | '
          f'{con_minimo(forte, VULN*g, nv):>16}')
