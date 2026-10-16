"""Pontes para as tabelas reais de B47; não escreve arquivos nem GS.

aplicar() altera somente o modelo em memória entregue pelo integrador.
O patch de incorporação chama este módulo DEPOIS das peças/famílias e ANTES
de ANALISE. Nenhum endereço do modelo é presumido como global.
"""
from copy import deepcopy
from dataclasses import dataclass
from openpyxl.utils import get_column_letter as L, column_index_from_string
from openpyxl.utils.cell import coordinate_from_string
from openpyxl.formula import Tokenizer
import custom_criacao as cc
import custom_pecas as cp
import ficha_amaldicoada as fa
import ficha_invocacoes as iv
from .fontes_livro import FAIXAS
from .planilha import intervalo, ref, criterio, q, literal


@dataclass
class Ambiente:
    familias_tabela: str  # nome,estado,livre,fechada
    rota: str
    bloqueia_extensao: str  # expressão existente, sem '='
    familias_entidades: list  # uma lista de nove referências por entidade


def _maxcol(cells):
    return max(column_index_from_string(coordinate_from_string(c)[0]) for c in cells)


def pontes(plano, livro, contrato, ambiente):
    """Tabelas com as larguras/ordens esperadas pelos consumidores existentes."""
    tabelas={}
    def tabela(grupo,nome,width,rows):
        aba=contrato.abas[grupo]
        start=_maxcol(plano.celulas[aba])+2
        for c in range(width): plano.por(aba,L(start+c)+'1',nome+'.'+str(c))
        for r,values in enumerate(rows,2):
            if len(values)!=width: raise ValueError('Largura incorreta em '+nome)
            for c,v in enumerate(values,start): plano.por(aba,L(c)+str(r),v)
        tabelas[nome]=dict(aba=aba,coluna=start,primeiro=2,ultimo=len(rows)+1,largura=width,
                           intervalo=intervalo(aba,start,len(rows),width))
    t=plano.tabelas['forma']
    f=lambda k,r: ref(t['aba'],'$'+L(t['colunas'][k])+str(r))
    linhas_p,linhas_e=[],[]
    for r in range(2,t['total']+2):
        nome,fam,peso=f('nome',r),f('familia',r),f('peso',r)
        livre=f'IFERROR(VLOOKUP({criterio(fam)},{ambiente.familias_tabela},3,FALSE),0)'
        fech=f'IFERROR(VLOOKUP({criterio(fam)},{ambiente.familias_tabela},4,FALSE),0)'
        emb=f'IF({f("restricao_embutida",r)}="",0,1)'
        linhas_p.append(['='+nome,'='+fam,'='+peso,
            f'=IF({peso}=0,0,{peso}+3*{livre})','='+fech,'='+emb,
            '='+f('resultado',r),f'=IF(AND({f("resolucao",r)}="Acerto",{f("exige_tr",r)}),"Acerto + TR",{f("resolucao",r)})',
            '=N(OR('+f('exige_tr',r)+','+f('resolucao',r)+'="TR, metade"))',
            '='+f('p1_grau',r),'='+f('p2_grau',r),'='+f('alvos',r),'=N('+f('classe_0',r)+')',
            f'=IF({fech}=1,"",{nome})',f'=IF(AND({f("classe_0",r)},{fech}=0),{nome},"")'])
        linhas_e.append(['='+nome,'='+fam,'='+peso,'='+emb,'='+f('resultado',r),
            f'=IF({f("resolucao",r)}="Acerto","Ataque",IF({f("exige_tr",r)},"TR","—"))',
            '=N(OR('+f('exige_tr',r)+','+f('resolucao',r)+'="TR, metade"))','='+f('p1_grau',r),'='+f('p2_grau',r),'='+f('alvos',r),'=N('+f('classe_0',r)+')'])
    tabela('forma','formas_personagem',15,linhas_p)
    tabela('forma','formas_entidade',11,linhas_e)
    for nome,escada in livro['escadas'].items():
        tabela('forma','escada_'+nome,1,[[v] for v in escada])
    for contexto,faixas in FAIXAS.items():
        # Uma base/índice por componente e faixa, compartilhada pelos seis
        # degraus. O livro conserva as linhas constantes já normalizadas.
        cache=[];indices={};start=_maxcol(plano.celulas[t['aba']])+2
        for r in range(t['livro']+2,t['total']+2):
            for faixa in faixas:
                for n in (1,2):
                    rr=len(cache)+2;indices[(r,faixa,n)]=rr
                    dim=f('p'+str(n)+'_dimensao',r)
                    esc=f'IF({dim}="area",{f("area_escada",r)},{f("alcance_escada",r)})'
                    b=f'IF({dim}="area",{f("area_"+contexto+"_"+faixa,r)},{f("alcance_"+contexto+"_"+faixa,r)})'
                    er=ref(t['aba'],'$'+L(start+1)+str(rr));br=ref(t['aba'],'$'+L(start+2)+str(rr))
                    cache.append(['='+dim,'='+esc,'='+b,'='+f('p'+str(n)+'_antes',r),
                                  '='+f('p'+str(n)+'_depois',r),'='+_indice(livro['escadas'],er,br)])
        tabela('forma','base_alcance_'+contexto,6,cache)
        meta=tabelas['base_alcance_'+contexto]
        rows=deepcopy(livro['alcances'][contexto])
        for r in range(t['livro']+2,t['total']+2):
            for faixa in faixas:
                values=['='+f('nome',r)+'&'+q(' · '+faixa.replace('_',' '))]
                for n in (1,2):
                    rr=indices[(r,faixa,n)]
                    campos=[ref(meta['aba'],'$'+L(meta['coluna']+k)+str(rr)) for k in range(6)]
                    dim,esc,b,antes,depois,idx=campos
                    if contexto=='entidade': depois=f'SUBSTITUTE({depois},"em você","nela")'
                    for grau in range(fa.GRAUS_NA_TABELA):
                        sub=b
                        if grau:
                            for nome,lista in reversed(list(livro['escadas'].items())):
                                source=tabelas['escada_'+nome]['intervalo']
                                sub=f'IF({esc}={q(nome)},INDEX({source},MIN({len(lista)},{idx}+{grau})),{sub})'
                        trecho=f'IF(OR({f("nome",r)}="",{dim}="",{b}=""),"",IF({b}="—","—",{antes}&{sub}&{depois}))'
                        if n==1:trecho=f'LET(trecho,{trecho},UPPER(LEFT(trecho,1))&MID(trecho,2,LEN(trecho)))'
                        values.append('='+trecho)
                rows.append(values)
        tabela('forma','alcance_'+contexto,13,rows)
    for i,fams in enumerate(ambiente.familias_entidades):
        if len(fams)!=9: raise ValueError('Entidade precisa preservar nove posições de Família')
        rows=[]
        for r in range(2,t['total']+2):
            fam=f('familia',r)
            aberto='OR('+','.join(f'{fam}={x}' for x in fams)+f',{fam}="")'
            nome=f('nome',r)
            rows.append([f'=IF({aberto},{nome},"")',f'=IF(AND({aberto},{f("classe_0",r)}),{nome},"")'])
        tabela('forma','menu_entidade_'+str(i),2,rows)
    t=plano.tabelas['talento']
    x=lambda k,r: ref(t['aba'],'$'+L(t['colunas'][k])+str(r))
    rows=[]
    for r in range(2,t['total']+2):
        rota=x('rota',r);nome=x('nome',r)
        fund=f'OR({rota}="Todas",{rota}="Fundamento / Manejos")'
        marc=f'OR({rota}="Todas",{rota}="Técnica Marcial")'
        disponivel=f'OR(AND({ambiente.rota}<=2,{fund}),AND({ambiente.rota}>=2,{marc}))'
        efeito=x('efeito',r)+'&IF('+x('requisitos',r)+'="","",CHAR(10)&"Requisitos: "&'+x('requisitos',r)+')'
        rows.append(['='+nome,'='+x('ce',r),'='+efeito,'=N('+fund+')','=N('+marc+')',
                     f'=IF({disponivel},{nome},"")','='+efeito])
    tabela('talento','passivas',7,rows)
    t=plano.tabelas['aptidao']
    x=lambda k,r: ref(t['aba'],'$'+L(t['colunas'][k])+str(r))
    rows=[]
    for r in range(2,t['total']+2):
        nome,tipo=x('nome',r),x('tipo',r)
        benc=f'{tipo}="Bênção"'
        permitido=f'AND(NOT({x("automatica",r)}),IF({ambiente.rota}=4,{benc},AND(NOT({benc}),NOT(AND({ambiente.bloqueia_extensao},{x("extensao",r)})))))'
        rows.append(['='+nome,'='+x('requisitos',r),'='+x('ce',r),'='+x('escala',r),'='+x('efeito',r),
                     f'=IF({permitido},{nome},"")','=N('+benc+')','=N('+x('extensao',r)+')',
                     f'=IF({x("escolha",r)}="Gratuita",1,0)','='+x('efeito',r)])
    tabela('aptidao','aptidoes',10,rows)
    return tabelas


def _indice(escadas,esc,b):
    """Índice base: exato, ou degrau abaixo do primeiro maior."""
    out='0'
    for nome,lista in reversed(list(escadas.items())):
        texto='{'+ ';'.join(q(v) for v in lista) +'}'
        numeros='{'+ ';'.join(str(float(v[:-2].replace(',','.'))) if v.endswith(' m') else '1E99' for v in lista) +'}'
        base_idx=f'IFERROR(MATCH(base,{texto},0),IFERROR(MATCH(valor,{numeros},1),0))'
        out=f'IF(escada={q(nome)},{base_idx},{out})'
    # Variáveis LET locais evitam repetir grandes expressões de busca em cada
    # degrau. Nenhum nome global/named range é criado.
    numero='IFERROR(VALUE(SUBSTITUTE(medida,",",""))/10^IFERROR(LEN(medida)-FIND(",",medida),0),1E99)'
    return f'LET(base,{b},escada,{esc},medida,LEFT(base,MAX(0,LEN(base)-2)),valor,{numero},IF(OR(escada="Fixo",base="—"),base,{out}))'


def _mapping(meta,owner,table,new):
    col,first,last,width=meta['D'].T[table]
    if width!=new['largura']: raise ValueError('Consumidor mudou de largura: '+table)
    return {(owner,fa._faixa(col+a,first,col+b,last).replace('$','')):
            intervalo(new['aba'],new['coluna']+a,new['ultimo']-1,b-a+1)
            for a in range(width) for b in range(a,width)}


def canonizar_comparacoes(formula,raw,canon,nomes):
    """Só comparações com nomes do livro; textos exibidos mantêm o alias."""
    if not isinstance(formula,str) or not formula.startswith('='): return formula
    tokens=Tokenizer(formula).items
    for i in range(len(tokens)-2):
        a,op,b=tokens[i:i+3]
        if op.type!='OPERATOR-INFIX' or op.value not in ('=','<>'): continue
        for left,right in [(a,b),(b,a)]:
            if left.type=='OPERAND' and left.subtype=='RANGE' and left.value==raw and right.subtype=='TEXT' and right.value[1:-1].replace('""','"') in nomes:
                left.value=canon
    return '='+''.join(t.value for t in tokens)


def aplicar(layout,plano,pontes,fam,inv,contrato):
    """Adapta o modelo em memória; devolve manifesto exato de antes/depois."""
    existentes={a['nome'] for a in layout['abas']}
    if existentes & set(plano.celulas): raise ValueError('Aba do contrato já existe; aplicação repetida recusada')
    tr=dict(antes={},depois={},entradas=deepcopy(plano.entradas),avisos=deepcopy(plano.avisos),substituicoes=0)
    targets={}
    for aba,cells in plano.celulas.items():
        tr['antes'][aba]={cel:None for cel in cells}
        tr['depois'][aba]=dict(cells)
        maxrow=max(coordinate_from_string(c)[1] for c in cells)
        layout['abas'].append(dict(nome=aba,estado='hidden',linhas=maxrow,colunas=_maxcol(cells),
            padrao=['Roboto',10,'#000000'],fundo_base='#FFFFFF',grade=False,paleta_fixa=True,
            celulas=[[c,v,None] for c,v in cells.items()],mescladas=[],menus=[],condicional=[],
            imagens=[],colunas_larg=[],linhas_alt=[],altura_padrao=15.75,validacao_em_matriz=True,abaixo=True))
    mapping={}
    for meta,owner,table,new in [(fam,fa.DADOS_AM,'formas','formas_personagem'),(fam,fa.DADOS_AM,'alcance','alcance_personagem'),
        (fam,fa.DADOS_AM,'passivas','passivas'),(fam,fa.DADOS_AM,'aptidoes','aptidoes'),
        (inv,iv.DADOS_IV,'formas','formas_entidade'),(inv,iv.DADOS_IV,'alcance','alcance_entidade')]:
        mapping.update(_mapping(meta,owner,table,pontes[new]))
    for i in range(len(inv['fichas_c'])):
        for k in range(2):
            original=inv['D'].faixa('menuf'+str(i),so=k).replace('$','')
            new=pontes['menu_entidade_'+str(i)]
            mapping[(iv.DADOS_IV,original)]=intervalo(new['aba'],new['coluna']+k,new['ultimo']-1)
    for value in mapping.values():
        owner,address=value.rsplit('!',1)
        targets[(owner.strip("'").replace("''","'"),address.replace('$',''))]=True
    cells={a['nome']:{x[0]:x for x in a['celulas']} for a in layout['abas']}
    def por(aba,cel,value):
        old=cells[aba].get(cel)
        antes=old[1] if old else None
        if antes==value: return
        tr['antes'].setdefault(aba,{}).setdefault(cel,antes)
        tr['depois'].setdefault(aba,{})[cel]=value
        if old: old[1]=value
        else:
            old=[cel,value,None];cells[aba][cel]=old
            next(a for a in layout['abas'] if a['nome']==aba)['celulas'].append(old)
    for aba in layout['abas']:
        if aba['nome'] in plano.celulas: continue
        for c,v,*_ in list(aba['celulas']):
            new=cc.troca_refs(v,aba['nome'],mapping)
            new=cp.buscas_literais(new,aba['nome'],set(targets))
            if new!=v:
                por(aba['nome'],c,new);tr['substituicoes']+=1
        for m in aba.get('menus',[]):
            if isinstance(m.get('formula'),str): m['formula']=cc.troca_refs('='+m['formula'],aba['nome'],mapping)[1:]
    # Corrigir o contador sem subtrair o total de gratuitas do catálogo custom:
    # as duas capacidades iniciais continuam automáticas, as novas gratuitas
    # aparecem nas cartas e custam zero escolhas.
    apt=pontes['aptidoes']; apt_range=apt['intervalo']
    consumo=[]
    for g in fam['aptidoes_c']:
        raw=fa._A(g['nome'],fa.AM)
        consumo.append(f'IF({raw}="",0,IFERROR(1-VLOOKUP({criterio(raw)},{apt_range},9,FALSE),1))')
    destino=fam['H']['aptidões anotadas']
    owner,cel=destino.rsplit('!',1)
    por(owner.strip("'"),cel.replace('$',''),'='+('+'.join(consumo) or '0'))
    # A quantidade comprável usa exclusivamente as duas iniciais do livro;
    # não se expande ao cadastrar uma gratuita custom.
    formas=plano.tabelas['forma']
    fonte_ident=intervalo(formas['aba'],formas['colunas']['identidade'],formas['total'])
    fonte_nome=plano.tabelas['forma']['nomes']
    fonte_emb=intervalo(formas['aba'],formas['colunas']['restricao_embutida'],formas['total'])
    for meta,owner,table in [(fam,fa.DADOS_AM,'feit'),(inv,iv.DADOS_IV,'cartas')]:
        aba=next(a for a in layout['abas'] if a['nome']==owner)
        begin=aba['colunas']+1
        _,first,last,_=meta['D'].T[table]
        for r in range(first,last+1):
            raw='$'+L(meta['col']['forma'])+str(r)
            canon='$'+L(begin)+str(r)
            idx=f'MATCH({criterio(raw)},{fonte_nome},0)'
            por(owner,L(begin)+str(r),f'=IFERROR(INDEX({fonte_ident},{idx}),"")')
            emb=f'IFERROR(INDEX({fonte_emb},{idx}),"")'
            embcanon='$'+L(begin+1)+str(r)
            por(owner,L(begin+1)+str(r),'='+_nome_restricao(emb,contrato.restricoes))
            for k in (1,2):por(owner,L(begin+1+k)+str(r),'=$'+L(meta['col']['b'+str(k)])+str(r))
            por(owner,L(begin+4)+str(r),'='+embcanon)
            bb='$'+L(meta['col']['b1'])+str(r)+':$'+L(meta['col']['b2'])+str(r)
            totalbb='$'+L(begin+2)+str(r)+':$'+L(begin+4)+str(r)
            for key,col in meta['col'].items():
                cel=L(col)+str(r); old=cells[owner].get(cel,[None,None])[1]
                new=canonizar_comparacoes(old,raw,canon,{x['nome'] for x in livro_formas(fam)})
                if key!='erros':
                    new=cp.canoniza_contagens(new,bb,totalbb,set(fa.RESTRICOES_CITADAS+fa.FREQUENCIA))
                por(owner,cel,new)
            # Restrição embutida: peso/frequência completos, sem supor que
            # toda Forma traz uma Restrição Média Corpo a Corpo.
            leve=_escolher_restricao(emb,contrato.restricoes,'devolve',1)
            media=_escolher_restricao(emb,contrato.restricoes,'devolve',2)
            if 'dL' in meta['col']:
                cel=L(meta['col']['dL'])+str(r)
                por(owner,cel,'='+cells[owner][cel][1][1:]+'+'+leve)
            cel=L(meta['col']['dM'])+str(r)
            old=cells[owner][cel][1]
            refemb='$'+L(meta['col']['emb'])+str(r)
            por(owner,cel,old.replace('+'+refemb,'+'+media))
            erro=L(meta['col']['erros'])+str(r)
            # A incompatibilidade nomeada diz que uma Forma já traz Corpo a
            # Corpo somente quando esta é a identidade da Restrição embutida.
            olderror=cells[owner][erro][1]
            olderror=olderror.replace(f'AND(COUNTIF({bb},"Corpo a Corpo")>0,{refemb}=1)',
                                     f'AND(COUNTIF({bb},"Corpo a Corpo")>0,{embcanon}="Corpo a Corpo")')
            por(owner,erro,olderror)
            desconhecida=f'IF(AND({raw}<>"",COUNTIF({fonte_nome},{criterio(raw)})=0),"Forma não cadastrada ou com erro: "&{raw},"")'
            extra=_avisos_embutida(meta,r,emb,contrato.restricoes,canon)
            ativo='$'+L(meta['col']['tem'])+str(r)
            por(owner,erro,f'=IF({ativo}=0,"",TEXTJOIN(" · ",TRUE,{cells[owner][erro][1][1:]},{desconhecida},{extra}))')
            if owner==iv.DADOS_IV:
                # Acerto que também exige TR usa a saída normal de ataque e
                # acrescenta a exigência explícita da Forma.
                cel=L(meta['col']['ptr'])+str(r)
                source=intervalo(formas['aba'],formas['colunas']['resolucao'],formas['total'])
                por(owner,cel,cells[owner][cel][1]+f'+IFERROR(N(AND(INDEX({source},{idx})="Acerto",$'+L(meta['col']['tr'])+str(r)+'=1)),0)')
        aba['colunas']=begin+4
        if aba.get('colunas_larg'): aba['colunas_larg'][0][1]=begin+4
    return tr


def livro_formas(fam):
    return fam['R']['formas']


def _escolher_restricao(emb,rs,campo,valor):
    if isinstance(rs,str):
        coluna={'nome':2,'devolve':3,'frequencia':4}[campo]
        return f'IF({emb}="",0,IFERROR(N(VLOOKUP({criterio(emb)},{rs},{coluna},FALSE)={valor}),0))'
    escolhas=[f'{emb}={q(n)}' for n,v in rs.items() if v[campo]==valor]
    return 'N(OR('+','.join(escolhas)+'))' if escolhas else '0'


def _nome_restricao(emb,restricoes):
    if isinstance(restricoes,str):
        return f'IFERROR(VLOOKUP({criterio(emb)},{restricoes},2,FALSE),"")'
    expr='""'
    for n,v in reversed(list(restricoes.items())):expr=f'IF({emb}={q(n)},{q(v["nome"])},{expr})'
    return expr


def _avisos_embutida(meta,r,emb,restricoes,forma_canon):
    col=meta['col']
    selecionadas=['$'+L(col['r'+str(k)])+str(r) for k in (1,2)]
    freq=_escolher_restricao(emb,restricoes,'frequencia',1)
    canonical=['$'+L(col['b'+str(k)])+str(r) for k in (1,2)]
    base_emb=_nome_restricao(emb,restricoes)
    duplicada='OR('+','.join(f'{base_emb}={x}' for x in canonical)+')'
    # Contagens de frequência das duas selecionadas usam seus rótulos e o
    # catálogo vigente já recebido de Melhorias/Restrições.
    fs=[]
    for raw in selecionadas: fs.append(_escolher_restricao(raw,restricoes,'frequencia',1))
    return (f'IF(AND({emb}<>"",{duplicada}),"Restrição repetida, contando a embutida","")'
            f',IF({freq}+{fs[0]}+{fs[1]}>1,"Duas Restrições de frequência, contando a embutida","")'
            f',IF(AND({base_emb}="Tudo ou Nada",${L(col["tr"])}{r}=0),"Tudo ou Nada exige TR","")'
            f',IF(AND({base_emb}="Corpo a Corpo",OR({forma_canon}="Cone",{forma_canon}="Linha")),"Corpo a Corpo não entra em Cone/Linha","")')
