'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib');
const root=path.resolve(__dirname,'..');
const GUARDA="  if (typeof r53PraticaRestaurar_ === 'function' && r53PraticaRestaurar_(e)) {\n    continuarPaleta_(inicio, null, false, e.range);\n    return;\n  }\n";
function dados(deltas=require('./diagnostico-android/classe_zero_plano.json'), tempo=[]){
 const p=require('./diagnostico-android/pratica_cotidiana_plano.json');
 const editor=JSON.parse(/^var R53_EDITOR_ = (\{[^\n]+\});/.exec(fs.readFileSync(path.join(root,'apps-script/EditorR53.gs'),'utf8'))[1]);
 const input=new Set(editor.contextos.slice(249).flatMap(g=>[g.cel.nome,...Object.values(g.entradas_diretas)]));
 const correcoes=new Map(deltas.map(d=>[JSON.stringify([d.aba,d.r,d.c]),d]));
 const valores = p.cells.filter(x=>x.aba!=='MONTAGENS'&&!(x.aba==='FICHA AMALDIÇOADA'&&(input.has(x.a1)||x.depois===null||x.depois===undefined))).map(x=>{
  const m=/^([A-Z]+)(\d+)$/.exec(x.a1),c=[...m[1]].reduce((a,v)=>26*a+v.charCodeAt(0)-64,0);
  const alvo=correcoes.get(JSON.stringify([x.aba,+m[2],c]));
  if(alvo&&alvo.antes!==x.depois)throw Error('Recuperação de Prática divergente: '+x.a1);
  let value=alvo?alvo.depois:x.depois;if(x.aba==='ANALISE'&&c===3&&typeof value==='string'){const lit=/^="((?:[^"]|"")*)"$/.exec(value);if(lit)value=lit[1].replace(/""/g,'"');}
  return [x.aba,+m[2],c,value];
 });
 const classeZero=deltas.filter(d=>d.aba==='DADOS_R53');
 return valores.concat([...classeZero,...tempo].map(d=>[d.aba,d.r,d.c,d.depois]));
}
function gerar(deltas, tempo=deltas===undefined?require('./diagnostico-android/tempo_feiticos_plano.json'):[]){
 deltas ??= require('./diagnostico-android/classe_zero_plano.json');
 const efeitos=tempo.filter(d=>d.aba==='DADOS_R53');
 const classeZero=deltas.filter(d=>d.aba==='DADOS_R53');
 const payload=z.gzipSync(JSON.stringify(dados(deltas,efeitos)),{mtime:0}).toString('base64');
 return `// GERADO por r53/pratica_cotidiana_runtime.js. Dados descompactados só nos alvos novos.
var R53_PRATICA_CACHE_;
function r53PraticaDados_(){if(!R53_PRATICA_CACHE_)R53_PRATICA_CACHE_=JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(${JSON.stringify(payload)}),'application/gzip')).getDataAsString('UTF-8'));return R53_PRATICA_CACHE_;}
function r53PraticaRestaurar_(e){
 if(!e||!e.range)return false;var range=e.range,r1=range.getRow(),r2=range.getLastRow(),c1=range.getColumn(),c2=range.getLastColumn();
 function toca(a,b,c,d){return r1<=c&&r2>=a&&c1<=d&&c2>=b;}
 function dentro(a,b,c,d){return r1>=a&&r2<=c&&c1>=b&&c2<=d;}
 if(!(toca(10,221,10,221)||toca(134,2,136,2)||toca(252,1,253,183)${classeZero.length?'||toca(41,181,45,183)':''}${efeitos.length?'||toca(2,160,37,160)':''}||toca(328,4,329,4)||toca(563,4,565,20)||toca(566,16,567,16)||toca(566,18,567,20)||toca(18410,1,18500,4)))return false;
 var sheet=range.getSheet(),name=sheet.getName();
 if(['FICHA AMALDIÇOADA','DADOS_AM','DADOS_CUSTOM','DADOS_R53','ANALISE'].indexOf(name)<0)return false;
 var data=r53PraticaDados_().filter(function(v){return v[0]===name&&v[1]>=r1&&v[1]<=r2&&v[2]>=c1&&v[2]<=c2;});
 var fronteira=name==='FICHA AMALDIÇOADA'&&toca(328,4,329,4);
 if(!data.length&&!fronteira)return false;
 var locale=sheet.getParent().getSpreadsheetLocale();
 function value(v){return typeof v==='string'&&v.charAt(0)==='='?r53CargaFormulaNoIdioma_(v,locale):v;}
 if(name==='DADOS_R53'${classeZero.length?'&&toca(252,1,253,183)':''}){
  var a=Math.max(r1,252),b=Math.min(r2,253),l=Math.max(c1,1),h=Math.min(c2,183),rows=[];
  for(var r=a;r<=b;r++){var line=[];for(var c=l;c<=h;c++){var found=data.filter(function(v){return v[1]===r&&v[2]===c;});if(found.length!==1)throw Error('Prática: célula calculada ausente');line.push(value(found[0][3]));}rows.push(line);}
  sheet.getRange(a,l,rows.length,h-l+1).setValues(rows);
  ${classeZero.length?`if(dentro(252,1,253,183))return true;
  data=data.filter(function(v){return v[1]<252;});`:'return dentro(252,1,253,183);'}
 }
 // Agrupa por coluna e tipo: textos permanecem textos, inclusive apóstrofos e "0".
 data.sort(function(a,b){return a[2]-b[2]||a[1]-b[1];});var groups=[];
 data.forEach(function(v){var rich=typeof v[3]==='string'&&v[3].charAt(0)!=='=',last=groups[groups.length-1];if(!last||last.c!==v[2]||last.rich!==rich||last.r+last.rows.length!==v[1]){last={r:v[1],c:v[2],rich:rich,rows:[]};groups.push(last);}var val=value(v[3]);
  // O Google também interpreta RichText "0" como número. O escape força
  // texto e é consumido na gravação, preservando um apóstrofo já existente.
  if(rich)val=SpreadsheetApp.newRichTextValue().setText("'"+val).build();
  last.rows.push([val]);
 });
 groups.forEach(function(g){var cell=sheet.getRange(g.r,g.c,g.rows.length,1);if(g.rich)cell.setRichTextValues(g.rows);else cell.setValues(g.rows);});
 // A indicação encosta na Liberação, que ocupa duas linhas mescladas.
 // Recupera a âncora separadamente quando a edição toca um dos dois blocos.
 if(fronteira)sheet.getRange(329,4).setFormula('=DADOS_AM!$KV$36');
 // A rota curta só encerra eventos cobertos por esta correção.
 // Entradas e fórmulas históricas da mesma colagem seguem o editor anterior.
 if(name==='FICHA AMALDIÇOADA'){
  return (fronteira&&dentro(328,4,330,20))||dentro(563,4,565,20)||
         dentro(566,16,567,16)||dentro(566,18,567,20);
 }
 return data.length===(r2-r1+1)*(c2-c1+1);
}
`;
}
function reverterFonte(src){if(src.split(GUARDA).length!==2)throw Error('Guarda de Prática divergente');return src.replace(GUARDA,'');}
module.exports={dados,gerar,GUARDA,reverterFonte};
if(require.main===module){const code=gerar();new Function(code);fs.writeFileSync(path.join(root,'apps-script/PraticaCotidiana.gs'),code);console.log(JSON.stringify({bytes:code.length,alvos:dados(undefined,require('./diagnostico-android/tempo_feiticos_plano.json').filter(d=>d.aba==='DADOS_R53')).length}));}
