"""Parte 3c: catálogos custom e limites de Famílias aprovados.

Os estados da técnica e as Famílias abertas das entidades são independentes.
Nenhuma descrição é executada como regra. Catálogos excluem registros inválidos,
mas a ANALISE conserva as entradas e os respectivos avisos.
"""
import json
import re
from copy import deepcopy
from pathlib import Path
from openpyxl.formula import Tokenizer
import indice_ficha as ix
import ficha_amaldicoada as fa

ROOT = Path(__file__).resolve().parent.parent
NOME = 'DADOS_CRIACAO'
from capacidades import FAMILIAS, INICIO_FAMILIAS
INICIO, PASSO = INICIO_FAMILIAS, 14
REGRAS = {'livres': 157, 'fechadas': 158, 'neutras': 159, 'total': 160}


def q(value):
    return '"'+str(value).replace('"', '""')+'"'


def ref(coord, sheet=NOME):
    r, c = ix._lc(coord)
    return "'"+sheet+"'!$"+ix._letras(c)+'$'+str(r)


def familia(n):
    if not 1 <= n <= FAMILIAS:
        raise ValueError('Família fora da capacidade aprovada')
    r, c = INICIO + ((n-1)//2)*PASSO, 2 if n % 2 else 10
    L = ix._letras
    return dict(n=n, r=r, c=c, nome=f'{L(c)}{r+4}', mestre_viu=f'{L(c+4)}{r+2}',
                estado=f'{L(c+3)}{r+5}', descricao=f'{L(c)}{r+7}', aviso=f'{L(c)}{r+12}')


def criterio(value):
    """COUNTIF trata nomes como texto literal, inclusive * ? e ~."""
    return f'SUBSTITUTE(SUBSTITUTE(SUBSTITUTE({value},"~","~~"),"*","~*"),"?","~?")'


def troca_refs(formula, sheet, mapping):
    """Reescreve apenas referências, preservando literais e a aba implícita."""
    if not isinstance(formula, str) or not formula.startswith('='):
        return formula
    out = []
    for t in Tokenizer(formula).items:
        value = t.value
        if t.type == 'OPERAND' and t.subtype == 'RANGE':
            if '!' in value:
                owner, address = value.rsplit('!', 1)
                owner = owner.strip("'").replace("''", "'")
            else:
                owner, address = sheet, value
            value = mapping.get((owner, address.replace('$', '')), value)
        out.append(value)
    return '='+''.join(out)


def aplica(layout, fam, inv):
    config = ix._aba(layout, 'CONFIGURAÇÃO')
    prior_end = config['linhas']
    if prior_end >= INICIO:
        raise ValueError('Área de custom 3c já ocupada')
    styles = {v[0]: v[2] for v in config['celulas']}
    st = dict(fundo=styles['A1'], secao=styles['B9'], rotulo=styles['B10'],
              entrada=styles['C11'], caixa=styles['B11'], nota=styles['B5'], numero=styles['E11'])
    wrap = deepcopy(layout['estilos'][st['entrada']])
    wrap[3] = ['left', 'top', True, 0]
    if wrap not in layout['estilos']:
        layout['estilos'].append(wrap)
    st['texto'] = layout['estilos'].index(wrap)
    data = dict(nome=NOME, estado='hidden', linhas=FAMILIAS+10, colunas=15,
                padrao=['Roboto', 10, '#000000'], fundo_base='#FFFFFF', grade=False,
                celulas=[], mescladas=[], menus=[], condicional=[], imagens=[],
                colunas_larg=[], linhas_alt=[], altura_padrao=15.75, paleta_fixa=True,
                validacao_em_matriz=True)
    layout['abas'].append(data)
    cells = {a['nome']: {v[0]: v for v in a['celulas']} for a in layout['abas']}
    tr = dict(antes={}, depois={}, entradas=[], familias=[familia(n) for n in range(1, FAMILIAS+1)],
              inicio=INICIO, fim=familia(FAMILIAS)['r']+12, fim_progressao=prior_end,
              aba=data, substituicoes=0)

    def put(sheet, coord, value, style=None):
        old = cells[sheet].get(coord)
        before = old[1] if old is not None else None
        if before != value:
            tr['antes'].setdefault(sheet, {}).setdefault(coord, before)
            tr['depois'].setdefault(sheet, {})[coord] = value
        if old is None:
            old = [coord, value, style]
            cells[sheet][coord] = old
            ix._aba(layout, sheet)['celulas'].append(old)
        else:
            old[1] = value
            if style is not None:
                old[2] = style

    def d(c, value):
        put(NOME, c, value)

    def box(r, c, value=None, er=None, ec=None, kind='entrada', note=None):
        a1, end = f'{ix._letras(c)}{r}', f'{ix._letras(ec or c)}{er or r}'
        if a1 in cells['CONFIGURAÇÃO'] and cells['CONFIGURAÇÃO'][a1][1] not in (None, ''):
            raise ValueError('Área ocupada em CONFIGURAÇÃO: '+a1)
        put('CONFIGURAÇÃO', a1, value, st[kind])
        if a1 != end:
            config['mescladas'].append(a1+':'+end)
        config['notas'][a1] = note or 'Cadastro de Família custom. Nome único; estado vale para a técnica do personagem.'

    def menu(coord, source, kind='list'):
        config['menus'].append(dict(onde=coord, tipo=kind, formula=source,
                                    vazio_ok=True, mostra_seta=kind == 'list', estrito=True))
        config.setdefault('menus_estritos', []).append(coord)

    cat = json.loads((ROOT/'catalogo-projeto-m.json').read_text())
    book = list(cat['familias'])
    for i, name in enumerate(['registro', 'nome', 'estado', 'mestre viu', 'descrição', 'problema'], 1):
        d(ix._letras(i)+'1', name)
    for i, name in enumerate(['família', 'estado da técnica', 'Livre', 'Fechada'], 8):
        d(ix._letras(i)+'1', name)
    d('M1', 'estado permitido')
    for r, state in enumerate([fa.LIVRE, fa.NEUTRA, fa.FECHADA], 2):
        d('M'+str(r), state)
    raw_names = f'${"B"}$2:$B${FAMILIAS+1}'
    # Livro mantém seus nove estados nos espaços originais da técnica.
    for r, (name, (col, _)) in enumerate(zip(book, fam['G']['cols_fam']), 2):
        d('H'+str(r), name)
        d('I'+str(r), '='+ref(col+str(fam['G']['familias']+1), fa.NOME)+'&""')
        d('J'+str(r), f'=IF(I{r}="Livre",1,0)')
        d('K'+str(r), f'=IF(I{r}="Fechada",1,0)')
    for g in tr['familias']:
        r, dst = g['n']+1, len(book)+g['n']+1
        d('A'+str(r), g['n'])
        for col, key in zip('BCDE', ['nome', 'estado', 'mestre_viu', 'descricao']):
            rr = ref(g[key], 'CONFIGURAÇÃO')
            d(col+str(r), f'=IF(ISBLANK({rr}),"",{rr})')
            tr['entradas'].append((f'custom.familia.{g["n"]}.{key}', g[key], key == 'mestre_viu'))
        n, state, seen = 'B'+str(r), 'C'+str(r), 'D'+str(r)
        book_count = '+'.join(f'IF({n}={q(name)},1,0)' for name in book)
        invalid = (f'TEXTJOIN(" · ",TRUE,IF(OR(NOT(ISTEXT({n})),TRIM({n})<>{n}),"NOME precisa ser texto sem espaços nas pontas",""),'
                   f'IF(OR(COUNTIF({raw_names},{criterio(n)})>1,{book_count}>0),"Nome repetido no livro ou custom",""),'
                   f'IF(COUNTIF($M$2:$M$4,{state})<>1,"Escolha Livre, Neutra ou Fechada",""),'
                   f'IF(ISLOGICAL({seen}),"","MESTRE VIU deve ser caixa de seleção"))')
        d('F'+str(r), f'=IF({n}="",IF(OR(E{r}<>"",{seen}=TRUE,AND({state}<>"",{state}<>"Neutra")),"Preencha NOME",""),{invalid})')
        d('H'+str(dst), f'=IF(AND({n}<>"",F{r}=""),{n},"")')
        d('I'+str(dst), f'=IF(H{dst}="","",{state})')
        d('J'+str(dst), f'=IF(AND(H{dst}<>"",I{dst}="Livre"),1,0)')
        d('K'+str(dst), f'=IF(AND(H{dst}<>"",I{dst}="Fechada"),1,0)')
    end = len(book)+FAMILIAS+1
    names_range = ref('H2')+':$H$'+str(end)
    tr['catalogo_familias'] = names_range
    mapping = {}
    # Preserva a aba de cada referência, inclusive nas fórmulas locais de apoio.
    old_col, old_first, old_last, width = fam['D'].T['fam']
    for left in range(width):
        for right in range(left, width):
            old = fa._faixa(old_col+left, old_first, old_col+right, old_last).replace('$', '')
            new = ref(ix._letras(8+left)+'2')+':$'+ix._letras(8+right)+'$'+str(end)
            mapping[(fa.DADOS_AM, old)] = new
    old_iv = inv['D'].faixa('familias').replace('$', '')
    mapping[('DADOS_INVOC', old_iv)] = names_range
    for a in layout['abas']:
        if a['nome'] == NOME:
            continue
        for v in list(a['celulas']):
            new = troca_refs(v[1], a['nome'], mapping)
            if new != v[1]:
                put(a['nome'], v[0], new)
                tr['substituicoes'] += 1
        for m in a.get('menus', []):
            original = m.get('formula', '')
            m['formula'] = troca_refs('='+original, a['nome'], mapping)[1:]

    # Campanha: limites aprovados; Neutras é o saldo do catálogo válido.
    box(153, 2, 'TÉCNICA · FAMÍLIAS', er=154, ec=7, kind='secao')
    for c, label, ec in [(2, 'REGRA', 4), (5, 'LIVRO', 5), (6, 'CAMPANHA', 6), (7, 'EM USO', 7)]:
        box(156, c, label, ec=ec, kind='rotulo')
    book_limits = {'livres': cat['fundamento']['familias_livres'], 'fechadas': cat['fundamento']['familias_fechadas'],
                   'neutras': len(book)-cat['fundamento']['familias_livres']-cat['fundamento']['familias_fechadas'], 'total': len(book)}
    for key, label in [('livres', 'Famílias Livres'), ('fechadas', 'Famílias Fechadas'),
                       ('neutras', 'Famílias Neutras'), ('total', 'Famílias disponíveis')]:
        r = REGRAS[key]
        note = ('Quantidade da técnica do personagem. Não muda os limites das entidades. '
                'Campanha em branco usa o livro; Neutras é o total válido menos Livres e Fechadas.')
        box(r, 2, label, ec=4, note=note)
        box(r, 5, book_limits[key], kind='numero', note=note)
        if key in ('livres', 'fechadas'):
            box(r, 6, kind='numero', note=note)
            valid = f'AND(ISNUMBER(F{r}),F{r}>=0,INT(F{r})=F{r})'
            box(r, 7, f'=IF(ISBLANK(F{r}),E{r},IF(IFERROR({valid},FALSE),F{r},NA()))', kind='numero', note=note)
            menu('F'+str(r), f'OR(ISBLANK(F{r}),IFERROR({valid},FALSE))', 'custom')
        else:
            box(r, 6, 'saldo' if key == 'neutras' else 'catálogo', kind='entrada', note=note)
            box(r, 7, '=G160-G157-G158' if key == 'neutras' else f'=COUNTIF({names_range},"?*")', kind='numero', note=note)
    box(162, 2, '=IFERROR(IF(G159<0,"⚠ Livres + Fechadas ultrapassam o catálogo.",""),"⚠ Confira os limites das Famílias.")',
        er=164, ec=7, kind='nota', note='Aviso de quantidades incompatíveis ou de entrada inválida. Não concede Famílias adicionais.')
    summary = fam['G']['resumo_familias']
    nl, nf = (value if '!' in value else fa.DA+value
              for value in (fam['H'][key] for key in ['famílias livres', 'famílias fechadas']))
    limit_l, limit_f = ref('G157', 'CONFIGURAÇÃO'), ref('G158', 'CONFIGURAÇÃO')
    # A carta permanece um espelho simples; as contas moram na tabela de apoio.
    summary_link = cells[fa.NOME][summary][1]
    cache = re.fullmatch(r'=DADOS_AM!(\$?[A-Z]+\$?\d+)', summary_link)
    if not cache:
        raise ValueError('Resumo das Famílias sem espelho simples na DADOS_AM')
    put(fa.DADOS_AM, cache[1].replace('$', ''), f'=IF(OR({nl}<>{limit_l},{nf}<>{limit_f},{ref("G159", "CONFIGURAÇÃO")}<0),"{fa.T_ERRO} ","")'
        f'&{nl}&" de "&{limit_l}&" · "&{nf}&" de "&{limit_f}')

    config['linhas'] = tr['fim']
    for r in range(prior_end+1, tr['fim']+1):
        for c in range(1, 17):
            put('CONFIGURAÇÃO', ix._letras(c)+str(r), None, st['fundo'])
    box(INICIO-2, 2, 'FAMÍLIAS CUSTOM', ec=15, kind='secao')
    state_list = ref('M2')+':$M$4'
    for g in tr['familias']:
        r, c = g['r'], g['c']
        box(r, c, f'FAMÍLIA · {g["n"]}', ec=c+5, kind='secao')
        box(r+1, c, 'TIPO', ec=c+3, kind='rotulo')
        box(r+2, c, 'Família', ec=c+3)
        box(r+1, c+4, 'MESTRE VIU', ec=c+5, kind='rotulo')
        box(r+2, c+4, False, ec=c+5, kind='caixa', note='Lembrete marcado pelo jogador. Aprovação ocorre pelo bot no chat.')
        box(r+3, c, 'NOME', ec=c+5, kind='rotulo')
        box(r+4, c, ec=c+5)
        box(r+5, c, 'ESTADO', ec=c+2, kind='rotulo')
        box(r+5, c+3, fa.NEUTRA, ec=c+5)
        menu(g['estado'], state_list)
        box(r+6, c, 'DESCRIÇÃO', ec=c+5, kind='rotulo')
        box(r+7, c, er=r+10, ec=c+5, kind='texto', note='Tema e descrição da Família criada com o mestre.')
        box(r+12, c, f'=IF({ref("F"+str(g["n"]+1))}="","","⚠ "&{ref("F"+str(g["n"]+1))})', ec=c+5, kind='nota')
    config['linhas_alt'] += [[r, 18.75] for r in range(prior_end+1, tr['fim']+1)]
    config.setdefault('copias', []).append([INICIO, INICIO+12,
        list(range(INICIO+PASSO, tr['fim'], PASSO)), 2, 15, [[2, 7], [10, 15]], True])
    # Mesmas linhas para os dois cartões: cresce pelo texto mais comprido.
    def width(col):
        return sum(next((w for lo,hi,w in config['colunas_larg'] if lo<=c<=hi),4)*8-1
                   for c in range(col,col+6))-12
    for i in range(0,FAMILIAS,2):
        pair=tr['familias'][i:i+2]
        config.setdefault('esticam',[]).append(dict(gatilhos=[g['descricao'] for g in pair],aba='CONFIGURAÇÃO',minima=25,
            textos=[[width(g['c']),[g['descricao']],g['r']+7,4,0] for g in pair]))
    return tr


def exporta(tr):
    out = []
    for key, coord, boolean in tr['entradas']:
        rr = ref(coord, 'CONFIGURAÇÃO')
        value = f'=N({rr})&""' if boolean else f'=IF(ISBLANK({rr}),"",{rr}&"")'
        out.append([key, value, rr.replace('$', ''), 'configuração'])
    for g in tr['familias']:
        rr = ref('F'+str(g['n']+1))
        out.append([f'aviso.custom.familia.{g["n"]}', '='+rr+'&""', rr.replace('$', ''), 'aviso'])
    for key in ['livres', 'fechadas', 'neutras', 'total']:
        r = REGRAS[key]
        rr = ref('G'+str(r), 'CONFIGURAÇÃO')
        out.append(['regra.familias_'+key, '='+rr+'&""', rr.replace('$', ''), 'configuração'])
        if key in ('livres', 'fechadas'):
            rr = ref('F'+str(r), 'CONFIGURAÇÃO')
            out.append(['regra.familias_'+key+'.campanha', f'=IF(ISBLANK({rr}),"",{rr}&"")', rr.replace('$', ''), 'entrada'])
    rr = ref('B162', 'CONFIGURAÇÃO')
    out.append(['aviso.regras_familias', '='+rr+'&""', rr.replace('$', ''), 'aviso'])
    return out
