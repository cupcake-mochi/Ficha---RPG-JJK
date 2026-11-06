'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {formulas, blocoMontagens} = require('./preparar_fragil_fica');
const {linhas} = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./fragil_catalogo_base.json');

const CODIGO_BASE = 'e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR81');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function prepararCelulas(snapshot, selecionadas = linhas) {
  return planejarComBase(snapshot, selecionadas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_fragil_catalogo.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
