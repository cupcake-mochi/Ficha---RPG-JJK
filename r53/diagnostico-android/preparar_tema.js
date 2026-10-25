'use strict';
// Monta o pacote do teste de paleta por tema para uma cópia descartável: TemaPaleta.gs com as PALETAS da fonte,
// o desvio da CARTEIRA!C27 no onEdit e o serviço avançado do Sheets no manifesto. Não executa nada na planilha.
// Uso: node r53/diagnostico-android/preparar_tema.js <conteúdo do projeto .json> <saída .json>
const fs = require('fs'), vm = require('vm'), path = require('path'), crypto = require('crypto');
const root = path.resolve(__dirname, '../..');
const ANCORA = 'if(e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27")return r53PaletaLeve_().trocar(e);';
const NOVO = 'if(e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getA1Notation()==="C27"){if(r53TemaAtivo_(SpreadsheetApp.getActive()))return r53TemaTrocar_(e);return r53PaletaLeve_().trocar(e);}';
function paletas() {
  const src = fs.readFileSync(path.join(root, 'apps-script/Codigo.gs'), 'utf8');
  const i = src.indexOf('var PALETAS = ');
  let d = 0, j = src.indexOf('{', i);
  const s = j;
  for (;; j++) { if (src[j] === '{') d++; else if (src[j] === '}') { d--; if (!d) break; } }
  return JSON.parse(src.slice(s, j + 1));
}
function preparar(conteudo) {
  const tpl = fs.readFileSync(path.join(__dirname, 'tema_paleta.gs'), 'utf8');
  if (tpl.split('/*PALETAS*/null').length !== 2) throw Error('Marcador de PALETAS ausente');
  const tema = tpl.replace('/*PALETAS*/null', () => JSON.stringify(paletas()));
  new vm.Script(tema);
  const files = conteudo.files.map(f => Object.assign({}, f));
  if (files.some(f => f.name === 'TemaPaleta')) throw Error('TemaPaleta já instalado');
  const cod = files.find(f => f.name === 'Codigo');
  if (cod.source.split(ANCORA).length !== 2) throw Error('Âncora do onEdit divergente');
  cod.source = cod.source.replace(ANCORA, () => NOVO);
  const man = files.find(f => f.name === 'appsscript'), m = JSON.parse(man.source);
  m.dependencies = m.dependencies || {};
  m.dependencies.enabledAdvancedServices = [{userSymbol: 'Sheets', serviceId: 'sheets', version: 'v4'}];
  man.source = JSON.stringify(m, null, 2);
  files.push({name: 'TemaPaleta', type: 'SERVER_JS', source: tema});
  return {files, sha_tema: crypto.createHash('sha256').update(tema).digest('hex')};
}
if (require.main === module) {
  const [entrada, saida] = process.argv.slice(2);
  const r = preparar(JSON.parse(fs.readFileSync(entrada, 'utf8')));
  fs.writeFileSync(saida, JSON.stringify({files: r.files}));
  console.log(JSON.stringify({arquivos: r.files.length, sha_tema: r.sha_tema}));
}
module.exports = {preparar, ANCORA, NOVO};
