'use strict';
// Leva o salário por fórmula a um projeto já instalado (Codigo com o Salarios.gs embutido + SalarioLote).
// Só troca trechos ancorados; recusa se alguma âncora não aparece exatamente uma vez. Não publica nada.
// Uso: node r53/diagnostico-android/preparar_salario_formula.js <conteúdo .json> <saída .json>
const fs = require('fs'), vm = require('vm'), path = require('path');
const raiz = path.resolve(__dirname, '../..');
const salarios = fs.readFileSync(path.join(raiz, 'apps-script/Salarios.gs'), 'utf8');
const BLOCO = salarios.slice(salarios.indexOf('\n/** Salário por fórmula'));
const PARES = [
  ["function salarioStatus_(ss,texto) {ss.getSheetByName(SALARIO_.config).getRange('O46').setValue(texto);}",
   "function salarioStatus_(ss,texto) {var c=ss.getSheetByName(SALARIO_.config).getRange('O46');if(SALARIO_.formula&&String(texto).charAt(0)!=='⚠')c.setFormula(SALARIO_.f.painel.O46);else c.setValue(texto);}"],
  ["  var formula='=O86+SUM(\\'SALÁRIOS\\'!J2:J)';",
   "  var formula=SALARIO_.formula?SALARIO_.f.total:'=O86+SUM(\\'SALÁRIOS\\'!J2:J)';"],
  ["function salarioApurar_(ss,hoje,cache) {\n  cache=cache||{};",
   "function salarioApurar_(ss,hoje,cache) {\n  cache=cache||{};\n  if(SALARIO_.formula){\n    var ms=cache.missoes||salarioSincronizar_(ss,cache.estado||salarioEstado_(ss),hoje,false,true);if(ms.gravar)ms.gravar();\n    SpreadsheetApp.flush();var feito=salarioCongelar_(ss,hoje);salarioStatus_(ss,'');return feito;\n  }"],
  ["      var cfg=ss.getSheetByName(SALARIO_.config),st=salarioEstado_(ss);\n      if(total)salarioLigacoes_(ss);\n      var controle=",
   "      // A troca vai antes de qualquer leitura: até ela chegar, a fórmula paga o passado com o valor novo.\n      var chave=SALARIO_.formula&&salarioChaveTroca_(r,n);\n      if(chave){salarioRegistrarTroca_(ss,chave,e);return;}\n      var cfg=ss.getSheetByName(SALARIO_.config),st=salarioEstado_(ss);\n      if(total)salarioLigacoes_(ss);\n      var controle="],
  ["        cfg.getRange('O48').setValue(salarioData_(dia+dias));cfg.getRange('O69').setValue(salarioData_(dia));",
   "        if(SALARIO_.formula){salarioStatus_(ss,'');return;}\n        cfg.getRange('O48').setValue(salarioData_(dia+dias));cfg.getRange('O69').setValue(salarioData_(dia));"],
  ["      var hoje=salarioHoje_();\n      if(missao&&!config){",
   "      var hoje=salarioHoje_();\n      // Por fórmula a edição só registra a missão; o pagamento já aparece na hora e o livro congela depois.\n      if(SALARIO_.formula){if(missao&&!config&&salarioToca_(r,15,87,49,72))salarioSincronizar_(ss,st,hoje,false);return;}\n      if(missao&&!config){"],
  ["  if(!config&&!missao&&!nome&&!total&&!emitir)return false;",
   "  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,86,87,15,21)&&salarioGasto_(ss,r,e))return true;\n  if(!config&&!missao&&!nome&&!total&&!emitir)return false;"],
  ["  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,86,87,15,21)&&salarioGasto_(ss,r,e))return true;\n",
   "  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,86,87,15,21)&&salarioGasto_(ss,r,e))return true;\n  if(SALARIO_.formula&&n==='FICHA PESSOAL'&&salarioToca_(r,10,12,61,71)&&salarioCorrigirData_(ss,r,e))return true;\n"],
];
function preparar(conteudo) {
  const files = conteudo.files.map(f => Object.assign({}, f));
  const cod = files.filter(f => /var SALARIO_ = \{/.test(f.source || ''));
  if (cod.length !== 1) throw Error('Módulo de salários ausente ou duplicado');
  let s = cod[0].source;
  if (s.includes('SALARIO_.formula')) throw Error('Salário por fórmula já instalado');
  for (const [a, b] of PARES) {
    if (s.split(a).length !== 2) throw Error('Âncora divergente: ' + a.slice(0, 60));
    s = s.replace(a, () => b);
  }
  // O bloco entra logo depois do painel, onde o Salarios.gs termina dentro do Codigo.
  const fim = s.indexOf('\n', s.indexOf("carteira.getRange('AT3').insertCheckboxes()"));
  const fimPainel = s.indexOf('\n}', fim) + 2;
  if (fim < 0 || fimPainel < 2) throw Error('Fim do painel não encontrado');
  s = s.slice(0, fimPainel) + BLOCO + s.slice(fimPainel);
  new vm.Script(s);
  cod[0].source = s;
  const lote = files.filter(f => f.name === 'SalarioLote');
  if (lote.length !== 1) throw Error('SalarioLote ausente ou duplicado');
  lote[0].source = fs.readFileSync(path.join(__dirname, 'salario_lote.gs'), 'utf8');
  new vm.Script(lote[0].source);
  return {files};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  fs.writeFileSync(saida, JSON.stringify(preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')))));
  console.log('ok');
}
module.exports = {preparar, PARES, BLOCO};
