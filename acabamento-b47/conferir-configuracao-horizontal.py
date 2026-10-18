"""Compara snapshots nativos antes/depois; nenhuma escrita ou acesso à rede."""
import argparse,json,re,sys
from pathlib import Path
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import get_column_letter as L,range_boundaries
ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47')]
import configuracao_horizontal as h
from lotes import native_value,pt

def load(path):
    d=json.loads(Path(path).read_text(encoding='utf-8-sig'));return d.get('structuredContent',d)

def cells(d):
    out={}
    for s in d['sheets']:
        for grid in s.get('data',[]):
            for y,row in enumerate(grid.get('rowData',[])):
                for x,c in enumerate(row.get('values',[])):
                    out[s['properties']['title'],L(x+grid.get('startColumn',0)+1)+str(y+grid.get('startRow',0)+1)]=c
    return out

def equivalent(v):
    if 'formulaValue' not in v:return v
    # Sheets remove aspas opcionais de nomes simples de abas ao salvar.
    # Normalizar somente tokens RANGE, nunca textos entre aspas da fórmula.
    tokens=Tokenizer(v['formulaValue']).items
    for t in tokens:
        if t.type=='OPERAND' and t.subtype=='RANGE':
            t.value=re.sub(r"^'([A-Za-z_][A-Za-z_0-9]*)'!",r'\1!',t.value)
            t.value=re.sub(r'(!?\$?[A-Z]+\$?\d+):\1$',r'\1',t.value)
    return {'formulaValue':'='+''.join(t.value for t in tokens)}

def run(args):
    target=load(args.alvo);a=next(x for x in target['layout']['abas'] if x['nome']=='CONFIGURAÇÃO')
    source=cells(load(args.antes));actual=cells(load(args.depois));values={x[0]:x[1] for x in a['celulas']}
    presentation=set()
    for region in a['apresentacao']:
        c,r,cc,rr=range_boundaries(region)
        presentation.update(L(x)+str(y) for y in range(r,rr+1) for x in range(c,cc+1))
    fields=[];count=0
    for (_,addr),cell in source.items():
        v=cell.get('userEnteredValue',{})
        if not v:continue
        dest=h.coord(addr)
        if dest in presentation:continue
        expected=native_value(values[dest]) if 'formulaValue' in v else v
        if equivalent(expected)!=equivalent(actual.get(('CONFIGURAÇÃO',dest),{}).get('userEnteredValue',{})):fields.append(dict(de=addr,para=dest))
        count+=1
    notes={addr:c['note'] for (s,addr),c in actual.items() if c.get('note')}
    note_diffs=sorted(x for x in set(notes)|set(a['notas']) if notes.get(x)!=a['notas'].get(x))
    # Preservar todas as validações nativas, incluindo caixas de seleção.
    # O XLSX também declara validações custom que não são menus do Google;
    # não inventar uma mudança nelas durante uma revisão de apresentação.
    menus={}
    for (_,addr),cell in source.items():
        if cell.get('dataValidation'):
            rule=json.loads(json.dumps(cell['dataValidation']))
            for v in rule['condition'].get('values',[]):
                if v.get('userEnteredValue','').startswith('='):v['userEnteredValue']=h.formula(v['userEnteredValue'],'CONFIGURAÇÃO')
            menus[h.coord(addr)]=rule
    menu_diffs=[]
    for addr,rule in menus.items():
        actual_rule=actual.get(('CONFIGURAÇÃO',addr),{}).get('dataValidation',{})
        got=actual_rule.get('condition',{});condition=rule['condition']
        def norm(c):return(c.get('type'),[equivalent({'formulaValue':v['userEnteredValue']}) if v['userEnteredValue'].startswith('=') else v for v in c.get('values',[])])
        if norm(got)!=norm(condition) or any(bool(actual_rule.get(k))!=bool(rule.get(k)) for k in ['strict','showCustomUi']):menu_diffs.append(addr)
    menu_diffs.extend(addr for (sheet,addr),c in actual.items() if c.get('dataValidation') and addr not in menus)
    before=cells(load(args.analise_antes));after=cells(load(args.analise_depois));value_diffs=[];origin_diffs=[]
    for key,c in before.items():
        column=re.match('[A-Z]+',key[1])[0];v=c.get('effectiveValue',{});got=after.get(key,{}).get('effectiveValue',{})
        if column in ('A','B') and got!=v:value_diffs.append(key[1])
        if column=='C':
            expected={k:h.formula(t,'ANALISE') if isinstance(t,str) else t for k,t in v.items()}
            if got!=expected:origin_diffs.append(key[1])
    errors=[addr for (_,addr),c in actual.items() if c.get('effectiveValue',{}).get('errorValue')]
    report=dict(campos_conferidos=count,diferencas_campos=fields,menus_conferidos=len(menus),diferencas_menus=menu_diffs,notas=len(notes),diferencas_notas=note_diffs,diferencas_valores=value_diffs,diferencas_origens=origin_diffs,erros_configuracao=errors)
    report['resultado']='OK' if not any(v for k,v in report.items() if k.startswith(('diferencas','erros'))) else 'FALHOU'
    Path(args.saida).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False));return report['resultado']=='OK'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['antes','depois','alvo','analise-antes','analise-depois','saida']:p.add_argument('--'+n,required=True)
    sys.exit(0 if run(p.parse_args()) else 1)
