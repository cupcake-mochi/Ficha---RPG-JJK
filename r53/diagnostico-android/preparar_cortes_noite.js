'use strict';
// Cortes da noite de 26/10/2026: o trecho para o console do editor do Apps Script que leva, de uma vez, o módulo com os
// remendos 39–41 (marcas K7/K8 guardadas e XP devolvida sem ler a DADOS), o atalho regerado para ele e o EditorR53 com
// a versão guardada (MONTAGENS). Confere tudo antes de gravar: o módulo instalado (52fc6903), o bloco do atalho no fim
// do Codigo (o r53/atalho_livre.gs de ee201f0), o EditorR53 (68f21a08) e, no fim, o Codigo, o EditorR53 e o módulo
// iguais aos gerados aqui. Só grava se tudo bater; salvar o projeto depois.
// Uso: node r53/diagnostico-android/preparar_cortes_noite.js <projeto exportado .json> [saída do trecho]
const fs = require('fs'), path = require('path'), crypto = require('crypto'), zlib = require('zlib'), { execSync } = require('child_process');
const raiz = path.join(__dirname, '..', '..');
const { aplicarIncremento } = require('./instalar_pacote_leve');
const { pares, aplicar } = require('./preparar_cartao_leve');
const { preparar: atalhoNoCodigo } = require('./preparar_atalho');
const { preparar: transporte } = require('../editor_lazy');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const BASE = 'ee201f0', DESDE = 38, ATE = 41, INICIO = '\n// GERADO por r53/atalho_livre.js;';
const git = f => execSync('git show ' + BASE + ':' + f, { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');

function gerar(projeto) {
  const arq = n => projeto.files.find(f => f.name === n).source;
  const codigo = arq('Codigo'), editor = arq('EditorR53');
  const remendos = JSON.parse(fs.readFileSync(path.join(__dirname, 'pacote_leve_remendos.json'), 'utf8')).slice(0, ATE);
  // módulo instalado, pelas cinco fatias
  const fatias = projeto.files.map(f => /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(f.source)).filter(Boolean);
  const instalado = zlib.gunzipSync(Buffer.from(fatias.sort((a, b) => a[2] - b[2]).map(x => JSON.parse(x[3])).join(''), 'base64')).toString('utf8');
  const hashAntes = /if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto/.exec(codigo)[1];
  if (sha(instalado) !== hashAntes) throw Error('módulo instalado diferente do hash do Codigo');
  const modulo = aplicarIncremento(instalado, remendos, DESDE), hashModulo = sha(modulo);
  // Codigo: hash do r53Modulo_ e o atalho regerado
  const atalhoVelho = git('r53/atalho_livre.gs'), atalhoNovo = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
  if (!codigo.endsWith('\n' + atalhoVelho)) throw Error('o Codigo instalado não termina no atalho de ' + BASE);
  if (atalhoNovo.indexOf(hashModulo) < 0) throw Error('r53/atalho_livre.gs não foi regerado para o módulo ' + hashModulo.slice(0, 8));
  const comHash = codigo.replace("if(hash!=='" + hashAntes + "')", "if(hash!=='" + hashModulo + "')");
  const codigoNovo = atalhoNoCodigo(comHash, atalhoNovo);
  // EditorR53: os trechos que mudaram desde a base, aplicados no de transporte instalado
  const fonteVelha = git('apps-script/EditorR53.gs'), fonteNova = fs.readFileSync(path.join(raiz, 'apps-script/EditorR53.gs'), 'utf8');
  if (transporte(fonteVelha).code !== editor) throw Error('o EditorR53 instalado não é o de ' + BASE);
  const ps = pares(fonteVelha, fonteNova), editorNovo = transporte(fonteNova).code;
  if (aplicar(editor, ps) !== editorNovo) throw Error('os trechos não reproduzem o EditorR53 novo');
  const esperado = { modulo_antes: hashAntes, modulo: hashModulo, codigo_antes: sha(codigo), codigo: sha(codigoNovo),
    atalho_antes: sha(atalhoVelho), editor_antes: sha(editor), editor: sha(editorNovo) };
  return { esperado, trecho: trecho(remendos, ps, atalhoNovo, esperado), codigoNovo, editorNovo, modulo };
}

function trecho(remendos, ps, atalhoNovo, x) {
  return 'await (async () => { try {\n' +
    'const aplicarIncremento = ' + aplicarIncremento.toString() + ';\n' +
    'const remendos = ' + JSON.stringify(remendos) + ', pares = ' + JSON.stringify(ps) + ', atalho = ' + JSON.stringify(atalhoNovo) + ';\n' +
    'const X = ' + JSON.stringify(x) + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const ms = monaco.editor.getModels(), dados = [];\n' +
    'for (const m of ms) { const v = m.getValue(); const r = /^(\\/\\/[^\\n]*\\n)var R53_CODIGO_(\\d+)_ = ("[^\\n]*");\\n?$/.exec(v); if (r) dados[+r[2]] = {m, cab: r[1], s: JSON.parse(r[3])}; }\n' +
    'if (dados.length !== 5 || dados.some(d => !d)) throw new Error("Esperava os cinco pedaços R53_CODIGO_");\n' +
    'const um = (marca, nome) => { const l = ms.filter(m => m.getValue().indexOf(marca) >= 0); if (l.length !== 1) throw new Error(nome + " encontrado " + l.length + " vez(es)"); return l[0]; };\n' +
    'const cod = um("function r53Modulo_()", "Codigo"), ed = um("function r53ConfigEditor_(", "EditorR53");\n' +
    'const fonte = cod.getValue(), editor = ed.getValue();\n' +
    'if (await sha(fonte) !== X.codigo_antes) throw new Error("Codigo instalado diferente do esperado: " + (await sha(fonte)).slice(0, 12));\n' +
    'if (await sha(editor) !== X.editor_antes) throw new Error("EditorR53 instalado diferente do esperado: " + (await sha(editor)).slice(0, 12));\n' +
    'const bin = Uint8Array.from(atob(dados.map(d => d.s).join("")), c => c.charCodeAt(0));\n' +
    'const texto = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();\n' +
    'if (await sha(texto) !== X.modulo_antes) throw new Error("Módulo instalado diferente do esperado");\n' +
    'const code = aplicarIncremento(texto, remendos, ' + DESDE + ');\n' +
    'if (await sha(code) !== X.modulo) throw new Error("O módulo saiu diferente do testado no node");\n' +
    'const i = fonte.indexOf(' + JSON.stringify(INICIO) + ');\n' +
    'if (i < 0 || await sha(fonte.slice(i + 1)) !== X.atalho_antes) throw new Error("Bloco do atalho no fim do Codigo diferente do esperado");\n' +
    'const fonteNova = fonte.slice(0, i + 1).replace("if(hash!==\'" + X.modulo_antes + "\')", "if(hash!==\'" + X.modulo + "\')") + atalho;\n' +
    'if (await sha(fonteNova) !== X.codigo) throw new Error("O Codigo saiu diferente do gerado no node");\n' +
    'let editorNovo = editor; for (const p of pares) { const n = editorNovo.split(p[0]).length - 1; if (n !== 1) throw new Error("Trecho do EditorR53 encontrado " + n + " vez(es)"); editorNovo = editorNovo.replace(p[0], () => p[1]); }\n' +
    'if (await sha(editorNovo) !== X.editor) throw new Error("O EditorR53 saiu diferente do gerado no node");\n' +
    'const gz = new Uint8Array(await new Response(new Blob([new TextEncoder().encode(code)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());\n' +
    'let b64 = ""; for (let k = 0; k < gz.length; k += 0x8000) b64 += String.fromCharCode.apply(null, gz.subarray(k, k + 0x8000));\n' +
    'b64 = btoa(b64);\n' +
    'const fatias = []; for (let k = 0; k < b64.length; k += 850000) fatias.push(b64.slice(k, k + 850000));\n' +
    'if (fatias.length > 5) throw new Error("Pacote passa de cinco pedaços");\n' +
    'dados.forEach((d, k) => d.m.setValue(d.cab + "var R53_CODIGO_" + k + "_ = " + JSON.stringify(fatias[k] || "") + ";\\n"));\n' +
    'cod.setValue(fonteNova); ed.setValue(editorNovo);\n' +
    'return {modulo: X.modulo.slice(0, 12), codigo: X.codigo.slice(0, 12), editor: X.editor.slice(0, 12), pedacos: fatias.length};\n' +
    '} catch (err) { return "ERRO, nada gravado: " + err.message; } })()';
}

if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_cortes_noite.js <projeto exportado .json> [saída do trecho]');
  const r = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, r.trecho);
  console.log(JSON.stringify(Object.assign({ bytes_trecho: r.trecho.length }, r.esperado), null, 1));
}
module.exports = { gerar };
