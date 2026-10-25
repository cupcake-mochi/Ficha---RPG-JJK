'use strict';
// Delta revisável; nunca publica nem toca em dados de personagens.
const fs=require('fs'),path=require('path'),vm=require('vm');
const helper=fs.readFileSync(path.join(__dirname,'../../salarios/missoes_integradas.gs'),'utf8').trimEnd()+'\n\n'+fs.readFileSync(path.join(__dirname,'../../salarios/missoes_diretas.gs'),'utf8')+'\nvar SALARIO_MISSOES_MOLDES_='+fs.readFileSync(path.join(__dirname,'../../salarios/missoes_moldes.json'),'utf8').trim()+';\n';
const antigo='if(SALARIO_.formula){if(missao&&!config&&salarioToca_(r,15,87,49,72))salarioSincronizar_(ss,st,hoje,false);return;}';
const novo='if(SALARIO_.formula){if(missao&&!config&&salarioToca_(r,15,87,49,72)){var ms=salarioSincronizar_(ss,st,hoje,false,true,!!e.salarioAntesGravar_);if(e.salarioAntesGravar_)e.salarioAntesGravar_();ms.gravar();}return;}';
function preparar(source){
 if(source.includes('function salarioIntegrarMissao_'))throw Error('Integração de missões já presente');
 if(source.split(antigo).length!==2)throw Error('Corpo salarial divergente');
 let out=source.replace(antigo,novo);
 const pairs=[
  ['function salarioMissoesAtuais_(ss) {','function salarioMissoesAtuais_(ss,agrupar) {'],
  ['out.faixa=faixa;out.notas=notas;out.limpar=[];','out.faixa=faixa;out.notas=notas;out.limpar=[];var matriz=agrupar?faixa.getValues():null;'],
  ['var v=pessoal.getRange(15,col,73,2).getValues();','var v=matriz?matriz.map(function(row){return row.slice(col-49,col-47);}):pessoal.getRange(15,col,73,2).getValues();'],
  ['function salarioSincronizar_(ss,estado,hoje,baseline,adiar) {','function salarioSincronizar_(ss,estado,hoje,baseline,adiar,agrupar) {'],
  ['var atuais=salarioMissoesAtuais_(ss),notesChanged=false;','var atuais=salarioMissoesAtuais_(ss,agrupar),notesChanged=false;']
 ];
 for(const [a,b] of pairs){if(out.split(a).length!==2)throw Error('Leitura de missões divergente');out=out.replace(a,b);}
 const wrapper='function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();';
 if(out.includes('r53OnEditOriginal_')){
  if(out.split(wrapper).length!==2)throw Error('Entrada instalada divergente');
  out=out.replace(wrapper,wrapper+'if(salarioIntegrarMissao_(e,function(ev){return r53Modulo_().onEdit(ev);}))return;');
 }
 out=helper+out;new vm.Script(out);return out;
}
if(require.main===module){const [input,output]=process.argv.slice(2);fs.writeFileSync(output,preparar(fs.readFileSync(input,'utf8')));}
module.exports={preparar,antigo,novo};
