'use strict';
// O XP digitado em cima da caixa de XP da FICHA (27/10/2026). Trocas pequenas no Codigo instalado, como pares
// [antes, depois] com contexto que aparece uma vez só: no salário, o congelamento das missões (salarioXpCongelado_,
// xp_atualizar_salario.json); no bloco gerado do atalho, a caixa de XP (R53_LIVRE_XP_ e r53LivreXp_,
// xp_atualizar_atalho.json, o mesmo que regerar o r53/atalho_livre.gs). Módulo, EditorR53 e os outros arquivos ficam
// como estão. O trecho para o console do editor confere o Codigo de hoje (b8410018) e depois o Codigo igual ao gerado
// aqui; recusa sem gravar se algo não bater. A planilha não muda (só a nota da FICHA!AN10).
// Uso: node r53/diagnostico-android/preparar_xp_atualizar.js <projeto-leve.json> [saída do trecho]
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto'), { execSync } = require('child_process');
const raiz = path.join(__dirname, '..', '..');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const PARES = JSON.parse(fs.readFileSync(path.join(__dirname, 'xp_atualizar_salario.json'), 'utf8'));
const PARES_ATALHO = JSON.parse(fs.readFileSync(path.join(__dirname, 'xp_atualizar_atalho.json'), 'utf8'));
const BASE = '64b84e4', CODIGO_ANTES = 'b8410018';

/** O Salarios.gs (ou o Codigo) com o par do congelamento; recusa se já tiver ou se o bloco divergir. */
function preparar(source) {
  if (PARES.every(([, b]) => source.split(b).length === 2)) throw Error('XP congelado já presente');
  let out = source;
  for (const [a, b] of PARES) {
    if (out.split(a).length !== 2) throw Error('Caminho das missões divergente: ' + a.split('\n')[0].slice(0, 60));
    out = out.replace(a, () => b);
  }
  new vm.Script(out); return out;
}
function aplicar(source, pares) {
  let out = source;
  for (const [a, b] of pares) {
    if (out.split(a).length !== 2) throw Error('trecho antigo encontrado ' + (out.split(a).length - 1) + ' vez(es): ' + a.trim().split('\n')[0].slice(0, 60));
    out = out.replace(a, () => b);
  }
  return out;
}
function gerar(projeto) {
  const codigo = require('./preparar_missoes_sem_registros').gerar(projeto).codigoNovo;
  if (sha(codigo).slice(0, 8) !== CODIGO_ANTES) throw Error('o Codigo de hoje saiu ' + sha(codigo).slice(0, 8) + ', esperava ' + CODIGO_ANTES);
  const atalhoAntes = execSync('git show ' + BASE + ':r53/atalho_livre.gs', { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');
  const atalho = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
  if (aplicar(atalhoAntes, PARES_ATALHO) !== atalho) throw Error('os pares do atalho não dão o r53/atalho_livre.gs');
  const pares = PARES.concat(PARES_ATALHO), codigoNovo = aplicar(codigo, pares);
  new vm.Script(codigoNovo);
  return { pares, codigo, codigoNovo, esperado: { antes: sha(codigo), depois: sha(codigoNovo) } };
}
function trecho(g) {
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(g.pares) + ', X = ' + JSON.stringify(g.esperado) + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("Codigo encontrado " + cod.length + " vez(es)");\n' +
    'const v = cod[0].getValue();\n' +
    'if (await sha(v) !== X.antes) throw new Error("Codigo instalado diferente: " + (await sha(v)).slice(0, 8));\n' +
    'let novo = v;\n' +
    'for (const [a, b] of pares) { if (novo.split(a).length !== 2) throw new Error("trecho antigo fora do lugar"); novo = novo.replace(a, () => b); }\n' +

    'if (await sha(novo) !== X.depois) throw new Error("saiu diferente do node: " + (await sha(novo)).slice(0, 8));\n' +
    'cod[0].setValue(novo);\n' +
    'return {ok: true, antes: X.antes.slice(0, 8), depois: (await sha(cod[0].getValue())).slice(0, 8)};\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}
if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_xp_atualizar.js <projeto-leve.json> [saída do trecho]');
  const g = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, trecho(g));
  console.log(JSON.stringify({ codigo_antes: g.esperado.antes.slice(0, 8), codigo_depois: g.esperado.depois, bytes_trecho: trecho(g).length }));
}
module.exports = { preparar, aplicar, gerar, trecho, PARES, PARES_ATALHO };
