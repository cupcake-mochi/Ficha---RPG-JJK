'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {blocoMontagens} = require('./preparar_fragil_fica');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./forma_funcao_base.json');

const CODIGO_BASE = 'ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR82');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function formulas(pasta) {
  return alvos.formulas(pasta, [180]); // FX
}

function prepararCelulas(snapshot, selecionadas = alvos.linhas) {
  return planejarComBase(snapshot, selecionadas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_forma_funcao.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
