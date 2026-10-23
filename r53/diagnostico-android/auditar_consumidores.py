"""Complementa dependências com validações, formatação e INDIRECT nativos."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import get_column_letter as L, range_boundaries
from revisar import english

PRIVATE=Path(sys.argv[1])
HERE=Path(__file__).resolve().parent
report=json.loads((HERE/'RECONCILIACAO-2026-10-23.json').read_text())
extras=defaultdict(dict)
for i in report['adicionais']['celulas']:
    c,r,_,_=range_boundaries(i['celula']);extras[i['aba']][i['celula']]=(c,r)

hits=[];fd=[];analise=[];unknown=[];indirect=[];rules=[]
def inspect(expr,owner,address,kind):
    if not expr.startswith('='):return
    if 'INDIRECT(' in expr:
        indirect.append({'aba':owner,'celula':address,'tipo':kind,'monta_endereco':bool(re.search(r'INDIRECT\([^)]*&',expr))})
    try:tokens=Tokenizer(english(expr)).items
    except Exception as e:raise ValueError((owner,address,kind)) from e
    for t in tokens:
        if t.type!='OPERAND':continue
        if t.subtype=='RANGE':value=t.value
        elif t.subtype=='TEXT' and 'INDIRECT(' in expr:
            value=t.value[1:-1].replace('""','"')
            if '!' not in value:continue
        else:continue
        prefix,sep,coords=value.rpartition('!')
        sheet=prefix.strip("'").replace("''", "'") if sep else owner
        try:c,r,cc,rr=range_boundaries(coords)
        except ValueError:
            # São candidatos dinâmicos/nomes, não referências resolvidas.
            if kind!='formula' or 'INDIRECT(' in expr:
                unknown.append({'aba':owner,'celula':address,'tipo':kind,'referencia':value})
            continue
        entry={'aba':owner,'celula':address,'tipo':kind,'destino':sheet,'intervalo':coords}
        if sheet=='DADOS_R53' and (c or 1)<=160<=(cc or 183):fd.append(entry)
        if sheet=='ANALISE':analise.append(entry)
        for cell,(ec,er) in extras.get(sheet,{}).items():
            if (c or 1)<=ec<=(cc or 100000) and (r or 1)<=er<=(rr or 1000000):
                hits.append({**entry,'adicional':cell})

for path in sorted((PRIVATE/'validacoes').glob('*.json')):
    for s in json.loads(path.read_text()).get('sheets',[]):
        for d in s.get('data',[]):
            for r,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
                for c,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):
                    rule=cell.get('dataValidation')
                    if not rule:continue
                    owner=s['properties']['title'];address=L(c)+str(r);rules.append(rule)
                    for v in rule['condition'].get('values',[]):inspect(v.get('userEnteredValue',''),owner,address,'validacao')

cf_count=0
for s in json.loads((PRIVATE/'metadata-revisao.json').read_text())['sheets']:
    for i,rule in enumerate(s.get('conditionalFormats',[])):
        cf_count+=1
        condition=rule.get('booleanRule',{}).get('condition',{})
        for v in condition.get('values',[]):inspect(v.get('userEnteredValue',''),s['properties']['title'],'CF'+str(i),'condicional')

live=json.loads((PRIVATE/'formulas-nativas-normalizadas.json').read_text())
indirect_forms=[]
for s,cells in live.items():
    for cell,formula in cells.items():
        if 'INDIRECT(' in formula:
            inspect(formula,s,cell,'formula')
            # Apenas nomes de abas literais, sem publicar entradas reais.
            indirect_forms.append({'aba':s,'celula':cell,'abas_mencionadas':[n for n in live if re.search(r"(?<![A-Za-z0-9_])'?"+re.escape(n)+r"'?!",formula)]})

result=dict(celulas_com_validacao=len(rules),condicoes=dict(Counter(r['condition']['type'] for r in rules)),
    regras_condicionais=cf_count,referencias_adicionais=hits,referencias_FD=fd,referencias_ANALISE=analise,
    formulas_INDIRECT=indirect_forms,referencias_nao_resolvidas=unknown,
    limites=['Não inclui nomes/proteções que o conector não expôs nem consumidores externos',
             'INDIRECT com concatenação não é resolvido por execução simbólica',
             'Código remoto Apps Script ainda precisa de leitura atual'])
(HERE/'DEPENDENCIAS-2026-10-23.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in result.items() if k!='limites'},ensure_ascii=False))
