'use strict';
// DADOS_CUSTOM sem INDIRECT: o conversor das planilhas montadas leva a forma antiga exatamente à forma do gerador.
// node r53/testes/custom_sem_indirect.js
const assert = require('assert'), fs = require('fs'), path = require('path');
const C = require('../diagnostico-android/preparar_custom_sem_indirect.js');
const root = path.resolve(__dirname, '../..');

/** Inverso exato do conversor: CHOOSE(IFERROR(MATCH(...))) volta a INDIRECT(SWITCH(...)) com as faixas entre aspas. */
function antigo(f) {
  return f.replace(/CHOOSE\(IFERROR\(MATCH\(([^(),]+),\{([^{}]*)\},0\),(\d+)\),([^()]*)\)/g, (todo, sel, chaves, n, faixas) => {
    const k = chaves.split(';'), r = faixas.split(',');
    assert.strictEqual(Number(n), k.length + 1); assert.strictEqual(r.length, k.length + 1);
    return 'INDIRECT(SWITCH(' + sel + ',' + k.map((x, i) => x + ',"' + r[i] + '"').join(',') + ',"' + r[k.length] + '"))';
  });
}

const formulas = [];
for (const nome of C.FONTES) {
  const t = fs.readFileSync(path.join(root, 'apps-script', nome), 'utf8');
  for (const s of t.match(/"(?:[^"\\]|\\.)*"/g)) { const f = JSON.parse(s); if (f.indexOf('CHOOSE(IFERROR(MATCH(') >= 0) formulas.push(f); }
}
assert.strictEqual(formulas.length, 225, 'fórmulas com a escolha de faixa');
const reqs = C.pedidos(1439829572);
let trocas = 0;
for (const novo of formulas) {
  const velho = antigo(novo);
  assert.strictEqual((velho.match(/INDIRECT\(/g) || []).length, (novo.match(/CHOOSE\(IFERROR/g) || []).length);
  trocas += (velho.match(/INDIRECT\(/g) || []).length;
  assert.strictEqual(C.converterIngles(velho), novo, 'conversor das fontes');
  assert.strictEqual(C.aplicarPedidos(C.paraPtBr(velho), reqs), C.paraPtBr(novo), 'pedidos da planilha montada');
  (novo.match(/MATCH\([^,]+,\{([^{}]*)\}/g) || []).forEach(m => assert.deepStrictEqual(m.replace(/^[^{]*\{|\}$/g, '').split(';'), C.CHAVES.map(k => '"' + k + '"')));
}
assert.strictEqual(trocas, 525);
console.log('ok: 225 fórmulas, 525 INDIRECT: conversor das fontes e pedidos da planilha dão a forma do gerador');

// Os pedidos: um batchUpdate, os dois na DADOS_CUSTOM DF2:JZ26, com fórmulas.
assert.strictEqual(reqs.length, 2);
reqs.forEach(r => { assert.deepStrictEqual(r.findReplace.range, { sheetId: 1439829572, startRowIndex: 1, endRowIndex: 26, startColumnIndex: 109, endColumnIndex: 286 }); assert.strictEqual(r.findReplace.includeFormulas, true); });

let acesos = 0;
function acende(nome, ok) { assert.ok(ok, nome + ' não acendeu'); acesos++; console.log('ok: defeito plantado acende: ' + nome); }
const amostra = C.paraPtBr(antigo(formulas[0]));
acende('planilha com as chaves noutra ordem fica com INDIRECT (a contagem da resposta denuncia)',
  /INDIRECT\(/.test(C.aplicarPedidos(amostra.replace('"Menor";', '"MENOR_X";'), reqs)));
acende('só o segundo pedido, sem tirar as aspas, não converte nada',
  C.aplicarPedidos(amostra, [reqs[1]]) === amostra);
acende('padrão do SWITCH perdido muda o resultado',
  C.aplicarPedidos(amostra, reqs) !== C.aplicarPedidos(amostra.replace(/;"('DADOS_[A-Z]+'![^"]+)"\)\)/, ')))'), reqs));
let lancou = false; try { C.converterIngles('=INDIRECT(SWITCH(A1,"Origem","texto solto","x"))'); } catch (e) { lancou = /não é faixa/.test(e.message); }
acende('conversor das fontes recusa SWITCH que não é de faixas', lancou);
lancou = false; try { C.reescreverCustomGs('var X = ["=INDIRECT(\\"A1\\")"];'); } catch (e) { lancou = /Sobrou INDIRECT/.test(e.message); }
acende('INDIRECT fora do molde não passa calado', lancou);
assert.strictEqual(acesos, 5);
console.log('custom_sem_indirect: tudo certo (' + acesos + ' defeitos plantados acesos)');
