"""Validação aditiva do domínio; preserva aquisição, cartões e versões.

Aplicada após o layout final. Cada cartão normal é uma identidade conhecida:
suas sete versões não são sete aquisições. Escolhas próprias da Trilha,
básicas, Liberações e Máxima não entram no orçamento básico de especiais.
"""
from openpyxl.utils.cell import coordinate_to_tuple
import re

DI = 'DADOS_INVOC'
NOTA = ('O degrau registra a aquisição permanente: Incompleta ocupa 2 espaços, '
        'Completa 3 e Sem Barreiras 5 no total, sem somar novamente os anteriores. '
        'O orçamento soma uma vaga por especial normal com nome, independentemente '
        'da Classe em uso e das versões preparadas. Básicas, Liberações, Máxima '
        'e escolhas extras da Trilha têm aquisições próprias e ficam fora dessa soma. '
        'As escolhas extras devem ser registradas no repertório da Trilha. '
        'A conferência automática usa tipo do livro, nível próprio, refino do '
        'invocador e especialização em Ocultismo. Técnica própria e aquisição '
        'das etapas anteriores precisam de conferência da mesa; tipo custom '
        'exige permissão expressa, não é aprovado por possuir reserva de PE. '
        'Sem Barreiras conserva 5 espaços ao abrir fechado. Os dois valores de '
        'PE são fechado/aberto, respectivamente. Nenhuma montagem é apagada.')


def contagem(row, criterio=None):
    """Nomes não vazios ocupam vaga mesmo quando seu tipo não é texto.

    O critério antigo serve apenas para gerar o delta incremental exato.
    Não converte nomes e não conta versões nem extras da Trilha.
    """
    if criterio not in (None, '?*', 'global'):
        raise ValueError('Critério de contagem desconhecido')
    if criterio == '?*':
        return (f'COUNTIFS(DADOS_R53!$A$2:$A$253,"entidade."&$DD{row}&".esp.*",'
                'DADOS_R53!$B$2:$B$253,"?*")')
    identidade = f'REGEXMATCH(DADOS_R53!$A$2:$A$253,"^entidade[.]"&$DD{row}&"[.]esp[.]")'
    if criterio == 'global':
        # Somente para preparar a migração da primeira versão da PR88.
        return (f'SUMPRODUCT(N({identidade}),'
                'N(LEN(DADOS_R53!$B$2:$B$253&"")>0))')
    # Filtrar antes de LEN impede que um nome com erro fora da categoria/
    # entidade contamine a soma. Erros dos próprios nomes continuam visíveis.
    # O comprimento em texto distingue vazio de 0/FALSE sem converter entradas.
    return (f'SUMPRODUCT(N(LEN(FILTER(DADOS_R53!$B$2:$B$253,{identidade})&"")>0))')


def plano_contagem(plano, criterio_anterior='?*'):
    """24 alterações sobre PR87; não repete aquisição, notas ou ANALISE."""
    if criterio_anterior not in ('?*', 'global'):
        raise ValueError('Base de contagem desconhecida')
    deltas = []
    for d in plano:
        if d['aba'] != DI or d['c'] not in (239, 270):
            continue
        atual = contagem(d['r'])
        if d['depois'].count(atual) != 1:
            raise ValueError('Contagem normal divergente')
        deltas.append(dict(aba=DI, r=d['r'], c=d['c'],
                           antes=d['depois'].replace(atual, contagem(d['r'], criterio_anterior)),
                           depois=d['depois']))
    if len(deltas) != 24:
        raise ValueError('Doze orçamentos e requisitos obrigatórios')
    return deltas


def formulas(row, nomes, tipos):
    if len(nomes) != 8 or len(set(nomes)) != 8:
        raise ValueError('São necessárias oito identidades normais por entidade')
    stage, nivel, classe, capacidade = (f'${c}{row}' for c in ('FL', 'FO', 'FP', 'GV'))
    # Conta identidades no registro leve, não as sete versões de cada cartão.
    # Os IDs excluem básicas, extras da Trilha e trunfos sem listas de endereços.
    conhecidas = contagem(row)
    custo = f'SWITCH({stage},"Incompleta",2,"Completa",3,"Sem Barreiras",5,0)'
    total = f'{conhecidas}+{custo}'
    hab = (f'=LET(conhecidas,{conhecidas},dominio,{custo},'
           f'IF(conhecidas+dominio>{capacidade},"REVISAR · ","")&'
           '"HABILIDADES · especiais + domínio "&conhecidas&"+"&dominio&" de "&'
           f'{capacidade}&" · Classe "&{classe}&" · básica "&$FQ{row}&"d6 · "&$GX{row}&IF($GX{row}=1," talento"," talentos"))')
    pe = f'=IF({stage}="Sem Barreiras",6*{classe}&"/"&7*{classe},6*{classe})&" PE"'
    pede = (f'=IF({stage}="","Escolha o degrau",LET('
            f'degrau,IFERROR(MATCH({stage},$CU$2:$CU$4,0),0),'
            f'ocupados,{total},'
            'problemas,TEXTJOIN(" · ",TRUE,'
            'IF(degrau=0,"degrau desconhecido",""),'
            f'IF($DF{row}="Maldição domada","",IF(COUNTIF({tipos},SUBSTITUTE(SUBSTITUTE(SUBSTITUTE($DF{row},"~","~~"),"*","~*"),"?","~?"))>0,'
            '"tipo incompatível","tipo custom: conferir permissão")),'
            f'IF({nivel}<IF(degrau=1,10,14),"nível mínimo "&IF(degrau=1,10,14),""),'
            'IF(N(DADOS_AM!$HM$6)<IF(degrau=1,4,IF(degrau=2,5,10)),'
            '"refino mínimo "&IF(degrau=1,4,IF(degrau=2,5,10)),""),'
            'IF(AND(degrau=3,FICHA!$E$87<>TRUE),"especialização em Ocultismo",""),'
            f'IF(ocupados>{capacidade},"espaços excedidos: "&ocupados&"/"&{capacidade},"")),'
            'IF(problemas<>"","REVISAR · "&problemas,'
            '"Requisitos numéricos atendidos · conferir técnica própria e etapas")))')
    return {'IE': hab, 'JH': pe, 'JJ': pede}


def aplica(layout, tr):
    abas = {a['nome']: a for a in layout['abas']}
    dados = {c[0]: c for c in abas[DI]['celulas']}
    cab = [pos for pos, cell in dados.items() if cell[1] == 'tipo de entidade' and coordinate_to_tuple(pos)[0] == 1]
    if len(cab) != 1:
        raise ValueError('Catálogo de tipos do livro divergente')
    coltipo = cab[0][:-1]
    tipos = f'${coltipo}$2:${coltipo}$6'
    plano, notas = [], []
    for i in range(12):
        ctx = [g for g in tr['contextos'] if g['id'].startswith(f'entidade.{i+1}.esp.')]
        nomes = ["'INVOCAÇÕES'!" + g['cel']['nome'] for g in ctx]
        row = i + 2
        for col, depois in formulas(row, nomes, tipos).items():
            a1 = col + str(row)
            cell = dados[a1]
            antes = cell[1]
            if not isinstance(antes, str) or not antes.startswith('='):
                raise ValueError('Origem calculada ausente: ' + a1)
            cell[1] = depois
            r, c = coordinate_to_tuple(a1)
            plano.append(dict(aba=DI, r=r, c=c, antes=antes, depois=depois))
            # Só as âncoras que exibem essas contas recebem a nota. Não mexe
            # em mesclas, entradas, estilos nem no contrato ANALISE12/esquema2.
            matches = []
            for ui in abas['INVOCAÇÕES']['celulas']:
                if isinstance(ui[1], str) and ui[1].replace("'", '').replace('$', '') == '=' + DI + '!' + a1:
                    matches.append(ui[0])
            if len(matches) != 1:
                raise ValueError('Exibição do domínio divergente: ' + a1)
            pos = matches[0]
            notas.append(dict(aba='INVOCAÇÕES', a1=pos,
                              antes=abas['INVOCAÇÕES']['notas'].get(pos), depois=NOTA))
            abas['INVOCAÇÕES']['notas'][pos] = NOTA
    analise = {c[0]: c for c in abas['ANALISE']['celulas']}
    achadas = []
    for pos, cell in analise.items():
        if pos.startswith('A') and isinstance(cell[1], str) and cell[1].startswith('invocacao.') and cell[1].endswith('.exp.acerto'):
            r, _ = coordinate_to_tuple(pos)
            if analise['D'+str(r)][1] != 'resultado':
                raise ValueError('Metadado de Acerto não corrigido no exportador')
            achadas.append(r)
            plano.append(dict(aba='ANALISE', r=r, c=4, antes='entrada', depois='resultado'))
    if len(achadas) != 12:
        raise ValueError('Contrato de doze Acertos divergente')
    notas.sort(key=lambda d: coordinate_to_tuple(d['a1']))
    return plano, notas


def suporte(layout, plano):
    """Moldes inalterados necessários a colagens mistas, sem novo delta."""
    cells = {a['nome']: {c[0]: c[1] for c in a['celulas']} for a in layout['abas']
             if a['nome'] in ('ANALISE', DI)}
    out = [dict(aba=DI, r=r, c=269, depois=cells[DI]['JI'+str(r)]) for r in range(2, 14)]
    # Colagem/apagamento IE:IF não precisa carregar o editor integral só
    # para recuperar a fórmula vizinha, que não muda mecanicamente.
    out += [dict(aba=DI, r=r, c=240, depois=cells[DI]['IF'+str(r)]) for r in range(2, 14)]
    for d in plano:
        if d['aba'] != 'ANALISE':
            continue
        for col, letra in enumerate('ABC', 1):
            value = cells['ANALISE'][letra+str(d['r'])]
            if col == 3:
                match = re.fullmatch(r'="((?:[^"]|"")*)"', value)
                if match:
                    value = match[1].replace('""', '"')
            out.append(dict(aba='ANALISE', r=d['r'], c=col, depois=value))
    if len(out) != 60:
        raise ValueError('Moldes de suporte do domínio divergentes')
    return out
