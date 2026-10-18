"""Confere preservação da migração usando snapshots nativos, sem rede."""
import json,sys
from pathlib import Path
from importlib.machinery import SourceFileLoader
p=SourceFileLoader('planejador',str(Path(__file__).with_name('aplicar-extensoes-custom.py'))).load_module()

def run(folder,oficial=False):
    folder=Path(folder)
    before=p.cells(p.load(folder/('extensoes-oficial-antes-1.json' if oficial else 'extensoes-antes.json')))
    after=p.cells(p.load(folder/('extensoes-oficial-prova-1.json' if oficial else 'extensoes-prova-copia-1.json')))
    allcells=p.cells(p.load(folder/('extensoes-oficial-prova-0.json' if oficial else 'extensoes-prova-copia-0.json')))
    diffs=[];preserved=0
    headers={'FICHA':{91,102},'FICHA AMALDIÇOADA':{38},'INVOCAÇÕES':{51+198*i for i in range(6)}}
    for (name,c),cell in before.items():
        if name not in ('FICHA','FICHA AMALDIÇOADA','INVOCAÇÕES','ANALISE'):continue
        if name=='ANALISE' and not c.startswith(('A','B')):continue
        if p.coordinate_to_tuple(c)[0] in headers.get(name,set()):continue
        dest=p.e.coord(name,c)
        old=cell.get('effectiveValue',{});new=after.get((name,dest),{}).get('effectiveValue',{})
        if old!=new:diffs.append(dict(aba=name,de=c,para=dest,antes=old,depois=new))
        preserved+=1
    errors=[dict(aba=n,celula=c,erro=v['effectiveValue']['errorValue']) for (n,c),v in allcells.items() if v.get('effectiveValue',{}).get('errorValue')]
    # Whole new bodies are blank until there is a valid definition. Check names
    # and state cells, excluding editable false checkboxes.
    targets=p.load(folder/'extensoes-modelo.json');blank=[]
    for a in targets['layout']['abas']:
        if a['nome'] not in p.e.INSERCOES:continue
        for panel in targets['auditoria']['paineis']:
            if panel['aba']!=a['nome']:continue
            for (name,c),cell in after.items():
                r,_=p.coordinate_to_tuple(c)
                if name==a['nome'] and panel['primeira']<=r<=panel['ultima'] and cell.get('effectiveValue',{}).get('stringValue'):
                    blank.append((name,c))
    keys=[v.get('effectiveValue',{}).get('stringValue') for (n,c),v in after.items() if n=='ANALISE' and c.startswith('A')]
    keys=[k for k in keys if k and k not in ('chave','versão','versao')]
    report={'celulas_preservadas_conferidas':preserved,'diferencas':diffs,'erros_22_abas':errors,'textos_indevidos_em_paineis_vazios':blank,'resultado':'OK' if not(diffs or errors or blank) else 'FALHOU'}
    (folder/('extensoes-comparacao-oficial.json' if oficial else 'extensoes-comparacao-copia.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False));assert report['resultado']=='OK'

if __name__=='__main__':run(sys.argv[1], '--oficial' in sys.argv)
