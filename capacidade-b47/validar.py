#!/usr/bin/env python3
"""Executor focal serial A+B. Sem Google; cada falha/impedimento fica explícito."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--saida',type=Path,default=ROOT/'nuvem-b47/saidas/focal')
a=ap.parse_args();out=a.saida.resolve();out.mkdir(parents=True,exist_ok=True)
python=str(ROOT/'.venv/bin/python')
if not Path(python).exists():raise SystemExit('Execute bash nuvem-b47/preparar.sh antes do roteiro focal')
base=str(out/'baseline-v9.json');model=str(out/'pecas-modelo.json');prior=str(out/'pecas-modelo-anterior.json')
commands=[('smoke',[python,'nuvem-b47/conferir.py','--smoke']),
          ('base',[python,'capacidade-b47/exportar-base.py','--saida',base]),
          ('modelo',[python,'nuvem-b47/exportar-baseline.py','--destino',str(out)]),
          ('geracao',[python,'ficha-v01/monta.py']),
          ('infra-unit',[python,'-m','unittest','discover','-s','infra-b47','-p','test_*.py','-v']),
          ('selo',['node','capacidade-b47/testar-geracao.js']),
          ('envio',[python,'capacidade-b47/testar-envio.py']),
          ('revisao-contrato',[python,'revisao-b47/test_contrato.py','--perfil','b47-v10','--analise',model]),
          ('revisao-leitor',[python,'revisao-b47/test_leitor.py','--perfil','b47-v10','--analise',model]),
          ('revisao-enderecos',[python,'revisao-b47/test_enderecos.py','--perfil','b47-v10','--analise',model]),
          ('capacidade',[python,'capacidade-b47/testar-capacidade.py','--base',base,'--alvo',model]),
          ('migracao',[python,'capacidade-b47/testar-migracao.py','--base',base,'--alvo',model]),
          ('pecas',[python,'regressao-pecas.py','--modelo',model,'--anterior',prior]),
          ('progressao',[python,'regressao-progressao.py']),
          ('treinos',[python,'capacidade-b47/testar-treinos.py','--modelo',model]),
          ('validacao3a',[python,'capacidade-b47/testar-validacao3a.py','--modelo',model]),
          ('familias',[python,'regressao-familias-invocacao.py']),
          ('copias',[python,'conferir-copias.py']),
          ('construir',['node','--max-old-space-size=1500','regressao-construir.js']),
          ('textos',['node','regressao-textos-custom.js',model]),
          ('leitor',[python,'ler-analise.py','--teste'])]
env=dict(os.environ);env['PATH']=str(ROOT/'.venv/bin')+os.pathsep+env['PATH'];env['NODE_OPTIONS']='--max-old-space-size=1500'
report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'tipo':'testes locais; sem execução Google','testes':[]}
for name,cmd in commands:
    print('Executando '+name,flush=True);start=time.perf_counter()
    with (out/(name+'.log')).open('w') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    report['testes'].append({'teste':name,'comando':cmd,'exit':result.returncode,'segundos':time.perf_counter()-start})
    report['resultado']='OK' if all(x['exit']==0 for x in report['testes']) else 'FALHA'
    (out/'resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(name+': exit='+str(result.returncode),flush=True)
    # Dependent steps cannot use a missing/stale artifact after setup/generation fails.
    if result.returncode and name in ('smoke','base','modelo','geracao'):break
raise SystemExit(report['resultado']!='OK')
