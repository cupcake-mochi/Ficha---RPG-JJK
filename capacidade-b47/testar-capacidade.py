#!/usr/bin/env python3
"""Auditoria focal de capacidade/contrato no modelo real recém-gerado."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT/'ficha-v01'),str(Path(__file__).resolve().parent)]
import capacidades as cap
from migracao import raw,contract,source
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--base',type=Path,required=True);ap.add_argument('--alvo',type=Path,required=True)
a=ap.parse_args();b=json.loads(a.base.read_text());t=json.loads(a.alvo.read_text())
br,tr=raw(b),raw(t);bc,tc=contract(br['ANALISE']),contract(tr['ANALISE'])
checks=[]
def check(name,ok):checks.append({'teste':name,'ok':bool(ok)});print(('OK ' if ok else 'FALHA ')+name,flush=True)
check('limites independentes aprovados', (cap.FAMILIAS,cap.MELHORIAS,cap.RESTRICOES,cap.PERICIAS,cap.OFICIOS)==(10,30,30,10,10))
expected_retired={k for k in bc if k.startswith(('custom.treino.','aviso.custom.treino.')) or
                 any((m:=re.fullmatch(r'(?:custom|aviso.custom)\.'+group+r'\.(\d+)(?:\..*)?',k)) and int(m[1])>lim for group,lim in [('familia',10),('melhoria',30),('restricao',30)])}
expected_new={f'{prefix}custom.{group}.{n}'+('' if prefix else '.'+field)
              for group in ('pericia','oficio') for n in range(1,11)
              for prefix,fields in [('',('tipo','nome','mestre_viu','atributo','efeito')),('aviso.',('',))]
              for field in fields}
check('11712 chaves descontinuadas exatamente; nenhuma retirada incidental',set(bc)-set(tc)==expected_retired and len(expected_retired)==11712)
check('120 chaves novas exatamente; namespaces sem reciclagem',set(tc)-set(bc)==expected_new and len(expected_new)==120)
check('7356 chaves únicas e formato 10',len(tc)==7356 and sum(bool(re.fullmatch(r'A\d+',c)) and c!='A1' for c in tr['ANALISE'])==7356 and tc['formato.versao'][0]=='10')
check('partes semânticas das 7236 chaves retidas preservadas',all(tc[k][2]==bc[k][2] for k in bc.keys()&tc.keys()))
check('25 cartões 3a e Caminho/Trilha intactos',all(tc[k]==v for k,v in bc.items() if re.match(r'custom\.\d+\.',k) or k.startswith(('custom.caminho.','custom.trilha.'))))
check('12 invocações conservam 108 chaves de Família e fontes',all(tc[f'invocacao.{n}.familia.{f}']==bc[f'invocacao.{n}.familia.{f}'] for n in range(1,13) for f in range(1,10)))
check('autonomia e seus limites conservam identidade/fontes',all(tc[k]==v for k,v in bc.items() if re.fullmatch(r'invocacao.\d+.(autonomia|limite_familias|limite_livres)',k)))
check('catálogo unido contém livro + 10 famílias; não multiplica por entidade',next(a for a in t['layout']['abas'] if a['nome']=='DADOS_CRIACAO')['linhas']==20 and len([v for c,v in tr['DADOS_CRIACAO'].items() if re.fullmatch('A[0-9]+',c) and isinstance(v,int)])==10)
check('20 tipos de cadastro fixos: 10 Perícias e 10 Ofícios',sum(tr['CONFIGURAÇÃO'].get(source(v[1])[1])=='Perícia' for k,v in tc.items() if re.fullmatch(r'custom.pericia.\d+.tipo',k))==10 and sum(tr['CONFIGURAÇÃO'].get(source(v[1])[1])=='Ofício' for k,v in tc.items() if re.fullmatch(r'custom.oficio.\d+.tipo',k))==10)
# No executable reference may point past the new native grid. Ignore strings
# in formulas through Tokenizer; text is not a cell reference.
from openpyxl.formula import Tokenizer
limits={a['nome']:a['linhas'] for a in t['layout']['abas']}
bad=[]
for a in t['layout']['abas']:
    formulas=[v[1] for v in a['celulas'] if isinstance(v[1],str) and v[1].startswith('=')]
    formulas+=['='+m['formula'].lstrip('=') for m in a.get('menus',[])]
    for f in formulas:
        for token in Tokenizer(f).items:
            if token.type!='OPERAND' or token.subtype!='RANGE':continue
            owner,address=token.value.rsplit('!',1) if '!' in token.value else (a['nome'],token.value)
            owner=owner.strip("'")
            if owner not in limits:continue
            rows=[int(n) for n in re.findall(r'\$?[A-Z]+\$?(\d+)',address)]
            if rows and max(rows)>limits[owner]:bad.append((a['nome'],token.value))
check('fórmulas e menus não referenciam linhas retiradas',not bad)
if bad:print(bad[:10])
check('CONFIGURAÇÃO tem 1731 linhas; sem 16928 linhas de reserva',limits['CONFIGURAÇÃO']==1731)
check('painéis de treino do jogador conservam 23+11 posições',all(k in tc for group,n in [('pericia',23),('oficio',11)] for k in [f'personagem.{group}_custom.{n}.nome']))
print(json.dumps({'resultado':'OK' if all(c['ok'] for c in checks) else 'FALHA','checagens':checks},ensure_ascii=False))
raise SystemExit(not all(c['ok'] for c in checks))
