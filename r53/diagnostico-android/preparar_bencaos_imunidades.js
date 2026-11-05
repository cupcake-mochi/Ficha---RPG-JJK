'use strict';
const fs = require('node:fs'), path = require('node:path');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {sha, trocar} = require('./preparar_recursos_fila');
const plano = require('./bencaos_imunidades_plano.json');
const BASE = 'a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac';
const BASE_REVISAO = '170273ca8ecb3f7da41310dc1e15c37f89894775a4c16ebfa1af30f429c34310';
const normalizar = s => typeof s === 'string' && s.startsWith('=') ?
  s.split(/("(?:[^"]|"")*")/).map((t,i)=>i%2?t:t.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g,'$1!')).join('') : s;
function molde() {
  return 'var R53_BENCAOS_IMUNIDADES_ = ' + JSON.stringify(plano) + ';\n' +
    fs.readFileSync(path.join(__dirname,'pilha_5156_molde.gs'),'utf8')
      .replaceAll('r53AjustarPilha516_','r53AjustarBencaosImunidades_')
      .replaceAll('R53_PILHA_516_','R53_BENCAOS_IMUNIDADES_')
      .replaceAll('Pilha 51–56:','Bênçãos e imunidades:');
}
function prepararCodigo(codigo) {
  if(sha(codigo)!==BASE)throw Error('Codigo.gs incompatível com PR64 ensaiada');
  const ancora='r53AjustarEquipamento_(R53_MODULO_.__estado().abas);';
  return trocar(codigo,ancora,ancora+' r53AjustarBencaosImunidades_(R53_MODULO_.__estado().abas);')+'\n'+molde();
}
function atualizarCodigoRevisao(codigo) {
  if(sha(codigo)!==BASE_REVISAO)throw Error('Codigo.gs incompatível com a revisão anterior da PR65');
  const ancora='\nvar R53_BENCAOS_IMUNIDADES_ = ';
  if(codigo.split(ancora).length!==2)throw Error('Molde de Bênçãos divergente');
  return codigo.slice(0,codigo.lastIndexOf(ancora))+'\n'+molde();
}
function planejarCom(snapshot,reverter,entradas) {
  const cells=snapshot.cells.map(d=>d.addr?d:{...d,value:normalizar(d.value)});
  const alvos=entradas.map(d=>d.addr?d:{...d,antes:normalizar(d.antes),depois:normalizar(d.depois)});
  return planejarCelulas({...snapshot,cells},reverter,alvos);
}
const planejar=(snapshot,reverter=false)=>planejarCom(snapshot,reverter,plano);
const planejarRevisao=(snapshot,reverter=false)=>planejarCom(snapshot,reverter,require('./imunidade_custom_revisao_plano.json'));
module.exports={plano,molde,prepararCodigo,planejar,BASE,BASE_REVISAO,atualizarCodigoRevisao,planejarRevisao};
