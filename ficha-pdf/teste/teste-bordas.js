// Casos de borda da ficha em PDF no pdf.js: ficha vazia, os seis Caminhos,
// níveis fora da faixa, Defesa com teto e escudo, Sequelas, ofícios, régua
// estourada, Técnica Máxima nas três faixas, Expansão Sem Barreiras,
// "ignorar selos" ligando e desligando, vírgula e texto em campo de número.
// Uso: node teste-bordas.js ficha.pdf
const {chromium} = require('playwright');

(async () => {
  const pdf = process.argv[2] || 'ficha-ciclo-maldito-mizuki-escuro.pdf';
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1000, height: 1400}});
  const erros = [];
  p.on('console', m => { if (m.type() === 'error') erros.push(m.text()); });
  p.on('pageerror', e => erros.push(String(e)));
  await p.goto('http://localhost:8765/viewer.html?file=' + pdf);
  await p.waitForSelector('.annotationLayer input', {timeout: 20000});
  await p.waitForTimeout(1500);

  const ids = await p.evaluate(async () => {
    const f = await window.__doc.getFieldObjects(); const o = {};
    for (const [k, v] of Object.entries(f)) o[k] = v[0].id;
    return o;
  });
  const sel = n => `.annotationLayer [name="${n}"]`;
  const espera = () => p.waitForTimeout(220);
  async function pagina(n) { await p.evaluate(n => { window.__viewer.currentPageNumber = n; }, n); await p.waitForTimeout(500); }
  async function digita(n, v) {
    const e = await p.$(sel(n)); if (!e) throw new Error('campo não encontrado: ' + n);
    await e.scrollIntoViewIfNeeded(); await e.click(); await e.fill(String(v)); await p.keyboard.press('Tab'); await espera();
  }
  async function marca(n) { const e = await p.$(sel(n)); await e.scrollIntoViewIfNeeded(); await e.click(); await espera(); }
  async function escolhe(n, v) { await p.selectOption(sel(n), v); await espera(); }
  async function valor(n) { const e = await p.$(sel(n)); return e ? e.evaluate(x => x.value) : '(sem campo)'; }
  async function visivel(n) {
    return p.evaluate(id => { const e = document.querySelector(`[data-annotation-id="${id}"]`); return !!e && getComputedStyle(e).visibility !== 'hidden'; }, ids[n]);
  }
  async function travado(n) { const e = await p.$(sel(n)); return e.evaluate(x => x.disabled || x.readOnly); }

  let ok = 0, falha = 0;
  function confere(rot, veio, esperado) {
    if (veio === esperado) ok++; else { falha++; console.log('FALHA', rot, 'esperado', JSON.stringify(esperado), 'veio', JSON.stringify(veio)); }
  }
  async function tab(t, etapa) { for (const [k, v] of Object.entries(t)) confere(etapa + ' ' + k, await valor(k), v); }
  const SELOS = {2: ['selo_c0_3', 'selo_c0_4', 'selo_c0_5'], 5: ['selo_exp', 'selo_lib1', 'selo_lib2', 'selo_lib3', 'selo_tm']};
  async function selos(rot, esperado) {   // cada selo só existe na tela com a página dele aberta
    for (const [pg, lista] of Object.entries(SELOS)) {
      await pagina(Number(pg));
      for (const s of lista) confere(rot + ' ' + s, await visivel(s), esperado);
    }
  }

  // 1 · ficha vazia, como abre
  confere('quantidade de campos', Object.keys(ids).length > 590, true);
  await tab({nivel: '2', grau: '4', maestria: '+1', espacos: '3', classe0: '2', classe_max: '1', refino: '1',
    vida_max: '-', pe_max: '-', integ_max: '25', defesa: '11', protecao: '1', bloquear: '2d10 + 0',
    tr_fis: '-', cd_tec: '-', atq_tec: '-', carga: '5', morr_janela: '3 rodadas', of_forja: '-',
    apt_1: 'Cobrir-se de Energia', apt_2: 'Canalizar Energia'}, 'vazia');
  await selos('vazia', true);
  await pagina(2); await tab({esp_usados: '0 de 3'}, 'vazia');

  // 2 · os seis Caminhos no nível 5 com CON 1 (cap. 6)
  await pagina(1);
  await digita('nivel', 5); await digita('atr_con', 1);
  const caminhos = {'Bastião': [13 + 8 * 4, 20], 'Vanguarda': [9 + 6 * 4, 25], 'Guia': [9 + 6 * 4, 25],
    'Emanador': [7 + 5 * 4, 30], 'Evocador': [7 + 5 * 4, 30], 'Incursor': [7 + 5 * 4, 30]};
  for (const [cm, [vida, pe]] of Object.entries(caminhos)) {
    await escolhe('caminho', cm);
    await tab({vida_max: String(vida), pe_max: String(pe)}, cm);
  }
  await escolhe('caminho', '-');
  await tab({vida_max: '-', pe_max: '-'}, 'sem caminho');

  // 3 · nível fora da faixa e o topo da tabela
  await digita('nivel', 0);  await tab({maestria: '+1', espacos: '2', classe_max: '1'}, 'nível 0');
  await digita('nivel', 31); await tab({maestria: '+4', espacos: '24', classe0: '5', classe_max: '7', refino: '8'}, 'nível 31');
  await digita('nivel', 30);
  await digita('atr_ess', 3); await marca('per_percepcao_t'); await marca('per_percepcao_e');
  await tab({per_percepcao: '+9'}, 'nível 30 especialista');   // 3 + 4 + 2

  // 4 · Defesa: escudo, teto de DES, proteção do Traje
  await digita('atr_des', 3);
  await tab({protecao: String(1 + Math.floor(8 / 3)), defesa: String(10 + 3 + 3)}, 'cobrir-se refino 8');
  await digita('escudo', 2); await digita('teto_des', 1); await digita('prot_equip', 3);
  await tab({protecao: '5', defesa: '16', bloquear: '2d10 + 5'}, 'traje+escudo+teto');

  // 5 · Sequelas e Morrendo
  for (const s of ['sequela_1', 'sequela_2', 'sequela_3']) await marca(s);
  await tab({morr_janela: 'Derrotado'}, '3 sequelas');
  await marca('sequela_3'); await tab({morr_janela: '1 rodada'}, '2 sequelas');

  // 6 · ofícios
  await digita('atr_for', 3); await marca('of_forja_t');
  await tab({of_forja: '+7', carga: '8'}, 'ofício nível 30');   // 3 + 4
  await digita('of_forja_aj', -1); await tab({of_forja: '+6'}, 'ofício com ±');

  // 7 · vírgula e texto em campo de número
  await digita('vida_aj', '2,5'); await digita('atr_int', 'abc');
  await tab({per_investigacao: '+0'}, 'texto conta 0');

  // 8 · Técnica Máxima nas três faixas
  await pagina(5);
  confere('nível 30 selo_tm', await visivel('selo_tm'), false);
  for (const [nv, d, pts, pe] of [[17, '24d8', '8', '25'], [21, '28d8', '12', '30'], [26, '32d8', '16', '35']]) {
    await pagina(1); await digita('nivel', nv); await pagina(5);
    await tab({tm_dados: d, tm_pontos: pts, tm_pe: pe}, 'TM nível ' + nv);
  }

  // 9 · Expansão Sem Barreiras com refino 10
  await pagina(1); await digita('nivel', 30); await digita('refino_aj', 2);
  await pagina(5); await escolhe('exp_degrau', 'Sem Barreiras');
  await tab({exp_abertura: '42 PE', exp_raio: '15 m', exp_duracao: '5 turnos', exp_desconto: '-5 PE',
    exp_barreira: '250 PV', exp_dados: '14d8'}, 'sem barreiras');
  await digita('lib2_classe', 5); await tab({lib2_pe: '23', lib2_dano: '+5d8'}, 'liberação 20');

  // 10 · régua de espaços estourando no nível 2
  await pagina(1); await digita('nivel', 2); await digita('refino_aj', 0);
  await pagina(3);
  for (let i = 1; i <= 4; i++) await digita('r' + i + '_nome', 'Feitiço ' + i);
  await digita('r2_classe', 0); await tab({r2_pe: '0', r3_pe: ''}, 'classe 0 e vazio');
  await pagina(2); await tab({esp_feiticos: '4'}, 'régua');
  confere('régua acima', await valor('esp_usados'), '9 de 3  ACIMA');   // 4 fichas + Sem Barreiras (5), limite 3 no nível 2

  // 11 · selos voltam a fechar ao baixar o nível; "ignorar selos" liga e desliga
  await selos('nível 2 de novo', true);
  await pagina(5);
  confere('exp travada de novo', await travado('exp_nome'), true);
  await marca('ignorar_selos');
  await selos('ignorar', false);
  await pagina(5);
  confere('exp livre com ignorar', await travado('exp_nome'), false);
  await marca('ignorar_selos');
  confere('desligar ignorar selo_tm', await visivel('selo_tm'), true);
  confere('desligar ignorar trava', await travado('tm_nome'), true);

  confere('erros no console', erros.join(' | '), '');
  console.log(pdf, 'bordas ok', ok, 'falha', falha);
  if (falha) process.exitCode = 1;
  await b.close();
})();
