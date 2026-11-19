'use strict';
// Ponto fora de 0 a 6 na FICHA do jogador (10/11/2026). As caixas de pontos (D21, L21, T21, AB21, AJ21) e as
// do Corpo (AK15:AS15) não têm menu: negativo, fração, 7 e "1/2" (que vira data) passavam sem aviso.
// O resumo dos pontos (Z15) e o do Corpo (AK14) passam a acusar, sem reescrever a entrada. Texto que não é
// número continua valendo 0, em silêncio, como nas entidades (PR94). O teto do jogador segue a campanha
// (DADOS_CONFIG!$S$5); o do Corpo fica em 6. Só essas duas fórmulas mudam.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/pontos_ficha_delta.json';
const TETO = 'DADOS_CONFIG!$S$5';
const N = a1 => `IFERROR(VALUE($${a1.replace(/(\d+)$/, '$$$1')}&""),0)`;
const fora = (caixas, teto) => 'OR(' + caixas.map(N).map(x => `${x}<0,${x}>${teto},${x}<>INT(${x})`).join(',') + ')';
const PONTOS = ['D21', 'L21', 'T21', 'AB21', 'AJ21'];
const CORPO = ['AK15', 'AM15', 'AO15', 'AQ15', 'AS15'];
const ALVOS = { '15:26': 'Z15', '14:37': 'AK14' };
const ROTULO_CORPO = '="Pontos de Marco de Corpo Disponíveis - "&';

// Depois = antes com o aviso na frente; nada mais muda.
function explicar(pos, antes) {
  if (typeof antes !== 'string') return null;
  if (pos === '15:26' && antes.startsWith('=IF(DADOS!$AK$7>DADOS!$AK$6,')) {
    return `=IF(${fora(PONTOS, TETO)},"Ponto fora de 0 a "&${TETO},${antes.slice(1)})`;
  }
  if (pos === '14:37' && antes.startsWith(ROTULO_CORPO)) {
    return `${ROTULO_CORPO}IF(${fora(CORPO, 6)},"Ponto fora de 0 a 6",${antes.slice(ROTULO_CORPO.length)})`;
  }
  return null;
}

function comparar(base, atual) {
  assert.deepEqual(atual.map(a => a.nome), base.map(a => a.nome), 'Abas divergentes');
  const delta = [];
  let posicoes = 0;
  for (const [i, a] of base.entries()) {
    const b = atual[i];
    const estrutura = ({ vals, abaixo, geracao, notas, ...resto }) => resto;
    assert.deepEqual(estrutura(b), estrutura(a), 'Estrutura ' + a.nome);
    assert.deepEqual(b.notas || [], a.notas || [], 'Notas ' + a.nome);
    const o = expandir(a), d = expandir(b);
    for (const pos of new Set([...o.keys(), ...d.keys()])) {
      posicoes++;
      if (o.get(pos) === d.get(pos)) continue;
      assert.equal(a.nome, 'FICHA', 'Mudança fora da FICHA: ' + a.nome + ' ' + pos);
      assert.ok(ALVOS[pos], 'Mudança fora de Z15/AK14: ' + pos);
      assert.equal(explicar(pos, o.get(pos)), d.get(pos), 'Mudança fora do aviso em ' + ALVOS[pos]);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  assert.equal(delta.length, 2, 'Esperadas duas fórmulas');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve Z15 e AK14 ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const aba = abas.find(a => a.nome === 'FICHA');
  if (!aba) throw Error('Pontos da ficha: aba FICHA ausente');
  const antes = expandir(aba);
  for (const d of delta) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Pontos da ficha divergentes: FICHA!' + d.r + ',' + d.c);
  const copia = structuredClone(aba);
  for (const v of copia.vals) {
    const d = delta.find(d => d.r === v[0] && d.c === v[1]);
    if (d) v[2] = d.antes;
  }
  const depois = expandir(copia);
  const alvo = new Map(delta.map(d => [d.r + ':' + d.c, d.antes]));
  for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
    const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
    if (depois.get(pos) !== esperado) throw Error('Pontos da ficha: reversão fora do molde em FICHA!' + pos);
  }
  aba.vals = copia.vals;
  return abas;
}

// Instalação nas QAs: snapshot = { locale, sheetIds: {FICHA: id}, cells: [{aba, r, c, value}] } na ordem do delta.
function pedidos(delta, snapshot, reverter = false) {
  assert.ok(['pt_BR', 'en_US'].includes(snapshot.locale), 'Localidade não ensaiada');
  assert.equal(snapshot.cells.length, delta.length, 'Quantidade de alterações divergente');
  const cells = snapshot.cells.map(c => ({ ...c, sheetId: snapshot.sheetIds[c.aba] }));
  return planejarCelulas({ locale: snapshot.locale, cells }, reverter, delta).requests;
}

if (require.main === module) {
  const [base, atual] = process.argv.slice(2);
  if (!base || !atual) throw Error('Informe os dois diretórios de fontes GS');
  const r = comparar(ler(base), ler(atual));
  fs.writeFileSync(CAMINHO, JSON.stringify(r.delta, null, 2) + '\n');
  console.log(JSON.stringify({ abas: r.abas, posicoes: r.posicoes, formulas: r.delta.length }));
}

module.exports = { explicar, comparar, reverterModelo, pedidos, fora, PONTOS, CORPO, TETO };
