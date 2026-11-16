'use strict';
// Fase 0 da rodada nas oficiais (16/11/2026, decisão D5 do PLANO-RODADA-OFICIAIS-2026-11-16.md).
//
// Refaz, sem Google, toda a cadeia de código que as QAs receberam de #57 a #110: cada preparador roda no commit do
// próprio PR (os preparadores leem arquivos vivos do repo, como apps-script/EditorR53.gs, r53/atalho_livre.gs e os
// *_runtime.gs, que mudaram depois), e cada hash de saída é conferido com o da cadeia.
//
//   node r53/diagnostico-android/reproduzir_cadeia_oficiais.js <Codigo 52302778> <EditorR53 08badae1> <pasta das cinco
//        partes do módulo 9dc3480a (qa-era-*.gs ou modulo-*.gs)> <pasta-nova>
//
// Grava na pasta nova o Codigo e o EditorR53 de cada passo, as cinco partes do módulo depois do #105 e um
// manifesto.json. Sai com erro no primeiro hash divergente. Os arquivos de entrada e de saída são privados.
//
// Cuidados que a reprodução exige (todos conferidos em 16/11):
// - Os preparadores rodaram no Linux: o gzip do Node grava 3 (Unix) no byte de sistema do cabeçalho. No Windows o Node
//   grava 10 e o hash muda (#70 em diante). O passo fixa o byte em 3. O #105 rodou no navegador
//   (CompressionStream), que também grava 3, com o nível padrão.
// - #60, #61 e #62 usam o mesmo preparar_recursos_fila.js, com ANTES fixo no 8a0f2ed6: cada PR refaz a troca inteira
//   a partir do Codigo do #57, com os arquivos do próprio commit. Vale o do #62.
// - #65 e #88 tinham um meio-termo dentro do PR (170273ca e 8935211c). No head, o prepararCodigo já faz as duas etapas.
// - #68 e #91–#103 não mexem no Codigo (o #91–#103 foi só pela API). #104 e #106 são auditorias.
// - O #105 (instalar_frequencia_cena.js) é um trecho de console: aqui roda a mesma troca no node, com as frases do
//   r53/textos_revisados.py do commit do #105.
const fs = require('fs'), path = require('path'), os = require('os'), crypto = require('crypto');
const { execFileSync } = require('child_process');

const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const NOMES = ['Ficha', 'Invocacoes', 'Analise', 'Configuracao', 'Origens'];
const INICIO = { C: '52302778db247518b39eb9ebd741cb6a24fc58063a992a24bda69789dac1c775',
  E: '08badae12322539ff013e728bbf6ad270d9f68455bd4eac548648c2a4ae1b910',
  M: '9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc' };

// [PR, head do PR, preparador, função, C (Codigo) | E (EditorR53) | F (frequência: Codigo e módulo), hash depois, entrada fixa]
const PASSOS = [
  [57, '8db0bae93a3fb04a4a165d632590a0b270aef51a', 'preparar_pilha_5156', 'preparar', 'C', '8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0'],
  [60, 'eaab143c8d0199ad1bd13238f2c51808d32cb6cd', 'preparar_recursos_fila', 'preparar', 'C', '6aec0d0a1e88f777475bc7578fc231c982f0d9b08783c6e8fbe90becdf920455', 57],
  [61, 'cb043171a2cf02dffa14e2933cb08d845eeb8b8e', 'preparar_recursos_fila', 'preparar', 'C', '5b81e86d0d5f06d648d9ae91af23dfee435aa6b3aec57c677b15309a3f750cb8', 57],
  [62, '528e20e39b8c090b5cd434296bb4029c4ad5e7ad', 'preparar_recursos_fila', 'preparar', 'C', '3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7', 57],
  [63, '4a2fb4018e27a2934be02fda91c269732c4cb31e', 'preparar_integridade_movimento', 'prepararCodigo', 'C', '9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631'],
  [64, 'ffdee604b654d454ea2868b02e78cfee33c7c6d2', 'preparar_equipamento', 'prepararCodigo', 'C', 'a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac'],
  [65, '5f6abeae7517b51544edf3e2abb5b6c159aef9c5', 'preparar_bencaos_imunidades', 'prepararCodigo', 'C', '19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac'],
  [66, 'f2bc70fd27b73db1cda3260b108f1c78371daea9', 'preparar_descanso_origens', 'prepararCodigo', 'C', 'd5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084'],
  [67, '971228d2b82980a331a8ebcc577bde6f4fa8b804', 'preparar_origens_recursos', 'prepararCodigo', 'C', 'bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130'],
  [69, '6928962804d0f287587e559b24a1300dc84cf50c', 'preparar_reserva_bolsa', 'prepararCodigo', 'C', '4b0d2cc1952ac3726a47a1969c66c04e30658f7397a927f7af0930615ee9daa9'],
  [70, '4324ad3b8f501819c2be9ee0a8ed15d45841364c', 'preparar_pratica_cotidiana', 'prepararCodigo', 'C', '50f3aa55662adc7251a9be91cae4aace316c84ec3df3f53af471c841094b633b'],
  [70, '4324ad3b8f501819c2be9ee0a8ed15d45841364c', 'preparar_pratica_cotidiana', 'prepararEditor', 'E', '98413975988095b99da8f260c7295b09d00f7f40ae85b4f14ec86f9e88ed6844'],
  [71, 'c54f74a09393be4de1df4fefc8d4813b08065ae0', 'preparar_conjuracao_integridade', 'prepararCodigo', 'C', '6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8'],
  [71, 'c54f74a09393be4de1df4fefc8d4813b08065ae0', 'preparar_conjuracao_integridade', 'prepararEditor', 'E', '165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466'],
  [72, 'b7c06b06a560a92ea9c870e52c180c55cac60a76', 'preparar_classe_zero', 'prepararCodigo', 'C', 'e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e'],
  [72, 'b7c06b06a560a92ea9c870e52c180c55cac60a76', 'preparar_classe_zero', 'prepararEditor', 'E', '13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55'],
  [73, '868ebb8ca10e15606f203d3d42eab208ecd74371', 'preparar_alcance_cura', 'prepararCodigo', 'C', '5c8c7493600367d4c004c3c85a4cc0f5e82459ec4cb4a54ccdb1c769741e3a2c'],
  [73, '868ebb8ca10e15606f203d3d42eab208ecd74371', 'preparar_alcance_cura', 'prepararEditor', 'E', 'aa77309cb42e08f49dbe1f427c72b0c68ec6168fbf6b2294d4d3555a7a7b5c09'],
  [74, '758c571aad04d85a4068c3d976fd3a48275f5f53', 'preparar_alcance_beneficios', 'prepararCodigo', 'C', '2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b'],
  [74, '758c571aad04d85a4068c3d976fd3a48275f5f53', 'preparar_alcance_beneficios', 'prepararEditor', 'E', '2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928'],
  [75, 'af22de97e39301ab71a18456c3990cd6f7fbbcb1', 'preparar_tempo_feiticos', 'prepararCodigo', 'C', '21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923'],
  [75, 'af22de97e39301ab71a18456c3990cd6f7fbbcb1', 'preparar_tempo_feiticos', 'prepararEditor', 'E', '676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49'],
  [76, '4911da8f8d42329cd3744ab425fc5b655258f5d8', 'preparar_rajada_alvos', 'prepararCodigo', 'C', '6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769'],
  [77, 'fa2acaa7ef6bcc6d0305293470c802f1b3ecfc42', 'preparar_fragil_fica', 'prepararCodigo', 'C', 'cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd'],
  [78, '262e264f288c261455949a52f2b828fc6570b01d', 'preparar_sem_volta', 'prepararCodigo', 'C', '01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e'],
  [79, '4118bb9b307cf4f9ee34ff3a45a1a93c1f8e4ece', 'preparar_devolucoes_incompativeis', 'prepararCodigo', 'C', '30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658'],
  [80, '97d1b00ee3c39b699f89d7baa02c96b55bee3fa7', 'preparar_restricoes_agrupadas', 'prepararCodigo', 'C', '9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05'],
  [81, 'bfe00a528eddd7679fafe6792de715c14a593158', 'preparar_fragil_instantaneo', 'prepararCodigo', 'C', 'e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f'],
  [82, 'b11c46a2fc52abe087992d9152f6f346b174b121', 'preparar_fragil_catalogo', 'prepararCodigo', 'C', 'ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75'],
  [83, 'b6c1ac1b3384eaf81d1987cf583fd24645579cb3', 'preparar_forma_funcao', 'prepararCodigo', 'C', 'cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672'],
  [84, '74d83b7f3c836376f658c2e8ccfdca5cf0488552', 'preparar_corroi', 'prepararCodigo', 'C', 'da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e'],
  [85, '735d499684a96d21a457327c5e9fc2d5833552ff', 'preparar_liberacoes', 'prepararCodigo', 'C', '7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7'],
  [86, '6568838badd1a92b130dd46058527fa089da655f', 'preparar_expansao_domada', 'prepararCodigo', 'C', '5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef'],
  [87, '0554071051697790d9c807f2478f6c5816018aa1', 'preparar_repertorio_trilha', 'prepararCodigo', 'C', '26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c'],
  [88, 'ab05bcf9cc5f831dfe460544f935546e40296ea8', 'preparar_contagem_especiais', 'prepararCodigo', 'C', '36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc'],
  [89, 'e2b03307ebfaa3df67b494704508c10f3bd523b6', 'preparar_criacao_nivel_fixo', 'prepararCodigo', 'C', 'ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352'],
  [90, '4eeb276b3938105f9e33a647e9fa0657a700b4f8', 'preparar_nivel_obtido', 'prepararCodigo', 'C', 'b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e'],
  [105, '88e516c480d7430e68c3f3945be1dd084eb48244', 'instalar_frequencia_cena', 'trocas', 'F', '0292582a1fffaa7a328980e14bac39830e67cd58e6d48a0563bc665854193463'],
  [107, 'f11ca2216d6b0e571a9d5fe67a7d062145fde567', 'preparar_trava_nivel_missao', 'preparar', 'C', 'b5861c145394db8ce803304699776986300c121ca0a9ce2f9264edeed3ae4ed5'],
  [108, 'b4b65c36a16fc543d212e9fd39890e587532b40d', 'preparar_corte_xp_missao', 'preparar', 'C', 'c175d8389dce879910ea91e719f6e734ed2f104052e35a4e19e1137cb6a72d48'],
  [109, '1d0e00c2db434836231ac9518db713e7f85afc0a', 'preparar_xp_congelado_nome', 'preparar', 'C', '6ecbe59316825ba0548960ea589a6731dd88a4ef975e71fe36b163fda5609bb3'],
  [110, '2e0ba52032c4b3216c7404dfe7b60afe11920998', 'preparar_xp_linha_congelada', 'preparar', 'C', '4f6600227cd1aeaf6ce090260bd81dce64a3b3c3acd6643247f283230dbc8a77'],
];
// Depois do #105: módulo e as cinco partes (só a Analise muda).
const FIM_MODULO = 'bd42b5351ec1d299e9e54ecd8281de5d75ee129f01fd3c8e4475b5c6fc9e066e';
const FIM_PARTES = {
  Ficha: '6012dcb3dbcd1050f91101c14c68d68ce30c9640c82a56d3ceb4104724003e34',
  Invocacoes: 'ebf20bb167b57cc73a1b7cf71c635303805e43aa7e21f89109f02cb4ba520ee9',
  Analise: '8a54a5162c48d9f340a0aa7178b6f0449dede1a170b32da263eddaeb9ecbf4f6',
  Configuracao: 'bb784c6d0e5fcd08f37650802e10e87413c094570af71393809c4cf8edd1b69f',
  Origens: '9009522887026e3c402345862566834186fd166f336cc8e5c745077351e43792' };

/** Partes do módulo de uma pasta: [{nome, cab, i, s}] na ordem do índice R53_CODIGO_. */
function lerPartes(pasta) {
  const partes = [];
  for (const f of fs.readdirSync(pasta)) {
    const m = /^(?:modulo|qa-era)-(Ficha|Invocacoes|Analise|Configuracao|Origens)\.gs$/.exec(f);
    if (!m) continue;
    const t = fs.readFileSync(path.join(pasta, f), 'utf8');
    const x = /^(\/\/[^\n]*\n)var R53_CODIGO_(\d+)_ = ("[^\n]*");\n?$/.exec(t);
    if (!x) throw Error('Parte do módulo fora do formato: ' + f);
    if (partes[+x[2]]) throw Error('Índice repetido: ' + f);
    partes[+x[2]] = { nome: m[1], cab: x[1], i: +x[2], s: JSON.parse(x[3]), texto: t };
  }
  if (partes.length !== 5 || partes.some(p => !p)) throw Error('Esperadas as cinco partes do módulo em ' + pasta);
  return partes;
}
const moduloDe = (partes, zlib) => zlib.gunzipSync(Buffer.from(partes.map(p => p.s).join(''), 'base64')).toString();

/** Filho: roda um passo dentro do worktree, com o gzip do Linux e o python do Windows. */
function filho(args) {
  const zlib = require('zlib'), gz = zlib.gzipSync;
  zlib.gzipSync = (...a) => { const b = gz(...a); b[9] = 3; return b; };
  const cp = require('child_process'), exe = cp.execFileSync;
  cp.execFileSync = (cmd, a, o) => cmd === 'python3' && process.platform === 'win32' ? exe('python', ['-X', 'utf8', ...a], o) : exe(cmd, a, o);
  const [raiz, arq, fn, entrada, saida, partesEnt, partesSai] = args;
  process.chdir(raiz);
  const mod = require(path.join(raiz, 'r53/diagnostico-android', arq + '.js'));
  const src = fs.readFileSync(entrada, 'utf8');
  if (fn !== 'trocas') { fs.writeFileSync(saida, mod[fn](src)); return; }
  // #105: a mesma troca do trecho de console, no módulo e no caminho leve.
  const pares = mod.trocas(), partes = lerPartes(partesEnt);
  const gz64 = t => zlib.gzipSync(Buffer.from(t, 'utf8')).toString('base64');
  const hm = /if\(hash!=='([0-9a-f]{64})'\)throw new Error\('Pacote R53 incompleto/.exec(src);
  const modulo = moduloDe(partes, zlib);
  if (!hm || sha(modulo) !== hm[1]) throw Error('#105: módulo diferente do hash do Codigo');
  const moduloNovo = mod.aplicar(modulo, pares, 'módulo'), m64 = gz64(moduloNovo);
  const fatias = []; for (let i = 0; i < m64.length; i += 850000) fatias.push(m64.slice(i, i + 850000));
  if (fatias.length > 5) throw Error('#105: pacote passa de cinco arquivos');
  const cl = /(function r53CaminhoLeve_\(\)\{[^\n]*?base64Decode\(")([A-Za-z0-9+\/=]+)("\)[^\n]*?if\(hash!==")([0-9a-f]{64})("\)throw Error\("Caminho: pacote divergente"\))/.exec(src);
  const leve = cl && zlib.gunzipSync(Buffer.from(cl[2], 'base64')).toString();
  if (!cl || sha(leve) !== cl[4]) throw Error('#105: caminho leve diferente do hash');
  const leveNovo = mod.aplicar(leve, pares, 'caminho leve');
  const novo = src.replace(cl[0], () => cl[1] + gz64(leveNovo) + cl[3] + sha(leveNovo) + cl[5])
    .replace(hm[0], () => hm[0].replace(hm[1], sha(moduloNovo)));
  fs.mkdirSync(partesSai);
  for (const p of partes) fs.writeFileSync(path.join(partesSai, 'modulo-' + p.nome + '.gs'),
    p.cab + 'var R53_CODIGO_' + p.i + '_ = ' + JSON.stringify(fatias[p.i] || '') + ';\n');
  fs.writeFileSync(saida, novo);
}

function principal([codigo, editor, pastaModulo, destino]) {
  if (!destino) throw Error('uso: <Codigo 52302778> <EditorR53 08badae1> <pasta das partes do módulo 9dc3480a> <pasta-nova>');
  if (fs.existsSync(destino)) throw Error('A saída deve ser uma pasta nova');
  const zlib = require('zlib');
  if (sha(fs.readFileSync(codigo, 'utf8')) !== INICIO.C) throw Error('Codigo de partida diferente do 52302778');
  if (sha(fs.readFileSync(editor, 'utf8')) !== INICIO.E) throw Error('EditorR53 de partida diferente do 08badae1');
  if (sha(moduloDe(lerPartes(pastaModulo), zlib)) !== INICIO.M) throw Error('Módulo de partida diferente do 9dc3480a');
  const repo = execFileSync('git', ['rev-parse', '--show-toplevel'], { cwd: __dirname, encoding: 'utf8' }).trim();
  const wt = fs.mkdtempSync(path.join(os.tmpdir(), 'cadeia-oficiais-'));
  fs.rmdirSync(wt);
  execFileSync('git', ['-C', repo, 'worktree', 'add', '-q', '--detach', wt, PASSOS[0][1]]);
  fs.mkdirSync(destino);
  const atual = { C: codigo, E: editor, M: pastaModulo }, porPR = {}, manifesto = [];
  try {
    for (const [pr, head, arq, fn, tipo, esperado, fixa] of PASSOS) {
      execFileSync('git', ['-C', wt, 'checkout', '-q', '--detach', head]);
      const lado = tipo === 'E' ? 'E' : 'C';
      const entrada = fixa ? porPR[fixa] : atual[lado];
      const saida = path.join(destino, (lado === 'E' ? 'EditorR53-' : 'Codigo-') + pr + '.gs');
      const extra = tipo === 'F' ? [atual.M, path.join(destino, 'modulo-' + pr)] : [];
      execFileSync(process.execPath, [__filename, '--passo', wt, arq, fn, entrada, saida, ...extra], { stdio: ['ignore', 'ignore', 'inherit'] });
      const antes = sha(fs.readFileSync(entrada, 'utf8')), depois = sha(fs.readFileSync(saida, 'utf8'));
      const ok = depois === esperado;
      manifesto.push({ pr, head: head.slice(0, 10), preparador: arq + '.' + fn, lado, antes, depois, ok });
      console.log('#' + pr + ' ' + (arq + '.' + fn).padEnd(50) + antes.slice(0, 8) + ' -> ' + depois.slice(0, 8) + (ok ? '  ok' : '  DIVERGE (esperado ' + esperado.slice(0, 8) + ')'));
      if (!ok) throw Error('Hash divergente no #' + pr);
      atual[lado] = saida; if (lado === 'C') porPR[pr] = saida;
      if (tipo === 'F') atual.M = extra[1];
    }
    const partes = lerPartes(atual.M), m = sha(moduloDe(partes, zlib));
    if (m !== FIM_MODULO) throw Error('Módulo final divergente: ' + m.slice(0, 8));
    for (const p of partes) if (sha(p.texto) !== FIM_PARTES[p.nome]) throw Error('Parte ' + p.nome + ' divergente');
    console.log('módulo ' + INICIO.M.slice(0, 8) + ' -> ' + m.slice(0, 8) + '  ok (cinco partes conferidas)');
    fs.writeFileSync(path.join(destino, 'manifesto.json'), JSON.stringify({ passos: manifesto, modulo: m,
      fim: { codigo: sha(fs.readFileSync(atual.C, 'utf8')), editor: sha(fs.readFileSync(atual.E, 'utf8')) } }, null, 1));
    console.log(JSON.stringify({ resultado: 'OK', passos: manifesto.length }));
  } finally {
    execFileSync('git', ['-C', repo, 'worktree', 'remove', '--force', wt]);
  }
}

if (require.main === module) {
  const a = process.argv.slice(2);
  if (a[0] === '--passo') filho(a.slice(1)); else principal(a);
}
module.exports = { PASSOS, INICIO, FIM_MODULO, FIM_PARTES, lerPartes };
