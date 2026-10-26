'use strict';
// Caminho e Trilha escolhidos em sequência rápida: a Trilha escolhida enquanto a
// execução do Caminho ainda calcula tem de sobreviver, com as cartas dela.
const vm=require('vm'),assert=require('assert'),{gerar}=require('../caminho_leve');
const d=gerar(),raw={};vm.createContext(raw);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),raw);
let checks=0;const eq=(a,b,m)=>{assert.deepStrictEqual(a,b,m);checks++;};
function pos(a){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a.replace(/\$/g,''));assert(m,a);const c=s=>[...s].reduce((n,x)=>n*26+x.charCodeAt(0)-64,0);return[+m[2],c(m[1]),+(m[4]||m[2]),c(m[3]||m[1])];}
// Leituras de primeiro nível, por aba: o retrato da R53_EVENTOS lê as outras abas por dentro.
let fundo=0;const leituras=[];
class Range{
 constructor(sh,r,c,nr=1,nc=1){Object.assign(this,{sh,r,c,nr,nc});}getRow(){return this.r;}getColumn(){return this.c;}getLastRow(){return this.r+this.nr-1;}getLastColumn(){return this.c+this.nc-1;}getNumRows(){return this.nr;}getNumColumns(){return this.nc;}getSheet(){return this.sh;}getCell(r,c){return new Range(this.sh,this.r+r-1,this.c+c-1);}
 getA1Notation(){let c=this.c,s='';while(c){let i=(c-1)%26;s=String.fromCharCode(65+i)+s;c=Math.floor((c-1)/26);}return s+this.r;}
 getValues(){if(!fundo)leituras.push(this.sh.name);fundo++;try{return Array.from({length:this.nr},(_,y)=>Array.from({length:this.nc},(_,x)=>this.sh.name==='R53_EVENTOS'&&this.c+x===2&&this.r+y>1?(()=>{let label=this.sh.cells.get(`${this.r+y},1`),i=label.lastIndexOf('!');return this.sh.book.get(label.slice(0,i)).getRange(label.slice(i+1)).getValue();})():(this.sh.cells.get(`${this.r+y},${this.c+x}`)??'')));}finally{fundo--;}}
 getValue(){return this.getValues()[0][0];}getNotes(){return Array.from({length:this.nr},(_,y)=>Array.from({length:this.nc},(_,x)=>this.sh.notes.get(`${this.r+y},${this.c+x}`)||''));}
 setValues(v){v.forEach((row,y)=>row.forEach((x,z)=>this.sh.cells.set(`${this.r+y},${this.c+z}`,x)));return this;}setValue(v){return this.setValues([[v]]);}setNote(v){this.sh.notes.set(`${this.r},${this.c}`,v);return this;}setRichTextValue(v){return this.setValue(v.text);}
}
class Sheet{
 constructor(s,book){this.book=book;this.name=s.nome;this.rows=s.rows;this.cols=s.cols;this.cells=new Map;this.notes=new Map;this.alturas=new Map;for(const[r,c,v]of s.vals)this.cells.set(`${r},${c}`,typeof v==='string'&&v.startsWith('=')?'':v);}
 getName(){return this.name;}getDataRange(){return new Range(this,1,1,this.rows,this.cols);}getRange(a,c,nr,nc){if(typeof a==='string'){let[r,col,rr,cc]=pos(a);return new Range(this,r,col,rr-r+1,cc-col+1);}return new Range(this,a,c,nr,nc);}
 getRangeList(ps){return{setValue:v=>ps.forEach(p=>this.getRange(p).setValue(v)),setNote:v=>ps.forEach(p=>this.getRange(p).setNote(v))};}setRowHeights(r,n,h){for(let i=0;i<n;i++)this.alturas.set(r+i,h);}
}
const atual={};
function planilha(){const book=new Map;raw.ABAS.forEach(s=>book.set(s.nome,new Sheet(s,book)));atual.ss={getSheetByName:n=>book.get(n),toast:()=>{}};book.get('FICHA').getRange('N11').setValue('Escolha sua Trilha');return atual.ss;}
const box={SpreadsheetApp:{getActive:()=>atual.ss,newTextStyle:()=>({setBold(){return this;},build(){return{};}}),newRichTextValue:()=>({setText(t){this.text=t;return this;},setTextStyle(){return this;},build(){return this;}})}};
vm.createContext(box);vm.runInContext(d.code.replace('return {editar:function(e){','var module={editar:function(e){'),box);
const ed=(ss,a1,v,o)=>{const f=ss.getSheetByName('FICHA');f.getRange(a1).setValue(v);box.module.editar({source:ss,range:f.getRange(a1),value:v,oldValue:o});};
// Tudo o que as regras do Caminho e da Trilha escrevem.
const estado=ss=>JSON.stringify(['FICHA','FICHA PESSOAL','DADOS_PROGRESSAO'].map(n=>{const s=ss.getSheetByName(n);return[[...s.cells].sort(),[...s.notes].sort(),[...s.alturas].sort()];}));
const trilhaCartas=ss=>[...box.cartasDaDadosAm_(ss).cartas].filter(c=>c.fonte==='Trilha').map(c=>ss.getSheetByName('FICHA').getRange(c.nome).getValue());
// A execução do Caminho tira o retrato; o jogador escolhe a Trilha antes de ela terminar.
function durante(acao){const original=box.r53FilaSnapshotCaminho_;box.r53FilaSnapshotCaminho_=function(real,seed){const f=original(real,seed),grava=f.grava;let uma=true;f.grava=function(a){if(uma){uma=false;acao();}return grava.call(this,a);};f.aplicar=(aplicar=>function(){try{return aplicar.apply(this,arguments);}finally{box.r53FilaSnapshotCaminho_=original;}})(f.aplicar);return f;};}

for(const [de,tri,para,nova] of [['Emanador','Ressonante','Bastião','Muro'],['Incursor','Sombra','Vanguarda','Estocada'],['Bastião','Muro','Incursor','Pugilista']]){
 // Referência: uma escolha de cada vez.
 let ss=planilha();ed(ss,'D11',de,'');ed(ss,'N11',tri,'Escolha sua Trilha');ed(ss,'D11',para,de);
 eq(ss.getSheetByName('FICHA').getRange('N11').getValue(),'Escolha sua Trilha',`${para}: a Trilha de ${de} é limpa`);
 ed(ss,'N11',nova,'Escolha sua Trilha');const esperado=estado(ss);
 eq(trilhaCartas(ss).every(Boolean),true,`${nova}: cartas da Trilha escritas`);
 // Corrida: a Trilha entra e termina enquanto o Caminho ainda calcula.
 ss=planilha();ed(ss,'D11',de,'');ed(ss,'N11',tri,'Escolha sua Trilha');
 durante(()=>ed(ss,'N11',nova,tri));leituras.length=0;ed(ss,'D11',para,de);
 eq(ss.getSheetByName('FICHA').getRange('N11').getValue(),nova,`${para}+${nova}: a Trilha nova fica`);
 eq(estado(ss),esperado,`${para}+${nova}: corrida igual à sequência`);
}
// Sem corrida, a única leitura a mais é a da Trilha, e só quando ela vai ser limpa.
let ss=planilha();ed(ss,'D11','Emanador','');ed(ss,'N11','Ressonante','Escolha sua Trilha');
leituras.length=0;ed(ss,'D11','Bastião','Emanador');eq(leituras.filter(n=>n==='FICHA').length,1,'troca com Trilha: relê a Trilha uma vez');
eq(trilhaCartas(ss),['','','',''],'troca com Trilha: cartas da Trilha antiga apagadas');
ss=planilha();leituras.length=0;ed(ss,'D11','Emanador','');eq(leituras.filter(n=>n==='FICHA').length,0,'personagem novo: nenhuma leitura a mais');
ss=planilha();ed(ss,'D11','Emanador','');ed(ss,'N11','Ressonante','Escolha sua Trilha');
leituras.length=0;ed(ss,'D11','Emanador','Emanador');eq(leituras.filter(n=>n==='FICHA').length,0,'mesmo Caminho: Trilha compatível, nenhuma leitura a mais');
eq(ss.getSheetByName('FICHA').getRange('N11').getValue(),'Ressonante','mesmo Caminho: Trilha mantida');
console.log(JSON.stringify({checks,resultado:'OK',escopo:'Trilha escolhida durante a execução do Caminho em três trocas, releitura só ao limpar; simulação não mede Google.'}));
