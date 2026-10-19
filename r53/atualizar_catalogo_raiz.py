"""Atualiza o catálogo comum com entradas publicadas, mantendo outros domínios.

O núcleo usa opções normalizadas de r53/catalogo.json. As entradas comuns
continuam agrupadas por peça (61/19); opções não viram capacidades extras.
"""
from pathlib import Path
import json,re,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def atualizar():
 p=ROOT/'catalogo-projeto-m.json';d=json.loads(p.read_text());r=json.loads((ROOT/'r53/catalogo.json').read_text())
 t=json.loads((ROOT/'ficha-v01/tecnica-do-livro.json').read_text())
 spec=importlib.util.spec_from_file_location('extrair_manual',ROOT/'extrair-manual.py');em=importlib.util.module_from_spec(spec);spec.loader.exec_module(em)
 def corpo(texto):
  raw='\n'.join(texto.splitlines()[1:])
  raw=re.sub(r'\*\*(?:Família|Preço|Devolução):.*?\.\*\*\s*','',raw)
  return re.sub(r'(?m)^#+\s*','',em.texto(raw)).strip()
 for tipo in ['melhorias','restricoes']:
  out={}
  for item in r[tipo]:
   choices=[v for v in r['opcoes'] if v['tipo']==tipo and v['id']==item['id']]
   levels=list(dict.fromkeys({1:'Leve',2:'Media',3:'Pesada'}[v['peso']] for v in choices))
   v={'fonte_id':item['id'],'opcoes':[v['rotulo'] for v in choices]}
   if tipo=='melhorias':v.update(familia=None if item['nome']=='Efeito Próprio' else item['familia'],peso=' ou '.join(levels),efeito=corpo(item['texto']))
   else:v.update(devolve=' ou '.join(levels),o_que_muda=corpo(item['texto']))
   out[item['nome']]=v
  d[tipo]=out
 d['formas']={v['nome']:dict(custa=None if v['custa']=='—' else v['custa'].replace('Média','Media'),
      familia='Área' if v['nome'] in ['Explosão','Aura','Cone','Linha'] else None,
      alcance=v['o_que_e'],resolve=v['resolve'],devolucao_toque=v.get('devolve')) for v in t['formas']}
 # Descrições e conversões ativas acompanham as funções da R53.
 import sys
 sys.path.insert(0,str(ROOT));import livro as Lv
 d['familias']={f[0]:f[1].rstrip('.') for f in Lv.tabela(Lv.secao('10. Fundamento'),'Família')[1]}
 d['fundamento']['ponto_nao_gasto']='Distribuído na criação entre as funções escolhidas; sobra pode ficar sem uso'
 d['fundamento']['ponto_por_funcao']={'dano':'1d8','cura':'1d8','vida_temporaria':3}
 d['fundamento']['restricao_paga']='Toque e Restrições pagam Melhorias, sem pagar base ou Forma, limitados ao gasto e a 2 × Classe'
 d['_meta'].update(versao='R53',versao_data='19/10/2026',versao_dona=t['_meta']['versao_do_livro'],
      fonte='referencias-r53/LIVRO-COMPLETO.md e BLOCOS-R53.json; manual-fonte.json e r53/catalogo.json registram hashes')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n')
if __name__=='__main__':atualizar();print('Catálogo comum: 61 Melhorias, 19 Restrições, seis Formas R53.')
