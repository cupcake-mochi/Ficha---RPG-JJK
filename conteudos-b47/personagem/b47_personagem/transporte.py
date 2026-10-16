"""Proposta de transporte para o integrador; só devolve metadados em memória.

Nomes de arquivos/variáveis abaixo pertencem ao patch proposto, ainda não são
namespaces instalados no núcleo. As faixas saem das células efetivamente
geradas; nenhum .gs é produzido por este módulo.
"""
import json
from collections import defaultdict
from openpyxl.utils.cell import coordinate_from_string
from openpyxl.utils import column_index_from_string


def fatiar_colunas(celulas,limite=240_000):
    if type(limite) is not int or limite<1000:
        raise ValueError('Limite de fragmento inválido')
    por=defaultdict(int)
    for cel,v in celulas.items():
        col,row=coordinate_from_string(cel)
        c=column_index_from_string(col)
        por[c]+=len(json.dumps([row,c,v],ensure_ascii=False).encode('utf8'))+4
    result=[];first=None;last=None;size=0
    for c,quantidade in sorted(por.items()):
        if quantidade>limite:raise ValueError('Uma coluna excede o limite; integrar corte por linhas: '+str(c))
        if first is not None and size+quantidade>limite:
            result.append((first,last,size));first=None;size=0
        if first is None:first=c
        last=c;size+=quantidade
    if first is not None:result.append((first,last,size))
    return result


def separadas(tr):
    abas=tr['contrato'].abas
    return {'FormasPersonagem.gs':('ABAS_PERSONAGEM_FORMAS',(abas['forma'],)),
            'AptidoesPersonagem.gs':('ABAS_PERSONAGEM_APTIDOES',(abas['aptidao'],)),
            'TalentosPersonagem.gs':('ABAS_PERSONAGEM_TALENTOS',(abas['talento'],))}


def suplementos(layout,tr):
    aba=next(x for x in layout['abas'] if x['nome']==tr['contrato'].abas['forma'])
    cells={x[0]:x[1] for x in aba['celulas']}
    out={f'PersonagemFormas{i}.gs':(aba['nome'],c1,c2)
         for i,(c1,c2,_) in enumerate(fatiar_colunas(cells),1)}
    out['PersonagemPainel.gs']=('CONFIGURAÇÃO',1,16,tr['inicio'],tr['fim'])
    if 'analise_inicio' in tr:
        out['PersonagemAnalise.gs']=('ANALISE',1,4,tr['analise_inicio'],tr['analise_fim'])
    return out


def complementos(suplementos):
    out={}
    for arq in suplementos:
        if arq.startswith('PersonagemFormas'):
            n=arq[len('PersonagemFormas'):-3]
            out[arq]='VALORES_PERSONAGEM_FORMAS_'+n+'_'
        elif arq=='PersonagemPainel.gs':out[arq]='VALORES_PERSONAGEM_PAINEL_'
        elif arq=='PersonagemAnalise.gs':out[arq]='CONTRATO_PERSONAGEM_'
        else:raise ValueError('Fragmento de outra frente: '+arq)
    return out
