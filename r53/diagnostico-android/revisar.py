"""Auditoria offline do inventário privado; não escreve na ficha nem no gerador.

Uso: .venv/bin/python r53/diagnostico-android/revisar.py <diretorio-privado>
Relatório sanitizado em RECONCILIACAO-2026-10-23.json. As fórmulas ficam privadas.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import get_column_letter as L, range_boundaries

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'capacidade-b47'))
from migracao import canonical

TEXT = re.compile(r'("(?:[^"]|"")*")')
CELL = re.compile(r'(?<![A-Za-z0-9_.])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![A-Za-z0-9_(])')


def english(formula):
    """Converte pt_BR preservando linhas/colunas de matrizes e literais."""
    parts = TEXT.split(formula)
    # Um separador ; dentro de uma matriz inglesa não identifica pt_BR.
    paren = 0
    arrays = []
    native = False
    for i, part in enumerate(parts):
        if i % 2:
            continue
        for ch in part:
            if ch == '(': paren += 1
            elif ch == ')': paren -= 1
            elif ch == '{': arrays.append(paren)
            elif ch == '}': arrays.pop()
            elif ch == '\\' or (ch == ';' and not (arrays and arrays[-1] == paren)): native = True
    if not native:
        return formula
    paren = 0
    arrays = []
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            out.append(part)
            continue
        for j, ch in enumerate(part):
            if ch == '(': paren += 1
            elif ch == ')': paren -= 1
            elif ch == '{': arrays.append(paren)
            elif ch == '}': arrays.pop()
            if ch == '\\': ch = ','
            elif ch == ';' and not (arrays and arrays[-1] == paren): ch = ','
            elif ch == ',' and part[j-1:j].isdigit() and part[j+1:j+2].isdigit(): ch = '.'
            out.append(ch)
    return ''.join(out)


def normalized(formula, order_ranges=False):
    f = english(formula)
    result = []
    for t in Tokenizer(f).items:
        value = t.value
        if t.type == 'OPERAND' and t.subtype == 'NUMBER':
            value = str(Decimal(value).normalize())
        if t.type == 'OPERAND' and t.subtype == 'RANGE':
            value = re.sub(r"^'([A-Za-z_][A-Za-z0-9_]*)'!", r'\1!', value)
            # Apenas extremos literalmente iguais: não confundir A1 com $A$1.
            value = re.sub(r'(\$?[A-Z]+\$?\d+):\1$', r'\1', value)
            if order_ranges and ':' in value:
                prefix, _, coords = value.rpartition('!')
                m = re.fullmatch(r'(\$[A-Z]+\$)(\d+):(\$[A-Z]+\$)(\d+)', coords)
                if m and m[1] == m[3] and int(m[2]) > int(m[4]):
                    value = (prefix+'!' if prefix else '') + m[1]+m[4]+':'+m[3]+m[2]
        result.append((t.type, t.subtype, value))
    return result


def expand(tabs):
    out = {}
    for tab in tabs:
        cells = {(r,c): v for r,c,v,*_ in tab['vals']}
        for ra,ca,rb,cb in tab.get('abaixo', []):
            for c in range(ca, cb+1):
                template = cells[ra,c]
                for r in range(ra+1, rb+1):
                    cells[r,c] = ''.join(p if i%2 else CELL.sub(
                        lambda m: m[0] if m[3] else f'{m[1]}{m[2]}{int(m[4])+r-ra}', p)
                        for i,p in enumerate(TEXT.split(template)))
        out[tab['nome']] = {L(c)+str(r):v for (r,c),v in cells.items()}
    return out


def selfcheck():
    assert normalized('=SUM(A1:A1,15.0,1E99)') == normalized('=SUM(A1;15;1E+99)')
    assert normalized('=SPARKLINE(A1,{"charttype","bar";"max",2})') == normalized('=SPARKLINE(A1;{"charttype"\\"bar";"max"\\2})')
    assert normalized('=SPARKLINE(A1,{"max",MAX(1,B1)})') == normalized('=SPARKLINE(A1;{"max"\\MAX(1;B1)})')
    assert normalized('=SUM({1,2;3,4})') != normalized('=SUM({1;2;3;4})')
    assert normalized('="1,5;A1:A1"') != normalized('="1.5,A1"')
    assert normalized('=A1:$A$1') != normalized('=A1')
    assert normalized('=INDEX($CO$2:$CO$1,1)',True) == normalized('=INDEX($CO$1:$CO$2;1)',True)


def main():
    selfcheck()
    private = Path(sys.argv[1])
    source = json.loads((private/'fonte-materializada-formulas.json').read_text())
    live = json.loads((private/'formulas-nativas-normalizadas.json').read_text())
    vals = expand(json.loads((private/'abas-fonte.json').read_text()))
    old = expand(json.loads((private/'abas-base-pre-r53.json').read_text()))
    sys.path.insert(0,str(ROOT/'ficha-v01'))
    import extensoes_custom as ex
    editor_source=(ROOT/'apps-script/EditorR53.gs').read_text()
    editor,_=json.JSONDecoder().raw_decode(editor_source[editor_source.index('=')+1:].lstrip())
    points=set()
    for g in editor['contextos']:
        if g['aba']=='INVOCAÇÕES' and (g['id'].endswith('.liberacao.1') or g['id'].endswith('.maxima.1')):
            points.add((int(re.search(r'\d+',g['cel']['nome'])[0]),8 if g['id'].endswith('.liberacao.1') else 7))
    inserts=[]
    for row,offset in sorted(points): inserts.append([row-10*len(inserts)+offset,10])
    assert len(inserts)==12
    ex.INSERCOES={'INVOCAÇÕES':inserts};ex.formula.cache_clear()
    details = defaultdict(list)
    extra_details = []
    errors = []
    old_counts = Counter()
    for sheet, cells in source.items():
        for addr, formula in cells.items():
            native = live.get(sheet,{}).get(addr)
            if native is None:
                category = 'formula_fonte_substituida_ou_ausente'
                old_counts['ausentes'] += 1
            elif canonical(formula) == canonical(native):
                category = 'iguais_normalizacao_anterior'
                old_counts['iguais'] += 1
            else:
                old_counts['diferentes'] += 1
                if sheet == 'DADOS_R53' and addr.startswith('FD'):
                    category = 'efeitos_fonte_truncada'
                elif '__xludf.DUMMYFUNCTION' in native:
                    category = 'barra_com_funcao_incompativel'
                elif (sheet,addr) in [('CARTEIRA','AH3'),('FICHA PESSOAL','W86')]:
                    category = 'extensao_salarios_documentada'
                elif normalized(formula) == normalized(native):
                    category = 'normalizacao_matriz_numero_intervalo_unitario'
                elif normalized(formula,True) == normalized(native,True):
                    category = 'intervalo_invertido_normalizado_pelo_google'
                else:
                    category = 'divergencia_nao_classificada'
            if category != 'iguais_normalizacao_anterior':
                details[category].append({'aba':sheet,'celula':addr})
        for addr, formula in live.get(sheet,{}).items():
            if addr in cells:
                continue
            planned = vals.get(sheet,{}).get(addr)
            historical = old.get(sheet,{}).get(addr)
            origin = 'nao_equivale_a_baseline_pre_r53'
            if isinstance(historical,str) and historical.startswith('='):
                try:
                    if normalized(formula) == normalized(historical): origin = 'igual_a_formula_pre_r53'
                    elif normalized(formula) == normalized(ex.formula(historical,sheet)): origin = 'formula_pre_r53_com_insercoes_documentadas'
                except Exception as e:
                    errors.append({'aba':sheet,'celula':addr,'etapa':'historico','erro':type(e).__name__})
            extra_details.append({'aba':sheet,'celula':addr,'origem':origin,
                'fonte_atual':'omitida' if addr not in vals.get(sheet,{}) else 'vazia' if planned in ('',None) else 'literal',
                'categoria':'extensao_salarios_documentada' if sheet=='CONFIGURAÇÃO' else 'persistencia_a_reconciliar'})

    # Dependentes estáticos das fórmulas adicionais; não prova ausência de
    # consumidores dinâmicos, script ou intervalo nomeado.
    extras_by_sheet = defaultdict(dict)
    for item in extra_details:
        c,r,_,_=range_boundaries(item['celula'])
        extras_by_sheet[item['aba']][item['celula']] = (c,r)
    consumers = defaultdict(list)
    nonextra_consumers=set()
    extra_edges=defaultdict(set)
    analysis_refs = []
    effects_consumers = []
    indirect = []
    open_ranges = []
    for sheet,cells in live.items():
        for addr,f in cells.items():
            if 'INDIRECT(' in f:
                indirect.append({'aba':sheet,'celula':addr})
            if '__xludf' in f:
                continue  # Texto da função fictícia não é dependência calculada.
            try:
                tokens = Tokenizer(english(f)).items
            except Exception as e:
                errors.append({'aba':sheet,'celula':addr,'etapa':'dependencias','erro':type(e).__name__})
                continue
            for t in tokens:
                if t.type!='OPERAND' or t.subtype!='RANGE': continue
                prefix,sep,coords=t.value.rpartition('!')
                owner=prefix.strip("'").replace("''", "'") if sep else sheet
                try:
                    c,r,cc,rr=range_boundaries(coords)
                except ValueError:
                    # Sheets aceita J2:J; openpyxl.range_boundaries não.
                    mixed=re.fullmatch(r'(\$?[A-Z]+)(\$?\d*)?:(\$?[A-Z]+)(\$?\d*)?',coords)
                    if not mixed: continue  # Nome definido: limite explícito.
                    c=range_boundaries(mixed[1]+'1')[0];cc=range_boundaries(mixed[3]+'1')[0]
                    r=int(mixed[2].replace('$','')) if mixed[2] else None
                    rr=int(mixed[4].replace('$','')) if mixed[4] else None
                if None in (c,r,cc,rr):
                    open_ranges.append({'aba':sheet,'celula':addr,'destino':owner,'intervalo':coords})
                if owner=='ANALISE':
                    analysis_refs.append({'aba':sheet,'celula':addr,'intervalo':coords})
                if owner=='DADOS_R53' and (c or 1)<=160<=(cc or 183):
                    effects_consumers.append({'aba':sheet,'celula':addr,'intervalo':coords})
                if owner not in extras_by_sheet: continue
                for extra,(ec,er) in extras_by_sheet[owner].items():
                    if (c or 1)<=ec<=(cc or 100000) and (r or 1)<=er<=(rr or 1000000):
                        key=(owner,extra)
                        if addr in extras_by_sheet.get(sheet,{}): extra_edges[key].add((sheet,addr))
                        else: nonextra_consumers.add(key)
                        if len(consumers[key])<3:
                            consumers[key].append({'aba':sheet,'celula':addr,'intervalo':coords})
    for item in extra_details:
        cs=consumers.get((item['aba'],item['celula']),[])
        item['consumidores_estaticos_amostra']=cs
        item['tem_consumidor_estatico']=bool(cs)
        item['consumida_por_formula_fora_do_conjunto_adicional']=(item['aba'],item['celula']) in nonextra_consumers
    reaches=set(nonextra_consumers)
    while True:
        more={k for k,values in extra_edges.items() if values & reaches}
        if more<=reaches: break
        reaches |= more
    report={
        'base':'fbd6d156602958dc0f9da467a4a80100ad7b913f',
        'escopo':'Revisão offline; nenhuma exclusão autorizada por ausência de dependentes estáticos',
        'comparacao_anterior':dict(old_counts),
        'insercoes_r53_reconciliadas':inserts,
        'diferencas_classificadas':{k:{'quantidade':len(v),'celulas':v} for k,v in details.items()},
        'adicionais':{'quantidade':len(extra_details),'por_origem':dict(Counter(i['origem'] for i in extra_details)),
            'por_aba':{s:dict(total=sum(i['aba']==s for i in extra_details),com_consumidor_estatico=sum(i['aba']==s and i['tem_consumidor_estatico'] for i in extra_details),alcanca_formula_fora_do_conjunto=sum(x[0]==s for x in reaches)) for s in extras_by_sheet},'celulas':extra_details},
        'dependencias':{'referencias_ANALISE':analysis_refs,'consumidores_FD':effects_consumers,
            'formulas_com_INDIRECT':indirect,'intervalos_abertos':open_ranges},
        'erros_do_analisador':errors,
        'limites':['Referências em INDIRECT, intervalos nomeados e código remoto exigem conferência própria',
            'Referência sintática não prova execução de ramo nem relevância mecânica',
            'Fórmulas mascaradas por IFERROR podem ocultar defeitos apesar de zero erros efetivos']}
    dest=Path(__file__).with_name('RECONCILIACAO-2026-10-23.json')
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'classificacao':{k:len(v) for k,v in details.items()},'adicionais':report['adicionais']['por_aba'],
        'origens':report['adicionais']['por_origem'],'erros_analisador':len(errors),
        'refs_ANALISE':len(analysis_refs),'consumidores_FD':len(effects_consumers),'faixas_abertas':len(open_ranges)},ensure_ascii=False))
    assert not details.get('divergencia_nao_classificada')
    assert not errors


if __name__=='__main__': main()
