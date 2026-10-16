# -*- coding: utf-8 -*-
"""Mecânica de Melhorias/Restrições na capacidade do perfil, pelo próprio regressao-pecas.py.

Copia regressao-pecas.py (do integrador) para uma pasta temporária, troca só os literais da
capacidade atual (789, 395, linha 396) pelas constantes e o executa num processo em que as
constantes do perfil já estão aplicadas. Recalcula no LibreOffice; nada vai ao Google.

As checagens que contam o contrato do formato 9 (789/395, 9.082/18.948 chaves) não se aplicam a
uma capacidade reduzida e são separadas. Todas as outras (herança, criação do zero, curingas,
repetidos, Classe 0, nona Família da entidade, primeira/última vaga) têm de passar.

    python revisao-b47/test_pecas_capacidade.py --perfil base-v9        # calibração: = original
    python revisao-b47/test_pecas_capacidade.py --perfil simulado-alvo
"""
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import comum

ap = comum.argumentos(__doc__)
args = ap.parse_args()
p = comum.perfil(args.perfil)
P = comum.Placar('pecas capacidade ' + args.perfil)
modelo = comum.exportar(args.perfil, 'pecas')
anterior = comum.RAIZ / 'nuvem-b47' / 'saidas' / 'pecas-modelo-anterior.json'
if not anterior.exists():
    subprocess.run([comum.python(), str(comum.RAIZ / 'nuvem-b47' / 'exportar-baseline.py')], cwd=comum.RAIZ, check=True,
                   capture_output=True)
ESTRUTURAIS = {'capacidade cobre todas as escolhas atuais', '9082 chaves anteriores com fontes e posições preservadas',
               '9866 chaves novas, sem duplicatas'}

origem = (comum.RAIZ / 'regressao-pecas.py').read_text(encoding='utf-8')
trocas = [("ROOT=Path(__file__).resolve().parent", f"ROOT=Path({str(comum.RAIZ)!r})"),
          ("reg('melhoria',789,", "reg('melhoria',cp.MELHORIAS,"),
          ("reg('restricao',395,", "reg('restricao',cp.RESTRICOES,"),
          ("for n in [1,2,3,4,5,6,7,8,9,17,789]:", "for n in [1,2,3,4,5,6,7,8,9,17,cp.MELHORIAS]:"),
          ("'N'+str(mr+396)", "'N'+str(mr+cp.RESTRICOES+1)"),
          ("[('melhoria',789),('restricao',395)]", "[('melhoria',cp.MELHORIAS),('restricao',cp.RESTRICOES)]")]
faltam = [a for a, _ in trocas if a not in origem]
if len(faltam) == len(trocas) - 1:   # a troca de ROOT sempre existe
    print('INFO  regressao-pecas.py deste SHA já é parametrizado: executado sem trocas')
else:
    P.check('literais conhecidos encontrados no regressao-pecas.py deste SHA', not faltam, faltam)
for a, b in trocas:
    origem = origem.replace(a, b)
restantes = sorted(set(re.findall(r'\b(789|395|396|1184)\b', origem)))
P.check('nenhum literal da capacidade antiga nos cenários', set(restantes) <= {'1184', '395', '789'},
        restantes, nivel='risco')

tmp = Path(tempfile.mkdtemp(prefix='revisao-b47-pecas-'))
try:
    copia = tmp / 'regressao_pecas_parametrizada.py'
    copia.write_text(origem, encoding='utf-8')
    executor = tmp / 'executa.py'
    executor.write_text(
        'import json, runpy, sys\n'
        f'sys.path[:0] = [{str(comum.RAIZ / "ficha-v01")!r}, {str(comum.RAIZ / "ficha")!r}, {str(comum.RAIZ)!r}]\n'
        f'for alvo, valor in json.loads({json.dumps(json.dumps(p["trocas"]))}).items():\n'
        '    m, n = alvo.rsplit(".", 1); setattr(__import__(m), n, valor)\n'
        f'sys.argv = ["regressao-pecas.py", "--modelo", {str(modelo)!r}, "--anterior", {str(anterior)!r}, '
        f'"--evidencia", {str(tmp / "evidencia.json")!r}]\n'
        f'runpy.run_path({str(copia)!r}, run_name="__main__")\n', encoding='utf-8')
    r = subprocess.run([comum.python(), str(executor)], cwd=comum.RAIZ, capture_output=True, text=True, timeout=1800)
    ev = tmp / 'evidencia.json'
    if not ev.exists():
        P.check('regressão parametrizada terminou com evidência', False, (r.stdout + r.stderr)[-1500:])
        P.fim()
    checks = json.loads(ev.read_text(encoding='utf-8'))['checagens']
finally:
    shutil.rmtree(tmp, ignore_errors=True)

mec = [c for c in checks if c['teste'] not in ESTRUTURAIS]
for c in checks:
    if c['teste'] in ESTRUTURAIS:
        if (p['catalogos']['melhoria']['capacidade'], p['catalogos']['restricao']['capacidade']) != (789, 395):
            print(f"N/A   [contrato v9, não se aplica à capacidade do perfil] {c['teste']}: "
                  + ('passou' if c['ok'] else 'falhou, como esperado'))
        else:
            P.check(f"[contrato v9] {c['teste']}", c['ok'], c['detalhe'])
    else:
        P.check(c['teste'], c['ok'], c['detalhe'])
P.fim(dict(perfil=args.perfil, mecanicas=len(mec), mecanicas_ok=sum(c['ok'] for c in mec)))
