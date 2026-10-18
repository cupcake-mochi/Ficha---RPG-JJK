"""Planeja a migração horizontal sem rede; não executa construir/continuar.

Preserva entradas por cópia nativa da aba; reescreve somente fórmulas cuja
referência mudou, notas auditadas e estrutura da apresentação. Recibos e
snapshots devem permanecer fora do Git.
"""
import argparse
import json
import sys
from pathlib import Path
from openpyxl.utils.cell import coordinate_to_tuple, range_boundaries, get_column_letter as L

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT/'ficha-v01'),str(ROOT/'capacidade-b47')]
import configuracao_horizontal as horizontal
from lotes import native_value, format_, rgb


def load(path):
    d=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    return d.get('structuredContent',d)


def apresentar(target, sid, *, excluir=()):
    """Somente títulos, aberturas e índice novos; nunca entradas do jogador."""
    a=next(x for x in target['layout']['abas'] if x['nome']=='CONFIGURAÇÃO')
    cells={x[0]:x for x in a['celulas']};links={x['celula']:x for x in a.get('links_paineis',[])}
    requests=[]
    for region in a['apresentacao']:
        if region in excluir:continue
        c,r,cc,rr=range_boundaries(region);addr=L(c)+str(r);record=cells[addr]
        grid=dict(sheetId=sid,startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc)
        style=target['layout']['estilos'][record[2]];fmt=format_(style)
        if style[3] and style[3][3]:fmt['textRotation']={'angle':style[3][3]}
        if addr in links:fmt['textFormat']['link']={'uri':f'#gid={sid}&range={links[addr]["alvo"]}'}
        requests.extend([
            {'mergeCells':{'range':grid,'mergeType':'MERGE_ALL'}},
            {'repeatCell':{'range':grid,'cell':{'userEnteredFormat':fmt},'fields':'userEnteredFormat'}},
            {'updateCells':{'start':dict(sheetId=sid,rowIndex=r-1,columnIndex=c-1),
                            'rows':[{'values':[{'userEnteredValue':native_value(record[1])}]}],'fields':'userEnteredValue'}},
        ])
    return requests


def regras_condicionais(target,sid):
    a=next(x for x in target['layout']['abas'] if x['nome']=='CONFIGURAÇÃO')
    out=[]
    for rule in a.get('condicional_gs',[]):
        ranges=[]
        for region in rule['faixas']:
            c,r,cc,rr=range_boundaries(region)
            ranges.append(dict(sheetId=sid,startRowIndex=r-1,endRowIndex=rr,startColumnIndex=c-1,endColumnIndex=cc))
        condition={'type':'CUSTOM_FORMULA','values':[{'userEnteredValue':native_value(rule['formula'])['formulaValue']}]} if rule.get('formula') else {'type':'TEXT_CONTAINS','values':[{'userEnteredValue':rule['contem']}]}
        fmt={}
        if rule.get('fundo'):fmt['backgroundColor']=rgb(rule['fundo'])
        if rule.get('fonte'):fmt['textFormat']={'foregroundColor':rgb(rule['fonte'])}
        out.append({'addConditionalFormatRule':{'index':len(out),'rule':{'ranges':ranges,'booleanRule':{'condition':condition,'format':fmt}}}})
    return out


def planejar(base, target, metadata, native):
    meta=metadata.get('updatedSpreadsheet',metadata)
    sheets={s['properties']['title']:s for s in meta['sheets']}
    cfg=sheets['CONFIGURAÇÃO'];sid=cfg['properties']['sheetId'];old=cfg['properties']['gridProperties']
    assert old['columnCount']==16 and old['rowCount']==2812, 'Origem não é a vertical auditada'
    tabs={a['nome']:a for a in target['layout']['abas']};new=tabs['CONFIGURAÇÃO']
    assert new['horizontal']['versao']==1 and new['linhas']<=405
    tmp=90847001
    assert all(s['properties']['sheetId']!=tmp for s in meta['sheets'])
    sourceid=meta['spreadsheetId']
    actual={}
    for s in native['sheets']:
        for d in s.get('data',[]):
            for y,row in enumerate(d.get('rowData',[])):
                for x,cell in enumerate(row.get('values',[])):
                    actual[L(d.get('startColumn',0)+x+1)+str(d.get('startRow',0)+y+1)]=cell
    original=next(a for a in base['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    source_notes=original['notas']
    assert {a:c['note'] for a,c in actual.items() if c.get('note')}==source_notes, 'Notas mudaram desde a auditoria; reler antes de planejar'

    def grid(sid, ra,ca,rb,cb):
        return dict(sheetId=sid,startRowIndex=ra-1,endRowIndex=rb,startColumnIndex=ca-1,endColumnIndex=cb)
    def at(sid,addr):
        r,c=coordinate_to_tuple(addr);return dict(sheetId=sid,rowIndex=r-1,columnIndex=c-1)
    def put(sid,addr,cell,fields):
        return {'updateCells':{'start':at(sid,addr),'rows':[{'values':[cell]}],'fields':fields}}
    phases=[]
    prep=[{'duplicateSheet':{'sourceSheetId':sid,'newSheetId':tmp,'newSheetName':'__CFG_ORIGEM_HORIZONTAL__'}},
          {'updateSheetProperties':{'properties':{'sheetId':tmp,'hidden':True},'fields':'hidden'}},
          {'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':{'columnCount':new['colunas']}},'fields':'gridProperties.columnCount'}}]
    for g in sorted(cfg.get('rowGroups',[]),key=lambda x:x.get('depth',1),reverse=True):
        prep.append({'deleteDimensionGroup':{'range':g['range']}})
    assert 'conditionalFormats' in cfg, 'Reler regras condicionais antes da migração'
    # copyPaste também leva regras condicionais. Evitar duplicação e faixas
    # antigas sobrevivendo sob os painéis; recriar as regras canônicas ao fim.
    for owner in (sid,tmp):
        prep.extend({'deleteConditionalFormatRule':{'sheetId':owner,'index':0}} for _ in cfg['conditionalFormats'])
    for title in cfg.get('merges',[]):
        if title.get('startRowIndex')==1 and title.get('startColumnIndex')==1:
            prep.append({'unmergeCells':{'range':{**title,'sheetId':tmp}}})
    area=grid(sid,1,1,old['rowCount'],new['colunas'])
    prep.extend([{'unmergeCells':{'range':area}},
                 {'repeatCell':{'range':area,'cell':{'userEnteredFormat':format_(target['layout']['estilos'][next(x[2] for x in new['celulas'] if x[0]=='B1')])},'fields':'userEnteredValue,note,dataValidation,userEnteredFormat'}}])
    phases.append(('preparar',prep))
    copies=[]
    for ra,ca,rb,cb,dr,dc,panel in horizontal.BLOCOS:
        if panel==0:rb=170  # a cauda vazia não pertence ao painel Geral
        copies.append({'copyPaste':{'source':grid(tmp,ra,ca,rb,cb),'destination':grid(sid,ra+dr,ca+dc,rb+dr,cb+dc),'pasteType':'PASTE_NORMAL','pasteOrientation':'NORMAL'}})
    # A mescla do título antigo atravessava os dois painéis; agora pertence ao Geral.
    title=horizontal.faixa('B2:H3');c,r,cc,rr=range_boundaries(title)
    copies.append({'mergeCells':{'range':grid(sid,r,c,rr,cc),'mergeType':'MERGE_ALL'}})
    phases.append(('copiar_cartoes',copies))

    values_before={a['nome']:{x[0]:x[1] for x in a['celulas']} for a in base['layout']['abas']}
    formulas=[];count={}
    for a in target['layout']['abas']:
        name=a['nome']
        if name not in sheets:continue
        # Entradas literais são preservadas pela cópia nativa, não substituídas pelo modelo.
        for addr,v in {x[0]:x[1] for x in a['celulas']}.items():
            if not isinstance(v,str) or not (v.startswith('=') or v.startswith('CONFIGURAÇÃO!') or v.startswith("'CONFIGURAÇÃO'!")):continue
            if name!='CONFIGURAÇÃO' and values_before.get(name,{}).get(addr)==v:continue
            formulas.append(put(sheets[name]['properties']['sheetId'],addr,{'userEnteredValue':native_value(v)},'userEnteredValue'))
            count[name]=count.get(name,0)+1
    # Dividir por tamanho, não por uma contagem que esconda fórmulas longas.
    chunk=[];size=0
    for q in formulas:
        n=len(json.dumps(q,ensure_ascii=False))
        if chunk and size+n>110000:phases.append(('formulas',chunk));chunk=[];size=0
        chunk.append(q);size+=n
    if chunk:phases.append(('formulas',chunk))

    keep={}
    removed={x['celula']:x['texto'] for x in target['auditoria']['notas_removidas']}
    for addr,cell in actual.items():
        note=cell.get('note')
        if note and removed.get(addr)!=note:keep[horizontal.coord(addr)]=note
    for s in new['horizontal']['secoes']:
        addr=L(s['coluna'])+'2';keep[addr]=new['notas'][addr]
    notes=[]
    for s in new['horizontal']['secoes']:
        lo=s['coluna'];hi=s['fim'];rows=[]
        for r in range(1,new['linhas']+1):
            rows.append({'values':[{'note':keep[L(c)+str(r)]} if L(c)+str(r) in keep else {} for c in range(lo,hi+1)]})
        notes.append({'updateCells':{'range':grid(sid,1,lo,new['linhas'],hi),'rows':rows,'fields':'note'}})
    # Notas e campos são independentes: apagar uma ajuda não apaga a entrada.
    phases.append(('notas',notes))

    structure=[]
    structure.extend(apresentar(target,sid))
    structure.extend(regras_condicionais(target,sid))
    for lo,hi,width in new['colunas_larg']:
        structure.append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'COLUMNS','startIndex':lo-1,'endIndex':hi},'properties':{'pixelSize':round(width*8-1),'hiddenByUser':False},'fields':'pixelSize,hiddenByUser'}})
    heights={r:round(h*4/3) for r,h in new['linhas_alt']}
    spans=[]
    for r,h in sorted(heights.items()):
        if spans and spans[-1][1]==r-1 and spans[-1][2]==h:spans[-1][1]=r
        else:spans.append([r,r,h])
    for lo,hi,h in spans:
        structure.append({'updateDimensionProperties':{'range':{'sheetId':sid,'dimension':'ROWS','startIndex':lo-1,'endIndex':hi},'properties':{'pixelSize':h,'hiddenByUser':False},'fields':'pixelSize,hiddenByUser'}})
    structure.append({'updateSheetProperties':{'properties':{'sheetId':sid,'gridProperties':{'rowCount':new['linhas'],'columnGroupControlAfter':False,'rowGroupControlAfter':False}},'fields':'gridProperties.rowCount,gridProperties.columnGroupControlAfter,gridProperties.rowGroupControlAfter'}})
    for lo,hi,closed in new['grupos']['colunas']:
        rg={'sheetId':sid,'dimension':'COLUMNS','startIndex':lo-1,'endIndex':hi}
        structure.append({'addDimensionGroup':{'range':rg}})
        structure.append({'updateDimensionGroup':{'dimensionGroup':{'range':rg,'depth':1,'collapsed':closed},'fields':'collapsed'}})
        structure.append({'updateDimensionProperties':{'range':rg,'properties':{'hiddenByUser':closed},'fields':'hiddenByUser'}})
    phases.append(('estrutura',structure))
    phases.append(('retirar_origem',[{'deleteSheet':{'sheetId':tmp}}]))
    return {'destino':sourceid,'formula_por_aba':count,'notas_removidas':len(removed),'notas_finais':len(keep),'secoes':14,'linhas':new['linhas'],'colunas':new['colunas'],'fases':[{'nome':n,'requests':q} for n,q in phases]}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','alvo','metadata','nativo','saida']:p.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();plan=planejar(load(args.base),load(args.alvo),load(args.metadata),load(args.nativo))
    args.saida.write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in plan.items() if k!='fases'},ensure_ascii=False))
    print([(x['nome'],len(x['requests'])) for x in plan['fases']])
