"""Catálogos e contas sem endereços, versão ANALISE ou rede.

Interface proposta: compilar(livro, registros, capacidades, familias) retorna
cadastros crus, avisos e pools válidos. Um cadastro é compartilhado por todos
os consumidores. Vazio herda; zero/False são escolhas explícitas.
"""
from collections import Counter
from copy import deepcopy
from .medidas_r53 import linha,ordem_linha
from dataclasses import dataclass, field
import math
import re

from .fontes_livro import FAIXAS

COMUNS = ('tipo', 'nome', 'base', 'mestre_viu', 'requisitos', 'efeito')
FORMAS = ('familia', 'peso', 'resolucao', 'resultado', 'exige_tr', 'classe_0',
          'restricao_embutida', 'alcance_escada', 'area_escada') + tuple(
    f'{d}_{c}_{f}' for d in ('alcance', 'area') for c, faixas in FAIXAS.items() for f in faixas)
CAMPOS = {'forma': COMUNS + FORMAS,
          'aptidao': COMUNS + ('ce', 'nivel_minimo', 'refino_minimo', 'escolha'),
          'talento': COMUNS + ('ce', 'rota')}
TIPOS = {'forma': ('Forma',), 'aptidao': ('Aptidão', 'Bênção'), 'talento': ('Talento',)}
LEGADO_FORMA = ('resolucao', 'resultado', 'exige_tr', 'restricao_embutida')


def vazio(x):
    return x is None or (isinstance(x, str) and x == '')


def chave(x):
    return x.casefold() if isinstance(x, str) else str(x).casefold()


def inteiro(x, lo, hi):
    return type(x) is int and lo <= x <= hi


def metros(x):
    if not isinstance(x, str):
        return None
    m = re.fullmatch(r'(\d+(?:,\d+)?) m', x)
    return float(m[1].replace(',', '.')) if m else None


def subir(escada, base, graus):
    if not inteiro(graus, 0, 1000):
        raise ValueError('Degraus precisam ser inteiros não negativos')
    if base in escada:
        i = escada.index(base)
    elif graus == 0:
        return base
    else:
        num=ordem_linha if any(linha(x) for x in escada) else metros
        b=num(base)
        candidatos=[k for k,x in enumerate(escada) if num(x) is None or (b is not None and num(x)>=b)]
        if b is None or not candidatos:
            raise ValueError('Base incompatível com a escada: ' + str(base))
        i = candidatos[0] - 1
    return escada[min(len(escada) - 1, i + graus)]


@dataclass
class Catalogos:
    crus: dict
    avisos: dict
    pools: dict
    livro: dict

    def obter(self, grupo, nome):
        return next((deepcopy(x) for x in self.pools[grupo] if chave(x['nome']) == chave(nome)), None)


def compilar(livro, registros, capacidades, familias=(), restricoes=None):
    """Capacidades são obrigatórias e pertencem ao contrato do integrador."""
    if restricoes is not None:
        livro=deepcopy(livro)
        livro['restricoes'].update(deepcopy(restricoes))
    crus, avisos, pools = {}, {}, {}
    familias = {chave(x) for x in list(livro['familias']) + list(familias)}
    for grupo in CAMPOS:
        cap = capacidades[grupo]
        if not inteiro(cap, 1, 30):
            raise ValueError('Capacidade deve ser pequena, explícita e entre 1 e 30: ' + grupo)
        entrada = registros.get(grupo, [])
        if len(entrada) > cap:
            raise ValueError('Registros excedem capacidade de ' + grupo)
        crus[grupo] = deepcopy(entrada) + [{} for _ in range(cap - len(entrada))]
        avisos[grupo], pools[grupo] = [], deepcopy(livro[grupo])
        nomes = Counter(chave(x.get('nome', '')) for x in crus[grupo] if not vazio(x.get('nome')))
        bases = {chave(x['nome']): x for x in livro[grupo]}
        for n, raw in enumerate(crus[grupo], 1):
            erros = []
            ativo = any(not vazio(v) and not (k == 'mestre_viu' and v is False)
                        and not (k == 'tipo' and v in TIPOS[grupo])
                        for k, v in raw.items())
            if not ativo:
                avisos[grupo].append(())
                continue
            nome = raw.get('nome', '')
            if not isinstance(nome, str) or not nome or nome != nome.strip():
                erros.append('NOME precisa ser texto sem espaços nas pontas')
            if nomes[chave(nome)] > 1 or chave(nome) in bases:
                erros.append('Nome repetido no livro ou custom')
            if any(k not in CAMPOS[grupo] for k in raw):
                erros.append('Campo fora do contrato')
            base = raw.get('base')
            herdada = None if vazio(base) or base == 'Nenhuma' else bases.get(chave(base))
            if not vazio(base) and base != 'Nenhuma' and herdada is None:
                erros.append('BASE DO LIVRO inválida para o grupo')
            out = deepcopy(herdada) if herdada else {}
            for k, v in raw.items():
                if not vazio(v):
                    out[k] = v
            out.update(nome=nome, base=herdada['nome'] if herdada else '', origem='custom', vaga=n,
                       identidade=herdada['identidade'] if herdada else '', automatica=False)
            out.setdefault('tipo', TIPOS[grupo][0] if grupo != 'aptidao' else '')
            if out['tipo'] not in TIPOS[grupo]:
                erros.append('TIPO inválido para o grupo')
            if type(out.setdefault('mestre_viu', False)) is not bool:
                erros.append('MESTRE VIU precisa ser caixa de seleção')
            for k in ('efeito', 'requisitos'):
                out.setdefault(k, '')
                if not isinstance(out[k], str):
                    erros.append(k.upper() + ' precisa ser texto')
            if grupo == 'forma':
                _forma(out, herdada, livro, familias, erros)
            elif grupo == 'aptidao':
                if herdada and out['tipo'] != herdada['tipo']:
                    erros.append('TIPO deve preservar a rota da base escolhida')
                out.setdefault('ce', '—')
                out.setdefault('nivel_minimo', 1)
                out.setdefault('refino_minimo', 1)
                out.setdefault('escolha', 'Consome uma escolha')
                if not (out['ce'] == '—' or inteiro(out['ce'], 1, 3)):
                    erros.append('CE deve ser — ou 1/2/3')
                for k, hi in [('nivel_minimo', 30), ('refino_minimo', 10)]:
                    if not inteiro(out[k], 1, hi):
                        erros.append(k + ' fora do limite')
                if out['escolha'] not in ('Consome uma escolha', 'Gratuita'):
                    erros.append('ESCOLHA deve declarar consumo ou gratuidade')
            else:
                out.setdefault('rota', 'Todas')
                if not inteiro(out.get('ce'), 1, 3):
                    erros.append('Talento exige CE 1/2/3')
                if out['rota'] not in ('Todas', 'Fundamento / Manejos', 'Técnica Marcial'):
                    erros.append('ROTA inválida')
            avisos[grupo].append(tuple(erros))
            if not erros:
                pools[grupo].append(out)
    return Catalogos(crus, avisos, pools, livro)


def _forma(out, base, livro, familias, erros):
    # R53: function and resolution belong to each application, not its shape.
    # Retain legacy fields only for old exports and recovery, never as gates.
    for k,default in [('resultado',0),('resolucao','Automático'),('exige_tr',False),('restricao_embutida','')]:
        out[k]=base.get(k,default) if base else default
    for k, lo, hi in [('peso', 0, 3)]:
        if not inteiro(out.get(k), lo, hi):
            erros.append(k.upper() + ' exige código explícito 0/1/2/3')
    for k in ('classe_0',):
        if type(out.get(k)) is not bool:
            erros.append(k.upper() + ' exige Sim/Não explícito')
    out.setdefault('familia', '')
    if out['familia'] == 'Nenhuma':
        out['familia'] = ''
    if out['familia'] and chave(out['familia']) not in familias:
        erros.append('FAMÍLIA não cadastrada ou inválida')
    out.setdefault('restricao_embutida', '')
    if out['restricao_embutida'] == 'Nenhuma':
        out['restricao_embutida'] = ''
    # Sem base: alcance e área são componentes independentes. Formatação livre
    # permanece no efeito, sem virar instrução executável.
    if not base:
        out['partes'] = [dict(dimensao='alcance', antes='', depois='', grau=1, fixo=None),
                         dict(dimensao='area', antes=' · área ', depois='',
                              grau=2, fixo=None)]
        out['alvos'] = 0
    else:
        for d in ('alcance','area'):
            usa=any(p['dimensao']==d for p in out['partes'])
            valores=[out.get(f'{d}_{c}_{f}') for c,fs in FAIXAS.items() for f in fs]
            if not usa and any(not vazio(v) for v in valores):
                out['partes'].append(dict(dimensao=d,antes=' · '+('alcance' if d=='alcance' else 'área')+' ',
                    depois='',grau=1 if d=='alcance' else 2,fixo=None))
    for d in ('alcance', 'area'):
        out.setdefault(d + '_escada', 'Fixo')
        escada = out[d + '_escada']
        permitidas = ('Fixo', 'alcance') if d == 'alcance' else ('Fixo', 'raio', 'comprimento', 'linha')
        if escada not in permitidas:
            erros.append('ESCADA inválida para ' + d)
            continue
        for contexto, faixas in FAIXAS.items():
            for faixa in faixas:
                k = f'{d}_{contexto}_{faixa}'
                out.setdefault(k, '')
                valor = out[k]
                if not isinstance(valor, str):
                    erros.append(k + ' precisa ser texto')
                    continue
                if faixa == 'classe_0' and not out.get('classe_0'):
                    continue
                usa_dimensao = any(p['dimensao'] == d for p in out['partes'])
                if d == 'alcance' and usa_dimensao and not valor:
                    erros.append('Base de alcance ausente: ' + contexto + '/' + faixa)
                if escada != 'Fixo' and valor not in ('', '—'):
                    if escada=='linha':
                        v=linha(valor);lim=linha(livro['escadas'][escada][-1])
                        if not v or min(v)<=0 or any(a>b for a,b in zip(v,lim)):erros.append('Base incompatível com escada: '+k)
                        continue
                    num = metros(valor)
                    if num is None or num <= 0 or (metros(livro['escadas'][escada][-1]) is not None
                                                  and num > metros(livro['escadas'][escada][-1])):
                        erros.append('Base incompatível com escada: ' + k)
    # Base fixa também pode ser substituída; sem substituição mantém o texto.
    for p in out['partes']:
        if p['fixo'] is not None:
            p['antes'], p['depois'], p['fixo'] = '', '', None


@dataclass
class Contexto:
    rota: int = 1  # Fundamento / Sem Técnica / TM com energia / TM sem energia
    nivel: int = 1
    refino: int = 1
    escolhas: int = 0  # orçamento existente, descontadas as duas iniciais
    leques: int = 0
    espacos: int = 0  # livres após Domínio/invocações/Regra, fornecidos pelo núcleo
    atributos: dict = field(default_factory=dict)
    origem: str = ''
    historia_treinada: bool = False
    aprendizado: frozenset = frozenset()
    voto_iniciante: bool = False
    tecnica_inata: bool = False
    concessoes: frozenset = frozenset()  # exceções já aprovadas pelo núcleo, por identidade


def menu(cat, grupo, contexto=None, familias_abertas=None, classe=None):
    items = cat.pools[grupo]
    if grupo == 'forma':
        abertas = None if familias_abertas is None else {chave(x) for x in familias_abertas}
        items = [x for x in items if (classe != 0 or x['classe_0']) and
                 (abertas is None or not x.get('familia') or chave(x['familia']) in abertas)]
    elif contexto is not None:
        if grupo == 'aptidao':
            items = [x for x in items if not x.get('automatica') and
                     (x['tipo'] == 'Bênção') == (contexto.rota == 4) and
                     not (contexto.origem == 'Corpo Amaldiçoado' and x.get('extensao'))]
        else:
            items = [x for x in items if x['rota'] == 'Todas' or contexto.rota == 2 or
                     (x['rota'] == 'Fundamento / Manejos' and contexto.rota == 1) or
                     (x['rota'] == 'Técnica Marcial' and contexto.rota in (3, 4))]
    return [x['nome'] for x in items]


def forma(cat, nome, contexto, classe, *, longe=0, maior=0, livre=False,
          familias_abertas=None, melhorias=0, restricoes=(), pessoal=False, maxima=False):
    if contexto not in FAIXAS or not inteiro(classe, 0, 7):
        raise ValueError('Contexto/Classe inválido')
    f = cat.obter('forma', nome)
    if not f:
        return dict(avisos=['Forma não cadastrada ou com erro'], valido=False)
    avisos = []
    if chave(nome) not in {chave(x) for x in menu(cat, 'forma', familias_abertas=familias_abertas, classe=classe)}:
        avisos.append('Forma indisponível na Classe/Família')
    faixa = FAIXAS[contexto][0 if classe == 0 else 1 if classe <= 5 else 2 if contexto == 'personagem' or classe == 6 else 3]
    partes = []
    for p in f['partes']:
        d = p['dimensao']
        b = f.get(f'{d}_{contexto}_{faixa}', '')
        if not b:
            partes.append('')
            continue
        escada = f[d + '_escada']
        graus = (0, longe, maior, longe + maior)[p['grau']]
        v = b if escada == 'Fixo' or b == '—' else subir(cat.livro['escadas'][escada], b, graus)
        partes.append('—' if v == '—' else p['antes'] + v + p['depois'].replace('em você', 'nela') if contexto == 'entidade'
                      else '—' if v == '—' else p['antes'] + v + p['depois'])
    emb = cat.livro['restricoes'].get(f.get('restricao_embutida'))
    selecionadas = [cat.livro['restricoes'].get(x) for x in restricoes]
    if any(x is None for x in selecionadas):
        avisos.append('Restrição não cadastrada ou com erro')
    todas = [x for x in selecionadas if x] + ([emb] if emb else [])
    if len(todas) > 2 and classe > 0:
        avisos.append('Limite de duas Restrições, contando a embutida')
    if sum(x['frequencia'] for x in todas) > 1:
        avisos.append('Duas Restrições de frequência')
    ids = [x['nome'] for x in todas]
    if len(ids) != len(set(ids)):
        avisos.append('Restrição repetida, contando a embutida')
    if 'Queima-Roupa' in ids and (f['identidade'] in ('Toque','Aura') or pessoal):
        avisos.append('Queima-Roupa incompatível com Toque/Aura ou aplicação pessoal')
    if longe and (f['identidade'] in ('Toque','Aura') or 'Queima-Roupa' in ids):
        avisos.append('Longe incompatível com proximidade')
    exige_tr=f['exige_tr'] or f['resolucao']=='TR, metade'
    if 'Tudo ou Nada' in ids and not exige_tr:
        avisos.append('Tudo ou Nada exige TR')
    custo = 0 if classe == 0 or f['peso'] == 0 else math.ceil(classe * f['peso'] / 2)
    # R53: nem a Forma publicada nem a custom recebe desconto de Família Livre.
    toque=math.ceil(classe/2) if classe>0 and f['identidade']=='Toque' and not pessoal and not maxima else 0
    devs=[math.ceil(classe*(2 if x['nome']=='Queima-Roupa' and f['identidade']=='Projétil' else x['devolve'])/2) for x in todas]
    devolucao=0 if maxima else min(2*classe,sum(devs)+toque)
    utilizada = min(devolucao, melhorias)  # nunca paga a Forma
    return dict(nome=f['nome'], identidade=f['identidade'], custo=custo,
                resolucao=f['resolucao'], resultado=f['resultado'], exige_tr=exige_tr,
                alcance=''.join(partes), componentes=partes, restricao_embutida=emb,
                devolucao=devolucao, utilizada=utilizada, perdida=devolucao-utilizada,
                efeito=f['efeito'], requisitos=f['requisitos'], avisos=avisos, valido=not avisos)


def aptidoes(cat, nomes, ctx):
    avisos, identidades, compradas, cartas = [], [], 0, []
    for pos, nome in enumerate(nomes, 1):
        if vazio(nome):
            continue
        a = cat.obter('aptidao', nome)
        if not a:
            avisos.append(f'Aptidão {pos}: não cadastrada ou com erro')
            continue
        ident = a['identidade'] or a['nome']
        if chave(nome) not in {chave(x) for x in menu(cat, 'aptidao', ctx)}:
            avisos.append(f'Aptidão {pos}: rota/origem incompatível ou capacidade inicial automática')
        # Aliases da mesma base não contornam a proibição de repetição.
        grupo = 'Aptidão Própria' if ident.startswith('Aptidão Própria (') else 'Bênção Própria' if ident.startswith('Bênção Própria (') else ident
        if chave(grupo) in {chave(x) for x in identidades}:
            avisos.append(f'Aptidão {pos}: repetida')
        anteriores = {chave(x) for x in identidades}
        if ident not in ctx.concessoes:
            minimo = max(a.get('refino_minimo', 1), {1: 1, 2: 4, 3: 7}.get(a['ce'], 1) if a['tipo'] == 'Bênção' else 1)
            if ident == 'Domínio Simples' and ctx.voto_iniciante:
                minimo = 4 if a.get('origem') == 'livro' else max(4, minimo if minimo != 5 else 4)
            if ctx.nivel < a.get('nivel_minimo', 1) or ctx.refino < minimo:
                avisos.append(f'Aptidão {pos}: nível ou Refino/Lapidação insuficiente')
            for pred in a.get('predecessoras', ()):
                if chave(pred) not in anteriores:
                    avisos.append(f'Aptidão {pos}: exige {pred} anterior')
            atr = a.get('atributo')
            if atr and ctx.atributos.get(atr[0], 0) < atr[1]:
                avisos.append(f'Aptidão {pos}: exige {atr[0]} {atr[1]}')
            if ident == 'Represália' and max(ctx.atributos.get('Força', 0), ctx.atributos.get('Destreza', 0)) < 4:
                avisos.append(f'Aptidão {pos}: exige Força ou Destreza 4')
            if ident == 'Cesta Oca de Vime' and not (ctx.origem == 'Encarnado' or ctx.historia_treinada):
                avisos.append(f'Aptidão {pos}: exige Encarnado ou treino em História')
            if ident in ('Domínio Simples', 'Extensão de Domínio') and ident not in ctx.aprendizado:
                avisos.append(f'Aptidão {pos}: aprendizado não registrado')
            if ident == 'Pétala' and not (ctx.origem == 'Descendente' or ident in ctx.aprendizado):
                avisos.append(f'Aptidão {pos}: exige Descendente ou aprendizado de clã')
            if ident == 'Ritual' and not ctx.tecnica_inata:
                avisos.append(f'Aptidão {pos}: exige Técnica Inata')
        identidades.append(grupo)
        consome = int(a['escolha'] != 'Gratuita')
        compradas += consome
        cartas.append(dict(nome=nome, ce=a['ce'], escolha=a['escolha'], consumo=consome,
                           requisitos=a['requisitos'], efeito=a['efeito']))
    if compradas > ctx.escolhas:
        avisos.append(f'Escolhas de Aptidão/Bênção excedidas: {compradas} de {ctx.escolhas}')
    return dict(consumo=compradas, cartas=cartas, avisos=avisos)


def talentos(cat, pagos, leque, ctx):
    cartas, avisos, custo = [], [], 0
    for origem, nomes in [('pago', pagos), ('leque', leque)]:
        for pos, nome in enumerate(nomes, 1):
            if vazio(nome):
                continue
            t = cat.obter('talento', nome)
            if not t:
                avisos.append(f'Talento {origem} {pos}: não cadastrado ou com erro')
                continue
            if chave(nome) not in {chave(x) for x in menu(cat, 'talento', ctx)}:
                avisos.append(f'Talento {origem} {pos}: rota incompatível')
            if ctx.nivel < cat.livro['nivel_ce'][t['ce']]:
                avisos.append(f'Talento {origem} {pos}: exige nível {cat.livro["nivel_ce"][t["ce"]]}')
            if origem == 'leque' and pos > ctx.leques:
                avisos.append(f'Talento Leque {pos}: vaga não liberada')
            custo += t['ce'] if origem == 'pago' else 0
            cartas.append(dict(nome=nome, ce=t['ce'], custo=t['ce'] if origem == 'pago' else 0,
                               requisitos=t['requisitos'], efeito=t['efeito']))
    if sum(not vazio(n) for n in pagos) > 5:
        avisos.append('Máximo de cinco Talentos pagos')
    if custo > ctx.espacos:
        avisos.append(f'Espaços de Talentos excedidos: {custo} de {ctx.espacos}')
    return dict(custo=custo, cartas=cartas, avisos=avisos)
