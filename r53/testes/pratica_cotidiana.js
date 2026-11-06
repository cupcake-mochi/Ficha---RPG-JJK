'use strict';
const fs=require('node:fs'),vm=require('node:vm'),z=require('node:zlib'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const p=require('../diagnostico-android/preparar_pratica_cotidiana'),rt=require('../pratica_cotidiana_runtime'),{formulaLocal}=require('../diagnostico-android/preparar_pilha_5156');
let checks=0;const t=f=>{f();checks++;},clone=x=>JSON.parse(JSON.stringify(x));
const c={};vm.runInNewContext(require('../../medidas/carregar-ficha').fontes(),c);t(()=>assert.equal(c.SOBRAS_.length,0));
const editor=c.R53_EDITOR_;t(()=>assert.equal(editor.contextos.length,251));
t(()=>assert.equal(crypto.createHash('sha256').update(JSON.stringify(editor.contextos.slice(0,249))).digest('hex'),'09d6c58b762db5290f8ac12807d9c631e6840449b104873d6cf5100c3918c9a6'));
const indexes=new Map(c.ABAS.map(a=>[a.nome,{spec:a,values:new Map(a.vals.map(v=>[v[0]+','+v[1],v]))}]));
const v=(aba,a1)=>{const m=/^([A-Z]+)(\d+)$/.exec(a1),col=[...m[1]].reduce((a,x)=>26*a+x.charCodeAt(0)-64,0),r=+m[2],spec=indexes.get(aba).spec,direct=indexes.get(aba).values.get(r+','+col);if(direct)return aba==='ANALISE'&&col===2&&direct[2]==="'0"?'0':direct[2];const block=(spec.abaixo||[]).find(b=>b[0]<r&&b[2]>=r&&b[1]<=col&&b[3]>=col);if(block){const src=indexes.get(aba).values.get(block[0]+','+col);if(src)return require('../../medidas/sheets-de-mentira').deslocaFormula(src[2],r-block[0]);}return null;};
for(const x of p.p.cells)t(()=>assert.equal(p.norm(v(x.aba,x.a1)),p.norm(x.depois),x.aba+'!'+x.a1));
t(()=>assert.equal(v('DADOS_R53','A251'),'r53.editor.gid'));
for(const g of editor.contextos.slice(249)){
 t(()=>assert.deepEqual(Object.keys(g.formulas).sort(),[g.cel.dano,g.cel.alcance].sort()));
 for(const [pos,formula]of Object.entries(g.formulas))t(()=>assert.equal(p.norm(v(g.aba,pos)),p.norm(formula)));
 t(()=>assert(v('MONTAGENS','A'+g.editor).startsWith('="'+g.id+' · "&')));
}
t(()=>assert.deepEqual(Array.from(editor.contextos.slice(249),g=>[g.id,g.linha,g.editor,g.cel.nome]),[['classe0.6',252,9467,'D566'],['classe0.7',253,9505,'D567']]));
t(()=>assert(v('DADOS_CUSTOM','B134').includes('$B$126')));t(()=>assert(v('DADOS_AM','HM10').endsWith('+DADOS_CUSTOM!$B$134')));
// Native preflight is read-only and refuses even a late occupied target.
for(const locale of ['pt_BR','en_US']){
 const by=new Map();for(const x of [...p.p.cells,...p.p.notes])by.set(x.aba+'!'+x.a1,{aba:x.aba,a1:x.a1,sheetId:['FICHA AMALDIÇOADA','DADOS_AM','DADOS_CUSTOM','MONTAGENS','DADOS_R53','ANALISE'].indexOf(x.aba),value:formulaLocal(p.p.cells.find(t=>t.aba===x.aba&&t.a1===x.a1)?.antes??null,locale),note:p.p.notes.find(t=>t.aba===x.aba&&t.a1===x.a1)?.antes??null});
 const s={locale,cells:[...by.values()]},before=clone(s);t(()=>assert.equal(p.planejar(s).requests.length,p.p.cells.length+p.p.notes.length));t(()=>assert.deepEqual(s,before));
 const occupied=clone(s);occupied.cells.at(-1).note='nota manual';t(()=>assert.throws(()=>p.planejar(occupied),/ocupado|divergente/));
 const dup=clone(s);dup.cells.push(clone(dup.cells[0]));t(()=>assert.throws(()=>p.planejar(dup),/duplicada/));
 const missing=clone(s);missing.cells.pop();t(()=>assert.throws(()=>p.planejar(missing),/ausente/));
}
t(()=>assert.throws(()=>p.prepararCodigo('base errada'),/PR69/));t(()=>assert.throws(()=>p.prepararEditor('base errada'),/divergente/));
// The cold common path must neither ask for a sheet nor decompress the payload.
let loads=0,writes=[];const b={Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>{loads++;return{getDataAsString:()=>z.gunzipSync(x).toString()};}},SpreadsheetApp:{newRichTextValue:()=>({setText(x){this.x=x;return this;},build(){return{rich:this.x};}})},r53CargaFormulaNoIdioma_:formulaLocal};vm.createContext(b);vm.runInContext(rt.gerar(),b);
function event(name,r,c,rr=r,cc=c){return{range:{getRow:()=>r,getLastRow:()=>rr,getColumn:()=>c,getLastColumn:()=>cc,getSheet:()=>({getName:()=>name,getParent:()=>({getSpreadsheetLocale:()=> 'pt_BR'}),getRange:(r,c,h,w)=>({setValues:x=>writes.push({name,r,c,h,w,x,rich:false}),setRichTextValues:x=>writes.push({name,r,c,h,w,x,rich:true})})})}};}
for(const [r,c]of [[11,4],[566,4],[566,6],[566,17],[567,10]]){const e=event('FICHA AMALDIÇOADA',r,c);e.range.getSheet=()=>{throw Error('edição comum consultou a aba');};t(()=>assert.equal(b.r53PraticaRestaurar_(e),false));}t(()=>assert.equal(loads,0));
t(()=>assert.equal(b.r53PraticaRestaurar_(event('FICHA AMALDIÇOADA',566,4,567,20)),false));t(()=>assert(writes.every(w=>[16,18].includes(w.c))));t(()=>assert.equal(writes.length,2));t(()=>assert.equal(loads,1));
t(()=>assert.equal(b.r53PraticaRestaurar_(event('FICHA AMALDIÇOADA',566,16)),true));
writes=[];t(()=>assert.equal(b.r53PraticaRestaurar_(event('DADOS_R53',252,1,253,183)),true));t(()=>assert.equal(writes.length,1));t(()=>assert.equal(writes[0].x.length,2));t(()=>assert.equal(writes[0].x[0].length,183));t(()=>assert.equal(writes[0].x[0][0],'classe0.6'));t(()=>assert.equal(writes[0].x[1][0],'classe0.7'));t(()=>assert(writes[0].x[0].some(x=>typeof x==='string'&&x.includes('D566'))));
const addr=rt.dados().find(x=>x[0]==='ANALISE'&&x[2]===3&&typeof x[3]==='string'&&x[3].startsWith("'"));writes=[];b.r53PraticaRestaurar_(event('ANALISE',addr[1],3));t(()=>assert.equal(writes[0].x[0][0].rich,"'"+addr[3]));
const zero=rt.dados().find(x=>x[0]==='ANALISE'&&x[2]===2&&x[3]==='0');writes=[];b.r53PraticaRestaurar_(event('ANALISE',zero[1],2));t(()=>assert.equal(writes[0].x[0][0].rich,"'0"));
t(()=>assert.equal(loads,1));t(()=>assert.equal(rt.gerar(),fs.readFileSync('apps-script/PraticaCotidiana.gs','utf8')));
// Optional full historical model comparison, using a private baseline without publishing it.
if(process.argv[2]){const old=JSON.parse(fs.readFileSync(process.argv[2]));for(const a of old){const cur=c.ABAS.find(b=>b.nome===a.nome),allowed=new Set(p.p.cells.filter(x=>x.aba===a.nome).map(x=>x.a1));for(const cell of a.vals){const a1=col(cell[1])+cell[0];if(!allowed.has(a1))t(()=>assert.equal(v(a.nome,a1),a.nome==='ANALISE'&&cell[1]===2&&cell[2]==="'0"?'0':cell[2],a.nome+'!'+a1));}}}
function col(n){let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,contextosAntigosPreservados:249,contextosNovos:2,escopo:'estrutura, transporte e restauração em VM; Google separado'}));
