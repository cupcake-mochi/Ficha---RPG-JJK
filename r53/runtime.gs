/** Editor do documento atual. Não usa Drive, UrlFetch ou gatilho instalável. */
var R53_REF_CACHE_ = {};
function r53Menu_() {
  if (typeof R53_EDITOR_ === 'undefined') return;
  SpreadsheetApp.getUi().createMenu('Feitiços').addItem('Editar funções e pontos', 'editarFeiticoR53').addToUi();
}
function r53Pos_(a1) {
  var m = /^([A-Z]+)(\d+)$/.exec(a1), c = 0;
  if (!m) throw new Error('Endereço R53 inválido');
  for (var i = 0; i < m[1].length; i++) c = c * 26 + m[1].charCodeAt(i) - 64;
  return [Number(m[2]), c];
}
function r53Atinge_(range, a1) {
  var p = r53Pos_(a1);
  return p[0] >= range.getRow() && p[0] <= range.getLastRow() && p[1] >= range.getColumn() && p[1] <= range.getLastColumn();
}
function r53Contexto_(range) {
  var aba = range.getSheet().getName(), r = range.getRow(), c = range.getColumn();
  return R53_EDITOR_.contextos.filter(function(g) {
    var a = g.area_editor; return g.aba === aba && r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3];
  })[0];
}
function r53Formula_(v, ss) {
  if(!R53_REF_CACHE_.idioma)R53_REF_CACHE_.idioma=ss.getSpreadsheetLocale();
  return typeof v === 'string' && v.charAt(0) === '=' && typeof formulaNoIdioma_ === 'function'
    ? formulaNoIdioma_(v, R53_REF_CACHE_.idioma) : v;
}
function r53Literal_(v) {
  // setValues interpreta '='; campos do jogador são sempre literais.
  return typeof v === 'string' && /^[=']/.test(v) ? "'" + v : v;
}
function r53LeReferencia_(ss, address) {
  var key='v:'+address;
  if (Object.prototype.hasOwnProperty.call(R53_REF_CACHE_,key)) return R53_REF_CACHE_[key];
  var p = address.lastIndexOf('!'), owner = address.slice(0,p).replace(/^'|'$/g,'').replace(/''/g,"'");
  return R53_REF_CACHE_[key]=ss.getSheetByName(owner).getRange(address.slice(p+1)).getValue();
}
function r53Classes_(ss,g) {
  var max = Number(r53LeReferencia_(ss,g.classe_maxima));
  return g.classes.filter(function(c) { return c === null || c === 0 || c <= max; }).map(function(c) { return c === null ? max : c; });
}
function r53Coluna_(ss,g,classe) {
  var allowed = r53Classes_(ss,g);
  if (typeof classe !== 'number' || classe % 1 || allowed.indexOf(classe) < 0) throw new Error('Esta Classe não está disponível neste cartão.');
  return g.classes.indexOf(g.classes[0] === null ? null : classe) + 2;
}
function r53Ativa_(ss,g) {
  if (g.classes[0] === null) return Number(r53LeReferencia_(ss,g.classe_maxima));
  if (g.classes.length === 1) return g.classes[0];
  var v = ss.getSheetByName(g.aba).getRange(g.cel.classe).getValue();
  return v === '' ? r53Classes_(ss,g)[0] : Number(v);
}
function r53LerVersao_(ss,g,classe) {
  return ss.getSheetByName(R53_EDITOR_.storage).getRange(g.editor+2,r53Coluna_(ss,g,classe),R53_EDITOR_.campos.length,1).getValues().map(function(r) { return r[0]; });
}
function r53Vazia_(vals) {
  return R53_EDITOR_.campos.every(function(f,i) { return vals[i] === R53_EDITOR_.defaults[f[0]]; });
}
function r53Inicializar_(ss,g,classe) {
  var vals = r53LerVersao_(ss,g,classe);
  if (!r53Vazia_(vals) || g.classes.length === 1) return vals;
  var storage = ss.getSheetByName(R53_EDITOR_.storage), matrix = storage.getRange(g.editor+2,2,R53_EDITOR_.campos.length,g.classes.length).getValues();
  var prep = R53_EDITOR_.campos.map(function(f) { return f[0]; }).indexOf('preparada'), origem = matrix[prep].indexOf(true);
  if (origem < 0) return vals;
  vals = R53_EDITOR_.campos.map(function(f,i) {
    return /^(preparada|pontos[123]|migracao)$/.test(f[0]) ? R53_EDITOR_.defaults[f[0]] : matrix[i][origem];
  });
  storage.getRange(g.editor+2,r53Coluna_(ss,g,classe),vals.length,1).setValues(vals.map(function(v) { return [r53Literal_(v)]; }));
  return vals;
}
function r53Mostrar_(ss,g,classe,inicializar) {
  var inicio=Date.now();
  var panel = R53_EDITOR_.paineis[g.aba], sh = ss.getSheetByName(g.aba);
  var values = inicializar ? r53Inicializar_(ss,g,classe) : r53LerVersao_(ss,g,classe);
  console.log('R53 painel · versão lida: '+(Date.now()-inicio)+' ms');
  var matrix = panel.template.map(function(row) { return row.map(function(v) { return v === null ? '' : r53Formula_(v,ss); }); });
  function set(a1,v) { var p = r53Pos_(a1); matrix[p[0]-panel.linha][p[1]-panel.coluna] = v; }
  R53_EDITOR_.campos.forEach(function(f,i) { set(panel.campos[f[0]],r53Literal_(values[i])); });
  var nome = sh.getRange(g.cel.nome).getValue();
  set(panel.nome, r53Literal_(nome || 'Dê um nome ao feitiço no cartão.'));set(panel.classe,classe);set(panel.voltar,false);
  // A lista precisa aceitar a nova modalidade ANTES de gravar sua Classe.
  // A lista da montagem anterior pode conter 1–7 e rejeitar a Classe0.
  sh.getRange(panel.classe).setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(r53Classes_(ss,g).map(String),true).setAllowInvalid(false).build());
  ss.getSheetByName(R53_EDITOR_.data).getRange(panel.estado,1,1,3).setValues([[g.aba,g.id,classe]]);
  sh.getRange(panel.linha,panel.coluna,matrix.length,8).setValues(matrix);
  console.log('R53 painel · gravado: '+(Date.now()-inicio)+' ms');
}
function r53Abrir_(ss,g) {
  var classe = r53Ativa_(ss,g);r53Coluna_(ss,g,classe);
  var panel = R53_EDITOR_.paineis[g.aba], sh = ss.getSheetByName(g.aba);
  // A Classe ativa já está no cartão; regravá-la força recálculo desnecessário.
  r53Mostrar_(ss,g,classe,true);
  var grupo = sh.getColumnGroup(panel.coluna,1);
  if (grupo) grupo.expand();else sh.showColumns(panel.coluna,8);
  // A Classe fica na última coluna e no topo: a seleção exibe todo o painel.
  sh.setActiveSelection(panel.classe);
}
function editarFeiticoR53() {
  R53_REF_CACHE_ = {};
  var ss = SpreadsheetApp.getActive(), g = r53Contexto_(ss.getActiveRange());
  if (!g) { ss.toast('Selecione um cartão de feitiço ou habilidade montada.');return; }
  var lock = LockService.getDocumentLock();
  if (!lock.tryLock(1500)) { ss.toast('Há outra edição em andamento. Tente novamente.');return; }
  try { r53Abrir_(ss,g); } catch(err) { ss.toast(err.message);throw err; } finally { lock.releaseLock(); }
}
function r53Validar_(kind,v,ss,panel,key) {
  if (kind === 'bool') return typeof v === 'boolean';
  if (kind === 'inteiro') return typeof v === 'number' && isFinite(v) && v >= 0 && v % 1 === 0;
  if (typeof v !== 'string') return false;
  var menu = panel.menus[key];
  if (!menu || menu.tipo !== 'list' || v === '') return true;
  var f = menu.formula, allowed;
  if (f.charAt(0) === '"') allowed = f.slice(1,-1).split(',');
  else {
    var cut = f.lastIndexOf('!'), owner = f.slice(0,cut).replace(/^'|'$/g,'').replace(/''/g,"'");
    allowed = [].concat.apply([],ss.getSheetByName(owner).getRange(f.slice(cut+1)).getValues());
  }
  return allowed.indexOf(v) >= 0;
}
function r53Editar_(e) {
  R53_REF_CACHE_ = {};
  if (typeof R53_EDITOR_ === 'undefined' || !e || !e.range) return false;
  var range = e.range, sh = range.getSheet(), owner = sh.getName(), panel = R53_EDITOR_.paineis[owner];
  if (!panel) return false;
  var ss = e.source || SpreadsheetApp.getActive();
  var ispanel = range.getLastColumn() >= panel.coluna && range.getColumn() < panel.coluna+8 && range.getLastRow() >= panel.linha && range.getRow() <= panel.fim;
  var gs = R53_EDITOR_.contextos.filter(function(g) { return g.aba === owner; });
  var action = gs.filter(function(g) { return g.abrir_editor && r53Atinge_(range,g.abrir_editor); })[0];
  var repaired = false;
  if (!ispanel && !action) {
    gs.forEach(function(g) {
      Object.keys(g.formulas).forEach(function(a1) {
        if (!r53Atinge_(range,a1)) return;
        sh.getRange(a1).setFormula(r53Formula_(g.formulas[a1],ss));repaired = true;
      });
    });
    if (repaired) { ss.toast('Este resultado é calculado. Use Editar funções e pontos no cartão.');return true; }
    return false;
  }
  var lock = LockService.getDocumentLock();
  if (!lock.tryLock(1500)) { ss.toast('Outra edição está sendo salva. Refaça esta alteração.');return true; }
  var current = null, classe;
  try {
    if (action) {
      var clicked = sh.getRange(action.abrir_editor);var checked = clicked.getValue() === true;clicked.setValue(false);
      if (checked) r53Abrir_(ss,action);return true;
    }
    var state = ss.getSheetByName(R53_EDITOR_.data).getRange(panel.estado,2,1,2).getValues()[0];
    current = gs.filter(function(g) { return g.id === state[0]; })[0];classe = state[1];
    if (!current) throw new Error('Abra um cartão antes de editar este painel.');
    if (r53Atinge_(range,panel.voltar) && sh.getRange(panel.voltar).getValue() === true) {
      sh.getRange(panel.voltar).setValue(false);sh.setActiveSelection(current.cel.nome);
      var grupo = sh.getColumnGroup(panel.coluna,1);if (grupo) grupo.collapse();else sh.hideColumns(panel.coluna,8);
      return true;
    }
    if (r53Atinge_(range,panel.classe)) {
      if (range.getNumRows() > 1 || range.getNumColumns() > 1) throw new Error('Troque a Classe separadamente dos demais campos.');
      var rawClass = sh.getRange(panel.classe).getValue();
      if (rawClass === '') throw new Error('Escolha uma Classe na lista.');
      var next = Number(rawClass);r53Coluna_(ss,current,next);
      if (current.cel.classe && current.classes.length > 1) sh.getRange(current.cel.classe).setValue(next);
      r53Mostrar_(ss,current,next,true);return true;
    }
    if (r53Ativa_(ss,current) !== classe) throw new Error('A Classe mudou no cartão. Abra o cartão novamente antes de editar.');
    var changes = [], values = r53LerVersao_(ss,current,classe);
    R53_EDITOR_.campos.forEach(function(f,i) {
      var a1 = panel.campos[f[0]];if (!r53Atinge_(range,a1)) return;
      var cell = sh.getRange(a1), v = cell.getValue();
      if (cell.getFormula() || !r53Validar_(f[2],v,ss,panel,f[0])) throw new Error('Valor inválido em '+f[1]+'. Use a lista, caixa ou número inteiro.');
      values[i] = v;changes.push(i);
    });
    if (changes.length) {
      ss.getSheetByName(R53_EDITOR_.storage).getRange(current.editor+2,r53Coluna_(ss,current,classe),values.length,1)
        .setValues(values.map(function(v) { return [r53Literal_(v)]; }));
    } else r53Mostrar_(ss,current,classe,false);
    return true;
  } catch(err) {
    if (current && typeof classe === 'number') r53Mostrar_(ss,current,classe,false);
    ss.toast(err.message);console.log('Editor R53: '+err.message);return true;
  } finally { lock.releaseLock(); }
}
