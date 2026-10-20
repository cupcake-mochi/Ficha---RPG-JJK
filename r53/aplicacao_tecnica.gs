/** Atualização retomável das tabelas técnicas da cópia autorizada. */
function atualizarTabelasR53() {
 var ss=SpreadsheetApp.getActive();
 if(ss.getId()!=='1SHJ4Ms6f8ZmiLzBsvEFfq6iQrcp1zHKXq5sunZfbqJo')throw new Error('Este aplicador só atende à cópia de validação autorizada.');
 var lock=LockService.getDocumentLock();if(!lock.tryLock(1500))throw new Error('Outra atualização está em andamento.');
 var locale=ss.getSpreadsheetLocale();
 try {
  var state=r53Modulo_().__estado(),props=PropertiesService.getDocumentProperties(),key='R53_TABELAS_FASE';
  var signature=props.getProperty('R53_TABELAS_GERACAO');
  if(signature && signature!==state.geracao)throw new Error('O plano foi iniciado com outra geração. Conferir antes de retomar.');
  var names=['MONTAGENS','DADOS_R53_CATALOGO','DADOS','DADOS_AM','DADOS_INVOC','DADOS_CUSTOM','DADOS_MELHORIAS','DADOS_RESTRICOES','DADOS_FORMAS','DADOS_APTIDOES','DADOS_TALENTOS','ANALISE','DADOS_R53'];
  var specs={};state.abas.forEach(function(s){specs[s.nome]=s;});
  // As referências só são escritas depois de todas as grades terem tamanho suficiente.
  names.forEach(function(name){var spec=specs[name],sh=ss.getSheetByName(name);if(!sh)sh=ss.insertSheet(name);if(sh.getMaxRows()<spec.rows)sh.insertRowsAfter(sh.getMaxRows(),spec.rows-sh.getMaxRows());if(sh.getMaxColumns()<spec.cols)sh.insertColumnsAfter(sh.getMaxColumns(),spec.cols-sh.getMaxColumns());sh.hideSheet();});
  props.setProperty('R53_TABELAS_GERACAO',state.geracao);
  var phase=Number(props.getProperty(key)||0),done=[],started=Date.now();
  ss.setSpreadsheetLocale('en_US');
  while(phase<names.length && Date.now()-started<140000){
   var name=names[phase],spec=specs[name],sh=ss.getSheetByName(name),matrix=Array.from({length:spec.rows},function(){return Array(spec.cols).fill('');});
   spec.vals.forEach(function(t){matrix[t[0]-1][t[1]-1]=t[2];});
   if(name==='MONTAGENS')r53MigrarArmazenamento_(ss,sh,matrix,state.editor,props);
   // Somente tabelas técnicas: dados do personagem continuam nas abas visíveis.
   sh.getRange(1,1,sh.getMaxRows(),sh.getMaxColumns()).clearDataValidations();
   sh.getDataRange().breakApart();sh.getDataRange().clearContent();
   // Um bloco por vez mantém as chamadas e o tamanho da transmissão previsíveis.
   var step=name==='MONTAGENS'?1500:name==='ANALISE'?2500:spec.rows;
   for(var row=0;row<spec.rows;row+=step){var rows=matrix.slice(row,row+step);sh.getRange(row+1,1,rows.length,spec.cols).setValues(rows);}
   (spec.abaixo||[]).forEach(function(b){sh.getRange(b[0],b[1],1,b[3]-b[1]+1).copyTo(sh.getRange(b[0]+1,b[1],b[2]-b[0],b[3]-b[1]+1),SpreadsheetApp.CopyPasteType.PASTE_FORMULA,false);});
   SpreadsheetApp.flush();phase++;props.setProperty(key,String(phase));done.push(name);console.log('R53 · tabela concluída: '+name);
  }
  console.log(JSON.stringify({geracao:state.geracao,concluidas:done,fase:phase,total:names.length,completo:phase===names.length,proxima:names[phase]||''}));
 } finally {ss.setSpreadsheetLocale(locale);lock.releaseLock();}
}
function r53MigrarArmazenamento_(ss,sh,matrix,cfg,props){
 var old=sh.getDataRange().getValues(),legacy=ss.getSheetByName('R53_LEGADO');
 if(!props.getProperty('R53_LEGADO_SALVO')){
  if(legacy)throw new Error('Já existe um arquivo de recuperação sem recibo; conferir antes de continuar.');
  legacy=ss.insertSheet('R53_LEGADO');if(legacy.getMaxRows()<old.length+1)legacy.insertRowsAfter(legacy.getMaxRows(),old.length+1-legacy.getMaxRows());
  legacy.getRange(1,1,1,2).setValues([['Linha anterior de MONTAGENS','Valores anteriores em JSON']]);
  for(var r=0;r<old.length;r+=1500){var data=old.slice(r,r+1500).map(function(row,i){return[r+i+1,JSON.stringify(row)];});legacy.getRange(r+2,1,data.length,2).setValues(data);}
  legacy.hideSheet();props.setProperty('R53_LEGADO_SALVO','1');
 }
 var byid={};cfg.contextos.forEach(function(g){byid[g.id]=g;});var sections=[];
 old.forEach(function(row,i){if(typeof row[0]!=='string')return;var m=/^([a-z0-9.]+) ·/.exec(row[0]);if(m&&byid[m[1]])sections.push({id:m[1],row:i});});
 var fields=cfg.campos.map(function(f){return f[0];}),label={};cfg.campos.forEach(function(f){label[f[1]]=f[0];});var kept=0;
 sections.forEach(function(section,index){
  var g=byid[section.id],end=index+1<sections.length?sections[index+1].row:old.length,header=old[section.row+1]||[];
  for(var c=1;c<header.length;c++){
   var cl=g.classes[0]===null?null:header[c],j=g.classes.indexOf(cl);if(j<0)continue;
   var vals={},flags={},points={};
   for(var r=section.row+2;r<end;r++){
    var row=old[r],name=row[0],v=row[c];if(name in label)vals[label[name]]=v;
    if(name==='Dano')flags.Dano=v;if(name==='Cura direta')flags.Cura=v;if(name==='Vida temporária')flags['PV temporários']=v;
    if(name==='Pontos de dano')points.Dano=v;if(name==='Pontos de cura')points.Cura=v;if(name==='Pontos de vida temporária')points['PV temporários']=v;
   }
   if(!('funcao1' in vals)){
    var n=0;['Dano','Cura','PV temporários'].forEach(function(k){if(flags[k]===true || Number(points[k])>0){n++;vals['funcao'+n]=flags[k]===true?k:'';vals['pontos'+n]=points[k]||0;if(flags[k]!==true)vals.migracao='Revisão necessária';}if(k in flags && typeof flags[k]!=='boolean')vals.migracao='Revisão necessária';});
    if(vals.preparada===true && vals.res_dano==='TR' && !vals.tr_dano)vals.migracao='Revisão necessária';
   }
   var meaningful=fields.some(function(k){return k in vals && vals[k]!==cfg.defaults[k];});
   if(!meaningful)continue;
   fields.forEach(function(k,i){if(k in vals){var v=vals[k];if(typeof v==='string'&&/^[=']/.test(v))v="'"+v;matrix[g.editor+1+i][j+1]=v;}});kept++;
  }
 });
 console.log('R53 · versões preservadas do armazenamento: '+kept);
}
