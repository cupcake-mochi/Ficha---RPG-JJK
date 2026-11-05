'use strict';
// Preparação offline. Aplicar só após uma leitura atual de todas as células e do código.
const fs = require('node:fs');
const path = require('node:path');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {sha, trocar} = require('./preparar_recursos_fila');
const plano = require('./integridade_movimento_plano.json');
const BASE = '3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7';

function molde() {
  const modelo = fs.readFileSync(path.join(__dirname, 'pilha_5156_molde.gs'), 'utf8')
    .replaceAll('r53AjustarPilha516_', 'r53AjustarIntegridadeMovimento_')
    .replaceAll('R53_PILHA_516_', 'R53_INTEGRIDADE_MOVIMENTO_')
    .replaceAll('Pilha 51–56:', 'Integridade e movimento:');
  return 'var R53_INTEGRIDADE_MOVIMENTO_ = ' + JSON.stringify(plano) + ';\n' + modelo;
}

function prepararCodigo(codigo) {
  if (sha(codigo) !== BASE) throw Error('Codigo.gs incompatível com a base ensaiada da PR62');
  const dados = 'R53_MODULO_.__estado().abas';
  const anterior = 'r53AjustarPilha516_(' + dados + ');';
  return trocar(codigo, anterior, anterior + ' r53AjustarIntegridadeMovimento_(' + dados + ');') + '\n' + molde();
}

// O modelo guarda a primeira linha; as fichas montadas já têm as doze fórmulas.
const emFormula = (s, f) => typeof s === 'string' && s.startsWith('=') ?
  s.split(/("(?:[^"]|"")*")/).map((t, i) => i % 2 ? t : f(t)).join('') : s;
const normalizar = s => emFormula(s, t => t.replace(/'([A-Za-z_][A-Za-z_0-9]*)'!/g, '$1!'));
function alvosNativos() {
  return plano.flatMap(d => {
    if (d.aba === 'DADOS_INVOC') {
      if (d.r !== 2) throw Error('Linha de molde da entidade divergente');
      return Array.from({length: 12}, (_, i) => {
        const r = i + 2;
        const traduz = s => emFormula(s, t => t.replace(/(\$[A-Z]{1,3})2\b/g, (_, c) => c + r));
        return {...d, r, antes: traduz(d.antes), depois: traduz(d.depois)};
      });
    }
    return [d];
  });
}

function planejar(snapshot, reverter = false) {
  const normal = {...snapshot, cells: snapshot.cells.map(d => d.addr ? d : {...d, value: normalizar(d.value)})};
  const alvos = alvosNativos().map(d => d.addr ? d : {...d, antes: normalizar(d.antes), depois: normalizar(d.depois)});
  return planejarCelulas(normal, reverter, alvos);
}

module.exports = {plano, alvosNativos, molde, prepararCodigo, planejar, BASE};
