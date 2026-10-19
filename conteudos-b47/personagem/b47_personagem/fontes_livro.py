"""Adaptador de leitura da base B47; não executa monta.py nem grava saídas.

Os catálogos normalizados existentes são a fonte das identidades e exceções.
Requisitos abaixo são transcrições explícitas, nunca interpretação de prosa.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'ficha-v01'))
import ficha_amaldicoada as fa
import ficha_invocacoes as iv

FAIXAS = {'personagem': ('classe_0', 'classes_1_a_5', 'classes_6_e_7'),
          'entidade': ('classe_0', 'classes_1_a_5', 'classe_6', 'classe_7')}


def carregar():
    r, entidade = fa.regras(), iv.regras()
    tec = json.loads((ROOT / 'ficha-v01/tecnica-do-livro.json').read_text(encoding='utf8'))
    formas_texto = {f['nome']: f['o_que_e'] for f in tec['formas']}
    formas = []
    for f in r['formas']:
        n = f['nome']
        g = dict(tipo='Forma', nome=n, base='', familia=f['familia'] or '', peso=f['peso'],
                 resolucao=f['resolve'], resultado=f['tipo'], exige_tr=bool(f['tr']),
                 classe_0=bool(f['na_zero']), restricao_embutida='Corpo a Corpo' if f['embutida'] else '',
                 requisitos='', efeito=formas_texto[n], mestre_viu=False, identidade=n,
                 alvos=f['alvos'], partes=[], origem='livro')
        for p in fa.ALCANCE[n]:
            if p is None:
                continue
            antes, escada, grau, depois = p
            dimensao = 'area' if escada in ('raio', 'comprimento', 'linha') else 'alcance'
            # Componentes fixos (Toque/Efeito) também são alcance explícito.
            g[dimensao + '_escada'] = escada or 'Fixo'
            g['partes'].append(dict(dimensao=dimensao, antes=antes if escada else '',
                                    depois=depois if escada else '', grau=fa.GRAU[grau],
                                    fixo=None if escada else antes + depois))
        for dimensao in ('alcance', 'area'):
            g.setdefault(dimensao + '_escada', 'Fixo')
            for contexto, faixas in FAIXAS.items():
                linhas = r['alcance'] if contexto == 'personagem' else entidade['alcance']
                originais = [x for x in linhas if x[0].startswith(n + ' · ')]
                for k, faixa in enumerate(faixas):
                    parte = next((j for j, p in enumerate(g['partes']) if p['dimensao'] == dimensao), None)
                    valor = ''
                    if parte is not None:
                        p = g['partes'][parte]
                        if p['fixo'] is not None:
                            valor = p['fixo'].replace('em você', 'nela') if contexto == 'entidade' else p['fixo']
                        else:
                            texto = originais[k][1 + parte * fa.GRAUS_NA_TABELA]
                            m = re.search(r'\d+(?:,\d+)? × \d+(?:,\d+)? m' if g[dimensao+'_escada']=='linha' else r'\d+(?:,\d+)? m', texto)
                            valor = m.group() if m else '—'
                    g[f'{dimensao}_{contexto}_{faixa}'] = valor
        formas.append(g)

    # Nome -> (nível, Refino/Lapidação, predecessoras). As exceções de criação
    # são dados do contexto; não são inferidas do texto digitado pelo jogador.
    req = {
        'Energia Reversa': (14, 7, ()), 'Circulação': (1, 8, ('Energia Reversa',)),
        'Regravação': (1, 1, ('Circulação',)), 'Kokusen Melhorado': (14, 5, ()),
        'Kokusen Constante': (1, 5, ()), 'Domínio Simples': (1, 5, ()),
        'Pétala': (10, 4, ()), 'Extensão de Domínio': (18, 7, ()),
        'Cortina': (1, 1, ('Barreira Simples',)), 'Ritual': (10, 1, ()),
    }
    atributos = {'Ímpeto': ('Destreza', 4), 'Casco': ('Constituição', 4),
                 'Presilha': ('Força', 4), 'Antecipar': ('Inteligência', 4),
                 'Sangue Frio': ('Constituição', 4), 'Assombro': ('Essência', 4),
                 'Ritual': ('Inteligência', 5)}
    aptidoes = []
    for a in r['aptidoes']:
        n = a['nome']
        nivel, refino, anteriores = req.get(n, (1, 1, ()))
        aptidoes.append(dict(tipo='Bênção' if a['bencao'] else 'Aptidão', nome=n, base='',
            ce=a['cp'], nivel_minimo=nivel, refino_minimo=refino,
            escolha='Gratuita' if a['gratis'] else 'Consome uma escolha',
            requisitos=a['requisito'], efeito=a['faz'], mestre_viu=False,
            identidade=n, predecessoras=anteriores, atributo=atributos.get(n),
            extensao=bool(a['extensao']), escala=fa._ini(a['escala']), resumo=a['resumo'], origem='livro',
            automatica=bool(a['gratis'])))
    talentos = [dict(tipo='Talento', nome=p['nome'], base='', ce=p['cp'],
        rota='Todas' if p['fund'] and p['marc'] else 'Fundamento / Manejos' if p['fund'] else 'Técnica Marcial',
        requisitos='', efeito=p['faz'], resumo=p['resumo'], mestre_viu=False, identidade=p['nome'], origem='livro')
        for p in r['passivas']]
    restricoes = {x['rotulo']: dict(x) for x in r['restricoes']}
    return deepcopy(dict(forma=formas, aptidao=aptidoes, talento=talentos,
        familias=r['familias'], restricoes=restricoes, escadas=tec['escadas'],
        nivel_ce=r['cp'], entidades=entidade['formas'],
        alcances={'personagem':r['alcance'],'entidade':entidade['alcance']}))
