/**
 * A caixinha de +/- da ficha, recalculada contra o que o documento publica.
 *
 * O Apps Script nao roda fora do Google, entao o aplicaPasso_ do Codigo.gs
 * mora sozinho, sem tocar em planilha nenhuma, e este arquivo o carrega e o
 * roda no node. Nenhum numero esperado esta escrito aqui: o exemplo sai do
 * manual-temporario.md e as regras saem do decisoes-ficha.json.
 *
 * node regressao-delta.js
 */
'use strict';
const fs = require('fs');
const path = require('path');
const RAIZ = __dirname;

let ok = 0;
const falhas = [];
function checa(nome, obtido, esperado) {
  const a = JSON.stringify(obtido), b = JSON.stringify(esperado);
  if (a === b) { ok++; return; }
  falhas.push(`${nome}\n      obtido:   ${a}\n      esperado: ${b}`);
}

// --- carrega o aplicaPasso_ do Codigo.gs, so ele -------------------------
function extrai(fonte, nome) {
  const i = fonte.indexOf('function ' + nome + '(');
  if (i < 0) throw new Error(`${nome} nao existe no Codigo.gs`);
  let n = 0, j = fonte.indexOf('{', i);
  const ini = j;
  for (; j < fonte.length; j++) {
    if (fonte[j] === '{') n++;
    else if (fonte[j] === '}' && --n === 0) return fonte.slice(i, j + 1);
  }
  throw new Error(`${nome} nao fecha`);
}
const GS = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Codigo.gs'), 'utf8');
const aplicaPasso_ = new Function(extrai(GS, 'aplicaPasso_') +
                                  '; return aplicaPasso_;')();

// --- o que os documentos dizem ------------------------------------------
const A2 = JSON.parse(fs.readFileSync(path.join(RAIZ, 'decisoes-ficha.json'),
                                      'utf8'))['A2_temporario'];
const MAN = fs.readFileSync(path.join(RAIZ, 'manual-temporario.md'), 'utf8');

// "Kaori tem 9 de vida temporaria ... Muralha ... que da 18 ... fica com 18,
//  nao com 27" / "toma 20 de dano ... os 2 que sobram descem na vida dela"
const mTemp = MAN.match(/fica com (\d+), não com (\d+)/);
const mDano = MAN.match(/toma (\d+) de dano.*?os (\d+) que sobram/s);
if (!mTemp || !mDano) throw new Error('o exemplo do manual-temporario.md mudou de forma');
const TEMP = Number(mTemp[1]);         // 18
const SOMA = Number(mTemp[2]);         // 27, a soma que a regra proibe
const DANO = Number(mDano[1]);         // 20
const SOBRA = Number(mDano[2]);        // 2, o que desce na vida

// --- 1. o exemplo publicado, ao pe da letra -----------------------------
const MAXV = 40;                       // qualquer teto acima do exemplo
const kaori = aplicaPasso_(MAXV, MAXV, TEMP, -DANO);
checa('exemplo do manual · a temporaria vai embora inteira',
      kaori.temp, 0);
checa(`exemplo do manual · so ${SOBRA} descem na vida`,
      MAXV - kaori.atual, SOBRA);
checa('exemplo do manual · a temporaria nao virou soma',
      kaori.atual !== MAXV - DANO + (SOMA - TEMP), true);

// --- 2. a temporaria absorve tudo quando da conta -----------------------
const meio = aplicaPasso_(MAXV, MAXV, TEMP, -(TEMP - 1));
checa('dano menor que a temporaria · a reserva nao e tocada',
      meio.atual, MAXV);
checa('dano menor que a temporaria · sobra temporaria',
      meio.temp, 1);
const exato = aplicaPasso_(MAXV, MAXV, TEMP, -TEMP);
checa('dano igual a temporaria · a reserva nao e tocada', exato.atual, MAXV);
checa('dano igual a temporaria · a temporaria zera', exato.temp, 0);

// --- 3. as duas reservas que a A2 manda gastar primeiro -----------------
checa('A2 diz que a vida temporaria gasta antes da vida',
      A2.vida.gasta_antes_da_vida_normal, true);
checa('A2 diz que a energia temporaria gasta antes do PE',
      A2.energia.gasta_antes_do_pe_normal, true);

// --- 4. sem temporaria, a caixinha e a de antes -------------------------
const seca = aplicaPasso_(19, 19, 0, -9);
checa('sem temporaria · desce direto na reserva', seca.atual, 10);
checa('sem temporaria · nada a descontar', seca.temp, 0);
const vazio = aplicaPasso_(19, 19, '', -9);
checa('campo TEMP vazio vale zero', vazio, { atual: 10, temp: 0 });

// --- 5. ganho nao devolve temporaria ------------------------------------
const cura = aplicaPasso_(10, 19, 5, 4);
checa('ganho nao mexe na temporaria', cura.temp, 5);
checa('ganho sobe a reserva', cura.atual, 14);
checa('ganho nao passa do maximo', aplicaPasso_(17, 19, 0, 9).atual, 19);

// --- 6. os limites -----------------------------------------------------
checa('perda nao passa de zero', aplicaPasso_(4, 19, 0, -30).atual, 0);
checa('perda alem de zero nao deixa temporaria para tras',
      aplicaPasso_(4, 19, 3, -30).temp, 0);
checa('temporaria negativa e lida como zero',
      aplicaPasso_(19, 19, -5, -2).atual, 17);
checa('sem maximo declarado o ganho nao e preso',
      aplicaPasso_(10, 0, 0, 40).atual, 50);
checa('passo zero nao move nada', aplicaPasso_(10, 19, 5, 0), { atual: 10, temp: 5 });

// --- resultado ---------------------------------------------------------
const barra = '='.repeat(74);
console.log('');
console.log(barra);
if (falhas.length) {
  console.log(`>>> ${falhas.length} FALHA(S) de ${ok + falhas.length} checagens\n`);
  falhas.forEach(f => console.log('  · ' + f));
  console.log(barra);
  process.exit(1);
}
console.log(`>>> TUDO OK — as ${ok} checagens saem do exemplo do`);
console.log('    manual-temporario.md e das regras do decisoes-ficha.json.');
console.log(barra);
