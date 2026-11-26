"""Extensão aditiva: duas vagas de Classe 0 sem mover endereços existentes.

Aplicada após a apresentação final dos cartões. Os 249 contextos históricos
continuam nas mesmas posições; os dois novos ficam no fim do registro.
"""
import copy
import re
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import coordinate_to_tuple, get_column_letter as L, range_boundaries
import montagens_r53 as R

AM = 'FICHA AMALDIÇOADA'
DC = 'DADOS_CUSTOM'
BONUS, QUANTOS, AVISO = 'B134', 'B135', 'B136'


def aplica(layout, tr, analise=None):
    if tr.get('pratica_cotidiana'):
        raise ValueError('Prática Cotidiana já aplicada')
    abas = {a['nome']: a for a in layout['abas']}
    cells = {n: {v[0]: v for v in a['celulas']} for n, a in abas.items()}
    if len(tr['contextos']) != 249 or len([g for g in tr['contextos'] if g['modo'] == 'Classe 0']) != 5:
        raise ValueError('Registro anterior de cartões divergente')
    base = copy.deepcopy(next(g for g in tr['contextos'] if g['id'] == 'classe0.5'))
    rbase = coordinate_to_tuple(base['cel']['nome'])[0]
    # 26/11/2026 (etapa 3 da versão rápida): o cartão de Classe 0 do personagem é leve. A linha dele na FICHA AMALDIÇOADA
    # só aponta para a conta da DADOS_AM (a tabela "classe 0 anotada"); as duas vagas novas ganham duas linhas a mais
    # nessa tabela, logo abaixo da quinta, nas mesmas colunas
    leve = base.get('leve', False)
    zrow, zcols = None, set()
    if leve:
        zref = re.fullmatch(r"='?DADOS_AM'?!\$([A-Z]+)\$(\d+)", cells[AM][base['cel']['dano']][1] or '')
        if not zref:
            raise ValueError('Classe 0 leve sem referência à DADOS_AM')
        zrow = int(zref[2])
        cz = next(coordinate_to_tuple(v[0])[1] for v in abas['DADOS_AM']['celulas']
                  if coordinate_to_tuple(v[0])[0] == 1 and v[1] == 'classe 0 anotada')
        zcols = set(range(cz, cz + 8))
    # Só há uma linha vazia antes da Liberação. Acrescentar o bloco no fim
    # evita deslocar esse título e todos os contratos que vêm depois dele.
    start = abas[AM]['linhas'] + 2
    entry = start + 3
    total = 'DADOS_AM!$HM$10'
    for p in (BONUS, QUANTOS, AVISO):
        if cells[DC].get(p, [None, None])[1] is not None:
            raise ValueError('Helper de Prática Cotidiana ocupado')
    def put(owner, pos, value, style=None):
        if pos in cells[owner]:
            cells[owner][pos][1] = value
            if style is not None:
                cells[owner][pos][2] = style
        else:
            v = [pos, value, style]
            cells[owner][pos] = v
            abas[owner]['celulas'].append(v)
    def mapper(ui, row, editor, zalvo=None):
        def coord(owner, text):
            m = re.fullmatch(r'(\$?)([A-Z]+)(\$?)([0-9]+)', text)
            if not m:
                return text
            n = int(m[4])
            if owner == AM and n == rbase:
                n = ui
            elif owner == R.DADOS and n == base['linha']:
                n = row
            elif owner == R.EDITOR and base['editor'] <= n < base['editor'] + R.PASSO:
                n += editor - base['editor']
            elif owner == 'DADOS_AM' and zalvo and n == zrow and coordinate_to_tuple(m[2] + '1')[1] in zcols:
                n = zalvo
            return m[1] + m[2] + m[3] + str(n)
        def formula(value, owner):
            if not isinstance(value, str) or not value.startswith('='):
                return value
            out = []
            for token in Tokenizer(value).items:
                text = token.value
                if token.type == 'OPERAND' and token.subtype == 'RANGE':
                    prefix, address = text.rsplit('!', 1) if '!' in text else ('', text)
                    source = prefix.strip("'").replace("''", "'") if prefix else owner
                    text = (prefix + '!' if prefix else '') + ':'.join(coord(source, p) for p in address.split(':'))
                out.append(text)
            return '=' + ''.join(out)
        return coord, formula
    for i in range(2):
        # A251/B251 guardam r53.editor.gid nas fichas existentes.
        row = max(coordinate_to_tuple(v[0])[0] for v in abas[R.DADOS]['celulas']) + 1
        editor = 5 + len(tr['contextos']) * R.PASSO
        ui = entry + i
        zalvo = zrow + 1 + i if leve else None
        coord, formula = mapper(ui, row, editor, zalvo)
        g = copy.deepcopy(base)
        g.update(id='classe0.' + str(6 + i), linha=row, editor=editor)
        def move(value):
            if isinstance(value, str):
                return coord(AM, value) if re.fullmatch(r'[A-Z]+[0-9]+', value) else formula(value, AM)
            if isinstance(value, list):
                return [move(v) for v in value]
            if isinstance(value, dict):
                return {k: move(v) for k, v in value.items()}
            return value
        for k in ('cel', 'entradas_diretas', 'menus_diretos', 'funcoes_diretas'):
            if k in g:
                g[k] = move(g[k])
        delta = ui - rbase
        for k in ('area_editor', 'area_escrita'):
            if k in g:
                g[k] = [g[k][0] + delta, g[k][1], g[k][2] + delta, g[k][3]]
        if 'gravacoes_diretas' in base:
            g['gravacoes_diretas'] = [[a + delta, b, c + delta, d] for a, b, c, d in base['gravacoes_diretas']]
        g['campos'] = {k: v + editor - base['editor'] for k, v in base['campos'].items()}
        for owner, predicate in ((AM, lambda r: r == rbase),
                                 (R.DADOS, lambda r: r == base['linha']),
                                 (R.EDITOR, lambda r: base['editor'] <= r < base['editor'] + R.PASSO)):
            for pos, value, *rest in list(abas[owner]['celulas']):
                if predicate(coordinate_to_tuple(pos)[0]):
                    target = coord(owner, pos)
                    if target in cells[owner] and cells[owner][target][1] is not None:
                        raise ValueError('Extensão sobrescreveria ' + owner + '!' + target)
                    value = formula(value, owner)
                    if owner == R.DADOS and pos == 'A' + str(base['linha']):
                        value = g['id']
                    elif owner == R.EDITOR and pos == 'A' + str(base['editor']):
                        # O identificador no título é texto dentro da fórmula;
                        # o deslocador de referências não deve alterá-lo.
                        expected = '="' + base['id'] + ' · "&'
                        if not value.startswith(expected):
                            raise ValueError('Título do modelo de montagem divergente')
                        value = '="' + g['id'] + ' · "&' + value[len(expected):]
                    elif owner == R.EDITOR and value == base['id']:
                        value = g['id']
                    put(owner, target, value, rest[0] if rest else None)
            for merge in list(abas[owner]['mescladas']):
                c1, r1, c2, r2 = range_boundaries(merge)
                if predicate(r1) and predicate(r2):
                    abas[owner]['mescladas'].append(':'.join(coord(owner, x) for x in merge.split(':')))
            for p, note in list(abas[owner].get('notas', {}).items()):
                if predicate(coordinate_to_tuple(p)[0]):
                    abas[owner]['notas'][coord(owner, p)] = note
        if leve:
            # a conta leve das duas linhas novas: a da quinta Classe 0, sem o portão de nível (a vaga vem da Prática)
            for pos, value, *rest in list(abas['DADOS_AM']['celulas']):
                r_, c_ = coordinate_to_tuple(pos)
                if r_ == zrow and c_ in zcols:
                    target = L(c_) + str(zalvo)
                    if target in cells['DADOS_AM'] and cells['DADOS_AM'][target][1] is not None:
                        raise ValueError('Extensão sobrescreveria DADOS_AM!' + target)
                    value = formula(value, 'DADOS_AM')
                    if c_ == min(zcols):
                        value = 'Classe 0 · ' + str(6 + i)
                    elif isinstance(value, str):
                        value = value.replace('=IF(5>', '=IF(0>').replace('=IF(OR(5>', '=IF(OR(0>')
                    put('DADOS_AM', target, value, rest[0] if rest else None)
            # os menus de Forma e de peças da linha de Classe 0, nas duas linhas novas
            for m in list(abas[AM]['menus']):
                novos = []
                for parte in m['onde'].split():
                    c1, r1, c2, r2 = range_boundaries(parte)
                    if r1 <= rbase <= r2 and r1 != r2:
                        novos.append(f'{L(c1)}{ui}' if c1 == c2 else f'{L(c1)}{ui}:{L(c2)}{ui}')
                if novos:
                    abas[AM]['menus'].append({**copy.deepcopy(m), 'onde': ' '.join(novos)})
            def da_conta(k):
                z = re.fullmatch(r"='?DADOS_AM'?!\$([A-Z]+)\$(\d+)", cells[AM][g['cel'][k]][1] or '')
                if not z:
                    raise ValueError('Classe 0 da Prática sem referência à DADOS_AM: ' + g['cel'][k])
                return z[1] + z[2]
            name = R.ref(AM, g['cel']['nome'])
            pos = da_conta('dano')
            put('DADOS_AM', pos, f'=IF({name}="","",IF({DC}!$B$134<>2,"Requer Prática Cotidiana",IF({DC}!$B$135>{total},'
                                 f'"Revisar limite de Classe 0",{cells["DADOS_AM"][pos][1][1:]})))')
            pos = da_conta('alcance')
            put('DADOS_AM', pos, f'=IF({DC}!${BONUS[0]}${BONUS[1:]}=2,{cells["DADOS_AM"][pos][1][1:]},"")')
            tr['formulas'][g['id']] = {}
            g['formulas'] = {}
            tr['contextos'].append(g)
            continue
        for m in g['menus_diretos'].values():
            abas[AM]['menus'].append(copy.deepcopy(m))
        newform = {coord(AM, p): formula(v, AM) for p, v in tr['formulas'][base['id']].items()}
        name = R.ref(AM, g['cel']['nome'])
        p = g['cel']['dano']
        newform[p] = f'=IF({name}="","",IF({DC}!$B$134<>2,"Requer Prática Cotidiana",IF({DC}!$B$135>{total},"Revisar limite de Classe 0",{newform[p][1:]})))'
        p = g['cel']['alcance']
        newform[p] = f'=IF({DC}!${BONUS[0]}${BONUS[1:]}=2,{newform[p][1:]},"")'
        for p, value in newform.items():
            put(AM, p, value)
        # Advertências permanecem explícitas, sem apagar montagem nem saldos.
        c = tr['colunas']
        af = c['avisos_funcoes'] + str(row)
        put(R.DADOS, af, f'=TEXTJOIN(" · ",TRUE,IF({DC}!$B$134=2,"","Requer Prática Cotidiana"),IF({DC}!$B$135>{total},"Limite de feitiços Classe 0 excedido",""))')
        valid = c['valida'] + str(row)
        put(R.DADOS, valid, f'=AND({cells[R.DADOS][valid][1][1:]},{DC}!$B$134=2,{DC}!$B$135<={total})')
        tr['formulas'][g['id']] = newform
        g['formulas'] = copy.deepcopy(newform)
        tr['contextos'].append(g)
    abas[AM]['linhas'] = entry + 3
    abas[R.DADOS]['linhas'] = max(abas[R.DADOS]['linhas'], tr['contextos'][-1]['linha'] + 2)
    abas[R.EDITOR]['linhas'] = 5 + len(tr['contextos']) * R.PASSO
    for pos, value, *rest in list(abas[AM]['celulas']):
        if coordinate_to_tuple(pos)[0] == rbase - 5:
            put(AM, re.sub(r'[0-9]+$', str(start+2), pos), value, rest[0] if rest else None)
    for merge in list(abas[AM]['mescladas']):
        c1, r1, c2, r2 = range_boundaries(merge)
        if r1 == r2 == rbase - 5:
            # No exemplar antigo, P:Q ainda estava mesclado e escondia "USAR".
            # O cabeçalho novo deve ter as duas caixas independentes.
            if c1 == 16 and c2 == 17 and not leve:
                continue
            abas[AM]['mescladas'].append(f'{L(c1)}{start+2}:{L(c2)}{start+2}')
    for r, text in ((start, 'CLASSE 0 · VAGAS ADICIONAIS DE PRÁTICA COTIDIANA'),
                    (start+1, '=IF(DADOS_CUSTOM!$B$134=2,"Duas vagas adicionais · seguem as regras normais de Classe 0","Escolha Prática Cotidiana válida para usar estas vagas. As entradas são preservadas.")&IF(DADOS_CUSTOM!$B$136<>""," · "&DADOS_CUSTOM!$B$136,"")'),
                    (rbase+1, f'="Classe 0: "&{DC}!$B$135&" de "&{total}&" conhecidos · vagas adicionais no fim desta aba"&IF({DC}!$B$136<>""," · "&{DC}!$B$136,"")')):
        if r == rbase+1 and any(v[1] is not None and coordinate_to_tuple(v[0])[0] == r and 4 <= coordinate_to_tuple(v[0])[1] <= 20 for v in abas[AM]['celulas']):
            raise ValueError('Linha de orientação ocupada')
        put(AM, 'D'+str(r), text, cells[AM]['D320' if r == start else 'R327'][2])
        abas[AM]['mescladas'].append(f'D{r}:T{r}')
    abas[AM]['linhas_alt'] += [[start, 32], [start+1, 34], [start+2, 30], [entry, 36], [entry+1, 36], [rbase+1, 30]]
    abas[AM]['notas']['P58'] += ' Prática Cotidiana válida acrescenta dois. Há duas vagas adicionais no fim desta aba; retirar a menor conserva as entradas e exige revisar o uso. Elas não fornecem espaços para Talentos ou invocações.'
    put(DC, BONUS, '=IF(AND($B$126,OR(FICHA!$S$52="Prática Cotidiana",FICHA!$AG$52="Prática Cotidiana")),2,0)')
    put(DC, QUANTOS, f'=SUMPRODUCT(--(LEN(\'{AM}\'!D323:D327)>0))+SUMPRODUCT(--(LEN(\'{AM}\'!D{entry}:D{entry+1})>0))')
    put(DC, AVISO, f'=TEXTJOIN(" · ",TRUE,IF(AND($B$134<>2,COUNTA(\'{AM}\'!D{entry}:D{entry+1})>0),"Requer Prática Cotidiana válida",""),IF($B$135>{total},"Revisar: limite de Classe 0 excedido",""))')
    old = cells['DADOS_AM']['HM10'][1]
    put('DADOS_AM', 'HM10', f'=({old[1:]})+{DC}!$B$134')
    # Append contract rows; no historical key changes row, type, origin or value.
    added = {'contextos': tr['contextos'][-2:], 'colunas': tr['colunas']}
    lines = R.exporta(added)[2:] + R.exporta_versoes(added)[1:]
    for i, g in enumerate(added['contextos'], 6):
        prefix = f'zero.{i}'
        lines += [[prefix+'.classe', '0', '', 'entrada'], [prefix+'.pe', '0', '', 'resultado']]
        for k in ['nome', 'forma', 'dano', 'alcance', 'pecas', 'restricoes']:
            p = g['cel'][{'pecas': 'mel', 'restricoes': 'res'}.get(k, k)]
            p = p[0] if isinstance(p, list) else p
            ref = R.ref(AM, p)
            lines.append([prefix+'.'+k, '='+ref+'&""', ref, 'resultado' if k in ['dano', 'alcance'] else 'entrada'])
    for suffix, cell, kind in [('vagas', BONUS, 'resultado'), ('anotados', QUANTOS, 'resultado'), ('aviso', AVISO, 'aviso')]:
        ref = R.ref(DC, cell)
        lines.append(['origem.pratica_cotidiana.'+suffix, '='+ref+'&""', ref, kind])
    last = max(coordinate_to_tuple(v[0])[0] for v in abas['ANALISE']['celulas'])
    style = cells['ANALISE']['A2'][2]
    for row, line in enumerate(lines, last+1):
        for col, value in zip('ABCD', line):
            if col == 'C' and value.startswith("'"):
                value = '="'+value.replace('"', '""')+'"'
            put('ANALISE', col+str(row), value, style)
    abas['ANALISE']['linhas'] = last + len(lines)
    if analise is not None:
        analise['linhas'].extend(copy.deepcopy(lines))
    tr['pratica_cotidiana'] = dict(entradas=[entry, entry+1], analise_inicio=last+1, analise_fim=last+len(lines))
    return tr['pratica_cotidiana']
