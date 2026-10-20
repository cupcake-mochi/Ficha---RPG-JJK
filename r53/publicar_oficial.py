"""Planeja a promoção incremental B47 -> R53 a partir de snapshots nativos.
Não envia pedidos. Conserva o documento, as imagens e o seletor de paleta.
Não usa construir/continuar nem importa uma planilha de outro formato.
"""
import json,sys,copy,hashlib
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'r53/saidas/publicacao'
sys.path[:0]=[str(ROOT/'capacidade-b47'),str(ROOT/'ficha-v01'),str(ROOT/'r53')]
from lotes import format_,pt
from preparar_nativo import native_value as base_native_value
from migrar_cartoes_diretos import IDS
import extensoes_custom as EX
from openpyxl.formula.translate import Translator
IDS['CONFIGURAÇÃO']=1364162823

def idioma(formula,nativo=True):
 out=[];quoted=False;paren=0;arrays=[];i=0
 while i<len(formula):
  ch=formula[i]
  if ch=='"':
   if quoted and formula[i+1:i+2]=='"':out.extend(['"','"']);i+=2;continue
   quoted=not quoted
  if not quoted:
   if ch=='(':paren+=1
   elif ch==')':paren-=1
   elif ch=='{':arrays.append(paren)
   elif ch=='}':arrays.pop()
   inarray=bool(arrays and arrays[-1]==paren)
   if nativo:
    if ch==',':ch='\\' if inarray else ';'
    elif ch=='.' and formula[i-1:i].isdigit() and formula[i+1:i+2].isdigit():ch=','
   else:
    if ch==';' and not inarray:ch=','
    elif ch=='\\':ch=','
    elif ch==',' and formula[i-1:i].isdigit() and formula[i+1:i+2].isdigit():ch='.'
  out.append(ch);i+=1
 return ''.join(out)
def native_value(v):
 result=base_native_value(v)
 if isinstance(v,str) and v.startswith('='):result['formulaValue']=idioma(v)
 return result

def read(p):return json.loads(Path(p).read_text())
def snapshots():
 out=defaultdict(dict)
 for path in [OUT/'oficial-visiveis-antes.json']+sorted(OUT.glob('tecnica-*.json')):
  for sh in read(path)['sheets']:
   for d in sh.get('data',[]):
    for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
     for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):
      if cell.get('userEnteredValue'):out[sh['properties']['title']][L(c)+str(r)]=cell['userEnteredValue']
 return out

def main():
 model=read(ROOT/'r53/saidas/modelo-r53.json');tabs={a['nome']:a for a in model['layout']['abas']};meta=read(OUT/'oficial-metadados-antes.json');sheets={a['properties']['title']:a for a in meta['sheets']};live=snapshots();tr=model['r53'];before=copy.deepcopy(live)
 assert len(sheets)==22 and set(tabs)-set(sheets)=={'MONTAGENS','DADOS_R53','DADOS_R53_CATALOGO'}
 inserts=tr['insercoes_diretas'];oldins=EX.INSERCOES;EX.INSERCOES=inserts;EX.formula.cache_clear()
 def move(owner,pos):
  r,c=coordinate_to_tuple(pos);return L(c)+str(r+sum(n for at,n in inserts.get(owner,[]) if r>=at))
 for owner,cm in list(live.items()):live[owner]={move(owner,p):({'formulaValue':idioma(EX.formula(idioma(v['formulaValue'],False),owner))} if 'formulaValue'in v else v)for p,v in cm.items()}
 # Grounded column formatting exemplars carry the existing official palette.
 old=read(ROOT/'r53/saidas/base-b47-final.json');ot={a['nome']:a for a in old['layout']['abas']};palette={}
 fmt=read(OUT/'oficial-formatos-antes.json')
 def hex_(rgb):return '#'+''.join(f'{round(rgb.get(k,0)*255):02X}'for k in ['red','green','blue'])
 for sh in fmt['sheets']:
  owner=sh['properties']['title']
  if owner not in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:continue
  palette[owner]={};oldcells={v[0]:v for v in ot[owner]['celulas']}
  for d in sh['data']:
   for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
    for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):
     style=old['layout']['estilos'][oldcells[L(c)+str(r)][2]];native=cell['userEnteredFormat'];mapping=palette[owner]
     if style[1]:mapping[style[1].upper()]=hex_(native['backgroundColor'])
     if style[0]:mapping[style[0][2].upper()]=hex_(native['textFormat']['foregroundColor'])
     for side,edge in (style[2]or{}).items():
      if side in native.get('borders',{}):mapping[edge[1].upper()]=hex_(native['borders'][side]['color'])
 texts_by_background={}
 for sh in read(OUT/'paleta-completa-oficial.json')['sheets']:
  owner=sh['properties']['title'];oldcells={v[0]:v for v in ot[owner]['celulas']};texts_by_background[owner]={}
  for d in sh.get('data',[]):
   for row,rr in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
    for col,cell in enumerate(rr.get('values',[]),d.get('startColumn',0)+1):
     item=oldcells.get(L(col)+str(row));native=cell.get('userEnteredFormat',{})
     if not item or item[2]is None or 'backgroundColor'not in native:continue
     style=old['layout']['estilos'][item[2]];bg=style[1]
     if not bg:continue
     palette[owner][bg.upper()]=hex_(native['backgroundColor'])
     fg=native.get('textFormat',{}).get('foregroundColor')
     if style[0]and fg:texts_by_background[owner].setdefault(bg.upper(),{})[style[0][2].upper()]=hex_(fg)
 def ink(owner,sid):
  style=copy.deepcopy(model['layout']['estilos'][sid]);mp=palette.get(owner,{})
  if style[0]:style[0][2]=texts_by_background.get(owner,{}).get((style[1]or'').upper(),{}).get(style[0][2].upper(),mp.get(style[0][2].upper(),style[0][2]))
  if style[1]:style[1]=mp.get(style[1].upper(),style[1])
  if style[2]:
   for side,edge in style[2].items():edge[1]=mp.get(edge[1].upper(),edge[1])
  result=format_(style)
  if style[4] and style[4]!='General':result['numberFormat']={'type':'NUMBER','pattern':style[4]}
  return result
 def grid(owner,p):
  c,r,cc,rr=range_boundaries(p);return dict(sheetId=IDS[owner],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
 def shifted_grid(owner,rg):
  q=copy.deepcopy(rg)
  for field,plus in [('startRowIndex',1),('endRowIndex',0)]:
   r=q.get(field,0)+plus;q[field]=r+sum(n for at,n in inserts.get(owner,[])if r>=at)-plus
  return q
 def addr(rg):return f"{L(rg.get('startColumnIndex',0)+1)}{rg.get('startRowIndex',0)+1}:{L(rg['endColumnIndex'])}{rg['endRowIndex']}"
 areas=defaultdict(list)
 for g in tr['contextos']:areas[g['aba']].append(g['area_editor'])
 cfg=tabs['CONFIGURAÇÃO'];headers=[coordinate_to_tuple(v[0])for v in cfg['celulas']if isinstance(v[1],str)and v[1].startswith('FORMAS · ')]
 areas['CONFIGURAÇÃO']=[(r,c,r+45,c+5)for r,c in headers]
 def owned(owner,p):
  r,c=coordinate_to_tuple(p);return any(y<=r<=yy and x<=c<=xx for y,x,yy,xx in areas.get(owner,[]))
 phases=[]
 def add(name,rs):
  if rs:phases.append((name,rs))
 req=[]
 for owner,entries in inserts.items():
  for at,n in reversed(entries):req.append({'insertDimension':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':at-1,'endIndex':at-1+n},'inheritFromBefore':True}})
 for owner,tab in tabs.items():
  if owner not in sheets:req.append({'addSheet':{'properties':{'sheetId':IDS[owner],'title':owner,'hidden':True,'gridProperties':{'rowCount':tab['linhas'],'columnCount':tab['colunas'],'hideGridlines':True}}}})
  else:
   gp=sheets[owner]['properties']['gridProperties'];afterrows=gp['rowCount']+sum(n for _,n in inserts.get(owner,[]));grow={}
   if tab['linhas']>afterrows:grow['rowCount']=tab['linhas']
   if tab['colunas']>gp['columnCount']:grow['columnCount']=tab['colunas']
   if grow:req.append({'updateSheetProperties':{'properties':{'sheetId':IDS[owner],'gridProperties':grow},'fields':','.join('gridProperties.'+k for k in grow)}})
 add('01-grade',req);req=[];newmerges=[]
 for owner in areas:
  actual={addr(shifted_grid(owner,m)):shifted_grid(owner,m)for m in sheets[owner].get('merges',[])if owned(owner,addr(shifted_grid(owner,m)).split(':')[0])}
  future={a1 for a1 in tabs[owner]['mescladas']if owned(owner,a1.split(':')[0])}
  for a1 in actual.keys()-future:req.append({'unmergeCells':{'range':actual[a1]}})
  for a1 in future-actual.keys():newmerges.append({'mergeCells':{'range':grid(owner,a1),'mergeType':'MERGE_ALL'}})
 add('02-desmesclar',req);req=[];counts=defaultdict(int)
 expected={};copied=set();formula_copies=[]
 for owner,tab in tabs.items():
  if tab.get('estado')!='hidden':continue
  cols=defaultdict(list)
  for pos,value,*_ in tab['celulas']:
   if isinstance(value,str)and value.startswith('='):
    r,c=coordinate_to_tuple(pos)
    try:normal=Translator(value,origin=pos).translate_formula(L(c)+'1')
    except Exception:continue
    cols[c].append((r,pos,value,normal))
  for c,entries in cols.items():
   groups=[];g=[]
   for entry in sorted(entries):
    if g and(entry[0]!=g[-1][0]+1 or entry[3]!=g[-1][3]):groups.append(g);g=[]
    g.append(entry)
   if g:groups.append(g)
   for group in groups:
    if len(group)<3 or sum(len(x[2])for x in group)<2000:continue
    first=group[0]
    for row,pos,value,_ in group[1:]:
     assert Translator(first[2],origin=first[1]).translate_formula(pos)==value
     copied.add((owner,pos));expected[owner+'!'+pos]=native_value(value)
    formula_copies.append({'copyPaste':{'source':grid(owner,first[1]),'destination':grid(owner,L(c)+str(first[0]+1)+':'+L(c)+str(group[-1][0])),'pasteType':'PASTE_FORMULA'}})
 # Only a known typing exercise is removed; every other native literal which
 # differs from the base is preserved unless it is an authored label in scope.
 assert before['FICHA AMALDIÇOADA'].get('E64',{}).get('stringValue')=='fsda'
 for owner,tab in tabs.items():
  current=live.get(owner,{});target={v[0]:v for v in tab['celulas']};rows=defaultdict(dict)
  for p in current.keys()|target.keys():
   if(owner,p)in copied:continue
   item=target.get(p);is_owned=owned(owner,p);prev=current.get(p,{})
   if item is None:
    if not is_owned:continue
    desired={}
   else:desired=native_value(item[1])
   if not is_owned and not tab.get('estado')=='hidden' and item is not None and item[1] is None and prev and 'formulaValue'not in prev:desired=prev
   # Native palette controls are not authored by the cell generator.
   if owner=='CARTEIRA'and p in current and p not in target:continue
   if desired==prev and not is_owned:continue
   cell={'userEnteredValue':desired}
   if is_owned:
    cell.update(userEnteredFormat=ink(owner,item[2])if item and item[2] is not None else {},note=tab.get('notas',{}).get(p,''),dataValidation=None)
   r,c=coordinate_to_tuple(p);rows[r][c]=cell;counts[owner]+=1;expected[owner+'!'+p]=desired
  # Fuse identical column spans on adjacent rows into bounded native blocks.
  chunks=[]
  for r,cols in sorted(rows.items()):
   groups=[];g=[]
   for c in sorted(cols):
    if g and(c!=g[-1]+1 or ('userEnteredFormat'in cols[c])!=('userEnteredFormat'in cols[g[-1]])):groups.append(g);g=[]
    g.append(c)
   if g:groups.append(g)
   for cs in groups:chunks.append((r,cs[0],cs[-1],{'values':[cols[c]for c in cs]},'userEnteredValue'+(',userEnteredFormat,note,dataValidation'if'userEnteredFormat'in cols[cs[0]]else'')))
  active=None;size=0
  for r,c,cc,row,mask in chunks:
   length=len(json.dumps(row,ensure_ascii=False))
   if active and(active['last']+1!=r or active['c']!=c or active['cc']!=cc or active['mask']!=mask or size+length>400000):
    req.append(active['request']);active=None
   if not active:
    active=dict(last=r,c=c,cc=cc,mask=mask,request={'updateCells':{'start':{'sheetId':IDS[owner],'rowIndex':r-1,'columnIndex':c-1},'rows':[],'fields':mask}});size=0
   active['request']['updateCells']['rows'].append(row);active['last']=r;size+=length
  if active:req.append(active['request'])
 add('03-celulas',req);add('03b-formulas-relativas',formula_copies);add('04-mesclar',newmerges);req=[]
 # Restore full merged ink, including continuous perimeter borders.
 for owner in areas:
  cells={v[0]:v for v in tabs[owner]['celulas']}
  for a1 in tabs[owner]['mescladas']:
   p=a1.split(':')[0];item=cells.get(p)
   if owned(owner,p)and item and item[2]is not None:req.append({'repeatCell':{'range':grid(owner,a1),'cell':{'userEnteredFormat':ink(owner,item[2])},'fields':'userEnteredFormat'}})
 add('05-bordas',req);req=[]
 for owner,tab in tabs.items():
  for m in tab.get('menus',[]):
   f=m['formula'];kind='BOOLEAN'if m['tipo']=='bool'else'CUSTOM_FORMULA'if m['tipo']=='custom'else'ONE_OF_LIST'if f.startswith('"')else'ONE_OF_RANGE';cond={'type':kind}
   if kind!='BOOLEAN':cond['values']=[{'userEnteredValue':x}for x in f[1:-1].split(',')]if kind=='ONE_OF_LIST'else[{'userEnteredValue':idioma('='+f.lstrip('='))}]
   for region in m['onde'].split():req.append({'setDataValidation':{'range':grid(owner,region),'rule':{'condition':cond,'strict':m.get('estrito',True),'showCustomUi':m.get('mostra_seta',True)}}})
  for p,v,*_ in tab['celulas']:
   if type(v)is bool and owned(owner,p):req.append({'setDataValidation':{'range':grid(owner,p),'rule':{'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}}})
  for p,note in tab.get('notas',{}).items():
   if not owned(owner,p) and ot.get(owner,{}).get('notas',{}).get(p)!=note:req.append({'repeatCell':{'range':grid(owner,p),'cell':{'note':note},'fields':'note'}})
 add('06-menus-notas',req);req=[]
 for owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
  for group in sorted(sheets[owner].get('rowGroups',[]),key=lambda g:g['depth'],reverse=True):
   rg=group['range'];q=dict(rg)
   for fld,plus in [('startIndex',1),('endIndex',0)]:
    row=q[fld]+plus;q[fld]=row+sum(n for at,n in inserts.get(owner,[])if row>=at-(1 if fld=='endIndex' else 0))-plus
   req.append({'deleteDimensionGroup':{'range':q}})
  for r,rr,closed in tabs[owner]['grupos']['linhas']:
   rg={'sheetId':IDS[owner],'dimension':'ROWS','startIndex':r-1,'endIndex':rr}
   req.append({'addDimensionGroup':{'range':rg}})
  groups=tabs[owner]['grupos']['linhas']
  for r,rr,closed in groups:
   depth=1+sum(a<=r and rr<=b and(a,b)!=(r,rr)for a,b,_ in groups)
   req.append({'updateDimensionGroup':{'dimensionGroup':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':r-1,'endIndex':rr},'depth':depth,'collapsed':bool(closed)},'fields':'collapsed'}})
  # Set visibility from ancestor to descendants; a closed ancestor always wins.
  groups=tabs[owner]['grupos']['linhas']
  req.append({'updateDimensionProperties':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':0,'endIndex':tabs[owner]['linhas']},'properties':{'hiddenByUser':False},'fields':'hiddenByUser'}})
  for r,rr,closed in groups:
   if closed:req.append({'updateDimensionProperties':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':r-1,'endIndex':rr},'properties':{'hiddenByUser':True},'fields':'hiddenByUser'}})
  for r,height in tabs[owner].get('linhas_alt',[]):req.append({'updateDimensionProperties':{'range':{'sheetId':IDS[owner],'dimension':'ROWS','startIndex':r-1,'endIndex':r},'properties':{'pixelSize':round(height*4/3)},'fields':'pixelSize'}})
 add('07-grupos-alturas',req)
 # No removal/recreation of sheets, images, named ranges, palette or permissions.
 path=OUT/'lotes';path.mkdir(exist_ok=True);manifest=[]
 for phase,requests in phases:
  batch=[];size=0
  def save():
   raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p=path/f'{len(manifest):03d}.json';p.write_text(raw);manifest.append(dict(arquivo=str(p),fase=phase,pedidos=len(batch),bytes=len(raw.encode()),sha256=hashlib.sha256(raw.encode()).hexdigest()))
  for request in requests:
   n=len(json.dumps(request,ensure_ascii=False))
   if batch and(size+n>650000 or len(batch)>=400):save();batch=[];size=0
   batch.append(request);size+=n
  if batch:save()
 (OUT/'valores-esperados.json').write_text(json.dumps(expected,ensure_ascii=False))
 proof=dict(abas_antes=22,abas_depois=25,insercoes=120,formulas_copiadas=len(copied),celulas=dict(counts),lotes=manifest,pedidos=sum(x['pedidos']for x in manifest),modelo_sha256=hashlib.sha256((ROOT/'r53/saidas/modelo-r53.json').read_bytes()).hexdigest(),limpeza=['FICHA AMALDIÇOADA!E64: nome fsda retirado'],paleta=palette)
 (OUT/'manifesto.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in ['lotes','paleta']}|{'lotes':len(manifest)},ensure_ascii=False))
 EX.INSERCOES=oldins;EX.formula.cache_clear()
if __name__=='__main__':main()
