'use strict';

const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {norm} = require('./preparar_pratica_cotidiana');
const runtime = require('../pratica_cotidiana_runtime');
const plano = require('./classe_zero_plano.json');

const CODIGO_BASE = '6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8';
const EDITOR_BASE = '165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466';

function editorProposto() {
  const fonte = fs.readFileSync(path.join(__dirname, '../../apps-script/EditorR53.gs'), 'utf8');
  return require('../editor_lazy').preparar(fonte);
}

function reverterEditor(configuracao) {
  const anterior = JSON.parse(JSON.stringify(configuracao));
  for (const alvo of plano.filter(d => d.cartao)) {
    const contexto = anterior.contextos.find(g => g.id === alvo.cartao);
    if (contexto?.formulas[alvo.a1] !== alvo.depois) {
      throw Error('Recuperação de Classe 0 divergente: ' + alvo.cartao + '!' + alvo.a1);
    }
    contexto.formulas[alvo.a1] = alvo.antes;
  }
  return anterior;
}

function prepararEditor(src) {
  if (sha(src) !== EDITOR_BASE) throw Error('Editor exige a versão ensaiada da PR71');
  const payload = /Utilities.base64Decode\(("[^"]+")\)/.exec(src);
  const anterior = zlib.gunzipSync(Buffer.from(JSON.parse(payload[1]), 'base64')).toString('utf8');
  const novo = editorProposto();
  const corpo = s => s.slice(s.indexOf('var R53_EDITOR_=new Proxy'));
  if (JSON.stringify(reverterEditor(JSON.parse(novo.json))) !== anterior ||
      corpo(src) !== corpo(novo.code)) {
    throw Error('Editor mudou além das fórmulas de Classe 0');
  }
  return novo.code;
}

function molde() {
  const fonte = fs.readFileSync(path.join(__dirname, 'pilha_5156_molde.gs'), 'utf8');
  // O módulo antigo tem apenas as cinco linhas visíveis originais.
  const originais = plano.filter(d => d.aba === 'FICHA AMALDIÇOADA' && d.r <= 327);
  return 'var R53_CLASSE_ZERO_=' + JSON.stringify(originais) + ';\n' + fonte
    .replaceAll('r53AjustarPilha516_', 'r53AjustarClasseZero_')
    .replaceAll('R53_PILHA_516_', 'R53_CLASSE_ZERO_')
    .replaceAll('Pilha 51–56:', 'Classe 0:');
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR71');
  const anchor = 'r53AjustarConjuracao_(R53_MODULO_.__estado().abas);';
  const atalho = /^var R53_LIVRE_HASHES_=(\[[^\n]+\]);$/m.exec(src);
  if (!atalho) throw Error('Atalho do Editor ausente');
  const hashes = JSON.parse(atalho[1]);
  hashes[1] = editorProposto().hash;
  let novo = trocar(src, atalho[0], 'var R53_LIVRE_HASHES_=' + JSON.stringify(hashes) + ';');
  novo = trocar(novo, anchor, anchor + ' r53AjustarClasseZero_(R53_MODULO_.__estado().abas);');
  novo = trocar(novo, runtime.gerar([]), runtime.gerar(undefined, []));
  return novo + '\n' + molde();
}

function planejar(snapshot, reverter = false) {
  return planejarCelulas({
    ...snapshot,
    cells: snapshot.cells.map(x => ({...x, value: norm(x.value)})),
  }, reverter, plano.map(x => ({...x, antes: norm(x.antes), depois: norm(x.depois)})));
}

module.exports = {plano, molde, prepararCodigo, prepararEditor, reverterEditor, planejar};
