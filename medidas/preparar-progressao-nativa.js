'use strict';
// Prepara a migração pontual 3b. Não faz chamadas de rede nem importa XLSX.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..'),out=path.resolve(root,'../evidencias-3b');
const ctx={};vm.createContext(ctx);vm.runInContext(require('./carregar-ficha.js').fontes(),ctx);
// O construir() preenche estes retângulos depois de ler o ABAS. A migração
// pontual precisa das linhas expandidas, não só da primeira fórmula do lote.
const {deslocaFormula}=require('./sheets-de-mentira.js');
function expandeAbaixo(a){for(const [r,c,rr,cc]of a.abaixo||[])for(let j=c;j<=cc;j++){
 const base=a.vals.find(v=>v[0]===r&&v[1]===j);if(!base)throw Error(`Sem fórmula-base ${a.nome} ${r},${j}`);
 for(let i=r+1;i<=rr;i++)if(!a.vals.some(v=>v[0]===i&&v[1]===j))a.vals.push([i,j,deslocaFormula(base[2],i-r,0),base[3]]);
}}
ctx.ABAS.forEach(expandeAbaixo);
const before=Object.fromEntries(JSON.parse(fs.readFileSync(path.join(out,'layout-parte3a.json'),'utf8')).map(a=>[a.nome,a]));
Object.values(before).forEach(expandeAbaixo);
const after=Object.fromEntries(ctx.ABAS.map(a=>[a.nome,a]));
const ids={'CARTEIRA':1384316560,'FICHA':1980633175,'FICHA PESSOAL':913591496,'FICHA AMALDIÇOADA':1449473752,'INVOCAÇÕES':161192554,'DADOS':1430425982,'DADOS_AM':1201840268,'DADOS_INVOC':1471151297,'DADOS_CONFIG':47002,'CONFIGURAÇÃO':47001,'ANALISE':1893369489,'DADOS_CUSTOM':47004,'DADOS_PROGRESSAO':47006};
const col=s=>[...s].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0);
function letters(n){let s='';while(n){const r=(n-1)%26;s=String.fromCharCode(65+r)+s;n=Math.floor((n-1)/26);}return s;}
function grid(id,r,c,rr=r,cc=c){return {sheetId:id,startRowIndex:r-1,endRowIndex:rr,startColumnIndex:c-1,endColumnIndex:cc};}
function range(id,s){const m=/^\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?$/.exec(s);if(!m)throw Error(s);return grid(id,+m[2],col(m[1]),+(m[4]||m[2]),col(m[3]||m[1]));}
function pt(v){let quoted=false,out='';for(let i=0;i<v.length;i++){let c=v[i];if(c==='"'){if(quoted&&v[i+1]==='"'){out+='""';i++;continue;}quoted=!quoted;}if(!quoted&&c===',')c=';';else if(!quoted&&c==='.'&&/\d/.test(v[i-1]||'')&&/\d/.test(v[i+1]||''))c=',';out+=c;}return out;}
const uv=v=>v==null?{}:typeof v==='boolean'?{boolValue:v}:typeof v==='number'?{numberValue:v}:v.startsWith('=')?{formulaValue:pt(v)}:{stringValue:String(v).replace(/^'/,'')};
const rgb=h=>Object.fromEntries(['red','green','blue'].map((k,i)=>[k,parseInt(h.replace('#','').slice(i*2,i*2+2),16)/255]));
const groups={estrutura:[],dados:[],painel:[],contas:[],menus:[],contrato:[]};
const guards=[],menus=[];
function byCell(a){return Object.fromEntries(a.vals.map(([r,c,v])=>[letters(c)+r,v]));}
function style(e){return {textFormat:{fontFamily:e[0],fontSize:e[1],...(e[2]?{foregroundColor:rgb(e[2])}:{}),bold:!!e[3],italic:!!e[7]},horizontalAlignment:e[4].toUpperCase(),verticalAlignment:(e[5]==='center'?'middle':e[5]).toUpperCase(),wrapStrategy:e[8]?'WRAP':'CLIP'};}
function rule(f,strict=false){const list=f.startsWith('"');return {condition:{type:list?'ONE_OF_LIST':'ONE_OF_RANGE',values:list?f.slice(1,-1).split(',').map(userEnteredValue=>({userEnteredValue})):[{userEnteredValue:'='+f}]},strict,showCustomUi:true};}
for(const n of ['CONFIGURAÇÃO','FICHA','DADOS_CONFIG','ANALISE'])groups.estrutura.push({updateSheetProperties:{properties:{sheetId:ids[n],gridProperties:{rowCount:Math.max(before[n].rows,after[n].rows)}},fields:'gridProperties.rowCount'}});
groups.estrutura.push({addSheet:{properties:{sheetId:ids.DADOS_PROGRESSAO,title:'DADOS_PROGRESSAO',hidden:true,gridProperties:{rowCount:after.DADOS_PROGRESSAO.rows,columnCount:after.DADOS_PROGRESSAO.cols,hideGridlines:true}}}});
const prog=after.DADOS_PROGRESSAO;
for(let r=1;r<=prog.rows;r++){
 const vs=prog.vals.filter(v=>v[0]===r).sort((a,b)=>a[1]-b[1]);if(!vs.length)continue;
 const c=vs[0][1],values=Array.from({length:vs.at(-1)[1]-c+1},()=>({}));
 for(const [,cc,v]of vs)values[cc-c]={userEnteredValue:uv(v)};
 groups.dados.push({updateCells:{start:{sheetId:ids.DADOS_PROGRESSAO,rowIndex:r-1,columnIndex:c-1},rows:[{values}],fields:'userEnteredValue'}});
}
const weights={thin:'SOLID',medium:'SOLID_MEDIUM',thick:'SOLID_THICK',double:'DOUBLE',dotted:'DOTTED',dashed:'DASHED'};
for(const [n,first]of [['CONFIGURAÇÃO',733],['FICHA',410]]){
 const a=after[n],id=ids[n],width=n==='CONFIGURAÇÃO'?16:50;
 groups.painel.push({repeatCell:{range:grid(id,first,1,a.rows,width),cell:{userEnteredFormat:{backgroundColor:rgb(a.fundo_base),textFormat:{fontFamily:a.padrao[0],fontSize:a.padrao[1],foregroundColor:rgb(a.padrao[2])}}},fields:'userEnteredFormat'}},
 {updateDimensionProperties:{range:{sheetId:id,dimension:'ROWS',startIndex:first-1,endIndex:a.rows},properties:{pixelSize:25},fields:'pixelSize'}});
 const baseFormat={backgroundColor:rgb(a.fundo_base),textFormat:{fontFamily:a.padrao[0],fontSize:a.padrao[1],foregroundColor:rgb(a.padrao[2])}};
 const rows=Array.from({length:a.rows-first+1},()=>({values:Array.from({length:width},()=>({userEnteredFormat:baseFormat}))}));
 for(const [r,c,v,e]of a.vals)if(r>=first)rows[r-first].values[c-1]={userEnteredValue:uv(v),userEnteredFormat:{...baseFormat,...style(a.estilos[e])}};
 for(const [r,c1,c2,hex]of a.fundos)if(r>=first)for(let c=c1;c<=c2;c++){
  const cell=rows[r-first].values[c-1];cell.userEnteredFormat={...(cell.userEnteredFormat||{}),backgroundColor:rgb(hex)};
 }
 for(const [cell,note]of a.notas||[]){const g=range(id,cell);if(g.startRowIndex>=first-1)rows[g.startRowIndex-first+1].values[g.startColumnIndex].note=note;}
 for(let i=0;i<rows.length;i+=4)groups.painel.push({updateCells:{start:{sheetId:id,rowIndex:i+first-1,columnIndex:0},rows:rows.slice(i,i+4),fields:'userEnteredValue,userEnteredFormat,note'}});
 for(const [r,c,rr,cc]of a.merges)if(r>=first)groups.painel.push({mergeCells:{range:grid(id,r,c,rr,cc),mergeType:'MERGE_ALL'}});
 const borders=new Map();for(const [side,weight,hex,ranges]of a.bordas||[])for(const addr of ranges){const g=range(id,addr);if(g.startRowIndex<first-1)continue;const k=JSON.stringify(g),v=borders.get(k)||{range:g};v[side]={style:weights[weight]||'SOLID',color:rgb(hex)};borders.set(k,v);}
 for(const v of borders.values())groups.painel.push({updateBorders:v});
 for(const [c,r,num]of a.caixas||[])if(r>=first)groups.menus.push({setDataValidation:{range:grid(id,r,c,r+num-1,c),rule:{condition:{type:'BOOLEAN'},strict:true,showCustomUi:true}}});
 for(const [r,rr,collapsed,depth]of a.grupos?.lin||[])if(r>=first){
  groups.painel.push({addDimensionGroup:{range:{sheetId:id,dimension:'ROWS',startIndex:r-1,endIndex:rr}}});
  if(collapsed)groups.painel.push({updateDimensionGroup:{dimensionGroup:{range:{sheetId:id,dimension:'ROWS',startIndex:r-1,endIndex:rr},depth,collapsed:true},fields:'collapsed'}});
 }
}
for(const [n,a]of Object.entries(after)){
 if(!before[n]||n==='ANALISE')continue;
 const prev=byCell(before[n]);
 for(const [r,c,v]of a.vals){
  if(n==='CONFIGURAÇÃO'&&r>=733||n==='FICHA'&&r>=410)continue;
  const coord=letters(c)+r,b=prev[coord]??null;if(JSON.stringify(b)===JSON.stringify(v??null))continue;
  guards.push({sheet:n,coord,before:uv(b),after:uv(v)});
  groups.contas.push({updateCells:{range:grid(ids[n],r,c),rows:[{values:[{userEnteredValue:uv(v)}]}],fields:'userEnteredValue'}});
 }
 const dv=new Map((before[n].dv||[]).map(d=>[d[0],d[1]]));
 for(const [addr,f]of a.dv||[])if(f!==dv.get(addr)){
  menus.push({sheet:n,coord:addr,before:dv.get(addr)??null,after:f});
  groups.menus.push({setDataValidation:{range:range(ids[n],addr),rule:rule(f,(a.menus_estritos||[]).includes(addr))}});
 }
}
const ac=after.ANALISE,oldLast=Math.max(...before.ANALISE.vals.filter(v=>v[1]===1&&v[2]).map(v=>v[0]));
groups.contrato.push({updateCells:{start:{sheetId:ids.ANALISE,rowIndex:1,columnIndex:1},rows:[{values:[{userEnteredValue:{stringValue:'6'}}]}],fields:'userEnteredValue'}});
for(let r=oldLast+1;r<=ac.rows;r+=15){const rows=[];for(let rr=r;rr<=Math.min(r+14,ac.rows);rr++){const values=Array.from({length:4},()=>({}));for(const [,c,v]of ac.vals.filter(v=>v[0]===rr))values[c-1]={userEnteredValue:uv(v)};rows.push({values});}groups.contrato.push({updateCells:{start:{sheetId:ids.ANALISE,rowIndex:r-1,columnIndex:0},rows,fields:'userEnteredValue'}});}
const dest=path.join(out,'pedidos-nativos');fs.mkdirSync(dest,{recursive:true});
const manifest=[];
for(const [name,requests]of Object.entries(groups)){
 let chunk=[],size=0,i=0;const flush=()=>{if(chunk.length){const file=`${name}-${String(i++).padStart(3,'0')}.json`;fs.writeFileSync(path.join(dest,file),JSON.stringify(chunk));manifest.push({grupo:name,file,pedidos:chunk.length});}chunk=[];size=0;};
 for(const r of requests){const n=JSON.stringify(r).length;if(chunk.length&&(size+n>60000||chunk.length>=200))flush();chunk.push(r);size+=n;}flush();
}
fs.writeFileSync(path.join(out,'manifesto-nativo.json'),JSON.stringify(manifest));
fs.writeFileSync(path.join(out,'guardas-nativas.json'),JSON.stringify({ids,guards,menus},null,2));
console.log(JSON.stringify({guardas:guards.length,menus:menus.length,grupos:Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,v.length]))}));
