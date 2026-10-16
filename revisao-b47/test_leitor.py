# -*- coding: utf-8 -*-
"""ler-analise.py (embrião do bot) diante dos avisos dos catálogos custom.

As mensagens não são copiadas à mão: saem das fórmulas que alimentam cada aviso
de catálogo no modelo gerado pelo SHA em teste. Cada mensagem, sozinha, descreve
um cadastro com problema; o leitor tem de reprovar a ficha.

    python revisao-b47/test_leitor.py [--perfil base-v9]
"""
import json
import re

from openpyxl.formula import Tokenizer

import comum

ap = comum.argumentos(__doc__)
ap.add_argument('--com-patch', nargs='?', const='ler-analise-avisos-custom.diff', default=None,
                help='testa cópia temporária com o patch indicado em patches/ (v10: ler-analise-avisos-custom-v10.diff)')
args = ap.parse_args()
p = comum.perfil(args.perfil)
modelo = json.loads(comum.exportar(args.perfil, 'pecas').read_text(encoding='utf-8'))
cel = {a['nome']: {v[0]: v[1] for v in a['celulas']} for a in modelo['layout']['abas']}
an = next(a for a in modelo['layout']['abas'] if a['nome'] == 'ANALISE')
L = comum._linhas_da_aba(an)
A = {l[0]: l for l in L}
if args.com_patch:
    import shutil, subprocess, tempfile
    tmp = tempfile.mkdtemp(prefix='revisao-b47-leitor-')
    shutil.copy(comum.RAIZ / 'ler-analise.py', tmp)
    subprocess.run(['git', 'apply', '--unsafe-paths', '--directory=' + tmp.lstrip('/'),
                    str(comum.AQUI / 'patches' / args.com_patch)], cwd='/', check=True)
    leitor = comum.ler_analise_modulo(tmp + '/ler-analise.py')
    shutil.rmtree(tmp, ignore_errors=True)
else:
    leitor = comum.ler_analise_modulo()
P = comum.Placar('leitor ' + args.perfil + (' com patch' if args.com_patch else ''))
fmt = int(str(A['formato.versao'][1]).lstrip("'"))
print(f'SHA {comum.sha()} · perfil {args.perfil} · formato {fmt}\n')


def fonte(formula):
    """Primeira referência da fórmula do aviso: 'ABA'!$C$2 -> (ABA, C2)."""
    for t in Tokenizer(formula).items:
        if t.type == 'OPERAND' and t.subtype == 'RANGE' and '!' in t.value:
            aba, end = t.value.rsplit('!', 1)
            return aba.strip("'"), end.replace('$', '')
    return None


def mensagens(formula):
    """Literais devolvidos como texto; ignora os que só aparecem em comparação (B2="Alcance")."""
    ts = [t for t in Tokenizer(formula).items if t.type != 'WHITE-SPACE']
    out = set()
    for i, t in enumerate(ts):
        if (t.type != 'OPERAND' or t.subtype != 'TEXT' or len(t.value) <= 6 or '!$' in t.value
                or not re.search(r'[A-Za-zÀ-ú]{3}', t.value)):
            continue
        vizinhos = [ts[j] for j in (i - 1, i + 1) if 0 <= j < len(ts)]
        if any(v.type == 'OPERATOR-INFIX' and v.value in ('=', '<>') for v in vizinhos):
            continue
        out.add(t.value[1:-1].replace('""', '"'))
    return sorted(out)


def avalia(chave, valor):
    ficha = {'formato.versao': {'valor': fmt, 'celula': '', 'parte': 'cabeçalho'},
             chave: {'valor': leitor.normaliza(valor), 'celula': A[chave][2], 'parte': A[chave][3]}}
    return leitor.relatorio(ficha)[0]


resumo = {}
for cat, d in p['catalogos'].items():
    chave = d['aviso'].format(n=1)
    if chave not in A:
        P.check(f'{cat}: aviso do primeiro registro existe', False, chave)
        continue
    origem = fonte(A[chave][1])
    formula = cel.get(origem[0], {}).get(origem[1], '') if origem else ''
    msgs = [m for m in mensagens(formula) if m not in ('Nenhuma', 'Neutra', 'Sim', 'Não', 'Perícia', 'Ofício')]
    P.check(f'{cat}: mensagens encontradas na fórmula de origem {origem}', bool(msgs), formula[:120])
    # O que a ANALISE realmente publica é a fórmula da coluna B aplicada ao texto bruto.
    prefixo = '⚠ ' if '"⚠ "&' in A[chave][1] else ''
    soltas = [m for m in msgs if avalia(chave, prefixo + m) != 'reprovada']
    resumo[cat] = dict(origem=origem, prefixo=bool(prefixo), mensagens=msgs, aceitas=soltas)
    P.check(f'{cat}: leitor reprova cada um dos {len(msgs)} avisos de cadastro', not soltas,
            f'{len(soltas)} aceitos como aprovada, ex.: {soltas[:3]}')
    combinado = prefixo + ' · '.join(msgs[:2])
    P.check(f'{cat}: leitor reprova avisos combinados', avalia(chave, combinado) == 'reprovada', combinado)
    P.check(f'{cat}: aviso vazio não reprova', avalia(chave, '') == 'aprovada')

# Outros avisos custom fora da redução (25 cartões 3a, Caminho, Trilha): mesmo consumidor.
for chave in ['aviso.custom.1', 'aviso.custom.caminho', 'aviso.custom.trilha']:
    if chave not in A:
        continue
    origem = fonte(A[chave][1])
    formula = cel.get(origem[0], {}).get(origem[1], '') if origem else ''
    msgs = set(mensagens(formula))
    linha = re.sub(r'\D', '', origem[1]) if origem else ''
    for t in Tokenizer(formula).items:   # um nível: TEXTJOIN(U2,V2,...) na mesma linha
        if t.type == 'OPERAND' and t.subtype == 'RANGE' and '!' not in t.value and re.sub(r'\D', '', t.value) == linha:
            msgs |= set(mensagens(cel[origem[0]].get(t.value.replace('$', ''), '') or ''))
    prefixo = '⚠ ' if '"⚠ "&' in A[chave][1] else ''
    soltas = sorted(m for m in msgs if avalia(chave, prefixo + m) != 'reprovada')
    resumo[chave] = dict(origem=origem, prefixo=bool(prefixo), mensagens=sorted(msgs), aceitas=soltas)
    P.check(f'{chave} (fora da redução): leitor reprova os {len(msgs)} avisos', not soltas,
            f'{len(soltas)} aceitos, ex.: {soltas[:3]}')

# Valores de erro do Sheets: uma migração que apaga linhas produz #REF!; nenhum deve passar calado.
for chave in [p['catalogos'][c]['aviso'].format(n=1) for c in p['catalogos']] + ['aviso.custom.1', 'defesa',
                                                                                  'custom.melhoria.1.nome']:
    if chave not in A:
        continue
    for erro in ['#REF!', '#N/A', '#NAME?', '#ERROR!']:
        if avalia(chave, erro) != 'reprovada':
            P.check(f'valor de erro {erro} em {chave} reprova a ficha', False,
                    f'parte {A[chave][3]!r}: aceito como aprovada')
            break
    else:
        P.check(f'valores de erro em {chave} reprovam a ficha', True)

# Consistência: todos os catálogos publicam o aviso no mesmo padrão
padroes = {cat: r['prefixo'] for cat, r in resumo.items()}
P.check('mesmo padrão de aviso (com ou sem ⚠) em todos os catálogos', len(set(padroes.values())) <= 1, padroes,
        nivel='risco')

# Nomes custom chegam ao bot como texto literal (impressão digital do cadastro)
for nome in ['007', '1,5', 'VERDADEIRO']:
    v = leitor.normaliza(nome)
    P.check(f'nome custom {nome!r} preservado pelo normaliza', v == nome.strip() and isinstance(v, str), repr(v),
            nivel='risco')
P.fim(dict(perfil=args.perfil, catalogos=resumo))
