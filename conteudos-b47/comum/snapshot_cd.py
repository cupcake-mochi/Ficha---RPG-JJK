"""Snapshot nativo C: conserva valores, notas e validações; sem rede."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from openpyxl.utils.cell import get_column_letter as L
import migracao_cd as m
sys.path.insert(0,str(m.ROOT/'capacidade-b47'))
from snapshot import normalizar,fatiar


def integral(metadata):
    ranges={s['properties']['title']:[f'A1:{L(s["properties"]["gridProperties"]["columnCount"])}{s["properties"]["gridProperties"]["rowCount"]}'] for s in metadata['sheets']}
    return fatiar(metadata,ranges)


def normalizar_cd(metadata,plan,blocks,backup_id,captured_at,backup_created_at):
    result=normalizar(metadata,plan,blocks,backup_id,captured_at)
    result['backup_created_at']=backup_created_at
    for block in blocks.values():
        for sheet in block['response']['sheets']:
            out=result['cells'].setdefault(sheet['properties']['title'],{})
            for d in sheet['data']:
                for y,row in enumerate(d.get('rowData',[])):
                    for x,cell in enumerate(row.get('values',[])):
                        if 'dataValidation' in cell:
                            co=L(d.get('startColumn',0)+x+1)+str(d.get('startRow',0)+y+1)
                            out.setdefault(co,{})['dataValidation']=deepcopy(cell['dataValidation'])
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('metadata','saida'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--partes',type=Path);p.add_argument('--backup-id');p.add_argument('--backup-created-at');p.add_argument('--captured-at')
    a=p.parse_args();meta=json.loads(a.metadata.read_text(encoding='utf8'));plan=integral(meta)
    if a.partes:
        if not all((a.backup_id,a.backup_created_at,a.captured_at)):p.error('Snapshot exige backup e horários explícitos')
        blocks={c['arquivo']:json.loads((a.partes/c['arquivo']).read_text(encoding='utf8')) for c in plan['chunks']}
        result=normalizar_cd(meta,plan,blocks,a.backup_id,a.captured_at,a.backup_created_at)
    else:result=plan
    a.saida.write_text(json.dumps(result,ensure_ascii=False),encoding='utf8')
    print(json.dumps({'blocos':len(plan['chunks']),'destino':meta['spreadsheetId']}))
