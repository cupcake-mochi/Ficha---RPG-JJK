"""Compara os resultados completos antigos/atuais, listando toda diferença."""
import json
import math
from pathlib import Path
import sys
from openpyxl.utils import get_column_letter as L
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'capacidade-b47'))
from contratos_historicos import classificar_vazio


def plano(kind,folder):
    old=json.loads((folder/f'historico-{kind}.json').read_text(encoding='utf-8'))
    assert not old['diferencas']
    chunks=[]
    for sheet in old['abas']:
        if sheet['nome'] in ('CONFIGURAÇÃO','ANALISE') or kind=='campanha' and sheet['nome']=='DADOS_CONFIG':continue
        rows,cols=sheet['rows'],sheet['cols'];step=max(1,7000//cols)
        for r in range(1,rows+1,step):
            chunks.append(f"'{sheet['nome']}'!A{r}:{L(cols)}{min(rows,r+step-1)}")
    (folder/f'comparacao-{kind}-plano.json').write_text(json.dumps({'faixas':chunks},ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'tipo':kind,'blocos':len(chunks)},ensure_ascii=False))


def ler(folder):
    cells={};errors=[]
    for path in sorted(folder.glob('*.json')):
        raw=json.loads(path.read_text(encoding='utf-8'))
        assert not raw.get('isError')
        for sheet in raw['structuredContent']['sheets']:
            values=cells.setdefault(sheet['properties']['title'],{})
            for b in sheet.get('data',[]):
                for r,row in enumerate(b.get('rowData',[]),b.get('startRow',0)+1):
                    for c,cell in enumerate(row.get('values',[]),b.get('startColumn',0)+1):
                        v=cell.get('effectiveValue',{})
                        value=v.get('numberValue',v.get('boolValue',v.get('stringValue')))
                        if 'errorValue' in v:
                            value='#'+v['errorValue']['type'];errors.append([sheet['properties']['title'],L(c)+str(r),v['errorValue']])
                        if value not in (None,''):values[L(c)+str(r)]=value
    return cells,errors


def conferir(kind,folder):
    before,eb=ler(folder/f'{kind}-base');after,ea=ler(folder/f'{kind}-vazia')
    dif=[]
    for sheet,values in before.items():
        for cell,b in values.items():
            a=after.get(sheet,{}).get(cell)
            same=math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else a==b
            if not same:dif.append([sheet,cell,b,a])
    print('DIFERENÇAS COMPLETAS '+kind.upper()+': '+json.dumps(dif,ensure_ascii=False),flush=True)
    classified,pending=classificar_vazio(dif,lambda s,c:after.get(s,{}).get(c))
    report={'referencia':kind,'celulas_anteriores':sum(map(len,before.values())),
            'erros_base':eb,'erros_atual':ea,'diferencas_completas':dif,
            'classificadas':classified,'pendentes':pending,'classificado':not pending and not eb and not ea}
    (folder/f'comparacao-{kind}-resultado.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'celulas':report['celulas_anteriores'],'diferencas':len(dif),'classificadas':len(classified),'pendentes':len(pending),'erros_base':len(eb),'erros_atual':len(ea)}))
    sys.exit(not report['classificado'])


if __name__=='__main__':
    {'plano':plano,'conferir':conferir}[sys.argv[1]](sys.argv[2],Path(sys.argv[3]))
