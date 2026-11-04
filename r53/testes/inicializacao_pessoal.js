'use strict';
// Não calcula fórmulas: testa escopo, contrato, diário e falhas por chamada.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const {ambiente,a1}=require('./apoio_inicializacao');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);
vm.runInContext(fs.readFileSync(path.join(root,'apps-script/Ficha.gs'),'utf8'),g);
const original=g.ABAS.find(x=>x.nome==='FICHA'),val=addr=>{const [r,c]=a1(addr);return original.vals.find(x=>x[0]===r&&x[1]===c)[2];};
const note=addr=>(original.notas||[]).find(x=>x[0]===addr)?.[1]||'';
const sources=['contrato_pessoal','pessoal'].map(n=>fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8'));
let casos=0;function caso(n,f){try{f();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function preparado(dom){const a=ambiente();for(const f of sources)vm.runInContext(f,a.ctx);a.dom=dom;
 const c=a.ctx.R53_NOVA_PESSOAL_CONTRATO_[dom];
 for(const [addr,label]of Object.entries(c.cabecalhos))a.put('FICHA',addr,label,'','INSTRUÇÃO NO CABEÇALHO');
 for(const x of c.formulas)a.put('FICHA',x.faixa,777,val(x.faixa));
 for(const x of c.campos)a.put('FICHA',x.faixa,x.formula?999:typeof x.valor==='boolean'?true:typeof x.valor==='number'?987:'DADO PESSOAL ANTIGO','','NOTA PRIVADA');
 a.put('CONFIGURAÇÃO','AK51','CATÁLOGO DA MESA');a.put('CONFIGURAÇÃO','F46',10);a.put('DADOS','CZ54',3700);
 a.put('FICHA PESSOAL','Q27','HISTÓRIA FORA DO DOMÍNIO');a.put('FICHA PESSOAL','AB11','Grau especial do modelo');
 if(dom!=='escolhas'){a.put('FICHA','D11','Caminho escolhido');a.put('FICHA','D21',5);}else a.put('FICHA','D26',123);
 a.contrato=c;a.previa=()=>a.ctx.r53NovaPerfilPrevia_(a.ss,a.context,a.ctx.r53NovaPessoalPerfil_(dom));
 a.aplicar=p=>a.ctx.r53NovaPerfilAplicar_(a.ss,a.context,p.assinatura,a.ctx.r53NovaPessoalPerfil_(dom));
 a.concluir=p=>{for(let i=0;i<40;i++){const r=a.aplicar(p);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('limite de retomadas');};
 return a;
}
function conferir(a){for(const x of a.contrato.campos){const r=a.range('FICHA',x.faixa);if(x.formula)assert.equal(r.getFormulas()[0][0],val(x.faixa));else{assert.equal(r.getValue(),val(x.faixa));assert.equal(r.getFormulas()[0][0],'');}assert.equal(r.getNotes()[0][0],note(x.faixa));}
 assert.equal(a.range('CONFIGURAÇÃO','AK51').getValue(),'CATÁLOGO DA MESA');assert.equal(a.range('CONFIGURAÇÃO','F46').getValue(),10);assert.equal(a.range('DADOS','CZ54').getValue(),3700);
 assert.equal(a.range('FICHA PESSOAL','Q27').getValue(),'HISTÓRIA FORA DO DOMÍNIO');assert.equal(a.range('FICHA PESSOAL','AB11').getValue(),'Grau especial do modelo');
 assert.equal(a.range('FICHA PESSOAL','D92').getValue(),'inventário antigo fora deste domínio');assert.equal(a.range('EXTRATO','A2').getValue(),'SEGREDO financeiro');
 assert.equal(a.doc.get('r53_recuperacao_personagem'),'recuperação fora deste domínio');
 for(const cell of a.cells.values()){assert.equal(cell.fmt,'tema');assert.equal(cell.dv,'menu');}
 for(const x of a.contrato.formulas)assert.equal(a.range('FICHA',x.faixa).getFormulas()[0][0],val(x.faixa));
 for(const [addr,label]of Object.entries(a.contrato.cabecalhos)){assert.equal(a.range('FICHA',addr).getValue(),label);assert.equal(a.range('FICHA',addr).getNotes()[0][0],'INSTRUÇÃO NO CABEÇALHO');}
 const raw=a.doc.get(a.ctx.r53NovaPessoalPerfil_(a.dom).diario);assert(!raw.includes('DADO PESSOAL ANTIGO'));assert(!raw.includes('NOTA PRIVADA'));assert(Buffer.byteLength(raw)<9000);assert.equal(JSON.parse(raw).concluido,true);assert(!a.locked());
}
caso('contrato conferido sem regeneração e escopos ancorados no fonte',()=>{
 execFileSync(process.execPath,['r53/inicializacao/gerar_contrato_pessoal.js','--conferir'],{cwd:root});
 for(const [dom,total]of [['escolhas',19],['recursos',20],['condicoes',9]]){const a=preparado(dom);assert.equal(a.contrato.campos.length,total);for(const x of a.contrato.campos){assert.equal(x.formula||x.valor,val(x.faixa));assert.equal(x.nota,note(x.faixa));}}
});
for(const dom of ['escolhas','recursos','condicoes']){
 caso(dom+' aplica, preserva outros domínios e repete sem escrever',()=>{const a=preparado(dom),p=a.previa();assert.equal(a.writes.length,0);assert.equal(p.criacaoDisponivel,false);const r=a.concluir(p);assert.equal(r.criacaoDisponivel,false);assert(r.pendente.includes('conferencia_conjunta'));conferir(a);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);});
 caso(dom+' quatro passos por chamada, conclusão não prematura',()=>{const a=preparado(dom),p=a.previa(),r=a.aplicar(p);assert.equal(r.concluido,false);assert.equal(r.retomar,true);assert.equal(a.writes.filter(x=>x[0]!=='propriedade').length,4);a.concluir(p);conferir(a);});
 caso(dom+' prévia envelhecida não escreve',()=>{const a=preparado(dom),p=a.previa();a.put('FICHA',a.contrato.campos[0].faixa,'EDIÇÃO RECENTE');assert.throws(()=>a.aplicar(p),/mudou após/);assert.equal(a.writes.length,0);});
 caso(dom+' fórmula protegida alterada é recusada',()=>{const a=preparado(dom);a.put('FICHA',a.contrato.formulas[0].faixa,0,'=0');assert.throws(()=>a.previa(),/protegida/);assert.equal(a.writes.length,0);});
 caso(dom+' cabeçalho desconhecido é recusado',()=>{const a=preparado(dom);a.put('FICHA',Object.keys(a.contrato.cabecalhos)[0],'OUTRO');assert.throws(()=>a.previa(),/rótulo/);assert.equal(a.writes.length,0);});
 caso(dom+' fórmula em entrada literal não é apagada',()=>{const a=preparado(dom),x=a.contrato.campos.find(x=>!x.formula);a.put('FICHA',x.faixa,1,'=1');assert.throws(()=>a.previa(),/fórmula inesperada/);assert.equal(a.writes.length,0);});
 caso(dom+' CellImage em entrada não passa como objeto vazio',()=>{const a=preparado(dom);a.put('FICHA',a.contrato.campos[0].faixa,{valueType:'IMAGE'});assert.throws(()=>a.previa(),/imagem ou valor/);assert.equal(a.writes.length,0);});
 caso(dom+' nova nota após uso não é apagada',()=>{const a=preparado(dom),p=a.previa();a.concluir(p);const x=a.contrato.campos[0],r=a.range('FICHA',x.faixa);a.put('FICHA',x.faixa,r.getValue(),r.getFormulas()[0][0],'NOTA NOVA');const n=a.writes.length;assert.throws(()=>a.aplicar(p),/editados|já foi usada/);assert.equal(a.writes.length,n);});
 const base=preparado(dom);base.concluir(base.previa());
 for(let i=1;i<=base.writes.length;i++)for(const fase of ['antes','depois'])caso(dom+' retoma queda '+fase+' '+i,()=>{const a=preparado(dom),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});assert.throws(()=>a.concluir(p),/queda/);assert(!a.locked());a.hook(null);a.concluir(p);conferir(a);});
 caso(dom+' mudança de fórmula durante pausa não avança',()=>{const a=preparado(dom),p=a.previa();a.aplicar(p);const n=a.writes.length;a.put('FICHA',a.contrato.formulas[0].faixa,1,'=1');assert.throws(()=>a.aplicar(p),/protegida/);assert.equal(a.writes.length,n);});
}
caso('cena restaura ligação aos máximos sem copiar resultado antigo',()=>{const a=preparado('recursos');a.concluir(a.previa());for(const r of [26,30,34])assert.equal(a.range('FICHA','D'+r).getFormulas()[0][0],'=J'+r);assert.equal(a.range('FICHA','D11').getValue(),'Caminho escolhido');assert.equal(a.range('FICHA','D21').getValue(),5);});
caso('condições restauram a instrução das Sequelas extras',()=>{const a=preparado('condicoes');a.concluir(a.previa());conferir(a);assert.equal(a.range('FICHA','J50').getNotes()[0][0],note('J50'));assert(note('J50').length>30);});
caso('escolhas não recarregam recursos de cena',()=>{const a=preparado('escolhas');a.concluir(a.previa());assert.equal(a.range('FICHA','D26').getValue(),123);assert.equal(a.range('FICHA','D11').getValue(),'Escolha seu Caminho');assert.equal(a.range('FICHA','X11').getValue(),'Latente');assert.equal(a.range('FICHA','Z67').getValue(),'ESSÊNCIA');});
caso('fórmula pessoal do recurso atual exige revisão',()=>{const a=preparado('recursos');a.put('FICHA','D26',1,'=J26+1');assert.throws(()=>a.previa(),/recurso atual/);assert.equal(a.writes.length,0);});
caso('fórmula original já presente é aceita sem copiar cache',()=>{const a=preparado('recursos');a.put('FICHA','D26',98765,'=J26');a.concluir(a.previa());conferir(a);});
caso('assinatura de outro domínio não permite aplicar',()=>{const a=preparado('recursos');const outro=preparado('escolhas').previa();assert.throws(()=>a.aplicar(outro),/mudou após/);assert.equal(a.writes.length,0);});
caso('contrato ausente não cria diário ou escrita',()=>{const a=preparado('recursos');a.ctx.R53_NOVA_PESSOAL_CONTRATO_=undefined;assert.throws(()=>a.previa(),/contrato pessoal/);assert.equal(a.writes.length,0);});
caso('variante nativa troca separadores sem alterar vírgulas literais',()=>{const {separadores}=require('../inicializacao/gerar_contrato_pessoal');assert.equal(separadores('=IF(A1="a,b",1,0)'),'=IF(A1="a,b";1;0)');for(const dom of ['recursos','condicoes','escolhas']){const a=preparado(dom);for(const x of a.contrato.formulas)a.put('FICHA',x.faixa,0,separadores(val(x.faixa)));a.concluir(a.previa());assert.equal(a.range('FICHA',a.contrato.formulas[0].faixa).getFormulas()[0][0],separadores(val(a.contrato.formulas[0].faixa)));}});


caso('aspas opcionais observadas no Google, sem alterar texto literal',()=>{
 const {separadores,aspasOpcionais}=require('../inicializacao/gerar_contrato_pessoal');
 assert.equal(aspasOpcionais('=IF(A1="'+"'FICHA'!"+'",'+"'FICHA'!$J$26"+',0)'), '=IF(A1="'+"'FICHA'!"+'",FICHA!$J$26,0)');
 for(const dom of ['recursos','condicoes']){const a=preparado(dom);for(const x of a.contrato.formulas)a.put('FICHA',x.faixa,0,aspasOpcionais(separadores(val(x.faixa))));a.concluir(a.previa());}
});
caso('variante nativa não libera mudar a conta do máximo',()=>{
 const {separadores,aspasOpcionais}=require('../inicializacao/gerar_contrato_pessoal');const a=preparado('recursos');
 a.put('FICHA','J26',0,aspasOpcionais(separadores(val('J26'))).replace('DADOS_CONFIG!$E$2','DADOS_CONFIG!$E$3'));
 assert.throws(()=>a.previa(),/protegida/);assert.equal(a.writes.length,0);
});
caso('diário grande é recusado antes de qualquer escrita',()=>{const a=preparado('recursos');a.context.modelo='modelo-'+('é'.repeat(6000));const p=a.previa();assert.throws(()=>a.aplicar(p),/diário excede/);assert.equal(a.writes.length,0);assert(!a.doc.has(a.ctx.r53NovaPessoalPerfil_('recursos').diario));assert(!a.locked());});
console.log(`${casos} cenários offline de escolhas/recursos/condições aprovados; sem aceite nativo ou inicialização geral.`);
