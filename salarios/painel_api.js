'use strict';
// Usa o mesmo autor do painel Apps Script para preparar a migração nativa atômica.
const fs=require('fs'),vm=require('vm');
const config=1364162823,carteira=946642491,ledger=1985872561;
const cells=new Map(),merges=[],sizes=new Map();
function col(s){return [...s].reduce((n,c)=>26*n+c.charCodeAt(0)-64,0);}
class Range {
 constructor(sh,a,b,h=1,w=1){if(typeof a==='string'){const m=/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a);this.r=+m[2];this.c=col(m[1]);this.h=m[4]?+m[4]-this.r+1:1;this.w=m[3]?col(m[3])-this.c+1:1;}else Object.assign(this,{r:a,c:b,h,w});this.sh=sh;}
 each(fn){for(let i=0;i<this.h;i++)for(let j=0;j<this.w;j++){const key=[this.sh,this.r+i,this.c+j].join(':');if(!cells.has(key))cells.set(key,{});fn(cells.get(key));}return this;}
 merge(){if(this.h*this.w>1)merges.push({sheetId:this.sh,startRowIndex:this.r-1,endRowIndex:this.r+this.h-1,startColumnIndex:this.c-1,endColumnIndex:this.c+this.w-1});return this;}
 breakApart(){return this;}
 fmt(k,v){return this.each(c=>{(c.userEnteredFormat??={})[k]=v;});}
 setBackground(v){return this.fmt('backgroundColor',{red:parseInt(v.slice(1,3),16)/255,green:parseInt(v.slice(3,5),16)/255,blue:parseInt(v.slice(5,7),16)/255});}
 text(k,v){return this.each(c=>{((c.userEnteredFormat??={}).textFormat??={})[k]=v;});}
 setFontFamily(v){return this.text('fontFamily',v);}setFontSize(v){return this.text('fontSize',v);}setFontWeight(v){return this.text('bold',v==='bold');}
 setFontColor(v){return this.text('foregroundColor',{red:parseInt(v.slice(1,3),16)/255,green:parseInt(v.slice(3,5),16)/255,blue:parseInt(v.slice(5,7),16)/255});}
 setVerticalAlignment(v){return this.fmt('verticalAlignment',v.toUpperCase());}setWrap(v){return this.fmt('wrapStrategy',v?'WRAP':'CLIP');}
 setValue(v){if(v instanceof Date)v=(v.getTime()-12*3600000)/86400000+25569;const key=[this.sh,this.r,this.c].join(':');if(!cells.has(key))cells.set(key,{});cells.get(key).userEnteredValue={[typeof v==='boolean'?'boolValue':typeof v==='number'?'numberValue':'stringValue']:v};return this;}
 setFormula(v){this.setValue('');cells.get([this.sh,this.r,this.c].join(':')).userEnteredValue={formulaValue:v};return this;}
 setNote(v){return this.each(c=>c.note=v);}setDataValidation(v){return this.each(c=>c.dataValidation=v);}insertCheckboxes(){return this.setDataValidation({condition:{type:'BOOLEAN'},strict:true,showCustomUi:true});}
 setNumberFormat(v){return this.fmt('numberFormat',{type:v==='dd/mm/yyyy'?'DATE':v==='0%'?'PERCENT':'CURRENCY',pattern:v});}
}
const sh=id=>({getRange:(...a)=>new Range(id,...a),getSheetId:()=>id,setRowHeight:(r,h)=>sizes.set(r,h)});
const validation=()=>{let rule={};const b={requireDate:()=>{rule.condition={type:'DATE_IS_VALID'};return b;},requireNumberBetween:(a,c)=>{rule.condition={type:'NUMBER_BETWEEN',values:[{userEnteredValue:String(a)},{userEnteredValue:String(c)}]};return b;},requireNumberGreaterThanOrEqualTo:a=>{rule.condition={type:'NUMBER_GREATER_THAN_EQ',values:[{userEnteredValue:String(a)}]};return b;},setAllowInvalid:v=>{rule.strict=!v;return b;},build:()=>rule};return b;};
const ctx={Date,SpreadsheetApp:{newDataValidation:validation}};vm.createContext(ctx);vm.runInContext(fs.readFileSync('apps-script/Salarios.gs','utf8'),ctx);ctx.salarioHoje_=()=>46315;ctx.salarioCriarPainel_(sh(config),sh(carteira));
const requests=[];
function rect(id,r,c,h,w){return {sheetId:id,startRowIndex:r-1,endRowIndex:r+h-1,startColumnIndex:c-1,endColumnIndex:c+w-1};}
requests.push({unmergeCells:{range:rect(carteira,3,34,1,13)}});
for(const [id,r,c,h,w] of [[config,35,11,61,7],[config,32,15,2,3],[carteira,3,34,1,13]]){
 const rows=Array.from({length:h},(_,i)=>({values:Array.from({length:w},(_,j)=>cells.get([id,r+i,c+j].join(':'))||{})}));
 requests.push({updateCells:{range:rect(id,r,c,h,w),rows,fields:'userEnteredValue,userEnteredFormat,dataValidation,note'}});
}
for(const range of merges)if(!(range.sheetId===config&&range.startRowIndex===31))requests.push({mergeCells:{range,mergeType:'MERGE_ALL'}});
for(const [r,h]of sizes)requests.push({updateDimensionProperties:{range:{sheetId:config,dimension:'ROWS',startIndex:r-1,endIndex:r},properties:{pixelSize:h},fields:'pixelSize'}});
requests.push({updateSheetProperties:{properties:{sheetId:ledger,hidden:true},fields:'hidden'}});
function prepararMigracao(snapshot) {
 const sheets=snapshot.sheets,cfg=sheets.find(s=>s.properties.sheetId===config),car=sheets.find(s=>s.properties.sheetId===carteira);
 if(!cfg||!car||!sheets.some(s=>s.properties.sheetId===ledger))throw Error('Abas da instalação observada não encontradas.');
 function cell(sh,r,c){for(const d of sh.data||[]){const rr=r-1-(d.startRow||0),cc=c-1-(d.startColumn||0);if(rr>=0&&cc>=0){const v=d.rowData?.[rr]?.values?.[cc];if(v)return v;}}return {};}
 if(cell(cfg,320,3).userEnteredValue?.stringValue!=='14 · EMISSÃO E SALÁRIOS'||!cell(cfg,323,7).userEnteredValue)throw Error('Painel antigo ausente; não repetir migração.');
 for(let r=35;r<=95;r++)for(let c=11;c<=17;c++)if(cell(cfg,r,c).userEnteredValue)throw Error('Destino ocupado: '+r+':'+c);
 const out=JSON.parse(JSON.stringify(requests)),panel=out.find(q=>q.updateCells?.range.sheetId===config&&q.updateCells.range.startRowIndex===34).updateCells;
 const map={323:38,324:39,325:40,326:41,327:42,328:43,329:44,331:46,333:48,334:49,335:50,348:69,349:70,350:71,351:72,353:74};
 for(const [old,row]of Object.entries(map))if(![324,334,335].includes(+old))panel.rows[row-35].values[4].userEnteredValue=cell(cfg,+old,7).userEnteredValue;
 for(let i=0;i<5;i++)panel.rows[54+i-35].values[4].userEnteredValue=cell(cfg,339+i,7).userEnteredValue;
 for(let i=0;i<6;i++)panel.rows[62+i-35].values[4].userEnteredValue=cell(cfg,339+i,16).userEnteredValue;
 const wallet=out.find(q=>q.updateCells?.range.sheetId===carteira).updateCells;
 for(let i=0;i<13;i++)wallet.rows[0].values[i].userEnteredFormat=cell(car,3,34+i).userEnteredFormat||cell(car,3,34).userEnteredFormat||{};
 wallet.rows[0].values[12].userEnteredFormat={...wallet.rows[0].values[12].userEnteredFormat,horizontalAlignment:'CENTER'};
 for(const range of cfg.merges.filter(m=>m.startRowIndex>=319&&m.endRowIndex<=355&&m.startColumnIndex>=2&&m.endColumnIndex<=17))out.push({unmergeCells:{range}});
 out.push({repeatCell:{range:rect(config,320,3,36,15),cell:{},fields:'userEnteredValue,userEnteredFormat,dataValidation,note'}});
 return out;
}
if(require.main===module){const data=process.argv[2]?prepararMigracao(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))):requests;fs.writeFileSync('salarios/saidas/painel-base.json',JSON.stringify(data));console.log(JSON.stringify({requests:data.length,migracao:!!process.argv[2]}));}
module.exports={prepararMigracao};
