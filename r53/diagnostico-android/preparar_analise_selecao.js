'use strict';
// Conferência da cópia nova no próximo clique (25/11/2026). Vem depois do preparar_analise_depois.js: o
// onSelectionChange de entrada do Codigo ganha, como última linha, a chamada ao analiseNaSelecao_ quando não há paleta
// pendente. Precisa do AnaliseEstatica.gs novo; com o antigo a linha não faz nada (typeof).
// As oficiais não têm o onSelectionChange igual ao do empacotar_script.py (16/11: "if(pending)r53PaletaLeve_()..."),
// então a linha entra antes da chave que fecha a função, sem depender do resto dela. Só mexe no Codigo de entrada:
// o módulo comprimido não muda.
//
//   node r53/diagnostico-android/preparar_analise_selecao.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_analise_selecao.js --reverter > trecho.js   (desfaz)
const vm = require('vm');

const ABRE_SEL = 'function onSelectionChange(e) {';
const LINHA_SEL = ' if(!pending&&typeof analiseNaSelecao_==="function")analiseNaSelecao_(e);';

/** O Codigo com a linha nova; recusa se já tiver, se a função não estiver lá uma vez só ou não tiver o `pending`. */
function encaixar(texto, ABRE_SEL, LINHA_SEL) {
  if (texto.indexOf('analiseNaSelecao_') >= 0) throw new Error('Conferência no clique já presente');
  if (texto.split(ABRE_SEL).length !== 2) throw new Error('onSelectionChange de entrada ausente ou repetido no Codigo');
  const nl = texto.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
  const ini = texto.indexOf(ABRE_SEL), fim = texto.indexOf(nl + '}', ini);
  if (fim < 0) throw new Error('O onSelectionChange não fecha numa linha só com }');
  const corpo = texto.slice(ini, fim);
  if (!/\bvar pending\s*=/.test(corpo)) throw new Error('O onSelectionChange não tem a variável pending');
  if (corpo.slice(ABRE_SEL.length).indexOf('function ') >= 0) throw new Error('Outra função dentro do onSelectionChange');
  return texto.slice(0, fim) + nl + LINHA_SEL + texto.slice(fim);
}

/** Desfaz o encaixar. */
function desencaixar(texto, ABRE_SEL, LINHA_SEL) {
  const nl = texto.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
  if (texto.split(nl + LINHA_SEL).length !== 2) throw new Error('Conferência no clique ausente ou repetida');
  return texto.replace(nl + LINHA_SEL, () => '');
}

function preparar(source) { const out = encaixar(source, ABRE_SEL, LINHA_SEL); new vm.Script(out); return out; }
function reverter(source) { const out = desencaixar(source, ABRE_SEL, LINHA_SEL); new vm.Script(out); return out; }

/** Trecho para o console do editor do Apps Script (Codigo aberto no Monaco), como os outros preparadores. */
function trecho(desfazer = false) {
  const f = desfazer ? desencaixar : encaixar;
  return 'await (async () => { try {\n' +
    'const ABRE_SEL = ' + JSON.stringify(ABRE_SEL) + ', LINHA_SEL = ' + JSON.stringify(LINHA_SEL) + ';\n' +
    'const f = ' + f.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf(ABRE_SEL) >= 0 && m.getValue().indexOf("analiseNaEdicao_") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("onSelectionChange de entrada encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = f(antes, ABRE_SEL, LINHA_SEL);\n' +
    'window.__analiseSelecaoAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes.replace(/\\r/g, ""))).slice(0, 12), depois: (await sha(cod[0].getValue().replace(/\\r/g, ""))).slice(0, 12) });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { ABRE_SEL, LINHA_SEL, preparar, reverter, trecho };
