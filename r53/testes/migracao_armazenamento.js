'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('apps-script/EditorR53.gs','utf8');let cfg=JSON.parse(source.slice(source.indexOf('=')+1,source.indexOf(';\n')));cfg.contextos=cfg.contextos.slice(0,2);
const fields=cfg.campos.map(f=>f[0]),old=Array.from({length:90},()=>Array(9).fill(''));
// Um registro R53 novo e outro da interface antiga de flags independentes.
old[4][0]='feitico.1 · Novo';old[5]=['Classe preparada',1,2,3,4,5,6,7];
cfg.campos.forEach((f,i)=>{old[6+i][0]=f[1];old[6+i][3]=cfg.defaults[f[0]];});
old[6+fields.indexOf('funcao1')][3]='Dano';old[6+fields.indexOf('pontos1')][3]=2;old[6+fields.indexOf('preparada')][3]=true;old[6+fields.indexOf('origem_permissao')][3]='=texto literal';
old[44][0]='feitico.2 · Anterior';old[45]=['Classe preparada',1,2,3,4,5,6,7];
const original=[['Versão preparada',true],['Forma','Projétil'],['Dano',true],['Pontos de dano',2],['Cura direta',true],['Pontos de cura',3],['Vida temporária',false],['Pontos de vida temporária',0],['Regra permite dano',true],['Só pode afetar quem executa',false]];
original.forEach(([label,value],i)=>{old[46+i][0]=label;old[46+i][3]=value;});
const sandbox={console:{log(){}},ss:null};vm.createContext(sandbox);vm.runInContext(fs.readFileSync('r53/aplicacao_tecnica.gs','utf8'),sandbox);
function run(){let matrix=Array.from({length:cfg.contextos[1].editor+40},()=>Array(9).fill(''));let props={getProperty(){return'1';}},ss={getSheetByName(){return{};}},sh={getDataRange(){return{getValues(){return old;}};}};sandbox.r53MigrarArmazenamento_(ss,sh,matrix,cfg,props);return matrix;}
let result=run(),get=(g,cl,k)=>result[g.editor+1+fields.indexOf(k)][g.classes.indexOf(cl)+1];
assert.strictEqual(get(cfg.contextos[0],3,'pontos1'),2);assert.strictEqual(get(cfg.contextos[0],3,'preparada'),true);assert.strictEqual(get(cfg.contextos[0],3,'origem_permissao'),"'=texto literal");
assert.strictEqual(get(cfg.contextos[1],3,'funcao1'),'Dano');assert.strictEqual(get(cfg.contextos[1],3,'pontos1'),2);assert.strictEqual(get(cfg.contextos[1],3,'funcao2'),'Cura');assert.strictEqual(get(cfg.contextos[1],3,'pontos2'),3);assert.strictEqual(get(cfg.contextos[1],3,'pessoal'),false);assert.strictEqual(get(cfg.contextos[1],3,'permite_dano'),true);
// Uma quantidade sem a função comprovada não pode virar uma montagem aprovada.
old[48][3]=false;result=run();assert.strictEqual(get(cfg.contextos[1],3,'funcao1'),'');assert.strictEqual(get(cfg.contextos[1],3,'pontos1'),2);assert.strictEqual(get(cfg.contextos[1],3,'migracao'),'Revisão necessária');
console.log('12 verificações de preservação/conversão do armazenamento passaram.');
