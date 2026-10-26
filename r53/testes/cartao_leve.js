'use strict';
// Cartão em menos idas (26/10/2026): o EditorR53 de agora e o do commit anterior rodam lado a lado, cada um na sua
// planilha de mentira, e cada edição precisa deixar as duas iguais (abas, versões salvas, propriedades e avisos).
// Uso: node r53/testes/cartao_leve.js [EditorR53 de antes] — sem argumento, o de antes sai do git.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),{execSync}=require('child_process');
let checks=0;
function eq(a,b,m){assert.deepStrictEqual(a,b,m);checks++;}
const novo=fs.readFileSync('apps-script/EditorR53.gs','utf8');
const arq=process.argv.slice(2).find(a=>!a.startsWith('--')),antigo=arq?fs.readFileSync(arq,'utf8'):execSync('git show 3e77909:apps-script/EditorR53.gs',{maxBuffer:1<<26}).toString('utf8');
assert.notStrictEqual(novo,antigo,'o EditorR53 de antes é igual ao de agora');

function pos(a){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a.replace(/\$/g,''));assert(m,a);const col=s=>[...s].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);return [+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1])];}
function mundo(fonte){
 const io=[],sheets=new Map,props=new Map,toasts=[];
 class Range{
  constructor(sh,r,c,nr=1,nc=1){Object.assign(this,{sh,r,c,nr,nc});}
  getSheet(){return this.sh;}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}
  getValues(){io.push('read:'+this.sh.n);return Array.from({length:this.nr},(_,i)=>Array.from({length:this.nc},(_,j)=>this.sh.map.get(`${this.r+i},${this.c+j}`)??''));}
  getValue(){return this.getValues()[0][0];}
  getFormulas(){return this.getValues().map(r=>r.map(v=>typeof v==='string'&&v.startsWith('=')?v:''));}
  setValues(v){io.push('write:'+this.sh.n);v.forEach((row,i)=>row.forEach((x,j)=>this.sh.map.set(`${this.r+i},${this.c+j}`,typeof x==='string'&&x.startsWith("'")?x.slice(1):x)));return this;}
  setValue(v){return this.setValues([[v]]);}setFormula(v){return this.setValue(v);}
  setDataValidation(v){this.sh.dv.set(`${this.r},${this.c}`,JSON.stringify(v));return this;}clearDataValidations(){this.sh.dv.delete(`${this.r},${this.c}`);return this;}
 }
 class Sheet{
  constructor(n){this.n=n;this.map=new Map;this.dv=new Map;}getName(){return this.n;}
  getRange(a,c,nr,nc){if(typeof a==='string'){const[r,cc,rr,c2]=pos(a);return new Range(this,r,cc,rr-r+1,c2-cc+1);}return new Range(this,a,c,nr,nc);}
  getRangeList(ps){return {setValue:v=>ps.forEach(p=>this.getRange(p).setValue(v))};}
  getDataRange(){let r=1,c=1;for(const k of this.map.keys()){const[y,x]=k.split(',').map(Number);r=Math.max(r,y);c=Math.max(c,x);}return new Range(this,1,1,r,c);}
 }
 const ss={getSheetByName(n){if(!sheets.has(n))sheets.set(n,new Sheet(n));return sheets.get(n);},toast(t){toasts.push(t);},getSpreadsheetLocale(){return 'en_US';}};
 const box={console:{log(){}},
  PropertiesService:{getDocumentProperties:()=>({getProperty:k=>props.has(k)?props.get(k):null,setProperty:(k,v)=>props.set(k,v)})},
  LockService:{getDocumentLock:()=>({tryLock:()=>true,releaseLock(){}})},
  SpreadsheetApp:{getActive:()=>ss,flush(){io.push('flush');},newDataValidation(){const o={};for(const k of ['requireCheckbox','requireValueInList','requireFormulaSatisfied','setAllowInvalid'])o[k]=function(...v){this[k+'_args']=v;return this;};o.build=function(){return {...this};};return o;}},
  Utilities:{base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>({getDataAsString:()=>require('zlib').gunzipSync(x).toString('utf8')})}};
 vm.createContext(box);vm.runInContext(fonte,box);
 const cfg=box.R53_EDITOR_,campos=cfg.campos.map(f=>f[0]);
 ss.getSheetByName(cfg.amparo.aba).getRange(cfg.amparo.faixa).setValues([Array(13).fill('Normal')]);
 for(const g of cfg.contextos){
  const p=g.classe_maxima.lastIndexOf('!');ss.getSheetByName(g.classe_maxima.slice(0,p).replace(/^'|'$/g,'')).getRange(g.classe_maxima.slice(p+1)).setValue(7);
  const sh=ss.getSheetByName(g.aba);sh.getRange(g.cel.nome).setValue(g.id);if(g.cel.classe)sh.getRange(g.cel.classe).setValue(g.classes[0]);
  g.classes.forEach((c,i)=>ss.getSheetByName(cfg.storage).getRange(g.editor+2,i+2,campos.length,1).setValues(campos.map(f=>[cfg.defaults[f]])));
  box.r53Mostrar_(ss,g,g.classes[0]===null?7:g.classes[0]);
 }
 props.set('r53_amparo_direto',JSON.stringify(Array(13).fill('Normal')));
 function foto(){
  const abas={};for(const [n,sh] of sheets)abas[n]={v:[...sh.map].sort(),dv:[...sh.dv].sort()};
  return JSON.parse(JSON.stringify({abas,props:[...props].sort(),toasts}));
 }
 return {box,ss,cfg,io,foto,sh:n=>ss.getSheetByName(n)};
}
const A=mundo(antigo),B=mundo(novo);
eq(B.foto(),A.foto(),'as duas planilhas começam iguais');
const g=id=>A.cfg.contextos.find(x=>x.id===id);
// Um passo roda nas duas planilhas; a edição chega como no Sheets: a célula já escrita e o e.value em texto.
function passo(nome,fn){
 const r=[A,B].map(w=>{w.box.R53_REF_CACHE_={};const antes=w.io.length;const out=fn(w);const lidas=w.io.slice(antes).filter(x=>x.startsWith('read:'));return {out,lidas};});
 eq(r[1].out,r[0].out,nome+': retorno');eq(B.foto(),A.foto(),nome+': planilha no fim');
 return {nome,antes:r[0].lidas.length,depois:r[1].lidas.length,abas:[...new Set(r[0].lidas)].filter(x=>!r[1].lidas.includes(x)).map(x=>x.slice(5))};
}
function edita(w,card,a1,valor,escalar=true,velho){
 const c=w.cfg.contextos.find(x=>x.id===card),r=w.sh(c.aba).getRange(a1);
 if(Array.isArray(valor))r.setValues(valor);else r.setValue(valor);
 const e={source:w.ss,range:r};if(escalar&&!Array.isArray(valor)){e.value=typeof valor==='boolean'?String(valor).toUpperCase():String(valor);if(velho!==undefined)e.oldValue=velho;}
 return w.box.r53Editar_(e);
}
function amparo(w,lista){w.sh(w.cfg.amparo.aba).getRange(w.cfg.amparo.faixa).setValues([lista]);w.box.R53_REF_CACHE_={};return w.box.r53Editar_({source:w.ss,range:w.sh('CARTEIRA').getRange('A1')});}
const f=g('feitico.1'),max=g('maxima.1'),zero=g('classe0.1'),esp=g('entidade.1.esp.1');
const tabela=[
 passo('feitiço: pontos de dano (E71 = 3)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,3)),
 passo('feitiço: mesmo valor de novo',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,3)),
 passo('feitiço: pontos de cura (F71 = 2)',w=>edita(w,'feitico.1',f.funcoes_diretas.cura,2)),
 passo('feitiço: forma',w=>edita(w,'feitico.1',f.entradas_diretas.forma,'Projétil')),
 passo('feitiço: melhoria 1',w=>edita(w,'feitico.1',f.entradas_diretas.m1,'Alcance')),
 passo('feitiço: colar as três funções (sem e.value)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano+':'+f.funcoes_diretas.vt,[[1,1,1]],false)),
 passo('feitiço: ponto negativo (erro)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,-1)),
 passo('feitiço: apagar o dano (sem e.value)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,'',false)),
 passo('Família geral fechada',w=>amparo(w,['Fechada',...Array(12).fill('Normal')])),
 passo('feitiço fechado: pontos de dano (E71 = 4)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,4)),
 passo('feitiço fechado: tentar cura (F71 = 2)',w=>edita(w,'feitico.1',f.funcoes_diretas.cura,2)),
 passo('Família geral aberta de novo',w=>amparo(w,Array(13).fill('Normal'))),
 passo('feitiço: depois de reabrir (E71 = 5)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,5)),
 passo('feitiço: troca de Classe 1 → 3',w=>edita(w,'feitico.1',f.cel.classe,3,true,'1')),
 passo('feitiço: dano na Classe 3 (E71 = 2)',w=>edita(w,'feitico.1',f.funcoes_diretas.dano,2)),
 passo('máxima (caixas): marcar dano',w=>edita(w,'maxima.1',max.funcoes_diretas.dano,true)),
 passo('máxima (caixas): marcar cura',w=>edita(w,'maxima.1',max.funcoes_diretas.cura,true)),
 passo('máxima (caixas): desmarcar cura',w=>edita(w,'maxima.1',max.funcoes_diretas.cura,false)),
 passo('Classe 0: marcar dano',w=>edita(w,'classe0.1',zero.funcoes_diretas.dano,true)),
 passo('entidade: pontos de dano (= 6)',w=>edita(w,'entidade.1.esp.1',esp.funcoes_diretas.dano,6)),
 passo('Família da entidade fechada',w=>amparo(w,['Normal','Fechada',...Array(11).fill('Normal')])),
 passo('entidade fechada: pontos de dano (= 7)',w=>edita(w,'entidade.1.esp.1',esp.funcoes_diretas.dano,7)),
 passo('entidade fechada: melhoria 1',w=>edita(w,'entidade.1.esp.1',esp.entradas_diretas.m1,'Alcance')),
];
// O caso medido no Google (pontos num cartão de Família aberta) perde a releitura e o Amparo.
const comum=tabela[0];eq(comum.antes-comum.depois,2);eq(comum.abas.includes(A.cfg.amparo.aba),true);
assert(tabela.every(t=>t.depois<=t.antes),'nenhum passo lê mais que antes');checks++;
if(process.argv.includes('--tabela'))console.table(tabela.map(t=>({passo:t.nome,leituras:t.antes+' → '+t.depois,'abas que saíram':t.abas.join(', ')})));
console.log(JSON.stringify({checks,resultado:'OK',escopo:tabela.length+' edições com o EditorR53 de antes e o de agora: mesmas abas, versões, propriedades e avisos; leituras '+comum.antes+' → '+comum.depois+' nos pontos de um cartão aberto'}));
