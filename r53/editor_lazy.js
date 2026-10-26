'use strict';
// O catálogo permanece igual; o evento só o materializa se consultar o editor.
const fs=require('fs'),z=require('zlib'),crypto=require('crypto');
function preparar(src){
 const m=/^var R53_EDITOR_ = (\{[^\n]+\});\n/.exec(src);if(!m)throw Error('Editor: catálogo ausente ou já preparado');
 const data=JSON.parse(m[1]),json=JSON.stringify(data),hash=crypto.createHash('sha256').update(json).digest('hex'),payload=z.gzipSync(json,{mtime:0}).toString('base64');
 const head='var R53_EDITOR_CACHE_;\nfunction r53ConfigEditor_(){if(R53_EDITOR_CACHE_)return R53_EDITOR_CACHE_;var text=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode('+JSON.stringify(payload)+'),"application/gzip")).getDataAsString("UTF-8");var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,text,Utilities.Charset.UTF_8).map(function(b){return ("0"+((b+256)%256).toString(16)).slice(-2);}).join("");if(hash!=='+JSON.stringify(hash)+')throw Error("Editor: catálogo divergente");return R53_EDITOR_CACHE_=JSON.parse(text);}\n'+
 'var R53_EDITOR_=new Proxy({}, {get:function(t,k){return r53ConfigEditor_()[k];},set:function(t,k,v){r53ConfigEditor_()[k]=v;return true;},ownKeys:function(){return Reflect.ownKeys(r53ConfigEditor_());},getOwnPropertyDescriptor:function(t,k){var d=Object.getOwnPropertyDescriptor(r53ConfigEditor_(),k);if(d)d.configurable=true;return d;}});\n';
 const code=head+src.slice(m[0].length);new Function(code);return {code,hash,json};
}
if(require.main===module){const[a,b]=process.argv.slice(2);if(!a||!b)throw Error('Uso: <Editor fonte> <Editor de transporte>');const d=preparar(fs.readFileSync(a,'utf8'));fs.writeFileSync(b,d.code);console.log(JSON.stringify({bytes:d.code.length,hash:d.hash}));}
module.exports={preparar};
