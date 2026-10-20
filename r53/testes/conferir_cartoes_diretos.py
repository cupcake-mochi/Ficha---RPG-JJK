"""Guardas da geração: geometria, referências, configuração e tipos nativos."""
import json,sys
from pathlib import Path
from openpyxl.utils.cell import range_boundaries,coordinate_to_tuple
root=Path(__file__).resolve().parents[2]
m=json.loads((root/'r53/saidas/modelo-r53.json').read_text());old=json.loads((root/'r53/saidas/modelo-antes-diretos.json').read_text())
tr=m['r53'];assert tr['direto'] and not tr['paineis'];assert len(tr['contextos'])==249
names={a['nome']:a for a in m['layout']['abas']};oldtabs={a['nome']:a for a in old['layout']['abas']};n=0
for owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
 ranges=[]
 for text in names[owner]['mescladas']:
  c,r,cc,rr=range_boundaries(text)
  assert all(c>xx or cc<x or r>yy or rr<y for _,(x,y,xx,yy) in ranges),(owner,text)
  ranges.append((text,(c,r,cc,rr)));n+=1
for g in tr['contextos']:
 a=names[g['aba']];v={x[0]:x[1] for x in a['celulas']};inputs=g['entradas_diretas'];assert inputs and not g.get('abrir_editor')
 assert not(set(inputs.values())&set(tr['formulas'][g['id']])),g['id']
 for key,pos in inputs.items():
  assert not(isinstance(v[pos],str) and v[pos].startswith('=')),(g['id'],key)
  assert key in g['menus_diretos'];n+=1
 if g['modo']=='Comum':assert 'pessoal' in inputs and 'controle' in inputs and 'fragil_pago' in inputs
 if g['modo']=='Liberação de entidade':assert len(g['cel']['mel'])==4 and len(g['cel']['res'])==2
 for pos,txt in a['notas'].items():
  if pos in inputs.values():assert 'Use Editar' not in txt and 'MONTAGENS, linha' not in txt
 for p,formula in tr['formulas'][g['id']].items():assert formula==v[p]
# Configuration inputs are preserved verbatim; references to moved invocation rows
# may legitimately change, but their values/defaults and capacity do not.
newcfg={v[0]:v[1] for v in names['CONFIGURAÇÃO']['celulas'] if not(isinstance(v[1],str) and v[1].startswith('='))}
oldcfg={v[0]:v[1] for v in oldtabs['CONFIGURAÇÃO']['celulas'] if not(isinstance(v[1],str) and v[1].startswith('='))}
headers=[coordinate_to_tuple(p) for p,v in newcfg.items() if isinstance(v,str) and v.startswith('FORMAS · ')]
assert len(headers)==10
def forma(p):
 r,c=coordinate_to_tuple(p)
 return any(y<=r<y+46 and x<=c<x+6 for y,x in headers)
# Only the Formas cards and their introduction may change in CONFIGURAÇÃO.
changed={p for p in newcfg.keys()|oldcfg.keys() if newcfg.get(p)!=oldcfg.get(p)}
assert all(forma(p) or ('Forma define' in str(newcfg.get(p,''))) for p in changed),changed
assert names['CONFIGURAÇÃO']['linhas']==oldtabs['CONFIGURAÇÃO']['linhas'];n+=2
for p,v in newcfg.items():
 if forma(p):assert v not in ['RESOLUÇÃO','RESULTADO','EXIGE TR','RESTRIÇÃO EMBUTIDA'];n+=1
for g in tr['contextos']:
 blocks=g['gravacoes_diretas']
 for i,(r,c,rr,cc) in enumerate(blocks):
  assert all(c>xx or cc<x or r>yy or rr<y for y,x,yy,xx in blocks[:i]),g['id']
  for merge in names[g['aba']]['mescladas']:
   x,y,xx,yy=range_boundaries(merge)
   if not(c>xx or cc<x or r>yy or rr<y):assert c<=x<=xx<=cc and r<=y<=yy<=rr,(g['id'],merge)
 for p in g['entradas_diretas'].values():
  r,c=coordinate_to_tuple(p);assert sum(y<=r<=yy and x<=c<=xx for y,x,yy,xx in blocks)==1,(g['id'],p);n+=1
for entity in names['INVOCAÇÕES']['familias_custom']:
 for line in entity['linhas']:
  cell=next(v for v in names['INVOCAÇÕES']['celulas'] if v[0]==line['estado']);assert cell[1]==line['formula'];n+=1
print(json.dumps({'resultado':'OK','guardas':n,'cartoes':249,'escopo':'Geometria, tipos editáveis, referências de Famílias, configuração preservada; não substitui o Google.'},ensure_ascii=False))
