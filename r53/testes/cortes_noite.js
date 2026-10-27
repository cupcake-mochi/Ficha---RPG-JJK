'use strict';
// O trecho do console dos cortes da noite de 26/10/2026 (preparar_cortes_noite.js), rodado num editor de mentira com os
// arquivos do projeto exportado (nuvem-b47/saidas/atalho/, fora do Git): grava o Codigo, o EditorR53 e o módulo iguais
// aos gerados no node; recusa sem gravar nada com um arquivo diferente do esperado. Depois, o projeto gravado roda no
// arnês: os três cortes valem juntos (habilidade custom com as marcas guardadas, XP, pontos de um cartão duas vezes).
const fs = require('fs'), path = require('path'), vm = require('vm'), zlib = require('zlib'), crypto = require('crypto'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const ok = (c, m) => { assert(c, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('cortes_noite: sem a ficha exportada, pulado'); process.exit(0); }
const projeto = JSON.parse(fs.readFileSync(fp, 'utf8')), dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
const { remendosDoProjeto, criar } = require('../arnes_custo');
if (remendosDoProjeto(projeto) !== 38) { console.log('cortes_noite: a exportação não é a das oficiais de 26/10 (38º remendo), pulado'); process.exit(0); }
const { gerar } = require('../diagnostico-android/preparar_cortes_noite');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const g = gerar(projeto);

async function rodar(arquivos) {
  const modelos = arquivos.map(f => ({ nome: f.name, v: f.source, getValue() { return this.v; }, setValue(x) { this.v = x; this.gravado = true; } }));
  const box = { monaco: { editor: { getModels: () => modelos } }, crypto: globalThis.crypto, TextEncoder, Response, Blob,
    DecompressionStream, CompressionStream, atob, btoa, Uint8Array, String, JSON, Error, Promise };
  vm.createContext(box);
  const r = await vm.runInContext('(async () => { return ' + g.trecho.replace(/^await /, '') + '; })()', box);
  return { r, modelos };
}
(async () => {
  // 1. Projeto como exportado: grava e sai igual ao node
  const { r, modelos } = await rodar(projeto.files);
  ok(typeof r === 'object', 'o trecho recusou: ' + r);
  const m = n => modelos.find(x => x.nome === n);
  eq(sha(m('Codigo').v), g.esperado.codigo, 'Codigo gravado');
  eq(sha(m('EditorR53').v), g.esperado.editor, 'EditorR53 gravado');
  const pedacos = modelos.map(x => /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(x.v)).filter(Boolean).sort((a, b) => a[2] - b[2]);
  eq(pedacos.length, 5, 'cinco pedaços');
  eq(sha(zlib.gunzipSync(Buffer.from(pedacos.map(x => JSON.parse(x[3])).join(''), 'base64')).toString('utf8')), g.esperado.modulo, 'módulo gravado');
  const intocados = projeto.files.filter(f => !['Codigo', 'EditorR53'].includes(f.name) && !/var R53_CODIGO_\d+_ = /.test(f.source));
  for (const f of intocados) eq(m(f.name).v, f.source, f.name + ' intocado');
  // 2. Arquivo diferente do esperado: recusa e não grava nada
  for (const [nome, troca] of [['Codigo', s => s + ' '], ['EditorR53', s => s.replace('function r53Menu_', 'function  r53Menu_')]]) {
    const outro = projeto.files.map(f => f.name === nome ? Object.assign({}, f, { source: troca(f.source) }) : f);
    const x = await rodar(outro);
    ok(typeof x.r === 'string' && /^ERRO, nada gravado/.test(x.r), nome + ' diferente não recusou');
    ok(x.modelos.every(y => !y.gravado), nome + ' diferente gravou algo');
  }
  // 3. O projeto gravado no arnês
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  for (const x of modelos) vm.runInContext(x.v + '\n', A.ctx, { filename: x.nome });
  vm.runInContext('r53Modulo_()', A.ctx);
  const editar = (aba, a1, v) => {
    const sh = A.ss.getSheetByName(aba), rg = sh.getRange(a1), c = sh.cel(rg.r, rg.c, true), old = c.v; c.v = v; delete c.f; A.reset();
    vm.runInContext('onEdit(__e)', Object.assign(A.ctx, { __e: { range: sh.getRange(a1), source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old } }));
    return A.log.filter(e => e.t === 'R').map(e => e.a);
  };
  editar('CONFIGURAÇÃO', 'AS51', 'Teste curto');
  const lidas = editar('CONFIGURAÇÃO', 'AS51', '');
  ok(!lidas.some(a => /^DADOS_PROGRESSAO!/.test(a)), 'habilidade custom com as marcas guardadas leu K7:K8: ' + lidas);
  ok(!editar('FICHA', 'AN11', 50).some(a => /^DADOS!/.test(a)), 'XP leu a DADOS');
  editar('FICHA AMALDIÇOADA', 'E71', 1);
  const cartao = editar('FICHA AMALDIÇOADA', 'E71', 0);
  ok(!cartao.some(a => /^MONTAGENS!/.test(a)), 'cartão leu a MONTAGENS com a versão guardada: ' + cartao);
  console.log('cortes_noite: ' + checks + ' verificações; Codigo ' + g.esperado.codigo.slice(0, 8) + ', EditorR53 ' + g.esperado.editor.slice(0, 8) +
    ', módulo ' + g.esperado.modulo.slice(0, 8) + '; leituras do cartão na segunda edição: ' + cartao.join(', '));
})().catch(err => { console.error(err); process.exit(1); });
