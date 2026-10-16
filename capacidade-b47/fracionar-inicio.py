#!/usr/bin/env python3
"""Fraciona só o primeiro lote v9→v10 sem mudar um pedido ou sua ordem.

Não envia nada. Exige manifesto e hashes íntegros; conserva backup, snapshot,
prova e guardas do plano. Timeout exige leitura do estado antes de usar isto.
"""
import argparse
import json
from pathlib import Path
from migracao import OFICIAL, sha


def fracionar(origem, saida, limite=50):
    if limite < 1 or saida.exists():
        raise ValueError('Limite inválido ou destino já existe')
    manifest = json.loads((origem/'manifesto.json').read_text(encoding='utf8'))
    payloads = []
    for entry in manifest['lotes']:
        name = entry['arquivo']
        if Path(name).name != name:
            raise ValueError('Caminho de lote inválido')
        p = json.loads((origem/name).read_text(encoding='utf8'))
        if sha(p) != entry['sha256'] or len(p['requests']) != entry['pedidos']:
            raise ValueError('Lote alterado: '+name)
        if p['spreadsheet_id'] != manifest['destino'] or p['spreadsheet_id'] == OFICIAL:
            raise ValueError('Destino inválido')
        payloads.append(p)
    first = payloads[0]['requests']
    split = next(i for i, r in enumerate(first) if 'mergeCells' in r)
    expected = ['updateSheetProperties', 'deleteDimensionGroup', 'unmergeCells',
                'repeatCell', 'updateDimensionProperties', 'repeatCell']
    if [next(iter(r)) for r in first[:split]] != expected:
        raise ValueError('Cabeçalho diferente da migração v9→v10 esperada')
    if any(set(r) != {'mergeCells'} for r in first[split:]):
        raise ValueError('Cauda inicial contém pedidos além de mesclagens')
    chunks = [[r] for r in first[:split]]
    chunks += [first[i:i+limite] for i in range(split, len(first), limite)]
    chunks += [p['requests'] for p in payloads[1:]]
    # Compara a sequência integral, incluindo restauração e exclusão das caudas.
    old = [r for p in payloads for r in p['requests']]
    new = [r for c in chunks for r in c]
    if old != new or len(old) != manifest['pedidos']:
        raise ValueError('Pedidos/ordem divergentes')
    saida.mkdir(parents=True)
    entries = []
    for i, requests in enumerate(chunks):
        p = {'spreadsheet_id': manifest['destino'], 'requests': requests}
        name = f'{i:04d}.json'
        (saida/name).write_text(json.dumps(p,ensure_ascii=False,separators=(',',':')),encoding='utf8')
        entries.append({'arquivo':name,'sha256':sha(p),'pedidos':len(requests)})
    result = {**manifest, 'lotes':entries, 'fracionamento':{
        'origem_manifesto_sha256':sha(manifest),'lote_inicial_sha256':manifest['lotes'][0]['sha256'],
        'cabecalho_isolado':split,'max_mesclagens_por_fracao':limite,
        'pedidos_ordem_identicos':True,'demais_lotes_inalterados':True}}
    (saida/'manifesto.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return {'lotes':len(entries),'pedidos':len(old),'cabecalho_isolado':split}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--origem',type=Path,required=True)
    ap.add_argument('--saida',type=Path,required=True)
    ap.add_argument('--limite',type=int,default=50)
    a = ap.parse_args()
    print(json.dumps(fracionar(a.origem,a.saida,a.limite)))
