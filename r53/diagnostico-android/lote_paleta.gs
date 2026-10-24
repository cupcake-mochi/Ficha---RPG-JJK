/**
 * Troca de paleta num lote só pelo SpreadsheetApp (teste em cópia descartável, 24/10/2026).
 *
 * Bordas e imagens ficam fixas (decisão do Mizuki, 24/10/2026); só fundo e letra mudam. Cada gravação nesta ficha paga
 * ~9 s de recálculo, então tudo é lido primeiro, calculado em memória e gravado no fim, com um flush só: ler depois de
 * gravar forçaria um flush no meio. Roda no acionador simples, o único que vai junto numa cópia.
 */
var R53_LOTE_ABAS_ = ['CARTEIRA', 'FICHA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'FICHA PESSOAL', 'GLOSSÁRIO'];
var R53_LOTE_PAPEIS_ = ['fundo', 'tinta', 'painel', 'painel_alto', 'papel', 'menu_grande', 'texto', 'texto_fraco',
                        'acento', 'painel_baixo', 'bloco', 'linha', 'regua'];
var R53_LOTE_PROP_ = 'lote_paleta';
var R53_LOTE_PALETAS_ = /*PALETAS*/null;

function r53LoteCores_(nome) {
  var p = String(nome || '').trim().split(' · ');
  var t = R53_LOTE_PALETAS_[p[0]];
  return t && (p[1] === 'Claro' || p[1] === 'Escuro') ? t[p[1] === 'Claro' ? 'claro' : 'escuro'] : null;
}

function r53LoteTrocar_(e) {
  var t0 = Date.now(), ss = SpreadsheetApp.getActive(), props = PropertiesService.getDocumentProperties();
  var marca = function (o) { console.log('LOTE ' + o + ' ' + (Date.now() - t0) + ' ms'); };
  marca('início (' + (t0 - (e && e.r53Inicio_ || t0)) + ' ms desde o onEdit)');
  var nomeNovo = e && e.value !== undefined ? e.value : e.range.getDisplayValue();
  var agora = r53LoteCores_(nomeNovo);
  var antes = r53LoteCores_(props.getProperty(R53_LOTE_PROP_) || (e && e.oldValue));
  if (!agora || !antes) { marca('paleta não reconhecida: ' + nomeNovo + ' / ' + (e && e.oldValue)); return; }
  var h = function (x) { return '#' + String(x).toLowerCase(); };
  var papelDoFundo = {};
  R53_LOTE_PAPEIS_.forEach(function (p) { if (!(h(antes[p]) in papelDoFundo)) papelDoFundo[h(antes[p])] = p; });
  var textoAntes = h(antes.texto), textoAgora = '#' + agora.texto;
  var mesmo = function (mapa, papel, cor) { return mapa && mapa[papel] && h(mapa[papel]) === cor; };

  var lidas = [];
  R53_LOTE_ABAS_.forEach(function (nome) {
    var sh = ss.getSheetByName(nome);
    if (!sh) return;
    var faixa = sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns());
    lidas.push({nome: nome, faixa: faixa, fundos: faixa.getBackgrounds(), letras: faixa.getFontColors()});
    marca('lida ' + nome);
  });

  var trocadas = 0;
  lidas.forEach(function (aba) {
    for (var r = 0; r < aba.fundos.length; r++) {
      var lf = aba.fundos[r], ll = aba.letras[r];
      for (var c = 0; c < lf.length; c++) {
        var fb = String(lf[c]).toLowerCase(), papel = papelDoFundo[fb], fl = String(ll[c]).toLowerCase();
        if (papel) { lf[c] = '#' + agora[papel]; trocadas++; }
        if (fl === textoAntes) ll[c] = textoAgora;
        else if (papel && mesmo(antes.osso_por_papel, papel, fl)) ll[c] = '#' + agora.osso_por_papel[papel];
        else if (papel && mesmo(antes.aviso_por_papel, papel, fl)) ll[c] = '#' + agora.aviso_por_papel[papel];
        else if (papelDoFundo[fl]) ll[c] = '#' + agora[papelDoFundo[fl]];
      }
    }
  });
  marca('calculado (' + trocadas + ' fundos)');

  lidas.forEach(function (aba) {
    aba.faixa.setBackgrounds(aba.fundos);
    aba.faixa.setFontColors(aba.letras);
  });
  ss.getSheetByName('DADOS').getRange('CZ51').setValue('#' + agora.barra);
  props.setProperty(R53_LOTE_PROP_, String(nomeNovo));
  props.deleteProperty('paleta_pendente');
  marca('gravações enfileiradas');
  SpreadsheetApp.flush();
  marca('flush (fim)');
}
