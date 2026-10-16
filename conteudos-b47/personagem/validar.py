"""Roteiro focal serial e evidência pequena; sem Calc/Google/geração GS."""
import argparse
import contextlib
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest
import warnings

AREA=Path(__file__).resolve().parent
ROOT=AREA.parents[1]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf8').strip()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidencia',action='store_true',help='salva VALIDACAO.json na pasta da entrega')
    a=ap.parse_args()
    print('Testes focais em série; a fixture canônica só é construída em memória.',flush=True)
    log=io.StringIO();t0=time.monotonic()
    with warnings.catch_warnings(),contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        # Os loaders canônicos abrem referências sem context manager; este
        # warning histórico não altera os resultados nem é teste de domínio.
        warnings.simplefilter('ignore',ResourceWarning)
        suite=unittest.defaultTestLoader.discover(str(AREA),pattern='test_*.py')
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    text=log.getvalue()
    local=AREA/'_local';local.mkdir(exist_ok=True)
    (local/'testes.log').write_text(text,encoding='utf8')
    hashes={}
    for p in sorted(AREA.rglob('*')):
        if p.is_file() and p.suffix in ('.py','.js','.patch') and '_local' not in p.parts and '__pycache__' not in p.parts:
            hashes[str(p.relative_to(AREA)).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest()
    mod=sys.modules.get('test_planilha')
    cls=getattr(mod,'TestPlanilha',None)
    evidencia=dict(data_utc=datetime.now(timezone.utc).isoformat(),ramo=git('branch','--show-current'),sha_testado=git('rev-parse','HEAD'),
        base_comum='0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd',contrato_lido='ae16895967d23044f558f31638df23c0fbdd7598',
        python=platform.python_version(),node=subprocess.check_output(['node','--version']).decode().strip(),
        segundos=round(time.monotonic()-t0,3),testes=result.testsRun,falhas=len(result.failures),erros=len(result.errors),
        pulados=len(result.skipped),resultado='OK' if result.wasSuccessful() else 'FALHA',
        medidas=getattr(cls,'medidas',None),novas_entradas=len(getattr(cls,'tr',{}).get('entradas',[])),
        editor={k:getattr(cls,'tr',{}).get(k) for k in ('inicio','fim')},
        arquivos_sha256=hashes,google='nenhuma escrita; nenhuma leitura de dados nativos nesta frente',
        integracao_producao=False,geracao_gs=False,
        impedidos=[dict(teste='recálculo das fórmulas no Calc',motivo='LibreOffice Calc ausente'),
                   dict(teste='bateria POSIX agregada da infra',motivo='fcntl indisponível no Python Windows'),
                   dict(teste='validação, aplicação e inspeção Google',motivo='responsabilidade exclusiva do integrador; não executadas')])
    if a.evidencia:(AREA/'VALIDACAO.json').write_text(json.dumps(evidencia,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(text[-10000:] if not result.wasSuccessful() else '\n'.join(x for x in text.splitlines() if x.startswith(('MEDIDAS','TRANSPORTE','CARREGAMENTO','Ran ')) or x=='OK'))
    print(json.dumps({k:evidencia[k] for k in ('resultado','testes','falhas','erros','segundos','sha_testado')},ensure_ascii=False),flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':sys.exit(main())
