# -*- coding: utf-8 -*-
"""Confere os patches desta pasta numa worktree descartável (nunca no checkout, nunca no Google).

    python revisao-b47/cd-entidades/conferir_patches.py [--base REV] [--so 01|02|ambos] [--regressao] [--manter]

1. `git worktree add --detach` da base (padrão: HEAD) numa pasta temporária;
2. `git apply --check` e `git apply` dos patches, na ordem 02 → 01 (02 é independente);
3. a cópia ficha-v01/entidades_custom.py tem de ser idêntica ao módulo desta pasta;
4. ANALISE exportada antes e depois do 01: linhas da base idênticas e na mesma ordem, só as chaves novas no fim;
5. geração completa (monta.py) só na worktree: abas e .gs abaixo de 900.000 bytes;
6. sonda do carregador: os vals de cada aba carregados pelo JS, em três ordens, iguais à referência Python;
7. com --regressao, node regressao-construir.js antes (base versionada) e depois; falha que já existia na
   base vira risco preexistente, falha nova é bloqueante (pesado, ~1 min cada).

Os .gs gerados ficam na worktree temporária, que é apagada no fim (salvo --manter).
"""
import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
from comum_cd import Placar, python  # noqa: E402

PATCHES = {'02': AQUI / 'patches' / '02-copias-de-complemento.patch',
           '01': AQUI / 'patches' / '01-entidades-no-gerador.patch'}
TETO = 900_000

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--base', default='HEAD')
ap.add_argument('--so', choices=['01', '02', 'ambos'], default='ambos')
ap.add_argument('--regressao', action='store_true')
ap.add_argument('--manter', action='store_true')
args = ap.parse_args()
P = Placar('conferir patches ' + args.so)
tmp = Path(tempfile.mkdtemp(prefix='cd-ent-wt-'))
wt = tmp / 'wt'


def roda(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


try:
    base = roda(['git', 'rev-parse', args.base], cwd=RAIZ).stdout.strip()
    r = roda(['git', 'worktree', 'add', '--detach', str(wt), base], cwd=RAIZ)
    if r.returncode:
        raise SystemExit(r.stderr)
    print(f'base {base} · worktree {wt}\n')
    ordem = ['02', '01'] if args.so == 'ambos' else [args.so]
    env = dict(os.environ, PYTHONUTF8='1')

    def analise():
        destino = tmp / 'analise.json'
        r = roda([python(), 'ficha-v01/monta.py', '--exportar-analise', str(destino)], cwd=wt, env=env, timeout=1800)
        if r.returncode:
            raise SystemExit((r.stdout + r.stderr)[-1500:])
        return [tuple(l[:4]) for l in json.loads(destino.read_text(encoding='utf-8'))['linhas']]

    def regressao():
        rg = roda(['node', 'regressao-construir.js'], cwd=wt, timeout=1800)
        falhas = {l.strip() for l in rg.stdout.splitlines() if l.strip().startswith('FALHA')}
        return rg, len(re.findall(r'^\s+ok\s', rg.stdout, re.M)), falhas

    reg_base = regressao() if args.regressao and shutil.which('node') else None
    an_antes = None
    for k in ordem:
        if k == '01':
            an_antes = analise()
        chk = roda(['git', 'apply', '--check', str(PATCHES[k])], cwd=wt)
        P.check(f'patch {k} aplica limpo na base', not chk.returncode, chk.stderr[-400:])
        if not chk.returncode:
            roda(['git', 'apply', str(PATCHES[k])], cwd=wt)
    if '01' in ordem:
        P.check('ficha-v01/entidades_custom.py do patch é idêntico ao módulo desta pasta',
                filecmp.cmp(wt / 'ficha-v01' / 'entidades_custom.py', AQUI / 'entidades_custom.py', shallow=False))
        an = analise()
        novas = an[len(an_antes):]
        P.check(f'as {len(an_antes)} linhas ANALISE da base continuam idênticas e na mesma ordem',
                an[:len(an_antes)] == an_antes)
        P.check(f'{len(novas)} chaves novas no fim = 10×9 + 20×7 (custom.tipo_entidade / talento_entidade e avisos)',
                len(novas) == 230 and all(re.match(r'^(aviso\.)?custom\.(tipo|talento)_entidade\.\d+', l[0]) for l in novas),
                len(novas))
    g = roda([python(), 'ficha-v01/monta.py'], cwd=wt, env=env, timeout=1800)
    P.check('geração completa na worktree termina sem erro', not g.returncode, (g.stdout + g.stderr)[-800:])
    if '01' in ordem:
        P.check('DADOS_ENTIDADES entre as abas geradas', "'DADOS_ENTIDADES'" in g.stdout)
    gs = {p.name: p.stat().st_size for p in (wt / 'apps-script').glob('*.gs')}
    maior = max(gs.items(), key=lambda x: x[1])
    P.check(f'todos os {len(gs)} .gs abaixo de {TETO} bytes (maior {maior[0]} {maior[1]})',
            all(v < TETO for v in gs.values()), {k: v for k, v in gs.items() if v >= TETO})
    if '01' in ordem:
        P.check('Entidades.gs e EntidadesPainel.gs gerados', {'Entidades.gs', 'EntidadesPainel.gs'} <= set(gs), sorted(gs))
    ref = tmp / 'ref.json'
    rr = roda([python(), str(AQUI / 'referencia_carregador.py'), str(wt), str(wt / 'apps-script'), str(ref)], cwd=wt, env=env)
    if rr.returncode:
        P.check('referência Python do carregador', False, rr.stderr[-600:])
    elif not shutil.which('node'):
        P.impedido('carregador JS = referência Python', 'node ausente')
    else:
        s = roda(['node', str(AQUI / 'sonda_carregador_copias.js'), str(wt / 'apps-script'), str(ref)])
        print(s.stdout.strip())
        # sem o 02, a lacuna preexistente das cópias da CONFIGURAÇÃO aparece aqui: risco da base, não do 01
        P.check('carregador JS = referência Python em todas as abas, três ordens', not s.returncode, s.stdout[-600:],
                nivel='bloqueante' if '02' in ordem else 'risco')
    if args.regressao:
        if not shutil.which('node'):
            P.impedido('regressao-construir.js', 'node ausente')
        else:
            rg, oks, falhas = regressao()
            _, oks_base, falhas_base = reg_base
            P.check(f'regressao-construir.js: nenhuma falha nova ({oks} ok; base {oks_base} ok)',
                    oks > 0 and falhas <= falhas_base and (rg.returncode == 0 or falhas),
                    sorted(falhas - falhas_base) or (rg.stdout + rg.stderr)[-600:])
            if falhas_base:
                P.check('regressao-construir.js sem falhas preexistentes da base', not falhas_base,
                        sorted(falhas_base), nivel='risco')
finally:
    if not args.manter:
        roda(['git', 'worktree', 'remove', '--force', str(wt)], cwd=RAIZ)
        shutil.rmtree(tmp, ignore_errors=True)
P.fim()
