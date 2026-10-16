#!/usr/bin/env python3
"""Guarda somente as fórmulas existentes que a migração de peças substituirá.

Lê o snapshot nativo feito pelo MCP. Não acessa o Google nem altera a ficha.
"""
import json
from pathlib import Path
import re
from openpyxl.utils.cell import get_column_letter as L

EVID=Path(__file__).resolve().parent.parent.parent/'evidencias-3b'
model=json.loads((EVID/'pecas-modelo.json').read_text())
old=json.loads((EVID/'pecas-modelo-anterior.json').read_text())
native=json.loads((EVID/'pecas-revisao-antes-apoio.json').read_text())
assert native['spreadsheetId']=='1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0'
raw={s['nome']:{c:v for c,v,*_ in s['celulas']} for s in old['layout']['abas']}
actual={s['properties']['title']:{L(d.get('startColumn',0)+ci+1)+str(d.get('startRow',0)+ri+1):v.get('userEnteredValue',{})
    for d in s.get('data',[]) for ri,row in enumerate(d.get('rowData',[])) for ci,v in enumerate(row.get('values',[]))}
    for s in native['sheets']}

def simple_sheet(f):
    return re.sub(r"'([A-Z][A-Z_0-9]*)'!",r'\1!',f)

def source_pt(f):
    quoted=False;out=''
    for i,c in enumerate(f):
        if c=='"':quoted=not quoted
        if not quoted:
            if c==',':c=';'
            elif c=='.' and f[i-1:i].isdigit() and f[i+1:i+2].isdigit():c=','
        out+=c
    return simple_sheet(out)

def uv(v):
    if v is None or v=='':return {}
    if isinstance(v,bool):return {'boolValue':v}
    if isinstance(v,(int,float)):return {'numberValue':v}
    return {'formulaValue':source_pt(v)} if v.startswith('=') else {'stringValue':v}

diffs=[];count=0
for s in ['DADOS_AM','DADOS_INVOC']:
    for c in model['depois'][s]:
        if c not in raw[s]:continue
        expected=uv(raw[s][c]);a=actual[s].get(c,{})
        # O nativo já usa vírgula decimal; não converter seus separadores de novo.
        if 'formulaValue' in a:a={'formulaValue':simple_sheet(a['formulaValue'])}
        count+=1
        if a!=expected:diffs.append(dict(aba=s,celula=c,esperado=expected,atual=a))
result=dict(resultado='OK' if not diffs else 'DIVERGENTE',comparadas=count,diferencas=diffs)
(EVID/'pecas-revisao-guarda.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(dict(resultado=result['resultado'],comparadas=count,diferencas=len(diffs))))
raise SystemExit(bool(diffs))
