// Reproduz, sem Sheets, a deriva de cor de fonte da descartável D (FICHA!A147:AX436 em F1BFD6 depois do ensaio
// Claro→Escuro). Usa o mesmo Sheets de mentira do regressao-paleta.js (as linhas 1-125 dele, sem os testes).
//
// Cenário: a ficha está convergida em Mizuki Escuro; as propriedades do documento somem (cópia da planilha não as
// leva); o jogador escolhe o Claro e, antes de a troca terminar, volta ao Escuro. Controle: o mesmo, com as
// propriedades. Uso: node acabamento-b47/reproduzir-deriva-paleta.js [caminho/do/Codigo.gs]
var fs = require('fs'), path = require('path');
const RAIZ_REPO = path.join(__dirname, '..');
const prefixo = fs.readFileSync(path.join(RAIZ_REPO, 'regressao-paleta.js'), 'utf8').split('\n').slice(0, 125).join('\n')
  .replace("const RAIZ=__dirname;", "const RAIZ=" + JSON.stringify(RAIZ_REPO) + ";")
  .replace("require('./medidas/carregar-ficha.js')", "require(" + JSON.stringify(path.join(RAIZ_REPO, 'medidas/carregar-ficha.js')) + ")")
  .replace(/^(const|let) /gm, 'var ');   // o eval direto prende const/let no próprio escopo
eval(prefixo + '\nglobalThis.H = { criaPlanilha, carrega, SRC_NOVO, ABAS, a1 };');
var { criaPlanilha, carrega, SRC_NOVO, ABAS, a1 } = globalThis.H;
const codigo = process.argv[2] ? fs.readFileSync(process.argv[2], 'utf8') : SRC_NOVO;

const ESCURO = 'Mizuki · Escuro · ameixa e rosa', CLARO = 'Mizuki · Claro · rosa e magenta';

function convergida(nome) {
  const P = criaPlanilha(ABAS); const { ctx } = carrega(codigo, P);
  P.abas.CARTEIRA.valores.paleta = nome; ctx.convergirPaleta_(P.clock.t, Infinity);
  return P;
}
function trocas(P, escolhas, cliquesEntre) {
  const { ctx, celPaleta } = carrega(codigo, P);
  escolhas.forEach((n, i) => {
    const antes = P.abas.CARTEIRA.valores.paleta;
    P.abas.CARTEIRA.valores.paleta = n;
    ctx.onEdit({ range: celPaleta, value: n, oldValue: antes }); P.clock.t += 500;
    const limite = i < escolhas.length - 1 ? cliquesEntre : 80;
    for (let k = 0; k < limite && P.props.paleta_pendente; k++) { ctx.onSelectionChange({}); P.clock.t += 500; }
  });
}
function diferencas(P, Q) {
  const out = {};
  for (const nome of Object.keys(P.abas)) {
    const a = P.abas[nome], b = Q.abas[nome]; let n = 0, ex = null; const cores = {};
    for (let r = 0; r < a.fc.length; r++) for (let c = 0; c < a.fc[r].length; c++) {
      if (a.fc[r][c] !== b.fc[r][c] || a.bg[r][c] !== b.bg[r][c]) {
        n++; ex = ex || `${a1(r, c)} fonte ${a.fc[r][c]} (esperado ${b.fc[r][c]})`;
        const k = b.fc[r][c] + '→' + a.fc[r][c]; cores[k] = (cores[k] || 0) + 1;
      }
    }
    if (n) out[nome] = { celulas: n, primeira: ex, cores };
  }
  return out;
}

const ref = convergida(ESCURO);
for (const [rotulo, apagar] of [['cópia sem propriedades', true], ['mesma planilha (controle)', false]]) {
  for (const cliques of [0, 1, 3]) {
    const P = convergida(ESCURO);
    if (apagar) for (const k of Object.keys(P.props)) delete P.props[k];
    trocas(P, [CLARO, ESCURO], cliques);
    const d = diferencas(P, ref);
    console.log(`${rotulo}, ${cliques} clique(s) no Claro: ` + (Object.keys(d).length ? JSON.stringify(d) : 'igual ao Escuro limpo'));
  }
}
