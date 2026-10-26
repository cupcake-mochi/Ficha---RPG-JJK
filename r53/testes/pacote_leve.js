'use strict';
// Pacote leve: os remendos instalados batem com o Codigo.gs do repositório, o corte da montagem deixa um módulo
// que carrega com as abas do jogador, e as correções lidas como dados dão o mesmo texto que executá-las.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const { transformarModulo, corrigirSemExecutar, remendos } = require('../diagnostico-android/instalar_pacote_leve');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };

// 1. Cada remendo instalado deixa o texto que está no Codigo.gs do repositório.
const codigo = fs.readFileSync(path.join(raiz, 'apps-script/Codigo.gs'), 'utf8');
for (const [i, p] of remendos().entries()) ok(codigo.includes(p[1]), 'remendo ' + (i + 1) + ' fora do Codigo.gs');

// 2. Sem remendos, o corte vale para o módulo montado das fontes do repositório.
const fontes = require(path.join(raiz, 'medidas/carregar-ficha.js')).fontes() + '\n' + codigo;
const leve = transformarModulo(fontes + '\nreturn {construir: construir, continuar: continuar, acabar: acabar, onEdit: onEdit, abas: function () { return ABAS; }, sobras: function () { return SOBRAS_; }};', []);
ok(leve.cortados.length >= 25 && leve.travas === 3, 'corte: ' + leve.cortados.length + ' tabelas, ' + leve.travas + ' travas');
const box = { console: { log() {} } }; vm.createContext(box);
const mod = vm.runInContext('(function(){' + leve.code + '\n})', box)();
const nomes = mod.abas().map(a => a.nome);
ok(!['ANALISE', 'MONTAGENS', 'DADOS_R53', 'DADOS_R53_CATALOGO'].some(n => nomes.includes(n)), 'abas da montagem continuam: ' + nomes);
ok(['FICHA', 'FICHA PESSOAL', 'DADOS', 'INVOCAÇÕES', 'CONFIGURAÇÃO'].every(n => nomes.includes(n)), 'falta aba do jogador');
ok(mod.sobras().length === 0, 'gerações misturadas');
for (const f of ['construir', 'continuar', 'acabar']) {
  let erro = null; try { mod[f](); } catch (e) { erro = e; }
  ok(erro && /Pacote leve/.test(erro.message), f + ' não travou');
}

// 3. As correções lidas como dados dão o mesmo texto que executar as funções delas.
const fonte = [
  'function r53CorrecaoAbertura_(code){var patches=' + JSON.stringify([['alfa', 'A$&A']]) + ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção R53: âncora divergente");code=code.replace(p[0],p[1]);});return code;}',
  'function r53CorrecaoAndroid_(code){var patches=' + JSON.stringify([['beta', 'B']]) + ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção Android: âncora divergente");code=code.replace(p[0],p[1]);});return code;}',
  'function r53CorrecaoFila_(code){var patches=' + JSON.stringify([['gama', 'G$&G']]) + ';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção da fila: âncora divergente");code=code.replace(p[0],function(){return p[1];});});return code;}',
  'function r53CorrecaoCaminho_(code){var a="delta \\"x\\"",b="D";if(code.split(a).length!==2)throw Error("Caminho: entrada do editor divergente");return code.replace(a,b);}'
].join('\n');
const texto = 'alfa beta gama delta "x"';
const executado = new Function(fonte + '\nreturn r53CorrecaoCaminho_(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(' + JSON.stringify(texto) + '))));')();
ok(corrigirSemExecutar(fonte, texto) === executado, 'correções como dados: ' + corrigirSemExecutar(fonte, texto) + ' / ' + executado);

console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'remendos no Codigo.gs, corte da montagem, travas da montagem e correções sem executar texto; o hash do pacote instalado só é conferido no Google.' }));
