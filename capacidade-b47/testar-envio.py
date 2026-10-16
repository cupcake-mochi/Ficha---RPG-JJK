#!/usr/bin/env python3
"""Integração offline da geração atual com API de pacote; snapshot remoto sintético v9."""
import importlib.util,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('apps',ROOT/'infra-b47/apps_script.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
SID='PROJETO_SINTETICO_B47';REMOVE=['PecasAnalise2','PecasAnalise3','PecasAnalise4'];checks=[]
def check(name,ok):checks.append(bool(ok));print(('OK ' if ok else 'FALHA ')+name,flush=True)
def rejects(name,fn,text):
 try:fn();check(name,False)
 except ValueError as e:check(name,text in str(e))
with tempfile.TemporaryDirectory(prefix='b47-envio-') as temp:
 temp=Path(temp);src=temp/'fontes';shutil.copytree(ROOT/'apps-script',src)
 names=subprocess.check_output(['git','ls-tree','-r','--name-only','4187df3','--','apps-script'],cwd=ROOT,text=True).splitlines()
 old=[{'name':Path(p).stem,'type':'SERVER_JS','source':subprocess.check_output(['git','show','4187df3:'+p],cwd=ROOT).decode()} for p in names if p.endswith('.gs')]
 old += [{'name':'appsscript','type':'JSON','source':'{"timeZone":"America/Sao_Paulo"}'},{'name':'Tela','type':'HTML','source':'<p>Preservar</p>'}]
 snapshot=temp/'antes.json';api.gravar(snapshot,{'scriptId':SID,'files':old})
 rejects('remotos antigos exigem remoção explícita',lambda:api.preparar(src,snapshot,SID),'ausentes localmente')
 rejects('remover só uma sobra não descarta as outras',lambda:api.preparar(src,snapshot,SID,REMOVE[:1]),'ausentes localmente')
 payload=api.preparar(src,snapshot,SID,REMOVE)
 check('pacote tem 20 GS e preserva manifesto/HTML',len(payload['files'])==22 and payload['files'][-2:]==old[-2:])
 package=temp/'pacote.json';api.gravar(package,payload);readback=temp/'depois.json';api.gravar(readback,payload)
 check('releitura independente coincide byte a byte',api.conferir(package,readback,SID)['igual'])
 rejects('não permite remover código presente',lambda:api.preparar(src,snapshot,SID,REMOVE+['Codigo']),'só aceita')
 (src/'PecasAnalise3.gs').write_bytes(subprocess.check_output(['git','show','4187df3:apps-script/PecasAnalise3.gs'],cwd=ROOT))
 rejects('sobra local não entra no pacote',lambda:api.preparar(src,snapshot,SID,REMOVE),'geração divergente')
 (src/'PecasAnalise3.gs').unlink()
 original=(src/'Criacao.gs').read_bytes();(src/'Criacao.gs').write_bytes(subprocess.check_output(['git','show','4187df3:apps-script/Criacao.gs'],cwd=ROOT))
 rejects('aba gerada antiga é recusada antes de upload',lambda:api.preparar(src,snapshot,SID,REMOVE),'geração divergente')
 (src/'Criacao.gs').write_bytes(original);(src/'PecasAnalise1.gs').unlink()
 rejects('complemento declarado ausente é recusado',lambda:api.preparar(src,snapshot,SID,REMOVE),'declarados ausentes')
print(json.dumps({'resultado':'OK' if all(checks) else 'FALHA','checagens':len(checks),'tipo':'snapshot sintético; sem rede'},ensure_ascii=False))
raise SystemExit(not all(checks))
