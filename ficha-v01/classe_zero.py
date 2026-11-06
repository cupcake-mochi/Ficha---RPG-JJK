"""Alcance de benefício e limite do repertório pessoal de Classe 0."""

from openpyxl.utils.cell import coordinate_to_tuple

import montagens_r53 as R


def aplica(layout, tr):
    amal, custom, dados = 'FICHA AMALDIÇOADA', 'DADOS_CUSTOM', R.DADOS
    nomes = [amal, custom, dados]
    cells = {a['nome']: {c[0]: c for c in a['celulas']}
             for a in layout['abas'] if a['nome'] in nomes}
    col = tr['colunas']
    plano = []
    limite = 'DADOS_CUSTOM!$B$135>DADOS_AM!$HM$10'
    aviso = 'Limite de feitiços Classe 0 excedido'

    def mudar(aba, pos, depois, cartao=None):
        cell = cells[aba][pos]
        antes = cell[1]
        r, c = coordinate_to_tuple(pos)
        delta = dict(aba=aba, r=r, c=c, antes=antes, depois=depois)
        if cartao:
            formulas = tr['formulas'][cartao]
            if formulas.get(pos) != antes:
                raise ValueError('Recuperação de Classe 0 divergente: ' + pos)
            formulas[pos] = depois
            delta.update(cartao=cartao, a1=pos)
        plano.append(delta)
        cell[1] = depois

    contextos = [g for g in tr['contextos'] if g['aba'] == amal and g['modo'] == 'Classe 0']
    if len(contextos) != 7:
        raise ValueError('Cobertura dos cartões Classe 0 divergente')
    comuns, extras = contextos[:5], contextos[5:]
    contagem = lambda grupo: f"SUMPRODUCT(--(LEN('{amal}'!{grupo[0]['cel']['nome']}:{grupo[-1]['cel']['nome']})>0))"
    # As escolhas que ficam guardadas em vagas indisponíveis não consomem o teto.
    mudar(custom, 'B135', f'={contagem(comuns)}+IF($B$134=2,{contagem(extras)},0)')

    for g in contextos:
        row = g['linha']
        saida = lambda k: R.ref(dados, '$'+col[k]+'$'+str(row))
        pos = g['cel']['alcance']
        antes = cells[amal][pos][1]
        ofensivo = saida('alcance_ofensivo')
        if antes.count(ofensivo) != 1:
            raise ValueError('Resumo de alcance divergente: ' + pos)
        # São os três benefícios individuais identificados pelo modelo.
        melhoria = saida('nome_m1')
        aux = ','.join(f'{melhoria}="{nome}"' for nome in ('Guarda', 'Impulso', 'Firmeza'))
        beneficio = f'AND(NOT({saida("dano")}),NOT({saida("coletiva")}),OR({aux}))'
        alcance = f'IF({beneficio},IF({saida("forma_base")}="Toque","1,5 m","4,5 m"),{ofensivo})'
        mudar(amal, pos, antes.replace(ofensivo, alcance), g['id'])

        if g in extras:
            continue
        pos = g['cel']['dano']
        antes = cells[amal][pos][1]
        guard = f'IF({saida("nome")}="","",'
        if not antes.startswith('='+guard):
            raise ValueError('Resumo de Classe 0 divergente: ' + pos)
        mudar(amal, pos, '='+guard+f'IF({limite},"Revisar limite de Classe 0",'
              + antes[1+len(guard):]+')', g['id'])
        pos = col['avisos_funcoes']+str(row)
        antes = cells[dados][pos][1]
        mudar(dados, pos, f'=TEXTJOIN(" · ",TRUE,{antes[1:]},IF({limite},"{aviso}",""))')
        pos = col['valida']+str(row)
        antes = cells[dados][pos][1]
        mudar(dados, pos, f'=AND({antes[1:]},NOT({limite}))')
    return plano
