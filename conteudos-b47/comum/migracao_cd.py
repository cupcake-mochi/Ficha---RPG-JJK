"""Planejamento offline da migração pontual B47 10→11, sem acesso Google.

Não reutiliza a migração 9→10. Exige cópia nativa/backup novos, cobertura
explícita e releitura idêntica; nenhuma entrada antiga muda de endereço.
O plano ainda não é uma autorização de envio e não executa lotes.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'capacidade-b47'))
from migracao import sha,raw,contract,source,equivalent,covered,value,OFICIAL,REVISAO
from openpyxl.utils.cell import range_boundaries,get_column_letter as L

RETIRADAS={'INVOCAÇÃO','CATÁLOGO','DADOS_INV'}
NOVAS={'DADOS_DANOS','DADOS_FORMAS','DADOS_APTIDOES','DADOS_TALENTOS','DADOS_ENTIDADES'}


def contrato(base,alvo):
    old,new=raw(base),raw(alvo)
    a,b=contract(old['ANALISE']),contract(new['ANALISE'])
    if len(a)!=7356 or len(b)!=8190 or str(a['formato.versao'][0])!='10' or str(b['formato.versao'][0])!='11':
        raise ValueError('Exige contrato completo 10/7356 → 11/8190')
    # contract() sozinho poderia esconder duplicatas: conferir as linhas cruas.
    for cells,expected in [(old['ANALISE'],7356),(new['ANALISE'],8190)]:
        if len([c for c in cells if re.fullmatch(r'A\d+',c) and c!='A1'])!=expected:
            raise ValueError('Chaves duplicadas ou linhas inesperadas na ANALISE')
    if list(a)!=list(b)[:len(a)]:raise ValueError('Identidade/ordem antiga alterada')
    for key,row in a.items():
        if key=='formato.versao':
            if row[1:]!=b[key][1:]:raise ValueError('Fonte/escopo da versão alterados')
        elif row!=b[key]:raise ValueError('Contrato antigo alterado: '+key)
    if set(new)-set(old)!=NOVAS:raise ValueError('Conjunto de novas auxiliares inesperado')
    # As 3 abas históricas não existem na ficha nativa e não são alvo de migração.
    if set(old)&RETIRADAS!=RETIRADAS:raise ValueError('Baseline exportada sem as abas históricas esperadas')
    return old,new,a,b


def delta(base,alvo):
    old,new,_,_=contrato(base,alvo)
    changes={}
    for sheet,cells in new.items():
        if sheet in RETIRADAS:continue
        before=old.get(sheet,{})
        different={c:cells.get(c) for c in before.keys()|cells.keys()
                   if not equivalent(before.get(c),cells.get(c))}
        if different:changes[sheet]=different
    return changes


def faixas(base,alvo,metadata):
    """Inclui vizinhos e notas de toda a área nova, mesmo nas linhas de padding."""
    changes=delta(base,alvo)
    sheets={s['properties']['title']:s['properties'] for s in metadata['sheets']}
    if NOVAS & sheets.keys():raise ValueError('Há auxiliar C no destino; possível reaplicação')
    required={}
    for name,cells in changes.items():
        if name in NOVAS:continue
        if name not in sheets:raise ValueError('Aba nativa necessária ausente: '+name)
        boxes=[range_boundaries(c) for c in cells]
        if boxes:required[name]=[f'{L(min(x[0] for x in boxes))}{min(x[1] for x in boxes)}:{L(max(x[2] for x in boxes))}{max(x[3] for x in boxes)}']
    old_cfg=next(a for a in base['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    new_cfg=next(a for a in alvo['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    # O painel começa nas duas últimas linhas vazias nativas; nunca presumir
    # que padding já existente esteja vazio ou sem notas.
    required.setdefault('CONFIGURAÇÃO',[]).append(f'A{old_cfg["linhas"]+2}:P{new_cfg["linhas"]+2}')
    # Também guardar modalidades novas, cujo valor default é vazio e portanto
    # não aparece no delta de valores.
    for g in alvo['condicoes']['registros']:
        required['CONFIGURAÇÃO'].append(g['modalidade'])
    # A prova da versão efetiva não depende de confiar no título do documento.
    required.setdefault('ANALISE',[]).append('A1:D2')
    # Uma faixa por aba evita leituras sobrepostas, recusadas pelo normalizador
    # de snapshot. O leitor nativo divide este retângulo em blocos delimitados.
    out={}
    for name,areas in required.items():
        boxes=[range_boundaries(a) for a in areas]
        out[name]=[f'{L(min(x[0] for x in boxes))}{min(x[1] for x in boxes)}:{L(max(x[2] for x in boxes))}{max(x[3] for x in boxes)}']
    return out


def agora(value,now,label):
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError(label+' exige fuso explícito')
    if not 0<=(now-t).total_seconds()<=900:raise ValueError(label+' deve ter no máximo 15 minutos')
    return t


def planejar(base,alvo,snapshot,*,now=None,prova=None):
    old,new,bc,nc=contrato(base,alvo)
    now=now or datetime.now(timezone.utc)
    dest=snapshot.get('spreadsheetId')
    if not dest or dest==OFICIAL:raise ValueError('Destino ausente ou ficha oficial')
    backup=snapshot.get('backup_id')
    if not backup or backup in (dest,OFICIAL):raise ValueError('Exige backup nativo integral distinto')
    captured=agora(snapshot['captured_at'],now,'Snapshot')
    backup_time=agora(snapshot['backup_created_at'],now,'Backup')
    if backup_time>captured:raise ValueError('Backup deve preceder o snapshot')
    metadata=snapshot.get('metadata',{})
    if metadata.get('spreadsheetId')!=dest:raise ValueError('Metadados de outro destino')
    if dest==REVISAO:
        # Construção vazia não substitui ensaio da migração com os dados reais.
        if not prova or any(prova.get(k)!=v for k,v in {
            'resultado':'OK','tipo':'migracao-cd-nativa','alvo_sha256':sha(alvo),
            'entradas_notas_preservadas':True,'codigo_relido_igual':True,'erros_formula':0}.items()):
            raise ValueError('Revisão exige prova nativa da migração do alvo exato')
        if prova.get('destino') in (None,REVISAO,OFICIAL,dest):raise ValueError('Prova deve vir de outra descartável')
    required=faixas(base,alvo,metadata)
    for sheet,areas in required.items():
        for area in areas:
            c,r,cc,rr=range_boundaries(area)
            for y in range(r,rr+1):
                for x in range(c,cc+1):
                    if not covered(snapshot,sheet,L(x)+str(y)):
                        raise ValueError('Snapshot incompleto: '+sheet+'!'+L(x)+str(y))
    live=snapshot['cells']
    if value(live.get('ANALISE',{}).get('A2',{}))!='formato.versao' or str(value(live.get('ANALISE',{}).get('B2',{})))!='10':
        raise ValueError('Destino nativo não está no contrato 10')
    changes=delta(base,alvo)
    # Não usar a exportação compactada GS como delta de valores: abaixo/cópias
    # são preenchidos em runtime. O modelo integral contém todos os destinos.
    for sheet,cells in changes.items():
        if sheet in NOVAS:continue
        for coord in cells:
            cell=live.get(sheet,{}).get(coord,{})
            if not equivalent(value(cell),old[sheet].get(coord)):
                raise ValueError('Conteúdo divergente da base: '+sheet+'!'+coord)
    # Nenhum conteúdo inesperado pode ser soterrado pelo desenho da área nova.
    cfg_old=next(a for a in base['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    cfg_new=next(a for a in alvo['layout']['abas'] if a['nome']=='CONFIGURAÇÃO')
    for r in range(cfg_old['linhas']+2,cfg_new['linhas']+3):
        for c in range(1,17):
            coord=L(c)+str(r)
            if not equivalent(value(live.get('CONFIGURAÇÃO',{}).get(coord,{})),old['CONFIGURAÇÃO'].get(coord)):
                raise ValueError('Área nova ocupada: CONFIGURAÇÃO!'+coord)
    for g in alvo['condicoes']['registros']:
        coord=g['modalidade']
        if not equivalent(value(live.get('CONFIGURAÇÃO',{}).get(coord,{})),old['CONFIGURAÇÃO'].get(coord)):
            raise ValueError('Campo de modalidade ocupado: '+coord)
    preserved=[]
    for key,row in bc.items():
        origin=source(row[1])
        if not origin:continue
        target=source(nc[key][1])
        if origin!=target:raise ValueError('Entrada antiga mudou de endereço: '+key)
        # Campos de resultado também têm fontes; só impedir alteração de uma
        # fonte editável (valor inicial sem fórmula). Os resultados continuam
        # sendo atualizados pelas fórmulas canônicas nas tabelas de apoio.
        sh,co=origin
        initial=old.get(sh,{}).get(co)
        if not (isinstance(initial,str) and initial.startswith('=')):
            if co in changes.get(sh,{}):raise ValueError('Migração tenta sobrescrever entrada: '+key)
            preserved.append(dict(chave=key,aba=sh,celula=co))
    notes={sheet:{c:deepcopy(v) for c,v in cells.items() if v.get('note')}
           for sheet,cells in live.items()}
    return dict(formato_de=10,formato_para=11,destino=dest,backup_id=backup,
        snapshot_sha256=sha(snapshot),base_sha256=sha(base),alvo_sha256=sha(alvo),
        valores_alterados=changes,faixas=required,entradas_imoveis=preserved,
        notas_preservadas=notes,requer_releitura_identica=True,
        excluir_linhas=False,excluir_abas=False,
        pendente='Gerar lotes próprios; provar migração nativa em descartável antes da revisão')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('base','alvo','metadata','saida'):ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--snapshot',type=Path)
    ap.add_argument('--prova',type=Path)
    args=ap.parse_args()
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    base,alvo,meta=map(read,(args.base,args.alvo,args.metadata))
    result=planejar(base,alvo,read(args.snapshot),prova=read(args.prova) if args.prova else None) if args.snapshot else {
        'faixas_necessarias':faixas(base,alvo,meta),'base_sha256':sha(base),'alvo_sha256':sha(alvo)}
    args.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(args.saida)
