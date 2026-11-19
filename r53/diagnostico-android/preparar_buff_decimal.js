'use strict';
// Buff/Debuff decimal contra o dono (10/11/2026): a mesma leitura (ficha-v01/leitura_buff.py) nos
// 11 Buff/Debuff da FICHA e nos 14 de cada uma das 12 entidades. Só troca o leitor; nenhuma outra
// parte das fórmulas muda. O delta é gerado comparando as fontes GS de antes e de depois.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/buff_decimal_delta.json';
const NUMERO_TEXTUAL = '^[+-]?[0-9]+([.,][0-9]+)?$';

function leitor(x) {
  const inteiro = `VALUE(REGEXEXTRACT(${x},"[0-9]+"))`;
  const quebrado = `N(REGEXMATCH(${x},"[.,][0-9]*[1-9]"))`;
  const texto = `IF(REGEXMATCH(${x},"${NUMERO_TEXTUAL}"),IF(LEFT(${x},1)="-",-${inteiro}-${quebrado},MAX(${inteiro},${quebrado})),0)`;
  const numero = `IF(N(${x})>0,MAX(1,INT(N(${x}))),INT(N(${x})))`;
  return `IFERROR(IF(ISTEXT(${x}),${texto},${numero}),0)`;
}
const leitorAntigo = x => `IFERROR(VALUE(${x}&""),0)`;
const entidadeAntiga = x => `=IF(ISTEXT(${x}),IF(REGEXMATCH(${x},"^[+-]?[0-9]+$"),VALUE(SUBSTITUTE(${x},"+","")),0),N(${x}))`;
const escapa = s => s.replace(/[$.*+?^()[\]{}|\\]/g, '\\$&');

// Os Buff/Debuff do jogador, pelo rótulo da caixa (conferidos na FICHA em 10/11/2026).
const BUFFS_FICHA = ['L59', 'W59', 'AS59', 'L63', 'W63', 'AS63', 'AH63', 'P26', 'P30', 'P34', 'W67'];
const refsFicha = a1 => {
  const [, c, r] = /^([A-Z]+)(\d+)$/.exec(a1);
  return [`$${c}$${r}`, `'FICHA'!$${c}$${r}`, `FICHA!$${c}$${r}`];
};

// Depois = antes com cada leitor antigo de um Buff/Debuff trocado pelo novo, e nada além disso.
function explicar(antes) {
  if (typeof antes !== 'string') return null;
  const m = /^=IF\(ISTEXT\(([^()]+)\),IF\(REGEXMATCH/.exec(antes);
  if (m && antes === entidadeAntiga(m[1])) return '=' + leitor(m[1]);
  let t = antes;
  for (const a1 of BUFFS_FICHA) for (const ref of refsFicha(a1)) {
    t = t.replace(new RegExp(escapa(leitorAntigo(ref)), 'g'), leitor(ref));
  }
  return t === antes ? null : t;
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
      assert.equal(explicar(o.get(pos)), d.get(pos), 'Mudança fora do leitor: ' + a.nome + ' ' + pos);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve o modelo ao leitor antigo antes das camadas anteriores
// (Reserva/Bolsa, Origens…). Atômico: confere tudo numa cópia e só então grava.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const porAba = new Map();
  for (const d of delta) {
    if (!porAba.has(d.aba)) porAba.set(d.aba, []);
    porAba.get(d.aba).push(d);
  }
  const trocas = [];
  for (const [nome, lista] of porAba) {
    const aba = abas.find(a => a.nome === nome);
    if (!aba) throw Error('Buff decimal: aba ausente ' + nome);
    const antes = expandir(aba);
    for (const d of lista) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Buff decimal divergente: ' + nome + '!' + d.r + ',' + d.c);
    const copia = structuredClone(aba);
    for (const v of copia.vals) {
      const d = lista.find(d => d.r === v[0] && d.c === v[1]);
      if (d) v[2] = d.antes;
    }
    const depois = expandir(copia);
    const alvo = new Map(lista.map(d => [d.r + ':' + d.c, d.antes]));
    for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
      const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
      if (depois.get(pos) !== esperado) throw Error('Buff decimal: reversão fora do molde em ' + nome + '!' + pos);
    }
    trocas.push([aba, copia.vals]);
  }
  for (const [aba, vals] of trocas) aba.vals = vals;
  return abas;
}

// Instalação nas QAs: snapshot = { locale, sheetIds: {aba: id}, cells: [{aba, r, c, value}] }.
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
  const porAba = {};
  for (const d of r.delta) porAba[d.aba] = (porAba[d.aba] || 0) + 1;
  console.log(JSON.stringify({ abas: r.abas, posicoes: r.posicoes, formulas: r.delta.length, porAba }));
}

module.exports = { leitor, explicar, comparar, reverterModelo, pedidos, BUFFS_FICHA };
