'use strict';
const fs = require('fs'), vm = require('vm'), assert = require('assert'), crypto = require('crypto');
const code = fs.readFileSync(__dirname + '/auditar_contexto_android.gs', 'utf8');
const original = '1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro';
const copy = '1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8';
function fixture(id, script, pending, broken) {
  let writes = 0, loads = 0;
  const forbidden = () => { writes++; throw Error('Escrita não permitida'); };
  const properties = {getProperty: k => k === 'paleta_pendente' ? pending : k === 'paleta_atual' ? 'Padrão' : null, setProperty: forbidden, deleteProperty: forbidden};
  const context = {
    console: {log() {}},
    r53Modulo_: () => { loads++; throw Error('Carregou regras'); },
    SpreadsheetApp: {getActive: () => ({getId: () => id,
      getRangeByName: () => ({getCell: () => ({getValue: () => 'Padrão'})}),
      getSheetByName: name => ({getRange: () => ({getValue: () => name === 'DADOS_SALARIOS' ? JSON.stringify({versao: 1, agenda: 'origem'}) : 'Diária', setValue: forbidden})}),
      getNamedRanges: () => []}), flush: forbidden},
    ScriptApp: {getScriptId: () => script,
      getProjectTriggers: () => {if (broken) throw Error('Leitura indisponível'); return script === 'origem' ? [{getHandlerFunction: () => 'salarioAposAbrir', getEventType: () => 'ON_OPEN', getTriggerSource: () => 'SPREADSHEETS', getTriggerSourceId: () => original}] : [];},
      newTrigger: forbidden, deleteTrigger: forbidden},
    PropertiesService: {getDocumentProperties: () => properties, getScriptProperties: () => ({getProperty: () => 'origem', setProperty: forbidden})},
    Utilities: {DigestAlgorithm: {SHA_256: 'sha256'}, Charset: {UTF_8: 'utf8'}, computeDigest: (_, text) => Array.from(crypto.createHash('sha256').update(text).digest())}
  };
  vm.createContext(context); vm.runInContext(code, context);
  return {context, run: () => context.auditarContextoAndroid(), writes: () => writes, loads: () => loads};
}
const a = fixture(original, 'origem', 'tema-pendente', false), ar = a.run();
assert.strictEqual(ar.somenteLeitura, true);
assert.strictEqual(ar.salarios.agendaApontaEsteProjeto, true);
assert.strictEqual(ar.acionadores.length, 1);
assert.strictEqual(ar.paleta.paleta_pendente, 'tema-pendente');
assert.strictEqual(a.writes(), 0); assert.strictEqual(a.loads(), 0);
const b = fixture(copy, 'copia', null, false), br = b.run();
assert.strictEqual(br.salarios.agendaApontaEsteProjeto, false);
assert.strictEqual(br.salarios.edicaoInstalavelMarcadaNesteProjeto, false);
assert.strictEqual(br.acionadores.length, 0);
assert.strictEqual(b.writes(), 0); assert.strictEqual(b.loads(), 0);
const broken = fixture(original, 'origem', null, true).run();
assert.strictEqual(broken.acionadores.erro, 'Leitura indisponível');
assert.strictEqual(broken.salarios.moduloInicializado, true);
assert.throws(() => fixture('outro-documento', 'x', null, false).run(), /restrito/);
console.log(JSON.stringify({resultado: 'OK', escrita: 0, cargaCatalogos: 0, cenarios: ['original', 'copia-com-agenda-herdada', 'falha-parcial-de-leitura', 'documento-fora-do-escopo']}));
