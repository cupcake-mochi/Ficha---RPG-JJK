"""Requisições de teste nativo, geradas do mesmo modelo usado no produto."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from modelo import INPUTS,ARVORE,DEFAULTS,CAT,LOOKUP_FIELDS,formulas
from verificar import CASOS,BASE
from formulas import native,x
from formas_custom import CAMPOS as FORMA_CAMPOS
CAT_ABA='DADOS_R53_TESTES'
CAT_ID=53018005

def col(n):
    s=''
    while n: n,a=divmod(n-1,26);s=chr(a+65)+s
    return s

def cel(v):
    if isinstance(v,str) and v.startswith('='): return dict(userEnteredValue=dict(formulaValue=v))
    if isinstance(v,bool): return dict(userEnteredValue=dict(boolValue=v))
    if isinstance(v,(int,float)): return dict(userEnteredValue=dict(numberValue=v))
    return dict(userEnteredValue=dict(stringValue='' if v is None else str(v)))

def gerar():
    campos=INPUTS+list(ARVORE); cols={k:col(i+1) for i,k in enumerate(campos)}
    extras={}
    for caso in CASOS:
        for nome,v in caso.get('catalogo',{}).items():
            if nome in extras and extras[nome]!=v:raise ValueError('Catálogo de teste conflitante: '+nome)
            extras[nome]=v
    catrows=[LOOKUP_FIELDS]+[[v[k] for k in LOOKUP_FIELDS] for v in CAT['opcoes']+list(extras.values())]
    catalog_end=len(catrows)
    familias=sorted({f for caso in CASOS for f in caso.get('familias_custom',{})})
    family_start=20
    while len(catrows)<len(familias)+1:catrows.append([])
    for row in catrows:row.extend(['']*max(0,family_start+len(CASOS)-len(row)+1))
    for ri,fam in enumerate(['Família']+familias):
        catrows[ri][family_start-1]=fam
        for i,caso in enumerate(CASOS):catrows[ri][family_start+i]=caso['nome'] if ri==0 else caso.get('familias_custom',{}).get(fam,'Fechada')
    formas={}
    for caso in CASOS:
        for name,data in caso.get('formas',{}).items():
            if name in formas and formas[name]!=data:raise ValueError('Forma de teste conflitante: '+name)
            formas[name]=data
    forma_col=family_start+len(CASOS)+2
    for row in catrows:row.extend(['']*max(0,forma_col+len(FORMA_CAMPOS)-len(row)))
    for ri,row in enumerate([FORMA_CAMPOS]+[[data.get(k,0 if k in ['peso','classe_0','coletiva'] else '') if not k.startswith('medida_') else data.get('medidas',['']*84)[int(k[7:])] for k in FORMA_CAMPOS] for data in formas.values()]):
        catrows[ri][forma_col-1:forma_col-1+len(row)]=row
    forma_range=f"'{CAT_ABA}'!${col(forma_col)}$2:${col(forma_col+len(FORMA_CAMPOS)-1)}${max(2,len(formas)+1)}"
    rows=[campos+['caso','resultado esperado','confere']]
    for lin,caso in enumerate(CASOS,2):
        valores={**DEFAULTS,**BASE,**caso['entrada']}
        fun=formulas(lin,cols,f"'{CAT_ABA}'!$A$2:${col(len(LOOKUP_FIELDS))}${catalog_end}",separator=';',familias_range=f"'{CAT_ABA}'!$T$2:${col(family_start+len(CASOS))}${len(familias)+1}" if familias else None,familias_coluna=lin,formas_range=forma_range)
        expected=caso['esperado']
        checks=[]
        for k,v in expected.items():
            lit=native(x(v),{},'',[],separator=';')
            checks.append(cols[k]+str(lin)+'='+lit)
        for k,v in caso.get('contem',{}).items():checks.append('ISNUMBER(SEARCH('+native(x(v),{},'',[],separator=';')+';'+cols[k]+str(lin)+'))')
        for k,v in caso.get('nao_contem',{}).items():checks.append('NOT(ISNUMBER(SEARCH('+native(x(v),{},'',[],separator=';')+';'+cols[k]+str(lin)+')))')
        rows.append([valores[k] for k in INPUTS]+[fun[k] for k in ARVORE]+[caso['nome'],json.dumps(expected,ensure_ascii=False),'=AND('+(';'.join(checks))+')'])
    return [{'updateCells':{'start':{'sheetId':CAT_ID,'rowIndex':0,'columnIndex':0},'rows':[{'values':list(map(cel,r))} for r in catrows],'fields':'userEnteredValue'}},
            {'updateCells':{'start':{'sheetId':53018002,'rowIndex':0,'columnIndex':0},'rows':[{'values':list(map(cel,r))} for r in rows],'fields':'userEnteredValue'}}]

if __name__=='__main__':
    destino=Path(sys.argv[1]);destino.write_text(json.dumps(gerar(),ensure_ascii=False))
    Path(str(destino)+'.meta.json').write_text(json.dumps(dict(casos=len(CASOS),linhas=len(CASOS)+1,colunas=len(INPUTS)+len(ARVORE)+3,catalogo_aba=CAT_ABA,catalogo_id=CAT_ID,catalogo_colunas=20+len(CASOS)+2+len(FORMA_CAMPOS),inicio_resultados=col(len(INPUTS)+len(ARVORE)+1),fim=col(len(INPUTS)+len(ARVORE)+3))))
    print(f'{len(CASOS)} casos; {len(INPUTS)} entradas e {len(ARVORE)} resultados por caso. {destino.stat().st_size} bytes.')
