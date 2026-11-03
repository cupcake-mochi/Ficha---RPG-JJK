"""Plano offline e reversão dos avisos de funções; não acessa o Google.

Exige modelo da base e snapshot atual A:M e GA da DADOS_R53. A aplicação externa
deve conferir novamente as guardas antes de escrever; o plano não trava a API.
"""
import argparse
import copy
import json
import sys
from pathlib import Path
from openpyxl.utils.cell import get_column_letter
from openpyxl.formula import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'ficha-v01'), str(ROOT/'r53')]
from avisos_cartoes_r53 import formula_avisos_funcoes
from origens_analise import assinatura_formula


def formula_nativa(formula):
    # Estes diagnósticos usam funções escalares, sem literais de matriz.
    # Tokenizar evita trocar vírgulas/decimais dentro de texto ou nomes de aba.
    out=[]
    for t in Tokenizer(formula).items:
        if t.type=='ARRAY':raise ValueError('Diagnóstico com matriz exige revisão regional')
        out.append(';' if t.type=='SEP' and t.value==',' else
                   t.value.replace('.',',') if t.type=='OPERAND' and t.subtype=='NUMBER' else t.value)
    return '='+''.join(out)


def assinatura(formula):
    # O Sheets salva INDEX(B1683:B1683;...) como INDEX(B1683;...).
    # Só a faixa degenerada é equivalente; intervalos reais não são reduzidos.
    out=[]
    for token in assinatura_formula(formula):
        if token[0]=='REF' and ':' in token[2]:
            start,end=token[2].split(':',1)
            if start==end:token=('REF',token[1],start)
        out.append(token)
    return out


def planejar(modelo, snapshot):
    tab = next(a for a in modelo['layout']['abas'] if a['nome']=='DADOS_R53')
    old = {p:v for p,v,*_ in tab['celulas']}
    live = {}; sid = None
    for sheet in snapshot['sheets']:
        if sheet['properties']['title']!='DADOS_R53':
            continue
        actual = sheet['properties']['sheetId']
        if sid is not None and sid!=actual:
            raise ValueError('Abas diferentes no snapshot')
        sid = actual
        for block in sheet.get('data', []):
            for i,row in enumerate(block.get('rowData', [])):
                for j,cell in enumerate(row.get('values', [])):
                    pos = get_column_letter(block.get('startColumn',0)+j+1)+str(block.get('startRow',0)+i+1)
                    if pos in live:raise ValueError('Leitura sobreposta: '+pos)
                    live[pos] = copy.deepcopy(cell.get('userEnteredValue', {}))
    if sid is None:raise ValueError('DADOS_R53 ausente')
    requests=[]; rollback=[]; guards=[]; updated=0
    col=modelo['r53']['colunas']['avisos_funcoes']
    def request(row, value):
        return {'updateCells':{'start':{'sheetId':sid,'rowIndex':row-1,'columnIndex':182},
            'rows':[{'values':[{'userEnteredValue':value}]}],'fields':'userEnteredValue'}}
    if col!='GA':raise ValueError('Esquema de diagnóstico diferente de GA')
    for g in modelo['r53']['contextos']:
        row=g['linha'];key='A'+str(row);pos=col+str(row)
        if live.get(key)!={'stringValue':g['id']}:raise ValueError('ID divergente: '+key)
        # ID e GA="" sozinhos sobreviveriam a outra mudança de layout. Nome,
        # Classe e entradas efetivas precisam continuar apontando para a base.
        layout_guards={}
        for letter in ['B','C','H','I','J','K','L','M']:
            addr=letter+str(row);expected=old[addr];got=live.get(addr,{})
            if isinstance(expected,str) and expected.startswith('='):
                ok='formulaValue' in got and assinatura(got['formulaValue'])==assinatura(expected)
            else:
                kind='boolValue' if isinstance(expected,bool) else 'numberValue' if isinstance(expected,(int,float)) else 'stringValue'
                ok=got=={kind:expected}
            if not ok:raise ValueError('Layout/entrada divergente: '+addr)
            layout_guards[addr]=got
        new=formula_nativa(formula_avisos_funcoes(g));value=live.get(pos,{});formula=value.get('formulaValue')
        if not formula:raise ValueError('Fórmula ausente: '+pos)
        if assinatura(formula)==assinatura(new):updated+=1;continue
        if assinatura(formula)!=assinatura(old[pos]):raise ValueError('Diagnóstico divergente: '+pos)
        guards.append(dict(id=g['id'],linha=row,layout=layout_guards,anterior=value,novo={'formulaValue':new}))
        requests.append(request(row, {'formulaValue':new}));rollback.append(request(row,value))
    return dict(pedidos=requests,reversao=rollback,guardas=guards,ja_atualizadas=updated,
                aviso='Releia guardas imediatamente antes da aplicação; plano offline não trava a API.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--modelo-base',type=Path,required=True);p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();out=planejar(json.loads(a.modelo_base.read_text()),json.loads(a.snapshot.read_text()))
    a.saida.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(pedidos=len(out['pedidos']),ja_atualizadas=out['ja_atualizadas'])))


if __name__=='__main__':main()
