'use strict';
// Migração local do carregador instalado; não envia código nem executa a ficha.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
function ajustarRitual(abas) {
  var spec=abas.filter(function(a){return a.nome==='DADOS_AM';})[0];
  if(!spec)throw Error('Ritual: DADOS_AM ausente');
  var expected=[[2,346],[3,347]],changes=[];
  expected.forEach(function(pos){
    var cells=spec.vals.filter(function(t){return t[0]===pos[0]&&t[1]===pos[1];});
    if(cells.length!==1)throw Error('Ritual: molde ausente ou duplicado');
    var old='=IF(AND(NOT(OR(FALSE)),$LI'+pos[0]+'="Ritual"),"Conferir Técnica Inata","")';
    var next='=IF(AND(NOT(OR(FALSE)),AND($LI'+pos[0]+'="Ritual",NOT((DADOS_AM!$A$2=1)))),"Conferir Técnica Inata","")';
    if(cells[0][2]!==old&&cells[0][2]!==next)throw Error('Ritual: fórmula do molde divergente');
    changes.push([cells[0],next]);
  });
  if(!spec.abaixo.some(function(t){return t[0]===3&&t[1]===343&&t[2]===13&&t[3]===347;}))
    throw Error('Ritual: replicação das vagas divergente');
  changes.forEach(function(p){p[0][2]=p[1];});
}
function preparar(before) {
  assert(!before.includes('function r53AjustarRitual_('),'Correção já instalada');
  const anchor=' if(R53_MODULO_.__estado().sobras.length)throw new Error(\'Gerações de dados misturadas no pacote.\');';
  assert.strictEqual(before.split(anchor).length,2,'Carregador divergente');
  const helper=ajustarRitual.toString().replace('function ajustarRitual(','function r53AjustarRitual_(');
  const after=before.replace(anchor,' try { r53AjustarRitual_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n'+anchor)+'\n// Ritual: mesmos requisitos na restauração e nas células; 25/10/2026.\n'+helper+'\n';
  new vm.Script(after);
  return after;
}
if(require.main===module){
  const [input,output]=process.argv.slice(2);
  assert(input&&output,'Informe captura e saída privada');
  fs.writeFileSync(output,preparar(fs.readFileSync(input,'utf8')),{flag:'wx'});
}
module.exports={preparar,ajustarRitual};
