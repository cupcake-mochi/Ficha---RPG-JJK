"""Fragmentos de transporte R53 limitados por tamanho real estimado.

Reutiliza a cópia de linhas do emissor existente. O conteúdo completo continua
no modelo para auditoria; só a representação enviada ao AppsScript é reduzida.
"""
import json,sys
from pathlib import Path
from collections import defaultdict
from openpyxl.utils.cell import coordinate_to_tuple
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ficha'))
import emitir_gs as E
ABAS={'Dados':'DADOS_R53','Catalogo':'DADOS_R53_CATALOGO','Montagens':'MONTAGENS','Cartoes':'FICHA AMALDIÇOADA','CartoesEntidade':'INVOCAÇÕES'}
LIMITE=550_000

def valores_transporte(aba):
 vals=[]
 for addr,value,style,*_ in aba['celulas']:
  r,c=coordinate_to_tuple(addr);vals.append([r,c,value,style])
 if not aba.get('abaixo'):return vals
 blocos=E._blocos_para_baixo(vals)
 fora={(r,c) for ra,c1,rb,c2 in blocos for r in range(ra+1,rb+1) for c in range(c1,c2+1)}
 return [v for v in vals if (v[0],v[1]) not in fora]

def fatiar_linhas(vals,limite=LIMITE):
 if type(limite) is not int or limite<1000:raise ValueError('Limite inválido')
 rows=defaultdict(int)
 for row,col,value,*resto in vals:rows[row]+=len(json.dumps([row,col,value,*resto],ensure_ascii=False).encode())+5
 out=[];first=last=None;size=0
 for row,n in sorted(rows.items()):
  if n>limite:raise ValueError('Linha excede o limite do fragmento: '+str(row))
  if first is not None and size+n>limite:out.append((first,last,size));first=None;size=0
  if first is None:first=row
  last=row;size+=n
 if first is not None:out.append((first,last,size))
 return out

def suplementos(layout):
 tabs={a['nome']:a for a in layout['abas']};out={}
 for kind,name in ABAS.items():
  a=tabs[name]
  for i,(r1,r2,_) in enumerate(fatiar_linhas(valores_transporte(a)),1):out[f'R53{kind}{i}.gs']=(name,1,a['colunas'],r1,r2)
 a=tabs['ANALISE'];rows={coordinate_to_tuple(c[0])[0] for c in a['celulas'] if c[0].startswith('A') and isinstance(c[1],str) and c[1].startswith('r53.')}
 if not rows:raise ValueError('Contrato R53 ausente')
 vals=[v for v in valores_transporte(a) if v[0] in rows]
 for i,(r1,r2,_) in enumerate(fatiar_linhas(vals),1):out[f'R53Analise{i}.gs']=('ANALISE',1,4,r1,r2)
 return out

def complementos(suplementos):
 import re
 out={}
 # Retire only previously generated R53 fragments that no longer fit this
 # generation's partition. Register them so the emitter's existing cleanup
 # can remove them; unknown/user-authored files remain untouched.
 retired=[]
 for path in (ROOT/'apps-script').glob('R53*.gs'):
  if path.name not in suplementos and path.read_text().startswith('// GERADO POR ficha-v01/monta.py'):
   if re.fullmatch(r'R53(Dados|Catalogo|Montagens|Analise|Cartoes|CartoesEntidade)([1-9][0-9]*)\.gs',path.name):retired.append(path.name)
 for filename in list(suplementos)+retired:
  m=re.fullmatch(r'R53(Dados|Catalogo|Montagens|Analise|Cartoes|CartoesEntidade)([1-9][0-9]*)\.gs',filename)
  if not m:raise ValueError('Fragmento R53 inválido: '+filename)
  out[filename]='VALORES_R53_'+m[1].upper()+'_'+m[2]+'_'
 return out
