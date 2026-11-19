'use strict';

const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarComBase, escreverEntrega} = require('./preparar_rajada_alvos');
const {blocoMontagens} = require('./preparar_fragil_fica');
const alvos = require('../rajada_alvos');
const liberacoes = require('../liberacoes');
const runtime = require('../pratica_cotidiana_runtime');

const CODIGO_BASE = 'da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e';
const base = Object.fromEntries(['pt_BR', 'en_US'].map(locale => [
  locale, alvos.linhas.map(() => sha(JSON.stringify(['=""']))),
]));

function faixaMontagens(src) {
  const bloco = /^ if\(!anterior&&!\(([^\n]+)\)\)return false;$/m.exec(src);
  if (!bloco) throw Error('Guarda de recuperação de montagens ausente');
  return bloco[1];
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR84');
  const novo = runtime.gerar();
  let saida = trocar(src, blocoMontagens(src), blocoMontagens(novo));
  const antes = faixaMontagens(saida);
  if (saida.split(antes).length !== 3) throw Error('Duas guardas de montagem obrigatórias');
  return saida.split(antes).join(faixaMontagens(novo));
}

function prepararCelulas(snapshot) {
  return planejarComBase(snapshot, liberacoes.linhas, liberacoes.formulas(), base);
}

if (require.main === module) {
  escreverEntrega(process.argv.slice(2), prepararCodigo, prepararCelulas, 'preparar_liberacoes.js');
}

module.exports = {formulas: liberacoes.formulas, prepararCodigo, prepararCelulas, faixaMontagens};
