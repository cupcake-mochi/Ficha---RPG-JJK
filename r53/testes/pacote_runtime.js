'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),z=require('zlib'),crypto=require('crypto'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'r53/saidas/pacote-script');
const m=JSON.parse(fs.readFileSync(path.join(out,'manifesto.json')));
function hash(v){return crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');}
function context(){const c={console,Utilities:{DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},base64Decode:s=>Buffer.from(s,'base64'),newBlob:b=>b,ungzip:b=>({getDataAsString:()=>z.gunzipSync(b).toString('utf8')}),computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest())}};vm.createContext(c);return c;}
let plain=context();vm.runInContext(m.geracao_arquivos.map(n=>fs.readFileSync(path.join(root,'apps-script',n),'utf8')).join('\n'),plain);
const expected=hash(plain.ABAS),gen=plain.GERACAO_;assert.deepStrictEqual(Array.from(plain.SOBRAS_),[]);
let bundle=context();for(const name of Object.keys(m.arquivos))vm.runInContext(fs.readFileSync(path.join(out,name),'utf8'),bundle);
// Prova de autonomia antes de carregar qualquer arquivo legado.
let standalone=vm.runInContext('r53Modulo_().__estado()',bundle);
assert.strictEqual(hash(standalone.abas),expected);assert.strictEqual(standalone.geracao,gen);
assert.deepStrictEqual(Array.from(standalone.sobras),[]);assert.strictEqual(standalone.editor.contextos.length,249);
for(const name of m.geracao_arquivos.filter(n=>!m.arquivos[n]))vm.runInContext(fs.readFileSync(path.join(root,'apps-script',name),'utf8'),bundle);
let state=vm.runInContext('r53Modulo_().__estado()',bundle);
assert.strictEqual(hash(state.abas),expected);assert.strictEqual(state.geracao,gen);assert.deepStrictEqual(Array.from(state.sobras),[]);assert.strictEqual(state.editor.contextos.length,249);
for(const name of m.entradas_publicas)assert.strictEqual(vm.runInContext('typeof '+name,bundle),'function');
assert.strictEqual(vm.runInContext('r53Modulo_()===r53Modulo_()',bundle),true);
// Um clique comum não carrega as tabelas; os dois comportamentos originais
// continuam delegados: abrir uma invocação e concluir a troca de paleta.
let fast=context(),pending=false,calls=0;
fast.PropertiesService={getDocumentProperties:()=>({getProperty:()=>pending?'1':null})};
vm.runInContext(fs.readFileSync(path.join(out,'Codigo.gs'),'utf8'),fast);
fast.R53_MODULO_={onSelectionChange(){calls++;}};
function select(name,address){fast.onSelectionChange({range:{getA1Notation:()=>address,getSheet:()=>({getName:()=>name})}});}
select('FICHA AMALDIÇOADA','AE4');assert.strictEqual(calls,0);
const inv=plain.ABAS.find(a=>a.nome==='INVOCAÇÕES');
assert.deepStrictEqual(Array.from(fast.R53_NAVEGACAO_.alvos),Array.from(inv.abrir,a=>a[0]));
select('INVOCAÇÕES',inv.abrir[0][0]);assert.strictEqual(calls,1);
pending=true;select('FICHA AMALDIÇOADA','AE4');assert.strictEqual(calls,2);
assert.strictEqual(state.editor.esquema,3);assert.strictEqual(state.editor.contextos.every(g=>!g.abrir_editor&&Object.keys(g.entradas_diretas).length>0),true);
// Ordinary card edits use the standalone controller before loading the heavy module.
let edits=0,loaded=0;fast.r53Editar_=()=>{edits++;return true;};fast.R53_MODULO_.onEdit=()=>{loaded++;};fast.onEdit({});assert.strictEqual(edits,1);assert.strictEqual(loaded,0);
// Misturar/omitir uma parte deve falhar antes de executar a geração.
let broken=context();for(const name of Object.keys(m.arquivos))vm.runInContext(fs.readFileSync(path.join(out,name),'utf8'),broken);
vm.runInContext('R53_CODIGO_0_ = R53_CODIGO_0_.slice(9)',broken);assert.throws(()=>vm.runInContext('r53Modulo_()',broken));
console.log(JSON.stringify({resultado:'OK',arquivos:Object.keys(m.arquivos).length,entradas:m.entradas_publicas.length,abas:state.abas.length,cartoes:state.editor.contextos.length,hash_abas:expected,geracao:gen,escopo:'Empacotamento sem perda e falha fechada. Execução nativa ainda separada.'}));
