"""Diagnóstico offline: diferenças contra a base B47 na geometria atual."""
import sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ficha-v01')]
import configuracao_horizontal as H,extensoes_custom as E

def preparar(base,alvo):
 b=copy.deepcopy(base['layout']);H.aplica(b);E.deslocar(b)
 old={a['nome']:a for a in b['abas']};new={a['nome']:a for a in alvo['layout']['abas']};diff={}
 for n,a in new.items():
  if n not in old:continue
  ov={r[0]:r[1] for r in old[n]['celulas']};nv={r[0]:r[1] for r in a['celulas']}
  changes={k:v for k,v in nv.items() if k not in ov or type(v) is not type(ov[k]) or v!=ov[k]}
  diff[n]=changes
 return b,diff
if __name__=='__main__':
 base=json.loads((ROOT/'r53/saidas/base-b47-ccbd053.json').read_text());alvo=json.loads((ROOT/'r53/saidas/modelo-r53.json').read_text());b,d=preparar(base,alvo)
 (ROOT/'r53/saidas/base-b47-final.json').write_text(json.dumps({'layout':b},ensure_ascii=False))
 (ROOT/'r53/saidas/delta-valores.json').write_text(json.dumps(d,ensure_ascii=False))
 print({k:len(v) for k,v in d.items()})
