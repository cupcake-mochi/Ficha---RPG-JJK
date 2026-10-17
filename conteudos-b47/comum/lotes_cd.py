"""Lotes REST 10→11: somente delta, novas auxiliares e apêndice de C.

Não envia pedidos, não reconstrói fichas, não apaga abas/linhas nem move entradas.
As validações vêm das especificações GS expandidas; os valores vêm do modelo
integral, pois `abaixo` e cópias do GS só são materializados na construção.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from openpyxl.utils.cell import range_boundaries, get_column_letter as L
import migracao_cd as m

sys.path.insert(0,str(m.ROOT/'capacidade-b47'))
from lotes import native_value,format_


def coordenadas(area):
    c,r,cc,rr=range_boundaries(area)
    for y in range(r,rr+1):
        for x in range(c,cc+1):yield L(x)+str(y)


def validacoes(specs):
    out={}
    for s in specs:
        cells=out.setdefault(s['nome'],{})
        for where,source in s.get('dv',[]):
            literal=re.fullmatch(r'"(.*)"',source)
            if literal:
                condition={'type':'ONE_OF_LIST','values':[{'userEnteredValue':x} for x in literal[1].split(',')]}
            else:
                condition={'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+source.replace('$','')}]}
            rule={'condition':condition,'strict':where in s.get('menus_estritos',[]),'showCustomUi':True}
            for area in where.split():
                for co in coordenadas(area):cells[co]=rule
        for col,row,count in s.get('caixas',[]):
            for y in range(row,row+count):cells[L(col)+str(y)]={'condition':{'type':'BOOLEAN'}}
    return out


def canon_rule(rule):
    if not rule:return None
    rule=deepcopy(rule)
    rule['strict']=rule.get('strict',False)
    rule['showCustomUi']=rule.get('showCustomUi',False)
    for x in rule.get('condition',{}).get('values',[]):
        v=x.get('userEnteredValue','')
        if v.startswith('='):
            # Native Apps Script strips $ and optional quotes on ASCII names.
            from migracao import canonical
            v=canonical(v).replace('$','')
            x['userEnteredValue']=re.sub(r'\b([A-Z]+[1-9][0-9]*):\1(?![A-Za-z0-9_])',r'\1',v)
    return rule


def delta_validacoes(before,after):
    a,b=validacoes(before),validacoes(after)
    return {s:{c:b.get(s,{}).get(c) for c in a.get(s,{}).keys()|b.get(s,{}).keys()
               if canon_rule(a.get(s,{}).get(c))!=canon_rule(b.get(s,{}).get(c))}
            for s in a.keys()|b.keys()}


def gerar(base,alvo,snapshot,plan,before_specs,after_specs):
    if any((m.sha(snapshot)!=plan['snapshot_sha256'],m.sha(alvo)!=plan['alvo_sha256'],
            m.sha(base)!=plan['base_sha256'])):raise ValueError('Plano não corresponde aos arquivos')
    if plan['excluir_linhas'] or plan['excluir_abas']:raise ValueError('Exclusão fora do escopo C')
    tabs={a['nome']:a for a in alvo['layout']['abas']}
    props={s['properties']['title']:deepcopy(s['properties']) for s in snapshot['metadata']['sheets']}
    cfg=tabs['CONFIGURAÇÃO'];old_cfg=next(a for a in base['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    first=old_cfg['linhas']+2;last=cfg['linhas']+2
    # The connector cannot expose merges. A sheet ending before the appended
    # area proves no existing merge/group can overlap it; otherwise stop.
    if props['CONFIGURAÇÃO']['gridProperties']['rowCount']>=first:
        raise ValueError('Área nova já existe na grade; requer auditoria de mesclas/grupos')
    requests=[];used={p['sheetId'] for p in props.values()};next_id=47020
    def grid(s,area):
        c,r,cc,rr=range_boundaries(area)
        return dict(sheetId=props[s]['sheetId'],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
    for name in sorted(m.NOVAS):
        while next_id in used:next_id+=1
        t=tabs[name];p=dict(sheetId=next_id,title=name,hidden=True,gridProperties={
            'rowCount':t['linhas']+2,'columnCount':t['colunas'],'hideGridlines':True})
        props[name]=p;used.add(next_id);next_id+=1
        requests.append({'addSheet':{'properties':deepcopy(p)}})
    for name,cells in plan['valores_alterados'].items():
        if name in m.NOVAS:continue
        t=tabs[name];g=props[name]['gridProperties'];grow={}
        if t['linhas']+2>g['rowCount']:grow['rowCount']=t['linhas']+2
        if t['colunas']>g['columnCount']:grow['columnCount']=t['colunas']
        if grow:
            requests.append({'updateSheetProperties':{'properties':{'sheetId':props[name]['sheetId'],'gridProperties':grow},
                'fields':','.join('gridProperties.'+k for k in grow)}})
    # Sparse value runs never clear adjacent old inputs. No note/format fields
    # are included on existing cells outside the guarded blank appendix.
    for name,cells in plan['valores_alterados'].items():
        if name=='CONFIGURAÇÃO':continue
        byrow={}
        for co,v in cells.items():
            c,r,_,_=range_boundaries(co);byrow.setdefault(r,{})[c]=v
        for r,row in sorted(byrow.items()):
            cols=sorted(row);runs=[]
            for c in cols:
                if not runs or c!=runs[-1][-1]+1:runs.append([])
                runs[-1].append(c)
            for run in runs:
                requests.append({'updateCells':{'start':{'sheetId':props[name]['sheetId'],'rowIndex':r-1,'columnIndex':run[0]-1},
                    'rows':[{'values':[{'userEnteredValue':native_value(row[c])} for c in run]}], 'fields':'userEnteredValue'}})
    # Entire appendix was proved blank, including padding and notes. Paint
    # only there; all CONFIGURAÇÃO rows above it remain in place.
    cells={co:(v,style) for co,v,style,*_ in cfg['celulas']}
    values=[]
    for r in range(first,last+1):
        line=[]
        for c in range(1,17):
            co=L(c)+str(r);v,style=cells.get(co,(None,None));cell={'userEnteredValue':native_value(v)}
            if style is not None:cell['userEnteredFormat']=format_(alvo['layout']['estilos'][style])
            if cfg.get('notas',{}).get(co):cell['note']=cfg['notas'][co]
            line.append(cell)
        values.append({'values':line})
    requests.append({'updateCells':{'start':{'sheetId':props['CONFIGURAÇÃO']['sheetId'],'rowIndex':first-1,'columnIndex':0},
        'rows':values,'fields':'userEnteredValue,userEnteredFormat,note'}})
    # Any generated delta preceding the appendix must also be applied, but
    # preserve notes and formatting. The planner already guards old inputs.
    for co,v in plan['valores_alterados'].get('CONFIGURAÇÃO',{}).items():
        c,r,_,_=range_boundaries(co)
        if r>=first:continue
        requests.append({'updateCells':{'start':{'sheetId':props['CONFIGURAÇÃO']['sheetId'],'rowIndex':r-1,'columnIndex':c-1},
            'rows':[{'values':[{'userEnteredValue':native_value(v)}]}],'fields':'userEnteredValue'}})
    for area in cfg['mescladas']:
        if range_boundaries(area)[1]>=first:requests.append({'mergeCells':{'range':grid('CONFIGURAÇÃO',area),'mergeType':'MERGE_ALL'}})
    heights=[]
    for r,h in cfg.get('linhas_alt',[]):
        if r<first:continue
        px=round(h*4/3)
        if heights and heights[-1][1]==r-1 and heights[-1][2]==px:heights[-1][1]=r
        else:heights.append([r-1,r,px])
    for start,end,px in heights:requests.append({'updateDimensionProperties':{'range':{'sheetId':props['CONFIGURAÇÃO']['sheetId'],
        'dimension':'ROWS','startIndex':start,'endIndex':end},'properties':{'pixelSize':px},'fields':'pixelSize'}})
    changed_dv=delta_validacoes(before_specs,after_specs)
    base_dv=validacoes(before_specs)
    for name,changes in changed_dv.items():
        if name not in props:continue
        for co,rule in changes.items():
            if (name not in m.NOVAS and range_boundaries(co)[1]<first) or name not in ('CONFIGURAÇÃO',*m.NOVAS):
                if not m.covered(snapshot,name,co):raise ValueError('Validação sem snapshot: '+name+'!'+co)
                old=base_dv.get(name,{}).get(co)
                native=snapshot['cells'].get(name,{}).get(co,{}).get('dataValidation')
                if canon_rule(native)!=canon_rule(old):raise ValueError('Validação nativa divergente: '+name+'!'+co)
            request={'range':grid(name,co)}
            if rule:request['rule']=rule
            requests.append({'setDataValidation':request})
    # Fixed helper formatting matches the generated hidden data sheets.
    for name in m.NOVAS:
        t=tabs[name]
        requests.append({'repeatCell':{'range':grid(name,f'A1:{L(t["colunas"])}{t["linhas"]+2}'),
            'cell':{'userEnteredFormat':{'backgroundColor':{'red':1,'green':1,'blue':1},'textFormat':{'fontFamily':'Roboto','fontSize':10,'foregroundColor':{'red':0,'green':0,'blue':0}}}},'fields':'userEnteredFormat'}})
    return requests,props


def fracionar(requests,max_bytes=60000,max_requests=40):
    size=lambda x:len(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode())
    def split(req):
        if size(req)<=45000:return [req]
        u=req.get('updateCells')
        if not u:raise ValueError('Pedido grande demais')
        cut=len(u['rows'])//2
        if cut:
            a={**u,'rows':u['rows'][:cut]};b={**u,'rows':u['rows'][cut:],'start':{**u['start'],'rowIndex':u['start']['rowIndex']+cut}}
        else:
            vals=u['rows'][0]['values'];cut=len(vals)//2
            if not cut:raise ValueError('Célula grande demais')
            a={**u,'rows':[{'values':vals[:cut]}]};b={**u,'rows':[{'values':vals[cut:]}],'start':{**u['start'],'columnIndex':u['start']['columnIndex']+cut}}
        return split({'updateCells':a})+split({'updateCells':b})
    parts=[];batch=[]
    for req in requests:
        for item in split(req):
            if batch and (len(batch)>=max_requests or size(batch+[item])>max_bytes):parts.append(batch);batch=[]
            batch.append(item)
    if batch:parts.append(batch)
    return parts


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('base','alvo','snapshot','spec_base','spec_alvo','saida'):p.add_argument('--'+k.replace('_','-'),type=Path,required=True)
    p.add_argument('--prova',type=Path);a=p.parse_args();read=lambda f:json.loads(f.read_text(encoding='utf8'))
    base,target,snapshot=map(read,(a.base,a.alvo,a.snapshot));plan=m.planejar(base,target,snapshot,prova=read(a.prova) if a.prova else None)
    req,props=gerar(base,target,snapshot,plan,read(a.spec_base),read(a.spec_alvo));parts=fracionar(req);a.saida.mkdir(parents=True,exist_ok=False)
    for i,batch in enumerate(parts):(a.saida/f'{i:03d}.json').write_text(json.dumps({'spreadsheet_id':plan['destino'],'requests':batch},ensure_ascii=False),encoding='utf8')
    public={k:v for k,v in plan.items() if k not in ('valores_alterados','notas_preservadas')}
    (a.saida/'manifesto.json').write_text(json.dumps({**public,'props':props,'lotes':len(parts),'pedidos':len(req)},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'lotes':len(parts),'pedidos':len(req),'destino':plan['destino']}))
