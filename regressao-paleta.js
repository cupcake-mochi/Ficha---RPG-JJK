// Roda no node, sem Sheets: a troca de paleta em passos (convergirPaleta_, do Codigo.gs) num Sheets de mentira
// montado do estado de fábrica do ABAS (Ficha.gs), com relógio simulado.
//
// 25/09/2026, achado do Mizuki: numa cópia da ficha a cor não trocava, porque o gatilho instalável não viaja na
// cópia; a troca voltou pro gatilho simples, em passos que cabem nos 30 segundos. Com os tempos que ele mediu no
// Sheets, ela não cabia numa execução só. O pedido dele: a execução da troca faz as cores e a régua e termina; a arte
// vai por último e, quando não cabe, entra na próxima vez que alguém mexer na ficha, sem aviso. (Partir da ficha de
// fábrica sem ler a planilha foi tentado e medido: ficou mais lento, e voltou a ler.) Aqui se prova:
//   - nenhuma execução passa de 30 s, e a troca nunca mostra aviso; cor e régua vão aba por aba, a CARTEIRA e a
//     FICHA primeiro, e o que sobra passa na frente quando o jogador abre a aba (o CUSTO de cada chamada é
//     calibrado pelos testes dele, de 25/09/2026);
//   - em passos, a ficha sai igual à troca feita de uma vez pelo mesmo caminho, e nunca misturada;
//   - todo lado de régua do ABAS acaba na régua do tema (referência que não depende do Codigo.gs);
//   - a original pintada pelo esquema de antes converge, e o gatilho instalável velho se apaga.
// No dia, a troca de uma vez também foi comparada contra o repintarPaleta_ antigo, partindo da fábrica, nos 122 temas.
const fs=require('fs'), vm=require('vm'), path=require('path');
const RAIZ=__dirname;
const NOVO=path.join(RAIZ,'apps-script/Codigo.gs'), FICHA=path.join(RAIZ,'apps-script/Ficha.gs');
const FICHA_SRC=fs.readFileSync(FICHA,'utf8');
let falhas=0; const ok=(n,c,d='')=>{console.log((c?'  ok   ':'  FALHA ')+n+(c?'':'  '+d)); if(!c) falhas++;};

// custo das chamadas ao Sheets (ms), calibrado pelos tempos do Mizuki (25/09/2026): um passo de cor, que lia e
// gravava fundo e fonte, levou de 1,5 s (GLOSSÁRIO, 2 mil células) a 4,8 s (FICHA, 7 mil); a régua, uns 300 ms por
// chamada; cada imagem, de 1 a 2 s. ESCALA deixa rodar o mesmo teste com o Sheets mais lento.
let ESCALA=1;
const CUSTO={ler:n=>(150+0.16*n)*ESCALA, escrever:n=>(150+0.16*n)*ESCALA, borda:()=>300*ESCALA,
             imgLer:()=>150*ESCALA, imgEscrever:()=>1100*ESCALA, prop:()=>30, cel:()=>80};
// onde o configurarPaleta_ põe a caixa da paleta na CARTEIRA (do Kaori.xlsx): [linha, coluna, linhas, colunas]
const CAIXA={PALETA_ROTULO:[26,3,1,7,'painel_alto','texto_fraco'],PALETA_ESCOLHIDA:[27,3,2,11,'painel','texto'],
             PALETA_AVISO:[29,3,1,11,'painel','texto_fraco']};
const FABRICA={painel:'#1E1733',painel_alto:'#3D2E78',texto:'#F4F1F7',texto_fraco:'#998BA9'};

function criaPlanilha(ABAS, {id='x'}={}){
  const abas={}, clock={t:0}, props={}, gatilhos=[], log={toasts:[],bordas:{}};
  for(const s of ABAS){
    const bg0=String(s.fundo_base===undefined?'#120F1D':s.fundo_base).toUpperCase();
    const fc0=String((s.padrao||['Roboto',11,'#F4F1F7'])[2]).toUpperCase();
    const bg=[...Array(s.rows)].map(()=>Array(s.cols).fill(bg0)), fc=[...Array(s.rows)].map(()=>Array(s.cols).fill(fc0));
    (s.fundos||[]).forEach(f=>{for(let c=f[1];c<=f[2];c++) bg[f[0]-1][c-1]=String(f[3]).toUpperCase();});
    (s.vals||[]).forEach(t=>{const e=t.length>3?s.estilos[t[3]]:null; if(e&&e[2]) fc[t[0]-1][t[1]-1]=String(e[2]).toUpperCase();});
    const imgs={}; (s.imgs||[]).forEach(im=>{imgs[im[0]+','+im[1]]={nome:im[4],cor:'fabrica'};});
    abas[s.nome]={bg,fc,imgs,valores:{}};
  }
  for(const [r,c,nl,nc,pb,pf] of Object.values(CAIXA))
    for(let i=r-1;i<r-1+nl;i++) for(let j=c-1;j<c-1+nc;j++){ abas.CARTEIRA.bg[i][j]=FABRICA[pb]; abas.CARTEIRA.fc[i][j]=FABRICA[pf]; }
  return {abas,clock,props,gatilhos,log,id};
}
function a1(r,c){let s='';c++;while(c>0){const m=(c-1)%26;s=String.fromCharCode(65+m)+s;c=Math.floor((c-1)/26);}return s+(r+1);}

function carrega(src, P, {autorizado=false}={}){
  const {abas,clock,props,gatilhos,log}=P;
  const gasta=ms=>{clock.t+=Math.round(ms);};   // o Date.now() do Sheets é inteiro
  const sheet=(nome)=>{ const A=abas[nome]; if(!A) return null; return {
    getName:()=>nome,
    getRange:(r,c,nl,nc)=>{
      if(nl===undefined){ const k=r+','+c; return {
        getValue:()=>{gasta(CUSTO.imgLer()); const im=A.imgs[k]; if(nome==='CARTEIRA'&&r===27&&c===3) return A.valores.paleta; if(!im) return ''; return {valueType:'IMAGE',getAltTextTitle:()=>'PM-ARTE:'+im.nome,getAltTextDescription:()=>im.cor};},
        getBackground:()=>A.bg[r-1][c-1], setValue:(v)=>{gasta(CUSTO.imgEscrever()); A.imgs[k].cor=v.desc;},
        getA1Notation:()=>a1(r-1,c-1), getSheet:()=>sheet(nome)}; }
      const n=nl*nc;
      return { getBackgrounds:()=>{gasta(CUSTO.ler(n));log.leituras=(log.leituras||0)+1;return A.bg.map(l=>l.slice());},
        getFontColors:()=>{gasta(CUSTO.ler(n));log.leituras=(log.leituras||0)+1;return A.fc.map(l=>l.slice());},
        setBackgrounds:(m)=>{gasta(CUSTO.escrever(n));A.bg=m.map(l=>l.slice());}, setFontColors:(m)=>{gasta(CUSTO.escrever(n));A.fc=m.map(l=>l.slice());} };
    },
    // a borda fica registrada faixa a faixa e lado a lado: o que importa é a cor de cada lado, não como foi pedida
    getRangeList:(lista)=>({setBorder:(t,l,b,r,v,h,cor)=>{gasta(CUSTO.borda()); log.chamadasBorda=(log.chamadasBorda||0)+1;
      for(const f of lista) [['top',t],['left',l],['bottom',b],['right',r]].forEach(([n,x])=>{ if(x) log.bordas[nome+'|'+f+'|'+n]=cor; });}}),
  };};
  const celPaleta={getA1Notation:()=>'C27',getSheet:()=>sheet('CARTEIRA'),getValue:()=>{gasta(CUSTO.cel());return abas.CARTEIRA.valores.paleta;},getCell:()=>celPaleta,
    setBorder:(...a)=>{log.bordas['caixa']=a[6];}};
  const nomeado=(n)=>{ const [r,c,nl,nc]=CAIXA[n]; return {getA1Notation:()=>a1(r-1,c-1)+':'+a1(r+nl-2,c+nc-2),getSheet:()=>sheet('CARTEIRA'),
    getCell:()=>n==='PALETA_ESCOLHIDA'?celPaleta:null,getRow:()=>r,getColumn:()=>c,getNumRows:()=>nl,getNumColumns:()=>nc,
    setBorder:(...a)=>{log.bordas['caixa:'+n]=a[6];}}; };
  const ss={getId:()=>P.id,getSheetByName:sheet,getRangeByName:n=>CAIXA[n]?nomeado(n):null,
    toast:(m)=>log.toasts.push(m)};
  const precisa=()=>{ if(!autorizado) throw new Error('sem permissão'); };
  const ctx={console:{log:()=>{}}, Logger:{log:(m)=>{log.registro=m;}}, Utilities:{ base64Decode: s => Array.from(Buffer.from(s, 'base64')).map(x => (x > 127 ? x - 256 : x)),
    base64Encode: a => Buffer.from(a.map(x => x & 255)).toString('base64'), sleep: ()=>{} },
    Date:{now:()=>clock.t},
    SpreadsheetApp:{getActive:()=>ss, flush:()=>{}, ValueType:{IMAGE:'IMAGE'}, BorderStyle:new Proxy({},{get:(o,k)=>k}),
      newCellImage:()=>{const b={desc:null,setSourceUrl(){return b;},setAltTextTitle(){return b;},setAltTextDescription(d){b.desc=d;return b;},build(){return b;}};return b;}},
    ScriptApp:{getProjectTriggers:()=>{precisa();return gatilhos.map(g=>({getHandlerFunction:()=>g}));},deleteTrigger:(t)=>{precisa();gatilhos.splice(gatilhos.indexOf(t.getHandlerFunction()),1);}},
    PropertiesService:{getDocumentProperties:()=>({getProperty:k=>{gasta(CUSTO.prop());return k in props?props[k]:null;},setProperty:(k,v)=>{gasta(CUSTO.prop());props[k]=String(v);},
      setProperties:(o)=>{gasta(CUSTO.prop());Object.assign(props,o);},deleteProperty:k=>{gasta(CUSTO.prop());delete props[k];}})},
    LockService:{getDocumentLock:()=>({tryLock:()=>true,releaseLock:()=>{}})},
  };
  vm.createContext(ctx); vm.runInContext(FICHA_SRC,ctx); vm.runInContext(src,ctx);
  return {ctx,ss,celPaleta,sheet};
}

const SRC_NOVO=fs.readFileSync(NOVO,'utf8');
const ctx0={}; vm.createContext(ctx0); vm.runInContext(FICHA_SRC,ctx0); const ABAS=ctx0.ABAS;

// a referência: a mesma convergirPaleta_, de uma vez só, com orçamento infinito
function umaVez(sequencia){
  const P=criaPlanilha(ABAS); const {ctx}=carrega(SRC_NOVO,P);
  for(const n of sequencia){ P.abas.CARTEIRA.valores.paleta=n; ctx.convergirPaleta_(P.clock.t,Infinity); }
  return P;
}
// gatilhos simples, cada um com o próprio relógio; devolve o que cada execução fez
function emPassos(P, escolhas, {cliquesEntre=0}={}){
  const {ctx,celPaleta}=carrega(SRC_NOVO,P,{autorizado:false});
  const execs=[];
  const roda=(tipo,fn)=>{ const t0=P.clock.t, antes=JSON.parse(P.props.paleta_feito||'{}'); fn();
    const depois=JSON.parse(P.props.paleta_feito||'{}');
    execs.push({tipo, ms:P.clock.t-t0, passos:Object.keys(depois).filter(k=>depois[k]!==antes[k])}); P.clock.t+=500; };
  for(const [i,n] of escolhas.entries()){
    P.abas.CARTEIRA.valores.paleta=n;
    roda('troca',()=>ctx.onEdit({range:celPaleta,value:n}));
    const limite = i<escolhas.length-1 ? cliquesEntre : 50;
    for(let k=0;k<limite && P.props.paleta_pendente;k++) roda('clique',()=>ctx.onSelectionChange({}));
  }
  return {execs, maior:Math.max(...execs.map(e=>e.ms)), ctx};
}
function igual(P,Q){
  for(const nome of Object.keys(P.abas)){
    const a=P.abas[nome], b=Q.abas[nome];
    for(let r=0;r<a.bg.length;r++) for(let c=0;c<a.bg[r].length;c++){
      if(a.bg[r][c]!==b.bg[r][c]) return `${nome}!${a1(r,c)} fundo ${a.bg[r][c]} x ${b.bg[r][c]}`;
      if(a.fc[r][c]!==b.fc[r][c]) return `${nome}!${a1(r,c)} fonte ${a.fc[r][c]} x ${b.fc[r][c]}`;
    }
    for(const k of Object.keys(a.imgs)) if(a.imgs[k].cor!==b.imgs[k].cor) return `${nome} arte ${k} ${a.imgs[k].cor} x ${b.imgs[k].cor}`;
  }
  for(const k of new Set([...Object.keys(P.log.bordas),...Object.keys(Q.log.bordas)])) if(P.log.bordas[k]!==Q.log.bordas[k]) return `borda ${k} ${P.log.bordas[k]} x ${Q.log.bordas[k]}`;
  return '';
}
const semArte=(ps)=>ps.filter(p=>!p.startsWith('arte:'));
const resumo=(r)=>r.execs.map(e=>`${e.tipo} ${(e.ms/1000).toFixed(1)} s (${e.passos.length} passos)`).join(' → ');

const E='Eucalipto · Escuro', M='Mizuki · Claro', B='Brasa · Claro';
const visiveis=ABAS.filter(s=>!s.oculta).map(s=>s.nome);
const daAba=(ps,aba)=>ps.filter(p=>p.split(':')[1]===aba && !p.startsWith('arte:'));
const regua=(P,n)=>{ const rg='#'+String(r.ctx.coresDoNome_(n).regua).toUpperCase(); const falta=[];
  for(const s of ABAS) for(const b of (s.bordas||[])){ if(String(b[2]).toUpperCase()!=='#8A7EC4') continue;
    for(const f of b[3]) if(P.log.bordas[s.nome+'|'+f+'|'+b[0]]!==rg) falta.push(s.nome+'!'+f+' '+b[0]); }
  return falta; };

console.log('1. cópia nova, primeira troca (nenhum passo medido ainda)');
let P=criaPlanilha(ABAS); let r=emPassos(P,[E]);
console.log('       '+resumo(r));
ok('terminou', !P.props.paleta_pendente);
ok(`nenhuma execução passou de 30 s (maior: ${(r.maior/1000).toFixed(1)} s)`, r.maior<=30000);
ok('a CARTEIRA e a FICHA (cor e régua) entraram na execução da troca',
   ['CARTEIRA','FICHA'].every(a=>daAba(r.ctx.passosDaPaleta_(),a).every(p=>r.execs[0].passos.includes(p))), r.execs[0].passos.join(', '));
ok('nenhum aviso na tela', P.log.toasts.length===0, P.log.toasts.join(' | '));
ok('igual, célula a célula, à troca feita de uma vez só', !igual(P,umaVez([E])), igual(P,umaVez([E])));
{ const fab=new Set(['120F1D','1E1733','3D2E78','493F54','F4F1F7','998BA9','0A0810','17131F','1B142F','756588','211940','3B3360'].map(h=>'#'+h));
  const sobra={bg:0,fc:0};
  for(const s of ABAS){ if(s.oculta) continue; const A=P.abas[s.nome];
    for(const l of A.bg) for(const x of l) if(fab.has(x)) sobra.bg++;
    for(const l of A.fc) for(const x of l) if(fab.has(x)) sobra.fc++; }
  ok('nenhum fundo nem fonte das abas visíveis ficou na cor de fábrica', !sobra.bg && !sobra.fc, JSON.stringify(sobra)); }
{ const falta=regua(P,E); ok('todo lado de régua do ABAS acaba na régua do tema', falta.length===0, falta.slice(0,4).join(', ')); }
ok('a caixa da paleta volta com os papéis dela (valor no painel, rótulo no painel_alto)',
   P.abas.CARTEIRA.bg[26][2]==='#'+r.ctx.coresDoNome_(E).painel.toUpperCase() && P.abas.CARTEIRA.bg[25][2]==='#'+r.ctx.coresDoNome_(E).painel_alto.toUpperCase());
ok('paleta_atual gravada no fim', P.props.paleta_atual===E);
P.props.paleta_tempos=JSON.stringify(Object.assign(JSON.parse(P.props.paleta_tempos),{'cor:DADOS':99999}));
{ const {ctx}=carrega(SRC_NOVO,P); ctx.verTemposDaPaleta(); const reg=P.log.registro||'';
  ok('o relatório diz a versão, ignora passo de versão anterior, conta as execuções e mostra o passo de cor por dentro',
     /versão do Codigo\.gs: /.test(reg) && !/cor:DADOS/.test(reg) && /em \d+ execução/.test(reg) && /do começo ao fim \d+ ms/.test(reg)
     && /FICHA \(7050 células\): lê \d+ ms, conta \d+ ms, grava fundo \d+ ms, grava fonte \d+ ms/.test(reg), reg.split('\n').slice(0,3).join(' / ')); }

console.log('2. segunda troca, com os tempos medidos');
P.log.toasts=[]; r=emPassos(P,[M]); console.log('       '+resumo(r));
ok(`nenhuma execução passou de 30 s (maior: ${(r.maior/1000).toFixed(1)} s)`, r.maior<=30000);
ok('cor e régua de todas as abas na execução da troca, sem aviso',
   visiveis.every(a=>daAba(r.ctx.passosDaPaleta_(),a).every(p=>r.execs[0].passos.includes(p))) && P.log.toasts.length===0, r.execs[0].passos.join(', '));
ok('igual a E→M de uma vez', !igual(P,umaVez([E,M])), igual(P,umaVez([E,M])));

console.log('3. troca no meio de outra');
function caminhoLimpo(P, refs){ const achou={}; let todas=true;
  for(const s of ABAS){ if(s.oculta) continue; const a=P.abas[s.nome];
    const k=Object.keys(refs).find(k=>{const b=refs[k].abas[s.nome]; return JSON.stringify(a.bg)===JSON.stringify(b.bg)&&JSON.stringify(a.fc)===JSON.stringify(b.fc);});
    if(!k) todas=false; achou[s.nome]=k||'NENHUM'; }
  return {todas, achou}; }
P=criaPlanilha(ABAS); r=emPassos(P,[E,B],{cliquesEntre:1});
{ const c=caminhoLimpo(P,{'E→B':umaVez([E,B]),'B':umaVez([B])}); ok('E, um clique, B: cada aba é um caminho limpo até B '+JSON.stringify(c.achou), !P.props.paleta_pendente && c.todas); }
P=criaPlanilha(ABAS); r=emPassos(P,[E,M,B]);
{ const c=caminhoLimpo(P,{'E→M→B':umaVez([E,M,B]),'M→B':umaVez([M,B]),'E→B':umaVez([E,B]),'B':umaVez([B])});
  ok('E, M, B sem clique entre elas: cada aba é um caminho limpo até B '+JSON.stringify(c.achou), c.todas); }

console.log('4. a original do Mizuki, pintada pelo esquema de antes (paleta_atual, sem paleta_feito)');
P=umaVez([M]); P.props={paleta_atual:M}; P.gatilhos=['aplicarPaleta_']; P.log.toasts=[];
r=emPassos(P,[E]);
ok('igual a M→E de uma vez', !igual(P,umaVez([M,E])), igual(P,umaVez([M,E])));
{ const {ctx}=carrega(SRC_NOVO,P,{autorizado:true}); ctx.aplicarPaleta_({}); ok('o gatilho velho se apaga sozinho', P.gatilhos.length===0); }

console.log('5. cor pintada à mão pelo jogador');
P=umaVez([M]); P.abas.FICHA.bg[40][10]='#FFFF00'; r=emPassos(P,[E]);
ok('fica na troca de tema', P.abas.FICHA.bg[40][10]==='#FFFF00');

console.log('6. o que não cabe: a aba em que o jogador clica passa na frente, e ninguém é avisado');
ESCALA=1.4; P=criaPlanilha(ABAS);
{ const {ctx:C,celPaleta:cp}=carrega(SRC_NOVO,P); P.abas.CARTEIRA.valores.paleta=E;
  C.onEdit({range:cp,value:E});
  const feito=()=>JSON.parse(P.props.paleta_feito||'{}'); const falta=()=>C.passosDaPaleta_().filter(k=>feito()[k]!==E);
  const f0=falta(); console.log('       ficou pra depois da troca: '+f0.join(', '));
  ok('com o Sheets 40% mais lento, a CARTEIRA e a FICHA entraram na troca, e sobrou trabalho',
     f0.length>0 && ['CARTEIRA','FICHA'].every(a=>daAba(f0.concat(),a).length===0), f0.join(', '));
  const alvo=visiveis.filter(a=>daAba(f0,a).length).pop();
  ok('há uma aba com cor ou régua pendente pra testar o clique', !!alvo, f0.join(', '));
  if(alvo){ P.clock.t+=500; const ini=P.clock.t; const cel={getSheet:()=>({getName:()=>alvo}),getA1Notation:()=>'B5'};
    const antes=feito(); C.onSelectionChange({range:cel});
    const ordem=Object.keys(feito()).filter(k=>feito()[k]===E && antes[k]!==E);
    ok(`clicar na ${alvo} pinta a ${alvo} primeiro`, daAba(ordem,alvo).length>0 && ordem.indexOf(daAba(ordem,alvo)[0])===0, ordem.join(', ')); }
  for(let k=0;k<20 && P.props.paleta_pendente;k++){ P.clock.t+=500; C.onSelectionChange({range:{getSheet:()=>({getName:()=>'GLOSSÁRIO'})}}); }
  ok('os cliques seguintes terminam tudo', !P.props.paleta_pendente && !igual(P,umaVez([E])), igual(P,umaVez([E])));
  ok('e nenhum aviso apareceu em momento nenhum', P.log.toasts.length===0, P.log.toasts.join(' | ')); }
// a edição também continua ("caso alguém mexa na ficha"): outra troca do zero, e uma edição fora da FICHA logo depois
P=criaPlanilha(ABAS);
{ const {ctx:C,celPaleta:cp}=carrega(SRC_NOVO,P); P.abas.CARTEIRA.valores.paleta=E; C.onEdit({range:cp,value:E});
  const antes=P.props.paleta_feito; P.clock.t+=500;
  C.onEdit({range:{getSheet:()=>({getName:()=>'INVOCAÇÃO'}),getA1Notation:()=>'B5'},value:'x'});
  ok('uma edição fora da FICHA continua a troca pendente', !!P.props.paleta_pendente===false || P.props.paleta_feito!==antes, 'nada andou'); }
ESCALA=1;

console.log('6b. a estimativa de passo ainda não medido cobre o custo (calibrado pelos tempos do Mizuki)');
{ const Q=umaVez([E]); const {ctx}=carrega(SRC_NOVO,Q); const t=JSON.parse(Q.props.paleta_tempos); const baixa=[];
  for(const k of Object.keys(t)) if(ctx.estimativaDoPasso_(k) < t[k]) baixa.push(`${k}: estima ${ctx.estimativaDoPasso_(k)}, custa ${t[k]}`);
  ok('nenhum passo custa mais do que a estimativa dele', baixa.length===0, baixa.join(' · ')); }

console.log('7. escolher a mesma paleta de novo, e clicar sem nada pendente');
P=umaVez([E]); const antesT=P.clock.t; r=emPassos(P,[E]);
ok('não repinta nada', P.clock.t-antesT < 3000, `${P.clock.t-antesT} ms`);
{ const {ctx}=carrega(SRC_NOVO,P); const t0=P.clock.t; let leu=false;
  ctx.onSelectionChange({range:{getSheet:()=>{leu=true; return {getName:()=>'FICHA'};}}});
  ok('clique sem pendente custa uma leitura de propriedade, e não lê a aba', P.clock.t-t0<=CUSTO.prop() && !leu, `${P.clock.t-t0} ms, leu a aba: ${leu}`); }

console.log('8. o Sheets três vezes mais lento');
ESCALA=3; P=criaPlanilha(ABAS); r=emPassos(P,[E]); console.log('       '+resumo(r));
ok(`nenhuma execução passou de 30 s (maior: ${(r.maior/1000).toFixed(1)} s)`, r.maior<=30000);
ok('termina igual à troca de uma vez, sem aviso', !P.props.paleta_pendente && !igual(P,umaVez([E])) && P.log.toasts.length===0);
ESCALA=1;

console.log('9. um passo sozinho mais lento que o orçamento não trava a troca pra sempre');
P=criaPlanilha(ABAS); P.props.paleta_tempos=JSON.stringify({'cor:FICHA':40000}); r=emPassos(P,[E]);
ok('terminou mesmo assim', !P.props.paleta_pendente && !igual(P,umaVez([E])));

console.log(falhas?`\n${falhas} FALHA(S)`:'\nTODOS PASSARAM'); process.exit(falhas?1:0);
