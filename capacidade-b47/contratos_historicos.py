"""Mudanças aprovadas no formato 7: nove Famílias e respiro da Definição.

Transformação exata do contrato anterior, independente do modelo atual. Nunca
aceita diferenças genéricas de fórmula/endereço nem lê expectativas do alvo.
"""
import re


def transformar(row,*,versao=10,reverter=False):
    row=list(row);key=row[0]
    if key=='formato.versao':row[1]=str(versao);return row
    fm=re.fullmatch(r'invocacao\.(\d+)\.familias',key)
    if fm:
        r=int(fm[1])+1
        cols=['EL','EM','EN','EO','EP']
        if reverter:cols+=['QV','QW','QX','QY']
        expected='=TEXTJOIN(" · ",TRUE,'+','.join(f'DADOS_INVOC!${c}${r}' for c in cols)+')'
        expected_source=' '.join(f'DADOS_INVOC!{c}{r}' for c in cols)
        if row[1]!=expected or row[2]!=expected_source:raise ValueError('Agregado histórico inesperado: '+key)
        cols=cols[:5] if reverter else cols+['QV','QW','QX','QY']
        row[1]='=TEXTJOIN(" · ",TRUE,'+','.join(f'DADOS_INVOC!${c}${r}' for c in cols)+')'
        row[2]=' '.join(f'DADOS_INVOC!{c}{r}' for c in cols)
    fm=re.fullmatch(r'invocacao\.(\d+)\.definicao',key)
    if fm:
        n=int(fm[1])-1;c='I' if n<6 else 'AB';r=52+198*(n%6)+(1 if reverter else 0);dest=r+(-1 if reverter else 1)
        src=f"'INVOCAÇÕES'!${c}${r}";dst=f"'INVOCAÇÕES'!${c}${dest}"
        if row[1]!=f'=IF(ISBLANK({src}),"",{src}&"")' or row[2]!=f'="\'INVOCAÇÕES\'!{c}{r}"':raise ValueError('Definição histórica inesperada: '+key)
        row[1]=row[1].replace(src,dst);row[2]=f'="\'INVOCAÇÕES\'!{c}{dest}"'
    return row
