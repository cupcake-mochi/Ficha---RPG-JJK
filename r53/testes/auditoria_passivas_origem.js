'use strict';
// Diagnóstico reproduzível: exit zero significa leitura concluída, não ficha aprovada.
// Recebe ensaios.json privado (CellData nativo); nunca exige credenciais ou exportação Office.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const book='JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d';
function flat(x){const out={};for(const s of x.sheets)for(const d of s.data||[])for(const [i,r]of (d.rowData||[]).entries())for(const [j,v]of (r.values||[]).entries())out[s.properties.title+':'+((d.startRow||0)+i)+':'+((d.startColumn||0)+j)]=v;return out;}
function diagnosticar(ensaio){
 const dados=new Map(ensaio.casos.map(x=>[x.modelo+':'+x.label,flat(x.planilha)]));
 const val=(modelo,label,k)=>{const c=dados.get(modelo+':'+label)?.[k];assert(c,'Célula ausente '+modelo+'/'+label+'/'+k);const v=c.effectiveValue;assert(!v?.errorValue,'Erro nativo '+k);return v?.numberValue??v?.stringValue??v?.boolValue??c.formattedValue;};
 const r=[],put=(modelo,caso,alvo,esperado,obtido,id)=>r.push({modelo,caso,alvo,esperado,obtido,conforme:esperado===obtido,...id?{achado:id}:{}});
 for(const modelo of ['Era','Ciclo']){
  const basePe=val(modelo,'oaControleReserva','FICHA:29:9');
  for(const label of ['oaReservaPrimeira','oaReservaSegundaEss4','oaReservaEvento']){
   const ess=val(modelo,label,'FICHA:18:35');
   put(modelo,label,'FICHA!J30',basePe+2*ess,val(modelo,label,'FICHA:29:9'),'P01');
   put(modelo,label+' saldo preservado','FICHA!D30',0,val(modelo,label,'FICHA:29:3'));
  }
  put(modelo,'compensação manual da Reserva','FICHA!J30',basePe+8,val(modelo,'oaReservaManual','FICHA:29:9'));
  const limiteBase=val(modelo,'oaControleBolsa','DADOS:40:103');
  for(const label of ['oaBolsaPrimeira','oaBolsaSegunda','oaBolsaCarga83','oaBolsaCarga163']){
   const maestria=val(modelo,label,'DADOS_AM:2:220'),limite=limiteBase+maestria;
   put(modelo,label,'DADOS!CZ41',limite,val(modelo,label,'DADOS:40:103'),'P02');
   if(label.includes('Carga')){
    const carga=val(modelo,label,'DADOS:39:103');
    const movimento=carga>2*limite?'0 m':carga>limite?'4,5 m':'9 m';
    put(modelo,label+' movimento','FICHA!O67',movimento,val(modelo,label,'FICHA:66:14'),'P02');
   }
  }
  for(const [label,mov]of [['oaBolsaManualCarga163','4,5 m'],['oaBolsaManualCarga83','9 m']]){
   put(modelo,label,'DADOS!CZ41',limiteBase+val(modelo,label,'DADOS_AM:2:220'),val(modelo,label,'DADOS:40:103'));
   put(modelo,label+' movimento','FICHA!O67',mov,val(modelo,label,'FICHA:66:14'));
  }
  const normais=val(modelo,'oaControlePratica','DADOS_AM:9:220');
  for(const label of ['oaPraticaPrimeira','oaPraticaSegundoNivelOriginal'])
   put(modelo,label+' mostrador','DADOS_AM!HM10',normais+2,val(modelo,label,'DADOS_AM:9:220'),'P03');
  put(modelo,'Prática no nível 30, mostrador','DADOS_AM!HM10',7,val(modelo,'oaPraticaNivel30','DADOS_AM:9:220'),'P03');
  for(const label of ['oaManifestacao','oaTracoCoexistencia','oaConstrucao'])
   put(modelo,label,'DADOS_AM!HM51',1,val(modelo,label,'DADOS_AM:50:220'));
  put(modelo,'Coexistência, repertório','DADOS_AM!HM53',2,val(modelo,'oaTracoCoexistencia','DADOS_AM:52:220'));
  put(modelo,'Coexistência, total gratuito','DADOS_AM!HM55',2,val(modelo,'oaTracoCoexistencia','DADOS_AM:54:220'));
  put(modelo,'retirada da menor de Talento','DADOS_AM!HM51',0,val(modelo,'oaSemBonusTalento','DADOS_AM:50:220'));
 }
 return {tipo:'diagnóstico de recálculo nativo; controles e repetições incluídos',baseLivro:book,base:ensaio.base,total:r.length,conformes:r.filter(x=>x.conforme).length,divergentes:r.filter(x=>!x.conforme).length,causas:[...new Set(r.filter(x=>!x.conforme).map(x=>x.achado))],resultados:r};
}
function manifesto(){
 const c=vm.createContext({});vm.runInContext(require('../../medidas/carregar-ficha').fontes(),c);
 const am=c.ABAS.find(a=>a.nome==='DADOS_AM');
 const vagas=am.vals.filter(v=>typeof v[2]==='string'&&/^Classe 0 · \d+$/.test(v[2])).length;
 return {baseLivro:book,alvos:['FICHA!J30','DADOS!CZ41','DADOS_AM!HM10','DADOS_AM!HM51','DADOS_AM!HM53','DADOS_AM!HM55'],linhasClasse0NoModelo:vagas,limite:'Inspeção estrutural. Sem CellData privado não reproduz resultados nativos.'};
}
module.exports={flat,diagnosticar,manifesto};
if(require.main===module)console.log(JSON.stringify(process.argv[2]?diagnosticar(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))):manifesto(),null,2));
