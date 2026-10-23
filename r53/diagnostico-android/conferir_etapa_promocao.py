"""Classifica uma etapa contra releitura nativa; nunca aplica pedidos.

Antes de aplicar/reverter, capture TODOS os alvos da etapa. Após timeout,
somente 'aplicada' permite pular o lote; 'mista' ou 'divergente' exige parar.
"""
import argparse
import json
from pathlib import Path
from preparar_promocao import cells, read


def classify(stage, document):
    if stage['nome'] == 'grade':
        sh = next(s for s in document['sheets'] if s['properties']['title']=='ANALISE')
        n = sh['properties']['gridProperties']['columnCount']
        if n == 4:return 'aplicada'
        if n != 12:return 'divergente'
        values=cells(document)
        if any(c.get(k) for key,c in values.items() if key[2]>=4
               for k in ('userEnteredValue','note','dataValidation')):return 'divergente'
        # O chamador deve fornecer releitura delimitada E1:L18394 completa,
        # além de conferir nomes/proteções; metadados sozinhos não bastam.
        return 'estrutura_antes_exige_conferencia_excedente'
    live=cells(document)
    states=[]
    for check in stage['precondicoes']:
        key=(check['aba'],check['row'],check['col'])
        if key not in live:return 'incompleta'
        value=live[key].get('userEnteredValue',{})
        if value==check['antes']:states.append('antes')
        elif value==check['depois']:states.append('aplicada')
        else:return 'divergente'
    return states[0] if len(set(states))==1 else 'mista'


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('delta',type=Path);p.add_argument('etapa',type=int)
    p.add_argument('releitura',type=Path);p.add_argument('--alvo',required=True)
    a=p.parse_args();d=read(a.delta);live=read(a.releitura)
    assert live['spreadsheetId']==a.alvo,'Alvo da releitura divergente'
    stage=d['etapas'][a.etapa];state=classify(stage,live)
    print(json.dumps({'etapa':stage['nome'],'estado':state},ensure_ascii=False))
    if state not in ('antes','aplicada'):raise SystemExit(2)
