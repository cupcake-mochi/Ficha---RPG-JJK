"""Listas recolhíveis junto das escolhas do livro, sem novos benefícios.

Transformação final da apresentação. Os leitores mecânicos continuam lendo
as mesmas entradas; apenas os campos de edição mudam de lugar.
"""
import copy
import re
from functools import lru_cache
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import coordinate_to_tuple, get_column_letter as L

INSERCOES = {'FICHA': [(92, 13), (103, 13)],
             'FICHA AMALDIÇOADA': [(39, 13)],
             'INVOCAÇÕES': [(52 + 198*i, 13) for i in range(6)]}
ORDEM = [0, 1, 5, 6, 7, 8, 2, 3, 4]


def linha(sheet, row):
    return row + sum(n for at, n in INSERCOES.get(sheet, []) if row >= at)


def coord(sheet, text):
    def one(x):
        m = re.fullmatch(r'(\$?[A-Z]+)(\$?)(\d+)', x)
        if m:
            return m[1] + m[2] + str(linha(sheet, int(m[3])))
        if re.fullmatch(r'\$?\d+', x):
            return ('$' if x.startswith('$') else '') + str(linha(sheet, int(x.lstrip('$'))))
        return x  # whole-column and named ranges
    return ':'.join(one(x) for x in text.split(':'))


@lru_cache(maxsize=40000)
def formula(text, owner):
    if not isinstance(text, str):
        return text
    literal = re.fullmatch(r"('(?:[^']|'')+'|[^!=]+)!([A-Z]+\d+(?::[A-Z]+\d+)?)", text)
    if literal:
        return literal[1]+'!'+coord(literal[1].strip("'").replace("''", "'"), literal[2])
    if not text.startswith('=') or (owner not in INSERCOES and not any(s in text for s in INSERCOES)):
        return text
    out = []
    for token in Tokenizer(text).items:
        value = token.value
        if token.type == 'OPERAND' and token.subtype == 'RANGE':
            if '!' in value:
                prefix, address = value.rsplit('!', 1)
                sheet = prefix.strip("'").replace("''", "'")
                value = prefix+'!'+coord(sheet, address)
            else:
                value = coord(owner, value)
        out.append(value)
    return '='+''.join(out)


def deslocar(layout):
    for a in layout['abas']:
        owner = a['nome']
        own = lambda x: coord(owner, x)
        indices_am = {re.match(r'[A-Z]+',x[0])[0] for x in a['celulas']
                      if x[0].endswith('1') and x[1]=='caixa calculada'} if owner=='DADOS_AM' else set()
        for x in a['celulas']:
            x[0] = own(x[0]); x[1] = formula(x[1], owner)
            if indices_am and re.match(r'[A-Z]+',x[0])[0] in indices_am and isinstance(x[1],str) and re.fullmatch(r'[A-Z]+\d+',x[1]):
                x[1] = coord('FICHA AMALDIÇOADA',x[1])
            if len(x) > 3:
                x[3] = own(x[3])
        for m in a.get('menus', []):
            m['onde'] = ' '.join(own(x) for x in m['onde'].split())
            f = m.get('formula')
            if isinstance(f, str):
                m['formula'] = formula('='+f.lstrip('='), owner)[1:]
        for cf in a.get('condicional', []):
            cf['onde'] = ' '.join(own(x) for x in cf['onde'].split())
            cf['formula'] = [formula('='+x.lstrip('='), owner)[1:] for x in cf['formula']]
        for cf in a.get('condicional_gs', []):
            cf['faixas'] = [own(x) for x in cf['faixas']]
            if cf.get('formula'):
                cf['formula'] = formula(cf['formula'], owner)
        for g in a.get('esticam', []):
            g['gatilhos'] = [own(x) for x in g['gatilhos']]
            for t in g['textos']:
                t[1] = [own(x) for x in t[1]]
                t[2] = linha(g['aba'], t[2])
        if owner not in INSERCOES:
            continue
        a['linhas'] = linha(owner, a['linhas'])
        a['mescladas'] = [own(x) for x in a['mescladas']]
        a['notas'] = {own(k): v for k, v in a.get('notas', {}).items()}
        a['linhas_alt'] = [[linha(owner, r), h] for r, h in a['linhas_alt']]
        for g in a.get('grupos', {}).get('linhas', []):
            g[0], g[1] = linha(owner, g[0]), linha(owner, g[1])
        for k in ['livres', 'menus_estritos', 'da_carteira']:
            if k in a:
                a[k] = [own(x) for x in a[k]]
        for g in a.get('sem_trava', []):
            if isinstance(g, list):
                g[0], g[1] = linha(owner, g[0]), linha(owner, g[1])
        for g in a.get('copias', []):
            g[0], g[1], g[2] = linha(owner, g[0]), linha(owner, g[1]), [linha(owner, x) for x in g[2]]
        for g in a.get('abrir', []):
            g[0], g[1] = own(g[0]), linha(owner, g[1])
        if 'redutores' in a:
            a['redutores'] = [[own(x) for x in g] for g in a['redutores']]
        if a.get('notas_contextuais'):
            a['notas_contextuais']['destinos'] = [own(x) for x in a['notas_contextuais']['destinos']]
        for im in a['imagens']:
            im['lin'] = linha(owner, im['lin'])


def aplica(layout, prog, criacao, inv):
    if any(a.get('extensoes_custom') for a in layout['abas']):
        raise ValueError('Extensões já aplicadas')
    from configuracao_horizontal import coord as horizontal
    from custom_criacao import criterio
    # Capture the original canonical records before their physical translation.
    usos = copy.deepcopy(prog['linhas_ficha'])
    entidades = copy.deepcopy(inv.get('fichas_c', inv.get('fichas')))
    deslocar(layout)
    abas = {a['nome']: a for a in layout['abas']}
    cells = {n: {x[0]: x for x in a['celulas']} for n, a in abas.items()}
    audit = {'insercoes': INSERCOES, 'transferencias': [], 'paineis': []}
    def put(sheet, c, v, style=None):
        x = cells[sheet].get(c)
        if x is None:
            x = [c, v, style]; cells[sheet][c] = x; abas[sheet]['celulas'].append(x)
        else:
            x[1] = v
            if style is not None:
                x[2] = style
    # Native row insertion inherits the spine's ink/divider. A fresh build
    # must paint the same empty cells explicitly as well.
    for at,n in INSERCOES['FICHA']:
        first=linha('FICHA',at)-n
        for r in range(first,first+n):
            for col in ('A','B'):
                put('FICHA',col+str(r),None,cells['FICHA'][col+str(first-1)][2])
    st = {'secao': cells['FICHA']['G76'][2], 'rotulo': cells['FICHA']['D79'][2],
          'entrada': cells['FICHA'][coord('FICHA', 'F413')][2],
          'caixa': cells['FICHA']['D80'][2]}
    for k in ['rotulo', 'entrada', 'nota']:
        src = st.get(k, st['entrada']); e = copy.deepcopy(layout['estilos'][src])
        e[0][0] = 'Roboto'; e[0][1] = 10 if k != 'nota' else 9
        e[3] = ['left' if k == 'nota' else 'center', 'center', True, 0]
        if e not in layout['estilos']:
            layout['estilos'].append(e)
        st[k] = layout['estilos'].index(e)
    def box(sheet, row, ca, cb, value=None, kind='entrada'):
        c = L(ca)+str(row); end = L(cb)+str(row)
        put(sheet, c, value, st[kind])
        if c != end:
            abas[sheet]['mescladas'].append(c+':'+end)
        return c
    def menu(sheet, c, source, tipo='list'):
        abas[sheet]['menus'].append(dict(tipo=tipo, formula=source, onde=c,
                                        vazio_ok=True, mostra_seta=True, estrito=True))
    def panel(sheet, header, ca, cb, title, intro, group=True):
        # Headers remain available when their body is collapsed; body text is
        # entirely empty until at least one valid definition exists.
        pool = "'DADOS_CRIACAO'!$H$11:$H$20" if 'FAMÍLIA' in title else "'DADOS_PROGRESSAO'!$AV$2:$AV$11" if 'PERÍCIA' in title else "'DADOS_PROGRESSAO'!$AW$2:$AW$11"
        box(sheet, header, ca, cb, title+' · CONFIGURAÇÃO', 'secao')
        box(sheet, header+1, ca, cb, f'=IF(COUNTIF({pool},"?*")=0,"","{intro}")', 'nota')
        if group:
            abas[sheet].setdefault('grupos', {}).setdefault('linhas', []).append([header+1, header+13, True])
        abas[sheet]['linhas_alt'] += [[header,18.75],[header+1,31.5]]+[[header+i,18.75] for i in range(2,14)]
        audit['paineis'].append(dict(aba=sheet, cabecalho=header, primeira=header+1, ultima=header+13))
        return pool

    # FICHA: one stable visible row per definition; old calculation slots become
    # mirrors. This preserves all counters and existing ANALISE keys.
    sheet = 'FICHA'
    for typ, old_header, poolcol in [('Perícia',91,'AV'),('Ofício',102,'AW')]:
        h = linha(sheet, old_header)
        pool = panel(sheet,h,4,46,typ.upper()+'S CUSTOM',
                     'T = treino; E = especialização. Usam os mesmos limites do livro. Edite o cadastro em CONFIGURAÇÃO.')
        for ca,cb,label in [(4,4,'T'),(5,5,'E'),(6,22,'NOME'),(23,29,'ATRIBUTO'),(30,37,'TOTAL'),(38,46,'BÔNUS')]:
            box(sheet,h+2,ca,cb,f'=IF(COUNTIF({pool},"?*")=0,"","{label}")','rotulo')
        selected = [g for g in usos if g['tipo']==typ]
        for g in selected:
            n = g['n']
            old = {k: coord(sheet,g[k]) for k in ['treino','especializacao','nome','atributo','resultado','bonus']}
            # No editable selectors remain in the hidden canonical area.
            for m in list(abas[sheet]['menus']):
                if m['onde'] == old['nome'] or (typ=='Ofício' and m['onde']==old['atributo']):
                    abas[sheet]['menus'].remove(m)
            if n > 10:
                put(sheet,old['nome'],None)
                continue
            row = h+2+n
            new = {'treino':'D'+str(row),'especializacao':'E'+str(row),'nome':'F'+str(row),
                   'atributo':'W'+str(row),'resultado':'AD'+str(row),'bonus':'AL'+str(row)}
            name = f"='DADOS_PROGRESSAO'!${poolcol}${n+1}"
            put(sheet,old['nome'],name)
            box(sheet,row,6,22,name)
            for key,col,end in [('treino',4,4),('especializacao',5,5),('bonus',38,46)]:
                box(sheet,row,col,end,False if key!='bonus' else None,'caixa' if key!='bonus' else 'entrada')
                put(sheet,old[key],f'=IF({new["nome"]}="",'+('FALSE' if key!='bonus' else '""')+f',{new[key]})')
                audit['transferencias'].append(dict(aba=sheet,de=old[key],para=new[key],nome=old['nome'],tipo=typ,n=n,campo=key))
            box(sheet,row,30,37,'='+old['resultado'])
            if typ=='Perícia':
                box(sheet,row,23,29,'='+old['atributo'])
            else:
                # Default attribute remains editable exactly as for book offices.
                attr = f'=IFERROR(VLOOKUP({criterio(new["nome"])},\'DADOS_PROGRESSAO\'!$AJ$2:$AK$22,2,FALSE),"")'
                box(sheet,row,23,29,attr)
                put(sheet,old['atributo'],f'=IF({new["nome"]}="","",{new["atributo"]})')
                abas[sheet].setdefault('livres',[]).append(new['atributo'])
                if old['atributo'] in abas[sheet]['livres']:
                    abas[sheet]['livres'].remove(old['atributo'])
                menu(sheet,new['atributo'],"'DADOS_PROGRESSAO'!$AN$2:$AN$6")
                audit['transferencias'].append(dict(aba=sheet,de=old['atributo'],para=new['atributo'],nome=old['nome'],tipo=typ,n=n,campo='atributo'))
    abas[sheet]['linhas_ocultas'] = [[linha(sheet,411), linha(sheet,436)]]

    # Technique states now belong next to the book states. CONFIGURAÇÃO stores
    # only the definition and a read-only mirror, so it cannot disagree.
    sheet = 'FICHA AMALDIÇOADA';h=38
    pool=panel(sheet,h,4,20,'FAMÍLIAS CUSTOM','Escolha Livre, Neutra ou Fechada. Usa os mesmos limites e custos das Famílias do livro.')
    for group in abas[sheet]['grupos']['linhas']:
        if group[:2]==[11,37]:
            group[1]=51
    for ca,cb,label in [(4,14,'FAMÍLIA'),(15,20,'ESTADO')]:
        box(sheet,h+2,ca,cb,f'=IF(COUNTIF({pool},"?*")=0,"","{label}")','rotulo')
    for g in criacao['familias']:
        n=g['n'];row=h+2+n;dr=n+1
        name=f'D{row}';state=f'O{row}';cfg=horizontal(g['estado'])
        box(sheet,row,4,14,f"='DADOS_CRIACAO'!$H${n+10}")
        # Independent name validity avoids a cycle through the state catalogue.
        raw=f"'DADOS_CRIACAO'!$B${dr}"
        valid=f'AND(ISTEXT({raw}),{raw}<>"",TRIM({raw})={raw},COUNTIF(\'DADOS_CRIACAO\'!$B$2:$B$11,{criterio(raw)})=1,COUNTIF(\'DADOS_CRIACAO\'!$H$2:$H$10,{criterio(raw)})=0)'
        box(sheet,row,15,20,f'=IF({valid},"Neutra","")')
        abas[sheet].setdefault('livres',[]).append(state)
        menu(sheet,state,"'DADOS_CRIACAO'!$M$2:$M$4")
        put('CONFIGURAÇÃO',cfg,f'=IF(\'{sheet}\'!{state}="","Neutra",\'{sheet}\'!{state})')
        label=horizontal(L(g['c'])+str(g['r']+5))
        put('CONFIGURAÇÃO',label,'ESTADO NA FICHA')
        for m in list(abas['CONFIGURAÇÃO']['menus']):
            if m['onde']==cfg:
                abas['CONFIGURAÇÃO']['menus'].remove(m)
        abas['CONFIGURAÇÃO']['notas'].pop(cfg,None)
        abas['CONFIGURAÇÃO']['menus_estritos']=[x for x in abas['CONFIGURAÇÃO'].get('menus_estritos',[]) if x!=cfg]
        audit['transferencias'].append(dict(aba='CONFIGURAÇÃO',de=cfg,aba_destino=sheet,para=state,tipo='Família',n=n,campo='estado'))

    # Each entity's list edits the existing nine slots via the onEdit controller.
    # The controls are mirrors, not a second set of mechanical choices.
    sheet='INVOCAÇÕES';controls=[]
    for i,g in enumerate(entidades):
        h=linha(sheet,g['r']+42);b=g['blocos'][1]
        pool=panel(sheet,h,b[0],b[4],'FAMÍLIAS CUSTOM','Livre conta como aberta. As escolhas usam as vagas e os limites desta entidade.',group=i<6)
        slots=[coord(sheet,c) for c in g['fam']]
        livre=f"'DADOS_INVOC'!$RA${i+2}"
        maximum=f"'DADOS_INVOC'!${L(inv['colf']['maxfam'])}${i+2}"
        for ca,cb,label in [(b[0],b[2],'FAMÍLIA'),(b[3],b[4],'ESTADO')]:
            box(sheet,h+2,ca,cb,f'=IF(COUNTIF({pool},"?*")=0,"","{label}")','rotulo')
        rows=[]
        for n in range(1,11):
            row=h+2+n
            name=box(sheet,row,b[0],b[2],f"='DADOS_CRIACAO'!$H${n+10}")
            branches=','.join(f'{slot}={name},IF({livre}>={ORDEM.index(j)+1},"Livre","Aberta")' for j,slot in enumerate(slots))
            f=f'=IF({name}="","",IFS({branches},TRUE,"Não escolhida"))'
            state=box(sheet,row,b[3],b[4],f)
            # onEdit restores this control itself, after translating the choice
            # into the existing slots. The generic formula guard must skip it.
            abas[sheet].setdefault('livres',[]).append(state)
            menu(sheet,state,'"Não escolhida,Livre,Aberta"')
            rows.append(dict(nome=name,estado=state,formula=f))
        controls.append(dict(entidade=i+1,vagas=slots,ordem=ORDEM,livres=livre,limite=maximum,linhas=rows))
    abas[sheet]['familias_custom']=controls
    for sheet in INSERCOES:
        abas[sheet]['extensoes_custom']=True
    return audit
