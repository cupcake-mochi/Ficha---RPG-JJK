// GERADO por r53/descanso_leve.js; funções extraídas de Codigo.gs.
var R53_DESCANSO_LEVE_;
function r53DescansoLeve_(){return R53_DESCANSO_LEVE_||(R53_DESCANSO_LEVE_=(function(){
var SEM_DESCANSO_ = 'Escolha o descanso';
var DESCANSOS_ = {
  'Curto · lugar propício': { longo: false, propicio: true },
  'Curto · fora': { longo: false, propicio: false },
  'Longo · lugar propício': { longo: true, propicio: true },
  'Longo · fora': { longo: true, propicio: false }
};
var PE_DO_DESCANSO_CURTO_ = [25, 15, 5, 0];   // % do PE máximo, pelo degrau de Exaustão, fora de lugar propício

/** Calcula o descanso a partir dos recursos e das capacidades de Origem já selecionadas. */

function indiceEstatico_(){return {"descanso":"D45","último descanso":"O45","vida":"D26","energia":"D30","integridade":"D34","vida_max":"J26","energia_max":"J30","integridade_max":"J34","origem":"X11","marcante":"D52","menor 1":"S52","menor 2":"AG52","classe máxima":"Z73","exaustão":"O48","sequela 1":"F48","sequela 2":"H48","sequela 3":"J48","sequela extras":"J50"};}
function cel_(idx, chave) {
  return idx[chave] ? idx[chave].replace(/\$/g, '') : null;
}
function limitesA1_(a1) {
  var m = /^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/.exec(String(a1 || '').replace(/\$/g, ''));
  if (!m) return null;
  var col = function (t) { var n = 0; for (var i = 0; i < t.length; i++) n = n * 26 + t.charCodeAt(i) - 64; return n; };
  return { l1: Number(m[2]), c1: col(m[1]), l2: Number(m[4] || m[2]), c2: col(m[3] || m[1]) };
}
function lerCelulas_(aba, lista) {
  var f = lista.map(limitesA1_);
  var l1 = Math.min.apply(null, f.map(function (x) { return x.l1; })), c1 = Math.min.apply(null, f.map(function (x) { return x.c1; }));
  var l2 = Math.max.apply(null, f.map(function (x) { return x.l1; })), c2 = Math.max.apply(null, f.map(function (x) { return x.c1; }));
  var v = aba.getRange(l1, c1, l2 - l1 + 1, c2 - c1 + 1).getValues(), out = {};
  lista.forEach(function (a1, i) { out[a1] = v[f[i].l1 - l1][f[i].c1 - c1]; });
  return out;
}
function regraDoDescanso_(tipo, s) {
  var d = DESCANSOS_[tipo];
  return d ? { longo: d.longo, propicio: d.propicio || s.existenciaArtificial === true } : null;
}
function contaDoDescanso_(tipo, s) {
  var d = regraDoDescanso_(tipo, s);
  if (!d) return null;
  var n = function (x) { return Number(x) || 0; };
  var fim = { vida: n(s.vida), pe: n(s.pe), integ: n(s.integ), sequelas: n(s.sequelas),
              exaustao: Math.max(0, Math.min(PE_DO_DESCANSO_CURTO_.length - 1, n(s.exaustao))) };
  var vidaMax = n(s.vidaMax), peMax = n(s.peMax), integMax = n(s.integMax);
  if (!d.longo) {
    var pct = d.propicio && s.recuperacaoAbundante ? 40 : PE_DO_DESCANSO_CURTO_[d.propicio ? 0 : fim.exaustao];
    var ganho = Math.floor(peMax * pct / 100);
    if (ganho < 1 && peMax * pct > 0) ganho = 1;
    // Fôlego só complementa uma recuperação permitida; não vence a proibição do grau 3.
    if (pct > 0 && s.folegoRecuperado) ganho += Math.max(0, Math.floor(n(s.classeDisponivel)));
    if (peMax > 0) fim.pe = Math.max(fim.pe, Math.min(peMax, fim.pe + ganho));
    return fim;
  }
  var metade = function (max) { return Math.max(1, Math.floor(max / 2)); };
  if (vidaMax > 0) {
    if (!s.exaurido) {
      fim.vida = d.propicio ? vidaMax : Math.max(fim.vida, metade(vidaMax));
    } else if (d.propicio) {
      var ganhoVida = Math.max(1, Math.floor(vidaMax / 4));
      fim.vida = Math.max(fim.vida, Math.min(vidaMax, fim.vida + ganhoVida));
    }
  }
  if (peMax > 0) fim.pe = d.propicio ? peMax : Math.max(fim.pe, metade(peMax));
  if (integMax > 0) fim.integ = integMax;
  fim.sequelas = 0;
  if (d.propicio) fim.exaustao = 0;
  return fim;
}
function textoDoDescanso_(tipo, antes, fim) {
  var d = regraDoDescanso_(tipo, antes);
  var partes = [(d.longo ? 'Longo' : 'Curto') + (d.propicio ? ', em lugar propício' : ', fora de lugar propício')];
  if (antes.existenciaArtificial && !DESCANSOS_[tipo].propicio)
    partes.push('Existência Artificial: local tratado como propício');
  [['vida', 'vida'], ['PE', 'pe'], ['Integridade', 'integ'], ['Sequelas', 'sequelas'], ['Exaustão', 'exaustao']].forEach(function (p) {
    if (antes[p[1]] !== fim[p[1]]) partes.push(p[0] + ' ' + antes[p[1]] + ' → ' + fim[p[1]]);
  });
  if (d.longo && !d.propicio && fim.exaustao > 0) partes.push('Exaustão fica em ' + fim.exaustao);
  if (partes.length === 1) partes.push('nada mudou');
  return partes.join(' · ');
}
function descansar_(e, idx, quedaConfirmada, jaConvertido) {
  var cd = cel_(idx, 'descanso');
  if (!cd || cd !== e.range.getA1Notation().split(':')[0]) return false;
  // 04/11/2026: o evento já traz a escolha; ler a célula custava quase 5 s dos 30 do gatilho.
  var tipo = String(e.value !== undefined ? e.value : e.range.getValue());
  if (!DESCANSOS_[tipo]) return false;
  var ficha = e.range.getSheet();
  var onde = { vida: 'vida', pe: 'energia', integ: 'integridade', exaustao: 'exaustão' };
  var caixinhas = ['sequela 1', 'sequela 2', 'sequela 3'].map(function (k) { return cel_(idx, k); })
                                                       .filter(function (c) { return c; });
  var cExtras = cel_(idx, 'sequela extras');
  // Tudo o que o descanso consulta numa leitura só (cada ida ao servidor custa 1,5 a 2 s)
  var campos = ['descanso', 'vida_max', 'energia_max', 'integridade_max', 'origem', 'marcante', 'menor 1', 'menor 2', 'classe máxima'];
  var lidas = campos.concat(Object.keys(onde).map(function (k) { return onde[k]; }))
    .map(function (k) { return cel_(idx, k); }).concat(caixinhas, cExtras ? [cExtras] : []).filter(function (c) { return c; });
  var v = lerCelulas_(ficha, lidas);
  // Um evento atrasado não pode reaplicar um descanso já concluído ou substituir outra escolha.
  // O menu vem na mesma leitura dos recursos, sem uma chamada extra ao Sheets.
  if (!quedaConfirmada && String(v[cd]) !== tipo) return false;
  if (quedaConfirmada && v[cd] !== SEM_DESCANSO_) throw Error('Aguarde o menu de descanso voltar a Escolha o descanso.');
  var queda = DESCANSOS_[tipo].longo && typeof r53SocorroLer_ === 'function'
    ? r53SocorroLer_(SpreadsheetApp.getActive()) : null;
  var quedaAtiva = queda && r53SocorroAtivo_(queda);
  if (quedaConfirmada && (!quedaAtiva || JSON.stringify(quedaConfirmada) !== JSON.stringify(queda))) {
    throw Error('O registro da queda mudou. Confira SOCORRO e tente novamente.');
  }
  if (quedaAtiva && !quedaConfirmada) {
    e.range.setValue(SEM_DESCANSO_);
    SpreadsheetApp.getActive().toast('Use Recursos → Descanso longo com queda ativa.', 'Queda em andamento', 8);
    return false;
  }
  var valor = function (k) { return v[cel_(idx, k)]; };
  var le = function (k) { return Number(valor(k)) || 0; };
  var antes = { vidaMax: le('vida_max'), peMax: le('energia_max'), integMax: le('integridade_max') };
  Object.keys(onde).forEach(function (k) { antes[k] = le(onde[k]); });
  var extras = cExtras ? Math.max(0, Number(v[cExtras]) || 0) : 0;
  antes.sequelas = caixinhas.filter(function (c) { return v[c] === true; }).length + extras;
  var corpo = valor('marcante');
  var abundante = valor('menor 1') === 'Recuperação Abundante' || valor('menor 2') === 'Recuperação Abundante';
  var publicado = valor('origem') === 'Restrição Celestial · Restrição corporal' &&
    ['Corpo Debilitado', 'Corpo Quebradiço', 'Corpo Exaurido'].indexOf(corpo) >= 0;
  antes.existenciaArtificial = valor('origem') === 'Corpo Amaldiçoado';
  var semEnergia = valor('origem') === 'Restrição Celestial · Sem Energia';
  // Uma leitura limitada também fornece a base válida e as duas permissões corporais.
  var custom = !antes.existenciaArtificial && !publicado && !semEnergia ? SpreadsheetApp.getActive().getSheetByName('DADOS_CUSTOM') : null;
  var regras = custom ? custom.getRange(121, 2, 10, 1).getValues() : [];
  if (regras.length && regras[0][0] === true && regras[2][0] === 'Corpo Amaldiçoado')
    antes.existenciaArtificial = true;
  var temFolego = valor('menor 1') === 'Fôlego Recuperado' || valor('menor 2') === 'Fôlego Recuperado';
  antes.folegoRecuperado = temFolego && (semEnergia || (regras.length > 9 && regras[9][0] === true));
  antes.classeDisponivel = le('classe máxima');
  if (corpo === 'Corpo Exaurido' || abundante) {
    var corporal = publicado || (regras.length > 5 && regras[5][0] === true);
    antes.exaurido = corporal && corpo === 'Corpo Exaurido';
    antes.recuperacaoAbundante = corporal && abundante && (publicado || regras[6][0] === true);
  }
  if (quedaAtiva) {
    var recursos = antes;
    var conversao = r53SocorroResolverConversao_(queda, antes.vida, antes.vidaMax, jaConvertido);
    if (conversao.convertido) recursos = Object.assign({}, antes, {vida: antes.vida + conversao.convertido});
    var recuperados = contaDoDescanso_(tipo, recursos);
    var encerrou = recuperados.vida >= 1 &&
      (queda.status !== 'Derrotado' || antes.integMax === 0 || recuperados.integ >= 1);
    var textoQueda = textoDoDescanso_(tipo, antes, recuperados) + (encerrou
      ? ' · queda encerrada; Sequelas removidas após a recuperação'
      : ' · queda permanece ativa; confira a recuperação com o mestre');
    var alteracoes = [[cd, SEM_DESCANSO_], [cel_(idx, 'último descanso'), textoQueda]];
    Object.keys(onde).forEach(function (k) {
      if (recuperados[k] !== antes[k]) alteracoes.push([cel_(idx, onde[k]), recuperados[k]]);
    });
    caixinhas.forEach(function (c) { if (v[c] === true) alteracoes.push([c, false]); });
    if (cExtras && extras) alteracoes.push([cExtras, 0]);
    var registro = encerrou ? Object.assign({}, conversao.estado, {status: 'Encerrado no descanso'}) : conversao.estado;
    r53SocorroGravar_(SpreadsheetApp.getActive(), registro, null, null, false,
      alteracoes.filter(function (par) { return par[0]; }).map(function (par) {
        var pos = limitesA1_(par[0]);
        return {updateCells: {start: {sheetId: ficha.getSheetId(), rowIndex: pos.l1 - 1, columnIndex: pos.c1 - 1},
          rows: [{values: [r53SocorroCelula_(par[1])]}], fields: 'userEnteredValue'}};
      }));
    SpreadsheetApp.getActive().toast(textoQueda, 'Descanso', 8);
    return true;
  }
  var fim = contaDoDescanso_(tipo, antes);
  // só o que mudou é escrito: a caixa que nasceu como conta (o atual de uma ficha intocada) fica como está
  Object.keys(onde).forEach(function (k) {
    var c = cel_(idx, onde[k]);
    if (c && fim[k] !== antes[k]) ficha.getRange(c).setValue(fim[k]);
  });
  if (fim.sequelas !== antes.sequelas) {
    caixinhas.forEach(function (c, i) { ficha.getRange(c).setValue(i < fim.sequelas); });
    if (cExtras) ficha.getRange(cExtras).setValue(Math.max(0, fim.sequelas - caixinhas.length));
  }
  var texto = textoDoDescanso_(tipo, antes, fim);
  var cu = cel_(idx, 'último descanso');
  if (cu) ficha.getRange(cu).setValue(texto);
  e.range.setValue(SEM_DESCANSO_);
  SpreadsheetApp.getActive().toast(texto, 'Descanso', 8);
  return true;
}
function r53DescansarComQueda(tipo, queda, jaConvertido) {
  var idx = indiceEstatico_();
  var ficha = SpreadsheetApp.getActive().getSheetByName('FICHA');
  return descansar_({range: ficha.getRange(cel_(idx, 'descanso')), value: tipo}, idx, queda, jaConvertido);
}
return {editar:function(e){return descansar_(e,indiceEstatico_());},comQueda:r53DescansarComQueda};
})());}
function r53DescansoEdit_(e){
 if(!e||!e.range)return false;var r=e.range;
 if(r.getSheet().getName()!=='FICHA'||r.getRow()!==45||r.getColumn()!==4||r.getNumRows()!==1||r.getNumColumns()>10)return false;
 var tipo=e.value;if(tipo!==undefined&&['Curto · lugar propício','Curto · fora','Longo · lugar propício','Longo · fora'].indexOf(String(tipo))<0)return true;
 var lock=LockService.getDocumentLock();if(!lock.tryLock(1000)){SpreadsheetApp.getActive().toast('Outra operação está em andamento. Escolha o descanso novamente após ela terminar.','Descanso',6);return true;}
 try{r53DescansoLeve_().editar(e);}finally{try{SpreadsheetApp.flush();}finally{lock.releaseLock();}}return true;
}
