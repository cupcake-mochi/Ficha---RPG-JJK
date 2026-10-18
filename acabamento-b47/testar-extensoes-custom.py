"""Verificações estruturais da apresentação, sem recalcular a ficha inteira.

Uso: python testar-extensoes-custom.py modelo-horizontal.json geometria.json saida.json
Os dois primeiros arquivos são exportações do gerador, sem dados do jogador.
"""
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ficha-v01'))
import extensoes_custom as e
import custom_criacao
from openpyxl.utils.cell import range_boundaries

def usos():
    out=[]
    for c,t,total,offset,r in [(4,'Perícia',12,0,411),(24,'Perícia',11,12,411),(4,'Ofício',6,0,427),(24,'Ofício',5,6,427)]:
        for i in range(total):
            out.append(dict(tipo=t,n=offset+i+1,**{k:e.L(c+d)+str(r+2+i) for k,d in [('treino',0),('especializacao',1),('nome',2),('atributo',10),('resultado',14),('bonus',16)]}))
    return out

if __name__=='__main__':
    l=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))['layout']
    geo=json.loads(Path(sys.argv[2]).read_text(encoding='utf8'))['geo']['invocacoes']
    before=copy.deepcopy(l)
    audit=e.aplica(l,{'linhas_ficha':usos()},{'familias':[custom_criacao.familia(n) for n in range(1,11)]},geo)
    assert e.coord('FICHA','$D$103')=='$D$129'
    assert e.formula('=IF("D103"="D103",\'FICHA\'!D103,0)','DADOS')=='=IF("D103"="D103",\'FICHA\'!D129,0)'
    assert e.formula("'INVOCAÇÕES'!H207",'ANALISE')=="'INVOCAÇÕES'!H220"
    assert next(x[1] for a in l['abas'] if a['nome']=='DADOS_AM' for x in a['celulas'] if x[0]=='KU19')=='J55'
    for a in l['abas']:
        rects=[]
        for m in a['mescladas']:
            r=range_boundaries(m)
            assert not any(max(r[0],q[0])<=min(r[2],q[2]) and max(r[1],q[1])<=min(r[3],q[3]) for q in rects),(a['nome'],m,'mesclagem sobreposta')
            rects.append(r)
        groups=a.get('grupos',{}).get('linhas',[])
        for x in groups:
            for y in groups:
                assert not (x[0]<y[0]<=x[1]<y[1]),(a['nome'],x,y,'grupos cruzados')
    assert len(audit['paineis'])==15
    assert sum(len(a.get('familias_custom',[])) for a in l['abas'])==12
    old=next(a for a in before['abas'] if a['nome']=='ANALISE')
    new=next(a for a in l['abas'] if a['nome']=='ANALISE')
    assert [x[1] for x in old['celulas'] if x[0].startswith('A')]==[x[1] for x in new['celulas'] if x[0].startswith('A')]
    Path(sys.argv[3]).write_text(json.dumps({'layout':l,'auditoria':audit},ensure_ascii=False),encoding='utf8')
    print('OK: referências por tokens, identidade ANALISE, 15 painéis, 12 entidades, mesclagens e grupos sem sobreposição.')
