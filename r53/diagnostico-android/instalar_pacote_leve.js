'use strict';
// Pacote leve (25/10/2026): a ficha já está montada, então o módulo que roda em cada edição não precisa das
// tabelas que só a montagem usa (DADOS_R53, MONTAGENS, catálogo e ANALISE: 12 dos 21 MB), nem dos remendos de
// texto aplicados a cada execução (4,5 s medidos no Google). O código completo continua no repositório.
//
// node r53/diagnostico-android/instalar_pacote_leve.js > trecho.js
// imprime o trecho que roda no editor do Apps Script de uma cópia (javascript no console da página): ele lê o
// pacote instalado, confere o hash, embute os remendos, aplica pacote_leve_remendos.json, corta a montagem,
// recompacta e grava os cinco arquivos de dados e o r53Modulo_. Salvar o projeto depois.
const fs = require('fs'), path = require('path');

/** Função pura: o módulo já corrigido vira o módulo leve. Roda igual no node e no navegador. */
function transformarModulo(code, remendos) {
  var aplicados = 0;
  remendos.forEach(function (p, i) {
    var n = code.split(p[0]).length - 1;
    if (n !== 1) throw new Error('Remendo ' + (i + 1) + ': âncora encontrada ' + n + ' vez(es)');
    code = code.replace(p[0], function () { return p[1]; });
    aplicados++;
  });
  var montagem = /^var (VALORES_R53_(DADOS|ANALISE|MONTAGENS|CATALOGO)_\d+_|ABAS_R53_(MONTAGENS|DADOS|CATALOGO)_|ABAS_DA_ANALISE|FONTES_DA_ANALISE_) = /;
  var partes = [], i = 0, cortados = [], re = /\nvar ([A-Z0-9_]+) = /g, m;
  while ((m = re.exec(code))) {
    if (!montagem.test(m[0].slice(1))) continue;
    var fim = code.indexOf('\nif (typeof juntar', m.index);
    if (fim < 0) throw new Error('Tabela sem fim reconhecível: ' + m[1]);
    partes.push(code.slice(i, m.index + 1), 'var ' + m[1] + ' = null;');
    cortados.push(m[1]);
    i = fim;
    re.lastIndex = fim;
  }
  partes.push(code.slice(i));
  code = partes.join('');
  // A montagem precisa do pacote completo: aqui ela recusa antes de tocar em qualquer aba.
  var travas = 0;
  ['construir', 'continuar', 'acabar'].forEach(function (nome) {
    var a = '\nfunction ' + nome + '() {\n', n = code.split(a).length - 1;
    if (n !== 1) throw new Error(nome + ': declaração encontrada ' + n + ' vez(es)');
    code = code.replace(a, a + "  throw new Error('Pacote leve: esta cópia não monta fichas. Use o pacote completo do repositório.');\n");
    travas++;
  });
  return {code: 'var R53_PACOTE_LEVE_ = true;\n' + code, aplicados: aplicados, cortados: cortados, travas: travas};
}

/**
 * Os remendos que o r53Modulo_ instalado aplica a cada execução, lidos como dados e aplicados com a mesma regra.
 * O editor do Apps Script proíbe executar texto (new Function), então as listas saem do próprio Codigo.gs.
 */
function corrigirSemExecutar(fonte, code) {
  var lista = function (nome, laco) {
    var ini = fonte.indexOf('function ' + nome + '(code){var patches=');
    if (ini < 0) throw new Error(nome + ' ausente');
    ini += ('function ' + nome + '(code){var patches=').length;
    var fim = fonte.indexOf(';patches.forEach(function(p){', ini);
    if (fim < 0 || fonte.slice(fim, fim + laco.length) !== laco) throw new Error(nome + ': laço diferente do esperado');
    return JSON.parse(fonte.slice(ini, fim));
  };
  var trocas = function (patches, comoTexto) {
    patches.forEach(function (p) {
      if (code.split(p[0]).length !== 2) throw new Error('Correção: âncora divergente');
      code = comoTexto ? code.replace(p[0], p[1]) : code.replace(p[0], function () { return p[1]; });
    });
  };
  // Abertura e Android trocam com texto (como o String.replace delas); a Fila troca com função
  trocas(lista('r53CorrecaoAbertura_', ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção R53: âncora divergente");code=code.replace(p[0],p[1]);});return code;}'), true);
  trocas(lista('r53CorrecaoAndroid_', ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção Android: âncora divergente");code=code.replace(p[0],p[1]);});return code;}'), true);
  trocas(lista('r53CorrecaoFila_', ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção da fila: âncora divergente");code=code.replace(p[0],function(){return p[1];});});return code;}'), false);
  var c = /function r53CorrecaoCaminho_\(code\)\{var a=("(?:[^"\\]|\\.)*"),b=("(?:[^"\\]|\\.)*");if\(code\.split\(a\)\.length!==2\)throw Error\("Caminho: entrada do editor divergente"\);return code\.replace\(a,b\);\}/.exec(fonte);
  if (!c) throw new Error('r53CorrecaoCaminho_ diferente do esperado');
  trocas([[JSON.parse(c[1]), JSON.parse(c[2])]], true);
  return code;
}

/** O trecho do navegador: tudo dentro de uma função assíncrona, sem rede e sem executar texto. */
function trecho(remendos, esperado) {
  return 'await (async () => { try {\n' +
    'const transformarModulo = ' + transformarModulo.toString() + ';\n' +
    'const remendos = ' + JSON.stringify(remendos) + ';\n' +
    'const ms = monaco.editor.getModels();\n' +
    'const dados = [];\n' +
    'for (const m of ms) { const v = m.getValue(); const x = /^(\\/\\/[^\\n]*\\n)var R53_CODIGO_(\\d+)_ = ("[^\\n]*");\\n?$/.exec(v); if (x) dados[+x[2]] = {m, cab: x[1], s: JSON.parse(x[3])}; }\n' +
    'if (dados.length !== 5 || dados.some(d => !d)) throw new Error("Esperava os cinco arquivos R53_CODIGO_");\n' +
    'const cod = ms.filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53Modulo_ não encontrado uma vez só");\n' +
    'const fonte = cod[0].getValue();\n' +
    'const cadeia = "R53_MODULO_=(new Function(r53CorrecaoCaminho_(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code))))))();";\n' +
    'if (fonte.split(cadeia).length !== 2) throw new Error("A cadeia de correções não é a esperada (pacote já leve?)");\n' +
    'const hashAntigo = /if\\(hash!==\'([0-9a-f]{64})\'\\)throw new Error\\(\'Pacote R53 incompleto/.exec(fonte);\n' +
    'if (!hashAntigo) throw new Error("Hash do pacote não encontrado");\n' +
    'const b64 = dados.map(d => d.s).join("");\n' +
    'const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));\n' +
    'const texto = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'if (await sha(texto) !== hashAntigo[1]) throw new Error("Pacote instalado diferente do hash conferido");\n' +
    'const corrigirSemExecutar = ' + corrigirSemExecutar.toString() + ';\n' +
    'const leve = transformarModulo(corrigirSemExecutar(fonte, texto), remendos);\n' +
    'const esperado = ' + JSON.stringify(esperado || null) + ';\n' +
    'if (esperado && await sha(leve.code) !== esperado) throw new Error("O módulo leve saiu diferente do testado no node");\n' +
    'const gz = new Uint8Array(await new Response(new Blob([new TextEncoder().encode(leve.code)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());\n' +
    'let novo64 = ""; for (let i = 0; i < gz.length; i += 0x8000) novo64 += String.fromCharCode.apply(null, gz.subarray(i, i + 0x8000));\n' +
    'novo64 = btoa(novo64);\n' +
    'const fatias = []; for (let i = 0; i < novo64.length; i += 850000) fatias.push(novo64.slice(i, i + 850000));\n' +
    'if (fatias.length > 5) throw new Error("Pacote leve ainda passa de cinco arquivos");\n' +
    'const hashNovo = await sha(leve.code);\n' +
    'dados.forEach((d, i) => d.m.setValue(d.cab + "var R53_CODIGO_" + i + "_ = " + JSON.stringify(fatias[i] || "") + ";\\n"));\n' +
    'cod[0].setValue(fonte.replace(cadeia, "R53_MODULO_=(new Function(code))();").replace(hashAntigo[0], hashAntigo[0].replace(hashAntigo[1], hashNovo)));\n' +
    'return {antes_MB: +(texto.length / 1048576).toFixed(1), depois_MB: +(leve.code.length / 1048576).toFixed(1), base64_antes: b64.length, base64_depois: novo64.length, arquivos_com_dados: fatias.length, remendos: leve.aplicados, tabelas_cortadas: leve.cortados.length, travas: leve.travas, hash_antigo: hashAntigo[1].slice(0, 12), hash_novo: hashNovo.slice(0, 12)};\n' +
    '} catch (err) { return "ERRO: " + err.message + " | " + String(err.stack).split("\\n").slice(0, 3).join(" / "); } })()';
}

const remendos = () => JSON.parse(fs.readFileSync(path.join(__dirname, 'pacote_leve_remendos.json'), 'utf8'));
if (require.main === module) process.stdout.write(trecho(remendos(), process.argv[2]));
module.exports = { transformarModulo, corrigirSemExecutar, trecho, remendos };
