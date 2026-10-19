'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const runtime=process.argv[2]||'r53/saidas/EditorR53-prototipo.gs';
let checks=0;function eq(a,b){assert.deepStrictEqual(a,b);checks++;}
function pos(s){let m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(s);assert(m,s);let c=t=>[...t].reduce((n,l)=>n*26+l.charCodeAt(0)-64,0);return [+m[2],c(m[1]),+(m[4]||m[2]),c(m[3]||m[1])];}
class Range{
 constructor(sheet,r,c,nr=1,nc=1){Object.assign(this,{sheet,r,c,nr,nc});}
 getSheet(){return this.sheet;}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}
 getValues(){return Array.from({length:this.nr},(_,i)=>Array.from({length:this.nc},(_,j)=>this.sheet.cells.get(`${this.r+i},${this.c+j}`)??''));}
 getValue(){return this.getValues()[0][0];}getFormula(){let v=this.getValue();return typeof v==='string'&&v.startsWith('=')?v:'';}
 setValues(v){v.forEach((row,i)=>row.forEach((x,j)=>{let rule=this.sheet.validations.get(`${this.r+i},${this.c+j}`);if(rule&&!rule.allowInvalid&&x!==''&&!rule.values.includes(String(x)))throw new Error('Validação nativa rejeitou '+x);}));v.forEach((row,i)=>row.forEach((x,j)=>this.sheet.cells.set(`${this.r+i},${this.c+j}`,typeof x==='string'&&x.startsWith("'")?x.slice(1):x)));return this;}
 setValue(v){return this.setValues([[v]]);}setFormula(v){return this.setValue(v);}setDataValidation(v){this.sheet.validations.set(`${this.r},${this.c}`,v);return this;}
}
class Sheet{
 constructor(name){this.name=name;this.cells=new Map;this.validations=new Map;this.visible=false;this.selection='';}
 getName(){return this.name;}getRange(a,c,nr,nc){if(typeof a==='string'){let [r,col,rr,cc]=pos(a.replace(/\$/g,''));return new Range(this,r,col,rr-r+1,cc-col+1);}return new Range(this,a,c,nr,nc);}
 getColumnGroup(){return {expand:()=>{this.visible=true;},collapse:()=>{this.visible=false;}};}
 showColumns(){this.visible=true;}hideColumns(){this.visible=false;}setActiveSelection(a){this.selection=a;}
}
let sheets=new Map(),toasts=[];let ss={getSheetByName(n){if(!sheets.has(n))sheets.set(n,new Sheet(n));return sheets.get(n);},getSpreadsheetLocale(){return'en_US';},toast(x){toasts.push(x);},getActiveRange(){return ss.active;},setActiveSheet(sh){ss.activeSheet=sh;return sh;},setActiveRange(r){let c=r.c,s='';while(c){let k=(c-1)%26;s=String.fromCharCode(65+k)+s;c=Math.floor((c-1)/26);}r.sheet.selection=s+r.r;ss.active=r;return r;}};
let sandbox={console,SpreadsheetApp:{getActive:()=>ss,newDataValidation(){return{values:[],allowInvalid:true,requireValueInList(v){this.values=Array.from(v);return this;},setAllowInvalid(v){this.allowInvalid=v;return this;},build(){return{values:this.values,allowInvalid:this.allowInvalid};}};}},LockService:{getDocumentLock(){return{tryLock:()=>true,releaseLock(){}};}}};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(runtime,'utf8'),sandbox);
let cfg=sandbox.R53_EDITOR_,fields=cfg.campos.map(f=>f[0]);
function init(g,cl=3){let sh=ss.getSheetByName(g.aba);sh.getRange(g.cel.nome).setValue(g.id);if(g.cel.classe)sh.getRange(g.cel.classe).setValue(cl);
let p=g.classe_maxima.lastIndexOf('!');ss.getSheetByName(g.classe_maxima.slice(0,p).replace(/^'|'$/g,'')).getRange(g.classe_maxima.slice(p+1)).setValue(4);
g.classes.forEach((c,j)=>ss.getSheetByName(cfg.storage).getRange(g.editor+2,j+2,fields.length,1).setValues(fields.map(k=>[cfg.defaults[k]])));}
function values(g,cl){return Array.from(sandbox.r53LerVersao_(ss,g,cl));}
function save(g,cl,x){let a=values(g,cl);for(let[k,v]of Object.entries(x))a[fields.indexOf(k)]=v;ss.getSheetByName(cfg.storage).getRange(g.editor+2,sandbox.r53Coluna_(ss,g,cl),fields.length,1).setValues(a.map(v=>[v]));}
function edit(sh,a,v){let r=sh.getRange(a);sh.cells.set(`${r.r},${r.c}`,v);eq(sandbox.r53Editar_({range:r,source:ss}),true);}
let first=cfg.contextos.find(g=>g.id==='feitico.1'),entity=cfg.contextos.find(g=>g.id==='entidade.1.esp.1');init(first);init(entity);
save(first,3,{preparada:true,funcao1:'Dano',pontos1:2,funcao2:'Cura',pontos2:2,m1:'Mais Um',origem_permissao:'Texto literal',tr_dano:'Físico'});
let sh=ss.getSheetByName(first.aba),panel=cfg.paineis[first.aba];edit(sh,first.abrir_editor,true);
eq(sh.visible,true);eq(sh.getRange(first.abrir_editor).getValue(),false);eq(sh.getRange(panel.campos.pontos1).getValue(),2);
edit(sh,panel.campos.pontos1,3);eq(values(first,3)[fields.indexOf('pontos1')],3);
edit(sh,panel.classe,4);eq(sh.getRange(first.cel.classe).getValue(),4);eq(sh.getRange(panel.campos.funcao2).getValue(),'Cura');eq(sh.getRange(panel.campos.pontos1).getValue(),0);eq(sh.getRange(panel.campos.preparada).getValue(),false);
edit(sh,panel.campos.pontos1,4);edit(sh,panel.campos.pontos2,2);edit(sh,panel.campos.preparada,true);
edit(sh,panel.classe,3);eq(sh.getRange(panel.campos.pontos1).getValue(),3);eq(values(first,4)[fields.indexOf('pontos1')],4);
let before=values(first,3);edit(sh,panel.campos.pontos1,-1);eq(values(first,3),before);eq(sh.getRange(panel.campos.pontos1).getValue(),3);
edit(sh,panel.campos.pontos1,1.5);eq(values(first,3),before);edit(sh,panel.campos.pontos1,'=1+1');eq(values(first,3),before);
edit(sh,panel.campos.preparada,'TRUE');eq(values(first,3),before);
edit(sh,panel.classe,7);eq(sh.getRange(panel.classe).getValue(),3);eq(sh.getRange(first.cel.classe).getValue(),3);
edit(sh,panel.voltar,true);eq(sh.visible,false);eq(sh.selection,first.cel.nome);
let ish=ss.getSheetByName(entity.aba),ip=cfg.paineis[entity.aba];edit(ish,entity.abrir_editor,true);edit(ish,ip.campos.funcao1,'Dano');edit(ish,ip.campos.pontos1,6);eq(values(entity,3)[fields.indexOf('pontos1')],6);eq(values(first,3),before);
// Prosa com '=' precisa continuar literal no armazenamento.
edit(ish,ip.campos.origem_permissao,'=texto');eq(values(entity,3)[fields.indexOf('origem_permissao')],'');
edit(ish,ip.campos.origem_permissao,'Texto\n"aspas" \\ barra');eq(values(entity,3)[fields.indexOf('origem_permissao')],'Texto\n"aspas" \\ barra');
// Voltar e reabrir não perde a versão salva.
edit(ish,ip.voltar,true);edit(ish,entity.abrir_editor,true);eq(ish.getRange(ip.campos.pontos1).getValue(),6);
// Restauração usa a fórmula R53, não o resultado antigo do B47.
let computed=Object.keys(first.formulas)[0];edit(sh,computed,'999');eq(sh.getRange(computed).getFormula(),first.formulas[computed]);
// Cópia: o código sempre consulta a planilha ativa, sem IDs externos.
let compact=cfg.contextos.find(g=>g.id==='classe0.1');init(compact,0);
edit(sh,compact.abrir_editor,true);
eq(sh.visible,true);eq(sh.selection,panel.classe);
eq(sh.getRange(panel.classe).getValue(),0);
eq(cfg.contextos.every(g=>typeof g.abrir_editor==='string'),true);
edit(sh,first.abrir_editor,true);eq(sh.getRange(panel.classe).getValue(),3);
eq(/openById|UrlFetchApp|DriveApp|ScriptApp\.newTrigger/.test(fs.readFileSync(runtime,'utf8')),false);
console.log(checks+' verificações do editor passaram (simulação; prova Google ainda separada).');
