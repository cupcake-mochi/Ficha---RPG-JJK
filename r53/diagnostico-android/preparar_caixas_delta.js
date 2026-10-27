'use strict';
// Caixas de ± da FICHA sem abrir o módulo (27/10/2026): o trecho para o console do editor do Apps Script que troca só o
// bloco gerado do atalho no fim do Codigo (r53/atalho_livre.gs com R53_LIVRE_DELTA_ e r53LivreDelta_). Módulo,
// EditorR53 e os outros arquivos ficam como estão. Confere antes o Codigo instalado (dc1aa740, o dos cortes da noite) e
// o bloco do atalho de 895d1ec, e depois o Codigo igual ao gerado aqui; recusa sem gravar se algo não bater.
// Uso: node r53/diagnostico-android/preparar_caixas_delta.js <projeto exportado antes dos cortes .json> [saída do trecho]
//      (o projeto de hoje sai dele pelo preparar_cortes_noite.js, como no r53/testes/caixas_delta.js)
const fs = require('fs'), path = require('path'), crypto = require('crypto'), { execSync } = require('child_process');
const raiz = path.join(__dirname, '..', '..');
const { preparar: atalhoNoCodigo } = require('./preparar_atalho');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const BASE = '895d1ec', INICIO = '\n// GERADO por r53/atalho_livre.js;', CODIGO_ANTES = 'dc1aa740';

function gerar(projetoAntesDosCortes) {
  const g = require('./preparar_cortes_noite').gerar(projetoAntesDosCortes);
  const atalhoVelho = execSync('git show ' + BASE + ':r53/atalho_livre.gs', { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');
  const atalhoNovo = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
  if (atalhoNovo.indexOf('function r53LivreDelta_') < 0) throw Error('r53/atalho_livre.gs sem as caixas de ±');
  if (atalhoNovo.indexOf(g.esperado.modulo) < 0) throw Error('r53/atalho_livre.gs não é do módulo ' + g.esperado.modulo.slice(0, 8));
  const codigo = atalhoNoCodigo(g.codigoNovo, atalhoVelho);
  if (sha(codigo).slice(0, 8) !== CODIGO_ANTES) throw Error('o Codigo de hoje saiu ' + sha(codigo).slice(0, 8) + ', esperava ' + CODIGO_ANTES);
  const codigoNovo = atalhoNoCodigo(codigo, atalhoNovo);
  const esperado = { codigo_antes: sha(codigo), codigo: sha(codigoNovo), atalho_antes: sha(atalhoVelho), atalho: sha(atalhoNovo) };
  return { esperado, codigo, codigoNovo, trecho: trecho(atalhoNovo, esperado) };
}

function trecho(atalho, x) {
  return 'await (async () => { try {\n' +
    'const atalho = ' + JSON.stringify(atalho) + ', X = ' + JSON.stringify(x) + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'if (await sha(atalho) !== X.atalho) throw new Error("Trecho corrompido no caminho");\n' +
    'const l = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (l.length !== 1) throw new Error("Codigo encontrado " + l.length + " vez(es)");\n' +
    'const fonte = l[0].getValue();\n' +
    'if (await sha(fonte) !== X.codigo_antes) throw new Error("Codigo instalado diferente do esperado: " + (await sha(fonte)).slice(0, 12));\n' +
    'const i = fonte.indexOf(' + JSON.stringify(INICIO) + ');\n' +
    'if (i < 0 || await sha(fonte.slice(i + 1)) !== X.atalho_antes) throw new Error("Bloco do atalho no fim do Codigo diferente do esperado");\n' +
    'const fonteNova = fonte.slice(0, i + 1) + atalho;\n' +
    'if (await sha(fonteNova) !== X.codigo) throw new Error("O Codigo saiu diferente do gerado no node");\n' +
    'l[0].setValue(fonteNova);\n' +
    'return {codigo: X.codigo.slice(0, 12), atalho: X.atalho.slice(0, 12)};\n' +
    '} catch (err) { return "ERRO, nada gravado: " + err.message; } })()';
}

if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_caixas_delta.js <projeto exportado .json> [saída do trecho]');
  const r = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, r.trecho);
  console.log(JSON.stringify(Object.assign({ bytes_trecho: r.trecho.length, sha_trecho: sha(r.trecho) }, r.esperado), null, 1));
}
module.exports = { gerar, trecho };
