#!/usr/bin/env python3
"""Contraprovas portáteis do filtro de formatos, sem rede/dados de jogadores."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from migracao import sha

spec=importlib.util.spec_from_file_location('coalescer',Path(__file__).with_name('coalescer-formatos.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.src=self.root/'src';self.src.mkdir();self.dst=self.root/'dst'
        self.rg={'sheetId':1,'startRowIndex':732,'endRowIndex':736,'startColumnIndex':1,'endColumnIndex':7}
        self.style={'backgroundColor':{'red':0.5},'wrapStrategy':'WRAP'}
        self.anchor={'updateCells':{'start':{'sheetId':1,'rowIndex':732,'columnIndex':1},'rows':[{'values':[{'userEnteredValue':{'stringValue':'literal * ? ~'},'note':'nota','userEnteredFormat':self.style}]}],'fields':'userEnteredValue,note,userEnteredFormat'}}
        self.repeat={'repeatCell':{'range':self.rg,'cell':{'userEnteredFormat':self.style},'fields':'userEnteredFormat'}}
    def tearDown(self):self.tmp.cleanup()
    def write(self,tail):
        head=[{'unmergeCells':{'range':self.rg}},{'mergeCells':{'range':self.rg,'mergeType':'MERGE_ALL'}},self.anchor]
        batches=[head,tail];entries=[]
        for i,requests in enumerate(batches):
            payload={'spreadsheet_id':'descartavel-sintetica','requests':requests};name=f'{i:04d}.json'
            (self.src/name).write_text(json.dumps(payload),encoding='utf8')
            entries.append({'arquivo':name,'sha256':sha(payload),'pedidos':len(requests)})
        (self.src/'manifesto.json').write_text(json.dumps({'destino':'descartavel-sintetica','lotes':entries,'pedidos':sum(map(len,batches))}),encoding='utf8')
    def result(self):
        result=mod.otimizar(self.src,self.dst,1)
        return result,json.loads((self.dst/'0001.json').read_text(encoding='utf8'))['requests']
    def test_remove_across_batch_boundary_keep_literal_and_note(self):
        other={'updateCells':{'start':{'sheetId':1,'rowIndex':740,'columnIndex':1},'rows':[{'values':[{'userEnteredValue':{'stringValue':'outro literal * ? ~'},'note':'outra nota'}]}],'fields':'userEnteredValue,note'}}
        self.write([self.repeat,other]);r,requests=self.result()
        self.assertEqual(r['formatos_omitidos'],1);self.assertEqual(requests,[other])
    def test_keep_different_format(self):
        r=json.loads(json.dumps(self.repeat));r['repeatCell']['cell']['userEnteredFormat']['wrapStrategy']='CLIP'
        self.write([r]);self.assertEqual(self.result()[1],[r])
    def test_keep_extra_field(self):
        r=json.loads(json.dumps(self.repeat));r['repeatCell']['cell']['note']='preservar';r['repeatCell']['fields']+=',note'
        self.write([r]);self.assertEqual(self.result()[1],[r])
    def test_keep_unmerged_range(self):
        r=json.loads(json.dumps(self.repeat));r['repeatCell']['range']['endRowIndex']+=1
        self.write([r]);self.assertEqual(self.result()[1],[r])
    def test_keep_without_immediate_anchor(self):
        other={'updateDimensionProperties':{'range':{'sheetId':1,'dimension':'ROWS','startIndex':732,'endIndex':736},'properties':{'pixelSize':25},'fields':'pixelSize'}}
        self.write([other,self.repeat]);self.assertEqual(self.result()[1],[other,self.repeat])
    def test_bad_hash_no_output(self):
        self.write([self.repeat]);f=self.src/'0001.json';f.write_text(f.read_text().replace('WRAP','CLIP'))
        with self.assertRaises(ValueError):self.result()
        self.assertFalse(self.dst.exists())
    def test_reject_restart_from_zero(self):
        self.write([self.repeat])
        with self.assertRaises(ValueError):mod.otimizar(self.src,self.dst,0)
        self.assertFalse(self.dst.exists())


if __name__=='__main__':unittest.main()
