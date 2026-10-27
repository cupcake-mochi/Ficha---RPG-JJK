'use strict';
// Marcas custom guardadas e XP devolvida (26/10/2026, remendos 39–41). Com a ficha exportada (nuvem-b47/saidas/atalho/,
// fora do Git; o projeto exportado precisa estar no módulo 52fc6903, o dos remendos até o 38º):
// 1. habilidades custom da CONFIGURAÇÃO (AK50:AX64 e uma borda em volta), nas quatro combinações de K7/K8, sem marcas
//    guardadas e com elas guardadas: mesmas células e gravações que o módulo de antes; com guardadas, sem ler a
//    DADOS_PROGRESSAO; sem guardadas, lê uma vez e guarda o valor certo;
// 2. o r53EdicaoLivre_ do atalho regerado apaga as guardadas numa edição em cada célula de que K7/K8 dependem
//    (rastreadas pelas fórmulas), dentro ou fora do mapa, e em nenhuma da faixa das habilidades; e nenhuma delas fica
//    numa área tratada antes dele (salário, versão pública, lote da paleta);
// 3. escrever na XP da FICHA (conta): a conta volta, o nível fica, e a DADOS não é lida; o resto igual.
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto'), assert = require('assert');
const raiz = path.resolve(__dirname, '..', '..');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const ok = (c, m) => { assert(c, m); checks++; };
const pasta = path.join(raiz, 'nuvem-b47/saidas/atalho');
const fp = path.join(pasta, 'projeto-leve.json'), fd = path.join(pasta, 'oficial-era.json');
if (!fs.existsSync(fp) || !fs.existsSync(fd)) { console.log('marcas_custom: sem a ficha exportada, pulado'); process.exit(0); }
const { criar, custo, projetoComIncremento } = require('../arnes_custo');
const { entradasDoAmparo } = require('../atalho_livre');
const projeto = JSON.parse(fs.readFileSync(fp, 'utf8')), dump = JSON.parse(fs.readFileSync(fd, 'utf8'));
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const { velho: antigo, novo, hashVelho: hv } = projetoComIncremento(projeto, dump, 38, 41);
ok(hv.indexOf('52fc6903') === 0, 'o projeto exportado está no módulo 52fc6903');
ok(antigo !== novo, 'os remendos 39–41 mudam o módulo');

// O de antes com o atalho instalado; o novo com o atalho regerado (r53/atalho_livre.gs), como vai para as oficiais.
const { preparar } = require('../diagnostico-android/preparar_atalho');
function montar(modulo) {
  const A = criar(JSON.parse(JSON.stringify(dump)), { props: { salario_proximo: '99999' } });
  A.ctx.__codigo = modulo;
  for (const f of projeto.files.filter(f => f.type !== 'JSON')) {
    let s = f.source;
    if (f.name === 'Codigo') {
      s = s.replace(/var code=Utilities\.ungzip\([^\n]*\.getDataAsString\('UTF-8'\);/, () => 'var code=__codigo;').split(hv).join(sha(modulo));
      if (modulo !== antigo) s = preparar(s);
    }
    vm.runInContext(s + '\n', A.ctx, { filename: f.name });
  }
  vm.runInContext('r53Modulo_()', A.ctx);
  return A;
}
const conteudo = /^(lista\.)?(valores|valor|fórmula|fórmulas|nota|notas|rico|limpar|setValue|setFormula|setNote|check|uncheck|clearContent)$/;
function editar(A, aba, r, c, v, k7, k8) {
  const p = A.ss.getSheetByName('DADOS_PROGRESSAO'), m7 = p.cel(7, 11, true), m8 = p.cel(8, 11, true), o7 = m7.v, o8 = m8.v;
  if (k7 !== undefined) { m7.v = k7; m8.v = k8; }
  const sh = A.ss.getSheetByName(aba), x = sh.cel(r, c, true), old = x.v, oldf = x.f; x.v = v; delete x.f; A.reset();
  A.ctx.__e = { range: sh.getRange(r, c), source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old };
  let erro = null; try { vm.runInContext('onEdit(__e)', A.ctx); } catch (err) { erro = err.message; }
  const grav = A.log.filter(e => e.t === 'W' && !conteudo.test(e.k)).map(e => [e.k, e.a || '', e.x || ''].join(' '));
  const alt = JSON.stringify(A.alteradas()), s = custo(A.log).s;
  const progressao = A.log.some(e => e.t === 'R' && /^DADOS_PROGRESSAO!K7:K8/.test(e.a || ''));
  const dados = A.log.some(e => e.t === 'R' && /^DADOS!/.test(e.a || ''));
  A.desfazer(); x.v = old; if (oldf) x.f = oldf; m7.v = o7; m8.v = o8;
  return { erro, grav, alt, s, progressao, dados, log: A.log.slice() };
}

// 1. Habilidades custom da CONFIGURAÇÃO
const V = montar(antigo), N = montar(novo);
let n = 0, guardadas = 0;
for (let r = 48; r <= 66; r++) for (let c = 35; c <= 52; c++) for (const [k7, k8] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
  const v = (r + c) % 2 ? 'Texto de teste da habilidade custom, longo o bastante para pedir mais de uma linha na caixa.' : '';
  const onde = 'CONFIGURAÇÃO ' + r + ',' + c + ' K7=' + k7 + ' K8=' + k8, dentro = r >= 50 && r <= 64 && c >= 37 && c <= 50;
  const a = editar(V, 'CONFIGURAÇÃO', r, c, v, k7, k8);
  delete N.props.r53_marcas_custom;
  const b = editar(N, 'CONFIGURAÇÃO', r, c, v, k7, k8);
  eq(b.erro, a.erro, onde + ' erro (sem guardadas)'); eq(b.alt, a.alt, onde + ' células (sem guardadas)'); eq(b.grav, a.grav, onde + ' gravações (sem guardadas)');
  ok(b.s <= a.s + 0.15, onde + ' ficou mais caro sem guardadas: ' + a.s + ' → ' + b.s);
  if (dentro) eq(N.props.r53_marcas_custom, JSON.stringify([k7, k8]), onde + ' guardou as marcas');
  N.props.r53_marcas_custom = JSON.stringify([k7, k8]);
  const g = editar(N, 'CONFIGURAÇÃO', r, c, v, k7, k8);
  eq(g.erro, a.erro, onde + ' erro (guardadas)'); eq(g.alt, a.alt, onde + ' células (guardadas)'); eq(g.grav, a.grav, onde + ' gravações (guardadas)');
  // Fora da faixa, ou do lado em uso, as cartas são refeitas e o livroDasCartas_ lê K7:K8 como antes.
  const semUso = (c <= 44 ? k7 : k8) !== 1 && (c >= 37 && c <= 44 || c >= 45 && c <= 50);
  if (dentro && semUso) { ok(!g.progressao, onde + ' leu a DADOS_PROGRESSAO com as marcas guardadas'); if (a.progressao) guardadas++; }
  else eq(g.progressao, a.progressao, onde + ' leitura de K7:K8 fora do corte');
  n++;
}
ok(guardadas >= 2 * 15 * 14, 'edições que deixam de ler K7:K8: ' + guardadas);
// Guardada estragada: lê a planilha de novo.
N.props.r53_marcas_custom = '[1]';
const est = editar(N, 'CONFIGURAÇÃO', 51, 37, 'x', 0, 0);
ok(est.progressao && N.props.r53_marcas_custom === '[0,0]', 'guardada estragada é refeita');
delete N.props.r53_marcas_custom;

// 2. O atalho regerado apaga as guardadas onde K7/K8 mudam
const gs = fs.readFileSync(path.join(raiz, 'r53/atalho_livre.gs'), 'utf8');
ok(gs.indexOf(sha(novo)) >= 0, 'atalho_livre.gs regerado para o módulo novo');
const At = criar(JSON.parse(JSON.stringify(dump)), {});
vm.runInContext(gs + '\n', At.ctx, { filename: 'atalho_livre.gs' });
const marcas = entradasDoAmparo(dump, ['DADOS_PROGRESSAO', 7, 11, 8, 11]);
let apagadas = 0;
const marcar = (aba, r, c) => { At.props.r53_marcas_custom = '[0,0]'; At.ctx.__e = { range: At.ss.getSheetByName(aba).getRange(r, c) };
  vm.runInContext('r53EdicaoLivre_(__e)', At.ctx); return !('r53_marcas_custom' in At.props); };
for (const aba of ['CONFIGURAÇÃO', 'FICHA']) for (const [r, c] of marcas[aba]) { ok(marcar(aba, r, c), aba + ' ' + r + ',' + c + ' não apagou'); apagadas++; }
for (let r = 50; r <= 64; r++) for (let c = 37; c <= 50; c++) ok(!marcar('CONFIGURAÇÃO', r, c), 'CONFIGURAÇÃO ' + r + ',' + c + ' apagou as marcas');
ok(marcar('FICHA', 11, 4) && marcar('FICHA', 11, 14), 'Caminho e Trilha da FICHA apagam');
const { FIXAS } = require('../atalho_livre');
const antes = [['CONFIGURAÇÃO', FIXAS['CONFIGURAÇÃO']], ['CARTEIRA', [[27, 3, 27, 3]]]];
for (const [aba, areas] of antes) for (const [r, c] of marcas[aba] || []) ok(!areas.some(a => r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3]), aba + ' ' + r + ',' + c + ' tratada antes do atalho');
const Vp = montar(antigo), publica = vm.runInContext('typeof R53_VERSAO_PUBLICA_!=="undefined"?R53_VERSAO_PUBLICA_:[]', Vp.ctx);
for (const x of publica) ok(!(marcas[x.aba] || []).some(([r, c]) => r === x.linha && c === x.coluna), 'versão pública ' + x.aba + ' nas marcas');

// 3. XP da FICHA escrita por cima
const idx = dump.DADOS.cells;
const achar = k => Object.keys(idx).filter(x => x.endsWith(',53') && idx[x].v === k).map(x => idx[x.replace(/,53$/, ',54')].v)[0];
const cxp = achar('xp'), cniv = achar('nivel');
const pos = a1 => { const m = /^([A-Z]+)(\d+)$/.exec(a1); return [+m[2], [...m[1]].reduce((n, x) => n * 26 + x.charCodeAt(0) - 64, 0)]; };
const [rx, cx] = pos(cxp), [rn, cn] = pos(cniv);
ok(dump.FICHA.cells[rx + ',' + cx].f, 'a XP é conta na ficha exportada');
for (const v of [0, 50, 5000, 'abc', '']) {
  const a = editar(V, 'FICHA', rx, cx, v), b = editar(N, 'FICHA', rx, cx, v), onde = 'XP = ' + JSON.stringify(v);
  eq(b.erro, a.erro, onde + ' erro');
  const sem = s => { const o = JSON.parse(s); delete o['FICHA!' + rn + ',' + cn]; return o; };
  eq(sem(b.alt), sem(a.alt), onde + ' células fora do nível');
  ok(!('FICHA!' + rn + ',' + cn in JSON.parse(b.alt)), onde + ' mudou o nível');
  eq(JSON.parse(b.alt)['FICHA!' + rx + ',' + cx], JSON.parse(a.alt)['FICHA!' + rx + ',' + cx], onde + ' a conta volta igual');
  ok(!b.dados, onde + ' leu a DADOS');
  ok(b.s <= a.s, onde + ' ficou mais caro: ' + a.s + ' → ' + b.s);
}
// Outras células da FICHA perto da XP e do nível: iguais.
for (let r = rx - 1; r <= rx + 1; r++) for (let c = Math.min(cx, cn) - 2; c <= Math.max(cx, cn) + 2; c++) for (const v of [3, '']) {
  const a = editar(V, 'FICHA', r, c, v), b = editar(N, 'FICHA', r, c, v), onde = 'FICHA ' + r + ',' + c + ' = ' + v;
  if (r === rx && c === cx) continue;
  eq(b.erro, a.erro, onde + ' erro'); eq(b.alt, a.alt, onde + ' células'); eq(b.grav, a.grav, onde + ' gravações');
}
console.log('marcas_custom: ' + checks + ' verificações, ' + n + ' edições na CONFIGURAÇÃO (' + guardadas + ' sem ler K7:K8 com as marcas guardadas), ' +
  apagadas + ' células que apagam as marcas; módulo novo ' + sha(novo).slice(0, 8));
