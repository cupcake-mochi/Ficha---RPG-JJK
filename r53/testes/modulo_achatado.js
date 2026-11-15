'use strict';
// Módulo achatado: o código que o new Function recebe é idêntico antes e depois; defeitos plantados acendem.
// node r53/testes/modulo_achatado.js
const assert = require('assert'), zlib = require('zlib'), crypto = require('crypto'), vm = require('vm');
const A = require('../diagnostico-android/preparar_modulo_achatado.js');

const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const gz64 = s => zlib.gzipSync(Buffer.from(s, 'utf8'), { level: 9 }).toString('base64');

// Módulo de mentira com a mesma forma do instalado: globais, entradas e __estado.
const ORIGINAL = "var ABAS=[{nome:'A'}],SOBRAS_=[];function f(){return 'velho';}\n" +
  "return {f:f,__estado:function(){return {abas:ABAS,sobras:SOBRAS_};}};";
// Remendos nas duas formas que os preparadores instalam (lista com forEach e IIFE com guarda).
const REMENDOS = [
  " var ajustesDescanso = [[\"return 'velho';\", \"return 'novo';\"]];",
  ' ajustesDescanso.forEach(function(par) {',
  "   if (code.split(par[0]).length !== 2) throw new Error('Trecho de descanso divergente.');",
  '   code = code.replace(par[0], function() { return par[1]; });',
  ' });',
  "(function(){var mudancas=[[\"nome:'A'\",\"nome:'B'\"]];",
  'mudancas.forEach(function(m){if(code.split(m[0]).length!==2)throw Error("Origem/recursos: fonte divergente");});',
  'mudancas.forEach(function(m){code=code.replace(m[0],function(){return m[1];});});})();'].join('\n');
const ESPERADO = ORIGINAL.replace("return 'velho';", "return 'novo';").replace("nome:'A'", "nome:'B'");

function instalado(original, remendos, opcoes) {
  opcoes = opcoes || {};
  const b64 = gz64(original), n = opcoes.partes || 3, passo = Math.ceil(b64.length / n);
  const pedacos = []; for (let i = 0; i < b64.length; i += passo) pedacos.push(b64.slice(i, i + passo));
  const nomes = pedacos.map((_, k) => 'R53_CODIGO_' + k + '_');
  const modulo = [A.ABRE, A.PRIMEIRA,
    " var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode([" + (opcoes.nomes || nomes).join(',') + "].join('')), 'application/gzip')).getDataAsString('UTF-8');",
    " var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8).map(function(b){return ('0'+((b+256)%256).toString(16)).slice(-2);}).join('');",
    " if(hash!=='" + (opcoes.hash || sha(original)) + "')throw new Error('Pacote R53 incompleto: conteúdo divergente.');",
    remendos, A.INSTANCIA,
    ' try { r53AjustarX_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }',
    " if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');",
    ' return R53_MODULO_;', '}'].join('\n');
  const codigo = '/** @OnlyCurrentDoc */\nvar R53_MODULO_;\n' + modulo +
    "\nfunction r53AjustarX_(abas){abas.push({nome:'ajuste'});}\nfunction outra(){return 1;}\n";
  const arquivos = pedacos.map((p, k) => '// PACOTE R53 · fonte e hashes em r53/empacotar_script.py\nvar R53_CODIGO_' + k + '_ = ' + JSON.stringify(p) + ';\n');
  arquivos.push('// Conteúdo incluído no pacote R53; fonte legível preservada no repositório.\n');
  if (opcoes.vazia !== false) arquivos.push(A.PARTE_VAZIA);
  return { codigo: codigo, arquivos: arquivos };
}

/** Roda o projeto num contexto com Utilities do Apps Script; captura o texto que chega ao new Function. */
function rodar(codigo, arquivos) {
  const recebidos = [];
  const c = { console, Error,
    Utilities: { DigestAlgorithm: { SHA_256: 'sha256' }, Charset: { UTF_8: 'utf8' },
      base64Decode: s => Buffer.from(s, 'base64'), newBlob: b => b,
      ungzip: b => ({ getDataAsString: () => zlib.gunzipSync(b).toString('utf8') }),
      computeDigest: (_, s) => Array.from(crypto.createHash('sha256').update(s, 'utf8').digest())},
    Function: function () { recebidos.push(arguments[arguments.length - 1]); return Function.apply(null, arguments); } };
  vm.createContext(c);
  arquivos.concat([codigo]).forEach(t => vm.runInContext(t, c));
  const m = vm.runInContext('r53Modulo_()', c);
  return { f: m.f(), abas: JSON.stringify(m.__estado().abas), recebidos: recebidos };
}

// 1. Achatado: mesmo texto no new Function, mesmo resultado, sem remendos nem hash na execução.
const base = instalado(ORIGINAL, REMENDOS);
const antes = rodar(base.codigo, base.arquivos);
const r = A.achatar(base.codigo, base.arquivos);
const novos = base.arquivos.map((t, i) => r.arquivos[i] !== undefined ? r.arquivos[i] : t);
const depois = rodar(r.codigo, novos);
assert.strictEqual(antes.recebidos.length, 1);
assert.strictEqual(antes.recebidos[0], ESPERADO, 'o instalado de hoje remenda como esperado');
assert.deepStrictEqual(depois.recebidos, antes.recebidos, 'o new Function recebe o mesmo texto');
assert.strictEqual(r.final, ESPERADO);
assert.strictEqual(depois.f, 'novo'); assert.strictEqual(depois.abas, antes.abas);
assert.strictEqual(depois.abas, JSON.stringify([{ nome: 'B' }, { nome: 'ajuste' }]));
assert.ok(r.codigo.indexOf(A.MARCA) >= 0);
['computeDigest', 'ajustesDescanso', 'mudancas', "if(hash!=="].forEach(t => assert.strictEqual(r.codigo.indexOf(t), -1, t + ' ainda no Codigo'));
assert.ok(r.codigo.indexOf("if(code.length!==" + ESPERADO.length + ")") >= 0);
assert.ok(r.codigo.indexOf("function r53AjustarX_(abas)") >= 0 && r.codigo.indexOf('function outra(){return 1;}') >= 0, 'o resto do Codigo fica');
assert.strictEqual(r.hashFinal, sha(ESPERADO));
console.log('ok: achatado entrega ao new Function o mesmo texto (' + ESPERADO.length + ' caracteres)');

// 2. A forma gerada pelo empacotador (sem remendos) também achata, e o resultado é o original.
const limpo = instalado(ORIGINAL, '');
const rl = A.achatar(limpo.codigo, limpo.arquivos);
assert.strictEqual(rl.final, ORIGINAL);
assert.deepStrictEqual(rodar(rl.codigo, limpo.arquivos.map((t, i) => rl.arquivos[i] !== undefined ? rl.arquivos[i] : t)).recebidos, [ORIGINAL]);
console.log('ok: Codigo do empacotador, sem remendos, achata sem mudar o código');

// 3. Partes: crescer usa o arquivo de parte vazio; sem arquivo vazio, recusa; encolher esvazia a sobra.
const QUATRO = Math.ceil(gz64(ESPERADO).length / 4);
const cresce = A.achatar(base.codigo, base.arquivos, QUATRO);
assert.strictEqual(cresce.nPartes, 4, 'esperado 4 partes, veio ' + cresce.nPartes);
const semVazia = instalado(ORIGINAL, REMENDOS, { vazia: false });
assert.throws(() => A.achatar(semVazia.codigo, semVazia.arquivos, QUATRO), /Faltam arquivos vazios|excede/);
const encolhe = A.achatar(base.codigo, base.arquivos, 100000);
assert.strictEqual(encolhe.nPartes, 1);
assert.strictEqual(encolhe.arquivos[1], A.PARTE_VAZIA); assert.strictEqual(encolhe.arquivos[2], A.PARTE_VAZIA);
assert.deepStrictEqual(rodar(encolhe.codigo, base.arquivos.map((t, i) => encolhe.arquivos[i] !== undefined ? encolhe.arquivos[i] : t)).recebidos, [ESPERADO]);
console.log('ok: partes crescem no arquivo vazio e encolhem sem deixar declaração velha');

// Defeitos plantados: cada um precisa acender.
let acesos = 0;
function acende(nome, fn, padrao) { assert.throws(fn, padrao, nome + ' não acendeu'); acesos++; console.log('ok: defeito plantado acende: ' + nome); }

acende('remendo com âncora que não existe mais', () => {
  const x = instalado(ORIGINAL, REMENDOS.replace("[\"return 'velho';\"", "[\"return 'antigo';\""));
  A.achatar(x.codigo, x.arquivos);
}, /Trecho de descanso divergente/);
acende('parte cortada no instalado', () => {
  const x = instalado(ORIGINAL, REMENDOS); const c = x.arquivos[1].replace(/.{8}";\n$/, '";\n');
  assert.notStrictEqual(c, x.arquivos[1]); x.arquivos[1] = c;
  A.achatar(x.codigo, x.arquivos);
}, /./);
acende('hash do r53Modulo_ diferente do pacote', () => {
  const x = instalado(ORIGINAL, REMENDOS, { hash: sha(ORIGINAL + ' ') }); A.achatar(x.codigo, x.arquivos);
}, /não confere com o hash/);
acende('segunda passada sobre Codigo já achatado', () => A.achatar(r.codigo, novos), /já achatado/);
acende('partes fora de ordem no r53Modulo_', () => {
  const x = instalado(ORIGINAL, REMENDOS, { nomes: ['R53_CODIGO_1_', 'R53_CODIGO_0_', 'R53_CODIGO_2_'] }); A.achatar(x.codigo, x.arquivos);
}, /Partes fora de ordem/);
acende('parte declarada duas vezes', () => {
  A.achatar(base.codigo, base.arquivos.concat([base.arquivos[0]]));
}, /declarado duas vezes/);
acende('conferência de tamanho na execução (parte trocada por outro código)', () => {
  const troca = novos.slice(); const b = gz64(ESPERADO + ' ');
  Object.keys(r.arquivos).forEach(i => { if (r.arquivos[i] !== A.PARTE_VAZIA) troca[i] = A.PARTE_VAZIA; });
  troca[0] = A.CABECA_PARTE + 'var R53_CODIGO_0_ = ' + JSON.stringify(b.slice(0, Math.ceil(b.length / 2))) + ';\n' +
    'var R53_CODIGO_1_ = ' + JSON.stringify(b.slice(Math.ceil(b.length / 2))) + ';\n';
  const cod = r.codigo.replace(/\[R53_CODIGO_0_(,R53_CODIGO_\d+_)*\]/, '[R53_CODIGO_0_,R53_CODIGO_1_]');
  rodar(cod, troca);
}, /tamanho divergente/);
assert.strictEqual(acesos, 7);

// 4. O trecho do console faz a mesma conta com as APIs do navegador (Node 18+ tem as mesmas).
(async () => {
  const modelos = base.arquivos.concat([base.codigo]).map(t => ({ v: t, getValue() { return this.v; }, setValue(x) { this.v = x; } }));
  global.monaco = { editor: { getModels: () => modelos } }; global.window = {};
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  const saida = await new AsyncFunction('return ' + A.trecho().replace(/^await /, ''))();
  assert.ok(!/^ERRO/.test(saida), saida);
  const info = JSON.parse(saida);
  assert.strictEqual(info.final, r.hashFinal.slice(0, 12));
  const doTrecho = rodar(modelos[modelos.length - 1].v, modelos.slice(0, -1).map(m => m.v));
  assert.deepStrictEqual(doTrecho.recebidos, antes.recebidos, 'o trecho entrega o mesmo texto ao new Function');
  assert.strictEqual(await (async () => window.__achatadoReverter())(), 'revertido; salvar com Ctrl+S');
  assert.strictEqual(modelos[modelos.length - 1].v, base.codigo); base.arquivos.forEach((t, i) => assert.strictEqual(modelos[i].v, t));
  const deNovo = await new AsyncFunction('return ' + A.trecho().replace(/^await /, ''))();
  assert.ok(!/^ERRO/.test(deNovo), deNovo);
  assert.ok(/^ERRO: Módulo já achatado/.test(await new AsyncFunction('return ' + A.trecho().replace(/^await /, ''))()), 'o trecho recusa a segunda passada');
  console.log('ok: trecho do console achata igual, reverte e recusa a segunda passada');

  // 5. O editor do Apps Script de verdade: Trusted Types sem 'unsafe-eval' (new Function dá erro, mesmo com TrustedScript).
  // O trecho tem de compilar por <script> com o nonce da página e chegar ao mesmo resultado.
  const editor = (nonceAceito, modelosEd) => {
    const ouvintes = [];
    const ctx = { monaco: { editor: { getModels: () => modelosEd } }, TextEncoder, TextDecoder, crypto: globalThis.crypto,
      CompressionStream, DecompressionStream, Response, Blob, atob, btoa, console,
      addEventListener: (t, f) => ouvintes.push(f), removeEventListener: (t, f) => ouvintes.splice(ouvintes.indexOf(f), 1),
      trustedTypes: { createPolicy: (n, p) => ({ createScript: s => ({ toString: () => p.createScript(s) }) }) },
      document: { querySelector: () => ({ nonce: 'n0nce' }), createElement: () => ({ remove() {} }),
        head: { appendChild(s) {
          const falha = m => ouvintes.slice().forEach(f => f({ message: m }));
          if (s.nonce !== nonceAceito) return falha("Refused to execute inline script because it violates the CSP directive 'script-src'");
          if (typeof s.text !== 'object') return falha('This document requires TrustedScript assignment');
          try { vm.runInContext(String(s.text), ctx); } catch (e) { falha('Uncaught ' + e.name + ': ' + e.message); }
        } } } };
    ctx.window = ctx;
    vm.createContext(ctx);
    vm.runInContext('Function = function () { throw new TypeError("Evaluating a string as JavaScript violates this document\'s Trusted Type assignment requirements."); };', ctx);
    return vm.runInContext('(' + A.trecho().replace(/^await /, '') + ')', ctx).then(saida => ({ saida, ctx }));
  };
  const modelosEd = () => base.arquivos.concat([base.codigo]).map(t => ({ v: t, getValue() { return this.v; }, setValue(x) { this.v = x; } }));
  const ed = modelosEd(), noEditor = await editor('n0nce', ed);
  assert.ok(!/^ERRO/.test(noEditor.saida), noEditor.saida);
  assert.strictEqual(JSON.parse(noEditor.saida).final, r.hashFinal.slice(0, 12), 'no editor, mesmo hash final');
  assert.deepStrictEqual(rodar(ed[ed.length - 1].v, ed.slice(0, -1).map(m => m.v)).recebidos, antes.recebidos, 'no editor, mesmo texto ao new Function');
  console.log('ok: trecho roda no editor com Trusted Types (compila por <script> com nonce) e dá o mesmo resultado');
  // Defeitos plantados no caminho do editor: sem o nonce a página recusa; erro de sintaxe nos remendos aparece com a causa.
  const semNonce = modelosEd(), recusa = await editor('outro', semNonce);
  assert.ok(/^ERRO: O editor não compilou o trecho: Refused/.test(recusa.saida), recusa.saida);
  assert.strictEqual(semNonce[semNonce.length - 1].v, base.codigo, 'recusado, nada muda'); acesos++;
  console.log('ok: defeito plantado acende: página recusa o <script> sem nonce, e nada é gravado');
  const quebrado = modelosEd(), q = quebrado[quebrado.length - 1];
  q.v = q.v.replace('\n' + A.INSTANCIA, '\n code=code.split("a").join(("b");\n' + A.INSTANCIA);
  const sint = await editor('n0nce', quebrado);
  assert.ok(/^ERRO: O editor não compilou o trecho: Uncaught SyntaxError/.test(sint.saida), sint.saida);
  assert.ok(q.v.indexOf(A.MARCA) < 0, 'erro de sintaxe, nada gravado'); acesos++;
  console.log('ok: defeito plantado acende: remendo com erro de sintaxe para o trecho com a causa');
  assert.strictEqual(acesos, 9);
  console.log('modulo_achatado: tudo certo (' + acesos + ' defeitos plantados acesos)');
})().catch(e => { console.error(e); process.exit(1); });
