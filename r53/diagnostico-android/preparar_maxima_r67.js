'use strict';
// Rodada R67 nas oficiais (18/11/2026, plano aprovado pelo Mizuki: "Pode seguir"). Ver PLANO-RODADA-R67-2026-11-18.md.
//
// Leva a Técnica Máxima R67 (#117) e os consertos do construir() da PR #135 para um projeto instalado igual às
// oficiais de 18/11 (Codigo 94f1a184, EditorR53 35065b22, AnaliseEstatica 450709a1, módulo achatado 35d00ae2).
// Tudo offline, no node; na oficial vão os arquivos prontos, conferidos pelo hash (forma B da rodada de 16/11).
//
// Projeto (prepararProjeto):
//   - Codigo: r53AjustarMaximaR67_ (as 67 células e as 54 notas dos cartões no molde, depois do molde API); o
//     restaurador da Prática com a FX nova (251 linhas) e as 14 células das linhas 252–253; a T357 da FA no mapa do
//     atalho; o tamanho e a fonte do módulo novo; os dois hashes do atalho (módulo e catálogo do editor).
//   - EditorR53: os contextos da Máxima (44 e 204–248) no catálogo compactado do r53ConfigEditor_, e o hash dele.
//   - Módulo (partes R53_CODIGO_k_ em Ficha/Invocacoes/Analise): criarGrupos_ e a guarda do estilo no montarAba_.
//   - AnaliseEstatica: o breakApart da caixa AT4 (arquivo inteiro, o do repositório).
// Planilha (pedidos): os pedidos do batchUpdate, por lote, com a contagem que cada findReplace tem de responder.
//
//   node r53/diagnostico-android/preparar_maxima_r67.js <pasta com os .gs instalados> <pasta de saída>
//   node r53/diagnostico-android/preparar_maxima_r67.js --pedidos <ids.json> <saida.json> [--ponto-e-virgula]
//        (ids.json: {"DADOS_R53": id, "DADOS_AM": id, "FICHA AMALDIÇOADA": id, "INVOCAÇÕES": id})
const fs = require('fs'), path = require('path'), zlib = require('zlib'), crypto = require('crypto'), vm = require('vm');
const achatador = require('./preparar_modulo_achatado');

const ANTES = {
  Codigo: '94f1a184f2af',
  EditorR53: '35065b22a3ea',
  AnaliseEstatica: '450709a1a988',
  modulo: '35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10',
  catalogo: 'da1226e924f48ff01c7ec1e0a57faf77e8556f23027656dd225508e6cfdaf0e3',
};
const ABAS_MOLDE = ['FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'DADOS_AM'];
const ANCORA_AJUSTE = ' try { r53AjustarMoldeApi_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n';
const CHAMADA = ' try { r53AjustarMaximaR67_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n';
const LIVRE_T357 = [357, 20, 357, 20];
const ABRE_MODULO = 'function r53Modulo_() {';
const MARCA = ' // R53 achatado: remendos aplicados no pacote por preparar_modulo_achatado.js; fonte ';

// PR #135 (19c8f4a e b2078d4): os dois trechos do Ficha.gs, como estão dentro do pacote achatado.
const FICHA_PARES = [
  ['function gruposDeMescla_(merges) {',
    '/**\n' +
    ' * Cria os grupos de linhas e de colunas de uma aba (`[primeira, última, ...]`, base 1). Com o serviço Google Sheets\n' +
    ' * ligado, tudo vai num batchUpdate só; sem ele, um shiftRowGroupDepth por grupo, como antes. O flush antes da chamada\n' +
    ' * garante que a API veja a aba com o que o SpreadsheetApp já gravou.\n' +
    ' */\n' +
    'function criarGrupos_(aba, lin, col) {\n' +
    '  if (!lin.length && !col.length) return;\n' +
    "  if (typeof Sheets !== 'undefined' && Sheets.Spreadsheets) {\n" +
    '    var id = aba.getSheetId();\n' +
    '    var pedido = function (dim) {\n' +
    '      return function (g) { return { addDimensionGroup: { range: { sheetId: id, dimension: dim, startIndex: g[0] - 1, endIndex: g[1] } } }; };\n' +
    '    };\n' +
    '    SpreadsheetApp.flush();\n' +
    "    Sheets.Spreadsheets.batchUpdate({ requests: lin.map(pedido('ROWS')).concat(col.map(pedido('COLUMNS'))) },\n" +
    '      aba.getParent().getId());\n' +
    '    return;\n' +
    '  }\n' +
    '  lin.forEach(function (g) { aba.getRange(g[0], 1, g[1] - g[0] + 1, 1).shiftRowGroupDepth(1); });\n' +
    '  col.forEach(function (g) { aba.getRange(1, g[0], 1, g[1] - g[0] + 1).shiftColumnGroupDepth(1); });\n' +
    '}\n' +
    '\n' +
    'function gruposDeMescla_(merges) {'],
  ['    (spec.grupos.lin || []).forEach(function (g) { aba.getRange(g[0], 1, g[1] - g[0] + 1, 1).shiftRowGroupDepth(1); });\n' +
    '    (spec.grupos.col || []).forEach(function (g) { aba.getRange(1, g[0], 1, g[1] - g[0] + 1).shiftColumnGroupDepth(1); });',
    '    // 18/11/2026: na MONTAGENS, os 207 grupos um por vez levaram 201 s e a aba passava dos 6 minutos. Com o serviço\n' +
    '    // Google Sheets do projeto, todos nascem numa chamada só (addDimensionGroup, na mesma ordem: o de dentro aprofunda).\n' +
    '    criarGrupos_(aba, spec.grupos.lin || [], spec.grupos.col || []);'],
  ['    if (t.length > 3) {\n      var e = spec.estilos[t[3]];',
    '    // 18/11/2026: a R53_EVENTOS (r53/caminho_leve.js) grava o estilo 0 com a lista de estilos vazia; sem o estilo,\n' +
    '    // a caixa fica com o padrão da aba.\n' +
    '    if (t.length > 3 && spec.estilos && spec.estilos[t[3]]) {\n      var e = spec.estilos[t[3]];'],
];

const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
/** gzip igual em qualquer máquina: o byte de sistema do cabeçalho fica 3 (Unix), como no Linux e no navegador. */
const gzip = s => { const b = zlib.gzipSync(Buffer.from(s, 'utf8'), { level: 9, mtime: 0 }); b[9] = 3; return b; };
const gz64 = s => gzip(s).toString('base64');
const ungz = b64 => zlib.gunzipSync(Buffer.from(b64, 'base64')).toString('utf8');

function plano() { return JSON.parse(fs.readFileSync(path.join(__dirname, 'maxima_r67_plano.json'), 'utf8')); }

function trocarUma(texto, velho, novo, onde) {
  const n = texto.split(velho).length - 1;
  if (n !== 1) throw Error(onde + ': trecho antigo encontrado ' + n + ' vez(es)');
  return texto.replace(velho, () => novo);
}

/** Aplica o trecho de linha (\x01 = número da linha) numa fórmula; o antes tem de aparecer uma vez só. */
function aplicarTrecho(f, r, ta, tb, onde) {
  return trocarUma(f, ta.replace(/\x01/g, r), tb.replace(/\x01/g, r), onde + ' ' + r);
}

// ---------------------------------------------------------------------------------------------------------- molde

/** O .gs do ajuste do molde (vai no Codigo, fora do pacote): células e notas dos cartões. */
function runtimeAjuste(p) {
  p = p || plano();
  const dados = { celulas: p.celulas.filter(d => ABAS_MOLDE.indexOf(d[0]) >= 0), notas: p.notas };
  return [
    '// GERADO por r53/diagnostico-android/preparar_maxima_r67.js: a Técnica Máxima R67 no molde dos cartões',
    '// (' + dados.celulas.length + ' células e ' + dados.notas.length + ' notas na FICHA AMALDIÇOADA, INVOCAÇÕES e DADOS_AM).',
    'var R53_MAXIMA_R67_ = ' + JSON.stringify(gz64(JSON.stringify(dados))) + ';',
    'function r53AjustarMaximaR67_(abas) {',
    "  var p = JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(R53_MAXIMA_R67_), 'application/gzip')).getDataAsString('UTF-8'));",
    '  if (p.celulas.length !== ' + dados.celulas.length + ' || p.notas.length !== ' + dados.notas.length + ") throw new Error('Máxima R67: plano incompleto');",
    '  var specs = {}, ops = [];',
    '  var spec = function (nome) {',
    '    if (!specs[nome]) {',
    '      var achadas = abas.filter(function (a) { return a.nome === nome; });',
    "      if (achadas.length !== 1 || !Array.isArray(achadas[0].vals)) throw new Error('Máxima R67: aba divergente ' + nome);",
    '      var s = achadas[0], idx = {};',
    "      s.vals.forEach(function (v) { var k = v[0] + ':' + v[1]; (idx[k] = idx[k] || []).push(v); });",
    '      specs[nome] = { s: s, idx: idx };',
    '    }',
    '    return specs[nome];',
    '  };',
    '  p.celulas.forEach(function (d) {',
    "    var e = spec(d[0]), alvos = e.idx[d[1] + ':' + d[2]] || [];",
    '    if (alvos.length === 1 && JSON.stringify(alvos[0][2]) === JSON.stringify(d[4])) return;',
    '    if (d[3] === null) {',
    "      if (alvos.length) throw new Error('Máxima R67: célula nova já ocupada ' + d[0] + ' ' + d[1] + ',' + d[2]);",
    '      ops.push(function () {',
    '        var t = [d[1], d[2], d[4]];',
    '        if (d[5]) {',
    '          var lista = e.s.estilos = e.s.estilos || [], k = -1;',
    '          lista.forEach(function (x, i) { if (k < 0 && JSON.stringify(x) === JSON.stringify(d[5])) k = i; });',
    '          if (k < 0) { lista.push(d[5]); k = lista.length - 1; }',
    '          t.push(k);',
    '        }',
    '        e.s.vals.push(t);',
    '      });',
    '      return;',
    '    }',
    '    if (alvos.length !== 1 || JSON.stringify(alvos[0][2]) !== JSON.stringify(d[3]))',
    "      throw new Error('Máxima R67: alvo divergente ' + d[0] + ' ' + d[1] + ',' + d[2]);",
    '    ops.push(function () { alvos[0][2] = d[4]; });',
    '  });',
    '  p.notas.forEach(function (d) {',
    '    var s = spec(d[0]).s, lista = s.notas = s.notas || [];',
    '    var achadas = lista.filter(function (n) { return n[0] === d[1]; });',
    '    if (achadas.length > 1) throw new Error("Máxima R67: nota repetida " + d[0] + " " + d[1]);',
    '    var agora = achadas.length ? achadas[0][1] : null;',
    '    if (agora === d[3]) return;',
    '    if (agora !== d[2]) throw new Error("Máxima R67: nota divergente " + d[0] + " " + d[1]);',
    '    ops.push(function () {',
    '      if (d[3] === null) s.notas = lista.filter(function (n) { return n[0] !== d[1]; });',
    '      else if (achadas.length) achadas[0][1] = d[3];',
    '      else lista.push([d[1], d[3]]);',
    '    });',
    '  });',
    '  ops.forEach(function (op) { op(); });',
    '}',
    ''].join('\n');
}

// ------------------------------------------------------------------------------------------------- Prática Cotidiana

const RE_PRATICA = n => n + "=JSON\\.parse\\(Utilities\\.ungzip\\(Utilities\\.newBlob\\(Utilities\\.base64Decode\\(\"([A-Za-z0-9+/=]+)\"\\)";

/** O molde da montagem como o pratica_cotidiana_runtime.js escreve (o número da linha vira \x01). */
function moldePratica(f, r) {
  const refs = new RegExp("(('DADOS_R53'!\\$FZ\\$)|(?<![\\w.])(\\$?[A-Z]{1,3}))" + r + "(?![\\w(])", 'g');
  if (f.includes('\x01')) throw Error('Marcador já presente na fórmula de montagem');
  const m = f.split(/("(?:[^"]|"")*")/).map((p, i) => i % 2 ? p : p.replace(refs, '$1\x01')).join('');
  if (m.replace(/\x01/g, String(r)) !== f) throw Error('Molde de montagem divergente');
  return m;
}

/** Pura: troca a FX e as 14 células das linhas 252–253 nos dados do restaurador da Prática. */
function ajustarPratica(montagem, dados, p) {
  p = p || plano();
  const porCol = new Map(p.dadosR53.map(g => [g[0], g]));
  let nMont = 0, nDados = 0;
  // montagem: [coluna, molde, [linhas]]; refaz os grupos das colunas trocadas
  const novos = new Map(), fora = [];
  for (const [c, m, linhas] of montagem) {
    const g = porCol.get(c);
    if (!g) { fora.push([c, m, linhas]); continue; }
    for (const r of linhas) {
      if (g[3].indexOf(r) < 0) throw Error('Prática: linha fora da R67 ' + r + ':' + c);
      const f = aplicarTrecho(m.replace(/\x01/g, String(r)), r, g[1], g[2], 'Prática (montagem)');
      const k = JSON.stringify([c, moldePratica(f, r)]);
      if (!novos.has(k)) novos.set(k, []);
      novos.get(k).push(r); nMont++;
    }
  }
  const montagemNova = fora.concat([...novos].map(([k, l]) => JSON.parse(k).concat([l])));
  // dados: [aba, linha, coluna, valor]; a FX das linhas 252–253 vem da montagem (que passa por cima) e fica
  const montCols = new Set(montagem.map(g => g[0]));
  const dadosNovos = dados.map(v => {
    if (v[0] !== 'DADOS_R53' || montCols.has(v[2])) return v;
    const g = porCol.get(v[2]);
    if (!g || g[3].indexOf(v[1]) < 0) return v;
    nDados++;
    return [v[0], v[1], v[2], aplicarTrecho(v[3], v[1], g[1], g[2], 'Prática (dados)')];
  });
  return { montagem: montagemNova, dados: dadosNovos, nMont, nDados };
}

// --------------------------------------------------------------------------------------------------------- Codigo

/** Pura: o Codigo novo. `modulo` = { fonte, tamanho } do pacote novo; `catalogo` = hash do catálogo novo do editor. */
function prepararCodigo(src, modulo, catalogo, p, antes) {
  p = p || plano(); antes = antes || ANTES;
  if (src.indexOf('function r53AjustarMaximaR67_(') >= 0) throw Error('Máxima R67 já presente');
  let out = trocarUma(src, ANCORA_AJUSTE, ANCORA_AJUSTE + CHAMADA, 'Codigo: chamada do molde API');
  // restaurador da Prática
  const reM = new RegExp(RE_PRATICA('R53_PRATICA_MONTAGEM_')), reD = new RegExp(RE_PRATICA('R53_PRATICA_CACHE_'));
  const mM = reM.exec(out), mD = reD.exec(out);
  if (!mM || !mD) throw Error('Codigo: restaurador da Prática ausente');
  const prat = ajustarPratica(JSON.parse(ungz(mM[1])), JSON.parse(ungz(mD[1])), p);
  const fx = p.dadosR53.find(g => g[0] === 180);
  if (prat.nMont !== fx[3].length || prat.nDados !== 14) throw Error('Prática: contagem divergente ' + prat.nMont + '/' + prat.nDados);
  out = trocarUma(out, mM[1], gz64(JSON.stringify(prat.montagem)), 'Codigo: montagem da Prática');
  out = trocarUma(out, mD[1], gz64(JSON.stringify(prat.dados)), 'Codigo: dados da Prática');
  // mapa do atalho: a T357 (fórmula do SEM DANO) da FA
  const mL = /^var R53_LIVRE_=(\{.*\});$/m.exec(out);
  if (!mL) throw Error('Codigo: mapa do atalho ausente');
  const livre = JSON.parse(mL[1]), fa = livre['FICHA AMALDIÇOADA'];
  if (!fa || fa.some(q => LIVRE_T357[0] <= q[2] && LIVRE_T357[2] >= q[0] && LIVRE_T357[1] <= q[3] && LIVRE_T357[3] >= q[1]))
    throw Error('Codigo: T357 já no mapa do atalho');
  fa.push(LIVRE_T357);
  out = trocarUma(out, mL[0], 'var R53_LIVRE_=' + JSON.stringify(livre) + ';', 'Codigo: mapa do atalho');
  // cabeça do módulo achatado
  const ini = out.indexOf(ABRE_MODULO), fim = out.indexOf('\n}\n', ini);
  const corpo = out.slice(ini, fim);
  const mF = new RegExp(MARCA.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([0-9a-f]{64})\\.').exec(corpo);
  const mT = /if\(code\.length!==(\d+)\)throw new Error\('Pacote R53 incompleto: tamanho divergente\.'\);/.exec(corpo);
  if (!mF || !mT || mF[1] !== antes.modulo) throw Error('Codigo: cabeça do módulo achatado divergente');
  const corpoNovo = corpo.replace(mF[0], () => MARCA + modulo.fonte + '.')
    .replace(mT[0], () => mT[0].replace(mT[1], String(modulo.tamanho)));
  const partes = /\[((?:R53_CODIGO_\d+_,)*R53_CODIGO_\d+_)\]\.join/.exec(corpoNovo);
  const nomes = []; for (let k = 0; k < modulo.partes; k++) nomes.push('R53_CODIGO_' + k + '_');
  out = out.slice(0, ini) + corpoNovo.replace(partes[1], nomes.join(',')) + out.slice(fim);
  // atalho: os dois hashes
  const mH = /^var R53_LIVRE_HASHES_=\["([0-9a-f]{64})","([0-9a-f]{64})"\];$/m.exec(out);
  if (!mH) throw Error('Codigo: R53_LIVRE_HASHES_ com forma inesperada');
  if (mH[1] !== antes.modulo || mH[2] !== antes.catalogo)
    throw Error('Codigo: atalho já desligado (' + mH[1].slice(0, 8) + '/' + mH[2].slice(0, 8) + ')');
  out = out.replace(mH[0], () => 'var R53_LIVRE_HASHES_=["' + modulo.fonte + '","' + catalogo + '"];');
  out = out + '\n' + runtimeAjuste(p);
  new vm.Script(out);
  return out;
}

// ------------------------------------------------------------------------------------------------------- EditorR53

const RE_CATALOGO = /base64Decode\("([A-Za-z0-9+/=]+)"\),"application\/gzip"\)\)\.getDataAsString\("UTF-8"\);var hash=[^\n]*?;if\(hash!=="([0-9a-f]{64})"\)/;

/** Pura: o EditorR53 com os contextos da Máxima trocados; devolve o texto e o hash do catálogo novo. */
function prepararEditor(src, p, catalogoAntes) {
  p = p || plano(); catalogoAntes = catalogoAntes || ANTES.catalogo;
  const m = RE_CATALOGO.exec(src);
  if (!m || src.split('function r53ConfigEditor_(){').length !== 2) throw Error('EditorR53: catálogo compactado ausente');
  const texto = ungz(m[1]);
  if (sha(texto) !== m[2] || m[2] !== catalogoAntes) throw Error('EditorR53: catálogo diferente do esperado');
  const cfg = JSON.parse(texto);
  if (JSON.stringify(cfg) !== texto) throw Error('EditorR53: serialização do catálogo divergente');
  const idx = Object.keys(p.editor).map(Number);
  if (idx.join(',') !== '44,204,208,212,216,220,224,228,232,236,240,244,248') throw Error('EditorR53: contextos do plano divergentes');
  for (const i of idx) {
    const atual = JSON.stringify(cfg.contextos[i]);
    if (sha(atual) !== p.editor[i].antes) throw Error('EditorR53: contexto ' + i + ' divergente');
    cfg.contextos[i] = p.editor[i].depois;
  }
  const novo = JSON.stringify(cfg), hash = sha(novo);
  const out = src.replace(m[0], () => m[0].replace(m[1], gz64(novo)).replace(m[2], hash));
  new vm.Script(out);
  return { texto: out, catalogo: hash };
}

// ------------------------------------------------------------------------------------------------------------ módulo

/** Pura: os consertos do construir() no texto do pacote. */
function prepararModulo(code) {
  if (code.indexOf('function criarGrupos_(') >= 0) throw Error('Módulo: criarGrupos_ já presente');
  let out = code;
  FICHA_PARES.forEach(([velho, novo], i) => { out = trocarUma(out, velho, novo, 'Módulo: conserto ' + (i + 1) + ' da PR #135'); });
  new Function(out);
  return out;
}

// ----------------------------------------------------------------------------------------------------------- projeto

/** O arquivo de um conjunto {nome: texto} que contém o marcador; exatamente um. */
function unico(arquivos, marca, onde) {
  const n = Object.keys(arquivos).filter(k => arquivos[k].indexOf(marca) >= 0);
  if (n.length !== 1) throw Error(onde + ' encontrado em ' + n.length + ' arquivo(s)');
  return n[0];
}

/**
 * Pura: o projeto novo. `arquivos` = {nome: texto} do projeto instalado; `analise` = texto do AnaliseEstatica novo.
 * `conferir` = false só nos testes com projeto sintético.
 */
function prepararProjeto(arquivos, analise, opcoes) {
  opcoes = Object.assign({ conferir: true }, opcoes);
  const p = opcoes.plano || plano();
  const nCod = unico(arquivos, ABRE_MODULO, 'r53Modulo_'), nEd = unico(arquivos, 'function r53ConfigEditor_(){', 'r53ConfigEditor_');
  const nAn = unico(arquivos, 'function analiseCaixaInstalar_(', 'analiseCaixaInstalar_');
  if (opcoes.conferir) {
    for (const [n, h] of [[nCod, ANTES.Codigo], [nEd, ANTES.EditorR53], [nAn, ANTES.AnaliseEstatica]])
      if (sha(arquivos[n]).slice(0, 12) !== h) throw Error(n + ' diferente do instalado nas oficiais (exige ' + h + ')');
  }
  if (analise.indexOf('destino.breakApart();') < 0) throw Error('AnaliseEstatica nova sem o breakApart');
  // módulo
  const textos = Object.keys(arquivos).map(k => arquivos[k]), achadas = achatador.lerPartes(textos);
  const nomes = Object.keys(arquivos);
  const ks = Object.keys(achadas).map(Number).sort((a, b) => a - b);
  ks.forEach((k, i) => { if (k !== i) throw Error('Partes do módulo fora de ordem'); });
  const code = ungz(ks.map(k => achadas[k].valor).join(''));
  if (opcoes.conferir && sha(code) !== ANTES.modulo) throw Error('Módulo diferente do instalado (exige ' + ANTES.modulo.slice(0, 12) + ')');
  const codeNovo = prepararModulo(code), fonte = sha(codeNovo);
  const b64 = gzip(codeNovo).toString('base64');
  if (ungz(b64) !== codeNovo) throw Error('Compressão do módulo divergente');
  const d = achatador.distribuir(b64, { partes: ks.map(k => 'R53_CODIGO_' + k + '_') }, achadas, textos);
  // editor e Codigo
  const ed = prepararEditor(arquivos[nEd], p);
  const cod = prepararCodigo(arquivos[nCod], { fonte, tamanho: codeNovo.length, partes: d.nPartes }, ed.catalogo, p);
  const novos = Object.assign({}, arquivos);
  Object.keys(d.saida).forEach(a => { novos[nomes[a]] = d.saida[a]; });
  novos[nCod] = cod; novos[nEd] = ed.texto; novos[nAn] = analise;
  const hashes = {};
  for (const n of nomes) hashes[n] = { antes: sha(arquivos[n]).slice(0, 12), depois: sha(novos[n]).slice(0, 12) };
  return { arquivos: novos, hashes, modulo: { antes: sha(code), fonte, tamanho: codeNovo.length, partes: d.nPartes },
    catalogo: { antes: ANTES.catalogo, depois: ed.catalogo } };
}

// --------------------------------------------------------------------------------------------------------- planilha

const A1 = (r, c) => { let s = '', n = c; while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); } return s + r; };
const TRACO = { thin: 'SOLID', medium: 'SOLID_MEDIUM', thick: 'SOLID_THICK', dashed: 'DASHED', dotted: 'DOTTED', double: 'DOUBLE' };
const cor = h => ({ red: parseInt(h.slice(1, 3), 16) / 255, green: parseInt(h.slice(3, 5), 16) / 255, blue: parseInt(h.slice(5, 7), 16) / 255 });
const escaparRegex = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** Vírgula de argumento vira ponto e vírgula fora dos textos (para planilha que compara a fórmula no idioma dela). */
function pontoEVirgula(f) {
  return f.split(/("(?:[^"]|"")*")/).map((p, i) => i % 2 ? p : p.replace(/,/g, ';')).join('');
}

/** A regex de um trecho de linha: o primeiro número de linha é o grupo 1, os outros só precisam ser número. */
function regexDoTrecho(t) {
  const partes = t.split('\x01').map(escaparRegex);
  return partes.length === 1 ? partes[0] : partes[0] + '(\\d+)' + partes.slice(1).join('\\d+');
}
const substituicao = t => t.replace(/\$/g, '$$$$').replace(/\x01/g, '$1');

// Planilha em pt_BR: a API lê e devolve a fórmula com ponto e vírgula; com vírgula dá "Formula parse error" (visto
// no ensaio de 18/11). As fórmulas da R67 não têm decimal nem matriz literal fora das aspas (o teste confere).
function valorApi(v, fr) {
  if (typeof v === 'boolean') return { boolValue: v };
  if (typeof v === 'number') return { numberValue: v };
  if (typeof v === 'string' && v[0] === '=') return { formulaValue: (fr || (s => s))(v) };
  return { stringValue: v };
}

/**
 * Os pedidos da planilha, em lotes, com a resposta esperada de cada findReplace. `ids` = {aba: sheetId}.
 * Ordem: DADOS_R53 (células, depois colunas por regex em faixas de até 40 linhas), DADOS_AM, cartões
 * (desfaz mesclas, valores e estilos das caixas novas, notas, caixas de seleção, fundos, formatos, mescla nova, bordas).
 */
function pedidos(ids, opcoes) {
  opcoes = Object.assign({ faixa: 40, pontoEVirgula: false }, opcoes);
  const p = opcoes.plano || plano();
  const id = aba => { if (!Number.isInteger(ids[aba])) throw Error('sheetId ausente: ' + aba); return ids[aba]; };
  const cel = (aba, r, c) => ({ sheetId: id(aba), startRowIndex: r - 1, endRowIndex: r, startColumnIndex: c - 1, endColumnIndex: c });
  const lotes = [];
  const fr = opcoes.pontoEVirgula ? pontoEVirgula : (s => s);
  // 1. DADOS_R53: as 26 células
  lotes.push({ nome: 'DADOS_R53 células', pedidos: p.celulas.filter(d => d[0] === 'DADOS_R53').map(d => ({
    updateCells: { range: cel('DADOS_R53', d[1], d[2]), rows: [{ values: [{ userEnteredValue: valorApi(d[4], fr) }] }], fields: 'userEnteredValue' } })) });
  // 2. DADOS_R53: colunas por regex
  for (const [c, ta, tb, linhas] of p.dadosR53) {
    // faixas contínuas (a linha 251 fica de fora: a R67 não muda nada nela) de até `faixa` linhas
    const fatias = [];
    for (const r of linhas) {
      const ult = fatias[fatias.length - 1];
      if (ult && r === ult[ult.length - 1] + 1 && ult.length < opcoes.faixa) ult.push(r); else fatias.push([r]);
    }
    for (const fatia of fatias) {
      lotes.push({ nome: 'DADOS_R53 ' + A1(fatia[0], c) + ':' + A1(fatia[fatia.length - 1], c), esperado: fatia.length, pedidos: [{
        findReplace: { find: regexDoTrecho(fr(ta)), replacement: substituicao(fr(tb)), searchByRegex: true, includeFormulas: true,
          matchCase: true, range: { sheetId: id('DADOS_R53'), startRowIndex: fatia[0] - 1, endRowIndex: fatia[fatia.length - 1],
            startColumnIndex: c - 1, endColumnIndex: c } } }] });
    }
  }
  // 3. DADOS_AM e cartões
  const cartoes = [];
  for (const [aba, me] of Object.entries(p.mesclas)) for (const m of me.menos)
    cartoes.push({ unmergeCells: { range: { sheetId: id(aba), startRowIndex: m[0] - 1, endRowIndex: m[2], startColumnIndex: m[1] - 1, endColumnIndex: m[3] } } });
  for (const d of p.celulas.filter(d => d[0] !== 'DADOS_R53')) {
    const v = { userEnteredValue: valorApi(d[4], fr) };
    let fields = 'userEnteredValue';
    if (d[5]) {
      const e = d[5];
      v.userEnteredFormat = { textFormat: { fontFamily: e[0], fontSize: e[1], foregroundColorStyle: { rgbColor: cor(e[2] || '#000000') },
        bold: !!e[3], italic: !!e[7] }, horizontalAlignment: String(e[4]).toUpperCase(),
        verticalAlignment: (e[5] === 'center' ? 'middle' : e[5]).toUpperCase(), wrapStrategy: e[8] ? 'WRAP' : 'OVERFLOW_CELL' };
      fields += ',userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment,userEnteredFormat.wrapStrategy';
    }
    cartoes.push({ updateCells: { range: cel(d[0], d[1], d[2]), rows: [{ values: [v] }], fields } });
  }
  for (const [aba, a1, , depois] of p.notas) {
    const m = /^([A-Z]+)(\d+)$/.exec(a1); let c = 0; for (const ch of m[1]) c = c * 26 + ch.charCodeAt(0) - 64;
    cartoes.push({ updateCells: { range: cel(aba, +m[2], c), rows: [{ values: [{ note: depois === null ? '' : depois }] }], fields: 'note' } });
  }
  for (const [aba, lista] of Object.entries(p.caixas)) for (const [c, r, n] of lista)
    cartoes.push({ setDataValidation: { range: { sheetId: id(aba), startRowIndex: r - 1, endRowIndex: r - 1 + n, startColumnIndex: c - 1, endColumnIndex: c },
      rule: { condition: { type: 'BOOLEAN' }, strict: true } } });
  for (const [aba, r, c, , depois] of p.fundos)
    cartoes.push({ repeatCell: { range: cel(aba, r, c), cell: { userEnteredFormat: { backgroundColorStyle: { rgbColor: cor(depois) } } },
      fields: 'userEnteredFormat.backgroundColorStyle' } });
  for (const [aba, a1, fmt] of p.formatos) {
    const m = /^([A-Z]+)(\d+)$/.exec(a1); let c = 0; for (const ch of m[1]) c = c * 26 + ch.charCodeAt(0) - 64;
    cartoes.push({ repeatCell: { range: cel(aba, +m[2], c), cell: { userEnteredFormat: { numberFormat: { type: 'NUMBER', pattern: fmt } } },
      fields: 'userEnteredFormat.numberFormat' } });
  }
  for (const [aba, me] of Object.entries(p.mesclas)) for (const m of me.mais)
    cartoes.push({ mergeCells: { mergeType: 'MERGE_ALL', range: { sheetId: id(aba), startRowIndex: m[0] - 1, endRowIndex: m[2], startColumnIndex: m[1] - 1, endColumnIndex: m[3] } } });
  for (const [aba, t, r, c, , depois] of p.bordas) {
    const lado = depois ? { style: TRACO[depois[0]] || 'SOLID', colorStyle: { rgbColor: cor(depois[1]) } } : { style: 'NONE' };
    const b = { range: cel(aba, r, c) };
    b[t === 'h' ? 'top' : 'left'] = lado;
    cartoes.push({ updateBorders: b });
  }
  lotes.push({ nome: 'DADOS_AM e cartões', pedidos: cartoes });
  return lotes;
}

/** A volta dos findReplace da DADOS_R53 (troca antes e depois); o resto volta pela foto tirada antes (ver o roteiro). */
function pedidosVolta(ids, opcoes) {
  const p = Object.assign({}, (opcoes && opcoes.plano) || plano());
  p.dadosR53 = p.dadosR53.map(([c, ta, tb, l]) => [c, tb, ta, l]);
  p.celulas = p.celulas.filter(d => d[0] === 'DADOS_R53').map(d => [d[0], d[1], d[2], d[4], d[3], null]);
  return pedidos(ids, Object.assign({}, opcoes, { plano: p })).filter(l => l.nome.indexOf('DADOS_R53') === 0);
}

/** As faixas que a foto de antes tem de cobrir nos cartões (valor, formato, nota, validação, mescla). */
function faixasDaFoto(p) {
  p = p || plano();
  const pts = {};
  const add = (aba, r, c) => { (pts[aba] = pts[aba] || []).push([r, c]); };
  p.celulas.filter(d => d[0] !== 'DADOS_R53').forEach(d => add(d[0], d[1], d[2]));
  p.fundos.forEach(d => add(d[0], d[1], d[2]));
  p.bordas.forEach(d => { add(d[0], d[2], d[3]); if (d[1] === 'h') add(d[0], d[2] - 1, d[3]); else add(d[0], d[2], d[3] - 1); });
  Object.entries(p.mesclas).forEach(([aba, me]) => me.mais.concat(me.menos).forEach(m => { add(aba, m[0], m[1]); add(aba, m[2], m[3]); }));
  const faixas = [];
  for (const [aba, l] of Object.entries(pts)) {
    l.sort((a, b) => a[0] - b[0]);
    let bloco = null;
    for (const [r, c] of l) {
      if (bloco && r <= bloco[2] + 3) { bloco[2] = Math.max(bloco[2], r); bloco[1] = Math.min(bloco[1], c); bloco[3] = Math.max(bloco[3], c); }
      else { bloco = [r, c, r, c]; faixas.push([aba, bloco]); }
    }
  }
  return faixas.map(([aba, b]) => "'" + aba + "'!" + A1(b[0], b[1]) + ':' + A1(b[2], b[3]));
}

if (require.main === module) {
  const a = process.argv.slice(2);
  if (a[0] === '--pedidos') {
    const ids = JSON.parse(fs.readFileSync(a[1], 'utf8')), pv = a.includes('--ponto-e-virgula');
    const saida = { ida: pedidos(ids, { pontoEVirgula: pv }), volta: pedidosVolta(ids, { pontoEVirgula: pv }), foto: faixasDaFoto() };
    fs.writeFileSync(a[2], JSON.stringify(saida, null, 1));
    console.log(JSON.stringify({ lotes: saida.ida.length, pedidos: saida.ida.reduce((s, l) => s + l.pedidos.length, 0), foto: saida.foto }));
  } else if (a.length === 2) {
    const arquivos = {};
    for (const n of fs.readdirSync(a[0]).filter(n => n.endsWith('.gs'))) arquivos[n] = fs.readFileSync(path.join(a[0], n), 'utf8');
    const analise = fs.readFileSync(path.join(__dirname, '../../apps-script/AnaliseEstatica.gs'), 'utf8');
    const r = prepararProjeto(arquivos, analise);
    fs.mkdirSync(a[1], { recursive: true });
    for (const [n, t] of Object.entries(r.arquivos)) fs.writeFileSync(path.join(a[1], n), t);
    fs.writeFileSync(path.join(a[1], 'manifesto.json'), JSON.stringify({ hashes: r.hashes, modulo: r.modulo, catalogo: r.catalogo }, null, 1));
    console.log(JSON.stringify({ hashes: r.hashes, modulo: r.modulo.fonte.slice(0, 12), partes: r.modulo.partes, catalogo: r.catalogo.depois.slice(0, 12) }, null, 1));
  } else { console.error('uso: <pasta instalada> <pasta saída> | --pedidos <ids.json> <saida.json> [--ponto-e-virgula]'); process.exit(2); }
}

module.exports = { ANTES, FICHA_PARES, CHAMADA, LIVRE_T357, sha, gzip, ungz, plano, aplicarTrecho, runtimeAjuste, moldePratica,
  ajustarPratica, prepararCodigo, prepararEditor, prepararModulo, prepararProjeto, pedidos, pedidosVolta, faixasDaFoto,
  regexDoTrecho, substituicao, pontoEVirgula };
