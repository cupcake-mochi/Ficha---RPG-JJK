'use strict';
// Incremento somente no carregador já corrigido de salários, sem regravar os
// cinco catálogos, executar construir/continuar ou mudar acionadores.
const fs=require('fs'),vm=require('vm');
function preparar(before) {
 const marker='// ANDROID: constantes da ANALISE';
 if(before.includes(marker))throw Error('Carregador Android já aplicado');
 const anchor='R53_MODULO_=(new Function(r53CorrecaoAbertura_(code)))();';
 if(before.split(anchor).length!==2 || !before.includes("hash!=='2f153f659f714a7e5d16e483832f0bd4914bb93175f0527d97c7d20a03c2b110'"))throw Error('Carregador/base divergente');
 const source=fs.readFileSync('apps-script/Codigo.gs','utf8');
 const at=source.indexOf('    // Endereços fixos da exportação continuam restauráveis');
 const end=source.indexOf('    if (REFERENCIA_PURA_.test(t[2])) {',at);
 if(at<0||end<0)throw Error('Correção fonte ausente');
 const old='    var cel = aba.getRange(t[0], t[1]);\n    if (REFERENCIA_PURA_.test(t[2])) {';
 const replacement='    var cel = aba.getRange(t[0], t[1]);\n'+source.slice(at,end)+'    if (REFERENCIA_PURA_.test(t[2])) {';
 const budget="e && typeof e.r53Inicio_ === 'number' ? e.r53Inicio_ : Date.now()";
 const patches=[[old,replacement],
  ['function onEdit(e) {\n  var inicio = Date.now();','function onEdit(e) {\n  var inicio = '+budget+';'],
  ['function onOpen(e) {\n  var inicio = Date.now();','function onOpen(e) {\n  var inicio = '+budget+';'],
  ["  if (typeof r53Editar_ === 'function' && r53Editar_(e)) return;\n  // A troca de paleta",'  // A troca de paleta'],
  ['  // 01/10/2026: a FICHA PESSOAL tem as caixas de treino',"  if (typeof r53Editar_ === 'function' && r53Editar_(e)) return;\n  // 01/10/2026: a FICHA PESSOAL tem as caixas de treino"],
  ['continuarPaleta_(Date.now(), null, false, e && e.range);','continuarPaleta_('+budget+', null, false, e && e.range);'],
  ['continuarPaleta_(inicio, e.oldValue, true);','continuarPaleta_(inicio, e.oldValue, true, null, e.value);'],
  ['  var alvo = ss.getRangeByName(NOME_CEL_PALETA_);\n  var novo = alvo ? nomeCanonicoDaPaleta_(alvo.getCell(1, 1).getValue()) : \'\';',
   "  var novo = nomeCanonicoDaPaleta_(props.getProperty(PROP_PENDENTE_));\n  if (!coresDoNome_(novo)) {\n    var alvo = ss.getRangeByName(NOME_CEL_PALETA_);\n    novo = alvo ? nomeCanonicoDaPaleta_(alvo.getCell(1, 1).getValue()) : '';\n  }"],
  ["  if (!agora) { props.deleteProperty(PROP_PENDENTE_); return null; }", "  if (!agora) { props.deleteProperty(PROP_PENDENTE_); return null; }\n  props.setProperty(PROP_PENDENTE_, novo);"],
  ["  if (nomeCanonicoDaPaleta_(alvo.getCell(1, 1).getValue()) !== novo) {\n    props.setProperty(PROP_PENDENTE_, '1');", "  var escolhaFinal = ss.getRangeByName(NOME_CEL_PALETA_);\n  var pedidoFinal = escolhaFinal ? nomeCanonicoDaPaleta_(escolhaFinal.getCell(1, 1).getValue()) : '';\n  if (pedidoFinal !== novo) {\n    props.setProperty(PROP_PENDENTE_, pedidoFinal || '1');"],
  ['function continuarPaleta_(inicio, dica, marcar, onde) {','function continuarPaleta_(inicio, dica, marcar, onde, escolha) {'],
  ["    if (marcar) props.setProperty(PROP_PENDENTE_, '1');", "    if (marcar) props.setProperty(PROP_PENDENTE_, coresDoNome_(escolha) ? nomeCanonicoDaPaleta_(escolha) : '1');"],
  ['var CELULAS_POR_PASSO_ = 7500;','var CELULAS_POR_PASSO_ = 3500;'],
  ['spec.rows * spec.cols > 4 * CELULAS_POR_PASSO_', 'spec.rows * spec.cols > 30000'],
  ['function trechosDaAba_(spec) {\n  var n = spec.rows * spec.cols;\n  if (n <= CELULAS_POR_PASSO_) return null;\n  var k = Math.ceil(n / CELULAS_POR_PASSO_), por = Math.ceil(spec.rows / k), out = [];',
   "function trechosDaAba_(spec) {\n  var limite = spec.nome === 'CARTEIRA' ? 1500 : CELULAS_POR_PASSO_;\n  var n = spec.rows * spec.cols;\n  if (n <= limite) return null;\n  var k = Math.ceil(n / limite), por = Math.ceil(spec.rows / k), out = [];"]];
 // As três funções de paleta ficam idênticas à fonte atual, inclusive a leitura
 // das propriedades em lote. A origem é fixa e pública; nenhuma função nativa
 // é substituída sem conferir o corpo anterior inteiro.
 let original=require('child_process').execFileSync('git',['show','fbd6d156602958dc0f9da467a4a80100ad7b913f:apps-script/Codigo.gs'],{encoding:'utf8'});
 patches.forEach(([a,b])=>{if(original.split(a).length!==2)throw Error('Base de correção divergente');original=original.replace(a,b);});
 const body=(text,name)=>{const start=text.indexOf('function '+name+'('),end=text.indexOf('\n}',start);if(start<0||end<0)throw Error('Função ausente: '+name);return text.slice(start,end+2);};
 for(const name of ['convergirPaleta_','continuarPaleta_','trechosDaAba_','estimativaDoPasso_']){
  const beforeBody=body(original,name),afterBody=body(source,name);
  if(beforeBody!==afterBody)patches.push([beforeBody,afterBody]);
 }
 const patch='\n'+marker+'\nfunction r53CorrecaoAndroid_(code){var patches='+JSON.stringify(patches)+';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção Android: âncora divergente");code=code.replace(p[0],p[1]);});return code;}\n';
 let result=before.replace(anchor,'R53_MODULO_=(new Function(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code))))();');
 const wrappers=[['function onEdit(e){','function onEdit(e){if(e)e.r53Inicio_=Date.now();'],
  ['function onSelectionChange(e) {','function onSelectionChange(e) {\n if(e)e.r53Inicio_=Date.now();'],
  ['function onOpen(){return r53Modulo_()["onOpen"].apply(this,arguments);}', 'function onOpen(e){e=e||{};e.r53Inicio_=Date.now();return r53Modulo_().onOpen(e);}']];
 wrappers.forEach(([a,b])=>{if(result.split(a).length!==2)throw Error('Entrada pública divergente: '+a);result=result.replace(a,b);});
 const editor='if(typeof r53Editar_==="function" && r53Editar_(e))return;';
 if(result.split(editor).length!==2)throw Error('Entrada de cartões divergente');
 result=result.replace(editor,'if(e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27")return r53Modulo_().onEdit(e);'+editor);
 result=result.replace('return r53Modulo_().onEdit(e);'+editor,'return r53PaletaLeve_().trocar(e);'+editor);
 result=result.replace('if(pending || opening)return r53Modulo_().onSelectionChange(e);','if(opening)return r53Modulo_().onSelectionChange(e);\n if(pending)r53PaletaLeve_().continuar(e);');
 result=result.replace('function onOpen(e){e=e||{};e.r53Inicio_=Date.now();return r53Modulo_().onOpen(e);}',
  'function onOpen(e){e=e||{};e.r53Inicio_=Date.now();if(typeof salarioAbrir_==="function")salarioAbrir_();if(typeof r53Menu_==="function")r53Menu_();if(PropertiesService.getDocumentProperties().getProperty("paleta_pendente"))r53PaletaLeve_().continuar(e);}');
 result+=patch+fs.readFileSync('apps-script/Android.gs','utf8')+fs.readFileSync('apps-script/PaletaAndroid.gs','utf8');
 new vm.Script(result);
 return result;
}
if(require.main===module){const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Informe entrada e saída');const result=preparar(fs.readFileSync(input,'utf8'));fs.writeFileSync(output,result);console.log(JSON.stringify({bytes:Buffer.byteLength(result),destino:output}));}
module.exports={preparar};
