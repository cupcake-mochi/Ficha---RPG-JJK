"""Prepara lotes offline APENAS para a nova descartável C+D, sem rede.

Não é migrador de revisão. Exige ID exclusivo da cópia nativa já identificada.
Não reaplicar lotes após envio; reler estado quando houver resultado incerto.
"""
import argparse
import json
from pathlib import Path
import sys
from openpyxl.utils.cell import range_boundaries

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47')]
from lotes import native_value,format_,pt
from custom_condicoes import exporta as exporta_condicoes
from custom_danos import exporta as exporta_danos

DESTINO='1BzVzrqjKsarh6DCAu6FGZ_yOxy0aBzttfX4n1JH2QFI'
IDS={'CONFIGURAÇÃO':1676293043,'DADOS_MELHORIAS':1452793632,
     'DADOS_CUSTOM':1236764512,'INVOCAÇÕES':1403461220,
     'DADOS_DANOS':47011,'CD_TESTE_ANALISE':47012}


def preparar(model,destino):
    if destino!=DESTINO:raise ValueError('Destino não é a descartável C+D deste ensaio')
    tabs={a['nome']:a for a in model['layout']['abas']}
    tr=model['danos'];cfg=tabs['CONFIGURAÇÃO'];data=tabs['DADOS_DANOS']
    init=[{'addSheet':{'properties':{'sheetId':IDS['DADOS_DANOS'],'title':'DADOS_DANOS',
        'hidden':True,'gridProperties':{'rowCount':data['linhas'],'columnCount':data['colunas']}}}},
        {'addSheet':{'properties':{'sheetId':IDS['CD_TESTE_ANALISE'],'title':'CD_TESTE_ANALISE',
        'hidden':True,'gridProperties':{'rowCount':81,'columnCount':4}}}},
        {'updateSheetProperties':{'properties':{'sheetId':IDS['CONFIGURAÇÃO'],
        'gridProperties':{'rowCount':cfg['linhas']+2}},'fields':'gridProperties.rowCount'}},
        {'updateSheetProperties':{'properties':{'sheetId':IDS['DADOS_MELHORIAS'],
        'gridProperties':{'columnCount':tabs['DADOS_MELHORIAS']['colunas']}},'fields':'gridProperties.columnCount'}}]
    requests=[]
    def grid(name,a1):
        c,r,cc,rr=range_boundaries(a1)
        return dict(sheetId=IDS[name],startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
    def write(name,a1,cell,fields):
        c,r,_,_=range_boundaries(a1)
        requests.append({'updateCells':{'start':{'sheetId':IDS[name],'rowIndex':r-1,'columnIndex':c-1},
            'rows':[{'values':[cell]}],'fields':fields}})
    changes={}
    for part in [model['condicoes'],tr]:
        for name,cells in part['depois'].items():changes.setdefault(name,{}).update(cells)
    for name,cells in changes.items():
        for a1,value in cells.items():write(name,a1,{'userEnteredValue':native_value(value)},'userEnteredValue')
    # Estilo e notas apenas no painel novo, ainda vazio na cópia nativa.
    requests.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',f'A{tr["inicio"]-2}:P{tr["fim"]}'),
        'cell':{'userEnteredFormat':{'backgroundColor':{'red':0.06,'green':0.06,'blue':0.07}}},'fields':'userEnteredFormat.backgroundColor'}})
    for a1,value,style in cfg['celulas']:
        if range_boundaries(a1)[1]<tr['inicio']-2:continue
        if style is not None:write('CONFIGURAÇÃO',a1,{'userEnteredFormat':format_(model['layout']['estilos'][style])},'userEnteredFormat')
    for merge in cfg['mescladas']:
        if range_boundaries(merge)[1]>=tr['inicio']-2:
            requests.append({'mergeCells':{'range':grid('CONFIGURAÇÃO',merge),'mergeType':'MERGE_ALL'}})
    for a1,note in cfg['notas'].items():
        if range_boundaries(a1)[1]>=tr['inicio']-2 or any(g['modalidade']==a1 for g in model['condicoes']['registros']):
            write('CONFIGURAÇÃO',a1,{'note':note},'note')
    relevant={g['modalidade'] for g in model['condicoes']['registros']}
    relevant|={g['base'] for g in model['registros'] if g['tipo']=='melhoria'}
    for name in ['CONFIGURAÇÃO','INVOCAÇÕES']:
        for menu in tabs[name]['menus']:
            if not (menu['onde'] in relevant or 'DADOS_DANOS' in menu.get('formula','')):continue
            for a1 in menu['onde'].split():
                rule={'condition':{'type':'ONE_OF_RANGE','values':[{'userEnteredValue':'='+pt(menu['formula'])}]},
                      'strict':bool(menu.get('estrito',False)),'showCustomUi':True}
                requests.append({'setDataValidation':{'range':grid(name,a1),'rule':rule}})
    for g in tr['registros']:
        requests.append({'setDataValidation':{'range':grid('CONFIGURAÇÃO',g['mestre_viu']),
            'rule':{'condition':{'type':'BOOLEAN'}}}})
    # Exportação desta frente em aba técnica própria: ANALISE v10 da cópia
    # permanece intacta. Isso não representa integração final em formato 11.
    rows=[{'values':[{'userEnteredValue':{'stringValue':x}} for x in ['chave','valor','célula','parte']]}]
    for row in exporta_condicoes(model['condicoes'])+exporta_danos(tr):
        rows.append({'values':[{'userEnteredValue':native_value(x)} for x in row]})
    requests.append({'updateCells':{'start':{'sheetId':IDS['CD_TESTE_ANALISE'],'rowIndex':0,'columnIndex':0},
        'rows':rows,'fields':'userEnteredValue'}})
    return [init]+[requests[i:i+30] for i in range(0,len(requests),30)]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo',type=Path,required=True)
    parser.add_argument('--destino',required=True)
    parser.add_argument('--saida',type=Path,required=True)
    a=parser.parse_args();model=json.loads(a.modelo.read_text(encoding='utf-8'))
    batches=preparar(model,a.destino);a.saida.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for i,batch in enumerate(batches):
        p=a.saida/f'{i:03d}.json'
        p.write_text(json.dumps({'spreadsheet_id':a.destino,'requests':batch},ensure_ascii=False),encoding='utf-8')
        manifest.append({'arquivo':p.name,'requests':len(batch),'bytes':p.stat().st_size})
    (a.saida/'manifesto.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'destino':a.destino,'lotes':len(batches),'requests':sum(len(x) for x in batches)}))
