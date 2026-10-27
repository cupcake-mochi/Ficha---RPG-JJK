'use strict';
// A abertura sem a releitura diária do salário (27/10/2026): sem carteira emitida, o salarioCongelar_ marcava a próxima
// conferência para amanhã, e a primeira abertura de cada dia (no Android, a primeira edição rápida) lia a
// DADOS_SALARIOS!P2:Y130 à toa (6–7,5 s). Agora fica para daqui a 3650 dias; emitir apaga a data e ela volta na hora.
// O trecho para o console do editor troca só essa linha do Codigo instalado: confere antes o Codigo de hoje (97c430f4)
// e depois o Codigo igual ao gerado aqui; recusa sem gravar se algo não bater.
// Uso: node r53/diagnostico-android/preparar_abertura_salario.js <projeto-leve.json> [saída do trecho]
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const CODIGO_ANTES = '97c430f4';
const ANTES = '  var q2=salarioDia_(v[0][1]);if(!isFinite(q2))return {novos:0,proximo:hoje+1};';

/** O par sai do próprio Salarios.gs: o bloco novo é o que está lá, e o antigo é a linha de antes. */
function par() {
  const s = fs.readFileSync(path.join(__dirname, '..', '..', 'apps-script', 'Salarios.gs'), 'utf8');
  const fim = '  var q2=salarioDia_(v[0][1]);if(!isFinite(q2))return {novos:0,proximo:hoje+3650};';
  const j = s.indexOf(fim), i = s.lastIndexOf('  // 27/10/2026: sem carteira emitida', j);
  if (j < 0 || i < 0 || s.split(fim).length !== 2) throw Error('Salarios.gs sem o bloco novo da abertura');
  return [ANTES, s.slice(i, j + fim.length)];
}
function aplicar(codigo, p) {
  if (codigo.split(p[0]).length !== 2) throw Error('Trecho antigo encontrado ' + (codigo.split(p[0]).length - 1) + ' vez(es)');
  return codigo.replace(p[0], () => p[1]);
}
function gerar(projeto) {
  const codigo = require('./preparar_xp_nivel').gerar(projeto).codigoNovo;
  if (sha(codigo).slice(0, 8) !== CODIGO_ANTES) throw Error('o Codigo de hoje saiu ' + sha(codigo).slice(0, 8) + ', esperava ' + CODIGO_ANTES);
  const p = par(), codigoNovo = aplicar(codigo, p);
  return { par: p, codigo, codigoNovo, esperado: { antes: sha(codigo), depois: sha(codigoNovo) } };
}
function trecho(g) {
  return 'await (async () => { try {\n' +
    'const par = ' + JSON.stringify(g.par) + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("Codigo encontrado " + cod.length + " vez(es)");\n' +
    'const v = cod[0].getValue();\n' +
    'if (await sha(v) !== ' + JSON.stringify(g.esperado.antes) + ') throw new Error("Codigo instalado diferente: " + (await sha(v)).slice(0, 8));\n' +
    'if (v.split(par[0]).length !== 2) throw new Error("trecho antigo fora do lugar");\n' +
    'const novo = v.replace(par[0], () => par[1]);\n' +
    'if (await sha(novo) !== ' + JSON.stringify(g.esperado.depois) + ') throw new Error("saiu diferente do node: " + (await sha(novo)).slice(0, 8));\n' +
    'cod[0].setValue(novo);\n' +
    'return {ok: true, antes: ' + JSON.stringify(g.esperado.antes.slice(0, 8)) + ', depois: (await sha(cod[0].getValue())).slice(0, 8)};\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}
if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_abertura_salario.js <projeto-leve.json> [saída do trecho]');
  const g = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, trecho(g));
  console.log(JSON.stringify({ codigo_antes: g.esperado.antes.slice(0, 8), codigo_depois: g.esperado.depois, bytes_trecho: trecho(g).length }));
}
module.exports = { par, aplicar, gerar, trecho, ANTES };
