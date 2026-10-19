"""Plano incremental, reversível por backup nativo; não reconstrói a ficha.

Usa snapshot atual de entradas e versões. A aplicação é externa e sequencial.
"""
import copy,json,sys,re,hashlib
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'capacidade-b47'),str(ROOT/'ficha-v01'),str(ROOT/'r53')]
from lotes import format_,pt
from preparar_nativo import native_value
import extensoes_custom as EX
IDS={'FICHA AMALDIÇOADA':543479115,'INVOCAÇÕES':996249592,'DADOS_R53':53018004,'DADOS_R53_CATALOGO':53018001,'MONTAGENS':53018003,'DADOS':198565231,'DADOS_AM':1282281881,'DADOS_INVOC':1590325709,'DADOS_CUSTOM':1439829572,'ANALISE':1944458422,'DADOS_CONFIG':1372383464,'DADOS_CRIACAO':1504397161,'DADOS_PROGRESSAO':472126497,'FICHA':2091222604,'FICHA PESSOAL':994525406,'CARTEIRA':946642491,'DADOS_MELHORIAS':682222867,'DADOS_RESTRICOES':287788271,'DADOS_FORMAS':1617619316,'DADOS_APTIDOES':593061321,'DADOS_TALENTOS':477737645,'DADOS_ENTIDADES':582955243,'DADOS_DANOS':1278004766,'GLOSSÁRIO':1625460345}
def cells(snapshot,field='userEnteredValue'):
 out={}
 for sh in snapshot['sheets']:
  name=sh['properties']['title'];values=out.setdefault(name,{})
  for d in sh.get('data',[]):
   for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
    for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):
     value=cell.get(field,{})
     if value:values[L(c)+str(r)]=next(iter(value.values()))
 return out

def main():
 old=json.loads((ROOT/'r53/saidas/modelo-antes-diretos.json').read_text());new=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=new['r53']
 if not tr.get('direto'):raise ValueError('Modelo ainda não contém a interface direta')
 live=cells(json.loads((ROOT/'r53/saidas/entradas-antes-diretos.json').read_text()))
 effective=cells(json.loads((ROOT/'r53/saidas/entradas-antes-diretos.json').read_text()),'effectiveValue')
 versions={}
 for n in [1,2]:versions.update(cells(json.loads((ROOT/f'r53/saidas/montagens-antes-diretos-{n}.json').read_text()))['MONTAGENS'])
 oldctx={g['id']:g for g in old['r53']['contextos']};tabs={a['nome']:a for a in new['layout']['abas']};oldtabs={a['nome']:a for a in old['layout']['abas']}
 fields={k:i for i,(k,_,_) in enumerate(tr['editor_campos'])}; defaults={k:v[1] for v in tabs['MONTAGENS']['celulas'] for k in []}
 sourceversions={v[0]:v[1] for v in tabs['MONTAGENS']['celulas']}
 def version(g,idx):
  col=idx+2;vals={k:versions.get(L(col)+str(g['editor']+2+i),sourceversions.get(L(col)+str(g['editor']+2+i))) for k,i in fields.items()}
  amounts=defaultdict(int)
  for i in [1,2,3]:
   fn=vals.get('funcao'+str(i));p=vals.get('pontos'+str(i),0)
   if fn in ['Dano','Cura','PV temporários']:amounts[fn]+=p if isinstance(p,(int,float)) else 0
  chosen={vals.get('funcao'+str(i)) for i in [1,2,3]}
  for i,fn in enumerate(['Dano','Cura','PV temporários'],1):vals['funcao'+str(i)]=fn if fn in chosen else '';vals['pontos'+str(i)]=amounts[fn]
  return vals
 def nativegrid(owner,a1):
  c,r,cc,rr=range_boundaries(a1);return dict(sheetId=IDS[owner],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
 phases=[]
 def phase(name,req):
  if req:phases.append((name,req))
 req=[]
 for owner,inserts in tr['insercoes_diretas'].items():
  for at,num in reversed(inserts):req.append({'insertDimension':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':at-1,'endIndex':at-1+num},'inheritFromBefore':True}})
 phase('01-inserir',req)
 # Describe the state after Sheets' own reference adjustment.
 original=EX.INSERCOES
 try:
  EX.INSERCOES=tr['insercoes_diretas'];EX.formula.cache_clear();EX.deslocar(old['layout'])
 finally:EX.INSERCOES=original;EX.formula.cache_clear()
 before={a['nome']:{v[0]:v for v in a['celulas']} for a in old['layout']['abas']};after={a['nome']:{v[0]:copy.deepcopy(v) for v in a['celulas']} for a in new['layout']['abas']}
 def moved(owner,pos):
  r,c=coordinate_to_tuple(pos);r+=sum(n for at,n in tr['insercoes_diretas'].get(owner,[]) if r>=at);return L(c)+str(r)
 # Preserve every user-supplied name/description/Class, even inside new regions.
 for g in tr['contextos']:
  oldg=oldctx[g['id']];owner=g['aba']
  for key in ['nome','como','classe']:
   if key in oldg['cel'] and key in g['cel']:
    pos=oldg['cel'][key]
    if key=='como' and g['modo']=='Técnica Máxima':
     rr,cc=coordinate_to_tuple(pos);pos=L(cc)+str(rr+1)
    value=live.get(owner,{}).get(pos)
    if value is not None:after[owner][g['cel'][key]][1]=value
  rawclass=live.get(owner,{}).get(oldg['cel'].get('classe'),g['classes'][0]);rawclass=int(rawclass) if isinstance(rawclass,str) and rawclass.isdigit() else rawclass;idx=0 if len(g['classes'])==1 else g['classes'].index(rawclass)
  vals=version(g,idx)
  # Class maximum is not used to locate the single-column Máxima version.
  amparo=effective['DADOS_R53_CATALOGO'].get(L(24+(g['entidade']+1 if g.get('entidade') is not None else 0))+'10','Fechada')
  def allowed(key):
   if key=='dano':return True
   if g['portas'].get(key)=='FALSE':return False
   if g['classes'][0]==0 and rawclass==0:return False
   return amparo!='Fechada'
  for key,pos in g['entradas_diretas'].items():
   if key.startswith('usar_'):
    fn=key[5:];n=['dano','cura','vt'].index(fn)+1;value=vals['funcao'+str(n)]==['Dano','Cura','PV temporários'][n-1]
    if not allowed(fn):value='—'
   elif key.startswith('pontos'):
    value=vals[key];fn=['dano','cura','vt'][int(key[-1])-1]
    if not allowed(fn):value='—'
   else:value=vals[key]
   after[owner][pos][1]=value
  # Keep the storage canonical, leaving every non-interface field intact.
  for ci in range(len(g['classes'])):
   normalized=version(g,ci)
   if ci==idx and after[owner][g['cel']['nome']][1]:normalized['preparada']=True
   for key in fields:
    p=L(ci+2)+str(g['editor']+2+fields[key]);after['MONTAGENS'][p][1]=normalized[key]
 # Only modified merges, not a rebuild of either sheet.
 req=[];merges=[]
 for owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
  prior=set(oldtabs[owner]['mescladas']);future=set(tabs[owner]['mescladas'])
  for a1 in sorted(prior-future):req.append({'unmergeCells':{'range':nativegrid(owner,a1)}})
  for a1 in sorted(future-prior):merges.append({'mergeCells':{'range':nativegrid(owner,a1),'mergeType':'MERGE_ALL'}})
 phase('02-desmesclar',req)
 areas=defaultdict(list)
 for area in tr['areas_diretas']:areas[area['aba']].append(range_boundaries(area['faixa']))
 def inarea(owner,p):
  r,c=coordinate_to_tuple(p);return any(a<=c<=cc and b<=r<=rr for a,b,cc,rr in areas.get(owner,[]))
 # Group adjacent cells on each row, preserving all untouched fields.
 req=[];inputset={(g['aba'],p) for g in tr['contextos'] for p in g['entradas_diretas'].values()}
 for owner,cm in after.items():
  if owner not in IDS:continue
  rows=defaultdict(dict)
  for p,item in cm.items():
   value=item[1];prev=before.get(owner,{}).get(p)
   style=inarea(owner,p)
   if not style and (owner,p) not in inputset:
    if owner=='MONTAGENS':
     if versions.get(p,sourceversions.get(p))==value:continue
    elif prev is not None and prev[1]==value:continue
    if owner=='MONTAGENS' and versions.get(p,sourceversions.get(p))==value:continue
    if owner!='MONTAGENS' and (not isinstance(value,str) or not value.startswith('=')) and not(owner=='FICHA AMALDIÇOADA' and p in ['P322','Q322']):continue
   # Do not clear private input cells unless explicitly part of this card edit.
   cell={'userEnteredValue':({'stringValue':value} if owner=='MONTAGENS' and isinstance(value,str) and not(isinstance(prev[1] if prev else None,str) and str(prev[1]).startswith('=')) else native_value(value))}
   if style:
    ink=new['layout']['estilos'][item[2]];cell['userEnteredFormat']=format_(ink)
    if ink[4] and ink[4]!='General':cell['userEnteredFormat']['numberFormat']={'type':'NUMBER','pattern':ink[4]}
   if owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
    cell['note']=tabs[owner].get('notas',{}).get(p,'');cell['dataValidation']=None
   r,c=coordinate_to_tuple(p);rows[r][c]=cell
  fields_out='userEnteredValue'
  if owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:fields_out+=',userEnteredFormat,note,dataValidation'
  # Format mask only where an authored style exists; elsewhere retain native ink.
  for r,cols in sorted(rows.items()):
   groups=[];group=[]
   for c in sorted(cols):
    key='userEnteredFormat' in cols[c]
    if group and (c!=group[-1]+1 or key!=('userEnteredFormat' in cols[group[-1]])):groups.append(group);group=[]
    group.append(c)
   if group:groups.append(group)
   for cs in groups:
    mask=fields_out if 'userEnteredFormat' in cols[cs[0]] else fields_out.replace(',userEnteredFormat','')
    req.append({'updateCells':{'start':{'sheetId':IDS[owner],'rowIndex':r-1,'columnIndex':cs[0]-1},'rows':[{'values':[cols[c] for c in cs]}],'fields':mask}})
 phase('03-celulas',req);phase('04-mesclar',merges)
 # Restore direct controls with dynamic family gates; no panel inputs survive.
 req=[]
 for g in tr['contextos']:
  for key,menu in g['menus_diretos'].items():
   p=menu['onde'];f=menu['formula'];value=after[g['aba']][p][1]
   if value=='—':rule={'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':'—'}]},'strict':True,'showCustomUi':False} if g['fixa'] else {'condition':{'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':'='+pt(f)}]},'strict':True,'showCustomUi':False}
   elif menu['tipo']=='bool':rule={'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}
   elif menu['tipo']=='custom':rule={'condition':{'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':'='+pt(f)}]},'strict':True,'showCustomUi':False}
   else:
    kind='ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE';vs=[{'userEnteredValue':v} for v in f[1:-1].split(',')] if kind=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f)}]
    rule={'condition':{'type':kind,'values':vs},'strict':True,'showCustomUi':True}
   req.append({'setDataValidation':{'range':nativegrid(g['aba'],p),'rule':rule}})
 phase('05-validacoes',req)
 req=[]
 for owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
  oldheight=dict(oldtabs[owner]['linhas_alt']);newheight=dict(tabs[owner]['linhas_alt'])
  for row,height in newheight.items():
   if oldheight.get(row)!=height:req.append({'updateDimensionProperties':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':row-1,'endIndex':row},'properties':{'pixelSize':round(height*4/3)},'fields':'pixelSize'}})
 # Remove the obsolete hidden side-panel contents, keeping unused columns hidden.
 for owner,panel in old['r53']['paineis'].items():
  start=panel['coluna'];req.append({'repeatCell':{'range':nativegrid(owner,f'{L(start)}4:{L(start+7)}{panel["fim"]}'),'cell':{},'fields':'userEnteredValue,note,dataValidation,userEnteredFormat'}})
 req.append({'repeatCell':{'range':nativegrid('DADOS_R53','A253:C254'),'cell':{},'fields':'userEnteredValue'}})
 for g in tr['contextos']:
  for key in ['nome','como']:
   pos=g['cel'].get(key)
   if pos and pos in tabs[g['aba']].get('notas',{}):req.append({'repeatCell':{'range':nativegrid(g['aba'],pos),'cell':{'note':tabs[g['aba']]['notas'][pos]},'fields':'note'}})
 phase('06-acabamento',req)
 out=ROOT/'r53/saidas/direto-lotes';out.mkdir(exist_ok=True);manifest=[]
 for phase_name,reqs in phases:
  batch=[];size=0
  def save():
   raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p=out/(str(len(manifest)).zfill(3)+'.json');p.write_text(raw)
   manifest.append(dict(arquivo=str(p),fase=phase_name,pedidos=len(batch),bytes=len(raw.encode()),sha256=hashlib.sha256(raw.encode()).hexdigest()))
  for req in reqs:
   n=len(json.dumps(req,ensure_ascii=False))
   if batch and (size+n>330000 or len(batch)>=250):save();batch=[];size=0
   batch.append(req);size+=n
  if batch:save()
 (out/'manifesto.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
 print(json.dumps({'lotes':len(manifest),'pedidos':sum(v['pedidos'] for v in manifest),'por_fase':{name:len(reqs) for name,reqs in phases}},ensure_ascii=False))
if __name__=='__main__':main()
