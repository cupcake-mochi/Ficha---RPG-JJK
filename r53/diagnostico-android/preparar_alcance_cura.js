'use strict';

const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {norm} = require('./preparar_pratica_cotidiana');
const plano = require('./alcance_cura_plano.json');

const CODIGO_BASE = 'e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e';
const EDITOR_BASE = '13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55';

function editorProposto() {
  const raw = fs.readFileSync(path.join(__dirname, '../../apps-script/EditorR53.gs'), 'utf8');
  return require('../editor_lazy').preparar(raw);
}

function reverterEditor(configuracao) {
  const original = JSON.parse(JSON.stringify(configuracao));
  for (const alvo of plano) {
    const contexto = original.contextos.find(g => g.id === alvo.cartao);
    if (contexto?.formulas[alvo.a1] !== alvo.depois) {
      throw new Error('Recuperação do cartão divergente: ' + alvo.cartao);
    }
    contexto.formulas[alvo.a1] = alvo.antes;
  }
  return original;
}

function prepararEditor(src) {
  if (sha(src) !== EDITOR_BASE) throw new Error('Editor exige a versão ensaiada da PR72');
  const payload = /Utilities.base64Decode\(("[^"]+")\)/.exec(src);
  const anterior = zlib.gunzipSync(Buffer.from(JSON.parse(payload[1]), 'base64')).toString('utf8');
  const novo = editorProposto();
  const cauda = s => s.slice(s.indexOf('var R53_EDITOR_=new Proxy'));
  if (JSON.stringify(reverterEditor(JSON.parse(novo.json))) !== anterior ||
      cauda(src) !== cauda(novo.code)) {
    throw new Error('Editor mudou além das fórmulas do resumo');
  }
  return novo.code;
}

function molde() {
  const fonte = fs.readFileSync(path.join(__dirname, 'pilha_5156_molde.gs'), 'utf8');
  return 'var R53_ALCANCE_CURA_=' + JSON.stringify(plano) + ';\n' + fonte
    .replaceAll('r53AjustarPilha516_', 'r53AjustarAlcanceCura_')
    .replaceAll('R53_PILHA_516_', 'R53_ALCANCE_CURA_')
    .replaceAll('Pilha 51–56:', 'Alcance de cura:');
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw new Error('Código exige a versão ensaiada da PR72');
  const anchor = 'r53AjustarClasseZero_(R53_MODULO_.__estado().abas);';
  const hashLine = /^var R53_LIVRE_HASHES_=(\[[^\n]+\]);$/m.exec(src);
  if (!hashLine) throw new Error('Atalho do editor ausente');
  const hashes = JSON.parse(hashLine[1]);
  hashes[1] = editorProposto().hash;
  let novo = trocar(src, hashLine[0], 'var R53_LIVRE_HASHES_=' + JSON.stringify(hashes) + ';');
  novo = trocar(novo, anchor, anchor + ' r53AjustarAlcanceCura_(R53_MODULO_.__estado().abas);');
  return novo + '\n' + molde();
}

function planejar(snapshot, reverter = false) {
  return planejarCelulas({
    ...snapshot,
    cells: snapshot.cells.map(x => ({...x, value: norm(x.value)})),
  }, reverter, plano.map(x => ({...x, antes: norm(x.antes), depois: norm(x.depois)})));
}

module.exports = {plano, molde, prepararCodigo, prepararEditor, reverterEditor, planejar};
