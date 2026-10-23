"""Contraprova local e preparo de QA nativo. Não modifica fonte de produção.

Gera somente pedidos offline em nuvem-b47/saidas/diagnostico-mobile-20261023/qa.
O envio é separado e deve usar a planilha sintética, nunca a ficha oficial.
"""
import hashlib
import json
import random
import sys
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'r53'),str(ROOT/'r53/testes'),str(ROOT/'ficha')]
import modelo as M
import verificar as V
import gerar_nativo as G
import emitir_gs as E
from formulas import X

OUT = ROOT/'nuvem-b47/saidas/diagnostico-mobile-20261023/qa'
REPLACEMENTS = [
    ("valor=IF(AND(OR(limdano,semdano),curto,prolongado.eq(False)),valor.cat(' · +1 rodada no prazo curto; conserva o término e as saídas'),valor)",
     "valor=valor.cat(IF(AND(OR(limdano,semdano),curto,prolongado.eq(False)),' · +1 rodada no prazo curto; conserva o término e as saídas',''))"),
    ("valor=IF(AND(semdano,LOOK(rot,'controle_compat').gt(0),LOOK(rot,'tr').gt(0)),valor.cat(' · TR próprio e saídas: CD ').cat(ref('cd_controle')),valor)",
     "valor=valor.cat(IF(AND(semdano,LOOK(rot,'controle_compat').gt(0),LOOK(rot,'tr').gt(0)),x(' · TR próprio e saídas: CD ').cat(ref('cd_controle')),''))")]


def candidate():
    source = Path(M.__file__).read_text()
    changed = source
    for old,new in REPLACEMENTS:
        assert changed.count(old)==1
        changed = changed.replace(old,new)
    trial = types.ModuleType('modelo_experimento')
    trial.__file__ = M.__file__
    exec(compile(changed,'<experimento-em-memoria>','exec'),trial.__dict__)
    return trial,source,changed


def refs(e):
    if not isinstance(e,X): return set()
    result = {e.args[0]} if e.op=='ref' else set()
    for a in e.args: result |= refs(a)
    return result


def local(trial):
    V.verificar()
    for livre in [False,True]:
        before,after=M.arvore(livre),trial.arvore(livre)
        assert list(before)==list(after)
        assert [k for k in before if before[k]!=after[k]]==['efeitos']
        assert refs(before['efeitos'])==refs(after['efeitos'])
    corpus=[]
    for c in V.CASOS:
        corpus.append(({**V.BASE,**c['entrada']},dict(catalogo_extra=c.get('catalogo'),familias_custom=c.get('familias_custom'),formas_custom=c.get('formas'))))
    rng=random.Random(531023)
    options=list(M.OPCOES)+['','Desconhecida * ? ~']
    modes=['Comum','Classe 0','Básica','Entidade','Técnica Máxima','Máxima de entidade','Liberação Máxima','Liberação de entidade']
    for i in range(1024):
        e={**V.BASE,'classe':rng.randrange(0,8),'modalidade':modes[i%8],'nivel':rng.choice([1,6,17,21,26,30]),
           'controle':rng.choice(['Sem reforço','Dano limitado à Classe','Sem dano']),
           **{f'm{j}':rng.choice(options) for j in range(1,5)},
           'dano':rng.choice([True,False]),'cura':rng.choice([True,False]),'vt':rng.choice([True,False]),
           'p_dano':rng.randrange(0,25),'p_cura':rng.randrange(0,25),'p_vt':rng.randrange(0,25),
           'cd':rng.randrange(0,40)}
        corpus.append((e,{}))
    coverage=Counter();compared=0
    for e,kw in corpus:
        a,b=M.calcular(e,**kw),trial.calcular(e,**kw)
        assert a==b
        compared+=len(a)
        text=a['efeitos'];p=' · +1 rodada no prazo curto;' in text;t=' · TR próprio e saídas: CD ' in text
        coverage['ambos' if p and t else 'prazo' if p else 'tr' if t else 'nenhum']+=1
    return dict(casos_existentes=len(V.CASOS),casos_adicionais=1024,campos_comparados=compared,
                resultados_iguais=True,cobertura_sufixos=dict(coverage),campos_alterados=['efeitos'],
                dependencias_efeitos=sorted(refs(M.ARVORE['efeitos'])),dependencias_iguais=True)


def prepare(trial):
    requests = G.gerar()
    catalog=requests[0]['updateCells']['rows']
    rows=requests[1]['updateCells']['rows']
    fields=M.INPUTS+list(M.ARVORE)
    cols={k:G.col(i+1) for i,k in enumerate(fields)}
    newcol=G.col(len(fields)+4);eqcol=G.col(len(fields)+5)
    for i,row in enumerate(rows):
        if i==0:
            row['values'] += [G.cel('efeitos fatorados'),G.cel('efeitos idênticos')]
            continue
        # Gerar somente efeitos com as MESMAS referências do emissor existente.
        # A fórmula não usa famílias/formas; confirmar igualdade com a emissão
        # original antes de substituir a árvore.
        rownum=i+1
        f=M.formulas(rownum,cols,f"'{G.CAT_ABA}'!$A$2:${G.col(len(M.LOOKUP_FIELDS))}${len(catalog)}",separator=';',saidas={'efeitos'})['efeitos']
        assert f==row['values'][fields.index('efeitos')]['userEnteredValue']['formulaValue']
        new=trial.formulas(rownum,cols,f"'{G.CAT_ABA}'!$A$2:${G.col(len(M.LOOKUP_FIELDS))}${len(catalog)}",separator=';',saidas={'efeitos'})['efeitos']
        row['values'] += [G.cel(new),G.cel(f'=EXACT({cols["efeitos"]}{rownum};{newcol}{rownum})')]
    data=[]
    for sheetid,rr in [(G.CAT_ID,catalog),(53018002,rows)]:
        vals=[];cells={}
        for r,row in enumerate(rr,1):
            for c,cell in enumerate(row['values'],1):
                cells[r,c]=cell;vals.append([r,c,next(iter(cell.get('userEnteredValue',{}).values()),''),0])
        blocks=E._blocos_para_baixo(vals)
        removed={(r,c) for ra,ca,rb,cb in blocks for r in range(ra+1,rb+1) for c in range(ca,cb+1)}
        kept={(r,c):v for r,c,v,_ in vals if (r,c) not in removed};rest=dict(kept)
        for ra,ca,rb,cb in blocks:
            for r in range(ra+1,rb+1):
                for c in range(ca,cb+1):rest[r,c]=E.desloca(rest[ra,c],r-ra)
        assert rest=={(r,c):v for r,c,v,_ in vals}
        for start in range(0,len(rr),3):
            data.append({'updateCells':{'start':{'sheetId':sheetid,'rowIndex':start,'columnIndex':0},
                'rows':[{'values':[cells[r,c] if (r,c) in kept else {} for c in range(1,len(row['values'])+1)]} for r,row in enumerate(rr[start:start+3],start+1)],'fields':'userEnteredValue'}})
        for ra,ca,rb,cb in blocks:
            data.append({'copyPaste':{'source':dict(sheetId=sheetid,startRowIndex=ra-1,endRowIndex=ra,startColumnIndex=ca-1,endColumnIndex=cb),
                'destination':dict(sheetId=sheetid,startRowIndex=ra,endRowIndex=rb,startColumnIndex=ca-1,endColumnIndex=cb),'pasteType':'PASTE_FORMULA'}})
    batches=[];batch=[];size=0
    for req in data:
        n=len(json.dumps(req,ensure_ascii=False))
        if batch and size+n>160000:batches.append(batch);batch=[];size=0
        batch.append(req);size+=n
    if batch:batches.append(batch)
    for i,batch in enumerate(batches):
        (OUT/f'lote-{i:02}.json').write_text(json.dumps(batch,ensure_ascii=False,separators=(',',':')))
    meta=dict(casos=len(V.CASOS),linhas=len(rows),colunas=len(rows[0]['values']),catalogo_linhas=len(catalog),catalogo_colunas=max(len(r['values']) for r in catalog),
        coluna_caso=G.col(len(fields)+1),coluna_teste=G.col(len(fields)+3),coluna_fatorada=newcol,coluna_equivalencia=eqcol,
        lotes=len(batches),pedidos=len(data),formulas_originais_completas=True,compactacao_reexpandida_exata=True)
    (OUT/'manifesto.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    return meta


if __name__=='__main__':
    OUT.mkdir(exist_ok=True,parents=True)
    trial,source,changed=candidate()
    result=local(trial)
    result.update(fonte_sha256=hashlib.sha256(source.encode()).hexdigest(),prototipo_sha256=hashlib.sha256(changed.encode()).hexdigest(),
                  escopo='Experimento em memória; sem mudança de fonte de produção',nativo_preparado=prepare(trial))
    Path(__file__).with_name('EQUIVALENCIA-LOCAL-2026-10-23.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
