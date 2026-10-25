'use strict';
// Preparo local sem rede: entrega exatamente o carregador ensaiado na C.
// O preparador geral só serve para provar que o restante deriva da oficial.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const crypto = require('crypto');
const {preparar} = require('./preparar_loader');
const sha = s => crypto.createHash('sha256').update(s).digest('hex');
function body(s, name) {
  const start = s.indexOf('function ' + name + '(');
  assert(start >= 0, name + ' ausente');
  const end = s.indexOf('\n}', start);
  // Funções empacotadas ficam numa única linha, inclusive o fechamento.
  const lineEnd = s.indexOf('\n', start);
  if (name === 'r53CorrecaoAndroid_' || name === 'r53PaletaLeve_')
    return s.slice(start, lineEnd < 0 ? s.length : lineEnd);
  assert(end > start, name + ' incompleta');
  return s.slice(start, end + 2);
}
function prepararPromocao(before, reference) {
  assert.strictEqual(sha(reference), '6112c6cf4ff34c88cea6c944b55aaf62a878e2310bb502b2ac5d2131f2d57e80', 'Referência C divergente');
  assert(!reference.includes('concluirEnsaioPaletaC'));
  const proposed = preparar(before);
  const allowed = ['r53CorrecaoAndroid_', 'otimizarAnaliseAndroid', 'r53PaletaLeve_'];
  const mask = text => allowed.reduce((s,n) => s.replace(body(s,n), '// REFERENCIA ' + n), text).trim();
  assert.strictEqual(mask(proposed), mask(reference), 'Diferença fora dos três corpos conhecidos');
  new vm.Script(reference);
  let menus = 0, appearances = 0, pending = false;
  const ctx = {PropertiesService:{getDocumentProperties:()=>({getProperty:()=>pending?'tema':null})}};
  vm.createContext(ctx); vm.runInContext(reference, ctx);
  ctx.r53Modulo_ = () => {throw Error('Carregou catálogos na abertura');};
  ctx.salarioAbrir_ = () => menus++; ctx.r53Menu_ = () => menus++;
  ctx.r53PaletaLeve_ = () => ({continuar:()=>appearances++});
  ctx.onOpen({}); assert.strictEqual(menus,2); assert.strictEqual(appearances,0);
  pending=true;ctx.onOpen({});assert.strictEqual(menus,4);assert.strictEqual(appearances,1);
  return {code:reference,manifest:{oficial_sha256:sha(before),proposta_sha256:sha(reference),
    caracteres:reference.length,paleta_da_C_preservada:true,abertura_leve:true,
    limite:'Validação local; exige instalar e reler na cópia nativa antes de promover.'}};
}
if(require.main===module){
  const [input,reference,output] = process.argv.slice(2);
  if(!input||!reference||!output)throw Error('Informe oficial, referência C e saída privada');
  const result=prepararPromocao(fs.readFileSync(input,'utf8'),fs.readFileSync(reference,'utf8'));
  fs.writeFileSync(output,result.code,{flag:'wx'});
  fs.writeFileSync(output+'.manifesto.json',JSON.stringify(result.manifest,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify(result.manifest));
}
module.exports={prepararPromocao};
