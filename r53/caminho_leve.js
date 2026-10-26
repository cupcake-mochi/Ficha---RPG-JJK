'use strict';
// Extrai as mesmas regras do editor, sem os catálogos de combate.
const fs=require('fs'),path=require('path'),z=require('zlib'),crypto=require('crypto'),vm=require('vm');
const root=path.resolve(__dirname,'..');
const NOMES=['cel_','indiceDosDados_','tabelaDaDados_','limitesA1_',
 'periciasDoCaminho_','marcarPericiasDoCaminho_','trilhaQueFica_','trilhaDoCaminho_',
 'habilidadeQueFica_','notaDaCarta_','cartasDaFicha_','linhasDoTexto_','alturaDaCaixa_',
 'negritosDoTexto_','escreverTextoDoLivro_','cartasDaDadosAm_','livroDasCartas_',
 'habilidadesDaFicha_','grupoDeArmaDaTrilha_','trocaArmaDoCaminho_',
 'caixasDeTreino_','treinoDoCaminho_','gravarCaixas_','treinoPeloCaminho_',
 'notasVivas_','fichaMexeNaPessoal_','treinoMarcado_','treinoDepoisDaCaixa_','tocaFaixa_'];
function corpo(src,n){const s=src.indexOf('function '+n+'('),e=src.indexOf('\n}',s);if(s<0||e<0)throw Error('Função ausente: '+n);const out=src.slice(s,e+2);new Function(out);return out;}
function gerar(){
 const src=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8');
 const ioPatches=[['var vals = ficha.getDataRange().getValues();','var vals = r53LerPericias_(ficha);'],['var grade = ficha.getDataRange(), valores = grade.getValues(), notas = grade.getNotes();','var grade = r53GradeCartas_(ficha), valores = grade.getValues(), notas = grade.getNotes();'],["var v = ss.getSheetByName(DADOS_DA_AMALDICOADA_).getDataRange().getValues(), h = v[0];","var v = R53_CAMINHO_CARTAS_, h = v[0];"],["var dados = ss.getSheetByName('DADOS').getDataRange().getValues();","var dados = r53DadosNotasCaminho_(ss);"]];
 let helpers=NOMES.map(n=>corpo(src,n)).join('\n');
 for(const[a,b]of ioPatches){if(helpers.split(a).length!==2)throw Error('Leitura divergente: '+a);helpers=helpers.replace(a,b);}
 helpers=helpers.replace(/ss.getSheetByName\('DADOS_PROGRESSAO'\)/g,'r53ProgCaminho_(ss)').replace(/SpreadsheetApp.getActive\(\).getSheetByName\('DADOS_PROGRESSAO'\)/g,'r53ProgCaminho_(SpreadsheetApp.getActive())');
 helpers=helpers.replace(/SpreadsheetApp.getActive\(\)/g,'R53_CAMINHO_SS_');
 const declarations=['IDX_COL_CAMPO','IDX_COL_CEL','ABA_PESSOAL_','DADOS_DA_AMALDICOADA_','TRILHAS_COM_CATEGORIA_'].map(n=>{
  const a=src.indexOf('var '+n+' '),b=src.indexOf('\n',a);if(a<0)throw Error(n);return src.slice(a,b);
 }).join('\n');
 const ctx={};vm.createContext(ctx);vm.runInContext(require('../medidas/carregar-ficha.js').fontes(),ctx);
 const spec=ctx.ABAS.find(a=>a.nome==='DADOS'),dados=Array.from({length:spec.rows},()=>Array(spec.cols).fill(''));
 for(const [r,c,v]of spec.vals){const a=typeof v==='string'&&v.startsWith('=ADDRESS(')?[...v.matchAll(/ADDRESS\(ROW\((?:'[^']+'|[A-Z_]+)!\$?([A-Z]+)\$?(\d+)\)/g)]:[];dados[r-1][c-1]=a.length?a.map(x=>x[1]+x[2]).join(':'):typeof v==='string'&&v.startsWith('=')?'':v;}
 const pessoal={};for(const row of dados)if(row[118]&&row[119])pessoal[row[118]]=row[119];
 if(!pessoal.treino)throw Error('Metadados de treino ausentes');
 const ficha=ctx.ABAS.find(a=>a.nome==='FICHA'),am=ctx.ABAS.find(a=>a.nome==='DADOS_AM'),progressao=ctx.ABAS.find(a=>a.nome==='DADOS_PROGRESSAO');
 const cat=JSON.parse(fs.readFileSync(path.join(root,'catalogo-projeto-m.json'),'utf8'));
 const rows=ficha.vals.filter(t=>Object.keys(cat.pericias).includes(t[2])&&ficha.vals.some(v=>v[0]===t[0]&&v[1]===t[1]-2&&typeof v[2]==='boolean')).map(t=>t[0]);
 const custom=progressao.vals.filter(t=>t[1]===56&&t[0]>=2&&t[0]<=24).map(t=>{let m=/ROW\('FICHA'!\$?[A-Z]+\$?(\d+)\)/.exec(t[2]);if(!m)throw Error('Perícia custom sem endereço');return +m[1];});
 const nr=spec.vals.find(t=>t[2]==='nota viva'),nt=spec.vals.find(t=>t[0]===nr[0]&&t[2]==='texto da nota');let count=0;while(dados[nr[0]+count]&&dados[nr[0]+count][nr[1]-1]!=='')count++;
 const cartas=Array.from({length:am.rows},()=>Array(am.cols).fill(''));for(const[r,c,v]of am.vals)if(c>=256&&c<=263){const a=typeof v==='string'&&/^=ADDRESS\(ROW\((?:'[^']+'|[A-Z_]+)!\$?([A-Z]+)\$?(\d+)\)/.exec(v);cartas[r-1][c-1]=a?a[1]+a[2]:v;}
 const cr=cartas.slice(1).map(r=>r[259]).filter(Boolean).map(v=>+String(v).replace(/^[A-Z]+/,''));
 if(rows.length!==23||cr.length!==9||cr.some(v=>!Number.isInteger(v))||count<1)throw Error('Índice limitado divergente');
 const io={rows:ficha.rows,cols:ficha.cols,pericias:[[Math.min(...rows),Math.max(...rows)],[Math.min(...custom),Math.max(...custom)]],cartas:[Math.min(...cr)-1,Math.max(...cr)+3],notas:[nr[0]+1,nt[1],count]};
 const refs=new Map(),letters=c=>{let s='';for(;c;c=Math.floor((c-1)/26))s=String.fromCharCode(65+(c-1)%26)+s;return s;};
 const add=(n,r,c)=>refs.set(n+'!'+letters(c)+r,[n,r,c,n+'!'+letters(c)+r]);
 const rect=(n,r,c,rr,cc)=>{for(let y=r;y<=rr;y++)for(let x=c;x<=cc;x++)add(n,y,x);};
 for(const t of ficha.vals)if(Object.keys(cat.pericias).includes(t[2])&&ficha.vals.some(v=>v[0]===t[0]&&v[1]===t[1]-2&&typeof v[2]==='boolean')){add('FICHA',t[0],t[1]);add('FICHA',t[0],t[1]-2);}
 for(const t of progressao.vals.filter(t=>t[1]===56&&t[0]>=2&&t[0]<=24)){const m=/ROW\('FICHA'!\$?([A-Z]+)\$?(\d+)\)/.exec(t[2]),c=[...m[1]].reduce((n,x)=>n*26+x.charCodeAt(0)-64,0);add('FICHA',+m[2],c);add('FICHA',+m[2],c-2);}
 for(const row of cartas.slice(1))for(const c of [258,259])if(row[c]){let m=/^([A-Z]+)(\d+)$/.exec(row[c]);if(!m)throw Error('Carta sem endereço');add('FICHA',+m[2],[...m[1]].reduce((n,x)=>n*26+x.charCodeAt(0)-64,0));}
 add('FICHA',11,4);add('FICHA',11,14);
 for(const p of [[2,13,8,22],[2,27,22,28],[2,48,63,48],[2,56,24,56],[4,11,4,11],[7,11,8,11],[2,57,61,60],[8,67,8,79],[2,80,10,81]])rect('DADOS_PROGRESSAO',...p);
 for(let r=io.notas[0];r<io.notas[0]+io.notas[2];r++)add('DADOS',r,io.notas[1]);
 // O treino usa somente as caixas publicadas nos dois catálogos de armas.
 const capture={};vm.createContext(capture);vm.runInContext(declarations+'\n'+corpo(src,'tabelaDaDados_')+'\n'+corpo(src,'caixasDeTreino_'),capture);
 for(const t of [...capture.caixasDeTreino_(dados).armas,...capture.caixasDeTreino_(dados).grupos]){let m=/^([A-Z]+)(\d+)$/.exec(t.caixa);add('FICHA PESSOAL',+m[2],[...m[1]].reduce((n,x)=>n*26+x.charCodeAt(0)-64,0));}
 const referenceList=[...refs.values()].sort((a,b)=>a[0].localeCompare(b[0])||a[1]-b[1]||a[2]-b[2]);
 const refhash=crypto.createHash('sha256').update(JSON.stringify(referenceList)).digest('hex');
 const eventSchema={hash:refhash,refs:referenceList,grades:Object.fromEntries(['FICHA','FICHA PESSOAL','DADOS_PROGRESSAO','DADOS'].map(n=>{let a=ctx.ABAS.find(a=>a.nome===n);return[n,[a.rows,a.cols]];}))};
 const code=declarations+'\nvar R53_EVENTOS_='+JSON.stringify(eventSchema)+';\nvar R53_CAMINHO_DADOS_='+JSON.stringify(dados)+';\nvar R53_CAMINHO_IP_='+JSON.stringify(pessoal)+';\nvar R53_CAMINHO_CARTAS_='+JSON.stringify(cartas)+';\nvar R53_CAMINHO_IO_='+JSON.stringify(io)+';\n'+fs.readFileSync(path.join(root,'apps-script/Habilidades.gs'),'utf8')+'\n'+helpers+'\n'+fs.readFileSync(path.join(root,'r53/caminho_io.gs'),'utf8')+`\nreturn {editar:function(e){
 R53_CAMINHO_PROGRESSAO_=null;
 var real=e.source||SpreadsheetApp.getActive(),seed=r53CapturarEvento_(real),fila=r53FilaCaminho_(real,seed),ss=R53_CAMINHO_SS_=fila.ss,dados=R53_CAMINHO_DADOS_,idx=indiceDosDados_(dados);
 e=Object.assign({},e,{source:ss,range:fila.range(e.range)});
 if(e.range.getSheet().getName()==='FICHA PESSOAL'){treinoMarcado_(e,e.range.getSheet(),dados,R53_CAMINHO_IP_);fila.aplicar();return;}
 var cc=cel_(idx,'caminho'),ct=cel_(idx,'trilha'),trilhaAntes=cc&&ct&&e.range.getA1Notation()===cc?String(ss.getSheetByName('FICHA').getRange(ct).getValue()):null;
 marcarPericiasDoCaminho_(e,idx,dados);trilhaDoCaminho_(e,idx,dados);
 habilidadesDaFicha_(e,idx);grupoDeArmaDaTrilha_(e,idx);trocaArmaDoCaminho_(e,idx);fichaMexeNaPessoal_(e,idx);
 if(trilhaAntes!==null)r53TrilhaTrocada_(real,fila,ct,trilhaAntes);
 fila.aplicar();
}};`;
 new Function(code);
 const hash=crypto.createHash('sha256').update(code).digest('hex'),payload=z.gzipSync(code,{mtime:0}).toString('base64');
 // Endereços fixos do contrato atual; confirmar contra o índice na conferência.
 const bounds=/^([A-Z]+)(\d+):([A-Z]+)(\d+)$/.exec(pessoal.treino);if(!bounds)throw Error('Treino: faixa inválida');
 const col=t=>[...t].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0),treino=[+bounds[2],col(bounds[1]),+bounds[4],col(bounds[3])];
 const output='// GERADO por r53/caminho_leve.js; regras extraídas de Codigo/Habilidades.\nvar R53_CAMINHO_LEVE_;\nvar R53_TREINO_AREA_='+JSON.stringify(treino)+';\n'+
 'function r53CaminhoLeve_(){if(R53_CAMINHO_LEVE_)return R53_CAMINHO_LEVE_;var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode('+JSON.stringify(payload)+'),"application/gzip")).getDataAsString("UTF-8");var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8).map(function(b){return ("0"+((b+256)%256).toString(16)).slice(-2);}).join("");if(hash!=='+JSON.stringify(hash)+')throw Error("Caminho: pacote divergente");return R53_CAMINHO_LEVE_=(new Function(code))();}\n'+
 `function r53EditarCaminho_(e){
 if(!e||!e.range)return false;var r=e.range;
 if(r.getSheet().getName()==='FICHA PESSOAL'){var a=R53_TREINO_AREA_;if(r.getRow()<a[0]||r.getLastRow()>a[2]||r.getColumn()<a[1]||r.getLastColumn()>a[3])return false;r53CaminhoLeve_().editar(e);return true;}
 if(r.getSheet().getName()!=='FICHA'||r.getRow()!==11||r.getNumRows()!==1)return false;
 var c=r.getColumn();if((c!==4&&c!==14)||r.getNumColumns()>9)return false;
 var ev=Object.assign({},e,{range:r.getCell(1,1)});if(ev.value===undefined)ev.value=ev.range.getValue();
 r53CaminhoLeve_().editar(ev);return true;
}\n`;
 const values=[['R53_EVENTOS_1',refhash],...referenceList.map(p=>{let a="'"+p[0].replace(/'/g,"''")+"'!"+letters(p[2])+p[1];return[p[3],'=IF(ISBLANK('+a+'),"",'+a+')'];})];
 const nativeRows=values.map(row=>({values:row.map((v,c)=>({userEnteredValue:typeof v==='string'&&v.startsWith('=')?{formulaValue:v.replace(/,/g,';')}:{stringValue:v}}))}));
 const requests=[{addSheet:{properties:{sheetId:53018005,title:'R53_EVENTOS',hidden:true,gridProperties:{rowCount:values.length,columnCount:2,hideGridlines:true}}}},{updateCells:{range:{sheetId:53018005,startRowIndex:0,endRowIndex:values.length,startColumnIndex:0,endColumnIndex:2},rows:nativeRows,fields:'userEnteredValue'}}];
 const specEventos={nome:'R53_EVENTOS',rows:values.length,cols:2,larg:100,padrao:['Roboto',10,'#000000'],fundo_base:'#FFFFFF',vals:values.flatMap((row,i)=>row.map((v,c)=>[i+1,c+1,v,0])),estilos:[],fundos:[],bordas:[],merges:[],dv:[],imgs:[],alturas:{},largs:[],oculta:true,paleta_fixa:true,caixas:[],depois:'MONTAGENS',geracao:ctx.GERACAO_,arquivo:'Eventos.gs'};
 const eventosOutput='// GERADO por r53/caminho_leve.js; somente referências a entradas existentes.\nvar ABAS_DOS_EVENTOS='+JSON.stringify([specEventos])+';\nif(typeof juntarAbas_===\'function\')juntarAbas_(ABAS_DOS_EVENTOS);\n';
 new Function(output);return {output,code,hash,helpers:NOMES.length,ioPatches,requests,eventosOutput,eventSchema};
}
if(require.main===module){let d=gerar();fs.writeFileSync(path.join(root,'apps-script/Caminho.gs'),d.output);fs.writeFileSync(path.join(root,'apps-script/Eventos.gs'),d.eventosOutput);fs.writeFileSync(path.join(root,'r53/saidas/eventos-pedidos.json'),JSON.stringify(d.requests));console.log(JSON.stringify({bytes:d.code.length,transporte:d.output.length,hash:d.hash,funcoes:d.helpers,referencias:d.eventSchema.refs.length}));}
module.exports={gerar,corpo,NOMES};
