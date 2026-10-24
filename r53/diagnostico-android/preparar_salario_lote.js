'use strict';
// Monta o teste do fechamento de salário em lote para uma cópia descartável: SalarioLote.gs e a chamada no início do
// onEdit. Não executa nada na planilha.
// Uso: node r53/diagnostico-android/preparar_salario_lote.js <conteúdo do projeto .json> <saída .json>
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const ANCORA = 'function onEdit(e){if(e)e.r53Inicio_=Date.now();';
const NOVO = ANCORA + 'if(typeof r53SalarioLote_==="function"&&r53SalarioLote_(e))return;';
function preparar(conteudo) {
  const fonte = fs.readFileSync(path.join(__dirname, 'salario_lote.gs'), 'utf8');
  new vm.Script(fonte);
  const files = conteudo.files.map(f => Object.assign({}, f));
  if (files.some(f => f.name === 'SalarioLote')) throw Error('SalarioLote já instalado');
  const cod = files.find(f => f.name === 'Codigo');
  if (cod.source.split(ANCORA).length !== 2) throw Error('Âncora do onEdit divergente');
  cod.source = cod.source.replace(ANCORA, () => NOVO);
  files.push({name: 'SalarioLote', type: 'SERVER_JS', source: fonte});
  return {files, sha: crypto.createHash('sha256').update(fonte).digest('hex')};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  const r = preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')));
  fs.writeFileSync(saida, JSON.stringify({files: r.files}));
  console.log(JSON.stringify({arquivos: r.files.length, sha: r.sha}));
}
module.exports = {preparar, ANCORA, NOVO};
