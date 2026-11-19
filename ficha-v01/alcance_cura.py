"""Usa os alcances de dano e benefício no resumo de execução pessoal."""

from openpyxl.utils.cell import coordinate_to_tuple

import montagens_r53 as R


def aplica(layout, tr):
    aba = 'FICHA AMALDIÇOADA'
    ficha = next(a for a in layout['abas'] if a['nome'] == aba)
    cells = {c[0]: c for c in ficha['celulas']}
    col = tr['colunas']
    plano, beneficios = [], []
    for g in tr['contextos']:
        if g['aba'] != aba or g['modo'] != 'Comum':
            continue
        row = g['linha']
        saida = lambda chave: R.ref(R.DADOS, '$'+col[chave]+'$'+str(row))
        dano, cura, vt = (saida(k) for k in ('dano', 'cura', 'vt'))
        ofensivo = saida('alcance_ofensivo')
        beneficio = saida('alcance_beneficio')
        rotulo = f'IF({cura},IF({vt},"Cura/PV temp.","Cura"),"PV temp.")'
        alcance = (
            f'IF(OR({cura},{vt}),'
            f'LET(distdano,{ofensivo},distapoio,{beneficio},'
            f'IF(AND({dano},distdano<>distapoio),'
            f'"Dano "&distdano&" · "&{rotulo}&" "&distapoio,distapoio)),{ofensivo})'
        )
        nomes = (saida('nome_m'+str(i)) for i in range(1, 5))
        aux = ','.join(f'REGEXMATCH({nome},"^(Guarda|Impulso|Firmeza)$")' for nome in nomes)
        rotulo_apoio = (
            f'TEXTJOIN("/",TRUE,IF({cura},"Cura",""),'
            f'IF({vt},"PV temp.",""),IF(apoio,"Apoio",""))'
        )
        alcance_com_apoio = (
            f'LET(apoio,OR({aux}),IF(OR({cura},{vt},apoio),'
            f'LET(distdano,{ofensivo},distapoio,{beneficio},'
            f'IF(AND({dano},distdano<>distapoio),'
            f'"Dano "&distdano&" · "&{rotulo_apoio}&" "&distapoio,distapoio)),{ofensivo}))'
        )
        pos = g['cel']['execucao_resumo']
        cell = cells[pos]
        antes = cell[1]
        formulas = tr['formulas'][g['id']]
        if antes.count(ofensivo) != 1 or formulas.get(pos) != antes:
            raise ValueError('Resumo de execução divergente: ' + pos)
        depois = antes.replace(ofensivo, alcance)
        r, c = coordinate_to_tuple(pos)
        alvo = dict(aba=aba, r=r, c=c, antes=antes, depois=depois, cartao=g['id'], a1=pos)
        plano.append(alvo)
        final = antes.replace(ofensivo, alcance_com_apoio)
        beneficios.append(dict(alvo, antes=depois, depois=final))
        formulas[pos] = final
        cell[1] = final
    if len(plano) != 36:
        raise ValueError('Cobertura dos cartões de alcance divergente')
    return plano, beneficios
