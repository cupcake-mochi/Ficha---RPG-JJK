'use strict';
// VM offline: falhas de serviço, edição concorrente e propriedades controladas.
// Não executa fórmulas do Sheets nem certifica automações de uma cópia nativa.
const assert = require('node:assert/strict');
const {ambiente} = require('./apoio_inicializacao');
let cenarios = 0;
function caso(nome, fn) {
  try { fn(); cenarios++; } catch (e) { e.message = nome + ': ' + e.message; throw e; }
}
function verificar(a) {
  const val = (s, x) => a.range(s, x).getValue();
  assert.equal(val('DADOS_SALARIOS', 'L2'), '{"versao":1,"graus":[]}');
  assert.deepEqual(JSON.parse(JSON.stringify(a.ctx.salarioEstado_(a.ss))), {versao: 1, graus: []});
  assert.equal(val('DADOS_SALARIOS', 'N2'), '');
  assert.equal(val('FICHA PESSOAL', 'O86'), '');
  assert.equal(val('CARTEIRA', 'AT3'), false); assert.equal(val('CONFIGURAÇÃO', 'O39'), false);
  assert.equal(val('FICHA', 'AH11'), 2); assert.equal(val('CONFIGURAÇÃO', 'F46'), 5);
  assert.equal(a.range('CONFIGURAÇÃO', 'G46').getFormulas()[0][0], '=F46');
  assert.equal(val('CONFIGURAÇÃO', 'AK51'), 'habilidade custom da mesa');
  assert.equal(val('FICHA PESSOAL', 'D92'), 'inventário antigo fora deste domínio');
  assert.equal(a.range('FICHA PESSOAL', 'O86').getNotes()[0][0], 'nota do campo');
  for (const col of ['BA', 'BG', 'BM', 'BS']) assert.equal(a.range('FICHA PESSOAL', col + '15').getFormulas()[0][0], '=XP_MISSAO()');
  for (const col of ['AW', 'BC', 'BI', 'BO']) assert.equal(a.range('FICHA PESSOAL', col + '15').getNotes()[0][0], '');
  for (const cell of a.cells.values()) { assert.equal(cell.fmt, 'tema'); assert.equal(cell.dv, 'menu'); }
  for (const k of a.ctx.R53_NOVA_FIN_.propriedadesDocumento) assert(!a.doc.has(k));
  for (const k of a.ctx.R53_NOVA_FIN_.propriedadesScript) assert(!a.script.has(k));
  assert.equal(a.doc.get('r53_recuperacao_personagem'), 'recuperação fora deste domínio');
  assert.equal(a.script.get('paleta'), 'conservar'); assert(!a.locked());
  const journal = a.doc.get(a.ctx.R53_NOVA_FIN_.diario);
  assert(Buffer.byteLength(journal) < 9000, 'abaixo do limite por propriedade do Apps Script');
  assert(!/SEGREDO|missão privada|projeto-antigo|id-antigo|123456/.test(journal));
  assert.equal(JSON.parse(journal).concluido, true);
}
caso('prévia não grava e não revela dados', () => {
  const a = ambiente(); const p = a.preview(); assert.equal(a.writes.length, 0);
  assert.equal(p.criacaoDisponivel, false); assert(p.alteracoes > 0);
  assert(!/SEGREDO|missão privada|123456|projeto-antigo/.test(JSON.stringify(p)));
});
caso('executor por perfil preserva a assinatura financeira v1 anterior', () => {
  // Capturada executando o financeiro.gs de 4f3555d sobre a mesma fixture
  // pública. A expectativa fixa protege diários anteriores à extração do executor.
  const p = ambiente().preview();
  assert.equal(p.assinatura, '2a5aa979285af032193b890becfab2e7afb94b5bf16dc2dd02fe76af425789ae');
  assert.equal(p.alteracoes, 26); assert.equal(p.dominio, 'financeiro');
});
caso('limpeza financeira preserva campanha e o que não pertence ao domínio', () => {
  const a = ambiente(); const p = a.preview(), r = a.complete(p); verificar(a);
  assert.equal(r.criacaoDisponivel, false); assert.equal(r.concluido, true);
  assert(r.pendente.includes('inventario')); assert(r.pendente.includes('prova_nativa'));
  const n = a.writes.length; a.complete(p); assert.equal(a.writes.length, n, 'segunda execução não grava');
});
caso('última linha 5000 e notas são limpas mesmo sem emissão', () => {
  const a = ambiente({rows: 5000, semEmissao: true}); a.complete(a.preview()); verificar(a);
  for (const s of ['EXTRATO', 'SALÁRIOS', 'DADOS_SALARIOS']) {
    assert.equal(a.range(s, 'C5000').getValue(), ''); assert.equal(a.range(s, 'C5000').getNotes()[0][0], '');
    assert.equal(a.range(s, 'A1').getValue(), 'Cabeçalho');
  }
});
caso('cache de fórmula de O86 pode recalcular sem representar edição', () => {
  let n = 0; const a = ambiente({o86Formula: true, recalculo: () => ++n});
  a.complete(a.preview()); verificar(a);
});
for (const id of ['1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k', '1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw'])
  caso('recusa oficial ' + id.slice(0, 5), () => { const a = ambiente({id}); assert.throws(() => a.preview(), /cópia nova/); assert.equal(a.writes.length, 0); });
for (const [key, value] of [['responsavelConfirmado', false], ['copiaNovaConfirmada', false], ['versao', 2],
  ['modelo', ''], ['modelo', 'copia-descartavel'], ['destino', 'outro'], ['operacao', 'curta'], ['arquivosRegistrados', ['copia-descartavel']]])
  caso('recusa contexto ' + key + String(value), () => { const a = ambiente(); a.context[key] = value; assert.throws(() => a.preview(), /cópia nova/); assert.equal(a.writes.length, 0); });
for (const op of [{rows: 5001}, {rows: 1}, {ativoDiferente: true}])
  caso('recusa grade/documento ' + JSON.stringify(op), () => { const a = ambiente(op); assert.throws(() => a.preview()); assert.equal(a.writes.length, 0); });
caso('modo legado não suportado', () => { const a = ambiente(); a.ctx.SALARIO_.formula = false; assert.throws(() => a.preview(), /fórmula não confirmado/); assert.equal(a.writes.length, 0); });
for (const [s, addr] of [['EXTRATO', 'B2'], ['SALÁRIOS', 'K3'], ['FICHA PESSOAL', 'AW15'], ['DADOS_SALARIOS', 'L2']])
  caso('fórmula inesperada ' + addr, () => { const a = ambiente(); a.put(s, addr, 3, '=CUSTOM()'); assert.throws(() => a.preview(), /fórmula inesperada/); assert.equal(a.writes.length, 0); });
caso('falta de fórmula protegida', () => { const a = ambiente(); a.put('DADOS_SALARIOS', 'Q2', 3); assert.throws(() => a.preview(), /fórmula financeira/); assert.equal(a.writes.length, 0); });
caso('fórmula protegida desconhecida não é certificada só por começar com igual', () => {
  const a = ambiente(); a.put('FICHA PESSOAL', 'W86', 0, '=0');
  assert.throws(() => a.preview(), /fora do contrato/); assert.equal(a.writes.length, 0);
});
caso('aspas opcionais de DADOS_SALARIOS normalizadas pelo Google são aceitas', () => {
  const a = ambiente();
  for (const c of a.cells.values()) c.f = c.f.replace(/'DADOS_SALARIOS'!/g, 'DADOS_SALARIOS!');
  a.complete(a.preview()); verificar(a);
});
caso('aba ausente', () => { const a = ambiente(); delete a.sheets.SALÁRIOS; assert.throws(() => a.preview()); assert.equal(a.writes.length, 0); });
caso('prévia envelhecida não cria diário nem limpa', () => { const a = ambiente(), p = a.preview(); a.put('EXTRATO', 'B2', 'novo'); assert.throws(() => a.complete(p), /mudou após/); assert.equal(a.writes.length, 0); assert(!a.locked()); });
caso('alterar fórmula da campanha mantendo cache invalida prévia', () => { const a = ambiente(), p = a.preview(); a.put('CONFIGURAÇÃO', 'G46', 5, '=5'); assert.throws(() => a.complete(p), /mudou após/); assert.equal(a.writes.length, 0); });
caso('trava ocupada', () => { const a = ambiente({ocupado: true}), p = a.preview(); assert.throws(() => a.complete(p), /outra operação/); assert.equal(a.writes.length, 0); });
// Todas as fronteiras reais de escrita: antes e depois da chamada, inclusive
// depois de apagar conteúdo e antes de apagar notas, e entre duas propriedades.
const base = ambiente(); base.complete(base.preview());
for (let falha = 1; falha <= base.writes.length; falha++) for (const fase of ['antes', 'depois'])
  caso(`retoma queda ${fase} da escrita ${falha}`, () => {
    const a = ambiente(), p = a.preview(); let n = 0;
    a.hook(f => { if (f === fase && ++n === falha) throw new Error('queda simulada'); });
    assert.throws(() => a.complete(p), /queda simulada/); assert(!a.locked());
    a.hook(null); a.complete(p); verificar(a);
  });
caso('edição alheia em nota depois de queda não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'conteudo') throw Error('queda'); });
  assert.throws(() => a.complete(p), /queda/); a.hook(null);
  a.put('EXTRATO', 'A2', '', '', 'nota nova'); const n = a.writes.length;
  assert.throws(() => a.complete(p), /editados/); assert.equal(a.writes.length, n);
  assert.equal(a.range('EXTRATO', 'A2').getNotes()[0][0], 'nota nova');
});
caso('propriedade salarial alterada durante pausa não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'excluirPropriedade') throw Error('queda'); });
  assert.throws(() => a.complete(p), /queda/); a.hook(null); a.doc.set('salario_proximo', 'estado novo');
  const n = a.writes.length; assert.throws(() => a.complete(p), /editados/); assert.equal(a.writes.length, n);
  assert.equal(a.doc.get('salario_proximo'), 'estado novo');
});
caso('mesma chamada depois do uso não reinicializa', () => {
  const a = ambiente(), p = a.preview(); a.complete(p); a.put('EXTRATO', 'A2', 'novo lançamento');
  const n = a.writes.length; assert.throws(() => a.complete(p), /editados|já foi usada/); assert.equal(a.writes.length, n);
});
caso('propriedade original reaparecida após conclusão não é apagada', () => {
  const a = ambiente(), p = a.preview(); a.complete(p); a.doc.set('salario_proximo', 'SEGREDO-salario_proximo');
  const n = a.writes.length; assert.throws(() => a.complete(p), /já foi usada/); assert.equal(a.writes.length, n);
});
caso('outra operação não toma diário pendente nem cria nova prévia', () => {
  const a = ambiente(), p = a.preview(); a.complete(p); a.context.operacao = 'outra_operacao_00002';
  const n = a.writes.length; assert.throws(() => a.complete(p), /operação diferente/); assert.throws(() => a.preview(), /retome/); assert.equal(a.writes.length, n);
});
for (const raw of ['{', 'null', '{}']) caso('diário inválido ' + raw, () => {
  const a = ambiente(), p = a.preview(); a.doc.set(a.ctx.R53_NOVA_FIN_.diario, raw);
  assert.throws(() => a.complete(p), /diário inválido/); assert.equal(a.writes.length, 0);
});
caso('diário adulterado', () => {
  const a = ambiente(), p = a.preview(); a.complete(p); const k = a.ctx.R53_NOVA_FIN_.diario, j = JSON.parse(a.doc.get(k));
  j.plano.alteracoes++; a.doc.set(k, JSON.stringify(j)); const n = a.writes.length;
  assert.throws(() => a.complete(p), /diário inválido/); assert.equal(a.writes.length, n);
});
caso('edição no meio da execução interrompe sem sobrescrever', () => {
  const a = ambiente(), p = a.preview(); a.hook((f, kind) => { if (f === 'depois' && kind === 'conteudo') a.put('SALÁRIOS', 'A2', 'lançamento novo'); });
  assert.throws(() => a.apply(p), /concorrente/); assert.equal(a.range('SALÁRIOS', 'A2').getValue(), 'lançamento novo');
  assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario)).concluido, false);
});
caso('estado inicial não inventa início, emissão ou agenda; fórmulas reais exigem emissão', () => {
  const a = ambiente(); a.complete(a.preview()); const state = a.ctx.salarioEstado_(a.ss);
  for (const key of ['inicio', 'ultimaEmissao', 'agenda']) assert.equal(state[key], undefined);
  assert.equal(a.ctx.SALARIO_.formula, true);
  const aux = a.ctx.SALARIO_.f.aux;
  assert(aux[1][1].startsWith('=IF(ISNUMBER(N2);'), 'início pendente depende de emissão numérica');
  assert(aux[2][1].includes('AND(ISNUMBER(N2);'), 'períodos vencidos dependem de emissão');
  assert(a.ctx.SALARIO_.f.emissao.includes("ISNUMBER('DADOS_SALARIOS'!N2)"));
  // Conferência estática do fonte e do leitor reais; não avaliação das fórmulas.
});

caso('execução parcial limita escritas e não declara conclusão', () => {
  const a = ambiente(), p = a.preview(); const r = a.apply(p);
  assert.equal(r.concluido, false); assert.equal(r.retomar, true);
  assert.equal(a.writes.filter(([tipo]) => tipo !== 'propriedade').length, 4);
  assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario)).concluido, false);
  a.complete(p); verificar(a);
});
caso('orçamento esgotado deixa diário retomável sem limpar', () => {
  const a = ambiente(), p = a.preview(); a.ctx.R53_NOVA_FIN_.orcamentoMs = -1;
  const r = a.apply(p); assert.equal(r.concluido, false); assert.equal(r.retomar, true);
  assert.equal(a.writes.length, 1, 'somente diário, sem alteração na ficha');
  a.ctx.R53_NOVA_FIN_.orcamentoMs = 210000; a.complete(p); verificar(a);
});
caso('sem orçamento para conferir não devolve conclusão', () => {
  const a = ambiente(), p = a.preview(); a.complete(p);
  a.ctx.R53_NOVA_FIN_.orcamentoMs = -1;
  const n = a.writes.length, r = a.apply(p);
  assert.equal(r.concluido, false); assert.equal(r.retomar, true); assert.equal(a.writes.length, n);
});
caso('imagem em caixa de lançamento é recusada antes de qualquer escrita', () => {
  const a = ambiente(); a.put('FICHA PESSOAL', 'O86', {valueType: 'IMAGE'});
  assert.throws(() => a.preview(), /imagem ou valor/); assert.equal(a.writes.length, 0);
});
console.log(`${cenarios} cenários offline de inicialização financeira aprovados; nenhuma prova nativa ou liberação de criação.`);
