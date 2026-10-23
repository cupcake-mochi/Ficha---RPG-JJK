'use strict';
// VM com serviços simulados: migração de uma aba pequena e troca pelo tema. Não fala com o Sheets.
const vm = require('vm'), assert = require('assert'), path = require('path');
const {preparar} = require('../diagnostico-android/preparar_tema.js');
const pacote = preparar({files: [{name: 'Codigo', type: 'SERVER_JS', source: require('../diagnostico-android/preparar_tema.js').ANCORA},
                                 {name: 'appsscript', type: 'JSON', source: '{}'}]});
const tema = pacote.files.find(f => f.name === 'TemaPaleta').source;
const log = {vagas: {}, rl: [], batch: [], valores: {}, meta: null, props: {}};
const ctx = {console: {log() {}}, JSON, Math, Date, Object, String, Error};
vm.createContext(ctx);
vm.runInContext(tema, ctx);
const t = vm.runInContext('r53TemaCores_("Blush · Claro · rosa e coral")', ctx);
assert(t && t.fundo === 'FFF0F0');
const h = x => '#' + x.toLowerCase();
// 2x3: [fundo|acento|painel] / [menu_grande|bloco|tinta]; letras: texto, osso sobre acento, texto_fraco...
const fundos = [[h(t.fundo), h(t.acento), h(t.painel)], [h(t.menu_grande), h(t.bloco), h(t.tinta)]];
const fontes = [[h(t.texto), h(t.osso_por_papel.acento), '#123456'], [h(t.texto), h(t.texto_fraco), h(t.texto)]];
const cor = {build() { return Object.assign({}, this.v); }, setRgbColor(x) { this.v = {rgb: x}; return this; },
  setThemeColor(x) { this.v = {tema: x}; return this; }};
const A1 = (r, c, nr, nc) => String.fromCharCode(64 + c) + r + (nc > 1 ? ':' + String.fromCharCode(63 + c + nc) + r : '');
const abaFicha = {getName: () => 'CARTEIRA', getSheetId: () => 7, getMaxRows: () => 2, getMaxColumns: () => 3,
  getRange: (r, c, nr, nc) => typeof r === 'string' ? {getValue: () => ''} : ({
    getBackgrounds: () => fundos, getFontColors: () => fontes,
    setBackgroundObjects: o => { log.fundo = o; }, setFontColorObjects: o => { log.letra = o; },
    getA1Notation: () => A1(r, c, nr, nc), getDisplayValue: () => 'Blush · Claro'}),
  getRangeList: l => ({setBackground: x => log.rl.push(['f', x, l]), setFontColor: x => log.rl.push(['l', x, l])})};
const linhasTema = {};
const abaTema = {hideSheet() {}, getLastColumn: () => 2,
  getRange: (a, b, c, d) => typeof a === 'string' ? {setValues() {}, setValue(v) { linhasTema.A1 = v; }, getValue: () => linhasTema.A1 || 'migrando'}
    : {setValues: v => { linhasTema[a] = v[0]; }, getValues: () => [linhasTema[2] || ['', ''], ['', '']].slice(0, c)}};
let temAbaTema = false;
const ss = {getId: () => 'X', getSheetByName: n => n === 'CARTEIRA' ? Object.assign({}, abaFicha, {getRange: (r, c, nr, nc) => r === 'C27' ? {getDisplayValue: () => 'Blush · Claro · rosa e coral'} : abaFicha.getRange(r, c, nr, nc)})
    : n === 'R53_TEMA' ? (temAbaTema ? abaTema : null) : n === 'DADOS' ? {getRange: a => ({setValue: v => { log.valores[a] = v; }})} : null,
  insertSheet: () => { temAbaTema = true; return abaTema; },
  getSpreadsheetTheme: () => ({setConcreteColor: (k, c) => { log.vagas[k] = c.rgb; }}), setSpreadsheetTheme() {},
  createDeveloperMetadataFinder: () => ({withKey: () => ({find: () => []})}), addDeveloperMetadata: (k, v) => { log.meta = JSON.parse(v); }};
ctx.SpreadsheetApp = {getActive: () => ss, flush() {}, newColor: () => Object.create(cor),
  ThemeColorType: {TEXT: 'TEXT', BACKGROUND: 'BACKGROUND', ACCENT1: 'ACCENT1', ACCENT2: 'ACCENT2', ACCENT3: 'ACCENT3',
    ACCENT4: 'ACCENT4', ACCENT5: 'ACCENT5', ACCENT6: 'ACCENT6', HYPERLINK: 'HYPERLINK'}};
ctx.PropertiesService = {getDocumentProperties: () => ({getProperty: k => log.props[k] || null, setProperty: (k, v) => { log.props[k] = v; }, deleteProperty: k => { delete log.props[k]; }})};
const regua = {red: parseInt(t.regua.slice(0, 2), 16) / 255, green: parseInt(t.regua.slice(2, 4), 16) / 255, blue: parseInt(t.regua.slice(4), 16) / 255};
ctx.Sheets = {Spreadsheets: {get: () => ({sheets: [{data: [{rowData: [{values: [{userEnteredFormat: {borders: {top: {style: 'SOLID', color: regua}, left: {style: 'SOLID', colorStyle: {rgbColor: {red: 1}}}}}}]}]}]}]}),
  batchUpdate: b => log.batch.push(b)}};
ctx.R53_TEMA_ABAS_ = ['CARTEIRA'];
vm.runInContext('R53_TEMA_ABAS_ = ["CARTEIRA"]', ctx);
const res = vm.runInContext('migrarParaTema()', ctx);
assert.strictEqual(linhasTema.A1, 'ativo');
// fundos: fundo, painel, menu_grande, tinta pelo tema; acento e bloco ficam em hex e entram no resto
assert.deepStrictEqual(JSON.parse(JSON.stringify(log.fundo.map(l => l.map(x => x.tema || x.rgb)))), [['BACKGROUND', h(t.acento), 'ACCENT2'], ['HYPERLINK', h(t.bloco), 'ACCENT1']]);
assert.deepStrictEqual(JSON.parse(JSON.stringify(log.letra.map(l => l.map(x => x.tema || x.rgb)))), [['TEXT', h(t.osso_por_papel.acento), '#123456'], ['TEXT', h(t.texto_fraco), 'TEXT']]);
const resto = JSON.parse(linhasTema[2].slice(1).join(''));
assert.deepStrictEqual(resto, {'f:acento': ['B1'], 'o:acento': ['B1'], 'f:bloco': ['B2'], 't:texto_fraco': ['B2']});
const borda = JSON.parse(JSON.stringify(log.batch[0].requests[0].updateCells.rows[0].values[0].userEnteredFormat.borders));
assert.deepStrictEqual(borda.top.colorStyle, {themeColor: 'ACCENT5'});
assert.deepStrictEqual(borda.left.colorStyle, {rgbColor: {red: 1}});
assert.strictEqual(log.vagas.ACCENT5, '#' + t.regua); assert.strictEqual(log.vagas.ACCENT6, '#' + t.regua);
// Troca para outra paleta: só vagas, resto miúdo e barra
log.rl = []; log.vagas = {};
vm.runInContext('r53TemaTrocar_({value: "Noite · Escuro"})', ctx);
const n = vm.runInContext('r53TemaCores_("Noite · Escuro")', ctx);
assert.strictEqual(log.vagas.BACKGROUND, '#' + n.fundo); assert.strictEqual(log.vagas.HYPERLINK, '#' + n.menu_grande);
assert(log.rl.some(x => x[0] === 'f' && x[1] === '#' + n.acento && x[2][0] === 'B1'));
assert(log.rl.some(x => x[0] === 'l' && x[1] === '#' + n.osso_por_papel.acento));
assert.strictEqual(log.valores.CZ51, '#' + n.barra);
assert(log.meta && log.meta.paleta === 'Noite · Escuro');
console.log(JSON.stringify({resultado: 'OK', limite: 'VM com serviços simulados; não mede o Sheets nem o Android.'}));
