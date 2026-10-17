"""Confere leituras integrais antes/depois contra os pedidos efetivamente enviados."""
import argparse
from copy import deepcopy
import json
from decimal import Decimal
from pathlib import Path
from openpyxl.utils.cell import get_column_letter as L
import lotes_cd as l
from migracao import equivalent,sha,canonical
from openpyxl.formula import Tokenizer


def equivalente_nativo(a,b):
    if equivalent(a,b):return True
    if not all(isinstance(x,str) and x.startswith('=') for x in (a,b)):return False
    def normalized(v):
        tokens=Tokenizer(canonical(v)).items
        return [(t.type,t.subtype,str(Decimal(t.value).normalize()) if t.type=='OPERAND' and t.subtype=='NUMBER' else t.value) for t in tokens]
    return normalized(a)==normalized(b)


def ler(folder):
    out={};errors=[]
    for p in sorted(folder.glob('[0-9]*.json')):
        r=json.loads(p.read_text(encoding='utf8'))['response']
        for s in r['sheets']:
            cells=out.setdefault(s['properties']['title'],{})
            for d in s['data']:
                for y,row in enumerate(d.get('rowData',[])):
                    for x,cell in enumerate(row.get('values',[])):
                        co=L(d.get('startColumn',0)+x+1)+str(d.get('startRow',0)+y+1)
                        if cell:cells[co]=cell
                        if cell.get('effectiveValue',{}).get('errorValue'):errors.append([s['properties']['title'],co,cell['effectiveValue']['errorValue']])
    return out,errors


def conferir(before,after,requests,metadata,target):
    old,_=ler(before);native,errors=ler(after);expected=deepcopy(old)
    ids={s['properties']['sheetId']:s['properties']['title'] for s in metadata['sheets']}
    changed=set();rules=set()
    for req in requests:
        if 'addSheet'in req:
            p=req['addSheet']['properties'];ids[p['sheetId']]=p['title'];expected[p['title']]={}
        if 'updateCells'in req:
            u=req['updateCells'];s=ids[u['start']['sheetId']];fields=u['fields'].split(',')
            for y,row in enumerate(u['rows']):
                for x,cell in enumerate(row['values']):
                    co=L(u['start']['columnIndex']+x+1)+str(u['start']['rowIndex']+y+1)
                    out=expected.setdefault(s,{}).setdefault(co,{})
                    for f in fields:
                        if f in ('userEnteredValue','note','dataValidation'):
                            out[f]=cell.get(f,{}) if f!='note' else cell.get(f,'')
                    changed.add((s,co))
        if 'setDataValidation'in req:
            u=req['setDataValidation'];g=u['range'];s=ids[g['sheetId']]
            for y in range(g['startRowIndex'],g['endRowIndex']):
                for x in range(g['startColumnIndex'],g['endColumnIndex']):
                    co=L(x+1)+str(y+1);expected.setdefault(s,{}).setdefault(co,{})['dataValidation']=u.get('rule')
                    rules.add((s,co))
    differences=[];notes=0;unchanged=0
    for s in expected.keys()|native.keys():
        for co in expected.get(s,{}).keys()|native.get(s,{}).keys():
            a=expected.get(s,{}).get(co,{});b=native.get(s,{}).get(co,{})
            av=next(iter(a.get('userEnteredValue',{}).values()),None);bv=next(iter(b.get('userEnteredValue',{}).values()),None)
            if not equivalente_nativo(av,bv):differences.append({'aba':s,'celula':co,'campo':'userEnteredValue','esperado':av,'recebido':bv})
            if (a.get('note') or '')!=(b.get('note') or ''):differences.append({'aba':s,'celula':co,'campo':'note'})
            if l.canon_rule(a.get('dataValidation'))!=l.canon_rule(b.get('dataValidation')):differences.append({'aba':s,'celula':co,'campo':'dataValidation','esperado':a.get('dataValidation'),'recebido':b.get('dataValidation')})
            if old.get(s,{}).get(co,{}).get('note'):notes+=1
            if (s,co) not in changed and old.get(s,{}).get(co,{}).get('userEnteredValue'):unchanged+=1
    val=lambda s,c:next(iter(native.get(s,{}).get(c,{}).get('effectiveValue',{}).values()),'')
    rows=[[val('ANALISE',c+str(r)) for c in 'ABCD'] for r in range(2,8192)]
    keys=[r[0] for r in rows]
    canonical=next(a for a in target['layout']['abas'] if a['nome']=='ANALISE')
    raw={c[0]:c[1] for c in canonical['celulas']}
    contract=[]
    for r,row in enumerate(rows,2):
        for i,c in [(0,'A'),(2,'C'),(3,'D')]:
            wanted=raw.get(c+str(r),'')
            if isinstance(wanted,str) and wanted.startswith('="') and wanted.endswith('"'):wanted=wanted[2:-1].replace('""','"')
            if row[i]!=wanted:contract.append([r,c])
    return dict(resultado='OK' if not(errors or differences or contract) and len(set(keys))==8190 and str(val('ANALISE','B2'))=='11' else 'FALHA',
        erros_formula=errors,diferencas=differences,contrato_diferencas=contract,chaves=len(keys),chaves_unicas=len(set(keys)),
        versao=val('ANALISE','B2'),notas_antigas_conferidas=notes,celulas_antigas_sem_escrita_conferidas=unchanged,
        celulas_alteradas=len(changed),validacoes_alteradas=len(rules),analise_sha256=sha(rows)),rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('antes','depois','lotes','metadata','alvo','saida'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();read=lambda f:json.loads(f.read_text(encoding='utf8'))
    requests=[r for f in sorted(a.lotes.glob('[0-9]*.json')) for r in read(f)['requests']]
    report,rows=conferir(a.antes,a.depois,requests,read(a.metadata),read(a.alvo))
    a.saida.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    a.saida.with_name(a.saida.stem+'-analise.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()},ensure_ascii=False))
    raise SystemExit(report['resultado']!='OK')
