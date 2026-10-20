"""Casos observáveis do prompt; também produzem os casos enviados ao Sheets."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from modelo import calcular,DEFAULTS
CASOS=json.loads(Path(__file__).with_name('casos.json').read_text())
BASE=dict(tr_dano='Físico',tr_controle='Físico',preparada=True,origem_permissao='Caso de conferência do autor R53',permite_dano=True,permite_cura=True,permite_vt=True,
          dest_dano='Inimigo válido',dest_cura='Aliado disposto',dest_vt='Aliado disposto')
def verificar():
    erros=[]
    for caso in CASOS:
        obtido=calcular({**BASE,**caso['entrada']},catalogo_extra=caso.get('catalogo'),familias_custom=caso.get('familias_custom'),formas_custom=caso.get('formas'))
        for k,v in caso['esperado'].items():
            if obtido[k]!=v: erros.append(f"{caso['nome']}: {k}: esperado {v!r}, obtido {obtido[k]!r}; {obtido['avisos']}")
        for k,v in caso.get('contem',{}).items():
            if v not in str(obtido[k]):erros.append(caso['nome']+': trecho esperado ausente em '+k)
        for k,v in caso.get('nao_contem',{}).items():
            if v in str(obtido[k]):erros.append(caso['nome']+': trecho incompatível em '+k)
    if erros: raise AssertionError('\n'.join(erros))
    print(f'{len(CASOS)} casos R53 passaram no avaliador de diagnóstico. Ainda não substitui o teste nativo.')
if __name__=='__main__': verificar()
