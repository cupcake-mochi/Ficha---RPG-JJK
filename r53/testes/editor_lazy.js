'use strict';
const fs=require('fs'),vm=require('vm'),z=require('zlib'),crypto=require('crypto'),assert=require('assert');
const {preparar}=require('../editor_lazy'),src=fs.readFileSync('apps-script/EditorR53.gs','utf8'),d=preparar(src);
const box={};vm.createContext(box);vm.runInContext(d.code,box);assert.strictEqual(box.R53_EDITOR_CACHE_,undefined);
let loads=0;box.Utilities={DigestAlgorithm:{SHA_256:1},Charset:{UTF_8:1},base64Decode:s=>Buffer.from(s,'base64'),newBlob:x=>x,ungzip:x=>{loads++;return{getDataAsString:()=>z.gunzipSync(x).toString('utf8')};},computeDigest:(_,s)=>Array.from(crypto.createHash('sha256').update(s).digest())};
assert.strictEqual(box.R53_EDITOR_.esquema,3);assert.strictEqual(loads,1);assert.strictEqual(JSON.stringify(box.R53_EDITOR_),d.json);assert.strictEqual(loads,1);
const keys=Object.keys(box.R53_EDITOR_);assert(keys.includes('contextos'));assert.strictEqual(box.R53_EDITOR_.contextos.length,249);
assert.throws(()=>preparar(d.code),/já preparado/);
console.log('Editor: inicialização sem serviços, catálogo completo igual e carga única aprovados.');
