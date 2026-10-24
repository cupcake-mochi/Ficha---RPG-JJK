'use strict';
// Leva a caixa ± GASTO / GANHO (extrato de ienes) a um projeto que já tem o salário por fórmula.
// Troca o bloco "Salário por fórmula" inteiro pelo do Salarios.gs e acrescenta o desvio no salarioEditar_.
// Recusa se já estiver instalado ou se alguma âncora não aparece exatamente uma vez. Não publica nada.
// Uso: node r53/diagnostico-android/preparar_salario_extrato.js <conteúdo .json> <saída .json>
// Depois de publicar, rode prepararSalarioLote() pelo editor: ele cria o EXTRATO com o saldo de O86.
const fs = require('fs'), vm = require('vm');
const {PARES, BLOCO} = require('./preparar_salario_formula.js');
const DESVIO = PARES[PARES.length - 1];
const FIM = 'function atualizarSalarioFormula() {';
function preparar(conteudo) {
  const files = conteudo.files.map(f => Object.assign({}, f));
  const cod = files.filter(f => /var SALARIO_ = \{/.test(f.source || ''));
  if (cod.length !== 1) throw Error('Módulo de salários ausente ou duplicado');
  let s = cod[0].source;
  if (s.includes('salarioGasto_')) throw Error('Extrato já instalado');
  if (!s.includes('SALARIO_.formula = true;')) throw Error('Instale antes o salário por fórmula');
  const ini = s.indexOf('\n/** Salário por fórmula'), f = s.indexOf(FIM);
  if (ini < 0 || f < ini || s.indexOf('\n/** Salário por fórmula', ini + 1) >= 0 || s.indexOf(FIM, f + 1) >= 0) throw Error('Bloco por fórmula divergente');
  const fimLinha = s.indexOf('\n', f);
  s = s.slice(0, ini) + BLOCO.replace(/\n+$/, '') + (fimLinha < 0 ? '' : s.slice(fimLinha));
  if (s.split(DESVIO[0]).length !== 2) throw Error('Âncora divergente: ' + DESVIO[0].slice(0, 60));
  s = s.replace(DESVIO[0], () => DESVIO[1]);
  new vm.Script(s);
  cod[0].source = s;
  return {files};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  fs.writeFileSync(saida, JSON.stringify(preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')))));
  console.log('ok');
}
module.exports = {preparar};
