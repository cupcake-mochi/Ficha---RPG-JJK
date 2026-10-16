#!/usr/bin/env python3
"""Gera lotes Sheets REST offline, após guardas de migracao.planejar.

Não envia nada. Requer snapshot integral das faixas e metadados nativos com
sheetId/gridProperties/rowGroups. A aplicação precisa de nova releitura igual,
registro de cada lote e conferência nativa; não reutilizar arquivos de outra cópia.
"""
import argparse,json,re
from pathlib import Path
from openpyxl.utils.cell import range_boundaries,get_column_letter as L
from migracao import planejar,sha,raw,uv

ENXUGAR_LINHAS = ('CONFIGURAÇÃO','DADOS_PROGRESSAO','DADOS_CRIACAO','DADOS_MELHORIAS','DADOS_RESTRICOES','ANALISE')

def pt(formula):
    quoted=False;out=[]
    for i,ch in enumerate(formula):
        if ch=='"':quoted=not quoted
        if not quoted:
            if ch==',':ch=';'
            elif ch=='.' and formula[i-1:i].isdigit() and formula[i+1:i+2].isdigit():ch=','
        out.append(ch)
    return ''.join(out)


def native_value(v):
    result=uv(v)
    if 'formulaValue' in result:result['formulaValue']=pt(result['formulaValue'])
    return result


def rgb(value):
    value=value.lstrip('#')[-6:]
    return {k:int(value[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}


def format_(style):
    font,bg,border,align,num=style;out={}
    if font:
        name,size,color,bold,italic=font
        out['textFormat']={'fontFamily':name,'fontSize':round(size),'foregroundColor':rgb(color),'bold':bold,'italic':italic}
    if bg:out['backgroundColor']=rgb(bg)
    if align:out.update(horizontalAlignment=align[0].upper(),verticalAlignment={'center':'MIDDLE','top':'TOP','bottom':'BOTTOM'}[align[1]],wrapStrategy='WRAP' if align[2] else 'CLIP')
    if border:
        styles={'thin':'SOLID','medium':'SOLID_MEDIUM','thick':'SOLID_THICK','double':'DOUBLE','dotted':'DOTTED','dashed':'DASHED','hair':'DOTTED'}
        out['borders']={side:{'style':styles.get(weight,'SOLID'),'color':rgb(color)} for side,(weight,color) in border.items() if side in ('top','bottom','left','right')}
    return out


def gerar(base,target,snapshot,plan):
    if sha(snapshot)!=plan['snapshot_sha256'] or sha(target)!=plan['alvo_sha256']:
        raise ValueError('Plano não corresponde ao snapshot/alvo')
    metadata=snapshot.get('metadata')
    if not metadata or metadata.get('spreadsheetId')!=plan['destino']:raise ValueError('Metadados nativos integrais ausentes')
    sheets={s['properties']['title']:s for s in metadata['sheets']}
    tabs={s['nome']:s for s in target['layout']['abas']};vals=raw(target);requests=[]
    def grid(sheet,coord):
        c,r,cc,rr=range_boundaries(coord)
        return {'sheetId':sheets[sheet]['properties']['sheetId'],'startRowIndex':r-1,'endRowIndex':rr,'startColumnIndex':c-1,'endColumnIndex':cc}
    def write(sheet,coord,cell,fields):
        requests.append({'updateCells':{'start':{'sheetId':sheets[sheet]['properties']['sheetId'],'rowIndex':range_boundaries(coord)[1]-1,'columnIndex':range_boundaries(coord)[0]-1},'rows':[{'values':[cell]}],'fields':fields}})
    # Grow technical grids before writing new validation helper columns.
    for name in plan['valores_alterados']:
        if name not in sheets or name not in tabs:continue
        current=sheets[name]['properties']['gridProperties'];tab=tabs[name];grow={}
        if tab['colunas']>current['columnCount']:grow['columnCount']=tab['colunas']
        if tab['linhas']>current['rowCount']:grow['rowCount']=tab['linhas']
        if grow:requests.append({'updateSheetProperties':{'properties':{'sheetId':sheets[name]['properties']['sheetId'],'gridProperties':grow},'fields':','.join('gridProperties.'+k for k in grow)}})
    cfg=tabs['CONFIGURAÇÃO'];end=cfg['linhas'];oldend=sheets['CONFIGURAÇÃO']['properties']['gridProperties']['rowCount']
    # Metadata must explicitly include these arrays, even when empty. A tool
    # which omits them has not provided enough evidence for this edit pass.
    if 'rowGroups' not in sheets['CONFIGURAÇÃO'] or 'merges' not in sheets['CONFIGURAÇÃO']:
        raise ValueError('Snapshot deve declarar merges e rowGroups de CONFIGURAÇÃO')
    for merge in sheets['CONFIGURAÇÃO']['merges']:
        if merge.get('startRowIndex',0)<732<merge.get('endRowIndex',0):
            raise ValueError('Mesclagem cruza limite da migração')
    for group in sorted(sheets['CONFIGURAÇÃO']['rowGroups'],key=lambda g:g['depth'],reverse=True):
        rg=group['range']
        if rg['startIndex']<732<rg['endIndex']:raise ValueError('Grupo cruza limite da migração')
        if rg['startIndex']>=732:requests.append({'deleteDimensionGroup':{'range':rg}})
    requests.append({'unmergeCells':{'range':grid('CONFIGURAÇÃO',f'A733:P{oldend}')}})
    requests.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',f'A733:P{oldend}'),'cell':{},'fields':'userEnteredValue,userEnteredFormat,note,dataValidation'}})
    # Removing an old group does not clear hiddenByUser on its former rows.
    # The native v9 copy retained rows 793–874 hidden after the group was
    # shortened to the two introduction rows, concealing Perícias and Ofícios.
    requests.append({'updateDimensionProperties':{'range':{'sheetId':sheets['CONFIGURAÇÃO']['properties']['sheetId'],'dimension':'ROWS','startIndex':732,'endIndex':end},'properties':{'pixelSize':25,'hiddenByUser':False},'fields':'pixelSize,hiddenByUser'}})
    # Paint the approved cards on their compacted geometry. No study tabs or
    # upper 3a/campaign controls are rebuilt.
    base_style=next(v[2] for v in cfg['celulas'] if v[0]=='A1')
    requests.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',f'A733:P{end}'),'cell':{'userEnteredFormat':format_(target['layout']['estilos'][base_style])},'fields':'userEnteredFormat'}})
    merged={}
    for region in cfg['mescladas']:
        c,r,cc,rr=range_boundaries(region)
        if r<733:continue
        for y in range(r,rr+1):
            for x in range(c,cc+1):merged[L(x)+str(y)]=region
        requests.append({'mergeCells':{'range':grid('CONFIGURAÇÃO',region),'mergeType':'MERGE_ALL'}})
    for coord,value,style,*_ in cfg['celulas']:
        c,r,_,_=range_boundaries(coord)
        if r<733:continue
        if coord in merged and coord!=merged[coord].split(':')[0]:continue
        cell={'userEnteredValue':native_value(value),'note':cfg.get('notas',{}).get(coord,'')}
        if style is not None:cell['userEnteredFormat']=format_(target['layout']['estilos'][style])
        if isinstance(value,bool):cell['dataValidation']={'condition':{'type':'BOOLEAN'},'strict':True}
        write('CONFIGURAÇÃO',coord,cell,'userEnteredValue,userEnteredFormat,note,dataValidation')
        if coord in merged and style is not None:
            requests.append({'repeatCell':{'range':grid('CONFIGURAÇÃO',merged[coord]),'cell':{'userEnteredFormat':format_(target['layout']['estilos'][style])},'fields':'userEnteredFormat'}})
    for r,height in cfg.get('linhas_alt',[]):
        if r>=733:requests.append({'updateDimensionProperties':{'range':{'sheetId':sheets['CONFIGURAÇÃO']['properties']['sheetId'],'dimension':'ROWS','startIndex':r-1,'endIndex':r},'properties':{'pixelSize':round(height*4/3)},'fields':'pixelSize'}})
    for r,rr,collapsed in cfg.get('grupos',{}).get('linhas',[]):
        if r<733:continue
        rg={'sheetId':sheets['CONFIGURAÇÃO']['properties']['sheetId'],'dimension':'ROWS','startIndex':r-1,'endIndex':rr}
        requests.append({'addDimensionGroup':{'range':rg}})
        requests.append({'updateDimensionGroup':{'dimensionGroup':{'range':rg,'depth':1,'collapsed':bool(collapsed)},'fields':'collapsed'}})
        requests.append({'updateDimensionProperties':{'range':rg,'properties':{'hiddenByUser':bool(collapsed)},'fields':'hiddenByUser'}})
    for sheet,changes in plan['valores_alterados'].items():
        if sheet=='CONFIGURAÇÃO':continue
        for coord,value in changes.items():
            # The guarded tail is deleted after all consumers are updated.
            # Clearing each retired cell first adds thousands of REST requests
            # without changing the final state. Retained rows still get clears.
            if sheet in ENXUGAR_LINHAS and range_boundaries(coord)[1]>tabs[sheet]['linhas']:continue
            write(sheet,coord,{'userEnteredValue':native_value(value)},'userEnteredValue')
    # Only changed validation sources outside CONFIGURAÇÃO need replacement.
    before={a['nome']:{m['onde']:m for m in a.get('menus',[])} for a in base['layout']['abas']}
    for sheet,tab in tabs.items():
        if sheet not in sheets:continue  # retired input tabs are not native production tabs
        for menu in tab.get('menus',[]):
            if sheet=='CONFIGURAÇÃO':
                if max(range_boundaries(x)[1] for x in menu['onde'].split())<733 and before.get(sheet,{}).get(menu['onde'])==menu:continue
            elif before.get(sheet,{}).get(menu['onde'])==menu:continue
            kind={'list':'ONE_OF_RANGE','custom':'CUSTOM_FORMULA'}[menu['tipo']]
            rule={'condition':{'type':kind,'values':[{'userEnteredValue':'='+pt(menu['formula'].lstrip('='))}]},'strict':menu.get('estrito',False),'showCustomUi':menu.get('mostra_seta',False)}
            for region in menu['onde'].split():requests.append({'setDataValidation':{'range':grid(sheet,region),'rule':rule}})
    for sheet,cells in plan['entradas'].items():
        for coord,cell in cells.items():write(sheet,coord,{'userEnteredValue':cell.get('userEnteredValue',{}),'note':cell.get('note','')},'userEnteredValue,note')
    # Delete surplus rows only after every consumer is updated. Do not shrink
    # columns or the 3b CB2:CC10 cache; do not remove studies or player choices.
    for sheet in ENXUGAR_LINHAS:
        count=sheets[sheet]['properties']['gridProperties']['rowCount'];needed=tabs[sheet]['linhas']
        if count>needed:requests.append({'deleteDimension':{'range':{'sheetId':sheets[sheet]['properties']['sheetId'],'dimension':'ROWS','startIndex':needed,'endIndex':count}}})
    return requests


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('base','alvo','snapshot','saida'):ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--prova-descartavel',type=Path,help='Prova do alvo exato, obrigatória para gerar lotes da revisão')
    a=ap.parse_args();base=json.loads(a.base.read_text());target=json.loads(a.alvo.read_text());snapshot=json.loads(a.snapshot.read_text())
    proof=json.loads(a.prova_descartavel.read_text()) if a.prova_descartavel else None
    plan=planejar(base,target,snapshot,permitir_revisao=proof is not None,prova=proof);requests=gerar(base,target,snapshot,plan)
    a.saida.mkdir(parents=True,exist_ok=False);parts=[];batch=[];size=0
    def save():
        name=f'{len(parts):04d}.json';payload={'spreadsheet_id':plan['destino'],'requests':list(batch)}
        content=json.dumps(payload,ensure_ascii=False,separators=(',',':'));(a.saida/name).write_text(content)
        parts.append({'arquivo':name,'sha256':sha(payload),'pedidos':len(batch)})
    for request in requests:
        n=len(json.dumps(request,ensure_ascii=False).encode())
        if batch and size+n>100000:save();batch=[];size=0
        batch.append(request);size+=n
    if batch:save()
    (a.saida/'manifesto.json').write_text(json.dumps({**{k:v for k,v in plan.items() if k not in ('entradas','valores_alterados')},'lotes':parts,'pedidos':len(requests),'atomico_entre_lotes':False,'falha_parcial':'Interromper; registrar último lote confirmado e estado. Não repetir cegamente; restaurar backup com guarda ou recomeçar em nova descartável, com snapshot renovado.'},ensure_ascii=False,indent=2))
    print(json.dumps({'destino':plan['destino'],'lotes':len(parts),'pedidos':len(requests)}))

if __name__=='__main__':main()
