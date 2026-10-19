"""Prepara a retirada dos exemplos sintéticos da cópia de validação R53.

Não usa rede. Apenas os dois registros comprovadamente criados pelo teste,
os controles de ação e os painéis transitórios são restaurados.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ficha-v01'),str(ROOT/'r53')]
from preparar_nativo import native_value,grid,IDS
import montagens_r53 as R

def preparar():
 m=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());tr=m['r53'];req=[]
 def values(sid,a1,rows):
  req.append({'updateCells':{'range':grid(sid,a1),'rows':[{'values':[{'userEnteredValue':native_value(v)} for v in row]}for row in rows],'fields':'userEnteredValue'}})
 values(IDS['FICHA AMALDIÇOADA'],'D64:E64',[[1,None]])
 values(1364162823,'F46',[[None]])
 # O teclado chegou à próxima linha visível ao tentar uma linha recolhida.
 # A célula era vazia no snapshot e só recebeu um espaço durante o teste.
 values(IDS['FICHA AMALDIÇOADA'],'N366',[[None]])
 defaults=[R.DEFAULTS_EDITOR[k] for k,_,_ in R.CAMPOS]
 values(IDS['MONTAGENS'],'D7:E39',[[v,v]for v in defaults])
 values(IDS['DADOS_R53'],'A253:C254',[[None]*3,[None]*3])
 original_maxima={'sheetId':IDS['FICHA AMALDIÇOADA'],'dimension':'ROWS','startIndex':354,'endIndex':365}
 req.extend([{'updateDimensionGroup':{'dimensionGroup':{'range':original_maxima,'depth':1,'collapsed':True},'fields':'collapsed'}},{'updateDimensionProperties':{'range':original_maxima,'properties':{'hiddenByUser':True},'fields':'hiddenByUser'}}])
 for name,panel in tr['paineis'].items():
  sid=IDS[name];c=panel['coluna'];r=panel['linha'];last=panel['fim']
  req.append({'setDataValidation':{'range':grid(sid,panel['classe']),'rule':{'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':str(i)}for i in range(1,8)]},'strict':True,'showCustomUi':True}}})
  req.append({'updateCells':{'start':{'sheetId':sid,'rowIndex':r-1,'columnIndex':c-1},'rows':[{'values':[{'userEnteredValue':native_value(v)}for v in row]}for row in panel['template']],'fields':'userEnteredValue'}})
  group={'sheetId':sid,'dimension':'COLUMNS','startIndex':c-1,'endIndex':c+7}
  req.extend([{'updateDimensionGroup':{'dimensionGroup':{'range':group,'depth':1,'collapsed':True},'fields':'collapsed'}},{'updateDimensionProperties':{'range':group,'properties':{'hiddenByUser':True},'fields':'hiddenByUser'}}])
 for g in tr['contextos']:values(IDS[g['aba']],g['abrir_editor'],[[False]])
 values(53018006,'B1',[['Validada; exemplos de teste retirados']])
 for row in [3,4]:values(53018006,'D'+str(row),[['Exemplo sintético retirado da ficha; registro preservado para recuperação']])
 req.extend({'deleteSheet':{'sheetId':sid}}for sid in [53018002,53018005])
 out=ROOT/'r53/saidas/limpeza-final.json';out.write_text(json.dumps(req,ensure_ascii=False));print(json.dumps({'arquivo':str(out),'pedidos':len(req),'caracteres':len(out.read_text())}))
if __name__=='__main__':preparar()
