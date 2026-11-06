"""Apresentação de preparo, disparo e duração de Guarda nos feitiços comuns."""

from openpyxl.utils.cell import coordinate_to_tuple

import montagens_r53 as R


def tem(saida, campos, padrao):
    testes = (f'REGEXMATCH({saida(campo)},"^({padrao})$")' for campo in campos)
    return 'OR('+','.join(testes)+')'


def aplica(layout, tr):
    aba, dados = 'FICHA AMALDIÇOADA', R.DADOS
    cells = {a['nome']: {c[0]: c for c in a['celulas']}
             for a in layout['abas'] if a['nome'] in (aba, dados)}
    col = tr['colunas']
    plano = []
    melhorias = [f'nome_m{i}' for i in range(1, 5)]
    opcoes = [f'm{i}' for i in range(1, 5)]
    normal = 'até o fim do próximo turno do alvo'

    def mudar(aba, pos, depois, cartao=None):
        cell = cells[aba][pos]
        antes = cell[1]
        r, c = coordinate_to_tuple(pos)
        delta = dict(aba=aba, r=r, c=c, antes=antes, depois=depois)
        if cartao:
            formulas = tr['formulas'][cartao]
            if formulas.get(pos) != antes:
                raise ValueError('Recuperação de Tempo divergente: '+pos)
            formulas[pos] = depois
            delta.update(cartao=cartao, a1=pos)
        plano.append(delta)
        cell[1] = depois

    for g in tr['contextos']:
        if g['aba'] != aba or g['modo'] != 'Comum':
            continue
        row = g['linha']
        saida = lambda k: R.ref(dados, '$'+col[k]+'$'+str(row))
        guarda = tem(saida, melhorias, 'Guarda')
        concentrada = tem(saida, opcoes, 'Concentrada')
        duradoura = tem(saida, opcoes, 'Duradoura')
        curto = tem(saida, melhorias,
                    'Condição|Cerca|Prende|Terreno|Impulso|Trava|Firmeza|'
                    'Marca|Ecoa|Pressa|Enfraquece|Sobrecarga|Sem Cura|Alvo de Caça')
        # Outras peças e efeitos próprios podem ter duração decidida na criação.
        prazo = (
            f'IF(AND({concentrada},NOT({duradoura})),IF({curto},'
            '"por 1 min com concentração",'
            '"por até 10 min com concentração, conforme o menor prazo"),'
            f'IF(AND({duradoura},NOT({concentrada})),"por 1 min",""))'
        )
        pos = col['efeitos']+str(row)
        antes = cells[dados][pos][1]
        if antes.count(': +2 Defesa '+normal) != 4:
            raise ValueError('Texto de Guarda divergente: '+pos)
        trecho = '+2 Defesa '+normal
        mudar(dados, pos,
              f'=LET(prazoguarda,{prazo},SUBSTITUTE({antes[1:]},"{trecho}",'
              f'"+2 Defesa "&IF(prazoguarda="","{normal}",prazoguarda)))')

        pos = g['cel']['avisos']
        antes = cells[aba][pos][1]
        avisos = saida('avisos')
        if antes.count(avisos) != 1:
            raise ValueError('Avisos do cartão divergentes: '+pos)
        texto = (f'LET(prazoguarda,{prazo},TEXTJOIN(" · ",TRUE,{avisos},'
                 f'IF(AND({guarda},prazoguarda<>""),"Guarda: +2 Defesa "&prazoguarda,"")))')
        mudar(aba, pos, antes.replace(avisos, texto), g['id'])

        pos = g['cel']['execucao_resumo']
        antes = cells[aba][pos][1]
        acao = saida('acao')
        ini, fim = ','+acao+',LET(estagio,', ',LET(apoio,'
        if antes.count(ini) != 1 or antes.count(fim) != 1:
            raise ValueError('Resumo de execução divergente: '+pos)
        i = antes.index(ini)
        j = antes.index(fim, i)
        preco = antes[i+len(acao)+2:j]
        carregar = tem(saida, ['nome_r1', 'nome_r2'], 'Carregar')
        armado = tem(saida, melhorias, 'Armado')
        momento = (
            f'LET(precoexec,{preco},acaoexec,SUBSTITUTE({acao},"Ação ",""),'
            f'IF(AND({saida("valida")},REGEXMATCH(precoexec," PE( · |$)")),'
            f'IF({carregar},"Carregar agora: Padrão + "&precoexec&'
            '" · "&acaoexec&" no próximo turno",'
            f'IF({armado},"Armar: "&acaoexec&" + "&precoexec&" · Gatilho sem Reação",'
            f'{acao}&" · "&precoexec)),{acao}&" · "&precoexec))'
        )
        mudar(aba, pos, antes[:i]+','+momento+antes[j:], g['id'])
    if len(plano) != 108:
        raise ValueError('Cobertura dos cartões de Tempo divergente')
    return plano
