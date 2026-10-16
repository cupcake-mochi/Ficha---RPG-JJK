#!/usr/bin/env python3
"""Exporta v9 do Git em checkout isolado; preserva a árvore de trabalho atual."""
import argparse,json,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--saida',type=Path,default=ROOT/'nuvem-b47/saidas/baseline-v9.json')
ap.add_argument('--medir-geracao',action='store_true',help='Também gera XLSX/GS somente no checkout temporário')
a=ap.parse_args();dest=a.saida.resolve();dest.parent.mkdir(parents=True,exist_ok=True)
sha=subprocess.check_output(['git','rev-parse','4187df3^{commit}'],cwd=ROOT,text=True).strip()
with tempfile.TemporaryDirectory(prefix='b47-base-') as tmp:
    checkout=Path(tmp)/'checkout'
    subprocess.run(['git','worktree','add','--detach',str(checkout),sha],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    try:
        start=time.perf_counter()
        subprocess.run([sys.executable,str(checkout/'ficha-v01/monta.py'),'--exportar-pecas',str(dest)],cwd=checkout,check=True)
        report={'base':sha,'exportacao_segundos':time.perf_counter()-start}
        if a.medir_geracao:
            import resource
            start=time.perf_counter();subprocess.run([sys.executable,str(checkout/'ficha-v01/monta.py')],cwd=checkout,check=True)
            report['geracao_segundos']=time.perf_counter()-start
            report['rss_max_filhos_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            report['gs']=[{'arquivo':p.name,'bytes':p.stat().st_size} for p in sorted((checkout/'apps-script').glob('*.gs'))]
            report['xlsx_bytes']=(checkout/'ficha-v01/ficha-projeto-m-0.1.xlsx').stat().st_size
        dest.with_suffix('.origem.json').write_text(json.dumps(report,indent=2))
    finally:
        # Only this newly-created temporary worktree can contain generated
        # changes. --force never addresses the user's checkout or a branch.
        subprocess.run(['git','worktree','remove','--force',str(checkout)],cwd=ROOT,check=True)
print(dest)
