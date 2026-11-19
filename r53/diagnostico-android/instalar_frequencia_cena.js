'use strict';
// Frequência do R66 nas QAs (12/11/2026). As cartas de habilidade moram em dois lugares do projeto instalado:
// - no módulo R53, compactado nos cinco arquivos R53_CODIGO_, com o hash conferido no r53Modulo_ do Codigo.gs;
// - no caminho leve, o blob do r53CaminhoLeve_ no Codigo.gs, com o hash dele.
// O trecho abre os dois, confere os hashes, troca as oito frases (cada uma exatamente uma vez em cada lugar),
// recompacta, grava e devolve os hashes novos. Atômico: confere tudo antes do primeiro setValue. Salvar depois.
//
//   node r53/diagnostico-android/instalar_frequencia_cena.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/instalar_frequencia_cena.js --reverter > trecho.js   (desfaz)
//
// Não é o pacote integral: o resto do código instalado fica como está. As frases saem de r53/textos_revisados.py.
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');

function trocas(reverter = false) {
  const python = fs.existsSync('.venv/bin/python') ? '.venv/bin/python' : 'python3';
  const pares = JSON.parse(execFileSync(python, ['-c',
    'import json,sys; sys.path.insert(0,"."); from r53.textos_revisados import FREQUENCIA_POR_CENA as F; ' +
    'print(json.dumps([p for v in F.values() for p in v], ensure_ascii=False))'], { encoding: 'utf8' }));
  if (pares.length !== 8) throw Error('Esperadas oito frases');
  return reverter ? pares.map(([a, d]) => [d, a]) : pares;
}

/** Função pura, igual no node e no navegador: cada frase velha uma vez, e nenhuma sobra depois. */
function aplicar(texto, pares, onde) {
  for (const [velha, nova] of pares) {
    const n = texto.split(velha).length - 1;
    if (n !== 1) throw new Error(onde + ': frase encontrada ' + n + ' vez(es): ' + velha.slice(0, 50));
    texto = texto.replace(velha, () => nova);
  }
  for (const [velha] of pares) if (texto.includes(velha)) throw new Error(onde + ': sobrou ' + velha.slice(0, 50));
  return texto;
}

function trecho(reverter = false) {
  const pares = trocas(reverter);
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(pares) + ';\n' +
    'const aplicar = ' + aplicar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const gunz = async b64 => new Response(new Blob([Uint8Array.from(atob(b64), c => c.charCodeAt(0))]).stream().pipeThrough(new DecompressionStream("gzip"))).text();\n' +
    'const gz64 = async t => { const gz = new Uint8Array(await new Response(new Blob([new TextEncoder().encode(t)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer()); let s = ""; for (let i = 0; i < gz.length; i += 0x8000) s += String.fromCharCode.apply(null, gz.subarray(i, i + 0x8000)); return btoa(s); };\n' +
    'const ms = monaco.editor.getModels();\n' +
    'const dados = []; for (const m of ms) { const x = /^(\\/\\/[^\\n]*\\n)var R53_CODIGO_(\\d+)_ = ("[^\\n]*");\\n?$/.exec(m.getValue()); if (x) dados[+x[2]] = {m, cab: x[1], s: JSON.parse(x[3])}; }\n' +
    'if (dados.length !== 5 || dados.some(d => !d)) throw new Error("Esperava os cinco arquivos R53_CODIGO_");\n' +
    'const cod = ms.filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53Modulo_ não encontrado uma vez só");\n' +
    'let fonte = cod[0].getValue();\n' +
    // módulo R53
    'const hm = /if\\(hash!==\'([0-9a-f]{64})\'\\)throw new Error\\(\'Pacote R53 incompleto/.exec(fonte);\n' +
    'if (!hm) throw new Error("Hash do módulo não encontrado");\n' +
    'const modulo = await gunz(dados.map(d => d.s).join(""));\n' +
    'if (await sha(modulo) !== hm[1]) throw new Error("Módulo instalado diferente do hash");\n' +
    'const moduloNovo = aplicar(modulo, pares, "módulo");\n' +
    'const hmNovo = await sha(moduloNovo), m64 = await gz64(moduloNovo);\n' +
    'if (await gunz(m64) !== moduloNovo) throw new Error("Recompactação do módulo divergente");\n' +
    'const fatias = []; for (let i = 0; i < m64.length; i += 850000) fatias.push(m64.slice(i, i + 850000));\n' +
    'if (fatias.length > 5) throw new Error("Pacote passa de cinco arquivos");\n' +
    // caminho leve
    'const cl = /(function r53CaminhoLeve_\\(\\)\\{[^\\n]*?base64Decode\\(")([A-Za-z0-9+\\/=]+)("\\)[^\\n]*?if\\(hash!==")([0-9a-f]{64})("\\)throw Error\\("Caminho: pacote divergente"\\))/.exec(fonte);\n' +
    'if (!cl) throw new Error("Caminho leve não encontrado");\n' +
    'const leve = await gunz(cl[2]);\n' +
    'if (await sha(leve) !== cl[4]) throw new Error("Caminho leve diferente do hash");\n' +
    'const leveNovo = aplicar(leve, pares, "caminho leve");\n' +
    'const hlNovo = await sha(leveNovo), l64 = await gz64(leveNovo);\n' +
    'if (await gunz(l64) !== leveNovo) throw new Error("Recompactação do caminho leve divergente");\n' +
    // tudo conferido: grava
    'const fonteNova = fonte.replace(cl[0], () => cl[1] + l64 + cl[3] + hlNovo + cl[5]).replace(hm[0], () => hm[0].replace(hm[1], hmNovo));\n' +
    'if (fonteNova.split(hmNovo).length !== 2 || fonteNova.split(hlNovo).length !== 2) throw new Error("Hash novo fora do lugar");\n' +
    'window.__freqCenaAntes = { dados: dados.map(d => d.m.getValue()), codigo: fonte };\n' +
    'dados.forEach((d, i) => d.m.setValue(d.cab + "var R53_CODIGO_" + i + "_ = " + JSON.stringify(fatias[i] || "") + ";\\n"));\n' +
    'cod[0].setValue(fonteNova);\n' +
    'return JSON.stringify({ modulo: hm[1].slice(0, 12) + " -> " + hmNovo.slice(0, 12), caminho: cl[4].slice(0, 12) + " -> " + hlNovo.slice(0, 12), fatias: fatias.length, frases: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { trocas, aplicar, trecho };
