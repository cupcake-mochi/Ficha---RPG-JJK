'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const anchor=' try { r53AjustarCargaInvocacoes_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }';
function preparar(source){
 if(source.includes('function r53AjustarVersaoPublica_'))throw Error('Versão pública já instalada');
 if(source.split(anchor).length!==2)throw Error('Carregador divergente');
 const call='\n try { r53AjustarVersaoPublica_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }';
 const edit='function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();';
 if(source.split(edit).length!==2)throw Error('Entrada de edição divergente');
 const out=source.replace(anchor,anchor+call).replace(edit,edit+'if(r53RestaurarVersaoPublica_(e))return r53ContinuarPaletaPendente_(e);')+'\n'+fs.readFileSync(path.join(__dirname,'versao_publica.gs'),'utf8');
 new vm.Script(out);return out;
}
if(require.main===module){const [input,output]=process.argv.slice(2);fs.writeFileSync(output,preparar(fs.readFileSync(input,'utf8')));}
module.exports={preparar,anchor};
