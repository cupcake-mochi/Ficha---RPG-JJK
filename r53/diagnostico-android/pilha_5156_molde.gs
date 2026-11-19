function r53AjustarPilha516_(abas) {
  var operacoes = R53_PILHA_516_.map(function (d) {
    var tabs = abas.filter(function (a) { return a.nome === d.aba; });
    if (tabs.length !== 1) throw Error('Pilha 51–56: aba divergente ' + d.aba);
    var lista = d.addr ? tabs[0].notas : tabs[0].vals;
    if (!Array.isArray(lista)) throw Error('Pilha 51–56: tabela ausente ' + d.aba);
    var alvos = lista.filter(function (v) { return d.addr ? v[0] === d.addr : v[0] === d.r && v[1] === d.c; });
    var pos = d.addr ? 1 : 2;
    var atual = alvos.length ? alvos[0][pos] : null;
    if (alvos.length > 1 || (atual !== d.antes && atual !== d.depois))
      throw Error('Pilha 51–56: alvo divergente ' + d.aba + ' ' + (d.addr || d.r + ',' + d.c));
    return {lista:lista, alvo:alvos[0], pos:pos, delta:d};
  });
  operacoes.forEach(function (op) {
    if (op.alvo) op.alvo[op.pos] = op.delta.depois;
    else op.lista.push([op.delta.r, op.delta.c, op.delta.depois, 0]);
  });
}
