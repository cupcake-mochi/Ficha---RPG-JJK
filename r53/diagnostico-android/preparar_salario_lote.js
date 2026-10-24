'use strict';
// Monta o teste do fechamento de salário em lote para uma cópia descartável: SalarioLote.gs e a chamada no início do
// onEdit. Não executa nada na planilha.
// Uso: node r53/diagnostico-android/preparar_salario_lote.js <conteúdo do projeto .json> <saída .json>
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const ANCORA = 'function onEdit(e){if(e)e.r53Inicio_=Date.now();';
const ANTIGO = ANCORA + 'if(typeof r53SalarioLote_==="function"&&r53SalarioLote_(e))return;';
const NOVO = 'function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();';
const ENTRADA = '\nfunction onEdit(e){return r53SalarioOnEdit_(e);}\n';
const SHA_ANTERIOR = '6d0f7356db93b7ef721a51e0e397b5d607e0d08b6c1f1b43a4e9ff359bfa1232'; // a2ca590
function preparar(conteudo) {
  const fonte = fs.readFileSync(path.join(__dirname, 'salario_lote.gs'), 'utf8');
  new vm.Script(fonte);
  const files = conteudo.files.map(f => Object.assign({}, f));
  const anteriores = files.filter(f => f.name === 'SalarioLote');
  if (anteriores.length > 1) throw Error('SalarioLote duplicado');
  const cod = files.find(f => f.name === 'Codigo');
  if (!cod || files.filter(f => f.name === 'Codigo').length !== 1) throw Error('Codigo ausente ou duplicado');
  if (cod.source.includes('r53OnEditOriginal_') || cod.source.includes('r53SalarioOnEdit_')) throw Error('Integração nova já instalada');
  if (anteriores.length) {
    // Atualiza somente a experiência anterior conhecida; nunca anexa dois fechadores.
    const hash = crypto.createHash('sha256').update(anteriores[0].source).digest('hex');
    if (hash !== SHA_ANTERIOR || cod.source.split(ANTIGO).length !== 2) throw Error('Experiência salarial divergente');
    cod.source = cod.source.replace(ANTIGO, () => ANCORA);
  } else if (cod.source.includes('r53SalarioLote_(e)')) throw Error('Chamada salarial sem módulo');
  if (cod.source.split(ANCORA).length !== 2) throw Error('Âncora do onEdit divergente');
  cod.source = cod.source.replace(ANCORA, () => NOVO) + ENTRADA;
  new vm.Script(cod.source);
  if (anteriores.length) anteriores[0].source = fonte;
  else files.push({name: 'SalarioLote', type: 'SERVER_JS', source: fonte});
  return {files, sha: crypto.createHash('sha256').update(fonte).digest('hex')};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  const r = preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')));
  fs.writeFileSync(saida, JSON.stringify({files: r.files}));
  console.log(JSON.stringify({arquivos: r.files.length, sha: r.sha}));
}
module.exports = {preparar, ANCORA, NOVO, ANTIGO, ENTRADA};
