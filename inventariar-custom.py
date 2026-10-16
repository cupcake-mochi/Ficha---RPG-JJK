#!/usr/bin/env python3
"""Inventário de leitura: menus, listas e capacidade para o custom da B47.

Lê XML do artefato interno e as geometrias do gerador. Não executa monta.py,
não altera a ficha, não importa XLSX e não constrói cartões de produção.
"""
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as E
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
sys.path[:0] = [str(ROOT/'ficha-v01'), str(ROOT/'ficha')]
from openpyxl.utils.cell import range_boundaries, get_column_letter
import ficha_pessoal
import emitir_gs


def coords(area):
    x1, y1, x2, y2 = range_boundaries(area)
    return [f'{get_column_letter(x)}{y}' for y in range(y1, y2+1) for x in range(x1, x2+1)]


def value(c):
    f = c.find('s:f', NS)
    if f is not None:
        return '='+(f.text or '')
    if c.attrib.get('t') == 'inlineStr':
        return ''.join(c.itertext())
    return c.findtext('s:v', '', NS)


def classify(sheet, header, formula):
    if formula.startswith('"'):
        return 'controle', 'opções fixas de operação/atributo/estado'
    if sheet == 'CONFIGURAÇÃO':
        return 'controle', 'destinos e fontes dos bônus'
    h = header.lower()
    if any(x in h for x in ['marcante', 'menores', 'mão principal', 'mão secundária', 'vestindo', 'equipável', 'origens']):
        return '3a', header
    if any(x in h for x in ['caminho', 'trilha', 'perícia', 'ofício']):
        # Talento da trilha da entidade pertence à invocação, não à Trilha do personagem.
        return ('3c' if 'talento' in h else '3b'), header
    if any(x in h for x in ['forma', 'melhoria', 'restrição', 'passiva', 'aptidão', 'tipo de entidade', 'família', 'tipo de dano', 'talento']):
        if h.startswith(('estado de família', 'classe passiva', 'forma do pacto')):
            return 'controle', header
        return '3c', header
    if h == 'tipo de missão':
        return 'mesa (escopo a confirmar)', header
    return 'controle', header or 'revisar fonte sem cabeçalho'


def budget(n):
    # Envelope sintético, não é desenho aprovado nem cartão implementado.
    # 26 linhas x 6 colunas por cartão; 17 campos; notas e fórmulas curtas.
    vals, notes, merges, borders = [], [], [], []
    for k in range(n):
        r = 10+k*29
        vals += [[r+y, 10+x, '', 0] for y in range(26) for x in range(6)]
        for j in range(17):
            notes.append([f'J{r+j}', 'Campo do molde. Preencha conforme a regra criada com o mestre.'])
            merges.append([r+j, 10, r+j, 12])
            vals.append([r+j, 10, f'=IF($K${r}="Arma","CAMPO {j+1}","")', 1])
        borders.append(['bottom', 'SOLID', '#B377BB', [f'J{r}:O{r+19}']])
    payload={'vals': vals, 'notas': notes, 'merges': merges, 'bordas': borders}
    encoded=emitir_gs._sem_linha_gigante(payload).encode()
    return {'cartoes':n, 'linhas_com_respiro':n*29, 'celulas_de_grade':n*26*6,
            'campos_de_entrada_modelados':n*17, 'bytes_envelope_sintetico':len(encoded),
            'nao_inclui':'listas unificadas, fórmulas específicas dos moldes, ANALISE 5, texto escrito pelos jogadores e ajustes de layout'}


def inventory_3c(menus, capacity_3a):
    """Separa escolhas físicas de dependências de catálogo; não define capacidade.

    Uma condição usa um lugar de Melhoria. As Famílias de peças da entidade
    precisam estar entre as nove escolhas dela, portanto não se somam de novo
    à capacidade de um catálogo que cubra uma ficha válida inteira.
    """
    names = {'menu de aptidão': 'Aptidão / Bênção', 'menu de passiva': 'Talento do personagem',
             'família': 'Família', 'menu de talento da trilha': 'Talento de entidade',
             'talento': 'Talento de entidade', 'tipo de dano': 'Tipo de dano',
             'tipo de entidade': 'Tipo de entidade'}
    slots, unmatched = {}, []
    for m in menus:
        if m['etapa'] != '3c':
            continue
        h = m['grupo']
        typ = names.get(h)
        for prefix, label in [('menu de forma', 'Forma'), ('menu de melhoria', 'Melhoria'),
                              ('menu de restrição', 'Restrição')]:
            if h.startswith(prefix):
                typ = label
        if typ is None:
            unmatched.append({'aba': m['aba'], 'grupo': h, 'caixas': m['caixas']})
            continue
        slots.setdefault(typ, {}).setdefault(m['aba'], set()).update(m['caixas'])
    counts = {typ: {sheet: len(cells) for sheet, cells in sheets.items()} for typ, sheets in slots.items()}
    totals = {typ: sum(sheets.values()) for typ, sheets in counts.items()}
    # Referências de Forma e Melhoria por personagem; cada uma pode apontar
    # para uma Família própria. Restrições não referenciam Famílias.
    character = sum(counts.get(t, {}).get('FICHA AMALDIÇOADA', 0) for t in ('Forma', 'Melhoria'))
    entity = totals.get('Família', 0)
    all_parts = totals.get('Forma', 0) + totals.get('Melhoria', 0)
    family_bound = character + entity
    # Dano da técnica é livre hoje; as oito armas guardadas podem usar tipos
    # diferentes, e as mãos apenas referenciam esses mesmos equipamentos.
    import ficha_amaldicoada
    free_damage = ficha_amaldicoada.geometria()['tipo_dano']
    damage_bound = totals.get('Tipo de dano', 0) + 1 + capacity_3a['equipaveis_guardados']
    candidate = dict(totals)
    candidate['Família'], candidate['Tipo de dano'] = family_bound, damage_bound
    return {'escolhas_com_menu_por_aba': counts, 'totais_escolhas_com_menu': totals,
            'total_escolhas_com_menu': sum(totals.values()), 'nao_classificados': unmatched,
            'familias': {'referencias_personagem': character, 'escolhas_entidades': entity,
                         'limite_superior_ficha_valida': family_bound,
                         'limite_sem_exigir_familias_abertas_nas_entidades': all_parts+entity,
                         'premissa': 'Cada peça da entidade usa uma de suas nove Famílias abertas; os catálogos podem reutilizar uma Família.'},
            'danos': {'campo_livre_tecnica': 'FICHA AMALDIÇOADA!'+free_damage,
                      'equipamentos_distintos_guardados': capacity_3a['equipaveis_guardados'],
                      'limite_superior_em_uso': damage_bound},
            'limites_superiores_registros_em_uso': candidate,
            'soma_limites_superiores_em_uso': sum(candidate.values()),
            'estado': 'dimensionamento conservador, sem aprovação de capacidade ou custo; não gerar cartões automaticamente',
            'pendente': ['revisar herança de bases e dependências mecânicas',
                         'desenhar armazenamento e medir .gs reais',
                         'medir construir() nativo na descartável antes do fechamento']}


def inventory(path):
    sheets={}
    with ZipFile(path) as z:
        wb=E.fromstring(z.read('xl/workbook.xml'))
        relns={'r':'http://schemas.openxmlformats.org/package/2006/relationships'}
        rels={r.attrib['Id']:r.attrib['Target'] for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sh in wb.find('s:sheets',NS):
            target=rels[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            xml=E.fromstring(z.read(target))
            sheets[sh.attrib['name']]={'cells':{c.attrib['r']:value(c) for c in xml.findall('s:sheetData/s:row/s:c',NS)},
                                      'dv':xml.findall('s:dataValidations/s:dataValidation',NS)}
    menus=[]
    for name, sh in sheets.items():
        for dv in sh['dv']:
            formula=dv.findtext('s:formula1','',NS)
            places=sorted({c for a in dv.attrib['sqref'].split() for c in coords(a)})
            src=re.fullmatch(r"(?:'([^']+)'|([^!]+))!\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)",formula)
            header, source, samples='',None,[]
            if src:
                sn=src[1] or src[2];col=src[3];row=int(src[4]);cells=sheets[sn]['cells']
                header=cells.get(f'{col}{row-1}','')
                source={'aba':sn,'faixa':f'{col}{row}:{src[5]}{src[6]}','cabecalho':header}
                samples=[cells.get(c,'') for c in coords(source['faixa'])][:3]
            phase, kind=classify(name,header,formula)
            menus.append({'aba':name,'faixas':dv.attrib['sqref'].split(),'quantidade_de_caixas':len(places),
                          'caixas':places,'formula':formula,'fonte':source,'amostra_da_fonte':samples,
                          'etapa':phase,'grupo':kind,'tipo_validacao':dv.attrib['type']})
    lists=[]
    for c in 'ABCDEFGHIJKL':
        vals=[(coord,v) for coord,v in sheets['DADOS']['cells'].items()
              if re.fullmatch(c+r'\d+',coord) and int(re.search(r'\d+',coord)[0])>=4 and v!='']
        lists.append({'coluna':c,'titulo':sheets['DADOS']['cells'].get(c+'3',''),'entradas':len(vals),
                      'menus_diretos':sum(m['formula'].startswith('DADOS!$'+c+'$') for m in menus)})
    g=ficha_pessoal.geometria(ficha_pessoal.regras())
    eq=g['equip_fim']-g['equip_ini']+1;items=2*(g['itens_fim']-g['itens_ini']+1)
    capacity={'origem_base':1,'capacidade_marcante':1,'capacidades_menores':2,
              'equipaveis_guardados':eq,'uniforme_vestido':1,'itens_guardados':items}
    formula_cells=sum(isinstance(v,str) and v.startswith('=') for sh in sheets.values() for v in sh['cells'].values())
    return {'artefato':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'resumo':{'abas':len(sheets),'validacoes':len(menus),'caixas_com_menu':sum(m['quantidade_de_caixas'] for m in menus),
                      'fontes_distintas':len({m['formula'] for m in menus}),'formulas_no_artefato':formula_cells,
                      'caixas_por_etapa':dict(Counter({k:sum(m['quantidade_de_caixas'] for m in menus if m['etapa']==k) for k in {m['etapa'] for m in menus}}))},
            'menus':menus,'listas_originais_DADOS':lists,'capacidade_3a':capacity,
            'inventario_3c': inventory_3c(menus, capacity),
            'total_3a_proposto':sum(capacity.values()),
            'geometria':{k:g[k] for k in ['equip_ini','equip_fim','itens_ini','itens_fim']},
            'medidas_sinteticas':[budget(n) for n in [12,sum(capacity.values()),32]],
            'scripts_atuais':{p.name:p.stat().st_size for p in sorted((ROOT/'apps-script').glob('*.gs'))},
            'limites':['Quantidade de caixas é a união de células em cada validação, não quantidade de conteúdos únicos.',
                       'Uma mesma lista pode alimentar várias caixas; controle de classe, estado e atributo não vira tipo custom automaticamente.',
                       '12 listas originais são registradas mesmo quando o menu usa uma lista derivada ou não existe menu direto.',
                       'Custos sintéticos são apenas envelope de transporte; não são medição do construir() no Google.',
                       'Tempo real de montagem e tamanho final de ANALISE 5 só podem ser medidos após aprovar e implementar os moldes.']}


def markdown(d):
    s=['# Inventário custom · B47', '', 'Levantamento para decisão; nenhuma fórmula ou aba foi alterada.', '',
       '## Cobertura', '', json.dumps(d['resumo'],ensure_ascii=False), '',
       '| Aba | Caixas com menu | Validações agrupadas |','|---|---:|---:|']
    for aba in dict.fromkeys(m['aba'] for m in d['menus']):
        ms=[m for m in d['menus'] if m['aba']==aba]
        s.append(f'| {aba} | {sum(m["quantidade_de_caixas"] for m in ms)} | {len(ms)} |')
    s += ['', '## Fontes dos menus', '', '| Aba | Lista ou opções | Caixas | Etapa |', '|---|---|---:|---|']
    for m in d['menus']:
        label=(m['fonte']['cabecalho']+' · '+m['formula']) if m['fonte'] else m['formula']
        s.append(f'| {m["aba"]} | {label} | {m["quantidade_de_caixas"]} | {m["etapa"]} |')
    s += ['', '## Listas originais da DADOS', '', '| Lista | Coluna | Entradas | Menus diretos |','|---|---|---:|---:|']
    for x in d['listas_originais_DADOS']:s.append(f'| {x["titulo"]} | {x["coluna"]} | {x["entradas"]} | {x["menus_diretos"]} |')
    s += ['', '## Capacidade mínima proposta para a parte 3a', '', '| Conteúdo distinto em uso | Lugares |','|---|---:|']
    for k,n in d['capacidade_3a'].items():s.append(f'| {k} | {n} |')
    s += [f'| **Total proposto** | **{d["total_3a_proposto"]}** |','',
          'A conta propõe Origem-base e capacidades como registros separados. Se o cartão de Origem guardar todas as capacidades dentro dele, a contagem muda. Não é uma decisão tomada.',
          'As duas mãos reutilizam os oito equipáveis e não somam dois cartões. Ferramenta amaldiçoada ocupa um dos mesmos lugares, não oito lugares adicionais. Quantidade empilhada do mesmo item reutiliza um cadastro.',
          'Há seis equipáveis com menu + duas linhas totalmente livres. Itens comuns têm doze campos livres, sem catálogo/menu hoje. Para completar a automação proposta, é preciso decidir se as duas linhas livres e os itens passam a aceitar menu livro + custom, preservando a digitação livre.',
          'A capacidade de 25 cobre substituir simultaneamente todos os lugares atuais da parte 3a. Não cobre guardar um catálogo ilimitado de alternativas. Não é um teto para todas as partes 3a–3c.',
          '', '## Medida de transporte (estimativa limitada)', '',
          'Envelope sintético com 26 linhas × 6 colunas e 17 campos/notas por cartão, usando o serializador real. Nenhum molde foi construído no gerador ou na cópia nativa.', '',
          '| Cartões | Linhas com respiro | Células de grade | Bytes do envelope |','|---:|---:|---:|---:|']
    for x in d['medidas_sinteticas']:s.append(f'| {x["cartoes"]} | {x["linhas_com_respiro"]} | {x["celulas_de_grade"]} | {x["bytes_envelope_sintetico"]} |')
    s += ['', 'Não somar esses bytes como se fossem o custo final. Faltam os moldes, tabelas e fórmulas de integração e a ANALISE 5. O texto preenchido pelo jogador não fica embutido no .gs da ficha vazia. O tempo local de serialização não representa o tempo do Google.', '',
          '## Limites', '']+['- '+x for x in d['limites']]
    return '\n'.join(s)+'\n\nDecisões e protótipo: [DECISOES-E-INTEGRACAO.md](DECISOES-E-INTEGRACAO.md).\n'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--arquivo',type=Path,default=ROOT/'ficha-v01/ficha-projeto-m-0.1.xlsx')
    p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();a.saida.mkdir(parents=True,exist_ok=True)
    d=inventory(a.arquivo)
    (a.saida/'inventario-custom.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    (a.saida/'INVENTARIO-CUSTOM.md').write_text(markdown(d))
    print(json.dumps({'resumo':d['resumo'],'capacidade_3a':d['capacidade_3a'],'medidas_sinteticas':d['medidas_sinteticas']},ensure_ascii=False,indent=2))
