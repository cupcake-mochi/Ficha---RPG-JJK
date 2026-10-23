// Fixture mínima das entradas públicas; não contém catálogos nem dados privados.
var R53_MODULO_;
var R53_NAVEGACAO_={aba:'INVOCAÇÕES',alvos:['I9']};
function r53Modulo_(){
 var code='',hash='';
 if(hash!=='2f153f659f714a7e5d16e483832f0bd4914bb93175f0527d97c7d20a03c2b110')throw Error('Fixture');
 R53_MODULO_=(new Function(r53CorrecaoAbertura_(code)))();
 return R53_MODULO_;
}
function onSelectionChange(e) {
 if(!e || !e.range)return;
 var pending=true;
 try {pending=!!PropertiesService.getDocumentProperties().getProperty('paleta_pendente');}catch(err){}
 var address=e.range.getA1Notation().split(':')[0];
 var opening=R53_NAVEGACAO_.alvos.indexOf(address)>=0 && e.range.getSheet().getName()===R53_NAVEGACAO_.aba;
 if(pending || opening)return r53Modulo_().onSelectionChange(e);
}
function onEdit(e){if(typeof salarioEditar_==="function" && salarioEditar_(e))return;if(typeof r53Editar_==="function" && r53Editar_(e))return;return r53Modulo_().onEdit(e); }
function onOpen(){return r53Modulo_()["onOpen"].apply(this,arguments);}
