"""Migração conservadora de registros; não escreve planilhas nem lê prosa livre.

O chamador fornece os campos originais e o contexto mecânico comprovado.
Sem prova estruturada da função/distribuição, conserva o original e pede revisão.
Ledger de personagem deve permanecer privado, fora do Git.
"""
import copy,hashlib,json,re
from modelo import calcular,FORMAS,CAT

ALIASES={'Certeiro':'Precisão','Muito Longe':'Longe · três degraus','Longe':'Longe · um degrau',
 'Muito Maior':'Maior · três degraus','Maior':'Maior · um degrau','Dívida':'Sobrecusto','Junto':'Mais Um'}
CONDICOES={v['rotulo'].split(' · ',1)[1]:v['rotulo'] for v in CAT['opcoes'] if v['nome']=='Condição'}
OPCOES={v['rotulo'] for v in CAT['opcoes']}
FUNCOES={'Dano':('dano','p_dano'),'Cura':('cura','p_cura'),'PV temporários':('vt','p_vt')}

def planejar(original,contexto,catalogo_extra=None,familias_custom=None):
 old=copy.deepcopy(original);problemas=[];mudancas=[]
 sha=hashlib.sha256(json.dumps(old,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 result=dict(original=old,sha256_original=sha,status='revisar',problemas=problemas,mudancas=mudancas,proposta=None)
 if not old.get('nome') and not old.get('parcial'):
  result['status']='vazio';return result
 if old.get('versoes_r53'):
  result.update(status='preservado',proposta=copy.deepcopy(old['versoes_r53']));return result
 a={**contexto,'nome':old.get('nome',''),'classe':old.get('classe',0),'forma':old.get('forma',''),
    'migracao':'Revisado','preparada':True}
 # Distribuição e função exigem campos mecânicos, não palavras na descrição.
 funcoes=old.get('funcoes_comprovadas')
 if not isinstance(funcoes,list) or not funcoes or any(f not in FUNCOES for f in funcoes):
  problemas.append('Função/distribuição antiga sem prova estruturada; não inferir pela descrição')
  funcoes=[]
 if a['forma'] in ['Cura','Apoio']:
  implied='Cura' if a['forma']=='Cura' else 'PV temporários'
  if funcoes!=[implied]:problemas.append('Forma antiga de recuperação exige conferir a função')
  mudancas.append(dict(campo='forma',antes=a['forma'],depois='Projétil'));a['forma']='Projétil'
 elif a['forma']=='Onda':
  if len(funcoes)!=1 or funcoes[0] not in ['Cura','PV temporários']:problemas.append('Onda: conferir cura ou vida temporária e distribuição')
  mudancas.append(dict(campo='forma',antes='Onda',depois='Aura'));a['forma']='Aura'
 elif a['forma']=='Efeito':
  target=old.get('forma_destino_comprovada')
  if target not in FORMAS:problemas.append('Efeito fora de combate: conferir Forma, extensão e duração')
  else:a['forma']=target
 selecionadas={}
 for kind,limit in [('melhorias',4),('restricoes',2)]:
  values=[]
  for v in old.get(kind,[]):
   if not v:continue
   if v=='Corpo a Corpo':
    if old.get('forma') in ['Toque','Aura']:
     mudancas.append(dict(campo=kind,antes=v,depois=None,motivo='retirada da antiga inclusão por proximidade'));continue
    problemas.append('Corpo a Corpo explícito: conferir Queima-Roupa e a origem desejada');values.append(v);continue
   if v in old.get('opcoes_comprovadas',{}):new=old['opcoes_comprovadas'][v]
   else:new=ALIASES.get(v,CONDICOES.get(v,v))
   if new not in OPCOES and new not in (catalogo_extra or {}):problemas.append('Opção fixa ou cadastro precisa de conferência: '+v)
   if new!=v:mudancas.append(dict(campo=kind,antes=v,depois=new))
   values.append(new)
  if len(values)>limit:problemas.append('Quantidade de '+kind+' acima das vagas')
  selecionadas[kind]=values
  for i in range(limit):a[('m' if kind=='melhorias' else 'r')+str(i+1)]=values[i] if i<len(values) else ''
 if 'Junto' in old.get('melhorias',[]) and 'Mais Um' in old.get('melhorias',[]):problemas.append('Junto com Mais Um: conferir destinatários para não duplicar a compra')
 for f,(flag,pontos) in FUNCOES.items():a[flag]=f in funcoes;a[pontos]=0
 distribuicao=old.get('distribuicao_comprovada')
 if len(funcoes)>1 and not isinstance(distribuicao,dict):problemas.append('Mescla antiga com quantidade única exige separar parcelas')
 if not problemas:
  # Custos não dependem da proporção; uma função única usa o saldo recalculado.
  preliminar=calcular(a,catalogo_extra,familias_custom)
  for f in funcoes:
   flag,points=FUNCOES[f]
   a[points]=distribuicao.get(f,0) if isinstance(distribuicao,dict) else max(0,int(preliminar['saldo']))
  out=calcular(a,catalogo_extra,familias_custom)
  if not out['valida']:problemas.append(out['avisos'])
  result['resultado']=dict((k,out[k]) for k in ['base_funcoes','custo_forma','melhorias_pagas','devolucao','saldo','dano_d8','cura_d8','vida_temporaria','pe'])
 a['migracao']='Revisão necessária' if problemas else 'Revisado'
 result.update(proposta=a,status='revisar' if problemas else 'automatico')
 return result
