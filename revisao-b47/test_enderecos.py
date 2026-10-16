# -*- coding: utf-8 -*-
"""Endereços fixos que não acompanham a capacidade.

1. Faixas que apontam para as tabelas de catálogo (DADOS_PROGRESSAO/CRIACAO/MELHORIAS/
   RESTRICOES) e terminam além da última linha com dado da coluna (+1 de folga): sinal de
   número de linha escrito à mão para a capacidade antiga.
2. Faixa vazia contínua na CONFIGURAÇÃO (cartões retirados que deixaram linhas, alturas e fundo).
3. Nomes custom usados como critério de COUNTIF sem o escape de * ? ~ (nomes literais).

    python revisao-b47/test_enderecos.py --perfil simulado-alvo
"""
import json
import re
from collections import Counter, defaultdict

from openpyxl.formula import Tokenizer
from openpyxl.utils import column_index_from_string as ci, get_column_letter as gl

import comum

ap = comum.argumentos(__doc__)
ap.add_argument('--folga', type=int, default=1)
ap.add_argument('--buraco', type=int, default=10, help='linhas vazias toleradas dentro de uma faixa')
ap.add_argument('--faixa-morta', type=int, default=100, help='linhas vazias seguidas toleradas na CONFIGURAÇÃO')
args = ap.parse_args()
modelo = json.loads(comum.exportar(args.perfil, 'pecas').read_text(encoding='utf-8'))
abas = {a['nome']: a for a in modelo['layout']['abas']}
P = comum.Placar('enderecos ' + args.perfil)
ALVOS = [n for n in ('DADOS_PROGRESSAO', 'DADOS_CRIACAO', 'DADOS_MELHORIAS', 'DADOS_RESTRICOES') if n in abas]
print(f'SHA {comum.sha()} · perfil {args.perfil} · tabelas {ALVOS}\n')

ultima, linhas_com_dado, spill = {}, {}, set()
for nome in ALVOS:
    u, rows = defaultdict(int), defaultdict(set)
    for coord, valor, *_ in abas[nome]['celulas']:
        if valor not in (None, ''):
            m = re.fullmatch(r'([A-Z]+)(\d+)', coord)
            u[ci(m[1])] = max(u[ci(m[1])], int(m[2]))
            rows[ci(m[1])].add(int(m[2]))
            if isinstance(valor, str) and re.search(r'\b(FILTER|SORT|UNIQUE|ARRAYFORMULA)\(', valor.upper()):
                spill.add((nome, ci(m[1])))   # coluna preenchida por derramamento: fim dinâmico
    ultima[nome], linhas_com_dado[nome] = u, rows


def maior_buraco(dono, c1, r1, c2, r2):
    """Maior sequência sem dado ENTRE linhas com dado, dentro da faixa."""
    cheias = sorted({r for c in range(c1, c2 + 1) for r in linhas_com_dado[dono].get(c, ()) if r1 <= r <= r2})
    return max((b - a - 1 for a, b in zip(cheias, cheias[1:])), default=0), cheias

RE_FAIXA = re.compile(r'^\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)$')


RE_TEXTO = re.compile(r"'?([A-Z_ÇÃÕÉÊÍÓÚ ]+)'?!(\$?[A-Z]{1,3}\$?\d+:\$?[A-Z]{1,3}\$?\d+)")
em_texto = Counter()


def faixas(formula, aba_atual):
    for t in Tokenizer(formula).items:
        if t.type == 'OPERAND' and t.subtype == 'RANGE':
            dono, end = (t.value.rsplit('!', 1) if '!' in t.value else (aba_atual, t.value))
            yield dono.strip("'").replace("''", "'"), end, t
        elif t.type == 'OPERAND' and t.subtype == 'TEXT':
            # Endereço dentro de texto (INDIRECT): troca_refs não o reescreve.
            for dono, end in RE_TEXTO.findall(t.value.replace('""', '"')):
                if dono in ALVOS:
                    em_texto[(aba_atual, dono, end.replace('$', ''))] += 1
                    yield dono, end, t


def argumentos_de(ts, i):
    """Fatias de tokens de cada argumento da função aberta em ts[i]."""
    partes, atual, prof = [], [], 0
    for x in ts[i + 1:]:
        if x.subtype == 'OPEN' and x.type in ('FUNC', 'PAREN', 'ARRAY'):
            prof += 1
        elif x.subtype == 'CLOSE' and x.type in ('FUNC', 'PAREN', 'ARRAY'):
            if prof == 0:
                partes.append(atual)
                return partes
            prof -= 1
        elif x.type == 'SEP' and x.subtype == 'ARG' and prof == 0:
            partes.append(atual)
            atual = []
            continue
        if x.type != 'WHITE-SPACE':
            atual.append(x)
    return partes


def resolve(ref, aba_atual):
    dono, end = (ref.rsplit('!', 1) if '!' in ref else (aba_atual, ref))
    return dono.strip("'").replace("''", "'"), end.replace('$', '')


# Células de NOME custom: a própria ANALISE diz onde moram; espelhos nas tabelas ocultas também contam.
an = comum._linhas_da_aba(abas['ANALISE'])
RE_NOME = re.compile(r'^(custom\.(familia|melhoria|restricao|treino|pericia|oficio)\.\d+|custom\.\d+|'
                     r'personagem\.(pericia|oficio)_custom\.\d+)\.nome$')
nomes_custom = {}
for k, v, c, parte in an:
    m = RE_NOME.match(k or '')
    if m and isinstance(v, str):
        for t in Tokenizer(v).items:
            if t.type == 'OPERAND' and t.subtype == 'RANGE':
                nomes_custom[resolve(t.value, 'ANALISE')] = re.sub(r'\.\d+.*', '', k)
                break
for _ in range(2):
    for nome in ALVOS:
        for coord, v, *_ in abas[nome]['celulas']:
            if not (isinstance(v, str) and v.startswith('=')) or (nome, coord) in nomes_custom:
                continue
            if re.search(r'COUNTIF|MATCH|LOOKUP|TEXTJOIN', v.upper()) or len(v) > 160:
                continue
            for t in Tokenizer(v).items:
                if t.type == 'OPERAND' and t.subtype == 'RANGE' and resolve(t.value, nome) in nomes_custom:
                    nomes_custom[(nome, coord)] = nomes_custom[resolve(t.value, nome)]
                    break
print(f'{len(nomes_custom)} células de nome custom (entrada e espelhos)')


alem, buracos = Counter(), Counter()
exemplos = {}
criterios = Counter()
for nome, aba in abas.items():
    formulas = [(c, v) for c, v, *_ in aba['celulas'] if isinstance(v, str) and v.startswith('=')]
    formulas += [('menu ' + str(m.get('onde'))[:20], '=' + m['formula']) for m in aba.get('menus', [])
                 if isinstance(m.get('formula'), str) and m.get('tipo') == 'list']
    for coord, f in formulas:
        try:
            ts = Tokenizer(f).items
        except Exception:
            continue
        for dono, end, _ in faixas(f, nome):
            m = RE_FAIXA.match(end)
            if dono not in ultima or not m:
                continue
            c1, r1, c2, r2 = ci(m[1]), int(m[2]), ci(m[3]), int(m[4])
            if any((dono, c) in spill for c in range(c1, c2 + 1)):
                continue
            fim = max(ultima[dono].get(c, 0) for c in range(c1, c2 + 1))
            if r2 > fim + args.folga:
                chave = (dono, end.replace('$', ''), fim)
                alem[chave] += 1
                exemplos.setdefault(chave, f'{nome}!{coord}')
            buraco, _ = maior_buraco(dono, c1, r1, c2, r2)
            if buraco > args.buraco:
                chave = (dono, end.replace('$', ''), buraco)
                buracos[chave] += 1
                exemplos.setdefault(chave, f'{nome}!{coord}')
        # Nome custom cru como critério: COUNTIF/MATCH/VLOOKUP tratam * ? ~ como curingas
        for i, t in enumerate(ts):
            if t.type != 'FUNC' or t.subtype != 'OPEN':
                continue
            fn = t.value.upper()
            if fn not in ('COUNTIF(', 'COUNTIFS(', 'MATCH(', 'VLOOKUP(', 'XLOOKUP('):
                continue
            partes = argumentos_de(ts, i)
            idx = range(1, len(partes), 2) if fn.startswith('COUNTIF') else [0]
            for k in idx:
                if k < len(partes) and len(partes[k]) == 1 and partes[k][0].subtype == 'RANGE':
                    alvo = resolve(partes[k][0].value, nome)
                    if alvo in nomes_custom:
                        criterios[(nome, fn[:-1], nomes_custom[alvo])] += 1
                        exemplos.setdefault(('crit', nome, fn[:-1], nomes_custom[alvo]), f'{nome}!{coord}')

P.check(f'faixas sobre as tabelas de catálogo terminam junto dos dados (folga {args.folga})', not alem,
        '; '.join(f'{d}!{e} (dados até {fim}) ×{n} ex. {exemplos[(d, e, fim)]}'
                  for (d, e, fim), n in alem.most_common(8)))
P.check(f'faixas sobre as tabelas de catálogo sem buraco interno > {args.buraco} linhas', not buracos,
        '; '.join(f'{d}!{e} (buraco de {b}) ×{n} ex. {exemplos[(d, e, b)]}'
                  for (d, e, b), n in buracos.most_common(8)), nivel='risco')

cfg = abas['CONFIGURAÇÃO']
cheias = {int(re.sub(r'\D', '', c)) for c, v, *_ in cfg['celulas'] if v not in (None, '') and re.fullmatch(r'[A-Z]+\d+', c)}
maior, corrida, inicio_maior, inicio = 0, 0, 0, 0
for r in range(1, cfg['linhas'] + 1):
    if r in cheias:
        corrida = 0
    else:
        corrida += 1
        if corrida == 1:
            inicio = r
        if corrida > maior:
            maior, inicio_maior = corrida, inicio
longas = sorted((len(v), f'{n}!{c}') for n, a in abas.items() for c, v, *_ in a['celulas']
                if isinstance(v, str) and v.startswith('=') and len(v) > 8192)
P.check('nenhuma fórmula acima de 8.192 caracteres (limite do xlsx; o LibreOffice devolve #NAME?)', not longas,
        f'{len(longas)} fórmulas, maior {longas[-1] if longas else ""}', nivel='risco')
P.check('nenhum endereço de catálogo escrito como texto (INDIRECT)', not em_texto,
        '; '.join(f'{a} -> {d}!{e} ×{n}' for (a, d, e), n in em_texto.most_common(8)), nivel='risco')
P.check(f'CONFIGURAÇÃO sem faixa vazia acima de {args.faixa_morta} linhas', maior <= args.faixa_morta,
        f'{maior} linhas vazias a partir da {inicio_maior} (de {cfg["linhas"]})', nivel='risco')

P.check('nomes custom não entram crus como critério de COUNTIF/MATCH/VLOOKUP (* ? ~ literais)', not criterios,
        '; '.join(f'{fn} em {a} sobre {grupo} ×{n} ex. {exemplos[("crit", a, fn, grupo)]}'
                  for (a, fn, grupo), n in criterios.most_common(10)), nivel='risco')
P.fim(dict(perfil=args.perfil, alem=[[*k, n, exemplos[k]] for k, n in alem.most_common()],
           buracos=[[*k, n, exemplos[k]] for k, n in buracos.most_common()],
           faixa_morta=[maior, inicio_maior, cfg['linhas']],
           enderecos_em_texto=[[*k, n] for k, n in em_texto.most_common()],
           criterios_crus=[[*k, n] for k, n in criterios.most_common()]))
