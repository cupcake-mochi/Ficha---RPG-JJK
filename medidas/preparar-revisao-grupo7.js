'use strict';
// Migração pontual da revisão 3b: não usa rede, não importa XLSX e não monta a ficha.
// Exige os backups nativos da rodada e o ABAS anterior. Preserva entradas por registro.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..'),evid=path.resolve(root,'../evidencias-3b');
const backup=JSON.parse(fs.readFileSync(path.join(evid,'correcao-grupo7-antes.json')));
const ctx={};vm.createContext(ctx);vm.runInContext(require('./carregar-ficha.js').fontes()+'\n'+fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8'),ctx);
const {deslocaFormula}=require('./sheets-de-mentira.js');
function expand(a){for(const [r,c,rr,cc]of a.abaixo||[])for(let j=c;j<=cc;j++){
 const base=a.vals.find(v=>v[0]===r&&v[1]===j);if(!base)throw Error('Fórmula-base ausente');
 for(let i=r+1;i<=rr;i++)if(!a.vals.some(v=>v[0]===i&&v[1]===j))a.vals.push([i,j,deslocaFormula(base[2],i-r,0),base[3]]);
}}
const before=JSON.parse(fs.readFileSync(path.join(evid,'layout-antes-correcao-grupo7.json'))),after=JSON.parse(JSON.stringify(ctx.ABAS));
before.forEach(expand);after.forEach(expand);
const B=Object.fromEntries(before.map(a=>[a.nome,a])),A=Object.fromEntries(after.map(a=>[a.nome,a]));
const live={};for(const obj of Object.values(backup))for(const s of obj.sheets||[])for(const d of s.data||[])for(const [r,row]of(d.rowData||[]).entries())for(const[c,cell]of(row.values||[]).entries())live[s.properties.title+'|'+((d.startRow||0)+r+1)+'|'+((d.startColumn||0)+c+1)]=cell;
const ids={'FICHA':1980633175,'CONFIGURAÇÃO':47001,'DADOS_PROGRESSAO':47006,'DADOS_CONFIG':47002,'ANALISE':1893369489};
const grid=(n,r,c,rr=r,cc=c)=>({sheetId:ids[n],startRowIndex:r-1,endRowIndex:rr,startColumnIndex:c-1,endColumnIndex:cc});
const pt=s=>{let quoted=false,out='';for(let i=0;i<s.length;i++){let c=s[i];if(c==='"'){if(quoted&&s[i+1]==='"'){out+='""';i++;continue;}quoted=!quoted;}if(!quoted&&c===',')c=';';else if(!quoted&&c==='.'&&/\d/.test(s[i-1]||'')&&/\d/.test(s[i+1]||''))c=',';out+=c;}return out;};
const uv=v=>v==null?{}:typeof v==='boolean'?{boolValue:v}:typeof v==='number'?{numberValue:v}:v.startsWith('=')?{formulaValue:pt(v)}:{stringValue:String(v).replace(/^'/,'')};
const rgb=h=>Object.fromEntries(['red','green','blue'].map((k,i)=>[k,parseInt(h.replace('#','').slice(i*2,i*2+2),16)/255]));
const groups={estrutura:[],painel:[],formulas:[],final:[]},guards=[],notes=[];
const canonical=v=>v?.formulaValue?{formulaValue:v.formulaValue.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g,'$1!')}:v||{};
const same=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b));
const get=(n,r,c)=>live[n+'|'+r+'|'+c]||{};
const single=(n,r,c,v)=>({updateCells:{range:grid(n,r,c),rows:[{values:[{userEnteredValue:v}]}],fields:'userEnteredValue'}});
function style(e){return {textFormat:{fontFamily:e[0],fontSize:e[1],...(e[2]?{foregroundColor:rgb(e[2])}:{}),bold:!!e[3],italic:!!e[7]},horizontalAlignment:e[4].toUpperCase(),verticalAlignment:(e[5]==='center'?'middle':e[5]).toUpperCase(),wrapStrategy:e[8]?'WRAP':'CLIP'};}
const weights={thin:'SOLID',medium:'SOLID_MEDIUM',thick:'SOLID_THICK',double:'DOUBLE',dotted:'DOTTED',dashed:'DASHED'};
function addr(n,s){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(s),num=t=>[...t].reduce((v,c)=>v*26+c.charCodeAt(0)-64,0);if(!m)throw Error(s);return grid(n,+m[2],num(m[1]),+(m[4]||m[2]),num(m[3]||m[1]));}
function panel(n,first,last,width){const a=A[n],id=ids[n];
 const rows=Array.from({length:last-first+1},()=>({values:Array.from({length:width},()=>({userEnteredFormat:{backgroundColor:rgb(a.fundo_base),textFormat:{fontFamily:a.padrao[0],fontSize:a.padrao[1],foregroundColor:rgb(a.padrao[2])}}}))}));
 for(const[r,c,v,e]of a.vals)if(r>=first&&r<=last&&c<=width)rows[r-first].values[c-1]={userEnteredValue:uv(v),userEnteredFormat:{...rows[r-first].values[c-1].userEnteredFormat,...style(a.estilos[e])}};
 for(const[r,c1,c2,color]of a.fundos)if(r>=first&&r<=last)for(let c=c1;c<=c2;c++)if(c<=width)rows[r-first].values[c-1].userEnteredFormat.backgroundColor=rgb(color);
 for(const[cell,note]of a.notas||[]){const g=addr(n,cell);if(g.startRowIndex>=first-1&&g.startRowIndex<last)rows[g.startRowIndex-first+1].values[g.startColumnIndex].note=note;}
 if(n==='FICHA'){
  const hex=x=>'#'+['red','green','blue'].map(k=>Math.round((x?.[k]||0)*255).toString(16).padStart(2,'0')).join('').toUpperCase();
  let bg=rows.map(row=>row.values.map(c=>hex(c.userEnteredFormat.backgroundColor))),fc=rows.map(row=>row.values.map(c=>hex(c.userEnteredFormat.textFormat.foregroundColor)));
  ctx.repintarCoresDaAba_({getSheetByName:()=>({getRange:()=>({getBackgrounds:()=>bg,getFontColors:()=>fc,setBackgrounds:v=>bg=v,setFontColors:v=>fc=v})})},ctx.ABAS.find(x=>x.nome===n),null,'Mizuki · Escuro · ameixa e rosa',[first,last]);
  rows.forEach((row,r)=>row.values.forEach((cell,c)=>{cell.userEnteredFormat.backgroundColor=rgb(bg[r][c]);cell.userEnteredFormat.textFormat.foregroundColor=rgb(fc[r][c]);}));
 }
 for(let i=0;i<rows.length;i+=5)groups.painel.push({updateCells:{start:{sheetId:id,rowIndex:first-1+i,columnIndex:0},rows:rows.slice(i,i+5),fields:'userEnteredValue,userEnteredFormat,note,dataValidation'}});
 for(const[r,c,rr,cc]of a.merges)if(r>=first&&rr<=last)groups.painel.push({mergeCells:{range:grid(n,r,c,rr,cc),mergeType:'MERGE_ALL'}});
 const borders=new Map();for(const[side,weight,color,ranges]of a.bordas||[])for(const range of ranges){const g=addr(n,range);if(g.startRowIndex<first-1||g.endRowIndex>last)continue;const k=JSON.stringify(g),item=borders.get(k)||{range:g};item[side]={style:weights[weight]||'SOLID',color:rgb(n==='FICHA'?'#B377BB':color)};borders.set(k,item);}
 groups.painel.push(...[...borders.values()].map(v=>({updateBorders:v})));
 for(const[c,r,num]of a.caixas||[])if(r>=first&&r<=last)groups.painel.push({setDataValidation:{range:grid(n,r,c,Math.min(r+num-1,last),c),rule:{condition:{type:'BOOLEAN'},strict:true,showCustomUi:true}}});
 for(const[cell,f]of a.dv||[]){const g=addr(n,cell);if(g.startRowIndex<first-1||g.endRowIndex>last)continue;groups.painel.push({setDataValidation:{range:g,rule:{condition:{type:'ONE_OF_RANGE',values:[{userEnteredValue:'='+f}]},strict:(a.menus_estritos||[]).includes(cell),showCustomUi:true}}});}
 return rows;
}
// Validate generated formulas before replacing them. Inputs are remapped separately.
for(const[n,a]of Object.entries(A)){if(!ids[n]||n==='FICHA')continue;
 const prev=new Map(B[n].vals.map(([r,c,v])=>[r+'|'+c,v]));
 for(const[r,c,v]of a.vals){if(n==='CONFIGURAÇÃO'&&r>=778&&r<=875)continue;
  const old=prev.get(r+'|'+c);if(same(uv(old),uv(v)))continue;
  const actual=get(n,r,c).userEnteredValue;
  if(!same(actual,uv(old)))throw Error('Guarda não corresponde: '+n+' '+r+','+c);
  guards.push({n,r,c,before:uv(old),after:uv(v)});groups.formulas.push(single(n,r,c,uv(v)));
 }
}
// The removed mirror contains generated formulas only. Keep all player inputs.
const oldFicha=new Map(B.FICHA.vals.map(([r,c,v])=>[r+'|'+c,v]));
for(const[k,cell]of Object.entries(live)){const [n,rr,cc]=k.split('|');if(n==='FICHA'&&+rr>=437&&cell.userEnteredValue&&!same(cell.userEnteredValue,uv(oldFicha.get(rr+'|'+cc))))throw Error('Conteúdo manual no bloco removido: '+rr+','+cc);}
groups.estrutura.push({updateSheetProperties:{properties:{sheetId:ids.DADOS_PROGRESSAO,gridProperties:{columnCount:81}},fields:'gridProperties.columnCount'}},
 {unmergeCells:{range:grid('FICHA',411,1,596,50)}},
 {unmergeCells:{range:grid('CONFIGURAÇÃO',778,1,875,16)}});
for(const[r,rr]of B['CONFIGURAÇÃO'].grupos?.lin||[])if(r>=778&&rr<=875)groups.estrutura.push({deleteDimensionGroup:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:r-1,endIndex:rr}}});
panel('FICHA',411,436,50);panel('CONFIGURAÇÃO',778,875,16);
const pack=JSON.parse(fs.readFileSync(path.join(evid,'progressao-em-integracao.json')));
for(const g of pack.linhas_ficha){const oldCol=g.tipo==='Perícia'?4:24,oldRow=412+g.n;
 for(const[key,offset]of [['treino',0],['especializacao',1],['nome',2],['atributo',10],['bonus',16]]){
  const source=get('FICHA',oldRow,oldCol+offset),value=source.userEnteredValue||{};
  if(key==='atributo'&&(g.tipo==='Perícia'||value.formulaValue))continue;
  const target=addr('FICHA',g[key]);groups.formulas.push(single('FICHA',target.startRowIndex+1,target.startColumnIndex+1,value));
  if(source.note)notes.push({source:[oldRow,oldCol+offset],target:g[key],note:source.note});
 }
}
for(const[typ,col,levels]of [['Caminho',2,[2,7,15,23,30]],['Trilha',10,[2,11,19,27]]]){
 levels.forEach((level,i)=>{for(const[oldRow,oldCol,newRow,newCol]of [[778+3*(level-1),col+1,778+3*i,col+1],[779+3*(level-1),col,779+3*i,col]]){
  groups.formulas.push(single('CONFIGURAÇÃO',newRow,newCol,get('CONFIGURAÇÃO',oldRow,oldCol).userEnteredValue||{}));
 }});
}
for(const note of notes){const g=addr('FICHA',note.target);groups.formulas.push({updateCells:{range:g,rows:[{values:[{note:note.note}]}],fields:'note'}});}
groups.final.push({copyPaste:{source:grid('FICHA',407,1,407,2),destination:grid('FICHA',408,1,436,2),pasteType:'PASTE_FORMAT',pasteOrientation:'NORMAL'}},
 {updateDimensionProperties:{range:{sheetId:ids.FICHA,dimension:'ROWS',startIndex:410,endIndex:436},properties:{pixelSize:25},fields:'pixelSize'}},
 {updateDimensionProperties:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:777,endIndex:875},properties:{pixelSize:25,hiddenByUser:false},fields:'pixelSize,hiddenByUser'}},
 {addDimensionGroup:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:792,endIndex:874}}},
 {updateDimensionGroup:{dimensionGroup:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:792,endIndex:874},depth:1,collapsed:true},fields:'collapsed'}},
 {updateDimensionProperties:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:792,endIndex:874},properties:{hiddenByUser:true},fields:'hiddenByUser'}},
 {deleteDimension:{range:{sheetId:ids.FICHA,dimension:'ROWS',startIndex:436,endIndex:596}}});
const out=path.join(evid,'correcao-grupo7-pedidos');fs.mkdirSync(out,{recursive:true});const manifest=[];
for(const[name,requests]of Object.entries(groups)){let chunk=[],size=0,i=0;const flush=()=>{if(chunk.length){const file=`${name}-${String(i++).padStart(3,'0')}.json`;fs.writeFileSync(path.join(out,file),JSON.stringify(chunk));manifest.push({grupo:name,file,pedidos:chunk.length});}chunk=[];size=0;};for(const r of requests){const len=JSON.stringify(r).length;if(chunk.length&&(size+len>60000||chunk.length>=150))flush();chunk.push(r);size+=len;}flush();}
fs.writeFileSync(path.join(evid,'correcao-grupo7-manifesto.json'),JSON.stringify({manifest,guards,notes},null,2));
console.log(JSON.stringify({groups:Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,v.length])),guards:guards.length,files:manifest.length}));
