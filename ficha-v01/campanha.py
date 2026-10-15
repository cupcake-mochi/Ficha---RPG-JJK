# -*- coding: utf-8 -*-
"""B47 parte 2: regras aprovadas, XP por nível e registro persistente de vida.

Morte permanente foi removida a pedido do usuário (15/10): não automatiza a
ficha. Os helpers guardam EM USO; CAMPANHA vazia preserva o livro. As fórmulas
antigas são registradas para que os validadores legados aceitem somente a
transformação exata, sem esconder uma fórmula adulterada.
"""
import json
import os
import re
from copy import deepcopy
from pathlib import Path
import indice_ficha as ix
import ficha_automatica
import livro

RAIZ = Path(__file__).resolve().parent.parent
CF = "'CONFIGURAÇÃO'!"
DC = 'DADOS_CONFIG'
FORMULAS = RAIZ/'ficha-v01/campanha-formulas.json'
ESPEC = [
 ('nivel_inicial','Nível inicial',2,'inteiro',1,30),
 ('atributos_pontos','Pontos de atributo iniciais',9,'inteiro',0,None),
 ('atributos_teto_criacao','Teto de atributo · criação',3,'inteiro',0,None),
 ('atributos_teto','Teto de atributo · progressão',6,'inteiro',0,None),
 ('pericias_com_oficio','Perícias · com ofícios',9,'inteiro',0,None),
 ('oficios_criacao','Ofícios · criação',2,'inteiro',0,None),
 ('pericias_sem_oficio','Perícias · sem ofícios',10,'inteiro',0,None),
 ('deslocamento_base','Deslocamento base',9,'numero',0,None),
 ('morrendo_aguentar','Morrendo · Aguentar',.25,'fracao',0,None),
 ('morrendo_insistir_1','Morrendo · Insistir · 1ª vez',1/3,'fracao',0,None),
 ('morrendo_insistir_2','Morrendo · Insistir · seguintes',.5,'fracao',0,None),
 ('morrendo_teto','Morrendo · teto de Insistir',15,'numero',0,None),
 ('morrendo_prazo','Morrendo · prazo',3,'inteiro',0,None),
 ('vida_rolada','Vida rolada','Não','sim_nao',None,None)]
POS={k:(46+i,2+i) for i,(k,*_) in enumerate(ESPEC)}

def ref(chave):return f'{DC}!$S${POS[chave][1]}'
def _r(aba,c):return f"'{aba}'!{ix._fixa(c) if hasattr(ix,'_fixa') else '$'+re.sub(r'(\d+)$',r'$\1',c)}"

def dados_livro():
 cat=json.loads((RAIZ/'catalogo-projeto-m.json').read_text())
 r=ficha_automatica.regras(cat)
 defaults={'nivel_inicial':cat['_meta']['nivel_inicial'],'atributos_pontos':r['pontos_criacao'],
           'atributos_teto_criacao':r['teto_criacao'],'atributos_teto':r['teto_atributo'],
           'pericias_com_oficio':r['pericias_com'],'oficios_criacao':r['oficios_com'],
           'pericias_sem_oficio':r['pericias_troca']}
 return cat,defaults

def trocas(layout, extras=None):
 idx=ix.indice(layout)
 cells={a['nome']:{r[0]:r for r in a['celulas']} for a in layout['abas']}
 tr={'antes':{},'celulas':{},'idx':idx,'extras':extras}
 def poe(aba,c,v):
  old=cells[aba][c][1]
  if old==v:return
  tr['antes'].setdefault(aba,{})[c]=old
  tr['celulas'].setdefault(aba,{})[c]=v
 def f(c):return cells['FICHA'][c][1]
 dc={v[1]:c for c,v in cells['DADOS'].items() if c.startswith('AJ') and isinstance(v[1],str) and not v[1].startswith('=')}
 def conta(nome):
  c=dc[nome];return 'AK'+re.search(r'\d+',c)[0]
 def muda_conta(nome,velho,novo):
  c=conta(nome);s=cells['DADOS'][c][1]
  if velho not in s:raise ValueError((nome,'trecho não encontrado',velho,s))
  poe('DADOS',c,s.replace(velho,novo))
 muda_conta('pontos de atributo','=9+',f'={ref("atributos_pontos")}+')
 c=idx['pontos disponíveis'];s=f(c)
 s=s.replace('>6,',f'>{ref("atributos_teto")},').replace('"Um atributo passou de 6"',f'"Um atributo passou de "&{ref("atributos_teto")}')
 s=s.replace('>3)',f'>{ref("atributos_teto_criacao")})').replace('"Na criação, nenhum acima de 3"',f'"Na criação, nenhum acima de "&{ref("atributos_teto_criacao")}')
 poe('FICHA',c,s)
 c=conta('rota do ofício');s=cells['DADOS'][c][1]
 for n,k in [(9,'pericias_com_oficio'),(2,'oficios_criacao'),(10,'pericias_sem_oficio')]:s=s.replace(f'-{n})',f'-{ref(k)})')
 poe('DADOS',c,s)
 muda_conta('perícias da rota',',9,10)',f',{ref("pericias_com_oficio")},{ref("pericias_sem_oficio")})')
 muda_conta('ofícios da rota',',2,0)',f',{ref("oficios_criacao")},0)')
 for nome in ['perícias que faltam sem ofício','Corpo por escolher sem ofício']:
  c=conta(nome);s=cells['DADOS'][c][1].replace('10-',ref('pericias_sem_oficio')+'-').replace('-10)',f'-{ref("pericias_sem_oficio")})');poe('DADOS',c,s)
 poe('FICHA',idx['nivel'],'='+ref('nivel_inicial'))
 c=idx['deslocamento'];s=f(c)
 if s.count('(9+')!=1:raise ValueError(('Deslocamento mudou',s))
 poe('FICHA',c,s.replace('(9+',f'({ref("deslocamento_base")}+'))
 vm=f'N({_r("FICHA",idx["vida_max"])})';cl=f'N({_r("FICHA",idx["classe máxima"])})'
 teto=f'{ref("morrendo_teto")}*{cl}'
 seq='+'.join(f'N({_r("FICHA",idx["sequela "+str(i)])})' for i in range(1,4))
 if extras:
  er=_r('FICHA',extras)
  seq+=f'+IF(ISBLANK({er}),0,IF(IFERROR(AND(ISNUMBER({er}),{er}>=0,INT({er})={er}),FALSE),{er},NA()))'
 prazo=ref('morrendo_prazo');rest=f'MAX(0,{prazo}-({seq}))'
 for campo,k in [('morrendo aguentar','morrendo_aguentar'),('morrendo insistir 1','morrendo_insistir_1'),('morrendo insistir 2','morrendo_insistir_2')]:
  tratamento=f'ROUNDUP(ROUND({vm}*{ref(k)},10),0)'
  if campo!='morrendo aguentar':tratamento=f'MIN({tratamento},{teto})'
  poe('FICHA',idx[campo],'='+tratamento)
  c=idx[campo];row,col=ix._lc(c);sub=f'{ix._letras(col)}{row+1}'
  texto=f'=TEXT({ref(k)},"# ?/?")&" da vida máxima, para cima"'
  if campo!='morrendo aguentar':texto+=f'&" · teto "&{ref("morrendo_teto")}&" × Classe"'
  old_text=cells['FICHA'][sub][1]
  rr=POS[k][0]
  unchanged=f'ISBLANK({CF}$E${rr})'
  if campo!='morrendo aguentar':unchanged=f'AND({unchanged},ISBLANK({CF}$E${POS["morrendo_teto"][0]}))'
  poe('FICHA',sub,f'=IF({unchanged},{old_text[1:]},{texto[1:]})')
 poe('FICHA',idx['morrendo prazo'],f'=IF({rest}=0,"Derrotado na hora",{rest}&IF({rest}=1," rodada"," rodadas"))')
 row,col=ix._lc(idx['morrendo prazo']);poe('FICHA',f'{ix._letras(col)}{row+1}',f'={prazo}&" rodadas, menos 1 por Sequela marcada"')
 # A legenda abaixo das Sequelas também usa a regra, não o antigo 3/2/1.
 import estado_do_personagem as ep
 for c,v in cells['FICHA'].items():
  if isinstance(v[1],str) and v[1].startswith('=') and 'Próxima queda:' in v[1]:
   poe('FICHA',c,f'="Próxima queda: "&IF({rest}=0,"Derrotado na hora",{rest}&IF({rest}=1," rodada de janela"," rodadas de janela"))')
 # A curva atual da DADOS passa a ler o XP acumulado do helper.
 cabe=next(c for c,v in cells['DADOS'].items() if v[1]=='xp acumulado')
 row,col=ix._lc(cabe)
 for n in range(2,31):poe('DADOS',f'{ix._letras(col)}{row+n-1}',f'={DC}!$Z${n+1}')
 c=idx['vida_max'];old=f(c);nivel=_r('FICHA',idx['nivel']);con=_r('FICHA',idx['atr_Constituição'])
 buff=_r('FICHA',idx['buff de vida'])
 nova=f'IF({DC}!$AF$32<>"",NA(),SUM({DC}!$AF$2:$AF$31)+IFERROR(VALUE({buff}&""),0))'
 poe('FICHA',c,f'=IF({ref("vida_rolada")}="Não",{old[1:]},{nova})')
 return tr

def aplica(layout,tr):
 for a in layout['abas']:
  for r in a['celulas']:
   if r[0] in tr['celulas'].get(a['nome'],{}):r[1]=tr['celulas'][a['nome']][r[0]]

def anterior(formula):
 if not isinstance(formula,str) or not formula.startswith('='):return formula
 if not FORMULAS.exists():return formula
 # A correspondência cobre a fórmula inteira: uma mutação não é normalizada.
 if not hasattr(anterior,'mapa'):anterior.mapa=json.loads(FORMULAS.read_text())
 old=anterior.mapa.get(formula,formula)
 return old if isinstance(old,str) else formula

def guarda(tr):
 mapa={v:tr['antes'][a][c] for a,cs in tr['celulas'].items() for c,v in cs.items() if isinstance(v,str) and v.startswith('=')}
 FORMULAS.write_text(json.dumps(mapa,ensure_ascii=False,indent=2)+'\n')

def desenha(layout,tr):
 a=ix._aba(layout,'CONFIGURAÇÃO');h=ix._aba(layout,DC)
 # Reutiliza somente os papéis de estilo já aprovados da configuração.
 styles={r[0]:r[2] for r in a['celulas']}
 st={'fundo':styles['A1'],'secao':styles['B9'],'rotulo':styles['B10'],'entrada':styles['C11'],'numero':styles['E11'],'calc':styles['I11'],'nota':styles['B5']}
 for key,pattern in [('fracao','# ?/?'),('metro','0.0" m"')]:
  e=deepcopy(layout['estilos'][st['numero']]);e[4]=pattern
  if e not in layout['estilos']:layout['estilos'].append(e)
  st[key]=layout['estilos'].index(e)
 # O painel RESULTADOS sai, liberando J:O para os cartões da próxima etapa.
 a['celulas']=[r for r in a['celulas'] if ix._lc(r[0])[1]<9 or ix._lc(r[0])[0]<=3]
 a['mescladas']=[m for m in a['mescladas'] if ix._lc(m.split(':')[0])[1]<9]
 a['mescladas']=[('B2:O3' if m=='B2:L3' else m) for m in a['mescladas']]
 a['condicional_gs']=[]
 a['linhas']=132;a['colunas']=16;h['linhas']=max(h['linhas'],34);h['colunas']=35
 a['colunas_larg']=[[c,c,(w+1)/8] for c,w in enumerate([24,60,186,95,70,115,155,24,24,95,95,95,95,95,95,24],1)]
 existing={r[0] for r in a['celulas']}
 for r in range(1,133):
  for c in range(1,17):
   co=f'{ix._letras(c)}{r}'
   if co not in existing:a['celulas'].append([co,None,st['fundo']])
 def put(c,v,style='entrada',merge=None,note=None):
  # Remover duplicados garante que apagar um exemplo realmente o apague.
  a['celulas'][:]=[r for r in a['celulas'] if r[0]!=c]
  a['celulas'].append([c,v,st[style]])
  if merge:a['mescladas'].append(c+':'+merge)
  if note:a['notas'][c]=note
 def helper(c,v):h['celulas'].append([c,v,None])
 def faixa(r,title):put(f'B{r}',title,'secao',f'G{r}')
 def cab(r,labels):
  for c,v in zip('BDEFG',labels):put(f'{c}{r}',v,'rotulo',f'C{r}' if c=='B' else None,note={'B':'Regra ou nível.','D':'Valor padrão do livro R51.','E':'Em branco usa o livro. Zero é um valor informado.','F':'Valor efetivamente usado pela ficha.','G':'Justificativa da mudança.'}[c])
 cat,defaults=dados_livro()
 faixa(43,'REGRAS DE CAMPANHA')
 put('B44','CAMPANHA em branco usa o livro. Preencha só o que mudar e registre o motivo.','nota','G44')
 cab(45,['REGRA','LIVRO','CAMPANHA','EM USO','MOTIVO'])
 for i,(k,label,default,kind,mn,mx) in enumerate(ESPEC):
  row,j=POS[k];default=defaults.get(k,default);inp=f'E{row}'
  valid=f'AND(ISNUMBER({inp}),{inp}>={mn}' if kind!='sim_nao' else f'OR({inp}="Sim",{inp}="Não"'
  if kind=='inteiro':valid+=f',INT({inp})={inp}'
  if mx is not None:valid+=f',{inp}<={mx}'
  valid+=')'
  valid=f'IFERROR({valid},FALSE)'
  valor=f'=IF({inp}="",D{row},IF({valid},{inp},NA()))'
  note={'nivel_inicial':'XP começa em zero neste nível. Para começar em 1, informe o custo 1→2 na tabela.',
        'vida_rolada':'Vida inicial fixa do Caminho. Cada nível seguinte guarda o resultado do dado, sem Constituição, no registro abaixo.',
        'morrendo_prazo':'Rodadas menos uma por Sequela. Inclui as Sequelas extras se preenchidas.'}.get(k,'Regra da campanha. Campo vazio usa o valor do R51.')
  put(f'B{row}',label,merge=f'C{row}',note=note)
  style='fracao' if kind=='fracao' else 'metro' if k=='deslocamento_base' else 'numero' if kind!='sim_nao' else 'calc'
  put(f'D{row}',default,style);put(inp,None,note=note);put(f'F{row}',valor,style);put(f'G{row}',None)
  helper(f'R{j}',k);helper(f'S{j}',f"={CF}$F${row}")
  helper(f'T{j}',f'=IF(ISERROR(S{j}),"Confira {label}","")')
  if kind=='sim_nao':a['menus'].append({'tipo':'list','formula':'"Sim,Não"','onde':inp,'vazio_ok':True,'mostra_seta':True})
  a['linhas_alt'].append([row,25.5])
 helper('R1','regra');helper('S1','em uso');helper('T1','problema')
 # Erros das regras são mostrados sem esconder a origem em campos calculados.
 helper('T17','=TEXTJOIN(" · ",TRUE,T2:T15,Z33)')
 put('B61',f'=IF({DC}!$T$17="","",{DC}!$T$17)','nota','G61')
 faixa(62,'XP · CUSTO POR NÍVEL');put('B63','Custo para sair do nível indicado. XP acumulado começa em zero no nível inicial da campanha.','nota','G63')
 cab(64,['NÍVEL','LIVRO','CAMPANHA','EM USO','XP ACUMULADO'])
 for n in range(1,31):
  row=64+n;j=n+1;cost=cat['progressao']['tabela_impressa'].get(str(n),{}).get('xp')
  default=int(str(cost).replace('.','')) if cost and cost!='—' else None
  put(f'B{row}',n,'numero',f'C{row}');put(f'D{row}',default,'numero')
  put(f'E{row}',None,note='Custo deste nível para o próximo; inteiro não negativo. O custo 1→2 precisa ser definido pela campanha, se usado.')
  put(f'F{row}',f'=IF(E{row}="",IF(D{row}="","",D{row}),IF(IFERROR(AND(ISNUMBER(E{row}),E{row}>=0,INT(E{row})=E{row}),FALSE),E{row},NA()))' if n<30 else '—','numero')
  put(f'G{row}',f'={DC}!Z{j}','numero',note='XP necessário para chegar a este nível desde o nível inicial da campanha.')
  helper(f'V{j}',n);helper(f'W{j}',f"={CF}$F${row}")
  cum=(f'IF({n}<{ref("nivel_inicial")},"—",IF({n}={ref("nivel_inicial")},0,'
       f'IF(OR(Z{j-1}="Pendente",W{j-1}=""),"Pendente",Z{j-1}+W{j-1})))') if n>1 else f'IF({ref("nivel_inicial")}=1,0,"—")'
  helper(f'Z{j}','='+cum)
 helper('V1','nível');helper('W1','custo');helper('Z1','XP acumulado')
 helper('Z33','=IF(COUNTIF(Z2:Z31,"Pendente")>0,"Informe o custo de XP do nível 1 para 2",IF(ISERROR(SUM(W2:W30)),"Confira os custos de XP",""))')
 # Registro dos dados: dado por Caminho vem da tabela do R51.
 nomes=json.loads((RAIZ/'decisoes-ficha.json').read_text())['C1_evocador']['caminhos_no_menu']
 for j,nome in enumerate(nomes,2):
  m=re.search(r'Dado de vida, na variante \| d(\d+)', '\n'.join(livro.secao(nome)))
  if not m:raise ValueError(('Dado de vida não encontrado',nome))
  helper(f'AH{j}',nome);helper(f'AI{j}',int(m[1]))
 idx=tr['idx'];cam=_r('FICHA',idx['caminho']);nv=_r('FICHA',idx['nivel']);con=_r('FICHA',idx['atr_Constituição'])
 helper('AI10',f'=IFERROR(VLOOKUP({cam},$AH$2:$AI${len(nomes)+1},2,FALSE),"")')
 # Vida inicial fixa e CON atual em cada nível, como a conta anterior.
 base=f'IFERROR(VLOOKUP({cam},DADOS!$N$5:$U$10,3,FALSE),"")'
 faixa(97,'VIDA ROLADA · REGISTRO')
 put('B98','Primeiro nível usa a vida inicial fixa. Registre o resultado do dado nos níveis seguintes; Constituição entra normalmente.','nota','G98')
 cab(99,['NÍVEL','DADO','ROLAGEM','GANHO','MOTIVO'])
 for n in range(1,31):
  row=99+n;j=n+1
  put(f'B{row}',n,'numero',f'C{row}')
  put(f'D{row}','Inicial fixa' if n==1 else f'=IF({DC}!$AI$10="","","d"&{DC}!$AI$10)','calc')
  put(f'E{row}','—' if n==1 else None,'numero',note='Resultado guardado, sem Constituição. Não há sorteio automático.')
  helper(f'AC{j}',n);helper(f'AE{j}',f"={CF}$E${row}" if n>1 else '')
  gain=f'{base}+{con}' if n==1 else f'IF(IFERROR(AND(ISNUMBER(AE{j}),AE{j}>=1,AE{j}<=$AI$10,INT(AE{j})=AE{j}),FALSE),AE{j}+{con},NA())'
  helper(f'AF{j}',f'=IF(OR({ref("vida_rolada")}="Não",{n}>{nv}),0,{gain})')
  put(f'F{row}',f'=IF({ref("vida_rolada")}="Não","",IF({n}>{nv},"",{DC}!AF{j}))','numero')
 helper('AF32','=IF(COUNTIF(AF2:AF31,"#N/A")>0,"Confira as rolagens da vida",IF(ISERROR(SUM(AF2:AF31)),"Confira as rolagens da vida",""))')
 put('B130',f'={DC}!$AF$32','nota','G130')
 a['grupos']['linhas'] += [[65,94,False],[100,129,False]]
 a['linhas_alt'] += [[43,22.5],[44,30],[45,24],[62,22.5],[63,30],[64,24],[97,22.5],[98,30],[99,24]]
 for r in range(65,130):
  if r not in [97,98,99]:a['linhas_alt'].append([r,21])
 # A nota antiga apontava para o painel de resultados, agora removido.
 a['notas']['C10']='Escolha a caixa afetada. A ficha aplica o resultado no lugar original.'
 # Mesmo com os resultados removidos, os avisos dos efeitos continuam visíveis.
 put('J5','Mizuki Escuro · paleta fixa','nota','O5')
 put('J7',f'=TEXTJOIN(" · ",TRUE,{DC}!$P$2,{DC}!$T$17,{DC}!$AF$32)','calc','O8')
 a['condicional_gs']=[{'faixas':['J7','B61','B130'],'contem':'Confira','fundo':'#C2334D','fonte':'#FFFFFF'}]


def exporta(tr):
 out=[]
 def add(k,origem):out.append([k,f'=IF(ISBLANK({origem}),"",{origem}&"")',origem.replace('$',''),'configuração'])
 for k,(r,j) in POS.items():
  add('regra.'+k,f'{DC}!$S${j}');add('regra.'+k+'.campanha',f'{CF}$E${r}')
 for n in range(1,30):
  add(f'regra.xp.{n}',f'{CF}$F${64+n}');add(f'regra.xp.{n}.campanha',f'{CF}$E${64+n}')
 for n in range(2,31):add(f'vida.rolagem.{n}',f'{CF}$E${99+n}')
 add('aviso.regras_campanha',f'{DC}!$T$17');add('aviso.vida_rolada',f'{DC}!$AF$32')
 if tr['extras']:add('sequela.extras',_r('FICHA',tr['extras']))
 return out


def extras(layout):
 """Uma caixa na linha vazia entre Sequelas e Origem, sem deslocar a ficha."""
 idx=ix.indice(layout);a=ix._aba(layout,'FICHA');cells={r[0]:r for r in a['celulas']}
 row=ix._lc(idx['sequela 1'])[0]+2
 label,valor=f'D{row}',f'J{row}'
 estilos={label:cells[f'D{row-3}'][2],valor:cells[idx['exaustão']][2]}
 for c,v in [(label,'SEQUELAS EXTRAS'),(valor,0)]:
  a['celulas']=[r for r in a['celulas'] if r[0]!=c]
  a['celulas'].append([c,v,estilos[c]])
 a['mescladas'] += [f'D{row}:I{row}',f'J{row}:M{row}']
 a.setdefault('notas',{})[valor]='Sequelas além das três caixas. Somam no prazo de Morrendo e são removidas pelo descanso longo, junto das caixas.'
 d=ix._aba(layout,'DADOS');r=max(ix._lc(c[0])[0] for c in d['celulas'] if c[0].startswith('BA') and c[1])+1
 # Índice por endereço, igual aos demais campos da ficha.
 d['celulas'] += [[f'BA{r}','sequela extras',None],[f'BB{r}',ix.FORMULA.format(c=valor),None]]
 d['linhas']=max(d['linhas'],r)
 return valor
