"""Delta nativo de cartões e validações; preserva entradas e estilos existentes."""
import json,sys,copy,hashlib
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import range_boundaries,coordinate_to_tuple,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'capacidade-b47'),str(ROOT/'r53')]
from lotes import pt,format_
from preparar_nativo import native_value

def load(p):return json.loads((ROOT/p).read_text())
def val(cell):return cell.get('userEnteredValue',{})
def rg(sid,a1):
 c,r,cc,rr=range_boundaries(a1);return dict(sheetId=sid,startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
def box(m):return m.get('startRowIndex',0)+1,m.get('startColumnIndex',0)+1,m['endRowIndex'],m['endColumnIndex']
def a1(b):r,c,rr,cc=b;return L(c)+str(r)+':'+L(cc)+str(rr)
def inside(a,b):return not(a[0]>b[2] or b[0]>a[2] or a[1]>b[3] or b[1]>a[3])

def main():
 model=load('r53/saidas/modelo-r53.json');tr=model['r53'];tabs={a['nome']:a for a in model['layout']['abas']}
 meta=load('r53/saidas/metadados-antes-integral.json');sheets={a['properties']['title']:a for a in meta['sheets']}
 base=load('r53/saidas/base-b47-final.json');old={a['nome']:{v[0]:v[1] for v in a['celulas']} for a in base['layout']['abas']}
 delta=load('r53/saidas/delta-valores.json');snapshot=defaultdict(dict)
 for p in (ROOT/'r53/saidas/snapshot-integral').glob('*.json'):
  snap=json.loads(p.read_text())
  for s in snap['sheets']:
   for data in s.get('data',[]):
    for y,row in enumerate(data.get('rowData',[]),data.get('startRow',0)+1):
     for x,cell in enumerate(row.get('values',[]),data.get('startColumn',0)+1):snapshot[s['properties']['title']][L(x)+str(y)]=cell
 visible=['FICHA','FICHA AMALDIÇOADA','INVOCAÇÕES','CONFIGURAÇÃO'];phases=defaultdict(list);computed=defaultdict(set);regions=defaultdict(list)
 input_cells=defaultdict(set)
 for g in tr['contextos']:
  computed[g['aba']].update(tr['formulas'][g['id']]);regions[g['aba']].append(g['area_editor'])
  input_cells[g['aba']].update(g['cel'][k] for k in ['nome','como'] if k in g['cel'])
 for name,panel in tr['paineis'].items():regions[name].append([panel['linha'],panel['coluna'],panel['fim'],panel['coluna']+7])
 for name in visible:
  tab=tabs[name];sid=sheets[name]['properties']['sheetId'];grid=sheets[name]['properties']['gridProperties'];grow={}
  if tab['colunas']>grid['columnCount']:grow['columnCount']=tab['colunas']
  if tab['linhas']>grid['rowCount']:grow['rowCount']=tab['linhas']
  if grow:
   phases['00-grade'].append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':grow},'fields':','.join('gridProperties.'+k for k in grow)}})
   # O Sheets estende automaticamente o grupo que termina na última coluna.
   # Repor seu limite original evita englobar o novo painel do editor.
   if 'columnCount' in grow:
    for group in sheets[name].get('columnGroups',[]):
     original=group['range']
     if original['endIndex']!=grid['columnCount']:continue
     extended={**original,'endIndex':grow['columnCount']}
     phases['00-grade'].extend([{'deleteDimensionGroup':{'range':extended}},{'addDimensionGroup':{'range':original}},{'updateDimensionGroup':{'dimensionGroup':{'range':original,'depth':group['depth'],'collapsed':group.get('collapsed',False)},'fields':'collapsed'}}])
  if name not in regions:continue
  owned=lambda b:any(inside(b,r) for r in regions[name])
  current={a1(box(m)):box(m) for m in sheets[name].get('merges',[]) if owned(box(m))}
  desired={m:[range_boundaries(m)[1],range_boundaries(m)[0],range_boundaries(m)[3],range_boundaries(m)[2]] for m in tab['mescladas'] if owned([range_boundaries(m)[1],range_boundaries(m)[0],range_boundaries(m)[3],range_boundaries(m)[2]])}
  for m in current.keys()-desired.keys():phases['01-desmesclar'].append({'unmergeCells':{'range':rg(sid,m)}})
  for m in desired.keys()-current.keys():phases['02-mesclar'].append({'mergeCells':{'range':rg(sid,m),'mergeType':'MERGE_ALL'}})
 # A linha Função precisa ficar fora dos grupos que recolhem a descrição.
 adjusted=set()
 for g in tr['contextos']:
  if 'linha_funcao' not in g:continue
  name=g['aba'];sid=sheets[name]['properties']['sheetId'];r=g['linha_funcao'];first=coordinate_to_tuple(g['cel']['como'])[0]
  for group in sheets[name].get('rowGroups',[]):
   source=group['range'];key=(name,source['startIndex'],source['endIndex'])
   if source['endIndex']!=r or source['startIndex']<first-2 or key in adjusted:continue
   target={**source,'endIndex':r-1};depth=group['depth'];closed=group.get('collapsed',False)
   if target['endIndex']<=target['startIndex']:raise ValueError('Grupo de descrição vazio')
   phases['01-desmesclar'].append({'deleteDimensionGroup':{'range':source}})
   phases['02-mesclar'].extend([{'addDimensionGroup':{'range':target}},{'updateDimensionGroup':{'dimensionGroup':{'range':target,'depth':depth,'collapsed':closed},'fields':'collapsed'}}])
   ancestor=any(other.get('collapsed',False) and other['range']['startIndex']<source['startIndex'] and other['range']['endIndex']>=r for other in sheets[name].get('rowGroups',[]))
   if not ancestor:phases['04-estilos'].append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'ROWS','startIndex':r-1,'endIndex':r},'properties':{'hiddenByUser':False},'fields':'hiddenByUser'}})
   adjusted.add(key)
 preserved=[];changed=defaultdict(dict);named=[];partial=[]
 for g in tr['contextos']:
  cells=snapshot[g['aba']];name=val(cells.get(g['cel']['nome'],{})).get('stringValue','')
  if name:named.append(g['id'])
 for name in visible:
  sid=sheets[name]['properties']['sheetId'];rows=defaultdict(dict)
  for pos,v in delta.get(name,{}).items():
   if pos in input_cells[name]:continue
   cell=snapshot[name].get(pos,{});before=val(cell);after=native_value(v)
   if before==after:continue
   iscomputed=pos in computed[name]
   meaningful=bool(before) and before!={'stringValue':''}
   original=native_value(old.get(name,{}).get(pos))
   # Os valores do jogador prevalecem sobre padrões/etiquetas de fábrica.
   if meaningful and not iscomputed and before!=original and not (name in tr['paineis'] and coordinate_to_tuple(pos)[1]>=tr['paineis'][name]['coluna']):
    preserved.append([name,pos]);continue
   r,c=coordinate_to_tuple(pos);rows[r][c]=(after,iscomputed);changed[name][pos]=v
  for row,values in sorted(rows.items()):
   columns=sorted(values);i=0
   while i<len(columns):
    j=i
    while j+1<len(columns) and columns[j+1]==columns[j]+1 and values[columns[j+1]][1]==values[columns[i]][1]:j+=1
    data=[{'userEnteredValue':values[c][0]} for c in columns[i:j+1]]
    fields='userEnteredValue,dataValidation' if values[columns[i]][1] else 'userEnteredValue'
    phases['03-valores'].append({'updateCells':{'start':{'sheetId':sid,'rowIndex':row-1,'columnIndex':columns[i]-1},'rows':[{'values':data}],'fields':fields}});i=j+1
 # Apenas a nova linha Função e os novos painéis recebem estilos.
 heights=set()
 for g in tr['contextos']:
  name=g['aba'];sid=sheets[name]['properties']['sheetId'];tab=tabs[name];cells={v[0]:v for v in tab['celulas']}
  if 'linha_funcao' not in g:continue
  r=g['linha_funcao'];c=g['coluna'];region=L(c)+str(r)+':'+L(c+4)+str(r)
  for pos in [L(c)+str(r),g['funcao']]:
   value=cells[pos];fmt=format_(model['layout']['estilos'][value[2]])
   merge=next((m for m in tab['mescladas'] if m.split(':')[0]==pos),pos)
   phases['04-estilos'].append({'repeatCell':{'range':rg(sid,merge),'cell':{'userEnteredFormat':fmt,'note':tab.get('notas',{}).get(pos,'')},'fields':'userEnteredFormat,note'}})
  if (name,r) not in heights:phases['04-estilos'].append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'ROWS','startIndex':r-1,'endIndex':r},'properties':{'pixelSize':56},'fields':'pixelSize'}});heights.add((name,r))
 for name,panel in tr['paineis'].items():
  sid=sheets[name]['properties']['sheetId'];tab=tabs[name];c=panel['coluna'];r=panel['linha'];last=panel['fim']
  for pos,v,st,*_ in tab['celulas']:
   rr,cc=coordinate_to_tuple(pos)
   if not(r<=rr<=last and c<=cc<c+8):continue
   phases['04-estilos'].append({'repeatCell':{'range':rg(sid,pos),'cell':{'userEnteredFormat':format_(model['layout']['estilos'][st]),'note':tab.get('notas',{}).get(pos,'')},'fields':'userEnteredFormat,note'}})
  group={'sheetId':sid,'dimension':'COLUMNS','startIndex':c-1,'endIndex':c+7}
  if not any(x['range'].get('startIndex')==c-1 and x['range'].get('endIndex')==c+7 for x in sheets[name].get('columnGroups',[])):phases['06-paineis'].append({'addDimensionGroup':{'range':group}})
  phases['06-paineis'].extend([{'updateDimensionProperties':{'range':group,'properties':{'pixelSize':87,'hiddenByUser':True},'fields':'pixelSize,hiddenByUser'}},{'updateDimensionGroup':{'dimensionGroup':{'range':group,'depth':1,'collapsed':True},'fields':'collapsed'}}])
 for name in visible:
  sid=sheets[name]['properties']['sheetId']
  for menu in tabs[name]['menus']:
   f=menu['formula'];kind='BOOLEAN' if menu['tipo']=='bool' else 'CUSTOM_FORMULA' if menu['tipo']=='custom' else 'ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE';condition={'type':kind}
   if kind!='BOOLEAN':condition['values']=[{'userEnteredValue':x} for x in f[1:-1].split(',')] if kind=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f.lstrip('='))}]
   for part in menu['onde'].split():phases['05-menus'].append({'setDataValidation':{'range':rg(sid,part),'rule':{'condition':condition,'strict':True if kind=='BOOLEAN' else menu.get('estrito',False),'showCustomUi':menu.get('mostra_seta',True) if kind!='BOOLEAN' else True}}})
 out=ROOT/'r53/saidas/cartoes-integral';out.mkdir(exist_ok=True);manifest=[]
 for phase,reqs in sorted(phases.items()):
  batch=[];size=0
  def save():
   p=out/(str(len(manifest)).zfill(3)+'-'+phase+'.json');raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p.write_text(raw);manifest.append(dict(arquivo=str(p),fase=phase,pedidos=len(batch),caracteres=len(raw),sha256=hashlib.sha256(raw.encode()).hexdigest()))
  for req in reqs:
   n=len(json.dumps(req,ensure_ascii=False))
   if batch and (size+n>150000 or len(batch)>=700):save();batch=[];size=0
   batch.append(req);size+=n
  if batch:save()
 summary=dict(lotes=manifest,nomeados=named,preservados=preserved,celulas_alteradas={k:len(v) for k,v in changed.items()},pedidos_por_fase={k:len(v) for k,v in phases.items()})
 (out/'manifesto.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k not in ['lotes','preservados','nomeados']},ensure_ascii=False));print('nomeados',len(named),'entradas preservadas',len(preserved),'lotes',len(manifest))
if __name__=='__main__':main()
