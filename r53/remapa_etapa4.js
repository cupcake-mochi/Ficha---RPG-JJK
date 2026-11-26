'use strict';
// 26/11/2026 (etapa 4 da versão rápida): cada fileira da INVOCAÇÕES ganhou 11 linhas (a lista de perícias, logo abaixo da
// DEFINIÇÃO). Os remendos antigos guardados em diagnostico-android/*.json (antes/depois de cada célula) citam as linhas
// de antes. Eles continuam valendo para as fichas oficiais, que ainda têm o desenho antigo, então os arquivos não mudam:
// quem gera o código do Google (os *_runtime.js) passa os dados por aqui e recebe as linhas novas.
//
// A régua saiu do alinhamento das duas gerações, linha a linha: a linha antiga R desce 11 vezes o número de fileiras
// cuja lista de perícias começa em R ou antes (a 1ª em 68, uma a cada 231 linhas, seis fileiras).
const INICIO = 68, PASSO = 231, FILEIRAS = 6, NOVAS = 11;
const ABA = 'INVOCAÇÕES';

function linha(r) {
  let n = 0;
  for (let f = 0; f < FILEIRAS; f++) if (INICIO + PASSO * f <= r) n++;
  return r + NOVAS * n;
}

// Troca as referências à INVOCAÇÕES dentro de uma fórmula. `propria` diz se a fórmula mora na própria INVOCAÇÕES: aí a
// referência sem nome de aba também é dela.
function texto(s, propria = false) {
  if (typeof s !== 'string') return s;
  s = s.replace(/('INVOCAÇÕES'!\$?[A-Z]{1,3}\$?)(\d+)/g, (m, a, n) => a + linha(+n));
  if (propria) {
    s = s.replace(/("[^"]*")|('[^']*'!\$?[A-Z]{1,3}\$?\d+)|([A-Za-z_]+!\$?[A-Z]{1,3}\$?\d+)|(?<![A-Za-z0-9_.$])(\$?[A-Z]{1,3}\$?)(\d+)(?![A-Za-z0-9_(])/g,
      (m, str, outra, outra2, a, n) => str || outra || outra2 || (a + linha(+n)));
  }
  return s;
}

function a1(s) {
  const m = /^([A-Z]+)(\d+)$/.exec(s);
  return m ? m[1] + linha(+m[2]) : s;
}

function valor(v, propria) {
  if (typeof v === 'string') return texto(v, propria);
  if (Array.isArray(v)) return v.map(x => valor(x, propria));
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, valor(x, propria)]));
  return v;
}

// Uma entrada de remendo: {aba, r, c, antes, depois} ou {aba, a1, antes, depois}.
function item(d) {
  const propria = d.aba === ABA, o = { ...d };
  if (propria && typeof o.r === 'number') o.r = linha(o.r);
  if (propria && typeof o.a1 === 'string') o.a1 = o.a1.split(' ').map(a1).join(' ');
  for (const k of ['antes', 'depois']) if (k in o) o[k] = valor(o[k], propria);
  return o;
}

const lista = xs => (xs || []).map(item);

module.exports = { linha, texto, item, lista, a1 };
