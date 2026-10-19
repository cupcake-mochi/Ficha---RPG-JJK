"""Compacta o roteiro já localizado para o Sheets, sem localizar duas vezes."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'ficha'))
import emitir_gs as E

def gerar():
 src=json.loads((ROOT/'r53/saidas/testes-integral.json').read_text())
 meta=json.loads((ROOT/'r53/saidas/testes-integral.json.meta.json').read_text())
 req=[]
 for sid,grid in [(53018002,{'rowCount':meta['linhas'],'columnCount':meta['colunas']}),(53018005,{'columnCount':meta['catalogo_colunas']})]:
  req.append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':grid},'fields':','.join('gridProperties.'+k for k in grid)}})
 for item in src:
  u=item['updateCells'];sid=u['start']['sheetId'];rows=u['rows'];vals=[];cells={}
  for r,row in enumerate(rows,1):
   for c,cell in enumerate(row['values'],1):
    cells[r,c]=cell;vals.append([r,c,next(iter(cell.get('userEnteredValue',{}).values()),''),0])
  blocks=E._blocos_para_baixo(vals)
  removed={(r,c) for ra,c1,rb,c2 in blocks for r in range(ra+1,rb+1) for c in range(c1,c2+1)}
  kept={(r,c):v for r,c,v,_ in vals if (r,c) not in removed};rest=dict(kept)
  for ra,c1,rb,c2 in blocks:
   for r in range(ra+1,rb+1):
    for c in range(c1,c2+1):rest[r,c]=E.desloca(rest[ra,c],r-ra)
  assert rest=={(r,c):v for r,c,v,_ in vals}
  for start in range(0,len(rows),5):
   data=[{'values':[cells[rr,c] if (rr,c) in kept else {} for c in range(1,len(row['values'])+1)]} for rr,row in enumerate(rows[start:start+5],start+1)]
   req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':start,'columnIndex':0},'rows':data,'fields':'userEnteredValue'}})
  for ra,c1,rb,c2 in blocks:
   req.append({'copyPaste':{'source':{'sheetId':sid,'startRowIndex':ra-1,'endRowIndex':ra,'startColumnIndex':c1-1,'endColumnIndex':c2},'destination':{'sheetId':sid,'startRowIndex':ra,'endRowIndex':rb,'startColumnIndex':c1-1,'endColumnIndex':c2},'pasteType':'PASTE_FORMULA'}})
 out=ROOT/'r53/saidas/testes-lotes';out.mkdir(exist_ok=True);manifest=[];batch=[];size=0
 def save():
  raw=json.dumps(batch,ensure_ascii=False,separators=(',',':'));p=out/(str(len(manifest))+'.json');p.write_text(raw);manifest.append({'arquivo':str(p),'caracteres':len(raw)})
 for r in req:
  n=len(json.dumps(r,ensure_ascii=False))
  if batch and size+n>400000:save();batch=[];size=0
  batch.append(r);size+=n
 if batch:save()
 (out/'manifesto.json').write_text(json.dumps(manifest))
 print('Roteiro nativo preservado exatamente;',len(manifest),'lotes;',sum(x['caracteres'] for x in manifest),'caracteres')
if __name__=='__main__':gerar()
