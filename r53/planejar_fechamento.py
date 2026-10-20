"""Migração incremental da configuração de Formas e notas R53.
Não insere linhas, não reconstrói a ficha e não envia nada ao Google.
Preserva entradas por identidade (vaga/campo), inclusive campos aposentados.
"""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'capacidade-b47'),str(ROOT/'r53')]
from lotes import format_,pt
from preparar_nativo import native_value
from migrar_cartoes_diretos import IDS
IDS['CONFIGURAÇÃO']=1364162823

def read(path):return json.loads(Path(path).read_text())
def live_cells(s):
 out=defaultdict(dict)
 for sh in s['sheets']:
  for d in sh.get('data',[]):
   for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
    for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):out[sh['properties']['title']][L(c)+str(r)]=cell
 return out

def plan(snapshot,out):
 old=read(ROOT/'r53/saidas/antes-fechamento-config/modelo-r53.json');new=read(ROOT/'r53/saidas/modelo-r53.json')
 ot={a['nome']:a for a in old['layout']['abas']};nt={a['nome']:a for a in new['layout']['abas']}
 before={k:{v[0]:v for v in a['celulas']} for k,a in ot.items()};after={k:{v[0]:copy.deepcopy(v) for v in a['celulas']} for k,a in nt.items()}
 live=live_cells(snapshot);mapped={};proof=[]
 def ref(formula):
  m=re.search(r"(?:'([^']+)'|([A-Z_ÇÃ ]+))!\$?([A-Z]+)\$?(\d+)",str(formula));assert m,formula
  return m[1] or m[2],m[3]+m[4]
 fields={coordinate_to_tuple(p)[1]:v[1][8:] for p,v in before['DADOS_FORMAS'].items() if coordinate_to_tuple(p)[0]==1 and isinstance(v[1],str) and v[1].startswith('entrada.')}
 for row in range(2,12):
  for col,field in fields.items():
   p=L(col)+str(row);src,sp=ref(before['DADOS_FORMAS'][p][1]);dst,dp=ref(after['DADOS_FORMAS'][p][1]);assert src=='CONFIGURAÇÃO'
   sr,sc=coordinate_to_tuple(sp);assert 9<=sr<=244 and 156<=sc<=169,('snapshot incompleto',sp)
   value=copy.deepcopy(live[src].get(sp,{}).get('userEnteredValue',{}));mapped[(dst,dp)]=value
   proof.append(dict(vaga=row-1,campo=field,origem=sp,destino=dst+'!'+dp,valor=value))
 headers=[coordinate_to_tuple(p) for p,v in after['CONFIGURAÇÃO'].items() if isinstance(v[1],str) and v[1].startswith('FORMAS · ')]
 assert len(headers)==10
 areas=[(r,c,r+45,c+5) for r,c in headers]
 def inside(p):
  r,c=coordinate_to_tuple(p);return any(y<=r<=yy and x<=c<=xx for y,x,yy,xx in areas)
 def grid(owner,p):
  c,r,cc,rr=range_boundaries(p);return dict(sheetId=IDS[owner],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
 phases=[]
 def add(name,req):
  if req:phases.append((name,req))
 req=[]
 for a1 in sorted(set(ot['CONFIGURAÇÃO']['mescladas'])-set(nt['CONFIGURAÇÃO']['mescladas'])):
  assert inside(a1.split(':')[0]);req.append({'unmergeCells':{'range':grid('CONFIGURAÇÃO',a1)}})
 add('desmesclar',req);req=[]
 for y,x,yy,xx in areas:
  req.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',f'{L(x)}{y}:{L(xx)}{yy}'),'cell':{},'fields':'userEnteredValue,note,dataValidation,userEnteredFormat'}})
 add('limpar-moldes',req)
 req=[];counts=defaultdict(int)
 for owner,cm in after.items():
  if owner not in IDS:continue
  rows=defaultdict(dict)
  for p in cm.keys()|before[owner].keys():
   item=cm.get(p);prev=before[owner].get(p);area=owner=='CONFIGURAÇÃO' and inside(p);override=(owner,p) in mapped
   if not area and not override and (item[1] if item else None)==(prev[1] if prev else None):continue
   if owner=='CONFIGURAÇÃO' and not area and not override:
    assert item and isinstance(item[1],str) and 'Forma define' in item[1],('mudança CONFIG fora de escopo',p)
   cell={'userEnteredValue':mapped[(owner,p)] if override else native_value(item[1] if item else None)}
   if area:
    cell['note']=nt[owner].get('notas',{}).get(p,'');cell['userEnteredFormat']=format_(new['layout']['estilos'][item[2]]) if item and item[2] is not None else {}
   r,c=coordinate_to_tuple(p);rows[r][c]=cell;counts[owner]+=1
  for r,cols in sorted(rows.items()):
   groups=[];g=[]
   for c in sorted(cols):
    if g and (c!=g[-1]+1 or ('userEnteredFormat'in cols[c])!=('userEnteredFormat'in cols[g[-1]])):groups.append(g);g=[]
    g.append(c)
   if g:groups.append(g)
   for cs in groups:
    mask='userEnteredValue'+(',userEnteredFormat,note' if 'userEnteredFormat'in cols[cs[0]] else '')
    req.append({'updateCells':{'start':{'sheetId':IDS[owner],'rowIndex':r-1,'columnIndex':cs[0]-1},'rows':[{'values':[cols[c] for c in cs]}],'fields':mask}})
 add('valores',req);req=[]
 for a1 in sorted(set(nt['CONFIGURAÇÃO']['mescladas'])-set(ot['CONFIGURAÇÃO']['mescladas'])):req.append({'mergeCells':{'range':grid('CONFIGURAÇÃO',a1),'mergeType':'MERGE_ALL'}})
 # Unchanged merges also lost their ink when the card rectangles were cleared.
 for a1 in nt['CONFIGURAÇÃO']['mescladas']:
  p=a1.split(':')[0]
  if inside(p):
   item=after['CONFIGURAÇÃO'].get(p)
   if item and item[2] is not None:req.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',a1),'cell':{'userEnteredFormat':format_(new['layout']['estilos'][item[2]])},'fields':'userEnteredFormat'}})
 add('mesclar-e-bordas',req);req=[]
 for owner,a in nt.items():
  if owner not in IDS:continue
  prior={m['onde']:m for m in ot[owner].get('menus',[])};future={m['onde']:m for m in a.get('menus',[])}
  for p in prior.keys()-future.keys():
   for region in p.split():req.append({'setDataValidation':{'range':grid(owner,region)}})
  for p,m in future.items():
   if prior.get(p)==m and not(owner=='CONFIGURAÇÃO' and inside(p.split(':')[0])):continue
   f=m['formula'];kind='BOOLEAN' if m['tipo']=='bool' else 'CUSTOM_FORMULA' if m['tipo']=='custom' else 'ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE'
   cond={'type':kind}
   if kind!='BOOLEAN':cond['values']=[{'userEnteredValue':v} for v in f[1:-1].split(',')] if kind=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f.lstrip('='))}]
   for region in p.split():req.append({'setDataValidation':{'range':grid(owner,region),'rule':{'condition':cond,'strict':m.get('estrito',True),'showCustomUi':m.get('mostra_seta',True)}}})
 for p,item in after['CONFIGURAÇÃO'].items():
  if inside(p) and type(item[1]) is bool:req.append({'setDataValidation':{'range':grid('CONFIGURAÇÃO',p),'rule':{'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}}})
 add('menus',req);req=[]
 for owner,a in nt.items():
  if owner not in IDS:continue
  prior=ot[owner].get('notas',{});future=a.get('notas',{})
  for p in prior.keys()|future.keys():
   if prior.get(p)==future.get(p) or(owner=='CONFIGURAÇÃO' and inside(p)):continue
   req.append({'repeatCell':{'range':grid(owner,p),'cell':{'note':future.get(p,'')},'fields':'note'}})
 add('notas',req)
 out=Path(out);out.mkdir(parents=True,exist_ok=True);manifest=[]
 for phase,reqs in phases:
  batch=[];size=0
  def save():
   raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p=out/f'{len(manifest):03d}.json';p.write_text(raw);manifest.append(dict(arquivo=str(p),fase=phase,pedidos=len(batch),sha256=hashlib.sha256(raw.encode()).hexdigest()))
  for req in reqs:
   length=len(json.dumps(req,ensure_ascii=False))
   if batch and(size+length>600000 or len(batch)>=500):save();batch=[];size=0
   batch.append(req);size+=length
  if batch:save()
 result=dict(destino=snapshot['spreadsheetId'],backup='1bt_oVOW0VD6riBZp0l9XyHVNicYEiFivEjUu71HkjhE',entradas=proof,celulas=dict(counts),lotes=manifest,sem_insercoes=True,modelo_sha256=hashlib.sha256((ROOT/'r53/saidas/modelo-r53.json').read_bytes()).hexdigest())
 (out/'manifesto.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['entradas','lotes']}|{'lotes':len(manifest),'pedidos':sum(x['pedidos'] for x in manifest),'entradas':len(proof)},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('snapshot');ap.add_argument('out');a=ap.parse_args();plan(read(a.snapshot),a.out)
