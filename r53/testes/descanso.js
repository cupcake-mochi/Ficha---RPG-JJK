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
range.setValue(CP);
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), true);
assert.equal(le('energia'), 5);
assert.equal(le('descanso'), 'Escolha o descanso');
cenarios++;

// O mesmo evento reapresentado depois do reset não pode recuperar PE outra vez.
const registroAntes = le('último descanso'), avisosAntes = P.avisos.length;
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), false);
assert.equal(le('energia'), 5);
assert.equal(le('último descanso'), registroAntes);
assert.equal(P.avisos.length, avisosAntes);
cenarios++;

// Uma escolha diferente mais recente deve ficar intacta, junto com os recursos e o registro.
range.setValue(LF);
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), false);
assert.equal(le('descanso'), LF);
assert.equal(le('energia'), 5);
assert.equal(le('último descanso'), registroAntes);
assert.equal(P.avisos.length, avisosAntes);
cenarios++;

// Um novo descanso escolhido de propósito continua válido, inclusive do mesmo tipo.
range.setValue(CP);
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), true);
assert.equal(le('energia'), 9);
assert.equal(le('descanso'), 'Escolha o descanso');
cenarios++;

// Colagem/evento sem value mantém a leitura de reserva, mas não repete após o reset.
assert.equal(ctx.descansar_({ range }, idx), false);
assert.equal(le('energia'), 9);
cenarios++;

// O menu não amplia a faixa nem acrescenta uma chamada à leitura em lote.
const lerAntes = ctx.lerCelulas_;
let lotes = 0;
ctx.lerCelulas_ = (aba, lista) => {
  lotes++;
  assert(lista.includes(idx.descanso));
  const bounds = xs => xs.map(ctx.limitesA1_).reduce((b, r) =>
    [Math.min(b[0], r.l1), Math.min(b[1], r.c1), Math.max(b[2], r.l1), Math.max(b[3], r.c1)],
    [Infinity, Infinity, 0, 0]);
  assert.deepEqual(bounds(lista), bounds(lista.filter(c => c !== idx.descanso)));
  return lerAntes(aba, lista);
};
range.setValue(CP);
assert.equal(ctx.descansar_({ range: semLeitura, value: CP }, idx), true);
assert.equal(lotes, 1);
ctx.lerCelulas_ = lerAntes;
cenarios++;

// Todos os tipos recusam repetição após o reset, inclusive a cura aditiva do Exaurido.
for (const tipo of [CP, CF, LP, LF]) {
  for (const [chave, valor] of Object.entries({ ...base, origem: restricao, marcante: 'Corpo Exaurido',
    'menor 1': abundante, 'menor 2': '' })) celula(chave).setValue(valor);
  range.setValue(tipo);
  assert.equal(ctx.descansar_({ range, value: tipo }, idx), true);
  const depois = estado.map(le), registro = le('último descanso'), avisos = P.avisos.length;
  assert.equal(ctx.descansar_({ range, value: tipo }, idx), false);
  assert.deepEqual(estado.map(le), depois);
  assert.equal(le('último descanso'), registro);
  assert.equal(le('descanso'), 'Escolha o descanso');
  assert.equal(P.avisos.length, avisos);
  cenarios++;
}

// O convite no evento não é descanso, e nada muda na ficha.
celula('energia').setValue(1);
assert.equal(ctx.descansar_({ range: semLeitura, value: 'Escolha o descanso' }, idx), false);
assert.equal(le('energia'), 1);
cenarios++;
// Uma queda ativa desvia o seletor normal para a ação autorizada.
const vm = require('node:vm');
vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script', 'Socorro.gs'), 'utf8'), ctx);
const socorro = ss.insertSheet('SOCORRO');
socorro.getRange('A2').setValue('SOCORRO_R53_1');
const queda = ctx.r53SocorroNovaQueda_({
  atual: 0, maximo: 23, classe: 1, sequelas: 1, regras: [.25, 1/3, .5, 15, 3]
}, 2);
const lote = [];
ctx.Sheets = { Spreadsheets: { batchUpdate: ({requests}) => lote.push(requests) } };
for (const [tipo, corpo, derrotado, tratamento, vida, status, convertido] of [
  [LP, 'Corpo Exaurido', false, 0, 5, 'Encerrado no descanso'],
  [LF, 'Corpo Exaurido', false, 0, 0, 'Morrendo'],
  [LF, 'Corpo Exaurido', true, 3, 3, 'Encerrado no descanso'],
  [LF, '', false, 0, 11, 'Encerrado no descanso'],
  [LF, 'Corpo Exaurido', true, 3, 0, 'Derrotado', true]
]) {
  const registro = { ...queda, ...(derrotado ? {status: 'Derrotado', janela: 0} : {}), tratamento, ...(convertido ? {tratamentoConvertido: true} : {}) };
  socorro.getRange('B2').setValue(JSON.stringify(registro));
  for (const [chave, valor] of Object.entries({ ...base, vida: 0, origem: restricao, marcante: corpo,
    'menor 1': '', 'menor 2': '' })) celula(chave).setValue(valor);
  range.setValue(tipo);
  assert.equal(ctx.descansar_({range, value: tipo}, idx), false);
  assert.equal(le('vida'), 0);
  assert.equal(le('descanso'), 'Escolha o descanso');
  assert.throws(() => ctx.r53DescansarComQueda(tipo, {...registro, janela: 5}), /registro da queda mudou/);
  assert.equal(lote.length, 0);
  assert.equal(ctx.r53DescansarComQueda(tipo, registro), true);
  assert.equal(lote.length, 1);
  const atualizacoes = lote.pop().filter(r => r.updateCells).map(r => r.updateCells);
  const serializado = atualizacoes.find(r => r.rows[1]).rows[1].values[1].userEnteredValue.stringValue;
  assert.equal(JSON.parse(serializado).status, status);
  const escrito = chave => {
    const pos = ctx.limitesA1_(idx[chave]);
    return atualizacoes.find(r => r.start.rowIndex === pos.l1 - 1 && r.start.columnIndex === pos.c1 - 1)
      ?.rows[0].values[0].userEnteredValue;
  };
  assert.equal(escrito('vida')?.numberValue ?? 0, vida);
  assert.equal(escrito('sequela 1').boolValue, false);
  assert.equal(escrito('sequela extras').numberValue, 0);
  cenarios++;
}
console.log(JSON.stringify({ resultado: 'OK', cenarios }));
