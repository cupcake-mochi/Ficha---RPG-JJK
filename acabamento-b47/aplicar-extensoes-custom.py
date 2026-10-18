"""Planejador offline da migração nativa; não reconstrói nem importa arquivo.

Recebe modelos e snapshots atuais. Os lotes resultantes só são aplicáveis à
cópia identificada no snapshot, com releitura e comparação após a aplicação.
Entradas preenchidas dos antigos seletores exigem migração explícita por nome.
"""
import copy
import json
import re
import sys
from pathlib import Path
from openpyxl.utils.cell import coordinate_to_tuple, range_boundaries, get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47')]
import extensoes_custom as e
from lotes import native_value, format_, pt

def load(p):
    d=json.loads(Path(p).read_text(encoding='utf8'));return d.get('structuredContent',d)

def cells(d):
    out={}
    for s in d['sheets']:
        name=s['properties']['title']
        for g in s.get('data',[]):
            for y,row in enumerate(g.get('rowData',[])):
                for x,c in enumerate(row.get('values',[])):
                    out[name,L(x+g.get('startColumn',0)+1)+str(y+g.get('startRow',0)+1)]=c
    return out

def plan(base,target,metadata,structure,snapshot,config):
    actual={**cells(snapshot),**cells(config)}
    sheets={s['properties']['title']:s for s in metadata['sheets']}
    oldstructure={s['properties']['title']:s for s in structure['updatedSpreadsheet']['sheets']}
    for name,ins in e.INSERCOES.items():
        assert sheets[name]['properties']['gridProperties']['rowCount']==next(a['linhas'] for a in base['layout']['abas'] if a['nome']==name)
    original=copy.deepcopy(base['layout']);e.deslocar(original)
    oldtabs={a['nome']:a for a in original['abas']}
    old={a['nome']:{c[0]:c for c in a['celulas']} for a in original['abas']}
    tabs={a['nome']:a for a in target['layout']['abas']}
    requests=[];stats={}
    def grid(s,c):
        ca,r,cb,rr=range_boundaries(c)
        return dict(sheetId=sheets[s]['properties']['sheetId'],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=ca-1,endColumnIndex=cb)
    def write(s,c,cell,fields='userEnteredValue'):
        r,col=coordinate_to_tuple(c)
        requests.append({'updateCells':{'start':dict(sheetId=sheets[s]['properties']['sheetId'],rowIndex=r-1,columnIndex=col-1),'rows':[{'values':[cell]}],'fields':fields}})
    # Drop only row-group structure, preserving all cells, styles and columns.
    for name in e.INSERCOES:
        sid=sheets[name]['properties']['sheetId']
        for g in sorted(oldstructure[name].get('rowGroups',[]),key=lambda g:g['depth'],reverse=True):
            requests.append({'deleteDimensionGroup':{'range':g['range']}})
        for at,n in reversed(e.INSERCOES[name]):
            requests.append({'insertDimension':{'range':dict(sheetId=sid,dimension='ROWS',startIndex=at-1,endIndex=at+n-1),'inheritFromBefore':True}})
    # New panels and deliberate mirrors; normal references move natively with
    # row insertion. Do not overwrite any other literal or player override.
    for name,a in tabs.items():
        if name not in sheets:continue
        for item in {x[0]:x for x in a['celulas']}.values():
            c,v,style=item[:3];prior=old.get(name,{}).get(c)
            if prior is not None and prior[1:]==item[1:]:continue
            # Literal ANALISE origins do not follow native row insertion.
            if name=='ANALISE' and prior is not None and prior[1]==v:continue
            cell={'userEnteredValue':native_value(v)};fields='userEnteredValue'
            link=next((x for x in a.get('links_paineis',[]) if x['celula']==c),None)
            if link:
                textstyle=format_(target['layout']['estilos'][style])['textFormat']
                cell['textFormatRuns']=[{'startIndex':0,'format':{'link':{'uri':f'#gid={sheets[name]["properties"]["sheetId"]}&range={link["alvo"]}'},'foregroundColor':textstyle['foregroundColor'],'underline':False}}]
                fields+=',textFormatRuns'
            if style is not None and (prior is None or prior[2]!=style):
                cell['userEnteredFormat']=format_(target['layout']['estilos'][style]);fields+=',userEnteredFormat,dataValidation'
                if isinstance(v,bool):cell['dataValidation']={'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}
            write(name,c,cell,fields);stats[name]=stats.get(name,0)+1
        # Origin strings need comparison against the unshifted source.
        if name in ('ANALISE','DADOS_AM'):
            src={x[0]:x[1] for x in next(x for x in base['layout']['abas'] if x['nome']==name)['celulas']}
            for c,v,*_ in a['celulas']:
                if isinstance(v,str) and not v.startswith('=') and src.get(c)!=v:
                    write(name,c,{'userEnteredValue':native_value(v)})
    # Sheets moves reference tokens but leaves an internal hyperlink's range
    # fragment as text. Rebuild only that documented fragment, preserving all
    # other URL/text content and translating reference tokens separately.
    owners={str(s['properties']['sheetId']):n for n,s in sheets.items() if n in e.INSERCOES}
    for (name,c),cell in actual.items():
        f=cell.get('userEnteredValue',{}).get('formulaValue','')
        def jump(m):
            return m[1]+e.coord(owners[m[2]],m[3]) if m[2] in owners else m[0]
        changed=re.sub(r'(#gid=(\d+)&range=)([A-Z]+\d+)',jump,f)
        if changed!=f:
            write(name,e.coord(name,c),{'userEnteredValue':{'formulaValue':e.formula(changed,name)}})
    # Refuse to silently discard a legacy manual selection. A populated sheet
    # must be migrated by identity, not by its old arbitrary selector position.
    for a in base['layout']['abas']:
        if a['nome']!='FICHA':continue
        for c,v,*_ in a['celulas']:
            r,col=coordinate_to_tuple(c)
            if col in (6,26) and (413<=r<=424 or 429<=r<=434):
                value=actual.get(('FICHA',c),{}).get('effectiveValue',{})
                assert not value.get('stringValue'), 'Escolha custom antiga preenchida: '+c+'; migrar por nome antes de continuar'
    # Preserve the previous technique states when a definition exists. Blank
    # definitions keep the automatic blank/default formula in their new row.
    for t in target['auditoria']['transferencias']:
        if t['tipo']!='Família':continue
        name=actual.get(('DADOS_CRIACAO','B'+str(t['n']+1)),{}).get('effectiveValue',{}).get('stringValue','')
        cell=actual.get(('CONFIGURAÇÃO',t['de']),{}).get('userEnteredValue',{})
        if name and cell and 'formulaValue' not in cell:
            write(t['aba_destino'],t['para'],{'userEnteredValue':cell})
    # Newly merged rectangles only; existing merges follow native inserts.
    for name in e.INSERCOES:
        a=tabs[name];prior=set(oldtabs[name]['mescladas']);sid=sheets[name]['properties']['sheetId']
        for m in a['mescladas']:
            if m not in prior:requests.append({'mergeCells':{'range':grid(name,m),'mergeType':'MERGE_ALL'}})
        groups=a['grupos']['linhas']
        for lo,hi,closed in groups:
            rg=dict(sheetId=sid,dimension='ROWS',startIndex=lo-1,endIndex=hi)
            requests.append({'addDimensionGroup':{'range':rg}})
        for lo,hi,closed in sorted(groups,key=lambda g:sum(x[0]<=g[0] and g[1]<=x[1] for x in groups),reverse=True):
            rg=dict(sheetId=sid,dimension='ROWS',startIndex=lo-1,endIndex=hi)
            depth=sum(x[0]<=lo and hi<=x[1] for x in groups)
            requests.append({'updateDimensionGroup':{'dimensionGroup':{'range':rg,'depth':depth,'collapsed':closed},'fields':'collapsed'}})
        # Match the collapsed-by-default source, including previously hidden
        # nested groups. Inner groups must remain hidden under open parents.
        requests.append({'updateDimensionProperties':{'range':dict(sheetId=sid,dimension='ROWS',startIndex=0,endIndex=a['linhas']),'properties':{'hiddenByUser':False},'fields':'hiddenByUser'}})
        for lo,hi,closed in groups:
            if closed:requests.append({'updateDimensionProperties':{'range':dict(sheetId=sid,dimension='ROWS',startIndex=lo-1,endIndex=hi),'properties':{'hiddenByUser':True},'fields':'hiddenByUser'}})
        for lo,hi in a.get('linhas_ocultas',[]):
            requests.append({'updateDimensionProperties':{'range':dict(sheetId=sid,dimension='ROWS',startIndex=lo-1,endIndex=hi),'properties':{'hiddenByUser':True},'fields':'hiddenByUser'}})
        requests.append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':{'rowGroupControlAfter':False}},'fields':'gridProperties.rowGroupControlAfter'}})
        for panel in target['auditoria']['paineis']:
            if panel['aba']!=name:continue
            lo,hi=panel['cabecalho'],panel['ultima']
            for r,h in dict(a['linhas_alt']).items():
                if lo<=r<=hi:requests.append({'updateDimensionProperties':{'range':dict(sheetId=sid,dimension='ROWS',startIndex=r-1,endIndex=r),'properties':{'pixelSize':round(h*4/3)},'fields':'pixelSize'}})
    # Remove the old selectors' validations, then add the new menus only.
    for name,a in oldtabs.items():
        if name not in sheets:continue
        newmenus=tabs[name]['menus']
        newwhere={m['onde'] for m in newmenus}
        for m in a['menus']:
            if m['onde'] not in newwhere:
                for region in m['onde'].split():requests.append({'setDataValidation':{'range':grid(name,region)}})
        prior={m['onde']:m for m in a['menus']}
        for m in newmenus:
            if prior.get(m['onde'])==m:continue
            f=m['formula']
            if f.startswith('"') and f.endswith('"'):
                cond={'type':'ONE_OF_LIST','values':[{'userEnteredValue':v} for v in f[1:-1].split(',')]}
            else:cond={'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+pt(f.lstrip('='))}]}
            rule={'condition':cond,'strict':m.get('estrito',False),'showCustomUi':True}
            for region in m['onde'].split():requests.append({'setDataValidation':{'range':grid(name,region),'rule':rule}})
        for c,note in a.get('notas',{}).items():
            if tabs[name].get('notas',{}).get(c)!=note:
                write(name,c,{'note':tabs[name].get('notas',{}).get(c,'')},'note')
    chunks=[];chunk=[];size=0
    for q in requests:
        n=len(json.dumps(q,ensure_ascii=False))
        if chunk and (size+n>90000 or len(chunk)>=180):chunks.append(chunk);chunk=[];size=0
        chunk.append(q);size+=n
    if chunk:chunks.append(chunk)
    return {'destino':snapshot['spreadsheetId'],'alteracoes':stats,'lotes':chunks}

if __name__=='__main__':
    if len(sys.argv)!=8:raise SystemExit('base alvo metadata estrutura snapshot config saida')
    p=plan(*(load(x) for x in sys.argv[1:7]))
    Path(sys.argv[7]).write_text(json.dumps(p,ensure_ascii=False),encoding='utf8')
    print(json.dumps({'destino':p['destino'],'alteracoes':p['alteracoes'],'lotes':len(p['lotes']),'pedidos':sum(map(len,p['lotes']))},ensure_ascii=False))
