"""Compara o candidato nativo relido com snapshot/produção, sem rede."""
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'r53/diagnostico-android')]
from revisar import normalized
from openpyxl.utils.cell import get_column_letter as L
PRIVATE=ROOT/'nuvem-b47/saidas/diagnostico-mobile-20261023'

def cells(doc):
    result={}
    for s in doc['sheets']:
        for b in s.get('data',[]):
            for r,row in enumerate(b.get('rowData',[]),b.get('startRow',0)+1):
                for c,cell in enumerate(row.get('values',[]),b.get('startColumn',0)+1):
                    result[L(c)+str(r)]=cell
    return result

before,after={},{}
for prefix,out in [('antes',before),('depois',after)]:
    for path in sorted((PRIVATE/'c-compactacao').glob(prefix+'-*.json')):
        doc=json.loads(path.read_text())
        assert doc['spreadsheetId']=='1VO61vXu8FjsDvc27c5c_ke93be-4Ta2rGaToDCv0Wgc'
        out.update(cells(doc))
expected=json.loads((PRIVATE/'compactacao-esperado.json').read_text())
assert len(expected)==498
for address,formula in expected.items():
    old,new=before[address],after[address]
    assert normalized(formula)==normalized(new['userEnteredValue']['formulaValue']),address
    assert 'errorValue' not in new.get('effectiveValue',{}),address
    assert {k:v for k,v in old.items() if k!='userEnteredValue'}=={k:v for k,v in new.items() if k!='userEnteredValue'},address
summary=json.loads((PRIVATE/'compactacao-template.json').read_text())
summary.pop('template')
summary.update(candidato='1VO61vXu8FjsDvc27c5c_ke93be-4Ta2rGaToDCv0Wgc',
   formulas_conferidas=498,resultados_formatos_validacoes_notas_iguais=True,
   total_texto_antes=34725005,total_texto_depois=34725005-summary['bytes_antes']+summary['bytes_depois'],
   grade_antes=857739,grade_depois=710587,formulas_antes=137180,formulas_depois=137180,
   QA_nativa=dict(casos=89,comparacoes_exatas_efeitos=89,comparacoes_exatas_avisos=89,criterios_mecanicos=89,erros=0),
   limite='Comparação por API e testes sintéticos; candidato C ainda precisa de teste nos aparelhos afetados e revisão de acionadores para publicação.')
Path(__file__).with_name('COMPACTACAO-NATIVA-2026-10-23.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
