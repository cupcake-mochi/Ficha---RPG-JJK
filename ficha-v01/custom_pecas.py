"""Melhorias e Restrições custom: cadastro, herança e menus dos cartões atuais.

Texto livre não é executado. As verificações publicadas leem a identidade da
base; preços e menus leem os campos efetivos do cadastro. Os catálogos originais
continuam nos mesmos endereços, para não deslocar contratos anteriores.
"""
from copy import deepcopy
from openpyxl.formula import Tokenizer
import indice_ficha as ix
import ficha_amaldicoada as fa
import ficha_invocacoes as iv
from custom_criacao import criterio, ref, q, troca_refs

from capacidades import MELHORIAS, RESTRICOES
MEL = 'DADOS_MELHORIAS'
RES = 'DADOS_RESTRICOES'
PASSO_MEL, PASSO_RES = 26, 22


def coord(r, c):
    return ix._letras(c)+str(r)


def faixa(sheet, c1, r1, c2, r2):
    return ref(coord(r1, c1), sheet)+':$'+ix._letras(c2)+'$'+str(r2)


def registro(tipo, n, inicio):
    total, passo = (MELHORIAS, PASSO_MEL) if tipo == 'melhoria' else (RESTRICOES, PASSO_RES)
    if not 1 <= n <= total:
        raise ValueError('Registro fora da capacidade: '+tipo)
    r, c = inicio+(n-1)//2*passo, 2 if n % 2 else 10
    g = dict(tipo=tipo, n=n, r=r, c=c, nome=coord(r+4,c), base=coord(r+5,c+3),
             mestre_viu=coord(r+2,c+4))
    if tipo == 'melhoria':
        g.update(familia=coord(r+6,c+3), peso=coord(r+7,c+3), exige_tr=coord(r+8,c+3),
                 requisitos=coord(r+11,c), efeito=coord(r+17,c), aviso=coord(r+23,c))
    else:
        g.update(devolucao=coord(r+6,c+3), frequencia=coord(r+7,c+3),
                 efeito=coord(r+10,c), aviso=coord(r+18,c))
    return g


def canoniza_contagens(formula, original, canonica, nomes):
    """Só COUNTIF(faixa de Melhorias, "nome do livro") troca de faixa.

    A contagem de peças, as consultas de preços e os textos literais conservam
    os nomes escolhidos pelo jogador.
    """
    if not isinstance(formula, str) or not formula.startswith('=') or 'COUNTIF(' not in formula.upper():
        return formula
    ts = Tokenizer(formula).items
    for i in range(len(ts)-4):
        a,b,c,d,e = ts[i:i+5]
        if (a.type == 'FUNC' and a.subtype == 'OPEN' and a.value.upper() == 'COUNTIF('
                and b.type == 'OPERAND' and b.subtype == 'RANGE' and b.value == original
                and c.type == 'SEP' and d.type == 'OPERAND' and d.subtype == 'TEXT'
                and d.value[1:-1].replace('""','"') in nomes
                and e.type == 'FUNC' and e.subtype == 'CLOSE'):
            b.value = canonica
    return '='+''.join(t.value for t in ts)


def buscas_literais(formula, sheet, catalogos):
    """MATCH/VLOOKUP exatos também têm curingas: escapar o nome custom."""
    if not isinstance(formula, str) or not formula.startswith('=') or not any(f in formula.upper() for f in ['VLOOKUP(','MATCH(']):
        return formula
    ts = Tokenizer(formula).items
    edits = []
    for i,t in enumerate(ts):
        if t.type != 'FUNC' or t.subtype != 'OPEN' or t.value.upper() not in ('VLOOKUP(', 'MATCH('):
            continue
        depth, sep, end = 0, [], None
        for j in range(i+1,len(ts)):
            x = ts[j]
            if x.subtype == 'OPEN' and x.type in ('FUNC','PAREN','ARRAY'):
                depth += 1
            elif x.subtype == 'CLOSE' and x.type in ('FUNC','PAREN','ARRAY'):
                if depth == 0:
                    end = j
                    break
                depth -= 1
            elif x.type == 'SEP' and depth == 0:
                sep.append(j)
        if len(sep) < 2 or end is None:
            continue
        arg = ts[sep[0]+1:sep[1]]
        if len(arg) != 1 or arg[0].subtype != 'RANGE':
            continue
        owner, address = (arg[0].value.rsplit('!',1) if '!' in arg[0].value else (sheet,arg[0].value))
        if (owner.strip("'").replace("''", "'"), address.replace('$','')) not in catalogos:
            continue
        first = ''.join(x.value for x in ts[i+1:sep[0]])
        edits.append((i+1,sep[0],criterio(first)))
    values = [t.value for t in ts]
    # Called on ordinary lookups; nested first arguments remain intact.
    prefix,suffix=criterio('\0').split('\0')
    for start,end,value in edits:
        values[start]=prefix+values[start]
        values[end-1]+=suffix
    return '='+''.join(values)


def aplica(layout, fam, inv, criacao):
    config = ix._aba(layout,'CONFIGURAÇÃO')
    prior_end = config['linhas']
    inicio_m = prior_end+4
    fim_m = inicio_m+(MELHORIAS-1)//2*PASSO_MEL+24
    inicio_r = fim_m+5
    fim_r = inicio_r+(RESTRICOES-1)//2*PASSO_RES+19
    regs_m = [registro('melhoria',n,inicio_m) for n in range(1,MELHORIAS+1)]
    regs_r = [registro('restricao',n,inicio_r) for n in range(1,RESTRICOES+1)]
    styles = {v[0]:v[2] for v in config['celulas']}
    st = dict(secao=styles['B9'], rotulo=styles['B10'], entrada=styles['C11'],
              caixa=styles['B11'], nota=styles['B5'])
    text = deepcopy(layout['estilos'][st['entrada']]); text[3]=['left','top',True,0]
    if text not in layout['estilos']:
        layout['estilos'].append(text)
    st['texto'] = layout['estilos'].index(text)
    tr = dict(antes={},depois={},entradas=[],registros=regs_m+regs_r,
              inicio=inicio_m,fim=fim_r,fim_familias=prior_end,substituicoes=0,
              limites={},catalogos={})
    for name,rows,cols in [(MEL,MELHORIAS+len(fam['R']['pecas'])+3,69),
                           (RES,RESTRICOES+len(fam['R']['restricoes'])+3,22)]:
        layout['abas'].append(dict(nome=name,estado='hidden',linhas=rows,colunas=cols,
            padrao=['Roboto',10,'#000000'],fundo_base='#FFFFFF',grade=False,
            celulas=[],mescladas=[],menus=[],condicional=[],imagens=[],colunas_larg=[],
            linhas_alt=[],altura_padrao=15.75,paleta_fixa=True,validacao_em_matriz=True,abaixo=True))
    cells = {a['nome']:{v[0]:v for v in a['celulas']} for a in layout['abas']}

    def put(sheet,a1,value,style=None):
        old = cells[sheet].get(a1)
        before = old[1] if old is not None else None
        if before != value:
            tr['antes'].setdefault(sheet,{}).setdefault(a1,before)
            tr['depois'].setdefault(sheet,{})[a1]=value
        if old is None:
            old=[a1,value,style]; cells[sheet][a1]=old
            ix._aba(layout,sheet)['celulas'].append(old)
        else:
            old[1]=value
            if style is not None:
                old[2]=style

    def d(sheet,r,c,value):
        put(sheet,coord(r,c),value)

    def box(r,c,value=None,er=None,ec=None,kind='entrada',note=None):
        a1,end=coord(r,c),coord(er or r,ec or c)
        if a1 in cells['CONFIGURAÇÃO']:
            raise ValueError('Novo cartão sobrepõe CONFIGURAÇÃO!'+a1)
        put('CONFIGURAÇÃO',a1,value,st[kind])
        if a1 != end:
            config['mescladas'].append(a1+':'+end)
        config['notas'][a1]=note or 'Campo do cadastro custom. Em branco herda a base do livro, quando escolhida.'

    def menu(a1,source):
        config['menus'].append(dict(onde=a1,tipo='list',formula=source,vazio_ok=True,mostra_seta=True,estrito=True))
        config.setdefault('menus_estritos',[]).append(a1)

    def read_config(sheet,r,c,offset,delta,g):
        # Referência direta acompanha o cartão ao reorganizar os painéis.
        # O INDEX antigo dependia de uma matriz vertical única e de números
        # de linha/coluna guardados separadamente no catálogo.
        expr=ref(f'{ix._letras(g["c"]+delta)}{g["r"]+offset}', 'CONFIGURAÇÃO')
        d(sheet,r,c,f'=IF(ISBLANK({expr}),"",{expr})')

    family_source=criacao['catalogo_familias']
    family_end=ix._lc(family_source.rsplit('!')[1].split(':')[-1].replace('$',''))[0]
    family_names=faixa(MEL,65,2,65,family_end+1)
    d(MEL,1,65,'Família permitida'); d(MEL,2,65,'Nenhuma')
    for r in range(2,family_end+1):
        rr=ref('H'+str(r),'DADOS_CRIACAO')
        d(MEL,r+1,65,f'=IF({rr}="","",{rr})')
    for sheet,weights in [(MEL,['Leve','Média','Pesada']),(RES,['Leve','Média'])]:
        for r,name in enumerate(weights,2): d(sheet,r,66 if sheet==MEL else 20,name)
        for r,name in enumerate(['Sim','Não'],2): d(sheet,r,67 if sheet==MEL else 21,name)
        d(sheet,2,68 if sheet==MEL else 22,'Nenhuma')

    # Livro continua em suas posições antigas; os catálogos unidos só o espelham.
    books={MEL:len(fam['R']['pecas']),RES:len(fam['R']['restricoes'])}
    for sheet,kind,catalog,table,width,start in [(MEL,'melhoria',fam['R']['pecas'],'pecas',9,15),
                                                (RES,'restricao',fam['R']['restricoes'],'res',5,13)]:
        nbook=books[sheet]
        total=nbook+(MELHORIAS if sheet==MEL else RESTRICOES)
        tr['limites'][sheet]=dict(livro=nbook,total=total,inicio=start,largura=width)
        for r,item in enumerate(catalog,2):
            for k in range(width):
                source=fam['D'].celula(table,r-2,k,aba=fa.DA)
                d(sheet,r,start+k,f'=IF(ISBLANK({source}),"",{source})')
            base_name=item['nome'] if sheet==MEL else item['rotulo']
            d(sheet,r+1,68 if sheet==MEL else 22,base_name)
            if sheet==MEL:
                d(sheet,r,24,item['nome'])
                d(sheet,r,25,int(item['nome'] in inv['R']['reduzidas']))
        book_names=faixa(sheet,start,2,start,nbook+1)
        base_list=faixa(sheet,68 if sheet==MEL else 22,2,68 if sheet==MEL else 22,nbook+2)
        tr['catalogos'][kind]=faixa(sheet,start,2,start+width-1,total+1)
        regs=regs_m if sheet==MEL else regs_r
        headers=(['linha CONFIGURAÇÃO','lado CONFIGURAÇÃO','registro','nome','base','família','peso','exige TR',
                  'requisitos e repetição','efeito','mestre viu','linha da base','problema'] if sheet==MEL else
                 ['linha CONFIGURAÇÃO','lado CONFIGURAÇÃO','registro','nome','base','devolução','frequência','efeito',
                  'mestre viu','linha da base','problema'])
        for c,label in enumerate(headers,1): d(sheet,1,c,label)
        for g in regs:
            r,dst=g['n']+1,nbook+g['n']+1
            d(sheet,r,1,g['r']); d(sheet,r,2,g['c']-2); d(sheet,r,3,g['n'])
            fields=([('nome',4,0),('base',5,3),('familia',6,3),('peso',7,3),('exige_tr',8,3),
                     ('requisitos',11,0),('efeito',17,0),('mestre_viu',2,4)] if sheet==MEL else
                    [('nome',4,0),('base',5,3),('devolucao',6,3),('frequencia',7,3),('efeito',10,0),('mestre_viu',2,4)])
            for c,(key,offset,delta) in enumerate(fields,4):
                read_config(sheet,r,c,offset,delta,g)
                tr['entradas'].append((f'custom.{kind}.{g["n"]}.{key}',g[key],key=='mestre_viu'))
            idx,err,master=('L','M','K') if sheet==MEL else ('J','K','I')
            d(sheet,r,ix._lc(idx+'1')[1],f'=IF(OR(E{r}="",E{r}="Nenhuma"),0,IFERROR(MATCH({criterio("E"+str(r))},{book_names},0),-1))')
            invalid=[f'IF(OR(NOT(ISTEXT(D{r})),TRIM(D{r})<>D{r}),"NOME precisa ser texto sem espaços nas pontas","")',
                     f'IF(COUNTIF($D$2:$D${len(regs)+1},{criterio("D"+str(r))})+COUNTIF({book_names},{criterio("D"+str(r))})>1,"Nome repetido no livro ou custom","")',
                     f'IF({idx}{r}<0,"Escolha uma BASE DO LIVRO válida","")',
                     f'IF(ISLOGICAL({master}{r}),"","MESTRE VIU deve ser caixa de seleção")']
            weightcol='G' if sheet==MEL else 'F'
            wrange=faixa(sheet,66 if sheet==MEL else 20,2,66 if sheet==MEL else 20,4 if sheet==MEL else 3)
            yncol='H' if sheet==MEL else 'G'
            invalid += [f'IF(AND({weightcol}{r}="",{idx}{r}<=0),"Escolha '+('PESO' if sheet==MEL else 'DEVOLUÇÃO')+'","")',
                        f'IF(AND({weightcol}{r}<>"",COUNTIF({wrange},{criterio(weightcol+str(r))})<>1),"Peso ou devolução inválido","")',
                        f'IF(AND({yncol}{r}<>"",{yncol}{r}<>"Sim",{yncol}{r}<>"Não"),"Escolha Sim ou Não","")']
            if sheet==MEL:
                invalid.append(f'IF(AND(F{r}<>"",COUNTIF({family_names},{criterio("F"+str(r))})<>1),"Família não cadastrada ou com erro","")')
            extras=('OR(I{r}<>"",J{r}<>"",F{r}<>"",G{r}<>"",H{r}<>"",K{r}=TRUE,AND(E{r}<>"",E{r}<>"Nenhuma"))' if sheet==MEL else
                    'OR(F{r}<>"",G{r}<>"",H{r}<>"",I{r}=TRUE,AND(E{r}<>"",E{r}<>"Nenhuma"))').format(r=r)
            d(sheet,r,ix._lc(err+'1')[1],f'=IF(D{r}="",IF({extras},"Preencha NOME",""),TEXTJOIN(" · ",TRUE,{",".join(invalid)}))')
            valid=f'AND(D{r}<>"",{err}{r}="")'
            d(sheet,dst,start,f'=IF({valid},D{r},"")')
            base=lambda c: f'IF({idx}{r}>0,INDEX({faixa(sheet,c,2,c,nbook+1)},{idx}{r}),0)'
            if sheet==MEL:
                d(sheet,dst,16,f'=IF(F{r}<>"",IF(F{r}="Nenhuma","",F{r}),IF({idx}{r}>0,INDEX($P$2:$P${nbook+1},{idx}{r}),""))')
                d(sheet,dst,17,f'=IF(G{r}<>"",IFERROR(MATCH(G{r},{wrange},0),0),{base(17)})')
                fc=criterio('P'+str(dst))
                d(sheet,dst,18,f'=Q{dst}+3*IFERROR(VLOOKUP({fc},{faixa("DADOS_CRIACAO",8,2,11,family_end)},3,FALSE),0)')
                d(sheet,dst,19,f'=IFERROR(VLOOKUP({fc},{faixa("DADOS_CRIACAO",8,2,11,family_end)},4,FALSE),0)')
                d(sheet,dst,20,f'=IF(OR(P{dst}="Controle",{base(20)}=1),1,0)')
                d(sheet,dst,21,f'=IF(S{dst}=1,"",O{dst})')
                d(sheet,dst,22,f'=IF(AND(Q{dst}=1,S{dst}=0),O{dst},"")')
                d(sheet,dst,23,f'=IF(H{r}="",{base(23)},IF(H{r}="Sim",1,0))')
                d(sheet,dst,24,f'=IF({idx}{r}>0,INDEX($X$2:$X${nbook+1},{idx}{r}),D{r})')
                d(sheet,dst,25,'='+base(25))
            else:
                d(sheet,dst,14,f'=IF({idx}{r}>0,INDEX($N$2:$N${nbook+1},{idx}{r}),D{r})')
                d(sheet,dst,15,f'=IF(F{r}<>"",IFERROR(MATCH(F{r},{wrange},0),0),{base(15)})')
                d(sheet,dst,16,f'=IF(G{r}="",{base(16)},IF(G{r}="Sim",1,0))')
                d(sheet,dst,17,f'=IF(O{dst}=1,M{dst},"")')
            # Buscas de uma caixa vazia podem encontrar uma linha excluída do
            # catálogo. Seus campos mecânicos também precisam ficar neutros.
            text_cols={16,21,22,24} if sheet==MEL else {14,17}
            name_col='O' if sheet==MEL else 'M'
            for c in range(start+1,start+(11 if sheet==MEL else 5)):
                a1=coord(dst,c)
                value=cells[sheet][a1][1][1:]
                blank='""' if c in text_cols else '0'
                d(sheet,dst,c,f'=IF({name_col}{dst}="",{blank},{value})')
            # Cartão com o mesmo desenho aprovado e notas contextuais.
            rr,c=g['r'],g['c']; label='MELHORIA' if sheet==MEL else 'RESTRIÇÃO'
            box(rr,c,label+' · '+str(g['n']),ec=c+5,kind='secao')
            box(rr+1,c,'TIPO',ec=c+3,kind='rotulo'); box(rr+2,c,label.title(),ec=c+3)
            box(rr+1,c+4,'MESTRE VIU',ec=c+5,kind='rotulo')
            box(rr+2,c+4,False,ec=c+5,kind='caixa',note='Lembrete marcado pelo jogador. Aprovação ocorre pelo bot no chat.')
            box(rr+3,c,'NOME',ec=c+5,kind='rotulo'); box(rr+4,c,ec=c+5)
            def field(offset,title,key,source,note):
                box(rr+offset,c,title,ec=c+2,kind='rotulo',note=note)
                box(rr+offset,c+3,'Nenhuma' if key=='base' else None,ec=c+5,note=note)
                menu(g[key],source)
            field(5,'BASE DO LIVRO','base',base_list,
                  'Opcional. Nenhuma cria do zero. Com base, campos em branco e verificações específicas herdam o livro. Texto livre não cria automações.')
            if sheet==MEL:
                field(6,'FAMÍLIA','familia',family_names,'Em branco herda a base; Nenhuma remove a Família. A técnica usa o estado cadastrado; entidades usam suas próprias Famílias abertas.')
                field(7,'PESO','peso',wrange,'Em branco herda a base. Sem base, escolha Leve, Média ou Pesada. Preços e desconto seguem a Classe da ficha.')
                field(8,'EXIGE TR','exige_tr',faixa(sheet,67,2,67,3),'Em branco herda a base. Sim indica que o efeito exige TR, inclusive em Forma de ataque.')
                box(rr+10,c,'REQUISITOS E REPETIÇÃO',ec=c+5,kind='rotulo')
                box(rr+11,c,er=rr+14,ec=c+5,kind='texto',note='Descreva requisitos, incompatibilidades e limite de compras. Verificações da base continuam; texto livre é conferido pelo mestre e pelo bot.')
                box(rr+16,c,'EFEITO',ec=c+5,kind='rotulo')
                box(rr+17,c,er=rr+21,ec=c+5,kind='texto',note='Efeito completo da Melhoria. Números do personagem sem campo próprio são registrados em BÔNUS E MUDANÇAS.')
                box(rr+23,c,f'=IF({ref(err+str(r),sheet)}="","","⚠ "&{ref(err+str(r),sheet)})',er=rr+24,ec=c+5,kind='nota')
            else:
                field(6,'DEVOLUÇÃO','devolucao',wrange,'Em branco herda a base. Sem base, escolha Leve ou Média. Restrição paga Melhorias, nunca a Forma, e conserva o teto e o limite de Restrições.')
                field(7,'FREQUÊNCIA','frequencia',faixa(sheet,21,2,21,3),'Em branco herda a base. Sim identifica Restrição de frequência; duas de frequência continuam incompatíveis.')
                box(rr+9,c,'EFEITO E REQUISITOS',ec=c+5,kind='rotulo')
                box(rr+10,c,er=rr+16,ec=c+5,kind='texto',note='Exigência, momento de cumprir, duração e incompatibilidades. Texto livre não é executado como fórmula.')
                box(rr+18,c,f'=IF({ref(err+str(r),sheet)}="","","⚠ "&{ref(err+str(r),sheet)})',er=rr+19,ec=c+5,kind='nota')

    # Índices próprios para entidades: mesmos campos e pesos, sem o estado da
    # técnica nem seu desconto. Cada entidade mantém as nove aberturas.
    mtotal=tr['limites'][MEL]['total']
    for r in range(2,mtotal+2):
        for c,source in enumerate(['O','P','Q','T','Y','W'],33):
            d(MEL,r,c,'='+source+str(r))
        for i in range(len(inv['fichas_c'])):
            own=[ref(coord(i+2,inv['colf']['f'+str(j)]),iv.DADOS_IV) for j in range(9)]
            opened='OR(P'+str(r)+'="",'+','.join('P'+str(r)+'='+rr for rr in own)+')'
            d(MEL,r,40+2*i,f'=IF({opened},O{r},"")')
            d(MEL,r,41+2*i,f'=IF(AND(Q{r}=1,{opened}),O{r},"")')

    # Substituir somente os intervalos de catálogo, sem deslocar outras tabelas.
    mapping={}
    for owner,meta,table,new_sheet,start,width,total in [
            (fa.DADOS_AM,fam,'pecas',MEL,15,9,mtotal),
            (iv.DADOS_IV,inv,'pecas',MEL,33,6,mtotal),
            (fa.DADOS_AM,fam,'res',RES,13,5,tr['limites'][RES]['total']),
            (iv.DADOS_IV,inv,'res',RES,13,5,tr['limites'][RES]['total'])]:
        old_c,first,last,_=meta['D'].T[table]
        for left in range(width):
            for right in range(left,width):
                old=fa._faixa(old_c+left,first,old_c+right,last).replace('$','')
                mapping[(owner,old)]=faixa(new_sheet,start+left,2,start+right,total+1)
    for i in range(len(inv['fichas_c'])):
        for k in range(2):
            old=inv['D'].faixa('menu'+str(i),so=k).replace('$','')
            mapping[(iv.DADOS_IV,old)]=faixa(MEL,40+2*i+k,2,40+2*i+k,mtotal+1)
    targets=set()
    for value in mapping.values():
        owner,address=value.rsplit('!',1)
        targets.add((owner.strip("'"),address.replace('$','')))
    # These internal formulas intentionally mirror the old book tables.
    for aba in layout['abas']:
        if aba['nome'] in (MEL,RES): continue
        for v in list(aba['celulas']):
            new=troca_refs(v[1],aba['nome'],mapping)
            new=buscas_literais(new,aba['nome'],targets)
            if new != v[1]:
                put(aba['nome'],v[0],new); tr['substituicoes']+=1
        for m in aba['menus']:
            m['formula']=troca_refs('='+m['formula'],aba['nome'],mapping)[1:]

    # Cache de identidade da base: os textos e custos mantêm o nome custom.
    canonical_catalog=faixa(MEL,15,2,24,mtotal+1)
    names={p['nome'] for p in fam['R']['pecas']}
    for owner,meta,table in [(fa.DADOS_AM,fam,'feit'),(iv.DADOS_IV,inv,'cartas')]:
        aba=ix._aba(layout,owner)
        begin=aba['colunas']+1
        _,first,last,_=meta['D'].T[table]
        for k in range(1,5):
            d(owner,1,begin+k-1,'base da melhoria '+str(k))
            for r in range(first,last+1):
                raw='$'+coord(r,meta['col']['m'+str(k)])
                d(owner,r,begin+k-1,f'=IF({raw}="","",IFERROR(VLOOKUP({criterio(raw)},{canonical_catalog},10,FALSE),{raw}))')
        for r in range(first,last+1):
            old='$'+coord(r,meta['col']['m1'])+':$'+coord(r,meta['col']['m4'])
            new='$'+coord(r,begin)+':$'+coord(r,begin+3)
            for c in meta['col'].values():
                a1=coord(r,c)
                value=cells[owner][a1][1]
                changed=canoniza_contagens(value,old,new,names)
                if changed != value: put(owner,a1,changed)
            unknown=[]
            for kind,prefix,count,name_range in [
                    ('Melhoria','m',4,faixa(MEL,15,2,15,mtotal+1)),
                    ('Restrição','r',2,faixa(RES,13,2,13,tr['limites'][RES]['total']+1))]:
                for k in range(1,count+1):
                    raw='$'+coord(r,meta['col'][prefix+str(k)])
                    unknown.append(f'IF(AND({raw}<>"",COUNTIF({name_range},{criterio(raw)})=0),"{kind} não cadastrada ou com erro: "&{raw},"")')
            error_cell=coord(r,meta['col']['erros'])
            old_error=cells[owner][error_cell][1][1:]
            tem='$'+coord(r,meta['col']['tem'])
            put(owner,error_cell,f'=IF({tem}=0,"",TEXTJOIN(" · ",TRUE,{old_error},{",".join(unknown)}))')
        aba['colunas']=begin+3
        if aba['colunas_larg']: aba['colunas_larg'][0][1]=aba['colunas']
    # As Classes 0 usam comparação direta no alcance, não COUNTIF.
    owner=fa.DADOS_AM; aba=ix._aba(layout,owner); cache=aba['colunas']+1
    d(owner,1,cache,'base da melhoria da classe 0')
    zcol,zfirst,zlast,_=fam['D'].T['carta_zero']
    for r in range(zfirst,zlast+1):
        raw='$'+coord(r,zcol+2)
        canon='$'+coord(r,cache)
        d(owner,r,cache,f'=IF({raw}="","",IFERROR(VLOOKUP({criterio(raw)},{canonical_catalog},10,FALSE),{raw}))')
        a1=coord(r,zcol+7); value=cells[owner][a1][1]
        tokens=Tokenizer(value).items
        for token in tokens:
            if token.type=='OPERAND' and token.subtype=='RANGE' and token.value==raw:
                token.value=canon
        put(owner,a1,'='+''.join(t.value for t in tokens))
    aba['colunas']=cache
    if aba['colunas_larg']: aba['colunas_larg'][0][1]=cache

    # Rodapé e altura acompanham o maior texto dos dois cartões vizinhos.
    config['linhas']=fim_r
    for regs,step,end in [(regs_m,PASSO_MEL,fim_m),(regs_r,PASSO_RES,fim_r)]:
        begin=regs[0]['r']
        box(begin-2,2,'MELHORIAS CUSTOM' if regs is regs_m else 'RESTRIÇÕES CUSTOM',ec=15,kind='secao')
        config.setdefault('copias',[]).append([begin,begin+step-2,
            [begin+i*step for i in range(1,len(regs)//2)],2,15,[[2,7],[10,15]],True])
        config['linhas_alt'] += [[r,18.75] for r in range(begin-2,end+1)]
        for i in range(0,len(regs),2):
            pair=regs[i:i+2]
            for key,offset,height in ([('requisitos',11,4),('efeito',17,5)] if regs is regs_m else [('efeito',10,7)]):
                texts=[]
                for g in pair:
                    width=sum(next((w for lo,hi,w in config['colunas_larg'] if lo<=c<=hi),4)*8-1 for c in range(g['c'],g['c']+6))-12
                    texts.append([width,[g[key]],g['r']+offset,height,0])
                config.setdefault('esticam',[]).append(dict(gatilhos=[g[key] for g in pair],aba='CONFIGURAÇÃO',minima=25,textos=texts))
    tr['consumidores']={
        fa.DADOS_AM:dict(col=fam['col'],tabelas=fam['D'].T,globais=fam['H'],lugares=fam['lugares'],zero=fam['zero_c']),
        iv.DADOS_IV:dict(col=inv['col'],colf=inv['colf'],tabelas=inv['D'].T,globais=inv['H'],
                        fichas=[{k:v for k,v in g.items() if k!='cartas'} for g in inv['fichas_c']],cartas=inv['cartas'])}
    return tr


def exporta(tr):
    out=[]
    for key,a1,boolean in tr['entradas']:
        rr=ref(a1,'CONFIGURAÇÃO')
        value=f'=N({rr})&""' if boolean else f'=IF(ISBLANK({rr}),"",{rr}&"")'
        out.append([key,value,rr.replace('$',''),'configuração'])
    for g in tr['registros']:
        sheet,err=(MEL,'M') if g['tipo']=='melhoria' else (RES,'K')
        rr=ref(err+str(g['n']+1),sheet)
        out.append([f'aviso.custom.{g["tipo"]}.{g["n"]}','='+rr+'&""',rr.replace('$',''),'aviso'])
    return out
