'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {formulas, blocoMontagens} = require('./preparar_fragil_fica');
const {linhas} = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./sem_volta_base.json');

const CODIGO_BASE = 'cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR77');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function prepararCelulas(snapshot, selecionadas = linhas) {
  return planejarComBase(snapshot, selecionadas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_sem_volta.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
