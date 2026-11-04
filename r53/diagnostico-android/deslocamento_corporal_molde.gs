/** Delta do molde O67 para carregadores existentes. Não escreve na planilha.
 * Aplicar depois dos demais remendos de r53Modulo_, antes de devolver o módulo.
 * B126 e a célula viva devem ser conferidos separadamente na promoção.
 */
var R53_DESLOCAMENTO_CORPORAL_ = {"antes": "=IF(DADOS_CONFIG!$E$12<>\"\",NA(),IF(DADOS_CONFIG!$C$12=1,(DADOS_CONFIG!$D$12)&\" m\",IF(DADOS_CONFIG!$B$12=0,IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1)))&\" m\",(IF((IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))=\"\",\"\",(IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))+DADOS_CONFIG!$B$12))&\" m\")))", "depois": "=IF(AND('DADOS_CUSTOM'!$B$126,OR('FICHA'!$D$52=\"Corpo Debilitado\",'FICHA'!$D$52=\"Corpo Quebradiço\")),\"0 m\",IF(AND('DADOS_CUSTOM'!$B$126,'FICHA'!$D$52=\"Corpo Exaurido\"),IF(N('FICHA'!$D$26)<=INT(N('FICHA'!$J$26)/2),\"0 m\",MIN(4.5,VALUE(SUBSTITUTE((IF(DADOS_CONFIG!$E$12<>\"\",NA(),IF(DADOS_CONFIG!$C$12=1,(DADOS_CONFIG!$D$12)&\" m\",IF(DADOS_CONFIG!$B$12=0,IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1)))&\" m\",(IF((IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))=\"\",\"\",(IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))+DADOS_CONFIG!$B$12))&\" m\")))),\" m\",\"\")))&\" m\"),IF(DADOS_CONFIG!$E$12<>\"\",NA(),IF(DADOS_CONFIG!$C$12=1,(DADOS_CONFIG!$D$12)&\" m\",IF(DADOS_CONFIG!$B$12=0,IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1)))&\" m\",(IF((IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))=\"\",\"\",(IF(DADOS!$CZ$46=1,0,MIN(IF(N($O$48)>=2,4.5,9999),(DADOS_CONFIG!$S$9+IFERROR(VALUE($W$67&\"\"),0))/IF(DADOS!$CZ$45=1,2,1))))+DADOS_CONFIG!$B$12))&\" m\")))))"};
function r53AjustarDeslocamentoCorporal_(abas) {
 var fichas=abas.filter(function(a){return a.nome==='FICHA';});
 if(fichas.length!==1)throw Error('Deslocamento: aba FICHA ausente ou duplicada');
 var vals=fichas[0].vals.filter(function(v){return v[0]===67&&v[1]===15;});
 if(vals.length!==1)throw Error('Deslocamento: molde O67 ausente ou duplicado');
 var v=vals[0],p=R53_DESLOCAMENTO_CORPORAL_;
 if(v[2]===p.depois)return false;
 if(v[2]!==p.antes)throw Error('Deslocamento: fórmula anterior divergente em O67');
 v[2]=p.depois;return true;
}
