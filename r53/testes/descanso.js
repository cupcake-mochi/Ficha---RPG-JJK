'use strict';
// Exercita a rotina do menu com o índice publicado, sem reconstruir a ficha.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const raiz = path.resolve(__dirname, '../..');
const { fontes } = require('../../medidas/carregar-ficha.js');
const { criaSheets } = require('../../medidas/sheets-de-mentira.js');
const codigo = fs.readFileSync(path.join(raiz, 'apps-script', 'Codigo.gs'), 'utf8');
const { ctx, ss, P } = criaSheets(fontes(), codigo);
const idx = ctx.indiceEstatico_();
const ficha = ss.insertSheet('FICHA');
ficha.insertColumnsAfter(26, 24);
const dadosCustom = ss.getSheetByName('DADOS_CUSTOM') || ss.insertSheet('DADOS_CUSTOM');
const celula = chave => ficha.getRange(idx[chave]);
const le = chave => celula(chave).getValue();
const base = { vida: 3, vida_max: 23, energia: 1, energia_max: 10, integridade: 4, integridade_max: 20,
  'exaustão': 2, 'sequela 1': true, 'sequela 2': false, 'sequela 3': false, 'sequela extras': 2 };
const restricao = 'Restrição Celestial · Restrição corporal', abundante = 'Recuperação Abundante';
const LP = 'Longo · lugar propício', LF = 'Longo · fora';
const CP = 'Curto · lugar propício', CF = 'Curto · fora';
const estado = ['vida', 'energia', 'integridade', 'exaustão', 'sequela 1', 'sequela extras'];
let cenarios = 0;

function descanso(tipo, campos, esperado, registro, regras = {}) {
  dadosCustom.getRange('B126').setValue(regras.corporal === true);
  dadosCustom.getRange('B127').setValue(regras.permitida === true);
  for (const [chave, valor] of Object.entries({ ...base, origem: restricao, marcante: 'Corpo Exaurido',
    'menor 1': abundante, 'menor 2': '', ...campos })) {
    celula(chave).setValue(valor);
  }
  const range = celula('descanso');
  range.setValue(tipo);
  const avisos = P.avisos.length;
  assert.equal(ctx.descansar_({ range }, idx), true, tipo);
  assert.deepEqual(estado.map(le), esperado, tipo);
  assert.equal(le('descanso'), 'Escolha o descanso');
  assert.match(le('último descanso'), registro);
  assert.equal(P.avisos.length, avisos + 1);
  cenarios++;
}

descanso(LP, {}, [8, 10, 20, 0, false, 0], /vida 3 → 8/);
descanso(LF, {}, [3, 5, 20, 2, false, 0], /Exaustão fica em 2/);
descanso(LP, { vida: 1, vida_max: 3 }, [2, 10, 20, 0, false, 0], /vida 1 → 2/);
descanso(LP, { vida: 22 }, [23, 10, 20, 0, false, 0], /vida 22 → 23/);
descanso(LP, { vida: 0, vida_max: 0 }, [0, 10, 20, 0, false, 0], /PE 1 → 10/);
descanso(CP, {}, [3, 5, 4, 2, true, 2], /PE 1 → 5/);
descanso(CF, {}, [3, 2, 4, 2, true, 2], /PE 1 → 2/);
descanso(CP, { marcante: 'Corpo Debilitado', 'menor 1': '', 'menor 2': abundante },
  [3, 5, 4, 2, true, 2], /PE 1 → 5/);
descanso(CP, { energia: 9 }, [3, 10, 4, 2, true, 2], /PE 9 → 10/);
descanso(CP, { energia: 0, energia_max: 2 }, [3, 1, 4, 2, true, 2], /PE 0 → 1/);
descanso(CP, { origem: 'Latente' }, [3, 3, 4, 2, true, 2], /PE 1 → 3/);
descanso(CP, { marcante: '' }, [3, 3, 4, 2, true, 2], /PE 1 → 3/);
descanso(LF, { origem: 'Latente' }, [11, 5, 20, 2, false, 0], /vida 3 → 11/);

// A Origem custom válida com base corporal herda as regras dos corpos publicados.
const custom = 'Corpo Partido', baseCorporal = { corporal: true, permitida: true };
descanso(LP, { origem: custom }, [8, 10, 20, 0, false, 0], /vida 3 → 8/, baseCorporal);
descanso(LF, { origem: custom }, [3, 5, 20, 2, false, 0], /Exaustão fica em 2/, baseCorporal);
descanso(CP, { origem: custom }, [3, 5, 4, 2, true, 2], /PE 1 → 5/, baseCorporal);
descanso(CF, { origem: custom }, [3, 2, 4, 2, true, 2], /PE 1 → 2/, baseCorporal);
for (const corpo of ['Corpo Debilitado', 'Corpo Quebradiço']) {
  descanso(LP, { origem: custom, marcante: corpo }, [23, 10, 20, 0, false, 0], /vida 3 → 23/, baseCorporal);
  descanso(LF, { origem: custom, marcante: corpo }, [11, 5, 20, 2, false, 0], /vida 3 → 11/, baseCorporal);
  descanso(CP, { origem: custom, marcante: corpo }, [3, 5, 4, 2, true, 2], /PE 1 → 5/, baseCorporal);
}

// Um corpo próprio permitido conserva a menor, sem receber as regras do Exaurido.
for (const origem of [restricao, custom]) {
  for (const corpo of ['Criada com o mestre', 'Corpo Próprio']) {
    descanso(LP, { origem, marcante: corpo }, [23, 10, 20, 0, false, 0], /vida 3 → 23/, baseCorporal);
    descanso(LF, { origem, marcante: corpo }, [11, 5, 20, 2, false, 0], /vida 3 → 11/, baseCorporal);
    descanso(CP, { origem, marcante: corpo }, [3, 5, 4, 2, true, 2], /PE 1 → 5/, baseCorporal);
    descanso(CF, { origem, marcante: corpo }, [3, 2, 4, 2, true, 2], /PE 1 → 2/, baseCorporal);
  }
}

// Sem a base válida ou sem a marcante no menu, nada é inferido do nome exibido.
const semBase = { corporal: false, permitida: false };
for (const origem of [custom, 'Latente']) {
  descanso(LP, { origem }, [23, 10, 20, 0, false, 0], /vida 3 → 23/, semBase);
  descanso(LF, { origem }, [11, 5, 20, 2, false, 0], /vida 3 → 11/, semBase);
  descanso(CP, { origem }, [3, 3, 4, 2, true, 2], /PE 1 → 3/, semBase);
}
descanso(CP, { marcante: 'Tentativa e Erro' }, [3, 3, 4, 2, true, 2], /PE 1 → 3/, { corporal: true, permitida: false });
descanso(CP, { origem: custom, marcante: 'Tentativa e Erro' }, [3, 3, 4, 2, true, 2], /PE 1 → 3/,
  { corporal: true, permitida: false });
descanso(CP, { origem: custom, 'menor 1': '' }, [3, 3, 4, 2, true, 2], /PE 1 → 3/, baseCorporal);

// Ficha antiga, sem as células novas: o que depende delas cai na regra normal.
dadosCustom.getRange('B126:B127').clearContent();
for (const [chave, valor] of Object.entries({ ...base, origem: custom, marcante: 'Corpo Exaurido', 'menor 1': abundante, 'menor 2': '' })) {
  celula(chave).setValue(valor);
}
const range = celula('descanso');
range.setValue(CP);
assert.equal(ctx.descansar_({ range }, idx), true);
assert.equal(le('energia'), 3);
cenarios++;

// O evento já traz a escolha: com e.value, o tipo não custa uma leitura da célula.
const semLeitura = Object.create(range);
semLeitura.getValue = () => { throw new Error('descansar_ leu a célula tendo e.value'); };
for (const [chave, valor] of Object.entries({ ...base, origem: restricao, marcante: 'Corpo Exaurido', 'menor 1': abundante, 'menor 2': '' })) {
  celula(chave).setValue(valor);
}
range.setValue('Escolha o descanso');
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), true);
assert.equal(le('energia'), 5);
assert.equal(le('descanso'), 'Escolha o descanso');
cenarios++;

// O convite no evento não é descanso, e nada muda na ficha.
celula('energia').setValue(1);
assert.equal(ctx.descansar_({ range: semLeitura, value: 'Escolha o descanso' }, idx), false);
assert.equal(le('energia'), 1);
cenarios++;
console.log(JSON.stringify({ resultado: 'OK', cenarios }));
