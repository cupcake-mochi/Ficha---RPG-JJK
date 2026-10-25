'use strict';
// Monta o teste de troca em lote único para uma cópia descartável: LotePaleta.gs com as PALETAS da fonte e o onEdit da
// CARTEIRA!C27 desviado para ele. Não executa nada na planilha.
// Uso: node r53/diagnostico-android/preparar_lote.js <conteúdo do projeto .json> <saída .json>
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const {ANCORA} = require('./preparar_tema.js');
const NOVO = 'if(e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27")return r53LoteTrocar_(e);';
function paletas() {
  const src = fs.readFileSync(path.resolve(__dirname, '../../apps-script/Codigo.gs'), 'utf8');
  const i = src.indexOf('var PALETAS = ');
  let d = 0, j = src.indexOf('{', i);
  const s = j;
  for (;; j++) { if (src[j] === '{') d++; else if (src[j] === '}') { d--; if (!d) break; } }
  return JSON.parse(src.slice(s, j + 1));
}
function arte() {
  const ctx = {};
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.resolve(__dirname, '../../apps-script/Ficha.gs'), 'utf8'), ctx);
  const ARTE = vm.runInContext('ARTE', ctx), imgs = {}, usadas = {};
  vm.runInContext('ABAS', ctx).forEach(a => (a.imgs || []).forEach(im => {
    (imgs[a.nome] = imgs[a.nome] || []).push([im[0], im[1], im[4]]);
    usadas[im[4]] = ARTE[im[4]];
  }));
  return {arte: usadas, imgs};
}
function preparar(conteudo) {
  const tpl = fs.readFileSync(path.join(__dirname, 'lote_paleta.gs'), 'utf8');
  if (tpl.split('/*PALETAS*/null').length !== 2) throw Error('Marcador de PALETAS ausente');
  const a = arte();
  const lote = tpl.replace('/*PALETAS*/null', () => JSON.stringify(paletas()))
    .replace('/*ARTE*/null', () => JSON.stringify(a.arte)).replace('/*IMGS*/null', () => JSON.stringify(a.imgs));
  new vm.Script(lote);
  const files = conteudo.files.map(f => Object.assign({}, f));
  if (files.some(f => f.name === 'LotePaleta')) throw Error('LotePaleta já instalado');
  const cod = files.find(f => f.name === 'Codigo');
  if (cod.source.split(ANCORA).length !== 2) throw Error('Âncora do onEdit divergente');
  cod.source = cod.source.replace(ANCORA, () => NOVO);
  files.push({name: 'LotePaleta', type: 'SERVER_JS', source: lote});
  return {files, sha_lote: crypto.createHash('sha256').update(lote).digest('hex')};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  const r = preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')));
  fs.writeFileSync(saida, JSON.stringify({files: r.files}));
  console.log(JSON.stringify({arquivos: r.files.length, sha_lote: r.sha_lote}));
}
module.exports = {preparar, NOVO};
