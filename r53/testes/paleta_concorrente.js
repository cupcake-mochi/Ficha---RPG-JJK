'use strict';
// Um callback pode terminar a pintura enquanto outro tenta obter o bloqueio.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync('apps-script/Codigo.gs', 'utf8');
const light = require('../paleta_leve.js').gerar().code;
let checks = 0;
for (const code of [source, light.replace(/return \{trocar:[\s\S]*$/, '')]) {
  for (const scenario of ['terminou', 'avancou', 'ocupado', 'sem-pendencia']) {
    let locked = false, releases = 0, reads = 0, paints = 0;
    const state = scenario === 'sem-pendencia' ? {} : {paleta_pendente: 'Noite · Claro', paleta_feito: 'antes'};
    const ctx = {console, PropertiesService: {getDocumentProperties: () => ({
      getProperty: key => state[key],
      getProperties: () => { assert(locked); reads++; return {...state}; }
    })}, LockService: {getScriptLock: () => ({
      tryLock: () => {
        if (scenario === 'ocupado') return false;
        locked = true;
        if (scenario === 'terminou') delete state.paleta_pendente;
        if (scenario === 'avancou') state.paleta_feito = 'depois';
        return true;
      },
      releaseLock: () => { assert(locked); locked = false; releases++; }
    })}};
    vm.createContext(ctx); vm.runInContext(code, ctx);
    ctx.convergirPaleta_ = (inicio, orcamento, dica, aba, snapshot) => {
      assert(locked); assert.strictEqual(snapshot.paleta_feito, 'depois'); paints++;
    };
    ctx.continuarPaleta_(0, null, false, null);
    assert.strictEqual(paints, scenario === 'avancou' ? 1 : 0);
    assert.strictEqual(reads, ['terminou', 'avancou'].includes(scenario) ? 1 : 0);
    assert.strictEqual(releases, reads); assert.strictEqual(locked, false);
    checks++;
  }
}
console.log(JSON.stringify({resultado:'OK', cenarios:checks, escopo:'VM: fonte integral e módulo leve; sem Google'}));
