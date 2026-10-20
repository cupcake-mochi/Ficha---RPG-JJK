"""Planeja aplicação R53 em cópia identificada, sem rede e sem Excel.

Novas abas são gravadas por blocos. Alterações de cartões ficam numa fase
separada e exigem snapshot/backup atual. Não chama construir/continuar.
"""
from pathlib import Path
import sys,json,copy
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'capacidade-b47'),str(ROOT/'ficha-v01')]
from lotes import format_,rgb,pt

def native_value(value):
 if value is None:return {}
 if type(value) is bool:return {'boolValue':value}
 if isinstance(value,(int,float)):return {'numberValue':value}
 if isinstance(value,str) and value.startswith('='):return {'formulaValue':pt(value)}
 return {'stringValue':str(value)}
import montagens_r53 as R
IDS={'MONTAGENS':53018003,'DADOS_R53':53018004,'DADOS_R53_CATALOGO':53018001,
     'FICHA AMALDIÇOADA':543479115,'INVOCAÇÕES':996249592}


def grid(sid,a1):
 c,r,cc,rr=range_boundaries(a1)
 return dict(sheetId=sid,startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)


def preparar(modelo,destino):
 tabs={a['nome']:a for a in modelo['layout']['abas']};out=Path(destino);out.mkdir(parents=True,exist_ok=True)
 fases=[]
 def guardar(nome,req):
  path=out/(nome+'.json');path.write_text(json.dumps(req,ensure_ascii=False));fases.append(dict(fase=nome,arquivo=str(path),requests=len(req)))
 novas=[]
 for nome in ['MONTAGENS','DADOS_R53']:
  a=tabs[nome];novas.append({'addSheet':{'properties':{'sheetId':IDS[nome],'title':nome,'hidden':a['estado']=='hidden','gridProperties':{'rowCount':a['linhas'],'columnCount':a['colunas'],'hideGridlines':True,'frozenRowCount':3 if nome=='MONTAGENS' else 0}}}})
 novas.append({'updateSheetProperties':{'properties':{'sheetId':IDS['DADOS_R53_CATALOGO'],'gridProperties':{'columnCount':tabs['DADOS_R53_CATALOGO']['colunas']}},'fields':'gridProperties.columnCount'}})
 guardar('00-criar',novas)
 for nome in ['DADOS_R53_CATALOGO','DADOS_R53','MONTAGENS']:
  a=tabs[nome];sid=IDS[nome];vals={coordinate_to_tuple(v[0]):v for v in a['celulas']}
  passo=4 if nome=='DADOS_R53' else 300 if nome=='MONTAGENS' else 180
  for inicio in range(1,a['linhas']+1,passo):
   rows=[]
   for r in range(inicio,min(a['linhas']+1,inicio+passo)):
    row=[]
    for c in range(1,a['colunas']+1):
     v=vals.get((r,c)); cell={}
     if v:
      cell['userEnteredValue']=native_value(v[1])
      if isinstance(v[1],bool):cell['dataValidation']={'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}
     row.append(cell)
    rows.append({'values':row})
   fields='userEnteredValue,dataValidation' if nome=='MONTAGENS' else 'userEnteredValue'
   guardar(nome+'-'+str(inicio).zfill(4),[{'updateCells':{'start':{'sheetId':sid,'rowIndex':inicio-1,'columnIndex':0},'rows':rows,'fields':fields}}])
 if True:
  a=tabs['MONTAGENS'];sid=IDS['MONTAGENS'];req=[]
  for c1,c2,w in a['colunas_larg']:
   req.append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'COLUMNS','startIndex':c1-1,'endIndex':c2},'properties':{'pixelSize':int(w*7+5)},'fields':'pixelSize'}})
  for a1 in a['mescladas']:req.append({'mergeCells':{'range':grid(sid,a1),'mergeType':'MERGE_ALL'}})
  from collections import defaultdict
  from openpyxl.formula.translate import Translator
  grupos=defaultdict(list)
  for menu in a['menus']:
   row,column=coordinate_to_tuple(menu['onde'])
   formula=menu['formula']
   if menu['tipo']=='custom':formula=Translator('='+formula,origin=menu['onde']).translate_formula('B'+str(row))[1:]
   grupos[(row,menu['tipo'],formula)].append(column)
  menus=[]
  for (row,tipo,formula),columns in grupos.items():
   menus.append(dict(onde=L(min(columns))+str(row)+':'+L(max(columns))+str(row),tipo=tipo,formula=formula))
  for menu in menus:
   if menu['tipo']=='bool':continue # Checkbox data is already written with its cells.
   f=menu['formula'];kind='CUSTOM_FORMULA' if menu['tipo']=='custom' else 'ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE'
   values=[{'userEnteredValue':x} for x in f[1:-1].split(',')] if kind=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f.lstrip('='))}]
   rule={'condition':{'type':kind,'values':values},'strict':True,'showCustomUi':True}
   req.append({'setDataValidation':{'range':grid(sid,menu['onde']),'rule':rule}})
  for num,(r,rr,fechada) in enumerate(a['grupos']['linhas']):
   rg={'sheetId':sid,'dimension':'ROWS','startIndex':r-1,'endIndex':rr}
   req.extend([{'addDimensionGroup':{'range':rg}},
    {'updateDimensionGroup':{'dimensionGroup':{'range':rg,'depth':1,'collapsed':bool(fechada and num>0)},'fields':'collapsed'}}])
  # Estilos são aplicados por regiões, não repetidos em 47 mil células.
  records={v[0]:v for v in a['celulas']}
  first=modelo['r53']['contextos'][0]
  entrada=records['B'+str(first['campos']['preparada'])][2]
  rotulo=records['A'+str(first['campos']['preparada'])][2]
  formatos=[{'repeatCell':{'range':{'sheetId':sid},'cell':{'userEnteredFormat':format_(modelo['layout']['estilos'][entrada])},'fields':'userEnteredFormat'}},
            {'repeatCell':{'range':{'sheetId':sid,'startColumnIndex':0,'endColumnIndex':1},'cell':{'userEnteredFormat':format_(modelo['layout']['estilos'][rotulo])},'fields':'userEnteredFormat'}}]
  for g in modelo['r53']['contextos']:
   row=g['editor'];header=records['A'+str(row)][2]
   formatos.append({'repeatCell':{'range':grid(sid,f'A{row}:I{row}'),'cell':{'userEnteredFormat':format_(modelo['layout']['estilos'][header])},'fields':'userEnteredFormat'}})
  req=formatos+req
  for i in range(0,len(req),500):guardar('editor-estrutura-'+str(i).zfill(5),req[i:i+500])
 (out/'FASES.json').write_text(json.dumps(fases,ensure_ascii=False,indent=2)+'\n')
 return fases


if __name__=='__main__':
 m=json.loads(Path(sys.argv[1]).read_text());r=preparar(m,sys.argv[2]);print('Fases:',len(r),'requisições:',sum(v['requests'] for v in r))
