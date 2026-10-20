"""Árvore única de expressões para cálculo verificável e fórmulas nativas.

O avaliador serve para diagnósticos locais; o produto usa as mesmas expressões
como fórmulas comuns de Google Sheets, sem funções customizadas ou autorização.
"""
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class X:
    op: str
    args: tuple
    def __add__(self,b): return X('+',(self,x(b)))
    def __radd__(self,b): return x(b)+self
    def __sub__(self,b): return X('-',(self,x(b)))
    def __rsub__(self,b): return x(b)-self
    def __mul__(self,b): return X('*',(self,x(b)))
    def __rmul__(self,b): return x(b)*self
    def __truediv__(self,b): return X('/',(self,x(b)))
    def __neg__(self): return 0-self
    def eq(self,b): return X('=',(self,x(b)))
    def ne(self,b): return X('<>',(self,x(b)))
    def gt(self,b): return X('>',(self,x(b)))
    def ge(self,b): return X('>=',(self,x(b)))
    def lt(self,b): return X('<',(self,x(b)))
    def le(self,b): return X('<=',(self,x(b)))
    def cat(self,b): return X('&',(self,x(b)))


def x(v): return v if isinstance(v,X) else X('lit',(v,))
def ref(k): return X('ref',(k,))
def f(op,*args): return X(op,tuple(x(a) for a in args))
def IF(c,a,b=0): return f('IF',c,a,b)
def AND(*v): return f('AND',*v) if v else x(True)
def OR(*v): return f('OR',*v) if v else x(False)
def SUM(v): return f('SUM',*v) if v else x(0)
def MIN(*v): return f('MIN',*v)
def MAX(*v): return f('MAX',*v)
def UP(v): return f('ROUNDUP',v,0)
def INT(v): return f('INT',v)
def JOIN(*v): return f('TEXTJOIN','; ',True,*v)
def LOOK(v,field): return X('lookup',(x(v),field))
def FAMILY(v):return X('family',(x(v),))
def FORM(v,field,offset=0):return X('form',(x(v),field,x(offset)))


def number(v):
    if v is None or v == '': return 0
    return float(v)


def evaluate(e, env, catalog):
    e=x(e); op=e.op
    if op=='lit': return e.args[0]
    if op=='ref': return env.get(e.args[0],0)
    if op=='IF': return evaluate(e.args[1] if evaluate(e.args[0],env,catalog) else e.args[2],env,catalog)
    if op=='family':
        name=evaluate(e.args[0],env,catalog)
        return 'Neutra' if not name else env.get('fam_'+name,env.get('_familias',{}).get(name,'Fechada'))
    if op=='form':
        name=evaluate(e.args[0],env,catalog);field=e.args[1];offset=int(number(evaluate(e.args[2],env,catalog)))
        row=env.get('_formas',{}).get(name,{})
        if field=='medida_0':return row.get('medidas',['']*84)[offset]
        return row.get(field,0 if field in ('peso','classe_0','coletiva') else '')
    if op=='lookup': return catalog.get(evaluate(e.args[0],env,catalog),{}).get(e.args[1], '')
    a=[evaluate(v,env,catalog) for v in e.args]
    if op in ['+','-','*','/']:
        l,r=map(number,a)
        return {'+':lambda:l+r,'-':lambda:l-r,'*':lambda:l*r,'/':lambda:l/r}[op]()
    if op in ['=','<>','>','>=','<','<=']:
        l,r=a
        if op=='=': return l==r
        if op=='<>': return l!=r
        l,r=number(l),number(r)
        return {'>':lambda:l>r,'>=':lambda:l>=r,'<':lambda:l<r,'<=':lambda:l<=r}[op]()
    if op=='&': return ''.join(str(int(v)) if isinstance(v,float) and v.is_integer() else str(v) for v in a)
    if op=='AND': return all(a)
    if op=='OR': return any(a)
    if op=='SUM': return sum(map(number,a))
    if op=='MIN': return min(map(number,a))
    if op=='MAX': return max(map(number,a))
    if op=='ROUNDUP': return math.ceil(number(a[0]))
    if op=='INT': return math.floor(number(a[0]))
    if op=='TEXTJOIN': return str(a[0]).join(str(v) for v in a[2:] if v!='')
    raise ValueError(op)


def native(e, refs, lookup_range, lookup_fields, separator=','):
    e=x(e);op=e.op
    if op=='lit':
        v=e.args[0]
        if isinstance(v,bool): return 'TRUE' if v else 'FALSE'
        if isinstance(v,str): return '"'+v.replace('"','""')+'"'
        if v is None: return '""'
        return str(v).replace('.', ',') if separator == ';' else str(v)
    if op=='ref': return refs[e.args[0]]
    if op=='form':
        value=native(e.args[0],refs,lookup_range,lookup_fields,separator)
        empty='0' if e.args[1] in ('peso','classe_0','coletiva') else '""'
        if '__formas_range__' not in refs:return empty
        for a,b in [('~','~~'),('*','~*'),('?','~?')]:value=f'SUBSTITUTE({value}{separator}"{a}"{separator}"{b}")'
        coluna=refs['__formas_campos__'].index(e.args[1])+1
        offset=native(e.args[2],refs,lookup_range,lookup_fields,separator)
        return f'IFERROR(VLOOKUP({value}{separator}{refs["__formas_range__"]}{separator}{coluna}+{offset}{separator}FALSE){separator}{empty})'
    if op=='family':
        value=native(e.args[0],refs,lookup_range,lookup_fields,separator)
        fallback='"Fechada"'
        if '__familias_range__' in refs:
            criterio=value
            for a,b in [('~','~~'),('*','~*'),('?','~?')]:criterio=f'SUBSTITUTE({criterio}{separator}"{a}"{separator}"{b}")'
            fallback=f'IFERROR(VLOOKUP({criterio}{separator}{refs["__familias_range__"]}{separator}{refs["__familias_col__"]}{separator}FALSE){separator}"Fechada")'
        for key in reversed([k for k in refs if k.startswith('fam_')]):
            name=key[4:].replace('"','""')
            fallback=f'IF({value}="{name}"{separator}{refs[key]}{separator}{fallback})'
        return f'IF({value}=""{separator}"Neutra"{separator}{fallback})'
    if op=='lookup':
        v,field=e.args
        col=lookup_fields.index(field)+1
        empty='""' if field in ['nome','familia','tipo','id','rotulo_base'] else '0'
        value=native(v,refs,lookup_range,lookup_fields,separator)
        for a,b in [('~','~~'),('*','~*'),('?','~?')]:
            value=f'SUBSTITUTE({value}{separator}"{a}"{separator}"{b}")'
        return f'IFERROR(VLOOKUP({value}{separator}{lookup_range}{separator}{col}{separator}FALSE){separator}{empty})'
    a=[native(v,refs,lookup_range,lookup_fields,separator) for v in e.args]
    if op in ['+','-','*','/','=','<>','>','>=','<','<=','&']: return '('+a[0]+op+a[1]+')'
    return op+'('+separator.join(a)+')'
