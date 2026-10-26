'use strict';
// FICHA PESSOAL e Força com leitura curta (25/10/2026): o índice pessoal sai do molde, as tabelas da DADOS são lidas
// só nas colunas delas e as notas vivas só no retângulo das caixas. Confere, contra o código de antes, que as notas
// gravadas são as mesmas, e conta as leituras. Sheets de mentira: não mede o Google.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };

const letras = c => { let s = ''; for (; c; c = Math.floor((c - 1) / 26)) s = String.fromCharCode(65 + (c - 1) % 26) + s; return s; };
const pos = a1 => { const m = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(String(a1).replace(/\$/g, '')); assert(m, a1); const c = t => [...t].reduce((n, x) => n * 26 + x.charCodeAt(0) - 64, 0); return [+m[2], c(m[1]), +(m[4] || m[2]), c(m[3] || m[1])]; };

// As idas ao servidor: toda leitura conta; gravar não conta (o Google junta as gravações até a próxima leitura).
const io = [];
class Range {
  constructor(sh, r, c, nr = 1, nc = 1) { Object.assign(this, { sh, r, c, nr, nc }); }
  getSheet() { return this.sh; } getRow() { return this.r; } getColumn() { return this.c; }
  getLastRow() { return this.r + this.nr - 1; } getLastColumn() { return this.c + this.nc - 1; }
  getNumRows() { return this.nr; } getNumColumns() { return this.nc; }
  getA1Notation() { return letras(this.c) + this.r + (this.nr > 1 || this.nc > 1 ? ':' + letras(this.getLastColumn()) + this.getLastRow() : ''); }
  grade(mapa) { return Array.from({ length: this.nr }, (_, i) => Array.from({ length: this.nc }, (_, j) => mapa.get((this.r + i) + ',' + (this.c + j)) ?? '')); }
  getValues() { io.push('valores ' + this.sh.n + '!' + this.getA1Notation()); return this.grade(this.sh.v); }
  getValue() { return this.getValues()[0][0]; }
  getNotes() { io.push('notas ' + this.sh.n + '!' + this.getA1Notation()); return this.grade(this.sh.notas); }
  getFormulasR1C1() { io.push('fórmulas ' + this.sh.n); return this.grade(new Map()); }
  setValue(v) { this.sh.v.set(this.r + ',' + this.c, v); return this; }
  setNote(t) { this.sh.escritas.push([this.getA1Notation(), t]); this.sh.notas.set(this.r + ',' + this.c, t); return this; }
}
class Sheet {
  constructor(n, rows, cols) { Object.assign(this, { n, rows, cols, v: new Map(), notas: new Map(), escritas: [] }); }
  getName() { return this.n; }
  getRange(a, c, nr, nc) { if (typeof a === 'string') { const [r1, c1, r2, c2] = pos(a); return new Range(this, r1, c1, r2 - r1 + 1, c2 - c1 + 1); } return new Range(this, a, c, nr, nc); }
  getLastRow() { io.push('getLastRow ' + this.n); return this.rows; }
  getDataRange() { io.push('getDataRange ' + this.n); return new Range(this, 1, 1, this.rows, this.cols); }
}

function montar(codigo) {
  const sheets = new Map();
  const ss = { getSheetByName: n => sheets.get(n) || null, getSpreadsheetLocale: () => 'pt_BR', toast() {} };
  const ctx = { console: { log() {} }, SpreadsheetApp: { getActive: () => ss, flush() { io.push('flush'); } } };
  vm.createContext(ctx);
  vm.runInContext(require(path.join(raiz, 'medidas/carregar-ficha.js')).fontes() + '\n' + codigo, ctx);
  for (const spec of ctx.ABAS) if (['DADOS', 'FICHA PESSOAL', 'FICHA'].includes(spec.nome)) sheets.set(spec.nome, new Sheet(spec.nome, spec.rows, spec.cols));
  // A DADOS como o Google a mostra: endereço onde há ADDRESS, um texto que muda com a ficha onde há outra conta.
  const dados = sheets.get('DADOS'), spec = ctx.ABAS.find(s => s.nome === 'DADOS');
  for (const [r, c, v] of spec.vals) {
    const a = typeof v === 'string' && v.startsWith('=ADDRESS(') ? [...v.matchAll(/ADDRESS\(ROW\((?:'[^']+'|[A-Z_]+)!\$?([A-Z]+)\$?(\d+)\)/g)] : [];
    dados.v.set(r + ',' + c, a.length ? a.map(x => x[1] + x[2]).join(':') : typeof v === 'string' && v.startsWith('=') ? 'conta ' + r + ',' + c : v);
  }
  return { ctx, ss, sheets, dados, spec };
}

const novo = fs.readFileSync(path.join(raiz, 'apps-script/Codigo.gs'), 'utf8');
const N = montar(novo), ctx = N.ctx;
const ip = ctx.indicePessoal_();

// 1. As tabelas lidas só nas colunas dão o mesmo que a DADOS inteira, em todas as que o Codigo.gs lê.
const cheia = N.dados.getDataRange().getValues();
const tabelas = [['Caminho'], ['Caminho que treina todas as armas'], ['categoria de arma', ['conjurador treina', 'caixa do grupo']],
  ['equipável', ['categoria do equipável', 'caixa do treino']], ['limiar do feito'], ['nível', ['xp acumulado']],
  ['nota viva', ['texto da nota', 'caixa da nota']], ['capacidade da origem']];
for (const [chave, outras] of tabelas) {
  const antes = JSON.stringify(ctx.tabelaDaDados_(cheia, chave, outras));
  io.length = 0;
  const lida = JSON.stringify(ctx.tabelaLida_(N.ss, chave, outras));
  eq(lida, antes, 'tabela ' + chave);
  eq(io.length, 1, 'tabela ' + chave + ' numa ida só');
  assert(!io[0].startsWith('getDataRange'), 'tabela ' + chave + ' sem o getDataRange'); checks++;
  assert(JSON.parse(antes).length > 0, 'tabela vazia: ' + chave); checks++;
}
eq(JSON.stringify(ctx.tabelaLida_(N.ss, 'cabeçalho que não existe')), '[]', 'tabela ausente');

// 2. O índice pessoal do molde é o mesmo que a leitura das duas colunas, e não vai à planilha.
io.length = 0;
eq(ctx.indicePessoal_(), ip); eq(io.length, 0, 'índice pessoal sem leitura');
const lido = {};
N.dados.getRange(1, ctx.IDXP_COL_CAMPO, N.dados.rows, 2).getValues().forEach(l => { if (l[0] && l[1] && l[0] !== 'campo pessoal') lido[l[0]] = String(l[1]); });
eq(JSON.stringify(ip), JSON.stringify(lido), 'índice pessoal do molde');
eq(ip.principal, 'D64', 'mão principal no índice');

// 3. As notas: o mesmo que o notasVivas_ com a DADOS inteira, em duas leituras.
const notasDe = sh => [...sh.notas.entries()].sort().map(x => x.join('=')).join('|');
const caixas = ctx.tabelaDaDados_(cheia, 'nota viva', ['texto da nota', 'caixa da nota']).filter(l => l['caixa da nota']);
assert(caixas.length >= 3, 'poucas notas vivas: ' + caixas.length); checks++;
function cenario(rodar) {
  const P = montar(novo), pessoal = P.sheets.get('FICHA PESSOAL');
  // uma nota já certa, uma desatualizada e as outras vazias
  const c0 = pos(caixas[0]['caixa da nota']), c1 = pos(caixas[1]['caixa da nota']);
  pessoal.notas.set(c0[0] + ',' + c0[1], String(caixas[0]['texto da nota']));
  pessoal.notas.set(c1[0] + ',' + c1[1], 'nota velha');
  io.length = 0;
  rodar(P);
  return { notas: notasDe(pessoal), escritas: pessoal.escritas.map(x => x.join('=')).sort(), leituras: io.slice() };
}
const velho = cenario(P => P.ctx.notasVivas_(P.ss, P.dados.getDataRange().getValues()));
const leve = cenario(P => P.ctx.notasVivasLeves_(P.ss));
eq(leve.notas, velho.notas, 'notas finais');
eq(leve.escritas, velho.escritas, 'notas gravadas');
eq(leve.escritas.length, caixas.length - 1, 'só as notas que mudaram');
eq(leve.leituras.length, 2, 'notas em duas leituras: ' + leve.leituras);

// 4. A arma na mão pela FICHA PESSOAL: mesmas notas, duas leituras (eram 12 no contador de 25/10).
const mao = ip.principal, ev = P => ({ range: P.sheets.get('FICHA PESSOAL').getRange(mao), value: 'Bastão', source: P.ss });
const armaLeve = cenario(P => { P.ctx.textoDaCapacidade_(ev(P)); P.ctx.pessoalEditada_(ev(P)); });
eq(armaLeve.escritas, velho.escritas, 'arma na mão: notas');
eq(armaLeve.leituras.length, 2, 'arma na mão: ' + armaLeve.leituras);

// 5. A Força pelo onEdit comum: o mesmo que o fichaMexeNaPessoal_, duas leituras (eram 8).
const idx = ctx.indiceEstatico_();
for (const campo of ['atr_base_Força', 'corpo_Força']) {
  const evF = P => ({ range: P.sheets.get('FICHA').getRange(ctx.cel_(idx, campo)), value: '3', source: P.ss });
  const antes = cenario(P => P.ctx.fichaMexeNaPessoal_(evF(P), idx));
  const depois = cenario(P => P.ctx.fichaMexeNaPessoalLeve_(evF(P), idx));
  eq(depois.escritas, antes.escritas, campo + ': notas');
  eq(depois.leituras.length, 2, campo + ': ' + depois.leituras);
}
// Outra célula da FICHA não mexe na FICHA PESSOAL; o Caminho segue pelo de sempre.
const outra = cenario(P => P.ctx.fichaMexeNaPessoalLeve_({ range: P.sheets.get('FICHA').getRange('B2'), value: 'x', source: P.ss }, idx));
eq(outra.leituras.length + outra.escritas.length, 0, 'célula comum da FICHA');
assert(/fichaMexeNaPessoalLeve_\(e, idx\); \} catch/.test(novo) && !/try \{ fichaMexeNaPessoal_\(e, idx\); \}/.test(novo), 'onEdit não chama o leve'); checks++;
assert(/if \(a1 === cel_\(idx, 'caminho'\)\) return fichaMexeNaPessoal_\(e, idx\);/.test(novo), 'Caminho fora do de sempre'); checks++;

console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'tabelas da DADOS por coluna iguais à leitura inteira, índice pessoal do molde, notas vivas iguais às de antes na arma da mão e na Força, e contagem de leituras; não mede o Google.' }));
