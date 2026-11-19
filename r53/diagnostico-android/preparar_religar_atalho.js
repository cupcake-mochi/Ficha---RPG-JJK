'use strict';
// Religa o atalho das edições livres (16/11/2026, pedido do Mizuki depois da rodada nas oficiais).
//
// O atalho (r53/atalho_livre.gs, r53EdicaoLivre_) deixa a edição numa célula em que o script não faz nada sair em
// ~0,3 s, sem abrir o módulo. Ele só vale para o módulo de onde o mapa saiu: o r53LivreValido_ procura o
// R53_LIVRE_HASHES_[0] dentro do texto do r53Modulo_ e, se não acha, se desliga calado.
//
// Na rodada de 16/11 o hash do módulo mudou duas vezes e o R53_LIVRE_HASHES_[0] ficou no 9dc3480a:
// - o #105 (instalar_frequencia_cena.js) trocou o pacote: 9dc3480a -> bd42b535;
// - o achatador gravou o código já remendado e só deixa o "fonte 35d00ae2" no r53Modulo_.
// Resultado nas duas oficiais: todo Buff, vida, texto ou nota roda o onEdit inteiro, ~3–5 s a mais por edição.
// Medido na cópia da oficial do Ciclo (ACHADOS-2026-11-16.md, pacote privado): handler 3,4 s; com o hash trocado,
// 0,29–0,58 s.
//
// Este preparador troca o R53_LIVRE_HASHES_[0] pelo hash que está no r53Modulo_ (forma achatada ou não), mas só para
// trocas conferidas: o mapa de células livres continua certo para o código novo. A conferência é o --conferir abaixo
// (moldes do módulo nas células livres, antes x depois). Troca não conferida é recusada: aí o caminho é regerar o atalho
// com r53/atalho_livre.js e a ficha exportada.
//
// Conferido em 16/11 para 9dc3480a -> bd42b535 e 9dc3480a -> 35d00ae2 (Ciclo e Era, projetos do ensaio):
// das células com molde diferente entre o 9dc3480a e o código achatado, só 14 caem fora do mapa, todas nas INVOCAÇÕES
// (D34, D37 e as linhas 170, 401, 632, 863, 1094, 1325 nas colunas I e AB), e o r53RepertorioRestaurar_ trata essas
// antes do atalho. O bd42b535 entra porque o código que ele executa (pacote + remendos) é o mesmo do 35d00ae2.
//
// No console do editor do Apps Script (projeto aberto, Codigo carregado):
//   node r53/diagnostico-android/preparar_religar_atalho.js > trecho.js     (cola o trecho; depois "Salvar projeto")
// Desfazer: na mesma aba, window.__religarReverter(); ou restaurar a versão de backup do projeto.
// Conferir uma troca nova, com os .gs dos dois projetos em pastas:
//   node r53/diagnostico-android/preparar_religar_atalho.js --conferir <pasta antes> <pasta depois>

const ABRE_MODULO = 'function r53Modulo_() {';
// Hash do atalho -> hashes de módulo para os quais o mapa foi conferido.
const VERIFICADAS = {
  '9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc': [
    'bd42b5351ec1d299e9e54ecd8281de5d75ee129f01fd3c8e4475b5c6fc9e066e',
    '35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10'],
};

/** Pura: o hash que o r53LivreValido_ vai achar no r53Modulo_ (pacote não achatado ou fonte do achatado). */
function hashDoModulo(codigo) {
  const n = codigo.split(ABRE_MODULO).length - 1;
  if (n !== 1) throw new Error('r53Modulo_ encontrado ' + n + ' vez(es)');
  const ini = codigo.indexOf(ABRE_MODULO), fim = codigo.indexOf('\n}\n', ini);
  if (fim < 0) throw new Error('Fim do r53Modulo_ não encontrado');
  const corpo = codigo.slice(ini, fim);
  const pacote = corpo.match(/if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto/g) || [];
  const fonte = corpo.match(/ \/\/ R53 achatado: [^\n]*; fonte ([0-9a-f]{64})\./g) || [];
  if (pacote.length + fonte.length !== 1) throw new Error('Hash do r53Modulo_ ambíguo ou ausente');
  return /([0-9a-f]{64})/.exec(pacote[0] || fonte[0])[1];
}

/** Pura: troca o R53_LIVRE_HASHES_[0] pelo hash do módulo, se a troca foi conferida. */
function religar(codigo, verificadas) {
  verificadas = verificadas || VERIFICADAS;
  const modulo = hashDoModulo(codigo);
  if (codigo.split('var R53_LIVRE_HASHES_=').length !== 2) throw new Error('Atalho das edições livres ausente ou duplicado');
  const m = /^var R53_LIVRE_HASHES_=\["([0-9a-f]{64})",("[0-9a-f]{64}")\];$/m.exec(codigo);
  if (!m) throw new Error('R53_LIVRE_HASHES_ com forma inesperada');
  if (codigo.indexOf('String(r53Modulo_).indexOf(R53_LIVRE_HASHES_[0])>=0') < 0) throw new Error('r53LivreValido_ divergente');
  if (m[1] === modulo) return { codigo: codigo, antes: m[1], depois: modulo, mudou: false };
  if ((verificadas[m[1]] || []).indexOf(modulo) < 0)
    throw new Error('Troca ' + m[1].slice(0, 8) + ' -> ' + modulo.slice(0, 8) + ' não conferida: regerar o atalho com r53/atalho_livre.js e a ficha exportada');
  const novo = codigo.replace(m[0], () => 'var R53_LIVRE_HASHES_=["' + modulo + '",' + m[2] + '];');
  return { codigo: novo, antes: m[1], depois: modulo, mudou: true };
}

/** O trecho para o console do editor: mesma conta, grava no modelo do Codigo e guarda o texto de antes. */
function trecho() {
  const f = [hashDoModulo, religar].map(x => 'const ' + x.name + ' = ' + x.toString() + ';').join('\n');
  return 'await (async () => { try {\n' +
    'const ABRE_MODULO = ' + JSON.stringify(ABRE_MODULO) + ', VERIFICADAS = ' + JSON.stringify(VERIFICADAS) + ';\n' +
    f + '\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf(ABRE_MODULO) >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53Modulo_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), r = religar(antes, VERIFICADAS);\n' +
    'if (!r.mudou) return JSON.stringify({ atalho: "já ligado", modulo: r.depois.slice(0, 8) });\n' +
    'window.__religarReverter = () => { cod[0].setValue(antes); return "revertido; salvar o projeto"; };\n' +
    'cod[0].setValue(r.codigo);\n' +
    'return JSON.stringify({ atalho: r.antes.slice(0, 8) + " -> " + r.depois.slice(0, 8), salvar: "botão Salvar projeto no Drive" });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

// --conferir: carrega os dois projetos no node e compara os moldes que o módulo grava nas abas do atalho.
const ORDEM = ['Codigo.gs', 'Ficha.gs', 'Invocacoes.gs', 'Analise.gs', 'Configuracao.gs', 'Origens.gs', 'EditorR53.gs',
  'LotePaleta.gs', 'PaletaSegundoPlano.gs', 'SalarioLote.gs'];
const ABAS = ['CARTEIRA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'CONFIGURAÇÃO', 'FICHA', 'FICHA PESSOAL'];

function carregarProjeto(pasta, trocarCodigo) {
  const fs = require('fs'), path = require('path'), vm = require('vm'), zlib = require('zlib'), crypto = require('crypto');
  const Utilities = {
    base64Decode: s => Buffer.from(s, 'base64'), newBlob: b => ({ b: b }),
    ungzip: blob => { const t = zlib.gunzipSync(blob.b).toString('utf8'); return { getDataAsString: () => t }; },
    computeDigest: (a, s) => [...crypto.createHash('sha256').update(s, 'utf8').digest()].map(x => x > 127 ? x - 256 : x),
    DigestAlgorithm: { SHA_256: 1 }, Charset: { UTF_8: 1 }, formatDate: () => '',
  };
  const ctx = { Utilities, console: { log() {} }, PropertiesService: {}, SpreadsheetApp: {} };
  vm.createContext(ctx);
  for (const nome of ORDEM) {
    const p = path.join(pasta, nome); if (!fs.existsSync(p)) continue;
    let src = fs.readFileSync(p, 'utf8'); if (nome === 'Codigo.gs' && trocarCodigo) src = trocarCodigo(src);
    vm.runInContext(src, ctx, { filename: nome });
  }
  const moldes = new Map();
  for (const a of ctx.r53Modulo_().__estado().abas) if (ABAS.indexOf(a.nome) >= 0)
    for (const t of a.vals || []) moldes.set(a.nome + '|' + t[0] + '|' + t[1], t[2]);
  return { ctx, moldes };
}

/** Node: religa o Codigo da pasta "depois" e lista as células livres (fora do mapa) cujo molde mudou. */
function conferirTroca(pastaAntes, pastaDepois) {
  const fs = require('fs'), path = require('path');
  const codigoDepois = fs.readFileSync(path.join(pastaDepois, 'Codigo.gs'), 'utf8');
  const antes = hashDoModulo(fs.readFileSync(path.join(pastaAntes, 'Codigo.gs'), 'utf8'));
  const depois = hashDoModulo(codigoDepois);
  const verif = {}; verif[/^var R53_LIVRE_HASHES_=\["([0-9a-f]{64})"/m.exec(codigoDepois)[1]] = [depois];
  const A = carregarProjeto(pastaAntes), D = carregarProjeto(pastaDepois, src => religar(src, verif).codigo);
  const L = D.ctx.R53_LIVRE_;
  const noMapa = (aba, lin, col) => (L[aba] || []).some(q => lin >= q[0] && lin <= q[2] && col >= q[1] && col <= q[3]);
  const fora = [];
  const chaves = new Set([...A.moldes.keys(), ...D.moldes.keys()]);
  for (const k of chaves) {
    if (A.moldes.get(k) === D.moldes.get(k)) continue;
    const [aba, lin, col] = k.split('|');
    if (!noMapa(aba, +lin, +col)) fora.push(k);
  }
  return { antes, depois, valido: D.ctx.r53LivreValido_(), mudaramForaDoMapa: fora };
}

if (require.main === module) {
  const a = process.argv.slice(2);
  if (a[0] === '--conferir') {
    const r = conferirTroca(a[1], a[2]);
    console.log(JSON.stringify({ antes: r.antes.slice(0, 8), depois: r.depois.slice(0, 8), atalhoLigado: r.valido,
      moldesMudadosForaDoMapa: r.mudaramForaDoMapa.length, celulas: r.mudaramForaDoMapa }, null, 1));
  } else process.stdout.write(trecho() + '\n');
}
module.exports = { VERIFICADAS, hashDoModulo, religar, trecho, conferirTroca };
