'use strict';
// IDs são públicos e vêm do editor; jamais obter uma lista de escrita do browser.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);
vm.runInContext(fs.readFileSync(path.join(root,'apps-script/EditorR53.gs'),'utf8'),g);
const editor=g.R53_EDITOR_,contextos=editor.contextos.map(x=>[x.id,x.classes]);
if(editor.storage!=='MONTAGENS'||new Set(contextos.map(x=>x[0])).size!==contextos.length||contextos.some(x=>!/^[-a-z0-9.]+$/.test(x[0])))throw Error('editor incompatível');
const contrato={versao:1,porGrupo:24,editorHash:crypto.createHash('sha256').update(JSON.stringify([editor.storage,contextos])).digest('hex'),
 chaves:['r53_versoes','r53_marcas_custom','r53_amparo_direto','r53_amparo_sujo',...contextos.map(x=>'r53_classe_visivel_'+x[0])]};
const text='/** Memórias pessoais conhecidas do editor; sem dados de jogador. */\nvar R53_NOVA_MEMORIAS_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_memorias.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de memórias desatualizado');console.log('Contrato de memórias igual ao editor público.');}else fs.writeFileSync(file,text);}
module.exports={contrato};
