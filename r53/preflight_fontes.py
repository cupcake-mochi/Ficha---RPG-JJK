"""Reúne padrões literais ausentes antes de executar extratores antigos.

É diagnóstico de compatibilidade, não substitui a extração com escopo de
capítulo. Não altera nem reinterpreta uma frase ausente para passar no teste.
"""
import ast,importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def conferir():
 spec=importlib.util.spec_from_file_location('extrair_manual',ROOT/'extrair-manual.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 manual=mod.texto((ROOT/'referencias-r53/LIVRO-COMPLETO.md').read_text());texto=' '.join(manual.split())
 titles={l.lstrip('#').strip() for l in manual.splitlines() if l.startswith('#')}
 checks=[]
 for path in sorted((ROOT/'ficha-v01').glob('extrair_*.py')):
  for node in ast.walk(ast.parse(path.read_text())):
   if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='frases' for t in node.targets) and isinstance(node.value,ast.Dict):
    for k,v in zip(node.value.keys,node.value.values):
     if isinstance(v,ast.Tuple) and v.elts and isinstance(v.elts[0],ast.Constant) and isinstance(v.elts[0].value,str):
      pattern=v.elts[0].value
      if ' '.join(pattern.split()) not in texto:checks.append(dict(arquivo=str(path.relative_to(ROOT)),linha=v.lineno,tipo='frase em lista',padrao=pattern))
   if not isinstance(node,ast.Call):continue
   if isinstance(node.func,ast.Name) and node.func.id=='exemplo':
    for val in node.args:
     if isinstance(val,ast.Constant) and isinstance(val.value,str) and ' '.join(val.value.split()) not in texto:checks.append(dict(arquivo=str(path.relative_to(ROOT)),linha=val.lineno,tipo='exemplo',padrao=val.value))
   name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
   idx=1 if name=='tab' else 0
   if name not in {'frase','re_frase','sec','capitulo','tabela','tab'} or len(node.args)<=idx:continue
   val=node.args[idx]
   if not isinstance(val,ast.Constant) or not isinstance(val.value,str):continue
   pattern=val.value
   if name in {'sec','capitulo'}:ok=pattern in titles
   elif name=='re_frase':ok=re.search(pattern,texto) is not None
   elif name in {'tab','tabela'}:ok=any(l.startswith(pattern+' | ') or l==pattern for l in manual.splitlines())
   else:ok=' '.join(pattern.split()) in texto
   if not ok:checks.append(dict(arquivo=str(path.relative_to(ROOT)),linha=node.lineno,tipo=name,padrao=pattern))
 return dict(edicao='R53',ausentes=len(checks),padroes=checks,escopo='Literais apenas; variáveis e frases em listas são revalidadas pelo extrator completo.')
if __name__=='__main__':
 r=conferir();(ROOT/'r53/PADROES-PENDENTES.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r['ausentes'],'padrões antigos ausentes; lista em r53/PADROES-PENDENTES.json')
