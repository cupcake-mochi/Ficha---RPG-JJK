'use strict';
// Módulo achatado (15/11/2026, pedido do Mizuki depois do pente fino de desempenho).
//
// Cada preparador desta pasta injeta no r53Modulo_ instalado um remendo de texto que roda em TODA execução:
// descompacta o pacote (8,7 milhões de caracteres), confere o SHA-256 e aplica dezenas de split/replace antes do
// new Function. Medido na cópia descartável em 6 edições: remendos 0,4–1,0 s e hash 0,08–0,23 s, de um módulo de
// 1,7–4,1 s (r53/diagnostico-android/PENTE-FINO-DESEMPENHO-2026-11-15.md, no repositório Claude 3).
//
// Este preparador é o último da cadeia, rodado antes de instalar. Ele aplica os remendos uma vez só e grava o código
// já remendado nas partes R53_CODIGO_*. O r53Modulo_ resultante só descompacta, confere o tamanho e roda os
// r53Ajustar* (que ficam iguais). O código que o new Function recebe é o mesmo, caractere por caractere: o trecho
// confere isso descompactando as partes novas antes de gravar.
//
// Preparadores futuros que remendam o módulo continuam valendo: rodam sobre um Codigo NÃO achatado (o backup da
// versão anterior) e o achatador roda de novo no fim. Sobre um Codigo já achatado, o achatador recusa.
//
// No console do editor do Apps Script (projeto com o Codigo instalado aberto):
//   node r53/diagnostico-android/preparar_modulo_achatado.js > trecho.js     (achata; depois Ctrl+S)
// Desfazer: na mesma aba, window.__achatadoReverter(); ou restaurar a versão de backup do projeto.
//
// Atalho das edições livres (16/11/2026): o r53LivreValido_ procura o R53_LIVRE_HASHES_[0] no texto do r53Modulo_.
// Achatar tira dali o hash do pacote, então o achatador troca o R53_LIVRE_HASHES_[0] pelo hash da fonte achatada.
// O código executado é o mesmo, então o mapa continua valendo. Se o atalho já estava desligado antes (o
// R53_LIVRE_HASHES_[0] não é o hash do pacote instalado), o achatador recusa: religar antes com
// preparar_religar_atalho.js. Foi isso que passou calado na rodada de 16/11 (o #105 trocou o pacote).
const zlib = require('zlib'), crypto = require('crypto'), vm = require('vm');

const ABRE = 'function r53Modulo_() {';
const PRIMEIRA = ' if (R53_MODULO_) return R53_MODULO_;';
const INSTANCIA = ' R53_MODULO_=(new Function(code))();';
const MARCA = ' // R53 achatado: remendos aplicados no pacote por preparar_modulo_achatado.js';
const PASSO = 850000;
const MAX_PARTES = 5;
const CABECA_PARTE = '// PACOTE R53 achatado · r53/diagnostico-android/preparar_modulo_achatado.js\n';
const PARTE_VAZIA = '// Parte de dados anterior incorporada ao pacote R53.\n';

/** Pura: separa o r53Modulo_ instalado em partes conhecidas; recusa qualquer forma inesperada. */
function separar(src) {
  if (src.indexOf(MARCA) >= 0) throw new Error('Módulo já achatado');
  const n = src.split(ABRE).length - 1;
  if (n !== 1) throw new Error('r53Modulo_ encontrado ' + n + ' vez(es)');
  const ini = src.indexOf(ABRE), fim = src.indexOf('\n}\n', ini);
  if (fim < 0) throw new Error('Fim do r53Modulo_ não encontrado');
  const corpo = src.slice(ini, fim + 2), linhas = corpo.split('\n');
  const mCode = /^ var code=Utilities\.ungzip\(Utilities\.newBlob\(Utilities\.base64Decode\(\[((?:R53_CODIGO_\d+_,)*R53_CODIGO_\d+_)\]\.join\(''\)\), 'application\/gzip'\)\)\.getDataAsString\('UTF-8'\);$/.exec(linhas[2] || '');
  const mHash = /^ if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto: conteúdo divergente\.'\);$/.exec(linhas[4] || '');
  if (linhas[0] !== ABRE || linhas[1] !== PRIMEIRA || !mCode || !mHash ||
      (linhas[3] || '').indexOf(' var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8)') !== 0)
    throw new Error('Cabeça do r53Modulo_ divergente');
  const iInst = linhas.indexOf(INSTANCIA);
  if (iInst < 5 || linhas.lastIndexOf(INSTANCIA) !== iInst) throw new Error('Instanciação do módulo divergente');
  const partes = mCode[1].split(',');
  partes.forEach((p, i) => { if (p !== 'R53_CODIGO_' + i + '_') throw new Error('Partes fora de ordem: ' + mCode[1]); });
  return { ini: ini, fim: fim + 2, partes: partes, hash: mHash[1],
           remendos: linhas.slice(5, iInst).join('\n'), cauda: linhas.slice(iInst).join('\n') };
}

/** Pura: leva o atalho das edições livres para o hash da fonte achatada; recusa atalho já desligado. */
function ajustarAtalho(codigo, hashPacote, hashFinal) {
  const n = codigo.split('var R53_LIVRE_HASHES_=').length - 1;
  if (n === 0) return { codigo: codigo, atalho: 'sem atalho' };
  const m = /^var R53_LIVRE_HASHES_=\["([0-9a-f]{64})",("[0-9a-f]{64}")\];$/m.exec(codigo);
  if (n !== 1 || !m) throw new Error('Atalho das edições livres com forma inesperada');
  if (m[1] !== hashPacote) throw new Error('Atalho das edições livres já desligado (' + m[1].slice(0, 8) + ' em vez de ' +
    hashPacote.slice(0, 8) + '): religar antes com preparar_religar_atalho.js');
  return { codigo: codigo.replace(m[0], () => 'var R53_LIVRE_HASHES_=["' + hashFinal + '",' + m[2] + '];'),
    atalho: hashPacote.slice(0, 8) + ' -> ' + hashFinal.slice(0, 8) };
}

/** Pura: roda o bloco de remendos instalado sobre o código, como o r53Modulo_ faria a cada execução. */
function aplicarRemendos(code, remendos) {
  return new Function('code', remendos + '\nreturn code;')(code);
}

/** Pura: o r53Modulo_ achatado (sem remendos e sem hash; confere o tamanho descompactado). */
function novoModulo(sep, nPartes, tamanho, hashFinal) {
  const nomes = []; for (let i = 0; i < nPartes; i++) nomes.push('R53_CODIGO_' + i + '_');
  return [ABRE, PRIMEIRA, MARCA + '; fonte ' + hashFinal + '.',
    " var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode([" + nomes.join(',') + "].join('')), 'application/gzip')).getDataAsString('UTF-8');",
    " if(code.length!==" + tamanho + ")throw new Error('Pacote R53 incompleto: tamanho divergente.');",
    sep.cauda].join('\n');
}

/** Pura: lê as partes R53_CODIGO_k_ de um conjunto de textos de arquivo; devolve {k: {arquivo, valor}}. */
function lerPartes(arquivos) {
  const achadas = {};
  arquivos.forEach((txt, a) => {
    const re = /^var R53_CODIGO_(\d+)_ = ("(?:[^"\\]|\\.)*");$/gm; let m;
    while ((m = re.exec(txt))) {
      if (achadas[m[1]]) throw new Error('R53_CODIGO_' + m[1] + '_ declarado duas vezes');
      achadas[m[1]] = { arquivo: a, valor: JSON.parse(m[2]) };
    }
  });
  return achadas;
}

/** Pura: distribui o base64 novo nos arquivos de parte (os antigos primeiro, depois os vazios). */
function distribuir(b64, sep, achadas, arquivos, passo) {
  passo = passo || PASSO;
  const pedacos = []; for (let i = 0; i < b64.length; i += passo) pedacos.push(b64.slice(i, i + passo));
  if (pedacos.length > MAX_PARTES) throw new Error('Pacote achatado excede ' + MAX_PARTES + ' partes');
  const donos = sep.partes.map((_, k) => { if (!achadas[k]) throw new Error('R53_CODIGO_' + k + '_ ausente'); return achadas[k].arquivo; });
  const livres = arquivos.map((t, a) => a).filter(a => donos.indexOf(a) < 0 && arquivos[a] === PARTE_VAZIA);
  const destino = pedacos.map((_, k) => k < donos.length ? donos[k] : livres.shift());
  if (destino.some(a => a === undefined)) throw new Error('Faltam arquivos vazios para as partes novas');
  const saida = {};
  destino.forEach((a, k) => { saida[a] = (saida[a] || CABECA_PARTE) + 'var R53_CODIGO_' + k + '_ = ' + JSON.stringify(pedacos[k]) + ';\n'; });
  donos.forEach(a => { if (!(a in saida)) saida[a] = PARTE_VAZIA; });
  return { saida: saida, nPartes: pedacos.length };
}

/** Node (testes e conferência local): mesma conta do trecho, síncrona. Devolve os textos novos, sem gravar nada. */
function achatar(codigo, arquivos, passo) {
  const sep = separar(codigo), achadas = lerPartes(arquivos);
  ajustarAtalho(codigo, sep.hash, sep.hash);
  const b64 = sep.partes.map((_, k) => { if (!achadas[k]) throw new Error('R53_CODIGO_' + k + '_ ausente'); return achadas[k].valor; }).join('');
  const original = zlib.gunzipSync(Buffer.from(b64, 'base64')).toString('utf8');
  if (crypto.createHash('sha256').update(original, 'utf8').digest('hex') !== sep.hash) throw new Error('Pacote instalado não confere com o hash do r53Modulo_');
  const final = aplicarRemendos(original, sep.remendos);
  const hashFinal = crypto.createHash('sha256').update(final, 'utf8').digest('hex');
  const novoB64 = zlib.gzipSync(Buffer.from(final, 'utf8'), { level: 9 }).toString('base64');
  if (zlib.gunzipSync(Buffer.from(novoB64, 'base64')).toString('utf8') !== final) throw new Error('Compressão divergente');
  const d = distribuir(novoB64, sep, achadas, arquivos, passo);
  const at = ajustarAtalho(codigo.slice(0, sep.ini) + novoModulo(sep, d.nPartes, final.length, hashFinal) + codigo.slice(sep.fim), sep.hash, hashFinal);
  const novoCodigo = at.codigo;
  new vm.Script(novoCodigo);
  return { codigo: novoCodigo, arquivos: d.saida, final: final, hashFinal: hashFinal, nPartes: d.nPartes, remendos: sep.remendos.length, atalho: at.atalho };
}

/** O trecho para o console do editor: mesma conta, com as APIs de compressão do navegador. */
// O editor do Apps Script exige Trusted Types e não tem 'unsafe-eval': new Function e eval dão erro lá, mesmo com
// TrustedScript (conferido em 15/11/2026). O trecho compila por um <script> com o nonce da própria página; onde
// new Function funciona (node, página sem essa CSP), usa ele mesmo.
function compilar(params, corpo) {
  try { return new Function(params, corpo); } catch (e) {
    if (!/Trusted Type|unsafe-eval|Content Security/i.test(String(e && e.message))) throw e;
  }
  let erro = null;
  const ouvir = ev => { erro = ev.message || String(ev.error); };
  const pol = trustedTypes.createPolicy('achatador-' + Date.now(), { createScript: s => s });
  const s = document.createElement('script'), comNonce = document.querySelector('script[nonce]');
  if (comNonce) s.nonce = comNonce.nonce;
  window.__achatadoFn = undefined;
  window.addEventListener('error', ouvir);
  s.text = pol.createScript('window.__achatadoFn = function (' + params + ') {\n' + corpo + '\n};');
  document.head.appendChild(s); s.remove();
  window.removeEventListener('error', ouvir);
  const f = window.__achatadoFn; window.__achatadoFn = undefined;
  if (typeof f !== 'function') throw new Error('O editor não compilou o trecho' + (erro ? ': ' + erro : ' (CSP)'));
  return f;
}

function trecho() {
  const f = [separar, novoModulo, lerPartes, distribuir, compilar, ajustarAtalho].map(x => 'const ' + x.name + ' = ' + x.toString() + ';').join('\n');
  return 'await (async () => { try {\n' +
    'const ABRE = ' + JSON.stringify(ABRE) + ', PRIMEIRA = ' + JSON.stringify(PRIMEIRA) + ', INSTANCIA = ' + JSON.stringify(INSTANCIA) + ', MARCA = ' + JSON.stringify(MARCA) + ';\n' +
    'const PASSO = ' + PASSO + ', MAX_PARTES = ' + MAX_PARTES + ', CABECA_PARTE = ' + JSON.stringify(CABECA_PARTE) + ', PARTE_VAZIA = ' + JSON.stringify(PARTE_VAZIA) + ';\n' +
    f + '\n' +
    'const aplicarRemendos = (code, remendos) => compilar("code", remendos + "\\nreturn code;")(code);\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const deB64 = s => { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; };\n' +
    'const paraB64 = u => { let s = ""; for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s); };\n' +
    'const passar = async (u, fluxo) => new Uint8Array(await new Response(new Blob([u]).stream().pipeThrough(fluxo)).arrayBuffer());\n' +
    'const modelos = monaco.editor.getModels(), textos = modelos.map(m => m.getValue());\n' +
    'const cod = modelos.filter((m, i) => textos[i].indexOf(ABRE) >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53Modulo_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const codigo = cod[0].getValue(), sep = separar(codigo), achadas = lerPartes(textos);\n' +
    'ajustarAtalho(codigo, sep.hash, sep.hash);\n' +
    'const b64 = sep.partes.map((_, k) => { if (!achadas[k]) throw new Error("R53_CODIGO_" + k + "_ ausente"); return achadas[k].valor; }).join("");\n' +
    'const original = new TextDecoder().decode(await passar(deB64(b64), new DecompressionStream("gzip")));\n' +
    'if (await sha(original) !== sep.hash) throw new Error("Pacote instalado não confere com o hash do r53Modulo_");\n' +
    'const final = aplicarRemendos(original, sep.remendos), hashFinal = await sha(final);\n' +
    'const novoB64 = paraB64(await passar(new TextEncoder().encode(final), new CompressionStream("gzip")));\n' +
    'if (new TextDecoder().decode(await passar(deB64(novoB64), new DecompressionStream("gzip"))) !== final) throw new Error("Compressão divergente");\n' +
    'const d = distribuir(novoB64, sep, achadas, textos);\n' +
    'const at = ajustarAtalho(codigo.slice(0, sep.ini) + novoModulo(sep, d.nPartes, final.length, hashFinal) + codigo.slice(sep.fim), sep.hash, hashFinal);\n' +
    'const novoCodigo = at.codigo;\n' +
    'compilar("", novoCodigo);\n' +
    'const antes = {}; antes[modelos.indexOf(cod[0])] = codigo; Object.keys(d.saida).forEach(a => { antes[a] = textos[a]; });\n' +
    'window.__achatadoAntes = antes;\n' +
    'window.__achatadoReverter = () => { Object.keys(antes).forEach(a => modelos[a].setValue(antes[a])); return "revertido; salvar com Ctrl+S"; };\n' +
    'Object.keys(d.saida).forEach(a => modelos[a].setValue(d.saida[a]));\n' +
    'cod[0].setValue(novoCodigo);\n' +
    'return JSON.stringify({ antes: sep.hash.slice(0, 12), final: hashFinal.slice(0, 12), caracteres: final.length, remendos: sep.remendos.length, partes: sep.partes.length + " -> " + d.nPartes, base64: b64.length + " -> " + novoB64.length, codigo: codigo.length + " -> " + novoCodigo.length, atalho: at.atalho, salvar: "Ctrl+S" });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho() + '\n');
module.exports = { ABRE, PRIMEIRA, INSTANCIA, MARCA, PASSO, CABECA_PARTE, PARTE_VAZIA, separar, aplicarRemendos, ajustarAtalho, novoModulo, lerPartes, distribuir, achatar, trecho };
