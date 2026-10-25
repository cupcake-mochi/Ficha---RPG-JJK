"""Prepara correção focal de Ritual a partir de captura nativa; sem rede.

Não aplica o lote. A ficha usada como exemplo continua somente leitura.
Antes de aplicar: snapshot atual e igualdade das doze fórmulas anteriores.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def prepare(document):
    found=[]
    pattern=re.compile(r'^=IF\(AND\(NOT\(OR\(FALSE\)\);\$LI(\d+)="Ritual"\);"Conferir Técnica Inata";""\)$')
    for sheet in document['sheets']:
        if sheet['properties']['title']!='DADOS_AM':continue
        sid=sheet['properties']['sheetId']
        for block in sheet.get('data',[]):
            for row,item in enumerate(block.get('rowData',[]),block.get('startRow',0)):
                for col,cell in enumerate(item.get('values',[]),block.get('startColumn',0)):
                    before=cell.get('userEnteredValue',{}).get('formulaValue','')
                    match=pattern.fullmatch(before)
                    if not match:continue
                    assert int(match[1])==row+1
                    condition=f'$LI{row+1}="Ritual"'
                    after=before.replace(condition,f'AND({condition};NOT((DADOS_AM!$A$2=1)))')
                    found.append(dict(sheetId=sid,row=row,col=col,antes=before,depois=after))
    assert len(found)==12 and {f['row'] for f in found}==set(range(1,13)), 'Captura incompleta ou fórmula divergente; parar'
    def requests(field):
        return [{'updateCells':{'range':{'sheetId':f['sheetId'],'startRowIndex':f['row'],
            'endRowIndex':f['row']+1,'startColumnIndex':f['col'],'endColumnIndex':f['col']+1},
            'rows':[{'values':[{'userEnteredValue':{'formulaValue':f[field]}}]}],
            'fields':'userEnteredValue'}} for f in found]
    return dict(alvo=document['spreadsheetId'],precondicoes=found,
        requests=requests('depois'),rollback=requests('antes'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('captura',type=Path);p.add_argument('saida',type=Path)
    a=p.parse_args();data=prepare(json.loads(a.captura.read_text()))
    private=Path(__file__).resolve().parents[2]/'nuvem-b47/saidas'
    assert a.saida.resolve().is_relative_to(private.resolve()), 'Salvar lote somente na área privada ignorada'
    with a.saida.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps({'celulas':len(data['requests']), 'sha256_pedidos':hashlib.sha256(
        json.dumps(data['requests'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        'aplicado':False}))
