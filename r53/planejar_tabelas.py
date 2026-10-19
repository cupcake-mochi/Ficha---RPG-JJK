"""Requisições nativas para tabelas técnicas, sem importar XLSX ou pedir OAuth.

Usa os snapshots atuais para converter as versões guardadas. As entradas
visíveis não são reescritas. O conector executará os lotes sequencialmente.
"""
import json,sys,copy,re,hashlib
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import coordinate_to_tuple,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'r53'),str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47')]
import transporte as T,emitir_gs as E
from preparar_nativo import native_value

NAMES=['MONTAGENS','DADOS_R53_CATALOGO','DADOS','DADOS_AM','DADOS_INVOC','DADOS_CUSTOM','DADOS_MELHORIAS','DADOS_RESTRICOES','DADOS_FORMAS','DADOS_APTIDOES','DADOS_TALENTOS','ANALISE','DADOS_R53']

def main():
 model=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=model['r53'];tabs={a['nome']:a for a in model['layout']['abas']}
 meta=json.loads((ROOT/'r53/saidas/metadados-antes-integral.json').read_text());sheets={s['properties']['title']:s for s in meta['sheets']}
 originals={}
 for p in (ROOT/'r53/saidas/snapshot-integral').glob('montagens-*.json'):
  for s in json.loads(p.read_text())['sheets']:
   for d in s.get('data',[]):
    for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
     for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):originals[(r,c)]=cell.get('userEnteredValue',{})
 def value(r,c):
  x=originals.get((r,c),{});return next(iter(x.values()),'')
 known={g['id']:g for g in tr['contextos']};sections=[]
 for (r,c),v in originals.items():
  if c!=1:continue
  text=next(iter(v.values()),'');m=re.search(r'([a-z][a-z0-9.]+) ·',text) if isinstance(text,str) else None
  if m and m[1] in known:sections.append((r,m[1]))
 sections.sort();fieldmap={label:k for k,label,_ in tr['editor_campos']};defaults={}
 source={coordinate_to_tuple(v[0]):v for v in tabs['MONTAGENS']['celulas']}
 first=tr['contextos'][0]
 for k,label,kind in tr['editor_campos']:defaults[k]=source[(first['campos'][k],2)][1]
 kept=[];ledger=[]
 for index,(r,id_) in enumerate(sections):
  end=sections[index+1][0] if index+1<len(sections) else max(k[0] for k in originals)+1;g=known[id_]
  for c in range(2,10):
   if g['classes']==[None] and c!=2:continue
   cl=None if g['classes']==[None] else value(r+1,c)
   if cl not in g['classes']:continue
   destcol=g['classes'].index(cl)+2;vals={};raw={};flags={};points={}
   for rr in range(r+2,end):
    label=value(rr,1);v=value(rr,c)
    if label in fieldmap:
     raw[label]=originals.get((rr,c),{})
     if raw[label]:vals[fieldmap[label]]=v
    if label in ['Dano','Cura direta','Vida temporária'] and originals.get((rr,c)):flags[{'Dano':'Dano','Cura direta':'Cura','Vida temporária':'PV temporários'}[label]]=v;raw[label]=originals.get((rr,c),{})
    if label in ['Pontos de dano','Pontos de cura','Pontos de vida temporária'] and originals.get((rr,c)):points[{'Pontos de dano':'Dano','Pontos de cura':'Cura','Pontos de vida temporária':'PV temporários'}[label]]=v;raw[label]=originals.get((rr,c),{})
   if 'funcao1' not in vals:
    n=0
    for f in ['Dano','Cura','PV temporários']:
     if flags.get(f) is True or (isinstance(points.get(f),(int,float)) and points[f]>0):
      n+=1;vals['funcao'+str(n)]=f if flags.get(f) is True else '';vals['pontos'+str(n)]=points.get(f,0)
      if flags.get(f) is not True:vals['migracao']='Revisão necessária'
     if f in flags and type(flags[f]) is not bool:vals['migracao']='Revisão necessária'
    if vals.get('preparada') is True and vals.get('res_dano')=='TR' and not vals.get('tr_dano'):vals['migracao']='Revisão necessária'
   if vals.get('preparada') is True and 'forma' not in vals:vals['forma']='';vals['migracao']='Revisão necessária'
   meaningful=any(k in defaults and (type(v) is not type(defaults[k]) or v!=defaults[k]) for k,v in vals.items())
   if not meaningful:continue
   for k,v in vals.items():
    if k not in g['campos']:continue
    if isinstance(v,str) and v.startswith(('=',"'")):v="'"+v
    key=(g['campos'][k],destcol)
    if key not in source:raise ValueError('Destino de versão fora do cadastro')
    source[key][1]=v
   kept.append([id_,'maxima' if cl is None else cl]);ledger.append([id_,'maxima' if cl is None else cl,json.dumps(raw,ensure_ascii=False),'Preservado; original recuperável no backup nativo'])
 # Guardas de compacidade: a reconstrução das fórmulas precisa ser exata.
 values={};copies={};roundtrips={}
 for name in NAMES:
  a=tabs[name];allvals=[[r,c,v[1],v[2]] for v in a['celulas'] for r,c in [coordinate_to_tuple(v[0])]]
  vs=T.valores_transporte(a);blocs=E._blocos_para_baixo(allvals) if a.get('abaixo') else []
  original={(r,c):v for r,c,v,*_ in allvals};restored={(r,c):v for r,c,v,*_ in vs}
  for ra,c1,rb,c2 in blocs:
   for r in range(ra+1,rb+1):
    for c in range(c1,c2+1):restored[(r,c)]=E.desloca(restored[(ra,c)],r-ra)
  if restored!=original:raise ValueError('Transporte não reconstrói '+name)
  values[name]=vs;copies[name]=blocs;roundtrips[name]=len(original)
 phases=[]
 def phase(name,requests):phases.append((name,requests))
 prep=[]
 for name in NAMES:
  a=tabs[name];s=sheets[name];sid=s['properties']['sheetId'];grid=s['properties']['gridProperties'];grow={}
  if a['linhas']>grid['rowCount']:grow['rowCount']=a['linhas']
  if a['colunas']>grid['columnCount']:grow['columnCount']=a['colunas']
  if grow:prep.append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':grow},'fields':','.join('gridProperties.'+k for k in grow)}})
  prep.append({'updateSheetProperties':{'properties':{'sheetId':sid,'hidden':True},'fields':'hidden'}})
 if any(s['properties']['sheetId']==53018006 for s in meta['sheets']):raise ValueError('ID do registro de recuperação já usado')
 prep.append({'addSheet':{'properties':{'sheetId':53018006,'title':'R53_LEGADO','hidden':True,'gridProperties':{'rowCount':max(10,len(ledger)+4),'columnCount':4}}}})
 rows=[['Migração R53','Em andamento','Backup nativo','https://docs.google.com/spreadsheets/d/15TBWm6zotvMyTISr9zAlccM42JAvpdW2Wb82WXgl5QY/edit'],['Cartão','Classe','Campos anteriores em JSON','Tratamento']]+ledger
 prep.append({'updateCells':{'start':{'sheetId':53018006,'rowIndex':0,'columnIndex':0},'rows':[{'values':[{'userEnteredValue':native_value(v)} for v in row]} for row in rows],'fields':'userEnteredValue'}})
 phase('00-preparar',prep)
 for name in NAMES:
  sid=sheets[name]['properties']['sheetId'];a=tabs[name];grid=sheets[name]['properties']['gridProperties'];rg={'sheetId':sid,'startRowIndex':0,'endRowIndex':max(a['linhas'],grid['rowCount']),'startColumnIndex':0,'endColumnIndex':a['colunas']}
  requests=[]
  if name=='MONTAGENS':requests.append({'unmergeCells':{'range':rg}})
  requests.append({'repeatCell':{'range':rg,'cell':{},'fields':'userEnteredValue,dataValidation'}})
  byrow=defaultdict(dict)
  for r,c,v,*_ in values[name]:byrow[r][c]=v
  block=[];first=None;last=None;size=0
  def flush():
   nonlocal block,first,last,size
   if block:requests.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':first-1,'columnIndex':0},'rows':block,'fields':'userEnteredValue'}})
   block=[];first=last=None;size=0
  for r,cols in sorted(byrow.items()):
   row={'values':[{'userEnteredValue':native_value(cols[c])} if c in cols else {} for c in range(1,max(cols)+1)]};n=len(json.dumps(row,ensure_ascii=False))
   if block and (r!=last+1 or size+n>200000):flush()
   if first is None:first=r
   block.append(row);last=r;size+=n
  flush()
  for ra,c1,rb,c2 in copies[name]:requests.append({'copyPaste':{'source':{'sheetId':sid,'startRowIndex':ra-1,'endRowIndex':ra,'startColumnIndex':c1-1,'endColumnIndex':c2},'destination':{'sheetId':sid,'startRowIndex':ra,'endRowIndex':rb,'startColumnIndex':c1-1,'endColumnIndex':c2},'pasteType':'PASTE_FORMULA','pasteOrientation':'NORMAL'}})
  phase(name,requests)
 out=ROOT/'r53/saidas/tabelas-integral';out.mkdir(exist_ok=True);manifest=[]
 for name,reqs in phases:
  batch=[];size=0
  def save():
   p=out/(str(len(manifest)).zfill(3)+'.json');raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p.write_text(raw);manifest.append(dict(arquivo=str(p),fase=name,pedidos=len(batch),caracteres=len(raw),sha256=hashlib.sha256(raw.encode()).hexdigest()))
  for req in reqs:
   n=len(json.dumps(req,ensure_ascii=False))
   if batch and size+n>450000:save();batch=[];size=0
   batch.append(req);size+=n
  if batch:save()
 report=dict(lotes=manifest,versoes_preservadas=kept,transporte_reconstruido=roundtrips,backup='15TBWm6zotvMyTISr9zAlccM42JAvpdW2Wb82WXgl5QY',autorizacao_adicional=False)
 (out/'manifesto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='lotes'},ensure_ascii=False));print('lotes',len(manifest),'caracteres',sum(x['caracteres'] for x in manifest))
if __name__=='__main__':main()
