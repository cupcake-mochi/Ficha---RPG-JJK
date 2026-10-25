"""Prepara candidato de FD+FX e prova o encaixe em TODAS as fórmulas atuais.

Sem rede; fontes/snapshots privados nunca são substituídos. Não usa Workbook.
"""
import json, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'r53'),str(ROOT/'r53/diagnostico-android')]
import modelo as M
from formulas import native
from compactar import native_compact
from formas_custom import CAMPOS
from revisar import normalized
from openpyxl.utils.cell import get_column_letter as L

PRIVATE=ROOT/'nuvem-b47/saidas/diagnostico-mobile-20261023'
data=json.loads((PRIVATE/'formulas-atual.json').read_text())['DADOS_R53']
columns={k:L(i+1) for i,k in enumerate(M.INPUTS+list(M.ARVORE))}
tree=M.arvore(True)
def build(row, compact):
    refs={k:c+str(row) for k,c in columns.items()}
    refs.update(__familias_range__="'DADOS_R53_CATALOGO'!$W$2:$AJ$20",
        __familias_col__=f'IFERROR(VALUE(REGEXEXTRACT(A{row};"^entidade[.]([0-9]+)[.]"))+2;2)',
        __formas_range__="'DADOS_R53_CATALOGO'!$AL$2:$DZ$11", __formas_campos__=CAMPOS)
    out={}
    for field,col in [('efeitos','FD'),('avisos','FX')]:
        e=tree[field]
        if compact:
            text=native_compact(e,refs,"'DADOS_R53_CATALOGO'!$A$2:$O$179",M.LOOKUP_FIELDS,';',field=='efeitos')
        else:
            text=native(e,refs,"'DADOS_R53_CATALOGO'!$A$2:$O$179",M.LOOKUP_FIELDS,';')
        if field=='avisos':
            identity=f"'DADOS_R53'!$FZ${row}"
            text=f'TEXTJOIN(" · ";TRUE;{text};GA{row};IF({identity}<>"";"Ampliação altera funções ou peças: "&{identity};""))'
        out[col]=f'=IF(B{row}="";"";{text})'
    return out

templates=build('ZZROWZZ', True)
expected={}
for row in range(2,251):
    original=build(row,False)
    new=build(row,True)
    for col,f in original.items():
        address=f'{col}{row}'
        assert normalized(f)==normalized(data[address]), address
        assert new[col]==templates[col].replace('ZZROWZZ',str(row)), address
        assert len(new[col])<32767
        expected[address]=new[col]
result=dict(template=templates,rows=249,alvos=['FD','FX'],
    bytes_antes=sum(len(data[a].encode()) for a in expected),
    bytes_depois=sum(len(f.encode()) for f in expected.values()),
    originais_conferidas=len(expected),
    sha256=hashlib.sha256(json.dumps(expected,ensure_ascii=False,sort_keys=True).encode()).hexdigest())
(PRIVATE/'compactacao-esperado.json').write_text(json.dumps(expected,ensure_ascii=False))
(PRIVATE/'compactacao-template.json').write_text(json.dumps(result,ensure_ascii=False))
print(json.dumps(result,ensure_ascii=False))
