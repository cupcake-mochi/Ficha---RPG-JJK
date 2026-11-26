'use strict';
// Teste da rodada R67 nas oficiais (preparar_maxima_r67.js), com defeitos plantados. Ver PLANO-RODADA-R67-2026-11-18.md.
//   node r53/testes/maxima_r67_rodada.js
// Com o projeto instalado das oficiais numa pasta (fora do git), roda também a cadeia inteira sobre os arquivos reais:
//   R67_PROJETO=<pasta com os .gs instalados> node r53/testes/maxima_r67_rodada.js
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const zlib = require('node:zlib'), crypto = require('node:crypto'), cp = require('node:child_process'), os = require('node:os');
const R = require('../diagnostico-android/preparar_maxima_r67');
const { ler, expandir } = require('./expansao_domada_modelo');

const raiz = path.resolve(__dirname, '../..');
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const gz64 = s => zlib.gzipSync(Buffer.from(s, 'utf8')).toString('base64');
const utilities = () => ({
  base64Decode: s => Buffer.from(s, 'base64'), newBlob: x => ({ bytes: Buffer.from(x) }),
  ungzip: b => { const o = zlib.gunzipSync(b.bytes); return { getDataAsString: () => o.toString('utf8') }; },
  computeDigest: (a, t) => [...crypto.createHash('sha256').update(t, 'utf8').digest()].map(x => x > 127 ? x - 256 : x),
  DigestAlgorithm: { SHA_256: 1 }, Charset: { UTF_8: 1 } });
const P = R.plano();
let n = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); n++; };
const recusa = (fn, re, msg) => { assert.throws(fn, re, msg); n++; };
const clone = x => JSON.parse(JSON.stringify(x));

// ---------------------------------------------------------------------------------------------- 1. forma do plano
const porAba = {}; P.celulas.forEach(d => { porAba[d[0]] = (porAba[d[0]] || 0) + 1; });
assert.deepEqual(porAba, { 'FICHA AMALDIÇOADA': 6, 'INVOCAÇÕES': 60, DADOS_AM: 1, DADOS_R53: 26 }); n++;
ok(P.notas.length === 54, 'notas');
ok(new Set(P.celulas.map(d => d[0] + '!' + d[1] + ':' + d[2])).size === P.celulas.length, 'alvo repetido');
ok(P.celulas.every(d => JSON.stringify(d[3]) !== JSON.stringify(d[4])), 'alvo sem mudança');
assert.deepEqual(P.dadosR53.map(g => g[0]), [100, 105, 106, 111, 112, 113, 164, 180]); n++;
ok(P.dadosR53.every(g => g[3].length === 251 && g[3][0] === 2 && g[3][250] === 252 && g[3].indexOf(253) < 0 || g[3].length === 251), 'linhas');
assert.deepEqual(Object.keys(P.editor).map(Number), [44, 204, 208, 212, 216, 220, 224, 228, 232, 236, 240, 244, 248]); n++;
ok(Object.values(P.caixas).flat().length === 13, 'caixas');

// ------------------------------------------------------------------ 2. o "depois" do plano é o gerador de hoje
// 26/11/2026 (etapa 3 da versão rápida): o cartão da Técnica Máxima do personagem virou de preencher (caixinhas DANO /
// CURA / PV TEMP. / SEM DANO na linha 356, valores na 357, conta na DADOS_AM coluna KV) e é conferido em
// cartao_preencher.js. Aqui saem da comparação as células do personagem (FICHA AMALDIÇOADA, DADOS_AM, DADOS_R53 nas
// linhas 2 a 46 e 252–253) e o contexto 44 (maxima.1). As invocações continuam conferidas como antes; os contextos
// delas são achados pelo id, porque mudaram de posição quando os do personagem saíram do editor.
const pessoalR53 = r => r <= 46 || r >= 252;
const doPersonagem = d => d[0] === 'FICHA AMALDIÇOADA' || d[0] === 'DADOS_AM' || (d[0] === 'DADOS_R53' && pessoalR53(d[1]));
const hoje = ler(path.join(raiz, 'apps-script'));
const conferirDepois = (pl, onde) => {
  for (const d of pl.celulas) {
    if (doPersonagem(d)) continue;
    const s = hoje.find(a => a.nome === d[0]), m = expandir(s);
    assert.deepEqual(m.get(d[1] + ':' + d[2]), d[4], onde + ': depois ≠ gerador em ' + d[0] + '!' + d[1] + ':' + d[2]);
  }
  for (const [aba, a1, , depois] of pl.notas) if (aba !== 'FICHA AMALDIÇOADA') assert.equal(new Map(hoje.find(a => a.nome === aba).notas).get(a1) ?? null, depois, onde + ': nota ' + a1);
  const r53 = expandir(hoje.find(a => a.nome === 'DADOS_R53'));
  for (const [c, , tb, linhas] of pl.dadosR53) for (const r of linhas.filter(r => !pessoalR53(r)))
    assert.ok(String(r53.get(r + ':' + c)).split(tb.replace(/\x01/g, r)).length === 2, onde + ': trecho novo ausente em ' + r + ':' + c);
  const ed = JSON.parse(/^var R53_EDITOR_ = (\{[^\n]+\});/m.exec(fs.readFileSync(path.join(raiz, 'apps-script/EditorR53.gs'), 'utf8'))[1]);
  for (const [i, g] of Object.entries(pl.editor)) {
    if (!g.depois.id.startsWith('entidade.')) continue;
    assert.deepEqual(ed.contextos.find(x => x.id === g.depois.id), g.depois, onde + ': contexto ' + i);
  }
};
conferirDepois(P, 'plano'); n++;
// Defeitos: uma célula das invocações com o valor antigo, o contexto de uma entidade antigo, uma célula da FX trocada.
// (Os de antes, R356, contexto 44 e HM38, eram do personagem e foram trocados na etapa 3.)
for (const [nome, estragar] of [
  ['INVOCAÇÕES antiga', p => { const d = p.celulas.find(x => x[0] === 'INVOCAÇÕES'); d[4] = d[3]; }],
  ['contexto 204 antigo', p => { p.editor[204].depois = Object.assign({}, p.editor[204].depois, { formulas: {} }); }],
  ['DADOS_R53 206 antiga', p => { const d = p.celulas.find(x => x[0] === 'DADOS_R53' && x[1] === 206); d[4] = d[3]; }],
  ['FX trocada', p => { const g = p.dadosR53.find(x => x[0] === 180); g[2] = g[2].replace('sem dano', 'sem  dano'); }],
]) { const p = clone(P); estragar(p); recusa(() => conferirDepois(p, nome), assert.AssertionError, 'defeito não acendeu: ' + nome); }

// ------------------------------------------------- 3. (opcional) o plano sai igual do gerador f474691 -> 0ac372f
let regerado = false;
try {
  cp.execSync('git cat-file -e f474691^{commit} && git cat-file -e 0ac372f^{commit}', { cwd: raiz, stdio: 'ignore' });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'r67-'));
  for (const [r, d] of [['f474691', 'a'], ['0ac372f', 'b']]) {
    fs.mkdirSync(path.join(tmp, d));
    cp.execSync('git archive ' + r + ' apps-script | tar -x -C "' + path.join(tmp, d).replace(/\\/g, '/') + '"', { cwd: raiz, stdio: 'ignore', shell: true });
  }
  const g = require('../diagnostico-android/gerar_maxima_r67_plano').gerar(path.join(tmp, 'a/apps-script'), path.join(tmp, 'b/apps-script'));
  assert.deepEqual(clone(g), P, 'plano congelado diferente do gerador'); n++;
  fs.rmSync(tmp, { recursive: true, force: true });
  regerado = true;
} catch (e) { if (e instanceof assert.AssertionError) throw e; }

// -------------------------------------------------------------------------------------- 4. o ajuste do molde
const ctx = vm.createContext({ Utilities: utilities() });
vm.runInContext(R.runtimeAjuste(), ctx);
const sintetico = () => {
  const abas = ['FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'DADOS_AM', 'FICHA'].map(nome => ({ nome, vals: [[1, 1, 'outro']], notas: [['A1', 'nota alheia']], estilos: [['Roboto', 9]] }));
  for (const d of P.celulas.filter(d => d[0] !== 'DADOS_R53')) if (d[3] !== null) abas.find(a => a.nome === d[0]).vals.push([d[1], d[2], d[3], 0]);
  for (const d of P.notas) if (d[2] !== null) abas.find(a => a.nome === d[0]).notas.push([d[1], d[2]]);
  return abas;
};
{
  const abas = sintetico();
  ctx.r53AjustarMaximaR67_(abas);
  for (const d of P.celulas.filter(d => d[0] !== 'DADOS_R53')) {
    const t = abas.find(a => a.nome === d[0]).vals.filter(v => v[0] === d[1] && v[1] === d[2]);
    assert.equal(t.length, 1); assert.equal(JSON.stringify(t[0][2]), JSON.stringify(d[4]));
    if (d[5]) assert.equal(JSON.stringify(abas.find(a => a.nome === d[0]).estilos[t[0][3]]), JSON.stringify(d[5]), 'estilo da caixa nova');
  }
  for (const d of P.notas) assert.equal(new Map(abas.find(a => a.nome === d[0]).notas).get(d[1]) ?? null, d[3]);
  n += 2;
  const uma = JSON.stringify(abas); ctx.r53AjustarMaximaR67_(abas);
  ok(JSON.stringify(abas) === uma, 'aplicar duas vezes muda o molde');
  ok(abas.find(a => a.nome === 'FICHA').vals.length === 1 && abas[0].notas[0][1] === 'nota alheia', 'mexeu fora dos alvos');
}
for (const [nome, estragar] of [
  ['valor divergente', a => { a[1].vals.find(v => v[0] === 228 && v[1] === 12)[2] = '=1'; }],
  ['nota divergente', a => { a[0].notas.find(x => x[0] === P.notas[0][1])[1] = 'outra'; }],
  ['célula nova ocupada', a => { a[0].vals.push([356, 20, 'x']); }],
  ['aba repetida', a => { a.push(clone(a[0])); }],
]) {
  const a = sintetico(); estragar(a); const antes = JSON.stringify(a);
  recusa(() => ctx.r53AjustarMaximaR67_(a), /Máxima R67/, nome);
  ok(JSON.stringify(a) === antes, 'recusa não é atômica: ' + nome);
}

// --------------------------------------------------------------------------- 5. restaurador da Prática Cotidiana
{
  const fx = P.dadosR53.find(g => g[0] === 180);
  const formula = (t, r) => '=IF(B' + r + '="","",CONCAT(A' + r + ',' + t.replace(/\x01/g, r) + '))';
  const montagem = fx[3].map(r => [180, R.moldePratica(formula(fx[1], r), r), [r]]).concat([[89, '=A\x01', [2, 3]]]);
  const dados = [];
  for (const g of P.dadosR53.filter(g => g[0] !== 180)) for (const r of [252, 253]) dados.push(['DADOS_R53', r, g[0], formula(g[1], r)]);
  dados.push(['DADOS_R53', 252, 180, '=velha'], ['FICHA AMALDIÇOADA', 563, 4, 'x']);
  const r = R.ajustarPratica(montagem, dados, P);
  ok(r.nMont === 251 && r.nDados === 14, 'contagem da Prática ' + r.nMont + '/' + r.nDados);
  const exp = new Map(); for (const [c, m, l] of r.montagem) for (const x of l) exp.set(x + ':' + c, m.replace(/\x01/g, x));
  ok(fx[3].every(x => exp.get(x + ':180') === formula(fx[2], x)) && exp.get('2:89') === '=A2', 'montagem nova');
  ok(r.dados.filter(v => v[1] >= 252 && v[2] !== 180 && v[0] === 'DADOS_R53').every(v => v[3] === formula(P.dadosR53.find(g => g[0] === v[2])[2], v[1])), 'dados 252–253');
  ok(r.dados.some(v => v[3] === '=velha'), 'a FX das linhas 252–253 nos dados fica (a montagem passa por cima)');
  const m2 = clone(montagem); m2[5][1] = m2[5][1].replace('sem dano', 'sem  dano');
  recusa(() => R.ajustarPratica(m2, dados, P), /trecho antigo encontrado 0/, 'FX divergente na Prática');
}

// ------------------------------------------------------------------------------------ 6. EditorR53 (sintético)
const editorSintetico = (contextos) => {
  const txt = JSON.stringify({ esquema: 3, contextos });
  return { txt, src: 'var R53_EDITOR_CACHE_=null;\nfunction r53ConfigEditor_(){if(R53_EDITOR_CACHE_)return R53_EDITOR_CACHE_;var text=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode("' +
    gz64(txt) + '"),"application/gzip")).getDataAsString("UTF-8");var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,text,Utilities.Charset.UTF_8).map(function(b){return ("0"+((b+256)%256).toString(16)).slice(-2);}).join("");if(hash!=="' +
    sha(txt) + '")throw Error("Editor: catálogo divergente");return R53_EDITOR_CACHE_=JSON.parse(text);}\n' };
};
{
  const ctxs = []; for (let i = 0; i < 251; i++) ctxs.push({ id: 'c' + i, formulas: { A1: '=' + i } });
  const p = clone(P); for (const i of Object.keys(p.editor)) p.editor[i].antes = sha(JSON.stringify(ctxs[i]));
  const e = editorSintetico(ctxs), r = R.prepararEditor(e.src, p, sha(e.txt));
  const c2 = vm.createContext({ Utilities: utilities() }); vm.runInContext(r.texto, c2);
  const cfg = c2.r53ConfigEditor_();
  ok(Object.keys(p.editor).every(i => JSON.stringify(cfg.contextos[i]) === JSON.stringify(p.editor[i].depois)), 'contextos novos');
  ok(cfg.contextos.every((g, i) => p.editor[i] || JSON.stringify(g) === JSON.stringify(ctxs[i])), 'contexto alheio mudou');
  ok(r.catalogo === sha(JSON.stringify(cfg)) && r.texto.indexOf(r.catalogo) > 0, 'hash do catálogo');
  const ruim = clone(ctxs); ruim[7].formulas.A1 = '=x';
  // um contexto fora da Máxima mudou: o catálogo não é o instalado (o hash esperado é o do catálogo bom)
  const er = editorSintetico(ruim); recusa(() => R.prepararEditor(er.src, p, sha(e.txt)), /catálogo diferente/, 'catálogo alheio');
  const ruim44 = clone(ctxs); ruim44[44].formulas.A1 = '=x';
  const e44 = editorSintetico(ruim44); recusa(() => R.prepararEditor(e44.src, p, sha(e44.txt)), /contexto 44 divergente/, 'contexto 44 antigo');
}

// ------------------------------------------------------------------------------------------- 7. pacote (Ficha.gs)
{
  const fonte = 'function gruposDeMescla_(merges) {\n  return [];\n}\nfunction montarAba_(aba, spec) {\n  var v=[],t=[1,1,1,0];\n  if (spec.grupos) {\n' +
    R.FICHA_PARES[1][0] + '\n  }\n  [t].forEach(function (t) {\n' + R.FICHA_PARES[2][0] + '\n    }\n  });\n}\n';
  const novo = R.prepararModulo(fonte);
  ok(novo.indexOf('function criarGrupos_(aba, lin, col)') > 0 && novo.indexOf('criarGrupos_(aba, spec.grupos.lin') > 0 &&
    novo.indexOf('spec.estilos && spec.estilos[t[3]]') > 0, 'consertos da PR #135');
  recusa(() => R.prepararModulo(novo), /já presente/, 'criarGrupos_ duas vezes');
  recusa(() => R.prepararModulo(fonte.replace(R.FICHA_PARES[2][0], '')), /conserto 3/, 'guarda do estilo ausente');
  recusa(() => R.prepararModulo(fonte + R.FICHA_PARES[1][0]), /conserto 2/, 'trecho dos grupos repetido');
  // o mesmo texto do repositório
  const ficha = fs.readFileSync(path.join(raiz, 'apps-script/Ficha.gs'), 'utf8');
  // o primeiro par leva o criarGrupos_ para antes do gruposDeMescla_ (no repositório ele vem depois; a função é a mesma)
  ok(R.FICHA_PARES.every(p => ficha.indexOf(p[1].split('\n\nfunction gruposDeMescla_')[0]) >= 0), 'conserto diferente do apps-script/Ficha.gs');
}

// ------------------------------------------------------------------------------------------ 8. pedidos da planilha
{
  const ids = { DADOS_R53: 1, DADOS_AM: 2, 'FICHA AMALDIÇOADA': 3, 'INVOCAÇÕES': 4 };
  const ida = R.pedidos(ids), volta = R.pedidosVolta(ids);
  const regex = ida.filter(l => l.esperado);
  ok(regex.every(l => l.esperado <= 40 && l.pedidos.length === 1), 'faixa da regex acima de 40 linhas');
  ok(regex.reduce((s, l) => s + l.esperado, 0) === 2008, 'células por regex');
  ok(regex.every(l => !/\\[1-9]|\(\?[<=!]/.test(l.pedidos[0].findReplace.find)), 'regex fora do RE2 (retrovisor ou lookaround)');
  ok(ida[0].pedidos.length === 26, 'células soltas da DADOS_R53');
  const cart = ida[ida.length - 1].pedidos;
  const tipos = {}; cart.forEach(q => { const k = Object.keys(q)[0]; tipos[k] = (tipos[k] || 0) + 1; });
  assert.deepEqual(tipos, { unmergeCells: 38, updateCells: 67 + 54, setDataValidation: 13, repeatCell: 39 + 5, mergeCells: 2, updateBorders: 45 }); n++;
  ok(cart.findIndex(q => q.unmergeCells) === 0 && cart.findIndex(q => q.mergeCells) > cart.findIndex(q => q.updateCells), 'ordem das mesclas');
  // simula o findReplace (o JS e o RE2 concordam nesta forma) sobre fórmulas com o trecho antigo
  const formula = (t, r) => '=IF(B' + r + '="","",X(A' + r + ',' + t.replace(/\x01/g, r) + ',Z' + r + '))';
  const aplicar = (lotes, de) => {
    for (const l of lotes.filter(l => l.esperado)) {
      const f = l.pedidos[0].findReplace, c = f.range.startColumnIndex + 1, re = new RegExp(f.find, 'g');
      let cont = 0;
      for (let r = f.range.startRowIndex + 1; r <= f.range.endRowIndex; r++) {
        const k = r + ':' + c; de.set(k, de.get(k).replace(re, (...m) => { cont++; return f.replacement.replace(/\$\$/g, '\0').replace(/\$1/g, m[1]).replace(/\0/g, '$'); }));
      }
      assert.equal(cont, l.esperado, 'contagem da regex ' + l.nome);
    }
  };
  const folha = new Map(), alvo = new Map();
  for (const [c, ta, tb, linhas] of P.dadosR53) for (const r of linhas) { folha.set(r + ':' + c, formula(ta, r)); alvo.set(r + ':' + c, formula(tb, r)); }
  const original = new Map(folha);
  aplicar(ida, folha);
  ok([...alvo].every(([k, v]) => folha.get(k) === v), 'regex não chega ao depois');
  aplicar(volta, folha);
  ok([...original].every(([k, v]) => folha.get(k) === v), 'volta não chega ao antes');
  // defeito: uma linha da FX já com outra versão não é trocada e a contagem acusa
  const torta = new Map(original); torta.set('100:180', torta.get('100:180').replace('sem dano', 'sem  dano'));
  recusa(() => aplicar(ida, torta), /contagem da regex DADOS_R53 FX82:FX121/, 'FX divergente não acusou');
  ok(R.pedidos(ids, { pontoEVirgula: true }).filter(l => l.esperado).every(l => R.pontoEVirgula(l.pedidos[0].findReplace.find) === l.pedidos[0].findReplace.find), 'variante com ponto e vírgula');
  {
    // pt_BR: a fórmula do updateCells também vai com ponto e vírgula (com vírgula a API deu "Formula parse error").
    const fora = f => f.split(/("(?:[^"]|"")*")/).filter((x, i) => i % 2 === 0).join('');
    const formulas = [].concat(...R.pedidos(ids, { pontoEVirgula: true }).map(l => l.pedidos))
      .filter(q => q.updateCells).map(q => q.updateCells.rows[0].values[0].userEnteredValue)
      .filter(v => v && v.formulaValue).map(v => v.formulaValue);
    ok(formulas.length > 40 && formulas.every(f => fora(f).indexOf(',') < 0), 'updateCells com ponto e vírgula: ' + formulas.length);
    const todas = [].concat(...P.celulas.map(c => [c[3], c[4]]), ...P.dadosR53.map(d => [d[1], d[2]]))
      .filter(f => typeof f === 'string');
    ok(todas.every(f => !/\d\.\d|[{}]/.test(fora(f))), 'sem decimal nem matriz literal fora das aspas');
  }
  recusa(() => R.pedidos({ DADOS_R53: 1 }), /sheetId ausente/, 'sheetId ausente');
  ok(R.faixasDaFoto().length === 8, 'faixas da foto: ' + R.faixasDaFoto().length);
}

// ------------------------------------------------------------------- 9. (opcional) a cadeia inteira no projeto real
let real = false;
if (process.env.R67_PROJETO) {
  const pasta = process.env.R67_PROJETO, arquivos = {};
  for (const nome of fs.readdirSync(pasta).filter(x => x.endsWith('.gs'))) arquivos[nome] = fs.readFileSync(path.join(pasta, nome), 'utf8');
  const analise = fs.readFileSync(path.join(raiz, 'apps-script/AnaliseEstatica.gs'), 'utf8');
  const r = R.prepararProjeto(arquivos, analise);
  const esperado = { 'Codigo.gs': 'd7031a736b37', 'EditorR53.gs': 'f23329f99dc3', 'AnaliseEstatica.gs': '4543892d3cd9',
    'Ficha.gs': '57d66d9cb7b5', 'Invocacoes.gs': '650d9336aba9', 'Analise.gs': '948bd0b51a61' };
  for (const [k, h] of Object.entries(esperado)) assert.equal(r.hashes[k].depois, h, 'hash de ' + k);
  ok(r.modulo.fonte.slice(0, 12) === 'ae0ed42b84da' && r.catalogo.depois.slice(0, 12) === 'eb35b245e9db', 'módulo/catálogo');
  const c = vm.createContext({ Utilities: utilities(), console });
  for (const t of Object.values(r.arquivos)) vm.runInContext(t, c);
  vm.runInContext('r53Modulo_()', c);
  ok(c.r53LivreValido_() === true, 'atalho desligado no projeto novo');
  recusa(() => R.prepararProjeto(r.arquivos, analise), /diferente do instalado/, 'segunda aplicação');
  const sem = Object.assign({}, arquivos); sem['Codigo.gs'] = sem['Codigo.gs'].replace(/var R53_LIVRE_HASHES_=\["([0-9a-f]{64})"/, 'var R53_LIVRE_HASHES_=["' + '0'.repeat(64) + '"');
  recusa(() => R.prepararProjeto(sem, analise, { conferir: false }), /atalho já desligado/, 'atalho [0] já desligado');
  const sem1 = Object.assign({}, arquivos); sem1['Codigo.gs'] = sem1['Codigo.gs'].replace(/("[0-9a-f]{64}")\];\n/, '"' + '1'.repeat(64) + '"];\n');
  recusa(() => R.prepararProjeto(sem1, analise, { conferir: false }), /atalho já desligado/, 'atalho [1] já desligado');
  const comT = Object.assign({}, arquivos); comT['Codigo.gs'] = comT['Codigo.gs'].replace('"FICHA AMALDIÇOADA":[', '"FICHA AMALDIÇOADA":[[357,20,357,20],');
  recusa(() => R.prepararProjeto(comT, analise, { conferir: false }), /T357 já no mapa/, 'T357 já no mapa');
  real = true;
}

console.log(JSON.stringify({ resultado: 'OK', verificacoes: n, planoRegerado: regerado, projetoReal: real }));
