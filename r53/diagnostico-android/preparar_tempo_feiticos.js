'use strict';

const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarCelulas} = require('./preparar_pilha_5156');
const {norm} = require('./preparar_pratica_cotidiana');
const plano = require('./tempo_feiticos_plano.json');
const runtime = require('../pratica_cotidiana_runtime');

const CODIGO_BASE = '2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b';
const EDITOR_BASE = '2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928';

function editorProposto() {
  const raw = fs.readFileSync(path.join(__dirname, '../../apps-script/EditorR53.gs'), 'utf8');
  return require('../editor_lazy').preparar(raw);
}

function reverterEditor(configuracao) {
  const original = JSON.parse(JSON.stringify(configuracao));
  for (const alvo of plano.filter(d => d.cartao)) {
    const contexto = original.contextos.find(g => g.id === alvo.cartao);
    if (contexto?.formulas[alvo.a1] !== alvo.depois) {
      throw new Error('Recuperação do cartão divergente: ' + alvo.cartao);
    }
    contexto.formulas[alvo.a1] = alvo.antes;
  }
  return original;
}

function prepararEditor(src) {
  if (sha(src) !== EDITOR_BASE) throw new Error('Editor exige a versão ensaiada da PR74');
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
  return 'var R53_TEMPO_FEITICOS_=' + JSON.stringify(plano.filter(d => d.cartao)) + ';\n' + fonte
    .replaceAll('r53AjustarPilha516_', 'r53AjustarTempoFeiticos_')
    .replaceAll('R53_PILHA_516_', 'R53_TEMPO_FEITICOS_')
    .replaceAll('Pilha 51–56:', 'Tempo dos feitiços:');
}

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw new Error('Código exige a versão ensaiada da PR74');
  const anchor = 'r53AjustarAlcanceBeneficios_(R53_MODULO_.__estado().abas);';
  const hashLine = /^var R53_LIVRE_HASHES_=(\[[^\n]+\]);$/m.exec(src);
  if (!hashLine) throw new Error('Atalho do editor ausente');
  const hashes = JSON.parse(hashLine[1]);
  hashes[1] = editorProposto().hash;
  let novo = trocar(src, hashLine[0], 'var R53_LIVRE_HASHES_=' + JSON.stringify(hashes) + ';');
  novo = trocar(novo, anchor, anchor + ' r53AjustarTempoFeiticos_(R53_MODULO_.__estado().abas);');
  novo = trocar(novo, runtime.gerar(undefined, []), runtime.gerar());
  return novo + '\n' + molde();
}

function planejar(snapshot, reverter = false) {
  return planejarCelulas({
    ...snapshot,
    cells: snapshot.cells.map(x => ({...x, value: norm(x.value)})),
  }, reverter, plano.map(x => ({...x, antes: norm(x.antes), depois: norm(x.depois)})));
}

module.exports = {plano, molde, prepararCodigo, prepararEditor, reverterEditor, planejar};
