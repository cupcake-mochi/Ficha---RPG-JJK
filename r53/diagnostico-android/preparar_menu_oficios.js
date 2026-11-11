'use strict';
// Ofícios e TR Físico da FICHA do jogador (11/11/2026). Dois consertos da mesma faixa (linhas 108 a 113):
// 1. Os menus de atributo dos onze ofícios (K108:K113, X108:X112) e o do TR Físico (AK108) não são estritos, e o IFS
//    das contas não tem caso padrão: vazio ou "FORCA" sem cedilha virava #N/A. A caixa passa a dizer "Escolha o
//    atributo", como a CD e os ataques desde a PR100. O TR Físico aceita só FORÇA e DESTREZA, como o menu dele.
// 2. Os menus dos ofícios nasciam todos em INTELIGÊNCIA. Passam ao atributo padrão da tabela de Ofícios do livro
//    (R66, capítulo 7): só os oito que não são Inteligência mudam.
// Geradores: ficha-v01/configuracao.py (avisa_menu) e ficha-v01/ficha_automatica.py (padrão dos ofícios).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { ler, expandir } = require('../testes/expansao_domada_modelo');
const { planejarCelulas } = require('./preparar_pilha_5156');

const CAMINHO = __dirname + '/menu_oficios_delta.json';
const ATRIBUTOS = ['FORÇA', 'DESTREZA', 'CONSTITUIÇÃO', 'INTELIGÊNCIA', 'ESSÊNCIA'];
const AVISO = 'Escolha o atributo';
const col = L => [...L].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
// conta → [menu, linha da DADOS_CONFIG, nomes aceitos]
const CONTAS = {};
['K108', 'K109', 'K110', 'K111', 'K112', 'K113'].forEach((m, i) => { CONTAS[(108 + i) + ':14'] = [m, 37 + i, ATRIBUTOS]; });
// A DADOS_CONFIG segue a ordem do catálogo (Instrumento antes de Jogatina); a FICHA põe Jogatina na linha 111.
[['X108', 43], ['X109', 44], ['X110', 45], ['X111', 47], ['X112', 46]].forEach(([m, l], i) => { CONTAS[(108 + i) + ':27'] = [m, l, ATRIBUTOS]; });
CONTAS['108:42'] = ['AK108', 48, ['FORÇA', 'DESTREZA']];
// menu → atributo padrão do livro (só os que mudam de INTELIGÊNCIA)
const PADRAO = { K108: 'DESTREZA', K109: 'DESTREZA', K111: 'FORÇA', K112: 'DESTREZA',
  X108: 'DESTREZA', X109: 'DESTREZA', X111: 'ESSÊNCIA', X112: 'ESSÊNCIA' };
const VALORES = Object.fromEntries(Object.entries(PADRAO).map(([m, v]) => [Number(m.slice(1)) + ':' + col(m[0]), v]));
const invalido = (menu, linha, nomes = ATRIBUTOS) =>
  `AND(DADOS_CONFIG!$C$${linha}<>1,NOT(OR(${nomes.map(a => `${menu}="${a}"`).join(',')})))`;

// Depois = antes com o aviso por fora (contas) ou o atributo do livro (menus); nada mais muda.
function explicar(pos, antes) {
  if (VALORES[pos]) return antes === 'INTELIGÊNCIA' ? VALORES[pos] : null;
  const alvo = CONTAS[pos];
  if (!alvo || typeof antes !== 'string') return null;
  const [menu, linha, nomes] = alvo;
  if (!antes.startsWith(`=IF(DADOS_CONFIG!$E$${linha}<>"",NA(),`) || !antes.includes(`IFS(${menu}="FORÇA",`)) return null;
  return `=IF(${invalido(menu, linha, nomes)},"${AVISO}",${antes.slice(1)})`;
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
      assert.ok(CONTAS[pos] || VALORES[pos], 'Mudança fora dos ofícios e do TR Físico: ' + pos);
      assert.equal(explicar(pos, o.get(pos)), d.get(pos), 'Mudança fora do molde em ' + pos);
      const [r, c] = pos.split(':').map(Number);
      delta.push({ aba: a.nome, r, c, antes: o.get(pos), depois: d.get(pos) });
    }
  }
  assert.equal(delta.length, 20, 'Esperadas doze contas e oito menus');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve as vinte células ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const aba = abas.find(a => a.nome === 'FICHA');
  if (!aba) throw Error('Menu dos ofícios: aba FICHA ausente');
  const antes = expandir(aba);
  for (const d of delta) if (antes.get(d.r + ':' + d.c) !== d.depois) throw Error('Menu dos ofícios divergente: FICHA!' + d.r + ',' + d.c);
  const copia = structuredClone(aba);
  for (const v of copia.vals) {
    const d = delta.find(d => d.r === v[0] && d.c === v[1]);
    if (d) v[2] = d.antes;
  }
  const depois = expandir(copia);
  const alvo = new Map(delta.map(d => [d.r + ':' + d.c, d.antes]));
  for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
    const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
    if (depois.get(pos) !== esperado) throw Error('Menu dos ofícios: reversão fora do molde em FICHA!' + pos);
  }
  aba.vals = copia.vals;
  return abas;
}

// Instalação nas QAs: snapshot = { locale, sheetIds: {FICHA: id}, cells: [{aba, r, c, value}] } na ordem do delta.
// Um menu que o jogador já trocou (diferente de INTELIGÊNCIA) recusa a instalação: escolha do jogador não se sobrescreve.
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
  console.log(JSON.stringify({ abas: r.abas, posicoes: r.posicoes, alteracoes: r.delta.length }));
}

module.exports = { explicar, comparar, reverterModelo, pedidos, invalido, CONTAS, VALORES, ATRIBUTOS, AVISO };
