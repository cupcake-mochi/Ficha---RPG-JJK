'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {sha, trocar} = require('./preparar_recursos_fila');
const {planejarCelulas, formulaLocal} = require('./preparar_pilha_5156');
const {norm} = require('./preparar_pratica_cotidiana');
const base = require('./rajada_alvos_base.json');
const alvos = require('../rajada_alvos');
const runtime = require('../pratica_cotidiana_runtime');

const CODIGO_BASE = '21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923';

function prepararCodigo(src) {
  if (sha(src) !== CODIGO_BASE) throw Error('Código exige a versão ensaiada da PR75');
  return trocar(src, runtime.gerar(undefined, undefined, []), runtime.gerar());
}

function prepararCelulas(snapshot, linhas = alvos.linhas) {
  const {locale, cells} = snapshot ?? {};
  if (!base[locale] || !Array.isArray(cells)) throw Error('Snapshot atual obrigatório');
  if (!linhas.length || new Set(linhas).size !== linhas.length ||
      !linhas.every(r => alvos.linhas.includes(r))) throw Error('Linhas de montagem inválidas');

  const formulas = alvos.formulas().filter(d => linhas.includes(d.r));
  const atuais = new Map();
  for (const x of cells) {
    const chave = x.r + ':' + x.c;
    if (x.aba !== alvos.aba || atuais.has(chave)) throw Error('Snapshot com alvo divergente: ' + chave);
    atuais.set(chave, x);
  }
  if (atuais.size !== formulas.length) throw Error('Cobertura do snapshot divergente');
  const plano = formulas.map(d => ({...d, antes: norm(atuais.get(d.r + ':' + d.c)?.value)}));
  for (const r of linhas) {
    const linha = plano.filter(d => d.r === r).map(d => d.antes);
    if (sha(JSON.stringify(linha)) !== base[locale][alvos.linhas.indexOf(r)]) {
      throw Error('Fórmulas anteriores divergentes na linha ' + r);
    }
  }

  const snapshotNormal = {...snapshot, cells: cells.map(x => ({...x, value: norm(x.value)}))};
  const deltaLocal = plano.map(d => ({
    ...d, depois: norm(formulaLocal(d.depois, locale)),
  }));
  // As duas versões já estão localizadas. A comparação usa o mesmo formato dos pedidos.
  const final = deltaLocal.map(d => ({
    ...atuais.get(d.r + ':' + d.c), value: d.depois,
  }));
  return {
    pedidos: planejarCelulas({...snapshotNormal, locale: 'en_US'}, false, deltaLocal).requests,
    reverter: atual => {
      if (atual.locale !== locale || atual.cells.some(x =>
        x.sheetId !== atuais.get(x.r + ':' + x.c)?.sheetId)) throw Error('Alvo da reversão divergente');
      const releitura = atual.cells.map(x => ({...x, value: norm(x.value)}));
      const pedidos = planejarCelulas({locale: 'en_US', cells: releitura}, true, deltaLocal).requests;
      for (const [i, {r, c}] of deltaLocal.entries()) {
        pedidos[i].updateCells.rows[0].values[0].userEnteredValue.formulaValue =
          atuais.get(r + ':' + c).value;
      }
      return pedidos;
    },
    final: {...snapshot, cells: final},
  };
}

if (require.main === module) {
  const [codigo, celulas, destino] = process.argv.slice(2);
  if (!codigo || !celulas || !destino || fs.existsSync(destino)) {
    throw Error('Uso: node preparar_rajada_alvos.js Codigo-snapshot.gs celulas-snapshot.json pasta-nova');
  }
  const anterior = fs.readFileSync(codigo, 'utf8');
  const snapshot = JSON.parse(fs.readFileSync(celulas, 'utf8'));
  const plano = prepararCelulas(snapshot);
  const arquivos = {
    'Codigo-proposto.gs': prepararCodigo(anterior),
    'Codigo-reversao.gs': anterior,
    'pedidos.json': JSON.stringify(plano.pedidos),
    'reversao.json': JSON.stringify(plano.reverter(plano.final)),
  };
  fs.mkdirSync(destino);
  for (const [nome, conteudo] of Object.entries(arquivos)) {
    fs.writeFileSync(path.join(destino, nome), conteudo);
  }
}

module.exports = {prepararCodigo, prepararCelulas};
