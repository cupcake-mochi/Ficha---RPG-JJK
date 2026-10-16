"""Extensão nativa do ESTUDO 3C; não altera as contas da ficha.

Regra informada pelo autor, destinada ao futuro Guia de Criação. A autonomia
não deve ser apresentada como regra da mesa nem como texto já publicado na R52.
"""
import json
from pathlib import Path
from prototipo_custom_3c import SID, rgb, BG, PANEL, HEAD, INK, LINE

NOTA_AUTONOMIA = (
    'Regra do sistema prevista para o Guia de Criação; ainda não abordada no livro de regras atual. '
    'Autônoma é o padrão e mantém o funcionamento atual. '
    'Não autônoma: recebe uma Família Livre adicional, que é uma nova Família aberta, '
    'e precisa de ordem prévia para qualquer ação, exceto a Reação. '
    'A ficha calcula a Família adicional; as ordens são controladas durante o jogo.'
)
NOTA_EXEMPLO = (
    'Demonstração: mudar este menu só altera este exemplo. '
    'A escolha real está em cada ficha da aba INVOCAÇÕES. '
)


def build():
    req, controls = [], []

    def area(r, c, er=None, ec=None):
        return dict(sheetId=SID, startRowIndex=r-1, endRowIndex=er or r,
                    startColumnIndex=c-1, endColumnIndex=ec or c)

    req.append({'updateSheetProperties': {'properties': {'sheetId': SID,
                'gridProperties': {'rowCount': 172}}, 'fields': 'gridProperties.rowCount'}})
    req.append({'updateDimensionProperties': {'range': {'sheetId': SID, 'dimension': 'COLUMNS',
        'startIndex': 1, 'endIndex': 2}, 'properties': {'pixelSize': 130}, 'fields': 'pixelSize'}})
    req.append({'repeatCell': {'range': area(125, 1, 172, 16), 'cell': {'userEnteredFormat': {
        'backgroundColor': rgb(BG), 'textFormat': {'fontFamily': 'Roboto', 'fontSize': 10,
        'foregroundColor': rgb(INK)}}}, 'fields': 'userEnteredFormat'}})
    req.append({'updateDimensionProperties': {'range': {'sheetId': SID, 'dimension': 'ROWS',
        'startIndex': 124, 'endIndex': 172}, 'properties': {'pixelSize': 27}, 'fields': 'pixelSize'}})

    def cell(r, c, value=None, er=None, ec=None, head=False, note=None):
        rg = area(r, c, er, ec)
        data = {'note': note or 'Protótipo de desenho, sem efeito na ficha. '+NOTA_AUTONOMIA,
                'userEnteredFormat': {'backgroundColor': rgb(HEAD if head else PANEL),
                    'textFormat': {'fontFamily': 'Oswald' if head else 'Roboto', 'fontSize': 10,
                                   'foregroundColor': rgb(INK)},
                    'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'}}
        if value is not None:
            key = 'numberValue' if isinstance(value, (int, float)) else 'formulaValue' if value.startswith('=') else 'stringValue'
            data['userEnteredValue'] = {key: value}
        req.append({'repeatCell': {'range': rg, 'cell': {'userEnteredFormat': data['userEnteredFormat']},
                                  'fields': 'userEnteredFormat'}})
        req.append({'updateCells': {'start': {'sheetId': SID, 'rowIndex': r-1, 'columnIndex': c-1},
                                   'rows': [{'values': [data]}], 'fields': 'userEnteredValue,note'}})
        if (er or r, ec or c) != (r, c):
            req.append({'mergeCells': {'range': rg, 'mergeType': 'MERGE_ALL'}})
        edge = {'style': 'SOLID', 'color': rgb(LINE)}
        req.append({'updateBorders': {'range': rg, 'top': edge, 'bottom': edge, 'left': edge, 'right': edge}})

    cell(127, 2, 'EXEMPLO DA ENTIDADE · AUTONOMIA', er=128, ec=15, head=True)
    cell(130, 2, 'AUTONOMIA · EXEMPLO', ec=4, head=True, note=NOTA_EXEMPLO+NOTA_AUTONOMIA)
    cell(130, 5, 'Autônoma', ec=7, note=NOTA_EXEMPLO+NOTA_AUTONOMIA)
    options = {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': v} for v in ('Autônoma', 'Não autônoma')]}
    req.append({'setDataValidation': {'range': area(130, 5), 'rule': {
        'condition': options, 'strict': True, 'showCustomUi': True}}})
    controls.append([130, 5, options])
    cell(132, 2, 'NOTA DO CAMPO', ec=7, head=True)
    cell(133, 2, NOTA_EXEMPLO+NOTA_AUTONOMIA, er=139, ec=7, note=NOTA_EXEMPLO+NOTA_AUTONOMIA)
    cell(130, 10, 'PADRÃO · AUTÔNOMA', ec=15, head=True)
    cell(132, 10, 'EXEMPLO · INVOCAÇÃO PRINCIPAL', ec=15, head=True)
    for r, label, formula in (
        (133, 'FAMÍLIAS ABERTAS', '=G149+IF(E130="Não autônoma";G151;0)'),
        (134, 'LIVRES', '=G150+IF(E130="Não autônoma";G151;0)')):
        cell(r, 10, label, ec=12, head=True)
        cell(r, 13, formula, ec=15)
    cell(136, 10, '=IF(E130="Não autônoma";"+1 Livre = uma Família nova. Exige ordem prévia, exceto para a Reação.";'
         '"Mantém o funcionamento atual. Nenhuma Família adicional por autonomia.")', er=139, ec=15)
    cell(141, 2, 'CONFIGURAÇÃO · LIMITES DAS ENTIDADES EM ESTUDO', ec=15, head=True)
    for c, label, ec in ((2, 'REGRA', 4), (5, 'SISTEMA', 5), (6, 'CAMPANHA', 6), (7, 'EM USO', 7)):
        cell(143, c, label, ec=ec, head=True)
    labels = [
        ('Abertas · padrão', 3), ('Livres · padrão', 1),
        ('Abertas · Parceria / Múltiplas', 4), ('Livres · Parceria / Múltiplas', 1),
        ('Abertas · Invocação Principal', 5), ('Livres · Invocação Principal', 2),
        ('Não autônoma · Livres adicionais', 1),
    ]
    for r, (label, base) in enumerate(labels, 145):
        note = ('Em branco usa o sistema. Livres fazem parte do total de Famílias abertas. '
                'A capacidade física é de nove caixas por entidade. '+NOTA_AUTONOMIA)
        cell(r, 2, label, ec=4, note=note)
        cell(r, 5, base, note=note)
        cell(r, 6, note=note)
        cell(r, 7, f'=IF(F{r}="";E{r};F{r})', note=note)
        condition = {'type': 'CUSTOM_FORMULA', 'values': [{'userEnteredValue':
            f'=OR(F{r}="";AND(ISNUMBER(F{r});F{r}>=0;F{r}<=9;MOD(F{r};1)=0))'}]}
        req.append({'setDataValidation': {'range': area(r, 6), 'rule': {
            'condition': condition, 'strict': True, 'showCustomUi': True}}})
        controls.append([r, 6, condition])
    cell(143, 10, 'LEITURA DOS LIMITES', ec=15, head=True)
    cell(145, 10, 'Livre já faz parte das abertas. O bônus da Não autônoma acrescenta uma nova Família '
         'e essa nova Família é Livre. Não acrescenta outra Aberta comum.', er=148, ec=15)
    cell(150, 10, 'As nove caixas dão espaço para as escolhas permitidas pelas regras '
         'e pela campanha; nove caixas não concedem nove Famílias.', er=153, ec=15)
    cell(154, 2, 'EM BRANCO = SISTEMA · AUTÔNOMA = COMPORTAMENTO ATUAL', ec=15, head=True)
    cell(156, 2, 'O campo entra no espaço livre abaixo da aquisição, em cada uma das 12 entidades. '
         'A nota fica no rótulo e no menu; CONFIGURAÇÃO também informa a origem no Guia de Criação.', er=158, ec=15)
    cell(160, 2, 'Este complemento mostra o novo campo e a tabela de limites antes da integração. '
         'O desenho anterior de Família, Forma, Melhoria e Restrição já foi aprovado.', er=162, ec=15)
    # Atualizações pequenas no estudo anterior, sem reconstruir nem apagar entradas.
    for r, c, value in ((86, 2, 'Família: 12 × 9 = 108 seleções; catálogo também usado pelas peças'),
                         (86, 14, 108), (106, 2, 'DESENHO APROVADO · COMPLEMENTO DE AUTONOMIA ABAIXO'),
                         (107, 2, 'Família, Forma, Melhoria, Restrição e Neutras por saldo: desenho aprovado. '
                          'Capacidade e custo de integração ainda em aberto.')):
        req.append({'updateCells': {'start': {'sheetId': SID, 'rowIndex': r-1, 'columnIndex': c-1},
            'rows': [{'values': [{'userEnteredValue': {'numberValue' if isinstance(value, int) else 'stringValue': value}}]}],
            'fields': 'userEnteredValue'}})
    return dict(sheetId=SID, requests=req, controls=controls, nota_autonomia=NOTA_AUTONOMIA)


if __name__ == '__main__':
    import sys
    dest = Path(sys.argv[1])
    model = build()
    dest.write_text(json.dumps(model, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps({'pedidos': len(model['requests']), 'controles': len(model['controls'])}))
