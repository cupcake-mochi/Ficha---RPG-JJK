'use strict';
// Exercita o protocolo real do executor; células/PropertiesService em VM.
// Não prova atomicidade, quotas de requisições ou latência do Google.
const assert=require('node:assert/strict');
const {ambiente}=require('./apoio_inicializacao');
const {contrato}=require('../inicializacao/gerar_contrato_cartoes');
let casos=0;
function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function preparo(op={}){
 const a=ambiente(op);a.put('FICHA','A1','SEGREDO');a.put('FICHA','A2','PRIVADO','','NOTA PRIVADA');
 a.perfil={recibo:true,nome:'teste',diario:'r53_nova_ficha_teste_v1',limites:{escritasPorExecucao:4,orcamentoMs:210000},
 operacoes:()=>[{aba:'FICHA',faixa:'A1',tipo:'valor',valor:0},{aba:'FICHA',faixa:'A2',tipo:'valor',valor:false},{aba:'FICHA',faixa:'A2',tipo:'nota',valor:''}],
 preservados:()=>a.ctx.r53NovaFinHash_(a.range('CONFIGURAÇÃO','AK51').getValues()),pendente:['prova_nativa']};
 a.previa=()=>a.ctx.r53NovaPerfilPrevia_(a.ss,a.context,a.perfil);
 a.aplicar=p=>a.ctx.r53NovaPerfilAplicar_(a.ss,a.context,p.assinatura,a.perfil);
 return a;
}
function recibo(a){return JSON.parse(a.doc.get(a.perfil.diario));}
function semEscrever(a,fn,rx){const n=a.writes.length;assert.throws(fn,rx);assert.equal(a.writes.length,n);assert(!a.locked());}
caso('termina com recibo vinculado, privado e terminal',()=>{
 const a=preparo(),p=a.previa();const r=a.aplicar(p);assert(r.concluido);assert.equal(r.criacaoDisponivel,false);
 const j=recibo(a);assert.equal(j.recibo,1);assert(!j.plano);assert(!/SEGREDO|PRIVADO|modelo-sintetico|copia-descartavel/.test(JSON.stringify(j)));
 assert(Buffer.byteLength(JSON.stringify(j))<600);const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n);
 semEscrever(a,()=>a.previa(),/já existe/);
});
for(let k=1;k<=5;k++)for(const fase of ['antes','depois'])caso('queda '+fase+' escrita '+k,()=>{
 const a=preparo(),p=a.previa();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});
 assert.throws(()=>a.aplicar(p),/queda/);assert(!a.locked());a.hook(null);assert(a.aplicar(p).concluido);assert.equal(recibo(a).recibo,1);
});
caso('queda após todos os dados preserva diário detalhado para retomada',()=>{
 const a=preparo(),p=a.previa();let n=0;a.hook((f,t)=>{if(f==='antes'&&t==='propriedade'&&++n===2)throw Error('queda');});
 assert.throws(()=>a.aplicar(p),/queda/);const j=recibo(a);assert(j.plano);assert.equal(j.concluido,false);
 a.hook(null);a.aplicar(p);assert.equal(recibo(a).recibo,1);
});
for(const change of [a=>a.put('FICHA','A1',7),a=>a.put('FICHA','A1',0,'=0'),a=>a.put('FICHA','A2',false,'','nova nota')])caso('recibo detecta uso posterior sem reescrever',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);change(a);semEscrever(a,()=>a.aplicar(p),/já foi usada/);
});
for(const key of ['assinatura','vinculo','layout','preservados','resultado','integridade'])caso('hash de recibo alterado '+key,()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);const j=recibo(a);j[key]='0'.repeat(64);a.doc.set(a.perfil.diario,JSON.stringify(j));semEscrever(a,()=>a.aplicar(p),/diário inválido/);
});
for(const change of [j=>j.extra=true,j=>j.recibo=2,j=>j.concluido=false,j=>delete j.layout])caso('formato futuro ou incompleto é recusado',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);const j=recibo(a);change(j);a.doc.set(a.perfil.diario,JSON.stringify(j));semEscrever(a,()=>a.aplicar(p),/diário inválido/);
});
for(const key of ['operacao','modelo'])caso('vínculo com '+key+' é obrigatório mesmo com mesma assinatura',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);a.context[key]+='_outra';semEscrever(a,()=>a.aplicar(p),/operação diferente/);
});
caso('copiar recibo para outro destino não autoriza limpar',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);const b=preparo({id:'outra-copia'});b.doc.set(b.perfil.diario,a.doc.get(a.perfil.diario));semEscrever(b,()=>b.aplicar(p),/operação diferente/);
});
for(const change of [a=>a.perfil.nome='outro',a=>{a.doc.set('outra-chave',a.doc.get(a.perfil.diario));a.perfil.diario='outra-chave';}])caso('recibo não pode ser transferido de domínio',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);change(a);semEscrever(a,()=>a.aplicar(p),/operação diferente/);
});
caso('assinatura de chamada diferente é recusada',()=>{const a=preparo(),p=a.previa();a.aplicar(p);semEscrever(a,()=>a.aplicar({assinatura:'a'.repeat(64)}),/operação diferente/);});
caso('operação de fábrica alterada impede reconhecer recibo antigo',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);const ops=a.perfil.operacoes();ops[0].valor=1;a.perfil.operacoes=()=>ops;semEscrever(a,()=>a.aplicar(p),/estrutura/);
});
caso('guarda editada depois e durante leitura é recusada',()=>{
 for(const durante of [false,true]){const a=preparo(),p=a.previa();a.aplicar(p);
 if(durante){const fn=a.perfil.preservados;let n=0;a.perfil.preservados=()=>{if(++n===2)a.put('CONFIGURAÇÃO','AK51','outra regra');return fn();};}
 else a.put('CONFIGURAÇÃO','AK51','outra regra');semEscrever(a,()=>a.aplicar(p),/estrutura/);}
});
caso('recibo de perfil sem adesão explícita não é aceito',()=>{const a=preparo(),p=a.previa();a.aplicar(p);a.perfil.recibo=false;semEscrever(a,()=>a.aplicar(p),/recibo não reconhecido/);});
for(const concluded of [false,true])caso('migra diário v1 '+concluded+' só após conferir estado final',()=>{
 const a=preparo();a.perfil.recibo=false;const p=a.previa();a.aplicar(p);const j=recibo(a);j.concluido=concluded;a.doc.set(a.perfil.diario,JSON.stringify(j));
 a.perfil.recibo=true;const n=a.writes.length;a.aplicar(p);assert.equal(a.writes.length,n+1);assert.equal(a.writes.at(-1)[0],'propriedade');assert.equal(recibo(a).recibo,1);
});
caso('diário v1 concluído com edição não é compactado',()=>{
 const a=preparo();a.perfil.recibo=false;const p=a.previa();a.aplicar(p);a.perfil.recibo=true;a.put('FICHA','A1',7);semEscrever(a,()=>a.aplicar(p),/editados|já foi usada/);assert(recibo(a).plano);
});
caso('confirma persistência do diário antes de tocar nos dados',()=>{
 const a=preparo(),p=a.previa(),factory=a.ctx.PropertiesService.getDocumentProperties;
 a.ctx.PropertiesService.getDocumentProperties=()=>({...factory(),setProperty:()=>{}});
 semEscrever(a,()=>a.aplicar(p),/diário não confirmada/);assert.equal(a.range('FICHA','A1').getValue(),'SEGREDO');
});
caso('falha silenciosa ao substituir deixa diário retomável',()=>{
 const a=preparo(),p=a.previa(),factory=a.ctx.PropertiesService.getDocumentProperties;let n=0;
 a.ctx.PropertiesService.getDocumentProperties=()=>{const obj=factory();return {...obj,setProperty:(k,v)=>{if(++n!==2)obj.setProperty(k,v);}};};
 assert.throws(()=>a.aplicar(p),/diário não confirmada/);assert(recibo(a).plano);a.ctx.PropertiesService.getDocumentProperties=factory;a.aplicar(p);assert.equal(recibo(a).recibo,1);
});
caso('limite UTF-8 individual é conferido antes de gravar',()=>{
 const a=preparo();semEscrever(a,()=>a.ctx.r53NovaDiarioSalvar_(a.ctx.PropertiesService.getDocumentProperties(),'x',{texto:'🙂'.repeat(2300)}),/limite/);
});
function encher(a,bytes){let i=0;while(bytes>0){const n=Math.min(8000,bytes);a.doc.set('alheia'+i++,'x'.repeat(n));bytes-=n;}}
caso('propriedades alheias contam: falta de espaço recusa antes da limpeza',()=>{
 const a=preparo(),p=a.previa();encher(a,449000);const antes=JSON.stringify([...a.doc]);semEscrever(a,()=>a.aplicar(p),/espaço seguro/);assert.equal(JSON.stringify([...a.doc]),antes);
});
caso('substituição menor pode recuperar diário perto da quota, sem apagar alheios',()=>{
 const a=preparo();a.perfil.recibo=false;const p=a.previa();a.aplicar(p);encher(a,450000);const alheios=[...a.doc].filter(([k])=>k!==a.perfil.diario);
 a.perfil.recibo=true;a.aplicar(p);assert.equal(recibo(a).recibo,1);for(const [k,v]of alheios)assert.equal(a.doc.get(k),v);
 a.perfil.diario='novo';semEscrever(a,()=>a.aplicar(a.previa()),/espaço seguro/);
});
caso('respeita orçamento ao reconferir recibo sem refazer limpeza',()=>{
 const a=preparo(),p=a.previa();a.aplicar(p);a.perfil.limites.orcamentoMs=0;const n=a.writes.length;const r=a.aplicar(p);assert.equal(r.concluido,false);assert(r.retomar);assert.equal(a.writes.length,n);
});
let total=0,pico=0;
caso('572 recibos num só store mais 100 KB reservados e diário pendente cabem',()=>{
 const a=preparo();encher(a,100000);const props=a.ctx.PropertiesService.getDocumentProperties;
 const contar=()=>[...a.doc].reduce((n,[k,v])=>n+Buffer.byteLength(k)+Buffer.byteLength(v),0);
 const factory=props;a.ctx.PropertiesService.getDocumentProperties=()=>{const p=factory();return {...p,setProperty:(k,v)=>{p.setProperty(k,v);pico=Math.max(pico,contar());assert(pico<=450000);}};};
 const perfis=['montagens','cartoes'].flatMap(tipo=>Object.keys(contrato.contextos).map(id=>tipo+'_'+id));
 perfis.push(...Object.keys(require('../inicializacao/gerar_contrato_entidades').contrato.dominios).map(id=>'entidades_'+id));
 perfis.push('fotos_ancoras');
 for(const nome of perfis){
  a.perfil.nome=nome;a.perfil.diario='r53_nova_ficha_'+nome+'_v1';a.put('FICHA','A1','SEGREDO');a.put('FICHA','A2','PRIVADO','','NOTA PRIVADA');
  a.aplicar(a.previa());assert.equal(recibo(a).recibo,1);
 }
 assert.equal([...a.doc].filter(([k])=>k.startsWith('r53_nova_ficha_')).length,572);
 // Reserva de valor máximo e chave para o próximo domínio, ainda sem limpar nada.
 assert(contar()+9100<450000);total=contar();assert(!a.writes.some(([tipo])=>tipo==='excluirPropriedade'));
});
console.log(`${casos} cenários offline de recibos/quota aprovados; 572 recibos + reserva: ${total} bytes, pico ${pico}. Não é prova nativa nem orquestração completa.`);
