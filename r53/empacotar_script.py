"""Pacote fechado para instalar a geração via editor em poucos arquivos.

Conserva as fontes GS legíveis como origem. O pacote contém somente essas
fontes, comprimidas; não busca código na rede nem concede permissões novas.
Entradas públicas delegam ao módulo isolado, que mantém os seus globais.
"""
import base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'r53/saidas/pacote-script'

def gerar():
 OUT.mkdir(exist_ok=True,parents=True)
 folder=ROOT/'apps-script';names=['Ficha.gs']+sorted(p.name for p in folder.glob('*.gs') if p.name not in ['Ficha.gs','Codigo.gs','Habilidades.gs','Salarios.gs','PaletaAndroid.gs'])+['Habilidades.gs','Codigo.gs']
 sources=[(folder/n).read_text() for n in names];source='\n'.join(sources)
 variables=sorted(set(re.findall(r'^var\s+([A-Za-z_$][\w$]*)\s*=',source,re.M)))
 functions=sorted(set(re.findall(r'^function\s+([A-Za-z_$][\w$]*)\s*\(',source,re.M)))
 public=[n for n in functions if not n.endswith('_')]
 # O carregador original consulta os globais do projeto. Aqui eles são os
 # locais do módulo, relidos a cada chamada (as declarações var são içadas).
 source+='\nfunction globais_(){return {'+','.join(json.dumps(n)+':'+n for n in variables)+'};}\n'
 source+='\nreturn {'+','.join(json.dumps(n)+':'+n for n in public)+',__estado:function(){return {abas:ABAS,sobras:SOBRAS_,geracao:GERACAO_,editor:R53_EDITOR_};}};'
 raw=source.encode();digest=hashlib.sha256(raw).hexdigest();b64=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
 step=850_000;parts=[b64[i:i+step] for i in range(0,len(b64),step)]
 slots=['Ficha.gs','Invocacoes.gs','Analise.gs','Configuracao.gs','Origens.gs']
 if len(parts)>len(slots):raise ValueError('Pacote excede os cinco arquivos de dados reservados')
 for i,(name,part) in enumerate(zip(slots,parts)):(OUT/name).write_text('// PACOTE R53 · fonte e hashes em r53/empacotar_script.py\nvar R53_CODIGO_'+str(i)+'_ = '+json.dumps(part)+';\n')
 # Todos os três arquivos substituídos precisam deixar de declarar as abas antigas.
 for name in slots[len(parts):]:(OUT/name).write_text('// Parte de dados anterior incorporada ao pacote R53.\n')
 (OUT/'EditorR53.gs').write_text((folder/'EditorR53.gs').read_text())
 # Módulo leve: edições de missão/data não precisam descompactar os catálogos.
 if (folder/'Salarios.gs').exists():(OUT/'Salarios.gs').write_text((folder/'Salarios.gs').read_text())
 if (folder/'PaletaAndroid.gs').exists():(OUT/'PaletaAndroid.gs').write_text((folder/'PaletaAndroid.gs').read_text())
 bootstrap='''/** @OnlyCurrentDoc */
// PACOTE R53 · entradas públicas; sem rede, sem gatilhos instaláveis novos.
var R53_MODULO_;
function r53Documento_(){return SpreadsheetApp.getActive();}
function r53Modulo_() {
 if (R53_MODULO_) return R53_MODULO_;
 var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode([PARTES].join('')), 'application/gzip')).getDataAsString('UTF-8');
 var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8).map(function(b){return ('0'+((b+256)%256).toString(16)).slice(-2);}).join('');
 if(hash!=='HASH')throw new Error('Pacote R53 incompleto: conteúdo divergente.');
 R53_MODULO_=(new Function(code))();
 if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');
 return R53_MODULO_;
}
function verificarPacoteR53() {
 var s=r53Modulo_().__estado();console.log(JSON.stringify({geracao:s.geracao,abas:s.abas.length,cartoes:s.editor.contextos.length,sobras:s.sobras}));
}
'''.replace('PARTES',','.join('R53_CODIGO_'+str(i)+'_' for i in range(len(parts)))).replace('HASH',digest)
 # Cliques comuns não precisam carregar as tabelas inteiras. O comportamento
 # original só abre fichas de invocação ou continua uma troca de paleta pendente.
 # O pacote deve ser reproduzível em um clone limpo, sem o modelo intermediário
 # ignorado. As mesmas âncoras já fazem parte da fonte GS versionada.
 inv_source=(folder/'Invocacoes.gs').read_text()
 start=re.search(r'^var\s+ABAS_DA_INVOCACAO\s*=\s*',inv_source,re.M)
 if not start:raise ValueError('Fonte de INVOCAÇÕES ausente ou inválida')
 inv_tabs,_=json.JSONDecoder().raw_decode(inv_source[start.end():])
 inv=next(a for a in inv_tabs if a['nome']=='INVOCAÇÕES')
 bootstrap+='var R53_NAVEGACAO_ = '+json.dumps({'aba':inv['nome'],'alvos':[v[0] for v in inv.get('abrir',[])]},ensure_ascii=False)+';\n'
 bootstrap+='''function onSelectionChange(e) {
 if(!e || !e.range)return;
 e.r53Inicio_=Date.now();
 var pending=true;
 try {pending=!!PropertiesService.getDocumentProperties().getProperty('paleta_pendente');}catch(err){}
 var address=e.range.getA1Notation().split(':')[0];
 var opening=R53_NAVEGACAO_.alvos.indexOf(address)>=0 && e.range.getSheet().getName()===R53_NAVEGACAO_.aba;
 if(opening)return r53Modulo_().onSelectionChange(e);
 if(pending && typeof r53PaletaLeve_==='function')r53PaletaLeve_().continuar(e);
 else if(pending)return r53Modulo_().onSelectionChange(e);
}
'''
 for n in public:
  if n=='onEdit':
   bootstrap+='function onEdit(e){if(e)e.r53Inicio_=Date.now();if(typeof salarioIntegrarMissao_==="function"&&salarioIntegrarMissao_(e,function(ev){return r53Modulo_().onEdit(ev);}))return;if(typeof salarioEditar_==="function" && salarioEditar_(e))return;if(e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27")return typeof r53PaletaLeve_==="function" ? r53PaletaLeve_().trocar(e) : r53Modulo_().onEdit(e);if(typeof r53Editar_==="function" && r53Editar_(e))return;return r53Modulo_().onEdit(e); }\n'
  elif n=='onOpen':
   bootstrap+='function onOpen(e){e=e||{};e.r53Inicio_=Date.now();if(typeof r53PaletaLeve_!=="function")return r53Modulo_().onOpen(e);if(typeof salarioAbrir_==="function")salarioAbrir_();if(typeof r53Menu_==="function")r53Menu_();if(PropertiesService.getDocumentProperties().getProperty("paleta_pendente"))r53PaletaLeve_().continuar(e);}\n'
  elif n!='onSelectionChange':bootstrap+='function '+n+'(){return r53Modulo_()['+json.dumps(n)+'].apply(this,arguments);}\n'
 (OUT/'Codigo.gs').write_text(bootstrap)
 (OUT/'fonte-modulo.js').write_text(source)
 arquivos={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.glob('*.gs')}
 # Arquivos desta geração que existirem separadamente no projeto antigo
 # duplicariam a inicialização. Guardar o conteúdo antes de trocar por estes
 # marcadores; não tocar em arquivos externos desconhecidos do projeto.
 legados=[n for n in names if n not in arquivos]
 destino_legado=OUT/'legado';destino_legado.mkdir(exist_ok=True)
 for name in legados:(destino_legado/name).write_text('// Conteúdo incluído no pacote R53; fonte legível preservada no repositório.\n')
 manifest=dict(fonte_sha256=digest,geracao_arquivos=names,entradas_publicas=public,partes=len(parts),bytes_fonte=len(raw),bytes_base64=len(b64),arquivos=arquivos,arquivos_legados_desativar=legados)
 (OUT/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in manifest.items() if k not in ['geracao_arquivos','entradas_publicas']},ensure_ascii=False))
if __name__=='__main__':gerar()
