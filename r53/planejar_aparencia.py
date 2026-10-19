"""Adapta somente os campos novos à paleta que a cópia já utiliza."""
import json
from pathlib import Path
from openpyxl.utils.cell import coordinate_to_tuple
ROOT=Path(__file__).resolve().parents[1]

def gerar():
 model=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=model['r53']
 sample=json.loads((ROOT/'r53/saidas/amostras-paleta-por-aba.json').read_text())
 swatches={}
 for sheet in sample['sheets']:
  cells={}
  for data in sheet['data']:
   for r,row in enumerate(data.get('rowData',[]),data['startRow']+1):
    for c,cell in enumerate(row.get('values',[]),data['startColumn']+1):cells[r,c]=cell.get('userEnteredFormat',{})
  swatches[sheet['properties']['title']]=(cells[73,4],cells[73,5]) if sheet['properties']['title']=='FICHA AMALDIÇOADA' else (cells[72,9],cells[80,10])
 ids={'FICHA AMALDIÇOADA':543479115,'INVOCAÇÕES':996249592};req=[]
 def colors(sid,r,c,rr,cc,bg):
  rg={'sheetId':sid,'startRowIndex':r-1,'endRowIndex':rr,'startColumnIndex':c-1,'endColumnIndex':cc}
  req.append({'repeatCell':{'range':rg,'cell':{'userEnteredFormat':{'backgroundColorStyle':{'rgbColor':bg},'textFormat':{'foregroundColorStyle':{'rgbColor':text}}}},'fields':'userEnteredFormat.backgroundColorStyle,userEnteredFormat.textFormat.foregroundColorStyle'}})
 def borders(sid,r,c,rr,cc):
  edge={'style':'SOLID_MEDIUM','colorStyle':{'rgbColor':border}}
  req.append({'updateBorders':{'range':{'sheetId':sid,'startRowIndex':r-1,'endRowIndex':rr,'startColumnIndex':c-1,'endColumnIndex':cc},**{k:edge for k in ['top','bottom','left','right','innerHorizontal','innerVertical']}}})
 for g in tr['contextos']:
  if 'linha_funcao' not in g:continue
  label,body=swatches[g['aba']];border=body['borders']['top']['color'];text=body['textFormat']['foregroundColor']
  sid=ids[g['aba']];r=g['linha_funcao'];c=g['coluna']
  colors(sid,r,c,r,c,label['backgroundColor']);colors(sid,r,c+1,r,c+4,body['backgroundColor']);borders(sid,r,c,r,c+4)
 for owner,p in tr['paineis'].items():
  label,body=swatches[owner];border=body['borders']['top']['color'];text=body['textFormat']['foregroundColor']
  sid=ids[owner];r=p['linha'];c=p['coluna'];end=p['fim']
  colors(sid,r,c,end,c+7,body['backgroundColor']);borders(sid,r,c,end,c+7)
  for row in [4,5,8,15,22]:colors(sid,row,c,row,c+7,label['backgroundColor'])
  for key,pos in p['campos'].items():
   row,col=coordinate_to_tuple(pos)
   if row in [7,9,10,11,20,21]:continue
   colors(sid,row,c,row,c+2,label['backgroundColor'])
 out=ROOT/'r53/saidas/aparencia-lotes';out.mkdir(exist_ok=True);manifest=[]
 for i in range(0,len(req),300):
  path=out/(str(len(manifest))+'.json');raw=json.dumps(req[i:i+300],ensure_ascii=False,separators=(',',':'));path.write_text(raw);manifest.append({'arquivo':str(path),'caracteres':len(raw)})
 (out/'manifesto.json').write_text(json.dumps(manifest));print('Apenas cores e bordas novas:',len(req),'pedidos;',len(manifest),'lotes')
if __name__=='__main__':gerar()
