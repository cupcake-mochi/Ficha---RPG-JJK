"""Diagnóstico das funções salvas que a porta do cartão deixou indisponíveis.

As contas continuam bloqueadas pela porta. O aviso lê a intenção preservada na
versão/entrada, pois os flags efetivos já são falsos quando Amparo está Fechada.

Veio da PR45 (Codex, 30/10/2026) e foi refeito sobre a main da R67: o aviso de
requisito é o `R.aviso_requisito(g)`, com o texto configurável de cada contexto
(Trunfo, Liberação Máxima N), e os de função entram depois dele.
"""
import re

from openpyxl.utils.cell import get_column_letter

import montagens_r53 as R


def referencia(aba, endereco):
    return R.ref(aba, endereco)


def formula_avisos_funcoes(g, classe=None):
    """Fórmula da coluna avisos_funcoes (GA) da DADOS_R53 para o contexto `g`.

    `classe` é a referência da Classe ativa do cartão; o padrão é a coluna C da
    linha do contexto, onde a DADOS_R53 guarda a Classe.
    """
    terms = []
    requisito = R.aviso_requisito(g)
    if requisito != '""':
        terms.append(requisito)
    end = get_column_letter(len(g['classes']) + 1)
    headers = referencia(R.EDITOR, f'$B${g["editor"]+1}:${end}${g["editor"]+1}')
    classe = classe or referencia(R.DADOS, f'$C${g["linha"]}')
    selected = '1' if len(g['classes']) == 1 else f'MATCH({classe},{headers},0)'
    for n, key, function in [(2, 'cura', 'Cura'), (3, 'vt', 'PV temporários')]:
        gate = g['portas'].get(key, 'FALSE')
        pos = g.get('funcoes_diretas', {}).get(key)
        if not pos or gate == 'TRUE':
            continue
        value = referencia(g['aba'], pos)
        visible = f'{value}=TRUE' if g['fixa'] else f'AND(ISNUMBER({value}),{value}>0)'
        if g['fixa']:
            # Modalidade fixa marca a função direto no cartão; não há versão por Classe.
            intent = visible
        else:
            row = g['campos']['funcao' + str(n)]
            pool = referencia(R.EDITOR, f'$B${row}:${end}${row}')
            saved = f'IFERROR(INDEX({pool},1,{selected})="{function}",FALSE)'
            intent = f'OR({saved},{visible})'
        label = 'cura' if key == 'cura' else 'vida temporária'
        amparo = f'"Amparo Fechada: função de {label} salva indisponível"'
        extra = re.fullmatch(r'AND\((.+)<>0,(.+)\)', gate)
        if gate == 'FALSE':
            warning = f'"Função indisponível nesta modalidade: {label}"'
        elif extra:
            # Carta extra de entidade: a Classe 0 (Básica) também fecha a função; não culpar a Amparo.
            warning = f'IF(NOT({extra[2]}),{amparo},"Classe 0 (Básica): função de {label} salva indisponível")'
        else:
            warning = amparo
        terms.append(f'IF(AND(NOT({gate}),{intent}),{warning},"")')
    if not terms:
        return '=""'
    if len(terms) == 1 and terms[0] == requisito:
        return '=' + requisito
    return '=TEXTJOIN(" · ",TRUE,' + ','.join(terms) + ')'
