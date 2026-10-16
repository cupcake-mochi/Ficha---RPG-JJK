# -*- coding: utf-8 -*-
"""B47/3b: Caminho, Trilha e registros curtos aprovados em 15/10/2026.

Reutiliza o grupo 7 e distribui treinos custom em duas colunas.
Mantém os níveis do livro e as chaves de exportação publicadas. Catálogos válidos
alimentam menus e cálculos; ANALISE conserva também entradas inválidas.
Nenhuma descrição é interpretada como fórmula ou concessão de benefício.
"""
import json
from copy import deepcopy
from pathlib import Path
import indice_ficha as ix
import custom
import ficha_automatica as fa
import capacidades as cap
from custom_criacao import criterio

ROOT = Path(__file__).resolve().parent.parent
NOME = 'DADOS_PROGRESSAO'
INICIO = cap.INICIO_PROGRESSAO
CURTOS = cap.CURTOS
INI_CURTOS = cap.INICIO_CURTOS
PASSO = cap.PASSO_CURTOS
ATRIBUTOS = [x[0] for x in ix.ATRS]
NIVEIS = {'Caminho': (2, 7, 15, 23, 30), 'Trilha': (2, 11, 19, 27)}
CAM_FIELDS = ['VIDA INICIAL', 'VIDA POR NÍVEL', 'DADO DE VIDA', 'PE POR NÍVEL',
              'ATRIBUTO NATURAL 1', 'ATRIBUTO NATURAL 2', 'PERÍCIA FIXA 1', 'PERÍCIA FIXA 2',
              'TROCA PERÍCIAS POR ARMA', 'TREINO DE ARMA'] + ['CATEGORIA DE ARMA '+str(i) for i in range(1,14)]


def q(v):
    return '"'+str(v).replace('"','""')+'"'


def ref(c, sheet=NOME):
    r, col = ix._lc(c)
    return f"'{sheet}'!${ix._letras(col)}${r}"


def rg(c, end, start=2, width=1):
    return f"'{NOME}'!${ix._letras(c)}${start}:${ix._letras(c+width-1)}${end}"


def curto(n):
    if not 1 <= n <= CURTOS:
        raise ValueError('registro curto fora da capacidade aprovada')
    r = INI_CURTOS + ((n-1)//2)*PASSO
    c = 2 if n % 2 else 10
    L = ix._letras
    return dict(n=n, categoria='Perícia' if n <= cap.PERICIAS else 'Ofício',
                indice=n if n <= cap.PERICIAS else n-cap.PERICIAS,
                inicio=r, col=c, tipo=f'{L(c)}{r+2}', nome=f'{L(c)}{r+4}',
                mestre_viu=f'{L(c+4)}{r+2}', atributo=f'{L(c+3)}{r+5}',
                efeito=f'{L(c)}{r+7}', aviso=f'{L(c)}{r+11}')


def longo(tipo):
    c = 2 if tipo == 'Caminho' else 10
    L = ix._letras
    return dict(tipo=tipo, col=c, inicio=INICIO, nome=f'{L(c)}{INICIO+4}',
                mestre_viu=f'{L(c+4)}{INICIO+2}',
                campos={k:f'{L(c+3)}{INICIO+5+i}' for i,k in enumerate(CAM_FIELDS if c==2 else ['CAMINHO','BASE DO LIVRO'])},
                efeito=f'{L(c)}{INICIO+32}', aviso=f'{L(c)}{INICIO+36}',
                niveis=[dict(nivel=n,
                             nome=f'{L(c+1)}{INICIO+41+3*NIVEIS[tipo].index(n)}' if n in NIVEIS[tipo] else None,
                             texto=f'{L(c)}{INICIO+42+3*NIVEIS[tipo].index(n)}' if n in NIVEIS[tipo] else None)
                        for n in range(1,31)])


def aba_dados():
    return dict(nome=NOME, estado='hidden', linhas=1, colunas=81,
                padrao=['Roboto',10,'#000000'], fundo_base='#FFFFFF', paleta_fixa=True,
                colunas_larg=[], linhas_alt=[], altura_padrao=15.75, grade=False,
                celulas=[], mescladas=[], menus=[], condicional=[], imagens=[])


def aplica(layout, fp, fiv):
    cat = json.loads((ROOT/'catalogo-projeto-m.json').read_text())
    paths = list(cat['caminhos'])
    trails = fa.trilhas_do_menu(cat)
    cfg = ix._aba(layout, 'CONFIGURAÇÃO')
    data = aba_dados()
    layout['abas'].append(data)
    tr = dict(aba=data, curtos=[curto(n) for n in range(1,CURTOS+1)],
              caminho=longo('Caminho'), trilha=longo('Trilha'), antes={}, depois={},
              entradas=[], linhas_ficha=[])
    # Staging pointwise migration records the old values, including empty cells.
    cells = {a['nome']:{v[0]:v for v in a['celulas']} for a in layout['abas']}
    def put(sheet, c, v, style=None):
        old = cells[sheet].get(c, [c,None,None])
        if old[1] != v:
            tr['antes'].setdefault(sheet,{}).setdefault(c,old[1])
            tr['depois'].setdefault(sheet,{})[c] = v
        if c in cells[sheet]:
            old[1] = v
            if style is not None: old[2] = style
        else:
            item = [c,v,style]
            ix._aba(layout,sheet)['celulas'].append(item)
            cells[sheet][c] = item
    def d(c,v): put(NOME,c,v)
    def input_(key,c): tr['entradas'].append((key,c))
    for g in [tr['caminho'],tr['trilha']]:
        key = 'custom.'+g['tipo'].lower()
        for k in ['nome','mestre_viu','efeito']:
            input_(key+'.'+k,g[k])
        from analise import chave
        for label,c in g['campos'].items(): input_(key+'.campo.'+chave(label),c)
        for lv in g['niveis']:
            for k in ['nome','texto']: input_(key+f'.nivel.{lv["nivel"]}.'+k,lv[k])
    for g in tr['curtos']:
        for k in ['tipo','nome','mestre_viu','atributo','efeito']:
            input_(f'custom.{"pericia" if g["categoria"] == "Perícia" else "oficio"}.{g["indice"]}.{k}',g[k])
    # Raw short records. A name is accepted only once and with a real attribute.
    for c,v in enumerate(['registro','tipo','nome','atributo','mestre viu','descrição','problema'],1): d(f'{ix._letras(c)}1',v)
    for g in tr['curtos']:
        r = g['n']+1
        d(f'A{r}',g['n'])
        for col,k in enumerate(['tipo','nome','atributo','mestre_viu','efeito'],2):
            rr=ref(g[k],'CONFIGURAÇÃO'); d(f'{ix._letras(col)}{r}',f'=IF(ISBLANK({rr}),"",{rr})')
    # Fixed option lists. Separate book-only lists break dependency cycles.
    lists = {39:['Perícia','Ofício'],40:ATRIBUTOS,41:['d4','d6','d8','d10','d12','d20'],
             42:['Sim','Não'],43:['Todas','Categorias selecionadas'],
             44:custom.listas()['categorias'],47:['Nenhuma']+[n for n,_ in trails],
             51:list(cat['pericias']),52:list(cat['oficios']),53:paths,
             54:[n for n,_ in trails]}
    for col, vals in lists.items():
        d(f'{ix._letras(col)}1','opções '+str(col))
        for r,v in enumerate(vals,2): d(f'{ix._letras(col)}{r}',v)
    short_names=rg(3,CURTOS+1)
    for g in tr['curtos']:
        r=g['n']+1
        d(f'G{r}',f'=IF(AND(C{r}="",D{r}="",F{r}="",E{r}=FALSE,B{r}={q(g["categoria"])}),"",TEXTJOIN(" · ",TRUE,'
          f'IF(B{r}<>{q(g["categoria"])},"Tipo incompatível com o cadastro",""),'
          f'IF(OR(C{r}="",TRIM(C{r})<>C{r}),"Preencha NOME sem espaços nas pontas",""),'
          f'IF(OR(COUNTIF({short_names},{criterio("C"+str(r))})>1,COUNTIF($AY$2:$AY$24,{criterio("C"+str(r))})>0,COUNTIF($AZ$2:$AZ$12,{criterio("C"+str(r))})>0),"Nome repetido no livro ou custom",""),'
          f'IF(COUNTIF($AN$2:$AN$6,D{r})=0,"Escolha um atributo válido",""),'
          f'IF(ISLOGICAL(E{r}),"","MESTRE VIU deve ser caixa de seleção")))')
    # Book + valid custom skills and offices, same row count for lookup columns.
    for col,key in [(33,'pericias'),(36,'oficios')]:
        vals=cat[key]
        for i,(name,rule) in enumerate(vals.items(),2):
            d(f'{ix._letras(col)}{i}',name)
            attr = rule.get('atributo','') if isinstance(rule,dict) else ''
            # Ofício's default attribute is in its catalog entry; never infer from the name.
            if isinstance(attr,dict): raise ValueError('atributo inesperado no catálogo')
            d(f'{ix._letras(col+1)}{i}',attr)
        typ='Perícia' if key=='pericias' else 'Ofício'
        for g in (g for g in tr['curtos'] if g['categoria']==typ):
            r=g['n']+1; dest=len(vals)+g['indice']+1
            d(f'{ix._letras(col)}{dest}',f'=IF(AND($B{r}={q(typ)},$C{r}<>"",$G{r}=""),$C{r},"")')
            d(f'{ix._letras(col+1)}{dest}',f'=IF({ix._letras(col)}{dest}="","",$D{r})')
            d(f'{ix._letras(48 if key=="pericias" else 49)}{g["indice"]+1}',f'={ix._letras(col)}{dest}')
    skills=rg(33,len(cat['pericias'])+cap.PERICIAS+1, width=2)
    offices=rg(36,len(cat['oficios'])+cap.OFICIOS+1, width=2)
    # Origem 3a already offers an explicit “—” for no office. Preserve that
    # option without turning it into an office definition or a trained choice.
    office_none = len(cat['oficios'])+cap.OFICIOS+2
    d('AJ'+str(office_none),'—')
    tr['pericias']=skills;tr['oficios']=offices
    # Book paths retain original values and column order N:U used by all life/PE lookups.
    for j,v in enumerate(['Caminho','atributos naturais','vida inicial','vida por nível','PE por nível','perícia fixa 1','perícia fixa 2','dado de vida','troca perícias por arma','treino de arma'],13): d(f'{ix._letras(j)}1',v)
    import campanha
    # Existing six book dice already came from the book parser in campanha.desenha.
    dice={cells['DADOS_CONFIG'][f'AH{r}'][1]:cells['DADOS_CONFIG'][f'AI{r}'][1] for r in range(2,8)}
    for row,name in enumerate(paths,2):
        v=cat['caminhos'][name]
        attrs=v['atributos_naturais']
        vals=[name,' · '.join(attrs),v['vida_inicial'],v['vida_por_nivel'],v['pe_por_nivel'],
              *v['pericias_fixas'],dice[name], 'Sim' if v['troca_duas_pericias_por_arma'] else 'Não',
              'Todas' if v['armas']=='todas' else 'Categorias selecionadas']
        for col,value in enumerate(vals,13): d(f'{ix._letras(col)}{row}',value)
    cam=tr['caminho']; C=lambda k:ref(cam['campos'][k],'CONFIGURAÇÃO')
    name=ref(cam['nome'],'CONFIGURAÇÃO')
    # Path diagnostics are independent of the combined path menu to avoid cycles.
    checks=[f'IF(OR(TRIM({name})<>{name},COUNTIF($BA$2:$BA$7,{name})>0),"Nome de Caminho inválido ou repetido","")',
            f'IF(ISLOGICAL({ref(cam["mestre_viu"],"CONFIGURAÇÃO")}),"","MESTRE VIU deve ser caixa de seleção")']
    for k in ['VIDA INICIAL','VIDA POR NÍVEL','PE POR NÍVEL']:
        v=C(k);checks.append(f'IF(IFERROR(AND(ISNUMBER({v}),{v}>=0,MOD({v},1)=0),FALSE),"",{q(k+": use inteiro não negativo")})')
    for k,col,end in [('DADO DE VIDA','AO',7),('ATRIBUTO NATURAL 1','AN',6),('ATRIBUTO NATURAL 2','AN',6),
                       ('TROCA PERÍCIAS POR ARMA','AP',3),('TREINO DE ARMA','AQ',3)]:
        optional=k=='ATRIBUTO NATURAL 2'
        pred=f'COUNTIF(${col}$2:${col}${end},{C(k)})=0'
        if optional:pred=f'AND({C(k)}<>"",{pred})'
        checks.append(f'IF({pred},{q("Opção inválida: "+k)},"")')
    for k in ['PERÍCIA FIXA 1','PERÍCIA FIXA 2']:
        checks.append(f'IF(COUNTIF({rg(33,len(cat["pericias"])+cap.PERICIAS+1)},{C(k)})=0,{q("Escolha "+k)},"")')
    for a,b in [('ATRIBUTO NATURAL 1','ATRIBUTO NATURAL 2'),('PERÍCIA FIXA 1','PERÍCIA FIXA 2')]:
        checks.append(f'IF(AND({C(a)}<>"",{C(a)}={C(b)}),{q(a+" e 2 devem ser distintos")},"")')
    cats=f"'CONFIGURAÇÃO'!$E${INICIO+15}:$E${INICIO+27}"
    for k in CAM_FIELDS[10:]:
        v=C(k)
        checks.append(f'IF(AND({C("TREINO DE ARMA")}="Categorias selecionadas",{v}<>"",OR(COUNTIF($AR$2:$AR$14,{v})=0,COUNTIF({cats},{v})>1)),"Categoria de arma inválida ou repetida","")')
    d('K2',f'=IF({name}="","",TEXTJOIN(" · ",TRUE,'+','.join(checks)+'))')
    raw=[name,f'TEXTJOIN(" · ",TRUE,{C("ATRIBUTO NATURAL 1")},{C("ATRIBUTO NATURAL 2")})',
         C('VIDA INICIAL'),C('VIDA POR NÍVEL'),C('PE POR NÍVEL'),C('PERÍCIA FIXA 1'),C('PERÍCIA FIXA 2'),f'VALUE(SUBSTITUTE({C("DADO DE VIDA")},"d",""))',C('TROCA PERÍCIAS POR ARMA'),C('TREINO DE ARMA')]
    row=len(paths)+2
    for col,v in enumerate(raw,13): d(f'{ix._letras(col)}{row}',f'=IF(AND({name}<>"",$K$2=""),{v},"")')
    for i,k in enumerate(CAM_FIELDS[10:],67): d(f'{ix._letras(i)}{row}',f'=IF($M${row}="","",{C(k)})')
    for r in range(2,len(paths)+3): d(f'AS{r}',f'=$M{r}')
    path_table=rg(13,row,width=8);tr['caminhos']=path_table
    # A trail base inherits only mechanical automation. Its prose remains its own.
    for r,(n,p) in enumerate(trails,2):
        for col,v in enumerate([n,p,n],27): d(f'{ix._letras(col)}{r}',v)
    trail=tr['trilha'];T=lambda k:ref(trail['campos'][k],'CONFIGURAÇÃO')
    tname=ref(trail['nome'],'CONFIGURAÇÃO');trow=len(trails)+2
    d('K3',f'=IF({tname}="","",TEXTJOIN(" · ",TRUE,'
      f'IF(OR(TRIM({tname})<>{tname},COUNTIF($BB$2:$BB${len(trails)+1},{tname})>0),"Nome de Trilha inválido ou repetido",""),'
      f'IF(COUNTIF($AS$2:$AS$8,{T("CAMINHO")})=0,"Escolha um Caminho válido",""),'
      f'IF(ISLOGICAL({ref(trail["mestre_viu"],"CONFIGURAÇÃO")}),"","MESTRE VIU deve ser caixa de seleção"),'
      f'IF(COUNTIF($AU$2:$AU${len(trails)+2},{T("BASE DO LIVRO")})=0,"Escolha BASE DO LIVRO ou Nenhuma","")))')
    for col,v in enumerate([tname,T('CAMINHO'),T('BASE DO LIVRO')],27): d(f'{ix._letras(col)}{trow}',f'=IF(AND({tname}<>"",$K$3=""),{v},"")')
    idx=ix.indice(layout);pc=ref(idx['caminho'],'FICHA');pt=ref(idx['trilha'],'FICHA')
    d('AT2',fa.ESCOLHA_TRILHA)
    d('AT3',f'=IFERROR(FILTER($AA$2:$AA${trow},$AB$2:$AB${trow}={pc}),"")')
    d('K4',f'=IFERROR(IF(VLOOKUP({pt},$AA$2:$AC${trow},3,FALSE)="Nenhuma","",VLOOKUP({pt},$AA$2:$AC${trow},3,FALSE)),"")')
    d('K5',f'=IFERROR(VLOOKUP({pc},$M$2:$V$8,9,FALSE),"Não")')
    d('K6',f'=IFERROR(VLOOKUP({pc},$M$2:$V$8,10,FALSE),"")')
    d('K7',f'=IF(AND({pc}=$M$8,$M$8<>""),1,0)')
    d('K8',f'=IF(AND({pt}=$AA${trow},$AA${trow}<>""),1,0)')
    d('K9',f'=IFERROR(VLOOKUP({pc},$M$2:$T$8,8,FALSE),"")')
    # Progression is a live formula source; editing text needs no activation script.
    for typ,g,flag in [('Caminho',cam,'K7'),('Trilha',trail,'K8')]:
        for lv in g['niveis']:
            r=lv['nivel']+(1 if typ=='Caminho' else 31)
            for col,v in enumerate([typ,lv['nivel']],57):d(f'{ix._letras(col)}{r}',v)
            d(f'BG{r}',f'=IF(AND(${flag[0]}${flag[1:]}=1,{ref(lv["nome"],"CONFIGURAÇÃO")}<>""),{ref(lv["nome"],"CONFIGURAÇÃO")},"")' if lv['nome'] else '=""')
            d(f'BH{r}',f'=IF(OR(BG{r}="",{ref(lv["texto"],"CONFIGURAÇÃO")}=""),"",{ref(lv["texto"],"CONFIGURAÇÃO")})' if lv['texto'] else '=""')
    d('CB1','último nome automático · grupo 7')
    d('CC1','último texto automático · grupo 7')
    # Geometry and formulas both consume the same field map.
    desenha(layout,tr,put)
    ficha(layout,tr,put,idx)
    replacements={'DADOS!$N$5:$U$10':path_table,
                  'DADOS!$AM$5:$AM$11':rg(45,8),
                  'DADOS!$AP$5:$AP$25':rg(46,trow+2),
                  'DADOS_INVOC!$CC$2:$CC$24':rg(33,len(cat['pericias'])+cap.PERICIAS+1),
                  'DADOS_INVOC!$CC$2:$CD$24':skills,
                  'DADOS_INVOC!$CH$2:$CH$12':rg(36,len(cat['oficios'])+cap.OFICIOS+1),
                  'DADOS!$B$4:$B$26':rg(33,len(cat['pericias'])+cap.PERICIAS+1)}
    # Extend the existing 3a pools (Origem skills / office) without changing cards.
    pools=custom.listas(); cols={k:78+i for i,k in enumerate(pools)}
    replacements[custom.faixa(cols['pericias'],160)]=rg(33,len(cat['pericias'])+cap.PERICIAS+1)
    replacements[custom.faixa(cols['oficios'],160)]=rg(36,office_none)
    for a in layout['abas']:
        if a['nome']==NOME: continue
        local=dict(replacements)
        if a['nome']=='DADOS_INVOC':local.update({'$CC$2:$CD$24':skills,'$CC$2:$CC$24':rg(33,len(cat['pericias'])+cap.PERICIAS+1),'$CH$2:$CH$12':rg(36,len(cat['oficios'])+cap.OFICIOS+1)})
        for x in list(a['celulas']):
            if not isinstance(x[1],str) or not x[1].startswith('='):continue
            v=x[1]
            for old,new in local.items():v=v.replace(old,new)
            # Only mechanical branch comparisons use the inherited trail identity.
            if a['nome']=='DADOS_INVOC' and any(q(n) in v for n in ['Invocação Principal','Múltiplas Invocações','Parceria']):v=v.replace('$DB$4',ref('K4'))
            put(a['nome'],x[0],v)
        for menu in a.get('menus',[]):
            for old,new in local.items():menu['formula']=menu['formula'].replace(old,new)
    efeitos(layout,tr,put,fiv)
    # The variant die and the permission for trading skills are live lookups.
    put('DADOS_CONFIG','AI10','='+ref('K9'))
    v=cells['DADOS']['AK18'][1]
    prefix='OR(FICHA!$D$11="Guia",FICHA!$D$11="Emanador",FICHA!$D$11="Evocador")'
    if prefix not in v:raise ValueError('conta de troca de perícia mudou; rever integração')
    put('DADOS','AK18',v.replace(prefix,ref('K5')+'="Sim"'))
    summary=idx.get('armas')
    # Existing summary is uniquely located by its text, not by an exported index.
    for c,x in cells['FICHA'].items():
        if isinstance(x[1],str) and 'Treinado em Todas as Armas' in x[1]:
            put('FICHA',c,f'=IF({ref("K7")}=1,IF({ref("K6")}="Todas","Treinado em Todas as Armas","Treinado em "&TEXTJOIN(", ",TRUE,{cats})),{x[1][1:]})')
    # Custom names are literal in exact lookups throughout all consumers.
    from custom_pecas import buscas_literais
    targets=set()
    for table in (skills, offices):
        owner,address=table.rsplit('!',1)
        targets.add((owner.strip("'"),address.replace('$','')))
    for a in layout['abas']:
        for item in list(a['celulas']):
            changed=buscas_literais(item[1],a['nome'],targets)
            if changed!=item[1]: put(a['nome'],item[0],changed)
    data['linhas']=max(ix._lc(c[0])[0] for c in data['celulas'])
    tr['put']=put
    return tr


def desenha(layout,tr,put):
    a=ix._aba(layout,'CONFIGURAÇÃO')
    styles={x[0]:x[2] for x in a['celulas']}
    st=dict(fundo=styles['A1'],secao=styles['B9'],rotulo=styles['B10'],entrada=styles['C11'],caixa=styles['B11'],nota=styles['B5'])
    wrap=deepcopy(layout['estilos'][st['entrada']]);wrap[3]=['left','top',True,0]
    if wrap not in layout['estilos']:layout['estilos'].append(wrap)
    st['efeito']=layout['estilos'].index(wrap)
    a['linhas']=curto(CURTOS)['inicio']+12
    for r in range(733,a['linhas']+1):
        for c in range(1,17):put(a['nome'],f'{ix._letras(c)}{r}',None,st['fundo'])
    def box(r,c,v=None,er=None,ec=None,kind='entrada',note=None):
        cell=f'{ix._letras(c)}{r}';end=f'{ix._letras(ec or c)}{er or r}'
        put(a['nome'],cell,v,st[kind])
        if cell!=end:a['mescladas'].append(cell+':'+end)
        a['notas'][cell]=note or ('Campo do molde aprovado. Use o menu quando disponível; números do Caminho usam as mesmas contas do livro. MESTRE VIU é apenas um lembrete.' if kind not in ['secao','nota'] else 'Conteúdo custom da parte 3b. Aprovação ocorre pelo bot no chat.')
    def menu(c,source):
        a['menus'].append(dict(tipo='list',formula=source,onde=c,vazio_ok=True,mostra_seta=True,estrito=True))
        a.setdefault('menus_estritos',[]).append(c)
    def check(c):put(a['nome'],c,False,st['caixa'])
    for g in [tr['caminho'],tr['trilha']]:
        c=g['col'];r=g['inicio'];L=ix._letras
        box(r,c,g['tipo'].upper()+' · CUSTOM',ec=c+5,kind='secao')
        box(r+1,c,'TIPO',ec=c+3,kind='rotulo');box(r+2,c,g['tipo'],ec=c+3)
        box(r+1,c+4,'MESTRE VIU',ec=c+5,kind='rotulo',note='Lembrete do jogador; o bot aprova no chat.')
        box(r+2,c+4,False,ec=c+5,kind='caixa')
        box(r+3,c,'NOME',ec=c+5,kind='rotulo');box(r+4,c,ec=c+5)
        for i,(label,addr) in enumerate(g['campos'].items()):
            rr=r+5+i
            box(rr,c,label,ec=c+2,kind='rotulo');box(rr,c+3,ec=c+5)
            source=(rg(41,7) if label=='DADO DE VIDA' else rg(40,6) if label.startswith('ATRIBUTO') else tr['pericias'].split(':')[0]+':$AG$'+tr['pericias'].rsplit('$',1)[1] if label.startswith('PERÍCIA') else rg(42,3) if label.startswith('TROCA') else rg(43,3) if label=='TREINO DE ARMA' else rg(44,14) if label.startswith('CATEGORIA') else rg(45,8) if label=='CAMINHO' else rg(47,22) if label=='BASE DO LIVRO' else None)
            if source:menu(addr,source)
            if label in ['TREINO DE ARMA','TROCA PERÍCIAS POR ARMA']:put(a['nome'],addr,'Todas' if label=='TREINO DE ARMA' else 'Não')
            if label=='BASE DO LIVRO':
                put(a['nome'],addr,'Nenhuma')
                a['notas'][addr]='Opcional: herda as automações da Trilha do livro. Nenhuma cria do zero. Texto próprio não é convertido em regra.'
        box(r+31,c,'OBSERVAÇÕES',ec=c+5,kind='rotulo')
        box(r+32,c,er=r+34,ec=c+5,kind='efeito')
        box(r+36,c,'=IF('+ref('K2' if c==2 else 'K3')+'="","Livro + custom nos menus.","⚠ "&'+ref('K2' if c==2 else 'K3')+')',er=r+37,ec=c+5,kind='nota')
        box(r+39,c,'HABILIDADES POR NÍVEL · '+g['tipo'].upper(),ec=c+5,kind='secao')
        box(r+40,c,'Mesmos níveis do livro · preenche o grupo 7 da FICHA.',ec=c+5,kind='nota')
        for lv in g['niveis']:
            if not lv['nome']:continue
            rr=ix._lc(lv['nome'])[0]
            box(rr,c,lv['nivel'],kind='rotulo');box(rr,c+1,ec=c+5)
            box(rr+1,c,er=rr+2,ec=c+5,kind='efeito',note='Texto integral da habilidade. Campo vazio não concede habilidade; nenhum texto é interpretado como cálculo.')
    # Keep the approved cards; compact the unused spacer before the catalog.
    a.setdefault('grupos',{}).setdefault('linhas',[]).append([INICIO+56,INI_CURTOS-3,True])
    for g in tr['curtos']:
        c=g['col'];r=g['inicio'];n=g['n']
        box(r,c,f'{g["categoria"].upper()} {g["indice"]} · CUSTOM',ec=c+5,kind='secao')
        box(r+1,c,'TIPO',ec=c+3,kind='rotulo');box(r+2,c,g['categoria'],ec=c+3)
        menu(g['tipo'],rg(39,2 if g['categoria']=='Perícia' else 3, start=2 if g['categoria']=='Perícia' else 3))
        box(r+1,c+4,'MESTRE VIU',ec=c+5,kind='rotulo');box(r+2,c+4,False,ec=c+5,kind='caixa')
        box(r+3,c,'NOME',ec=c+5,kind='rotulo');box(r+4,c,ec=c+5)
        box(r+5,c,f'=IF({g["tipo"]}="Ofício","ATRIBUTO PADRÃO","ATRIBUTO FIXO")',ec=c+2,kind='rotulo')
        box(r+5,c+3,ec=c+5);menu(g['atributo'],rg(40,6))
        box(r+6,c,'DESCRIÇÃO',ec=c+5,kind='rotulo');box(r+7,c,er=r+9,ec=c+5,kind='efeito')
        box(r+11,c,f'=IF({ref("G"+str(n+1))}="","Usa os treinos e especializações existentes.","⚠ "&{ref("G"+str(n+1))})',er=r+12,ec=c+5,kind='nota')
    a['linhas_alt'] += [[r,18.75] for r in range(INICIO,a['linhas']+1)]
    a.setdefault('sem_trava',[])
    a['sem_trava'] += [c for _,c in tr['entradas'] if c]
    # Long descriptions share rows across the two cards. Resize the pair as a
    # unit so editing one side cannot clip the other; use the existing mechanism.
    def width(c):
        return sum(next((w for lo,hi,w in a['colunas_larg'] if lo<=i<=hi),4)*8-1
                   for i in range(c,c+6))-12
    def stretch(cards,key,rows):
        sources=[g[key] for g in cards]
        a.setdefault('esticam',[]).append(dict(gatilhos=sources,aba=a['nome'],
            textos=[[width(g['col']),[g[key]],ix._lc(g[key])[0],rows,0] for g in cards]))
    stretch([tr['caminho'],tr['trilha']],'efeito',3)
    for i in range(5):
        cards=[dict(col=g['col'],texto=lv['texto']) for g in [tr['caminho'],tr['trilha']]
               for lv in g['niveis'] if lv['nome'] and ix._lc(lv['nome'])[0]==INICIO+41+i*3]
        stretch(cards,'texto',2)
    for n in range(0,CURTOS,2):stretch(tr['curtos'][n:n+2],'efeito',3)


def ficha(layout,tr,put,idx):
    """Two columns of skills/offices; abilities reuse section 7. Budgets unchanged."""
    a=ix._aba(layout,'FICHA')
    styles={x[0]:x[2] for x in a['celulas']}
    st=dict(secao=styles['G76'],rotulo=styles['D79'],entrada=styles['F80'],caixa=styles['D80'],nota=styles['F80'])
    # New FICHA panels use the FICHA's palette roles; only CONFIGURAÇÃO is fixed.
    for key in ['rotulo','entrada','nota']:
        e=deepcopy(layout['estilos'][st[key]])
        e[0]=['Oswald' if key=='rotulo' else 'Roboto',10,e[0][2],False,False]
        e[3]=['center' if key=='rotulo' else 'left','center',True,0]
        if e not in layout['estilos']:layout['estilos'].append(e)
        st[key]=layout['estilos'].index(e)
    e=deepcopy(layout['estilos'][st['entrada']]);e[3]=['left','top',True,0]
    if e not in layout['estilos']:layout['estilos'].append(e)
    st['efeito']=layout['estilos'].index(e)
    anterior=a['linhas']; start=anterior+4; a['linhas']=start+25
    # Continue both the spine fill and B's right border, including the gap.
    # A1 is only the fill: copying it into B used to erase the divider.
    for r in range(anterior+1,a['linhas']+1):
        for c in ['A','B']:put('FICHA',c+str(r),None,styles[c+str(anterior)])
    def box(c,v=None,end=None,kind='entrada'):
        put('FICHA',c,v,st[kind])
        if end:a['mescladas'].append(c+':'+end)
    def menu(c,source):a['menus'].append(dict(tipo='list',formula=source,onde=c,vazio_ok=True,mostra_seta=True,estrito=True))
    attrs={n:ref(idx['atr_'+n],'FICHA') for n in ATRIBUTOS}
    paineis=[(4,'Perícia',12,48,0,start),(24,'Perícia',11,48,12,start),
             (4,'Ofício',6,49,0,start+16),(24,'Ofício',5,49,6,start+16)]
    nomes={typ:[ref(f'{ix._letras(col+2)}{r+2}', 'FICHA')+':'+ref(f'{ix._letras(col+2)}{r+1+total}', 'FICHA').split('!')[1]
                for col,t,total,pool,offset,r in paineis if t==typ]
           for typ in ['Perícia','Ofício']}
    for col,typ,total,pool,offset,r in paineis:
        L=ix._letras
        titulo=typ.upper()+' CUSTOM · '+str(offset+1)+'–'+str(offset+total)
        box(f'{L(col)}{r}',titulo,f'{L(col+17)}{r}',kind='secao')
        for c,label,width in [(col,'T',1),(col+1,'E',1),(col+2,'NOME',8),(col+10,'ATRIBUTO',4),(col+14,'TOTAL',2),(col+16,'BÔNUS',2)]:
            box(f'{L(c)}{r+1}',label,f'{L(c+width-1)}{r+1}' if width>1 else None,'rotulo')
        for i in range(total):
            rr=r+2+i;train=f'{L(col)}{rr}';spec=f'{L(col+1)}{rr}';name=f'{L(col+2)}{rr}';at=f'{L(col+10)}{rr}';res=f'{L(col+14)}{rr}';bonus=f'{L(col+16)}{rr}'
            box(train,False,kind='caixa');box(spec,False,kind='caixa');box(name,end=f'{L(col+9)}{rr}')
            menu(name,rg(pool,(cap.PERICIAS if typ=='Perícia' else cap.OFICIOS)+1))
            source=tr['pericias'] if typ=='Perícia' else tr['oficios']
            attr=f'IFERROR(VLOOKUP({name},{source},2,FALSE),"")'
            box(at,'='+attr,f'{L(col+13)}{rr}')
            # Office attribute stays manually overrideable, like the original office rows.
            if typ=='Ofício':menu(at,rg(40,6));a.setdefault('livres',[]).append(at)
            value='SWITCH('+at+','+','.join(q(n)+','+v for n,v in attrs.items())+',NA())'
            rn=ref(name,'FICHA')
            # Count across both columns, not only the current half.
            unique='('+ '+'.join(f'COUNTIF({area},{criterio(rn)})' for area in nomes[typ])+')=1'
            valid=f'AND({rn}<>"",COUNTIF({rg(pool,(cap.PERICIAS if typ=='Perícia' else cap.OFICIOS)+1)},{criterio(rn)})=1,{unique})'
            box(res,f'=IF({name}="","",IF({valid},{value}+IF({spec},{ref(idx["maestria"],"FICHA")}+INT({ref(idx["maestria"],"FICHA")}/2),IF({train},{ref(idx["maestria"],"FICHA")},0))+IFERROR(VALUE({bonus}&""),0),NA()))',f'{L(col+15)}{rr}')
            box(bonus,end=f'{L(col+17)}{rr}')
            tr['linhas_ficha'].append(dict(tipo=typ,n=offset+i+1,treino=train,especializacao=spec,nome=name,atributo=at,resultado=res,bonus=bonus,valido=valid))
            if typ=='Perícia':put(NOME,f'BD{offset+i+2}',f'=ADDRESS(ROW({ref(name,"FICHA")}),COLUMN({ref(name,"FICHA")}),4)')
            # Hidden counters count only one occurrence of a valid definition.
            dr=2+offset+i+(0 if typ=='Perícia' else 23)
            for dc,expr in [('BK',train),('BL',spec)]:
                put(NOME,f'{dc}{dr}',f'=IF({valid},N({ref(expr,"FICHA")}),0)')
    # Append to existing totals; no additional granted choices.
    for c,area in [('AK13','BK2:BK24'),('AK14','BK25:BK35'),('AK15','BL2:BL35')]:
        old=next(v[1] for v in ix._aba(layout,'DADOS')['celulas'] if v[0]==c)
        put('DADOS',c,old+'+SUM(\''+NOME+'\'!'+area+')')
    # All abilities use the original section 7 cards, populated by Codigo.gs.
    a['linhas_alt'] += [[r,18.75] for r in range(start,a['linhas']+1)]


def efeitos(layout,tr,put,fiv):
    """Custom skills/offices accept the same somar/trocar-por rules as book rows."""
    import configuracao as cfg
    h=ix._aba(layout,cfg.DADOS)
    rs=lambda col:f"'CONFIGURAÇÃO'!${col}$11:${col}$40"
    cells={v[0]:v[1] for v in ix._aba(layout,'FICHA')['celulas']}
    for n,g in enumerate(tr['linhas_ficha'],54):
        name=ref(g['nome'],'FICHA');target=q(g['tipo']+' · ')
        base=cells[g['resultado']]
        original=cfg.qualifica(base,'FICHA')
        values={'A':f'=IF({g["valido"]},{target}&{name},"")',
                'B':f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"somar")',
                'C':f'=COUNTIFS({rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"trocar por")',
                'D':f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"trocar por")',
                'E':f'=IF(COUNTIFS({rs("B")},"<>FALSE",{rs("C")},A{n},$L$2:$L$31,0)>0,"Entrada inválida",IF(C{n}>1,"Conflito: mais de uma troca",""))',
                'F':original,'G':original,'H':'='+ref(g['resultado'],'FICHA')}
        for col,v in values.items():put(cfg.DADOS,f'{col}{n}',v)
        put('FICHA',g['resultado'],f'=IF({name}="","",{cfg.envolve(base,n)[1:]})')
        g['efeito_linha']=n
    tr['efeitos_invocacoes']=[]
    for n,key in [(88,'teto de ativas'),(89,'famílias da trilha')]:
        coord=fiv['H'][key].split('!')[-1].replace('$','')
        old=next(v[1] for v in ix._aba(layout,'DADOS_INVOC')['celulas'] if v[0]==coord)
        values={'A':'Invocações · '+key,'B':f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"somar")',
                'C':f'=COUNTIFS({rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"trocar por")',
                'D':f'=SUMIFS({rs("E")},{rs("B")},TRUE,{rs("C")},A{n},{rs("D")},"trocar por")',
                'E':f'=IF(COUNTIFS({rs("B")},"<>FALSE",{rs("C")},A{n},$L$2:$L$31,0)>0,"Entrada inválida",IF(C{n}>1,"Conflito: mais de uma troca",""))',
                'F':cfg.qualifica(old,'DADOS_INVOC'),'G':cfg.qualifica(old,'DADOS_INVOC'),'H':'='+ref(coord,'DADOS_INVOC')}
        for col,v in values.items():put(cfg.DADOS,f'{col}{n}',v)
        put('DADOS_INVOC',coord,cfg.envolve(old,n))
        tr['efeitos_invocacoes'].append((n,key))
    h['linhas']=max(h['linhas'],89)
    # The old 50 targets retain their exact row numbers.
    for x in list(h['celulas']):
        if isinstance(x[1],str) and x[1].startswith('='):
            v=x[1].replace('$A$2:$A$51','$A$2:$A$89').replace('C2:C51','C2:C89')
            put(cfg.DADOS,x[0],v)
    for m in ix._aba(layout,'CONFIGURAÇÃO')['menus']:
        if m['formula']=='DADOS_CONFIG!$A$2:$A$51':m['formula']='DADOS_CONFIG!$A$2:$A$89'


def exporta(tr):
    out=[]
    for key,c in tr['entradas']:
        if not c:
            # Keep the v6 keys; unsupported book milestones have no input.
            out.append([key,'=""','','configuração'])
            continue
        r=ref(c,'CONFIGURAÇÃO')
        formula=f'=N({r})&""' if key.endswith('.mestre_viu') else f'=IF(ISBLANK({r}),"",{r}&"")'
        out.append([key,formula,r.replace('$',''),'configuração'])
    for g in tr['curtos']:
        rr=ref('G'+str(g['n']+1))
        out.append([f'aviso.custom.{"pericia" if g["categoria"] == "Perícia" else "oficio"}.{g["indice"]}',f'=IF({rr}="","","⚠ "&{rr})',NOME+'!G'+str(g['n']+1),'aviso'])
    for key,cell in [('caminho','K2'),('trilha','K3')]:
        rr=ref(cell)
        out.append(['aviso.custom.'+key,f'=IF({rr}="","","⚠ "&{rr})',NOME+'!'+cell,'aviso'])
    for g in tr['linhas_ficha']:
        typ='pericia' if g['tipo']=='Perícia' else 'oficio'
        for key in ['nome','treino','especializacao','atributo','resultado','bonus']:
            c=ref(g[key],'FICHA')
            formula=f'=N({c})&""' if key in ['treino','especializacao'] else f'=IF(ISBLANK({c}),"",{c}&"")'
            out.append([f'personagem.{typ}_custom.{g["n"]}.{key}',formula,c.replace('$',''),'entrada' if key!='resultado' else 'resultado'])
        n=g['efeito_linha']
        out.append([f'aviso.efeito_caixa.{typ}_custom.{g["n"]}',f'=DADOS_CONFIG!$E${n}&""',f'DADOS_CONFIG!E{n}','aviso'])
        name=ref(g['nome'],'FICHA');at=ref(g['atributo'],'FICHA')
        out.append([f'aviso.personagem.{typ}_custom.{g["n"]}',
                    f'=IF({name}="","",IF(AND({g["valido"]},COUNTIF({rg(40,6)},{at})=1),"","⚠ Custom inválido ou repetido; confira NOME e ATRIBUTO"))',
                    name.replace('$',''),'aviso'])
    from analise import chave
    for n,key in tr['efeitos_invocacoes']:
        out.append(['aviso.efeito_caixa.invocacoes.'+chave(key),f'=DADOS_CONFIG!$E${n}&""',f'DADOS_CONFIG!E{n}','aviso'])
    return out
