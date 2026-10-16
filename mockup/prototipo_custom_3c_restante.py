"""Complemento nativo dos moldes 3c: somente estudo, sem integração.

Acrescenta linhas ao ESTUDO 3C existente. Não reescreve o desenho já aprovado.
Os comportamentos próprios de um tipo de entidade são proposta para revisão.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'ficha-v01'), str(ROOT / 'ficha')]
import ficha_amaldicoada as fa
from prototipo_custom_3c import SID, rgb, BG, PANEL, HEAD, INK, LINE


def build():
    cat = json.loads((ROOT / 'catalogo-projeto-m.json').read_text())
    inv = json.loads((ROOT / 'ficha-v01/invocacao-do-livro.json').read_text())
    rules = fa.regras()
    req, controls, anchors = [], [], []

    def area(r, c, er=None, ec=None):
        return dict(sheetId=SID, startRowIndex=r-1, endRowIndex=er or r,
                    startColumnIndex=c-1, endColumnIndex=ec or c)

    req.append({'updateSheetProperties': {'properties': {'sheetId': SID,
                'gridProperties': {'rowCount': 268}}, 'fields': 'gridProperties.rowCount'}})
    req.append({'repeatCell': {'range': area(173, 1, 268, 16), 'cell': {'userEnteredFormat': {
        'backgroundColor': rgb(BG), 'textFormat': {'fontFamily': 'Roboto', 'fontSize': 10,
        'foregroundColor': rgb(INK)}}}, 'fields': 'userEnteredFormat'}})
    req.append({'updateDimensionProperties': {'range': {'sheetId': SID, 'dimension': 'ROWS',
        'startIndex': 172, 'endIndex': 268}, 'properties': {'pixelSize': 27}, 'fields': 'pixelSize'}})

    def cell(r, c, value=None, er=None, ec=None, head=False, note=None):
        rg = area(r, c, er, ec)
        data = {'note': note or 'Molde em estudo. Não altera os cadastros nem as contas da ficha.',
                'userEnteredFormat': {'backgroundColor': rgb(HEAD if head else PANEL),
                    'textFormat': {'fontFamily': 'Oswald' if head else 'Roboto', 'fontSize': 10,
                                   'foregroundColor': rgb(INK)},
                    'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'}}
        if value is not None:
            k = ('boolValue' if isinstance(value, bool) else 'numberValue' if isinstance(value, (int, float))
                 else 'formulaValue' if value.startswith('=') else 'stringValue')
            data['userEnteredValue'] = {k: value}
        req.append({'repeatCell': {'range': rg, 'cell': {'userEnteredFormat': data['userEnteredFormat']},
                                  'fields': 'userEnteredFormat'}})
        req.append({'updateCells': {'start': {'sheetId': SID, 'rowIndex': r-1, 'columnIndex': c-1},
                                   'rows': [{'values': [data]}], 'fields': 'userEnteredValue,note'}})
        anchors.append([r, c])
        if (er or r, ec or c) != (r, c):
            req.append({'mergeCells': {'range': rg, 'mergeType': 'MERGE_ALL'}})
        edge = {'style': 'SOLID', 'color': rgb(LINE)}
        req.append({'updateBorders': {'range': rg, 'top': edge, 'bottom': edge, 'left': edge, 'right': edge}})

    def options(r, c, values):
        condition = ({'type': 'BOOLEAN'} if values is None else
                     {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': str(v)} for v in values]})
        req.append({'setDataValidation': {'range': area(r, c), 'rule': {
            'condition': condition, 'strict': True, 'showCustomUi': True}}})
        controls.append([r, c, condition])

    def field(r, c, label, values=None, value=None, note=None):
        cell(r, c, label, ec=c+2, head=True, note=note)
        cell(r, c+3, value, ec=c+5, note=note)
        if values is not None:
            options(r, c+3, values)

    base_note = ('Opcional. Em branco nos demais campos, uma base herda as automações do livro. '
                 'Nenhuma permite conteúdo próprio. O texto do efeito não é interpretado como fórmula.')

    def card(r, c, title, bases=None):
        cell(r, c, title, ec=c+5, head=True)
        cell(r+1, c, 'NOME', ec=c+3, head=True,
             note='Nome único. O menu da ficha reunirá o livro e os cadastros válidos.')
        cell(r+1, c+4, 'MESTRE VIU', ec=c+5, head=True,
             note='Lembrete marcado pelo jogador; aprovação é feita pelo bot, no chat.')
        cell(r+2, c, ec=c+3, note='Nome próprio do conteúdo criado com o mestre.')
        cell(r+2, c+4, False, ec=c+5,
             note='Marque depois de mostrar este cadastro ao mestre. Não significa aprovação automática.')
        options(r+2, c+4, None)
        if bases is not None:
            field(r+4, c, 'BASE DO LIVRO', ['Nenhuma']+bases, 'Nenhuma', base_note)

    def text(r, c, label, end, note):
        cell(r, c, label, ec=c+5, head=True, note=note)
        cell(r+1, c, er=end, ec=c+5, note=note)

    cell(175, 2, 'CUSTOM · MOLDES RESTANTES', ec=15, head=True)
    card(178, 2, 'APTIDÃO / BÊNÇÃO', [x['nome'] for x in rules['aptidoes']])
    field(183, 2, 'TIPO', ['Aptidão', 'Bênção'], 'Aptidão',
          'Aptidão usa Refino; Bênção pertence à rota sem energia e usa Lapidação. Em branco com base, herda o tipo.')
    field(184, 2, 'CATEGORIA DE EFEITO', ['—', 1, 2, 3], None,
          'Categoria do conteúdo. — significa que a entrada não usa Categoria de Efeito; não concede gratuidade.')
    field(185, 2, 'NÍVEL MÍNIMO', list(range(1, 31)), None,
          'Nível mínimo verificável. Em branco com base, herda os requisitos da base.')
    field(186, 2, 'REFINO / LAPIDAÇÃO', list(range(1, 11)), None,
          'Valor mínimo exigido, conforme o tipo. O requisito adicional completo continua no campo REQUISITOS.')
    field(187, 2, 'ESCOLHA', ['Consome uma escolha', 'Gratuita'], 'Consome uma escolha',
          'Proposta de campo: a gratuidade deve ser definida expressamente pelo mestre; não decorre de CE vazia.')
    text(189, 2, 'REQUISITOS', 192, 'Requisitos completos, incluindo capacidades anteriores e aprendizado.')
    text(194, 2, 'EFEITO', 202, 'Descrição completa. A seleção preenche a carta de aptidão/Bênção existente.')

    card(178, 10, 'TALENTO · PERSONAGEM', [x['nome'] for x in rules['passivas']])
    field(183, 10, 'CATEGORIA DE EFEITO', [1, 2, 3], None,
          'A categoria é conferida com a progressão e o limite já existentes de Talentos.')
    field(184, 10, 'ROTA', ['Todas', 'Fundamento / Manejos', 'Técnica Marcial'], 'Todas',
          'Disponibilidade nas mesmas famílias de rota já separadas pelo livro. Sem energia também é Técnica Marcial.')
    text(189, 10, 'REQUISITOS', 192, 'Condições adicionais declaradas pelo mestre; texto não cria automações novas.')
    text(194, 10, 'EFEITO', 202, 'Descrição completa, exibida na carta de Talento existente.')

    card(206, 2, 'TIPO DE ENTIDADE', [x['nome'] for x in inv['tipos']])
    field(211, 2, 'VIDA', ['Normal da entidade', 'Corpo de criação'], None,
          'Em branco herda a base; sem base usa a vida normal. Corpo de criação usa a regra publicada de 4 + Constituição após o primeiro nível.')
    field(212, 2, 'TALISMÃ', ['Não usa', 'Usa'], None,
          'Em branco herda a base; sem base não usa. Usar habilita o tratamento de carga da entidade de criação.')
    field(214, 2, 'RESERVA DE PE', ['Normal da entidade', 'Maldição domada'], None,
          'Em branco herda a base; sem base usa a reserva normal. A opção domada aplica o cálculo já publicado.')
    text(217, 2, 'DEFINIÇÃO', 220, 'Corpo, natureza e características do tipo de entidade.')
    text(222, 2, 'EFEITO E REQUISITOS', 230, 'Outras regras e requisitos próprios do tipo, exibidos na ficha selecionada.')

    card(206, 10, 'TALENTO · ENTIDADE', [x['nome'] for x in inv['talentos']])
    field(211, 10, 'CATEGORIA DE EFEITO', [1, 2, 3], None,
          'Conferida com a Categoria de Efeito que o nível da entidade permite. As escolhas da Trilha continuam com teto 1.')
    text(217, 10, 'REQUISITOS', 220, 'Exigências completas do Talento de entidade.')
    text(222, 10, 'EFEITO', 230, 'Descrição completa, exibida na carta existente. Base conserva as verificações específicas.')

    card(234, 2, 'TIPO DE DANO')
    text(239, 2, 'DEFINIÇÃO', 244, 'Natureza do dano criado com o mestre. Nome entra nos menus de tipo de dano.')
    text(246, 2, 'EFEITO E REQUISITOS', 258,
         'Interações e requisitos. Resistência, vulnerabilidade e dano aplicados em jogo não são deduzidos deste texto.')

    card(234, 10, 'CONDIÇÃO · MELHORIA', list(cat['condicoes']))
    field(239, 10, 'FAMÍLIA', list(cat['familias']), 'Controle',
          'Condição ocupa um cadastro de Melhoria e usa o mesmo catálogo de Famílias, livro + custom.')
    field(240, 10, 'PESO', ['Leve', 'Média', 'Pesada'], None,
          'O peso define o preço e quais menus aceitam a condição, inclusive a básica quando for Leve.')
    field(241, 10, 'EXIGE TR', value='="Sim"',
          note='Condição segue a regra publicada: pede TR mesmo em um feitiço ou habilidade de ataque.')
    text(246, 10, 'EFEITO E REQUISITOS', 258,
         'Efeito, duração, encerramento e limites da condição. Usa os mesmos espaços e orçamento de Melhorias.')
    return dict(sheetId=SID, requests=req, controls=controls, anchors=anchors,
                ranges=['B175:O202', 'B206:O230', 'B234:O258'])


if __name__ == '__main__':
    out = Path(sys.argv[1])
    model = build()
    out.write_text(json.dumps(model, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps({'requests': len(model['requests']), 'controls': len(model['controls']),
                      'bytes': out.stat().st_size}))
