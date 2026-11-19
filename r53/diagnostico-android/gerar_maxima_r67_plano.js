'use strict';
// Gera o plano congelado da rodada R67 (maxima_r67_plano.json), sem Google. Ver PLANO-RODADA-R67-2026-11-18.md.
//
// Compara a saída do gerador antes da R67 (f474691) e depois (0ac372f) e guarda só o que a R67 muda:
//   - celulas: os valores das abas de cartão e da DADOS_AM (FICHA AMALDIÇOADA, INVOCAÇÕES, DADOS_AM), com o estilo
//     da caixa nova;
//   - notas, mesclas, caixas, fundos, formatos e bordas (aresta por aresta) dessas abas;
//   - dadosR53: as fórmulas da DADOS_R53 em moldes de linha (o número da linha vira \x01), com as linhas de cada um;
//   - editor: os 13 contextos da Máxima (44 e 204–248), com o hash do antes de cada um.
//
//   git archive f474691 apps-script | tar -x -C <antes>;  git archive 0ac372f apps-script | tar -x -C <depois>
//   node r53/diagnostico-android/gerar_maxima_r67_plano.js <antes>/apps-script <depois>/apps-script
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { ler, expandir } = require('../testes/expansao_domada_modelo');

const ABAS_CARTAO = ['FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'DADOS_AM'];
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');

function colNum(l) { let c = 0; for (const ch of l) c = c * 26 + ch.charCodeAt(0) - 64; return c; }
function faixa(a1) {
  const m = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(a1);
  if (!m) throw Error('A1 inválido ' + a1);
  const r1 = +m[2], c1 = colNum(m[1]);
  return [r1, c1, m[3] ? +m[4] : r1, m[3] ? colNum(m[3]) : c1];
}

/** As arestas que a lista de bordas desenha (a última vence, como no montarAba_): chave -> [traço, cor]. */
function arestas(bordas) {
  const m = new Map();
  for (const [lado, traco, cor, lista] of bordas || []) for (const a1 of lista) {
    const [r1, c1, r2, c2] = faixa(a1);
    if (lado === 'top' || lado === 'bottom') {
      const r = lado === 'top' ? r1 : r2 + 1;
      for (let c = c1; c <= c2; c++) m.set('h:' + r + ':' + c, [traco, cor]);
    } else {
      const c = lado === 'left' ? c1 : c2 + 1;
      for (let r = r1; r <= r2; r++) m.set('v:' + r + ':' + c, [traco, cor]);
    }
  }
  return m;
}

/** Molde de linha: as referências à própria linha viram \x01 (fora dos textos entre aspas). */
function molde(f, r) {
  const refs = new RegExp("((?<![\\w.])\\$?[A-Z]{1,3})" + r + "(?![\\w(\\d])", 'g');
  const m = f.split(/("(?:[^"]|"")*")/).map((p, i) => i % 2 ? p : p.replace(refs, '$1\x01')).join('');
  if (m.replace(/\x01/g, String(r)) !== f) throw Error('molde divergente na linha ' + r);
  return m;
}

/** O trecho que muda entre dois moldes, alargado até a fronteira de um nome ou número dos dois lados. */
function trecho(a, b) {
  const fronteira = ch => ch === undefined || !/[A-Za-z0-9_$\x01.]/.test(ch);
  let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
  let j = 0; while (j < a.length - i && j < b.length - i && a[a.length - 1 - j] === b[b.length - 1 - j]) j++;
  while (i > 0 && !(fronteira(a[i - 1]) || fronteira(a[i]))) i--;
  while (j > 0 && !(fronteira(a[a.length - j]) || fronteira(a[a.length - j - 1]))) j--;
  // O novo cita a linha e o antigo não: a regex precisa de um número de linha no antes para o $1. Alarga para trás
  // até a referência à linha mais próxima (o começo é igual nos dois).
  if (b.slice(i, b.length - j).indexOf('\x01') >= 0 && a.slice(i, a.length - j).indexOf('\x01') < 0) {
    const k = a.lastIndexOf('\x01', i - 1);
    if (k < 0) throw Error('trecho sem número de linha para a regex');
    i = k; while (i > 0 && !fronteira(a[i - 1])) i--;
  }
  return [a.slice(i, a.length - j), b.slice(i, b.length - j)];
}

function diferencaConjunto(a, b) {
  const sa = new Set((a || []).map(x => JSON.stringify(x))), sb = new Set((b || []).map(x => JSON.stringify(x)));
  return { mais: [...sb].filter(x => !sa.has(x)).map(x => JSON.parse(x)), menos: [...sa].filter(x => !sb.has(x)).map(x => JSON.parse(x)) };
}

function editorDe(pasta) {
  return JSON.parse(/^var R53_EDITOR_ = (\{[^\n]+\});/m.exec(fs.readFileSync(path.join(pasta, 'EditorR53.gs'), 'utf8'))[1]);
}

function gerar(pastaAntes, pastaDepois) {
  const A = ler(pastaAntes), B = ler(pastaDepois);
  const plano = { origem: { antes: 'f474691', depois: '0ac372f' }, celulas: [], notas: [], mesclas: {}, caixas: {},
    fundos: [], formatos: [], bordas: [], dadosR53: [], editor: {} };
  for (const nome of ABAS_CARTAO) {
    const a = A.find(s => s.nome === nome), b = B.find(s => s.nome === nome);
    const va = new Map(a.vals.map(t => [t[0] + ':' + t[1], t])), vb = new Map(b.vals.map(t => [t[0] + ':' + t[1], t]));
    for (const k of new Set([...va.keys(), ...vb.keys()])) {
      const ta = va.get(k), tb = vb.get(k);
      if (JSON.stringify(ta && ta[2]) === JSON.stringify(tb && tb[2])) continue;
      if (!tb) throw Error('a R67 não apaga célula: ' + nome + '!' + k);
      plano.celulas.push([nome, tb[0], tb[1], ta ? ta[2] : null, tb[2], ta ? null : (b.estilos[tb[3]] || null)]);
    }
    const na = new Map(a.notas || []), nb = new Map(b.notas || []);
    for (const k of new Set([...na.keys(), ...nb.keys()])) if (na.get(k) !== nb.get(k))
      plano.notas.push([nome, k, na.has(k) ? na.get(k) : null, nb.has(k) ? nb.get(k) : null]);
    const me = diferencaConjunto(a.merges, b.merges); if (me.mais.length || me.menos.length) plano.mesclas[nome] = me;
    const cx = diferencaConjunto(a.caixas, b.caixas);
    if (cx.menos.length) throw Error('a R67 não tira caixa');
    if (cx.mais.length) plano.caixas[nome] = cx.mais;
    // fundos célula a célula
    const fundo = s => { const m = new Map(); for (const f of s.fundos || []) for (let c = f[1]; c <= f[2]; c++) m.set(f[0] + ':' + c, f[3]); return m; };
    const fa = fundo(a), fb = fundo(b);
    for (const k of new Set([...fa.keys(), ...fb.keys()])) if (fa.get(k) !== fb.get(k)) {
      const [r, c] = k.split(':').map(Number);
      if (!fb.has(k)) throw Error('fundo removido sem substituto ' + nome + '!' + k);
      plano.fundos.push([nome, r, c, fa.get(k) || null, fb.get(k)]);
    }
    const fo = diferencaConjunto(a.formatos, b.formatos);
    if (fo.menos.length) throw Error('a R67 não tira formato');
    fo.mais.forEach(f => plano.formatos.push([nome].concat(f)));
    const ea = arestas(a.bordas), eb = arestas(b.bordas);
    for (const k of new Set([...ea.keys(), ...eb.keys()])) {
      if (JSON.stringify(ea.get(k)) === JSON.stringify(eb.get(k))) continue;
      const [t, r, c] = k.split(':');
      plano.bordas.push([nome, t, +r, +c, ea.get(k) || null, eb.get(k) || null]);
    }
    if (JSON.stringify(a.estilos) !== JSON.stringify(b.estilos)) throw Error('a R67 não muda estilos: ' + nome);
  }
  // DADOS_R53: célula de uma linha só vai inteira (celulas); coluna inteira vai como trecho de linha (\x01 é o número
  // da linha), que aparece uma vez só em cada fórmula, para o findReplace por regex e para o restaurador da Prática.
  const ra = A.find(s => s.nome === 'DADOS_R53'), rb = B.find(s => s.nome === 'DADOS_R53');
  const xa = expandir(ra), xb = expandir(rb), grupos = new Map();
  for (const k of new Set([...xa.keys(), ...xb.keys()])) {
    if (xa.get(k) === xb.get(k)) continue;
    const [r, c] = k.split(':').map(Number), fa = xa.get(k), fb = xb.get(k);
    if (typeof fa !== 'string' || typeof fb !== 'string' || fa[0] !== '=' || fb[0] !== '=') throw Error('DADOS_R53 fora de fórmula ' + k);
    const [ta, tb] = trecho(molde(fa, r), molde(fb, r));
    const chave = JSON.stringify([c, ta, tb]);
    if (!grupos.has(chave)) grupos.set(chave, []);
    grupos.get(chave).push([r, fa, fb]);
  }
  for (const [chave, linhas] of grupos) {
    const [c, ta, tb] = JSON.parse(chave);
    if (linhas.length === 1) { const [r, fa, fb] = linhas[0]; plano.celulas.push(['DADOS_R53', r, c, fa, fb, null]); continue; }
    for (const [r, fa, fb] of linhas) {
      const a = ta.replace(/\x01/g, r), b = tb.replace(/\x01/g, r);
      if (fa.split(a).length !== 2) throw Error('trecho não é único em DADOS_R53 ' + r + ':' + c);
      if (fa.replace(a, () => b) !== fb) throw Error('trecho não reproduz o depois em ' + r + ':' + c);
    }
    plano.dadosR53.push([c, ta, tb, linhas.map(l => l[0]).sort((x, y) => x - y)]);
  }
  plano.dadosR53.sort((x, y) => x[0] - y[0]);
  // Editor
  const ea = editorDe(pastaAntes), eb = editorDe(pastaDepois);
  for (const k of Object.keys(eb)) if (k !== 'contextos' && JSON.stringify(ea[k]) !== JSON.stringify(eb[k])) throw Error('editor: chave mudou ' + k);
  if (ea.contextos.length !== eb.contextos.length) throw Error('editor: número de contextos');
  ea.contextos.forEach((g, i) => {
    const sa = JSON.stringify(g), sb = JSON.stringify(eb.contextos[i]);
    if (sa !== sb) plano.editor[i] = { antes: sha(sa), depois: eb.contextos[i] };
  });
  return plano;
}

if (require.main === module) {
  const p = gerar(process.argv[2], process.argv[3]);
  const saida = path.join(__dirname, 'maxima_r67_plano.json');
  fs.writeFileSync(saida, JSON.stringify(p) + '\n');
  console.log(JSON.stringify({ celulas: p.celulas.length, notas: p.notas.length, fundos: p.fundos.length,
    formatos: p.formatos.length, bordas: p.bordas.length, caixas: Object.values(p.caixas).flat().length,
    mesclas: Object.fromEntries(Object.entries(p.mesclas).map(([k, v]) => [k, '+' + v.mais.length + ' -' + v.menos.length])),
    dadosR53: p.dadosR53.length + " colunas, " + p.dadosR53.reduce((s, g) => s + g[3].length, 0) + " células",
    editor: Object.keys(p.editor).join(','), bytes: fs.statSync(saida).size }));
}
module.exports = { gerar, arestas, molde, trecho, faixa, colNum };
