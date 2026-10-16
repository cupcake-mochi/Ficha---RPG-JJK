'use strict';
// Carrega os .gs de uma pasta num VM, sem Google. Executa a guarda de montar_() até o
// primeiro acesso a SpreadsheetApp (sentinela) e descreve a ANALISE montada em memória.
// Uso: node sonda_carregador.js <pasta> <chaves.json> [arquivo-ignorado ...]
const fs = require('fs'), path = require('path'), vm = require('vm');
const [pasta, chavesArq, ...ignorar] = process.argv.slice(2);
const fora = new Set(['Ficha.gs', 'Codigo.gs', 'Habilidades.gs', ...ignorar]);
const arquivos = ['Ficha.gs', ...fs.readdirSync(pasta).filter(n => n.endsWith('.gs') && !fora.has(n)).sort()];
const c = {}; vm.createContext(c);
for (const f of arquivos) vm.runInContext(fs.readFileSync(path.join(pasta, f), 'utf8'), c, { filename: f });
const SENT = '__SENTINELA_SEM_GOOGLE__';
const falha = () => { throw new Error(SENT); };
c.SpreadsheetApp = { getActive: falha, getActiveSpreadsheet: falha };
c.PropertiesService = { getDocumentProperties: falha, getScriptProperties: falha };
let guarda;
try { c.montar_(); guarda = 'sem sentinela'; } catch (e) { guarda = e.message.includes(SENT) ? 'passa' : e.message; }
const esperadas = JSON.parse(fs.readFileSync(chavesArq, 'utf8'));
const an = c.ABAS.find(a => a.nome === 'ANALISE');
const col1 = an.vals.filter(v => v[1] === 1 && v[0] > 1).sort((a, b) => a[0] - b[0]);
const chaves = col1.map(v => v[2]);
const repetidas = chaves.filter((k, i) => chaves.indexOf(k) !== i);
const maxLinha = Math.max(...an.vals.map(v => v[0]));
const alemDaGrade = c.ABAS.map(a => ({ nome: a.nome, rows: a.rows, max: Math.max(0, ...a.vals.map(v => v[0])) }))
  .filter(a => a.rows && a.max > a.rows);
const obsoletas = chaves.filter(k => !esperadas.includes(k));
const faltam = esperadas.filter(k => !chaves.includes(k));
console.log(JSON.stringify({
  arquivos, guarda, linhasAnalise: an.rows, maxLinha, chaves: chaves.length,
  unicas: new Set(chaves).size, repetidas: repetidas.slice(0, 5), nRepetidas: repetidas.length,
  obsoletas: obsoletas.slice(0, 5), nObsoletas: obsoletas.length, faltam: faltam.slice(0, 5), nFaltam: faltam.length,
  mesmaOrdem: faltam.length === 0 && obsoletas.length === 0 && chaves.every((k, i) => k === esperadas[i]),
  alemDaGrade
}));
