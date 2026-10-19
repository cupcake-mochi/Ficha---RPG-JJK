"""Ponte das Formas próprias já validadas pelo cadastro B47.

Os componentes de alcance/área são dados estruturados. Reutiliza as escadas
calculadas do cadastro, sem deduzir geometria do texto de efeito.
"""
from openpyxl.utils import get_column_letter as L
CAMPOS=['rotulo','base','familia','peso','classe_0','coletiva','restricao_embutida','p1_dimensao','p2_dimensao']+['medida_'+str(i) for i in range(84)]
FAIXAS=[('personagem','classe_0'),('personagem','classes_1_a_5'),('personagem','classes_6_e_7'),('entidade','classe_0'),('entidade','classes_1_a_5'),('entidade','classe_6'),('entidade','classe_7')]

def aplicar(personagem,put,catalogo,ref):
    t=personagem['plano'].tabelas['forma'];first=38
    col=t['colunas'];own=t['aba'];r=lambda k,row:ref(own,L(col[k])+str(row))
    for i,k in enumerate(CAMPOS):put(L(first+i)+'1','forma.'+k)
    rows=[]
    for row in range(t['livro']+2,t['total']+2):
        dest=len(rows)+2;rows.append(dest)
        values=[r('nome',row),r('base',row),r('familia',row),r('peso',row),r('classe_0',row),
                'OR('+r('p1_dimensao',row)+'="area",'+r('p2_dimensao',row)+'="area")',r('restricao_embutida',row),r('p1_dimensao',row),r('p2_dimensao',row)]
        for contexto,faixa in FAIXAS:
            m=personagem['catalogos']['alcance_'+contexto]
            for part in range(2):
                for step in range(6):
                    key=r('nome',row)+'&" · '+faixa.replace('_',' ')+'"'
                    source=m['intervalo']
                    key='SUBSTITUTE(SUBSTITUTE(SUBSTITUTE('+key+',"~","~~"),"*","~*"),"?","~?")'
                    values.append('IFERROR(VLOOKUP('+key+','+source+','+str(2+part*6+step)+',FALSE),"")')
        for i,value in enumerate(values):put(L(first+i)+str(dest),'='+value)
    catalogo['colunas']=max(catalogo['colunas'],first+len(CAMPOS)-1)
    return ref(catalogo['nome'],f'${L(first)}$2:${L(first+len(CAMPOS)-1)}${rows[-1]}'),rows
