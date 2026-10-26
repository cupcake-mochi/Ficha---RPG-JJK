/** Edição direta R53. Apenas a planilha atual; sem navegação ou painel. */
var R53_REF_CACHE_ = {};
function r53Menu_() {}
function r53Pos_(a1) {var m=/^([A-Z]+)(\d+)$/.exec(a1),c=0;for(var i=0;i<m[1].length;i++)c=c*26+m[1].charCodeAt(i)-64;return [+m[2],c];}
function r53Atinge_(range,a1) {var p=r53Pos_(a1);return p[0]>=range.getRow()&&p[0]<=range.getLastRow()&&p[1]>=range.getColumn()&&p[1]<=range.getLastColumn();}
function r53Literal_(v) {return typeof v==='string'&&/^[=']/.test(v)?"'"+v:v;}
function r53Formula_(v,ss) {
  // All generated functions use English names; only the argument separator changes.
  if(typeof v!=='string'||v.charAt(0)!=='=')return v;
  var locale=R53_REF_CACHE_.locale||(R53_REF_CACHE_.locale=ss.getSpreadsheetLocale());
  if(!/^(pt|fr|de|es|it|ru|nl|pl)/.test(locale))return v;
  var quoted=false,out='';for(var i=0;i<v.length;i++){var c=v[i];if(c==='"'){if(quoted&&v[i+1]==='"'){out+='""';i++;continue;}quoted=!quoted;}out+=c===','&&!quoted?';':c;}return out;
}
function r53LeReferencia_(ss,address) {
 var key='r:'+address;if(Object.prototype.hasOwnProperty.call(R53_REF_CACHE_,key))return R53_REF_CACHE_[key];
 var p=address.lastIndexOf('!');return R53_REF_CACHE_[key]=ss.getSheetByName(address.slice(0,p).replace(/^'|'$/g,'').replace(/''/g,"'")).getRange(address.slice(p+1)).getValue();
}
function r53Classes_(ss,g) {var max=Number(r53LeReferencia_(ss,g.classe_maxima));return g.classes.filter(function(c){return c===null||c===0||c<=max;}).map(function(c){return c===null?max:c;});}
function r53Coluna_(ss,g,cl) {if(typeof cl!=='number'||cl%1||r53Classes_(ss,g).indexOf(cl)<0)throw Error('Escolha uma Classe disponível neste cartão.');return g.classes.indexOf(g.classes[0]===null?null:cl)+2;}
function r53Ativa_(ss,g) {if(g.classes[0]===null)return Number(r53LeReferencia_(ss,g.classe_maxima));if(g.classes.length===1)return g.classes[0];return Number(ss.getSheetByName(g.aba).getRange(g.cel.classe).getValue());}
function r53Indice_(g,cl) {var i=g.classes[0]===null?0:g.classes.indexOf(cl);if(i<0)throw Error('Versão de Classe inválida.');return i+2;}
function r53LerVersao_(ss,g,cl) {return ss.getSheetByName(R53_EDITOR_.storage).getRange(g.editor+2,r53Indice_(g,cl),R53_EDITOR_.campos.length,1).getValues().map(function(r){return r[0];});}
function r53Campo_(key) {return R53_EDITOR_.campos.map(function(f){return f[0];}).indexOf(key);}
function r53Amparo_(ss) {
 if(R53_REF_CACHE_.amparo)return R53_REF_CACHE_.amparo;
 var p=R53_EDITOR_.amparo;return R53_REF_CACHE_.amparo=ss.getSheetByName(p.aba).getRange(p.faixa).getValues()[0];
}
function r53Porta_(ss,g,key,cl) {if(key!=='dano'&&g.classes.length>1&&g.classes[0]===0&&(cl===undefined?r53Ativa_(ss,g):cl)===0)return false;var f=g.portas[key]||'FALSE';if(f==='TRUE')return true;if(f==='FALSE')return false;return r53Amparo_(ss)[g.entidade===null||typeof g.entidade==='undefined'?0:g.entidade+1]!=='Fechada';}
function r53Gravar_(ss,g,cl,values) {ss.getSheetByName(R53_EDITOR_.storage).getRange(g.editor+2,r53Indice_(g,cl),values.length,1).setValues(values.map(function(v){return [r53Literal_(v)];}));}
function r53ValoresCartao_(ss,g) {
 var sh=ss.getSheetByName(g.aba),a=g.area_editor,m=sh.getRange(a[0],a[1],a[2]-a[0]+1,a[3]-a[1]+1).getValues();
 return function(pos,col){var p=col===undefined?r53Pos_(pos):[pos,col];return m[p[0]-a[0]][p[1]-a[1]];};
}
/** Verdadeiro quando gravar a caixa da função não mudaria nada: o mesmo valor salvo, num formato que a porta aberta aceita. */
function r53FuncaoComoSalva_(g,v,initial,values,i,cl) {
 var f=r53Campo_('funcao'+(i+1)),p=r53Campo_('pontos'+(i+1)),nome=['Dano','Cura','PV temporários'][i];
 if(values[f]!==initial[f]||values[p]!==initial[p])return false;
 if(g.fixa)return typeof v==='boolean'&&(v?nome:'')===initial[f]&&initial[p]===0;
 if(typeof v!=='number'||!isFinite(v)||v<0||v%1||(g.classes.length>1&&g.classes[0]===0&&cl===0&&v>1))return false;
 return v===initial[p];
}
function r53SalvarCartao_(ss,g,cl,edited,snapshot,stored) {
 var get=snapshot||r53ValoresCartao_(ss,g),values=stored?stored.slice():r53LerVersao_(ss,g,cl),initial=values.slice();
 Object.keys(g.entradas_diretas).forEach(function(k){
   if(/^usar_/.test(k)||/^pontos[123]$/.test(k))return;
   var v=get(g.entradas_diretas[k]),idx=r53Campo_(k);if(idx<0)return;
   if(typeof v==='string'&&v.charAt(0)==='=')throw Error('Use a lista ou um valor neste campo.');
   if(k==='fragil_pago'&&(typeof v!=='number'||v<0||v%1))throw Error('Frágil precisa de um número inteiro não negativo.');values[idx]=v;
 });
 ['dano','cura','vt'].forEach(function(key,i){
   var pos=g.funcoes_diretas[key];if(!pos)return;
   // 26/10/2026: a porta lê o Amparo em outra aba (~3 s). Com a caixa igual à versão salva e fora da edição,
   // aberta ou fechada dá o mesmo resultado; só uma caixa diferente precisa da porta.
   if(!(edited&&r53Atinge_(edited,pos))&&r53FuncaoComoSalva_(g,get(pos),initial,values,i,cl))return;
   if(!r53Porta_(ss,g,key,cl))return;
   var v=get(pos);
   if(g.fixa){if(typeof v!=='boolean')throw Error('Use a caixa de seleção da função.');values[r53Campo_('funcao'+(i+1))]=v?['Dano','Cura','PV temporários'][i]:'';values[r53Campo_('pontos'+(i+1))]=0;}
   else {if(typeof v!=='number'||!isFinite(v)||v<0||v%1||(g.classes.length>1&&g.classes[0]===0&&cl===0&&v>1))throw Error('Distribua pontos inteiros; na Classe 0 use 0 ou 1 para escolher dano.');if(v!==initial[r53Campo_('pontos'+(i+1))]||(edited&&r53Atinge_(edited,pos)))values[r53Campo_('funcao'+(i+1))]=v>0?['Dano','Cura','PV temporários'][i]:'';values[r53Campo_('pontos'+(i+1))]=v;}
 });
 var explicit=edited&&(r53Atinge_(edited,g.cel.nome)||Object.keys(g.entradas_diretas).some(function(k){return r53Atinge_(edited,g.entradas_diretas[k]);}));
 var changed=values.some(function(v,i){return v!==initial[i]&&['preparada','r1_valida','r2_valida'].indexOf(R53_EDITOR_.campos[i][0])<0;});
 values[r53Campo_('preparada')]=!!get(g.cel.nome)&&(initial[r53Campo_('preparada')]||explicit||changed);
 values[r53Campo_('r1_valida')]=true;values[r53Campo_('r2_valida')]=true;
 r53Gravar_(ss,g,cl,values);return values;
}
function r53Herdar_(ss,g,cl,from,defer,known) {
 var vals=known||r53LerVersao_(ss,g,cl);
 var empty=R53_EDITOR_.campos.every(function(f,i){return vals[i]===R53_EDITOR_.defaults[f[0]];});
 if(!empty||!from)return defer?{values:vals,herdar:false}:undefined;
 vals=R53_EDITOR_.campos.map(function(f,i){return /^(preparada|pontos[123]|migracao)$/.test(f[0])?R53_EDITOR_.defaults[f[0]]:from[i];});
 if(defer)return {values:vals,herdar:true};
 r53Gravar_(ss,g,cl,vals);
}
function r53Mostrar_(ss,g,cl,state) {
 var vals=state?state.values:r53LerVersao_(ss,g,cl),sh=ss.getSheetByName(g.aba),a=g.area_escrita,grid=null;
 if(a){var range=sh.getRange(a[0],a[1],a[2]-a[0]+1,a[3]-a[1]+1),v=state&&state.card?Array.from({length:a[2]-a[0]+1},function(_,i){return Array.from({length:a[3]-a[1]+1},function(_,j){return state.card(a[0]+i,a[1]+j);});}):range.getValues(),f=range.getFormulas();grid=v.map(function(row,y){return row.map(function(x,z){return f[y][z]||r53Literal_(x);});});}
 // Read gates and prepare validations before writing either storage or UI.
 // A read after setValues waits for the entire workbook to recalculate.
 var rules=r53RegrasCartao_(ss,g);
 Object.keys(g.entradas_diretas).forEach(function(k){
   var pos=g.entradas_diretas[k],i=r53Campo_(k),v=i<0?false:vals[i];
   if(/^usar_/.test(k)){var key=k.slice(5),n=['dano','cura','vt'].indexOf(key)+1;v=vals[r53Campo_('funcao'+n)]===['Dano','Cura','PV temporários'][n-1];}
   if(/^pontos[123]$/.test(k)){var key=['dano','cura','vt'][Number(k.slice(-1))-1];if(!r53Porta_(ss,g,key))v='—';}
   if(/^usar_/.test(k)&&!r53Porta_(ss,g,k.slice(5)))v='—';
   if(grid){var p=r53Pos_(pos);grid[p[0]-a[0]][p[1]-a[1]]=r53Literal_(v);}else sh.getRange(pos).setValue(r53Literal_(v));
 });
 // Fixed cards can switch between checkbox and blocked dash. Install the
 // destination rule before writing, otherwise Sheets rejects the dash.
 if(g.fixa)rules.forEach(function(item){if(item)sh.getRange(item.pos).setDataValidation(item.rule);});
 if(state&&state.herdar)r53Gravar_(ss,g,cl,vals);
 if(grid)g.gravacoes_diretas.forEach(function(b){sh.getRange(b[0],b[1],b[2]-b[0]+1,b[3]-b[1]+1).setValues(grid.slice(b[0]-a[0],b[2]-a[0]+1).map(function(row){return row.slice(b[1]-a[1],b[3]-a[1]+1);}));});
 r53BloqueiosCartao_(ss,g,rules,!!g.fixa);
 PropertiesService.getDocumentProperties().setProperty('r53_classe_visivel_'+g.id,String(cl));
}
function r53RegrasCartao_(ss,g) {
 return ['dano','cura','vt'].map(function(key,i){var pos=g.funcoes_diretas[key];if(!pos)return null;
   var open=r53Porta_(ss,g,key),rule;
   if(g.fixa)rule=open?SpreadsheetApp.newDataValidation().requireCheckbox().setAllowInvalid(false).build():SpreadsheetApp.newDataValidation().requireValueInList(['—'],false).setAllowInvalid(false).build();
   else {var k='pontos'+(i+1),formula='='+g.menus_diretos[k].formula;rule=SpreadsheetApp.newDataValidation().requireFormulaSatisfied(r53Formula_(formula,ss)).setAllowInvalid(false).build();}
   return {pos:pos,open:open,rule:rule};
 });
}
function r53BloqueiosCartao_(ss,g,rules,validationsReady) {
 var sh=ss.getSheetByName(g.aba);(rules||r53RegrasCartao_(ss,g)).forEach(function(item){if(!item)return;var cell=sh.getRange(item.pos);if(!validationsReady)cell.setDataValidation(item.rule);if(!item.open)cell.setValue('—');});
}
function r53SincronizarFamilias_(ss) {
 var current=r53Amparo_(ss),props=PropertiesService.getDocumentProperties(),raw=props.getProperty('r53_amparo_direto');
 // As propriedades do documento não vão na cópia da planilha. Sem estado, a
 // cópia herda os cartões já acertados: guardar o atual em vez de varrer 249.
 if(!raw){props.setProperty('r53_amparo_direto',JSON.stringify(current));return false;}
 var prev=JSON.parse(raw);
 if(JSON.stringify(prev)===JSON.stringify(current))return false;
 var snapshots={},stored=null,groups={};
 R53_EDITOR_.contextos.forEach(function(g){
   var i=g.entidade===null||typeof g.entidade==='undefined'?0:g.entidade+1;if(current[i]===prev[i])return;
   var sh=ss.getSheetByName(g.aba),matrix=snapshots[g.aba]||(snapshots[g.aba]=sh.getDataRange().getValues());
   ['cura','vt'].forEach(function(key,n){
     var pos=g.funcoes_diretas[key];if(!pos||g.portas[key]==='FALSE')return;
     var p=r53Pos_(pos),value=matrix[p[0]-1][p[1]-1],open=r53Porta_(ss,g,key),next=value;
     if(!open)next='—';
     else if(value==='—'){
       stored=stored||ss.getSheetByName(R53_EDITOR_.storage).getDataRange().getValues();
       var col=r53Indice_(g,r53Ativa_(ss,g))-1;
       next=g.fixa?stored[g.editor+1+r53Campo_('funcao'+(n+2))][col]===['Cura','PV temporários'][n]:stored[g.editor+1+r53Campo_('pontos'+(n+2))][col];
     }
     if(next===value)return;
     var id=g.aba+'|'+JSON.stringify(next);if(!groups[id])groups[id]={sh:sh,value:next,places:[]};groups[id].places.push(pos);
     if(g.fixa){var cell=sh.getRange(pos),dv=SpreadsheetApp.newDataValidation();cell.clearDataValidations();cell.setDataValidation(open?dv.requireCheckbox().setAllowInvalid(false).build():dv.requireValueInList(['—'],false).setAllowInvalid(false).build());}
   });
 });
 Object.keys(groups).forEach(function(k){var v=groups[k];v.sh.getRangeList(v.places).setValue(v.value);});
 props.setProperty('r53_amparo_direto',JSON.stringify(current));return true;
}
function r53Editar_(e) {
 R53_REF_CACHE_={};if(typeof R53_EDITOR_==='undefined'||R53_EDITOR_.esquema!==3||!e||!e.range)return false;
 var range=e.range,owner=range.getSheet().getName(),ss=e.source||SpreadsheetApp.getActive();
 // FICHA não contém cartões nem escolhas de Família. Em cópias novas, a
 // sincronização inicial de 249 cartões esgotava o evento antes do Caminho.
 if(!/^(FICHA AMALDIÇOADA|INVOCAÇÕES|CONFIGURAÇÃO|CARTEIRA)$/.test(owner))return false;
 var gs=R53_EDITOR_.contextos.filter(function(g){var a=g.area_editor;return g.aba===owner&&range.getLastRow()>=a[0]&&range.getRow()<=a[2]&&range.getLastColumn()>=a[1]&&range.getColumn()<=a[3];});
 if(!gs.length){r53SincronizarFamilias_(ss);return false;}
 // Capture before waiting: an older Class callback may overwrite the visible
 // cell while this newer input event is queued. Scalar events retain e.value.
 // 26/10/2026: numa célula só, o e.value já é o valor; reler a célula custava uma ida ao servidor.
 var replay=gs.map(function(g){var v={};Object.keys(g.entradas_diretas).forEach(function(k){var p=g.entradas_diretas[k];if(!r53Atinge_(range,p))return;var unica=e.value!==undefined&&range.getRow()===r53Pos_(p)[0]&&range.getColumn()===r53Pos_(p)[1],x=unica?e.value:range.getSheet().getRange(p).getValue();if(unica){var t=g.menus_diretos[k].tipo;if(t==='bool')x=String(x).toUpperCase()==='TRUE'?true:String(x).toUpperCase()==='FALSE'?false:x;else if(t==='custom'&&/^-?\d+(?:[.,]\d+)?$/.test(String(x)))x=Number(String(x).replace(',','.'));}v[k]=x;});return v;});
 var lock=LockService.getDocumentLock();if(!lock.tryLock(20000)){PropertiesService.getDocumentProperties().setProperty('r53_recuperacao_'+Date.now(),JSON.stringify({aba:owner,contextos:gs.map(function(g){return g.id;}),valores:replay}));ss.toast('O salvamento demorou. Sua alteração foi guardada para recuperação; aguarde antes de continuar.');return true;}
 try {
  gs.forEach(function(g,gi){
   var sh=range.getSheet(),classEdit=g.classes.length>1&&g.cel.classe&&r53Atinge_(range,g.cel.classe);
   if(classEdit){
     if(range.getNumRows()!==1||range.getNumColumns()!==1)throw Error('Troque a Classe separadamente dos outros campos.');
     var props=PropertiesService.getDocumentProperties(),key='r53_classe_visivel_'+g.id,marker=props.getProperty(key),old=marker===null?Number(e.oldValue):Number(marker),next=e.value===undefined?r53Ativa_(ss,g):Number(e.value);
     if(marker===null&&isFinite(old)&&g.classes.indexOf(old)>=0)props.setProperty(key,String(old));
     if(next!==r53Ativa_(ss,g))return; // A later Class selection is already visible.
     r53Coluna_(ss,g,next);
     // Read all seven small versions together, before any inherited state is written.
     var matrix=ss.getSheetByName(R53_EDITOR_.storage).getRange(g.editor+2,2,R53_EDITOR_.campos.length,g.classes.length).getValues();
     var version=function(cl){var col=r53Indice_(g,cl)-2;return matrix.map(function(row){return row[col];});};
     var previous=null,get=r53ValoresCartao_(ss,g);
     if(isFinite(old)&&old!==next&&g.classes.indexOf(old)>=0){
       previous=version(old);var dirty=Object.keys(g.entradas_diretas).some(function(k){var x=get(g.entradas_diretas[k]);if(x==='—')return false;var i=r53Campo_(k);if(/^usar_/.test(k)){var n=['dano','cura','vt'].indexOf(k.slice(5))+1;return x!==(previous[r53Campo_('funcao'+n)]===['Dano','Cura','PV temporários'][n-1]);}return i>=0&&x!==previous[i];});
       if(dirty){r53Amparo_(ss);sh.getRange(g.cel.classe).setValue(old);r53SalvarCartao_(ss,g,old,range,get,previous);ss.toast('Uma edição ainda estava sendo salva. Ela foi preservada na Classe '+old+'. Escolha novamente a outra Classe.');return;}
     }
     var state=r53Herdar_(ss,g,next,previous,true,version(next));state.card=get;r53Mostrar_(ss,g,next,state);return;
   }
   // Replay queued input in memory; reading after writing each UI cell forced
   // several workbook recalculations before its storage could be saved.
   var snapshot=r53ValoresCartao_(ss,g),updates={},cl=r53Ativa_(ss,g),classRollback=false;
   var get=function(pos,col){var key=col===undefined?pos:null;return key&&Object.prototype.hasOwnProperty.call(updates,key)?updates[key]:snapshot(pos,col);};
   Object.keys(replay[gi]).forEach(function(k){updates[g.entradas_diretas[k]]=replay[gi][k];});
   if(g.classes.length>1){var props=PropertiesService.getDocumentProperties(),shown=props.getProperty('r53_classe_visivel_'+g.id);if(shown!==null&&Number(shown)!==cl){cl=Number(shown);classRollback=true;}}
   var changed=Object.keys(g.entradas_diretas).filter(function(k){return r53Atinge_(range,g.entradas_diretas[k]);});
   if(g.fixa)changed.filter(function(k){return /^usar_/.test(k)&&get(g.entradas_diretas[k])===true;}).forEach(function(k){
     Object.keys(g.entradas_diretas).filter(function(other){return /^usar_/.test(other)&&other!==k&&r53Porta_(ss,g,other.slice(5),cl);}).forEach(function(other){updates[g.entradas_diretas[other]]=false;});
   });
   var blocked=false,rules=[];
   ['dano','cura','vt'].forEach(function(key){var pos=g.funcoes_diretas[key];if(!pos||!r53Atinge_(range,pos))return;var open=r53Porta_(ss,g,key,cl);if(!open){updates[pos]='—';blocked=true;}if(g.fixa)rules.push({pos:pos,rule:open?SpreadsheetApp.newDataValidation().requireCheckbox().setAllowInvalid(false).build():SpreadsheetApp.newDataValidation().requireValueInList(['—'],false).setAllowInvalid(false).build()});});
   var formulas=Object.keys(g.formulas).filter(function(pos){return r53Atinge_(range,pos);}).map(function(pos){return {pos:pos,formula:r53Formula_(g.formulas[pos],ss)};});
   if(changed.length||r53Atinge_(range,g.cel.nome))r53SalvarCartao_(ss,g,cl,range,get);
   // All reads have finished. Apply only the queued cells, leaving unrelated
   // player input, formulas, notes and validations intact.
   rules.forEach(function(item){sh.getRange(item.pos).setDataValidation(item.rule);});
   Object.keys(updates).forEach(function(pos){sh.getRange(pos).setValue(r53Literal_(updates[pos]));});
   if(classRollback){sh.getRange(g.cel.classe).setValue(cl);ss.toast('A edição foi preservada na Classe '+cl+'. Aguarde o salvamento e selecione a outra Classe novamente.');}
   if(blocked)ss.toast('Função indisponível nesta modalidade ou com Amparo Fechada.');
   formulas.forEach(function(item){sh.getRange(item.pos).setFormula(item.formula);});
  });
  return gs.some(function(g){return r53Atinge_(range,g.cel.nome)||Object.keys(g.entradas_diretas).some(function(k){return r53Atinge_(range,g.entradas_diretas[k]);})||Object.keys(g.formulas).some(function(p){return r53Atinge_(range,p);})||(g.cel.classe&&r53Atinge_(range,g.cel.classe));});
 } catch(err) {
  gs.forEach(function(g){try{if(e.oldValue!==undefined&&range.getNumRows()===1&&range.getNumColumns()===1&&g.cel.classe&&r53Atinge_(range,g.cel.classe))range.setValue(Number(e.oldValue));r53Mostrar_(ss,g,r53Ativa_(ss,g));}catch(ignored){}});
  ss.toast(err.message);console.log('R53 direto: '+err.message);return true;
 } finally {try {SpreadsheetApp.flush();} finally {lock.releaseLock();}}
}
