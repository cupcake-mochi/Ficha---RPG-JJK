"""Tipos de dano custom: nomes nos menus; descrição não executa mecânica."""
from copy import deepcopy

import indice_ficha as ix
import ficha_invocacoes as iv
from capacidades import DANOS
from custom_criacao import criterio, ref, troca_refs
from custom_pecas import coord, faixa

NOME = 'DADOS_DANOS'
PASSO = 28


def registros(inicio, capacidade=DANOS):
    if isinstance(capacidade, bool) or not isinstance(capacidade, int) or capacidade < 1:
        raise ValueError('Capacidade de dano precisa ser inteiro positivo')
    out = []
    for n in range(1, capacidade + 1):
        r, c = inicio + ((n - 1) // 2) * PASSO, 2 if n % 2 else 10
        out.append(dict(n=n, r=r, c=c, nome=coord(r+2, c),
                        mestre_viu=coord(r+2, c+4), definicao=coord(r+6, c),
                        efeito=coord(r+13, c)))
    return out


def aplica(layout, contexto):
    if any(a['nome'] == NOME for a in layout['abas']):
        raise ValueError('Catálogo de dano aplicado duas vezes')
    config = ix._aba(layout, 'CONFIGURAÇÃO')
    inicio = config['linhas'] + 4
    regs = registros(inicio, contexto.get('capacidades', {}).get('dano', DANOS))
    fim = regs[-1]['r'] + 26
    book = list(contexto['inv']['R']['LIV']['tipos_de_dano'])
    if len(set(book)) != len(book):
        raise ValueError('Livro contém tipos de dano duplicados')
    data = dict(nome=NOME, estado='hidden', linhas=len(book)+len(regs)+1,
                colunas=13, padrao=['Roboto', 10, '#000000'], fundo_base='#FFFFFF',
                grade=False, celulas=[], mescladas=[], menus=[], condicional=[],
                imagens=[], colunas_larg=[], linhas_alt=[], altura_padrao=15.75,
                paleta_fixa=True, validacao_em_matriz=True)
    layout['abas'].append(data)
    cells = {a['nome']: {v[0]: v for v in a['celulas']} for a in layout['abas']}
    tr = dict(antes={}, depois={}, entradas=[], registros=regs, inicio=inicio,
              fim=fim, catalogos={'dano': faixa(NOME, 10, 2, 12, data['linhas'])},
              consumidores={}, substituicoes=0)

    def put(sheet, a1, value, style=None):
        old = cells[sheet].get(a1)
        before = old[1] if old else None
        if before != value:
            tr['antes'].setdefault(sheet, {}).setdefault(a1, before)
            tr['depois'].setdefault(sheet, {})[a1] = value
        if old is None:
            old = [a1, value, style]
            cells[sheet][a1] = old
            ix._aba(layout, sheet)['celulas'].append(old)
        else:
            old[1] = value
            if style is not None:
                old[2] = style

    styles = {v[0]: v[2] for v in config['celulas']}
    st = dict(secao=styles['B9'], rotulo=styles['B10'], entrada=styles['C11'],
              caixa=styles['B11'], nota=styles['B5'])
    wrap = deepcopy(layout['estilos'][st['entrada']])
    wrap[3] = ['left', 'top', True, 0]
    if wrap not in layout['estilos']:
        layout['estilos'].append(wrap)
    st['texto'] = layout['estilos'].index(wrap)

    def box(r, c, value=None, er=None, ec=None, kind='entrada', note=None):
        a1, end = coord(r, c), coord(er or r, ec or c)
        if a1 in cells['CONFIGURAÇÃO']:
            raise ValueError('Cadastro sobrepõe CONFIGURAÇÃO!'+a1)
        put('CONFIGURAÇÃO', a1, value, st[kind])
        if a1 != end:
            config['mescladas'].append(a1+':'+end)
        if note:
            config.setdefault('notas', {})[a1] = note

    headers = {'A1': 'registro', 'D1': 'nome', 'E1': 'mestre viu',
               'F1': 'definição', 'G1': 'efeito e requisitos', 'H1': 'aviso',
               'J1': 'tipo de dano', 'K1': 'definição', 'L1': 'efeito e requisitos',
               'M1': 'tipos do livro'}
    for a1, value in headers.items():
        put(NOME, a1, value)
    for r, name in enumerate(book, 2):
        put(NOME, 'M'+str(r), name)
        put(NOME, 'J'+str(r), '=M'+str(r))
    book_names = faixa(NOME, 13, 2, 13, len(book)+1)
    for g in regs:
        r, dst = g['n']+1, len(book)+g['n']+1
        put(NOME, 'A'+str(r), g['n'])
        for key, col in [('nome', 'D'), ('mestre_viu', 'E'), ('definicao', 'F'), ('efeito', 'G')]:
            source = ref(g[key], 'CONFIGURAÇÃO')
            put(NOME, col+str(r), f'=IF(ISBLANK({source}),"",{source})')
            tr['entradas'].append((f'custom.dano.{g["n"]}.{key}', g[key], key == 'mestre_viu'))
        errors = [f'IF(OR(NOT(ISTEXT(D{r})),TRIM(D{r})<>D{r}),"NOME precisa ser texto sem espaços nas pontas","")',
                  f'IF(COUNTIF($D$2:$D${len(regs)+1},{criterio("D"+str(r))})+COUNTIF({book_names},{criterio("D"+str(r))})>1,"Nome repetido no livro ou custom","")',
                  f'IF(ISLOGICAL(E{r}),"","MESTRE VIU deve ser caixa de seleção")']
        partial = f'OR(F{r}<>"",G{r}<>"",E{r}=TRUE)'
        put(NOME, 'H'+str(r), f'=IF(D{r}="",IF({partial},"Preencha NOME",""),TEXTJOIN(" · ",TRUE,{",".join(errors)}))')
        valid = f'AND(D{r}<>"",H{r}="")'
        put(NOME, 'J'+str(dst), f'=IF({valid},D{r},"")')
        put(NOME, 'K'+str(dst), f'=IF(J{dst}="","",F{r})')
        put(NOME, 'L'+str(dst), f'=IF(J{dst}="","",G{r})')
        rr, c = g['r'], g['c']
        box(rr, c, 'TIPO DE DANO · '+str(g['n']), ec=c+5, kind='secao')
        box(rr+1, c, 'NOME', ec=c+3, kind='rotulo')
        box(rr+1, c+4, 'MESTRE VIU', ec=c+5, kind='rotulo')
        box(rr+2, c, ec=c+3, note='Nome único. Livro e cadastros válidos aparecem juntos nos menus.')
        box(rr+2, c+4, False, ec=c+5, kind='caixa', note='Lembrete; aprovação ocorre pelo bot no chat.')
        box(rr+5, c, 'DEFINIÇÃO', ec=c+5, kind='rotulo')
        box(rr+6, c, er=rr+10, ec=c+5, kind='texto', note='Natureza do dano criada com o mestre. Não altera números automaticamente.')
        box(rr+12, c, 'EFEITO E REQUISITOS', ec=c+5, kind='rotulo')
        box(rr+13, c, er=rr+24, ec=c+5, kind='texto', note='Interações e requisitos. Resistência, vulnerabilidade e dano aplicado não são deduzidos deste texto.')
        box(rr+25, c, f'=IF({ref("H"+str(r),NOME)}="","","⚠ "&{ref("H"+str(r),NOME)})', er=rr+26, ec=c+5, kind='nota')

    # O pool 3a já é usado por fórmulas INDIRECT e validações dinâmicas.
    # Atualizar sua fonte preserva esses consumidores, inclusive suas strings.
    pool = contexto['custom']['pools']['danos']
    owner, address = pool.rsplit('!', 1)
    owner = owner.strip("'")
    first, last = address.replace('$', '').split(':')
    row, col = ix._lc(first)
    last_row, _ = ix._lc(last)
    if len(book)+len(regs) > last_row-row+1:
        raise ValueError('Catálogo de dano excede o pool 3a')
    for i in range(len(book)+len(regs)):
        source = ref('J'+str(i+2), NOME)
        put(owner, coord(row+i, col), f'=IF({source}="","",{source})')
    old_col, old_first, old_last, old_width = contexto['inv']['D'].T['danos']
    source = faixa(iv.DADOS_IV, old_col, old_first, old_col+old_width-1, old_last)
    src_owner, src_addr = source.rsplit('!', 1)
    unified = faixa(NOME, 10, 2, 10, data['linhas'])
    mapping = {(src_owner.strip("'"), src_addr.replace('$', '')): unified}
    for aba in layout['abas']:
        if aba['nome'] == NOME:
            continue
        for cell in list(aba['celulas']):
            changed = troca_refs(cell[1], aba['nome'], mapping)
            if changed != cell[1]:
                put(aba['nome'], cell[0], changed)
                tr['substituicoes'] += 1
        for menu in aba['menus']:
            before = menu['formula']
            menu['formula'] = troca_refs('='+before, aba['nome'], mapping)[1:]
            if before != menu['formula']:
                tr['consumidores'].setdefault(aba['nome'], []).append(menu['onde'])
    # A caixa livre de tipo de dano da técnica mantém a digitação autorizada.
    box(inicio-2, 2, 'TIPOS DE DANO CUSTOM', ec=15, kind='secao')
    config['linhas'] = fim
    config['linhas_alt'] += [[r, 18.75] for r in range(inicio-2, fim+1)]
    # Copiar só pares completos; uma capacidade ímpar pode deixar o último sem par.
    pair_count = len(regs)//2
    if pair_count > 1:
        config.setdefault('copias', []).append([inicio, inicio+PASSO-2,
            [inicio+i*PASSO for i in range(1, pair_count)], 2, 15, [[2,7],[10,15]], True])
    for i in range(0, len(regs), 2):
        pair = regs[i:i+2]
        for key, offset, height in [('definicao', 6, 5), ('efeito', 13, 12)]:
            texts = []
            for g in pair:
                width = sum(next((w for lo,hi,w in config['colunas_larg'] if lo <= c <= hi), 4)*8-1
                            for c in range(g['c'], g['c']+6))-12
                texts.append([width, [g[key]], g['r']+offset, height, 0])
            config.setdefault('esticam', []).append(dict(gatilhos=[g[key] for g in pair],
                aba='CONFIGURAÇÃO', minima=25, textos=texts))
    return tr


def exporta(tr):
    out = []
    for key, a1, boolean in tr['entradas']:
        source = ref(a1, 'CONFIGURAÇÃO')
        value = f'=N({source})&""' if boolean else f'=IF(ISBLANK({source}),"",{source}&"")'
        out.append([key, value, source.replace('$', ''), 'configuração'])
    for g in tr['registros']:
        source = ref('H'+str(g['n']+1), NOME)
        out.append([f'aviso.custom.dano.{g["n"]}', '='+source+'&""', source.replace('$', ''), 'aviso'])
    return out
