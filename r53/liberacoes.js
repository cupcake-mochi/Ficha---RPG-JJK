'use strict';

const alvos = require('./rajada_alvos');
const linhas = [38, 39, 40];
function formulas(pasta) {
  return alvos.formulas(pasta, [183]).filter(d => linhas.includes(d.r)); // GA
}
module.exports = {formulas, linhas};
