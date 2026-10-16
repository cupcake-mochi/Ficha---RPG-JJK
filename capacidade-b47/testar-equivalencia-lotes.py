#!/usr/bin/env python3
"""Compara o estado final de dois pacotes REST, sem enviar nada ao Google."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import unittest
from openpyxl.utils.cell import coordinate_to_tuple


def pedidos(directory):
    result=[]
    for file in sorted(directory.glob('[0-9]*.json')): result.extend(json.loads(file.read_text())['requests'])
    return result


def estado(cells, requests):
    state=deepcopy(cells)
    for q in requests:
        if 'updateCells' in q:
            u=q['updateCells'];start=u['start'];sid=start['sheetId'];fields=u['fields'].split(',')
            for y,row in enumerate(u.get('rows',[]),start['rowIndex']):
                for x,cell in enumerate(row.get('values',[]),start['columnIndex']):
                    dest=state.setdefault(sid,{}).setdefault((y,x),{})
                    for field in ('userEnteredValue','note'):
                        if field in fields:
                            if cell.get(field) not in (None,{},''):dest[field]=deepcopy(cell[field])
                            else:dest.pop(field,None)
        elif 'repeatCell' in q:
            u=q['repeatCell'];rg=u['range'];sid=rg['sheetId'];fields=u['fields'].split(',')
            if not set(fields)&{'userEnteredValue','note'}:continue
            for (y,x),dest in state.get(sid,{}).items():
                if rg.get('startRowIndex',0)<=y<rg.get('endRowIndex',float('inf')) and rg.get('startColumnIndex',0)<=x<rg.get('endColumnIndex',float('inf')):
                    for field in ('userEnteredValue','note'):
                        if field in fields:
                            value=u.get('cell',{}).get(field)
                            if value not in (None,{},''):dest[field]=deepcopy(value)
                            else:dest.pop(field,None)
        elif 'deleteDimension' in q:
            rg=q['deleteDimension']['range'];sid=rg['sheetId'];start,end=rg['startIndex'],rg['endIndex'];new={}
            for (y,x),cell in state.get(sid,{}).items():
                index=y if rg['dimension']=='ROWS' else x
                if start<=index<end:continue
                if index>=end:
                    if rg['dimension']=='ROWS':y-=end-start
                    else:x-=end-start
                new[y,x]=cell
            state[sid]=new
    return {sid:{coord:cell for coord,cell in entries.items() if cell} for sid,entries in state.items()}


def outros(requests):
    return [q for q in requests if 'updateCells' not in q or q['updateCells']['fields']!='userEnteredValue']


class EquivalenciaTest(unittest.TestCase):
    def test_limpeza_excluida_e_estado_final(self):
        cell=lambda y,v:{'updateCells':{'start':{'sheetId':7,'rowIndex':y,'columnIndex':0},'rows':[{'values':[{'userEnteredValue':v}]}],'fields':'userEnteredValue'}}
        cut={'deleteDimension':{'range':{'sheetId':7,'dimension':'ROWS','startIndex':1,'endIndex':2}}}
        initial={7:{(0,0):{'userEnteredValue':{'stringValue':'Antigo'}},(1,0):{'userEnteredValue':{'stringValue':'Retirado'},'note':'Nota'}}}
        original=[cell(0,{'stringValue':'Novo'}),cell(1,{}),cut];optimized=[original[0],cut]
        self.assertEqual(estado(initial,original),estado(initial,optimized))
        self.assertEqual(outros(original),outros(optimized))
        self.assertNotEqual(estado(initial,original),estado(initial,[cut]))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot',type=Path);ap.add_argument('--antes',type=Path);ap.add_argument('--depois',type=Path)
    args=ap.parse_args()
    if not args.snapshot:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EquivalenciaTest))
        raise SystemExit(not result.wasSuccessful())
    if not args.antes or not args.depois:ap.error('--antes e --depois são obrigatórios')
    snapshot=json.loads(args.snapshot.read_text());ids={s['properties']['title']:s['properties']['sheetId'] for s in snapshot['metadata']['sheets']}
    initial={ids[name]:{tuple(v-1 for v in coordinate_to_tuple(coord)):cell for coord,cell in cells.items()} for name,cells in snapshot['cells'].items()}
    old,new=pedidos(args.antes),pedidos(args.depois)
    assert outros(old)==outros(new),'Alteração em formatação, menus, grupos ou estrutura'
    assert estado(initial,old)==estado(initial,new),'Estado final de valores/notas divergente'
    print(json.dumps({'resultado':'OK','pedidos_antes':len(old),'pedidos_depois':len(new),'valores_notas_e_demais_operacoes_iguais':True}))


if __name__=='__main__':main()
