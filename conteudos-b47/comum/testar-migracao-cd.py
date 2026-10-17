"""Guardas 10→11 sobre modelos reais; snapshots são sintéticos e não provam Google."""
import argparse
from copy import deepcopy
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import unittest

import migracao_cd as m
from migracao import uv


class MigracaoCD(unittest.TestCase):
    def snapshot(self):
        meta=deepcopy(META)
        meta['spreadsheetId']='descartavel-cd-sintetica'
        old=m.raw(BASE)
        return dict(spreadsheetId=meta['spreadsheetId'],backup_id='backup-nativo-sintetico-distinto',
            captured_at=NOW.isoformat(),backup_created_at=(NOW-timedelta(seconds=30)).isoformat(),
            metadata=meta,ranges=m.faixas(BASE,TARGET,meta),
            cells={s:{c:{'userEnteredValue':uv(v)} for c,v in cs.items()}
                   for s,cs in old.items() if s not in m.RETIRADAS})

    def planejar(self,snapshot,**kw):
        return m.planejar(BASE,TARGET,snapshot,now=NOW,**kw)

    def test_plano_preserva_nota_manual_e_entrada_existente(self):
        s=self.snapshot()
        s['cells']['CONFIGURAÇÃO']['B1013']['note']='Nota manual 007 — conservar'
        p=self.planejar(s)
        self.assertEqual(p['formato_de'],10)
        self.assertEqual(p['formato_para'],11)
        self.assertFalse(p['excluir_linhas'])
        self.assertFalse(p['excluir_abas'])
        self.assertEqual(p['notas_preservadas']['CONFIGURAÇÃO']['B1013']['note'],'Nota manual 007 — conservar')
        self.assertGreater(len(p['entradas_imoveis']),500)
        self.assertEqual(set(p['valores_alterados'])-set(m.raw(BASE)),m.NOVAS)

    def test_destino_oficial_recusado(self):
        s=self.snapshot();s['spreadsheetId']=m.OFICIAL
        with self.assertRaisesRegex(ValueError,'oficial'):self.planejar(s)

    def test_backup_mesmo_documento_recusado(self):
        s=self.snapshot();s['backup_id']=s['spreadsheetId']
        with self.assertRaisesRegex(ValueError,'backup'):self.planejar(s)

    def test_snapshot_expirado_recusado(self):
        s=self.snapshot();s['captured_at']=(NOW-timedelta(seconds=901)).isoformat()
        with self.assertRaisesRegex(ValueError,'15 minutos'):self.planejar(s)

    def test_backup_expirado_recusado(self):
        s=self.snapshot();s['backup_created_at']=(NOW-timedelta(seconds=901)).isoformat()
        with self.assertRaisesRegex(ValueError,'15 minutos'):self.planejar(s)

    def test_metadados_de_outro_documento_recusados(self):
        s=self.snapshot();s['metadata']['spreadsheetId']='outro'
        with self.assertRaisesRegex(ValueError,'Metadados'):self.planejar(s)

    def test_cobertura_incompleta_recusada(self):
        s=self.snapshot();s['ranges']['DADOS_AM']=[]
        with self.assertRaisesRegex(ValueError,'Snapshot incompleto'):self.planejar(s)

    def test_formula_alterada_pelo_jogador_nao_e_sobrescrita(self):
        s=self.snapshot();a1=next(iter(m.delta(BASE,TARGET)['DADOS_AM']))
        s['cells']['DADOS_AM'][a1]={'userEnteredValue':{'formulaValue':'=123'}}
        with self.assertRaisesRegex(ValueError,'Conteúdo divergente'):self.planejar(s)

    def test_padding_preenchido_nao_e_soterrado(self):
        s=self.snapshot();s['cells']['CONFIGURAÇÃO']['P1733']={'userEnteredValue':{'stringValue':'anotação do jogador'}}
        with self.assertRaisesRegex(ValueError,'Área nova ocupada'):self.planejar(s)

    def test_modalidade_nova_ocupada_recusada(self):
        s=self.snapshot();s['cells']['CONFIGURAÇÃO']['B1013']['userEnteredValue']={'stringValue':'já uso este espaço'}
        with self.assertRaisesRegex(ValueError,'modalidade ocupado'):self.planejar(s)

    def test_reaplicacao_apos_auxiliar_existente_recusada(self):
        s=self.snapshot();s['metadata']['sheets'].append({'properties':{'title':'DADOS_FORMAS','sheetId':123}})
        with self.assertRaisesRegex(ValueError,'reaplicação'):self.planejar(s)

    def test_revisao_sem_prova_nativa_da_migracao_recusada(self):
        s=self.snapshot();s['spreadsheetId']=s['metadata']['spreadsheetId']=m.REVISAO
        with self.assertRaisesRegex(ValueError,'prova nativa da migração'):self.planejar(s)

    def test_fontes_anteriores_nao_podem_mudar(self):
        target=deepcopy(TARGET)
        an=next(a for a in target['layout']['abas'] if a['nome']=='ANALISE')
        next(c for c in an['celulas'] if c[0]=='C3')[1]='CONFIGURAÇÃO!A999'
        with self.assertRaisesRegex(ValueError,'Contrato antigo alterado'):
            m.contrato(BASE,target)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('base','alvo','metadata'):ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args()
    BASE,TARGET,META=[json.loads(p.read_text(encoding='utf8')) for p in (args.base,args.alvo,args.metadata)]
    NOW=datetime.now(timezone.utc)
    unittest.main(argv=['testar-migracao-cd.py'],verbosity=2)
