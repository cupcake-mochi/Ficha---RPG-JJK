'use strict';
// Atalho das edições livres e módulo achatado (16/11/2026): o preparador religa só trocas conferidas, o achatador leva
// o atalho junto e recusa atalho já desligado; defeitos plantados acendem.
// node r53/testes/religar_atalho.js
const assert = require('assert'), zlib = require('zlib'), crypto = require('crypto'), vm = require('vm');
const R = require('../diagnostico-android/preparar_religar_atalho.js');
const A = require('../diagnostico-android/preparar_modulo_achatado.js');

const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const H = c => c.repeat(64);
const CATALOGO = H('c');
const VALIDO = 'function r53LivreValido_(){\n if(typeof r53Modulo_!==\'function\'||typeof r53ConfigEditor_!==\'function\')return false;\n' +
  ' return String(r53Modulo_).indexOf(R53_LIVRE_HASHES_[0])>=0&&String(r53ConfigEditor_).indexOf(R53_LIVRE_HASHES_[1])>=0;\n}\n';
const EDITOR = 'function r53ConfigEditor_(){if(hash!=="' + CATALOGO + '")throw Error("Editor: catálogo divergente");}\n';
const atalho = h0 => 'var R53_LIVRE_={"FICHA":[[1,1,2,2]]};\nvar R53_LIVRE_HASHES_=["' + h0 + '","' + CATALOGO + '"];\n' + VALIDO;

// Módulo instalado (forma do empacotador, com remendos) num Codigo com o atalho.
const ORIGINAL = "var ABAS=[{nome:'A'}],SOBRAS_=[];function f(){return 'velho';}\nreturn {f:f,__estado:function(){return {abas:ABAS,sobras:SOBRAS_};}};";
const REMENDO = "(function(){var m=[\"return 'velho';\",\"return 'novo';\"];if(code.split(m[0]).length!==2)throw Error('x');code=code.replace(m[0],function(){return m[1];});})();";
function instalado(original, h0) {
  const b64 = zlib.gzipSync(Buffer.from(original, 'utf8'), { level: 9 }).toString('base64'), meio = Math.ceil(b64.length / 2);
  const modulo = [A.ABRE, A.PRIMEIRA,
    " var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode([R53_CODIGO_0_,R53_CODIGO_1_].join('')), 'application/gzip')).getDataAsString('UTF-8');",
    " var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8).map(function(b){return ('0'+((b+256)%256).toString(16)).slice(-2);}).join('');",
    " if(hash!=='" + sha(original) + "')throw new Error('Pacote R53 incompleto: conteúdo divergente.');",
    REMENDO, A.INSTANCIA, ' return R53_MODULO_;', '}'].join('\n');
  return { codigo: '/** @OnlyCurrentDoc */\nvar R53_MODULO_;\n' + modulo + '\n' + atalho(h0 === undefined ? sha(original) : h0) + 'function outra(){return 1;}\n',
    arquivos: ['var R53_CODIGO_0_ = ' + JSON.stringify(b64.slice(0, meio)) + ';\n', 'var R53_CODIGO_1_ = ' + JSON.stringify(b64.slice(meio)) + ';\n', A.PARTE_VAZIA] };
}
/** O que o r53LivreValido_ responde para este Codigo (sem rodar o módulo). */
function ligado(codigo) {
  const c = { console }; vm.createContext(c); vm.runInContext(codigo + '\n' + EDITOR, c);
  return vm.runInContext('r53LivreValido_()', c);
}

let checks = 0;
const ok = (c, m) => { assert.ok(c, m); checks++; };
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const acende = (nome, fn, padrao) => { assert.throws(fn, padrao, nome + ' não acendeu'); checks++; console.log('ok: defeito plantado acende: ' + nome); };

// 1. Achatador leva o atalho ligado para o hash da fonte.
const base = instalado(ORIGINAL);
ok(ligado(base.codigo), 'atalho ligado no instalado');
const r = A.achatar(base.codigo, base.arquivos);
eq(r.atalho, sha(ORIGINAL).slice(0, 8) + ' -> ' + r.hashFinal.slice(0, 8));
ok(r.codigo.indexOf('var R53_LIVRE_HASHES_=["' + r.hashFinal + '","' + CATALOGO + '"];') >= 0, 'HASHES_[0] = fonte achatada');
ok(ligado(r.codigo), 'atalho continua ligado depois de achatar');
ok(r.codigo.indexOf('var R53_LIVRE_={"FICHA":[[1,1,2,2]]};') >= 0 && r.codigo.indexOf('function outra(){return 1;}') >= 0, 'o resto fica');
eq(R.hashDoModulo(r.codigo), r.hashFinal, 'o preparador lê a fonte achatada');
eq(R.religar(r.codigo, {}).mudou, false, 'achatado com atalho ligado: nada a religar');
console.log('ok: achatador leva o atalho junto (' + r.atalho + ')');

// 2. Achatador sem atalho no Codigo segue como antes.
const sem = instalado(ORIGINAL); sem.codigo = sem.codigo.replace(atalho(sha(ORIGINAL)), '');
eq(A.achatar(sem.codigo, sem.arquivos).atalho, 'sem atalho');

// 3. Preparador: religa troca conferida, nas duas formas do módulo; o trecho do console faz o mesmo e reverte.
const VELHO = H('9');
const desligadoAchatado = r.codigo.replace('["' + r.hashFinal + '"', '["' + VELHO + '"');
ok(!ligado(desligadoAchatado), 'plantado: achatado com hash velho fica desligado (o caso da rodada de 16/11)');
const ver = {}; ver[VELHO] = [r.hashFinal, sha(ORIGINAL)];
const rel = R.religar(desligadoAchatado, ver);
ok(rel.mudou && rel.antes === VELHO && rel.depois === r.hashFinal, 'religado no achatado');
eq(rel.codigo, r.codigo, 'só a linha do hash muda');
ok(ligado(rel.codigo), 'religado: r53LivreValido_ = true');
const desligadoInstalado = base.codigo.replace('["' + sha(ORIGINAL) + '"', '["' + VELHO + '"');
const rel2 = R.religar(desligadoInstalado, ver);
eq(rel2.codigo, base.codigo, 'religado no não achatado');
ok(ligado(rel2.codigo), 'religado no não achatado: ligado');
console.log('ok: preparador religa troca conferida, achatado ou não');

(async () => {
  const modelos = [{ v: desligadoAchatado }, { v: 'var R53_CODIGO_0_ = "x";\n' }].map(m => Object.assign(m, { getValue() { return this.v; }, setValue(x) { this.v = x; } }));
  global.monaco = { editor: { getModels: () => modelos } }; global.window = {};
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  const rodar = t => new AsyncFunction('return ' + t.replace(/^await /, ''))();
  const trechoCom = v => R.trecho().replace(JSON.stringify(R.VERIFICADAS), JSON.stringify(v));
  ok(/^ERRO: Troca 99999999 -> /.test(await rodar(R.trecho())), 'trecho com a lista real recusa troca não conferida');
  eq(modelos[0].v, desligadoAchatado, 'recusado, nada muda');
  const saida = JSON.parse(await rodar(trechoCom(ver)));
  eq(saida.atalho, '99999999 -> ' + r.hashFinal.slice(0, 8));
  eq(modelos[0].v, r.codigo, 'trecho grava o Codigo religado');
  eq(JSON.parse(await rodar(trechoCom(ver))).atalho, 'já ligado', 'segunda passada não muda nada');
  eq(window.__religarReverter(), 'revertido; salvar o projeto');
  eq(modelos[0].v, desligadoAchatado, 'reverter volta o texto de antes');
  console.log('ok: trecho do console religa, reconhece já ligado e reverte');

  // 4. Lista real: as trocas da rodada de 16/11 (9dc3480a -> bd42b535 e -> 35d00ae2) e nenhuma outra.
  eq(Object.keys(R.VERIFICADAS), ['9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc']);
  eq(R.VERIFICADAS['9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc'].map(h => h.slice(0, 8)), ['bd42b535', '35d00ae2']);
  const real = r.codigo.replace('["' + r.hashFinal + '"', '["9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc"')
    .replace('; fonte ' + r.hashFinal + '.', '; fonte 35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10.');
  const rr = R.religar(real);
  ok(rr.mudou && rr.depois === '35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10' && ligado(rr.codigo), 'a troca da rodada religa');

  // 5. Defeitos plantados.
  acende('achatador sobre Codigo com atalho já desligado', () => A.achatar(desligadoInstalado, base.arquivos), /já desligado \(99999999 em vez de/);
  const mods = base.arquivos.concat([desligadoInstalado]).map(t => ({ v: t, getValue() { return this.v; }, setValue(x) { this.v = x; } }));
  global.monaco = { editor: { getModels: () => mods } };
  const doTrecho = await rodar(A.trecho());
  ok(/^ERRO: Atalho das edições livres já desligado \(99999999/.test(doTrecho), 'trecho do achatador recusa atalho desligado: ' + doTrecho);
  ok(mods.every((m, i) => m.v === base.arquivos.concat([desligadoInstalado])[i]), 'recusado, nada gravado');
  console.log('ok: defeito plantado acende: trecho do achatador sobre atalho já desligado');
  const mods2 = base.arquivos.concat([base.codigo]).map(t => ({ v: t, getValue() { return this.v; }, setValue(x) { this.v = x; } }));
  global.monaco = { editor: { getModels: () => mods2 } };
  const info = JSON.parse(await rodar(A.trecho()));
  eq(info.atalho, r.atalho, 'trecho do achatador leva o atalho igual ao node');
  ok(ligado(mods2[mods2.length - 1].v) && mods2[mods2.length - 1].v.indexOf('["' + r.hashFinal + '"') >= 0, 'trecho do achatador: atalho ligado');
  acende('troca não conferida', () => R.religar(desligadoAchatado), /não conferida/);
  acende('atalho duplicado', () => R.religar(desligadoAchatado + atalho(VELHO), ver), /ausente ou duplicado/);
  acende('Codigo sem atalho', () => R.religar(sem.codigo, ver), /ausente ou duplicado/);
  acende('r53LivreValido_ com outra conta', () => R.religar(desligadoAchatado.replace('indexOf(R53_LIVRE_HASHES_[0])>=0', 'indexOf(R53_LIVRE_HASHES_[1])>=0'), ver), /r53LivreValido_ divergente/);
  acende('módulo com as duas marcas de hash', () => R.religar(desligadoAchatado.replace(A.MARCA, " if(hash!=='" + H('1') + "')throw new Error('Pacote R53 incompleto: x');\n" + A.MARCA), ver), /ambíguo/);
  acende('dois r53Modulo_', () => R.religar(desligadoAchatado + '\n' + A.ABRE + '\n}\n', ver), /2 vez/);
  acende('achatador com R53_LIVRE_HASHES_ fora da forma', () => {
    const x = instalado(ORIGINAL); x.codigo = x.codigo.replace('","' + CATALOGO + '"];', '","' + CATALOGO + '"] ;'); A.achatar(x.codigo, x.arquivos);
  }, /forma inesperada/);
  console.log('religar_atalho: tudo certo (' + checks + ' verificações)');
})().catch(e => { console.error(e); process.exit(1); });
