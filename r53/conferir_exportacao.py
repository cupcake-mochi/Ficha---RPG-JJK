"""Confere o contrato real a partir de uma leitura nativa da aba ANALISE."""
import argparse,json
from pathlib import Path
from contrato import decodificar

def conferir(path):
 snapshot=json.loads(Path(path).read_text());ficha={}
 for sh in snapshot['sheets']:
  if sh['properties']['title']!='ANALISE':continue
  for block in sh.get('data',[]):
   assert block.get('startColumn',0)==0
   for row in block.get('rowData',[]):
    values=[]
    for cell in row.get('values',[]):
     ev=cell.get('effectiveValue',{});assert 'errorValue' not in ev,ev
     values.append(next(iter(ev.values()),''))
    values+=['']*4
    if values[0]:
     assert values[0] not in ficha,('chave duplicada',values[0]);ficha[values[0]]=dict(valor=values[1],parte=values[2],celula=values[3])
 assert ficha['formato.versao']['valor'] in (12,'12')
 decoded=decodificar(ficha)
 return dict(resultado='OK',destino=snapshot['spreadsheetId'],chaves=len(ficha),chaves_preenchidas=sum(v['valor']!='' for v in ficha.values()),aplicacoes=len(decoded),versoes={k:list(v['versoes']) for k,v in decoded.items()}),decoded
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('snapshot');ap.add_argument('--saida');a=ap.parse_args();result,decoded=conferir(a.snapshot)
 print(json.dumps(result,ensure_ascii=False))
 if a.saida:Path(a.saida).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
