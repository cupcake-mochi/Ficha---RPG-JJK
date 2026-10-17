'use strict';
// Preservação de texto manual, atualização, limpeza e leituras delimitadas.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8');
const block=source.slice(source.indexOf('// B47 C+D: notas contextuais de tipo'),source.indexOf('// FIM DAS NOTAS CONTEXTUAIS B47'));
let reads=0,writes=0,flushes=0;
const notes={I43:'Nota manual · preservar 007',AB43:'Outra nota'},props={},texts=['DEFINIÇÃO\nTipo A','EFEITO E REQUISITOS\nTipo B'];
const ranges={};for(const a1 of Object.keys(notes))ranges[a1]={getNote:()=>notes[a1],setNote:t=>{writes++;notes[a1]=t;}};
const ss={getSheetByName:name=>name==='DADOS_ENTIDADES'?{getRange:(row,col,count,width)=>{
 assert.deepEqual([row,col,count,width],[2,42,2,1]);return{getDisplayValues:()=>{reads++;return texts.map(t=>[t]);}};
}}:name==='INVOCAÇÕES'?{getSheetId:()=>4,getRange:a1=>ranges[a1]}:null};
const ctx=vm.createContext({
 ABAS:[{nome:'INVOCAÇÕES',notas_contextuais:{fonte:'DADOS_ENTIDADES',coluna:42,primeira:2,destinos:['I43','AB43'],gatilhos:['B2390']}}],
 ABA_INVOCACOES_:'INVOCAÇÕES',SpreadsheetApp:{getActive:()=>ss,flush:()=>{flushes++;}},
 PropertiesService:{getDocumentProperties:()=>({getProperties:()=>({...props}),setProperties:p=>Object.assign(props,p),deleteProperty:k=>delete props[k]})},
 Utilities:{DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},computeDigest:(alg,t,charset)=>Array.from(crypto.createHash(alg).update(t,charset).digest())},
 tocaFaixa_:(r,a1)=>r.getA1Notation()===a1
});
vm.runInContext(block,ctx);
const event=(sheet,a1)=>({range:{getSheet:()=>({getName:()=>sheet}),getA1Notation:()=>a1}});
let checks=0;function check(name,fn){fn();checks++;console.log('OK '+name);}
check('edição alheia não lê nem escreve',()=>{assert.equal(ctx.notasDosTipos_(event('CONFIGURAÇÃO','B1')),0);assert.equal(reads,0);assert.equal(writes,0);});
check('seleção atualiza somente sua nota',()=>{assert.equal(ctx.notasDosTipos_(event('INVOCAÇÕES','I43')),1);assert.equal(notes.I43,'Nota manual · preservar 007\n\n'+texts[0]);assert.equal(notes.AB43,'Outra nota');assert.equal(reads,1);});
check('repetir é idempotente',()=>{assert.equal(ctx.notasDosTipos_(event('INVOCAÇÕES','I43')),0);assert.equal(writes,1);});
check('edição do cadastro atualiza todas as seleções com uma leitura',()=>{texts[0]='DEFINIÇÃO\nTipo novo';const before=reads;assert.equal(ctx.notasDosTipos_(event('CONFIGURAÇÃO','B2390')),2);assert.equal(reads-before,1);assert.equal(notes.I43,'Nota manual · preservar 007\n\n'+texts[0]);});
check('nota manual editada depois é preservada inteira',()=>{notes.I43+='\nMinha observação';const manual=notes.I43;texts[0]='Texto seguinte';ctx.notasDosTipos_(event('INVOCAÇÕES','I43'));assert.ok(notes.I43.startsWith(manual+'\n\n'));});
check('limpeza retira somente a última ajuda calculada',()=>{const estado=JSON.parse(props.b47_tipo_nota_4_I43),manual=notes.I43.slice(0,estado.tamanhoBase);texts[0]='';ctx.notasDosTipos_(event('INVOCAÇÕES','I43'));assert.equal(notes.I43,manual);assert.equal(props.b47_tipo_nota_4_I43,undefined);});
check('ajuda longa conserva a nota manual e aponta para o cadastro completo',()=>{const manual='Observação '.repeat(20),r=ctx.comporNotaContextual_(manual,null,'A'.repeat(20000));assert.ok(r.nota.startsWith(manual));assert.ok(r.nota.endsWith('Texto completo em CONFIGURAÇÃO.'));assert.ok(r.nota.length<45000);assert.ok(JSON.stringify(r.estado).length<150);});
check('estado adulterado não apaga texto',()=>{const r=ctx.comporNotaContextual_('Texto original',{hash:'inválido',tamanhoBase:0},'Ajuda');assert.equal(r.nota,'Texto original\n\nAjuda');});
check('abertura atualiza as notas sem ativação manual',()=>{texts[1]='Texto na cópia';assert.equal(ctx.notasDosTipos_(),1);assert.equal(notes.AB43,'Outra nota\n\nTexto na cópia');});
// 17/10/2026: a cópia da planilha não leva as propriedades do documento.
check('cópia sem propriedades não dobra a ajuda na abertura',()=>{for(const k of Object.keys(props))delete props[k];const antes=notes.AB43;ctx.notasDosTipos_();assert.equal(notes.AB43,antes);});
check('cópia que já dobrou a ajuda volta a ter uma só',()=>{for(const k of Object.keys(props))delete props[k];notes.AB43='Outra nota\n\n'+texts[1]+'\n\n'+texts[1];ctx.notasDosTipos_();assert.equal(notes.AB43,'Outra nota\n\n'+texts[1]);});
check('ajuda sozinha numa cópia continua sozinha',()=>{for(const k of Object.keys(props))delete props[k];notes.AB43=texts[1]+'\n\n'+texts[1];ctx.notasDosTipos_();assert.equal(notes.AB43,texts[1]);});
check('cópia que dobrou e já gravou estado também volta a ter uma só',()=>{for(const k of Object.keys(props))delete props[k];const dobrada='Outra nota\n\n'+texts[1]+'\n\n'+texts[1];notes.AB43=dobrada;props.b47_tipo_nota_4_AB43=JSON.stringify({hash:crypto.createHash('sha256').update(dobrada,'utf8').digest('hex'),tamanhoBase:('Outra nota\n\n'+texts[1]).length});ctx.notasDosTipos_();assert.equal(notes.AB43,'Outra nota\n\n'+texts[1]);});
console.log(JSON.stringify({resultado:'OK',checagens:checks,leituras:reads,escritas:writes,flushes,tipo:'VM; sem Google'}));
