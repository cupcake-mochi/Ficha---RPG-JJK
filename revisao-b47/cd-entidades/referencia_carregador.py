# -*- coding: utf-8 -*-
"""Referência Python do carregador: as abas como o script deveria usá-las.

emitir_gs.abas_do_script junta abas separadas e complementos e só depois expande as `copias`.
Saída: {aba: [vals serializados]} para a sonda_carregador_copias.js comparar com o carregador JS.

    python referencia_carregador.py <raiz do checkout/worktree> <pasta dos .gs> <saida.json>
"""
import json
import sys

raiz, gsdir, saida = sys.argv[1:4]
sys.path[:0] = [raiz + '/ficha', raiz + '/ficha-v01']
import emitir_gs as e


def normal(v):
    # o JS escreve 0 onde o Python escreve 0.0; o resto da tripla vai igual
    return json.dumps([int(x) if isinstance(x, float) and x.is_integer() else x for x in v],
                      ensure_ascii=False, separators=(',', ':'))


abas = e.abas_do_script(gsdir + '/Ficha.gs')
with open(saida, 'w', encoding='utf-8') as f:
    json.dump({a['nome']: sorted(normal(v) for v in a['vals']) for a in abas}, f, ensure_ascii=False)
