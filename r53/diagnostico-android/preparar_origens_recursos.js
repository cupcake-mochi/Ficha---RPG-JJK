'use strict';
const fs=require('node:fs'),path=require('node:path');
const {sha,trocar}=require('./preparar_recursos_fila');
const {planejarCelulas}=require('./preparar_pilha_5156');
const plano=require('./origens_recursos_plano.json'),mudancas=require('./origens_recursos_patch.json');
const BASE='d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084';
function runtime(){return '(function(){var mudancas='+JSON.stringify(mudancas.slice(0,2))+';\n'+
 'mudancas.forEach(function(m){if(code.split(m[0]).length!==2)throw Error("Origem/recursos: fonte divergente");});\n'+
 'mudancas.forEach(function(m){code=code.replace(m[0],function(){return m[1];});});})();\n';}
function reverterFonte(src){
 for(const [a,b]of [...mudancas].reverse()){if(src.split(b).length!==2)throw Error('Fonte Origem/recursos divergente');src=src.replace(b,()=>a);}return src;
}
function molde(){return 'var R53_ORIGENS_RECURSOS_='+JSON.stringify(plano)+';\n'+
 fs.readFileSync(path.join(__dirname,'pilha_5156_molde.gs'),'utf8').replaceAll('r53AjustarPilha516_','r53AjustarOrigensRecursos_').replaceAll('R53_PILHA_516_','R53_ORIGENS_RECURSOS_').replaceAll('Pilha 51–56:','Origens/recursos:');}
function prepararCodigo(src){
 if(sha(src)!==BASE)throw Error('Código divergente: exige PR66 ensaiada');
 const root='function onEdit(e){return r53SalarioOnEdit_(e);}';
 src=trocar(src,root,'function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53DescansoEdit_(e))return r53ContinuarPaletaPendente_(e);return r53SalarioOnEdit_(e);}');
 const a=' R53_MODULO_=(new Function(code))();';src=trocar(src,a,runtime()+a);
 const b='r53AjustarBencaosImunidades_(R53_MODULO_.__estado().abas);';src=trocar(src,b,b+' r53AjustarOrigensRecursos_(R53_MODULO_.__estado().abas);');
 const ativo='function r53DescansarComQueda(tipo, queda, jaConvertido) { return r53Modulo_().r53DescansarComQueda(tipo, queda, jaConvertido); }';
 src=trocar(src,ativo,'function r53DescansarComQueda(tipo,queda,jaConvertido){return r53DescansoLeve_().comQueda(tipo,queda,jaConvertido);}');
 return src+'\n'+molde()+'\n'+fs.readFileSync(path.join(__dirname,'../../apps-script/Descanso.gs'),'utf8');
}
const normalizar=s=>typeof s==='string'&&s.startsWith('=')?s.split(/("(?:[^"]|"")*")/).map((t,i)=>i%2?t:t.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g,'$1!')).join(''):s;
function planejar(snapshot,reverter=false){return planejarCelulas({...snapshot,cells:snapshot.cells.map(d=>({...d,value:normalizar(d.value??null)}))},reverter,plano.map(d=>({...d,antes:normalizar(d.antes),depois:normalizar(d.depois)})));}
// Uso exclusivo dos comparadores de gerações históricas, nunca da instalação.
function reverterModelo(abas){
 const ops=plano.map(d=>{const a=abas.find(a=>a.nome===d.aba),v=a&&a.vals.filter(v=>v[0]===d.r&&v[1]===d.c);if(!v||v.length!==1||v[0][2]!==d.depois)throw Error('Molde de origem divergente');return {a,d,v:v[0]};});
 for(const {a,d,v}of ops){if(d.antes===null)a.vals.splice(a.vals.indexOf(v),1);else v[2]=d.antes;}return abas;
}
module.exports={BASE,plano,mudancas,runtime,reverterFonte,molde,prepararCodigo,planejar,reverterModelo,normalizar};
if(require.main===module){const [a,b]=process.argv.slice(2);fs.writeFileSync(b,prepararCodigo(fs.readFileSync(a,'utf8')));console.log(sha(fs.readFileSync(b,'utf8')));}
