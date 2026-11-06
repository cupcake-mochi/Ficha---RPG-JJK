'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./restricoes_agrupadas_base.json');

const CODIGO_BASE = '30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658';
const colunas = [89, 94, 104]; // CK, CP, CZ

function formulas(pasta) {
  return alvos.formulas(pasta, colunas);
}

function blocoRecuperacao(src) {
  const bloco = /^\/\/ GERADO por r53\/pratica_cotidiana_runtime\.js\.[^\n]*\n[\s\S]*?^}\n/m.exec(src);
  if (!bloco) throw Error('Recuperação de Prática Cotidiana ausente');
  return bloco[0];
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR79');
  return trocar(src, blocoRecuperacao(src), runtime.gerar());
}

function prepararCelulas(snapshot, linhas = alvos.linhas) {
  return planejarComBase(snapshot, linhas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_restricoes_agrupadas.js');
}

module.exports = {formulas, blocoRecuperacao, prepararCodigo, prepararCelulas};
