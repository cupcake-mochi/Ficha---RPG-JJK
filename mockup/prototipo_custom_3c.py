"""Estudo nativo de Famílias e peças, sem integração à ficha ou ANALISE.

Emite somente pedidos para uma aba de estudo. Não importa Excel nem altera
CONFIGURAÇÃO. Quantidade final de registros depende do orçamento da integração.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SID, TITLE = 47007, 'ESTUDO 3C'
CAT = json.loads((ROOT / 'catalogo-projeto-m.json').read_text())
BG, PANEL, HEAD, INK, LINE = '1B111D', '302034', '492D4D', 'FBE4EF', 'B377BB'


def rgb(h):
    return dict(zip(('red', 'green', 'blue'), (int(h[i:i+2], 16)/255 for i in (0, 2, 4))))


def build():
    req, boxes, merges, controls = [], [], [], []

    def area(r, c, er=None, ec=None):
        return dict(sheetId=SID, startRowIndex=r-1, endRowIndex=er or r,
                    startColumnIndex=c-1, endColumnIndex=ec or c)

    def cell(r, c, value, er=None, ec=None, heading=False,
             note='Estudo de desenho. Este campo não alimenta as contas da ficha.'):
        rg = area(r, c, er, ec)
        fmt = dict(backgroundColor=rgb(HEAD if heading else PANEL),
                   textFormat=dict(fontFamily='Oswald' if heading else 'Roboto', fontSize=10,
                                   foregroundColor=rgb(INK)),
                   wrapStrategy='WRAP', verticalAlignment='MIDDLE')
        req.append({'repeatCell': {'range': rg, 'cell': {'userEnteredFormat': fmt},
                                    'fields': 'userEnteredFormat'}})
        key = ('boolValue' if isinstance(value, bool) else 'numberValue' if isinstance(value, (int, float))
               else 'formulaValue' if isinstance(value, str) and value.startswith('=') else 'stringValue')
        data = {'note': note}
        if value is not None:
            data['userEnteredValue'] = {key: value}
        req.append({'updateCells': {'start': dict(sheetId=SID, rowIndex=r-1, columnIndex=c-1),
                                    'rows': [{'values': [data]}], 'fields': 'userEnteredValue,note'}})
        if (er or r, ec or c) != (r, c):
            merges.append(rg)
        boxes.append(rg)

    def choices(r, c, values=None, condition=None):
        condition = condition or ({'type': 'BOOLEAN'} if values is None else
                                  {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': str(x)} for x in values]})
        req.append({'setDataValidation': {'range': area(r, c), 'rule': {
            'condition': condition, 'strict': True, 'showCustomUi': True}}})
        controls.append([r, c, condition])

    def field(r, c, label, value, options=None, note=None):
        kw = {'note': note} if note else {}
        cell(r, c, label, ec=c+2, heading=True, **kw)
        cell(r, c+3, value, ec=c+5, **kw)
        if options:
            choices(r, c+3, options)

    def card(r, c, typ, name, base=None):
        cell(r, c, typ.upper()+' · MOLDE EM ESTUDO', ec=c+5, heading=True)
        cell(r+1, c, 'NOME', ec=c+3, heading=True, note='Nome único no livro e nos cadastros custom.')
        cell(r+1, c+4, 'MESTRE VIU', ec=c+5, heading=True,
             note='Lembrete marcado pelo jogador. Quem aprova continua sendo o bot, no chat.')
        cell(r+2, c, name, ec=c+3)
        cell(r+2, c+4, False, ec=c+5)
        choices(r+2, c+4)
        if base:
            field(r+4, c, 'BASE DO LIVRO', 'Nenhuma', ['Nenhuma']+base,
                  'Opcional, conforme aprovado. Uma base herda suas automações; sem base, usa os campos próprios. '
                  'Campos vazios com base herdam o livro; sem base, os campos necessários precisam estar preenchidos.')

    req.append({'repeatCell': {'range': area(1, 1, 124, 16), 'cell': {'userEnteredFormat': {
        'backgroundColor': rgb(BG), 'textFormat': {'fontFamily': 'Roboto', 'fontSize': 10,
                                                'foregroundColor': rgb(INK)}}}, 'fields': 'userEnteredFormat'}})
    cell(2, 2, 'CONFIGURAÇÃO · ESTUDO 3C', er=3, ec=15, heading=True)
    cell(5, 2, 'PRIMEIRO BLOCO · Famílias, Formas, Melhorias e Restrições. Exemplos sem efeito na ficha.', ec=15)
    cell(6, 2, 'Base do livro opcional · menus fechados para opções fixas · texto completo nos cartões existentes.', ec=15)
    cell(8, 2, 'FAMÍLIAS · REGRA DA CAMPANHA EM ESTUDO', ec=7, heading=True)
    for c, label, end in [(2, 'REGRA', 4), (5, 'LIVRO', 5), (6, 'CAMPANHA', 6), (7, 'EM USO', 7)]:
        cell(9, c, label, ec=end, heading=True)
    for r, label, book, campaign, use in [
        (11, 'Famílias Livres', 2, None, '=IF(F11="";E11;F11)'),
        (12, 'Famílias Fechadas', 3, None, '=IF(F12="";E12;F12)'),
        (13, 'Famílias Neutras', 4, 'saldo', '=G14-G11-G12'),
        (14, 'Famílias disponíveis', 9, 'catálogo', '=9+IF(J11="";0;1)')]:
        note = ('PROPOSTA: Neutras são o total disponível menos Livres e Fechadas. '
                'A família de exemplo acrescenta uma ao total; não substitui nenhuma das nove do livro.')
        cell(r, 2, label, ec=4, note=note)
        cell(r, 5, book, note=note)
        cell(r, 6, campaign, note=note)
        cell(r, 7, use, note=note)
    for r in (11, 12):
        choices(r, 6, condition={'type': 'CUSTOM_FORMULA', 'values': [{'userEnteredValue':
            f'=OR(F{r}="";AND(ISNUMBER(F{r});F{r}>=0;MOD(F{r};1)=0))'}]})
    cell(16, 2, '=IF(G13<0;"ERRO · Livres + Fechadas ultrapassam o total.";"Em branco usa o livro. Neutras são calculadas pelo saldo.")',
         er=17, ec=7)
    cell(19, 2, 'A quantidade vale para o personagem. A proposta conserva os limites próprios das entidades.', er=21, ec=7)
    card(9, 10, 'Família', 'Ressonância · exemplo')
    field(13, 10, 'ESTADO', 'Neutra', ['Livre', 'Neutra', 'Fechada'],
          'Estado desta família na ficha do personagem. Deve contar junto das nove famílias publicadas.')
    cell(15, 10, 'DESCRIÇÃO', ec=15, heading=True)
    cell(16, 10, 'Descreva o tema da família criada com o mestre.', er=19, ec=15)
    cell(21, 10, 'Aparece nas listas de Família das peças e entidades. A ficha conserva as nove famílias do livro.', er=24, ec=15)
    cell(26, 2, 'DESTINO NA FICHA', ec=15, heading=True)
    cell(27, 2, 'Famílias novas ganham seu estado junto às existentes. Formas, Melhorias e Restrições entram nos menus '
         'e nas contas dos cartões que já existem; não criam outro conjunto de feitiços.', er=29, ec=15)

    card(33, 2, 'Forma', 'Forma própria · exemplo', list(CAT['formas']))
    card(33, 10, 'Melhoria', 'Melhoria própria · exemplo', list(CAT['melhorias']))
    families = ['Nenhuma']+list(CAT['familias'])+['Ressonância · exemplo']
    for r, label, val, opts in [
        (39, 'FAMÍLIA', 'Ressonância · exemplo', families),
        (40, 'PESO', 'Leve', ['Sem custo', 'Leve', 'Média', 'Pesada']),
        (41, 'RESOLUÇÃO', 'Acerto', ['Acerto', 'TR, metade', 'Automático']),
        (42, 'RESULTADO', 'Dano', ['Dano', 'Cura', 'Vida temporária', 'Efeito']),
        (43, 'EXIGE TR', 'Não', ['Sim', 'Não']),
        (44, 'CLASSE 0', 'Não', ['Sim', 'Não']),
        (45, 'RESTRIÇÃO EMBUTIDA', 'Nenhuma', ['Nenhuma']+list(CAT['restricoes']))]:
        field(r, 2, label, val, opts)
    cell(47, 2, 'ALCANCE E ÁREA', ec=7, heading=True)
    cell(48, 2, 'Bases por faixa de Classe e escadas no quadro abaixo. Com base do livro, herda a tabela completa.', er=50, ec=7)
    cell(52, 2, 'EFEITO E REQUISITOS', ec=7, heading=True)
    cell(53, 2, 'Texto completo da Forma: alvos, origem da área, requisitos e limites.', er=57, ec=7)
    for r, label, val, opts in [
        (39, 'FAMÍLIA', 'Ressonância · exemplo', families),
        (40, 'PESO', 'Leve', ['Leve', 'Média', 'Pesada']),
        (41, 'EXIGE TR', 'Não', ['Sim', 'Não'])]:
        field(r, 10, label, val, opts)
    cell(43, 10, 'REQUISITOS E REPETIÇÃO', ec=15, heading=True)
    cell(44, 10, 'Escreva requisitos, incompatibilidades e quantas vezes pode comprar. '
         'A base herda as verificações específicas já existentes; efeitos próprios precisam de campos mecânicos explícitos.', er=48, ec=15)
    cell(52, 10, 'EFEITO', ec=15, heading=True)
    cell(53, 10, 'Texto completo da Melhoria, sem fórmula digitada no texto.', er=57, ec=15)

    card(61, 2, 'Restrição', 'Restrição própria · exemplo', list(CAT['restricoes']))
    field(67, 2, 'DEVOLUÇÃO', 'Leve', ['Leve', 'Média'],
          'Segue a devolução existente: não paga a Forma, respeita o teto e o gasto com Melhorias.')
    field(68, 2, 'FREQUÊNCIA', 'Não', ['Sim', 'Não'],
          'Identifica as Restrições de frequência para as verificações já existentes. A base herda sua categoria.')
    cell(70, 2, 'EFEITO E REQUISITOS', ec=7, heading=True)
    cell(71, 2, 'Texto completo: exigência, momento de cumprir, duração e incompatibilidades.', er=77, ec=7)
    cell(61, 10, 'FORMA · QUADRO DE ALCANCE EM ESTUDO', ec=15, heading=True)
    field(63, 10, 'ESCADA DE ALCANCE', 'alcance', ['Fixo']+list(json.loads((ROOT/'ficha-v01/tecnica-do-livro.json').read_text())['escadas']))
    field(64, 10, 'ESCADA DE ÁREA', 'Fixo', ['Fixo', 'raio', 'comprimento'])
    for r, label, val in [(66, 'PERSONAGEM · CLASSE 0', 'Indisponível'),
                          (67, 'PERSONAGEM · CLASSES 1–5', '18 m'),
                          (68, 'PERSONAGEM · CLASSES 6–7', '18 m'),
                          (70, 'ENTIDADE · CLASSE 0', 'Indisponível'),
                          (71, 'ENTIDADE · CLASSES 1–5', '18 m'),
                          (72, 'ENTIDADE · CLASSE 6', '18 m'),
                          (73, 'ENTIDADE · CLASSE 7', '18 m')]:
        field(r, 10, label, val, note='O livro tem faixas distintas para personagem e entidade; conservar as duas tabelas. '
              'O desenho final precisa separar alcance e tamanho da área, com valores de base compatíveis com a escada.')
    cell(75, 10, 'Valores acima só ilustram os campos. Os degraus continuam vindo das escadas do livro.', er=77, ec=15)
    cell(81, 2, 'CAPACIDADE · INVENTÁRIO, AINDA SEM FECHAR O ORÇAMENTO', ec=15, heading=True)
    for r, label, count in [(83, 'Forma: 45 na técnica + 12 × 13 nas entidades', 201),
                            (84, 'Melhoria: 165 na técnica + 12 × 52 nas entidades', 789),
                            (85, 'Restrição: 83 na técnica + 12 × 26 nas entidades', 395),
                            (86, 'Família: 108 seleções nas entidades; catálogo também usado pelas peças', 108)]:
        cell(r, 2, label, ec=13)
        cell(r, 14, count, ec=15)
    cell(88, 2, 'São lugares independentes, não conteúdo distinto obrigatório. Um cadastro pode ser reutilizado. '
         'Condições aparecem como Melhorias; não são outros 13 menus.', er=90, ec=15)
    cell(92, 2, 'CUSTO ANTES DE FECHAR A CAPACIDADE', ec=15, heading=True)
    cell(93, 2, 'O estudo não mede o tamanho final dos .gs nem o tempo de construir(). '
         'A integração precisará de divisão de arquivos e medição na cópia descartável; '
         'não reutilizar os 6 min 16,8 s da 3b como previsão da 3c.', er=96, ec=15)
    cell(99, 2, 'DEPOIS DESTE DESENHO', ec=15, heading=True)
    cell(100, 2, 'Aptidões/Bênçãos, Talentos, tipos/Talentos de entidade, condições e tipos de dano terão '
         'seus moldes e dependências apresentados antes de integrar. Base opcional já aprovada.', er=103, ec=15)
    cell(106, 2, 'DECISÃO PEDIDA NESTA RODADA', ec=15, heading=True)
    cell(107, 2, 'Aprovar ou ajustar o desenho dos limites de Famílias e o primeiro conjunto de campos. '
         'Não é aprovação de uma capacidade ou de um custo ainda não medido.', er=110, ec=15)

    req += [{'mergeCells': {'range': x, 'mergeType': 'MERGE_ALL'}} for x in merges]
    edge = {'style': 'SOLID', 'color': rgb(LINE)}
    req += [{'updateBorders': {'range': x, 'top': edge, 'bottom': edge, 'left': edge, 'right': edge}} for x in boxes]
    widths = [22, 70, 55, 70, 80, 70, 75, 18, 18, 70, 55, 70, 80, 70, 75, 22]
    for i, width in enumerate(widths):
        req.append({'updateDimensionProperties': {'range': dict(sheetId=SID, dimension='COLUMNS', startIndex=i, endIndex=i+1),
                                                  'properties': {'pixelSize': width}, 'fields': 'pixelSize'}})
    req.append({'updateDimensionProperties': {'range': dict(sheetId=SID, dimension='ROWS', startIndex=0, endIndex=124),
                                              'properties': {'pixelSize': 27}, 'fields': 'pixelSize'}})
    return {'sheetId': SID, 'title': TITLE, 'requests': req, 'controls': controls}


if __name__ == '__main__':
    import sys
    dest = Path(sys.argv[1])
    model = build()
    dest.write_text(json.dumps(model, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps({'pedidos': len(model['requests']), 'bytes_estudo': dest.stat().st_size,
                      'controles': len(model['controls'])}))
