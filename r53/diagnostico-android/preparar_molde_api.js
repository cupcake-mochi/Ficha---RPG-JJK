'use strict';
// Molde das fórmulas que foram só pela API (16/11/2026, decisão D2 + D3 do PLANO-RODADA-OFICIAIS-2026-11-16.md).
//
// O onEdit devolve a conta de uma caixa calculada pelo molde do módulo (devolverConta_, que lê ABAS[].vals). De #57 a
// #90 cada preparador levava o molde junto. De #91 a #103, o #108 (FICHA PESSOAL) e o #119 (DADOS_CUSTOM sem
// INDIRECT) foram só pela API: quem escrevesse por cima de uma dessas caixas e apagasse recebia a fórmula ANTIGA.
//
// Este preparador anexa ao Codigo um r53AjustarMoldeApi_, no modelo do pilha_5156_molde.gs: na carga do módulo, troca
// no ABAS[].vals as 593 fórmulas pela versão nova. Aceita, em cada alvo, só a fórmula antiga exata ou a nova (aplicar
// duas vezes não muda nada) e confere tudo antes de trocar a primeira (recusa atômica).
//
// Os 593 alvos (molde_api_plano.json), só nas abas que o onEdit restaura:
//   FICHA 54 (#96 buff decimal, #98, #100, #101, #102, #103), FICHA PESSOAL 292 (#108), DADOS_CONFIG 22 (#96),
//   DADOS_CUSTOM 225 (#119). A DADOS_INVOC e a DADOS_AM ficam de fora: o onEdit não restaura essas abas.
// O "antes" de cada alvo é o primeiro "antes" da cadeia dos deltas (o #100 parte do texto que o #96 deixou, etc.), e
// foi conferido igual ao modelo instalado nas QAs (Codigo b709ad14 + módulo 9dc3480a). O "depois" é o último, e é
// igual ao gerador atual (apps-script/*.gs): o molde fica como o construir() escreveria.
//
// Os dados vão compactados (gzip + base64, ~55 mil caracteres no Codigo em vez de 1,2 milhão) e só abrem na carga do
// módulo. Entra depois do #110 e antes do achatador, que conserva os r53Ajustar*.
//
//   node r53/diagnostico-android/preparar_molde_api.js <Codigo-base.gs> <saida.gs>   (offline; imprime os hashes)
//   node r53/diagnostico-android/preparar_molde_api.js --trecho <Codigo-base.gs> > trecho.js
//        (console do editor: confere o hash de antes e o de depois, guarda o antes em window.__moldeApiAntes e grava;
//         depois Ctrl+S. Gerar UMA vez e usar o mesmo trecho no ensaio e nas oficiais: o hash de depois vem dele.)
// Desfazer: na mesma aba, cod.setValue(window.__moldeApiAntes); ou a versão de backup do projeto.
const fs = require('fs'), path = require('path'), zlib = require('zlib'), crypto = require('crypto'), vm = require('vm');

const BASE = '4f6600227cd1aeaf6ce090260bd81dce64a3b3c3acd6643247f283230dbc8a77'; // Codigo das QAs depois do #110
const ANCORA = " if(R53_MODULO_.__estado().sobras.length)throw new Error('Gerações de dados misturadas no pacote.');";
const CHAMADA = ' try { r53AjustarMoldeApi_(R53_MODULO_.__estado().abas); } catch(err) { R53_MODULO_=null; throw err; }\n';
const CONTAGEM = { 'FICHA': 54, 'FICHA PESSOAL': 292, 'DADOS_CONFIG': 22, 'DADOS_CUSTOM': 225 };
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');

/** O plano congelado: [aba, linha, coluna, antes, depois]. */
function plano() {
  return JSON.parse(fs.readFileSync(path.join(__dirname, 'molde_api_plano.json'), 'utf8'));
}

/** Pura: confere a forma do plano (contagem por aba, alvos únicos, fórmulas, antes ≠ depois). */
function conferirPlano(p) {
  const por = {}, vistos = new Set();
  for (const d of p) {
    if (!Array.isArray(d) || d.length !== 5) throw Error('Molde API: entrada malformada');
    const [aba, r, c, antes, depois] = d, k = aba + '!' + r + ':' + c;
    if (vistos.has(k)) throw Error('Molde API: alvo repetido ' + k);
    vistos.add(k);
    if (!Number.isInteger(r) || !Number.isInteger(c)) throw Error('Molde API: posição inválida ' + k);
    for (const f of [antes, depois]) if (typeof f !== 'string' || f[0] !== '=') throw Error('Molde API: não é fórmula ' + k);
    if (antes === depois) throw Error('Molde API: alvo sem mudança ' + k);
    por[aba] = (por[aba] || 0) + 1;
  }
  if (JSON.stringify(por) !== JSON.stringify(CONTAGEM)) throw Error('Molde API: contagem divergente ' + JSON.stringify(por));
  return p.length;
}

/** O .gs anexado ao Codigo: os dados compactados e o ajuste. */
function runtime(p) {
  p = p || plano();
  conferirPlano(p);
  const b64 = zlib.gzipSync(Buffer.from(JSON.stringify(p), 'utf8'), { level: 9 }).toString('base64');
  return [
    '// GERADO por r53/diagnostico-android/preparar_molde_api.js: molde das fórmulas que foram só pela API',
    '// (#96–#103, #108, #119). ' + p.length + ' alvos; ver o cabeçalho do preparador.',
    'var R53_MOLDE_API_ = ' + JSON.stringify(b64) + ';',
    'function r53AjustarMoldeApi_(abas) {',
    "  var p = JSON.parse(Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode(R53_MOLDE_API_), 'application/gzip')).getDataAsString('UTF-8'));",
    '  if (p.length !== ' + p.length + ") throw new Error('Molde API: plano incompleto');",
    '  var indices = {};',
    '  var ops = p.map(function (d) {',
    '    var idx = indices[d[0]];',
    '    if (!idx) {',
    '      var tabs = abas.filter(function (a) { return a.nome === d[0]; });',
    "      if (tabs.length !== 1 || !Array.isArray(tabs[0].vals)) throw new Error('Molde API: aba divergente ' + d[0]);",
    '      idx = indices[d[0]] = {};',
    "      tabs[0].vals.forEach(function (v) { var k = v[0] + ':' + v[1]; (idx[k] = idx[k] || []).push(v); });",
    '    }',
    "    var alvos = idx[d[1] + ':' + d[2]] || [];",
    '    if (alvos.length !== 1 || (alvos[0][2] !== d[3] && alvos[0][2] !== d[4]))',
    "      throw new Error('Molde API: alvo divergente ' + d[0] + ' ' + d[1] + ',' + d[2]);",
    '    return [alvos[0], d[4]];',
    '  });',
    '  ops.forEach(function (op) { op[0][2] = op[1]; });',
    '}',
    ''].join('\n');
}

/** Pura: o Codigo com o ajuste. Recusa base diferente, âncora ausente ou repetida e segunda aplicação. */
function prepararCodigo(src, p) {
  if (src.indexOf('function r53AjustarMoldeApi_(') >= 0) throw Error('Molde API já presente');
  if (sha(src) !== BASE) throw Error('Codigo diferente do ensaiado (exige o ' + BASE.slice(0, 12) + ', depois do #110)');
  if (src.split(ANCORA).length !== 2) throw Error('Âncora das sobras divergente');
  const out = src.replace(ANCORA, () => CHAMADA + ANCORA) + '\n' + runtime(p);
  new vm.Script(out);
  return out;
}

/** O trecho para o console do editor do Apps Script. */
function trecho(src) {
  const out = prepararCodigo(src), antes = sha(src), depois = sha(out);
  return 'await (async () => { try {\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53Modulo_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const fonte = cod[0].getValue();\n' +
    'if (fonte.indexOf("function r53AjustarMoldeApi_(") >= 0) throw new Error("Molde API já presente");\n' +
    'if (await sha(fonte) !== ' + JSON.stringify(antes) + ') throw new Error("Codigo diferente do ensaiado");\n' +
    'const ancora = ' + JSON.stringify(ANCORA) + ';\n' +
    'if (fonte.split(ancora).length !== 2) throw new Error("Âncora das sobras divergente");\n' +
    'const novo = fonte.replace(ancora, () => ' + JSON.stringify(CHAMADA) + ' + ancora) + "\\n" + ' + JSON.stringify(runtime()) + ';\n' +
    'if (await sha(novo) !== ' + JSON.stringify(depois) + ') throw new Error("Resultado diferente do preparado no node");\n' +
    'window.__moldeApiAntes = fonte;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: ' + JSON.stringify(antes.slice(0, 12)) + ', depois: ' + JSON.stringify(depois.slice(0, 12)) + ', alvos: ' + plano().length + ' });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) {
  const a = process.argv.slice(2);
  if (a[0] === '--trecho' && a[1]) process.stdout.write(trecho(fs.readFileSync(a[1], 'utf8')) + '\n');
  else if (a.length === 2) {
    const src = fs.readFileSync(a[0], 'utf8'), out = prepararCodigo(src);
    fs.writeFileSync(a[1], out);
    console.log(JSON.stringify({ antes: sha(src), depois: sha(out), alvos: plano().length }));
  } else { console.error('uso: <Codigo-base.gs> <saida.gs> | --trecho <Codigo-base.gs>'); process.exit(2); }
}

module.exports = { BASE, ANCORA, CHAMADA, CONTAGEM, sha, plano, conferirPlano, runtime, prepararCodigo, trecho };
