'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib');
const GUARDA=`  if (typeof r53RepertorioRestaurar_ === 'function' &&
      (r53RepertorioRestaurar_(e) || r53RepertorioEntrada_(e))) {
    continuarPaleta_(inicio, null, false, e.range);
    return;
  }
`;
function reverterFonte(src){const n=src.split(GUARDA).length-1;if(n>1)throw Error('Guarda de repertório duplicada');return n?src.replace(GUARDA,''):src;}
function gerar(){
 const data={valores:require('./diagnostico-android/repertorio_trilha_plano.json'),notas:require('./diagnostico-android/repertorio_trilha_notas.json'),suporte:require('./diagnostico-android/repertorio_trilha_suporte.json')};
 const ui=data.valores.filter(d=>d.aba==='INVOCAÇÕES').map(d=>[d.r,d.c]);
 const blocos=ui.map(([r,c])=>r>=170?[r,c,r,c+16]:r===37?[37,4,39,6]:[34,4,34,6]);
 const payload=z.gzipSync(JSON.stringify(data),{mtime:0}).toString('base64');
 return `// GERADO por r53/repertorio_trilha_runtime.js. Não altera compras nem versões.
var R53_REPERTORIO_CACHE_;
function r53RepertorioCarga_(){if(!R53_REPERTORIO_CACHE_)R53_REPERTORIO_CACHE_=JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(${JSON.stringify(payload)}),'application/gzip')).getDataAsString('UTF-8'));return R53_REPERTORIO_CACHE_;}
function r53RepertorioEntrada_(e){if(!e||!e.range)return false;var r=e.range;return r.getSheet().getName()==='INVOCAÇÕES'&&r.getRow()>=35&&r.getLastRow()<=36&&r.getColumn()>=4&&r.getLastColumn()<=6;}
function r53RepertorioRestaurar_(e){
 if(!e||!e.range)return false;
 var range=e.range,sheet=range.getSheet(),name=sheet.getName();
 if(name!=='DADOS_INVOC'&&name!=='DADOS_R53'&&name!=='INVOCAÇÕES')return false;
 var r=range.getRow(),rr=range.getLastRow(),c=range.getColumn(),cc=range.getLastColumn();
 if(name==='INVOCAÇÕES'&&!${JSON.stringify(ui)}.some(function(p){return p[0]>=r&&p[0]<=rr&&p[1]>=c&&p[1]<=cc;}))return false;
 if(name==='DADOS_INVOC'&&!(r<=28&&rr>=16&&c<=108&&cc>=105))return false;
 if(name==='DADOS_R53'&&!(r<=253&&rr>=2&&c<=183&&cc>=181))return false;
 var carga=r53RepertorioCarga_(),data=carga.valores.concat(carga.suporte).filter(function(d){return d.aba===name&&d.r>=r&&d.r<=rr&&d.c>=c&&d.c<=cc;});
 if(!data.length)return false;
 // O editor pode entregar só uma âncora ao apagar mesclas juntas.
 // Recompõe os dois rótulos calculados, sem regravar a escolha D35.
 if(name==='INVOCAÇÕES'&&data.some(function(d){return d.r===34||d.r===37;}))data=carga.valores.filter(function(d){return d.aba===name&&(d.r===34||d.r===37);});
 var locale=sheet.getParent().getSpreadsheetLocale();
 data.sort(function(a,b){return a.c-b.c||a.r-b.r;});var grupos=[];
 data.forEach(function(d){var g=grupos[grupos.length-1];if(!g||g.c!==d.c||g.r+g.rows.length!==d.r){g={r:d.r,c:d.c,rows:[]};grupos.push(g);}g.rows.push([d.depois.charAt(0)==='='?r53CargaFormulaNoIdioma_(d.depois,locale):d.depois]);});
 grupos.forEach(function(g){sheet.getRange(g.r,g.c,g.rows.length,1).setValues(g.rows);});
 if(name==='INVOCAÇÕES'&&r<=39&&rr>=34)console.log('Repertório: recuperação '+(range.getA1Notation?range.getA1Notation():'')+' · '+data.length+' células calculadas');
 if(name==='INVOCAÇÕES'&&(${JSON.stringify(blocos)}.some(function(p){return r>=p[0]&&c>=p[1]&&rr<=p[2]&&cc<=p[3];})||(r>=34&&rr<=39&&c>=4&&cc<=6)))return true;
 return data.length===(rr-r+1)*(cc-c+1);
}
function r53AjustarRepertorio_(abas,externas){
 var carga=r53RepertorioCarga_(),ops=[],copias=[];
 carga.valores.forEach(function(d){
  var tabs=abas.filter(function(a){return a.nome===d.aba;});
  // O pacote Android ensaiado recupera DADOS_R53 pelo editor direto e
  // pelos moldes de Prática. Não injeta uma aba parcial no módulo antigo.
  if(!tabs.length&&d.aba==='DADOS_R53'&&externas===true)return;
  if(tabs.length!==1)throw Error('Repertório: aba divergente');
  var a=tabs[0],found=a.vals.filter(function(v){return v[0]===d.r&&v[1]===d.c;});
  if(found.length>1)throw Error('Repertório: alvo duplicado');
  var old=found.length?found[0][2]:null;
  if(!found.length&&d.aba==='DADOS_R53'&&d.c===183){
   var blocks=(a.abaixo||[]).filter(function(b){return b[0]<d.r&&d.r<=b[2]&&b[1]<=d.c&&d.c<=b[3];});
   if(blocks.length!==1)throw Error('Repertório: cópia abaixo divergente');
   var b=blocks[0],first=a.vals.filter(function(v){return v[0]===b[0]&&v[1]===183;});
   // Esta coluna legada copia somente a fórmula vazia. Não desloca
   // coordenadas nem supõe equivalência de fórmulas arbitrárias.
   if(first.length!==1||first[0][2]!=='=""'||d.antes!=='=""')throw Error('Repertório: molde vazio divergente');
   old=first[0][2];if(!copias.some(function(x){return x.a===a&&x.b===b;}))copias.push({a:a,b:b,style:first[0][3]});
  }
  if(old!==d.antes&&old!==d.depois)throw Error('Repertório: célula divergente '+d.aba+' '+d.r+':'+d.c);
  ops.push([a,found[0],d]);
 });
 var notes=carga.notas.map(function(d){var a=abas.filter(function(a){return a.nome===d.aba;})[0];var cells=(a.notas||[]).filter(function(v){return v[0]===d.a1;});if(cells.length>1||((cells.length?cells[0][1]:null)!==d.antes&&(cells.length?cells[0][1]:null)!==d.depois))throw Error('Repertório: nota divergente');return [a,cells[0],d];});
 // Materializa só a coluna dos moldes vazios; as fórmulas das outras
 // colunas e os registros explícitos existentes continuam intactos.
 copias.forEach(function(x){for(var r=x.b[0]+1;r<=x.b[2];r++)if(!x.a.vals.some(function(v){return v[0]===r&&v[1]===183;}))x.a.vals.push([r,183,'=""',x.style]);x.a.abaixo=x.a.abaixo.reduce(function(out,b){if(b!==x.b){out.push(b);return out;}if(b[1]<183)out.push([b[0],b[1],b[2],182]);if(b[3]>183)out.push([b[0],184,b[2],b[3]]);return out;},[]);});
 ops.forEach(function(op){var cell=op[0].vals.filter(function(v){return v[0]===op[2].r&&v[1]===op[2].c;})[0];if(cell)cell[2]=op[2].depois;else op[0].vals.push([op[2].r,op[2].c,op[2].depois]);});
 notes.forEach(function(op){if(op[1])op[1][1]=op[2].depois;else{op[0].notas=op[0].notas||[];op[0].notas.push([op[2].a1,op[2].depois]);}});
}
`;
}
module.exports={gerar,GUARDA,reverterFonte};
if(require.main===module){const code=gerar();new Function(code);fs.writeFileSync(path.join(__dirname,'../apps-script/RepertorioTrilha.gs'),code);console.log(JSON.stringify({bytes:code.length}));}
