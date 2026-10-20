"""Leitura portátil do formato ANALISE12. Somente biblioteca padrão.

Preserva tipos e versões; não substitui a aprovação do bot nem executa texto
livre. Campos novos seguem separados de resultados e do resumo visível.
"""
import json,re

class ErroContrato(ValueError):
 def __init__(self,erros):self.erros=erros;super().__init__('; '.join(erros))

BOOL={'preparada','pessoal','dano','cura','vt','permite_dano','permite_cura','permite_vt','permite_alma','r1_valida','r2_valida'}
INTEIROS={'classe','nivel','classe_maxima','dados_zero','fragil_pago','p_dano','p_cura','p_vt','pontos1','pontos2','pontos3'}

def decodificar(ficha):
 erros=[];out={}
 def valor(k):return ficha.get(k,{}).get('valor','')
 if valor('r53.montagem.esquema') not in [2,'2']:
  raise ErroContrato(['R53: esquema de montagem ausente ou desconhecido'])
 def schema(k,obrigatorios):
  try:
   v=json.loads(valor(k))
   if not isinstance(v,list) or any(not isinstance(x,str) for x in v) or len(v)!=len(set(v)) or not obrigatorios<=set(v):raise ValueError()
   return v
  except (ValueError,TypeError):erros.append(k+': esquema de campos inválido');return []
 campos=schema('r53.versao.campos',{'classe','preparada','forma','funcao1','pontos1','funcao2','pontos2','funcao3','pontos3','m1','r1','tr_dano','tr_controle'})
 entradas=schema('r53.entrada.campos',{'id','nome','classe','modalidade','dano','cura','vt','p_dano','p_cura','p_vt','tr_dano','tr_controle'})
 def registro(key,campos):
  try:
   raw=json.loads(valor(key))
   if not campos or not isinstance(raw,list) or len(raw)!=len(campos):raise ValueError('quantidade de campos')
   row=dict(zip(campos,raw))
   for k,v in row.items():
    if k in BOOL and type(v) is not bool:raise ValueError(k+' precisa ser booleano')
    if k in INTEIROS and (type(v) is not int or (k!='cd' and v<0)):raise ValueError(k+' precisa ser inteiro válido')
    if k=='cd' and type(v) not in (int,float):raise ValueError('cd precisa ser número')
    if k not in BOOL|INTEIROS|{'cd'} and not isinstance(v,str):raise ValueError(k+' precisa ser texto')
   return row
  except (ValueError,TypeError) as err:erros.append(key+': registro inválido ('+str(err)+')');return None
 for key,meta in ficha.items():
  if meta.get('valor','')=='':continue
  m=re.fullmatch(r'r53\.(.+)\.versao\.(\d|maxima)',key)
  if m:
   r=registro(key,campos)
   if not r:continue
   if not r['preparada']:erros.append(key+': versão publicada sem estar preparada')
   if m[2]!='maxima' and r['classe']!=int(m[2]):erros.append(key+': Classe não corresponde à chave')
   if r['classe']>7:erros.append(key+': Classe fora de0a7')
   out.setdefault(m[1],dict(versoes={}))['versoes'][m[2]]=r
  elif re.fullmatch(r'r53\..+\.entrada',key):
   id_=key[4:-8];r=registro(key,entradas)
   if r:
    if r['id']!=id_:erros.append(key+': identidade não corresponde à chave')
    out.setdefault(id_,dict(versoes={}))['ativa']=r
 for id_,data in out.items():
  ativa=data.get('ativa')
  if ativa:
   key='maxima' if ativa['modalidade'] in ('Técnica Máxima','Máxima de entidade') else str(ativa['classe'])
   if key not in data['versoes']:erros.append(id_+': versão ativa sem registro preparado')
  elif data['versoes']:erros.append(id_+': versões preparadas sem identificação ativa')
 if erros:raise ErroContrato(erros)
 return out
