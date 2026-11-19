'use strict';
// Preparação offline. A aplicação exige snapshot de fórmulas, nota, validações e código.
const {chave, formulaLocal, planejarCelulas} = require('./preparar_pilha_5156');
const {sha, trocar} = require('./preparar_recursos_fila');
const plano = require('./equipamento_plano.json');

const BASE = '9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631';
const normalizar = s => typeof s === 'string' && s.startsWith('=') ?
  s.split(/("(?:[^"]|"")*")/).map((p, i) => i % 2 ? p : p.replace(/'(DADOS|DADOS_CUSTOM)'!/g, '$1!')).join('') : s;

function molde() {
  const fs = require('node:fs'), path = require('node:path');
  const remendo = fs.readFileSync(path.join(__dirname, 'pilha_5156_molde.gs'), 'utf8')
    .replaceAll('r53AjustarPilha516_', 'r53AjustarEquipamento_')
    .replaceAll('R53_PILHA_516_', 'R53_EQUIPAMENTO_')
    .replaceAll('Pilha 51–56:', 'Equipamento:');
  return 'var R53_EQUIPAMENTO_ = ' + JSON.stringify(plano.celulas) + ';\n' + remendo;
}

function prepararCodigo(codigo) {
  if (sha(codigo) !== BASE) throw Error('Codigo.gs incompatível com a base PR63 ensaiada');
  const dados = 'R53_MODULO_.__estado().abas';
  const anterior = 'r53AjustarIntegridadeMovimento_(' + dados + ');';
  return trocar(codigo, anterior, anterior + ' r53AjustarEquipamento_(' + dados + ');') + '\n' + molde();
}

function planejar(snapshot, reverter = false) {
  const deltas = plano.celulas.map(d => d.addr ? d : {...d, antes: normalizar(d.antes), depois: normalizar(d.depois)});
  const cells = snapshot.cells.map(d => d.addr ? d : {...d, value: normalizar(d.value)});
  const requests = planejarCelulas({...snapshot, cells}, reverter, deltas).requests;
  const pessoal = cells.find(d => d.aba === 'FICHA PESSOAL');
  for (const d of plano.validacoes) {
    const alvo = {aba: 'FICHA PESSOAL', r: Number(d[0].slice(1)), c: 11};
    const registros = cells.filter(x => chave(x) === chave(alvo));
    const rule = {condition: {type: 'CUSTOM_FORMULA', values: [{userEnteredValue: formulaLocal(d[1], snapshot.locale)}]}, strict: true};
    const estado = registros[0]?.validation;
    if (registros.length !== 1 || registros[0].sheetId !== pessoal.sheetId ||
        (reverter ? estado?.strict !== true || estado?.condition?.type !== 'CUSTOM_FORMULA' ||
          estado.condition.values?.[0]?.userEnteredValue !== rule.condition.values[0].userEnteredValue : estado != null)) {
      throw Error('Validação divergente: ' + chave(alvo));
    }
    const start = {sheetId: pessoal.sheetId, rowIndex: alvo.r - 1, columnIndex: alvo.c - 1};
    requests.push({updateCells: {start, rows: [{values: [reverter ? {} : {dataValidation: rule}]}], fields: 'dataValidation'}});
  }
  return {requests};
}
module.exports = {plano, planejar, prepararCodigo, molde};
