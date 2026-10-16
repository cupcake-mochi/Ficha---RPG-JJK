# -*- coding: utf-8 -*-
"""Carregador do Apps Script (modelo.gs.js) diante de uma ANALISE de tamanho diferente.

Modo real (perfil sem 'trocas'): usa os .gs versionados do SHA em teste.
Modo simulado: gera tudo numa worktree temporária com as constantes trocadas e testa
os dois cenários de implantação: arquivos antigos ainda no projeto e arquivos antigos apagados.
Nada é escrito no checkout nem no Google.

    python revisao-b47/test_carregador.py --perfil base-v9
    python revisao-b47/test_carregador.py --perfil simulado-alvo
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import comum

ap = comum.argumentos(__doc__)
ap.add_argument('--manter', action='store_true', help='não apagar a worktree temporária')
args = ap.parse_args()
p = comum.perfil(args.perfil)
P = comum.Placar('carregador ' + args.perfil)
L = comum.linhas_analise(args.analise or comum.exportar(args.perfil, 'analise'))
chaves_arq = comum.SAIDAS / f'chaves-{args.perfil}.json'
chaves_arq.write_text(json.dumps([l[0] for l in L], ensure_ascii=False), encoding='utf-8')
print(f'SHA {comum.sha()} · perfil {args.perfil} · {len(L)} chaves esperadas\n')


def sonda(pasta, ignorar=()):
    r = subprocess.run(['node', str(comum.AQUI / 'sonda_carregador.js'), str(pasta), str(chaves_arq), *ignorar],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return json.loads(r.stdout)


def avalia(rotulo, s):
    P.check(f'{rotulo}: guarda de montar_() deixa construir', s['guarda'] == 'passa', s['guarda'])
    P.check(f'{rotulo}: ANALISE montada = contrato exportado (ordem e chaves)', s['mesmaOrdem'],
            f"{s['chaves']} chaves, {s['nRepetidas']} repetidas, {s['nObsoletas']} obsoletas, {s['nFaltam']} faltando; "
            f"ex. obsoletas {s['obsoletas'][:2]}")
    P.check(f'{rotulo}: nenhum valor além da grade declarada', not s['alemDaGrade'], s['alemDaGrade'][:3])


extra = {}
if not p['trocas']:
    s = sonda(comum.RAIZ / 'apps-script')
    extra['real'] = s
    avalia('versionados', s)
else:
    tmp = Path(tempfile.mkdtemp(prefix='revisao-b47-'))
    wt = tmp / 'wt'
    subprocess.run(['git', 'worktree', 'add', '-q', '--detach', str(wt), 'HEAD'], cwd=comum.RAIZ, check=True)
    try:
        # O emissor reescreve todo arquivo que produz; o que ficar com mtime 0 é sobra.
        for f in (wt / 'apps-script').glob('*.gs'):
            os.utime(f, (0, 0))
        inicio = 1
        r = subprocess.run([comum.python(), str(comum.AQUI / 'rodar_gerador.py'), str(wt), json.dumps(p['trocas'])],
                           cwd=wt, capture_output=True, text=True)
        P.check('geração completa simulada termina', r.returncode == 0, (r.stdout + r.stderr)[-500:])
        pasta = wt / 'apps-script'
        velhos = sorted(f.name for f in pasta.glob('*.gs') if f.stat().st_mtime < inicio
                        and f.name not in ('Codigo.gs', 'Habilidades.gs'))
        extra['nao_regenerados'] = velhos
        P.check('gerador não deixa .gs de geração anterior na pasta', not velhos, velhos)
        s1 = sonda(pasta)
        avalia('projeto com arquivos antigos', s1)
        s2 = sonda(pasta, velhos)
        avalia('projeto sem arquivos antigos', s2)
        extra.update(com_antigos=s1, sem_antigos=s2,
                     tamanhos={f.name: f.stat().st_size for f in sorted(pasta.glob('*.gs'))})
    finally:
        if not args.manter:
            subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=comum.RAIZ)
            shutil.rmtree(tmp, ignore_errors=True)
P.fim(extra)
