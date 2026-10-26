/** Leituras limitadas às entradas e aos metadados usados pelo evento. */
var R53_CAMINHO_PROGRESSAO_;
var R53_CAMINHO_SS_;
/** Planeja leituras antes das gravações; mantém alterações anteriores visíveis
 * às próprias regras sem provocar um recálculo do documento a cada passagem. */
function r53FilaCaminho_(real,seed){
 if(seed)return r53FilaSnapshotCaminho_(real,seed);
 var sheets={},writes=[],values={},notes={},reads={};
 if(seed)Object.keys(seed).forEach(function(n){var s=seed[n];reads[n]=[{r:1,c:1,r2:s.length,c2:s[0].length,v:s}];});
 var table=function(map,name){return map[name]||(map[name]={});};
 function span(a){return limitesA1_(a);}
 function put(sh,p,v,map){var t=table(map,sh.getName());for(var r=p.l1;r<=p.l2;r++)for(var c=p.c1;c<=p.c2;c++)t[r+','+c]=Array.isArray(v)?v[r-p.l1][c-p.c1]:v;}
 function range(sh,native){
  return new Proxy(native,{get:function(target,key){
   if(key==='getSheet')return function(){return sheet(sh);};
   if(['setValue','setValues','setNote','setRichTextValue'].indexOf(key)>=0)return function(v){
    var p={l1:target.getRow(),l2:target.getLastRow(),c1:target.getColumn(),c2:target.getLastColumn()};
    var scalar=key==='setRichTextValue'?(v.getText?v.getText():v.text):v;
    // Valores escalares de uma célula mesclada pertencem somente à âncora.
    if(key!=='setValues'){p.l2=p.l1;p.c2=p.c1;}put(sh,p,scalar,key==='setNote'?notes:values);
    writes.push({sheet:sh.getName(),type:key,p:p,run:function(){target[key](v);}});return this;
   };
   if(key==='getValue'||key==='getValues'||key==='getNotes')return function(){
    var note=key==='getNotes',t=table(note?notes:values,sh.getName()),r=target.getRow(),c=target.getColumn();
    if(key==='getValue'&&Object.prototype.hasOwnProperty.call(t,r+','+c))return t[r+','+c];
    var out;
    if(note)out=Array.from({length:target.getNumRows()},function(){return Array(target.getNumColumns()).fill('\u0000');});
    else {
     var lastRow=key==='getValue'?r:target.getLastRow(),lastCol=key==='getValue'?c:target.getLastColumn(),list=reads[sh.getName()]||(reads[sh.getName()]=[]);
     var found=list.filter(function(p){return r>=p.r&&lastRow<=p.r2&&c>=p.c&&lastCol<=p.c2;})[0];
     if(found)out=found.v.slice(r-found.r,lastRow-found.r+1).map(function(row){return row.slice(c-found.c,lastCol-found.c+1);});
     else {out=key==='getValue'?[[target.getValue()]]:target.getValues();list.push({r:r,c:c,r2:lastRow,c2:lastCol,v:out});}
    }
    return key==='getValue'?out[0][0]:out.map(function(row,y){return row.map(function(v,x){var k=(r+y)+','+(c+x);return Object.prototype.hasOwnProperty.call(t,k)?t[k]:v;});});
   };
   var v=target[key];return typeof v==='function'?v.bind(target):v;
  }});
 }
 function sheet(sh){var name=sh.getName();if(sheets[name])return sheets[name];return sheets[name]=new Proxy(sh,{get:function(target,key){
  if(key==='getRange'||key==='getDataRange')return function(){return range(sh,target[key].apply(target,arguments));};
  if(key==='getRangeList')return function(list){return {setValue:function(v){list.forEach(function(a){put(sh,span(a),v,values);});var w={sheet:name,type:'list',list:list,run:function(){sh.getRangeList(w.list).setValue(v);}};writes.push(w);return this;}};};
  if(key==='setRowHeights')return function(){var args=Array.prototype.slice.call(arguments);writes.push({sheet:name,type:'height',row:args[0],count:args[1],run:function(){target.setRowHeights.apply(target,args);}});return this;};
  var v=target[key];return typeof v==='function'?v.bind(target):v;
 }});}
 return {ss:new Proxy(real,{get:function(target,key){if(key==='getSheetByName')return function(n){var sh=target.getSheetByName(n);return sh?sheet(sh):null;};var v=target[key];return typeof v==='function'?v.bind(target):v;}}),range:function(r){return range(r.getSheet(),r);},grava:function(alvos){return writes.some(function(w){return r53TocaCaminho_(w,alvos);});},descartar:function(alvos){writes=r53SemAlvosCaminho_(writes,alvos);},aplicar:function(){writes.forEach(function(w){if(w.type!=='list'||w.list.length)w.run();});}};
}
/** Com o retrato compacto, as regras trabalham só em memória. Nenhuma busca
 * de aba ou leitura de faixa é refeita antes da gravação final. */
function r53FilaSnapshotCaminho_(real,seed){
 var sheets={},native={},writes=[];
 function letters(c){var s='';for(;c;c=Math.floor((c-1)/26))s=String.fromCharCode(65+(c-1)%26)+s;return s;}
 function sheet(n){if(!seed[n])return null;if(sheets[n])return sheets[n];return sheets[n]={
  getName:function(){return n;},getDataRange:function(){return range(n,{l1:1,c1:1,l2:seed[n].length,c2:seed[n][0].length});},
  getRange:function(a,c,nr,nc){return range(n,typeof a==='string'?limitesA1_(a):{l1:a,c1:c,l2:a+(nr||1)-1,c2:c+(nc||1)-1});},
  getRangeList:function(list){return {setValue:function(v){list.forEach(function(a){var p=limitesA1_(a);for(var r=p.l1;r<=p.l2;r++)for(var c=p.c1;c<=p.c2;c++)seed[n][r-1][c-1]=v;});writes.push({sheet:n,type:'list',list:list,value:v});return this;}};},
  setRowHeights:function(row,count,height){writes.push({sheet:n,type:'height',row:row,count:count,height:height});return this;}
 };}
 function range(n,p){
  var read=function(){var out=[];for(var r=p.l1;r<=p.l2;r++){var row=[];for(var c=p.c1;c<=p.c2;c++)row.push(seed[n][r-1]&&seed[n][r-1][c-1]!==undefined?seed[n][r-1][c-1]:'');out.push(row);}return out;};
  var x={getSheet:function(){return sheet(n);},getRow:function(){return p.l1;},getColumn:function(){return p.c1;},getLastRow:function(){return p.l2;},getLastColumn:function(){return p.c2;},getNumRows:function(){return p.l2-p.l1+1;},getNumColumns:function(){return p.c2-p.c1+1;},getA1Notation:function(){return letters(p.c1)+p.l1+(p.l2!==p.l1||p.c2!==p.c1?':'+letters(p.c2)+p.l2:'');},getCell:function(r,c){return range(n,{l1:p.l1+r-1,c1:p.c1+c-1,l2:p.l1+r-1,c2:p.c1+c-1});},getValues:read,getValue:function(){return read()[0][0];},getNotes:function(){return Array.from({length:p.l2-p.l1+1},function(){return Array(p.c2-p.c1+1).fill('\u0000');});}};
  ['setValue','setValues','setNote','setRichTextValue'].forEach(function(type){x[type]=function(v){var value=type==='setRichTextValue'?(v.getText?v.getText():v.text):v;if(type==='setValue'||type==='setRichTextValue')seed[n][p.l1-1][p.c1-1]=value;else if(type==='setValues')r53PreencherCaminho_(seed[n],v,p.l1,p.c1);writes.push({sheet:n,type:type,p:p,value:v});return x;};});return x;
 }
 return {ss:{getSheetByName:sheet,toast:function(){return real.toast.apply(real,arguments);}},range:function(r){return range(r.getSheet().getName(),{l1:r.getRow(),c1:r.getColumn(),l2:r.getLastRow(),c2:r.getLastColumn()});},grava:function(alvos){return writes.some(function(w){return r53TocaCaminho_(w,alvos);});},descartar:function(alvos){writes=r53SemAlvosCaminho_(writes,alvos);},aplicar:function(){var groups={};writes=writes.filter(function(w){return w.type!=='list'||w.list.length;});writes.forEach(function(w){if(w.type!=='setValue'&&w.type!=='setNote')return;var key=w.sheet+'|'+w.type+'|'+JSON.stringify(w.value);if(!groups[key])groups[key]={sheet:w.sheet,type:w.type,value:w.value,list:[]};groups[key].list.push(letters(w.p.c1)+w.p.l1);});writes.forEach(function(w){if(w.type==='setValue'||w.type==='setNote')return;var sh=native[w.sheet]||(native[w.sheet]=real.getSheetByName(w.sheet));if(w.type==='list')sh.getRangeList(w.list).setValue(w.value);else if(w.type==='height')sh.setRowHeights(w.row,w.count,w.height);else{var p=w.p,r=w.type==='setValues'?sh.getRange(p.l1,p.c1,p.l2-p.l1+1,p.c2-p.c1+1):sh.getRange(p.l1,p.c1);r[w.type](w.value);}});Object.keys(groups).forEach(function(key){var g=groups[key],sh=native[g.sheet]||(native[g.sheet]=real.getSheetByName(g.sheet));sh.getRangeList(g.list)[g.type](g.value);});}};
}
function r53CapturarEvento_(ss){
 var sh=ss.getSheetByName('R53_EVENTOS');if(!sh)return null;
 var rows=sh.getRange(1,1,R53_EVENTOS_.refs.length+1,2).getValues();
 if(rows[0][0]!=='R53_EVENTOS_1'||rows[0][1]!==R53_EVENTOS_.hash)throw Error('Os dados internos da automação estão desatualizados.');
 var out={};Object.keys(R53_EVENTOS_.grades).forEach(function(n){var g=R53_EVENTOS_.grades[n];out[n]=r53MatrizCaminho_(g[0],g[1]);});
 R53_EVENTOS_.refs.forEach(function(p,i){if(rows[i+1][0]!==p[3])throw Error('Endereço interno da automação divergente.');out[p[0]][p[1]-1][p[2]-1]=rows[i+1][1];});return out;
}
function r53MatrizCaminho_(rows,cols){return Array.from({length:rows},function(){return Array(cols).fill('');});}
function r53PreencherCaminho_(target,values,row,col){values.forEach(function(v,y){v.forEach(function(x,z){target[row+y-1][col+z-1]=x;});});return target;}
function r53LerPericias_(ficha){
 return ficha.getDataRange().getValues();
}
function r53GradeCartas_(ficha){
 return ficha.getDataRange();
}
function r53ProgCaminho_(ss){
 if(R53_CAMINHO_PROGRESSAO_)return R53_CAMINHO_PROGRESSAO_;
 var sh=ss.getSheetByName('DADOS_PROGRESSAO');if(!sh)return null;
 var values=sh.getDataRange().getValues();
 return R53_CAMINHO_PROGRESSAO_={getRange:function(a){
  var p=limitesA1_(a),read=function(){var out=[];for(var r=p.l1;r<=p.l2;r++){var row=[];for(var c=p.c1;c<=p.c2;c++)row.push(values[r-1]&&values[r-1][c-1]!==undefined?values[r-1][c-1]:'');out.push(row);}return out;};
  return {getValues:read,getValue:function(){return read()[0][0];},setValues:function(v){r53PreencherCaminho_(values,v,p.l1,p.c1);sh.getRange(a).setValues(v);return this;}};
 }};
}
/** Caminho e Trilha escolhidos em sequência: a execução do Caminho grava uns
 * 10 s depois de ler o retrato, e apagava a Trilha escolhida nesse meio-tempo,
 * com as cartas dela. Só quando vai limpar a Trilha, relê a célula. Se o
 * jogador já trocou, a execução da Trilha recalcula as nove cartas com o
 * Caminho novo, e esta não grava nada que dependa da Trilha. */
function r53TrilhaTrocada_(real,fila,ct,antes){
 var p=limitesA1_(ct),alvos=[{sheet:'FICHA',l1:p.l1,c1:p.c1,l2:p.l1,c2:p.c1}];
 if(!fila.grava(alvos))return false;
 if(String(real.getSheetByName('FICHA').getRange(ct).getValue())===antes)return false;
 var D=cartasDaDadosAm_(R53_CAMINHO_SS_),cartas=D?D.cartas:[];
 cartas.forEach(function(c){[c.nome,c.texto].forEach(function(a1){var q=limitesA1_(a1);alvos.push({sheet:'FICHA',l1:q.l1,c1:q.c1,l2:q.l1,c2:q.c1});});});
 var auto=limitesA1_('CB2:CC10');alvos.push({sheet:'DADOS_PROGRESSAO',l1:auto.l1,c1:auto.c1,l2:auto.l2,c2:auto.c2});
 fila.descartar(alvos);return true;
}
function r53CobreCaminho_(a,sheet,l1,c1,l2,c2){return a.sheet===sheet&&l1<=a.l2&&a.l1<=l2&&c1<=a.c2&&a.c1<=c2;}
/** A gravação cai em algum alvo? Altura de linha vale para a linha inteira. */
function r53TocaCaminho_(w,alvos,a1){
 return alvos.some(function(a){
  if(a1){var q=limitesA1_(a1);return r53CobreCaminho_(a,w.sheet,q.l1,q.c1,q.l2,q.c2);}
  if(w.type==='height')return r53CobreCaminho_(a,w.sheet,w.row,1,w.row+w.count-1,Infinity);
  if(w.type==='list')return w.list.some(function(x){return r53TocaCaminho_(w,[a],x);});
  return r53CobreCaminho_(a,w.sheet,w.p.l1,w.p.c1,w.p.l2,w.p.c2);
 });
}
function r53SemAlvosCaminho_(writes,alvos){
 return writes.filter(function(w){return w.type==='list'||!r53TocaCaminho_(w,alvos);}).map(function(w){
  if(w.type==='list')w.list=w.list.filter(function(x){return !r53TocaCaminho_(w,alvos,x);});return w;
 });
}
function r53DadosNotasCaminho_(ss){
 var data=R53_CAMINHO_DADOS_.map(function(r){return r.slice();}),p=R53_CAMINHO_IO_.notas;
 var text=ss.getSheetByName('DADOS').getRange(p[0],p[1],p[2],1).getValues();
 text.forEach(function(r,i){data[p[0]+i-1][p[1]-1]=r[0];});return data;
}
