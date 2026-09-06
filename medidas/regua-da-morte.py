# -*- coding: utf-8 -*-
"""A tabela de golpes do §3.5 da peça 15, remedida contra o bestiário (peça 26).

A tabela publicada é da v0.58. O §12 do `conferir-invocacoes.py` deriva dela uma
JANELA e confere se a régua da morte cai dentro, então trocar a regra sem remedir
faz a checagem medir contra uma escala inventada.

⚠ A MEDIDA CERTA É A DA ROLAGEM, E NÃO A DO ALVO. O gatilho B da regra da morte
é *"um único golpe causar a régua inteira"* — uma ROLAGEM, não uma média. A peça
26 §4.4 manda o mestre rolar `N` dados mais um fixo, com metade do alvo em dado,
e o máximo dessa expressão fica `1,38×` a `1,45×` acima do alvo em toda faixa.
Medir pela média esconde exatamente a cauda que decide a morte em definitivo.

De onde vem cada número — nenhum é chute, e nenhum é meu:

  FAIXAS      `sistema/05-material/gerador-inimigo/dados.js`, que por sua vez
              copia a tabela `Inimigos` do manual. Conferido contra o docx.
  ROTINA      manual, tabela de dano de feitiço por Classe, coluna `Rotina`.
              É a unidade `R` em que o §3.5 mede.
  CATEGORIAS  peça 26 §4 — o fator é personagens/4 e as ações são personagens
              menos um, piso 1. As duas derivam.
  arred/dado  porte fiel do `make.js` do gerador-inimigo (v0.216). A seção 1
              prova o porte contra a tabela que a peça 26 §4.4 publica.
  CRIT        peça 26 §4.4 — dobra os dados, e não o fixo.
  VULN        peça 15 §3.5 — a área cai UMA VEZ, com vulnerabilidade ×1,5.
  cru/forte   peça 15 §3.6 e §3.7, as duas fórmulas de vida do corpo.

A casa final disto é o `conferir-invocacoes.py` do JJK---Project; aqui ele fica
porque o container da sessão é descartável e a medida não pode morrer com ele.
"""
import math

# --- gerador-inimigo/dados.js: rótulo, de, até, dano do chefe -----------------
FAIXAS = [('2 a 4', 2, 4, 17), ('5 a 8', 5, 8, 39), ('9 a 12', 9, 12, 75),
          ('13 a 16', 13, 16, 111), ('17 a 20', 17, 20, 147),
          ('21 a 25', 21, 25, 183), ('26 a 30', 26, 30, 219)]

# --- manual, a coluna `Rotina` por faixa de Classe ----------------------------
ROTINA = [((1, 4), 13), ((5, 8), 31), ((9, 12), 45), ((13, 16), 63),
          ((17, 20), 76), ((21, 25), 94), ((26, 30), 108)]

# --- peça 26 §4: nome, personagens, fator -------------------------------------
CATEGORIAS = [('Ronda', 1, 0.25), ('Dupla', 2, 0.50),
              ('Alcateia', 4, 1.00), ('Calamidade', 6, 1.50)]

DADOS = [4, 6, 8, 10, 12]
VULN = 1.5
NIVEIS = [2, 5, 10, 15, 20, 25, 30]
CONS = (0, 3, 6)


def arred(x):
    """peça 26 §4.1 — meio para BAIXO, e a regra é declarada porque vinte e duas
    das cinquenta e seis células caem exatamente em ,5."""
    return math.ceil(x - 0.5)


def acoes(pes):
    return max(1, pes - 1)


def rotina(nv):
    for (a, b), r in ROTINA:
        if a <= nv <= b:
            return r
    raise ValueError(nv)


def linha(nv):
    for _, a, b, d in FAIXAS:
        if a <= nv <= b:
            return d
    raise ValueError(nv)


def dado(alvo):
    """Porte fiel do dado() do make.js. Devolve (n, d, fixo); n=0 é número seco."""
    if alvo < 5:
        return (0, 0, arred(alvo))
    meta, bom = alvo / 2, None
    for d in DADOS:
        med = (d + 1) / 2
        n = max(1, round(meta / med))
        if n > 8:
            continue
        fixo = alvo - n * med
        if fixo < 0:
            continue
        inteiro = 0 if abs(fixo - round(fixo)) < 1e-9 else 1
        erro = abs(n * med - meta)
        if (bom is None or inteiro < bom['inteiro']
                or (inteiro == bom['inteiro'] and erro < bom['erro'] - 1e-9)
                or (inteiro == bom['inteiro'] and abs(erro - bom['erro']) < 1e-9
                    and n < bom['n'])):
            bom = {'inteiro': inteiro, 'erro': erro, 'n': n, 'd': d,
                   'fixo': round(fixo)}
    if bom is None:
        n = max(1, round(alvo / 9))
        return (n, 8, max(0, arred(alvo - 4.5 * n)))
    return (bom['n'], bom['d'], bom['fixo'])


def golpe(nv, cat):
    for nome, pes, fator in CATEGORIAS:
        if nome == cat:
            return dado(arred(linha(nv) * fator) / acoes(pes))
    raise ValueError(cat)


def texto(t):
    n, d, f = t
    if n == 0:
        return str(f)
    return f'{n}d{d} + {f}' if f > 0 else f'{n}d{d}'


def media(t, crit=False):
    n, d, f = t
    return f if n == 0 else (2 * n if crit else n) * (d + 1) / 2 + f


def maximo(t, crit=False):
    n, d, f = t
    return f if n == 0 else (2 * n if crit else n) * d + f


def p_alcanca(t, alvo, crit=False):
    """P(uma rolagem de NdX + fixo chegar a `alvo`), exata por convolução."""
    n, d, f = t
    if n == 0:
        return 1.0 if f >= alvo else 0.0
    if crit:
        n *= 2
    dist = {0: 1}
    for _ in range(n):
        nova = {}
        for s, c in dist.items():
            for face in range(1, d + 1):
                nova[s + face] = nova.get(s + face, 0) + c
        dist = nova
    return sum(c for s, c in dist.items() if s + f >= alvo) / d ** n


def cru(base, con, nv):
    """peça 15 §3.6 — h, a fórmula crua. É o corpo do `Coro`."""
    return base + (2 + con) * nv


def forte(base, con, nv):
    """peça 15 §3.7 — `Servo` e o pool da `Matilha`. A Constituição fica FORA do
    multiplicador desde a v0.178."""
    return math.floor(2.5 * (base + 2 * nv) + con * nv)


def titulo(t):
    print('\n' + '=' * 84 + '\n' + t + '\n' + '=' * 84)


# =============================================================================
titulo('1. CONTRA-PROVA — o porte reproduz o que a peça 26 publica?')
PUB_DANO = {(10, 'Ronda'): 19, (20, 'Ronda'): 37, (30, 'Ronda'): 55,
            (10, 'Dupla'): 37, (20, 'Dupla'): 73, (30, 'Dupla'): 109,
            (10, 'Alcateia'): 75, (20, 'Alcateia'): 147, (30, 'Alcateia'): 219,
            (10, 'Calamidade'): 112, (20, 'Calamidade'): 220, (30, 'Calamidade'): 328}
PUB_DADO = {'Ronda': '6d8 + 28', 'Dupla': '8d12 + 57',
            'Alcateia': '8d8 + 37', 'Calamidade': '6d10 + 33'}
mau = 0
for (nv, cat), esperado in sorted(PUB_DANO.items()):
    fator = [c[2] for c in CATEGORIAS if c[0] == cat][0]
    got = arred(linha(nv) * fator)
    if got != esperado:
        print(f'  DIVERGE  §4.1 nv{nv} {cat}: calculei {got}, a peça publica {esperado}')
        mau += 1
for cat, esperado in PUB_DADO.items():
    got = texto(golpe(30, cat))
    if got != esperado:
        print(f'  DIVERGE  §4.4 {cat}: calculei {got}, a peça publica {esperado}')
        mau += 1
print(f'  as {len(PUB_DANO)} células de dano do §4.1 e as {len(PUB_DADO)} expressões '
      f'de dado do §4.4 fecham' if not mau else f'  {mau} divergência(s) — PARE')

# =============================================================================
titulo('2. A CAUDA — é ela que o gatilho B lê, e a tabela da v0.58 não a tinha')
print(f"  {'faixa':<9} {'categoria':<11} {'expressão':<12} {'alvo':>6} {'média':>7} "
      f"{'máximo':>7} {'máx/alvo':>9}")
razoes = []
for rot, de, ate, dano in FAIXAS:
    for nome, pes, fator in CATEGORIAS:
        t = golpe(de, nome)
        alvo = arred(dano * fator) / acoes(pes)
        mx = maximo(t)
        if t[0]:                      # célula de número seco não tem cauda
            razoes.append(mx / alvo)
        print(f'  {rot:<9} {nome:<11} {texto(t):<12} {alvo:>6.1f} {media(t):>7.1f} '
              f'{mx:>7} {mx/alvo:>8.2f}×')
print(f'\n  Nas {len(razoes)} células que rolam dado, o máximo de UMA rolagem fica de')
print(f'  {min(razoes):.2f}× a {max(razoes):.2f}× acima do alvo. É esse o `1,4× a 1,5×` do handoff — ele')
print('  é a folga do DADO sobre o próprio alvo, e não a tabela da v0.58')
print('  exagerando o dano real. A única célula sem cauda é a `Ronda` do nível 2,')
print('  que fica em número seco pelo piso de 5 do §4.4.')

# =============================================================================
titulo('3. O GOLPE EM ROTINAS — a peça 15 §3.5 publica um 0,50 R para tudo')
print(f"  {'nv':>3} {'Rotina':>7} | " + ' | '.join(f'{c[0]:>18}' for c in CATEGORIAS))
faixa_r = []
for nv in NIVEIS:
    R, cel = rotina(nv), []
    for nome, _, _ in CATEGORIAS:
        t = golpe(nv, nome)
        faixa_r += [media(t) / R, maximo(t) / R]
        cel.append(f'{media(t)/R:.2f}R máx {maximo(t)/R:.2f}R')
    print(f'  {nv:>3} {R:>7} | ' + ' | '.join(f'{x:>18}' for x in cel))
print(f'\n  De {min(faixa_r):.2f} R a {max(faixa_r):.2f} R — um vão de {max(faixa_r)/min(faixa_r):.1f}×,')
print('  e a tabela da v0.58 põe um único 0,50 R no lugar dele.')
print('\n  `área grande` (1,88 R) e `Expansão de Domínio` (3,00 R) não têm derivação')
print('  em documento nenhum do projeto, e a peça 26 §6.4 diz que a Expansão NÃO')
print('  acrescenta dano: ela garante o acerto, o que vale 1,92× de saída efetiva')
print('  e vira degrau de categoria. Nada no bestiário chega a 3,00 R.')

# =============================================================================
titulo('4. A RÉGUA DE HOJE (5 × h) EM ROTINAS — o §12 confere 2,50 R')
print('  REGUA_R = 5 × AREA_ROTINA usa h = MEIA ROTINA, que é o ALVO de design.')
print('  O h de uma ficha carrega a Constituição, e sai do alvo:\n')
for con in CONS:
    v = [5 * cru(2, con, nv) / rotina(nv) for nv in NIVEIS]
    print(f'  CON {con}: a régua vale de {min(v):.2f} R a {max(v):.2f} R')
print('\n  Nenhuma ficha joga com a régua de 2,50 R que a checagem confere.')

# =============================================================================
titulo('5. QUEM DESTRÓI CADA CORPO COM UMA ROLAGEM (base `técnica`)')


def rotulo(t, vm, mult=1.0):
    alvo = math.ceil(vm / mult)
    p, pc = p_alcanca(t, alvo), p_alcanca(t, alvo, crit=True)
    if p >= 0.999:
        return 'sempre'
    if p > 0:
        return f'{p*100:.0f}%'
    if pc > 0:
        return f'só crít {pc*100:.0f}%'
    return 'nunca'


for nome_c, corpo in (('CORPO CRU — o `Coro`', cru),
                      ('CORPO FORTE — `Servo` e o pool da `Matilha`', forte)):
    for mult, como in ((1.0, 'golpe único'), (VULN, 'área, com a vulnerabilidade ×1,5')):
        print(f'\n  {nome_c}  ·  {como}')
        print(f"    {'nv':>3} {'CON':>4} {'vida':>5} | "
              + ' | '.join(f'{c[0]:>13}' for c in CATEGORIAS))
        for nv in NIVEIS:
            for con in CONS:
                vm = corpo(2, con, nv)
                cel = [rotulo(golpe(nv, n), vm, mult) for n, _, _ in CATEGORIAS]
                print(f'    {nv:>3} {con:>4} {vm:>5} | '
                      + ' | '.join(f'{x:>13}' for x in cel))
