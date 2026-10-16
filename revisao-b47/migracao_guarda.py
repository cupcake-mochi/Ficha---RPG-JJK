# -*- coding: utf-8 -*-
"""Guarda e plano de migração dos catálogos custom para a capacidade reduzida (proposta do revisor).

Não acessa o Google nem altera arquivos. Recebe um snapshot da ANALISE (chave -> valor), que já
exporta o cadastro cru dos 1.633 registros, inclusive inválidos, e devolve:
- quais registros têm dado (comparando com o molde vazio derivado do gerador, não com 'célula vazia');
- o mapeamento registro antigo -> registro novo, por catálogo de destino;
- bloqueios: perda de dado, tipo ambíguo, referência a cadastro que sumiria.

Regras (recomendação, a confirmar pelo integrador):
- Sem --compactar, o número do registro é mantido; registro com dado acima da capacidade bloqueia.
- Com --compactar, os registros com dado são renumerados em ordem; a troca de número é listada
  (o bot identifica por impressão digital, mas a chave custom.<tipo>.N muda de dono).
- Perícia/Ofício: o catálogo antigo mistura tipos; com destino separado, o mapeamento é sempre explícito.
- Nada é fundido nem descartado em silêncio: nomes repetidos são preservados crus e avisados.

    python revisao-b47/migracao_guarda.py snapshot.json --perfil alvo-real-separado [--compactar]

snapshot.json: {"custom.melhoria.1.nome": "...", ...} ou a saída de ler_link()/ler_xlsx() do ler-analise.py.
"""
import json
import re
import sys
from collections import defaultdict

RE_REG = re.compile(r'^custom\.(familia|melhoria|restricao|treino)\.(\d+)\.(\w+)$')
VAZIOS_COMUNS = {'', None}
# Fallback documentado; o teste confere que é igual ao molde do gerador.
PADROES = {('familia', 'estado'): 'Neutra', ('melhoria', 'base'): 'Nenhuma', ('restricao', 'base'): 'Nenhuma'}
REFERENCIAS = [
    ('melhoria', re.compile(r'\.pecas$'), True),
    ('restricao', re.compile(r'\.restricoes$'), True),
    ('familia', re.compile(r'^invocacao\.\d+\.familia\.\d+$'), False),
    ('treino', re.compile(r'^(personagem\.(pericia|oficio)_custom\.\d+\.nome|invocacao\.\d+\.pericia\.\d+)$'), False),
]


def valor(v):
    if isinstance(v, dict):
        v = v.get('valor')
    if v is None:
        return ''
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


def vazio(cat, campo, v, padroes):
    if v in VAZIOS_COMUNS:
        return True
    if campo == 'mestre_viu':
        return v in ('0', 'FALSO', 'FALSE')
    return v == padroes.get((cat, campo))


def chave_nome(n):
    """Sheets compara nomes sem diferenciar maiúsculas (COUNTIF, =)."""
    return n.strip().casefold()


def registros(snapshot, padroes):
    regs = defaultdict(dict)
    for k, v in snapshot.items():
        m = RE_REG.match(k)
        if m:
            regs[(m[1], int(m[2]))][m[3]] = valor(v)
    com_dado = {}
    for (cat, n), campos in regs.items():
        if any(not vazio(cat, c, v, padroes) for c, v in campos.items()):
            com_dado[(cat, n)] = campos
    return regs, com_dado


def destino_de(cat, campos, catalogos):
    if cat != 'treino' or 'treino' in catalogos:
        return cat
    tipo = campos.get('tipo', '')
    return {'Perícia': 'pericia', 'Ofício': 'oficio'}.get(tipo)


def planejar(snapshot, catalogos, padroes=None, compactar=False):
    """catalogos: {destino: {'capacidade': int}}. Devolve dict com mapa, bloqueios e avisos."""
    padroes = {**PADROES, **(padroes or {})}
    todos, com_dado = registros(snapshot, padroes)
    plano = dict(mapa=[], bloqueios=[], avisos=[], resumo={})
    por_destino = defaultdict(list)
    for (cat, n), campos in sorted(com_dado.items(), key=lambda x: (x[0][0], x[0][1])):
        dst = destino_de(cat, campos, catalogos)
        if dst is None:
            plano['bloqueios'].append(f'{cat}.{n}: TIPO ausente ou inválido ({campos.get("tipo")!r}) com outros campos '
                                      'preenchidos; decidir Perícia ou Ofício antes de migrar')
            continue
        if dst not in catalogos:
            plano['bloqueios'].append(f'{cat}.{n}: sem catálogo de destino {dst!r} no perfil')
            continue
        por_destino[dst].append((cat, n, campos))
    separado = 'treino' not in catalogos
    for dst, itens in por_destino.items():
        cap = catalogos[dst]['capacidade']
        renumera = compactar or (separado and dst in ('pericia', 'oficio'))
        livres = iter(range(1, cap + 1))
        for i, (cat, n, campos) in enumerate(itens):
            novo = next(livres, None) if renumera else n
            if novo is None or novo > cap:
                plano['bloqueios'].append(f'{cat}.{n} ({campos.get("nome", "")!r}) não cabe em {dst} (capacidade {cap}); '
                                          'nenhum registro com dado pode ser cortado')
                continue
            plano['mapa'].append(dict(origem=f'custom.{cat}.{n}', destino=f'custom.{dst}.{novo}',
                                      renumerado=(cat != dst or n != novo), campos=campos))
        plano['resumo'][dst] = dict(capacidade=cap, com_dado=len(itens))
    # Nomes: repetidos, separador de lista e mesmo nome nos dois tipos (o catálogo antigo os comparava juntos)
    nomes = defaultdict(list)
    for item in plano['mapa']:
        nome = item['campos'].get('nome', '')
        if nome:
            nomes[(item['destino'].split('.')[1], chave_nome(nome))].append(item['origem'])
            if ' · ' in nome:
                plano['avisos'].append(f'{item["origem"]}: nome contém " · ", separador das listas da ANALISE')
    for (dst, nome), origens in nomes.items():
        if len(origens) > 1:
            plano['avisos'].append(f'{dst}: nome repetido {nome!r} em {origens}; já inválido, preservar ambos crus')
    if separado:
        p = {n for (d, n) in nomes if d == 'pericia'}
        o = {n for (d, n) in nomes if d == 'oficio'}
        for n in sorted(p & o):
            plano['avisos'].append(f'nome {n!r} existe como Perícia e Ofício: era inválido no catálogo único; '
                                   'decidir se continua inválido após separar')
    # Referências por nome nas posições de uso (reutilização): todo cadastro citado tem de continuar existindo
    mantidos = {(item['origem'].split('.')[1], chave_nome(item['campos'].get('nome', ''))) for item in plano['mapa']}
    por_nome = {(cat, chave_nome(c.get('nome', ''))): f'custom.{cat}.{n}' for (cat, n), c in todos.items() if c.get('nome')}
    usos = defaultdict(int)
    for k, v in snapshot.items():
        for cat, padrao, lista in REFERENCIAS:
            if padrao.search(k):
                for nome in (valor(v).split(' · ') if lista else [valor(v)]):
                    if nome and (cat, chave_nome(nome)) in por_nome:
                        usos[(cat, chave_nome(nome))] += 1
                        if (cat, chave_nome(nome)) not in mantidos:
                            plano['bloqueios'].append(f'{k} usa {nome!r} ({por_nome[(cat, chave_nome(nome))]}), '
                                                      'que não sobreviveria à migração')
    plano['reutilizados'] = {f'{c}:{n}': q for (c, n), q in usos.items() if q > 1}
    plano['ok'] = not plano['bloqueios']
    return plano


if __name__ == '__main__':
    import argparse
    sys.path.insert(0, __file__.rsplit('/', 1)[0])
    import comum
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('snapshot')
    ap.add_argument('--perfil', default='alvo-real-separado')
    ap.add_argument('--compactar', action='store_true')
    a = ap.parse_args()
    snap = json.load(open(a.snapshot, encoding='utf-8'))
    plano = planejar(snap, comum.perfil(a.perfil)['catalogos'], compactar=a.compactar)
    print(json.dumps(plano, ensure_ascii=False, indent=1))
    sys.exit(0 if plano['ok'] else 2)
