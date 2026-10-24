'use strict';
// VM com serviços simulados: mapearLote() acha a paleta pintada e grava o mapa; a troca lê só o mapa, grava por papel
// e faz um flush no fim. Não fala com o Sheets.
const vm = require('vm'), assert = require('assert');
const {preparar, NOVO} = require('../diagnostico-android/preparar_lote.js');
const {ANCORA} = require('../diagnostico-android/preparar_tema.js');
const p = preparar({files: [{name: 'Codigo', type: 'SERVER_JS', source: ANCORA}]});
assert.strictEqual(p.files[0].source, NOVO);
const ctx = {console: {log() {}}};
vm.createContext(ctx);
vm.runInContext(p.files.find(f => f.name === 'LotePaleta').source, ctx);
const A = vm.runInContext('r53LoteCores_("Blush · Claro · rosa e coral")', ctx), N = vm.runInContext('r53LoteCores_("Noite · Escuro")', ctx);
const h = x => '#' + x.toLowerCase();
// Faixas: duas linhas iguais emendam; célula fixa fica de fora.
assert.deepStrictEqual(JSON.parse(JSON.stringify(vm.runInContext('r53LoteFaixas_([["a","a",null],["a","a","b"]])', ctx))), {a: ['A1:B2'], b: ['C2']});
assert.strictEqual(vm.runInContext('r53LoteA1_(0, 27)', ctx), 'AB1');
const ordem = [], grav = {};
const fundos = [[h(A.fundo), h(A.acento), '#123456'], [h(A.fundo), h(A.painel), h(A.painel)]];
const letras = [[h(A.texto), h(A.osso_por_papel.acento), '#123456'], [h(A.texto), h(A.linha), h(A.texto)]];
let mapaGravado = null;
const aba = nome => ({getMaxRows: () => 2, getMaxColumns: () => 3,
  getName: () => nome,
  getRange: (r, c) => ({getBackgrounds: () => (ordem.push('ler'), fundos), getFontColors: () => letras, getA1Notation: () => 'A1:C2',
    setValue: v => { grav[nome + ' img ' + r + ',' + c] = v; }}),
  getRangeList: lista => ({setBackground: c => { ordem.push('gravar'); lista.forEach(a => grav[nome + ' b ' + a] = c); },
                           setFontColor: c => { lista.forEach(a => grav[nome + ' f ' + a] = c); },
                           setBorder: (t, l, b, r, v, h, c, e) => { lista.forEach(a => grav[nome + ' r ' + [t, l, b, r].map(x => x ? 1 : 0).join('') + ' ' + a] = c + ' ' + e); }})});
const mapaAba = {getRange: () => ({setNumberFormat() { return this; }, setValues: v => { mapaGravado = v; },
  getValues: () => (ordem.push('ler mapa'), mapaGravado)}), hideSheet() {}};
let temMapa = false;
const ss = {getSheetByName: n => n === 'DADOS' ? {getRange: () => ({setValue: v => { grav.barra = v; }})}
  : n === 'R53_LOTE' ? (temMapa ? mapaAba : null) : n === 'CARTEIRA' ? aba(n) : null,
  insertSheet: () => (temMapa = true, mapaAba)};
// Bordas: topo nas duas primeiras células da linha 1 (um trecho só), esquerda em A1 e A2 (um trecho de coluna).
const sol = {style: 'SOLID_MEDIUM'};
ctx.Sheets = {Spreadsheets: {get: () => ({sheets: [{data: [{rowData: [
  {values: [{userEnteredFormat: {borders: {top: sol, left: sol}}}, {userEnteredFormat: {borders: {top: sol}}}, {}]},
  {values: [{userEnteredFormat: {borders: {left: sol}}}, {}, {}]}]}]}]})}};
ctx.Utilities = {base64Decode: s => Array.from(Buffer.from(s, 'base64')).map(b => b > 127 ? b - 256 : b),
  base64Encode: a => Buffer.from(a.map(b => b & 255)).toString('base64')};
const construtor0 = {setSourceUrl() { return this; }, setAltTextTitle() { return this; }, setAltTextDescription(d) { this.d = d; return this; }, build() { return this.d; }};
ctx.SpreadsheetApp = {getActive: () => ss, flush: () => ordem.push('flush'), BorderStyle: {SOLID_MEDIUM: 'SM'},
  newCellImage: () => Object.create(construtor0)};
ss.getId = () => 'x';
vm.runInContext('mapearLote()', ctx);
const mapa = JSON.parse(mapaGravado.map(l => l[0]).join(''));
assert.strictEqual(mapa.paleta.split(' · ')[0], 'Blush');
ordem.length = 0;
vm.runInContext('r53LoteTrocar_({value: "Noite · Escuro"})', ctx);
assert.strictEqual(ordem[0], 'ler mapa'); assert.strictEqual(ordem[ordem.length - 1], 'flush');
assert(!ordem.includes('ler'));
assert.strictEqual(grav['CARTEIRA b A1:A2'], '#' + N.fundo);
assert.strictEqual(grav['CARTEIRA b B1'], '#' + N.acento);
assert.strictEqual(grav['CARTEIRA b B2:C2'], '#' + N.painel);
assert(!Object.keys(grav).some(k => k.endsWith(' C1')));
assert.strictEqual(grav['CARTEIRA f B1'], '#' + N.osso_por_papel.acento);
assert.strictEqual(grav['CARTEIRA f B2'], '#' + N.linha);
assert.strictEqual(grav.barra, '#' + N.barra);
assert.strictEqual(grav['CARTEIRA r 1000 A1:B1'], '#' + N.regua + ' SM');
assert.strictEqual(grav['CARTEIRA r 0100 A1:A2'], '#' + N.regua + ' SM');
assert.strictEqual(Object.keys(grav).filter(k => k.includes(' r ')).length, 2);
const cantos = vm.runInContext('R53_LOTE_IMGS_.CARTEIRA', ctx).filter(i => /canto/.test(i[2]));
assert(cantos.length === 2 && cantos.every(i => grav['CARTEIRA img ' + i[0] + ',' + i[1]] === '#' + N.regua.toUpperCase()));
console.log(JSON.stringify({resultado: 'OK', limite: 'VM com serviços simulados; não mede o Sheets nem o Android.'}));
// Bordas: toda borda vira #857F99 com o mesmo estilo; lado sem borda fica de fora; um batchUpdate só.
const lotes = [];
ctx.Sheets = {Spreadsheets: {
  get: () => ({sheets: [{data: [{rowData: [{values: [{userEnteredFormat: {borders: {top: {style: 'SOLID_MEDIUM', colorStyle: {rgbColor: {red: 1}}}, left: {style: 'NONE'}}}}]}]}]}]}),
  batchUpdate: (b) => lotes.push(b)}};
const sh1 = {getMaxRows: () => 1, getMaxColumns: () => 1, getSheetId: () => 7, getRange: () => ({getA1Notation: () => 'A1'})};
ctx.SpreadsheetApp = {getActive: () => ({getId: () => 'x', getSheetByName: n => n === 'CARTEIRA' || n === 'FICHA' ? sh1 : null})};
vm.runInContext('fixarBordasLote()', ctx);
assert.strictEqual(lotes.length, 1); assert.strictEqual(lotes[0].requests.length, 2);
const bd = JSON.parse(JSON.stringify(lotes[0].requests[0].updateCells.rows[0].values[0].userEnteredFormat.borders));
assert.deepStrictEqual(Object.keys(bd), ['top']); assert.strictEqual(bd.top.style, 'SOLID_MEDIUM');
assert.strictEqual(Math.round(bd.top.colorStyle.rgbColor.red * 255), 0x85);
console.log(JSON.stringify({bordas: 'OK'}));
// Arte: a pincelada sai com o PLTE todo em #857F99 e o CRC certo; a imagem sem o título PM-ARTE: não é tocada.
const zlib = require('zlib');
ctx.Utilities = {base64Decode: s => Array.from(Buffer.from(s, 'base64')).map(b => b > 127 ? b - 256 : b),
  base64Encode: a => Buffer.from(a.map(b => b & 255)).toString('base64')};
const nomeArte = vm.runInContext('R53_LOTE_IMGS_.CARTEIRA[0][2]', ctx);
const png = Buffer.from(vm.runInContext('r53LotePng_(R53_LOTE_ARTE_["' + nomeArte + '"], "#857F99")', ctx), 'base64');
let pos = 8, achou = false;
while (pos + 12 <= png.length) {
  const len = png.readUInt32BE(pos), tipo = png.toString('latin1', pos + 4, pos + 8);
  if (tipo === 'PLTE') {
    for (let i = 0; i < len; i += 3) assert.deepStrictEqual([...png.subarray(pos + 8 + i, pos + 11 + i)], [0x85, 0x7F, 0x99]);
    assert.strictEqual(png.readUInt32BE(pos + 8 + len), zlib.crc32(png.subarray(pos + 4, pos + 8 + len)));
    achou = true;
  }
  pos += 12 + len;
}
assert(achou);
const postas = [];
const celula = titulo => ({getValue: () => ({valueType: 'IMG', getAltTextTitle: () => titulo}), setValue: v => postas.push(v), getA1Notation: () => 'X'});
const shArte = {getRange: (r, c) => celula(r === 7 ? 'foto do jogador' : 'PM-ARTE:' + vm.runInContext('R53_LOTE_IMGS_.CARTEIRA', ctx).find(i => i[0] === r)[2])};
const construtor = {setSourceUrl() { return this; }, setAltTextTitle() { return this; }, setAltTextDescription(d) { this.d = d; return this; }, build() { return this.d; }};
ctx.SpreadsheetApp = {ValueType: {IMAGE: 'IMG'}, newCellImage: () => Object.create(construtor),
  getActive: () => ({getSheetByName: n => n === 'CARTEIRA' ? shArte : null})};
vm.runInContext('fixarArteLote()', ctx);
assert.strictEqual(postas.length, vm.runInContext('R53_LOTE_IMGS_.CARTEIRA.length', ctx) - 1);
assert(postas.every(d => d === '#857F99'));
console.log(JSON.stringify({arte: 'OK', imagens_carteira: postas.length}));
