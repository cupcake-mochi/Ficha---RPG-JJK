# -*- coding: utf-8 -*-
"""Contrato ANALISE diante da redução de capacidade.

Compara o contrato exportado pelo SHA em teste com a fixture do formato 9 (4187df3).
As quantidades vêm do perfil (casos/perfis.json), não do código revisado.

    python revisao-b47/test_contrato.py --perfil base-v9
    python revisao-b47/test_contrato.py --perfil simulado-alvo        # simulação, espera falhas
    python revisao-b47/test_contrato.py --perfil alvo-real-separado   # commit A, se separar tipos
"""
import re
from collections import defaultdict

import comum

ap = comum.argumentos(__doc__)
args = ap.parse_args()
p = comum.perfil(args.perfil)
caminho = args.analise or comum.exportar(args.perfil, 'analise')
L = comum.linhas_analise(caminho)
v9 = comum.carregar_v9()
V9 = {k: (parte, aba) for k, parte, aba in v9['chaves']}
P = comum.Placar('contrato ' + args.perfil)
print(f'SHA {comum.sha()} · perfil {args.perfil} · {len(L)} linhas · {caminho}\n')

# 1. Forma das linhas
chaves = [l[0] for l in L]
P.check('quatro colunas por linha', all(len(l) == 4 for l in L))
P.check('nenhuma chave vazia', all(isinstance(k, str) and k for k in chaves))
dup = [k for k in set(chaves) if chaves.count(k) > 1] if len(set(chaves)) != len(chaves) else []
P.check('chaves únicas', not dup, dup[:5])
P.check('chaves minúsculas, sem acento nem espaço', all(re.fullmatch(r'[a-z0-9_.]+', k) for k in chaves),
        [k for k in chaves if not re.fullmatch(r'[a-z0-9_.]+', k)][:5])
A = {l[0]: l for l in L}
fmt = A.get('formato.versao', [None, None])[1]
try:
    fmt_n = int(str(fmt).lstrip("'"))
except ValueError:
    fmt_n = None
P.check('formato.versao numérico', fmt_n is not None, fmt)

# 2. Leitor reconhece o formato emitido
leitor = comum.ler_analise_modulo()
P.check('ler-analise.py conhece o formato emitido', fmt_n in leitor.FORMATOS_CONHECIDOS,
        f'formato {fmt_n}; conhecidos {sorted(leitor.FORMATOS_CONHECIDOS)}')

# 3. Catálogos: exatamente 1..capacidade, todos os campos e um aviso por registro
vistos = defaultdict(set)
for k in chaves:
    m = comum.RE_CATALOGO.match(k)
    if m:
        vistos[m[1]].add(int(m[2]))
for cat, d in p['catalogos'].items():
    cap = d['capacidade']
    esperado = {d['chave'].format(n=n, campo=c) for n in range(1, cap + 1) for c in d['campos']}
    esperado |= {d['aviso'].format(n=n) for n in range(1, cap + 1)}
    faltam = sorted(esperado - set(chaves))
    P.check(f'{cat}: {cap} registros com {len(d["campos"])} campos e aviso', not faltam, faltam[:4])
    sobra = sorted(n for n in vistos.get(cat, ()) if n > cap)
    P.check(f'{cat}: nenhuma chave acima de {cap}', not sobra, f'{len(sobra)} números, primeiro {sobra[:1]}')
    # fonte de cada campo: célula própria em CONFIGURAÇÃO; aviso numa tabela DADOS_*
    fontes = [A[d['chave'].format(n=n, campo=c)][2] for n in range(1, cap + 1) for c in d['campos']
              if d['chave'].format(n=n, campo=c) in A]
    P.check(f'{cat}: entradas lidas da CONFIGURAÇÃO', all(comum.aba_de(f) == 'CONFIGURAÇÃO' for f in fontes))
    P.check(f'{cat}: nenhuma célula de origem compartilhada entre chaves', len(set(fontes)) == len(fontes),
            f'{len(fontes) - len(set(fontes))} repetidas')
    avisos = [A[d['aviso'].format(n=n)] for n in range(1, cap + 1) if d['aviso'].format(n=n) in A]
    P.check(f'{cat}: avisos na parte "aviso" e em tabela DADOS_*',
            all(a[3] == 'aviso' and comum.aba_de(a[2]).startswith('DADOS_') for a in avisos))
extras = sorted(set(vistos) - set(p['catalogos']))
P.check('nenhum catálogo inesperado na ANALISE', not extras, extras)

# 4. Fora dos catálogos nada some, muda de parte ou de aba; ordem relativa preservada
fora_v9 = [k for k in V9 if not comum.RE_CATALOGO.match(k)]
fora = [k for k in chaves if not comum.RE_CATALOGO.match(k)]
sumiram = [k for k in fora_v9 if k not in A]
P.check(f'{len(fora_v9)} chaves fora dos catálogos preservadas', not sumiram, sumiram[:5])
sentido = [k for k in fora_v9 if k in A and k != 'formato.versao'
           and (A[k][3], comum.aba_de(A[k][2])) != V9[k]]
P.check('mesma parte e aba de origem nas chaves preservadas', not sentido,
        [(k, V9[k], (A[k][3], comum.aba_de(A[k][2]))) for k in sentido[:3]])
ordem_v9 = [k for k in fora_v9 if k in A]
ordem = [k for k in fora if k in V9]
P.check('ordem relativa das chaves preservadas', ordem == ordem_v9)

# 5. Regra do contrato: retirar chaves exige formato novo; chave mantida não muda de sentido
removidas = [k for k in V9 if k not in A]
if removidas:
    P.check(f'{len(removidas)} chaves do formato 9 retiradas -> formato.versao > 9',
            fmt_n is not None and fmt_n > 9, f'formato emitido {fmt_n}')
P.check(f'formato.versao >= {p["formato_minimo"]} (perfil)', fmt_n is not None and fmt_n >= p['formato_minimo'], fmt_n)
mantidas_cat = [k for k in V9 if comum.RE_CATALOGO.match(k) and k in A]
reuso = [k for k in mantidas_cat if (A[k][3], comum.aba_de(A[k][2])) != V9[k]]
P.check('chaves de catálogo mantidas conservam parte e aba', not reuso, reuso[:3])
P.fim(dict(perfil=args.perfil, linhas=len(L), formato=fmt_n, removidas=len(removidas)))
