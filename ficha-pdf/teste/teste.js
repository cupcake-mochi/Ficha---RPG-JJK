const {chromium}=require('playwright');
(async()=>{
 const pdf=process.argv[2]||'ficha-ciclo-maldito-mizuki-escuro.pdf';
 // Caso de teste: a Kaori do livro (cap. 4), depois no nível 10 com ajustes.
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1100,height:1500}});
 p.on('console',m=>{ if(m.type()==='error') console.log('CONSOLE',m.text())});
 await p.goto('http://localhost:8765/viewer.html?file='+pdf);
 await p.waitForSelector('.annotationLayer input',{timeout:20000});
 await p.waitForTimeout(1500);
 const nomes=await p.$$eval('.annotationLayer [name]',e=>e.slice(0,8).map(x=>x.tagName+':'+x.name));
  const sel=n=>`.annotationLayer [name="${n}"]`;
 async function digita(n,v){const e=await p.$(sel(n)); await e.click(); await e.fill(String(v)); await p.keyboard.press('Tab'); await p.waitForTimeout(250);}
 async function marca(n){await p.click(sel(n)); await p.waitForTimeout(250);}
 async function escolhe(n,v){await p.selectOption(sel(n),v); await p.waitForTimeout(250);}
 await escolhe('caminho','Bastião');
 for (const [k,v] of [['atr_for',3],['atr_des',2],['atr_con',2],['atr_int',1],['atr_ess',1],['prot_equip',1]]) await digita(k,v);
 await escolhe('tec_atr','FOR'); await escolhe('tr_fis_atr','FOR');
 await marca('tr_fis_t'); await marca('tr_vig_t'); await marca('per_atletismo_t');
 await digita('f1_classe',1);
 await p.waitForTimeout(800);
 const ler=async n=>p.$eval(sel(n),e=>e.value);
 const esperado={maestria:'+1',espacos:'3',classe0:'2',classe_max:'1',refino:'1',vida_max:'23',pe_max:'8',integ_max:'26',protecao:'1',defesa:'13',bloquear:'2d10 + 2',iniciativa:'+2',deslocamento:'9 m',cd_tec:'12',atq_tec:'+4',atq_cac:'+4',atq_dist:'+3',carga:'8',per_atletismo:'+4',per_acrobacia:'+2',per_percepcao:'+1',tr_fis:'+4',tr_vig:'+3',tr_itl:'+1',tr_esp:'+1',of_forja:'-',morr_aguentar:'6',morr_ins1:'8',morr_ins2:'12',morr_janela:'3 rodadas',f1_pe:'3'};
 let ok=0,falha=0;
 for(const [k,v] of Object.entries(esperado)){const r=await ler(k); if(r===v)ok++; else {falha++; console.log('FALHA',k,'esperado',v,'veio',JSON.stringify(r));}}
 // ajustes, especialista, nível 10, sem traje, sequela
 await digita('nivel',10); await marca('per_atletismo_e'); await digita('defesa_aj',2); await digita('prot_equip',''); await marca('sequela_1'); await digita('vida_aj',-3); await digita('item_1_vol',3); await digita('item_2_vol',6);
 await p.waitForTimeout(800);
 const e2={maestria:'+2',refino:'3',classe_max:'3',protecao:'2',defesa:'16',bloquear:'2d10 + 5',per_atletismo:'+6',vida_max:String((12+2)+(7+2)*9-3),morr_janela:'2 rodadas',pe_max:'40',integ_max:String(20+6*9),carga_usada:'9 / 8  · acima do limite'};
 for(const [k,v] of Object.entries(e2)){const r=await ler(k); if(r===v)ok++; else {falha++; console.log('FALHA2',k,'esperado',v,'veio',JSON.stringify(r));}}
 console.log(pdf,'ok',ok,'falha',falha); if(falha) process.exitCode=1;
 if(process.env.TELA) await p.screenshot({path:'tela-'+pdf.replace('.pdf','')+'.png'});
 await b.close();
})();
