"""Reexecuta os 13 cenários/expectativas originais de Famílias no Sheets."""
import ast
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);sys.path.insert(0,str(ROOT))
SOURCE=ROOT/'regressao-familias-invocacao.py'
helpers=runpy.run_path(str(ROOT/'acabamento-b47/regressao-pessoal-nativa.py'))


def preparar(folder):
    source=SOURCE.read_text(encoding='utf-8');tree=ast.parse(source)
    end=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.With))
    nodes=[]
    for n in tree.body[:end]:
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='subprocess.run':continue
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pack' for t in n.targets):
            n.value=ast.parse("EVID/'progressao-em-integracao.json'",mode='eval').body
        nodes.append(n)
    e={'__file__':str(SOURCE),'__name__':'familias_nativa'}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(SOURCE),'exec'),e)
    expected_ast=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and
                      any(isinstance(t,ast.Name) and t.id=='expected' for t in n.targets))
    cases=[]
    for name,values,mode,trail,maximum,livres,count,duplicates,opened,price,overrides in e['scenarios']:
        edits={('DADOS_INVOC','DB4'):trail,('INVOCAÇÕES','K50'):mode,('INVOCAÇÕES','K248'):'Autônoma'}
        edits.update({('CONFIGURAÇÃO','F'+str(row)):overrides.get(row,e['raw']['CONFIGURAÇÃO'].get('F'+str(row))) for row in range(139,146)})
        edits.update({('DADOS_INVOC',e['col'](e['fields'][field])+'2'):value for field,value in
                      [('ficha',1),('lf',e['cura']-1),('w1',2),('f1','Amparo'),('classe',1)]})
        edits.update({('INVOCAÇÕES',coord):value for coord,value in zip(e['familias'],values)})
        e.update(locals())
        exec(compile(ast.Module(body=[expected_ast],type_ignores=[]),str(SOURCE),'exec'),e)
        cases.append({'nome':name,'entradas':[[s,c,v] for (s,c),v in edits.items()],'esperado':e['expected']})
    inputs={(s,c) for case in cases for s,c,v in case['entradas']}
    plan={'fonte':SOURCE.name,'sha256_teste':hashlib.sha256(source.encode()).hexdigest(),
          'sha256_pacote':hashlib.sha256((ROOT/'nuvem-b47/saidas/progressao-em-integracao.json').read_bytes()).hexdigest(),
          'cenarios':cases,'entradas':[[s,c,e['raw'][s].get(c)] for s,c in sorted(inputs)],
          'faixas_entrada':helpers['ranges'](inputs),
          'faixas_saida':helpers['ranges']({('DADOS_INVOC',c) for c in e['targets']}),
          'alvos':e['targets'],'checagens_estruturais':e['checks']}
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'plano-familias.json').write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'cenarios':len(cases),'estrutura':e['checks']},ensure_ascii=False))


def conferir(folder):
    plan=json.loads((folder/'plano-familias.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==plan['sha256_teste']
    fails=[]
    for i,case in enumerate(plan['cenarios']):
        data=json.loads((folder/f'familias-{i:02}.json').read_text(encoding='utf-8'))
        assert not data.get('isError');values={}
        for s in data['structuredContent']['sheets']:
            for b in s.get('data',[]):
                for r,row in enumerate(b.get('rowData',[]),b.get('startRow',0)+1):
                    for c,cell in enumerate(row.get('values',[]),b.get('startColumn',0)+1):
                        v=cell.get('effectiveValue',{});val=v.get('numberValue',v.get('boolValue',v.get('stringValue')))
                        if 'errorValue' in v:val=v['errorValue']
                        values[helpers['get_column_letter'](c)+str(r)]=None if val=='' else val
        actual=[values.get(c) for c in plan['alvos']]
        ok=actual==case['esperado']
        print(('OK ' if ok else 'FALHA ')+case['nome'],flush=True)
        if not ok:
            print('obtido',actual,'esperado',case['esperado'],flush=True);fails.append(case['nome'])
    print('FAMÍLIAS NATIVAS: '+str(len(fails))+' falhas')
    sys.exit(bool(fails) or not all(plan['checagens_estruturais']))


if __name__=='__main__':
    {'preparar':preparar,'conferir':conferir}[sys.argv[1]](Path(sys.argv[2]))
