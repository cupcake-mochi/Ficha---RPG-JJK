'use strict';
// Restaura somente o limite calculado; nenhuma outra célula da DADOS é regravada.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const GUARDA="  if (typeof r53RestaurarCargaOrigem_ === 'function' && r53RestaurarCargaOrigem_(e)) {\n    continuarPaleta_(inicio, null, false, e.range);\n    return;\n  }\n";
function gerar(){
 const dados=require('./diagnostico-android/reserva_bolsa_plano.json').filter(d=>d.aba==='DADOS'&&d.r===41&&d.c===104);
 if(dados.length!==1)throw Error('Endereço do limite de carga mudou');
 const formula=dados[0].depois;
 if(!formula?.startsWith('=LET(cargaOrigem,'))throw Error('Fórmula do limite divergente');
 // Confere as tuplas emitidas sem inicializar novamente todo o modelo (20 MB).
 const fontes=require('../medidas/carregar-ficha').fontes();
 for(const v of [[41,103,'limite de carga'],[41,104,formula]])if(fontes.split(JSON.stringify(v).slice(0,-1)+',').length!==2)throw Error('Plano e fonte do limite divergentes');
 const src=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8'),a=src.indexOf('function formulaNoIdioma_('),b=src.indexOf('\n}',a);
 if(a<0||b<0)throw Error('Conversor de idioma ausente');
 const idioma=src.slice(a,b+2).replace('function formulaNoIdioma_(','function r53CargaFormulaNoIdioma_(');
 const output='// GERADO por r53/reserva_bolsa_restaurar.js; somente DADOS!CZ41.\nvar R53_CARGA_ORIGEM_FORMULA_='+JSON.stringify(formula)+';\n'+idioma+`\nfunction r53RestaurarCargaOrigem_(e){
 if(!e||!e.range)return false;var r=e.range;
 if(r.getRow()>41||r.getLastRow()<41||r.getColumn()>104||r.getLastColumn()<104||r.getSheet().getName()!=='DADOS')return false;
 var sheet=r.getSheet(),cel=sheet.getRange(41,104),formula=r53CargaFormulaNoIdioma_(R53_CARGA_ORIGEM_FORMULA_,sheet.getParent().getSpreadsheetLocale());
 if(cel.getFormula()!==formula)cel.setFormula(formula);
 return true;
}\n`;
 new vm.Script(output);return {output,formula};
}
function reverterFonte(src){
 const n=src.split(GUARDA).length-1;if(n!==1)throw Error('Guarda de carga divergente');return src.replace(GUARDA,'');
}
module.exports={gerar,GUARDA,reverterFonte};
if(require.main===module){const x=gerar();fs.writeFileSync(path.join(root,'apps-script/ReservaBolsa.gs'),x.output);console.log(JSON.stringify({bytes:x.output.length,alvo:'DADOS!CZ41'}));}
