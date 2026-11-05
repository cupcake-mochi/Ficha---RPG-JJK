'use strict';
// Preparação exclusivamente local. Não contém cliente Google nem comando de aplicação.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const raiz = path.resolve(__dirname, '../..');
const ler = p => fs.readFileSync(path.join(raiz, p), 'utf8');
const sha = s => crypto.createHash('sha256').update(s).digest('hex');
const ANTES = '52302778db247518b39eb9ebd741cb6a24fc58063a992a24bda69789dac1c775';
const DEPOIS = '8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0';
const MODULO = '9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc';
const plano = JSON.parse(ler('r53/diagnostico-android/pilha_5156_plano.json'));
function unico(s, a, b) {
  if (s.split(a).length !== 2) throw Error('Âncora ausente ou duplicada');
  return s.replace(a, () => b);
}
function sufixo() {
  return ler('apps-script/CuraRecebida.gs') + '\n' + ler('apps-script/Socorro.gs') +
    '\nfunction r53DescansarComQueda(tipo, queda, jaConvertido) { return r53Modulo_().r53DescansarComQueda(tipo, queda, jaConvertido); }\n' +
    'var R53_PILHA_516_ = ' + JSON.stringify(plano) + ';\n' + ler('r53/diagnostico-android/pilha_5156_molde.gs');
}
function preparar(fonte) {
  if (sha(fonte) !== ANTES) throw Error('Snapshot incompatível: exige Codigo.gs anterior conferido; não reaplicar');
  let novo = unico(fonte, ' R53_MODULO_=(new Function(code))();',
    ler('r53/diagnostico-android/pilha_5156_runtime.gs') + ' R53_MODULO_=(new Function(code))();');
  const a = " if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
  novo = unico(novo, a, ' try { r53AjustarPilha516_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n' + a);
  novo = unico(novo, 'function onOpen(e){', 'function onOpen(e){r53CuraMenu_();');
  novo += '\n' + sufixo();
  if (sha(novo) !== DEPOIS) throw Error('Saída diferente da proposta relida nas duas cópias');
  return novo;
}
// Estas 9 fórmulas não contêm literais de matriz. Recusar matrizes até haver tratamento próprio.
function formulaLocal(s, locale) {
  if (!s || typeof s !== 'string' || !s.startsWith('=')) return s;
  if (!['pt_BR', 'en_US'].includes(locale)) throw Error('Locale não ensaiado');
  if (locale === 'en_US') return s;
  let aspas = false, out = '';
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '"') aspas = !aspas;
    if (!aspas && /[{}]/.test(c)) throw Error('Matriz requer revisão específica');
    out += !aspas && c === ',' ? ';' : !aspas && c === '.' && /\d/.test(s[i-1] || '') && /\d/.test(s[i+1] || '') ? ',' : c;
  }
  if (aspas) throw Error('Fórmula com texto não fechado');
  return out;
}
function coordenadas(d) {
  if (!d.addr) return {r:d.r,c:d.c};
  const m = /^([A-Z]+)([1-9]\d*)$/.exec(d.addr);
  if (!m) throw Error('Endereço inválido');
  return {r:Number(m[2]),c:[...m[1]].reduce((v,c)=>v*26+c.charCodeAt(0)-64,0)};
}
function chave(d) { const p=coordenadas(d); return `${d.aba}!${p.r},${p.c}:${d.addr?'note':'value'}`; }
function entrada(v) {
  if (v === null || v === '') return {};
  if (typeof v === 'string') return v.startsWith('=') ? {formulaValue:v} : {stringValue:v};
  if (typeof v === 'boolean') return {boolValue:v};
  if (typeof v === 'number' && Number.isFinite(v)) return {numberValue:v};
  throw Error('Tipo de célula inesperado');
}
// Snapshot normalizado: {locale, cells:[{aba,r,c OU addr,sheetId,value OU note}]}.
// Produz pedidos e reversão guardada; quem aplicar deve reler os alvos imediatamente antes.
function planejarCelulas(snapshot, reverter=false, entradas=plano) {
  if (!snapshot || !Array.isArray(snapshot.cells)) throw Error('Snapshot de células ausente');
  const ids = new Map(), abasPorId = new Map();
  const requests = entradas.map(d => {
    const encontrados=snapshot.cells.filter(x=>chave(x)===chave(d));
    if (encontrados.length!==1) throw Error('Alvo ausente ou duplicado: '+chave(d));
    const x=encontrados[0], p=coordenadas(d), id=x.sheetId;
    if (!Number.isSafeInteger(id)||id<0) throw Error('sheetId inválido');
    if ((ids.has(d.aba)&&ids.get(d.aba)!==id)||(abasPorId.has(id)&&abasPorId.get(id)!==d.aba)) throw Error('Mapeamento de abas divergente');
    ids.set(d.aba,id);abasPorId.set(id,d.aba);
    const atual=d.addr?x.note:x.value;
    const antes=formulaLocal(reverter?d.depois:d.antes,snapshot.locale);
    const depois=formulaLocal(reverter?d.antes:d.depois,snapshot.locale);
    if ((atual ?? '') !== (antes ?? '')) throw Error('Célula divergente: '+chave(d));
    const fields=d.addr?'note':'userEnteredValue';
    const cell=d.addr?{note:depois ?? ''}:{userEnteredValue:entrada(depois)};
    return {updateCells:{start:{sheetId:id,rowIndex:p.r-1,columnIndex:p.c-1},rows:[{values:[cell]}],fields}};
  });
  return {requests};
}
if(require.main===module) {
  const [codigo,celulas,destino]=process.argv.slice(2);
  if(!codigo||!celulas||!destino)throw Error('Uso: node preparar_pilha_5156.js snapshot-Codigo.gs snapshot-celulas.json pasta-nova');
  if(fs.existsSync(destino))throw Error('A saída deve ser uma pasta nova; preserve entregas anteriores');
  const fonte=fs.readFileSync(codigo,'utf8'),snapshot=JSON.parse(fs.readFileSync(celulas,'utf8'));
  const novo=preparar(fonte),pedidos=planejarCelulas(snapshot);
  const final={...snapshot,cells:snapshot.cells.map(x=>{
    const d=plano.find(d=>chave(d)===chave(x));return d?{...x,[d.addr?'note':'value']:formulaLocal(d.depois,snapshot.locale)}:x;
  })};
  const reversao=planejarCelulas(final,true);
  fs.mkdirSync(destino,{recursive:true});
  for(const [nome,conteudo] of Object.entries({'Codigo-proposto.gs':novo,'Codigo-reversao.gs':fonte,'pedidos.json':JSON.stringify(pedidos,null,2),'reversao.json':JSON.stringify(reversao,null,2),
    'manifesto.json':JSON.stringify({antes:ANTES,depois:DEPOIS,moduloPreservado:MODULO,celulas:11,notas:3,aplicado:false,snapshotCelulas:sha(JSON.stringify(snapshot))},null,2)}))fs.writeFileSync(path.join(destino,nome),conteudo);
}
module.exports={preparar,planejarCelulas,formulaLocal,coordenadas,chave,plano,sha,ANTES,DEPOIS,MODULO};
