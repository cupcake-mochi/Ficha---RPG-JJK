// Migração pontual 3b: reaproveita o motor de paleta sem chamadas de rede.
// Uso: node medidas/preparar-cores-progressao.js "$PWD" ../evidencias-3b
// Lê o backup cores-novas-antes.json e prepara somente pedidos de cor da área nova.
const fs=require('fs'),vm=require('vm'),root=process.argv[2],evid=process.argv[3],c={};vm.createContext(c);vm.runInContext(require(root+'/medidas/carregar-ficha.js').fontes()+'\n'+fs.readFileSync(root+'/apps-script/Codigo.gs','utf8'),c);
const data=JSON.parse(fs.readFileSync(evid+'/cores-novas-antes.json')).sheets[0].data[0];
const hex=x=>'#'+['red','green','blue'].map(k=>Math.round((x?.[k]||0)*255).toString(16).padStart(2,'0')).join('').toUpperCase();
let bg=Array.from({length:187},(_,r)=>Array.from({length:50},(_,k)=>hex(data.rowData[r]?.values?.[k]?.userEnteredFormat?.backgroundColor))),fc=Array.from({length:187},(_,r)=>Array.from({length:50},(_,k)=>hex(data.rowData[r]?.values?.[k]?.userEnteredFormat?.textFormat?.foregroundColor)));
c.repintarCoresDaAba_({getSheetByName:()=>({getRange:()=>({getBackgrounds:()=>bg,getFontColors:()=>fc,setBackgrounds:v=>bg=v,setFontColors:v=>fc=v})})},c.ABAS.find(a=>a.nome==='FICHA'),null,'Mizuki · Escuro · ameixa e rosa',[410,596]);
const rgb=h=>Object.fromEntries(['red','green','blue'].map((k,i)=>[k,parseInt(h.slice(1+i*2,3+i*2),16)/255]));
const rows=bg.map((row,r)=>({values:row.map((b,k)=>({userEnteredFormat:{backgroundColor:rgb(b),textFormat:{foregroundColor:rgb(fc[r][k])}}}))}));
const groups=[];for(let r=0;r<rows.length;r+=8)groups.push([{updateCells:{start:{sheetId:1980633175,rowIndex:409+r,columnIndex:0},rows:rows.slice(r,r+8),fields:'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.foregroundColor'}}]);
fs.writeFileSync(evid+'/reparo-paleta-area-nova.json',JSON.stringify(groups));
console.log(JSON.stringify({chunks:groups.length,cells:rows.length*50}));
