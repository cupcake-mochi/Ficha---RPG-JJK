# -*- coding: utf-8 -*-
"""Casos da guarda de migração (migracao_guarda.py) sobre o molde real do SHA em teste.

O snapshot de partida é a ANALISE com os valores que o gerador põe nos cartões vazios;
cada caso altera só o necessário. Sem Google.

    python revisao-b47/test_migracao.py
"""
import json
import re

import comum
import migracao_guarda as g

ap = comum.argumentos(__doc__)
args = ap.parse_args()
modelo = json.loads(comum.exportar('base-v9', 'pecas').read_text(encoding='utf-8'))
cfg = {c: v for c, v, *_ in next(a for a in modelo['layout']['abas'] if a['nome'] == 'CONFIGURAÇÃO')['celulas']}
an = comum._linhas_da_aba(next(a for a in modelo['layout']['abas'] if a['nome'] == 'ANALISE'))
P = comum.Placar('migracao')

# Molde: o que um cartão nunca tocado exporta (False -> "0", None -> "")
molde = {}
for k, v, c, parte in an:
    if g.RE_REG.match(k or ''):
        celula = re.sub(r'^="|"$', '', str(c)).split('!')[-1]
        molde[k] = g.valor(cfg.get(celula))
padroes_do_gerador = {}
for k, v in molde.items():
    m = g.RE_REG.match(k)
    if v not in ('', '0'):
        padroes_do_gerador.setdefault((m[1], m[3]), set()).add(v)
P.check('padrões do molde coincidem com os da guarda',
        {k: next(iter(v)) for k, v in padroes_do_gerador.items()} == g.PADROES and
        all(len(v) == 1 for v in padroes_do_gerador.values()), padroes_do_gerador)

SEP = comum.perfil('alvo-real-separado')['catalogos']
UNI = comum.perfil('alvo-real-treino-unico')['catalogos']


def snap(**mudancas):
    s = dict(molde)
    for k, v in mudancas.items():
        s[k.replace('__', '.')] = v
    return s


def caso(nome, s, cat=SEP, compactar=False):
    return g.planejar(s, cat, compactar=compactar)


p = caso('molde', snap())
P.check('molde intacto: nenhum registro com dado, nada bloqueado', p['ok'] and not p['mapa'], p['bloqueios'][:2])
P.check('estado apagado sem outros campos não conta como dado',
        not caso('', snap(**{'custom.familia.3.estado': ''}))['mapa'])

p = caso('parcial', snap(**{'custom.melhoria.7.efeito': 'Texto sem nome'}))
P.check('registro só com EFEITO (sem nome) é preservado', [m['origem'] for m in p['mapa']] == ['custom.melhoria.7'])
p = caso('mestre', snap(**{'custom.restricao.2.mestre_viu': '1'}))
P.check('MESTRE VIU marcado sozinho conta como dado', [m['origem'] for m in p['mapa']] == ['custom.restricao.2'])

p = caso('ultima', snap(**{'custom.melhoria.30.nome': 'Última'}))
P.check('última vaga (30) mantém o número', p['ok'] and p['mapa'][0]['destino'] == 'custom.melhoria.30'
        and not p['mapa'][0]['renumerado'])
p = caso('primeira', snap(**{'custom.familia.1.nome': 'Primeira'}))
P.check('primeira vaga mantém o número', p['ok'] and p['mapa'][0]['destino'] == 'custom.familia.1')

alem = snap(**{'custom.melhoria.31.nome': 'Excedente', 'custom.melhoria.31.peso': 'Leve'})
p = caso('corte', alem)
P.check('dado acima da capacidade bloqueia (sem compactar)', not p['ok'] and any('melhoria.31' in b for b in p['bloqueios']))
p = caso('compacta', alem, compactar=True)
P.check('com --compactar vai para a primeira vaga livre e marca renumeração',
        p['ok'] and p['mapa'][0]['destino'] == 'custom.melhoria.1' and p['mapa'][0]['renumerado'])
cheio = snap(**{f'custom.melhoria.{n}.nome': f'M{n}' for n in range(1, 32)})
p = caso('cheio', cheio, compactar=True)
P.check('31 Melhorias com dado não cabem nem compactando', not p['ok'] and len(p['mapa']) == 30)

treinos = {}
for i, n in enumerate([1, 9, 40, 77, 100, 110, 120, 125, 130, 131]):
    treinos[f'custom.treino.{n}.tipo'] = 'Perícia'
    treinos[f'custom.treino.{n}.nome'] = f'Pericia {i}'
for i, n in enumerate(range(2, 21, 2)):
    treinos[f'custom.treino.{n}.tipo'] = 'Ofício'
    treinos[f'custom.treino.{n}.nome'] = f'Oficio {i}'
p = caso('treino', snap(**treinos))
dest = {m['origem']: m['destino'] for m in p['mapa']}
P.check('10 Perícias + 10 Ofícios espalhados em 131 vagas cabem no destino separado', p['ok'] and len(dest) == 20,
        p['bloqueios'][:2])
P.check('Perícia 131 vai para custom.pericia.10 explicitamente', dest.get('custom.treino.131') == 'custom.pericia.10')
p = caso('treino+1', snap(**treinos, **{'custom.treino.60.tipo': 'Perícia', 'custom.treino.60.nome': 'Sobra'}))
P.check('11ª Perícia bloqueia', not p['ok'] and any('não cabe em pericia' in b for b in p['bloqueios']))
p = caso('sem tipo', snap(**{'custom.treino.5.nome': 'Sem tipo'}))
P.check('treino com nome e sem TIPO bloqueia (decisão necessária)', not p['ok'] and 'TIPO ausente' in p['bloqueios'][0])
p = caso('unico', snap(**{'custom.treino.21.tipo': 'Ofício', 'custom.treino.21.nome': 'X'}), UNI)
P.check('perfil de catálogo único: registro 21 com dado bloqueia', not p['ok'])

curinga = 'Golpe *Duplo* ~?'
p = caso('curinga', snap(**{'custom.melhoria.3.nome': curinga, 'custom.melhoria.4.nome': 'golpe *duplo* ~?'}))
P.check('nome com * ? ~ chega idêntico ao destino', p['mapa'][0]['campos']['nome'] == curinga)
P.check('nomes iguais sem diferenciar maiúsculas: avisa e preserva os dois', len(p['mapa']) == 2 and
        any('repetido' in a for a in p['avisos']))
p = caso('separador', snap(**{'custom.restricao.1.nome': 'A · B'}))
P.check('nome com o separador " · " é avisado', any('separador' in a for a in p['avisos']))
p = caso('dois tipos', snap(**{'custom.treino.1.tipo': 'Perícia', 'custom.treino.1.nome': 'Ofuscar',
                               'custom.treino.2.tipo': 'Ofício', 'custom.treino.2.nome': 'Ofuscar'}))
P.check('mesmo nome em Perícia e Ofício pede decisão', any('Perícia e Ofício' in a for a in p['avisos']))

uso = {'custom.familia.40.nome': 'Eco', 'custom.familia.40.estado': 'Livre',
       'invocacao.1.familia.6': 'Eco', 'invocacao.5.familia.9': 'Eco', 'invocacao.12.familia.1': 'Eco'}
p = caso('reuso', snap(**uso), compactar=True)
P.check('Família reutilizada em 3 invocações continua existindo após compactar', p['ok'] and
        p['reutilizados'].get('familia:eco') == 3)
p = caso('reuso cortado', snap(**uso))
P.check('Família usada acima da capacidade bloqueia também pelas referências', not p['ok'] and
        sum('invocacao.' in b for b in p['bloqueios']) == 3)
p = caso('lista', snap(**{'custom.melhoria.50.nome': 'Ricochete', 'feitico.3.pecas': 'Alcance Ampliado · Ricochete'}))
P.check('Melhoria citada em lista " · " de feitiço é rastreada', any('feitico.3.pecas' in b for b in p['bloqueios']))
P.fim()
