"use strict";
// Prepara arquivo local revisável. Não acessa Google nem instala código.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ancora=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
const chamada=" try { r53AjustarDeslocamentoCorporal_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n";
function preparar(fonte,sha) {
 if(crypto.createHash('sha256').update(fonte).digest('hex')!==sha)throw Error('Snapshot do código diverge do SHA informado');
 if(fonte.includes('r53AjustarDeslocamentoCorporal_'))throw Error('Delta já presente: conferir versão antes de reaplicar');
 if(fonte.split(ancora).length!==2)throw Error('Âncora de fechamento do módulo ausente ou duplicada');
 const helper=fs.readFileSync(path.join(__dirname,'deslocamento_corporal_molde.gs'),'utf8');
 return fonte.replace(ancora,chamada+ancora)+'\n'+helper;
}
if(require.main===module){
 const [entrada,sha,saida]=process.argv.slice(2);
 if(!entrada||!sha||!saida)throw Error('Uso: node preparar_deslocamento_loader.js entrada.gs SHA256 saida.gs');
 if(path.resolve(entrada)===path.resolve(saida))throw Error('Preserve o snapshot de entrada');
 fs.writeFileSync(saida,preparar(fs.readFileSync(entrada,'utf8'),sha));
}
module.exports={preparar,ancora,chamada};
