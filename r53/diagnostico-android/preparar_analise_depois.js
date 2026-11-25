'use strict';
// Conferência da ANALISE no fim da primeira edição (24/11/2026; medição no ANALISE-ESTATICA-2026-11-17.md, "Primeira
// edição de uma cópia"). Vem depois do preparar_analise_estatica.js: o onEdit que tem o gancho analiseNaEdicao_ passa a
// rodar o resto dele num try, e o finally chama o analiseDepoisDaEdicao_, que só faz algo na cópia sem propriedades.
// Precisa do AnaliseEstatica.gs novo no projeto; com o antigo o gancho não faz nada (typeof).
// Só mexe no texto do Codigo de entrada (fora do módulo comprimido): o hash do módulo e o atalho calado não mudam.
//
//   node r53/diagnostico-android/preparar_analise_depois.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_analise_depois.js --reverter > trecho.js   (desfaz)
const vm = require('vm');
const { GANCHO_EDIT } = require('./preparar_analise_estatica.js');

const ABRE = 'try{';
const FECHA = '}finally{if(typeof analiseDepoisDaEdicao_==="function")analiseDepoisDaEdicao_(e);}';

/** O Codigo com o finally; recusa se já tiver. O onEdit mora numa linha só: a função acaba na última chave dela. */
function embrulhar(texto, GANCHO_EDIT, ABRE, FECHA) {
  if (texto.indexOf('analiseDepoisDaEdicao_') >= 0) throw new Error('Conferência no fim da edição já presente');
  if (texto.split(GANCHO_EDIT).length !== 2) throw new Error('Gancho analiseNaEdicao_ ausente ou repetido no Codigo');
  const ini = texto.indexOf(GANCHO_EDIT) + GANCHO_EDIT.length, nl = texto.indexOf('\n', ini);
  const linha = texto.slice(ini, nl < 0 ? texto.length : nl), fim = linha.lastIndexOf('}');
  if (fim < 1 || linha.slice(fim + 1).trim()) throw new Error('O onEdit não acaba na linha do gancho');
  // Uma função só na linha, e as chaves dela fecham ali (a abertura da função ficou antes do gancho).
  if (/\bfunction\s+\w+\s*\(/.test(linha)) throw new Error('Outra função na linha do onEdit');
  if (linha.split('{').length + 1 !== linha.split('}').length) throw new Error('Chaves do onEdit não fecham na linha');
  return texto.slice(0, ini) + ABRE + linha.slice(0, fim) + FECHA + linha.slice(fim) + texto.slice(ini + linha.length);
}

/** Desfaz o embrulhar. */
function desembrulhar(texto, GANCHO_EDIT, ABRE, FECHA) {
  if (texto.split(GANCHO_EDIT + ABRE).length !== 2 || texto.split(FECHA).length !== 2) throw new Error('Conferência no fim da edição ausente ou repetida');
  return texto.replace(GANCHO_EDIT + ABRE, () => GANCHO_EDIT).replace(FECHA, () => '');
}

function preparar(source) { const out = embrulhar(source, GANCHO_EDIT, ABRE, FECHA); new vm.Script(out); return out; }
function reverter(source) { const out = desembrulhar(source, GANCHO_EDIT, ABRE, FECHA); new vm.Script(out); return out; }

/** Trecho para o console do editor do Apps Script (Codigo aberto no Monaco), como os outros preparadores. */
function trecho(desfazer = false) {
  const f = desfazer ? desembrulhar : embrulhar;
  return 'await (async () => { try {\n' +
    'const GANCHO_EDIT = ' + JSON.stringify(GANCHO_EDIT) + ', ABRE = ' + JSON.stringify(ABRE) + ', FECHA = ' + JSON.stringify(FECHA) + ';\n' +
    'const f = ' + f.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf(GANCHO_EDIT) >= 0);\n' +
    'if (cod.length !== 1) throw new Error("gancho do onEdit encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = f(antes, GANCHO_EDIT, ABRE, FECHA);\n' +
    'window.__analiseDepoisAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12) });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { ABRE, FECHA, preparar, reverter, trecho };
