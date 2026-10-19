"""Emissor Sheets/Excel parametrizado: cadastros vivos, herança e catálogos.

Não escolhe posição de CONFIGURAÇÃO, nome de aba nem namespace ANALISE.
O integrador fornece todas as fontes e nomes no Contrato. Fórmulas usam os
mesmos códigos das tabelas canônicas; células de entrada aceitam os rótulos
do estudo (Leve, Sim, Cura...). Este módulo só retorna dados em memória.
"""
from dataclasses import dataclass, field
from copy import deepcopy
from openpyxl.utils import get_column_letter as L

from .motor import CAMPOS, TIPOS, LEGADO_FORMA
from .fontes_livro import FAIXAS


def q(x):
    return '"' + str(x).replace('"', '""') + '"'


def literal(x):
    if isinstance(x, bool):
        return 'TRUE' if x else 'FALSE'
    return str(x) if type(x) in (int, float) else q(x or '')


def ref(aba, cel):
    return "'" + aba.replace("'", "''") + "'!" + cel


def criterio(expr):
    return f'SUBSTITUTE(SUBSTITUTE(SUBSTITUTE({expr},"~","~~"),"*","~*"),"?","~?")'


def intervalo(aba, col, n, largura=1, primeiro=2):
    return ref(aba, f'${L(col)}${primeiro}:${L(col+largura-1)}${n+primeiro-1}')


def numero(x, lo, hi):
    return f'IFERROR(AND(ISNUMBER({x}),NOT(ISLOGICAL({x})),{x}=INT({x}),{x}>={lo},{x}<={hi}),FALSE)'


@dataclass
class Contrato:
    capacidades: dict
    fontes: dict  # grupo -> lista de {campo: referência absoluta da entrada}
    abas: dict   # grupo -> nome reservado pelo integrador
    familias: str  # intervalo dos nomes de Famílias válidas (livro+custom)
    restricoes: object  # dict válido ou tabela viva [rótulo,nome,devolve,frequencia,menu leve]


@dataclass
class Plano:
    celulas: dict = field(default_factory=dict)
    tabelas: dict = field(default_factory=dict)
    entradas: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    validacoes: list = field(default_factory=list)

    def por(self, aba, cel, valor):
        destino = self.celulas.setdefault(aba, {})
        if cel in destino:
            raise ValueError('Célula emitida duas vezes: ' + ref(aba, cel))
        destino[cel] = valor


def _internos(grupo):
    if grupo == 'forma':
        return ('identidade', 'alvos') + tuple('p' + str(n) + '_' + k for n in (1, 2)
                for k in ('dimensao', 'antes', 'depois', 'grau'))
    if grupo == 'aptidao':
        return ('identidade', 'extensao', 'escala', 'automatica')
    return ('identidade',)


def _registro_livro(grupo, g):
    out = deepcopy(g)
    if grupo == 'forma':
        for n in (1, 2):
            p = g['partes'][n-1] if len(g['partes']) >= n else {}
            for k in ('dimensao', 'antes', 'depois', 'grau'):
                out[f'p{n}_{k}'] = p.get(k, 0 if k == 'grau' else '')
            if p.get('fixo') is not None:
                out[f'p{n}_antes'], out[f'p{n}_depois'] = '', ''
    return out


def _normalizar(campo, expr):
    if campo in ('exige_tr', 'classe_0'):
        return f'IF({expr}="Sim",TRUE,IF({expr}="Não",FALSE,{expr}))'
    return expr


def emitir(livro, contrato):
    """Gera as três tabelas; nenhuma aba de produção é alterada aqui."""
    p = Plano()
    if len(set(contrato.abas.values())) != 3:
        raise ValueError('Cada catálogo precisa de aba própria reservada pelo contrato')
    for grupo, campos in CAMPOS.items():
        cap, fontes = contrato.capacidades[grupo], contrato.fontes[grupo]
        if type(cap) is not int or not 1 <= cap <= 30 or len(fontes) != cap:
            raise ValueError('Capacidade/fontes incoerentes: ' + grupo)
        if any(set(f) != set(campos) for f in fontes):
            raise ValueError('Fontes incompletas ou fora do contrato: ' + grupo)
        aba, book = contrato.abas[grupo], livro[grupo]
        internos = _internos(grupo)
        efetivos = campos + internos
        inicio = len(campos) + 4
        total = len(book) + cap
        col = {k: inicio+i for i, k in enumerate(efetivos)}
        rawcol = {k: i+1 for i, k in enumerate(campos)}
        errocol, basecol, ativocol = len(campos)+1, len(campos)+2, len(campos)+3
        for i, k in enumerate(campos, 1):
            p.por(aba, L(i)+'1', 'entrada.'+k)
        for i, k in [(errocol,'aviso'),(basecol,'linha_base'),(ativocol,'ativo')]:
            p.por(aba,L(i)+'1',k)
        for k, i in col.items():
            p.por(aba, L(i)+'1', k)
        e = lambda k, r: '$'+L(col[k])+str(r)
        raw = lambda k, r: '$'+L(rawcol[k])+str(r)
        tabela = intervalo(aba, inicio, total, len(efetivos))
        nomes = intervalo(aba,col['nome'],total)
        nomes_livro = intervalo(aba,col['nome'],len(book))
        nomes_raw = intervalo(aba,rawcol['nome'],cap)
        p.tabelas[grupo] = dict(aba=aba, inicio=inicio, campos=efetivos, colunas=col,
                               total=total, livro=len(book), catalogo=tabela, nomes=nomes,
                               nomes_livro=nomes_livro, erros=intervalo(aba,errocol,cap),
                               primeiro_custom=len(book)+2)
        for row, item in enumerate(book, 2):
            g = _registro_livro(grupo,item)
            for k in efetivos:
                value = g.get(k,'')
                # INDEX de célula nativamente vazia vira zero no Sheets.
                # Uma base sem texto deve herdar texto vazio, inclusive nas
                # dimensões que aquela Forma não usa.
                p.por(aba,L(col[k])+str(row),'=""' if value in (None,'') else value)
        for slot, fonte in enumerate(fontes, 1):
            r, dst = slot+1, len(book)+slot+1
            for k in campos:
                f = fonte[k]
                p.por(aba,L(rawcol[k])+str(r),f'=IF(ISBLANK({f}),"",{f})')
                p.entradas.append(dict(grupo=grupo,vaga=slot,campo=k,fonte=f))
            b, nome, base = '$'+L(basecol)+str(r), raw('nome',r), raw('base',r)
            ativo = '$'+L(ativocol)+str(r)
            p.por(aba,L(basecol)+str(r),f'=IF(OR({base}="",{base}="Nenhuma"),0,IFERROR(MATCH({criterio(base)},{nomes_livro},0),-1))')
            testes_ativos = [f'{raw(k,r)}<>""' for k in campos if k not in ('tipo','mestre_viu')]
            testes_ativos += [f'AND({raw("mestre_viu",r)}<>"",{raw("mestre_viu",r)}<>FALSE)',
                              'AND('+','.join(f'{raw("tipo",r)}<>{q(x)}' for x in ('',)+TIPOS[grupo])+')']
            p.por(aba,L(ativocol)+str(r),'=OR('+','.join(testes_ativos)+')')
            exprs = {}
            for k in campos:
                v = raw(k,r)
                herdada = f'IF({b}>0,INDEX({intervalo(aba,col[k],len(book))},MAX(1,{b})),{_padrao(grupo,k)})'
                expr = f'IF({v}="",{herdada},{v})'
                if k in ('peso','resultado'):
                    labels = ('Sem custo','Leve','Média','Pesada') if k=='peso' else ('Dano','Cura','Vida temporária','Efeito')
                    normal = v
                    for codigo, label in reversed(list(enumerate(labels))):
                        normal = f'IF({v}={q(label)},{codigo},{normal})'
                    expr = f'IF({v}="",{herdada},{normal})'
                elif k in ('exige_tr','classe_0'):
                    expr = f'IF({v}="",{herdada},{_normalizar(k,v)})'
                elif k in ('familia','restricao_embutida'):
                    expr = f'IF({v}="Nenhuma","",{expr})'
                if grupo=='forma' and k in LEGADO_FORMA:expr=herdada
                exprs[k] = expr
            # Validação lê valores resolvidos auxiliares, inclusive quando o
            # registro é inválido. O catálogo público só lê uma linha sem erro.
            # Auxiliares ficam após o catálogo, impedindo ciclos com a exclusão.
            aux_ini = inicio + len(efetivos) + 2
            resolved = {k:'$'+L(aux_ini+i)+str(r) for i,k in enumerate(efetivos)}
            for i,k in enumerate(efetivos):
                if k in exprs:
                    expr = exprs[k]
                elif k == 'automatica':
                    expr = 'FALSE'
                else:
                    default = _interno_padrao(grupo,k)
                    if grupo=='forma' and k=='p2_grau':
                        default='2'
                    expr = f'IF({b}>0,INDEX({intervalo(aba,col[k],len(book))},MAX(1,{b})),{default})'
                    if grupo=='forma' and k.startswith('p2_'):
                        # Campos de uma dimensão nova também funcionam sobre
                        # uma base de um componente, sem apagar o herdado.
                        p1=f'INDEX({intervalo(aba,col["p1_dimensao"],len(book))},MAX(1,{b}))'
                        p2=f'INDEX({intervalo(aba,col["p2_dimensao"],len(book))},MAX(1,{b}))'
                        tests={d:'OR('+','.join(raw(f'{d}_{c}_{f}',r)+'<>""' for c,fs in FAIXAS.items() for f in fs)+')'
                               for d in ('alcance','area')}
                        novo=f'IF(AND({p1}="alcance",{tests["area"]}),"area",IF(AND({p1}="area",{tests["alcance"]}),"alcance",""))'
                        campo=k[3:]
                        valor={'dimensao':novo,'antes':f'IF({novo}="alcance"," · alcance ",IF({novo}="area"," · área ",""))',
                               'depois':'""','grau':f'IF({novo}="",0,IF({novo}="alcance",1,2))'}[campo]
                        expr=f'IF(AND({b}>0,{p2}=""),{valor},{expr})'
                p.por(aba,L(aux_ini+i)+str(r),'='+expr)
            erros = _erros(grupo, raw, r, resolved, b, nome, nomes_raw, nomes_livro, contrato, livro)
            err = '$'+L(errocol)+str(r)
            checkcol=aux_ini+len(efetivos)+1
            for i,expr in enumerate(erros):
                p.por(aba,L(checkcol+i)+str(r),'='+expr)
            checks='$'+L(checkcol)+str(r)+':$'+L(checkcol+len(erros)-1)+str(r)
            p.por(aba,L(errocol)+str(r),f'=IF({ativo},TEXTJOIN(" · ",TRUE,{checks}),"")')
            p.avisos.append(dict(grupo=grupo,vaga=slot,fonte=ref(aba,err)))
            for k in efetivos:
                vazio = 'FALSE' if k in ('mestre_viu','exige_tr','classe_0','automatica','extensao') else (
                    '0' if k in ('peso','resultado','ce','nivel_minimo','refino_minimo','alvos','p1_grau','p2_grau') else '""')
                p.por(aba,L(col[k])+str(dst),f'=IF(AND({ativo},{err}=""),{resolved[k]},{vazio})')
            for k, opcoes in opcoes_campos(grupo,livro).items():
                p.validacoes.append(dict(fonte=fonte[k],opcoes=opcoes))
    return p


def _padrao(grupo,k):
    if k=='tipo' and grupo != 'aptidao': return q(TIPOS[grupo][0])
    if k=='mestre_viu': return 'FALSE'
    if k=='ce' and grupo=='aptidao': return q('—')
    if k in ('nivel_minimo','refino_minimo'): return '1'
    if k=='escolha': return q('Consome uma escolha')
    if k=='rota': return q('Todas')
    if grupo=='forma' and k in ('resultado','exige_tr','resolucao'):
        return {'resultado':'0','exige_tr':'FALSE','resolucao':q('Automático')}[k]
    if k.endswith('_escada'): return q('Fixo')
    return '""'


def _interno_padrao(grupo,k):
    if k=='alvos' or k=='extensao': return '0'
    if k.startswith('p') and '_' in k:
        n, campo = k[1:].split('_',1)
        return literal(dict(dimensao='alcance' if n=='1' else 'area', antes='' if n=='1' else ' · área ',
                            depois='',grau=int(n))[campo])
    return '""'


def opcoes_campos(grupo,livro):
    out = dict(tipo=list(TIPOS[grupo]), base=['Nenhuma']+[x['nome'] for x in livro[grupo]])
    if grupo=='forma':
        out.update(peso=['Sem custo','Leve','Média','Pesada'],classe_0=['Sim','Não'],
                   alcance_escada=['Fixo','alcance'],area_escada=['Fixo','raio','comprimento','linha'])
    elif grupo=='aptidao':
        out.update(ce=['—',1,2,3],nivel_minimo=list(range(1,31)),refino_minimo=list(range(1,11)),
                   escolha=['Consome uma escolha','Gratuita'])
    else:
        out.update(ce=[1,2,3],rota=['Todas','Fundamento / Manejos','Técnica Marcial'])
    return out


def _erros(grupo,raw,r,x,b,nome,nomes_raw,nomes_livro,contrato,livro):
    def falha(ok,msg): return f'IF({ok},"",{q(msg)})'
    erros = [falha(f'AND(ISTEXT({nome}),{nome}<>"",TRIM({nome})={nome})','NOME precisa ser texto sem espaços nas pontas'),
             falha(f'COUNTIF({nomes_raw},{criterio(nome)})+COUNTIF({nomes_livro},{criterio(nome)})=1','Nome repetido no livro ou custom'),
             falha(f'{b}>=0','BASE DO LIVRO inválida para o grupo'),
             falha('OR('+','.join(f'{x["tipo"]}={q(t)}' for t in TIPOS[grupo])+')','TIPO inválido para o grupo'),
             falha(f'ISLOGICAL({x["mestre_viu"]})','MESTRE VIU precisa ser caixa de seleção')]
    for k in ('efeito','requisitos'):
        erros.append(falha(f'ISTEXT({x[k]})',k.upper()+' precisa ser texto'))
    if grupo=='forma':
        for k in ('peso',): erros.append(falha(numero(x[k],0,3),k.upper()+' exige 0/1/2/3'))
        for k in ('classe_0',): erros.append(falha(f'ISLOGICAL({x[k]})',k.upper()+' exige Sim/Não'))
        erros.append(falha(f'OR({x["familia"]}="",COUNTIF({contrato.familias},{criterio(x["familia"])})>0)','FAMÍLIA não cadastrada ou inválida'))
        if isinstance(contrato.restricoes,str):
            valido=f'IFERROR(MATCH({criterio(x["restricao_embutida"])},INDEX({contrato.restricoes},0,1),0),0)>0'
        else:
            restr = ','.join(f'{x["restricao_embutida"]}={q(t)}' for t in contrato.restricoes)
            valido=f'OR(FALSE{","+restr if restr else ""})'
        for d, escadas in [('alcance',('Fixo','alcance')),('area',('Fixo','raio','comprimento','linha'))]:
            esc = x[d+'_escada']
            erros.append(falha('OR('+','.join(f'{esc}={q(t)}' for t in escadas)+')','ESCADA inválida para '+d))
            for c,faixas in FAIXAS.items():
                for f in faixas:
                    valor=x[f'{d}_{c}_{f}']
                    exigivel=f'OR({x["p1_dimensao"]}={q(d)},{x["p2_dimensao"]}={q(d)})'
                    if f=='classe_0': exigivel=f'AND({x["classe_0"]},{exigivel})'
                    if d=='alcance': erros.append(falha(f'OR(NOT({exigivel}),{valor}<>"")','Base de alcance ausente: '+c+'/'+f))
                    # Medidas são texto; 0/False não viram string vazia.
                    erros.append(falha(f'ISTEXT({valor})','Base precisa ser texto: '+d+'/'+c+'/'+f))
                    medida=f'LEFT({valor},MAX(0,LEN({valor})-2))'
                    num=f'IFERROR(VALUE(SUBSTITUTE({medida},",",""))/10^IFERROR(LEN({medida})-FIND(",",{medida}),0),-1)'
                    valid=f'AND(RIGHT({valor},2)=" m",{num}>0)'
                    for ladder in escadas[1:]:
                        last=livro['escadas'][ladder][-1]
                        if ladder=='linha':continue
                        if last.endswith(' m'):
                            teto=float(last[:-2].replace(',','.'))
                            valid=f'AND({valid},OR({esc}<>{q(ladder)},{num}<={teto}))'
                    linha_valida=f'IFERROR(AND(REGEXMATCH({valor},"^[0-9]+(?:,[0-9]+)? × [0-9]+(?:,[0-9]+)? m$"),VALUE(REGEXEXTRACT({valor},"^[0-9]+(?:,[0-9]+)?"))>0,VALUE(REGEXEXTRACT({valor},"^[0-9]+(?:,[0-9]+)?"))<=60,VALUE(REGEXEXTRACT({valor},"× ([0-9]+(?:,[0-9]+)?) m$"))>0,VALUE(REGEXEXTRACT({valor},"× ([0-9]+(?:,[0-9]+)?) m$"))<=4.5),FALSE)'
                    valid=f'IF({esc}="linha",{linha_valida},{valid})'
                    erros.append(falha(f'OR(NOT({exigivel}),{esc}="Fixo",{valor}="",{valor}="—",{valid})','Base incompatível com escada: '+d+'/'+c+'/'+f))
    else:
        ce=x['ce']
        ok=numero(ce,1,3)
        if grupo=='aptidao': ok=f'OR({ce}="—",{ok})'
        erros.append(falha(ok,'CE inválida'))
        if grupo=='aptidao':
            book_tipo=intervalo(contrato.abas[grupo],len(CAMPOS[grupo])+4,len(livro[grupo]))
            erros.append(falha(f'OR({b}<=0,{x["tipo"]}=INDEX({book_tipo},MAX(1,{b})))','TIPO deve preservar a rota da base'))
            for k,hi in [('nivel_minimo',30),('refino_minimo',10)]: erros.append(falha(numero(x[k],1,hi),k+' fora do limite'))
            erros.append(falha(f'OR({x["escolha"]}="Gratuita",{x["escolha"]}="Consome uma escolha")','ESCOLHA inválida'))
        else:
            erros.append(falha('OR('+','.join(f'{x["rota"]}={q(t)}' for t in ('Todas','Fundamento / Manejos','Técnica Marcial'))+')','ROTA inválida'))
    return erros


def exportar(plano, nome_chave):
    """Callback obrigatório fecha os namespaces fora deste módulo.

    nome_chave(grupo,vaga,campo,aviso) -> chave aprovada pelo integrador.
    Não modifica formato.versao e recusa colisões dentro desta entrega.
    """
    linhas=[]
    for entrada in plano.entradas:
        g,n,k,f=entrada['grupo'],entrada['vaga'],entrada['campo'],entrada['fonte']
        valor=f'=IF(ISBLANK({f}),"",{f}&"")' if k!='mestre_viu' else f'=N({f})&""'
        linhas.append([nome_chave(g,n,k,False),valor,f.replace('$',''),'configuração'])
    for aviso in plano.avisos:
        f=aviso['fonte']
        linhas.append([nome_chave(aviso['grupo'],aviso['vaga'],'',True),'='+f+'&""',f.replace('$',''),'aviso'])
    keys=[x[0] for x in linhas]
    if len(set(keys))!=len(keys) or 'formato.versao' in keys or any(not isinstance(k,str) or not k for k in keys):
        raise ValueError('Contrato de exportação vazio, duplicado ou tenta escolher versão')
    return linhas
