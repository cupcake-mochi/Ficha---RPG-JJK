'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {formulas, blocoMontagens} = require('./preparar_fragil_fica');
const {linhas} = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./fragil_instantaneo_base.json');

const CODIGO_BASE = '9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR80');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function prepararCelulas(snapshot, selecionadas = linhas) {
  return planejarComBase(snapshot, selecionadas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_fragil_instantaneo.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
