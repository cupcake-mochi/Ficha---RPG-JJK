# -*- coding: utf-8 -*-
"""Valida o patch sugerido patches/carregador-selo-de-geracao.diff numa worktree temporária.

Cenários, para o perfil escolhido:
  1. pasta gerada pelo patch: guarda deixa construir e a ANALISE montada é o contrato exportado;
  2. mesma pasta + PecasAnalise2/3/4.gs da base (sobras de um projeto Apps Script antigo):
     a guarda recusa citando as sobras, e as sobras não entram na ANALISE.
Não altera o checkout nem o Google. O patch é proposta; quem aplica é o integrador.

    python revisao-b47/test_patch_carregador.py --perfil simulado-alvo
    python revisao-b47/test_patch_carregador.py --perfil base-v9
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import comum

ap = comum.argumentos(__doc__)
args = ap.parse_args()
p = comum.perfil(args.perfil)
P = comum.Placar('patch carregador ' + args.perfil)
L = comum.linhas_analise(args.analise or comum.exportar(args.perfil, 'analise'))
chaves = comum.SAIDAS / f'chaves-{args.perfil}.json'
chaves.write_text(json.dumps([l[0] for l in L], ensure_ascii=False), encoding='utf-8')
patch = comum.AQUI / 'patches' / 'carregador-selo-de-geracao.diff'


def sonda(pasta):
    r = subprocess.run(['node', str(comum.AQUI / 'sonda_carregador.js'), str(pasta), str(chaves)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout)


tmp = Path(tempfile.mkdtemp(prefix='revisao-b47-patch-'))
wt = tmp / 'wt'
subprocess.run(['git', 'worktree', 'add', '-q', '--detach', str(wt), 'HEAD'], cwd=comum.RAIZ, check=True)
try:
    r = subprocess.run(['git', 'apply', str(patch)], cwd=wt, capture_output=True, text=True)
    P.check('patch aplica sobre o SHA em teste', r.returncode == 0, r.stderr)
    r = subprocess.run([comum.python(), str(comum.AQUI / 'rodar_gerador.py'), str(wt), json.dumps(p['trocas'])],
                       cwd=wt, capture_output=True, text=True)
    P.check('geração completa com o patch termina', r.returncode == 0, (r.stdout + r.stderr)[-500:])
    pasta = wt / 'apps-script'
    pecas = sorted(f.name for f in pasta.glob('PecasAnalise*.gs'))
    s = sonda(pasta)
    P.check(f'pasta gerada ({len(pecas)} PecasAnalise): guarda deixa construir', s['guarda'] == 'passa', s['guarda'])
    P.check('pasta gerada: ANALISE montada = contrato', s['mesmaOrdem'] and not s['alemDaGrade'],
            f"{s['nObsoletas']} obsoletas, {s['nRepetidas']} repetidas")
    antigos = [n for n in ('PecasAnalise2.gs', 'PecasAnalise3.gs', 'PecasAnalise4.gs') if n not in pecas]
    if antigos:
        for n in antigos:
            shutil.copy(comum.RAIZ / 'apps-script' / n, pasta / n)
        s2 = sonda(pasta)
        P.check('com sobras antigas: guarda recusa e cita os arquivos',
                s2['guarda'].startswith('Apague do projeto') and all(n in s2['guarda'] for n in antigos), s2['guarda'])
        P.check('com sobras antigas: nada delas entra na ANALISE', s2['mesmaOrdem'] and not s2['alemDaGrade'],
                f"{s2['nObsoletas']} obsoletas")
    P.check('arquivos dentro do teto de 900.000 bytes', all(f.stat().st_size < 900000 for f in pasta.glob('*.gs')),
            {f.name: f.stat().st_size for f in pasta.glob('*.gs') if f.stat().st_size >= 900000})
finally:
    subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=comum.RAIZ)
    shutil.rmtree(tmp, ignore_errors=True)
P.fim(dict(perfil=args.perfil, pecas=pecas))
