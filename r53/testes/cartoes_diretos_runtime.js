'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');let checks=0;const io=[];let enforceValidation=false;
function eq(a,b){assert.deepStrictEqual(a,b);checks++;}
function pos(a){let m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a.replace(/\$/g,''));assert(m,a);const col=s=>[...s].reduce((a,c)=>a*26+c.charCodeAt(0)-64,0);return [+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1])];}
class Range{
 constructor(sh,r,c,nr=1,nc=1){Object.assign(this,{sh,r,c,nr,nc});}getSheet(){return this.sh;}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}
 getValues(){io.push('read:'+this.sh.n);return Array.from({length:this.nr},(_,i)=>Array.from({length:this.nc},(_,j)=>this.sh.map.get(`${this.r+i},${this.c+j}`)??''));}getValue(){return this.getValues()[0][0];}
 getFormulas(){return this.getValues().map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?v:''));}
 setValues(v){io.push('write:'+this.sh.n);v.forEach((row,i)=>row.forEach((v,j)=>{const key=`${this.r+i},${this.c+j}`,dv=this.sh.dv.get(key);if(enforceValidation&&dv&&dv.setAllowInvalid_args[0]===false){if(dv.requireCheckbox_args)assert.strictEqual(typeof v,'boolean','checkbox rejects '+v);if(dv.requireValueInList_args)assert(dv.requireValueInList_args[0].includes(v),'blocked field rejects '+v);}this.sh.map.set(key,typeof v==='string'&&v.startsWith("'")?v.slice(1):v);}));return this;}setValue(v){return this.setValues([[v]]);}setFormula(v){return this.setValue(v);}setDataValidation(v){this.sh.dv.set(`${this.r},${this.c}`,v);return this;}clearDataValidations(){this.sh.dv.delete(`${this.r},${this.c}`);return this;}
}
class Sheet{
 constructor(n){this.n=n;this.map=new Map;this.dv=new Map;}getName(){return this.n;}getRange(a,c,nr,nc){if(typeof a==='string'){let[r,c,rr,cc]=pos(a);return new Range(this,r,c,rr-r+1,cc-c+1);}return new Range(this,a,c,nr,nc);}
 getRangeList(ps){return {setValue:v=>ps.forEach(p=>this.getRange(p).setValue(v))};}
 getDataRange(){let r=1,c=1;for(const k of this.map.keys()){let[y,x]=k.split(',').map(Number);r=Math.max(r,y);c=Math.max(c,x);}return new Range(this,1,1,r,c);}
}
const sheets=new Map,props=new Map,toasts=[];
const ss={getSheetByName(n){if(!sheets.has(n))sheets.set(n,new Sheet(n));return sheets.get(n);},toast(t){toasts.push(t);},getSpreadsheetLocale(){return'en_US';}};
const lockTrace=[];let locked=false;
const box={console,PropertiesService:{getDocumentProperties:()=>({getProperty:k=>props.get(k)||null,setProperty:(k,v)=>props.set(k,v)})},LockService:{getDocumentLock:()=>({tryLock(){locked=true;lockTrace.push('acquire');return true;},releaseLock(){assert(locked);assert.strictEqual(lockTrace.at(-1),'flush');locked=false;lockTrace.push('release');}})},SpreadsheetApp:{getActive:()=>ss,flush(){assert(locked);lockTrace.push('flush');},newDataValidation(){let o={};for(const k of ['requireCheckbox','requireValueInList','requireFormulaSatisfied','setAllowInvalid'])o[k]=function(...v){this[k+'_args']=v;return this;};o.build=function(){return {...this};};return o;}}};
box.Utilities={DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1},base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>require('zlib').gunzipSync(x).toString('utf8')}),computeDigest:(_,s)=>Array.from(require('crypto').createHash('sha256').update(s).digest())};
vm.createContext(box);vm.runInContext(fs.readFileSync(process.argv[2]||'apps-script/EditorR53.gs','utf8'),box);
const cfg=box.R53_EDITOR_,fields=cfg.campos.map(f=>f[0]);eq(cfg.esquema,3);eq(cfg.contextos.length,249);eq(!!cfg.paineis,false);
// Uma cópia começa sem propriedades: editar Caminho/Trilha não pode iniciar
// a recuperação de 249 cartões antes das automações da FICHA.
for(const cell of ['D11','N11']){
 const before=io.length;eq(box.r53Editar_({source:ss,range:ss.getSheetByName('FICHA').getRange(cell)}),false);
 eq(io.length,before);eq(props.has('r53_amparo_direto'),false);
}
ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);
for(const g of cfg.contextos){
 let p=g.classe_maxima.lastIndexOf('!');ss.getSheetByName(g.classe_maxima.slice(0,p).replace(/^'|'$/g,'')).getRange(g.classe_maxima.slice(p+1)).setValue(7);
 let sh=ss.getSheetByName(g.aba);sh.getRange(g.cel.nome).setValue(g.id);if(g.cel.classe)sh.getRange(g.cel.classe).setValue(g.classes[0]);
 g.classes.forEach((c,i)=>ss.getSheetByName(cfg.storage).getRange(g.editor+2,i+2,fields.length,1).setValues(fields.map(f=>[cfg.defaults[f]])));
 box.r53Mostrar_(ss,g,g.classes[0]===null?7:g.classes[0]);
 assert(!g.abrir_editor);assert(Object.keys(g.entradas_diretas).length>=1);checks+=2;
}
// Cópia nova: as propriedades do documento não vão junto. Editar fora dos
// cartões guarda o amparo atual sem varrer os 249 (estourava 30 s no Google).
for(const [aba,cell] of [['CARTEIRA','A1'],['FICHA AMALDIÇOADA','B500'],['INVOCAÇÕES','A1'],['CONFIGURAÇÃO','A1']]){
 props.delete('r53_amparo_direto');box.R53_REF_CACHE_={};io.length=0;
 eq(box.r53Editar_({source:ss,range:ss.getSheetByName(aba).getRange(cell)}),false);
 eq(io,['read:'+cfg.amparo.aba]);eq(JSON.parse(props.get('r53_amparo_direto')),Array(13).fill('Normal'));
}
// Com o estado guardado, fechar uma Família ainda acerta só os cartões dela.
{const esp=cfg.contextos.find(g=>g.id==='entidade.1.esp.1'),inv=ss.getSheetByName(esp.aba),cura=inv.getRange(esp.funcoes_diretas.cura).getValue();
 ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([['Normal','Fechada',...Array(11).fill('Normal')]]);box.R53_REF_CACHE_={};io.length=0;
 eq(box.r53Editar_({source:ss,range:ss.getSheetByName('CARTEIRA').getRange('A1')}),false);
 eq(inv.getRange(esp.funcoes_diretas.cura).getValue(),'—');eq(io.includes('read:FICHA AMALDIÇOADA'),false);
 ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);box.R53_REF_CACHE_={};box.r53SincronizarFamilias_(ss);
 eq(inv.getRange(esp.funcoes_diretas.cura).getValue(),cura);props.delete('r53_amparo_direto');}
const first=cfg.contextos.find(g=>g.id==='feitico.1'),sh=ss.getSheetByName(first.aba);
function read(g,cl,k){return box.r53LerVersao_(ss,g,cl)[fields.indexOf(k)];}
function edit(g,p,v,old){let r=ss.getSheetByName(g.aba).getRange(p);r.setValue(v);return box.r53Editar_({range:r,source:ss,oldValue:old});}
function cl(g,next,old){eq(edit(g,g.cel.classe,next,String(old)),true);}
// Changing to a new version must finish all reads before its first write.
// In Sheets a read after writing storage forces a full recalculation; the old
// path timed out at 30.707 s and left the previous Class's points visible.
io.length=0;cl(first,2,1);
const firstWrite=io.findIndex(x=>x==='write:'+cfg.storage);
eq(firstWrite>=0,true);eq(io.slice(firstWrite).some(x=>x.startsWith('read:')),false);
cl(first,1,2);
cl(first,3,1);edit(first,first.funcoes_diretas.dano,3);edit(first,first.funcoes_diretas.cura,2);eq(read(first,3,'pontos1'),3);eq(read(first,3,'pontos2'),2);
cl(first,4,3);eq(read(first,4,'preparada'),false);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),0);edit(first,first.funcoes_diretas.dano,4);cl(first,3,4);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),3);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),2);eq(read(first,4,'pontos1'),4);
edit(first,first.funcoes_diretas.dano,-1);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),3);edit(first,first.funcoes_diretas.dano,1.5);eq(read(first,3,'pontos1'),3);edit(first,first.funcoes_diretas.dano,'=1+1');eq(read(first,3,'pontos1'),3);
props.set('r53_amparo_direto',JSON.stringify(Array(13).fill('Normal')));ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([['Fechada',...Array(12).fill('Normal')]]);box.R53_REF_CACHE_={};box.r53SincronizarFamilias_(ss);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),'—');eq(read(first,3,'pontos2'),2);edit(first,first.funcoes_diretas.cura,99);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),'—');eq(read(first,3,'pontos2'),2);
ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);box.R53_REF_CACHE_={};box.r53SincronizarFamilias_(ss);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),2);
const entity=cfg.contextos.find(g=>g.id==='entidade.1.esp.1');cl(entity,3,1);edit(entity,entity.funcoes_diretas.dano,6);eq(read(entity,3,'pontos1'),6);eq(read(first,3,'pontos1'),3);
const maximum=cfg.contextos.find(g=>g.id==='maxima.1');edit(maximum,maximum.funcoes_diretas.dano,true);edit(maximum,maximum.funcoes_diretas.cura,true);eq(ss.getSheetByName(maximum.aba).getRange(maximum.funcoes_diretas.dano).getValue(),false);eq(read(maximum,7,'funcao2'),'Cura');eq(ss.getSheetByName(maximum.aba).getRange(maximum.funcoes_diretas.vt).getValue(),'—');
const zero=cfg.contextos.find(g=>g.id==='classe0.1');edit(zero,zero.funcoes_diretas.dano,true);eq(read(zero,0,'funcao1'),'Dano');
const lib=cfg.contextos.find(g=>g.id==='entidade.1.liberacao.1');edit(lib,lib.funcoes_diretas.dano,4);eq(read(lib,3,'pontos1'),4);eq(Object.keys(lib.entradas_diretas).includes('m4'),true);eq(ss.getSheetByName(lib.aba).getRange(lib.funcoes_diretas.cura).getValue(),'—');
// Native Sheets rejects a blocked dash under an existing strict checkbox rule.
const lastMaximum=cfg.contextos.find(g=>g.id==='entidade.12.maxima.1');
const blocked=ss.getSheetByName(lastMaximum.aba).getRange(lastMaximum.funcoes_diretas.vt);
blocked.clearDataValidations().setValue(false).setDataValidation(box.SpreadsheetApp.newDataValidation().requireCheckbox().setAllowInvalid(false).build());
enforceValidation=true;box.r53Mostrar_(ss,lastMaximum,7);enforceValidation=false;
eq(blocked.getValue(),'—');eq(blocked.sh.dv.get(`${blocked.r},${blocked.c}`).requireValueInList_args[0][0],'—');
// Point/checkbox edits must also complete every read before storage is written.
for(const [g,value] of [[first,6],[lastMaximum,true]]){
 io.length=0;edit(g,g.funcoes_diretas.dano,value);
 const savedAt=io.findIndex(x=>x==='write:'+cfg.storage);
 eq(savedAt>=0,true);eq(io.slice(savedAt).some(x=>x.startsWith('read:')),false);
}
// A visit to an unedited Class does not publish a draft version.
cl(first,5,3);cl(first,3,5);eq(read(first,5,'preparada'),false);
const computed=Object.keys(first.formulas)[0];edit(first,computed,999);eq(sh.getRange(computed).getValue(),first.formulas[computed]);
cl(first,7,3);cl(first,8,7);eq(sh.getRange(first.cel.classe).getValue(),7);eq(/openById|UrlFetchApp|DriveApp|ScriptApp\.newTrigger/.test(fs.readFileSync(process.argv[2]||'apps-script/EditorR53.gs','utf8')),false);
// A Class switch cannot silently replace input still waiting to be saved.
cl(first,3,7);sh.getRange(first.funcoes_diretas.dano).setValue(5);io.length=0;cl(first,4,3);
// First write is the simulated user selection; second is the runtime rollback.
const rollback=io.map((x,i)=>x==='write:'+first.aba?i:-1).filter(i=>i>=0)[1];
eq(typeof rollback,'number');eq(io.slice(rollback).some(x=>x.startsWith('read:')),false);
eq(sh.getRange(first.cel.classe).getValue(),3);eq(read(first,3,'pontos1'),5);
eq(toasts.some(t=>t.includes('preservada na Classe')),true);
cl(first,4,3);eq(sh.getRange(first.cel.classe).getValue(),4);
// A scalar event dispatched after an older callback rewrote its UI cell
// replays its own payload, instead of saving the stale visible value.
let late=sh.getRange(first.funcoes_diretas.dano);late.setValue(0);
box.r53Editar_({range:late,source:ss,value:'6',oldValue:'4'});eq(read(first,4,'pontos1'),6);eq(late.getValue(),6);
// An obsolete Class event must not roll back a later user selection.
sh.getRange(first.cel.classe).setValue(5);box.r53Editar_({range:sh.getRange(first.cel.classe),source:ss,value:'3',oldValue:'4'});eq(sh.getRange(first.cel.classe).getValue(),5);
// A failed flush still releases the document lock, without hiding the failure.
const flush=box.SpreadsheetApp.flush;
box.SpreadsheetApp.flush=()=>{flush();throw Error('flush indisponível no ensaio');};
assert.throws(()=>edit(first,first.funcoes_diretas.dano,6),/flush indisponível no ensaio/);checks++;
eq(locked,false);eq(lockTrace.slice(-3),['acquire','flush','release']);
box.SpreadsheetApp.flush=flush;
console.log(JSON.stringify({checks,resultado:'OK',escopo:'Persistência, Classes, edição direta, proteção de edições concorrentes, bloqueio por Família e modalidades; fórmulas e visual exigem prova Google.'}));
