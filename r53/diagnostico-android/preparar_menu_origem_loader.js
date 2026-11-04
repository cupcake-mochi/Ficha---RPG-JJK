'use strict';
// Preparação offline: não escreve em planilhas nem instala o pacote integral.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ancora=" if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
function preparar(fonte,sha){
 if(crypto.createHash('sha256').update(fonte).digest('hex')!==sha)throw Error('Snapshot divergente');
 if(fonte.includes('r53AjustarMenuOrigem_'))throw Error('Delta já presente');
 if(fonte.split(ancora).length!==2)throw Error('Âncora ausente ou duplicada');
 const helper=fs.readFileSync(path.join(__dirname,'menu_origem_molde.gs'),'utf8');
 return fonte.replace(ancora," try { r53AjustarMenuOrigem_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n"+ancora)+'\n'+helper;
}
if(require.main===module){
 const [entrada,sha,saida]=process.argv.slice(2);
 if(!entrada||!sha||!saida||path.resolve(entrada)===path.resolve(saida))throw Error('Informe entrada.gs SHA256 saída.gs distintos');
 fs.writeFileSync(saida,preparar(fs.readFileSync(entrada,'utf8'),sha));
}
module.exports={preparar,ancora};
