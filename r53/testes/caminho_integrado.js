'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),{gerar}=require('../caminho_leve');
const d=gerar(),raw={};vm.createContext(raw);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),raw);
let checks=0;const io=[];const eq=(a,b)=>{assert.deepStrictEqual(a,b);checks++;};
function pos(a){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a.replace(/\$/g,''));assert(m,a);const c=s=>[...s].reduce((n,x)=>n*26+x.charCodeAt(0)-64,0);return[+m[2],c(m[1]),+(m[4]||m[2]),c(m[3]||m[1])];}
class Range{
 constructor(sh,r,c,nr=1,nc=1){Object.assign(this,{sh,r,c,nr,nc});}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}getSheet(){return this.sh;}getCell(r,c){return new Range(this.sh,this.r+r-1,this.c+c-1);}
 getA1Notation(){let c=this.c,s='';while(c){let i=(c-1)%26;s=String.fromCharCode(65+i)+s;c=Math.floor((c-1)/26);}return s+this.r;}
 getValues(){io.push('read');return Array.from({length:this.nr},(_,y)=>Array.from({length:this.nc},(_,x)=>this.sh.name==='R53_EVENTOS'&&this.c+x===2&&this.r+y>1?(()=>{let label=this.sh.cells.get(`${this.r+y},1`),i=label.lastIndexOf('!');return sheets.get(label.slice(0,i)).getRange(label.slice(i+1)).getValue();})():(this.sh.cells.get(`${this.r+y},${this.c+x}`)??'')));}getValue(){return this.getValues()[0][0];}getNotes(){io.push('read');return Array.from({length:this.nr},(_,y)=>Array.from({length:this.nc},(_,x)=>this.sh.notes.get(`${this.r+y},${this.c+x}`)||''));}
 setValues(v){io.push('write');v.forEach((row,y)=>row.forEach((x,z)=>this.sh.cells.set(`${this.r+y},${this.c+z}`,x)));return this;}setValue(v){return this.setValues([[v]]);}setNote(v){io.push('write');this.sh.notes.set(`${this.r},${this.c}`,v);return this;}setRichTextValue(v){return this.setValue(v.text);}
}
class Sheet{
 constructor(s){this.name=s.nome;this.rows=s.rows;this.cols=s.cols;this.cells=new Map;this.notes=new Map;for(const[r,c,v]of s.vals)this.cells.set(`${r},${c}`,typeof v==='string'&&v.startsWith('=')?'':v);}
 getName(){return this.name;}getDataRange(){return new Range(this,1,1,this.rows,this.cols);}getRange(a,c,nr,nc){if(typeof a==='string'){let[r,col,rr,cc]=pos(a);return new Range(this,r,col,rr-r+1,cc-col+1);}return new Range(this,a,c,nr,nc);}getRangeList(ps){return{setValue:v=>ps.forEach(p=>this.getRange(p).setValue(v)),setNote:v=>ps.forEach(p=>this.getRange(p).setNote(v))};}setRowHeights(){}
}
const sheets=new Map(raw.ABAS.map(s=>[s.nome,new Sheet(s)]));const ss={getSheetByName:n=>sheets.get(n),toast:()=>{}};
const box={SpreadsheetApp:{getActive:()=>ss,newTextStyle:()=>({setBold(){return this;},build(){return{};}}),newRichTextValue:()=>({setText(t){this.text=t;return this;},setTextStyle(){return this;},build(){return this;}})}};
vm.createContext(box);vm.runInContext(d.code.replace('return {editar:function(e){','var module={editar:function(e){'),box);
const ficha=sheets.get('FICHA'),progressao=sheets.get('DADOS_PROGRESSAO');ficha.getRange('N11').setValue('Escolha sua Trilha');
const cat=JSON.parse(fs.readFileSync('catalogo-projeto-m.json','utf8'));let old='';
function editar(e){io.length=0;box.module.editar(e);const first=io.indexOf('write');if(first>=0)eq(io.slice(first).includes('read'),false);}
for(const path of Object.keys(cat.caminhos)){
 ficha.getRange('D11').setValue(path);editar({source:ss,range:ficha.getRange('D11'),value:path,oldValue:old});
 for(const name of cat.caminhos[path].pericias_fixas){let place=raw.ABAS.find(s=>s.nome==='FICHA').vals.find(t=>t[2]===name);eq(ficha.getRange(place[0],place[1]-2).getValue(),true);}
 const card=box.cartasDaDadosAm_(ss).cartas[0],expected=box.HABILIDADES_DO_LIVRO_.find(h=>h.fonte==='Caminho'&&h.dono===path&&h.nivel===card.nivel);
 eq(ficha.getRange(card.nome).getValue(),expected.nome);eq(ficha.getRange(card.texto).getValue(),expected.texto);old=path;
}
const card=box.cartasDaDadosAm_(ss).cartas[0];ficha.getRange(card.texto).setValue('Texto pessoal que deve ficar.');ficha.getRange('D11').setValue('Guia');box.module.editar({source:ss,range:ficha.getRange('D11'),value:'Guia',oldValue:old});eq(ficha.getRange(card.texto).getValue(),'Texto pessoal que deve ficar.');assert(ficha.getRange(card.texto).getNotes()[0][0].length>0);checks++;
const pessoal=sheets.get('FICHA PESSOAL'),tables=box.caixasDeTreino_(box.R53_CAMINHO_DADOS_),group=tables.grupos[0],children=tables.armas.filter(a=>a.categoria===group.categoria);
for(const state of [false,true,false]){pessoal.getRange(group.caixa).setValue(state);box.module.editar({source:ss,range:pessoal.getRange(group.caixa),value:String(state).toUpperCase()});for(const child of children)eq(pessoal.getRange(child.caixa).getValue(),state);}
pessoal.getRange(group.caixa).setValue(true);box.module.editar({source:ss,range:pessoal.getRange(group.caixa)});pessoal.getRange(children[0].caixa).setValue(false);box.module.editar({source:ss,range:pessoal.getRange(children[0].caixa)});eq(pessoal.getRange(group.caixa).getValue(),false);
// Caminho e perícia custom usam as definições nativas, sem fixar uma cópia do catálogo.
progressao.getRange('M8:V8').setValues([['Caminho QA','Essência',8,5,5,'Arte QA','Percepção',8,'Não','Todas']]);progressao.getRange('K7').setValue(1);progressao.getRange('K8').setValue(0);progressao.getRange('AV2').setValue('Arte QA');progressao.getRange('BD2').setValue('F439');progressao.getRange('BE2:BH2').setValues([['Caminho',2,'Pulso QA','Texto de habilidade custom.']]);
ficha.getRange(card.texto).setValue('');ficha.getRange('D11').setValue('Caminho QA');box.module.editar({source:ss,range:ficha.getRange('D11'),value:'Caminho QA',oldValue:'Guia'});
eq(ficha.getRange('F439').getValue(),'Arte QA');eq(ficha.getRange('D439').getValue(),true);eq(ficha.getRange(card.nome).getValue(),'Pulso QA');eq(ficha.getRange(card.texto).getValue(),'Texto de habilidade custom.');
console.log(JSON.stringify({checks,resultado:'OK',escopo:'Seis Caminhos completos, texto manual preservado e ida/volta do treino de armas; simulação não mede Google.'}));
