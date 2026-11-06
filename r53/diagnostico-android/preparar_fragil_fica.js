'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');
const base = require('./fragil_fica_base.json');

const CODIGO_BASE = '6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769';
const colunas = [89, 94, 180]; // CK, CP, FX

function formulas(pasta) {
  return alvos.formulas(pasta).filter(d => colunas.includes(d.c));
}

function blocoMontagens(src) {
  const bloco = /^var R53_PRATICA_MONTAGEM_;\nfunction r53PraticaMontagem_\(\)\{[^\n]+\}\n/m.exec(src);
  if (!bloco) throw Error('Recuperação de montagens ausente');
  return bloco[0];
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR76');
  return trocar(src, blocoMontagens(src), blocoMontagens(runtime.gerar()));
}

function prepararCelulas(snapshot, linhas = alvos.linhas) {
  return planejarComBase(snapshot, linhas, formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_fragil_fica.js');
}

module.exports = {colunas, formulas, prepararCodigo, prepararCelulas};
