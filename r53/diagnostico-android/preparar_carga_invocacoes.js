'use strict';
// Delta estrito do molde de restauração; não envia código ao Google.
const fs=require('fs'),assert=require('assert'),vm=require('vm');
function ajustarCarga(abas) {
  var spec=abas.filter(function(a){return a.nome==='DADOS_INVOC';})[0];
  if(!spec)throw Error('Carga: DADOS_INVOC ausente');
  var changes=[];
  for(var side=0;side<2;side++)for(var i=1;i<6;i++) {
    var row=2+side*6+i,col=side?'AR':'Y';
    var formula=function(step){
      var p=[33,35,37,42].map(function(r){return "'INVOCAÇÕES'!$"+col+'$'+(r+step*i);});
      return '=SUM('+p[0]+':'+p[1]+','+p[2]+':'+p[3]+')';
    };
    var found=spec.vals.filter(function(t){return t[0]===row&&t[1]===139;});
    if(found.length!==1)throw Error('Carga: molde ausente ou duplicado');
    var next=formula(231);
    if(found[0][2]!==formula(198)&&found[0][2]!==next)
      throw Error('Carga: fórmula divergente em EI'+row);
    changes.push([found[0],next]);
  }
  if(spec.abaixo.some(function(t){return t[1]<=139&&t[3]>=139&&t[0]<=13&&t[2]>=2;}))
    throw Error('Carga: replicação inesperada');
  changes.forEach(function(p){p[0][2]=p[1];});
}
function preparar(before) {
  assert(!before.includes('function r53AjustarCargaInvocacoes_('),'Correção já instalada');
  const anchor=' try { r53AjustarRitual_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }';
  assert.strictEqual(before.split(anchor).length,2,'Carregador divergente');
  const helper=ajustarCarga.toString().replace('function ajustarCarga(','function r53AjustarCargaInvocacoes_(');
  const after=before.replace(anchor,anchor+'\n try { r53AjustarCargaInvocacoes_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }')+
    '\n// Carga das 12 invocações acompanha a expansão; 25/10/2026.\n'+helper+'\n';
  new vm.Script(after);return after;
}
if(require.main===module){const [input,output]=process.argv.slice(2);assert(input&&output);fs.writeFileSync(output,preparar(fs.readFileSync(input,'utf8')),{flag:'wx'});}
module.exports={preparar,ajustarCarga};
