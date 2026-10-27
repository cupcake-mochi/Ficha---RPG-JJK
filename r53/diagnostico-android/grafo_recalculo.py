import json,re,sys,collections
import numpy as np
d=json.load(open(sys.argv[1]))
abas=list(d)
def col(s):
  n=0
  for ch in s: n=n*26+ord(ch)-64
  return n
REF=re.compile(r"(?:'((?:[^']|'')+)'|([A-Za-zÀ-ÿ_][A-Za-zÀ-ÿ0-9_ ]*?))?!?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")
REF=re.compile(r"(?:(?:'((?:[^']|'')+)'|([A-Za-z_][A-Za-z0-9_]*))!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?(?![A-Za-z0-9_(])")
forms=[]  # (aba,r,c,[(aba,r1,c1,r2,c2)])
for aba,s in d.items():
  for k,e in s['cells'].items():
    f=e.get('f')
    if not f: continue
    r,c=map(int,k.split(','))
    refs=[]
    for m in REF.finditer(str(f)):
      sh=(m.group(1) or m.group(2) or aba).replace("''","'")
      if sh not in d: continue
      try:
        c1=col(m.group(3)); r1=int(m.group(4))
        if m.group(5): c2=col(m.group(5)); r2=int(m.group(6))
        else: c2,r2=c1,r1
      except: continue
      refs.append((sh,min(r1,r2),min(c1,c2),max(r1,r2),max(c1,c2)))
    forms.append((aba,r,c,refs,str(f)))
print('fórmulas',len(forms),file=sys.stderr)
dim={a:(max(d[a]['rows'],1)+2,max(d[a]['cols'],1)+2) for a in d}
def fecho(sementes):
  dirty={a:np.zeros(dim[a],dtype=np.int32) for a in d}
  for a,r,c in sementes: dirty[a][r,c]=1
  marcado=set((a,r,c) for a,r,c in sementes)
  while True:
    ps={a:dirty[a].cumsum(0).cumsum(1) for a in d}
    def tem(a,r1,c1,r2,c2):
      P=ps[a]; R,C=P.shape; r2=min(r2,R-1); c2=min(c2,C-1)
      if r1>r2 or c1>c2: return False
      v=P[r2,c2]-(P[r1-1,c2] if r1>0 else 0)-(P[r2,c1-1] if c1>0 else 0)+(P[r1-1,c1-1] if r1>0 and c1>0 else 0)
      return v>0
    novos=[]
    for (a,r,c,refs,f) in forms:
      if (a,r,c) in marcado: continue
      if any(tem(*x) for x in refs): novos.append((a,r,c))
    if not novos: break
    for a,r,c in novos: dirty[a][r,c]=1; marcado.add((a,r,c))
  return marcado
def resumo(nome,m):
  cnt=collections.Counter(a for a,_,_ in m)
  tam=collections.Counter()
  fl={(a,r,c):len(f) for a,r,c,_,f in forms}
  for x in m: tam[x[0]]+=fl.get(x,0)
  print(nome,len(m),'células;', sum(tam.values())//1000,'mil caracteres de fórmula')
  for a,n in cnt.most_common(12): print('   ',a,n,tam[a]//1000,'k')
vol=[(a,r,c) for a,r,c,_,f in forms if 'INDIRECT' in f.upper()]
resumo('VOLÁTEIS (toda edição):',fecho(vol))
for alvo in sys.argv[2:]:
  a,cel=alvo.split('!'); m=re.match(r'([A-Z]+)(\d+)',cel)
  resumo('EDITAR '+alvo+':',fecho([(a,int(m.group(2)),col(m.group(1)))]))
