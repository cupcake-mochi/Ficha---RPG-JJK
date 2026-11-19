'use strict';
// Offline; dois arquivos de código e plano preciso, sem construir/continuar.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const p=require('./pratica_cotidiana_plano.json'),runtime=require('../pratica_cotidiana_runtime');
const {formulaLocal}=require('./preparar_pilha_5156');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function editorProposto(){
 const raw=fs.readFileSync(path.join(__dirname,'../../apps-script/EditorR53.gs'),'utf8');
 return require('../editor_lazy').preparar(raw);
}
function atualizarAtalho(src,editor){
 const hashLine=/^var R53_LIVRE_HASHES_=(\[[^\n]+\]);$/m.exec(src);
 const areaLine=/^var R53_LIVRE_=(\{[^\n]+\});$/m.exec(src);
 if(!hashLine||!areaLine)throw Error('Prática: atalho instalado divergente');
 const hashes=JSON.parse(hashLine[1]),areas=JSON.parse(areaLine[1]);
 const cards=JSON.parse(editor.json).contextos.slice(249);
 if(cards.length!==2||cards.some(g=>g.aba!=='FICHA AMALDIÇOADA'))throw Error('Prática: novas áreas do atalho divergentes');
 for(const card of cards)areas[card.aba].push(card.area_editor);
 hashes[1]=editor.hash;
 return src.replace(hashLine[0],'var R53_LIVRE_HASHES_='+JSON.stringify(hashes)+';')
           .replace(areaLine[0],'var R53_LIVRE_='+JSON.stringify(areas)+';');
}
function prepararCodigo(src){
 if(sha(src)!==p.baseCodigoSha256)throw Error('Prática: exige Codigo.gs PR69 ensaiado');
 const anchor='if(r53RestaurarCargaOrigem_(e))return r53ContinuarPaletaPendente_(e);';
 if(src.split(anchor).length!==2)throw Error('Prática: entrada onEdit divergente');
 src=src.replace(anchor,'if(r53PraticaRestaurar_(e))return r53ContinuarPaletaPendente_(e);'+anchor);
 src=atualizarAtalho(src,editorProposto());
 // O módulo antigo conserva seu catálogo; a edição efetiva usa o editor leve atualizado.
 const report='cartoes:s.editor.contextos.length,sobras:s.sobras';
 if(src.split(report).length!==2)throw Error('Prática: verificador divergente');
 return src.replace(report,'cartoes:r53ConfigEditor_().contextos.length,cartoesModulo:s.editor.contextos.length,sobras:s.sobras')+'\n'+runtime.gerar([]);
}
function prepararEditor(src){
 if(sha(src)!==p.baseEditorSha256)throw Error('Prática: editor instalado divergente');
 const novo=editorProposto().code;
 // Nenhuma mudança no runtime ou nos 249 registros existentes é autorizada.
 const z=require('node:zlib'),read=s=>{const m=/Utilities.base64Decode\(("[^"]+")\)/.exec(s);if(!m)throw Error('Editor inválido');return JSON.parse(z.gunzipSync(Buffer.from(JSON.parse(m[1]),'base64')).toString());};
 const a=read(src),b=read(novo);if(b.contextos.length!==251||JSON.stringify(a.contextos)!==JSON.stringify(b.contextos.slice(0,249)))throw Error('Prática: contexto histórico alterado');
 const tail=s=>s.slice(s.indexOf('var R53_EDITOR_=new Proxy'));
 if(tail(src)!==tail(novo))throw Error('Prática: runtime do editor mudou');
 return novo;
}
const norm=v=>typeof v==='string'&&v.startsWith('=')?v.split(/("(?:[^"]|"")*")/).map((x,i)=>i%2?x:x.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g,'$1!')).join(''):v===''?null:v??null;
function planejar(snapshot){
 if(!snapshot||!Array.isArray(snapshot.cells)||!snapshot.locale)throw Error('Snapshot atual obrigatório');
 const requests=[];
 for(const [kind,targets]of [['value',p.cells],['note',p.notes]])for(const t of targets){
  const xs=snapshot.cells.filter(x=>x.aba===t.aba&&x.a1===t.a1);if(xs.length!==1||!Number.isSafeInteger(xs[0].sheetId))throw Error('Leitura ausente/duplicada: '+t.aba+'!'+t.a1);
  const x=xs[0],before=kind==='value'?formulaLocal(t.antes,snapshot.locale):t.antes;
  if(norm(x[kind])!==norm(before))throw Error('Alvo ocupado/divergente: '+t.aba+'!'+t.a1);
  const m=/^([A-Z]+)(\d+)$/.exec(t.a1),col=[...m[1]].reduce((a,v)=>26*a+v.charCodeAt(0)-64,0),out={};
  if(kind==='note')out.note=t.depois;else {const v=formulaLocal(t.depois,snapshot.locale);if(v!==null&&v!==undefined)out.userEnteredValue=typeof v==='string'?(v.startsWith('=')?{formulaValue:v}:{stringValue:v}):typeof v==='boolean'?{boolValue:v}:{numberValue:v};}
  requests.push({updateCells:{start:{sheetId:x.sheetId,rowIndex:+m[2]-1,columnIndex:col-1},rows:[{values:[out]}],fields:kind==='note'?'note':'userEnteredValue'}});
 }
 return {requests};
}
function planejarInstalacao(snapshot,metadata){
 const values=planejar(snapshot),sheets=new Map(metadata.sheets.map(s=>[s.properties.title,s.properties]));
 if(snapshot.locale!==metadata.properties.locale)throw Error('Idioma mudou depois do snapshot');
 if(snapshot.cells.some(x=>sheets.get(x.aba)?.sheetId!==x.sheetId))throw Error('ID de aba diverge do snapshot');
 const grid=(aba,a1)=>{const xs=a1.split(':').map(x=>{const m=/^([A-Z]+)(\d+)$/.exec(x);return[+m[2],[...m[1]].reduce((a,v)=>26*a+v.charCodeAt(0)-64,0)];}),a=xs[0],b=xs.at(-1),s=sheets.get(aba);if(!s)throw Error('Aba ausente');return{sheetId:s.sheetId,startRowIndex:a[0]-1,endRowIndex:b[0],startColumnIndex:a[1]-1,endColumnIndex:b[1]};};
 const requests=[];
 for(const [aba,rows]of Object.entries(p.grids)){const s=sheets.get(aba);if(!s||s.gridProperties.rowCount!==rows.antes)throw Error('Grade anterior divergente: '+aba);requests.push({updateSheetProperties:{properties:{sheetId:s.sheetId,gridProperties:{rowCount:rows.depois}},fields:'gridProperties.rowCount'}});}
 // Também guardamos as células vazias que serão mescladas/formatadas.
 const blank=[...Array.from({length:17},(_,i)=>['FICHA AMALDIÇOADA',328,i+4]),...Array.from({length:9},(_,i)=>['MONTAGENS',9467,i+1])];
 for(const [aba,r,c]of blank){const xs=snapshot.blankCells?.filter(x=>x.aba===aba&&x.r===r&&x.c===c);if(!xs||xs.length!==1||xs[0].value!=null&&xs[0].value!==''||xs[0].note)throw Error('Área vazia ausente/ocupada: '+aba+' '+r+','+c);}
 const am='FICHA AMALDIÇOADA';
 function copy(aba,src,dst,pasteType){requests.push({copyPaste:{source:grid(aba,src),destination:grid(aba,dst),pasteType,pasteOrientation:'NORMAL'}});}
 copy(am,'A561:U561','A562:U569','PASTE_FORMAT');
 copy(am,'D322:T322','D565:T565','PASTE_FORMAT');
 copy(am,'D327:T327','D566:T567','PASTE_FORMAT');copy(am,'D327:T327','D566:T567','PASTE_DATA_VALIDATION');
 copy('MONTAGENS','A1639:I1676','A9467:I9542','PASTE_FORMAT');
 copy('DADOS_R53','A45:GA45','A252:GA253','PASTE_FORMAT');
 copy('ANALISE','A18409:D18409','A18410:D18500','PASTE_FORMAT');
 copy('DADOS_CUSTOM','B133','B134:B136','PASTE_FORMAT');
 // Copy-format implementations differ on merged cells. Normalize only new areas.
 requests.push({unmergeCells:{range:grid(am,'D563:T567')}});
 for(const [aba,shapes]of Object.entries(p.shapes)){
  for(const a1 of shapes.merges)requests.push({mergeCells:{range:grid(aba,a1),mergeType:'MERGE_ALL'}});
  for(const [row,pixels]of shapes.alturas)requests.push({updateDimensionProperties:{range:{sheetId:sheets.get(aba).sheetId,dimension:'ROWS',startIndex:row-1,endIndex:row},properties:{pixelSize:pixels},fields:'pixelSize'}});
 }
 function format(target,source){const f=snapshot.formats?.[source];if(!f)throw Error('Formato do exemplar ausente: '+source);requests.push({repeatCell:{range:grid(am,target),cell:{userEnteredFormat:f},fields:'userEnteredFormat'}});}
 format('D563:T563','D320');format('D564:T564','R327');format('D328:T328','R327');format('Q565','P322');
 // Merge adjacent value updates to keep one atomic request batch small.
 const lines=new Map();for(const q of values.requests){const u=q.updateCells,k=u.fields+':'+u.start.sheetId+':'+u.start.rowIndex;if(!lines.has(k))lines.set(k,[]);lines.get(k).push(u);}
 for(const list of lines.values()){list.sort((a,b)=>a.start.columnIndex-b.start.columnIndex);let current;
  for(const u of list){if(!current||current.start.columnIndex+current.rows[0].values.length!==u.start.columnIndex){current={start:{...u.start},rows:[{values:[]}],fields:u.fields};requests.push({updateCells:current});}current.rows[0].values.push(u.rows[0].values[0]);}
 }
 if(snapshot.mapParts){
  const before=JSON.parse(snapshot.mapParts.join('')),after=require('./pratica_aparencia').aplicar(before),text=JSON.stringify(after),rows=[];
  for(let i=0;i<text.length;i+=40000)rows.push({values:[{userEnteredValue:{stringValue:text.slice(i,i+40000)}}]});
  if(rows.length!==snapshot.mapParts.length)throw Error('Quantidade de fragmentos do mapa mudou; preparar expansão separada');
  requests.push({updateCells:{start:{sheetId:sheets.get('R53_LOTE').sheetId,rowIndex:0,columnIndex:0},rows,fields:'userEnteredValue'}});
 }else throw Error('Snapshot do mapa de aparência obrigatório');
 return{requests};
}
module.exports={p,sha,prepararCodigo,prepararEditor,planejar,planejarInstalacao,norm,atualizarAtalho};
