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
    abas[s.nome]={bg,fc,imgs,valores:{},vals:s.vals||[],rows:s.rows};
  }
  for(const [r,c,nl,nc,pb,pf] of Object.values(CAIXA))
    for(let i=r-1;i<r-1+nl;i++) for(let j=c-1;j<c-1+nc;j++){ abas.CARTEIRA.bg[i][j]=FABRICA[pb]; abas.CARTEIRA.fc[i][j]=FABRICA[pf]; }
  return {abas,clock,props,gatilhos,log,id};
}
function a1(r,c){let s='';c++;while(c>0){const m=(c-1)%26;s=String.fromCharCode(65+m)+s;c=Math.floor((c-1)/26);}return s+(r+1);}

function carrega(src, P, {autorizado=false}={}){
  const {abas,clock,props,gatilhos,log}=P;
  const gasta=ms=>{clock.t+=Math.round(ms);};   // o Date.now() do Sheets é inteiro
  // o valor de uma célula da DADOS como o script a lê: o texto do ABAS, e o endereço quando a fórmula é um ADDRESS
  const valorDe=v=>{ if(typeof v!=='string'||v[0]!=='=') return v;
    const m=/^=ADDRESS\(ROW\((?:'[^']+'|[A-ZÇÃ_]+)!\$?([A-Z]+)\$?(\d+)\)/.exec(v.replace(/\s/g,'')); return m?m[1]+m[2]:''; };
  const sheet=(nome)=>{ const A=abas[nome]; if(!A) return null; return {
    getName:()=>nome, getLastRow:()=>A.rows,
    getRange:(r,c,nl,nc)=>{
      // 01/10/2026, a barra cheia: a troca lê o índice da FICHA PESSOAL (duas colunas da DADOS) e grava uma célula
      if(typeof r==='string') return { getValue:()=>{gasta(CUSTO.cel()); return A.valores[r]===undefined?'':A.valores[r];},
        setValue:(v)=>{gasta(CUSTO.cel()); A.valores[r]=v;} };
      if(nl!==undefined && nome==='DADOS') return { getValues:()=>{ gasta(CUSTO.ler(nl*nc)); const m=[...Array(nl)].map(()=>Array(nc).fill(''));
        A.vals.forEach(t=>{const i=t[0]-r,j=t[1]-c; if(i>=0&&i<nl&&j>=0&&j<nc) m[i][j]=valorDe(t[2]);}); return m; } };
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
  if(JSON.stringify(P.abas.DADOS.valores)!==JSON.stringify(Q.abas.DADOS.valores)) return `barra ${JSON.stringify(P.abas.DADOS.valores)} x ${JSON.stringify(Q.abas.DADOS.valores)}`;
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
// 01/10/2026, a revisão das cores. Referências que não dependem do Codigo.gs: a barra, a tinta de enfeite e a arte.
const hexDe=(n,k)=>'#'+String(r.ctx.coresDoNome_(n)[k]).toUpperCase();
const lumDe=(h)=>[0,2,4].reduce((s,i,j)=>{const c=parseInt(h.substr(1+i,2),16)/255; return s+[0.2126,0.7152,0.0722][j]*(c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4));},0);
const contr=(a,b)=>{const x=lumDe(a),y=lumDe(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05);};
const matiz=(h)=>{const R=parseInt(h.substr(1,2),16),G=parseInt(h.substr(3,2),16),B=parseInt(h.substr(5,2),16),mx=Math.max(R,G,B),mn=Math.min(R,G,B),d=mx-mn;
  if(!d) return null; const x=mx===R?((G-B)/d+6)%6:mx===G?(B-R)/d+2:(R-G)/d+4; return x*60;};
const enfeiteDoAbas=()=>{ const out=[]; for(const s of ABAS){ if(s.oculta) continue; (s.vals||[]).forEach(t=>{ const e=t.length>3?s.estilos[t[3]]:null;
  const cor=e&&String(e[2]||'').toUpperCase(); if(cor==='#756588') out.push([s.nome,t[0],t[1],'bloco']); if(cor==='#493F54') out.push([s.nome,t[0],t[1],'linha']); }); } return out; };
const enfeiteFora=(P,n)=>enfeiteDoAbas().filter(([aba,l,c,papel])=>P.abas[aba].fc[l-1][c-1]!==hexDe(n,papel)).map(x=>x.join(' '));
// a célula da barra é a conta "cor da barra cheia" da DADOS: o rótulo, e o valor na coluna seguinte (o osso de fábrica)
const celBarra=()=>{ const V=ABAS.find(s=>s.nome==='DADOS').vals; const viz=t=>V.find(x=>x[0]===t[0]&&x[1]===t[1]+1);
  const t=V.find(t=>t[2]==='cor da barra cheia' && viz(t) && viz(t)[2]==='#E8DCD4'); return t?a1(t[0]-1,t[1]):'?'; };
ok('a barra cheia é gravada na DADOS, na conta "cor da barra cheia", com a barra do tema', P.abas.DADOS.valores[celBarra()]===hexDe(E,'barra'),
   `${celBarra()} = ${P.abas.DADOS.valores[celBarra()]}, e a do tema é ${hexDe(E,'barra')}`);
ok(`as ${enfeiteDoAbas().length} letras de enfeite (a marca, o número, a lombada) saem no bloco e na linha do tema`, enfeiteDoAbas().length>=10 && enfeiteFora(P,E).length===0, enfeiteFora(P,E).slice(0,4).join(', '));
{ const ruins=[]; const papelDaArte=r.ctx.PAPEL_DA_ARTE_;
  for(const s of ABAS) for(const im of (s.imgs||[])){ const cor=P.abas[s.nome].imgs[im[0]+','+im[1]].cor, fundo=P.abas[s.nome].bg[im[0]-1][im[1]-1];
    const papel=papelDaArte[String(im[4]).replace(/-\d+x\d+\.png$/,'')], doPapel=hexDe(E,papel);
    const mesmoMatiz=matiz(cor)!==null&&matiz(doPapel)!==null&&Math.min(Math.abs(matiz(cor)-matiz(doPapel)),360-Math.abs(matiz(cor)-matiz(doPapel)))<=4;
    if(contr(cor,fundo)<3 || !(cor===doPapel||cor===hexDe(E,'acento')||mesmoMatiz)) ruins.push(`${s.nome} ${im[4]} ${cor}`); }
  ok('cada imagem aparece (3,0 sobre o fundo dela) e é a cor do papel dela, o acento do tema ou o papel dela no mesmo matiz', ruins.length===0, ruins.join(', ')); }
P.props.paleta_tempos=JSON.stringify(Object.assign(JSON.parse(P.props.paleta_tempos),{'cor:DADOS':99999}));
{ const {ctx}=carrega(SRC_NOVO,P); ctx.verTemposDaPaleta(); const reg=P.log.registro||'';
  ok('o relatório diz a versão, ignora passo de versão anterior, conta as execuções e mostra o passo de cor por dentro',
     /versão do Codigo\.gs: /.test(reg) && !/cor:DADOS/.test(reg) && /em \d+ execução/.test(reg) && /do começo ao fim \d+ ms/.test(reg)
     && /FICHA \(7050 células\): lê \d+ ms, conta \d+ ms, grava fundo \d+ ms, grava fonte \d+ ms/.test(reg), reg.split('\n').slice(0,3).join(' / ')); }

console.log('2. segunda troca, com os tempos medidos');
P.log.toasts=[]; r=emPassos(P,[M]); console.log('       '+resumo(r));
ok(`nenhuma execução passou de 30 s (maior: ${(r.maior/1000).toFixed(1)} s)`, r.maior<=30000);
// 01/10/2026: com a FICHA PESSOAL (4.920 células; a FICHA tem 7.050) cor e régua de todas as abas deixaram de caber
// numa execução. A troca pinta as que o jogador vê primeiro — a CARTEIRA, a FICHA e a FICHA PESSOAL — e o resto
// termina no clique seguinte, sem aviso, como a arte já terminava.
// Com a FICHA AMALDIÇOADA (11 mil células, em 21 colunas) a terceira aba da ordem passou a ser ela: a troca pinta a
// CARTEIRA, a FICHA e a FICHA AMALDIÇOADA, e a FICHA PESSOAL, o GLOSSÁRIO e a arte terminam no clique seguinte. A aba
// em que o jogador clica continua passando na frente (o teste 6).
const PRIMEIRAS=['CARTEIRA','FICHA','FICHA AMALDIÇOADA'];
ok('cor e régua da CARTEIRA, da FICHA e da FICHA AMALDIÇOADA na execução da troca, sem aviso',
   PRIMEIRAS.every(a=>daAba(r.ctx.passosDaPaleta_(),a).every(p=>r.execs[0].passos.includes(p))) && P.log.toasts.length===0, r.execs[0].passos.join(', '));
ok('as outras abas terminam no primeiro clique depois da troca',
   r.execs.length===2 && visiveis.every(a=>daAba(r.ctx.passosDaPaleta_(),a).every(p=>r.execs[0].passos.concat(r.execs[1].passos).includes(p))), resumo(r));
ok('igual a E→M de uma vez', !igual(P,umaVez([E,M])), igual(P,umaVez([E,M])));
ok('depois da segunda troca a barra e as letras de enfeite são as do tema novo, sem depender do anterior',
   P.abas.DADOS.valores[celBarra()]===hexDe(M,'barra') && enfeiteFora(P,M).length===0, `${P.abas.DADOS.valores[celBarra()]} · ${enfeiteFora(P,M).slice(0,4).join(', ')}`);

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

console.log('5b. a cor de aviso acesa na hora da troca não fica gravada na célula');
// Achado do Mizuki em 01/10/2026, na planilha exportada: o getBackgrounds() devolve a cor que a regra de aviso está
// mostrando. Aqui a regra acesa é imitada pondo o vermelho e o branco de estado (e o âmbar, noutra célula) na grade
// que a troca lê: depois da troca, a cor gravada tem de ser a do papel da célula, igual à de uma troca sem aviso.
{ const AM='FICHA AMALDIÇOADA', S=ABAS.find(s=>s.nome===AM);
  const comValor=S.vals.filter(t=>typeof t[2]==='string' && t[2][0]==='=' && t[0]>=30);     // caixas calculadas, onde o aviso acende
  const [la,ca]=[comValor[0][0]-1, comValor[0][1]-1], [lb,cb]=[comValor[1][0]-1, comValor[1][1]-1];
  ok('a aba tem caixas que podem acender o aviso', comValor.length>=2, String(comValor.length));
  const limpa=umaVez([E]);
  P=criaPlanilha(ABAS); P.abas[AM].bg[la][ca]='#C2334D'; P.abas[AM].fc[la][ca]='#FFFFFF'; P.abas[AM].fc[lb][cb]='#D89B3A'; r=emPassos(P,[E]);
  ok('o vermelho de estado aceso na troca não vira o fundo da célula', P.abas[AM].bg[la][ca]===limpa.abas[AM].bg[la][ca] && P.abas[AM].fc[la][ca]===limpa.abas[AM].fc[la][ca],
     `${P.abas[AM].bg[la][ca]} ${P.abas[AM].fc[la][ca]}, e a troca limpa dá ${limpa.abas[AM].bg[la][ca]} ${limpa.abas[AM].fc[la][ca]}`);
  ok('o âmbar de estado aceso na troca não vira a fonte da célula', P.abas[AM].fc[lb][cb]===limpa.abas[AM].fc[lb][cb], `${P.abas[AM].fc[lb][cb]} != ${limpa.abas[AM].fc[lb][cb]}`);
  ok('a planilha inteira termina igual à da troca sem aviso', !igual(P,limpa), igual(P,limpa));
  // a planilha que uma troca antiga deixou com o vermelho gravado: a troca seguinte desfaz
  P=umaVez([E]); P.abas[AM].bg[la][ca]='#C2334D'; P.abas[AM].fc[la][ca]='#FFFFFF'; r=emPassos(P,[M]);
  ok('o vermelho que uma troca antiga gravou sai na troca seguinte', !igual(P,umaVez([E,M])), igual(P,umaVez([E,M]))); }

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

console.log('10. a revisão das cores de 01/10/2026: a lombada que ficou presa noutro papel volta, e a arte nas 122');
// a ficha pintada pelo esquema de antes: a rede de legibilidade trocava a lombada pelo acento, e ela ficava "acento" pra sempre
P=umaVez([M]);
{ const {ctx}=carrega(SRC_NOVO,P); const presa='#'+String(ctx.coresDoNome_(M).acento).toUpperCase();
  for(const [aba,l,c,papel] of enfeiteDoAbas()) if(papel==='linha') P.abas[aba].fc[l-1][c-1]=presa; }
r=emPassos(P,[E]);
ok('a lombada que uma troca antiga deixou na cor do acento volta pra linha do tema (é achada pelo endereço, e não pela cor)',
   enfeiteFora(P,E).length===0, enfeiteFora(P,E).slice(0,4).join(', '));
{ const {ctx}=carrega(SRC_NOVO,criaPlanilha(ABAS)); const ruins=[], usos={papel:0,acento:0,matiz:0};
  const ondeMora={carteira:'tinta',ficha:'fundo'};
  for(const tema of Object.keys(ctx.PALETAS)) for(const v of ['Claro','Escuro']){ const n=tema+' · '+v, p=ctx.coresDoNome_(n);
    for(const [img,papel] of Object.entries(ctx.PAPEL_DA_ARTE_)){ const fundo='#'+String(p[ondeMora[img.split('-')[0]]]).toUpperCase();
      const doPapel='#'+String(p[papel]).toUpperCase(), acento='#'+String(p.acento).toUpperCase(), cor=ctx.corDaArte_(p,papel,fundo);
      const esperado = contr(doPapel,fundo)>=3 ? 'papel' : contr(acento,fundo)>=3 ? 'acento' : 'matiz';
      const dm=matiz(cor)===null||matiz(doPapel)===null?0:Math.min(Math.abs(matiz(cor)-matiz(doPapel)),360-Math.abs(matiz(cor)-matiz(doPapel)));
      const certo = contr(cor,fundo)>=3 && (esperado==='papel'?cor===doPapel:esperado==='acento'?cor===acento:dm<=4);
      usos[esperado]++; if(!certo) ruins.push(`${n} ${img}: ${cor} (esperado: ${esperado})`); } }
  ok(`nas 122 paletas cada imagem sai na cor do papel dela (${usos.papel}), e só quando ela não aparece no acento do tema (${usos.acento}) ou no mesmo matiz (${usos.matiz})`,
     ruins.length===0 && usos.papel>0 && usos.acento>0, ruins.slice(0,4).join(' · '));
  // um tema que não existe, onde nem a régua nem o acento aparecem: sobra a régua no mesmo matiz, mais escura
  const falso={regua:'F3E9A0',acento:'F5F0C8',texto:'101010'}, saiu=ctx.corDaArte_(falso,'regua','#FFFBEA');
  ok('quando nem o papel nem o acento aparecem, a imagem fica no matiz do papel dela, escurecida até aparecer, e nunca noutra cor',
     contr(saiu,'#FFFBEA')>=3 && Math.abs(matiz(saiu)-matiz('#F3E9A0'))<=4 && saiu!=='#101010', saiu);
  const bloco=[], linha=[], barra=[];
  for(const tema of Object.keys(ctx.PALETAS)) for(const v of ['claro','escuro']){ const p=ctx.PALETAS[tema][v], h=k=>'#'+String(p[k]).toUpperCase();
    for(const f of ['tinta','fundo','papel']){ if(contr(h('bloco'),h(f))<3.5) bloco.push(`${tema} ${v} ${f}`); if(contr(h('linha'),h(f))<3.0) linha.push(`${tema} ${v} ${f}`); }
    if(!p.barra || contr(h('barra'),h('painel'))<3.0) barra.push(`${tema} ${v}`); }
  ok('nas 122 o bloco lê 3,5 e a linha lê 3,0 sobre a tinta, o fundo e o papel: a tinta de enfeite nunca depende da rede de legibilidade',
     bloco.length===0 && linha.length===0, bloco.concat(linha).slice(0,4).join(' · '));
  ok('nas 122 a barra cheia existe e lê 3,0 sobre o painel, que é onde as barras moram', barra.length===0, barra.slice(0,4).join(' · ')); }

console.log(falhas?`\n${falhas} FALHA(S)`:'\nTODOS PASSARAM'); process.exit(falhas?1:0);
