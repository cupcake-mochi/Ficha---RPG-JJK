# -*- coding: utf-8 -*-
"""Estrutura do módulo de entidades sobre o gerador real (sem Calc, sem Google).

Para cada par de capacidades: contrato ANALISE 10 preservado e chaves novas só no fim; consumidores
ligados aos catálogos unidos; nenhum resto das tabelas antigas; diferenças restritas ao previsto;
cartões sem sobreposição; primeira/última vaga; tamanho.

    python revisao-b47/cd-entidades/test_entidades_estrutura.py --pares 10x20 5x7 1x1
"""
import argparse
import re

from openpyxl.utils import get_column_letter as L
from openpyxl.utils.cell import range_boundaries

import comum_cd as c
import entidades_custom as ec

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--pares', nargs='+', default=['10x20', '5x7', '1x1'])
args = ap.parse_args()
P = c.Placar('entidades estrutura')
m_base, _ = c.exportar(None)
base = c.carregar(m_base)
cb = c.celulas(base)
an_base = [(cb['ANALISE'].get(f'A{r}'), cb['ANALISE'].get(f'B{r}'), cb['ANALISE'].get(f'C{r}'), cb['ANALISE'].get(f'D{r}'))
           for r in range(2, 1 + sum(1 for k in cb['ANALISE'] if re.fullmatch(r'A\d+', k)))]
print(f'SHA {c.sha()} · ANALISE base {len(an_base)} chaves\n')


def menus(modelo, aba):
    a = next(x for x in modelo['layout']['abas'] if x['nome'] == aba)
    return a.get('menus', [])


for par in args.pares:
    nt, nl = map(int, par.split('x'))
    m, trp = c.exportar(nt, nl)
    mod, tr = c.carregar(m), c.carregar(trp)
    cm = c.celulas(mod)
    tag = f'[{nt}/{nl}]'
    # 1. contrato
    an = [(cm['ANALISE'].get(f'A{r}'), cm['ANALISE'].get(f'B{r}'), cm['ANALISE'].get(f'C{r}'), cm['ANALISE'].get(f'D{r}'))
          for r in range(2, 1 + sum(1 for k in cm['ANALISE'] if re.fullmatch(r'A\d+', k)))]
    P.check(f'{tag} as {len(an_base)} linhas da ANALISE 10 continuam idênticas e na mesma ordem', an[:len(an_base)] == an_base,
            next((i for i, (x, y) in enumerate(zip(an, an_base)) if x != y), None))
    novas = an[len(an_base):]
    esperado = nt * (len(ec.CAMPOS['tipo']) + 1) + nl * (len(ec.CAMPOS['talento']) + 1)
    P.check(f'{tag} {esperado} chaves novas, únicas, só de custom.tipo_entidade/talento_entidade',
            len(novas) == esperado and len({k for k, *_ in an}) == len(an) and
            all(re.match(r'^(aviso\.)?custom\.(tipo|talento)_entidade\.\d+', k) for k, *_ in novas), len(novas))
    for kind, n in [('tipo', 1), ('tipo', nt), ('talento', 1), ('talento', nl)]:
        k = f'custom.{ec.CHAVE[kind]}.{n}.nome'
        P.check(f'{tag} vaga {n} de {kind} exportada', any(x[0] == k for x in novas), k)
    # a coluna C é texto-fórmula (="'CONFIGURAÇÃO'!E1739"), como nas linhas do custom_pecas
    fontes = [re.sub(r'^="(.*)"$', r'\1', x[2] or '') for x in novas if x[3] == 'configuração']
    P.check(f'{tag} cada campo novo lê uma célula própria da CONFIGURAÇÃO', len(fontes) == len(set(fontes))
            and all(f.startswith("'CONFIGURAÇÃO'!") for f in fontes), len(fontes))
    # 2. consumidores
    alvo_t, alvo_l = (tr['catalogos'][k].split('!')[1].replace('$', '') for k in ('tipo_entidade', 'talento_entidade'))
    ant = [(kk, vv) for kk, vv in cm['DADOS_INVOC'].items() if isinstance(vv, str) and
           re.search(r'\$?(Corpo amaldiçoado de criação|Shikigami de criação|Maldição domada)"', vv) and '="' in vv and
           re.search(r'\$[A-Z]+\d+="(Corpo amaldiçoado de criação|Shikigami de criação|Maldição domada)"', vv)]
    P.check(f'{tag} nenhuma comparação de tipo por nome restou na DADOS_INVOC', not ant, ant[:2])
    mi = menus(mod, 'INVOCAÇÕES')
    tipos_m = [x for x in mi if ec.NOME in x['formula'] and alvo_t.split(':')[0][:1] in x['formula']]
    P.check(f'{tag} menus de tipo e de talento das 12 invocações apontam para {ec.NOME}',
            sum(1 for x in mi if ec.NOME in x['formula']) >= 3 and
            not any("DADOS_INVOC'!" in x['formula'] or 'DADOS_INVOC!' in x['formula']
                    for x in mi if x in [y for y in menus(base, 'INVOCAÇÕES') if 'tipos' in str(y)]),
            [x['formula'] for x in mi if ec.NOME in x['formula']][:3])
    P.check(f'{tag} buscas nos catálogos unidos escapam curingas do nome', all(
        'SUBSTITUTE(' in vv for cels in cm.values() for vv in cels.values()
        if isinstance(vv, str) and 'VLOOKUP(' in vv and (alvo_t in vv.replace('$', '') or alvo_l in vv.replace('$', ''))))
    # 3. diferenças restritas
    colf = tr['geo']['colf']
    previstas = {L(colf[k]) for k in ('cri', 'ent', 'd_res')} | {L(colf[k]) for k in colf
                                                                    if re.fullmatch(r'(ce|d_tt|d_xt)\d+', k)}
    dif = {}
    for aba in cb:
        for a1 in set(cb[aba]) | set(cm.get(aba, {})):
            if cb[aba].get(a1) != cm[aba].get(a1):
                dif.setdefault(aba, set()).add(a1)
    fora = {aba: sorted(x for x in cels if not (aba == 'DADOS_INVOC' and re.sub(r'\d', '', x) in previstas))
            for aba, cels in dif.items() if aba not in ('CONFIGURAÇÃO', 'ANALISE')}
    fora = {k: v for k, v in fora.items() if v}
    P.check(f'{tag} fora da CONFIGURAÇÃO/ANALISE só mudam cri/ent/d_res e as consultas de talento',
            not fora, {k: v[:6] for k, v in fora.items()})
    acima = [a1 for a1 in dif.get('CONFIGURAÇÃO', ()) if int(re.sub(r'\D', '', a1)) < tr['inicio'] - 2]
    P.check(f'{tag} CONFIGURAÇÃO só muda a partir do bloco novo (linha {tr["inicio"] - 2})', not acima, acima[:5])
    # 4. cartões
    cfg = next(a for a in mod['layout']['abas'] if a['nome'] == 'CONFIGURAÇÃO')
    ocup, sob = set(), []
    for reg in cfg['mescladas']:
        c1, r1, c2, r2 = range_boundaries(reg)
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                if (rr, cc) in ocup:
                    sob.append(reg)
                ocup.add((rr, cc))
    P.check(f'{tag} mesclagens da CONFIGURAÇÃO sem sobreposição', not sob, sob[:3])
    P.check(f'{tag} CONFIGURAÇÃO termina no fim do bloco ({tr["fim"]})', cfg['linhas'] == tr['fim'], cfg['linhas'])
    novas_est = [x for x in cfg.get('esticam', []) if all(int(re.sub(r'\D', '', a)) >= tr['inicio'] for a in x['gatilhos'])]
    pares = (nt + 1) // 2 + (nl + 1) // 2
    alvos_txt = {g[k] for kind, campos in (('tipo_entidade', ('definicao', 'efeito')), ('talento_entidade', ('requisitos', 'efeito')))
                 for g in tr['registros'][kind] for k in campos}
    P.check(f'{tag} áreas de texto esticam: 2 por par de cartões ({2 * pares}), cobrindo todos os textos',
            len(novas_est) == 2 * pares and {a for x in novas_est for a in x['gatilhos']} == alvos_txt, len(novas_est))
    nova = next(a for a in mod['layout']['abas'] if a['nome'] == ec.NOME)
    P.check(f'{tag} {ec.NOME} oculta, paleta fixa, {nova["linhas"]} linhas × {nova["colunas"]} colunas',
            nova['estado'] == 'hidden' and nova['paleta_fixa'] and nova['linhas'] <= max(nt, nl) + 20)
    P.check(f'{tag} comparações trocadas nas 12 fichas', all(v == 12 for v in tr['consumidores']['comparacoes'].values()),
            tr['consumidores']['comparacoes'])
P.fim()
