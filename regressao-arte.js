// Roda no node, sem Sheets: a recoloração da arte (pngComCor_, do Codigo.gs) contra os PNGs que o Ficha.gs
// realmente embute. Nenhum valor esperado escrito aqui além da cor de teste.
//
// O que ele prova, pra CADA imagem do ARTE:
//   · o PNG de saída é um PNG bem formado — assinatura, e o CRC de TODO bloco confere, calculado aqui por um
//     CRC-32 próprio, sem usar o do Codigo.gs;
//   · o bloco PLTE tem a cor pedida em todas as entradas, e SÓ ele mudou: cabeçalho (IHDR), transparência
//     (tRNS) e pixels (IDAT) saem byte a byte iguais aos de entrada — ou seja, o alfa, que é a textura do
//     pincel, não foi tocado;
//   · o que o construir() grava (a cor de fábrica) também é PNG de paleta, com 256 entradas iguais e a rampa
//     de alfa 0..255 na tRNS — a condição pra o recolorir funcionar.
//
//   node regressao-arte.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const RAIZ = __dirname;
const codigo = fs.readFileSync(path.join(RAIZ, 'apps-script/Codigo.gs'), 'utf-8');
const ficha = fs.readFileSync(path.join(RAIZ, 'apps-script/Ficha.gs'), 'utf-8');
const m = ficha.match(/var ARTE = (\{[\s\S]*?\n\});/);
const ARTE = JSON.parse(m[1].replace(/"\s*\+\s*\n?\s*"/g, ''));

const sb = {
  Utilities: {
    base64Decode: s => Array.from(Buffer.from(s, 'base64')).map(x => (x > 127 ? x - 256 : x)),
    base64Encode: a => Buffer.from(a.map(x => x & 255)).toString('base64'),
  },
};
vm.createContext(sb);
// só as funções da arte, sem carregar o PALETAS de 200 KB
const ini = codigo.indexOf('var CRC_TABELA_ = null;');
const fim = codigo.indexOf('/**\n * Recolore cada imagem NOSSA');
vm.runInContext(codigo.slice(ini, fim), sb);

// CRC-32 independente do do Codigo.gs
const T = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; T.push(c >>> 0); }
const crc = b => { let c = 0xFFFFFFFF; for (const x of b) c = T[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };

function blocos(buf) {
  if (buf.slice(0, 8).toString('hex') !== '89504e470d0a1a0a') throw new Error('assinatura de PNG inválida');
  const out = []; let p = 8;
  while (p < buf.length) {
    const len = buf.readUInt32BE(p), tipo = buf.slice(p + 4, p + 8).toString('latin1');
    const dados = buf.slice(p + 8, p + 8 + len), c = buf.readUInt32BE(p + 8 + len);
    out.push({ tipo, dados, crcOk: crc(buf.slice(p + 4, p + 8 + len)) === c });
    p += 12 + len;
  }
  return out;
}

let falhas = 0, n = 0;
const checa = (nome, ok, det) => { n++; if (!ok) { falhas++; console.log('  [FALHA] ' + nome + (det ? '  <- ' + det : '')); } };

const COR = '#3A7BC8', RGB = [0x3A, 0x7B, 0xC8];
Object.keys(ARTE).forEach(chave => {
  const orig = Buffer.from(ARTE[chave], 'base64');
  const bo = blocos(orig);
  const plte0 = bo.find(b => b.tipo === 'PLTE'), trns0 = bo.find(b => b.tipo === 'tRNS');
  checa(`${chave}: a arte embutida é PNG de paleta com 256 entradas`, !!plte0 && plte0.dados.length === 768);
  checa(`${chave}: todas as entradas da paleta de fábrica são iguais`, !!plte0 && [...Array(256).keys()].every(i => plte0.dados[i * 3] === plte0.dados[0] && plte0.dados[i * 3 + 1] === plte0.dados[1] && plte0.dados[i * 3 + 2] === plte0.dados[2]));
  checa(`${chave}: a tRNS é a rampa de alfa 0..255`, !!trns0 && trns0.dados.length === 256 && [...trns0.dados].every((v, i) => v === i));

  const novo = Buffer.from(sb.pngComCor_(ARTE[chave], COR), 'base64');
  const bn = blocos(novo);
  checa(`${chave}: todo bloco do PNG recolorido tem o CRC certo`, bn.every(b => b.crcOk), bn.filter(b => !b.crcOk).map(b => b.tipo).join());
  checa(`${chave}: mesma sequência de blocos`, bn.map(b => b.tipo).join() === bo.map(b => b.tipo).join());
  const plte1 = bn.find(b => b.tipo === 'PLTE');
  checa(`${chave}: as 256 entradas da paleta viram a cor pedida`, plte1.dados.length === 768 && [...Array(256).keys()].every(i => plte1.dados[i * 3] === RGB[0] && plte1.dados[i * 3 + 1] === RGB[1] && plte1.dados[i * 3 + 2] === RGB[2]));
  const igual = t => Buffer.compare(bo.filter(b => b.tipo === t).reduce((a, b) => Buffer.concat([a, b.dados]), Buffer.alloc(0)),
                                    bn.filter(b => b.tipo === t).reduce((a, b) => Buffer.concat([a, b.dados]), Buffer.alloc(0))) === 0;
  checa(`${chave}: o cabeçalho, a transparência e os pixels não mudaram um byte`, igual('IHDR') && igual('tRNS') && igual('IDAT'));
  // e recolorir duas vezes dá o mesmo que recolorir uma (nada acumula)
  const duas = sb.pngComCor_(sb.pngComCor_(ARTE[chave], '#112233'), COR);
  checa(`${chave}: recolorir em cima de recolorido dá o mesmo PNG`, duas === Buffer.from(novo).toString('base64'));
});
checa('o ARTE tem as seis imagens da ficha', Object.keys(ARTE).length === 6, String(Object.keys(ARTE).length));
let erro = null; try { sb.pngComCor_(Buffer.from('iVBORw0KGgo=', 'base64').toString('base64'), COR); } catch (e) { erro = e.message; }
checa('um PNG sem paleta é recusado em voz alta, não recolorido errado', /sem bloco de paleta/.test(erro || ''), String(erro));

console.log(falhas ? `${falhas} FALHA(S) em ${n} checagens` : `a recoloração da arte passa: ${n} checagens, ${Object.keys(ARTE).length} imagens`);
process.exit(falhas ? 1 : 0);
