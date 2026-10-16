#!/usr/bin/env python3
"""Continua plano existente omitindo só formatos redundantes de mesclas.

Não envia nada e não autoriza reaplicar o prefixo. A equivalência deve ser
validada nativamente antes do uso: updateCells na âncora já formata a mescla.
"""
import argparse
import json
from pathlib import Path
from migracao import OFICIAL, sha


def otimizar(origem, saida, inicio):
    if saida.exists() or inicio < 1:
        raise ValueError('Saída existente ou continuação inválida')
    m=json.loads((origem/'manifesto.json').read_text(encoding='utf8'))
    if m['destino']==OFICIAL or inicio>=len(m['lotes']):
        raise ValueError('Destino/índice inválido')
    files=[];previous=None;merged=set();cfg=None;removed=[];before=0
    def box(r):
        return tuple(r.get(k) for k in ('sheetId','startRowIndex','endRowIndex','startColumnIndex','endColumnIndex'))
    for i,entry in enumerate(m['lotes']):
        name=entry['arquivo']
        if Path(name).name!=name:raise ValueError('Caminho inválido')
        p=json.loads((origem/name).read_text(encoding='utf8'))
        if sha(p)!=entry['sha256'] or p['spreadsheet_id']!=m['destino'] or len(p['requests'])!=entry['pedidos']:
            raise ValueError('Lote alterado: '+name)
        kept=[]
        for n,q in enumerate(p['requests']):
            if 'unmergeCells' in q:
                r=q['unmergeCells']['range']
                if r.get('startRowIndex')==732:cfg=r['sheetId']
            if 'mergeCells' in q:merged.add(box(q['mergeCells']['range']))
            r=q.get('repeatCell');u=(previous or {}).get('updateCells',{})
            vals=u.get('rows',[{}])[0].get('values',[]) if len(u.get('rows',[]))==1 else []
            anchor=vals[0] if len(vals)==1 else {}
            start=u.get('start',{});rg=(r or {}).get('range',{})
            redundant=bool(r and cfg is not None and rg.get('sheetId')==cfg
                and rg.get('startRowIndex',-1)>=732 and box(rg) in merged
                and r['fields']=='userEnteredFormat' and set(r['cell'])=={'userEnteredFormat'}
                and 'userEnteredFormat' in u.get('fields','').split(',')
                and start.get('sheetId')==cfg and start.get('rowIndex')==rg['startRowIndex']
                and start.get('columnIndex')==rg['startColumnIndex']
                and anchor.get('userEnteredFormat')==r['cell']['userEnteredFormat'])
            if redundant:
                if i>=inicio:removed.append({'lote':i,'pedido':n,'mescla':list(box(rg))})
            else:kept.append(q)
            previous=q
        if i>=inicio:
            before+=len(p['requests'])
            files.append((i,{'spreadsheet_id':p['spreadsheet_id'],'requests':kept},entry))
    saida.mkdir(parents=True)
    entries=[]
    for i,p,old in files:
        name=f'{i:04d}.json'
        (saida/name).write_text(json.dumps(p,ensure_ascii=False,separators=(',',':')),encoding='utf8')
        entries.append({'arquivo':name,'indice_origem':i,'sha256':sha(p),'pedidos':len(p['requests']),'origem_sha256':old['sha256']})
    result={**m,'lotes':entries,'pedidos':sum(e['pedidos'] for e in entries),'continuacao':{
        'a_partir':inicio,'prefixo_nao_reaplicar':True,'origem_manifesto_sha256':sha(m),
        'pedidos_antes':before,'formatos_redundantes_omitidos':len(removed),
        'demais_pedidos_e_ordem_preservados':True,'prova_exigida':'Equivalência nativa em mesclas simples e multilinha + prefixo confirmado.'}}
    (saida/'manifesto.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    (saida/'formatos-coalescidos.json').write_text(json.dumps(removed,ensure_ascii=False),encoding='utf8')
    return {'lotes_pendentes':len(entries),'pedidos':result['pedidos'],'formatos_omitidos':len(removed)}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--origem',type=Path,required=True)
    ap.add_argument('--saida',type=Path,required=True)
    ap.add_argument('--a-partir',type=int,required=True)
    a=ap.parse_args();print(json.dumps(otimizar(a.origem,a.saida,a.a_partir)))
