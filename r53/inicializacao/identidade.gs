/** Apenas textos pessoais. Fotos/arte sobreposta e escolhas de jogo não são
 * inicializadas por este domínio. Não integra o bot nem certifica ficha pronta.
 */
var R53_NOVA_IDENT_ = {
  diario: 'r53_nova_ficha_identidade_textual_v1', escritasPorExecucao: 4, orcamentoMs: 210000,
  nome: 'Coloque o nome do personagem aqui',
  campos: [
    ['CARTEIRA', 'O9', 'O8', 'PORTADOR'], ['CARTEIRA', 'AK22', 'AK21', 'REGISTRADO POR'],
    ['FICHA PESSOAL', 'AI11', 'AI10', 'IDADE'], ['FICHA PESSOAL', 'AO11', 'AO10', 'ALTURA'],
    ['FICHA PESSOAL', 'Q15', 'Q14', 'OLHOS'], ['FICHA PESSOAL', 'Y15', 'Y14', 'CABELO'],
    ['FICHA PESSOAL', 'AG15', 'AG14', 'PELE'], ['FICHA PESSOAL', 'AO15', 'AO14', 'GÊNERO'],
    ['FICHA PESSOAL', 'Q19', 'Q18', 'APARÊNCIA'], ['FICHA PESSOAL', 'AI19', 'AI18', 'CICATRIZES'],
    ['FICHA PESSOAL', 'Q23', 'Q22', 'TRAÇO · UMA FRASE DA SUA HISTÓRIA'],
    ['FICHA PESSOAL', 'Q27', 'Q26', 'HISTÓRIA'], ['FICHA PESSOAL', 'Q35', 'Q34', 'LAÇOS E ANOTAÇÕES'],
    ['FICHA PESSOAL', 'D31', 'D30', 'PERSONALIDADE']
  ]
};
function r53NovaIdentPreservados_(ss) {
  var etiquetas = R53_NOVA_IDENT_.campos.map(function(x) {
    var sh = ss.getSheetByName(x[0]);
    if (!sh || sh.getRange(x[2]).getValue() !== x[3]) r53NovaFinErro_('layout dos textos pessoais não reconhecido.');
    return [x[0], x[2], x[3]];
  });
  // Não serializar CellImage nem tratar imagens diferentes como o mesmo {}.
  var foto = r53NovaFinLer_(ss, {aba: 'CARTEIRA', faixa: 'C8'});
  if (foto.formulas[0][0] || (foto.valores[0][0] !== '' && foto.valores[0][0] !== 'FOTO\n顔'))
    r53NovaFinErro_('foto pessoal não suportada; use modelo sem foto de personagem.');
  var espelhos = [['FICHA', 'AB2', '=IF(OR(CARTEIRA!$O$9="",CARTEIRA!$O$9="Coloque o nome do personagem aqui"),"",CARTEIRA!$O$9)'], ['FICHA PESSOAL', 'Q11', '=FICHA!AB2'],
                   ['FICHA PESSOAL', 'D10', '=CARTEIRA!$C$8']].map(function(x) {
    var f = ss.getSheetByName(x[0]).getRange(x[1]).getFormulas()[0][0];
    if (f !== x[2] && f !== x[2].replace(/,/g, ';')) r53NovaFinErro_('espelho de nome/foto fora do contrato.');
    return [x[0], x[1], f];
  });
  return r53NovaFinHash_([etiquetas, foto, espelhos]);
}
function r53NovaIdentOperacoes_() {
  var ops = [];
  R53_NOVA_IDENT_.campos.forEach(function(x, i) {
    ops.push({aba: x[0], faixa: x[1], tipo: i === 0 ? 'valor' : 'limpar',
              valor: i === 0 ? R53_NOVA_IDENT_.nome : undefined, formulasLivres: false});
    // Notas de entrada não guardam instruções no molde: as instruções ficam
    // nos cabeçalhos preservados. Não deixar texto pessoal escondido na nota.
    ops.push({aba: x[0], faixa: x[1], tipo: 'notas'});
  });
  return ops;
}
function r53NovaIdentPerfil_() {
  return {nome: 'identidade_textual', diario: R53_NOVA_IDENT_.diario, limites: R53_NOVA_IDENT_,
          operacoes: r53NovaIdentOperacoes_, preservados: r53NovaIdentPreservados_,
          pendente: ['financeiro', 'fotos_e_imagens_sobrepostas', 'progressao', 'escolhas_e_recursos', 'inventario', 'cartoes', 'automacoes', 'prova_nativa']};
}
function r53NovaFichaIdentidadePrevia(ss, contexto) { return r53NovaPerfilPrevia_(ss, contexto, r53NovaIdentPerfil_()); }
function r53NovaFichaIdentidadeAplicar(ss, contexto, assinatura) {
  return r53NovaPerfilAplicar_(ss, contexto, assinatura, r53NovaIdentPerfil_());
}
