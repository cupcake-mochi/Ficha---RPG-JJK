'use strict';
// Pacote leve: os remendos instalados batem com o Codigo.gs do repositório, o corte da montagem deixa um módulo
// que carrega com as abas do jogador, e as correções lidas como dados dão o mesmo texto que executá-las.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
const { transformarModulo, corrigirSemExecutar, aplicarIncremento, remendos } = require('../diagnostico-android/instalar_pacote_leve');
let checks = 0;
const ok = (c, m) => { assert(c, m); checks++; };

// 1. Cada remendo instalado deixa o texto que está no Codigo.gs do repositório. Um remendo pode mexer no texto que um
// anterior deixou (26/10/2026: a tabelaLida_ do 16º virou a tabelaLidaDe_ no 23º), então confere de trás pra frente.
const codigo = fs.readFileSync(path.join(raiz, 'apps-script/Codigo.gs'), 'utf8');
{ let t = codigo; for (const [i, p] of [...remendos().entries()].reverse()) { ok(t.includes(p[1]), 'remendo ' + (i + 1) + ' fora do Codigo.gs'); t = t.replace(p[1], () => p[0]); } }

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

// 4. O incremento (25/10/2026): um módulo já leve recebe só os remendos do 15º em diante e chega ao Codigo.gs atual.
const ja = 14, todos = remendos();
let antigo = codigo;
for (const p of todos.slice(ja).reverse()) { ok(antigo.split(p[1]).length === 2, 'remendo novo ambíguo no Codigo.gs'); antigo = antigo.replace(p[1], () => p[0]); }
ok(aplicarIncremento('var R53_PACOTE_LEVE_ = true;\n' + antigo, todos, ja) === 'var R53_PACOTE_LEVE_ = true;\n' + codigo, 'incremento não reproduz o Codigo.gs');
let recusa = null; try { aplicarIncremento(antigo, todos, ja); } catch (e) { recusa = e; }
ok(recusa && /não é o pacote leve/.test(recusa.message), 'incremento aceitou módulo que não é leve');
recusa = null; try { aplicarIncremento('var R53_PACOTE_LEVE_ = true;\n' + codigo, todos, ja); } catch (e) { recusa = e; }
ok(recusa && /âncora encontrada 0 vez/.test(recusa.message), 'incremento aplicado duas vezes');

// 5. O segundo incremento (26/10/2026): o módulo leve da cópia de teste já tem até o 22º e recebe do 23º em diante.
const ja2 = 22;
let antigo2 = codigo;
for (const p of todos.slice(ja2).reverse()) { ok(antigo2.split(p[1]).length === 2, 'remendo ' + ja2 + '+ ambíguo no Codigo.gs'); antigo2 = antigo2.replace(p[1], () => p[0]); }
ok(aplicarIncremento('var R53_PACOTE_LEVE_ = true;\n' + antigo2, todos, ja2) === 'var R53_PACOTE_LEVE_ = true;\n' + codigo, 'segundo incremento não reproduz o Codigo.gs');

console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'remendos no Codigo.gs, incremento num módulo já leve, corte da montagem, travas da montagem e correções sem executar texto; o hash do pacote instalado só é conferido no Google.' }));
