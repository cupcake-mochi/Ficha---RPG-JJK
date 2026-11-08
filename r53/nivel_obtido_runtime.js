'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib');
function gerar(){
 const dados={valores:require('./diagnostico-android/nivel_obtido_valores.json'),notas:require('./diagnostico-android/nivel_obtido_notas.json'),validacoes:require('./diagnostico-android/nivel_obtido_validacoes.json'),suporte:require('./diagnostico-android/nivel_obtido_suporte.json')};
 const gzip=z.gzipSync(JSON.stringify(dados));gzip[9]=3;
 return `// GERADO por r53/nivel_obtido_runtime.js. AQ02: entradas preservadas.
var R53_NIVEL_OBTIDO_CACHE_;
function r53NivelCarga_(){if(!R53_NIVEL_OBTIDO_CACHE_)R53_NIVEL_OBTIDO_CACHE_=JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(${JSON.stringify(gzip.toString('base64'))}),'application/gzip')).getDataAsString('UTF-8'));return R53_NIVEL_OBTIDO_CACHE_;}
function r53NivelRestaurar_(e){
 if(!e||!e.range)return false;
 var range=e.range,r=range.getRow(),rr=range.getLastRow(),c=range.getColumn(),cc=range.getLastColumn(),sheet=range.getSheet();
 if(sheet.getName()!=='DADOS_INVOC'||r>13||rr<2||![112,215,271].some(function(x){return c<=x&&x<=cc;}))return false;
 var data=r53NivelCarga_(),cells=data.valores.concat(data.suporte).filter(function(d){return d.r>=r&&d.r<=rr&&d.c>=c&&d.c<=cc;}),locale=sheet.getParent().getSpreadsheetLocale(),grupos=[];
 cells.sort(function(a,b){return a.c-b.c||a.r-b.r;});
 cells.forEach(function(d){var tipo=typeof d.depois,g=grupos[grupos.length-1];if(!g||g.c!==d.c||g.tipo!==tipo||g.r+g.rows.length!==d.r){g={r:d.r,c:d.c,tipo:tipo,rows:[]};grupos.push(g);}g.rows.push([tipo==='string'&&d.depois.charAt(0)==='='?r53CargaFormulaNoIdioma_(d.depois,locale):d.depois]);});
 grupos.forEach(function(g){sheet.getRange(g.r,g.c,g.rows.length,1).setValues(g.rows);});
 return cells.length===(rr-r+1)*(cc-c+1);
}
function r53AjustarNivel_(abas){
 var data=r53NivelCarga_(),ops=[],notes=[],dv=[],strict=[];
 function tab(nome){var a=abas.filter(function(a){return a.nome===nome;});if(a.length!==1)throw Error('Nível obtido: aba divergente');return a[0];}
 data.valores.forEach(function(d){var a=tab(d.aba),v=a.vals.filter(function(v){return v[0]===d.r&&v[1]===d.c;});if(v.length!==1||(v[0][2]!==d.antes&&v[0][2]!==d.depois))throw Error('Nível obtido: valor divergente');ops.push([v[0],d.depois]);});
 data.notas.forEach(function(d){var a=tab(d.aba),n=(a.notas||[]).filter(function(n){return n[0]===d.a1;});if(n.length!==1||(n[0][1]!==d.antes&&n[0][1]!==d.depois))throw Error('Nível obtido: nota divergente');notes.push([n[0],d.depois]);});
 data.validacoes.forEach(function(d){var a=tab(d.aba),v=(a.dv||[]).filter(function(v){return v[0].split(' ').indexOf(d.a1)>=0;}),formula='"'+d.depois.condition.values.map(function(x){return x.userEnteredValue;}).join(',')+'"';if(v.length>1||(v.length===1&&(v[0][0]!==d.a1||v[0][1]!==formula)))throw Error('Nível obtido: validação divergente');if(!v.length)dv.push([a,[d.a1,formula]]);var stricts=a.menus_estritos||[];if(stricts.filter(function(x){return x===d.a1;}).length>1)throw Error('Nível obtido: validação estrita duplicada');if(stricts.indexOf(d.a1)<0)strict.push([a,d.a1]);});
 ops.forEach(function(op){op[0][2]=op[1];});notes.forEach(function(op){op[0][1]=op[1];});dv.forEach(function(op){op[0].dv=op[0].dv||[];op[0].dv.push(op[1]);});strict.forEach(function(op){op[0].menus_estritos=op[0].menus_estritos||[];op[0].menus_estritos.push(op[1]);});
}
`;
}
module.exports={gerar};
if(require.main===module)fs.writeFileSync(path.join(__dirname,'../apps-script/NivelObtido.gs'),gerar());
