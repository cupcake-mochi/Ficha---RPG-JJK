'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto'),z=require('zlib');
const data=require('../paleta_leve.js').gerar();
const ctx={};vm.createContext(ctx);vm.runInContext(require('../../medidas/carregar-ficha.js').fontes(),ctx);vm.runInContext(fs.readFileSync('apps-script/Codigo.gs','utf8'),ctx);
const expected=ctx.ABAS.filter(s=>!s.oculta&&!s.paleta_fixa);
assert.strictEqual(data.tabs.length,expected.length);
const light={};vm.createContext(light);
vm.runInContext('var lightModule_=(function(){'+data.code.replace('return {trocar:', 'return {grade:gradeDeFabrica_,enfeites:celulasDeEnfeite_,avisos:celulasDeAviso_,passos:passosDaPaleta_,trocar:')+'})();',light);
const equal=(a,b)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b));
for(const full of expected){const small=data.tabs.find(s=>s.nome===full.nome);equal(ctx.gradeDeFabrica_(full),light.lightModule_.grade(small));equal(ctx.celulasDeEnfeite_(full),light.lightModule_.enfeites(small));equal(ctx.celulasDeAviso_(full),light.lightModule_.avisos(small));}
equal(ctx.passosDaPaleta_('CARTEIRA'),light.lightModule_.passos('CARTEIRA'));
equal(ctx.ARTE && Object.fromEntries(Object.keys(light.lightModule_.__arte).map(k=>[k,ctx.ARTE[k]])),light.lightModule_.__arte);
// O caminho leve não carrega o módulo de regras, nem chama o editor de cartões.
const pre=require('../diagnostico-android/preparar_loader.js').preparar;
const baseline=fs.readFileSync('r53/testes/carregador-fixture.gs','utf8');
let loaded=0,paint=0,continued=0,menu=0;
const runtime={console,PropertiesService:{getDocumentProperties:()=>({getProperty:()=> 'Noite · Claro'})}};
vm.createContext(runtime);vm.runInContext(pre(baseline),runtime);
runtime.r53Modulo_=()=>{loaded++;throw Error('Módulo pesado não deve carregar');};
runtime.r53PaletaLeve_=()=>({trocar(){paint++;},continuar(){continued++;}});
runtime.salarioEditar_=()=>false;runtime.r53Editar_=()=>{throw Error('Editor de cartões não deve rodar');};
runtime.salarioAbrir_=()=>{menu++;};runtime.r53Menu_=()=>{menu++;};
const event={value:'Noite · Claro',range:{getSheet:()=>({getName:()=> 'CARTEIRA'}),getA1Notation:()=> 'C27'}};
runtime.onEdit(event);runtime.onSelectionChange(event);runtime.onOpen({});
assert.strictEqual(loaded,0);assert.strictEqual(paint,1);assert.strictEqual(continued,2);assert.strictEqual(menu,2);
console.log(JSON.stringify({resultado:'OK',abas:expected.length,grade_cores_igual:true,arte_igual:true,fila_igual:true,carga_regras_no_caminho_leve:loaded,bytes_modulo:data.bytes,bytes_transporte:data.transport}));
