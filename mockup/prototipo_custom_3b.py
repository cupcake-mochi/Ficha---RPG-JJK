"""Protótipo nativo 3b. Só emite pedidos de estudo; não modifica o gerador.

Os exemplos não alimentam contas nem ANALISE. A construção depende da
aprovação do desenho. Nunca importa o artefato XLSX no Google Sheets.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SID = 47005
TITLE = 'ESTUDO 3B'
CAT = json.loads((ROOT / 'catalogo-projeto-m.json').read_text())
BG, PANEL, HEADER, INK, LINE = '1B111D', '302034', '492D4D', 'FBE4EF', 'B377BB'


def rgb(h):
    return {k: int(h[i:i+2], 16) / 255 for k, i in zip(['red', 'green', 'blue'], [0, 2, 4])}


def build():
    req, boxes, merges, inputs = [], [], [], []
    def area(r, c, er=None, ec=None):
        return dict(sheetId=SID, startRowIndex=r-1, endRowIndex=er or r,
                    startColumnIndex=c-1, endColumnIndex=ec or c)
    def cell(r, c, value, er=None, ec=None, heading=False, note=None):
        rg = area(r, c, er, ec)
        fmt = dict(backgroundColor=rgb(HEADER if heading else PANEL),
                   textFormat=dict(fontFamily='Oswald' if heading else 'Roboto', fontSize=10,
                                   foregroundColor=rgb(INK)),
                   verticalAlignment='MIDDLE', wrapStrategy='WRAP')
        data = {'userEnteredFormat': fmt}
        if value is not None:
            key = ('boolValue' if isinstance(value, bool) else 'numberValue' if isinstance(value, (int, float))
                   else 'formulaValue' if str(value).startswith('=') else 'stringValue')
            data['userEnteredValue'] = {key: value}
        if note:
            data['note'] = note
        req.append({'updateCells': {'start': dict(sheetId=SID, rowIndex=r-1, columnIndex=c-1),
                                    'rows': [{'values': [data]}], 'fields': 'userEnteredValue,userEnteredFormat,note'}})
        if (er or r, ec or c) != (r, c):
            merges.append(rg)
        boxes.append(rg)
        return rg
    def choices(r, c, values, boolean=False):
        rule = {'condition': {'type': 'BOOLEAN' if boolean else 'ONE_OF_LIST'}, 'strict': True, 'showCustomUi': True}
        if not boolean:
            rule['condition']['values'] = [{'userEnteredValue': str(v)} for v in values]
        req.append({'setDataValidation': {'range': area(r, c), 'rule': rule}})
        inputs.append([r, c, values])
    def field(r, c, label, value, options=None, note='Campo do molde; o exemplo não altera a ficha.'):
        cell(r, c, label, ec=c+2, heading=True, note=note)
        cell(r, c+3, value, ec=c+5, note=note)
        if options:
            choices(r, c+3, options)
    def card(c, typ, name):
        cell(9, c, typ.upper()+' · ESTUDO', ec=c+5, heading=True)
        cell(10, c, 'TIPO', ec=c+3, heading=True)
        cell(10, c+4, 'MESTRE VIU', ec=c+5, heading=True,
             note='Lembrete do jogador. Aprovação continua no bot, pelo chat.')
        cell(11, c, typ, ec=c+3)
        cell(11, c+4, False, ec=c+5)
        choices(11, c+4, [], boolean=True)
        cell(12, c, 'NOME', ec=c+5, heading=True, note='Nome único no livro e no custom.')
        cell(13, c, name, ec=c+5)
    def progression(c, label):
        cell(45, c, 'HABILIDADES POR NÍVEL · '+label, ec=c+5, heading=True,
             note='Uma entrada por nível. Em branco não concede habilidade. Textos do custom entram nas cartas da ficha.')
        cell(46, c, 'NÍVEIS 6–20 E 21–30 · GRUPOS +/−', ec=c+5, heading=True,
             note='Fechar linhas não muda os dados. O segundo grupo conserva os níveis 23, 27 e 30 do livro.')
        for n in range(1, 31):
            r = 48+(n-1)*3
            cell(r, c, n, heading=True, note='Nível de aquisição; não muda o nível inicial da campanha.')
            cell(r, c+1, 'Habilidade de exemplo' if n == 2 else None, ec=c+5,
                 note='Nome da habilidade deste nível. Vazio quando o nível não dá habilidade.')
            cell(r+1, c, 'Texto completo da habilidade criada com o mestre.' if n == 2 else None,
                 er=r+2, ec=c+5, note='Efeito, ação, custo, frequência e limites. A ficha não interpreta prosa para alterar números.')

    req.append({'repeatCell': {'range': area(1, 1, 184, 16), 'cell': {'userEnteredFormat': {
        'backgroundColor': rgb(BG), 'textFormat': {'fontFamily': 'Roboto', 'fontSize': 10, 'foregroundColor': rgb(INK)}}},
        'fields': 'userEnteredFormat'}})
    cell(2, 2, 'CONFIGURAÇÃO · ESTUDO 3B', er=3, ec=15, heading=True)
    cell(5, 2, 'PROPOSTA · 133 novos registros: 1 Caminho + 1 Trilha + 108 perícias + 23 ofícios.', ec=15)
    cell(6, 2, 'Perícias: 23 + 12×7 + 1. Ofícios: 11 + 12. Com a 3a: 158 registros. Custo final a medir.', ec=15)
    cell(7, 2, 'Exemplos de desenho · sem efeito nas contas · títulos e listas seguem a ficha.', ec=15)
    card(2, 'Caminho', 'Caminho de exemplo')
    attrs = ['—', 'Força', 'Destreza', 'Constituição', 'Inteligência', 'Essência']
    # O sistema usa cinco atributos: não inventar um sexto por hábito de outros jogos.
    per = ['—'] + list(CAT['pericias']) + ['Rituais Urbanos · exemplo']
    fields = [
        ('VIDA INICIAL', 8, None), ('VIDA POR NÍVEL', 5, None),
        ('DADO DE VIDA', 'd8', ['d4', 'd6', 'd8', 'd10', 'd12', 'd20']),
        ('PE POR NÍVEL', 5, None), ('ATRIBUTO NATURAL 1', 'Destreza', attrs),
        ('ATRIBUTO NATURAL 2', 'Força', attrs), ('PERÍCIA FIXA 1', 'Acrobacia', per),
        ('PERÍCIA FIXA 2', 'Percepção', per),
        ('TROCA PERÍCIAS POR ARMA', 'Não', ['Sim', 'Não']),
        ('TREINO DE ARMA', 'Todas', ['Todas', 'Categorias selecionadas'])]
    for r, (label, val, opts) in enumerate(fields, 14):
        note = ('Permite a troca já existente de duas perícias por categoria de arma; não concede treino extra sem pagar.'
                if label.startswith('TROCA') else 'Dado usado na variante de vida rolada; vida inicial continua fixa.'
                if label == 'DADO DE VIDA' else 'Mesmo campo das características do Caminho. Valores do exemplo vêm da Vanguarda.')
        field(r, 2, label, val, opts, note)
    categories = sorted({a['categoria'] for a in CAT['equipamento']['armas'].values()})
    for i in range(len(categories)):
        field(24+i, 2, 'CATEGORIA DE ARMA '+str(i+1), '—', ['—']+categories,
              'Preencha categorias distintas quando TREINO DE ARMA usar a seleção. Todas já inclui o catálogo inteiro.')
    cell(39, 2, 'OBSERVAÇÕES', ec=7, heading=True)
    cell(40, 2, 'Treinos, números e textos próprios do Caminho. Alterações numéricas específicas continuam em BÔNUS E MUDANÇAS.', er=43, ec=7)
    progression(2, 'CAMINHO')
    card(10, 'Trilha', 'Trilha de exemplo')
    field(14, 10, 'CAMINHO', 'Caminho de exemplo', list(CAT['caminhos'])+['Caminho de exemplo'],
          'Livro + custom. A Trilha aparece somente no Caminho escolhido, como as Trilhas do livro.')
    cell(16, 10, 'ROTAS', ec=15, heading=True)
    cell(17, 10, 'Se houver versões por rota, cada versão tem nome próprio no menu, como Batedor · Yumi. A vinculação continua sendo ao Caminho.', er=20, ec=15)
    cell(22, 10, 'EFEITO E ESCOLHAS', ec=15, heading=True)
    cell(23, 10, 'Registre nas habilidades os textos de cada nível. Escolhas específicas que precisem de novos campos serão levantadas antes da integração.', er=28, ec=15)
    cell(30, 10, 'REGISTROS', ec=15, heading=True)
    cell(31, 10, 'Um Caminho e uma Trilha são usados por personagem. Uma rota alternativa pode usar outro registro do mesmo tipo, se a capacidade final for ampliada.', er=35, ec=15)
    cell(39, 10, 'OBSERVAÇÕES', ec=15, heading=True)
    cell(40, 10, 'Os grupos do estudo fecham níveis dos dois painéis. Na CONFIGURAÇÃO, ficam abaixo do fim da parte 3a, sem esconder bônus ou campanha.', er=43, ec=15)
    progression(10, 'TRILHA')
    for c, typ, name, attr, text in [
        (2, 'Perícia', 'Rituais Urbanos · exemplo', 'Inteligência', 'Escreva o escopo da perícia criada com o mestre.'),
        (10, 'Ofício', 'Restauro · exemplo', 'Destreza', 'Escreva tarefas, ferramentas e requisitos do ofício.')]:
        type_cell = '$E$145' if c == 2 else '$M$145'
        cell(143, c, f'=UPPER({type_cell})&" · MOLDE CURTO"', ec=c+5, heading=True)
        field(145, c, 'TIPO', typ, ['Perícia', 'Ofício'])
        field(146, c, 'NOME', name)
        field(147, c, f'=IF({type_cell}="Perícia";"ATRIBUTO";"ATRIBUTO PADRÃO")', attr, attrs[1:],
              'Perícia usa atributo fixo. Ofício tem padrão; o mestre pode trocar conforme a tarefa (R52, capítulo 7).')
        field(148, c, 'MESTRE VIU', False)
        choices(148, c+3, [], boolean=True)
        cell(150, c, 'DESCRIÇÃO', ec=c+5, heading=True)
        cell(151, c, text, er=155, ec=c+5)
        cell(157, c, 'NA FICHA · PROPOSTA', ec=c+5, heading=True)
        cell(158, c, 'Linhas próprias de custom com TREINO, ESPECIALIZAÇÃO e resultado; entram nos totais já existentes sem conceder escolhas extras.', er=162, ec=c+5)
    cell(166, 2, 'CAPACIDADE · PROPOSTA PARA APROVAÇÃO', ec=15, heading=True)
    cell(167, 2, '131 cartões curtos de Perícia/Ofício, além de 1 Caminho e 1 Trilha. Inclui os lugares das 12 entidades e a perícia da FICHA AMALDIÇOADA. Um registro pode ser reutilizado; as listas do livro continuam disponíveis.', er=169, ec=15)
    cell(171, 2, 'ESPAÇO NA CONFIGURAÇÃO', ec=15, heading=True)
    cell(172, 2, 'Parte 3b abaixo do cartão 25 da 3a. Caminho e Trilha usam cartões longos; perícias e ofícios compartilham molde curto. Não aumentar todos os cartões antigos.', er=175, ec=15)
    cell(177, 2, 'CUSTO', ec=15, heading=True)
    cell(178, 2, 'Tamanho real dos .gs e tempo do construir() dependem da integração. O estudo mede apenas pedidos de desenho, não fecha o orçamento final.', er=181, ec=15)
    # Estilo em toda a caixa, incluindo células mescladas; contorno por caixa.
    req += [{'mergeCells': {'range': rg, 'mergeType': 'MERGE_ALL'}} for rg in merges]
    edge = {'style': 'SOLID', 'color': rgb(LINE)}
    req += [{'updateBorders': {'range': rg, 'top': edge, 'bottom': edge, 'left': edge, 'right': edge}} for rg in boxes]
    # Uma linha de intervalo evita que o Sheets junte grupos adjacentes.
    # O título do nível 21 permanece visível como referência do segundo grupo.
    for start, end in [(62, 107), (108, 137)]:
        rg = dict(sheetId=SID, dimension='ROWS', startIndex=start, endIndex=end)
        req += [{'addDimensionGroup': {'range': rg}},
                {'updateDimensionGroup': {'dimensionGroup': {'range': rg, 'depth': 1, 'collapsed': True}, 'fields': 'collapsed'}},
                {'updateDimensionProperties': {'range': rg, 'properties': {'hiddenByUser': True}, 'fields': 'hiddenByUser'}}]
    widths = [22, 70, 55, 70, 80, 70, 75, 18, 18, 70, 55, 70, 80, 70, 75, 22]
    for i, width in enumerate(widths):
        req.append({'updateDimensionProperties': {'range': dict(sheetId=SID, dimension='COLUMNS', startIndex=i, endIndex=i+1),
                                                  'properties': {'pixelSize': width}, 'fields': 'pixelSize'}})
    req.append({'updateDimensionProperties': {'range': dict(sheetId=SID, dimension='ROWS', startIndex=0, endIndex=184),
                                              'properties': {'pixelSize': 27}, 'fields': 'pixelSize'}})
    return {'sheetId': SID, 'title': TITLE, 'requests': req, 'inputs': inputs,
            'capacity_proposal': {'Caminho': 1, 'Trilha': 1, 'Perícia': 23+12*7+1, 'Ofício': 11+12},
            'notes': 'Somente estudo. Sem construção de contas ou contrato. Custo real ainda depende da integração.'}


if __name__ == '__main__':
    import sys
    dest = Path(sys.argv[1])
    model = build()
    dest.write_text(json.dumps(model, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps({'pedidos': len(model['requests']), 'bytes_estudo': dest.stat().st_size,
                      'capacidade_proposta': model['capacity_proposal']}, ensure_ascii=False))
