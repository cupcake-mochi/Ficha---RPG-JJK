"""Delta de validação do editor SOMENTE para o primeiro cartão sintético.

Exige backup nativo e snapshot recente. Não é migração integral nem instalação
na oficial. O script apenas prepara pedidos, nunca realiza chamadas de rede.
"""
import json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47'),str(ROOT/'r53')]
import editor_r53 as E,montagens_r53 as R
from preparar_nativo import native_value,grid
from lotes import format_,pt
from openpyxl.utils.cell import coordinate_to_tuple,get_column_letter as L

def preparar():
 m=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=m['r53'];tabs={a['nome']:a for a in m['layout']['abas']}
 snap=json.loads((ROOT/'r53/saidas/antes-editor-native.json').read_text())['structuredContent']
 snap_tabs={s['properties']['title']:s for s in snap['sheets']}
 block=snap_tabs['MONTAGENS']['data'][0];saved={}
 for i,row in enumerate(block['rowData']):
  for j,cell in enumerate(row.get('values',[])):
   value=cell.get('userEnteredValue',{});saved[(block.get('startRow',0)+i+1,block.get('startColumn',0)+j+1)]=next(iter(value.values()),'')
 g=copy.deepcopy(tr['contextos'][0]);assert g['id']=='feitico.1'
 source=tabs[R.DADOS];cat=tabs[R.CATALOGO];owner=tabs[g['aba']];panel=tr['paineis'][g['aba']]
 assert panel['estado']==205 and panel['coluna']==24
 cfg=copy.deepcopy(tr);cfg['contextos']=[g]
 E.escrever(cfg,ROOT/'r53/saidas/EditorR53-prototipo.gs')
 req=[]
 for sid,props in [(543479115,{'columnCount':31}),(53018004,{'columnCount':len(tr['colunas']),'rowCount':207}),(53018001,{'columnCount':36})]:
  req.append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':props},'fields':','.join('gridProperties.'+k for k in props)}})
 def cells(sid,records,width,first,last):
  lookup={coordinate_to_tuple(c[0]):c for c in records};rows=[]
  for rr in range(first,last+1):
   rows.append({'values':[{'userEnteredValue':native_value(lookup[(rr,cc)][1])} if (rr,cc) in lookup else {} for cc in range(1,width+1)]})
  return {'updateCells':{'start':{'sheetId':sid,'rowIndex':first-1,'columnIndex':0},'rows':rows,'fields':'userEnteredValue'}}
 # Catálogo próprio será validado na etapa integral; os nomes vazios ficam protegidos pela condição da fórmula.
 req.append(cells(53018001,cat['celulas'],36,1,cat['linhas']))
 req.append(cells(53018004,source['celulas'],len(tr['colunas']),1,2))
 storage=[]
 for rr,(key,label,kind) in enumerate(R.CAMPOS,7):
  vals=[]
  for cc in range(2,9):
   value=saved.get((rr,cc),R.DEFAULTS_EDITOR[key]) if rr<=37 else R.DEFAULTS_EDITOR[key]
   vals.append({'userEnteredValue':native_value(value)})
  storage.append({'values':vals})
 req.append({'updateCells':{'start':{'sheetId':53018003,'rowIndex':6,'columnIndex':1},'rows':storage,'fields':'userEnteredValue'}})
 # Os campos de distribuição preservam os valores literais que o usuário já viu no teste.
 req.append({'repeatCell':{'range':grid(53018003,'B38:H39'),'cell':{},'fields':'dataValidation'}})
 out=ROOT/'r53/saidas/editor-nativo';out.mkdir(exist_ok=True)
 # Validação do armazenamento acompanha o catálogo novo, inclusive as Formas.
 req.append({'repeatCell':{'range':grid(53018003,'B7:H39'),'cell':{},'fields':'dataValidation'}})
 by={v['onde']:v for v in tabs[R.EDITOR]['menus']}
 for key,label,kind in R.CAMPOS:
  rr=g['campos'][key];menu=by.get('B'+str(rr))
  if not menu:continue
  f=menu['formula'];typ='BOOLEAN' if menu['tipo']=='bool' else 'CUSTOM_FORMULA' if menu['tipo']=='custom' else 'ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE';condition={'type':typ}
  if typ!='BOOLEAN':condition['values']=[{'userEnteredValue':v} for v in f[1:-1].split(',')] if typ=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f.lstrip('='))}]
  req.append({'setDataValidation':{'range':grid(53018003,'B'+str(rr)+':H'+str(rr)),'rule':{'condition':condition,'strict':True,'showCustomUi':True}}})
 (out/'01-dados.json').write_text(json.dumps(req,ensure_ascii=False))
 req=[];sid=543479115;records={v[0]:v for v in owner['celulas']}
 base=records[panel['campos']['funcao1']][2]
 req.append({'repeatCell':{'range':grid(sid,f'X{panel["linha"]}:AE{panel["fim"]}'),'cell':{'userEnteredFormat':format_(m['layout']['estilos'][base])},'fields':'userEnteredFormat'}})
 for a1,value,st,*_ in owner['celulas']:
  rr,cc=coordinate_to_tuple(a1)
  if not(panel['linha']<=rr<=panel['fim'] and 24<=cc<=31):continue
  cell={'userEnteredValue':native_value(value),'userEnteredFormat':format_(m['layout']['estilos'][st])}
  if a1 in owner.get('notas',{}):cell['note']=owner['notas'][a1]
  req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':rr-1,'columnIndex':cc-1},'rows':[{'values':[cell]}],'fields':'userEnteredValue,userEnteredFormat,note'}})
 for merged in owner['mescladas']:
  if coordinate_to_tuple(merged.split(':')[0])[1]>=24:req.append({'mergeCells':{'range':grid(sid,merged),'mergeType':'MERGE_ALL'}})
 for menu in owner['menus']:
  if not re_panel(menu['onde']):continue
  f=menu['formula'];kind='BOOLEAN' if menu['tipo']=='bool' else 'CUSTOM_FORMULA' if menu['tipo']=='custom' else 'ONE_OF_LIST' if f.startswith('"') else 'ONE_OF_RANGE'
  condition={'type':kind}
  if kind!='BOOLEAN':condition['values']=[{'userEnteredValue':v} for v in f[1:-1].split(',')] if kind=='ONE_OF_LIST' else [{'userEnteredValue':'='+pt(f.lstrip('='))}]
  req.append({'setDataValidation':{'range':grid(sid,menu['onde']),'rule':{'condition':condition,'strict':True,'showCustomUi':True}}})
 for col in range(24,32):req.append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'COLUMNS','startIndex':col-1,'endIndex':col},'properties':{'pixelSize':82},'fields':'pixelSize'}})
 req.append({'addDimensionGroup':{'range':{'sheetId':sid,'dimension':'COLUMNS','startIndex':23,'endIndex':31}}})
 (out/'02-painel.json').write_text(json.dumps(req,ensure_ascii=False))
 # O cartão já tem a linha Função; preserve sua geometria e desenho.
 req=[{'unmergeCells':{'range':grid(sid,'E80:H81')}},
      {'mergeCells':{'range':grid(sid,'E80:G81'),'mergeType':'MERGE_ALL'}},
      {'mergeCells':{'range':grid(sid,'H80:H81'),'mergeType':'MERGE_ALL'}}]
 for a1,formula in tr['formulas'][g['id']].items():
  rr,cc=coordinate_to_tuple(a1);req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':rr-1,'columnIndex':cc-1},'rows':[{'values':[{'userEnteredValue':native_value(formula)}]}],'fields':'userEnteredValue'}})
 for a1,v in [('E80','Editar funções e pontos →'),('H80',False),('D80','Editar')]:
  rr,cc=coordinate_to_tuple(a1);req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':rr-1,'columnIndex':cc-1},'rows':[{'values':[{'userEnteredValue':native_value(v)}]}],'fields':'userEnteredValue'}})
 req.append({'setDataValidation':{'range':grid(sid,'H80:H81'),'rule':{'condition':{'type':'BOOLEAN'},'strict':True,'showCustomUi':True}}})
 req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':63,'columnIndex':4},'rows':[{'values':[{'note':owner['notas'][g['cel']['nome']]}]}],'fields':'note'}})
 (out/'03-cartao.json').write_text(json.dumps(req,ensure_ascii=False))
 print('3 fases preparadas; runtime reduzido', (ROOT/'r53/saidas/EditorR53-prototipo.gs').stat().st_size,'bytes')

def re_panel(a1):return all(coordinate_to_tuple(v)[1]>=24 for v in a1.replace(':',' ').split())
if __name__=='__main__':preparar()
