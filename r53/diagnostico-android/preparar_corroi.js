'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {blocoMontagens} = require('./preparar_fragil_fica');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./corroi_base.json');

const CODIGO_BASE = 'cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR83');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function formulas(pasta) {
  return alvos.formulas(pasta, [180]); // FX
}

function prepararCelulas(snapshot, selecionadas = alvos.linhas) {
  return planejarComBase(snapshot, selecionadas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_corroi.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
