"""Prepara ensaio das fórmulas reais em cópia Google; não escreve em produção."""
import json,subprocess,math
from pathlib import Path
from openpyxl.formula import Tokenizer
js="const vm=require('vm'),c={};vm.createContext(c);vm.runInContext(require('./medidas/carregar-ficha').fontes(),c);console.log(JSON.stringify(c.ABAS.find(a=>a.nome==='FICHA').vals.filter(v=>v[0]===41&&[4,15,26,37].includes(v[1]))));"
forms=[v[2] for v in json.loads(subprocess.check_output(['node','-e',js]))]
cases=[(1,1,0,0),(3,1,0,0),(4,1,1,0),(11,1,2,0),(45,1,3,0),(46,1,0,0),(93,3,0,0),(395,7,0,0),(100,2,1,0),(20,1,0,3),(20,1,2,2)]
def cv(v):return {'userEnteredValue':{'boolValue' if isinstance(v,bool) else 'numberValue' if isinstance(v,(int,float)) else 'stringValue':v}}
def pt(f):return '='+''.join(';' if t.type=='SEP' and t.subtype=='ARG' else t.value for t in Tokenizer(f).items)
rows=[{'values':[cv(v) for v in ['Cenário','Máximo','Classe','Sequela 1','Sequela 2','Sequela 3','Extras','Aguentar esperado','Insistir 1 esperado','Insistir 2 esperado','Janela esperada','Aguentar real','Insistir 1 real','Insistir 2 real','Janela real','OK']]}]
for r,(mx,cl,s,e) in enumerate(cases,2):
 window=max(0,3-s-e); exp=[math.ceil(mx/4),min(math.ceil(mx/3),15*cl),min(math.ceil(mx/2),15*cl),'Derrotado na hora' if not window else str(window)+(' rodada' if window==1 else ' rodadas')]
 vals=[cv(v) for v in [f'Caso {r-1}',mx,cl,s>=1,s>=2,s>=3,e]+exp]
 for f in forms:
  for a,b in [('J26',f'B{r}'),('Z73',f'C{r}'),('F48',f'D{r}'),('H48',f'E{r}'),('J48',f'F{r}'),('J50',f'G{r}')]:
   import re
   f=f.replace("'FICHA'!$"+re.sub(r'(\d+)',r'$\1',a),b)
  vals.append({'userEnteredValue':{'formulaValue':pt(f)}})
 vals.append({'userEnteredValue':{'formulaValue':f'=AND(H{r}=L{r};I{r}=M{r};J{r}=N{r};K{r}=O{r})'}})
 rows.append({'values':vals})
requests=[{'addSheet':{'properties':{'sheetId':53018008,'title':'QA Morrendo','gridProperties':{'rowCount':20,'columnCount':16,'frozenRowCount':1}}}},{'updateCells':{'start':{'sheetId':53018008,'rowIndex':0,'columnIndex':0},'rows':rows,'fields':'userEnteredValue'}}]
Path('/tmp/morrendo-pedidos.json').write_text(json.dumps(requests,ensure_ascii=False))
print(json.dumps({'cenarios':len(cases),'formulas':len(forms)}))
