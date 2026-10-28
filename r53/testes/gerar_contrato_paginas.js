'use strict';
// Amostra sintética do protocolo produzida pelas funções reais em VM, sem rede.
const fs=require('fs'),path=require('path');
function texto(){
 const a=require('./inicializacao_conferencia_paginas').ambiente(),plano=a.plano();
 return JSON.stringify({assinaturaSequencia:a.p.assinatura,plano:plano,paginas:[a.pagina(plano,0)]},null,2)+'\n';
}
if(require.main===module){
 const file=path.resolve(__dirname,'fixtures/conferencia_paginas_v1.json'),s=texto();
 if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==s)throw Error('Amostra do protocolo divergente.');process.stdout.write('Amostra sintética igual às funções do produtor.\n');}
 else{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,s);}
}
module.exports={texto};
