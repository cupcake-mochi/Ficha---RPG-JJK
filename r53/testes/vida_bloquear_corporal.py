"""Prepara ensaio nativo focal; não escreve em planilhas remotas."""
import json,sys,subprocess,argparse
from pathlib import Path
from openpyxl.formula import Tokenizer
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'ficha-v01'))
import configuracao as cfg

def pt(f):
 return '='+''.join(';' if t.type=='SEP' and t.subtype=='ARG' else t.value.replace('.',',') if t.type=='OPERAND' and t.subtype=='NUMBER' else t.value for t in Tokenizer(f).items)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pedidos',type=Path,required=True);args=ap.parse_args()
 js="const vm=require('vm');let c={};vm.createContext(c);vm.runInContext(require('./medidas/carregar-ficha').fontes(),c);console.log(JSON.stringify(c.ABAS.find(a=>a.nome==='FICHA').vals.filter(v=>(v[0]===26&&v[1]===10)||(v[0]===56&&v[1]===26))));"
 vals=json.loads(subprocess.check_output(['node','-e',js],cwd=ROOT));life=next(v[2] for v in vals if v[0]==26);block=next(v[2] for v in vals if v[0]==56)
 m=cfg.VIDA_QUEBRADICO.fullmatch(life);assert m
 assert cfg.anterior(life)==cfg.anterior('='+m['base'])
 assert not cfg.VIDA_QUEBRADICO.fullmatch(life.replace('INT(vidaNormal/2)','INT(vidaNormal/3)'))
 life=life.replace(m['base'],'B{r}').replace("'DADOS_CUSTOM'!$B$126",'D{r}').replace("'FICHA'!$D$52",'C{r}').replace('DADOS_CONFIG!$C$2','E{r}')
 block=block.replace("'DADOS_CUSTOM'!$B$126",'D{r}').replace("'FICHA'!$D$52",'C{r}').replace('D59','B{r}')
 cases=[]
 def add(name,n,body,base,swap,expected,formula=life):cases.append((name,n,body,base,swap,expected,formula))
 q='Corpo Quebradiço'
 for n,e in [(8,4),(13,6),(16,8),(22,11),(1,1),(0,1),(-3,1),('', '')]:add('Vida '+repr(n),n,q,True,0,e)
 for body in ['Corpo Exaurido','Corpo Debilitado','Corpo Próprio','Criada com o mestre']:add(body,16,body,True,0,16)
 add('Nome residual sem base',16,q,False,0,16)
 add('Trocar por final',30,q,True,1,30)
 add('Trocar por zero final',0,q,True,1,0)
 add('Erro de configuração','#N/A',q,True,0,'#N/A')
 for body in [q,'Corpo Exaurido','Corpo Debilitado']:add('Bloquear '+body,0,body,True,0,'Não pode bloquear',block)
 add('Bloquear corpo próprio',15,'Corpo Próprio',True,0,'2d10 + 4',block)
 add('Bloquear sem base',15,q,False,0,'2d10 + 4',block)
 def cell(v):return {'userEnteredValue':{'boolValue' if isinstance(v,bool) else 'numberValue' if isinstance(v,(int,float)) else 'stringValue':v}}
 rows=[{'values':[cell(x) for x in ['Cenário','Conta normal / Defesa','Corpo','Base corporal','Trocas','Esperado','Resultado','OK']]}]
 for r,(name,n,body,base,swap,expected,f) in enumerate(cases,2):
  cs=[cell(x) for x in [name,n,body,base,swap,expected]]
  if n=='#N/A':cs[1]={'userEnteredValue':{'formulaValue':'=NA()'}}
  cs += [{'userEnteredValue':{'formulaValue':pt(f.format(r=r))}},{'userEnteredValue':{'formulaValue':f'=ISNA(G{r})' if expected=='#N/A' else f'=AND(TYPE(G{r})=TYPE(F{r});G{r}=F{r})'}}]
  rows.append({'values':cs})
 sid=53018007
 req=[{'addSheet':{'properties':{'sheetId':sid,'title':'QA vida e Bloquear','gridProperties':{'rowCount':len(rows)+3,'columnCount':8,'frozenRowCount':1}}}},{'updateCells':{'start':{'sheetId':sid,'rowIndex':0,'columnIndex':0},'rows':rows,'fields':'userEnteredValue'}},{'autoResizeDimensions':{'dimensions':{'sheetId':sid,'dimension':'COLUMNS','startIndex':0,'endIndex':8}}}]
 args.pedidos.write_text(json.dumps(req,ensure_ascii=False));args.pedidos.with_suffix('.formulas.json').write_text(json.dumps({str(v[0]):pt(v[2]) for v in vals},ensure_ascii=False))
 print(json.dumps({'estrutura':'OK','cenarios':len(cases)}))
if __name__=='__main__':main()
