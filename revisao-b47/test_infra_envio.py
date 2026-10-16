# -*- coding: utf-8 -*-
"""Ferramenta de envio do chat 3 (infra-b47/apps_script.py) diante da redução (achado A1).

Lê a ferramenta de um ref Git (padrão origin/codex/b47-infra) para uma pasta temporária e a
executa offline, com um snapshot remoto FALSO montado dos .gs versionados da base (23 arquivos
+ appsscript.json). Nada vai ao Google.

  E1  redução simulada SEM o patch do carregador: a pasta local guarda PecasAnalise2-4 velhos.
      O pacote não deve levá-los ao projeto.
  E2  redução simulada COM patches/carregador-selo-de-geracao.diff: a pasta local está certa e o
      projeto remoto ainda tem PecasAnalise2-4. Precisa existir um caminho explícito e
      registrado para retirá-los (a guarda atual só bloqueia).

    python revisao-b47/test_infra_envio.py [--ref origin/codex/b47-infra]
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import comum

ap = comum.argumentos(__doc__, padrao='simulado-alvo')
ap.add_argument('--ref', default='origin/codex/b47-infra')
ap.add_argument('--com-patch-infra', action='store_true', help='aplica patches/infra-remover-explicito.diff à cópia da ferramenta')
args = ap.parse_args()
p = comum.perfil(args.perfil)
P = comum.Placar('infra envio ' + args.perfil + (' com patch' if args.com_patch_infra else ''))
ref_sha = subprocess.check_output(['git', 'rev-parse', args.ref], cwd=comum.RAIZ, text=True).strip()
print(f'SHA revisado {comum.sha()} · ferramenta {args.ref} = {ref_sha}\n')

tmp = Path(tempfile.mkdtemp(prefix='revisao-b47-infra-'))
ferramenta = tmp / 'infra-b47' / 'apps_script.py'
ferramenta.parent.mkdir(parents=True)
ferramenta.write_bytes(subprocess.check_output(['git', 'show', f'{ref_sha}:infra-b47/apps_script.py'], cwd=comum.RAIZ))
if args.com_patch_infra:
    subprocess.run(['patch', '-s', '-p1', '-i', str(comum.AQUI / 'patches' / 'infra-remover-explicito.diff')], cwd=tmp, check=True)
SCRIPT_ID = 'PROJETO_DE_TESTE_REVISAO'
remoto = tmp / 'remoto-antes.json'
arquivos = [{'name': f.stem, 'type': 'SERVER_JS', 'source': f.read_text(encoding='utf-8')}
            for f in sorted((comum.RAIZ / 'apps-script').glob('*.gs'))]
arquivos.append({'name': 'appsscript', 'type': 'JSON', 'source': '{"timeZone": "America/Sao_Paulo"}'})
remoto.write_text(json.dumps({'scriptId': SCRIPT_ID, 'files': arquivos}, ensure_ascii=False), encoding='utf-8')


def preparar(pasta, saida, extra=()):
    return subprocess.run([comum.python(), str(ferramenta), 'preparar', '--fontes', str(pasta), '--snapshot', str(remoto),
                           '--script-id', SCRIPT_ID, '--saida', str(saida), *extra], capture_output=True, text=True)


def gerar(wt):
    for f in (wt / 'apps-script').glob('*.gs'):
        os.utime(f, (0, 0))
    r = subprocess.run([comum.python(), str(comum.AQUI / 'rodar_gerador.py'), str(wt), json.dumps(p['trocas'])],
                       cwd=wt, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit((r.stdout + r.stderr)[-2000:])
    pasta = wt / 'apps-script'
    return sorted(f.stem for f in pasta.glob('PecasAnalise*.gs') if f.stat().st_mtime > 1)


wt = tmp / 'wt'
subprocess.run(['git', 'worktree', 'add', '-q', '--detach', str(wt), 'HEAD'], cwd=comum.RAIZ, check=True)
try:
    # E1: sem patch
    produzidos = gerar(wt)
    r = preparar(wt / 'apps-script', tmp / 'pacote-e1.json')
    P.check('E1: preparar aceita a pasta gerada', r.returncode == 0, r.stderr)
    if r.returncode == 0:
        nomes = {f['name'] for f in json.loads((tmp / 'pacote-e1.json').read_text())['files']}
        velhos = sorted(n for n in nomes if n.startswith('PecasAnalise') and n not in produzidos)
        P.check('E1: pacote não leva PecasAnalise que a geração atual não produziu', not velhos,
                f'gerados {produzidos}; pacote leva também {velhos} (sobras da pasta, ver A1)')
    # E2: com patch do carregador
    subprocess.run(['git', 'checkout', '-q', '--', '.'], cwd=wt, check=True)
    subprocess.run(['git', 'apply', str(comum.AQUI / 'patches' / 'carregador-selo-de-geracao.diff')], cwd=wt, check=True)
    produzidos = gerar(wt)
    locais = sorted(f.stem for f in (wt / 'apps-script').glob('*.gs'))
    r = preparar(wt / 'apps-script', tmp / 'pacote-e2.json')
    P.check('E2: com remotos obsoletos a guarda bloqueia (comportamento desejado)', r.returncode != 0 and
            'ausentes localmente' in r.stderr, r.stderr.strip())
    ajuda = subprocess.run([comum.python(), str(ferramenta), 'preparar', '--help'], capture_output=True, text=True).stdout
    P.check('E2: existe opção explícita para retirar remotos nomeados (ex.: --remover)', 'remov' in ajuda.lower(),
            'preparar não oferece remoção explícita; o integrador teria de editar o pacote à mão', nivel='risco')
    extras = sorted(f['name'] for f in arquivos if f['type'] == 'SERVER_JS' and f['name'] not in locais)
    P.check('E2: os remotos bloqueados são exatamente as sobras previstas', extras == ['PecasAnalise2', 'PecasAnalise3',
                                                                                         'PecasAnalise4'], extras)
    if args.com_patch_infra:
        rem = [x for n in extras for x in ('--remover', n)]
        r = preparar(wt / 'apps-script', tmp / 'pacote-e3.json', rem)
        P.check('E3: --remover das três sobras gera o pacote', r.returncode == 0 and 'Removidos' in r.stderr, r.stderr)
        if r.returncode == 0:
            pacote = json.loads((tmp / 'pacote-e3.json').read_text())
            nomes = sorted(f['name'] for f in pacote['files'])
            P.check('E3: pacote = arquivos gerados + appsscript, sem as sobras', nomes == sorted(locais + ['appsscript']),
                    sorted(set(nomes) ^ set(locais + ['appsscript'])))
            montado = tmp / 'montado'
            montado.mkdir()
            for f in pacote['files']:
                if f['type'] == 'SERVER_JS':
                    (montado / (f['name'] + '.gs')).write_text(f['source'], encoding='utf-8')
            chaves = comum.SAIDAS / f'chaves-{args.perfil}.json'
            chaves.write_text(json.dumps([l[0] for l in comum.linhas_analise(comum.exportar(args.perfil, 'analise'))],
                                         ensure_ascii=False), encoding='utf-8')
            s = json.loads(subprocess.check_output(['node', str(comum.AQUI / 'sonda_carregador.js'), str(montado), str(chaves)]))
            P.check('E3: projeto resultante constrói e monta a ANALISE = contrato', s['guarda'] == 'passa' and s['mesmaOrdem'],
                    s['guarda'])
        r = preparar(wt / 'apps-script', tmp / 'pacote-e4.json', ['--remover', 'Codigo'] + rem)
        P.check('E3: --remover recusa arquivo que existe localmente', r.returncode != 0 and 'só aceita' in r.stderr, r.stderr)
        r = preparar(wt / 'apps-script', tmp / 'pacote-e5.json', rem[:2])
        P.check('E3: remover só uma sobra ainda bloqueia as outras', r.returncode != 0 and 'PecasAnalise3' in r.stderr, r.stderr)
        shutil.copy(comum.RAIZ / 'apps-script' / 'PecasAnalise3.gs', wt / 'apps-script' / 'PecasAnalise3.gs')
        r = preparar(wt / 'apps-script', tmp / 'pacote-e6.json', rem)
        P.check('E3: sobra local recolocada é recusada pelo selo do Ficha.gs', r.returncode != 0 and 'Sobras locais' in r.stderr,
                r.stderr)
finally:
    subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=comum.RAIZ)
    shutil.rmtree(tmp, ignore_errors=True)
P.fim(dict(ref=args.ref, ref_sha=ref_sha))
