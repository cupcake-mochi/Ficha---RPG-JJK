'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');let checks=0;
function eq(a,b){assert.deepStrictEqual(a,b);checks++;}
function pos(a){let m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a.replace(/\$/g,''));assert(m,a);const col=s=>[...s].reduce((a,c)=>a*26+c.charCodeAt(0)-64,0);return [+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1])];}
class Range{
 constructor(sh,r,c,nr=1,nc=1){Object.assign(this,{sh,r,c,nr,nc});}getSheet(){return this.sh;}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}
 getValues(){return Array.from({length:this.nr},(_,i)=>Array.from({length:this.nc},(_,j)=>this.sh.map.get(`${this.r+i},${this.c+j}`)??''));}getValue(){return this.getValues()[0][0];}
 getFormulas(){return this.getValues().map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?v:''));}
 setValues(v){v.forEach((row,i)=>row.forEach((v,j)=>this.sh.map.set(`${this.r+i},${this.c+j}`,typeof v==='string'&&v.startsWith("'")?v.slice(1):v)));return this;}setValue(v){return this.setValues([[v]]);}setFormula(v){return this.setValue(v);}setDataValidation(v){this.sh.dv.set(`${this.r},${this.c}`,v);return this;}clearDataValidations(){this.sh.dv.delete(`${this.r},${this.c}`);return this;}
}
class Sheet{
 constructor(n){this.n=n;this.map=new Map;this.dv=new Map;}getName(){return this.n;}getRange(a,c,nr,nc){if(typeof a==='string'){let[r,c,rr,cc]=pos(a);return new Range(this,r,c,rr-r+1,cc-c+1);}return new Range(this,a,c,nr,nc);}
 getRangeList(ps){return {setValue:v=>ps.forEach(p=>this.getRange(p).setValue(v))};}
 getDataRange(){let r=1,c=1;for(const k of this.map.keys()){let[y,x]=k.split(',').map(Number);r=Math.max(r,y);c=Math.max(c,x);}return new Range(this,1,1,r,c);}
}
const sheets=new Map,props=new Map,toasts=[];
const ss={getSheetByName(n){if(!sheets.has(n))sheets.set(n,new Sheet(n));return sheets.get(n);},toast(t){toasts.push(t);},getSpreadsheetLocale(){return'en_US';}};
const box={console,PropertiesService:{getDocumentProperties:()=>({getProperty:k=>props.get(k)||null,setProperty:(k,v)=>props.set(k,v)})},LockService:{getDocumentLock:()=>({tryLock:()=>true,releaseLock(){}})},SpreadsheetApp:{getActive:()=>ss,newDataValidation(){let o={};for(const k of ['requireCheckbox','requireValueInList','requireFormulaSatisfied','setAllowInvalid'])o[k]=function(...v){this[k+'_args']=v;return this;};o.build=function(){return {...this};};return o;}}};
vm.createContext(box);vm.runInContext(fs.readFileSync(process.argv[2]||'apps-script/EditorR53.gs','utf8'),box);
const cfg=box.R53_EDITOR_,fields=cfg.campos.map(f=>f[0]);eq(cfg.esquema,3);eq(cfg.contextos.length,249);eq(!!cfg.paineis,false);
ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);
for(const g of cfg.contextos){
 let p=g.classe_maxima.lastIndexOf('!');ss.getSheetByName(g.classe_maxima.slice(0,p).replace(/^'|'$/g,'')).getRange(g.classe_maxima.slice(p+1)).setValue(7);
 let sh=ss.getSheetByName(g.aba);sh.getRange(g.cel.nome).setValue(g.id);if(g.cel.classe)sh.getRange(g.cel.classe).setValue(g.classes[0]);
 g.classes.forEach((c,i)=>ss.getSheetByName(cfg.storage).getRange(g.editor+2,i+2,fields.length,1).setValues(fields.map(f=>[cfg.defaults[f]])));
 box.r53Mostrar_(ss,g,g.classes[0]===null?7:g.classes[0]);
 assert(!g.abrir_editor);assert(Object.keys(g.entradas_diretas).length>=1);checks+=2;
}
const first=cfg.contextos.find(g=>g.id==='feitico.1'),sh=ss.getSheetByName(first.aba);
function read(g,cl,k){return box.r53LerVersao_(ss,g,cl)[fields.indexOf(k)];}
function edit(g,p,v,old){let r=ss.getSheetByName(g.aba).getRange(p);r.setValue(v);return box.r53Editar_({range:r,source:ss,oldValue:old});}
function cl(g,next,old){eq(edit(g,g.cel.classe,next,String(old)),true);}
cl(first,3,1);edit(first,first.funcoes_diretas.dano,3);edit(first,first.funcoes_diretas.cura,2);eq(read(first,3,'pontos1'),3);eq(read(first,3,'pontos2'),2);
cl(first,4,3);eq(read(first,4,'preparada'),false);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),0);edit(first,first.funcoes_diretas.dano,4);cl(first,3,4);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),3);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),2);eq(read(first,4,'pontos1'),4);
edit(first,first.funcoes_diretas.dano,-1);eq(sh.getRange(first.funcoes_diretas.dano).getValue(),3);edit(first,first.funcoes_diretas.dano,1.5);eq(read(first,3,'pontos1'),3);edit(first,first.funcoes_diretas.dano,'=1+1');eq(read(first,3,'pontos1'),3);
props.set('r53_amparo_direto',JSON.stringify(Array(13).fill('Normal')));ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([['Fechada',...Array(12).fill('Normal')]]);box.R53_REF_CACHE_={};box.r53SincronizarFamilias_(ss);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),'—');eq(read(first,3,'pontos2'),2);edit(first,first.funcoes_diretas.cura,99);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),'—');eq(read(first,3,'pontos2'),2);
ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);box.R53_REF_CACHE_={};box.r53SincronizarFamilias_(ss);eq(sh.getRange(first.funcoes_diretas.cura).getValue(),2);
const entity=cfg.contextos.find(g=>g.id==='entidade.1.esp.1');cl(entity,3,1);edit(entity,entity.funcoes_diretas.dano,6);eq(read(entity,3,'pontos1'),6);eq(read(first,3,'pontos1'),3);
const maximum=cfg.contextos.find(g=>g.id==='maxima.1');edit(maximum,maximum.funcoes_diretas.dano,true);edit(maximum,maximum.funcoes_diretas.cura,true);eq(ss.getSheetByName(maximum.aba).getRange(maximum.funcoes_diretas.dano).getValue(),false);eq(read(maximum,7,'funcao2'),'Cura');eq(ss.getSheetByName(maximum.aba).getRange(maximum.funcoes_diretas.vt).getValue(),'—');
const zero=cfg.contextos.find(g=>g.id==='classe0.1');edit(zero,zero.funcoes_diretas.dano,true);eq(read(zero,0,'funcao1'),'Dano');
const lib=cfg.contextos.find(g=>g.id==='entidade.1.liberacao.1');edit(lib,lib.funcoes_diretas.dano,4);eq(read(lib,3,'pontos1'),4);eq(Object.keys(lib.entradas_diretas).includes('m4'),true);eq(ss.getSheetByName(lib.aba).getRange(lib.funcoes_diretas.cura).getValue(),'—');
// A visit to an unedited Class does not publish a draft version.
cl(first,5,3);cl(first,3,5);eq(read(first,5,'preparada'),false);
const computed=Object.keys(first.formulas)[0];edit(first,computed,999);eq(sh.getRange(computed).getValue(),first.formulas[computed]);
cl(first,7,3);cl(first,8,7);eq(sh.getRange(first.cel.classe).getValue(),7);eq(/openById|UrlFetchApp|DriveApp|ScriptApp\.newTrigger/.test(fs.readFileSync(process.argv[2]||'apps-script/EditorR53.gs','utf8')),false);
// A Class switch cannot silently replace input still waiting to be saved.
cl(first,3,7);sh.getRange(first.funcoes_diretas.dano).setValue(5);cl(first,4,3);
eq(sh.getRange(first.cel.classe).getValue(),3);eq(read(first,3,'pontos1'),5);
eq(toasts.some(t=>t.includes('preservada na Classe')),true);
cl(first,4,3);eq(sh.getRange(first.cel.classe).getValue(),4);
// A scalar event dispatched after an older callback rewrote its UI cell
// replays its own payload, instead of saving the stale visible value.
let late=sh.getRange(first.funcoes_diretas.dano);late.setValue(0);
box.r53Editar_({range:late,source:ss,value:'6',oldValue:'4'});eq(read(first,4,'pontos1'),6);eq(late.getValue(),6);
// An obsolete Class event must not roll back a later user selection.
sh.getRange(first.cel.classe).setValue(5);box.r53Editar_({range:sh.getRange(first.cel.classe),source:ss,value:'3',oldValue:'4'});eq(sh.getRange(first.cel.classe).getValue(),5);
console.log(JSON.stringify({checks,resultado:'OK',escopo:'Persistência, Classes, edição direta, proteção de edições concorrentes, bloqueio por Família e modalidades; fórmulas e visual exigem prova Google.'}));
