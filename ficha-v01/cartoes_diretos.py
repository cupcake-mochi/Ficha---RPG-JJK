"""Cartões R53 editáveis no lugar. Montagens guarda somente versões ocultas.

A expansão das modalidades compactas é uma transformação de coordenadas:
nenhuma ficha é reconstruída durante a migração nativa.
"""
import copy,json,re
from openpyxl.utils.cell import coordinate_to_tuple,range_boundaries,get_column_letter as L
import montagens_r53 as R
import modelo as M


def expandir(layout,tr):
    import extensoes_custom as ex
    inserts=[]
    for g in tr['contextos']:
        if g['aba']=='INVOCAÇÕES' and g['id'].endswith('.liberacao.1'):
            inserts.append((coordinate_to_tuple(g['cel']['nome'])[0]+8,10))
        if g['aba']=='INVOCAÇÕES' and g['id'].endswith('.maxima.1'):
            inserts.append((coordinate_to_tuple(g['cel']['nome'])[0]+7,10))
    inserts=sorted(set(inserts));tr['insercoes_diretas']={'INVOCAÇÕES':inserts}
    original=ex.INSERCOES
    try:
        ex.INSERCOES=tr['insercoes_diretas'];ex.formula.cache_clear()
        ex.deslocar(layout)
        def move(v,owner):
            if isinstance(v,str):
                return ex.coord(owner,v) if re.fullmatch(r'[A-Z]+\d+',v) else ex.formula(v,owner)
            if isinstance(v,list):return [move(x,owner) for x in v]
            if isinstance(v,dict):return {k:move(x,owner) for k,x in v.items()}
            return v
        for a in layout['abas']:
            if a.get('familias_custom'):a['familias_custom']=move(a['familias_custom'],a['nome'])
        for g in tr['contextos']:
            owner=g['aba'];g['cel']=move(g['cel'],owner)
            for k in ['funcao','abrir_editor','nivel','classe_maxima','dados_zero','cd','requisito']:
                if k in g:g[k]=move(g[k],owner)
            if 'linha_funcao' in g:g['linha_funcao']=ex.linha(owner,g['linha_funcao'])
            if 'area_editor' in g:
                a=g['area_editor'];a[0]=ex.linha(owner,a[0]);a[2]=ex.linha(owner,a[2])
            tr['formulas'][g['id']]={ex.coord(owner,k):ex.formula(v,owner) for k,v in tr['formulas'][g['id']].items()}
        for key in ['antes','depois']:
            tr[key]={n:{ex.coord(n,k):ex.formula(v,n) for k,v in reg.items()} for n,reg in tr[key].items()}
    finally:
        ex.INSERCOES=original;ex.formula.cache_clear()


def aplica(layout,tr):
    if tr.get('direto'):raise ValueError('Cartões diretos já aplicados')
    # Compatibilidade com um modelo intermediário exportado, sem criar painéis.
    abas={a['nome']:a for a in layout['abas']}
    for owner,p in tr.get('paineis',{}).items():
        a=abas[owner];c=p['coluna']
        a['celulas']=[v for v in a['celulas'] if coordinate_to_tuple(v[0])[1]<c]
        a['mescladas']=[v for v in a['mescladas'] if range_boundaries(v)[0]<c]
        a['menus']=[v for v in a['menus'] if all(range_boundaries(x)[0]<c for x in v['onde'].split())]
        a['notas']={k:v for k,v in a.get('notas',{}).items() if coordinate_to_tuple(k)[1]<c}
        a['colunas']=c-3;a['colunas_larg']=[v for v in a['colunas_larg'] if v[0]<c]
        a['grupos']['colunas']=[v for v in a['grupos']['colunas'] if v[0]<c]
    tr['paineis']={};tr.pop('compactos_checkbox',None)
    expandir(layout,tr)
    cells={n:{v[0]:v for v in a['celulas']} for n,a in abas.items()}
    originals={n:{p:v[1] for p,v in cm.items()} for n,cm in cells.items()}
    old_contexts={g['id']:copy.deepcopy(g['cel']) for g in tr['contextos']}

    styles={}
    src=cells['FICHA AMALDIÇOADA']
    for k,pos,bg in [('label','D73','492D4D'),('input','E73','311E33'),('result','E70','251727')]:
        style=copy.deepcopy(layout['estilos'][src[pos][2]])
        style[0]=['Roboto',9,'FBE4EF',k=='label',False];style[1]=bg
        style[2]={edge:['thin','B377BB'] for edge in ['left','right','top','bottom']}
        style[3]=['center','center',True,0];style[4]='General'
        layout['estilos'].append(style);styles[k]=len(layout['estilos'])-1
    tr['areas_diretas']=[]
    for g in tr['contextos']:
        owner=g['aba'];a=abas[owner];cm=cells[owner];cel=g['cel'];row=g['linha'];out=tr['formulas'][g['id']]
        g.pop('abrir_editor',None);g['entradas_diretas']={};g['menus_diretos']={}
        g['fixa']=g['modo'] in ['Classe 0','Básica','Técnica Máxima','Máxima de entidade']
        def data(k):return R.ref(R.DADOS,'$'+tr['colunas'][k]+'$'+str(row))
        def put(pos,val,kind=None,end=None,note=None):
            if pos not in cm:cm[pos]=[pos,val,styles[kind or 'input']];a['celulas'].append(cm[pos])
            else:
                cm[pos][1]=val
                if kind:cm[pos][2]=styles[kind]
            if end and pos!=end:a['mescladas'].append(pos+':'+end)
            if note:a.setdefault('notas',{})[pos]=note
            if isinstance(val,str) and val.startswith('='):out[pos]=val
            else:out.pop(pos,None)
            tr['depois'].setdefault(owner,{})[pos]=val
            return pos
        def clear(r,c,rr,cc):
            overlaps=lambda x:not (range_boundaries(x)[2]<c or range_boundaries(x)[0]>cc or range_boundaries(x)[3]<r or range_boundaries(x)[1]>rr)
            a['mescladas']=[x for x in a['mescladas'] if not overlaps(x)]
            for y in range(r,rr+1):
                for x in range(c,cc+1):
                    pos=L(x)+str(y);a.setdefault('notas',{}).pop(pos,None);put(pos,None,'input')
            tr['areas_diretas'].append(dict(id=g['id'],aba=owner,faixa=f'{L(c)}{r}:{L(cc)}{rr}'))
        def box(r,c,cc,value,kind='input',note=None):return put(L(c)+str(r),value,kind,L(cc)+str(r),note)
        def inp(k,r,c,cc,kind=None,default=None):
            kind=kind or dict((x,z) for x,_,z in R.CAMPOS)[k]
            v=R.DEFAULTS_EDITOR.get(k,'') if default is None else default
            pos=box(r,c,cc,v,'input');g['entradas_diretas'][k]=pos
            if kind=='bool':m=dict(tipo='bool',formula='',vazio_ok=False,mostra_seta=False)
            elif kind=='inteiro':m=dict(tipo='custom',formula=f'AND(ISNUMBER({pos}),{pos}>=0,INT({pos})={pos})',vazio_ok=False,mostra_seta=False)
            else:m=dict(tipo='list',formula=tr['menus_editor'][kind],vazio_ok=True,mostra_seta=True,estrito=True)
            m['onde']=pos;g['menus_diretos'][k]=m
            a.setdefault('notas',{})[pos]=('Marque quando o feitiço afetar exclusivamente quem o executa. Deixe desmarcado se puder afetar outras criaturas. Na Forma Toque, usar somente em si não concede devolução de pontos. Descreva alvos e detalhes em COMO É.' if k=='pessoal' else 'Escolha neste cartão. A Classe selecionada conserva suas próprias escolhas.')
            return pos
        def functions(r,c):
            box(r,c,c,'FUNÇÃO','label');box(r+1,c,c,'Usar' if g['fixa'] else ('=IF('+data('zero')+',"Usar (0/1)","Pontos")' if g.get('extra') else 'Pontos'),'label');box(r+2,c,c,'Resultado','label')
            for i,(label,key,start,end) in enumerate([('DANO','dano',c+1,c+1),('CURA','cura',c+2,c+2),('PV TEMP.','vt',c+3,c+4)],1):
                gate='FALSE' if (key!='dano' and g['modo'] in ['Classe 0','Básica']) or (key=='cura' and 'Liberação' in g['modo']) or (key=='vt' and 'Máxima' in g['modo']) else 'TRUE' if key=='dano' else f'{data("fam_Amparo")}<>"Fechada"'
                if g.get('extra') and key!='dano':gate=f'AND({data("classe")}<>0,{gate})'
                g.setdefault('portas',{})[key]=gate
                box(r,start,end,f'=IF({gate},"{label}","—")','label')
                pos=inp('usar_'+key if g['fixa'] else 'pontos'+str(i),r+1,start,end,'bool' if g['fixa'] else 'inteiro',False if g['fixa'] else 0)
                g.setdefault('funcoes_diretas',{})[key]=pos
                if not g['fixa']:
                    v=pos
                    gate_indirect=re.sub(r"'DADOS_R53'!([A-Z$0-9]+)",lambda m:'INDIRECT("\'DADOS_R53\'!'+m[1]+'")',gate)
                    g['menus_diretos']['pontos'+str(i)]['formula']=f'IF({gate_indirect},AND(ISNUMBER({v}),{v}>=0,INT({v})={v}),{v}="—")'

                a['notas'][pos]=('Marque somente uma função. Esta modalidade tem dados próprios.' if g['fixa'] else 'Distribua pontos inteiros. Os pontos usados aqui deixam de estar disponíveis nas outras funções.')+' Cura/PV temporários ficam indisponíveis com Amparo Fechada. Defina alvos, resolução e detalhes em COMO É.'
                result=data('dano_resultado') if key=='dano' else data('cura_d8')+'&"d8"' if key=='cura' else data('vida_temporaria')+'&" PV"'
                box(r+2,start,end,f'=IF({gate},IF({data("nome")}<>"",{result},""),"—")','result')
        normal='linha_funcao' in g and g.get('modo') not in ['Liberação de entidade','Máxima de entidade']
        if normal:
            r,c=g['linha_funcao'],g['coluna']
            # Preserve the description anchor, trim one row for Forma.
            desc=cel['como'];merge=next(v for v in a['mescladas'] if v.startswith(desc+':'))
            a['mescladas'].remove(merge);end=L(c+4)+str(r-2)
            if desc!=end:a['mescladas'].append(desc+':'+end)
            clear(r-1,c,r+2,c+4)
            box(r-1,c,c,'FORMA','label');cel['forma']=inp('forma',r-1,c+1,c+2)
            box(r-1,c+3,c+3,'SÓ EM SI','label');inp('pessoal',r-1,c+4,c+4,'bool',False)
            functions(r,c);cel['dano']=L(c+1)+str(r+2)
            # Existing pieces stay where the player already finds them.
            for k,prefix in [('mel','m'),('res','r')]:
                for i,pos in enumerate(cel.get(k,[]),1):
                    rr,cc=coordinate_to_tuple(pos);merge=next((v for v in a['mescladas'] if v.startswith(pos+':')),pos)
                    endcol=range_boundaries(merge)[2];put(pos,'')
                    g['entradas_diretas'][prefix+str(i)]=pos
                    g['menus_diretos'][prefix+str(i)]=dict(onde=pos,tipo='list',formula=tr['menus_editor']['melhoria' if k=='mel' else 'restricao'],vazio_ok=True,mostra_seta=True,estrito=True)
            footer=coordinate_to_tuple(cel['ampliar'])[0];clear(footer,c,footer+1,c+4)
            box(footer,c,c,'CONTROLE','label');inp('controle',footer,c+1,c+3)
            fragil=inp('fragil_pago',footer,c+4,c+4,'inteiro',0)
            ink=copy.deepcopy(layout['estilos'][cm[fragil][2]]);ink[4]='"Frágil: "0'
            layout['estilos'].append(ink);cm[fragil][2]=len(layout['estilos'])-1
            a['notas'][L(c+4)+str(footer)]='Frágil: informe só os pontos pagos em Melhorias que podem ser interrompidas. Se não usa Frágil, deixe 0.'
            box(footer+1,c,c+4,f'=IF({data("nome")}="","",TEXTJOIN(" · ",TRUE,{data("acao")},{data("pe")}&" PE",{data("alcance_ofensivo")},{data("area")}))','result')
            cel['execucao_resumo']=L(c)+str(footer+1);cel.pop('ampliar',None)
            for stale in ['pe','resolve','alcance','acao','tdano','rmenu']:cel.pop(stale,None)
            # Old entity action/damage-type rows now hold a useful summary only.
            if owner=='INVOCAÇÕES':
                clear(r+3,c,r+3,c+4)
                box(r+3,c,c+4,f'=IF({data("nome")}="","","Dano/Cura: 1 ponto = 1d8 · PV temp.: 1 ponto = 3 PV")','result')
            put(cel['conta'],f'=IF({data("nome")}="","","Saldo "&{data("saldo")}&" · Distribuídos "&({data("p_dano")}+{data("p_cura")}+{data("p_vt")})&" · Restam "&{data("sem_uso")})')
            a['linhas_alt'].append([coordinate_to_tuple(cel['conta'])[0],28])
            if cel.get('avisos'):put(cel['avisos'],f'=IF({data("nome")}<>"",{data("avisos")},"")')
            dr,dc=coordinate_to_tuple(desc);a['linhas_alt'] += [[dr,60],[r-1,22],[r,24],[r+1,24],[r+2,24],[footer,28],[footer+1,28]]
        elif g['modo']=='Classe 0':
            rr,_=coordinate_to_tuple(cel['nome']);clear(rr,16,rr,17)
            put('P'+str(rr),f'=IF({data("nome")}="","",IF({data("dano")},{data("dano_resultado")},"Utilidade"))','result')
            inp('usar_dano',rr,17,17,'bool',False);g['funcoes_diretas']={'dano':'Q'+str(rr)};g['portas']={'dano':'TRUE','cura':'FALSE','vt':'FALSE'}
            for k,pos in [('forma',cel['forma']),('m1',cel['mel'][0]),('r1',cel['res'][0])]:
                put(pos,'Projétil' if k=='forma' else '');g['entradas_diretas'][k]=pos
                g['menus_diretos'][k]=dict(onde=pos,tipo='list',formula=tr['menus_editor']['forma' if k=='forma' else 'melhoria' if k=='m1' else 'restricao'],vazio_ok=True,mostra_seta=True,estrito=True)
            put('P322','DANO','label');put('Q322','USAR','label')
        elif g['modo']=='Técnica Máxima':
            rr,cc=coordinate_to_tuple(cel['nome']);cel['como']=L(cc)+str(rr+6);clear(rr-1,12,rr+1,14)
            for key,col,label in [('dano',12,'DANO'),('cura',13,'CURA'),('vt',14,'PV TEMP.')]:
                gate='TRUE' if key=='dano' else f'{data("fam_Amparo")}<>"Fechada"' if key=='cura' else 'FALSE'
                g.setdefault('portas',{})[key]=gate
                box(rr-1,col,col,f'=IF({gate},"{label}","—")','label')
                inp('usar_'+key,rr,col,col,'bool',False);g.setdefault('funcoes_diretas',{})[key]=L(col)+str(rr)
                result=data('dano_resultado') if key=='dano' else data('cura_d8')+'&"d8"'
                box(rr+1,col,col,f'=IF({gate},IF({data("nome")}<>"",{result},""),"—")','result')
            for k,pos in [('forma',cel['forma'])]+[('m'+str(i),p) for i,p in enumerate(cel['mel'],1)]:
                put(pos,'Projétil' if k=='forma' else '');g['entradas_diretas'][k]=pos
                g['menus_diretos'][k]=dict(onde=pos,tipo='list',formula=tr['menus_editor']['forma' if k=='forma' else 'melhoria'],vazio_ok=True,mostra_seta=True,estrito=True)
        else:
            # Entity trumps receive complete cards in their existing section.
            start,c=coordinate_to_tuple(cel.get('classe',cel['nome']));end=start+17
            keep={cel['nome'],cel['como'],cel.get('classe')};saved={p:cm[p][1] for p in keep if p in cm}
            clear(start,c,end,c+4)
            if 'classe' in cel:
                box(start,c,c,saved.get(cel['classe'],3),'input');box(start,c+1,c+3,saved.get(cel['nome']))
            else:box(start,c,c+3,saved.get(cel['nome']))
            box(start,c+4,c+4,f'=IF({data("nome")}="","",{data("pe")}&" PE")','result')
            box(start+1,c,c+4,saved.get(cel['como']),note='COMO É: descreva efeitos, alvos, resolução, duração e detalhes das peças aqui.')
            a['mescladas'].remove(L(c)+str(start+1)+':'+L(c+4)+str(start+1));a['mescladas'].append(L(c)+str(start+1)+':'+L(c+4)+str(start+3))
            box(start+4,c,c,'FORMA','label');cel['forma']=inp('forma',start+4,c+1,c+2)
            box(start+4,c+3,c+3,'SÓ EM SI','label');inp('pessoal',start+4,c+4,c+4,'bool',False)
            functions(start+5,c);cel['dano']=L(c+1)+str(start+7);g['linha_funcao']=start+5;g['coluna']=c
            cel['mel']=[];cel['res']=[];cel['preco']=[];cel['dev']=[]
            for typ,prefix,offset,count in [('mel','m',8,4),('res','r',12,2)]:
                for i in range(1,count+1):
                    rr=start+offset+i-1;box(rr,c,c,('Melhoria ' if typ=='mel' else 'Restrição ')+str(i),'label')
                    cel[typ].append(inp(prefix+str(i),rr,c+1,c+2,'melhoria' if typ=='mel' else 'restricao'))
                    k=('pago_m' if typ=='mel' else 'retorno_r')+str(i);pos=box(rr,c+3,c+4,f'=IF({data("nome")}<>"",{data(k)},"")','result');cel['preco' if typ=='mel' else 'dev'].append(pos)
            cel['conta']=box(start+14,c,c+4,f'=IF({data("nome")}="","","Saldo "&{data("saldo")}&" · Sem uso "&{data("sem_uso")})','result')
            box(start+15,c,c,'FRÁGIL','label');inp('fragil_pago',start+15,c+1,c+1,'inteiro',0)
            box(start+15,c+2,c+4,f'=IF({data("nome")}="","",{data("acao")}&" · "&{data("pe")}&" PE")','result')
            cel['avisos']=box(start+16,c,c+4,f'=IF({data("nome")}="","",{data("avisos")})','result')
            a['mescladas'].remove(cel['avisos']+':'+L(c+4)+str(start+16));a['mescladas'].append(cel['avisos']+':'+L(c+4)+str(end))
            a['linhas_alt'] += [[start+1,50],[start+5,26],[start+6,24],[start+7,24],[start+14,30],[start+16,34],[start+17,34]]
        # All computed addresses removed by a region clear stay out of repair data.
        out={k:v for k,v in out.items() if k in cm and cm[k][1]==v};tr['formulas'][g['id']]=out
        allpoints=[]
        for value in cel.values():
            for p in value if isinstance(value,list) else [value]:
                if isinstance(p,str) and re.fullmatch('[A-Z]+[0-9]+',p):allpoints.append(coordinate_to_tuple(p))
        allpoints += [coordinate_to_tuple(p) for p in g['entradas_diretas'].values()]
        g['area_editor']=[min(r for r,c in allpoints),min(c for r,c in allpoints),max(r for r,c in allpoints)+1,max(c for r,c in allpoints)]
        a.setdefault('notas',{})[cel['nome']]='Edite neste cartão. A troca de Classe recupera as escolhas salvas daquela versão. Os detalhes do efeito ficam em COMO É.'
        if cel.get('como'):a['notas'][cel['como']]='Descreva aqui os efeitos, alvos, tipo de dano, resolução (ataque/TR), duração e detalhes de Melhorias/Restrições.'
        # Rewire the calculation to literal inputs: immediate shared-budget math.
        dc=cells[R.DADOS]
        def raw(k,value):dc[tr['colunas'][k]+str(row)][1]=value
        # Prepared state remains persisted per Class; editing the card saves it.
        for k,pos in g['entradas_diretas'].items():
            if k in M.INPUTS:raw(k,'='+R.ref(owner,pos))
        for i,key in enumerate(['dano','cura','vt'],1):
            gate=g['portas'].get(key,'FALSE');pos=g.get('funcoes_diretas',{}).get(key)
            val=R.ref(owner,pos) if pos else '0'
            if g['fixa']:flag=f'AND({gate},{val}=TRUE)'
            else:
                nc=len(g['classes']);pool=R.ref(R.EDITOR,f'$B${g["campos"]["funcao"+str(i)]}:${L(nc+1)}${g["campos"]["funcao"+str(i)]}')
                headers=R.ref(R.EDITOR,f'$B${g["editor"]+1}:${L(nc+1)}${g["editor"]+1}')
                selected='1' if nc==1 else f'MATCH({data("classe")},{headers},0)'
                fn=['Dano','Cura','PV temporários'][i-1]
                flag=f'AND({gate},OR(AND(ISNUMBER({val}),{val}>0),IFERROR(INDEX({pool},1,{selected})="{fn}",FALSE)))'
            raw(key,'='+flag)
            raw('p_'+key,'=0' if g['fixa'] else f'=IF(AND({gate},ISNUMBER({val})),{val},0)')
        for k in ['r1_valida','r2_valida']:raw(k,True)
        dc[tr['colunas']['avisos_funcoes']+str(row)][1]='='+('IF('+g['requisito']+',"","Trunfo exige maldição domada com técnica própria e nível de aquisição")' if g.get('requisito') else '""')
        # Textual adjudication belongs to COMO É, not a second input form.
        # Ampliação preserves the spell's identity; only its allocation scales.
        invariants=['forma','funcao1','funcao2','funcao3','m1','m2','m3','m4','r1','r2','controle','pessoal']
        nc=len(g['classes']);prepared=R.ref(R.EDITOR,f'$B${g["campos"]["preparada"]}:${L(nc+1)}${g["campos"]["preparada"]}')
        changes=[]
        for invariant in invariants:
            rr=g['campos'][invariant];pool=R.ref(R.EDITOR,f'$B${rr}:${L(nc+1)}${rr}')
            changes.append(f'IF(SUMPRODUCT(({prepared}=TRUE)*({pool}<>INDEX({pool},1,MATCH(TRUE,{prepared},0))))>0,"{invariant}","")')
        dc[tr['colunas']['identidade_ampliacao']+str(row)][1]='=IFERROR(TEXTJOIN(" · ",TRUE,'+','.join(changes)+'),"")' if nc>1 else '=""'
        ff=M.formulas(row,tr['colunas'],tr['lookup_range'],familias_range=tr['familias_range'],familias_coluna=f'IFERROR(VALUE(REGEXEXTRACT(A{row},"^entidade[.]([0-9]+)[.]"))+2,2)',formas_range=tr['formas_range'],registro_livre=True,saidas={"avisos","valida"})
        for k in ['avisos','valida']:
            value=ff[k]
            if k=='avisos':value='=TEXTJOIN(" · ",TRUE,'+value[1:]+','+tr['colunas']['avisos_funcoes']+str(row)+',IF('+data('identidade_ampliacao')+'<>"","Ampliação altera funções ou peças: "&'+data('identidade_ampliacao')+',""))'
            dc[tr['colunas'][k]+str(row)][1]=f'=IF({tr["colunas"]["nome"]}{row}="",'+('FALSE' if k=='valida' else '""')+','+value[1:]+')'
    # Clear obsolete menus; install strict direct controls, including blank slots.
    for owner in ['FICHA AMALDIÇOADA','INVOCAÇÕES']:
        a=abas[owner];areas=[range_boundaries(v['faixa']) for v in tr['areas_diretas'] if v['aba']==owner]
        inputs={p for g in tr['contextos'] if g['aba']==owner for p in g['entradas_diretas'].values()}
        def affected(p):
            c,r,cc,rr=range_boundaries(p)
            return any(not(cc<ca or c>cb or rr<ra or r>rb) for ca,ra,cb,rb in areas) or p in inputs
        menus=[]
        for v in a['menus']:
            places=[p for p in v['onde'].split() if not affected(p)]
            if places:menus.append({**v,'onde':' '.join(places)})
        for g in tr['contextos']:
            if g['aba']==owner:menus+=list(g['menus_diretos'].values())
        a['menus']=menus
    abas[R.EDITOR]['estado']='hidden';abas[R.EDITOR]['menus']=[]
    # Basic and graded cards now have different native input types. The old
    # rectangular clone template cannot represent that difference safely.
    abas['INVOCAÇÕES']['copias']=[]
    # Move consumers of relocated anchors, never freshly authored formulas.
    from openpyxl.formula import Tokenizer
    moves={}
    for g in tr['contextos']:
        old=old_contexts[g['id']]
        for k in ['forma','dano','acao']:
            if k not in old or k not in g['cel']:continue
            target=g['cel'][k]
            if k=='dano' and 'linha_funcao' in g:
                target=L(g['coluna']+1)+str(g['linha_funcao']+2)
            if old[k]!=target:moves[g['aba'],old[k]]=target
    for owner,cm in cells.items():
        for pos,item in cm.items():
            v=item[1]
            if v!=originals[owner].get(pos) or not isinstance(v,str) or not v.startswith('='):continue
            output=[]
            for token in Tokenizer(v).items:
                text=token.value
                if token.type=='OPERAND' and token.subtype=='RANGE':
                    prefix,address=text.rsplit('!',1) if '!' in text else ('',text)
                    source=prefix.strip("'").replace("''","'") if prefix else owner
                    parts=[]
                    for part in address.split(':'):
                        match=re.fullmatch(r'(\$?)([A-Z]+)(\$?)([0-9]+)',part)
                        dest=moves.get((source,part.replace('$','')))
                        if match and dest:
                            rr,cc=coordinate_to_tuple(dest);part=match[1]+L(cc)+match[3]+str(rr)
                        parts.append(part)
                    text=(prefix+'!' if prefix else '')+':'.join(parts)
                output.append(text)
            item[1]='='+''.join(output)
    for g in tr['contextos']:
        tr['formulas'][g['id']]={p:cells[g['aba']][p][1] for p in tr['formulas'][g['id']]}
        # Four bulk writes replace dozens of cell-by-cell round trips. Every
        # rectangle covers complete merges and preserves formulas between inputs.
        merges=[range_boundaries(v) for v in abas[g['aba']]['mescladas']]
        byrow={}
        for p in g['entradas_diretas'].values():
            rr,cc=coordinate_to_tuple(p)
            byrow.setdefault(rr,[]).append(next((v for v in merges if v[0]<=cc<=v[2] and v[1]<=rr<=v[3]),(cc,rr,cc,rr)))
        blocks=[]
        for rr,parts in sorted(byrow.items()):
            b=[min(v[1] for v in parts),min(v[0] for v in parts),max(v[3] for v in parts),max(v[2] for v in parts)]
            while True:
                prior=b[:]
                for c1,r1,c2,r2 in merges:
                    if not(c2<b[1] or c1>b[3] or r2<b[0] or r1>b[2]):b=[min(b[0],r1),min(b[1],c1),max(b[2],r2),max(b[3],c2)]
                if prior==b:break
            if blocks and blocks[-1][1::2]==b[1::2] and blocks[-1][2]+1==b[0]:blocks[-1][2]=b[2]
            elif not any(v[0]<=b[0]<=b[2]<=v[2] and v[1]<=b[1]<=b[3]<=v[3] for v in blocks):blocks.append(b)
        g['gravacoes_diretas']=blocks
        g['area_escrita']=[min(v[0] for v in blocks),min(v[1] for v in blocks),max(v[2] for v in blocks),max(v[3] for v in blocks)]
    tr['movimentos_ancoras']=[dict(aba=n,antes=p,depois=q) for (n,p),q in moves.items()]
    tr['direto']=True;tr['esquema_editor']=3
    return tr


def configuracao(tr):
    keys=['id','aba','cel','classes','editor','linha','area_editor','area_escrita','gravacoes_diretas','classe_maxima','entradas_diretas','menus_diretos','fixa','portas','funcoes_diretas','entidade','modo']
    return dict(amparo=dict(aba=R.CATALOGO,faixa='X10:AJ10'),esquema=3,storage=R.EDITOR,data=R.DADOS,campos=R.CAMPOS,defaults={k:R.DEFAULTS_EDITOR[k] for k,_,_ in R.CAMPOS},contextos=[{**{k:g[k] for k in keys if k in g},'formulas':tr['formulas'][g['id']]} for g in tr['contextos']])
