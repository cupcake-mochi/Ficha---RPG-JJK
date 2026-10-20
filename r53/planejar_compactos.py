"""Delta final dos 54 controles Editar; conserva os campos e a paleta vivos."""
import json,copy,sys
from pathlib import Path
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'capacidade-b47')]
from lotes import pt
IDS={'FICHA AMALDIÇOADA':543479115,'INVOCAÇÕES':996249592}

def rg(sid,a1):
 c,r,cc,rr=range_boundaries(a1);return dict(sheetId=sid,startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
def fmt(cell):
 source=cell.get('userEnteredFormat',{});out={k:copy.deepcopy(source[k]) for k in ['backgroundColorStyle','backgroundColor','textFormat','horizontalAlignment','verticalAlignment','wrapStrategy'] if k in source}
 out['borders']={k:{kk:copy.deepcopy(v[kk]) for kk in ['style','colorStyle','color'] if kk in v} for k,v in source.get('borders',{}).items()}
 return out
def value(v):
 if type(v)is bool:return {'boolValue':v}
 if isinstance(v,(int,float)):return {'numberValue':v}
 if isinstance(v,str) and v.startswith('='):return {'formulaValue':pt(v)}
 return {'stringValue':'' if v is None else str(v)}

def main():
 model=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=model['r53'];changes=tr.get('compactos_checkbox',[])
 if len(changes)!=54 or not all(g.get('abrir_editor') for g in tr['contextos']):raise ValueError('Geração dos249controles incompleta')
 snap=json.loads((ROOT/'r53/saidas/compactos-antes-nativo.json').read_text());native={}
 for sh in snap['sheets']:
  dst=native.setdefault(sh['properties']['title'],{})
  for data in sh.get('data',[]):
   for r,row in enumerate(data.get('rowData',[]),data.get('startRow',0)+1):
    for c,cell in enumerate(row.get('values',[]),data.get('startColumn',0)+1):dst[L(c)+str(r)]=cell
 tabs={a['nome']:a for a in model['layout']['abas']};cells={name:{v[0]:v[1] for v in a['celulas']} for name,a in tabs.items()}
 requests=[]
 for ch in changes:
  requests.append({'unmergeCells':{'range':rg(IDS[ch['aba']],ch['antes'])}})
  if ch['header']:requests.append({'unmergeCells':{'range':rg(IDS[ch['aba']],ch['header']['antes'])}})
 for ch in changes:
  name=ch['aba'];sid=IDS[name];row,col=coordinate_to_tuple(ch['checkbox']);cb=ch['checkbox']+':'+L(col)+str(ch['fim'])
  merges=[ch['depois'],cb]+([ch['header']['depois']] if ch['header'] else [])
  for merge in merges:
   c,r,cc,rr=range_boundaries(merge)
   if c!=cc or r!=rr:requests.append({'mergeCells':{'range':rg(sid,merge),'mergeType':'MERGE_ALL'}})
  for pos in [ch['funcao'],ch['checkbox']]+([ch['header']['rotulo'],ch['header']['editar']] if ch['header'] else []):
   r,c=coordinate_to_tuple(pos);requests.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':r-1,'columnIndex':c-1},'rows':[{'values':[{'userEnteredValue':value(cells[name][pos]),'note':tabs[name].get('notas',{}).get(pos,'')}]}],'fields':'userEnteredValue,note'}})
  # O formato Texto transforma o clique da checkbox em "TRUE" literal.
  # Ao substituir o formato completo, omitir numberFormat repõe Geral.
  form=fmt(native[name][ch['funcao']]);form.update(wrapStrategy='WRAP',verticalAlignment='MIDDLE')
  if ch['altura']:form.setdefault('textFormat',{})['fontSize']=9
  requests.append({'repeatCell':{'range':rg(sid,ch['depois']),'cell':{'userEnteredFormat':form},'fields':'userEnteredFormat'}})
  check=copy.deepcopy(form);check['horizontalAlignment']='CENTER'
  requests.append({'repeatCell':{'range':rg(sid,cb),'cell':{'userEnteredFormat':check},'fields':'userEnteredFormat'}})
  requests.append({'setDataValidation':{'range':rg(sid,cb),'rule':{'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}}})
  if ch['header']:
   h=ch['header'];f=fmt(native[name][h['rotulo']])
   for hpos in [h['rotulo'],h['editar']]:requests.append({'repeatCell':{'range':rg(sid,hpos),'cell':{'userEnteredFormat':f},'fields':'userEnteredFormat'}})
  if ch['altura']:requests.append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'ROWS','startIndex':row-1,'endIndex':row},'properties':{'pixelSize':ch['altura']},'fields':'pixelSize'}})
 out=ROOT/'r53/saidas/compactos-lotes';out.mkdir(exist_ok=True);manifest=[]
 for i in range(0,len(requests),200):
  path=out/(str(len(manifest))+'.json');raw=json.dumps(requests[i:i+200],ensure_ascii=False,separators=(',',':'));path.write_text(raw);manifest.append({'arquivo':str(path),'caracteres':len(raw)})
 (out/'manifesto.json').write_text(json.dumps(manifest));print(len(changes),'cartões;',len(requests),'pedidos;',len(manifest),'lotes')
if __name__=='__main__':main()
