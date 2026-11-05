'use strict';
const fs = require('node:fs'), path = require('node:path');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {sha, trocar} = require('./preparar_recursos_fila');
const plano = require('./bencaos_imunidades_plano.json');
const BASE = 'a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac';
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
function planejar(snapshot,reverter=false) {
  const cells=snapshot.cells.map(d=>d.addr?d:{...d,value:normalizar(d.value)});
  const alvos=plano.map(d=>d.addr?d:{...d,antes:normalizar(d.antes),depois:normalizar(d.depois)});
  return planejarCelulas({...snapshot,cells},reverter,alvos);
}
module.exports={plano,molde,prepararCodigo,planejar,BASE};
