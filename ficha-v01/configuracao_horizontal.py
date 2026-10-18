"""Apresentação horizontal da CONFIGURAÇÃO; aplicada depois das regras.

As fórmulas são traduzidas por tokens, nunca por substituição de números.
Retângulos que não têm tradução afim única são recusados: o leitor INDEX
antigo das peças é resolvido explicitamente antes de mover os cartões.
"""
import copy
import re
from collections import Counter
from functools import lru_cache
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import coordinate_to_tuple, get_column_letter as L

NOME = 'CONFIGURAÇÃO'
SECOES = [
    ('Geral', 1, 736), ('Cadastros gerais', 1, 733),
    ('Caminho e Trilha', 737, 796), ('Perícias', 797, 866),
    ('Ofícios', 867, 936), ('Famílias', 937, 1008),
    ('Melhorias', 1009, 1401), ('Restrições', 1402, 1732),
    ('Tipos de dano', 1733, 1876), ('Formas', 1877, 2112),
    ('Aptidões e Bênçãos', 2113, 2253), ('Talentos', 2254, 2385),
    ('Tipos de entidade', 2386, 2527), ('Talentos de entidade', 2528, 2812),
]
PASSO = 17  # coluna de identificação + dezesseis colunas do painel
ABERTURAS = {
    'Cadastros gerais': 'Cadastre aqui conteúdos próprios para aparecerem nos menus da ficha. Escolha o tipo e um nome único; MESTRE VIU é um lembrete de revisão, e a aprovação acontece no chat.',
    'Caminho e Trilha': 'Personalize Caminho e Trilha escolhendo uma base do livro ou preenchendo os campos próprios. Campos em branco herdam a base escolhida; confira os avisos de cada cadastro.',
    'Perícias': 'Crie Perícias próprias para os menus da ficha. Use um nome único, escolha uma base quando quiser herdar suas regras e preencha somente as diferenças.',
    'Ofícios': 'Cadastre Ofícios próprios para os menus da ficha. Escolha uma base para herdar seus campos ou descreva um Ofício novo; confira os requisitos e avisos antes de usá-lo.',
    'Famílias': 'Defina Famílias próprias e suas características para os conteúdos que as utilizam. Use nomes únicos e confira os avisos. Campos em branco herdam a base escolhida, quando houver.',
    'Melhorias': 'Cadastre Melhorias próprias e seus valores. A base do livro fornece os campos deixados em branco; sem base, preencha os campos necessários. Confira os avisos antes de escolher na ficha.',
    'Restrições': 'Cadastre Restrições próprias e suas condições de uso. Deixe em branco os campos que devem herdar a base do livro. A descrição registra a regra; texto livre não cria automação.',
    'Tipos de dano': 'Crie Tipos de dano para os menus da ficha. Escolha uma base do livro para herdar seus campos ou preencha os dados próprios. Confira as condições, os avisos e o efeito descrito.',
    'Formas': 'Cadastre Formas para personagens e entidades. Campos em branco herdam a base do livro. ALC = alcance; P = personagem; E = entidade; os números indicam a Classe ou faixa de Classes. TR = Teste de Resistência. As escadas definem a progressão de alcance e área.',
    'Aptidões e Bênçãos': 'Crie Aptidões e Bênçãos do personagem escolhendo o tipo e, se desejar, uma base do livro. Campos em branco herdam essa base. Confira os requisitos, o efeito e os avisos do cadastro.',
    'Talentos': 'Cadastre Talentos do personagem. Use uma base do livro para herdar os campos em branco ou descreva um Talento próprio; confira os requisitos e avisos. Texto livre não cria automação.',
    'Tipos de entidade': 'Defina Tipos de entidade para as invocações e demais entidades. Escolha uma base para herdar os campos em branco. PE = pontos de energia; confira os valores, requisitos e avisos.',
    'Talentos de entidade': 'Cadastre Talentos usados por entidades. Escolha uma base do livro ou preencha os campos próprios e confira os requisitos. PE = pontos de energia; descrições em texto não criam automação.',
}


def blocos():
    # (r1,c1,r2,c2,dr,dc,painel); coordenadas inclusivas, base 1.
    out = [(1, 1, 736, 8, 0, 1, 0), (1, 9, 8, 16, 0, PASSO-7, 1)]
    for n in range(25):
        r = 9 + 29*n
        out.append((r, 9, r+28, 16, 12+(n//2)*29-r,
                    PASSO+1+(n % 2)*8-8, 1))
    out.append((734, 9, 736, 16, 389-734, PASSO-7, 1))
    for i, (_, lo, hi) in enumerate(SECOES[2:], 2):
        out.append((lo, 1, hi, 16, 9-lo, i*PASSO+1, i))
    return out


BLOCOS = blocos()


@lru_cache(maxsize=60000)
def ponto(row, col):
    for r1,c1,r2,c2,dr,dc,p in BLOCOS:
        if r1 <= row <= r2 and c1 <= col <= c2:
            return row+dr, col+dc
    raise ValueError(f'CONFIGURAÇÃO fora do mapa: {L(col)}{row}')


def coord(a1):
    m = re.fullmatch(r'(\$?)([A-Z]+)(\$?)(\d+)', a1)
    if not m:
        raise ValueError('Coordenada inválida: '+a1)
    r,c = coordinate_to_tuple(m[2]+m[4]); nr,nc = ponto(r,c)
    return m[1]+L(nc)+m[3]+str(nr)


def faixa(a1):
    parts = a1.split(':')
    if len(parts) == 1:
        return coord(a1)
    a,b = [coordinate_to_tuple(x.replace('$','')) for x in parts]
    da = tuple(x-y for x,y in zip(ponto(*a),a))
    db = tuple(x-y for x,y in zip(ponto(*b),b))
    # Endpoints iguais não bastam quando há cartões intercalados no meio.
    for r1,c1,r2,c2,dr,dc,_ in BLOCOS:
        if max(a[0],r1) <= min(b[0],r2) and max(a[1],c1) <= min(b[1],c2):
            if (dr,dc) != da:
                raise ValueError('Faixa atravessa painéis: '+a1)
    if da != db:
        raise ValueError('Faixa sem tradução única: '+a1)
    return ':'.join(coord(x) for x in parts)


@lru_cache(maxsize=25000)
def formula(text, owner):
    if isinstance(text,str):
        address = re.fullmatch(r"('CONFIGURAÇÃO'|CONFIGURAÇÃO)!(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)",text)
        if address:
            return address[1]+'!'+faixa(address[2])
    if not isinstance(text,str) or not text.startswith('='):
        return text
    if owner != NOME and NOME not in text:
        return text
    tokens = Tokenizer(text).items
    for t in tokens:
        # A coluna de origem da ANALISE publica endereços como texto em
        # fórmulas ="'CONFIGURAÇÃO'!B11"; o valor também precisa acompanhar.
        if t.type=='OPERAND' and t.subtype=='TEXT':
            literal=t.value[1:-1].replace('""','"')
            moved=formula(literal,owner)
            if moved!=literal:t.value='"'+moved.replace('"','""')+'"'
            continue
        if t.type != 'OPERAND' or t.subtype != 'RANGE':
            continue
        ref = t.value
        if '!' in ref:
            sheet, ref = ref.rsplit('!',1)
            if sheet.strip("'") != NOME:
                continue
            prefix = sheet+'!'
        elif owner == NOME:
            prefix = ''
        else:
            continue
        if re.fullmatch(r'\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?',ref):
            t.value = prefix+faixa(ref)
        else:
            raise ValueError('Referência de configuração não mapeada: '+ref)
    return '=' + ''.join(t.value for t in tokens)


def suplementos(old):
    """Os mesmos arquivos continuam particionando seus retângulos originais."""
    out = {}
    for filename, regions in old.items():
        regions = [regions] if isinstance(regions,tuple) else regions
        dest = []
        for f in regions:
            if f[0] != NOME:
                dest.append(f); continue
            _,ca,cb,*rr = f; ra,rb = rr if rr else (1,2812)
            for r1,c1,r2,c2,dr,dc,_ in BLOCOS:
                lo,hi,lc,hc = max(ra,r1),min(rb,r2),max(ca,c1),min(cb,c2)
                if lo <= hi and lc <= hc:
                    dest.append((NOME,lc+dc,hc+dc,lo+dr,hi+dr))
        out[filename] = dest
    return out


def limpar_notas(a):
    values = {x[0]:x[1] for x in a['celulas']}
    removed = []
    boilerplate = (
        'Em branco herda a base escolhida. Sem base, preencha os campos próprios.',
        'Campo do cadastro custom. Em branco herda a base do livro, quando escolhida.',
        'Campo do molde aprovado. Use o menu quando disponível;',
        'Cadastro de Família custom. Nome único;',
        'Cadastro custom de entidade. Em branco herda a base do livro, quando escolhida.',
    )
    notes = a.get('notas',{})
    for addr,note in list(notes.items()):
        reason = None
        if note.startswith(boilerplate):
            reason = 'orientação geral repetida; mantida uma vez no cabeçalho da categoria'
        else:
            r,c = coordinate_to_tuple(addr)
            # A mesma ajuda foi gravada no rótulo e no campo editável à direita.
            if values.get(addr) not in (None,'') and any(
                    notes.get(L(c+d)+str(r)) == note for d in range(1,6)):
                reason = 'duplicata no rótulo; ajuda do campo editável preservada'
        if reason:
            removed.append({'celula':addr,'motivo':reason,'texto':note})
            del notes[addr]
    return removed


def aplica(layout):
    config = next(a for a in layout['abas'] if a['nome'] == NOME)
    if config.get('horizontal'):
        raise ValueError('Layout horizontal aplicado duas vezes')
    removed = limpar_notas(config)
    fundo_style = next(x[2] for x in config['celulas'] if x[0]=='A1')
    # O antigo título geral atravessava os dois painéis independentes.
    config['mescladas'] = [m for m in config['mescladas'] if not m.startswith('B2:')]
    config['mescladas'].append('B2:H3')
    # A reserva vazia inferior do painel Geral não é um campo do jogador.
    config['celulas'] = [x for x in config['celulas'] if not (
        coordinate_to_tuple(x[0])[0]>170 and coordinate_to_tuple(x[0])[1]<=8 and
        coordinate_to_tuple(x[0])[0]<737 and x[1] in (None,''))]
    for a in layout['abas']:
        owner = a['nome']
        for x in a['celulas']:
            x[1] = formula(x[1],owner)
            if owner == NOME:
                x[0] = coord(x[0])
                if len(x)>3: x[3] = faixa(x[3])
        for menu in a.get('menus',[]):
            f = menu.get('formula')
            if isinstance(f,str):
                menu['formula'] = formula(f if f.startswith('=') else '='+f,owner).lstrip('=') if (owner==NOME or NOME in f) else f
            if owner==NOME:
                menu['onde'] = ' '.join(faixa(p) for p in menu['onde'].split())
        if owner != NOME:
            contextual = a.get('notas_contextuais')
            if contextual:
                contextual['gatilhos'] = [faixa(x) for x in contextual['gatilhos']]
            continue
        a['mescladas'] = [faixa(m) for m in a['mescladas']]
        a['notas'] = {coord(k):v for k,v in a['notas'].items()}
        a['menus_estritos'] = [faixa(x) for x in a.get('menus_estritos',[])]
        a['sem_trava'] = [faixa(x) for x in a.get('sem_trava',[])]
        for cf in a.get('condicional',[]):
            cf['onde'] = ' '.join(faixa(x) for x in cf['onde'].split())
            cf['formula'] = [formula('='+x.lstrip('='),NOME)[1:] for x in cf['formula']]
        for cf in a.get('condicional_gs',[]):
            cf['faixas'] = [faixa(x) for x in cf['faixas']]
            if cf.get('formula'):cf['formula'] = formula(cf['formula'],NOME)
        # A expansão por cópia ainda é afim dentro de cada catálogo.
        for g in a.get('copias',[]):
            ra,rb,targets,ca,cb = g[:5]
            nr,nc = ponto(ra,ca); end = ponto(rb,cb)
            g[:5] = [nr,end[0],[ponto(r,ca)[0] for r in targets],nc,end[1]]
            if len(g)>5:g[5] = [[ponto(ra,c1)[1],ponto(ra,c2)[1]] for c1,c2 in g[5]]
        # O compactador histórico replica linhas inteiras da aba. Em painéis
        # paralelos isso copiaria também as categorias vizinhas. As células
        # já estão explícitas no LAYOUT; não aplicar esse atalho à CONFIGURAÇÃO.
        a['copias'] = []
        textos, gatilhos = [], []
        for g in a.get('esticam',[]):
            assert g['aba']==NOME
            gatilhos.extend(faixa(x) for x in g['gatilhos'])
            for t in g['textos']:
                t=copy.deepcopy(t);old=coordinate_to_tuple(t[1][0].split(':')[0]);t[2]=ponto(t[2],old[1])[0]
                t[1]=[faixa(x) for x in t[1]];textos.append(t)
        a['esticam'] = [dict(aba=NOME,gatilhos=gatilhos,textos=textos,minima=25)]
        heights = {}
        for r,h in a['linhas_alt']:
            for r1,c1,r2,c2,dr,dc,_ in BLOCOS:
                if r1<=r<=r2 and not (r>170 and r<737 and c2<=8):
                    heights[r+dr]=max(h,heights.get(r+dr,0))
        a['linhas_alt'] = sorted([[r,h] for r,h in heights.items()])
        widths = {c:w for ca,cb,w in a['colunas_larg'] for c in range(ca,cb+1)}
        a['colunas_larg'] = []
        for i in range(len(SECOES)):
            a['colunas_larg'].append([i*PASSO+1,i*PASSO+1,4.1])
            for c in range(1,17):
                # O painel Geral tem controles assimétricos históricos.
                # Os cadastros em pares usam cartões de mesma largura.
                width=widths.get(c,4) if i==0 else (2.125 if c in (1,8,9,16) else 10.125)
                a['colunas_larg'].append([i*PASSO+1+c,i*PASSO+1+c,width])
        # O cartão 3a que ocupava só a direita agora também usa a esquerda;
        # medir a caixa pela largura real das novas colunas.
        px = {c:w*8-1 for lo,hi,w in a['colunas_larg'] for c in range(lo,hi+1)}
        merges = {m.split(':')[0]:m for m in a['mescladas']}
        for t in textos:
            region = merges.get(t[1][0])
            if region:
                ca = coordinate_to_tuple(region.split(':')[0])[1]
                cb = coordinate_to_tuple(region.split(':')[-1])[1]
                t[0] = sum(px[c] for c in range(ca,cb+1))-12
        a['grupos'] = {'linhas':[], 'colunas':[[i*PASSO+2,(i+1)*PASSO,i>0] for i in range(len(SECOES))]}
        a['linhas'] = max(coordinate_to_tuple(x[0])[0] for x in a['celulas'])+2
        a['colunas'] = len(SECOES)*PASSO
        a['horizontal'] = {'versao':1,'secoes':[{'nome':n,'coluna':i*PASSO+1,'inicio':i*PASSO+2,'fim':(i+1)*PASSO} for i,(n,_,_) in enumerate(SECOES)]}
        a['gatilhos_habilidades'] = [faixa('B737:O792')]
        # Identificação vertical fica visível mesmo com a lista recolhida.
        style=copy.deepcopy(layout['estilos'][next(x[2] for x in a['celulas'] if x[0]==coord('B9'))])
        style[3]=['center','center',False,90];layout['estilos'].append(style);idx=len(layout['estilos'])-1
        a['apresentacao'] = []
        for i,(name,_,_) in enumerate(SECOES):
            col=L(i*PASSO+1)
            a['celulas'].append([col+'2',name.upper(),idx]);a['mescladas'].append(col+'2:'+col+'9')
            a['apresentacao'].append(col+'2:'+col+'9')
            a['notas'][col+'2']='Use o + acima para abrir esta lista à direita; o − recolhe apenas este painel. Em branco herda a base escolhida; textos próprios não viram regras automaticamente.'
        # O antigo vão à direita do painel Geral vira um índice útil.
        field_styles={x[0]:x[2] for x in a['celulas']}
        section_style=field_styles[coord('B9')]
        note_style=field_styles[coord('B5')]
        entry_style=field_styles[coord('C11')]
        a['links_paineis']=[]
        def index(addr,end,text,style):
            a['celulas']=[x for x in a['celulas'] if x[0]!=addr]
            a['celulas'].append([addr,text,style]);a['mescladas'].append(addr+':'+end)
            a['apresentacao'].append(addr+':'+end)
        # Uma abertura por lista: a ajuda fica visível antes dos cartões,
        # sem repetir a explicação em cada campo ou cadastro.
        for i,(name,_,_) in enumerate(SECOES[1:],1):
            lo=i*PASSO+3;hi=(i+1)*PASSO-1
            title_row_end=2 if i==1 else 3
            body_start,body_end=(3,4) if i==1 else (4,7)
            index(L(lo)+'2',L(hi)+str(title_row_end),name.upper(),section_style)
            index(L(lo)+str(body_start),L(hi)+str(body_end),ABERTURAS[name],note_style)
        index('K5','Q6','LISTAS DE CONFIGURAÇÃO',section_style)
        index('K7','Q9','Escolha uma lista abaixo e use o + acima para abrir os cartões à direita.',note_style)
        for i,(name,_,_) in enumerate(SECOES[1:]):
            row=11+(i//2)*3;col=11+(i%2)*4
            addr=L(col)+str(row);end=L(min(col+3,17))+str(row+1)
            index(addr,end,name,entry_style)
            a['links_paineis'].append({'celula':addr,'alvo':L((i+1)*PASSO+1)+'2','texto':name})
        # O retângulo autorado também inclui o espaço abaixo das listas curtas.
        # Células novas não podem herdar o branco padrão do documento.
        occupied = {x[0] for x in a['celulas']}
        a['celulas'].extend([L(c)+str(r),None,fundo_style]
                            for r in range(1,a['linhas']+1) for c in range(1,a['colunas']+1)
                            if L(c)+str(r) not in occupied)
    return {'notas_removidas':removed,'notas_antes':len(removed)+len(config['notas'])-len(SECOES),'notas_depois':len(config['notas']),'secoes':config['horizontal']['secoes'],'linhas':config['linhas'],'colunas':config['colunas']}
