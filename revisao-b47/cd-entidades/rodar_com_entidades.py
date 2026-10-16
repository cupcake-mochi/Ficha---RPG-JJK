# -*- coding: utf-8 -*-
"""Roda ficha-v01/monta.py com o módulo de entidades injetado, sem editar o núcleo.

    python rodar_com_entidades.py <raiz> <tr.json> <tipos> <talentos> <argumentos do monta.py...>

O módulo entra logo depois do último módulo custom do monta.py (custom_danos quando existe; senão
custom_pecas), a mesma ordem do patch 01, e suas linhas ANALISE vêm depois das dele, no fim do contrato. O registro
da transformação (endereços dos cartões, capacidades) vai para <tr.json>.

Guarda: sem --exportar-* o gerador grava .gs/XLSX; isso só é aceito fora do checkout de trabalho.
"""
import json
import os
import runpy
import sys

raiz = os.path.abspath(sys.argv[1])
destino_tr, tipos, talentos = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
argumentos = sys.argv[5:]
aqui = os.path.dirname(os.path.abspath(__file__))
checkout = os.path.abspath(os.path.join(aqui, '..', '..'))
if not any(a.startswith('--exportar-') for a in argumentos) and raiz == checkout:
    sys.exit('recusado: geração completa grava .gs/XLSX canônicos; use uma worktree temporária')

sys.path[:0] = [os.path.join(raiz, 'ficha-v01'), os.path.join(raiz, 'ficha'), raiz, aqui]
os.chdir(raiz)
import custom_pecas
import entidades_custom
try:
    import custom_danos as anterior
except ImportError:
    anterior = custom_pecas

estado = {}
pecas_original = custom_pecas.aplica


def pecas(layout, fam, inv, criacao):
    estado['ctx'] = dict(fam=fam, inv=inv, criacao=criacao)
    return pecas_original(layout, fam, inv, criacao)


custom_pecas.aplica = pecas
aplica_original, exporta_original = anterior.aplica, anterior.exporta


def aplica(layout, *args):
    tr = aplica_original(layout, *args)
    ctx = estado['ctx']
    estado['tr'] = entidades_custom.aplica(layout, dict(ctx, capacidades=dict(tipo_entidade=tipos, talento_entidade=talentos)))
    import indice_ficha
    inv = ctx['inv']
    chaves = ('nome', 'tipo', 'talisma', 'tal', 'talx', 'aquis', 'nivel_fixo', 'alma', 'autonomia')
    estado['geo'] = dict(colf=inv['colf'], nivel_ficha=indice_ficha.indice(layout).get('nivel'),
                         fichas=[{k: g[k] for k in chaves if k in g} for g in inv['fichas_c']],
                         abre_tal=inv['R']['abre_tal'], teto_tal=inv['R']['teto_tal'], anterior=anterior.__name__)
    return tr


def exporta(tr):
    return exporta_original(tr) + entidades_custom.exporta(estado['tr'])


anterior.aplica, anterior.exporta = aplica, exporta


def salvar_tr():
    t = estado.get('tr')
    if t:
        with open(destino_tr, 'w', encoding='utf-8') as f:
            json.dump({k: t[k] for k in ('registros', 'catalogos', 'inicio', 'fim', 'capacidades', 'substituicoes',
                                         'consumidores')} | {'geo': estado.get('geo')},
                      f, ensure_ascii=False)


sys.argv = ['monta.py'] + argumentos
try:
    runpy.run_path(os.path.join(raiz, 'ficha-v01', 'monta.py'), run_name='__main__')
finally:
    salvar_tr()
