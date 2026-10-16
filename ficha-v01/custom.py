# -*- coding: utf-8 -*-
"""B47/3a: esquema e cartões custom aprovados, sem interpretar prosa como regra.

Os sete seletores fechados e os seis campos livres mantêm posições estáveis
quando o tipo muda. A ficha valida os dados guardados, além do menu nativo:
colar valores ou trocar o tipo nunca faz uma entrada inválida valer como zero.
"""
import json
import re
from copy import deepcopy
from pathlib import Path
import indice_ficha as ix
import livro

RAIZ = Path(__file__).resolve().parent.parent
NOME = 'DADOS_CUSTOM'
QUANTIDADE = 25
INICIO, PASSO = 9, 29
ROTAS = ('Fundamento', 'Manejos', 'Técnica Marcial com energia', 'Técnica Marcial sem energia')
SEM_BASE = 'Nenhuma'
RESTRICAO = 'Restrição Celestial · Restrição corporal'
SPEC = {
 'Origem': (['PERÍCIA 1', 'PERÍCIA 2', 'PERÍCIA 3', 'PERÍCIA 4', 'ROTA', 'BASE DO LIVRO', 'OFÍCIO'], ['TALENTO CE 4']),
 'Marcante': (['ORIGEM'], ['FREQUÊNCIA']),
 'Menor': (['ORIGEM', 'EXIGE MARCANTE'], ['FREQUÊNCIA']),
 'Arma': (['CATEGORIA', 'MÃO', 'TIPO DE DANO', 'PROPRIEDADE 1', 'PROPRIEDADE 2', 'PROPRIEDADE 3', 'PROPRIEDADE 4'],
          ['DADO', 'FORÇA', 'VOLUME', 'ALCANCE', 'RECARGA', 'PREÇO']),
 'Escudo': ([], ['PROTEÇÃO', 'TETO DE DESTREZA', 'FORÇA', 'VOLUME', 'PREÇO']),
 'Uniforme': (['GRAU MÍNIMO'], ['PROTEÇÃO', 'TETO DE DESTREZA', 'FORÇA', 'VOLUME', 'PREÇO']),
 'Item comum': ([], ['VOLUME', 'PREÇO']),
 'Ferramenta amaldiçoada': (['BASE', 'GRAU'], ['ESTIGMA', 'DESGASTE', 'VOLUME', 'PREÇO'])}
CAMPOS = {t: c + [''] * (7-len(c)) + f + [''] * (6-len(f)) for t, (c, f) in SPEC.items()}


def cartao(n):
 if not 1 <= n <= QUANTIDADE:
  raise ValueError('cartão fora da capacidade da parte 3a')
 r = INICIO + (n-1)*PASSO
 return {'n': n, 'inicio': r, 'tipo': f'J{r+2}', 'nome': f'J{r+4}', 'mestre_viu': f'N{r+2}',
         'campos': [f'L{r+5+i}' for i in range(13)], 'efeito': f'J{r+19}', 'aviso': f'J{r+24}'}


def texto(v):
 return '"'+str(v).replace('"','""')+'"'


def ref(c, aba=NOME):
 r, col = ix._lc(c)
 return f"'{aba}'!${ix._letras(col)}${r}"


def faixa(col, fim, inicio=2, largura=1):
 return f"'{NOME}'!${ix._letras(col)}${inicio}:${ix._letras(col+largura-1)}${fim}"


def escolha(tipo, opcoes, padrao='""'):
 return 'SWITCH('+tipo+','+','.join(texto(k)+','+v for k,v in opcoes.items())+','+padrao+')'


def itens_livro():
 cab, rows = livro.tabela(livro.secao('Itens comuns'), 'Item')
 assert cab == ['Item', 'Conteúdo', 'Preço (¥)', 'Volume']
 return [{'nome': n, 'texto': t, 'preco': int(p.replace('.','')), 'volume': float(v.replace(',','.'))}
         for n,t,p,v in rows]


def listas():
 cat = json.loads((RAIZ/'catalogo-projeto-m.json').read_text())
 ori = json.loads((RAIZ/'ficha-v01/origens-do-livro.json').read_text())
 eq = json.loads((RAIZ/'ficha-v01/equipamento-do-livro.json').read_text())
 return {
  'tipos': list(SPEC), 'pericias': list(cat['pericias']), 'rotas': list(ROTAS),
  'origens': [o['menu'] for o in ori['origens']],
  'bases': [SEM_BASE]+[o['menu'] for o in ori['origens']],
  'oficios': ['—']+list(cat['oficios']),
  'categorias': sorted({a['categoria'] for a in cat['equipamento']['armas'].values()}),
  'maos': [1,2],
  'danos': ['Cortante','Perfurante','Concussão','Fogo','Frio','Elétrico','Ácido','Trovejante','Veneno','Radiante','Necrótico','Psíquico','Energia Reversa','Força','Alma'],
  'propriedades': ['—']+[x['nome'] for x in eq['propriedades']+eq['restricoes']],
  'graus': ['—']+list(cat['patentes']['salario_por_mes']),
  'equipamentos': list(cat['equipamento']['armas'])+list(cat['equipamento_defesa']['escudos'])+list(cat['equipamento_defesa']['uniformes'])+[i['nome'] for i in itens_livro()],
  'marcantes': ['—']+[x['nome'] for o in ori['origens'] for x in o['marcantes']], 'vazio': []}


def lista_campo(label):
 if label.startswith('PERÍCIA'): return 'pericias'
 if label.startswith('PROPRIEDADE'): return 'propriedades'
 return {'ROTA':'rotas','BASE DO LIVRO':'bases','ORIGEM':'origens','OFÍCIO':'oficios','CATEGORIA':'categorias',
         'MÃO':'maos','TIPO DE DANO':'danos','GRAU MÍNIMO':'graus','GRAU':'graus','BASE':'equipamentos',
         'EXIGE MARCANTE':'marcantes'}.get(label,'vazio')


def aba_dados():
 return {'nome': NOME, 'estado': 'hidden', 'linhas': 160, 'colunas': 284,
         'padrao': ['Roboto',10,'#000000'], 'fundo_base':'#FFFFFF', 'paleta_fixa':True,
         'colunas_larg':[], 'linhas_alt':[], 'altura_padrao':15.75, 'grade':False,
         'celulas':[], 'mescladas':[], 'menus':[], 'condicional':[], 'imagens':[]}


def desenha(layout, tr=None):
 """Só o painel direito. Preserva alturas e mesclagens do painel de campanha."""
 a = ix._aba(layout,'CONFIGURAÇÃO')
 # Os 204 menus dos cartões e da campanha devem caber na montagem nativa.
 # A gravação individual estourou seis minutos no teste autorizado de 15/10.
 a['validacao_em_matriz'] = True
 aviso_global=next((x[1] for x in a['celulas'] if x[0]=='J7'),None)
 if not isinstance(aviso_global,str) or not aviso_global.startswith('='):
  raise ValueError('o aviso global da configuração não foi encontrado')
 if tr is None:
  tr = prepara(layout)
 h = tr['aba']
 # Retirar a reserva antiga do painel direito antes dos cartões.
 a['celulas']=[x for x in a['celulas'] if ix._lc(x[0])[1]<10 or ix._lc(x[0])[0]<=3]
 a['mescladas']=[m for m in a['mescladas'] if ix._lc(m.split(':')[0])[1]<10]
 a['notas']={c:v for c,v in a['notas'].items() if ix._lc(c)[1]<10}
 estilos = {r[0]:r[2] for r in a['celulas']}
 st = {'fundo':estilos['A1'],'secao':estilos['B9'],'rotulo':estilos['B10'],
       'entrada':estilos['C11'],'caixa':estilos['B11'],'nota':estilos['B5']}
 # Cada caixa mesclada recebe só o seu próprio contorno, nunca uma grade global.
 st['efeito']=st['entrada']
 efeito=deepcopy(layout['estilos'][st['entrada']]);efeito[3]=['left','top',True,0]
 if efeito not in layout['estilos']:layout['estilos'].append(efeito)
 st['efeito']=layout['estilos'].index(efeito)
 antigo=a['linhas'];a['linhas']=cartao(QUANTIDADE)['inicio']+25
 usados={c[0] for c in a['celulas']}
 for r in range(1,a['linhas']+1):
  for c in range(1,17):
   co=f'{ix._letras(c)}{r}'
   if co not in usados:a['celulas'].append([co,None,st['fundo']])
 a['linhas_alt'] += [[r,18.75] for r in range(antigo+1,a['linhas']+1)]
 a.setdefault('menus_estritos',[])
 def put(c,v=None,est='entrada',fim=None,nota=None):
  a['celulas'][:]=[x for x in a['celulas'] if x[0]!=c]
  a['celulas'].append([c,v,st[est]])
  if fim:a['mescladas'].append(c+':'+fim)
  if nota:a['notas'][c]=nota
 def helper(c,v):h['celulas'].append([c,v,None])
 pools=listas();pc={k:78+i for i,k in enumerate(pools)}
 pr={k:faixa(c,160) for k,c in pc.items()}
 pr['origens_marcante']=faixa(75,160)
 helper('BW1','origens que podem criar marcante')
 helper('BW2',RESTRICAO)
 for row in range(2,QUANTIDADE+2):
  helper(f'BW{row+1}',f'=IF(AND($B{row}="Origem",OR($J{row}="",$J{row}="{SEM_BASE}",$J{row}="{RESTRICAO}")),$C{row},"")')
 for k,values in pools.items():
  c=pc[k];helper(f'{ix._letras(c)}1',k)
  for r,v in enumerate(values,2):helper(f'{ix._letras(c)}{r}',v)
  if k in ('origens','marcantes','equipamentos'):
   tipos={'origens':['Origem'],'marcantes':['Marcante'],'equipamentos':['Arma','Escudo','Uniforme','Item comum']}[k]
   for row,n in enumerate(range(1,QUANTIDADE+1),len(values)+2):
    g=cartao(n);pred='OR('+','.join(ref(g['tipo'],'CONFIGURAÇÃO')+'='+texto(t) for t in tipos)+')'
    helper(f'{ix._letras(c)}{row}',f'=IF({pred},{ref(g["nome"],"CONFIGURAÇÃO")},"")')
 def menu(c,source):
  a['menus'].append({'tipo':'list','formula':source,'onde':c,'vazio_ok':True,'mostra_seta':True,'estrito':True})
  a['menus_estritos'].append(c)
 put('J5','CONTEÚDO CUSTOM','secao','O5')
 put('J6',f'=IF(({aviso_global[1:]})="","Livro + custom nos menus. MESTRE VIU é um lembrete; o bot aprova no chat.","⚠ "&({aviso_global[1:]}))','nota','O7')
 a.setdefault('condicional_gs',[]).append({'faixas':['J6'],'contem':'⚠','fundo':'#C2334D','fonte':'#FFFFFF'})
 for n in range(1,QUANTIDADE+1):
  g=cartao(n);r=g['inicio'];t=ref(g['tipo'],'CONFIGURAÇÃO')
  put(f'J{r}',f'CARTÃO {n} · CUSTOM','secao',f'O{r}')
  put(f'J{r+1}','TIPO','rotulo',f'M{r+1}', 'Troque o tipo e revise os valores que já estavam guardados.')
  put(f'N{r+1}','MESTRE VIU','rotulo',f'O{r+1}', 'Lembrete do jogador; aprovação só pelo bot no chat.')
  put(g['tipo'],None,'entrada',f'M{r+2}');menu(g['tipo'],pr['tipos'])
  put(g['mestre_viu'],False,'caixa',f'O{r+2}')
  put(f'J{r+3}','NOME','rotulo',f'O{r+3}', 'Nome único. Capacidades apontam para o nome da Origem, do livro ou custom.')
  put(g['nome'],None,'entrada',f'O{r+4}')
  for i,c in enumerate(g['campos']):
   label=f'J{r+5+i}'
   note='Campos por tipo: '+'; '.join(k+': '+(v[i] or 'não usado') for k,v in CAMPOS.items())+'.'
   if i<4:note+=' Origem: quatro opções distintas, escolha uma ao criar o personagem.'
   if i==0:note+=' Marcante própria: só Restrição corporal ou Origem criada do zero; base do livro mantém opções publicadas (R52).'
   if i==5:note+=' BASE DO LIVRO = Nenhuma permite criar do zero; rota própria, sem herdar benefícios exclusivos.'
   put(label,'='+escolha(t,{k:texto(v[i]) for k,v in CAMPOS.items()}),'rotulo',f'K{r+5+i}',note)
   put(c,None,'entrada',f'O{r+5+i}',note)
   if i<7:
    col=110+(n-1)*7+i
    opts=escolha(t,{k:texto(pr['origens_marcante' if k=='Marcante' and i==0 else lista_campo(v[i])]) for k,v in CAMPOS.items()},texto(pr['vazio']))
    helper(f'{ix._letras(col)}1',f'cartão {n} · opção {i+1}')
    helper(f'{ix._letras(col)}2',f'=IFERROR(UNIQUE(FILTER(INDIRECT({opts}),INDIRECT({opts})<>"")),"")')
    menu(c,faixa(col,160))
  put(f'J{r+18}','EFEITO · DESCRIÇÃO','rotulo',f'O{r+18}', 'Texto integral. Descreve regras; não interpreta a prosa como cálculo.')
  put(g['efeito'],None,'efeito',f'O{r+23}')
  put(g['aviso'],f'=IF({ref("S"+str(n+1))}="","Revise os valores ao trocar o tipo.","⚠ "&{ref("S"+str(n+1))})','nota',f'O{r+25}')
  a.setdefault('condicional_gs',[]).append({'faixas':[f'J{r+5}:O{r+17}'],'formula':f'=$J{r+5}=""','fundo':'#'+layout['estilos'][st['fundo']][1]})
  a.setdefault('condicional',[]).append({'tipo':'expression','onde':f'J{r+5}:O{r+17}',
       'formula':[f'$J{r+5}=""'],'cor_texto':None,'fundo':layout['estilos'][st['fundo']][1]})
 # Registro cru independente de validação: o bot precisa ler inclusive entradas inválidas.
 heads=['registro','tipo','nome','mestre viu']+[f'campo {i}' for i in range(1,14)]+['efeito','problema','válido']
 for i,v in enumerate(heads,1):helper(f'{ix._letras(i)}1',v)
 for n in range(1,QUANTIDADE+1):
  g=cartao(n);row=n+1;helper(f'A{row}',n)
  for col,c in zip([2,3,4,*range(5,18),18],[g['tipo'],g['nome'],g['mestre_viu'],*g['campos'],g['efeito']]):
   rr=ref(c,'CONFIGURAÇÃO');helper(f'{ix._letras(col)}{row}',f'=IF(ISBLANK({rr}),"",{rr})')
 for item in h['celulas']:item[2]=tr['estilo_dados']
 return tr


def exporta(tr):
 """Nomes semânticos estáveis, inclusive campos vazios e registros inválidos."""
 from analise import chave
 out=[]
 campos=sorted({label for labels in CAMPOS.values() for label in labels if label})
 for g in tr['cartoes']:
  n=g['n'];t=ref(g['tipo'],'CONFIGURAÇÃO')
  for key,c in [('tipo',g['tipo']),('nome',g['nome']),('mestre_viu',g['mestre_viu']),('efeito',g['efeito'])]:
   rr=ref(c,'CONFIGURAÇÃO')
   formula=f'=N({rr})&""' if key=='mestre_viu' else f'=IF(ISBLANK({rr}),"",{rr}&"")'
   out.append([f'custom.{n}.{key}',formula,rr.replace('$',''),'configuração'])
  for label in campos:
   opts={typ:ref(g['campos'][labels.index(label)],'CONFIGURAÇÃO') for typ,labels in CAMPOS.items() if label in labels}
   expr=escolha(t,{typ:f'IF(ISBLANK({rr}),"",{rr}&"")' for typ,rr in opts.items()})
   out.append([f'custom.{n}.campo.{chave(label)}','='+expr,' '.join(v.replace('$','') for v in opts.values()),'configuração'])
  out.append([f'aviso.custom.{n}',f'={ref("S"+str(n+1))}&""',f'{NOME}!S{n+1}','aviso'])
 return out


def valida(tr, fp):
 """Diagnósticos em camadas, sem dependência circular entre pais e filhos."""
 h=tr['aba'];pools=tr['pools'];L=tr['listas']
 def put(c,v):h['celulas'].append([c,v,None])
 import ficha_automatica
 variantes=[o+ficha_automatica.SEM_TECNICA for o in L['origens'][:5]]
 nomes=sorted(set(variantes+['Escolha sua Origem',fp['R']['origens_do_livro']['criada']]+L['origens']+L['equipamentos']+[x['nome'] for o in fp['R']['origens_do_livro']['origens'] for x in o['marcantes']+o['menores']]))
 for r,n in enumerate(nomes,2):put(f'BV{r}',n)
 h['linhas']=max(h['linhas'],len(nomes)+1)
 livros=faixa(74,len(nomes)+1)
 tipos=faixa(2,QUANTIDADE+1);nomes_custom=faixa(3,QUANTIDADE+1)
 basicos=faixa(21,QUANTIDADE+1)
 for n in range(1,QUANTIDADE+1):
  row=n+1;g=cartao(n);t=f'$B{row}';name=f'$C{row}'
  checks=[f'IF(COUNTIF({pools["tipos"]},{t})=0,"Escolha um tipo válido","")',
          f'IF(LEN(TRIM({name}))=0,"Preencha NOME","")',
          f'IF(OR(COUNTIF({nomes_custom},{name})>1,COUNTIF({livros},{name})>0),"Nome repetido no livro ou custom","")']
  for i,c in enumerate(g['campos']):
   v=f'${ix._letras(5+i)}{row}'
   used=escolha(t,{k:texto(labels[i]) for k,labels in CAMPOS.items()})
   if i<7:
    ps=escolha(t,{k:texto(pools['origens_marcante' if k=='Marcante' and i==0 else lista_campo(labels[i])]) for k,labels in CAMPOS.items()},texto(pools['vazio']))
    checks.append(f'IF(AND({v}<>"",{used}=""),"Apague campo que este tipo não usa",IF(AND({v}<>"",COUNTIF(INDIRECT({ps}),{v})=0),"Opção inválida: "&{used},""))')
   else:
    numeric={typ:label for typ,labels in CAMPOS.items() if (label:=labels[i]) in ['FORÇA','VOLUME','PREÇO','PROTEÇÃO','TETO DE DESTREZA','DESGASTE','RECARGA']}
    pred='OR('+','.join(t+'='+texto(k) for k in numeric)+')'
    dash_types=[typ for typ,label in numeric.items() if label in ['FORÇA','TETO DE DESTREZA','RECARGA','DESGASTE']]
    dash='OR('+','.join(t+'='+texto(k) for k in dash_types)+')' if dash_types else 'FALSE'
    checks.append(f'IF(AND({v}<>"",{used}=""),"Apague campo que este tipo não usa",IF(AND({pred},{v}<>"",NOT(ISNUMBER({v})),NOT(AND({v}="—",{dash}))),"Informe número: "&{used},""))')
  required={'Origem': [0,1,2,3,4], 'Marcante':[0], 'Menor':[0], 'Arma':[0,1,2,7,8,9], 'Escudo':[7,8,9,10],
            'Uniforme':[0,7,8,9,10], 'Item comum':[7], 'Ferramenta amaldiçoada':[0,1]}
  for typ,ii in required.items():
   blanks='OR('+','.join(f'${ix._letras(5+i)}{row}=""' for i in ii)+')'
   checks.append(f'IF(AND({t}={texto(typ)},{blanks}),"Preencha os campos obrigatórios de {typ}","")')
  unique='COUNTA(E'+str(row)+':H'+str(row)+')=4'
  distinct='AND('+','.join(f'{a}{row}<>{b}{row}' for i,a in enumerate('EFGH') for b in 'EFGH'[i+1:])+')'
  checks.append(f'IF(AND({t}="Origem",{unique},NOT({distinct})),"Escolha quatro perícias diferentes","")')
  # Uma base herda suas regras, sem deixar ROTA contradizer o pacote escolhido.
  O=fp['R']['origens_do_livro']['origens']
  for o in O:
   base=o['menu'];routes=ROTAS[:2] if base in [x['menu'] for x in O[:5]] else [ROTAS[3] if 'Sem Energia' in base else ROTAS[2] if base=='Corpo Amaldiçoado' else ROTAS[0]]
   good='OR('+','.join(f'I{row}={texto(r)}' for r in routes)+')'
   checks.append(f'IF(AND({t}="Origem",J{row}={texto(base)},NOT({good})),"ROTA não combina com BASE DO LIVRO","")')
  # Keep each expression below the XLSX limit without changing diagnostics,
  # their order, or the published U/S sources. These columns are internal only.
  chunks=[];chunk=[];size=0
  for check in checks:
   if chunk and size+len(check)>5000:chunks.append(chunk);chunk=[];size=0
   if len(check)>8000:raise ValueError('Validação básica excede limite por expressão')
   chunk.append(check);size+=len(check)
  if chunk:chunks.append(chunk)
  guard=f'AND({t}="",{name}="",LEN(TEXTJOIN("",TRUE,E{row}:R{row}))=0)'
  for i,part in enumerate(chunks):
   col=285+i;expr='TEXTJOIN(" · ",TRUE,'+','.join(part)+')'
   put(f'{ix._letras(col)}{row}',f'=IF({guard},"",{expr})')
   if n==1:put(f'{ix._letras(col)}1','erro básico · parte '+str(i+1))
  h['colunas']=max(h['colunas'],284+len(chunks))
  put(f'U{row}',f'=TEXTJOIN(" · ",TRUE,{ix._letras(285)}{row}:{ix._letras(284+len(chunks))}{row})')
  # Capacidade aponta para Origem existente e válida; não consulta a validação dos filhos.
  parent=f'E{row}'
  good_parent=f'OR(COUNTIF({pools["bases"]},{parent})>0,COUNTIFS({nomes_custom},{parent},{tipos},"Origem",{basicos},"")=1)'
  own_base=f'IFERROR(INDEX({faixa(10,QUANTIDADE+1)},MATCH({parent},{nomes_custom},0)),{parent})'
  allows=f'OR({parent}={texto(RESTRICAO)},AND(COUNTIFS({nomes_custom},{parent},{tipos},"Origem",{basicos},"")=1,OR({own_base}="",{own_base}={texto(SEM_BASE)},{own_base}={texto(RESTRICAO)})))'
  put(f'V{row}',f'=IF(AND(OR({t}="Marcante",{t}="Menor"),NOT({good_parent})),"Origem vinculada não existe ou tem erro",IF(AND({t}="Marcante",NOT({allows})),"Marcante própria só para Restrição corporal ou Origem do zero; use a marcante publicada da base",""))')
  requires=f'F{row}'
  bookcap=[]
  for o in O:
   for cap in o['marcantes']:bookcap.append('AND('+requires+'='+texto(cap['nome'])+','+'OR('+parent+'='+texto(o['menu'])+','+own_base+'='+texto(o['menu'])+')'+')')
  customcap=f'COUNTIFS({nomes_custom},{requires},{tipos},"Marcante",{faixa(5,QUANTIDADE+1)},{parent},{basicos},"",{faixa(22,QUANTIDADE+1)},"")=1'
  put(f'W{row}',f'=IF(AND({t}="Menor",{requires}<>"",{requires}<>"—",NOT(OR('+','.join(bookcap+[customcap])+'))),"Marcante exigida não pertence à Origem ou tem erro","")')
  bookbases=list(set(L['equipamentos']))
  literal=f'COUNTIF({faixa(78+list(L).index("equipamentos"),len(L["equipamentos"])+1)},{parent})>0'
  allowed='OR('+','.join(f'COUNTIFS({nomes_custom},{parent},{tipos},{texto(k)},{basicos},"")=1' for k in ['Arma','Escudo','Uniforme','Item comum'])+')'
  put(f'X{row}',f'=IF(AND({t}="Ferramenta amaldiçoada",NOT(OR({literal},{allowed}))),"Base da ferramenta não existe ou tem erro","")')
  put(f'S{row}',f'=TEXTJOIN(" · ",TRUE,U{row},V{row},W{row},X{row})')
  put(f'T{row}',f'=AND(B{row}<>"",C{row}<>"",S{row}="")')
 # Duas colunas de diagnóstico extra sem adicionar campos ao cartão.
 for c,v in [('U1','erro básico'),('V1','erro de vínculo'),('W1','erro de marcante'),('X1','erro de ferramenta'),('BV1','nomes reservados do livro')]:put(c,v)


def tabelas(layout,tr,fp):
 """Catálogos combinados. Bases de ferramenta usam só os registros básicos,
 nunca a lista final que contém a própria ferramenta.
 """
 from configuracao import qualifica
 h=tr['aba'];T={};rows={}
 def put(c,v):h['celulas'].append([c,v,None])
 def tabela(k,col,headers,values):
  for i,v in enumerate(headers):put(f'{ix._letras(col+i)}1',v)
  for r,values_row in enumerate(values,2):
   for i,v in enumerate(values_row):
    if v is not None:put(f'{ix._letras(col+i)}{r}',v)
  T[k]=(col,2,len(values)+1,len(headers));rows[k]=values
  h['linhas']=max(h['linhas'],len(values)+1)
 def tab(k,only=None,base=False):
  c,lo,hi,w=T[k]
  if base:hi-=QUANTIDADE
  return faixa(c+(only or 0),hi,lo,1 if only is not None else w)
 def book(k):
  col,l1,l2,w=fp['T'][k];cells={x[0]:x[1] for x in ix._aba(layout,'DADOS')['celulas']}
  return [[qualifica(v,'DADOS') if isinstance(v,str) and v.startswith('=') else v
           for i in range(w) for v in [cells.get(f'{ix._letras(col+i)}{r}')]] for r in range(l1,l2+1)]
 # Base rows have validation U only; independent of tools/capacity dependencies.
 def gate(row,types,values,base=True):
  pred='AND(OR('+','.join(f'$B{row}={texto(t)}' for t in types)+f'),$C{row}<>"",'+(f'$U{row}=""' if base else f'$T{row}=TRUE')+')'
  return [f'=IF({pred},{v},"")' for v in values]
 R=fp['R'];cats=fp['faixa_t']('categ')
 equip=book('equip');unif=book('unif');items=[[i['nome'],i['volume'],i['preco'],i['texto']] for i in itens_livro()]
 # Shield/uniform stats are separate from descriptive properties.
 stat=[]
 for s in R['escudos']:
  teto=re.search(r'teto de Destreza (\d+)',s['propriedades'])
  stat.append([s['nome'],'Escudo',s['protecao'],int(teto.group(1)) if teto else '—',s['forca'],s['volume'],'—','',''])
 for u in R['uniformes']:stat.append([u['nome'],'Uniforme',u['protecao'],u['teto'],u['forca'],u['volume'],u['grau'],'',''])
 for a in R['armas']:stat.append([a['nome'],'Arma',0,'—',a['forca'],a['volume'],'—','',''])
 for i in itens_livro():stat.append([i['nome'],'Item comum',0,'—',0,i['volume'],'—','',''])
 for row in range(2,QUANTIDADE+2):
  name=f'$C{row}';typ=f'$B{row}';f=lambda i:f'${ix._letras(5+i)}{row}'
  shield=f'{typ}="Escudo"';strength=f'IF({shield},{f(9)},{f(8)})';vol=f'IF({shield},{f(10)},{f(9)})'
  props=f'IF({shield},"Proteção +"&{f(7)}&" · teto de Destreza "&{f(8)},TEXTJOIN(" · ",TRUE,IF({f(3)}="—","",{f(3)}),IF({f(4)}="—","",{f(4)}),IF({f(5)}="—","",{f(5)}),IF({f(6)}="—","",{f(6)})))'
  equip.append(gate(row,['Arma','Escudo'],[name,f'IF({shield},"Escudo",{f(0)})',f'IF({shield},1,{f(1)})',f'IF({shield},"—",{f(7)})',props,strength,vol,f'IF({shield},"",{f(10)})',f'IF({shield},"",{f(11)})',f'IF({shield},TRUE,IFERROR(VLOOKUP({f(0)},{cats},4,FALSE),FALSE))','""']))
  unif.append(gate(row,['Uniforme'],[name,f(7),f(8),f(9),f(10),f'IFERROR(VLOOKUP({f(0)},{fp["faixa_t"]("grau")},3,FALSE),1)',f(0)]))
  items.append(gate(row,['Item comum'],[name,f(7),f(8),f'$R{row}']))
  stat.append(gate(row,['Arma','Escudo','Uniforme','Item comum'],[name,typ,
      f'IF(OR({typ}="Escudo",{typ}="Uniforme"),{f(7)},0)',f'IF(OR({typ}="Escudo",{typ}="Uniforme"),{f(8)},"—")',
      f'IF({typ}="Arma",{f(8)},IF({typ}="Item comum",0,{f(9)}))',
      f'IF({typ}="Arma",{f(9)},IF({typ}="Item comum",{f(7)},{f(10)}))',f'IF({typ}="Uniforme",{f(0)},"—")','""','""']))
 # Allocate base-only views now; final tables will extend them with tool rows.
 def register(k,col,values,width):T[k]=(col,2,len(values)+1,width)
 register('equip',27,equip,11);register('unif',39,unif,7);register('item',47,items,4);register('stats',65,stat,9)
 bases={k:tab(k) for k in T}
 for row in range(2,QUANTIDADE+2):
  name=f'$C{row}';base=f'$E{row}';kind=f'IFERROR(VLOOKUP({base},{bases["stats"]},2,FALSE),"")'
  pred=f'AND($B{row}="Ferramenta amaldiçoada",$T{row}=TRUE)'
  def tool(values,when='TRUE'):return [f'=IF(AND({pred},{when}),{v},"")' for v in values]
  v=lambda k,j:f'IFERROR(VLOOKUP({base},{bases[k]},{j},FALSE),"")'
  eqv=[name]+[v('equip',j) for j in range(2,12)]
  # The tool's Volume overrides base only when provided; zero is explicit.
  eqv[6]=f'IF($N{row}="",{v("equip",7)},$N{row})'
  equip.append(tool(eqv,f'OR({kind}="Arma",{kind}="Escudo")'))
  uv=[name]+[v('unif',j) for j in range(2,8)];uv[4]=f'IF($N{row}="",{v("unif",5)},$N{row})'
  unif.append(tool(uv,f'{kind}="Uniforme"'))
  iv=[name,f'IF($N{row}="",{v("item",2)},$N{row})',f'$O{row}',f'$R{row}']
  items.append(tool(iv,f'{kind}="Item comum"'))
  sv=[name,kind,v('stats',3),v('stats',4),v('stats',5),f'IF($N{row}="",{v("stats",6)},$N{row})',f'$F{row}',f'$L{row}',f'$M{row}']
  stat.append(tool(sv))
 tabela('equip',27,['equipável','categoria','mão','dado','propriedades','força','volume','alcance','recarga','treino','caixa do treino'],equip)
 tabela('unif',39,['uniforme','proteção','teto','força','volume','ordem do grau','grau mínimo'],unif)
 tabela('item',47,['item','volume','preço','descrição'],items)
 tabela('stats',65,['nome','tipo base','proteção','teto','força','volume','grau','estigma','desgaste'],stat)
 caps=book('origem_cap');origens=book('origem_base')
 for row in range(2,QUANTIDADE+2):
  caps.append(gate(row,['Marcante','Menor'],[f'$C{row}',f'$E{row}',f'IF($B{row}="Marcante","marcante","menor")',f'IF($B{row}="Menor",IF($F{row}="—","",$F{row}),"")',f'$L{row}',f'$R{row}'],False))
  origens.append(gate(row,['Origem'],[f'$C{row}',f'TEXTJOIN(" · ",TRUE,$E{row}:$H{row})',f'$I{row}'],False))
 tabela('origem_cap',52,['capacidade','origem','tipo','exige','frequência','texto'],caps)
 tabela('origem_base',59,['origem','perícias','rota'],origens)
 tr.update(T=T,tab=tab,bases=bases)


def prepara(layout):
 if any(a['nome']==NOME for a in layout['abas']):
  raise ValueError('custom aplicado duas vezes')
 h=aba_dados();layout['abas'].append(h)
 neutral=[['Roboto',10,'000000',False,False],'FFFFFF',None,None,None]
 if neutral not in layout['estilos']:layout['estilos'].append(neutral)
 data_style=layout['estilos'].index(neutral)
 pools=listas();pc={k:78+i for i,k in enumerate(pools)}
 return {'aba':h,'estilo_dados':data_style,'listas':pools,'pools':{**{k:faixa(c,160) for k,c in pc.items()},'origens_marcante':faixa(75,160)},
         'cartoes':[cartao(n) for n in range(1,QUANTIDADE+1)]}


def integra(layout,tr,fp):
 """Trocas explícitas das fontes e contas. Não modifica nem desloca índices."""
 from ficha_pessoal import COLS_EQUIP, COLS_ITENS
 cells={a['nome']:{x[0]:x for x in a['celulas']} for a in layout['abas']}
 antes={};depois={}
 def put(aba,c,v):
  old=cells[aba].get(c,[c,None,None])[1]
  if old==v:return
  antes.setdefault(aba,{}).setdefault(c,old);depois.setdefault(aba,{})[c]=v
  if c in cells[aba]:cells[aba][c][1]=v
  else:
   item=[c,v,None];ix._aba(layout,aba)['celulas'].append(item);cells[aba][c]=item
 tab=tr['tab'];H=fp['H'];G=fp['G'];idx=ix.indice(layout)
 # Replace all exact table ranges, including single columns in FILTER sources.
 replacements={}
 for k in ['equip','unif','origem_cap','origem_base']:
  for only in [None,*range(fp['T'][k][3])]:
   replacements[fp['faixa_t'](k,so=only)]=tab(k,only)
 for a in layout['abas']:
  if a['nome']==NOME:continue
  for x in list(a['celulas']):
   if isinstance(x[1],str) and x[1].startswith('='):
    new=x[1]
    for old,v in replacements.items():new=new.replace(old,v)
    put(a['nome'],x[0],new)
  for m in a.get('menus',[]):
   for old,v in replacements.items():m['formula']=m['formula'].replace(old,v)
 pessoal=ix._aba(layout,'FICHA PESSOAL')
 livres=pessoal.setdefault('livres',[])
 def manual(c,v):
  put('FICHA PESSOAL',c,v)
  if c not in livres:livres.append(c)
 # Every inventory slot accepts catalog entries and free typing.
 equip_menu=f'D{G["equip_ini"]}:D{G["equip_fim"]}'
 pessoal['menus']=[m for m in pessoal['menus'] if not m['onde'].startswith('D'+str(G['equip_ini']))]
 pessoal['menus'].append({'tipo':'list','formula':tab('equip',0),'onde':equip_menu,'vazio_ok':True,'mostra_seta':True})
 source={'Categoria':2,'Mão':3,'Dado':4,'Propriedades':5,'Força':6}
 for row in range(G['equip_ini'],G['equip_fim']+1):
  for label,c,_ in COLS_EQUIP:
   if label in source:
    v=f'=IF($D{row}="","",IFERROR(VLOOKUP($D{row},{tab("equip")},{source[label]},FALSE),""))'
   elif label=='Vol.':v=f'=IF($D{row}="","",IFERROR(IF($K{row}="",1,$K{row})*VLOOKUP($D{row},{tab("equip")},7,FALSE),""))'
   else:continue
   if row>=G['equip_ini']+6:manual(c+str(row),v)
  for c,col in [('AI',7),('AK',8),('AQ',9)]:
   manual(c+str(row),f'=IF($D{row}="","",IFERROR(VLOOKUP($D{row},{tab("stats")},{col},FALSE),""))')
 for columns in COLS_ITENS:
  (_,name,_),(_,qty,_),(_,volume,_)=columns
  pessoal['menus'].append({'tipo':'list','formula':tab('item',0),'onde':f'{name}{G["itens_ini"]}:{name}{G["itens_fim"]}', 'vazio_ok':True,'mostra_seta':True})
  for row in range(G['itens_ini'],G['itens_fim']+1):
   old=cells['FICHA PESSOAL'][volume+str(row)][1]
   vol=f'IFERROR(VLOOKUP(${name}{row},{tab("item")},2,FALSE),{fp["R"]["leve"]})'
   manual(volume+str(row),f'=IF(${name}{row}="","",IF(${qty}{row}="",1,${qty}{row})*{vol})')
 # Menu capacity filters must accommodate all custom records; use hidden spare
 # columns rather than overwriting adjacent original DADOS tables.
 for k,col in [('menu_marcante',94),('menu_menor',95),('menu_vestindo',96)]:
  c,l1,l2,w=fp['T'][k];oldrange=fp['faixa_t'](k,so=0)
  values=[cells['DADOS'].get(f'{ix._letras(c)}{r}',[None,None])[1] for r in range(l1,l2+1)]
  for i,v in enumerate(values,2):
   if v is not None:
    tr['aba']['celulas'].append([f'{ix._letras(col)}{i}', ('='+__import__('configuracao').qualifica(v,'DADOS')[1:]) if isinstance(v,str) and v.startswith('=') else v,None])
  newrange=faixa(col,160)
  for m in pessoal['menus']:
   if m['formula']==oldrange:m['formula']=newrange
 # R52: book bases keep published marcantes. No-base homebrew and corporal
 # restriction keep their creation permission, explicitly confirmed by Mizuki.
 selected=H['origem da ficha']
 base=f'IFERROR(INDEX({faixa(10,QUANTIDADE+1)},MATCH({selected},{faixa(3,QUANTIDADE+1)},0)),"")'
 customorigin=f'COUNTIFS({faixa(3,QUANTIDADE+1)},{selected},{faixa(2,QUANTIDADE+1)},"Origem",{faixa(20,QUANTIDADE+1)},TRUE)=1'
 can_create=f'OR({selected}={texto(RESTRICAO)},AND({customorigin},OR({base}="",{base}={texto(SEM_BASE)},{base}={texto(RESTRICAO)})))'
 cmenu=faixa(94,160)
 inherited=f'(({tab("origem_cap",1)}={selected})+(({base}<>"")*({base}<>{texto(SEM_BASE)})*({tab("origem_cap",1)}={base})))'
 corrections={
  'CP2':f'=IF({can_create},{texto(fp["R"]["origens_do_livro"]["criada"])},"")',
  'CP3':f'=IFERROR(FILTER({tab("origem_cap",0)},{inherited},{tab("origem_cap",2)}="marcante"),"")',
  'CQ3':f'=IFERROR(FILTER({tab("origem_cap",0)},{inherited},{tab("origem_cap",2)}="menor",({tab("origem_cap",3)}="")+({tab("origem_cap",3)}={ref(G["cap_menu"][0],"FICHA PESSOAL")})),"")'}
 for c,v in corrections.items():
  tr['aba']['celulas'][:]=[x for x in tr['aba']['celulas'] if x[0]!=c]
  tr['aba']['celulas'].append([c,v,None])
 pessoal.setdefault('menus_estritos',[]).append(G['cap_menu'][0])
 for m in pessoal['menus']:
  if m['onde']==G['cap_menu'][0]:m['estrito']=True
 # Pasted legacy names are diagnosed too; never describe an illegal selection as created.
 freq=G['cap_freq'][0];old=cells['FICHA PESSOAL'][freq][1];mn=ref(G['cap_menu'][0],'FICHA PESSOAL')
 put('FICHA PESSOAL',freq,f'=IF(AND({mn}<>"",COUNTIF({cmenu},{mn})=0),"⚠ Marcante inválida para esta Origem; escolha uma opção do menu.",{old[1:]})')
 pessoal.setdefault('notas',{})[G['cap_menu'][0]]='R52: use uma marcante publicada da Origem ou da BASE DO LIVRO. Marcante própria somente para Restrição corporal ou Origem do zero (BASE DO LIVRO = Nenhuma). Cadastre no CONTEÚDO CUSTOM ou use a opção criada com o mestre quando disponível. Menores e Legados de história continuam personalizáveis.'

 # Origin menu adds only usable custom definitions, not capabilities or tools.
 ori_col=97;bookmenu=[]
 origem_coord=idx['origem'];originalmenu=next(m for m in ix._aba(layout,'FICHA')['menus'] if origem_coord in m['onde'].split())
 m=re.fullmatch(r'DADOS!\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)',originalmenu['formula'])
 if not m:raise ValueError(('menu de origem inesperado',originalmenu))
 for r in range(int(m[2]),int(m[4])+1):
  value=cells['DADOS'].get(f'{m[1]}{r}',[None,None])[1]
  bookmenu.append(value)
 for i,v in enumerate(bookmenu,2):tr['aba']['celulas'].append([f'{ix._letras(ori_col)}{i}',v,None])
 for i,row in enumerate(range(2,QUANTIDADE+2),len(bookmenu)+2):
  tr['aba']['celulas'].append([f'{ix._letras(ori_col)}{i}',f'=IF(AND($B{row}="Origem",$T{row}=TRUE),$C{row},"")',None])
 originalmenu['formula']=faixa(ori_col,len(bookmenu)+QUANTIDADE+1)
 # Selected origin metadata. Invalid selections are diagnosed, never guessed.
 ori=ref(origem_coord,'FICHA');lookup=f'IFERROR(MATCH({ori},{faixa(3,QUANTIDADE+1)},0),0)'
 helpers={
  'B120':'='+lookup,
  'B121':f'=IF($B$120=0,FALSE,AND(INDEX({faixa(2,QUANTIDADE+1)},$B$120)="Origem",INDEX({faixa(20,QUANTIDADE+1)},$B$120)=TRUE))',
  'B122':f'=IF($B$121,INDEX({faixa(9,QUANTIDADE+1)},$B$120),"")',
  'B123':f'=IF($B$121,INDEX({faixa(10,QUANTIDADE+1)},$B$120),"")',
  'B124':f'=IF($B$121,INDEX({faixa(11,QUANTIDADE+1)},$B$120),"")',
  'B125':f'=IF($B$121,INDEX({faixa(12,QUANTIDADE+1)},$B$120),"")'}
 for c,v in helpers.items():tr['aba']['celulas'].append([c,v,None])
 # Preserve the old branch verbatim for every book Origin.
 for aba in ['DADOS']:
  for c,x in list(cells[aba].items()):
   if not isinstance(x[1],str) or not x[1].startswith('='):continue
   labelcol=ix._letras(ix._lc(c)[1]-1)+str(ix._lc(c)[0]);label=cells[aba].get(labelcol,[None,None])[1]
   if label not in ['sem energia','sem técnica','técnica marcial']:continue
   cond={'sem energia':f'{ref("B122")}="{ROTAS[3]}"','sem técnica':f'{ref("B122")}="Manejos"',
         'técnica marcial':f'OR({ref("B122")}="{ROTAS[2]}",{ref("B122")}="{ROTAS[3]}")'}[label]
   put(aba,c,f'=IF({ref("B121")},IF({cond},1,0),{x[1][1:]})')
 # User-owned creation records can default from the custom card, while preserving
 # a manually entered instance value (same mechanism used by capacity text).
 manual(G['oficio'],f'=IF({ref("B121")},{ref("B124")},"")')
 manual(G['ce4'],f'=IF({ref("B121")},{ref("B125")},"")')
 ce4row,ce4col=ix._lc(G['ce4']);ce4label=f'{ix._letras(ce4col)}{ce4row-1}'
 oldlabel=cells['FICHA PESSOAL'][ce4label][1]
 put('FICHA PESSOAL',ce4label,f'=IF({ref("B121")},"TALENTO DE CATEGORIA DE EFEITO 4 · REGISTRO DA ORIGEM CUSTOM",{texto(oldlabel)})')
 sub=G['oficio_sub'];old=cells['FICHA PESSOAL'][sub][1]
 put('FICHA PESSOAL',sub,f'=IF({ref("B121")},IF({ref("B124")}="—","sem ofício de reparo definido","ofício definido na CONFIGURAÇÃO"),{old[1:]})')
 for c in G['cap_freq']:
  old=cells['FICHA PESSOAL'][c][1]
  # Same frequency and text lookup; identify the provenance accurately.
  put('FICHA PESSOAL',c,old.replace('&" · do livro"','&IF(COUNTIF('+faixa(3,QUANTIDADE+1)+',VLOOKUP('+ref(G['cap_menu'][G['cap_freq'].index(c)],'FICHA PESSOAL')+','+tab('origem_cap')+',1,FALSE))>0," · custom"," · do livro")'))
 # Shield/uniform stats replace the closed pair lookup only for custom gear.
 P=ref(G['principal'],'FICHA PESSOAL');S=ref(G['secundaria'],'FICHA PESSOAL');V=ref(G['vestindo'],'FICHA PESSOAL')
 customgear=f'OR(COUNTIF({faixa(3,QUANTIDADE+1)},{V})>0,AND({H["escudo na secundária"]}=1,COUNTIF({faixa(3,QUANTIDADE+1)},{S})>0))'
 uprot=H['proteção do uniforme'];uteto=H['teto do uniforme'];uv=H['uniforme vale'];esc=H['escudo na secundária']
 shieldprot=f'IF({esc}=1,IFERROR(VLOOKUP({S},{tab("stats")},3,FALSE),0),0)'
 shieldteto=f'IF({esc}=1,IFERROR(VALUE(VLOOKUP({S},{tab("stats")},4,FALSE)&""),9999),9999)'
 # Read PASSIVA from the original defense formula so book constants stay owned
 # by defesa_equipamento rather than being duplicated here.
 from openpyxl.formula import Tokenizer
 protcell=idx['proteção'];old=cells['FICHA'][protcell][1]
 toks=Tokenizer(old).items;depth=0;args=[];part=[];tail=''
 for pos,tok in enumerate(toks[1:],1):
  if tok.subtype=='CLOSE' and depth==0:
   args.append(''.join(part));tail=''.join(x.value for x in toks[pos+1:]);break
  if tok.type=='SEP' and tok.subtype=='ARG' and depth==0:
   args.append(''.join(part));part=[];continue
  if tok.subtype=='OPEN':depth+=1
  if tok.subtype=='CLOSE':depth-=1
  part.append(tok.value)
 if len(args)!=3:raise ValueError(('Proteção não é IF de três argumentos',old))
 passive=args[1]
 put('FICHA',protcell,f'=IF({customgear},IF({uv}=1,{uprot},{passive})+{shieldprot}{tail},{old[1:]})')
 des=ref(idx['atr_Destreza'],'FICHA');buff=ref(idx['buff de defesa'],'FICHA')
 teto=f'MIN(IFERROR(VALUE({uteto}&""),9999),{shieldteto})'
 old=cells['FICHA'][idx['defesa']][1]
 put('FICHA',idx['defesa'],f'=IF({customgear},10+MIN({des},{teto})+{ref(protcell,"FICHA")}+IFERROR(VALUE({buff}&""),0),{old[1:]})')
 # Invalid selected custom records must not silently fall back to an avulso value.
 # The visible per-card warning and ANALISE publish the cause.
 tr['antes']=antes;tr['depois']=depois


def guarda(tr):
 # Exact whole-formula mapping used only by legacy validators; custom mechanics
 # have separate scenarios and may not pass by merely matching this map.
 pairs={v:tr['antes'][a][c] for a,cs in tr['depois'].items() for c,v in cs.items()
        if isinstance(v,str) and v.startswith('=') and isinstance(tr['antes'][a][c],str) and tr['antes'][a][c].startswith('=')}
 (RAIZ/'ficha-v01/custom-formulas.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2)+'\n')


def anterior(formula):
 if not isinstance(formula,str):return formula
 p=RAIZ/'ficha-v01/custom-formulas.json'
 if not p.exists():return formula
 if not hasattr(anterior,'mapa'):anterior.mapa=json.loads(p.read_text())
 return anterior.mapa.get(formula,formula)
