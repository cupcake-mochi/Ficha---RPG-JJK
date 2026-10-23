"""Perfila a releitura completa atual; mantém fórmulas em diretório privado."""
import json, re, hashlib
from collections import Counter
from pathlib import Path
from openpyxl.utils.cell import get_column_letter as L

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT/'nuvem-b47/saidas/diagnostico-mobile-20261023'
old = json.loads((PRIVATE/'formulas-nativas-normalizadas.json').read_text())
current, errors, covered = {}, [], Counter()
for path in sorted((PRIVATE/'leitura-atual').glob('*.json')):
    doc = json.loads(path.read_text())
    assert doc['spreadsheetId'] == '1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro'
    for sheet in doc['sheets']:
        name = sheet['properties']['title']
        current.setdefault(name,{})
        for block in sheet.get('data',[]):
            for r,row in enumerate(block.get('rowData',[]),block.get('startRow',0)+1):
                for c,cell in enumerate(row.get('values',[]),block.get('startColumn',0)+1):
                    a=L(c)+str(r)
                    f=cell.get('userEnteredValue',{}).get('formulaValue')
                    if f:
                        assert a not in current[name], (name,a)
                        current[name][a]=f
                    if 'errorValue' in cell.get('effectiveValue',{}): errors.append([name,a,cell['effectiveValue']['errorValue']])
meta = json.loads((PRIVATE/'metadata-atual.json').read_text())
sizes={}
changes=[]
for name,cells in current.items():
    columns=Counter()
    for a,f in cells.items(): columns[re.sub(r'\d','',a)]+=len(f.encode())
    sizes[name]=dict(formulas=len(cells),bytes_utf8=sum(len(f.encode()) for f in cells.values()),
                     maiores_colunas=columns.most_common(6),maior_formula=max(map(len,cells.values()),default=0))
    for a in set(cells)|set(old.get(name,{})):
        if cells.get(a)!=old.get(name,{}).get(a):changes.append(dict(aba=name,celula=a))
values=list(f for cells in current.values() for f in cells.values())
result=dict(data='2026-10-23',fonte='81 leituras delimitadas, todas as 27 abas',
    abas=len(current),grade_total=sum(s['properties']['gridProperties']['rowCount']*s['properties']['gridProperties']['columnCount'] for s in meta['sheets']),
    formulas=len(values),bytes_formulas_utf8=sum(len(f.encode()) for f in values),erros=errors,
    tamanho_drive_bytes=1919122,alteracoes_formulas_desde_pacote=changes,
    constantes_textuais=sum(bool(re.fullmatch(r'="(?:[^"]|"")*"',f)) for f in values),
    abas_detalhes=sizes,
    relato_android={'A':'abriu, mas demorou bons segundos','B':'abriu relativamente rápido, sem maiores problemas',
       'limite':'relato único, sem cronometragem/repetição; A também abriu; não isola cópia/cache/estado do documento'},
    limites=['Tamanho Drive não é RAM nem soma de fórmulas','Máscara não inclui conteúdo manual, imagens ou código remoto'])
(PRIVATE/'formulas-atual.json').write_text(json.dumps(current,ensure_ascii=False))
Path(__file__).with_name('AUDITORIA-ATUAL-2026-10-23.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='abas_detalhes'},ensure_ascii=False))
