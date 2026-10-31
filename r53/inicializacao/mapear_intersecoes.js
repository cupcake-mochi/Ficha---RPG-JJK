'use strict';
// Mapa estático das escritas e guardas declaradas. Não lê planilhas ou fórmulas
// calculadas; dependências indiretas e eventos continuam fora deste inventário.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'../..');
function mapear(){
 const {ambiente,a1}=require('../testes/apoio_inicializacao'),a=ambiente({rows:5000}),c=a.ctx;
 for(const file of ['apps-script/EditorR53.gs',...['progressao','identidade','contrato_pessoal','pessoal','contrato_formacao','formacao','validacoes','contrato_memorias','memorias','contrato_montagens','montagens','contrato_cartoes','cartoes','contrato_entidades','entidades','contrato_arte','arte','inventario_imagens','sequencia'].map(n=>'r53/inicializacao/'+n+'.gs')])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),c);
 // Só os endereços são inventariados: estes resultados não decidem mecânica.
 c.r53NovaProgDados_=()=>({nivel:1,base:0});c.r53NovaCartAmparo_=()=> 'Normal';
 const fases=c.r53NovaSeqPlano_([]).filter(f=>f.tipo!=='imagens'),writes=[],guards=[];
 function add(out,perfil,aba,faixa,camada='conteudo'){out.push({perfil,aba,faixa,camada,pos:a1(faixa)});}
 for(const f of fases){
  const p=c.r53NovaSeqPerfil_(f),ops=p.operacoes(a.ss,a.context);
  for(const op of ops){if(op.tipo==='propriedade')continue;add(writes,p.nome,op.aba,op.faixa,/^nota/.test(op.tipo)?'nota':op.tipo==='validacao'?'validacao':'conteudo');}
  if(f.tipo==='financeiro'){
   for(const [aba,faixa]of c.R53_NOVA_FIN_.formulas)add(guards,p.nome,aba,faixa);
   add(guards,p.nome,'FICHA','AH11');add(guards,p.nome,'CONFIGURAÇÃO','E46:G46');
  }else if(f.tipo==='identidade'){
   for(const x of c.R53_NOVA_IDENT_.campos)add(guards,p.nome,x[0],x[2]);
   for(const [aba,faixa]of [['CARTEIRA','C8'],['FICHA','AB2'],['FICHA PESSOAL','Q11'],['FICHA PESSOAL','D10']])add(guards,p.nome,aba,faixa);
  }else if(f.tipo==='pessoal'){
   const d=c.r53NovaPessoalContrato_(f.id);for(const x of Object.keys(d.cabecalhos))add(guards,p.nome,'FICHA',x);for(const x of d.formulas)add(guards,p.nome,'FICHA',x.faixa);
  }else if(f.tipo==='formacao'){
   for(const x of c.r53NovaFormContrato_(f.id).guardas)add(guards,p.nome,x.aba,x.faixa);
  }else if(f.tipo==='entidade'){
   const d=c.r53NovaEntContrato_(f.id);for(const x of d.guardas)add(guards,p.nome,d.aba,x.faixa);if(d.foto)add(guards,p.nome,d.aba,d.foto);
  }else if(f.tipo==='cartao'){
   const d=c.r53NovaCartContrato_(f.id);for(const x of d.guardas)add(guards,p.nome,d.aba,x.faixa);add(guards,p.nome,d.amparo.aba,d.amparo.faixa);
  }else if(f.tipo==='fotos'){
   for(const x of c.r53NovaArteContrato_().campos)add(guards,p.nome,x.aba,x.guarda.faixa);
  }
 }
 function colisao(left,right,mesmo){
  const by={};for(const r of right)(by[r.aba+':'+r.camada]??=[]).push(r);
  const out=[];
  for(const x of left)for(const y of by[x.aba+':'+x.camada]||[]){if(x.perfil===y.perfil||mesmo&&x.perfil>=y.perfil)continue;const p=x.pos,q=y.pos;if(p[0]<=q[2]&&q[0]<=p[2]&&p[1]<=q[3]&&q[1]<=p[3])out.push({escritor:x.perfil,leitor:y.perfil,aba:x.aba,escrita:x.faixa,leitura:y.faixa,camada:x.camada});}
  return out;
 }
 return {versao:1,perfis:fases.length,operacoesCelulares:writes.length,guardasDeclaradas:guards.length,
  escritasCruzadas:colisao(writes,writes,true),escritasEmGuardas:colisao(writes,guards,false),
  limite:'Mapa direto de endereços: não enumera toda leitura dinâmica, validações, propriedades ou dependências de fórmulas/eventos. Sem prova nativa.'};
}
if(require.main===module)process.stdout.write(JSON.stringify(mapear(),null,2)+'\n');
module.exports={mapear};
