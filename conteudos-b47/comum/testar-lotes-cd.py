"""Simula os pedidos C sobre valores/validações reais do gerador, sem rede."""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import unittest
from openpyxl.utils.cell import get_column_letter as L,range_boundaries
import lotes_cd as l
import migracao_cd as m
from migracao import uv,canonical

R=m.ROOT
read=lambda p:json.loads((R/p).read_text(encoding='utf8'))
BASE=read('nuvem-b47/saidas/pecas-modelo.json')
TARGET=read('nuvem-b47/saidas/cd/combinado-modelo.json')
BS=read('nuvem-b47/saidas/cd/referencia-base-v10.json')
TS=read('nuvem-b47/saidas/cd/referencia-combinada.json')
META=read('nuvem-b47/saidas/cd/revisao-metadata-preparacao.json')
META['spreadsheetId']='ensaio-offline-cd'
NOW=datetime.now(timezone.utc)
SNAP=dict(spreadsheetId=META['spreadsheetId'],backup_id='backup-offline-distinto',metadata=META,
    captured_at=NOW.isoformat(),backup_created_at=(NOW-timedelta(seconds=1)).isoformat(),
    cells={s:{c:{'userEnteredValue':uv(v)} for c,v in cs.items()} for s,cs in m.raw(BASE).items() if s not in m.RETIRADAS},
    ranges={s['properties']['title']:[f'A1:{L(s["properties"]["gridProperties"]["columnCount"])}{s["properties"]["gridProperties"]["rowCount"]}'] for s in META['sheets']})
for s,cs in l.validacoes(BS).items():
    for c,r in cs.items():SNAP['cells'].setdefault(s,{}).setdefault(c,{})['dataValidation']=r
SNAP['cells']['CONFIGURAÇÃO']['B1013']['note']='007 nota manual preservada'
PLAN=m.planejar(BASE,TARGET,SNAP,now=NOW)
REQ,PROPS=l.gerar(BASE,TARGET,SNAP,PLAN,BS,TS)


class LotesCD(unittest.TestCase):
    def test_delta_valores_integral_e_nenhuma_entrada_antiga(self):
        writes={}
        byid={p['sheetId']:s for s,p in PROPS.items()}
        for req in REQ:
            u=req.get('updateCells')
            if not u:continue
            s=byid[u['start']['sheetId']]
            for y,row in enumerate(u['rows']):
                for x,cell in enumerate(row['values']):
                    co=L(u['start']['columnIndex']+x+1)+str(u['start']['rowIndex']+y+1)
                    writes.setdefault(s,{})[co]=next(iter(cell.get('userEnteredValue',{}).values()),None)
        for s,cs in PLAN['valores_alterados'].items():
            for co,v in cs.items():self.assertEqual(canonical(writes.get(s,{}).get(co)),canonical(v),(s,co))
        for p in PLAN['entradas_imoveis']:
            self.assertNotIn(p['celula'],writes.get(p['aba'],{}))

    def test_nao_exclui_nem_altera_notas_antigas(self):
        self.assertFalse(any(k.startswith('delete') or k=='unmergeCells' for r in REQ for k in r))
        ids={p['sheetId']:s for s,p in PROPS.items()}
        for r in REQ:
            u=r.get('updateCells')
            if not u or 'note' not in u['fields']:continue
            self.assertEqual(ids[u['start']['sheetId']],'CONFIGURAÇÃO')
            self.assertGreaterEqual(u['start']['rowIndex'],1732)

    def test_auxiliares_e_ids_sem_colisao(self):
        adds=[r['addSheet']['properties'] for r in REQ if 'addSheet'in r]
        self.assertEqual({p['title'] for p in adds},m.NOVAS)
        self.assertTrue(all(p['hidden'] for p in adds))
        self.assertEqual(len({p['sheetId'] for p in PROPS.values()}),len(PROPS))

    def test_pedidos_partidos_cabem_e_preservam_matriz(self):
        batches=l.fracionar(REQ)
        self.assertTrue(all(len(b)<=40 and len(json.dumps(b,ensure_ascii=False,separators=(',',':')).encode())<=60000 for b in batches))
        count=lambda rs:sum(sum(len(x['values']) for x in r['updateCells']['rows']) for r in rs if 'updateCells'in r)
        self.assertEqual(count(REQ),count([r for b in batches for r in b]))

    def test_validacao_manual_divergente_bloqueia(self):
        s=deepcopy(SNAP);s['cells']['FICHA AMALDIÇOADA']['D58']['dataValidation']={'condition':{'type':'BOOLEAN'}}
        p={**PLAN,'snapshot_sha256':m.sha(s)}
        with self.assertRaisesRegex(ValueError,'Validação nativa divergente'):l.gerar(BASE,TARGET,s,p,BS,TS)

    def test_grade_com_area_existente_exige_auditoria(self):
        s=deepcopy(SNAP)
        next(x for x in s['metadata']['sheets'] if x['properties']['title']=='CONFIGURAÇÃO')['properties']['gridProperties']['rowCount']=1733
        p={**PLAN,'snapshot_sha256':m.sha(s)}
        with self.assertRaisesRegex(ValueError,'auditoria'):l.gerar(BASE,TARGET,s,p,BS,TS)


if __name__=='__main__':unittest.main()
