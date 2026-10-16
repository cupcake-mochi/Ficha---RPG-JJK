#!/usr/bin/env python3
"""Executor serial focal; só executa seleções explícitas. Não acessa Google."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'infra-b47/saidas'
PYTHON = ROOT/'.venv/bin/python'


def inventario():
    p = str(PYTHON)
    model = str(OUT/'baseline/pecas-modelo.json')
    old = str(OUT/'baseline/pecas-modelo-anterior.json')
    def task(cmd, scope, *, deps=(), heavy=False, baseline=False, files=(), note=''):
        return dict(comando=cmd, escopo=scope, ferramentas=list(deps), pesado=heavy,
                    baseline=baseline, entradas=list(files), limite=note)
    return {
        'smoke': task([p, 'nuvem-b47/conferir.py', '--smoke'], 'Sintaxe, referências, catálogo/progressão/Kaori', deps=('node',)),
        'baseline': task([p, 'nuvem-b47/exportar-baseline.py', '--destino', str(OUT/'baseline')], 'Exportação única do modelo; não gera .gs', heavy=True),
        'pecas-estrutura': task([p, 'regressao-pecas.py', '--modelo', model, '--anterior', old, '--estrutura'], 'Estrutura e contrato de peças', baseline=True, note='Expectativas 789/395: integrador revisa após A.'),
        'pecas-calculo': task([p, 'regressao-pecas.py', '--modelo', model, '--anterior', old], 'Cálculo local das peças', deps=('calc',), heavy=True, baseline=True),
        'textos': task(['node', 'regressao-textos-custom.js', model], 'Sete cenários em VM', deps=('node',), baseline=True),
        'copias': task([p, 'conferir-copias.py'], 'Compactação/reexpansão dos .gs versionados', deps=('node',), heavy=True),
        'construcao': task(['node', '--max-old-space-size=1500', 'regressao-construir.js'], 'Construção simulada, não nativa', deps=('node',), heavy=True),
        'familias': task([p, 'regressao-familias-invocacao.py'], 'Nove posições, autonomia e orçamento local', deps=('calc',), heavy=True),
        'configuracao': task([p, 'regressao-configuracao.py'], 'Bônus, trocas e conflitos no workbook local', deps=('libreoffice',), heavy=True, files=('ficha-v01/ficha-projeto-m-0.1.xlsx',)),
        'campanha': task([p, 'regressao-campanha.py'], 'Regressão histórica de campanha', deps=('libreoffice',), heavy=True, files=('nuvem-b47/fixtures/base-parte1.xlsx',), note='Expectativa histórica de formato 5; não ajustar só para verde.'),
        'custom': task([p, 'regressao-custom.py'], 'Regressão histórica 3a', deps=('libreoffice',), heavy=True, files=('nuvem-b47/fixtures/base-parte2-local.xlsx',), note='Expectativa histórica de formato 6 e limitação FILTER.'),
        'progressao': task([p, 'regressao-progressao.py'], 'Regressão histórica 3b', deps=('libreoffice',), heavy=True, note='Expectativa histórica de formato 7.'),
        'leitor': task([p, 'ler-analise.py', '--teste'], 'Leitor do workbook local', deps=('libreoffice',), heavy=True, files=('ficha-v01/ficha-projeto-m-0.1.xlsx',), note='Exige workbook recém-gerado pelo integrador; não prova migração.'),
        'comparador': task([p, 'comparar-ficha-01.py'], 'Comparação histórica com original.xlsx', heavy=True, files=('nuvem-b47/fixtures/original.xlsx', 'ficha-v01/ficha-projeto-m-0.1.xlsx'), note='Original histórico disponível no Git; workbook atual não é gerado por este executor.'),
    }


def gravar(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def fingerprint():
    # Conteúdo real do checkout, inclusive alterações não commitadas do núcleo.
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'ficha-v01').rglob('*.py')]
    h = hashlib.sha256()
    for name in sorted(set(filter(None, names))):
        if name.startswith(('infra-b47/', 'revisao-b47/')):
            continue
        path = ROOT/name
        h.update(name.encode())
        h.update(hash_file(path).encode() if path.is_file() else b'AUSENTE')
    h.update(sys.version.encode())
    h.update(subprocess.check_output([str(PYTHON), '-m', 'pip', 'freeze'], cwd=ROOT))
    return h.hexdigest()


def baseline_valida(stamp):
    receipt = OUT/'baseline/recibo.json'
    try:
        data = json.loads(receipt.read_text())
        if not isinstance(data, dict):
            return False
        files = data.get('arquivos')
        if not isinstance(files, dict) or set(files) != {'pecas-modelo.json', 'pecas-modelo-anterior.json'}:
            return False
        return data.get('fingerprint') == stamp and all(
            isinstance(sha, str) and hash_file(OUT/'baseline'/n) == sha for n, sha in files.items()
        )
    except (OSError, ValueError):
        return False


def run_task(cmd, log, timeout, env):
    started = time.monotonic()
    with log.open('w') as stream:
        process = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
            reason = ''
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code, reason = process.returncode, 'Tempo limite; grupo de processos encerrado.'
    return dict(estado='executado' if code == 0 else 'falhou', exit_code=code,
                segundos=round(time.monotonic()-started, 3), motivo=reason, log=str(log))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('testes', nargs='*', choices=sorted(inventario()))
    ap.add_argument('--listar', action='store_true')
    ap.add_argument('--permitir-pesados', action='store_true')
    ap.add_argument('--timeout', type=int, default=900)
    a = ap.parse_args()
    if a.listar:
        print(json.dumps(inventario(), ensure_ascii=False, indent=2))
        return 0
    if not a.testes or a.timeout <= 0:
        ap.error('Selecione testes explicitamente e timeout positivo; use --listar.')
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT/'execucao.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            ap.exit(2, 'Outro executor focal está ativo neste checkout.\n')
        return executar(a)


def executar(a):
    folder = OUT/(time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())+'-'+uuid.uuid4().hex[:8])
    folder.mkdir()
    env = os.environ.copy()
    env['PATH'] = str(PYTHON.parent) + os.pathsep + env.get('PATH', '')
    env.setdefault('NODE_OPTIONS', '--max-old-space-size=1500')
    stamp = fingerprint() if PYTHON.is_file() else None
    report = {'sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'diff_inicial': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
              'fingerprint': stamp, 'resultados': [], 'aviso': 'Testes locais; sem Google. Smoke não é bateria integral.'}
    tasks = inventario()
    selected = list(dict.fromkeys(a.testes))
    if any(tasks[n]['baseline'] for n in selected):
        selected = ['baseline'] + [n for n in selected if n != 'baseline']
    for name in selected:
        t = tasks[name]
        result = dict(teste=name, comando=t['comando'], escopo=t['escopo'], limite=t['limite'])
        reasons = []
        if not PYTHON.is_file():
            reasons.append('Executar bootstrap nuvem-b47/preparar.sh.')
        for tool in t['ferramentas']:
            present = (shutil.which('libreoffice') or shutil.which('soffice')) if tool == 'calc' else shutil.which(tool)
            if not present:
                reasons.append('Ferramenta ausente: '+tool)
        reasons += ['Entrada ausente: '+n for n in t['entradas'] if not (ROOT/n).is_file()]
        cached = name == 'baseline' and stamp and baseline_valida(stamp)
        if t['pesado'] and not a.permitir_pesados and not cached:
            reasons.append('Requer --permitir-pesados e conferência prévia de memória.')
        if t['baseline'] and (not stamp or not baseline_valida(stamp)):
            reasons.append('Baseline ausente, alterada ou obsoleta; não reutilizada.')
        if reasons:
            result.update(estado='impedido', exit_code=None, motivo=' '.join(reasons))
        elif cached:
            result.update(estado='reutilizado', exit_code=None, motivo='Recibo e hashes válidos; exportação não repetida.')
        else:
            if name == 'baseline':
                (OUT/'baseline/recibo.json').unlink(missing_ok=True)
            try:
                result.update(run_task(t['comando'], folder/(name+'.log'), a.timeout, env))
                if name == 'baseline' and result['exit_code'] == 0:
                    if fingerprint() != stamp:
                        result.update(estado='falhou', motivo='Fontes mudaram durante exportação; sem recibo.')
                    else:
                        gravar(OUT/'baseline/recibo.json', {'fingerprint': stamp, 'sha': report['sha'],
                            'arquivos': {n: hash_file(OUT/'baseline'/n) for n in ('pecas-modelo.json', 'pecas-modelo-anterior.json')}})
            except OSError as e:
                result.update(estado='impedido', exit_code=None, motivo=str(e))
        report['resultados'].append(result)
        gravar(folder/'relatorio.json', report)
        print(name+': '+result['estado'], flush=True)
    print('Relatório: '+str(folder/'relatorio.json'))
    return 1 if any(r['estado'] == 'falhou' for r in report['resultados']) else 2 if any(r['estado'] == 'impedido' for r in report['resultados']) else 0


if __name__ == '__main__':
    sys.exit(main())
