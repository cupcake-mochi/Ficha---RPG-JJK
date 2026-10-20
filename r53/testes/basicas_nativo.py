"""Teste focal nativo: dependências dos quatro casos de dados/atuação básicos."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import modelo as M
from formulas import X,native,x
from verificar import CASOS,BASE
from gerar_nativo import col,cel
cases=CASOS[-4:];needed=set()
def walk(node):
 if not isinstance(node,X):return
 if node.op=='ref' and node.args[0] in M.ARVORE:
  key=node.args[0]
  if key not in needed:needed.add(key);walk(M.ARVORE[key])
 for arg in node.args:walk(arg)
for case in cases:
 for k in case['esperado']:
  if k!='valida':needed.add(k);walk(M.ARVORE[k])
outputs=[k for k in M.ARVORE if k in needed];names=M.INPUTS+outputs;cols={k:col(i+1) for i,k in enumerate(names)};rows=[]
for r,case in enumerate(cases,70):
 vals={**M.DEFAULTS,**BASE,**case['entrada']};refs={k:cols[k]+str(r) for k in names}
 expected={k:v for k,v in case['esperado'].items() if k!='valida'}
 checks=[refs[k]+'='+native(x(v),{},'',[],separator=';') for k,v in expected.items()]
 values=[vals[k] for k in M.INPUTS]+['='+native(M.ARVORE[k],refs,"'DADOS_R53_TESTES'!$A$2:$O$128",M.LOOKUP_FIELDS,separator=';') for k in outputs]+[case['nome'],'=AND('+';'.join(checks)+')']
 rows.append({'values':[cel(v) for v in values]})
req=[{'updateCells':{'start':{'sheetId':53018002,'rowIndex':69,'columnIndex':0},'rows':rows,'fields':'userEnteredValue'}}]
out=Path(__file__).resolve().parents[1]/'saidas/basicas-nativo.json';out.write_text(json.dumps(req,ensure_ascii=False))
meta={'casos':[c['nome'] for c in cases],'outputs':outputs,'range':"'TESTES R53'!"+col(len(names)+1)+'70:'+col(len(names)+2)+'73'};out.with_suffix('.meta.json').write_text(json.dumps(meta,ensure_ascii=False));print(meta['range'],len(out.read_text()),'bytes',len(outputs),'resultados necessários')
