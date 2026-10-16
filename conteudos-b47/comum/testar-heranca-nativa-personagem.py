"""Confere uma releitura real do ensaio de herança; sem rede e sem Calc."""
import argparse
import json
from pathlib import Path
from openpyxl.utils import get_column_letter as L

DESTINO='1mZaDlSvdYsAcsD-2dJmX5GG0Geo2ObJBJFhA0sFwTok'


def valores(response):
    r=response.get('structuredContent',response)
    if r.get('spreadsheetId')!=DESTINO:raise ValueError('Leitura de outro destino')
    result={}
    for sheet in r['sheets']:
        for data in sheet.get('data',[]):
            for dr,row in enumerate(data.get('rowData',[])):
                for dc,cell in enumerate(row.get('values',[])):
                    v=cell.get('effectiveValue',{})
                    if 'errorValue' in v:raise ValueError('Erro de fórmula: '+str(v))
                    key=sheet['properties']['title']+'!'+L(data.get('startColumn',0)+dc+1)+str(data.get('startRow',0)+dr+1)
                    result[key]=next(iter(v.values()),'')
    return result


def conferir(model,response):
    m=model['personagem'];cells=valores(response);checks=[]
    def get(aba,col,row):return cells.get(aba+'!'+L(col)+str(row),'')
    def check(nome,a,b):
        # bool e número não são equivalentes; 0.0 e 0 nativos são.
        ok=a==b and isinstance(a,bool)==isinstance(b,bool)
        checks.append(dict(nome=nome,ok=ok,**({} if ok else dict(esperado=a,recebido=b))))
    bases={'forma':['Explosão','Cone'],'aptidao':['Energia Reversa','Cobrir-se de Energia'],
           'talento':['Leitura','Reserva Profunda']}
    labels={'forma':'Forma','aptidao':'Aptidão','talento':'Talento'}
    for grupo,t in m['tabelas'].items():
        for index,n in enumerate((1,10)):
            dst=t['livro']+n+1
            row=next(r for r in range(2,t['livro']+2) if get(t['aba'],t['colunas']['nome'],r)==bases[grupo][index])
            check(grupo+f'.{n}.nome',labels[grupo]+' *?~ '+('inicial' if n==1 else 'final'),get(t['aba'],t['colunas']['nome'],dst))
            for campo in (k for k in t['campos'] if k not in ('nome','base','automatica')):
                col=t['colunas'][campo]
                check(grupo+f'.{n}.'+campo,get(t['aba'],col,row),get(t['aba'],col,dst))
            if grupo=='aptidao' and n==10:
                check('gratuidade herdada','Gratuita',get(t['aba'],t['colunas']['escolha'],dst))
                check('gratuita selecionada não é automática',False,get(t['aba'],t['colunas']['automatica'],dst))
            if grupo!='forma':continue
            for contexto,faixas in [('personagem',3),('entidade',4)]:
                out=m['catalogos']['alcance_'+contexto]
                book_first=2+(row-2)*faixas;custom_first=2+(t['livro']+n-1)*faixas
                for faixa in range(faixas):
                    for grau in range(1,out['largura']):
                        col=out['coluna']+grau
                        check(f'alcance.{contexto}.{n}.{faixa}.{grau}',
                            get(out['aba'],col,book_first+faixa),get(out['aba'],col,custom_first+faixa))
    p=m['catalogos']['alcance_personagem'];e=m['catalogos']['alcance_entidade']
    check('Explosão personagem classe 6','Raio 4,5 m',get(p['aba'],p['coluna']+1,34))
    check('Explosão entidade classe 6','Raio 3 m',get(e['aba'],e['coluna']+1,44))
    check('Explosão entidade classe 7','Raio 4,5 m',get(e['aba'],e['coluna']+1,45))
    check('alcance personagem classe 6',', a 36 m',get(p['aba'],p['coluna']+7,34))
    check('alcance entidade classe 6',', a 36 m',get(e['aba'],e['coluna']+7,44))
    return dict(resultado='OK' if all(x['ok'] for x in checks) else 'FALHA',
                checagens=len(checks),falhas=[x for x in checks if not x['ok']],
                escopo='catálogos e pontes em Sheets; consumidores/gatilhos não instalados neste ensaio')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--modelo',type=Path,required=True);p.add_argument('--leitura',type=Path,required=True)
    a=p.parse_args()
    report=conferir(json.loads(a.modelo.read_text(encoding='utf8')),json.loads(a.leitura.read_text(encoding='utf8')))
    print(json.dumps(report,ensure_ascii=False));raise SystemExit(report['resultado']!='OK')
