"""Concessão e orçamento dos extras; não altera compras nem versões salvas."""
import copy
from openpyxl.utils.cell import coordinate_to_tuple, get_column_letter as L

DI = 'DADOS_INVOC'
IV = 'INVOCAÇÕES'
SELETOR = 'D35'
NOTA = ('Uma escolha é uma básica de Classe 0, uma especial normal OU um talento CE 1. '
        'Capacidades e talentos extras compartilham o limite. Invocação Principal: '
        'uma escolha nos níveis 8, 16 e 24 da entidade. Repertório do Conjunto: '
        'nível 27 do invocador e metade do atributo permanente escolhido em '
        'O CONJUNTO, para baixo. Parceria não concede escolhas extras. '
        'Versões de um cartão não multiplicam aquisições. Nenhuma montagem é apagada. '
        'Definição da entidade, requisitos dos talentos e uso com exatamente uma '
        'invocação ativa na Principal continuam exigindo conferência da mesa.')
NOTA_SELETOR = ('Escolha Essência ou Inteligência ao receber Repertório do Conjunto. '
                'Vale para todas as invocações; é independente da escolha da Defesa. '
                'Usa o valor permanente da FICHA, sem Buff/Debuff. '
                'A troca deste campo não apaga as montagens já registradas.')


def formulas(row):
    """Tabela aditiva em DA16:DD28, sem deslocar os endereços existentes."""
    r = row + 15
    attr = (f'IF(\'{IV}\'!${SELETOR[0]}${SELETOR[1:]}="Essência",'
            'IFERROR(VALUE(FICHA!$AJ$21),-1),IFERROR(VALUE(FICHA!$AB$21),-1))')
    caminho = 'FICHA!$D$11="Evocador"'
    principal = '$DB$4="Invocação Principal"'
    conjunto = '$DB$4="Múltiplas Invocações"'
    escolhido = f'OR(\'{IV}\'!$D$35="Essência",\'{IV}\'!$D$35="Inteligência")'
    valido = 'AND(atributo>=0,atributo=INT(atributo))'
    quota = (f'=LET(atributo,{attr},IF({caminho},'
             f'IF({principal},IF($DB$2>=2,INT($FO{row}>=8)+INT($FO{row}>=16)+INT($FO{row}>=24),0),'
             f'IF(AND({conjunto},$DB$2>=27,{escolhido},{valido}),INT(atributo/2),0)),0))')
    used = (f'=COUNTIFS(DADOS_R53!$A$2:$A$253,"entidade."&$DD{row}&".ext.*",'
            # O nome vem sem coerção: números e booleanos também ocupam vaga.
            # "<>" ignora o resultado vazio da fórmula, preservando esses tipos.
            f'DADOS_R53!$B$2:$B$253,"<>")+COUNTIF($FF{row}:$FH{row},"?*")')
    warning = (f'=IF($DC{r}=0,"",LET(atributo,{attr},TEXTJOIN(" · ",TRUE,'
               f'IF({caminho},"","Repertório extra exige Evocador"),'
               f'IF(OR({principal},{conjunto}),"","Trilha sem escolhas extras"),'
               f'IF(AND({principal},$DB$2<2),"Trilha exige nível 2 do invocador",""),'
               f'IF(AND({conjunto},$DB$2<27),"Repertório do Conjunto: nível mínimo 27 do invocador",""),'
               f'IF(AND({conjunto},$DB$2>=27,{escolhido}=FALSE),"Escolha Essência ou Inteligência em O CONJUNTO",""),'
               f'IF(AND({conjunto},$DB$2>=27,{escolhido},{valido}=FALSE),"Atributo permanente inválido",""),'
               f'IF($DC{r}>$DB{r},"Escolhas extras excedidas: "&$DC{r}&"/"&$DB{r},""))))')
    return {'DA': f'="entidade.{row-1}"', 'DB': quota, 'DC': used, 'DD': warning}


def aplica(layout, tr):
    abas = {a['nome']: a for a in layout['abas']}
    maps = {name: {c[0]: c for c in a['celulas']} for name, a in abas.items()}
    plano, notas = [], []

    def put(aba, a1, value, style=None):
        cells = maps[aba]
        old = cells[a1][1] if a1 in cells else None
        r, c = coordinate_to_tuple(a1)
        plano.append(dict(aba=aba, r=r, c=c, antes=old, depois=value))
        if a1 in cells:
            cells[a1][1] = value
            if style is not None:
                cells[a1][2] = style
        else:
            cell = [a1, value, style]
            abas[aba]['celulas'].append(cell)
            cells[a1] = cell

    def note(a1, value):
        old = abas[IV]['notas'].get(a1)
        notas.append(dict(aba=IV, a1=a1, antes=old, depois=value))
        abas[IV]['notas'][a1] = value

    for col, name in zip(('DA', 'DB', 'DC', 'DD'),
                         ('repertório da Trilha', 'limite extra', 'escolhas extras usadas', 'revisão dos extras')):
        put(DI, col+'16', name)
    for row in range(2, 14):
        for col, value in formulas(row).items():
            if col+str(row+15) in maps[DI]:
                raise ValueError('Área de suporte ocupada: '+col+str(row+15))
            put(DI, col+str(row+15), value)
        cards = [g for g in tr['contextos'] if g['id'].startswith(f'entidade.{row-1}.ext.')]
        if len(cards) != 3:
            raise ValueError('Três cartões extras por entidade são obrigatórios')
        for g in cards:
            a1 = 'GA'+str(g['linha'])
            old = maps['DADOS_R53'][a1][1]
            put('DADOS_R53', a1, '=TEXTJOIN(" · ",TRUE,'+old[1:]+f',\'{DI}\'!$DD${row+15})')
        # Cabeçalho compartilhado também cobre a montagem composta só de talentos.
        first = coordinate_to_tuple(cards[0]['cel']['classe'])[0]
        col = ''.join(c for c in cards[0]['cel']['classe'] if c.isalpha())
        a1 = col+str(first-3)
        if not str(maps[IV][a1][1]).startswith('REPERTÓRIO DA TRILHA'):
            raise ValueError('Cabeçalho do repertório divergente: '+a1)
        put(IV, a1, f'=IF(\'{DI}\'!$DD${row+15}<>"","REVISAR · ","")&"REPERTÓRIO DA TRILHA · "&\'{DI}\'!$DC${row+15}&"/"&\'{DI}\'!$DB${row+15}&IF(\'{DI}\'!$DD${row+15}<>""," · "&\'{DI}\'!$DD${row+15},"")')
        note(a1, NOTA)
    for r in range(34, 40):
        for c in range(4, 7):
            p = L(c)+str(r)
            if maps[IV].get(p, [None, None])[1] is not None:
                raise ValueError('Área do seletor ocupada: '+p)
    estilos = layout['estilos']
    label = maps[IV]['D16'][2]
    val = maps[IV]['D17'][2]
    hint = copy.deepcopy(estilos[val])
    hint[0][1] = 9
    hint[3] = ['left', 'center', True, 0]
    estilos.append(hint)
    for r in range(34, 40):
        for c in range(4, 7):
            p = L(c)+str(r)
            maps[IV][p][2] = label if r == 34 else val if r <= 36 else len(estilos)-1
    put(IV, 'D34', 'REPERTÓRIO DO CONJUNTO USA')
    put(IV, 'D37', 'Escolha o atributo do repertório extra. Usa o valor permanente, sem Buff/Debuff; não altera a Defesa.')
    abas[IV]['mescladas'].extend(['D34:F34', 'D35:F36', 'D37:F39'])
    menu = dict(onde='D35', tipo='list', formula='DADOS_INVOC!$CY$2:$CY$3', vazio_ok=True, mostra_seta=True)
    abas[IV]['menus'].append(menu)
    note('D34', NOTA_SELETOR)
    note('D35', NOTA_SELETOR)
    return plano, notas, dict(mesclas=['D34:F34', 'D35:F36', 'D37:F39'], menu=menu)


def suporte(layout, tr):
    """Vizinhos inalterados para recuperar o bloco FY:FZ:GA em conjunto."""
    cells = {c[0]: c[1] for a in layout['abas'] if a['nome'] == 'DADOS_R53' for c in a['celulas']}
    return [dict(aba='DADOS_R53', r=g['linha'], c=c, depois=cells[col+str(g['linha'])])
            for g in tr['contextos'] if g.get('extra') for col, c in [('FY', 181), ('FZ', 182)]]
