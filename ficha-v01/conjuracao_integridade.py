"""Apresentação do custo e teto de combate nos cartões do personagem."""

import re

from openpyxl.utils.cell import coordinate_to_tuple


def estadio(atual, maximo):
    return (f'IF(AND(ISNUMBER({atual}),ISNUMBER({maximo}),{maximo}>0),'
            f'IF({atual}<=0,4,IF({atual}<={maximo}/4,3,IF({atual}<={maximo}/2,2,'
            f'IF({atual}<={maximo}*3/4,1,0)))),0)')


def teto(classe):
    return f'IF({classe}>=1,MAX(1,INT({classe}/2)),0)'


def preco_execucao(preco, classe):
    estado = estadio('FICHA!$D$34', 'FICHA!$J$34')
    limite = teto('N(FICHA!$Z$73)')
    return (
        f'LET(estagio,{estado},classeuso,N({classe}),tetouso,{limite},'
        'IF(estagio=4,"Sem conjuração",'
        'IF(AND(estagio=3,classeuso>tetouso),"Acima do teto "&tetouso,'
        f'({preco}+IF(estagio>=2,classeuso,0))&" PE"&'
        'IF(estagio=3," · Teto "&tetouso,""))))'
    )


def aplica(layout, tr):
    abas = {a['nome']: a for a in layout['abas']}
    ficha, amal = 'FICHA', 'FICHA AMALDIÇOADA'
    cells = {a: {c[0]: c for c in abas[a]['celulas']} for a in [ficha, amal]}
    plano = []

    def mudar(aba, pos, depois, cartao=None):
        cell = cells[aba][pos]
        antes = cell[1]
        r, c = coordinate_to_tuple(pos)
        delta = dict(aba=aba, r=r, c=c, antes=antes, depois=depois)
        if cartao:
            formulas = tr['formulas'][cartao]
            if formulas.get(pos) != antes:
                raise ValueError('Fórmula de recuperação divergente: ' + pos)
            formulas[pos] = depois
            delta.update(cartao=cartao, a1=pos)
        plano.append(delta)
        cell[1] = depois

    maximo = teto('N($Z$73)')
    antigo = cells[ficha]['D37'][1]
    rotulo = '"Estágio 3 · Desvantagem em ataques e TRs, Classe máxima à metade"'
    if antigo.count(rotulo) != 1:
        raise ValueError('Resumo de Integridade divergente')
    mudar(ficha, 'D37', antigo.replace(
        rotulo,
        f'"Estágio 3 · Teto de conjuração "&{maximo}&" · +1 PE por Classe · Desvantagem em ataques e TRs"',
    ))
    for g in tr['contextos']:
        if g['aba'] != amal or g['modo'] == 'Classe 0':
            continue
        pos = g['cel'].get('execucao_resumo') or g['cel']['pe']
        row = g['linha']
        before = cells[amal][pos][1]
        pattern = rf"""((?:'DADOS_R53'|DADOS_R53)!\$?DX\$?{row})&" PE" """
        after, total = re.subn(pattern.rstrip(), lambda m: preco_execucao(
            m[1], f'DADOS_R53!$C${row}'), before)
        if total != 1:
            raise ValueError('Preço base ausente ou duplicado: ' + pos)
        mudar(amal, pos, after, g['id'])
    if len(plano) != 41:
        raise ValueError('Cobertura dos cartões pessoais divergente')
    return plano
