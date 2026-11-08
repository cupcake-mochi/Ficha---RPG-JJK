'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib');
function gerar(){
 const dados={valores:require('./diagnostico-android/criacao_nivel_fixo_plano.json'),notas:require('./diagnostico-android/criacao_nivel_fixo_notas.json'),suporte:require('./diagnostico-android/criacao_nivel_fixo_suporte.json')};
 const gzip=z.gzipSync(JSON.stringify(dados));gzip[9]=3;
 return `// GERADO por r53/criacao_nivel_fixo_runtime.js. Nível fabricado, sem alterar entradas.
var R53_CRIACAO_CACHE_;
function r53CriacaoCarga_(){if(!R53_CRIACAO_CACHE_)R53_CRIACAO_CACHE_=JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(${JSON.stringify(gzip.toString('base64'))}),'application/gzip')).getDataAsString('UTF-8'));return R53_CRIACAO_CACHE_;}
function r53CriacaoRestaurar_(e){
 if(!e||!e.range)return false;
 var range=e.range,r=range.getRow(),rr=range.getLastRow(),c=range.getColumn(),cc=range.getLastColumn(),sheet=range.getSheet();
 if(sheet.getName()!=='DADOS_INVOC'||!((r<=13&&rr>=2&&c<=171&&cc>=171)||(r<=5&&rr>=5&&c<=69&&cc>=69)))return false;
 var carga=r53CriacaoCarga_(),data=carga.valores.concat(carga.suporte).filter(function(d){return d.aba==='DADOS_INVOC'&&d.r>=r&&d.r<=rr&&d.c>=c&&d.c<=cc;});
 if(!data.length)return false;
 var locale=sheet.getParent().getSpreadsheetLocale(),grupos=[];
 data.sort(function(a,b){return a.c-b.c||a.r-b.r;});
 data.forEach(function(d){var tipo=typeof d.depois,g=grupos[grupos.length-1];if(!g||g.c!==d.c||g.tipo!==tipo||g.r+g.rows.length!==d.r){g={r:d.r,c:d.c,tipo:tipo,rows:[]};grupos.push(g);}var v=tipo==='string'&&d.depois.charAt(0)==='='?r53CargaFormulaNoIdioma_(d.depois,locale):d.depois;g.rows.push([v]);});
 grupos.forEach(function(g){sheet.getRange(g.r,g.c,g.rows.length,1).setValues(g.rows);});
 return data.length===(rr-r+1)*(cc-c+1);
}
// O módulo Android antigo conserva o retrato anterior. Valida tudo antes
// de ajustá-lo; colagens mistas continuam no editor com os moldes corretos.
function r53AjustarCriacao_(abas){
 var carga=r53CriacaoCarga_(),ops=[],copias=[],notes=[];
 carga.valores.forEach(function(d){
  var tabs=abas.filter(function(a){return a.nome===d.aba;});if(tabs.length!==1)throw Error('Criação: aba divergente');
  var a=tabs[0],cells=a.vals.filter(function(v){return v[0]===d.r&&v[1]===d.c;});if(cells.length>1)throw Error('Criação: alvo duplicado');
  if(cells.length){if(cells[0][2]!==d.antes&&cells[0][2]!==d.depois)throw Error('Criação: valor divergente');ops.push([a,cells[0],d]);return;}
  var blocks=(a.abaixo||[]).filter(function(b){return b[0]<d.r&&d.r<=b[2]&&b[1]<=d.c&&d.c<=b[3];});
  if(d.aba!=='DADOS_INVOC'||d.c!==171||blocks.length!==1||blocks[0][0]!==2||blocks[0][2]!==13)throw Error('Criação: cópia abaixo divergente');
  var base=carga.valores.filter(function(x){return x.aba===d.aba&&x.r===2&&x.c===d.c;})[0],first=a.vals.filter(function(v){return v[0]===2&&v[1]===d.c;});
  if(!base||first.length!==1||(first[0][2]!==base.antes&&first[0][2]!==base.depois))throw Error('Criação: molde divergente');
  ops.push([a,null,d,first[0][3]]);if(!copias.some(function(x){return x.a===a&&x.b===blocks[0];}))copias.push({a:a,b:blocks[0]});
 });
 carga.notas.forEach(function(d){var tabs=abas.filter(function(a){return a.nome===d.aba;});if(tabs.length!==1)throw Error('Criação: aba de notas divergente');var a=tabs[0],cells=(a.notas||[]).filter(function(v){return v[0]===d.a1;});if(cells.length!==1||(cells[0][1]!==d.antes&&cells[0][1]!==d.depois))throw Error('Criação: nota divergente');notes.push([cells[0],d.depois]);});
 copias.forEach(function(x){x.a.abaixo=x.a.abaixo.reduce(function(out,b){if(b!==x.b)out.push(b);else{if(b[1]<171)out.push([b[0],b[1],b[2],170]);if(b[3]>171)out.push([b[0],172,b[2],b[3]]);}return out;},[]);});
 ops.forEach(function(op){if(op[1])op[1][2]=op[2].depois;else op[0].vals.push([op[2].r,op[2].c,op[2].depois,op[3]]);});
 notes.forEach(function(op){op[0][1]=op[1];});
}
`;
}
module.exports={gerar};
if(require.main===module)fs.writeFileSync(path.join(__dirname,'../apps-script/CriacaoNivelFixo.gs'),gerar());
