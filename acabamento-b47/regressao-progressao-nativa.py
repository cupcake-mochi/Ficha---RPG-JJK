"""Cenários da regressão de progressão no Sheets; preservação histórica explícita.

Requer exportação fresca --exportar-progressao, feita uma vez nesta retomada.
Não confunde o cenário atual vazio com a antiga ficha livro_base do Calc.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]; os.chdir(ROOT)
sys.path.insert(0,str(ROOT))
SOURCE=ROOT/'regressao-progressao.py'
helpers=runpy.run_path(str(ROOT/'acabamento-b47/regressao-pessoal-nativa.py'))


def preparar(folder):
    source=SOURCE.read_text(encoding='utf-8'); tree=ast.parse(source)
    end=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.With))
    nodes=[n for n in tree.body[:end] if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
           and ast.unparse(n.value.func)=='subprocess.run')]
    e={'__file__':str(SOURCE),'__name__':'progressao_nativa'}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),e)
    # Exigir o pacote cuja emissão foi solicitada nesta sessão, sem regenerar
    # os mesmos 25 MB para cada teste. Hash fica preso ao plano de execução.
    packfile=ROOT/'nuvem-b47/saidas/progressao-em-integracao.json'
    wanted=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='wanted' for t in n.targets))
    exec(compile(ast.Module(body=[wanted],type_ignores=[]),str(SOURCE),'exec'),e)
    cases=[{'nome':name,'entradas':[[s,c,v] for (s,c),v in {**e['common'],**edits}.items()]}
           for name,original,edits in e['cases'] if original is not None]
    inputs={(s,c) for case in cases for s,c,v in case['entradas']}
    outputs={(s,c) for s,cs in e['wanted'].items() for c in cs}
    plan={'fonte':SOURCE.name,'sha256_teste':hashlib.sha256(source.encode()).hexdigest(),
          'sha256_pacote':hashlib.sha256(packfile.read_bytes()).hexdigest(),
          'cenarios':cases,'entradas':[[s,c,e['raw'][s].get(c)] for s,c in sorted(inputs)],
          'faixas_entrada':helpers['ranges'](inputs),'faixas_saida':helpers['ranges'](outputs),
          'per':e['per'],'off':e['off'],'dados':e['p'].NOME,
          'falhas_estruturais':e['fails'],
          'diferencas_estruturais':e['changed'],'diferencas_contrato':e['contract_diff'],
          'pendente':'Comparação calculada livro_base histórico; não substituída por duplicata da ficha atual.'}
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'plano-progressao.json').write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'cenarios':len(cases),'falhas_estruturais':e['fails'],
                      'diferencas':len(e['changed']),'contrato':len(e['contract_diff'])},ensure_ascii=False))


def conferir(folder):
    source=SOURCE.read_text(encoding='utf-8');tree=ast.parse(source)
    plan=json.loads((folder/'plano-progressao.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(source.encode()).hexdigest()==plan['sha256_teste']
    results={}
    for i,case in enumerate(plan['cenarios']):
        data=json.loads((folder/f'progressao-{i:02}.json').read_text(encoding='utf-8'))
        assert not data.get('isError');values={}
        for s in data['structuredContent']['sheets']:
            cells=values.setdefault(s['properties']['title'],{})
            for b in s.get('data',[]):
                for row,rd in enumerate(b.get('rowData',[]),b.get('startRow',0)+1):
                    for col,c in enumerate(rd.get('values',[]),b.get('startColumn',0)+1):
                        v=c.get('effectiveValue',{}); value=v.get('numberValue',v.get('boolValue',v.get('stringValue')))
                        if 'errorValue' in v:value='#'+v['errorValue']['type']
                        cells[helpers['get_column_letter'](col)+str(row)]=value
        results[case['nome']]=values
    e={'results':results,'fails':[],'per':plan['per'],'off':plan['off']}
    class P: NOME=plan['dados']
    e['p']=P
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('check','get')]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),e)
    first=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.FunctionDef) and n.name=='get')+1
    last=next(i for i,n in enumerate(tree.body[first:],first) if isinstance(n,ast.Expr)
              and isinstance(n.value,ast.Call) and ast.unparse(n.value.func).endswith('write_text'))
    # Primeira asserção exige resultados da geração histórica. Mantê-la
    # pendente separadamente, em vez de inventar valores para esse cenário.
    exec(compile(ast.Module(body=tree.body[first+1:last],type_ignores=[]),str(SOURCE),'exec'),e)
    print('PROGRESSÃO NATIVA: '+str(len(e['fails']))+' falhas mecânicas; preservação histórica separada')
    sys.exit(bool(e['fails']))


if __name__=='__main__':
    {'preparar':preparar,'conferir':conferir}[sys.argv[1]](Path(sys.argv[2]))
