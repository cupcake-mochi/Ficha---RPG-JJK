/** Rótulos públicos estáveis; não altera a edição interna da ANALISE. */
var R53_VERSAO_PUBLICA_ = [{"aba":"CARTEIRA","linha":2,"coluna":34,"antes":"=\"Nº M-\"&DADOS!$B$1&\"-\"&IF(FICHA!$AB$2=\"\",\"····\",UPPER(LEFT(FICHA!$AB$2,4)))","depois":"=\"Nº M-\"&\"1.0\"&\"-\"&IF(FICHA!$AB$2=\"\",\"····\",UPPER(LEFT(FICHA!$AB$2,4)))"},{"aba":"FICHA","linha":4,"coluna":8,"antes":"=DADOS!$F$1&\" · \"&IF(DADOS!$B$1=DADOS!$D$1,\"v\"&DADOS!$B$1&\" · em dia\",\"⚠ v\"&DADOS!$B$1&\" · a atual é a v\"&DADOS!$D$1)","depois":"=DADOS!$F$1&\" · v1.0\""}];
function r53AjustarVersaoPublica_(abas) {
 var plano=R53_VERSAO_PUBLICA_.map(function(p){
  var a=abas.filter(function(a){return a.nome===p.aba;})[0];
  var rows=a&&a.vals.filter(function(v){return v[0]===p.linha&&v[1]===p.coluna;});
  if(!rows||rows.length!==1||[p.antes,p.depois].indexOf(rows[0][2])<0)throw Error('Versão pública: molde divergente em '+p.aba);
  return {row:rows[0],novo:p.depois};
 });
 var n=0;plano.forEach(function(p){if(p.row[2]!==p.novo){p.row[2]=p.novo;n++;}});return n;
}

/** Somente os rótulos mesclados; colagens que incluem outros campos seguem o editor original. */
function r53RestaurarVersaoPublica_(e) {
 if(!e||!e.range)return false;
 var r=e.range,n=r.getSheet().getName(),row=r.getRow(),col=r.getColumn(),nr=r.getNumRows(),nc=r.getNumColumns();
 var p=R53_VERSAO_PUBLICA_.filter(function(p){return p.aba===n&&p.linha===row&&p.coluna===col;})[0];
 if(!p||nr!==1||nc>(n==='FICHA'?26:46)-col+1)return false;
 r.getSheet().getRange(row,col).setFormula(r53Formula_(p.depois,e.source||SpreadsheetApp.getActive()));return true;
}
