'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib');
const root=path.resolve(__dirname,'..');
function gerar(plano=require('./diagnostico-android/expansao_domada_plano.json'),suporte=require('./diagnostico-android/expansao_domada_suporte.json')) {
 const notas=require('./diagnostico-android/expansao_domada_notas.json');
 const linhasAnalise=plano.filter(d=>d.aba==='ANALISE').map(d=>d.r);
 const inicioAnalise=Math.min(...linhasAnalise),fimAnalise=Math.max(...linhasAnalise);
 const payload=z.gzipSync(JSON.stringify({valores:plano,notas,suporte}),{mtime:0}).toString('base64');
 return `// GERADO por r53/expansao_domada_runtime.js. Só aquisição e metadados calculados.
var R53_EXPANSAO_CACHE_;
function r53ExpansaoCarga_(){if(!R53_EXPANSAO_CACHE_)R53_EXPANSAO_CACHE_=JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(${JSON.stringify(payload)}),'application/gzip')).getDataAsString('UTF-8'));return R53_EXPANSAO_CACHE_;}
function r53ExpansaoDados_(){return r53ExpansaoCarga_().valores;}
function r53ExpansaoRestaurar_(e){
 if(!e||!e.range)return false;
 var range=e.range,r=range.getRow(),rr=range.getLastRow(),c=range.getColumn(),cc=range.getLastColumn();
 if(!((r<=13&&rr>=2&&((c<=239&&cc>=239)||(c<=270&&cc>=268)))||(r<=${fimAnalise}&&rr>=${inicioAnalise}&&c<=4&&cc>=1)))return false;
 var sheet=range.getSheet(),name=sheet.getName();
 if(name!=='DADOS_INVOC'&&name!=='ANALISE')return false;
 var data=r53ExpansaoDados_().concat(r53ExpansaoCarga_().suporte).filter(function(d){return d.aba===name&&d.r>=r&&d.r<=rr&&d.c>=c&&d.c<=cc;});
 if(!data.length)return false;
 var locale=sheet.getParent().getSpreadsheetLocale();
 // Agrupa por coluna e tipo, como a recuperação de Prática Cotidiana.
 // Preserva o escape dos literais de origem: o Google consome um apóstrofo.
 data.sort(function(a,b){return a.c-b.c||a.r-b.r;});var grupos=[];
 data.forEach(function(d){var rich=d.depois.charAt(0)!=='=',g=grupos[grupos.length-1];if(!g||g.c!==d.c||g.rich!==rich||g.r+g.rows.length!==d.r){g={r:d.r,c:d.c,rich:rich,rows:[]};grupos.push(g);}var v=rich?SpreadsheetApp.newRichTextValue().setText("'"+d.depois).build():r53CargaFormulaNoIdioma_(d.depois,locale);g.rows.push([v]);});
 grupos.forEach(function(g){var cell=sheet.getRange(g.r,g.c,g.rows.length,1);if(g.rich)cell.setRichTextValues(g.rows);else cell.setValues(g.rows);});
 return data.length===(rr-r+1)*(cc-c+1);
}
// Atualiza também o retrato do pacote antigo. Assim uma colagem mista que
// continua no editor histórico não repõe fórmulas ou tipos anteriores.
function r53AjustarExpansao_(abas,analiseExterna){
 var plano=r53ExpansaoDados_(),ops=[];
 plano.forEach(function(d){
  var tabs=abas.filter(function(a){return a.nome===d.aba;});
  // O pacote Android anterior omite ANALISE: sua recuperação é externa.
  // Não injeta uma aba parcial nem recarrega os catálogos para doze tags.
  if(!tabs.length&&d.aba==='ANALISE'&&analiseExterna===true)return;
  if(tabs.length!==1)throw Error('Expansão: aba divergente '+d.aba);
  var a=tabs[0],cells=a.vals.filter(function(v){return v[0]===d.r&&v[1]===d.c;});
  if(cells.length>1)throw Error('Expansão: alvo duplicado');
  if(cells.length){if(cells[0][2]!==d.antes&&cells[0][2]!==d.depois)throw Error('Expansão: valor divergente');ops.push([a,cells[0],d]);return;}
  var blocks=(a.abaixo||[]).filter(function(b){return b[0]<d.r&&d.r<=b[2]&&b[1]<=d.c&&d.c<=b[3];});
  if(blocks.length!==1||blocks[0][0]!==2||blocks[0][2]!==13||d.aba!=='DADOS_INVOC')throw Error('Expansão: cópia abaixo divergente');
  var base=plano.filter(function(p){return p.aba===d.aba&&p.r===2&&p.c===d.c;})[0];
  var first=a.vals.filter(function(v){return v[0]===2&&v[1]===d.c;});
  if(!base||first.length!==1||(first[0][2]!==base.antes&&first[0][2]!==base.depois))throw Error('Expansão: molde divergente');
  ops.push([a,null,d,first[0][3]]);
 });
 var notes=r53ExpansaoCarga_().notas.map(function(d){
  var a=abas.filter(function(a){return a.nome===d.aba;})[0];if(!a)throw Error('Expansão: aba de notas ausente');
  var cells=(a.notas||[]).filter(function(v){return v[0]===d.a1;});
  if(cells.length>1||((cells.length?cells[0][1]:null)!==d.antes&&(cells.length?cells[0][1]:null)!==d.depois))throw Error('Expansão: nota divergente');
  return [a,cells[0],d];
 });
 // Tudo foi validado antes da primeira mutação.
 var inv=abas.filter(function(a){return a.nome==='DADOS_INVOC';})[0];
 [239,268,270].forEach(function(col){inv.abaixo=(inv.abaixo||[]).reduce(function(out,b){if(b[1]<=col&&col<=b[3]&&b[0]===2&&b[2]===13){if(b[1]<col)out.push([b[0],b[1],b[2],col-1]);if(col<b[3])out.push([b[0],col+1,b[2],b[3]]);}else out.push(b);return out;},[]);});
 ops.forEach(function(op){if(op[1])op[1][2]=op[2].depois;else op[0].vals.push([op[2].r,op[2].c,op[2].depois,op[3]]);});
 notes.forEach(function(op){if(op[1])op[1][1]=op[2].depois;else{op[0].notas=op[0].notas||[];op[0].notas.push([op[2].a1,op[2].depois]);}});
}
`;
}
module.exports={gerar};
if(require.main===module){const code=gerar();new Function(code);fs.writeFileSync(path.join(root,'apps-script/ExpansaoDomada.gs'),code);console.log(JSON.stringify({bytes:code.length}));}
