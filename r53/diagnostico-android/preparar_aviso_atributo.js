'use strict';
// Menu de atributo sem #N/A na FICHA do jogador (10/11/2026). Os menus da técnica (Z67), do corpo a corpo (AK67) e da
// distância (AE70) não são estritos, e o IFS das contas não tem caso padrão: vazio ou "FORCA" sem cedilha quebrava a
// CD, a Conjuração e os ataques com #N/A, que saía também na ANALISE. A caixa passa a dizer "Escolha o atributo", sem
// reescrever o menu. Com valor fixo da campanha (DADOS_CONFIG coluna C = 1) o menu não conta e o aviso não aparece.
// Só essas quatro fórmulas mudam. O gerador é ficha-v01/configuracao.py (avisa_menu).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/aviso_atributo_delta.json';
const ATRIBUTOS = ['FORÇA', 'DESTREZA', 'CONSTITUIÇÃO', 'INTELIGÊNCIA', 'ESSÊNCIA'];
const AVISO = 'Escolha o atributo';
// posição → [menu, linha da DADOS_CONFIG]
const ALVOS = { '63:4': ['Z67', 8], '63:15': ['Z67', 9], '63:26': ['AK67', 10], '63:37': ['AE70', 11] };
const invalido = (menu, linha) => `AND(DADOS_CONFIG!$C$${linha}<>1,NOT(OR(${ATRIBUTOS.map(a => `${menu}="${a}"`).join(',')})))`;

// Depois = antes com o aviso por fora; nada mais muda.
function explicar(pos, antes) {
  const alvo = ALVOS[pos];
  if (!alvo || typeof antes !== 'string') return null;
  const [menu, linha] = alvo;
  if (!antes.startsWith(`=IF(DADOS_CONFIG!$E$${linha}<>"",NA(),`) || !antes.includes(`IFS(${menu}="FORÇA",`)) return null;
  return `=IF(${invalido(menu, linha)},"${AVISO}",${antes.slice(1)})`;
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
      assert.ok(ALVOS[pos], 'Mudança fora das quatro caixas: ' + pos);
      assert.equal(explicar(pos, o.get(pos)), d.get(pos), 'Mudança fora do aviso em ' + pos);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  assert.equal(delta.length, 4, 'Esperadas quatro fórmulas');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve as quatro caixas ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const aba = abas.find(a => a.nome === 'FICHA');
  if (!aba) throw Error('Aviso de atributo: aba FICHA ausente');
  const antes = expandir(aba);
  for (const d of delta) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Aviso de atributo divergentes: FICHA!' + d.r + ',' + d.c);
  const copia = structuredClone(aba);
  for (const v of copia.vals) {
    const d = delta.find(d => d.r === v[0] && d.c === v[1]);
    if (d) v[2] = d.antes;
  }
  const depois = expandir(copia);
  const alvo = new Map(delta.map(d => [d.r + ':' + d.c, d.antes]));
  for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
    const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
    if (depois.get(pos) !== esperado) throw Error('Aviso de atributo: reversão fora do molde em FICHA!' + pos);
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

module.exports = { explicar, comparar, reverterModelo, pedidos, invalido, ALVOS, ATRIBUTOS, AVISO };
