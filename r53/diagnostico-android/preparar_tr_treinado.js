'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler } = require('../testes/expansao_domada_modelo');
const { comparar } = require('./preparar_pericias_entidades');
const { coordenadas, planejarCelulas } = require('./preparar_pilha_5156');

// Título das 12 entidades (d_titulo): pede a escolha do TR treinado quando ele não é um dos quatro testes.
const letra = c => (c > 26 ? String.fromCharCode(64 + Math.floor((c - 1) / 26)) : '') + String.fromCharCode(65 + ((c - 1) % 26));
const colunas = [215];
const valores = new Map();
for (let r = 2; r <= 13; r++) {
  for (const c of colunas) valores.set(r + ':' + c, letra(c) + r);
}

function pedidos(delta, snapshot, reverter = false) {
  assert.ok(['pt_BR', 'en_US'].includes(snapshot.locale), 'Localidade não ensaiada');
  assert.equal(delta.length, valores.size, 'Quantidade de alterações divergente');
  assert.deepEqual(new Set(delta.map(d => d.r + ':' + d.c)), new Set(valores.keys()), 'Alvos divergentes');
  const cells = delta.map(d => {
    assert.equal(d.aba, 'DADOS_INVOC', 'Aba fora do plano');
    const key = d.aba + '!' + valores.get(d.r + ':' + d.c);
    const value = snapshot.cells[key]?.userEnteredValue?.formulaValue;
    assert.equal(typeof value, 'string', 'Fórmula ausente: ' + key);
    return { aba: d.aba, r: d.r, c: d.c, sheetId: snapshot.sheetIds[d.aba], value };
  });
  return planejarCelulas({ locale: snapshot.locale, cells }, reverter, delta).requests;
}

if (require.main === module) {
  const [base, atual, saida] = process.argv.slice(2);
  if (!base || !atual || !saida) throw Error('Informe os dois diretórios de fontes GS e o arquivo de saída');
  const resultado = comparar(ler(base), ler(atual), { valores, notas: [] });
  const delta = resultado.delta.map(d => ({
    aba: d.aba, ...coordenadas({ addr: d.a1 }), antes: d.antes, depois: d.depois,
  }));
  fs.writeFileSync(saida, JSON.stringify(delta, null, 2) + '\n');
  console.log(JSON.stringify({ abas: resultado.abas, posicoes: resultado.posicoes, formulas: delta.length }));
}

module.exports = { valores, pedidos };
