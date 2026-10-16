#!/usr/bin/env python3
"""Prepara lotes para a cópia descartável de peças. Sem rede ou Excel.

O destino é fixo e distinto da revisão/oficial. Repetições de fórmulas são
copiadas nativamente; cartões copiam formato, notas e validação juntos.
"""
import json
import argparse
from pathlib import Path
import sys
from openpyxl.utils.cell import range_boundaries

ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT/'ficha'),str(ROOT/'ficha-v01')]
import emitir_gs as gs
import indice_ficha as ix
import custom_pecas as cp

EVID=ROOT.parent/'evidencias-3b'
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--revisao',action='store_true',help='Exige snapshot e guarda da revisão, após testar a cópia')
args=ap.parse_args()
DEST='1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0' if args.revisao else '1D215acC6Dxhu8i7x0aF7pmiNbJ95_U1CiH4980QozLk'
MODEL=json.loads((EVID/'pecas-modelo.json').read_text())
META=json.loads((EVID/('pecas-revisao-metadata.json' if args.revisao else 'pecas-teste-metadata.json')).read_text())
assert META['spreadsheetId']==DEST
assert META['properties']['title'].startswith('Ciclo Maldito — B47 — cópia nativa para revisão' if args.revisao else 'TESTE DESCARTÁVEL')
if args.revisao:
    guarda=json.loads((EVID/'pecas-revisao-guarda.json').read_text())
    assert guarda['resultado']=='OK' and guarda['comparadas']==4270 and not guarda['diferencas']
TABS={t['nome']:t for t in MODEL['layout']['abas']}
IDS={s['properties']['title']:s['properties']['sheetId'] for s in META['sheets']}
IDS.update({cp.MEL:47008,cp.RES:47009})
RAW={s:{c:(v,st) for c,v,st,*_ in t['celulas']} for s,t in TABS.items()}
OUT=EVID/('pecas-lotes-revisao' if args.revisao else 'pecas-lotes-nativos');OUT.mkdir(exist_ok=True)
BATCHES=[]


def grid(s,r,c,rr=None,cc=None):
    return dict(sheetId=IDS[s],startRowIndex=r-1,endRowIndex=rr or r,
                startColumnIndex=c-1,endColumnIndex=cc or c)


def pt(formula):
    quoted=False;out=''
    for i,ch in enumerate(formula):
        if ch=='"':quoted=not quoted
        if not quoted:
            if ch==',':ch=';'
            elif ch=='.' and formula[i-1:i].isdigit() and formula[i+1:i+2].isdigit():ch=','
        out+=ch
    return out


def uv(value):
    if value is None or value=='':return {}
    if isinstance(value,bool):return {'boolValue':value}
    if isinstance(value,(int,float)):return {'numberValue':value}
    if value.startswith('='):return {'formulaValue':pt(value)}
    return {'stringValue':value}


def rgb(value):
    return {k:int(value[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}


def fmt(index):
    font,bg,border,align,num=MODEL['layout']['estilos'][index]
    out={}
    if font:
        name,size,color,bold,italic=font
        out['textFormat']=dict(fontFamily=name,fontSize=round(size),foregroundColor=rgb(color),bold=bold,italic=italic)
    if bg:out['backgroundColor']=rgb(bg)
    if align:
        out.update(horizontalAlignment=align[0].upper(),verticalAlignment={'center':'MIDDLE','top':'TOP','bottom':'BOTTOM'}[align[1]],
                   wrapStrategy='WRAP' if align[2] else 'CLIP')
    return out,border


def emit(label,requests):
    """Lotes de até30KB, sem dividir uma requisição estruturada."""
    batch=[];size=0
    for req in requests:
        assert len(req)==1
        n=len(json.dumps(req,ensure_ascii=False).encode())
        if batch and size+n>30000:
            save(label,batch);batch=[];size=0
        batch.append(req);size+=n
    if batch:save(label,batch)


def save(label,requests):
    name=f'{len(BATCHES):03d}-{label}.json'
    payload={'spreadsheet_id':DEST,'requests':requests}
    (OUT/name).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    BATCHES.append(dict(arquivo=name,etapa=label,pedidos=len(requests)))


def values_requests(s,values):
    """Trechos contíguos por linha; nenhuma célula vizinha é apagada."""
    byrow={}
    for a1,value in values.items():
        r,c=ix._lc(a1);byrow.setdefault(r,{})[c]=value
    out=[]
    for r,cols in sorted(byrow.items()):
        seq=[]
        for c in sorted(cols):
            if seq and c!=seq[-1]+1:
                out.append((r,seq));seq=[]
            seq.append(c)
        if seq:out.append((r,seq))
    return [{'updateCells':{'range':grid(s,r,cs[0],r,cs[-1]),
        'rows':[{'values':[{'userEnteredValue':uv(values[cp.coord(r,c)])} for c in cs]}],
        'fields':'userEnteredValue'}} for r,cs in out]


def formulas_and_values(s,values):
    triples=sorted([[*ix._lc(c),v] for c,v in values.items()],key=lambda x:(x[0],x[1]))
    blocks=gs._blocos_para_baixo(triples)
    base=[v for v in triples if not any(r<v[0]<=rr and c<=v[1]<=cc for r,c,rr,cc in blocks)]
    emit('valores-'+s.lower(),values_requests(s,{cp.coord(v[0],v[1]):v[2] for v in base}))
    emit('formulas-'+s.lower(),[{'copyPaste':{'source':grid(s,r,c,r,cc),
        'destination':grid(s,r+1,c,rr,cc),'pasteType':'PASTE_FORMULA','pasteOrientation':'NORMAL'}} for r,c,rr,cc in blocks])


requests=[]
for s in [cp.MEL,cp.RES]:
    assert s not in [p['properties']['title'] for p in META['sheets']]
    t=TABS[s]
    requests.append({'addSheet':{'properties':{'sheetId':IDS[s],'title':s,'hidden':True,
        'gridProperties':{'rowCount':t['linhas']+2,'columnCount':t['colunas'],'hideGridlines':True}}}})
for s in ['CONFIGURAÇÃO','DADOS_AM','DADOS_INVOC','ANALISE']:
    t=TABS[s];old=next(x['properties']['gridProperties'] for x in META['sheets'] if x['properties']['title']==s)
    props={}
    if t['linhas']>old['rowCount']:props['rowCount']=t['linhas']+2
    if t['colunas']>old['columnCount']:props['columnCount']=t['colunas']
    if props:requests.append({'updateSheetProperties':{'properties':{'sheetId':IDS[s],'gridProperties':props},
        'fields':','.join('gridProperties.'+k for k in props)}})
cfg=TABS['CONFIGURAÇÃO'];old_end=MODEL['fim_familias']
base_idx=RAW['CONFIGURAÇÃO']['A1'][1];base,_=fmt(base_idx)
requests.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',old_end+1,1,MODEL['fim'],16),
    'cell':{'userEnteredFormat':base},'fields':'userEnteredFormat'}})
requests.append({'updateDimensionProperties':{'range':{'sheetId':IDS['CONFIGURAÇÃO'],'dimension':'ROWS',
    'startIndex':old_end,'endIndex':MODEL['fim']},'properties':{'pixelSize':25},'fields':'pixelSize'}})
emit('estrutura',requests)

for s in [cp.MEL,cp.RES]:
    formulas_and_values(s,{c:v for c,(v,_) in RAW[s].items() if v is not None})

# Só os dois moldes e os cabeçalhos; o restante nasce de cópia nativa.
merges={ix._lc(a.split(':')[0]):range_boundaries(a) for a in cfg['mescladas']}
menus={v['onde']:v for v in cfg['menus'] if ' ' not in v['onde'] and ':' not in v['onde']}


def draw(r1,r2,c1=1,c2=16):
    requests=[]
    for a1,(value,style) in RAW['CONFIGURAÇÃO'].items():
        r,c=ix._lc(a1)
        if not (r1<=r<=r2 and c1<=c<=c2) or style is None:continue
        box=merges.get((r,c),(c,r,c,r));_,_,cc,rr=box
        assert rr<=r2 and cc<=c2
        rg=grid('CONFIGURAÇÃO',r,c,rr,cc)
        if (r,c)!=(rr,cc):requests.append({'mergeCells':{'range':rg,'mergeType':'MERGE_ALL'}})
        f,b=fmt(style)
        requests.append({'repeatCell':{'range':rg,'cell':{'userEnteredFormat':f},'fields':'userEnteredFormat'}})
        if b:
            edge={side:{'style':'SOLID','color':rgb(color)} for side,(_,color) in b.items()}
            requests.append({'updateBorders':{'range':rg,**edge}})
        data={'userEnteredValue':uv(value),'note':cfg['notas'].get(a1,'')}
        if isinstance(value,bool):data['dataValidation']={'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}
        elif a1 in menus:
            m=menus[a1];data['dataValidation']={'condition':{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+m['formula'].lstrip('=')}]},'strict':True,'showCustomUi':True}
        requests.append({'updateCells':{'range':grid('CONFIGURAÇÃO',r,c),'rows':[{'values':[data]}],
            'fields':'userEnteredValue,note,dataValidation'}})
    return requests


for kind,step in [('melhoria',cp.PASSO_MEL),('restricao',cp.PASSO_RES)]:
    regs=[g for g in MODEL['registros'] if g['tipo']==kind];first=regs[0]['r']
    emit('molde-'+kind,draw(first-2,first+step-2))
    copies=[]
    # Destinos múltiplos exatos da altura do molde, sem copiar a última coluna
    # vazia quando a capacidade termina em um cartão ímpar.
    pairs=len(regs)//2
    for start in range(1,pairs,50):
        count=min(50,pairs-start)
        copies.append({'copyPaste':{'source':grid('CONFIGURAÇÃO',first,1,first+step-1,16),
            'destination':grid('CONFIGURAÇÃO',first+start*step,1,first+(start+count)*step-1,16),
            'pasteType':'PASTE_NORMAL','pasteOrientation':'NORMAL'}})
    emit('copias-'+kind,copies)
    if len(regs)%2:emit('ultimo-'+kind,draw(regs[-1]['r'],regs[-1]['r']+step-2,2,7))
    # A fórmula da nota usa referência absoluta: cada cópia recebe seu aviso.
    chosen={}
    for g in regs:
        chosen[cp.coord(g['r'],g['c'])]=RAW['CONFIGURAÇÃO'][cp.coord(g['r'],g['c'])][0]
        chosen[g['aviso']]=RAW['CONFIGURAÇÃO'][g['aviso']][0]
    emit('titulos-avisos-'+kind,values_requests('CONFIGURAÇÃO',chosen))

for s in ['DADOS_AM','DADOS_INVOC']:
    formulas_and_values(s,MODEL['depois'][s])

# Menus nos cartões originais: somente as fontes de Melhoria/Restrição mudam.
for s in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
    req=[]
    for m in TABS[s]['menus']:
        if not any(name in m['formula'] for name in [cp.MEL,cp.RES]):continue
        for area in m['onde'].split():
            c,r,cc,rr=range_boundaries(area)
            req.append({'setDataValidation':{'range':grid(s,r,c,rr,cc),'rule':{'condition':{
                'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+m['formula'].lstrip('=')}]},
                'showCustomUi':True,'strict':m.get('estrito',False)}}})
    emit('menus-'+('personagem' if s.startswith('FICHA') else 'entidades'),req)

an=RAW['ANALISE'];old_rows=9083
req=values_requests('ANALISE',{'B2':an['B2'][0]})
for r in range(old_rows+1,TABS['ANALISE']['linhas']+1,60):
    rr=min(r+59,TABS['ANALISE']['linhas'])
    req.append({'updateCells':{'range':grid('ANALISE',r,1,rr,4),
        'rows':[{'values':[{'userEnteredValue':uv(an.get(cp.coord(row,c),(None,None))[0])} for c in range(1,5)]}
                for row in range(r,rr+1)],'fields':'userEnteredValue'}})
emit('analise-formato9',req)
manifest=dict(destino=DEST,abas=IDS,lotes=BATCHES,inicio=MODEL['inicio'],fim=MODEL['fim'],
    regras='Migração pontual com entradas preservadas. Não executar construir().')
(OUT/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(dict(lotes=len(BATCHES),pedidos=sum(x['pedidos'] for x in BATCHES),destino=DEST)))
