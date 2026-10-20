"""Repara somente o artefato temporário gerado antes da correção do cache.

A correção definitiva está no typed=True dos transformadores do gerador.
Não lê/escreve dados de personagem, não envia nada ao Google.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ficha-v01'))
import montagens_r53 as r
p=Path(sys.argv[1]);j=json.loads(p.read_text());abas={a['nome']:a for a in j['layout']['abas']}
editor={v[0]:v for v in abas[r.EDITOR]['celulas']};n=0
for g in j['r53']['contextos']:
 for c,classe in enumerate(g['classes'],2):
  for campo,_,kind in r.CAMPOS:
   a1=r.L(c)+str(g['campos'][campo]);v=editor[a1]
   if kind=='inteiro' and type(v[1]) is bool and v[1] is False:
    v[1]=0;n+=1
  header=editor[r.L(c)+str(g['editor']+1)]
  if classe==0 and type(header[1]) is bool:header[1]=0;n+=1
cat={v[0]:v for v in abas[r.CATALOGO]['celulas']}
for row,opt in enumerate(r.M.CAT['opcoes'],2):
 for c,key in enumerate(r.M.LOOKUP_FIELDS,1):cat[r.L(c)+str(row)][1]=opt[key]
p.write_text(json.dumps(j,ensure_ascii=False));print('Valores tipados reparados no artefato local:',n)
