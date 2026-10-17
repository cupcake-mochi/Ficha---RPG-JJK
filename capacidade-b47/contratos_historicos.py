"""Mudanças aprovadas no formato 7: nove Famílias e respiro da Definição.

Transformação exata do contrato anterior, independente do modelo atual. Nunca
aceita diferenças genéricas de fórmula/endereço nem lê expectativas do alvo.
"""
import re


def classificar_vazio(diferencas,ler_atual):
    """Exceções exatas da referência antiga, sem descartar valores numéricos.

    Os rótulos foram substituídos pelo limite real de Famílias (C, prova dos
    13 cenários em REGRESSAO-FAMILIAS-NATIVA.json). DEFINIÇÃO não é excluída:
    exige o texto no novo endereço, pelo respiro aprovado no formato 7.
    """
    aceitas=[];pendentes=[]
    for diferenca in diferencas:
        sheet,coord,before,after=diferenca
        m=re.fullmatch(r'(P|S|AI|AL)([0-9]+)',coord)
        header=re.fullmatch(r'(I|AB)([0-9]+)',coord)
        if sheet=='INVOCAÇÕES' and m and int(m[2]) in [47+198*i for i in range(6)] and after=='ABERTA' and before==('LIVRE · TRILHA' if m[1] in ('P','AI') else 'ABERTA · TRILHA'):
            aceitas.append({'diferenca':list(diferenca),'causa':'C: rótulo lê o limite individual de Famílias; prova nativa separada.'})
        elif sheet=='INVOCAÇÕES' and header and int(header[2]) in [51+198*i for i in range(6)] and before=='DEFINIÇÃO' and after in (None,'') and ler_atual(sheet,header[1]+str(int(header[2])+1))=='DEFINIÇÃO':
            aceitas.append({'diferenca':list(diferenca),'causa':'Cabeçalho preservado uma linha abaixo, no respiro aprovado do formato 7.'})
        else:pendentes.append(diferenca)
    return aceitas,pendentes


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
