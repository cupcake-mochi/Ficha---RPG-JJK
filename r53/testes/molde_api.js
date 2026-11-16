'use strict';
// preparar_molde_api.js: plano, ajuste no modelo, recusas e (opcional) o Codigo real das QAs com o módulo.
//   node r53/testes/molde_api.js                                   (portátil, no smoke)
//   node r53/testes/molde_api.js <Codigo-110.gs> <pasta das partes> (privado: Codigo 4f660022 e partes do módulo bd42b535)
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const z = require('node:zlib'), crypto = require('node:crypto');
const p = require('../diagnostico-android/preparar_molde_api');
const { converterIngles } = require('../diagnostico-android/preparar_custom_sem_indirect');
const { ler } = require('./expansao_domada_modelo');
const D = path.join(__dirname, '../diagnostico-android');
let n = 0; const t = f => { f(); n++; };

const plano = p.plano();
t(() => assert.equal(p.conferirPlano(plano), 593));

// 1. O "depois" é o que o gerador atual escreve.
const gerado = ler(path.join(__dirname, '../../apps-script'));
for (const [aba, r, c, , depois] of plano) {
  const v = gerado.find(a => a.nome === aba).vals.filter(v => v[0] === r && v[1] === c);
  assert.equal(v.length, 1, aba + ' ' + r + ',' + c);
  assert.equal(v[0][2], depois, 'Gerador diverge em ' + aba + ' ' + r + ',' + c);
}
n++;

// 2. O plano é a cadeia composta dos deltas (primeiro antes, último depois) e o #119 aplicado nas 225 da DADOS_CUSTOM.
const ordem = ['buff_decimal', 'pontos_ficha', 'aviso_atributo', 'menu_oficios', 'especializacao', 'texto_extra', 'corte_xp_missao'];
const cadeia = new Map();
for (const f of ordem) for (const x of JSON.parse(fs.readFileSync(path.join(D, f + '_delta.json'), 'utf8'))) {
  if (x.addr || !['FICHA', 'FICHA PESSOAL', 'DADOS_CONFIG'].includes(x.aba)) continue;
  if (typeof x.antes !== 'string' || x.antes[0] !== '=') continue; // valores de menu: o restaurador só devolve fórmula
  const k = x.aba + '!' + (+x.r) + ':' + (+x.c), prev = cadeia.get(k);
  if (prev) { assert.equal(x.antes, prev[1], 'Cadeia quebrada em ' + k); prev[1] = x.depois; } else cadeia.set(k, [x.antes, x.depois]);
}
let indiretos = 0;
for (const [aba, r, c, antes, depois] of plano) {
  if (aba === 'DADOS_CUSTOM') {
    assert.ok(antes.includes('INDIRECT(SWITCH('));
    assert.equal(depois, converterIngles(antes));
    assert.ok(!depois.includes('INDIRECT('));
    indiretos += antes.split('INDIRECT(').length - 1;
  } else assert.deepEqual([antes, depois], cadeia.get(aba + '!' + r + ':' + c), aba + ' ' + r + ',' + c);
}
t(() => assert.equal(cadeia.size, 593 - 225));
t(() => assert.equal(indiretos, 525));

// 3. O ajuste no modelo: aplica, repete sem mudar, e recusa sem tocar em nada.
const utilities = { base64Decode: s => Buffer.from(s, 'base64'), newBlob: x => x,
  ungzip: x => ({ getDataAsString: () => z.gunzipSync(x).toString() }),
  computeDigest: (_, s) => Array.from(crypto.createHash('sha256').update(s).digest()), DigestAlgorithm: { SHA_256: 1 }, Charset: { UTF_8: 1 } };
const c = vm.createContext({ Utilities: utilities });
vm.runInContext(p.runtime(), c);
const fixture = () => ['FICHA', 'FICHA PESSOAL', 'DADOS_CONFIG', 'DADOS_CUSTOM', 'DADOS_INVOC'].map(nome => ({
  nome, vals: plano.filter(d => d[0] === nome).map(d => [d[1], d[2], d[3], 7]).concat([[1, 1, '=1+1', 7], [999, 1, 'texto', 7]]) }));
const abas = fixture();
c.r53AjustarMoldeApi_(abas);
for (const [aba, r, col, , depois] of plano) assert.equal(abas.find(a => a.nome === aba).vals.find(v => v[0] === r && v[1] === col)[2], depois);
t(() => assert.deepEqual(abas.map(a => a.vals.slice(-2)), fixture().map(a => a.vals.slice(-2)), 'Vizinhos intactos'));
const uma = JSON.stringify(abas); c.r53AjustarMoldeApi_(abas);
t(() => assert.equal(JSON.stringify(abas), uma, 'Segunda passada não muda nada'));
for (const estraga of [
  a => { a[0].vals[0][2] = '=outra()'; },                 // fórmula nem antiga nem nova
  a => { a[1].vals.push(a[1].vals[3].slice()); },          // alvo duplicado
  a => { a.splice(2, 1); },                                // aba ausente
  a => { a.push({ nome: 'DADOS_CUSTOM', vals: [] }); },    // aba duplicada
  a => { a[3].vals.splice(10, 1); },                       // alvo ausente
]) {
  const ruim = fixture(); estraga(ruim);
  const antes = JSON.stringify(ruim);
  assert.throws(() => c.r53AjustarMoldeApi_(ruim), /Molde API/);
  assert.equal(JSON.stringify(ruim), antes, 'Recusa atômica');
  n++;
}

// 4. Defeitos plantados no plano e na preparação do Codigo.
for (const estraga of [
  q => q.pop(), q => q.push(q[0].slice()), q => { q[0][4] = q[0][3]; }, q => { q[5][3] = 'texto'; }, q => { q[7][0] = 'FICHA AMALDIÇOADA'; },
]) { const q = structuredClone(plano); estraga(q); assert.throws(() => p.conferirPlano(q), /Molde API/); n++; }
t(() => assert.throws(() => p.prepararCodigo('function onEdit(e){}'), /ensaiado/));
t(() => assert.throws(() => p.prepararCodigo('function r53AjustarMoldeApi_(abas){}'), /já presente/));
t(() => assert.ok(p.runtime().length < 80000, 'Dados compactados no Codigo'));

// 5. Privado: o Codigo real das QAs (#110) com o módulo, e o achatador por cima.
if (process.argv[2]) {
  const src = fs.readFileSync(process.argv[2], 'utf8'), pasta = process.argv[3];
  t(() => assert.equal(p.sha(src), p.BASE));
  const out = p.prepararCodigo(src);
  t(() => assert.throws(() => p.prepararCodigo(out), /já presente/));
  const nomes = fs.readdirSync(pasta).filter(f => /^(modulo|qa-era)-(Ficha|Invocacoes|Analise|Configuracao|Origens)\.gs$/.test(f));
  assert.equal(nomes.length, 5, 'Esperadas as cinco partes do módulo');
  const partes = nomes.map(f => fs.readFileSync(path.join(pasta, f), 'utf8'));
  const carregar = (codigo, arquivos) => {
    const k = vm.createContext({ Utilities: utilities, console });
    vm.runInContext(codigo, k); arquivos.forEach(a => vm.runInContext(a, k));
    return k.r53Modulo_().__estado();
  };
  const conferir = s => {
    assert.equal(s.sobras.length, 0);
    for (const [aba, r, col, , depois] of plano) {
      const v = s.abas.find(a => a.nome === aba).vals.filter(v => v[0] === r && v[1] === col);
      assert.equal(v.length, 1); assert.equal(v[0][2], depois, aba + ' ' + r + ',' + col);
    }
  };
  const sem = carregar(src, partes);
  t(() => assert.ok(plano.every(([aba, r, col, antes]) => sem.abas.find(a => a.nome === aba).vals.find(v => v[0] === r && v[1] === col)[2] === antes),
    'Sem o ajuste, o modelo instalado tem as 593 antigas'));
  t(() => conferir(carregar(out, partes)));
  const { achatar } = require('../diagnostico-android/preparar_modulo_achatado');
  const ach = achatar(out, partes);
  const arquivos = partes.map((a, i) => ach.arquivos[i] !== undefined ? ach.arquivos[i] : a);
  t(() => conferir(carregar(ach.codigo, arquivos)));
  t(() => assert.ok(ach.codigo.includes('r53AjustarMoldeApi_(R53_MODULO_.__estado().abas)'), 'O achatador conserva o ajuste'));
}

console.log(JSON.stringify({ resultado: 'OK', verificacoes: n, alvos: plano.length, privado: !!process.argv[2] }));
