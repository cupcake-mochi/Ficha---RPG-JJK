'use strict';
// Somente em descartável. Marca fases no log, sem leitura/escrita extra no Sheets.
const {sha,trocar}=require('./preparar_recursos_fila');
const BASE='d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084';
function preparar(src,base=BASE) {
 if(sha(src)!==base)throw Error('Perfil: Código divergente');
 const roots=src.match(/^function onEdit\(e\)\{[^\n]*\}$/gm);
 if(!roots||roots.length!==1)throw Error('Entrada onEdit divergente');
 const root=roots[0],body=root.slice(root.indexOf('{')+1,-1);
 src=trocar(src,root,'function onEdit(e){console.log("QA67 entrada "+Date.now());try{'+body+'}finally{console.log("QA67 saida "+Date.now());}}');
 const runtime='(function(){'+JSON.stringify(['devolverConta_','esticarCaixas_','lerCelulas_','descansar_'])+'.forEach(function(n){'+
  'var a="function "+n+"(",b="function QA67_"+n+"(";if(code.split(a).length!==2)throw Error("Perfil: função divergente "+n);'+
  'code=code.replace(a,b);code+="\\nfunction "+n+"(){console.log(\\"QA67 "+n+" antes \\"+Date.now());try{return QA67_"+n+".apply(this,arguments);}finally{console.log(\\"QA67 "+n+" depois \\"+Date.now());}}";'+
  '});})();\n';
 const anchor=' R53_MODULO_=(new Function(code))();';
 return trocar(src,anchor,runtime+'console.log("QA67 modulo antes "+Date.now());\n'+anchor+'console.log("QA67 modulo depois "+Date.now());\n');
}
module.exports={preparar,BASE};
if(require.main===module){const fs=require('node:fs');const [a,b]=process.argv.slice(2);fs.writeFileSync(b,preparar(fs.readFileSync(a,'utf8')));console.log(sha(fs.readFileSync(b,'utf8')));}
