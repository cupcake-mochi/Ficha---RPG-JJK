'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {ambiente}=require('./apoio_inicializacao'),{contrato}=require('../inicializacao/gerar_contrato_arte');
const root=path.resolve(__dirname,'../..'),scripts=['contrato_arte','arte','inventario_imagens'].map(n=>new vm.Script(fs.readFileSync(path.join(root,'r53/inicializacao/'+n+'.gs'),'utf8')));
let casos=0,maior=0;function caso(nome,fn){try{fn();casos++;}catch(e){e.message=nome+': '+e.message;throw e;}}
function pos(a){const m=/^([A-Z]+)(\d+)$/.exec(a);return [+m[2],[...m[1]].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)];}
function imagem(titulo='FOTO PRIVADA'){return {valueType:'IMAGE',getAltTextTitle:()=>titulo,getContentUrl:()=>{throw Error('NUNCA ler URL privada');}};}
function preparado(op={}){
 const a=ambiente(op);for(const s of scripts)s.runInContext(a.ctx);a.ctx.SpreadsheetApp.ValueType={IMAGE:'IMAGE'};a.dados=new Map();a.leituras=[];a.ids={};a.meta=[];
 const specs=[['CARTEIRA',30,45],['FICHA',133,45],['FICHA AMALDIÇOADA',6,3],['INVOCAÇÕES',1171,45],['FICHA PESSOAL',31,45],['ABA PRIVADA',3,130]];
 for(let i=0;i<specs.length;i++){
  const [nome,rows,cols]=specs[i],m={id:i+1,nome,rows,cols,images:[],drawings:[],hidden:i===5};a.meta.push(m);a.ids[nome]=m.id;
  m.sh={getSheetId:()=>m.id,getName:()=>m.nome,getMaxRows:()=>m.rows,getMaxColumns:()=>m.cols,getImages:()=>m.images,getDrawings:()=>m.drawings,
  getRange:(r,c,nr,nc)=>{
   assert(Number.isInteger(r)&&Number.isInteger(c)&&Number.isInteger(nr)&&Number.isInteger(nc));assert(r+nr-1<=m.rows&&c+nc-1<=m.cols);assert(nr*nc<=4096);
   const read=key=>{a.leituras.push([m.id,r,c,nr,nc,key]);if(a.failRead)throw Error('SEGREDO https://nao-retornar');const data=Array.from({length:nr},(_,i)=>Array.from({length:nc},(_,j)=>a.dados.get(m.id+':'+(r+i)+','+(c+j))?.[key]??''));return a.incompleto?data.slice(0,-1):data;};
   return {getValues:()=>read('v'),getFormulas:()=>read('f')};
  }};
 }
 a.ss.getSheets=()=>a.meta.map(m=>m.sh);a.ss.getSheetByName=n=>a.meta.find(m=>m.nome===n)?.sh;
 a.put=(aba,r,c,v,f='')=>a.dados.set(a.ids[aba]+':'+r+','+c,{v,f});
 for(const x of contrato.decoracoes){const [r,c]=pos(x.faixa);a.put(x.aba,r,c,imagem('PM-ARTE:'+x.arquivo));}
 if(op.fotos)for(const x of contrato.campos){const [r,c]=pos(x.faixa);a.put(x.aba,r,c,imagem(),x.formulaDestino||'');}
 a.preview=(fase='antes')=>a.ctx.r53NovaFichaImagensPrevia(a.ss,a.context,fase);
 a.apply=(p,fase='antes')=>a.ctx.r53NovaFichaImagensInspecionar(a.ss,a.context,fase,p.assinatura);
 a.complete=(p,fase='antes')=>{for(let i=0;i<100;i++){const out=a.apply(p,fase);assert.equal(out.criacaoDisponivel,false);assert.equal(out.consistenciaTemporalVerificada,false);assert.equal(out.autenticidadeDecoracaoVerificada,false);for(const [k,v]of a.doc)if(k.startsWith('r53_nova_ficha_inventario_imagens_')){maior=Math.max(maior,Buffer.byteLength(v));assert(!/FOTO PRIVADA|ABA PRIVADA|https:/.test(v));}if(out.leituraConcluida)return out;assert(out.retomar);}throw Error('retomadas demais');};
 return a;
}
caso('toda a grade física é lida uma vez, inclusive oculta, bordas e colunas depois da 64',()=>{
 const a=preparado({fotos:true});a.put('ABA PRIVADA',3,130,imagem());a.put('ABA PRIVADA',2,65,'','=IF(FALSE;IMAGE("https://PRIVADO");"")');a.put('ABA PRIVADA',1,64,'IMAGE(x)','="IMAGE(x)"');a.put('CARTEIRA',1,2,new Date());
 const antes=new Map(a.dados),p=a.preview();assert.equal(a.writes.length,0);assert.equal(a.leituras.length,0);const r=a.complete(p);
 assert.equal(r.contagem.fotos,14);assert.equal(r.contagem.decoracoesMarcadas,10);assert.equal(r.contagem.decoracoesAusentes,0);assert.equal(r.contagem.fora,2);assert.equal(r.contagem.formulasImagem,1);assert.equal(r.contagem.indeterminadas,0);assert(r.amostra.some(x=>x.abaId===6&&x.linha===3&&x.coluna===130));
 const total=a.meta.reduce((n,m)=>n+m.rows*m.cols,0);assert.equal(r.contagem.celulas,total);assert.equal(p.celulas,total);assert.equal(a.leituras.filter(x=>x.at(-1)==='v').reduce((n,x)=>n+x[3]*x[4],0),total);
 assert.deepEqual(a.dados,antes);assert(a.writes.every(([t])=>t==='propriedade'));assert(!/PRIVAD|https:/.test(JSON.stringify(r)));
});
caso('máximo de quatro páginas por execução e repetição concluída não refaz nem atualiza a rodada',()=>{
 const a=preparado(),p=a.preview(),r=a.apply(p);assert.equal(r.paginasLidas,4);assert(r.retomar);a.complete(p);const n=a.leituras.length,w=a.writes.length;r.contagem.fora=999;const out=a.apply(p);assert.equal(out.contagem.fora,0);assert.equal(a.leituras.length,n);assert.equal(a.writes.length,w);assert(out.retrataSomenteEstaRodada);
});
const base=preparado();base.complete(base.preview());
for(let k=1;k<=base.writes.length;k++)for(const fase of ['antes','depois'])caso('checkpoint com queda '+fase+' '+k+' não pula nem duplica página',()=>{
 const a=preparado(),p=a.preview();let n=0;a.hook(f=>{if(f===fase&&++n===k)throw Error('queda');});assert.throws(()=>a.complete(p),/queda/);assert(!a.locked());a.hook(null);const r=a.complete(p);assert.equal(r.contagem.celulas,p.celulas);assert.equal(r.contagem.decoracoesMarcadas,10);
});
caso('leitura com erro ou truncada não avança checkpoint nem revela mensagem recebida',()=>{
 for(const field of ['failRead','incompleto']){const a=preparado(),p=a.preview();a[field]=true;let err;try{a.apply(p);}catch(e){err=e;}assert(err);assert(!/SEGREDO|https:/.test(err.message));const j=JSON.parse(a.doc.get(a.ctx.r53NovaInvImagemFase_('antes')));assert.equal(j.proxima,0);a[field]=false;assert(a.complete(p).leituraConcluida);}
});
caso('oito endereços no máximo, totais não truncados e sem texto/URL/alt',()=>{
 const a=preparado();for(let c=1;c<=30;c++)a.put('ABA PRIVADA',1,c,imagem('ALT SEGREDO'));const r=a.complete(a.preview());assert.equal(r.contagem.fora,30);assert.equal(r.amostra.length,8);assert(r.amostraLimitada);assert(!/SEGREDO|PRIVADA|https:/.test(JSON.stringify(r)));
});
caso('marca PM-ARTE é só candidata: mesma marca não prova pixels ou origem',()=>{
 const a=preparado(),x=contrato.decoracoes[0],[r,c]=pos(x.faixa);a.put(x.aba,r,c,imagem('PM-ARTE:'+x.arquivo));const out=a.complete(a.preview());assert.equal(out.contagem.decoracoesMarcadas,10);assert.equal(out.autenticidadeDecoracaoVerificada,false);assert.equal(out.criacaoDisponivel,false);
});
caso('decoração com marca diferente ou ausente é apontada, nunca removida',()=>{
 for(const value of [imagem('outro título'),'']){const a=preparado(),x=contrato.decoracoes[0],[r,c]=pos(x.faixa);a.put(x.aba,r,c,value);const out=a.complete(a.preview());assert.equal(out.contagem.decoracoesMarcadas,9);assert.equal(out.contagem.fora+out.contagem.decoracoesAusentes,1);assert.equal(a.dados.get(a.ids[x.aba]+':'+r+','+c).v,value);}
});
for(const value of [{erro:'privado'},{get valueType(){throw Error('URL PRIVADA');}},imagem()])caso('objeto desconhecido ou alt ilegível não ganha classificação de decoração',()=>{
 const a=preparado(),x=contrato.decoracoes[0],[r,c]=pos(x.faixa);const v=typeof value.getAltTextTitle==='function'?{...value,getAltTextTitle:()=>{throw Error('URL PRIVADA');}}:value;a.put(x.aba,r,c,v);const out=a.complete(a.preview());assert.equal(out.contagem.decoracoesMarcadas,9);assert.equal(out.contagem.indeterminadas+out.contagem.fora,1);assert(!/URL PRIVADA/.test(JSON.stringify(out)));
});
caso('sobreposições e desenhos são contados sem ler título/URL ou chamar remove',()=>{
 const a=preparado();a.meta[5].images=[{remove(){throw Error();},getUrl(){throw Error();}}];a.meta[5].drawings=[{}];const r=a.complete(a.preview());assert.equal(r.sobrepostas,1);assert.equal(r.desenhos,1);assert.equal(r.criacaoDisponivel,false);
});
for(const change of [a=>a.meta[0].rows++,a=>a.meta[0].nome+=' nova',a=>a.meta[0].images.push({}),a=>a.meta[0].drawings.push({})])caso('mudança da grade/abas/quantidade de objetos recusa sem avançar',()=>{
 const a=preparado(),p=a.preview();a.apply(p);const raw=a.doc.get(a.ctx.r53NovaInvImagemFase_('antes')),w=a.writes.length;change(a);assert.throws(()=>a.apply(p),/mudaram|inválido|âncora conhecida fora/);assert.equal(a.writes.length,w);assert.equal(a.doc.get(a.ctx.r53NovaInvImagemFase_('antes')),raw);
});
caso('conversão de ordem das abas não muda o plano, IDs únicos são obrigatórios',()=>{
 const a=preparado(),p=a.preview();a.meta.reverse();assert.equal(a.preview().assinatura,p.assinatura);a.complete(p);const b=preparado();b.meta[1].id=b.meta[0].id;assert.throws(()=>b.preview(),/metadados/);assert.equal(b.writes.length,0);
});
caso('antes e depois são rodadas distintas, uma não serve como fotografia atual da outra',()=>{
 const a=preparado(),p=a.preview();a.complete(p);a.put('ABA PRIVADA',3,130,imagem());const antigo=a.apply(p);assert.equal(antigo.contagem.fora,0);assert.equal(antigo.consistenciaTemporalVerificada,false);const fresh=a.complete(a.preview('depois'),'depois');assert.equal(fresh.contagem.fora,1);assert.equal([...a.doc.keys()].filter(k=>k.startsWith('r53_nova_ficha_inventario_imagens_')).length,2);
});
caso('inserção numa página já lida é limite explícito, não selo de consistência temporal',()=>{
 const a=preparado(),p=a.preview();a.apply(p);a.put('CARTEIRA',1,1,imagem());const r=a.complete(p);assert.equal(r.contagem.fora,0);assert.equal(r.consistenciaTemporalVerificada,false);assert.equal(r.criacaoDisponivel,false);assert.equal(a.complete(a.preview('depois'),'depois').contagem.fora,1);
});
for(const fase of ['qualquer','__proto__',null,1])caso('rodada não confiável '+fase,()=>{const a=preparado();assert.throws(()=>a.preview(fase),/desconhecida/);assert.equal(a.writes.length,0);});
for(const change of [j=>j.proxima++,j=>j.contagem.fora++,j=>j.extra='privado',j=>j.amostra.push({url:'https://segredo'}),j=>j.contagem.extra='privado'])caso('checkpoint alterado recusa em vez de recomeçar',()=>{
 const a=preparado(),p=a.preview();a.apply(p);const key=a.ctx.r53NovaInvImagemFase_('antes'),j=JSON.parse(a.doc.get(key));change(j);a.doc.set(key,JSON.stringify(j));const w=a.writes.length;assert.throws(()=>a.apply(p),/diário|vínculo/);assert.equal(a.writes.length,w);
});
caso('checkpoint corrompido e operação diferente não são aceitos',()=>{
 for(const tipo of ['json','operacao']){const a=preparado(),p=a.preview();a.apply(p);if(tipo==='json')a.doc.set(a.ctx.r53NovaInvImagemFase_('antes'),'{');else a.context.operacao+='outra';const w=a.writes.length;assert.throws(()=>a.apply(p),/diário|vínculo|mudaram/);assert.equal(a.writes.length,w);}
});
caso('limites de abas/células/páginas ou âncoras ausentes não produzem resultado truncado',()=>{
 for(const tipo of ['abas','celulas','paginas','ausente']){const a=preparado();if(tipo==='abas')a.ctx.R53_NOVO_INVENTARIO_IMAGENS_.limiteAbas=5;if(tipo==='celulas')a.meta[0].rows=999999;if(tipo==='paginas')a.ctx.R53_NOVO_INVENTARIO_IMAGENS_.limitePaginas=1;if(tipo==='ausente')a.meta=a.meta.filter(x=>x.nome!=='INVOCAÇÕES');assert.throws(()=>a.preview(),/limite|exced|âncora/);assert.equal(a.writes.length,0);}
});
caso('orçamento expirado interrompe sem ler páginas e mantém retomada',()=>{
 const a=preparado();a.ctx.R53_NOVO_INVENTARIO_IMAGENS_.orcamentoMs=0;const p=a.preview(),r=a.apply(p);assert.equal(r.paginasLidas,0);assert(r.retomar);assert.equal(a.leituras.length,0);
});
caso('espaço de propriedades insuficiente recusa sem tocar células',()=>{
 const a=preparado(),p=a.preview();for(let i=0;i<57;i++)a.doc.set('alheio'+i,'x'.repeat(8000));assert.throws(()=>a.apply(p),/espaço seguro/);assert.equal(a.writes.length,0);assert.equal(a.leituras.length,0);
});
for(const op of [{id:'1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k'},{ativoDiferente:true},{ocupado:true}])caso('alvo/trava recusados '+JSON.stringify(op),()=>{const a=preparado(op);assert.throws(()=>a.complete(a.preview()),/alvo|vinculado|andamento/);assert.equal(a.writes.length,0);});
caso('token IMAGE fora de strings é detectado sem confundir texto ou nome de aba',()=>{
 const a=preparado(),fn=a.ctx.r53NovaInvImagemFormula_;for(const f of ['=IMAGE("a")','=IF(FALSE;image(A1);"")','= _xlfn.IMAGE(A1)'])assert(fn(f));
 for(const f of ['="IMAGE(x)"',"='IMAGE(x)'!A1",'texto IMAGE(x)','=MYIMAGE(A1)','=CONCAT("a";"IMAGE(\"\")")'])assert(!fn(f),f);
});
caso('duração/leituras não mudam valores; diários pequenos não contêm conteúdo pessoal',()=>{assert(maior<9000);});
console.log(`${casos} cenários offline do inventário paginado de imagens aprovados; maior checkpoint ${maior} bytes. Sem selo temporal/pixels, escrita de células ou liberação de criação.`);
