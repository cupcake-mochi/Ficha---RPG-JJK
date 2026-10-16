"""Nove vagas de Família e autonomia individual das doze entidades.

Conserva as cinco entradas antigas, os limites publicados e os endereços das
demais contas. As quatro entradas extras ficam ao fim de DADOS_INVOC, evitando
deslocar a tabela inteira e as fontes já publicadas para o leitor da ANALISE.
CONFIGURAÇÃO altera limites e ganhos; a escolha de autonomia pertence à entidade.
"""
import indice_ficha as ix
import ficha_invocacoes as iv

CAPACIDADE = 9
NOTA_AUTONOMIA = (
    'Regra do sistema prevista para o Guia de Criação; ainda não abordada no livro de regras atual. '
    'Autônoma é o padrão e mantém o funcionamento atual. '
    'Não autônoma recebe uma Família Livre adicional, que é uma nova Família aberta, '
    'e precisa de ordem prévia para qualquer ação, exceto a Reação. '
    'Os ganhos podem ser alterados em CONFIGURAÇÃO. A ficha calcula as Famílias; '
    'as ordens são controladas durante o jogo.'
)
REGRAS = [
    ('abertas_padrao', 'Abertas · Autônoma · padrão', 3),
    ('livres_padrao', 'Livres · Autônoma · padrão', 1),
    ('abertas_parceria', 'Abertas · Parceria / Múltiplas', 4),
    ('livres_parceria', 'Livres · Parceria / Múltiplas', 1),
    ('abertas_principal', 'Abertas · Invocação Principal', 5),
    ('livres_principal', 'Livres · Invocação Principal', 2),
    ('livres_nao_autonoma', 'Não autônoma · Livres adicionais', 1),
]
REGRA_LINHAS = {key: 139+i for i, (key, _, _) in enumerate(REGRAS)}


def amplia_countif(formula, faixa, extra):
    """Soma a faixa extra somente nos COUNTIF que leem a faixa exata indicada."""
    token = 'COUNTIF('+faixa+','
    offset = 0
    while True:
        start = formula.find(token, offset)
        if start < 0:
            return formula
        depth, quoted, end = 1, False, start+len('COUNTIF(')
        while depth:
            ch = formula[end]
            if ch == '"':
                quoted = not quoted
            if not quoted:
                depth += (ch == '(') - (ch == ')')
            end += 1
        call = formula[start:end]
        replacement = '('+call+'+'+call.replace(token, 'COUNTIF('+extra+',', 1)+')'
        formula = formula[:start]+replacement+formula[end:]
        offset = start+len(replacement)


def aplica(layout, fiv):
    aba = ix._aba(layout, iv.NOME)
    dados = ix._aba(layout, iv.DADOS_IV)
    config = ix._aba(layout, 'CONFIGURAÇÃO')
    cells = {a['nome']: {c[0]: c for c in a['celulas']} for a in (aba, dados, config)}
    tr = dict(antes={}, depois={}, entradas=[], autonomias=[], regras=[])

    def put(sheet, coord, value, style=None):
        old = cells[sheet].get(coord, [coord, None, style])
        if old[1] != value:
            tr['antes'].setdefault(sheet, {})[coord] = old[1]
            tr['depois'].setdefault(sheet, {})[coord] = value
        if coord not in cells[sheet]:
            ix._aba(layout, sheet)['celulas'].append(old)
            cells[sheet][coord] = old
        old[1] = value
        if style is not None:
            old[2] = style

    first = dados['colunas']+1
    for j in range(CAPACIDADE-5):
        put(iv.DADOS_IV, ix._letras(first+j)+'1', 'família extra '+str(j+6))
        fiv['colf']['f'+str(j+5)] = first+j
        fiv['nomes_f'].append('f'+str(j+5))
    dados['colunas'] += CAPACIDADE-5
    ca, cl, cf = dados['colunas']+1, dados['colunas']+2, dados['colunas']+3
    dados['colunas'] += 11  # modo efetivo, limite Livre e nove Famílias Livres
    dados['colunas_larg'][0][1] = dados['colunas']
    f = iv._Folha(layout)
    family_menu = fiv['D'].faixa('familias', aba=iv.DI)
    all_rows = len(fiv['fichas_c'])
    put(iv.DADOS_IV, ix._letras(ca)+'1', 'autonomia efetiva')
    put(iv.DADOS_IV, ix._letras(cl)+'1', 'limite de Famílias Livres')
    for j in range(CAPACIDADE):
        put(iv.DADOS_IV, ix._letras(cf+j)+'1', 'Família Livre efetiva '+str(j+1))

    # Complemento aprovado em grade. Não existe seletor global de autonomia.
    styles = {c[0]: c[2] for c in config['celulas']}
    def cfg(coord, value, style='C11', end=None, note=NOTA_AUTONOMIA):
        if cells['CONFIGURAÇÃO'].get(coord, [None, None])[1] not in (None, ''):
            raise ValueError('Área de limites de entidade ocupada: '+coord)
        put('CONFIGURAÇÃO', coord, value, styles[style])
        config['notas'][coord] = note
        if end:
            config['mescladas'].append(coord+':'+end)
    cfg('B133', 'INVOCAÇÕES · FAMÍLIAS', 'B9', 'G134')
    cfg('B135', 'Autonomia é escolhida em cada entidade. Em branco usa o sistema. '
        'Não autônoma: ganho previsto para o Guia de Criação.', 'B5', 'G136')
    for coord, label, end in [('B138','REGRA','D138'), ('E138','SISTEMA',None),
                              ('F138','CAMPANHA',None), ('G138','EM USO',None)]:
        cfg(coord, label, 'B10', end)
    for key, label, default in REGRAS:
        r = REGRA_LINHAS[key]
        note = ('Livres fazem parte do total de Famílias abertas. Inteiro de 0 a 9. '
                'O ganho da Não autônoma soma ao total e às Livres. '+NOTA_AUTONOMIA)
        cfg('B'+str(r), label, end='D'+str(r), note=note)
        cfg('E'+str(r), default, 'E11', note=note)
        cfg('F'+str(r), None, 'E11', note=note)
        check = f'AND(ISNUMBER(F{r}),F{r}>=0,F{r}<={CAPACIDADE},INT(F{r})=F{r})'
        cfg('G'+str(r), f'=IF(ISBLANK(F{r}),E{r},IF(IFERROR({check},FALSE),F{r},NA()))', 'F46', note=note)
        config['menus'].append(dict(onde='F'+str(r), tipo='custom',
            formula=f'OR(ISBLANK(F{r}),IFERROR({check},FALSE))', vazio_ok=True, mostra_seta=False))
        tr['regras'].append((key, r))
    cfg('B147', 'Nove espaços não concedem nove Famílias. Livre conta como aberta. '
        'Limites incompatíveis ou acima da capacidade geram aviso na entidade.', 'B5', 'G149')

    def regra(key):
        return "'CONFIGURAÇÃO'!$G$"+str(REGRA_LINHAS[key])
    def perfil(prefix):
        trail = fiv['H']['trilha']
        return f'IF({trail}="{iv.PRINCIPAL}",{regra(prefix+"_principal")},IF(OR({trail}="{iv.PARCERIA}",{trail}="{iv.MULTIPLAS}"),{regra(prefix+"_parceria")},{regra(prefix+"_padrao")}))'

    for i, g in enumerate(fiv['fichas_c']):
        row, b = g['r'], g['blocos'][1]
        # Reduz só a altura das cinco caixas antigas. Seus cantos de entrada
        # continuam nos mesmos endereços; duas caixas largas cabem na folga.
        for c in b:
            old = iv._a1(c, row+39)+':'+iv._a1(c, row+40)
            if old not in aba['mescladas']:
                raise ValueError('Mesclagem de Família mudou: '+old)
            aba['mescladas'].remove(old)
        # Duas linhas de texto continuam cabendo nas cinco entradas antigas.
        # As fileiras são compartilhadas pelas duas colunas de entidades.
        if i < 6:
            aba['linhas_alt'].extend([[row+39, 24], [row+40, 15], [row+41, 24]])
        note = ('Espaço adicional de Família. Continua sujeito ao limite de Famílias abertas da entidade. '
                'Nove caixas disponíveis não concedem nove escolhas. Livre conta no total aberto. '
                'A categoria de cada espaço aparece no rótulo acima; os limites vêm de CONFIGURAÇÃO.')
        for j, (c1, c2) in enumerate(((b[0], b[0]), (b[1], b[1]), (b[2], b[2]), (b[3], b[4])), 6):
            f.add('rot', c1, row+40, c2, row+40, 'FAMÍLIA '+str(j), note)
            coord = f.add('cel', c1, row+41, c2, row+41, None, note)
            g['fam'].append(coord)
            f.menu(coord, family_menu)
            put(iv.DADOS_IV, ix._letras(first+j-6)+str(i+2),
                f'={iv._A(coord, iv.IV)}&""')
            tr['entradas'].append((f'invocacao.{i+1}.familia.{j}', coord))

        core = f"${ix._letras(fiv['colf']['f0'])}{i+2}:${ix._letras(fiv['colf']['f4'])}{i+2}"
        extra = f'${ix._letras(first)}{i+2}:${ix._letras(first+CAPACIDADE-6)}{i+2}'
        nfam = iv._a1(fiv['colf']['nfam'], i+2)
        old = cells[iv.DADOS_IV][nfam][1]
        if old != '=COUNTIF('+core+',"?*")':
            raise ValueError('Contagem de Famílias mudou: '+old)
        put(iv.DADOS_IV, nfam, amplia_countif(old, core, extra))
        rep = iv._a1(fiv['colf']['rep'], i+2)
        formula = amplia_countif(cells[iv.DADOS_IV][rep][1], core, extra)
        for c in range(first, first+CAPACIDADE-5):
            ref = iv._abs(c, i+2)
            formula += f'+IF({ref}="",0,IF(COUNTIF({core},{ref})+COUNTIF({extra},{ref})>1,1,0))'
        put(iv.DADOS_IV, rep, formula)

        # Listas de Forma/Melhoria da entidade leem as nove escolhas.
        core = iv._faixa(fiv['colf']['f0'], i+2, fiv['colf']['f4'], i+2)
        extra = iv._faixa(first, i+2, first+CAPACIDADE-6, i+2)
        for name in ('menu'+str(i), 'menuf'+str(i)):
            begin = fiv['D'].T[name][0]
            for r in range(2, 2+len(fiv['R']['pecas'] if name.startswith('menu') and not name.startswith('menuf') else fiv['R']['formas'])):
                for c in (begin, begin+1):
                    coord = iv._a1(c, r)
                    old = cells[iv.DADOS_IV][coord][1]
                    new = amplia_countif(old, core, extra)
                    if old == new:
                        raise ValueError('Menu não lê a Família esperada: '+coord)
                    put(iv.DADOS_IV, coord, new)

        # Reaproveita a linha vazia abaixo da aquisição, em cada ficha.
        a, _, c = g['blocos']
        g['autonomia'] = iv._a1(a[2], row+41)
        f.add('rot', a[0], row+41, a[1], row+41, 'AUTONOMIA', NOTA_AUTONOMIA)
        f.add('cel', a[2], row+41, a[4], row+41, 'Autônoma', NOTA_AUTONOMIA)
        f.menu(g['autonomia'], '"Autônoma,Não autônoma"')
        mode, livres = iv._abs(ca, i+2), iv._abs(cl, i+2)
        put(iv.DADOS_IV, iv._a1(ca, i+2), f'=IF({iv._A(g["autonomia"], iv.IV)}="","Autônoma",{iv._A(g["autonomia"], iv.IV)})')
        bonus = f'IF({mode}="Não autônoma",{regra("livres_nao_autonoma")},0)'
        maximum = iv._a1(fiv['colf']['maxfam'], i+2)
        put(iv.DADOS_IV, maximum, '='+perfil('abertas')+'+'+bonus)
        put(iv.DADOS_IV, iv._a1(cl, i+2), '='+perfil('livres')+'+'+bonus)
        # As antigas vagas Livre/Trilha conservam prioridade; as quatro novas
        # permitem ampliar Livres sem mudar as cinco entradas já preenchidas.
        order = [0, 1, 5, 6, 7, 8, 2, 3, 4]
        for j, fam in enumerate(g['fam']):
            rank = order.index(j)+1
            helper = iv._a1(cf+j, i+2)
            ref = iv._abs(fiv['colf']['f'+str(j)], i+2)
            put(iv.DADOS_IV, helper, f'=IF({livres}>={rank},{ref},"")')
            rr, cc = ix._lc(fam)
            label = iv._a1(cc, rr-1)
            label_livres = iv._abs(cl, i+2, iv.DI)
            value = f'=IF({label_livres}>={rank},"LIVRE","ABERTA")'
            if j >= 5:
                value = f'=IF({label_livres}>={rank},"LIVRE {j+1}","FAMÍLIA {j+1}")'
            # f.cel será incorporado no fim; registrar o rótulo já desenhado.
            if label in f.cel:
                f.cel[label] = (value, f.cel[label][1])
            else:
                put(iv.NOME, label, value)
            aba['notas'][label] = note
        fam_note = NOTA_AUTONOMIA+' Nove espaços físicos. Livres estão incluídas no total aberto.'
        aba['notas'][g['fam_rot']] = fam_note
        maxref = iv._abs(fiv['colf']['maxfam'], i+2)
        d_fam = iv._a1(fiv['colf']['d_fam'], i+2)
        old = cells[iv.DADOS_IV][d_fam][1]
        put(iv.DADOS_IV, d_fam, old+f'&IF(OR({livres}>{maxref},{maxref}>{CAPACIDADE})," · LIMITES INCOMPATÍVEIS","")')
        domain = iv._a1(fiv['colf']['d_ea'], i+2)
        old = cells[iv.DADOS_IV][domain][1]
        fam_ines = f'IFERROR(VLOOKUP("{iv.INESCAPAVEL}",{fiv["D"].faixa("pecas")},2,FALSE),"")'
        token = f'OR({fam_ines}=${ix._letras(fiv["colf"]["f0"])}{i+2},{fam_ines}=${ix._letras(fiv["colf"]["f1"])}{i+2})'
        if token not in old:
            raise ValueError('Desconto de Inescapável mudou: '+domain)
        put(iv.DADOS_IV, domain, old.replace(token, f'COUNTIF({iv._faixa(cf,i+2,cf+8,i+2)},{fam_ines})>0'))
        tr['autonomias'].append((i+1, g['autonomia'], iv._a1(fiv['colf']['maxfam'],i+2), iv._a1(cl,i+2)))

        # Abre uma linha de respiro acima de DEFINIÇÃO sem deslocar habilidades.
        # A antiga linha vazia de baixo recebe o fim da caixa de texto.
        low, high = row+42, row+44
        snapshot = {coord: value[:] for coord, value in cells[iv.NOME].items()
                    if low <= ix._lc(coord)[0] <= high and a[0] <= ix._lc(coord)[1] <= c[4]}
        for cc in range(a[0], c[4]+1):
            blank = cells[iv.NOME].get(iv._a1(cc,row+45), [None,None,None])
            if blank[1] is not None:
                raise ValueError('Respiro da definição ocupado')
            put(iv.NOME, iv._a1(cc,low), None, blank[2])
        for coord, (_, value, style) in sorted(snapshot.items(), key=lambda item: ix._lc(item[0])[0], reverse=True):
            rr, cc = ix._lc(coord)
            put(iv.NOME, iv._a1(cc,rr+1), value, style)
        for idx, merge in enumerate(aba['mescladas']):
            (r1,c1),(r2,c2) = map(ix._lc,merge.split(':'))
            if low<=r1<=r2<=high and a[0]<=c1<=c2<=c[4]:
                aba['mescladas'][idx] = iv._a1(c1,r1+1)+':'+iv._a1(c2,r2+1)
        for coord in sorted(list(aba['notas']), key=lambda co: ix._lc(co)[0], reverse=True):
            rr, cc = ix._lc(coord)
            if low<=rr<=high and a[0]<=cc<=c[4]:
                aba['notas'][iv._a1(cc,rr+1)] = aba['notas'].pop(coord)
        g['def'] = iv._a1(a[0],row+44)

    # Verificações de Família Fechada nas 156 aplicações usam as quatro extras.
    core_table = iv._faixa(fiv['colf']['f0'], 2, fiv['colf']['f4'], all_rows+1)
    extra_table = iv._faixa(first, 2, first+CAPACIDADE-6, all_rows+1)
    for i in range(len(fiv['cartas'])):
        r = i+2
        fi = '$'+ix._letras(fiv['col']['ficha'])+str(r)
        core = f'INDEX({core_table},{fi},0)'
        extra = f'INDEX({extra_table},{fi},0)'
        for key in ('x0', 'x1', 'x2', 'x3', 'x4'):
            coord = iv._a1(fiv['col'][key], r)
            old = cells[iv.DADOS_IV][coord][1]
            new = amplia_countif(old, core, extra)
            if old == new:
                raise ValueError('Aplicação não lê a Família esperada: '+coord)
            put(iv.DADOS_IV, coord, new)
        for k in range(1, iv.N_MEL+1):
            coord = iv._a1(fiv['col']['k'+str(k)], r)
            old = cells[iv.DADOS_IV][coord][1]
            fk = '$'+ix._letras(fiv['col']['f'+str(k)])+str(r)
            f0 = f'INDEX({iv._faixa(fiv["colf"]["f0"],2,fiv["colf"]["f0"],13)},{fi})'
            f1 = f'INDEX({iv._faixa(fiv["colf"]["f1"],2,fiv["colf"]["f1"],13)},{fi})'
            token = f'OR({fk}={f0},{fk}={f1})'
            if token not in old:
                raise ValueError('Desconto de Melhoria mudou: '+coord)
            free = f'INDEX({iv._faixa(cf,2,cf+8,13)},{fi},0)'
            put(iv.DADOS_IV,coord,old.replace(token,f'COUNTIF({free},{fk})>0'))

    for coord, (value, style) in f.cel.items():
        put(iv.NOME, coord, value, style)
    aba['mescladas'].extend(f.mesclas)
    aba['notas'].update(f.notas)
    for formula, where in f.menus.items():
        aba['menus'].append(dict(onde=' '.join(where), tipo='list', formula=formula,
                                 vazio_ok=True, mostra_seta=True))
    return tr


def exporta(tr):
    # Acrescenta as chaves depois das já publicadas, conservando a ordem antiga.
    out = []
    # Mantém as 24 chaves 6/7 já publicadas na mesma ordem, antes de 8/9.
    entries = [v for v in tr['entradas'] if int(v[0].split('.')[-1])<=7]+[v for v in tr['entradas'] if int(v[0].split('.')[-1])>7]
    for key, coord in entries:
        ref = iv._A(coord, iv.IV)
        out.append([key, f'=IF(ISBLANK({ref}),"",{ref}&"")', ref.replace('$', ''), 'entrada'])
    for n, coord, maximum, livres in tr['autonomias']:
        ref = iv._A(coord, iv.IV)
        out.append([f'invocacao.{n}.autonomia', f'=IF({ref}="","Autônoma",{ref}&"")', ref.replace('$',''), 'entrada'])
        for key, cell in [('limite_familias',maximum), ('limite_livres',livres)]:
            ref = iv._A(cell,iv.DI)
            out.append([f'invocacao.{n}.{key}', '='+ref, ref.replace('$',''), 'resultado'])
    for key,r in tr['regras']:
        for suffix,col in [('', 'G'),('.campanha','F')]:
            ref=f"'CONFIGURAÇÃO'!${col}${r}"
            out.append(['regra.invocacao_familias_'+key+suffix,
                        f'=IF(ISBLANK({ref}),"",{ref})',ref.replace('$',''),'configuração'])
    return out
