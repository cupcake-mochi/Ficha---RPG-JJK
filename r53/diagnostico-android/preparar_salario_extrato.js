'use strict';
// Atualiza um projeto que já tem o salário por fórmula: caixa ± GASTO / GANHO, extrato e últimos créditos.
// Troca o bloco "Salário por fórmula" inteiro pelo do Salarios.gs e acrescenta o desvio no salarioEditar_.
// Recusa se o bloco já estiver igual ou se alguma âncora não aparece exatamente uma vez. Não publica nada.
// Uso: node r53/diagnostico-android/preparar_salario_extrato.js <conteúdo .json> <saída .json>
// Depois de publicar, rode prepararSalarioLote() pelo editor: ele cria o EXTRATO com o saldo de O86.
const fs = require('fs'), vm = require('vm');
const {PARES, BLOCO} = require('./preparar_salario_formula.js');
const DESVIOS = PARES.slice(-3);
const FIM = 'function atualizarSalarioFormula() {';
function preparar(conteudo) {
  const files = conteudo.files.map(f => Object.assign({}, f));
  const cod = files.filter(f => /var SALARIO_ = \{/.test(f.source || ''));
  if (cod.length !== 1) throw Error('Módulo de salários ausente ou duplicado');
  let s = cod[0].source;
  if (s.includes(BLOCO.replace(/\n+$/, ''))) throw Error('Bloco já atualizado');
  if (!s.includes('SALARIO_.formula = true;')) throw Error('Instale antes o salário por fórmula');
  const ini = s.indexOf('\n/** Salário por fórmula'), f = s.indexOf(FIM);
  if (ini < 0 || f < ini || s.indexOf('\n/** Salário por fórmula', ini + 1) >= 0 || s.indexOf(FIM, f + 1) >= 0) throw Error('Bloco por fórmula divergente');
  // O bloco termina no marcador; versões antigas, no fim do salarioGasto_ ou na linha do atualizarSalarioFormula.
  const MARCA = '// FIM DO SALÁRIO POR FÓRMULA', gasto = s.indexOf('function salarioGasto_(');
  let fimLinha;
  if (s.includes(MARCA)) fimLinha = s.indexOf('\n', s.indexOf(MARCA));
  else if (gasto >= 0) fimLinha = s.indexOf('\n}', gasto) + 2;
  else fimLinha = s.indexOf('\n', f);
  if (s.lastIndexOf('function salarioGasto_(') !== gasto) throw Error('salarioGasto_ duplicado');
  s = s.slice(0, ini) + BLOCO.replace(/\n+$/, '') + (fimLinha < 0 ? '' : s.slice(fimLinha));
  for (const [de, para] of DESVIOS) {
    // Já instalado: a linha que o par acrescenta (a primeira que não existia antes) está lá.
    const nova = para.split('\n').find(l => !de.includes(l));
    if (s.includes(nova)) continue;
    if (s.split(de).length !== 2) throw Error('Âncora divergente: ' + de.slice(0, 60));
    s = s.replace(de, () => para);
  }
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
