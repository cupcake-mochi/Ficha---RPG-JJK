# -*- coding: utf-8 -*-
"""C+D · Tipos e Talentos de entidade custom (frente 3, módulo isolado para o integrador).

Molde aprovado: mockup/prototipo_custom_3c_restante.py (TIPO DE ENTIDADE e TALENTO · ENTIDADE).
Regras: livro R52, "Tipos de entidade" (p. 366) e "Talentos da entidade" (p. 375).

- Tipo custom: BASE DO LIVRO opcional. VIDA, TALISMÃ e RESERVA DE PE são três funcionamentos
  independentes. Em branco herda a base; sem base vale o funcionamento normal (vida 3 + CON,
  sem talismã, reserva comum). Um campo nunca liga outro, nem concede o que só a base daria.
- Talento custom: BASE DO LIVRO opcional; CATEGORIA DE EFEITO e EFEITO em branco herdam a base;
  sem base a Categoria é obrigatória. Orçamento, teto por ganho e escolhas da Trilha (só CE 1)
  continuam sendo as contas existentes da ficha, agora sobre o catálogo livro + custom válido.
- Autonomia, alma, nove Famílias e a ficha das 12 invocações não são tocadas.
- Texto (DEFINIÇÃO, EFEITO, REQUISITOS) é registro: nunca vira automação.

Etapa 5 da versão rápida (26/11/2026): os cadastros viraram lista simples. Tipo: NOME, VIDA, TALISMÃ, RESERVA DE PE e
um texto livre (DESCRIÇÃO, no lugar do EFEITO). Talento: NOME, CATEGORIA DE EFEITO e EFEITO. Saíram a BASE DO LIVRO (a
herança), o MESTRE VIU, a DEFINIÇÃO/REQUISITOS e os avisos. Os endereços dos cartões e das colunas não mudaram, e as
chaves da ANALISE dos campos que saíram continuam no lugar, em branco. Sem base, vale o funcionamento normal descrito
acima; um talento só entra nos menus com NOME e CATEGORIA.

Nada aqui fixa endereço global: o início dos cartões vem de CONFIGURAÇÃO['linhas'] (ou do parâmetro
`inicio`) e as capacidades são parâmetros. Capacidades, nomes de campo e chaves seguem o contrato
comum (conteudos-b47/comum/, revisão 1); nome da aba oculta e formato ANALISE continuam proposta
até o integrador fechar o contrato (ver PROPOSTA-CONTRATO.md).
"""
from copy import deepcopy

import indice_ficha as ix
import ficha_invocacoes as iv
from custom_criacao import criterio, ref, troca_refs
from custom_pecas import buscas_literais
from capacidades import TIPOS_ENTIDADE, TALENTOS_ENTIDADE

NOME = 'DADOS_ENTIDADES'
TIPOS, TALENTOS = TIPOS_ENTIDADE, TALENTOS_ENTIDADE
PASSO = 28                          # altura do par de cartões, como no protótipo aprovado
VIDA = ('Normal da entidade', 'Corpo de criação')
TALISMA = ('Não usa', 'Usa')
RESERVA = ('Normal da entidade', 'Maldição domada')
CES = (1, 2, 3)
# Funcionamentos que o livro liga a cada tipo publicado (as mesmas constantes que a ficha compara).
MODOS_DO_LIVRO = {iv.CORPO_CRIACAO: (1, 0, 0), iv.SH_CRIACAO: (0, 1, 0), iv.DOMADA: (0, 0, 1)}

# Colunas da aba oculta (1 = A). Blocos separados; nenhuma tabela depende de outra posição.
TR = dict(reg=1, nome=2, base=3, vida=4, talisma=5, reserva_pe=6, mestre_viu=7, definicao=8, efeito=9, idx=10, erro=11)
TC = dict(nome=13, vida=14, talisma=15, domada=16)
OP = dict(vida=18, talisma=19, reserva_pe=20, base_tipo=21, categoria=22, base_talento=23)
LR = dict(reg=25, nome=26, base=27, categoria=28, requisitos=29, efeito=30, mestre_viu=31, idx=32, erro=33)
LC = dict(nome=35, ce=36, faz=37, trilha=38)
COLUNAS = 44

L = ix._letras


def coord(r, c):
    return L(c) + str(r)


def faixa(c1, r1, c2, r2, sheet=NOME):
    return ref(coord(r1, c1), sheet) + ':$' + L(c2) + '$' + str(r2)


def cartao(kind, n, inicio):
    """Endereços de um cartão na CONFIGURAÇÃO, pelo molde do protótipo (pares lado a lado)."""
    r, c = inicio + (n - 1) // 2 * PASSO, 2 if n % 2 else 10
    g = dict(kind=kind, n=n, r=r, c=c, nome=coord(r + 2, c), mestre_viu=coord(r + 2, c + 4),
             base=coord(r + 4, c + 3), aviso=coord(r + 26, c))
    if kind == 'tipo':
        g.update(vida=coord(r + 5, c + 3), talisma=coord(r + 6, c + 3), reserva_pe=coord(r + 8, c + 3),
                 definicao=coord(r + 12, c), efeito=coord(r + 17, c))
    else:
        g.update(categoria=coord(r + 5, c + 3), requisitos=coord(r + 12, c), efeito=coord(r + 17, c))
    return g


# Ordem e nomes de conteudos-b47/comum/contrato.json ("campos").
CAMPOS = {'tipo': ['nome', 'mestre_viu', 'base', 'vida', 'talisma', 'reserva_pe', 'definicao', 'efeito'],
          'talento': ['nome', 'mestre_viu', 'base', 'categoria', 'requisitos', 'efeito']}
ROTULO = dict(vida='VIDA', talisma='TALISMÃ', reserva_pe='RESERVA DE PE')
LISTAS = dict(vida=VIDA, talisma=TALISMA, reserva_pe=RESERVA, categoria=CES)
# Etapa 5 da versão rápida: campos que saíram (a chave da ANALISE fica, em branco; nenhuma fórmula lê a célula).
SAI = {'tipo': ('mestre_viu', 'base', 'definicao'), 'talento': ('mestre_viu', 'base', 'requisitos')}
FICA = {k: [c for c in v if c not in SAI[k]] for k, v in CAMPOS.items()}
CHAVE = {'tipo': 'tipo_entidade', 'talento': 'talento_entidade'}


def aplica(layout, contexto):
    """Acrescenta cadastros, catálogos unidos e liga os consumidores da DADOS_INVOC.

    Interface do contrato comum: `contexto['inv']` é o retorno de ficha_invocacoes (o mesmo objeto
    que custom_pecas recebe); `capacidades` ({'tipo_entidade': n, 'talento_entidade': n}) e `inicio`
    são opcionais. Devolve a transformação (antes/depois, entradas, registros, catálogos, início/fim).
    """
    fiv = contexto['inv']
    cap = contexto.get('capacidades') or {}
    tipos, talentos = cap.get('tipo_entidade', TIPOS), cap.get('talento_entidade', TALENTOS)
    inicio = contexto.get('inicio')
    if any(type(n) is not int or not 1 <= n <= 30 for n in (tipos, talentos)):
        raise ValueError('capacidades precisam ser inteiros de 1 a 30')
    if any(a['nome'] == NOME for a in layout['abas']):
        raise ValueError('Catálogo de entidades já existe; aplicação repetida recusada')
    config = ix._aba(layout, 'CONFIGURAÇÃO')
    inicio = config['linhas'] + 4 if inicio is None else inicio
    if type(inicio) is not int or inicio < config['linhas'] + 3:
        raise ValueError('Início deve reservar cabeçalho depois do fim real de CONFIGURAÇÃO')
    meio = inicio + (tipos + 1) // 2 * PASSO + 2
    fim = meio + (talentos + 1) // 2 * PASSO
    regs_t = [cartao('tipo', n, inicio) for n in range(1, tipos + 1)]
    regs_l = [cartao('talento', n, meio) for n in range(1, talentos + 1)]
    D, R, colf = fiv['D'], fiv['R'], fiv['colf']
    livro_tipos = [t['nome'] for t in R['LIV']['tipos']]
    livro_tal = R['talentos']
    nbt, nbl = len(livro_tipos), len(livro_tal)
    falta = [n for n in MODOS_DO_LIVRO if n not in livro_tipos]
    if falta:
        raise ValueError('tipos do livro esperados ausentes: ' + ', '.join(falta))

    linhas = max(tipos, talentos) + max(nbt, nbl) + 3
    layout['abas'].append(dict(nome=NOME, estado='hidden', linhas=linhas, colunas=COLUNAS,
                               padrao=['Roboto', 10, '#000000'], fundo_base='#FFFFFF', grade=False,
                               celulas=[], mescladas=[], menus=[], condicional=[], imagens=[], colunas_larg=[],
                               linhas_alt=[], altura_padrao=15.75, paleta_fixa=True, validacao_em_matriz=True))
    cells = {a['nome']: {v[0]: v for v in a['celulas']} for a in layout['abas']}
    tr = dict(antes={}, depois={}, entradas=[], registros={CHAVE['tipo']: regs_t, CHAVE['talento']: regs_l},
              catalogos={}, inicio=inicio, fim=fim, capacidades={CHAVE['tipo']: tipos, CHAVE['talento']: talentos},
              substituicoes=0, consumidores={}, esticam=0)

    def put(sheet, a1, value, style=None):
        old = cells[sheet].get(a1)
        before = old[1] if old is not None else None
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

    def d(r, c, v):
        put(NOME, coord(r, c), v)

    # --- listas fechadas
    for key, vals in LISTAS.items():
        d(1, OP[key], 'opções ' + key)
        for i, v in enumerate(vals, 2):
            d(i, OP[key], v)

    # --- catálogo de tipos: livro espelhado da DADOS_INVOC + custom válido
    for c, h in [(TC['nome'], 'tipo de entidade'), (TC['vida'], 'vida de criação'), (TC['talisma'], 'usa talismã'),
                 (TC['domada'], 'reserva de domada')]:
        d(1, c, h)
    for i, nome in enumerate(livro_tipos):
        r, src = 2 + i, D.celula('tipos', i, 0, aba=iv.DI)
        d(r, TC['nome'], f'=IF(ISBLANK({src}),"",{src})')
        for c, v in zip((TC['vida'], TC['talisma'], TC['domada']), MODOS_DO_LIVRO.get(nome, (0, 0, 0))):
            d(r, c, v)
    livro_tipos_nomes = faixa(TC['nome'], 2, TC['nome'], nbt + 1)
    for c, h in [(TR['reg'], 'registro'), (TR['nome'], 'nome'), (TR['vida'], 'vida'),
                 (TR['talisma'], 'talismã'), (TR['reserva_pe'], 'reserva de PE'), (TR['efeito'], 'descrição')]:
        d(1, c, h)
    for g in regs_t:
        r, dst = g['n'] + 1, nbt + g['n'] + 1
        d(r, TR['reg'], g['n'])
        for key in CAMPOS['tipo']:
            tr['entradas'].append((f'custom.{CHAVE["tipo"]}.{g["n"]}.{key}', g[key], key == 'mestre_viu', key in SAI['tipo']))
            if key in SAI['tipo']:
                continue
            rr = ref(g[key], 'CONFIGURAÇÃO')
            d(r, TR[key], f'=IF(ISBLANK({rr}),"",{rr})')
        cn = coord(r, TR['nome'])
        valido = coord(dst, TC['nome'])
        d(dst, TC['nome'], f'=IF({cn}<>"",{cn},"")')
        for key, col, liga in [('vida', TC['vida'], VIDA[1]), ('talisma', TC['talisma'], TALISMA[1]),
                               ('reserva_pe', TC['domada'], RESERVA[1])]:
            cv = coord(r, TR[key])
            d(dst, col, f'=IF({valido}="",0,IF({cv}="{liga}",1,0))')
    tot_t = nbt + tipos
    TIPOS_UNIAO = faixa(TC['nome'], 2, TC['domada'], tot_t + 1)
    tr['catalogos'][CHAVE['tipo']] = TIPOS_UNIAO

    # --- catálogo de talentos: livro espelhado (4 colunas da tabela "talentos") + custom válido
    for c, h in [(LC['nome'], 'talento'), (LC['ce'], 'categoria de efeito'), (LC['faz'], 'o que o talento faz'),
                 (LC['trilha'], 'menu de talento da trilha')]:
        d(1, c, h)
    for i in range(nbl):
        r = 2 + i
        for k, c in enumerate((LC['nome'], LC['ce'], LC['faz'], LC['trilha'])):
            src = D.celula('talentos', i, k, aba=iv.DI)
            d(r, c, f'=IF(ISBLANK({src}),"",{src})')
    livro_tal_nomes = faixa(LC['nome'], 2, LC['nome'], nbl + 1)
    for c, h in [(LR['reg'], 'registro'), (LR['nome'], 'nome'), (LR['categoria'], 'categoria de efeito'),
                 (LR['efeito'], 'efeito')]:
        d(1, c, h)
    for g in regs_l:
        r, dst = g['n'] + 1, nbl + g['n'] + 1
        d(r, LR['reg'], g['n'])
        for key in CAMPOS['talento']:
            tr['entradas'].append((f'custom.{CHAVE["talento"]}.{g["n"]}.{key}', g[key], key == 'mestre_viu', key in SAI['talento']))
            if key in SAI['talento']:
                continue
            rr = ref(g[key], 'CONFIGURAÇÃO')
            d(r, LR[key], f'=IF(ISBLANK({rr}),"",{rr})')
        cn, cc = coord(r, LR['nome']), coord(r, LR['categoria'])
        valido = coord(dst, LC['nome'])
        # Sem os avisos, o talento só entra nos menus com NOME e CATEGORIA (o menu da categoria só aceita 1, 2 ou 3).
        d(dst, LC['nome'], f'=IF(AND({cn}<>"",{cc}<>""),{cn},"")')
        d(dst, LC['ce'], f'=IF({valido}="",0,IFERROR(VALUE({cc}&""),0))')
        d(dst, LC['faz'], f'=IF({valido}="","",{coord(r, LR["efeito"])})')
        d(dst, LC['trilha'], f'=IF(AND({valido}<>"",{coord(dst, LC["ce"])}=1),{valido},"")')
    tot_l = nbl + talentos
    TALENTOS_UNIAO = faixa(LC['nome'], 2, LC['trilha'], tot_l + 1)
    tr['catalogos'][CHAVE['talento']] = TALENTOS_UNIAO

    # --- consumidores: tabelas da DADOS_INVOC trocadas pelos catálogos unidos (todas as subfaixas)
    mapping = {}
    col, first, last, width = D.T['talentos']
    for left in range(width):
        for right in range(left, width):
            old = iv._faixa(col + left, first, col + right, last).replace('$', '')
            mapping[(iv.DADOS_IV, old)] = faixa(LC['nome'] + left, 2, LC['nome'] + right, tot_l + 1)
    col, first, last, _ = D.T['tipos']
    mapping[(iv.DADOS_IV, iv._faixa(col, first, col, last).replace('$', ''))] = faixa(TC['nome'], 2, TC['nome'], tot_t + 1)
    alvos = set()
    for v in mapping.values():
        owner, address = v.rsplit('!', 1)
        alvos.add((owner.strip("'"), address.replace('$', '')))
    for aba in layout['abas']:
        if aba['nome'] == NOME:
            continue
        for v in list(aba['celulas']):
            novo = buscas_literais(troca_refs(v[1], aba['nome'], mapping), aba['nome'], alvos)
            if novo != v[1]:
                put(aba['nome'], v[0], novo)
                tr['substituicoes'] += 1
        for m in aba.get('menus', []):
            m['formula'] = troca_refs('=' + m['formula'], aba['nome'], mapping)[1:]

    # --- comparações do tipo por nome viram consulta aos funcionamentos efetivos
    trocas = {iv.CORPO_CRIACAO: 2, iv.SH_CRIACAO: 3, iv.DOMADA: 4}
    feitas = {k: 0 for k in trocas}
    dados_iv = cells[iv.DADOS_IV]
    for i in range(len(fiv['fichas_c'])):
        linha = 2 + i
        tipo = f'${L(colf["tipo"])}{linha}'
        for a1, cel in list(dados_iv.items()):
            v = cel[1]
            if not (isinstance(v, str) and v.startswith('=') and ix._lc(a1)[0] == linha):
                continue
            novo = v
            for nome, k in trocas.items():
                alvo = f'{tipo}="{nome}"'
                if alvo in novo:
                    novo = novo.replace(alvo, f'IFERROR(VLOOKUP({criterio(tipo)},{TIPOS_UNIAO},{k},FALSE),0)=1')
                    feitas[nome] += 1
            if novo != v:
                put(iv.DADOS_IV, a1, novo)
    if any(n != len(fiv['fichas_c']) for n in feitas.values()):
        raise ValueError(f'comparações de tipo não encontradas em todas as fichas: {feitas}')
    tr['consumidores'] = dict(comparacoes=feitas, colunas=[k for k in ('cri', 'ent', 'd_res') if k in colf])

    # O texto do tipo aparece como ajuda no seletor existente da invocação.
    # A DEFINIÇÃO livre do jogador conserva sua entrada e seu endereço.
    for c, text in [(39,'índice do tipo custom selecionado'),(40,'definição do tipo selecionado'),
                    (41,'efeito do tipo selecionado'),(42,'nota do tipo selecionado'),
                    (43,'definição efetiva do tipo'),(44,'efeito efetivo do tipo')]:
        d(1,c,text)
    for i,tipo_livro in enumerate(R['LIV']['tipos'],2):
        d(i,43,tipo_livro['corpo']);d(i,44,tipo_livro['ficha'])
    for g in regs_t:
        r,dst=g['n']+1,nbt+g['n']+1
        # Etapa 5: a DEFINIÇÃO saiu; o texto livre (DESCRIÇÃO) vai na coluna do efeito.
        d(dst,44,f'=IF({coord(dst,TC["nome"])}="","",{coord(r,TR["efeito"])})')
    nomes_uniao = faixa(TC['nome'],2,TC['nome'],tot_t+1)
    for i,g in enumerate(fiv['fichas_c']):
        r=i+2;chosen=ref(g['tipo'],iv.NOME);idx=coord(r,39)
        d(r,39,f'=IF({chosen}="",0,IFERROR(MATCH({criterio(chosen)},{nomes_uniao},0),0))')
        for target,source in [(40,43),(41,44)]:
            d(r,target,f'=IF({idx}=0,"",IFERROR(INDEX({faixa(source,2,source,tot_t+1)},{idx})&"",""))')
        definicao,efeito=coord(r,40),coord(r,41)
        d(r,42,f'=TEXTJOIN(CHAR(10)&CHAR(10),TRUE,IF({definicao}="","","DEFINIÇÃO"&CHAR(10)&{definicao}),'
               f'IF({efeito}="","","EFEITO E REQUISITOS"&CHAR(10)&{efeito}))')
    ix._aba(layout,iv.NOME)['notas_contextuais'] = dict(
        fonte=NOME,coluna=42,primeira=2,destinos=[g['tipo'] for g in fiv['fichas_c']],
        gatilhos=[g[key] for g in regs_t for key in FICA['tipo']])

    # --- cartões na CONFIGURAÇÃO (molde do protótipo aprovado)
    styles = {v[0]: v[2] for v in config['celulas']}
    st = dict(secao=styles['B9'], rotulo=styles['B10'], entrada=styles['C11'], caixa=styles['B11'], nota=styles['B5'],
              fundo=styles['A1'])
    texto = deepcopy(layout['estilos'][st['entrada']])
    texto[3] = ['left', 'top', True, 0]
    if texto not in layout['estilos']:
        layout['estilos'].append(texto)
    st['texto'] = layout['estilos'].index(texto)
    config.setdefault('notas', {})

    def box(r, c, value=None, er=None, ec=None, kind='entrada', note=None):
        a1, end = coord(r, c), coord(er or r, ec or c)
        if a1 in cells['CONFIGURAÇÃO'] and cells['CONFIGURAÇÃO'][a1][1] not in (None, ''):
            raise ValueError('Novo cartão sobrepõe CONFIGURAÇÃO!' + a1)
        put('CONFIGURAÇÃO', a1, value, st[kind])
        if a1 != end:
            config['mescladas'].append(a1 + ':' + end)
        config['notas'][a1] = note or 'Cadastro custom de entidade. Em branco herda a base do livro, quando escolhida.'

    def menu(a1, source):
        config['menus'].append(dict(onde=a1, tipo='list', formula=source, vazio_ok=True, mostra_seta=True, estrito=True))
        config.setdefault('menus_estritos', []).append(a1)

    for r in range(config['linhas'] + 1, fim + 1):
        for c in range(1, 17):
            if coord(r, c) not in cells['CONFIGURAÇÃO']:
                put('CONFIGURAÇÃO', coord(r, c), None, st['fundo'])
    lista = lambda key: faixa(OP[key], 2, OP[key], 1 + len(LISTAS[key]))

    def cabeca(g, titulo):
        r, c = g['r'], g['c']
        box(r, c, f'{titulo} · {g["n"]}', ec=c + 5, kind='secao')
        box(r + 1, c, 'NOME', ec=c + 5, kind='rotulo', note='O menu da invocação reúne o livro e estes nomes.')
        box(r + 2, c, ec=c + 5, note='Nome próprio do conteúdo criado com o mestre.')

    def campo(g, off, rotulo, key, note):
        r, c = g['r'], g['c']
        box(r + off, c, rotulo, ec=c + 2, kind='rotulo', note=note)
        box(r + off, c + 3, ec=c + 5, note=note)
        menu(g[key], lista(key))

    def area(g, off, rotulo, ate, note):
        r, c = g['r'], g['c']
        box(r + off, c, rotulo, ec=c + 5, kind='rotulo', note=note)
        box(r + off + 1, c, er=r + ate, ec=c + 5, kind='texto', note=note)

    for g in regs_t:
        cabeca(g, 'TIPO DE ENTIDADE')
        campo(g, 5, 'VIDA', 'vida', 'Em branco usa a vida normal da entidade. Corpo de criação usa 4 + Constituição '
              'por nível após o primeiro.')
        campo(g, 6, 'TALISMÃ', 'talisma', 'Em branco não usa. Usar habilita a carga do talismã na entrada da entidade.')
        campo(g, 8, 'RESERVA DE PE', 'reserva_pe', 'Em branco usa a reserva normal. A opção domada aplica o cálculo já '
              'publicado.')
        area(g, 16, 'DESCRIÇÃO', 24, 'Texto livre do tipo: corpo, natureza, efeito e requisitos. Aparece na nota do '
             'seletor TIPO da invocação; não cria automações.')
    for g in regs_l:
        cabeca(g, 'TALENTO · ENTIDADE')
        campo(g, 5, 'CATEGORIA DE EFEITO', 'categoria', 'Obrigatória para o talento entrar nos menus. Conferida com o teto '
              'de cada ganho; as escolhas da Trilha aceitam só a Categoria 1.')
        area(g, 16, 'EFEITO', 24, 'Descrição completa, exibida na carta existente. Texto livre não cria automações.')
    # Áreas de texto esticam com o conteúdo (esticarCaixas_), por par de cartões vizinhos, como no custom_pecas.
    for regs, areas in [(regs_t, [('efeito', 17, 8)]), (regs_l, [('efeito', 17, 8)])]:
        for i in range(0, len(regs), 2):
            pair = regs[i:i + 2]
            for key, offset, height in areas:
                texts = []
                for g in pair:
                    width = sum(next((w for lo, hi, w in config['colunas_larg'] if lo <= c <= hi), 4) * 8 - 1
                                for c in range(g['c'], g['c'] + 6)) - 12
                    texts.append([width, [g[key]], g['r'] + offset, height, 0])
                config.setdefault('esticam', []).append(dict(gatilhos=[g[key] for g in pair], aba='CONFIGURAÇÃO',
                                                             minima=25, textos=texts))
                tr['esticam'] += 1
    box(inicio - 2, 2, 'ENTIDADES CUSTOM · TIPOS', ec=15, kind='secao')
    box(meio - 2, 2, 'ENTIDADES CUSTOM · TALENTOS', ec=15, kind='secao')
    config['linhas'] = fim
    config['linhas_alt'] = config.get('linhas_alt', []) + [[r, 18.75] for r in range(inicio - 2, fim + 1)]
    return tr


def exporta(tr):
    """Linhas ANALISE propostas: cadastro cru (mesmo inválido) e aviso por registro, no fim do contrato."""
    out = []
    for key, a1, booleano, saiu in tr['entradas']:
        if saiu:
            out.append([key, '', '', 'configuração'])
            continue
        rr = ref(a1, 'CONFIGURAÇÃO')
        valor = f'=N({rr})&""' if booleano else f'=IF(ISBLANK({rr}),"",{rr}&"")'
        out.append([key, valor, rr.replace('$', ''), 'configuração'])
    # Etapa 5: os avisos saíram; a chave fica, em branco.
    for kind in ('tipo', 'talento'):
        for g in tr['registros'][CHAVE[kind]]:
            out.append([f'aviso.custom.{CHAVE[kind]}.{g["n"]}', '', '', 'aviso'])
    return out
