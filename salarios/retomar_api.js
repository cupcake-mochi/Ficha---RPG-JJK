'use strict';
// Retomada de uma instalação interrompida: somente duas abas novas e ainda vazias.
// A fonte é uma leitura nativa da cópia ensaiada; snapshots ficam fora do Git.
const fs=require('fs'),path=require('path'),assert=require('assert');
const dir=path.join(__dirname,'saidas'),source=JSON.parse(fs.readFileSync(path.join(dir,'retomada-fonte.json'),'utf8')).updatedSpreadsheet;
const before=JSON.parse(fs.readFileSync(path.join(dir,'retomada-oficial-antes.json'),'utf8'));
const ids={CONFIGURAÇÃO:1364162823,CARTEIRA:946642491,'FICHA PESSOAL':994525406,DADOS_SALARIOS:119828827,'SALÁRIOS':1985872561};
const tabs=Object.fromEntries(source.sheets.map(s=>[s.properties.title,s]));
function cells(s){let map=new Map();for(const d of s.data||[])for(let r=0;r<(d.rowData||[]).length;r++)for(let c=0;c<(d.rowData[r].values||[]).length;c++)map.set(((d.startRow||0)+r)+','+((d.startColumn||0)+c),d.rowData[r].values[c]);return map;}
const maps=Object.fromEntries(Object.entries(tabs).map(([n,s])=>[n,cells(s)]));
for(const s of before.sheets.filter(s=>['DADOS_SALARIOS','SALÁRIOS'].includes(s.properties.title)))assert([...cells(s).values()].every(c=>!c.userEnteredValue),'Aba parcial preenchida; não sobrescrever.');
let grade='';const personal=before.sheets.find(s=>s.properties.title==='FICHA PESSOAL');
for(const [k,c]of cells(personal)){if(k==='10,27')grade=c.effectiveValue?.stringValue||c.userEnteredValue?.stringValue||'';else assert(!c.userEnteredValue,'Há missões anteriores; faça a importação de datas pendentes explicitamente.');}
const grades=['Grau 4','Grau 3','Grau 2','Grau 1','Especial'];assert(grades.includes(grade));
const day=Math.floor(maps['CONFIGURAÇÃO'].get('322,6').userEnteredValue.numberValue);
assert(day===46315,'Releia a fonte e revise a data de emissão.');
const req=[];
const grid=(name,r,c,h=1,w=1)=>({sheetId:ids[name],startRowIndex:r,endRowIndex:r+h,startColumnIndex:c,endColumnIndex:c+w});
function safeCell(c){let o={};for(const k of ['userEnteredValue','userEnteredFormat','note','dataValidation'])if(c?.[k]!==undefined)o[k]=c[k];return JSON.parse(JSON.stringify(o));}
function put(name,r,c,value,fields='userEnteredValue'){req.push({updateCells:{range:grid(name,r,c),rows:[{values:[value]}],fields}});}
function matrix(name,r,c,h,w){req.push({updateCells:{range:grid(name,r,c,h,w),rows:Array.from({length:h},(_,i)=>({values:Array.from({length:w},(_,j)=>safeCell(maps[name].get((r+i)+','+(c+j))))})),fields:'userEnteredValue,userEnteredFormat,note,dataValidation'}});}
for(const range of [grid('CONFIGURAÇÃO',319,2,36,15),grid('CONFIGURAÇÃO',31,14,2,3)])req.push({unmergeCells:{range}});
matrix('CONFIGURAÇÃO',319,2,36,15);matrix('CONFIGURAÇÃO',31,14,2,3);
for(const m of tabs['CONFIGURAÇÃO'].merges||[])if((m.startRowIndex>=319&&m.endRowIndex<=355&&m.startColumnIndex>=2&&m.endColumnIndex<=17)||(m.startRowIndex===31&&m.endRowIndex===33&&m.startColumnIndex===14&&m.endColumnIndex===17))req.push({mergeCells:{range:{...m,sheetId:ids['CONFIGURAÇÃO']},mergeType:'MERGE_ALL'}});
for(const d of tabs['CONFIGURAÇÃO'].data)if(d.startRow===319)for(let i=0;i<36;i++)req.push({updateDimensionProperties:{range:{sheetId:ids['CONFIGURAÇÃO'],dimension:'ROWS',startIndex:319+i,endIndex:320+i},properties:{pixelSize:d.rowMetadata[i].pixelSize},fields:'pixelSize'}});
for(const [r,v]of [[323,day],[324,false],[325,true],[331,'Aguardando o nome do personagem na CARTEIRA.'],[333,day+30],[348,day],[349,0],[350,150000*Math.pow(2,grades.indexOf(grade))*.25],[351,'Nenhum'],[353,'Ao abrir ou editar a ficha']])put('CONFIGURAÇÃO',r-1,6,{userEnteredValue:typeof v==='number'?{numberValue:v}:typeof v==='boolean'?{boolValue:v}:{stringValue:v}});
for(const name of ['SALÁRIOS','DADOS_SALARIOS'])matrix(name,0,0,1,12);
put('DADOS_SALARIOS',1,11,{userEnteredValue:{stringValue:JSON.stringify({versao:1,inicio:day,graus:[[day,grade]],ultimaEmissao:day})}});
req.push({updateSheetProperties:{properties:{sheetId:ids.DADOS_SALARIOS,hidden:true},fields:'hidden'}});
for(const [c,w]of [[0,3],[5,1]])req.push({repeatCell:{range:grid('DADOS_SALARIOS',0,c,1000,w),cell:{userEnteredFormat:{numberFormat:{type:'TEXT',pattern:'@'}}},fields:'userEnteredFormat.numberFormat'}});
req.push({updateSheetProperties:{properties:{sheetId:ids['SALÁRIOS'],gridProperties:{frozenRowCount:1,hideGridlines:true}},fields:'gridProperties.frozenRowCount,gridProperties.hideGridlines'}});
req.push({updateDimensionProperties:{range:{sheetId:ids['SALÁRIOS'],dimension:'ROWS',startIndex:0,endIndex:1},properties:{pixelSize:50},fields:'pixelSize'}});
for(const [c,end,width]of [[0,12,135],[0,1,210],[10,11,260]])req.push({updateDimensionProperties:{range:{sheetId:ids['SALÁRIOS'],dimension:'COLUMNS',startIndex:c,endIndex:end},properties:{pixelSize:width},fields:'pixelSize'}});
req.push({updateDimensionProperties:{range:{sheetId:ids['SALÁRIOS'],dimension:'COLUMNS',startIndex:11,endIndex:12},properties:{hiddenByUser:true},fields:'hiddenByUser'}});
for(const [c,w,format]of [[1,3,{type:'DATE',pattern:'dd/mm/yyyy'}],[5,1,{type:'NUMBER',pattern:'"¥ "#,##0'}],[8,1,{type:'PERCENT',pattern:'0%'}],[9,1,{type:'NUMBER',pattern:'"¥ "#,##0'}]])req.push({repeatCell:{range:grid('SALÁRIOS',1,c,999,w),cell:{userEnteredFormat:{numberFormat:format}},fields:'userEnteredFormat.numberFormat'}});
req.push({addProtectedRange:{protectedRange:{range:grid('SALÁRIOS',0,0,1000,11),description:'Histórico fechado de salários; evite alterar pagamentos manualmente.',warningOnly:true}}});
put('CARTEIRA',2,33,{userEnteredValue:maps.CARTEIRA.get('2,33').userEnteredValue});
for(const c of [14,22])put('FICHA PESSOAL',84,c,{userEnteredValue:maps['FICHA PESSOAL'].get('84,'+c).userEnteredValue});
put('FICHA PESSOAL',85,14,{note:maps['FICHA PESSOAL'].get('85,14').note},'note');
const total=maps['FICHA PESSOAL'].get('85,22');put('FICHA PESSOAL',85,22,{userEnteredValue:total.userEnteredValue,note:total.note,userEnteredFormat:{numberFormat:total.userEnteredFormat.numberFormat}},'userEnteredValue,note,userEnteredFormat.numberFormat');
// O saldo manual nunca integra um pedido de escrita de valor.
assert(!req.some(x=>x.updateCells?.range?.sheetId===ids['FICHA PESSOAL']&&x.updateCells.range.startRowIndex===85&&x.updateCells.range.startColumnIndex===14&&x.updateCells.fields.includes('userEnteredValue')));
for(const r of req){assert(Object.keys(r).length===1);if(r.updateCells){const q=r.updateCells;assert(q.rows.length===q.range.endRowIndex-q.range.startRowIndex);assert(q.rows.every(v=>v.values.length===q.range.endColumnIndex-q.range.startColumnIndex));}}
fs.writeFileSync(path.join(dir,'retomada-pedidos.json'),JSON.stringify(req));console.log(JSON.stringify({resultado:'OK',pedidos:req.length,grau:grade,data:day,saldo_manual_preservado:true}));
