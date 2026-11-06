'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {blocoMontagens} = require('./preparar_fragil_fica');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./devolucoes_incompativeis_base.json');

const CODIGO_BASE = '01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e';
const colunas = [89, 94]; // CK, CP

function formulas(pasta) {
  return alvos.formulas(pasta).filter(d => colunas.includes(d.c));
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR78');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function prepararCelulas(snapshot, linhas = alvos.linhas) {
  return planejarComBase(snapshot, linhas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_devolucoes_incompativeis.js');
}

module.exports = {formulas, prepararCodigo, prepararCelulas};
