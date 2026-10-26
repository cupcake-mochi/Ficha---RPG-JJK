'use strict';
// Incremento estrito: não recompila nem troca os catálogos instalados.
const fs=require('fs'),vm=require('vm');
const ANTES="  if (typeof r53Editar_ === 'function' && r53Editar_(e)) return;";
const DEPOIS="  if (!e.r53EditorVerificado_ && typeof r53Editar_ === 'function' && r53Editar_(e)) return;";
function preparar(src){
 const anchor='R53_MODULO_=(new Function(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code)))))();';
 const wrapper='if(typeof r53Editar_==="function" && r53Editar_(e))return r53ContinuarPaletaPendente_(e);return r53Modulo_().onEdit(e);';
 for(const x of [anchor,wrapper])if(src.split(x).length!==2)throw Error('Caminho: carregador divergente ou incremento já aplicado');
 let out=src.replace(anchor,'R53_MODULO_=(new Function(r53CorrecaoCaminho_(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code))))))();')
  .replace(wrapper,'if(r53EditarCaminho_(e))return r53ContinuarPaletaPendente_(e);if(typeof r53Editar_==="function" && r53Editar_(e))return r53ContinuarPaletaPendente_(e);if(e)e.r53EditorVerificado_=true;return r53Modulo_().onEdit(e);');
 out+='\nfunction r53CorrecaoCaminho_(code){var a='+JSON.stringify(ANTES)+',b='+JSON.stringify(DEPOIS)+';if(code.split(a).length!==2)throw Error("Caminho: entrada do editor divergente");return code.replace(a,b);}\n';
 out+='\n'+require('../caminho_leve').gerar().output;
 new vm.Script(out);return out;
}
if(require.main===module){const[a,b]=process.argv.slice(2);if(!a||!b)throw Error('Uso: <Codigo salvo> <saida>');fs.writeFileSync(b,preparar(fs.readFileSync(a,'utf8')));}
module.exports={preparar,ANTES,DEPOIS};
