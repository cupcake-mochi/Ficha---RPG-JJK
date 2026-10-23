"""Monta delta e recuperação a partir das capturas privadas atuais; sem rede.

Não reconstrói fichas. Lotes preservam somente userEnteredValue e removem
exclusivamente ANALISE E:L, comprovadas vazias. Aplicação exige preflight.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

OFFICIAL = '1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro'
CANDIDATE = '1VO61vXu8FjsDvc27c5c_ke93be-4Ta2rGaToDCv0Wgc'


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def cells(doc):
    out = {}
    for sh in doc['sheets']:
        for block in sh.get('data', []):
            for ri, row in enumerate(block.get('rowData', []), block.get('startRow', 0)):
                for ci, cell in enumerate(row.get('values', []), block.get('startColumn', 0)):
                    key = (sh['properties']['title'], ri, ci)
                    assert key not in out
                    out[key] = cell
    return out


def collect(folder, pattern, identity):
    out = {}
    for p in sorted(folder.glob(pattern)):
        doc = read(p)
        assert doc['spreadsheetId'] == identity, p.name
        block = cells(doc)
        assert not (out.keys() & block.keys()), p.name
        out.update(block)
    return out


def update(sid, row, col, values):
    return {'updateCells': {'range': {'sheetId': sid, 'startRowIndex': row,
        'endRowIndex': row+len(values), 'startColumnIndex': col, 'endColumnIndex': col+1},
        'rows': [{'values': [{'userEnteredValue': v}]} for v in values],
        'fields': 'userEnteredValue'}}


def prepare(folder):
    meta = read(folder/'oficial-meta-1.json')
    assert meta['spreadsheetId'] == OFFICIAL
    sheets = {s['properties']['title']: s['properties'] for s in meta['sheets']}
    assert len(sheets) == 27
    assert sheets['ANALISE']['gridProperties'] == dict(rowCount=18394, columnCount=12, hideGridlines=True)
    full = read(folder/'ensaio-estrutura-completa.json')['updatedSpreadsheet']
    aid = sheets['ANALISE']['sheetId']
    assert all(n['range']['sheetId'] != aid for n in full.get('namedRanges', []))
    analysis = next(s for s in full['sheets'] if s['properties']['title']=='ANALISE')
    assert not analysis.get('protectedRanges') and not analysis.get('merges')
    excess_paths = list(folder.glob('oficial-excedente-*.json'))
    assert {int(p.stem.split('-')[-1]) for p in excess_paths} == set(range(1,18395,4000))
    for p in excess_paths:
        doc = read(p)
        assert len(doc['sheets']) == 1
        assert doc['sheets'][0]['properties']['title'] == 'ANALISE'
        assert doc['sheets'][0]['properties']['gridProperties']['columnCount'] == 12
    excess = collect(folder, 'oficial-excedente-*.json', OFFICIAL)
    assert all(not any(cell.get(k) for k in ('userEnteredValue','note','dataValidation')) for cell in excess.values())
    before = collect(folder, 'oficial-fd-fx-*.json', OFFICIAL)
    proposed = collect(folder, 'c-fd-fx-*.json', CANDIDATE)
    expected_keys = {('DADOS_R53',r,c) for r in range(1,250) for c in (159,179)}
    assert before.keys() == proposed.keys() == expected_keys
    stages=[]
    def stage(name, requests, reverse, checks):
        stages.append(dict(nome=name,requests=requests,rollback=reverse,precondicoes=checks,
            requests_sha256=digest(requests)))
    for start in range(1,250,10):
        req, rev, checks = [], [], []
        for col in (159,179):
            old, new = [], []
            for row in range(start,min(250,start+10)):
                key=('DADOS_R53',row,col)
                a,b=before[key],proposed[key]
                assert 'errorValue' not in a.get('effectiveValue',{})
                assert 'formulaValue' in a['userEnteredValue'] and 'formulaValue' in b['userEnteredValue']
                assert len(b['userEnteredValue']['formulaValue']) < 32767
                old.append(a['userEnteredValue']);new.append(b['userEnteredValue'])
                checks.append(dict(aba=key[0],row=row,col=col,antes=old[-1],depois=new[-1]))
            req.append(update(sheets['DADOS_R53']['sheetId'],start,col,new))
            rev.append(update(sheets['DADOS_R53']['sheetId'],start,col,old))
        stage('formulas-'+str(start+1),req,rev,checks)
    analise=collect(folder,'oficial-analise-*.json',OFFICIAL)
    keys=[analise[('ANALISE',r,0)]['effectiveValue']['stringValue'] for r in range(1,18394)]
    assert len(keys)==len(set(keys))==18393
    converted=0
    for start in range(1,18394,2000):
        req,rev,checks=[],[],[]
        run=[]; runstart=None
        def flush():
            nonlocal run, runstart
            if run:
                req.append(update(aid,runstart,2,[v[1] for v in run]))
                rev.append(update(aid,runstart,2,[v[0] for v in run]))
                run=[]
        for row in range(start,min(18394,start+2000)):
            cell=analise[('ANALISE',row,2)];old=cell.get('userEnteredValue',{})
            m=re.fullmatch(r'="((?:[^"]|"")*)"',old.get('formulaValue',''))
            if not m: flush();continue
            text=m[1].replace('""','"')
            assert cell['effectiveValue']=={'stringValue':text}
            # updateCells usa stringValue RAW, sem consumir apóstrofo. O escape
            # RichText continua no carregador para recuperação por edição nativa.
            new={'stringValue':text}
            if not run:runstart=row
            run.append((old,new));converted+=1
            checks.append(dict(aba='ANALISE',row=row,col=2,antes=old,depois=new))
        flush()
        if req:stage('literais-'+str(start+1),req,rev,checks)
    assert converted==15869
    old_bars=cells(read(folder/'oficial-sentinelas.json'))
    new_bars=cells(read(folder/'c-sentinelas.json'))
    req,rev,checks=[],[],[]
    for row in (25,29,33):
        key=('FICHA',row,18);old=old_bars[key]['userEnteredValue'];new=new_bars[key]['userEnteredValue']
        assert 'SPARKLINE' in new['formulaValue'] and 'IF(OR(N(' in new['formulaValue']
        req.append(update(sheets['FICHA']['sheetId'],row,18,[new]));rev.append(update(sheets['FICHA']['sheetId'],row,18,[old]))
        checks.append(dict(aba='FICHA',row=row,col=18,antes=old,depois=new))
    stage('barras',req,rev,checks)
    # Reconstrução dos formatos comprimidos na captura, incluindo os vazios.
    restore=[{'appendDimension':{'sheetId':aid,'dimension':'COLUMNS','length':8}}]
    count=0
    format_paths = list(folder.glob('excedente-formatos-*.json'))
    assert {int(p.stem.split('-')[-1]) for p in format_paths} == set(range(1,18395,1000))
    for p in sorted(format_paths):
        doc=read(p);pos=0
        assert doc['start'] == int(p.stem.split('-')[-1])
        assert doc['end'] == min(18394, doc['start']+999)
        for idx,n in doc['runs']:
            left=n
            while left:
                row=(doc['start']-1)+pos//8;col=4+pos%8
                take=min(left,8-pos%8)
                if col==4 and left>=8:take=(left//8)*8
                endrow=row+(take//8 if take>=8 else 1)
                endcol=12 if take>=8 else col+take
                restore.append({'repeatCell':{'range':{'sheetId':aid,'startRowIndex':row,'endRowIndex':endrow,'startColumnIndex':col,'endColumnIndex':endcol},'cell':{'userEnteredFormat':doc['pool'][idx]},'fields':'userEnteredFormat'}})
                pos+=take;left-=take
        assert pos==(doc['end']-doc['start']+1)*8
        count+=pos
    assert count==18394*8
    stage('grade',[{'deleteDimension':{'range':{'sheetId':aid,'dimension':'COLUMNS','startIndex':4,'endIndex':12}}}],restore,
        [dict(aba='ANALISE',colunas_antes=12,colunas_depois=4,excedente_vazio=True)])
    result=dict(oficial=OFFICIAL,snapshot_meta=read(folder/'oficial-meta-0.json'),
        etapas=stages,resumo=dict(formulas=498,literais=converted,barras=3,posicoes_removidas=count,
        etapas=len(stages),regra='Preflight de cada célula e dimensão antes de aplicar ou reverter; divergência interrompe.'))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('pasta',type=Path);args=parser.parse_args()
    result=prepare(args.pasta)
    destination=args.pasta/'delta.json'
    with destination.open('x') as f:json.dump(result,f,ensure_ascii=False)
    print(json.dumps(result['resumo'],ensure_ascii=False))
