"""Prepara delta do protótipo na cópia nativa; jamais escreve pela rede.

Snapshot do primeiro bloco é requisito. Converte flags do protótipo anterior
em escolhas explícitas sem alterar pontos/versões. Não é migração de usuários.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'r53'),str(ROOT/'ficha-v01')]
from preparar_nativo import native_value,grid,IDS
import montagens_r53 as R

def preparar(modelo,snapshot):
 m=modelo; tabs={a['nome']:a for a in m['layout']['abas']};tr=m['r53'];g=tr['contextos'][0]
 cells={n:{v[0]:v for v in a['celulas']} for n,a in tabs.items()}
 originals={}
 for s in snapshot['structuredContent']['sheets']:
  if s['properties']['title']!='MONTAGENS':continue
  for d in s.get('data',[]):
   for ri,row in enumerate(d.get('rowData',[]),d.get('startRow',0)+1):
    for ci,cell in enumerate(row.get('values',[]),d.get('startColumn',0)+1):
     originals[(ri,ci)]=cell.get('userEnteredValue',{})
 req=[]
 def put(sheet,a1,value,note=None):
  c={'userEnteredValue':native_value(value)}
  if note is not None:c['note']=note
  req.append({'updateCells':{'range':grid(IDS[sheet],a1),'rows':[{'values':[c]}],'fields':'userEnteredValue'+(',note' if note is not None else '')}})
 for row,label in [(9,'Dano'),(11,'Cura'),(13,'PV temporários')]:
  put('MONTAGENS','A'+str(row),cells['MONTAGENS']['A'+str(row)][1])
  for ci in range(2,9):
   old=originals.get((row,ci),{})
   if 'boolValue' not in old:raise ValueError(f'Conversão já realizada ou valor não booleano: {row},{ci}')
   put('MONTAGENS',R.L(ci)+str(row),label if old['boolValue'] else '')
  rg=grid(IDS['MONTAGENS'],f'B{row}:H{row}')
  req.append({'setDataValidation':{'range':rg,'rule':{'condition':{'type':'ONE_OF_LIST','values':[{'userEnteredValue':v} for v in R.FUNCOES]},'strict':True,'showCustomUi':True}}})
 for row in [10,12,14]:put('MONTAGENS','A'+str(row),cells['MONTAGENS']['A'+str(row)][1])
 for row in [38,39]:
  for ci in range(1,9):
   a1=R.L(ci)+str(row);put('MONTAGENS',a1,cells['MONTAGENS'][a1][1])
  req.append({'copyPaste':{'source':grid(IDS['MONTAGENS'],'A14:H14'),'destination':grid(IDS['MONTAGENS'],f'A{row}:H{row}'),'pasteType':'PASTE_FORMAT'}})
 for key in ['dano','cura','vt','p_dano','p_cura','p_vt','avisos','identidade_ampliacao']:
  a1=tr['colunas'][key]+'2';put('DADOS_R53',a1,cells['DADOS_R53'][a1][1])
 put('DADOS_R53',tr['gid_editor'],IDS['MONTAGENS'])
 put('DADOS_R53','A203','r53.editor.gid')
 for a1 in [g['cel']['ampliar']]+g['cel'].get('preco',[])+g['cel'].get('dev',[])+[g['cel']['avisos']]:
  put(g['aba'],a1,tr['formulas'][g['id']][a1])
 for a1 in ['E70',g['cel']['ampliar']]:
  cell={'note':'Resumo automático. Edite funções e pontos pelo controle do cartão; as escolhas e a distribuição ficam salvas por Classe. MONTAGENS é o protótipo técnico, ainda não o editor final.'}
  req.append({'repeatCell':{'range':grid(IDS[g['aba']],a1),'cell':cell,'fields':'note'}})
 req.append({'updateSheetProperties':{'properties':{'sheetId':53018002,'hidden':True},'fields':'hidden'}})
 return req

if __name__=='__main__':
 m=json.loads(Path(sys.argv[1]).read_text());s=json.loads(Path(sys.argv[2]).read_text());r=preparar(m,s)
 Path(sys.argv[3]).write_text(json.dumps(r,ensure_ascii=False));print(len(r),'requisições no delta do primeiro cartão')
