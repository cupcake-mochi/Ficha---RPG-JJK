'use strict';
// Conferência do transporte gerado; não abre nem escreve planilhas.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const {fontes}=require('../../medidas/carregar-ficha');
const ctx={console};vm.createContext(ctx);vm.runInContext(fontes(),ctx);
assert.deepStrictEqual(Array.from(ctx.SOBRAS_),[]);
let formulas=0,max=0,efeitos=0,avisos=0;
for(const sheet of ctx.ABAS){
 // As abas-base da Ficha.gs usam GERACAO_ global; suplementos têm a tag local.
 if(sheet.geracao!==undefined)assert.strictEqual(sheet.geracao,ctx.GERACAO_);
 for(const [row,col,value] of sheet.vals){
  if(typeof value!=='string'||!value.startsWith('='))continue;
  formulas++;max=Math.max(max,value.length);
  assert(value.length<=32767,`${sheet.nome}!${row}:${col}: limite de texto`);
  if(sheet.nome==='DADOS_R53'&&(col===160||col===180)){
   assert(value.includes('LET('),'compactação ausente');
   let depth=0,quoted=false;
   for(let i=0;i<value.length;i++){
    const char=value[i];
    if(char==='"'){if(quoted&&value[i+1]==='"'){i++;continue;}quoted=!quoted;}
    else if(!quoted){if(char==='(')depth++;if(char===')')depth--;assert(depth>=0,'parêntese sem abertura');}
   }
   assert(!quoted&&depth===0,'fórmula incompleta');
   if(col===160)efeitos++;else avisos++;
  }
 }
}
assert(efeitos>0&&avisos>0);
const result={resultado:'OK',geracao:ctx.GERACAO_,abas:ctx.ABAS.length,
 formulas_transportadas:formulas,maior_formula_caracteres:max,
 moldes_efeitos:efeitos,moldes_avisos:avisos,geracoes_misturadas:0,
 limite:'Confere fontes e moldes antes das cópias abaixo; não reconstrói ficha preenchida nem substitui teste nativo.'};
fs.writeFileSync(path.join(__dirname,'GERACAO-INTEGRAL-2026-10-23.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
