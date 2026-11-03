"""Diagnóstico das funções salvas que a porta do cartão deixou indisponíveis.

As contas continuam bloqueadas pela porta. O aviso lê a intenção preservada na
versão/entrada, pois os flags efetivos já são falsos quando Amparo está Fechada.
"""
from openpyxl.utils.cell import get_column_letter


def referencia(aba, endereco):
    return "'" + aba.replace("'", "''") + "'!" + endereco


def formula_avisos_funcoes(g):
    terms = []
    if g.get('requisito'):
        terms.append('IF(' + g['requisito'] + ',"","Trunfo exige maldição domada com técnica própria e nível de aquisição")')
    end = get_column_letter(len(g['classes']) + 1)
    headers = referencia('MONTAGENS', f'$B${g["editor"]+1}:${end}${g["editor"]+1}')
    selected = '1' if len(g['classes']) == 1 else f'MATCH(\'DADOS_R53\'!$C${g["linha"]},{headers},0)'
    for n, key, function in [(2, 'cura', 'Cura'), (3, 'vt', 'PV temporários')]:
        gate = g['portas'].get(key, 'FALSE')
        pos = g.get('funcoes_diretas', {}).get(key)
        if not pos or gate == 'TRUE':
            continue
        value = referencia(g['aba'], pos)
        row = g['campos']['funcao' + str(n)]
        pool = referencia('MONTAGENS', f'$B${row}:${end}${row}')
        saved = f'IFERROR(INDEX({pool},1,{selected})="{function}",FALSE)'
        visible = f'{value}=TRUE' if g['fixa'] else f'AND(ISNUMBER({value}),{value}>0)'
        label = 'cura' if key == 'cura' else 'vida temporária'
        warning = (f'Função indisponível nesta modalidade: {label}' if gate == 'FALSE'
                   else f'Amparo Fechada: função de {label} salva indisponível')
        terms.append(f'IF(AND(NOT({gate}),OR({saved},{visible})),"{warning}","")')
    return '=TEXTJOIN(" · ",TRUE,' + ','.join(terms) + ')' if terms else '=""'
