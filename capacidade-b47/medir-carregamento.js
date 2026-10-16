// Medida local em VM, sem serviços Google. Cada repetição usa contexto novo.
const fs=require('fs'),vm=require('vm'),path=require('path');
const dir=process.argv[2]||path.join(__dirname,'../apps-script');
const files=fs.readdirSync(dir).filter(n=>n.endsWith('.gs')).sort();
const sources=files.map(n=>[n,fs.readFileSync(path.join(dir,n),'utf8')]);
const samples=[];
for(let i=0;i<5;i++){
  const ctx=vm.createContext({});const t=performance.now();const perFile={};
  for(const [n,src] of sources){const start=performance.now();vm.runInContext(src,ctx,{filename:n});perFile[n]=performance.now()-start;}
  samples.push({ms:performance.now()-t,por_arquivo_ms:perFile});
}
console.log(JSON.stringify({tipo:'simulação VM Node; não é Apps Script',node:process.version,arquivos:files.length,bytes:sources.reduce((s,[,v])=>s+Buffer.byteLength(v),0),amostras:samples},null,2));
