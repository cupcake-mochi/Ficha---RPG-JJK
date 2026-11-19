'use strict';
const assert=require('node:assert/strict'),p=require('../diagnostico-android/preparar_pratica_cotidiana'),a=require('../diagnostico-android/pratica_aparencia');
let checks=0;const test=f=>{f();checks++;},clone=x=>JSON.parse(JSON.stringify(x));
const names=[...new Set([...p.p.cells,...p.p.notes].map(x=>x.aba)),'R53_LOTE'];
const metadata={properties:{locale:'pt_BR'},sheets:names.map((title,sheetId)=>({properties:{title,sheetId,gridProperties:{rowCount:p.p.grids[title]?.antes??1000,columnCount:300}}}))};
const cells=new Map();for(const x of [...p.p.cells,...p.p.notes]){const k=x.aba+'!'+x.a1;if(!cells.has(k))cells.set(k,{aba:x.aba,a1:x.a1,sheetId:names.indexOf(x.aba),value:null,note:null});cells.get(k)[p.p.notes.includes(x)?'note':'value']=x.antes;}
// No idioma inglês, antes das equivalências de representação do Google.
metadata.properties.locale='en_US';
const map={paletas:{controle:['#ffffff','#000000']},abas:{'FICHA AMALDIÇOADA':{b:{papel:['A1:U561']},f:{tinta:['A1:U561']}},CONTROLE:{b:{papel:['A1:Z20']},f:{tinta:['A1:Z20']}}}};
const s={locale:'en_US',cells:[...cells.values()],formats:{D320:{},R327:{},P322:{}},mapParts:[JSON.stringify(map)],blankCells:[...Array.from({length:17},(_,i)=>({aba:'FICHA AMALDIÇOADA',r:328,c:i+4,value:null})),...Array.from({length:9},(_,i)=>({aba:'MONTAGENS',r:9467,c:i+1,value:null}))]};
const before=clone(s),r=p.planejarInstalacao(s,metadata);
test(()=>assert.deepEqual(s,before));test(()=>assert(r.requests.length<300));
test(()=>assert.equal(r.requests.filter(x=>x.updateSheetProperties).length,4));
test(()=>assert(r.requests.some(x=>x.mergeCells?.range.startRowIndex===564&&x.mergeCells.range.startColumnIndex===17)));
test(()=>assert(!r.requests.some(x=>x.mergeCells?.range.startRowIndex===564&&x.mergeCells.range.startColumnIndex===15&&x.mergeCells.range.endColumnIndex===17)));
for(const corrupt of [x=>x.blankCells.pop(),x=>x.blankCells[4].value='entrada preservada',x=>x.blankCells[20].note='nota manual',x=>x.cells.at(-1).note='nota manual',x=>delete x.mapParts,x=>delete x.formats.P322]){const q=clone(s);corrupt(q);test(()=>assert.throws(()=>p.planejarInstalacao(q,metadata)));}
for(const n of Object.keys(p.p.grids)){const m=clone(metadata);m.sheets.find(x=>x.properties.title===n).properties.gridProperties.rowCount++;test(()=>assert.throws(()=>p.planejarInstalacao(s,m),/Grade/));}
const next=a.aplicar(map);test(()=>assert.deepEqual(a.aplicar(next),next));test(()=>assert.deepEqual(next.abas.CONTROLE,map.abas.CONTROLE));test(()=>assert.deepEqual(next.paletas,map.paletas));
// Avalia o mapa como células, independente da partição dos retângulos.
function expanded(m,ch){const out=new Map();for(const[k,rs]of Object.entries(m.abas['FICHA AMALDIÇOADA'][ch]))for(const range of rs){const [r,c,rr,cc]=a.rect(range);for(let i=r;i<=rr;i++)for(let j=c;j<=cc;j++){const key=i+','+j;assert(!out.has(key),'Sobreposição '+key);out.set(key,k);}}return out;}
for(const ch of ['b','f']){const old=expanded(map,ch),cur=expanded(next,ch);for(const[k,v]of old)test(()=>assert.equal(cur.get(k),v));test(()=>assert.equal(cur.get('567,17'),ch==='b'?'papel':'tinta'));}
console.log(JSON.stringify({resultado:'OK',verificacoes:checks,escopo:'preflight, limites, áreas vazias e mapa de aparência; sem Google'}));
