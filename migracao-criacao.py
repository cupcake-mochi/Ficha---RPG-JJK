#!/usr/bin/env python3
"""Prepara pedidos delimitados para Sheets; não faz rede nem importa Excel.

Aplicação pelo conector exige pré-leitura, igualdade dos cálculos antigos e
verificação das cópias de formato/mesclagens. Nunca executar construir na revisão.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def cell_coord(c):
    m = re.fullmatch(r'([A-Z]+)(\d+)', c)
    col = 0
    for k in m[1]: col = col*26+ord(k)-64
    return int(m[2])-1, col-1


def formula_native(f):
    # A localidade da revisão é pt_BR. Aspas duplas protegem literais.
    parts = re.split(r'("(?:[^"]|"")*")', f)
    return ''.join(v if i%2 else v.replace(',', ';') for i,v in enumerate(parts))


def value(v):
    if v is None: return {}
    if isinstance(v, bool): return {'boolValue': v}
    if isinstance(v, (int, float)): return {'numberValue': v}
    return {'formulaValue': formula_native(v)} if v.startswith('=') else {'stringValue': v}


def color(h):
    h = h.lstrip('#')[-6:]
    return dict(zip(['red','green','blue'],[int(h[i:i+2],16)/255 for i in [0,2,4]]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--modelo',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); model=json.loads(a.modelo.read_text());a.saida.mkdir(exist_ok=True,parents=True)
    layout=model['layout'];sheets={x['nome']:x for x in layout['abas']}
    raw={n:{v[0]:(v[1],v[2]) for v in x['celulas']} for n,x in sheets.items()}
    cfg=sheets['CONFIGURAÇÃO']; last=model['fim']; first=1800
    ids={n:n for n in ['CONFIGURAÇÃO','DADOS_CRIACAO','DADOS_AM','FICHA AMALDIÇOADA','ANALISE','INVOCAÇÕES']}
    def rect(sheet,r,c,rr,cc):
        return dict(sheetId=ids[sheet],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
    def update(sheet,r,c,rows,fields='userEnteredValue,note'):
        return {'updateCells':dict(start=dict(sheetId=ids[sheet],rowIndex=r-1,columnIndex=c-1),rows=rows,fields=fields)}
    def matrix(sheet,r1,r2,c1,c2,notes=False):
        cells={(cell_coord(c)[0]+1,cell_coord(c)[1]+1):v for c,(v,s) in raw[sheet].items()}
        nt=sheets[sheet].get('notas',{}) if notes else {}
        from openpyxl.utils import get_column_letter as L
        rows=[]
        for r in range(r1,r2+1):
            row=[]
            for c in range(c1,c2+1):
                v=value(cells.get((r,c))); obj={'userEnteredValue':v} if v else {}
                if notes and (t:=nt.get(L(c)+str(r))):obj['note']=t
                row.append(obj)
            rows.append({'values':row})
        return rows
    def fmt(style_id):
        st=layout['estilos'][style_id]
        font,fill,edges,align,num=st
        f={}
        if font:
            f['textFormat']=dict(fontFamily=font[0],fontSize=font[1],foregroundColor=color(font[2]),bold=bool(font[3]),italic=bool(font[4]))
        if fill:f['backgroundColor']=color(fill)
        if align:
            f.update(horizontalAlignment=(align[0] or 'left').upper(),verticalAlignment={'center':'MIDDLE','top':'TOP','bottom':'BOTTOM'}.get(align[1],'MIDDLE'),wrapStrategy='WRAP' if align[2] else 'CLIP')
        return f
    def frames(start,end):
        merges={m.split(':')[0]:m for m in cfg['mescladas'] if start<=cell_coord(m.split(':')[0])[0]+1<=end}
        result=[]
        for addr,(v,st) in raw['CONFIGURAÇÃO'].items():
            r,c=cell_coord(addr);r+=1;c+=1
            if not start<=r<=end:continue
            if st==raw['CONFIGURAÇÃO']['A1'][1]:continue
            er,ec=(cell_coord(merges[addr].split(':')[1]) if addr in merges else (r-1,c-1))
            er+=1;ec+=1;rg=rect('CONFIGURAÇÃO',r,c,er,ec)
            if addr in merges:result.append({'mergeCells':dict(range=rg,mergeType='MERGE_ALL')})
            result.append({'repeatCell':dict(range=rg,cell={'userEnteredFormat':fmt(st)},fields='userEnteredFormat')})
            edges=layout['estilos'][st][2]
            if edges:
                native={k:dict(style={'thin':'SOLID','medium':'SOLID_MEDIUM','thick':'SOLID_THICK'}.get(v[0],'SOLID'),color=color(v[1])) for k,v in edges.items() if v}
                if native:result.append({'updateBorders':dict(range=rg,**native)})
        return result
    def dv(sheet,addr,condition,strict=True):
        r,c=cell_coord(addr)
        return {'setDataValidation':dict(range=rect(sheet,r+1,c+1,r+1,c+1),rule=dict(condition=condition,strict=strict,showCustomUi=True))}
    result={}
    result['resize']=[{'updateSheetProperties':dict(properties=dict(sheetId=ids['CONFIGURAÇÃO'],gridProperties={'rowCount':last+2}),fields='gridProperties.rowCount')},
                       {'updateSheetProperties':dict(properties=dict(sheetId=ids['ANALISE'],gridProperties={'rowCount':sheets['ANALISE']['linhas']+2}),fields='gridProperties.rowCount')}]
    result['apoio']=[update('DADOS_CRIACAO',r,1,matrix('DADOS_CRIACAO',r,min(r+79,sheets['DADOS_CRIACAO']['linhas']),1,15),'userEnteredValue')
                     for r in range(1,sheets['DADOS_CRIACAO']['linhas']+1,80)]
    bg=fmt(raw['CONFIGURAÇÃO']['A1'][1])
    result['template']=[{'repeatCell':dict(range=rect('CONFIGURAÇÃO',first,1,last+2,16),cell={'userEnteredFormat':bg},fields='userEnteredFormat')},
                        {'updateDimensionProperties':dict(range=dict(sheetId=ids['CONFIGURAÇÃO'],dimension='ROWS',startIndex=first-1,endIndex=last+2),properties={'pixelSize':25},fields='pixelSize')}]
    result['template']+=frames(153,164)+frames(1803,1817)
    for g in model['familias'][:2]:
        result['template'].append(dv('CONFIGURAÇÃO',g['mestre_viu'],{'type':'BOOLEAN'}))
        result['template'].append(dv('CONFIGURAÇÃO',g['estado'],{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':"='DADOS_CRIACAO'!$M$2:$M$4"}]}))
    for m in cfg['menus']:
        if m['onde'] in ('F157','F158'):
            result['template'].append(dv('CONFIGURAÇÃO',m['onde'],{'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':'='+formula_native(m['formula'])}]}))
    result['primeira_copia']=[{'copyPaste':dict(source=rect('CONFIGURAÇÃO',1805,2,1817,15),destination=rect('CONFIGURAÇÃO',1819,2,1831,15),pasteType='PASTE_FORMAT',pasteOrientation='NORMAL')}]
    result['copias']=[{'copyPaste':dict(source=rect('CONFIGURAÇÃO',1805,2,1817,15),destination=rect('CONFIGURAÇÃO',r,2,r+12,15),pasteType='PASTE_FORMAT',pasteOrientation='NORMAL')} for r in range(1833,last,14)]
    # PASTE_FORMAT copiou as mesclagens no Google, mas não os controles.
    result['validacoes_copiadas']=[{'copyPaste':dict(source=rect('CONFIGURAÇÃO',1805,2,1817,15),destination=rect('CONFIGURAÇÃO',r,2,r+12,15),pasteType='PASTE_DATA_VALIDATION',pasteOrientation='NORMAL')} for r in range(1819,last,14)]
    result['entradas']=[update('CONFIGURAÇÃO',153,2,matrix('CONFIGURAÇÃO',153,164,2,7,True))]+[
        update('CONFIGURAÇÃO',r,1,matrix('CONFIGURAÇÃO',r,min(r+99,last),1,16,True)) for r in range(first,last+1,100)]
    result['calculos']=[]
    before={}
    for name,changes in model['depois'].items():
        if name in ('CONFIGURAÇÃO','DADOS_CRIACAO'):continue
        before[name]=model['antes'][name]
        for addr,v in changes.items():
            r,c=cell_coord(addr)
            result['calculos'].append(update(name,r+1,c+1,[{'values':[{'userEnteredValue':value(v)}]}],'userEnteredValue'))
    # O formato sobe somente junto das novas chaves. Células antigas ficam.
    result['analise']=[update('ANALISE',2,2,[{'values':[{'userEnteredValue':value(raw['ANALISE']['B2'][0])}]}],'userEnteredValue')]+[
                        update('ANALISE',r,1,matrix('ANALISE',r,min(r+149,sheets['ANALISE']['linhas']),1,4),'userEnteredValue')
                        for r in range(7487,sheets['ANALISE']['linhas']+1,150)]
    result['menus']=[]
    for m in sheets['INVOCAÇÕES']['menus']:
        if m['formula']!=model['catalogo_familias']:continue
        for area in m['onde'].split():
            from openpyxl.utils.cell import range_boundaries
            c,r,cc,rr=range_boundaries(area)
            result['menus'].append({'setDataValidation':dict(range=rect('INVOCAÇÕES',r,c,rr,cc),rule=dict(condition={'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+m['formula'].lstrip('=')}]},strict=m.get('estrito',False),showCustomUi=True))})
    # As cópias precisam devolver exatamente estas mesclagens.
    expected=[]
    for m in cfg['mescladas']:
        r,c=cell_coord(m.split(':')[0]);rr,cc=cell_coord(m.split(':')[-1])
        if 153<=r+1<=164 or r+1>=first:expected.append([r,c,rr+1,cc+1])
    meta=dict(spreadsheet_id='1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0',before=before,
              rows_config=last+2,rows_apoio=sheets['DADOS_CRIACAO']['linhas'],old_keys=[raw['ANALISE']['A'+str(r)][0] for r in range(2,7487)],
              expected_merges=expected,source_cells=sum(len(v) for v in before.values()))
    (a.saida/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')))
    for stage,requests in result.items():
        # Limita o tamanho transportado pelo executor sem cortar JSON.
        chunks,chunk,size=[],[],0
        for request in requests:
            size_request=len(json.dumps(request,ensure_ascii=False))
            if chunk and (size+size_request>100000 or len(chunk)>=80):
                chunks.append(chunk);chunk=[];size=0
            chunk.append(request);size+=size_request
        if chunk:chunks.append(chunk)
        for i,chunk in enumerate(chunks):
            (a.saida/f'{stage}-{i:02}.json').write_text(json.dumps(chunk,ensure_ascii=False,separators=(',',':')))
    print(json.dumps({'stages':{k:len(v) for k,v in result.items()},'source_cells':meta['source_cells'],'merges':len(expected)}))


if __name__=='__main__':main()
