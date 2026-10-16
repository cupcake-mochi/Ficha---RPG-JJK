#!/usr/bin/env python3
"""Casos de perda/identidade com modelos v9/v10 reais; snapshot SINTÉTICO."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import migracao as m

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--base',type=Path,required=True);ap.add_argument('--alvo',type=Path,required=True)
a=ap.parse_args();base=json.loads(a.base.read_text());target=json.loads(a.alvo.read_text())
raw=m.raw(base);old=m.contract(raw['ANALISE']);new=m.contract(m.raw(target)['ANALISE'])
now=datetime.now(timezone.utc)
notes={a['nome']:a.get('notas',{}) for a in base['layout']['abas']}
snapshot={'spreadsheetId':'TESTE-SINTETICO','backup_id':'BACKUP-SINTETICO','captured_at':now.isoformat(),
          'ranges':m.required_ranges(base,target),'cells':{s:{co:{'userEnteredValue':m.uv(v),'note':notes[s].get(co,'')}
          for co,v in cells.items()} for s,cells in raw.items()}}
checks=[]
def run(name,edit=None,error=None,verify=None):
    s=deepcopy(snapshot)
    if edit:edit(s)
    try:
        plan=m.planejar(base,target,s,now=now)
        ok=error is None and (verify(plan) if verify else True)
        detail='não bloqueou' if error else ''
    except ValueError as ex:
        ok=error is not None and error in str(ex);detail=str(ex)
    checks.append({'teste':name,'ok':bool(ok),'detalhe':detail})
    print(('OK ' if ok else 'FALHA ')+name+(' '+detail if not ok else ''),flush=True)

def put(s,key,value,note=None):
    sheet,coord=m.source(old[key][1]);s['cells'][sheet][coord]['userEnteredValue']=m.uv(value)
    if note is not None:s['cells'][sheet][coord]['note']=note

def populated(s):
    for group,n in [('familia',1),('familia',10),('melhoria',1),('melhoria',30),('restricao',1),('restricao',30)]:
        put(s,f'custom.{group}.{n}.nome',f'{group} {n} * ? ~')
    for slot,typ,name in [(1,'Ofício','Ofício inicial'),(2,'Perícia','Perícia inicial'),(130,'Perícia','Perícia final'),(131,'Ofício','Ofício final')]:
        for field,value in [('tipo',typ),('nome',name),('atributo','Essência'),('efeito','Texto integral\ncom segunda linha'),('mestre_viu',True)]:
            put(s,f'custom.treino.{slot}.{field}',value,'Nota manual preservada' if field=='efeito' else None)

def preserved(plan):
    for group,n in [('familia',1),('familia',10),('melhoria',1),('melhoria',30),('restricao',1),('restricao',30)]:
        sh,co=m.source(new[f'custom.{group}.{n}.nome'][1])
        if m.value(plan['entradas'][sh][co])!=f'{group} {n} * ? ~':return False
    for group in ('pericia','oficio'):
        sh,co=m.source(new[f'custom.{group}.2.efeito'][1])
        cell=plan['entradas'][sh][co]
        if cell['note']!='Nota manual preservada' or m.value(cell)!='Texto integral\ncom segunda linha':return False
    return {x['de']:x['para'] for x in plan['mapeamento']}.get('custom.treino.131')=='custom.oficio.2'

run('catálogos vazios migram; 3a fora do escopo de escrita')
run('primeira/última vagas, índices 130/131 e notas preservados por mapeamento',populated,verify=preserved)
for key in ('custom.familia.11.nome','custom.melhoria.31.nome','custom.restricao.31.nome'):
    run('bloqueia vaga retirada preenchida: '+key,lambda s,k=key:put(s,k,'Não pode desaparecer'),error='Vaga retirada preenchida')
run('mestre viu isolado também bloqueia perda',lambda s:put(s,'custom.familia.11.mestre_viu',True),error='Vaga retirada preenchida')
run('zero numérico em checkbox retirado não é falso vazio',lambda s:put(s,'custom.familia.11.mestre_viu',0),error='Vaga retirada preenchida')
run('registro parcial de treino sem tipo é preservado por bloqueio',lambda s:put(s,'custom.treino.131.efeito','Descrição sem nome'),error='sem tipo válido')
def overflow(s):
    for n in range(1,12):
        put(s,f'custom.treino.{n}.tipo','Perícia');put(s,f'custom.treino.{n}.nome',f'Perícia {n}')
run('onze Perícias não ocupam vaga de Ofício',overflow,error='Capacidade excedida')
run('conteúdo avulso em área retirada é detectado',lambda s:s['cells']['CONFIGURAÇÃO'].update({'A1800':{'userEnteredValue':m.uv('Nota fora de campo')}}),error='Conteúdo divergente')
run('nota manual fora dos campos bloqueia reconstrução pontual',lambda s:s['cells']['CONFIGURAÇÃO'].update({'A1800':{'note':'Não apagar'}}),error='Nota manual')
run('snapshot incompleto nunca vira vazio',lambda s:s['ranges'].pop('CONFIGURAÇÃO'),error='Snapshot incompleto')
run('snapshot vencido exige releitura',lambda s:s.update(captured_at=(now-timedelta(hours=1)).isoformat()),error='15 minutos')
run('oficial recusada',lambda s:s.update(spreadsheetId=m.OFICIAL),error='ficha oficial')
run('revisão exige prova descartável do alvo exato',lambda s:s.update(spreadsheetId=m.REVISAO),error='prova descartável')
run('backup precisa ser outra planilha',lambda s:s.update(backup_id=s['spreadsheetId']),error='backup nativo')
run('fórmula de entrada movida exige revisão explícita',lambda s:put(s,'custom.familia.1.nome','=A1'),error='Fórmula de entrada movida')
# Native padding is also destructive scope: two extra visible grid rows must
# not hide a manually entered value outside the model's nominal last row.
def native_meta(s):
    s['metadata']={'spreadsheetId':s['spreadsheetId'],'sheets':[{'properties':{'sheetId':i+1,'title':a['nome'],'gridProperties':{'rowCount':a['linhas']+(2 if a['nome']=='CONFIGURAÇÃO' else 0),'columnCount':a['colunas']}},'rowGroups':[],'merges':[]} for i,a in enumerate(base['layout']['abas'])]}
    s['ranges']=m.required_ranges(base,target,s['metadata'])
def tail_content(s):
    native_meta(s);s['cells']['CONFIGURAÇÃO']['A18661']={'userEnteredValue':m.uv('Não cortar a cauda nativa')}
run('conteúdo nas duas linhas extras da grade nativa bloqueia corte',tail_content,error='Conteúdo divergente')
def lots_ok(plan):
    # Recreate the exact snapshot deterministically: metadata and cells are
    # unchanged by the guard. This is a local recipe, not a native test.
    from lotes import gerar
    s=deepcopy(snapshot);native_meta(s)
    requests=gerar(base,target,s,plan)
    if not requests:return False
    ids={a['properties']['title']:a['properties']['sheetId'] for a in s['metadata']['sheets']}
    deleted=[r['deleteDimension']['range'] for r in requests if 'deleteDimension' in r]
    if len(deleted)!=6 or not all(r['dimension']=='ROWS' for r in deleted):return False
    # Original 3a inputs, player choices and the group-7 cache are not cleared.
    for r in requests:
        if 'repeatCell' in r and r['repeatCell']['range']['sheetId']==ids['CONFIGURAÇÃO']:
            if r['repeatCell']['range']['startRowIndex']<732:return False
    return not any('addSheet' in r or 'deleteSheet' in r for r in requests)
run('lotes REST pontuais, sem abas apagadas ou reset dos campos anteriores',native_meta,verify=lots_ok)
print(json.dumps({'resultado':'OK' if all(c['ok'] for c in checks) else 'FALHA','tipo':'simulação; não é snapshot Google','checagens':checks},ensure_ascii=False))
raise SystemExit(not all(c['ok'] for c in checks))
