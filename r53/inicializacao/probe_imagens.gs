/** @OnlyCurrentDoc */
/** Sonda manual, apenas em uma planilha técnica vazia e descartável.
 * Substituir o ID localmente. Não instalar no modelo, no pacote ou no bot.
 * Sem Drive, UrlFetch, acionadores ou retorno de URL de conteúdo.
 */
var R53_QA_IMAGENS_ALVO_='DEFINIR_ID_DA_DESCARTAVEL';
function qaImagensAlvo_(){
  var ss=SpreadsheetApp.getActive();
  if(!ss||ss.getId()!==R53_QA_IMAGENS_ALVO_||ss.getName().indexOf('QA Carteira — leitura de imagens — DESCARTÁVEL')!==0)
    throw new Error('Sonda restrita à planilha técnica descartável.');
  var sh=ss.getSheetByName('Sheet1');if(!sh)throw new Error('Aba técnica ausente.');return sh;
}
function qaImagensPreparar(){
  var sh=qaImagensAlvo_();
  sh.getRange('A1').setValue(SpreadsheetApp.newCellImage()
    .setSourceUrl('https://www.gstatic.com/images/branding/productlogos/apps_script/v10/web-64dp/logo_apps_script_color_1x_web_64dp.png')
    .setAltTextTitle('QA IMAGEM FICTÍCIA').setAltTextDescription('Apenas ensaio técnico').build());
  sh.getRange('B1').setFormula('=A1');
  sh.getRange('A3:B3').setValues([['Teste técnico de imagens','Sem dados reais']]);
  PropertiesService.getDocumentProperties().deleteProperty('qa_imagem_hash');SpreadsheetApp.flush();
}
function qaImagensMedir(){
  var sh=qaImagensAlvo_(),inicio=Date.now(),isImage=function(v){return !!v&&v.valueType===SpreadsheetApp.ValueType.IMAGE;};
  var v1=sh.getRange('A1').getValue(),batch=sh.getRange('A1:B1').getValues()[0],v2=sh.getRange('A1').getValue();
  var out={individualImagem:isImage(v1),loteImagem:isImage(batch[0]),espelhoImagem:isImage(batch[1]),urlLegivel:false,igualNaExecucao:false,temMedicaoAnterior:false,igualEntreExecucoes:false};
  try{
    var u1=v1.getContentUrl(),u2=v2.getContentUrl(),u3=sh.getRange('A1').getValue().getContentUrl();
    out.urlLegivel=typeof u1==='string'&&u1.indexOf('https://')===0;
    out.igualNaExecucao=out.urlLegivel&&u1===u2&&u2===u3;
    var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,u1,Utilities.Charset.UTF_8)
      .map(function(b){return ('0'+((b+256)%256).toString(16)).slice(-2);}).join('');
    var p=PropertiesService.getDocumentProperties(),anterior=p.getProperty('qa_imagem_hash');
    out.temMedicaoAnterior=anterior!==null;out.igualEntreExecucoes=anterior===hash;p.setProperty('qa_imagem_hash',hash);
  }catch(e){out.erro='identificacao_indisponivel';}
  out.duracaoMs=Date.now()-inicio;
  var linhas=Object.keys(out).map(function(k){return [k,out[k]];});sh.getRange(4,1,linhas.length,2).setValues(linhas);
  console.log(JSON.stringify(out));return out;
}
function qaImagensLimpar(){
  var sh=qaImagensAlvo_();sh.getRange('A1').setValue('FOTO');SpreadsheetApp.flush();
  var vs=sh.getRange('A1:B1').getValues()[0],out={fotoVirouTexto:vs[0]==='FOTO',formulaEspelhoPreservada:sh.getRange('B1').getFormula()==='=A1',espelhoVirouTexto:vs[1]==='FOTO'};
  sh.getRange('D4:E6').setValues(Object.keys(out).map(function(k){return [k,out[k]];}));console.log(JSON.stringify(out));return out;
}
