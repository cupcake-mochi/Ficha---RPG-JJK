// Abre a ficha no pdf.js (o leitor do Firefox) com JavaScript ligado, preenche
// a Kaori do livro (cap. 4) e confere contas, barras, régua de espaços e selos.
// Uso: node teste.js ficha.pdf   (TELA=1 salva um print de cada página)
const {chromium} = require('playwright');

(async () => {
  const pdf = process.argv[2] || 'ficha-ciclo-maldito-mizuki-escuro.pdf';
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1000, height: 1400}});
  p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
  await p.goto('http://localhost:8765/viewer.html?file=' + pdf);
  await p.waitForSelector('.annotationLayer input', {timeout: 20000});
  await p.waitForTimeout(1500);

  const ids = await p.evaluate(async () => {
    const f = await window.__doc.getFieldObjects();
    const o = {};
    for (const [k, v] of Object.entries(f)) o[k] = v[0].id;
    return o;
  });
  const sel = n => `.annotationLayer [name="${n}"]`;
  const espera = () => p.waitForTimeout(220);
  async function pagina(n) {   // garante que a página está desenhada antes de mexer nela
    await p.evaluate(n => { window.__viewer.currentPageNumber = n; }, n);
    await p.waitForTimeout(500);
  }
  async function digita(n, v) {
    const e = await p.$(sel(n));
    if (!e) throw new Error('campo não encontrado: ' + n);
    await e.scrollIntoViewIfNeeded(); await e.click(); await e.fill(String(v));
    await p.keyboard.press('Tab'); await espera();
  }
  async function marca(n) { const e = await p.$(sel(n)); await e.scrollIntoViewIfNeeded(); await e.click(); await espera(); }
  async function escolhe(n, v) { await p.selectOption(sel(n), v); await espera(); }
  async function valor(n) { const e = await p.$(sel(n)); return e ? e.evaluate(x => x.value) : '(sem campo)'; }
  async function visivel(n) {
    return p.evaluate(id => {
      const e = document.querySelector(`[data-annotation-id="${id}"]`);
      return !!e && getComputedStyle(e).visibility !== 'hidden';
    }, ids[n]);
  }
  async function travado(n) { const e = await p.$(sel(n)); return e.evaluate(x => x.disabled || x.readOnly); }
  async function cheios(pref, N) { let q = 0; for (let i = 1; i <= N; i++) if (await visivel(pref + i)) q++; return q; }

  let ok = 0, falha = 0;
  function confere(rot, veio, esperado) {
    if (veio === esperado) ok++; else { falha++; console.log('FALHA', rot, 'esperado', JSON.stringify(esperado), 'veio', JSON.stringify(veio)); }
  }
  async function confereValores(tab, etapa) { for (const [k, v] of Object.entries(tab)) confere(etapa + ' ' + k, await valor(k), v); }

  if (process.env.TELA) {   // estado inicial: selos fechados
    for (const i of [2, 3, 5]) {
      await pagina(i); await p.waitForTimeout(700);
      await (await p.$(`.page[data-page-number="${i}"]`)).screenshot({path: `tela-${pdf.replace('.pdf', '')}-inicio-${i}.png`});
    }
  }
  // --- 1 · Kaori no nível 2
  await pagina(1);
  await escolhe('caminho', 'Bastião');
  for (const [k, v] of [['atr_for', 3], ['atr_des', 2], ['atr_con', 2], ['atr_int', 1], ['atr_ess', 1], ['prot_equip', 1]]) await digita(k, v);
  await escolhe('tec_atr', 'FOR'); await escolhe('tr_fis_atr', 'FOR');
  await marca('tr_fis_t'); await marca('tr_vig_t'); await marca('per_atletismo_t');
  await digita('vida_atual', 23); await digita('pe_atual', 4);
  await confereValores({maestria: '+1', espacos: '3', classe0: '2', classe_max: '1', refino: '1', vida_max: '23',
    pe_max: '8', integ_max: '26', protecao: '1', defesa: '13', bloquear: '2d10 + 2', iniciativa: '+2',
    deslocamento: '9 m', cd_tec: '12', atq_tec: '+4', atq_cac: '+4', atq_dist: '+3', carga: '8',
    per_atletismo: '+4', per_acrobacia: '+2', per_percepcao: '+1', tr_fis: '+4', tr_vig: '+3', tr_itl: '+1',
    tr_esp: '+1', of_forja: '-', morr_aguentar: '6', morr_ins1: '8', morr_ins2: '12', morr_janela: '3 rodadas'}, 'nv2');
  confere('nv2 barra vida', await cheios('seg_vida_', 16), 16);
  confere('nv2 barra pe', await cheios('seg_pe_', 16), 8);
  await pagina(3);
  await digita('r1_nome', 'Peso nas Mãos'); await digita('r1_classe', 1);
  const longo = 'Cumpre o Selo e encosta as duas mãos no alvo. '.repeat(8);
  await digita('r1_como', longo);
  confere('texto longo inteiro', (await valor('r1_como')).length, longo.length);
  await pagina(2);
  await digita('tal_1_ce', 1); await digita('tal_1_nome', 'Raiz');
  await confereValores({r1_pe: '3', esp_usados: '2 de 3', esp_feiticos: '1', esp_talentos: '1', esp_expansao: '0'}, 'nv2');
  confere('nv2 régua', await cheios('seg_esp_', 24), 2);
  for (const s of ['selo_c0_3', 'selo_c0_4', 'selo_c0_5', 'selo_exp', 'selo_lib1', 'selo_lib2', 'selo_lib3', 'selo_tm'])
    confere('nv2 visível ' + s, await visivel(s), true);
  await pagina(5);
  confere('nv2 exp_nome travado', await travado('exp_nome'), true);
  confere('nv2 lib1_classe travado', await travado('lib1_classe'), true);

  // --- 2 · nível 10, refino 3: Liberação abre, Expansão ainda pede refino 4
  await pagina(1);
  await digita('nivel', 10); await marca('per_atletismo_e'); await digita('defesa_aj', 2); await digita('prot_equip', '');
  await marca('sequela_1'); await digita('vida_aj', -3); await digita('bloquear_aj', 1);
  await digita('morr_aguentar_aj', 2); await digita('morr_janela_aj', 1);
  await confereValores({maestria: '+2', refino: '3', classe_max: '3', espacos: '9', protecao: '2', defesa: '16',
    bloquear: '2d10 + 6', per_atletismo: '+6', vida_max: String((12 + 2) + (7 + 2) * 9 - 3),
    morr_aguentar: String(Math.ceil(92 / 4) + 2), morr_janela: '3 rodadas', pe_max: '40', integ_max: String(20 + 6 * 9)}, 'nv10');
  confere('nv10 barra vida', await cheios('seg_vida_', 16), Math.round(16 * 23 / 92));
  confere('nv10 selo_lib1', await visivel('selo_lib1'), false);
  confere('nv10 selo_lib2', await visivel('selo_lib2'), true);
  confere('nv10 selo_exp (refino 3)', await visivel('selo_exp'), true);
  confere('nv10 selo_c0_3', await visivel('selo_c0_3'), false);
  confere('nv10 selo_c0_4', await visivel('selo_c0_4'), true);
  // --- 3 · um marco de Refino: refino 4 abre a Expansão
  await digita('refino_aj', 1);
  confere('nv10 refino 4 selo_exp', await visivel('selo_exp'), false);
  await pagina(5);
  confere('nv10 exp_nome livre', await travado('exp_nome'), false);
  await escolhe('exp_degrau', 'Incompleta'); await digita('exp_nome', 'Balança do Último Grão');
  await confereValores({exp_abertura: '18 PE', exp_raio: '6 m', exp_duracao: '2 turnos', exp_desconto: '-1 PE',
    exp_barreira: 'sem barreira', exp_dados: '6d8'}, 'exp');
  await escolhe('exp_degrau', 'Completa'); await digita('exp_raio_aj', 1.5);
  await confereValores({exp_raio: '7,5 m', exp_desconto: '-2 PE', exp_barreira: '100 PV'}, 'exp completa');
  await digita('lib1_classe', 3); await digita('lib1_pe_aj', -1);
  await confereValores({lib1_pe: '13', lib1_dano: '+3d8', tm_dados: '-'}, 'lib');
  await pagina(2);
  await confereValores({esp_usados: '5 de 9', esp_expansao: '3'}, 'nv10');
  confere('nv10 régua', await cheios('seg_esp_', 24), 5);

  // --- 4 · nível 17: Técnica Máxima abre; caixa "ignorar selos" abre o resto
  await pagina(1);
  await digita('nivel', 17);
  await pagina(5);
  confere('nv17 selo_tm', await visivel('selo_tm'), false);
  await confereValores({tm_dados: '24d8', tm_pontos: '8', tm_pe: '25'}, 'nv17');
  await marca('ignorar_selos');
  confere('ignorar selo_lib3', await visivel('selo_lib3'), false);

  console.log(pdf, 'ok', ok, 'falha', falha);
  if (falha) process.exitCode = 1;
  if (process.env.TELA) {
    for (let i = 1; i <= 6; i++) {
      await pagina(i);
      await p.waitForTimeout(700);
      const el = await p.$(`.page[data-page-number="${i}"]`);
      await el.screenshot({path: `tela-${pdf.replace('.pdf', '')}-${i}.png`});
    }
  }
  await b.close();
})();
