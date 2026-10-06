// Roda no node, sem Sheets: pinta a ficha de fábrica com cada paleta, pelo mesmo convergirPaleta_ do Codigo.gs, e
// grava num .json a cor que cada célula, cada imagem e cada barra ficou. É a metade de conta do medidas/ver-paletas.py,
// que desenha o resultado para alguém olhar.
//
//   node medidas/pintar-paletas.js saida.json                       # as 122
//   node medidas/pintar-paletas.js saida.json "Alfazema · Claro"    # só as que forem ditas
//
// O Sheets de mentira é o mínimo que a troca usa: fundo e fonte em matriz, a imagem com a cor na descrição, a régua
// pelo que o setBorder recebeu, e os valores que a troca grava (a cor da barra, na DADOS).
const fs = require('fs'), vm = require('vm'), path = require('path');
const RAIZ = path.dirname(__dirname);
const FICHA_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script/Ficha.gs'), 'utf8') + '\n' + fs.readFileSync(path.join(RAIZ, 'apps-script/Invocacoes.gs'), 'utf8');
const CODIGO_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script/Codigo.gs'), 'utf8');
// onde o configurarPaleta_ põe a caixa da paleta na CARTEIRA: [linha, coluna, linhas, colunas, fundo, fonte]
const CAIXA = { PALETA_ROTULO: [26, 3, 1, 7, '#3D2E78', '#998BA9'], PALETA_ESCOLHIDA: [27, 3, 2, 11, '#1E1733', '#F4F1F7'],
                PALETA_AVISO: [29, 3, 1, 11, '#1E1733', '#998BA9'] };

const ctx0 = {}; vm.createContext(ctx0); vm.runInContext(FICHA_SRC, ctx0); const ABAS = ctx0.ABAS;

function fabrica() {
  const abas = {};
  for (const s of ABAS) {
    const bg0 = String(s.fundo_base === undefined ? '#120F1D' : s.fundo_base).toUpperCase();
    const fc0 = String((s.padrao || ['Roboto', 11, '#F4F1F7'])[2]).toUpperCase();
    const bg = [...Array(s.rows)].map(() => Array(s.cols).fill(bg0)), fc = [...Array(s.rows)].map(() => Array(s.cols).fill(fc0));
    (s.fundos || []).forEach(f => { for (let c = f[1]; c <= f[2]; c++) bg[f[0] - 1][c - 1] = String(f[3]).toUpperCase(); });
    (s.vals || []).forEach(t => { const e = t.length > 3 ? s.estilos[t[3]] : null; if (e && e[2]) fc[t[0] - 1][t[1] - 1] = String(e[2]).toUpperCase(); });
    const imgs = {}; (s.imgs || []).forEach(im => { imgs[im[0] + ',' + im[1]] = { nome: im[4], cor: 'fabrica' }; });
    abas[s.nome] = { bg, fc, imgs, valores: {}, vals: s.vals || [], rows: s.rows };
  }
  for (const [r, c, nl, nc, b, f] of Object.values(CAIXA))
    for (let i = r - 1; i < r - 1 + nl; i++) for (let j = c - 1; j < c - 1 + nc; j++) { abas.CARTEIRA.bg[i][j] = b; abas.CARTEIRA.fc[i][j] = f; }
  return abas;
}

function pinta(nome) {
  const abas = fabrica(), props = {}, bordas = {};
  // o valor de uma célula como o script a lê: o texto do ABAS, e o endereço quando a fórmula é um ADDRESS
  const valorDe = v => { if (typeof v !== 'string' || v[0] !== '=') return v;
    const m = /^=ADDRESS\(ROW\((?:'[^']+'|[A-ZÇÃ_]+)!\$?([A-Z]+)\$?(\d+)\)/.exec(v.replace(/\s/g, '')); return m ? m[1] + m[2] : ''; };
  const sheet = (n) => { const A = abas[n]; if (!A) return null; return {
    getName: () => n, getLastRow: () => A.rows,
    getRange: (r, c, nl, nc) => {
      if (typeof r === 'string') return { setValue: v => { A.valores[r] = v; }, getValue: () => A.valores[r] === undefined ? '' : A.valores[r] };
      if (nl !== undefined && n === 'DADOS') return { getValues: () => { const m = [...Array(nl)].map(() => Array(nc).fill(''));
        A.vals.forEach(t => { const i = t[0] - r, j = t[1] - c; if (i >= 0 && i < nl && j >= 0 && j < nc) m[i][j] = valorDe(t[2]); }); return m; } };
      if (nl === undefined) { const k = r + ',' + c; return {
        getValue: () => { const im = A.imgs[k]; if (n === 'CARTEIRA' && r === 27 && c === 3) return nome; if (!im) return A.valores[k] === undefined ? '' : A.valores[k];
          return { valueType: 'IMAGE', getAltTextTitle: () => 'PM-ARTE:' + im.nome, getAltTextDescription: () => im.cor }; },
        getBackground: () => A.bg[r - 1][c - 1],
        setValue: v => { if (A.imgs[k] && v && v.desc !== undefined) A.imgs[k].cor = v.desc; else A.valores[k] = v; },
        getA1Notation: () => '', getSheet: () => sheet(n) }; }
      return { getBackgrounds: () => A.bg.map(l => l.slice()), getFontColors: () => A.fc.map(l => l.slice()),
        setBackgrounds: m => { A.bg = m.map(l => l.slice()); }, setFontColors: m => { A.fc = m.map(l => l.slice()); } };
    },
    getRangeList: () => ({ setBorder: (t, l, b, r, v, h, cor) => { bordas[n] = cor; } }),
  }; };
  const celPaleta = { getA1Notation: () => 'C27', getSheet: () => sheet('CARTEIRA'), getValue: () => nome, getCell: () => celPaleta, setBorder: () => {} };
  const nomeado = k => { const [r, c, nl, nc] = CAIXA[k]; return { getA1Notation: () => '', getSheet: () => sheet('CARTEIRA'),
    getCell: () => k === 'PALETA_ESCOLHIDA' ? celPaleta : null, getRow: () => r, getColumn: () => c, getNumRows: () => nl, getNumColumns: () => nc, setBorder: () => {} }; };
  const ss = { getId: () => 'x', getSheetByName: sheet, getRangeByName: k => CAIXA[k] ? nomeado(k) : null, toast: () => {} };
  const ctx = { console: { log: () => {} }, Logger: { log: () => {} },
    Utilities: { base64Decode: s => Array.from(Buffer.from(s, 'base64')).map(x => (x > 127 ? x - 256 : x)),
                 base64Encode: a => Buffer.from(a.map(x => x & 255)).toString('base64'), sleep: () => {} },
    SpreadsheetApp: { getActive: () => ss, flush: () => {}, ValueType: { IMAGE: 'IMAGE' }, BorderStyle: new Proxy({}, { get: (o, k) => k }),
      newCellImage: () => { const b = { desc: null, setSourceUrl() { return b; }, setAltTextTitle() { return b; }, setAltTextDescription(d) { b.desc = d; return b; }, build() { return b; } }; return b; } },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger: () => {} },
    PropertiesService: { getDocumentProperties: () => ({ getProperty: k => (k in props ? props[k] : null), setProperty: (k, v) => { props[k] = String(v); },
      setProperties: o => { Object.assign(props, o); }, deleteProperty: k => { delete props[k]; } }) },
    LockService: { getDocumentLock: () => ({ tryLock: () => true, releaseLock: () => {} }) },
  };
  vm.createContext(ctx); vm.runInContext(FICHA_SRC, ctx); vm.runInContext(CODIGO_SRC, ctx);
  const parou = ctx.convergirPaleta_(Date.now(), Infinity);
  if (parou) throw new Error(nome + ': a troca parou em ' + parou);
  const cores = ctx.coresDoNome_(nome);
  const out = { papeis: {}, abas: {} };
  Object.keys(cores).forEach(k => { if (typeof cores[k] === 'string') out.papeis[k] = '#' + cores[k].toUpperCase(); });
  for (const s of ABAS) {
    if (s.oculta) { const v = abas[s.nome].valores, k = Object.keys(v);
      if (k.length) out.abas[s.nome] = { valores: Object.assign({ barra: k.map(x => v[x]).find(x => /^#[0-9A-F]{6}$/.test(String(x))) }, v) };
      continue; }
    const A = abas[s.nome], imgs = {};
    Object.keys(A.imgs).forEach(k => { imgs[k] = A.imgs[k].cor; });
    out.abas[s.nome] = { bg: A.bg, fc: A.fc, imgs, regua: bordas[s.nome] || null, valores: A.valores };
  }
  return out;
}

const saida = process.argv[2];
if (!saida) { console.error('uso: node medidas/pintar-paletas.js saida.json [paleta...]'); process.exit(2); }
const ctxN = {}; vm.createContext(ctxN); vm.runInContext(CODIGO_SRC.slice(CODIGO_SRC.indexOf('var PALETAS = {'), CODIGO_SRC.indexOf('var PALETA_DE_FABRICA_')), ctxN);
let nomes = process.argv.slice(3);
if (!nomes.length) Object.keys(ctxN.PALETAS).forEach(t => { nomes.push(t + ' · Claro'); nomes.push(t + ' · Escuro'); });
const tudo = {};
for (const n of nomes) tudo[n] = pinta(n);
fs.writeFileSync(saida, JSON.stringify(tudo));
console.log(nomes.length + ' paleta(s) -> ' + saida);
