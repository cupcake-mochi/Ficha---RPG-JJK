"""Prepara 16 regressões de montagem para abas novas de uma cópia descartável.

Só escreve JSON local; não aplica pedidos remotos nem importa Office.
As expectativas são as do conjunto versionado, não um oráculo integral da R66.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gerar_nativo as g
from formulas import X

IDS = [0, 5, 10, 11, 23, 24, 28, 29, 32, 34, 35, 43, 49, 53, 59, 60]


def gerar(restantes=False):
    originais, antigo_id, antigo_nome = g.CASOS, g.CAT_ID, g.CAT_ABA
    selecionados = [i for i in range(len(originais)) if i not in IDS] if restantes else IDS
    casos = [originais[i] for i in selecionados]
    sid = 53019003 if restantes else 53019001
    nomes = ['QA catalogo restante', 'QA montagem restante'] if restantes else ['QA catalogo ampliado', 'QA montagem ampliada']
    try:
        g.CASOS = casos
        g.CAT_ID, g.CAT_ABA = sid, nomes[0]
        pedidos = g.gerar()
    finally:
        g.CASOS, g.CAT_ID, g.CAT_ABA = originais, antigo_id, antigo_nome
    pedidos[1]['updateCells']['start']['sheetId'] = sid + 1
    necessarios = set()

    def visitar(node):
        if not isinstance(node, X):
            return
        if node.op == 'ref' and node.args[0] in g.ARVORE:
            chave = node.args[0]
            if chave not in necessarios:
                necessarios.add(chave)
                visitar(g.ARVORE[chave])
        for arg in node.args:
            visitar(arg)

    for caso in casos:
        for chave in set(caso['esperado']) | set(caso.get('contem', {})) | set(caso.get('nao_contem', {})):
            if chave in g.ARVORE:
                necessarios.add(chave)
                visitar(g.ARVORE[chave])
    colunas = g.INPUTS + list(g.ARVORE)
    for row in pedidos[1]['updateCells']['rows'][1:]:
        for i, chave in enumerate(colunas):
            if chave in g.ARVORE and chave not in necessarios:
                row['values'][i] = {}
    adds = []
    for i, pedido in enumerate(pedidos):
        dados = pedido['updateCells']
        rows = dados['rows']
        adds.append({'addSheet': {'properties': {
            'sheetId': dados['start']['sheetId'],
            'title': nomes[i],
            'gridProperties': {'rowCount': len(rows) + 2,
                               'columnCount': max(len(r['values']) for r in rows)}}}})
    for row in pedidos[0]['updateCells']['rows']:
        while row['values'] and row['values'][-1].get('userEnteredValue', {}).get('stringValue') == '':
            row['values'].pop()
    return adds + pedidos


if __name__ == '__main__':
    restantes = '--restantes' in sys.argv
    Path(sys.argv[1]).write_text(json.dumps(gerar(restantes), ensure_ascii=False, separators=(',', ':')))
    print('73 cenários restantes' if restantes else '16 cenários; ler QA montagem ampliada!FZ2:GB17 depois de aplicar em cópia.')
