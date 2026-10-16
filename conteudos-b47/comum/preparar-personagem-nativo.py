"""Lotes offline do ensaio focal de catálogos de personagem numa cópia exclusiva.

Não migra revisão, não grava GS e não altera consumidores antigos. A construção
conjunta e as interações nas fichas continuam como etapas independentes.
"""
import argparse
import json
from pathlib import Path
import sys
from openpyxl.utils.cell import range_boundaries

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'capacidade-b47'))
from lotes import native_value,format_

DESTINO='1mZaDlSvdYsAcsD-2dJmX5GG0Geo2ObJBJFhA0sFwTok'
IDS={'CONFIGURAÇÃO':1676293043,'CD_TESTE_ANALISE':47012,
     'DADOS_FORMAS':47013,'DADOS_APTIDOES':47014,'DADOS_TALENTOS':47015}


def preparar(model,meta):
    if meta['spreadsheetId']!=DESTINO:raise ValueError('Destino não é a cópia focal de personagem')
    if meta['properties']['title']!='TESTE DESCARTÁVEL B47 C+D — personagem e comuns — 2026-10-16':
        raise ValueError('Título de destino divergente')
    before={s['properties']['title']:s['properties'] for s in meta['sheets']}
    tabs={a['nome']:a for a in model['layout']['abas']}
    tr=model['personagem'];cfg=tabs['CONFIGURAÇÃO']
    if before['CONFIGURAÇÃO']['gridProperties']['rowCount']>=tr['inicio']:
        raise ValueError('Área de ensaio já existe; não reaplicar lotes')
    for name in ('CONFIGURAÇÃO','CD_TESTE_ANALISE'):
        if before[name]['sheetId']!=IDS[name]:raise ValueError('ID de aba divergente')
    aux=['DADOS_FORMAS','DADOS_APTIDOES','DADOS_TALENTOS']
    used={p['sheetId'] for p in before.values()}
    if any(name in before or IDS[name] in used for name in aux):raise ValueError('Auxiliar já existe; não reaplicar')
    requests=[]
    for name in aux:
        a=tabs[name]
        requests.append({'addSheet':{'properties':{'sheetId':IDS[name],'title':name,'hidden':True,
            'gridProperties':{'rowCount':a['linhas']+2,'columnCount':a['colunas'],'hideGridlines':True}}}})
    for name,rows in [('CONFIGURAÇÃO',cfg['linhas']+2),('CD_TESTE_ANALISE',605)]:
        requests.append({'updateSheetProperties':{'properties':{'sheetId':IDS[name],
            'gridProperties':{'rowCount':rows}},'fields':'gridProperties.rowCount'}})

    def grid(name,a1):
        c,r,cc,rr=range_boundaries(a1)
        return dict(sheetId=IDS[name],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)

    def matrix(name,first,last,width,values,fields,chunk=10):
        for start in range(first,last+1,chunk):
            rows=[{'values':[values.get((r,c),{}) for c in range(1,width+1)]}
                  for r in range(start,min(start+chunk,last+1))]
            requests.append({'updateCells':{'start':{'sheetId':IDS[name],'rowIndex':start-1,'columnIndex':0},
                'rows':rows,'fields':fields}})

    for name in aux:
        a=tabs[name];values={}
        for a1,v,*_ in a['celulas']:
            c,r,_,_=range_boundaries(a1)
            values[(r,c)]={'userEnteredValue':native_value(v)}
        matrix(name,1,a['linhas'],a['colunas'],values,'userEnteredValue')
    values={}
    for a1,v,style in cfg['celulas']:
        c,r,_,_=range_boundaries(a1)
        if r<tr['inicio']:continue
        cell={'userEnteredValue':native_value(v)}
        if style is not None:cell['userEnteredFormat']=format_(model['layout']['estilos'][style])
        if a1 in cfg.get('notas',{}):cell['note']=cfg['notas'][a1]
        values[(r,c)]=cell
    matrix('CONFIGURAÇÃO',tr['inicio'],tr['fim'],16,values,'userEnteredValue,userEnteredFormat,note',40)
    requests.append({'updateDimensionProperties':{'range':{'sheetId':IDS['CONFIGURAÇÃO'],'dimension':'ROWS',
        'startIndex':tr['inicio']-1,'endIndex':tr['fim']},'properties':{'pixelSize':25},'fields':'pixelSize'}})
    for region in cfg['mescladas']:
        if range_boundaries(region)[1]>=tr['inicio']:
            requests.append({'mergeCells':{'range':grid('CONFIGURAÇÃO',region),'mergeType':'MERGE_ALL'}})
    for menu in cfg['menus']:
        if range_boundaries(menu['onde'])[1]<tr['inicio']:continue
        requests.append({'setDataValidation':{'range':grid('CONFIGURAÇÃO',menu['onde']),
            'rule':{'condition':{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+menu['formula']}]},
                    'strict':True,'showCustomUi':True}}})
    for key,a1,boolean in tr['entradas']:
        if boolean:requests.append({'setDataValidation':{'range':grid('CONFIGURAÇÃO',a1),
            'rule':{'condition':{'type':'BOOLEAN'}}}})
    cells={c[0]:c[1] for c in tabs['ANALISE']['celulas']}
    rows=[]
    for r in range(tr['analise_inicio'],tr['analise_fim']+1):
        # Avisos de uso dependem dos consumidores modificados, que este ensaio
        # não instala. Exportar aqui somente cadastros/avisos dos catálogos.
        if str(cells['A'+str(r)]).startswith('aviso.personagem.'):continue
        rows.append({'values':[{'userEnteredValue':native_value(cells[col+str(r)])} for col in 'ABCD']})
    if len(rows)!=500:raise ValueError('Ensaio focal exige 500 campos/avisos de cadastro')
    requests.append({'updateCells':{'start':{'sheetId':IDS['CD_TESTE_ANALISE'],'rowIndex':81,'columnIndex':0},
        'rows':rows,'fields':'userEnteredValue'}})
    # Limitar também bytes: uma matriz de fórmulas é muito maior que trinta
    # pedidos de mesclagem. Dividir matrizes não muda seu conteúdo nem alvo.
    def size(x):return len(json.dumps(x,ensure_ascii=False).encode('utf8'))
    def split(request):
        if size(request)<=45000:return [request]
        u=request.get('updateCells')
        if not u:raise ValueError('Pedido individual grande demais')
        if len(u['rows'])==1:
            values=u['rows'][0]['values'];cut=len(values)//2
            if not cut:raise ValueError('Célula individual grande demais')
            left={'updateCells':{**u,'rows':[{'values':values[:cut]}]}}
            right={'updateCells':{**u,'start':{**u['start'],'columnIndex':u['start']['columnIndex']+cut},
                'rows':[{'values':values[cut:]}]}}
            return split(left)+split(right)
        cut=len(u['rows'])//2
        left={'updateCells':{**u,'rows':u['rows'][:cut]}}
        right={'updateCells':{**u,'start':{**u['start'],'rowIndex':u['start']['rowIndex']+cut},'rows':u['rows'][cut:]}}
        return split(left)+split(right)
    batches=[requests[:5]];current=[]
    for request in requests[5:]:
        for part in split(request):
            if current and (len(current)>=30 or size(current+[part])>60000):
                batches.append(current);current=[]
            current.append(part)
    if current:batches.append(current)
    return batches


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--modelo',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args()
    m=json.loads(a.modelo.read_text(encoding='utf8'))
    meta=json.loads(a.metadata.read_text(encoding='utf8'))
    if 'destination' in meta:meta=meta['destination']['structuredContent']
    batches=preparar(m,meta);a.saida.mkdir(parents=True,exist_ok=True)
    for i,b in enumerate(batches):
        f=a.saida/f'{i:03d}.json'
        if f.exists():raise ValueError('Saída já existe: '+str(f))
        f.write_text(json.dumps({'spreadsheet_id':DESTINO,'requests':b},ensure_ascii=False),encoding='utf8')
    print(json.dumps({'lotes':len(batches),'requests':sum(map(len,batches)),'destino':DESTINO}))
