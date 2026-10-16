"""Condição é modalidade dos mesmos cadastros/consumidores de Melhoria."""
import indice_ficha as ix
import json
from pathlib import Path
from custom_criacao import criterio, ref
from custom_pecas import MEL, coord, faixa


def aplica(layout, pecas):
    data = ix._aba(layout, MEL)
    config = ix._aba(layout, 'CONFIGURAÇÃO')
    conditions = json.loads((Path(__file__).resolve().parent.parent/'catalogo-projeto-m.json').read_text(encoding='utf-8'))['condicoes']
    cells = {a['nome']: {v[0]: v for v in a['celulas']} for a in layout['abas']}
    tr = dict(antes={}, depois={}, entradas=[], registros=[], catalogos={})

    def put(sheet, a1, value):
        old = cells[sheet].get(a1)
        before = old[1] if old else None
        if before != value:
            tr['antes'].setdefault(sheet, {}).setdefault(a1, before)
            tr['depois'].setdefault(sheet, {})[a1] = value
        if old is None:
            old = [a1, value, None]
            cells[sheet][a1] = old
            ix._aba(layout, sheet)['celulas'].append(old)
        else:
            old[1] = value

    if 'BR1' in cells[MEL]:
        raise ValueError('Coluna reservada para modalidade já ocupada')
    put(MEL, 'BR1', 'modalidade da Melhoria')
    put(MEL, 'BT1', 'modalidades')
    put(MEL, 'BT2', 'Melhoria')
    put(MEL, 'BT3', 'Condição')
    put(MEL, 'BU1', 'bases de Condição')
    put(MEL, 'BU2', 'Nenhuma')
    for r, name in enumerate(conditions, 3):
        put(MEL, 'BU'+str(r), name)
    modes = faixa(MEL, 72, 2, 72, 3)
    bases = faixa(MEL, 73, 2, 73, len(conditions)+2)
    melhorias = [g for g in pecas['registros'] if g['tipo'] == 'melhoria']
    data['colunas'] = max(data['colunas'], 73+len(melhorias))
    if data['colunas_larg']:
        data['colunas_larg'][0][1] = data['colunas']
    nbook = pecas['limites'][MEL]['livro']
    for i, g in enumerate(melhorias):
        n, r = g['n'], g['n']+1
        dst = nbook+n+1
        a1 = coord(g['r']+2, g['c'])
        source = ref(a1, 'CONFIGURAÇÃO')
        put(MEL, 'BR'+str(r), f'=IF(OR(ISBLANK({source}),{source}=""),"Melhoria",{source})')
        tr['entradas'].append((f'custom.melhoria.{n}.modalidade', a1, False))
        tr['registros'].append(dict(n=n, modalidade=a1))
        config['menus'].append(dict(onde=a1, tipo='list', formula=modes,
            vazio_ok=True, mostra_seta=True, estrito=True))
        config.setdefault('menus_estritos', []).append(a1)
        config.setdefault('notas', {})[a1] = ('Condição usa este mesmo cadastro e orçamento de Melhoria. '
            'Família em branco usa a base ou Controle sem base; EXIGE TR deve ficar vazio ou Sim. '
            'Peso e efeito seguem os campos deste cartão. Texto não executa regras.')
        for menu in config['menus']:
            if menu['onde'] == g['base']:
                # Apps Script requireValueInRange exige referência estática.
                # Cada cartão filtra o catálogo em uma coluna técnica própria;
                # trocar a modalidade recompõe a lista sem trocar a validação.
                col = 74+i
                put(MEL, coord(1, col), f'bases do cadastro {n}')
                pool = f'$BP$2:$BP${nbook+2}'
                put(MEL, coord(2, col),
                    f'=FILTER({pool},ARRAYFORMULA(IF($BR${r}="Condição",'
                    f'COUNTIF({bases},{pool})>0,ROW({pool})>0)))')
                menu['formula'] = faixa(MEL, col, 2, col, nbook+2)
                break
        else:
            raise ValueError('Menu da base da Melhoria não encontrado')
        old_error = cells[MEL]['M'+str(r)][1][1:]
        errors = [f'IF(AND(BR{r}<>"Melhoria",BR{r}<>"Condição"),"Modalidade inválida","")',
                  f'IF(AND(BR{r}="Condição",E{r}<>"",E{r}<>"Nenhuma",COUNTIF({bases},{criterio("E"+str(r))})<>1),"Base de Condição inválida","")',
                  f'IF(AND(BR{r}="Condição",H{r}<>"",H{r}<>"Sim"),"Condição exige TR","")']
        put(MEL, 'M'+str(r), f'=IF(D{r}="",IF(BR{r}<>"Melhoria","Preencha NOME",{old_error}),TEXTJOIN(" · ",TRUE,{old_error},{",".join(errors)}))')
        for col in ['P', 'T', 'W']:
            target = col+str(dst)
            old = cells[MEL][target][1][1:]
            if col == 'P':
                value = f'IF(AND(BR{r}="Condição",F{r}="",L{r}=0),"Controle",{old})'
                value = f'IF(O{dst}="","",{value})'
            else:
                value = f'IF(O{dst}="",0,IF(BR{r}="Condição",1,{old}))'
            put(MEL, target, '='+value)
    return tr


def exporta(tr):
    return [[key, f'=IF(ISBLANK({ref(a1,"CONFIGURAÇÃO")}),"",{ref(a1,"CONFIGURAÇÃO")}&"")',
             ref(a1, 'CONFIGURAÇÃO').replace('$', ''), 'configuração']
            for key, a1, _ in tr['entradas']]
