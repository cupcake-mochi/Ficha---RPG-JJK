"""Migração nativa 7→9, autonomia individual e limites. Sem rede ou Excel.

Exige backup recente. Conserva entradas 1–7 e conteúdo/nota da Definição.
Gera lotes; nenhuma chamada remota acontece neste programa.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT.parent/'evidencias-3b'
before = {a['nome']: {c:v for c,v,*_ in a['celulas']} for a in
          json.loads((EVID/'layout-antes-autonomia9.json').read_text())['layout']['abas']}
layout = json.loads((EVID/'layout-autonomia9-pacote.json').read_text())['layout']
after = {a['nome']:a for a in layout['abas']}
live = {}
for payload in [*json.loads((EVID/'autonomia9-antes-nativo.json').read_text()).values(),
                json.loads((EVID/'autonomia9-estilos-antes.json').read_text()),
                json.loads((EVID/'autonomia9-panels-preflight.json').read_text())]:
    for sheet in payload['sheets']:
        for block in sheet.get('data',[]):
            for r,row in enumerate(block.get('rowData',[]),block.get('startRow',0)+1):
                for c,cell in enumerate(row.get('values',[]),block.get('startColumn',0)+1):
                    live.setdefault((sheet['properties']['title'],r,c),{}).update(cell)
ids={'INVOCAÇÕES':161192554,'CONFIGURAÇÃO':47001,'DADOS_INVOC':1471151297,'ANALISE':1893369489}


def lc(coord):
    s,r=re.fullmatch(r'([A-Z]+)(\d+)',coord).groups()
    return int(r),sum((ord(c)-64)*26**i for i,c in enumerate(s[::-1]))


def letters(n):
    s=''
    while n:
        n,r=divmod(n-1,26);s=chr(65+r)+s
    return s


def grid(name,r,c,rr=None,cc=None):
    return dict(sheetId=ids[name],startRowIndex=r-1,endRowIndex=rr or r,
                startColumnIndex=c-1,endColumnIndex=cc or c)


def pt(s):
    quoted=False;out=''
    for i,ch in enumerate(s):
        if ch=='"':quoted=not quoted
        if not quoted:
            if ch==',':ch=';'
            elif ch=='.' and s[i-1:i].isdigit() and s[i+1:i+2].isdigit():ch=','
        out+=ch
    return out


def uv(value):
    if value is None or value=='':return {}
    if isinstance(value,bool):return {'boolValue':value}
    if isinstance(value,(int,float)):return {'numberValue':value}
    return {'formulaValue':pt(value)} if value.startswith('=') else {'stringValue':value.lstrip("'")}


def canon(value):
    value=value or {}
    if value.get('formulaValue'):
        return {'formulaValue':re.sub(r"'([A-Za-z_][A-Za-z_0-9]*)'!",r'\1!',value['formulaValue'])}
    return {} if value.get('stringValue')=='' else value


requests=[];guards=[];moved=[]


def write(name,r,c,data,fields='userEnteredValue,note'):
    requests.append({'updateCells':{'start':{'sheetId':ids[name],'rowIndex':r-1,'columnIndex':c-1},
                                   'rows':[{'values':[data]}],'fields':fields}})


def box(name,r,c,rr,cc,fmt,value=None,note='',rich=None,original_uv=None):
    rg=grid(name,r,c,rr,cc)
    requests.append({'repeatCell':{'range':rg,'cell':{'userEnteredFormat':fmt},'fields':'userEnteredFormat'}})
    if (r,c)!=(rr,cc):requests.append({'mergeCells':{'range':rg,'mergeType':'MERGE_ALL'}})
    data={'userEnteredValue':uv(value),'note':note}
    if original_uv is not None:data['userEnteredValue']=original_uv
    if rich:data['textFormatRuns']=rich
    write(name,r,c,data,'userEnteredValue,note,textFormatRuns')


for name,key,count in [('DADOS_INVOC','columnCount',after['DADOS_INVOC']['colunas']),
                        ('ANALISE','rowCount',after['ANALISE']['linhas']+2)]:
    requests.append({'updateSheetProperties':{'properties':{'sheetId':ids[name],'gridProperties':{key:count}},
                                             'fields':'gridProperties.'+key}})
raw={n:{c:v for c,v,*_ in a['celulas']} for n,a in after.items()}
menu='='+next(m['formula'] for m in after['INVOCAÇÕES']['menus'] if 'O50' in m['onde'].split()).lstrip('=')
for i in range(12):
    row=48+198*(i%6);a=9+19*(i//6);b=a+6;end=a+16
    name='INVOCAÇÕES'
    # Não tocar no painel Corpo (termina na mesma linha das novas caixas).
    for r,c,rr,cc in [(row+1,b,row+1,b+1),(row+1,b+2,row+1,b+4),
                      (row+2,b,row+2,b+1),(row+2,b+2,row+2,b+4),
                      (row+3,a,row+3,end),(row+4,a,row+5,end)]:
        requests.append({'unmergeCells':{'range':grid(name,r,c,rr,cc)}})
    inp=live[name,row,b]['userEnteredFormat'];head=live[name,row-1,b]['userEnteredFormat']
    blank=live[name,row+6,a]['userEnteredFormat']
    # Guarda e move as duas entradas já publicadas, antes de limpar sua grade.
    old_extra=[live.get((name,row+2,c),{}) for c in (b,b+2)]
    requests.append({'updateCells':{'range':grid(name,row+1,b,row+2,b+4),
        'rows':[{'values':[{}]*5},{'values':[{}]*5}],
        'fields':'userEnteredValue,note,dataValidation,textFormatRuns'}})
    for j,(left,right) in enumerate(((b,b),(b+1,b+1),(b+2,b+2),(b+3,b+4)),6):
        for rr,fmt in ((row+1,head),(row+2,inp)):
            coord=letters(left)+str(rr)
            note=after[name]['notas'].get(coord,'')
            value=raw[name].get(coord)
            rich=None
            if rr==row+2 and j<=7:
                prior=old_extra[j-6]
                value=next(iter(prior.get('userEnteredValue',{}).values()),None)
                note=prior.get('note',note);rich=prior.get('textFormatRuns')
                moved.append([name,letters(b if j==6 else b+2)+str(rr),coord])
            box(name,rr,left,rr,right,fmt,value,note,rich,
                old_extra[j-6].get('userEnteredValue',{}) if rr==row+2 and j<=7 else None)
        requests.append({'setDataValidation':{'range':grid(name,row+2,left),'rule':{
            'condition':{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':menu}]},'showCustomUi':True}}})
    for c in range(b,b+5):
        coord=letters(c)+str(row-1)
        write(name,row-1,c,{'userEnteredValue':uv(raw[name][coord]),'note':after[name]['notas'][coord]})
    # Só os dois campos da nova linha de autonomia; nada no painel da alma.
    for c in range(a,a+5):
        prior=live.get((name,row+2,c),{})
        if canon(prior.get('userEnteredValue')) or prior.get('note'):
            raise ValueError('Folga de autonomia ocupada: '+letters(c)+str(row+2))
    for left,right,fmt in ((a,a+1,head),(a+2,a+4,inp)):
        coord=letters(left)+str(row+2)
        box(name,row+2,left,row+2,right,fmt,raw[name][coord],after[name]['notas'][coord])
    requests.append({'setDataValidation':{'range':grid(name,row+2,a+2),'rule':{
        'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':v} for v in ('Autônoma','Não autônoma')]},
        'strict':True,'showCustomUi':True}}})
    old_def=live[name,row+4,a]
    title=live[name,row+3,a]
    for rr in range(row+3,row+7):
        for cc in range(a,end+1):
            prior=live.get((name,rr,cc),{})
            if (rr,cc) not in ((row+3,a),(row+4,a)) and (canon(prior.get('userEnteredValue')) or prior.get('note')):
                raise ValueError('Folga da definição ocupada: '+letters(cc)+str(rr))
    requests.append({'updateCells':{'range':grid(name,row+3,a,row+6,end),
        'rows':[{'values':[{}]*(end-a+1)} for _ in range(4)],
        'fields':'userEnteredValue,note,dataValidation,textFormatRuns'}})
    requests.append({'repeatCell':{'range':grid(name,row+3,a,row+3,end),
        'cell':{'userEnteredFormat':blank},'fields':'userEnteredFormat'}})
    box(name,row+4,a,row+4,end,title['userEnteredFormat'],'DEFINIÇÃO',title.get('note',''))
    value=next(iter(old_def.get('userEnteredValue',{}).values()),None)
    box(name,row+5,a,row+6,end,old_def['userEnteredFormat'],value,old_def.get('note',''),old_def.get('textFormatRuns'),old_def.get('userEnteredValue',{}))
    moved.append([name,letters(a)+str(row+4),letters(a)+str(row+5)])
    if i<6:
        requests.append({'updateDimensionProperties':{'range':{'sheetId':ids[name],'dimension':'ROWS',
            'startIndex':row+1,'endIndex':row+2},'properties':{'pixelSize':32},'fields':'pixelSize'}})
    write(name,row-2,b,{'note':after[name]['notas'][letters(b)+str(row-2)]},'note')

# Tabela de campanha só na folga previamente lida; sem selecionar autonomia.
name='CONFIGURAÇÃO'
for rr in range(133,150):
    for cc in range(2,8):
        prior=live.get((name,rr,cc),{})
        if canon(prior.get('userEnteredValue')) or prior.get('note'):
            raise ValueError('Área da configuração ocupada')
new_coords={coord for coord,value,*_ in after[name]['celulas'] if 133<=lc(coord)[0]<=149 and 2<=lc(coord)[1]<=7 and value is not None}
merges={m.split(':')[0]:m.split(':')[1] for m in after[name]['mescladas'] if m.split(':')[0] in new_coords}
sources={'B133':(9,2),'B135':(5,2),'B147':(5,2)}
for coord in sorted(new_coords|{'F'+str(r) for r in range(139,146)},key=lc):
    rr,cc=lc(coord);end=merges.get(coord,coord);er,ec=lc(end)
    src=sources.get(coord,(10,2) if rr==138 else (46,4) if cc in (5,6,7) else (46,2))
    fmt=live[name,*src]['userEnteredFormat']
    box(name,rr,cc,er,ec,fmt,raw[name].get(coord),after[name]['notas'].get(coord,''))
for r in range(139,146):
    formula=f'=OR(ISBLANK(F{r});IFERROR(AND(ISNUMBER(F{r});F{r}>=0;F{r}<=9;INT(F{r})=F{r});FALSE))'
    requests.append({'setDataValidation':{'range':grid(name,r,6),'rule':{
        'condition':{'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':formula}]},'strict':True}}})

for name in ('DADOS_INVOC','ANALISE'):
    for coord,value,*_ in after[name]['celulas']:
        old=before[name].get(coord)
        if uv(old)==uv(value):continue
        r,c=lc(coord);actual=live.get((name,r,c),{}).get('userEnteredValue')
        outside=(name=='DADOS_INVOC' and c>465) or (name=='ANALISE' and r>7412)
        if not outside and canon(actual)!=canon(uv(old)):
            raise ValueError(f'Guarda divergente: {name} {coord}: {actual} != {uv(old)}')
        guards.append([name,coord,uv(old),uv(value)])
        write(name,r,c,{'userEnteredValue':uv(value)},'userEnteredValue')
requests.append({'copyPaste':{'source':grid('ANALISE',7412,1,7412,4),
    'destination':grid('ANALISE',7413,1,after['ANALISE']['linhas'],4),'pasteType':'PASTE_FORMAT'}})
chunks=[];batch=[];size=0
for item in requests:
    n=len(json.dumps(item,ensure_ascii=False))
    if batch and (size+n>55000 or len(batch)>=120):chunks.append(batch);batch=[];size=0
    batch.append(item);size+=n
if batch:chunks.append(batch)
dest=EVID/'autonomia9-pedidos';dest.mkdir(exist_ok=True)
for i,chunk in enumerate(chunks):
    (dest/f'{i:03}.json').write_text(json.dumps(chunk,ensure_ascii=False,separators=(',',':')))
manifest={'requests':len(requests),'lotes':len(chunks),'guards':guards,'moved':moved}
(EVID/'autonomia9-manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False))
print(json.dumps({'pedidos':len(requests),'lotes':len(chunks),'guardas':len(guards),'movidos':len(moved)}))
